
/**
 * MODULE 4 — Example 2: Agent Loop (Java Equivalent)
 * =====================================================
 * Java equivalent of 02_agent_loop.py
 *
 * Implements the ReAct (Reason + Act) agent loop:
 *   1. LLM reasons about the task
 *   2. LLM decides which tool to call
 *   3. Tool executes and returns result
 *   4. LLM reasons again with new info
 *   5. Repeat until task complete
 *
 * COMPILE & RUN:
 *   javac AgentLoop.java && java AgentLoop
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.LocalDateTime;
import java.util.*;

public class AgentLoop {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();
    private static final int MAX_ITERATIONS = 5;

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    // ── Tool definitions ──
    static final String TOOLS_JSON = """
            [
                {"type":"function","function":{"name":"search_docs","description":"Search internal documentation for Java/Spring topics","parameters":{"type":"object","properties":{"query":{"type":"string","description":"Search query"}},"required":["query"]}}},
                {"type":"function","function":{"name":"run_code_check","description":"Check if a code snippet has syntax errors or common issues","parameters":{"type":"object","properties":{"code":{"type":"string","description":"Java code to check"}},"required":["code"]}}},
                {"type":"function","function":{"name":"get_dependency_info","description":"Get information about a Maven/Gradle dependency","parameters":{"type":"object","properties":{"artifact":{"type":"string","description":"Maven artifact ID like spring-boot-starter-web"}},"required":["artifact"]}}}
            ]
            """;

    // ── Tool implementations ──
    static String executeTool(String name, String args) {
        return switch (name) {
            case "search_docs" -> {
                String query = extractJsonStr(args, "query");
                // Simulated doc search
                Map<String, String> docs = Map.of(
                        "virtual threads",
                        "Java 21 virtual threads: Use Thread.ofVirtual().start(). Enable in Spring Boot with spring.threads.virtual.enabled=true. Best for I/O-bound tasks.",
                        "connection pool",
                        "HikariCP sizing: connections = (CPU cores * 2) + spindle_count. Default max=10. Monitor with /actuator/metrics.",
                        "caching",
                        "Spring Cache: Add @EnableCaching. Use @Cacheable on methods. Supports Redis, Caffeine, EhCache providers.",
                        "security",
                        "Spring Security 6: Use SecurityFilterChain bean. JWT requires custom OncePerRequestFilter. @PreAuthorize for method security.",
                        "testing",
                        "Spring Boot Test: @SpringBootTest for integration, @WebMvcTest for controller, @DataJpaTest for repository testing.");
                String result = docs.entrySet().stream()
                        .filter(e -> query.toLowerCase().contains(e.getKey())
                                || e.getKey().contains(query.toLowerCase().split(" ")[0]))
                        .map(e -> e.getValue()).findFirst()
                        .orElse("No specific docs found for: " + query
                                + ". General tip: Check official Spring docs at spring.io/docs.");
                yield "{\"results\":[\"%s\"]}".formatted(esc(result));
            }
            case "run_code_check" -> {
                String code = extractJsonStr(args, "code");
                List<String> issues = new ArrayList<>();
                if (code.contains(".get()") && !code.contains("isPresent"))
                    issues.add("NoSuchElementException risk: Use .orElse() or .orElseThrow() instead of .get()");
                if (code.contains("new ArrayList<>()") && !code.contains("final"))
                    issues.add("Consider making list references 'final' for immutability");
                if (code.contains("@Autowired") && !code.contains("constructor"))
                    issues.add("Prefer constructor injection over @Autowired field injection");
                yield "{\"issues\":%s,\"count\":%d}".formatted(
                        issues.isEmpty() ? "[]" : "[\"" + String.join("\",\"", issues) + "\"]", issues.size());
            }
            case "get_dependency_info" -> {
                String artifact = extractJsonStr(args, "artifact");
                yield "{\"artifact\":\"%s\",\"latest_version\":\"3.2.5\",\"status\":\"stable\",\"license\":\"Apache-2.0\"}"
                        .formatted(artifact);
            }
            default -> "{\"error\":\"Unknown tool\"}";
        };
    }

    static String extractJsonStr(String json, String key) {
        String m = "\"" + key + "\":";
        int i = json.indexOf(m);
        if (i == -1)
            return "";
        i += m.length();
        while (i < json.length() && json.charAt(i) == ' ')
            i++;
        if (json.charAt(i) != '"')
            return "";
        i++;
        StringBuilder sb = new StringBuilder();
        while (i < json.length() && json.charAt(i) != '"') {
            if (json.charAt(i) == '\\') {
                i++;
                if (i < json.length()) {
                    sb.append(json.charAt(i));
                    i++;
                    continue;
                }
            }
            sb.append(json.charAt(i));
            i++;
        }
        return sb.toString();
    }

    // ═══════════════════════════════════════════════════
    // AGENT LOOP
    // ═══════════════════════════════════════════════════

    static String runAgent(String task) throws Exception {
        System.out.println("  🚀 Agent starting: \"" + task + "\"\n");

        List<String> messages = new ArrayList<>();
        messages.add("{\"role\":\"system\",\"content\":\"%s\"}".formatted(esc(
                "You are a helpful Java development assistant. Use tools to research, check code, "
                        + "and gather information. Call tools as needed, then provide a comprehensive final answer.")));
        messages.add("{\"role\":\"user\",\"content\":\"%s\"}".formatted(esc(task)));

        for (int iteration = 1; iteration <= MAX_ITERATIONS; iteration++) {
            System.out.println("  ──── Iteration " + iteration + "/" + MAX_ITERATIONS + " ────");

            String body = "{\"model\":\"gpt-4o-mini\",\"messages\":[%s],\"tools\":%s,\"tool_choice\":\"auto\"}"
                    .formatted(String.join(",", messages), TOOLS_JSON);

            var req = HttpRequest.newBuilder().uri(URI.create(API_URL))
                    .header("Content-Type", "application/json").header("Authorization", "Bearer " + API_KEY)
                    .POST(HttpRequest.BodyPublishers.ofString(body)).build();
            var resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
            String json = resp.body();

            if (json.contains("\"tool_calls\"")) {
                // Extract and execute tool calls
                String assistantMsg = extractAssistantMessage(json);
                messages.add(assistantMsg);

                List<String[]> calls = parseToolCalls(json);
                for (String[] tc : calls) {
                    System.out.println(
                            "    🔧 " + tc[1] + "(" + tc[2].substring(0, Math.min(50, tc[2].length())) + "...)");
                    String result = executeTool(tc[1], tc[2]);
                    System.out.println("    ← " + result.substring(0, Math.min(80, result.length())) + "...");
                    messages.add("{\"role\":\"tool\",\"tool_call_id\":\"%s\",\"content\":\"%s\"}".formatted(tc[0],
                            esc(result)));
                }
            } else {
                // No tool calls → final answer
                String content = extractContent(json);
                System.out.println("    ✅ Agent finished (no more tools needed)\n");
                return content;
            }
        }
        return "Agent reached max iterations.";
    }

    static String extractAssistantMessage(String json) {
        int msgIdx = json.indexOf("\"message\":");
        int start = json.indexOf("{", msgIdx + 10);
        int depth = 1, pos = start + 1;
        while (pos < json.length() && depth > 0) {
            if (json.charAt(pos) == '{')
                depth++;
            if (json.charAt(pos) == '}')
                depth--;
            pos++;
        }
        return json.substring(start, pos);
    }

    static List<String[]> parseToolCalls(String json) {
        List<String[]> calls = new ArrayList<>();
        int searchFrom = 0;
        while (true) {
            int tcIdx = json.indexOf("\"id\":", searchFrom);
            if (tcIdx == -1 || (json.indexOf("\"usage\"") > 0 && tcIdx > json.indexOf("\"usage\"")))
                break;
            String id = extractAfter(json, "\"id\":", tcIdx);
            int fnIdx = json.indexOf("\"name\":", tcIdx);
            String name = extractAfter(json, "\"name\":", fnIdx);
            int argIdx = json.indexOf("\"arguments\":", tcIdx);
            String args = extractAfter(json, "\"arguments\":", argIdx);
            if (id != null && name != null && args != null) {
                args = args.replace("\\\"", "\"").replace("\\n", "\n");
                calls.add(new String[] { id, name, args });
            }
            searchFrom = argIdx + 1;
        }
        return calls;
    }

    static String extractAfter(String json, String marker, int start) {
        int idx = start + marker.length();
        while (idx < json.length() && (json.charAt(idx) == ' ' || json.charAt(idx) == '\n'))
            idx++;
        if (idx >= json.length() || json.charAt(idx) != '"')
            return null;
        idx++;
        StringBuilder sb = new StringBuilder();
        while (idx < json.length()) {
            char c = json.charAt(idx);
            if (c == '\\' && idx + 1 < json.length()) {
                sb.append(json.charAt(idx + 1));
                idx += 2;
                continue;
            }
            if (c == '"')
                break;
            sb.append(c);
            idx++;
        }
        return sb.toString();
    }

    static String extractContent(String json) {
        String m = "\"content\":";
        int idx = json.indexOf(m);
        if (idx == -1)
            return "[No content]";
        idx += m.length();
        while (idx < json.length() && (json.charAt(idx) == ' ' || json.charAt(idx) == '\n'))
            idx++;
        if (json.charAt(idx) != '"')
            return "[Null]";
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

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 4.2: Agent Loop (Java)            ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        String[] tasks = {
                "How should I configure connection pooling in my Spring Boot app?",
                "Review this code: userRepo.findById(id).get() — is it safe?",
        };

        for (String task : tasks) {
            System.out.println("  ═══════════════════════════════════════");
            String result = runAgent(task);
            System.out.println("  🤖 Answer: " + result.substring(0, Math.min(300, result.length())) + "...\n");
        }

        System.out.println("  ✅ Agent Loop Pattern (ReAct):");
        System.out.println("     Observe → Think → Act → Observe → ... → Answer\n");
    }
}
