"""
Phase 11 · 11.2 — PostgreSQL Checkpointing (durable LangGraph state)
====================================================================

In dev you used `MemorySaver` (Phase 3) — state lives in the process and dies on
restart. In production you switch the checkpointer to `PostgresSaver` so a graph's
state survives deploys, crashes, and horizontal scaling: any worker can resume any
thread by `thread_id` because the truth is in Postgres, not local memory.

Java analogy
------------
`MemorySaver` == an in-memory `HashMap` of state. `PostgresSaver` == a JPA-backed
repository: durable, shared across nodes, survives restarts. The graph code doesn't
change — only which checkpointer you compile with (constructor injection of a
different bean).

Offline mode
------------
No Postgres in this sandbox, so `USE_MOCK = True` compiles the graph with a
`MemorySaver` and simulates a "restart" by REBUILDING the graph object against the
SAME saver instance — demonstrating that whoever holds the durable checkpointer can
resume the thread. With real Postgres the saver is external, so this works across
actual process restarts and machines.

Run:  python 02_postgres_checkpointing.py
"""

from __future__ import annotations

import logging
import os
from typing import Annotated, Any, TypedDict

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("pg-checkpoint")

USE_MOCK = True
DB_URI = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/agent_db")

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage
from langchain_core.messages import AIMessage


# ─────────────────────────────────────────────────────────────────────────────
# Offline fake chat model so graph mechanics run without an API key.
# Swap for `ChatAnthropic(model="claude-sonnet-4-6")`.
# ─────────────────────────────────────────────────────────────────────────────
class FakeChatModel:
    """Deterministic stand-in. Echoes the count of prior turns to prove recall."""

    def invoke(self, messages: list) -> AIMessage:
        last = messages[-1].content if messages else ""
        return AIMessage(content=f"Seen {len(messages)} msgs. You said: {last!r}")


def get_llm() -> Any:
    if USE_MOCK:
        return FakeChatModel()
    from langchain_anthropic import ChatAnthropic  # type: ignore

    return ChatAnthropic(model="claude-sonnet-4-6")


# ─────────────────────────────────────────────────────────────────────────────
# A tiny chat graph (the same shape as Phase 3.4).
# ─────────────────────────────────────────────────────────────────────────────
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]


def build_graph(checkpointer: Any):
    """Build + compile the graph with whatever checkpointer is injected."""
    llm = get_llm()

    def chat_node(state: ChatState) -> dict:
        return {"messages": [llm.invoke(state["messages"])]}

    builder = StateGraph(ChatState)
    builder.add_node("chat", chat_node)
    builder.set_entry_point("chat")
    builder.add_edge("chat", END)
    return builder.compile(checkpointer=checkpointer)


def make_checkpointer():
    """
    Return a durable checkpointer.

    REAL Postgres path (commented) — requires:
        pip install langgraph-checkpoint-postgres
        from langgraph.checkpoint.postgres import PostgresSaver
        cp_ctx = PostgresSaver.from_conn_string(DB_URI)
        checkpointer = cp_ctx.__enter__()
        checkpointer.setup()   # creates the langgraph checkpoint tables once
        return checkpointer
    """
    if not USE_MOCK:
        from langgraph.checkpoint.postgres import PostgresSaver  # type: ignore

        logger.info("Opening PostgresSaver against %s", DB_URI)
        cp = PostgresSaver.from_conn_string(DB_URI).__enter__()
        cp.setup()
        return cp

    logger.info("[MOCK] Using MemorySaver as a stand-in for PostgresSaver.")
    return MemorySaver()


# ─────────────────────────────────────────────────────────────────────────────
# Demo: prove a thread resumes after a simulated "restart".
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    from langchain_core.messages import HumanMessage

    print("=" * 70)
    print("Phase 11.2 — Durable checkpointing (offline MemorySaver stand-in)")
    print("=" * 70)

    # The checkpointer is the durable component. In production it's Postgres, so it
    # outlives any single graph object / process. We hold ONE instance here.
    checkpointer = make_checkpointer()
    config = {"configurable": {"thread_id": "user-alice-session-42"}}

    # --- "Process #1" builds a graph and runs two turns ---
    graph_v1 = build_graph(checkpointer)
    graph_v1.invoke({"messages": [HumanMessage("My name is Alice.")]}, config)
    graph_v1.invoke({"messages": [HumanMessage("I work in Java.")]}, config)
    snap = graph_v1.get_state(config)
    print(f"\nBefore 'restart': thread has {len(snap.values['messages'])} messages persisted.")

    # --- Simulate a restart: throw away the graph object entirely ---
    del graph_v1
    print("...simulating process restart (graph object discarded)...")

    # --- "Process #2" rebuilds the graph against the SAME durable checkpointer ---
    graph_v2 = build_graph(checkpointer)
    result = graph_v2.invoke({"messages": [HumanMessage("What do you know about me?")]}, config)
    print(f"After 'restart': thread now has {len(result['messages'])} messages.")
    print(f"Latest reply -> {result['messages'][-1].content}")
    print("\nState survived because it lived in the checkpointer, not the graph object.")
    print("Swap USE_MOCK=False to make this survive REAL restarts via Postgres.")


if __name__ == "__main__":
    main()
