#!/usr/bin/env python3
"""
Context Manager — Sliding Conversation Window with Token Budget Tracking
==========================================================================
Manages a stateful conversation history with:
  • Fixed token budget enforcement
  • Sliding window with configurable overlap
  • Historical summary truncation (oldest messages → compressed summary)
  • Priority-based message retention (system > recent user > old assistant)
  • Token counting estimation

Run:
    python context_manager.py
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import textwrap


# ── Data Types ──────────────────────────────────────────────────────────────
class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    SUMMARY = "summary"  # Compressed historical context


@dataclass
class Message:
    role: MessageRole
    content: str
    token_count: int = 0
    turn_index: int = 0
    is_pinned: bool = False  # Pinned messages are never evicted

    def __post_init__(self):
        if self.token_count == 0:
            self.token_count = self.estimate_tokens()

    def estimate_tokens(self) -> int:
        """Rough token estimate: ~4 characters per token for English text."""
        return max(1, len(self.content) // 4)


@dataclass
class TokenBudget:
    """Token allocation across different prompt sections."""
    total: int = 4096
    system: int = 500       # Reserved for system prompt
    context: int = 1500     # Retrieved context (RAG)
    history: int = 1500     # Conversation history
    response: int = 596     # Reserved for model output

    def validate(self) -> bool:
        allocated = self.system + self.context + self.history + self.response
        return allocated <= self.total

    def available_for_history(self) -> int:
        return self.history


@dataclass
class WindowConfig:
    """Sliding window configuration."""
    max_turns: int = 10            # Maximum conversation turns to keep
    summary_threshold: int = 6     # Summarize when turns exceed this
    overlap_turns: int = 2         # Keep N recent turns during compression
    min_summary_tokens: int = 100  # Minimum tokens for a summary block


# ── Conversation Summarizer ────────────────────────────────────────────────
class ConversationSummarizer:
    """
    Compresses older conversation turns into a compact summary.
    In production, this would call an LLM. Here we use extractive summarization.
    """

    def summarize(self, messages: List[Message]) -> str:
        """Extract key information from a list of messages."""
        if not messages:
            return ""

        # Extract first sentence from each message (mock summarization)
        key_points: List[str] = []
        for msg in messages:
            first_sentence = msg.content.split(".")[0].strip()
            if len(first_sentence) > 10:
                role_label = msg.role.value.upper()
                key_points.append(f"[{role_label}] {first_sentence}.")

        # Limit summary length
        summary = " ".join(key_points[:6])
        return f"[Conversation Summary] {summary}"


# ── Context Manager ────────────────────────────────────────────────────────
class ContextManager:
    """
    Manages the full conversation context with:
      - Token budget enforcement
      - Sliding window with historical compression
      - Priority-based eviction
    """

    def __init__(
        self,
        budget: Optional[TokenBudget] = None,
        window: Optional[WindowConfig] = None,
    ):
        self.budget = budget or TokenBudget()
        self.window = window or WindowConfig()
        self.summarizer = ConversationSummarizer()

        self._messages: List[Message] = []
        self._summary: Optional[Message] = None
        self._turn_counter: int = 0
        self._total_tokens_processed: int = 0

    def set_system_prompt(self, content: str) -> None:
        """Set or replace the system prompt (always pinned)."""
        # Remove existing system messages
        self._messages = [m for m in self._messages if m.role != MessageRole.SYSTEM]
        msg = Message(role=MessageRole.SYSTEM, content=content, is_pinned=True)
        self._messages.insert(0, msg)

    def add_user_message(self, content: str) -> None:
        """Add a user message and trigger window management."""
        self._turn_counter += 1
        msg = Message(role=MessageRole.USER, content=content, turn_index=self._turn_counter)
        self._messages.append(msg)
        self._total_tokens_processed += msg.token_count
        self._manage_window()

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant response."""
        msg = Message(role=MessageRole.ASSISTANT, content=content, turn_index=self._turn_counter)
        self._messages.append(msg)
        self._total_tokens_processed += msg.token_count
        self._manage_window()

    def get_context_window(self) -> List[Dict[str, str]]:
        """
        Build the final context window for the LLM, respecting token budget.
        Returns messages in the format expected by chat completion APIs.
        """
        result: List[Dict[str, str]] = []

        # 1. System prompt (always first)
        for msg in self._messages:
            if msg.role == MessageRole.SYSTEM:
                result.append({"role": "system", "content": msg.content})

        # 2. Historical summary (if exists)
        if self._summary:
            result.append({"role": "system", "content": self._summary.content})

        # 3. Recent conversation turns (within budget)
        history_budget = self.budget.available_for_history()
        if self._summary:
            history_budget -= self._summary.token_count

        history_messages = [
            m for m in self._messages
            if m.role in (MessageRole.USER, MessageRole.ASSISTANT)
        ]

        # Take messages from the end (most recent first) within budget
        selected: List[Message] = []
        tokens_used = 0
        for msg in reversed(history_messages):
            if tokens_used + msg.token_count > history_budget:
                break
            selected.insert(0, msg)
            tokens_used += msg.token_count

        for msg in selected:
            result.append({"role": msg.role.value, "content": msg.content})

        return result

    def _manage_window(self) -> None:
        """Apply sliding window with summarization when history exceeds threshold."""
        conversation_msgs = [
            m for m in self._messages
            if m.role in (MessageRole.USER, MessageRole.ASSISTANT)
        ]

        turn_count = len([m for m in conversation_msgs if m.role == MessageRole.USER])

        if turn_count > self.window.summary_threshold:
            self._compress_history()

    def _compress_history(self) -> None:
        """Compress oldest messages into a summary, keep recent turns."""
        conversation_msgs = [
            m for m in self._messages
            if m.role in (MessageRole.USER, MessageRole.ASSISTANT)
        ]

        # Split into old (to summarize) and recent (to keep)
        keep_count = self.window.overlap_turns * 2  # user + assistant per turn
        old_msgs = conversation_msgs[:-keep_count] if keep_count < len(conversation_msgs) else []
        recent_msgs = conversation_msgs[-keep_count:] if keep_count < len(conversation_msgs) else conversation_msgs

        if not old_msgs:
            return

        # Generate summary
        summary_text = self.summarizer.summarize(old_msgs)
        if self._summary:
            # Append to existing summary
            summary_text = f"{self._summary.content}\n{summary_text}"

        self._summary = Message(
            role=MessageRole.SUMMARY,
            content=summary_text,
            is_pinned=True,
        )

        # Rebuild message list: system + recent only
        system_msgs = [m for m in self._messages if m.role == MessageRole.SYSTEM]
        self._messages = system_msgs + recent_msgs

    def stats(self) -> Dict[str, int]:
        """Return context manager statistics."""
        conversation_msgs = [
            m for m in self._messages
            if m.role in (MessageRole.USER, MessageRole.ASSISTANT)
        ]
        return {
            "total_messages": len(self._messages),
            "conversation_turns": len([m for m in conversation_msgs if m.role == MessageRole.USER]),
            "current_token_usage": sum(m.token_count for m in self._messages) + (
                self._summary.token_count if self._summary else 0
            ),
            "history_budget": self.budget.available_for_history(),
            "summary_tokens": self._summary.token_count if self._summary else 0,
            "total_tokens_processed": self._total_tokens_processed,
            "compressions": 1 if self._summary else 0,
        }


# ── Demo ────────────────────────────────────────────────────────────────────
def run_demo() -> None:
    print("=" * 72)
    print("CONTEXT MANAGER — Sliding Window + Token Budget Demo")
    print("=" * 72)

    # Create manager with tight budget for demonstration
    budget = TokenBudget(total=2048, system=200, context=500, history=800, response=548)
    window = WindowConfig(max_turns=10, summary_threshold=4, overlap_turns=2)

    ctx = ContextManager(budget=budget, window=window)

    # Set system prompt
    ctx.set_system_prompt(
        "You are a helpful financial advisor. Provide accurate, personalized "
        "advice based on the user's portfolio and risk tolerance."
    )

    # Simulate a multi-turn conversation
    conversation = [
        ("I'm 30 years old and want to start investing. I have $50k saved.",
         "Great starting point! At 30, you have a long investment horizon. I'd recommend "
         "a diversified portfolio: 70% equities (index funds), 20% bonds, 10% alternatives."),

        ("What index funds would you recommend specifically?",
         "For a core holding, consider: VTI (Total US Market), VXUS (International), "
         "and BND (Total Bond Market). These three cover global diversification at minimal cost."),

        ("What about individual stocks? I'm interested in tech.",
         "Individual stocks add concentration risk. If you allocate, limit to 5-10% of your "
         "portfolio. For tech exposure, consider QQQ (Nasdaq-100) as a diversified alternative."),

        ("How much should I keep in an emergency fund?",
         "Standard guidance: 3-6 months of essential expenses in a high-yield savings account. "
         "At your income level, aim for $15-20k liquid before aggressive investing."),

        ("Should I max out my 401k before investing in a brokerage?",
         "Absolutely prioritize tax-advantaged accounts: 1) 401k match (free money), "
         "2) Roth IRA ($7,000/year), 3) Remaining 401k up to limit, 4) Taxable brokerage."),

        ("What about crypto? Is it a good investment?",
         "Crypto is highly speculative. If interested, limit to 1-3% of total portfolio. "
         "Bitcoin and Ethereum have the strongest network effects. Never invest more than "
         "you can afford to lose completely."),

        ("Thanks! Can you summarize our entire conversation?",
         "We covered: starting portfolio allocation (70/30/10), core index funds (VTI, VXUS, BND), "
         "individual stock limits (5-10%), emergency fund sizing ($15-20k), tax-advantaged account "
         "priority order, and crypto allocation limits (1-3%)."),
    ]

    for i, (user_msg, assistant_msg) in enumerate(conversation):
        print(f"\n{'─' * 60}")
        print(f"  TURN {i + 1}")
        print(f"{'─' * 60}")
        print(f"  USER: {user_msg[:70]}...")
        ctx.add_user_message(user_msg)
        ctx.add_assistant_message(assistant_msg)

        stats = ctx.stats()
        print(f"  STATS: {stats['conversation_turns']} turns | "
              f"{stats['current_token_usage']}/{stats['history_budget']} tokens | "
              f"summary={stats['summary_tokens']} tokens | "
              f"compressions={stats['compressions']}")

    # Show final context window
    print(f"\n{'═' * 72}")
    print("  FINAL CONTEXT WINDOW (sent to LLM):")
    print(f"{'═' * 72}")
    window = ctx.get_context_window()
    for msg in window:
        role = msg["role"].upper()
        content = msg["content"][:100]
        print(f"\n  [{role}]")
        print(textwrap.indent(textwrap.fill(content, 65), "    "))
        if len(msg["content"]) > 100:
            print(f"    ... ({len(msg['content'])} chars total)")

    # Final statistics
    print(f"\n{'─' * 60}")
    print(f"  FINAL STATISTICS: {ctx.stats()}")
    print(f"{'─' * 60}")


if __name__ == "__main__":
    run_demo()
