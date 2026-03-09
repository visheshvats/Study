
/**
 * MODULE 0 — Example 1: Calling an LLM API (Java Equivalent)
 * =============================================================
 * Java equivalent of 01_call_llm_api.py
 *
 * Demonstrates:
 *   1. Basic LLM API call using java.net.http.HttpClient
 *   2. Using a system prompt to control behavior
 *   3. Temperature parameter for creativity vs determinism
 *
 * JAVA ANALOGY:
 *   - HttpClient is like RestTemplate / WebClient in Spring Boot
 *   - JSON building is like creating a DTO and serializing with Jackson
 *   - The OpenAI API is just a REST endpoint — same as calling any microservice
 *
 * SETUP:
 *   export OPENAI_API_KEY=your-key-here
 *
 * COMPILE & RUN:
 *   javac 01_CallLlmApi.java && java CallLlmApi
 *
 * REQUIRES: Java 11+ (java.net.http.HttpClient)
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.List;

public class CallLlmApi {

    // ═══════════════════════════════════════════════════
    // CONFIG — Like application.properties in Spring Boot
    // ═══════════════════════════════════════════════════

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final String MODEL = "gpt-4o-mini";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    // ═══════════════════════════════════════════════════
    // HELPER — Reusable LLM call method
    // (Like a @Service method in Spring Boot)
    // ═══════════════════════════════════════════════════

    /**
     * Call the OpenAI Chat Completions API.
     *
     * @param messages    JSON array string of messages [{role, content}, ...]
     * @param temperature creativity (0.0 = deterministic, 1.0 = creative)
     * @return the assistant's reply text
     */
    static String callLlm(String messagesJson, double temperature) throws Exception {
        // Build the request body JSON manually
        // In production, you'd use Jackson ObjectMapper or Gson
        String body = """
                {
                    "model": "%s",
                    "messages": %s,
                    "temperature": %s
                }
                """.formatted(MODEL, messagesJson, temperature);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_URL))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

        HttpResponse<String> response = httpClient.send(request,
                HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new RuntimeException("API error " + response.statusCode()
                    + ": " + response.body());
        }

        // Parse the response to extract the assistant's message
        // Simple JSON parsing without external libraries
        return extractContent(response.body());
    }

    /**
     * Extract "content" from the OpenAI response JSON.
     * A simple parser — in production, use Jackson/Gson.
     */
    static String extractContent(String json) {
        // Find "content": "..." in the response
        String marker = "\"content\":";
        int idx = json.indexOf(marker);
        if (idx == -1)
            return "[No content found in response]";

        // Skip past "content": and any whitespace
        idx += marker.length();
        while (idx < json.length() && (json.charAt(idx) == ' ' || json.charAt(idx) == '\n'))
            idx++;

        if (json.charAt(idx) == '"') {
            // Simple string value
            idx++; // skip opening quote
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
        return "[Unexpected JSON format]";
    }

    /**
     * Build a JSON messages array from role-content pairs.
     */
    static String buildMessages(String[][] messages) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < messages.length; i++) {
            if (i > 0)
                sb.append(",");
            String role = messages[i][0];
            String content = escapeJson(messages[i][1]);
            sb.append("""
                    {"role": "%s", "content": "%s"}""".formatted(role, content));
        }
        sb.append("]");
        return sb.toString();
    }

    static String escapeJson(String s) {
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\t", "\\t");
    }

    // ═══════════════════════════════════════════════════
    // DEMO 1: Basic API Call
    // ═══════════════════════════════════════════════════

    static void demo1_BasicCall() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("DEMO 1: Basic API Call");
        System.out.println("═══════════════════════════════════════════\n");

        String messages = buildMessages(new String[][] {
                { "user", "What is Java in one sentence?" }
        });

        String reply = callLlm(messages, 0.7);
        System.out.println("  🤖 Reply: " + reply);
    }

    // ═══════════════════════════════════════════════════
    // DEMO 2: System Prompt (Controlling Behavior)
    // ═══════════════════════════════════════════════════

    static void demo2_SystemPrompt() throws Exception {
        System.out.println("\n═══════════════════════════════════════════");
        System.out.println("DEMO 2: System Prompt — Controls Behavior");
        System.out.println("═══════════════════════════════════════════\n");

        // Without system prompt — generic answer
        String msgs1 = buildMessages(new String[][] {
                { "user", "Explain polymorphism" }
        });
        System.out.println("  📝 Without system prompt:");
        System.out.println("  " + callLlm(msgs1, 0.7));

        // With system prompt — targeted answer
        // System prompt is like @Profile or @Qualifier in Spring —
        // it tells the LLM WHAT ROLE to assume
        String msgs2 = buildMessages(new String[][] {
                { "system", "You are a Java instructor explaining to beginners. "
                        + "Use simple analogies and short code examples. Max 3 sentences." },
                { "user", "Explain polymorphism" }
        });
        System.out.println("\n  📝 With system prompt (Java instructor):");
        System.out.println("  " + callLlm(msgs2, 0.7));
    }

    // ═══════════════════════════════════════════════════
    // DEMO 3: Temperature (Creativity vs Precision)
    // ═══════════════════════════════════════════════════

    static void demo3_Temperature() throws Exception {
        System.out.println("\n═══════════════════════════════════════════");
        System.out.println("DEMO 3: Temperature — Creativity Control");
        System.out.println("═══════════════════════════════════════════\n");

        System.out.println("  Temperature is like a 'randomness dial':");
        System.out.println("    0.0 = Always pick the most likely word (deterministic)");
        System.out.println("    1.0 = More random word choices (creative)");
        System.out.println("    Think: autocomplete that always picks #1 vs sometimes #2 or #3\n");

        String msgLow = buildMessages(new String[][] {
                { "user", "Give me a one-line metaphor for Java interfaces" }
        });
        String msgHigh = buildMessages(new String[][] {
                { "user", "Give me a one-line metaphor for Java interfaces" }
        });

        System.out.println("  🧊 Temperature 0.0 (deterministic):");
        System.out.println("  " + callLlm(msgLow, 0.0));

        System.out.println("\n  🔥 Temperature 1.0 (creative):");
        System.out.println("  " + callLlm(msgHigh, 1.0));

        System.out.println("\n  💡 Rule of thumb:");
        System.out.println("    • Factual/code tasks → temperature 0.0-0.3");
        System.out.println("    • Creative writing   → temperature 0.7-1.0");
        System.out.println("    • General use         → temperature 0.5");
    }

    // ═══════════════════════════════════════════════════
    // MAIN
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 0.1: Calling LLM API (Java)      ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY environment variable first!");
            System.out.println("   export OPENAI_API_KEY=sk-your-key-here");
            return;
        }

        demo1_BasicCall();
        demo2_SystemPrompt();
        demo3_Temperature();

        System.out.println("\n\n✅ Key takeaways:");
        System.out.println("  • LLM APIs are just REST endpoints — HttpClient works fine");
        System.out.println("  • System prompts set the role (like @Profile in Spring)");
        System.out.println("  • Temperature controls randomness (0=precise, 1=creative)");
        System.out.println("  • In production, use Spring WebClient or RestTemplate\n");
    }
}
