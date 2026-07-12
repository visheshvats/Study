"""
FastAPI surface for the Blog Generator. Phase 0 section 0.5.
Real server:  uvicorn app:app --reload   |   Offline self-test:  python app.py
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from orchestrator import Orchestrator
from workers import WorkerAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("app")

app = FastAPI(title="Blog Generator", version="1.0.0")


def _build_orchestrator() -> Orchestrator:
    return Orchestrator([
        WorkerAgent("Researcher", "research", "Find facts and data. Be specific."),
        WorkerAgent("Writer", "writing", "Write clear, engaging content from the research."),
        WorkerAgent("Editor", "editing", "Improve clarity, grammar, and flow."),
    ])


class GenerateRequest(BaseModel):
    topic: str
    word_count: int = 300


@app.post("/generate")
async def generate(req: GenerateRequest) -> dict:
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="topic cannot be empty")
    goal = f"{req.topic} (~{req.word_count} words)"
    article = _build_orchestrator().run(goal)
    return {"topic": req.topic, "article": article}


def _self_test() -> None:
    from fastapi.testclient import TestClient

    print("=" * 68)
    print("Blog Generator — offline self-test (no server, no API key)")
    print("=" * 68)
    with TestClient(app) as http:
        r = http.post("/generate", json={"topic": "the benefits of RAG in enterprise AI", "word_count": 300})
        print(f"\nPOST /generate -> {r.status_code}\n")
        print(r.json()["article"])
        print("\n(Note: FINAL text flowed Researcher -> Writer -> Editor in dependency order.)")
        bad = http.post("/generate", json={"topic": "  "})
        print(f"\nPOST /generate (empty) -> {bad.status_code} (expected 400)")
    print("\nSelf-test complete.")


if __name__ == "__main__":
    _self_test()
