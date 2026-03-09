"""
MODULE 8 — Example 2: Build a Tool Framework from Scratch
============================================================
A @tool decorator that auto-generates JSON schemas from
Python type hints — eliminating boilerplate.

SETUP:
  pip install openai python-dotenv

RUN:
  python 02_tool_framework.py

KEY CONCEPT:
  Write a function with type hints and docstring.
  The framework handles everything else:
    - JSON schema generation
    - Tool registration
    - Argument validation
    - Error handling
    - Execution logging
"""

import os
import json
import inspect
import time
import functools
from typing import get_type_hints
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# ══════════════════════════════════════════════════════
# THE TOOL FRAMEWORK
# ══════════════════════════════════════════════════════

# Python type → JSON Schema type mapping
TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


class ToolRegistry:
    """
    Registry that stores tool definitions and implementations.
    
    Java Analogy: Like Spring's ApplicationContext —
    auto-registers beans (tools) and provides them to consumers.
    """

    def __init__(self):
        self._tools: dict[str, dict] = {}  # name → {fn, schema, metadata}

    def register(self, fn, description: str = "", require_confirm: bool = False, tags: list = None):
        """Register a function as a tool."""
        name = fn.__name__
        hints = get_type_hints(fn)
        sig = inspect.signature(fn)

        # Parse docstring for parameter descriptions
        param_docs = self._parse_param_docs(fn.__doc__ or "")

        # Build JSON Schema from type hints
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name == "return":
                continue

            param_type = hints.get(param_name, str)
            json_type = TYPE_MAP.get(param_type, "string")

            prop = {"type": json_type}
            if param_name in param_docs:
                prop["description"] = param_docs[param_name]

            properties[param_name] = prop

            # If no default value, parameter is required
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description or (fn.__doc__ or "").split("\n")[0].strip(),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

        self._tools[name] = {
            "fn": fn,
            "schema": schema,
            "require_confirm": require_confirm,
            "tags": tags or [],
            "call_count": 0,
            "total_time": 0,
        }

    def _parse_param_docs(self, docstring: str) -> dict:
        """Extract parameter descriptions from docstring."""
        params = {}
        in_args = False
        for line in docstring.split("\n"):
            stripped = line.strip()
            if stripped.lower().startswith("args:"):
                in_args = True
                continue
            if in_args:
                if stripped.startswith("returns:") or stripped.startswith("return"):
                    break
                if ":" in stripped:
                    parts = stripped.split(":", 1)
                    param_name = parts[0].strip().strip("-").strip()
                    param_desc = parts[1].strip()
                    if param_name:
                        params[param_name] = param_desc
        return params

    def get_schemas(self, tags: list = None) -> list:
        """Get all tool schemas, optionally filtered by tags."""
        schemas = []
        for tool in self._tools.values():
            if tags:
                if any(t in tool["tags"] for t in tags):
                    schemas.append(tool["schema"])
            else:
                schemas.append(tool["schema"])
        return schemas

    def execute(self, name: str, arguments: dict) -> str:
        """Execute a tool by name with arguments."""
        if name not in self._tools:
            return json.dumps({"error": f"Unknown tool: {name}"})

        tool = self._tools[name]

        # Check confirmation
        if tool["require_confirm"]:
            return json.dumps({
                "status": "confirmation_required",
                "tool": name,
                "args": arguments,
                "message": f"Tool '{name}' requires confirmation before execution.",
            })

        # Execute with timing and error handling
        start = time.time()
        try:
            result = tool["fn"](**arguments)
            elapsed = time.time() - start
            tool["call_count"] += 1
            tool["total_time"] += elapsed
            return result if isinstance(result, str) else json.dumps(result)
        except TypeError as e:
            return json.dumps({"error": f"Invalid arguments for '{name}': {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Execution failed for '{name}': {str(e)}"})

    def get_stats(self) -> dict:
        return {
            name: {"calls": t["call_count"], "avg_ms": round(t["total_time"] / max(t["call_count"], 1) * 1000, 1)}
            for name, t in self._tools.items()
        }


# Global registry
registry = ToolRegistry()


def tool(description: str = "", require_confirm: bool = False, tags: list = None):
    """
    Decorator that registers a function as a tool.
    
    Usage:
        @tool(description="Search the web", tags=["search"])
        def search(query: str) -> str:
            ...
    """
    def decorator(fn):
        registry.register(fn, description, require_confirm, tags or [])

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper
    return decorator


# ══════════════════════════════════════════════════════
# DEFINE TOOLS USING THE FRAMEWORK
# ══════════════════════════════════════════════════════

@tool(description="Search the web for information. Returns relevant results.", tags=["search"])
def search_web(query: str) -> str:
    """Search the web.
    
    Args:
        query: The search query string
    """
    results = {"python": "Python 3.12", "java": "Java 21 LTS", "spring": "Spring Boot 3.3"}
    for k, v in results.items():
        if k in query.lower():
            return json.dumps({"query": query, "result": v})
    return json.dumps({"query": query, "result": f"Results for: {query}"})


@tool(description="Evaluate a mathematical expression safely.", tags=["math"])
def calculate(expression: str) -> str:
    """Calculate math.
    
    Args:
        expression: Math expression (e.g., '2 + 3 * 4')
    """
    import math as m
    safe = {"__builtins__": {}, "math": m, "abs": abs, "round": round}
    result = eval(expression, safe)
    return json.dumps({"expression": expression, "result": result})


@tool(description="Get the current weather for a city.", tags=["data"])
def get_weather(city: str) -> str:
    """Get weather data.
    
    Args:
        city: City name (e.g., 'Tokyo', 'London')
    """
    temps = {"tokyo": 22, "london": 14, "paris": 18}
    return json.dumps({"city": city, "temp_c": temps.get(city.lower(), 20)})


@tool(description="Delete a file or record. DESTRUCTIVE!", require_confirm=True, tags=["admin"])
def delete_record(record_id: str) -> str:
    """Delete a record.
    
    Args:
        record_id: ID of the record to delete
    """
    return json.dumps({"deleted": record_id, "status": "success"})


# ══════════════════════════════════════════════════════
# AGENT USING THE FRAMEWORK
# ══════════════════════════════════════════════════════

def run_agent(query: str, tool_tags: list = None):
    """Run agent with framework-managed tools."""
    schemas = registry.get_schemas(tags=tool_tags)

    print(f"\n  👤 Query: {query}")
    print(f"  🔧 Available tools: {[s['function']['name'] for s in schemas]}")

    messages = [
        {"role": "system", "content": "You are helpful. Use tools when needed."},
        {"role": "user", "content": query},
    ]

    for _ in range(5):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=schemas, tool_choice="auto",
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                print(f"  🔧 {name}({args})")

                result = registry.execute(name, args)
                print(f"  📋 → {result[:80]}")

                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        else:
            print(f"  🤖 {msg.content[:150]}")
            return msg.content

    return "Max iterations."


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🏗️  Tool Framework — @tool Decorator         ║")
    print("║  Auto-generates schemas from type hints       ║")
    print("╚══════════════════════════════════════════════╝")

    # Show auto-generated schemas
    print(f"\n  {'═'*55}")
    print("  AUTO-GENERATED SCHEMAS:")
    print(f"  {'─'*55}")
    for schema in registry.get_schemas():
        fn = schema["function"]
        params = list(fn["parameters"]["properties"].keys())
        print(f"  🔧 {fn['name']}({', '.join(params)})")
        print(f"     Description: {fn['description'][:60]}")

    # Test 1: Normal usage
    print(f"\n  {'═'*55}")
    print("  TEST 1: Regular tool usage")
    print(f"  {'─'*55}")
    run_agent("What's the weather in Tokyo?")

    # Test 2: Tag-based filtering
    print(f"\n  {'═'*55}")
    print("  TEST 2: Only math tools (tag filter)")
    print(f"  {'─'*55}")
    run_agent("Calculate 25 * 4 + 17", tool_tags=["math"])

    # Test 3: Destructive tool (confirmation required)
    print(f"\n  {'═'*55}")
    print("  TEST 3: Destructive tool (blocked by framework)")
    print(f"  {'─'*55}")
    result = registry.execute("delete_record", {"record_id": "user-123"})
    print(f"  🛑 {result}")

    # Stats
    print(f"\n  {'═'*55}")
    print(f"  📊 Tool execution stats:")
    for name, stats in registry.get_stats().items():
        print(f"     {name}: {stats['calls']} calls, avg {stats['avg_ms']}ms")

    print(f"\n  ✅ Framework benefits:")
    print(f"     • @tool decorator auto-generates JSON schemas")
    print(f"     • Tag-based tool filtering (role/context)")
    print(f"     • require_confirm blocks destructive tools")
    print(f"     • Built-in error handling and timing\n")


if __name__ == "__main__":
    main()
