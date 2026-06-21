"""mock_kit.py — shared OFFLINE scaffolding for Phase 2 RAG demos.

Why this file exists
--------------------
Every Phase 2 example *conceptually* needs three things that cost money or
require files you don't have yet:

  1. An embeddings model (OpenAI) — needs an API key + network.
  2. Source documents (PDFs / CSVs / web pages) — won't exist on your disk.
  3. An LLM (Claude) — needs an API key + network.

So instead of failing on import, the scripts default to ``USE_MOCK = True`` and
pull deterministic, dependency-free stand-ins from this module. The *concepts*
(chunking, cosine similarity, top-k retrieval, LCEL piping) all still work and
print real numbers — only the "intelligence" is faked.

Java analogy
------------
This is exactly your test setup with **Mockito / a fake repository**: the same
interfaces the production code expects, but with deterministic in-memory
implementations so the unit under test runs without a database or network.

When you are ready for the real thing, each script tells you the one or two
lines to change (set ``USE_MOCK = False`` and provide a key).
"""

from __future__ import annotations

import hashlib
import logging
import math
import re
from typing import Sequence

# We deliberately re-create tiny stand-ins for langchain_core.Document and the
# Embeddings interface so this module imports with ZERO third-party packages.
# If LangChain is installed, the real Document is import-compatible (same
# attribute names: .page_content and .metadata).

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Document — a structurally-compatible stand-in for langchain_core.documents.Document
# ---------------------------------------------------------------------------
class Document:
    """A chunk of text plus metadata.

    Java analogy: a plain DTO / record —
        record Document(String pageContent, Map<String,Object> metadata) {}

    The real ``langchain_core.documents.Document`` exposes the same two
    attributes (``page_content`` and ``metadata``), so code written against
    this stand-in works unchanged once you swap in the real loaders.
    """

    def __init__(self, page_content: str, metadata: dict | None = None) -> None:
        self.page_content: str = page_content
        self.metadata: dict = metadata or {}

    def __repr__(self) -> str:  # readable logging, like a good toString()
        preview = self.page_content[:50].replace("\n", " ")
        return f"Document(meta={self.metadata}, text={preview!r}...)"


# ---------------------------------------------------------------------------
# MockEmbeddings — deterministic bag-of-words vectors (no API, no network)
# ---------------------------------------------------------------------------
class MockEmbeddings:
    """A deterministic, dependency-free embeddings model.

    Strategy: hash each word into one of ``dim`` buckets and count it
    (a "hashing vectorizer" / bag-of-words). Texts that share words land in the
    same buckets, so they end up with similar vectors — which means cosine
    similarity still behaves correctly: related sentences score HIGH, unrelated
    sentences score LOW. It is NOT semantic (no synonyms), but it is enough to
    make the *math lesson* land.

    Java analogy: think of it as a hand-rolled ``HashingVectorizer`` — a
    deterministic ``Function<String, double[]>`` you could unit-test.

    Interface parity: exposes ``embed_query`` and ``embed_documents``, exactly
    like ``langchain_openai.OpenAIEmbeddings``, so it is a drop-in replacement.
    """

    def __init__(self, dim: int = 64) -> None:
        # Real OpenAI text-embedding-3-small is 1536-dim; 64 is plenty for a demo.
        self.dim = dim

    def _tokenize(self, text: str) -> list[str]:
        # Lowercase + split on non-letters. (A real tokenizer is far richer.)
        return re.findall(r"[a-z]+", text.lower())

    def embed_query(self, text: str) -> list[float]:
        """Embed a single string into a fixed-length vector."""
        vec = [0.0] * self.dim
        for word in self._tokenize(text):
            # Stable hash -> bucket index. (Python's built-in hash() is salted
            # per-process, so we use md5 for run-to-run determinism.)
            bucket = int(hashlib.md5(word.encode()).hexdigest(), 16) % self.dim
            vec[bucket] += 1.0
        return vec

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed many strings — same contract as OpenAIEmbeddings.embed_documents."""
        return [self.embed_query(t) for t in texts]


# ---------------------------------------------------------------------------
# cosine_sim — the one formula at the heart of all vector search
# ---------------------------------------------------------------------------
def cosine_sim(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity in [-1, 1]; 1.0 = identical direction (same meaning).

    Pure-Python (no numpy) so this module has zero dependencies. The real demo
    in 03_embeddings_cosine.py shows the numpy one-liner too.

    similarity = (a . b) / (||a|| * ||b||)
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0  # avoid divide-by-zero on empty text
    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Sample corpus — stands in for "PDFs / CSVs you loaded"
# ---------------------------------------------------------------------------
def sample_documents() -> list[Document]:
    """A small, realistic in-memory corpus (a fake product/policy knowledge base).

    These are what you'd normally get back from PyPDFLoader / CSVLoader.
    Metadata mirrors what real loaders attach (source, section, page, year),
    so metadata-filtering examples are meaningful.
    """
    return [
        Document(
            "Our return policy allows refunds within 30 days of the purchase "
            "date. Items must be unused and in original packaging.",
            {"source": "policy_v2", "section": "returns", "year": 2024},
        ),
        Document(
            "Refund processing takes 5 to 7 business days after we receive the "
            "returned item. The credit goes back to the original payment method.",
            {"source": "policy_v2", "section": "returns", "year": 2024},
        ),
        Document(
            "Standard shipping is free on orders over 50 dollars and arrives in "
            "3 to 5 business days. Express shipping arrives next day.",
            {"source": "policy_v2", "section": "shipping", "year": 2024},
        ),
        Document(
            "The annual subscription costs 99 dollars and includes priority "
            "support and unlimited downloads for one calendar year.",
            {"source": "pricing", "section": "subscription", "year": 2024},
        ),
        Document(
            "Python is a high level programming language widely used for web "
            "development, data science, and building AI agents.",
            {"source": "tech_notes", "section": "languages", "year": 2023},
        ),
    ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    emb = MockEmbeddings()
    docs = sample_documents()
    logger.info("Loaded %d sample documents.", len(docs))
    logger.info("Embedding dim = %d", emb.dim)
    q = emb.embed_query("how long for a refund?")
    d = emb.embed_query(docs[1].page_content)
    logger.info("cosine(query, refund-doc) = %.3f", cosine_sim(q, d))
