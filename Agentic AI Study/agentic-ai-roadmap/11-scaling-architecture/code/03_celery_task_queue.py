"""
Phase 11.3 — Background Task Queue (Celery)
===========================================

Goal
----
Get long-running agent work OUT of the HTTP request thread. A research run can
take 30+ seconds; you must NOT hold an HTTP connection open that long. Instead:
submit the job to a queue, return a `task_id` immediately (HTTP 202-style), and
let the client POLL for the result. This is the submit-and-poll pattern.

Java analogy
------------
- `@celery_app.task`        ~ Spring's `@Async` method... but backed by a REAL
                              broker (Redis/RabbitMQ) and separate worker
                              processes, not just a JVM thread pool. Survives an
                              API restart; scales workers independently.
- the broker (Redis/Rabbit) ~ your Kafka / RabbitMQ / SQS — the durable queue
                              between the producer (API) and the consumers (workers).
- the result backend         ~ where the worker writes the answer so the poller
                              can fetch it (here: the SessionStore from 11.1).
- `.delay(...)`              ~ "fire the message onto the queue and return now."
- `max_retries` / retry      ~ your `@Retryable` / DLQ redelivery semantics.

Why this matters: doing the agent run inside the request thread blocks a server
worker for the whole duration, so a handful of slow users can exhaust your
thread pool and take the API down. Offloading to Celery keeps the API snappy and
lets you scale CPU-heavy agent work by adding workers, not API replicas.

Offline note
------------
No broker exists in this sandbox. We set `task_always_eager=True`, which makes
Celery run the task SYNCHRONOUSLY in-process the moment you call `.delay()` —
perfect for tests and demos, no Redis/RabbitMQ required. The REAL setup (broker
URL + a `celery -A ... worker` process) is shown in `_real_worker_setup()`.

Run
---
    python 03_celery_task_queue.py
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("celery_tasks")

# ---------------------------------------------------------------------------
# OFFLINE SWITCH
# ---------------------------------------------------------------------------
USE_MOCK: bool = os.getenv("USE_MOCK", "true").lower() != "false"
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ---------------------------------------------------------------------------
# Celery import. In production `celery` is installed (see requirements.txt) and
# we use the real thing. To keep the OFFLINE demo runnable even where Celery is
# not installed, we fall back to a tiny eager-mode shim that mimics just the
# Celery surface this file uses: `Celery(...)`, `.conf.update(...)`,
# `@app.task(...)`, `task.delay(...)`, `task.run(...)`, and an AsyncResult with
# an `.id`. The shim ALWAYS runs tasks inline (exactly like
# `task_always_eager=True`), so behaviour matches real Celery in eager mode.
# ---------------------------------------------------------------------------
try:
    from celery import Celery  # type: ignore

    _CELERY_REAL = True
except ImportError:  # pragma: no cover - offline fallback
    _CELERY_REAL = False
    logger.warning("celery not installed — using a minimal in-process eager shim for the demo.")

    class _EagerAsyncResult:
        """Mimics celery.result.AsyncResult enough for the demo (.id, .get())."""

        def __init__(self, task_id: str, value: Any) -> None:
            self.id: str = task_id
            self._value = value

        def get(self, timeout: Optional[float] = None) -> Any:
            return self._value

    class _EagerTask:
        """Wraps a function so .delay()/.run() execute it inline (eager)."""

        def __init__(self, fn: Any, bind: bool = False) -> None:
            self._fn = fn
            self._bind = bind
            self.max_retries = 3

        def run(self, *args: Any, **kwargs: Any) -> Any:
            # `bind=True` => first positional arg is the task instance (`self`).
            if self._bind:
                return self._fn(self, *args, **kwargs)
            return self._fn(*args, **kwargs)

        def delay(self, *args: Any, **kwargs: Any) -> "_EagerAsyncResult":
            value = self.run(*args, **kwargs)
            return _EagerAsyncResult(str(uuid.uuid4()), value)

        def retry(self, exc: BaseException, **kwargs: Any) -> Any:
            # In eager mode the real Celery also re-raises; mirror that so the
            # idempotency/retry logic is exercised identically.
            raise exc

    class _EagerConf(dict):
        def update(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
            super().update(*args, **kwargs)

    class Celery:  # type: ignore[no-redef]
        """Minimal stand-in for celery.Celery (eager-only)."""

        def __init__(self, name: str, broker: str = "", backend: str = "") -> None:
            self.name = name
            self.broker = broker
            self.backend = backend
            self.conf = _EagerConf()

        def task(self, *dargs: Any, **dkwargs: Any) -> Any:
            bind = bool(dkwargs.get("bind", False))

            def decorator(fn: Any) -> _EagerTask:
                return _EagerTask(fn, bind=bind)

            return decorator

# ---------------------------------------------------------------------------
# Reuse the SessionStore from 11.1 as our result backend so results expire too.
# We import defensively so this file stands alone even if run from elsewhere.
# ---------------------------------------------------------------------------
try:
    from importlib import import_module

    _m = import_module("01_redis_session_state")
    SessionStore = _m.SessionStore  # type: ignore[attr-defined]
    make_redis = _m.make_redis      # type: ignore[attr-defined]
except Exception:  # pragma: no cover - fallback when run in isolation
    logger.warning("Could not import 01_redis_session_state; using a local FakeRedis fallback.")
    import json
    from datetime import timedelta

    class _FakeRedis:
        def __init__(self) -> None:
            self._d: Dict[str, str] = {}

        def setex(self, name: str, time_seconds: int, value: str) -> bool:
            self._d[name] = value
            return True

        def get(self, name: str) -> Optional[str]:
            return self._d.get(name)

        def expire(self, name: str, time_seconds: int) -> bool:
            return name in self._d

        def delete(self, *names: str) -> int:
            return sum(1 for n in names if self._d.pop(n, None) is not None)

    def make_redis() -> Any:  # type: ignore[misc]
        return _FakeRedis()

    class SessionStore:  # type: ignore[no-redef]
        def __init__(self, client: Any, ttl_minutes: int = 60) -> None:
            self.r = client
            self.ttl = timedelta(minutes=ttl_minutes)

        def _key(self, sid: str) -> str:
            return f"session:{sid}"

        def save(self, sid: str, state: Dict[str, Any]) -> None:
            self.r.setex(self._key(sid), int(self.ttl.total_seconds()), json.dumps(state, default=str))

        def load(self, sid: str) -> Optional[Dict[str, Any]]:
            data = self.r.get(self._key(sid))
            return json.loads(data) if data else None


# Shared result store (the Celery "result backend" for our app-level results).
result_store = SessionStore(make_redis(), ttl_minutes=60)


# ===========================================================================
# 1. Celery app — broker + backend wiring
# ===========================================================================
celery_app = Celery(
    "agent_tasks",
    broker=REDIS_URL,            # producer -> queue (ignored when eager)
    backend=REDIS_URL.replace("/0", "/1"),  # Celery's own result backend (db 1)
)

if USE_MOCK:
    # task_always_eager=True => .delay() runs the task INLINE, synchronously,
    # with no broker and no worker. This is the documented way to test Celery
    # tasks. eager_propagates=True re-raises task exceptions to the caller so
    # failures don't pass silently in tests.
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
    logger.info("USE_MOCK=True — Celery eager mode (tasks run inline, no broker).")
else:
    logger.info("USE_MOCK=False — Celery will use broker %s (start a worker!).", REDIS_URL)


# ===========================================================================
# 2. A mock long-running agent so the demo is offline & deterministic
# ===========================================================================
class _MockOrchestrator:
    """Stand-in for your real orchestrator from earlier phases."""

    def run(self, query: str) -> str:
        # A real run would fan out to tools/sub-agents and take many seconds.
        time.sleep(0.05)  # token nod to "this is slow work"
        return f"Research complete for: {query!r} — 3 sources synthesized."


orchestrator = _MockOrchestrator()


# ===========================================================================
# 3. The background task — with retries and idempotency
# ===========================================================================
@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def run_research_task(self: Any, task_id: str, query: str, user_id: str) -> Dict[str, Any]:
    """Run the agent in the background and stash the result for polling.

    `bind=True` gives us `self` so we can call `self.retry(...)` — the Celery
    equivalent of `@Retryable` with backoff. `max_retries`/`default_retry_delay`
    cap and space out redelivery so a transient failure self-heals.

    IDEMPOTENCY: a retried/duplicated message must NOT double-process. We check
    the result store first and short-circuit if this task_id is already done —
    the same reason you'd guard a Kafka consumer with a processed-id check
    before committing the offset.
    """
    existing = result_store.load(f"result:{task_id}")
    if existing is not None and existing.get("status") == "done":
        logger.info("Task %s already completed — idempotent skip.", task_id)
        return {"task_id": task_id, "status": "already_completed"}

    try:
        logger.info("Worker running research task %s for user %s", task_id, user_id)
        result = orchestrator.run(query)
        result_store.save(
            f"result:{task_id}",
            {"status": "done", "result": result, "user_id": user_id},
        )
        return {"task_id": task_id, "status": "completed"}
    except Exception as exc:  # noqa: BLE001 - we re-raise via retry
        logger.error("Task %s failed: %s — scheduling retry.", task_id, exc)
        # Record the failure so a poller sees "failed" rather than spinning forever.
        result_store.save(f"result:{task_id}", {"status": "failed", "error": str(exc)})
        raise self.retry(exc=exc)


# ===========================================================================
# 4. FastAPI — submit-and-poll endpoints
# ===========================================================================
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from pydantic import BaseModel

    _FASTAPI_AVAILABLE = True

    # Module-level body model (see 01_redis_session_state.py for why a model
    # nested inside the factory can be misread as a query param -> HTTP 422).
    class ResearchRequest(BaseModel):
        message: str
        # Optional client-supplied idempotency key: same key => same task_id,
        # so a retried POST does not enqueue the job twice. (Stripe-style.)
        idempotency_key: Optional[str] = None

except ImportError:  # pragma: no cover
    _FASTAPI_AVAILABLE = False
    logger.warning("fastapi not installed — skipping HTTP layer (task demo still runs).")


def build_app() -> "FastAPI":
    app = FastAPI(title="Phase 11.3 — Async Research over Celery")

    @app.post("/research/async", status_code=202)
    async def submit_research(request: ResearchRequest) -> Dict[str, Any]:
        # Derive a stable task_id from the idempotency key when provided, else
        # mint a fresh one. A duplicate submit with the same key returns the
        # SAME task_id instead of starting a second run.
        task_id = (
            f"idem-{request.idempotency_key}"
            if request.idempotency_key
            else str(uuid.uuid4())
        )

        already = result_store.load(f"result:{task_id}")
        if already is not None:
            return {"task_id": task_id, "status": "duplicate", "detail": "already submitted"}

        # .delay() => enqueue and return immediately (HTTP 202 Accepted).
        # In eager mode this actually runs inline before returning.
        task = run_research_task.delay(task_id, request.message, "user-123")
        return {"task_id": task_id, "status": "queued", "celery_id": task.id}

    @app.get("/research/{task_id}")
    async def get_result(task_id: str) -> Dict[str, Any]:
        # The poll endpoint: cheap, fast, returns "processing" until the worker
        # has written a result. The client polls this on an interval.
        result = result_store.load(f"result:{task_id}")
        if result is None:
            return {"task_id": task_id, "status": "processing"}
        return {"task_id": task_id, **result}

    return app


def _real_worker_setup() -> None:
    """Reference only — how you'd run this for real (NOT executed).

    1. Start Redis (or RabbitMQ) as the broker.
    2. Set USE_MOCK=False so eager mode is OFF.
    3. Run a worker process (separate from the API):

         celery -A 03_celery_task_queue.celery_app worker --loglevel=info

       That worker is your horizontally-scalable consumer pool — add more
       worker processes/pods to handle more concurrent agent runs, exactly like
       scaling out Kafka consumers in a consumer group.
    4. Run the FastAPI app (uvicorn) as a SEPARATE process; it only enqueues.
    """
    raise NotImplementedError("Reference notes only; start a real broker + worker to run.")


# ===========================================================================
# 5. Demo — submit and poll, fully offline (eager mode)
# ===========================================================================
def _demo() -> None:
    print("=" * 70)
    print("Phase 11.3 — Celery submit-and-poll demo (offline, eager mode)")
    print("=" * 70)

    # --- Direct task call via .delay() (runs inline because eager) ------
    print("\n[1] Submit a task with .delay() — returns immediately (eager runs it inline):")
    tid = str(uuid.uuid4())
    async_result = run_research_task.delay(tid, "impact of rate hikes", "user-123")
    print(f"    enqueued task_id={tid} celery_id={async_result.id}")

    print("\n[2] Poll the result store until done (the client's polling loop):")
    for attempt in range(1, 6):
        stored = result_store.load(f"result:{tid}")
        status = stored["status"] if stored else "processing"
        print(f"    poll #{attempt}: status={status}")
        if stored and status == "done":
            print(f"    result -> {stored['result']}")
            break
        time.sleep(0.05)
    assert result_store.load(f"result:{tid}")["status"] == "done"

    # --- Idempotency: submitting the SAME task_id again is a no-op -------
    print("\n[3] Idempotency — re-running the same task_id does NOT reprocess:")
    again = run_research_task.run(tid, "impact of rate hikes", "user-123")
    print(f"    second call -> {again}  (status 'already_completed' == idempotent)")
    assert again["status"] == "already_completed"

    # --- HTTP submit-and-poll via offline TestClient --------------------
    if _FASTAPI_AVAILABLE:
        print("\n[4] FastAPI submit-and-poll over HTTP (offline TestClient):")
        app = build_app()
        with TestClient(app) as http:
            submit = http.post(
                "/research/async",
                json={"message": "summarize Q3 filings", "idempotency_key": "abc-123"},
            )
            sub_body = submit.json()
            print(f"    POST /research/async -> {submit.status_code} {sub_body}")
            task_id = sub_body["task_id"]

            # Poll until done (eager => already done on first poll).
            poll = http.get(f"/research/{task_id}")
            print(f"    GET  /research/{{id}} -> {poll.status_code} status={poll.json()['status']}")
            assert poll.json()["status"] == "done"

            # Same idempotency key => duplicate, NOT a second run.
            dupe = http.post(
                "/research/async",
                json={"message": "summarize Q3 filings", "idempotency_key": "abc-123"},
            )
            print(f"    duplicate submit -> status={dupe.json()['status']} (idempotent)")
            assert dupe.json()["status"] == "duplicate"
        print("    OK — submitted, polled to completion, and dedup'd a retry.")
    else:
        print("\n[4] Skipped HTTP demo (fastapi not installed).")

    print("\nDone. For real async: set USE_MOCK=False, start Redis, run a celery worker.")
    print("(See _real_worker_setup() for the exact worker command.)")


if __name__ == "__main__":
    _demo()
