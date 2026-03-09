
/**
 * MODULE 2 — Example 2: Similarity Search (Java Equivalent)
 * ============================================================
 * Java equivalent of 02_similarity_search.py
 *
 * NO API KEY NEEDED — all math computed locally!
 *
 * Demonstrates:
 *   1. Cosine similarity (angle between vectors)
 *   2. Euclidean distance (straight-line distance)
 *   3. Dot product (combined magnitude + direction)
 *   4. Brute-force vs pre-sorted search comparison
 *
 * JAVA ANALOGY:
 *   - Cosine similarity → Comparator<double[]> for semantic sorting
 *   - Euclidean distance → Math.sqrt() on feature differences
 *   - Index building → building a TreeMap or HashMap index
 *
 * COMPILE & RUN:
 *   javac SimilaritySearch.java && java SimilaritySearch
 */

import java.util.*;
import java.util.stream.IntStream;

public class SimilaritySearch {

    // ═══════════════════════════════════════════════════
    // SIMILARITY METRICS
    // ═══════════════════════════════════════════════════

    /** Cosine similarity: angle between vectors (1.0 = same direction). */
    static double cosineSimilarity(double[] a, double[] b) {
        double dot = 0, normA = 0, normB = 0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        return dot / (Math.sqrt(normA) * Math.sqrt(normB));
    }

    /** Euclidean distance: straight-line distance (0.0 = identical). */
    static double euclideanDistance(double[] a, double[] b) {
        double sum = 0;
        for (int i = 0; i < a.length; i++) {
            double diff = a[i] - b[i];
            sum += diff * diff;
        }
        return Math.sqrt(sum);
    }

    /** Dot product: combined magnitude and direction. */
    static double dotProduct(double[] a, double[] b) {
        double sum = 0;
        for (int i = 0; i < a.length; i++) {
            sum += a[i] * b[i];
        }
        return sum;
    }

    /** Normalize a vector to unit length. */
    static double[] normalize(double[] v) {
        double norm = 0;
        for (double x : v)
            norm += x * x;
        norm = Math.sqrt(norm);
        double[] result = new double[v.length];
        for (int i = 0; i < v.length; i++)
            result[i] = v[i] / norm;
        return result;
    }

    // ═══════════════════════════════════════════════════
    // PART 1: Compare All Three Metrics
    // ═══════════════════════════════════════════════════

    static void demo1_CompareMetrics() {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("PART 1: Similarity Metrics Compared");
        System.out.println("═══════════════════════════════════════════\n");

        // Simulated embeddings (2D for visualization)
        double[][] vectors = {
                { 1.0, 0.0 }, // → East
                { 0.7, 0.7 }, // ↗ Northeast
                { 0.0, 1.0 }, // ↑ North
                { -1.0, 0.0 }, // ← West (opposite of East)
                { 2.0, 0.0 }, // →→ East (same direction, bigger magnitude)
        };
        String[] labels = { "East", "NorthEast", "North", "West", "East(2x)" };

        System.out.println("  Comparing all pairs against East [1.0, 0.0]:\n");
        System.out.printf("  %-12s │ Cosine │ Euclidean │ Dot Product%n", "Vector");
        System.out.println("  ─────────────┼────────┼───────────┼────────────");

        double[] reference = vectors[0];
        for (int i = 0; i < vectors.length; i++) {
            System.out.printf("  %-12s │ %6.3f │ %9.3f │ %11.3f%n",
                    labels[i],
                    cosineSimilarity(reference, vectors[i]),
                    euclideanDistance(reference, vectors[i]),
                    dotProduct(reference, vectors[i]));
        }

        System.out.println("\n  💡 Key observations:");
        System.out.println("     • Cosine: Direction-only (East and East(2x) are identical)");
        System.out.println("     • Euclidean: Magnitude matters (East and East(2x) are far apart)");
        System.out.println("     • Dot product: Both direction AND magnitude\n");
        System.out.println("  📌 For text similarity: Use COSINE (direction = meaning)\n");
    }

    // ═══════════════════════════════════════════════════
    // PART 2: Brute-Force Search
    // ═══════════════════════════════════════════════════

    static void demo2_BruteForceSearch() {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("PART 2: Brute-Force Vector Search");
        System.out.println("═══════════════════════════════════════════\n");

        // Simulated document embeddings (128 dimensions)
        Random rng = new Random(42);
        int numDocs = 10_000;
        int dims = 128;

        System.out.printf("  Building index: %,d vectors × %d dimensions%n", numDocs, dims);

        double[][] database = new double[numDocs][dims];
        for (int i = 0; i < numDocs; i++) {
            for (int j = 0; j < dims; j++) {
                database[i][j] = rng.nextGaussian();
            }
            database[i] = normalize(database[i]);
        }

        // Query
        double[] query = new double[dims];
        for (int j = 0; j < dims; j++)
            query[j] = rng.nextGaussian();
        query = normalize(query);

        // Brute-force search
        long start = System.nanoTime();
        record ScoredResult(int index, double score) {
        }
        List<ScoredResult> results = new ArrayList<>();
        for (int i = 0; i < numDocs; i++) {
            results.add(new ScoredResult(i, cosineSimilarity(query, database[i])));
        }
        results.sort((a, b) -> Double.compare(b.score(), a.score()));
        long elapsed = System.nanoTime() - start;

        System.out.printf("  Search time: %.2f ms%n", elapsed / 1_000_000.0);
        System.out.println("  Top 5 results:");
        for (int i = 0; i < 5; i++) {
            System.out.printf("    %d. doc_%d (similarity: %.4f)%n",
                    i + 1, results.get(i).index(), results.get(i).score());
        }

        System.out.println("\n  💡 Brute-force is O(n × d) per query");
        System.out.println("     10K docs → fast. 10M docs → too slow!");
        System.out.println("     Solution: ANN algorithms (FAISS, HNSW) for O(log n)\n");
    }

    // ═══════════════════════════════════════════════════
    // PART 3: Performance Comparison
    // ═══════════════════════════════════════════════════

    static void demo3_PerformanceScaling() {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("PART 3: How Search Scales");
        System.out.println("═══════════════════════════════════════════\n");

        int dims = 128;
        int[] sizes = { 1_000, 5_000, 10_000, 50_000, 100_000 };
        Random rng = new Random(42);

        // Query vector
        double[] query = normalize(randomVector(dims, rng));

        System.out.printf("  %-15s │ Time (ms) │ Docs/ms%n", "Database Size");
        System.out.println("  ────────────────┼───────────┼────────");

        for (int size : sizes) {
            double[][] db = new double[size][];
            for (int i = 0; i < size; i++) {
                db[i] = normalize(randomVector(dims, rng));
            }

            long start = System.nanoTime();
            double bestScore = -1;
            for (int i = 0; i < size; i++) {
                double sim = cosineSimilarity(query, db[i]);
                if (sim > bestScore)
                    bestScore = sim;
            }
            long elapsed = System.nanoTime() - start;
            double ms = elapsed / 1_000_000.0;

            System.out.printf("  %,15d │ %9.2f │ %,.0f%n",
                    size, ms, size / ms);
        }

        System.out.println("\n  💡 Brute-force: Linear scaling O(n)");
        System.out.println("     For millions of vectors, use FAISS/HNSW → O(log n)\n");
    }

    static double[] randomVector(int dims, Random rng) {
        double[] v = new double[dims];
        for (int i = 0; i < dims; i++)
            v[i] = rng.nextGaussian();
        return v;
    }

    // ═══════════════════════════════════════════════════
    // MAIN
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 2.2: Similarity Search (Java)     ║");
        System.out.println("║  NO API KEY NEEDED — runs locally            ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        demo1_CompareMetrics();
        demo2_BruteForceSearch();
        demo3_PerformanceScaling();

        System.out.println("✅ Key Takeaways:");
        System.out.println("  • Cosine: Best for text similarity (ignores magnitude)");
        System.out.println("  • Euclidean: Good for spatial data");
        System.out.println("  • Brute-force: Simple but O(n) per query");
        System.out.println("  • For production: Use vector DBs (ChromaDB, Pinecone, Weaviate)\n");
    }
}
