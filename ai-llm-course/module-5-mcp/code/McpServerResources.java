
/**
 * MODULE 5 — Example 3: MCP Server with Resources & Prompts (Java)
 * ===================================================================
 * Java equivalent of 03_mcp_server_resources.py
 *
 * Extends the basic server with all 3 MCP primitives:
 *   - Tools: Actions (deploy, rollback)
 *   - Resources: Read-only data (metrics, logs)
 *   - Prompts: Reusable prompt templates
 *
 * COMPILE & RUN:
 *   javac McpServerResources.java && java McpServerResources --demo
 */

import java.util.*;
import java.time.LocalDateTime;

public class McpServerResources {

    // ═══════════════════════════════════════════════════
    // TOOLS (Actions)
    // ═══════════════════════════════════════════════════
    record Tool(String name, String description) {
    }

    static final List<Tool> TOOLS = List.of(
            new Tool("deploy_service", "Deploy a service to an environment"),
            new Tool("rollback_service", "Rollback a service to previous version"),
            new Tool("scale_service", "Scale service replicas up or down"));

    static String callTool(String name, String args) {
        return switch (name) {
            case "deploy_service" ->
                "{\"status\":\"deployed\",\"version\":\"v2.1\",\"timestamp\":\"%s\"}".formatted(LocalDateTime.now());
            case "rollback_service" -> "{\"status\":\"rolled_back\",\"previous_version\":\"v2.0\",\"timestamp\":\"%s\"}"
                    .formatted(LocalDateTime.now());
            case "scale_service" ->
                "{\"status\":\"scaled\",\"replicas\":3,\"timestamp\":\"%s\"}".formatted(LocalDateTime.now());
            default -> "{\"error\":\"Unknown tool\"}";
        };
    }

    // ═══════════════════════════════════════════════════
    // RESOURCES (Read-only data)
    // ═══════════════════════════════════════════════════
    record Resource(String uri, String name, String mimeType) {
    }

    static final List<Resource> RESOURCES = List.of(
            new Resource("metrics://cpu", "CPU Metrics", "application/json"),
            new Resource("metrics://memory", "Memory Metrics", "application/json"),
            new Resource("logs://app/recent", "Recent App Logs", "text/plain"));

    static String readResource(String uri) {
        Random rng = new Random();
        return switch (uri) {
            case "metrics://cpu" -> "{\"cpu_percent\":%.1f,\"cores\":8,\"load_avg\":[%.2f,%.2f,%.2f]}"
                    .formatted(20 + rng.nextDouble() * 60, 1 + rng.nextDouble() * 3, 1 + rng.nextDouble() * 2,
                            rng.nextDouble() * 2);
            case "metrics://memory" -> "{\"used_gb\":%.1f,\"total_gb\":16,\"percent\":%.1f}"
                    .formatted(4 + rng.nextDouble() * 8, 30 + rng.nextDouble() * 50);
            case "logs://app/recent" ->
                "[INFO] Service started\\n[WARN] Connection pool 80% full\\n[INFO] Request latency p99: 250ms";
            default -> "{\"error\":\"Resource not found\"}";
        };
    }

    // ═══════════════════════════════════════════════════
    // PROMPTS (Templates)
    // ═══════════════════════════════════════════════════
    record PromptDef(String name, String description, String template) {
    }

    static final List<PromptDef> PROMPTS = List.of(
            new PromptDef("incident_response",
                    "Guide through incident response steps",
                    "An incident has been reported for service '%s' in %s environment. "
                            + "Current status: elevated error rates. Guide me through the incident response process."),
            new PromptDef("capacity_planning",
                    "Analyze capacity and recommend scaling",
                    "Analyze the current resource utilization for service '%s' and recommend "
                            + "capacity planning actions for the upcoming %s."));

    // ═══════════════════════════════════════════════════
    // JSON-RPC DISPATCHER
    // ═══════════════════════════════════════════════════

    static String handleRequest(String requestJson) {
        String method = extractStr(requestJson, "method");
        return switch (method) {
            case "initialize" -> resp(1,
                    "{\"protocolVersion\":\"2024-11-05\",\"serverInfo\":{\"name\":\"java-devops-mcp\"},\"capabilities\":{\"tools\":{},\"resources\":{},\"prompts\":{}}}");
            case "tools/list" -> {
                StringBuilder sb = new StringBuilder("[");
                for (int i = 0; i < TOOLS.size(); i++) {
                    if (i > 0)
                        sb.append(",");
                    sb.append("{\"name\":\"%s\",\"description\":\"%s\"}".formatted(TOOLS.get(i).name,
                            TOOLS.get(i).description));
                }
                yield resp(1, "{\"tools\":" + sb + "]}");
            }
            case "tools/call" -> {
                String name = extractNestedStr(requestJson, "name");
                String result = callTool(name, "{}");
                yield resp(1,
                        "{\"content\":[{\"type\":\"text\",\"text\":\"%s\"}]}".formatted(result.replace("\"", "\\\"")));
            }
            case "resources/list" -> {
                StringBuilder sb = new StringBuilder("[");
                for (int i = 0; i < RESOURCES.size(); i++) {
                    if (i > 0)
                        sb.append(",");
                    Resource r = RESOURCES.get(i);
                    sb.append("{\"uri\":\"%s\",\"name\":\"%s\",\"mimeType\":\"%s\"}".formatted(r.uri, r.name,
                            r.mimeType));
                }
                yield resp(1, "{\"resources\":" + sb + "]}");
            }
            case "resources/read" -> {
                String uri = extractNestedStr(requestJson, "uri");
                String content = readResource(uri);
                yield resp(1, "{\"contents\":[{\"uri\":\"%s\",\"text\":\"%s\"}]}".formatted(uri,
                        content.replace("\"", "\\\"")));
            }
            case "prompts/list" -> {
                StringBuilder sb = new StringBuilder("[");
                for (int i = 0; i < PROMPTS.size(); i++) {
                    if (i > 0)
                        sb.append(",");
                    sb.append("{\"name\":\"%s\",\"description\":\"%s\"}".formatted(PROMPTS.get(i).name,
                            PROMPTS.get(i).description));
                }
                yield resp(1, "{\"prompts\":" + sb + "]}");
            }
            default ->
                "{\"jsonrpc\":\"2.0\",\"id\":1,\"error\":{\"code\":-32601,\"message\":\"Unknown: " + method + "\"}}";
        };
    }

    static String resp(int id, String result) {
        return "{\"jsonrpc\":\"2.0\",\"id\":%d,\"result\":%s}".formatted(id, result);
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 5.3: MCP Server + Resources       ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        String[] requests = {
                "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\"}",
                "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\"}",
                "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"resources/list\"}",
                "{\"jsonrpc\":\"2.0\",\"id\":4,\"method\":\"prompts/list\"}",
                "{\"jsonrpc\":\"2.0\",\"id\":5,\"method\":\"resources/read\",\"params\":{\"uri\":\"metrics://cpu\"}}",
                "{\"jsonrpc\":\"2.0\",\"id\":6,\"method\":\"resources/read\",\"params\":{\"uri\":\"logs://app/recent\"}}",
                "{\"jsonrpc\":\"2.0\",\"id\":7,\"method\":\"tools/call\",\"params\":{\"name\":\"deploy_service\"}}",
        };

        for (String req : requests) {
            String method = extractStr(req, "method");
            System.out.println("  → " + method);
            String response = handleRequest(req);
            System.out.println("  ← " + response.substring(0, Math.min(120, response.length())) + "...\n");
        }

        System.out.println("  ✅ MCP Server Capabilities:");
        System.out.println("     • Tools: deploy, rollback, scale");
        System.out.println("     • Resources: CPU, memory, logs");
        System.out.println("     • Prompts: incident response, capacity planning\n");
    }

    static String extractStr(String json, String key) {
        String m = "\"" + key + "\":";
        int i = json.indexOf(m);
        if (i == -1)
            return "";
        i += m.length();
        while (i < json.length() && json.charAt(i) == ' ')
            i++;
        if (i >= json.length() || json.charAt(i) != '"')
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

    static String extractNestedStr(String json, String key) {
        // Look for key after "params"
        int pi = json.indexOf("\"params\":");
        if (pi == -1)
            return extractStr(json, key);
        return extractStr(json.substring(pi), key);
    }
}
