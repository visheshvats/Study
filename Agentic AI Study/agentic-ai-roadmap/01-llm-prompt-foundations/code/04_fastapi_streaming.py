"""
Phase 1 - 1.3 Streaming Responses (FastAPI SSE endpoint)
========================================================

Exposes POST /chat/stream that streams the model's reply over Server-Sent
Events (text/event-stream). Each token is sent as `data: <chunk>\\n\\n`, and the
stream ends with `data: [DONE]\\n\\n`.

Java analogy
------------
SSE here == Spring's SseEmitter (or Flux<ServerSentEvent> in WebFlux): one held-
open HTTP connection over which the server pushes a sequence of events.

THE EVENT-LOOP TRAP (important)
-------------------------------
FastAPI async endpoints run on a single-threaded event loop. The Anthropic SDK
stream is BLOCKING/synchronous. Iterating it directly inside `async def` would
block the loop and freeze every other request -- the same sin as calling blocking
JDBC on a WebFlux event-loop thread. So we offload the blocking iterator to a
thread pool and feed chunks back to the loop via an asyncio.Queue.

Run (offline mock):
    pip install fastapi uvicorn          # anthropic/dotenv only needed if USE_MOCK=False
    uvicorn 04_fastapi_streaming:app --reload
    # then:  curl -N -X POST localhost:8000/chat/stream -H "Content-Type: application/json" -d '{"message":"hi"}'
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import AsyncIterator, Iterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
)
logger = logging.getLogger("phase1.fastapi_streaming")

# ===========================================================================
#  USE_MOCK : True = offline fake token stream; False = real Anthropic SDK.
#  To use the real client:
#    1) pip install anthropic python-dotenv
#    2) set ANTHROPIC_API_KEY (env or code/.env)
#    3) USE_MOCK = False
# ===========================================================================
USE_MOCK: bool = True

MODEL: str = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Mock streaming client  (MOCK -- offline learning only)
# ---------------------------------------------------------------------------
class _MockStream:
    def __init__(self, prompt: str) -> None:
        reply = f"[MOCK SSE reply to {prompt!r}] tokens stream over text/event-stream."
        self._chunks: list[str] = [w + " " for w in reply.split(" ")]

    def __enter__(self) -> "_MockStream":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    @property
    def text_stream(self) -> Iterator[str]:
        for chunk in self._chunks:
            time.sleep(0.03)
            yield chunk


class MockMessages:
    def stream(
        self, *, model: str, max_tokens: int, messages: list[dict]
    ) -> _MockStream:
        prompt = messages[-1]["content"] if messages else ""
        return _MockStream(prompt)


class MockAnthropic:
    def __init__(self) -> None:
        self.messages = MockMessages()


def build_client() -> object:
    if USE_MOCK:
        logger.info("Using MockAnthropic streaming (offline).")
        return MockAnthropic()
    from anthropic import Anthropic
    from dotenv import load_dotenv

    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY not set (code/.env or environment).")
    logger.info("Using real Anthropic client.")
    return Anthropic()


client = build_client()

app = FastAPI(title="Phase 1 - SSE Streaming")


class StreamRequest(BaseModel):
    message: str


def _blocking_stream(message: str) -> Iterator[str]:
    """Synchronous generator wrapping the (blocking) SDK stream."""
    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": message}],
    ) as stream:
        yield from stream.text_stream


async def _stream_off_event_loop(message: str) -> AsyncIterator[str]:
    """Run the blocking iterator in a worker thread; relay chunks via a queue.

    This is what keeps the event loop free. Never iterate the blocking SDK
    stream directly inside an async function.
    """
    queue: asyncio.Queue[str | None] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def _produce() -> None:
        try:
            for chunk in _blocking_stream(message):
                # Hand the chunk back to the loop thread-safely.
                asyncio.run_coroutine_threadsafe(queue.put(chunk), loop)
        except Exception:  # noqa: BLE001
            logger.exception("producer thread failed")
        finally:
            asyncio.run_coroutine_threadsafe(queue.put(None), loop)  # sentinel

    # Offload the blocking work to a thread (executor); do not await it here.
    loop.run_in_executor(None, _produce)

    while True:
        chunk = await queue.get()
        if chunk is None:  # producer finished
            break
        yield chunk


@app.post("/chat/stream")
async def chat_stream(request: StreamRequest) -> StreamingResponse:
    async def generate() -> AsyncIterator[str]:
        try:
            async for chunk in _stream_off_event_loop(request.message):
                # SSE frame format: "data: <payload>\n\n"
                yield f"data: {chunk}\n\n"
        except Exception:  # noqa: BLE001
            logger.exception("SSE generate failed")
            yield "data: [ERROR]\n\n"
        finally:
            yield "data: [DONE]\n\n"  # sentinel so the client closes cleanly

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mode": "mock" if USE_MOCK else "live"}


# ---------------------------------------------------------------------------
# Offline self-test: exercise the streaming generator WITHOUT a running server.
# (Lets `python 04_fastapi_streaming.py` prove the SSE pipeline works offline.)
# ---------------------------------------------------------------------------
async def _selftest() -> None:
    logger.info("--- offline self-test of SSE generator ---")
    async for chunk in _stream_off_event_loop("hello from selftest"):
        print(f"data: {chunk}\n", end="")
    print("data: [DONE]")


if __name__ == "__main__":
    # Demonstrates the pipeline offline. To serve for real:
    #   uvicorn 04_fastapi_streaming:app --reload
    asyncio.run(_selftest())
