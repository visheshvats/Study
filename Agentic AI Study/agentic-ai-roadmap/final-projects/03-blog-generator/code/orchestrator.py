"""
Orchestrator: plan -> execute (dependency-aware) -> synthesize. Phase 5 section 5.1.
"""
from __future__ import annotations

import logging
from typing import Dict, List

import mock_kit
from workers import WorkerAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("orchestrator")

USE_MOCK = True


class Orchestrator:
    def __init__(self, workers: List[WorkerAgent]) -> None:
        self.workers: Dict[str, WorkerAgent] = {w.name: w for w in workers}
        if not USE_MOCK:
            from langchain_anthropic import ChatAnthropic  # type: ignore

            self.llm = ChatAnthropic(model="claude-sonnet-4-6")

    def plan(self, goal: str) -> List[Dict]:
        """Produce an ordered, dependency-aware task list (JSON)."""
        if USE_MOCK:
            # Deterministic plan; real path asks the LLM for JSON then parses w/ fallback.
            return [
                {"step": 1, "worker": "Researcher", "task": f"Research {goal}", "depends_on": []},
                {"step": 2, "worker": "Writer", "task": f"Write a draft about {goal}", "depends_on": [1]},
                {"step": 3, "worker": "Editor", "task": "Edit and polish the draft", "depends_on": [2]},
            ]
        prompt = (
            f"Break this goal into ordered subtasks for workers {list(self.workers)}.\n"
            f"Goal: {goal}\nReturn ONLY a JSON array of "
            '{step, worker, task, depends_on}.'
        )
        from langchain_core.messages import HumanMessage

        text = self.llm.invoke([HumanMessage(content=prompt)]).content
        return mock_kit.parse_plan_or_fallback(text, self.workers, goal)

    def execute(self, plan: List[Dict]) -> Dict[int, str]:
        """Run steps in order, feeding each step's dependency outputs in as context."""
        results: Dict[int, str] = {}
        for step in sorted(plan, key=lambda s: s["step"]):
            ctx = "\n\n".join(
                f"(from step {d})\n{results[d]}" for d in step.get("depends_on", []) if d in results
            )
            worker = self.workers.get(step["worker"])
            if worker is None:
                results[step["step"]] = f"ERROR: unknown worker {step['worker']!r}"
                continue
            results[step["step"]] = worker.run(step["task"], ctx)
        return results

    def synthesize(self, goal: str, results: Dict[int, str]) -> str:
        """Final article = the last (Editor) step's output."""
        if not results:
            return "(no output)"
        return results[max(results)]

    def run(self, goal: str) -> str:
        plan = self.plan(goal)
        logger.info("plan has %d steps", len(plan))
        return self.synthesize(goal, self.execute(plan))


if __name__ == "__main__":
    orch = Orchestrator([
        WorkerAgent("Researcher", "research"),
        WorkerAgent("Writer", "writing"),
        WorkerAgent("Editor", "editing"),
    ])
    print(orch.run("the benefits of RAG in enterprise AI"))
