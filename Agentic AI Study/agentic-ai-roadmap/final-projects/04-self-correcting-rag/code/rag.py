"""
Adaptive + corrective retrieval. Phase 8 sections 8.1-8.2. Offline via mock_kit.
"""
from __future__ import annotations

import logging
from typing import List, Tuple

from langchain_core.documents import Document

import mock_kit

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("rag")

USE_MOCK = True
_GREETING = ("hello", "hi ", "how are you", "your name", "thank")


def get_store() -> mock_kit.InMemoryVectorStore:
    return mock_kit.InMemoryVectorStore(mock_kit.MockEmbeddings(), mock_kit.SAMPLE_DOCS)


def needs_retrieval(query: str) -> bool:
    """Adaptive gate: skip retrieval for small-talk; retrieve for substantive questions."""
    if not USE_MOCK:
        # REAL: ask the LLM 'yes_retrieval'/'no_retrieval' and parse.
        raise NotImplementedError
    q = query.lower()
    return not any(g in q for g in _GREETING)


def grade_doc_relevance(query: str, doc: Document) -> bool:
    """True if the doc shares meaningful terms with the query."""
    if not USE_MOCK:
        raise NotImplementedError
    q = {t for t in mock_kit.tokenize(query) if len(t) > 3}
    d = {t for t in mock_kit.tokenize(doc.page_content) if len(t) > 3}
    for a in q:
        for b in d:
            if a == b or a.startswith(b) or b.startswith(a):
                return True
    return False


def corrective_retrieve(query: str, store: mock_kit.InMemoryVectorStore) -> Tuple[List[Document], List[str]]:
    """Retrieve, grade, and supplement with web search when < 2 docs are relevant."""
    raw = store.search(query, k=4)
    relevant = [d for d in raw if grade_doc_relevance(query, d)]
    logger.info("retrieved %d, relevant after grading %d", len(raw), len(relevant))
    if len(relevant) < 2:
        logger.info("insufficient grounding -> web-search fallback")
        relevant.append(Document(page_content=mock_kit.WEB_FALLBACK, metadata={"source": "web_search"}))
    sources = sorted({d.metadata.get("source", "unknown") for d in relevant})
    return relevant, sources


if __name__ == "__main__":
    store = get_store()
    print("needs_retrieval('hello there'):", needs_retrieval("hello there"))
    docs, src = corrective_retrieve("What is the refund window?", store)
    print("sources:", src)
    docs, src = corrective_retrieve("What do competitors charge?", store)
    print("fallback sources:", src)
