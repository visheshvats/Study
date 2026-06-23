"""
FastAPI surface for Chat-with-PDF. See Phase 0 section 0.5.
Run:  uvicorn app:app --reload
"""
from __future__ import annotations

from typing import Optional

# TODO: from fastapi import FastAPI, UploadFile, File, HTTPException
# TODO: from pydantic import BaseModel
# TODO: import ingest, rag_chain

# app = FastAPI(title="Chat with PDF")


# class ChatRequest(BaseModel):
#     question: str


# @app.post("/ingest")
# async def ingest_endpoint(file: UploadFile = File(...)):
#     # TODO: save upload to a temp path, call ingest.ingest(path), return {"chunks": n}
#     raise NotImplementedError


# @app.post("/chat")
# async def chat_endpoint(req: ChatRequest):
#     # TODO: chain = rag_chain.build_rag_chain(); return {"answer": chain.invoke(req.question)}
#     raise NotImplementedError


if __name__ == "__main__":
    print("Fill in the endpoints, then run: uvicorn app:app --reload")
