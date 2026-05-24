# Topic 3: Vectors (Embeddings)

> **Java Analogy:** An embedding vector is like a `float[]` feature array where each dimension encodes a semantic property. Think of it as a multi-dimensional `hashCode()` — but instead of collapsing to a single int, it expands to 1536 floats that preserve semantic relationships.

---

## What This Is (Plain English)

A vector embedding is a list of numbers (e.g., 1536 floats) that represents the *meaning* of a piece of text. Similar meanings produce similar numbers. "How do I reset my password?" and "I forgot my login credentials" will have vectors that are numerically close, even though they share zero words. This is the foundation of semantic search — finding things by meaning, not keywords.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Embedding vector** | `float[1536]` — a fixed-length numeric representation of text |
| **Embedding model** | A `Function<String, float[]>` — text in, vector out |
| **Cosine similarity** | A distance function between two `float[]` arrays. Returns 0 to 1 (1 = identical meaning). |
| **Vector space** | Like a coordinate system. Each text gets an "address" in 1536-dimensional space. |
| **Embedding matrix** | A giant `float[vocabularySize][embeddingDim]` lookup table |

---

## Why This Matters to You

As a Java backend engineer, embeddings are your entry point to:

1. **Semantic search:** "Find similar support tickets" without keyword matching
2. **RAG pipelines:** Converting documents to vectors for retrieval (Topic 9)
3. **Classification:** Clustering customer feedback by meaning
4. **Deduplication:** Finding near-duplicate content across databases
5. **Recommendation:** "Users who searched for X also need Y"

---

## Java Ecosystem & Libraries

| Library | Purpose |
|---|---|
| **Spring AI EmbeddingClient** | Call OpenAI/Ollama/HuggingFace embedding APIs with Spring auto-config. |
| **LangChain4j EmbeddingModel** | Unified interface for embedding providers. Supports 10+ providers. |
| **DJL (Deep Java Library)** | Run embedding models *locally* in Java. No API call needed. |
| **Apache Commons Math** | `RealVector` and `CosineSimilarity` for vector operations. |
| **ONNX Runtime Java** | Load ONNX embedding models and run inference in-process. |

---

## Code Bridge

### Generating Embeddings with Spring AI

```java
@Service
public class EmbeddingService {
    private final EmbeddingModel embeddingModel;

    public EmbeddingService(EmbeddingModel embeddingModel) {
        this.embeddingModel = embeddingModel;
    }

    public float[] embed(String text) {
        EmbeddingResponse response = embeddingModel.call(
            new EmbeddingRequest(List.of(text), EmbeddingOptions.EMPTY)
        );
        return response.getResult().getOutput();
    }

    public List<float[]> embedBatch(List<String> texts) {
        EmbeddingResponse response = embeddingModel.call(
            new EmbeddingRequest(texts, EmbeddingOptions.EMPTY)
        );
        return response.getResults().stream()
            .map(r -> r.getOutput())
            .toList();
    }
}
```

### Cosine Similarity — Pure Java

```java
public class VectorMath {

    /**
     * Cosine similarity: measures directional alignment between two vectors.
     * Returns value in [-1, 1]. Higher = more similar.
     * 
     * Formula: cos(a,b) = (a · b) / (||a|| × ||b||)
     */
    public static double cosineSimilarity(float[] a, float[] b) {
        if (a.length != b.length) throw new IllegalArgumentException("Dimension mismatch");
        
        double dotProduct = 0.0;
        double normA = 0.0;
        double normB = 0.0;

        for (int i = 0; i < a.length; i++) {
            dotProduct += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }

        double denominator = Math.sqrt(normA) * Math.sqrt(normB);
        return denominator == 0 ? 0 : dotProduct / denominator;
    }

    /**
     * Euclidean distance: straight-line distance in vector space.
     * Lower = more similar.
     */
    public static double euclideanDistance(float[] a, float[] b) {
        double sum = 0.0;
        for (int i = 0; i < a.length; i++) {
            double diff = a[i] - b[i];
            sum += diff * diff;
        }
        return Math.sqrt(sum);
    }

    /**
     * L2 normalize: scales vector to unit length.
     * Required before storing in vector DBs that use dot-product internally.
     */
    public static float[] normalize(float[] v) {
        double norm = 0.0;
        for (float x : v) norm += x * x;
        norm = Math.sqrt(norm);
        
        float[] result = new float[v.length];
        for (int i = 0; i < v.length; i++) {
            result[i] = (float) (v[i] / norm);
        }
        return result;
    }
}
```

### Semantic Search — Finding Similar Documents

```java
@Service
public class SemanticSearchService {
    private final EmbeddingService embeddingService;
    private final List<Document> documents; // Pre-embedded

    public List<Document> findSimilar(String query, int topK) {
        float[] queryVector = embeddingService.embed(query);

        return documents.stream()
            .map(doc -> new ScoredDocument(doc, 
                VectorMath.cosineSimilarity(queryVector, doc.getEmbedding())))
            .sorted(Comparator.comparingDouble(ScoredDocument::score).reversed())
            .limit(topK)
            .map(ScoredDocument::document)
            .toList();
    }

    record ScoredDocument(Document document, double score) {}
}
```

---

## Critical Concepts

### Why Cosine over Euclidean?

- **Cosine similarity** measures *direction* (are these vectors pointing the same way?). Ignores magnitude.
- **Euclidean distance** measures *absolute position* (how far apart are they?). Sensitive to magnitude.
- In practice, cosine similarity is preferred because embedding vectors can vary in magnitude without changing meaning. A longer document doesn't mean a "bigger" meaning.

### Vector Dimensions

| Embedding Model | Dimensions | Speed | Quality |
|---|---|---|---|
| `text-embedding-3-small` | 1536 | Fast | Good |
| `text-embedding-3-large` | 3072 | Slower | Better |
| `nomic-embed-text` (local) | 768 | Very Fast | Good |
| `all-MiniLM-L6-v2` (local) | 384 | Fastest | Adequate |

More dimensions = more nuance captured, but also more storage and slower search. 1536 is the sweet spot for most production use cases.

---

## Production Patterns

1. **Always normalize before storing.** Some vector DBs use dot-product internally. Without normalization, rankings will be wrong.

2. **Batch embed, don't loop.** Embedding 1000 documents one-by-one = 1000 API calls. Batching = ~10 calls. Always use batch APIs.

3. **Cache embeddings.** The embedding of "What is Spring Boot?" is always the same vector. Store it alongside the text in your DB.

4. **Track model version.** If you switch from `ada-002` to `text-embedding-3-small`, ALL existing vectors are invalid. You must re-embed your entire corpus.

---

## Interview-Ready Summary

- Vector embeddings convert text to fixed-length `float[]` arrays that encode semantic meaning.
- Similar meanings → similar vectors (high cosine similarity).
- Cosine similarity ranges from -1 to 1 (1 = identical direction, 0 = unrelated).
- Use `Spring AI EmbeddingClient` or `LangChain4j` in Java to generate embeddings.
- Always L2-normalize vectors before storing in a vector database.
- Changing the embedding model requires re-embedding your entire dataset.
- The famous analogy: `king - man + woman ≈ queen` — vector arithmetic encodes relationships.
