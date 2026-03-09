
/**
 * MODULE 0 — Example 2: Basic Prompt Engineering (Java Equivalent)
 * ==================================================================
 * Java equivalent of 02_basic_prompts.py
 *
 * Demonstrates prompt engineering patterns that work with ANY LLM:
 *   1. Vague vs Specific prompts
 *   2. Unstructured vs Structured output
 *   3. Role prompting (persona assignment)
 *
 * JAVA ANALOGY:
 *   - Vague prompt = vague JIRA ticket → unpredictable result
 *   - Specific prompt = detailed API contract → expected output
 *   - Role prompt = @Profile annotation → specialized behavior
 *   - Structured output = DTO with @JsonProperty → parseable
 *
 * COMPILE & RUN:
 *   javac 02_BasicPrompts.java && java BasicPrompts
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class BasicPrompts {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final String MODEL = "gpt-4o-mini";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    // ── Reusable helpers ──

    static String escapeJson(String s) {
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\t", "\\t");
    }

    static String callLlm(String systemPrompt, String userPrompt, double temperature) throws Exception {
        String systemPart = systemPrompt != null
                ? """
                        {"role": "system", "content": "%s"},""".formatted(escapeJson(systemPrompt))
                : "";

        String body = """
                {
                    "model": "%s",
                    "messages": [%s {"role": "user", "content": "%s"}],
                    "temperature": %s
                }
                """.formatted(MODEL, systemPart, escapeJson(userPrompt), temperature);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_URL))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

        HttpResponse<String> response = httpClient.send(request,
                HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new RuntimeException("API error " + response.statusCode() + ": " + response.body());
        }

        // Extract content from response
        String json = response.body();
        String marker = "\"content\":";
        int idx = json.indexOf(marker);
        if (idx == -1)
            return "[No content]";
        idx += marker.length();
        while (idx < json.length() && (json.charAt(idx) == ' ' || json.charAt(idx) == '\n'))
            idx++;
        if (json.charAt(idx) != '"')
            return "[Unexpected format]";
        idx++;
        StringBuilder sb = new StringBuilder();
        while (idx < json.length()) {
            char c = json.charAt(idx);
            if (c == '\\' && idx + 1 < json.length()) {
                char next = json.charAt(idx + 1);
                switch (next) {
                    case '"':
                        sb.append('"');
                        idx += 2;
                        continue;
                    case '\\':
                        sb.append('\\');
                        idx += 2;
                        continue;
                    case 'n':
                        sb.append('\n');
                        idx += 2;
                        continue;
                    case 't':
                        sb.append('\t');
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
    // DEMO 1: Vague vs Specific Prompts
    // ═══════════════════════════════════════════════════

    static void demo1_VagueVsSpecific() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("DEMO 1: Vague vs Specific Prompts");
        System.out.println("═══════════════════════════════════════════\n");

        // Vague prompt — like a vague JIRA ticket
        System.out.println("  ❌ Vague: \"Tell me about Spring Boot\"");
        String vague = callLlm(null, "Tell me about Spring Boot", 0.7);
        System.out.println("  → " + vague.substring(0, Math.min(200, vague.length())) + "...\n");

        // Specific prompt — like a detailed API contract
        System.out.println("  ✅ Specific: Clear constraints + desired format");
        String specific = callLlm(null,
                "List the top 3 advantages of Spring Boot over plain Spring Framework. "
                        + "For each, give a one-sentence explanation and a practical example. "
                        + "Target audience: Java developer with 2 years experience.",
                0.7);
        System.out.println("  → " + specific + "\n");

        System.out.println("  💡 Lesson: Specific prompts = specific results");
        System.out.println("     Like writing a good API specification vs a vague requirement\n");
    }

    // ═══════════════════════════════════════════════════
    // DEMO 2: Unstructured vs Structured Output
    // ═══════════════════════════════════════════════════

    static void demo2_StructuredOutput() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("DEMO 2: Unstructured vs Structured Output");
        System.out.println("═══════════════════════════════════════════\n");

        // Unstructured — hard to parse in code
        System.out.println("  ❌ Unstructured: \"Compare Java and Kotlin\"");
        String unstructured = callLlm(null, "Compare Java and Kotlin briefly", 0.5);
        System.out.println("  → " + unstructured.substring(0, Math.min(200, unstructured.length())) + "...\n");

        // Structured — parseable by code (like @RequestBody with a DTO)
        System.out.println("  ✅ Structured: Request JSON output");
        String structured = callLlm(null,
                "Compare Java and Kotlin. Return JSON with this exact format:\n"
                        + "{\n"
                        + "  \"comparison\": [\n"
                        + "    {\"feature\": \"...\", \"java\": \"...\", \"kotlin\": \"...\", \"winner\": \"...\"}\n"
                        + "  ],\n"
                        + "  \"recommendation\": \"...\"\n"
                        + "}\n"
                        + "Include 3 features: null safety, verbosity, and learning curve.",
                0.3);
        System.out.println("  → " + structured + "\n");

        System.out.println("  💡 Lesson: Ask for JSON → get parseable output");
        System.out.println("     Like defining a ResponseDTO in Spring Boot\n");
    }

    // ═══════════════════════════════════════════════════
    // DEMO 3: Role Prompting (Persona Assignment)
    // ═══════════════════════════════════════════════════

    static void demo3_RolePrompting() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("DEMO 3: Role Prompting — Same Question, Different Expert");
        System.out.println("═══════════════════════════════════════════\n");

        String question = "How should I handle database connections in a web application?";

        String[][] roles = {
                { "Junior Java developer", "You are a junior Java developer. Explain simply with basic examples." },
                { "Senior architect", "You are a senior software architect with 15 years experience. "
                        + "Focus on patterns, scalability, and trade-offs. Be concise." },
                { "DevOps engineer", "You are a DevOps engineer focused on reliability and monitoring. "
                        + "Focus on connection pool metrics, health checks, and failure modes." },
        };

        System.out.println("  Question: \"" + question + "\"\n");

        for (String[] roleConfig : roles) {
            String roleName = roleConfig[0];
            String systemPrompt = roleConfig[1];

            System.out.println("  🎭 Role: " + roleName);
            String reply = callLlm(systemPrompt, question, 0.5);
            // Show first 250 chars
            String preview = reply.length() > 250 ? reply.substring(0, 250) + "..." : reply;
            System.out.println("  → " + preview);
            System.out.println();
        }

        System.out.println("  💡 Lesson: Same question, different system prompts → different expertise");
        System.out.println("     Like @Profile(\"dev\") vs @Profile(\"prod\") in Spring\n");
    }

    // ═══════════════════════════════════════════════════
    // MAIN
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 0.2: Prompt Engineering (Java)    ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY environment variable first!");
            return;
        }

        demo1_VagueVsSpecific();
        demo2_StructuredOutput();
        demo3_RolePrompting();

        System.out.println("✅ Key takeaways:");
        System.out.println("  • Specific prompts give predictable results (like API contracts)");
        System.out.println("  • Request JSON format for machine-parseable output (like DTOs)");
        System.out.println("  • System prompts control the LLM's persona (like @Profile)\n");
    }
}
