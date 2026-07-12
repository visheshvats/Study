# Final Project 3 — Blog Generator (Planner + Writer + Editor)

**Complexity:** ⭐⭐⭐  **Draws from:** Phases 0–5 (FastAPI · LLM · RAG · LangGraph · Workflows · Orchestrators)

## Goal
An orchestrator that turns a topic into a finished blog post by coordinating specialist agents:
a **Researcher** gathers facts, a **Writer** drafts, an **Editor** polishes. This is the
orchestrator–worker pattern (Phase 5) end to end — the agent equivalent of a Saga coordinator
delegating to specialist services and aggregating the result.

## What you'll build
- A reusable `WorkerAgent` (specialty injected via system prompt).
- An `Orchestrator` that **plans** subtasks, **executes** them respecting dependencies, and **synthesizes** the final post.
- A `POST /generate` endpoint that returns the finished article.

## Step-by-step build plan
1. **Skeleton run.** venv + `pip install -r code/requirements.txt`, copy `.env.example` → `.env`.
2. **Workers (`code/workers.py`).** Implement `WorkerAgent.run` (system prompt + context + task → content). See Phase 5 §5.1.
3. **Orchestrator (`code/orchestrator.py`).** Implement `plan` (LLM returns a JSON task list — guard the parse!), `execute` (dependency-aware, pass upstream results as context), `synthesize`. See Phase 5 §5.1.
4. **Pipeline.** Wire Researcher → Writer → Editor with `depends_on` so each stage sees the previous output.
5. **API (`code/app.py`).** `POST /generate {topic, word_count}` → run orchestrator → return the article.
6. **Quality gate (stretch).** Add a Phase 6 evaluator loop so the Editor's output must score ≥ 7 before returning.
7. **Async (stretch).** Move generation to a background task (Phase 11) and poll for the result.

## Files (`code/`) — complete reference implementation
| File | Your job |
|------|----------|
| `workers.py` | `WorkerAgent` with specialty injection. |
| `orchestrator.py` | `plan` / `execute` / `synthesize`. |
| `app.py` | FastAPI `/generate` endpoint. |
| `requirements.txt` / `.env.example` | Install / configure. |

## Done when
`POST /generate {"topic": "benefits of RAG in enterprise AI", "word_count": 300}` returns a coherent,
edited post produced by all three workers in dependency order.


---

## ✅ Status: fully implemented (runs offline, no API key)

The `code/` folder is a **complete, runnable reference implementation** — not just stubs. Every
module has an offline **mock path** (`USE_MOCK = True`) plus a clearly-commented **real-key path**.

- **Offline scaffolding:** `code/mock_kit.py` provides deterministic embeddings / vector store / LLM
  stand-ins so nothing external is required.
- **Run the offline self-test:** `cd code && python app.py` → a plan executed Researcher -> Writer -> Editor in dependency order, producing a final article
- **Run as a service:** `pip install -r code/requirements.txt`, then `uvicorn app:app --reload`.
- **Go live:** copy `.env.example` → `.env`, add your keys, set `USE_MOCK = False` in each module, and
  swap the mock classes for the real LangChain / Anthropic / Chroma classes named in the TODO comments.
