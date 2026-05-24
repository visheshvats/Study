# Model Context Protocol (MCP) — Client-Server Lifecycle Specification

## Overview

The **Model Context Protocol (MCP)** is an open standard that enables AI models (clients) to securely interact with external tools, data sources, and services (servers) through a structured, transport-agnostic interface.

MCP decouples the **semantic reasoning loop** (what the model decides to do) from the **execution layer** (how actions are carried out), creating a clean separation of concerns identical to the client-server paradigm in distributed systems.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        MCP HOST APPLICATION                      │
│  (IDE, Chat UI, Agent Framework — e.g., Claude Desktop, Cursor)  │
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│   │  MCP Client  │    │  MCP Client  │    │  MCP Client  │        │
│   │  (Session 1) │    │  (Session 2) │    │  (Session 3) │        │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│          │                  │                  │                  │
└──────────┼──────────────────┼──────────────────┼─────────────────┘
           │                  │                  │
    ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
    │  MCP Server  │    │  MCP Server  │    │  MCP Server  │
    │  (Database)  │    │   (GitHub)   │    │  (Payments)  │
    └─────────────┘    └─────────────┘    └─────────────┘
```

### Key Roles

| Component   | Responsibility                                                       |
|-------------|----------------------------------------------------------------------|
| **Host**    | The application housing the LLM (IDE, chat interface, agent runtime) |
| **Client**  | Maintains a 1:1 session with a specific MCP server                   |
| **Server**  | Exposes tools, resources, and prompts to the client                  |

---

## Protocol Primitives

MCP defines three categories of capabilities that servers can expose:

### 1. Tools (Model-Controlled)
Executable functions that the LLM can invoke based on its reasoning.

```json
{
  "name": "query_database",
  "description": "Execute a read-only SQL query against the analytics database",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "SQL SELECT statement" },
      "limit": { "type": "integer", "default": 100 }
    },
    "required": ["query"]
  }
}
```

### 2. Resources (Application-Controlled)
Contextual data exposed by the server (files, database schemas, API docs). The host application decides when to include these in the model's context.

```json
{
  "uri": "db://analytics/schema",
  "name": "Analytics Database Schema",
  "mimeType": "application/json",
  "description": "Table definitions, column types, and relationships"
}
```

### 3. Prompts (User-Controlled)
Pre-built prompt templates that users can invoke explicitly.

```json
{
  "name": "explain_query_plan",
  "description": "Explain a SQL query execution plan in plain language",
  "arguments": [
    { "name": "query", "description": "The SQL query to analyze", "required": true }
  ]
}
```

---

## Connection Lifecycle

### Phase 1: Discovery & Initialization

```
Client                           Server
  │                                │
  │──── initialize ───────────────▶│
  │     {protocolVersion, capabilities}
  │                                │
  │◀─── initialize response ──────│
  │     {protocolVersion, capabilities, serverInfo}
  │                                │
  │──── initialized notification ─▶│
  │                                │
```

1. Client sends `initialize` with its protocol version and capabilities.
2. Server responds with its own capabilities and supported protocol version.
3. Client sends `initialized` notification to confirm the session is active.

### Phase 2: Capability Negotiation

During initialization, both sides declare supported features:

| Capability       | Client                   | Server                         |
|------------------|--------------------------|--------------------------------|
| `tools`          | Can invoke tools         | Exposes callable tools         |
| `resources`      | Can read resources       | Exposes contextual data        |
| `prompts`        | Can use prompt templates | Exposes prompt templates       |
| `logging`        | Can receive log messages | Can emit structured logs       |
| `sampling`       | Supports model sampling  | Can request LLM completions    |

### Phase 3: Operation (Steady State)

```
User Query: "What were our top 10 products last quarter?"
    │
    ▼
┌─────────┐    tools/list    ┌──────────┐
│  Client  │────────────────▶│  Server   │
│  (LLM)   │◀───────────────│ (DB Tool) │
│          │  [query_database]│           │
│          │                  │           │
│          │  tools/call      │           │
│          │  {query: "SELECT...", limit: 10}
│          │─────────────────▶│           │
│          │◀────────────────│           │
│          │  {result: [...]} │           │
└─────────┘                  └──────────┘
    │
    ▼
Generated Answer: "The top 10 products by revenue last quarter were..."
```

### Phase 4: Shutdown

```
Client                           Server
  │                                │
  │──── shutdown request ─────────▶│
  │◀─── shutdown response ────────│
  │──── exit notification ────────▶│
  │                                │
  ×                                ×
```

---

## Transport Layers

MCP is transport-agnostic. Two standard transports are defined:

### 1. stdio (Standard I/O)
- Server runs as a **child process** of the host
- Communication via `stdin` / `stdout`
- Best for: local tools, CLI integrations, development

```
Host Process
  └── spawns → Server Process
        ├── stdin  ← JSON-RPC messages from client
        └── stdout → JSON-RPC messages to client
```

### 2. HTTP + Server-Sent Events (SSE)
- Server runs as an **independent HTTP service**
- Client sends requests via HTTP POST
- Server streams responses via SSE
- Best for: remote servers, cloud deployments, shared services

```
Client ──POST──▶ https://mcp.example.com/rpc
Client ◀──SSE───  https://mcp.example.com/events
```

---

## Message Format (JSON-RPC 2.0)

All MCP messages follow the JSON-RPC 2.0 specification:

### Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "query_database",
    "arguments": { "query": "SELECT * FROM products LIMIT 5" }
  }
}
```

### Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      { "type": "text", "text": "[{\"id\": 1, \"name\": \"Widget\", ...}]" }
    ]
  }
}
```

### Notification (no response expected)
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/updated",
  "params": { "uri": "db://analytics/schema" }
}
```

---

## Security Model

| Concern              | Mitigation                                                      |
|----------------------|-----------------------------------------------------------------|
| **Input Validation** | Servers validate all tool inputs against JSON Schema             |
| **Least Privilege**  | Servers expose only necessary tools; clients request only needed capabilities |
| **Transport Security** | HTTPS/TLS for remote transports; process isolation for stdio  |
| **Rate Limiting**    | Servers implement per-client rate limits                         |
| **Audit Logging**    | All tool invocations are logged with timestamps and parameters   |
| **Human-in-the-Loop** | Hosts can require user approval before executing sensitive tools |

---

## Implementation Checklist

- [ ] Define tool schemas with precise `inputSchema` JSON Schema definitions
- [ ] Implement `initialize` / `initialized` handshake
- [ ] Handle `tools/list` and `tools/call` methods
- [ ] Add error handling with standard JSON-RPC error codes
- [ ] Support at least one transport (stdio recommended for local development)
- [ ] Implement graceful shutdown via `shutdown` / `exit` lifecycle
- [ ] Add structured logging for debugging
- [ ] Write integration tests covering the full lifecycle

---

## References

- [MCP Specification (modelcontextprotocol.io)](https://modelcontextprotocol.io)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
