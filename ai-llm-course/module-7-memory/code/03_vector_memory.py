"""
MODULE 7 — Example 3: Vector Memory (Episodic Recall)
=======================================================
Semantic search over past conversations using ChromaDB.
The agent remembers by SEARCHING, not by storing everything.

SETUP:
  pip install openai chromadb python-dotenv

RUN:
  python 03_vector_memory.py
"""

import os
import json
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# ══════════════════════════════════════════════════════
# VECTOR MEMORY STORE (ChromaDB)
# ══════════════════════════════════════════════════════

class EpisodicMemory:
    """
    Stores all interactions as embeddings in ChromaDB.
    Retrieves relevant past context via semantic search.
    
    Episodic = specific past events/conversations
    (vs Semantic = general knowledge, which is RAG from Module 3)
    
    Java Analogy: Elasticsearch for log searching.
    Instead of reading ALL logs, search for relevant entries.
    """

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.chroma = chromadb.Client()
        self.collection = self.chroma.create_collection(
            name=f"memory_{user_id}",
            metadata={"hnsw:space": "cosine"},
        )
        self.turn_counter = 0

    def store(self, role: str, content: str, metadata: dict = None):
        """Store a message as an embedding for future retrieval."""
        self.turn_counter += 1
        doc_id = hashlib.md5(f"{self.user_id}-{self.turn_counter}-{content[:50]}".encode()).hexdigest()[:16]

        meta = {
            "role": role,
            "user_id": self.user_id,
            "turn": self.turn_counter,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            meta.update(metadata)

        self.collection.add(
            documents=[f"[{role}] {content}"],
            metadatas=[meta],
            ids=[doc_id],
        )

    def recall(self, query: str, n_results: int = 5) -> list[dict]:
        """Search for relevant past messages."""
        if self.collection.count() == 0:
            return []

        n = min(n_results, self.collection.count())
        results = self.collection.query(
            query_texts=[query],
            n_results=n,
        )

        memories = []
        for i in range(len(results["documents"][0])):
            memories.append({
                "content": results["documents"][0][i],
                "turn": results["metadatas"][0][i].get("turn", 0),
                "role": results["metadatas"][0][i].get("role", "unknown"),
                "relevance": round(1 - results["distances"][0][i] / 2, 3),
            })

        return memories

    def recall_formatted(self, query: str, n_results: int = 5) -> str:
        """Get formatted memory context for injecting into prompts."""
        memories = self.recall(query, n_results)
        if not memories:
            return ""

        lines = ["RELEVANT MEMORIES FROM PAST CONVERSATIONS:"]
        for m in memories:
            lines.append(f"  [Turn {m['turn']}, relevance: {m['relevance']}] {m['content']}")
        return "\n".join(lines)

    def stats(self) -> dict:
        return {
            "total_memories": self.collection.count(),
            "turns": self.turn_counter,
        }


# ══════════════════════════════════════════════════════
# CHATBOT WITH EPISODIC MEMORY
# ══════════════════════════════════════════════════════

class EpisodicChatbot:
    """
    Chatbot that uses vector search to recall relevant
    past interactions. Scales to thousands of messages.
    """

    SYSTEM_PROMPT = (
        "You are a helpful assistant with episodic memory. "
        "You can recall relevant parts of past conversations using your memory. "
        "When memory context is provided, use it to give personalized, contextual answers. "
        "If you're not sure about something from memory, say so."
    )

    def __init__(self, user_id: str = "default"):
        self.memory = EpisodicMemory(user_id)
        self.recent_messages = []  # Last few messages for immediate context
        self.max_recent = 6        # Keep last 3 exchanges in buffer

    def chat(self, user_message: str) -> str:
        """Process a message with episodic memory recall."""

        # Step 1: Recall relevant memories
        memory_context = self.memory.recall_formatted(user_message, n_results=3)

        # Step 2: Build messages
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        if memory_context:
            messages.append({"role": "system", "content": memory_context})
        messages.extend(self.recent_messages)
        messages.append({"role": "user", "content": user_message})

        # Step 3: Get response
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=300,
        )
        reply = response.choices[0].message.content

        # Step 4: Store in memory
        self.memory.store("user", user_message)
        self.memory.store("assistant", reply)

        # Step 5: Update recent buffer
        self.recent_messages.append({"role": "user", "content": user_message})
        self.recent_messages.append({"role": "assistant", "content": reply})
        if len(self.recent_messages) > self.max_recent:
            self.recent_messages = self.recent_messages[-self.max_recent:]

        return reply


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🧠 Vector Memory — Episodic Recall          ║")
    print("║  ChromaDB semantic search over past messages  ║")
    print("╚══════════════════════════════════════════════╝\n")

    bot = EpisodicChatbot(user_id="demo")

    # Phase 1: Seed memories
    print("  ▶ Phase 1: Building memories...\n")

    seed_messages = [
        "My name is Alice and I work at TechCorp as a senior Java developer.",
        "We're building a microservices platform using Spring Boot 3 and Kafka.",
        "Our team uses PostgreSQL for the main database and Redis for caching.",
        "I'm in the Tokyo timezone and prefer working from 9 AM to 6 PM.",
        "My biggest challenge right now is migrating our monolith to microservices.",
        "I prefer concise, bullet-point answers with code examples.",
        "We deploy to AWS EKS with ArgoCD for GitOps.",
        "Our CI/CD pipeline uses GitHub Actions with SonarQube for code quality.",
    ]

    for msg in seed_messages:
        reply = bot.chat(msg)
        print(f"    👤 {msg[:60]}...")
        print(f"    🤖 {reply[:60]}...\n")

    print(f"  📊 Memories stored: {bot.memory.stats()['total_memories']}")

    # Phase 2: Test recall
    print(f"\n  {'═'*55}")
    print(f"  ▶ Phase 2: Testing recall...")
    print(f"  {'═'*55}\n")

    recall_tests = [
        "What database do we use?",
        "What's my name and where do I work?",
        "How do we deploy our services?",
        "What code quality tools do we use?",
    ]

    for test in recall_tests:
        print(f"  👤 {test}")

        # Show what was recalled
        memories = bot.memory.recall(test, n_results=2)
        for m in memories:
            print(f"    🔍 Recalled (rel: {m['relevance']}): {m['content'][:70]}...")

        reply = bot.chat(test)
        print(f"  🤖 {reply[:150]}")
        print()

    # Summary
    print(f"  {'═'*55}")
    print(f"  ✅ Vector Memory advantages:")
    print(f"     • Retrieves RELEVANT memories, not all of them")
    print(f"     • Scales to thousands of messages")
    print(f"     • Semantic search finds related context")
    print(f"     • Cost per query is constant (not growing)\n")


if __name__ == "__main__":
    main()
