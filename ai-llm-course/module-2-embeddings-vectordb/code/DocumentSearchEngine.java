
/**
 * MODULE 2 — PROJECT: Document Search Engine (Java Equivalent)
 * ==============================================================
 * Java equivalent of 05_document_search_engine.py
 *
 * A complete semantic search engine that:
 *   1. Indexes documents with embeddings
 *   2. Supports full CRUD operations
 *   3. Searches by semantic similarity
 *   4. Generates AI-powered answers from search results (RAG-lite)
 *
 * JAVA ANALOGY:
 *   Like a simplified Elasticsearch + Spring Boot:
 *   - DocumentRepository for CRUD
 *   - SearchService for similarity queries
 *   - AnswerService for AI-generated responses
 *
 * COMPILE & RUN:
 *   javac DocumentSearchEngine.java && java DocumentSearchEngine
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.stream.Collectors;

public class DocumentSearchEngine {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String EMBED_URL = "https://api.openai.com/v1/embeddings";
    private static final String CHAT_URL = "https://api.openai.com/v1/chat/completions";
    private static final String EMBED_MODEL = "text-embedding-3-small";
    private static final String CHAT_MODEL = "gpt-4o-mini";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String escapeJson(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static double[] getEmbedding(String text) throws Exception {
        String body = "{\"model\": \"%s\", \"input\": \"%s\"}".formatted(EMBED_MODEL, escapeJson(text));
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(EMBED_URL)).header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200)
            throw new RuntimeException("Embed error: " + response.body());
        String json = response.body();
        int s = json.indexOf("[", json.indexOf("\"embedding\":")), e = json.indexOf("]", s);
        String[] parts = json.substring(s + 1, e).split(",");
        double[] vec = new double[parts.length];
        for (int i = 0; i < parts.length; i++)
            vec[i] = Double.parseDouble(parts[i].trim());
        return vec;
    }

    static String chatLlm(String system, String user) throws Exception {
        String body = """
                {"model":"%s","messages":[{"role":"system","content":"%s"},{"role":"user","content":"%s"}],"temperature":0.5,"max_tokens":400}
                """
                .formatted(CHAT_MODEL, escapeJson(system), escapeJson(user));
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(CHAT_URL)).header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        HttpResponse<String> resp = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() != 200)
            throw new RuntimeException("Chat error: " + resp.body());
        String json = resp.body();
        String marker = "\"content\":";
        int idx = json.indexOf(marker) + marker.length();
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
        double dot = 0, nA = 0, nB = 0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            nA += a[i] * a[i];
            nB += b[i] * b[i];
        }
        return dot / (Math.sqrt(nA) * Math.sqrt(nB));
    }

    // ═══════════════════════════════════════════════════
    // DOCUMENT SEARCH ENGINE
    // ═══════════════════════════════════════════════════

    static class SearchEngine {
        record Document(String id, String title, String content, String category,
                double[] embedding) {
        }

        record SearchResult(Document doc, double score) {
        }

        private final Map<String, Document> documents = new LinkedHashMap<>();

        void addDocument(String id, String title, String content, String category) throws Exception {
            String fullText = title + ". " + content;
            double[] embedding = getEmbedding(fullText);
            documents.put(id, new Document(id, title, content, category, embedding));
        }

        List<SearchResult> search(String query, int topK, String categoryFilter) throws Exception {
            double[] queryEmb = getEmbedding(query);
            return documents.values().stream()
                    .filter(d -> categoryFilter == null || d.category.equals(categoryFilter))
                    .map(d -> new SearchResult(d, cosine(queryEmb, d.embedding)))
                    .sorted((a, b) -> Double.compare(b.score, a.score))
                    .limit(topK)
                    .collect(Collectors.toList());
        }

        String answerWithContext(String query, int topK) throws Exception {
            List<SearchResult> results = search(query, topK, null);
            if (results.isEmpty())
                return "No relevant documents found.";

            StringBuilder context = new StringBuilder();
            for (int i = 0; i < results.size(); i++) {
                var r = results.get(i);
                context.append(String.format("[%d] %s: %s\n", i + 1, r.doc.title, r.doc.content));
            }

            return chatLlm(
                    "Answer the question using ONLY the provided context. "
                            + "Cite sources as [1], [2], etc. If the context doesn't contain the answer, say so.",
                    "Context:\n" + context + "\nQuestion: " + query);
        }

        void deleteDocument(String id) {
            documents.remove(id);
        }

        int count() {
            return documents.size();
        }
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 2.5: Document Search Engine       ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY environment variable first!");
            return;
        }

        SearchEngine engine = new SearchEngine();

        // Index documents
        System.out.println("  📥 Indexing documents...\n");
        String[][] docs = {
                { "1", "Spring Boot Auto-Configuration",
                        "Spring Boot auto-configures beans based on classpath dependencies. Use @SpringBootApplication to enable.",
                        "framework" },
                { "2", "Java Virtual Threads",
                        "Java 21 virtual threads are lightweight threads managed by JVM. Use Thread.ofVirtual() to create. Great for I/O-bound tasks.",
                        "concurrency" },
                { "3", "Docker Containerization",
                        "Docker packages apps with dependencies. Use Dockerfile to define images. Containers are isolated and portable.",
                        "devops" },
                { "4", "JPA Entity Mapping",
                        "JPA @Entity maps Java classes to database tables. Use @Id for primary key, @Column for fields.",
                        "database" },
                { "5", "Kubernetes Deployments",
                        "K8s Deployments manage replica sets. Use kubectl apply -f deployment.yaml. Supports rolling updates.",
                        "devops" },
                { "6", "HashMap Internals",
                        "HashMap uses array of linked lists (buckets). Hash collision resolved by chaining. Load factor 0.75 triggers resize.",
                        "collections" },
                { "7", "Spring Security JWT",
                        "Spring Security with JWT: configure SecurityFilterChain, create JwtAuthFilter, validate tokens per request.",
                        "security" },
                { "8", "GC Algorithms",
                        "Java GC algorithms: G1 (default), ZGC (low latency), Shenandoah (concurrent). Choose based on latency requirements.",
                        "jvm" },
        };

        for (String[] d : docs) {
            engine.addDocument(d[0], d[1], d[2], d[3]);
            System.out.println("    ✅ " + d[1] + " [" + d[3] + "]");
        }
        System.out.println("\n  📊 Total documents: " + engine.count());

        // Search demos
        String[] queries = {
                "How do I create lightweight threads in Java?",
                "How do I deploy containers?",
                "What is the best garbage collector for low latency?",
        };

        for (String query : queries) {
            System.out.println("\n  ═══════════════════════════════════════");
            System.out.println("  🔍 Query: \"" + query + "\"\n");

            var results = engine.search(query, 3, null);
            System.out.println("  Top results:");
            for (var r : results) {
                System.out.printf("    [%.3f] %s — %s%n", r.score(), r.doc().title(),
                        r.doc().content().substring(0, Math.min(60, r.doc().content().length())) + "...");
            }

            System.out.println("\n  🤖 AI Answer:");
            String answer = engine.answerWithContext(query, 3);
            System.out.println("  " + answer);
        }

        System.out.println("\n\n  ✅ Document Search Engine Features:");
        System.out.println("     • Add/delete documents with auto-embedding");
        System.out.println("     • Semantic search with cosine similarity");
        System.out.println("     • Category-based filtering");
        System.out.println("     • RAG-style AI answers with source citations\n");
    }
}
