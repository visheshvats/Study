# Phase 1 — LLM & Prompt Foundations

> **Duration:** 1 week
> **Goal:** Deep understanding of how LLMs work, prompting techniques, streaming, and function calling.

---

## Why this matters

If you take away one sentence from this whole phase, make it this:

> **An LLM API call is a stateless pure function. You resend the entire conversation history on every single call. There is no server-side session.**

Coming from Spring Boot, your instinct is wrong here, and the wrong instinct will cost you days of debugging. In a Spring app, when a user logs in you stash their state in an `HttpSession`, the servlet container hands you a `JSESSIONID` cookie, and on the next request you just reach for `session.getAttribute("user")`. The server *remembers*. State lives on the server, keyed by a session ID.

The Anthropic API does **none** of that. Think of `client.messages.create(...)` as a method like this:

```java
// Mental model — the LLM as a pure function
String reply = llm.complete(systemPrompt, fullMessageHistory, temperature);
```

Every call is independent. The model has no memory of your previous call. If you want it to "remember" that the user said their name is Alice three turns ago, **you** must include that turn in the `messages` array you send *this* time. Forget to do that and the model genuinely has no idea — not because it's broken, but because you never told it.

This is closer to a **stateless REST endpoint behind a load balancer** than to a stateful session bean. Imagine your Spring app is deployed across 50 pods with no sticky sessions and no shared session store. Each request could land on any pod, so each request must carry everything needed to process it. That discipline — "the request is self-contained" — is exactly the discipline the LLM forces on you. The `messages` list *is* the state, and you own it.

| Spring Boot world | LLM API world |
|---|---|
| `HttpSession` holds state server-side | No server state — you hold the `messages` list |
| `JSESSIONID` cookie identifies the session | Nothing identifies anything; every call is fresh |
| Server "remembers" the logged-in user | Model remembers nothing between calls |
| Stateful `@SessionScope` beans | Stateless function: `(system, messages, temperature) -> response` |
| You trust the container to persist state | You explicitly persist and resend state |

Get this mental model right and 80% of "why did the model forget?" bugs disappear before you write them.

---

## Core Concepts

Four knobs control every call. Learn what each one does.

### System prompt
The system prompt sets the model's persona, rules, and constraints. It is sent separately from the conversation (`system="..."`), not as a `user` message. Think of it as the **configuration / behavioral contract** for the call — analogous to a Spring `@Configuration` class or application properties that shape how a bean behaves, except it's natural language. It applies to the whole conversation, not a single turn.

> Rule of thumb: put *durable instructions* ("you are a support classifier, only return one category word") in the system prompt, and *the actual request* ("Why can't I export to PDF?") in a `user` message. Mixing them is a common beginner smell.

### Temperature
A float, typically `0.0`–`1.0`, controlling randomness.

- `temperature=0.0` — **deterministic-ish**. Same input tends to give the same output. Use for classification, extraction, JSON, routing — anything where you want a single correct answer.
- `temperature=1.0` — **creative / varied**. Use for brainstorming, copywriting, ideation.

For Java devs: think of it as a sampling strategy flag. Low temperature is like always picking the highest-confidence branch; high temperature lets the model explore lower-probability tokens. It is **not** a "smartness" dial — turning it up does not make the model better, just more varied.

### Context window
The maximum number of tokens (input + output combined) the model can consider in a single call. This is a hard ceiling, like a buffer size or a max payload limit on an endpoint. As your conversation grows, the `messages` array grows, and you consume more of the window on every call. Eventually you must **truncate, summarize, or window** old turns — you cannot grow history forever. (We'll engineer this properly in later phases; for now just internalize that the window is finite and you're paying for every token in it, in and out.)

### Stateless API
Covered above, but it bears repeating because it's the foundation: the API keeps **no state**. The conversation is a value you construct and resend. There is no `conversationId` that the server hydrates for you.

### Core Concepts diagram (reproduced)

The full Mermaid source lives in `diagrams.md`. In words: the **LLM** is the central node. Into it flow four inputs — **System Prompt** (personality/instructions), **User Messages** (the conversation history), **Temperature** (0 deterministic → 1 creative), and **Context Window** (max tokens in + out). Out of it comes a single **Response**, which may be plain text, a tool call, or both.

### Key terms (token)
A **token** is the unit the model reads and bills in — roughly 3–4 characters of English, or about ¾ of a word. "Tokenization" is the model's equivalent of splitting an input stream into lexer tokens before parsing. You pay per input token and per output token, and the context window is measured in tokens. When someone says "that prompt is too long," they mean too many tokens.

---

## 1.1 Basic LLM API Call & Multi-turn History

> Source code: `code/01_basic_llm_call.py`

The simplest call sends one user message and reads back text:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    temperature=temperature,
    system=system,
    messages=[{"role": "user", "content": user_message}],
)
return response.content[0].text
```

Note the shape: `system` is a top-level parameter, and `messages` is a list of `{"role": ..., "content": ...}` dicts. The response's `content` is a **list of blocks** (not a string) — `response.content[0].text` pulls the text out of the first block. This matters later: when tools are involved, `content` can contain multiple blocks of different types.

### Multi-turn: you manage history

Because the API is stateless, a "conversation" is just a growing list you maintain. The pattern is a strict alternation of roles:

```
[ {role: user, ...}, {role: assistant, ...}, {role: user, ...}, {role: assistant, ...}, ... ]
```

After each call you **must append the assistant's reply** to the list before sending the next user turn. If you skip that append, the model never sees its own previous answer, and the conversation silently loses coherence.

```python
def chat_with_history(messages: list[dict], system: str = "") -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system,
        messages=messages,        # full history every time!
    )
    assistant_reply = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_reply})  # don't forget this
    return assistant_reply
```

**Java analogy.** This is the *stateless REST* discipline. Each call is self-contained; the "session" is a `List<Message>` you carry on the client side and serialize into every request. There is no `@SessionAttribute` doing it for you. If you've ever built an API that's idempotent and horizontally scalable by pushing all state into the request body, you already think this way — you just have to apply it consciously here.

---

## 1.2 Prompt Engineering Patterns

> Source code: `code/02_prompt_patterns.py`

Three patterns you'll reach for constantly. The clean way to think about them: each is a different **strategy** for shaping the system prompt, swapped in for the job at hand — like the Strategy pattern, where `ClassifierStrategy`, `ReasoningStrategy`, and `ExtractionStrategy` all implement the same "build a prompt" interface but encode different behavior.

### Few-shot prompting
Instead of describing the task abstractly, you *show* the model 2–5 worked examples (input → desired output) right in the system prompt, then give it a new input. The model pattern-matches against your examples. This dramatically improves consistency for classification and formatting tasks.

```text
Feedback: "The app crashes when I open settings"
Category: BUG

Feedback: "Would love a dark mode option"
Category: FEATURE_REQUEST

Return ONLY the category word.
```

**Java analogy.** Few-shot examples are your **unit-test fixtures, repurposed as documentation the model reads at runtime.** They pin down the contract by example the same way a parameterized test pins down expected behavior — except here the examples actively steer the output.

### Chain-of-thought (CoT)
You instruct the model to reason step by step before committing to an answer, often with an explicit format (`THOUGHT:` then `ANSWER:`). For multi-step or arithmetic problems, forcing the reasoning out loud measurably improves correctness, because the model "computes" in the visible tokens rather than guessing in one leap.

```text
Solve step by step.
THOUGHT: <your reasoning>
ANSWER: <final answer only>
```

The trade-off: more output tokens (slower, costs more). When you only need the final answer downstream, parse out the `ANSWER:` line and discard the thinking.

### Structured JSON output
You ask the model to return *only* valid JSON matching a schema, with no prose and no markdown fences. This turns free-text generation into something your code can deserialize — the bridge between "LLM speaks English" and "my service needs a typed object."

```text
Return ONLY valid JSON. No markdown code fences. No preamble.
Schema:
{ "name": string, "age": number | null, "skills": string[], "experience_years": number | null }
```

**Java analogy.** This is your **Jackson `ObjectMapper.readValue(json, Person.class)` boundary** — except the JSON producer is a probabilistic model, so you must defend the parse. Models frequently wrap JSON in ```` ```json ```` fences even when told not to, so always strip fences before parsing:

```python
def extract_json(text: str) -> dict:
    clean = re.sub(r"```json|```", "", text).strip()
    return json.loads(clean)
```

In production you'd go further: validate against a Pydantic model (your equivalent of a Bean Validation `@Valid` DTO) and retry on parse failure.

---

## 1.3 Streaming Responses

> Source code: `code/03_streaming_terminal.py` and `code/04_fastapi_streaming.py`

Without streaming, you wait for the *entire* response before seeing anything — for a long answer that's several seconds of a blank screen. Streaming delivers tokens as they're generated, so the UI fills in progressively (the ChatGPT typewriter effect). It doesn't make generation faster; it makes it *feel* faster by reducing time-to-first-token.

### Terminal streaming
The SDK exposes a context manager that yields text chunks:

```python
with client.messages.stream(model=..., max_tokens=1024, messages=[...]) as stream:
    for chunk in stream.text_stream:
        print(chunk, end="", flush=True)
```

### FastAPI SSE endpoint
To stream to a browser, you wrap the chunks in **Server-Sent Events (SSE)** — a simple one-way `text/event-stream` protocol where each event is `data: <payload>\n\n`. FastAPI's `StreamingResponse` takes a generator and pushes each yielded chunk down the wire. You terminate with a sentinel like `data: [DONE]\n\n` so the client knows to close.

```python
@app.post("/chat/stream")
async def chat_stream(request: StreamRequest):
    async def generate():
        for chunk in _stream():            # produced from the SDK stream
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Java analogy.** SSE is **exactly Spring's `SseEmitter`** (or a `Flux<ServerSentEvent>` in WebFlux). Same protocol, same `text/event-stream` content type, same "server pushes a sequence of events over one held-open HTTP connection" model. If you've returned an `SseEmitter` from a `@GetMapping`, you already know the client side.

**The event-loop trap.** FastAPI's async endpoints run on a single-threaded event loop (conceptually similar to a Netty/WebFlux event loop). The Anthropic SDK's `messages.stream(...)` is a **blocking, synchronous** iterator. If you iterate it directly inside an `async def` without offloading, you **block the event loop** and freeze every other concurrent request on that worker. The fix is to run the blocking stream in a thread (e.g. via `asyncio`'s executor / `run_in_threadpool`) and hand chunks back to the loop. This is the same sin as calling a blocking JDBC driver on a Netty event-loop thread in WebFlux — never block the loop.

---

## 1.4 Tool / Function Calling & the Agentic Loop

> Source code: `code/05_tool_calling_agent.py`

This is where an LLM stops being a chatbot and starts being an **agent**. Tool calling lets the model *request that your code run a function* and then continue reasoning with the result.

### How it works (the contract)
1. You declare available tools as JSON schemas (`name`, `description`, `input_schema`). This is the model's "API catalog."
2. You pass `tools=TOOLS` on the call.
3. The model decides — on its own — whether to answer directly or to call a tool. If it wants a tool, the response comes back with `stop_reason == "tool_use"` and a `tool_use` content block containing the tool `name`, the `input` arguments (already parsed to a dict), and a unique `id`.
4. **You** execute the corresponding function with those arguments. The model never runs anything itself — it only *asks*.
5. You append the assistant's `tool_use` turn **and** a `user` turn containing a `tool_result` block (matched by `tool_use_id`) carrying your function's output.
6. You call the model again. It now sees the result and either calls another tool or produces the final text answer.
7. Repeat until `stop_reason != "tool_use"`.

### The agentic loop
That repetition is the **agentic loop** — the heartbeat of every agent you'll build for the rest of this roadmap:

```python
while True:
    response = client.messages.create(model=..., tools=TOOLS, messages=messages)
    if response.stop_reason == "tool_use":
        # find the tool_use block, look up the function, run it
        tool_result = TOOL_REGISTRY[tool_block.name](**tool_block.input)
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": tool_block.id,
             "content": json.dumps(tool_result)}
        ]})
    else:
        return final_text(response)   # stop_reason != "tool_use" -> we're done
```

**Java analogy — two of them, both useful.**

- **Dependency injection / a callback registry.** `TOOL_REGISTRY` is a `Map<String, Function>` — your application context of available beans, keyed by name. The model says "I need the bean named `create_ticket`," and you look it up and invoke it. The model is the orchestrator; your registry is the IoC container handing back the right collaborator. You can swap a real implementation for a mock without the model knowing — exactly like injecting a stub `@Repository` in a test.
- **The loop itself** is a request-driven dispatch loop: receive a command (`tool_use`), dispatch to a handler, feed the result back, repeat until a terminal state. If you've written a command processor or a state machine that loops until it reaches a final state, the control flow is familiar.

The critical discipline: **the model drives, your code executes.** You provide capabilities (tools) and a registry; the model decides the sequence. That inversion of control — you don't call the model in a fixed script, the model calls *you* — is the conceptual leap from "API client" to "agent."

---

> ## ⚠️ Common Java-dev mistakes
>
> These are the traps that bite Spring developers specifically. Read them now; you'll recognize every one of them in your own code within a week.
>
> - **Forgetting to append assistant turns to history.** You call the model, read the text, send the next user message — but never appended the assistant's reply. The model loses the thread. The `messages` list must contain *both* sides of every prior turn. (No `HttpSession` is doing this for you.)
> - **Parsing JSON without stripping markdown fences.** The model wraps its JSON in ```` ```json ... ``` ```` and your `json.loads()` throws. Always run the fence-stripping `extract_json` (your defensive deserialization step) before parsing.
> - **Assuming the server keeps state.** "Why did it forget the user's name?" Because the API is stateless and you didn't resend that turn. There is no server-side session. You are the session store.
> - **Not handling `stop_reason == "tool_use"`.** You read `response.content[0].text` and crash with an `AttributeError`, because the first block is a `tool_use` block, not text. Always branch on `stop_reason` before assuming the response is text.
> - **Blocking the event loop while streaming.** Iterating the synchronous SDK stream directly inside an `async def` freezes the whole FastAPI worker. Offload the blocking iterator to a thread — same rule as never calling blocking JDBC on a WebFlux event-loop thread.
> - **Hardcoding API keys.** Never put `ANTHROPIC_API_KEY` in source. Load it from the environment (`python-dotenv` for local dev, real secrets manager in prod) — the same hygiene as not committing `application.properties` with a DB password.

---

## Key terms (glossary)

| Term | Meaning |
|---|---|
| **System prompt** | Top-level instruction setting persona/rules for the whole conversation; sent via `system=`, not as a user message. |
| **Temperature** | Randomness knob, ~`0.0`–`1.0`. Low = deterministic (classification/JSON); high = creative (brainstorming). |
| **Context window** | Max tokens (input + output) the model can process in one call. A hard ceiling; you must window/summarize long histories. |
| **Token** | The model's unit of text (~3–4 chars / ¾ word). Billing and the context window are measured in tokens. |
| **Few-shot** | Including 2–5 worked input→output examples in the prompt so the model pattern-matches the desired behavior. |
| **Chain-of-thought (CoT)** | Instructing the model to reason step by step before answering; improves multi-step accuracy at the cost of more tokens. |
| **Structured output** | Constraining the model to return parseable data (usually JSON matching a schema) instead of free prose. |
| **Streaming / SSE** | Delivering the response incrementally as tokens are generated. Over HTTP this uses Server-Sent Events (`text/event-stream`), the equivalent of Spring `SseEmitter`. |
| **Tool use (function calling)** | The model requesting that your code run a declared function, then continuing with the result. |
| **`stop_reason`** | Field on the response saying why generation stopped. `"tool_use"` means the model wants a tool run; otherwise the turn is complete. The loop condition for an agent. |
| **Agentic loop** | The repeated cycle of call model → run requested tool → feed result back → call again, until `stop_reason != "tool_use"`. The core control flow of every agent. |
