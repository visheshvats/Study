"""04_async_basics.py — asyncio: coroutines, gather, async generators.

asyncio is Python's single-threaded cooperative concurrency model. Compared to
Java:
  * `async def`            ~ a method returning CompletableFuture<T>.
  * `await x`              ~ `.join()` / `.get()`, but it YIELDS the event loop
                            instead of blocking a thread (cooperative, not
                            thread-pool based).
  * `asyncio.gather(*t)`   ~ `CompletableFuture.allOf(...).join()` then collect.
  * `async for` generator  ~ a streaming/reactive Publisher (Flux/Stream).

KEY DIFFERENCE: there is ONE event loop on ONE thread. If you `await`, control
returns to the loop and other coroutines progress. If you call a BLOCKING
function (e.g. time.sleep, blocking JDBC), you freeze the whole loop — the
cardinal async sin. Use awaitable equivalents (asyncio.sleep) instead.

This file is FULLY OFFLINE: instead of real HTTP, it simulates network calls
with asyncio.sleep so it runs anywhere with no dependencies.

Run it:  python 04_async_basics.py
"""

from __future__ import annotations

import asyncio
import logging
import random

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# A single async "fetch" — simulated. In a real app this would be:
#   async with httpx.AsyncClient(timeout=30.0) as client:
#       resp = await client.get(url); resp.raise_for_status(); return resp.json()
# Here we sleep a random amount to mimic variable network latency.
# ---------------------------------------------------------------------------
async def fetch_data(url: str) -> dict[str, object]:
    """Simulate an async HTTP GET that returns JSON-like data.

    Java: CompletableFuture.supplyAsync(() -> webClient.get(url));
    """
    latency = random.uniform(0.05, 0.25)
    await asyncio.sleep(latency)  # NON-blocking sleep — yields the event loop
    # Simulate the occasional failure so we can show error handling in gather.
    if url.endswith("/boom"):
        raise ConnectionError(f"simulated failure for {url}")
    return {"url": url, "latency_ms": round(latency * 1000), "ok": True}


# ---------------------------------------------------------------------------
# Fan-out / fan-in — run many fetches concurrently and join results.
# return_exceptions=True means a single failure does NOT cancel the others;
# failures arrive as Exception objects we filter out. (In Java you'd handle
# each future's exceptionally(...) before allOf.)
# ---------------------------------------------------------------------------
async def fetch_all(urls: list[str]) -> list[dict[str, object]]:
    """Run fetches concurrently; drop the ones that failed."""
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    good = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]
    for err in failed:
        logger.warning("dropped failed fetch: %s", err)
    return good  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Async generator — streaming token-by-token, like an LLM streaming response.
# `yield` inside `async def` makes this an async generator; consume with
# `async for`. Analogous to a reactive Flux<String> emitting tokens.
# ---------------------------------------------------------------------------
async def stream_tokens(prompt: str):
    """Yield words one at a time with a small delay (simulated streaming)."""
    for word in prompt.split():
        await asyncio.sleep(0.05)  # simulate per-token network delay
        yield word + " "


async def collect_stream(prompt: str) -> str:
    """Consume the async generator and assemble the full text."""
    chunks: list[str] = []
    async for token in stream_tokens(prompt):
        chunks.append(token)
    return "".join(chunks).strip()


async def main() -> None:
    # 1) Concurrent fan-out — three "HTTP" calls + one that fails on purpose.
    urls = [
        "https://api.example.com/a",
        "https://api.example.com/b",
        "https://api.example.com/boom",  # this one raises
    ]
    results = await fetch_all(urls)
    logger.info("fetch_all returned %d successful result(s): %s", len(results), results)

    # 2) Streaming consumption.
    text = await collect_stream("Hello streaming world from asyncio")
    logger.info("collected stream -> %r", text)


# asyncio.run(...) creates the event loop, runs the coroutine, then closes it.
# It is the async equivalent of a `public static void main` entry point.
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    asyncio.run(main())
    logger.info("Async basics demo complete.")
