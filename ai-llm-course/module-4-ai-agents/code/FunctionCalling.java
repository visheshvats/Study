
/**
 * MODULE 4 — Example 1: Function Calling (Java Equivalent)
 * ===========================================================
 * Java equivalent of 01_function_calling.py
 *
 * Demonstrates OpenAI function/tool calling:
 *   1. Define tools as JSON schemas
 *   2. LLM decides when and how to call tools
 *   3. Execute tools and return results to LLM
 *
 * JAVA ANALOGY:
 *   - Tool definitions = @Operation annotations in OpenAPI/Swagger
 *   - Tool execution = calling a @Service method via reflection/dispatcher
 *   - The LLM acts like a controller routing to the right handler
 *
 * COMPILE & RUN:
 *   javac FunctionCalling.java && java FunctionCalling
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.LocalDateTime;
import java.util.*;

public class FunctionCalling {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    // ═══════════════════════════════════════════════════
    // TOOL DEFINITIONS (like @Operation in OpenAPI)
    // ═══════════════════════════════════════════════════

    static final String TOOLS_JSON = """
            [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get current weather for a city",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name"},
                                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature unit"}
                            },
                            "required": ["city"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "calculate",
                        "description": "Perform a mathematical calculation",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "expression": {"type": "string", "description": "Math expression to evaluate, e.g. '2 + 3 * 4'"}
                            },
                            "required": ["expression"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_current_time",
                        "description": "Get the current date and time",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "timezone": {"type": "string", "description": "Timezone like UTC, EST, IST"}
                            }
                        }
                    }
                }
            ]
            """;

    // ═══════════════════════════════════════════════════
    // TOOL IMPLEMENTATIONS (like @Service methods)
    // ═══════════════════════════════════════════════════

    static String executeTool(String toolName, String argsJson) {
        return switch (toolName) {
            case "get_weather" -> {
                String city = extractJsonString(argsJson, "city");
                String unit = extractJsonString(argsJson, "unit");
                if (unit == null)
                    unit = "celsius";
                // Simulated weather data
                Random rng = new Random(city.hashCode());
                int temp = unit.equals("celsius") ? 15 + rng.nextInt(20) : 59 + rng.nextInt(36);
                String[] conditions = { "Sunny", "Cloudy", "Rainy", "Partly Cloudy" };
                yield "{\"city\":\"%s\",\"temperature\":%d,\"unit\":\"%s\",\"condition\":\"%s\",\"humidity\":%d}"
                        .formatted(city, temp, unit, conditions[rng.nextInt(4)], 40 + rng.nextInt(40));
            }
            case "calculate" -> {
                String expr = extractJsonString(argsJson, "expression");
                try {
                    double result = evalSimple(expr);
                    yield "{\"expression\":\"%s\",\"result\":%.2f}".formatted(expr, result);
                } catch (Exception e) {
                    yield "{\"error\":\"Cannot evaluate: %s\"}".formatted(expr);
                }
            }
            case "get_current_time" -> {
                yield "{\"datetime\":\"%s\"}".formatted(LocalDateTime.now().toString());
            }
            default -> "{\"error\":\"Unknown tool: " + toolName + "\"}";
        };
    }

    /** Simple math expression evaluator. */
    static double evalSimple(String expr) {
        expr = expr.replaceAll("\\s+", "");
        // Handle basic operations
        if (expr.contains("+")) {
            String[] parts = expr.split("\\+", 2);
            return evalSimple(parts[0]) + evalSimple(parts[1]);
        }
        if (expr.contains("-") && expr.lastIndexOf('-') > 0) {
            int idx = expr.lastIndexOf('-');
            return evalSimple(expr.substring(0, idx)) - evalSimple(expr.substring(idx + 1));
        }
        if (expr.contains("*")) {
            String[] parts = expr.split("\\*", 2);
            return evalSimple(parts[0]) * evalSimple(parts[1]);
        }
        if (expr.contains("/")) {
            String[] parts = expr.split("/", 2);
            return evalSimple(parts[0]) / evalSimple(parts[1]);
        }
        return Double.parseDouble(expr);
    }

    static String extractJsonString(String json, String key) {
        String marker = "\"" + key + "\":";
        int idx = json.indexOf(marker);
        if (idx == -1)
            return null;
        idx += marker.length();
        while (idx < json.length() && json.charAt(idx) == ' ')
            idx++;
        if (json.charAt(idx) == '"') {
            idx++;
            StringBuilder sb = new StringBuilder();
            while (idx < json.length() && json.charAt(idx) != '"') {
                if (json.charAt(idx) == '\\')
                    idx++;
                sb.append(json.charAt(idx++));
            }
            return sb.toString();
        }
        return null;
    }

    // ═══════════════════════════════════════════════════
    // FUNCTION CALLING FLOW
    // ═══════════════════════════════════════════════════

    static String callWithTools(String userMessage) throws Exception {
        System.out.println("  👤 User: " + userMessage + "\n");

        // Step 1: Send message with tool definitions
        String body = """
                {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant. Use tools when needed."},
                        {"role": "user", "content": "%s"}
                    ],
                    "tools": %s,
                    "tool_choice": "auto"
                }
                """.formatted(esc(userMessage), TOOLS_JSON);

        var req = HttpRequest.newBuilder().uri(URI.create(API_URL))
                .header("Content-Type", "application/json").header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        var resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
        String json = resp.body();

        // Check if LLM wants to call tools
        if (json.contains("\"tool_calls\"")) {
            System.out.println("  🔧 LLM decided to call tool(s):");

            // Parse tool calls (simplified)
            List<String[]> toolCalls = parseToolCalls(json);
            StringBuilder toolMessages = new StringBuilder();

            for (String[] tc : toolCalls) {
                String callId = tc[0], funcName = tc[1], funcArgs = tc[2];
                System.out.println("    → " + funcName + "(" + funcArgs + ")");

                String result = executeTool(funcName, funcArgs);
                System.out.println("    ← " + result);

                toolMessages.append("""
                        ,{"role": "tool", "tool_call_id": "%s", "content": "%s"}""".formatted(callId, esc(result)));
            }

            // Step 2: Send tool results back to LLM
            // Reconstruct the assistant message with tool_calls
            String assistantMsg = extractAssistantToolMessage(json);
            String body2 = """
                    {
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": "%s"},
                            %s%s
                        ]
                    }
                    """.formatted(esc(userMessage), assistantMsg, toolMessages.toString());

            var req2 = HttpRequest.newBuilder().uri(URI.create(API_URL))
                    .header("Content-Type", "application/json").header("Authorization", "Bearer " + API_KEY)
                    .POST(HttpRequest.BodyPublishers.ofString(body2)).build();
            var resp2 = httpClient.send(req2, HttpResponse.BodyHandlers.ofString());
            return extractContent(resp2.body());
        } else {
            // No tool call needed — direct response
            return extractContent(json);
        }
    }

    static List<String[]> parseToolCalls(String json) {
        List<String[]> calls = new ArrayList<>();
        int searchFrom = 0;
        while (true) {
            int tcIdx = json.indexOf("\"id\":", searchFrom);
            if (tcIdx == -1 || tcIdx > json.indexOf("\"usage\"", searchFrom > 0 ? searchFrom : 0))
                break;
            String id = extractAfter(json, "\"id\":", tcIdx);
            int fnIdx = json.indexOf("\"name\":", tcIdx);
            String name = extractAfter(json, "\"name\":", fnIdx);
            int argIdx = json.indexOf("\"arguments\":", tcIdx);
            String args = extractAfter(json, "\"arguments\":", argIdx);
            if (id != null && name != null && args != null) {
                // Unescape the arguments string
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

    static String extractAssistantToolMessage(String json) {
        // Extract the full assistant message object containing tool_calls
        int choicesIdx = json.indexOf("\"choices\":");
        int msgIdx = json.indexOf("\"message\":", choicesIdx);
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

    static String extractContent(String json) {
        String m = "\"content\":";
        int idx = json.indexOf(m);
        if (idx == -1)
            return "[No content]";
        idx += m.length();
        while (idx < json.length() && (json.charAt(idx) == ' ' || json.charAt(idx) == '\n'))
            idx++;
        if (json.charAt(idx) != '"')
            return "[Null content]";
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
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 4.1: Function Calling (Java)      ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        String[] queries = {
                "What's the weather in Tokyo?",
                "What is 42 * 17 + 5?",
                "What time is it right now?",
                "What's the weather in London and calculate 100 / 3?",
        };

        for (String q : queries) {
            System.out.println("  ═══════════════════════════════════════");
            String result = callWithTools(q);
            System.out.println("\n  🤖 Final: " + result + "\n");
        }

        System.out.println("  ✅ Function Calling Pattern:");
        System.out.println("     1. Define tools as JSON schemas (like OpenAPI)");
        System.out.println("     2. LLM decides which tools to call");
        System.out.println("     3. Execute tools, return results to LLM");
        System.out.println("     4. LLM generates final response using tool outputs\n");
    }
}
