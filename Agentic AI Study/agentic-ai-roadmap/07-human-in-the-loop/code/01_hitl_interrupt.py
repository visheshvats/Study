"""01_hitl_interrupt.py -- Human-in-the-Loop (HITL) with LangGraph interrupt_before (Phase 7.1).

A HITL graph PAUSES itself before a high-risk step, lets a human inspect the
work-in-progress, then RESUMES with the human's decision injected into state.
The two things that make pause/resume possible are:

  1. a CHECKPOINTER  -- persists the full state after each super-step, so the
                        graph can be frozen mid-run and thawed later.
  2. a thread_id     -- the key the checkpointer uses to find "this run". You
                        resume by calling invoke() again with the SAME thread_id.

Java analogies (you have 6 yrs of Spring Boot):
  * interrupt_before        ~ a @PreAuthorize / approval gate that BLOCKS the
                              transition until an authorised human acts.
  * checkpointer            ~ Spring Session / a JPA-persisted workflow state;
                              without it there is nothing to pause and resume.
  * thread_id               ~ an HTTP session id / a BPM process-instance id /
                              a correlation id. Resume with the wrong one and
                              you resume the WRONG case.
  * the interrupted graph   ~ a BPMN "human task": the engine parks the process
                              instance and waits for a person to complete it.
  * approve vs reject path  ~ the two outgoing transitions from a manual
                              approval stage in a CI/CD pipeline.

OFFLINE NOTE
------------
The roadmap source uses a real ChatAnthropic and a BLOCKING input() call for
the human review. Blocking on stdin is fine in a notebook but is exactly the
mistake you must NOT ship to a server (it freezes the request thread). So this
demo:
  * uses a deterministic FakeChatModel (USE_MOCK = True) -- runs with NO API key,
  * drives the human review NON-INTERACTIVELY, simulating BOTH an "approve" run
    and a "reject-with-feedback" run programmatically -- no stdin, no blocking.
The real interactive input() version is kept below, COMMENTED, for reference.

Run it (offline):   python 01_hitl_interrupt.py
Go live:            set USE_MOCK = False and export ANTHROPIC_API_KEY, then the
                    build_llm() factory returns ChatAnthropic(model="claude-sonnet-4-6").
"""

from __future__ import annotations

import logging
from typing import Any, List, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# OFFLINE SWITCH
# -----------------------------------------------------------------------------
USE_MOCK = True  # offline by default -- no API key needed


class FakeChatModel:
    """Deterministic stand-in for ChatAnthropic so the demo runs offline.

    It is intentionally dumb but predictable: a first draft, then -- when it sees
    feedback in the revise prompt -- a "revised" draft that echoes the feedback.
    That determinism is what lets the __main__ smoke test ASSERT on the output
    (a mock LLM is the unit-test seam, like Mockito stubbing a Spring bean).
    """

    def invoke(self, messages: List[Any]) -> AIMessage:
        prompt = " ".join(str(m.content) for m in messages).lower()

        if "revise" in prompt or "feedback" in prompt:
            # Pull the feedback line back out so the revision visibly reflects it.
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

        # First-pass draft.
        return AIMessage(
            content=(
                "DRAFT REFUND POLICY (v1)\n"
                "- 14-day money-back guarantee.\n"
                "- No refunds after 14 days.\n"
                "- Contact support@example.com to request a refund."
            )
        )


def build_llm() -> Any:
    """Factory for the chat model -- the one place to flip mock vs. real.

    Java analogy: a @Profile-switched @Bean. Test profile wires the fake, prod
    profile wires the real client. Call sites never change.
    """
    if USE_MOCK:
        logger.info("Using FakeChatModel (offline, deterministic).")
        return FakeChatModel()
    # -- Real model (requires ANTHROPIC_API_KEY in the environment) --
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model="claude-sonnet-4-6")


llm = build_llm()


# -----------------------------------------------------------------------------
# STATE -- the shared object carried between nodes (like a BPM process-variables map)
# -----------------------------------------------------------------------------
class HITLState(TypedDict):
    task: str        # what the user asked for
    draft: str       # the work product awaiting human review
    approved: bool   # the human's decision, injected on resume
    feedback: str    # free-text the human gives when rejecting
    final: str       # the output after approval or revision


# -----------------------------------------------------------------------------
# NODES -- each is a pure function: State -> partial State (never mutate in place)
# -----------------------------------------------------------------------------
def generate_draft(state: HITLState) -> dict:
    """Produce the first draft. Runs BEFORE the interrupt."""
    logger.info("Node 'generate': drafting for task=%r", state["task"])
    response = llm.invoke(
        [HumanMessage(content=f"Complete this task:\n{state['task']}")]
    )
    return {"draft": response.content}


def request_review(state: HITLState) -> dict:
    """Placeholder node. Because the graph is compiled with
    interrupt_before=["review"], execution PAUSES *before* this node ever runs.
    The human's decision is injected into state on resume, then this node is a
    no-op pass-through. (Think: a BPMN user-task node that the engine parks on.)
    """
    logger.info("Node 'review': resumed past the interrupt with the human decision.")
    return {}


def apply_decision(state: HITLState) -> dict:
    """Branch on the human decision: approve -> ship the draft as-is;
    reject -> ask the LLM to revise using the feedback. This is the two-way
    transition out of an approval gate.
    """
    if state.get("approved", False):
        logger.info("Node 'decide': APPROVED -- shipping the draft unchanged.")
        return {"final": state["draft"]}

    feedback = state.get("feedback", "").strip()
    logger.info("Node 'decide': REJECTED -- revising with feedback=%r", feedback)
    revision = llm.invoke(
        [
            HumanMessage(
                content=(
                    "Revise this based on feedback.\n\n"
                    f"Original:\n{state['draft']}\n\n"
                    f"Feedback:\n{feedback}"
                )
            )
        ]
    )
    return {"final": revision.content}


# -----------------------------------------------------------------------------
# GRAPH BUILDER
# -----------------------------------------------------------------------------
def build_graph(checkpointer: MemorySaver):
    """Wire generate -> review -> decide -> END and compile WITH a checkpointer
    and an interrupt_before on "review".

    The checkpointer is NOT optional for HITL: without it there is no persisted
    state to pause on, and interrupt_before would have nothing to resume.
    """
    builder = StateGraph(HITLState)
    builder.add_node("generate", generate_draft)
    builder.add_node("review", request_review)
    builder.add_node("decide", apply_decision)

    builder.set_entry_point("generate")
    builder.add_edge("generate", "review")
    builder.add_edge("review", "decide")
    builder.add_edge("decide", END)

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["review"],  # <-- PAUSE HERE for the human
    )


# -----------------------------------------------------------------------------
# HELPERS -- split the run into "until interrupt" and "resume" so a server could
# call them from two different HTTP handlers (see 02_hitl_fastapi.py).
# -----------------------------------------------------------------------------
def start_until_interrupt(graph: Any, task: str, thread_id: str) -> str:
    """Run from the entry point until the graph hits interrupt_before=["review"],
    then return the draft for a human to inspect. Returns the draft text.
    """
    config = {"configurable": {"thread_id": thread_id}}
    initial: HITLState = {
        "task": task,
        "draft": "",
        "approved": False,
        "feedback": "",
        "final": "",
    }
    graph.invoke(initial, config)  # stops at the interrupt; does NOT run 'review'

    snapshot = graph.get_state(config)
    # snapshot.next tells you which node is QUEUED but not yet run. For a paused
    # HITL graph it should be ("review",) -- proof the interrupt fired.
    if "review" not in snapshot.next:
        logger.warning(
            "Expected to be paused before 'review' but next=%s", snapshot.next
        )
    return snapshot.values["draft"]


def resume_with_decision(
    graph: Any,
    thread_id: str,
    approved: bool,
    feedback: str = "",
) -> str:
    """Resume the SAME thread_id with the human decision injected into state.
    Returns the final output. Validate the human input before injecting it --
    never trust the resume payload blindly (it may come from a web request).

    HOW RESUME ACTUALLY WORKS (important -- the roadmap source is subtly wrong):
    The source resumes via graph.invoke({"approved": ...}, config). Passing a
    NON-None input dict makes LangGraph treat it as a brand-new run and re-run
    from the entry point (you'll see 'generate' fire again). The correct
    resume-from-checkpoint pattern is two steps:
        1. graph.update_state(config, {...})  -> patch the human decision into the
                                                 persisted checkpoint (a delta merge),
        2. graph.invoke(None, config)         -> continue from exactly where it
                                                 paused (runs 'review' -> 'decide').
    Java analogy: update_state is "set the process variables on the parked
    instance"; invoke(None) is "signal/complete the human task to let it flow on".
    """
    if approved and feedback:
        # Defensive: an approval carrying feedback is contradictory; log + drop.
        logger.warning("Approval arrived WITH feedback; ignoring feedback on approve.")
        feedback = ""
    if not approved and not feedback.strip():
        # A rejection with no guidance can't be acted on -- fail loud, don't guess.
        raise ValueError("Rejection requires non-empty feedback to revise from.")

    config = {"configurable": {"thread_id": thread_id}}
    # Step 1: inject the human decision into the persisted checkpoint.
    graph.update_state(config, {"approved": approved, "feedback": feedback})
    # Step 2: resume from the checkpoint (None == "continue", not "restart").
    result = graph.invoke(None, config)
    return result["final"]


# -----------------------------------------------------------------------------
# INTERACTIVE VERSION (reference only -- DO NOT use on a server thread)
# -----------------------------------------------------------------------------
def _interactive_review_BLOCKS_stdin(graph: Any, thread_id: str) -> str:
    """The roadmap source's blocking-input version, kept for reference.

    This is correct for a one-off script / notebook, but on a web server it
    would FREEZE the request-handling thread until a human typed something --
    the classic Java-dev mistake. The FastAPI example (02) does it the right
    way: park the state and resume from a separate POST request.

    To use it, uncomment the body and call it instead of resume_with_decision().
    """
    raise NotImplementedError(
        "Interactive stdin review is disabled in the offline demo. "
        "Uncomment the body below to try it manually."
    )
    # config = {"configurable": {"thread_id": thread_id}}
    # approved = input("\nApprove? (y/n): ").strip().lower() == "y"
    # feedback = "" if approved else input("Enter feedback: ")
    # graph.update_state(config, {"approved": approved, "feedback": feedback})
    # result = graph.invoke(None, config)  # None == resume from checkpoint
    # return result["final"]


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------
def run_scenario(
    label: str,
    task: str,
    thread_id: str,
    approved: bool,
    feedback: str = "",
) -> str:
    """Run one full HITL cycle: build a fresh graph, pause at the interrupt,
    print the draft, then resume with a programmatic decision and print final.
    Each scenario uses its OWN thread_id so the checkpoints never collide.
    """
    logger.info("======== SCENARIO: %s (thread_id=%s) ========", label, thread_id)
    graph = build_graph(MemorySaver())

    draft = start_until_interrupt(graph, task, thread_id)
    logger.info("[INTERRUPTED] draft awaiting human review:\n%s", draft)

    decision = "APPROVE" if approved else f"REJECT (feedback: {feedback!r})"
    logger.info("Injected human decision: %s", decision)

    final = resume_with_decision(graph, thread_id, approved, feedback)
    logger.info("[FINAL] output:\n%s", final)
    return final


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    task = "Draft a refund policy for a SaaS product"

    # Scenario A: the human APPROVES the first draft -> final == draft.
    final_approved = run_scenario(
        label="APPROVE",
        task=task,
        thread_id="hitl-approve-001",
        approved=True,
    )
    assert "DRAFT REFUND POLICY" in final_approved, "approve path should ship v1"

    # Scenario B: the human REJECTS with feedback -> graph revises -> final == v2.
    final_revised = run_scenario(
        label="REJECT + FEEDBACK",
        task=task,
        thread_id="hitl-reject-002",
        approved=False,
        feedback="14 days is too short; make it 30 and add pro-rated annual refunds.",
    )
    assert "REVISED REFUND POLICY" in final_revised, "reject path should revise to v2"
    assert "30" in final_revised, "revision should reflect the 30-day feedback"

    logger.info("Both HITL scenarios completed successfully (offline).")


if __name__ == "__main__":
    main()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
