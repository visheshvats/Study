"""
Adaptive + corrective retrieval. See Phase 8 (08-advanced-rag) sections 8.1-8.2.
"""
from __future__ import annotations

from typing import List


def needs_retrieval(query: str) -> bool:
    """Adaptive gate: True if the query needs documents, False if general knowledge suffices."""
    # TODO: ask the LLM yes_retrieval / no_retrieval and parse the answer.
    raise NotImplementedError


def grade_doc_relevance(query: str, doc) -> bool:
    """Return True if a retrieved doc is actually relevant to the query."""
    # TODO: ask the LLM 'yes'/'no' given query + doc excerpt.
    raise NotImplementedError


def corrective_retrieve(query: str, retriever) -> List:
    """Retrieve, grade, and web-supplement when fewer than 2 docs are relevant."""
    # TODO: docs = retriever.invoke(query); relevant = [d for d in docs if grade_doc_relevance(...)]
    # TODO: if len(relevant) < 2: append a web-search Document (mock now, Tavily later)
    # TODO: return relevant
    raise NotImplementedError


if __name__ == "__main__":
    print("Implement needs_retrieval/grade_doc_relevance/corrective_retrieve.")
