"""
Offline scaffolding for the Self-correcting RAG API (no API key needed).
Depends only on numpy + langchain_core. Real swaps named in each TODO.
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

    def embed_query(self, t: str):
        return self._vec(t).tolist()

    def embed_documents(self, ts):
        return [self._vec(t).tolist() for t in ts]


def cosine(a, b) -> float:
    a, b = np.asarray(a), np.asarray(b)
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / d) if d else 0.0


class InMemoryVectorStore:
    """Cosine top-k store. Real swap: Chroma."""

    def __init__(self, emb: MockEmbeddings, docs: List[Document]) -> None:
        self.emb = emb
        self._items = list(zip(docs, emb.embed_documents([d.page_content for d in docs])))

    def search(self, query: str, k: int = 4) -> List[Document]:
        qv = self.emb.embed_query(query)
        ranked = sorted(self._items, key=lambda it: cosine(qv, it[1]), reverse=True)
        return [d for d, _ in ranked[:k]]


class MockGenerator:
    """Simulates an LLM that produces a WEAK first answer and IMPROVES once given
    evaluator feedback — so the optimizer loop visibly raises the score.
    Real swap: ChatAnthropic(model='claude-sonnet-4-6')."""

    def generate(self, question: str, context: str, feedback: str = "") -> str:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", context) if s.strip()]
        q_tokens = {t for t in tokenize(question) if len(t) > 3}
        relevant = [s for s in sentences if q_tokens & set(tokenize(s))] or sentences[:1]

        if not feedback:
            # Weak, vague first attempt (no specifics, no figures).
            return "Our policy covers this; please see the documentation for details."
        # Improved attempt: detailed and grounded, includes the concrete figures.
        return "Based on the documentation: " + " ".join(relevant[:3])


SAMPLE_DOCS = [
    Document(page_content="Customers may return any item within 30 days of the purchase date for a full refund. "
                          "Items must be unused and in original packaging.",
             metadata={"source": "returns_policy"}),
    Document(page_content="Refunds are processed within 5 business days after the returned item is received.",
             metadata={"source": "returns_policy"}),
    Document(page_content="Standard shipping takes 3 to 5 business days; express shipping arrives next business day.",
             metadata={"source": "shipping_policy"}),
    Document(page_content="All electronics include a 12 month limited warranty covering manufacturing defects.",
             metadata={"source": "warranty_policy"}),
]

# Canned web result for the corrective-RAG fallback (real swap: Tavily API).
WEB_FALLBACK = ("[web] Industry refund norms range from 14 to 30 days; competitors typically "
                "process refunds within 5 to 10 business days.")
