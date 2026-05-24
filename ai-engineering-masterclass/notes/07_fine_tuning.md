# Topic 7: Fine-Tuning

> **Java Analogy:** Fine-tuning is like extending a well-tested base class. The pre-trained model is `AbstractLanguageModel` with broad capabilities. Fine-tuning is writing `MedicalAssistantModel extends AbstractLanguageModel` — you override specific behaviors while inheriting everything else. LoRA fine-tuning is even more targeted: it's like using the Decorator pattern to wrap specific methods without touching the original class.

---

## What This Is (Plain English)

Fine-tuning takes a general-purpose LLM and specializes it for your domain by training it on curated (question, answer) pairs. Pre-training teaches the model *language*. Fine-tuning teaches it *behavior* — how to respond in a specific format, tone, or domain (medical, legal, banking, customer support). It's the difference between hiring a college graduate (pre-trained) and training them for your specific job (fine-tuned).

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Base model (pre-trained)** | `AbstractLanguageModel` — broad capabilities, no domain specialization. |
| **Full fine-tuning** | Rewriting the entire class. All weights updated. Expensive. |
| **LoRA** | Decorator pattern — wrap specific layers with lightweight adapters. Original weights frozen. |
| **QLoRA** | Decorator on a compressed class — base model quantized to INT4, adapters in FP16. |
| **Training dataset** | A JSONL file of (system, user, assistant) tuples — like test fixtures that define desired behavior. |
| **Overfitting** | Like hard-coding answers to specific test inputs instead of writing generalizable logic. |
| **Catastrophic forgetting** | Like overriding `hashCode()` in a subclass and accidentally breaking `equals()` contract. |
| **Loss masking** | Only computing loss on the assistant's response tokens — like `@Test` annotations that mark which methods are under test. |

---

## When to Fine-Tune vs When NOT To

| Situation | Best Approach |
|---|---|
| Model doesn't know your domain | **RAG** (Topic 9) — inject knowledge at runtime |
| Model knows the content but wrong format/tone | **Fine-tuning** — teach new behavioral patterns |
| < 200 examples available | **Few-shot prompting** (Topic 8) — examples in the prompt |
| 500–100K examples, specific behavior | **LoRA fine-tuning** — best cost/quality balance |
| Need complete model control | **Full fine-tuning** — expensive but maximum customization |

**Rule of thumb:** Try prompting first → try RAG → try fine-tuning, in that order. Fine-tuning is the last resort, not the first.

---

## LoRA — The Technique You'll Actually Use

**Problem:** Full fine-tuning a 7B model requires ~56GB GPU memory (weights + optimizer states + gradients).

**LoRA solution:** Freeze all original weights. Add tiny trainable matrices (adapters) to each attention layer:

```
Original: output = input × W           (W is 4096×4096 = 16M parameters, frozen)
LoRA:     output = input × W + input × B × A   (B is 4096×8, A is 8×4096 = 65K params, trainable)
```

- **Rank 8 LoRA on a 7B model:** ~4M trainable parameters (0.06% of total)
- **Memory:** 7B model fits in 4-6 GB GPU at INT4. LoRA adapters add ~16MB.
- **Result:** Fine-tune a 7B model on a single consumer GPU (RTX 3060 12GB)

---

## Fine-Tuning Data Format

### JSONL (Standard Format)

```jsonl
{"messages":[{"role":"system","content":"You are a banking support agent."},{"role":"user","content":"My UPI payment failed but money got debited."},{"role":"assistant","content":"I understand your concern about the failed UPI transaction. Let me help you:\n\n1. The debited amount will auto-refund within 24-48 hours\n2. If not refunded, please raise a complaint via the app\n3. Note down the transaction reference number\n\nWould you like me to help you raise a dispute?"}]}
{"messages":[{"role":"system","content":"You are a banking support agent."},{"role":"user","content":"How do I increase my credit card limit?"},{"role":"assistant","content":"To request a credit card limit increase:\n\n1. Log into the mobile app → Cards → Manage Limit\n2. Submit an increase request with updated income proof\n3. Processing takes 3-5 business days\n\nEligibility depends on your payment history and credit score. Would you like detailed steps for the app?"}]}
```

### Dataset Quality Checklist

- [ ] Minimum 500 examples (below this, use few-shot prompting instead)
- [ ] Consistent format and tone across all examples
- [ ] Diverse scenarios — cover edge cases, not just happy paths
- [ ] 10-20% held out for validation
- [ ] No contradictions between examples
- [ ] System prompt consistent across all entries

---

## Java Ecosystem for Fine-Tuning

| Tool | Role |
|---|---|
| **Unsloth** | Python library for fast LoRA/QLoRA fine-tuning. You'll use this for the actual training (sorry, it's Python). |
| **HuggingFace Transformers** | The PyTorch ecosystem for model training. Industry standard. |
| **OpenAI Fine-Tuning API** | Upload JSONL → get a fine-tuned GPT model back. No GPUs needed. |
| **LangChain4j** | Java framework that calls your fine-tuned model via API — same interface as base models. |
| **Spring AI** | Same. Your Java code doesn't change — just point to the new model ID. |

### Calling a Fine-Tuned Model (Java)

```java
// The ONLY thing that changes is the model name
ChatLanguageModel model = OpenAiChatModel.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .modelName("ft:gpt-4o-mini:my-org:banking-v2:abc123")  // ← Fine-tuned model ID
    .temperature(0.3)
    .build();

String response = model.generate("My UPI payment failed");
// → Responds in your trained banking support format
```

### Preparing Training Data (Java)

```java
/**
 * Converts your existing support ticket database
 * into fine-tuning JSONL format.
 */
@Service
public class TrainingDataExporter {

    public void exportToJsonl(List<SupportTicket> tickets, Path outputPath) {
        try (var writer = Files.newBufferedWriter(outputPath)) {
            for (SupportTicket ticket : tickets) {
                var json = Map.of("messages", List.of(
                    Map.of("role", "system", "content", SYSTEM_PROMPT),
                    Map.of("role", "user", "content", ticket.getCustomerQuery()),
                    Map.of("role", "assistant", "content", ticket.getResolvedResponse())
                ));
                writer.write(objectMapper.writeValueAsString(json));
                writer.newLine();
            }
        }
    }
}
```

---

## Pitfalls for Java Engineers

1. **"I'll fine-tune for everything"** — No. Fine-tuning is for behavior, not knowledge. Use RAG for injecting facts.
2. **Small datasets** — Below 500 examples, few-shot prompting beats fine-tuning. Below 200, don't even try.
3. **Overfitting** — If training loss drops to 0 but validation loss increases, the model memorized your examples.
4. **Catastrophic forgetting** — After fine-tuning on banking data, the model may forget how to write code. Mix 10% general data into your training set.
5. **Evaluation** — Always test on held-out examples. Manual review of 50+ outputs is mandatory.

---

## Interview-Ready Summary

- Fine-tuning adjusts pre-trained model weights on curated (input, output) pairs.
- It teaches *behavior* (format, tone, domain compliance), not *knowledge* (use RAG for that).
- LoRA freezes original weights and adds tiny adapter matrices — trains 0.06% of parameters.
- QLoRA = INT4 base model + FP16 LoRA adapters — fine-tune 70B models on a single GPU.
- Data format is JSONL with `system`, `user`, `assistant` roles.
- Minimum ~500 examples. Quality >> quantity. Always hold out 10-20% for validation.
- As a Java engineer, you prepare data in Java, train with Python tools (Unsloth/HuggingFace), and consume the model via the same API/SDK as before.
