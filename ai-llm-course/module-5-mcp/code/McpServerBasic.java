
/**
 * MODULE 5 — Example 2: Basic MCP Server (Java Equivalent)
 * ===========================================================
 * Java equivalent of 02_mcp_server_basic.py
 *
 * NO API KEY NEEDED — runs as a local HTTP server
 *
 * Implements a basic MCP server using Java's built-in HttpServer:
 *   - Handles JSON-RPC requests
 *   - Exposes tools (initialize, tools/list, tools/call)
 *   - Calculator and string tools
 *
 * COMPILE & RUN:
 *   javac McpServerBasic.java && java McpServerBasic
 *   Then test: curl -X POST http://localhost:3000/mcp -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
 */

import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class McpServerBasic {

    // ═══════════════════════════════════════════════════
    // TOOL REGISTRY
    // ═══════════════════════════════════════════════════

    record ToolDef(String name, String description, String schemaJson) {
    }

    static final List<ToolDef> TOOLS = List.of(
            new ToolDef("add", "Add two numbers",
                    "{\"type\":\"object\",\"properties\":{\"a\":{\"type\":\"number\"},\"b\":{\"type\":\"number\"}},\"required\":[\"a\",\"b\"]}"),
            new ToolDef("multiply", "Multiply two numbers",
                    "{\"type\":\"object\",\"properties\":{\"a\":{\"type\":\"number\"},\"b\":{\"type\":\"number\"}},\"required\":[\"a\",\"b\"]}"),
            new ToolDef("uppercase", "Convert text to uppercase",
                    "{\"type\":\"object\",\"properties\":{\"text\":{\"type\":\"string\"}},\"required\":[\"text\"]}"),
            new ToolDef("word_count", "Count words in text",
                    "{\"type\":\"object\",\"properties\":{\"text\":{\"type\":\"string\"}},\"required\":[\"text\"]}"));

    // ═══════════════════════════════════════════════════
    // TOOL EXECUTION
    // ═══════════════════════════════════════════════════

    static String executeTool(String name, String argsJson) {
        return switch (name) {
            case "add" -> {
                double a = extractNum(argsJson, "a"), b = extractNum(argsJson, "b");
                yield "{\"result\":%.2f}".formatted(a + b);
            }
            case "multiply" -> {
                double a = extractNum(argsJson, "a"), b = extractNum(argsJson, "b");
                yield "{\"result\":%.2f}".formatted(a * b);
            }
            case "uppercase" -> {
                String text = extractStr(argsJson, "text");
                yield "{\"result\":\"%s\"}".formatted(text.toUpperCase());
            }
            case "word_count" -> {
                String text = extractStr(argsJson, "text");
                int count = text.trim().isEmpty() ? 0 : text.trim().split("\\s+").length;
                yield "{\"result\":%d}".formatted(count);
            }
            default -> "{\"error\":\"Unknown tool: " + name + "\"}";
        };
    }

    // ═══════════════════════════════════════════════════
    // JSON-RPC HANDLER
    // ═══════════════════════════════════════════════════

    static String handleRequest(String requestJson) {
        String method = extractStr(requestJson, "method");
        String idStr = extractNumStr(requestJson, "id");
        int id = idStr != null ? Integer.parseInt(idStr) : 0;

        return switch (method) {
            case "initialize" -> jsonRpcResponse(id,
                    "{\"protocolVersion\":\"2024-11-05\",\"serverInfo\":{\"name\":\"java-mcp-server\",\"version\":\"1.0\"},\"capabilities\":{\"tools\":{}}}");
            case "tools/list" -> {
                StringBuilder toolsList = new StringBuilder("[");
                for (int i = 0; i < TOOLS.size(); i++) {
                    if (i > 0)
                        toolsList.append(",");
                    ToolDef t = TOOLS.get(i);
                    toolsList.append("{\"name\":\"%s\",\"description\":\"%s\",\"inputSchema\":%s}"
                            .formatted(t.name, t.description, t.schemaJson));
                }
                toolsList.append("]");
                yield jsonRpcResponse(id, "{\"tools\":" + toolsList + "}");
            }
            case "tools/call" -> {
                // Extract params.name and params.arguments
                int paramsIdx = requestJson.indexOf("\"params\":");
                String params = paramsIdx >= 0 ? requestJson.substring(paramsIdx) : "";
                String toolName = extractStr(params, "name");
                int argsIdx = params.indexOf("\"arguments\":");
                String argsJson = argsIdx >= 0 ? extractObject(params, argsIdx + 12) : "{}";

                System.out.println("  🔧 Executing: " + toolName + "(" + argsJson + ")");
                String result = executeTool(toolName, argsJson);
                System.out.println("  ← " + result);
                yield jsonRpcResponse(id, "{\"content\":[{\"type\":\"text\",\"text\":" + quote(result) + "}]}");
            }
            default -> jsonRpcError(id, -32601, "Method not found: " + method);
        };
    }

    static String jsonRpcResponse(int id, String result) {
        return "{\"jsonrpc\":\"2.0\",\"id\":%d,\"result\":%s}".formatted(id, result);
    }

    static String jsonRpcError(int id, int code, String msg) {
        return "{\"jsonrpc\":\"2.0\",\"id\":%d,\"error\":{\"code\":%d,\"message\":\"%s\"}}".formatted(id, code, msg);
    }

    static String quote(String s) {
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }

    // ═══════════════════════════════════════════════════
    // HTTP SERVER
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws IOException {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 5.2: Basic MCP Server (Java)      ║");
        System.out.println("║  NO API KEY NEEDED                           ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        // If "--demo" flag, just simulate requests
        if (args.length > 0 && args[0].equals("--demo")) {
            runDemo();
            return;
        }

        int port = 3000;
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        server.createContext("/mcp", exchange -> {
            if ("POST".equals(exchange.getRequestMethod())) {
                String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
                System.out.println("  📨 Request: " + body.substring(0, Math.min(100, body.length())));

                String response = handleRequest(body);
                byte[] responseBytes = response.getBytes(StandardCharsets.UTF_8);

                exchange.getResponseHeaders().set("Content-Type", "application/json");
                exchange.sendResponseHeaders(200, responseBytes.length);
                exchange.getResponseBody().write(responseBytes);
            } else {
                exchange.sendResponseHeaders(405, -1);
            }
            exchange.close();
        });

        server.start();
        System.out.println("  🚀 MCP Server running on http://localhost:" + port + "/mcp");
        System.out.println("  📋 Available tools: " + TOOLS.stream().map(t -> t.name).toList());
        System.out.println("\n  Test with:");
        System.out.println("    curl -X POST http://localhost:" + port + "/mcp \\");
        System.out.println("      -H 'Content-Type: application/json' \\");
        System.out.println("      -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}'");
        System.out.println("\n  Press Ctrl+C to stop.\n");
    }

    static void runDemo() {
        System.out.println("  ── Demo mode: simulating MCP requests ──\n");

        String[] requests = {
                "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\"}",
                "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\"}",
                "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/call\",\"params\":{\"name\":\"add\",\"arguments\":{\"a\":42,\"b\":17}}}",
                "{\"jsonrpc\":\"2.0\",\"id\":4,\"method\":\"tools/call\",\"params\":{\"name\":\"uppercase\",\"arguments\":{\"text\":\"hello world\"}}}",
                "{\"jsonrpc\":\"2.0\",\"id\":5,\"method\":\"tools/call\",\"params\":{\"name\":\"word_count\",\"arguments\":{\"text\":\"Spring Boot makes Java fun\"}}}",
        };

        for (String req : requests) {
            System.out.println("  → " + req.substring(0, Math.min(80, req.length())) + "...");
            String resp = handleRequest(req);
            System.out.println("  ← " + resp);
            System.out.println();
        }
    }

    // ── JSON Helpers ──
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

    static double extractNum(String json, String key) {
        String m = "\"" + key + "\":";
        int i = json.indexOf(m);
        if (i == -1)
            return 0;
        i += m.length();
        while (i < json.length() && json.charAt(i) == ' ')
            i++;
        StringBuilder sb = new StringBuilder();
        while (i < json.length()
                && (Character.isDigit(json.charAt(i)) || json.charAt(i) == '.' || json.charAt(i) == '-')) {
            sb.append(json.charAt(i));
            i++;
        }
        return sb.length() > 0 ? Double.parseDouble(sb.toString()) : 0;
    }

    static String extractNumStr(String json, String key) {
        String m = "\"" + key + "\":";
        int i = json.indexOf(m);
        if (i == -1)
            return null;
        i += m.length();
        while (i < json.length() && json.charAt(i) == ' ')
            i++;
        StringBuilder sb = new StringBuilder();
        while (i < json.length() && Character.isDigit(json.charAt(i))) {
            sb.append(json.charAt(i));
            i++;
        }
        return sb.length() > 0 ? sb.toString() : null;
    }

    static String extractObject(String json, int start) {
        while (start < json.length() && json.charAt(start) != '{')
            start++;
        if (start >= json.length())
            return "{}";
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
}
