"""02_router_pattern.py - LangGraph router with conditional edges (Phase 4.2).

PATTERN: Router. ONE classifier looks at the input, picks a CATEGORY, and the
graph dispatches to exactly ONE specialist handler for that category.

    input --> classify --(route)--> code      --> END
                                |--> business  --> END
                                |--> creative  --> END  (also the DEFAULT)

Java analogy: this is Spring MVC dispatch. `classify` is the `DispatcherServlet`
reading the request and choosing a `@RequestMapping`; the conditional edge is
handler mapping; each specialist node is a `@Controller` method. Equivalently:
the Strategy pattern, where `route()` selects which `Strategy` implementation
runs. The crucial production detail (notes.md): a router MUST have a DEFAULT
branch so an unexpected/garbled classification never dead-ends the graph - here
anything that is not "code" or "business" falls back to "creative".

WHEN TO USE: when inputs fall into MUTUALLY EXCLUSIVE categories that each need
different handling. If subtasks are independent and all run, that is
parallelization, not routing.

OFFLINE BY DEFAULT
------------------
USE_MOCK = True uses a deterministic FakeChatModel (keyword-based classifier) so
the BRANCHING is reproducible with no API key. Flip to False for the real model.

Run it (offline):  python 02_router_pattern.py
Real model:        set USE_MOCK = False, then export ANTHROPIC_API_KEY
"""

from __future__ import annotations

import logging
from typing import Any, List, Literal, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# USE_MOCK: offline switch. True = FakeChatModel, no key. False = ChatAnthropic.
# ---------------------------------------------------------------------------
USE_MOCK = True

VALID_CATEGORIES = ("code", "business", "creative")


class FakeChatModel:
    """Deterministic offline LLM. Two behaviours, picked by prompt content:

    1. Classification prompt -> return a single category word via keyword match
       (so routing is reproducible).
    2. Specialist prompt -> echo a role-tagged canned answer.

    Replace with ChatAnthropic for genuine classification + answers.
    """

    def invoke(self, messages: List[Any]) -> AIMessage:
        text = " ".join(str(getattr(m, "content", m)) for m in messages).lower()

        # --- classification branch -------------------------------------------
        if "classify" in text and "return only" in text:
            # Isolate the user's input line so we don't keyword-match the
            # instruction text itself (which lists the category names).
            query = ""
            for line in text.splitlines():
                if line.strip().startswith("input:"):
                    query = line.split("input:", 1)[1]
                    break
            if any(k in query for k in ("python", "java", "code", "bug", "function", "api", "refactor")):
                return AIMessage(content="code")
            if any(k in query for k in ("revenue", "market", "roi", "strategy", "pricing", "customer", "business")):
                return AIMessage(content="business")
            # Anything else (incl. deliberately weird input) -> not in the first
            # two; the router's DEFAULT will turn it into "creative".
            return AIMessage(content="creative")

        # --- specialist branches (detect role from the system prompt) --------
        role = "generalist"
        if "software architect" in text:
            role = "code-expert"
        elif "business analyst" in text:
            role = "business-analyst"
        elif "creative writing" in text:
            role = "creative-writer"
        # The last message is the user's actual request.
        user_msg = str(getattr(messages[-1], "content", messages[-1]))
        return AIMessage(content=f"[MOCK {role}] answering: {user_msg[:70]}")


def build_llm() -> Any:
    """Factory: FakeChatModel offline, ChatAnthropic when USE_MOCK = False."""
    if USE_MOCK:
        logger.info("Using FakeChatModel (offline, no API key).")
        return FakeChatModel()

    # pip install langchain-anthropic ; export ANTHROPIC_API_KEY=...
    from langchain_anthropic import ChatAnthropic

    logger.info("Using real ChatAnthropic(model='claude-sonnet-4-6').")
    return ChatAnthropic(model="claude-sonnet-4-6")


llm = build_llm()


# ---------------------------------------------------------------------------
# STATE - the shared object that flows through the graph (like the HTTP request
# context). `input` is set by the caller; `route` by classify; `output` by one
# specialist.
# ---------------------------------------------------------------------------
class WorkflowState(TypedDict):
    input: str
    route: str
    output: str


# ---------------------------------------------------------------------------
# NODES
# ---------------------------------------------------------------------------
def classify_input(state: WorkflowState) -> dict:
    """The dispatcher. Ask the model to label the input, store it in `route`."""
    prompt = (
        "Classify into: code, business, creative\n"
        f"Input: {state['input']}\n"
        "Return ONLY the label."
    )
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        category = result.content.strip().lower()
    except Exception:  # noqa: BLE001
        # If classification itself fails, degrade to the default rather than
        # crashing the whole request. (Org rule: omit no key risks; fail safe.)
        logger.exception("classify_input failed; defaulting route to 'creative'")
        category = "creative"
    logger.info("[classify] input=%r -> route=%r", state["input"][:50], category)
    return {"route": category}


def code_handler(state: WorkflowState) -> dict:
    r = llm.invoke(
        [SystemMessage("You are a senior software architect."), HumanMessage(state["input"])]
    )
    logger.info("[code] handled")
    return {"output": r.content}


def business_handler(state: WorkflowState) -> dict:
    r = llm.invoke(
        [SystemMessage("You are an MBA-level business analyst."), HumanMessage(state["input"])]
    )
    logger.info("[business] handled")
    return {"output": r.content}


def creative_handler(state: WorkflowState) -> dict:
    r = llm.invoke(
        [SystemMessage("You are a creative writing expert."), HumanMessage(state["input"])]
    )
    logger.info("[creative] handled")
    return {"output": r.content}


# ---------------------------------------------------------------------------
# ROUTING FUNCTION - reads state, returns the next node's KEY. This is where the
# DEFAULT lives: anything not in ("code", "business") falls back to "creative".
# Without this default, a stray classification ("Code", "coding", "??") would
# error out with no matching edge.
# ---------------------------------------------------------------------------
def router(state: WorkflowState) -> Literal["code", "business", "creative"]:
    chosen = state["route"] if state["route"] in ("code", "business") else "creative"
    logger.info("[route] %r -> %r%s", state["route"], chosen,
                " (DEFAULT)" if chosen == "creative" and state["route"] != "creative" else "")
    return chosen


def build_graph() -> Any:
    """Wire classify -> conditional edge -> {code|business|creative} -> END."""
    builder = StateGraph(WorkflowState)
    for name, fn in [
        ("classify", classify_input),
        ("code", code_handler),
        ("business", business_handler),
        ("creative", creative_handler),
    ]:
        builder.add_node(name, fn)

    builder.set_entry_point("classify")

    # The conditional edge. LEFT key = what router() returns; RIGHT = node name.
    builder.add_conditional_edges(
        "classify",
        router,
        {"code": "code", "business": "business", "creative": "creative"},
    )
    for n in ("code", "business", "creative"):
        builder.add_edge(n, END)

    return builder.compile()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    graph = build_graph()
    logger.info("Graph as Mermaid:\n%s", graph.get_graph().draw_mermaid())

    # Four inputs: one per real branch, plus one nonsense input to PROVE the
    # default branch catches the unclassifiable case.
    inputs = [
        "How do I refactor this Python function to remove the nested loops?",  # code
        "What pricing strategy maximizes revenue for a new SaaS product?",      # business
        "Write a short poem about the sea at dawn.",                            # creative
        "asdfghjkl ??? purple monday",                                          # -> default
    ]

    print("\n=== ROUTER PATTERN ===\n")
    for text in inputs:
        result = graph.invoke({"input": text, "route": "", "output": ""})
        print(f"INPUT : {text}")
        print(f"ROUTED: {result['route']}")
        print(f"OUTPUT: {str(result['output'])[:90]}")
        print("-" * 60)

    print("=== done ===")


if __name__ == "__main__":
    main()
