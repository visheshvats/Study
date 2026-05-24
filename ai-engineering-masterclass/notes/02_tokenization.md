# Topic 2: Tokenization

> **Java Analogy:** Tokenization is like `String.split()` on steroids — but instead of splitting on whitespace or regex, it uses a learned vocabulary of sub-word units, similar to how `java.text.BreakIterator` finds word boundaries but optimized for ML efficiency.

---

## What This Is (Plain English)

Before an LLM can process text, the raw string must be broken into numbered chunks called **tokens**. These aren't full words — they're sub-word pieces. "unhappiness" → `["un", "happiness"]`. "ChatGPT" → `["Chat", "G", "PT"]`. Each token maps to an integer ID, and these IDs are what the model actually processes.

Why not just split on spaces? Because "running" and "run" would be unrelated entries. Sub-word tokenization shares the "run" prefix, so the model knows they're related — drastically reducing vocabulary size and improving generalization.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Vocabulary** | A `Map<String, Integer>` mapping sub-word strings to integer IDs (like an enum ordinal). |
| **Tokenizer** | A specialized `String → int[]` converter. Think of it as a custom `Codec` or `Serializer`. |
| **BPE merges** | Like a `TreeMap<Pair<String,String>, String>` of character-pair merge rules, applied greedily left-to-right. |
| **Special tokens** | Like sentinel values — `[CLS]`, `[SEP]`, `[PAD]` serve as control characters (think `\0`, `\n` in protocol design). |
| **Token ID** | An index into the embedding matrix — conceptually `embeddingMatrix[tokenId]` returning a `float[]`. |

---

## Why This Matters to You

As a Java backend engineer building AI features:

1. **Token counting determines cost.** API pricing is per-token, not per-character. You need to estimate token counts before sending requests to stay within budget.
2. **Token limits determine what fits.** A 4K-token context window isn't 4K words — it's roughly 3K English words or 1.5K lines of Java code.
3. **Different models use different tokenizers.** GPT-4 and Claude have incompatible tokenizers. You can't count tokens for one and assume it works for the other.

---

## Practical Token Math

| Content Type | Approx. Tokens per Word | Approx. Tokens per Line |
|---|---|---|
| English prose | ~1.3 | ~12 |
| Java code | ~2.5 | ~20 |
| JSON | ~3.0 | ~25 |
| Hindi/Arabic text | ~3-5 | ~30+ |
| URLs | ~5-10 per URL | — |

**Rule of thumb:** 1 token ≈ 4 characters in English. 750 words ≈ 1,000 tokens.

---

## Java Ecosystem & Libraries

| Library | Purpose |
|---|---|
| **jtokkit** | Pure Java implementation of OpenAI's tokenizers (GPT-3.5/4/4o). Fast, zero dependencies. The library you need. |
| **tiktoken (via Python)** | OpenAI's official tokenizer — call from Java via ProcessBuilder if jtokkit doesn't suffice. |
| **HuggingFace Tokenizers** | Rust-based, blazing fast. Can be called via JNI or REST microservice. |
| **LangChain4j** | Built-in token estimation for context window management. |

---

## Code Bridge

### Token Counting with jtokkit

```java
// Maven: com.knuddels:jtokkit:1.0.0
import com.knuddels.jtokkit.Encodings;
import com.knuddels.jtokkit.api.Encoding;
import com.knuddels.jtokkit.api.EncodingType;
import com.knuddels.jtokkit.api.EncodingRegistry;

public class TokenCounter {
    private final Encoding encoding;

    public TokenCounter() {
        EncodingRegistry registry = Encodings.newDefaultEncodingRegistry();
        // cl100k_base is used by GPT-4, GPT-3.5-turbo
        this.encoding = registry.getEncoding(EncodingType.CL100K_BASE);
    }

    public int countTokens(String text) {
        return encoding.encode(text).size();
    }

    public List<String> tokenize(String text) {
        List<Integer> ids = encoding.encode(text);
        return ids.stream()
            .map(id -> encoding.decode(List.of(id)))
            .toList();
    }

    public static void main(String[] args) {
        var counter = new TokenCounter();
        
        String text = "Spring Boot makes it easy to create stand-alone applications.";
        System.out.println("Text: " + text);
        System.out.println("Token count: " + counter.countTokens(text));
        System.out.println("Tokens: " + counter.tokenize(text));
        // Output: Token count: 11
        // Tokens: [Spring,  Boot,  makes,  it,  easy,  to,  create,  stand, -alone,  applications, .]
    }
}
```

### Token Budget Management

```java
@Service
public class TokenBudgetManager {
    private static final int MAX_CONTEXT_TOKENS = 4096;
    private static final int SYSTEM_PROMPT_BUDGET = 300;
    private static final int RESPONSE_RESERVE = 800;

    private final TokenCounter tokenCounter;

    public String buildPrompt(String systemPrompt, List<Message> history, String userQuery) {
        int available = MAX_CONTEXT_TOKENS - SYSTEM_PROMPT_BUDGET - RESPONSE_RESERVE;
        int queryTokens = tokenCounter.countTokens(userQuery);
        available -= queryTokens;

        // Add history messages newest-first until budget exhausted
        List<Message> fittingHistory = new ArrayList<>();
        for (int i = history.size() - 1; i >= 0 && available > 0; i--) {
            int msgTokens = tokenCounter.countTokens(history.get(i).content());
            if (msgTokens <= available) {
                fittingHistory.add(0, history.get(i));
                available -= msgTokens;
            } else {
                break;  // Stop — can't fit partial messages
            }
        }

        return assembleFinalPrompt(systemPrompt, fittingHistory, userQuery);
    }
}
```

---

## Key Algorithms

### BPE (Byte-Pair Encoding) — How It Works

```
Step 1: Start with characters    → ['l', 'o', 'w', 'e', 'r']
Step 2: Count adjacent pairs     → ('l','o')=5, ('o','w')=3, ('w','e')=2...
Step 3: Merge most frequent pair  → ['lo', 'w', 'e', 'r']
Step 4: Repeat for K iterations   → ['low', 'er']
Final vocabulary after 32K merges → Contains optimal sub-word units
```

The tokenizer is trained once and then frozen. Every API call uses the same tokenizer — it's deterministic.

---

## Production Patterns

1. **Pre-flight token check:** Before calling the LLM API, count tokens. If over limit, truncate history or summarize context. Never let the API return a 400 error for context overflow.

2. **Cost estimation service:**
```java
public double estimateCost(String input, int expectedOutputTokens) {
    int inputTokens = tokenCounter.countTokens(input);
    double inputCost = inputTokens * COST_PER_INPUT_TOKEN;   // e.g., $2.50 / 1M
    double outputCost = expectedOutputTokens * COST_PER_OUTPUT_TOKEN;  // e.g., $10 / 1M
    return inputCost + outputCost;
}
```

3. **Logging:** Always log token counts per request for cost attribution and monitoring.

---

## Interview-Ready Summary

- Tokenization converts raw text to integer IDs using sub-word splitting (BPE).
- Sub-word tokenization enables vocabulary sharing ("run" + "ning") and handles unseen words.
- Token count ≠ word count. English: ~1.3 tokens/word. Code: ~2.5 tokens/word.
- Use `jtokkit` in Java to count tokens for OpenAI models.
- Token counting is essential for cost estimation, context budget management, and input validation.
- The tokenizer is deterministic — same input always produces same tokens.
