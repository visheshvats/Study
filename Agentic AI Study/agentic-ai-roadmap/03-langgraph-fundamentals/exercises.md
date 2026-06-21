# Phase 3 - Exercises

Work these in order; they climb from easy to hard. Each has a **one-line hint**, no solutions. Use the offline `USE_MOCK = True` pattern from `code/` so you can run everything without an API key. The Phase 3 checklist (build a 3-node graph, route to 3+ branches, ReAct agent, MemorySaver, print mermaid) is your baseline - these exercises go *beyond* it.

---

### Exercise 1 (easy) - Trace a 3-node linear graph

Build a `StateGraph` with state `{n: int, log: Annotated[list, add_messages-style append]}` and three nodes `double`, `add_ten`, `square` wired in a line. Each node appends a human-readable string to `log` describing what it did, and updates `n`. Invoke with `n=3` and print the final `n` and the full `log`.

> Hint: give `log` a reducer (use `add_messages` with string-wrapping `HumanMessage`, or write your own `operator.add` reducer) so appends accumulate instead of replacing.

---

### Exercise 2 (easy-medium) - Print and read your own graph

Take your Exercise 1 graph and print it with `print(graph.get_graph().draw_mermaid())`. Then, *without running it*, predict the order the nodes execute and confirm the printed `__start__` / `__end__` sentinels match your `set_entry_point` and `END` wiring.

> Hint: the mermaid output labels the entry as `__start__` and the terminal as `__end__`; trace the arrows.

---

### Exercise 3 (medium) - Four-way router with a fallback

Build a router that classifies a support ticket into `technical`, `billing`, `account`, or `general`, fans out to four specialist nodes via `add_conditional_edges`, and treats any unrecognised category as `general`. Feed it four tickets that each hit a different branch and assert (in code) that the right branch ran.

> Hint: widen the `Literal[...]` return type and the mapping dict together; route unknown labels to `"general"` so a misclassification never crashes the graph.

---

### Exercise 4 (medium-hard) - ReAct agent with two tools

Build a ReAct agent (mock or real) with exactly two tools: a `unit_converter(value, from_unit, to_unit)` and a `lookup_capital(country)` returning from a small dict. Ask a single question that forces *both* tools to fire ("How many miles is the distance if I drive 100 km, and what is the capital of France?") and print the full message trace.

> Hint: in offline mode, script the FakeChatModel to emit one tool call per turn (count the `ToolMessage`s already seen to decide the next move), then a final no-tool answer.

---

### Exercise 5 (hard) - Multi-turn memory + a control thread

Add `MemorySaver` to a chat graph. Over three turns on `thread_id="alpha"`, tell it a fact, tell it a second fact, then ask it to recall both. Then run one turn on `thread_id="beta"` asking for the same facts and confirm `beta` knows nothing. Finally call `graph.get_state(config)` for each thread and print how many messages each thread holds.

> Hint: the same `config={"configurable": {"thread_id": ...}}` must be passed on every `invoke`; compare `len(snapshot.values["messages"])` across the two threads to prove isolation.

---

### Exercise 6 (hard) - A loop with a stop condition

Build a graph with a single `refine` node and a conditional edge back to itself: `refine` increments a `quality` score in state, and a routing function sends it back to `refine` while `quality < 3`, otherwise to `END`. Print the mermaid and confirm the self-loop appears. Add a hard iteration cap so a bug can never spin forever.

> Hint: `add_conditional_edges("refine", should_continue, {"refine": "refine", "done": END})`; track an iteration counter in state and break to `"done"` if it exceeds your cap, mirroring the `max_iterations` guard in `code/03_react_agent.py`.
