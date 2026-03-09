
/**
 * MODULE 7 — Example 1: Evaluation Basics (Java Equivalent)
 * ============================================================
 * Java equivalent of 01_evaluation_basics.py
 *
 * How to evaluate LLM outputs:
 *   1. Deterministic checks (exact match, contains, regex)
 *   2. LLM-as-Judge (use another LLM to evaluate quality)
 *   3. Metrics: relevance, accuracy, fluency, helpfulness
 *
 * COMPILE & RUN:
 *   javac EvaluationBasics.java && java EvaluationBasics
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.regex.*;

public class EvaluationBasics {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static String chat(String system, String user) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":0.0,\"max_tokens\":300}"
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
    // PART 1: Deterministic Evaluation
    // ═══════════════════════════════════════════════════

    record EvalResult(String metric, boolean passed, String detail) {
    }

    static List<EvalResult> deterministicEval(String response, String expectedSubstring,
            Pattern regex, int maxLength) {
        List<EvalResult> results = new ArrayList<>();

        // Contains check
        boolean contains = response.toLowerCase().contains(expectedSubstring.toLowerCase());
        results.add(new EvalResult("Contains expected", contains,
                "'" + expectedSubstring + "' " + (contains ? "found" : "NOT found")));

        // Regex check
        boolean matches = regex.matcher(response).find();
        results.add(new EvalResult("Matches pattern", matches, regex.pattern()));

        // Length check
        boolean lenOk = response.length() <= maxLength;
        results.add(new EvalResult("Within length", lenOk,
                response.length() + "/" + maxLength + " chars"));

        // Non-empty
        results.add(new EvalResult("Non-empty", !response.trim().isEmpty(), ""));

        return results;
    }

    // ═══════════════════════════════════════════════════
    // PART 2: LLM-as-Judge
    // ═══════════════════════════════════════════════════

    record JudgmentResult(int score, String reasoning) {
    }

    static JudgmentResult llmJudge(String question, String response, String criteria) throws Exception {
        String result = chat(
                "You are an AI response evaluator. Score the response on a scale of 1-5 "
                        + "based on these criteria: " + criteria + "\n\n"
                        + "Return ONLY in this format:\n"
                        + "SCORE: N\n"
                        + "REASON: one-line explanation",
                "Question: " + question + "\n\nResponse: " + response);

        int score = 3; // default
        String reason = result;
        try {
            var scoreMatcher = Pattern.compile("SCORE:\\s*(\\d)").matcher(result);
            if (scoreMatcher.find())
                score = Integer.parseInt(scoreMatcher.group(1));
            var reasonMatcher = Pattern.compile("REASON:\\s*(.+)").matcher(result);
            if (reasonMatcher.find())
                reason = reasonMatcher.group(1);
        } catch (Exception ignored) {
        }

        return new JudgmentResult(score, reason);
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 7.1: Evaluation Basics (Java)     ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        // Generate some responses to evaluate
        String question = "Explain dependency injection in Spring Boot";

        System.out.println("  Generating responses to evaluate...\n");
        String goodResponse = chat(
                "You are a helpful Java tutor. Give a clear, detailed explanation with a code example.", question);
        String vagueResponse = chat("Give a vague, unhelpful 1-sentence answer. Do not include examples.", question);

        // Part 1: Deterministic
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  PART 1: Deterministic Evaluation");
        System.out.println("  ═══════════════════════════════════════\n");

        System.out.println("  Good response:");
        var goodEvals = deterministicEval(goodResponse, "injection", Pattern.compile("@\\w+"), 2000);
        for (var e : goodEvals) {
            System.out.printf("    %s %s: %-20s %s%n", e.passed ? "✅" : "❌", e.metric, e.detail, "");
        }

        System.out.println("\n  Vague response:");
        var vagueEvals = deterministicEval(vagueResponse, "injection", Pattern.compile("@\\w+"), 2000);
        for (var e : vagueEvals) {
            System.out.printf("    %s %s: %-20s %s%n", e.passed ? "✅" : "❌", e.metric, e.detail, "");
        }

        // Part 2: LLM-as-Judge
        System.out.println("\n  ═══════════════════════════════════════");
        System.out.println("  PART 2: LLM-as-Judge Evaluation");
        System.out.println("  ═══════════════════════════════════════\n");

        String[] criteria = { "Accuracy", "Completeness", "Clarity", "Code Examples" };

        for (String criterion : criteria) {
            var goodJudge = llmJudge(question, goodResponse, criterion);
            var vagueJudge = llmJudge(question, vagueResponse, criterion);

            System.out.printf("  %-15s │ Good: %d/5 │ Vague: %d/5%n",
                    criterion, goodJudge.score, vagueJudge.score);
        }

        System.out.println("\n  ✅ Evaluation Approaches:");
        System.out.println("     • Deterministic: Fast, cheap, for structural checks");
        System.out.println("     • LLM-as-Judge: Flexible, semantic, for quality assessment");
        System.out.println("     • Combine both for comprehensive evaluation\n");
    }
}
