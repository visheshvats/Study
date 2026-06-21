"""01_basic_state_graph.py — your first LangGraph StateGraph (Phase 3.1).

A StateGraph is a state machine for agents. If you know spring-statemachine,
the mapping is almost 1:1:

    spring-statemachine        LangGraph
    -------------------        ---------
    state / action             node  (a function: State -> partial State)
    transition                 edge  (add_edge / add_conditional_edge)
    guard                      conditional edge (routing function)
    extended state / context   the State TypedDict carried between nodes
    initial state              entry point (set_entry_point)
    end / final state          END

The single most important rule for a Java dev: a node returns a PARTIAL dict of
the keys it changed, NOT the whole state. LangGraph merges that partial back
into the shared state for you (using a reducer per key). You never mutate the
state object in place — you return "here is the delta", just like a reducer in
Redux or an event-sourced aggregate applying one event.

Run it (offline, no API key needed):  python 01_basic_state_graph.py

To run against the real model: set USE_MOCK = False, export ANTHROPIC_API_KEY,
and `pip install -r requirements.txt`.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any, List, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages  # reducer: APPENDS, not replaces

# We import the real message classes from langchain-core. These are plain data
# carriers (like immutable DTOs) and need no API key to construct.
from langchain_core.messages import AIMessage, HumanMessage

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# OFFLINE SWITCH
# ─────────────────────────────────────────────────────────────────────────────
# Set USE_MOCK = False to call the real Anthropic API. We keep True so the GRAPH
# MECHANICS (state flow, reducers, entry point -> END) run with zero setup.
USE_MOCK = True


class FakeChatModel:
    """A deterministic stand-in for ChatAnthropic — exercises graph mechanics
    without an API key.

    It mimics only the one method the graph uses: ``.invoke(messages) -> AIMessage``.
    Think of it as a hand-rolled Mockito stub for the LLM dependency: it returns
    a fixed, predictable answer so we can assert on graph behaviour, not on the
    model's creativity.
    """

    def invoke(self, messages: List[Any]) -> AIMessage:
        last = messages[-1].content if messages else ""
        return AIMessage(content=f"[MOCK ANSWER] You asked: {last!r}")


def build_llm() -> Any:
    """Return either the mock or the real ChatAnthropic.

    Swapping to the real model is a one-line change — exactly the dependency
    injection you'd do in Spring by switching a @Profile or a @Bean definition.
    """
    if USE_MOCK:
        logger.info("Using FakeChatModel (offline). Set USE_MOCK=False for the real API.")
        return FakeChatModel()

    # ── REAL MODEL ──
    # from langchain_anthropic import ChatAnthropic
    # return ChatAnthropic(model="claude-sonnet-4-6")
    from langchain_anthropic import ChatAnthropic  # imported lazily

    return ChatAnthropic(model="claude-sonnet-4-6")


llm = build_llm()


# ─────────────────────────────────────────────────────────────────────────────
# STATE DEFINITION
# ─────────────────────────────────────────────────────────────────────────────
# TypedDict declares the shape of the shared context the graph carries between
# nodes — the spring-statemachine "extended state". Each key can have a REDUCER
# (the Annotated[..., reducer] part) describing HOW updates are merged.
class AgentState(TypedDict):
    # add_messages is a reducer: when a node returns {"messages": [x]}, x is
    # APPENDED to the existing list. Without it, the new value would REPLACE the
    # old list — the #1 surprise for newcomers. (Java analogy: it's a custom
    # merge strategy, like a collector that concatenates instead of overwriting.)
    messages: Annotated[List[Any], add_messages]

    # These two keys have NO reducer, so the default behaviour is "last write
    # wins" (replace). step_count is just an int we bump each pass.
    step_count: int
    context: str


# ─────────────────────────────────────────────────────────────────────────────
# NODES — pure functions: State -> PARTIAL State
# ─────────────────────────────────────────────────────────────────────────────
def process_node(state: AgentState) -> dict:
    """Call the model and record that we advanced one step.

    Note we return ONLY the keys we changed. We do NOT return `context` because
    this node didn't touch it. Returning a partial dict is idiomatic; returning
    the full state is the classic Java-dev mistake (see notes.md).
    """
    response = llm.invoke(state["messages"])
    logger.info("[process] llm responded; bumping step_count")
    return {
        "messages": [response],            # add_messages APPENDS this AIMessage
        "step_count": state["step_count"] + 1,
    }


def enrich_context_node(state: AgentState) -> dict:
    """Derive a summary string from the latest message and store it in context."""
    last_msg = state["messages"][-1]
    logger.info("[enrich] summarising last message into context")
    return {"context": f"Processed: {last_msg.content[:50]}..."}


# ─────────────────────────────────────────────────────────────────────────────
# BUILD THE GRAPH
# ─────────────────────────────────────────────────────────────────────────────
def build_graph():
    """Wire nodes and edges, then compile.

    spring-statemachine analogy: this whole function is your
    StateMachineBuilder — you register states (add_node), transitions
    (add_edge), the initial state (set_entry_point), then build() == compile().
    """
    builder = StateGraph(AgentState)

    # Register nodes (states/actions). Nodes are STATELESS functions — never
    # treat them as objects that hold data between runs. All data lives in State.
    builder.add_node("process", process_node)
    builder.add_node("enrich", enrich_context_node)

    # Initial state.
    builder.set_entry_point("process")

    # Unconditional transitions: process -> enrich -> END.
    builder.add_edge("process", "enrich")
    builder.add_edge("enrich", END)

    return builder.compile()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    graph = build_graph()

    # ── Print the graph as Mermaid (Phase 3 checklist item) ──
    logger.info("Graph as Mermaid:\n%s", graph.get_graph().draw_mermaid())

    # invoke() runs the machine from the entry point until it reaches END,
    # returning the FINAL merged state — like StateMachine.sendEvent then reading
    # the extended state afterwards.
    initial_state: AgentState = {
        "messages": [HumanMessage("What is LangGraph?")],
        "step_count": 0,
        "context": "",
    }
    logger.info("Invoking graph with initial step_count=%d", initial_state["step_count"])

    result = graph.invoke(initial_state)

    # Trace the final state so the transitions are visible.
    logger.info("FINAL context : %s", result["context"])
    logger.info("FINAL steps   : %d", result["step_count"])
    logger.info("FINAL messages: %d (HumanMessage + appended AIMessage)", len(result["messages"]))
    for i, msg in enumerate(result["messages"]):
        logger.info("  [%d] %s: %s", i, msg.__class__.__name__, str(msg.content)[:80])

    logger.info("Basic StateGraph demo complete.")


if __name__ == "__main__":
    main()
