
/**
 * MODULE 3 — PROJECT: RAG Chatbot (Java Equivalent)
 * =====================================================
 * Java equivalent of 04_rag_chatbot.py
 *
 * A conversational chatbot with RAG:
 *   - Indexes a knowledge base
 *   - Retrieves relevant context for each question
 *   - Maintains conversation history
 *   - Generates grounded answers with citations
 *
 * COMPILE & RUN:
 *   javac RagChatbot.java && java RagChatbot
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.stream.Collectors;

public class RagChatbot {

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
    // KNOWLEDGE BASE + CHAT STATE
    // ═══════════════════════════════════════════════════

    record Chunk(String id, String text, String source, double[] embedding) {
    }

    record Message(String role, String content) {
        String toJson() {
            return "{\"role\":\"%s\",\"content\":\"%s\"}".formatted(role, esc(content));
        }
    }

    private final List<Chunk> knowledge = new ArrayList<>();
    private final List<Message> history = new ArrayList<>();
    private final String systemPrompt;

    RagChatbot(String systemPrompt) {
        this.systemPrompt = systemPrompt;
        history.add(new Message("system", systemPrompt));
    }

    void addKnowledge(String id, String text, String source) throws Exception {
        knowledge.add(new Chunk(id, text, source, embed(text)));
    }

    List<Chunk> retrieve(String query, int topK) throws Exception {
        double[] qe = embed(query);
        record Scored(Chunk c, double s) {
        }
        return knowledge.stream().map(c -> new Scored(c, cosine(qe, c.embedding)))
                .sorted((a, b) -> Double.compare(b.s, a.s)).limit(topK)
                .map(sc -> sc.c).collect(Collectors.toList());
    }

    String chat(String userMessage) throws Exception {
        // Retrieve context
        List<Chunk> context = retrieve(userMessage, 3);

        // Build context string
        StringBuilder ctx = new StringBuilder();
        for (int i = 0; i < context.size(); i++) {
            ctx.append("[").append(i + 1).append("] (").append(context.get(i).source).append("): ")
                    .append(context.get(i).text).append("\n");
        }

        // Add augmented user message
        String augmented = "Context from knowledge base:\n" + ctx + "\nUser question: " + userMessage;
        history.add(new Message("user", augmented));

        // Build messages JSON
        StringBuilder msgs = new StringBuilder("[");
        for (int i = 0; i < history.size(); i++) {
            if (i > 0)
                msgs.append(",");
            msgs.append(history.get(i).toJson());
        }
        msgs.append("]");

        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":%s,\"temperature\":0.5,\"max_tokens\":500}"
                .formatted(msgs.toString());
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

        String reply = sb.toString();
        history.add(new Message("assistant", reply));
        return reply;
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 3.4: RAG Chatbot (Java)           ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        var bot = new RagChatbot(
                "You are a Java programming expert assistant. "
                        + "Answer questions using the provided context from the knowledge base. "
                        + "Always cite your sources with [1], [2], etc. "
                        + "If the context doesn't have the answer, say so. Be concise.");

        // Index knowledge base
        System.out.println("  📥 Indexing knowledge base...\n");
        String[][] docs = {
                { "1", "Spring Boot 3.2+ supports virtual threads with spring.threads.virtual.enabled=true. This makes all request handlers use virtual threads automatically.",
                        "spring-boot-3.2" },
                { "2", "Virtual threads are created with Thread.ofVirtual().start(runnable). They are lightweight (few KB) versus platform threads (1MB). Ideal for I/O-bound tasks.",
                        "java-21-docs" },
                { "3", "CompletableFuture.supplyAsync() runs tasks asynchronously. Use thenApply() for chaining. thenCombine() merges two futures. join() blocks until complete.",
                        "java-concurrency" },
                { "4", "Spring WebFlux uses reactive streams for non-blocking I/O. Uses Mono<T> for single values and Flux<T> for collections. Based on Project Reactor.",
                        "spring-webflux" },
                { "5", "Connection pool sizing: HikariCP default max is 10. Formula: connections = (CPU cores * 2) + effective_spindle_count. Too many connections cause contention.",
                        "hikari-tuning" },
                { "6", "Spring Data JPA repositories: extend JpaRepository<Entity,ID>. Custom queries with @Query annotation. Supports Specification for dynamic queries.",
                        "spring-data-docs" },
        };
        for (String[] d : docs) {
            bot.addKnowledge(d[0], d[1], d[2]);
        }
        System.out.println("  ✅ Indexed " + docs.length + " knowledge chunks\n");

        // Interactive mode or demo
        Scanner scanner = new Scanner(System.in);
        System.out.println("  🤖 RAG Chatbot ready! Ask Java/Spring questions.");
        System.out.println("  💡 Type /quit to exit\n");

        // Demo questions (auto-run if no terminal available)
        String[] demoQuestions = {
                "How do I enable virtual threads in Spring Boot?",
                "Should I use virtual threads or WebFlux for my web app?",
                "How do I size my database connection pool?",
        };

        for (String q : demoQuestions) {
            System.out.println("  👤 " + q);
            String answer = bot.chat(q);
            System.out.println("  🤖 " + answer + "\n");
        }

        // Interactive loop
        while (true) {
            System.out.print("  👤 You: ");
            if (!scanner.hasNextLine())
                break;
            String input = scanner.nextLine().trim();
            if (input.equals("/quit")) {
                System.out.println("  👋 Goodbye!");
                break;
            }
            if (input.isEmpty())
                continue;
            System.out.println("  🤖 " + bot.chat(input) + "\n");
        }
    }
}
