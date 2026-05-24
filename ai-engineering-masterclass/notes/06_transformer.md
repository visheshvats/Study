# Topic 6: The Transformer

> **Java Analogy:** A Transformer is like a pipeline of `Filter` stages in a servlet filter chain — each layer takes input, enriches it (via attention + feedforward), adds the original input back (residual connection), and passes it to the next stage. Stack 32-96 of these stages, and raw tokens are progressively refined into rich semantic representations.

---

## What This Is (Plain English)

The Transformer is the architecture behind every major LLM (GPT, Claude, Gemini, LLaMA). It's a stack of identical processing layers, each containing two operations: (1) attention — lets every word look at every other word, and (2) feedforward network — processes each word independently through a neural network. The magic is in stacking these layers: lower layers learn syntax, middle layers learn semantics, upper layers learn reasoning patterns.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Transformer layer** | A `Filter` in a filter chain — processes, enriches, passes on. |
| **Multi-head attention** | `ExecutorService.invokeAll()` — multiple attention computations run in parallel, each looking at different relationship patterns. |
| **Feedforward network (FFN)** | A `Function<float[], float[]>` — two matrix multiplications with a GELU activation in between. This is where factual knowledge is stored. |
| **Residual connection** | `output = input + process(input)` — like a `try-catch` that always preserves the original data. Prevents information loss in deep networks. |
| **Layer normalization** | Like `Collections.sort()` applied to each vector — normalizes the scale of activations to prevent training instability. |
| **32-layer stack** | Like 32 nested `stream().map()` transformations — each one refines the representation further. |

---

## Transformer Block Structure

```
Input Tokens (float[seqLen][dim])
    │
    ▼
┌─────────────────────────────┐
│  Layer Norm                  │
│  Multi-Head Self-Attention   │ ← Every token attends to every other token
│  + Residual Connection       │ ← output = input + attention(input)
├─────────────────────────────┤
│  Layer Norm                  │
│  Feedforward Network (FFN)   │ ← Two linear layers + GELU activation
│  + Residual Connection       │ ← output = input + ffn(input)
└─────────────────────────────┘
    │
    ▼
    (Repeat 32–96 times)
    │
    ▼
Output Logits → Softmax → Next Token Probability
```

---

## Key Components Deep Dive

### Residual Connections — Why They Matter

```java
// Without residual: information degrades through 96 layers
output = layer96(layer95(...layer2(layer1(input))));  // Input signal is lost

// With residual: original signal is always preserved
output = input + layer1(input);
output = output + layer2(output);  // Original input still accessible
```

This is identical in principle to why `Optional.orElse(default)` preserves a fallback — the residual ensures the original representation is never completely destroyed.

### Feedforward Network — The Knowledge Store

```java
// Simplified FFN: expand → activate → compress
// dim=4096, ff_dim=16384 (4× expansion)
float[] hidden = matmul(input, W1);     // 4096 → 16384 (expand)
hidden = gelu(hidden);                   // Non-linear activation
float[] output = matmul(hidden, W2);     // 16384 → 4096 (compress)
```

**Critical insight:** Research shows the FFN layers store most factual knowledge. Attention *routes* information; FFN *transforms* it. When you fine-tune a model on medical data, you're primarily updating FFN weights.

### GELU Activation

```java
// GELU ≈ x * sigmoid(1.702 * x)
// Smoother than ReLU — no hard cutoff at zero
public static double gelu(double x) {
    return 0.5 * x * (1 + Math.tanh(
        Math.sqrt(2 / Math.PI) * (x + 0.044715 * x * x * x)
    ));
}
```

---

## Why This Matters to You

1. **Context window limits:** The $O(n^2)$ attention cost explains why API pricing increases with context length and why 128K context models cost more.

2. **Model size selection:** More layers + wider dimensions = more capable but slower. A 7B model (32 layers, dim 4096) vs 70B (80 layers, dim 8192) — the trade-off is speed vs quality.

3. **LoRA fine-tuning targets:** When you use LoRA adapters (Topic 7), you're injecting trainable parameters into the attention projection matrices. Understanding where attention vs FFN sits helps you choose which layers to target.

4. **Hardware requirements:** Each layer's weights must fit in GPU memory. A 70B model in FP16 needs 140GB VRAM — that's 2× A100 GPUs. Quantization (Topic 20) addresses this.

---

## Transformer Model Sizes

| Model | Layers | Hidden Dim | Heads | FFN Dim | Total Params |
|---|---|---|---|---|---|
| Phi-3 (3.8B) | 32 | 3072 | 32 | 8192 | 3.8B |
| LLaMA-3 7B | 32 | 4096 | 32 | 11008 | 6.7B |
| LLaMA-3 70B | 80 | 8192 | 64 | 28672 | 70B |
| GPT-4 (est.) | 120 | 12288 | 96 | 49152 | ~1.8T (MoE) |

---

## Interview-Ready Summary

- The Transformer is a stack of identical layers, each containing multi-head attention + feedforward network.
- Attention has O(n²) complexity — the fundamental compute bottleneck for long contexts.
- Residual connections prevent information loss through deep layer stacks.
- FFN layers store factual knowledge; attention layers route contextual information.
- GELU replaced ReLU as the standard activation for smoother gradients.
- Modern models use Pre-Norm (normalize before the sub-layer) for training stability.
- As a Java engineer, you don't build Transformers — but understanding the architecture helps you reason about model capabilities, costs, and limitations.
