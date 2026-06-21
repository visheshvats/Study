"""03_parallelization.py - fan-out / fan-in with asyncio.gather (Phase 4.3).

PATTERN: Parallelization. Run several INDEPENDENT analyses on the same input at
the same time, then combine the results.

    text --> sentiment    \\
         --> topics         >--> combine --> report
         --> readability   //
    (fan-out: 3 concurrent)   (fan-in: join)

Java analogy: `ExecutorService.invokeAll(tasks)` or composing
`CompletableFuture.supplyAsync(...)` and joining with `allOf(...).join()`. Each
analysis is an independent task; you submit them all, then collect. `asyncio`
is Python's single-threaded cooperative concurrency: while one task waits on I/O
(a model call), the event loop runs another. `asyncio.gather(a, b, c)` is the
join point - it awaits all coroutines and returns their results IN ORDER.

CRITICAL for Java devs (notes.md mistakes list): `llm.invoke(...)` is a BLOCKING
call. Calling it directly inside an `async def` would block the whole event loop
and serialise everything - you'd get NO speedup. You must hand it to a worker
thread with `await asyncio.to_thread(llm.invoke, ...)`, which is like submitting
the blocking call to an `ExecutorService` so the event-loop thread stays free.

WHEN TO USE: independent subtasks with no data dependency between them. If step B
needs step A's output, that is chaining (01), not parallelization.

OFFLINE BY DEFAULT + REAL SPEEDUP
---------------------------------
USE_MOCK = True uses a FakeChatModel whose `.invoke` SLEEPS for a fixed latency
to simulate a network round-trip. main() runs the 3 analyses sequentially and
then with gather, and prints the MEASURED wall-clock times and speedup. Because
the mock blocks (via time.sleep) and we dispatch it with asyncio.to_thread, the
parallel path is genuinely ~3x faster - proving the mechanic, no API key needed.

Run it (offline):  python 03_parallelization.py
Real model:        set USE_MOCK = False, then export ANTHROPIC_API_KEY
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, TypedDict

from langchain_core.messages import AIMessage, HumanMessage

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# USE_MOCK: offline switch. True = FakeChatModel (with simulated latency).
# ---------------------------------------------------------------------------
USE_MOCK = True

# Simulated per-call latency for the mock, in seconds. With 3 calls, sequential
# ~= 3 * this; parallel ~= 1 * this (plus small overhead). Tune to taste.
MOCK_LATENCY_S = 0.5


class FakeChatModel:
    """Deterministic offline LLM that SLEEPS to imitate a network round-trip.

    The sleep is what makes the speedup measurable: three sequential calls take
    ~3x one call, while three concurrent calls (each dispatched to its own
    worker thread via asyncio.to_thread) overlap their sleeps and finish in ~1x.

    `.invoke` is intentionally BLOCKING (time.sleep, not asyncio.sleep) because a
    real ChatAnthropic client is blocking too - that is exactly why we need
    asyncio.to_thread around it. Replace with ChatAnthropic for real calls.
    """

    def __init__(self, latency_s: float = MOCK_LATENCY_S) -> None:
        self.latency_s = latency_s

    def invoke(self, messages: List[Any]) -> AIMessage:
        time.sleep(self.latency_s)  # blocking, on purpose (simulated I/O wait)
        text = " ".join(str(getattr(m, "content", m)) for m in messages).lower()
        if "sentiment" in text:
            return AIMessage(content="7/10 - largely positive, with measured optimism.")
        if "topics" in text:
            return AIMessage(content='["performance", "caching", "cost", "reliability", "rollout"]')
        if "readability" in text:
            return AIMessage(content="8/10 - clear, short sentences; minimal jargon.")
        return AIMessage(content="[MOCK] generic analysis")


def build_llm() -> Any:
    """Factory: FakeChatModel offline, ChatAnthropic when USE_MOCK = False."""
    if USE_MOCK:
        logger.info("Using FakeChatModel (offline, simulated %.2fs latency).", MOCK_LATENCY_S)
        return FakeChatModel()

    # pip install langchain-anthropic ; export ANTHROPIC_API_KEY=...
    from langchain_anthropic import ChatAnthropic

    logger.info("Using real ChatAnthropic(model='claude-sonnet-4-6').")
    return ChatAnthropic(model="claude-sonnet-4-6")


llm = build_llm()


# ---------------------------------------------------------------------------
# THE THREE INDEPENDENT ANALYSES. Each wraps the BLOCKING llm.invoke in
# asyncio.to_thread so it does not freeze the event loop. Each also has its own
# try/except so ONE failing analysis returns an error string instead of taking
# the whole gather down (return_exceptions is the other option; see below).
# ---------------------------------------------------------------------------
async def _safe_call(label: str, prompt: str) -> str:
    """Run one blocking llm.invoke on a worker thread, guarding it."""
    try:
        # asyncio.to_thread == "submit this blocking call to a thread pool and
        # await the result" - i.e. ExecutorService.submit(...).get(), but
        # non-blocking for the event loop.
        result = await asyncio.to_thread(llm.invoke, [HumanMessage(content=prompt)])
        return str(result.content)
    except Exception as exc:  # noqa: BLE001
        logger.exception("analysis %r failed", label)
        return f"[{label} ERROR] {exc}"


async def analyze_parallel(text: str) -> Dict[str, str]:
    """Fan out 3 analyses concurrently, fan in with gather."""

    async def sentiment() -> str:
        return await _safe_call(
            "sentiment", f"Rate sentiment 1-10 with a one-line reason:\n{text}"
        )

    async def topics() -> str:
        return await _safe_call(
            "topics", f"List 5 main topics as JSON array. Return raw JSON only:\n{text}"
        )

    async def readability() -> str:
        return await _safe_call(
            "readability",
            f"Rate readability for a general audience (1=very hard, 10=very easy) "
            f"with brief explanation:\n{text}",
        )

    # FAN-OUT: all 3 coroutines start; the event loop runs them concurrently.
    # FAN-IN: gather awaits all and returns results IN THE ORDER OF THE ARGS
    # (not completion order!) - so unpacking sent/top/read is safe.
    sent, top, read = await asyncio.gather(sentiment(), topics(), readability())
    return {"sentiment": sent, "topics": top, "readability": read}


async def analyze_sequential(text: str) -> Dict[str, str]:
    """Same 3 analyses, but one after another - the SLOW baseline to compare."""
    sent = await _safe_call("sentiment", f"Rate sentiment 1-10 with a one-line reason:\n{text}")
    top = await _safe_call("topics", f"List 5 main topics as JSON array. Return raw JSON only:\n{text}")
    read = await _safe_call(
        "readability",
        f"Rate readability for a general audience (1=very hard, 10=very easy) with brief explanation:\n{text}",
    )
    return {"sentiment": sent, "topics": top, "readability": read}


# ---------------------------------------------------------------------------
# LANGGRAPH WIRING: a fan-out analysis node followed by a fan-in combine node.
# (The source's run_parallel_analysis used asyncio.run inside a sync node; we
# keep that shape so a graph can host the parallel work as one step.)
# ---------------------------------------------------------------------------
class ParallelState(TypedDict):
    text: str
    sentiment: str
    topics: str
    readability: str
    combined_report: str


def run_parallel_analysis(state: ParallelState) -> dict:
    """Sync graph node that drives the async fan-out via asyncio.run."""
    results = asyncio.run(analyze_parallel(state["text"]))
    return results


def combine_results(state: ParallelState) -> dict:
    """Fan-in: stitch the three independent results into one report."""
    report = (
        "# Document Analysis Report\n\n"
        f"## Sentiment\n{state['sentiment']}\n\n"
        f"## Topics\n{state['topics']}\n\n"
        f"## Readability\n{state['readability']}\n"
    )
    return {"combined_report": report}


def build_graph() -> Any:
    """analyze (fan-out) -> combine (fan-in) -> END."""
    from langgraph.graph import END, StateGraph

    builder = StateGraph(ParallelState)
    builder.add_node("analyze", run_parallel_analysis)
    builder.add_node("combine", combine_results)
    builder.set_entry_point("analyze")
    builder.add_edge("analyze", "combine")
    builder.add_edge("combine", END)
    return builder.compile()


async def _benchmark(text: str) -> None:
    """Time sequential vs parallel and print the real measured speedup."""
    t0 = time.perf_counter()
    seq = await analyze_sequential(text)
    seq_elapsed = time.perf_counter() - t0

    t0 = time.perf_counter()
    par = await analyze_parallel(text)
    par_elapsed = time.perf_counter() - t0

    speedup = seq_elapsed / par_elapsed if par_elapsed else float("inf")

    print("\n=== PARALLELIZATION: fan-out / fan-in ===\n")
    print("Parallel results (fan-in):")
    for k, v in par.items():
        print(f"  {k:<12}: {v}")
    print(f"\nSequential time : {seq_elapsed:6.3f}s  (3 calls back-to-back)")
    print(f"Parallel time   : {par_elapsed:6.3f}s  (gather of 3 concurrent calls)")
    print(f"Speedup         : {speedup:6.2f}x")
    # Sanity: ordering of gather results matches the argument order, not finish
    # order - so `seq` and `par` carry the same keys/meaning.
    assert set(seq) == set(par)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    text = (
        "Our platform team's performance overhaul added a caching layer and "
        "automatic retries, cut latency by 40 percent, and lowered monthly costs."
    )

    # 1) Measure the real speedup from gather.
    asyncio.run(_benchmark(text))

    # 2) Show the LangGraph fan-out/fan-in graph producing a combined report.
    graph = build_graph()
    logger.info("Graph as Mermaid:\n%s", graph.get_graph().draw_mermaid())
    final = graph.invoke(
        {
            "text": text,
            "sentiment": "",
            "topics": "",
            "readability": "",
            "combined_report": "",
        }
    )
    print("\n=== LangGraph combined report (fan-in node) ===")
    print(final["combined_report"])
    print("=== done ===")


if __name__ == "__main__":
    main()
