#!/usr/bin/env python3
"""
Vector Embeddings — Spatial Distance & Cosine Similarity
=========================================================
Demonstrates how words are projected into a dense numeric coordinate space and
how spatial relationships encode semantic meaning.

Run:
    python vector_embeddings.py
"""

import math
from typing import Dict, List, Tuple

# ── Mock Embedding Table ────────────────────────────────────────────────────
# Each word is mapped to a 5-dimensional dense vector (hand-crafted to
# illustrate real clustering properties).
EMBEDDINGS: Dict[str, List[float]] = {
    # Food / fruit cluster
    "apple":      [ 0.92,  0.15,  0.03,  0.88,  0.10],
    "banana":     [ 0.89,  0.12,  0.05,  0.91,  0.08],
    "orange":     [ 0.87,  0.18,  0.07,  0.85,  0.12],
    "mango":      [ 0.90,  0.10,  0.04,  0.93,  0.06],
    # Technology cluster
    "computer":   [ 0.05,  0.93,  0.88,  0.07,  0.90],
    "software":   [ 0.08,  0.90,  0.91,  0.10,  0.87],
    "algorithm":  [ 0.10,  0.88,  0.85,  0.12,  0.85],
    "python":     [ 0.12,  0.87,  0.90,  0.09,  0.83],
    # Finance cluster
    "stock":      [ 0.20,  0.70,  0.15,  0.18,  0.75],
    "dividend":   [ 0.22,  0.68,  0.12,  0.20,  0.78],
    "portfolio":  [ 0.19,  0.72,  0.18,  0.16,  0.73],
    # Ambiguous — sits between clusters
    "apple_inc":  [ 0.15,  0.85,  0.80,  0.20,  0.82],
}


# ── Vector Operations ───────────────────────────────────────────────────────
def dot_product(a: List[float], b: List[float]) -> float:
    """Compute the dot product of two equal-length vectors."""
    return sum(x * y for x, y in zip(a, b))


def magnitude(v: List[float]) -> float:
    """Compute the L2 (Euclidean) norm of a vector."""
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Cosine similarity  =  (A · B) / (‖A‖ × ‖B‖)
    Returns a value in [-1, 1]; higher means more semantically aligned.
    """
    mag_a, mag_b = magnitude(a), magnitude(b)
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_product(a, b) / (mag_a * mag_b)


def euclidean_distance(a: List[float], b: List[float]) -> float:
    """Straight-line distance in n-dimensional space."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def manhattan_distance(a: List[float], b: List[float]) -> float:
    """City-block (L1) distance — sum of absolute coordinate deltas."""
    return sum(abs(x - y) for x, y in zip(a, b))


# ── Nearest Neighbour Search ────────────────────────────────────────────────
def find_nearest(
    query: str,
    embeddings: Dict[str, List[float]],
    top_k: int = 3,
    metric: str = "cosine",
) -> List[Tuple[str, float]]:
    """Return the top-k most similar words to *query* by chosen metric."""
    query_vec = embeddings[query]
    scores: List[Tuple[str, float]] = []
    for word, vec in embeddings.items():
        if word == query:
            continue
        if metric == "cosine":
            scores.append((word, cosine_similarity(query_vec, vec)))
        elif metric == "euclidean":
            scores.append((word, -euclidean_distance(query_vec, vec)))  # negate so higher = closer
        else:
            scores.append((word, -manhattan_distance(query_vec, vec)))
    scores.sort(key=lambda t: t[1], reverse=True)
    return scores[:top_k]


# ── Analogy via Vector Arithmetic ───────────────────────────────────────────
def vector_add(a: List[float], b: List[float]) -> List[float]:
    return [x + y for x, y in zip(a, b)]


def vector_sub(a: List[float], b: List[float]) -> List[float]:
    return [x - y for x, y in zip(a, b)]


def analogy(a: str, b: str, c: str, embeddings: Dict[str, List[float]]) -> List[Tuple[str, float]]:
    """
    Solve: A is to B as C is to ?
    result_vec ≈ vec(B) - vec(A) + vec(C)
    """
    result_vec = vector_add(vector_sub(embeddings[b], embeddings[a]), embeddings[c])
    scores = []
    for word, vec in embeddings.items():
        if word in {a, b, c}:
            continue
        scores.append((word, cosine_similarity(result_vec, vec)))
    scores.sort(key=lambda t: t[1], reverse=True)
    return scores[:3]


# ── Demo ────────────────────────────────────────────────────────────────────
def run_demo() -> None:
    print("=" * 72)
    print("VECTOR EMBEDDINGS — Spatial Similarity Demo")
    print("=" * 72)

    # 1. Pairwise similarities
    pairs = [
        ("apple", "banana"),
        ("apple", "computer"),
        ("apple", "apple_inc"),
        ("computer", "software"),
        ("stock", "dividend"),
        ("stock", "banana"),
    ]
    print("\n1. Pairwise Cosine Similarities:")
    print(f"   {'Word A':>12s}  {'Word B':>12s}  {'Cosine':>8s}  {'Euclid':>8s}")
    print("   " + "-" * 48)
    for a, b in pairs:
        cs = cosine_similarity(EMBEDDINGS[a], EMBEDDINGS[b])
        ed = euclidean_distance(EMBEDDINGS[a], EMBEDDINGS[b])
        print(f"   {a:>12s}  {b:>12s}  {cs:>8.4f}  {ed:>8.4f}")

    # 2. Nearest neighbours
    print("\n2. Nearest Neighbours (cosine):")
    for query in ["apple", "computer", "stock"]:
        neighbours = find_nearest(query, EMBEDDINGS, top_k=3)
        labels = ", ".join(f"{w} ({s:.4f})" for w, s in neighbours)
        print(f"   {query:>10s} → {labels}")

    # 3. Vector analogy
    print("\n3. Vector Analogy — apple:banana :: computer:?")
    results = analogy("apple", "banana", "computer", EMBEDDINGS)
    for word, score in results:
        print(f"   → {word:>12s}  (similarity {score:.4f})")

    # 4. Cluster visualization (text-based)
    print("\n4. Cluster Membership (intra-cluster avg cosine):")
    clusters = {
        "Fruit":      ["apple", "banana", "orange", "mango"],
        "Technology":  ["computer", "software", "algorithm", "python"],
        "Finance":     ["stock", "dividend", "portfolio"],
    }
    for name, members in clusters.items():
        sims = []
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                sims.append(cosine_similarity(EMBEDDINGS[members[i]], EMBEDDINGS[members[j]]))
        avg = sum(sims) / len(sims) if sims else 0
        print(f"   {name:>12s}  avg intra-sim = {avg:.4f}")

    print("\n" + "-" * 72)
    print("KEY INSIGHT:")
    print("  Semantically related words cluster tightly in vector space.")
    print("  'apple' (fruit) is close to 'banana', but 'apple_inc' drifts")
    print("  toward the technology cluster — demonstrating how context")
    print("  determines which region of the embedding space a word occupies.")
    print("-" * 72)


if __name__ == "__main__":
    run_demo()
