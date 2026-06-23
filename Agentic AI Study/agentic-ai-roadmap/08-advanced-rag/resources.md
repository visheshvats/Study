# Phase 8 — Resources

Curated, verified links for Advanced RAG. Start with the LangGraph CRAG /
adaptive-RAG / self-RAG tutorials in the GitHub repo — they are the canonical
reference implementations of everything in this phase.

---

## Official Docs

- **[LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)**
  The framework behind agentic and self-correcting RAG graphs — read this to
  understand the state-machine model that adaptive/corrective loops are built on.

- **[LangChain docs (home)](https://docs.langchain.com/)**
  Home for the retriever, `@tool`, and chat-model primitives every script in
  `code/` imports; your reference when wiring real retrievers and LLMs.

- **[ChromaDB getting started](https://docs.trychroma.com/docs/overview/getting-started)**
  The vector store you'll plug into `_build_real_retriever()` to replace the
  in-memory mock with a real index for grading.

- **[Tavily quickstart](https://docs.tavily.com/documentation/quickstart)**
  An LLM-optimized search API — the real implementation behind the CRAG
  web-search fallback and the agentic `search_web` tool (1,000 free credits/mo).

---

## Article

- **[Anthropic — Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)**
  The conceptual backbone for *when* to add agentic routing vs. a fixed
  pipeline — directly informs the adaptive-gate and agentic-RAG decisions.

---

## GitHub

- **[LangGraph (CRAG / adaptive-RAG / self-RAG tutorials)](https://github.com/langchain-ai/langgraph)**
  The canonical, runnable reference implementations of all three Phase 8
  techniques — clone it and read the RAG tutorials alongside the `code/` files.
