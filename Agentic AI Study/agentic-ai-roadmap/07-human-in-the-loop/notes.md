# Phase 7 — Human in the Loop (HITL)

> **Duration:** ~0.5 week
> **Goal:** Build agents that *pause* for human approval before they act.

---

## Why this matters

Up to now your agents have run start-to-finish on their own. That's fine for drafting text or
answering questions — but the moment an agent can *do* something irreversible (issue a refund, send
an email to a customer, merge a PR, delete a record), "fully autonomous" becomes a liability. You
want a checkpoint where a person reviews, edits, or vetoes the agent's plan before it commits.

As a Spring developer you've built this pattern many times without calling it "HITL." It's the
manager-approval step in a `spring-statemachine` workflow. It's `@PreAuthorize` blocking a method
until a role check passes. It's a BPM (Activiti/Camunda) **user task** that parks a process instance
until someone clicks Approve. It's the manual-approval gate in a CI/CD pipeline that holds the deploy
until a human signs off. The hard part in all of these is the same: **how do you suspend a running
process, persist its exact state, and later resume it from precisely where it stopped — possibly on a
different machine, possibly hours later?**

LangGraph answers this with two primitives you already met in Phase 3: a **checkpointer** (state
persistence) and a **`thread_id`** (the conversation/session key). Add one compile-time flag —
`interrupt_before=[...]` — and the graph will halt before a chosen node, save everything, and hand
control back to you. When the human decision arrives, you call `invoke` again on the *same*
`thread_id` and execution continues. No global variables, no blocking threads, no lost work.

---

## The HITL sequence

The shape of every human-in-the-loop flow is the same:

1. User submits a task.
2. The agent does the *reversible* work (generate a draft, build a plan).
3. The graph **interrupts** and surfaces that draft to a human.
4. The human **approves**, **rejects with feedback**, or **edits**.
5. The graph **resumes**: ship the approved draft, or revise using the feedback.
6. Final output returns to the user.

The diagram for this is in [`diagrams.md`](./diagrams.md).

---

## 7.1 HITL with LangGraph `interrupt_before`

The mechanics rest on three pieces working together:

| Piece | Role | Java analogy |
|-------|------|--------------|
| `MemorySaver` (checkpointer) | Persists state after every node so execution can be paused and resumed. | A `JpaRepository`/session store that survives across requests. |
| `thread_id` (in `config`) | Identifies *which* paused run to resume. | The process-instance ID in Camunda, or an HTTP session id. |
| `interrupt_before=["review"]` | Tells the graph to halt **before** the named node runs. | A manual-approval stage that parks the pipeline. |

### The graph

The state carries the task, the draft, the human's decision, and the final output:

```python
class HITLState(TypedDict):
    task: str
    draft: str
    approved: bool
    feedback: str
    final: str
```

Three nodes wire together as `generate → review → decide → END`:

- **`generate_draft`** does the real LLM work and writes `draft`.
- **`request_review`** is a deliberate *no-op placeholder*. Execution is interrupted **before** it
  runs, so its body never executes on the first pass — it exists only as the pause point.
- **`apply_decision`** branches: if `approved`, the draft becomes `final`; otherwise it asks the LLM
  to revise the draft using `feedback`.

Compiling with both a checkpointer and the interrupt is what makes the pause possible:

```python
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["review"],   # ← PAUSE HERE for human input
)
```

### The three-step run

1. **Run until interrupt.** `graph.invoke(initial, config)` executes `generate_draft`, then stops
   *before* `review`. You read the draft with `graph.get_state(config).values["draft"]`.
2. **Human reviews.** In the source this is a blocking `input()` for demo purposes. **In production
   this must not block a server thread** — the draft goes to a UI/queue and the decision arrives
   later via a webhook or a second HTTP request.
3. **Resume.** `graph.invoke({"approved": ..., "feedback": ...}, config)` re-enters on the same
   `thread_id`; LangGraph restores the saved state, merges your injected values, runs `review` and
   `decide`, and returns the `final`.

The runnable code in [`code/01_hitl_interrupt.py`](./code/01_hitl_interrupt.py) demonstrates **both**
an approve path and a reject-with-feedback path *without* blocking on stdin, and
[`code/02_hitl_fastapi.py`](./code/02_hitl_fastapi.py) turns it into a two-endpoint web service
(`POST /draft` to start and get the draft, `POST /review/{thread_id}` to resume) — the realistic
production shape.

---

> ## ⚠️ Common Java-dev mistakes
>
> - **Forgetting the checkpointer.** Without `checkpointer=...`, `interrupt_before` has nowhere to
>   save state — there is nothing to resume. The pause/resume contract *requires* persistence.
> - **Blocking a server thread on `input()`.** The demo's `input()` is fine at a terminal but fatal
>   in a web app — it pins a worker thread indefinitely. Surface the draft and return; resume on a
>   later request. (Same reason you'd never call `Scanner.nextLine()` inside a `@RestController`.)
> - **In-memory checkpointing in production.** `MemorySaver` lives in the process — restart the
>   server and every paused workflow vanishes. Use a durable saver (Postgres/Redis, see Phase 11) so
>   approvals survive deploys.
> - **Resuming with the wrong `thread_id`.** The `thread_id` *is* the handle to the paused run. Lose
>   it or mismatch it and you start a brand-new run instead of continuing the old one.
> - **No timeout or escalation.** Humans forget. A parked workflow with no SLA/escalation path waits
>   forever — design a timeout (auto-reject, reminder, reassign), exactly as you would for a BPM user task.
> - **Trusting human input blindly.** The resumed payload (`approved`, `feedback`) is external input.
>   Validate it just like a `@RequestBody` — don't let a malformed decision corrupt state.

---

## Key terms

| Term | One-line definition |
|------|---------------------|
| **HITL** | Human-in-the-loop: a workflow that pauses for human review/approval before continuing. |
| **`interrupt_before` / `interrupt_after`** | Compile flags that halt the graph just before / just after a named node. |
| **Checkpointer** | The component (e.g. `MemorySaver`, `PostgresSaver`) that persists graph state so it can be paused and resumed. |
| **`thread_id`** | The key under `config["configurable"]` that identifies which saved run to resume. |
| **Resume** | Calling `invoke` again on the same `thread_id`; the graph restores state and continues from the interrupt. |
| **State snapshot** | The full saved state at a checkpoint, read via `graph.get_state(config)`. |
| **Approval gate** | A workflow stage that blocks progress until a human authorizes it. |
| **Webhook resume** | Production pattern where the human decision arrives as an async callback that triggers the resume. |
