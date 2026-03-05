"""
MODULE 5 — Example 2: Basic MCP Server
=========================================
A minimal MCP server with tools, built using the official
MCP Python SDK.

SETUP:
  pip install mcp

RUN (for testing with MCP Inspector):
  npx @modelcontextprotocol/inspector python 02_mcp_server_basic.py

OR configure in Claude Desktop:
  {
    "mcpServers": {
      "calculator": {
        "command": "python",
        "args": ["/full/path/to/02_mcp_server_basic.py"]
      }
    }
  }

KEY CONCEPT:
  An MCP server is just a Python script that exposes tools.
  The MCP SDK handles all the protocol details (JSON-RPC, etc).
"""

from mcp.server.fastmcp import FastMCP
import math
import json

# ══════════════════════════════════════════════════════
# CREATE THE MCP SERVER
# ══════════════════════════════════════════════════════

# FastMCP is the high-level API (like Flask for MCP)
mcp = FastMCP(
    name="calculator-server",
    version="1.0.0",
)


# ══════════════════════════════════════════════════════
# DEFINE TOOLS
# ══════════════════════════════════════════════════════

@mcp.tool()
def add(a: float, b: float) -> str:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        The sum of a and b
    """
    result = a + b
    return json.dumps({"operation": "add", "a": a, "b": b, "result": result})


@mcp.tool()
def multiply(a: float, b: float) -> str:
    """Multiply two numbers together.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        The product of a and b
    """
    result = a * b
    return json.dumps({"operation": "multiply", "a": a, "b": b, "result": result})


@mcp.tool()
def calculate_expression(expression: str) -> str:
    """Evaluate a mathematical expression safely.
    
    Supports: +, -, *, /, **, (), and math functions
    (sqrt, sin, cos, tan, log, pi, e).
    
    Args:
        expression: Math expression to evaluate (e.g., 'sqrt(144) + 2**3')
    
    Returns:
        The result of the expression
    """
    try:
        safe_dict = {
            "__builtins__": {},
            "math": math,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "pi": math.pi,
            "e": math.e,
            "abs": abs,
            "round": round,
        }
        result = eval(expression, safe_dict)
        return json.dumps({
            "expression": expression,
            "result": result,
        })
    except Exception as e:
        return json.dumps({
            "error": f"Cannot evaluate '{expression}': {str(e)}",
            "hint": "Use supported operations: +, -, *, /, **, (), sqrt(), sin(), cos(), log(), pi, e",
        })


@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between common units.
    
    Supported conversions:
    - Temperature: celsius, fahrenheit, kelvin
    - Length: meters, feet, inches, kilometers, miles
    - Weight: kilograms, pounds, ounces
    
    Args:
        value: The numeric value to convert
        from_unit: Source unit (e.g., 'celsius')
        to_unit: Target unit (e.g., 'fahrenheit')
    
    Returns:
        The converted value
    """
    conversions = {
        ("celsius", "fahrenheit"): lambda v: v * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda v: (v - 32) * 5 / 9,
        ("celsius", "kelvin"): lambda v: v + 273.15,
        ("kelvin", "celsius"): lambda v: v - 273.15,
        ("meters", "feet"): lambda v: v * 3.28084,
        ("feet", "meters"): lambda v: v / 3.28084,
        ("kilometers", "miles"): lambda v: v * 0.621371,
        ("miles", "kilometers"): lambda v: v / 0.621371,
        ("kilograms", "pounds"): lambda v: v * 2.20462,
        ("pounds", "kilograms"): lambda v: v / 2.20462,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return json.dumps({
            "from": f"{value} {from_unit}",
            "to": f"{round(result, 4)} {to_unit}",
        })
    
    return json.dumps({
        "error": f"Cannot convert {from_unit} to {to_unit}",
        "supported": list(set(u for pair in conversions.keys() for u in pair)),
    })


# ══════════════════════════════════════════════════════
# RUN THE SERVER
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    # This starts the server using stdio transport
    # The MCP client (Claude Desktop, etc.) will spawn this
    # process and communicate via stdin/stdout
    mcp.run()
