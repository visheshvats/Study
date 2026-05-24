# Topic 10: Vector Database

> **Java Analogy:** A vector database is like a `TreeMap` where the key is a `float[1536]` and `get()` returns the nearest neighbors by geometric distance instead of exact key match. Think `ConcurrentNavigableMap<Embedding, Document>` with fuzzy semantic lookup.

---

## What This Is (Plain English)

A vector database stores embedding vectors and supports fast "find me the most similar vectors" queries. When a user searches "payment failed," the system doesn't look for those exact words — it finds documents whose embedding vectors are geometrically close to the query vector in 1536-dimensional space. This is how "my card got declined" matches "payment processing error" — they're neighbors in vector space.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Vector index** | Like a spatial `R-Tree` or `KD-Tree` but for 1536 dimensions. |
| **ANN (Approximate Nearest Neighbor)** | Like `HashMap.get()` that returns "close enough" matches in O(log n) instead of exact matches in O(n). |
| **HNSW graph** | A skip-list-like multi-layer graph. Top layers = long-range jumps, bottom layer = precise local search. |
| **Metadata filtering** | `WHERE department = 'payments'` — SQL-style filters applied alongside vector search. |
| **Collection/Index** | Like a database table — one per document type or use case. |
| **Distance metric** | `Comparator<float[]>` — cosine similarity, Euclidean distance, or dot product. |

---

## Vector DB Options for Java Engineers

| Database | Type | Java SDK | Best For |
|---|---|---|---|
| **Pinecone** | Managed cloud | REST API / Java client | Production SaaS, zero-ops |
| **Weaviate** | Open-source | Official Java client | Self-hosted, hybrid search |
| **Milvus** | Open-source | Official Java SDK | High-scale, enterprise |
| **Qdrant** | Open-source | REST + gRPC | Performance-focused |
| **Chroma** | Open-source | REST API | Prototyping, lightweight |
| **pgvector** | PostgreSQL extension | JDBC + pgvector | If you're already on PostgreSQL |
| **Redis Stack** | In-memory | Jedis / Lettuce | Low-latency, existing Redis infra |
| **Spring AI VectorStore** | Abstraction | Built-in | Framework-native, provider-agnostic |

---

## Code Bridge

### Spring AI with pgvector (PostgreSQL)

```java
// application.yml
// spring:
//   ai:
//     vectorstore:
//       pgvector:
//         dimensions: 1536
//         index-type: HNSW
//         distance-type: COSINE_DISTANCE

@Service
public class DocumentIndexService {
    private final VectorStore vectorStore;

    // Store documents
    public void index(String content, Map<String, Object> metadata) {
        Document doc = new Document(content, metadata);
        vectorStore.add(List.of(doc));
    }

    // Search by semantic similarity
    public List<Document> search(String query, int topK) {
        return vectorStore.similaritySearch(
            SearchRequest.query(query)
                .withTopK(topK)
                .withSimilarityThreshold(0.7)  // Minimum relevance
                .withFilterExpression("department == 'engineering'")  // Metadata filter
        );
    }
}
```

### Direct Weaviate Client

```java
// Maven: io.weaviate:client:4.x.x
WeaviateClient client = new WeaviateClient(
    new Config("http", "localhost:8080")
);

// Create schema (like a CREATE TABLE)
client.schema().classCreator()
    .withClass(WeaviateClass.builder()
        .className("SupportTicket")
        .vectorizer("text2vec-openai")
        .properties(List.of(
            Property.builder().name("content").dataType(List.of("text")).build(),
            Property.builder().name("department").dataType(List.of("text")).build(),
            Property.builder().name("createdAt").dataType(List.of("date")).build()
        ))
        .build())
    .run();

// Insert document
client.data().creator()
    .withClassName("SupportTicket")
    .withProperties(Map.of(
        "content", "My UPI transaction failed but money was debited",
        "department", "payments",
        "createdAt", Instant.now().toString()
    ))
    .run();

// Semantic search with filter
Result<GraphQLResponse> result = client.graphQL().get()
    .withClassName("SupportTicket")
    .withFields(Field.builder().name("content").build())
    .withNearText(NearTextArgument.builder()
        .concepts(new String[]{"payment failure refund"})
        .build())
    .withWhere(WhereArgument.builder()
        .path("department")
        .operator(Operator.Equal)
        .valueText("payments")
        .build())
    .withLimit(5)
    .run();
```

### pgvector with Raw JDBC

```java
// If you prefer staying close to SQL
@Repository
public class VectorRepository {

    @Autowired
    private JdbcTemplate jdbc;

    public void insert(String content, float[] embedding) {
        jdbc.update("""
            INSERT INTO documents (content, embedding)
            VALUES (?, ?::vector)
            """, content, toVectorString(embedding));
    }

    public List<Document> findSimilar(float[] queryEmbedding, int limit) {
        return jdbc.query("""
            SELECT content, 1 - (embedding <=> ?::vector) as similarity
            FROM documents
            ORDER BY embedding <=> ?::vector
            LIMIT ?
            """,
            (rs, i) -> new Document(rs.getString("content"), rs.getDouble("similarity")),
            toVectorString(queryEmbedding),
            toVectorString(queryEmbedding),
            limit
        );
    }

    private String toVectorString(float[] v) {
        return "[" + Arrays.stream(v)
            .mapToObj(Float::toString)
            .collect(Collectors.joining(",")) + "]";
    }
}
```

---

## HNSW — How It Works (Simplified)

```
Layer 3 (top):    [A] ──────────────── [M]          (few nodes, long jumps)
Layer 2:          [A] ── [D] ──── [M] ── [P]       (more nodes)
Layer 1:          [A]-[B]-[D]-[G]-[M]-[N]-[P]-[R]  (even more)
Layer 0 (bottom): [A][B][C][D][E][F][G]...[R][S][T]  (ALL nodes)

Search for query Q:
1. Start at top layer → greedily walk to nearest node → A→M
2. Drop to layer 2, start from M → walk to nearest → M→P
3. Drop to layer 1, start from P → walk → P→N
4. Drop to layer 0, start from N → beam search → find exact top-K
```

**Result:** O(log n) search instead of O(n) brute force. For 1 million vectors, ~20 comparisons instead of 1,000,000.

---

## Production Patterns

1. **pgvector for startups:** If you're already on PostgreSQL, just add the pgvector extension. No new infrastructure.

2. **Dedicated vector DB for scale:** Beyond 1M vectors or when you need sub-10ms latency, use Pinecone/Milvus/Qdrant.

3. **Always track embedding model version.** Switching models = re-embed everything.

4. **Pre-filter vs post-filter:** Pre-filter (metadata first, then vector search) is faster but can miss relevant results. Post-filter (vector search first, then metadata) is safer.

---

## Interview-Ready Summary

- A vector database stores embedding vectors and supports approximate nearest-neighbor (ANN) search.
- HNSW is the dominant algorithm: multi-layer graph with O(log n) search.
- Java options: pgvector (PostgreSQL), Weaviate, Milvus, Pinecone, or Spring AI VectorStore abstraction.
- Use cosine similarity for direction-based comparison (standard for text).
- Combine vector search with metadata filtering for production queries.
- Start with pgvector if you're on PostgreSQL; scale to dedicated vector DBs when needed.
