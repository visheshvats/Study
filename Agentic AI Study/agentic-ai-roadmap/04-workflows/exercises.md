# Phase 4 — Workflows · Exercises

Fresh problems, easy → hard. One-line hints, **no solutions**. These deliberately differ from the
phase checklist — same concepts, new angles.

### 1. (Easy) Translate-then-formalize chain
Build a 2-step LCEL chain: step 1 translates an English paragraph to French, step 2 rewrites that
French into a formal register.
*Hint: each step is `prompt | llm | StrOutputParser()`; pass step 1's output string into step 2's template variable.*

### 2. (Easy) Give the router a safety net
Take a classifier router and guarantee that any label the LLM returns outside `{code, billing}`
lands on a `general` handler instead of throwing a `KeyError`.
*Hint: the routing function should return `"general"` whenever `state["route"]` isn't a known key — never trust the model to emit a valid label.*

### 3. (Medium) Fail-soft pipeline
Wrap a 3-step chain so that if step 2 raises, the pipeline returns step 1's partial result plus an
`"error"` field rather than propagating the exception.
*Hint: `try/except` around each `.invoke()`, accumulating into a result dict you return on either path — like a Spring `@Recover` fallback.*

### 4. (Medium) Prove the parallel speedup
Run 4 independent analyses both sequentially and via `asyncio.gather`, printing wall-clock time for
each approach.
*Hint: `time.perf_counter()` around each strategy; wrap the blocking `llm.invoke` in `asyncio.to_thread` so `gather` can actually overlap them.*

### 5. (Hard) Hybrid workflow
Compose all three patterns: route the input first, and for the `analysis` route fan out three
parallel sub-analyses, then chain a final "combine + summarize" step.
*Hint: a LangGraph node may itself call `asyncio.run(gather(...))`; the conditional edge picks the branch, and the combine step is just a normal downstream node.*

### 6. (Hard) Order-independent fan-in
Fan out N analyses where each coroutine returns `{ "name": ..., "result": ... }`, then fan in to a
dict keyed by `name` — correct even when results finish out of order.
*Hint: don't rely on list position from `gather`; have each coroutine carry its own key and build the dict from the returned objects.*
