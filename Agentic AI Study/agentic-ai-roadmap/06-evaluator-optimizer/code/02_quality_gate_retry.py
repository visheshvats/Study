"""Phase 6.2 — Self-improving retry loop (the evaluator-optimizer).

Generate -> evaluate -> if it fails, turn the judge's complaints into feedback
-> retry with that feedback -> repeat until it passes or ``max_retries`` is hit.

Java analogy: Spring Retry with a predicate (``maxAttempts``, ``retryFor``),
EXCEPT the input changes each attempt because we inject the judge's structured
feedback into the next prompt. That feedback is the "gradient" that turns a dumb
retrier into an optimizer.

This module duplicates the judge from ``01_llm_as_judge.py`` so it is fully
self-contained (the numeric filename prefix makes a clean import awkward; in a
real package you'd ``from judge import judge_output, EvalResult``).

OFFLINE NOTE
------------
``USE_MOCK = True`` (default) runs with no network. The mock GENERATOR produces a
poor first answer and visibly better answers once feedback is present in the
prompt, so the demo prints the score CLIMBING across attempts. The mock JUDGE
returns parseable structured output. Set ``USE_MOCK = False`` + provide
``ANTHROPIC_API_KEY`` to use a real model.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ValidationError

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
USE_MOCK: bool = True  # Flip to False for the real Anthropic API.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("phase6.gate")

FEEDBACK_MARKER = "IMPORTANT — Improve"  # Generator detects feedback via this.


# --------------------------------------------------------------------------- #
# Schema + parser (duplicated from 6.1)
# --------------------------------------------------------------------------- #
class EvalResult(BaseModel):
    """Typed judge verdict. Java: a ``@Validated`` DTO."""

    score: int = Field(ge=1, le=10, description="Quality score 1-10")
    passed: bool = Field(description="True if score >= 7")
    strengths: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)


# ``from __future__ import annotations`` makes the hints strings; resolve them so
# PydanticOutputParser can introspect the schema regardless of how this module
# is loaded (run vs imported). See 01_llm_as_judge.py for the same fix.
EvalResult.model_rebuild()

eval_parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=EvalResult)


# --------------------------------------------------------------------------- #
# Mock models: a generator that IMPROVES with feedback + a parseable judge
# --------------------------------------------------------------------------- #
class _MockChatModel:
    """One fake model that plays both generator and judge.

    It tells the two roles apart by looking at the prompt: a judge prompt
    contains "OUTPUT TO EVALUATE:"; anything else is a generation request.
    """

    @staticmethod
    def _is_judge_prompt(prompt: str) -> bool:
        return "OUTPUT TO EVALUATE:" in prompt

    # ---- generator behaviour ---- #
    @staticmethod
    def _generate(prompt: str) -> str:
        # Count how many feedback rounds have accumulated. Each retry appends a
        # feedback block, so more markers == later attempt == better answer.
        feedback_rounds = prompt.count(FEEDBACK_MARKER)

        if feedback_rounds == 0:
            # Attempt 1: deliberately weak (short + vague filler).
            return "Embeddings are stuff that turns text into numbers and things."
        if feedback_rounds == 1:
            # Attempt 2: longer, less vague, but still no Java analogy.
            return (
                "A vector embedding converts text into a fixed-length array of "
                "floating point values so that texts with similar meaning end up "
                "near each other, which is what powers semantic search and similarity."
            )
        # Attempt 3+: detailed, precise, and tailored to a Java developer.
        return (
            "A vector embedding maps text into a fixed-length float array so that "
            "semantically similar text lands close together, much like a Java "
            "HashMap maps keys to buckets except distance now encodes meaning. You "
            "compare two embeddings with cosine similarity just as you'd compare two "
            "double[] arrays, and that closeness score drives semantic search."
        )

    # ---- judge behaviour (same heuristics as 6.1) ---- #
    @staticmethod
    def _extract_output(prompt: str) -> str:
        match = re.search(
            r"OUTPUT TO EVALUATE:\s*(.*?)\s*EVALUATION CRITERIA:",
            prompt,
            flags=re.DOTALL,
        )
        return match.group(1).strip() if match else ""

    def _judge(self, prompt: str) -> str:
        output = self._extract_output(prompt)
        score, strengths, issues, improvements = 5, [], [], []

        if len(output.split()) >= 25:
            score += 2
            strengths.append("Sufficient detail and length")
        else:
            issues.append("Too short / lacks detail")
            improvements.append("Expand with a concrete example")

        if re.search(r"\b(stuff|thing|kinda|sort of)\b", output, flags=re.IGNORECASE):
            score -= 2
            issues.append("Contains vague filler words")
            improvements.append("Replace vague terms with precise technical language")
        else:
            strengths.append("Precise wording")

        if re.search(r"\bjava\b", output, flags=re.IGNORECASE):
            score += 1
            strengths.append("Tailored to the Java-developer audience")
        else:
            improvements.append("Add a Java analogy for the audience")

        score = max(1, min(10, score))
        payload = EvalResult(
            score=score,
            passed=score >= 7,
            strengths=strengths,
            issues=issues,
            improvements=improvements,
        )
        return "```json\n" + payload.model_dump_json() + "\n```"

    def invoke(self, messages: List[BaseMessage]) -> BaseMessage:
        prompt = messages[-1].content
        content = self._judge(prompt) if self._is_judge_prompt(prompt) else self._generate(prompt)
        return HumanMessage(content=content)


def _build_llm():
    """Factory hiding mock-vs-real behind a uniform ``.invoke`` interface."""
    if USE_MOCK:
        logger.info("USE_MOCK=True -> deterministic offline generator + judge.")
        return _MockChatModel()

    # from langchain_anthropic import ChatAnthropic
    # return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    from langchain_anthropic import ChatAnthropic

    logger.info("USE_MOCK=False -> ChatAnthropic(claude-sonnet-4-6).")
    return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)


llm = _build_llm()


# --------------------------------------------------------------------------- #
# Judge (duplicated from 6.1) — fails closed on parse error
# --------------------------------------------------------------------------- #
def judge_output(
    task: str,
    output: str,
    criteria: str = "accuracy, completeness, clarity, conciseness",
) -> EvalResult:
    """Score output against the task; return a validated EvalResult."""
    judge_prompt = f"""You are a strict quality evaluator. Be objective and critical.

TASK:
{task}

OUTPUT TO EVALUATE:
{output}

EVALUATION CRITERIA: {criteria}

Score 1-10 (7+ = acceptable for production).
Penalize: vague claims, missing information, poor structure, hallucinations.

{eval_parser.get_format_instructions()}"""

    response = llm.invoke([HumanMessage(content=judge_prompt)])
    try:
        return eval_parser.parse(response.content)
    except (ValidationError, ValueError, Exception) as exc:  # noqa: BLE001
        logger.warning("Judge parse failed (%s); failing closed.", exc)
        return EvalResult(
            score=4,
            passed=False,
            issues=["Evaluation parsing failed"],
            improvements=["Retry"],
        )


# --------------------------------------------------------------------------- #
# The quality-gate retry loop
# --------------------------------------------------------------------------- #
def generate_with_quality_gate(
    task: str,
    max_retries: int = 3,
    pass_threshold: int = 7,
) -> Dict[str, Any]:
    """Generate, evaluate, and retry-with-feedback until pass or cap.

    Returns a dict with the final output, its evaluation, attempt count, a
    per-attempt ``history``, and a ``success`` flag that honestly reports whether
    the gate was met. ``max_retries`` is the HARD CAP — without it this is an
    infinite (and expensive) loop. Java: ``@Retryable(maxAttempts=max_retries)``.
    """
    if max_retries < 1:
        raise ValueError("max_retries must be >= 1")
    if not 1 <= pass_threshold <= 10:
        raise ValueError("pass_threshold must be in 1..10")

    history: List[Dict[str, Any]] = []
    # Accumulate feedback across attempts (the running critique). Each failed
    # attempt appends one more block, so the generator sees the full history of
    # what's been wrong so far — a richer "gradient" than only the last round.
    feedback_blocks: List[str] = []

    for attempt in range(1, max_retries + 1):
        print(f"\n🔄 Attempt {attempt}/{max_retries}")

        # Build the prompt; carry forward accumulated feedback on retries.
        prompt = task
        for block in feedback_blocks:
            prompt += f"\n\n⚠️ {FEEDBACK_MARKER} based on this feedback:\n{block}"

        output = llm.invoke([HumanMessage(content=prompt)]).content
        evaluation = judge_output(task, output)
        print(f"   Score: {evaluation.score}/10 | Passed: {evaluation.passed}")

        history.append(
            {
                "attempt": attempt,
                "score": evaluation.score,
                "output_preview": output[:100],
            }
        )

        # Exit on success OR when the cap is reached (return last attempt either way).
        if evaluation.score >= pass_threshold or attempt == max_retries:
            return {
                "output": output,
                "evaluation": evaluation,
                "attempts": attempt,
                "history": history,
                "success": evaluation.score >= pass_threshold,
            }

        # Otherwise: append structured feedback for the next attempt.
        feedback_blocks.append(
            "Issues found:\n"
            + "\n".join(f"- {i}" for i in evaluation.issues)
            + "\n\nSuggestions:\n"
            + "\n".join(f"- {s}" for s in evaluation.improvements)
        )

    # Unreachable (the loop always returns), but keeps type-checkers happy.
    raise RuntimeError("retry loop exited without returning")  # pragma: no cover


def _print_climb(history: List[Dict[str, Any]], threshold: int) -> None:
    """Render the score-per-attempt trajectory so improvement is visible."""
    parts = []
    for row in history:
        passed = row["score"] >= threshold
        parts.append(f"Attempt {row['attempt']}: {row['score']}/10 {'✅' if passed else '…'}")
    print("\n📈 Score trajectory: " + " | ".join(parts))


# --------------------------------------------------------------------------- #
# Demo
# --------------------------------------------------------------------------- #
def _demo() -> None:
    task = "Write a 2-sentence explanation of vector embeddings for a Java developer."

    # Run twice to show BOTH gate paths:
    #   threshold=7 -> accepts early once the answer is "good enough"
    #   threshold=8 -> demands a higher bar, exercising the full 3-attempt climb
    for threshold in (7, 8):
        print("\n" + "=" * 64)
        print(f"RUN with pass_threshold={threshold}")
        print("=" * 64)
        result = generate_with_quality_gate(task=task, max_retries=3, pass_threshold=threshold)

        _print_climb(result["history"], threshold=threshold)
        print(
            f"\n✅ Final (score {result['evaluation'].score}/10, "
            f"attempts={result['attempts']}, success={result['success']}):"
        )
        print(result["output"])


if __name__ == "__main__":
    _demo()
