# Phase 01: Resources

Curated resources to master LLM APIs, prompt engineering, and tool calling.

### Official Documentation
1. **[Anthropic: Prompt Engineering Interactive Tutorial](https://docs.anthropic.com/en/docs/prompt-engineering)** - Anthropic's official guide to getting the best performance out of Claude. Essential reading for system prompts and XML tags.
2. **[Anthropic: Tool Use (Function Calling)](https://docs.anthropic.com/en/docs/tool-use)** - Detailed documentation on how to structure JSON schemas for tools and handle the multi-turn loop.
3. **[OpenAI: API Reference](https://platform.openai.com/docs/api-reference/chat)** - The standard specification that most open-source models also follow. Useful for understanding the `messages` array structure.

### Articles & Tutorials
4. **[PromptingGuide.ai](https://www.promptingguide.ai/)** - DAIR.AI's comprehensive, open-source guide to advanced prompting techniques like Chain of Thought (CoT), ReAct, and Tree of Thoughts.
5. **[Why LLMs Hallucinate and How to Prevent It](https://zapier.com/blog/ai-hallucinations/)** - A conceptual overview of why stateless token prediction sometimes invents facts, and how temperature and context grounding help.

### Tools & Repositories
6. **[Instructor](https://github.com/jxnl/instructor)** - A fantastic Python library that forces LLMs to output structured Pydantic data. It abstracts away a lot of the JSON parsing headaches. Highly recommended for Java devs used to strict DTOs!
