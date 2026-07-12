"""
Research agent. MOCK = a deterministic tool-routing loop (runs offline, no key).
REAL = LangGraph create_react_agent over the @tool functions. Phase 3 section 3.3.
"""
from __future__ import annotations

import logging
from typing import Dict, List

import tools

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("agent")

USE_MOCK = True

# Triggers that make the agent reach for live web search in addition to internal docs.
_WEB_TRIGGERS = ("competitor", "current", "latest", "news", "market", "compare", "vs", "today")


class ResearchAgent:
    """Decides which tools to call, executes them, and returns gathered findings."""

    def run(self, question: str) -> Dict[str, object]:
        if not USE_MOCK:
            return self._run_real(question)

        used: List[str] = []
        findings: List[str] = []
        sources: List[str] = []

        # Always consult the internal knowledge base.
        doc_result = tools.search_docs(question)
        used.append("search_docs")
        findings.append(f"Internal docs: {doc_result}")
        sources.append("internal_docs")

        # Reach for the web only when the question implies current/comparative info.
        if any(t in question.lower() for t in _WEB_TRIGGERS):
            web_result = tools.search_web(question)
            used.append("search_web")
            findings.append(f"Web: {web_result}")
            sources.append("web_search")

        logger.info("agent used tools: %s", used)
        return {"findings": "\n".join(findings), "tools_used": used, "sources": sources}

    def _run_real(self, question: str) -> Dict[str, object]:
        # REAL path:
        #   from langgraph.prebuilt import create_react_agent
        #   from langchain_anthropic import ChatAnthropic
        #   from langchain_core.messages import HumanMessage
        #   agent = create_react_agent(ChatAnthropic(model="claude-sonnet-4-6"), tools.as_tools())
        #   out = agent.invoke({"messages": [HumanMessage(question)]})
        #   return {"findings": out["messages"][-1].content, "tools_used": [...], "sources": [...]}
        from langchain_anthropic import ChatAnthropic  # type: ignore
        from langchain_core.messages import HumanMessage
        from langgraph.prebuilt import create_react_agent

        agent = create_react_agent(ChatAnthropic(model="claude-sonnet-4-6"), tools.as_tools())
        out = agent.invoke({"messages": [HumanMessage(question)]})
        return {"findings": out["messages"][-1].content, "tools_used": ["react_agent"], "sources": ["agent"]}


if __name__ == "__main__":
    r = ResearchAgent().run("How does our Pro plan price compare to competitors?")
    print(r["tools_used"], "\n", r["findings"])
