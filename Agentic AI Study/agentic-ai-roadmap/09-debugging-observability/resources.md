# Phase 9 — Resources

A short, curated list. Each line says why it earns your time.

## Official Docs
- [LangSmith — Observability](https://docs.langchain.com/langsmith/observability) — The primary reference for 9.1: enabling tracing, projects, and reading traces/spans. This is your "Jaeger manual" for agents.
- [Python `logging`](https://docs.python.org/3/library/logging.html) — The real, no-mock basis for 9.3. Handlers, formatters, and levels — your Logback/SLF4J equivalent, straight from the source.
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — Background for 9.2 state inspection: how graph state and checkpoints work, which is what `get_state`/`get_state_history` read.
- [Anthropic API docs](https://docs.claude.com/) — Where `response.usage` (input/output tokens) and current per-MTok pricing live — the ground truth behind 9.4 token tracking and cost math.

## GitHub
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) — Source and examples for the graph runtime; useful when you want to see real `get_state_history` snapshots and checkpointer wiring beyond the mock in this folder.
