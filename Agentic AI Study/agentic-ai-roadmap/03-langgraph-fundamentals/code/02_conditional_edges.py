"""02_conditional_edges.py - routing with conditional edges (Phase 3.2).

This is the LangGraph equivalent of a spring-statemachine GUARD. One node
(`classify`) decides a category, and a routing function inspects the state and
returns the NAME of the next node to jump to. The edge map then translates that
returned key into a real node.

    classify --(route fn)--> "technical" -> technical -> END
                          |-> "billing"   -> billing   -> END
                          |-> "general"   -> general   -> END

The routing function does NOT modify state - it only READS state and returns a
string. That separation (decide vs. act) is exactly a Spring guard returning a
boolean, except here it returns a label instead of true/false so we can fan out
to more than two branches.

Run it (offline):  python 02_conditional_edges.py
To use the real model: set USE_MOCK = False and export ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import logging
from typing import Any, List, Literal, TypedDict

from langgraph.graph import END, StateGraph
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

USE_MOCK = True  # offline by default; flip to False for the real API


class FakeChatModel:
    """Deterministic LLM stub. For routing demos it returns a category derived
    from simple keyword matching so the BRANCHING is reproducible (no real model
    needed). Replace with ChatAnthropic to get genuine classification.
    """

    def invoke(self, messages: List[Any]) -> AIMessage:
        text = " ".join(str(m.content) for m in messages).lower()

        # If this looks like the classification prompt, return a category word.
        if "classify this query" in text:
            # IMPORTANT: only keyword-match against the USER's query, not the
            # whole prompt. The instruction line literally contains the words
            # "technical, billing, general", so matching the full prompt would
            # always trigger. We isolate the "query: ..." line first.
            query_line = ""
            for line in text.splitlines():
                if line.strip().startswith("query:"):
                    query_line = line.split("query:", 1)[1]
                    break

            if any(k in query_line for k in ("invoice", "bill", "charge", "payment", "refund")):
                return AIMessage(content="billing")
            if any(k in query_line for k in ("error", "bug", "api", "deploy", "code", "stack")):
                return AIMessage(content="technical")
            return AIMessage(content="general")

        # Otherwise it's a specialist node asking for an answer.
        return AIMessage(content=f"[MOCK SPECIALIST REPLY] {messages[-1].content[:60]}")


def build_llm() -> Any:
    if USE_MOCK:
        logger.info("Using FakeChatModel (offline).")
        return FakeChatModel()
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model="claude-sonnet-4-6")


llm = build_llm()


# ---------------------------------------------------------------------------
# STATE
# ---------------------------------------------------------------------------
class RouterState(TypedDict):
    query: str
    category: str    # "technical" | "billing" | "general" (filled by classify)
    response: str    # filled by exactly one specialist node


# ---------------------------------------------------------------------------
# NODES
# ---------------------------------------------------------------------------
def classify(state: RouterState) -> dict:
    """Ask the model to label the query, store the label in `category`."""
    prompt = (
        "Classify this query into one of: technical, billing, general\n"
        f"Query: {state['query']}\n"
        "Return ONLY the category word."
    )
    result = llm.invoke([HumanMessage(content=prompt)])
    category = result.content.strip().lower()
    logger.info("[classify] query=%r -> category=%r", state["query"], category)
    return {"category": category}


def handle_technical(state: RouterState) -> dict:
    reply = llm.invoke(
        [SystemMessage("You are a senior software engineer."), HumanMessage(state["query"])]
    )
    logger.info("[technical] handled")
    return {"response": reply.content}


def handle_billing(state: RouterState) -> dict:
    reply = llm.invoke(
        [SystemMessage("You are a billing support specialist."), HumanMessage(state["query"])]
    )
    logger.info("[billing] handled")
    return {"response": reply.content}


def handle_general(state: RouterState) -> dict:
    reply = llm.invoke([HumanMessage(state["query"])])
    logger.info("[general] handled")
    return {"response": reply.content}


# ---------------------------------------------------------------------------
# ROUTING FUNCTION - the GUARD. Reads state, returns the next node's KEY.
# ---------------------------------------------------------------------------
def route(state: RouterState) -> Literal["technical", "billing", "general"]:
    """Return one of the edge-map KEYS. It must EXACTLY match a key in the dict
    passed to add_conditional_edges - a typo here silently routes nowhere / errors.
    """
    cat = state["category"]
    chosen = cat if cat in ("technical", "billing") else "general"
    logger.info("[route] category=%r -> next node=%r", cat, chosen)
    return chosen


# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------
def build_graph():
    builder = StateGraph(RouterState)
    builder.add_node("classify", classify)
    builder.add_node("technical", handle_technical)
    builder.add_node("billing", handle_billing)
    builder.add_node("general", handle_general)

    builder.set_entry_point("classify")

    # The conditional edge: from "classify", call route(state); use the returned
    # string to look up the real destination in the map. LEFT = what route()
    # returns, RIGHT = the node name to go to. They happen to match here, but
    # they need not - the map is the translation layer.
    builder.add_conditional_edges(
        "classify",
        route,
        {
            "technical": "technical",
            "billing": "billing",
            "general": "general",
        },
    )

    builder.add_edge("technical", END)
    builder.add_edge("billing", END)
    builder.add_edge("general", END)

    return builder.compile()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    graph = build_graph()
    logger.info("Graph as Mermaid:\n%s", graph.get_graph().draw_mermaid())

    # Three queries that should each take a DIFFERENT branch - proving the router.
    queries = [
        "My invoice shows the wrong amount",            # -> billing
        "I get a 500 error when I deploy the API",      # -> technical
        "What are your office hours?",                  # -> general
    ]

    for q in queries:
        result = graph.invoke({"query": q, "category": "", "response": ""})
        logger.info(
            "RESULT category=%-9s | reply=%s",
            result["category"],
            str(result["response"])[:80],
        )

    logger.info("Conditional-edges routing demo complete.")


if __name__ == "__main__":
    main()
