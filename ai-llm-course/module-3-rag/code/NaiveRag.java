
/**
 * MODULE 3 — Example 1: Naive RAG (Java Equivalent)
 * =====================================================
 * Java equivalent of 01_naive_rag.py
 *
 * RAG = Retrieval-Augmented Generation:
 *   1. INDEX: Embed documents and store them
 *   2. RETRIEVE: Find relevant docs for a query
 *   3. GENERATE: Use LLM with retrieved context to answer
 *
 * JAVA ANALOGY:
 *   Like a Spring @Service that:
 *   1. Loads data from a Repository
 *   2. Finds relevant records
 *   3. Sends them to an AI service for processing
 *
 * COMPILE & RUN:
 *   javac NaiveRag.java && java NaiveRag
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.stream.Collectors;

public class NaiveRag {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String EMBED_URL = "https://api.openai.com/v1/embeddings";
    private static final String CHAT_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static double[] embed(String text) throws Exception {
        var body = "{\"model\":\"text-embedding-3-small\",\"input\":\"%s\"}".formatted(esc(text));
        var req = HttpRequest.newBuilder().uri(URI.create(EMBED_URL))
                .header("Content-Type", "application/json").header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        var resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() != 200)
            throw new RuntimeException("Embed error: " + resp.body());
        String json = resp.body();
        int s = json.indexOf("[", json.indexOf("\"embedding\":")), e = json.indexOf("]", s);
        String[] parts = json.substring(s + 1, e).split(",");
        double[] vec = new double[parts.length];
        for (int i = 0; i < parts.length; i++)
            vec[i] = Double.parseDouble(parts[i].trim());
        return vec;
    }

    static String chat(String system, String user) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":0.3,\"max_tokens\":500}"
                .formatted(esc(system), esc(user));
        var req = HttpRequest.newBuilder().uri(URI.create(CHAT_URL))
                .header("Content-Type", "application/json").header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        var resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() != 200)
            throw new RuntimeException("Chat error: " + resp.body());
        String json = resp.body();
        String m = "\"content\":";
        int idx = json.indexOf(m) + m.length();
        while (json.charAt(idx) == ' ' || json.charAt(idx) == '\n')
            idx++;
        idx++;
        StringBuilder sb = new StringBuilder();
        while (idx < json.length()) {
            char c = json.charAt(idx);
            if (c == '\\' && idx + 1 < json.length()) {
                char n = json.charAt(idx + 1);
                switch (n) {
                    case '"':
                        sb.append('"');
                        idx += 2;
                        continue;
                    case 'n':
                        sb.append('\n');
                        idx += 2;
                        continue;
                    case '\\':
                        sb.append('\\');
                        idx += 2;
                        continue;
                    default:
                        sb.append(c);
                        idx++;
                        continue;
                }
            }
            if (c == '"')
                break;
            sb.append(c);
            idx++;
        }
        return sb.toString();
    }

    static double cosine(double[] a, double[] b) {
        double d = 0, nA = 0, nB = 0;
        for (int i = 0; i < a.length; i++) {
            d += a[i] * b[i];
            nA += a[i] * a[i];
            nB += b[i] * b[i];
        }
        return d / (Math.sqrt(nA) * Math.sqrt(nB));
    }

    // ═══════════════════════════════════════════════════
    // RAG PIPELINE
    // ═══════════════════════════════════════════════════

    record DocChunk(String id, String text, String source, double[] embedding) {
    }

    record SearchResult(DocChunk doc, double score) {
    }

    static List<DocChunk> knowledgeBase = new ArrayList<>();

    /** STEP 1: Index documents (split into chunks and embed). */
    static void indexDocuments(String[][] documents) throws Exception {
        System.out.println("  📥 Indexing documents...");
        for (String[] doc : documents) {
            String id = doc[0], text = doc[1], source = doc[2];
            double[] emb = embed(text);
            knowledgeBase.add(new DocChunk(id, text, source, emb));
        }
        System.out.println("  ✅ Indexed " + knowledgeBase.size() + " chunks\n");
    }

    /** STEP 2: Retrieve relevant chunks for a query. */
    static List<SearchResult> retrieve(String query, int topK) throws Exception {
        double[] queryEmb = embed(query);
        return knowledgeBase.stream()
                .map(doc -> new SearchResult(doc, cosine(queryEmb, doc.embedding)))
                .sorted((a, b) -> Double.compare(b.score, a.score))
                .limit(topK)
                .collect(Collectors.toList());
    }

    /** STEP 3: Generate answer using retrieved context. */
    static String generate(String query, List<SearchResult> context) throws Exception {
        StringBuilder ctx = new StringBuilder();
        for (int i = 0; i < context.size(); i++) {
            var r = context.get(i);
            ctx.append("[").append(i + 1).append("] (").append(r.doc.source).append("): ").append(r.doc.text)
                    .append("\n");
        }

        return chat(
                "Answer the question using ONLY the provided context. "
                        + "Cite your sources as [1], [2], etc. "
                        + "If the context doesn't contain the answer, say 'I don't have enough information.'",
                "Context:\n" + ctx + "\nQuestion: " + query);
    }

    /** Full RAG pipeline: Retrieve → Augment → Generate. */
    static String rag(String query, int topK) throws Exception {
        System.out.println("  🔍 Retrieving relevant context...");
        List<SearchResult> context = retrieve(query, topK);
        for (var r : context) {
            System.out.printf("    [%.3f] %s — %s%n", r.score, r.doc.source,
                    r.doc.text.substring(0, Math.min(60, r.doc.text.length())) + "...");
        }
        System.out.println("  🤖 Generating answer...");
        return generate(query, context);
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 3.1: Naive RAG Pipeline (Java)    ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        // Knowledge base about Java/Spring
        String[][] docs = {
                { "1", "Spring Boot uses embedded Tomcat by default. Configure server.port in application.properties to change the port. Supports Jetty and Undertow as alternatives.",
                        "spring-boot-docs" },
                { "2", "Java 21 introduced virtual threads via Project Loom. Create with Thread.ofVirtual().start(). They are managed by the JVM, not OS. Ideal for I/O-bound workloads with thousands of concurrent connections.",
                        "java-21-release-notes" },
                { "3", "Spring Data JPA provides repository abstractions. Extend JpaRepository<Entity,ID> for CRUD operations. Use @Query for custom JPQL. Supports pagination with Pageable parameter.",
                        "spring-data-docs" },
                { "4", "G1GC is the default garbage collector since Java 9. It divides heap into regions. ZGC offers sub-millisecond pause times for latency-sensitive applications. Shenandoah provides concurrent compaction.",
                        "jvm-tuning-guide" },
                { "5", "Spring Security 6 uses SecurityFilterChain bean configuration. JWT authentication requires a custom filter extending OncePerRequestFilter. Use @PreAuthorize for method-level security.",
                        "spring-security-docs" },
                { "6", "Records in Java 16+ are immutable data carriers. They auto-generate equals(), hashCode(), toString(). Use for DTOs, configuration, and value objects. Cannot extend other classes.",
                        "java-features-guide" },
        };

        indexDocuments(docs);

        String[] queries = {
                "How do I change the server port in Spring Boot?",
                "What are virtual threads and when should I use them?",
                "Which garbage collector has the lowest latency?",
        };

        for (String query : queries) {
            System.out.println("  ═══════════════════════════════════════");
            System.out.println("  👤 " + query + "\n");
            String answer = rag(query, 3);
            System.out.println("\n  🤖 Answer: " + answer + "\n");
        }

        System.out.println("  ✅ Naive RAG Pattern:");
        System.out.println("     1. INDEX: Embed documents → vector store");
        System.out.println("     2. RETRIEVE: Query → find similar chunks");
        System.out.println("     3. GENERATE: Context + question → LLM answer\n");
    }
}
