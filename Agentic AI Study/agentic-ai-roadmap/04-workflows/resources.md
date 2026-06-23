# Phase 4 — Workflows · Resources

Verified, current links (checked June 2026). A **workflow** orchestrates LLM calls through
*predefined* code paths — the opposite of letting an agent decide every step.

## Official docs
- [Anthropic — Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) — the canonical source for prompt chaining, routing, and parallelization. This entire phase maps directly onto it; read it first.
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — how to express routers and fan-out/fan-in as an explicit graph.
- [LangChain docs](https://docs.langchain.com/) — LCEL (the `|` pipe) reference, the backbone of prompt chaining.
- [Python `asyncio` docs](https://docs.python.org/3/library/asyncio.html) — `gather` and `to_thread`; your `ExecutorService.invokeAll` analogue for parallelization.

## GitHub
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) — runnable example graphs for conditional branching and parallel execution.
