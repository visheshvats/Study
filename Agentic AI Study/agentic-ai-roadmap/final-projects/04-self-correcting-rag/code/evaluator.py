"""
LLM-as-judge + hallucination grounding check. Phase 6 sections 6.1 and 6.3.
MOCK scoring is deterministic and rewards specificity/figures so the retry loop
visibly improves. Real path uses PydanticOutputParser + an LLM (TODO blocks).
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

import mock_kit

USE_MOCK = True


class EvalResult(BaseModel):
    score: int = Field(ge=1, le=10)
    passed: bool
    issues: List[str] = []
    improvements: List[str] = []


def judge_output(task: str, output: str, criteria: str = "accuracy, completeness, clarity") -> EvalResult:
    """Score an output 1-10 (>=7 passes). MOCK rewards length + concrete figures + relevance."""
    if not USE_MOCK:
        # REAL:
        #   parser = PydanticOutputParser(pydantic_object=EvalResult)
        #   prompt = f"...{task}...{output}...{parser.get_format_instructions()}"
        #   return parser.parse(ChatAnthropic(model="claude-sonnet-4-6").invoke(prompt).content)
        raise NotImplementedError("set USE_MOCK=False only with the real LLM wired in")

    score = 4
    issues: List[str] = []
    improvements: List[str] = []

    if len(output) >= 120:
        score += 2
    else:
        issues.append("Answer is too brief / vague.")
        improvements.append("Expand with the concrete details from the source.")

    if any(ch.isdigit() for ch in output):
        score += 2
    else:
        issues.append("No concrete figures or timeframes cited.")
        improvements.append("Cite exact numbers (e.g., days, amounts) from the context.")

    if {t for t in mock_kit.tokenize(task) if len(t) > 3} & set(mock_kit.tokenize(output)):
        score += 1
    else:
        issues.append("Does not clearly address the question.")
        improvements.append("Directly answer the question that was asked.")

    score = min(score, 10)
    return EvalResult(score=score, passed=score >= 7, issues=issues, improvements=improvements)


def check_hallucination(claim: str, source_context: str) -> dict:
    """Return {'verdict': SUPPORTED|INFERRED|UNSUPPORTED, 'reason': ...} by grounding overlap."""
    if not USE_MOCK:
        # REAL: prompt an LLM to classify the claim against the context; parse JSON.
        raise NotImplementedError("set USE_MOCK=False only with the real LLM wired in")

    claim_tokens = {t for t in mock_kit.tokenize(claim) if len(t) > 3}
    ctx_tokens = set(mock_kit.tokenize(source_context))
    if not claim_tokens:
        return {"verdict": "UNSUPPORTED", "reason": "empty claim"}
    overlap = len(claim_tokens & ctx_tokens) / len(claim_tokens)
    if overlap >= 0.5:
        return {"verdict": "SUPPORTED", "reason": f"{overlap:.0%} of claim terms grounded in context"}
    if overlap >= 0.2:
        return {"verdict": "INFERRED", "reason": f"partial grounding ({overlap:.0%})"}
    return {"verdict": "UNSUPPORTED", "reason": f"low grounding ({overlap:.0%})"}


if __name__ == "__main__":
    print(judge_output("refund window", "It is covered by policy."))
    print(judge_output("refund window", "Based on the documentation: returns within 30 days; refunds in 5 business days."))
