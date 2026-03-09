
/**
 * MODULE 7 — Example 2: Test Framework (Java Equivalent)
 * =========================================================
 * Java equivalent of 02_test_framework.py
 *
 * A lightweight test framework for evaluating LLM outputs:
 *   - Define test cases with expected behaviors
 *   - Run tests and collect results
 *   - Generate reports with pass/fail stats
 *
 * JAVA ANALOGY:
 *   Like JUnit, but for LLM outputs:
 *   @Test → TestCase record
 *   Assertions → deterministic + LLM-based checks
 *   @TestReport → summary with scores
 *
 * COMPILE & RUN:
 *   javac TestFramework.java && java TestFramework
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.regex.*;

public class TestFramework {

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
    // TEST FRAMEWORK
    // ═══════════════════════════════════════════════════

    record TestCase(String name, String systemPrompt, String userInput,
            List<String> mustContain, List<String> mustNotContain,
            int maxLength, String qualityCriteria) {
    }

    record TestResult(String name, boolean passed, List<String> details) {
    }

    static TestResult runTest(TestCase test) throws Exception {
        System.out.println("  ⏳ Running: " + test.name);
        List<String> details = new ArrayList<>();
        boolean allPassed = true;

        // Get LLM response
        String response = chat(test.systemPrompt, test.userInput);

        // Check must-contain
        for (String expected : test.mustContain) {
            boolean found = response.toLowerCase().contains(expected.toLowerCase());
            details.add((found ? "✅" : "❌") + " Contains '" + expected + "'");
            if (!found)
                allPassed = false;
        }

        // Check must-not-contain
        for (String forbidden : test.mustNotContain) {
            boolean found = response.toLowerCase().contains(forbidden.toLowerCase());
            details.add((!found ? "✅" : "❌") + " Does not contain '" + forbidden + "'");
            if (found)
                allPassed = false;
        }

        // Check length
        if (test.maxLength > 0) {
            boolean lenOk = response.length() <= test.maxLength;
            details.add((lenOk ? "✅" : "❌") + " Length: " + response.length() + "/" + test.maxLength);
            if (!lenOk)
                allPassed = false;
        }

        // LLM quality check
        if (test.qualityCriteria != null && !test.qualityCriteria.isEmpty()) {
            String judge = chat(
                    "Evaluate if this response meets this criterion: " + test.qualityCriteria
                            + ". Respond with exactly 'PASS' or 'FAIL' followed by a brief reason.",
                    "Response to evaluate: " + response);
            boolean qualityOk = judge.toUpperCase().startsWith("PASS");
            details.add((qualityOk ? "✅" : "❌") + " Quality: " + judge.substring(0, Math.min(60, judge.length())));
            if (!qualityOk)
                allPassed = false;
        }

        details.add("📝 Response preview: " + response.substring(0, Math.min(80, response.length())) + "...");
        return new TestResult(test.name, allPassed, details);
    }

    static void runTestSuite(String suiteName, List<TestCase> tests) throws Exception {
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  🧪 Test Suite: " + suiteName);
        System.out.println("  ═══════════════════════════════════════\n");

        int passed = 0, failed = 0;
        List<TestResult> results = new ArrayList<>();

        for (TestCase test : tests) {
            TestResult result = runTest(test);
            results.add(result);
            if (result.passed)
                passed++;
            else
                failed++;

            System.out.println("    " + (result.passed ? "✅ PASS" : "❌ FAIL") + ": " + result.name);
            for (String detail : result.details) {
                System.out.println("      " + detail);
            }
            System.out.println();
        }

        // Report
        System.out.println("  ──── REPORT ────");
        System.out.printf("  Total: %d │ Passed: %d │ Failed: %d │ Rate: %.0f%%%n",
                tests.size(), passed, failed, (passed * 100.0 / tests.size()));
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 7.2: Test Framework (Java)        ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        List<TestCase> tests = List.of(
                new TestCase("Code Quality Answer",
                        "You are a Java expert. Answer concisely.", "How do I use Optional correctly in Java?",
                        List.of("Optional", "orElse"), List.of(),
                        1500, "Response should mention avoiding .get() and explain why"),
                new TestCase("Security Awareness",
                        "You are a security-focused assistant.", "How should I store passwords in Java?",
                        List.of("hash", "bcrypt"), List.of("plain text", "Base64"),
                        1500, "Should recommend bcrypt/argon2 and warn against MD5/SHA"),
                new TestCase("Error Handling Guidance",
                        "You are a Java best practices expert.", "How to handle exceptions in Spring Boot?",
                        List.of("@ControllerAdvice"), List.of(),
                        2000, "Should mention global exception handling"),
                new TestCase("Concise Response",
                        "Answer in 1-2 sentences only. Be extremely brief.", "What is Spring Boot?",
                        List.of("Spring"), List.of(),
                        300, "Response should be genuinely brief, under 3 sentences"));

        runTestSuite("Java Knowledge Tests", tests);

        System.out.println("\n  ✅ Test Framework Pattern:");
        System.out.println("     Define test cases → Run → Evaluate → Report");
        System.out.println("     Combine deterministic + LLM-based assertions");
        System.out.println("     Like JUnit for LLM outputs!\n");
    }
}
