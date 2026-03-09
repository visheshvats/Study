# MODULE 6: Agentic AI Architecture (Advanced) — Complete Notes

> **For:** Engineers who built single agents (Module 4) and are ready to
> architect systems where multiple agents collaborate.
> **Key insight:** A single agent is a developer. A multi-agent system
> is a team — with roles, handoffs, and a manager.

---

# LESSON 6.1: Why Multi-Agent Systems?

## Single Agent Limitations

```
┌──────────────────────────────────────────────────────┐
│  SINGLE AGENT PROBLEMS                               │
│                                                       │
│  1. CONTEXT WINDOW OVERLOAD                          │
│     One agent handling research + writing + review    │
│     → system prompt is huge, tools are many           │
│     → LLM gets confused, picks wrong tools           │
│                                                       │
│  2. JACK OF ALL TRADES                               │
│     One prompt can't make the LLM a great researcher │
│     AND great writer AND great code reviewer.        │
│     Specialized prompts beat generic ones.            │
│                                                       │
│  3. NO SEPARATION OF CONCERNS                        │
│     One giant agent is a monolith — hard to test,    │
│     debug, and improve individual capabilities.       │
│                                                       │
│  4. HARD TO SCALE                                    │
│     Can't parallelize — everything is sequential.    │
│     Slow for complex tasks.                          │
│                                                       │
│  SOLUTION: Split into specialized agents that        │
│  collaborate — just like a real engineering team.     │
└──────────────────────────────────────────────────────┘
```

**Java Analogy:** A single agent is a **monolith** Spring Boot app doing everything.
Multi-agent is a **microservices architecture** — each service (agent) has a single
responsibility, communicates via well-defined interfaces, and can be scaled independently.

---

## Multi-Agent Paradigm

```
┌──────────────────────────────────────────────────────────┐
│  SINGLE AGENT (Monolith)       MULTI-AGENT (Microservices)│
│                                                           │
│  ┌───────────────────┐       ┌────────────────────┐     │
│  │  ONE GIANT AGENT  │       │   ORCHESTRATOR     │     │
│  │                   │       │   (decides flow)    │     │
│  │  • Research       │       └───┬─────┬──────┬───┘     │
│  │  • Write          │           │     │      │         │
│  │  • Code           │           ▼     ▼      ▼         │
│  │  • Review         │       ┌─────┐┌─────┐┌──────┐    │
│  │  • Fix            │       │Rsrch││Write││Review│    │
│  │  • Deploy         │       │Agent││Agent││Agent │    │
│  │                   │       └─────┘└─────┘└──────┘    │
│  │  15 tools         │       3 tools  2 tools 2 tools   │
│  │  1500-token prompt│       Focused prompts each       │
│  └───────────────────┘                                   │
│                                                           │
│  ❌ Confused          ✅ Specialized                     │
│  ❌ Hard to debug     ✅ Easy to debug                   │
│  ❌ Can't parallelize ✅ Parallelizable                  │
└──────────────────────────────────────────────────────────┘
```

---

# LESSON 6.2: Orchestration Patterns

## Pattern 1: Router (Dispatcher)

```
┌──────────────────────────────────────────────────────┐
│  ROUTER PATTERN                                       │
│                                                       │
│  A classifier agent routes requests to specialists.  │
│                                                       │
│  User Request                                        │
│       │                                               │
│       ▼                                               │
│  ┌──────────┐                                        │
│  │  ROUTER  │  "What kind of task is this?"          │
│  │  Agent   │                                        │
│  └──┬───┬───┘                                        │
│     │   │   └──────────────┐                         │
│     ▼   ▼                  ▼                         │
│  ┌──────┐ ┌──────┐    ┌──────┐                      │
│  │ Code │ │ Data │    │ DevOp│                       │
│  │ Agent│ │ Agent│    │ Agent│                       │
│  └──────┘ └──────┘    └──────┘                       │
│                                                       │
│  When to use:                                        │
│  • Customer support (route by category)              │
│  • Multi-domain assistants                           │
│  • API gateways for agents                           │
│                                                       │
│  Java Analogy: Spring Cloud Gateway routing          │
│  requests to different microservices.                │
└──────────────────────────────────────────────────────┘
```

## Pattern 2: Pipeline (Sequential Chain)

```
┌──────────────────────────────────────────────────────┐
│  PIPELINE PATTERN                                     │
│                                                       │
│  Agents run in sequence, each improving the output.  │
│                                                       │
│  Input                                                │
│    │                                                  │
│    ▼                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│  │ RESEARCH │──▶ │  WRITER  │──▶ │  EDITOR  │       │
│  │  Agent   │    │  Agent   │    │  Agent   │       │
│  │          │    │          │    │          │       │
│  │ Finds    │    │ Creates  │    │ Polishes │       │
│  │ facts    │    │ draft    │    │ final    │       │
│  └──────────┘    └──────────┘    └──────────┘       │
│                                       │              │
│                                       ▼              │
│                                   Final Output       │
│                                                       │
│  When to use:                                        │
│  • Content creation (research → write → edit)        │
│  • Data processing (extract → transform → validate)  │
│  • Code generation (plan → code → test → review)     │
│                                                       │
│  Java Analogy: Spring Batch steps —                  │
│  Reader → Processor → Writer                         │
└──────────────────────────────────────────────────────┘
```

## Pattern 3: Supervisor (Manager)

```
┌──────────────────────────────────────────────────────┐
│  SUPERVISOR PATTERN                                   │
│                                                       │
│  A manager agent delegates, reviews, and re-assigns. │
│                                                       │
│        ┌─────────────────────┐                       │
│        │    SUPERVISOR       │                       │
│        │  (Manager Agent)    │                       │
│        │                     │                       │
│        │ • Breaks down task  │                       │
│        │ • Assigns to workers│                       │
│        │ • Reviews output    │                       │
│        │ • Re-assigns if bad │                       │
│        └──┬──────┬──────┬───┘                       │
│           │      │      │                            │
│    assign ▼      ▼      ▼ assign                    │
│        ┌─────┐┌─────┐┌─────┐                        │
│        │ W1  ││ W2  ││ W3  │                        │
│        └──┬──┘└──┬──┘└──┬──┘                        │
│           │      │      │                            │
│    report ▼      ▼      ▼ report                    │
│        ┌─────────────────────┐                       │
│        │    SUPERVISOR       │                       │
│        │ Reviews all output  │                       │
│        │ "Is this good?"     │                       │
│        │ YES → combine       │                       │
│        │ NO → re-assign      │                       │
│        └─────────────────────┘                       │
│                                                       │
│  When to use:                                        │
│  • Complex tasks requiring quality control           │
│  • Tasks where outputs need integration              │
│  • When you need iteration (draft → review → fix)    │
│                                                       │
│  Java Analogy: Kubernetes controller loop —          │
│  observe state, decide action, take action, repeat.  │
└──────────────────────────────────────────────────────┘
```

## Pattern 4: Swarm (Handoff)

```
┌──────────────────────────────────────────────────────┐
│  SWARM PATTERN (OpenAI Swarm)                        │
│                                                       │
│  Agents hand off to each other dynamically.          │
│  No central controller — peer-to-peer.               │
│                                                       │
│  ┌───────┐  handoff  ┌────────┐  handoff  ┌───────┐│
│  │ Triage│──────────▶│ Tech   │──────────▶│Billing││
│  │ Agent │           │ Support│           │ Agent ││
│  │       │◀──────────│ Agent  │◀──────────│       ││
│  └───────┘  escalate └────────┘  escalate └───────┘│
│                                                       │
│  Each agent decides who should handle next.          │
│  Like a customer service call being transferred.     │
│                                                       │
│  When to use:                                        │
│  • Customer support with department handoffs         │
│  • Workflows with variable paths                     │
│  • When agents need peer-to-peer communication       │
│                                                       │
│  Java Analogy: Saga pattern in microservices —       │
│  each service decides the next step.                │
└──────────────────────────────────────────────────────┘
```

## Pattern 5: Parallel (Fan-Out/Fan-In)

```
┌──────────────────────────────────────────────────────┐
│  PARALLEL PATTERN                                     │
│                                                       │
│  Multiple agents work simultaneously on subtasks.    │
│                                                       │
│            ┌─────────────┐                           │
│            │ COORDINATOR │                           │
│            │ (splits work)│                           │
│            └──┬──┬──┬───┘                           │
│               │  │  │    fan-out                     │
│               ▼  ▼  ▼                                │
│           ┌──┐┌──┐┌──┐                               │
│           │A1││A2││A3│  (run in parallel)            │
│           └──┘└──┘└──┘                               │
│               │  │  │    fan-in                      │
│               ▼  ▼  ▼                                │
│            ┌─────────────┐                           │
│            │  AGGREGATOR │                           │
│            │(merges rslt)│                           │
│            └─────────────┘                           │
│                                                       │
│  When to use:                                        │
│  • Independent subtasks (search 5 sources at once)   │
│  • Speed-critical (3x faster with 3 parallel agents) │
│  • Multi-perspective analysis                        │
│                                                       │
│  Java Analogy: CompletableFuture.allOf() —           │
│  run tasks in parallel, join results.                │
└──────────────────────────────────────────────────────┘
```

### Pattern Decision Matrix

| Pattern | Complexity | Best For | Analogy |
|---------|-----------|----------|---------|
| Router | ⭐ | Multi-domain classification | API Gateway |
| Pipeline | ⭐⭐ | Sequential processing | Batch Job |
| Supervisor | ⭐⭐⭐ | Quality-critical tasks | Manager + Team |
| Swarm | ⭐⭐⭐ | Dynamic workflows, handoffs | Saga Pattern |
| Parallel | ⭐⭐⭐⭐ | Speed-critical, independent tasks | Fork-Join |

---

# LESSON 6.3: Agent Communication & State

## How Agents Share Information

```
┌──────────────────────────────────────────────────────┐
│  AGENT COMMUNICATION PATTERNS                        │
│                                                       │
│  1. MESSAGE PASSING (Direct)                         │
│     Agent A sends output directly to Agent B.        │
│     Simple, works for pipelines.                     │
│     ┌──────┐  message  ┌──────┐                     │
│     │  A   │──────────▶│  B   │                     │
│     └──────┘           └──────┘                     │
│                                                       │
│  2. SHARED STATE (Blackboard)                        │
│     All agents read/write to a shared state object.  │
│     Works for any pattern.                           │
│     ┌──────┐           ┌──────┐                     │
│     │  A   │─write──┐  │  B   │                     │
│     └──────┘        │  └──┬───┘                     │
│                  ┌──▼────▼──┐                        │
│                  │  SHARED  │                        │
│                  │  STATE   │                        │
│                  └──▲────▲──┘                        │
│     ┌──────┐        │  ┌──┴───┐                     │
│     │  C   │─read───┘  │  D   │                     │
│     └──────┘           └──────┘                     │
│                                                       │
│  3. EVENT BUS (Pub/Sub)                              │
│     Agents publish events, others subscribe.         │
│     Loosely coupled, scalable.                       │
│     ┌──────┐ publish  ┌─────────┐ notify ┌──────┐  │
│     │  A   │─────────▶│ EVENT   │───────▶│  B   │  │
│     └──────┘          │  BUS    │───────▶│  C   │  │
│                       └─────────┘        └──────┘  │
│                                                       │
│  Java Analogy:                                       │
│  1 = REST calls, 2 = Shared DB, 3 = Kafka topics    │
└──────────────────────────────────────────────────────┘
```

---

## State Management with TypedDict

```python
# The "shared state" that flows through the agent graph
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    """State shared between all agents in the system."""
    query: str                    # Original user request
    research_results: list[str]   # From research agent
    draft: str                    # From writer agent
    review_feedback: str          # From reviewer agent
    final_output: str             # Final result
    iteration: int                # Loop counter
    status: str                   # "researching" | "writing" | "reviewing" | "done"
```

This state object is the **single source of truth**. Each agent reads what it
needs and writes its contribution. Like a shared database in microservices.

---

# LESSON 6.4: LangGraph — Graph-Based Agent Orchestration

## What is LangGraph?

```
┌──────────────────────────────────────────────────────┐
│  LANGGRAPH                                           │
│                                                       │
│  A library for building agent workflows as GRAPHS.   │
│                                                       │
│  • Nodes = Actions (agent steps, tool calls)         │
│  • Edges = Transitions (what runs next)              │
│  • State = Shared data flowing through the graph     │
│                                                       │
│  Think of it as a flowchart that the code follows:   │
│                                                       │
│     START                                            │
│       │                                               │
│       ▼                                               │
│  ┌──────────┐                                        │
│  │ Research  │─────────────────┐                     │
│  └──────────┘                  │                     │
│       │                        │                     │
│       ▼                        │ if not enough       │
│  ┌──────────┐                  │                     │
│  │  Write   │                  │                     │
│  └──────────┘                  │                     │
│       │                        │                     │
│       ▼                        │                     │
│  ┌──────────┐  needs work     │                     │
│  │  Review  │─────────────────┘                     │
│  └──────────┘                                        │
│       │ approved                                     │
│       ▼                                               │
│      END                                              │
│                                                       │
│  Java Analogy:                                       │
│  LangGraph is like Spring State Machine —            │
│  define states, transitions, and actions.            │
└──────────────────────────────────────────────────────┘
```

## LangGraph Core Concepts

```
NODES     = Functions that process state
EDGES     = Connections between nodes
COND.EDGE = Branching based on state
COMPILE   = Creates a runnable graph
STATE     = TypedDict shared by all nodes

graph = StateGraph(AgentState)
graph.add_node("research", research_fn)
graph.add_node("write", write_fn)
graph.add_node("review", review_fn)

graph.add_edge(START, "research")
graph.add_edge("research", "write")
graph.add_conditional_edges("review", check_quality, {
    "approved": END,
    "needs_work": "write"
})
```

---

# LESSON 6.5: Frameworks Comparison

```
┌───────────────┬────────────────┬────────────────┬────────────────┐
│               │  LangGraph     │  CrewAI        │  AutoGen       │
├───────────────┼────────────────┼────────────────┼────────────────┤
│ Approach      │ Graph-based    │ Role-based     │ Conversation   │
│ Abstraction   │ Low-level      │ High-level     │ High-level     │
│ Control       │ Maximum        │ Framework      │ Moderate       │
│ Learning      │ Steeper        │ Easier         │ Moderate       │
│ Flexibility   │ Most flexible  │ Opinionated    │ Flexible       │
│ Production    │ Best suited    │ Growing        │ Good           │
│ Debug         │ Excellent      │ Moderate       │ Moderate       │
│ By            │ LangChain team │ Community      │ Microsoft      │
├───────────────┼────────────────┼────────────────┼────────────────┤
│ Java Analogy  │ Spring MVC     │ Spring Boot    │ Akka Actors    │
│               │ (full control) │ (opinionated)  │ (message-based)│
└───────────────┴────────────────┴────────────────┴────────────────┘

RECOMMENDATION:
  • Learning / full control → LangGraph
  • Quick prototype         → CrewAI
  • Microsoft ecosystem     → AutoGen
  • Production             → LangGraph (most mature)
```

---

# LESSON 6.6: Code Examples

See the `code/` directory:

1. **`01_router_pattern.py`** — Multi-domain router agent (classification + dispatch)
2. **`02_pipeline_pattern.py`** — Sequential pipeline (research → write → edit)
3. **`03_supervisor_pattern.py`** — Supervisor with quality control loop
4. **`04_content_pipeline.py`** — **PROJECT:** Full content production multi-agent system

---

# LESSON 6.7: Exercises

## Exercise 1: Design Patterns
1. For each pattern below, draw the agent graph and identify which orchestration pattern to use:
   - Customer support with routing to billing, tech, or sales
   - Automated code review (lint → security → style → summary)
   - Market research from 5 different sources simultaneously
2. What pattern would you use for a "write blog post" agent? Why?

## Exercise 2: Build a Multi-Agent System
1. Build a "Code Review Pipeline" with 3 agents: Linter, Security Checker, Reviewer
2. Each agent provides structured feedback
3. A supervisor decides if the code passes or needs changes

## Exercise 3: Compare Frameworks
1. Implement the same simple pipeline in both raw Python and with your preferred framework
2. Compare: lines of code, readability, debuggability
3. Which would you choose for production and why?

---

# LESSON 6.8: Interview Questions & Answers

## Q1: When should you use multi-agent over single-agent architecture?

**Answer:** Use multi-agent when: (1) **Too many tools** — a single agent with 15+ tools
gets confused; split into specialists with 3-5 tools each. (2) **Different expertise needed** —
a research task needs different prompting than a writing task; specialized system prompts
beat generic ones. (3) **Quality control** — you need one agent to check another's work
(writer → reviewer loop). (4) **Parallelism** — independent subtasks can run simultaneously.
(5) **Maintainability** — easier to update one specialist than a monolith agent. Use single
agent when the task is simple, few tools, and adding orchestration overhead isn't justified.

## Q2: Explain the 5 orchestration patterns and when to use each.

**Answer:** (1) **Router** — classifies input, routes to specialist. Use for multi-domain
assistants (support routing). (2) **Pipeline** — sequential chain of agents. Use for content
creation (research → write → edit). (3) **Supervisor** — manager delegates, reviews, re-assigns.
Use for quality-critical tasks with iteration. (4) **Swarm** — agents hand off to each other
peer-to-peer. Use for customer service with department transfers. (5) **Parallel** — multiple
agents work simultaneously on subtasks. Use for speed-critical independent tasks (search
5 sources at once).

## Q3: How do agents communicate in a multi-agent system?

**Answer:** Three patterns: (1) **Message passing** — direct output of Agent A becomes input
of Agent B. Simple, works for pipelines. (2) **Shared state** — all agents read/write a
common state object (TypedDict/dict). Like a shared database. Most flexible, used by
LangGraph. (3) **Event bus** — agents publish events, others subscribe. Most decoupled,
best for large systems. In practice, shared state (option 2) is most common because it's
simple and LangGraph uses this pattern natively.

## Q4: What is LangGraph and why would you use it?

**Answer:** LangGraph is a library from the LangChain team for building agent workflows
as directed graphs. Nodes are actions (agent steps), edges define transitions, and
conditional edges enable branching. Key benefits: (1) Visual workflow representation —
easy to reason about, (2) Built-in state management, (3) Support for cycles (loops for
iteration), (4) Checkpointing for long-running workflows, (5) Streaming support.
Use it when you need fine-grained control over agent flow, especially for production
systems with complex branching or iterative loops.

## Q5: How do you handle failures in multi-agent systems?

**Answer:** Strategies: (1) **Retry with backoff** — failed agent retries with exponential
delay. (2) **Fallback agent** — if specialist fails, route to a generalist. (3) **Circuit
breaker** — if an agent fails repeatedly, stop calling it (like Resilience4j). (4) **Supervisor
re-assignment** — supervisor detects failure, re-assigns to a different worker or adjusts
the approach. (5) **Graceful degradation** — return partial results with a note about what
failed. (6) **Max iterations** — prevent infinite loops in iterative patterns. (7) **Dead
letter queue** — log failed tasks for human review.

## Q6: Compare LangGraph, CrewAI, and AutoGen for production use.

**Answer:** **LangGraph**: Best for production — low-level control, graph-based flow,
excellent debugging, supports streaming and checkpointing. **CrewAI**: Best for rapid
prototyping — high-level abstractions, role-based agents, easier learning curve, but less
control. **AutoGen**: Best for conversation-heavy workflows — message-based agent
interactions, good for brainstorming/debate patterns. For production, I'd recommend
LangGraph because it gives maximum control over execution flow, has the most mature
production features (persistence, streaming), and is backed by the LangChain team.

---

# Common Mistakes

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| Multi-agent for simple tasks | Orchestration overhead, slower | Use single agent if <5 tools |
| No max iterations in loops | Infinite review → rewrite loop | Cap at 3-5 iterations |
| All agents see all tools | Confusion, wrong tool picks | Each agent gets only its tools |
| No shared state validation | Agents override each other's work | Define clear state ownership |
| Ignoring agent handoff errors | Lost context between agents | Log all handoffs for debugging |
| Giant supervisor prompt | Supervisor becomes a bottleneck | Keep supervisor logic simple |

---

# Best Practices

1. **Start with single agent** — only go multi-agent when you NEED it
2. **Single responsibility** — each agent does ONE thing well (3-5 tools max)
3. **Clear state contract** — define what each agent reads and writes
4. **Cap iterations** — supervisor loops should have max 3-5 cycles
5. **Log all handoffs** — trace which agent did what and why
6. **Test agents individually** — unit test each agent before integration
7. **Monitor costs** — multi-agent multiplies LLM calls (and costs)
8. **Graceful degradation** — partial results are better than total failure
9. **Keep the supervisor simple** — don't make the manager an expert
10. **Design for debuggability** — you WILL need to trace agent decisions

---

**Next Module:** [Module 7 — Memory in Agents →](../module-7-memory/)

Say **NEXT** to continue.
