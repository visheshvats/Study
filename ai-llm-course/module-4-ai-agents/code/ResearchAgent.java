
/**
 * MODULE 4 — PROJECT: Research Agent (Java Equivalent)
 * =======================================================
 * Java equivalent of 04_research_agent.py
 *
 * A multi-tool research agent that:
 *   1. Searches for information
 *   2. Analyzes/compares findings
 *   3. Generates a structured report
 *
 * COMPILE & RUN:
 *   javac ResearchAgent.java && java ResearchAgent
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;

public class ResearchAgent {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String esc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    static String chat(String system, String user) throws Exception {
        var body = "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"%s\"},{\"role\":\"user\",\"content\":\"%s\"}],\"temperature\":0.5,\"max_tokens\":700}"
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
    // RESEARCH TOOLS
    // ═══════════════════════════════════════════════════

    /** Simulated search — in production, use a real search API. */
    static String search(String query) throws Exception {
        return chat("You are a search engine. Return 3-4 factual bullet points about the query. "
                + "Include specific versions, dates, and performance numbers when possible.",
                "Search: " + query);
    }

    /** Analyze and compare information. */
    static String analyze(String topic, String data) throws Exception {
        return chat("You are a technical analyst. Analyze the data and provide insights. "
                + "Focus on trade-offs, performance, and practical recommendations.",
                "Topic: " + topic + "\n\nData to analyze:\n" + data);
    }

    /** Generate a structured research report. */
    static String generateReport(String topic, String research, String analysis) throws Exception {
        return chat("You are a technical writer. Create a clear, structured research report. "
                + "Include: Summary, Key Findings, Comparison Table (if applicable), "
                + "Recommendations, and Next Steps.",
                "Topic: " + topic + "\n\nResearch:\n" + research + "\n\nAnalysis:\n" + analysis);
    }

    // ═══════════════════════════════════════════════════
    // RESEARCH AGENT LOOP
    // ═══════════════════════════════════════════════════

    static void research(String topic) throws Exception {
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  🔬 Research Topic: " + topic);
        System.out.println("  ═══════════════════════════════════════\n");

        // Step 1: Generate search queries
        System.out.println("  📋 Step 1: Generating search queries...");
        String queries = chat("Generate 3 specific search queries to thoroughly research this topic. "
                + "Return one per line, no numbering.", topic);
        System.out.println("    Queries:\n    " + queries.replace("\n", "\n    ") + "\n");

        // Step 2: Search each query
        System.out.println("  🔍 Step 2: Searching...");
        StringBuilder allResults = new StringBuilder();
        for (String query : queries.split("\n")) {
            query = query.trim();
            if (query.isEmpty())
                continue;
            System.out.println("    Searching: \"" + query + "\"");
            String result = search(query);
            allResults.append("Query: ").append(query).append("\n").append(result).append("\n\n");
        }
        System.out.println("    ✅ Search complete\n");

        // Step 3: Analyze
        System.out.println("  🔬 Step 3: Analyzing findings...");
        String analysis = analyze(topic, allResults.toString());
        System.out.println("    ✅ Analysis complete\n");

        // Step 4: Generate report
        System.out.println("  📝 Step 4: Generating report...\n");
        String report = generateReport(topic, allResults.toString(), analysis);

        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  📋 RESEARCH REPORT");
        System.out.println("  ═══════════════════════════════════════\n");
        System.out.println("  " + report.replace("\n", "\n  "));
        System.out.println();
    }

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 4.4: Research Agent (Java)        ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY!");
            return;
        }

        research("Virtual Threads vs Reactive Programming (WebFlux) for Java microservices in 2024");

        System.out.println("  ✅ Research Agent Pattern:");
        System.out.println("     1. Plan queries → 2. Search → 3. Analyze → 4. Report\n");
    }
}
