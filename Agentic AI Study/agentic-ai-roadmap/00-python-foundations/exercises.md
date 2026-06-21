# Phase 0 — Exercises

Practice problems ordered easy to hard. Each has a single hint and no solution.
They exercise Phase-0 concepts without repeating the phase checklist verbatim.
Write your answers in the `code/` folder (e.g. `exercise_1.py`) and run them.

---

### 1. Token-count comprehension (easy)
Given `messages = [{"role": "user", "content": "..."}, ...]`, build a single dict comprehension that maps each role to the total word count across all its messages. Print the result sorted by count descending.

> Hint: combine a comprehension over distinct roles with a `sum(...)` of `len(m["content"].split())`; `sorted(..., key=..., reverse=True)` for the ordering.

---

### 2. Type-hinted retry helper (easy–medium)
Write a fully type-hinted function `with_default(value: T | None, default: T) -> T` that returns `value` if it is not `None`, else `default`. Make it generic so the IDE infers the return type. Demonstrate it on a `str | None` and an `int | None`.

> Hint: import `TypeVar` from `typing`, declare `T = TypeVar("T")`, and use it in the signature — this is your `<T>` generic.

---

### 3. dataclass vs Pydantic, side by side (medium) — *Java-migration angle*
Model a `ToolCall` (fields: `name: str`, `arguments: dict`, `timeout_s: int`) twice: once as a `@dataclass` and once as a Pydantic `BaseModel` that rejects `timeout_s` outside 1–300. Feed both an invalid `timeout_s=999` and show which one catches it and which one silently accepts garbage. Note in a comment why a Spring DTO would behave like the Pydantic version.

> Hint: only the Pydantic model raises — use `Field(ge=1, le=300)` and wrap construction in `try/except ValidationError`.

---

### 4. Concurrent fan-out with a deadline (medium–hard)
Write an async `fetch_all_with_timeout(urls, deadline_s)` that simulates fetching each URL (use `asyncio.sleep` with random latency), runs them concurrently, but cancels any that exceed `deadline_s`. Return successes and report how many timed out.

> Hint: wrap `asyncio.gather(...)` in `asyncio.wait_for(..., timeout=deadline_s)`, or wrap each task with `asyncio.wait_for` individually and use `return_exceptions=True`.

---

### 5. FastAPI endpoint with richer validation (hard)
Add a `POST /embed` endpoint to a FastAPI app that accepts `{"texts": [...], "model": "..."}` where `texts` must be a non-empty list of 1–100 strings and `model` must be one of a fixed allowed set. Return a mock embedding (a fixed-length list of floats) per text. Verify with `TestClient` that a 101-item list and an unknown model both return `422`.

> Hint: use Pydantic `Field(min_length=1, max_length=100)` on the list and a `Literal[...]` / `enum` for `model`; assert on `response.status_code` in your test.

---

### 6. Async streaming aggregator (hard) — *Java-migration angle*
Write an async generator `merge_streams(*streams)` that consumes several `stream_tokens`-style async generators concurrently and yields tokens as soon as ANY stream produces one (interleaved, not sequential). Compare in a comment to how you'd merge multiple reactive `Flux` publishers in Java.

> Hint: there's no built-in `async for` over many generators at once — push each generator's `__anext__()` as a task into `asyncio.as_completed` (or a queue) and re-schedule the producer after each yield.
