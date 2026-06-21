# Phase 1 — Exercises

Work these in order, easy → hard. They reinforce the same skills as the roadmap checklist but are **new tasks**, not the checklist itself. No solutions are given — struggle a little; that's where the learning is. One hint per exercise. Use the `USE_MOCK = True` mock client from the `code/` files so you can iterate offline before spending real tokens.

---

### Exercise 1 — Persona swap on a single call (warm-up)
Write a function that takes one user question and a `persona` argument (`"pirate"`, `"lawyer"`, `"toddler"`) and returns the answer in that voice. Run the *same* question through all three personas and print the results side by side. Confirm the only thing changing is the system prompt.

> **Hint:** The persona belongs in `system=`, never baked into the `user` message.

---

### Exercise 2 — Multi-turn history that survives a "callback" (history management)
Build a small REPL loop: read a line from the user, append it as a `user` turn, call the model, append the assistant reply, repeat. Across at least four turns, get the model to recall a fact you stated in turn 1 (e.g. your favorite color). Then deliberately *skip* appending one assistant reply and observe how the conversation degrades — that failure is the lesson.

> **Hint:** Roles must strictly alternate user / assistant; the list *is* your only memory.

---

### Exercise 3 — Few-shot ticket-priority classifier (few-shot)
Using few-shot prompting, build a classifier that maps a support message to exactly one priority: `LOW`, `MEDIUM`, or `HIGH`. Give 3–4 examples in the system prompt, set `temperature=0`, and require a single-word answer. Run it over a list of 6 test messages and print message → predicted priority.

> **Hint:** End the system prompt with "Return ONLY the priority word." and pin determinism with `temperature=0`.

---

### Exercise 4 — Robust JSON extraction that won't crash on bad output (structured output)
Write `extract_json_safe(text)` that returns a parsed dict on success and a `{"error": ...}` dict on failure — never raises. It must (a) strip markdown fences, (b) handle the model adding a leading sentence before the JSON, and (c) catch `json.JSONDecodeError`. Feed it three deliberately messy inputs (fenced JSON, JSON with a preamble, and non-JSON garbage) and confirm none of them throw.

> **Hint:** A regex to find the first `{...}` block, then `try/except json.JSONDecodeError` around the parse, is the defensible pattern.

---

### Exercise 5 — A streaming chat endpoint with a /reset (streaming)
Extend the FastAPI SSE example into a tiny stateful chat service: a `POST /chat/stream` that streams the reply *and* remembers history in memory, plus a `POST /reset` that clears it. Stream each token as an SSE `data:` event and end with `data: [DONE]`. Verify with `curl -N` that tokens arrive incrementally, not all at once.

> **Hint:** Offload the blocking SDK stream to a thread so you don't freeze the event loop; keep the per-session `messages` list outside the request handler.

---

### Exercise 6 — Two-tool agent that must chain (tool calling — hardest)
Build an agent with two tools: `get_account_balance(account_id)` and `convert_currency(amount, from_cur, to_cur)`. Ask it: *"What's account A-100's balance in EUR?"* The model must call `get_account_balance` first, then feed that number into `convert_currency` — a real multi-step chain. Log each tool call and assert the loop ran the agentic cycle at least twice before the final answer.

> **Hint:** Don't break out of the loop until `stop_reason != "tool_use"`; append both the assistant `tool_use` turn and the matching `tool_result` turn each pass, keyed by `tool_use_id`.
