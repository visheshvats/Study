"""
MODULE 2 — PROJECT: Document Search Engine
=============================================
A production-style document search engine using ChromaDB + OpenAI.

This project ties together everything from Module 2:
  - Text chunking
  - Embedding generation
  - Vector storage (ChromaDB)
  - Semantic search with metadata filtering
  - Search result ranking

FEATURES:
  1. Add documents (text files, strings, etc.)
  2. Automatic chunking for long documents
  3. Semantic search with relevance scores
  4. Metadata filtering (by source, date, topic)
  5. Interactive search REPL

SETUP:
  pip install chromadb openai python-dotenv rich

RUN:
  python 05_document_search_engine.py

JAVA ANALOGY:
  This is like building a simplified Elasticsearch, but instead of
  keyword-based BM25 scoring, we use semantic embeddings.
  Think of it as a Spring Boot @Service with a ChromaDB repository.
"""

import os
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ══════════════════════════════════════════════════════
# DOCUMENT CHUNKER
# ══════════════════════════════════════════════════════

class DocumentChunker:
    """
    Splits documents into overlapping chunks for embedding.
    
    Why chunk?
    - Embeddings work best on 200-500 token segments
    - Long documents get "diluted" — meaning gets averaged out
    - Chunks allow finding SPECIFIC relevant sections
    
    Java Analogy: Like splitting a large Kafka message into
    smaller batches for parallel processing.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Args:
            chunk_size: Max characters per chunk (approx ~125 tokens for English)
            chunk_overlap: Characters of overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, source: str = "unknown") -> list[dict]:
        """
        Split text into overlapping chunks with metadata.
        
        Strategy: Split by sentences first, then combine into chunks.
        This avoids cutting sentences in half.
        """
        # Split into sentences (simplified)
        sentences = []
        for part in text.replace("\n\n", ". ").split(". "):
            stripped = part.strip()
            if stripped:
                sentences.append(stripped + ".")

        chunks = []
        current_chunk = ""
        chunk_index = 0

        for sentence in sentences:
            # If adding this sentence exceeds chunk_size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "source": source,
                    "chunk_index": chunk_index,
                    "char_count": len(current_chunk.strip()),
                })
                chunk_index += 1

                # Keep overlap from end of current chunk
                overlap_text = current_chunk[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk += " " + sentence

        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "source": source,
                "chunk_index": chunk_index,
                "char_count": len(current_chunk.strip()),
            })

        return chunks


# ══════════════════════════════════════════════════════
# SEARCH ENGINE
# ══════════════════════════════════════════════════════

class DocumentSearchEngine:
    """
    A semantic search engine built on ChromaDB + OpenAI embeddings.
    
    Architecture:
    
    Document → Chunker → Embeddings (OpenAI) → ChromaDB
                                                    │
    Query → Embedding (OpenAI) → Search ────────────┘
                                    │
                                    ▼
                              Ranked Results
    """

    def __init__(self, collection_name: str = "doc_search", persist_dir: str = None):
        """
        Args:
            collection_name: Name of the ChromaDB collection
            persist_dir: Directory for persistent storage (None = in-memory)
        """
        if persist_dir:
            self.client = chromadb.PersistentClient(path=persist_dir)
        else:
            self.client = chromadb.Client()

        # Custom embedding function using OpenAI
        self.embed_fn = self._create_embedding_function()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )

        self.chunker = DocumentChunker()
        print(f"  📚 Search engine initialized. Documents: {self.collection.count()}")

    def _create_embedding_function(self):
        """Create a ChromaDB-compatible embedding function using OpenAI."""
        class OpenAIEmbedFunction:
            def __call__(self, input: list[str]) -> list[list[float]]:
                response = openai_client.embeddings.create(
                    input=input,
                    model="text-embedding-3-small",
                )
                return [item.embedding for item in response.data]
        return OpenAIEmbedFunction()

    def add_document(self, text: str, source: str = "manual", topic: str = "general"):
        """
        Add a document to the search index.
        Long documents are automatically chunked.
        
        Java Analogy: Like a REST endpoint:
        POST /api/documents { text, source, topic }
        """
        chunks = self.chunker.chunk_text(text, source)

        documents = []
        metadatas = []
        ids = []

        for chunk in chunks:
            # Generate unique ID from content hash
            doc_id = hashlib.md5(
                f"{source}_{chunk['chunk_index']}_{chunk['text'][:50]}".encode()
            ).hexdigest()

            documents.append(chunk["text"])
            metadatas.append({
                "source": source,
                "topic": topic,
                "chunk_index": chunk["chunk_index"],
                "total_chunks": len(chunks),
                "char_count": chunk["char_count"],
                "indexed_at": datetime.now().isoformat(),
            })
            ids.append(doc_id)

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

        print(f"  ✅ Added '{source}': {len(chunks)} chunk(s)")

    def search(
        self,
        query: str,
        n_results: int = 5,
        topic_filter: str = None,
        min_score: float = 0.0,
    ) -> list[dict]:
        """
        Search for documents semantically similar to the query.
        
        Args:
            query: Natural language search query
            n_results: Max results to return
            topic_filter: Optional topic to filter by
            min_score: Minimum similarity score (0-1)
        
        Returns:
            List of {text, source, score, metadata} dicts
        """
        where_filter = None
        if topic_filter:
            where_filter = {"topic": topic_filter}

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
        )

        # Format results
        formatted = []
        for i in range(len(results["documents"][0])):
            # ChromaDB returns distances, convert to similarity
            distance = results["distances"][0][i]
            # For cosine distance: similarity = 1 - distance
            # ChromaDB's cosine distance ranges from 0 (identical) to 2 (opposite)
            similarity = 1 - (distance / 2)

            if similarity >= min_score:
                formatted.append({
                    "text": results["documents"][0][i],
                    "score": round(similarity, 4),
                    "source": results["metadatas"][0][i]["source"],
                    "topic": results["metadatas"][0][i]["topic"],
                    "chunk": results["metadatas"][0][i]["chunk_index"],
                    "id": results["ids"][0][i],
                })

        return formatted

    def get_stats(self) -> dict:
        """Return index statistics."""
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection.name,
        }


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🔍 Document Search Engine                   ║")
    print("║  MODULE 2 PROJECT                            ║")
    print("║  Powered by ChromaDB + OpenAI Embeddings     ║")
    print("╚══════════════════════════════════════════════╝\n")

    # Create engine
    engine = DocumentSearchEngine(collection_name="tech_knowledge")

    # ── Add sample documents ──
    print("\n  📥 Indexing documents...\n")

    engine.add_document(
        text=(
            "Spring Boot is a framework built on top of Spring Framework that simplifies "
            "the creation of production-ready applications. It provides auto-configuration, "
            "embedded servers, and opinionated defaults. Spring Boot applications can be "
            "packaged as JAR files and run with 'java -jar'. The main annotation is "
            "@SpringBootApplication which combines @Configuration, @EnableAutoConfiguration, "
            "and @ComponentScan. Spring Boot Actuator provides health checks and metrics "
            "for production monitoring."
        ),
        source="spring-boot-guide",
        topic="spring",
    )

    engine.add_document(
        text=(
            "Apache Kafka is a distributed event streaming platform. It uses topics to "
            "organize messages and partitions for parallelism. Producers send messages to "
            "topics, and consumers read from them using consumer groups. Each consumer in a "
            "group reads from different partitions, enabling horizontal scaling. Kafka "
            "guarantees ordering within a partition but not across partitions. "
            "Key concepts include: offset (position in partition), retention (how long "
            "messages are stored), and replication (fault tolerance across brokers)."
        ),
        source="kafka-handbook",
        topic="messaging",
    )

    engine.add_document(
        text=(
            "Docker containers provide lightweight virtualization by sharing the host OS "
            "kernel. A Dockerfile defines the build steps: FROM base image, COPY files, "
            "RUN commands, and EXPOSE ports. Docker Compose orchestrates multi-container "
            "applications using a YAML file. Best practices: use multi-stage builds to "
            "reduce image size, don't run as root, use .dockerignore, and scan for "
            "vulnerabilities with tools like Trivy."
        ),
        source="docker-best-practices",
        topic="devops",
    )

    engine.add_document(
        text=(
            "PostgreSQL performance optimization starts with proper indexing. B-tree indexes "
            "are default and work for equality and range queries. GIN indexes are optimal for "
            "full-text search and JSONB queries. Use EXPLAIN ANALYZE to understand query plans. "
            "Connection pooling with PgBouncer or HikariCP reduces connection overhead. "
            "Partitioning large tables by date or range improves query performance. "
            "Vacuum and analyze should run regularly to maintain statistics."
        ),
        source="postgres-performance",
        topic="database",
    )

    engine.add_document(
        text=(
            "Microservice resilience patterns prevent cascade failures. Circuit Breaker "
            "(Resilience4j) stops calling a failing service after threshold errors. "
            "Retry pattern automatically retries failed requests with exponential backoff. "
            "Bulkhead pattern isolates resources to prevent one failing service from "
            "consuming all threads. Timeout pattern ensures requests don't hang indefinitely. "
            "Fallback provides default responses when the primary service is unavailable."
        ),
        source="microservices-patterns",
        topic="architecture",
    )

    # ── Show stats ──
    stats = engine.get_stats()
    print(f"\n  📊 Index stats: {stats['total_documents']} chunks indexed\n")

    # ── Run searches ──
    searches = [
        {"query": "How to make my database queries faster?", "topic": None},
        {"query": "What happens when a microservice goes down?", "topic": None},
        {"query": "How to deploy a Java application?", "topic": None},
        {"query": "parallel message processing", "topic": "messaging"},
        {"query": "container security best practices", "topic": "devops"},
    ]

    for search in searches:
        query = search["query"]
        topic = search["topic"]

        print(f"  {'═'*55}")
        filter_text = f" [topic={topic}]" if topic else ""
        print(f"  🔍 Query: '{query}'{filter_text}")
        print(f"  {'─'*55}")

        results = engine.search(query, n_results=3, topic_filter=topic)

        if not results:
            print(f"    No results found.")
        else:
            for i, r in enumerate(results, 1):
                print(f"    {i}. [{r['score']:.3f}] 📄 {r['source']} ({r['topic']})")
                # Show first 100 chars of matching text
                text_preview = r["text"][:100].replace("\n", " ")
                print(f"       \"{text_preview}...\"")
        print()

    # ── Interactive search (optional) ──
    print(f"  {'═'*55}")
    print(f"  💡 Try the interactive search!")
    print(f"  Type a question, or 'quit' to exit.\n")

    while True:
        try:
            user_query = input("  🔍 Search: ").strip()
            if user_query.lower() in ("quit", "exit", "q"):
                break
            if not user_query:
                continue

            results = engine.search(user_query, n_results=3)
            if not results:
                print("    No results found.\n")
            else:
                for i, r in enumerate(results, 1):
                    print(f"    {i}. [{r['score']:.3f}] 📄 {r['source']}")
                    text_preview = r["text"][:120].replace("\n", " ")
                    print(f"       \"{text_preview}...\"")
                print()
        except (KeyboardInterrupt, EOFError):
            break

    print("\n  👋 Search engine stopped.\n")


if __name__ == "__main__":
    main()
