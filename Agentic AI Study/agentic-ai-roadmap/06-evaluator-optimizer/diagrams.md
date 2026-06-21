# Phase 6 — Diagrams

## 1. Evaluation Loop (from the roadmap)

The canonical evaluator-optimizer flow. An agent generates output; an LLM judge scores it 1–10. If the score clears the threshold (≥ 7) the output is accepted and returned. If it falls short, the judge's structured feedback is captured and fed into a retry, which loops back to the generator. This is the high-level "what happens at each gate" view.

```mermaid
flowchart LR
    GEN["Agent\nGenerates Output"] --> EVAL{LLM Judge\nScores 1-10}
    EVAL -->|Score ≥ 7\nPASS| OK["✅ Accept\n& Return"]
    EVAL -->|Score < 7\nFAIL| FB["📝 Structured\nFeedback"]
    FB --> RETRY["🔄 Retry with\nFeedback"]
    RETRY --> GEN

    style EVAL fill:#FFD700,color:#000
    style OK   fill:#4CAF50,color:#fff
    style RETRY fill:#FF5722,color:#fff
```

**Explanation.** Read it as a control loop. The diamond (`EVAL`) is the decision point — the quality gate. The only two ways out of the loop are the green "Accept" node (the gate passed) or, implicitly, the loop running out of retries (not drawn here — see the sequence diagram below, which makes the `max_retries` exit explicit). The orange "Retry with Feedback" node is what distinguishes this from a plain retry: feedback flows *forward* into the next generation, so each pass through `GEN` is better-informed than the last.

---

## 2. `generate_with_quality_gate` across attempts (sequence diagram)

The flowchart above shows the *shape* of the loop but hides time and the `max_retries` cap. This sequence diagram traces an actual run of `generate_with_quality_gate` over multiple attempts: the generator produces output, the judge scores it, a failing score becomes feedback that is injected into the next generation, and the loop terminates either when the score clears the threshold or when the attempt counter hits `max_retries` (in which case the last — still failing — output is returned with `success=False`).

```mermaid
sequenceDiagram
    autonumber
    actor Caller
    participant Gate as generate_with_quality_gate
    participant Gen as Generator (llm)
    participant Judge as LLM Judge (judge_output)

    Caller->>Gate: task, max_retries=3, pass_threshold=7

    Note over Gate: Attempt 1 (no feedback yet)
    Gate->>Gen: prompt = task
    Gen-->>Gate: output_1
    Gate->>Judge: judge_output(task, output_1)
    Judge-->>Gate: EvalResult(score=5, passed=False, issues, improvements)
    Note over Gate: 5 < 7 → build feedback from issues + improvements

    Note over Gate: Attempt 2 (prompt + feedback_1)
    Gate->>Gen: prompt = task + feedback_1
    Gen-->>Gate: output_2
    Gate->>Judge: judge_output(task, output_2)
    Judge-->>Gate: EvalResult(score=6, passed=False, issues, improvements)
    Note over Gate: 6 < 7 → build feedback again

    Note over Gate: Attempt 3 (prompt + feedback_2) — also the max_retries cap
    Gate->>Gen: prompt = task + feedback_2
    Gen-->>Gate: output_3
    Gate->>Judge: judge_output(task, output_3)

    alt score ≥ pass_threshold (e.g. 8)
        Judge-->>Gate: EvalResult(score=8, passed=True)
        Gate-->>Caller: {output_3, success=True, attempts=3, history}
    else still below threshold AND attempt == max_retries
        Judge-->>Gate: EvalResult(score=6, passed=False)
        Note over Gate: cap reached → stop looping
        Gate-->>Caller: {output_3, success=False, attempts=3, history}
    end
```

**Explanation.** The two-LLM-call-per-attempt cost is now visible: every attempt is one round-trip to the generator *and* one to the judge — which is exactly why the `max_retries` cap matters. Notice the score climbing (5 → 6 → 8) as the judge's feedback accumulates into the prompt; that is the optimizer working. The closing `alt` block is the loop's exit logic from §6.2: it returns on either a passing score *or* the final attempt, and the returned `success` flag tells the caller honestly whether the gate was met (`True`) or whether they're holding the best-of-a-bad-batch last attempt (`False`). The `history` list records the per-attempt scores so the improvement trajectory is auditable after the fact.
