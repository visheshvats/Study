"""
LLM-as-judge + hallucination check. See Phase 6 (06-evaluator-optimizer) sections 6.1 and 6.3.
"""
from __future__ import annotations

from typing import List

# TODO: from pydantic import BaseModel, Field


# class EvalResult(BaseModel):
#     score: int          # 1-10
#     passed: bool        # score >= 7
#     issues: List[str]
#     improvements: List[str]


def judge_output(task: str, output: str, criteria: str = "accuracy, completeness, clarity"):
    """Score an output with a strict LLM judge; return an EvalResult. Provide a parse fallback."""
    # TODO: build a judge prompt with PydanticOutputParser format instructions; parse; on error -> failing EvalResult
    raise NotImplementedError


def check_hallucination(claim: str, source_context: str) -> dict:
    """Return {'verdict': SUPPORTED|INFERRED|UNSUPPORTED, 'reason': ...} for grounding."""
    # TODO: prompt the LLM to classify the claim against the context; parse JSON.
    raise NotImplementedError


if __name__ == "__main__":
    print("Implement judge_output/check_hallucination, then use in the self-correct loop.")
