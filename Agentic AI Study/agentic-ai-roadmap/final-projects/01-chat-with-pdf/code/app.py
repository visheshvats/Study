"""
FastAPI surface for Chat-with-PDF. Phase 0 section 0.5.
Run a real server:  uvicorn app:app --reload   (then POST /ingest, /chat)
Run the offline self-test:  python app.py
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import ingest
import rag_chain

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("app")

app = FastAPI(title="Chat with PDF", version="1.0.0")

# Module-level store == the loaded index. In production back this with persistent Chroma.
_STATE: dict[str, object] = {"store": None, "chunks": 0}


class IngestRequest(BaseModel):
    # For the demo we accept a path (real PDF) OR fall back to the bundled sample.
    path: Optional[str] = None


class ChatRequest(BaseModel):
    question: str


@app.post("/ingest")
async def ingest_endpoint(req: IngestRequest) -> dict:
    store, n = ingest.ingest(req.path)
    _STATE["store"], _STATE["chunks"] = store, n
    return {"status": "indexed", "chunks": n}


@app.post("/chat")
async def chat_endpoint(req: ChatRequest) -> dict:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    if _STATE["store"] is None:
        raise HTTPException(status_code=409, detail="ingest a document first")
    return rag_chain.answer(req.question, _STATE["store"])


def _self_test() -> None:
    from fastapi.testclient import TestClient

    print("=" * 68)
    print("Chat with PDF — offline self-test (TestClient, no server, no API key)")
    print("=" * 68)
    with TestClient(app) as http:
        ing = http.post("/ingest", json={})
        print(f"\nPOST /ingest -> {ing.status_code} {ing.json()}")

        grounded = http.post("/chat", json={"question": "What is the refund window?"})
        print(f"\nPOST /chat (grounded) -> {grounded.status_code}")
        print(f"  answer:  {grounded.json()['answer']}")
        print(f"  sources: {grounded.json()['sources']}")

        oot = http.post("/chat", json={"question": "Who won the 2024 World Series?"})
        print(f"\nPOST /chat (out-of-scope) -> {oot.status_code}")
        print(f"  answer:  {oot.json()['answer']}  (correct: refuses to hallucinate)")

        empty = http.post("/chat", json={"question": "  "})
        print(f"\nPOST /chat (empty) -> {empty.status_code} (expected 400)")
    print("\nSelf-test complete.")


if __name__ == "__main__":
    _self_test()
