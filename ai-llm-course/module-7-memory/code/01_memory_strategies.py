"""
MODULE 7 — Example 1: Memory Strategies Compared
===================================================
Side-by-side comparison of 4 memory strategies:
  1. Buffer (keep all)
  2. Window (keep last N)
  3. Summary (compress old into summary)
  4. Vector (semantic search over past messages)

SETUP:
  pip install openai python-dotenv tiktoken

RUN:
  python 01_memory_strategies.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"
encoder = tiktoken.encoding_for_model(MODEL)


def count_tokens(messages: list) -> int:
    """Count tokens in message list."""
    return sum(len(encoder.encode(m.get("content", ""))) for m in messages)


# ══════════════════════════════════════════════════════
# STRATEGY 1: Buffer Memory (Keep Everything)
# ══════════════════════════════════════════════════════

class BufferMemory:
    """
    Stores ALL messages. Perfect recall but grows unbounded.
    
    Java Analogy: ArrayList<Message> — just .add() everything.
    Works until you run out of memory (context window).
    """

    def __init__(self):
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant. Remember everything the user tells you."}
        ]

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_messages(self) -> list:
        return self.messages.copy()

    def stats(self) -> str:
        return f"Buffer: {len(self.messages)} messages, {count_tokens(self.messages)} tokens"


# ══════════════════════════════════════════════════════
# STRATEGY 2: Window Memory (Keep Last N)
# ══════════════════════════════════════════════════════

class WindowMemory:
    """
    Keeps only the last N message pairs (user + assistant).
    Fixed cost but forgets older context.
    
    Java Analogy: CircularFifoQueue — fixed capacity,
    oldest items are dropped automatically.
    """

    def __init__(self, window_size: int = 5):
        self.system_msg = {"role": "system", "content": "You are a helpful assistant. Remember everything the user tells you."}
        self.messages = []
        self.window_size = window_size  # Number of user+assistant pairs to keep

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # Trim to keep only last N*2 messages (pairs of user + assistant)
        max_msgs = self.window_size * 2
        if len(self.messages) > max_msgs:
            self.messages = self.messages[-max_msgs:]

    def get_messages(self) -> list:
        return [self.system_msg] + self.messages

    def stats(self) -> str:
        return f"Window(last {self.window_size}): {len(self.messages)} messages, {count_tokens(self.get_messages())} tokens"


# ══════════════════════════════════════════════════════
# STRATEGY 3: Summary Memory (Compress Old Messages)
# ══════════════════════════════════════════════════════

class SummaryMemory:
    """
    Summarizes old messages, keeps summary + recent messages.
    Best balance of recall and cost.
    
    Java Analogy: Log rotation — old logs are compressed,
    recent logs stay as-is.
    """

    def __init__(self, summarize_threshold: int = 6):
        self.system_msg = {"role": "system", "content": "You are a helpful assistant. Remember everything the user tells you."}
        self.summary = ""
        self.messages = []
        self.summarize_threshold = summarize_threshold

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

        # When messages exceed threshold, summarize older ones
        if len(self.messages) >= self.summarize_threshold:
            self._summarize()

    def _summarize(self):
        """Compress older messages into a summary."""
        # Take older half of messages to summarize
        split = len(self.messages) // 2
        old_messages = self.messages[:split]
        self.messages = self.messages[split:]

        old_text = "\n".join(f"{m['role']}: {m['content']}" for m in old_messages)
        existing = f"Previous summary: {self.summary}\n\n" if self.summary else ""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": (
                    "Summarize this conversation into a concise paragraph. "
                    "Preserve ALL key facts: names, preferences, decisions, "
                    "important details. Be brief but complete."
                )},
                {"role": "user", "content": f"{existing}New messages to include:\n{old_text}"},
            ],
            temperature=0,
            max_tokens=200,
        )
        self.summary = response.choices[0].message.content

    def get_messages(self) -> list:
        msgs = [self.system_msg]
        if self.summary:
            msgs.append({"role": "system", "content": f"CONVERSATION SUMMARY:\n{self.summary}"})
        msgs.extend(self.messages)
        return msgs

    def stats(self) -> str:
        summary_info = f", summary: {len(self.summary.split())} words" if self.summary else ""
        return f"Summary: {len(self.messages)} recent messages{summary_info}, {count_tokens(self.get_messages())} tokens"


# ══════════════════════════════════════════════════════
# STRATEGY 4: Vector Memory (Semantic Search)
# ══════════════════════════════════════════════════════

class VectorMemory:
    """
    Embeds all messages, retrieves relevant ones via similarity search.
    Scales to infinite history.
    
    Java Analogy: Elasticsearch — search relevant log entries
    instead of reading all logs.
    """

    def __init__(self, top_k: int = 3):
        self.system_msg = {"role": "system", "content": "You are a helpful assistant. Remember everything the user tells you."}
        self.all_messages = []   # Full history for embedding
        self.recent = []         # Last 2 messages for immediate context
        self.top_k = top_k
        self._embeddings_cache = {}

    def _embed(self, text: str) -> list:
        """Get embedding for a text string."""
        if text in self._embeddings_cache:
            return self._embeddings_cache[text]
        response = client.embeddings.create(model="text-embedding-3-small", input=text)
        embedding = response.data[0].embedding
        self._embeddings_cache[text] = embedding
        return embedding

    def _cosine_similarity(self, a: list, b: list) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a * norm_b > 0 else 0

    def add(self, role: str, content: str):
        entry = {"role": role, "content": content}
        self.all_messages.append(entry)
        self.recent.append(entry)
        if len(self.recent) > 4:
            self.recent = self.recent[-4:]  # Keep last 2 exchanges

    def _retrieve_relevant(self, query: str) -> list:
        """Find the most relevant past messages for this query."""
        if not self.all_messages:
            return []

        query_emb = self._embed(query)
        scored = []
        for msg in self.all_messages[:-2]:  # Exclude very recent
            sim = self._cosine_similarity(query_emb, self._embed(msg["content"]))
            scored.append((sim, msg))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [msg for _, msg in scored[:self.top_k]]

    def get_messages(self, current_query: str = "") -> list:
        msgs = [self.system_msg]

        if current_query and len(self.all_messages) > 4:
            relevant = self._retrieve_relevant(current_query)
            if relevant:
                context = "\n".join(f"- [{m['role']}] {m['content']}" for m in relevant)
                msgs.append({"role": "system", "content": f"RELEVANT PAST CONTEXT:\n{context}"})

        msgs.extend(self.recent)
        return msgs

    def stats(self) -> str:
        return f"Vector: {len(self.all_messages)} stored, {len(self.recent)} recent, {len(self._embeddings_cache)} embeddings"


# ══════════════════════════════════════════════════════
# COMPARISON DEMO
# ══════════════════════════════════════════════════════

def chat_with(memory, user_msg: str) -> str:
    """Send a message using the given memory strategy."""
    memory.add("user", user_msg)

    if isinstance(memory, VectorMemory):
        messages = memory.get_messages(current_query=user_msg)
    else:
        messages = memory.get_messages()

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
        max_tokens=150,
    )
    reply = response.choices[0].message.content
    memory.add("assistant", reply)
    return reply


def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🧠 Memory Strategies Compared               ║")
    print("╚══════════════════════════════════════════════╝\n")

    # Conversation that tests memory recall
    conversation = [
        "My name is Alice and I'm a Java developer at TechCorp.",
        "I prefer Spring Boot and use PostgreSQL for databases.",
        "What time zone should I use for scheduling? I'm in Tokyo.",
        "I also have experience with Kubernetes and Docker.",
        "We're migrating from monolith to microservices.",
        "Can you recommend a message broker? We handle 10K msg/sec.",
        # This question tests recall of early information
        "What's my name and where do I work?",
    ]

    strategies = {
        "Buffer": BufferMemory(),
        "Window(3)": WindowMemory(window_size=3),
        "Summary": SummaryMemory(summarize_threshold=6),
    }

    # Run conversation through first 3 strategies
    for name, memory in strategies.items():
        print(f"\n  {'═'*55}")
        print(f"  📊 Strategy: {name}")
        print(f"  {'─'*55}")

        for msg in conversation:
            reply = chat_with(memory, msg)
            if msg == conversation[-1]:  # Only show the recall test
                print(f"\n  👤 Test: \"{msg}\"")
                print(f"  🤖 Reply: {reply[:200]}")

        print(f"  📊 {memory.stats()}")

    # Vector memory (uses embeddings, do separately)
    print(f"\n  {'═'*55}")
    print(f"  📊 Strategy: Vector(top-3)")
    print(f"  {'─'*55}")

    vec_mem = VectorMemory(top_k=3)
    for msg in conversation:
        reply = chat_with(vec_mem, msg)
        if msg == conversation[-1]:
            print(f"\n  👤 Test: \"{msg}\"")
            print(f"  🤖 Reply: {reply[:200]}")

    print(f"  📊 {vec_mem.stats()}")

    # Summary
    print(f"\n\n  {'═'*55}")
    print(f"  📋 COMPARISON SUMMARY:")
    print(f"  {'═'*55}")
    print(f"""
  ┌──────────┬──────────┬──────────┬──────────┐
  │ Strategy │ Recall?  │ Cost     │ Scales?  │
  ├──────────┼──────────┼──────────┼──────────┤
  │ Buffer   │ ✅ All   │ 📈 High  │ ❌ No    │
  │ Window   │ ⚠️ Recent│ 📊 Fixed │ ✅ Yes   │
  │ Summary  │ ✅ Key   │ 📊 Med   │ ✅ Yes   │
  │ Vector   │ ✅ Smart │ 📊 Low*  │ ✅ Yes   │
  └──────────┴──────────┴──────────┴──────────┘
  * per-query cost is low, but embedding all messages has upfront cost
    """)


if __name__ == "__main__":
    main()
