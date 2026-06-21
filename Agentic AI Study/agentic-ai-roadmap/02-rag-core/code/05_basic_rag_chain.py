"""05_basic_rag_chain.py — wiring retrieval + LLM with LCEL (Phase 2.5).

This assembles the full query-time pipeline:

    question -> retrieve top-k chunks -> format into context
             -> fill prompt template -> call LLM -> parse text

LangChain Expression Language (LCEL) glues these stages with the ``|`` pipe.

Java analogy
------------
LCEL's ``|`` is a **fluent builder / Stream pipeline**. Reading
``retriever | format_docs | prompt | llm | parser`` is exactly like reading
``stream.map(...).filter(...).map(...).collect(...)`` — each stage's output is
the next stage's input. The dict ``{"context": ..., "question": ...}`` step is
a fan-out: it computes both keys (one runs retrieval, one passes the question
straight through) and hands a populated map downstream — like building a DTO
from several services before passing it to the next layer.

``RunnablePassthrough()`` is the identity function: it forwards its input
untouched (here, the raw question) so the prompt can see it alongside the
retrieved context.

Run it:  python 05_basic_rag_chain.py
"""

from __future__ import annotations

import logging

# ── OFFLINE SWITCH ──────────────────────────────────────────────────────────
# True  -> mock retriever + a FAKE llm that just echoes the context (no key).
# False -> real Chroma retriever + real ChatAnthropic (needs ANTHROPIC_API_KEY + OPENAI_API_KEY).
USE_MOCK = True

logger = logging.getLogger(__name__)


# format_docs is shared by mock and real paths — it turns a list of Documents
# into a single string the prompt can interpolate. (Same as the source guide.)
def format_docs(docs) -> str:
    """Join retrieved Documents into one labelled context block."""
    return "\n\n---\n\n".join(
        f"[Source: {d.metadata.get('source', 'unknown')}]\n{d.page_content}"
        for d in docs
    )


RAG_PROMPT_TEXT = """Answer the question based ONLY on the context below.
If the answer is not in the context, say "I don't have that information."
Do NOT make up information.

Context:
{context}

Question: {question}

Answer:"""


# ---------------------------------------------------------------------------
# MOCK path: a fake LLM so the whole pipe runs end-to-end with no API key
# ---------------------------------------------------------------------------
def build_chain_mock():
    """Return a callable that takes a question string and returns an answer string.

    We assemble the same logical stages as LCEL, but in plain Python so it runs
    offline. The 'LLM' is a deterministic stub: it extracts the most relevant
    sentence from the retrieved context (a stand-in for real generation).
    """
    from mock_kit import MockEmbeddings, sample_documents

    # Build the mock store+retriever from 04 by importing it.
    from importlib import import_module

    vs_module = import_module("04_vector_store")
    store = vs_module.MockVectorStore(sample_documents(), MockEmbeddings(dim=64))
    retriever = store.as_retriever(search_kwargs={"k": 2})

    def fake_llm(prompt_text: str) -> str:
        # A REAL LLM reads the whole prompt and reasons. Our stub just returns
        # the first context line so you can SEE retrieval feeding generation.
        for line in prompt_text.splitlines():
            line = line.strip()
            if line and not line.startswith(("[Source", "Context", "Question", "Answer", "---")) \
                    and "Answer the question" not in line and "If the answer" not in line \
                    and "Do NOT" not in line:
                return f"(mock answer derived from context) {line}"
        return "I don't have that information."

    def chain(question: str) -> str:
        docs = retriever.invoke(question)                       # retrieve
        context = format_docs(docs)                             # format_docs
        prompt_text = RAG_PROMPT_TEXT.format(context=context, question=question)  # prompt
        return fake_llm(prompt_text)                            # llm -> str

    logger.info("[MOCK] Built RAG chain (mock retriever + stub LLM).")
    return chain


# ---------------------------------------------------------------------------
# REAL path: the actual LCEL chain from the source guide
# ---------------------------------------------------------------------------
def build_chain_real():
    """Build the real LCEL RAG chain.

    Requires:  pip install langchain-anthropic langchain-openai langchain-community chromadb
    TODO: set ANTHROPIC_API_KEY and OPENAI_API_KEY in your .env.
    """
    from langchain_anthropic import ChatAnthropic
    from langchain_community.vectorstores import Chroma
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    # Assumes you already persisted this store in 04_vector_store.py.
    vectorstore = Chroma(
        collection_name="product_docs",
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = ChatAnthropic(model="claude-sonnet-4-6")
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEXT)

    # The LCEL chain — read it top-to-bottom like a Stream pipeline.
    rag_chain = (
        {
            "context": retriever | format_docs,   # retrieve, then stringify
            "question": RunnablePassthrough(),     # forward the raw question untouched
        }
        | prompt          # fill the template
        | llm             # call Claude
        | StrOutputParser()  # extract plain text from the chat message
    )
    logger.info("Built real LCEL RAG chain (Chroma retriever + ChatAnthropic).")
    return lambda q: rag_chain.invoke(q)


def build_chain():
    return build_chain_mock() if USE_MOCK else build_chain_real()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    chain = build_chain()

    for question in ["What is the return policy?", "Who won the world cup?"]:
        logger.info("Q: %s", question)
        logger.info("A: %s", chain(question))
        logger.info("-" * 50)

    logger.info("Basic RAG chain demo complete.")
