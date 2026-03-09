
/**
 * MODULE 2 — Example 1: Embeddings Basics (Java Equivalent)
 * ============================================================
 * Java equivalent of 01_embeddings_basics.py
 *
 * Demonstrates:
 *   1. What embeddings are (text → number vectors)
 *   2. Calling OpenAI Embeddings API
 *   3. Cosine similarity for comparing text meaning
 *   4. Basic semantic search
 *
 * JAVA ANALOGY:
 *   - Embedding = a hashCode() but for MEANING, not equality
 *   - Cosine similarity = Comparable.compareTo() but for semantic distance
 *   - Vector = double[] feature array (like ML feature engineering)
 *
 * COMPILE & RUN:
 *   javac EmbeddingsBasics.java && java EmbeddingsBasics
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;

public class EmbeddingsBasics {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/embeddings";
    private static final String EMBED_MODEL = "text-embedding-3-small";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String escapeJson(String s) {
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n");
    }

    // ═══════════════════════════════════════════════════
    // EMBEDDING API CALL
    // ═══════════════════════════════════════════════════

    static double[] getEmbedding(String text) throws Exception {
        String body = """
                {
                    "model": "%s",
                    "input": "%s"
                }
                """.formatted(EMBED_MODEL, escapeJson(text));

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_URL))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

        HttpResponse<String> response = httpClient.send(request,
                HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new RuntimeException("API error: " + response.body());
        }

        return parseEmbedding(response.body());
    }

    /** Parse the embedding array from OpenAI response JSON. */
    static double[] parseEmbedding(String json) {
        String marker = "\"embedding\":";
        int start = json.indexOf(marker);
        if (start == -1)
            return new double[0];
        start = json.indexOf('[', start);
        int end = json.indexOf(']', start);
        String arrayStr = json.substring(start + 1, end);
        String[] parts = arrayStr.split(",");
        double[] vec = new double[parts.length];
        for (int i = 0; i < parts.length; i++) {
            vec[i] = Double.parseDouble(parts[i].trim());
        }
        return vec;
    }

    // ═══════════════════════════════════════════════════
    // SIMILARITY METRICS
    // ═══════════════════════════════════════════════════

    static double cosineSimilarity(double[] a, double[] b) {
        double dot = 0, normA = 0, normB = 0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        return dot / (Math.sqrt(normA) * Math.sqrt(normB));
    }

    // ═══════════════════════════════════════════════════
    // PART 1: What embeddings look like
    // ═══════════════════════════════════════════════════

    static void demo1_WhatAreEmbeddings() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("PART 1: What Do Embeddings Look Like?");
        System.out.println("═══════════════════════════════════════════\n");

        String text = "Spring Boot makes Java development faster";
        double[] embedding = getEmbedding(text);

        System.out.println("  Text: \"" + text + "\"");
        System.out.println("  Dimensions: " + embedding.length);
        System.out.print("  First 10 values: [");
        for (int i = 0; i < 10; i++) {
            System.out.printf("%.6f%s", embedding[i], i < 9 ? ", " : "");
        }
        System.out.println(", ...]");
        System.out.println("\n  💡 Each text becomes a " + embedding.length + "-dimensional vector");
        System.out.println("     Similar meanings → vectors point in similar directions\n");
    }

    // ═══════════════════════════════════════════════════
    // PART 2: Similarity comparison
    // ═══════════════════════════════════════════════════

    static void demo2_SimilarityComparison() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("PART 2: Comparing Text Similarity");
        System.out.println("═══════════════════════════════════════════\n");

        String[][] pairs = {
                { "Java is a programming language", "Java is used for software development" }, // Similar
                { "Java is a programming language", "Python is a programming language" }, // Same domain
                { "Java is a programming language", "The weather is sunny today" }, // Unrelated
                { "Spring Boot application", "SpringBoot microservice project" }, // Near identical
                { "ArrayList vs LinkedList", "When to use array-based vs node-based collections" }, // Semantic
        };

        System.out.println("  Comparing text pairs (cosine similarity):");
        System.out.println("  ──────────────────────────────────────────────\n");

        for (String[] pair : pairs) {
            double[] emb1 = getEmbedding(pair[0]);
            double[] emb2 = getEmbedding(pair[1]);
            double sim = cosineSimilarity(emb1, emb2);

            String label = sim > 0.85 ? "🟢 Very similar"
                    : sim > 0.70 ? "🟡 Related" : sim > 0.50 ? "🟠 Somewhat" : "🔴 Different";

            System.out.printf("  %s %.3f%n", label, sim);
            System.out.println("    A: \"" + pair[0] + "\"");
            System.out.println("    B: \"" + pair[1] + "\"\n");
        }
    }

    // ═══════════════════════════════════════════════════
    // PART 3: Semantic search
    // ═══════════════════════════════════════════════════

    static void demo3_SemanticSearch() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("PART 3: Semantic Search");
        System.out.println("═══════════════════════════════════════════\n");

        // Knowledge base
        String[] documents = {
                "Spring Boot provides auto-configuration for rapid application development",
                "HashMap uses hashing for O(1) key-value lookups in Java",
                "Docker containers package applications with their dependencies",
                "JUnit 5 supports parameterized tests for data-driven testing",
                "Kubernetes orchestrates container deployments at scale",
                "The GC in Java automatically manages memory allocation and deallocation",
                "REST APIs use HTTP methods like GET POST PUT DELETE",
                "Hibernate ORM maps Java objects to database tables",
        };

        // Pre-compute embeddings (in production, store these)
        System.out.println("  📚 Indexing " + documents.length + " documents...");
        double[][] docEmbeddings = new double[documents.length][];
        for (int i = 0; i < documents.length; i++) {
            docEmbeddings[i] = getEmbedding(documents[i]);
        }
        System.out.println("  ✅ Indexed!\n");

        // Search queries
        String[] queries = {
                "How do I deploy containers?",
                "What handles memory in Java?",
                "How to write tests?",
        };

        for (String query : queries) {
            System.out.println("  🔍 Query: \"" + query + "\"");
            double[] queryEmb = getEmbedding(query);

            // Score all documents
            record ScoredDoc(int index, double score) {
            }
            List<ScoredDoc> scored = new ArrayList<>();
            for (int i = 0; i < documents.length; i++) {
                scored.add(new ScoredDoc(i, cosineSimilarity(queryEmb, docEmbeddings[i])));
            }
            scored.sort((a, b) -> Double.compare(b.score(), a.score()));

            // Show top 3
            for (int i = 0; i < 3; i++) {
                ScoredDoc doc = scored.get(i);
                System.out.printf("     %d. [%.3f] %s%n", i + 1, doc.score(), documents[doc.index()]);
            }
            System.out.println();
        }
    }

    // ═══════════════════════════════════════════════════
    // MAIN
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 2.1: Embeddings Basics (Java)     ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY environment variable first!");
            return;
        }

        demo1_WhatAreEmbeddings();
        demo2_SimilarityComparison();
        demo3_SemanticSearch();

        System.out.println("✅ Key Takeaways:");
        System.out.println("  • Embeddings convert text → number vectors (1536 dims)");
        System.out.println("  • Cosine similarity measures semantic closeness (0-1)");
        System.out.println("  • Semantic search > keyword search for meaning-based retrieval");
        System.out.println("  • In production: store embeddings in a vector DB, not memory\n");
    }
}
