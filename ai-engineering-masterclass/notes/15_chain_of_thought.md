# Topic 15: Chain of Thought (CoT)

> **Java Analogy:** CoT is like enabling `DEBUG` logging for an LLM — instead of getting just the final return value, you ask the model to log every intermediate computation step. The model's own output becomes its working memory, like writing intermediate results to a `StringBuilder` before returning the final answer.

---

## What This Is (Plain English)

Instead of asking "What is 17 × 24?" and getting "408" directly, you ask the model to "think step by step" and it outputs: "17 × 24 = 17 × 20 + 17 × 4 = 340 + 68 = 408." This dramatically improves accuracy on reasoning tasks because each intermediate step becomes part of the context for the next step — effectively giving the model scratch paper.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Direct prompting** | `return compute(input);` — single pass, no intermediate state |
| **Chain of Thought** | `log.debug(step1); log.debug(step2); return finalResult;` — each step logged and available for the next |
| **Scratchpad** | `StringBuilder` that accumulates intermediate reasoning |
| **Self-consistency** | Run the method 5 times with different random seeds, take the majority vote result |
| **Structured CoT** | `Step 1: ... Step 2: ... Step 3: ...` — like a template method pattern |

---

## Three Variants

### 1. Zero-Shot CoT
Just add "Let's think step by step" to ANY prompt. +10-40% accuracy on reasoning tasks.

```java
String prompt = userQuestion + "\n\nLet's think step by step.";
```

### 2. Few-Shot CoT
Provide worked examples with reasoning traces:

```java
String prompt = """
    Q: If a train travels 120km in 2 hours, what is its speed?
    A: Let me think step by step.
    Speed = Distance / Time
    Speed = 120km / 2 hours
    Speed = 60 km/h
    The answer is 60 km/h.
    
    Q: %s
    A: Let me think step by step.
    """.formatted(userQuestion);
```

### 3. Self-Consistency
Generate N independent reasoning traces, extract the final answer from each, take majority vote:

```java
public String selfConsistency(String question, int n) {
    Map<String, Integer> votes = new HashMap<>();
    for (int i = 0; i < n; i++) {
        String trace = llm.generate(question + "\nLet's think step by step.",
            Map.of("temperature", 0.7));  // Non-zero for diversity
        String answer = extractFinalAnswer(trace);
        votes.merge(answer, 1, Integer::sum);
    }
    return Collections.max(votes.entrySet(), Map.Entry.comparingByValue()).getKey();
}
```

---

## When to Use CoT vs When NOT To

| Task Type | CoT? | Why |
|---|---|---|
| Math/arithmetic | ✅ YES | Multi-step computation needs working memory |
| Code debugging | ✅ YES | Step-by-step trace of logic flow |
| Planning/scheduling | ✅ YES | Decomposition into sub-steps |
| Logical reasoning | ✅ YES | Explicit premise → conclusion chains |
| Sentiment classification | ❌ NO | Simple pattern match — CoT adds cost, may decrease accuracy |
| Entity extraction | ❌ NO | Direct pattern match is better |
| Translation | ❌ NO | Already token-by-token, CoT adds noise |

**Rule:** Use CoT for multi-step reasoning. Skip it for pattern-matching tasks.

---

## Code Bridge — Production CoT Service

```java
@Service
public class ReasoningService {
    private final ChatLanguageModel model;

    /**
     * Structured CoT for complex queries.
     * Forces the model into a step-by-step format for parseable output.
     */
    public ReasoningResult reason(String question) {
        String response = model.generate("""
            Answer the following question using structured reasoning.
            
            Format your response EXACTLY as:
            STEP 1: [First analysis step]
            STEP 2: [Second analysis step]
            STEP 3: [Third analysis step]
            CONCLUSION: [Final answer]
            CONFIDENCE: [HIGH/MEDIUM/LOW]
            
            Question: %s
            """.formatted(question));

        return parseStructuredResponse(response);
    }

    private ReasoningResult parseStructuredResponse(String response) {
        List<String> steps = new ArrayList<>();
        String conclusion = "";
        String confidence = "MEDIUM";

        for (String line : response.split("\n")) {
            if (line.startsWith("STEP")) steps.add(line.substring(line.indexOf(':') + 2));
            else if (line.startsWith("CONCLUSION:")) conclusion = line.substring(12).trim();
            else if (line.startsWith("CONFIDENCE:")) confidence = line.substring(12).trim();
        }

        return new ReasoningResult(steps, conclusion, confidence);
    }

    record ReasoningResult(List<String> steps, String conclusion, String confidence) {}
}
```

---

## Cost-Accuracy Tradeoff

| Approach | Tokens Used | Accuracy (Math) | Cost per Query |
|---|---|---|---|
| Direct answer | 50 | 60% | $0.001 |
| Zero-shot CoT | 200 | 80% | $0.004 |
| Few-shot CoT | 500 | 88% | $0.010 |
| Self-consistency (N=5) | 2500 | 93% | $0.050 |

CoT costs 4-50× more tokens but can double accuracy on reasoning tasks. Use it selectively.

---

## Interview-Ready Summary

- Chain of Thought forces the model to generate intermediate reasoning steps before the final answer.
- "Let's think step by step" alone improves accuracy by 10-40% on reasoning tasks (zero-shot CoT).
- Self-consistency generates N traces and takes the majority-vote answer — most accurate but N× cost.
- CoT works by giving the model "working memory" through its own output tokens.
- Don't use CoT for simple tasks (classification, extraction) — it can actually hurt accuracy.
- Production pattern: structured output format with STEP/CONCLUSION markers for easy parsing.
