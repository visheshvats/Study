"""
01_worker_agent.py
==================================================================
Phase 5 — Orchestrators (Multi-Agent)
The WorkerAgent: a single specialist agent with an injected role.

JAVA ANALOGY
------------
A WorkerAgent is a *concrete strategy bean*. There is one class with one
public method (`run`), and the behaviour is specialized entirely by what you
inject through the constructor (the `instructions` / system prompt). Think:

    public interface Worker { String run(String task, String context); }
    // Researcher, Writer, Editor are all the SAME class, configured by a
    // String injected at construction — not separate subclasses.

A worker is STATELESS across calls (like a well-behaved @Service that holds no
per-request state in fields). Everything it needs arrives as arguments.

OFFLINE MODE
------------
This file ships with `USE_MOCK = True` so it runs with NO API key. When mock is
on, `WorkerAgent` uses `FakeChatModel` — a deterministic stand-in that returns
canned, traceable text instead of calling the network. Flip the flag (and set
ANTHROPIC_API_KEY) to use the real model. See `_build_llm()` below.

Run:
    python 01_worker_agent.py
==================================================================
"""

from __future__ import annotations

import logging
from typing import Protocol

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

# ─────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────
# Set to False (and export ANTHROPIC_API_KEY) to call the real model.
USE_MOCK: bool = True

# Model id used ONLY when USE_MOCK is False.
REAL_MODEL_ID: str = "claude-sonnet-4-6"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("worker")


# ─────────────────────────────────────────────────────────────────
# A tiny structural type for "anything with .invoke(messages) -> obj.content"
# ─────────────────────────────────────────────────────────────────
class ChatLike(Protocol):
    """Structural type: both ChatAnthropic and FakeChatModel satisfy this.

    Java analogy: this is the `interface` both the real and the test-double
    implementations conform to, so the WorkerAgent never knows which it holds.
    """

    def invoke(self, messages: list[BaseMessage]) -> "AIResponseLike": ...


class AIResponseLike(Protocol):
    content: str


# ─────────────────────────────────────────────────────────────────
# Deterministic offline stand-in for ChatAnthropic
# ─────────────────────────────────────────────────────────────────
class _FakeResponse:
    """Mimics the `.content` attribute of a real LangChain AIMessage."""

    def __init__(self, content: str) -> None:
        self.content = content


class FakeChatModel:
    """Deterministic fake chat model for OFFLINE worker demos.

    It inspects the SystemMessage (the worker's specialty) and the HumanMessage
    task, then returns canned, *traceable* text. No randomness, no network — so
    the same input always yields the same output (great for tests, like a
    Mockito stub returning a fixed value).
    """

    def __init__(self, role_hint: str = "generic") -> None:
        self.role_hint = role_hint.lower()

    def invoke(self, messages: list[BaseMessage]) -> _FakeResponse:
        system = next(
            (m.content for m in messages if isinstance(m, SystemMessage)), ""
        )
        humans = [m.content for m in messages if isinstance(m, HumanMessage)]
        task = humans[-1] if humans else ""
        context = humans[0] if len(humans) > 1 else ""

        # Detect role from the injected specialty first (role_hint), then fall
        # back to scanning the system prompt. IMPORTANT: check "edit"/"writ"
        # BEFORE "research", because the Writer/Editor prompts mention the word
        # "research" incidentally ("...based on provided research.") and we must
        # not let that misroute them to the research branch.
        sys_l = system.lower()
        if "research" in self.role_hint:
            role = "research"
        elif "writ" in self.role_hint:
            role = "writing"
        elif "edit" in self.role_hint:
            role = "editing"
        elif "edit" in sys_l:
            role = "editing"
        elif "writ" in sys_l:
            role = "writing"
        elif "research" in sys_l:
            role = "research"
        else:
            role = self.role_hint

        # Canned, role-specific output that echoes whether context was received,
        # so you can SEE dependency data flowing along the graph edges.
        had_ctx = "yes" if context.strip() else "no"
        snippet = task.replace("Task:\n", "").strip()[:60]

        if role == "research":
            return _FakeResponse(
                "RESEARCH NOTES:\n"
                "- RAG grounds LLM answers in retrieved enterprise documents.\n"
                "- Cuts hallucination by citing source passages.\n"
                "- Keeps proprietary data out of model weights (governance win).\n"
                f"(mock research for: {snippet!r}; received_context={had_ctx})"
            )
        if role == "writing":
            return _FakeResponse(
                "DRAFT POST:\n"
                "Retrieval-Augmented Generation lets enterprises ground AI in "
                "their own documents, slashing hallucination and respecting data "
                "governance — without retraining a model.\n"
                f"(mock draft for: {snippet!r}; received_context={had_ctx})"
            )
        if role == "editing":
            return _FakeResponse(
                "EDITED POST:\n"
                "Retrieval-Augmented Generation (RAG) grounds enterprise AI in "
                "your own documents — reducing hallucination and honoring data "
                "governance, no retraining required.\n"
                f"(mock edit for: {snippet!r}; received_context={had_ctx})"
            )
        return _FakeResponse(
            f"GENERIC OUTPUT for {snippet!r} (received_context={had_ctx})"
        )


def _build_llm(role_hint: str) -> ChatLike:
    """Factory: returns the fake model offline, the real model otherwise.

    To use the REAL model, set USE_MOCK = False and ensure ANTHROPIC_API_KEY is
    exported. The import is done lazily so this file runs with NO dependency on
    langchain-anthropic when in mock mode.
    """
    if USE_MOCK:
        logger.info("USE_MOCK=True -> FakeChatModel(role_hint=%s)", role_hint)
        return FakeChatModel(role_hint=role_hint)

    # ── Real model path (requires `pip install langchain-anthropic`) ──
    from langchain_anthropic import ChatAnthropic  # noqa: PLC0415

    logger.info("USE_MOCK=False -> ChatAnthropic(model=%s)", REAL_MODEL_ID)
    return ChatAnthropic(model=REAL_MODEL_ID)  # type: ignore[return-value]


# ─────────────────────────────────────────────────────────────────
# WorkerAgent — the specialist
# ─────────────────────────────────────────────────────────────────
class WorkerAgent:
    """A single-specialty agent. Behaviour is injected via `instructions`.

    Java analogy: a concrete strategy. Same `run(...)` signature for every
    worker; the constructor argument (`instructions`) is what specializes it.
    """

    def __init__(self, name: str, specialty: str, instructions: str = "") -> None:
        self.name: str = name
        self.specialty: str = specialty
        # If no explicit instructions are injected, derive a default system
        # prompt from the specialty (sensible default, like a @Value fallback).
        self.instructions: str = instructions or f"You are a {specialty} specialist."
        # Each worker owns its own model handle (real or fake).
        self.llm: ChatLike = _build_llm(role_hint=specialty)

    def run(self, task: str, context: str = "") -> str:
        """Execute one subtask. Stateless: all inputs are arguments.

        `context` carries the outputs of the steps this worker depends on —
        this is how data flows along the edges of the dependency graph.
        """
        messages: list[BaseMessage] = [SystemMessage(content=self.instructions)]
        if context:
            messages.append(HumanMessage(content=f"Context:\n{context}"))
        messages.append(HumanMessage(content=f"Task:\n{task}"))

        try:
            response = self.llm.invoke(messages)
            logger.info("[%s] completed task", self.name)
            return response.content
        except Exception as exc:  # noqa: BLE001 — surface, don't swallow silently
            # In a real Saga you'd retry/timeout here (see exercises 3). For the
            # demo we degrade gracefully so one bad worker can't kill the run.
            logger.error("[%s] failed: %s", self.name, exc)
            return f"Error: worker '{self.name}' failed: {exc}"


def build_default_workers() -> list[WorkerAgent]:
    """The three-worker blog crew. Reused by 02_orchestrator_agent.py."""
    return [
        WorkerAgent(
            "Researcher",
            "research",
            "Find facts and data. Be specific and cite sources.",
        ),
        WorkerAgent(
            "Writer",
            "writing",
            "Write clear, engaging content based on provided research.",
        ),
        WorkerAgent(
            "Editor",
            "editing",
            "Review content for clarity, grammar, and logical flow.",
        ),
    ]


# ─────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────
def _demo() -> None:
    print("=" * 64)
    print(f"WorkerAgent demo  (USE_MOCK={USE_MOCK})")
    print("=" * 64)

    researcher, writer, _editor = build_default_workers()

    # 1) Researcher with no upstream context.
    notes = researcher.run("Find 3 enterprise benefits of RAG.")
    print(f"\n--- Researcher output ---\n{notes}")

    # 2) Writer that RECEIVES the researcher's notes as context — proving the
    #    dependency hand-off works at the worker level (before any orchestrator).
    draft = writer.run(
        "Write a 2-sentence intro about RAG benefits.",
        context=notes,
    )
    print(f"\n--- Writer output (note received_context=yes) ---\n{draft}")


if __name__ == "__main__":
    _demo()
