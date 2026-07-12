# Phase 02: RAG Core — Diagrams

## 1. RAG Architecture (Ingestion vs Retrieval)
This is the standard architectural diagram for a Retrieval-Augmented Generation system. It highlights the one-time indexing pipeline (ETL) and the real-time query pipeline.

```mermaid
flowchart LR
    subgraph INGEST["🏗️ Indexing (One-time)"]
        D["📄 Documents\nPDF / CSV / Web"] --> L["Loaders"]
        L --> S["Text Splitter\nchunks + overlap"]
        S --> E["Embeddings Model\ntext → vector"]
        E --> V[("🗄️ Vector DB\nChroma / FAISS")]
    end

    subgraph QUERY["🔍 Retrieval + Generation (Per Query)"]
        Q["User Query"] --> QE["Embed Query\nsame model"]
        QE --> R["Top-K Retrieval\nCosine Similarity"]
        V --> R
        R --> CTX["Context + Query\n→ Prompt"]
        CTX --> LLM["☁️ LLM"]
        LLM --> ANS["✅ Answer"]
    end

    style V fill:#6C63FF,color:#fff
    style LLM fill:#FF6B6B,color:#fff
```

## 2. Text Splitting and Chunk Overlap
*New diagram added to visualize why chunk overlap prevents data loss across boundaries.*

When splitting text, cutting rigidly at 1000 characters might slice a sentence in half, separating a subject from its predicate. Overlap duplicates characters across chunks to preserve context.

```mermaid
block-beta
  columns 1
  Doc["Original Document: 'The system will undergo maintenance on Friday at 2AM. Please save all your work.'"]
  
  block:Chunks
    columns 2
    C1["Chunk 1: 'The system will undergo maintenance on Friday at 2AM.'"]
    C2["Chunk 2: '...maintenance on Friday at 2AM. Please save all your work.'"]
  end
  
  Doc --> Chunks
  style Doc fill:#4CAF50,color:#fff
  style C1 fill:#FFC107,color:#000
  style C2 fill:#2196F3,color:#fff
```

### Why this matters for AI Engineering
If a user queries "When is the maintenance?", and the text was split exactly between "maintenance on" and "Friday at 2AM" without overlap, the embeddings for both chunks might score poorly for relevance because the sentence's meaning was destroyed. Overlap (shown in the duplicated phrase "...maintenance on Friday at 2AM.") guarantees that the semantic connection survives in at least one chunk.
