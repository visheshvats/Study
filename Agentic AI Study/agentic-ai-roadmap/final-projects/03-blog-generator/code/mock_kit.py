"""
Offline scaffolding for the Blog Generator (no API key needed).
Only the LLM is mocked. Real swap: ChatAnthropic(model='claude-sonnet-4-6').
"""
from __future__ import annotations


class MockLLM:
    """Deterministic, specialty-aware generator. Each specialty consumes the upstream
    worker's output (passed as `context`) so the dependency chain is visible."""

    def generate(self, specialty: str, task: str, context: str = "") -> str:
        s = specialty.lower()
        topic = task.replace("Research", "").replace("Write a draft about", "").strip(" :.")

        if "research" in s:
            return (
                f"Research notes on {topic}:\n"
                f"- Enterprises adopt this to cut manual effort (reported ~40% time savings).\n"
                f"- Key benefit: grounding answers in private data reduces hallucination.\n"
                f"- Risk to address: retrieval quality and data freshness."
            )
        if "writ" in s:
            head = next((ln for ln in context.splitlines() if ln.strip() and not ln.startswith("(from step")), "background research")
            return (
                f"DRAFT — {topic}\n\n"
                f"Intro: {topic} is reshaping how teams work.\n"
                f"Body (grounded in: '{head}'): It delivers measurable efficiency gains "
                f"while keeping answers tied to trusted sources.\n"
                f"Conclusion: adopt incrementally and measure impact."
            )
        if "edit" in s:
            polished = context.replace("DRAFT —", "FINAL —")
            return f"{polished}\n\n[Editor: tightened intro, fixed flow, verified claims.]"
        return f"[{specialty}] output for: {task}"


def parse_plan_or_fallback(text: str, workers, goal: str):
    """Parse a JSON plan from an LLM; fall back to a single-step plan on failure.
    (In mock mode the planner already returns valid JSON; this guards the real path.)"""
    import json
    import re

    try:
        cleaned = re.sub(r"```json|```", "", text).strip()
        return json.loads(cleaned)
    except Exception:
        first = list(workers)[0]
        return [{"step": 1, "worker": first, "task": goal, "depends_on": []}]
