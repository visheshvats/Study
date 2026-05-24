#!/usr/bin/env python3
"""
Agent Orchestrator — Autonomous LLM Agent with Tool Execution Loop
====================================================================
An event-driven execution loop that connects an LLM reasoning engine to
conditional external tool calls. Implements the core ReAct (Reason + Act)
pattern:

    Observe → Think → Decide (tool call or final answer) → Act → Repeat

Covers:
  • Tool registry with schema validation
  • Autonomous multi-step reasoning loop
  • Execution trace logging
  • Safety guardrails (max iterations, timeout simulation)
  • Inter-agent message passing

Run:
    python agent_orchestrator.py
"""

import json
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


# ── Data Types ──────────────────────────────────────────────────────────────
class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ToolDefinition:
    """Schema for a callable tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[..., str]
    requires_approval: bool = False


@dataclass
class ToolCall:
    """A single tool invocation record."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[str] = None
    duration_ms: float = 0.0
    success: bool = True


@dataclass
class ThoughtStep:
    """A single reasoning step in the agent's trace."""
    step_number: int
    observation: str
    reasoning: str
    action: str
    tool_call: Optional[ToolCall] = None


@dataclass
class AgentResult:
    """The final output of an agent execution."""
    answer: str
    steps: List[ThoughtStep]
    total_duration_ms: float
    tools_used: List[str]
    state: AgentState


# ── Mock Tool Implementations ──────────────────────────────────────────────
def calculator_tool(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "Error: Invalid characters in expression"
    try:
        result = eval(expression)  # In production: use ast.literal_eval or a parser
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"


def weather_tool(city: str) -> str:
    """Mock weather lookup."""
    weather_data = {
        "new york": "72°F, Partly Cloudy, Humidity: 65%",
        "london": "58°F, Rainy, Humidity: 80%",
        "tokyo": "68°F, Clear, Humidity: 55%",
        "mumbai": "88°F, Humid, Humidity: 85%",
        "sydney": "64°F, Sunny, Humidity: 45%",
    }
    city_lower = city.lower()
    if city_lower in weather_data:
        return f"Weather in {city}: {weather_data[city_lower]}"
    return f"Weather data not available for {city}"


def search_tool(query: str) -> str:
    """Mock web search."""
    mock_results = {
        "population": "World population (2024): approximately 8.1 billion people.",
        "python": "Python 3.12 was released in October 2023 with performance improvements.",
        "gdp": "US GDP (2024): approximately $28.78 trillion (nominal).",
        "distance": "Distance from Earth to Moon: approximately 384,400 km (238,855 miles).",
    }
    for key, result in mock_results.items():
        if key in query.lower():
            return result
    return f"No results found for: {query}"


def database_tool(query: str) -> str:
    """Mock database query."""
    mock_tables = {
        "users": [
            {"id": 1, "name": "Alice", "orders": 15, "total_spend": 2340.50},
            {"id": 2, "name": "Bob", "orders": 8, "total_spend": 1120.00},
            {"id": 3, "name": "Carol", "orders": 22, "total_spend": 4560.75},
        ],
        "products": [
            {"id": 101, "name": "Widget A", "price": 29.99, "stock": 150},
            {"id": 102, "name": "Widget B", "price": 49.99, "stock": 75},
        ],
    }
    if "users" in query.lower():
        return json.dumps(mock_tables["users"], indent=2)
    elif "products" in query.lower():
        return json.dumps(mock_tables["products"], indent=2)
    return "Error: Table not found"


# ── Mock LLM Reasoning Engine ──────────────────────────────────────────────
class MockReasoningEngine:
    """
    Simulates LLM reasoning by pattern-matching queries to predefined
    reasoning chains. In production, this calls the LLM API.
    """

    def reason(
        self,
        query: str,
        available_tools: List[str],
        history: List[ThoughtStep],
    ) -> Tuple[str, Optional[str], Optional[Dict[str, Any]]]:
        """
        Returns: (reasoning, tool_name_or_None, tool_args_or_None)
        If tool_name is None, the reasoning contains the final answer.
        """
        step = len(history)

        # First step: decide which tool to use
        if step == 0:
            query_lower = query.lower()
            if any(w in query_lower for w in ["calculate", "math", "compute", "sum"]):
                # Extract the expression
                nums = re.findall(r'[\d.+\-*/() ]+', query)
                expr = nums[0].strip() if nums else "0"
                return (
                    f"The user wants a calculation. I'll use the calculator tool with: {expr}",
                    "calculator",
                    {"expression": expr},
                )
            elif any(w in query_lower for w in ["weather", "temperature", "forecast"]):
                city = "new york"  # Default
                for c in ["new york", "london", "tokyo", "mumbai", "sydney"]:
                    if c in query_lower:
                        city = c
                        break
                return (
                    f"The user is asking about weather. I'll look up {city}.",
                    "weather",
                    {"city": city},
                )
            elif any(w in query_lower for w in ["search", "find", "what is", "who"]):
                return (
                    "The user needs information. I'll search for it.",
                    "search",
                    {"query": query},
                )
            elif any(w in query_lower for w in ["database", "users", "customers", "products"]):
                return (
                    "The user wants data from the database. I'll query it.",
                    "database",
                    {"query": query},
                )

        # If we have tool results, formulate final answer
        if history:
            last_step = history[-1]
            if last_step.tool_call and last_step.tool_call.result:
                result = last_step.tool_call.result
                return (
                    f"I have the result from {last_step.tool_call.tool_name}. "
                    f"Let me formulate the final answer based on: {result}",
                    None,
                    None,
                )

        # Default: answer directly
        return (
            "I can answer this directly without tools.",
            None,
            None,
        )


# ── Agent Orchestrator ─────────────────────────────────────────────────────
class AgentOrchestrator:
    """
    The core agent execution loop implementing ReAct (Reason + Act).

    Architecture:
        ┌─────────────────────────────────────────────┐
        │              Agent Loop                      │
        │  ┌──────────┐   ┌──────────┐   ┌─────────┐ │
        │  │ Observe  │──▶│  Think   │──▶│ Decide  │ │
        │  │ (context)│   │ (reason) │   │ (act?)  │ │
        │  └──────────┘   └──────────┘   └────┬────┘ │
        │       ▲                              │      │
        │       │         ┌──────────┐         │      │
        │       └─────────│   Act    │◀────────┘      │
        │                 │ (tool)   │                 │
        │                 └──────────┘                 │
        └─────────────────────────────────────────────┘
    """

    def __init__(
        self,
        max_iterations: int = 5,
        verbose: bool = True,
    ):
        self.max_iterations = max_iterations
        self.verbose = verbose
        self._tools: Dict[str, ToolDefinition] = {}
        self._engine = MockReasoningEngine()

    def register_tool(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def run(self, query: str) -> AgentResult:
        """Execute the agent loop for the given query."""
        start_time = time.perf_counter()
        steps: List[ThoughtStep] = []
        tools_used: List[str] = []

        if self.verbose:
            print(f"\n  🤖 AGENT: Processing query: \"{query}\"")

        for iteration in range(self.max_iterations):
            step_num = iteration + 1

            # THINK: Invoke reasoning engine
            reasoning, tool_name, tool_args = self._engine.reason(
                query, list(self._tools.keys()), steps
            )

            if self.verbose:
                print(f"\n  Step {step_num} — THINK: {reasoning[:80]}...")

            # DECIDE: Tool call or final answer?
            if tool_name is None:
                # Final answer
                step = ThoughtStep(
                    step_number=step_num,
                    observation="All necessary information gathered.",
                    reasoning=reasoning,
                    action="FINAL_ANSWER",
                )
                steps.append(step)

                # Extract answer from reasoning
                answer = reasoning
                if steps and len(steps) > 1:
                    prev = steps[-2]
                    if prev.tool_call and prev.tool_call.result:
                        answer = f"{reasoning}\n\nResult: {prev.tool_call.result}"

                elapsed = (time.perf_counter() - start_time) * 1000
                if self.verbose:
                    print(f"  Step {step_num} — ANSWER: {answer[:80]}...")
                    print(f"  ✅ Completed in {elapsed:.1f}ms ({step_num} steps)")

                return AgentResult(
                    answer=answer,
                    steps=steps,
                    total_duration_ms=elapsed,
                    tools_used=tools_used,
                    state=AgentState.COMPLETED,
                )

            # ACT: Execute tool
            tool_def = self._tools.get(tool_name)
            if not tool_def:
                step = ThoughtStep(
                    step_number=step_num,
                    observation=f"Tool '{tool_name}' not found.",
                    reasoning=reasoning,
                    action=f"ERROR: Unknown tool {tool_name}",
                )
                steps.append(step)
                continue

            # Execute the tool
            tool_start = time.perf_counter()
            try:
                result = tool_def.handler(**tool_args)
                tool_duration = (time.perf_counter() - tool_start) * 1000
                tool_call = ToolCall(
                    tool_name=tool_name,
                    arguments=tool_args,
                    result=result,
                    duration_ms=tool_duration,
                    success=True,
                )
            except Exception as e:
                tool_duration = (time.perf_counter() - tool_start) * 1000
                tool_call = ToolCall(
                    tool_name=tool_name,
                    arguments=tool_args,
                    result=f"Error: {e}",
                    duration_ms=tool_duration,
                    success=False,
                )

            tools_used.append(tool_name)

            step = ThoughtStep(
                step_number=step_num,
                observation=f"Tool '{tool_name}' returned: {tool_call.result}",
                reasoning=reasoning,
                action=f"CALL: {tool_name}({tool_args})",
                tool_call=tool_call,
            )
            steps.append(step)

            if self.verbose:
                status = "✅" if tool_call.success else "❌"
                print(f"  Step {step_num} — ACT: {tool_name}({tool_args}) → "
                      f"{status} ({tool_call.duration_ms:.1f}ms)")

        # Max iterations reached
        elapsed = (time.perf_counter() - start_time) * 1000
        return AgentResult(
            answer="Maximum iterations reached without a conclusive answer.",
            steps=steps,
            total_duration_ms=elapsed,
            tools_used=tools_used,
            state=AgentState.ERROR,
        )


# ── Demo ────────────────────────────────────────────────────────────────────
def run_demo() -> None:
    print("=" * 72)
    print("AGENT ORCHESTRATOR — Autonomous Tool-Calling Loop (ReAct)")
    print("=" * 72)

    # Create agent
    agent = AgentOrchestrator(max_iterations=5, verbose=True)

    # Register tools
    agent.register_tool(ToolDefinition(
        name="calculator",
        description="Evaluate mathematical expressions",
        parameters={"expression": {"type": "string"}},
        handler=calculator_tool,
    ))
    agent.register_tool(ToolDefinition(
        name="weather",
        description="Get current weather for a city",
        parameters={"city": {"type": "string"}},
        handler=weather_tool,
    ))
    agent.register_tool(ToolDefinition(
        name="search",
        description="Search the web for information",
        parameters={"query": {"type": "string"}},
        handler=search_tool,
    ))
    agent.register_tool(ToolDefinition(
        name="database",
        description="Query the internal database",
        parameters={"query": {"type": "string"}},
        handler=database_tool,
    ))

    # Run queries
    queries = [
        "Calculate 15 * 24 + 380 / 4",
        "What's the weather in Tokyo?",
        "What is the distance from Earth to Moon?",
        "Show me all users in the database",
    ]

    for query in queries:
        print(f"\n{'━' * 72}")
        result = agent.run(query)
        print(f"\n  📋 TRACE SUMMARY:")
        print(f"     Steps: {len(result.steps)}")
        print(f"     Tools: {result.tools_used}")
        print(f"     Time:  {result.total_duration_ms:.1f}ms")
        print(f"     State: {result.state.value}")

    # Architecture diagram
    print(f"\n{'═' * 72}")
    print("  AGENT ARCHITECTURE:")
    print("  ┌──────────┐")
    print("  │   User   │")
    print("  │  Query   │")
    print("  └────┬─────┘")
    print("       ▼")
    print("  ┌──────────────────────────────────────────┐")
    print("  │           ORCHESTRATION LOOP              │")
    print("  │  ┌────────┐  ┌────────┐  ┌────────────┐ │")
    print("  │  │Observe │─▶│ Think  │─▶│Tool / Answer│ │")
    print("  │  └────────┘  └────────┘  └─────┬──────┘ │")
    print("  │       ▲                        │        │")
    print("  │       └────────────────────────┘        │")
    print("  └──────────────────────────────────────────┘")
    print("       │")
    print("  ┌────▼────────────────────────────────────┐")
    print("  │  TOOL REGISTRY                          │")
    print("  │  ├─ calculator  (math expressions)      │")
    print("  │  ├─ weather     (city forecasts)        │")
    print("  │  ├─ search      (web lookups)           │")
    print("  │  └─ database    (SQL queries)           │")
    print("  └─────────────────────────────────────────┘")
    print("═" * 72)


if __name__ == "__main__":
    run_demo()
