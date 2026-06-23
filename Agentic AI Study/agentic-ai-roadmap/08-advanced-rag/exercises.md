# Phase 8 — Exercises

Work these in order — each builds on the last. No solutions provided; that is
deliberate. The runnable scripts in `code/` (all offline via `USE_MOCK = True`)
are your reference implementations to extend, not copy. One hint per exercise.

---

### Exercise 1 — Build the gate and measure its skip rate (easy)

Implement `needs_retrieval(query)` and run it over a list of at least 10
queries that you label by hand as "trivial" (skip) or "specific" (retrieve).
Print the **skip rate** (fraction answered without retrieval) and a confusion
count: how many trivial queries the gate *wrongly* sent to retrieval, and vice
versa.

> **Hint:** Start from `code/01_adaptive_rag.py`; the skip-rate counter is
> already there — add the hand-labels and compare against the gate's decision.

---

### Exercise 2 — Grade documents and log pass/fail counts (easy → medium)

Take a fixed corpus where you *know* which docs are relevant to a query. Run
`grade_doc_relevance` over all of them and log, per query, `N pass / M fail`.
Then deliberately add two obviously off-topic documents and confirm they get
graded `fail`.

> **Hint:** `code/02_corrective_rag.py` already seeds relevant *and* off-topic
> docs — extend the corpus and assert the off-topic ones score `fail`.

---

### Exercise 3 — Add a web-search fallback when relevance is thin (medium)

Wire the CRAG correction step so that when fewer than 2 docs pass grading, the
pipeline supplements with a (mock) web search and tags the answer's sources as
`index + web`. Craft one query the index *can* answer (no fallback) and one it
*cannot* (fallback fires), and verify the source tag differs between them.

> **Hint:** Toggle the `MIN_RELEVANT_DOCS` threshold and watch how often the
> fallback triggers; a query with no matching index docs should always supplement.

---

### Exercise 4 — Build a 3-tool agentic-RAG agent (medium → hard)

Create three tools — `search_pdf_docs`, `search_web`, `query_database` — and
hand them to an agent. Run four questions engineered so that each routes
differently: one PDF-only, one web-only, one DB-only, and one *compound*
question that forces two tools. Print which tool(s) the agent chose per
question.

> **Hint:** The tool **docstrings** are what the agent reads to route — make
> each one crisp and non-overlapping, then verify the compound question calls
> exactly two tools.

---

### Exercise 5 — Add a hallucination / grounding check before returning (hard)

After generation, add a `is_grounded(answer, context)` check that asks the LLM
whether every claim in the answer is supported by the supplied context. If it
returns `False`, do **not** return the answer — either re-retrieve once or
return an explicit "insufficient evidence" message. Test it by feeding the
generator context that does *not* contain the answer and confirming the check
catches the fabrication.

> **Hint:** A grounding grader is structurally the same prompt as your
> relevance grader — `Answer ONLY: grounded or hallucinated` — just comparing
> answer-vs-context instead of doc-vs-query.

---

### Exercise 6 — Assemble the full Advanced RAG pipeline (hard)

Combine Exercises 1–5 into one function that runs the complete decision flow
from `diagrams.md`: adaptive gate → (retrieve → grade → correct) → generate →
grounding check → answer with provenance. Add a hard cap so the
hallucination→re-retrieve loop can run at most **once** (no infinite loops),
and log every decision the pipeline made for a single query so the path is
fully auditable.

> **Hint:** Treat each stage as a guard that can short-circuit — the gate can
> skip retrieval, grading can trigger the web fallback, the grounding check can
> force one retry; log a one-line decision record at each guard.
