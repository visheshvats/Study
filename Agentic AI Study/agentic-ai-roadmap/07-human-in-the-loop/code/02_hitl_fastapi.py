"""02_hitl_fastapi.py -- HITL over HTTP: park the draft, resume from a separate POST (Phase 7).

This is the PRODUCTION-shaped version of 01_hitl_interrupt.py. Instead of
blocking the thread on input(), the two halves of a HITL cycle become two
separate HTTP requests:

  POST /draft              -> start the graph, run until interrupt_before=["review"],
                              return {thread_id, draft} so a UI can show it.
  POST /review/{thread_id} -> inject the human's approve/feedback decision and
                              RESUME the SAME thread_id; return the final output.

Why two endpoints instead of one blocking call? On a server you must NEVER hold
a request thread open waiting for a human -- that is the classic Spring-dev
mistake (a controller blocking on a manual approval will exhaust the thread
pool). Instead you PERSIST the interrupted state (the checkpointer does this),
return immediately, and let the human's later POST act as the "resume" event.

Java analogies:
  * POST /draft            ~ a controller that kicks off a BPM process and parks
                            it on a human task, returning the task id.
  * thread_id in the URL   ~ the process-instance / correlation id you hand back.
  * POST /review/{id}      ~ the "complete task" callback that resumes the
                            parked instance -- like a webhook/queue listener.
  * checkpointer (MemorySaver) ~ the workflow state store. For real durability
                            across restarts, swap MemorySaver for a Postgres
                            checkpointer (an in-memory store loses parked work
                            if the process dies -- see notes.md mistakes list).

OFFLINE NOTE
------------
Uses the same deterministic FakeChatModel (USE_MOCK = True) -- no API key needed.
The __main__ block runs an OFFLINE smoke test with FastAPI's TestClient (no
real network, no uvicorn server, no blocking stdin). To serve for real:
    uvicorn 02_hitl_fastapi:app --reload
and flip USE_MOCK = False after exporting ANTHROPIC_API_KEY (build_llm() then
returns ChatAnthropic(model="claude-sonnet-4-6")).

Run it (offline):   python 02_hitl_fastapi.py
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

logger = logging.getLogger(__name__)

USE_MOCK = True  # offline by default -- no API key needed


# -----------------------------------------------------------------------------
# MODEL (mock vs. real) -- same factory pattern as 01.
# -----------------------------------------------------------------------------
class FakeChatModel:
    """Deterministic stand-in for ChatAnthropic (see 01_hitl_interrupt.py)."""

    def invoke(self, messages: List[Any]) -> AIMessage:
        prompt = " ".join(str(m.content) for m in messages).lower()
        if "revise" in prompt or "feedback" in prompt:
            note = ""
            for m in messages:
                text = str(m.content)
                if "Feedback:" in text:
                    note = text.split("Feedback:", 1)[1].strip()
            return AIMessage(
                content=(
                    "REVISED REFUND POLICY (v2)\n"
                    "- 30-day money-back guarantee.\n"
                    "- Pro-rated refunds for annual plans cancelled mid-term.\n"
                    f"- Incorporated reviewer feedback: {note or '(none supplied)'}"
                )
            )
        return AIMessage(
            content=(
                "DRAFT REFUND POLICY (v1)\n"
                "- 14-day money-back guarantee.\n"
                "- No refunds after 14 days.\n"
                "- Contact support@example.com to request a refund."
            )
        )


def build_llm() -> Any:
    if USE_MOCK:
        logger.info("Using FakeChatModel (offline, deterministic).")
        return FakeChatModel()
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model="claude-sonnet-4-6")


llm = build_llm()


# -----------------------------------------------------------------------------
# STATE + NODES (identical shape to 01)
# -----------------------------------------------------------------------------
class HITLState(TypedDict):
    task: str
    draft: str
    approved: bool
    feedback: str
    final: str


def generate_draft(state: HITLState) -> dict:
    response = llm.invoke([HumanMessage(content=f"Complete this task:\n{state['task']}")])
    return {"draft": response.content}


def request_review(state: HITLState) -> dict:
    # Paused before this node by interrupt_before; a no-op once resumed.
    return {}


def apply_decision(state: HITLState) -> dict:
    if state.get("approved", False):
        return {"final": state["draft"]}
    revision = llm.invoke(
        [
            HumanMessage(
                content=(
                    "Revise this based on feedback.\n\n"
                    f"Original:\n{state['draft']}\n\n"
                    f"Feedback:\n{state.get('feedback', '')}"
                )
            )
        ]
    )
    return {"final": revision.content}


def build_graph(checkpointer: MemorySaver):
    builder = StateGraph(HITLState)
    builder.add_node("generate", generate_draft)
    builder.add_node("review", request_review)
    builder.add_node("decide", apply_decision)
    builder.set_entry_point("generate")
    builder.add_edge("generate", "review")
    builder.add_edge("review", "decide")
    builder.add_edge("decide", END)
    return builder.compile(checkpointer=checkpointer, interrupt_before=["review"])


# A single shared checkpointer + graph for the app's lifetime. The checkpointer
# is what carries parked state BETWEEN the two requests; rebuilding it per
# request would lose the interrupt (a common mistake). In prod this would be a
# Postgres-backed checkpointer so parked drafts survive a restart.
CHECKPOINTER = MemorySaver()
GRAPH = build_graph(CHECKPOINTER)


# -----------------------------------------------------------------------------
# REQUEST / RESPONSE SCHEMAS (Pydantic == your Spring DTOs with @Valid)
# -----------------------------------------------------------------------------
class DraftRequest(BaseModel):
    task: str = Field(..., min_length=1, description="What the agent should draft.")


class DraftResponse(BaseModel):
    thread_id: str
    draft: str
    status: str = "awaiting_review"


class ReviewRequest(BaseModel):
    approved: bool = Field(..., description="True to ship as-is, False to revise.")
    feedback: str = Field("", description="Required (non-empty) when approved is False.")


class ReviewResponse(BaseModel):
    thread_id: str
    final: str
    status: str = "completed"


# -----------------------------------------------------------------------------
# APP
# -----------------------------------------------------------------------------
app = FastAPI(title="HITL Draft-and-Review API", version="1.0.0")


@app.post("/draft", response_model=DraftResponse)
def create_draft(req: DraftRequest) -> DraftResponse:
    """Start a HITL run and park it at the interrupt. Returns the draft +
    a fresh thread_id the caller must echo back on /review.
    """
    thread_id = f"hitl-{uuid.uuid4().hex[:12]}"
    config: Dict[str, Any] = {"configurable": {"thread_id": thread_id}}
    initial: HITLState = {
        "task": req.task,
        "draft": "",
        "approved": False,
        "feedback": "",
        "final": "",
    }
    try:
        GRAPH.invoke(initial, config)  # runs to interrupt_before=["review"]
    except Exception as exc:  # surface graph failures as 500, don't leak traceback
        logger.exception("Graph failed during draft generation")
        raise HTTPException(status_code=500, detail="draft generation failed") from exc

    snapshot = GRAPH.get_state(config)
    if "review" not in snapshot.next:
        # Defensive: if we are NOT parked before 'review', the interrupt didn't
        # fire (likely a missing checkpointer / wiring bug) -- don't hand the
        # caller a thread_id that can't be resumed.
        logger.error("Expected pause before 'review' but next=%s", snapshot.next)
        raise HTTPException(status_code=500, detail="graph did not pause for review")

    draft = snapshot.values["draft"]
    logger.info("Parked thread_id=%s awaiting review", thread_id)
    return DraftResponse(thread_id=thread_id, draft=draft)


@app.post("/review/{thread_id}", response_model=ReviewResponse)
def submit_review(thread_id: str, req: ReviewRequest) -> ReviewResponse:
    """Resume the parked run identified by thread_id with the human decision.

    Validation mirrors 01: a rejection MUST carry feedback. A wrong/unknown
    thread_id resolves to an empty state -- we detect that and 404 instead of
    resuming the wrong (or no) case.
    """
    if not req.approved and not req.feedback.strip():
        raise HTTPException(
            status_code=422, detail="feedback is required when approved is false"
        )

    config: Dict[str, Any] = {"configurable": {"thread_id": thread_id}}
    snapshot = GRAPH.get_state(config)

    # An unknown/already-finished thread won't be parked before 'review'.
    if not snapshot.values or "review" not in snapshot.next:
        logger.warning(
            "No parked review found for thread_id=%s (next=%s)",
            thread_id,
            getattr(snapshot, "next", None),
        )
        raise HTTPException(
            status_code=404, detail="no draft awaiting review for that thread_id"
        )

    try:
        # Resume correctly: patch the decision into the checkpoint, then
        # invoke(None) to CONTINUE from the pause (passing a dict here would
        # restart the graph from 'generate' -- see 01_hitl_interrupt.py notes).
        GRAPH.update_state(
            config, {"approved": req.approved, "feedback": req.feedback}
        )
        result = GRAPH.invoke(None, config)
    except Exception as exc:
        logger.exception("Graph failed during resume for thread_id=%s", thread_id)
        raise HTTPException(status_code=500, detail="resume failed") from exc

    logger.info("Resumed thread_id=%s approved=%s", thread_id, req.approved)
    return ReviewResponse(thread_id=thread_id, final=result["final"])


# -----------------------------------------------------------------------------
# OFFLINE SMOKE TEST -- TestClient drives the API in-process (no uvicorn, no net,
# no stdin). This is your integration test, the way you'd use MockMvc in Spring.
# -----------------------------------------------------------------------------
def _smoke_test() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(app)
    logger.info("---- SMOKE: approve path ----")
    r = client.post("/draft", json={"task": "Draft a refund policy for a SaaS product"})
    assert r.status_code == 200, r.text
    body = r.json()
    tid_a = body["thread_id"]
    logger.info("draft (thread=%s):\n%s", tid_a, body["draft"])
    assert "DRAFT REFUND POLICY" in body["draft"]

    r = client.post(f"/review/{tid_a}", json={"approved": True})
    assert r.status_code == 200, r.text
    final_a = r.json()["final"]
    logger.info("final (approved):\n%s", final_a)
    assert "DRAFT REFUND POLICY" in final_a  # approve ships v1 unchanged

    logger.info("---- SMOKE: reject + feedback path ----")
    r = client.post("/draft", json={"task": "Draft a refund policy for a SaaS product"})
    tid_b = r.json()["thread_id"]
    r = client.post(
        f"/review/{tid_b}",
        json={"approved": False, "feedback": "Make it 30 days and add pro-rated refunds."},
    )
    assert r.status_code == 200, r.text
    final_b = r.json()["final"]
    logger.info("final (revised):\n%s", final_b)
    assert "REVISED REFUND POLICY" in final_b and "30" in final_b

    logger.info("---- SMOKE: validation + 404 guards ----")
    # Rejection without feedback -> 422.
    r = client.post("/draft", json={"task": "x"})
    tid_c = r.json()["thread_id"]
    r = client.post(f"/review/{tid_c}", json={"approved": False, "feedback": ""})
    assert r.status_code == 422, r.text
    # Unknown thread_id -> 404.
    r = client.post("/review/does-not-exist", json={"approved": True})
    assert r.status_code == 404, r.text

    logger.info("All FastAPI HITL smoke tests passed (offline).")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    _smoke_test()


if __name__ == "__main__":
    main()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
