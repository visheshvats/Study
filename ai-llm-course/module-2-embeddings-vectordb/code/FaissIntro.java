
/**
 * MODULE 2 — Example 4: FAISS Concepts (Java Equivalent)
 * =========================================================
 * Java equivalent of 04_faiss_intro.py
 *
 * NO API KEY NEEDED — all computation local!
 *
 * FAISS (Facebook AI Similarity Search) has no Java SDK.
 * We implement the core concepts in pure Java:
 *   1. Flat index (brute-force — exact but slow)
 *   2. IVF index (inverted file — approximate but fast)
 *   3. Performance comparison
 *
 * JAVA ANALOGY:
 *   - Flat index = ArrayList.contains() → O(n) linear scan
 *   - IVF index = HashMap bucketing → O(n/k) average search
 *   - Clustering = K-means for partitioning data into buckets
 *
 * COMPILE & RUN:
 *   javac FaissIntro.java && java FaissIntro
 */

import java.util.*;

public class FaissIntro {

    // ═══════════════════════════════════════════════════
    // SHARED UTILITIES
    // ═══════════════════════════════════════════════════

    static double cosineSimilarity(double[] a, double[] b) {
        double dot = 0, nA = 0, nB = 0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            nA += a[i] * a[i];
            nB += b[i] * b[i];
        }
        return dot / (Math.sqrt(nA) * Math.sqrt(nB));
    }

    static double euclideanDistance(double[] a, double[] b) {
        double sum = 0;
        for (int i = 0; i < a.length; i++) {
            double d = a[i] - b[i];
            sum += d * d;
        }
        return Math.sqrt(sum);
    }

    static double[] normalize(double[] v) {
        double norm = 0;
        for (double x : v)
            norm += x * x;
        norm = Math.sqrt(norm);
        double[] r = new double[v.length];
        for (int i = 0; i < v.length; i++)
            r[i] = v[i] / norm;
        return r;
    }

    static double[] randomVector(int dims, Random rng) {
        double[] v = new double[dims];
        for (int i = 0; i < dims; i++)
            v[i] = rng.nextGaussian();
        return normalize(v);
    }

    // ═══════════════════════════════════════════════════
    // INDEX 1: Flat Index (Exact / Brute-Force)
    // Like FAISS IndexFlatL2 / IndexFlatIP
    // ═══════════════════════════════════════════════════

    static class FlatIndex {
        private final List<double[]> vectors = new ArrayList<>();
        private final int dims;

        FlatIndex(int dims) {
            this.dims = dims;
        }

        void add(double[] vector) {
            vectors.add(vector);
        }

        void addAll(double[][] vecs) {
            for (var v : vecs)
                add(v);
        }

        int size() {
            return vectors.size();
        }

        /** Brute-force search: compare query to ALL vectors. */
        record SearchResult(int index, double distance) {
        }

        List<SearchResult> search(double[] query, int topK) {
            List<SearchResult> results = new ArrayList<>();
            for (int i = 0; i < vectors.size(); i++) {
                results.add(new SearchResult(i, euclideanDistance(query, vectors.get(i))));
            }
            results.sort(Comparator.comparingDouble(SearchResult::distance));
            return results.subList(0, Math.min(topK, results.size()));
        }
    }

    // ═══════════════════════════════════════════════════
    // INDEX 2: IVF Index (Approximate / Clustered)
    // Like FAISS IndexIVFFlat
    // ═══════════════════════════════════════════════════

    static class IVFIndex {
        private final int dims;
        private final int nClusters;
        private final int nProbe; // How many clusters to search
        private double[][] centroids;
        private List<List<Integer>> clusterAssignments; // cluster → vector indices
        private final List<double[]> allVectors = new ArrayList<>();

        IVFIndex(int dims, int nClusters, int nProbe) {
            this.dims = dims;
            this.nClusters = nClusters;
            this.nProbe = nProbe;
        }

        /** Train: run simplified K-means to find cluster centroids. */
        void train(double[][] trainingData) {
            Random rng = new Random(42);
            // Initialize centroids randomly from training data
            centroids = new double[nClusters][];
            Set<Integer> used = new HashSet<>();
            for (int i = 0; i < nClusters; i++) {
                int idx;
                do {
                    idx = rng.nextInt(trainingData.length);
                } while (used.contains(idx));
                used.add(idx);
                centroids[i] = Arrays.copyOf(trainingData[idx], dims);
            }

            // Run K-means for a few iterations
            for (int iter = 0; iter < 10; iter++) {
                // Assign each point to nearest centroid
                int[] assignments = new int[trainingData.length];
                for (int i = 0; i < trainingData.length; i++) {
                    assignments[i] = nearestCentroid(trainingData[i]);
                }

                // Update centroids
                for (int c = 0; c < nClusters; c++) {
                    double[] sum = new double[dims];
                    int count = 0;
                    for (int i = 0; i < trainingData.length; i++) {
                        if (assignments[i] == c) {
                            for (int d = 0; d < dims; d++)
                                sum[d] += trainingData[i][d];
                            count++;
                        }
                    }
                    if (count > 0) {
                        for (int d = 0; d < dims; d++)
                            centroids[c][d] = sum[d] / count;
                    }
                }
            }
        }

        private int nearestCentroid(double[] vec) {
            int best = 0;
            double bestDist = Double.MAX_VALUE;
            for (int c = 0; c < nClusters; c++) {
                double d = euclideanDistance(vec, centroids[c]);
                if (d < bestDist) {
                    bestDist = d;
                    best = c;
                }
            }
            return best;
        }

        /** Add vectors to the index (assigns to clusters). */
        void addAll(double[][] vectors) {
            clusterAssignments = new ArrayList<>();
            for (int i = 0; i < nClusters; i++)
                clusterAssignments.add(new ArrayList<>());

            for (var v : vectors) {
                int idx = allVectors.size();
                allVectors.add(v);
                int cluster = nearestCentroid(v);
                clusterAssignments.get(cluster).add(idx);
            }
        }

        /** Search: only check vectors in the nProbe closest clusters. */
        List<FlatIndex.SearchResult> search(double[] query, int topK) {
            // Find closest nProbe centroids
            record CentroidDist(int index, double distance) {
            }
            List<CentroidDist> centroidDists = new ArrayList<>();
            for (int c = 0; c < nClusters; c++) {
                centroidDists.add(new CentroidDist(c, euclideanDistance(query, centroids[c])));
            }
            centroidDists.sort(Comparator.comparingDouble(CentroidDist::distance));

            // Search only in the closest clusters
            List<FlatIndex.SearchResult> results = new ArrayList<>();
            int vectorsChecked = 0;
            for (int i = 0; i < Math.min(nProbe, nClusters); i++) {
                int cluster = centroidDists.get(i).index;
                for (int vecIdx : clusterAssignments.get(cluster)) {
                    results.add(new FlatIndex.SearchResult(vecIdx,
                            euclideanDistance(query, allVectors.get(vecIdx))));
                    vectorsChecked++;
                }
            }

            results.sort(Comparator.comparingDouble(FlatIndex.SearchResult::distance));
            return results.subList(0, Math.min(topK, results.size()));
        }

        int size() {
            return allVectors.size();
        }
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 2.4: FAISS Concepts (Java)        ║");
        System.out.println("║  NO API KEY NEEDED — runs locally            ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        int dims = 128;
        int numVectors = 50_000;
        Random rng = new Random(42);

        // Generate random vectors
        System.out.printf("  Generating %,d vectors (%d dims)...%n", numVectors, dims);
        double[][] data = new double[numVectors][];
        for (int i = 0; i < numVectors; i++)
            data[i] = randomVector(dims, rng);
        double[] query = randomVector(dims, rng);
        System.out.println("  ✅ Done\n");

        // ── Flat Index ──
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  INDEX 1: Flat (Exact Brute-Force)");
        System.out.println("  ═══════════════════════════════════════\n");

        FlatIndex flatIndex = new FlatIndex(dims);
        flatIndex.addAll(data);

        long t1 = System.nanoTime();
        var flatResults = flatIndex.search(query, 5);
        long flatTime = System.nanoTime() - t1;

        System.out.printf("  Search time: %.2f ms%n", flatTime / 1e6);
        System.out.printf("  Vectors checked: %,d (100%%)%n", numVectors);
        System.out.println("  Top 5:");
        for (var r : flatResults) {
            System.out.printf("    vec_%d (distance: %.4f)%n", r.index(), r.distance());
        }

        // ── IVF Index ──
        System.out.println("\n  ═══════════════════════════════════════");
        System.out.println("  INDEX 2: IVF (Approximate, Clustered)");
        System.out.println("  ═══════════════════════════════════════\n");

        int nClusters = 100;
        int nProbe = 10;

        System.out.printf("  Training IVF: %d clusters, nprobe=%d%n", nClusters, nProbe);
        IVFIndex ivfIndex = new IVFIndex(dims, nClusters, nProbe);

        long trainStart = System.nanoTime();
        ivfIndex.train(data);
        long trainTime = System.nanoTime() - trainStart;
        System.out.printf("  Training time: %.0f ms%n", trainTime / 1e6);

        ivfIndex.addAll(data);

        long t2 = System.nanoTime();
        var ivfResults = ivfIndex.search(query, 5);
        long ivfTime = System.nanoTime() - t2;

        System.out.printf("  Search time: %.2f ms%n", ivfTime / 1e6);
        System.out.printf("  Vectors checked: ~%,d (~%d%%)%n",
                numVectors / nClusters * nProbe,
                (100 * nProbe / nClusters));
        System.out.println("  Top 5:");
        for (var r : ivfResults) {
            System.out.printf("    vec_%d (distance: %.4f)%n", r.index(), r.distance());
        }

        // ── Comparison ──
        System.out.println("\n  ═══════════════════════════════════════");
        System.out.println("  📊 COMPARISON");
        System.out.println("  ═══════════════════════════════════════\n");
        System.out.printf("  %-12s │ %-10s │ %-8s │ %-8s%n", "Index", "Time (ms)", "Accuracy", "Vectors");
        System.out.println("  ─────────────┼────────────┼──────────┼─────────");
        System.out.printf("  %-12s │ %10.2f │ %-8s │ %,d%n", "Flat", flatTime / 1e6, "Exact", numVectors);
        System.out.printf("  %-12s │ %10.2f │ %-8s │ ~%,d%n", "IVF", ivfTime / 1e6, "~95-99%",
                numVectors / nClusters * nProbe);
        System.out.printf("%n  Speedup: %.1fx faster%n", (double) flatTime / ivfTime);

        // Check recall (how many IVF results are in flat results)
        Set<Integer> flatSet = new HashSet<>();
        for (var r : flatResults)
            flatSet.add(r.index());
        int matched = 0;
        for (var r : ivfResults)
            if (flatSet.contains(r.index()))
                matched++;
        System.out.printf("  Recall: %d/%d (%.0f%% of exact results found)%n",
                matched, flatResults.size(), (matched * 100.0 / flatResults.size()));

        System.out.println("\n  ✅ Key FAISS Concepts:");
        System.out.println("     • Flat: Exact but O(n) — good for < 100K vectors");
        System.out.println("     • IVF: Approximate but O(n/k) — good for millions");
        System.out.println("     • More clusters + fewer probes = faster but less accurate");
        System.out.println("     • In Java: Use HNSW libraries (like Lucene's vector search)\n");
    }
}
