"""
02_corrective_rag.py
==================================================================
Phase 8.2 — Corrective RAG (CRAG): grade each retrieved doc, and if the
relevant set is too thin, supplement with a web search before generating.

THE BIG IDEA
------------
A vector store returns the *nearest* documents, not the *relevant* ones.
"Nearest by cosine similarity" and "actually answers the question" are not
the same thing — a query can match an index entry that is topically close
but useless. Naive RAG stuffs all k hits into the prompt and hopes.

CRAG adds two correction steps:
  1. GRADE every retrieved doc for true relevance (a per-doc yes/no).
  2. If fewer than N (here: 2) docs pass, the retrieval is "thin" — so we
     SUPPLEMENT with a web search (Tavily/SerpAPI) and only then generate.

The generated answer always carries explicit SOURCE provenance so the
reader can see whether it came from the index, the web, or both.

JAVA ANALOGY (Spring Boot)
--------------------------
Grading is your input-validation / Bean-Validation layer applied to
retrieved data: never trust what the downstream returned just because it
returned *something*. The web-search fallback is a classic resilience
pattern — like a Resilience4j fallback when the primary source is degraded:

    @Retry / @CircuitBreaker(fallbackMethod = "searchWeb")
    List<Doc> primary = vectorStore.similaritySearch(q);
    // if primary fails the relevance check -> searchWeb(q)

OFFLINE MODE
------------
USE_MOCK = True wires a deterministic fake grader/LLM, an in-memory
retriever seeded with BOTH relevant and irrelevant docs (so grading visibly
filters), and a mock web-search tool. Flip USE_MOCK = False and fill the
three marked blocks to use real services.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Callable, Protocol, Sequence

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

# ------------------------------------------------------------------ logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("corrective_rag")

# ============================================================================
# TOGGLE: offline (mock) vs. real LLM + retriever + web search
# ============================================================================
USE_MOCK: bool = True

# How many graded-relevant docs we require before we trust the index alone.
MIN_RELEVANT_DOCS: int = 2


# ============================================================================
# Structural typing (Java-interface style)
# ============================================================================
class ChatModel(Protocol):
    def invoke(self, messages: Sequence[BaseMessage]) -> AIMessage: ...


class Retriever(Protocol):
    def invoke(self, query: str) -> list[Document]: ...


# A web-search tool is just "query string -> a Document of web content".
WebSearchFn = Callable[[str], Document]


# ============================================================================
# MOCK 1 — deterministic fake chat model (also the grader)
# ============================================================================
@dataclass
class FakeChatModel:
    """Stub LLM that (a) grades relevance by keyword overlap and (b) answers."""

    name: str = "fake-claude"

    def invoke(self, messages: Sequence[BaseMessage]) -> AIMessage:
        text = messages[-1].content if messages else ""
        lowered = text.lower()

        # Branch A: this is the GRADER prompt.
        if "answer only: yes or no" in lowered:
            # Pull the query and the doc excerpt back out of the prompt so the
            # grade is a real (if simple) relevance test, not a coin flip.
            query = _extract_after(text, "Query:")
            excerpt = _extract_after(text, "Document excerpt:")
            verdict = _keyword_overlap(query, excerpt)
            return AIMessage(content="yes" if verdict else "no")

        # Branch B: a normal "answer from this context" prompt.
        return AIMessage(
            content="[FAKE LLM] Synthesized answer grounded in the supplied context."
        )


def _extract_after(text: str, label: str) -> str:
    """Grab the line/segment following a label like 'Query:' from a prompt."""
    idx = text.find(label)
    if idx == -1:
        return ""
    tail = text[idx + len(label):]
    # Stop at the next labelled line if present.
    for stop in ("\nDocument excerpt:", "\nAnswer ONLY", "\nQuestion:"):
        cut = tail.find(stop)
        if cut != -1:
            tail = tail[:cut]
    return tail.strip()


def _keyword_overlap(query: str, excerpt: str) -> bool:
    """Cheap deterministic relevance: do query keywords appear in the excerpt?"""
    stop = {"the", "a", "an", "is", "are", "what", "our", "of", "for", "and", "to", "in"}
    q_words = {w for w in re.findall(r"[a-z]+", query.lower()) if w not in stop and len(w) > 2}
    if not q_words:
        return False
    excerpt_l = excerpt.lower()
    hits = sum(1 for w in q_words if w in excerpt_l)
    return hits >= 1


# ============================================================================
# MOCK 2 — in-memory retriever seeded with relevant AND irrelevant docs
# ============================================================================
# Intentionally returns some off-topic docs so the grader's filtering is
# visible, and (for some queries) leaves < 2 relevant so the web fallback fires.
# ============================================================================
@dataclass
class InMemoryRetriever:
    corpus: list[Document] = field(
        default_factory=lambda: [
            Document(
                page_content="Our refund policy allows returns within 30 days of purchase.",
                metadata={"source": "policy_handbook.pdf"},
            ),
            Document(
                page_content="The cafeteria menu rotates weekly and includes vegan options.",
                metadata={"source": "office_wiki.pdf"},   # off-topic noise
            ),
            Document(
                page_content="Shipping is free on orders over $50; returns ship prepaid.",
                metadata={"source": "shipping_faq.pdf"},
            ),
        ]
    )

    def invoke(self, query: str) -> list[Document]:
        logger.info("Retriever returning %d candidate docs for %r", len(self.corpus), query)
        return list(self.corpus)


# ============================================================================
# MOCK 3 — fake web search (the CRAG fallback)
# ============================================================================
def mock_web_search(query: str) -> Document:
    """Deterministic stand-in for Tavily/SerpAPI."""
    logger.info("MOCK web search invoked for %r", query)
    return Document(
        page_content=(
            f"[Web Search Result for {query!r}] Latest public info indicates "
            "competitors offer 14-day refunds; industry standard is 30 days."
        ),
        metadata={"source": "web_search"},
    )


# ============================================================================
# REAL wiring (only used when USE_MOCK = False)
# ============================================================================
def _build_real_llm() -> ChatModel:
    # ---- REAL LLM BLOCK -----------------------------------------------------
    #   from langchain_anthropic import ChatAnthropic
    #   return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    # -------------------------------------------------------------------------
    raise NotImplementedError("Set USE_MOCK=True or implement _build_real_llm().")


def _build_real_retriever() -> Retriever:
    # ---- REAL RETRIEVER BLOCK ----------------------------------------------
    #   from langchain_chroma import Chroma
    #   vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    #   return vectorstore.as_retriever(search_kwargs={"k": 4})
    # -------------------------------------------------------------------------
    raise NotImplementedError("Set USE_MOCK=True or implement _build_real_retriever().")


def _build_real_web_search() -> WebSearchFn:
    # ---- REAL WEB-SEARCH BLOCK ---------------------------------------------
    # Tavily (recommended for LLMs). Requires: pip install tavily-python
    # and TAVILY_API_KEY set. Docs: https://docs.tavily.com/documentation/quickstart
    #
    #   from tavily import TavilyClient
    #   client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    #   def search(query: str) -> Document:
    #       res = client.search(query=query, max_results=3)
    #       text = "\n".join(r["content"] for r in res["results"])
    #       return Document(page_content=text, metadata={"source": "web_search"})
    #   return search
    #
    # Alternative via LangChain community:
    #   from langchain_community.tools.tavily_search import TavilySearchResults
    # -------------------------------------------------------------------------
    raise NotImplementedError("Set USE_MOCK=True or implement _build_real_web_search().")


# ============================================================================
# 8.2 — GRADING + PIPELINE
# ============================================================================
def grade_doc_relevance(query: str, doc: Document, llm: ChatModel) -> bool:
    """Return True iff `doc` is actually relevant to `query` (per the LLM grader)."""
    prompt = (
        "Is this document relevant to the query?\n"
        f"Query: {query}\n"
        f"Document excerpt: {doc.page_content[:400]}\n"
        "Answer ONLY: yes or no"
    )
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
    except Exception:  # noqa: BLE001 - one bad grade must not sink the request
        # Fail-safe: if the grader errors, treat the doc as NOT relevant so we
        # err toward triggering the web-search supplement.
        logger.exception("Grader failed for source=%s; treating as NOT relevant",
                         doc.metadata.get("source"))
        return False
    verdict = (result.content or "").strip().lower() == "yes"
    logger.info("Grade source=%-20s -> %s", doc.metadata.get("source", "unknown"),
                "PASS" if verdict else "fail")
    return verdict


def corrective_rag_pipeline(
    query: str,
    retriever: Retriever,
    llm: ChatModel,
    web_search: WebSearchFn,
    min_relevant: int = MIN_RELEVANT_DOCS,
) -> str:
    """Retrieve -> grade -> (supplement if thin) -> generate, with provenance."""
    # Step 1: Retrieve.
    raw_docs = retriever.invoke(query)
    print(f"  Retrieved {len(raw_docs)} documents")

    # Step 2: Grade each for relevance.
    relevant = [d for d in raw_docs if grade_doc_relevance(query, d, llm)]
    passed, failed = len(relevant), len(raw_docs) - len(relevant)
    print(f"  Grading: {passed} PASS / {failed} fail")

    # Step 3: Correct if the relevant set is thin.
    supplemented = False
    if len(relevant) < min_relevant:
        print(f"  ⚠️  Only {len(relevant)} relevant (< {min_relevant}) — supplementing with web search")
        try:
            relevant.append(web_search(query))
            supplemented = True
        except Exception:  # noqa: BLE001 - if web search dies, proceed with what we have
            logger.exception("Web-search supplement failed; proceeding with index docs only")
    else:
        print(f"  ✅ {len(relevant)} relevant docs — index is sufficient, no web search needed")

    if not relevant:
        # Nothing relevant and the fallback also failed: be honest, do not hallucinate.
        return "I could not find relevant information to answer this question.\n\n*Sources: none*"

    # Step 4: Generate from the corrected context, then label sources.
    context = "\n\n---\n\n".join(d.page_content for d in relevant)
    sources = sorted({d.metadata.get("source", "unknown") for d in relevant})
    answer = llm.invoke(
        [HumanMessage(content=f"Answer based on this context:\n\n{context}\n\nQuestion: {query}")]
    )
    tag = " (index + web)" if supplemented else " (index only)"
    return f"{answer.content}\n\n*Sources{tag}: {', '.join(sources)}*"


# ============================================================================
# Demo
# ============================================================================
def _build_components() -> tuple[ChatModel, Retriever, WebSearchFn]:
    if USE_MOCK:
        logger.info("USE_MOCK=True -> FakeChatModel + InMemoryRetriever + mock_web_search")
        return FakeChatModel(), InMemoryRetriever(), mock_web_search
    logger.info("USE_MOCK=False -> real LLM + retriever + web search")
    return _build_real_llm(), _build_real_retriever(), _build_real_web_search()


def main() -> None:
    if not USE_MOCK and not os.getenv("ANTHROPIC_API_KEY"):
        logger.warning("USE_MOCK=False but ANTHROPIC_API_KEY is not set — calls will fail.")

    llm, retriever, web_search = _build_components()

    # Query A: two index docs are about refunds/returns -> >= 2 relevant -> NO web.
    # Query B: nothing in the index is about pricing -> < 2 relevant -> web fallback.
    queries = [
        "What is the refund and returns policy?",          # sufficient -> index only
        "What are competitor subscription pricing tiers?",  # thin -> web supplement
    ]

    print("\n" + "=" * 72)
    print("CORRECTIVE RAG (CRAG) — grade + correct")
    print("=" * 72)
    for q in queries:
        print(f"\nQ: {q}")
        answer = corrective_rag_pipeline(q, retriever, llm, web_search)
        print("  " + answer.replace("\n", "\n  "))

    print("\n" + "-" * 72)
    print("Takeaway: grading filters topically-close-but-irrelevant docs;")
    print("the web fallback only fires when the graded set is too thin.")
    print("-" * 72)


if __name__ == "__main__":
    main()
