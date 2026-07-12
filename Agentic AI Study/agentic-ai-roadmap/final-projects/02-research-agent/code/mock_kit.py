"""
Offline scaffolding for the Research Agent (no API key needed).
Depends only on numpy + langchain_core. Delete in production; use the real classes
named in each TODO.
"""
from __future__ import annotations

import re
from typing import List

import numpy as np
from langchain_core.documents import Document

_DIM = 256
_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(t: str) -> List[str]:
    return _TOKEN.findall(t.lower())


class MockEmbeddings:
    """Hashing-trick embeddings. Real swap: OpenAIEmbeddings(model='text-embedding-3-small')."""

    def _vec(self, text: str) -> np.ndarray:
        v = np.zeros(_DIM, dtype=np.float32)
        for tok in tokenize(text):
            v[hash(tok) % _DIM] += 1.0
        n = np.linalg.norm(v)
        return v / n if n else v

    def embed_query(self, text: str):
        return self._vec(text).tolist()

    def embed_documents(self, texts):
        return [self._vec(t).tolist() for t in texts]


def cosine(a, b) -> float:
    a, b = np.asarray(a), np.asarray(b)
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / d) if d else 0.0


class InMemoryVectorStore:
    """Cosine top-k store. Real swap: Chroma."""

    def __init__(self, emb: MockEmbeddings, docs: List[Document]) -> None:
        self.emb = emb
        self._items = list(zip(docs, emb.embed_documents([d.page_content for d in docs])))

    def search(self, query: str, k: int = 2) -> List[Document]:
        qv = self.emb.embed_query(query)
        ranked = sorted(self._items, key=lambda it: cosine(qv, it[1]), reverse=True)
        return [d for d, _ in ranked[:k]]


class MockLLM:
    """Deterministic synthesizer. Real swap: ChatAnthropic(model='claude-sonnet-4-6')."""

    def synthesize(self, question: str, findings: str, analyses: dict) -> str:
        topics = analyses.get("topics", "")
        return (
            f"Answer to: {question}\n"
            f"Synthesis (from internal docs + web research):\n{findings}\n"
            f"Key topics detected: {topics}"
        )


# Internal "knowledge base" the doc-search tool retrieves from.
INTERNAL_DOCS = [
    Document(page_content="Our Pro plan costs 49 dollars per month and includes 100 GB storage and priority support.",
             metadata={"source": "pricing.md"}),
    Document(page_content="The platform supports up to 100 concurrent users per workspace on the Pro plan.",
             metadata={"source": "specs.md"}),
    Document(page_content="Our Free plan includes 5 GB storage and community support only.",
             metadata={"source": "pricing.md"}),
]

# Canned web results so search_web works offline (real swap: Tavily API).
WEB_SNIPPETS = {
    "competitor": "Competitor X charges 59 dollars/month; Competitor Y charges 39 dollars/month for similar storage.",
    "default": "Recent market reports show steady growth in the SaaS storage segment through 2026.",
}
