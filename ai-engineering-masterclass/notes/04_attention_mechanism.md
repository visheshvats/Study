# Topic 4: Attention Mechanism

> **Java Analogy:** Attention is like a dynamic `JOIN` in SQL — for every word in a sentence, it computes a weighted relationship score against every other word and produces a context-enriched result. Think of it as `SELECT * FROM words w1 CROSS JOIN words w2 WHERE relevance_score(w1, w2) > threshold`.

---

## What This Is (Plain English)

The attention mechanism lets the model decide which words in a sentence are important to each other. When processing the word "apple" in "Apple reported record revenue," the model assigns high attention weights to "reported" and "revenue" — shifting "apple" from a fruit meaning to a company meaning. Without attention, every word would be processed in isolation, and the model could never disambiguate context.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Query (Q)** | The current word asking "What should I pay attention to?" — like a search key in a `Map.get()`. |
| **Key (K)** | Every other word advertising "Here's what I'm about" — like map keys. |
| **Value (V)** | The actual content each word provides — like map values. |
| **Attention score** | `Q · K` dot product = similarity between the searcher and each candidate. Like `Comparable.compareTo()`. |
| **Softmax** | Converts raw scores to a probability distribution that sums to 1. Like normalizing weights in a `WeightedRandom`. |
| **Attention output** | Weighted average of all Values — like `stream().reduce()` with custom weights. |
| **Multi-head** | Running multiple independent attention computations in parallel — like `ExecutorService.invokeAll()` with different "perspectives." |
| **Causal mask** | Ensures position `i` can only attend to positions `0..i-1`. Like a `for (int j = 0; j < i; j++)` loop — no looking ahead. |

---

## The Core Equation (Simplified)

```
For each word position:
  1. Compute Q = word × W_Q   (What am I looking for?)
  2. Compute K = word × W_K   (What do I contain?)
  3. Compute V = word × W_V   (What information do I provide?)
  4. Score = Q · K^T / √d_k   (How relevant is each other word?)
  5. Weights = softmax(Score)   (Normalize to probabilities)
  6. Output = Weights × V       (Weighted blend of all words)
```

The `√d_k` scaling prevents the dot products from becoming too large, which would make softmax output near-0/near-1 values (gradient death).

---

## The "Apple" Framework

The same word "apple" gets different contextual representations purely through attention:

| Sentence | High-Attention Words | Resulting Meaning |
|---|---|---|
| "Apple fell from the tree" | tree, fell | → Fruit |
| "Apple reported record revenue" | reported, revenue, record | → Company |
| "You are the apple of my eye" | you, my, eye | → Idiom/emotion |

No explicit rules — the model learns these attention patterns from training data.

---

## Why This Matters to You

As a Java engineer, you don't implement attention layers — but understanding them helps you:

1. **Debug prompt engineering:** If the model ignores important context, it's likely an attention issue. Placing critical information at the start or end of the prompt (where attention is strongest) improves results.
2. **Understand context limits:** Attention is $O(n^2)$ — doubling context length quadruples compute cost. This is why long-context models are expensive.
3. **Optimize API costs:** Knowing that attention weakens in the "middle" of long prompts (the "lost in the middle" problem) helps you structure inputs.
4. **Evaluate model trade-offs:** Sliding window attention (Mistral) vs full attention (GPT-4) has direct cost/quality implications.

---

## Code Bridge — Attention Intuition in Java

```java
/**
 * Simplified attention computation to build intuition.
 * In practice, this runs on GPUs inside the model — you never code this
 * in production Java. But understanding it helps you reason about LLM behavior.
 */
public class AttentionDemo {

    public static double[] attention(double[] query, double[][] keys, double[][] values) {
        int seqLen = keys.length;
        int dim = query.length;
        double scale = Math.sqrt(dim);

        // Step 1: Compute attention scores (Q · K^T / √d)
        double[] scores = new double[seqLen];
        for (int i = 0; i < seqLen; i++) {
            double dot = 0;
            for (int j = 0; j < dim; j++) {
                dot += query[j] * keys[i][j];
            }
            scores[i] = dot / scale;
        }

        // Step 2: Softmax — convert scores to probabilities
        double maxScore = Arrays.stream(scores).max().orElse(0);
        double sumExp = 0;
        double[] weights = new double[seqLen];
        for (int i = 0; i < seqLen; i++) {
            weights[i] = Math.exp(scores[i] - maxScore);
            sumExp += weights[i];
        }
        for (int i = 0; i < seqLen; i++) {
            weights[i] /= sumExp;  // Now sums to 1.0
        }

        // Step 3: Weighted sum of values
        double[] output = new double[values[0].length];
        for (int i = 0; i < seqLen; i++) {
            for (int j = 0; j < output.length; j++) {
                output[j] += weights[i] * values[i][j];
            }
        }

        return output;  // Context-enriched representation
    }
}
```

---

## Complexity — Why It Matters for Cost

| Context Length | Attention Operations | Cost Multiple |
|---|---|---|
| 4K tokens | 16 million | 1× (baseline) |
| 8K tokens | 64 million | 4× |
| 32K tokens | 1 billion | 64× |
| 128K tokens | 16 billion | 1,024× |

This $O(n^2)$ scaling is why long-context models charge significantly more and why you should always minimize context size.

---

## Interview-Ready Summary

- Attention lets each word dynamically determine how much to "attend to" every other word.
- Core formula: `Attention(Q,K,V) = softmax(QK^T / √d_k) × V`
- Q = what I'm looking for, K = what each word offers, V = the information content.
- Multi-head attention runs multiple independent attention computations in parallel.
- Complexity is O(n²) in sequence length — the primary compute bottleneck.
- Causal masking prevents the model from "seeing" future tokens during generation.
- Practical impact: put important context at the start/end of prompts, not the middle.
