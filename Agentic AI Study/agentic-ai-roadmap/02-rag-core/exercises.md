# Phase 2 — RAG Core: Exercises

Work these in order, easy → hard. Each is **new** (not a repeat of the Phase 2
checklist). One hint per exercise, no solutions — struggle a little, that's where
the learning is. You can do every one of these against the offline mocks in
`code/` (set `USE_MOCK = True`); swap in real loaders/embeddings only when you
want to see real numbers.

---

### Exercise 1 — Load a mixed corpus (easy)

Build a single `list[Document]` from **three different source types** at once:
one hand-written `Document`, one in-memory "CSV row" turned into a `Document`,
and one fake "web page" (just a multi-paragraph string). Give each a distinct
`source` in metadata, then print a table of `(source, char_count)` for every
document.

> Hint: every loader ultimately returns the same shape — `page_content` +
> `metadata` — so you can fabricate `Document` objects by hand to simulate any
> source.

---

### Exercise 2 — Tune chunk size & overlap, watch the boundaries (easy→medium)

Take one long paragraph (~800 chars). Split it three ways: `(size=200,
overlap=0)`, `(size=200, overlap=50)`, `(size=400, overlap=80)`. For each
config print the chunk count and the **last 20 chars of chunk N + first 20 chars
of chunk N+1** so you can literally see what the overlap preserves (or what
zero-overlap loses). Write one sentence on which config you'd ship and why.

> Hint: with `overlap=0`, find a sentence that gets cut in half across a
> boundary — that orphaned half is exactly the failure overlap prevents.

---

### Exercise 3 — Compute cosine similarity by hand (medium)

Without calling any embedding model, hand-write three 4-dimensional vectors:
two that should be "similar" (point roughly the same way) and one that's
"different." Implement cosine similarity from the formula
`dot(a,b) / (||a|| * ||b||)` yourself (no numpy), and assert that the similar
pair scores higher than either-vs-the-different one. Then re-run using the mock
embedder on real sentences and confirm the same ordering holds.

> Hint: do the arithmetic for `[1,1,0,0]` vs `[1,1,0,0]` first — you should get
> exactly `1.0`. Use that as your sanity check before trying unequal vectors.

---

### Exercise 4 — Persist and reload a store, prove it survived (medium)

Build a vector store over your Exercise 1 corpus, run a query, and record the
top result. Now **persist** it, tear down the object, **reload from disk**, and
run the identical query. Assert the top result is the same — proving you didn't
silently rebuild. Then deliberately delete/rename the persist directory and show
that reload now returns nothing (or rebuilds), so you *feel* what
`persist_directory` actually buys you.

> Hint: with the offline mock, "persist" can be pickling the store's
> `(documents, vectors)` to a file and reloading it; the lesson is the round-trip,
> not the specific backend.

---

### Exercise 5 — Build an LCEL chain end to end, then break the pipe (medium→hard)

Compose a chain with the pipe syntax: `retriever | format_docs` for context,
`RunnablePassthrough()` for the question, then prompt → llm → parser. Run a
question that IS answerable from your corpus and one that ISN'T, and confirm the
second returns the "I don't have that information" fallback. Then intentionally
**remove `format_docs`** from the pipe and observe how the chain breaks — explain
in one sentence what stage was relying on a string vs a list of `Document`s.

> Hint: think of `|` like a `Stream` pipeline — every stage's *output type* must
> match the next stage's *input type*; removing `format_docs` feeds raw
> `Document` objects where a string was expected.

---

### Exercise 6 — Metadata filtering + a conversational follow-up (hard)

Build a corpus where the words "policy" and "shipping" both appear in several
chunks across different `section` metadata values. (a) Show that an *unfiltered*
query about shipping accidentally surfaces a returns chunk; (b) add a metadata
filter `{"section": "shipping"}` and show the contamination disappears. Then
wrap it in a conversational chain: Turn 1 = "What's the shipping cost?", Turn 2 =
"How long does **it** take?" — and verify "it" resolves to shipping (not
returns) because history is carried into retrieval.

> Hint: the follow-up only works if the chain *condenses* "it" using the previous
> turn before retrieving — inspect/print the rewritten standalone question to
> confirm the coreference resolved.
