"""
Specialist worker agents. See Phase 5 (05-orchestrators) section 5.1.
"""
from __future__ import annotations


class WorkerAgent:
    """A specialist agent: its 'specialty' is injected as a system prompt."""

    def __init__(self, name: str, specialty: str, instructions: str = "") -> None:
        self.name = name
        self.specialty = specialty
        self.instructions = instructions or f"You are a {specialty} specialist."
        # TODO: self.llm = ChatAnthropic(model="claude-sonnet-4-6")

    def run(self, task: str, context: str = "") -> str:
        """Run the task with optional upstream context; return the worker's output."""
        # TODO: messages = [SystemMessage(self.instructions)]
        # TODO: if context: messages.append(HumanMessage(f"Context:\n{context}"))
        # TODO: messages.append(HumanMessage(f"Task:\n{task}"))
        # TODO: return self.llm.invoke(messages).content
        raise NotImplementedError


if __name__ == "__main__":
    print("Implement WorkerAgent.run, then build Researcher/Writer/Editor instances.")
