# Phase 00: Practice Exercises

These exercises test your Python foundations, focusing on patterns frequently used in Agentic AI development. 

## Exercise 1: Safe JSON Parsing (Easy)
**Scenario**: You are receiving JSON payloads from an unreliable LLM output.
**Task**: Write a function `extract_metadata(payload: str) -> dict` that takes a JSON string. If the string is valid JSON, return the parsed dictionary. If it's invalid, catch the specific exception and return an empty dictionary `{}`.
> *Hint*: Use `json.loads()` and catch `json.JSONDecodeError`.

## Exercise 2: List Comprehensions & Filtering (Medium)
**Scenario**: You have a list of chat message dictionaries, some of which are empty or have a `"role"` of `"system"`. 
**Task**: Write a single-line list comprehension that extracts only the `"content"` of messages where the `"role"` is `"user"`.
> *Hint*: `[msg["content"] for msg in ... if ...]`

## Exercise 3: Async Batch Processing (Medium)
**Scenario**: You need to fetch embeddings for 3 different documents simultaneously.
**Task**: Write an `async` function `fetch_all_embeddings(docs: list[str]) -> list[str]` that calls a mock async function `async def embed_doc(doc: str)` concurrently for all documents, and returns the list of results.
> *Hint*: Look up `asyncio.gather(*tasks)`.

## Exercise 4: Pydantic Validation (Hard)
**Scenario**: You are building the data model for a tool call.
**Task**: Create a Pydantic `BaseModel` called `SearchToolInput` that requires:
1. `query` (a string, minimum length 3).
2. `max_results` (an integer, defaulting to 5, must be between 1 and 20).
3. `filters` (an optional dictionary mapping strings to strings).
> *Hint*: Use `pydantic.Field(default=..., ge=..., le=...)` for validation constraints.

## Exercise 5: The Mutable Default Trap (Hard)
**Scenario**: A junior developer wrote a class to track conversation history:
```python
class ChatSession:
    def __init__(self, history=[]):
        self.history = history
    def add_message(self, msg):
        self.history.append(msg)
```
**Task**: Explain why this is dangerous in a web server environment, and rewrite the `__init__` method correctly using type hints.
> *Hint*: Default arguments are evaluated at definition time. Use `None` as the default instead.
