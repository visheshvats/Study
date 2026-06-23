# Phase 11 — Scaling & Architecture · Exercises

Fresh problems, easy → hard. One-line hints, **no solutions**. Different angles from the checklist.

### 1. (Easy) Sliding-expiration on read
Make `SessionStore.load` also call `extend`, so an active session's TTL refreshes on every request.
*Hint: reset the expiry after a successful read — that's how an HTTP session stays alive while a user is active.*

### 2. (Easy) Survive a "restart"
Run a graph for two turns, discard the graph object, rebuild it against the **same** checkpointer,
and prove the thread still remembers.
*Hint: the checkpointer — not the graph object — owns the state; reuse the same saver instance keyed by the same `thread_id`.*

### 3. (Medium) Submit-and-poll end to end
Wire `POST /research/async` (returns a `task_id`) and `GET /research/{task_id}` (returns
processing/done), backed by the task queue.
*Hint: write the result to Redis under `result:{task_id}`; the GET just reads that key — no blocking.*

### 4. (Medium) Idempotent task submission
Add an idempotency key so submitting the same job twice returns the original `task_id` instead of
running it again.
*Hint: hash the request, check Redis for an existing `task_id` under that hash before enqueuing — the at-least-once-consumer pattern.*

### 5. (Hard) Map the scaling boundaries
For the reference architecture, list which components scale horizontally (add replicas) versus which
are shared singletons/clusters, and why.
*Hint: stateless app/worker tiers scale out freely; Redis/Postgres/vector-DB are shared state that scale via clustering/replication, not by cloning your app.*

### 6. (Hard) Graceful shutdown without dropping work
Make a worker finish its in-flight task on `SIGTERM` instead of dropping it mid-run.
*Hint: trap the signal, stop accepting new tasks, drain the current one — the same `@PreDestroy`/graceful-shutdown discipline you'd give a Spring worker before a rolling deploy.*
