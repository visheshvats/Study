# Topic 11: Model Context Protocol (MCP)

> **Java Analogy:** MCP is like **JDBC for AI tools**. Just as JDBC provides a standard interface for Java applications to connect to *any* database (MySQL, PostgreSQL, Oracle) without custom code per vendor, MCP provides a standard interface for LLMs to connect to *any* external tool (databases, APIs, file systems) without custom integration per tool.

---

## What This Is (Plain English)

Before MCP, every tool integration with an LLM required custom glue code — different JSON schemas for OpenAI function calling vs Anthropic tool use vs Google function declarations. MCP standardizes this: an MCP server exposes tools with a standard schema, and any MCP-compatible client (Claude Desktop, VS Code, your Java app) can connect to it. Write the server once, use it everywhere.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **MCP Protocol** | Like JDBC — a standard interface spec. All implementations follow the same contract. |
| **MCP Server** | Like a JDBC Driver — implements the spec for a specific data source (PostgreSQL driver, Redis driver). |
| **MCP Client** | Like `DataSource` / `JdbcTemplate` — the consumer side that talks to any server via the standard protocol. |
| **Tools** | Like `@RequestMapping` endpoints — named functions with input schemas that the LLM can call. |
| **Resources** | Like `@ConfigurationProperties` — read-only contextual data injected into the model's context. |
| **Prompts** | Like `@Query` templates — pre-built prompt templates the user can invoke. |
| **JSON-RPC 2.0** | Like JAX-RS with JSON — the wire format for client-server communication. |
| **Capability negotiation** | Like TLS handshake — both sides declare what they support before proceeding. |

---

## MCP Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Host Application│     │  MCP Client       │     │  MCP Server       │
│  (Your Java App) │────▶│  (Protocol Layer) │────▶│  (Tool Provider)  │
│                  │     │                    │     │                    │
│  • Spring Boot   │     │  • Sends requests  │     │  • Exposes tools   │
│  • LLM API call  │     │  • Handles responses│     │  • Validates input │
│  • UI/API        │     │  • Session mgmt    │     │  • Executes logic  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                              │         │
                        ┌─────┘         └─────┐
                    stdio transport      HTTP+SSE transport
                    (local process)      (remote service)
```

---

## The Three MCP Primitives

| Primitive | Controlled By | Example | Java Analogy |
|---|---|---|---|
| **Tools** | Model decides when to call | `query_database(sql)`, `send_email(to, subject)` | `@Tool`-annotated methods |
| **Resources** | Application decides when to include | Database schema, file contents, API docs | `@ConfigurationProperties`, static context |
| **Prompts** | User explicitly invokes | "Explain this SQL query plan" | Pre-built `@Query` templates |

---

## Code Bridge

### Building an MCP Server in Java (Spring Boot)

```java
// Using the MCP Java SDK (io.modelcontextprotocol:sdk)
@SpringBootApplication
public class BankingMcpServer {

    @Bean
    public McpServer mcpServer() {
        return McpServer.builder()
            .name("banking-tools")
            .version("1.0.0")
            .tool(getAccountBalance())
            .tool(getTransactionHistory())
            .tool(initiateRefund())
            .build();
    }

    private Tool getAccountBalance() {
        return Tool.builder()
            .name("get_account_balance")
            .description("""
                Get the current balance for a bank account.
                Use when the user asks about their balance, available funds,
                or account status. Requires the account number.
                """)
            .inputSchema(JsonSchema.builder()
                .property("account_number", JsonSchema.string()
                    .description("10-digit bank account number"))
                .required("account_number")
                .build())
            .handler(args -> {
                String accountNo = args.get("account_number").asText();
                // Call your existing banking service
                AccountBalance balance = bankingService.getBalance(accountNo);
                return new ToolResult("""
                    Account: %s
                    Available Balance: ₹%,.2f
                    Last Updated: %s
                    """.formatted(accountNo, balance.amount(), balance.timestamp()));
            })
            .build();
    }

    private Tool initiateRefund() {
        return Tool.builder()
            .name("initiate_refund")
            .description("""
                Initiate a refund for a failed transaction.
                Only use when the user explicitly requests a refund AND
                provides a transaction ID. Do NOT call for general inquiries.
                """)
            .inputSchema(JsonSchema.builder()
                .property("transaction_id", JsonSchema.string())
                .property("reason", JsonSchema.string())
                .required("transaction_id", "reason")
                .build())
            .handler(args -> {
                // Your existing refund service
                RefundResult result = refundService.initiate(
                    args.get("transaction_id").asText(),
                    args.get("reason").asText()
                );
                return new ToolResult("Refund initiated. Reference: " + result.refId());
            })
            .build();
    }
}
```

### Connecting to MCP Server from Java Client

```java
@Service
public class McpClientService {

    public void connectAndUse() {
        // Connect via stdio (local process)
        McpClient client = McpClient.builder()
            .transport(new StdioTransport("java", "-jar", "banking-mcp-server.jar"))
            .build();

        client.initialize();

        // Discover available tools
        List<Tool> tools = client.listTools();
        tools.forEach(t -> System.out.println("Tool: " + t.name()));

        // Call a tool
        ToolResult result = client.callTool("get_account_balance",
            Map.of("account_number", "1234567890"));
        System.out.println(result.content());

        client.shutdown();
    }
}
```

### LLM + MCP Integration Flow

```java
@Service
public class AiAssistantWithTools {
    private final ChatLanguageModel model;
    private final McpClient mcpClient;

    public String handleQuery(String userQuery) {
        // 1. Send user query to LLM with tool descriptions
        List<ToolSpec> tools = mcpClient.listTools().stream()
            .map(t -> new ToolSpec(t.name(), t.description(), t.inputSchema()))
            .toList();

        ChatResponse response = model.chat(userQuery, tools);

        // 2. If LLM wants to call a tool
        if (response.hasToolCalls()) {
            for (ToolCall call : response.toolCalls()) {
                // 3. Execute via MCP
                ToolResult result = mcpClient.callTool(call.name(), call.arguments());
                // 4. Feed result back to LLM
                response = model.chat(
                    userQuery, tools, 
                    List.of(call), List.of(result)
                );
            }
        }

        return response.text();
    }
}
```

---

## Transport Options

| Transport | When to Use | Java Implementation |
|---|---|---|
| **stdio** | Local tools on the same machine. IDE plugins, CLI tools. | `ProcessBuilder` spawns the server as a child process. Communication via stdin/stdout. |
| **HTTP + SSE** | Remote/shared services. Microservice architecture. | Standard Spring Boot `@RestController` + SSE for streaming responses. |

---

## Tool Description Quality — The Make-or-Break Factor

```java
// ❌ BAD — LLM won't know when to call this
Tool.builder()
    .name("do_thing")
    .description("Does stuff with the data")

// ✅ GOOD — LLM knows exactly when and how to call this
Tool.builder()
    .name("get_account_balance")
    .description("""
        Retrieve the current available balance for a bank account.
        
        USE THIS WHEN: The user asks about their balance, available funds,
        remaining amount, or account status.
        
        DO NOT USE WHEN: The user asks about transaction history 
        (use get_transaction_history instead).
        
        RETURNS: Account number, available balance in INR, and last updated timestamp.
        """)
```

---

## Interview-Ready Summary

- MCP is a standard protocol (JSON-RPC 2.0) for connecting LLMs to external tools.
- Three primitives: Tools (model-controlled), Resources (app-controlled), Prompts (user-controlled).
- Two transports: stdio (local) and HTTP+SSE (remote).
- Think of it as JDBC for AI tools — write the server once, connect from any client.
- Tool descriptions are critical — the LLM decides what to call based solely on the description text.
- In Java: use the MCP Java SDK to build servers, Spring AI / LangChain4j to build clients.
- Always include input validation, human approval for sensitive actions, and rate limiting.
