# Phase 02: Practice Exercises

These exercises test your ability to build robust RAG pipelines, from data ingestion to retrieval logic.

## Exercise 1: Metadata Filtering (Medium)
**Scenario**: You have a `VectorStore` loaded with documents from various departments.
**Task**: In Python, write the setup to create a Retriever from a Chroma `vectorstore` that searches for the top 3 results, but *only* returns documents where the metadata field `"department"` equals `"HR"`.
> *Hint*: Look at the `search_kwargs={"filter": ...}` parameter in `vectorstore.as_retriever()`.

## Exercise 2: Implementing Cosine Similarity (Hard)
**Scenario**: You want to understand how vector search works under the hood.
**Task**: Write a pure Python function `calculate_cosine_similarity(vec1: list[float], vec2: list[float]) -> float` that calculates the cosine similarity between two 1D arrays WITHOUT using NumPy or SciPy (use only the built-in `math` module).
> *Hint*: Cosine Similarity = (Dot Product of A and B) / (Magnitude of A * Magnitude of B).

## Exercise 3: Dynamic LCEL Chains (Medium)
**Scenario**: You are using LCEL (`|`), but you want to format the retrieved documents cleanly before they go into the prompt.
**Task**: Write a Python function `format_docs(docs: list) -> str` that takes a list of LangChain `Document` objects and returns a single string where each document's `page_content` is separated by `\n\n--- DOCUMENT ---\n\n`. Add this function to an LCEL chain.
> *Hint*: In LCEL, you can pipe a retriever directly into a regular Python function before the PromptTemplate.

## Exercise 4: MMR vs Basic Retrieval (Concept)
**Scenario**: A user searches for "Latest company updates". Your basic Top-K retriever returns 5 documents that are almost identical (e.g., 5 versions of the same memo).
**Task**: Explain in 2 sentences how switching `search_type` to `"mmr"` (Maximal Marginal Relevance) solves this problem, and write the one line of Python code to instantiate an MMR retriever fetching 5 results out of a candidate pool of 20.
> *Hint*: MMR balances relevance to the query with diversity among the results.
