# Final Project 1 — Chat with PDF (FastAPI + RAG)

**Complexity:** ⭐⭐  **Draws from:** Phase 0 (FastAPI, async, Pydantic) · Phase 1 (LLM calls, prompting) · Phase 2 (loaders, splitting, embeddings, Chroma, LCEL RAG chain)

## Goal
A small web service where a user uploads a PDF, then asks questions and gets answers **grounded only
in that PDF**, with source citations. This is the "hello world" of production RAG — the same shape as
a Spring Boot service that ingests a document into a search index and answers queries against it.

## What you'll build
- `POST /ingest` — accept a PDF, chunk it, embed it, persist to a Chroma collection.
- `POST /chat` — retrieve top-k chunks for the question and answer via an LCEL RAG chain.
- Answers say "I don't have that information" when the PDF doesn't cover the question (no hallucinating).

## Step-by-step build plan
1. **Skeleton run.** Create the venv, `pip install -r code/requirements.txt`, copy `.env.example` → `.env`, add your `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`.
2. **Ingestion (`code/ingest.py`).** Implement `load_pdf` (PyPDFLoader), `split` (RecursiveCharacterTextSplitter, 1000/200), `build_store` (Chroma `persist_directory`). Re-read Phase 2 §2.1–2.4.
3. **RAG chain (`code/rag_chain.py`).** Implement `format_docs` and the LCEL chain (`{context, question} | prompt | llm | StrOutputParser`). Re-use the grounded prompt from Phase 2 §2.5.
4. **API (`code/app.py`).** Wire `/ingest` and `/chat` with Pydantic request/response models and proper error handling (Phase 0 §0.5). Save the uploaded file to a temp path before loading.
5. **Citations.** Return the `source`/`page` metadata of the retrieved chunks alongside the answer.
6. **Guard the empty case.** If retrieval returns nothing relevant, short-circuit with the "no information" response.
7. **Stretch.** Add streaming (`/chat/stream`, Phase 1 §1.3) and conversational memory (Phase 2 §2.6).

## Files (`code/`) — complete reference implementation
| File | Your job |
|------|----------|
| `ingest.py` | Load → split → embed → persist a PDF into Chroma. |
| `rag_chain.py` | Build the retrieval-augmented LCEL chain. |
| `app.py` | FastAPI endpoints tying ingestion + chat together. |
| `requirements.txt` | Already listed — install it. |
| `.env.example` | Copy to `.env`, add keys. |

## Done when
You can `POST /ingest` a real PDF, ask a question its content answers (cited), and ask an unrelated
question and get the "I don't have that information" fallback.


---

## ✅ Status: fully implemented (runs offline, no API key)

The `code/` folder is a **complete, runnable reference implementation** — not just stubs. Every
module has an offline **mock path** (`USE_MOCK = True`) plus a clearly-commented **real-key path**.

- **Offline scaffolding:** `code/mock_kit.py` provides deterministic embeddings / vector store / LLM
  stand-ins so nothing external is required.
- **Run the offline self-test:** `cd code && python app.py` → ingest -> grounded answer w/ citation -> refuses an out-of-scope question -> 400 on empty input
- **Run as a service:** `pip install -r code/requirements.txt`, then `uvicorn app:app --reload`.
- **Go live:** copy `.env.example` → `.env`, add your keys, set `USE_MOCK = False` in each module, and
  swap the mock classes for the real LangChain / Anthropic / Chroma classes named in the TODO comments.
