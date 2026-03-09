
/**
 * MODULE 1 — Example 2: Structured Output (Java Equivalent)
 * ============================================================
 * Java equivalent of 02_structured_output.py
 *
 * Getting PARSEABLE structured data from LLMs:
 *   1. Prompt-based JSON request
 *   2. response_format: json_object (guaranteed valid JSON)
 *   3. Few-shot examples for consistent structure
 *
 * JAVA ANALOGY:
 *   - Structured output = defining a @RequestBody DTO
 *   - JSON mode = @JsonProperty with Jackson validation
 *   - The LLM output should be deserializable into a Java POJO
 *
 * COMPILE & RUN:
 *   javac StructuredOutput.java && java StructuredOutput
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class StructuredOutput {

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

    static String callLlm(String systemPrompt, String userPrompt, double temperature,
            boolean jsonMode) throws Exception {
        String systemPart = systemPrompt != null
                ? """
                        {"role": "system", "content": "%s"},""".formatted(escapeJson(systemPrompt))
                : "";

        String formatPart = jsonMode
                ? """
                        , "response_format": {"type": "json_object"}"""
                : "";

        String body = """
                {
                    "model": "%s",
                    "messages": [%s {"role": "user", "content": "%s"}],
                    "temperature": %s,
                    "max_tokens": 600%s
                }
                """.formatted(MODEL, systemPart, escapeJson(userPrompt), temperature, formatPart);

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
    // APPROACH 1: Prompt-Based JSON
    // ═══════════════════════════════════════════════════

    static void approach1_PromptBasedJson() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("APPROACH 1: Prompt-Based JSON Request");
        System.out.println("═══════════════════════════════════════════\n");
        System.out.println("  Strategy: Ask for JSON in the prompt (no guarantee)\n");

        String reply = callLlm(null,
                "Analyze this Java dependency and return JSON.\n\n"
                        + "Dependency: spring-boot-starter-web 3.2.0\n\n"
                        + "Return this exact JSON structure:\n"
                        + "{\n"
                        + "  \"name\": \"artifact name\",\n"
                        + "  \"version\": \"version\",\n"
                        + "  \"purpose\": \"what it does\",\n"
                        + "  \"key_features\": [\"feature1\", \"feature2\"],\n"
                        + "  \"security_risk\": \"low/medium/high\",\n"
                        + "  \"alternatives\": [\"alt1\", \"alt2\"]\n"
                        + "}\n\n"
                        + "Return ONLY the JSON, no markdown or explanation.",
                0.3, false);

        System.out.println("  Response:\n  " + reply);
        System.out.println("\n  ⚠️  Without json_mode, the LLM MIGHT wrap in ```json or add text\n");
    }

    // ═══════════════════════════════════════════════════
    // APPROACH 2: JSON Mode (Guaranteed Valid JSON)
    // ═══════════════════════════════════════════════════

    static void approach2_JsonMode() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("APPROACH 2: JSON Mode (response_format)");
        System.out.println("═══════════════════════════════════════════\n");
        System.out.println("  Strategy: Use response_format={type: json_object}\n");
        System.out.println("  Java equiv: Like @Valid @RequestBody ensuring valid JSON response\n");

        String systemPrompt = "You are a code review assistant. Always respond in JSON format.";

        String userPrompt = "Review this code snippet and return JSON:\n"
                + "```java\n"
                + "public class UserService {\n"
                + "    public User findUser(String id) {\n"
                + "        User user = userRepo.findById(id).get();\n"
                + "        return user;\n"
                + "    }\n"
                + "}\n"
                + "```\n\n"
                + "Return: {\"issues\": [{\"severity\": \"...\", \"line\": N, "
                + "\"issue\": \"...\", \"fix\": \"...\"}], "
                + "\"overall_quality\": \"good/needs_improvement/poor\", "
                + "\"score\": 1-10}";

        String reply = callLlm(systemPrompt, userPrompt, 0.3, true);
        System.out.println("  Response:\n  " + reply);

        // Validate it's parseable JSON
        boolean isValidJson = reply.trim().startsWith("{") && reply.trim().endsWith("}");
        System.out.println("\n  ✅ Valid JSON: " + isValidJson);
        System.out.println("  ✅ With json_mode, output is ALWAYS valid JSON\n");
    }

    // ═══════════════════════════════════════════════════
    // APPROACH 3: Few-Shot for Consistent Structure
    // ═══════════════════════════════════════════════════

    static void approach3_FewShotStructured() throws Exception {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("APPROACH 3: Few-Shot for Structure Consistency");
        System.out.println("═══════════════════════════════════════════\n");
        System.out.println("  Strategy: Show examples of desired JSON structure\n");

        String systemPrompt = "You are a dependency analyzer. Respond ONLY in JSON format.\n\n"
                + "Example input: \"junit-jupiter 5.9.3\"\n"
                + "Example output:\n"
                + "{\n"
                + "  \"artifact\": \"junit-jupiter\",\n"
                + "  \"version\": \"5.9.3\",\n"
                + "  \"category\": \"testing\",\n"
                + "  \"is_latest\": false,\n"
                + "  \"latest_version\": \"5.10.2\",\n"
                + "  \"recommendation\": \"Update to 5.10.x for better parameterized test support\"\n"
                + "}\n\n"
                + "Example input: \"jackson-databind 2.15.0\"\n"
                + "Example output:\n"
                + "{\n"
                + "  \"artifact\": \"jackson-databind\",\n"
                + "  \"version\": \"2.15.0\",\n"
                + "  \"category\": \"serialization\",\n"
                + "  \"is_latest\": false,\n"
                + "  \"latest_version\": \"2.17.0\",\n"
                + "  \"recommendation\": \"Update — 2.15.x has known deserialization vulnerabilities\"\n"
                + "}";

        String reply = callLlm(systemPrompt, "spring-boot-starter-data-jpa 3.1.0", 0.3, true);
        System.out.println("  Response:\n  " + reply);
        System.out.println("\n  ✅ Few-shot examples ensure consistent structure across calls\n");
    }

    // ═══════════════════════════════════════════════════
    // MAIN
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 1.2: Structured Output (Java)     ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY environment variable first!");
            return;
        }

        approach1_PromptBasedJson();
        approach2_JsonMode();
        approach3_FewShotStructured();

        System.out.println("═══════════════════════════════════════════");
        System.out.println("✅ Key Takeaways:");
        System.out.println("  • Prompt-based: Simple but output may include markdown/text");
        System.out.println("  • json_mode: Guaranteed valid JSON (use for production)");
        System.out.println("  • Few-shot: Ensures CONSISTENT structure across calls");
        System.out.println("  • In Java: Parse with Jackson/Gson, map to DTOs\n");
        System.out.println("  Production pattern:");
        System.out.println("    1. Define a Java record/class for the expected shape");
        System.out.println("    2. Use json_mode to guarantee valid JSON");
        System.out.println("    3. ObjectMapper.readValue(response, MyDTO.class)");
        System.out.println("    4. Validate with Jakarta Bean Validation (@NotNull, etc.)\n");
    }
}
