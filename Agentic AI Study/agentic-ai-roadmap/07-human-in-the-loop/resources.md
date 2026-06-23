# Phase 7 — Human in the Loop · Resources

Verified, current links (checked June 2026). HITL = pausing a graph for human approval, built on
checkpointing + `thread_id`.

## Official docs
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — human-in-the-loop is a first-class LangGraph capability; the interrupt/resume model lives here.
- [LangChain docs](https://docs.langchain.com/) — broader context on agents, persistence, and how HITL fits the stack.
- [Anthropic API docs](https://docs.claude.com/) — message/tool semantics for the draft-generation and revision steps.

## GitHub
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) — source and examples for `interrupt_before`, checkpointers, and `get_state`.
- [langchain-ai/langgraph-101](https://github.com/langchain-ai/langgraph-101) — hands-on notebooks; includes human-in-the-loop walkthroughs you can run and adapt.
