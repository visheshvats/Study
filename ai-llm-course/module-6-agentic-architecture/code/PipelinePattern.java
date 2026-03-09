
/**
 * MODULE 6 — Example 2: Pipeline Pattern (Java Equivalent)
 * ===========================================================
 * Java equivalent of 02_pipeline_pattern.py
 *
 * Sequential processing pipeline where each stage transforms data:
 *   Stage 1: Extract → Stage 2: Enhance → Stage 3: Format
 *   Like Spring Batch or Unix pipes: cmd1 | cmd2 | cmd3
 *
 * COMPILE & RUN:
 *   javac PipelinePattern.java && java PipelinePattern
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class PipelinePattern {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static String chat(String system, String user, double temp) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":%s,\"max_tokens\":500}"
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
    // PIPELINE: Stage 1 → Stage 2 → Stage 3
    // ═══════════════════════════════════════════════════

    static String runPipeline(String rawContent) throws Exception {
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  📥 Input content:");
        System.out.println("  " + rawContent.substring(0, Math.min(100, rawContent.length())) + "...\n");

        // Stage 1: Extract key information
        System.out.println("  ▶ Stage 1: EXTRACT key information");
        String extracted = chat(
                "Extract the key technical facts from this text. "
                        + "Return a bullet-point list of facts. Be precise and concise.",
                rawContent, 0.3);
        System.out.println("    ✅ " + extracted.substring(0, Math.min(150, extracted.length())) + "...\n");

        // Stage 2: Enhance with additional context
        System.out.println("  ▶ Stage 2: ENHANCE with Java-specific context");
        String enhanced = chat(
                "Take these technical facts and enrich them with Java-specific context. "
                        + "Add: relevant Java APIs, design patterns, best practices, and common pitfalls. "
                        + "Keep the bullet-point format.",
                "Facts to enhance:\n" + extracted, 0.5);
        System.out.println("    ✅ " + enhanced.substring(0, Math.min(150, enhanced.length())) + "...\n");

        // Stage 3: Format into a polished document
        System.out.println("  ▶ Stage 3: FORMAT into a tech blog post");
        String formatted = chat(
                "Transform this enhanced information into a well-structured technical blog post section. "
                        + "Include: a catchy subtitle, 2-3 paragraphs, and a code example if relevant. "
                        + "Target audience: intermediate Java developers.",
                "Content to format:\n" + enhanced, 0.7);
        System.out.println("    ✅ Formatted!\n");

        return formatted;
    }

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 6.2: Pipeline Pattern (Java)      ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        String rawContent = "Java 21 introduced virtual threads which are lightweight threads "
                + "managed by the JVM rather than the OS. They allow millions of concurrent threads "
                + "with minimal memory overhead. Virtual threads are supported in Spring Boot 3.2 "
                + "via spring.threads.virtual.enabled=true. They replace the need for reactive "
                + "programming (WebFlux) in many I/O-bound scenarios while keeping imperative code style.";

        String result = runPipeline(rawContent);

        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  📋 FINAL OUTPUT:\n");
        System.out.println("  " + result.replace("\n", "\n  "));

        System.out.println("\n  ✅ Pipeline Pattern: Extract → Enhance → Format");
        System.out.println("     Each stage transforms the output of the previous stage");
        System.out.println("     Like: cat file.txt | grep pattern | sort | head\n");
    }
}
