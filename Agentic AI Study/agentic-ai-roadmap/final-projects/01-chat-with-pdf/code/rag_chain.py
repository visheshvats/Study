"""
Retrieval-augmented generation chain (LCEL). See Phase 2 section 2.5.
"""
from __future__ import annotations


def format_docs(docs) -> str:
    """Join retrieved docs into a context string with source tags."""
    # TODO: return "\n\n---\n\n".join(f"[{d.metadata.get('source','?')}] {d.page_content}" for d in docs)
    raise NotImplementedError


def build_rag_chain(persist_dir: str = "./chroma_db", collection: str = "pdf_docs"):
    """Load the Chroma store and return an LCEL chain: question -> grounded answer."""
    # TODO: load embeddings + Chroma(collection_name=..., persist_directory=...)
    # TODO: retriever = store.as_retriever(search_kwargs={"k": 4})
    # TODO: prompt = ChatPromptTemplate.from_template(GROUNDED_PROMPT)  # "answer ONLY from context..."
    # TODO: llm = ChatAnthropic(model="claude-sonnet-4-6")
    # TODO: chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()}
    #                | prompt | llm | StrOutputParser())
    # TODO: return chain
    raise NotImplementedError


if __name__ == "__main__":
    print("Implement build_rag_chain, then: build_rag_chain().invoke('your question')")
