"""
MODULE 2 — Example 1: Embeddings Basics
=========================================
Generate embeddings, visualize them, and understand their properties.

SETUP:
  pip install openai python-dotenv numpy
  OPENAI_API_KEY in .env

RUN:
  python 01_embeddings_basics.py

KEY LESSON:
  Embeddings convert text to numbers that capture MEANING.
  Similar meanings → similar numbers → nearby in vector space.
"""

import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """
    Generate an embedding for a single text.
    
    OpenAI models:
      text-embedding-3-small: 1536 dims, $0.02/1M tokens (cheaper, good enough)
      text-embedding-3-large: 3072 dims, $0.13/1M tokens (better quality)
    
    Java Analogy: Like calling a REST API that returns a float[1536].
    """
    response = client.embeddings.create(
        input=text,
        model=model,
    )
    return response.data[0].embedding


def get_embeddings_batch(texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    """
    Generate embeddings for multiple texts in one API call.
    ALWAYS use batch when possible — faster and same cost.
    """
    response = client.embeddings.create(
        input=texts,
        model=model,
    )
    return [item.embedding for item in response.data]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Formula: cos(θ) = (A · B) / (|A| × |B|)
    
    Returns value between -1 and 1:
      1.0  = identical meaning
      0.0  = unrelated
      -1.0 = opposite meaning
    """
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ──────────────────────────────────────────────────────
def demo_basic_embeddings():
    """Show what embeddings look like."""
    print("=" * 60)
    print("DEMO 1: What Do Embeddings Look Like?")
    print("=" * 60)

    text = "Spring Boot simplifies Java web development"
    embedding = get_embedding(text)

    print(f"\n  Text: \"{text}\"")
    print(f"  Dimensions: {len(embedding)}")
    print(f"  First 10 values: {[round(v, 4) for v in embedding[:10]]}")
    print(f"  Min value: {min(embedding):.4f}")
    print(f"  Max value: {max(embedding):.4f}")
    print(f"  Magnitude: {np.linalg.norm(embedding):.4f}")
    print(f"  (OpenAI embeddings are normalized, so magnitude ≈ 1.0)")


def demo_similarity():
    """Show that similar texts have similar embeddings."""
    print("\n" + "=" * 60)
    print("DEMO 2: Semantic Similarity")
    print("=" * 60)

    # Groups of related sentences
    sentences = [
        # Group 1: Java errors
        "NullPointerException in Java",
        "How to handle null references in Java",
        "Debugging null pointer errors",
        # Group 2: Cooking
        "How to bake chocolate cake",
        "Best recipe for brownies",
        "Chocolate dessert preparation",
        # Group 3: Machine Learning
        "Training a neural network",
        "Deep learning model optimization",
        "Machine learning gradient descent",
    ]

    print("\n  Generating embeddings for all sentences...")
    embeddings = get_embeddings_batch(sentences)

    # Compute all pairwise similarities
    print("\n  Pairwise Cosine Similarities:")
    print(f"  {'':40s}", end="")
    for i in range(len(sentences)):
        print(f" S{i+1:d}   ", end="")
    print()

    for i, sent_i in enumerate(sentences):
        label = sent_i[:38] + ".." if len(sent_i) > 40 else sent_i
        print(f"  S{i+1} {label:38s}", end="")
        for j in range(len(sentences)):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            # Color-code: high sim in same group
            marker = "██" if sim > 0.7 and i != j else "  "
            print(f" {sim:.2f}{marker}", end="")
        print()

    print("\n  ██ = High similarity (>0.7)")
    print("  Notice: sentences in the same topic cluster together!")


def demo_semantic_search():
    """
    Simple semantic search using embeddings.
    This is the FOUNDATION of RAG and vector databases.
    """
    print("\n" + "=" * 60)
    print("DEMO 3: Simple Semantic Search")
    print("=" * 60)

    # Our "document database"
    documents = [
        "Spring Boot auto-configuration scans classpath for beans",
        "Kafka consumer groups enable parallel message processing",
        "JPA repository interface generates SQL queries automatically",
        "Docker containers package applications with their dependencies",
        "Redis caching improves API response times significantly",
        "Kubernetes orchestrates container deployment and scaling",
        "REST API versioning strategies for backward compatibility",
        "Circuit breaker pattern prevents cascade failures in microservices",
        "OAuth2 JWT tokens for stateless authentication in APIs",
        "PostgreSQL indexing strategies for query performance optimization",
    ]

    # Generate embeddings for all documents (in production, do this once and store)
    print("\n  Indexing 10 documents...")
    doc_embeddings = get_embeddings_batch(documents)

    # Search queries
    queries = [
        "How to speed up my database queries?",
        "My microservice keeps timing out when another service is down",
        "How to run my app in containers?",
    ]

    for query in queries:
        print(f"\n  🔍 Query: \"{query}\"")
        query_embedding = get_embedding(query)

        # Compute similarity with all documents
        similarities = [
            (doc, cosine_similarity(query_embedding, doc_emb))
            for doc, doc_emb in zip(documents, doc_embeddings)
        ]

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Show top 3
        print(f"     Top 3 results:")
        for rank, (doc, sim) in enumerate(similarities[:3], 1):
            print(f"     {rank}. [{sim:.3f}] {doc}")


# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 MODULE 2: Embeddings Basics\n")

    demo_basic_embeddings()
    demo_similarity()
    demo_semantic_search()

    print("\n✅ Key insights:")
    print("   1. Embeddings capture MEANING as numbers")
    print("   2. Similar meanings → high cosine similarity")
    print("   3. Semantic search finds results keyword search would miss")
    print("   4. This is the foundation of RAG (Module 3)!\n")
