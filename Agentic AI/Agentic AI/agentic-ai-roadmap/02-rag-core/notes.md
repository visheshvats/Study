# Phase 02: RAG Core (Retrieval-Augmented Generation)

## 🎯 Why This Matters
LLMs have a knowledge cutoff and lack access to your company's private data. If you ask an LLM, "What is our company's refund policy?", it will either hallucinate or say it doesn't know. RAG solves this by injecting your private data into the LLM's prompt right before it generates an answer. For Java developers, building a RAG system is essentially building an ETL pipeline (Extract, Transform, Load) combined with a semantic search engine.

---

## 🏗️ 2.1 Document Loading (Extract)

Before you can search text, you must extract it from PDFs, CSVs, or web pages into a standard format. In LangChain, this format is the `Document` object, which contains `page_content` (the text) and `metadata` (source, page number, etc.).

### 💡 Java Analogy
*   **Loaders** ➡️ File Parsers (like Apache POI for docs, or OpenCSV).
*   **Document Object** ➡️ A POJO containing `String text` and `Map<String, Object> metadata`.

### 👨‍💻 Code Example: Loading a PDF
```python
from langchain_community.document_loaders import PyPDFLoader

# Extract text from a local PDF
loader = PyPDFLoader("./docs/user_manual.pdf")
docs = loader.load()

# The result is a list of Document objects (usually one per page)
print(docs[0].page_content[:100]) # First 100 characters
print(docs[0].metadata)           # e.g., {'source': './docs/user_manual.pdf', 'page': 0}
```

---

## ✂️ 2.2 Text Splitting (Transform)

You cannot send an entire 500-page PDF to an LLM (it exceeds the Context Window). You must chop the documents into smaller "chunks". The golden rule is to use "overlap" so that a sentence isn't abruptly cut in half, losing its meaning.

### 💡 Java Analogy
*   **Text Splitter** ➡️ String Tokenizers or Regex matchers splitting on `\n\n`.

### 👨‍💻 Code Example: Chunking with Overlap
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Prioritizes splitting by paragraph (\n\n), then sentence, then word.
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,   # Approx 750 words
    chunk_overlap=200  # 200 characters overlap between chunks
)

# Splitting the documents loaded in the previous step
chunks = splitter.split_documents(docs)
```
### 🚨 Common Java-Dev Mistakes
> [!WARNING]
> **Ignoring Chunk Overlap**: If Chunk 1 ends with "The password is" and Chunk 2 begins with "12345", searching for "password" might return Chunk 1, but the LLM won't know the password because it's in Chunk 2. Always use 10-20% chunk overlap!

---

## 🧮 2.3 Embeddings & Vector Stores (Load & Retrieve)

To search these chunks based on *meaning* rather than exact keyword matches, we convert text into a high-dimensional vector of numbers (an embedding). We store these vectors in a Vector Database (like Chroma or FAISS). When a user asks a question, we embed the question and find the vectors with the smallest "Cosine Distance".

### 💡 Java Analogy
*   **Embeddings** ➡️ Hash codes, but instead of detecting exact equality, they detect semantic similarity.
*   **Vector DB (Chroma)** ➡️ Elasticsearch or Solr, but optimized for vector math instead of BM25 text search.

### 👨‍💻 Code Example: Vectorizing and Saving
```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Initialize the embedding model (converts text to vector)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 2. Store the chunks in a local Chroma DB
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# 3. Retrieve chunks semantically similar to a query
retriever = vectorstore.as_retriever(search_kwargs={"k": 4}) # Get top 4 chunks
results = retriever.get_relevant_documents("How do I reset my password?")
```

---

## 🤖 2.4 RAG Chains (LCEL)

Once we retrieve the relevant chunks, we insert them into a Prompt Template and send it to the LLM. LangChain Expression Language (LCEL) uses the pipe `|` operator to chain these steps together beautifully.

### 💡 Java Analogy
*   **LCEL `|`** ➡️ Java Streams `.map().filter().collect()` or CompletableFuture `.thenApply()`. It chains runnables.

### 👨‍💻 Code Example: Basic RAG Chain
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template("""
Answer based ONLY on the context: {context}
Question: {question}
""")

# The LCEL Chain:
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()} 
    | prompt 
    | llm 
    | StrOutputParser() # Extracts string from LLM output object
)

# Execute the pipeline
print(rag_chain.invoke("How do I reset my password?"))
```

---

## 📚 Key Terms Glossary
*   **RAG (Retrieval-Augmented Generation)**: The process of fetching relevant data from a database and adding it to the LLM prompt before generating an answer.
*   **Embeddings**: An array of floating-point numbers representing the semantic meaning of text.
*   **Vector Database**: A database optimized to store and query embeddings using nearest-neighbor algorithms (like Cosine Similarity).
*   **Chunking / Splitting**: Breaking large documents into smaller pieces so they fit in the LLM's context window.
*   **LCEL (LangChain Expression Language)**: A declarative way to easily compose chains in LangChain using the pipe `|` syntax.
