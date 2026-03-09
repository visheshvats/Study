
/**
 * MODULE 5 — Example 1: MCP Concepts (Java Equivalent)
 * =======================================================
 * Java equivalent of 01_mcp_concepts.py
 *
 * NO API KEY NEEDED — demonstrates concepts with local code
 *
 * Model Context Protocol (MCP) is a standard for connecting AI assistants to tools.
 * Demonstrates:
 *   1. MCP architecture (Hosts, Clients, Servers)
 *   2. The three primitives (Tools, Resources, Prompts)
 *   3. JSON-RPC message format
 *   4. Transport mechanisms
 *
 * COMPILE & RUN:
 *   javac McpConcepts.java && java McpConcepts
 */

import java.util.*;

public class McpConcepts {

    // ═══════════════════════════════════════════════════
    // MCP PRIMITIVES (Data Models)
    // ═══════════════════════════════════════════════════

    /** Tool: An action the AI can execute (like a REST endpoint). */
    record Tool(String name, String description, Map<String, Object> inputSchema) {
        String toJson() {
            return """
                    {"name": "%s", "description": "%s", "inputSchema": %s}""".formatted(name, description,
                    mapToJson(inputSchema));
        }
    }

    /** Resource: Data the AI can read (like a GET endpoint). */
    record Resource(String uri, String name, String mimeType, String description) {
        String toJson() {
            return """
                    {"uri": "%s", "name": "%s", "mimeType": "%s", "description": "%s"}""".formatted(uri, name, mimeType,
                    description);
        }
    }

    /** Prompt: A reusable prompt template (like a view template). */
    record Prompt(String name, String description, List<PromptArgument> arguments) {
    }

    record PromptArgument(String name, String description, boolean required) {
    }

    static String mapToJson(Map<String, Object> map) {
        StringBuilder sb = new StringBuilder("{");
        int i = 0;
        for (var e : map.entrySet()) {
            if (i++ > 0)
                sb.append(",");
            sb.append("\"").append(e.getKey()).append("\":");
            if (e.getValue() instanceof String s)
                sb.append("\"").append(s).append("\"");
            else if (e.getValue() instanceof Map m)
                sb.append(mapToJson(m));
            else
                sb.append(e.getValue());
        }
        return sb.append("}").toString();
    }

    // ═══════════════════════════════════════════════════
    // JSON-RPC MESSAGE FORMAT
    // ═══════════════════════════════════════════════════

    record JsonRpcRequest(String jsonrpc, int id, String method, Map<String, Object> params) {
        String toJson() {
            String p = params != null ? mapToJson(params) : "{}";
            return "{\"jsonrpc\":\"%s\",\"id\":%d,\"method\":\"%s\",\"params\":%s}".formatted(jsonrpc, id, method, p);
        }
    }

    record JsonRpcResponse(String jsonrpc, int id, Object result) {
        String toJson() {
            return "{\"jsonrpc\":\"%s\",\"id\":%d,\"result\":%s}".formatted(jsonrpc, id, result);
        }
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 5.1: MCP Concepts (Java)          ║");
        System.out.println("║  NO API KEY NEEDED — concept demo            ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        // ── Architecture Overview ──
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  MCP ARCHITECTURE");
        System.out.println("  ═══════════════════════════════════════\n");
        System.out.println("  ┌──────────┐    ┌────────────┐    ┌────────────┐");
        System.out.println("  │   HOST   │───▶│   CLIENT   │───▶│   SERVER   │");
        System.out.println("  │ (Claude) │    │ (Connector)│    │ (Your App) │");
        System.out.println("  └──────────┘    └────────────┘    └────────────┘");
        System.out.println("                                    Exposes:");
        System.out.println("                                    • Tools");
        System.out.println("                                    • Resources");
        System.out.println("                                    • Prompts\n");

        // ── The Three Primitives ──
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  THE THREE PRIMITIVES");
        System.out.println("  ═══════════════════════════════════════\n");

        // Tools
        Tool tool = new Tool("deploy_service",
                "Deploy a microservice to Kubernetes",
                Map.of("type", "object",
                        "properties", Map.of(
                                "service_name", Map.of("type", "string"),
                                "version", Map.of("type", "string"),
                                "environment", Map.of("type", "string"))));
        System.out.println("  1️⃣ TOOL (action — like POST/PUT endpoint):");
        System.out.println("     " + tool.toJson());
        System.out.println("     Java equiv: @PostMapping method in a @RestController\n");

        // Resources
        Resource resource = new Resource(
                "metrics://cpu/service-a",
                "CPU Metrics for Service A",
                "application/json",
                "Real-time CPU utilization percentage");
        System.out.println("  2️⃣ RESOURCE (data — like GET endpoint):");
        System.out.println("     " + resource.toJson());
        System.out.println("     Java equiv: @GetMapping that returns read-only data\n");

        // Prompts
        Prompt prompt = new Prompt("code_review",
                "Review Java code for best practices",
                List.of(
                        new PromptArgument("code", "Java code to review", true),
                        new PromptArgument("focus", "Focus area (security, performance, style)", false)));
        System.out.println("  3️⃣ PROMPT (template — like a Thymeleaf template):");
        System.out.printf("     {name: %s, args: %s}%n", prompt.name, prompt.arguments);
        System.out.println("     Java equiv: Predefined prompt template with placeholders\n");

        // ── JSON-RPC Messages ──
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  JSON-RPC MESSAGE FORMAT");
        System.out.println("  ═══════════════════════════════════════\n");

        var listToolsReq = new JsonRpcRequest("2.0", 1, "tools/list", Map.of());
        System.out.println("  Request (tools/list):");
        System.out.println("    " + listToolsReq.toJson());

        var callToolReq = new JsonRpcRequest("2.0", 2, "tools/call",
                Map.of("name", "deploy_service", "arguments",
                        Map.of("service_name", "user-api", "version", "2.1.0", "environment", "staging")));
        System.out.println("\n  Request (tools/call):");
        System.out.println("    " + callToolReq.toJson());

        var response = new JsonRpcResponse("2.0", 2, "{\"success\":true,\"deployment_id\":\"dep-abc123\"}");
        System.out.println("\n  Response:");
        System.out.println("    " + response.toJson());

        // ── Transport Mechanisms ──
        System.out.println("\n  ═══════════════════════════════════════");
        System.out.println("  TRANSPORT MECHANISMS");
        System.out.println("  ═══════════════════════════════════════\n");
        System.out.println("  1. STDIO: stdin/stdout (local processes)");
        System.out.println("     → Like piping commands: java Server | java Client");
        System.out.println("  2. SSE: Server-Sent Events over HTTP");
        System.out.println("     → Like Spring WebFlux SSE endpoints");
        System.out.println("  3. Streamable HTTP (new): Flexible HTTP transport");
        System.out.println("     → Like Spring MVC with streaming responses\n");

        System.out.println("  ✅ Key Takeaways:");
        System.out.println("     • MCP = standard protocol (like REST, but for AI)");
        System.out.println("     • 3 primitives: Tools (actions), Resources (data), Prompts (templates)");
        System.out.println("     • Communication: JSON-RPC 2.0 over stdio/SSE/HTTP");
        System.out.println("     • Think of it as: OpenAPI/Swagger for AI assistants\n");
    }
}
