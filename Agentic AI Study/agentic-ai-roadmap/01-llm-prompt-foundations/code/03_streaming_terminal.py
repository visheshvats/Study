"""
Phase 1 - 1.3 Streaming Responses (terminal)
============================================

Streams the model's reply token-by-token to the terminal (the "typewriter"
effect). Streaming does not make generation faster -- it lowers time-to-first-
token so the output FEELS responsive.

Java analogy
------------
The SDK's `messages.stream(...)` is a blocking, synchronous iterator that hands
you chunks as they arrive -- conceptually like consuming an InputStream and
flushing each chunk to the console. (When you push these chunks over HTTP you
get Server-Sent Events; that's the FastAPI file, 04_fastapi_streaming.py.)

Runs OFFLINE out of the box (USE_MOCK = True).
"""

from __future__ import annotations

import logging
import os
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
)
logger = logging.getLogger("phase1.streaming_terminal")

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
    """Mimics the SDK stream context manager. .text_stream yields chunks."""

    def __init__(self, prompt: str) -> None:
        reply = f"[MOCK reply to {prompt!r}] Streaming arrives a few words at a time."
        # Split into word-ish chunks to imitate token streaming.
        self._chunks: list[str] = [w + " " for w in reply.split(" ")]

    def __enter__(self) -> "_MockStream":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    @property
    def text_stream(self) -> Iterator[str]:
        for chunk in self._chunks:
            time.sleep(0.03)  # simulate network latency between tokens
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


# ---------------------------------------------------------------------------
# Terminal streaming
# ---------------------------------------------------------------------------
def stream_to_terminal(prompt: str) -> str:
    """Stream the reply to stdout, flushing each chunk. Returns the full text.

    Both the mock and the real SDK expose the SAME context-manager + .text_stream
    shape, so this function is identical in mock and live mode.
    """
    print("Assistant: ", end="", flush=True)
    collected: list[str] = []
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for chunk in stream.text_stream:
                collected.append(chunk)
                sys.stdout.write(chunk)
                sys.stdout.flush()  # flush so the user sees tokens as they arrive
    except Exception:  # noqa: BLE001
        logger.exception("stream_to_terminal failed")
        raise
    print()  # trailing newline
    return "".join(collected)


@contextmanager
def _timed(label: str) -> Iterator[None]:
    start = time.perf_counter()
    yield
    logger.info("%s took %.2fs", label, time.perf_counter() - start)


def _demo() -> None:
    logger.info("--- streaming to terminal ---")
    with _timed("stream"):
        full = stream_to_terminal("Explain what streaming is in one sentence.")
    logger.info("Full collected length: %d chars", len(full))


if __name__ == "__main__":
    _demo()
