# Phase 9 — Exercises

Work these in order (easy → hard). No solutions provided — struggle is the point. These extend the phase; they do not repeat the checklist verbatim.

---

### 1. Enable tracing and add a custom span (easy)
Take any chain or function and turn on LangSmith tracing via the three env vars, then wrap one of your own functions with `@traceable(name=..., metadata={...})` and attach at least two metadata fields you'd actually filter by (e.g. `version`, `tenant`).
*Hint: set `LANGCHAIN_TRACING_V2`/`LANGCHAIN_API_KEY`/`LANGCHAIN_PROJECT` at the very top of the file — before any LangChain import — or the span never reports.*

### 2. Dump a full state history (easy–medium)
For a multi-step graph (or the mock graph from the code folder), iterate `get_state_history(config)` and print one aligned line per snapshot showing step number, source node, and message count — then also print the *current* state's `values` and `next`.
*Hint: history comes back newest-first; reverse it if you want chronological order.*

### 3. Write and apply `@logged_node` everywhere (medium)
Implement the `@logged_node(name)` decorator from scratch (enter log with state keys, timed exit log, error log + re-raise) using `functools.wraps`, then apply it to **every** node in a small graph. Confirm a deliberately-thrown exception in one node still propagates to the caller.
*Hint: `@wraps(fn)` keeps the wrapped function's name/docstring so the logs and any introspection still read correctly.*

### 4. Build a `TokenTracker` and assert the session math (medium)
Implement `TokenTracker` with per-call and running-session cost, feed it three mock responses with known `input_tokens`/`output_tokens`, and write `assert` statements proving the session total equals the sum of the calls and the dollar cost matches your hand-computed `tokens / 1e6 * price_per_mtok`.
*Hint: round both sides to the same number of decimals before comparing, or floating-point will bite you.*

### 5. Add a "debug mode" that pretty-prints state at each step (medium–hard)
Add a `debug: bool` flag (env var or argument) that, when on, pretty-prints the graph's state after every node — keys, sizes, and a truncated preview of message content — without changing behavior when off. Make it readable, not a raw `dict` dump.
*Hint: `json.dumps(..., indent=2, default=str)` handles non-serializable values; cap long strings so one giant message doesn't flood the console.*

### 6. Correlate all three signals with one id (hard)
Thread a single run id through the whole stack: use it as the graph `thread_id`, attach it as `@traceable` metadata, push it into every log line (via a `logging` filter or `extra=`), and tag the token-tracker output with it. Then prove you can take one id and pull the matching trace, log lines, and cost for that exact run.
*Hint: a `logging.Filter` (or `LoggerAdapter`) can inject a `run_id` field into the format string so you don't pass it manually to every `logger.info` call.*
