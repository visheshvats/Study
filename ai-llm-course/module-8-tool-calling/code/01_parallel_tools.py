"""
MODULE 8 — Example 1: Parallel & Chained Tool Calls
=====================================================
Advanced patterns: running tools in parallel and chaining
output from one tool into another.

SETUP:
  pip install openai python-dotenv

RUN:
  python 01_parallel_tools.py
"""

import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# ══════════════════════════════════════════════════════
# SIMULATED TOOLS (with artificial latency)
# ══════════════════════════════════════════════════════

def search_web(query: str) -> str:
    """Simulated web search with 0.5s latency."""
    time.sleep(0.5)  # Simulate network call
    results = {
        "python": "Python 3.12 is the latest stable version. Key features: improved error messages, performance gains.",
        "java": "Java 21 LTS features: virtual threads, pattern matching, sequenced collections.",
        "spring": "Spring Boot 3.3 latest. Key: virtual threads, Docker Compose support, GraalVM native.",
    }
    for key, val in results.items():
        if key in query.lower():
            return json.dumps({"query": query, "result": val})
    return json.dumps({"query": query, "result": f"General info about: {query}"})


def get_weather(city: str) -> str:
    """Simulated weather with 0.3s latency."""
    time.sleep(0.3)
    data = {"tokyo": 22, "london": 14, "paris": 18, "new york": 25}
    temp = data.get(city.lower(), 20)
    return json.dumps({"city": city, "temp_celsius": temp, "condition": "Partly cloudy"})


def calculate(expression: str) -> str:
    """Calculator with 0.1s latency."""
    time.sleep(0.1)
    try:
        result = eval(expression, {"__builtins__": {}})
        return json.dumps({"expression": expression, "result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_exchange_rate(from_currency: str, to_currency: str) -> str:
    """Simulated exchange rate with 0.4s latency."""
    time.sleep(0.4)
    rates = {
        ("USD", "EUR"): 0.92, ("USD", "GBP"): 0.79, ("USD", "JPY"): 149.5,
        ("EUR", "USD"): 1.09, ("GBP", "USD"): 1.27, ("JPY", "USD"): 0.0067,
    }
    rate = rates.get((from_currency.upper(), to_currency.upper()), 1.0)
    return json.dumps({"from": from_currency, "to": to_currency, "rate": rate})


TOOL_REGISTRY = {
    "search_web": search_web,
    "get_weather": get_weather,
    "calculate": calculate,
    "get_exchange_rate": get_exchange_rate,
}

TOOL_DEFS = [
    {"type": "function", "function": {"name": "search_web", "description": "Search the web for information.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "get_weather", "description": "Get weather for a city. Returns temperature in Celsius.", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "calculate", "description": "Evaluate a math expression.", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}},
    {"type": "function", "function": {"name": "get_exchange_rate", "description": "Get exchange rate between two currencies.", "parameters": {"type": "object", "properties": {"from_currency": {"type": "string"}, "to_currency": {"type": "string"}}, "required": ["from_currency", "to_currency"]}}},
]


# ══════════════════════════════════════════════════════
# PARALLEL EXECUTOR
# ══════════════════════════════════════════════════════

def execute_tools_sequential(tool_calls) -> list[dict]:
    """Execute tool calls one by one (baseline)."""
    results = []
    for tc in tool_calls:
        fn = TOOL_REGISTRY[tc.function.name]
        args = json.loads(tc.function.arguments)
        result = fn(**args)
        results.append({"tool_call_id": tc.id, "role": "tool", "content": result})
    return results


def execute_tools_parallel(tool_calls) -> list[dict]:
    """Execute tool calls in parallel using ThreadPoolExecutor."""
    results = [None] * len(tool_calls)

    def run(index, tc):
        fn = TOOL_REGISTRY[tc.function.name]
        args = json.loads(tc.function.arguments)
        return index, fn(**args)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run, i, tc) for i, tc in enumerate(tool_calls)]
        for future in as_completed(futures):
            idx, result = future.result()
            results[idx] = {
                "tool_call_id": tool_calls[idx].id,
                "role": "tool",
                "content": result,
            }

    return results


# ══════════════════════════════════════════════════════
# AGENT WITH PARALLEL TOOLS
# ══════════════════════════════════════════════════════

def agent_run(query: str, parallel: bool = True) -> str:
    """Run agent loop with parallel or sequential tool execution."""
    messages = [
        {"role": "system", "content": "You are helpful. Use tools when needed. You can call multiple tools at once."},
        {"role": "user", "content": query},
    ]

    total_tool_time = 0

    for _ in range(5):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_DEFS, tool_choice="auto",
        )
        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)

            tool_names = [tc.function.name for tc in message.tool_calls]
            print(f"    🔧 Calling {len(message.tool_calls)} tools: {tool_names}")

            start = time.time()
            if parallel and len(message.tool_calls) > 1:
                results = execute_tools_parallel(message.tool_calls)
                mode = "parallel"
            else:
                results = execute_tools_sequential(message.tool_calls)
                mode = "sequential"
            elapsed = time.time() - start
            total_tool_time += elapsed

            print(f"    ⏱️  Execution ({mode}): {elapsed:.2f}s")

            for r in results:
                messages.append(r)
        else:
            print(f"    📊 Total tool time: {total_tool_time:.2f}s")
            return message.content

    return "Max iterations."


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  ⚡ Parallel & Chained Tool Calls            ║")
    print("╚══════════════════════════════════════════════╝")

    # Test 1: Parallel execution
    print(f"\n  {'═'*55}")
    print("  TEST 1: Parallel calls (multiple cities)")
    print(f"  {'─'*55}")
    query1 = "What's the weather in Tokyo, London, and Paris?"

    print(f"\n  Sequential execution:")
    result1s = agent_run(query1, parallel=False)

    print(f"\n  Parallel execution:")
    result1p = agent_run(query1, parallel=True)

    # Test 2: Chained calls (output feeds input)
    print(f"\n  {'═'*55}")
    print("  TEST 2: Chained calls (weather → convert → exchange)")
    print(f"  {'─'*55}")
    query2 = (
        "Get the weather in Tokyo in Celsius, convert it to Fahrenheit, "
        "and also get the USD to JPY exchange rate."
    )
    result2 = agent_run(query2, parallel=True)
    print(f"\n  🤖 {result2[:200]}...")

    # Test 3: Mix of parallel + chained
    print(f"\n  {'═'*55}")
    print("  TEST 3: Complex query (search + weather + calculate)")
    print(f"  {'─'*55}")
    query3 = "Search for Java 21 features, get weather in New York, and calculate 2**16."
    result3 = agent_run(query3, parallel=True)
    print(f"\n  🤖 {result3[:200]}...")

    print(f"\n  {'═'*55}")
    print("  ✅ Key insights:")
    print("     • Parallel calls reduce latency when tools are independent")
    print("     • Chained calls happen naturally across agent loop iterations")
    print("     • ThreadPoolExecutor handles I/O-bound parallel execution")
    print("     • Each result needs correct tool_call_id mapping\n")


if __name__ == "__main__":
    main()
