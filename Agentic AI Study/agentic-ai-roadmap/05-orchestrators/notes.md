# Phase 5 — Orchestrators (Multi-Agent)

> **Duration:** 1 week
> **Goal:** Build systems where multiple agents coordinate to solve a complex task — one **orchestrator** decomposes the goal, delegates subtasks to specialized **workers**, then synthesizes the results into a final answer.

---

## Why this matters

You have spent six years wiring `@Service` beans together. The mental model you already own is exactly the one you need here, so let me name it before I name anything new.

Imagine a `BlogPostService` that, on a single REST call, has to: pull facts from a `ResearchService`, hand those facts to a `WritingService`, then run the draft through an `EditingService` before returning the response. The `BlogPostService` itself does no domain work — it **coordinates**. It knows the order, it passes the output of one specialist as the input to the next, and it assembles the final payload. That coordinator is an **orchestrator**. The specialist services are **workers**.

This is the **orchestrator–worker pattern**, and in the Spring world you have built it many times under different names:

- **Saga orchestration** — a central `OrderSaga` that calls `PaymentService`, then `InventoryService`, then `ShippingService`, holding the thread of "what's done, what's next." That is *orchestration*. Contrast it with **choreography**, where each service listens for events and reacts with no central brain. Multi-agent systems almost always start as orchestration because an LLM orchestrator is far easier to reason about and debug than a swarm of agents emitting events at each other.
- **A workflow engine** (Camunda, Temporal, AWS Step Functions) — you define a sequence of activities, some depending on the output of earlier ones, and the engine runs them in order. `OrchestratorAgent.execute()` is a tiny, LLM-flavored workflow engine: it sorts steps, gathers the outputs of dependencies, and feeds them forward.
- **Strategy + dependency injection** — each `WorkerAgent` is a strategy bean. The orchestrator holds a `Map<String, WorkerAgent>` (literally `Dict[str, WorkerAgent]` in the code) and picks the right strategy by name at runtime.

The one genuinely new thing is **who writes the plan**. In Spring, *you* hard-code the order of service calls at compile time. In a multi-agent system, the **LLM writes the plan at runtime** — it looks at the goal, looks at the available workers, and emits a JSON DAG of steps. That single shift — *a non-deterministic component deciding control flow* — is the source of every power and every danger in this phase. Hold onto it.

---

## The multi-agent architecture

The architecture from the roadmap is a hub-and-spoke:

```
                 ┌──────────────────────────────┐
   User ───────► │   Orchestrator               │
                 │   Decompose + Delegate +      │ ◄──┐
                 │   Synthesize                  │    │ results flow back
                 └───────┬───────┬───────┬───────┘    │
                         │       │       │            │
                    Researcher Writer  Editor  Analyst│
                         └───────┴───────┴────────────┘
```

Read it as three phases the orchestrator runs in sequence:

1. **Decompose (plan)** — the orchestrator asks the LLM: "Here is the goal, here are the workers I have, break this into ordered subtasks." The LLM returns a structured plan.
2. **Delegate (execute)** — the orchestrator walks the plan in dependency order, calling each worker with its task *plus the outputs of the steps it depends on*.
3. **Synthesize** — the orchestrator collects every worker's output and asks the LLM to weave them into one coherent answer.

Each worker is a self-contained mini-agent with its own **system prompt** (its "specialty"). It knows nothing about the orchestrator or its siblings — it just receives a task and some context and returns text. That isolation is deliberate and it is exactly the **single-responsibility principle** you already enforce on your beans.

---

## 5.1 The Worker + Orchestrator pattern

### `WorkerAgent` — a specialist bean with an injected role

```python
class WorkerAgent:
    def __init__(self, name: str, specialty: str, instructions: str = ""):
        self.name = name
        self.specialty = specialty
        self.instructions = instructions or f"You are a {specialty} specialist."
        self.llm = ChatAnthropic(model="claude-sonnet-4-6")
```

The `instructions` string **is** the worker's behavior. It is the equivalent of the concrete class behind a strategy interface: same `run()` signature for everyone, completely different behavior depending on what you injected. A `WorkerAgent("Researcher", "research", "Find facts and cite sources.")` and a `WorkerAgent("Writer", "writing", "Write engaging prose.")` share one class — the *constructor argument* is what specializes them. This is **specialty injection** (a.k.a. **system-prompt injection**): you configure behavior by data, not by subclassing.

The `run(task, context)` method is the worker's single public method:

```python
def run(self, task: str, context: str = "") -> str:
    messages = [SystemMessage(content=self.instructions)]
    if context:
        messages.append(HumanMessage(content=f"Context:\n{context}"))
    messages.append(HumanMessage(content=f"Task:\n{task}"))
    return self.llm.invoke(messages).content
```

The `SystemMessage` is the worker's role; the optional `context` is the upstream output (the "results of the steps I depend on"); the `task` is the specific instruction the orchestrator handed down. One LLM call, one string back. Clean, testable, stateless.

> **Stateless is a feature.** Just like a well-behaved `@Service` bean holds no per-request state in fields, a worker holds no state across calls. Everything it needs arrives as arguments. That is what makes it safe to reuse the same worker instance across many steps.

### `OrchestratorAgent` — the Saga coordinator

```python
class OrchestratorAgent:
    def __init__(self, workers: List[WorkerAgent]):
        self.workers: Dict[str, WorkerAgent] = {w.name: w for w in workers}
        self.llm = ChatAnthropic(model="claude-sonnet-4-6")
```

The orchestrator holds a **registry of workers keyed by name** — a `Dict[str, WorkerAgent]`. This is your `Map<String, Strategy>` injected by Spring. The orchestrator also has *its own* LLM, separate from the workers', because planning and synthesizing are themselves reasoning tasks.

**`plan(goal)` — the LLM acts as a workflow designer.** The orchestrator sends a prompt that says, in effect: "Here is the goal, here are my worker names, return ONLY a JSON array of steps where each step has `step`, `worker`, `task`, and `depends_on`." The response is parsed into `List[Dict]`. Crucially the prompt asks for `depends_on` — a list of earlier step numbers — which is what turns a flat list into a **dependency graph (a DAG)**.

```python
[
  {"step": 1, "worker": "Researcher", "task": "...", "depends_on": []},
  {"step": 2, "worker": "Writer",     "task": "...", "depends_on": [1]},
  {"step": 3, "worker": "Editor",     "task": "...", "depends_on": [2]}
]
```

The parse is **guarded**, and this is the single most important defensive line in the whole phase:

```python
json_text = re.sub(r'```json|```', '', response.content).strip()
try:
    return json.loads(json_text)
except json.JSONDecodeError:
    return [{"step": 1, "worker": list(self.workers.keys())[0], "task": goal, "depends_on": []}]
```

The LLM is *asked* for clean JSON but is not *guaranteed* to return it. It may wrap the array in a markdown fence, add a chatty preamble, or hallucinate a worker name. The `re.sub` strips the common ` ```json ` fences; the `try/except` catches anything still malformed and **falls back to a single-step plan** that just hands the whole goal to the first worker. The system degrades gracefully instead of throwing. In Spring terms: this is the `try/catch` around a flaky downstream call with a sane default — never let a malformed response from a non-deterministic component crash your coordinator.

**`execute(plan)` — dependency-aware delegation.** This is the workflow engine:

```python
def execute(self, plan: List[Dict]) -> Dict[int, str]:
    results = {}
    for step in sorted(plan, key=lambda x: x["step"]):
        dep_context = "\n\n".join(
            f"Step {d} result:\n{results[d]}"
            for d in step.get("depends_on", []) if d in results
        )
        worker_name = step["worker"]
        if worker_name in self.workers:
            results[step["step"]] = self.workers[worker_name].run(step["task"], dep_context)
        else:
            results[step["step"]] = f"Error: worker '{worker_name}' not found"
    return results
```

Walk through it like a code reviewer:

- `sorted(plan, key=lambda x: x["step"])` processes steps in numeric order. Because a well-formed plan only lets a step depend on *lower-numbered* steps, sorting by step number gives a valid **topological order** for free. (This is the cheap-and-cheerful version; a real DAG executor would do a proper topological sort and reject cycles — see the warnings and exercises.)
- `dep_context` collects the **outputs of every dependency** into one string and passes it forward. This is the heart of the pattern: step 2's worker sees step 1's research. Data flows along the edges of the graph.
- `if worker_name in self.workers` is another guard — the LLM might name a worker that doesn't exist. Instead of a `KeyError`, the step records an error string and execution continues. (In production you'd likely fail the run or retry the plan, but graceful continuation is a reasonable default for a learning harness.)

**`synthesize(goal, step_results)` — the reduce step.** All worker outputs (`Dict[int, str]`) are serialized and handed back to the orchestrator's LLM with the original goal: "Here is everything the workers produced; merge it into one comprehensive answer." If `execute` is the *map*, `synthesize` is the *reduce*.

**`run(goal)` — the public entry point.** It ties the three phases together: `plan → execute → synthesize`. This is the one method an outside caller touches, exactly like the single `@PostMapping` that fronts a Saga.

---

## When NOT to use multi-agent

This is on the Phase 5 checklist for a reason, and as an enterprise engineer you will feel the pull to over-architect. Resist it. Multi-agent is the **distributed system** of the agent world: more moving parts, more failure modes, more cost, harder to debug. Reach for it only when the problem genuinely demands it.

**Prefer a single agent (one LLM call, maybe with tools) when:**

- The task is one coherent thing a single capable model can do in one or two turns ("summarize this document," "answer this question"). Splitting it across workers just adds latency and token cost for no quality gain.
- You can't clearly name distinct specialties. If "Researcher" and "Writer" would get nearly identical system prompts, you don't have two workers — you have one.

**Prefer a plain deterministic workflow (Phase 4) when:**

- The steps and their order are **known at design time** and never change. You don't need an LLM to *plan* the sequence of "fetch → validate → transform → store" — you already know it. Hard-code it. Letting an LLM decide a fixed control flow is paying a non-determinism tax for nothing. (This is the same instinct that stops you from putting a rules engine in front of a three-line `if`.)

**Reach for multi-agent only when:**

- The task **decomposes into genuinely different skills** (research vs. writing vs. editing) where a focused system prompt per role measurably improves output.
- The **decomposition itself is dynamic** — the right plan depends on the goal and you can't enumerate every plan in advance. *This* is where letting the LLM plan earns its cost.
- Subtasks could run in **parallel** and the wall-clock win is worth the orchestration overhead.

**The cost reality:** every worker call is a separate LLM round-trip. A 3-worker pipeline with planning and synthesis is **5 LLM calls** (plan + 3 workers + synthesize), not 1. Latency adds up serially; cost adds up always; and **fan-out multiplies both** — an orchestrator that spawns 10 workers makes at least 12 calls. Always ask: would one good prompt have done this for one-fifth the cost and latency? Anthropic's own guidance ("Building Effective AI Agents," in resources.md) is blunt about this: start with the simplest thing, add agentic complexity only when simpler approaches measurably fall short.

---

## ⚠️ Common Java-dev mistakes

> **Callout — the six ways an experienced backend engineer trips on this pattern.** None of these are about Python syntax; they're about forgetting that one of your components is now non-deterministic.

1. **Trusting the LLM to return clean JSON.** You would never call `objectMapper.readValue()` on an untrusted external response without a `try/catch` and a fallback. Don't do it here either. The LLM *will* eventually wrap its plan in markdown, add a "Sure, here's the plan:" preamble, or emit a trailing comma. **Always strip fences and guard `json.loads` with a fallback plan**, exactly as the source code does. A naked `json.loads(response.content)` is a production incident waiting to happen.

2. **Ignoring `depends_on` ordering.** If you execute steps in arrival order instead of dependency order, the Writer runs before the Researcher and gets empty context. The naïve "sort by step number" works *only if* the plan number is monotonic with dependency order. The robust answer is a real topological sort — and that sort is also where you **detect cycles** (step 1 depends on step 2 which depends on step 1). An unguarded cycle is an infinite loop or a starved step.

3. **Unbounded fan-out cost.** The LLM might decide a goal needs 30 subtasks. With no cap, you've just authorized 32+ API calls from a single user request. Treat fan-out like a thread pool: **bound it.** Set a `max_steps`, validate the plan length, and reject or truncate plans that exceed it. This is rate-limiting and bulkheading applied to agents.

4. **Sharing mutable state between workers.** It is tempting to give workers a shared `context` object they can mutate, "for efficiency." Don't. Workers must be **stateless**, communicating only through the explicit `dep_context` the orchestrator passes. Shared mutable state across what are effectively concurrent, retryable units is the same race-condition nightmare you fight in multithreaded Java — except now the "thread" is a probabilistic model whose output you can't predict.

5. **No timeout or retry per worker.** Each worker call is a network call to a remote model. It can hang, rate-limit (429), or return garbage. A coordinator with no per-step timeout, retry, or circuit breaker will hang the whole run on one slow worker — the classic distributed-systems failure you already guard against with Resilience4j. Wrap each `worker.run()` in a bounded retry-with-backoff and a timeout.

6. **Treating the orchestrator as deterministic.** This is the meta-mistake that causes the other five. The plan is *generated*, not *configured*. The same goal can produce a different plan on two runs. Your tests cannot assert "the plan has exactly 3 steps in this order." Test the **invariants** instead: the plan is valid JSON, every worker named exists, there are no cycles, the run produces a non-empty synthesis. Pin the model behavior with a **mock/fake LLM** for deterministic tests (which is exactly why the code in this phase ships a `USE_MOCK` flag).

---

## Key terms

| Term | Plain meaning | Closest Spring/Java analogy |
|---|---|---|
| **Orchestrator** | The coordinating agent that decomposes a goal, delegates to workers, and synthesizes results. Does no domain work itself. | A Saga orchestrator / `@Service` that injects and sequences other services. |
| **Worker agent** | A self-contained specialist agent with one role (one system prompt) and one `run()` method. Stateless. | A concrete strategy bean behind a common interface. |
| **Plan / decompose** | The orchestrator's first phase: the LLM turns a goal into an ordered, dependency-tagged list of subtasks (JSON). | A workflow definition generated at runtime instead of compile time. |
| **Synthesize** | The final phase: merge all worker outputs into one coherent answer. | The "reduce" / response-assembly step at the end of a Saga. |
| **Dependency graph (DAG)** | Steps connected by `depends_on` edges; a step runs only after its dependencies. Must be acyclic. | A workflow/Step Functions state machine; a Maven build's task graph. |
| **Multi-agent** | A system of two or more cooperating agents (≥1 orchestrator + ≥1 worker). | A microservice constellation coordinated by a saga. |
| **Specialty / system-prompt injection** | Configuring a worker's behavior by passing its role as a string, not by subclassing. | Constructor injection of strategy behavior via configuration/data. |
| **Fan-out cost** | The multiplicative LLM-call (and latency and dollar) cost of an orchestrator spawning many workers. | Connection/thread-pool exhaustion from unbounded downstream calls. |

---

## The one-line takeaway

An orchestrator–worker system is a **Saga whose plan is written by an LLM at runtime**. Everything you know about coordinating services applies — *plus* the discipline of treating one of your components as untrusted and non-deterministic: guard its output, bound its cost, time out its calls, and test its invariants rather than its exact behavior.
