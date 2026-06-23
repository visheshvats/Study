"""
10.2 — Embedding Cache (runs fully OFFLINE)
===========================================

Why an embedding cache saves real money
----------------------------------------
Embeddings are *content-addressable*: the same text always maps to the same
vector. In any real retrieval pipeline (RAG, semantic search, dedup) the SAME
strings recur constantly — popular FAQ questions, repeated document chunks,
boilerplate. Re-embedding them is paying twice for an identical answer.

A cache turns those repeats into near-free dictionary lookups. Concretely, if
your live traffic has a 70% hit rate, you cut embedding spend by ~70% AND remove
that latency from the hot path. That is the single highest-leverage cost lever
in most agent stacks.

    Java analogy: Caffeine ``Cache`` with ``maximumSize(...)`` + LRU/LFU
    eviction, or Spring's ``@Cacheable`` where the cache key is derived from the
    method argument. Here the key is ``sha256(text)``.

OFFLINE NOTE
------------
``_mock_embed`` is a *deterministic* hash-seeded vector — no API, no key. Same
text -> same vector, every time, which is exactly the property a cache relies on.
To go live, set ``USE_MOCK=False`` and complete the TODO in ``_real_embed``
(LangChain / provider embeddings).

Run:  python3 02_embedding_cache.py
"""

from __future__ import annotations

import hashlib
import logging
import random
from collections import OrderedDict
from typing import Callable, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("embed_cache")

USE_MOCK: bool = True          # flip to False to use a real embedding model
EMBED_DIM: int = 8             # tiny dim so demo output is readable


# --------------------------------------------------------------------------- #
# LRU embedding cache
# --------------------------------------------------------------------------- #
class LRUEmbeddingCache:
    """Bounded least-recently-used cache mapping text -> embedding vector.

    Bounded is the whole point. An *unbounded* dict that grows with every unique
    query is a memory leak that eventually OOM-kills the process — a classic
    production incident. ``max_size`` caps it; the least-recently-used entry is
    evicted first.

    Java analogy: ``Caffeine.newBuilder().maximumSize(maxSize).build()``.
    ``OrderedDict.move_to_end`` == bumping recency; ``popitem(last=False)`` ==
    evicting the coldest entry.
    """

    def __init__(self, max_size: int = 5000) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self._cache: "OrderedDict[str, List[float]]" = OrderedDict()
        self.max_size: int = max_size
        self.hits: int = 0
        self.misses: int = 0

    @staticmethod
    def _key(text: str) -> str:
        """Stable content hash. Hashing also normalises huge keys to 64 chars."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> Optional[List[float]]:
        k = self._key(text)
        if k in self._cache:
            self._cache.move_to_end(k)  # mark as most-recently-used
            self.hits += 1
            return self._cache[k]
        self.misses += 1
        return None

    def set(self, text: str, embedding: List[float]) -> None:
        k = self._key(text)
        if k in self._cache:
            self._cache.move_to_end(k)
        elif len(self._cache) >= self.max_size:
            evicted, _ = self._cache.popitem(last=False)  # drop coldest
            logger.debug("Evicted LRU entry %s…", evicted[:8])
        self._cache[k] = embedding

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total, 3) if total else 0.0

    def stats(self) -> str:
        return (f"size={len(self._cache)}/{self.max_size} "
                f"hits={self.hits} misses={self.misses} "
                f"hit_rate={self.hit_rate:.1%}")


embedding_cache = LRUEmbeddingCache(max_size=1000)


# --------------------------------------------------------------------------- #
# The embedding function — mock by default, real model behind a flag
# --------------------------------------------------------------------------- #
def _mock_embed(text: str) -> List[float]:
    """Deterministic pseudo-embedding seeded by the text's hash.

    Same input -> identical vector every call. This mimics the contract a real
    embedding model gives you and is what makes caching correct.
    """
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
    rng = random.Random(seed)
    return [round(rng.uniform(-1.0, 1.0), 4) for _ in range(EMBED_DIM)]


def _real_embed(text: str) -> List[float]:
    """Live embedding call. Only used when USE_MOCK is False."""
    # TODO (to go live):
    #   1) pip install langchain-openai   (or your provider's embedding pkg)
    #   2) set the relevant API key in the environment
    #   3) Uncomment and delete the RuntimeError.
    #
    # from langchain_openai import OpenAIEmbeddings
    # model = OpenAIEmbeddings(model="text-embedding-3-small")
    # return model.embed_query(text)
    raise RuntimeError("Set USE_MOCK=False and complete the TODO to go live.")


def embed_with_cache(text: str, embed_fn: Callable[[str], List[float]] | None = None
                     ) -> List[float]:
    """Return the embedding for ``text``, serving from cache on a hit.

    Pass a custom ``embed_fn`` for tests; defaults to mock/real per ``USE_MOCK``.
    """
    cached = embedding_cache.get(text)
    if cached is not None:
        return cached
    fn = embed_fn or (_mock_embed if USE_MOCK else _real_embed)
    vec = fn(text)
    embedding_cache.set(text, vec)
    return vec


# --------------------------------------------------------------------------- #
# Demo: hit-rate under a realistic, skewed query mix
# --------------------------------------------------------------------------- #
def _demo() -> None:
    # Real traffic is Zipf-like: a few queries dominate. We model that with a
    # weighted pool so repeats (and thus cache hits) occur naturally.
    hot = ["What is my balance?", "Reset my password", "Store hours?"]
    warm = [f"Order status for #{i}" for i in range(10)]
    cold = [f"Edge case query {i}" for i in range(40)]

    population = hot * 8 + warm * 2 + cold * 1   # weights: hot >> warm >> cold
    rng = random.Random(42)
    stream = [rng.choice(population) for _ in range(300)]

    logger.info("Processing %d queries through embed_with_cache()…", len(stream))
    for q in stream:
        _ = embed_with_cache(q)

    logger.info("Cache stats: %s", embedding_cache.stats())

    # Prove determinism + that a repeat is a hit.
    h0 = embedding_cache.hits
    v1 = embed_with_cache("Reset my password")
    v2 = embed_with_cache("Reset my password")
    assert v1 == v2, "embeddings must be deterministic for caching to be valid"
    assert embedding_cache.hits == h0 + 2, "both repeats should be cache hits"
    logger.info("Determinism check passed; sample vector = %s", v1)

    # Demonstrate bounded eviction (no unbounded growth -> no memory leak).
    tiny = LRUEmbeddingCache(max_size=3)
    for i in range(10):
        tiny.set(f"k{i}", [float(i)])
    logger.info("Bounded cache held at size=%d after 10 inserts (max_size=3)",
                len(tiny._cache))
    assert len(tiny._cache) == 3


if __name__ == "__main__":
    _demo()
