"""
Retrieval tools the research agent can call. See Phase 1 section 1.4 and Phase 3 section 3.3.
"""
from __future__ import annotations

# TODO: from langchain_core.tools import tool


# @tool
def search_docs(query: str) -> str:
    """Search the internal document store and return the top matching passages."""
    # TODO: query a Chroma retriever (Phase 2) and join the top-k page_content.
    raise NotImplementedError


# @tool
def search_web(query: str) -> str:
    """Search the web for current information. (Mock now; integrate Tavily later.)"""
    # TODO (mock): return f"[web:{query}] placeholder result"
    # TODO (real): call the Tavily API with TAVILY_API_KEY.
    raise NotImplementedError


if __name__ == "__main__":
    print("Implement search_docs/search_web, then register them on the agent.")
