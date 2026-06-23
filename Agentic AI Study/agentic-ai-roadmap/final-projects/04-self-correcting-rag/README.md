# Final Project 4 — Self-correcting RAG API

**Complexity:** ⭐⭐⭐⭐  **Draws from:** Phases 0–6, 8–10 (FastAPI · LLM · RAG · LangGraph · Workflows · Orchestrators · Evaluator · Advanced RAG · Debugging · Production)

## Goal
A production-grade RAG API that **decides whether to retrieve**, **grades** what it retrieves,
**supplements** when retrieval is thin, **checks its own answer for hallucinations**, and **retries**
until a quality gate passes — all behind rate limiting and guardrails. This is the capstone: every
reliability pattern in the roadmap, composed.

## What you'll build
- Adaptive + corrective retrieval (Phase 8): skip retrieval when unneeded, grade docs, web-fallback.
- An evaluator loop (Phase 6): LLM-as-judge scores the answer; low scores trigger a feedback-driven retry.
- A hallucination/grounding check (Phase 6 §6.3) before returning.
- Guardrails (Phase 10): input injection/length checks, output PII redaction.
- Rate limiting + backoff (Phase 10) around every model call.
- LangSmith tracing + structured logging (Phase 9) so you can see why any answer happened.

## Step-by-step build plan
1. **Skeleton run.** venv + `pip install -r code/requirements.txt`, copy `.env.example` → `.env`.
2. **Retrieval (`code/rag.py`).** Implement `needs_retrieval` (adaptive gate), `grade_doc_relevance`, and `corrective_retrieve` (web fallback when < 2 relevant). See Phase 8 §8.1–8.2.
3. **Evaluation (`code/evaluator.py`).** Implement `judge_output` (Pydantic `EvalResult`) and `check_hallucination`. See Phase 6 §6.1, §6.3.
4. **Guardrails (`code/guardrails.py`).** Implement `validate_input` and `sanitize_output`. See Phase 10 §10.3.
5. **Self-correct loop (`code/app.py`).** Compose: guardrail → (adaptive) retrieve+grade → generate → hallucination check → judge → retry-with-feedback up to N times → sanitize → respond. Wrap model calls with rate limiting/backoff (Phase 10 §10.1).
6. **Observability.** Turn on LangSmith env vars and add a `@logged_node`-style wrapper (Phase 9).
7. **Stretch.** Express the whole loop as a LangGraph with conditional edges instead of imperative code.

## Files to fill in (`code/`)
| File | Your job |
|------|----------|
| `rag.py` | Adaptive gate + corrective retrieval with grading/fallback. |
| `evaluator.py` | LLM-as-judge `EvalResult` + hallucination check. |
| `guardrails.py` | Input validation + output sanitization. |
| `app.py` | The self-correcting loop + FastAPI endpoint, rate-limited. |
| `requirements.txt` / `.env.example` | Install / configure. |

## Done when
A query that the corpus can't answer triggers the web fallback; a deliberately weak first answer is
caught by the judge and improved on retry; and a prompt-injection input is rejected at the guardrail.
