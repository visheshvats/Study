# Phase 0 — Resources

Curated, verified links for the Python foundations a Java dev needs before
touching agents. Read the official docs for precision; use the article/video
for a guided tour; clone the repo when you want to see idiomatic source.

## Official Docs

- **Python `typing`** — https://docs.python.org/3/library/typing.html
  The reference for type hints (`Optional`, `dict[str, Any]`, `TypeVar`). This is the Python equivalent of understanding generics and method signatures, and it's what mypy/Pydantic/FastAPI build on.

- **Python `dataclasses`** — https://docs.python.org/3/library/dataclasses.html
  Defines the `@dataclass` decorator and `field(default_factory=...)`. Read this to internalize the mutable-default rule before it bites you; it's your `record` / Lombok `@Data`.

- **Python `asyncio`** — https://docs.python.org/3/library/asyncio.html
  The authoritative source on coroutines, the event loop, `gather`, and async generators. Pay attention to "don't block the loop" — it's the single most important rule for a Java dev used to thread pools.

- **Pydantic** — https://docs.pydantic.dev/latest/
  Validated models used everywhere in LangChain/FastAPI. Treat `BaseModel` + `Field` as Bean Validation for Python; the "Models" and "Fields" pages map directly to what you'd do with `@Valid`/`@Min`/`@Max`.

- **FastAPI tutorial (official)** — https://fastapi.tiangolo.com/tutorial/
  Step-by-step build of a typed, validated REST API. The path/query/body and response-model sections are a near one-to-one mapping to Spring's `@RestController`, `@RequestBody`, and DTO patterns.

## Article / Video

- **Real Python — Get started with FastAPI** — https://realpython.com/get-started-with-fastapi/
  A guided, narrative walkthrough that's gentler than the official tutorial. Good for a Java dev who wants the "why" and the Spring parallels spelled out before diving into the reference docs.

## GitHub repo

- **FastAPI source** — https://github.com/fastapi/fastapi
  Browse the source and especially the `examples`/tests to see idiomatic async + Pydantic usage in a real, production-grade codebase — the kind of code review you'd do when adopting a new framework at work.
