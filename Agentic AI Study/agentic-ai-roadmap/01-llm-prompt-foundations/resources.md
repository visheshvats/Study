# Phase 1 — Resources

A short, curated list. Read the docs first, the articles second. Everything here is current and directly relevant to this phase.

## Official Docs

- **[Anthropic API docs (home)](https://docs.claude.com/)** — Your reference for `messages.create`, the `system`/`messages`/`temperature` parameters, streaming, and the response shape. Bookmark this; you'll return to it every phase.
- **[Tool use (function calling) guide](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)** — The authoritative spec for §1.4: tool schemas, `stop_reason == "tool_use"`, and the `tool_use` / `tool_result` round-trip that powers the agentic loop.

## Articles

- **[Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)** — Anthropic's own framing of what an "agent" actually is (vs. a workflow), and when the agentic loop is worth the complexity. The conceptual north star for this whole roadmap.
- **[Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)** — Practical guidance on designing tool names, descriptions, and schemas so the model actually picks the right tool. Read it before you write your two-tool agent in Exercise 6.

## GitHub

- **[Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)** — The library every `code/` file imports. Source, changelog, and the streaming + tool-use examples that mirror what you're building here.
- **[Claude Cookbooks](https://github.com/anthropics/claude-cookbooks)** — Runnable, end-to-end notebooks for prompting patterns, structured output, and tool calling. The fastest way to see the patterns from §1.1–§1.4 working in context.
