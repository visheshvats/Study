"""
Ingestion pipeline: PDF -> chunks -> embeddings -> Chroma.
Fill in the TODOs. See Phase 2 (02-rag-core) sections 2.1-2.4.
"""
from __future__ import annotations

from typing import List


def load_pdf(path: str) -> List["Document"]:  # type: ignore[name-defined]
    """Load a PDF into LangChain Document objects (one per page)."""
    # TODO: from langchain_community.document_loaders import PyPDFLoader
    # TODO: return PyPDFLoader(path).load()
    raise NotImplementedError


def split(docs: List["Document"], chunk_size: int = 1000, overlap: int = 200):  # type: ignore[name-defined]
    """Split docs into overlapping chunks with RecursiveCharacterTextSplitter."""
    # TODO: build the splitter and return splitter.split_documents(docs)
    raise NotImplementedError


def build_store(chunks, persist_dir: str = "./chroma_db", collection: str = "pdf_docs"):
    """Embed chunks and persist them to a Chroma collection."""
    # TODO: embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    # TODO: return Chroma.from_documents(chunks, embeddings, collection_name=collection,
    #                                    persist_directory=persist_dir)
    raise NotImplementedError


def ingest(path: str, persist_dir: str = "./chroma_db") -> int:
    """End-to-end: load -> split -> store. Return the number of chunks indexed."""
    docs = load_pdf(path)
    chunks = split(docs)
    build_store(chunks, persist_dir)
    return len(chunks)


if __name__ == "__main__":
    # TODO: point at a real PDF once the functions are implemented.
    print("Implement load_pdf/split/build_store, then: ingest('sample.pdf')")
