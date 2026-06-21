"""Phase 6.3 — Hallucination detection (grounding check).

A high judge score says the answer is well-written; it does NOT say it is TRUE.
This module verifies that a claim is actually *grounded* in its source context,
returning a three-way verdict: SUPPORTED / INFERRED / UNSUPPORTED.

Java analogy: a referential-integrity / foreign-key constraint. An answer (child
row) must reference evidence (parent row) that actually exists. UNSUPPORTED is
the orphaned record — a claim pointing at no source.

OFFLINE NOTE
------------
``USE_MOCK = True`` (default) runs with no network. The mock model returns
deterministic, parseable JSON verdicts by checking whether the claim's content
words appear in the context, so the three verdict types are reproducible
offline. Set ``USE_MOCK = False`` + provide ``ANTHROPIC_API_KEY`` to use a real
model.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Dict, List

from langchain_core.messages import BaseMessage, HumanMessage

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
USE_MOCK: bool = True  # Flip to False for the real Anthropic API.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("phase6.hallucination")

VALID_VERDICTS = {"SUPPORTED", "INFERRED", "UNSUPPORTED"}
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "on", "and",
    "or", "for", "with", "that", "this", "it", "as", "by", "be", "can", "into",
}


# --------------------------------------------------------------------------- #
# Mock model: deterministic, parseable grounding verdicts
# --------------------------------------------------------------------------- #
class _MockGroundingModel:
    """Fake model that decides SUPPORTED/INFERRED/UNSUPPORTED by word overlap.

    - high overlap with context  -> SUPPORTED
    - partial overlap            -> INFERRED
    - little/no overlap          -> UNSUPPORTED
    Emits JSON wrapped in a code fence, like a real model would.
    """

    @staticmethod
    def _content_words(text: str) -> List[str]:
        words = re.findall(r"[a-z0-9]+", text.lower())
        return [w for w in words if w not in _STOPWORDS and len(w) > 2]

    def invoke(self, messages: List[BaseMessage]) -> BaseMessage:
        prompt = messages[-1].content
        claim_match = re.search(r"CLAIM:\s*(.*?)\s*CONTEXT:", prompt, flags=re.DOTALL)
        ctx_match = re.search(r"CONTEXT:\s*(.*?)\s*Is the claim:", prompt, flags=re.DOTALL)
        claim = claim_match.group(1).strip() if claim_match else ""
        context = ctx_match.group(1).strip() if ctx_match else ""

        claim_words = set(self._content_words(claim))
        context_words = set(self._content_words(context))
        overlap = (len(claim_words & context_words) / len(claim_words)) if claim_words else 0.0

        if overlap >= 0.8:
            verdict, reason = "SUPPORTED", "All key terms appear directly in the context."
        elif overlap >= 0.4:
            verdict, reason = "INFERRED", "Partially grounded; reasonable inference from context."
        else:
            verdict, reason = "UNSUPPORTED", "Key terms are absent from the context."

        payload = {"verdict": verdict, "reason": reason}
        return HumanMessage(content="```json\n" + json.dumps(payload) + "\n```")


def _build_llm():
    """Factory hiding mock-vs-real behind a uniform ``.invoke`` interface."""
    if USE_MOCK:
        logger.info("USE_MOCK=True -> deterministic offline grounding model.")
        return _MockGroundingModel()

    # from langchain_anthropic import ChatAnthropic
    # return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    from langchain_anthropic import ChatAnthropic

    logger.info("USE_MOCK=False -> ChatAnthropic(claude-sonnet-4-6).")
    return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)


llm = _build_llm()


# --------------------------------------------------------------------------- #
# Grounding check
# --------------------------------------------------------------------------- #
def check_hallucination(claim: str, source_context: str) -> Dict[str, str]:
    """Return ``{"verdict": ..., "reason": ...}`` for ``claim`` vs ``context``.

    Fails closed: if the model's reply cannot be parsed into a valid verdict, we
    return UNSUPPORTED (treat unverifiable claims as ungrounded), never raising.
    """
    prompt = f"""
Determine if this claim is supported by the provided context.

CLAIM: {claim}

CONTEXT: {source_context}

Is the claim:
A) SUPPORTED — directly stated in context
B) INFERRED — reasonably inferred from context
C) UNSUPPORTED — not in context or contradicts it

Return JSON only:
{{"verdict": "SUPPORTED"|"INFERRED"|"UNSUPPORTED", "reason": "brief explanation"}}"""

    result = llm.invoke([HumanMessage(content=prompt)])
    raw = getattr(result, "content", str(result))

    try:
        # Models love Markdown fences — strip them before json.loads.
        cleaned = re.sub(r"```json|```", "", raw).strip()
        parsed = json.loads(cleaned)
        verdict = str(parsed.get("verdict", "")).upper()
        if verdict not in VALID_VERDICTS:
            raise ValueError(f"unexpected verdict: {verdict!r}")
        return {"verdict": verdict, "reason": str(parsed.get("reason", ""))}
    except (json.JSONDecodeError, ValueError, AttributeError) as exc:
        logger.warning("Grounding parse failed (%s); failing closed to UNSUPPORTED.", exc)
        logger.debug("Raw grounding response: %r", raw)
        return {"verdict": "UNSUPPORTED", "reason": "Could not parse grounding verdict."}


# --------------------------------------------------------------------------- #
# RAG wrapper that flags low-confidence answers
# --------------------------------------------------------------------------- #
class _StubRetriever:
    """Minimal stand-in for a real LangChain retriever (offline demo)."""

    class _Doc:
        def __init__(self, page_content: str) -> None:
            self.page_content = page_content

    def __init__(self, passages: List[str]) -> None:
        self._docs = [self._Doc(p) for p in passages]

    def invoke(self, _query: str) -> List["_StubRetriever._Doc"]:
        return self._docs


def rag_with_hallucination_check(query: str, retriever, answer: str) -> str:
    """Grounding-checked RAG response.

    In a real pipeline ``answer`` comes from ``rag_chain.invoke(query)``; here it
    is passed in so the demo stays offline and deterministic. The answer is
    grounded against the retrieved context, and UNSUPPORTED answers are flagged
    (warned, not hidden) rather than silently dropped.
    """
    docs = retriever.invoke(query)
    context = "\n".join(d.page_content for d in docs)

    verdict = check_hallucination(answer, context)
    logger.info("Grounding verdict=%s reason=%s", verdict["verdict"], verdict["reason"])

    if verdict["verdict"] == "UNSUPPORTED":
        return f"[⚠️ Low confidence] {answer}"
    return answer


# --------------------------------------------------------------------------- #
# Demo
# --------------------------------------------------------------------------- #
def _demo() -> None:
    context = (
        "Vector embeddings convert text into fixed-length arrays of floating point "
        "numbers. Similar meanings produce vectors that are close together. Cosine "
        "similarity measures the closeness between two embedding vectors."
    )

    cases = [
        ("SUPPORTED", "Cosine similarity measures closeness between two embedding vectors."),
        ("INFERRED", "Embeddings let you find semantically similar text by comparing vectors."),
        ("UNSUPPORTED", "Embeddings were invented by Alan Turing in 1936 for cryptography."),
    ]

    print("=== Direct grounding checks ===")
    for expected, claim in cases:
        verdict = check_hallucination(claim, context)
        ok = "✓" if verdict["verdict"] == expected else "✗ (mismatch)"
        print(f"\n  claim   : {claim}")
        print(f"  expected: {expected}")
        print(f"  verdict : {verdict['verdict']} {ok}")
        print(f"  reason  : {verdict['reason']}")

    print("\n=== RAG wrapper (low-confidence answer is flagged) ===")
    retriever = _StubRetriever([context])
    bad_answer = "Embeddings were invented by Alan Turing in 1936 for cryptography."
    print("  ->", rag_with_hallucination_check("who invented embeddings?", retriever, bad_answer))

    good_answer = "Cosine similarity measures closeness between two embedding vectors."
    print("  ->", rag_with_hallucination_check("how is closeness measured?", retriever, good_answer))


if __name__ == "__main__":
    _demo()
