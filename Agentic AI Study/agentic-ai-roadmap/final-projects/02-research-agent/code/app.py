"""
FastAPI surface for the Research Agent. Phase 0 section 0.5.
Real server:  uvicorn app:app --reload   |   Offline self-test:  python app.py
Pipeline: agent gathers (tools) -> parallel analysis -> synthesis.
"""
from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import agent
import workflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("app")

app = FastAPI(title="Research Agent", version="1.0.0")
_AGENT = agent.ResearchAgent()


class ResearchRequest(BaseModel):
    question: str


@app.post("/research")
async def research(req: ResearchRequest) -> dict:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    gathered = _AGENT.run(req.question)                       # tools (fan-in of sources)
    analyses = await workflow.analyze_parallel(str(gathered["findings"]))  # parallel
    final = workflow.synthesize(req.question, str(gathered["findings"]), analyses)
    return {
        "answer": final,
        "tools_used": gathered["tools_used"],
        "sources": gathered["sources"],
        "analyses": analyses,
    }


def _self_test() -> None:
    from fastapi.testclient import TestClient

    print("=" * 68)
    print("Research Agent — offline self-test (no server, no API key)")
    print("=" * 68)
    with TestClient(app) as http:
        r = http.post("/research", json={"question": "How does our Pro plan price compare to competitors?"})
        body = r.json()
        print(f"\nPOST /research -> {r.status_code}")
        print(f"  tools_used: {body['tools_used']}  (used >1 source ✔)")
        print(f"  sources:    {body['sources']}")
        print(f"  analyses:   {body['analyses']}")
        print(f"  answer:\n    " + body["answer"].replace("\n", "\n    "))

        internal = http.post("/research", json={"question": "What storage does the Free plan include?"})
        print(f"\nPOST /research (internal-only) -> {internal.status_code} tools={internal.json()['tools_used']}")
    print("\nSelf-test complete.")


if __name__ == "__main__":
    _self_test()
