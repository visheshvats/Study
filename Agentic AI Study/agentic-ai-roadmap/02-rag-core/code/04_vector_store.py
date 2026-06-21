"""04_vector_store.py — storing & retrieving vectors (Phase 2.4).

A vector store is the database that holds your chunk embeddings and answers the
question "give me the k chunks most similar to this query vector." It is the
index in RAG — the thing that makes search fast and the thing you persist so you
don't re-embed your whole corpus on every restart.

Covered here:
  * Chroma — persists to disk (great for dev), reload from persist_directory.
  * Retrieval modes: basic top-k, MMR (Max Marginal Relevance, reduces
    redundancy), and metadata filtering (only search a subset).
  * FAISS — fast in-memory index, save_local / load_local.

Java analogy
------------
A vector store is your search index — think **Elasticsearch / Lucene**, but the
"match" is cosine similarity over dense vectors instead of an inverted token
index. ``as_retriever(...)`` is the configured query handle (like a prepared
``SearchRequest``). ``persist_directory`` is the on-disk index dir — lose it and
you must rebuild, exactly like a Lucene index directory.

Run it:  python 04_vector_store.py
"""

from __future__ import annotations

import logging

# ── OFFLINE SWITCH ──────────────────────────────────────────────────────────
# True  -> a tiny in-memory vector store implemented here (no Chroma/FAISS install).
# False -> real Chroma (persistent) + FAISS, with real embeddings.
USE_MOCK = True

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# MOCK: a minimal vector store so retrieval (top-k, MMR, filtering) runs offline
# ---------------------------------------------------------------------------
class MockVectorStore:
    """In-memory store that mimics the .as_retriever(...) surface of Chroma/FAISS.

    It embeds every chunk on construction (like Chroma.from_documents) and scores
    queries by cosine similarity. Enough to demonstrate top-k, MMR, and metadata
    filtering — the three retrieval behaviours the source guide shows.
    """

    def __init__(self, documents: list, embedding) -> None:
        from mock_kit import cosine_sim

        self._cosine = cosine_sim
        self._docs = list(documents)
        # Pre-compute the chunk vectors once — this is the "indexing" step.
        self._vectors = embedding.embed_documents([d.page_content for d in documents])
        self._embedding = embedding

    def _score_all(self, query: str):
        qv = self._embedding.embed_query(query)
        scored = [
            (self._cosine(qv, vec), doc)
            for vec, doc in zip(self._vectors, self._docs)
        ]
        return sorted(scored, key=lambda pair: pair[0], reverse=True)

    def as_retriever(self, search_type: str = "similarity", search_kwargs: dict | None = None):
        """Return a callable retriever — mirrors LangChain's retriever interface."""
        search_kwargs = search_kwargs or {}
        store = self

        class _Retriever:
            def invoke(self, query: str) -> list:
                k = search_kwargs.get("k", 4)
                metadata_filter = search_kwargs.get("filter")
                ranked = store._score_all(query)

                # Metadata filter: keep only chunks whose metadata matches.
                if metadata_filter:
                    ranked = [
                        (s, d) for s, d in ranked
                        if all(d.metadata.get(key) == val for key, val in metadata_filter.items())
                    ]

                if search_type == "mmr":
                    # Max Marginal Relevance (simplified): take a wider candidate
                    # pool (fetch_k), then greedily pick results that are relevant
                    # AND not near-duplicates of already-picked ones.
                    fetch_k = search_kwargs.get("fetch_k", 20)
                    candidates = ranked[:fetch_k]
                    selected: list = []
                    while candidates and len(selected) < k:
                        # Penalise candidates similar to what we've already chosen.
                        best = max(
                            candidates,
                            key=lambda pair: pair[0] - store._max_overlap(pair[1], selected),
                        )
                        selected.append(best[1])
                        candidates.remove(best)
                    return selected

                # Default: plain top-k similarity.
                return [doc for _score, doc in ranked[:k]]

        return _Retriever()

    def _max_overlap(self, doc, selected: list) -> float:
        """Rough redundancy penalty: highest cosine to any already-selected doc."""
        if not selected:
            return 0.0
        dv = self._embedding.embed_query(doc.page_content)
        return max(
            self._cosine(dv, self._embedding.embed_query(s.page_content)) for s in selected
        )


def build_store_mock(chunks: list):
    from mock_kit import MockEmbeddings

    logger.info("[MOCK] Building in-memory vector store over %d chunks.", len(chunks))
    return MockVectorStore(chunks, MockEmbeddings(dim=64))


def build_store_real(chunks: list):
    """Build BOTH a persistent Chroma store and an in-memory FAISS store.

    Requires:  pip install chromadb faiss-cpu langchain-community langchain-openai
    TODO: set OPENAI_API_KEY in your .env.
    """
    from langchain_community.vectorstores import Chroma, FAISS
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # ─── Chroma — persists to disk; survives restarts ───
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="product_docs",
        persist_directory="./chroma_db",  # CRITICAL: omit this and your index vanishes on exit
    )

    # Reload an EXISTING store later (no re-embedding) — note: same model required.
    # vectorstore = Chroma(
    #     collection_name="product_docs",
    #     embedding_function=embeddings,
    #     persist_directory="./chroma_db",
    # )

    # ─── FAISS — fast in-memory; explicitly save/load to disk ───
    faiss_store = FAISS.from_documents(chunks, embeddings)
    faiss_store.save_local("./faiss_index")
    # allow_dangerous_deserialization unpickles the index — ONLY enable for files
    # YOU created. Never load a FAISS index from an untrusted source (RCE risk).
    # faiss_loaded = FAISS.load_local(
    #     "./faiss_index", embeddings, allow_dangerous_deserialization=True
    # )
    logger.info("Built Chroma (persisted to ./chroma_db) and FAISS (saved to ./faiss_index).")
    return vectorstore


def build_store(chunks: list):
    return build_store_mock(chunks) if USE_MOCK else build_store_real(chunks)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    from mock_kit import sample_documents

    chunks = sample_documents()  # in real usage these would be split chunks from step 02
    store = build_store(chunks)

    query = "How long do refunds take?"

    # ─── Basic top-k retrieval ───
    retriever_basic = store.as_retriever(search_kwargs={"k": 2})
    logger.info("---- Basic top-2 for %r ----", query)
    for d in retriever_basic.invoke(query):
        logger.info("  [%s/%s] %s", d.metadata.get("source"), d.metadata.get("section"),
                    d.page_content[:60])

    # ─── MMR (diversity-aware) ───
    retriever_mmr = store.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 5})
    logger.info("---- MMR top-2 (less redundant) ----")
    for d in retriever_mmr.invoke(query):
        logger.info("  [%s/%s] %s", d.metadata.get("source"), d.metadata.get("section"),
                    d.page_content[:60])

    # ─── Metadata filtering — only search the 'shipping' section ───
    retriever_filtered = store.as_retriever(search_kwargs={"k": 2, "filter": {"section": "shipping"}})
    logger.info("---- Filtered to section='shipping' ----")
    for d in retriever_filtered.invoke("when does my order arrive?"):
        logger.info("  [%s/%s] %s", d.metadata.get("source"), d.metadata.get("section"),
                    d.page_content[:60])

    logger.info("Vector store demo complete.")
