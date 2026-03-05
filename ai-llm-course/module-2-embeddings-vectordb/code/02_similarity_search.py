"""
MODULE 2 — Example 2: Similarity Search Deep Dive
====================================================
Implements cosine similarity from scratch and shows how
similarity search works at different scales.

NO API KEY NEEDED for parts 1-2 (uses numpy only).
API KEY needed for part 3 (OpenAI embeddings).

SETUP:
  pip install numpy

RUN:
  python 02_similarity_search.py
"""

import numpy as np
import time


# ══════════════════════════════════════════════════════
# PART 1: Cosine Similarity from Scratch
# ══════════════════════════════════════════════════════

def cosine_similarity_manual(a, b):
    """
    Cosine similarity implemented step by step.
    
    Formula: cos(θ) = (A · B) / (|A| × |B|)
    
    Step 1: Dot product (A · B) = sum of element-wise multiplication
    Step 2: Magnitude |A| = sqrt(sum of squares)
    Step 3: Divide dot product by product of magnitudes
    """
    # Step 1: Dot product
    dot_product = sum(ai * bi for ai, bi in zip(a, b))
    
    # Step 2: Magnitudes
    magnitude_a = sum(ai ** 2 for ai in a) ** 0.5
    magnitude_b = sum(bi ** 2 for bi in b) ** 0.5
    
    # Step 3: Divide
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    return dot_product / (magnitude_a * magnitude_b)


def euclidean_distance(a, b):
    """Euclidean distance = straight-line distance between two points."""
    return sum((ai - bi) ** 2 for ai, bi in zip(a, b)) ** 0.5


def dot_product_similarity(a, b):
    """Simple dot product — works when vectors are normalized."""
    return sum(ai * bi for ai, bi in zip(a, b))


def demo_metrics():
    """Compare different similarity metrics."""
    print("=" * 60)
    print("PART 1: Similarity Metrics Compared")
    print("=" * 60)
    
    # Simple 3D vectors for intuition
    vectors = {
        "A (Java)":    [0.9, 0.1, 0.0],
        "B (Spring)":  [0.85, 0.15, 0.05],   # Similar to A
        "C (Cooking)": [0.1, 0.0, 0.95],     # Very different from A
        "D (Python)":  [0.7, 0.3, 0.0],      # Somewhat similar to A
    }
    
    base = vectors["A (Java)"]
    print(f"\n  Comparing all vectors to A (Java) = {base}:\n")
    print(f"  {'Vector':<15} {'Values':<25} {'Cosine':<10} {'Euclidean':<12} {'Dot Product'}")
    print(f"  {'─'*15} {'─'*25} {'─'*10} {'─'*12} {'─'*12}")
    
    for name, vec in vectors.items():
        cos = cosine_similarity_manual(base, vec)
        euc = euclidean_distance(base, vec)
        dot = dot_product_similarity(base, vec)
        print(f"  {name:<15} {str(vec):<25} {cos:>7.4f}   {euc:>8.4f}     {dot:>8.4f}")
    
    print(f"\n  Interpretation:")
    print(f"  • Cosine: 1.0=identical, 0.0=unrelated (angle-based)")
    print(f"  • Euclidean: 0.0=identical, ↑=more different (distance-based)")
    print(f"  • Dot Product: higher=more similar (magnitude matters)")


# ══════════════════════════════════════════════════════
# PART 2: Brute Force vs Optimized Search
# ══════════════════════════════════════════════════════

def demo_search_performance():
    """
    Shows why brute force doesn't scale and why we need
    approximate nearest neighbor (ANN) algorithms.
    """
    print("\n" + "=" * 60)
    print("PART 2: Search Performance at Scale")
    print("=" * 60)
    
    dimensions = 1536  # Same as OpenAI embeddings
    
    for n_vectors in [1_000, 10_000, 100_000]:
        # Generate random vectors (simulating a vector database)
        database = np.random.randn(n_vectors, dimensions).astype(np.float32)
        # Normalize (like OpenAI embeddings)
        norms = np.linalg.norm(database, axis=1, keepdims=True)
        database = database / norms
        
        # Random query vector
        query = np.random.randn(dimensions).astype(np.float32)
        query = query / np.linalg.norm(query)
        
        # Brute force search
        start = time.time()
        similarities = np.dot(database, query)  # Vectorized dot product
        top_k_indices = np.argsort(similarities)[-5:][::-1]  # Top 5
        elapsed = time.time() - start
        
        print(f"\n  {n_vectors:>8,} vectors × {dimensions} dims:")
        print(f"    Brute force search: {elapsed*1000:.1f}ms")
        print(f"    Top match similarity: {similarities[top_k_indices[0]]:.4f}")
        
        # Estimate for larger scales
        if n_vectors == 100_000:
            est_1m = elapsed * 10
            est_10m = elapsed * 100
            print(f"\n    Estimated at    1M vectors: {est_1m*1000:.0f}ms")
            print(f"    Estimated at   10M vectors: {est_10m*1000:.0f}ms")
            print(f"    → This is why we need ANN algorithms!")
            print(f"    → HNSW/IVF reduce this to ~1-5ms regardless of size")


# ══════════════════════════════════════════════════════
# PART 3: Practical Similarity Search Patterns
# ══════════════════════════════════════════════════════

def demo_search_patterns():
    """Common patterns for production similarity search."""
    print("\n" + "=" * 60)
    print("PART 3: Search Patterns")
    print("=" * 60)
    
    # Simulate a document database with random embeddings
    np.random.seed(42)
    n_docs = 1000
    dims = 1536
    
    # Generate and normalize
    doc_embeddings = np.random.randn(n_docs, dims).astype(np.float32)
    doc_embeddings = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
    
    query = np.random.randn(dims).astype(np.float32)
    query = query / np.linalg.norm(query)
    
    # Pattern 1: Top-K search
    print("\n  Pattern 1: Top-K Search (most common)")
    similarities = np.dot(doc_embeddings, query)
    top_k = 5
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    print(f"    Top {top_k} results:")
    for rank, idx in enumerate(top_indices, 1):
        print(f"      {rank}. Doc #{idx} (similarity: {similarities[idx]:.4f})")
    
    # Pattern 2: Threshold search
    print("\n  Pattern 2: Threshold Search (all above 0.3)")
    threshold = 0.3
    above_threshold = np.where(similarities > threshold)[0]
    print(f"    Found {len(above_threshold)} docs above {threshold}")
    print(f"    (In real data, threshold 0.7+ gives relevant results)")
    
    # Pattern 3: Top-K with score filtering
    print("\n  Pattern 3: Top-K + Minimum Score (production pattern)")
    min_score = 0.2
    top_k = 10
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    filtered = [(idx, similarities[idx]) for idx in top_indices 
                if similarities[idx] >= min_score]
    print(f"    Requested top {top_k}, got {len(filtered)} above min score {min_score}")
    
    # Pattern 4: Diversity search (MMR - Maximal Marginal Relevance)
    print("\n  Pattern 4: Diverse Results (MMR)")
    print("    Standard:  All top results might be about the same subtopic")
    print("    MMR:       Balances relevance AND diversity")
    print("    Formula:   MMR = λ·sim(q,d) - (1-λ)·max(sim(d,d_selected))")
    print("    λ=1.0:     Pure relevance")
    print("    λ=0.0:     Pure diversity")
    print("    λ=0.7:     Good production default")


# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 MODULE 2: Similarity Search Deep Dive\n")
    
    demo_metrics()
    demo_search_performance()
    demo_search_patterns()
    
    print("\n✅ Key takeaways:")
    print("   1. Cosine similarity is the default for text embeddings")
    print("   2. Brute force is O(N) — doesn't scale past ~100K vectors")
    print("   3. ANN algorithms (HNSW, IVF) make search fast at any scale")
    print("   4. Use Top-K + minimum score for production search")
    print("   5. MMR gives diverse results (avoids redundant matches)\n")
