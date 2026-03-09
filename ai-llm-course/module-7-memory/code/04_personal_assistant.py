"""
MODULE 7 — PROJECT: Personal Assistant with Full Memory System
================================================================
A production-style personal assistant combining ALL memory types:
  - Short-term: Conversation buffer (recent messages)
  - Long-term: User profile (extracted facts in SQLite)
  - Episodic: Past conversation recall (ChromaDB vectors)
  - Summary: Conversation compression (LLM-generated)

This is the HYBRID MEMORY approach recommended for production.

SETUP:
  pip install openai chromadb python-dotenv

RUN:
  python 04_personal_assistant.py
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"
DB_PATH = os.path.join(os.path.dirname(__file__), "assistant_memory.db")


# ══════════════════════════════════════════════════════
# MEMORY LAYERS
# ══════════════════════════════════════════════════════

class ShortTermMemory:
    """Recent conversation messages (sliding window)."""

    def __init__(self, max_messages: int = 12):
        self.messages = []
        self.max_messages = max_messages

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get(self) -> list:
        return self.messages.copy()

    def count(self) -> int:
        return len(self.messages)


class LongTermMemory:
    """Structured user profile stored in SQLite."""

    def __init__(self, user_id: str, db_path: str = DB_PATH):
        self.user_id = user_id
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_facts (
                    user_id TEXT, fact_key TEXT, fact_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, fact_key)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT, session_id TEXT,
                    summary TEXT, message_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_fact(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO user_facts (user_id, fact_key, fact_value, updated_at) VALUES (?, ?, ?, ?)",
                (self.user_id, key, value, datetime.now().isoformat())
            )

    def get_profile(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT fact_key, fact_value FROM user_facts WHERE user_id = ?",
                (self.user_id,)
            ).fetchall()
        return {r[0]: r[1] for r in rows}

    def save_session_summary(self, session_id: str, summary: str, msg_count: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversation_log (user_id, session_id, summary, message_count) VALUES (?, ?, ?, ?)",
                (self.user_id, session_id, summary, msg_count)
            )

    def get_past_sessions(self, limit: int = 3) -> list:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT summary, created_at, message_count FROM conversation_log WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (self.user_id, limit)
            ).fetchall()
        return [{"summary": r[0], "date": r[1], "messages": r[2]} for r in rows]


class EpisodicMemory:
    """Vector-based memory for semantic recall over past messages."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.chroma = chromadb.Client()
        self.collection = self.chroma.create_collection(
            name=f"episodic_{user_id}",
            metadata={"hnsw:space": "cosine"},
        )
        self.counter = 0

    def store(self, role: str, content: str):
        self.counter += 1
        doc_id = hashlib.md5(f"{self.counter}-{content[:30]}".encode()).hexdigest()[:16]
        self.collection.add(
            documents=[f"[{role}] {content}"],
            metadatas=[{"role": role, "turn": self.counter, "ts": datetime.now().isoformat()}],
            ids=[doc_id],
        )

    def recall(self, query: str, n: int = 3) -> list[str]:
        if self.collection.count() < 2:
            return []
        n = min(n, self.collection.count())
        results = self.collection.query(query_texts=[query], n_results=n)
        return results["documents"][0] if results["documents"] else []

    def count(self) -> int:
        return self.collection.count()


class SummaryMemory:
    """Compressed summary of the current conversation."""

    def __init__(self):
        self.summary = ""
        self.unsummarized_count = 0

    def update(self, messages: list, threshold: int = 8):
        """Update summary if enough new messages have accumulated."""
        self.unsummarized_count += 1
        if self.unsummarized_count < threshold:
            return

        recent_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages[-threshold:])
        existing = f"Existing summary: {self.summary}\n\n" if self.summary else ""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": (
                    "Summarize this conversation concisely. Preserve all key facts: "
                    "names, preferences, decisions, technical details. 2-3 sentences max."
                )},
                {"role": "user", "content": f"{existing}New messages:\n{recent_text}"},
            ],
            temperature=0,
            max_tokens=150,
        )
        self.summary = response.choices[0].message.content
        self.unsummarized_count = 0

    def get(self) -> str:
        return self.summary


# ══════════════════════════════════════════════════════
# MEMORY MANAGER (Orchestrates all memory layers)
# ══════════════════════════════════════════════════════

class MemoryManager:
    """
    Orchestrates all 4 memory layers into a unified context.
    
    Architecture:
      ┌────────────────────────────────────────┐
      │          MEMORY MANAGER                 │
      │                                         │
      │  ┌─────────┐  ┌─────────┐             │
      │  │ Short   │  │  Long   │  SQLite     │
      │  │ Term    │  │  Term   │  (profile)  │
      │  │ (buffer)│  │(profile)│             │
      │  └─────────┘  └─────────┘             │
      │                                         │
      │  ┌─────────┐  ┌─────────┐             │
      │  │Episodic │  │ Summary │  In-memory  │
      │  │(vector) │  │(compress│  (or cache) │
      │  │ChromaDB │  │  old)   │             │
      │  └─────────┘  └─────────┘             │
      └────────────────────────────────────────┘
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.short_term = ShortTermMemory(max_messages=12)
        self.long_term = LongTermMemory(user_id)
        self.episodic = EpisodicMemory(user_id)
        self.summary = SummaryMemory()
        self.session_id = hashlib.md5(f"{user_id}-{datetime.now().isoformat()}".encode()).hexdigest()[:12]

    def add_exchange(self, user_msg: str, assistant_msg: str):
        """Store an exchange across all memory layers."""
        # Short-term: add to buffer
        self.short_term.add("user", user_msg)
        self.short_term.add("assistant", assistant_msg)

        # Episodic: embed for future semantic search
        self.episodic.store("user", user_msg)
        self.episodic.store("assistant", assistant_msg)

        # Summary: update if threshold reached
        self.summary.update(self.short_term.get())

        # Long-term: extract facts (periodically)
        if self.short_term.count() % 4 == 0:
            self._extract_facts(user_msg, assistant_msg)

    def _extract_facts(self, user_msg: str, assistant_msg: str):
        """Extract key facts about user for long-term storage."""
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": (
                        "Extract facts about the user. Return JSON: "
                        '{\"facts\": [{\"key\": \"name\", \"value\": \"Alice\"}]} '
                        "Keys: name, role, company, location, tech_stack, preferences, "
                        "current_project, timezone, team_size. Return empty list if none."
                    )},
                    {"role": "user", "content": f"User: {user_msg}\nAssistant: {assistant_msg}"},
                ],
                temperature=0,
                response_format={"type": "json_object"},
                max_tokens=150,
            )
            facts = json.loads(response.choices[0].message.content).get("facts", [])
            for f in facts:
                self.long_term.save_fact(f["key"], f["value"])
        except Exception:
            pass

    def build_context(self, current_query: str) -> list:
        """Assemble full context from all memory layers."""
        messages = []

        # System prompt
        parts = [
            "You are a personal assistant with comprehensive memory.",
            "You remember the user across conversations and provide personalized help.",
        ]

        # Long-term: User profile
        profile = self.long_term.get_profile()
        if profile:
            profile_str = "\n".join(f"  - {k}: {v}" for k, v in profile.items())
            parts.append(f"\nUSER PROFILE:\n{profile_str}")

        # Episodic: Relevant past memories
        memories = self.episodic.recall(current_query, n=3)
        if memories:
            mem_str = "\n".join(f"  - {m}" for m in memories)
            parts.append(f"\nRELEVANT PAST MEMORIES:\n{mem_str}")

        # Summary of current conversation
        summary = self.summary.get()
        if summary:
            parts.append(f"\nCONVERSATION SO FAR:\n  {summary}")

        # Past sessions
        past = self.long_term.get_past_sessions(limit=2)
        if past:
            sess_str = "\n".join(f"  - [{s['date']}] {s['summary']}" for s in past)
            parts.append(f"\nPAST SESSIONS:\n{sess_str}")

        messages.append({"role": "system", "content": "\n".join(parts)})

        # Short-term: recent messages
        messages.extend(self.short_term.get())

        return messages

    def end_session(self):
        """Save session summary for future reference."""
        messages = self.short_term.get()
        if len(messages) < 2:
            return ""
        msgs_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages[:20])
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Summarize in 1-2 sentences: topics discussed and key decisions."},
                {"role": "user", "content": msgs_text},
            ],
            temperature=0,
            max_tokens=100,
        )
        summary = response.choices[0].message.content
        self.long_term.save_session_summary(self.session_id, summary, len(messages))
        return summary

    def get_stats(self) -> dict:
        return {
            "short_term_messages": self.short_term.count(),
            "long_term_facts": len(self.long_term.get_profile()),
            "episodic_memories": self.episodic.count(),
            "has_summary": bool(self.summary.get()),
            "past_sessions": len(self.long_term.get_past_sessions()),
        }


# ══════════════════════════════════════════════════════
# PERSONAL ASSISTANT
# ══════════════════════════════════════════════════════

class PersonalAssistant:
    """Full-featured assistant with hybrid memory."""

    def __init__(self, user_id: str = "default"):
        self.memory = MemoryManager(user_id)

    def chat(self, user_message: str) -> str:
        # Build context with all memory layers
        messages = self.memory.build_context(user_message)
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=400,
        )
        reply = response.choices[0].message.content

        # Store in all memory layers
        self.memory.add_exchange(user_message, reply)

        return reply


# ══════════════════════════════════════════════════════
# INTERACTIVE MODE
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🧠 Personal Assistant — Hybrid Memory       ║")
    print("║  MODULE 7 PROJECT                            ║")
    print("║                                              ║")
    print("║  Memory layers:                              ║")
    print("║  • Short-term (conversation buffer)          ║")
    print("║  • Long-term (SQLite user profile)           ║")
    print("║  • Episodic (ChromaDB vector search)         ║")
    print("║  • Summary (LLM compression)                 ║")
    print("╚══════════════════════════════════════════════╝\n")

    assistant = PersonalAssistant(user_id="demo_user")

    profile = assistant.memory.long_term.get_profile()
    if profile:
        print(f"  📋 Welcome back! Known profile:")
        for k, v in profile.items():
            print(f"     {k}: {v}")
    else:
        print(f"  👋 First time! Tell me about yourself.")

    print(f"\n  💡 Commands: /profile, /stats, /memory <query>, /quit\n")

    while True:
        try:
            user_input = input("  👤 You: ").strip()
            if not user_input:
                continue

            if user_input == "/quit":
                summary = assistant.memory.end_session()
                if summary:
                    print(f"\n  📝 Session saved: {summary}")
                break
            elif user_input == "/profile":
                p = assistant.memory.long_term.get_profile()
                print(f"\n  📋 Profile: {json.dumps(p, indent=2) if p else 'Empty'}\n")
                continue
            elif user_input == "/stats":
                s = assistant.memory.get_stats()
                print(f"\n  📊 Memory Stats:")
                for k, v in s.items():
                    print(f"     {k}: {v}")
                print()
                continue
            elif user_input.startswith("/memory "):
                query = user_input[8:]
                memories = assistant.memory.episodic.recall(query, n=5)
                print(f"\n  🔍 Memories matching '{query}':")
                for m in memories:
                    print(f"     {m}")
                print()
                continue

            reply = assistant.chat(user_input)
            print(f"\n  🤖 {reply}\n")

        except (KeyboardInterrupt, EOFError):
            summary = assistant.memory.end_session()
            if summary:
                print(f"\n  📝 Session saved: {summary}")
            break

    print("\n  👋 Goodbye! All memories saved.\n")


if __name__ == "__main__":
    main()
