"""
03_agentic_rag.py
==================================================================
Phase 8.3 — Agentic RAG (multi-source): give the agent THREE retrieval
tools and let it decide which source(s) to use per question.

THE BIG IDEA
------------
Adaptive RAG decides *whether* to retrieve. Corrective RAG decides *whether
the docs are good enough*. Agentic RAG decides *where to retrieve from*:

  - search_pdf_docs  -> internal PDF / vector knowledge base (private docs)
  - search_web       -> the public internet (current / external facts)
  - query_database   -> the structured product DB (numbers, records)

We wrap these as @tool functions and hand them to LangGraph's prebuilt
`create_react_agent`. The agent reasons in a ReAct loop (Thought -> Action
-> Observation -> ...) and may call several tools for one compound question,
e.g. "What do WE charge AND what do competitors charge?" -> DB + web.

JAVA ANALOGY (Spring Boot)
--------------------------
The tools are like a set of `@Service` beans (PdfSearchService,
WebSearchService, ProductDbService). The ReAct agent is a dynamic
orchestrator that picks which service(s) to call at runtime based on the
request — closer to a rules/workflow engine than a fixed `@RestController`
method that always calls the same repository.

⚠️ Guardrail: a free-running agent can loop forever across sources. We cap
iterations (recursion_limit) — the equivalent of a max-retries / timeout on
an orchestration so one query cannot spin indefinitely.

OFFLINE MODE
------------
USE_MOCK = True wires a deterministic fake ReAct agent (no LLM, no network)
that inspects the question and calls the appropriate mock tool(s), printing
each tool choice. Flip USE_MOCK = False and fill the marked block to use the
real ChatAnthropic + LangGraph create_react_agent.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Callable

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

# ------------------------------------------------------------------ logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("agentic_rag")

# ============================================================================
# TOGGLE: offline (mock) vs. real LLM-backed create_react_agent
# ============================================================================
USE_MOCK: bool = True

# Hard cap on agent reasoning steps — prevents infinite source-hopping loops.
MAX_AGENT_STEPS: int = 8


# ============================================================================
# Shared mock data sources (used by the @tool implementations below)
# ============================================================================
_PDF_CORPUS: list[Document] = [
    Document(
        page_content="Our Pro plan is $49/month; Enterprise is custom-priced per seat.",
        metadata={"source": "pricing_sheet.pdf"},
    ),
    Document(
        page_content="Refunds are processed within 5 business days of an approved request.",
        metadata={"source": "policy_handbook.pdf"},
    ),
]


# ============================================================================
# THE THREE TOOLS
# ============================================================================
# @tool turns a typed Python function into something the agent can call — the
# docstring is what the LLM reads to decide WHEN to use it, so it doubles as
# the tool's "API contract" (like Javadoc the orchestrator actually consumes).
# In USE_MOCK mode the bodies return deterministic strings; the marked TODOs
# show exactly how to swap in real implementations.
# ============================================================================
@tool
def search_pdf_docs(query: str) -> str:
    """Search the internal PDF knowledge base for company policies, pricing, and docs."""
    logger.info("TOOL search_pdf_docs(query=%r)", query)
    if USE_MOCK:
        return "\n---\n".join(d.page_content[:300] for d in _PDF_CORPUS[:3])
    # ---- REAL PDF/RETRIEVER BLOCK ------------------------------------------
    #   docs = retriever_basic.invoke(query)   # your Phase 2 Chroma retriever
    #   return "\n---\n".join(d.page_content[:300] for d in docs[:3])
    # -------------------------------------------------------------------------
    raise NotImplementedError("Set USE_MOCK=True or wire a real retriever.")


@tool
def search_web(query: str) -> str:
    """Search the public web for current/external information (e.g. competitors)."""
    logger.info("TOOL search_web(query=%r)", query)
    if USE_MOCK:
        return f"[Web results for {query!r}]: Competitor A charges $59/mo; Competitor B $39/mo."
    # ---- REAL WEB-SEARCH BLOCK ---------------------------------------------
    # Tavily docs: https://docs.tavily.com/documentation/quickstart
    #   from tavily import TavilyClient
    #   client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    #   res = client.search(query=query, max_results=3)
    #   return "\n".join(r["content"] for r in res["results"])
    # -------------------------------------------------------------------------
    raise NotImplementedError("Set USE_MOCK=True or wire a real web-search API.")


@tool
def query_database(sql_description: str) -> str:
    """Query the structured product database for counts, records, and metrics."""
    logger.info("TOOL query_database(sql_description=%r)", sql_description)
    if USE_MOCK:
        return f"[DB result for {sql_description!r}]: 1,284 active subscriptions; ARPU $46.20."
    # ---- REAL DB BLOCK ------------------------------------------------------
    #   from sqlalchemy import create_engine, text
    #   engine = create_engine(os.environ["DATABASE_URL"])
    #   with engine.connect() as conn:
    #       rows = conn.execute(text("SELECT ...")).fetchall()
    #   return str(rows)
    # Tip: never interpolate raw user text into SQL — use parameter binding.
    # -------------------------------------------------------------------------
    raise NotImplementedError("Set USE_MOCK=True or wire a real database.")


TOOLS = [search_pdf_docs, search_web, query_database]


# ============================================================================
# MOCK ReAct agent — deterministic, no LLM
# ============================================================================
# Mimics create_react_agent's *interface*: .invoke({"messages": [...]}) ->
# {"messages": [...]}. It routes by keyword so the "which source did the agent
# pick?" story is visible offline. Real reasoning happens in the LLM branch.
# ============================================================================
@dataclass
class FakeReactAgent:
    tools_by_name: dict[str, Callable[..., str]] = field(default_factory=dict)
    max_steps: int = MAX_AGENT_STEPS

    def invoke(self, state: dict[str, Any]) -> dict[str, Any]:
        messages = list(state.get("messages", []))
        question = messages[-1].content if messages else ""
        q = question.lower()

        # Decide which tools this question warrants (may be several).
        chosen: list[str] = []
        if any(k in q for k in ("our", "policy", "refund", "internal", "we charge", "our pricing")):
            chosen.append("search_pdf_docs")
        if any(k in q for k in ("competitor", "market", "current", "latest", "industry")):
            chosen.append("search_web")
        if any(k in q for k in ("how many", "count", "records", "metric", "arpu", "subscriptions")):
            chosen.append("query_database")
        if not chosen:  # default: try the private knowledge base first
            chosen.append("search_pdf_docs")

        chosen = chosen[: self.max_steps]  # enforce the loop cap
        print(f"  Agent reasoning -> chose tool(s): {chosen}")

        observations: list[str] = []
        for name in chosen:
            tool_fn = self.tools_by_name[name]
            # LangChain tools are invoked with a single-arg dict.
            arg_key = "sql_description" if name == "query_database" else "query"
            observation = tool_fn.invoke({arg_key: question})
            observations.append(f"[{name}] {observation}")
            messages.append(AIMessage(content=f"(called {name})"))

        final = AIMessage(
            content="[FAKE AGENT] Synthesized answer from: "
            + ", ".join(chosen)
            + "\n"
            + "\n".join(observations)
        )
        messages.append(final)
        return {"messages": messages}


# ============================================================================
# Agent builder
# ============================================================================
def build_agent() -> Any:
    """Return an object exposing .invoke({'messages': [...]}) -> {'messages': [...]}."""
    if USE_MOCK:
        logger.info("USE_MOCK=True -> FakeReactAgent over mock tools")
        return FakeReactAgent(tools_by_name={t.name: t for t in TOOLS})

    logger.info("USE_MOCK=False -> real create_react_agent")
    # ---- REAL AGENT BLOCK ---------------------------------------------------
    # Requires: pip install langgraph langchain-anthropic, ANTHROPIC_API_KEY set.
    #
    #   from langchain_anthropic import ChatAnthropic
    #   from langgraph.prebuilt import create_react_agent
    #   llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    #   return create_react_agent(llm, tools=TOOLS)
    #
    # Invoke with a recursion_limit to cap the ReAct loop:
    #   agent.invoke({"messages": [HumanMessage(q)]},
    #               config={"recursion_limit": MAX_AGENT_STEPS})
    # -------------------------------------------------------------------------
    raise NotImplementedError("Set USE_MOCK=True or implement the real agent block.")


def run_agent(agent: Any, question: str) -> str:
    """Invoke the agent and return its final message text, with the loop cap applied."""
    try:
        if USE_MOCK:
            result = agent.invoke({"messages": [HumanMessage(content=question)]})
        else:
            result = agent.invoke(
                {"messages": [HumanMessage(content=question)]},
                config={"recursion_limit": MAX_AGENT_STEPS},  # guardrail vs. infinite loops
            )
    except Exception:  # noqa: BLE001 - surface a clean message instead of a stack trace
        logger.exception("Agent invocation failed for %r", question)
        return "The agent could not complete this request."
    return result["messages"][-1].content


# ============================================================================
# Demo
# ============================================================================
def main() -> None:
    if not USE_MOCK and not os.getenv("ANTHROPIC_API_KEY"):
        logger.warning("USE_MOCK=False but ANTHROPIC_API_KEY is not set — calls will fail.")

    agent = build_agent()

    # Each question is engineered to exercise a different routing decision.
    questions = [
        "What is our refund policy?",                                   # -> PDF only
        "What do competitors charge for similar plans right now?",      # -> web only
        "How many active subscriptions do we have and what is ARPU?",   # -> DB only
        "What do WE charge and what do competitors charge in the market?",  # -> PDF + web
    ]

    print("\n" + "=" * 72)
    print("AGENTIC RAG — the agent picks the source per question")
    print("=" * 72)
    for q in questions:
        print(f"\nQ: {q}")
        answer = run_agent(agent, q)
        print("A: " + answer.replace("\n", "\n   "))

    print("\n" + "-" * 72)
    print("Takeaway: one agent, three sources. It routes (and combines) per query,")
    print(f"bounded by a {MAX_AGENT_STEPS}-step cap so it can never loop forever.")
    print("-" * 72)


if __name__ == "__main__":
    main()
