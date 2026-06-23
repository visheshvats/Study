"""
Orchestrator: plan -> execute (dependency-aware) -> synthesize.
See Phase 5 section 5.1. Guard the JSON parse — the LLM will occasionally misbehave.
"""
from __future__ import annotations

from typing import Dict, List


class Orchestrator:
    def __init__(self, workers: List["WorkerAgent"]) -> None:  # type: ignore[name-defined]
        self.workers = {w.name: w for w in workers}
        # TODO: self.llm = ChatAnthropic(model="claude-sonnet-4-6")

    def plan(self, goal: str) -> List[Dict]:
        """Ask the LLM for an ordered JSON task list; fall back to a single step on parse failure."""
        # TODO: prompt the LLM for a JSON array of {step, worker, task, depends_on}
        # TODO: strip ```json fences, json.loads, except -> [{"step":1,...}]
        raise NotImplementedError

    def execute(self, plan: List[Dict]) -> Dict[int, str]:
        """Run steps in order, feeding each step's dependencies in as context."""
        # TODO: for step in sorted(plan, key=step): gather dep context, call worker.run(...)
        raise NotImplementedError

    def synthesize(self, goal: str, results: Dict[int, str]) -> str:
        """Combine all worker outputs into the final article."""
        # TODO: prompt the LLM with goal + results to produce the final post.
        raise NotImplementedError

    def run(self, goal: str) -> str:
        plan = self.plan(goal)
        results = self.execute(plan)
        return self.synthesize(goal, results)


if __name__ == "__main__":
    print("Implement plan/execute/synthesize, then Orchestrator([...]).run(goal)")
