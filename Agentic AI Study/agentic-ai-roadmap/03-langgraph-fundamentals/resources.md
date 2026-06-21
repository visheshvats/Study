# Phase 3 - Resources

A short, curated list. Every link is verified; start with the Official Docs, then read the Anthropic article for the *why*, and keep the GitHub repos open as you code.

## Official Docs

- **LangGraph overview (official)** - https://docs.langchain.com/oss/python/langgraph/overview
  The canonical introduction to StateGraph, nodes, edges, and state. Read this first to anchor every term in `notes.md` to the official vocabulary.

- **LangChain docs (home)** - https://docs.langchain.com/
  The umbrella docs for LangChain + LangGraph. Use it to look up message types (`HumanMessage`, `AIMessage`, `ToolMessage`), the `@tool` decorator, and `ChatAnthropic` configuration.

## Article

- **Anthropic, "Building Effective AI Agents"** - https://www.anthropic.com/research/building-effective-agents
  The conceptual backbone for the whole roadmap: when to use a simple workflow vs. an agent, and why explicit, inspectable control flow (exactly what a state graph gives you) beats an over-clever black box.

## GitHub

- **LangGraph (source + examples)** - https://github.com/langchain-ai/langgraph
  The library itself. Skim `examples/` and the README for `create_react_agent`, checkpointers, and conditional-edge patterns straight from the maintainers.

- **LangGraph 101 (tutorials)** - https://github.com/langchain-ai/langgraph-101
  Beginner-oriented, runnable notebooks. The fastest way to see the 3.1-3.4 concepts end-to-end before you write your own from scratch.
