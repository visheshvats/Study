# Phase 6 — Exercises

Work these in order; each builds on the last. No solutions provided — that's the point. Run everything against the offline mock first (`USE_MOCK = True`), then, if you have a key, flip to a real model and watch the scores move.

---

### Exercise 1 — Tighten the judge's contract (easy)

Extend `EvalResult` with two new validated fields: `confidence: float` constrained to `0.0–1.0`, and `category: Literal["factual", "creative", "code"]`. Re-generate the parser's format instructions and confirm the judge prompt now asks for the new fields.

> Hint: `Field(ge=0.0, le=1.0)` for the float; `typing.Literal` gives you a Pydantic-enforced enum.

---

### Exercise 2 — A judge parse fallback you can trust (easy)

Write a `safe_judge(task, output)` that wraps `judge_output` and, on parse failure, logs the raw model response *before* returning the fail-closed `EvalResult`. Prove it works by feeding the parser a deliberately malformed string and confirming you get score 4 / `passed=False` and a log line — not an exception.

> Hint: catch the parse error, `logging.warning(raw_response)`, then return the same fallback `EvalResult` the roadmap uses.

---

### Exercise 3 — Build the loop and chart the climb (medium)

Implement `generate_with_quality_gate` and make it return a `history` list of `(attempt, score)`. After the run, print the scores as a simple ASCII sparkline or a one-line table so the improvement is *visible* (e.g. `Attempt 1: 5 | Attempt 2: 6 | Attempt 3: 8 ✅`). The mock generator must produce a worse first answer and better answers once feedback is present.

> Hint: have the mock generator branch on whether the prompt contains your feedback marker (`"IMPORTANT — Improve"`) and lengthen/sharpen its output each time it sees more feedback.

---

### Exercise 4 — Tune the threshold and observe the trade-off (medium)

Run the same task three times with `pass_threshold` set to 6, 8, and 10. For each, record: attempts used, final score, and whether `success` was `True`. Write a two-sentence conclusion about what happens to cost and pass-rate as you raise the bar.

> Hint: at threshold 10 you should see all `max_retries` consumed and `success=False` — confirm the loop still returns the last attempt rather than hanging.

---

### Exercise 5 — Ground a RAG answer (hard)

Take a small hand-written context paragraph and three candidate claims: one directly stated, one a fair inference, one invented. Run `check_hallucination` on each and assert you get SUPPORTED / INFERRED / UNSUPPORTED respectively. Then wire it into a `rag_with_hallucination_check` wrapper that prefixes `[⚠️ Low confidence]` only on the UNSUPPORTED case.

> Hint: keep the context short and unambiguous so the verdict is deterministic under the mock; test the three verdicts as three separate assertions.

---

### Exercise 6 — Cheaper judge, stricter generator (hard)

Make the judge use a *different, cheaper* model than the generator (e.g. generator on `claude-sonnet-4-6`, judge on `claude-3-5-haiku`). Inject both via a small factory so the choice is one config change, not a code edit. Then deliberately give the judge a hallucinated answer that *reads* well and note whether the cheap judge catches it — write down what this tells you about trusting a single judge.

> Hint: a `make_llm(role: Literal["generator", "judge"])` factory keeps the model choice in one place; under the mock, give the judge model deterministic verdicts so the experiment is repeatable.
