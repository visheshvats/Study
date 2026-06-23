# Phase 7 — Human in the Loop · Exercises

Fresh problems, easy → hard. One-line hints, **no solutions**. Different angles from the checklist.

### 1. (Easy) Pause and read the draft
Build the `generate → review → decide` graph, compile it with `interrupt_before=["review"]`, and
print the draft *while the graph is paused* — before injecting any decision.
*Hint: after the first `invoke`, read `graph.get_state(config).values["draft"]`; don't resume yet.*

### 2. (Easy) Inject an approval and resume
Resume the paused graph with `{"approved": True}` and confirm `final == draft`.
*Hint: call `invoke` a second time with the same `config` (same `thread_id`) — that's what continues the run rather than starting a new one.*

### 3. (Medium) Reject-with-feedback path
Resume with `{"approved": False, "feedback": "..."}` and verify the `final` differs from the draft.
*Hint: the `decide` node should call the LLM to revise only on the reject branch; assert the two strings aren't equal.*

### 4. (Medium) Non-blocking review over HTTP
Expose the draft via `POST /draft` (returns draft + `thread_id`) and resume via
`POST /review/{thread_id}` — with **no** `input()` anywhere.
*Hint: persist nothing yourself — the checkpointer already holds state keyed by `thread_id`; the second endpoint just injects the decision and re-invokes.*

### 5. (Hard) Admin gate on a high-risk tool
Insert an approval interrupt *only* before a destructive tool call (e.g. "delete account"), letting
read-only tools run without pausing.
*Hint: route risky vs safe actions to different nodes; apply `interrupt_before` to just the risky node, like `@PreAuthorize` on one method.*

### 6. (Hard) Approval timeout / escalation
Add a rule: if no decision arrives within N seconds, auto-reject (or escalate) instead of waiting
forever.
*Hint: record a timestamp when the interrupt fires; on resume compare against `now` and branch to an `escalate` node if the SLA was missed — the BPM "user task timeout" pattern.*
