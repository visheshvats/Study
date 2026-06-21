"""04_checkpointing_memory.py — persistent memory via checkpointing (Phase 3.4).

Without a checkpointer, every graph.invoke() starts from a blank state — the
agent is amnesiac. A CHECKPOINTER saves the full state after each run, keyed by
a `thread_id`, and auto-restores it on the next call with the same thread_id.
That is what gives a chatbot memory across turns.

Java analogies:
  * thread_id            ~ an HTTP session id / a conversation correlation id
  * MemorySaver          ~ an in-memory HttpSession store (dev only)
  * Postgres/RedisSaver  ~ Spring Session backed by JDBC/Redis (production)
  * graph.get_state(cfg) ~ peeking at the persisted session attributes

The `add_messages` reducer is what makes this work: each turn APPENDS the new
messages to the restored list, so the full history accumulates per thread.

Run it (offline):  python 04_checkpointing_memory.py
To use the real model: set USE_MOCK = False and export ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import logging
import re
from typing import Annotated, Any, List, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage

logger = logging.getLogger(__name__)

USE_MOCK = True  # offline by default


class FakeChatModel:
    """A stub that proves memory works: it scans the WHOLE message history it
    receives for a previously stated name, so on turn 2 it can answer "What is
    my name?" using only what the checkpointer restored from turn 1.

    If the checkpointer were missing, turn 2 would arrive with only the turn-2
    question and the stub would say it doesn't know — which is exactly how you'd
    detect a broken/forgotten thread_id.
    """

    def invoke(self, messages: List[Any]) -> AIMessage:
        history = " ".join(str(m.content) for m in messages)
        last = str(messages[-1].content).lower()

        if "what is my name" in last or "my name?" in last:
            match = re.search(r"my name is (\w+)", history, re.IGNORECASE)
            if match:
                return AIMessage(content=f"Your name is {match.group(1)}.")
            return AIMessage(content="I don't know your name yet — no memory of it.")

        if "my name is" in last:
            name = re.search(r"my name is (\w+)", last, re.IGNORECASE)
            who = name.group(1) if name else "there"
            return AIMessage(content=f"Nice to meet you, {who}!")

        return AIMessage(content="[MOCK] Acknowledged.")


def build_llm() -> Any:
    if USE_MOCK:
        logger.info("Using FakeChatModel (offline).")
        return FakeChatModel()
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model="claude-sonnet-4-6")


llm = build_llm()


# ─────────────────────────────────────────────────────────────────────────────
# STATE + NODE
# ─────────────────────────────────────────────────────────────────────────────
class ChatState(TypedDict):
    messages: Annotated[List[Any], add_messages]  # append-only history


def chat_node(state: ChatState) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}


def build_graph(checkpointer: MemorySaver):
    builder = StateGraph(ChatState)
    builder.add_node("chat", chat_node)
    builder.set_entry_point("chat")
    builder.add_edge("chat", END)

    # Compile WITH the checkpointer — this is the single line that turns an
    # amnesiac graph into a stateful, resumable one.
    return builder.compile(checkpointer=checkpointer)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    memory = MemorySaver()  # in-process store; swap for Postgres/Redis in prod
    graph = build_graph(memory)
    logger.info("Graph as Mermaid:\n%s", graph.get_graph().draw_mermaid())

    # The thread_id lives under config["configurable"]. SAME id == SAME memory.
    config = {"configurable": {"thread_id": "session-alice-001"}}

    # ── Turn 1: tell the agent our name ──
    logger.info("── Turn 1: stating the name ──")
    r1 = graph.invoke({"messages": [HumanMessage("My name is Alice.")]}, config)
    logger.info("Agent: %s", r1["messages"][-1].content)

    # ── Turn 2: SAME thread_id — state auto-restored, so it remembers ──
    logger.info("── Turn 2: asking the agent to recall (same thread_id) ──")
    r2 = graph.invoke({"messages": [HumanMessage("What is my name?")]}, config)
    logger.info("Agent: %s", r2["messages"][-1].content)

    # ── Inspect persisted state ──
    snapshot = graph.get_state(config)
    logger.info("Messages persisted in memory: %d", len(snapshot.values["messages"]))
    logger.info("Next node to run (empty tuple == finished): %s", snapshot.next)

    # ── Proof: a DIFFERENT thread_id has NO memory of Alice ──
    logger.info("── Control: a fresh thread_id should NOT remember ──")
    other = {"configurable": {"thread_id": "session-bob-002"}}
    r3 = graph.invoke({"messages": [HumanMessage("What is my name?")]}, other)
    logger.info("Agent (new thread): %s", r3["messages"][-1].content)

    logger.info("Checkpointing / memory demo complete.")


if __name__ == "__main__":
    main()
