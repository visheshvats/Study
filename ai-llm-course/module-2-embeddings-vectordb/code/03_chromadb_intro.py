"""
MODULE 2 — Example 3: ChromaDB Introduction
=============================================
Complete guide to using ChromaDB — the easiest vector database.

ChromaDB is like H2 for vectors: embedded, zero-config, perfect for
learning and prototyping. It's also production-viable for <1M vectors.

SETUP:
  pip install chromadb openai python-dotenv

RUN:
  python 03_chromadb_intro.py

KEY CONCEPT:
  ChromaDB can auto-generate embeddings OR accept your own.
  For learning, we'll use OpenAI embeddings for quality and
  ChromaDB's built-in function for convenience.
"""

import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ══════════════════════════════════════════════════════
# PART 1: ChromaDB Fundamentals
# ══════════════════════════════════════════════════════

def demo_basics():
    """
    Basic ChromaDB operations: create, add, query.
    
    ChromaDB concepts mapped to SQL:
      Collection → Table
      Document   → Row (text column)
      Embedding  → Row (vector column)
      Metadata   → Row (additional columns)
      ID         → Primary key
    """
    print("=" * 60)
    print("PART 1: ChromaDB Basics")
    print("=" * 60)

    # Create an in-memory client (data lost when script ends)
    # For persistence, use: chromadb.PersistentClient(path="./chroma_db")
    client = chromadb.Client()

    # Create a collection (like CREATE TABLE)
    # ChromaDB uses its own default embedding model (all-MiniLM-L6-v2)
    collection = client.create_collection(
        name="java_docs",
        metadata={"description": "Java documentation for semantic search"}
    )

    print(f"\n  Created collection: '{collection.name}'")

    # ── ADD DOCUMENTS ──
    # ChromaDB auto-generates embeddings if you provide documents!
    collection.add(
        documents=[
            "NullPointerException occurs when you call a method on a null reference",
            "Spring Boot auto-configuration automatically configures beans based on classpath",
            "HashMap is not thread-safe, use ConcurrentHashMap for multi-threaded access",
            "JPA @Entity annotation marks a class as a database entity",
            "Kafka consumer groups allow parallel processing of topic partitions",
            "Docker containers package application code with all dependencies",
            "REST API should use proper HTTP status codes: 200, 201, 404, 500",
            "Circuit breaker pattern prevents cascade failures between microservices",
            "Redis can be used as a cache layer to reduce database load",
            "PostgreSQL supports JSONB for storing and querying JSON documents",
        ],
        metadatas=[
            {"topic": "java-core", "difficulty": "beginner"},
            {"topic": "spring-boot", "difficulty": "intermediate"},
            {"topic": "java-core", "difficulty": "intermediate"},
            {"topic": "spring-data", "difficulty": "beginner"},
            {"topic": "kafka", "difficulty": "advanced"},
            {"topic": "devops", "difficulty": "beginner"},
            {"topic": "rest-api", "difficulty": "beginner"},
            {"topic": "microservices", "difficulty": "advanced"},
            {"topic": "caching", "difficulty": "intermediate"},
            {"topic": "database", "difficulty": "intermediate"},
        ],
        ids=[f"doc_{i}" for i in range(10)],  # Unique IDs required
    )

    print(f"  Added 10 documents with metadata")
    print(f"  Collection size: {collection.count()}")

    # ── QUERY ──
    # Query by text — ChromaDB embeds the query and finds similar docs
    results = collection.query(
        query_texts=["How to avoid null pointer errors in Java?"],
        n_results=3,  # Top 3
    )

    print(f"\n  🔍 Query: 'How to avoid null pointer errors in Java?'")
    print(f"  Top 3 results:")
    for i in range(len(results["documents"][0])):
        doc = results["documents"][0][i]
        dist = results["distances"][0][i]
        meta = results["metadatas"][0][i]
        print(f"    {i+1}. [{dist:.4f}] ({meta['topic']}) {doc[:70]}")

    return client


def demo_metadata_filtering():
    """
    Combine vector search with metadata filtering.
    
    This is ESSENTIAL for production — semantic search alone
    isn't enough. You need to filter by category, date, user, etc.
    
    Java Analogy: Like adding WHERE clauses to your JPA queries.
    """
    print("\n" + "=" * 60)
    print("PART 2: Metadata Filtering")
    print("=" * 60)

    client = chromadb.Client()
    collection = client.create_collection(name="tech_docs")

    # Add documents with rich metadata
    docs = [
        {"text": "Spring Boot 3 requires Java 17 minimum",
         "meta": {"framework": "spring", "version": "3.0", "year": 2023}},
        {"text": "Spring Boot 2 supports Java 8 through 17",
         "meta": {"framework": "spring", "version": "2.7", "year": 2022}},
        {"text": "Django 4 supports Python 3.8 and above",
         "meta": {"framework": "django", "version": "4.0", "year": 2022}},
        {"text": "React 18 introduced concurrent rendering features",
         "meta": {"framework": "react", "version": "18", "year": 2022}},
        {"text": "Spring Security OAuth2 resource server configuration",
         "meta": {"framework": "spring", "version": "3.0", "year": 2023}},
        {"text": "Kubernetes deployment YAML configuration guide",
         "meta": {"framework": "k8s", "version": "1.28", "year": 2023}},
    ]

    collection.add(
        documents=[d["text"] for d in docs],
        metadatas=[d["meta"] for d in docs],
        ids=[f"doc_{i}" for i in range(len(docs))],
    )

    # Query 1: Semantic search only
    print("\n  Query 1: 'Java version requirements' (no filter)")
    results = collection.query(
        query_texts=["Java version requirements"],
        n_results=3,
    )
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        print(f"    {i+1}. ({meta['framework']}) {doc}")

    # Query 2: Semantic search + metadata filter
    print("\n  Query 2: Same query, filtered to Spring only")
    results = collection.query(
        query_texts=["Java version requirements"],
        n_results=3,
        where={"framework": "spring"},  # SQL: WHERE framework = 'spring'
    )
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        print(f"    {i+1}. ({meta['framework']} {meta['version']}) {doc}")

    # Query 3: Complex filter
    print("\n  Query 3: 'configuration' + year >= 2023")
    results = collection.query(
        query_texts=["configuration guide"],
        n_results=3,
        where={"year": {"$gte": 2023}},  # SQL: WHERE year >= 2023
    )
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        print(f"    {i+1}. ({meta['framework']}, {meta['year']}) {doc}")

    # Available filter operators
    print("\n  📋 ChromaDB Filter Operators:")
    print("    $eq   : equal (default)")
    print("    $ne   : not equal")
    print("    $gt   : greater than")
    print("    $gte  : greater than or equal")
    print("    $lt   : less than")
    print("    $lte  : less than or equal")
    print("    $in   : in list")
    print("    $nin  : not in list")
    print("    $and  : logical AND (combine filters)")
    print("    $or   : logical OR")


def demo_persistence():
    """
    Persistent ChromaDB — data survives restarts.
    
    Java Analogy: Switching from H2 in-memory to H2 file-based.
    """
    print("\n" + "=" * 60)
    print("PART 3: Persistence")
    print("=" * 60)

    import tempfile
    import os

    # Use temp dir for demo (use a real path in production)
    persist_dir = os.path.join(tempfile.gettempdir(), "chroma_demo")

    # Create persistent client
    client = chromadb.PersistentClient(path=persist_dir)

    # Get or create collection
    collection = client.get_or_create_collection(name="persistent_docs")

    # Only add if empty
    if collection.count() == 0:
        collection.add(
            documents=["This data survives restarts!"],
            ids=["persistent_1"],
        )
        print(f"\n  Added document. Collection size: {collection.count()}")
    else:
        print(f"\n  Collection already has {collection.count()} documents (loaded from disk)")

    print(f"  Data stored at: {persist_dir}")
    print(f"  In production, use a stable path like: ./data/chroma_db")


def demo_update_delete():
    """CRUD operations on collections."""
    print("\n" + "=" * 60)
    print("PART 4: Update & Delete")
    print("=" * 60)

    client = chromadb.Client()
    collection = client.create_collection(name="crud_demo")

    # Add
    collection.add(
        documents=["Spring Boot version 2.7"],
        ids=["doc_1"],
        metadatas=[{"version": "2.7"}],
    )
    print(f"\n  Added: 'Spring Boot version 2.7'")

    # Update (upsert)
    collection.update(
        documents=["Spring Boot version 3.2 with Java 21"],
        ids=["doc_1"],
        metadatas=[{"version": "3.2"}],
    )
    print(f"  Updated: 'Spring Boot version 3.2 with Java 21'")

    # Verify
    result = collection.get(ids=["doc_1"])
    print(f"  Current: {result['documents'][0]} (v{result['metadatas'][0]['version']})")

    # Delete
    collection.delete(ids=["doc_1"])
    print(f"  Deleted: doc_1")
    print(f"  Collection size: {collection.count()}")


def demo_with_openai_embeddings():
    """
    Use OpenAI embeddings instead of ChromaDB's default.
    OpenAI embeddings are higher quality but cost money.
    """
    print("\n" + "=" * 60)
    print("PART 5: ChromaDB + OpenAI Embeddings")
    print("=" * 60)

    # Custom embedding function for ChromaDB
    class OpenAIEmbeddings:
        """Adapter to use OpenAI embeddings with ChromaDB."""
        def __call__(self, input: list[str]) -> list[list[float]]:
            response = openai_client.embeddings.create(
                input=input,
                model="text-embedding-3-small",
            )
            return [item.embedding for item in response.data]

    client = chromadb.Client()
    collection = client.create_collection(
        name="openai_collection",
        embedding_function=OpenAIEmbeddings(),
    )

    # Add documents — ChromaDB will use OpenAI to embed them
    collection.add(
        documents=[
            "Dependency injection in Spring creates loosely coupled components",
            "Aspect-oriented programming handles cross-cutting concerns",
            "Spring WebFlux enables reactive non-blocking web applications",
        ],
        ids=["spring_1", "spring_2", "spring_3"],
    )

    # Query — also embedded with OpenAI
    results = collection.query(
        query_texts=["How to build reactive APIs?"],
        n_results=2,
    )

    print(f"\n  🔍 Query: 'How to build reactive APIs?'")
    for i, doc in enumerate(results["documents"][0]):
        dist = results["distances"][0][i]
        print(f"    {i+1}. [{dist:.4f}] {doc}")

    print(f"\n  ✅ OpenAI embeddings give better relevance than default model")


# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 MODULE 2: ChromaDB Complete Guide\n")

    demo_basics()
    demo_metadata_filtering()
    demo_persistence()
    demo_update_delete()
    demo_with_openai_embeddings()

    print("\n✅ ChromaDB Summary:")
    print("   • pip install chromadb → ready to use")
    print("   • Auto-embeds documents (or use custom embeddings)")
    print("   • Supports metadata filtering (WHERE clauses)")
    print("   • Persistent mode for data that survives restarts")
    print("   • Perfect for learning and RAG prototypes\n")
