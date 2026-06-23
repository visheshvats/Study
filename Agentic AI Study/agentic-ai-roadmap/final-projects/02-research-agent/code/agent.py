"""
ReAct research agent. See Phase 3 section 3.3 (create_react_agent).
"""
from __future__ import annotations


def build_agent():
    """Return a ReAct agent that can call the retrieval tools."""
    # TODO: from langgraph.prebuilt import create_react_agent
    # TODO: from langchain_anthropic import ChatAnthropic
    # TODO: import tools
    # TODO: llm = ChatAnthropic(model="claude-sonnet-4-6")
    # TODO: return create_react_agent(llm, tools=[tools.search_docs, tools.search_web])
    raise NotImplementedError


if __name__ == "__main__":
    print("Implement build_agent, then: build_agent().invoke({'messages': [...]})")
