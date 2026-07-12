import math
from langchain_core.documents import Document

# --- Mock Implementations for Runnable Examples ---
class MockEmbeddings:
    def embed_query(self, text: str) -> list[float]:
        # Returns a dummy vector based on keywords
        text = text.lower()
        v1 = 1.0 if "python" in text or "django" in text else 0.1
        v2 = 1.0 if "framework" in text else 0.1
        v3 = 1.0 if "snake" in text else 0.1
        return [v1, v2, v3]
        
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(t) for t in texts]

class MockVectorStore:
    def __init__(self):
        self.docs = []
        
    def add_documents(self, docs: list[Document]):
        self.docs.extend(docs)
        
    def as_retriever(self, search_kwargs: dict = None):
        return MockRetriever(self.docs, search_kwargs or {})

class MockRetriever:
    def __init__(self, docs: list[Document], kwargs: dict):
        self.docs = docs
        self.kwargs = kwargs
        
    def get_relevant_documents(self, query: str) -> list[Document]:
        # Mocking retrieval logic: just return docs containing a word from query
        # or apply metadata filter if provided.
        k = self.kwargs.get("k", 4)
        filter_dict = self.kwargs.get("filter", {})
        
        results = []
        for doc in self.docs:
            # Check filter
            if filter_dict:
                match = all(doc.metadata.get(key) == val for key, val in filter_dict.items())
                if not match: continue
                
            results.append(doc)
            if len(results) == k: break
        return results
# ------------------------------------------------

def demonstrate_cosine_similarity():
    print("--- 1. Embeddings & Cosine Similarity ---")
    embeddings = MockEmbeddings()
    
    texts = [
        "Python is a programming language",   # Tech
        "Django is a Python web framework",   # Tech
        "A snake is a reptile with no legs",  # Biology
    ]
    
    vecs = embeddings.embed_documents(texts)
    print(f"Vectors: {vecs}")
    
    def cosine_sim(a: list[float], b: list[float]) -> float:
        dot_product = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(y * y for y in b))
        return dot_product / (mag_a * mag_b)
        
    print(f"Sim(Python vs Django): {cosine_sim(vecs[0], vecs[1]):.3f} (HIGH)")
    print(f"Sim(Python vs Snake):  {cosine_sim(vecs[0], vecs[2]):.3f} (LOW)\n")

def demonstrate_vector_store():
    print("--- 2. Vector Store & Retrievers ---")
    # Real: from langchain_community.vectorstores import Chroma
    # Real: vectorstore = Chroma.from_documents(...)
    
    docs = [
        Document(page_content="Policy: 30 day returns", metadata={"section": "returns", "dept": "HR"}),
        Document(page_content="Policy: Casual Fridays", metadata={"section": "culture", "dept": "HR"}),
        Document(page_content="Server maintenance at 2AM", metadata={"section": "IT", "dept": "IT"})
    ]
    
    vectorstore = MockVectorStore()
    vectorstore.add_documents(docs)
    
    # Basic Retrieval
    basic_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    res1 = basic_retriever.get_relevant_documents("policy")
    print(f"Basic Retrieval returned {len(res1)} docs.")
    
    # Metadata Filtered Retrieval
    filtered_retriever = vectorstore.as_retriever(
        search_kwargs={"k": 2, "filter": {"dept": "IT"}}
    )
    res2 = filtered_retriever.get_relevant_documents("maintenance")
    print(f"Filtered (dept=IT) Retrieval returned:")
    for d in res2:
        print(f"- {d.page_content} (Meta: {d.metadata})")

if __name__ == "__main__":
    demonstrate_cosine_similarity()
    demonstrate_vector_store()
