# Topic 5: Self-Supervised Learning

> **Java Analogy:** Self-supervised learning is like building a massive test suite where the tests are auto-generated from the source code itself. Imagine a framework that takes your entire Java codebase, randomly deletes method bodies, and trains a code-completion engine to predict the missing code from the surrounding context — no human-written tests needed.

---

## What This Is (Plain English)

Self-supervised learning (SSL) is how LLMs learn language without any human-labeled data. The trick: the training data *is* the label. Take a sentence, hide a word, and train the model to predict what was hidden. "The cat sat on the [MASK]" → the model learns to predict "mat." Do this with trillions of sentences, and the model absorbs grammar, facts, reasoning patterns, and even code conventions — all without anyone manually annotating a single example.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Masked Language Modeling (BERT-style)** | Like removing random method names from code and training an autocomplete engine to predict them from surrounding code. |
| **Causal Language Modeling (GPT-style)** | Like a `StringBuilder` that can only `append()` — predicts the next character without ever looking ahead. |
| **Training loss (cross-entropy)** | Like `assertEquals(expectedToken, predictedToken)` — measures how wrong the prediction was, but as a continuous probability score. |
| **Training corpus** | Like scanning all of GitHub, Stack Overflow, Wikipedia, and every book ever written into one massive `InputStream`. |
| **Epoch** | One complete pass through the training data — like running your full test suite once. |
| **Pre-training** | Building a generic engine (like the JVM). **Fine-tuning** = customizing for a specific app (like Spring Boot config). |

---

## Two Main Approaches

### 1. Masked Language Modeling (MLM) — BERT-style

```
Input:  "The [MASK] sat on the mat"
Target: "The _cat_ sat on the mat"
```

- Hide ~15% of tokens randomly
- Model sees ALL surrounding context (bidirectional)
- Good for: understanding, classification, NER, sentiment
- Used by: BERT, RoBERTa, DeBERTa

### 2. Causal Language Modeling (CLM) — GPT-style

```
Input:  "The cat sat on the"
Target: "mat" (predict next token)
```

- Predict the next token left-to-right
- Model can only see PAST tokens (unidirectional via causal mask)
- Good for: text generation, conversation, code completion
- Used by: GPT-4, Claude, LLaMA, Gemini

**GPT-style won** because it naturally supports *generation* — the model inherently produces text token by token, which is what chatbots need.

---

## Why This Matters to You

1. **Understanding model capabilities:** Pre-training determines what a model "knows." If a model was pre-trained before 2024, it doesn't know about events after 2024 — that's a knowledge cutoff, not a bug.

2. **Data quality intuition:** Models trained on cleaner data (filtered Stack Overflow, curated textbooks) outperform models trained on 5× more raw web scrape. This is directly analogous to the "garbage in, garbage out" principle you apply to database design.

3. **Fine-tuning decisions:** You need to understand that pre-training gives the model *language ability*, and fine-tuning gives it *task behavior*. You don't fine-tune for language — you fine-tune for format, tone, and domain compliance.

---

## The Scale of Pre-training

| Model | Training Data | Tokens | Training Cost (est.) | GPU-Hours |
|---|---|---|---|---|
| GPT-3 | 570 GB text | 300B | $4.6M | 355 GPU-years |
| LLaMA 2 70B | 2T tokens | 2T | $25M+ | 1.7M GPU-hours |
| LLaMA 3 405B | 15T+ tokens | 15T+ | $100M+ | Unknown |
| GPT-4 | Unknown | Unknown | $100M+ (rumored) | Unknown |

**You will never pre-train a model.** This is done by labs with thousands of GPUs. Your job starts at the fine-tuning or API-integration layer.

---

## Code Bridge — Conceptual Masking in Java

```java
/**
 * Demonstrates the self-supervised masking concept.
 * This is NOT real ML training — it's the conceptual pattern
 * that helps you understand what happens inside a pre-training pipeline.
 */
public class SelfSupervisedDemo {

    private static final double MASK_PROBABILITY = 0.15;
    private static final String MASK_TOKEN = "[MASK]";

    record MaskedExample(List<String> maskedTokens, Map<Integer, String> targets) {}

    public static MaskedExample createMaskedExample(List<String> tokens) {
        List<String> masked = new ArrayList<>(tokens);
        Map<Integer, String> targets = new HashMap<>();
        Random rng = new Random();

        for (int i = 0; i < tokens.size(); i++) {
            if (rng.nextDouble() < MASK_PROBABILITY) {
                targets.put(i, tokens.get(i));  // Save the answer

                double r = rng.nextDouble();
                if (r < 0.80) {
                    masked.set(i, MASK_TOKEN);       // 80%: replace with [MASK]
                } else if (r < 0.90) {
                    masked.set(i, getRandomToken());  // 10%: random token
                }
                // 10%: keep unchanged (model must still predict it)
            }
        }
        return new MaskedExample(masked, targets);
    }

    // Training loop (pseudocode — actual training is in PyTorch/JAX)
    // for each batch:
    //     maskedInput = mask(originalText)
    //     predictions = model.forward(maskedInput)  // float[] per position
    //     loss = crossEntropy(predictions, targets)  // How wrong was it?
    //     model.backward(loss)                       // Compute gradients
    //     optimizer.step()                           // Update weights
}
```

---

## The 80/10/10 Strategy — Why?

| Action | Percentage | Reason |
|---|---|---|
| Replace with `[MASK]` | 80% | Forces the model to learn to predict from context |
| Replace with random token | 10% | Makes the model robust to noisy/corrupted input |
| Keep original | 10% | Forces the model to represent ALL positions, not just masked ones |

If you always used `[MASK]`, the model would learn to only predict at `[MASK]` positions and would behave strangely on normal text during inference.

---

## Interview-Ready Summary

- Self-supervised learning trains models on unlabeled text by creating prediction tasks from the data itself.
- Two approaches: MLM (mask & predict, bidirectional — BERT) and CLM (next-token prediction, unidirectional — GPT).
- GPT-style CLM dominates because it naturally supports text generation.
- Pre-training happens at massive scale (trillions of tokens, millions of GPU-hours, $100M+).
- As a Java engineer, you never pre-train — you work at the API/fine-tuning layer.
- Data quality matters more than data quantity (the Chinchilla finding).
- The model's knowledge cutoff is determined by when pre-training data was collected.
