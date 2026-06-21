# Phase 6 — Evaluator & Optimizer

> **Duration:** 1 week
> **Goal:** Build self-improving AI workflows with quality gates.

---

## Why this matters

In your Spring Boot world, you never shipped a service that *might* return garbage and just hoped for the best. You wrapped inputs in `@Validated`, you asserted invariants, you had a CI pipeline that ran a test gate and **refused to merge** if a single test went red. The output of your code was deterministic: the same input produced the same output, and a test that passed yesterday passed today.

An LLM breaks that assumption completely. Call the same model with the same prompt twice and you can get two different answers — one excellent, one subtly wrong. There is no compiler to catch a hallucinated API method, no type system to reject a vague claim, no test that fails when the model invents a fact. The output is **non-deterministic**, and that is terrifying if you intend to put it in front of a customer.

So we rebuild the safety net we lost. Phase 6 is about putting a **quality gate** in front of LLM output — the exact same instinct as a CI test gate or a code-review bot that blocks a merge. We do it in three moves:

1. **LLM-as-Judge** — a second model call that *scores* the output against criteria and returns a typed, validated verdict (think: a `@Validated` DTO plus assertion checks, but where the "assertion" is itself an LLM).
2. **Self-improving retry loop** — if the score is below threshold, we feed the judge's specific complaints back into the generator and try again (think: Spring Retry with a predicate, where the predicate is "score >= 7").
3. **Hallucination detection** — a grounding check that asks "is this claim actually backed by the source?" and labels it SUPPORTED / INFERRED / UNSUPPORTED (think: a referential-integrity constraint between an answer and its evidence).

> ⚠️ **The source roadmap warns: "This is where 90% of developers stop. You must not."** Anyone can get a model to *produce* text. The engineers who get trusted with production are the ones who can prove the text is good *before* it ships. Skipping this phase is how you end up with the demo that wows the room and the incident that wakes you at 3am.

---

## 6.1 LLM-as-Judge

The core idea: use one LLM call to *generate* output, and a **separate** LLM call to *evaluate* it. The evaluator ("judge") is given the original task, the candidate output, and a set of criteria, and it returns a score plus structured commentary.

The trap here is that an LLM, left alone, will hand you a paragraph of prose: *"This is a pretty good answer, though it could be clearer in places..."*. You cannot branch on a paragraph. You need a number you can compare against a threshold and a list of issues you can feed back into a retry. So we force the judge's output into a **typed schema**.

### The `EvalResult` schema = a validated DTO

```python
from typing import List
from pydantic import BaseModel, Field

class EvalResult(BaseModel):
    score: int = Field(ge=1, le=10, description="Quality score 1-10")
    passed: bool = Field(description="True if score >= 7")
    strengths: List[str] = Field(description="What the output does well")
    issues: List[str] = Field(description="Specific problems found")
    improvements: List[str] = Field(description="Concrete suggestions")
```

This is *exactly* a DTO with bean validation. In Spring you'd write:

```java
public record EvalResult(
    @Min(1) @Max(10) int score,   // == Field(ge=1, le=10)
    boolean passed,
    List<String> strengths,
    List<String> issues,
    List<String> improvements
) {}
```

`Field(ge=1, le=10)` is `@Min(1) @Max(10)`. Pydantic validates on construction the same way Hibernate Validator validates on `@Valid`. If the model tries to return `score=15`, Pydantic raises a `ValidationError` — the bad value never enters your program.

### `PydanticOutputParser` = the Jackson `ObjectMapper` for LLM text

The model speaks text, not objects. `PydanticOutputParser` bridges the gap in two directions:

```python
from langchain_core.output_parsers import PydanticOutputParser

eval_parser = PydanticOutputParser(pydantic_object=EvalResult)
```

- `eval_parser.get_format_instructions()` generates a chunk of text you paste into the prompt that tells the model *exactly* what JSON shape to emit (the field names, types, and a JSON-schema description). This is like publishing your DTO's contract so the caller knows what to send.
- `eval_parser.parse(text)` takes the model's raw string response, extracts the JSON, and deserializes-and-validates it into a real `EvalResult`. This is `objectMapper.readValue(json, EvalResult.class)` followed by bean validation, in one step.

### The judge function

```python
def judge_output(task: str, output: str,
                 criteria: str = "accuracy, completeness, clarity, conciseness") -> EvalResult:
    judge_prompt = f"""You are a strict quality evaluator. Be objective and critical.

TASK:
{task}

OUTPUT TO EVALUATE:
{output}

EVALUATION CRITERIA: {criteria}

Score 1-10 (7+ = acceptable for production).
Penalize: vague claims, missing information, poor structure, hallucinations.

{eval_parser.get_format_instructions()}"""

    response = llm.invoke([HumanMessage(content=judge_prompt)])
    try:
        return eval_parser.parse(response.content)
    except Exception:
        return EvalResult(
            score=4, passed=False,
            strengths=[], issues=["Evaluation parsing failed"],
            improvements=["Retry"],
        )
```

Two design choices worth lingering on:

1. **"Be strict and critical."** A judge that praises everything is useless — it's a rubber-stamp code reviewer who approves every PR. You deliberately bias the prompt toward criticism so the gate actually catches problems.
2. **The `try/except` fallback.** What happens if the model returns malformed JSON and `parse()` throws? In Java you'd never let a `JsonProcessingException` propagate and crash a request thread — you'd catch it and return a sensible default. Here we catch the parse failure and return a *failing* `EvalResult` (score 4, `passed=False`). The philosophy is **fail closed**: if we can't verify quality, we treat the output as not-yet-good-enough rather than waving it through.

---

## 6.2 Self-improving retry loop (the "optimizer")

The judge alone is a gate — it says yes or no. The **evaluator-optimizer** pattern closes the loop: generate → evaluate → if it fails, turn the judge's complaints into feedback → retry with that feedback → repeat until it passes or you run out of attempts.

```python
def generate_with_quality_gate(task: str, max_retries: int = 3,
                               pass_threshold: int = 7) -> dict:
    history = []
    feedback = ""

    for attempt in range(1, max_retries + 1):
        prompt = task
        if feedback:
            prompt += f"\n\n⚠️ IMPORTANT — Improve based on this feedback:\n{feedback}"

        output = llm.invoke([HumanMessage(content=prompt)]).content
        evaluation = judge_output(task, output)
        history.append({"attempt": attempt, "score": evaluation.score})

        if evaluation.passed or attempt == max_retries:
            return {"output": output, "evaluation": evaluation,
                    "attempts": attempt, "history": history,
                    "success": evaluation.passed}

        feedback = (
            "Issues found:\n" + "\n".join(f"- {i}" for i in evaluation.issues) +
            "\n\nSuggestions:\n" + "\n".join(f"- {s}" for s in evaluation.improvements)
        )
```

### The Java analogy: Spring Retry with a predicate

You've written this loop before, just with a different body. Spring Retry lets you declare "retry this call up to N times *while* a condition holds":

```java
@Retryable(retryFor = QualityTooLowException.class, maxAttempts = 3)
public String generate(String task) { ... }
```

The mapping is one-to-one:

| Spring Retry concept | Here |
| --- | --- |
| `maxAttempts = 3` | `max_retries=3` (the **cap** — non-negotiable) |
| retry predicate (`retryFor` / `RetryPolicy`) | `if not evaluation.passed` |
| the thing that succeeds | `evaluation.passed` (score >= threshold) |
| exponential backoff between tries | (omitted here; you'd add it for rate limits) |

The crucial difference from a dumb retry: a Spring `@Retryable` re-runs the *same* call hoping a transient failure clears. Our loop is smarter — it **changes the input** each time. On retry the prompt now carries the judge's specific issues and suggestions. This is what makes it an *optimizer*, not just a retrier: each attempt is informed by why the last one failed. It is gradient descent done in natural language — the feedback is the gradient, pointing the generator toward a better answer.

### The two parameters that govern the loop

- **`max_retries`** — the hard cap. Without it you have an infinite loop, and since every iteration is two paid LLM calls (generate + judge), an infinite loop is a runaway bill. This is the single most important guardrail in the whole pattern.
- **`pass_threshold`** — how good is "good enough." Set it to 7/10 and you accept solid-but-imperfect work. Set it to 10 and almost nothing passes — you'll exhaust `max_retries` every time and ship the last (failing) attempt anyway. Threshold tuning is a real engineering decision, not a default to ignore.

Note the exit condition: `if evaluation.passed or attempt == max_retries`. We always return on the last attempt, even if it failed — but we return `"success": evaluation.passed` so the caller *knows* whether the gate was actually met. We never silently pretend a failing output passed.

---

## 6.3 Hallucination detection (grounding)

A high judge score tells you the answer is well-written and on-topic. It does **not** tell you the answer is *true*. A model can produce a beautifully structured, perfectly clear paragraph that confidently states a fact it invented. In RAG especially, the danger is the model "filling in" detail that isn't in the retrieved documents.

Hallucination detection is a **grounding check**: take a claim and the source context it's supposed to be based on, and ask whether the claim is actually backed by that context.

```python
def check_hallucination(claim: str, source_context: str) -> dict:
    prompt = f"""Determine if this claim is supported by the provided context.

CLAIM: {claim}

CONTEXT: {source_context}

Is the claim:
A) SUPPORTED — directly stated in context
B) INFERRED — reasonably inferred from context
C) UNSUPPORTED — not in context or contradicts it

Return JSON only:
{{"verdict": "SUPPORTED"|"INFERRED"|"UNSUPPORTED", "reason": "brief explanation"}}"""

    result = llm.invoke([HumanMessage(content=prompt)])
    return json.loads(re.sub(r'```json|```', '', result.content).strip())
```

The three-way verdict is the important nuance — it is not a binary true/false:

- **SUPPORTED** — the claim is directly stated in the context. Highest confidence. Ship it.
- **INFERRED** — not stated verbatim, but a reasonable deduction from what *is* there. Usually acceptable, but you may want to flag it depending on how risk-averse the domain is (fine for a help article, maybe not for a medical or financial statement).
- **UNSUPPORTED** — not in the context, or actively contradicts it. **This is the hallucination.** Do not ship it as fact.

The Java analogy is a **referential-integrity / foreign-key constraint**: an answer (child row) must point to evidence (parent row) that actually exists. UNSUPPORTED is the orphaned record — a claim with no backing source. You wouldn't let your DB persist a foreign key that references nothing; don't let your RAG pipeline emit a claim that references nothing.

The wrapper degrades gracefully rather than throwing the answer away:

```python
def rag_with_hallucination_check(query: str, retriever) -> str:
    docs = retriever.invoke(query)
    context = "\n".join(d.page_content for d in docs)
    answer = rag_chain.invoke(query)

    verdict = check_hallucination(answer, context)
    if verdict["verdict"] == "UNSUPPORTED":
        return f"[⚠️ Low confidence] {answer}"   # warn, don't hide
    return answer
```

Note the regex scrub `re.sub(r'```json|```', '', ...)` before `json.loads`. Models love to wrap JSON in Markdown code fences. Stripping the fences first is the difference between a clean parse and a `JSONDecodeError`. (A `PydanticOutputParser`, as in 6.1, is the more robust choice — `json.loads` here is the lightweight version.)

---

## ⚠️ Common Java-dev mistakes

- **Judge parsing failure with no fallback.** You assume the judge always returns clean JSON, call `eval_parser.parse()` with no `try/except`, and the first malformed response takes down the request thread. Always catch the parse error and **fail closed** to a failing `EvalResult` — never let an unverified output sneak through because the verifier crashed.
- **Same model as judge and generator, trusted blindly.** Convenient, but the model that wrote the answer is biased toward thinking the answer is good — like the author reviewing their own PR. Worse, the judge is *also* an LLM and *also* fallible: it can score a hallucination 9/10. Treat the judge's verdict as a signal, not gospel. Prefer a different (often cheaper, e.g. Haiku) model as judge.
- **No `max_retries` cap.** "Loop until it passes" sounds fine until the threshold is unreachable and you burn an infinite number of paid calls. Every iteration is *two* LLM calls. Always cap the loop. This is your `maxAttempts`.
- **Threshold set so high nothing passes.** `pass_threshold=10` feels rigorous but means every run exhausts retries and ships the last failing attempt anyway — you paid 6 LLM calls to deliver a 6/10 answer with `success=False`. Pick a realistic bar (7 is the roadmap default) and watch what actually passes.
- **Not feeding structured feedback back into the retry prompt.** If your retry just re-runs the same prompt (a plain Spring `@Retryable`), the generator has no reason to do better and you're rolling dice. The whole point of the *optimizer* is that the judge's `issues` and `improvements` become the next prompt. Skip that and you've built an expensive random retry.
- **Ignoring that the judge is also fallible.** The judge can hallucinate a perfect score, miss a real bug, or parse-fail. Don't build a system whose only safety net is a single LLM call you never audit. Log the verdicts, sample them, and for high-stakes flows consider a second judge or a human spot-check. The gate reduces risk; it does not eliminate it.

---

## Key terms

- **LLM-as-judge** — using a (preferably separate) LLM call to evaluate the output of another LLM against explicit criteria, returning a score and commentary.
- **Evaluator-optimizer** — the pattern of looping generate → evaluate → feed feedback back → regenerate, so output improves across attempts. The evaluator scores; the optimizer (the loop) drives improvement.
- **Quality gate** — a checkpoint that output must pass before being accepted/returned, analogous to a CI test gate that blocks a merge.
- **Pass threshold** — the minimum score considered "good enough" to accept (e.g. 7/10). The decision boundary the gate compares against.
- **`PydanticOutputParser`** — LangChain utility that (a) generates format instructions describing the target schema for the prompt, and (b) parses + validates the model's text response into a typed Pydantic object. The Jackson `ObjectMapper` + bean validation of the LLM world.
- **Structured feedback** — the judge's `issues` and `improvements` returned as typed lists, suitable for injecting verbatim into the next generation prompt.
- **Retry loop** — the bounded iteration (capped by `max_retries`) that regenerates until the output passes or attempts are exhausted.
- **Hallucination** — content the model states as fact that is not grounded in any provided source (or contradicts it); confidently wrong output.
- **Grounding** — the property of a claim being backed by actual source evidence; "grounding check" verifies that property.
- **SUPPORTED / INFERRED / UNSUPPORTED** — the three-way grounding verdict. SUPPORTED = directly in the source; INFERRED = reasonable deduction from the source; UNSUPPORTED = not in the source or contradicts it (the hallucination).
