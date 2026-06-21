"""
Phase 1 - 1.1 Basic LLM API Call & Multi-turn History
======================================================

Demonstrates the two foundational patterns:
  * ask_llm()          -> a single, stateless call
  * chat_with_history()-> multi-turn conversation where YOU manage history

Java analogy
------------
Think of the LLM call as a PURE FUNCTION:

    String reply = llm.complete(systemPrompt, fullMessageHistory, temperature);

There is NO server-side session (no HttpSession, no JSESSIONID). The conversation
"state" is just a List<Message> you carry on the client and resend EVERY call.
This is the stateless-REST discipline applied to an API.

Runs OFFLINE out of the box (USE_MOCK = True). Flip the flag to hit the real API.
"""

from __future__ import annotations

import logging
import os

# ---------------------------------------------------------------------------
# Configuration & logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
)
logger = logging.getLogger("phase1.basic_call")

# ===========================================================================
#  USE_MOCK  --  the single switch that keeps this file runnable offline.
# ---------------------------------------------------------------------------
#  True  : use the deterministic MockAnthropic client below. No network, no key.
#  False : use the REAL Anthropic SDK. To flip:
#            1) pip install anthropic python-dotenv
#            2) set ANTHROPIC_API_KEY in your environment (or code/.env)
#            3) set USE_MOCK = False
# ===========================================================================
USE_MOCK: bool = True

MODEL: str = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Mock client  (clearly marked MOCK -- not production; for offline learning)
# ---------------------------------------------------------------------------
class _MockTextBlock:
    """Mimics a single content block from the real SDK (block.text)."""

    def __init__(self, text: str) -> None:
        self.type: str = "text"
        self.text: str = text


class _MockResponse:
    """Mimics anthropic's Message response: .content is a LIST of blocks."""

    def __init__(self, text: str) -> None:
        self.content: list[_MockTextBlock] = [_MockTextBlock(text)]
        self.stop_reason: str = "end_turn"


class MockMessages:
    """MOCK of client.messages -- deterministic, no network."""

    def create(
        self,
        *,
        model: str,
        max_tokens: int,
        messages: list[dict],
        system: str = "",
        temperature: float = 1.0,
    ) -> _MockResponse:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        if isinstance(last_user, list):  # tool_result-style content; not used here
            last_user = str(last_user)

        # Deterministic fake "memory": if the user ever stated a name, recall it.
        stated_name = None
        for m in messages:
            if m["role"] == "user" and isinstance(m["content"], str):
                low = m["content"].lower()
                if "my name is" in low:
                    stated_name = m["content"].split("is", 1)[1].strip().split(".")[0].strip()

        if "what is my name" in last_user.lower() and stated_name:
            text = f"[MOCK] Your name is {stated_name}."
        elif "my name is" in last_user.lower():
            text = "[MOCK] Got it, I'll remember that."
        else:
            sys_hint = f" (system said: {system[:40]!r})" if system else ""
            text = f"[MOCK] You said: {last_user!r}.{sys_hint}"
        return _MockResponse(text)


class MockAnthropic:
    """Drop-in MOCK for anthropic.Anthropic()."""

    def __init__(self) -> None:
        self.messages = MockMessages()


# ---------------------------------------------------------------------------
# Client factory  --  the one place that chooses mock vs real
# ---------------------------------------------------------------------------
def build_client() -> object:
    if USE_MOCK:
        logger.info("Using MockAnthropic (offline, deterministic).")
        return MockAnthropic()

    # --- REAL client path ---------------------------------------------------
    from anthropic import Anthropic  # local import so mock mode needs no install
    from dotenv import load_dotenv

    load_dotenv()  # loads code/.env -> like Spring reading application.properties
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to code/.env or your environment."
        )
    logger.info("Using real Anthropic client.")
    return Anthropic()  # reads ANTHROPIC_API_KEY automatically


client = build_client()


# ---------------------------------------------------------------------------
# 1) Single stateless call
# ---------------------------------------------------------------------------
def ask_llm(
    user_message: str,
    system: str = "You are a helpful AI assistant.",
    temperature: float = 0.7,
) -> str:
    """One-shot call. No memory. Returns the assistant's text.

    `system` is the behavioral contract (like a @Configuration class).
    `temperature` is the randomness knob: 0 = deterministic, 1 = creative.
    """
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception:  # noqa: BLE001 - surface API/network errors with context
        logger.exception("ask_llm failed")
        raise
    return response.content[0].text


# ---------------------------------------------------------------------------
# 2) Multi-turn conversation -- YOU own the history list
# ---------------------------------------------------------------------------
def chat_with_history(messages: list[dict], system: str = "") -> str:
    """Send the FULL history every time. Append the reply so memory persists.

    CRITICAL: this function mutates `messages` by appending the assistant turn.
    Forgetting that append is the #1 'why did it forget?' bug.
    """
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=system,
            messages=messages,  # full history every time -- no server session!
        )
    except Exception:  # noqa: BLE001
        logger.exception("chat_with_history failed")
        raise

    assistant_reply = response.content[0].text
    # Append reply so the next turn sees both sides of the conversation.
    messages.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _demo() -> None:
    logger.info("--- ask_llm (single call) ---")
    print(ask_llm("Say hello in one sentence."))

    logger.info("--- chat_with_history (multi-turn, manual memory) ---")
    history: list[dict] = []

    history.append({"role": "user", "content": "My name is Alice. Remember that."})
    chat_with_history(history, system="You have a good memory.")

    history.append({"role": "user", "content": "What is my name?"})
    answer = chat_with_history(history)
    print(answer)  # MOCK correctly recalls "Alice" because the turn is in history

    logger.info("History now has %d turns (user+assistant pairs).", len(history))


if __name__ == "__main__":
    _demo()
