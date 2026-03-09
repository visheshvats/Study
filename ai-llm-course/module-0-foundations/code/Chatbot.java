
/**
 * MODULE 0 — Example 4: Interactive Chatbot (Java Equivalent)
 * ==============================================================
 * Java equivalent of 04_chatbot.py
 *
 * Demonstrates:
 *   1. Multi-turn conversation with history management
 *   2. System prompt as personality/role
 *   3. Streaming responses (Server-Sent Events)
 *   4. Token usage tracking
 *
 * JAVA ANALOGY:
 *   - Conversation history = session state in Spring (HttpSession)
 *   - Message list = List<ChatMessage> DTO
 *   - Streaming = SSE / WebFlux Flux<ServerSentEvent>
 *   - System prompt = Controller-level @Configuration
 *
 * COMPILE & RUN:
 *   javac 04_Chatbot.java && java Chatbot
 */

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Chatbot {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final String MODEL = "gpt-4o-mini";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    // ═══════════════════════════════════════════════════
    // CONVERSATION HISTORY
    // Like HttpSession or @SessionScope in Spring Boot
    // ═══════════════════════════════════════════════════

    /**
     * A simple chat message record.
     * In Spring Boot, this would be a DTO class:
     * public record ChatMessage(String role, String content) {}
     */
    record ChatMessage(String role, String content) {
        String toJson() {
            return """
                    {"role": "%s", "content": "%s"}""".formatted(role, escapeJson(content));
        }
    }

    /** Conversation history — like a List<ChatMessage> in a @Service */
    private final List<ChatMessage> history = new ArrayList<>();
    private int totalTokensUsed = 0;

    // ═══════════════════════════════════════════════════
    // CHATBOT SETUP
    // ═══════════════════════════════════════════════════

    Chatbot(String systemPrompt) {
        history.add(new ChatMessage("system", systemPrompt));
    }

    // ═══════════════════════════════════════════════════
    // SEND MESSAGE (Non-Streaming)
    // ═══════════════════════════════════════════════════

    String chat(String userMessage) throws Exception {
        // Add user message to history
        history.add(new ChatMessage("user", userMessage));

        // Build messages JSON array from history
        StringBuilder messagesJson = new StringBuilder("[");
        for (int i = 0; i < history.size(); i++) {
            if (i > 0)
                messagesJson.append(",");
            messagesJson.append(history.get(i).toJson());
        }
        messagesJson.append("]");

        String body = """
                {
                    "model": "%s",
                    "messages": %s,
                    "temperature": 0.7
                }
                """.formatted(MODEL, messagesJson.toString());

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

        String responseBody = response.body();
        String reply = extractContent(responseBody);
        int tokens = extractTokenUsage(responseBody);
        totalTokensUsed += tokens;

        // Add assistant reply to history
        history.add(new ChatMessage("assistant", reply));

        return reply;
    }

    // ═══════════════════════════════════════════════════
    // STREAMING CHAT
    // Like WebFlux Flux<String> or SSE in Spring Boot
    // ═══════════════════════════════════════════════════

    String chatStream(String userMessage) throws Exception {
        // Add user message to history
        history.add(new ChatMessage("user", userMessage));

        // Build messages JSON
        StringBuilder messagesJson = new StringBuilder("[");
        for (int i = 0; i < history.size(); i++) {
            if (i > 0)
                messagesJson.append(",");
            messagesJson.append(history.get(i).toJson());
        }
        messagesJson.append("]");

        String body = """
                {
                    "model": "%s",
                    "messages": %s,
                    "temperature": 0.7,
                    "stream": true
                }
                """.formatted(MODEL, messagesJson.toString());

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_URL))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

        // Stream the response — reads SSE events line by line
        HttpResponse<java.io.InputStream> response = httpClient.send(request,
                HttpResponse.BodyHandlers.ofInputStream());

        if (response.statusCode() != 200) {
            String err = new String(response.body().readAllBytes());
            throw new RuntimeException("API error: " + err);
        }

        StringBuilder fullReply = new StringBuilder();
        BufferedReader reader = new BufferedReader(new InputStreamReader(response.body()));
        String line;

        while ((line = reader.readLine()) != null) {
            if (line.startsWith("data: ")) {
                String data = line.substring(6).trim();
                if (data.equals("[DONE]"))
                    break;

                // Extract the delta content from the SSE chunk
                String delta = extractDeltaContent(data);
                if (delta != null && !delta.isEmpty()) {
                    System.out.print(delta); // Print each chunk as it arrives
                    fullReply.append(delta);
                }
            }
        }
        System.out.println(); // newline after streaming

        // Add complete reply to history
        history.add(new ChatMessage("assistant", fullReply.toString()));
        return fullReply.toString();
    }

    // ═══════════════════════════════════════════════════
    // JSON HELPERS
    // ═══════════════════════════════════════════════════

    static String escapeJson(String s) {
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\t", "\\t");
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

    /** Extract token count from "total_tokens": N in the response. */
    static int extractTokenUsage(String json) {
        String marker = "\"total_tokens\":";
        int idx = json.indexOf(marker);
        if (idx == -1)
            return 0;
        idx += marker.length();
        while (idx < json.length() && !Character.isDigit(json.charAt(idx)))
            idx++;
        StringBuilder num = new StringBuilder();
        while (idx < json.length() && Character.isDigit(json.charAt(idx))) {
            num.append(json.charAt(idx++));
        }
        return num.length() > 0 ? Integer.parseInt(num.toString()) : 0;
    }

    /** Extract delta content from a streaming SSE chunk. */
    static String extractDeltaContent(String json) {
        // Look for "delta":{"content":"..."}
        String marker = "\"content\":";
        int deltaIdx = json.indexOf("\"delta\":");
        if (deltaIdx == -1)
            return null;

        int contentIdx = json.indexOf(marker, deltaIdx);
        if (contentIdx == -1)
            return null;

        contentIdx += marker.length();
        while (contentIdx < json.length() && json.charAt(contentIdx) == ' ')
            contentIdx++;
        if (contentIdx >= json.length() || json.charAt(contentIdx) != '"')
            return null;
        contentIdx++;

        StringBuilder sb = new StringBuilder();
        while (contentIdx < json.length()) {
            char c = json.charAt(contentIdx);
            if (c == '\\' && contentIdx + 1 < json.length()) {
                char next = json.charAt(contentIdx + 1);
                switch (next) {
                    case '"':
                        sb.append('"');
                        contentIdx += 2;
                        continue;
                    case '\\':
                        sb.append('\\');
                        contentIdx += 2;
                        continue;
                    case 'n':
                        sb.append('\n');
                        contentIdx += 2;
                        continue;
                    case 't':
                        sb.append('\t');
                        contentIdx += 2;
                        continue;
                    default:
                        sb.append(c);
                        contentIdx++;
                        continue;
                }
            }
            if (c == '"')
                break;
            sb.append(c);
            contentIdx++;
        }
        return sb.toString();
    }

    // ═══════════════════════════════════════════════════
    // INTERACTIVE REPL
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) throws Exception {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 0.4: Interactive Chatbot (Java)   ║");
        System.out.println("║  Multi-turn conversation with streaming      ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        if (API_KEY == null || API_KEY.isEmpty()) {
            System.out.println("❌ Set OPENAI_API_KEY environment variable first!");
            return;
        }

        // Create chatbot with a system prompt personality
        Chatbot bot = new Chatbot(
                "You are a friendly Java programming tutor. "
                        + "You explain concepts using real-world analogies and short code examples. "
                        + "Keep responses concise (under 150 words). "
                        + "If the user asks about non-Java topics, gently redirect to Java.");

        System.out.println("  🤖 Java Tutor Bot ready! I can help you learn Java.");
        System.out.println("  💡 Commands:");
        System.out.println("     /stream  — Toggle streaming mode (currently: ON)");
        System.out.println("     /history — Show conversation history");
        System.out.println("     /tokens  — Show token usage");
        System.out.println("     /clear   — Clear conversation history");
        System.out.println("     /quit    — Exit\n");

        Scanner scanner = new Scanner(System.in);
        boolean useStreaming = true;

        while (true) {
            System.out.print("  👤 You: ");
            if (!scanner.hasNextLine())
                break;
            String input = scanner.nextLine().trim();

            if (input.isEmpty())
                continue;

            // Handle commands
            switch (input.toLowerCase()) {
                case "/quit" -> {
                    System.out.println("\n  👋 Goodbye! Happy coding!");
                    return;
                }
                case "/stream" -> {
                    useStreaming = !useStreaming;
                    System.out.println("  Streaming: " + (useStreaming ? "ON" : "OFF") + "\n");
                    continue;
                }
                case "/history" -> {
                    System.out.println("\n  📜 Conversation History:");
                    for (ChatMessage msg : bot.history) {
                        if (msg.role().equals("system"))
                            continue;
                        String icon = msg.role().equals("user") ? "👤" : "🤖";
                        String preview = msg.content().length() > 80
                                ? msg.content().substring(0, 80) + "..."
                                : msg.content();
                        System.out.println("     " + icon + " " + preview);
                    }
                    System.out.println();
                    continue;
                }
                case "/tokens" -> {
                    System.out.printf("  📊 Total tokens used: %,d%n",
                            bot.totalTokensUsed);
                    System.out.printf("  📊 Messages in history: %d%n%n",
                            bot.history.size());
                    continue;
                }
                case "/clear" -> {
                    String systemPrompt = bot.history.get(0).content();
                    bot.history.clear();
                    bot.history.add(new ChatMessage("system", systemPrompt));
                    bot.totalTokensUsed = 0;
                    System.out.println("  🗑️  History cleared.\n");
                    continue;
                }
            }

            // Chat!
            try {
                System.out.print("  🤖 ");
                if (useStreaming) {
                    bot.chatStream(input);
                } else {
                    String reply = bot.chat(input);
                    System.out.println(reply);
                }
                System.out.println();
            } catch (Exception e) {
                System.out.println("  ❌ Error: " + e.getMessage() + "\n");
            }
        }
    }
}
