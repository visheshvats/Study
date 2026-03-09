# MODULE 7: Memory in Agents — Complete Notes

> **For:** Engineers who've built agents (Module 4-6) and want them to
> remember context across conversations, sessions, and lifetimes.
> **Key insight:** LLMs are stateless — they forget everything after each call.
> Memory is what turns a chat-bot into an assistant that KNOWS you.

---

# LESSON 7.1: Why Memory Matters

## The Core Problem: LLMs Are Stateless

```
┌──────────────────────────────────────────────────────┐
│  WITHOUT MEMORY (Stateless)                          │
│                                                       │
│  Turn 1: "My name is Alice"        → "Nice to meet you, Alice!"
│  Turn 2: "What's my name?"         → "I don't know your name."
│                                                       │
│  Every API call starts fresh. The LLM has ZERO       │
│  memory of previous conversations.                   │
│                                                       │
│  WITH MEMORY (Stateful)                              │
│                                                       │
│  Turn 1: "My name is Alice"        → "Nice to meet you, Alice!"
│            ↓ (saved to memory)                       │
│  Turn 2: "What's my name?"         → "Your name is Alice!"
│            ↑ (loaded from memory)                    │
│                                                       │
│  Memory is code YOU write to persist context.        │
│  The LLM itself has no memory — YOU manage it.       │
└──────────────────────────────────────────────────────┘
```

**Java Analogy:** LLMs are like **stateless REST APIs**. Every request is independent.
Memory is like adding a **session store** (Redis/HttpSession) — state is managed
externally and injected into each request.

---

## What Memory Enables

| Without Memory | With Memory |
|---------------|-------------|
| "What's my name?" → "I don't know" | "Your name is Alice" |
| Repeats suggestions | Remembers what you tried |
| Generic responses | Personalized to your preferences |
| Loses track in long conversations | Maintains context over hours |
| Can't learn from past sessions | Recalls past interactions |
| No user profile | Knows your tech stack, role, preferences |

---

# LESSON 7.2: Types of Memory

```
┌──────────────────────────────────────────────────────────┐
│  AGENT MEMORY TYPES                                       │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  SHORT-TERM MEMORY (Conversation Buffer)         │    │
│  │  • Current conversation messages                  │    │
│  │  • Lasts: one conversation session               │    │
│  │  • Like: Java method local variables             │    │
│  │  • Implementation: messages[] list                │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  LONG-TERM MEMORY (Persistent Knowledge)         │    │
│  │  • Facts learned about user/domain                │    │
│  │  • Lasts: forever (until deleted)                 │    │
│  │  • Like: Database records                        │    │
│  │  • Implementation: vector DB / key-value store    │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  EPISODIC MEMORY (Past Events)                    │    │
│  │  • Summaries of past conversations               │    │
│  │  • Lasts: forever, searchable                    │    │
│  │  • Like: Log files / event store                 │    │
│  │  • Implementation: embeddings + vector search     │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  SEMANTIC MEMORY (World Knowledge)                │    │
│  │  • General knowledge, company docs, FAQ          │    │
│  │  • Lasts: forever, updated periodically          │    │
│  │  • Like: Reference documentation                 │    │
│  │  • Implementation: RAG + vector DB (Module 3)     │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  PROCEDURAL MEMORY (How to Do Things)             │    │
│  │  • Learned procedures, workflows, preferences    │    │
│  │  • Lasts: forever, refined over time             │    │
│  │  • Like: Configuration / user preferences        │    │
│  │  • Implementation: structured rules + DB          │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### Memory Type Decision Matrix

| Memory Type | Duration | Scope | Example | Java Analogy |
|------------|----------|-------|---------|-------------|
| Short-term | One session | Current chat | "User asked about Java" | Method variables |
| Long-term | Permanent | User profile | "User prefers Spring Boot" | Database record |
| Episodic | Permanent | Past events | "Last week we discussed K8s" | Event log |
| Semantic | Permanent | Domain knowledge | "Our API uses OAuth2" | Reference docs |
| Procedural | Permanent | Learned skills | "User likes bullet-point answers" | Config file |

---

# LESSON 7.3: Implementation Strategies

## Strategy 1: Conversation Buffer (Simplest)

```
┌──────────────────────────────────────────────────────┐
│  BUFFER MEMORY                                        │
│                                                       │
│  Store ALL messages in a list. Send ALL to LLM.      │
│                                                       │
│  messages = [                                        │
│    {system: "You are helpful..."},                   │
│    {user: "My name is Alice"},                       │
│    {assistant: "Nice to meet you!"},                 │
│    {user: "What's my name?"},       ← All sent      │
│    {assistant: "Your name is Alice!"},   to LLM     │
│  ]                                                   │
│                                                       │
│  ✅ Pros: Simple, perfect recall within window       │
│  ❌ Cons: Hits context limit with long conversations │
│  📊 Cost: Grows linearly (expensive for long chats) │
│                                                       │
│  Java Analogy: ArrayList — keeps everything.         │
│  Works until you run out of memory (context window). │
└──────────────────────────────────────────────────────┘
```

## Strategy 2: Sliding Window (Token Budget)

```
┌──────────────────────────────────────────────────────┐
│  WINDOW MEMORY                                        │
│                                                       │
│  Keep only the last N messages. Older ones are       │
│  dropped. Stays within token budget.                 │
│                                                       │
│  messages = [                                        │
│    {system: "..."},                                  │
│    ── dropped: {user: "My name is Alice"} ──        │
│    ── dropped: {assistant: "Nice to meet you!"} ──  │
│    {user: "Tell me about Java 21"},     ← Last N    │
│    {assistant: "Java 21 has virtual..."}, messages   │
│    {user: "What's my name?"},           only        │
│  ]                                                   │
│  → "I don't know your name" (lost earlier context!) │
│                                                       │
│  ✅ Pros: Fixed cost, stays within token budget      │
│  ❌ Cons: Loses early context, "forgetting" problem  │
│                                                       │
│  Java Analogy: Ring buffer / CircularFifoQueue.      │
└──────────────────────────────────────────────────────┘
```

## Strategy 3: Summary Memory (Compress)

```
┌──────────────────────────────────────────────────────┐
│  SUMMARY MEMORY                                       │
│                                                       │
│  Periodically summarize old messages into a compact  │
│  summary. Keep summary + recent messages.            │
│                                                       │
│  messages = [                                        │
│    {system: "..."},                                  │
│    {system: "CONVERSATION SUMMARY:                   │
│      The user's name is Alice. She is a Java dev    │
│      interested in Spring Boot and microservices.    │
│      We discussed Java 21 virtual threads."},       │
│    {user: "What's my name?"},     ← Recent messages │
│    {assistant: "Your name is Alice!"},              │
│  ]                                                   │
│                                                       │
│  ✅ Pros: Preserves key info, bounded cost           │
│  ❌ Cons: Loses details, summarization adds latency  │
│                                                       │
│  Java Analogy: Log rotation with compression.        │
└──────────────────────────────────────────────────────┘
```

## Strategy 4: Vector Memory (Semantic Search)

```
┌──────────────────────────────────────────────────────┐
│  VECTOR MEMORY                                        │
│                                                       │
│  Store all messages as embeddings. For each new turn,│
│  search for relevant past messages and inject them.  │
│                                                       │
│  User: "What's my name?"                             │
│                                                       │
│  1. Embed the query                                  │
│  2. Search vector DB for similar past messages       │
│  3. Found: "My name is Alice" (similarity: 0.92)    │
│  4. Inject into context                              │
│                                                       │
│  messages = [                                        │
│    {system: "..."},                                  │
│    {system: "RELEVANT PAST CONTEXT:                  │
│      [Turn 1] User said: 'My name is Alice'         │
│      [Turn 1] You replied: 'Nice to meet you!'"},   │
│    {user: "What's my name?"},                        │
│  ]                                                   │
│                                                       │
│  ✅ Pros: Scales infinitely, retrieves relevant info │
│  ❌ Cons: May miss context, embedding cost           │
│                                                       │
│  Java Analogy: Elasticsearch for logs —              │
│  search relevant entries, not all entries.            │
└──────────────────────────────────────────────────────┘
```

## Strategy 5: Hybrid Memory (Production Best Practice)

```
┌──────────────────────────────────────────────────────────┐
│  HYBRID MEMORY (Recommended for Production)              │
│                                                           │
│  Combine multiple strategies:                            │
│                                                           │
│  ┌──────────────────────────────────┐                    │
│  │  SYSTEM PROMPT                   │                    │
│  │  • Summary of conversation so far│  ← Summary Memory │
│  │  • User profile/preferences      │  ← Long-term      │
│  │  • Relevant past conversations   │  ← Vector Memory  │
│  ├──────────────────────────────────┤                    │
│  │  RECENT MESSAGES                 │                    │
│  │  • Last 10-20 messages          │  ← Window Memory  │
│  ├──────────────────────────────────┤                    │
│  │  CURRENT USER MESSAGE           │                    │
│  └──────────────────────────────────┘                    │
│                                                           │
│  Token Budget Allocation:                                │
│  ┌───────────┬────────────┬───────────┬──────────────┐  │
│  │ System    │ Memory     │ Recent    │ Current +    │  │
│  │ Prompt    │ Context    │ Messages  │ Response     │  │
│  │ 500 tok   │ 1000 tok   │ 2000 tok  │ 4500 tok     │  │
│  └───────────┴────────────┴───────────┴──────────────┘  │
│  Total: ~8000 tokens for gpt-4o-mini                    │
└──────────────────────────────────────────────────────────┘
```

### Strategy Comparison

```
┌──────────────┬──────────┬──────────┬──────────┬──────────┐
│ Strategy     │  Cost    │ Recall   │ Scales?  │ Use When │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│ Buffer       │ High     │ Perfect  │ No       │ Short chats
│ Window       │ Fixed    │ Recent   │ Yes      │ Casual chat
│ Summary      │ Medium   │ Key info │ Yes      │ Long sessions
│ Vector       │ Low/call │ Relevant │ Yes      │ Multi-session
│ Hybrid       │ Tunable  │ Best     │ Yes      │ Production
└──────────────┴──────────┴──────────┴──────────┴──────────┘
```

---

# LESSON 7.4: Persistent Memory with Databases

## Storage Options

```
┌──────────────────────────────────────────────────────┐
│  WHERE TO STORE AGENT MEMORY                         │
│                                                       │
│  1. IN-MEMORY (dict/list)                            │
│     • Fast, simple, lost on restart                  │
│     • Good for development                           │
│                                                       │
│  2. FILE SYSTEM (JSON/SQLite)                        │
│     • Simple persistence, single-user                │
│     • Good for personal assistants                   │
│                                                       │
│  3. KEY-VALUE STORE (Redis)                          │
│     • Fast, shared, TTL support                      │
│     • Good for session memory                        │
│                                                       │
│  4. VECTOR DATABASE (ChromaDB, Pinecone)             │
│     • Semantic search over memories                  │
│     • Good for episodic/semantic memory              │
│                                                       │
│  5. RELATIONAL DB (PostgreSQL)                       │
│     • Structured, queryable, ACID                    │
│     • Good for user profiles (long-term memory)      │
│                                                       │
│  RECOMMENDATION:                                     │
│  SQLite for local + ChromaDB for search =            │
│  lightweight but powerful for most use cases!        │
└──────────────────────────────────────────────────────┘
```

---

## Memory Architecture for Production

```
┌──────────────────────────────────────────────────────────────────┐
│                  PRODUCTION MEMORY ARCHITECTURE                   │
│                                                                   │
│  User Message                                                    │
│       │                                                           │
│       ▼                                                           │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                   MEMORY MANAGER                          │    │
│  │                                                           │    │
│  │  1. Load user profile ────────────▶ PostgreSQL/SQLite    │    │
│  │  2. Search relevant memories ─────▶ ChromaDB (vector)    │    │
│  │  3. Get conversation summary ─────▶ Redis/Cache          │    │
│  │  4. Get recent messages ──────────▶ In-Memory buffer     │    │
│  │                                                           │    │
│  │  5. Assemble context:                                    │    │
│  │     [System Prompt]                                      │    │
│  │     [User Profile]           ← from DB                   │    │
│  │     [Relevant Memories]      ← from vector search        │    │
│  │     [Conversation Summary]   ← from cache                │    │
│  │     [Recent Messages]        ← from buffer               │    │
│  │     [Current Message]        ← from user                 │    │
│  │                                                           │    │
│  │  6. Call LLM with assembled context                      │    │
│  │                                                           │    │
│  │  7. After response:                                      │    │
│  │     • Append to buffer                                   │    │
│  │     • Extract facts → store in DB                        │    │
│  │     • Embed messages → store in vector DB                │    │
│  │     • Update summary if needed                           │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Java Analogy:                                                   │
│  This is like a Spring Boot service with:                        │
│  • @Cacheable for recent context (Redis)                        │
│  • JPA for structured user data (PostgreSQL)                    │
│  • Elasticsearch for full-text memory search                    │
│  • In-memory buffer for current request scope                   │
└──────────────────────────────────────────────────────────────────┘
```

---

# LESSON 7.5: Code Examples

See the `code/` directory:

1. **`01_memory_strategies.py`** — 4 memory strategies compared (buffer, window, summary, vector)
2. **`02_persistent_memory.py`** — SQLite-backed memory that survives restarts
3. **`03_vector_memory.py`** — ChromaDB-based episodic memory with semantic recall
4. **`04_personal_assistant.py`** — **PROJECT:** Full assistant with hybrid memory system

---

# LESSON 7.6: Exercises

## Exercise 1: Memory Strategies
1. Implement a chatbot with buffer memory and test with 50 messages — what happens?
2. Add token counting and implement automatic window trimming
3. Compare the quality of recall between window (last 10) and summary strategies

## Exercise 2: Persistent Memory
1. Extend the SQLite memory to include user-preference extraction
2. Add a "user profile" that accumulates facts across sessions
3. Test: set preferences in session 1, verify recall in session 2

## Exercise 3: Design Challenge
1. Design a memory system for a customer support agent that:
   - Remembers customer history across tickets
   - Knows common solutions (semantic memory)
   - Has a "company policy" memory (procedural)
2. Draw the architecture diagram with storage choices

---

# LESSON 7.7: Interview Questions & Answers

## Q1: Why do AI agents need memory? Aren't LLMs already trained on data?

**Answer:** LLMs are **stateless** — every API call is independent with zero memory of
previous interactions. The model's training data gives it general knowledge, but not:
(1) Context from the current conversation (need short-term memory), (2) Knowledge about
the specific user (need long-term memory), (3) Information about past interactions (need
episodic memory), (4) Company-specific knowledge (need semantic memory / RAG). Memory
is the external system YOU build to persist and retrieve context. Without memory, every
conversation starts from zero — the LLM can't learn or personalize.

## Q2: Explain the 5 types of agent memory and give an example of each.

**Answer:** (1) **Short-term** — current conversation messages. Example: remembering the
user said their name 3 turns ago. (2) **Long-term** — persistent facts about the user.
Example: knowing the user prefers Spring Boot and works at a fintech company. (3)
**Episodic** — summaries of past conversations. Example: "Last week we discussed deploying
to Kubernetes." (4) **Semantic** — domain/world knowledge. Example: company documentation
about the internal API. (5) **Procedural** — learned procedures and preferences. Example:
knowing the user likes bullet-point answers with code examples.

## Q3: Compare buffer, window, summary, and vector memory strategies.

**Answer:** **Buffer**: stores all messages, perfect recall but hits token limits with long
conversations (O(n) cost). **Window**: keeps last N messages, fixed cost but loses early
context (user's name from turn 1 is forgotten). **Summary**: LLM periodically compresses
old messages into a summary, preserves key info with bounded cost, but loses details and
adds summarization latency. **Vector**: embeds all messages, retrieves relevant ones via
semantic search, scales infinitely but may miss context if embedding doesn't capture it.
In production, use **hybrid** — summary + vector + recent window combined.

## Q4: How do you handle token budget management for memory?

**Answer:** Allocate the context window budget: (1) System prompt: ~500 tokens
(fixed). (2) Memory context: ~1000-2000 tokens (user profile + relevant memories +
conversation summary). (3) Recent messages: ~2000 tokens (sliding window, most recent
turns). (4) Current message + response buffer: remaining tokens. Monitor total tokens
per request and implement strategies: trim oldest messages first, compress summaries if
too long, limit vector search results to top-3. Use tiktoken to count tokens accurately
before sending. Set max_tokens for response to prevent overflow.

## Q5: How would you implement memory for a multi-user production system?

**Answer:** Architecture: (1) **User isolation** — every memory entry is tagged with
user_id, queries always filter by user. Like multi-tenancy in databases. (2) **Storage** —
PostgreSQL for user profiles (long-term), ChromaDB/Pinecone for episodic memories
(vector search), Redis for session-scoped context (short-term). (3) **Memory Manager
service** — a service layer that orchestrates: load user profile → search relevant memories
→ assemble context → call LLM → extract new facts → store. (4) **Privacy** — user can
delete their memory, GDPR compliance, no cross-user memory leakage. (5) **TTL** — auto-expire
session memory after 24h, keep long-term memory indefinitely.

## Q6: What is the "lost in the middle" problem with memory?

**Answer:** Research shows LLMs pay most attention to the **beginning** and **end** of
the context window, giving less attention to content in the middle. This means: if you
pack memory context in the middle of a long prompt, the LLM may ignore it. Solutions:
(1) Put the most important memory at the **start** (right after system prompt) or
**end** (just before the user message). (2) Keep the total context concise — don't flood
with irrelevant memories. (3) Use recency bias — recent messages at the end where the
LLM pays most attention. (4) When injecting retrieved memories, rank by relevance and
put the most relevant first.

---

# Common Mistakes

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| No memory at all | Every conversation starts from zero | Add at minimum conversation buffer |
| Unbounded buffer | Hits token limit, API errors | Use window or summary strategy |
| Storing everything as memory | Noise drowns out signal | Extract only key facts/preferences |
| No user isolation | Memory leaks between users | Tag all memories with user_id |
| Ignoring token costs | Memory-heavy prompts are expensive | Set token budgets per section |
| Putting memories in the middle | LLM ignores middle context | Place important context first or last |
| Not testing memory recall | Assumed it works, doesn't | Write tests: set fact → query later |

---

# Best Practices

1. **Start with buffer, add complexity as needed** — don't over-engineer memory early
2. **Hybrid memory for production** — summary + vector + window = best recall
3. **Token budget discipline** — allocate tokens: system (10%), memory (20%), messages (40%), response (30%)
4. **Extract, don't dump** — use LLM to extract key facts instead of storing raw messages
5. **User profile as memory** — maintain a structured profile that grows over time
6. **Test recall explicitly** — set a fact, then query it 10 turns later
7. **Memory TTL** — auto-expire stale session data, keep long-term facts
8. **Privacy by design** — users must be able to view and delete their memory
9. **Place important context first** — avoid the "lost in the middle" problem
10. **Monitor memory quality** — log what was recalled vs what was relevant

---

**Next Module:** [Module 8 — Tool Calling and Function Calling (Deep Dive) →](../module-8-tool-calling/)

Say **NEXT** to continue.
