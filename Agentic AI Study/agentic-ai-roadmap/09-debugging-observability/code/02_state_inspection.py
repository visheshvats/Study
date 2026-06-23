"""
02_state_inspection.py — Phase 9.2: state inspection (offline-safe mock graph).

WHAT THIS SHOWS
    A LangGraph graph carries a STATE that every node reads/writes; with
    checkpointing it saves a STATE SNAPSHOT at every step. Inspecting these is two
    things at once:
      * `get_state(config)`         -> the CURRENT snapshot. Like pausing on a
                                       debugger breakpoint: inspect locals + see
                                       which line (node) runs next via `state.next`.
      * `get_state_history(config)` -> EVERY snapshot since the run started, newest
                                       first. Your time-travel debugger / audit log
                                       of how the agent's reasoning evolved.
    The `thread_id` in `config` is the correlation id for a run — like the traceId
    Spring Cloud Sleuth threads through everything, so all signals line up.

OFFLINE NOTE
    No LangGraph runtime, key, or network is needed. We build a TINY MOCK graph
    that records a snapshot per step and exposes `get_state` / `get_state_history`
    with the SAME shape as the real API (`.values`, `.next`, `.created_at`,
    `.metadata`). To use a real graph instead, see TODO markers at the bottom.

    Run:  python 02_state_inspection.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("phase9.state")


# ─────────────────────────────────────────────────────────────────────────────
# Snapshot shape — mirrors a real LangGraph StateSnapshot closely enough for a demo.
# Real attributes used in the roadmap: .values, .next, .created_at, .metadata.
# ─────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class StateSnapshot:
    """One checkpoint of graph state. Like a row in an audit log."""

    values: dict[str, Any]
    next: tuple[str, ...]          # node(s) about to run — like "next line" at a breakpoint
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


# A node is just a function state -> partial-state-update, same contract as LangGraph.
Node = Callable[[dict[str, Any]], dict[str, Any]]


class MockGraph:
    """A stand-in for a compiled LangGraph that records a snapshot per step.

    TODO(real): delete this class and build a real graph:
        from langgraph.graph import StateGraph
        from langgraph.checkpoint.memory import MemorySaver
        graph = builder.compile(checkpointer=MemorySaver())
    A real graph exposes `get_state(config)` / `get_state_history(config)` with the
    very same semantics demonstrated here — only the backing store differs.
    """

    def __init__(self, nodes: list[tuple[str, Node]]) -> None:
        self._nodes = nodes
        # threads maps thread_id -> list of snapshots (oldest first internally).
        self._threads: dict[str, list[StateSnapshot]] = {}

    @staticmethod
    def _thread_id(config: dict[str, Any]) -> str:
        # Real LangGraph reads config["configurable"]["thread_id"] — match that exactly.
        return config["configurable"]["thread_id"]

    def invoke(self, initial_state: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        """Run all nodes in order, checkpointing a snapshot before each step.

        Each snapshot's `next` is the node that is ABOUT to run, mirroring how a
        real graph reports `state.next` at a checkpoint.
        """
        thread = self._thread_id(config)
        history: list[StateSnapshot] = []
        state: dict[str, Any] = dict(initial_state)

        for step, (name, fn) in enumerate(self._nodes):
            # Snapshot the state as it stands BEFORE running this node.
            history.append(
                StateSnapshot(
                    values=dict(state),
                    next=(name,),
                    created_at=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                    metadata={"step": step, "source": name},
                )
            )
            update = fn(state)              # node returns a partial update, like LangGraph
            state.update(update)            # merge into running state

        # Final snapshot: nothing left to run, so `next` is empty.
        history.append(
            StateSnapshot(
                values=dict(state),
                next=(),
                created_at=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                metadata={"step": len(self._nodes), "source": "__end__"},
            )
        )
        self._threads[thread] = history
        return state

    def get_state(self, config: dict[str, Any]) -> StateSnapshot:
        """Return the CURRENT (latest) snapshot — the breakpoint view."""
        thread = self._thread_id(config)
        history = self._threads.get(thread)
        if not history:
            raise KeyError(f"No state for thread_id={thread!r}; run invoke() first.")
        return history[-1]

    def get_state_history(self, config: dict[str, Any]) -> Iterator[StateSnapshot]:
        """Yield ALL snapshots, NEWEST FIRST — matching real LangGraph ordering."""
        thread = self._thread_id(config)
        history = self._threads.get(thread, [])
        yield from reversed(history)


# ─────────────────────────────────────────────────────────────────────────────
# Three trivial nodes so the state visibly grows step by step.
# State carries a `messages` list (the conventional LangGraph key) plus a `step` tag.
# ─────────────────────────────────────────────────────────────────────────────
def classify_node(state: dict[str, Any]) -> dict[str, Any]:
    msgs = state["messages"] + [{"role": "system", "content": "classified: question"}]
    return {"messages": msgs, "intent": "qa"}


def retrieve_node(state: dict[str, Any]) -> dict[str, Any]:
    msgs = state["messages"] + [{"role": "tool", "content": "retrieved 2 docs"}]
    return {"messages": msgs, "doc_count": 2}


def answer_node(state: dict[str, Any]) -> dict[str, Any]:
    msgs = state["messages"] + [{"role": "assistant", "content": "Here is the answer."}]
    return {"messages": msgs, "done": True}


def main() -> None:
    """Build the mock graph, run it, then print current state + full history."""
    graph = MockGraph(
        [
            ("classify", classify_node),
            ("retrieve", retrieve_node),
            ("answer", answer_node),
        ]
    )

    # thread_id == correlation id for this run (Sleuth's traceId equivalent).
    config = {"configurable": {"thread_id": "debug-001"}}
    initial = {"messages": [{"role": "user", "content": "What is state inspection?"}]}

    logger.info("Running mock graph for thread_id=%s …", config["configurable"]["thread_id"])
    graph.invoke(initial, config)

    # ── Current state: the "breakpoint" view ────────────────────────────────
    state = graph.get_state(config)
    print("\n=== CURRENT STATE (get_state) — breakpoint view ===")
    print(f"Current values keys : {list(state.values.keys())}")
    print(f"Message count       : {len(state.values.get('messages', []))}")
    print(f"Next node           : {state.next or '(none — run complete)'}")
    print(f"Created at          : {state.created_at}")

    # ── Full history: the "audit log" / time-travel view ────────────────────
    print("\n=== STATE HISTORY (get_state_history) — newest first, audit log ===")
    for snapshot in graph.get_state_history(config):
        step = snapshot.metadata.get("step", 0)
        node = snapshot.metadata.get("source", "unknown")
        msg_count = len(snapshot.values.get("messages", []))
        nxt = snapshot.next[0] if snapshot.next else "—"
        print(f"Step {step:02d} | Node: {node:12s} | Messages: {msg_count} | Next: {nxt}")

    print(
        "\nRead bottom-to-top to replay chronologically: each step adds a message "
        "and updates state — exactly how you'd trace why an agent's reasoning went."
    )


if __name__ == "__main__":
    main()
