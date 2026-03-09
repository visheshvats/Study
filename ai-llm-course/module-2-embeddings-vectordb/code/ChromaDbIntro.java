
/**
 * MODULE 2 — Example 3: In-Memory Vector Store (Java Equivalent)
 * ================================================================
 * Java equivalent of 03_chromadb_intro.py
 *
 * Since ChromaDB doesn't have a Java SDK, we BUILD our own
 * in-memory vector store that demonstrates the same concepts:
 *   - Collections (like database tables)
 *   - Add documents with metadata
 *   - Query by similarity
 *   - Filter by metadata
 *   - Update and delete
 *
 * JAVA ANALOGY:
 *   ChromaDB collection = a Map<String, Document> + spatial index
 *   Like a simplified in-memory Elasticsearch
 *
 * COMPILE & RUN:
 *   javac ChromaDbIntro.java && java ChromaDbIntro
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.stream.Collectors;

public class ChromaDbIntro {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String EMBED_URL = "https://api.openai.com/v1/embeddings";
    private static final String EMBED_MODEL = "text-embedding-3-small";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String escapeJson(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static double[] getEmbedding(String text) throws Exception {
        String body = """
                {"model": "%s", "input": "%s"}
                """.formatted(EMBED_MODEL, escapeJson(text));

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(EMBED_URL))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200)
            throw new RuntimeException("API error: " + response.body());

        String json = response.body();
        int start = json.indexOf("[", json.indexOf("\"embedding\":"));
        int end = json.indexOf("]", start);
        String[] parts = json.substring(start + 1, end).split(",");
        double[] vec = new double[parts.length];
        for (int i = 0; i < parts.length; i++)
            vec[i] = Double.parseDouble(parts[i].trim());
        return vec;
    }

    static double cosineSimilarity(double[] a, double[] b) {
        double dot = 0, nA = 0, nB = 0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            nA += a[i] * a[i];
            nB += b[i] * b[i];
        }
        return dot / (Math.sqrt(nA) * Math.sqrt(nB));
    }

    // ═══════════════════════════════════════════════════
    // IN-MEMORY VECTOR COLLECTION
    // (Simulates ChromaDB operations)
    // ═══════════════════════════════════════════════════

    static class VectorCollection {
        record Document(String id, String text, double[] embedding, Map<String, String> metadata) {
        }

        record QueryResult(String id, String text, double score, Map<String, String> metadata) {
        }

        private final String name;
        private final Map<String, Document> documents = new LinkedHashMap<>();

        VectorCollection(String name) {
            this.name = name;
        }

        /** Add a document with its embedding and metadata. */
        void add(String id, String text, double[] embedding, Map<String, String> metadata) {
            documents.put(id, new Document(id, text, embedding, metadata));
        }

        /** Query: find the top-k most similar documents. */
        List<QueryResult> query(double[] queryEmbedding, int topK, Map<String, String> metadataFilter) {
            return documents.values().stream()
                    .filter(doc -> matchesFilter(doc, metadataFilter))
                    .map(doc -> new QueryResult(doc.id, doc.text,
                            cosineSimilarity(queryEmbedding, doc.embedding), doc.metadata))
                    .sorted((a, b) -> Double.compare(b.score(), a.score()))
                    .limit(topK)
                    .collect(Collectors.toList());
        }

        private boolean matchesFilter(Document doc, Map<String, String> filter) {
            if (filter == null || filter.isEmpty())
                return true;
            for (var entry : filter.entrySet()) {
                String docVal = doc.metadata.get(entry.getKey());
                if (docVal == null || !docVal.equals(entry.getValue()))
                    return false;
            }
            return true;
        }

        /** Update a document's text and re-embed. */
        void update(String id, String newText, double[] newEmbedding) {
            Document old = documents.get(id);
            if (old != null) {
                documents.put(id, new Document(id, newText, newEmbedding, old.metadata));
            }
        }

        /** Delete a document by ID. */
        void delete(String id) {
            documents.remove(id);
        }

        int count() {
            return documents.size();
        }

        String getName() {
            return name;
        }
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 2.3: Vector Store (Java)          ║");
        System.out.println("║  In-memory ChromaDB equivalent              ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY environment variable first!");
            return;
        }

        // ── Create collection ──
        VectorCollection collection = new VectorCollection("java_knowledge");
        System.out.println("  Created collection: " + collection.getName());

        // ── Add documents ──
        System.out.println("\n  📥 Adding documents...\n");

        String[][] docs = {
                { "doc1", "Spring Boot auto-configures beans based on classpath dependencies", "framework",
                        "beginner" },
                { "doc2", "HashMap uses hash tables for O(1) average-case lookups", "collections", "intermediate" },
                { "doc3", "CompletableFuture enables non-blocking async programming in Java", "concurrency",
                        "advanced" },
                { "doc4", "JPA @Entity maps a Java class to a database table", "database", "beginner" },
                { "doc5", "Docker containers run applications in isolated environments", "devops", "intermediate" },
                { "doc6", "Virtual threads in Java 21 are lightweight threads managed by the JVM", "concurrency",
                        "advanced" },
                { "doc7", "Spring Security uses filter chains for authentication and authorization", "security",
                        "intermediate" },
                { "doc8", "Garbage collection automatically frees unused objects from heap memory", "jvm", "beginner" },
        };

        for (String[] doc : docs) {
            double[] emb = getEmbedding(doc[1]);
            Map<String, String> meta = Map.of("category", doc[2], "level", doc[3]);
            collection.add(doc[0], doc[1], emb, meta);
            System.out.println("    ✅ Added: " + doc[0] + " [" + doc[2] + "/" + doc[3] + "]");
        }

        System.out.println("\n  📊 Collection size: " + collection.count());

        // ── Query: no filter ──
        System.out.println("\n  ═══════════════════════════════════════");
        System.out.println("  🔍 Query 1: \"How does async work in Java?\"");
        double[] q1 = getEmbedding("How does async work in Java?");
        var results1 = collection.query(q1, 3, null);
        for (var r : results1) {
            System.out.printf("    [%.3f] %s — %s%n", r.score(), r.id(), r.text());
        }

        // ── Query: with metadata filter ──
        System.out.println("\n  🔍 Query 2: \"Getting started\" (level=beginner only)");
        double[] q2 = getEmbedding("Getting started with Java frameworks");
        var results2 = collection.query(q2, 3, Map.of("level", "beginner"));
        for (var r : results2) {
            System.out.printf("    [%.3f] %s — %s [%s]%n", r.score(), r.id(), r.text(), r.metadata());
        }

        // ── Update ──
        System.out.println("\n  ✏️ Updating doc1...");
        String newText = "Spring Boot 3.x auto-configures beans and supports GraalVM native compilation";
        collection.update("doc1", newText, getEmbedding(newText));
        System.out.println("    Updated text: " + newText);

        // ── Delete ──
        System.out.println("\n  🗑️ Deleting doc5 (Docker)...");
        collection.delete("doc5");
        System.out.println("    Collection size: " + collection.count());

        // ── Final query ──
        System.out.println("\n  🔍 Query 3: \"container deployment\" (after deleting Docker doc)");
        double[] q3 = getEmbedding("container deployment");
        var results3 = collection.query(q3, 3, null);
        for (var r : results3) {
            System.out.printf("    [%.3f] %s — %s%n", r.score(), r.id(), r.text());
        }

        System.out.println("\n  ✅ ChromaDB Operations Covered:");
        System.out.println("     • Create collection ← new VectorCollection()");
        System.out.println("     • Add documents    ← collection.add()");
        System.out.println("     • Query by vector  ← collection.query()");
        System.out.println("     • Metadata filter  ← collection.query(..., filter)");
        System.out.println("     • Update           ← collection.update()");
        System.out.println("     • Delete           ← collection.delete()\n");
    }
}
