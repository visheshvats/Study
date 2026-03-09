
/**
 * MODULE 3 — Example 2: Chunking Strategies (Java Equivalent)
 * ==============================================================
 * Java equivalent of 02_chunking_strategies.py
 *
 * NO API KEY NEEDED — all text processing happens locally!
 *
 * Compares 4 chunking strategies:
 *   1. Fixed-size: Split every N characters
 *   2. Sentence-based: Split on sentence boundaries
 *   3. Structure-based: Split on markdown/code structure
 *   4. Recursive: Try splitting by structure, then sentence, then character
 *
 * COMPILE & RUN:
 *   javac ChunkingStrategies.java && java ChunkingStrategies
 */

import java.util.*;
import java.util.regex.*;

public class ChunkingStrategies {

    // ═══════════════════════════════════════════════════
    // STRATEGY 1: Fixed-Size Chunking
    // ═══════════════════════════════════════════════════

    static List<String> fixedSizeChunk(String text, int chunkSize, int overlap) {
        List<String> chunks = new ArrayList<>();
        int start = 0;
        while (start < text.length()) {
            int end = Math.min(start + chunkSize, text.length());
            chunks.add(text.substring(start, end));
            start += chunkSize - overlap;
        }
        return chunks;
    }

    // ═══════════════════════════════════════════════════
    // STRATEGY 2: Sentence-Based Chunking
    // ═══════════════════════════════════════════════════

    static List<String> sentenceChunk(String text, int maxChunkSize) {
        // Split on sentence boundaries
        String[] sentences = text.split("(?<=[.!?])\\s+");
        List<String> chunks = new ArrayList<>();
        StringBuilder current = new StringBuilder();

        for (String sentence : sentences) {
            if (current.length() + sentence.length() > maxChunkSize && current.length() > 0) {
                chunks.add(current.toString().trim());
                current = new StringBuilder();
            }
            current.append(sentence).append(" ");
        }
        if (current.length() > 0)
            chunks.add(current.toString().trim());
        return chunks;
    }

    // ═══════════════════════════════════════════════════
    // STRATEGY 3: Structure-Based Chunking
    // ═══════════════════════════════════════════════════

    static List<String> structureChunk(String text) {
        // Split on markdown headers, code blocks, blank lines
        String[] sections = text.split("(?m)(?=^#{1,3} |^```|\\n\\n)");
        List<String> chunks = new ArrayList<>();
        for (String section : sections) {
            String trimmed = section.trim();
            if (!trimmed.isEmpty())
                chunks.add(trimmed);
        }
        return chunks;
    }

    // ═══════════════════════════════════════════════════
    // STRATEGY 4: Recursive Chunking
    // ═══════════════════════════════════════════════════

    static List<String> recursiveChunk(String text, int maxChunkSize) {
        if (text.length() <= maxChunkSize) {
            return List.of(text);
        }

        // Try splitting by priority: \n\n → \n → . → space → character
        String[] separators = { "\n\n", "\n", ". ", " " };
        for (String sep : separators) {
            String[] parts = text.split(Pattern.quote(sep), -1);
            if (parts.length > 1) {
                List<String> chunks = new ArrayList<>();
                StringBuilder current = new StringBuilder();
                for (String part : parts) {
                    if (current.length() + part.length() + sep.length() > maxChunkSize
                            && current.length() > 0) {
                        chunks.add(current.toString().trim());
                        current = new StringBuilder();
                    }
                    if (current.length() > 0)
                        current.append(sep);
                    current.append(part);
                }
                if (current.length() > 0)
                    chunks.add(current.toString().trim());

                // If all chunks are within size, we're done
                boolean allFit = chunks.stream().allMatch(c -> c.length() <= maxChunkSize * 1.1);
                if (allFit)
                    return chunks;

                // Otherwise, recursively split oversized chunks
                List<String> result = new ArrayList<>();
                for (String chunk : chunks) {
                    if (chunk.length() > maxChunkSize * 1.1) {
                        result.addAll(recursiveChunk(chunk, maxChunkSize));
                    } else {
                        result.add(chunk);
                    }
                }
                return result;
            }
        }
        // Last resort: fixed-size split
        return fixedSizeChunk(text, maxChunkSize, 0);
    }

    // ═══════════════════════════════════════════════════
    // DEMO
    // ═══════════════════════════════════════════════════

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════╗");
        System.out.println("║  ☕ Module 3.2: Chunking Strategies (Java)   ║");
        System.out.println("║  NO API KEY NEEDED — runs locally            ║");
        System.out.println("╚══════════════════════════════════════════════╝\n");

        String sampleText = """
                # Spring Boot Configuration

                Spring Boot uses application.properties or application.yml for configuration.
                You can override properties using environment variables, command-line arguments,
                or profile-specific files like application-dev.properties.

                ## Database Configuration

                Configure the database connection using these properties:
                spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
                spring.datasource.username=admin
                spring.datasource.password=secret
                spring.jpa.hibernate.ddl-auto=update

                ## Server Configuration

                The embedded server can be configured with:
                server.port=8080
                server.servlet.context-path=/api
                server.compression.enabled=true

                For production, always externalize configuration using environment variables
                or a config server like Spring Cloud Config. Never hardcode credentials.

                ## Profiles

                Spring profiles allow environment-specific configuration.
                Use @Profile annotation or spring.profiles.active property.
                Common profiles: dev, staging, production.
                Each profile can have its own properties file.
                """;

        System.out.println("  📝 Sample text: " + sampleText.length() + " characters\n");

        // Strategy 1: Fixed-size
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  STRATEGY 1: Fixed-Size (200 chars, 50 overlap)\n");
        var fixed = fixedSizeChunk(sampleText, 200, 50);
        printChunks(fixed);

        // Strategy 2: Sentence-based
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  STRATEGY 2: Sentence-Based (max 250 chars)\n");
        var sentences = sentenceChunk(sampleText, 250);
        printChunks(sentences);

        // Strategy 3: Structure-based
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  STRATEGY 3: Structure-Based (headers/paragraphs)\n");
        var structural = structureChunk(sampleText);
        printChunks(structural);

        // Strategy 4: Recursive
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  STRATEGY 4: Recursive (max 250 chars)\n");
        var recursive = recursiveChunk(sampleText, 250);
        printChunks(recursive);

        // Comparison
        System.out.println("  ═══════════════════════════════════════");
        System.out.println("  📊 COMPARISON");
        System.out.println("  ═══════════════════════════════════════\n");
        System.out.printf("  %-15s │ Chunks │ Avg Size │ Min │ Max%n", "Strategy");
        System.out.println("  ────────────────┼────────┼──────────┼─────┼─────");
        printStats("Fixed-200", fixed);
        printStats("Sentence", sentences);
        printStats("Structure", structural);
        printStats("Recursive", recursive);

        System.out.println("\n  ✅ When to use each:");
        System.out.println("     Fixed    → Simple, predictable size. Breaks mid-sentence.");
        System.out.println("     Sentence → Clean breaks. May produce uneven sizes.");
        System.out.println("     Structure→ Best for docs with headers/sections.");
        System.out.println("     Recursive→ Best general-purpose. Tries structure first.\n");
        System.out.println("  📌 For RAG: Recursive chunking is usually best!\n");
    }

    static void printChunks(List<String> chunks) {
        for (int i = 0; i < chunks.size(); i++) {
            String preview = chunks.get(i).replace("\n", "\\n");
            if (preview.length() > 70)
                preview = preview.substring(0, 70) + "...";
            System.out.printf("    Chunk %d (%3d chars): %s%n", i + 1, chunks.get(i).length(), preview);
        }
        System.out.println();
    }

    static void printStats(String name, List<String> chunks) {
        int total = chunks.stream().mapToInt(String::length).sum();
        int min = chunks.stream().mapToInt(String::length).min().orElse(0);
        int max = chunks.stream().mapToInt(String::length).max().orElse(0);
        System.out.printf("  %-15s │ %6d │ %8d │ %3d │ %3d%n",
                name, chunks.size(), total / chunks.size(), min, max);
    }
}
