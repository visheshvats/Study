"""
The self-correcting RAG loop + FastAPI endpoint.
Composes Phases 6, 8, 9, 10. Wrap every model call with rate limiting + backoff.
Run:  uvicorn app:app --reload
"""
from __future__ import annotations

# TODO: from fastapi import FastAPI, HTTPException
# TODO: from pydantic import BaseModel
# TODO: import rag, evaluator, guardrails

# app = FastAPI(title="Self-correcting RAG")


# class AskRequest(BaseModel):
#     question: str
#     max_retries: int = 3


def self_correcting_answer(question: str, retriever, max_retries: int = 3) -> dict:
    """
    Orchestrate the full loop:
      1. guardrails.validate_input
      2. rag.needs_retrieval -> rag.corrective_retrieve (grade + web fallback)
      3. generate answer
      4. evaluator.check_hallucination (regenerate if unsupported)
      5. evaluator.judge_output -> retry with feedback until passed or max_retries
      6. guardrails.sanitize_output
    """
    # TODO: implement the loop described above, tracking attempts + final score.
    raise NotImplementedError


# @app.post("/ask")
# async def ask(req: AskRequest):
#     # TODO: ok, reason = guardrails.Guardrails.validate_input(req.question)
#     # TODO: if not ok: raise HTTPException(400, reason)
#     # TODO: return self_correcting_answer(req.question, retriever, req.max_retries)
#     raise NotImplementedError


if __name__ == "__main__":
    print("Implement self_correcting_answer + /ask, then run: uvicorn app:app --reload")
