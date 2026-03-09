
/**
 * MODULE 1 — Example 1: Prompt Techniques (Java Equivalent)
 * ============================================================
 * Java equivalent of 01_prompt_techniques.py
 *
 * Compares 4 prompting strategies on the SAME question:
 *   1. Zero-shot — just ask, no examples
 *   2. Few-shot — provide examples first
 *   3. Chain-of-thought — "think step by step"
 *   4. Role prompting — assign an expert persona
 *
 * JAVA ANALOGY:
 *   - Zero-shot = calling a method with no context
 *   - Few-shot = providing sample test cases alongside the requirement
 *   - CoT = writing pseudocode before real code
 *   - Role = using @Profile to activate a specific Spring component
 *
 * COMPILE & RUN:
 *   javac PromptTechniques.java && java PromptTechniques
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class PromptTechniques {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final String MODEL = "gpt-4o-mini";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

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
                    "temperature": %s,
                    "max_tokens": 500
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

        return extractContent(response.body());
    }

    static String extractContent(String json) {
        String marker = "\"content\":";
        int idx = json.indexOf(marker);
        if (idx == -1)
            return "[No content]";
        idx += marker.length();
        while (idx < json.length() && (json.charAt(idx) == ' ' || json.charAt(idx) == '\n'))
            idx++;
        if (idx >= json.length() || json.charAt(idx) != '"')
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
    // TEST QUESTION — Same for all techniques
    // ═══════════════════════════════════════════════════

    static final String QUESTION = "A team has 5 microservices. Each service communicates with 2 others. "
            + "How many total communication channels exist? "
            + "Is this a good architecture?";

    // ═══════════════════════════════════════════════════
    // TECHNIQUE 1: Zero-Shot
    // ═══════════════════════════════════════════════════

    static void technique1_ZeroShot() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("TECHNIQUE 1: Zero-Shot (Just Ask)");
        System.out.println("═══════════════════════════════════════════");
        System.out.println("  Strategy: Ask directly, no examples or guidance\n");

        String reply = callLlm(null, QUESTION, 0.5);
        System.out.println("  🤖 " + reply + "\n");
    }

    // ═══════════════════════════════════════════════════
    // TECHNIQUE 2: Few-Shot (Provide Examples)
    // ═══════════════════════════════════════════════════

    static void technique2_FewShot() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("TECHNIQUE 2: Few-Shot (Examples First)");
        System.out.println("═══════════════════════════════════════════");
        System.out.println("  Strategy: Show examples of desired format, THEN ask\n");

        String prompt = """
                Here are examples of how to analyze microservice architectures:

                Example 1:
                Q: "3 services, each talks to 1 other"
                A: Communication channels = 3×1/2 = 1.5 → but channels are bidirectional, \
                so it's actually 3 pairs. This is a simple chain topology — good for small systems.

                Example 2:
                Q: "4 services, each talks to all 3 others"
                A: Fully connected mesh: C(4,2) = 6 channels. High coupling — consider \
                an API gateway or message broker to reduce direct connections.

                Now analyze:
                """ + QUESTION;

        String reply = callLlm(null, prompt, 0.5);
        System.out.println("  🤖 " + reply + "\n");
    }

    // ═══════════════════════════════════════════════════
    // TECHNIQUE 3: Chain-of-Thought (Step by Step)
    // ═══════════════════════════════════════════════════

    static void technique3_ChainOfThought() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("TECHNIQUE 3: Chain-of-Thought (Think Step by Step)");
        System.out.println("═══════════════════════════════════════════");
        System.out.println("  Strategy: Ask to reason through it step by step\n");

        String prompt = QUESTION + "\n\n"
                + "Think through this step by step:\n"
                + "1. First, calculate the raw number of connections\n"
                + "2. Account for bidirectional vs unidirectional\n"
                + "3. Compare this to a fully-connected topology\n"
                + "4. Give your architecture assessment";

        String reply = callLlm(null, prompt, 0.5);
        System.out.println("  🤖 " + reply + "\n");
    }

    // ═══════════════════════════════════════════════════
    // TECHNIQUE 4: Role Prompting (Expert Persona)
    // ═══════════════════════════════════════════════════

    static void technique4_RolePrompting() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("TECHNIQUE 4: Role Prompting (Expert Persona)");
        System.out.println("═══════════════════════════════════════════");
        System.out.println("  Strategy: Assign a specialist role via system prompt\n");

        String systemPrompt = "You are a senior solutions architect at Netflix with 15 years experience "
                + "building large-scale microservice architectures. You always analyze: "
                + "1) coupling metrics, 2) failure blast radius, 3) operational complexity. "
                + "You recommend concrete patterns (saga, event-driven, API gateway).";

        String reply = callLlm(systemPrompt, QUESTION, 0.5);
        System.out.println("  🤖 " + reply + "\n");
    }

    // ═══════════════════════════════════════════════════
    // MAIN
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 1.1: Prompt Techniques (Java)     ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY environment variable first!");
            return;
        }

        System.out.println("  📋 Question: \"" + QUESTION + "\"\n");

        technique1_ZeroShot();
        technique2_FewShot();
        technique3_ChainOfThought();
        technique4_RolePrompting();

        System.out.println("═══════════════════════════════════════════");
        System.out.println("📊 COMPARISON:");
        System.out.println("═══════════════════════════════════════════");
        System.out.println("  Zero-shot  → Quick but may miss nuance");
        System.out.println("  Few-shot   → Consistent format, follows examples");
        System.out.println("  CoT        → Best for math/logic, shows reasoning");
        System.out.println("  Role       → Domain expertise, professional quality\n");
        System.out.println("  💡 Pick based on your use case:");
        System.out.println("     Classification → Zero-shot or Few-shot");
        System.out.println("     Calculation    → Chain-of-thought");
        System.out.println("     Expert advice  → Role prompting\n");
    }
}
