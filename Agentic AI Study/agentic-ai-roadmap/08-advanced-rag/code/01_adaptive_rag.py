"""
01_adaptive_rag.py
==================================================================
Phase 8.1 — Adaptive RAG: the `needs_retrieval` gate.

THE BIG IDEA
------------
Naive RAG *always* retrieves, then generates. That is wasteful: for
"What is 2 + 2?" or "Translate 'hello' to French" the LLM already knows
the answer, yet naive RAG still burns a vector-store round-trip plus the
extra tokens of stuffed context.

Adaptive RAG adds a cheap classifier *before* retrieval — a gate that
asks "do I actually need documents for this?". If no, we answer the LLM
directly (fast, cheap). If yes, we fall through to the normal RAG chain.

JAVA ANALOGY (Spring Boot)
--------------------------
Think of `needs_retrieval()` as a `@Cacheable` / circuit-breaker guard in
front of an expensive downstream call:

    if (cache.contains(key)) return cache.get(key);   // LLM already knows
    else return expensiveRepository.findBy(query);    // go retrieve

You would never hit the DB for data you can serve from memory. The gate is
the same instinct applied to retrieval.

OFFLINE MODE
------------
USE_MOCK = True wires in a deterministic fake chat model and a tiny
in-memory retriever, so this file RUNS with no API key and visibly prints
every routing decision. Flip USE_MOCK = False and fill in the two marked
blocks to use the real ChatAnthropic + a real retriever.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Protocol, Sequence

# langchain-core is the only hard dependency for the offline demo.
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

# ------------------------------------------------------------------ logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("adaptive_rag")

# ============================================================================
# TOGGLE: offline (mock) vs. real LLM + retriever
# ============================================================================
# Set to False AND fill in the two "REAL" blocks below to call live services.
USE_MOCK: bool = True


# ============================================================================
# Structural typing — like a Java interface. Both the mock and the real
# ChatAnthropic satisfy this, so the rest of the file does not care which.
# ============================================================================
class ChatModel(Protocol):
    def invoke(self, messages: Sequence[BaseMessage]) -> AIMessage: ...


class Retriever(Protocol):
    def invoke(self, query: str) -> list[Document]: ...


# ============================================================================
# MOCK 1 — deterministic fake chat model
# ============================================================================
# No randomness, no network. It classifies on simple keyword heuristics so the
# routing decisions are reproducible in CI. This is the analogue of a Mockito
# stub: `when(llm.invoke(any())).thenReturn(deterministicAnswer)`.
# ============================================================================
@dataclass
class FakeChatModel:
    """A stand-in for ChatAnthropic with no external calls."""

    name: str = "fake-claude"
    # Words that strongly imply the user wants *specific / private* data.
    _retrieval_triggers: tuple[str, ...] = field(
        default_factory=lambda: (
            "our",
            "policy",
            "internal",
            "document",
            "report",
            "pricing",
            "refund",
            "contract",
            "sla",
            "company",
        )
    )

    def invoke(self, messages: Sequence[BaseMessage]) -> AIMessage:
        raw = messages[-1].content if messages else ""
        text = raw.lower()

        # Branch A: this prompt is the GATE classifier prompt.
        if "yes_retrieval or no_retrieval" in text:
            # IMPORTANT: match triggers against ONLY the user's question, not the
            # whole prompt — the prompt boilerplate itself contains words like
            # "documents"/"data", which would otherwise force retrieval every time.
            question = text
            marker = "question:"
            if marker in text:
                after = text.split(marker, 1)[1]
                # Stop at the trailing "answer only:" instruction line.
                question = after.split("answer only", 1)[0]
            decision = (
                "yes_retrieval"
                if any(trigger in question for trigger in self._retrieval_triggers)
                else "no_retrieval"
            )
            return AIMessage(content=decision)

        # Branch B: a normal "answer from your own knowledge" prompt.
        return AIMessage(
            content="[FAKE LLM] General-knowledge answer generated without retrieval."
        )


# ============================================================================
# MOCK 2 — tiny in-memory retriever
# ============================================================================
# Returns a fixed set of Documents regardless of the query. In production this
# is a Chroma / FAISS / pgvector retriever; here it is a hard-coded list so the
# RAG branch produces visible output offline.
# ============================================================================
@dataclass
class InMemoryRetriever:
    """A fixed-corpus retriever — like an in-memory Map<String, Doc> repo."""

    corpus: list[Document] = field(
        default_factory=lambda: [
            Document(
                page_content="Our standard refund policy allows returns within 30 days.",
                metadata={"source": "policy_handbook.pdf"},
            ),
            Document(
                page_content="Enterprise SLA guarantees 99.9% uptime with 4-hour response.",
                metadata={"source": "sla_contract.pdf"},
            ),
        ]
    )

    def invoke(self, query: str) -> list[Document]:
        logger.info("Retriever hit for query=%r (returning %d docs)", query, len(self.corpus))
        return list(self.corpus)


# ============================================================================
# REAL wiring (only used when USE_MOCK = False)
# ============================================================================
def _build_real_llm() -> ChatModel:
    # ---- REAL LLM BLOCK -----------------------------------------------------
    # Requires: pip install langchain-anthropic  AND  ANTHROPIC_API_KEY set.
    #
    #   from langchain_anthropic import ChatAnthropic
    #   return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    #
    # ChatAnthropic already satisfies the ChatModel Protocol (.invoke -> AIMessage).
    # -------------------------------------------------------------------------
    raise NotImplementedError("Set USE_MOCK=True or implement _build_real_llm().")


def _build_real_retriever() -> Retriever:
    # ---- REAL RETRIEVER BLOCK ----------------------------------------------
    # Reuse the Phase 2 RAG vector store, e.g. Chroma:
    #
    #   from langchain_chroma import Chroma
    #   from langchain_anthropic import ... (or any embeddings provider)
    #   vectorstore = Chroma(persist_directory="./chroma_db",
    #                        embedding_function=embeddings)
    #   return vectorstore.as_retriever(search_kwargs={"k": 4})
    # -------------------------------------------------------------------------
    raise NotImplementedError("Set USE_MOCK=True or implement _build_real_retriever().")


# ============================================================================
# 8.1 — THE GATE
# ============================================================================
def needs_retrieval(query: str, llm: ChatModel) -> bool:
    """Decide whether `query` needs document retrieval or can be answered directly.

    Returns True  -> go retrieve (specific/private/factual-lookup question).
    Returns False -> let the LLM answer from its own parametric knowledge.

    This mirrors the roadmap snippet but adds type hints + error handling.
    """
    prompt = (
        "Does this question require looking up specific documents or data,\n"
        "or can it be answered from general knowledge?\n\n"
        f"Question: {query}\n\n"
        "Answer ONLY: yes_retrieval or no_retrieval"
    )
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
    except Exception:  # noqa: BLE001 - we degrade safely, never crash the request
        # Fail-safe default: if the classifier errors, ASSUME retrieval is needed.
        # (Better to be slow-but-correct than fast-but-wrong on a private question.)
        logger.exception("Gate classifier failed; defaulting to RETRIEVE")
        return True

    raw = (result.content or "").strip().lower()
    # Robust parse: look for the explicit 'yes' token, not a substring of 'no'.
    decision = bool(re.search(r"\byes", raw))
    logger.info("Gate raw=%r -> needs_retrieval=%s", raw, decision)
    return decision


def _rag_chain_invoke(query: str, retriever: Retriever, llm: ChatModel) -> str:
    """Minimal stand-in for the Phase 2 `rag_chain.invoke(query)`.

    Retrieve -> stuff context -> generate. In Phase 2 this was a prebuilt
    LCEL chain; here we inline it so this file is self-contained.
    """
    docs = retriever.invoke(query)
    context = "\n\n---\n\n".join(d.page_content for d in docs)
    answer = llm.invoke(
        [HumanMessage(content=f"Answer based on this context:\n\n{context}\n\nQuestion: {query}")]
    )
    sources = sorted({d.metadata.get("source", "unknown") for d in docs})
    return f"{answer.content}\n\n*Sources: {', '.join(sources)}*"


def adaptive_rag(query: str, retriever: Retriever, llm: ChatModel) -> str:
    """Route the query: skip retrieval when the LLM already knows the answer."""
    if needs_retrieval(query, llm):
        logger.info("ROUTE = RETRIEVE for query=%r", query)
        print("  -> 🔍 Using retrieval...")
        return _rag_chain_invoke(query, retriever, llm)

    logger.info("ROUTE = DIRECT for query=%r", query)
    print("  -> 🧠 Using LLM knowledge directly...")
    answer = llm.invoke([HumanMessage(content=query)])
    return answer.content


# ============================================================================
# Demo
# ============================================================================
def _build_components() -> tuple[ChatModel, Retriever]:
    if USE_MOCK:
        logger.info("USE_MOCK=True -> wiring FakeChatModel + InMemoryRetriever")
        return FakeChatModel(), InMemoryRetriever()
    logger.info("USE_MOCK=False -> wiring real ChatAnthropic + real retriever")
    return _build_real_llm(), _build_real_retriever()


def main() -> None:
    if not USE_MOCK and not os.getenv("ANTHROPIC_API_KEY"):
        logger.warning("USE_MOCK=False but ANTHROPIC_API_KEY is not set — calls will fail.")

    llm, retriever = _build_components()

    # A mix of trivial (skip retrieval) and specific (retrieve) questions so the
    # gate's behaviour is visible. We also measure the SKIP RATE — a key metric.
    queries = [
        "What is 2 + 2?",                                  # trivial -> DIRECT
        "Translate 'good morning' into Spanish.",          # trivial -> DIRECT
        "What is our refund policy for enterprise plans?",  # private -> RETRIEVE
        "Summarize the internal SLA document.",            # private -> RETRIEVE
        "Who wrote Romeo and Juliet?",                     # trivial -> DIRECT
    ]

    skipped = 0
    print("\n" + "=" * 72)
    print("ADAPTIVE RAG — routing decisions")
    print("=" * 72)
    for q in queries:
        print(f"\nQ: {q}")
        retrieved = needs_retrieval(q, llm)
        if not retrieved:
            skipped += 1
        answer = adaptive_rag(q, retriever, llm)
        print(f"A: {answer.splitlines()[0]}")

    rate = skipped / len(queries) * 100
    print("\n" + "-" * 72)
    print(f"SKIP RATE: {skipped}/{len(queries)} queries answered WITHOUT retrieval ({rate:.0f}%).")
    print("Each skip saved one vector-store round-trip + the context tokens.")
    print("-" * 72)


if __name__ == "__main__":
    main()
