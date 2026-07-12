"""
Retrieval tools the agent can call. Phase 1 section 1.4 / Phase 3 section 3.3.
Plain functions run offline; `as_tools()` returns @tool-wrapped versions for the
real create_react_agent path.
"""
from __future__ import annotations

import mock_kit

_STORE = mock_kit.InMemoryVectorStore(mock_kit.MockEmbeddings(), mock_kit.INTERNAL_DOCS)


def search_docs(query: str) -> str:
    """Search the internal document store; return the top matching passages."""
    hits = _STORE.search(query, k=2)
    return " | ".join(f"[{d.metadata['source']}] {d.page_content}" for d in hits)


def search_web(query: str) -> str:
    """Search the web for current info. MOCK now; integrate Tavily for production."""
    key = "competitor" if any(w in query.lower() for w in ("competitor", "vs", "compare", "market")) else "default"
    return mock_kit.WEB_SNIPPETS[key]


def as_tools():
    """REAL path: wrap the functions as LangChain tools for create_react_agent."""
    from langchain_core.tools import tool  # type: ignore

    return [tool(search_docs), tool(search_web)]


if __name__ == "__main__":
    print("docs ->", search_docs("pricing pro plan"))
    print("web  ->", search_web("competitor pricing"))
