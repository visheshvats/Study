# MODULE 5: MCP (Model Context Protocol) — Complete Notes

> **For:** Engineers who completed Module 4 (AI Agents) and want to learn the
> emerging standard for connecting AI to the real world.
> **Key insight:** MCP is like a USB port for AI — a universal standard that lets
> any AI model connect to any data source or tool.

---

# LESSON 5.1: What is MCP and Why It Exists

## The Problem Before MCP

In Module 4, we built agents with function calling. Each tool was:
- Hardcoded in the agent's code
- Tightly coupled to the LLM provider (OpenAI format)
- Not reusable across different AI applications
- Built from scratch every time

```
THE N×M PROBLEM (Before MCP):

  AI Applications              Data Sources / Tools
  ┌──────────┐                ┌──────────────┐
  │ ChatGPT  │──┐        ┌──▶│ GitHub API   │
  ├──────────┤  │        │   ├──────────────┤
  │ Claude   │──┼──custom─┼──▶│ Slack API    │
  ├──────────┤  │ code   │   ├──────────────┤
  │ Gemini   │──┤  for   ├──▶│ Database     │
  ├──────────┤  │  each  │   ├──────────────┤
  │ Your App │──┘  pair  └──▶│ File System  │
  └──────────┘                └──────────────┘

  4 apps × 4 tools = 16 custom integrations!
  Every new app or tool adds N more connections.

THE MCP SOLUTION (Universal Standard):

  AI Applications         MCP          Data Sources / Tools
  ┌──────────┐       ┌─────────┐      ┌──────────────┐
  │ ChatGPT  │──┐    │         │  ┌──▶│ GitHub API   │
  ├──────────┤  │    │   MCP   │  │   ├──────────────┤
  │ Claude   │──┼───▶│ Protocol│──┼──▶│ Slack API    │
  ├──────────┤  │    │  (USB)  │  │   ├──────────────┤
  │ Gemini   │──┤    │         │  ├──▶│ Database     │
  ├──────────┤  │    │         │  │   ├──────────────┤
  │ Your App │──┘    └─────────┘  └──▶│ File System  │
  └──────────┘                        └──────────────┘

  4 apps + 4 tools = 8 integrations (each connects to MCP once)
  Every new app or tool adds only 1 more connection!
```

---

## What is MCP?

**Simple:** MCP (Model Context Protocol) is an **open standard** created by Anthropic
that defines how AI applications communicate with external tools and data sources.

**One sentence:** MCP is the USB-C of AI — one standard plug that connects any AI to
any data source.

**Technical:** MCP is a JSON-RPC 2.0 based protocol that defines:
- How to **discover** available tools and resources
- How to **call** tools with parameters
- How to **read** data resources
- How to **use** pre-built prompt templates

**Java Analogy:** MCP is like **JDBC** for AI. Just as JDBC provides a standard interface
for Java to talk to ANY database (MySQL, PostgreSQL, Oracle), MCP provides a standard
interface for ANY AI model to use ANY tool or data source.

```
JDBC Analogy:
  Java App ──▶ JDBC Driver ──▶ PostgreSQL
  Java App ──▶ JDBC Driver ──▶ MySQL
  Java App ──▶ JDBC Driver ──▶ Oracle
  (Same Java code, different databases)

MCP Analogy:
  AI App ──▶ MCP Client ──▶ GitHub MCP Server
  AI App ──▶ MCP Client ──▶ Slack MCP Server
  AI App ──▶ MCP Client ──▶ Database MCP Server
  (Same AI app, different tools)
```

---

## Who Uses MCP?

- **Anthropic** — Created it, Claude Desktop supports MCP natively
- **OpenAI** — Adopted MCP support
- **Google** — Adopted MCP for Gemini
- **Cursor, VS Code** — Code editors using MCP for AI coding assistants
- **Growing ecosystem** — 1000s of MCP servers available for GitHub, Slack, databases, etc.

---

# LESSON 5.2: MCP Architecture

## The Three Components

```
┌──────────────────────────────────────────────────────────────┐
│                    MCP ARCHITECTURE                           │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                      HOST                               │  │
│  │  (The AI application: Claude Desktop, Cursor, Your App)│  │
│  │                                                         │  │
│  │  ┌──────────────┐  ┌──────────────┐                    │  │
│  │  │  MCP CLIENT  │  │  MCP CLIENT  │  ← 1 per server   │  │
│  │  │  (manages    │  │              │                    │  │
│  │  │  connection) │  │              │                    │  │
│  │  └──────┬───────┘  └──────┬───────┘                    │  │
│  └─────────┼─────────────────┼────────────────────────────┘  │
│            │ JSON-RPC        │ JSON-RPC                       │
│            │ (stdio/SSE)     │ (SSE/HTTP)                     │
│            │                 │                                │
│  ┌─────────▼───────┐  ┌─────▼──────────┐                    │
│  │   MCP SERVER    │  │   MCP SERVER   │                    │
│  │  "GitHub"       │  │  "Database"    │                    │
│  │                 │  │                │                    │
│  │  Tools:         │  │  Tools:        │                    │
│  │  • create_issue │  │  • run_query   │                    │
│  │  • list_repos   │  │  • list_tables │                    │
│  │                 │  │                │                    │
│  │  Resources:     │  │  Resources:    │                    │
│  │  • repo files   │  │  • schema      │                    │
│  │  • PR diffs     │  │  • table data  │                    │
│  │                 │  │                │                    │
│  │  Prompts:       │  │  Prompts:      │                    │
│  │  • code_review  │  │  • query_help  │                    │
│  └─────────────────┘  └────────────────┘                    │
└──────────────────────────────────────────────────────────────┘
```

### Component Roles

| Component | Role | Java Analogy |
|-----------|------|-------------|
| **Host** | The AI application that users interact with | Spring Boot Application |
| **Client** | Manages the connection to one MCP server | JDBC Connection/DataSource |
| **Server** | Exposes tools, resources, and prompts | REST API / Microservice |

---

## Transport Mechanisms

```
┌──────────────────────────────────────────────────────┐
│  MCP TRANSPORT OPTIONS                                │
│                                                       │
│  1. STDIO (Standard Input/Output)                    │
│     Client spawns server as a child process.         │
│     Communication via stdin/stdout pipes.            │
│     Best for: Local servers, desktop apps            │
│     Example: Claude Desktop running local MCP server │
│                                                       │
│     ┌────────┐  stdin   ┌────────────┐              │
│     │ Client │─────────▶│ Server     │              │
│     │        │◀─────────│ (process)  │              │
│     └────────┘  stdout  └────────────┘              │
│                                                       │
│  2. SSE (Server-Sent Events) + HTTP                  │
│     Client connects to server over HTTP.             │
│     Server pushes updates via SSE.                   │
│     Best for: Remote servers, cloud deployment       │
│                                                       │
│     ┌────────┐  HTTP    ┌────────────┐              │
│     │ Client │─────────▶│ Server     │              │
│     │        │◀─────────│ (remote)   │              │
│     └────────┘  SSE     └────────────┘              │
│                                                       │
│  Java Analogy:                                       │
│  • STDIO = In-process (like embedded H2)             │
│  • SSE   = Remote (like a REST API service)          │
└──────────────────────────────────────────────────────┘
```

---

# LESSON 5.3: MCP Primitives — What Servers Expose

MCP servers expose three types of capabilities:

## 1. Tools (Model-Controlled)

```
Tools are functions the AI can call (like OpenAI function calling).
The LLM DECIDES when to use them.

Example tool: "create_github_issue"
  Input:  { "repo": "my-app", "title": "Bug", "body": "..." }
  Output: { "issue_number": 42, "url": "..." }

Java Analogy: @RestController endpoints that the AI can call
```

## 2. Resources (Application-Controlled)

```
Resources are READ-ONLY data the application can show to the AI.
The APPLICATION decides when to fetch them (not the AI).

Example resource: "github://repos/my-app/README.md"
  Returns the content of the README file

Java Analogy: @GetMapping endpoints that return data
Like REST resources: GET /api/users/{id}
```

## 3. Prompts (User-Controlled)

```
Prompts are pre-built prompt templates the USER can invoke.
They include the right context and instructions.

Example prompt: "code_review"
  Template: "Review the following code for bugs, security issues,
             and performance problems: {code}"

Java Analogy: Like Thymeleaf templates — pre-built,
             parameterized text that gets filled in at runtime
```

### Comparison Table

```
┌──────────────┬───────────────┬───────────────┬───────────────┐
│              │    TOOLS      │   RESOURCES   │    PROMPTS    │
├──────────────┼───────────────┼───────────────┼───────────────┤
│ Controlled by│ Model (LLM)  │ Application   │ User          │
│ Purpose      │ Actions       │ Data access   │ Templates     │
│ Direction    │ App → Server  │ Server → App  │ Server → User │
│ Analogy      │ POST endpoint │ GET endpoint  │ HTML template │
│ Example      │ create_issue  │ get_file      │ code_review   │
│ Dangerous?   │ Yes (mutates) │ No (read-only)│ No            │
└──────────────┴───────────────┴───────────────┴───────────────┘
```

---

# LESSON 5.4: Building an MCP Server

## MCP Server Structure

```
┌────────────────────────────────────────────────┐
│  MCP SERVER STRUCTURE                          │
│                                                 │
│  my_mcp_server/                                │
│  ├── server.py         ← Main server code      │
│  ├── pyproject.toml    ← Package config         │
│  └── README.md         ← Documentation          │
│                                                 │
│  server.py contains:                           │
│  ┌─────────────────────────────────────────┐   │
│  │ 1. Server initialization                │   │
│  │ 2. Tool definitions (what can be done)  │   │
│  │ 3. Tool handlers (how it's done)        │   │
│  │ 4. Resource definitions (what data)     │   │
│  │ 5. Resource handlers (how to get data)  │   │
│  │ 6. Prompt templates (optional)          │   │
│  │ 7. Server startup                       │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Java Analogy:                                 │
│  This is like a Spring Boot microservice:      │
│  • @RestController = Tool/Resource handlers    │
│  • @Service = Business logic                   │
│  • application.yml = Server configuration      │
│  • pom.xml = pyproject.toml                    │
└────────────────────────────────────────────────┘
```

---

## MCP Server Lifecycle

```
┌──────────────────────────────────────────────────┐
│  MCP CONNECTION LIFECYCLE                         │
│                                                   │
│  1. INITIALIZE                                   │
│     Client connects, exchanges capabilities      │
│     Client: "I support tools and resources"      │
│     Server: "I provide 3 tools and 2 resources"  │
│                                                   │
│  2. DISCOVERY                                    │
│     Client asks: "What tools do you have?"       │
│     Server responds with tool schemas            │
│     Client asks: "What resources do you have?"   │
│     Server responds with resource URIs           │
│                                                   │
│  3. OPERATION                                    │
│     Client calls tools or reads resources        │
│     Server processes and returns results         │
│     (Repeats as needed)                          │
│                                                   │
│  4. SHUTDOWN                                     │
│     Client disconnects gracefully                │
│                                                   │
│  Java Analogy:                                   │
│  Like a Spring WebSocket lifecycle:              │
│  Connect → Handshake → Messages → Disconnect     │
└──────────────────────────────────────────────────┘
```

---

# LESSON 5.5: MCP Configuration

## Claude Desktop Configuration

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json  (Mac)
// %APPDATA%/Claude/claude_desktop_config.json                      (Windows)
// ~/.config/claude/claude_desktop_config.json                      (Linux)
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "API_KEY": "your-key-here"
      }
    },
    "another-server": {
      "command": "npx",
      "args": ["-y", "@some/mcp-server"]
    }
  }
}
```

---

# LESSON 5.6: Code Examples

See the `code/` directory:

1. **`01_mcp_concepts.py`** — MCP protocol explained with code (no server needed)
2. **`02_mcp_server_basic.py`** — Basic MCP server with tools
3. **`03_mcp_server_resources.py`** — MCP server with tools + resources + prompts
4. **`04_mcp_devops_server.py`** — **PROJECT:** DevOps MCP server for infrastructure tasks

---

# LESSON 5.7: Exercises

## Exercise 1: Concept Check
1. What problem does MCP solve? (The N×M problem)
2. What are the 3 MCP primitives and who controls each?
3. How is MCP different from OpenAI function calling?
4. What transport mechanisms does MCP support?

## Exercise 2: Design an MCP Server
1. Design tools, resources, and prompts for a "Jira MCP Server"
2. Define at least 3 tools (create_issue, assign_issue, get_sprint)
3. Define at least 2 resources (project://MYPROJ/backlog, sprint://current)
4. Write the tool schemas in JSON

## Exercise 3: Build
1. Build an MCP server for a use case relevant to your work
2. Test it with the MCP Inspector tool
3. Configure it with Claude Desktop

---

# LESSON 5.8: Interview Questions & Answers

## Q1: What is MCP and what problem does it solve?

**Answer:** MCP (Model Context Protocol) is an open standard by Anthropic that defines
how AI applications communicate with external tools and data sources. It solves the
**N×M integration problem**: without MCP, every AI application needs custom code for
every data source (N apps × M tools = N×M integrations). With MCP, each app implements
one MCP client and each tool implements one MCP server, reducing to N+M integrations.
It's analogous to JDBC in Java — one standard interface for all databases.

## Q2: Explain the MCP architecture: hosts, clients, and servers.

**Answer:** **Host**: The AI application users interact with (Claude Desktop, Cursor, your app).
It manages one or more MCP clients. **Client**: Manages the connection to a single MCP
server. Handles protocol negotiation, capability discovery, and message routing. One client
per server connection. **Server**: Exposes capabilities (tools, resources, prompts) over
the MCP protocol. Runs as a separate process (stdio) or remote service (SSE/HTTP).
Communication uses JSON-RPC 2.0 over the chosen transport.

## Q3: What are MCP primitives and how do they differ?

**Answer:** Three primitives: (1) **Tools** — model-controlled actions the LLM can invoke
(like function calling). Example: `create_github_issue()`. Can be dangerous (mutations).
(2) **Resources** — application-controlled read-only data. Example: `github://repo/file.py`.
Safe (read-only). (3) **Prompts** — user-controlled prompt templates with built-in context.
Example: `code_review` template. The key difference is **who controls invocation**: LLM
decides tools, application decides resources, user decides prompts.

## Q4: How is MCP different from OpenAI function calling?

**Answer:** OpenAI function calling is a **proprietary mechanism** tied to OpenAI's API.
MCP is an **open standard** that works with any AI provider. Key differences:
(1) **Standardization** — MCP tools work with Claude, ChatGPT, Gemini; function calling
is OpenAI-only, (2) **Discovery** — MCP supports dynamic tool discovery; function calling
requires hardcoded definitions, (3) **Resources** — MCP adds read-only data access;
function calling only has tools, (4) **Transport** — MCP supports stdio and SSE; function
calling is HTTP-only, (5) **Ecosystem** — MCP servers are reusable across applications;
function call implementations are app-specific.

## Q5: When would you build an MCP server vs use direct API integration?

**Answer:** Build an MCP server when: (1) Multiple AI apps need the same integration
(reusability), (2) You want to future-proof against AI provider changes, (3) You want
to leverage the growing MCP ecosystem, (4) The integration involves both tools AND
data resources. Use direct API integration when: (1) Only one app needs it, (2) You need
ultra-low latency (MCP adds a protocol layer), (3) The integration is trivial (single
function call).

## Q6: How would you secure an MCP server in production?

**Answer:** Security layers: (1) **Authentication** — require API keys or OAuth tokens
in environment variables, validate on every request, (2) **Authorization** — check if the
caller has permission for the requested tool/resource, (3) **Input validation** — validate
all tool parameters (like REST API input validation), (4) **Rate limiting** — prevent
abuse of expensive tools, (5) **Audit logging** — log all tool calls with caller identity,
(6) **Least privilege** — server should have minimal permissions on the systems it connects
to, (7) **Transport security** — use HTTPS for SSE transport, (8) **Sandboxing** — run
server in a container with limited access.

---

# Common Mistakes

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| Building everything as tools | Resources exist for read-only data | Use resources for data, tools for actions |
| No input validation | Security vulnerability | Validate all tool parameters |
| Vague tool descriptions | LLM picks wrong tools | Write detailed 2-3 sentence descriptions |
| Hardcoding credentials | Security risk | Use environment variables |
| No error handling | Server crashes break the AI app | Return structured error messages |
| Ignoring MCP for custom integrations | Missed reusability | Use MCP for any integration other apps might need |

---

# Best Practices

1. **Use MCP for reusable integrations** — if 2+ apps need it, make it MCP
2. **Clear tool descriptions** — the LLM reads these to decide when to use them
3. **Validate all inputs** — treat tool calls like untrusted REST requests
4. **Use resources for read-only data** — don't make everything a tool
5. **Environment variables for secrets** — never hardcode API keys
6. **Structured error messages** — return errors the LLM can understand
7. **Test with MCP Inspector** — official testing tool for MCP servers
8. **Document your server** — README with available tools, resources, and config
9. **Version your server** — breaking changes need version bumps
10. **Log everything** — tool calls, errors, and performance metrics

---

**Next Module:** [Module 6 — Agentic AI Architecture (Advanced) →](../module-6-agentic-architecture/)

Say **NEXT** to continue.
