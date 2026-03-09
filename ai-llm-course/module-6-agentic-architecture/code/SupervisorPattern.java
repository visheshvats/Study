
/**
 * MODULE 6 — Example 3: Supervisor Pattern (Java Equivalent)
 * =============================================================
 * Java equivalent of 03_supervisor_pattern.py
 *
 * The Supervisor pattern:
 *   - Worker generates content
 *   - Supervisor reviews it and provides feedback
 *   - Worker revises based on feedback
 *   - Loop until supervisor is satisfied
 *
 * COMPILE & RUN:
 *   javac SupervisorPattern.java && java SupervisorPattern
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class SupervisorPattern {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();
    private static final int MAX_REVISIONS = 3;

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static String chat(String system, String user, double temp) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":%s,\"max_tokens\":600}"
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

    // Worker: generates/revises content
    static String workerGenerate(String task, String feedback) throws Exception {
        String prompt = feedback == null
                ? "Write content for: " + task
                : "Revise this based on feedback.\n\nFeedback:\n" + feedback + "\n\nOriginal task: " + task;

        return chat(
                "You are a technical writer specializing in Java/Spring Boot documentation. "
                        + "Write clear, concise, accurate content. Include code examples when relevant.",
                prompt, 0.7);
    }

    // Supervisor: reviews and evaluates
    static String supervisorReview(String content, String task) throws Exception {
        return chat(
                "You are a senior technical editor reviewing content for accuracy and quality. "
                        + "Evaluate: technical accuracy, completeness, clarity, code quality. "
                        + "If the content is EXCELLENT, start your response with 'APPROVED'. "
                        + "Otherwise, provide specific, actionable feedback for improvement.",
                "Task: " + task + "\n\nContent to review:\n" + content, 0.3);
    }

    static String supervisorLoop(String task) throws Exception {
        System.out.println("  🎯 Task: " + task + "\n");

        String content = null;
        String feedback = null;

        for (int i = 1; i <= MAX_REVISIONS; i++) {
            System.out.println("  ──── Iteration " + i + "/" + MAX_REVISIONS + " ────\n");

            // Worker generates/revises
            System.out.println("  👷 Worker " + (i == 1 ? "generating" : "revising") + "...");
            content = workerGenerate(task, feedback);
            System.out.println("    ✅ " + content.substring(0, Math.min(150, content.length())) + "...\n");

            // Supervisor reviews
            System.out.println("  👔 Supervisor reviewing...");
            String review = supervisorReview(content, task);
            System.out.println("    " + review.substring(0, Math.min(150, review.length())) + "...\n");

            if (review.toUpperCase().startsWith("APPROVED")) {
                System.out.println("  ✅ APPROVED on iteration " + i + "!\n");
                return content;
            }

            feedback = review;
            System.out.println("  📝 Feedback provided. Revising...\n");
        }

        System.out.println("  ⚠️ Max revisions reached. Using last version.\n");
        return content;
    }

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 6.3: Supervisor Pattern (Java)    ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        String result = supervisorLoop(
                "Write a concise guide on implementing the Circuit Breaker pattern "
                        + "in a Spring Boot microservice using Resilience4j. "
                        + "Include a code example with @CircuitBreaker annotation.");

        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  📋 FINAL CONTENT:\n");
        System.out.println("  " + result.replace("\n", "\n  "));

        System.out.println("\n  ✅ Supervisor Pattern: Generate → Review → Revise → ... → Approve");
        System.out.println("     Like: Code Review cycle — submit PR → feedback → fix → approve\n");
    }
}
