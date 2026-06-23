# Phase 11 — Scaling & Architecture · Resources

Verified, current links (checked June 2026). This phase = pushing state out of the process so the app
tier scales horizontally.

## Official docs
- [redis-py documentation](https://redis.readthedocs.io/) — the Python Redis client used by `SessionStore`; your Spring Session + Redis analogue.
- [Celery documentation (stable)](https://docs.celeryq.dev/en/stable/) — distributed task queue for long-running agent jobs; `@Async` + a broker, done right.
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — persistence and checkpointers (`MemorySaver` → `PostgresSaver`) for durable graph state.
- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) — the stateless orchestrator service tier (background tasks, dependencies).

## GitHub
- [redis/redis-py](https://github.com/redis/redis-py) — source and examples for the Redis client.
- [celery/celery](https://github.com/celery/celery) — Celery source, with worker and broker configuration examples.
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) — checkpointer implementations (Postgres/Redis savers) and persistence examples.
