"""
MODULE 4 — Example 1: OpenAI Function Calling
================================================
The mechanism that powers AI agents. The LLM doesn't call functions —
it TELLS you what to call, and YOU execute it.

SETUP:
  pip install openai python-dotenv

RUN:
  python 01_function_calling.py

KEY CONCEPT:
  1. You define tools as JSON schemas
  2. LLM decides which tool to call (or none)
  3. LLM returns the tool name + arguments as JSON
  4. YOUR CODE executes the function
  5. You send the result back to the LLM
  6. LLM generates the final answer
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ══════════════════════════════════════════════════════
# STEP 1: Define your tools (what the LLM can "call")
# ══════════════════════════════════════════════════════

# These are the IMPLEMENTATIONS — what actually runs
def get_weather(city: str) -> str:
    """Simulated weather API."""
    weather_data = {
        "tokyo": {"temp": 22, "condition": "Sunny", "humidity": 45},
        "london": {"temp": 14, "condition": "Cloudy", "humidity": 78},
        "new york": {"temp": 28, "condition": "Partly cloudy", "humidity": 55},
    }
    data = weather_data.get(city.lower())
    if data:
        return json.dumps({
            "city": city,
            "temperature_celsius": data["temp"],
            "condition": data["condition"],
            "humidity": data["humidity"],
        })
    return json.dumps({"error": f"Weather data not available for {city}"})


def calculate(expression: str) -> str:
    """Safe math calculator."""
    try:
        # Only allow safe math operations
        allowed = set("0123456789+-*/.(). ")
        if all(c in allowed for c in expression):
            result = eval(expression)
            return json.dumps({"expression": expression, "result": result})
        return json.dumps({"error": "Invalid expression"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def search_products(query: str, max_results: int = 3) -> str:
    """Simulated product search."""
    products = [
        {"name": "MacBook Pro 14", "price": 1999, "rating": 4.8},
        {"name": "ThinkPad X1 Carbon", "price": 1399, "rating": 4.6},
        {"name": "Dell XPS 15", "price": 1549, "rating": 4.5},
        {"name": "Surface Laptop 5", "price": 1299, "rating": 4.4},
        {"name": "MacBook Air M3", "price": 1099, "rating": 4.9},
    ]
    # Simple keyword matching
    results = [p for p in products if query.lower() in p["name"].lower() or "laptop" in query.lower()]
    if not results:
        results = products  # Return all if no match
    return json.dumps({"results": results[:max_results]})


# Map function names to implementations
TOOL_IMPLEMENTATIONS = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_products": search_products,
}

# ══════════════════════════════════════════════════════
# STEP 2: Define tool SCHEMAS (what the LLM sees)
# ══════════════════════════════════════════════════════

# These JSON schemas tell the LLM WHAT tools exist
# The LLM reads these to decide which tool to use
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific city. Returns temperature in Celsius, conditions, and humidity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (e.g., 'Tokyo', 'London', 'New York')",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression. Supports +, -, *, /, and parentheses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate (e.g., '22 * 9/5 + 32')",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products in our catalog. Returns product names, prices, and ratings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'laptop', 'MacBook')",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 3)",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


# ══════════════════════════════════════════════════════
# STEP 3: The function calling flow
# ══════════════════════════════════════════════════════

def run_with_tools(user_message: str) -> str:
    """
    Complete function calling flow:
    1. Send message + tool definitions to LLM
    2. If LLM returns tool call → execute it → send result back
    3. Repeat until LLM gives a text response
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when needed to answer accurately."},
        {"role": "user", "content": user_message},
    ]

    print(f"\n  👤 User: {user_message}")

    iteration = 0
    max_iterations = 5

    while iteration < max_iterations:
        iteration += 1

        # Call LLM with tools
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",  # LLM decides whether to use a tool
        )

        message = response.choices[0].message

        # Check if LLM wants to call tool(s)
        if message.tool_calls:
            # Add the assistant's message to history
            messages.append(message)

            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                print(f"  🔧 Tool call: {fn_name}({fn_args})")

                # Execute the tool (YOUR code runs here)
                if fn_name in TOOL_IMPLEMENTATIONS:
                    result = TOOL_IMPLEMENTATIONS[fn_name](**fn_args)
                else:
                    result = json.dumps({"error": f"Unknown tool: {fn_name}"})

                print(f"  📋 Result: {result[:100]}...")

                # Send tool result back to LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            # LLM gave a text response — we're done!
            print(f"  🤖 Answer: {message.content}")
            return message.content

    return "Max iterations reached."


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🔧 OpenAI Function Calling                  ║")
    print("╚══════════════════════════════════════════════╝")

    # Test 1: Single tool call
    print("\n" + "=" * 55)
    print("TEST 1: Single tool call")
    print("=" * 55)
    run_with_tools("What's the weather in Tokyo?")

    # Test 2: Tool + reasoning
    print("\n" + "=" * 55)
    print("TEST 2: Tool call + reasoning")
    print("=" * 55)
    run_with_tools("What's the weather in Tokyo? Also convert the temperature to Fahrenheit.")

    # Test 3: No tool needed
    print("\n" + "=" * 55)
    print("TEST 3: No tool needed (LLM answers directly)")
    print("=" * 55)
    run_with_tools("What is the capital of France?")

    # Test 4: Multiple tool calls
    print("\n" + "=" * 55)
    print("TEST 4: Multiple tools in one query")
    print("=" * 55)
    run_with_tools("Show me laptops under $1500 and tell me what the weather is like in London right now.")

    print("\n\n✅ Key insight: The LLM DECIDES which tool to use (or not).")
    print("   Your code EXECUTES. This separation is what makes agents safe.\n")


if __name__ == "__main__":
    main()
