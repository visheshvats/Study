
/**
 * MODULE 3 — Example 3: Advanced RAG (Java Equivalent)
 * =======================================================
 * Java equivalent of 03_advanced_rag.py
 *
 * Advanced RAG patterns that improve over naive RAG:
 *   1. Multi-Query: Generate multiple search queries from one question
 *   2. Reranking: Use LLM to rerank retrieved results by relevance
 *   3. Citations: Generate answers with source references
 *
 * COMPILE & RUN:
 *   javac AdvancedRag.java && java AdvancedRag
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.stream.Collectors;

public class AdvancedRag {

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
        String json = resp.body();
        int s = json.indexOf("[", json.indexOf("\"embedding\":")), e = json.indexOf("]", s);
        String[] parts = json.substring(s + 1, e).split(",");
        double[] vec = new double[parts.length];
        for (int i = 0; i < parts.length; i++)
            vec[i] = Double.parseDouble(parts[i].trim());
        return vec;
    }

    static String chat(String system, String user) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":0.3,\"max_tokens\":600}"
                .formatted(esc(system), esc(user));
        var req = HttpRequest.newBuilder().uri(URI.create(CHAT_URL))
                .header("Content-Type", "application/json").header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        var resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
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

    // Knowledge base
    record Doc(String id, String text, String source, double[] embedding) {
    }

    static List<Doc> kb = new ArrayList<>();

    static void index(String[][] docs) throws Exception {
        for (String[] d : docs)
            kb.add(new Doc(d[0], d[1], d[2], embed(d[1])));
    }

    static List<Doc> search(String query, int topK) throws Exception {
        double[] qe = embed(query);
        record Scored(Doc doc, double score) {
        }
        return kb.stream().map(d -> new Scored(d, cosine(qe, d.embedding)))
                .sorted((a, b) -> Double.compare(b.score, a.score)).limit(topK)
                .map(s -> s.doc).collect(Collectors.toList());
    }

    // ═══════════════════════════════════════════════════
    // PATTERN 1: Multi-Query Retrieval
    // ═══════════════════════════════════════════════════

    static List<Doc> multiQueryRetrieve(String question, int topK) throws Exception {
        System.out.println("  ▶ Multi-Query: Generating search queries...");
        String queries = chat(
                "Generate 3 different search queries for the given question. "
                        + "Each should approach the topic from a different angle. "
                        + "Return ONLY the 3 queries, one per line, no numbering.",
                question);

        System.out.println("    Generated queries:");
        String[] queryList = queries.split("\n");
        Set<String> seenIds = new HashSet<>();
        List<Doc> allResults = new ArrayList<>();

        for (String q : queryList) {
            q = q.trim();
            if (q.isEmpty())
                continue;
            System.out.println("      → " + q);
            for (Doc doc : search(q, topK)) {
                if (seenIds.add(doc.id))
                    allResults.add(doc);
            }
        }
        // Also search with original
        for (Doc doc : search(question, topK)) {
            if (seenIds.add(doc.id))
                allResults.add(doc);
        }
        System.out.println("    Total unique results: " + allResults.size());
        return allResults;
    }

    // ═══════════════════════════════════════════════════
    // PATTERN 2: LLM Reranking
    // ═══════════════════════════════════════════════════

    static List<Doc> rerank(String question, List<Doc> candidates) throws Exception {
        System.out.println("  ▶ Reranking " + candidates.size() + " results...");
        StringBuilder docsStr = new StringBuilder();
        for (int i = 0; i < candidates.size(); i++) {
            docsStr.append("[").append(i).append("] ").append(candidates.get(i).text).append("\n");
        }

        String result = chat(
                "You are a relevance ranker. Given a question and candidate documents, "
                        + "rank them by relevance. Return ONLY the indices in order from most to least relevant, "
                        + "comma-separated. Example: 2,0,3,1",
                "Question: " + question + "\n\nDocuments:\n" + docsStr);

        List<Doc> reranked = new ArrayList<>();
        for (String idx : result.split("[,\\s]+")) {
            try {
                int i = Integer.parseInt(idx.trim());
                if (i >= 0 && i < candidates.size())
                    reranked.add(candidates.get(i));
            } catch (NumberFormatException ignored) {
            }
        }
        // Add any missing docs
        for (Doc d : candidates)
            if (!reranked.contains(d))
                reranked.add(d);

        System.out.println("    Reranked order: " + result.trim());
        return reranked;
    }

    // ═══════════════════════════════════════════════════
    // PATTERN 3: Answer with Citations
    // ═══════════════════════════════════════════════════

    static String answerWithCitations(String question, List<Doc> context) throws Exception {
        System.out.println("  ▶ Generating answer with citations...");
        StringBuilder ctx = new StringBuilder();
        for (int i = 0; i < context.size(); i++) {
            ctx.append("[").append(i + 1).append("] (").append(context.get(i).source).append("): ")
                    .append(context.get(i).text).append("\n");
        }

        return chat(
                "Answer the question using the provided context. "
                        + "RULES:\n"
                        + "1. Cite sources with [1], [2], etc.\n"
                        + "2. Only use information from the context\n"
                        + "3. If you're unsure, say so\n"
                        + "4. End with 'Sources:' listing the references used",
                "Context:\n" + ctx + "\nQuestion: " + question);
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 3.3: Advanced RAG (Java)          ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        String[][] docs = {
                { "1", "Virtual threads in Java 21 are lightweight threads managed by the JVM. They enable millions of concurrent threads. Created via Thread.ofVirtual(). Best for I/O-bound work like HTTP calls and DB queries.",
                        "java-21-docs" },
                { "2", "Platform threads map 1:1 to OS threads. They are heavyweight (1MB stack each). Limited to thousands. Good for CPU-bound computation. Use for parallel streams and compute-intensive work.",
                        "java-threading-guide" },
                { "3", "Project Loom introduced virtual threads to solve the thread-per-request scalability problem. Previously, reactive programming (WebFlux) was needed for high concurrency. Virtual threads offer the same scalability with imperative code.",
                        "project-loom-jep" },
                { "4", "Spring Boot 3.2 supports virtual threads via spring.threads.virtual.enabled=true. This makes all request handling use virtual threads. Compatible with Spring MVC, not needed for WebFlux.",
                        "spring-boot-3.2-notes" },
                { "5", "Thread pools with virtual threads: Don't pool virtual threads (they're cheap to create). Use Executors.newVirtualThreadPerTaskExecutor(). Avoid ThreadLocal with virtual threads as they share carrier threads.",
                        "java-concurrency-best-practices" },
                { "6", "Structured concurrency (preview in Java 21) groups related virtual threads. Use StructuredTaskScope for fork-join style concurrent operations. Ensures all subtasks complete or cancel together.",
                        "java-21-preview-features" },
        };

        System.out.println("  📥 Indexing...");
        index(docs);
        System.out.println("  ✅ Indexed " + kb.size() + " documents\n");

        String question = "How should I use virtual threads in my Spring Boot application?";
        System.out.println("  👤 Question: " + question + "\n");

        // Step 1: Multi-query retrieval
        List<Doc> retrieved = multiQueryRetrieve(question, 3);

        // Step 2: Rerank
        System.out.println();
        List<Doc> reranked = rerank(question, retrieved);

        // Step 3: Answer with citations (use top 4)
        System.out.println();
        List<Doc> topContext = reranked.subList(0, Math.min(4, reranked.size()));
        String answer = answerWithCitations(question, topContext);

        System.out.println("\n  ═══════════════════════════════════════");
        System.out.println("  🤖 ANSWER:\n");
        System.out.println("  " + answer);

        System.out.println("\n  ✅ Advanced RAG Patterns:");
        System.out.println("     1. Multi-query → covers more search angles");
        System.out.println("     2. Reranking → LLM judges relevance > cosine alone");
        System.out.println("     3. Citations → trustworthy, verifiable answers\n");
    }
}
