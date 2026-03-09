# MODULE 8: Tool Calling and Function Calling (Deep Dive) — Complete Notes

> **For:** Engineers who've used basic function calling (Module 4) and need
> production-grade tool systems with error handling, validation, and frameworks.
> **Key insight:** In Module 4 we learned the basics. This module teaches you
> how to build tool calling systems that are **reliable, safe, and scalable**.

---

# LESSON 8.1: Function Calling Internals

## How the LLM "Chooses" a Tool

```
┌──────────────────────────────────────────────────────────┐
│  WHAT HAPPENS INSIDE FUNCTION CALLING                    │
│                                                           │
│  1. Your code sends:                                     │
│     • System prompt                                      │
│     • User message                                       │
│     • Tool definitions (JSON schemas)                    │
│                                                           │
│  2. The LLM sees tools as part of its prompt:            │
│     "You have these functions available:                  │
│      - get_weather(city: str): Get weather data          │
│      - calculate(expr: str): Evaluate math               │
│      Based on the user's message, decide if/which        │
│      function to call and generate the arguments."       │
│                                                           │
│  3. The LLM outputs structured JSON:                     │
│     {"name": "get_weather", "arguments": {"city":"Tokyo"}}│
│     (NOT a function call — just JSON text!)              │
│                                                           │
│  4. YOUR CODE parses the JSON and calls the function     │
│                                                           │
│  KEY INSIGHT: The LLM never executes anything.           │
│  It only generates text that LOOKS like a function call. │
│  You are responsible for execution and safety.           │
└──────────────────────────────────────────────────────────┘
```

## Tool Selection Factors

The LLM chooses tools based on:

```
┌──────────────────────────────────────────────────────┐
│  WHAT INFLUENCES TOOL SELECTION                      │
│                                                       │
│  1. TOOL NAME (40%)                                  │
│     "get_weather" → clearly for weather queries      │
│     "gw" → unclear, LLM may not use it              │
│                                                       │
│  2. DESCRIPTION (35%)                                │
│     Detailed description helps LLM decide when       │
│     to use this tool vs another                      │
│                                                       │
│  3. PARAMETER NAMES + DESCRIPTIONS (15%)             │
│     "city: The city name" vs "c: str"                │
│     Better names = better argument generation        │
│                                                       │
│  4. USER MESSAGE CONTEXT (10%)                       │
│     The actual question determines tool relevance    │
│                                                       │
│  TAKEAWAY: 75% of tool calling success comes from    │
│  how well you NAME and DESCRIBE your tools.          │
└──────────────────────────────────────────────────────┘
```

## tool_choice Parameter

```python
# Let LLM decide (default)
tool_choice="auto"

# Force LLM to use a specific tool
tool_choice={"type": "function", "function": {"name": "get_weather"}}

# Prevent LLM from using any tools
tool_choice="none"

# Force the LLM to call at least one tool (any tool)
tool_choice="required"
```

**Java Analogy:**
- `auto` = Spring `@Autowired` — container decides which bean to inject
- `{"type":"function",...}` = `@Qualifier("specific")` — force specific bean
- `"none"` = No injection, manual instantiation
- `"required"` = `@Autowired(required=true)` — must inject something

---

# LESSON 8.2: Advanced Patterns

## Pattern 1: Parallel Tool Calls

```
┌──────────────────────────────────────────────────────┐
│  PARALLEL TOOL CALLS                                  │
│                                                       │
│  The LLM can request MULTIPLE tools in one turn.     │
│  Your code executes them (potentially in parallel).  │
│                                                       │
│  User: "What's the weather in Tokyo and London?"     │
│                                                       │
│  LLM returns TWO tool calls:                         │
│  [                                                   │
│    {name: "get_weather", args: {city: "Tokyo"}},     │
│    {name: "get_weather", args: {city: "London"}}     │
│  ]                                                   │
│                                                       │
│  Your code runs both → sends both results back →     │
│  LLM combines into a single answer.                 │
│                                                       │
│  Execution options:                                  │
│  • Sequential: for i in tool_calls: execute(i)      │
│  • Parallel: asyncio.gather(*[execute(t) for t...]) │
│  • Thread pool: ThreadPoolExecutor.map(execute, ...) │
│                                                       │
│  Java Analogy: CompletableFuture.allOf()             │
│  Run independent tasks in parallel, join all.        │
└──────────────────────────────────────────────────────┘
```

## Pattern 2: Chained Tool Calls

```
┌──────────────────────────────────────────────────────┐
│  CHAINED TOOL CALLS                                   │
│                                                       │
│  Tool A's output feeds into Tool B's input.          │
│  The LLM naturally chains across iterations.         │
│                                                       │
│  User: "Get the weather in Tokyo and convert to F"   │
│                                                       │
│  Iteration 1:                                        │
│    LLM calls: get_weather(city="Tokyo")              │
│    Result: {"temp": 22, "unit": "celsius"}           │
│                                                       │
│  Iteration 2:                                        │
│    LLM calls: calculate(expr="22 * 9/5 + 32")       │
│    Result: {"result": 71.6}                          │
│                                                       │
│  Iteration 3:                                        │
│    LLM responds: "It's 22°C (71.6°F) in Tokyo."     │
│                                                       │
│  The agent loop handles this naturally — each        │
│  iteration the LLM decides the next step.            │
│                                                       │
│  Java Analogy: Spring Integration message chain.     │
│  Each processor transforms data for the next.        │
└──────────────────────────────────────────────────────┘
```

## Pattern 3: Conditional Tool Calls

```
┌──────────────────────────────────────────────────────┐
│  CONDITIONAL / FALLBACK TOOLS                        │
│                                                       │
│  1. CONDITIONAL: Different tools for different cases │
│                                                       │
│     if user asks about weather → get_weather()       │
│     if user asks to calc     → calculate()           │
│     if neither              → respond directly       │
│                                                       │
│  2. FALLBACK: Try tool A, if it fails, try tool B   │
│                                                       │
│     try:                                             │
│         result = primary_search(query)               │
│     except ToolError:                                │
│         result = backup_search(query)                │
│                                                       │
│  3. CONFIRMATION: Ask user before dangerous tools    │
│                                                       │
│     if tool is "delete_file":                        │
│         ask_user("Are you sure?")                    │
│         if confirmed: execute()                      │
│                                                       │
│  Java Analogy:                                       │
│  1 = Strategy pattern                                │
│  2 = Circuit breaker / fallback                      │
│  3 = @PreAuthorize security                          │
└──────────────────────────────────────────────────────┘
```

## Pattern 4: Dynamic Tool Registration

```
┌──────────────────────────────────────────────────────┐
│  DYNAMIC TOOLS                                       │
│                                                       │
│  Tools available change based on context:            │
│                                                       │
│  • User role: Admin gets delete tools, Viewer doesn't│
│  • Conversation state: "payment" tools only after    │
│    "checkout" step                                   │
│  • Environment: "deploy" tools only in staging       │
│                                                       │
│  def get_tools_for(user, state):                     │
│      tools = [search, calculate]  # Base tools       │
│      if user.is_admin:                               │
│          tools += [delete, modify]                   │
│      if state == "checkout":                         │
│          tools += [process_payment]                   │
│      return tools                                    │
│                                                       │
│  Java Analogy: Spring Security + SpEL               │
│  @PreAuthorize("hasRole('ADMIN')") on endpoints     │
└──────────────────────────────────────────────────────┘
```

---

# LESSON 8.3: Building a Tool Framework

## The Problem

```
┌──────────────────────────────────────────────────────┐
│  WITHOUT A FRAMEWORK (Module 4 approach)             │
│                                                       │
│  # Define tool schema manually (50 lines of JSON)    │
│  tools = [{"type": "function", "function": {...}}]   │
│                                                       │
│  # Map names to functions manually                   │
│  REGISTRY = {"get_weather": get_weather, ...}        │
│                                                       │
│  # Handle errors manually                            │
│  if fn_name in REGISTRY:                             │
│      try: result = REGISTRY[fn_name](**args)         │
│      except: ...                                     │
│                                                       │
│  PROBLEMS:                                           │
│  • Schema and implementation can drift               │
│  • Repetitive boilerplate                            │
│  • No validation                                     │
│  • Easy to miss error handling                       │
│                                                       │
│  WITH A FRAMEWORK                                    │
│                                                       │
│  @tool(description="Get weather for a city")         │
│  def get_weather(city: str) -> str:                  │
│      ...                                             │
│                                                       │
│  • Schema auto-generated from type hints             │
│  • Automatic registration                            │
│  • Built-in validation and error handling            │
│  • One decorator = done                              │
└──────────────────────────────────────────────────────┘
```

## Key Components of a Tool Framework

```
┌──────────────────────────────────────────────────────────┐
│  TOOL FRAMEWORK ARCHITECTURE                             │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  @tool DECORATOR                                  │    │
│  │  • Reads function signature (type hints)          │    │
│  │  • Reads docstring (becomes description)          │    │
│  │  • Generates JSON schema automatically            │    │
│  │  • Registers in ToolRegistry                      │    │
│  └──────────────┬───────────────────────────────────┘    │
│                  │                                        │
│  ┌──────────────▼───────────────────────────────────┐    │
│  │  TOOL REGISTRY                                    │    │
│  │  • Maps tool names → implementations              │    │
│  │  • Stores schemas for LLM                         │    │
│  │  • Supports dynamic add/remove                    │    │
│  └──────────────┬───────────────────────────────────┘    │
│                  │                                        │
│  ┌──────────────▼───────────────────────────────────┐    │
│  │  TOOL EXECUTOR                                    │    │
│  │  • Validates arguments against schema             │    │
│  │  • Executes function (with timeout)               │    │
│  │  • Catches and formats errors                     │    │
│  │  • Logs execution + timing                        │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  Java Analogy: Like Spring's @RequestMapping             │
│  • Annotations auto-register endpoints                   │
│  • Framework handles serialization, validation, errors   │
│  • You just write the business logic                     │
└──────────────────────────────────────────────────────────┘
```

---

# LESSON 8.4: Error Handling and Safety

## Error Handling Strategies

```
┌──────────────────────────────────────────────────────┐
│  TOOL ERROR HANDLING LEVELS                          │
│                                                       │
│  Level 1: BASIC (catch + message)                    │
│    try:                                              │
│        result = tool(**args)                         │
│    except Exception as e:                            │
│        result = {"error": str(e)}                    │
│                                                       │
│  Level 2: TYPED (different handling per error)       │
│    except TimeoutError: → retry                      │
│    except AuthError:    → re-authenticate            │
│    except NotFound:     → tell user                  │
│    except RateLimit:    → backoff + retry             │
│                                                       │
│  Level 3: RETRY (with exponential backoff)           │
│    @retry(max=3, backoff=2)                          │
│    def call_api(...):                                │
│        ...                                           │
│                                                       │
│  Level 4: CIRCUIT BREAKER (stop calling failing tool)│
│    if tool.failure_rate > 50%:                       │
│        skip tool, use fallback                       │
│                                                       │
│  Java Analogy: Resilience4j patterns                 │
│  @Retry, @CircuitBreaker, @RateLimiter              │
└──────────────────────────────────────────────────────┘
```

## Safety Measures

```
┌──────────────────────────────────────────────────────┐
│  TOOL SAFETY CHECKLIST                               │
│                                                       │
│  ✅ INPUT VALIDATION                                 │
│     • Validate types, ranges, formats                │
│     • Reject SQL injection, path traversal           │
│     • Sanitize before execution                      │
│                                                       │
│  ✅ AUTHORIZATION                                    │
│     • Check user permissions before tool execution   │
│     • Admin-only tools should verify role             │
│     • Log who called what                            │
│                                                       │
│  ✅ RATE LIMITING                                    │
│     • Max N calls per minute per tool                │
│     • Prevent LLM from spamming expensive APIs       │
│                                                       │
│  ✅ SANDBOXING                                       │
│     • Don't run eval() on arbitrary input            │
│     • File system tools: restrict to safe dirs       │
│     • Network tools: allowlist domains               │
│                                                       │
│  ✅ CONFIRMATION                                     │
│     • Destructive actions (delete, send) need confirm│
│     • Show preview before execution                  │
│                                                       │
│  ✅ AUDIT LOGGING                                    │
│     • Log: who, what tool, what args, result, time   │
│     • Immutable audit trail for compliance           │
│                                                       │
│  Java Analogy: Spring Security + Validation          │
│  @Valid, @PreAuthorize, @Audited                     │
└──────────────────────────────────────────────────────┘
```

---

# LESSON 8.5: Code Examples

See the `code/` directory:

1. **`01_parallel_tools.py`** — Parallel + chained tool call patterns
2. **`02_tool_framework.py`** — Build a @tool decorator framework from scratch
3. **`03_error_handling.py`** — Retry, circuit breaker, and fallback patterns
4. **`04_smart_assistant.py`** — **PROJECT:** Full tool framework with dynamic registration

---

# LESSON 8.6: Exercises

## Exercise 1: Parallel Execution
1. Build an agent that searches 3 different APIs simultaneously
2. Measure execution time vs sequential
3. Handle the case where one API fails but others succeed

## Exercise 2: Build a Framework
1. Create a `@tool` decorator that auto-generates JSON schemas from type hints
2. Add support for `@tool(require_confirm=True)` for dangerous operations
3. Build a tool registry with enable/disable per-user-role

## Exercise 3: Error Resilience
1. Build a tool that simulates random failures (30% fail rate)
2. Implement retry with exponential backoff
3. Add a circuit breaker that opens after 3 consecutive failures

---

# LESSON 8.7: Interview Questions & Answers

## Q1: How does function calling work internally? Does the LLM actually execute functions?

**Answer:** No, the LLM never executes anything. Function calling works in 4 steps:
(1) You send the user message + tool definitions (JSON schemas) to the LLM. (2) The LLM
generates structured JSON output with the tool name and arguments — this is just text
generation, not execution. (3) Your code parses the JSON, validates arguments, and
executes the actual function. (4) You send the function result back to the LLM, which
then generates a natural language response incorporating the data. The LLM's role is
purely to DECIDE which tool to call and generate arguments — all execution is your code.

## Q2: How do you handle parallel tool calls?

**Answer:** When the LLM returns multiple tool_calls in a single response, you can
execute them in parallel: (1) Check `message.tool_calls` for multiple entries. (2)
Execute using `asyncio.gather()` or `ThreadPoolExecutor` for I/O-bound tools. (3) Send
ALL results back in the same order, each with its matching `tool_call_id`. (4) The LLM
then synthesizes all results into one response. Important: each tool result message must
include the correct `tool_call_id` to match the original request. Parallel execution
reduces latency significantly — 3 API calls that take 1s each complete in ~1s instead of ~3s.

## Q3: What makes a good tool definition? How do you improve tool selection accuracy?

**Answer:** Tool selection is 75% determined by naming and description. Best practices:
(1) **Clear name** — `search_products` not `sp` or `search`. (2) **Detailed description**
(2-3 sentences) — explain WHEN to use this tool, not just what it does. (3) **Parameter
descriptions** — `"city": "The city name (e.g., 'Tokyo')"` with examples. (4) **Minimal
required params** — fewer params = less chance of errors. (5) **Distinguish similar tools**
— if you have `search_web` and `search_database`, descriptions must clarify when to use which.
(6) **Test with edge cases** — try ambiguous queries and see if the LLM picks the right tool.

## Q4: How do you handle tool errors in a production agent?

**Answer:** Layered strategy: (1) **Input validation** — validate arguments before execution
(types, ranges, injection attacks). (2) **Try/except** — catch specific exceptions and
return structured error JSON (not raw stack traces). (3) **Retry with backoff** — transient
failures (timeouts, rate limits) get 2-3 retries with exponential delay. (4) **Circuit
breaker** — if a tool fails repeatedly, stop trying and use a fallback. (5) **Graceful
degradation** — tell the LLM "this tool is unavailable" so it adapts its response.
(6) **Timeout** — set max execution time per tool call. (7) **Audit log** — log success
and failures for debugging.

## Q5: How do you prevent dangerous tool usage in production?

**Answer:** Multiple safety layers: (1) **Authorization per tool** — check user role
before executing (admin-only tools). (2) **Confirmation for destructive actions** —
delete, send email, deploy require explicit user confirmation. (3) **Sandboxing** —
file tools restricted to safe directories, no `eval()` on arbitrary input. (4) **Rate
limiting** — max 10 calls/minute per expensive tool. (5) **Input sanitization** —
prevent SQL injection, path traversal, command injection in arguments. (6) **Audit
trail** — immutable log of who called what tool with what arguments. (7) **Dynamic tool
filtering** — only expose tools appropriate for the user's role and current state.

## Q6: What is a tool framework and why build one?

**Answer:** A tool framework automates the repetitive parts of tool integration:
(1) **Auto-schema generation** — `@tool` decorator reads Python type hints and docstrings
to generate JSON schemas automatically, eliminating schema/code drift. (2) **Automatic
registration** — decorated functions are registered in a tool registry. (3) **Built-in
validation** — arguments are validated against schemas before execution. (4) **Error
handling** — standard try/except with structured error responses. (5) **Execution logging**
— timing, inputs, outputs logged automatically. Without a framework, you write ~50 lines
of boilerplate per tool. With a framework, it's one decorator.

---

# Common Mistakes

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| Trusting LLM-generated arguments | LLMs hallucinate args | Validate all inputs before execution |
| No timeout on tool calls | One slow API blocks everything | Set timeouts (5-30s per tool) |
| Exposing all tools to all users | Security risk | Filter tools by user role |
| Raw stack traces in errors | LLM gets confused | Return structured error JSON |
| No retry on transient failures | Flaky experience | Retry 2-3x with backoff |
| Manual schema + code maintenance | Drift causes bugs | Use @tool decorator for auto-generation |
| Sequential parallel-capable calls | Slow for multi-tool queries | Use asyncio/threading for parallel |

---

# Best Practices

1. **Name tools clearly** — 75% of selection accuracy is naming + description
2. **Validate all inputs** — the LLM can hallucinate any argument value
3. **Auto-generate schemas** — use decorators/type hints to prevent drift
4. **Set timeouts** — 10-30 seconds max per tool call
5. **Retry transient failures** — 2-3 retries with exponential backoff
6. **Circuit break** — stop calling broken tools after N failures
7. **Filter tools by context** — user role, conversation state, environment
8. **Confirm destructive actions** — delete/send/deploy need human approval
9. **Log everything** — tool calls, args, results, timing, errors
10. **Return structured errors** — `{"error": "Not found", "suggestion": "Try X"}` not stack traces

---

**Next Module:** [Module 9 — Build Production-Grade AI System →](../module-9-production/)

Say **NEXT** to continue.
