"""
01_langsmith_tracing.py — Phase 9.1: LangSmith tracing (offline-safe).

WHAT THIS SHOWS
    LangSmith is to an agent what Jaeger/Zipkin/Sleuth is to a Spring service:
    a distributed-tracing backend that captures a TRACE (the whole request) made
    of nested SPANS (each LLM call, tool call, chain step) with inputs, outputs,
    latency and metadata attached. Setting three env vars auto-instruments every
    LangChain/LangGraph call — the zero-code-change equivalent of dropping the
    Sleuth starter on your classpath. `@traceable` wraps YOUR own functions so
    they show up as their own span, like Micrometer's `@Observed`.

OFFLINE NOTE
    This file requires NO API key and NO network. We set the env vars exactly as
    you would in production, but `@traceable` is applied to a MOCK pipeline so it
    runs locally. If `langsmith` is not installed, we fall back to a no-op
    `traceable` so the demo still runs. To go live, see TODO markers below.

    Run:  python 01_langsmith_tracing.py
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Set LangSmith env vars BEFORE any LangChain/LangSmith import.
#
# This is the #1 Java-dev gotcha. Auto-instrumentation reads LANGCHAIN_TRACING_V2
# at IMPORT TIME. Setting it after `import langchain...` gives silent no-tracing —
# the equivalent of configuring Sleuth too late to wire its interceptors.
# So these three lines come first, on purpose.
# ─────────────────────────────────────────────────────────────────────────────
import os

os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
# TODO(real): replace with your real key, e.g. "ls__abc123...". Offline default is a placeholder.
os.environ.setdefault("LANGCHAIN_API_KEY", "ls__OFFLINE_PLACEHOLDER_NO_NETWORK")
# A LangSmith PROJECT is just a named bucket of traces — like a Jaeger service name.
# Use one per environment so dev noise never pollutes prod traces.
os.environ.setdefault("LANGCHAIN_PROJECT", "agentic-ai-dev")

import logging
import time
from typing import Any, Callable, TypeVar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("phase9.tracing")

F = TypeVar("F", bound=Callable[..., Any])


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Import `traceable`, with an offline-safe fallback.
#
# In production this is simply `from langsmith import traceable`. Offline (or if
# langsmith is not installed) we provide a no-op decorator with the SAME signature
# so the rest of the file is identical to the real thing — only the backend differs.
# ─────────────────────────────────────────────────────────────────────────────
try:
    from langsmith import traceable  # type: ignore

    _LANGSMITH_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only when package is absent
    _LANGSMITH_AVAILABLE = False

    def traceable(  # type: ignore[no-redef]
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        **_kwargs: Any,
    ) -> Callable[[F], F]:
        """No-op stand-in for langsmith.traceable so this demo runs with no install.

        Mirrors the real decorator's call shape `@traceable(name=..., metadata=...)`.
        Java analogy: a Micrometer `@Observed` that points at a no-op MeterRegistry.
        """

        def decorator(fn: F) -> F:
            return fn

        return decorator


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — A MOCK pipeline so there is something to trace offline.
#
# In production these would be real LangChain primitives (a retriever + an LLM).
# Here they are deterministic stand-ins so the demo prints real output with no key.
# Each helper is itself `@traceable`, so in a real run they would appear as NESTED
# spans under the parent pipeline span — exactly the call tree you read in Jaeger.
# ─────────────────────────────────────────────────────────────────────────────
@traceable(name="retrieve_docs", metadata={"component": "retriever"})
def _mock_retrieve(query: str) -> list[str]:
    """Pretend vector search. TODO(real): `return retriever.invoke(query)`."""
    time.sleep(0.02)  # simulate I/O latency so the span has a measurable duration
    return [
        f"doc#1 about '{query}'",
        f"doc#2 about '{query}'",
    ]


@traceable(name="generate_answer", metadata={"component": "llm", "model": "mock-sonnet"})
def _mock_generate(query: str, docs: list[str]) -> str:
    """Pretend LLM call. TODO(real): `return llm.invoke(prompt).content`."""
    time.sleep(0.03)
    return f"Answer to '{query}' grounded in {len(docs)} document(s)."


# This is the function a real app would expose. `@traceable` makes it the PARENT span,
# carrying metadata you'd filter by in LangSmith (version, tenant, feature flag, ...).
@traceable(name="My RAG Pipeline", metadata={"version": "1.2", "tenant": "demo"})
def my_pipeline(query: str) -> str:
    """End-to-end mock RAG pipeline.

    TODO(real): replace the two mock calls below with `return rag_chain.invoke(query)`.
    With the env vars set above, the real chain auto-traces to smith.langchain.com.
    """
    docs = _mock_retrieve(query)
    answer = _mock_generate(query, docs)
    return answer


def main() -> None:
    """Demo entry point — prints config, runs the traced pipeline, reports status."""
    logger.info("LangSmith tracing demo (offline-safe)")
    logger.info("  LANGCHAIN_TRACING_V2 = %s", os.environ["LANGCHAIN_TRACING_V2"])
    logger.info("  LANGCHAIN_PROJECT    = %s", os.environ["LANGCHAIN_PROJECT"])
    logger.info(
        "  LANGCHAIN_API_KEY    = %s (masked)",
        os.environ["LANGCHAIN_API_KEY"][:6] + "…",  # never log full secrets / keys
    )
    logger.info(
        "  langsmith installed  = %s%s",
        _LANGSMITH_AVAILABLE,
        "" if _LANGSMITH_AVAILABLE else "  -> using no-op traceable fallback",
    )

    queries = ["What is observability?", "Why trace agents?"]
    for q in queries:
        try:
            result = my_pipeline(q)
            logger.info("Query=%r  ->  %s", q, result)
        except Exception:  # an aspect observes failures; it must not hide them
            logger.exception("Pipeline failed for query=%r", q)
            raise

    if _LANGSMITH_AVAILABLE and not os.environ["LANGCHAIN_API_KEY"].endswith("PLACEHOLDER_NO_NETWORK"):
        logger.info("Traces should now be visible at https://smith.langchain.com")
    else:
        logger.info(
            "Offline mode: no traces were sent. Set a real LANGCHAIN_API_KEY and "
            "install `langsmith` to view spans in the LangSmith UI (the Jaeger of agents)."
        )


if __name__ == "__main__":
    main()
