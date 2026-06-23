"""
10.1 — Rate Limiting + Exponential Backoff (runs fully OFFLINE)
================================================================

What this file demonstrates
---------------------------
1. ``TokenBucketLimiter``  — a sliding-window rate limiter that caps how many
   LLM calls leave your process per minute. This is your client-side defence
   against provider 429s.
       Java analogy: Bucket4j ``Bucket`` / Resilience4j ``RateLimiter`` —
       you acquire a permit before doing work; if none is free you wait.

2. ``retry_on_error``      — a decorator that retries a coroutine with
   *exponential backoff + jitter* and only on *retryable* exceptions.
       Java analogy: Spring Retry ``@Retryable(backoff = @Backoff(...))`` or
       Resilience4j ``Retry`` with an ``IntervalFunction.ofExponentialBackoff``.

3. ``resilient_llm_call``  — a mock async "LLM" wrapped by both of the above.
   The mock raises a transient error on a fixed schedule so you can SEE the
   backoff working without spending a cent or needing an API key.

OFFLINE NOTE
------------
``USE_MOCK = True`` routes every call through ``_mock_llm_create`` which never
touches the network. To run against the real provider, set ``USE_MOCK = False``,
fill ``ANTHROPIC_API_KEY`` (see ``.env.example``), ``pip install anthropic`` and
follow the inline TODO inside ``_real_llm_create``.

Run:  python3 01_rate_limiting_backoff.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import random
import time
from collections import deque
from functools import wraps
from typing import Awaitable, Callable, Deque, Tuple, Type, TypeVar

# --------------------------------------------------------------------------- #
# Logging — never print secrets here. In prod ship JSON logs to your platform.
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("rate_limit")

# Flip to False + install `anthropic` + set ANTHROPIC_API_KEY to go live.
USE_MOCK: bool = True

T = TypeVar("T")


# --------------------------------------------------------------------------- #
# Retryable vs non-retryable errors
# --------------------------------------------------------------------------- #
# Critical lesson: NEVER blindly retry every exception. A 400 (bad request) or
# a 401 (bad key) will fail identically on every attempt — retrying just wastes
# your retry budget and hammers the provider. Only retry *transient* faults:
# 429 (rate limit), 5xx (server), timeouts, connection resets.
#   Java analogy: Spring Retry's `retryFor = {...}` / `noRetryFor = {...}`,
#   or Resilience4j `retryOnException(Predicate)`.
class TransientLLMError(Exception):
    """Transient fault (429 / 5xx / timeout) — safe to retry."""


class FatalLLMError(Exception):
    """Permanent fault (400 / 401 / 403) — retrying is pointless."""


# --------------------------------------------------------------------------- #
# 1. Token-bucket / sliding-window rate limiter
# --------------------------------------------------------------------------- #
class TokenBucketLimiter:
    """Async sliding-window rate limiter.

    Allows at most ``calls_per_minute`` ``acquire()`` calls in any rolling 60s
    window. When the window is full, ``acquire()`` awaits (non-blocking) until
    the oldest call ages out.

    Java analogy: Bucket4j ``Bucket`` with a ``Bandwidth`` of N tokens / minute,
    or Resilience4j ``RateLimiter`` — both gate work behind a permit.

    Note on concurrency: a single ``asyncio`` event loop runs one coroutine at a
    time, so the read-modify-write of ``self.calls`` is already atomic between
    ``await`` points. We add an ``asyncio.Lock`` so the *check-then-sleep* across
    an ``await`` stays correct when many coroutines pile up at once.
    """

    def __init__(self, calls_per_minute: int) -> None:
        if calls_per_minute <= 0:
            raise ValueError("calls_per_minute must be positive")
        self.limit: int = calls_per_minute
        self.window_seconds: float = 60.0
        self._calls: Deque[float] = deque()
        self._lock = asyncio.Lock()

    def _evict_expired(self, now: float) -> None:
        """Drop timestamps older than the window's left edge."""
        cutoff = now - self.window_seconds
        while self._calls and self._calls[0] < cutoff:
            self._calls.popleft()

    async def acquire(self) -> None:
        """Block (cooperatively) until a permit is available, then consume it."""
        async with self._lock:
            now = time.monotonic()
            self._evict_expired(now)

            if len(self._calls) >= self.limit:
                # Wait just long enough for the oldest call to fall out of the
                # window (+ small pad to avoid a race on the boundary).
                wait = self.window_seconds - (now - self._calls[0]) + 0.05
                logger.warning("Rate limit hit (%d/min) — waiting %.2fs",
                               self.limit, wait)
                # await asyncio.sleep, NOT time.sleep: time.sleep would block the
                # whole event loop (the classic Java-dev mistake when going async).
                await asyncio.sleep(wait)
                now = time.monotonic()
                self._evict_expired(now)

            self._calls.append(time.monotonic())

    @property
    def in_flight(self) -> int:
        """Calls currently counted inside the live window (best-effort)."""
        self._evict_expired(time.monotonic())
        return len(self._calls)


# A generous default; tune per your provider's published limits.
limiter = TokenBucketLimiter(calls_per_minute=50)


# --------------------------------------------------------------------------- #
# 2. Exponential-backoff retry decorator (with jitter + selective retry)
# --------------------------------------------------------------------------- #
def retry_on_error(
    max_retries: int = 3,
    base_delay: float = 0.5,
    backoff: float = 2.0,
    max_delay: float = 30.0,
    jitter: float = 0.25,
    retry_on: Tuple[Type[Exception], ...] = (TransientLLMError,),
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator: retry an async fn with exponential backoff + jitter.

    delay(attempt) = min(base_delay * backoff**attempt, max_delay)
                     then multiplied by a random factor in [1-jitter, 1+jitter].

    Why jitter? If 100 clients all fail at the same instant and all back off by
    *exactly* 2s, they retry in lockstep and create a "thundering herd" that
    re-triggers the outage. Jitter de-synchronises them. AWS's "Exponential
    Backoff and Jitter" article is the canonical reference.

    Why ``retry_on``? Only transient errors are retried; a ``FatalLLMError``
    propagates immediately so we don't burn the budget on a request that can
    never succeed.

    Java analogy: Spring Retry ``@Retryable(maxAttempts, backoff=@Backoff(
    delay, multiplier, maxDelay))`` plus ``retryFor`` to scope the exceptions.
    """

    def decorator(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(fn)
        async def wrapper(*args: object, **kwargs: object) -> T:
            attempt = 0
            while True:
                try:
                    await limiter.acquire()  # rate-limit each *attempt*
                    return await fn(*args, **kwargs)
                except retry_on as exc:  # only catch what we declared retryable
                    attempt += 1
                    if attempt >= max_retries:
                        logger.error("Exhausted %d retries: %s", max_retries, exc)
                        raise
                    raw = base_delay * (backoff ** (attempt - 1))
                    capped = min(raw, max_delay)
                    factor = 1.0 + random.uniform(-jitter, jitter)
                    delay = round(capped * factor, 3)
                    logger.warning(
                        "Attempt %d/%d failed (%s) — retrying in %.2fs",
                        attempt, max_retries, exc, delay,
                    )
                    await asyncio.sleep(delay)
                # FatalLLMError (and anything not in retry_on) is NOT caught here
                # and propagates straight to the caller — by design.

        return wrapper

    return decorator


# --------------------------------------------------------------------------- #
# 3. The "LLM" call — mock by default, real client behind a flag
# --------------------------------------------------------------------------- #
# A deterministic, self-resetting failure schedule so the demo is reproducible:
# the first call to a fresh prompt fails twice, then succeeds.
_attempt_counter: dict[str, int] = {}


async def _mock_llm_create(prompt: str) -> str:
    """Offline stand-in for the provider SDK. Fails transiently, then succeeds."""
    await asyncio.sleep(0.02)  # simulate network latency without blocking loop
    n = _attempt_counter.get(prompt, 0)
    _attempt_counter[prompt] = n + 1
    if n < 2:  # fail the first two attempts to showcase backoff
        raise TransientLLMError(f"simulated 503 (attempt {n + 1})")
    return f"[mock-reply] You said: {prompt[:60]!r}"


async def _real_llm_create(prompt: str) -> str:
    """Live provider call. Only used when USE_MOCK is False."""
    # TODO (to go live):
    #   1) pip install anthropic
    #   2) export ANTHROPIC_API_KEY=...   (see .env.example)
    #   3) Uncomment the block below and delete the RuntimeError.
    #
    # from anthropic import AsyncAnthropic
    # from anthropic import APIStatusError, APIConnectionError, RateLimitError
    # client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    # try:
    #     resp = await client.messages.create(
    #         model="claude-sonnet-4-6",
    #         max_tokens=1024,
    #         messages=[{"role": "user", "content": prompt}],
    #     )
    #     return resp.content[0].text
    # except (RateLimitError, APIConnectionError) as e:        # 429 / network
    #     raise TransientLLMError(str(e)) from e
    # except APIStatusError as e:
    #     if e.status_code >= 500:                             # 5xx -> retry
    #         raise TransientLLMError(str(e)) from e
    #     raise FatalLLMError(str(e)) from e                   # 4xx -> don't
    _ = os.environ.get("ANTHROPIC_API_KEY")  # referenced for clarity
    raise RuntimeError("Set USE_MOCK=False and complete the TODO to go live.")


@retry_on_error(max_retries=4, base_delay=0.2)
async def resilient_llm_call(prompt: str) -> str:
    """Public entry point: rate-limited + retried LLM call."""
    if USE_MOCK:
        return await _mock_llm_create(prompt)
    return await _real_llm_create(prompt)


# --------------------------------------------------------------------------- #
# Demo
# --------------------------------------------------------------------------- #
async def _demo() -> None:
    logger.info("=== Demo 1: backoff recovers from transient failures ===")
    reply = await resilient_llm_call("Explain token-bucket rate limiting.")
    logger.info("Got reply: %s", reply)

    logger.info("=== Demo 2: fatal errors are NOT retried ===")

    @retry_on_error(max_retries=4, base_delay=0.1)
    async def _always_fatal() -> str:
        raise FatalLLMError("simulated 400 bad_request")

    t0 = time.monotonic()
    try:
        await _always_fatal()
    except FatalLLMError as e:
        elapsed = time.monotonic() - t0
        logger.info("Fatal error surfaced immediately in %.3fs (no retries): %s",
                    elapsed, e)

    logger.info("=== Demo 3: rate limiter serialises a concurrent burst ===")
    burst = TokenBucketLimiter(calls_per_minute=120)
    global limiter  # reuse the decorator's limiter for this demo
    saved, limiter = limiter, burst
    try:
        # Pre-seed the counter so each distinct prompt succeeds on its 3rd
        # attempt with no failures here — we want to observe pure throughput.
        for i in range(5):
            _attempt_counter[f"quick-{i}"] = 2

        async def _quick(i: int) -> str:
            return await resilient_llm_call(f"quick-{i}")

        results = await asyncio.gather(*[_quick(i) for i in range(5)])
        logger.info("Burst of %d calls done; limiter in-flight=%d/%d",
                    len(results), limiter.in_flight, limiter.limit)
    finally:
        limiter = saved


if __name__ == "__main__":
    asyncio.run(_demo())
