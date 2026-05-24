# Topic 8: Few-Shot Prompting

> **Java Analogy:** Few-shot prompting is like passing a `List<TestCase>` as an argument to a method. You don't retrain the model — you show it example input-output pairs at runtime, and it pattern-matches against them. It's the `@Example` annotation for LLMs.

---

## What This Is (Plain English)

Instead of modifying the model, you inject 2-5 worked examples into the prompt itself. "Here's how I want you to classify these support tickets — positive, negative, neutral. Here are 3 examples. Now classify this one." The model's weights never change — the examples act as runtime instructions that steer the output format and reasoning.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Zero-shot** | Calling `classify(input)` with just instructions — no examples. Like a generic interface without implementation hints. |
| **One-shot** | Providing 1 example — like a `@see` Javadoc reference. |
| **Few-shot** | Providing 3-5 examples — like a JUnit test with `@ParameterizedTest` providing sample input-output pairs. |
| **In-context learning** | The model infers the pattern from examples within the prompt — like Java's type inference from generics. |
| **Template** | A `String.format()` pattern with placeholders for examples and the query. |

---

## When to Use

| Scenario | Approach |
|---|---|
| Task is well-defined, format is simple | Zero-shot (just instructions) |
| Model struggles with format/output structure | **Few-shot** (2-3 examples fix it) |
| Domain-specific classification | **Few-shot** with representative examples per class |
| Complex reasoning or multi-step | **Chain-of-Thought** (Topic 15) + few-shot |
| Thousands of examples, consistent behavior needed | Fine-tuning (Topic 7) |

---

## Code Bridge

### Few-Shot Template in Java

```java
@Service
public class SentimentClassifier {
    private final ChatLanguageModel model;

    private static final String FEW_SHOT_PROMPT = """
        Classify the customer feedback as POSITIVE, NEGATIVE, or NEUTRAL.
        Respond with only the label.

        Feedback: "The app is incredibly fast and easy to use!"
        Classification: POSITIVE

        Feedback: "My transaction failed three times and nobody helped."
        Classification: NEGATIVE

        Feedback: "I transferred money today using the app."
        Classification: NEUTRAL

        Feedback: "%s"
        Classification:""";

    public String classify(String feedback) {
        String prompt = String.format(FEW_SHOT_PROMPT, feedback);
        return model.generate(prompt).trim();
    }
}
```

### Dynamic Example Selection (Production Pattern)

```java
@Service
public class DynamicFewShotService {
    private final EmbeddingService embeddingService;
    private final List<Example> exampleBank;  // Pre-embedded examples
    private final ChatLanguageModel model;

    /**
     * Selects the most relevant examples based on similarity to the query.
     * This outperforms static examples by 10-30%.
     */
    public String classifyWithDynamicExamples(String query, int numExamples) {
        // Find most similar examples from the bank
        float[] queryVector = embeddingService.embed(query);
        List<Example> selected = exampleBank.stream()
            .map(ex -> new ScoredExample(ex, cosineSimilarity(queryVector, ex.embedding())))
            .sorted(Comparator.comparingDouble(ScoredExample::score).reversed())
            .limit(numExamples)
            .map(ScoredExample::example)
            .toList();

        // Build prompt with selected examples
        StringBuilder prompt = new StringBuilder("Classify the feedback:\n\n");
        for (Example ex : selected) {
            prompt.append("Feedback: \"%s\"\nClassification: %s\n\n"
                .formatted(ex.text(), ex.label()));
        }
        prompt.append("Feedback: \"%s\"\nClassification:".formatted(query));

        return model.generate(prompt.toString()).trim();
    }

    record Example(String text, String label, float[] embedding) {}
    record ScoredExample(Example example, double score) {}
}
```

### Using LangChain4j Structured Prompts

```java
@AiService
public interface TicketRouter {

    @SystemMessage("""
        Route support tickets to the correct department.
        
        Examples:
        - "My card was stolen" → FRAUD
        - "I want to increase my FD" → INVESTMENTS
        - "Unable to login to app" → TECHNICAL
        - "What's the interest rate?" → GENERAL
        """)
    @UserMessage("Route this ticket: {{ticket}}")
    String routeTicket(@V("ticket") String ticket);
}
```

---

## Best Practices

1. **Order matters.** Place the most relevant example *last* (immediately before the query). LLMs attend more strongly to recent context.

2. **Cover all classes.** If you have 3 labels, include at least 1 example per label. Unrepresented labels get predicted less often.

3. **Consistent formatting.** Use identical delimiters, labels, and structure across all examples. Inconsistency confuses the model.

4. **Don't overdo it.** 3-5 examples is the sweet spot. Beyond 8, returns diminish and you waste context window space.

5. **Token budget.** Each example consumes tokens. 5 examples × 50 tokens each = 250 tokens of your context budget gone.

---

## Interview-Ready Summary

- Few-shot prompting injects example input-output pairs into the prompt at runtime.
- No model training or weight updates — purely in-context learning.
- 3-5 examples is optimal. Beyond 8, diminishing returns.
- Dynamic example selection (using embeddings) outperforms static examples by 10-30%.
- Example order matters — most relevant example goes last.
- Use few-shot for format/classification tasks; use fine-tuning for consistent large-scale behavior.
