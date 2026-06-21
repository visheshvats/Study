# Phase 2 — RAG Core: Notes

> Mentor track for an enterprise Java/Spring Boot engineer. Read this prose-first,
> then run the matching files in `code/`. Every concept is anchored to something
> you already know from JVM-land.

---

## Why this matters

An LLM on its own has a frozen brain. It knows whatever it saw during training
and nothing about *your* world: your refund policy, last night's deploy notes,
the customer's order history. Worse, when it doesn't know, it tends to make
something up confidently (hallucinate). That is unacceptable for the kind of
systems you build.

**Retrieval-Augmented Generation (RAG)** fixes this by giving the LLM a
searchable long-term memory. Instead of asking the model to *recall* an answer,
you first *retrieve* the relevant documents from a store you control, paste them
into the prompt as context, and ask the model to answer **using only that
context**. The model becomes a reasoning engine over *your* data rather than a
trivia machine.

The cleanest Java analogy: RAG is a **read-through cache backed by a search
index feeding a service call**.

- Your documents are the system of record (the database/files).
- The vector store is a **search index** — think Elasticsearch/Lucene, except
  the "match" is *semantic similarity* over dense numeric vectors instead of an
  inverted token index.
- At request time you query the index for the few most relevant chunks (a
  cache/index lookup), assemble them into a prompt, and call the LLM (the
  downstream service). The LLM never sees your whole corpus — only the handful
  of chunks the retriever judged relevant, exactly like a service that fetches
  only the rows it needs rather than `SELECT *`.

If you internalise one sentence: **RAG = search index + prompt assembly + LLM
call.** The rest of this phase is the plumbing for those three boxes.

---

## RAG architecture: two phases, two clocks

The single most important mental model in this phase is that RAG runs on **two
separate clocks**. Confusing them is the root of most beginner bugs.

### Indexing (build time — runs occasionally)

This is the "ETL / index build" job. You run it when your documents change, not
on every user request.

```
Documents (PDF/CSV/Web)  ->  Loaders  ->  Text Splitter (chunks + overlap)
                         ->  Embeddings Model (text -> vector)
                         ->  Vector DB (Chroma / FAISS)
```

Think of this like building a Lucene index or running a nightly batch that
populates a materialised view. It is comparatively slow and possibly expensive
(you pay the embedding model per chunk), so you do it once and **persist** the
result to disk.

### Retrieval + Generation (query time — runs per request)

This is the hot path that executes on every user question.

```
User Query  ->  Embed Query (SAME model)  ->  Top-K Retrieval (cosine similarity)
            ->  Context + Query -> Prompt  ->  LLM  ->  Answer
```

This is your request-scoped service method. It must be fast, and it must use the
**same embedding model** that built the index — more on why below.

The rule of thumb: anything involving *your documents* is indexing; anything
involving *the user's question right now* is query time. See `diagrams.md` for
both flows drawn out, including a runtime sequence diagram.

---

## 2.1 Document loading — adapters that normalise every source

The first stage turns messy real-world inputs (PDFs, CSV exports, web pages,
hand-written snippets) into one uniform domain object: the **`Document`**, which
is just `page_content` (the text) plus `metadata` (a dict: source, page,
section, year, …).

```python
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, WebBaseLoader
pdf_docs = PyPDFLoader("./docs/user_manual.pdf").load()
```

**Java analogy:** loaders are **adapters / Spring Data repositories**. A
`PyPDFLoader` is a `PdfRepository`, a `CSVLoader` is a `CsvRepository`. Each one
speaks a different backend protocol but they all hand back the same `Document`
type — just like every Spring Data repo returns your `@Entity` regardless of the
store underneath. `DirectoryLoader(glob="**/*.pdf", loader_cls=PyPDFLoader)` is
the batch variant that walks a tree and applies one loader per file.

The thing to *care* about here is **metadata**. The `metadata` dict is not
decoration — it is what powers filtering later ("only search the returns
section", "only documents from 2024"). Treat it like the indexed columns on a
table: decide up front what you'll want to filter or cite by, and make sure your
loaders populate it. `CSVLoader(metadata_columns=["product_id", "category"])`
promotes columns straight into metadata.

See `code/01_document_loading.py`. It runs offline with an in-memory corpus and
shows the real loader calls (commented for when you have files).

---

## 2.2 Text splitting — windowing with deliberate overlap

Loaders give you whole pages or whole files. But you don't want to embed a
20-page PDF as one vector (the meaning gets averaged into mush) and you can't
paste 20 pages into a prompt. So you **split** the text into smaller **chunks**.

Two knobs decide everything:

- **`chunk_size`** — how big each window is (commonly measured in characters or
  tokens). The source guide uses `1000` chars ≈ 750 words as a default.
- **`chunk_overlap`** — how much of the end of one chunk repeats at the start of
  the next (the guide uses `200`, i.e. 20%). Overlap exists so a sentence that
  straddles a boundary isn't orphaned — both chunks carry enough context to
  stand alone.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
chunks = splitter.split_documents(pdf_docs)
```

Use **`RecursiveCharacterTextSplitter` by default.** "Recursive" means it tries
separators in priority order — paragraph break `\n\n`, then line `\n`, then
sentence `. `, then space, then raw character — so it cuts on natural boundaries
whenever it can instead of slicing mid-word. `TokenTextSplitter` exists for when
you need to respect an exact *token* budget (e.g. a model's context limit) rather
than character counts.

**Java analogy:** splitting is a **sliding window over a stream** — like
`Lists.partition(list, size)` but where consecutive partitions deliberately
*share a tail*. The overlap is the slide that's smaller than the window.

### The chunk-size tradeoff (this is where judgement lives)

- **Too large** → the context window fills fast and retrieval gets imprecise:
  you pull in a wall of text where only one sentence mattered, diluting the
  signal and burning tokens.
- **Too small** → chunks lose their surrounding context and meaning collapses
  ("…30 days." — 30 days of *what*?).
- **Practical default:** 500–1500 characters, overlap = 10–20% of `chunk_size`.

`code/02_text_splitting.py` uses deliberately small sizes so you can *see* the
overlap in the printed output. Change the numbers and re-run — feeling the
boundaries is the lesson.

---

## 2.3 Embeddings & cosine similarity — the heart of retrieval

An **embedding** is a function that turns text into a fixed-length list of
numbers (a **vector**) that encodes *meaning*. OpenAI's
`text-embedding-3-small` produces 1536-dimensional vectors. The magic property:
texts with similar meaning get vectors that point in similar *directions*.

```python
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vec = embeddings.embed_query("Python is a programming language")  # -> [0.013, -0.04, ...] (1536 floats)
```

**Java analogy:** an embedding model is a deterministic
`Function<String, double[]>`. Same text in, same vector out.

To compare two vectors you use **cosine similarity** — the cosine of the angle
between them, a number in `[-1, 1]` where `1.0` means "same direction / same
meaning" and `~0` means "unrelated":

```python
def cosine_sim(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

With real embeddings: *"Python is a programming language"* vs *"Django is a
Python web framework"* scores ~0.87 (HIGH — both about tech), while *"Python is
a programming language"* vs *"A snake is a reptile with no legs"* scores ~0.30
(LOW — different meaning despite sharing the word "Python").

**Java analogy + the critical caveat:** cosine similarity is your **comparator /
score function** — like a custom `Comparator<double[]>` you sort search hits by.
But it is a *fuzzy ranking score, not `equals()`*. There is no exact hit/miss
the way `map.get(key)` either finds the key or doesn't. A score of 0.83 means
"very close in meaning"; you choose a `top-k` cutoff, you don't get a boolean
match. Treating cosine like SQL `WHERE col = value` is the #1 conceptual error
Java devs make here (see the callout below).

`code/03_embeddings_cosine.py` **actually computes and prints** these
similarities using a deterministic offline mock embedder, so the high-vs-low
lesson lands without an API key. The mock isn't semantic (it's bag-of-words),
but it preserves the ordering — related text still scores higher than unrelated
text, which is the whole point.

---

## 2.4 Vector store — the search index you persist

A **vector store** holds your chunk embeddings and answers one question fast:
"give me the `k` chunks whose vectors are most similar to this query vector."
It is the index in RAG.

**Java analogy:** this is **Elasticsearch / Lucene**, with cosine similarity
over dense vectors instead of an inverted token index. `as_retriever(...)` is a
configured query handle (a prepared `SearchRequest`).

### Chroma — persists to disk (great for dev)

```python
from langchain_community.vectorstores import Chroma
vectorstore = Chroma.from_documents(
    documents=chunks, embedding=embeddings,
    collection_name="product_docs",
    persist_directory="./chroma_db",   # <-- survives restarts
)
# Later, reload WITHOUT re-embedding:
vectorstore = Chroma(collection_name="product_docs",
                     embedding_function=embeddings, persist_directory="./chroma_db")
```

`persist_directory` is the on-disk index directory. **Omit it and your index
lives only in memory and vanishes when the process exits** — you'll silently
re-embed your whole corpus on every run and pay for it. It's the Lucene index
dir: lose it and you must rebuild.

### Retrieval modes

```python
retriever_basic = vectorstore.as_retriever(search_kwargs={"k": 4})            # plain top-k
retriever_mmr   = vectorstore.as_retriever(search_type="mmr",
                                           search_kwargs={"k": 6, "fetch_k": 20})
retriever_filtered = vectorstore.as_retriever(
    search_kwargs={"k": 4, "filter": {"section": "returns"}})                 # metadata filter
```

- **Basic top-k** — return the `k` highest-scoring chunks. Simple and usually
  fine.
- **MMR (Max Marginal Relevance)** — fetches a wider candidate pool (`fetch_k`)
  then greedily picks results that are *relevant AND not near-duplicates* of
  what's already chosen. Use it when your corpus has lots of repetitive text and
  plain top-k keeps returning five paraphrases of the same paragraph. It trades
  a little relevance for diversity.
- **Metadata filtering** — restrict the search to chunks whose metadata matches
  (`{"section": "returns"}`). *This* is your `WHERE` clause — pre-filter on
  metadata, then rank the survivors by cosine similarity. It's the right tool
  when you mean "exact match on a field," which cosine similarity is not.

### FAISS — fast in-memory index

```python
from langchain_community.vectorstores import FAISS
faiss_store = FAISS.from_documents(chunks, embeddings)
faiss_store.save_local("./faiss_index")
faiss_loaded = FAISS.load_local("./faiss_index", embeddings,
                                allow_dangerous_deserialization=True)
```

FAISS (from Facebook AI) is a fast approximate-nearest-neighbour library, great
for high-throughput in-memory search. It saves/loads explicitly. Note
`allow_dangerous_deserialization=True`: loading a FAISS index unpickles Python
objects, which can execute arbitrary code. **Only ever enable this for index
files you created yourself.** Loading one from an untrusted source is a remote
code execution vector — treat it exactly like you'd treat Java
deserialization of untrusted bytes (the classic `readObject` gadget-chain RCE).

`code/04_vector_store.py` demonstrates top-k, MMR, and metadata filtering with
an offline in-memory store, and shows the real Chroma+FAISS calls commented.

---

## 2.5 Basic RAG chain with LCEL — composing the query pipeline

Now assemble the query-time path: take a question, retrieve chunks, format them
into context, fill a prompt, call the LLM, parse the text out. LangChain wires
these stages with **LCEL (LangChain Expression Language)** and the `|` pipe.

```python
rag_chain = (
    {
        "context": retriever_basic | format_docs,   # retrieve, then stringify
        "question": RunnablePassthrough(),           # forward the raw question untouched
    }
    | RAG_PROMPT          # fill the template
    | llm                 # call Claude
    | StrOutputParser()   # extract plain text
)
answer = rag_chain.invoke("What is the return policy?")
```

**Java analogy:** the `|` pipe *is* a **fluent builder / `Stream` pipeline**.
Reading `retriever | format_docs | prompt | llm | parser` is exactly like
reading `stream.map(...).filter(...).map(...).collect(...)` — each stage's output
is the next stage's input. The leading `{...}` dict is a **fan-out**: it computes
both keys in parallel (one branch runs retrieval and formatting, the other passes
the question straight through) and hands a populated map downstream — like
building a DTO from two service calls before passing it to the next layer.

- **`format_docs(docs)`** joins the retrieved `Document` list into one labelled
  string the prompt can interpolate (and tags each with its source for
  citation).
- **`RunnablePassthrough()`** is the **identity function** — it forwards its
  input untouched. Here it carries the raw question so the prompt sees the
  question *and* the retrieved context.
- The prompt instructs the model to answer **only** from the context and to say
  "I don't have that information" otherwise. This anti-hallucination instruction
  is the whole reason RAG is trustworthy — keep it.

`code/05_basic_rag_chain.py` runs the full pipe offline with a stub LLM that
echoes retrieved context, and shows the real LCEL chain with `ChatAnthropic`.

---

## 2.6 Conversational RAG — adding memory

The basic chain is **stateless**: every question is answered in isolation. Real
conversations have follow-ups. "How long does *it* take to process?" only makes
sense if you remember the previous turn was about "the return policy."

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(memory_key="chat_history",
                                        return_messages=True, k=5)  # last 5 exchanges
conv_chain = ConversationalRetrievalChain.from_llm(
    llm=llm, retriever=retriever, memory=memory, return_source_documents=True)
```

Under the hood the chain does an extra step: it uses the chat history to
**condense the follow-up into a standalone question** ("How long does *it* take?"
→ "How long does *a return* take to process?"), *then* retrieves and answers.
That rewrite is why coreference ("it", "that") resolves correctly.

**Java analogy:** memory is your **`HttpSession` / conversation-scoped bean**.
The basic chain is a stateless `@RestController` endpoint; conversational RAG is
the same endpoint backed by a session that accumulates context.
`ConversationBufferWindowMemory(k=5)` is a **bounded** session — a sliding window
that keeps only the last 5 exchanges so context (and token cost) stays bounded,
like an LRU-capped cache rather than an unbounded list. (Unbounded memory is a
real cost and latency bug: every turn re-sends the whole history to the model.)

`return_source_documents=True` gives you the chunks used per answer — keep it
on so you can cite and debug. `code/06_conversational_rag.py` demonstrates the
two-turn flow offline (showing the "it" rewrite) and the real
`ConversationalRetrievalChain`.

---

## ⚠️ Common Java-dev mistakes

- **Chunk too large** → retrieval pulls in a wall of text, drowning the relevant
  sentence and burning context-window tokens. Precision drops.
- **Chunk too small** → chunks lose surrounding context and become meaningless
  ("…within 30 days." — of what?). Start at 500–1500 chars, overlap 10–20%.
- **Mismatched embedding model between index and query** → THE silent killer.
  You must embed the query with the *exact same model* that built the index.
  Different models produce different vector spaces; cosine similarity across them
  is garbage and retrieval silently returns nonsense (no exception, just wrong
  answers). It's like comparing hashes from two different hash functions.
- **Forgetting `persist_directory`** → your Chroma index lives only in memory,
  vanishes on process exit, and you re-embed (and re-pay for) the whole corpus
  every run without realising it.
- **Treating cosine distance like SQL equality** → cosine is a *fuzzy ranking
  score* in `[-1, 1]`, not a boolean match. There's no `WHERE vec = ?`. If you
  want exact field matching, that's **metadata filtering**, not similarity.
- **Loading the whole corpus into memory** → don't `load()` a giant directory and
  hold every `Document` plus every vector in RAM. Stream/batch the indexing job;
  persist to disk; at query time only the top-k chunks come back. RAG exists
  precisely so the LLM never sees the whole corpus.
- **Ignoring metadata filters** → without filtering, a question about "shipping"
  can retrieve "returns" chunks that happen to be lexically close. Populate
  metadata at load time and filter at query time — it's your `WHERE` clause.
- **`allow_dangerous_deserialization=True` on untrusted FAISS files** → this
  unpickles arbitrary Python objects and can execute arbitrary code. Only enable
  it for index files YOU created. Treat untrusted index files like untrusted Java
  serialized bytes — a remote-code-execution gadget waiting to fire.

---

## Key terms

- **Embedding** — a function that maps text to a fixed-length numeric vector
  encoding meaning; a deterministic `Function<String, double[]>`.
- **Vector** — that list of floats (e.g. 1536-dim). A point/direction in
  high-dimensional "meaning space."
- **Cosine similarity** — cosine of the angle between two vectors, in `[-1, 1]`;
  `1.0` = same meaning, `~0` = unrelated. A fuzzy ranking score, not `equals()`.
- **Chunk** — a small slice of a document that gets embedded and retrieved as a
  unit.
- **Overlap** — the repeated text shared between consecutive chunks so boundary
  sentences keep their context.
- **Vector store** — the database/index of chunk embeddings that answers
  nearest-neighbour queries (Chroma, FAISS). Your Lucene-for-vectors.
- **Retriever** — the configured query handle over a vector store
  (`as_retriever(...)`); given a query, returns relevant `Document`s.
- **Top-k** — return the `k` highest-scoring chunks for a query.
- **MMR (Max Marginal Relevance)** — retrieval mode that balances relevance
  against diversity to avoid returning near-duplicate chunks.
- **LCEL (LangChain Expression Language)** — the `|`-pipe DSL for composing
  runnables into a chain; reads like a `Stream` pipeline / fluent builder.
- **`RunnablePassthrough`** — the identity runnable; forwards its input unchanged
  (used to carry the raw question alongside retrieved context).
- **Conversational memory** — state that accumulates chat history across turns so
  follow-ups resolve; `ConversationBufferWindowMemory(k=N)` is a bounded sliding
  window, like an LRU-capped session.
