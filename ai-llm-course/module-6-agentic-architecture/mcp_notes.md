# Model Context Protocol (MCP) — Comprehensive Notes

## 1. What is MCP?

**MCP** stands for **Model Context Protocol**. It was introduced by **Anthropic** (the company behind Claude).

> **In simple terms:** MCP is a standardized way for LLMs (like Claude) to talk to external, real-world applications and services — Slack, GitHub, Google Drive, Zerodha, Blender, Kubernetes, and more.

### The Problem MCP Solves

Traditionally, if you want to interact with a service like Zerodha (a stock trading platform), you use a **web browser** or a **mobile app**. Your frontend sends HTTP requests to the backend.

But what if you want to do the same thing through an LLM? For example:
> *"Hey Claude, buy one stock of HDFC Bank on my Zerodha account."*

Two challenges arise:
1. **Authentication** — How does Claude access your specific account?
2. **API Knowledge** — How does Claude know which API endpoints to call, what parameters to send, etc.?

**MCP solves challenge #2.** It gives the model **context** about an application — what actions are available, what inputs they need, and what they return.

### The Architecture

```
┌──────────┐       ┌────────────┐       ┌──────────────────┐
│  LLM     │ ───── │ MCP Server │ ───── │ External Service │
│ (Claude) │  MCP  │  (Bridge)  │ HTTP  │   (e.g. Zerodha) │
└──────────┘       └────────────┘       └──────────────────┘
```

- The **MCP Server** sits as a **bridge/proxy** between the LLM and the external service.
- The LLM communicates with the MCP Server using the MCP specification.
- The MCP Server translates those requests into actual API calls to the external service.

### Key Analogy

Think of MCP like creating a **translator** between Claude and any backend. The backend already has functionality (buy stock, send message, create file). The MCP server just **exposes** that functionality in a format the LLM can understand and use.

---

## 2. MCP Servers in the Wild

There are hundreds of MCP servers already available at: [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

### Notable Examples

| MCP Server | What It Does |
|---|---|
| **Brave Search** | Lets the LLM search the web via Brave Search API |
| **GitHub** | Read repos, manage issues, PRs — all through Claude |
| **Blender** | Control 3D modeling software via natural language |
| **Webflow** | Edit/manage websites through chat |
| **YouTube** | Manage videos, thumbnails, titles |
| **Kubernetes** | Scale deployments, manage clusters via natural language |
| **AWS** | Interact with AWS services |

### Best Use Cases for MCP

MCP shines for applications that are **complex to use via GUI** — heavy SaaS tools like Blender, where users can open Claude on one side and Blender on the other, describing what they want in plain English.

### SDK Support

MCP servers can be written in any language. Official SDKs exist for:
- **TypeScript** (most popular)
- **Python**
- **Rust**
- **Kotlin / Java**

---

## 3. Programmatic Trading with Zerodha (Pre-MCP)

Before building the MCP server, the video demonstrates how to trade programmatically on Zerodha using their JavaScript SDK — **no AI involved yet**.

> **Note:** The video uses JavaScript/TypeScript. Below, each code block is shown in **both JS and Java** so you can compare.

### Step 1: Create a Zerodha Developer App

1. Go to [developers.kite.trade](https://developers.kite.trade)
2. Create a new application (e.g., "Trade GPT")
3. Provide a **Redirect URL** (e.g., `http://localhost:3000/trade/redirect`)
4. You receive an **API Key** and **API Secret**

### Step 2: OAuth Authentication Flow

Zerodha uses standard **OAuth** (like "Login with Google"):

```
User clicks "Login with Zerodha"
        │
        ▼
Redirected to kite.zerodha.com
        │
        ▼
User approves the app ("Authorize Trade GPT")
        │
        ▼
Zerodha redirects back to YOUR redirect URL
with a one-time "request_token" in the query params
        │
        ▼
You exchange the request_token for a long-lived "access_token"
using kc.generateSession(requestToken, apiSecret)  // JS
using kiteConnect.generateSession(requestToken, apiSecret)  // Java
        │
        ▼
Use the access_token for all future API calls
```

> **Important:**
> - The **request token** is **one-time use only**. You cannot reuse it.
> - The **access token** is long-lived and should be cached/stored.

### Step 3: Place Orders via SDK

**JavaScript:**
```javascript
import KiteConnect from "kiteconnect";

const kc = new KiteConnect({ api_key: "YOUR_API_KEY" });
kc.setAccessToken("YOUR_ACCESS_TOKEN");

// Buy 1 stock of HDFC Bank
await kc.placeOrder("regular", {
  exchange: "NSE",
  tradingsymbol: "HDFCBANK",
  transaction_type: "BUY",
  quantity: 1,
  product: "CNC",        // CNC = long-term, MIS = intraday
  order_type: "MARKET",  // MARKET or LIMIT
});
```

**Java equivalent:**
```java
import com.zerodhatech.kiteconnect.KiteConnect;
import com.zerodhatech.models.Order;
import com.zerodhatech.models.OrderParams;

public class TradeExample {
    public static void main(String[] args) throws Exception {
        KiteConnect kc = new KiteConnect("YOUR_API_KEY");
        kc.setAccessToken("YOUR_ACCESS_TOKEN");

        // Buy 1 stock of HDFC Bank
        OrderParams params = new OrderParams();
        params.exchange = "NSE";
        params.tradingsymbol = "HDFCBANK";
        params.transactionType = "BUY";
        params.quantity = 1;
        params.product = "CNC";      // CNC = long-term, MIS = intraday
        params.orderType = "MARKET"; // MARKET or LIMIT

        Order order = kc.placeOrder(params, "regular");
        System.out.println("Order placed: " + order.orderId);
    }
}
```

### Step 4: Create Reusable Functions

**JavaScript:**
```javascript
// trade.ts
export async function placeOrder(symbol, quantity, type) {
  await kc.placeOrder("regular", {
    exchange: "NSE",
    tradingsymbol: symbol,
    transaction_type: type,
    quantity: quantity,
    product: "CNC",
    order_type: "MARKET",
  });
}
```

**Java equivalent:**
```java
// TradeService.java
public class TradeService {
    private final KiteConnect kc;

    public TradeService(KiteConnect kc) {
        this.kc = kc;
    }

    public Order placeOrder(String symbol, int quantity, String type) throws Exception {
        OrderParams params = new OrderParams();
        params.exchange = "NSE";
        params.tradingsymbol = symbol;
        params.transactionType = type;  // "BUY" or "SELL"
        params.quantity = quantity;
        params.product = "CNC";
        params.orderType = "MARKET";

        return kc.placeOrder(params, "regular");
    }
}
```

---

## 4. Building the MCP Server

This is the core of the lesson — creating an MCP server that **exposes** trading functionality to the LLM.

### Step 1: Install the MCP SDK

**JavaScript:**
```bash
bun add @modelcontextprotocol/sdk
```

**Java (Maven — add to `pom.xml`):**
```xml
<dependency>
    <groupId>io.modelcontextprotocol</groupId>
    <artifactId>sdk</artifactId>
    <version>0.8.1</version>
</dependency>
```

### Step 2: Create the MCP Server

**JavaScript:**
```javascript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "Trade MCP Server",
  version: "1.0.0",
});
```

**Java equivalent:**
```java
import io.modelcontextprotocol.server.McpServer;
import io.modelcontextprotocol.server.McpServerFeatures;
import io.modelcontextprotocol.server.transport.StdioServerTransportProvider;
import io.modelcontextprotocol.spec.McpSchema;

McpServer server = McpServer.sync(
    new StdioServerTransportProvider()
).serverInfo(
    new McpSchema.Implementation("Trade MCP Server", "1.0.0")
).build();
```

> **JS analogy:** Think of this as `const app = express()` — you're initializing a server instance.
> **Java analogy:** Think of this as `SpringApplication.run(App.class)` — you're bootstrapping the server.

### Step 3: Define Tools

**Tools** are the core primitive. A tool is an action the LLM can execute on the server.

#### Tool Structure

Each tool has:
1. **Name** — unique identifier (no spaces/special chars)
2. **Description** — tells the LLM what this tool does
3. **Input Schema** — defines required inputs using [Zod](https://zod.dev/) in JS, or JSON Schema strings in Java
4. **Handler Function** — the actual code that runs when the tool is called (a callback in JS, a `ToolHandler` in Java)

#### Example Tools

**JavaScript:**
```javascript
// Tool 1: Add two numbers
server.tool("add_two_numbers", "Adds two numbers", {
  a: z.number(),
  b: z.number(),
}, async ({ a, b }) => {
  return { content: [{ type: "text", text: String(a + b) }] };
});

// Tool 2: Buy a stock
server.tool("buy_stock", "Buys a stock on the Zerodha exchange. Executes a REAL order.", {
  stock: z.string(),
  quantity: z.number(),
}, async ({ stock, quantity }) => {
  await placeOrder(stock, quantity, "BUY");
  return { content: [{ type: "text", text: `${stock} has been bought.` }] };
});

// Tool 3: Sell a stock
server.tool("sell_stock", "Sells a stock on the Zerodha exchange. Executes a REAL order.", {
  stock: z.string(),
  quantity: z.number(),
}, async ({ stock, quantity }) => {
  await placeOrder(stock, quantity, "SELL");
  return { content: [{ type: "text", text: `${stock} has been sold.` }] };
});

// Tool 4: Show portfolio
server.tool("show_portfolio", "Shows complete portfolio in Zerodha", {}, async () => {
  const holdings = await getPositions();
  return { content: [{ type: "text", text: holdings }] };
});
```

**Java equivalent:**
```java
import io.modelcontextprotocol.server.McpServerFeatures.SyncToolSpecification;
import io.modelcontextprotocol.spec.McpSchema.*;
import java.util.List;
import java.util.Map;

// ----- Tool 1: Add two numbers -----
var addTool = new Tool(
    "add_two_numbers",
    "Adds two numbers",
    """
    {
      "type": "object",
      "properties": {
        "a": { "type": "number" },
        "b": { "type": "number" }
      },
      "required": ["a", "b"]
    }
    """
);

server.addTool(new SyncToolSpecification(addTool, (exchange) -> {
    Map<String, Object> args = exchange.arguments();
    double a = ((Number) args.get("a")).doubleValue();
    double b = ((Number) args.get("b")).doubleValue();
    return new CallToolResult(
        List.of(new TextContent(String.valueOf(a + b))),
        false
    );
}));

// ----- Tool 2: Buy a stock -----
var buyTool = new Tool(
    "buy_stock",
    "Buys a stock on the Zerodha exchange. Executes a REAL order.",
    """
    {
      "type": "object",
      "properties": {
        "stock":    { "type": "string" },
        "quantity": { "type": "number" }
      },
      "required": ["stock", "quantity"]
    }
    """
);

server.addTool(new SyncToolSpecification(buyTool, (exchange) -> {
    String stock = (String) exchange.arguments().get("stock");
    int qty = ((Number) exchange.arguments().get("quantity")).intValue();
    tradeService.placeOrder(stock, qty, "BUY");
    return new CallToolResult(
        List.of(new TextContent(stock + " has been bought.")),
        false
    );
}));

// ----- Tool 3: Sell a stock -----
var sellTool = new Tool(
    "sell_stock",
    "Sells a stock on the Zerodha exchange. Executes a REAL order.",
    """
    {
      "type": "object",
      "properties": {
        "stock":    { "type": "string" },
        "quantity": { "type": "number" }
      },
      "required": ["stock", "quantity"]
    }
    """
);

server.addTool(new SyncToolSpecification(sellTool, (exchange) -> {
    String stock = (String) exchange.arguments().get("stock");
    int qty = ((Number) exchange.arguments().get("quantity")).intValue();
    tradeService.placeOrder(stock, qty, "SELL");
    return new CallToolResult(
        List.of(new TextContent(stock + " has been sold.")),
        false
    );
}));

// ----- Tool 4: Show portfolio -----
var portfolioTool = new Tool(
    "show_portfolio",
    "Shows complete portfolio in Zerodha",
    "{ \"type\": \"object\", \"properties\": {} }"
);

server.addTool(new SyncToolSpecification(portfolioTool, (exchange) -> {
    String positions = tradeService.getPositions();
    return new CallToolResult(
        List.of(new TextContent(positions)),
        false
    );
}));
```

> **JS vs Java comparison:**
> - In JS, **Zod** (`z.string()`, `z.number()`) defines the input schema inline.
> - In Java, you provide a **JSON Schema string** describing the same inputs.
> - In JS, the handler is an **async arrow function** `async ({ stock, quantity }) => { ... }`.
> - In Java, the handler is a **lambda** implementing a functional interface `(exchange) -> { ... }`.

> **Key Insight:** The tool **description** matters a lot! It helps the LLM decide *when* to use each tool and understand the real-world consequences. For example, specifying "executes a REAL order" makes Claude more cautious.

### Step 4: Set Up the Transport

**JavaScript:**
```javascript
const transport = new StdioServerTransport();
await server.connect(transport);
```

**Java equivalent:**
```java
// In Java, the transport is passed during McpServer.sync() builder.
// The StdioServerTransportProvider handles stdin/stdout automatically.
// The server.build() call at the end starts listening.
// No separate connect() call needed — it's part of the builder pattern.
```

#### What is a Transport?

A transport defines **how** the MCP client (Claude) communicates with the MCP server.

| Transport | When to Use |
|---|---|
| **stdio** (Standard I/O) | Both client and server are on the **same machine**. Claude spawns the MCP server process directly. |
| **HTTP / WebSocket** | MCP server is hosted **remotely** (e.g., on AWS). Client connects over the network. |

For local development, **stdio** is the standard choice.

---

## 5. Connecting the MCP Server to Claude Desktop

### Step 1: Install Claude Desktop App

MCP currently only works with local desktop apps (not claude.ai web). Supported clients:
- **Claude Desktop**
- **Cursor**
- **Windsurf**

### Step 2: Enable Developer Mode

In the Claude desktop app: **Help → Enable Developer Mode**

### Step 3: Edit the MCP Config

Go to **Settings → Developer → Edit Config**. This opens a JSON file:

**For JavaScript (bun/node):**
```json
{
  "mcpServers": {
    "trade": {
      "command": "/absolute/path/to/bun",
      "args": ["/absolute/path/to/your/project/index.ts"]
    }
  }
}
```

**For Java (run the compiled JAR):**
```json
{
  "mcpServers": {
    "trade": {
      "command": "/absolute/path/to/java",
      "args": ["-jar", "/absolute/path/to/your/project/target/trade-mcp.jar"]
    }
  }
}
```

> **Important:** You must use **absolute paths** for both the runtime (`bun`, `node`) and the script file. Claude cannot resolve relative paths or shell aliases. Run `which bun` or `which node` to find the correct path.

### Step 4: Restart Claude

After saving the config and restarting Claude, you'll see a **tools icon** in the chat showing the available MCP tools.

### How It Works at Runtime

```
Claude Desktop starts
       │
       ▼
Reads MCP config, finds "trade" server
       │
       ▼
Spawns the process: bun /path/to/index.ts
       │
       ▼
MCP server starts, exposes tools via stdio
       │
       ▼
Claude now has access to: buy_stock, sell_stock, show_portfolio, etc.
       │
       ▼
User types: "Buy 2 stocks of HDFC Bank"
       │
       ▼
Claude identifies the right tool → buy_stock(stock="HDFCBANK", quantity=2)
       │
       ▼
MCP server executes → calls Zerodha API → order placed
       │
       ▼
Claude receives response → tells the user the order was placed
```

---

## 6. Key Concepts Summary

### Tools vs Resources

| Concept | Purpose | Analogy |
|---|---|---|
| **Tool** | Executes an action (side-effect). Like a POST request. | "Buy a stock", "Send a message", "Delete a file" |
| **Resource** | Reads data (no side-effect). Like a GET request. | "Show my portfolio", "List my repos" |

> In this demo, even `show_portfolio` was implemented as a tool, but conceptually it's closer to a resource since it only reads data.

### Important Gotchas

1. **Tool names must not contain spaces or special characters** — use underscores (e.g., `buy_stock`, not `buy a stock`).
2. **Don't use `console.log` in your MCP server** — logs go through stdio and interfere with the MCP communication, causing errors in Claude.
3. **Descriptions matter** — the better you describe a tool, the smarter the LLM is about using it.
4. **Input validation** — In JS, use **Zod** (`z.string()`, `z.number()`). In Java, use **JSON Schema strings** to describe expected types.

---

## 7. When is MCP Actually Useful?

### Good Use Cases
- **Complex GUI applications** (Blender, Webflow, Figma) — natural language is simpler than navigating complex UIs
- **DevOps tasks** (Kubernetes, AWS) — non-technical people can manage infrastructure
- **Workflow automation** (Slack, GitHub, Jira) — chain multiple actions via conversation

### Questionable Use Cases
- **Stock trading** — latency matters; LLM interfaces add unnecessary delay
- **Anything requiring real-time precision** — MCP adds overhead

### The Gold Rush Analogy
> During a gold rush, the people who reliably profit are those selling the picks and shovels — not the miners. Similarly, MCP server builders are the new "toolmakers" enabling AI to interact with the real world.

---

## 8. Complete Project Structure

**JavaScript project:**
```
zerodha-trade/
├── index.ts        # MCP server — defines tools, starts stdio transport
├── trade.ts        # Zerodha SDK wrapper — placeOrder(), getPositions()
├── package.json    # Dependencies: kiteconnect, @modelcontextprotocol/sdk
└── bun.lockb
```

**Java project:**
```
zerodha-trade/
├── pom.xml
└── src/main/java/com/trade/
    ├── TradeMcpServer.java    # MCP server — defines tools, starts transport
    └── TradeService.java      # Zerodha SDK wrapper — placeOrder(), getPositions()
```

---

### Minimal JavaScript — `index.ts` (~60 lines)

```javascript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { placeOrder, getPositions } from "./trade";

const server = new McpServer({ name: "trade", version: "1.0.0" });

server.tool("buy_stock", "Buys stock on Zerodha. Executes a REAL order.", {
  stock: z.string(),
  quantity: z.number(),
}, async ({ stock, quantity }) => {
  await placeOrder(stock, quantity, "BUY");
  return { content: [{ type: "text", text: `${stock} bought.` }] };
});

server.tool("sell_stock", "Sells stock on Zerodha. Executes a REAL order.", {
  stock: z.string(),
  quantity: z.number(),
}, async ({ stock, quantity }) => {
  await placeOrder(stock, quantity, "SELL");
  return { content: [{ type: "text", text: `${stock} sold.` }] };
});

server.tool("show_portfolio", "Shows Zerodha portfolio.", {}, async () => {
  const positions = await getPositions();
  return { content: [{ type: "text", text: positions }] };
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Minimal Java — `TradeMcpServer.java`

```java
package com.trade;

import io.modelcontextprotocol.server.McpServer;
import io.modelcontextprotocol.server.McpServerFeatures.SyncToolSpecification;
import io.modelcontextprotocol.server.transport.StdioServerTransportProvider;
import io.modelcontextprotocol.spec.McpSchema.*;
import java.util.List;
import java.util.Map;

public class TradeMcpServer {

    private static final TradeService tradeService = new TradeService();

    public static void main(String[] args) {

        var server = McpServer.sync(
            new StdioServerTransportProvider()
        ).serverInfo(
            new Implementation("trade", "1.0.0")
        ).build();

        // --- Buy Stock Tool ---
        var buyTool = new Tool("buy_stock",
            "Buys stock on Zerodha. Executes a REAL order.",
            """
            { "type": "object",
              "properties": {
                "stock": { "type": "string" },
                "quantity": { "type": "number" }
              }, "required": ["stock", "quantity"] }
            """);
        server.addTool(new SyncToolSpecification(buyTool, (ex) -> {
            String stock = (String) ex.arguments().get("stock");
            int qty = ((Number) ex.arguments().get("quantity")).intValue();
            tradeService.placeOrder(stock, qty, "BUY");
            return new CallToolResult(List.of(new TextContent(stock + " bought.")), false);
        }));

        // --- Sell Stock Tool ---
        var sellTool = new Tool("sell_stock",
            "Sells stock on Zerodha. Executes a REAL order.",
            """
            { "type": "object",
              "properties": {
                "stock": { "type": "string" },
                "quantity": { "type": "number" }
              }, "required": ["stock", "quantity"] }
            """);
        server.addTool(new SyncToolSpecification(sellTool, (ex) -> {
            String stock = (String) ex.arguments().get("stock");
            int qty = ((Number) ex.arguments().get("quantity")).intValue();
            tradeService.placeOrder(stock, qty, "SELL");
            return new CallToolResult(List.of(new TextContent(stock + " sold.")), false);
        }));

        // --- Show Portfolio Tool ---
        var portfolioTool = new Tool("show_portfolio",
            "Shows Zerodha portfolio.",
            "{ \"type\": \"object\", \"properties\": {} }");
        server.addTool(new SyncToolSpecification(portfolioTool, (ex) -> {
            String positions = tradeService.getPositions();
            return new CallToolResult(List.of(new TextContent(positions)), false);
        }));

        System.err.println("Trade MCP Server running on stdio...");
        // Server is now listening on stdin/stdout
    }
}
```

---

## 9. What's Next?

- Explore existing MCP servers on [GitHub](https://github.com/modelcontextprotocol/servers)
- Read the official MCP specification docs
- Try building an MCP server for a service you use daily
- Experiment with **HTTP transports** for remote MCP servers
- Look into MCP **resources** and **prompts** for richer integrations
