# Topic 16: Reasoning Models (LRMs)

> **Java Analogy:** Standard LLMs are like calling `method()` with a fixed timeout — same compute for every input. Reasoning models are like `ForkJoinPool` — they dynamically allocate more threads (thinking tokens) to harder problems. Simple inputs finish instantly; complex problems get as much compute as they need.

---

## What This Is (Plain English)

Reasoning models (OpenAI o1/o3, DeepSeek-R1) go beyond standard chain-of-thought. Instead of generating a single linear reasoning trace, they run an *internal deliberation loop* — generating hypotheses, evaluating them, backtracking from dead ends, and trying different approaches. The model dynamically decides how much "thinking time" to spend based on problem difficulty. Simple factual questions take 1 second; complex math proofs take 30-60 seconds.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Standard LLM** | `FixedThreadPool(1)` — same compute for every task |
| **Reasoning model** | `ForkJoinPool` — dynamically scales compute per task complexity |
| **Thinking tokens** | Internal `log.trace()` output — extensive reasoning traces hidden from the user |
| **Test-time compute scaling** | Like using `@Timeout(adaptive=true)` — harder problems get more time |
| **Self-evaluation** | Like running unit tests inside the generation loop — model checks its own work |
| **Backtracking** | Like `git revert` during reasoning — model abandons bad approaches and tries new ones |

---

## Standard LLM vs Reasoning Model

```
STANDARD LLM (GPT-4o):
User: "Prove that √2 is irrational"
Model: [Single forward pass → immediate response]
Time: 2 seconds, 200 tokens
Accuracy: ~70%

REASONING MODEL (o3):
User: "Prove that √2 is irrational"
Model: [Internal thinking loop...]
  → Hypothesis 1: Proof by contradiction... let me check...
  → Found an error in step 3, backtracking...
  → Hypothesis 2: Assume √2 = p/q in lowest terms...
  → Verification: Does this satisfy all constraints? Yes.
  → Final answer extracted.
Time: 30 seconds, 5000 thinking tokens + 300 output tokens
Accuracy: ~95%
```

---

## When to Use Reasoning Models

| Task | Standard LLM | Reasoning Model | Use Which? |
|---|---|---|---|
| "What's the weather?" | ✅ Perfect | Overkill | Standard |
| Sentiment classification | ✅ Perfect | Overkill | Standard |
| Multi-step math proof | ❌ Often wrong | ✅ Strong | Reasoning |
| Complex code debugging | ❌ Misses edge cases | ✅ Thorough | Reasoning |
| Planning/scheduling | ❌ Superficial | ✅ Deep | Reasoning |
| Creative writing | ✅ Good | Similar | Standard (cheaper) |

---

## The Model Router Pattern

The optimal production architecture routes queries to the cheapest model that can handle them:

```java
@Service
public class ModelRouter {
    private final ChatLanguageModel fastModel;      // GPT-4o-mini ($0.15/1M)
    private final ChatLanguageModel standardModel;   // GPT-4o ($2.50/1M)
    private final ChatLanguageModel reasoningModel;  // o3 ($10/1M + thinking)

    private final ChatLanguageModel classifierModel; // Cheap classifier

    public String route(String query) {
        // Classify query difficulty
        String difficulty = classifierModel.generate("""
            Classify this query complexity as SIMPLE, MEDIUM, or COMPLEX.
            SIMPLE: factual lookup, classification, formatting
            MEDIUM: summarization, explanation, code generation
            COMPLEX: mathematical proof, multi-step reasoning, planning
            Query: "%s"
            Classification:""".formatted(query)).trim();

        return switch (difficulty) {
            case "SIMPLE" -> fastModel.generate(query);
            case "MEDIUM" -> standardModel.generate(query);
            case "COMPLEX" -> reasoningModel.generate(query);
            default -> standardModel.generate(query);
        };
    }
}
```

**Result:** 80% of queries hit the fast/cheap model. 15% hit standard. 5% hit reasoning. **Cost reduction: 5-10× vs sending everything to reasoning models.**

---

## Cost Implications

| Model | Input Cost/1M | Output Cost/1M | Thinking Tokens | Typical Query Cost |
|---|---|---|---|---|
| GPT-4o-mini | $0.15 | $0.60 | N/A | $0.001 |
| GPT-4o | $2.50 | $10.00 | N/A | $0.01 |
| o3-mini | $1.10 | $4.40 | Charged at output rate | $0.05–$0.50 |
| o3 | $10.00 | $40.00 | Charged at output rate | $0.50–$5.00 |

A single complex o3 query can cost as much as 5,000 GPT-4o-mini queries.

---

## Latency Handling

```java
// Reasoning models can take 30-60 seconds.
// Use streaming + progress indicators.

@GetMapping(value = "/reason", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> reasonWithStreaming(@RequestParam String query) {
    return Flux.create(sink -> {
        sink.next("event: thinking\ndata: Analyzing your question...\n\n");

        CompletableFuture.supplyAsync(() -> reasoningModel.generate(query))
            .thenAccept(result -> {
                sink.next("event: answer\ndata: " + result + "\n\n");
                sink.complete();
            })
            .orTimeout(90, TimeUnit.SECONDS)
            .exceptionally(ex -> {
                sink.next("event: error\ndata: Request timed out\n\n");
                sink.complete();
                return null;
            });
    });
}
```

---

## Interview-Ready Summary

- Reasoning models dynamically allocate more inference-time compute to harder problems.
- They generate internal "thinking tokens" (hidden from user) that include hypothesis generation, self-evaluation, and backtracking.
- Accuracy improves log-linearly with inference compute — doubling thinking tokens gives consistent but diminishing gains.
- Training: RL-based (o1) or distillation-based (DeepSeek-R1).
- Latency is highly variable: 1s for simple queries, 60s for complex reasoning.
- Production pattern: model router that sends 80% of queries to cheap/fast models, 5% to reasoning models.
- Cost can be 100-5000× more than standard models per query — use selectively.
