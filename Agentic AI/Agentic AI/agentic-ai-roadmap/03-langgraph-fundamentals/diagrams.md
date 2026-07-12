# Phase 03: LangGraph Fundamentals — Diagrams

## 1. LangGraph Mental Model (State Machine)
This diagram illustrates the core architecture of a LangGraph application, acting as a state machine where nodes update a shared state object.

```mermaid
stateDiagram-v2
    [*] --> Node_A : Entry Point
    Node_A --> Node_B : Edge (unconditional)
    Node_A --> Node_C : Conditional Edge
    Node_B --> Node_A : Loop
    Node_C --> [*] : END

    note right of Node_A
        Node = function(state) → partial_state
        Edge = transition rule
        State = shared TypedDict
        Conditional = routing function
    end note
```

## 2. Checkpointing and State Persistence Flow
*New diagram added to visualize how persistent memory (checkpointing) allows an Agent to remember context across disparate API requests.*

Unlike Java web apps that might hold session state in memory while a user is active, AI Agents often run as stateless cloud functions. LangGraph Checkpointing saves the exact state of the graph after every node, allowing a graph to be "paused" and "resumed" perfectly.

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI / API Gateway
    participant LG as LangGraph (Agent)
    participant DB as Checkpointer (e.g., Postgres/Redis)

    Note over User, DB: Turn 1: Initializing State
    User->>API: "Hi, I'm Alice." (thread_id: 123)
    API->>LG: invoke(thread_id: 123)
    LG->>DB: Fetch state for thread_id 123 (Empty)
    Note over LG: Node 1 executes...
    LG->>DB: Checkpoint: Save {"messages": ["Hi, I'm Alice"]}
    LG-->>API: Response: "Hello Alice!"
    API-->>User: "Hello Alice!"

    Note over User, DB: Turn 2: Resuming State (Minutes or Days Later)
    User->>API: "What is my name?" (thread_id: 123)
    API->>LG: invoke(thread_id: 123)
    LG->>DB: Fetch state for thread_id 123
    DB-->>LG: Returns {"messages": ["Hi, I'm Alice"]}
    Note over LG: Node 1 executes with full context...
    LG->>DB: Checkpoint: Save {"messages": [..., "What is my name?"]}
    LG-->>API: Response: "Your name is Alice."
    API-->>User: "Your name is Alice."
```

### Why this matters for AI Engineering
In enterprise Java, this is equivalent to Event Sourcing or CQRS. You aren't just saving the final state; the Checkpointer saves a snapshot at *every superstep* (every node execution). This allows for advanced features like "Time Travel" — rewinding an agent to a previous state, fixing a mistake, and letting it run again.
