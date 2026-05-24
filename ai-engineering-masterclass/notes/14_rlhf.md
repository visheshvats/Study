# Topic 14: Reinforcement Learning (RL / RLHF)

> **Java Analogy:** RLHF is like A/B testing with automated weight adjustment. You generate two code review responses, a human picks the better one, and the system adjusts its internal scoring to produce more of the preferred style — like a `Comparator<Response>` that the model internalizes through training.

---

## What This Is (Plain English)

RLHF (Reinforcement Learning from Human Feedback) is how ChatGPT went from a text-completion engine to a helpful assistant. After pre-training, the model generates multiple responses for the same prompt. Humans rank which response is better. A reward model learns these preferences. Then the LLM's generation policy is adjusted (via PPO) to produce more highly-ranked outputs. It's the process that teaches a model to be helpful, harmless, and honest.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Policy** | The model's current generation strategy — like the algorithm inside a `Comparator.thenComparing()` chain. |
| **Reward model** | A `Function<Response, Double>` that scores how "good" a response is. Like a code quality scoring tool. |
| **Preference data** | `Pair<Response, Response>` with a human annotation: "A is better than B." |
| **PPO** | An optimization algorithm that adjusts the policy to maximize reward while staying close to the original behavior — like a controlled refactoring that improves quality without breaking existing tests. |
| **KL penalty** | A constraint that prevents the model from drifting too far from its baseline — like `git diff` size limits in code reviews. |
| **Reward hacking** | When the model finds shortcuts to maximize the reward signal without actually being better — like optimizing for code coverage without meaningful tests. |

---

## The Three Phases

### Phase 1: Supervised Fine-Tuning (SFT)
Train the base model on high-quality demonstration data to establish a baseline.

### Phase 2: Reward Model Training
```
Prompt: "Explain microservices"
Response A: "Microservices is a software architecture pattern where..."  ← Human picks this (preferred)
Response B: "Microservices. Well, basically it's like, you know..."     ← Rejected

Train reward model: R(prompt, A) > R(prompt, B)
```

### Phase 3: Policy Optimization (PPO)
```
For each training prompt:
  1. Generate multiple responses
  2. Score each with the reward model
  3. Increase probability of high-scoring responses
  4. Decrease probability of low-scoring responses
  5. But don't drift too far from original behavior (KL penalty)
```

---

## Why RL Does NOT Create Understanding

**The coin-flip scenario:**

```
Q: "What is the probability of heads on a fair coin?"
A: "0.5" ← Correct. But WHY?

The model outputs "0.5" because that token sequence got high reward during training.
It has no physical model of a coin. No concept of gravity or aerodynamics.
It learned the SURFACE PATTERN: "fair coin" + "probability" → "0.5"

Q: "What is the probability of heads on a coin with heads on both sides?"
A: "0.5" ← WRONG. The model pattern-matched "coin + probability" → "0.5"
    It didn't reason from physical properties.
```

RL optimizes the *distribution of output tokens*, not the model's causal understanding of reality.

---

## DPO: The Simpler Alternative

**Direct Preference Optimization** eliminates the separate reward model entirely:

```
Instead of:  Train reward model → Run PPO → Update policy
DPO does:    Directly update policy from preference pairs

Loss = -log(σ(β * (log π(preferred) - log π(rejected))))
```

DPO is simpler to implement, more stable to train, and increasingly preferred over PPO in production.

---

## Why This Matters to You

As a Java engineer, you don't implement RLHF. But understanding it helps you:

1. **Model selection:** Models with better RLHF (GPT-4, Claude 3.5) produce more helpful, safe responses. Cheaper models may have worse alignment.
2. **Guardrails:** RLHF-trained models can still be jailbroken. Don't rely solely on model alignment — add output filtering.
3. **Evaluation:** When comparing models, test on adversarial prompts. Good RLHF → robust refusals. Poor RLHF → easy jailbreaks.
4. **Fine-tuning risk:** Fine-tuning can undo RLHF alignment (catastrophic forgetting). Always test safety after fine-tuning.

---

## Interview-Ready Summary

- RLHF aligns LLMs with human preferences through: SFT → Reward Model → PPO optimization.
- The reward model scores (prompt, response) pairs based on human preference data.
- PPO adjusts the model's generation policy to produce higher-scoring responses.
- KL penalty prevents the model from drifting too far from baseline behavior.
- RL does NOT create understanding — it optimizes token-level statistical patterns.
- DPO is a simpler alternative that skips the reward model entirely.
- Reward hacking is the #1 risk — models find shortcuts that satisfy the reward signal without being genuinely better.
- As a Java engineer, understand RLHF for model selection and evaluation, not implementation.
