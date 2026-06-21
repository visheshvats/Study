"""05_fastapi_app.py — a small FastAPI gateway with validation, middleware, errors.

FastAPI is to Python roughly what Spring Boot Web is to Java:
  * @app.post("/chat")     ~ @PostMapping("/chat") on a @RestController.
  * Pydantic request model ~ @RequestBody DTO + Bean Validation (@Valid).
  * response_model=...     ~ the declared return DTO (serialized to JSON).
  * HTTPException(400, ..) ~ throwing ResponseStatusException / @ResponseStatus.
  * @app.middleware("http") ~ a servlet Filter / OncePerRequestFilter.
  * uvicorn                ~ the embedded server (Tomcat/Netty).

Run the server:
    uvicorn 05_fastapi_app:app --reload
    # Swagger UI (auto-generated, like springdoc): http://localhost:8000/docs

Run THIS file directly (python 05_fastapi_app.py) to execute an offline,
in-process smoke test of the endpoints using FastAPI's TestClient — no server,
no network — so the demo block prints something meaningful.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic AI Gateway", version="1.0.0")


# ---------------------------------------------------------------------------
# Models — request/response DTOs. Like Spring @RequestBody / @ResponseBody.
# Pydantic validates `message` is a str, `temperature` is a float in range.
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)  # range-validated


class ChatResponse(BaseModel):
    response: str
    session_id: str
    tokens_used: int


# In-memory session store. Replace with Redis later (Phase 11 in the roadmap).
# Think of this as a HashMap standing in for a real cache/DB.
sessions: dict[str, list[str]] = {}


# ---------------------------------------------------------------------------
# Middleware — runs for every request, like a servlet Filter.
# Logs method/path in, status code out.
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("-> %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("<- %s", response.status_code)
    return response


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Handle a chat turn.

    Pydantic has already validated the body by the time we get here (like
    @Valid passing), so we only need business-rule checks below.
    """
    if not request.message.strip():
        # 400 Bad Request — like throwing ResponseStatusException(BAD_REQUEST).
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session_id = request.session_id or str(uuid.uuid4())

    # ===================================================================
    # MOCK RESPONSE (Phase 0).
    # The source roadmap had:  # TODO: Replace with actual LLM call in Phase 1
    # Until then we return a clearly-marked mock: echo the message uppercased.
    #
    # In Phase 1 the real call goes RIGHT HERE, e.g.:
    #     from anthropic import AsyncAnthropic
    #     client = AsyncAnthropic(api_key=ANTHROPIC_KEY)
    #     resp = await client.messages.create(
    #         model="claude-sonnet-4-6",
    #         max_tokens=1024,
    #         temperature=request.temperature,
    #         messages=[{"role": "user", "content": request.message}],
    #     )
    #     response_text = resp.content[0].text
    # ===================================================================
    response_text = f"[MOCK] {request.message.upper()}"

    # Track turns per session (toy memory; swap for Redis later).
    sessions.setdefault(session_id, []).append(request.message)

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        tokens_used=len(request.message.split()),  # crude token proxy
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe — like a Spring Actuator /health endpoint."""
    return {"status": "ok", "version": "1.0.0"}


def _smoke_test() -> None:
    """Offline, in-process test of the endpoints using TestClient.

    TestClient drives the ASGI app without binding a socket — like Spring's
    MockMvc. Lets the `python 05_fastapi_app.py` demo prove the API works.
    """
    from fastapi.testclient import TestClient

    client = TestClient(app)

    health_resp = client.get("/health")
    logger.info("GET /health -> %s %s", health_resp.status_code, health_resp.json())

    ok = client.post("/chat", json={"message": "hello agents"})
    logger.info("POST /chat (valid) -> %s %s", ok.status_code, ok.json())

    empty = client.post("/chat", json={"message": "   "})
    logger.info("POST /chat (empty) -> %s %s", empty.status_code, empty.json())

    bad = client.post("/chat", json={"message": "x", "temperature": 9.9})
    logger.info("POST /chat (bad temperature) -> %s (422 = validation error)", bad.status_code)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger.info("Running offline smoke test (no server needed)...")
    _smoke_test()
    logger.info("FastAPI demo complete. Serve for real with: uvicorn 05_fastapi_app:app --reload")
