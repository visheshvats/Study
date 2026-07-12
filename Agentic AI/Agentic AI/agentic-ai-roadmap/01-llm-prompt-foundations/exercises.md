# Phase 01: Practice Exercises

These exercises test your ability to interact with LLMs, construct effective prompts, and implement tool-calling logic.

## Exercise 1: Token Counting & Context Windows (Easy)
**Scenario**: You are passing a large log file to the LLM. 
**Task**: Write a Python function `estimate_tokens(text: str) -> int` that provides a rough estimation of token count (assume 1 word ≈ 1.3 tokens). If the estimate exceeds 8000 tokens, throw a `ValueError`.
> *Hint*: Use `len(text.split())` and multiply by a factor to estimate.

## Exercise 2: Few-Shot JSON Extraction (Medium)
**Scenario**: You need to extract a user's intent and entities from a raw chat message.
**Task**: Write a System Prompt (just the string) that uses Few-Shot examples to teach the LLM to output a JSON object containing `{"intent": "...", "entities": [...]}`. 
> *Hint*: Provide at least two examples inside the prompt string clearly marking Input and Output.

## Exercise 3: Manual History Management (Medium)
**Scenario**: You are building a CLI chatbot.
**Task**: Write a Python loop that takes user input `input("> ")`, appends it to a `history` list as a `{"role": "user"}` dict, mocks an LLM response appending a `{"role": "assistant"}` dict, and prints the history length. Limit the history to the last 4 messages (sliding window).
> *Hint*: Use Python list slicing: `history = history[-4:]`.

## Exercise 4: Defensive JSON Parsing (Hard)
**Scenario**: The LLM occasionally surrounds its JSON output in markdown blocks (e.g., ` ```json { ... } ``` `) despite instructions not to.
**Task**: Write a robust parser `parse_llm_json(raw_text: str) -> dict` that strips out markdown code blocks and parses the JSON. If parsing fails, it should return a fallback dictionary `{"error": "invalid format"}` rather than crashing.
> *Hint*: Use `re.sub(r'```(?:json)?|```', '', raw_text).strip()`.

## Exercise 5: Tool Schema Definition (Hard)
**Scenario**: You want the LLM to be able to query a PostgreSQL database to find a user's current subscription tier.
**Task**: Write the JSON Schema definition for a tool named `get_subscription_tier`. It should require a `user_email` (string, must be a valid email format pattern) and an optional `include_past_billing` (boolean).
> *Hint*: Look up the JSON Schema specification for `properties` and `required` fields.
