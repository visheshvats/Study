from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from typing import List, Optional
from abc import ABC, abstractmethod

# --- @dataclass — like Java record / Lombok @Data ---
@dataclass
class ChatMessage:
    role: str
    content: str
    tokens: int = 0
    # CRITICAL: Use default_factory for mutable objects like dicts or lists!
    # If you did `metadata: dict = {}`, every instance would share the SAME dict.
    metadata: dict = field(default_factory=dict)   

# --- Pydantic BaseModel — validated DTO, used everywhere in LangChain ---
# Think of this as Java's @Valid POJOs with Jackson annotations combined.
class LLMRequest(BaseModel):
    model: str = "claude-sonnet-4-6"
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    messages: List[dict] = []
    system: Optional[str] = None

# --- Abstract base class (Java Interface / Abstract Class equivalent) ---
class BaseAgent(ABC):
    def __init__(self, name: str, model: str = "claude-sonnet-4-6"):
        self.name = name
        self.model = model

    @abstractmethod
    def run(self, query: str) -> str:
        """Must be implemented by subclasses"""
        pass

    def __repr__(self):
        # Like Java's toString()
        return f"{self.__class__.__name__}(name={self.name})"

# --- Inheritance ---
class ResearchAgent(BaseAgent):
    def __init__(self, name: str, sources: List[str] = None):
        super().__init__(name)
        self.sources = sources or [] # Pythonic way to handle None for mutable lists

    def run(self, query: str) -> str:
        return f"[{self.name}] Researching '{query}' from {self.sources}"

if __name__ == "__main__":
    print("--- Dataclass ---")
    msg = ChatMessage(role="user", content="Hello!")
    print(f"Role: {msg.role}, Tokens: {msg.tokens}, Meta: {msg.metadata}")
    
    print("\n--- Pydantic BaseModel ---")
    try:
        req = LLMRequest(
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.5,
            # If we pass temperature=2.0, it will throw a ValidationError (le=1.0)
        )
        print("Dict dump:", req.model_dump())
        print("JSON dump:", req.model_dump_json(indent=2))
    except Exception as e:
        print(f"Validation Error: {e}")
        
    print("\n--- OOP & Inheritance ---")
    agent = ResearchAgent("WebBot", sources=["google", "bing"])
    print(agent) # Calls __repr__
    print(agent.run("What is RAG?"))
