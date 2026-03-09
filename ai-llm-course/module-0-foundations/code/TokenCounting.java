
/**
 * MODULE 0 — Example 3: Token Counting & Cost Estimation (Java Equivalent)
 * ==========================================================================
 * Java equivalent of 03_token_counting.py
 *
 * Demonstrates:
 *   1. What tokens are and how text gets tokenized
 *   2. Estimating token count (simplified — Java has no exact tiktoken equiv)
 *   3. Cost estimation for API calls
 *   4. Context window capacity checking
 *
 * NO API KEY NEEDED — runs entirely locally!
 *
 * JAVA ANALOGY:
 *   - Tokens are like bytes in a ByteBuffer — the actual unit the LLM "reads"
 *   - Context window = fixed-size buffer (like a circular buffer in Kafka)
 *   - Tokenization ≈ character encoding (like UTF-8 where 1 char ≠ 1 byte)
 *
 * COMPILE & RUN:
 *   javac 03_TokenCounting.java && java TokenCounting
 */

import java.util.*;
import java.util.regex.*;

public class TokenCounting {

    // ═══════════════════════════════════════════════════
    // PART 1: What are Tokens?
    // ═══════════════════════════════════════════════════

    static void demo1_WhatAreTokens() {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("PART 1: What are Tokens?");
        System.out.println("═══════════════════════════════════════════\n");

        System.out.println("  Tokens are the UNITS that LLMs read and generate.");
        System.out.println("  They're not quite words, not quite characters.\n");

        System.out.println("  Examples of tokenization (approximate):");
        System.out.println("  ─────────────────────────────────────────");

        String[] examples = {
                "Hello world", // Simple → ~2 tokens
                "Spring Boot auto-configuration", // Compound words → ~4-5 tokens
                "System.out.println(\"Hello\");", // Code → more tokens
                "こんにちは", // Japanese → many tokens
                "PostgreSQL", // Technical term → ~3 tokens
                "The quick brown fox jumps over the lazy dog", // ~9 tokens
        };

        for (String text : examples) {
            int estimatedTokens = estimateTokens(text);
            double ratio = (double) estimatedTokens / text.length();
            System.out.printf("  %-45s → ~%d tokens (%.2f tokens/char)%n",
                    "\"" + text + "\"", estimatedTokens, ratio);
        }

        System.out.println("\n  💡 Rule of thumb: 1 token ≈ 4 characters ≈ 0.75 words (English)");
        System.out.println("     Code and non-English text use MORE tokens per character\n");
    }

    /**
     * Estimate token count using heuristics.
     *
     * NOTE: Python uses the tiktoken library for exact counts.
     * Java has no official equivalent. This is a reasonable approximation.
     * For production, consider: https://github.com/knuddelsgmbh/jtokkit
     *
     * Heuristic: ~4 characters per token for English text,
     * adjusted for code and non-ASCII characters.
     */
    static int estimateTokens(String text) {
        if (text == null || text.isEmpty())
            return 0;

        // Count different character types for better estimation
        int asciiChars = 0;
        int nonAsciiChars = 0;
        int specialChars = 0;

        for (char c : text.toCharArray()) {
            if (c <= 127) {
                if (Character.isLetterOrDigit(c) || c == ' ')
                    asciiChars++;
                else
                    specialChars++;
            } else {
                nonAsciiChars++;
            }
        }

        // Heuristics:
        // - English text: ~4 chars per token
        // - Code/special chars: ~2 chars per token (more fragmented)
        // - Non-ASCII (CJK, etc): ~1-2 chars per token
        double estimate = (asciiChars / 4.0) + (specialChars / 2.0) + (nonAsciiChars / 1.5);
        return Math.max(1, (int) Math.ceil(estimate));
    }

    /**
     * Estimate tokens for a list of chat messages.
     */
    static int estimateMessageTokens(String[][] messages) {
        int total = 0;
        for (String[] msg : messages) {
            // Each message has ~4 tokens of overhead (role tags, separators)
            total += 4;
            total += estimateTokens(msg[1]); // content
        }
        total += 2; // conversation overhead
        return total;
    }

    // ═══════════════════════════════════════════════════
    // PART 2: Cost Estimation
    // ═══════════════════════════════════════════════════

    static void demo2_CostEstimation() {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("PART 2: Cost Estimation");
        System.out.println("═══════════════════════════════════════════\n");

        // Model pricing (as of 2024) per 1M tokens
        record ModelPricing(String model, double inputPer1M, double outputPer1M, int contextWindow) {
        }

        ModelPricing[] models = {
                new ModelPricing("gpt-4o-mini", 0.150, 0.600, 128_000),
                new ModelPricing("gpt-4o", 2.500, 10.000, 128_000),
                new ModelPricing("gpt-4-turbo", 10.00, 30.000, 128_000),
        };

        System.out.println("  Model Pricing (per 1M tokens):");
        System.out.println("  ─────────────────────────────────────────");
        System.out.printf("  %-15s │ %-10s │ %-10s │ %-10s%n",
                "Model", "Input", "Output", "Context");
        System.out.println("  ─────────────────────────────────────────");
        for (ModelPricing m : models) {
            System.out.printf("  %-15s │ $%-9.3f │ $%-9.3f │ %,d%n",
                    m.model, m.inputPer1M, m.outputPer1M, m.contextWindow);
        }

        // Example cost calculation
        System.out.println("\n  Example: Analyzing a code review");
        String codeReview = """
                Review this Spring Boot controller:
                @RestController
                @RequestMapping("/api/users")
                public class UserController {
                    @Autowired
                    private UserService userService;

                    @GetMapping
                    public ResponseEntity<List<UserDTO>> getAll(@RequestParam int page) {
                        return ResponseEntity.ok(userService.getAll(page));
                    }

                    @PostMapping
                    public ResponseEntity<UserDTO> create(@Valid @RequestBody CreateUserRequest req) {
                        return ResponseEntity.status(201).body(userService.create(req));
                    }
                }
                Please review for: error handling, validation, and best practices.
                """;

        int inputTokens = estimateTokens(codeReview);
        int estimatedOutputTokens = 200; // typical review response

        System.out.printf("  Input text: ~%d tokens%n", inputTokens);
        System.out.printf("  Expected output: ~%d tokens%n", estimatedOutputTokens);
        System.out.println();

        for (ModelPricing m : models) {
            double inputCost = (inputTokens / 1_000_000.0) * m.inputPer1M;
            double outputCost = (estimatedOutputTokens / 1_000_000.0) * m.outputPer1M;
            double totalCost = inputCost + outputCost;
            System.out.printf("  %-15s → $%.6f  (input: $%.6f + output: $%.6f)%n",
                    m.model, totalCost, inputCost, outputCost);
        }

        System.out.println("\n  💡 gpt-4o-mini is ~17x cheaper than gpt-4o for most tasks!");
        System.out.println("     Use mini for classification, extraction, simple Q&A");
        System.out.println("     Use gpt-4o for complex reasoning, code generation\n");
    }

    // ═══════════════════════════════════════════════════
    // PART 3: Context Window Capacity
    // ═══════════════════════════════════════════════════

    static void demo3_ContextWindow() {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("PART 3: Context Window — Will My Content Fit?");
        System.out.println("═══════════════════════════════════════════\n");

        int contextWindow = 128_000; // gpt-4o-mini

        System.out.println("  Context window = the LLM's 'working memory'");
        System.out.println("  Everything must fit: system prompt + history + input + output\n");

        // Simulate different content sizes
        record ContentExample(String name, int approximateTokens) {
        }

        ContentExample[] examples = {
                new ContentExample("Short question", 20),
                new ContentExample("Code review (50 lines)", 200),
                new ContentExample("Bug report with stack trace", 500),
                new ContentExample("Full Java class (200 lines)", 800),
                new ContentExample("API documentation page", 2_000),
                new ContentExample("README.md (large project)", 5_000),
                new ContentExample("Small codebase (10 files)", 15_000),
                new ContentExample("Medium codebase (50 files)", 75_000),
                new ContentExample("Large codebase (200 files)", 300_000),
        };

        int reservedForOutput = 4_000;
        int available = contextWindow - reservedForOutput;

        System.out.printf("  Context window: %,d tokens%n", contextWindow);
        System.out.printf("  Reserved for output: %,d tokens%n", reservedForOutput);
        System.out.printf("  Available for input: %,d tokens%n%n", available);

        System.out.println("  Content                          │ Tokens    │ Fits?  │ % Used");
        System.out.println("  ─────────────────────────────────┼───────────┼────────┼────────");

        for (ContentExample ex : examples) {
            boolean fits = ex.approximateTokens <= available;
            double pctUsed = (ex.approximateTokens / (double) available) * 100;
            System.out.printf("  %-35s│ %,9d │ %s    │ %5.1f%%%n",
                    ex.name, ex.approximateTokens,
                    fits ? "✅" : "❌", pctUsed);
        }

        System.out.println("\n  💡 When content is too large:");
        System.out.println("     → Chunking: Split into pieces (Module 3)");
        System.out.println("     → RAG: Only send relevant chunks (Module 3)");
        System.out.println("     → Summary: Compress old conversation (Module 7)\n");
    }

    // ═══════════════════════════════════════════════════
    // PART 4: Token Counting for Chat Messages
    // ═══════════════════════════════════════════════════

    static void demo4_ChatTokens() {
        System.out.println("═══════════════════════════════════════════");
        System.out.println("PART 4: Counting Tokens in Chat Messages");
        System.out.println("═══════════════════════════════════════════\n");

        // Simulate a conversation
        String[][] conversation = {
                { "system", "You are a helpful Java programming assistant." },
                { "user", "What is the difference between ArrayList and LinkedList?" },
                { "assistant", "ArrayList uses a dynamic array internally, providing O(1) random access "
                        + "but O(n) insertions in the middle. LinkedList uses a doubly-linked list, "
                        + "giving O(1) insertions/deletions but O(n) random access." },
                { "user", "Which should I use for a queue?" },
                { "assistant", "For a queue (FIFO), use ArrayDeque — it's faster than LinkedList for "
                        + "both add and remove operations due to better cache locality. "
                        + "LinkedList has more memory overhead per element (prev/next pointers)." },
                { "user", "Show me a code example" },
        };

        System.out.println("  Message-by-message token usage:");
        System.out.println("  ─────────────────────────────────────────");

        int runningTotal = 0;
        for (String[] msg : conversation) {
            int tokens = estimateTokens(msg[1]) + 4; // content + overhead
            runningTotal += tokens;
            String preview = msg[1].length() > 40
                    ? msg[1].substring(0, 40) + "..."
                    : msg[1];
            System.out.printf("  [%9s] ~%3d tokens (total: %4d) │ %s%n",
                    msg[0], tokens, runningTotal, preview);
        }

        System.out.println("\n  💡 Conversation tokens GROW with each message");
        System.out.println("     This is why chat apps need memory strategies (Module 7)");
        System.out.printf("     After 6 messages: ~%d tokens used%n", runningTotal);
        System.out.printf("     After 100 messages: ~%d tokens (estimate)%n\n",
                (int) (runningTotal * (100.0 / 6)));
    }

    // ═══════════════════════════════════════════════════
    // MAIN
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 0.3: Token Counting (Java)        ║");
        System.out.println("║  NO API KEY NEEDED — runs locally            ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        demo1_WhatAreTokens();
        demo2_CostEstimation();
        demo3_ContextWindow();
        demo4_ChatTokens();

        System.out.println("✅ Key takeaways:");
        System.out.println("  • 1 token ≈ 4 chars ≈ 0.75 words (English)");
        System.out.println("  • Code & non-English text use more tokens");
        System.out.println("  • gpt-4o-mini is cheapest for most tasks");
        System.out.println("  • Context window = total budget for input + output");
        System.out.println("  • Chat tokens grow with conversation length\n");
    }
}
