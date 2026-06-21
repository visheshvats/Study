"""
Phase 1 - 1.4 Tool / Function Calling & the Agentic Loop
========================================================

Builds an agent with TWO tools and the agentic loop that drives them:
  * TOOLS         -> JSON schemas the model can request (its "API catalog")
  * TOOL_REGISTRY -> name -> python function (your IoC container / DI map)
  * run_tool_agent() -> call model; if stop_reason == "tool_use", execute the
                        requested tool, feed the result back, repeat until done.

Java analogy
------------
TOOL_REGISTRY is a Map<String, Function> -- the application context of available
beans, keyed by name. The model says "I need the bean named create_ticket"; you
look it up and invoke it. The model ORCHESTRATES; your code EXECUTES. That
inversion of control is the leap from "API client" to "agent". You can swap real
implementations for mocks without the model knowing -- exactly like injecting a
stub @Repository in a test.

Runs OFFLINE out of the box (USE_MOCK = True). The mock model is scripted to
walk the loop: search the KB, then create a ticket, then answer.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Callable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
)
logger = logging.getLogger("phase1.tool_agent")

# ===========================================================================
#  USE_MOCK : True = offline scripted agent; False = real Anthropic SDK.
#  To use the real client:
#    1) pip install anthropic python-dotenv
#    2) set ANTHROPIC_API_KEY (env or code/.env)
#    3) USE_MOCK = False
# ===========================================================================
USE_MOCK: bool = True

MODEL: str = "claude-sonnet-4-6"
MAX_TURNS: int = 8  # safety valve so a misbehaving loop can't run forever


# ---------------------------------------------------------------------------
# Tool definitions -- the model's "API catalog" (JSON schemas)
# ---------------------------------------------------------------------------
TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_knowledge_base",
        "description": "Search internal knowledge base for information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 3},
            },
            "required": ["query"],
        },
    },
    {
        "name": "create_ticket",
        "description": "Create a support ticket",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
                "description": {"type": "string"},
            },
            "required": ["title", "priority", "description"],
        },
    },
]


# ---------------------------------------------------------------------------
# Tool implementations (MOCK business logic -- clearly marked).
# In production these would call a real search index and a real ticketing API.
# ---------------------------------------------------------------------------
def search_knowledge_base(query: str, max_results: int = 3) -> list[dict[str, Any]]:
    """MOCK knowledge-base search. Replace with a real search index in prod."""
    logger.info("[MOCK tool] search_knowledge_base(query=%r, max_results=%d)", query, max_results)
    return [
        {"id": 1, "title": f"Article about {query}", "snippet": "Known issue, fix pending."},
        {"id": 2, "title": f"FAQ: {query}", "snippet": "Workaround available."},
    ][:max_results]


def create_ticket(title: str, priority: str, description: str) -> dict[str, Any]:
    """MOCK ticket creation. Replace with a real ticketing API in prod."""
    logger.info("[MOCK tool] create_ticket(title=%r, priority=%r)", title, priority)
    return {"ticket_id": "TKT-001", "status": "CREATED", "title": title, "priority": priority}


TOOL_REGISTRY: dict[str, Callable[..., Any]] = {
    "search_knowledge_base": search_knowledge_base,
    "create_ticket": create_ticket,
}


# ---------------------------------------------------------------------------
# Mock model  (MOCK -- scripts the agentic loop so it runs offline)
# ---------------------------------------------------------------------------
class _MockToolUseBlock:
    def __init__(self, name: str, tool_input: dict[str, Any], block_id: str) -> None:
        self.type = "tool_use"
        self.name = name
        self.input = tool_input
        self.id = block_id


class _MockTextBlock:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _MockResponse:
    def __init__(self, content: list[Any], stop_reason: str) -> None:
        self.content = content
        self.stop_reason = stop_reason


class MockMessages:
    """Scripted model: decides what to do by inspecting the conversation so far.

    Step 1 (no tool used yet)   -> ask to search_knowledge_base
    Step 2 (search done)        -> ask to create_ticket
    Step 3 (ticket done)        -> final text answer (stop_reason='end_turn')
    """

    def create(
        self,
        *,
        model: str,
        max_tokens: int,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> _MockResponse:
        used = _tools_already_used(messages)

        if "search_knowledge_base" not in used:
            block = _MockToolUseBlock(
                "search_knowledge_base",
                {"query": "login fails for enterprise users", "max_results": 2},
                "toolu_mock_1",
            )
            return _MockResponse([block], "tool_use")

        if "create_ticket" not in used:
            block = _MockToolUseBlock(
                "create_ticket",
                {
                    "title": "Login fails for enterprise users",
                    "priority": "HIGH",
                    "description": "Enterprise SSO users cannot log in.",
                },
                "toolu_mock_2",
            )
            return _MockResponse([block], "tool_use")

        return _MockResponse(
            [_MockTextBlock("[MOCK] Created HIGH-priority ticket TKT-001 for the login issue.")],
            "end_turn",
        )


def _tools_already_used(messages: list[dict]) -> set[str]:
    """Scan history for assistant tool_use blocks we've already executed."""
    used: set[str] = set()
    for m in messages:
        if m["role"] == "assistant" and isinstance(m["content"], list):
            for block in m["content"]:
                name = getattr(block, "name", None)
                if getattr(block, "type", None) == "tool_use" and name:
                    used.add(name)
    return used


class MockAnthropic:
    def __init__(self) -> None:
        self.messages = MockMessages()


def build_client() -> object:
    if USE_MOCK:
        logger.info("Using MockAnthropic tool agent (offline, scripted loop).")
        return MockAnthropic()
    from anthropic import Anthropic
    from dotenv import load_dotenv

    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY not set (code/.env or environment).")
    logger.info("Using real Anthropic client.")
    return Anthropic()


client = build_client()


# ---------------------------------------------------------------------------
# The agentic loop
# ---------------------------------------------------------------------------
def run_tool_agent(user_message: str) -> str:
    """Drive the model through tool calls until it produces a final answer.

    Loop invariant: while stop_reason == "tool_use", execute the requested tool
    and feed the result back; otherwise return the final text. MAX_TURNS guards
    against an infinite loop.
    """
    messages: list[dict] = [{"role": "user", "content": user_message}]

    for turn in range(1, MAX_TURNS + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                tools=TOOLS,
                messages=messages,
            )
        except Exception:  # noqa: BLE001
            logger.exception("model call failed on turn %d", turn)
            raise

        if response.stop_reason == "tool_use":
            # The model asked for a tool. Find the tool_use block.
            tool_block = next(b for b in response.content if b.type == "tool_use")
            tool_name = tool_block.name
            tool_input = tool_block.input
            logger.info("Turn %d: tool requested -> %s(%s)", turn, tool_name, tool_input)

            # Execute it via the registry (our DI map). The model never runs code.
            fn = TOOL_REGISTRY.get(tool_name)
            if fn is None:
                tool_result: Any = {"error": f"Unknown tool: {tool_name}"}
            else:
                try:
                    tool_result = fn(**tool_input)
                except Exception as exc:  # noqa: BLE001 - report tool errors to the model
                    logger.exception("tool %s raised", tool_name)
                    tool_result = {"error": str(exc)}

            # Append BOTH turns: assistant's tool_use AND the matching tool_result.
            messages.append({"role": "assistant", "content": response.content})
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,  # MUST match the request id
                            "content": json.dumps(tool_result),
                        }
                    ],
                }
            )
            continue  # loop again so the model can react to the result

        # stop_reason != "tool_use" -> the model is done. Return its text.
        logger.info("Turn %d: final answer (stop_reason=%s)", turn, response.stop_reason)
        return next(b.text for b in response.content if getattr(b, "type", None) == "text")

    raise RuntimeError(f"Agent did not finish within MAX_TURNS={MAX_TURNS}")


def _demo() -> None:
    logger.info("--- tool-calling agent ---")
    result = run_tool_agent(
        "I need to create a HIGH priority ticket: Login fails for enterprise users"
    )
    print("\nFinal answer:", result)


if __name__ == "__main__":
    _demo()
