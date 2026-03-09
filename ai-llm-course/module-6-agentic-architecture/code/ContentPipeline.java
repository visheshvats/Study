
/**
 * MODULE 6 — PROJECT: Content Pipeline (Java Equivalent)
 * =========================================================
 * Java equivalent of 04_content_pipeline.py
 *
 * Combines all three patterns into a content generation pipeline:
 *   1. ROUTER: Classify content type
 *   2. PIPELINE: Multi-stage processing
 *   3. SUPERVISOR: Quality review loop
 *
 * COMPILE & RUN:
 *   javac ContentPipeline.java && java ContentPipeline
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ContentPipeline {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static String chat(String system, String user, double temp) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":%s,\"max_tokens\":600}"
                .formatted(esc(system), esc(user), temp);
        var req = HttpRequest.newBuilder().uri(URI.create(API_URL))
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

    // ═══════════════════════════════════════════════════
    // PHASE 1: ROUTER — Classify content type
    // ═══════════════════════════════════════════════════

    static String classifyContent(String topic) throws Exception {
        return chat("Classify this topic into one of: TUTORIAL, COMPARISON, DEEP_DIVE, QUICKSTART. "
                + "Return ONLY the category.", topic, 0.0).trim().toUpperCase();
    }

    // ═══════════════════════════════════════════════════
    // PHASE 2: PIPELINE — Generate content in stages
    // ═══════════════════════════════════════════════════

    static String generateContent(String topic, String type) throws Exception {
        System.out.println("    Pipeline Stage 1: Research...");
        String research = chat("You are a technical researcher. Gather key facts, APIs, patterns, "
                + "and best practices for this topic. Be thorough and accurate.",
                "Research: " + topic, 0.3);

        System.out.println("    Pipeline Stage 2: Draft...");
        String draft = chat("You are a technical writer. Using the research below, write a "
                + type + " article. Include code examples, practical tips, and clear explanations. "
                + "Structure with headers and sections.",
                "Topic: " + topic + "\n\nResearch:\n" + research, 0.7);

        System.out.println("    Pipeline Stage 3: Polish...");
        String polished = chat("You are an editor. Polish this draft: fix grammar, improve flow, "
                + "ensure code examples compile, add transitions between sections. "
                + "Make it engaging for intermediate Java developers.",
                "Draft to polish:\n" + draft, 0.5);

        return polished;
    }

    // ═══════════════════════════════════════════════════
    // PHASE 3: SUPERVISOR — Quality review
    // ═══════════════════════════════════════════════════

    static String reviewAndRefine(String content, String topic) throws Exception {
        for (int i = 1; i <= 2; i++) {
            System.out.println("    Supervisor Review " + i + "...");
            String review = chat("You are a senior tech editor. Review for: accuracy, completeness, "
                    + "code quality, readability. Start with 'APPROVED' if excellent, or give feedback.",
                    "Review:\n" + content, 0.3);

            if (review.toUpperCase().startsWith("APPROVED")) {
                System.out.println("    ✅ Approved on review " + i);
                return content;
            }

            System.out.println("    ✏️ Revising...");
            content = chat("Revise this content based on the editorial feedback.",
                    "Feedback:\n" + review + "\n\nContent:\n" + content, 0.5);
        }
        return content;
    }

    // ═══════════════════════════════════════════════════
    // FULL PIPELINE: Route → Generate → Review
    // ═══════════════════════════════════════════════════

    static void processContent(String topic) throws Exception {
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  📝 Topic: " + topic);
        System.out.println("  ═══════════════════════════════════════\n");

        // Phase 1: Route
        System.out.println("  Phase 1: ROUTER");
        String type = classifyContent(topic);
        System.out.println("    📋 Content type: " + type + "\n");

        // Phase 2: Pipeline
        System.out.println("  Phase 2: PIPELINE");
        String content = generateContent(topic, type);
        System.out.println("    ✅ Content generated\n");

        // Phase 3: Supervisor
        System.out.println("  Phase 3: SUPERVISOR");
        String finalContent = reviewAndRefine(content, topic);

        System.out.println("\n  ═══════════════════════════════════════");
        System.out.println("  📋 FINAL CONTENT:\n");
        System.out.println("  " + finalContent.replace("\n", "\n  "));
    }

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 6.4: Content Pipeline (Java)      ║");
        System.out.println("║  Combines: Router + Pipeline + Supervisor    ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        processContent("Implementing the Saga Pattern for distributed transactions in Spring Boot microservices");

        System.out.println("\n  ✅ Content Pipeline Architecture:");
        System.out.println("     1. ROUTER: Classify → type-specific handler");
        System.out.println("     2. PIPELINE: Research → Draft → Polish");
        System.out.println("     3. SUPERVISOR: Review → Revise → Approve\n");
    }
}
