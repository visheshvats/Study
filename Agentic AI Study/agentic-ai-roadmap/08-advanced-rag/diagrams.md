# Phase 8 — Diagrams

Two diagrams: the **Advanced RAG Decision Flow** (reproduced verbatim from the
roadmap) and a new **Corrective RAG sequence diagram** showing the CRAG
pipeline end to end.

---

## 1. Advanced RAG Decision Flow

```mermaid
flowchart TD
    Q["Query"] --> ADAP{Adaptive RAG\nNeed retrieval?}
    ADAP -->|Yes| RET["Retrieve Docs"]
    ADAP -->|No — LLM knows| GEN["Generate Direct"]
    RET --> GRADE{Corrective RAG\nGrade quality}
    GRADE -->|Relevant ≥2| RAG_GEN["Generate\nfrom Docs"]
    GRADE -->|Insufficient| WSEARCH["🌐 Web Search\nSupplement"]
    WSEARCH --> RAG_GEN
    RAG_GEN --> HCHECK{Hallucination\nCheck}
    HCHECK -->|Grounded| ANS["✅ Answer"]
    HCHECK -->|Hallucinated| RET

    style ADAP  fill:#6C63FF,color:#fff
    style GRADE fill:#FF6B6B,color:#fff
    style HCHECK fill:#FFD700,color:#000
```

**Explanation.** This is the whole phase on one page. A query first hits the
**adaptive gate** (purple): if the LLM already knows the answer it generates
directly and the rest of the pipeline is skipped — the cheapest possible path.
Otherwise it retrieves, and every retrieved doc passes through **corrective
grading** (red). With at least two relevant docs we generate straight from
them; if the set is too thin we detour through a **web-search supplement**
first. After generation, a **hallucination check** (gold) verifies the answer
is grounded in the context — grounded answers are returned, hallucinated ones
loop back to retrieval rather than being shipped. The three coloured diamonds
are the three "reason about retrieval" decisions that distinguish advanced RAG
from the naive retrieve-then-generate chain of Phase 2.

---

## 2. Corrective RAG (CRAG) — sequence diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant App as CRAG Pipeline
    participant Ret as Retriever (vector store)
    participant Grader as LLM Grader
    participant Web as Web Search (Tavily)
    participant Gen as LLM Generator

    User->>App: query
    App->>Ret: invoke(query)
    Ret-->>App: raw_docs [d1, d2, d3]

    loop grade each doc
        App->>Grader: relevant?(query, doc)
        Grader-->>App: yes / no
    end
    Note over App: relevant = docs that passed

    alt relevant >= 2 (sufficient)
        Note over App: index is enough — skip web
    else relevant < 2 (thin)
        App->>Web: search(query)
        Web-->>App: web Document
        Note over App: append web result to relevant
    end

    App->>Gen: generate(context = relevant docs, query)
    Gen-->>App: answer
    App-->>User: answer + "*Sources: ...*"
```

**Explanation.** This unrolls the corrective-grading diamond into a step-by-step
exchange between the participants. The pipeline retrieves raw candidates, then
**loops** over them asking the grader a yes/no relevance question per document
— this is the step naive RAG omits entirely. The `alt` block is the correction
decision: if at least two docs pass, the index is trusted as-is and the web is
never called (saving an external request); if fewer than two pass, the pipeline
**falls back** to a web search and folds that result into the context. Only then
does generation run, and the response is returned with explicit **source
provenance** so the caller can see whether each fact came from the index, the
web, or both. Mapped to Spring Boot: the grading loop is input validation on
downstream data, the `alt` fallback is a Resilience4j secondary source, and the
`*Sources*` tag is the audit field on the response DTO.
