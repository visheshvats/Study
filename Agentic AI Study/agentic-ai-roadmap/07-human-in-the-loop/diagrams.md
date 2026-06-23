# Phase 7 — Human in the Loop · Diagrams

## 1. HITL sequence (from the roadmap)

The end-to-end interaction: the graph generates a draft, **interrupts** to let a human review, then
resumes down the approve or reject-with-feedback branch.

```mermaid
sequenceDiagram
    participant U as User
    participant G as LangGraph
    participant H as Human Reviewer

    U->>G: Submit task
    G->>G: Generate draft
    G-->>H: ⏸️ INTERRUPT — Review draft
    H->>G: Approve / Reject / Edit
    alt Approved
        G->>G: Continue with draft
    else Rejected with feedback
        G->>G: Revise based on feedback
    end
    G->>U: Final output
```

---

## 2. Graph state machine (new — fills the gap)

The sequence diagram shows the *interaction over time*; this `stateDiagram-v2` shows the **compiled
graph itself** — the nodes, the interrupt point, and the two decision branches that the source only
expresses in code. This is the view that maps cleanly onto `spring-statemachine`: each box is a
state, the dashed interrupt is a manual-approval gate, and `decide` is a guarded transition.

```mermaid
stateDiagram-v2
    [*] --> generate : invoke(task, thread_id)
    generate --> review : edge
    note right of review
        interrupt_before=["review"]
        Graph PAUSES here.
        State persisted by checkpointer.
        Resumes on invoke(decision, same thread_id)
    end note
    review --> decide : resume with {approved, feedback}
    decide --> Approved : approved == True
    decide --> Revise : approved == False
    Approved --> [*] : final = draft
    Revise --> [*] : final = LLM revise(draft, feedback)
```

**How to read it:** `generate` runs autonomously and produces the draft. The graph then halts at the
dashed `review` boundary — nothing past it executes until a human decision is injected on the same
`thread_id`. `decide` is the guard: `approved == True` ships the draft as-is; otherwise the LLM
revises it using the feedback. Both branches terminate at `END`.
