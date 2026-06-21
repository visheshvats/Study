"""03_react_agent.py — a ReAct agent with tools (Phase 3.3).

ReAct = "Reasoning + Acting". The model loops:
    think -> decide to call a tool -> read the tool result -> think again ...
until it has enough information to answer. LangGraph's `create_react_agent`
builds this loop for you as a prebuilt graph (agent node <-> tools node).

Java analogy: imagine a Spring service that, on each request, may call out to
other @Service beans (the tools), feed their return values back into its own
logic, and repeat until done. The "agent" node is the orchestrating service;
the "tools" node is the bean registry it can dispatch to. The ReAct loop is the
while-loop that keeps dispatching until no more tool calls are requested.

OFFLINE NOTE
------------
A genuine ReAct loop needs a model that can emit structured tool calls, which a
trivial stub cannot fake well. So this file does two things:

  * USE_MOCK = True  -> runs a small HAND-WRITTEN ReAct loop using a FakeChatModel
                        that emits deterministic tool-call "decisions". This
                        exercises the SAME mechanics (reason -> call tool -> read
                        result -> answer) so you can watch the loop work offline.
  * USE_MOCK = False -> uses the real ChatAnthropic + create_react_agent.

The TOOLS themselves (calculator, get_stock_price, search_docs) are identical in
both modes and are fully implemented below.

Run it (offline):  python 03_react_agent.py
To use the real agent: set USE_MOCK = False and export ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import json
import logging
import math
from typing import Any, List

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

USE_MOCK = True  # offline by default


# ─────────────────────────────────────────────────────────────────────────────
# TOOLS — these are real and run identically offline or online.
# The @tool decorator turns a typed function into a schema the model can call —
# like exposing a method as a callable endpoint with its signature published.
# ─────────────────────────────────────────────────────────────────────────────
@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression safely. Supports basic arithmetic and math functions."""
    # SAFETY: we disable all builtins ({"__builtins__": {}}) so `eval` cannot
    # reach open(), __import__, etc. Only names from the `math` module are
    # allowed. This is the sandboxing the source mandates — never eval() raw
    # user input without locking down the namespace.
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307 (sandboxed)
        return str(result)
    except Exception as e:  # noqa: BLE001 — tools must return errors as data, not raise
        return f"Error: {e}"


@tool
def get_stock_price(ticker: str) -> str:
    """Get the current stock price for a ticker symbol."""
    # MOCK IMPLEMENTATION (clearly marked). In production, replace with a real
    # API call (Alpha Vantage, Yahoo Finance, etc.). Returns JSON so the model
    # gets structured data it can reason over.
    mock_prices = {"AAPL": 189.50, "GOOG": 2750.30, "MSFT": 415.20}
    price = mock_prices.get(ticker.upper())
    if price is None:
        return f"Unknown ticker: {ticker}"
    return json.dumps({"ticker": ticker.upper(), "price": price, "currency": "USD"})


@tool
def search_docs(query: str) -> str:
    """Search the product documentation for information."""
    # MOCK IMPLEMENTATION (clearly marked). In production, replace with a vector
    # store retrieval (Phase 2 / Phase 8 territory). Here we return a fixed fact.
    return f"[Doc search: '{query}'] Found: The feature supports up to 100 concurrent users."


TOOLS = [calculator, get_stock_price, search_docs]
# Registry by name so our offline loop can dispatch calls — the same lookup
# create_react_agent does internally.
TOOLS_BY_NAME = {t.name: t for t in TOOLS}


# ─────────────────────────────────────────────────────────────────────────────
# OFFLINE PATH: FakeChatModel + a tiny hand-written ReAct loop
# ─────────────────────────────────────────────────────────────────────────────
class FakeChatModel:
    """A scripted "model" that demonstrates the reason->act->observe loop.

    On each .invoke(messages) it looks at how many ToolMessages it has already
    seen and decides the next move. This is NOT intelligence — it is a fixed
    script — but it drives the EXACT same control flow as a real ReAct agent so
    you can watch tools being invoked and observations flowing back.

    It returns AIMessages carrying `.tool_calls` (a list of dicts) when it wants
    a tool, mirroring how a real model signals tool use.
    """

    def invoke(self, messages: List[Any]) -> AIMessage:
        observations = [m for m in messages if isinstance(m, ToolMessage)]
        seen = {obs.name for obs in observations}

        # Step 1: no observations yet -> ask for the stock price.
        if "get_stock_price" not in seen:
            return AIMessage(
                content="I should look up the AAPL stock price first.",
                tool_calls=[
                    {"name": "get_stock_price", "args": {"ticker": "AAPL"}, "id": "call-1"}
                ],
            )

        # Step 2: we have the price -> compute 15% of it.
        if "calculator" not in seen:
            price = _extract_price(observations)
            return AIMessage(
                content=f"Now I'll compute 15% of {price}.",
                tool_calls=[
                    {"name": "calculator", "args": {"expression": f"{price} * 0.15"}, "id": "call-2"}
                ],
            )

        # Step 3: we have the math -> look up the docs.
        if "search_docs" not in seen:
            return AIMessage(
                content="Next, search the docs for concurrent-user limits.",
                tool_calls=[
                    {"name": "search_docs", "args": {"query": "concurrent users"}, "id": "call-3"}
                ],
            )

        # Step 4: have everything -> final answer, no more tool calls.
        return AIMessage(
            content="15% of the AAPL price is computed above, and the product "
            "supports up to 100 concurrent users.",
            tool_calls=[],
        )

    def bind_tools(self, tools: List[Any]) -> "FakeChatModel":
        # Real chat models expose bind_tools(); we accept and ignore it so the
        # interface matches and swapping is frictionless.
        return self


def _extract_price(observations: List[ToolMessage]) -> float:
    for obs in observations:
        if obs.name == "get_stock_price":
            try:
                return float(json.loads(obs.content)["price"])
            except Exception:  # noqa: BLE001
                return 0.0
    return 0.0


def run_offline_react(model: FakeChatModel, user_msg: str) -> List[Any]:
    """A minimal ReAct loop: keep invoking the model; whenever it asks for a
    tool, run the tool and feed the result back; stop when it stops asking.

    This is the de-sugared version of what create_react_agent's compiled graph
    does (agent node -> conditional edge -> tools node -> back to agent).
    """
    messages: List[Any] = [HumanMessage(user_msg)]
    max_iterations = 6  # guardrail against infinite loops — always cap your agent

    for i in range(max_iterations):
        ai_msg = model.invoke(messages)
        messages.append(ai_msg)

        if not ai_msg.tool_calls:
            logger.info("[loop %d] model gave final answer — stopping.", i)
            break

        # Dispatch each requested tool and append a ToolMessage observation.
        for call in ai_msg.tool_calls:
            name, args, call_id = call["name"], call["args"], call["id"]
            logger.info("[loop %d] model -> tool %s(%s)", i, name, args)
            tool_fn = TOOLS_BY_NAME[name]
            observation = tool_fn.invoke(args)  # tools created with @tool expose .invoke
            logger.info("[loop %d] tool %s -> %s", i, name, str(observation)[:80])
            messages.append(ToolMessage(content=str(observation), name=name, tool_call_id=call_id))

    return messages


# ─────────────────────────────────────────────────────────────────────────────
# ONLINE PATH: the real prebuilt ReAct agent
# ─────────────────────────────────────────────────────────────────────────────
def run_real_react(user_msg: str) -> List[Any]:
    from langchain_anthropic import ChatAnthropic
    from langgraph.prebuilt import create_react_agent

    llm = ChatAnthropic(model="claude-sonnet-4-6")
    agent = create_react_agent(llm, tools=TOOLS)
    result = agent.invoke({"messages": [HumanMessage(user_msg)]})
    return result["messages"]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    user_msg = (
        "What is 15% of AAPL stock price? "
        "Also how many concurrent users does the product support?"
    )

    if USE_MOCK:
        logger.info("Running OFFLINE hand-written ReAct loop (USE_MOCK=True).")
        messages = run_offline_react(FakeChatModel(), user_msg)
    else:
        logger.info("Running REAL create_react_agent (USE_MOCK=False).")
        messages = run_real_react(user_msg)

    logger.info("─── Conversation trace (%d messages) ───", len(messages))
    for msg in messages:
        logger.info("[%s]: %s", msg.__class__.__name__, str(msg.content)[:200])

    logger.info("ReAct agent demo complete.")


if __name__ == "__main__":
    main()
