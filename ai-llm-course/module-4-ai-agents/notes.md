# MODULE 4: AI Agents — Complete Notes

> **For:** Engineers who completed Modules 0-3 and are ready for the paradigm shift.  
> **Key insight:** An agent is an LLM in a loop that can THINK, DECIDE, and ACT.
> Instead of getting one response, the LLM reasons step-by-step and uses tools.

---

# LESSON 4.1: What Are AI Agents and Why They Exist

## The Limitation of Basic LLM Calls

Everything we've built so far follows a simple pattern:

```
User Question → LLM → Answer

One shot. One response. Done.
```

This breaks down for complex tasks:

```
"Book me a flight from NYC to London next Friday under $500,
 then find a hotel near the conference venue,
 and add both to my calendar."

A single LLM call can't do this because:
  ❌ It can't search flight APIs
  ❌ It can't access hotel databases
  ❌ It can't write to your calendar
  ❌ It can't make decisions based on intermediate results
  ❌ It can't handle errors and retry
```

---

## What is an AI Agent?

**Simple:** An AI agent is an LLM that can **think**, **decide what to do next**, 
**use tools**, and **repeat** until the task is done.

**One sentence:** An agent = LLM + Tools + Loop.

```
┌─────────────────────────────────────────────────────────┐
│                   AI AGENT                               │
│                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│   │  THINK   │ ──▶│  DECIDE  │──▶│   ACT    │         │
│   │          │    │          │    │          │         │
│   │ "What do │    │ "I need  │    │ Call the │         │
│   │  I need  │    │  to use  │    │ search   │         │
│   │  to do?" │    │  search" │    │ tool"    │         │
│   └──────────┘    └──────────┘    └────┬─────┘         │
│        ▲                               │                │
│        │         ┌──────────┐          │                │
│        └─────────│ OBSERVE  │◀─────────┘                │
│                  │          │                           │
│                  │ "Search  │                           │
│                  │ returned │                           │
│                  │ 3 flights│                           │
│                  └──────────┘                           │
│                                                          │
│   This loop continues until the task is complete.       │
│   The LLM decides WHEN to stop.                        │
└─────────────────────────────────────────────────────────┘
```

**Java Analogy:** An agent is like a **Spring Batch job** with a smart controller.
Instead of predefined steps, the LLM dynamically decides what step to run next, 
which "service" (tool) to call, and whether the job is complete.

---

## Agent vs Chatbot vs RAG

```
┌──────────┬─────────────────────────────────────────────┐
│          │  What it does                                │
├──────────┼─────────────────────────────────────────────┤
│ Chatbot  │  LLM answers from training data.            │
│          │  One question → one answer.                 │
│          │  No tools, no actions.                      │
│          │  Example: "What is Java?"                   │
├──────────┼─────────────────────────────────────────────┤
│ RAG      │  LLM answers from YOUR data.                │
│          │  Search docs → paste → answer.              │
│          │  Read-only, no actions.                     │
│          │  Example: "What's in our wiki?"             │
├──────────┼─────────────────────────────────────────────┤
│ Agent    │  LLM TAKES ACTIONS in the real world.       │
│          │  Think → decide → act → observe → repeat.   │
│          │  Uses tools, multi-step, autonomous.        │
│          │  Example: "Deploy my PR to staging"         │
└──────────┴─────────────────────────────────────────────┘

Evolution:  Chatbot  →  RAG  →  Agent
            (talks)    (reads)  (acts)
```

---

# LESSON 4.2: Agent Architecture

## The ReAct Pattern (Reason + Act)

The most important agent pattern. Published by Google in 2022.

```
┌─────────────────────────────────────────────────────────┐
│  ReAct: REASON + ACT                                    │
│                                                          │
│  User: "What's the weather in Tokyo AND convert the     │
│         temperature from Celsius to Fahrenheit"          │
│                                                          │
│  ┌──── LOOP ITERATION 1 ────────────────────────────┐  │
│  │ THOUGHT: I need to find the weather in Tokyo.     │  │
│  │          I'll use the weather tool.               │  │
│  │ ACTION:  weather_tool("Tokyo")                    │  │
│  │ OBSERVATION: Temperature is 22°C, sunny           │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──── LOOP ITERATION 2 ────────────────────────────┐  │
│  │ THOUGHT: Got 22°C. Now I need to convert to      │  │
│  │          Fahrenheit. I'll use the calculator.     │  │
│  │ ACTION:  calculator("22 * 9/5 + 32")             │  │
│  │ OBSERVATION: 71.6                                 │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──── LOOP ITERATION 3 ────────────────────────────┐  │
│  │ THOUGHT: I have both pieces of information.       │  │
│  │          I can now give the final answer.         │  │
│  │ FINAL ANSWER: Tokyo is 22°C (71.6°F), sunny.     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## OpenAI Function Calling — How Agents Actually Work

Function calling is the **mechanism** that powers agents. The LLM doesn't literally 
"call" functions. Instead:

```
┌─────────────────────────────────────────────────────────┐
│  HOW FUNCTION CALLING WORKS                              │
│                                                          │
│  Step 1: You tell the LLM what tools exist              │
│                                                          │
│  tools = [                                               │
│    {                                                     │
│      "name": "get_weather",                              │
│      "description": "Get weather for a city",           │
│      "parameters": {                                     │
│        "city": {"type": "string"}                       │
│      }                                                   │
│    }                                                     │
│  ]                                                       │
│                                                          │
│  Step 2: LLM DECIDES to use a tool                      │
│  (it returns a function call instead of text)            │
│                                                          │
│  LLM Response: {                                         │
│    "function_call": {                                    │
│      "name": "get_weather",                              │
│      "arguments": "{\"city\": \"Tokyo\"}"               │
│    }                                                     │
│  }                                                       │
│                                                          │
│  Step 3: YOUR CODE executes the function                │
│  result = get_weather("Tokyo")  # YOU run this          │
│                                                          │
│  Step 4: Feed the result back to the LLM                │
│  LLM sees the result and decides what to do next.       │
│                                                          │
│  CRITICAL: The LLM NEVER executes code.                 │
│  It only TELLS you what to call. YOU execute it.        │
│  This keeps you in control.                              │
└─────────────────────────────────────────────────────────┘
```

**Java Analogy:** Function calling is like **Spring's Dependency Injection**.
The controller (LLM) declares what it needs (`@Autowired WeatherService`), 
and the framework (your agent loop) provides the actual implementation.
The controller never creates the service itself — it just declares intent.

---

## Agent Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                   AGENT ARCHITECTURE                      │
│                                                           │
│  User Input: "Analyze our Q3 sales data"                 │
│       │                                                   │
│       ▼                                                   │
│  ┌────────────────────────────────────┐                  │
│  │         AGENT LOOP                 │                  │
│  │                                    │                  │
│  │  ┌──────────┐                     │                  │
│  │  │   LLM    │◀── System Prompt    │                  │
│  │  │ (Brain)  │    (role + rules)   │                  │
│  │  │          │                     │                  │
│  │  │ Decides: │    ┌────────────┐   │                  │
│  │  │ • Think  │───▶│ Tool Call  │   │                  │
│  │  │ • Act    │    └─────┬──────┘   │                  │
│  │  │ • Finish │          │          │                  │
│  │  └──────────┘          ▼          │                  │
│  │       ▲         ┌────────────┐    │                  │
│  │       │         │  EXECUTOR  │    │                  │
│  │       │         │ (your code)│    │                  │
│  │       │         └─────┬──────┘    │                  │
│  │       │               │           │                  │
│  │       │               ▼           │                  │
│  │       │    ┌──────────────────┐   │                  │
│  │       │    │     TOOLS        │   │                  │
│  │       │    ├──────────────────┤   │                  │
│  │       │    │ 🔍 search_db()  │   │                  │
│  │       │    │ 📊 run_sql()    │   │                  │
│  │       │    │ 📧 send_email() │   │                  │
│  │       │    │ 📁 read_file()  │   │                  │
│  │       │    │ 🌐 web_search() │   │                  │
│  │       │    └──────┬───────────┘   │                  │
│  │       │           │               │                  │
│  │       └───────────┘               │                  │
│  │       (result fed back)           │                  │
│  │                                    │                  │
│  │  Loop continues until LLM says    │                  │
│  │  "I have the final answer"        │                  │
│  └────────────────────────────────────┘                  │
│       │                                                   │
│       ▼                                                   │
│  Final Answer to User                                    │
└──────────────────────────────────────────────────────────┘
```

---

## Types of Agents

```
┌─────────────────────────────────────────────────────────┐
│  AGENT TYPES (from simple to complex)                   │
│                                                          │
│  1. REACTIVE AGENT                                      │
│     └─ Responds to current input only                   │
│     └─ No planning, no memory                           │
│     └─ Like a switch-case: input → action               │
│     └─ Example: Simple customer support router          │
│                                                          │
│  2. ReAct AGENT (Reason + Act)                          │
│     └─ Thinks before acting                             │
│     └─ Uses tools in a loop                             │
│     └─ Most common and practical type                   │
│     └─ Example: Research assistant                      │
│                                                          │
│  3. PLANNING AGENT                                      │
│     └─ Creates a plan BEFORE acting                     │
│     └─ Executes steps, adjusts plan if needed          │
│     └─ Better for complex multi-step tasks              │
│     └─ Example: "Plan and execute a data migration"     │
│                                                          │
│  4. MULTI-AGENT SYSTEM                                  │
│     └─ Multiple specialized agents collaborate          │
│     └─ Orchestrator delegates to worker agents          │
│     └─ Example: "Researcher + Writer + Editor"          │
│     └─ Covered in Module 6                              │
└─────────────────────────────────────────────────────────┘
```

---

## Tool Design Principles

```
┌─────────────────────────────────────────────────────────┐
│  DESIGNING TOOLS FOR AGENTS                              │
│                                                          │
│  1. CLEAR NAMES                                          │
│     ❌ process_data()                                    │
│     ✅ search_customer_orders()                          │
│                                                          │
│  2. CLEAR DESCRIPTIONS                                   │
│     The LLM reads the description to decide when to     │
│     use the tool. Be specific!                          │
│     ❌ "Processes data"                                  │
│     ✅ "Search customer orders by customer ID, date      │
│         range, or product name. Returns order details."  │
│                                                          │
│  3. SIMPLE PARAMETERS                                    │
│     ❌ Complex nested objects                            │
│     ✅ Flat, well-typed parameters with defaults         │
│                                                          │
│  4. CLEAR RETURN VALUES                                  │
│     Return structured data the LLM can understand.      │
│     ❌ Raw database rows                                 │
│     ✅ Formatted summary with key fields                 │
│                                                          │
│  5. ERROR HANDLING                                       │
│     Return errors as strings, not exceptions.           │
│     The LLM needs to understand what went wrong         │
│     to decide what to do next.                          │
│     ✅ "Error: Customer ID 'abc' not found. Try a       │
│         valid numeric customer ID."                     │
│                                                          │
│  Java Analogy: Like designing a REST API —              │
│  clear endpoints, good docs, typed parameters.          │
└─────────────────────────────────────────────────────────┘
```

---

# LESSON 4.3: The Agent Loop — Core Implementation

The agent loop is deceptively simple:

```python
# PSEUDOCODE — The Agent Loop
while True:
    # 1. Ask LLM: "What should I do next?"
    response = llm.chat(messages, tools=available_tools)
    
    # 2. Check if LLM wants to use a tool
    if response.has_tool_call:
        # 3. Execute the tool (YOUR code runs)
        result = execute_tool(response.tool_call)
        
        # 4. Feed result back to LLM
        messages.append(tool_result=result)
        
    else:
        # 5. LLM is done — return the final answer
        return response.text
```

That's it. **Five lines of core logic.**  
Everything else (error handling, timeouts, guardrails) is production polish.

---

# LESSON 4.4: Code Examples

See the `code/` directory:

1. **`01_function_calling.py`** — OpenAI function calling from scratch
2. **`02_agent_loop.py`** — Build a complete agent loop (no frameworks)
3. **`03_planning_agent.py`** — Agent that plans before acting
4. **`04_research_agent.py`** — **PROJECT:** Multi-tool research agent

---

# LESSON 4.5: Exercises

## Exercise 1: Concept Check
1. What's the difference between a chatbot, RAG system, and an agent?
2. Explain the ReAct pattern in your own words.
3. Why doesn't the LLM execute tools directly?
4. Name 3 tool design principles.

## Exercise 2: Build Tools
1. Design 5 tools for an e-commerce agent (search products, check inventory, etc.)
2. Write the tool definitions (name, description, parameters)
3. Implement the tools as Python functions

## Exercise 3: Build an Agent
1. Create a "DevOps Agent" with tools: check_service_health, get_logs, restart_service
2. Use the agent loop from `02_agent_loop.py` as a starting point
3. Test with: "Service X is slow, investigate and fix it"

---

# LESSON 4.6: Interview Questions & Answers

## Q1: What is an AI agent and how does it differ from a chatbot?

**Answer:** An AI agent is an LLM-powered system that can reason, plan, and take actions
autonomously using tools. Unlike a chatbot (single question → single answer), an agent
operates in a loop: it thinks about what to do, executes an action (tool call), observes
the result, and repeats until the task is complete. The key difference is **autonomy** —
the agent decides what actions to take, which tools to use, and when the task is done.
A chatbot just generates text; an agent generates text AND takes actions.

## Q2: Explain the ReAct pattern and why it's important.

**Answer:** ReAct (Reason + Act) is an agent pattern where the LLM alternates between
reasoning steps and action steps. In each iteration: (1) **Thought** — the LLM reasons
about the current state and what to do next, (2) **Action** — the LLM chooses a tool to
call with specific arguments, (3) **Observation** — the tool's result is fed back to the
LLM. This is important because it makes the agent's reasoning transparent (you can see
WHY it chose each action), it breaks complex tasks into manageable steps, and it allows
the agent to adapt based on intermediate results.

## Q3: How does OpenAI function calling work under the hood?

**Answer:** Function calling has 4 steps: (1) You define available tools as JSON schemas
(name, description, parameters), (2) You send the user's message along with tool definitions
to the LLM, (3) The LLM decides whether to respond with text OR a tool call — if it
returns a tool call, it specifies the function name and arguments as JSON, (4) YOUR code
executes the actual function, then you send the result back to the LLM. Critically, the
LLM never executes code — it only generates the *intent* to call a function. You maintain
control of execution, which is essential for security and reliability.

## Q4: How do you handle agent failures and infinite loops?

**Answer:** Production safeguards: (1) **Max iterations** — cap the loop at 10-15 iterations,
(2) **Timeout** — overall execution time limit (e.g., 60 seconds), (3) **Tool error
handling** — return errors as strings so the LLM can adapt, (4) **Cost monitoring** — track
tokens and abort if exceeding budget, (5) **Guardrails** — validate tool inputs before
execution (e.g., don't allow DELETE queries on production DB), (6) **Human-in-the-loop** —
for high-risk actions (send email, deploy code), ask for confirmation.

## Q5: What makes a good tool definition for an agent?

**Answer:** Five principles: (1) **Clear name** — `search_customer_orders` not
`process_data`, (2) **Detailed description** — the LLM reads this to decide WHEN to use
it, so be specific about what it does and returns, (3) **Simple parameters** — flat,
well-typed fields with descriptions; avoid complex nested objects, (4) **Structured returns** —
return formatted strings the LLM can parse, not raw data, (5) **Graceful errors** —
return error messages as strings so the LLM can decide to retry or try something different.

## Q6: When should you use an agent vs RAG vs a simple LLM call?

**Answer:** Decision framework: **Simple LLM call** — when you just need text generation,
translation, or summarization. **RAG** — when you need to answer questions from a specific
knowledge base (read-only). **Agent** — when the task requires multiple steps, decision-making,
or taking actions (write operations, API calls, multi-system coordination). Rule of thumb:
if the task needs more than one tool call or involves non-trivial decision-making, use an
agent. If it's just "search and answer," use RAG.

---

# Common Mistakes

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| No max iterations | Agent loops forever | Set max_iterations=10 |
| Vague tool descriptions | LLM picks wrong tools | Write 2-3 sentence descriptions |
| Too many tools | LLM gets confused picking | Limit to 5-10 tools per agent |
| No error handling | Agent crashes on tool errors | Return errors as strings |
| No human approval | Agent takes destructive actions | Add confirmation for risky ops |
| Letting LLM run code | Security vulnerability | LLM DECIDES, you EXECUTE |

---

# Best Practices

1. **Start simple** — one tool, one task, then scale up
2. **Clear tool descriptions** — the LLM uses these to decide
3. **Max iterations** — always cap the agent loop (10-15 is good)
4. **Log everything** — thoughts, tool calls, results for debugging
5. **Handle errors gracefully** — return string errors, not exceptions
6. **Human-in-the-loop** — for destructive or costly actions
7. **Test adversarially** — try to break your agent with edge cases
8. **Monitor costs** — agents make multiple LLM calls, costs add up
9. **Separate concerns** — one agent per domain, not one giant agent
10. **Version your tools** — changing tool signatures breaks existing agents

---

**Next Module:** [Module 5 — MCP (Model Context Protocol) →](../module-5-mcp/)

Say **NEXT** to continue.
