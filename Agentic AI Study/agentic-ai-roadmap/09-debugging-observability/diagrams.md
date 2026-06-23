# Phase 9 — Diagrams

The source roadmap has no Mermaid diagram for this phase, so here are two that make the observability picture concrete. Both render on GitHub and in any Mermaid-aware Markdown viewer.

---

## 1. The observability stack (flowchart)

This is the "where does each signal go and who looks at it" map — the agentic counterpart of a diagram showing your Spring service emitting to Jaeger, your JSON logs flowing to a log aggregator, and your Micrometer metrics feeding a dashboard with alerts. One application/graph emits **three independent observability signals**: traces (LangSmith), structured logs, and token/cost metrics. Each lands in a different place and answers a different question — traces show the call tree, logs show the ordered narrative, and the token tracker shows the running bill — and the cost stream is the one you wire an alert on so a runaway loop pages you before the invoice does.

```mermaid
flowchart TD
    APP["App / LangGraph agent<br/>(nodes wrapped with @logged_node)"]

    APP -->|"auto-instrument + @traceable spans"| LS["LangSmith<br/>traces + spans"]
    APP -->|"logging (INFO / ERROR)"| LOG["Structured logs<br/>StreamHandler + FileHandler"]
    APP -->|"response.usage per call"| TT["TokenTracker<br/>per-call + session cost"]

    LS --> SMITH["smith.langchain.com<br/>(flame-graph view ≈ Jaeger UI)"]
    LOG --> CONSOLE["Console<br/>(live tail)"]
    LOG --> FILE["agent_YYYYMMDD.log<br/>(grep / ship to aggregator)"]
    TT --> COST["Cost log line + dashboard<br/>(≈ Micrometer gauge)"]
    COST --> ALERT["Budget alert<br/>(page before the bill)"]

    classDef signal fill:#1f6feb,stroke:#0b2447,color:#fff;
    classDef sink fill:#0b2447,stroke:#1f6feb,color:#fff;
    class LS,LOG,TT signal;
    class SMITH,CONSOLE,FILE,COST,ALERT sink;
```

---

## 2. One request through a `@logged_node`-wrapped node (sequence diagram)

This zooms into a single node call to show the AOP `@Around` shape of `@logged_node`: it logs on **enter**, calls the real node (`joinPoint.proceed()`), tracks tokens, then logs on **exit**. The bottom `alt` block is the critical bit — on the error path the wrapper logs the exception **and re-raises it** (`exc_info=True`, then `raise`). It never swallows the failure, so the caller still sees the error and the run fails *visibly* instead of marching on with corrupted state.

```mermaid
sequenceDiagram
    autonumber
    participant Caller as Graph runtime
    participant Wrap as @logged_node wrapper
    participant Node as Real node fn
    participant LLM as LLM call
    participant TT as TokenTracker
    participant Log as logger

    Caller->>Wrap: invoke(state)
    Wrap->>Log: INFO "→ [node] State keys: [...]"  (enter)
    Wrap->>Node: fn(state)            %% joinPoint.proceed()
    Node->>LLM: messages.create(...)
    LLM-->>Node: response (+ usage)

    alt success
        Node->>TT: track(response)
        TT-->>Node: {this_call, session_total}
        Node->>Log: INFO "Token usage: {...}"
        Node-->>Wrap: result state
        Wrap->>Log: INFO "← [node] Done in 0.42s"  (exit)
        Wrap-->>Caller: result state
    else exception in node
        Node-->>Wrap: raises Exception
        Wrap->>Log: ERROR "✗ [node] FAILED: ..." (exc_info=True)
        Wrap-->>Caller: re-raise (never swallow)
    end
```
