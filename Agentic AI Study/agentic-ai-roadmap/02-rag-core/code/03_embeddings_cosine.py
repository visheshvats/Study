"""03_embeddings_cosine.py — embeddings & cosine similarity (Phase 2.3).

This is the conceptual heart of RAG. An *embedding* turns text into a fixed-length
vector of numbers that encodes its MEANING. Texts with similar meaning point in
similar directions in that high-dimensional space, and *cosine similarity*
measures how aligned two vectors are (1.0 = same direction, 0.0 = unrelated).

Retrieval is then "find the stored chunks whose vectors point most like the
query's vector." That's it.

Java analogy
------------
An embedding model is a deterministic ``Function<String, double[]>``. Cosine
similarity is your comparator/score function — like a custom
``Comparator<double[]>`` you'd sort search hits by. Crucially it is a *fuzzy*
score, NOT ``equals()``: 0.83 means "very close in meaning," there is no exact
match the way ``map.get(key)`` either hits or misses.

This script ACTUALLY computes and prints similarities (using the offline mock
embedder by default) so the high-vs-low lesson lands without an API key.

Run it:  python 03_embeddings_cosine.py
"""

from __future__ import annotations

import logging

# ── OFFLINE SWITCH ──────────────────────────────────────────────────────────
# True  -> deterministic MockEmbeddings (no key, no network). Default.
# False -> real OpenAIEmbeddings(model="text-embedding-3-small"). Needs OPENAI_API_KEY.
USE_MOCK = True

logger = logging.getLogger(__name__)


def get_embedder():
    """Return an embeddings object exposing embed_query/embed_documents.

    The mock and the real OpenAIEmbeddings share the same interface, so the rest
    of the script doesn't care which one it got — classic dependency inversion.
    """
    if USE_MOCK:
        from mock_kit import MockEmbeddings

        logger.info("[MOCK] Using deterministic bag-of-words embeddings (dim=64).")
        return MockEmbeddings(dim=64)

    # ─── REAL embeddings ───  (TODO: set OPENAI_API_KEY in your .env)
    from langchain_openai import OpenAIEmbeddings

    logger.info("Using real OpenAIEmbeddings (text-embedding-3-small, dim=1536).")
    return OpenAIEmbeddings(model="text-embedding-3-small")


def cosine_sim_numpy(a: list, b: list) -> float:
    """The textbook numpy one-liner (the form the source guide uses).

    Falls back to the pure-Python version if numpy isn't installed, so the demo
    still runs offline with zero dependencies.
    """
    try:
        import numpy as np

        va, vb = np.array(a), np.array(b)
        return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))
    except ImportError:
        from mock_kit import cosine_sim

        return cosine_sim(a, b)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    embedder = get_embedder()

    # Three sentences: the first two share a topic (Python/tech), the third is
    # about a literal snake. We EXPECT high similarity between 0 and 1, low for 0 vs 2.
    texts = [
        "Python is a programming language",   # tech
        "Django is a Python web framework",   # tech — related to the first
        "A snake is a reptile with no legs",  # unrelated meaning
    ]

    # embed_documents == batch embed; same call shape as OpenAIEmbeddings.
    vecs = embedder.embed_documents(texts)
    logger.info("Embedded %d texts into %d-dim vectors.", len(vecs), len(vecs[0]))

    sim_related = cosine_sim_numpy(vecs[0], vecs[1])
    sim_unrelated = cosine_sim_numpy(vecs[0], vecs[2])

    logger.info("Python vs Django:  %.3f  <- expect HIGHER (shared words/meaning)", sim_related)
    logger.info("Python vs snake:   %.3f  <- expect LOWER  (different meaning)", sim_unrelated)

    # The lesson, asserted: related text must score higher than unrelated text.
    # (With real OpenAI embeddings you'd see ~0.87 vs ~0.30; the mock numbers
    #  differ but preserve the ordering, which is the whole point.)
    if sim_related > sim_unrelated:
        logger.info("PASS: related text scored higher than unrelated text. This is why retrieval works.")
    else:
        logger.warning("Unexpected ordering — with the bag-of-words mock this can happen on edge cases.")

    logger.info("Embeddings & cosine similarity demo complete.")
