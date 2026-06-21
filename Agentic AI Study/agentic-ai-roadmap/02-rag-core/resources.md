# Phase 2 — RAG Core: Resources

A short, curated list. Read the docs you'll actually use this week; bookmark the
GitHub repos for when you hit an edge case and need to read the source.

---

## Official Docs

- **LangChain docs (home)** — https://docs.langchain.com/
  The starting point for chains, LCEL, loaders, splitters, retrievers, and
  memory. This is the "Spring reference guide" for the whole framework — when in
  doubt, start here.

- **LangChain Python API reference** — https://python.langchain.com/api_reference/
  Exact signatures for `RecursiveCharacterTextSplitter`, `Chroma`, `FAISS`,
  `OpenAIEmbeddings`, `RunnablePassthrough`, etc. Use it like Javadoc: when a
  keyword argument like `search_kwargs` or `fetch_k` is unclear, look it up here.

- **ChromaDB getting started (official)** — https://docs.trychroma.com/docs/overview/getting-started
  Hands-on intro to the vector store this phase uses for dev. Covers
  collections, persistence, and querying — directly backs section 2.4 and the
  persist/reload exercise.

---

## GitHub

- **LangChain GitHub** — https://github.com/langchain-ai/langchain
  The source. When behaviour surprises you (e.g. how LCEL pipes types, or how a
  loader populates metadata), reading the implementation is faster than guessing.

- **ChromaDB GitHub** — https://github.com/chroma-core/chroma
  Issues + source for the Chroma store. The place to confirm persistence
  semantics and check known gotchas around `persist_directory`.

- **FAISS GitHub (facebookresearch)** — https://github.com/facebookresearch/faiss
  The underlying similarity-search library behind the FAISS store. Skim the
  README to understand what "approximate nearest neighbour, in-memory" buys you
  versus a persistent store like Chroma.
