# Phase 03: LangGraph Fundamentals

## 🎯 Why This Matters
As you build more complex LLM applications, you quickly realize that simple chains (Phase 2) are not enough. You need loops, conditional routing, and state that persists across multiple turns. LangGraph is a library for building stateful, multi-actor applications with LLMs, modeled as graphs (state machines). For a Java developer, this is the paradigm shift from writing linear imperative scripts to building scalable, event-driven state machines.

---

## 🕸️ 3.1 The LangGraph Mental Model

LangGraph treats your application as a graph where **Nodes** are functions and **Edges** determine the flow. Data is passed between nodes via a shared **State** object (a `TypedDict`).

### 💡 Java Analogy
*   **State (`TypedDict`)** ➡️ The `StateContext` in Spring Statemachine, or a shared Request Context object.
*   **Node** ➡️ A `Function<StateContext, StateContext>` that transforms or adds to the state.
*   **Edge** ➡️ A state transition.
*   **Conditional Edge** ➡️ A transition guard or router.

### 👨‍💻 Code Example: Basic Graph Setup
```python
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# 1. Define the State (Data structure passed around)
class AgentState(TypedDict):
    # 'add_messages' means new messages are appended, not overwritten
    messages: Annotated[List, add_messages] 
    step_count: int

# 2. Define a Node (A pure function)
def my_node(state: AgentState) -> dict:
    return {"step_count": state["step_count"] + 1} # Returns a partial update

# 3. Build the Graph
builder = StateGraph(AgentState)
builder.add_node("process", my_node)
builder.set_entry_point("process")
builder.add_edge("process", END)
graph = builder.compile()
```

---

## 🔀 3.2 Routing and Conditional Edges

Instead of a hardcoded path from Node A to Node B, you can write a function that inspects the current state and returns the name of the *next* node to execute.

### 💡 Java Analogy
*   **Router** ➡️ A `Switch` statement inside a controller, or the `RouterFunction` in Spring WebFlux.

### 👨‍💻 Code Example: Routing
```python
def route(state: AgentState) -> str:
    last_message = state["messages"][-1].content.lower()
    if "help" in last_message:
        return "support_node"
    return "general_node"

# Adding the conditional edge
builder.add_conditional_edges(
    "classify_node", # The node we are coming from
    route,           # The routing function
    {
        "support_node": "support_node", # if route() returns 'support_node', go here
        "general_node": "general_node"
    }
)
```

### 🚨 Common Java-Dev Mistakes
> [!WARNING]
> **Mutating State Directly**: Nodes in LangGraph must return a *dictionary representing updates*, not modify the state object in place. LangGraph handles the actual state update behind the scenes (similar to Redux reducers in JavaScript or immutable data structures in functional Java).

---

## 🤖 3.3 ReAct Agents with Tools

LangGraph provides a prebuilt `create_react_agent`. "ReAct" stands for Reasoning + Acting. The LLM reasons about the user's query, decides to call a Tool (Act), reads the result, reasons again, and eventually provides an answer. 

### 💡 Java Analogy
*   **ReAct Agent** ➡️ A dynamic while-loop that executes `Command` design patterns until a completion condition is met.

### 👨‍💻 Code Example: Prebuilt Agent
```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Returns the weather for a city."""
    return "75 degrees"

# This one line creates a complex graph that handles the while-loop of tool calling!
agent_executor = create_react_agent(llm, tools=[get_weather])
```

---

## 💾 3.4 Persistent Memory (Checkpointing)

By default, the graph loses state when the script ends. To build a chat app, you need memory that survives across HTTP requests. LangGraph uses "Checkpointers" to save the state after every node execution.

### 💡 Java Analogy
*   **Checkpointer** ➡️ Saving the Session State to Redis or a relational database after every request.

### 👨‍💻 Code Example: Memory Saver
```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
# Compile with the checkpointer
graph = builder.compile(checkpointer=memory)

# Execute using a specific thread_id (like a session ID)
config = {"configurable": {"thread_id": "user_123_session_1"}}
graph.invoke({"messages": [HumanMessage("My name is Alice")]}, config=config)

# Later, in a completely new API request using the same thread_id:
graph.invoke({"messages": [HumanMessage("What is my name?")]}, config=config)
# The graph restores the state from memory before running!
```

---

## 📚 Key Terms Glossary
*   **StateGraph**: The core class in LangGraph used to construct the state machine.
*   **TypedDict**: A Python type hint that defines the shape of a dictionary, used to define the schema of the Graph's State.
*   **Annotated / Reducers (`add_messages`)**: Tells LangGraph *how* to update a specific field in the state (e.g., append to a list instead of overwriting it).
*   **Node**: A Python function that takes the State as input and returns a dictionary of updates.
*   **Conditional Edge**: A function that determines the next Node to execute dynamically based on the current State.
*   **ReAct**: A prompting paradigm (Reason + Act) where the LLM talks to itself to solve problems using tools.
*   **Checkpointer**: A mechanism to save the Graph's state at every step to a persistent storage backend (Memory, SQLite, Postgres, Redis).
