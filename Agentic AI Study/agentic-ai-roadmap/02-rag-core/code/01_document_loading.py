"""01_document_loading.py — turning raw sources into Document objects (Phase 2.1).

The very first stage of RAG indexing: take PDFs, CSVs, web pages, and raw text
and normalise them all into one uniform shape — the ``Document`` (page_content +
metadata). Everything downstream (splitting, embedding, retrieval) only ever
sees ``Document`` objects, never the original file format.

Java analogy
------------
Loaders are your **adapters / repositories**: a ``PyPDFLoader`` is a
``PdfRepository``, a ``CSVLoader`` is a ``CsvRepository``. They each speak a
different backend but all return the same domain object — like Spring Data
repositories all returning your ``@Entity`` regardless of the underlying store.

Run it:  python 01_document_loading.py
"""

from __future__ import annotations

import logging

# ── OFFLINE SWITCH ──────────────────────────────────────────────────────────
# True  -> use in-memory sample docs (no files, no network). Default.
# False -> use the REAL LangChain loaders below (needs the files to exist).
USE_MOCK = True

logger = logging.getLogger(__name__)


def load_documents_mock() -> list:
    """Return a fixed in-memory corpus that stands in for loaded files.

    In real life these would come back from PyPDFLoader/CSVLoader/WebBaseLoader.
    """
    from mock_kit import sample_documents

    docs = sample_documents()
    logger.info("[MOCK] Loaded %d documents from the in-memory sample corpus.", len(docs))
    return docs


def load_documents_real() -> list:
    """Load from REAL sources using LangChain community loaders.

    Swap in your own file paths / URLs. This is the code the source guide shows.
    Requires:  pip install langchain-community pypdf
    """
    # NOTE: imports are inside the function so the file still runs offline
    # even when langchain_community is not installed.
    from langchain_community.document_loaders import (
        CSVLoader,
        DirectoryLoader,
        PyPDFLoader,
        WebBaseLoader,
    )
    from langchain_core.documents import Document

    all_docs: list = []

    # ─── PDF: one file ───  (TODO: point at a real PDF on your disk)
    pdf_loader = PyPDFLoader("./docs/user_manual.pdf")
    pdf_docs = pdf_loader.load()
    logger.info("Pages loaded: %d", len(pdf_docs))
    logger.info("First page metadata: %s", pdf_docs[0].metadata)  # {'source':..., 'page':0}
    all_docs.extend(pdf_docs)

    # ─── Entire folder of PDFs ───  (loader_cls = which loader to use per file)
    dir_loader = DirectoryLoader(
        "./docs/", glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True
    )
    all_docs.extend(dir_loader.load())

    # ─── Web page ───  (downloads + strips HTML to text)
    web_loader = WebBaseLoader("https://docs.anthropic.com/en/docs/about-claude/models")
    all_docs.extend(web_loader.load())

    # ─── CSV ───  (metadata_columns promotes those columns into metadata)
    csv_loader = CSVLoader("./data/products.csv", metadata_columns=["product_id", "category"])
    all_docs.extend(csv_loader.load())

    # ─── Manual document ───  (build one by hand, e.g. a policy snippet)
    all_docs.append(
        Document(
            page_content="The refund window is 30 days from purchase date.",
            metadata={"source": "policy_v2", "section": "returns", "year": 2024},
        )
    )

    logger.info("Loaded %d documents from real sources.", len(all_docs))
    return all_docs


def load_documents() -> list:
    """Dispatch to mock or real based on the USE_MOCK flag."""
    return load_documents_mock() if USE_MOCK else load_documents_real()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    docs = load_documents()

    # Inspect what a Document looks like — page_content + metadata, every time.
    for i, doc in enumerate(docs):
        preview = doc.page_content[:60].replace("\n", " ")
        logger.info("doc[%d] meta=%s text=%r...", i, doc.metadata, preview)

    logger.info("Document loading demo complete. (%d documents ready for splitting.)", len(docs))
