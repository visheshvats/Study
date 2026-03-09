
/**
 * MODULE 6 — Example 1: Router Pattern (Java Equivalent)
 * =========================================================
 * Java equivalent of 01_router_pattern.py
 *
 * The Router pattern:
 *   - LLM classifies the input into a category
 *   - Routes to the appropriate specialized handler
 *   - Like a Spring @Controller with @RequestMapping routing
 *
 * COMPILE & RUN:
 *   javac RouterPattern.java && java RouterPattern
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;

public class RouterPattern {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static String chat(String system, String user, double temp) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":%s,\"max_tokens\":400}"
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
    // ROUTER: Classify → Route → Handle
    // ═══════════════════════════════════════════════════

    static String classify(String input) throws Exception {
        return chat(
                "Classify the user's request into exactly ONE category. "
                        + "Categories: CODE_REVIEW, BUG_REPORT, FEATURE_REQUEST, GENERAL_QUESTION, OFF_TOPIC. "
                        + "Return ONLY the category name, nothing else.",
                input, 0.0).trim().toUpperCase();
    }

    static final Map<String, String> HANDLERS = Map.of(
            "CODE_REVIEW", "You are a senior Java code reviewer. Focus on: naming, SOLID principles, "
                    + "performance, security, and best practices. Be specific and constructive.",
            "BUG_REPORT", "You are a debugging expert. Ask clarifying questions about: environment, "
                    + "steps to reproduce, expected vs actual behavior. Suggest likely root causes.",
            "FEATURE_REQUEST", "You are a product analyst. Evaluate: feasibility, impact, effort. "
                    + "Suggest implementation approach and potential trade-offs.",
            "GENERAL_QUESTION", "You are a helpful Java programming tutor. Give clear, concise answers "
                    + "with code examples when appropriate.",
            "OFF_TOPIC", "You are a friendly assistant. Politely redirect the user to Java-related topics. "
                    + "Suggest what they could ask about instead.");

    static String route(String input) throws Exception {
        String category = classify(input);
        System.out.println("    📋 Category: " + category);

        String systemPrompt = HANDLERS.getOrDefault(category,
                HANDLERS.get("GENERAL_QUESTION"));

        return chat(systemPrompt, input, 0.5);
    }

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 6.1: Router Pattern (Java)        ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        String[] inputs = {
                "Review: public void process(Object o) { if (o != null) { String s = (String)o; System.out.println(s); }}",
                "My Spring Boot app throws 'BeanDefinitionOverrideException' after upgrading to 3.x",
                "Can we add GraphQL support to our REST API?",
                "What's the difference between @Component and @Service?",
                "What's the best pizza in NYC?",
        };

        for (String input : inputs) {
            System.out.println("  ═══════════════════════════════════════");
            System.out.println(
                    "    👤 " + input.substring(0, Math.min(70, input.length())) + (input.length() > 70 ? "..." : ""));
            String reply = route(input);
            System.out.println("    🤖 " + reply.substring(0, Math.min(200, reply.length())) + "...\n");
        }

        System.out.println("  ✅ Router Pattern: Classify → Route → Specialized Handler");
        System.out.println("     Like @RequestMapping + HandlerMapping in Spring MVC\n");
    }
}
