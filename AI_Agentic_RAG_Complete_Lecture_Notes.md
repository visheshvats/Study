# Generative AI, Agentic AI, RAG, Deep Agents, Safety, Evaluation, and LLM Gateways

## Comprehensive Study Notes from the Full Lecture Transcript

> **Scope.** These notes reconstruct the complete supplied lecture in its chronological order. The transcript describes a roughly **10.5-hour** course, despite the request referring to an 8-hour lecture. The notes therefore cover the entire supplied material: LangChain v1, LangGraph, MCP, traditional and vectorless RAG, deep agents, guardrails, LangSmith-based evaluation, and LLM gateways.

> **Normalization note.** Automatic-caption spellings have been standardized: *LangChain*, *LangGraph*, *Pydantic*, *Groq*, *Gemini*, *FAISS*, *PyMuPDF*, *ChromaDB*, *Tavily*, and *LiteLLM*. Exact package APIs and model names are version-sensitive; the lecture used the then-current LangChain v1-era interfaces.

## Table of Contents

1. [Course Roadmap and Architectural Theme](#1-course-roadmap-and-architectural-theme)
2. [Environment Setup with `uv`](#2-environment-setup-with-uv)
3. [LangChain v1: Models, Agents, Tools, Messages, and Structured Output](#3-langchain-v1-models-agents-tools-messages-and-structured-output)
4. [Middleware, Summarization, and Human Approval](#4-middleware-summarization-and-human-approval)
5. [LangGraph: Stateful Agent Workflows](#5-langgraph-stateful-agent-workflows)
6. [Model Context Protocol](#6-model-context-protocol)
7. [Traditional Retrieval-Augmented Generation](#7-traditional-retrieval-augmented-generation)
8. [Vectorless, Reasoning-Based RAG with PageIndex](#8-vectorless-reasoning-based-rag-with-pageindex)
9. [Deep Agents and Deep Research](#9-deep-agents-and-deep-research)
10. [Guardrails and AI Safety](#10-guardrails-and-ai-safety)
11. [Chatbot and RAG Evaluation with LangSmith](#11-chatbot-and-rag-evaluation-with-langsmith)
12. [LLM Gateways with LiteLLM](#12-llm-gateways-with-litellm)
13. [Integrated Production Architecture](#13-integrated-production-architecture)
14. [Glossary and Revision Checklist](#14-glossary-and-revision-checklist)

# 1. Course Roadmap and Architectural Theme

The lecture presents the modern AI-application stack as a sequence of increasing capability:

1. A plain **large language model (LLM)** maps a prompt to generated text.
2. A **tool-using agent** lets the model decide when external information or an action is required.
3. **LangGraph** makes the process explicit as a stateful graph with nodes, edges, branching, persistence, streaming, and interruption.
4. **MCP** standardizes how applications discover and invoke tools exposed by independent servers.
5. **RAG** injects authoritative external knowledge into generation without retraining the LLM.
6. **Vectorless RAG** replaces embedding similarity with LLM-guided traversal of a hierarchical document index.
7. **Deep agents** add planning, decomposition, subagents, file-backed context, and persistent work products.
8. **Guardrails** control unsafe inputs, outputs, and high-impact actions.
9. **Evaluation** measures correctness, relevance, grounding, and retrieval quality instead of relying on subjective impressions.
10. An **LLM gateway** centralizes provider access, routing, fallbacks, cost, caching, rate limits, and observability.

> **Generative AI application.** An application in which a model receives an instruction or prompt and generates an output from its learned parameters.

> **Agentic AI application.** An application in which an LLM does more than directly generate text: it selects tools, observes results, updates its working state, and continues until it can complete a task.

The recurring architectural principle is **separation of responsibilities**:

- The LLM performs language understanding, reasoning, and generation.
- Tools provide live data or execute operations.
- State and checkpoints preserve progress.
- Retrieval systems supply private or recent knowledge.
- Middleware and guardrails enforce policy around the workflow.
- Evaluation establishes measurable quality.
- A gateway manages access to many model providers.

## 1.1 Why a Plain LLM Is Insufficient

A standalone LLM has several limitations:

1. **Knowledge cutoff:** it cannot reliably know events after its training cutoff.
2. **Private knowledge gap:** it was not trained on an organization's internal HR, finance, policy, or product documents.
3. **Hallucination:** it may generate a plausible answer even when relevant knowledge is absent.
4. **No external action:** without tools, it cannot send an email, query a live API, update a record, or search current information.
5. **Weak control:** a single prompt-response call does not naturally provide branching, retries, approvals, or durable state.

Fine-tuning is not the universal answer. It can be expensive, operationally slow, and unsuitable for knowledge that changes frequently. RAG and tools keep knowledge or capabilities outside the model and make them available at inference time.

### Key Takeaways

- The lecture progresses from direct generation to controlled, stateful, tool-using systems.
- Agents do not eliminate the LLM; they wrap it in a decision-and-action loop.
- RAG addresses knowledge access, whereas fine-tuning primarily changes model behavior or learned patterns.
- Production readiness requires safety, evaluation, observability, and provider management in addition to prompting.

# 2. Environment Setup with `uv`

The implementation begins with **`uv`**, a fast Python project and package manager written in Rust.

> **Virtual environment.** An isolated Python environment whose interpreter and installed dependencies are separated from other projects.

## 2.1 Installation and Project Initialization

Install `uv` using the platform-specific command from its official installer, then initialize the repository:

```bash
uv init
```

This creates project metadata such as:

- `pyproject.toml`, containing the project definition and dependencies;
- a Python-version file;
- a default Python entry point such as `main.py`.

Create a virtual environment:

```bash
uv venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

The transcript sometimes calls the environment `venv`; the exact directory name depends on the command and local convention.

## 2.2 Dependency Management

The lecture's base dependency set includes integrations for multiple providers:

```text
langchain
langchain-community
langchain-openai
langchain-groq
langchain-google-genai
python-dotenv
```

Install a requirements file with:

```bash
uv add -r requirements.txt
```

Install a single package with:

```bash
uv add ipykernel
```

Unlike a bare `pip install`, `uv add` also updates project dependency metadata. The resulting versions can be inspected in `pyproject.toml` and the lock file.

## 2.3 API-Key Configuration

Keys for OpenAI, Google Gemini, Groq, LangSmith, Tavily, or PageIndex are placed in a `.env` file:

```dotenv
OPENAI_API_KEY=...
GOOGLE_API_KEY=...
GROQ_API_KEY=...
LANGSMITH_API_KEY=...
TAVILY_API_KEY=...
PAGEINDEX_API_KEY=...
```

Load them without hard-coding secrets:

```python
import os
from dotenv import load_dotenv

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
```

Security requirements omitted by a quick demo but necessary in real work:

1. Add `.env` to `.gitignore`.
2. Never print or commit live credentials.
3. Prefer a secret manager in deployment.
4. Scope and rotate keys.
5. Use separate credentials for development and production.

### Key Takeaways

- `uv init`, `uv venv`, and `uv add` provide a reproducible project workflow.
- `pyproject.toml` records the environment's declared dependencies.
- Provider credentials belong in environment variables, not source code.
- Model and framework APIs change; locking versions is essential for reproducibility.

# 3. LangChain v1: Models, Agents, Tools, Messages, and Structured Output

## 3.1 From an LLM Call to an Agent

A plain model performs:

$$
y = f_\theta(x),
$$

where $x$ is the prompt, $f_\theta$ is the model parameterized by learned weights $\theta$, and $y$ is generated text.

An agent introduces a policy that selects either a final answer or an external action:

$$
a_t = \pi_\theta(s_t), \qquad a_t \in \{\text{tool call},\ \text{final answer}\},
$$

where $s_t$ contains the conversation and tool observations available at step $t$.

> **Agent.** A model-centered system that autonomously decides whether it can answer directly or must invoke one or more tools, observes the returned context, and continues until it can produce a final response.

The lecture contrasts older, more manual ReAct-agent construction with LangChain v1's simpler `create_agent` interface.

## 3.2 Creating a Basic Agent

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5",
    tools=[],
    system_prompt="You are a helpful assistant.",
)
```

The conceptual graph initially contains only:

```text
START -> MODEL -> END
```

Define a Python function as a tool. Its name, type annotations, and docstring help the model understand when and how to call it:

```python
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"The weather in {city} is sunny."

agent = create_agent(
    model="openai:gpt-5",
    tools=[get_weather],
    system_prompt="You are a helpful assistant.",
)
```

Invocation uses a message-state dictionary:

```python
result = agent.invoke({
    "messages": [
        {"role": "user", "content": "What is the weather in New York?"}
    ]
})

final_text = result["messages"][-1].content
```

The resulting sequence is:

1. A `HumanMessage` contains the user's weather question.
2. An `AIMessage` requests the `get_weather` tool with a structured argument such as `{"city": "New York"}`.
3. A `ToolMessage` contains the function result.
4. A final `AIMessage` converts that observation into a natural-language answer.

This is a minimal **ReAct-style loop**:

$$
\text{Thought/decision} \rightarrow \text{Action} \rightarrow \text{Observation} \rightarrow \text{next decision}.
$$

## 3.3 Model Integration

The lecture demonstrates provider-specific integrations for OpenAI, Gemini, and Groq. The common abstraction lets application code call `.invoke()`, `.stream()`, and `.batch()` without changing its overall control flow.

Representative initialization patterns are:

```python
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

openai_model = ChatOpenAI(model="gpt-4o-mini")
gemini_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
groq_model = ChatGroq(model="qwen-qwq-32b")
```

The exact identifiers shown in a rapidly evolving lecture may be retired or renamed. The stable lesson is the adapter pattern: the application depends on a chat-model interface, while the integration package handles provider-specific requests.

### `invoke`: one request, one completed result

```python
response = openai_model.invoke("Hello, how are you?")
print(response.content)
```

The returned object is normally an `AIMessage`, not merely a string. It may include response metadata and token-usage metadata.

### `stream`: progressive output

```python
for chunk in openai_model.stream("Explain agentic AI in detail."):
    print(chunk.content, end="", flush=True)
```

Streaming reduces **perceived latency** because the user sees early tokens before the full response is complete. It does not necessarily reduce total generation time.

Let $t_0$ be request time, $t_1$ the first visible token, and $t_f$ completion time:

$$
\text{TTFT} = t_1 - t_0, \qquad
\text{total latency} = t_f - t_0.
$$

Streaming mainly improves the experience associated with **time to first token (TTFT)**.

### `batch`: independent requests together

```python
responses = openai_model.batch([
    "Why do parrots imitate sounds?",
    "What is retrieval-augmented generation?",
    "Define an AI agent.",
])
```

Batching is appropriate when inputs are independent. It is not a substitute for a multi-turn conversation in which later messages depend on earlier ones.

## 3.4 Explicit Tool Binding

Tools can also be bound directly to a model so the developer can inspect and execute tool calls manually:

```python
model_with_tools = openai_model.bind_tools([get_weather])
messages = [{"role": "user", "content": "Weather in Bengaluru?"}]

ai_message = model_with_tools.invoke(messages)
messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    tool_message = get_weather.invoke(tool_call)
    messages.append(tool_message)

final_message = model_with_tools.invoke(messages)
```

This makes the protocol visible:

- the model proposes a tool call;
- application code executes it;
- the result is correlated to the call through its tool-call identifier;
- the model receives the observation and generates the final response.

## 3.5 Message Types

> **Message.** A structured conversation object containing content, a role/type, and optional metadata such as identifiers, tool calls, and usage information.

The four central message types are:

| Type | Purpose | Typical producer |
| --- | --- | --- |
| `SystemMessage` | Defines behavior, constraints, role, or global instructions | Application developer |
| `HumanMessage` | Represents user input | User/application |
| `AIMessage` | Represents model output and possibly tool-call requests | LLM |
| `ToolMessage` | Returns the result of a particular tool call | Tool runtime |

```python
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)

messages = [
    SystemMessage(content="You are a concise AI tutor."),
    HumanMessage(content="Explain LangGraph."),
]

reply = openai_model.invoke(messages)
```

A message may carry metadata:

```python
message = HumanMessage(
    content="My name is Alice.",
    name="Alice",
    id="message-123",
)
```

For tool use, an `AIMessage` may have empty textual content but a nonempty `tool_calls` list. The associated `ToolMessage` must preserve the tool-call identifier so the model knows which observation answers which request.

## 3.6 Structured Output

Free-form text is unsuitable when downstream code expects stable fields. Structured output constrains the model response to a schema.

> **Structured output.** A model response that conforms to a declared schema, allowing downstream programs to consume named and typed fields rather than parse arbitrary prose.

### Pydantic: schema plus runtime validation

```python
from pydantic import BaseModel, Field

class Movie(BaseModel):
    title: str = Field(description="Movie title")
    year: int = Field(description="Release year")
    director: str = Field(description="Director name")
    rating: float = Field(description="Rating out of 10")

structured_model = openai_model.with_structured_output(Movie)
movie = structured_model.invoke("Provide details about Inception.")
```

Pydantic validates that, for example, `year` is an integer and `rating` is numeric. A nonconforming response either undergoes supported coercion or raises validation failure.

To retain the original provider message alongside the parsed object:

```python
structured_model = openai_model.with_structured_output(
    Movie,
    include_raw=True,
)
result = structured_model.invoke("Provide details about Inception.")

raw_message = result["raw"]
parsed_movie = result["parsed"]
parsing_error = result.get("parsing_error")
```

### Nested schemas

```python
from typing import Optional

class Actor(BaseModel):
    name: str
    role: str

class MovieDetails(BaseModel):
    title: str
    year: int
    cast: list[Actor]
    genres: list[str]
    budget_million_usd: Optional[float] = None
```

Nested models preserve the hierarchy of the domain. `cast` becomes a list of validated `Actor` objects rather than an ambiguous text block.

### `TypedDict`: lightweight typed dictionary

```python
from typing_extensions import TypedDict, Annotated

class MovieDict(TypedDict):
    title: Annotated[str, "Movie title"]
    year: Annotated[int, "Release year"]
    director: Annotated[str, "Director"]
    rating: Annotated[float, "Rating out of 10"]

typed_model = openai_model.with_structured_output(MovieDict)
```

`TypedDict` describes dictionary shape for type checkers and schema generation, but it does not provide Pydantic-style runtime validation by itself.

### Dataclasses

```python
from dataclasses import dataclass

@dataclass
class ContactInfo:
    name: str
    email: str
    phone: str
```

Dataclasses are convenient data containers. They are lighter than Pydantic models and do not inherently provide the same runtime validation behavior.

### Structured output from an agent

```python
agent = create_agent(
    model="openai:gpt-5",
    tools=[],
    response_format=ContactInfo,
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": (
            "Extract contact information: John Doe, "
            "john@example.com, +1-555-0100"
        ),
    }]
})

contact = result["structured_response"]
```

### Choosing a schema mechanism

| Mechanism | Runtime validation | Natural output | Best use |
| --- | ---: | --- | --- |
| Pydantic `BaseModel` | Yes | Model instance | External inputs, contracts, robust production validation |
| `TypedDict` | No intrinsic validation | Dictionary | Lightweight internal schemas |
| `dataclass` | No intrinsic validation | Dataclass instance | Simple typed containers and application-domain objects |

### Key Takeaways

- An agent is an LLM plus a controlled loop around tools and observations.
- Function docstrings and type annotations are part of the tool's machine-readable contract.
- `.invoke()`, `.stream()`, and `.batch()` solve different execution needs.
- Messages preserve roles, metadata, and tool-call correlation.
- Use Pydantic when runtime validation matters; use `TypedDict` or dataclasses for lighter-weight structure.
- Structured output is a programmatic interface, not merely nicer formatting.

# 4. Middleware, Summarization, and Human Approval

> **Agent middleware.** Logic inserted at defined lifecycle hooks to observe, transform, restrict, retry, interrupt, or otherwise control an agent's execution.

The lecture uses airport processing as an analogy. A passenger does not move directly from entrance to aircraft; security, immigration, and boarding checks intervene at specific points. Likewise, middleware adds controlled processing before or after an agent, model, or tool call.

Typical hooks include:

- before the agent starts;
- before the model is called;
- around or before a tool call;
- after a model call;
- after the agent finishes.

Middleware supports:

1. Logging, tracing, analytics, and debugging.
2. Prompt transformation.
3. Tool selection or restriction.
4. Output formatting.
5. Retries and provider fallbacks.
6. Early termination.
7. Model-call and tool-call limits.
8. Rate limits and cost controls.
9. PII detection and safety guardrails.
10. Conversation summarization.
11. Human approval of sensitive actions.

## 4.1 Built-In Middleware Families

The lecture names several reusable policies:

| Middleware | Purpose |
| --- | --- |
| Summarization | Compresses older conversation history near a message/token threshold |
| Human in the loop | Pauses before selected tool calls and requests approval |
| Model-call limit | Caps model invocations to control loops and cost |
| Tool-call limit | Caps tool execution |
| Model fallback | Tries an alternative model after failure |
| Tool retry | Repeats eligible failed calls |
| Tool selector | Restricts or chooses tools relevant to a request |
| To-do list | Tracks decomposed work |
| PII middleware | Detects and transforms sensitive data |

## 4.2 Summarization Middleware

Long-running conversations consume an increasing context window. If every historical message is retained verbatim, token usage and cost grow, and the model may eventually exceed its context limit.

Summarization preserves recent turns while compressing older turns:

$$
H_t = [m_1, m_2, \ldots, m_t]
\quad\longrightarrow\quad
H'_t = [S(m_1,\ldots,m_k),m_{k+1},\ldots,m_t],
$$

where $S$ is an LLM-produced summary.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[],
    checkpointer=InMemorySaver(),
    middleware=[
        SummarizationMiddleware(
            model="openai:gpt-4o-mini",
            trigger={"messages": 10},
            keep={"messages": 4},
        )
    ],
)
```

The lecture demonstrates four arithmetic questions. User and assistant turns increase the message count to the trigger; middleware then replaces older turns with a summary and keeps the four most recent messages. A separate example uses a token-count trigger and a hotel-search tool.

Important design choices:

- Use a lower-cost model for summarization when possible.
- Trigger early enough to leave space for the new query, tool output, and answer.
- Retain recent raw turns so local references remain precise.
- A summary is lossy; preserve durable facts separately when exact recall matters.
- Keep the same thread/checkpoint identity so the summarized state belongs to the correct conversation.

## 4.3 Human-in-the-Loop Middleware

> **Human in the loop (HITL).** A workflow pattern that pauses an automated process before a consequential operation and resumes only after a person approves, rejects, or edits the proposed action.

HITL is appropriate for sending messages, deleting records, transferring money, publishing content, or changing protected data. The system should show the proposed tool name and arguments—not merely ask “approve?” without context.

The lecture configures approval for selected tools while allowing harmless search to continue automatically. A typical pattern is:

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[search_web, send_email, delete_record],
    checkpointer=InMemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": True,
                "delete_record": True,
                "search_web": False,
            }
        )
    ],
)
```

Checkpointing is necessary because the process must preserve its exact state while paused and resume the same execution after the decision.

### Key Takeaways

- Middleware separates cross-cutting policy from core agent logic.
- Summarization controls context growth but is lossy, so it is not a substitute for exact persistent memory.
- Human approval should be required according to an action's impact, not for every call indiscriminately.
- Multiple middleware components can be stacked, but order matters because one layer may transform data seen by another.

# 5. LangGraph: Stateful Agent Workflows

## 5.1 Motivation

LangGraph represents an AI workflow as a graph rather than hiding all control flow inside one agent executor.

> **LangGraph.** A graph-based orchestration framework for building stateful, cyclic, branching, interruptible, and streamable LLM workflows and agents.

The lecture emphasizes four capabilities:

1. explicit graph structure;
2. state shared across nodes;
3. persistence/checkpointing;
4. advanced execution such as loops, streaming, and human interruption.

LangGraph is useful when a task is too complex for a single model call or a shallow tool loop. Examples include multi-step research, content pipelines, retrieval agents, and workflows requiring approvals.

## 5.2 Graph Primitives

> **Node.** A unit of computation, usually a Python function or runnable, that receives state and returns a state update.

> **Edge.** A transition defining which node executes next.

> **State.** The shared typed data structure available to nodes during one graph execution.

> **Reducer.** A function that combines a node's update with the existing state rather than simply overwriting it.

> **Conditional edge.** A transition selected at runtime by a routing function or condition.

A content workflow from the lecture can be represented as:

```text
START
  -> YouTube transcript extraction
  -> title generation
  -> content generation
  -> END
```

The transcript produced by the first node must be stored in graph state so later nodes can access it. This state is not automatically the same thing as cross-session, long-term memory.

## 5.3 State Schema and Reducers

The lecture builds a chatbot state with `TypedDict`, `Annotated`, and the `add_messages` reducer:

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

Without a reducer, a returned `messages` value may overwrite the previous value. With `add_messages`, new messages are merged/appended with message-aware semantics:

$$
M_{t+1} = \operatorname{add\_messages}(M_t, \Delta M_t).
$$

`Annotated` attaches reducer metadata to the state field. It does not itself perform the merge.

## 5.4 Building a Basic Chatbot Graph

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)

def chatbot(state: State):
    reply = model.invoke(state["messages"])
    return {"messages": [reply]}

builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile()
```

Execution:

```python
from langchain_core.messages import HumanMessage

result = graph.invoke({
    "messages": [HumanMessage(content="What is LangGraph?")]
})
```

Compilation validates and produces an executable graph. Visualizing `graph.get_graph()` is useful for verifying topology before execution.

The sequence is:

1. `START` receives initial state.
2. The `chatbot` node reads `state["messages"]`.
3. The model returns an `AIMessage`.
4. `add_messages` merges that update into state.
5. Control reaches `END`.

## 5.5 Tool-Calling Graph

The lecture extends the graph with multiple tools collected in a prebuilt `ToolNode` and uses `tools_condition` for routing.

```python
from langgraph.prebuilt import ToolNode, tools_condition

tools = [search_web, get_weather]
model_with_tools = model.bind_tools(tools)

def call_model(state: State):
    return {"messages": [model_with_tools.invoke(state["messages"])]}

builder = StateGraph(State)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

tool_graph = builder.compile()
```

The crucial final edge is `tools -> agent`, not `tools -> END`. A raw tool result is context, not necessarily a user-facing answer. Returning it to the model allows the model to interpret the observation, decide whether another tool is necessary, and then produce a final response.

The loop is:

$$
\text{model} \rightarrow
\begin{cases}
\text{tool node} \rightarrow \text{model}, & \text{if tool call exists},\\
\text{END}, & \text{otherwise}.
\end{cases}
$$

This graph may perform several model-tool cycles, so production systems should impose model-call/tool-call limits.

## 5.6 Checkpointing and Conversation Memory

The lecture adds an in-memory checkpoint saver:

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "user-thread-1"}}

graph.invoke(
    {"messages": [("user", "My favorite sport is cricket.")]},
    config=config,
)

graph.invoke(
    {"messages": [("user", "What sport do I like?")]},
    config=config,
)
```

> **Checkpoint.** A persisted snapshot of graph state associated with an execution identity, enabling later turns, recovery, inspection, and resumption.

`thread_id` separates conversations. Reusing it retrieves the existing state; changing it starts an independent thread. An in-memory saver is suitable for demonstration but is not durable across process restarts. Production use requires a persistent backend.

The lecture informally calls this “memory,” but three concepts should be distinguished:

| Concept | Lifetime | Example |
| --- | --- | --- |
| Graph state | Current execution | Messages and intermediate results |
| Checkpoint/thread memory | Across calls in one thread | Prior conversation turns |
| Long-term memory | Across threads/sessions/users as designed | User profile or durable knowledge store |

## 5.7 Streaming Graph Execution

LangGraph exposes synchronous and asynchronous streaming. The lecture contrasts stream modes such as `updates` and `values`.

```python
for event in graph.stream(
    {"messages": [("user", "Explain reducers.")]},
    config=config,
    stream_mode="updates",
):
    print(event)
```

- **`updates`** emits the delta returned after a node executes.
- **`values`** emits the complete current state after each step.
- Token/message-oriented modes can expose model output progressively when supported.
- Event streaming gives lower-level lifecycle events useful for tracing and custom interfaces.

For a three-node graph, if state updates are $\Delta S_1,\Delta S_2,\Delta S_3$:

$$
S_1 = R(S_0,\Delta S_1),\quad
S_2 = R(S_1,\Delta S_2),\quad
S_3 = R(S_2,\Delta S_3),
$$

where $R$ denotes the appropriate reducer. `updates` exposes the $\Delta S_i$; `values` exposes the $S_i$.

## 5.8 Human in the Loop with `interrupt` and `Command`

LangGraph can pause from inside a node or tool:

```python
from langgraph.types import interrupt, Command

def human_assistance(query: str) -> str:
    human_response = interrupt({"query": query})
    return human_response
```

The caller later resumes the same thread:

```python
graph.invoke(
    Command(resume="Approved. Continue with the recommendation."),
    config=config,
)
```

Operational sequence:

1. A node calls `interrupt(payload)`.
2. LangGraph checkpoints the current state.
3. Control returns to the application with an interruption payload.
4. The UI obtains human input.
5. The application sends `Command(resume=...)` using the same thread.
6. Execution resumes from the saved point.

Checkpoint durability and idempotent tools are important. If a process crashes near an external side effect, resumption must not accidentally execute the action twice.

### Key Takeaways

- Nodes perform work, edges control flow, state carries data, and reducers define merge semantics.
- Conditional edges make branching explicit and inspectable.
- In a ReAct graph, tool output should normally return to the model before termination.
- Checkpointers plus thread IDs provide multi-turn continuity and resumption.
- Streaming exposes either state deltas, complete states, tokens, or detailed events.
- `interrupt` and `Command(resume=...)` make approval a first-class graph operation.

# 6. Model Context Protocol

## 6.1 Purpose and Roles

> **Model Context Protocol (MCP).** A standardized protocol through which an AI host/client can discover and invoke capabilities—such as tools, resources, or prompts—exposed by independent MCP servers.

The lecture distinguishes three roles:

1. **MCP server:** exposes one or more capabilities, such as arithmetic or weather functions.
2. **MCP client:** establishes connections, discovers server tools, and converts them into objects usable by the agent framework.
3. **Host/application:** contains the LLM or agent and uses the client to access one or more servers.

The benefit is decoupling. A tool provider implements the MCP contract once; compatible clients can consume it without embedding provider-specific code into every agent.

The logical flow is:

```text
User -> Agent/LLM -> MCP client -> MCP server -> tool
                         ^                         |
                         +------ result ----------+
```

The LLM does not directly open a random server connection. The host controls discovery, permissions, transport, execution, and which returned tools are made available to the model.

## 6.2 Building a `FastMCP` Server

The lecture uses `FastMCP` to create servers with decorated Python functions.

### Math server over standard I/O

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

With **standard I/O (`stdio`) transport**, the client launches or attaches to a local subprocess and communicates through its input/output streams. It is convenient for local integrations because no listening network service is required.

### Weather server over streamable HTTP

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
def get_weather(location: str) -> str:
    """Return weather information for a location."""
    return f"It is raining in {location}."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

**Streamable HTTP** exposes a network endpoint, enabling a separately running service. The client must use the server's MCP URL, often ending in `/mcp` depending on configuration.

## 6.3 Multi-Server MCP Client

The lecture connects one local `stdio` server and one HTTP server using LangChain's MCP adapters.

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "math": {
        "command": "python",
        "args": ["math_server.py"],
        "transport": "stdio",
    },
    "weather": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    },
})

tools = await client.get_tools()
```

The discovered tools are then attached to a LangGraph ReAct agent:

```python
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

model = ChatGroq(model="qwen-qwq-32b")
agent = create_react_agent(model, tools)

result = await agent.ainvoke({
    "messages": [{
        "role": "user",
        "content": "What is (3 + 5) * 12?",
    }]
})

print(result["messages"][-1].content)
```

The client discovers tools from both servers. The agent selects the math tool for arithmetic and the weather tool for a location query.

## 6.4 Transport and Production Considerations

| Concern | `stdio` | Streamable HTTP |
| --- | --- | --- |
| Deployment | Local child process | Independent service |
| Network port | Not required | Required |
| Isolation | Process-local | Network/service boundary |
| Authentication | Usually host/process controls | Must be explicitly designed |
| Scaling | Tied to host | Can scale independently |
| Typical use | Desktop/local tool | Remote or shared tool service |

In production, MCP compatibility does not remove the need for:

- authentication and authorization;
- tool allowlists;
- schema and argument validation;
- timeouts, retries, and circuit breakers;
- audit logs;
- secrets isolation;
- output-size limits;
- human approval for consequential operations.

### Key Takeaways

- MCP standardizes tool exposure and discovery; it does not itself decide which tools an LLM should be allowed to use.
- `FastMCP` turns typed, documented Python functions into server tools.
- `stdio` is convenient locally; streamable HTTP supports independently deployed services.
- A multi-server client can aggregate tools and present them to one agent.
- Transport security and action authorization remain application responsibilities.

# 7. Traditional Retrieval-Augmented Generation

## 7.1 Definition and Motivation

> **Retrieval-augmented generation (RAG).** A method that retrieves information from an authoritative knowledge source outside the LLM's training parameters and supplies it as context before generation.

RAG addresses two lecture examples:

1. A model cannot know events after its training cutoff.
2. A model has not learned a startup's private HR, finance, or policy documents.

Rather than repeatedly fine-tune a large model whenever facts change, RAG keeps knowledge external and retrieves it at query time.

The two main pipelines are:

1. **Data-ingestion/indexing pipeline:** load, parse, chunk, embed, and store.
2. **Retrieval-generation pipeline:** embed the query, retrieve relevant chunks, construct a grounded prompt, and generate an answer.

## 7.2 End-to-End Architecture

### Ingestion

$$
D \xrightarrow{\text{load/parse}} \{d_i\}
\xrightarrow{\text{split}} \{c_j\}
\xrightarrow{E} \{\mathbf{v}_j\}
\xrightarrow{\text{store}} V,
$$

where:

- $D$ is the source corpus;
- $d_i$ is a loaded document or page;
- $c_j$ is a chunk;
- $E$ is an embedding model;
- $\mathbf{v}_j \in \mathbb{R}^d$ is the chunk vector;
- $V$ is a vector database or index.

### Retrieval and generation

$$
\mathbf{q}=E(q),
$$

$$
C_k(q)=\operatorname{TopK}_{c_j}\operatorname{sim}(\mathbf{q},\mathbf{v}_j),
$$

$$
y=\operatorname{LLM}(I,q,C_k(q)),
$$

where $I$ is the grounding instruction, $q$ is the user's query, and $C_k$ is the retrieved context.

## 7.3 Document Loading and LangChain's `Document`

Source data may be PDF, HTML, text, CSV, Excel, SQL, or another structured/unstructured format. The lecture focuses on text and PDF loaders.

```python
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    PyMuPDFLoader,
)

text_docs = TextLoader("data/notes.txt").load()
pdf_docs = PyMuPDFLoader("data/attention.pdf").load()
```

Each loaded object follows a document structure:

```python
Document(
    page_content="...text...",
    metadata={
        "source": "data/attention.pdf",
        "page": 3,
        # loader-specific fields may also appear
    },
)
```

> **Metadata.** Non-content attributes describing a document or chunk, such as source filename, page number, file type, author, section, or timestamp.

Metadata is critical for citations, filtering, debugging, and tracing an answer back to its source.

The lecture notes that PyMuPDF is often a stronger practical PDF parser than a basic PyPDF loader, although parser choice depends on layout, tables, scanned pages, and licensing/deployment needs.

## 7.4 Loading a Directory of PDFs

The modular example scans a directory, loads each PDF, and enriches metadata:

```python
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

def process_all_pdfs(pdf_directory: str):
    all_documents = []

    for pdf_path in Path(pdf_directory).glob("**/*.pdf"):
        documents = PyPDFLoader(str(pdf_path)).load()

        for doc in documents:
            doc.metadata["source_file"] = pdf_path.name
            doc.metadata["file_type"] = "pdf"

        all_documents.extend(documents)

    return all_documents
```

In the demonstration, four PDFs produce 64 page-level documents: an attention paper, an embeddings report, an object-detection document, and a one-page proposal.

## 7.5 Chunking

> **Chunking.** Dividing long documents into smaller, partially independent text units that fit embedding and LLM limits and can be retrieved individually.

The lecture uses `RecursiveCharacterTextSplitter`:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(documents)
```

The demonstration converts 64 page documents into approximately 359 chunks using `chunk_size=1000` and `chunk_overlap=200`.

Chunk overlap repeats a boundary region in adjacent chunks. If chunks are sequences $c_i$ and $c_{i+1}$ with overlap $o$:

$$
\operatorname{suffix}_o(c_i)=\operatorname{prefix}_o(c_{i+1}).
$$

Overlap reduces the risk that a fact spanning a boundary is separated, but it increases index size and redundant retrieval.

### Chunking trade-offs

- **Chunks too small:** lose surrounding context; retrieval may return fragments that cannot answer the question.
- **Chunks too large:** dilute semantic focus, consume more prompt tokens, and may exceed model constraints.
- **Too little overlap:** boundary information is lost.
- **Too much overlap:** storage, embedding cost, and duplicate results rise.
- **Character-based splitting:** simple and robust but unaware of semantic structure.
- **Structure-aware or semantic splitting:** can preserve headings/meaning but adds complexity and sometimes model cost.

## 7.6 Embeddings

> **Embedding.** A dense numerical representation intended to place semantically similar text near each other in a vector space.

The lecture uses the open-source Sentence Transformers model `all-MiniLM-L6-v2`, whose output dimension is 384.

```python
from sentence_transformers import SentenceTransformer

class EmbeddingManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def generate_embeddings(self, texts: list[str]):
        return self.model.encode(texts, show_progress_bar=True)
```

The same embedding model or a compatible query/document pair must be used for indexing and retrieval. Mixing unrelated embedding spaces invalidates similarity comparison.

## 7.7 Similarity Search

The lecture imports cosine similarity. For query vector $\mathbf{q}$ and chunk vector $\mathbf{v}$:

$$
\operatorname{cosine}(\mathbf{q},\mathbf{v})=
\frac{\mathbf{q}^{\top}\mathbf{v}}
{\lVert\mathbf{q}\rVert_2\lVert\mathbf{v}\rVert_2}.
$$

Values closer to $1$ indicate alignment for normalized, semantically trained embeddings. A retriever can return the top $k$ chunks and optionally reject results below a similarity threshold $\tau$:

$$
R(q)=\{c_j: c_j \in \operatorname{TopK}(q),\ \operatorname{sim}(q,c_j)\ge\tau\}.
$$

The threshold should be calibrated on representative data rather than assumed universally.

## 7.8 Persistent ChromaDB Vector Store

The first implementation creates a persistent ChromaDB client and collection. Each stored record needs:

- a unique identifier, generated with UUID in the lecture;
- the original chunk text;
- the embedding vector;
- metadata.

Representative structure:

```python
import chromadb
from uuid import uuid4

client = chromadb.PersistentClient(path="data/chroma_store")
collection = client.get_or_create_collection("pdf_documents")

collection.add(
    ids=[str(uuid4()) for _ in chunks],
    documents=[doc.page_content for doc in chunks],
    metadatas=[doc.metadata for doc in chunks],
    embeddings=embeddings.tolist(),
)
```

A custom retriever:

1. embeds the user query;
2. calls the collection's similarity query;
3. receives documents, distances/scores, and metadata;
4. filters by a threshold;
5. returns the best context.

## 7.9 Persistent FAISS Index

The later modular implementation uses FAISS. Its project structure is conceptually:

```text
src/
  data_loader.py
  embedding.py
  vector_store.py
  search.py
app.py
```

### `data_loader.py`

- Locate supported files with `Path.glob`.
- Load PDF, text, or CSV files using the appropriate loader.
- Normalize everything into LangChain `Document` objects.

### `embedding.py`

- Initialize `all-MiniLM-L6-v2`.
- Split documents with chunk size 1000 and overlap 200.
- Encode each chunk's `page_content`.

### `vector_store.py`

- Build a FAISS index such as `IndexFlatL2`.
- Add float32 vectors.
- Keep metadata aligned with vector positions.
- Save the index and metadata separately.

```python
import faiss
import numpy as np
import pickle

vectors = np.asarray(embeddings, dtype="float32")
index = faiss.IndexFlatL2(vectors.shape[1])
index.add(vectors)

faiss.write_index(index, "faiss_store/files.index")
with open("faiss_store/metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)
```

The index and metadata must stay synchronized. If vector position $i$ corresponds to chunk $c_i$, loading the wrong metadata file silently corrupts retrieval.

The lecture warns indirectly through its workflow that rebuilding is unnecessary on every query. Build and persist the index after ingestion; load it for later searches unless source documents have changed.

## 7.10 RAG Retrieval and Prompt Construction

A retrieval function returns top documents and scores. The generation layer then builds context:

```python
context = "\n\n".join(doc.page_content for doc in retrieved_docs)

prompt = f"""
You are a question-answering assistant.
Answer only from the supplied context.
If the answer is not present, say that you do not know.

Question:
{query}

Context:
{context}
"""

answer = llm.invoke(prompt).content
```

The instruction should explicitly constrain the model to the retrieved evidence. Useful production additions include:

- source labels and page numbers around each chunk;
- a requirement to cite source identifiers;
- a refusal rule when evidence is insufficient;
- deduplication or reranking before generation;
- a maximum context/token budget;
- logging of query, retrieved chunks, scores, prompt, and final response.

## 7.11 RAG Failure Modes

RAG can fail at each stage:

1. **Parsing failure:** tables, columns, OCR, or layout are extracted incorrectly.
2. **Chunking failure:** the answer is split from its qualifier or related section.
3. **Embedding failure:** semantic similarity does not match the user's intent.
4. **Retrieval failure:** the relevant chunk is absent from top $k$.
5. **Context failure:** too much irrelevant text distracts the model.
6. **Generation failure:** the model ignores context or invents unsupported details.
7. **Freshness failure:** updated documents were not re-indexed.
8. **Security failure:** unauthorized documents are retrieved across users or tenants.

These stages motivate the four RAG metrics later in the lecture: retrieval relevance, groundedness, answer relevance, and correctness.

## 7.12 Traditional RAG vs. Agentic RAG

The RAG introduction distinguishes a fixed retrieval chain from an agentic retrieval system.

> **Traditional RAG.** A predetermined pipeline in which every eligible query follows the same retrieval and generation sequence.

> **Agentic RAG.** A retrieval system in which an agent decides whether retrieval is required, which source/tool or retriever to use, whether the evidence is sufficient, and whether to search again before answering.

Traditional flow:

```text
query -> one retriever -> top-k context -> prompt -> answer
```

Agentic flow:

```text
query
  -> classify/plan
  -> choose vector retriever, web search, database, or another tool
  -> inspect evidence
  -> retrieve again or rewrite query if insufficient
  -> synthesize and answer
```

An agentic RAG graph may contain:

1. query-analysis/router node;
2. one or more retrieval/tool nodes;
3. document-relevance grader;
4. query-rewrite or web-search fallback;
5. answer-generation node;
6. groundedness or completeness check;
7. a bounded loop back to retrieval when evidence is inadequate.

The benefit is adaptive retrieval. The cost is additional model calls, latency, nondeterminism, and the possibility of unbounded loops. Model/tool-call limits and explicit termination conditions are therefore essential.

### Key Takeaways

- RAG is two systems: offline/periodic indexing and online retrieval-generation.
- Parsing and chunking quality often dominate downstream retrieval quality.
- Embeddings map chunks and queries into a common vector space; cosine or L2-based search retrieves candidates.
- ChromaDB and FAISS demonstrate two persistence approaches, but metadata alignment is essential in both.
- Retrieved context must be passed with a grounding instruction and source metadata.
- Agentic RAG adds routing, evidence assessment, and iterative retrieval to the fixed RAG pipeline.
- Fine-tuning and RAG solve different problems: behavioral adaptation versus dynamic knowledge access.

# 8. Vectorless, Reasoning-Based RAG with PageIndex

## 8.1 Motivation

Traditional vector RAG retrieves chunks that are close in embedding space. The lecture introduces **PageIndex** as a vectorless, reasoning-based alternative for long, structured documents.

> **Vectorless RAG.** A retrieval approach that organizes a document into a hierarchical, human-readable index and uses an LLM to reason over that hierarchy to select relevant sections, without embedding each chunk into a vector database.

The central contrast is:

```text
Traditional RAG:
document -> chunks -> embeddings -> vector DB -> similarity search

Vectorless PageIndex RAG:
document -> hierarchical tree index -> LLM tree search -> exact sections
```

## 8.2 Hierarchical Tree Construction

Given a structured PDF, the system uses its table of contents (TOC), headings, page boundaries, and model-generated summaries to construct a JSON tree.

A node may contain:

- `node_id`;
- title/section name;
- start/end page or page index;
- summary;
- children;
- optionally the full text or a locator for retrieving it.

Conceptual example:

```json
{
  "node_id": "0001",
  "title": "Deep Learning",
  "page_index": 12,
  "summary": "Introduces neural networks and representation learning.",
  "children": [
    {
      "node_id": "0001-01",
      "title": "Backpropagation",
      "page_index": 16,
      "summary": "Explains gradient-based training through the chain rule."
    }
  ]
}
```

If a useful TOC exists, the builder can map sections directly. If the TOC is absent or unreliable, the LLM analyzes pages, identifies section boundaries, summarizes sections, and assembles a parent-child hierarchy.

The lecture's PageIndex example produces about 40 nodes for its selected PDF.

## 8.3 Query-Time Tree Search

At query time:

1. Read or compress the tree index into a form that fits the model context.
2. Give the LLM the user query plus node titles and summaries.
3. Ask it to reason step by step and return the most relevant node IDs.
4. Locate those nodes in the tree.
5. Fetch their full section text.
6. Check whether the selected content is sufficient.
7. Generate an answer grounded in the selected sections.

Formally, let the document tree be $T=(N,E)$ and each node $n$ have summary $s_n$. An LLM-based selector approximates:

$$
N_q = \operatorname{Select}_{\text{LLM}}(q,\{(n,s_n):n\in N\}),
$$

followed by:

$$
y=\operatorname{LLM}(q,\operatorname{FullText}(N_q)).
$$

Unlike nearest-neighbor retrieval, the selector can reason about hierarchy and relationships among sections.

Representative selection prompt from the lecture's logic:

```text
You are given a user query and a hierarchical document index.
Identify the nodes most relevant to answering the query.
Reason step by step and return the selected node IDs.

Query: {query}
Tree index: {compressed_tree}
```

The answer prompt then receives the exact selected section text rather than only node summaries.

## 8.4 PageIndex API Workflow

The lecture's implementation follows this sequence:

1. Initialize the PageIndex client with its API key.
2. Upload/submit a PDF and retain the returned document ID.
3. Wait while tree construction runs asynchronously.
4. Poll until the tree is ready.
5. Fetch and inspect the tree.
6. Compress node metadata for selection.
7. Run LLM tree search for a query.
8. Resolve selected node IDs.
9. assemble full context and call the answer LLM.

Conceptual pseudocode:

```python
client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
doc = client.submit_document("document.pdf")
document_id = doc["doc_id"]

wait_until_ready(client, document_id)
tree = client.get_tree(document_id)

selected_ids = llm_tree_search(query, compress_nodes(tree))
selected_nodes = find_nodes_by_id(tree, selected_ids)
context = build_context(selected_nodes)
answer = answer_llm(query=query, context=context)
```

Index creation may take minutes for a long PDF because it performs structural analysis and summarization. The index should therefore be built once and reused.

## 8.5 Strengths of Vectorless RAG

1. **Preserves document hierarchy.** A subsection remains connected to its parent chapter.
2. **Cross-section reasoning.** The selector can intentionally compare multiple sections.
3. **Explainable retrieval.** Returned node IDs, titles, summaries, and pages show why content was selected.
4. **No embedding pipeline.** There is no chunk-embedding index to build or query.
5. **No embedding drift/mismatch.** Retrieval does not depend on a particular embedding geometry.
6. **Strong fit for structured long documents.** Manuals, annual reports, contracts, policies, and research reports naturally contain headings and sections.

## 8.6 Weaknesses and Limits

1. **Higher query latency.** Tree traversal may require multiple LLM calls, ranging from hundreds of milliseconds to seconds.
2. **Higher per-query model cost.** Vector lookup is inexpensive; LLM reasoning is not.
3. **Poor internet-scale behavior.** A single reasoning tree is not naturally suited to millions of heterogeneous documents.
4. **Dependence on structure.** Random notes, short posts, tickets, or weakly structured pages may gain little from a tree.
5. **Index-build cost.** Nodes and summaries must be generated and stored.
6. **Context-size pressure.** A very large tree must be compressed or searched hierarchically.
7. **Tooling maturity.** The lecture notes fewer established vectorless tools compared with the broad vector-database ecosystem.

## 8.7 Why Traditional Chunking Can Destroy Context

Fixed-size chunking may separate facts that are logically related but physically distant. For example:

- a rule appears in one chunk;
- an exception appears in another;
- a definition appears in a parent section;
- a later table contains the required value.

Similarity search ranks chunks independently, so it may retrieve the rule but not the exception. A tree retains structural relationships and lets the LLM select both sections.

However, “no chunking” should not be interpreted as “the full document is sent to the LLM every time.” The tree acts as a compact routing index; selected sections still need to fit the answer model's context window.

## 8.8 Traditional vs. Vectorless RAG

| Dimension | Traditional vector RAG | Vectorless tree RAG |
| --- | --- | --- |
| Index unit | Text chunk + vector | Hierarchical section node + summary |
| Query operation | One query embedding + vector search | LLM reasoning/traversal over tree |
| Query latency | Usually lower | Usually higher |
| Query cost | Usually lower | Usually higher |
| Scale | Strong for very large corpora | Better for bounded document sets |
| Cross-section reasoning | Weak unless enhanced | Stronger by design |
| Explainability | Chunk and score | Node path, title, summary, page |
| Setup | Splitter, embedding, vector DB | Tree builder and section summarizer |
| Best data | Large, mixed, unstructured corpora | Long, structured reports/manuals |

The lecture summarizes the trade-off as:

> **Traditional vector RAG = scale. Vectorless RAG = reasoning.**

## 8.9 Hybrid Retrieval

The two techniques need not be mutually exclusive. A practical hybrid can:

1. use vector search to select candidate documents from a very large corpus;
2. use tree-based reasoning inside the selected long documents;
3. fetch exact sections;
4. rerank or validate evidence;
5. generate a grounded answer.

This combines corpus-level scale with document-level structural reasoning.

### Key Takeaways

- Vectorless RAG replaces embedding similarity with LLM reasoning over a hierarchical document index.
- It is most attractive when document structure and cross-section relationships matter.
- It offers more explainable section selection but usually costs more and responds more slowly.
- Traditional vector RAG remains preferable for large, heterogeneous, latency-sensitive corpora.
- Hybrid systems can use vectors for global discovery and tree search for precise within-document reasoning.

# 9. Deep Agents and Deep Research

## 9.1 Shallow Agents vs. Deep Agents

The lecture first characterizes a conventional tool-using or ReAct agent:

```text
request -> model decision -> tool -> observation -> model -> answer
```

This is effective for bounded tasks but has limitations:

- no explicit multi-step plan;
- limited context retention;
- no formal task decomposition;
- no specialized subagents;
- no durable workspace for large intermediate results.

> **Deep agent.** An agent architecture designed for complex, long-horizon tasks through explicit planning, task decomposition, specialized subagents, file-system-backed context, persistent memory, and richer middleware.

Examples include deep-research agents and advanced coding assistants.

## 9.2 Four Core Components

The lecture presents four defining components.

### 1. Planning tool

The initial request is converted into a to-do list or structured plan. For “research and write a blog,” possible tasks are:

1. Research the topic on the web.
2. Search relevant papers.
3. Organize and compare findings.
4. Draft the blog.
5. Review and revise.

The plan makes progress inspectable and prevents the agent from treating a long task as one undifferentiated prompt.

### 2. Subagents

Independent subagents can handle specialized tasks, such as web research, paper research, drafting, or review. Benefits include:

- context isolation;
- specialized instructions and tools;
- parallelizable independent work;
- reduced clutter in the coordinator's active context.

Parallel execution is safe only when dependencies permit it. Drafting normally depends on completed research; independent searches can run concurrently.

### 3. System prompt

A deep agent requires strong operating instructions: role, scope, tool-use policy, safety constraints, completion criteria, file conventions, and escalation behavior. The lecture points to coding agents whose system prompts define both capability and refusal boundaries.

### 4. File system or persistent workspace

Large tool outputs should not remain entirely in the active message history. Agents can write notes, search results, drafts, and plans to files and later read only what is needed.

> **Context offloading.** Moving large intermediate information from the immediate LLM prompt into an external workspace while retaining references that allow later retrieval.

This serves as durable working memory, reduces context pressure, and allows subagents to share artifacts.

## 9.3 When to Use Deep Agents

Use a deep agent when the task:

- requires planning and decomposition;
- spans many dependent steps;
- produces or consumes large amounts of context;
- benefits from specialist subagents;
- needs persistent work across turns or threads;
- requires inspectable progress and intermediate artifacts.

Avoid the added complexity for a single factual answer, a single tool call, or a short deterministic workflow.

## 9.4 Implementation Setup

The lecture installs the `deepagents` package with LangChain/model integrations and uses a Tavily web-search tool.

```python
from tavily import TavilyClient

tavily = TavilyClient(api_key=TAVILY_API_KEY)

def web_search(topic: str):
    """Search the web for information about a topic."""
    return tavily.search(topic)
```

Create a basic deep agent:

```python
from deepagents import create_deep_agent
from langchain_groq import ChatGroq

model = ChatGroq(model="qwen-qwq-32b")

deep_agent = create_deep_agent(
    model=model,
    tools=[web_search],
    system_prompt=(
        "Act as a rigorous researcher. Decompose complex requests, "
        "use tools when necessary, preserve useful findings, and "
        "produce a well-supported final answer."
    ),
)
```

Invocation retains the usual message interface:

```python
result = deep_agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Research LangGraph and deep agents and compare them.",
    }]
})
```

## 9.5 What the Framework Adds

The lecture inspects the deep agent and contrasts it with a basic `create_agent`. A deep agent is built on LangGraph and includes middleware/hooks supporting:

- task planning and to-do tracking;
- file-system operations;
- summarization/context management;
- subagent delegation;
- interruption and resumption;
- model and tool lifecycle control.

When web search returns a large result, the agent may write content to a file and expose it under the result's `files` state rather than keeping everything in the visible answer. This is deliberate context management, not an incidental output format.

## 9.6 Deep-Research Execution Pattern

A robust deep-research workflow follows:

1. **Interpret the request.** Identify deliverable, scope, constraints, and evidence standard.
2. **Plan.** Create tasks and dependency relationships.
3. **Delegate.** Assign bounded research questions to specialist agents.
4. **Gather evidence.** Use search or document tools and record source metadata.
5. **Persist.** Save large outputs and structured notes to the workspace.
6. **Synthesize.** Compare claims, resolve contradictions, and find missing evidence.
7. **Draft.** Produce the requested artifact.
8. **Review.** Check coverage, unsupported claims, consistency, and format.
9. **Deliver.** Return a concise result and the persistent artifact when applicable.

## 9.7 Risks and Controls

Deep agents expand both capability and failure surface:

- plans may be inefficient or cyclic;
- subagents may duplicate work;
- sources may be unreliable;
- files may contain stale or conflicting facts;
- tool costs can grow rapidly;
- write/send/delete tools can create irreversible effects;
- a compromised tool result can inject malicious instructions.

Controls include step budgets, tool allowlists, source validation, sandboxed files, explicit dependency tracking, middleware, checkpoints, and human approval for consequential actions.

### Key Takeaways

- Deep agents are designed for long-horizon, multi-step work rather than simple question answering.
- Planning, subagents, strong system instructions, and file-backed context are the central additions.
- File systems offload large context and allow intermediate work to persist.
- The architecture is built on graph execution and middleware rather than a single opaque prompt loop.
- Greater autonomy requires stricter budgets, safety controls, and review.

# 10. Guardrails and AI Safety

## 10.1 Definition and Placement

> **Guardrails.** Safety and policy mechanisms that inspect or control model inputs, outputs, tool calls, and workflow transitions to reduce harmful, unauthorized, sensitive, or noncompliant behavior.

Guardrails can be placed:

- before the agent receives input;
- before/after a model call;
- before/after a tool call;
- after the final output;
- at several layers simultaneously.

They may block a request, redact or mask data, require approval, restrict tools, modify an output, or terminate the workflow.

## 10.2 Deterministic vs. Model-Based Guardrails

### Deterministic guardrails

Use fixed rules such as:

- keyword lists;
- regular expressions;
- schema validation;
- numeric thresholds;
- allowlists/denylists;
- role/permission checks.

```python
BANNED_KEYWORDS = {"hack", "malware", "exploit"}

def deterministic_guardrail(text: str) -> dict:
    normalized = text.lower()
    blocked = any(word in normalized for word in BANNED_KEYWORDS)
    return {"status": "blocked" if blocked else "allowed"}
```

Advantages: fast, inexpensive, predictable, testable, and zero model cost for requests blocked before inference. Disadvantages: brittle wording dependence, false positives, evasions, and weak semantic understanding.

### Model-based guardrails

Use another model to classify the input or output semantically:

```python
def model_based_guardrail(text: str) -> str:
    prompt = f"""
    Classify the following content as SAFE or UNSAFE.
    Content: {text}
    Return only the label.
    """
    return safety_model.invoke(prompt).content.strip()
```

Advantages: understands paraphrases and context. Disadvantages: higher latency/cost, probabilistic inconsistency, and vulnerability to adversarial prompting. A safety model should return a structured decision with reason/category rather than unconstrained prose.

## 10.3 Personally Identifiable Information Middleware

> **PII.** Information that directly or indirectly identifies a person or exposes sensitive identifiers, such as email addresses, card numbers, IP addresses, MAC addresses, URLs, or API keys.

The lecture presents four transformation strategies:

| Strategy | Effect |
| --- | --- |
| Redact | Replace the value with a label such as `[REDACTED_EMAIL]` |
| Mask | Preserve only a safe fragment, e.g. last four card digits |
| Hash | Replace with a deterministic/nonreversible representation as configured |
| Block | Raise an exception and stop the request |

Example middleware stack:

```python
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[customer_lookup],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
        PIIMiddleware("api_key", strategy="block", apply_to_input=True),
    ],
)
```

The lecture's test input contains an email and a credit-card number. The email is replaced with a redaction marker and the card is masked before it reaches the rest of the workflow. An API key triggers a blocked exception.

PII controls may need to apply to:

- user input;
- model output;
- arguments sent to tools;
- observations returned by tools;
- logs and traces.

Redacting only the user-visible answer is insufficient if raw PII has already been sent to a third-party model or stored in telemetry.

## 10.4 Human Approval for Sensitive Tools

The lecture defines dummy tools for web search, sending email, and deleting records. Search is allowed without approval; email and deletion are interrupted.

High-impact approval should include:

1. proposed operation;
2. exact arguments/recipient/target;
3. expected effect;
4. opportunity to approve, reject, or edit;
5. a durable audit trail;
6. safe resumption from a checkpoint.

## 10.5 Custom Middleware Guardrail

Custom middleware inherits the agent-middleware base and inspects state at a lifecycle hook. Conceptually:

```python
class ContentFilterMiddleware(AgentMiddleware):
    def __init__(self, banned_keywords: list[str]):
        self.banned_keywords = [x.lower() for x in banned_keywords]

    def before_agent(self, state, runtime):
        content = state["messages"][-1].content.lower()
        for keyword in self.banned_keywords:
            if keyword in content:
                raise ValueError(f"Blocked keyword detected: {keyword}")
```

A corresponding model-based middleware can inspect model output after generation and replace or reject unsafe content.

## 10.6 Layered Guardrails

The recommended approach combines layers:

1. **Layer 1—deterministic input filter:** reject known prohibited patterns cheaply.
2. **Layer 2—PII protection:** redact/mask/block sensitive data before external calls.
3. **Layer 3—authorization and HITL:** require approval for selected tools.
4. **Layer 4—model-based safety:** semantically review ambiguous input/output.
5. **Layer 5—postcondition/schema checks:** verify final output and action result.
6. **Layer 6—logging and monitoring:** record policy decisions and detect drift.

No single layer is complete. Deterministic filters are precise but narrow; model filters are flexible but probabilistic; human approval is powerful but costly and slow.

## 10.7 Guardrail Evaluation

For a binary safety classifier:

$$
\text{Precision}=\frac{TP}{TP+FP}, \qquad
\text{Recall}=\frac{TP}{TP+FN},
$$

$$
F_1=2\cdot\frac{\text{Precision}\cdot\text{Recall}}
{\text{Precision}+\text{Recall}}.
$$

Here, “positive” can mean unsafe content. High recall reduces missed unsafe requests; high precision reduces unnecessary blocking. The acceptable trade-off depends on the action's risk.

### Key Takeaways

- Guardrails operate around inputs, models, tools, outputs, and state transitions.
- Deterministic rules are cheap and predictable; model-based checks add semantic understanding.
- Protect PII before it reaches models, tools, or logs—not only in the final display.
- Human approval is appropriate for consequential operations such as email, deletion, or finance.
- Layered defenses are stronger than any single filter and must themselves be evaluated.

# 11. Chatbot and RAG Evaluation with LangSmith

## 11.1 Why Evaluation Is Necessary

LLM outputs are probabilistic and natural-language quality is multidimensional. “It looks good” is not an adequate release criterion. The lecture lists several evaluation approaches:

- LLM-as-a-judge;
- gold-standard/reference evaluation;
- functional tests;
- human evaluation and annotation;
- regression testing across model or prompt versions.

> **Evaluation dataset.** A versioned collection of representative inputs and, when applicable, expected/reference outputs and metadata.

> **Evaluator.** A function or model that maps an example and system run to one or more scores, labels, or explanations.

> **Experiment.** A reproducible execution of a target system over a dataset with specified evaluators, configuration, and identifying metadata.

## 11.2 LangSmith Workflow

The lecture uses LangSmith to create datasets, run experiments, inspect traces, and compare metrics.

High-level steps:

1. Configure the LangSmith API key and tracing environment.
2. Create a `Client`.
3. Create a named dataset.
4. Add examples with inputs and reference outputs.
5. Define the target function/application.
6. Define one or more evaluators.
7. Run an experiment with a meaningful prefix/version.
8. Inspect aggregate and per-example results.
9. Change the prompt/model and rerun as a separate experiment.

```python
from langsmith import Client

client = Client()
dataset = client.create_dataset(
    dataset_name="chatbot-evaluation",
    description="Reference QA examples for chatbot regression testing",
)

client.create_examples(
    inputs=[
        {"question": "What is LangChain?"},
        {"question": "What is LangGraph?"},
    ],
    outputs=[
        {"answer": "A framework for building LLM applications."},
        {"answer": "A graph framework for stateful agent workflows."},
    ],
    dataset_id=dataset.id,
)
```

The reference output is the **ground truth** for reference-dependent metrics. It should be curated; a weak or incorrect reference makes the metric misleading.

## 11.3 Chatbot Evaluation

The lecture constructs a simple target function that calls an OpenAI model and returns an answer. It then defines two judge-based metrics.

### Correctness

> **Correctness.** Whether the generated response agrees with the factual requirements of the reference answer.

Inputs to the judge:

- the question;
- the generated/student answer;
- the reference/ground-truth answer.

The judge is instructed that additional accurate information is acceptable, but contradictions or missing essential facts are not.

### Concision/relevance

The second chatbot metric checks whether the response is concise and focused. Depending on the exact prompt, this is labeled concision or relevance in the lecture's experiment view.

An LLM judge should produce a structured response:

```python
from pydantic import BaseModel, Field

class CorrectnessGrade(BaseModel):
    is_correct: bool
    explanation: str = Field(description="Short justification")
```

Conceptual evaluator:

```python
def correctness(inputs, outputs, reference_outputs):
    grade = correctness_judge.invoke({
        "question": inputs["question"],
        "student_answer": outputs["answer"],
        "reference_answer": reference_outputs["answer"],
    })
    return {
        "key": "correctness",
        "score": int(grade.is_correct),
        "comment": grade.explanation,
    }
```

Run an experiment:

```python
results = client.evaluate(
    target_function,
    data="chatbot-evaluation",
    evaluators=[correctness, concision],
    experiment_prefix="chatbot-v1",
)
```

The LangSmith interface shows aggregate scores and lets the developer inspect individual input, output, reference, trace, and evaluator explanation.

## 11.4 RAG Evaluation Dimensions

RAG must be evaluated at both retrieval and generation stages. The lecture defines four metrics:

### 1. Correctness

> Does the generated answer match the ground-truth/reference answer?

Comparison:

$$
\operatorname{Correctness}(q,a,a^*),
$$

where $a$ is the generated answer and $a^*$ is the reference answer.

This is reference-dependent.

### 2. Answer relevance

> Does the generated answer directly address the user's question, concisely and without irrelevant diversion?

Comparison:

$$
\operatorname{AnswerRelevance}(q,a).
$$

This can be judged without a reference answer. A response may be factually true but irrelevant to the actual question.

### 3. Groundedness/faithfulness

> Are the factual claims in the answer supported by the retrieved documents/context?

Comparison:

$$
\operatorname{Groundedness}(a,C),
$$

where $C$ is retrieved context. A response can match the reference yet still contain extra unsupported claims, so groundedness is a distinct metric.

For claim-level analysis, if the answer contains claims $\{z_1,\ldots,z_n\}$:

$$
\text{Faithfulness} =
\frac{\left|\{z_i:z_i\text{ is entailed by }C\}\right|}{n}.
$$

### 4. Retrieval relevance

> Are the retrieved documents relevant to the question?

Comparison:

$$
\operatorname{RetrievalRelevance}(q,C).
$$

This isolates the retriever from the answer generator. If irrelevant context is retrieved but the LLM guesses correctly, answer correctness alone hides the retrieval defect.

## 11.5 Building the RAG Evaluation Target

The lecture constructs a small RAG system:

1. Load a web page/blog.
2. Split it into documents.
3. Create embeddings and a vector store.
4. Retrieve context for each question.
5. Use a prompt instructing the model to answer from context, in at most a few sentences.
6. Return both answer and retrieved documents so separate evaluators can inspect them.

The target should expose at least:

```python
{
    "answer": generated_answer,
    "retrieved_docs": retrieved_texts,
}
```

If only the final answer is returned, groundedness and retrieval relevance cannot be evaluated reliably.

## 11.6 RAG Test Dataset

The lecture creates a LangSmith dataset with three question-answer examples derived from the loaded blog, including a question about self-reflection. Each example has:

- input question;
- reference answer;
- optionally source metadata or expected evidence.

A rigorous dataset should include:

1. common questions;
2. rare but important questions;
3. questions requiring multiple chunks;
4. ambiguous queries;
5. unanswerable/out-of-scope queries;
6. adversarial or misleading wording;
7. freshness-sensitive facts;
8. access-control cases.

## 11.7 Structured Judge Implementations

The lecture creates a separate Pydantic schema, prompt, and evaluator for each metric. Representative schema:

```python
class BinaryGrade(BaseModel):
    score: bool = Field(description="True only if all criteria are met")
    explanation: str
```

Each judge model is wrapped with structured output:

```python
judge = evaluator_model.with_structured_output(BinaryGrade)
```

### Correctness judge inputs

```text
Question + generated answer + reference answer
```

### Relevance judge inputs

```text
Question + generated answer
```

### Groundedness judge inputs

```text
Generated answer + retrieved facts/context
```

### Retrieval-relevance judge inputs

```text
Question + retrieved documents/context
```

The experiment is then run with all four custom evaluators and inspected in LangSmith.

## 11.8 Interpreting Metric Combinations

| Retrieval relevance | Groundedness | Correctness | Likely diagnosis |
| ---: | ---: | ---: | --- |
| Low | Low | Low | Retriever/index/chunking problem |
| High | Low | Low | Model ignored or distorted good context |
| Low | High | Low | Answer faithfully used irrelevant/insufficient context |
| High | High | Low | Reference conflict, incomplete evidence, or reasoning failure |
| Low | Low | High | Model guessed/used parametric memory; unsafe apparent success |
| High | High | High | Desired grounded RAG behavior |

Answer relevance can be low in any row if the response is verbose or fails to directly answer the question.

## 11.9 Limits of LLM-as-a-Judge

An LLM judge is scalable but not objective ground truth. Risks include:

- preference for verbose or stylistically similar answers;
- position/order bias;
- sensitivity to evaluator prompt wording;
- judge-model knowledge errors;
- inconsistent scores;
- susceptibility to adversarial text inside evaluated content;
- correlated errors when generator and judge are similar models.

Mitigations:

1. Use precise rubrics and structured outputs.
2. Blind the judge to model/provider identity.
3. Calibrate against human-labeled examples.
4. Use deterministic metrics where appropriate.
5. Repeat or use multiple judges for high-stakes decisions.
6. Inspect explanations and per-example traces, not only averages.
7. Version datasets, prompts, retrievers, and model configuration.

## 11.10 Experiment and Regression Discipline

For model/prompt version $v$, define a score over $N$ examples:

$$
\bar{s}_v=\frac{1}{N}\sum_{i=1}^{N}s_{i,v}.
$$

But an average can hide critical regressions. Track:

- per-category scores;
- worst-case examples;
- safety-critical slices;
- latency and token cost;
- retrieval hit rate;
- changes relative to a baseline.

A release gate may require:

$$
\bar{s}_{\text{new}} \ge \bar{s}_{\text{baseline}}-\epsilon
$$

and zero regressions on protected examples.

### Key Takeaways

- Evaluation requires versioned datasets, reproducible targets, explicit metrics, and named experiments.
- RAG quality is not one number: measure correctness, answer relevance, groundedness, and retrieval relevance separately.
- Return retrieved context from the target so retrieval and generation can be diagnosed independently.
- LLM judges are useful but should be calibrated against humans and supplemented with deterministic checks.
- Aggregate scores must be paired with slice-level and per-example inspection.

# 12. LLM Gateways with LiteLLM

## 12.1 Definition and Motivation

> **LLM gateway.** A centralized, provider-neutral middleware layer between applications and model providers that offers a unified API plus routing, fallbacks, caching, rate limits, cost tracking, guardrails, evaluation hooks, and observability.

Without a gateway, applications often accumulate:

- provider-specific SDK calls;
- incompatible request/response formats;
- duplicated retry code;
- no central cost view;
- no automatic fallback;
- difficult model migration;
- scattered safety and rate-limit policy.

With a gateway, the application sends a normalized request and the gateway handles provider selection and policy.

## 12.2 Core Features

### 1. Unified API

One request interface can call models from OpenAI, Gemini, Groq, and other providers by changing a model identifier or configuration rather than rewriting the application.

### 2. Automatic fallback

If a primary model fails, the gateway tries a configured alternative:

$$
m^* = \min\{m_i : \operatorname{call}(m_i)\text{ succeeds}\},
$$

with $m_1,m_2,\ldots$ ordered by policy.

Fallbacks improve availability but may change quality, context limits, tool support, latency, and compliance region. Those differences must be tested.

### 3. Smart routing

Choose a model based on task type:

- fast/cheap model for simple summaries;
- strong reasoning model for complex analysis;
- coding-specialized model for code;
- balanced model for ordinary chat.

### 4. Load balancing

Distribute requests across deployments/providers to avoid a single rate-limit or capacity bottleneck.

### 5. Rate limiting and budgets

Restrict requests or token consumption by user, key, team, or time window.

### 6. Caching

Return a stored response for a repeated equivalent request. If $h$ is cache hit rate, a simplified expected provider cost is:

$$
\mathbb{E}[C]=(1-h)C_{\text{model}}+C_{\text{cache}}.
$$

The lecture's local-cache example makes the second identical request faster and avoids a second model charge.

### 7. Cost tracking

The gateway records prompt/completion tokens and estimates price:

$$
C=\frac{T_{\text{in}}}{10^6}p_{\text{in}}+
\frac{T_{\text{out}}}{10^6}p_{\text{out}},
$$

where $p_{\text{in}}$ and $p_{\text{out}}$ are per-million-token prices.

### 8. Observability

Centralized traces can include selected model, fallback chain, status, error, latency, token counts, estimated cost, cache status, and policy decisions.

### 9. Guardrails and evaluation

Input/output filters, PII controls, and evaluation hooks can be applied centrally rather than reimplemented in each application.

## 12.3 LiteLLM Unified Completion

The lecture uses the open-source LiteLLM library:

```python
from litellm import completion

response = completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "What is an LLM gateway?"}],
)

print(response.choices[0].message.content)
```

Provider/model prefixes normalize access. The same `completion` function can target a different configured provider.

## 12.4 Automatic Fallback Example

The lecture intentionally uses an unavailable primary model and then supplies valid alternatives:

```python
response = completion(
    model="gemini/nonexistent-primary-model",
    messages=messages,
    fallbacks=[
        "openai/gpt-4o-mini",
        "groq/llama-3.1-8b-instant",
    ],
)
```

Expected flow:

1. Primary request fails.
2. Gateway catches an eligible error.
3. First configured fallback is attempted.
4. If it succeeds, the normalized response is returned.
5. Metadata should record which model actually served the response.

Fallback should not indiscriminately retry permanent failures such as invalid authentication or policy rejection.

## 12.5 Cost Calculation

LiteLLM exposes completion cost utilities. The lecture inspects input tokens, output tokens, and estimated model charge after a response. Production use should aggregate by:

- application;
- user/team;
- model/provider;
- feature or endpoint;
- cached vs. uncached request;
- time period.

## 12.6 Caching

The lecture configures a local cache:

```python
import litellm
from litellm.caching import Cache

litellm.cache = Cache(type="local")

first = completion(model="openai/gpt-4o-mini", messages=messages)
second = completion(model="openai/gpt-4o-mini", messages=messages)
```

Cache-key design must include all output-affecting inputs, such as model, messages, system prompt, temperature, tool definitions, structured-output schema, and relevant user/tenant scope. Do not share sensitive cached responses across unauthorized users.

## 12.7 Task-Based Routing

The lecture defines aliases such as:

- `fast-cheap`;
- `smart`;
- `balanced`.

A simple deterministic router maps a task label to a model:

```python
ROUTING = {
    "summary": "fast-cheap",
    "coding": "smart",
    "general": "balanced",
}

model_alias = ROUTING.get(task, "balanced")
```

The gateway/model list then maps each alias to provider credentials and an actual model. More advanced routing can use rules based on input length, SLA, cost budget, language, tool needs, or a classifier.

## 12.8 Load Balancing and Router Pools

A logical pool such as `gpt-pool` can include OpenAI and Groq deployments. A routing strategy selects among them, for example by least-busy or usage-based policy. The goals are:

- stay below provider rate limits;
- improve availability;
- distribute latency/capacity;
- control cost.

Do not assume different models are behaviorally interchangeable. Pool members should be evaluated against the same application contract.

## 12.9 LangChain Integration and `.with_fallbacks()`

The lecture also integrates LiteLLM through a LangChain chat-model wrapper and demonstrates LangChain-level fallbacks:

```python
primary = ChatLiteLLM(model="openai/nonexistent-model")
fallback_1 = ChatLiteLLM(model="openai/gpt-4o-mini")
fallback_2 = ChatLiteLLM(model="groq/llama-3.1-8b-instant")

resilient_model = primary.with_fallbacks([fallback_1, fallback_2])
answer = resilient_model.invoke("Explain LLM gateways in three bullets.")
```

This demonstrates two layers of resilience:

- the gateway itself may manage provider/model fallback;
- the orchestration framework may wrap runnable fallbacks.

Avoid redundant retry storms by defining which layer owns retries and how budgets are shared.

## 12.10 Combined Router with Latency and Cost Logging

The final example combines:

1. task classification or task label;
2. routing to a configured model;
3. fallback if the chosen model fails;
4. timing of the call;
5. token/cost calculation;
6. logging of the served model and response.

For request $i$:

$$
L_i=t_{i,\text{end}}-t_{i,\text{start}}.
$$

Aggregate percentiles matter more than the mean:

$$
p_{50}(L),\quad p_{95}(L),\quad p_{99}(L).
$$

## 12.11 Gateway-Level PII Guardrail

The lecture ends with a custom input guardrail that uses regex patterns to detect PII such as email addresses before making the provider request. When PII is detected, it logs the type/count and blocks or transforms the input.

This central layer is useful, but application-specific guardrails remain necessary because the gateway may not understand each tool's business impact.

## 12.12 Production Concerns

A production gateway should address:

- authentication and virtual keys;
- per-tenant authorization;
- secret management;
- encrypted transport;
- data residency and provider allowlists;
- retries with exponential backoff and jitter;
- circuit breakers;
- idempotency where relevant;
- rate and token limits;
- cache privacy and invalidation;
- prompt/tool logging with redaction;
- model-version pinning;
- quality regression tests before route changes.

### Key Takeaways

- An LLM gateway centralizes multi-provider access and operational policy behind a unified API.
- Fallbacks improve availability, routing improves task/cost fit, and load balancing manages capacity.
- Caching can reduce latency and cost but requires privacy-aware keys and invalidation.
- Cost, latency, actual served model, fallback path, and policy decisions should be observable.
- A gateway complements application-level orchestration and guardrails; it does not replace them.

# 13. Integrated Production Architecture

The lecture's components form one coherent stack:

1. **Client/UI** sends a user message and displays streamed updates.
2. **LLM gateway** authenticates the request, enforces budgets, selects a provider, caches eligible calls, and records cost/latency.
3. **Guardrail middleware** scans input and protects PII.
4. **LangGraph/deep agent** loads the thread checkpoint, plans, routes, and tracks state.
5. **Retriever** chooses vector, vectorless, or hybrid retrieval according to corpus structure and scale.
6. **MCP client** discovers allowed tools from independent servers.
7. **HITL** pauses before consequential tool calls.
8. **Checkpointer/workspace** persists messages, state, plans, and large intermediate artifacts.
9. **Evaluation/observability** stores traces and scores representative runs.

## 13.1 Control Flow

```text
User request
  -> input guardrail / PII policy
  -> load thread state
  -> plan or direct model decision
     -> retrieve knowledge if needed
     -> call MCP tool if needed
        -> request human approval if sensitive
  -> grounded generation
  -> output guardrail / schema validation
  -> stream response and persist checkpoint
  -> log latency, tokens, cost, retrieval, and policy outcomes
```

## 13.2 Design Decisions

### Agent vs. deterministic workflow

Use a deterministic graph for known business processes. Use model-directed routing only where flexible language understanding or planning provides value.

### Vector vs. vectorless retrieval

- Large mixed corpus, low latency, cost-sensitive: vector RAG.
- Bounded structured documents, cross-section reasoning: vectorless tree RAG.
- Large corpus of structured documents: vector search for document discovery plus tree reasoning within selected documents.

### In-memory vs. durable checkpointing

In-memory state is appropriate for notebooks. Production requires durable storage, retention policy, encryption, and tenant isolation.

### Automatic action vs. approval

Classify tools by impact. Read-only search may run automatically; email, deletion, finance, or publication should require stronger authorization or approval.

### Single model vs. gateway routing

A single model is simpler during prototyping. A gateway becomes valuable when availability, multiple providers, budgets, policy, and centralized observability matter.

## 13.3 End-to-End Quality Model

System success depends on several conditional stages:

$$
P(\text{correct grounded answer})
\approx P(R)\cdot P(G\mid R)\cdot P(S),
$$

where:

- $P(R)$ is probability that retrieval supplies sufficient evidence;
- $P(G\mid R)$ is probability that generation correctly uses that evidence;
- $P(S)$ is probability that safety and authorization controls behave correctly.

This simplified factorization explains why improving only the LLM does not fix poor parsing, retrieval, authorization, or guardrails.

### Key Takeaways

- The lecture's topics are complementary layers, not competing frameworks.
- Explicit state, tool boundaries, safety checks, and observability make agent behavior easier to inspect.
- Retrieval architecture should follow corpus structure, query complexity, latency, and scale.
- Production quality is an end-to-end property across retrieval, generation, safety, persistence, and operations.

# 14. Glossary and Revision Checklist

## 14.1 Glossary

| Term | Meaning |
| --- | --- |
| Agent | LLM-centered loop that chooses tools or a final response |
| ReAct | Iterative reasoning/action/observation pattern |
| Tool call | Structured model request to execute a named capability with arguments |
| Middleware | Lifecycle logic around agent/model/tool execution |
| State | Shared data passed through graph nodes |
| Reducer | Rule that merges a state update with existing state |
| Checkpoint | Saved graph-state snapshot for a thread/execution |
| Thread ID | Identifier used to isolate and resume one conversation |
| Conditional edge | Runtime-selected graph transition |
| HITL | Human approval or input within an automated workflow |
| MCP | Standard protocol for exposing/discovering model-facing capabilities |
| RAG | Retrieval of external knowledge before LLM generation |
| Chunk | Subdivision of a source document used as a retrieval unit |
| Embedding | Dense vector representation of text or other data |
| Vector store | System that stores vectors and performs similarity search |
| Cosine similarity | Normalized dot-product similarity between vectors |
| Vectorless RAG | LLM-guided retrieval over a hierarchical document index |
| Deep agent | Planning, subagent, workspace, and persistence-oriented agent |
| Guardrail | Mechanism that enforces safety, privacy, or action policy |
| Groundedness | Degree to which answer claims are supported by supplied context |
| Retrieval relevance | Degree to which retrieved content answers the query |
| LLM gateway | Unified model-access and operational-control layer |
| Fallback | Alternative model/provider attempted after failure |
| Smart routing | Policy that selects a model based on task or constraints |

## 14.2 Interview and Exam Revision Questions

1. Why can an LLM agent answer current-weather questions that a plain pretrained LLM cannot?
2. Describe the four message types and explain tool-call correlation.
3. Compare Pydantic, `TypedDict`, and dataclasses for structured output.
4. What lifecycle concerns belong in middleware rather than the main agent prompt?
5. Why does `add_messages` need to be declared as a reducer?
6. Why should a tool node often transition back to the model rather than directly to `END`?
7. How do checkpoints and thread IDs provide conversation continuity?
8. Compare `updates` and `values` stream modes.
9. Explain `interrupt` and `Command(resume=...)` in a HITL graph.
10. Distinguish an MCP server, client, and host.
11. Compare `stdio` and streamable-HTTP MCP transports.
12. Draw the indexing and online-query pipelines of traditional RAG.
13. Explain how chunk size and overlap affect recall, precision, prompt cost, and duplication.
14. Derive cosine similarity and explain why compatible embeddings are required.
15. Why must FAISS index positions stay aligned with metadata?
16. Describe PageIndex tree construction when a TOC exists and when it does not.
17. When is vectorless RAG preferable, and why does it have higher latency?
18. Propose a hybrid vector-plus-tree retrieval architecture.
19. What makes a deep agent “deep” rather than merely tool-using?
20. How does file-backed context help long-horizon agents?
21. Compare deterministic and model-based guardrails.
22. At which points must PII be filtered to prevent leakage?
23. Why are correctness and groundedness different RAG metrics?
24. Diagnose a system with high correctness but low groundedness.
25. What are the principal biases of LLM-as-a-judge?
26. How do gateway fallback, smart routing, and load balancing differ?
27. What fields must be included in a safe semantic cache key?
28. Why can a fallback model silently violate an application's quality contract?
29. Which latency and cost metrics should be logged for every model call?
30. Design a release gate that combines quality, safety, latency, and cost.

## 14.3 Final Revision Summary

- **LangChain v1** supplies common model interfaces, tool-aware agents, messages, structured output, and middleware.
- **LangGraph** makes execution explicit through typed state, reducers, nodes, edges, loops, checkpoints, streaming, and interruption.
- **MCP** decouples tool providers from agent applications through standardized servers and clients.
- **Traditional RAG** scales retrieval with chunks, embeddings, and vector similarity.
- **Vectorless RAG** uses a hierarchical document tree and LLM reasoning for structured, cross-section retrieval.
- **Deep agents** add plans, subagents, persistent workspaces, and long-horizon context management.
- **Guardrails** combine deterministic checks, model-based safety, PII protection, authorization, and HITL.
- **LangSmith evaluation** uses datasets and experiments to measure correctness, relevance, grounding, and retrieval.
- **LLM gateways** centralize provider access, routing, fallback, caching, budgets, cost, and observability.
- A reliable AI system is an engineered pipeline whose weakest stage can dominate overall behavior.
