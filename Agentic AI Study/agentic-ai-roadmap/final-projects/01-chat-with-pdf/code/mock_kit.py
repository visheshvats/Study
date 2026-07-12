"""
Offline scaffolding for Chat-with-PDF so the project runs with NO API key / no
external services. In production you delete this and use the real classes named in
each TODO. Depends only on numpy + langchain_core (both lightweight).

Contents:
  - MockEmbeddings      : deterministic hashing-trick vectors (stands in for OpenAIEmbeddings)
  - InMemoryVectorStore : cosine top-k retriever (stands in for Chroma)
  - MockLLM             : grounded answerer (stands in for ChatAnthropic)
  - SAMPLE_POLICY       : a sample document so `ingest` has something to load offline
"""
from __future__ import annotations

import re
from typing import Callable, List

import numpy as np
from langchain_core.documents import Document

_DIM = 256
_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> List[str]:
    return _TOKEN.findall(text.lower())


class MockEmbeddings:
    """Hashing-trick bag-of-words embeddings. Shared vocabulary -> higher cosine.

    Real swap:  from langchain_openai import OpenAIEmbeddings
                OpenAIEmbeddings(model="text-embedding-3-small")
    """

    def _vec(self, text: str) -> List[float]:
        v = np.zeros(_DIM, dtype=np.float32)
        for tok in _tokenize(text):
            v[hash(tok) % _DIM] += 1.0
        norm = np.linalg.norm(v)
        return (v / norm).tolist() if norm else v.tolist()

    def embed_query(self, text: str) -> List[float]:
        return self._vec(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._vec(t) for t in texts]


def cosine(a: List[float], b: List[float]) -> float:
    a, b = np.asarray(a), np.asarray(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0


class _Retriever:
    def __init__(self, store: "InMemoryVectorStore", k: int) -> None:
        self._store, self.k = store, k

    def invoke(self, query: str) -> List[Document]:
        return self._store.similarity_search(query, self.k)


class InMemoryVectorStore:
    """Tiny cosine vector store. Real swap: langchain_community.vectorstores.Chroma."""

    def __init__(self, embeddings: MockEmbeddings) -> None:
        self.embeddings = embeddings
        self._items: list[tuple[Document, List[float]]] = []

    @classmethod
    def from_documents(cls, docs: List[Document], embeddings: MockEmbeddings) -> "InMemoryVectorStore":
        store = cls(embeddings)
        vecs = embeddings.embed_documents([d.page_content for d in docs])
        store._items = list(zip(docs, vecs))
        return store

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        qv = self.embeddings.embed_query(query)
        ranked = sorted(self._items, key=lambda it: cosine(qv, it[1]), reverse=True)
        return [doc for doc, _ in ranked[:k]]

    def as_retriever(self, k: int = 4) -> _Retriever:
        return _Retriever(self, k)


class MockLLM:
    """Deterministic grounded answerer. Returns the fallback when the context does
    not lexically support the question — so the 'no hallucination' rule is visible.

    Real swap:  from langchain_anthropic import ChatAnthropic
                ChatAnthropic(model="claude-sonnet-4-6")
    """

    FALLBACK = "I don't have that information."

    def answer(self, question: str, context: str) -> str:
        q_tokens = {t for t in _tokenize(question) if len(t) > 3}
        # Pick context sentences that share meaningful tokens with the question.
        best: list[str] = []
        for sentence in re.split(r"(?<=[.!?])\s+", context):
            overlap = q_tokens & set(_tokenize(sentence))
            if overlap:
                best.append(sentence.strip())
        if not best:
            return self.FALLBACK
        return "Based on the document: " + " ".join(best[:2])


SAMPLE_POLICY = """\
Returns Policy. Customers may return any item within 30 days of the purchase date for a full refund.
Items must be unused and in original packaging. Refunds are processed within 5 business days.

Shipping. Standard shipping takes 3 to 5 business days. Express shipping is delivered next business day.
Shipping is free on orders over 50 dollars.

Warranty. All electronics include a 12 month limited warranty covering manufacturing defects.
The warranty does not cover accidental damage or water damage.
"""
