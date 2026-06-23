# Phase 9 — Debugging & Observability

> **Duration:** ~0.5 week
> **Goal:** Understand what your agent is doing and precisely *why* it fails.

---

## Why this matters

In your Spring Boot world, when a request misbehaves you have a reflex: pull up the trace in Jaeger, grep the JSON logs, check the Micrometer dashboard, find the slow span, fix it. The system is deterministic. The same input produces the same output, every time. A bug is a bug — reproduce it once and you can reproduce it forever.

Agents break that contract. An LLM-backed node is **non-deterministic**: the same prompt can yield a different tool call, a different answer, or a hallucinated field on the next run. Failures are rarely a clean `NullPointerException` — they're "the model decided not to call the search tool this time," or "the agent looped four times before giving up," or "the answer was confidently wrong." None of that shows up in a stack trace. You *cannot fix what you cannot see*, and with agents there is a lot you cannot see by default.

So observability stops being a nice-to-have and becomes the primary debugging surface. The good news: the discipline maps almost one-to-one onto the stack you already know.

| You know (Java / Spring) | Agentic equivalent (Phase 9) | What it answers |
| --- | --- | --- |
| Distributed tracing — Zipkin / Jaeger / Sleuth | **LangSmith tracing** (9.1) | "What was the full call tree for this request? Which span was slow? What did the model actually receive and return?" |
| SLF4J / Logback JSON appender | **Structured logging** (9.3) | "What happened, in order, with timestamps and correlation IDs I can grep?" |
| Micrometer metrics + cost monitoring | **Token tracking** (9.4) | "How many tokens did this cost, and what is the running bill for this session?" |
| Stepping a debugger / reading an audit log | **State inspection** (9.2) | "What did the graph's state look like at every checkpoint, and what was it about to do next?" |

The mental shift: in a deterministic service you mostly debug *after* the fact from logs. With agents you also debug *the reasoning itself* — the sequence of decisions the model made — which is why tracing and state history matter so much more here than they did for a typical CRUD endpoint.

---

## 9.1 LangSmith tracing — your distributed tracing for LLM calls

LangSmith is to an agent what Jaeger is to a microservice mesh. It captures a **trace** (the whole request) made of nested **spans** (each LLM call, each tool call, each chain step), with inputs, outputs, latency, and token counts attached to every span. You open it in a browser and see the call tree exactly the way you read a flame graph in Jaeger.

The killer feature is the same one Spring Cloud Sleuth gave you: **auto-instrumentation with zero code change.** In Sleuth you add the starter to the classpath and suddenly every HTTP call carries a trace ID. In LangSmith you set three environment variables and every LangChain/LangGraph call starts reporting:

```python
import os

# Set these BEFORE any LangChain import — this is the #1 gotcha (see below).
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"]    = "ls__your_key"
os.environ["LANGCHAIN_PROJECT"]    = "agentic-ai-dev"   # like a Jaeger service name

# After this, every chain/graph .invoke() auto-traces to https://smith.langchain.com.
```

A **LangSmith project** is just a named bucket of traces — think of it as the service name you pick in Jaeger so you can filter. Use one per environment (`agentic-ai-dev`, `agentic-ai-prod`) so dev noise never pollutes prod traces.

For your *own* functions — a RAG pipeline, a custom retriever, a business step that isn't a LangChain primitive — auto-instrumentation won't see inside them. That's what `@traceable` is for. It's the agentic equivalent of Micrometer's `@Observed` or a manual `tracer.spanBuilder(...).startSpan()`: it wraps a plain Python function so it shows up as its own span, with whatever metadata you attach.

```python
from langsmith import traceable

@traceable(name="My RAG Pipeline", metadata={"version": "1.2"})
def my_pipeline(query: str) -> str:
    return rag_chain.invoke(query)
```

That `metadata={"version": "1.2"}` is gold for debugging: tag traces with the prompt version, the model name, the tenant ID, the feature flag — anything you'd want to filter or group by later, just like span tags in Jaeger.

> **Offline note for the code folder:** the demo (`01_langsmith_tracing.py`) sets the env vars and decorates a function with `@traceable`, but runs it over a *mock pipeline* so it works with no API key and no network. Comments show exactly the one line to change to point it at a real chain.

---

## 9.2 State inspection — stepping the debugger / reading the audit log

A LangGraph graph carries a **state** object that every node reads and writes. When you enable checkpointing, the graph saves a **state snapshot** at every step — the values, the next node to run, a timestamp, and metadata. Inspecting these is two things at once:

- **Like stepping a debugger:** `get_state(config)` gives you the *current* snapshot — the live values and `state.next` (which node is about to execute). It's the agentic equivalent of pausing on a breakpoint and inspecting locals plus "what line runs next."
- **Like reading an audit log:** `get_state_history(config)` replays *every* snapshot since the run started, newest first. This is your time-travel debugger — you can see exactly how the state evolved decision by decision, which is precisely what you need when an agent's *reasoning* (not its code) went wrong.

```python
config = {"configurable": {"thread_id": "debug-001"}}   # thread_id ≈ a trace/correlation id

# Current state — the "breakpoint" view
state = graph.get_state(config)
print(f"Current values: {state.values}")
print(f"Next node:      {state.next}")
print(f"Created at:     {state.created_at}")

# Full history — the "audit log" / time-travel view
for snapshot in graph.get_state_history(config):
    step      = snapshot.metadata.get("step", 0)
    node      = snapshot.metadata.get("source", "unknown")
    msg_count = len(snapshot.values.get("messages", []))
    print(f"Step {step:02d} | Node: {node:20s} | Messages: {msg_count}")
```

The `thread_id` is the correlation ID for a conversation/run — like the `traceId` Sleuth threads through everything. Same id, same history; that's how you tie a user's whole session together. (And because the history is checkpointed, LangGraph can also *resume* from any snapshot — but that's Phase 8 territory; here we only read it.)

> **Offline note:** `02_state_inspection.py` builds a tiny **mock graph** that exposes `get_state` / `get_state_history` returning real snapshot-like objects, so the demo prints a genuine current state plus a full history with no LangGraph runtime needed. A comment shows how to swap in a real compiled graph with a checkpointer.

---

## 9.3 Structured logging — your Logback, plus an AOP twist

This one is *real* and runs as-is — no mocks. Python's `logging` module is the direct counterpart of SLF4J/Logback. `logging.basicConfig(...)` is your `logback.xml`: it sets the level, the format string (the equivalent of a Logback `<pattern>`), and the **handlers** (a `StreamHandler` = console appender, a `FileHandler` = rolling-file appender). `logging.getLogger("agentic-ai")` is `LoggerFactory.getLogger(...)`.

```python
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",   # ≈ Logback <pattern>
    handlers=[
        logging.StreamHandler(),                                   # ≈ console appender
        logging.FileHandler(f"agent_{datetime.now():%Y%m%d}.log"), # ≈ rolling file appender
    ],
)
logger = logging.getLogger("agentic-ai")
```

A **log handler** decides *where* a record goes; you can attach several, exactly like multiple Logback appenders. (For production you'd swap the format for a JSON formatter so logs are queryable in your log stack — the same reason you reach for `logstash-logback-encoder` in Spring.)

Now the part that should feel familiar in a different way. Manually adding `logger.info("entering...")` / `logger.info("exiting...")` to every node is exactly the boilerplate Spring AOP exists to kill. The **`@logged_node` decorator is an AOP `@Around` advice**: it wraps a node function so that *entering*, *timing*, *exiting*, and *exception logging* happen automatically — the proceed-and-measure pattern of an `@Around` aspect, expressed as a Python decorator instead of an annotation + pointcut.

```python
import time
from functools import wraps   # ≈ preserving method metadata so the proxy looks like the original

def logged_node(node_name: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(state: dict) -> dict:
            t0 = time.perf_counter()
            logger.info(f"→ [{node_name}] State keys: {list(state.keys())}")
            try:
                result = fn(state)                                  # joinPoint.proceed()
                logger.info(f"← [{node_name}] Done in {time.perf_counter() - t0:.2f}s")
                return result
            except Exception as e:
                logger.error(f"✗ [{node_name}] FAILED: {e}", exc_info=True)  # log THEN
                raise                                               # re-throw — never swallow
        return wrapper
    return decorator

@logged_node("process_query")
def process_node(state: dict) -> dict:
    ...
```

Note the `raise` after logging the error: the aspect *observes* the failure but does not *swallow* it. Swallowing exceptions in a node is one of the worst agentic anti-patterns (see below) — it makes failures invisible while corrupting downstream state.

---

## 9.4 Token tracking — Micrometer metrics for your LLM bill

There is no `RestTemplate` interceptor counting bytes here, but there's something better: every Anthropic response carries a `.usage` object with `input_tokens` and `output_tokens`. Tracking these is your **Micrometer + cost monitoring**: a per-call counter plus a running session total, turned into dollars. Tokens are billed **per MTok** (per million tokens) at different rates for input vs output, so the cost math is `tokens / 1_000_000 * price_per_mtok`.

```python
class TokenTracker:
    def __init__(self) -> None:
        self.total_input  = 0
        self.total_output = 0
        self.input_price_per_mtok  = 3.0    # $ per million input tokens  (check pricing page)
        self.output_price_per_mtok = 15.0   # $ per million output tokens

    def track(self, response) -> dict:
        inp = response.usage.input_tokens     # like reading a Micrometer Counter sample
        out = response.usage.output_tokens
        self.total_input  += inp
        self.total_output += out
        cost = (inp / 1_000_000 * self.input_price_per_mtok +
                out / 1_000_000 * self.output_price_per_mtok)
        return {"this_call": {"input": inp, "output": out, "cost_usd": round(cost, 6)},
                "session_total": {"input": self.total_input, "output": self.total_output, ...}}
```

Output tokens cost ~5x input here, which is the opposite intuition from "responses are small" — so a chatty agent that emits long answers can be your biggest line item. Log the per-call cost at `INFO` and you've got the equivalent of a Micrometer gauge you can alert on *before* the monthly bill surprises you.

> **Offline note:** `04_token_tracking.py` uses a **mock response object** exposing `.usage.input_tokens` / `.output_tokens`, so the cost math runs offline with no API key. A comment shows the single line to switch to a real `client.messages.create(...)` call.

---

## ⚠️ Common Java-dev mistakes

- **Setting LangSmith env vars *after* importing LangChain.** Auto-instrumentation reads `LANGCHAIN_TRACING_V2` at import time. Set it *after* `import langchain...` and you get silent no-tracing — the equivalent of putting Sleuth on the classpath but configuring it too late to wire the interceptors. Set the three env vars at the very top, before any LangChain/LangGraph import.
- **`print()` instead of `logging`.** `print()` is `System.out.println` — no levels, no timestamps, no handlers, ungreppable, can't be shipped to a log aggregator. Use the logger from day one, exactly as you'd never `System.out` in a Spring service.
- **No correlation / thread id.** Without a `thread_id` (and trace/span ids) you cannot stitch a multi-step run together — it's running distributed tracing with no `traceId`. Thread one id through the whole conversation so traces, logs, and state history all line up.
- **Logging full prompts with secrets/PII.** Prompts often contain user data, API keys echoed back, or internal context. Dumping the whole prompt at `INFO` is the agentic version of logging request bodies with passwords in them. Log lengths, hashes, IDs, and token counts — redact or omit the raw content.
- **Ignoring token cost until the bill arrives.** "We'll add metrics later" is how a runaway loop quietly spends thousands. Track cost per call from the first commit, the same way you'd never ship a hot endpoint with no latency metric.
- **Swallowing exceptions in nodes.** A bare `try/except: pass` (or returning a default on error) makes a node *look* successful while corrupting state — the failure becomes invisible and the agent marches on with bad data. Log the error *and re-raise* (as `@logged_node` does). Visible failures are debuggable; silent ones are not.

---

## Key terms

- **Trace** — the complete record of one request through the system, made of nested spans. The agentic equivalent of a Jaeger/Zipkin trace.
- **Span** — one timed unit of work inside a trace (an LLM call, a tool call, a chain step), with its own inputs, outputs, latency, and tags.
- **`@traceable`** — a LangSmith decorator that turns a plain Python function into its own span with custom name/metadata. Like Micrometer's `@Observed` or a manual `tracer.spanBuilder(...)`.
- **LangSmith project** — a named bucket of traces; effectively the "service name" you filter by. Use one per environment.
- **State snapshot** — the graph's saved state at one checkpoint: values, `next` node, timestamp, metadata. Like inspecting locals at a breakpoint.
- **State history** — the ordered sequence of all snapshots for a run; a time-travel/audit-log view of how state evolved.
- **Structured logging** — emitting log records with consistent fields (level, timestamp, name, message) via `logging`, ideally as JSON. The SLF4J/Logback discipline.
- **Log handler** — a destination/appender for log records (console, file, network). You can attach several, like multiple Logback appenders.
- **Decorator / AOP** — a Python decorator wraps a function to add cross-cutting behavior; `@logged_node` is the AOP `@Around` advice of the agent world (enter → proceed → exit, log on error and re-raise).
- **Token usage** — the `input_tokens` / `output_tokens` an LLM consumed for a call, exposed on `response.usage`. The raw metric behind cost.
- **Cost per MTok** — the billing unit: dollars per *million* tokens, charged separately for input and output (output is typically several times pricier).
