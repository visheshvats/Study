# Phase 5 — Exercises

Work these in order — they climb from "wire up one more bean" to "decide whether you should have built any of this." No solutions here; each has a one-line nudge. Use the code in `code/` as your starting harness (the `USE_MOCK` flag lets you run everything offline first).

These deliberately go *beyond* the Phase 5 checklist (which already covers building the Worker/Orchestrator classes, dependency-aware execution, the blog pipeline, and the "when not to" judgment). Treat the checklist as the floor; these are the climb.

---

### Exercise 1 — Add a new specialist worker *(easy)*

Add a fourth worker, `Analyst`, with a system prompt focused on extracting data-driven insights and numbers. Register it with the orchestrator and give it a goal where the plan *should* route a step to the Analyst (e.g. "Write a market summary of RAG adoption with adoption statistics").

> **Hint:** A new worker is just one more entry in the constructor list — like registering one more strategy bean. The interesting part is whether the planner actually *chooses* it; check the printed plan.

---

### Exercise 2 — Make the planner robust to bad JSON *(easy–medium)*

The source falls back to a single-step plan when `json.loads` throws. Harden it further: also handle the case where the parse *succeeds* but the structure is wrong — a step missing a `worker` key, a `depends_on` that isn't a list, or a `worker` name that isn't registered. Log each problem and either repair the step or drop it, never crash.

> **Hint:** Validate the parsed object against a schema before you trust it — same instinct as validating a deserialized DTO before passing it downstream.

---

### Exercise 3 — Add per-step retry and timeout *(medium)*

Wrap each `worker.run()` call so that a slow or failing worker is retried up to N times with exponential backoff, and abandoned after a timeout. On final failure, record an error result for that step instead of killing the whole run.

> **Hint:** This is Resilience4j for agents — a retry decorator plus a timeout around one remote call; decide whether a dead step fails the run or degrades it.

---

### Exercise 4 — Detect and reject cyclic dependencies *(medium–hard)*

The "sort by step number" trick silently assumes the plan is acyclic and monotonic. Replace it with a real topological sort that **detects cycles** (e.g. step 1 `depends_on: [2]` and step 2 `depends_on: [1]`) and a step depending on a non-existent step. On detection, refuse to execute and surface a clear error.

> **Hint:** Kahn's algorithm or a DFS with a "currently-visiting" set — if you revisit a node that's still on the stack, you have a cycle.

---

### Exercise 5 — Build the Researcher → Writer → Editor blog pipeline end to end *(medium–hard)*

Run the full blog-post goal so the plan produces three dependent steps and you can *see* the research feeding the draft and the draft feeding the edit. Then add an assertion harness that verifies the **invariants** (plan is valid, every named worker exists, dependencies form a DAG, synthesis is non-empty) rather than the exact wording.

> **Hint:** You can't assert the model's words, so assert its contracts — print the `dep_context` each worker receives to prove data is flowing along the edges.

---

### Exercise 6 — Decide when a single agent beats multi-agent *(hard / judgment)*

Take three goals: (a) "Summarize this paragraph," (b) "Translate then summarize this document," (c) "Research, write, and edit a blog post." For each, implement *both* a single-agent solution and the multi-agent one, then compare LLM-call count, latency, and output quality. Write a short paragraph recommending which approach you'd ship for each, and *why*.

> **Hint:** Count the round-trips before you measure quality — if multi-agent costs 5× the calls for no quality gain, the architecture review writes itself.
