
/**
 * MODULE 1 — PROJECT: Structured Response Generator (Java Equivalent)
 * =====================================================================
 * Java equivalent of 05_structured_generator.py
 *
 * A multi-step pipeline that processes support tickets:
 *   1. EXTRACT facts from raw customer message
 *   2. CLASSIFY the ticket priority and category
 *   3. GENERATE a structured response with resolution steps
 *
 * JAVA ANALOGY:
 *   This is like a Spring Batch pipeline:
 *     ItemReader (extract) → ItemProcessor (classify) → ItemWriter (generate)
 *   Or a multi-step @Service with @Transactional
 *
 * COMPILE & RUN:
 *   javac StructuredGenerator.java && java StructuredGenerator
 */

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class StructuredGenerator {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final String MODEL = "gpt-4o-mini";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    static String escapeJson(String s) {
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\t", "\\t");
    }

    static String callLlm(String systemPrompt, String userPrompt, double temperature,
            boolean jsonMode) throws Exception {
        String formatPart = jsonMode ? ", \"response_format\": {\"type\": \"json_object\"}" : "";

        String body = """
                {
                    "model": "%s",
                    "messages": [
                        {"role": "system", "content": "%s"},
                        {"role": "user", "content": "%s"}
                    ],
                    "temperature": %s,
                    "max_tokens": 600%s
                }
                """.formatted(MODEL, escapeJson(systemPrompt), escapeJson(userPrompt), temperature, formatPart);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_URL))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

        HttpResponse<String> response = httpClient.send(request,
                HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new RuntimeException("API error: " + response.body());
        }

        return extractContent(response.body());
    }

    static String extractContent(String json) {
        String marker = "\"content\":";
        int idx = json.indexOf(marker);
        if (idx == -1)
            return "[No content]";
        idx += marker.length();
        while (idx < json.length() && (json.charAt(idx) == ' ' || json.charAt(idx) == '\n'))
            idx++;
        if (idx >= json.length() || json.charAt(idx) != '"')
            return "[Unexpected format]";
        idx++;
        StringBuilder sb = new StringBuilder();
        while (idx < json.length()) {
            char c = json.charAt(idx);
            if (c == '\\' && idx + 1 < json.length()) {
                char next = json.charAt(idx + 1);
                switch (next) {
                    case '"':
                        sb.append('"');
                        idx += 2;
                        continue;
                    case '\\':
                        sb.append('\\');
                        idx += 2;
                        continue;
                    case 'n':
                        sb.append('\n');
                        idx += 2;
                        continue;
                    case 't':
                        sb.append('\t');
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
    // STEP 1: Extract Facts
    // Like an ItemReader in Spring Batch
    // ═══════════════════════════════════════════════════

    static String extractFacts(String rawMessage) throws Exception {
        System.out.println("  ▶ Step 1: EXTRACT — Pulling out structured facts\n");

        String systemPrompt = "You are a fact extraction specialist. Extract key facts from the support ticket. "
                + "Return JSON with this structure:\n"
                + "{\n"
                + "  \"customer_name\": \"name or 'Unknown'\",\n"
                + "  \"product\": \"product mentioned\",\n"
                + "  \"issue_summary\": \"one-sentence summary\",\n"
                + "  \"error_messages\": [\"exact error texts\"],\n"
                + "  \"environment\": \"OS/version/Java version if mentioned\",\n"
                + "  \"steps_tried\": [\"what they already tried\"],\n"
                + "  \"urgency_indicators\": [\"words suggesting urgency\"]\n"
                + "}";

        String extracted = callLlm(systemPrompt, rawMessage, 0.0, true);
        System.out.println("    ✅ Extracted: " + extracted.substring(0, Math.min(200, extracted.length())) + "...\n");
        return extracted;
    }

    // ═══════════════════════════════════════════════════
    // STEP 2: Classify Priority & Category
    // Like an ItemProcessor in Spring Batch
    // ═══════════════════════════════════════════════════

    static String classify(String extractedFacts) throws Exception {
        System.out.println("  ▶ Step 2: CLASSIFY — Determining priority and category\n");

        String systemPrompt = "You are a ticket classification system. Based on the extracted facts, classify the ticket.\n"
                + "Return JSON:\n"
                + "{\n"
                + "  \"priority\": \"P1_CRITICAL | P2_HIGH | P3_MEDIUM | P4_LOW\",\n"
                + "  \"category\": \"BUG | CONFIGURATION | PERFORMANCE | FEATURE_REQUEST | QUESTION\",\n"
                + "  \"subcategory\": \"more specific type\",\n"
                + "  \"estimated_complexity\": \"simple | moderate | complex\",\n"
                + "  \"suggested_team\": \"backend | frontend | devops | database | security\",\n"
                + "  \"classification_reasoning\": \"why this classification\"\n"
                + "}\n\n"
                + "Priority rules:\n"
                + "- P1: Production down, data loss, security breach\n"
                + "- P2: Major feature broken, many users affected\n"
                + "- P3: Minor bug, workaround available\n"
                + "- P4: Question, feature request, cosmetic issue";

        String classified = callLlm(systemPrompt, "Facts: " + extractedFacts, 0.0, true);
        System.out
                .println("    ✅ Classified: " + classified.substring(0, Math.min(200, classified.length())) + "...\n");
        return classified;
    }

    // ═══════════════════════════════════════════════════
    // STEP 3: Generate Response
    // Like an ItemWriter in Spring Batch
    // ═══════════════════════════════════════════════════

    static String generateResponse(String extractedFacts, String classification) throws Exception {
        System.out.println("  ▶ Step 3: GENERATE — Creating structured response\n");

        String systemPrompt = "You are a senior support engineer. Generate a professional response.\n"
                + "Return JSON:\n"
                + "{\n"
                + "  \"greeting\": \"personalized greeting\",\n"
                + "  \"issue_acknowledgment\": \"restate the problem\",\n"
                + "  \"resolution_steps\": [\n"
                + "    {\"step\": 1, \"action\": \"what to do\", \"command\": \"if applicable\", \"expected_result\": \"what should happen\"}\n"
                + "  ],\n"
                + "  \"if_not_resolved\": \"escalation steps\",\n"
                + "  \"closing\": \"professional closing\",\n"
                + "  \"internal_notes\": \"notes for the support team\"\n"
                + "}";

        String userPrompt = "Ticket facts:\n" + extractedFacts
                + "\n\nClassification:\n" + classification
                + "\n\nGenerate a complete support response.";

        String response = callLlm(systemPrompt, userPrompt, 0.5, true);
        System.out.println("    ✅ Response generated\n");
        return response;
    }

    // ═══════════════════════════════════════════════════
    // FULL PIPELINE
    // ═══════════════════════════════════════════════════

    static void processTicket(String ticket) throws Exception {
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  📨 Processing ticket...");
        System.out.println("  ═══════════════════════════════════════\n");
        System.out.println("  Raw input:");
        System.out.println("  " + ticket.substring(0, Math.min(200, ticket.length())) + "\n");

        // Pipeline: Extract → Classify → Generate
        String facts = extractFacts(ticket);
        String classification = classify(facts);
        String response = generateResponse(facts, classification);

        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  📋 PIPELINE RESULTS");
        System.out.println("  ═══════════════════════════════════════\n");
        System.out.println("  1️⃣ EXTRACTED FACTS:");
        System.out.println("  " + facts + "\n");
        System.out.println("  2️⃣ CLASSIFICATION:");
        System.out.println("  " + classification + "\n");
        System.out.println("  3️⃣ GENERATED RESPONSE:");
        System.out.println("  " + response + "\n");
    }

    // ═══════════════════════════════════════════════════
    // MAIN
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 1.5: Structured Generator (Java)  ║");
        System.out.println("║  Pipeline: Extract → Classify → Generate     ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY environment variable first!");
            return;
        }

        // Sample support tickets
        String ticket1 = "Hi, I'm John from Acme Corp. We're running Spring Boot 3.1 on Java 17 "
                + "(Ubuntu 22.04 LTS). Since yesterday's deployment, our user authentication "
                + "service is throwing 'io.jsonwebtoken.ExpiredJwtException' for ALL users — "
                + "not just expired tokens. We've already tried restarting the service and "
                + "clearing the Redis cache but the issue persists. This is blocking all 500 "
                + "users from logging in. URGENT — production is effectively down!";

        String ticket2 = "Hello, I was wondering if Spring Boot supports GraphQL out of the box? "
                + "I saw there's a spring-boot-starter-graphql but wasn't sure if it's "
                + "production-ready. We're considering migrating some of our REST endpoints. "
                + "Any recommendations? Thanks, Sarah.";

        processTicket(ticket1);
        System.out.println("\n\n");
        processTicket(ticket2);

        System.out.println("✅ Pipeline Pattern Summary:");
        System.out.println("  Extract → Classify → Generate");
        System.out.println("  Each step outputs JSON that feeds into the next");
        System.out.println("  Like Spring Batch: Reader → Processor → Writer\n");
    }
}
