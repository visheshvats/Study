# Phase 11 — Scaling & Architecture · Diagrams

## 1. Enterprise architecture (from the roadmap)

The full n-tier deployment: clients → gateway → stateless app tier → shared state → data →
observability. Note that everything mutable lives in the State/Data layers, never in the app tier.

```mermaid
graph TB
    subgraph CLIENTS["Client Layer"]
        WEB["🌐 Web App"]
        MOB["📱 Mobile"]
        EXT["🔌 3rd Party\nAPI Clients"]
    end

    subgraph GW["Gateway Layer"]
        APIGW["API Gateway\n• Auth / JWT\n• Rate Limiting\n• SSL Termination"]
    end

    subgraph APP["Application Layer"]
        ORCH_SVC["Orchestrator Service\nFastAPI"]
        W1["Agent Worker 1"]
        W2["Agent Worker 2"]
        W3["Agent Worker N"]
    end

    subgraph STATE["State & Cache Layer"]
        REDIS[("🟥 Redis\n• Session State\n• Embedding Cache\n• Rate Limit Counters")]
        PG[("🐘 PostgreSQL\n• LangGraph Checkpoints\n• Audit Logs")]
    end

    subgraph DATA["Data Layer"]
        VECTO[("🔵 Vector DB\nPinecone / Weaviate")]
        S3[("☁️ S3\nRaw Documents")]
    end

    subgraph OBS["Observability"]
        SMITH["LangSmith\nTracing"]
        PROM["Prometheus\n+ Grafana"]
    end

    WEB --> APIGW
    MOB --> APIGW
    EXT --> APIGW
    APIGW --> ORCH_SVC
    ORCH_SVC --> W1 & W2 & W3
    ORCH_SVC <--> REDIS
    ORCH_SVC <--> PG
    W1 & W2 & W3 --> VECTO & S3
    ORCH_SVC --> SMITH & PROM
```

---

## 2. Async background-task pattern (new — fills the gap)

The architecture diagram shows *where* the queue sits but not *how a long job flows through it*. This
sequence diagram makes the submit-and-poll pattern from §11.3 concrete — the agent equivalent of
Spring `@Async` + a broker, with the client polling for the result instead of blocking.

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI (Orchestrator)
    participant Q as Celery Broker (Redis)
    participant W as Worker Process
    participant R as Redis (results)

    C->>API: POST /research/async {query}
    API->>Q: enqueue run_research_task(task_id, query)
    API-->>C: 202 {task_id, status:"queued"}   %% returns immediately
    Q->>W: deliver task
    activate W
    W->>W: orchestrator.run(query)  (minutes)
    W->>R: save result:{task_id}
    deactivate W
    loop until done
        C->>API: GET /research/{task_id}
        API->>R: load result:{task_id}
        R-->>API: result or none
        API-->>C: {status:"processing"} or {status:"done", result}
    end
```

**How to read it:** the API never holds the request open for the long job — it enqueues and returns a
`task_id` in milliseconds. A worker process (scaled independently of the API tier) runs the agent and
writes the result to Redis. The client polls a lightweight status endpoint until the result appears.
This decoupling is what keeps the API responsive under long-running agent workloads.
