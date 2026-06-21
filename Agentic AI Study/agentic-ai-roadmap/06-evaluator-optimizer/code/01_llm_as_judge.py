"""Phase 6.1 — LLM-as-Judge.

Use a (preferably separate) LLM call to *evaluate* the output of another LLM,
returning a typed, validated verdict instead of a paragraph of prose.

Java analogy: the judge is a code-review bot. ``EvalResult`` is a ``@Validated``
DTO; ``PydanticOutputParser`` is the Jackson ``ObjectMapper`` + bean validation
that turns the model's text into that typed object.

OFFLINE NOTE
------------
This file runs with NO network and NO API key when ``USE_MOCK = True`` (the
default). A deterministic fake chat model stands in for the real LLM so the
LLM-as-judge flow is fully demonstrable offline. To use a real model, set
``USE_MOCK = False`` and provide ``ANTHROPIC_API_KEY`` (see ``.env.example``).
"""

from __future__ import annotations

import logging
import re
from typing import List

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ValidationError

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
# Flip to False to call the real Anthropic API instead of the offline mock.
USE_MOCK: bool = True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("phase6.judge")


# --------------------------------------------------------------------------- #
# 1. The evaluation schema — a validated DTO
# --------------------------------------------------------------------------- #
class EvalResult(BaseModel):
    """Typed verdict from the judge.

    Java: ``record EvalResult(@Min(1) @Max(10) int score, boolean passed, ...)``.
    Pydantic validates on construction exactly like Hibernate Validator on
    ``@Valid`` — a ``score`` of 15 raises ``ValidationError`` and never enters
    the program.
    """

    score: int = Field(ge=1, le=10, description="Quality score 1-10")
    passed: bool = Field(description="True if score >= 7")
    strengths: List[str] = Field(default_factory=list, description="What the output does well")
    issues: List[str] = Field(default_factory=list, description="Specific problems found")
    improvements: List[str] = Field(
        default_factory=list, description="Concrete suggestions for improvement"
    )


# ``from __future__ import annotations`` turns the type hints into strings, so we
# must resolve them before PydanticOutputParser introspects the schema. Without
# this, ``get_format_instructions()`` raises when the module is imported (rather
# than run as __main__). One line; saves a confusing error later.
EvalResult.model_rebuild()


# PydanticOutputParser == ObjectMapper for LLM text. It both (a) generates the
# format instructions we paste into the prompt and (b) parses+validates the
# model's reply into an EvalResult.
eval_parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=EvalResult)


# --------------------------------------------------------------------------- #
# 2. The model: offline mock OR real ChatAnthropic
# --------------------------------------------------------------------------- #
class _MockJudgeModel:
    """Deterministic fake chat model that emits parseable judge JSON.

    It inspects the prompt for the OUTPUT-TO-EVALUATE block and scores by simple,
    repeatable heuristics so the demo always behaves the same way offline.
    """

    @staticmethod
    def _extract_output(prompt: str) -> str:
        # Pull the text between "OUTPUT TO EVALUATE:" and "EVALUATION CRITERIA:".
        match = re.search(
            r"OUTPUT TO EVALUATE:\s*(.*?)\s*EVALUATION CRITERIA:",
            prompt,
            flags=re.DOTALL,
        )
        return match.group(1).strip() if match else ""

    def invoke(self, messages: List[BaseMessage]) -> BaseMessage:
        prompt = messages[-1].content
        output = self._extract_output(prompt)

        # Deterministic scoring heuristics (stand-in for a real judge's judgment):
        #  - longer, structured answers score higher
        #  - the word "stuff"/"thing" (vagueness) is penalised
        #  - a Java-developer audience term earns a point (relevance)
        score = 5
        issues: List[str] = []
        strengths: List[str] = []
        improvements: List[str] = []

        word_count = len(output.split())
        if word_count >= 25:
            score += 2
            strengths.append("Sufficient detail and length")
        else:
            issues.append("Too short / lacks detail")
            improvements.append("Expand the explanation with a concrete example")

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
            improvements.append("Tie the explanation to a Java analogy for the audience")

        score = max(1, min(10, score))
        passed = score >= 7

        # Emit JSON wrapped in a code fence — exactly the noise a real model adds,
        # so eval_parser.parse() is exercised against realistic input.
        payload = EvalResult(
            score=score,
            passed=passed,
            strengths=strengths,
            issues=issues,
            improvements=improvements,
        )
        return HumanMessage(content="```json\n" + payload.model_dump_json() + "\n```")


def _build_llm():
    """Return the chat model to use as the judge.

    Java analogy: a small factory / ``@Bean`` provider that hides the concrete
    implementation behind a uniform ``.invoke(messages)`` interface.
    """
    if USE_MOCK:
        logger.info("USE_MOCK=True -> using deterministic offline judge model.")
        return _MockJudgeModel()

    # --- Real model (requires `pip install langchain-anthropic` + API key) --- #
    # from langchain_anthropic import ChatAnthropic
    # return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    from langchain_anthropic import ChatAnthropic  # noqa: WPS433 (local import on purpose)

    logger.info("USE_MOCK=False -> using ChatAnthropic(claude-sonnet-4-6).")
    return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)


llm = _build_llm()


# --------------------------------------------------------------------------- #
# 3. The judge function
# --------------------------------------------------------------------------- #
def judge_output(
    task: str,
    output: str,
    criteria: str = "accuracy, completeness, clarity, conciseness",
) -> EvalResult:
    """Score ``output`` against ``task`` and ``criteria`` using the LLM judge.

    Fails CLOSED: if parsing the judge's reply fails, we return a *failing*
    EvalResult rather than letting the exception propagate or waving the output
    through. (Java: catch ``JsonProcessingException``, return a safe default.)
    """
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
        # Fail closed — never trust an output we could not verify.
        logger.warning("Judge parse failed (%s); returning fail-closed result.", exc)
        logger.debug("Raw judge response was: %r", getattr(response, "content", response))
        return EvalResult(
            score=4,
            passed=False,
            strengths=[],
            issues=["Evaluation parsing failed"],
            improvements=["Retry"],
        )


# --------------------------------------------------------------------------- #
# 4. Demo
# --------------------------------------------------------------------------- #
def _demo() -> None:
    task = "Write a 2-sentence explanation of vector embeddings for a Java developer."

    # A weak answer (short + vague) and a strong answer (detailed + Java-aware).
    weak = "Embeddings are stuff that turns text into numbers and things."
    strong = (
        "A vector embedding maps text into a fixed-length array of floats so that "
        "semantically similar text lands close together in that space, much like "
        "hashing in Java maps objects to buckets except distance now means meaning. "
        "You compare two embeddings with cosine similarity the way you'd compare "
        "two double[] arrays, and that score powers semantic search."
    )

    for label, candidate in (("WEAK", weak), ("STRONG", strong)):
        logger.info("Judging %s answer...", label)
        result = judge_output(task, candidate)
        print(f"\n=== {label} answer ===")
        print(f"  text     : {candidate[:80]}...")
        print(f"  score    : {result.score}/10")
        print(f"  passed   : {result.passed}")
        print(f"  strengths: {result.strengths}")
        print(f"  issues   : {result.issues}")
        print(f"  improve  : {result.improvements}")


if __name__ == "__main__":
    _demo()
