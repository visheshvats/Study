"""06_conversational_rag.py — RAG that remembers the conversation (Phase 2.6).

A basic RAG chain is stateless: every question is answered in isolation.
Conversational RAG adds *memory* so follow-ups work. When the user asks
"How long does it take to process?", the word "it" only makes sense given the
previous turn ("the return policy"). The chain rewrites the follow-up into a
standalone question using chat history, THEN retrieves and answers.

Java analogy
------------
Memory is your **HttpSession / conversation-scoped bean**. The basic chain is a
stateless ``@RestController`` endpoint; conversational RAG is the same endpoint
backed by a session that accumulates context across requests.
``ConversationBufferWindowMemory(k=5)`` is a bounded session — a sliding window
that keeps only the last 5 exchanges so the context (and token cost) stays
bounded, like an LRU-capped cache rather than an unbounded list.

Run it:  python 06_conversational_rag.py
"""

from __future__ import annotations

import logging

# OFFLINE SWITCH -------------------------------------------------------------
# True  -> mock retriever + stub LLM + a simple in-memory history (no key).
# False -> real ConversationalRetrievalChain with ChatAnthropic + Chroma.
USE_MOCK = True

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# MOCK path: demonstrates memory + coreference ("it" -> previous topic) offline
# ---------------------------------------------------------------------------
def build_conv_chain_mock():
    """A stub conversational chain that keeps a windowed history and resolves 'it'.

    It shows the SHAPE of conversational RAG (history -> rewrite -> retrieve ->
    answer) without an LLM. The 'rewrite' is a crude heuristic; a real chain
    uses the LLM to condense history + follow-up into a standalone question.
    """
    from collections import deque
    from importlib import import_module
    from types import SimpleNamespace

    from mock_kit import MockEmbeddings, sample_documents

    vs_module = import_module("04_vector_store")
    store = vs_module.MockVectorStore(sample_documents(), MockEmbeddings(dim=64))
    retriever = store.as_retriever(search_kwargs={"k": 2})

    history: deque = deque(maxlen=5)  # window of last 5 (question, answer) pairs

    def condense(question: str) -> str:
        # Crude coreference: if the follow-up leans on a pronoun and we have
        # history, append the last topic so retrieval has something to match.
        if history and any(p in question.lower() for p in (" it", "it ", "that", "this")):
            last_q = history[-1][0]
            rewritten = f"{question} (regarding: {last_q})"
            logger.info("   [condensed follow-up] %r -> %r", question, rewritten)
            return rewritten
        return question

    def invoke(payload: dict) -> dict:
        question = payload["question"]
        standalone = condense(question)
        docs = retriever.invoke(standalone)
        # Stub 'answer': echo the top retrieved chunk.
        answer = docs[0].page_content if docs else "I don't have that information."
        history.append((question, answer))
        return {"answer": answer, "source_documents": docs}

    logger.info("[MOCK] Built conversational chain (windowed memory k=5, stub LLM).")

    # Wrap the invoke closure in a tiny object exposing .invoke(...), so callers
    # use the same chain.invoke({"question": ...}) shape as the real chain.
    return SimpleNamespace(invoke=invoke)


# ---------------------------------------------------------------------------
# REAL path: the actual ConversationalRetrievalChain from the source guide
# ---------------------------------------------------------------------------
def build_conv_chain_real():
    """Build the real conversational RAG chain.

    Requires:  pip install langchain langchain-anthropic langchain-openai langchain-community chromadb
    TODO: set ANTHROPIC_API_KEY and OPENAI_API_KEY in your .env.
    """
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferWindowMemory
    from langchain_anthropic import ChatAnthropic
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(
        collection_name="product_docs",
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = ChatAnthropic(model="claude-sonnet-4-6")

    # Bounded sliding-window memory — keeps token cost predictable.
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=5,  # keep last 5 exchanges
    )

    conv_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False,
    )
    logger.info("Built real ConversationalRetrievalChain (windowed memory k=5).")
    return conv_chain


def build_conv_chain():
    return build_conv_chain_mock() if USE_MOCK else build_conv_chain_real()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    conv_chain = build_conv_chain()

    # Turn 1 — establishes the topic ("the return policy").
    r1 = conv_chain.invoke({"question": "What is the return policy?"})
    logger.info("Turn 1 A: %s", r1["answer"])
    logger.info("Turn 1 sources: %s", [d.metadata.get("source") for d in r1["source_documents"]])

    # Turn 2 — "it" must resolve to "the return" via the conversation history.
    r2 = conv_chain.invoke({"question": "How long does it take to process?"})
    logger.info("Turn 2 A: %s", r2["answer"])
    logger.info("Turn 2 sources: %s", [d.metadata.get("source") for d in r2["source_documents"]])

    logger.info("Conversational RAG demo complete.")
