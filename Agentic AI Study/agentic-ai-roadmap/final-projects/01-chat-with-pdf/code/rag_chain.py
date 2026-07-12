"""
Retrieval-augmented answering. Phase 2 section 2.5.
MOCK uses the grounded MockLLM; REAL builds an LCEL chain over ChatAnthropic.
"""
from __future__ import annotations

import logging
from typing import Dict, List

from langchain_core.documents import Document

import mock_kit

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("rag_chain")

USE_MOCK = True

GROUNDED_PROMPT = (
    "Answer the question based ONLY on the context below. "
    'If the answer is not in the context, say "I don\'t have that information." '
    "Do NOT make up information.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
)


def format_docs(docs: List[Document]) -> str:
    return "\n\n---\n\n".join(
        f"[source: {d.metadata.get('source', 'unknown')}] {d.page_content}" for d in docs
    )


def answer(question: str, store, k: int = 3) -> Dict[str, object]:
    """Retrieve top-k, build a grounded prompt, and answer. Returns answer + sources."""
    docs = store.as_retriever(k=k).invoke(question)
    context = format_docs(docs)
    sources = sorted({d.metadata.get("source", "unknown") for d in docs})

    if USE_MOCK:
        text = mock_kit.MockLLM().answer(question, context)
    else:
        # REAL LCEL chain:
        #   from langchain_anthropic import ChatAnthropic
        #   from langchain_core.prompts import ChatPromptTemplate
        #   from langchain_core.output_parsers import StrOutputParser
        #   prompt = ChatPromptTemplate.from_template(GROUNDED_PROMPT)
        #   chain = prompt | ChatAnthropic(model="claude-sonnet-4-6") | StrOutputParser()
        #   text = chain.invoke({"context": context, "question": question})
        from langchain_anthropic import ChatAnthropic  # type: ignore
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate

        chain = ChatPromptTemplate.from_template(GROUNDED_PROMPT) | ChatAnthropic(
            model="claude-sonnet-4-6"
        ) | StrOutputParser()
        text = chain.invoke({"context": context, "question": question})

    grounded = text.strip() != mock_kit.MockLLM.FALLBACK
    return {"answer": text, "sources": sources if grounded else [], "grounded": grounded}


if __name__ == "__main__":
    import ingest

    store, _ = ingest.ingest()
    for q in ["What is the refund window?", "Who won the 2024 World Series?"]:
        res = answer(q, store)
        print(f"\nQ: {q}\nA: {res['answer']}\n   sources={res['sources']}")
