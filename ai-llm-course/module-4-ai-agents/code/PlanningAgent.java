
/**
 * MODULE 4 — Example 3: Planning Agent (Java Equivalent)
 * =========================================================
 * Java equivalent of 03_planning_agent.py
 *
 * A planning agent that:
 *   1. Creates a step-by-step plan before acting
 *   2. Executes each step sequentially
 *   3. Adapts the plan based on results
 *
 * COMPILE & RUN:
 *   javac PlanningAgent.java && java PlanningAgent
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;

public class PlanningAgent {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static String chat(String system, String user) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":0.3,\"max_tokens\":600}"
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
    // PLANNING AGENT
    // ═══════════════════════════════════════════════════

    static void runPlanningAgent(String goal) throws Exception {
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  🎯 Goal: " + goal);
        System.out.println("  ═══════════════════════════════════════\n");

        // Step 1: Create a plan
        System.out.println("  📋 STEP 1: Creating plan...\n");
        String plan = chat(
                "You are a planning agent. Create a step-by-step plan to achieve the goal. "
                        + "Return ONLY a numbered list of 3-5 concrete, actionable steps. No explanation.",
                "Goal: " + goal);
        System.out.println("  Plan:\n  " + plan.replace("\n", "\n  ") + "\n");

        // Step 2: Execute each step
        String[] steps = plan.split("\\n");
        StringBuilder progress = new StringBuilder();

        for (int i = 0; i < steps.length; i++) {
            String step = steps[i].trim();
            if (step.isEmpty())
                continue;

            System.out.println("  ▶ Executing: " + step);

            String result = chat(
                    "You are an expert Java/Spring developer executing a plan step. "
                            + "Previous progress:\n" + (progress.length() == 0 ? "None" : progress.toString()),
                    "Execute this step and provide the concrete output/code/advice:\n" + step);

            String preview = result.length() > 200 ? result.substring(0, 200) + "..." : result;
            System.out.println("    Result: " + preview + "\n");

            progress.append("Step: ").append(step).append("\nResult: ").append(result).append("\n\n");
        }

        // Step 3: Synthesize final result
        System.out.println("  📊 STEP 3: Synthesizing final answer...\n");
        String synthesis = chat(
                "Synthesize the results of all executed plan steps into a concise, "
                        + "actionable final answer. Include any code examples.",
                "Goal: " + goal + "\n\nExecution results:\n" + progress);

        System.out.println("  🤖 Final Answer:\n  " + synthesis.replace("\n", "\n  ") + "\n");
    }

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 4.3: Planning Agent (Java)        ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        runPlanningAgent("Create a REST API endpoint in Spring Boot that accepts a CSV file upload, "
                + "parses it, validates the data, and stores it in a PostgreSQL database");

        System.out.println("  ✅ Planning Agent Pattern:");
        System.out.println("     1. PLAN: Break goal into steps");
        System.out.println("     2. EXECUTE: Run each step with context");
        System.out.println("     3. SYNTHESIZE: Combine results\n");
    }
}
