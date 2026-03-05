# MODULE 3: RAG (Retrieval Augmented Generation) — Complete Notes

> **For:** Engineers who completed Modules 0-2 and are ready to build the #1 production LLM pattern.  
> **Key insight:** RAG = "Give the LLM a cheat sheet before it answers."
> It's how ChatGPT, Perplexity, and every enterprise AI assistant actually work.

---

# LESSON 3.1: What is RAG and Why It Exists

## The Problem RAG Solves

LLMs have three critical limitations:

```
┌─────────────────────────────────────────────────────────────┐
│  LLM LIMITATIONS THAT RAG SOLVES                            │
│                                                              │
│  1. KNOWLEDGE CUTOFF                                        │
│     GPT-4 was trained on data up to a certain date.         │
│     It doesn't know what happened yesterday.                │
│     "What were our Q4 2025 revenue numbers?" → ❌           │
│                                                              │
│  2. NO ACCESS TO YOUR DATA                                  │
│     It never saw your company's internal docs, Jira,        │
│     Confluence, codebase, or database.                      │
│     "What does our UserService.java do?" → ❌               │
│                                                              │
│  3. HALLUCINATION                                           │
│     When it doesn't know, it makes things up confidently.   │
│     "What's our refund policy?" → 🤖 Invents a policy      │
│                                                              │
│  RAG SOLUTION: Retrieve relevant documents FIRST,           │
│  then give them to the LLM as context.                      │
│  Now it answers from YOUR data, not its imagination.        │
└─────────────────────────────────────────────────────────────┘
```

---

## What is RAG?

**Simple:** Before asking the LLM a question, you **search your own documents**, find the
most relevant pieces, and **paste them into the prompt** as context. The LLM then answers
based on those documents.

**One sentence:** RAG = Search + LLM.

```
WITHOUT RAG:                         WITH RAG:

User: "What's our refund policy?"    User: "What's our refund policy?"
         │                                    │
         ▼                                    ▼
    ┌─────────┐                         ┌──────────┐
    │   LLM   │                         │  SEARCH  │ ← Vector DB
    │         │                         │ your docs│
    │ (guesses│                         └────┬─────┘
    │  or     │                              │
    │  hallu- │                         Found: "Refund policy: Full
    │  cinates│                         refund within 30 days..."
    │)        │                              │
    └────┬────┘                              ▼
         │                             ┌──────────┐
         ▼                             │   LLM    │
  "Our refund policy                   │          │
   is 60 days..."                      │ (answers │
   ← WRONG! Made up!                  │  FROM    │
                                       │  the doc)│
                                       └────┬─────┘
                                            │
                                            ▼
                                    "Our refund policy is
                                     30 days full refund..."
                                     ← CORRECT! From real data!
```

---

## RAG Architecture — The Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAG ARCHITECTURE                             │
│                                                                  │
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║  OFFLINE PIPELINE (run once, or on schedule)              ║  │
│  ║                                                            ║  │
│  ║  Raw Documents                                            ║  │
│  ║  (PDF, TXT, HTML,      ┌───────────┐     ┌────────────┐  ║  │
│  ║   Markdown, Code,  ──▶ │  CHUNKER  │ ──▶ │ EMBEDDING  │  ║  │
│  ║   Confluence, DB)       │           │     │   MODEL    │  ║  │
│  ║                         │ Split into│     │            │  ║  │
│  ║                         │ 200-500   │     │ text→vector│  ║  │
│  ║                         │ token     │     │            │  ║  │
│  ║                         │ chunks    │     └──────┬─────┘  ║  │
│  ║                         └───────────┘            │        ║  │
│  ║                                                  ▼        ║  │
│  ║                                           ┌───────────┐   ║  │
│  ║                                           │ VECTOR DB │   ║  │
│  ║                                           │ (ChromaDB,│   ║  │
│  ║                                           │  Pinecone,│   ║  │
│  ║                                           │  FAISS)   │   ║  │
│  ║                                           └───────────┘   ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
│                                                  │               │
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║  ONLINE PIPELINE (runs per user query)                    ║  │
│  ║                                                            ║  │
│  ║  User Query                                               ║  │
│  ║  "What's our          ┌───────────┐     ┌────────────┐   ║  │
│  ║   refund policy?" ──▶ │ EMBEDDING │ ──▶ │ VECTOR DB  │   ║  │
│  ║                        │  MODEL    │     │  SEARCH    │   ║  │
│  ║                        └───────────┘     └──────┬─────┘   ║  │
│  ║                                                 │         ║  │
│  ║                                    Top-K relevant chunks  ║  │
│  ║                                                 │         ║  │
│  ║                                          ┌──────▼─────┐   ║  │
│  ║                                          │  RERANKER   │   ║  │
│  ║                                          │ (optional)  │   ║  │
│  ║                                          └──────┬─────┘   ║  │
│  ║                                                 │         ║  │
│  ║                            Best chunks + User query       ║  │
│  ║                                                 │         ║  │
│  ║                                          ┌──────▼─────┐   ║  │
│  ║                                          │    LLM     │   ║  │
│  ║                                          │ (GPT-4o,   │   ║  │
│  ║                                          │  Claude)   │   ║  │
│  ║                                          └──────┬─────┘   ║  │
│  ║                                                 │         ║  │
│  ║                                          ┌──────▼─────┐   ║  │
│  ║                                          │  RESPONSE  │   ║  │
│  ║                                          │ + Sources  │   ║  │
│  ║                                          └────────────┘   ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
└─────────────────────────────────────────────────────────────────┘
```

**Java Analogy:** RAG is like the **Backend for Frontend (BFF) pattern** in microservices.
Your BFF (the RAG pipeline) fetches data from multiple backend services (vector DB), 
aggregates it, and passes it to the client (LLM) in a format it can consume.

---

## The RAG Prompt Pattern

The LLM never sees the vector DB. It just sees a specially crafted prompt:

```
SYSTEM: "You are a helpful assistant. Answer questions based ONLY
         on the provided context. If the answer is not in the context,
         say 'I don't have enough information to answer that.'"

USER:   "Context (retrieved documents):
         ---
         Document 1: [Refund policy text from your vector DB]
         Document 2: [Related customer service guidelines]
         Document 3: [FAQ about returns]
         ---
         
         Question: What's our refund policy?
         
         Answer based on the context above:"
```

That's it. RAG is literally **search + paste into prompt + ask LLM**.

---

# LESSON 3.2: Chunking Strategies — The Make-or-Break Detail

## Why Chunking Matters

Chunking is the **most important** detail in RAG. Bad chunks = bad retrieval = bad answers.

```
┌─────────────────────────────────────────────────────────────┐
│  WHY CHUNKING MATTERS                                       │
│                                                              │
│  TOO BIG (whole document as one chunk):                     │
│  ❌ Embedding is diluted — averages all topics              │
│  ❌ Wastes context window — includes irrelevant text        │
│  ❌ Search returns entire doc when you need one paragraph   │
│                                                              │
│  TOO SMALL (every sentence is a chunk):                     │
│  ❌ Chunks lack context — "It was great" → what was great?  │
│  ❌ More chunks = more storage = higher cost                │
│  ❌ Related info split across chunks                        │
│                                                              │
│  JUST RIGHT (200-500 tokens with overlap):                  │
│  ✅ Each chunk has enough context to be meaningful          │
│  ✅ Embeddings are focused on specific topics               │
│  ✅ Overlap ensures nothing falls through the cracks        │
└─────────────────────────────────────────────────────────────┘
```

---

## Chunking Strategies

### Strategy 1: Fixed-Size Chunking

```
Text: "AAAA BBBB CCCC DDDD EEEE FFFF GGGG HHHH"

Chunk size: 4 words, Overlap: 1 word

Chunk 1: "AAAA BBBB CCCC DDDD"
Chunk 2: "DDDD EEEE FFFF GGGG"   ← "DDDD" overlaps
Chunk 3: "GGGG HHHH"

Simple but may cut mid-sentence.
```

### Strategy 2: Sentence-Based Chunking

```
Split by sentences first, then group into chunks.

Sentences: [S1, S2, S3, S4, S5, S6, S7, S8]

Chunk 1: [S1, S2, S3]     ← Complete sentences
Chunk 2: [S3, S4, S5]     ← S3 overlaps for context continuity
Chunk 3: [S5, S6, S7, S8] ← S5 overlaps

Better — never cuts mid-sentence.
```

### Strategy 3: Semantic Chunking (Advanced)

```
Use embeddings to detect topic shifts.

Text:  [Java intro] [Java syntax] [Java OOP] [Python intro] [Python syntax]
                                            ↑
                                     Topic shift detected!
                                  
Chunk 1: [Java intro + syntax + OOP]    ← One coherent topic
Chunk 2: [Python intro + syntax]         ← Different topic

Best quality but more expensive (requires embeddings during chunking).
```

### Strategy 4: Document-Structure Chunking

```
Use existing document structure (headings, sections).

Markdown:
# Chapter 1         ← Chunk boundary
## Section 1.1      ← Sub-chunk
## Section 1.2      ← Sub-chunk  
# Chapter 2         ← Chunk boundary

Preserves the author's intended organization.
Best for well-structured documents (docs, wikis, etc).
```

### Chunking Decision Matrix

| Strategy | Quality | Speed | Best For |
|----------|---------|-------|----------|
| Fixed-size | ⭐⭐ | ⭐⭐⭐⭐⭐ | Quick prototypes |
| Sentence-based | ⭐⭐⭐ | ⭐⭐⭐⭐ | General purpose (recommended default) |
| Semantic | ⭐⭐⭐⭐⭐ | ⭐⭐ | High-quality production systems |
| Structure-based | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Markdown, HTML, structured docs |

### Optimal Chunk Sizes

| Content Type | Chunk Size | Overlap |
|-------------|-----------|---------|
| Technical docs | 300-500 tokens | 50-100 tokens |
| Legal contracts | 200-400 tokens | 100 tokens |
| Code files | Per function/class | Include imports |
| FAQs | One Q&A pair per chunk | None |
| Chat logs | Per conversation turn | 1-2 turns |

---

# LESSON 3.3: Indexing, Retrieval, and Reranking

## Indexing — The Offline Step

```
┌─────────────────────────────────────────────────────┐
│  INDEXING PIPELINE                                   │
│                                                      │
│  1. LOAD documents (PDF, TXT, HTML, DB...)          │
│     ↓                                                │
│  2. CLEAN (strip HTML, fix encoding, remove noise)  │
│     ↓                                                │
│  3. CHUNK (split into optimal-sized pieces)         │
│     ↓                                                │
│  4. ENRICH (add metadata: source, date, topic)      │
│     ↓                                                │
│  5. EMBED (convert chunks to vectors)               │
│     ↓                                                │
│  6. STORE (save in vector DB with metadata)         │
│                                                      │
│  Java Analogy:                                      │
│  This is like an ETL pipeline:                      │
│    Extract (load) → Transform (chunk) → Load (store)│
└─────────────────────────────────────────────────────┘
```

---

## Retrieval — The Online Step

```
┌─────────────────────────────────────────────────────┐
│  RETRIEVAL STRATEGIES                                │
│                                                      │
│  1. BASIC: Embed query → Search top-K → Done        │
│     Simple, works for most cases.                   │
│                                                      │
│  2. HYBRID: Vector search + Keyword search (BM25)   │
│     Combines semantic AND exact matching.            │
│     Best of both worlds.                            │
│                                                      │
│  3. MULTI-QUERY: Generate multiple search queries    │
│     from one user question for broader coverage.     │
│     "Tell me about auth" →                          │
│       Query 1: "authentication methods"             │
│       Query 2: "OAuth2 configuration"               │
│       Query 3: "login security"                     │
│                                                      │
│  4. CONTEXTUAL: Include conversation history        │
│     in the search query for follow-up questions.    │
│     "And what about the timeout?"                   │
│     → Rephrased: "What is the timeout for the       │
│       Kafka consumer group rebalancing?"            │
│                                                      │
│  5. PARENT-CHILD: Retrieve small chunks,            │
│     but return parent (larger) chunks for context.   │
│     Search on focused embeddings, return full docs.  │
└─────────────────────────────────────────────────────┘
```

---

## Reranking — The Quality Booster

```
┌─────────────────────────────────────────────────────┐
│  WHY RERANKING?                                      │
│                                                      │
│  Vector search returns "approximately similar" docs.│
│  Reranking does a DEEPER comparison:                │
│                                                      │
│  Step 1: Vector search → 20 candidates (fast)      │
│  Step 2: Reranker scores each one (slower, better)  │
│  Step 3: Keep top 5 (best quality)                  │
│                                                      │
│  Analogy:                                            │
│  - Vector search = scanning 1000 resumes by keyword │
│  - Reranking = carefully reading the top 20         │
│                                                      │
│  Reranking models:                                  │
│  • Cohere Rerank API                                │
│  • Cross-encoder models (more accurate than         │
│    bi-encoder embeddings)                           │
│  • LLM-based reranking ("which docs best answer     │
│    this question?")                                 │
└─────────────────────────────────────────────────────┘
```

---

# LESSON 3.4: Advanced RAG Patterns

## Pattern 1: Naive RAG vs Advanced RAG

```
NAIVE RAG (starter):
  Query → Embed → Search → Top-K → Prompt → LLM → Answer
  
  Problems:
  ❌ Poor chunking = irrelevant retrieval
  ❌ No query reformulation
  ❌ No reranking
  ❌ Lost context in follow-up questions

ADVANCED RAG:
  Query → Rephrase → Multi-Query → Embed → Search → Rerank 
       → Filter → Prompt Engineer → LLM → Validate → Answer
  
  Improvements:
  ✅ Query rewriting for clarity
  ✅ Multiple search queries for coverage
  ✅ Reranking for precision
  ✅ Source citation for trust
  ✅ Answer validation for accuracy
```

## Pattern 2: Conversational RAG

```
┌──────────────────────────────────────────────────────┐
│  CONVERSATIONAL RAG (with follow-up questions)       │
│                                                       │
│  Turn 1:                                             │
│    User: "Tell me about Kafka consumer groups"       │
│    → Search: "Kafka consumer groups"                 │
│    → LLM answers with retrieved docs                 │
│                                                       │
│  Turn 2:                                             │
│    User: "What happens when one goes down?"          │
│    → Problem: "one" and "goes down" are ambiguous!   │
│                                                       │
│    Solution: QUERY REFORMULATION                     │
│    → Use LLM to rewrite: "What happens when a       │
│      Kafka consumer group member goes down?          │
│      How does rebalancing work?"                     │
│    → Now search with the clear, standalone query     │
│                                                       │
│  Implementation:                                     │
│    history + vague query → LLM → standalone query    │
│    standalone query → Search → Retrieved docs        │
│    history + docs + query → LLM → Answer             │
└──────────────────────────────────────────────────────┘
```

## Pattern 3: RAG with Citations

```
SYSTEM PROMPT:
  "Answer based on the provided documents.
   After each claim, cite the source using [Source: filename].
   If you can't find the answer, say so."

LLM OUTPUT:
  "Kafka consumer groups allow parallel processing of 
  topic partitions [Source: kafka-guide.md]. Each consumer 
  in a group reads from different partitions, enabling 
  horizontal scaling [Source: kafka-guide.md]. The rebalancing 
  protocol redistributes partitions when consumers join 
  or leave [Source: kafka-advanced.md]."

WHY: Users can verify claims. Essential for enterprise.
```

## Pattern 4: Self-Reflecting RAG

```
┌──────────────────────────────────────────────────────┐
│  SELF-REFLECTING RAG (CRAG — Corrective RAG)        │
│                                                       │
│  1. Retrieve documents                               │
│  2. LLM evaluates: "Are these docs relevant?"       │
│     → If YES: Generate answer                        │
│     → If PARTIALLY: Supplement with web search       │
│     → If NO: Fall back to web search or "I don't     │
│       know"                                          │
│  3. Generate answer                                  │
│  4. LLM checks: "Does my answer match the docs?"    │
│     → If NO: Regenerate                              │
│                                                       │
│  More expensive but much more reliable.              │
└──────────────────────────────────────────────────────┘
```

---

## RAG vs Fine-Tuning — When to Use Which

```
┌──────────────────┬────────────────┬──────────────────┐
│                  │     RAG        │  FINE-TUNING     │
├──────────────────┼────────────────┼──────────────────┤
│ Data freshness   │ Real-time      │ Snapshot in time │
│ Setup cost       │ Low            │ High             │
│ Running cost     │ Per query      │ Per query (lower)│
│ Accuracy         │ High (sourced) │ Variable         │
│ Hallucination    │ Low (grounded) │ Can still happen │
│ Data privacy     │ Data stays     │ Data in model    │
│                  │ in your DB     │                  │
│ Best for         │ Q&A over docs  │ Style/behavior   │
│ Example          │ "Search our    │ "Respond like    │
│                  │  wiki and      │  our brand       │
│                  │  answer"       │  voice always"   │
└──────────────────┴────────────────┴──────────────────┘

RULE: Use RAG for knowledge. Use fine-tuning for behavior.
```

---

# LESSON 3.5: Code Examples

See the `code/` directory:

1. **`01_naive_rag.py`** — Simplest RAG implementation (20 lines of core logic)
2. **`02_chunking_strategies.py`** — Compare all chunking methods
3. **`03_advanced_rag.py`** — Multi-query, reranking, citations
4. **`04_rag_chatbot.py`** — **PROJECT:** Conversational RAG chatbot with document upload

---

# LESSON 3.6: Exercises

## Exercise 1: Concept Check
1. Explain RAG to a non-technical person in 2 sentences.
2. Why is chunking the most important detail in RAG?
3. What's the difference between retrieval and reranking?
4. When would you choose RAG over fine-tuning?

## Exercise 2: Chunking Experiment
1. Take a 2000-word document and chunk it 4 different ways
2. Create embeddings for each chunking strategy
3. Run 5 test queries and compare retrieval quality
4. Which strategy works best for your document type?

## Exercise 3: Build a RAG System
1. Collect 10+ documents on a topic you know well
2. Build a RAG pipeline with ChromaDB
3. Test with 20 questions (10 answerable from docs, 10 not)
4. Measure: Does it answer correctly? Does it say "I don't know" when appropriate?

---

# LESSON 3.7: Interview Questions & Answers

## Q1: What is RAG and why is it preferred over fine-tuning for most use cases?

**Answer:** RAG (Retrieval Augmented Generation) retrieves relevant documents from a
knowledge base and includes them in the LLM prompt as context. It's preferred because:
(1) No training needed — just index your documents, (2) Data stays fresh — update the
vector DB, not the model, (3) Data stays private — documents never leave your infrastructure,
(4) Reduced hallucination — answers are grounded in real documents, (5) Source attribution —
you can cite which documents were used. Fine-tuning is only better for changing the model's
*behavior* or *style*, not its *knowledge*.

## Q2: Walk me through the complete RAG pipeline, offline and online.

**Answer:** **Offline pipeline** (run once or on schedule): (1) Load documents from various
sources, (2) Clean and preprocess text, (3) Chunk into 200-500 token segments with overlap,
(4) Generate embeddings using an embedding model, (5) Store in vector DB with metadata.
**Online pipeline** (per user query): (1) Receive user question, (2) Optionally reformulate
query for clarity, (3) Embed the query, (4) Search vector DB for top-K similar chunks,
(5) Optionally rerank results for better precision, (6) Construct prompt with retrieved
context + question, (7) Send to LLM, (8) Return answer with source citations.

## Q3: What is chunking and how does poor chunking affect RAG quality?

**Answer:** Chunking is splitting documents into small, meaningful segments for embedding.
Poor chunking causes: (1) **Too large** — embeddings become diluted, mixing unrelated
topics, making retrieval imprecise, (2) **Too small** — chunks lack context, making them
meaningless ("It was great" — what was great?), (3) **Mid-sentence splits** — broken
grammar confuses both embedding and LLM, (4) **No overlap** — important context at chunk
boundaries is lost. Best practice: sentence-based chunking, 200-500 tokens, 10-20% overlap.

## Q4: How do you handle follow-up questions in conversational RAG?

**Answer:** Follow-up questions are often ambiguous ("What about the timeout?"). Solution:
**Query reformulation** — use an LLM to rewrite the vague query into a standalone search
query using conversation history. Pipeline: (1) Take chat history + latest question,
(2) LLM rephrases to standalone query, (3) Search with rephrased query, (4) LLM answers
using retrieved docs + full chat history. This ensures the retrieval step gets a clear,
searchable query.

## Q5: How do you evaluate RAG system quality?

**Answer:** Four dimensions: (1) **Retrieval quality** — are the right documents found?
Measure with precision@K, recall@K, MRR (Mean Reciprocal Rank), (2) **Answer quality** —
is the generated answer correct? Use LLM-as-judge or human evaluation, (3) **Faithfulness** —
does the answer stay true to the retrieved documents, or does it hallucinate?
(4) **Latency** — is it fast enough for users? Aim for <3 seconds end-to-end.
Frameworks like RAGAS automate this evaluation.

## Q6: What is hybrid search and when would you use it?

**Answer:** Hybrid search combines vector similarity search (semantic) with keyword search
(BM25/TF-IDF). Use it when: (1) Exact terms matter — searching for error code "ERR_4032"
semantically might miss it, keyword search finds it exactly, (2) Domain jargon — specialized
terms might not embed well, (3) Best of both worlds — BM25 catches exact matches, vector
search catches paraphrases. Most production RAG systems use hybrid search. Weaviate and
Pinecone support it natively.

---

# Real-World Production Use Cases

| Use Case | RAG Implementation | Company |
|----------|-------------------|---------|
| Internal Knowledge Base | Chat over company docs, Confluence, wiki | Notion AI, Glean |
| Customer Support | Answer from support docs, FAQ, tickets | Zendesk, Intercom |
| Legal Research | Search case law, contracts, regulations | Harvey AI |
| Code Assistant | Search codebase, docs, Stack Overflow | GitHub Copilot |
| Medical Q&A | Answer from medical literature, guidelines | Google Health |
| Financial Analysis | Query SEC filings, reports, earnings | Bloomberg |

---

# Common Mistakes

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| No chunking (embed whole docs) | Diluted embeddings, poor retrieval | Chunk to 200-500 tokens |
| No overlap between chunks | Context lost at boundaries | 10-20% overlap |
| Stuffing all chunks into prompt | Exceeds context window, adds noise | Top 3-5 most relevant only |
| No "I don't know" capability | LLM hallucinates from irrelevant chunks | Explicit instruction in system prompt |
| Same embedding model for all content | Different content types need different models | Benchmark on YOUR data |
| Not including source citations | Users can't verify answers | Include [Source: ...] in prompt template |
| Ignoring metadata filters | Returns docs from wrong department/date | Combine vector + metadata filtering |

---

# Best Practices

1. **Chunk wisely** — Sentence-based, 200-500 tokens, 10-20% overlap
2. **Include metadata** — source, date, author, topic for filtering
3. **Use hybrid search** — vector + keyword for best coverage
4. **Rerank** — retrieve 20, rerank to top 5 for quality
5. **Cite sources** — every claim should have a [Source] tag
6. **Handle "I don't know"** — explicit system prompt instruction
7. **Query reformulation** — for conversational RAG
8. **Evaluate systematically** — build a test dataset with expected answers
9. **Monitor retrieval quality** — log what was retrieved vs what was useful
10. **Refresh index regularly** — stale data = wrong answers

---

**Next Module:** [Module 4 — AI Agents →](../module-4-ai-agents/)

Say **NEXT** to continue.
