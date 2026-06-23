"""
Phase 11 · 11.1 — Redis Session State
=====================================

Moves agent session state OUT of process memory and into Redis, so any one of N
stateless app nodes can serve any request. This is the single most important change
that lets you scale horizontally.

Java analogy
------------
This is exactly **Spring Session backed by Redis**. Your `@RestController` stays
stateless; the conversation lives in Redis with a TTL, and a load balancer can route
the next request to a different pod without losing context. `SessionStore` here ==
`RedisOperationsSessionRepository`.

Offline mode
------------
Real Redis isn't running in this sandbox, so `USE_MOCK = True` swaps in a tiny
dict-backed `FakeRedis` that implements just the commands we use (`setex`, `get`,
`expire`, `delete`) including real TTL expiry. Flip `USE_MOCK = False` and set
`REDIS_URL` to talk to a real server — the `SessionStore` code does not change.

Run:  python 01_redis_session_state.py
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from datetime import timedelta
from typing import Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("redis-session")

# ─────────────────────────────────────────────────────────────────────────────
# Toggle: True = run fully offline with FakeRedis. False = use the real redis client.
# ─────────────────────────────────────────────────────────────────────────────
USE_MOCK = True
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


# ─────────────────────────────────────────────────────────────────────────────
# Offline stand-in for redis.Redis — implements ONLY the commands SessionStore uses.
# A real redis.Redis(decode_responses=True) is a drop-in replacement.
# ─────────────────────────────────────────────────────────────────────────────
class FakeRedis:
    """Minimal in-memory Redis emulation with TTL support (single-process only)."""

    def __init__(self) -> None:
        # key -> (value:str, expires_at_epoch:float | None)
        self._data: dict[str, tuple[str, Optional[float]]] = {}

    def _expired(self, key: str) -> bool:
        item = self._data.get(key)
        if item is None:
            return True
        _, expires_at = item
        if expires_at is not None and time.time() > expires_at:
            self._data.pop(key, None)  # lazy eviction, like Redis
            return True
        return False

    def setex(self, key: str, ttl: "timedelta | int", value: str) -> None:
        seconds = int(ttl.total_seconds()) if isinstance(ttl, timedelta) else int(ttl)
        self._data[key] = (value, time.time() + seconds)

    def get(self, key: str) -> Optional[str]:
        if self._expired(key):
            return None
        return self._data[key][0]

    def expire(self, key: str, seconds: int) -> None:
        if not self._expired(key):
            value, _ = self._data[key]
            self._data[key] = (value, time.time() + seconds)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)


def make_redis() -> Any:
    """Factory: return FakeRedis offline, or a real redis client when USE_MOCK is False."""
    if USE_MOCK:
        logger.info("[MOCK] Using in-memory FakeRedis (no server required).")
        return FakeRedis()
    # --- REAL path (requires `pip install redis` and a running server) ---
    import redis  # type: ignore

    logger.info("Connecting to real Redis at %s", REDIS_URL)
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


# ─────────────────────────────────────────────────────────────────────────────
# SessionStore — the production component. Identical for FakeRedis and real Redis.
# ─────────────────────────────────────────────────────────────────────────────
class SessionStore:
    """TTL-bounded session storage in Redis. == Spring Session's Redis repository."""

    def __init__(self, client: Any, ttl_minutes: int = 60) -> None:
        self.r = client
        self.ttl = timedelta(minutes=ttl_minutes)

    def _key(self, session_id: str) -> str:
        return f"session:{session_id}"

    def save(self, session_id: str, state: dict) -> None:
        # default=str so datetimes etc. serialize without blowing up.
        self.r.setex(self._key(session_id), self.ttl, json.dumps(state, default=str))

    def load(self, session_id: str) -> Optional[dict]:
        data = self.r.get(self._key(session_id))
        return json.loads(data) if data else None

    def extend(self, session_id: str) -> None:
        """Sliding-expiration: reset the TTL on activity (like touching an HTTP session)."""
        self.r.expire(self._key(session_id), int(self.ttl.total_seconds()))

    def delete(self, session_id: str) -> None:
        self.r.delete(self._key(session_id))


# ─────────────────────────────────────────────────────────────────────────────
# Mock LLM call (stands in for the Phase 10 `resilient_llm_call`).
# ─────────────────────────────────────────────────────────────────────────────
async def resilient_llm_call(message: str) -> str:
    """[MOCK] Deterministic reply. Swap for the real rate-limited Anthropic call."""
    return f"(assistant) I received: {message!r}"


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI layer — stateless endpoint that reads/writes session state in Redis.
# Guarded so the file still runs if FastAPI isn't installed.
# ─────────────────────────────────────────────────────────────────────────────
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from pydantic import BaseModel

    _FASTAPI_AVAILABLE = True

    class ChatRequest(BaseModel):
        message: str
        session_id: Optional[str] = None
except ImportError:  # pragma: no cover
    _FASTAPI_AVAILABLE = False
    logger.warning("FastAPI not installed — skipping the HTTP demo. `pip install fastapi`.")


def build_app(store: "SessionStore"):
    """Build a FastAPI app whose /chat/stateful endpoint persists state in Redis."""

    app = FastAPI(title="Stateful Chat (Redis-backed)")

    @app.post("/chat/stateful")
    async def stateful_chat(request: ChatRequest) -> dict:
        # New session id if the client didn't supply one (first request).
        session_id = request.session_id or str(uuid.uuid4())

        # Load prior state from Redis (or start fresh). The pod has NO local memory.
        state = store.load(session_id) or {"messages": [], "context": {}}

        state["messages"].append({"role": "user", "content": request.message})
        reply = await resilient_llm_call(request.message)
        state["messages"].append({"role": "assistant", "content": reply})

        store.save(session_id, state)  # write-back to Redis
        return {"response": reply, "session_id": session_id, "turns": len(state["messages"])}

    return app


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=" * 70)
    print("Phase 11.1 — Redis Session State (offline FakeRedis demo)")
    print("=" * 70)

    store = SessionStore(make_redis(), ttl_minutes=60)
    sid = "alice-session-001"

    # [1] Save + load round-trip
    print("\n[1] Save then load a session:")
    store.save(sid, {"messages": [{"role": "user", "content": "Hello"}], "context": {}})
    print(f"    loaded -> {store.load(sid)}")

    # [2] TTL expiry (short TTL so we can observe eviction offline)
    print("\n[2] TTL expiry (1s):")
    short = make_redis()
    short.setex("session:ephemeral", 1, json.dumps({"tmp": True}))
    print(f"    immediate get -> {short.get('session:ephemeral')}")
    time.sleep(1.1)
    print(f"    get after expiry -> {short.get('session:ephemeral')}  (None == evicted)")

    # [3] Delete (logout)
    print("\n[3] Delete (explicit logout):")
    store.delete(sid)
    print(f"    load after delete -> {store.load(sid)}  (None == gone)")

    # [4] HTTP layer via offline TestClient
    if _FASTAPI_AVAILABLE:
        print("\n[4] FastAPI /chat/stateful smoke test (offline TestClient, no server):")
        app = build_app(SessionStore(make_redis(), ttl_minutes=60))
        with TestClient(app) as http:
            r1 = http.post("/chat/stateful", json={"message": "Hello"})
            body1 = r1.json()
            sid1 = body1["session_id"]
            print(f"    turn 1 -> status={r1.status_code} session={sid1} turns={body1['turns']}")

            # Reuse the SAME session id — proves continuity across stateless requests.
            r2 = http.post("/chat/stateful", json={"message": "Still here?", "session_id": sid1})
            body2 = r2.json()
            print(f"    turn 2 -> turns={body2['turns']} (transcript grew => state shared via Redis)")

    print("\nDemo complete. Swap USE_MOCK=False + REDIS_URL for a real server.")


if __name__ == "__main__":
    main()
