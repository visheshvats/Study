from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

# --- Mock Classes for LCEL demonstration ---
class MockLLM:
    def invoke(self, prompt: str) -> str:
        # A real LLM takes the formatted prompt string and generates an answer
        if "30 day" in prompt.lower():
            return "Based on the context, the return policy is 30 days."
        return "I cannot answer based on the provided context."

class MockRetriever:
    def invoke(self, query: str) -> list[Document]:
        print(f"\n[Retriever] Searching vector DB for: '{query}'")
        return [
            Document(page_content="The return policy is 30 days.", metadata={"source": "policy.pdf"})
        ]

class MockStrOutputParser:
    """Simulates extracting the string content from an AIMessage object."""
    def invoke(self, text: str) -> str:
        return text.strip()
# -------------------------------------------

def demonstrate_lcel_rag():
    print("--- Basic RAG Chain using LCEL (LangChain Expression Language) ---")
    
    retriever = MockRetriever()
    llm = MockLLM()
    
    prompt = ChatPromptTemplate.from_template("""
    Answer the question based ONLY on the context below.
    If the answer is not in the context, say "I don't have that information."

    Context:
    {context}

    Question: {question}

    Answer:""")
    
    def format_docs(docs: list[Document]) -> str:
        """Formats the retrieved Document objects into a single string for the prompt."""
        formatted = "\n\n".join(f"[Source: {d.metadata.get('source', 'unknown')}]\n{d.page_content}" for d in docs)
        print(f"[Formatter] Formatted context:\n{formatted}")
        return formatted

    # LCEL pipeline (Like Java Streams: pipeline = source | map | filter | collect)
    # 1. Take a dict {"question": "..."}
    # 2. Extract "question" and pass it to retriever | format_docs to build the "context" key
    # 3. RunnablePassthrough() keeps the original "question" key
    # 4. Pass the dict {"context": "...", "question": "..."} to the prompt template
    # 5. Pass formatted prompt to LLM
    # 6. Parse LLM output to string
    
    rag_chain = (
        {
            "context": retriever | format_docs, 
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | MockStrOutputParser()
    )

    query = "What is the return policy?"
    
    # In LCEL, .invoke() triggers the pipeline execution
    print(f"\n[User] Asks: {query}")
    answer = rag_chain.invoke(query)
    print(f"\n[LLM Answer] {answer}")

if __name__ == "__main__":
    demonstrate_lcel_rag()
