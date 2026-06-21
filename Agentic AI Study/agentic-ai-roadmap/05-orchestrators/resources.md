# Phase 5 — Resources

A short, curated list. Read the first one before anything else — it is the canonical source for the orchestrator–workers pattern you are building in this phase.

---

## Official Docs

- **LangGraph — Overview** — https://docs.langchain.com/oss/python/langgraph/overview
  The official entry point for building multi-agent and orchestrated systems as graphs; this is where your hand-rolled `plan/execute/synthesize` loop graduates into a production framework with state, checkpoints, and proper graph execution.

- **LangChain Docs — Home** — https://docs.langchain.com/
  The umbrella docs; your reference for `ChatAnthropic`, message types (`SystemMessage`/`HumanMessage`), and the model interface every `WorkerAgent` and `OrchestratorAgent` calls.

## Articles

- **Anthropic — Building Effective AI Agents** — https://www.anthropic.com/research/building-effective-agents
  The foundational article. Read the **orchestrator-workers** section directly — it names and justifies the exact pattern in this phase, and (just as importantly) argues for starting simple and *not* reaching for multi-agent until simpler approaches fall short.

- **Anthropic — Writing Tools for AI Agents** — https://www.anthropic.com/engineering/writing-tools-for-agents
  Once your workers need to *act* (search, fetch, query) rather than just reason, this is how to design the tools they call — directly relevant when you grow a Researcher worker that hits a real data source.

## GitHub

- **langchain-ai/langgraph** — https://github.com/langchain-ai/langgraph
  Source, examples, and multi-agent reference implementations; mine the `examples/` for orchestrator-worker and supervisor patterns to compare against your own `OrchestratorAgent`.
