"""
Specialist worker agents. Phase 5 section 5.1.
Specialty is injected as a system prompt. MOCK uses a deterministic generator;
REAL uses ChatAnthropic with SystemMessage/HumanMessage.
"""
from __future__ import annotations

import logging

import mock_kit

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("workers")

USE_MOCK = True


class WorkerAgent:
    def __init__(self, name: str, specialty: str, instructions: str = "") -> None:
        self.name = name
        self.specialty = specialty
        self.instructions = instructions or f"You are a {specialty} specialist."
        if not USE_MOCK:
            from langchain_anthropic import ChatAnthropic  # type: ignore

            self.llm = ChatAnthropic(model="claude-sonnet-4-6")

    def run(self, task: str, context: str = "") -> str:
        """Execute the task with optional upstream context; return the worker's output."""
        if USE_MOCK:
            out = mock_kit.MockLLM().generate(self.specialty, task, context)
        else:
            from langchain_core.messages import HumanMessage, SystemMessage

            messages = [SystemMessage(content=self.instructions)]
            if context:
                messages.append(HumanMessage(content=f"Context:\n{context}"))
            messages.append(HumanMessage(content=f"Task:\n{task}"))
            out = self.llm.invoke(messages).content
        logger.info("[%s] completed", self.name)
        return out


if __name__ == "__main__":
    r = WorkerAgent("Researcher", "research").run("Research benefits of RAG")
    print(r)
