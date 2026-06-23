"""
03_structured_logging.py — Phase 9.3: structured logging + @logged_node (REAL, runs as-is).

WHAT THIS SHOWS
    Python's `logging` is the direct counterpart of SLF4J/Logback:
      * logging.basicConfig(...)      ≈ logback.xml (level + <pattern> + appenders)
      * logging.StreamHandler()       ≈ console appender
      * logging.FileHandler(...)      ≈ rolling-file appender
      * logging.getLogger("name")     ≈ LoggerFactory.getLogger(...)
    The `@logged_node` decorator is an AOP `@Around` advice expressed in Python: it
    logs on ENTER, calls the real node (joinPoint.proceed()), logs on EXIT with
    timing, and on failure logs the exception AND RE-RAISES it — it never swallows
    the error, which is the cardinal sin that makes agent failures invisible.

OFFLINE NOTE
    This module is fully REAL — no mocks, no key, no network. It configures logging
    and runs three decorated nodes (one of which deliberately fails) so you can see
    enter/exit/error lines on the console and in a dated log file.

    Run:  python 03_structured_logging.py
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, TypeVar

# ─────────────────────────────────────────────────────────────────────────────
# Configure logging once, at startup — this is your logback.xml equivalent.
# Two handlers = two appenders: console (live tail) + dated file (greppable / shippable).
# In production you'd swap `format` for a JSON formatter so logs are queryable in
# your aggregator — the same reason you reach for logstash-logback-encoder in Spring.
# ─────────────────────────────────────────────────────────────────────────────
_LOG_FILE = f"agent_{datetime.now():%Y%m%d}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",  # ≈ Logback <pattern>
    handlers=[
        logging.StreamHandler(),          # ≈ console appender
        logging.FileHandler(_LOG_FILE),   # ≈ rolling-file appender
    ],
)
logger = logging.getLogger("agentic-ai")  # ≈ LoggerFactory.getLogger("agentic-ai")

# Type var so the decorator preserves the wrapped function's signature for tooling.
NodeFn = TypeVar("NodeFn", bound=Callable[[dict[str, Any]], dict[str, Any]])


# ─────────────────────────────────────────────────────────────────────────────
# The @logged_node decorator — the AOP @Around advice of the agent world.
# ─────────────────────────────────────────────────────────────────────────────
def logged_node(node_name: str) -> Callable[[NodeFn], NodeFn]:
    """Wrap a graph node so entry, timing, exit and errors are logged automatically.

    Java analogy: an `@Around` aspect over every node method —
        @Around("execution(* nodes..*(..))")
        Object log(ProceedingJoinPoint pjp) { /* before; pjp.proceed(); after */ }
    Implemented here as a decorator. `@wraps(fn)` is the Python equivalent of making
    the proxy keep the original method's name/metadata, so logs and introspection
    still read correctly.
    """

    def decorator(fn: NodeFn) -> NodeFn:
        @wraps(fn)
        def wrapper(state: dict[str, Any]) -> dict[str, Any]:
            t0 = time.perf_counter()
            # Log the STATE KEYS, not the values — values can contain prompts with
            # secrets/PII. Logging the whole prompt at INFO is the agentic version of
            # logging request bodies with passwords in them. Keys are safe + useful.
            logger.info("→ [%s] State keys: %s", node_name, list(state.keys()))
            try:
                result = fn(state)                                   # joinPoint.proceed()
                elapsed = time.perf_counter() - t0
                logger.info("← [%s] Done in %.3fs", node_name, elapsed)
                return result
            except Exception as exc:
                # Log the error WITH stack trace, THEN re-raise. Never swallow:
                # a swallowed exception makes the node look successful while it
                # corrupts downstream state — the worst kind of invisible bug.
                logger.error("✗ [%s] FAILED: %s", node_name, exc, exc_info=True)
                raise

        return wrapper  # type: ignore[return-value]

    return decorator


# ─────────────────────────────────────────────────────────────────────────────
# Three demo nodes. `process_query` mirrors the roadmap snippet; `flaky_node`
# deliberately raises so you can see the error path log + propagate.
# ─────────────────────────────────────────────────────────────────────────────
@logged_node("process_query")
def process_node(state: dict[str, Any]) -> dict[str, Any]:
    """Pretend LLM step. TODO(real): response = llm.invoke(state["messages"])."""
    time.sleep(0.02)
    messages = state["messages"] + [{"role": "assistant", "content": "processed"}]
    return {"messages": messages}


@logged_node("enrich")
def enrich_node(state: dict[str, Any]) -> dict[str, Any]:
    """Add a derived field; demonstrates a fast, successful node."""
    return {"token_estimate": sum(len(m["content"]) for m in state["messages"])}


@logged_node("flaky_step")
def flaky_node(state: dict[str, Any]) -> dict[str, Any]:
    """Intentionally fails to demonstrate the error path (log + re-raise)."""
    raise ValueError("simulated downstream tool timeout")


def main() -> None:
    """Run the happy path, then trigger the error path to show log + propagation."""
    logger.info("Structured logging demo — writing to console and %s", _LOG_FILE)

    state: dict[str, Any] = {"messages": [{"role": "user", "content": "hello agent"}]}

    # ── Happy path: chain two decorated nodes ───────────────────────────────
    state.update(process_node(state))
    state.update(enrich_node(state))
    logger.info("Final state (keys=%s) -> %s", list(state.keys()),
                json.dumps(state, default=str))

    # ── Error path: prove the exception is logged AND propagates to the caller ─
    logger.info("Now invoking a node that fails on purpose …")
    try:
        flaky_node(state)
    except ValueError as exc:
        # The decorator already logged the full traceback; the caller still sees it.
        logger.info("Caller received the re-raised error as expected: %s", exc)

    print(f"\nDone. Inspect the dated log file for the same lines: {_LOG_FILE}")


if __name__ == "__main__":
    main()
