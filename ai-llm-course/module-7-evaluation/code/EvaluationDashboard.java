
/**
 * MODULE 7 — PROJECT: Evaluation Dashboard (Java Equivalent)
 * =============================================================
 * Java equivalent of 04_evaluation_dashboard.py
 *
 * A comprehensive evaluation system that:
 *   1. Runs multiple test suites
 *   2. Compares prompt variants
 *   3. Tracks metrics over time
 *   4. Generates a summary report
 *
 * COMPILE & RUN:
 *   javac EvaluationDashboard.java && java EvaluationDashboard
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.LocalDateTime;
import java.util.*;
import java.util.regex.*;

public class EvaluationDashboard {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static String chat(String system, String user) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":0.3,\"max_tokens\":400}"
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
    // DATA MODELS
    // ═══════════════════════════════════════════════════

    record TestCase(String name, String input, List<String> mustContain, int maxLength) {
    }

    record PromptVariant(String name, String systemPrompt) {
    }

    record TestResult(String testName, String variantName, boolean passed, int score, int maxScore, long latencyMs) {
    }

    // ═══════════════════════════════════════════════════
    // EVALUATION ENGINE
    // ═══════════════════════════════════════════════════

    static TestResult evaluate(TestCase test, PromptVariant variant) throws Exception {
        long start = System.currentTimeMillis();
        String response = chat(variant.systemPrompt, test.input);
        long latency = System.currentTimeMillis() - start;

        int score = 0, max = test.mustContain.size() + 1; // +1 for length check

        for (String kw : test.mustContain) {
            if (response.toLowerCase().contains(kw.toLowerCase()))
                score++;
        }

        if (test.maxLength <= 0 || response.length() <= test.maxLength)
            score++;

        return new TestResult(test.name, variant.name, score == max, score, max, latency);
    }

    // ═══════════════════════════════════════════════════
    // DASHBOARD
    // ═══════════════════════════════════════════════════

    static void runDashboard(List<TestCase> tests, List<PromptVariant> variants) throws Exception {
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  🧪 EVALUATION DASHBOARD");
        System.out.println("  ═══════════════════════════════════════\n");
        System.out.println("  Tests: " + tests.size());
        System.out.println("  Variants: " + variants.size());
        System.out.println("  Total evaluations: " + (tests.size() * variants.size()) + "\n");

        Map<String, List<TestResult>> resultsByVariant = new LinkedHashMap<>();

        // Run all evaluations
        for (PromptVariant variant : variants) {
            List<TestResult> variantResults = new ArrayList<>();
            System.out.println("  ⏳ Running variant: " + variant.name);

            for (TestCase test : tests) {
                TestResult result = evaluate(test, variant);
                variantResults.add(result);
                System.out.printf("    %s %s (%.0f%%, %dms)%n",
                        result.passed ? "✅" : "❌", result.testName,
                        (result.score * 100.0 / result.maxScore), result.latencyMs);
            }
            resultsByVariant.put(variant.name, variantResults);
            System.out.println();
        }

        // Summary report
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  📊 SUMMARY REPORT");
        System.out.println("  ═══════════════════════════════════════\n");
        System.out.printf("  %-20s │ Pass Rate │ Avg Score │ Avg Latency%n", "Variant");
        System.out.println("  ─────────────────────┼───────────┼───────────┼────────────");

        String bestVariant = null;
        double bestRate = -1;

        for (var entry : resultsByVariant.entrySet()) {
            List<TestResult> results = entry.getValue();
            long passed = results.stream().filter(r -> r.passed).count();
            double passRate = (passed * 100.0) / results.size();
            double avgScore = results.stream().mapToDouble(r -> (r.score * 100.0 / r.maxScore)).average().orElse(0);
            double avgLatency = results.stream().mapToLong(r -> r.latencyMs).average().orElse(0);

            System.out.printf("  %-20s │ %7.0f%% │ %7.0f%% │ %8.0f ms%n",
                    entry.getKey(), passRate, avgScore, avgLatency);

            if (passRate > bestRate) {
                bestRate = passRate;
                bestVariant = entry.getKey();
            }
        }

        System.out.println(
                "\n  🏆 Best variant: " + bestVariant + " (" + String.format("%.0f", bestRate) + "% pass rate)");

        // Per-test breakdown
        System.out.println("\n  ──── Per-Test Breakdown ────\n");
        for (TestCase test : tests) {
            System.out.println("  📝 " + test.name + ":");
            for (var entry : resultsByVariant.entrySet()) {
                TestResult r = entry.getValue().stream()
                        .filter(res -> res.testName.equals(test.name)).findFirst().orElse(null);
                if (r != null) {
                    System.out.printf("    %-18s: %s %d/%d%n",
                            entry.getKey(), r.passed ? "✅" : "❌", r.score, r.maxScore);
                }
            }
        }
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 7.4: Evaluation Dashboard (Java)  ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        // Test cases
        List<TestCase> tests = List.of(
                new TestCase("HashMap Internals", "Explain how HashMap works internally in Java",
                        List.of("hash", "bucket", "O(1)"), 1500),
                new TestCase("Spring DI", "Explain dependency injection in Spring",
                        List.of("@Autowired", "bean", "IoC"), 1500),
                new TestCase("Thread Safety", "How to make a Java class thread-safe?",
                        List.of("synchronized", "thread"), 1500),
                new TestCase("Brief Answer", "What is JPA?",
                        List.of("Java Persistence"), 500));

        // Prompt variants to compare
        List<PromptVariant> variants = List.of(
                new PromptVariant("Basic", "You are a Java assistant."),
                new PromptVariant("Detailed", "You are a senior Java developer. Always include: "
                        + "code examples, complexity analysis, and best practices. Be thorough but concise."),
                new PromptVariant("Structured", "You are a Java expert. Structure every response as: "
                        + "1) Definition, 2) How it works, 3) Code example, 4) Best practices. "
                        + "Include Big-O notation where relevant. Be concise."));

        runDashboard(tests, variants);

        System.out.println("\n  ✅ Evaluation Dashboard:");
        System.out.println("     • Define test cases + prompt variants");
        System.out.println("     • Run all combinations automatically");
        System.out.println("     • Compare pass rates, scores, latency");
        System.out.println("     • Pick the best prompt variant for production\n");
    }
}
