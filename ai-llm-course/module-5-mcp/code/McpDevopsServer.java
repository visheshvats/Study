
/**
 * MODULE 5 — PROJECT: DevOps MCP Server (Java Equivalent)
 * ==========================================================
 * Java equivalent of 04_mcp_devops_server.py
 *
 * A comprehensive DevOps MCP server with:
 *   - Service management tools (deploy, health check, logs)
 *   - Infrastructure resources (metrics, alerts)
 *   - Operational prompts (runbook, post-mortem)
 *
 * COMPILE & RUN:
 *   javac McpDevopsServer.java && java McpDevopsServer
 */

import java.util.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class McpDevopsServer {

    // Simulated infrastructure state
    static final Map<String, Map<String, String>> SERVICES = new LinkedHashMap<>() {
        {
            put("user-api", Map.of("version", "2.1.0", "status", "running", "replicas", "3", "env", "production"));
            put("order-api", Map.of("version", "1.8.2", "status", "running", "replicas", "5", "env", "production"));
            put("auth-service", Map.of("version", "3.0.1", "status", "degraded", "replicas", "2", "env", "production"));
            put("notification-svc", Map.of("version", "1.2.0", "status", "running", "replicas", "2", "env", "staging"));
        }
    };

    static String handleMethod(String method, String params) {
        return switch (method) {
            case "tools/list" -> """
                    {"tools":[
                      {"name":"health_check","description":"Check service health"},
                      {"name":"get_logs","description":"Get recent service logs"},
                      {"name":"deploy","description":"Deploy a service version"},
                      {"name":"scale","description":"Scale service replicas"},
                      {"name":"create_alert","description":"Create a monitoring alert"}
                    ]}""";
            case "tools/call" -> executeDevOpsTool(params);
            case "resources/list" -> """
                    {"resources":[
                      {"uri":"infra://services","name":"All Services"},
                      {"uri":"infra://alerts","name":"Active Alerts"},
                      {"uri":"infra://metrics/overview","name":"System Metrics"}
                    ]}""";
            case "resources/read" -> readDevOpsResource(params);
            case "prompts/list" -> """
                    {"prompts":[
                      {"name":"incident_runbook","description":"Step-by-step incident response"},
                      {"name":"post_mortem","description":"Post-mortem report template"},
                      {"name":"deploy_checklist","description":"Pre-deployment checklist"}
                    ]}""";
            default -> "{\"error\":\"Unknown method\"}";
        };
    }

    static String executeDevOpsTool(String params) {
        String name = extractStr(params, "name");
        Random rng = new Random();
        return switch (name) {
            case "health_check" -> {
                StringBuilder sb = new StringBuilder("[");
                int i = 0;
                for (var e : SERVICES.entrySet()) {
                    if (i++ > 0)
                        sb.append(",");
                    int latency = 10 + rng.nextInt(200);
                    sb.append("{\"service\":\"%s\",\"status\":\"%s\",\"latency_ms\":%d,\"replicas\":%s}"
                            .formatted(e.getKey(), e.getValue().get("status"), latency, e.getValue().get("replicas")));
                }
                yield "{\"content\":[{\"type\":\"text\",\"text\":\"Health check results: " + sb + "]\"}]}";
            }
            case "get_logs" -> {
                String[] logs = {
                        "[INFO] Request processed in 45ms",
                        "[WARN] Connection pool 85% utilized",
                        "[ERROR] Timeout connecting to upstream service",
                        "[INFO] Health check passed",
                        "[WARN] Memory usage above 70%",
                };
                StringBuilder sb = new StringBuilder();
                for (int j = 0; j < 5; j++) {
                    sb.append(LocalDateTime.now().minusMinutes(5 - j).format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
                    sb.append(" ").append(logs[j]).append("\\n");
                }
                yield "{\"content\":[{\"type\":\"text\",\"text\":\"%s\"}]}".formatted(sb.toString());
            }
            case "deploy" ->
                "{\"content\":[{\"type\":\"text\",\"text\":\"Deployment initiated. Rolling update in progress. ETA: 2 minutes.\"}]}";
            case "scale" ->
                "{\"content\":[{\"type\":\"text\",\"text\":\"Scaling complete. New replica count: 5. All pods healthy.\"}]}";
            case "create_alert" ->
                "{\"content\":[{\"type\":\"text\",\"text\":\"Alert created: High CPU Usage > 90% for 5 minutes. Notification: Slack #ops-alerts.\"}]}";
            default -> "{\"content\":[{\"type\":\"text\",\"text\":\"Unknown tool\"}]}";
        };
    }

    static String readDevOpsResource(String params) {
        String uri = extractStr(params, "uri");
        Random rng = new Random();
        return switch (uri) {
            case "infra://services" -> {
                StringBuilder sb = new StringBuilder("[");
                int i = 0;
                for (var e : SERVICES.entrySet()) {
                    if (i++ > 0)
                        sb.append(",");
                    sb.append("{\"name\":\"%s\",\"version\":\"%s\",\"status\":\"%s\"}"
                            .formatted(e.getKey(), e.getValue().get("version"), e.getValue().get("status")));
                }
                yield "{\"contents\":[{\"text\":\"%s]\"}]}".formatted(sb.toString().replace("\"", "\\\""));
            }
            case "infra://alerts" ->
                "{\"contents\":[{\"text\":\"[ACTIVE] auth-service: High error rate (5xx > 5%). Duration: 12 min.\\n[RESOLVED] order-api: Latency spike. Resolved 30 min ago.\"}]}";
            case "infra://metrics/overview" ->
                "{\"contents\":[{\"text\":\"CPU: %.0f%%. Memory: %.0f%%. Disk: %.0f%%. Network: %.0f Mbps.\"}]}"
                        .formatted(30 + rng.nextDouble() * 50, 40 + rng.nextDouble() * 40, 20 + rng.nextDouble() * 60,
                                50 + rng.nextDouble() * 200);
            default -> "{\"contents\":[{\"text\":\"Resource not found: " + uri + "\"}]}";
        };
    }

    // ═══════════════════════════════════════════════════
    // DEMO: Simulate an incident response scenario
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 5.4: DevOps MCP Server (Java)     ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        // Simulate an incident response scenario
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  🚨 SCENARIO: auth-service is degraded");
        System.out.println("  ═══════════════════════════════════════\n");

        System.out.println("  Step 1: Check available tools");
        System.out.println("  → tools/list");
        System.out.println("  ← " + handleMethod("tools/list", "") + "\n");

        System.out.println("  Step 2: Run health check");
        System.out.println("  → tools/call {name: health_check}");
        System.out.println("  ← " + handleMethod("tools/call", "{\"name\":\"health_check\"}") + "\n");

        System.out.println("  Step 3: Check active alerts");
        System.out.println("  → resources/read {uri: infra://alerts}");
        System.out.println("  ← " + handleMethod("resources/read", "{\"uri\":\"infra://alerts\"}") + "\n");

        System.out.println("  Step 4: Get auth-service logs");
        System.out.println("  → tools/call {name: get_logs}");
        System.out.println("  ← " + handleMethod("tools/call", "{\"name\":\"get_logs\"}") + "\n");

        System.out.println("  Step 5: Check system metrics");
        System.out.println("  → resources/read {uri: infra://metrics/overview}");
        System.out.println("  ← " + handleMethod("resources/read", "{\"uri\":\"infra://metrics/overview\"}") + "\n");

        System.out.println("  Step 6: Scale auth-service");
        System.out.println("  → tools/call {name: scale}");
        System.out.println("  ← " + handleMethod("tools/call", "{\"name\":\"scale\"}") + "\n");

        System.out.println("  ✅ DevOps MCP Server Pattern:");
        System.out.println("     • AI assistant uses MCP to investigate and remediate incidents");
        System.out.println("     • Tools: health check, logs, deploy, scale, alerts");
        System.out.println("     • Resources: service list, active alerts, system metrics");
        System.out.println("     • Prompts: runbooks, post-mortems, checklists\n");
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
        while (i < json.length() && json.charAt(i) != '"')
            sb.append(json.charAt(i++));
        return sb.toString();
    }
}
