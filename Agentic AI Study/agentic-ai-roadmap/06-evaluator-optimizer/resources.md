# Phase 6 — Resources

Curated, verified links for the evaluator-optimizer pattern, LLM-as-judge, structured output, and observability. Read the Anthropic article first — it names the pattern you're building.

## Official Docs

- **LangSmith — Observability & Evaluation** — https://docs.langchain.com/langsmith/observability
  The production home for evaluation: run LLM-as-judge evaluators at scale, track scores over time, and see *why* an output failed. This is where your `EvalResult` graduates from a print statement to a dashboard.

- **Pydantic (latest)** — https://docs.pydantic.dev/latest/
  The validation engine behind `EvalResult` and `PydanticOutputParser`. The `Field` constraints (`ge`, `le`) and `Literal` types you use to make the judge's output a typed, validated contract live here — your bean-validation reference.

- **LangChain docs (home)** — https://docs.langchain.com/
  Entry point for `PydanticOutputParser`, `HumanMessage`, `ChatAnthropic`, and the `.invoke()` API used throughout the Phase 6 code. Start here when a class or import is unfamiliar.

## Article

- **Anthropic — Building Effective AI Agents** — https://www.anthropic.com/research/building-effective-agents
  The source-of-truth write-up of the **evaluator-optimizer** pattern (generate → evaluate → feedback → retry). Read this to understand *when* the pattern is worth its doubled LLM cost and how it compares to plain prompting.

## GitHub

- **LangGraph** — https://github.com/langchain-ai/langgraph
  When your retry loop needs real state, branching, and persistence (instead of a plain `for` loop), the evaluator-optimizer becomes a graph: a generator node, a judge node, and a conditional edge that routes back on failure. This repo shows how.
