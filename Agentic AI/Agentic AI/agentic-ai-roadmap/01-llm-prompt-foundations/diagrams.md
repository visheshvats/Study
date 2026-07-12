# Phase 01: LLM & Prompt Foundations — Diagrams

## 1. Core Concepts Diagram (Stateless API)
This diagram illustrates the stateless nature of the LLM API. The developer must assemble the full context window on every request.

```mermaid
graph TD
    subgraph LLM_API["LLM API Call"]
        SYS["System Prompt\n(Personality / Instructions)"] --> MODEL["LLM\nclaude-sonnet-4-6"]
        USR["User Messages\n(Conversation history)"] --> MODEL
        TEMP["Temperature\n0 = deterministic\n1 = creative"] --> MODEL
        CTX["Context Window\nMax tokens in + out"] --> MODEL
        MODEL --> OUT["Response\nText | Tool Call | Both"]
    end
```

## 2. Tool Calling (Function Calling) Sequence Diagram
*New diagram added to clarify the complex multi-step process of Tool Calling.*

When an LLM uses a tool, it doesn't execute the code itself. It simply asks your application to run the code on its behalf. This requires a round-trip loop.

```mermaid
sequenceDiagram
    participant User
    participant App as Python Application
    participant LLM as Anthropic API
    participant DB as Internal Database

    User->>App: "What is the status of ticket TKT-123?"
    App->>LLM: Send Message + Tool Definitions (e.g., `get_ticket`)
    
    Note over LLM: LLM decides it cannot answer<br/>without external data.
    LLM-->>App: ToolUseRequest(name="get_ticket", args={"id": "TKT-123"})
    
    Note over App: App intercepts request and<br/>executes local Python function.
    App->>DB: SELECT status FROM tickets WHERE id='TKT-123'
    DB-->>App: {"status": "RESOLVED"}
    
    App->>LLM: Send original history + ToolResult(content={"status": "RESOLVED"})
    
    Note over LLM: LLM reads the tool result<br/>and formulates a natural response.
    LLM-->>App: TextResponse("Ticket TKT-123 is currently resolved.")
    App-->>User: "Ticket TKT-123 is currently resolved."
```

### Why this matters for AI Engineering
In enterprise Java, this is conceptually similar to a saga pattern or an orchestration orchestrator (like Netflix Conductor), where the LLM acts as the orchestrator deciding *which* service to call next based on the state, and your Python code acts as the worker executing the task and reporting back.
