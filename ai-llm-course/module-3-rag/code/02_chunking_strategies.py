"""
MODULE 3 — Example 2: Chunking Strategies Compared
=====================================================
Shows 4 different chunking strategies and their impact on RAG quality.

Chunking is the MOST IMPORTANT detail in RAG.
Bad chunks = bad retrieval = bad answers.

SETUP:
  pip install tiktoken

RUN:
  python 02_chunking_strategies.py

NO API KEY NEEDED — runs entirely locally.
"""

import re
import tiktoken


# ══════════════════════════════════════════════════════
# SAMPLE DOCUMENT (realistic technical content)
# ══════════════════════════════════════════════════════

SAMPLE_DOCUMENT = """
# Apache Kafka: Complete Guide

## What is Kafka?

Apache Kafka is a distributed event streaming platform. Originally developed at LinkedIn, it is now maintained by the Apache Software Foundation. Kafka is designed for high-throughput, fault-tolerant, and scalable real-time data streaming.

## Core Concepts

### Topics and Partitions

A topic is a category or feed name to which records are published. Topics are split into partitions for parallelism. Each partition is an ordered, immutable sequence of records. Records within a partition are assigned a sequential ID called an offset.

Partitions allow Kafka to scale horizontally. Each partition can be hosted on a different broker, enabling parallel reads and writes. The number of partitions determines the maximum consumer parallelism.

### Producers

Producers publish data to topics. They are responsible for choosing which partition within a topic to send the record to. This can be done in a round-robin fashion for load balancing, or based on a message key for ordering guarantees.

Producer acknowledgment modes:
- acks=0: Fire and forget, fastest but may lose data
- acks=1: Leader acknowledgment, good balance
- acks=all: All replicas acknowledge, safest but slowest

### Consumers and Consumer Groups

Consumers read data from topics. Each consumer belongs to a consumer group. Within a group, each partition is consumed by exactly one consumer. This enables parallel processing while ensuring ordering within each partition.

When a consumer joins or leaves a group, the partitions are redistributed among the remaining consumers. This process is called rebalancing. Rebalancing ensures even workload distribution but temporarily pauses consumption.

### Kafka Connect

Kafka Connect is a framework for connecting Kafka with external systems. Source connectors import data from external systems into Kafka topics. Sink connectors export data from Kafka topics to external systems. Common connectors include JDBC, Elasticsearch, S3, and MongoDB.

## Performance Tuning

For optimal performance, consider these settings:

Batch size affects throughput. A larger batch size (batch.size) allows more records to be sent in a single request, improving throughput at the cost of latency.

Compression (compression.type) reduces network bandwidth usage. LZ4 provides the best balance of compression ratio and CPU usage. Snappy is slightly faster but with less compression.

Buffer memory (buffer.memory) determines how much memory the producer can use to buffer records waiting to be sent. If the buffer fills up, the producer will block or throw an exception depending on the max.block.ms setting.

## Security

Kafka supports multiple security mechanisms: SSL/TLS for encryption in transit, SASL for authentication (supporting PLAIN, SCRAM, GSSAPI/Kerberos, and OAuth), and ACLs for authorization. Always enable SSL in production environments.
"""


# ══════════════════════════════════════════════════════
# STRATEGY 1: Fixed-Size Chunking
# ══════════════════════════════════════════════════════

def chunk_fixed_size(text: str, chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    """
    Split text into fixed-size character chunks with overlap.
    
    Pros: Simple, predictable chunk sizes
    Cons: May cut mid-sentence, ignores document structure
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "strategy": "fixed_size",
                "start_char": start,
                "end_char": min(end, len(text)),
            })
        start += chunk_size - overlap  # Move forward, keeping overlap

    return chunks


# ══════════════════════════════════════════════════════
# STRATEGY 2: Sentence-Based Chunking
# ══════════════════════════════════════════════════════

def chunk_by_sentences(text: str, max_sentences: int = 5, overlap_sentences: int = 1) -> list[dict]:
    """
    Split by sentences, then group into chunks.
    
    Pros: Never cuts mid-sentence, natural boundaries
    Cons: Chunk sizes vary, may still split related paragraphs
    """
    # Simple sentence splitter (production: use spaCy or NLTK)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    i = 0

    while i < len(sentences):
        chunk_sentences = sentences[i:i + max_sentences]
        chunk_text = " ".join(chunk_sentences)

        if chunk_text.strip():
            chunks.append({
                "text": chunk_text.strip(),
                "strategy": "sentence_based",
                "sentence_start": i,
                "sentence_end": min(i + max_sentences, len(sentences)),
            })

        i += max_sentences - overlap_sentences

    return chunks


# ══════════════════════════════════════════════════════
# STRATEGY 3: Structure-Based Chunking (by headings)
# ══════════════════════════════════════════════════════

def chunk_by_structure(text: str) -> list[dict]:
    """
    Split by document structure (markdown headings).
    
    Pros: Preserves author's intended organization
    Cons: Only works for structured documents
    """
    chunks = []
    current_heading = "Introduction"
    current_text = ""

    for line in text.split("\n"):
        # Detect headings
        heading_match = re.match(r'^(#{1,3})\s+(.+)', line)

        if heading_match:
            # Save previous section
            if current_text.strip():
                chunks.append({
                    "text": f"{current_heading}\n\n{current_text.strip()}",
                    "strategy": "structure_based",
                    "heading": current_heading,
                })
            current_heading = heading_match.group(2)
            current_text = ""
        else:
            current_text += line + "\n"

    # Don't forget the last section
    if current_text.strip():
        chunks.append({
            "text": f"{current_heading}\n\n{current_text.strip()}",
            "strategy": "structure_based",
            "heading": current_heading,
        })

    return chunks


# ══════════════════════════════════════════════════════
# STRATEGY 4: Recursive Character Chunking
# (Similar to LangChain's RecursiveCharacterTextSplitter)
# ══════════════════════════════════════════════════════

def chunk_recursive(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
    separators: list[str] = None,
) -> list[dict]:
    """
    Try to split on the best separator first, then fall back to smaller ones.
    
    Hierarchy: paragraphs → sentences → words → characters
    
    Pros: Best balance of quality and simplicity
    Cons: Slightly more complex to implement
    
    This is what LangChain uses as its DEFAULT chunker.
    """
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    chunks = []

    def _split(text: str, seps: list[str]) -> list[str]:
        if not seps:
            return [text]

        sep = seps[0]
        if sep:
            parts = text.split(sep)
        else:
            # Last resort: split by characters
            parts = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

        result = []
        current = ""

        for part in parts:
            test = current + sep + part if current else part

            if len(test) <= chunk_size:
                current = test
            else:
                if current:
                    result.append(current)
                # If this single part is too big, split deeper
                if len(part) > chunk_size:
                    result.extend(_split(part, seps[1:]))
                else:
                    current = part

        if current:
            result.append(current)

        return result

    raw_chunks = _split(text, separators)

    # Add overlap
    for i, chunk in enumerate(raw_chunks):
        chunk_text = chunk.strip()
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "strategy": "recursive",
                "index": i,
            })

    return chunks


# ══════════════════════════════════════════════════════
# COMPARISON
# ══════════════════════════════════════════════════════

def compare_strategies():
    """Compare all 4 chunking strategies on the same document."""
    print("╔══════════════════════════════════════════════╗")
    print("║  📊 Chunking Strategy Comparison             ║")
    print("╚══════════════════════════════════════════════╝\n")

    enc = tiktoken.encoding_for_model("gpt-4o-mini")

    strategies = [
        ("Fixed-Size (500 chars)", chunk_fixed_size(SAMPLE_DOCUMENT, 500, 100)),
        ("Sentence-Based (5 sentences)", chunk_by_sentences(SAMPLE_DOCUMENT, 5, 1)),
        ("Structure-Based (headings)", chunk_by_structure(SAMPLE_DOCUMENT)),
        ("Recursive (500 chars)", chunk_recursive(SAMPLE_DOCUMENT, 500, 100)),
    ]

    for name, chunks in strategies:
        print(f"  {'═'*55}")
        print(f"  📋 Strategy: {name}")
        print(f"  {'─'*55}")
        print(f"  Total chunks: {len(chunks)}")

        sizes = [len(c["text"]) for c in chunks]
        token_counts = [len(enc.encode(c["text"])) for c in chunks]

        print(f"  Char sizes:  min={min(sizes)}, max={max(sizes)}, avg={sum(sizes)//len(sizes)}")
        print(f"  Token sizes: min={min(token_counts)}, max={max(token_counts)}, avg={sum(token_counts)//len(token_counts)}")

        # Show first chunk as example
        first_chunk = chunks[0]["text"][:150].replace("\n", " ")
        print(f"  First chunk: \"{first_chunk}...\"")

        # Show if any chunk cuts mid-sentence
        mid_sentence_cuts = 0
        for c in chunks:
            text = c["text"].strip()
            if text and not text[-1] in ".!?:'\"\n)" and not text.endswith("```"):
                mid_sentence_cuts += 1
        print(f"  Mid-sentence cuts: {mid_sentence_cuts}")
        print()

    # Recommendation
    print(f"  {'═'*55}")
    print(f"  💡 RECOMMENDATIONS:")
    print(f"  {'─'*55}")
    print(f"  • Quick prototype → Fixed-size (simple, fast)")
    print(f"  • General purpose → Recursive (LangChain default)")
    print(f"  • Markdown/HTML → Structure-based (preserves headings)")
    print(f"  • Best quality → Sentence-based with semantic grouping")
    print(f"  • Always → 10-20% overlap between chunks\n")


def demo_chunking_impact():
    """Shows how chunking affects search relevance."""
    print(f"  {'═'*55}")
    print(f"  🔍 How Chunking Affects Search")
    print(f"  {'─'*55}")

    query = "What are the producer acknowledgment modes in Kafka?"

    # The relevant text is in a paragraph about Producers
    relevant_text = (
        "acks=0: Fire and forget, fastest but may lose data\n"
        "acks=1: Leader acknowledgment, good balance\n"
        "acks=all: All replicas acknowledge, safest but slowest"
    )

    strategies = {
        "Fixed-Size": chunk_fixed_size(SAMPLE_DOCUMENT, 500, 100),
        "Sentence-Based": chunk_by_sentences(SAMPLE_DOCUMENT, 5, 1),
        "Structure-Based": chunk_by_structure(SAMPLE_DOCUMENT),
        "Recursive": chunk_recursive(SAMPLE_DOCUMENT, 500, 100),
    }

    for name, chunks in strategies.items():
        # Find which chunk contains the relevant text
        found_in = None
        for i, chunk in enumerate(chunks):
            if "acks=0" in chunk["text"] and "acks=all" in chunk["text"]:
                found_in = i
                break

        if found_in is not None:
            chunk_size = len(chunks[found_in]["text"])
            other_content = chunk_size - len(relevant_text)
            print(f"  {name:20s}: ✅ Found in chunk {found_in} ({chunk_size} chars, {other_content} chars of noise)")
        else:
            # Check if it's split across chunks
            chunks_with_acks = [i for i, c in enumerate(chunks) if "acks=" in c["text"]]
            print(f"  {name:20s}: ⚠️  Split across chunks {chunks_with_acks}")

    print(f"\n  → Structure-based chunking keeps the entire Producers section together!")
    print(f"  → Fixed-size may split the acks list across two chunks!")


if __name__ == "__main__":
    compare_strategies()
    demo_chunking_impact()
    print(f"\n  ✅ Key insight: Choose chunking strategy based on your document type.\n")
