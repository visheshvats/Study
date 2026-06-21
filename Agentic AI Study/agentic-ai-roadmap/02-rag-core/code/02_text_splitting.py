"""02_text_splitting.py — chunking documents for retrieval (Phase 2.2).

Loaders give you whole pages; an LLM retrieves *chunks*. Splitting cuts long
text into overlapping windows so that (a) each chunk fits comfortably in the
context window and (b) a single chunk carries enough surrounding context to be
meaningful on its own.

The two knobs that decide everything:
  * chunk_size    — how big each window is.
  * chunk_overlap — how much the end of one chunk repeats at the start of the next,
                    so a sentence split across a boundary isn't lost.

Java analogy
------------
This is windowing over a stream with a slide: think
``Collections`` / ``Lists.partition`` but with a deliberate *overlap* between
partitions — like a sliding-window batch where consecutive batches share a tail.

Run it:  python 02_text_splitting.py
"""

from __future__ import annotations

import logging

# ── OFFLINE SWITCH ──────────────────────────────────────────────────────────
# True  -> use a tiny hand-written splitter so the lesson runs with no installs.
# False -> use the REAL LangChain RecursiveCharacterTextSplitter / TokenTextSplitter.
USE_MOCK = True

logger = logging.getLogger(__name__)


def split_mock(docs: list, chunk_size: int, chunk_overlap: int) -> list:
    """A minimal character splitter that mimics chunk_size + overlap.

    It is NOT as smart as RecursiveCharacterTextSplitter (which prefers to break
    on paragraph/sentence boundaries), but it demonstrates the SAME two knobs and
    shows overlap visibly. Real semantics noted in split_real().
    """
    from mock_kit import Document

    chunks: list = []
    step = max(1, chunk_size - chunk_overlap)  # how far the window advances each time
    for doc in docs:
        text = doc.page_content
        start = 0
        while start < len(text):
            piece = text[start : start + chunk_size]
            chunks.append(Document(piece, {**doc.metadata, "chunk_start": start}))
            if start + chunk_size >= len(text):
                break
            start += step
    logger.info(
        "[MOCK] split %d docs into %d chunks (size=%d, overlap=%d)",
        len(docs), len(chunks), chunk_size, chunk_overlap,
    )
    return chunks


def split_real(docs: list, chunk_size: int, chunk_overlap: int) -> list:
    """Split with the REAL RecursiveCharacterTextSplitter — USE THIS in production.

    Requires:  pip install langchain
    """
    from langchain.text_splitter import (
        RecursiveCharacterTextSplitter,
        TokenTextSplitter,  # noqa: F401  (shown for reference below)
    )

    # RecursiveCharacterTextSplitter tries separators in priority order:
    #   "\n\n" (paragraphs) -> "\n" (lines) -> ". " (sentences) -> " " -> char.
    # That means it keeps natural boundaries intact when it can — far better
    # than the blunt character cut in split_mock().
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,       # ~750 words at 1000 chars
        chunk_overlap=chunk_overlap, # keep context across boundaries
        length_function=len,         # measure in characters; swap for a token counter if needed
    )
    chunks = splitter.split_documents(docs)

    # ─── Token-based alternative (exact token counts, e.g. to respect a model limit) ───
    # token_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=64)
    # chunks = token_splitter.split_documents(docs)

    logger.info("Split %d docs into %d chunks (size=%d, overlap=%d)",
                len(docs), len(chunks), chunk_size, chunk_overlap)
    return chunks


def split_documents(docs: list, chunk_size: int = 120, chunk_overlap: int = 30) -> list:
    """Dispatch to mock or real. Small sizes by default so overlap is visible in the demo."""
    if USE_MOCK:
        return split_mock(docs, chunk_size, chunk_overlap)
    return split_real(docs, chunk_size, chunk_overlap)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    from mock_kit import sample_documents

    docs = sample_documents()

    # Deliberately small chunk_size so you can SEE the overlap in the output.
    chunks = split_documents(docs, chunk_size=120, chunk_overlap=30)

    logger.info("---- Inspect chunk boundaries (notice the repeated tail/head) ----")
    for i, c in enumerate(chunks[:4]):
        logger.info("chunk[%d] (%d chars): %r", i, len(c.page_content), c.page_content)

    # ─── Why chunk size matters (rule of thumb) ───
    # Too large:  context window fills fast, retrieval is less precise (you pull
    #             in a wall of text where only one sentence was relevant).
    # Too small:  chunks lack surrounding context, meaning is lost.
    # Practical:  500-1500 chars, overlap = 10-20% of chunk_size.
    logger.info("Text splitting demo complete. Try changing chunk_size/overlap and re-run.")
