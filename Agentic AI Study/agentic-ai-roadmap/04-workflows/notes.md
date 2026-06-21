# Phase 4 - Workflows (Notes)

> **Duration:** ~1.5 weeks
> **Goal:** Stop building chatbots - start building **systems**.

---

## Why this matters

A chatbot is one `llm.invoke(prompt)` call wrapped in a loop. It is reactive, single-shot, and non-deterministic: you ask, it answers, and you have very little control over *how* it got there. That is fine for a demo and dangerous in production.

A **workflow** is the opposite. It is a *system* you design: a fixed arrangement of LLM calls and plain code, wired together so the control flow is explicit, inspectable, and (mostly) deterministic. The model still does the fuzzy reasoning inside each step, but *you* own the orchestration - which step runs, in what order, what happens on failure, and how results combine. Anthropic's "Building Effective AI Agents" draws exactly this line: a **workflow** is where the paths are predefined in code; an **agent** is where the model itself decides the next step at runtime. Phase 4 is all workflows. (Agents come later.)

You have built this kind of thing before, just without LLMs in the boxes:

- **Orchestrating microservices.** A request hits service A, whose output feeds service B, whose output feeds C. You already think in terms of "who calls whom, in what order, and what happens if one is down." Prompt chaining is that, with each "service" being an LLM call.
- **Spring Integration / pipes-and-filters.** A message flows through a chain of `MessageHandler`s on channels, each transforming it. LCEL's `prompt | llm | parser` pipe is the same shape - filters connected by channels.
- **`CompletableFuture` composition.** `supplyAsync(a).thenApply(b)` is sequential dependency (chaining). `CompletableFuture.allOf(a, b, c).join()` is fan-out/fan-in (parallelization). A `switch` that picks which future to build is routing. You have the mental machinery already; Phase 4 just relabels it.

The single biggest shift from "chatbot thinking" to "workflow thinking": **you stop asking the model to do everything in one giant prompt and instead decompose the job into small, single-purpose steps you can test, route, retry, and parallelize independently.** A 500-line mega-prompt is the AI equivalent of a 500-line `doEverything()` method. Workflows are how you refactor it into a clean service layer.

There are three foundational patterns, and almost every real system is a combination of them.

---

## The three patterns at a glance

```
4.1 Prompt Chaining     input -> step1 -> step2 -> step3 -> output   (sequential, dependent)
4.2 Router              input -> classify -> ONE of {A, B, C}        (mutually exclusive)
4.3 Parallelization     input -> {A, B, C all at once} -> combine    (independent, concurrent)
```

The decision tree for "which one?" lives in `diagrams.md`. The short version: **dependency between steps -> chain; mutually-exclusive categories -> route; independent subtasks -> parallelize.**

---

## 4.1 Prompt Chaining (LCEL)

**Chaining** runs steps in a fixed sequence where each step's **output becomes the next step's input**. The Phase 4 example takes an article and pushes it through three LLM calls: extract 5 key points -> write a 2-sentence executive summary from those points -> write a headline from that summary.

```python
parser = StrOutputParser()

step1 = ChatPromptTemplate.from_template(
    "Extract exactly 5 key points ...\n\n{article}"
) | llm | parser

step2 = ChatPromptTemplate.from_template(
    "Write a 2-sentence executive summary ...\n\n{key_points}"
) | llm | parser

step3 = ChatPromptTemplate.from_template(
    "Write ONE punchy headline ...\n\n{summary}"
) | llm | parser

def analyze_article(article: str) -> dict:
    key_points = step1.invoke({"article": article})
    summary    = step2.invoke({"key_points": key_points})   # output of step1 -> input of step2
    headline   = step3.invoke({"summary": summary})         # output of step2 -> input of step3
    return {"key_points": key_points, "summary": summary, "headline": headline}
```

### LCEL and the `|` pipe

`prompt | llm | parser` is **LangChain Expression Language (LCEL)**. The `|` operator is overloaded to *compose* runnables left-to-right, exactly like a Unix pipe (`cat file | grep foo | sort`) or a Java `Stream` chain (`stream.map(extract).map(summarize).map(headline)`) or `Function.andThen`. Each segment is a `Runnable` with a uniform `.invoke(input) -> output` contract:

- `ChatPromptTemplate` takes a dict of variables, returns a formatted prompt value.
- `llm` takes that prompt value, returns an `AIMessage`.
- `StrOutputParser` takes the `AIMessage`, returns the plain `.content` string.

Because every link speaks the same `invoke` interface, you can snap them together with `|`. (This is why, in the offline code, the `FakeChatModel` *subclasses* `Runnable` - a plain class cannot be piped; the `|` operator only composes `Runnable`s.)

### When to use chaining

Use it when **step N genuinely needs step N-1's result.** The headline cannot be written until the summary exists; the summary cannot be written until the key points exist. That is a true data dependency, so sequencing is correct.

The flip side, which trips up Java devs coming from imperative code: **if the steps do NOT depend on each other, chaining them is a latency bug.** Three independent analyses run in a chain take 3x as long as they need to. That is what parallelization (4.3) is for. Always ask "does B actually need A's output?" before reaching for a chain.

> Runnable, offline version: `code/01_prompt_chaining.py`. It prints all three stages so the output->input handoff is visible, and wraps each step in error handling so a failure names the stage that broke.

---

## 4.2 Router Pattern (LangGraph)

A **router** uses a first LLM call (or a classifier) to pick a **category**, then dispatches the input to exactly **one** specialist handler for that category. The Phase 4 example classifies input into `code`, `business`, or `creative`, and sends it to a matching expert.

```python
class WorkflowState(TypedDict):
    input: str
    route: str
    output: str

def classify_input(state):  # the dispatcher
    result = llm.invoke([HumanMessage(content=f"Classify into: code, business, creative\nInput: {state['input']}\nReturn ONLY the label.")])
    return {"route": result.content.strip().lower()}

def router(state) -> str:   # reads state, returns the next node's KEY
    return state["route"] if state["route"] in ("code", "business") else "creative"  # DEFAULT

builder = StateGraph(WorkflowState)
# ... add classify + 3 handler nodes ...
builder.set_entry_point("classify")
builder.add_conditional_edges("classify", router, {"code": "code", "business": "business", "creative": "creative"})
```

### LangGraph and conditional edges

This is built on the LangGraph state machine from Phase 3. The **State** (`WorkflowState`) is the shared object that flows through; `classify` writes `route`; the **conditional edge** calls `router(state)`, which *reads* state and *returns the name of the next node*. The mapping dict translates that returned key into a real node to run.

### Java analogy

This is **Spring MVC dispatch**. `classify` is the `DispatcherServlet` reading the request and deciding which controller should handle it; the conditional edge is the handler mapping; each specialist node is a `@RequestMapping` method. Equivalently, it is the **Strategy pattern**: `router()` is the selector that picks which `Strategy` implementation executes. A Spring `@RequestMapping` dispatch and a `router()` function do the same job - inspect the input, pick exactly one handler.

The key design difference from a scattered `if/else`: the routing decision is **centralised in one pure function** and the whole fan-out is **inspectable** (you can `draw_mermaid()` the graph and see every branch). Compare that to routing logic smeared across the specialist methods - impossible to audit at a glance.

### The DEFAULT branch is mandatory

Notice `router()` does NOT just `return state["route"]`. It returns `creative` for anything that is not `code` or `business`. **A router with no fallback is a production incident waiting to happen:** the moment the classifier returns `"Code"` (capitalised), `"coding"`, or some garbled label, an exact-match-only router has no matching edge and the graph errors out. The default branch is your "else" / your `RequestMappingHandlerMapping` returning a 404 handler instead of throwing. The offline code (`code/02_router_pattern.py`) deliberately feeds in one nonsense input (`"asdfghjkl ??? purple monday"`) to prove the default catches it.

### When to use a router

Use it when inputs fall into **mutually exclusive categories** that each need *different* handling, and only one handler should run. If you would run *all* the handlers regardless, that is not routing - it is parallelization.

> Runnable, offline version: `code/02_router_pattern.py`. It routes four inputs (one per branch plus one to the default) and prints which branch each took.

---

## 4.3 Parallelization (Fan-out / Fan-in)

**Parallelization** runs several **independent** analyses on the same input **concurrently**, then combines the results. The Phase 4 example analyzes a document for sentiment, topics, and readability all at once - three calls that do not depend on each other.

```python
import asyncio

async def analyze_parallel(text: str) -> dict:
    async def sentiment():
        r = await asyncio.to_thread(llm.invoke, [HumanMessage(f"Rate sentiment ...\n{text}")])
        return r.content
    async def topics(): ...
    async def readability(): ...

    # FAN-OUT: all 3 start concurrently. FAN-IN: gather awaits all, returns IN ORDER.
    sent, top, read = await asyncio.gather(sentiment(), topics(), readability())
    return {"sentiment": sent, "topics": top, "readability": read}
```

### `asyncio.gather` = fan-out + fan-in

`asyncio.gather(a(), b(), c())` schedules all three coroutines to run concurrently (**fan-out**), waits for every one to finish, and returns their results in a list **in the order of the arguments** - not the order they finished (**fan-in / join**). This is `ExecutorService.invokeAll(tasks)` or `CompletableFuture.allOf(a, b, c).join()` followed by collecting each future's value. The speedup is real: three calls that each take ~0.5s run in ~0.5s total instead of ~1.5s. The offline `code/03_parallelization.py` measures exactly this and prints a ~3.00x speedup.

### The `asyncio.to_thread` detail that Java devs MUST internalise

Here is the trap. `asyncio` is **single-threaded cooperative concurrency**: one event loop, one thread, switching between tasks only when a task `await`s something. A coroutine gives up control at an `await`; between awaits it hogs the loop.

`llm.invoke(...)` is a **blocking** call (it waits on a network round-trip without yielding to the event loop). If you call it *directly* inside an `async def`, you block the entire event loop - no other task can run while it waits - and `gather` gives you **zero speedup**. Everything serialises.

`await asyncio.to_thread(llm.invoke, messages)` fixes this: it hands the blocking call to a **worker thread** and `await`s the result, freeing the event-loop thread to run the other tasks. This is exactly submitting a blocking job to an `ExecutorService` so your main thread stays responsive. **The rule: any blocking/synchronous call inside async code must be wrapped in `asyncio.to_thread` (or use a natively-async client).** Forgetting this is the single most common reason "my parallel code isn't any faster."

(LangChain also offers a native `await chain.ainvoke(...)` / `chain.abatch(...)` path that is async all the way down and avoids the thread hop - prefer that with a real async-capable model. `asyncio.to_thread` is the universal escape hatch for any blocking call.)

### The LangGraph fan-out node

LangGraph can host the parallel work as one node, then a `combine` node performs the fan-in into a single report:

```python
class ParallelState(TypedDict):
    text: str; sentiment: str; topics: str; readability: str; combined_report: str

def run_parallel_analysis(state):   # fan-out node
    return asyncio.run(analyze_parallel(state["text"]))

def combine_results(state):         # fan-in node
    return {"combined_report": f"# Report\n## Sentiment\n{state['sentiment']}\n..."}
```

### When to use parallelization

Use it when subtasks are **independent** - no one needs another's output. If B needs A's output, you cannot parallelize them; that is a chain. A nice property: parallelization also gives you **redundancy/voting** patterns (run the same prompt 3 times, take the majority) - same fan-out/fan-in shape.

> Runnable, offline version: `code/03_parallelization.py`. It runs the analyses sequentially and with `gather`, then prints the measured wall-clock speedup using a mock model with simulated latency.

---

## Combining the patterns

Real systems chain these together. The Phase 4 capstone (the document analyzer) is all three at once:

1. **Route** the document by type (legal / marketing / technical).
2. **Parallelize** several analyses on it (sentiment, topics, readability).
3. **Chain** the combined analysis into a final summary -> headline.

Compose freely. A router branch can itself be a chain; a chain step can fan out to a parallel block. Think of them as the `if`, the `;` (sequence), and the thread pool of a higher-level language whose statements are LLM calls.

---

## Common Java-dev mistakes (read this twice)

> These are the traps that cost the most time. Each maps to a habit imperative/Spring developers carry over.

- **Chaining steps that should be parallel.** If three analyses do not depend on each other, running them in a sequential chain triples your latency for no reason. Before you chain, ask "does step B actually consume step A's output?" If not, fan them out with `asyncio.gather`. (Mirror of writing three sequential `future.get()` calls instead of `allOf(...).join()`.)

- **No error handling between chain steps, so one failure kills the pipeline.** A bare `step3.invoke(step2.invoke(step1.invoke(x)))` means any single step's exception aborts everything with a confusing trace and no indication of *which* step failed. Wrap each step (the offline `01_prompt_chaining.py` does this) so you log the failing stage and either re-raise with context or fall back to a degraded result. The org rule "omit no key risks; fail safe" applies directly.

- **Calling blocking `llm.invoke` inside `async def` without `asyncio.to_thread`.** This blocks the single event loop and serialises everything - your `gather` runs no faster than a sequential loop. Always `await asyncio.to_thread(llm.invoke, ...)` (or use the native `ainvoke`). This is the #1 "why is my parallel code slow" bug.

- **A router with no fallback branch.** Exact-match-only routing crashes the moment the classifier returns an unexpected label (`"Code"`, `"coding"`, empty string). Always have a default branch (`else -> general/creative`). Treat it like a `default:` in a `switch` or a 404 handler - it must exist.

- **Assuming completion order in parallel results.** `asyncio.gather(a, b, c)` returns results in **argument order**, but if you instead use `asyncio.as_completed` or collect in a shared list as tasks finish, the order is *completion* order and is non-deterministic. Do not assume the first result back is task A's. Unpack by position from `gather`, or key results explicitly by name. (Same trap as reading from a `CompletionService` and assuming FIFO.)

- **Writing a 500-line mega-prompt instead of decomposing.** Cramming "extract, summarize, classify, and route" into one prompt is the AI version of a god-method. You lose the ability to test, retry, route, and parallelize the pieces. Decompose into single-purpose steps - that is the entire point of workflows.

- **Mutating shared state across parallel branches.** In the LangGraph fan-out, each parallel branch should return its OWN keys; do not have two concurrent branches write the same state key without a reducer, or you get a last-write-wins race. (Phase 3's reducer rules still apply.)

---

## Key terms (glossary)

- **workflow** - a system where the control flow (which LLM/code step runs, in what order) is **predefined in code**. Deterministic orchestration around fuzzy steps. (Anthropic's distinction.)
- **agent** - a system where the **model itself decides** the next step at runtime. More flexible, less predictable. Phase 5+ territory; Phase 4 is workflows only.
- **prompt chaining** - running steps in a fixed sequence where each step's output is the next step's input. For *dependent* steps.
- **LCEL** - LangChain Expression Language: the `prompt | llm | parser` pipe syntax that composes `Runnable`s left-to-right. A Unix pipe / `Stream` chain / `Function.andThen` for LLM steps.
- **router** - a workflow that classifies the input and dispatches it to exactly one of several specialist handlers. Spring MVC dispatch / Strategy pattern.
- **conditional edge** - the LangGraph mechanism (`add_conditional_edges`) where a routing function reads state and returns the key of the next node. The router's dispatch.
- **fan-out** - splitting one input into multiple independent tasks that run concurrently.
- **fan-in** - joining the concurrent tasks back into one combined result.
- **`asyncio.gather`** - awaits multiple coroutines concurrently and returns their results **in argument order**. `ExecutorService.invokeAll` / `CompletableFuture.allOf(...).join()`.
- **`asyncio.to_thread`** - runs a **blocking** function on a worker thread and `await`s it, so it does not freeze the single event loop. The bridge that makes blocking `llm.invoke` safe inside async code. `ExecutorService.submit(blockingCall)`.

---

## What to build (see exercises.md)

The Phase 4 checklist, restated:

- [ ] Build a 3-step LCEL prompt chain.
- [ ] Create a router with 3 specialist branches.
- [ ] Run 3+ LLM calls in parallel with `asyncio.gather`.
- [ ] Build a document analyzer combining all patterns.

The runnable, offline-first versions of the three patterns live in `code/`. Work through them, then do the exercises without peeking - they push you to the capstone document analyzer.
