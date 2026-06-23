# Phase 8 — Advanced RAG

> **Duration:** 1 week
> **Goal:** RAG that adapts, self-corrects, and reasons *about* retrieval — not just retrieve-then-generate blindly.

---

## Why this matters

In Phase 2 you built a "naive" RAG chain: take a query, retrieve the top-k
documents, stuff them into the prompt, generate. It works on the happy path,
and it fails silently everywhere else. It retrieves even when the model
already knows the answer (burning latency and tokens on "What is 2 + 2?"). It
trusts whatever the vector store returns, even when those documents are merely
*near* the query rather than actually *relevant*. And it has no idea whether
the answer it produced was grounded in the retrieved text or quietly
hallucinated.

**Advanced RAG reasons *about* retrieval.** It asks three questions that naive
RAG never asks: *Do I even need to retrieve? Are these documents good enough?
Is my answer actually grounded in them?* Those three questions map to the
three techniques in this phase — Adaptive RAG, Corrective RAG, and Agentic RAG.

The mental model that will feel familiar from your Spring Boot years: advanced
RAG wraps your flaky downstream "retrieval service" in the same resilience
patterns you already use around a flaky API. A **circuit breaker** (the
adaptive gate — don't even call the service if you don't need it), a
**fallback** (corrective RAG — when the primary source returns garbage, fail
over to web search), and a **validation layer** (the grounding check — never
return a response you haven't verified). You would never ship a service that
calls a downstream blindly, trusts whatever comes back, and returns it
unvalidated. Naive RAG does exactly that. This phase fixes it.

---

## The Advanced RAG decision flow

Everything in this phase is a single pipeline with three decision points. (The
full Mermaid diagram is in `diagrams.md`; here is the prose walk-through.)

1. **Adaptive gate (`needs_retrieval`)** — first decision. Can the LLM answer
   from its own knowledge? If yes, skip retrieval entirely and generate
   directly. If no, fall through to retrieval.
2. **Corrective grading (CRAG)** — second decision. We retrieved some docs;
   grade each one for true relevance. If at least 2 pass, generate from them.
   If fewer than 2 pass, the retrieval is "thin" — supplement with a web
   search before generating.
3. **Hallucination / grounding check** — third decision. We generated an
   answer; is it actually supported by the context we gave it? If grounded,
   return it (with source provenance). If hallucinated, loop back and retrieve
   again rather than ship a fabrication.

| Decision point | Question it answers | Cheap thing it prevents |
| --- | --- | --- |
| Adaptive gate | "Do I need docs at all?" | Wasted retrieval cost/latency on trivial queries |
| Corrective grading | "Are these docs good enough?" | Generating from topically-close-but-irrelevant junk |
| Grounding check | "Is my answer supported?" | Shipping a confident hallucination |

---

## 8.1 Adaptive RAG — the retrieval gate

The simplest win. Before retrieving, a tiny classifier prompt asks the model
whether the question needs document lookup or can be answered from general
knowledge. "Who wrote Romeo and Juliet?" → no retrieval. "What is *our*
refund policy?" → retrieve.

```python
def needs_retrieval(query: str) -> bool:
    """Decide: can the LLM answer from knowledge, or do we need docs?"""
    prompt = f"""Does this question require looking up specific documents or data,
or can it be answered from general knowledge?

Question: {query}

Answer ONLY: yes_retrieval or no_retrieval"""
    result = llm.invoke([HumanMessage(content=prompt)])
    return "yes" in result.content.lower()
```

The gate is one extra cheap LLM call that can save an expensive vector-store
round-trip *plus* the context tokens that would otherwise be stuffed into the
prompt. The metric that proves it is working is the **skip rate** — what
fraction of queries get answered without retrieval. (The runnable demo in
`code/01_adaptive_rag.py` prints exactly that.)

> A subtlety worth internalizing: a *fail-safe* gate defaults to **retrieve**
> when the classifier errors or is ambiguous. Being slow-but-correct on a
> private question beats being fast-but-wrong.

---

## 8.2 Corrective RAG (CRAG) — grade, then correct

Vector search returns the *nearest* documents, which is not the same as the
*relevant* ones. CRAG inserts a per-document relevance grader between
retrieval and generation, and a web-search fallback when the graded set is too
thin.

```python
def grade_doc_relevance(query: str, doc: Document) -> bool:
    prompt = f"""Is this document relevant to the query?
Query: {query}
Document excerpt: {doc.page_content[:400]}
Answer ONLY: yes or no"""
    result = llm.invoke([HumanMessage(content=prompt)])
    return result.content.strip().lower() == "yes"
```

The pipeline then:

1. **Retrieves** raw candidates.
2. **Grades** each — `relevant = [d for d in raw_docs if grade_doc_relevance(query, d)]`.
3. **Corrects** if `len(relevant) < 2`: supplement with a web search
   (Tavily/SerpAPI in production) so the model has *something* solid to ground
   on instead of two weak hits.
4. **Generates** from the corrected context, then appends explicit source
   provenance: `*Sources: policy_handbook.pdf, web_search*`.

Why the "< 2" threshold? One relevant document is a single point of failure —
easy to misread, easy to be an outlier. Requiring at least two gives the model
corroboration and makes the web-search fallback fire precisely when the index
genuinely lacks coverage. (Runnable: `code/02_corrective_rag.py`.)

| CRAG step | Spring Boot analogue |
| --- | --- |
| Grade each doc | Bean Validation on data returned from a downstream |
| `< 2 relevant` → web search | Resilience4j fallback to a secondary source |
| Label sources in answer | Audit/provenance field on the response DTO |

---

## 8.3 Agentic RAG — the agent picks the source

Adaptive RAG decides *whether* to retrieve; CRAG decides *whether the docs are
good enough*; Agentic RAG decides *where to retrieve from*. You expose several
retrieval sources as tools and let a ReAct agent choose — and combine — them
per question.

```python
@tool
def search_pdf_docs(query: str) -> str:
    """Search internal PDF knowledge base."""
    ...

@tool
def search_web(query: str) -> str:
    """Search the web for current information."""
    ...

@tool
def query_database(sql_description: str) -> str:
    """Query the product database."""
    ...

agentic_rag_agent = create_react_agent(llm, tools=[search_pdf_docs, search_web, query_database])
```

A compound question like *"What do **we** charge and what do **competitors**
charge?"* makes the agent call `query_database`/`search_pdf_docs` **and**
`search_web`, then synthesize. The tool **docstrings are the contract** the LLM
reads to decide when each applies — treat them like Javadoc the orchestrator
actually consumes, not decoration. (Runnable: `code/03_agentic_rag.py`.)

> Guardrail: a free-running agent can hop between sources forever. Always cap
> the loop (`recursion_limit` / a max-steps bound) — the same instinct as a
> max-retries or timeout on any orchestration.

| Source tool | When the agent should reach for it |
| --- | --- |
| `search_pdf_docs` | Private/internal facts: our policies, our pricing, our docs |
| `search_web` | Current/external facts: competitors, market, "latest" |
| `query_database` | Structured numbers: counts, records, metrics, ARPU |

---

## ⚠️ Common Java-dev mistakes

Coming from deterministic Spring Boot pipelines, these are the traps that bite
hardest in advanced RAG:

- **Always retrieving, even for trivial questions.** Treating the vector store
  like a mandatory `@Autowired` dependency on every request. Trivial and
  general-knowledge queries should skip retrieval — that is the entire point of
  the adaptive gate. Every needless retrieval is latency + tokens + cost you
  pay for nothing.
- **Trusting retrieved docs without grading.** "The repository returned rows,
  therefore the rows are correct" is false for vector stores. Nearest ≠
  relevant. Always grade before you generate.
- **No fallback when retrieval is thin.** Generating a confident answer off one
  weak hit is worse than admitting the index lacks coverage. Wire the
  web-search supplement (or, at minimum, return "I don't have enough
  information") — never invent.
- **Letting the agent loop forever over sources.** Without a `recursion_limit`,
  an agentic-RAG agent can ping-pong between PDF/web/DB indefinitely. Bound it
  exactly as you would bound retries on a downstream call.
- **Confusing "relevant" with "present in the index."** A document being
  *retrievable* (it exists, it embedded close) is not the same as it being
  *relevant* to this query. Grading separates the two.
- **Not labeling source provenance in the answer.** If your response can't say
  *where* each fact came from (which PDF, the web, the DB), it can't be audited
  — and in a regulated/financial context, an unauditable answer is unusable.
  Always attach sources.

---

## Key terms

| Term | Meaning |
| --- | --- |
| **Adaptive RAG** | RAG that decides *whether* to retrieve at all, via a gate before retrieval. |
| **Corrective RAG (CRAG)** | RAG that grades retrieved docs and corrects thin retrieval (e.g. with web search) before generating. |
| **Agentic RAG** | RAG where an agent chooses *which* retrieval source(s) to use from a set of tools. |
| **Relevance grading** | A per-document yes/no judgment of whether a retrieved doc actually answers the query. |
| **Retrieval gate** | The `needs_retrieval` classifier that routes a query to "retrieve" or "answer directly." |
| **Web-search fallback** | Supplementing thin index results with a live web search (Tavily/SerpAPI) before generating. |
| **Grounding / hallucination check** | A post-generation verification that the answer is supported by the supplied context. |
| **Multi-source retrieval** | Drawing from several stores (PDF + web + DB) for one question, often combined. |
| **Provenance** | Explicit labeling of where each fact in the answer came from (source attribution). |

---

## Phase 8 checklist

- [ ] Implement `needs_retrieval()` adaptive gate
- [ ] Build Corrective RAG with document grading
- [ ] Set up Tavily or SerpAPI for real web search
- [ ] Build Agentic RAG with 3+ retrieval tools
- [ ] Build Multi-source RAG (PDF + Web + DB)
