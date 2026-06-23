# Phase 11 — Scaling & Architecture

> **Duration:** Ongoing
> **Goal:** Design production-grade, horizontally-scalable agent systems.

---

## Why this matters

This is your home turf. Everything you learned scaling Spring Boot services applies almost
one-to-one to agent systems — the vocabulary barely changes. A stateless API tier behind a load
balancer, session state in Redis, durable state in Postgres, long jobs pushed to async workers, and
metrics/traces flowing to an observability stack: you've built this shape before.

The one habit you must unlearn is the demo habit of keeping state *in the process*. A single Python
script holding conversation history in a dict works on your laptop and falls apart the moment you run
two replicas behind a load balancer — request 1 lands on pod A, request 2 lands on pod B, and the
agent has amnesia. Scaling an agent system is mostly the discipline of pushing every piece of state
out of the process and into a shared store, so any worker can serve any request. Once you do that,
horizontal scaling is just "add more pods."

This phase walks the reference architecture top to bottom, then implements the three load-bearing
pieces: Redis session state, durable LangGraph checkpoints in Postgres, and a Celery background-task
queue for long-running agent runs.

---

## The enterprise architecture, layer by layer

The full diagram is in [`diagrams.md`](./diagrams.md). Read it as the same n-tier layout you'd draw
for any Spring microservice deployment:

| Layer | Components | Java/Spring equivalent |
|-------|------------|------------------------|
| **Client** | Web, mobile, 3rd-party API clients | Same — any HTTP consumer. |
| **Gateway** | Auth/JWT, rate limiting, SSL termination | Spring Cloud Gateway / an API gateway (Kong, APIGW). |
| **Application** | Orchestrator service (FastAPI) + N agent workers | Stateless `@RestController` services behind a load balancer. |
| **State & Cache** | Redis (sessions, embedding cache, rate counters), Postgres (LangGraph checkpoints, audit) | Spring Session + Redis; JPA + Postgres. |
| **Data** | Vector DB (Pinecone/Weaviate), S3 (raw docs) | Your search index + object storage. |
| **Observability** | LangSmith tracing, Prometheus + Grafana | Sleuth/Zipkin + Micrometer + Grafana. |

The golden rule: **the Application layer is stateless.** All mutable state lives in the State layer.
That's what lets you scale workers horizontally and survive any single pod dying.

---

## 11.1 Redis session state

`SessionStore` wraps Redis with a TTL so conversation state lives outside the process. This is
**Spring Session backed by Redis**, almost verbatim: `save`/`load`/`extend`/`delete` map to writing a
session, reading it, sliding its expiry on activity, and invalidating on logout.

Two details matter in production:

- **TTL is mandatory.** Without an expiry, abandoned sessions accumulate forever and Redis memory
  grows without bound. The `setex` (set-with-expiry) call bakes the TTL in on every write.
- **The endpoint stays stateless.** `/chat/stateful` loads state from Redis at the start of the
  request and writes it back at the end. The pod holds nothing between requests, so a load balancer
  can route freely. See [`code/01_redis_session_state.py`](./code/01_redis_session_state.py) (runs
  offline against a `FakeRedis` stand-in).

## 11.2 PostgreSQL checkpointing

In Phase 3 you used `MemorySaver` — fine for dev, but it's an in-memory `HashMap` that dies with the
process. Production swaps in `PostgresSaver`: the same graph code, compiled with a durable
checkpointer, so a graph's state survives restarts, deploys, and crashes, and any worker can resume
any `thread_id` because the truth is in Postgres.

The mental model is exactly JPA: `MemorySaver` ≈ an in-memory map, `PostgresSaver` ≈ a
repository-backed store. You call `checkpointer.setup()` once (it creates the checkpoint tables, like
a Flyway migration), then `builder.compile(checkpointer=pg_saver)`. Nothing else changes.
[`code/02_postgres_checkpointing.py`](./code/02_postgres_checkpointing.py) demonstrates a thread
surviving a simulated restart (offline it falls back to `MemorySaver`, with the real
`PostgresSaver.from_conn_string(...)` usage clearly marked).

## 11.3 Background task queue

A research agent might run for minutes. You cannot hold an HTTP request open that long — it ties up a
worker thread and clients time out. The fix is the **submit-and-poll** pattern: the endpoint pushes
the job onto a Celery queue and returns a `task_id` immediately; a separate worker process runs the
agent and writes the result to Redis; the client polls a status endpoint until it's done.

This is precisely Spring's `@Async` + a real message broker (RabbitMQ/Kafka), or Spring Batch for
longer jobs. Celery's broker (Redis/RabbitMQ) is the queue; the worker is your `@Async` executor pool
living in its own process so it scales independently of the API tier.
[`code/03_celery_task_queue.py`](./code/03_celery_task_queue.py) runs offline with
`task_always_eager=True` (tasks execute inline, no broker needed) and shows the real broker/worker
setup in comments.

---

> ## ⚠️ Common Java-dev mistakes
>
> - **Keeping state in process memory.** A module-level dict of sessions works for one replica and
>   breaks the instant you scale to two. Push it to Redis. (The cardinal sin of this phase.)
> - **No TTL on sessions.** Unbounded Redis growth → OOM. Always `setex`, never plain `set`, for
>   session-scoped data.
> - **`MemorySaver` in production.** State vanishes on every deploy/restart. Use `PostgresSaver` (or
>   a Redis saver) for anything users expect to persist.
> - **Running long agent jobs inside the request thread.** Pins a worker, blows past gateway
>   timeouts, and can't be retried. Offload to Celery and return a `task_id`.
> - **No idempotency on task retries.** Celery retries failed tasks; if your task isn't idempotent
>   you'll double-charge / double-send. Use an idempotency key, exactly as you would for an at-least-once queue consumer.
> - **Sticky sessions as a crutch.** Pinning a user to one pod to "keep state" defeats horizontal
>   scaling and dies when that pod restarts. Externalize state instead.

---

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Horizontal scaling** | Adding more identical stateless instances behind a load balancer. |
| **Stateless service** | A service that keeps no mutable state between requests; all state is external. |
| **Session store** | External (Redis) storage of per-conversation state, with TTL. |
| **TTL** | Time-to-live; auto-expiry that bounds memory growth. |
| **Checkpointer / `PostgresSaver`** | The component that persists LangGraph state; Postgres-backed = durable across restarts. |
| **Task queue** | A queue of jobs processed asynchronously by worker processes (Celery). |
| **Broker** | The message transport (Redis/RabbitMQ) between task producers and workers. |
| **Worker** | A separate process that pulls tasks off the broker and executes them. |
| **Idempotency** | Property where running an operation twice has the same effect as once — essential for safe retries. |
| **API gateway** | The edge layer doing auth, rate limiting, and TLS termination. |
| **Fan-out workers** | Multiple agent worker processes sharing the load from the orchestrator. |
