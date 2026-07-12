# Final Project 2 — Multi-doc Research Agent

**Complexity:** ⭐⭐⭐  **Draws from:** Phases 0–4 (FastAPI · LLM/tools · RAG · LangGraph · Workflows)

## Goal
Given a research question, an agent gathers information from **multiple sources** (an internal doc
store plus a mock web search), runs sub-analyses in parallel, and synthesizes a cited answer. This is
the orchestration jump: from "answer one query" to "run a small research pipeline."

## What you'll build
- Retrieval **tools** the agent can call (doc search, web search).
- A **ReAct agent** (LangGraph `create_react_agent`) that decides which tool(s) to use.
- A **parallel** sub-analysis step (fan-out/fan-in with `asyncio.gather`) and a synthesis step.
- A `POST /research` endpoint returning the synthesized answer + sources.

## Step-by-step build plan
1. **Skeleton run.** venv + `pip install -r code/requirements.txt`, copy `.env.example` → `.env`.
2. **Tools (`code/tools.py`).** Implement `search_docs` (Phase 2 retriever) and `search_web` (mock now; Tavily later). Decorate with `@tool` (Phase 3 §3.3 / Phase 1 §1.4).
3. **Agent (`code/agent.py`).** Build a ReAct agent over those tools; let it plan the retrieval (Phase 3).
4. **Parallel analysis (`code/workflow.py`).** Implement `analyze_parallel` (sentiment/topics/key-claims) with `asyncio.gather`, then `synthesize` (Phase 4 §4.3 + §4.1).
5. **API (`code/app.py`).** Expose `POST /research`; run the agent, then the synthesis; return answer + source list.
6. **Stretch.** Add a router (Phase 4 §4.2) that sends factual vs. opinion questions down different pipelines.

## Files (`code/`) — complete reference implementation
| File | Your job |
|------|----------|
| `tools.py` | `@tool`-decorated `search_docs` + `search_web`. |
| `agent.py` | ReAct agent wiring over the tools. |
| `workflow.py` | Parallel sub-analyses + synthesis. |
| `app.py` | FastAPI `/research` endpoint. |
| `requirements.txt` / `.env.example` | Install / configure. |

## Done when
`POST /research {"question": ...}` returns a synthesized, source-attributed answer that demonstrably
used more than one tool.


---

## ✅ Status: fully implemented (runs offline, no API key)

The `code/` folder is a **complete, runnable reference implementation** — not just stubs. Every
module has an offline **mock path** (`USE_MOCK = True`) plus a clearly-commented **real-key path**.

- **Offline scaffolding:** `code/mock_kit.py` provides deterministic embeddings / vector store / LLM
  stand-ins so nothing external is required.
- **Run the offline self-test:** `cd code && python app.py` → a comparative query that uses BOTH doc + web tools, parallel analysis, and a cited synthesis
- **Run as a service:** `pip install -r code/requirements.txt`, then `uvicorn app:app --reload`.
- **Go live:** copy `.env.example` → `.env`, add your keys, set `USE_MOCK = False` in each module, and
  swap the mock classes for the real LangChain / Anthropic / Chroma classes named in the TODO comments.
