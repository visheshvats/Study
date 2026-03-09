"""
MODULE 7 — Example 2: Persistent Memory with SQLite
=====================================================
Memory that survives restarts using SQLite.

Every conversation is saved. Facts about the user are
extracted and stored separately. On restart, the agent
remembers who you are.

SETUP:
  pip install openai python-dotenv

RUN:
  python 02_persistent_memory.py

  # Run once → tell it your name and preferences
  # Run again → it remembers you!

NO EXTRA DEPENDENCIES — SQLite is built into Python.
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"
DB_PATH = os.path.join(os.path.dirname(__file__), "agent_memory.db")


# ══════════════════════════════════════════════════════
# PERSISTENT MEMORY STORE (SQLite)
# ══════════════════════════════════════════════════════

class PersistentMemory:
    """
    SQLite-backed memory with:
    - Conversation history (all messages, all sessions)
    - User profile (extracted facts/preferences)
    - Session tracking
    
    Java Analogy: JPA + H2/SQLite embedded DB.
    Like Spring Data repositories for chat history.
    """

    def __init__(self, user_id: str = "default", db_path: str = DB_PATH):
        self.user_id = user_id
        self.db_path = db_path
        self.session_id = hashlib.md5(f"{user_id}-{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    fact_key TEXT NOT NULL,
                    fact_value TEXT NOT NULL,
                    source TEXT DEFAULT 'conversation',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, fact_key)
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    summary TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS idx_messages_user 
                ON messages(user_id, created_at DESC);
                
                CREATE INDEX IF NOT EXISTS idx_profile_user 
                ON user_profile(user_id);
            """)
            # Register this session
            conn.execute(
                "INSERT OR IGNORE INTO sessions (session_id, user_id) VALUES (?, ?)",
                (self.session_id, self.user_id)
            )

    def save_message(self, role: str, content: str):
        """Save a message to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (user_id, session_id, role, content) VALUES (?, ?, ?, ?)",
                (self.user_id, self.session_id, role, content)
            )
            conn.execute(
                "UPDATE sessions SET message_count = message_count + 1 WHERE session_id = ?",
                (self.session_id,)
            )

    def get_recent_messages(self, limit: int = 20) -> list:
        """Get the most recent messages from current session."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE user_id = ? AND session_id = ? ORDER BY created_at ASC LIMIT ?",
                (self.user_id, self.session_id, limit)
            ).fetchall()
        return [{"role": r[0], "content": r[1]} for r in rows]

    def get_past_session_summaries(self, limit: int = 3) -> list:
        """Get summaries of past sessions (not current)."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT session_id, summary, started_at, message_count FROM sessions "
                "WHERE user_id = ? AND session_id != ? AND summary IS NOT NULL "
                "ORDER BY started_at DESC LIMIT ?",
                (self.user_id, self.session_id, limit)
            ).fetchall()
        return [{"session_id": r[0], "summary": r[1], "date": r[2], "messages": r[3]} for r in rows]

    def save_user_fact(self, key: str, value: str):
        """Save or update a fact in the user profile."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO user_profile (user_id, fact_key, fact_value) VALUES (?, ?, ?)",
                (self.user_id, key, value)
            )

    def get_user_profile(self) -> dict:
        """Get all known facts about the user."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT fact_key, fact_value FROM user_profile WHERE user_id = ?",
                (self.user_id,)
            ).fetchall()
        return {r[0]: r[1] for r in rows}

    def save_session_summary(self, summary: str):
        """Save a summary for the current session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE sessions SET summary = ? WHERE session_id = ?",
                (summary, self.session_id)
            )

    def get_session_count(self) -> int:
        """How many sessions has this user had?"""
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM sessions WHERE user_id = ?",
                (self.user_id,)
            ).fetchone()[0]
        return count

    def get_total_messages(self) -> int:
        """Total messages across all sessions."""
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE user_id = ?",
                (self.user_id,)
            ).fetchone()[0]
        return count


# ══════════════════════════════════════════════════════
# FACT EXTRACTOR (LLM extracts key facts from messages)
# ══════════════════════════════════════════════════════

def extract_facts(user_message: str, assistant_reply: str) -> list[dict]:
    """
    Use LLM to extract key facts from message exchange.
    Returns list of {key, value} dicts for the user profile.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "Extract key facts about the user from this message exchange. "
                "Return JSON: {\"facts\": [{\"key\": \"name\", \"value\": \"Alice\"}, ...]} "
                "Only extract explicit statements. Valid keys: name, role, company, "
                "location, tech_stack, preferences, experience, timezone, team_size, "
                "current_project. Return empty list if no facts found."
            )},
            {"role": "user", "content": f"User said: {user_message}\nAssistant replied: {assistant_reply}"},
        ],
        temperature=0,
        response_format={"type": "json_object"},
        max_tokens=200,
    )

    result = json.loads(response.choices[0].message.content)
    return result.get("facts", [])


# ══════════════════════════════════════════════════════
# CHATBOT WITH PERSISTENT MEMORY
# ══════════════════════════════════════════════════════

class PersistentChatbot:
    """
    A chatbot that remembers across sessions using SQLite.
    
    Flow:
    1. Load user profile, past session summaries
    2. Assemble context with memory
    3. Chat normally
    4. After each exchange, extract facts → save to profile
    5. On exit, summarize session
    """

    def __init__(self, user_id: str = "default"):
        self.memory = PersistentMemory(user_id)
        self.session_messages = []

    def _build_system_prompt(self) -> str:
        """Build system prompt with memory context."""
        parts = [
            "You are a helpful personal assistant with persistent memory.",
            "You remember the user across conversations.",
        ]

        # Add user profile
        profile = self.memory.get_user_profile()
        if profile:
            profile_text = "\n".join(f"- {k}: {v}" for k, v in profile.items())
            parts.append(f"\nKNOWN FACTS ABOUT USER:\n{profile_text}")

        # Add past session summaries
        past = self.memory.get_past_session_summaries()
        if past:
            summaries = "\n".join(f"- [{s['date']}] {s['summary']}" for s in past)
            parts.append(f"\nPAST CONVERSATIONS:\n{summaries}")

        sessions = self.memory.get_session_count()
        total_msgs = self.memory.get_total_messages()
        if sessions > 1:
            parts.append(f"\n(This is session #{sessions}. {total_msgs} total messages on record.)")

        return "\n".join(parts)

    def chat(self, user_message: str) -> str:
        """Process a user message."""
        self.memory.save_message("user", user_message)
        self.session_messages.append({"role": "user", "content": user_message})

        # Build messages with full memory context
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        messages.extend(self.memory.get_recent_messages())

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=300,
        )

        reply = response.choices[0].message.content
        self.memory.save_message("assistant", reply)
        self.session_messages.append({"role": "assistant", "content": reply})

        # Extract and save facts (background, non-blocking in production)
        try:
            facts = extract_facts(user_message, reply)
            for fact in facts:
                self.memory.save_user_fact(fact["key"], fact["value"])
                print(f"    💾 Saved fact: {fact['key']} = {fact['value']}")
        except Exception:
            pass  # Don't crash if extraction fails

        return reply

    def end_session(self):
        """Summarize and save the session."""
        if len(self.session_messages) < 2:
            return

        msgs_text = "\n".join(f"{m['role']}: {m['content']}" for m in self.session_messages)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Summarize this conversation in 1-2 sentences. Include key topics discussed and any decisions made."},
                {"role": "user", "content": msgs_text},
            ],
            temperature=0,
            max_tokens=100,
        )
        summary = response.choices[0].message.content
        self.memory.save_session_summary(summary)
        print(f"\n  📝 Session summary saved: {summary}")


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  💾 Persistent Memory Agent                  ║")
    print("║  Remembers you across sessions!              ║")
    print("╚══════════════════════════════════════════════╝\n")

    bot = PersistentChatbot(user_id="demo_user")

    profile = bot.memory.get_user_profile()
    sessions = bot.memory.get_session_count()

    if profile:
        print(f"  📋 Welcome back! Session #{sessions}")
        print(f"  📋 Known profile: {json.dumps(profile, indent=2)}")
    else:
        print(f"  👋 First session! Tell me about yourself.")

    print(f"\n  💡 Commands: /profile, /stats, /quit")
    print(f"  {'─'*55}\n")

    while True:
        try:
            user_input = input("  👤 You: ").strip()
            if not user_input:
                continue

            if user_input == "/quit":
                bot.end_session()
                break
            elif user_input == "/profile":
                profile = bot.memory.get_user_profile()
                print(f"\n  📋 User Profile:")
                for k, v in profile.items():
                    print(f"    {k}: {v}")
                print()
                continue
            elif user_input == "/stats":
                print(f"\n  📊 Sessions: {bot.memory.get_session_count()}")
                print(f"  📊 Total messages: {bot.memory.get_total_messages()}")
                print(f"  📊 Profile facts: {len(bot.memory.get_user_profile())}")
                print(f"  📊 DB: {bot.memory.db_path}\n")
                continue

            reply = bot.chat(user_input)
            print(f"\n  🤖 {reply}\n")

        except (KeyboardInterrupt, EOFError):
            bot.end_session()
            break

    print("\n  👋 Goodbye! Your memory is saved.\n")
    print(f"  💡 Run this script again — I'll remember you!\n")


if __name__ == "__main__":
    main()
