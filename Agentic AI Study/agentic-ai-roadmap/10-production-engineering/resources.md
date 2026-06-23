# Phase 10 — Resources

A short, curated set. Read the official docs first; they're the source of truth for the behaviours this phase hardens against.

## Official Docs

- **Python `asyncio`** — https://docs.python.org/3/library/asyncio.html
  The foundation under the rate limiter and retry decorator. Read the `asyncio.sleep` and `asyncio.Lock` sections to understand why backoff must be `await`ed and never `time.sleep`d on the event loop.

- **FastAPI tutorial** — https://fastapi.tiangolo.com/tutorial/
  How the `/chat/safe` endpoint, request models, and `HTTPException` work — and the `TestClient` that powers the offline smoke test in `03_guardrails.py`.

- **Pydantic** — https://docs.pydantic.dev/latest/
  The validation layer behind `ChatRequest`. `Field(min_length=..., max_length=...)` is your Bean-Validation-style first line of input defence, complementing the regex guardrail.

- **Anthropic API docs** — https://docs.claude.com/
  The authority on real rate limits and error codes. Use this to decide which SDK exceptions map to `TransientLLMError` (429/5xx) versus `FatalLLMError` (4xx) when you flip `USE_MOCK=False`.

- **LangChain docs (home)** — https://docs.langchain.com/
  Where the real `embed_query` lives. When you swap the mock embedder for a production model, this is the integration surface the cache wraps.

## Article

*(none beyond the verified bank for this phase — the official docs above cover the material directly.)*

## GitHub

*(none beyond the verified bank for this phase.)*
