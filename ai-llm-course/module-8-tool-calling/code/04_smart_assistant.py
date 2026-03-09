"""
MODULE 8 — PROJECT: Smart Assistant with Universal Tool Framework
==================================================================
A production-grade agent with:
  - Auto-registered tools via @tool decorator
  - Parallel tool execution
  - Error handling with retries
  - Dynamic tool filtering by context
  - Full execution logging & audit trail

SETUP:
  pip install openai python-dotenv

RUN:
  python 04_smart_assistant.py
"""

import os
import json
import time
import inspect
import functools
from typing import get_type_hints
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# ══════════════════════════════════════════════════════
# TOOL FRAMEWORK (production-grade)
# ══════════════════════════════════════════════════════

TYPE_MAP = {str: "string", int: "integer", float: "number", bool: "boolean", list: "array", dict: "object"}


class ToolFramework:
    """
    Production tool framework with auto-registration, validation,
    parallel execution, error handling, and audit logging.
    """

    def __init__(self):
        self._tools = {}
        self._audit_log = []

    def register(self, fn, description: str = "", category: str = "general",
                 require_confirm: bool = False, max_retries: int = 0):
        """Register a tool function."""
        name = fn.__name__
        hints = get_type_hints(fn)
        sig = inspect.signature(fn)

        properties, required = {}, []
        for pname, param in sig.parameters.items():
            ptype = hints.get(pname, str)
            properties[pname] = {"type": TYPE_MAP.get(ptype, "string")}
            if param.default == inspect.Parameter.empty:
                required.append(pname)

        self._tools[name] = {
            "fn": fn,
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description or (fn.__doc__ or name).split("\n")[0].strip(),
                    "parameters": {"type": "object", "properties": properties, "required": required},
                },
            },
            "category": category,
            "require_confirm": require_confirm,
            "max_retries": max_retries,
            "stats": {"calls": 0, "errors": 0, "total_ms": 0},
        }

    def tool(self, description: str = "", category: str = "general",
             require_confirm: bool = False, max_retries: int = 0):
        """Decorator to register tools."""
        def decorator(fn):
            self.register(fn, description, category, require_confirm, max_retries)
            return fn
        return decorator

    def get_schemas(self, categories: list = None) -> list:
        """Get schemas, optionally filtered by category."""
        return [
            t["schema"] for t in self._tools.values()
            if not categories or t["category"] in categories
        ]

    def execute(self, name: str, arguments: dict) -> str:
        """Execute a tool with validation, retries, and logging."""
        if name not in self._tools:
            return json.dumps({"error": f"Unknown tool: {name}"})

        tool = self._tools[name]

        if tool["require_confirm"]:
            self._log(name, arguments, "blocked", "Confirmation required")
            return json.dumps({"status": "confirmation_required", "tool": name})

        last_error = None
        max_attempts = tool["max_retries"] + 1

        for attempt in range(1, max_attempts + 1):
            start = time.time()
            try:
                result = tool["fn"](**arguments)
                elapsed = round((time.time() - start) * 1000)
                tool["stats"]["calls"] += 1
                tool["stats"]["total_ms"] += elapsed
                result_str = result if isinstance(result, str) else json.dumps(result)
                self._log(name, arguments, "success", f"{elapsed}ms")
                return result_str
            except Exception as e:
                last_error = e
                tool["stats"]["errors"] += 1
                if attempt < max_attempts:
                    delay = 0.5 * (2 ** (attempt - 1))
                    time.sleep(delay)

        self._log(name, arguments, "error", str(last_error))
        return json.dumps({"error": str(last_error), "tool": name, "suggestion": "Tool failed. Try rephrasing."})

    def execute_parallel(self, tool_calls) -> list:
        """Execute multiple tool calls in parallel."""
        if len(tool_calls) == 1:
            result = self.execute(tool_calls[0]["name"], tool_calls[0]["args"])
            return [{"tool_call_id": tool_calls[0]["id"], "role": "tool", "content": result}]

        results = [None] * len(tool_calls)

        def run(i, tc):
            return i, self.execute(tc["name"], tc["args"])

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(run, i, tc) for i, tc in enumerate(tool_calls)]
            for f in futures:
                idx, result = f.result()
                results[idx] = {"tool_call_id": tool_calls[idx]["id"], "role": "tool", "content": result}
        return results

    def _log(self, tool: str, args: dict, status: str, detail: str):
        self._audit_log.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "tool": tool,
            "args_summary": str(args)[:60],
            "status": status,
            "detail": detail,
        })

    def get_audit_log(self) -> list:
        return self._audit_log

    def get_stats(self) -> dict:
        return {
            name: {
                "calls": t["stats"]["calls"],
                "errors": t["stats"]["errors"],
                "avg_ms": round(t["stats"]["total_ms"] / max(t["stats"]["calls"], 1)),
            }
            for name, t in self._tools.items()
        }


# ══════════════════════════════════════════════════════
# INITIALIZE FRAMEWORK & REGISTER TOOLS
# ══════════════════════════════════════════════════════

fw = ToolFramework()


@fw.tool(description="Search the web for information on any topic.", category="search")
def search_web(query: str) -> str:
    """Search the web for information."""
    results = {
        "python": "Python 3.12: improved error messages, performance gains, new typing features.",
        "java": "Java 21 LTS: virtual threads, pattern matching, sequenced collections.",
        "spring boot": "Spring Boot 3.3: virtual threads support, Docker Compose, GraalVM native.",
        "kubernetes": "K8s 1.30: sidecar containers GA, memory limits improvements.",
        "docker": "Docker 26: multi-platform builds, improved build caching.",
    }
    for key, val in results.items():
        if key in query.lower():
            return json.dumps({"query": query, "results": [val], "source": "web"})
    return json.dumps({"query": query, "results": [f"Latest info about: {query}"], "source": "web"})


@fw.tool(description="Evaluate a mathematical expression. Supports basic arithmetic and functions.", category="math")
def calculate(expression: str) -> str:
    """Evaluate math expressions safely."""
    import math
    safe_env = {"__builtins__": {}, "math": math, "abs": abs, "round": round, "min": min, "max": max, "pow": pow}
    result = eval(expression, safe_env)
    return json.dumps({"expression": expression, "result": result})


@fw.tool(description="Get current weather for a city. Returns temperature in Celsius.", category="data")
def get_weather(city: str) -> str:
    """Get weather data for a city."""
    data = {"tokyo": (22, "Sunny"), "london": (14, "Cloudy"), "paris": (18, "Clear"), "new york": (25, "Humid")}
    temp, cond = data.get(city.lower(), (20, "Unknown"))
    return json.dumps({"city": city, "temp_celsius": temp, "condition": cond})


@fw.tool(description="Convert temperature between Celsius and Fahrenheit.", category="math")
def convert_temp(value: float, from_unit: str) -> str:
    """Convert temperature units."""
    if from_unit.lower().startswith("c"):
        result = value * 9 / 5 + 32
        return json.dumps({"input": f"{value}°C", "output": f"{result:.1f}°F"})
    else:
        result = (value - 32) * 5 / 9
        return json.dumps({"input": f"{value}°F", "output": f"{result:.1f}°C"})


@fw.tool(description="Get exchange rate between two currencies.", category="data", max_retries=2)
def get_exchange_rate(from_currency: str, to_currency: str) -> str:
    """Get currency exchange rate."""
    rates = {
        ("USD", "EUR"): 0.92, ("USD", "GBP"): 0.79, ("USD", "JPY"): 149.5,
        ("EUR", "USD"): 1.09, ("GBP", "USD"): 1.27, ("JPY", "USD"): 0.0067,
    }
    key = (from_currency.upper(), to_currency.upper())
    rate = rates.get(key, 1.0)
    return json.dumps({"from": from_currency, "to": to_currency, "rate": rate})


@fw.tool(description="Create a note or reminder. Saves to memory.", category="productivity")
def create_note(title: str, content: str) -> str:
    """Save a note."""
    return json.dumps({"id": f"note-{int(time.time())}", "title": title, "status": "saved"})


@fw.tool(description="List all saved notes.", category="productivity")
def list_notes() -> str:
    """List notes."""
    return json.dumps({"notes": [
        {"id": "note-1", "title": "Meeting notes", "date": "2025-03-08"},
        {"id": "note-2", "title": "Project ideas", "date": "2025-03-07"},
    ]})


@fw.tool(description="Delete a note permanently. DESTRUCTIVE.", category="admin", require_confirm=True)
def delete_note(note_id: str) -> str:
    """Delete a note."""
    return json.dumps({"deleted": note_id})


# ══════════════════════════════════════════════════════
# SMART ASSISTANT (THE AGENT)
# ══════════════════════════════════════════════════════

class SmartAssistant:
    """
    Production agent combining:
    - Tool framework with auto-registration
    - Parallel execution
    - Error handling
    - Dynamic tool filtering
    - Audit logging
    """

    SYSTEM_PROMPT = (
        "You are a smart personal assistant with access to tools for search, math, "
        "weather, currency, and notes. Use tools when you need real data. "
        "For multi-part questions, use multiple tools in parallel when possible. "
        "Be concise and helpful."
    )

    def __init__(self, framework: ToolFramework, categories: list = None):
        self.fw = framework
        self.categories = categories
        self.messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

    def chat(self, user_message: str) -> str:
        """Process a user message with tool support."""
        self.messages.append({"role": "user", "content": user_message})
        schemas = self.fw.get_schemas(categories=self.categories)

        for iteration in range(6):
            response = client.chat.completions.create(
                model=MODEL, messages=self.messages, tools=schemas, tool_choice="auto",
            )
            msg = response.choices[0].message

            if not msg.tool_calls:
                self.messages.append(msg)
                return msg.content

            self.messages.append(msg)

            # Prepare tool calls
            calls = [
                {"id": tc.id, "name": tc.function.name, "args": json.loads(tc.function.arguments)}
                for tc in msg.tool_calls
            ]
            names = [c["name"] for c in calls]
            print(f"    🔧 Tools: {names}")

            # Execute (parallel if multiple)
            results = self.fw.execute_parallel(calls)

            for r in results:
                content = json.loads(r["content"]) if isinstance(r["content"], str) and r["content"].startswith("{") else r["content"]
                print(f"    📋 → {str(content)[:70]}...")
                self.messages.append(r)

        return "I've reached the maximum number of tool calls. Please simplify your request."


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🧠 Smart Assistant — Universal Tool Framework║")
    print("║  MODULE 8 PROJECT                            ║")
    print("╚══════════════════════════════════════════════╝")

    # Show registered tools
    print(f"\n  📋 Registered Tools:")
    for schema in fw.get_schemas():
        fn = schema["function"]
        print(f"    🔧 {fn['name']}: {fn['description'][:50]}")

    assistant = SmartAssistant(fw)

    queries = [
        "What's the weather in Tokyo and London?",
        "Search for Java 21 features and calculate 2^16",
        "Get weather in Paris in Celsius and convert it to Fahrenheit",
        "What's the exchange rate from USD to EUR and USD to JPY?",
        "Delete note-123",  # Will be blocked (require_confirm)
    ]

    for query in queries:
        print(f"\n  {'═'*55}")
        print(f"  👤 {query}")
        print(f"  {'─'*55}")
        reply = assistant.chat(query)
        print(f"\n  🤖 {reply[:200]}")

    # Show stats
    print(f"\n\n  {'═'*55}")
    print(f"  📊 TOOL EXECUTION STATS:")
    print(f"  {'─'*55}")
    for name, stats in fw.get_stats().items():
        if stats["calls"] > 0 or stats["errors"] > 0:
            print(f"    {name}: {stats['calls']} calls, {stats['errors']} errors, avg {stats['avg_ms']}ms")

    print(f"\n  📜 AUDIT LOG:")
    print(f"  {'─'*55}")
    for entry in fw.get_audit_log():
        icon = "✅" if entry["status"] == "success" else ("🛑" if entry["status"] == "blocked" else "❌")
        print(f"    [{entry['timestamp']}] {icon} {entry['tool']} — {entry['detail']}")

    print(f"\n  ✅ Smart Assistant features:")
    print(f"     • @tool decorator auto-generates schemas")
    print(f"     • Parallel execution via ThreadPoolExecutor")
    print(f"     • Retry with backoff for flaky tools")
    print(f"     • Confirmation gate for destructive actions")
    print(f"     • Category-based tool filtering")
    print(f"     • Full audit log for compliance\n")


if __name__ == "__main__":
    main()
