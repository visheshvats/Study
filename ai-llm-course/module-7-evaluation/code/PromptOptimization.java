
/**
 * MODULE 7 — Example 3: Prompt Optimization (Java Equivalent)
 * ==============================================================
 * Java equivalent of 03_prompt_optimization.py
 *
 * Systematically improve prompts by:
 *   1. Testing current prompt against test cases
 *   2. Analyzing failure patterns
 *   3. Generating improved prompts
 *   4. Comparing before/after performance
 *
 * COMPILE & RUN:
 *   javac PromptOptimization.java && java PromptOptimization
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;

public class PromptOptimization {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static String chat(String system, String user) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":0.3,\"max_tokens\":500}"
                .formatted(esc(system), esc(user));
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
    // TEST CASES
    // ═══════════════════════════════════════════════════

    record TestCase(String input, List<String> expectedKeywords, String qualityCheck) {
    }

    static final List<TestCase> TESTS = List.of(
            new TestCase("What is HashMap?",
                    List.of("hash", "key", "value", "O(1)"),
                    "Should explain internal implementation briefly"),
            new TestCase("How does garbage collection work?",
                    List.of("GC", "heap", "memory"),
                    "Should mention at least two GC algorithms"),
            new TestCase("Explain SOLID principles",
                    List.of("Single Responsibility", "Open", "Liskov"),
                    "Should list all 5 principles with brief explanations"));

    // ═══════════════════════════════════════════════════
    // EVALUATION
    // ═══════════════════════════════════════════════════

    static double evaluatePrompt(String systemPrompt, String label) throws Exception {
        System.out.println("\n  Evaluating: " + label);
        int totalScore = 0, maxScore = 0;

        for (TestCase test : TESTS) {
            String response = chat(systemPrompt, test.input);
            int score = 0, max = test.expectedKeywords.size() + 1;

            // Keyword checks
            for (String kw : test.expectedKeywords) {
                if (response.toLowerCase().contains(kw.toLowerCase()))
                    score++;
            }

            // Quality check
            String judge = chat("Does this response satisfy: " + test.qualityCheck
                    + "? Reply PASS or FAIL only.", response);
            if (judge.toUpperCase().contains("PASS"))
                score++;

            totalScore += score;
            maxScore += max;
            System.out.printf("    %s: %d/%d points%n",
                    test.input.substring(0, Math.min(30, test.input.length())), score, max);
        }

        double pct = (totalScore * 100.0) / maxScore;
        System.out.printf("  Total: %d/%d (%.0f%%)%n", totalScore, maxScore, pct);
        return pct;
    }

    // ═══════════════════════════════════════════════════
    // OPTIMIZATION
    // ═══════════════════════════════════════════════════

    static String optimizePrompt(String originalPrompt, String failureAnalysis) throws Exception {
        return chat(
                "You are a prompt engineering expert. Improve this system prompt "
                        + "to address the identified failures. Return ONLY the improved prompt.",
                "Original prompt:\n" + originalPrompt
                        + "\n\nFailure analysis:\n" + failureAnalysis
                        + "\n\nGenerate an improved version of the system prompt.");
    }

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 7.3: Prompt Optimization (Java)   ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        // Version 1: Basic prompt
        String v1 = "You are a Java assistant. Answer questions.";

        // Evaluate V1
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  📊 Round 1: Baseline Prompt");
        double score1 = evaluatePrompt(v1, "V1 (basic)");

        // Analyze failures and optimize
        System.out.println("\n  🔬 Analyzing failures...");
        String analysis = chat(
                "You are a QA analyst. Analyze what might be causing low scores with this prompt. "
                        + "The prompt is used for Java technical questions. "
                        + "Suggest specific improvements.",
                "Prompt: " + v1 + "\n\nRequired: detailed answers with O(1), GC algorithms, SOLID principles.");
        System.out.println("  Analysis: " + analysis.substring(0, Math.min(200, analysis.length())) + "...");

        // Generate improved prompt
        System.out.println("\n  ✏️ Optimizing prompt...");
        String v2 = optimizePrompt(v1, analysis);
        System.out.println("  V2: " + v2.substring(0, Math.min(150, v2.length())) + "...");

        // Evaluate V2
        System.out.println("\n  ═══════════════════════════════════════");
        System.out.println("  📊 Round 2: Optimized Prompt");
        double score2 = evaluatePrompt(v2, "V2 (optimized)");

        // Comparison
        System.out.println("\n  ═══════════════════════════════════════");
        System.out.println("  📊 COMPARISON");
        System.out.println("  ═══════════════════════════════════════");
        System.out.printf("  V1 (basic):     %.0f%%%n", score1);
        System.out.printf("  V2 (optimized): %.0f%%%n", score2);
        System.out.printf("  Improvement:    %+.0f%%%n", score2 - score1);

        System.out.println("\n  ✅ Prompt Optimization Loop:");
        System.out.println("     1. Define test cases with expected outputs");
        System.out.println("     2. Evaluate current prompt → get score");
        System.out.println("     3. Analyze failures");
        System.out.println("     4. Generate improved prompt");
        System.out.println("     5. Repeat until satisfied\n");
    }
}
