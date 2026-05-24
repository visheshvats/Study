# Topic 12: Context Engineering

> **Java Analogy:** Context engineering is like managing a fixed-size `ByteBuffer`. You have a limited capacity (context window), and every byte matters — system instructions, conversation history, retrieved documents, and the user's query all compete for space. You're the architect deciding what stays, what gets evicted, and what gets compressed.

---

## What This Is (Plain English)

The context window is everything the model "sees" when generating a response — system prompt, conversation history, RAG documents, tool results, and the user query. It's a fixed size (4K–1M tokens depending on the model). Context engineering is the discipline of strategically managing what goes into this window, in what order, and at what compression level — because what the model sees determines what it produces.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Context window** | Fixed-size `ByteBuffer` or bounded `BlockingQueue` |
| **Token budget** | Like JVM heap size — fixed limit, everything must fit |
| **System prompt** | `application.yml` config — loaded at startup, rarely changes |
| **Conversation history** | `LinkedList<Message>` with a max-size eviction policy (LRU) |
| **Sliding window** | `CircularBuffer` that drops oldest entries when full |
| **Summary compression** | Like `gzip` for conversations — compress old messages to save space |
| **Context assembly** | `StringBuilder` with priority-ordered `append()` calls and a size check |

---

## Token Budget Breakdown

```
Total Context: 4096 tokens (gpt-4o-mini)
┌──────────────────────────────────────────────────────┐
│ System Prompt          │ 300 tokens  │ Fixed          │
├────────────────────────┼─────────────┼────────────────┤
│ RAG Context (3 chunks) │ 1500 tokens │ Variable       │
├────────────────────────┼─────────────┼────────────────┤
│ Conversation History   │ 1200 tokens │ Sliding window │
├────────────────────────┼─────────────┼────────────────┤
│ User Query             │ 200 tokens  │ Current turn   │
├────────────────────────┼─────────────┼────────────────┤
│ Reserved for Response  │ 800 tokens  │ Generation     │
└──────────────────────────────────────────────────────┘
```

**If you don't reserve tokens for the response, the model will hit the limit mid-sentence and truncate.**

---

## Code Bridge

### Context Window Manager

```java
@Service
public class ContextManager {
    private final TokenCounter tokenCounter;

    private static final int MAX_TOKENS = 4096;
    private static final int SYSTEM_BUDGET = 300;
    private static final int RESPONSE_RESERVE = 800;
    private static final int MAX_HISTORY_TURNS = 10;

    public ContextWindow build(
        String systemPrompt,
        List<Message> history,
        List<String> ragChunks,
        String userQuery
    ) {
        int available = MAX_TOKENS - RESPONSE_RESERVE;

        // 1. System prompt (always included, highest priority)
        int systemTokens = tokenCounter.countTokens(systemPrompt);
        available -= systemTokens;

        // 2. User query (always included)
        int queryTokens = tokenCounter.countTokens(userQuery);
        available -= queryTokens;

        // 3. RAG context (high priority — most relevant first)
        List<String> fittingChunks = new ArrayList<>();
        for (String chunk : ragChunks) {
            int chunkTokens = tokenCounter.countTokens(chunk);
            if (chunkTokens <= available) {
                fittingChunks.add(chunk);
                available -= chunkTokens;
            }
        }

        // 4. History (lowest priority — newest first, oldest evicted)
        List<Message> fittingHistory = new ArrayList<>();
        List<Message> recent = history.subList(
            Math.max(0, history.size() - MAX_HISTORY_TURNS), 
            history.size()
        );
        for (int i = recent.size() - 1; i >= 0 && available > 0; i--) {
            int msgTokens = tokenCounter.countTokens(recent.get(i).content());
            if (msgTokens <= available) {
                fittingHistory.add(0, recent.get(i));
                available -= msgTokens;
            } else {
                break;
            }
        }

        return new ContextWindow(systemPrompt, fittingHistory, fittingChunks, userQuery);
    }
}
```

### Conversation Summary Compression

```java
@Service
public class ConversationCompressor {
    private final ChatLanguageModel summaryModel;  // Use a cheap, fast model

    /**
     * Compresses old conversation turns into a brief summary.
     * Converts O(n) growing history into O(1) fixed-size summary.
     */
    public String compressHistory(List<Message> oldMessages) {
        String transcript = oldMessages.stream()
            .map(m -> m.role() + ": " + m.content())
            .collect(Collectors.joining("\n"));

        return summaryModel.generate("""
            Summarize this conversation in 2-3 sentences,
            preserving key facts, decisions, and user preferences:
            
            %s
            """.formatted(transcript));
    }

    /**
     * Manages sliding window with compression.
     */
    public List<Message> manageHistory(
        List<Message> fullHistory, 
        int keepRecentTurns
    ) {
        if (fullHistory.size() <= keepRecentTurns * 2) {
            return fullHistory;  // Fits without compression
        }

        // Split: old messages get compressed, recent stay intact
        List<Message> old = fullHistory.subList(0, fullHistory.size() - keepRecentTurns * 2);
        List<Message> recent = fullHistory.subList(fullHistory.size() - keepRecentTurns * 2, fullHistory.size());

        String summary = compressHistory(old);

        List<Message> managed = new ArrayList<>();
        managed.add(new Message("system", "[Previous conversation summary: " + summary + "]"));
        managed.addAll(recent);
        return managed;
    }
}
```

### Priority-Based Eviction

```java
public enum ContextPriority {
    SYSTEM_PROMPT(1),      // Never evict
    USER_QUERY(2),         // Never evict
    RAG_CONTEXT(3),        // Evict after old history
    RECENT_HISTORY(4),     // Evict oldest first
    OLD_HISTORY(5),        // First to go
    TOOL_RESULTS(6);       // Evict after use

    final int priority;
}
```

---

## Stateless vs Stateful

| Approach | How It Works | Pros | Cons |
|---|---|---|---|
| **Stateless** | Full context sent every request. Like REST — no server-side session. | Simple, scalable, no session management | Expensive (re-sends entire history every call) |
| **Stateful** | Server maintains session. Incremental updates only. Like WebSocket. | Token-efficient for long conversations | Complex session management, sticky sessions needed |

**Most production systems are stateless** — they reconstruct the full context from a database on each request. The client sends a `sessionId`, the server loads history from Redis/DB, builds the context, calls the LLM, and stores the new messages.

---

## Hidden Token Overhead

```java
// What you THINK the cost is:
"Hello"  // 1 token

// What the API ACTUALLY processes:
"<|im_start|>user\nHello<|im_end|>\n<|im_start|>assistant\n"  // 9 tokens!

// Each message boundary adds ~4-6 tokens of invisible formatting
// A 10-message conversation has ~50 tokens of pure overhead
```

**Always use the tokenizer to count actual tokens, not `String.length() / 4`.**

---

## Interview-Ready Summary

- Context engineering manages the fixed-size token budget of an LLM's context window.
- Budget allocation: system prompt (fixed) + RAG context + conversation history + user query + response reserve.
- Sliding window with summary compression converts O(n) growing history to O(1) fixed space.
- Priority-based eviction: old history goes first, system prompt and query never evicted.
- Chat APIs add invisible formatting tokens (~4-6 per message boundary).
- Most production systems are stateless — reconstruct context from DB on each request.
- Always reserve tokens for the response (typically 500-1000).
