#!/usr/bin/env python3
"""
Attention Weights — Contextual Vector Steering ("Apple" Disambiguation)
========================================================================
Demonstrates how an attention mechanism re-weights word embeddings based on
surrounding context, shifting the meaning of an ambiguous word like "Apple"
across semantic domains:

  • Fruit:      "Apple fell from the tree"
  • Enterprise: "Apple reported record revenue"
  • Idiom:      "You are the apple of my eye"

Run:
    python attention_weights.py
"""

import math
from typing import Dict, List, Tuple

# ── Prototype Domain Vectors (5-D) ─────────────────────────────────────────
# These represent the three possible "meanings" of "Apple".
DOMAIN_ANCHORS: Dict[str, List[float]] = {
    "fruit":       [0.90, 0.10, 0.05, 0.88, 0.08],
    "enterprise":  [0.10, 0.88, 0.85, 0.12, 0.90],
    "idiom":       [0.60, 0.30, 0.10, 0.55, 0.25],
}

# ── Context Word Embeddings ────────────────────────────────────────────────
WORD_VECTORS: Dict[str, List[float]] = {
    # Fruit context
    "fell":     [0.85, 0.05, 0.02, 0.80, 0.04],
    "from":     [0.50, 0.50, 0.50, 0.50, 0.50],  # function word — neutral
    "the":      [0.50, 0.50, 0.50, 0.50, 0.50],
    "tree":     [0.92, 0.08, 0.03, 0.90, 0.06],
    # Enterprise context
    "reported": [0.12, 0.80, 0.78, 0.15, 0.82],
    "record":   [0.15, 0.75, 0.70, 0.18, 0.80],
    "revenue":  [0.08, 0.90, 0.88, 0.10, 0.92],
    # Idiom context
    "you":      [0.55, 0.35, 0.20, 0.50, 0.30],
    "are":      [0.50, 0.50, 0.50, 0.50, 0.50],
    "of":       [0.50, 0.50, 0.50, 0.50, 0.50],
    "my":       [0.58, 0.30, 0.15, 0.52, 0.28],
    "eye":      [0.62, 0.25, 0.10, 0.58, 0.22],
    # Ambiguous token
    "apple":    [0.50, 0.50, 0.50, 0.50, 0.50],  # starts neutral
}


# ── Matrix Operations ──────────────────────────────────────────────────────
def dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def magnitude(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def cosine_sim(a: List[float], b: List[float]) -> float:
    ma, mb = magnitude(a), magnitude(b)
    if ma == 0 or mb == 0:
        return 0.0
    return dot(a, b) / (ma * mb)


def softmax(scores: List[float]) -> List[float]:
    """Numerically stable softmax over raw attention logits."""
    max_s = max(scores)
    exps = [math.exp(s - max_s) for s in scores]
    total = sum(exps)
    return [e / total for e in exps]


def scale_vec(v: List[float], s: float) -> List[float]:
    return [x * s for x in v]


def add_vecs(*vecs: List[float]) -> List[float]:
    return [sum(coords) for coords in zip(*vecs)]


# ── Scaled Dot-Product Attention (Single Query) ────────────────────────────
def scaled_dot_product_attention(
    query: List[float],
    keys: List[List[float]],
    values: List[List[float]],
    labels: List[str],
) -> Tuple[List[float], List[Tuple[str, float]]]:
    """
    Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V

    Returns the weighted output vector and the per-token attention weights.
    """
    d_k = len(query)
    scale = math.sqrt(d_k)

    # Raw scores
    raw_scores = [dot(query, k) / scale for k in keys]

    # Softmax normalisation
    weights = softmax(raw_scores)

    # Weighted sum of value vectors
    weighted_values = [scale_vec(v, w) for v, w in zip(values, weights)]
    output = weighted_values[0]
    for wv in weighted_values[1:]:
        output = add_vecs(output, wv)

    named_weights = list(zip(labels, weights))
    return output, named_weights


# ── Demonstration ───────────────────────────────────────────────────────────
def run_attention_for_sentence(sentence: str) -> None:
    """Run a single attention pass where "apple" is the query token."""
    tokens = sentence.lower().split()
    apple_idx = tokens.index("apple")

    # Query = apple's initial (neutral) embedding
    query = WORD_VECTORS["apple"]

    # Keys & Values = every other token in the sentence
    context_tokens = [t for i, t in enumerate(tokens) if i != apple_idx]
    keys = [WORD_VECTORS.get(t, WORD_VECTORS["the"]) for t in context_tokens]
    values = keys  # In this simplified demo, K == V

    output_vec, attn_weights = scaled_dot_product_attention(query, keys, values, context_tokens)

    # Report
    print(f"\n  Sentence : \"{sentence}\"")
    print(f"  Query    : apple (neutral)")
    print(f"  Attention weights:")
    for token, w in sorted(attn_weights, key=lambda t: t[1], reverse=True):
        bar = "█" * int(w * 40)
        print(f"    {token:>10s}  {w:.4f}  {bar}")

    # Compare attended output to each domain anchor
    print(f"  Domain alignment after attention:")
    for domain, anchor in DOMAIN_ANCHORS.items():
        sim = cosine_sim(output_vec, anchor)
        indicator = " ← WINNER" if sim == max(
            cosine_sim(output_vec, a) for a in DOMAIN_ANCHORS.values()
        ) else ""
        print(f"    {domain:>12s}  cosine = {sim:.4f}{indicator}")


def run_demo() -> None:
    print("=" * 72)
    print("ATTENTION WEIGHTS — Contextual Disambiguation of 'Apple'")
    print("=" * 72)
    print("\nScaled Dot-Product Attention: softmax(Q·Kᵀ / √d_k) · V")
    print("The query ('apple') attends to every other token. The resulting")
    print("weighted vector shifts toward the contextually correct domain.\n")

    sentences = [
        "Apple fell from the tree",
        "Apple reported record revenue",
        "You are the apple of my eye",
    ]

    for s in sentences:
        run_attention_for_sentence(s)

    # Multi-head intuition
    print("\n" + "-" * 72)
    print("MULTI-HEAD ATTENTION INTUITION:")
    print("  In a real Transformer, multiple attention heads run in parallel,")
    print("  each learning a different linguistic relationship:")
    print("    Head 1 → syntactic dependencies (subject–verb)")
    print("    Head 2 → semantic co-reference (apple ↔ fruit)")
    print("    Head 3 → positional proximity weighting")
    print("  Their outputs are concatenated and projected, giving the model a")
    print("  rich, multi-faceted contextual representation of every token.")
    print("-" * 72)


if __name__ == "__main__":
    run_demo()
