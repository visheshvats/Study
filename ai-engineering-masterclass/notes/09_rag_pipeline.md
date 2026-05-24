# Topic 9: Retrieval-Augmented Generation (RAG)

> **Java Analogy:** RAG is the `@Cacheable` + database lookup pattern for LLMs. Instead of relying on the model's memorized knowledge (which goes stale), you query an external knowledge base at runtime and inject the results into the prompt — like a service layer that enriches requests with live data before processing.

---

## What This Is (Plain English)

RAG = "Look it up before you answer." Before the LLM generates a response, the system searches a knowledge base for relevant documents, pastes the top results into the prompt, and asks the model to answer *based on the provided context*. This grounds the response in actual source material, dramatically reducing hallucination. It's how you give an LLM access to your company's internal docs, APIs, or databases without fine-tuning.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **RAG pipeline** | A service method: `queryDB(input) → enrichPrompt(results) → callLLM(enrichedPrompt)` |
| **Document chunking** | Splitting a file into `List<String>` segments — like `BufferedReader` reading in fixed-size blocks. |
| **Embedding** | `Function<String, float[]>` — convert text chunk to a searchable vector. |
| **Vector store** | A specialized `Map<float[], Document>` with nearest-neighbour lookup instead of exact-key lookup. |
| **Retrieval** | `vectorStore.findSimilar(queryVector, topK)` — like `repository.findByTitleContaining()` but semantic. |
| **Augmented prompt** | String concatenation: `systemPrompt + retrievedContext + userQuery` → LLM input. |
| **Citation** | Tracking which chunk contributed to which part of the answer — like source-line references in logs. |

---

## RAG Pipeline Architecture

```
User Query: "What's the refund policy for UPI failures?"
    │
    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Embed      │────▶│  Vector DB   │────▶│  Retrieve    │
│   Query      │     │  Search      │     │  Top-3 Docs  │
└──────────────┘     └──────────────┘     └──────────────┘
                                               │
                                               ▼
┌──────────────┐     ┌────────────────────────────────────┐
│   LLM        │◀────│  System: "Answer using the context" │
│   Generate   │     │  Context: [chunk1, chunk2, chunk3]  │
│   Response   │     │  User: "What's the refund policy?"  │
└──────────────┘     └────────────────────────────────────┘
    │
    ▼
"UPI failures auto-refund within 24-48 hours [Source: refund-policy.pdf, page 3]"
```

---

## Code Bridge — Full RAG Pipeline in Java

### Using Spring AI

```java
@Configuration
public class RagConfig {
    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel) {
        return new SimpleVectorStore(embeddingModel);
    }
}

@Service
public class RagService {
    private final VectorStore vectorStore;
    private final ChatClient chatClient;

    // Step 1: Index documents (one-time or scheduled)
    public void indexDocuments(List<Document> documents) {
        // Split into chunks
        var splitter = new TokenTextSplitter(500, 50);  // 500 tokens, 50 overlap
        List<Document> chunks = splitter.apply(documents);

        // Embed and store
        vectorStore.add(chunks);  // Embeds + stores automatically
    }

    // Step 2: Query with RAG
    public String query(String userQuestion) {
        // Retrieve relevant chunks
        List<Document> relevantDocs = vectorStore.similaritySearch(
            SearchRequest.query(userQuestion).withTopK(3)
        );

        // Build augmented prompt
        String context = relevantDocs.stream()
            .map(Document::getContent)
            .collect(Collectors.joining("\n---\n"));

        return chatClient.prompt()
            .system("""
                Answer the user's question using ONLY the provided context.
                If the context doesn't contain the answer, say "I don't have that information."
                Cite the source document for each claim.
                """)
            .user("""
                Context:
                %s

                Question: %s
                """.formatted(context, userQuestion))
            .call()
            .content();
    }
}
```

### Using LangChain4j (Full Pipeline)

```java
@Service
public class LangChain4jRagService {

    public static void main(String[] args) {
        // 1. Embedding model
        EmbeddingModel embeddingModel = OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("text-embedding-3-small")
            .build();

        // 2. Vector store (in-memory for demo; use Pinecone/Weaviate in production)
        EmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();

        // 3. Ingest documents
        Document doc = FileSystemDocumentLoader.loadDocument("refund-policy.pdf");
        DocumentSplitter splitter = DocumentSplitters.recursive(500, 50);
        List<TextSegment> segments = splitter.split(doc);

        List<Embedding> embeddings = embeddingModel.embedAll(
            segments.stream().map(TextSegment::text).toList()
        ).content();
        embeddingStore.addAll(embeddings, segments);

        // 4. Build RAG-enabled AI service
        ContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(3)
            .minScore(0.7)
            .build();

        ChatLanguageModel chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o")
            .build();

        // 5. Create AI service with RAG
        Assistant assistant = AiServices.builder(Assistant.class)
            .chatLanguageModel(chatModel)
            .contentRetriever(retriever)
            .build();

        String answer = assistant.chat("What is the UPI refund timeline?");
        System.out.println(answer);
    }

    interface Assistant {
        String chat(String message);
    }
}
```

---

## Chunking Strategies

| Strategy | Chunk Size | Overlap | Best For |
|---|---|---|---|
| Fixed-size | 500 tokens | 50 tokens | General documents |
| Paragraph-based | Variable | 1 sentence | Well-structured docs |
| Recursive (recommended) | 500 tokens | 10-20% | Mixed content |
| Semantic | Variable | 0 | Research papers with clear sections |

**Rule of thumb:** 256-512 tokens per chunk with 10-20% overlap. Too large = irrelevant noise in context. Too small = missing context.

---

## Production Concerns

1. **"Lost in the Middle":** LLMs ignore information in the middle of long prompts. Place the most relevant chunk FIRST, second-most-relevant LAST.

2. **Hybrid search:** Combine vector similarity (semantic) with BM25 keyword search. Vector search misses exact terms like error codes ("ERR-4001").

3. **Reranking:** After retrieving top-10 by vector search, use a cross-encoder reranker to re-score and select top-3. Improves precision significantly.

4. **Metadata filtering:** "Find docs about refunds WHERE department='payments' AND updated_after='2024-01-01'" — combine semantic search with SQL-like filters.

5. **Evaluation:** Measure retrieval quality separately from generation quality. If the wrong chunks are retrieved, the LLM can't save you.

---

## Interview-Ready Summary

- RAG retrieves relevant documents from a knowledge base and injects them into the LLM prompt.
- Three phases: Index (chunk → embed → store) → Retrieve (query → search → rank) → Generate (context + query → LLM).
- Eliminates hallucination by grounding responses in source documents.
- Use RAG for *knowledge* injection. Use fine-tuning for *behavioral* changes.
- In Java: Spring AI VectorStore or LangChain4j ContentRetriever.
- Chunking at 256-512 tokens with 10-20% overlap is the standard.
- Hybrid search (vector + keyword) outperforms pure vector search.
- Always put the most relevant chunk first in the prompt.
