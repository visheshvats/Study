"""
Phase 1 - 1.2 Prompt Engineering Patterns
==========================================

Three workhorse patterns, each a different STRATEGY for shaping the prompt:
  * Pattern 1: Few-shot prompting      -> classify by example
  * Pattern 2: Chain-of-thought (CoT)  -> reason step by step
  * Pattern 3: Structured JSON output  -> turn prose into a typed object

Plus extract_json(), the defensive deserialization step.

Java analogy
------------
The three patterns are like three implementations of a Strategy interface
("build a prompt"): ClassifierStrategy, ReasoningStrategy, ExtractionStrategy.
extract_json() is your Jackson boundary -- ObjectMapper.readValue(json, T.class) --
except the producer is a probabilistic model, so you MUST defend the parse
(strip the ```json fences models love to add).

Runs OFFLINE out of the box (USE_MOCK = True).
"""

from __future__ import annotations

import json
import logging
import os
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
)
logger = logging.getLogger("phase1.prompt_patterns")

# ===========================================================================
#  USE_MOCK : True = offline deterministic mock; False = real Anthropic SDK.
#  To use the real client:
#    1) pip install anthropic python-dotenv
#    2) set ANTHROPIC_API_KEY (env or code/.env)
#    3) USE_MOCK = False
# ===========================================================================
USE_MOCK: bool = True

MODEL: str = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Mock client  (MOCK -- offline learning only)
# ---------------------------------------------------------------------------
class _MockTextBlock:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _MockResponse:
    def __init__(self, text: str) -> None:
        self.content = [_MockTextBlock(text)]
        self.stop_reason = "end_turn"


class MockMessages:
    """Deterministic fake replies keyed off the system prompt's intent."""

    def create(
        self,
        *,
        model: str,
        max_tokens: int,
        messages: list[dict],
        system: str = "",
        temperature: float = 1.0,
    ) -> _MockResponse:
        user = messages[-1]["content"] if messages else ""
        sys_low = system.lower()

        # Pattern 1: few-shot classifier -> return ONE category word
        if "classify customer feedback" in sys_low:
            u = user.lower()
            if "crash" in u or "fails" in u or "broken" in u:
                return _MockResponse("BUG")
            if "would love" in u or "add" in u or "feature" in u:
                return _MockResponse("FEATURE_REQUEST")
            if "love" in u or "great" in u or "amazing" in u:
                return _MockResponse("PRAISE")
            return _MockResponse("QUESTION")

        # Pattern 2: chain-of-thought -> THOUGHT/ANSWER format
        if "step by step" in sys_low:
            return _MockResponse(
                "THOUGHT: 3 calls remaining, each op costs 2, so floor(3/2) = 1.\n"
                "ANSWER: 1"
            )

        # Pattern 3: structured JSON -> raw JSON (intentionally fenced to test stripping)
        if "valid json" in sys_low:
            payload = {
                "name": "Alice",
                "age": 28,
                "skills": ["Java"],
                "experience_years": 5,
            }
            # Models often wrap JSON in fences even when told not to -> we test that.
            return _MockResponse("```json\n" + json.dumps(payload) + "\n```")

        return _MockResponse(f"[MOCK] {user}")


class MockAnthropic:
    def __init__(self) -> None:
        self.messages = MockMessages()


def build_client() -> object:
    if USE_MOCK:
        logger.info("Using MockAnthropic (offline).")
        return MockAnthropic()
    from anthropic import Anthropic
    from dotenv import load_dotenv

    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY not set (code/.env or environment).")
    logger.info("Using real Anthropic client.")
    return Anthropic()


client = build_client()


def ask_llm(user_message: str, system: str = "", temperature: float = 0.0) -> str:
    """Single call helper. temperature=0 by default -- these patterns want determinism."""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception:  # noqa: BLE001
        logger.exception("ask_llm failed")
        raise
    return response.content[0].text


# ---------------------------------------------------------------------------
# Pattern 1: Few-shot prompting
# ---------------------------------------------------------------------------
FEW_SHOT_SYSTEM = """You classify customer feedback.
Categories: BUG, FEATURE_REQUEST, PRAISE, QUESTION

Examples:
Feedback: "The app crashes when I open settings"
Category: BUG

Feedback: "Would love a dark mode option"
Category: FEATURE_REQUEST

Feedback: "Absolutely love how fast it loads!"
Category: PRAISE

Return ONLY the category word."""


def classify_feedback(feedback: str) -> str:
    """Few-shot classifier. The examples ARE the contract (like test fixtures)."""
    return ask_llm(feedback, FEW_SHOT_SYSTEM, temperature=0.0).strip()


# ---------------------------------------------------------------------------
# Pattern 2: Chain of thought
# ---------------------------------------------------------------------------
COT_SYSTEM = """Solve the problem step by step.
Format:
THOUGHT: <your reasoning>
ANSWER: <final answer only>"""


def solve_with_reasoning(problem: str) -> str:
    """Force visible reasoning before the answer -> better multi-step accuracy."""
    return ask_llm(problem, COT_SYSTEM, temperature=0.0)


# ---------------------------------------------------------------------------
# Pattern 3: Structured JSON output + defensive parse
# ---------------------------------------------------------------------------
JSON_SYSTEM = """Extract structured data and return ONLY valid JSON.
No markdown code fences. No preamble. Raw JSON only.

Schema:
{
  "name": string,
  "age": number | null,
  "skills": string[],
  "experience_years": number | null
}"""


def extract_json(text: str) -> dict:
    """Defensive deserialization: strip markdown fences, then json.loads.

    This is the Jackson boundary. Always run it -- models add ```json fences
    even when instructed not to, and a raw json.loads() would throw.
    """
    clean = re.sub(r"```json|```", "", text).strip()
    return json.loads(clean)


def extract_profile(sentence: str) -> dict:
    raw = ask_llm(sentence, JSON_SYSTEM, temperature=0.0)
    return extract_json(raw)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _demo() -> None:
    logger.info("--- Pattern 1: few-shot classifier ---")
    for fb in [
        "Why can't I export to PDF?",
        "The login button is broken",
        "Absolutely love how fast it loads!",
        "Please add a dark mode",
    ]:
        print(f"{fb!r:45} -> {classify_feedback(fb)}")

    logger.info("--- Pattern 2: chain of thought ---")
    print(
        solve_with_reasoning(
            "A user has 3 API calls remaining. Each operation costs 2 calls. "
            "How many operations can they do?"
        )
    )

    logger.info("--- Pattern 3: structured JSON ---")
    data = extract_profile(
        "Alice is a 28-year-old Java developer with 5 years of experience."
    )
    print("Parsed dict:", data)
    print("Skills:", data["skills"])  # ['Java']


if __name__ == "__main__":
    _demo()
