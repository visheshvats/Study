"""
MODULE 5 — Example 1: MCP Concepts Explained with Code
========================================================
Understanding MCP protocol by implementing the concepts
WITHOUT needing the actual MCP SDK. This is pure learning.

NO DEPENDENCIES — runs with standard Python only.

RUN:
  python 01_mcp_concepts.py

KEY INSIGHT:
  MCP is just JSON-RPC messages. Understanding the protocol
  helps you build better MCP servers and debug issues.
"""

import json
from dataclasses import dataclass, asdict
from typing import Any


# ══════════════════════════════════════════════════════
# PART 1: MCP Messages are JSON-RPC 2.0
# ══════════════════════════════════════════════════════

def demo_jsonrpc():
    """
    MCP uses JSON-RPC 2.0 — a simple request/response protocol.
    
    Every message is a JSON object with:
    - "jsonrpc": "2.0" (always)
    - "method": "tools/list" (what to do)
    - "params": {...} (data)
    - "id": 1 (request tracking)
    
    Java Analogy: Like HTTP request/response, but for AI tools.
    """
    print("=" * 60)
    print("PART 1: MCP Messages (JSON-RPC 2.0)")
    print("=" * 60)

    # Request: Client asks server to list tools
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    print(f"\n  📤 Client → Server (Request):")
    print(f"  {json.dumps(request, indent=4)}")

    # Response: Server returns available tools
    response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "tools": [
                {
                    "name": "search_logs",
                    "description": "Search application logs by query string, time range, and severity level.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Log search query"},
                            "severity": {"type": "string", "enum": ["DEBUG", "INFO", "WARN", "ERROR"]},
                            "minutes_ago": {"type": "integer", "description": "How many minutes back to search"},
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "restart_service",
                    "description": "Restart a running service by name. Requires confirmation for production.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "service_name": {"type": "string"},
                            "environment": {"type": "string", "enum": ["dev", "staging", "production"]},
                        },
                        "required": ["service_name", "environment"]
                    }
                }
            ]
        }
    }
    print(f"\n  📥 Server → Client (Response):")
    print(f"  {json.dumps(response, indent=4)}")


# ══════════════════════════════════════════════════════
# PART 2: The 3 MCP Primitives
# ══════════════════════════════════════════════════════

def demo_primitives():
    """Shows the 3 types of things an MCP server can expose."""
    print("\n" + "=" * 60)
    print("PART 2: MCP Primitives (Tools, Resources, Prompts)")
    print("=" * 60)

    # ── TOOLS (Model-controlled) ──
    print("\n  🔧 TOOLS — Actions the LLM can call")
    tool_call = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "search_logs",
            "arguments": {
                "query": "NullPointerException",
                "severity": "ERROR",
                "minutes_ago": 30
            }
        }
    }
    print(f"  Request: tools/call → search_logs")
    print(f"  Arguments: {json.dumps(tool_call['params']['arguments'])}")

    tool_result = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "content": [{
                "type": "text",
                "text": "Found 3 ERROR logs:\n1. UserService.java:42 NullPointerException\n2. OrderService.java:88 NullPointerException\n3. PaymentService.java:156 NullPointerException"
            }]
        }
    }
    print(f"  Result: {tool_result['result']['content'][0]['text'][:80]}...")

    # ── RESOURCES (Application-controlled) ──
    print("\n  📄 RESOURCES — Read-only data")
    resource_list = {
        "method": "resources/list",
        "result": {
            "resources": [
                {
                    "uri": "config://application.yml",
                    "name": "Application Configuration",
                    "mimeType": "application/yaml",
                    "description": "Current Spring Boot application settings"
                },
                {
                    "uri": "metrics://service/user-service",
                    "name": "User Service Metrics",
                    "mimeType": "application/json",
                    "description": "CPU, memory, request count for User Service"
                },
            ]
        }
    }
    print(f"  Available resources:")
    for r in resource_list["result"]["resources"]:
        print(f"    📊 {r['uri']} — {r['description']}")

    # ── PROMPTS (User-controlled) ──
    print("\n  💬 PROMPTS — Pre-built templates")
    prompt_list = {
        "method": "prompts/list",
        "result": {
            "prompts": [
                {
                    "name": "debug_error",
                    "description": "Analyze an error and suggest fixes",
                    "arguments": [
                        {"name": "error_message", "required": True},
                        {"name": "stack_trace", "required": False},
                    ]
                },
                {
                    "name": "code_review",
                    "description": "Review code for bugs, security, and style",
                    "arguments": [
                        {"name": "code", "required": True},
                        {"name": "language", "required": False},
                    ]
                },
            ]
        }
    }
    print(f"  Available prompts:")
    for p in prompt_list["result"]["prompts"]:
        args = ", ".join(a["name"] for a in p["arguments"])
        print(f"    📝 {p['name']}({args}) — {p['description']}")


# ══════════════════════════════════════════════════════
# PART 3: MCP Connection Lifecycle
# ══════════════════════════════════════════════════════

def demo_lifecycle():
    """Shows how a client connects to a server."""
    print("\n" + "=" * 60)
    print("PART 3: MCP Connection Lifecycle")
    print("=" * 60)

    stages = [
        {
            "stage": "1. INITIALIZE",
            "direction": "Client → Server",
            "message": {
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "clientInfo": {"name": "MyAIApp", "version": "1.0"}
                }
            }
        },
        {
            "stage": "   Server responds",
            "direction": "Server → Client",
            "message": {
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": True}, "resources": {}},
                    "serverInfo": {"name": "DevOpsServer", "version": "1.0"}
                }
            }
        },
        {
            "stage": "2. INITIALIZED",
            "direction": "Client → Server",
            "message": {"method": "notifications/initialized"}
        },
        {
            "stage": "3. DISCOVER",
            "direction": "Client → Server",
            "message": {"method": "tools/list"}
        },
        {
            "stage": "4. OPERATE",
            "direction": "Client → Server",
            "message": {"method": "tools/call", "params": {"name": "search_logs", "arguments": {"query": "error"}}}
        },
        {
            "stage": "5. SHUTDOWN",
            "direction": "Client → Server",
            "message": {"method": "close"}
        },
    ]

    for s in stages:
        print(f"\n  {s['stage']}")
        print(f"    {s['direction']}: {json.dumps(s['message'])[:80]}")


# ══════════════════════════════════════════════════════
# PART 4: MCP vs OpenAI Function Calling
# ══════════════════════════════════════════════════════

def demo_comparison():
    """Compares MCP with OpenAI function calling."""
    print("\n" + "=" * 60)
    print("PART 4: MCP vs OpenAI Function Calling")
    print("=" * 60)

    print("""
  ┌─────────────────┬───────────────────┬───────────────────┐
  │ Feature         │ Function Calling  │ MCP               │
  ├─────────────────┼───────────────────┼───────────────────┤
  │ Standard        │ OpenAI-specific   │ Open standard     │
  │ Works with      │ OpenAI only       │ Any AI provider   │
  │ Tool discovery  │ Hardcoded         │ Dynamic           │
  │ Data access     │ Tools only        │ Tools + Resources │
  │ Transport       │ HTTP only         │ stdio, SSE, HTTP  │
  │ Ecosystem       │ Per-app           │ Shared servers    │
  │ Prompts         │ ❌                │ ✅ Built-in       │
  │ Complexity      │ Simple            │ More structured   │
  └─────────────────┴───────────────────┴───────────────────┘

  When to use which:
  • Function calling: Quick prototype, single app, OpenAI only
  • MCP: Reusable integrations, multi-provider, production systems
  """)


# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 MODULE 5: MCP Concepts Explained\n")

    demo_jsonrpc()
    demo_primitives()
    demo_lifecycle()
    demo_comparison()

    print("✅ Key takeaways:")
    print("   1. MCP = JSON-RPC 2.0 messages between client and server")
    print("   2. Three primitives: Tools (actions), Resources (data), Prompts (templates)")
    print("   3. Lifecycle: Initialize → Discover → Operate → Shutdown")
    print("   4. MCP is the universal standard; function calling is provider-specific\n")
