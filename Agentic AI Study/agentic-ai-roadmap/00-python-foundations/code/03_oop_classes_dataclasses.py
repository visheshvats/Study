"""03_oop_classes_dataclasses.py — dataclasses, Pydantic models, ABCs, inheritance.

Three ways to model data/behavior, each with a Java analogy:
  * @dataclass        ~ Java `record` / Lombok @Data — plain data holder.
  * Pydantic BaseModel ~ a DTO with Bean Validation (@Valid / @Min / @Max) baked in.
  * ABC + @abstractmethod ~ a Java `interface` / abstract class with abstract methods.

Run it:  python 03_oop_classes_dataclasses.py
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# @dataclass  ~  Java record / Lombok @Data
# Auto-generates __init__, __repr__, __eq__ — like a record's constructor,
# toString, and equals/hashCode.
# ---------------------------------------------------------------------------
@dataclass
class ChatMessage:
    role: str
    content: str
    tokens: int = 0
    # CRITICAL: a mutable default (dict/list) must use field(default_factory=...).
    # Writing `metadata: dict = {}` would share ONE dict across all instances —
    # the same footgun as a mutable default argument. default_factory makes a
    # fresh dict per instance, like initializing a field in a Java constructor.
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Pydantic BaseModel  ~  validated DTO (used everywhere in LangChain/FastAPI)
# Field(ge=..., le=...) is declarative validation, like @Min/@Max + @Valid.
# Validation runs automatically on construction — invalid data raises.
# ---------------------------------------------------------------------------
class LLMRequest(BaseModel):
    model: str = "claude-sonnet-4-6"
    max_tokens: int = Field(default=1024, ge=1, le=4096)          # @Min(1) @Max(4096)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)        # range-checked
    messages: list[dict] = Field(default_factory=list)            # avoid mutable default
    system: str | None = None


# ---------------------------------------------------------------------------
# Abstract base class  ~  Java interface / abstract class
# `@abstractmethod` forces subclasses to implement `run` — instantiating
# BaseAgent directly raises TypeError, exactly like `new SomeInterface()`.
# ---------------------------------------------------------------------------
class BaseAgent(ABC):
    def __init__(self, name: str, model: str = "claude-sonnet-4-6") -> None:
        self.name = name
        self.model = model

    @abstractmethod
    def run(self, query: str) -> str:
        """Subclasses MUST implement this (abstract method)."""
        ...

    def __repr__(self) -> str:  # like overriding toString()
        return f"{self.__class__.__name__}(name={self.name})"


# ---------------------------------------------------------------------------
# Inheritance  ~  `extends`. super().__init__(...) == super(...) in the ctor.
# ---------------------------------------------------------------------------
class ResearchAgent(BaseAgent):
    def __init__(self, name: str, sources: list[str] | None = None) -> None:
        super().__init__(name)
        # `sources or []` guards against the mutable-default None pattern.
        self.sources = sources or []

    def run(self, query: str) -> str:
        return f"[{self.name}] Researching '{query}' from {self.sources}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # --- dataclass ---
    msg = ChatMessage(role="user", content="Hello!")
    logger.info("ChatMessage -> role=%s repr=%s", msg.role, msg)

    # --- Pydantic: valid construction ---
    req = LLMRequest(messages=[{"role": "user", "content": "Hello"}], temperature=0.5)
    logger.info("LLMRequest.model_dump() -> %s", req.model_dump())
    logger.info("LLMRequest.model_dump_json() -> %s", req.model_dump_json())

    # --- Pydantic: validation actually fires (temperature out of range) ---
    try:
        LLMRequest(temperature=5.0)  # > 1.0 -> ValidationError
    except ValidationError as e:
        logger.info("Validation correctly rejected temperature=5.0: %s", e.errors()[0]["msg"])

    # --- ABC cannot be instantiated directly ---
    try:
        BaseAgent("nope")  # type: ignore[abstract]
    except TypeError as e:
        logger.info("BaseAgent is abstract, as expected: %s", e)

    # --- Inheritance + polymorphism ---
    agent = ResearchAgent("WebBot", sources=["google", "bing"])
    logger.info("ResearchAgent.run -> %s", agent.run("What is RAG?"))
    logger.info("OOP demo complete.")
