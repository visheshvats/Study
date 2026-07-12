"""
Ingestion pipeline: document -> chunks -> embeddings -> vector store.
Phases 0-2. Runs OFFLINE via mock_kit when USE_MOCK=True; flip to real loaders/
embeddings/Chroma for production.
"""
from __future__ import annotations

import logging
from typing import List, Tuple

from langchain_core.documents import Document

import mock_kit

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ingest")

USE_MOCK = True


def load_documents(path: str | None = None) -> List[Document]:
    """Load source documents.

    MOCK: return the bundled SAMPLE_POLICY as one Document.
    REAL: PyPDFLoader(path).load()  (pip install pypdf langchain-community)
    """
    if USE_MOCK:
        logger.info("[MOCK] loading bundled sample policy document")
        return [Document(page_content=mock_kit.SAMPLE_POLICY, metadata={"source": "sample_policy"})]
    from langchain_community.document_loaders import PyPDFLoader  # type: ignore

    if not path:
        raise ValueError("path is required when USE_MOCK is False")
    return PyPDFLoader(path).load()


def split(docs: List[Document], chunk_size: int = 300, overlap: int = 50) -> List[Document]:
    """Split documents into overlapping chunks.

    MOCK: a simple paragraph/character splitter with overlap.
    REAL: RecursiveCharacterTextSplitter(chunk_size, chunk_overlap)  (pip install langchain-text-splitters)
    """
    if not USE_MOCK:
        from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        return splitter.split_documents(docs)

    chunks: List[Document] = []
    for doc in docs:
        text = doc.page_content
        # Prefer paragraph boundaries; fall back to fixed windows with overlap.
        units = [u.strip() for u in text.split("\n\n") if u.strip()] or [text]
        for u in units:
            if len(u) <= chunk_size:
                chunks.append(Document(page_content=u, metadata=dict(doc.metadata)))
            else:
                start = 0
                while start < len(u):
                    chunks.append(Document(page_content=u[start:start + chunk_size], metadata=dict(doc.metadata)))
                    start += chunk_size - overlap
    logger.info("[MOCK] split %d docs into %d chunks", len(docs), len(chunks))
    return chunks


def build_store(chunks: List[Document]):
    """Embed chunks and build a vector store.

    MOCK: in-memory cosine store.
    REAL: Chroma.from_documents(chunks, OpenAIEmbeddings(...), persist_directory=...)
    """
    if USE_MOCK:
        return mock_kit.InMemoryVectorStore.from_documents(chunks, mock_kit.MockEmbeddings())
    from langchain_community.vectorstores import Chroma  # type: ignore
    from langchain_openai import OpenAIEmbeddings  # type: ignore

    return Chroma.from_documents(
        chunks, OpenAIEmbeddings(model="text-embedding-3-small"),
        collection_name="pdf_docs", persist_directory="./chroma_db",
    )


def ingest(path: str | None = None) -> Tuple[object, int]:
    """End-to-end: load -> split -> store. Returns (store, n_chunks)."""
    docs = load_documents(path)
    chunks = split(docs)
    store = build_store(chunks)
    logger.info("ingested %d chunks", len(chunks))
    return store, len(chunks)


if __name__ == "__main__":
    store, n = ingest()
    print(f"Indexed {n} chunks. Sample retrieval for 'refund window':")
    for d in store.as_retriever(k=2).invoke("refund window"):
        print("  -", d.page_content[:80].replace("\n", " "), "...")
