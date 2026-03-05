"""
MODULE 2 — Example 4: FAISS Introduction
==========================================
Facebook AI Similarity Search — the speed demon of vector search.

FAISS is a library, not a database. It's blazing fast but minimal:
no metadata, no auto-embedding, no persistence by default.
Think of it as a raw data structure for vector search.

SETUP:
  pip install faiss-cpu numpy openai python-dotenv

RUN:
  python 04_faiss_intro.py

JAVA ANALOGY:
  FAISS is like a raw HashMap — extremely fast at one thing (lookup),
  you build everything else around it.
"""

import os
import time
import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ══════════════════════════════════════════════════════
# PART 1: FAISS Fundamentals
# ══════════════════════════════════════════════════════

def demo_flat_index():
    """
    IndexFlatL2: Exact nearest neighbor search.
    Brute force, 100% accurate, but slow for large datasets.
    
    Use this for:
    - Small datasets (<100K vectors)
    - When accuracy is critical
    - Benchmarking other indexes
    """
    print("=" * 60)
    print("PART 1: FAISS Flat Index (Exact Search)")
    print("=" * 60)

    dimension = 128  # Vector dimension (small for demo)
    n_vectors = 10000

    # Generate random normalized vectors
    np.random.seed(42)
    database = np.random.randn(n_vectors, dimension).astype(np.float32)
    faiss.normalize_L2(database)  # Normalize in-place

    # Create index — IndexFlatIP = dot product (cosine sim for normalized vectors)
    index = faiss.IndexFlatIP(dimension)

    # Add vectors to index
    index.add(database)
    print(f"\n  Index type: Flat (exact search)")
    print(f"  Vectors: {index.ntotal}")
    print(f"  Dimensions: {dimension}")

    # Search
    query = np.random.randn(1, dimension).astype(np.float32)
    faiss.normalize_L2(query)

    k = 5  # Top 5 results
    start = time.time()
    scores, indices = index.search(query, k)
    elapsed = time.time() - start

    print(f"\n  Search time: {elapsed*1000:.2f}ms")
    print(f"  Top {k} results:")
    for i in range(k):
        print(f"    {i+1}. Index: {indices[0][i]}, Score: {scores[0][i]:.4f}")


def demo_ivf_index():
    """
    IndexIVFFlat: Approximate search using clustering.
    Much faster than flat for large datasets.
    
    How it works:
    1. Cluster all vectors into n_lists groups (using k-means)
    2. At search time, only search the nearest n_probe clusters
    3. Trade-off: n_probe ↑ = accuracy ↑ but speed ↓
    """
    print("\n" + "=" * 60)
    print("PART 2: FAISS IVF Index (Approximate Search)")
    print("=" * 60)

    dimension = 256
    n_vectors = 100_000

    # Generate data
    np.random.seed(42)
    database = np.random.randn(n_vectors, dimension).astype(np.float32)
    faiss.normalize_L2(database)

    # IVF index requires a "quantizer" (the underlying index for centroids)
    n_lists = 100  # Number of clusters (rule of thumb: sqrt(n_vectors))
    quantizer = faiss.IndexFlatIP(dimension)
    index = faiss.IndexIVFFlat(quantizer, dimension, n_lists)

    # IVF must be trained before use (learns the cluster centers)
    print(f"\n  Training IVF index on {n_vectors} vectors...")
    index.train(database)  # Learn cluster centers
    index.add(database)    # Add vectors to clusters
    print(f"  Done! Clusters: {n_lists}")

    # Compare different n_probe values
    query = np.random.randn(1, dimension).astype(np.float32)
    faiss.normalize_L2(query)

    print(f"\n  n_probe comparison (accuracy vs speed trade-off):")
    print(f"  {'n_probe':<10} {'Time (ms)':<12} {'Top-1 Score'}")
    print(f"  {'─'*10} {'─'*12} {'─'*12}")

    for n_probe in [1, 5, 10, 50, 100]:
        index.nprobe = n_probe

        start = time.time()
        scores, indices = index.search(query, 5)
        elapsed = time.time() - start

        print(f"  {n_probe:<10} {elapsed*1000:<12.2f} {scores[0][0]:.4f}")

    print(f"\n  Rule of thumb: n_probe = n_lists/10 to n_lists/5")


def demo_performance_comparison():
    """
    Compare Flat vs IVF performance at scale.
    """
    print("\n" + "=" * 60)
    print("PART 3: Flat vs IVF Performance")
    print("=" * 60)

    dimension = 1536  # Real OpenAI embedding dimension
    n_vectors = 50_000

    np.random.seed(42)
    database = np.random.randn(n_vectors, dimension).astype(np.float32)
    faiss.normalize_L2(database)

    query = np.random.randn(1, dimension).astype(np.float32)
    faiss.normalize_L2(query)

    # Flat index
    flat_index = faiss.IndexFlatIP(dimension)
    flat_index.add(database)

    start = time.time()
    flat_scores, flat_indices = flat_index.search(query, 10)
    flat_time = time.time() - start

    # IVF index
    n_lists = int(np.sqrt(n_vectors))
    quantizer = faiss.IndexFlatIP(dimension)
    ivf_index = faiss.IndexIVFFlat(quantizer, dimension, n_lists)
    ivf_index.train(database)
    ivf_index.add(database)
    ivf_index.nprobe = 10

    start = time.time()
    ivf_scores, ivf_indices = ivf_index.search(query, 10)
    ivf_time = time.time() - start

    # Compare
    print(f"\n  Dataset: {n_vectors} vectors × {dimension} dimensions\n")
    print(f"  {'Metric':<25} {'Flat (Exact)':<15} {'IVF (Approx)'}")
    print(f"  {'─'*25} {'─'*15} {'─'*15}")
    print(f"  {'Search time':<25} {flat_time*1000:<15.2f} {ivf_time*1000:.2f}ms")
    print(f"  {'Top-1 score':<25} {flat_scores[0][0]:<15.4f} {ivf_scores[0][0]:.4f}")
    print(f"  {'Speedup':<25} {'1x':<15} {flat_time/ivf_time:.1f}x")

    # Check if IVF found the same top result
    same_top = flat_indices[0][0] == ivf_indices[0][0]
    print(f"  {'Same top-1 result':<25} {'—':<15} {'✅ Yes' if same_top else '❌ No'}")


def demo_save_load():
    """
    Save and load FAISS indexes from disk.
    
    Java Analogy: Like serializing a HashMap to file.
    """
    print("\n" + "=" * 60)
    print("PART 4: Save & Load Index")
    print("=" * 60)

    import tempfile

    dimension = 128
    index = faiss.IndexFlatIP(dimension)
    data = np.random.randn(1000, dimension).astype(np.float32)
    faiss.normalize_L2(data)
    index.add(data)

    # Save to disk
    filepath = os.path.join(tempfile.gettempdir(), "demo_index.faiss")
    faiss.write_index(index, filepath)
    print(f"\n  Saved index ({index.ntotal} vectors) to: {filepath}")

    # Load from disk
    loaded_index = faiss.read_index(filepath)
    print(f"  Loaded index: {loaded_index.ntotal} vectors")

    # Verify search works
    query = np.random.randn(1, dimension).astype(np.float32)
    faiss.normalize_L2(query)
    scores, indices = loaded_index.search(query, 3)
    print(f"  Search works! Top result: index={indices[0][0]}, score={scores[0][0]:.4f}")

    # Cleanup
    os.remove(filepath)


def demo_with_real_embeddings():
    """
    FAISS with actual OpenAI embeddings.
    Unlike ChromaDB, you must generate embeddings yourself.
    """
    print("\n" + "=" * 60)
    print("PART 5: FAISS + OpenAI Embeddings")
    print("=" * 60)

    documents = [
        "Spring Boot autoconfiguration scans for beans on classpath",
        "Kafka uses consumer groups for parallel message processing",
        "JPA generates SQL from repository method names",
        "Docker containers isolate applications in lightweight environments",
        "Redis serves as an in-memory cache for fast data access",
    ]

    # Step 1: Generate embeddings with OpenAI
    print("\n  Generating OpenAI embeddings...")
    response = openai_client.embeddings.create(
        input=documents,
        model="text-embedding-3-small",
    )
    embeddings = np.array([item.embedding for item in response.data], dtype=np.float32)
    dimension = embeddings.shape[1]  # 1536

    # Step 2: Create FAISS index
    index = faiss.IndexFlatIP(dimension)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    print(f"  Indexed {index.ntotal} documents ({dimension} dimensions)")

    # Step 3: Search
    query_text = "How to cache data for better performance?"
    print(f"\n  🔍 Query: '{query_text}'")

    query_response = openai_client.embeddings.create(
        input=[query_text],
        model="text-embedding-3-small",
    )
    query_vec = np.array([query_response.data[0].embedding], dtype=np.float32)
    faiss.normalize_L2(query_vec)

    scores, indices = index.search(query_vec, 3)

    print(f"  Top 3 results:")
    for i in range(3):
        doc_idx = indices[0][i]
        score = scores[0][i]
        print(f"    {i+1}. [{score:.4f}] {documents[doc_idx]}")

    # NOTE: FAISS doesn't store documents or metadata!
    # You must maintain a separate mapping: index_id → document
    print(f"\n  ⚠️  Note: FAISS only stores vectors, not documents!")
    print(f"     You need a separate dict/DB: {{faiss_id: document_text}}")


# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 MODULE 2: FAISS Complete Guide\n")

    demo_flat_index()
    demo_ivf_index()
    demo_performance_comparison()
    demo_save_load()
    demo_with_real_embeddings()

    print("\n✅ FAISS Summary:")
    print("   • Blazing fast — C++ core, optional GPU support")
    print("   • Flat index = exact but slow, IVF = approximate but fast")
    print("   • No metadata, no persistence by default (DIY)")
    print("   • Best for: high-performance research, when you need speed")
    print("   • For production apps, combine FAISS with a metadata store\n")
