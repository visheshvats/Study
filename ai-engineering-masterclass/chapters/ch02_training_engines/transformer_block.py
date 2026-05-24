#!/usr/bin/env python3
"""
Transformer Block — Stacked Multi-Head Attention + Feedforward Simulation
==========================================================================
A from-scratch programmatic layout simulating the core components of a single
Transformer encoder block:

    Input → LayerNorm → Multi-Head Attention → Residual Add
          → LayerNorm → Feedforward Network   → Residual Add → Output

All operations use pure Python (no external libraries).

Run:
    python transformer_block.py
"""

import math
import random
from typing import List, Tuple

random.seed(42)

# Type aliases
Vector = List[float]
Matrix = List[Vector]


# ── Linear Algebra Utilities ────────────────────────────────────────────────
def mat_mul(A: Matrix, B: Matrix) -> Matrix:
    """Multiply two matrices (list of row-vectors)."""
    rows_a, cols_a = len(A), len(A[0])
    rows_b, cols_b = len(B), len(B[0])
    assert cols_a == rows_b, f"Incompatible shapes: {rows_a}x{cols_a} @ {rows_b}x{cols_b}"
    result: Matrix = []
    for i in range(rows_a):
        row = []
        for j in range(cols_b):
            row.append(sum(A[i][k] * B[k][j] for k in range(cols_a)))
        result.append(row)
    return result


def transpose(M: Matrix) -> Matrix:
    return [list(row) for row in zip(*M)]


def add_matrices(A: Matrix, B: Matrix) -> Matrix:
    return [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def scale_matrix(M: Matrix, s: float) -> Matrix:
    return [[x * s for x in row] for row in M]


def random_matrix(rows: int, cols: int, scale: float = 0.5) -> Matrix:
    return [[random.gauss(0, scale) for _ in range(cols)] for _ in range(rows)]


# ── Activation Functions ───────────────────────────────────────────────────
def relu(x: float) -> float:
    return max(0.0, x)


def gelu(x: float) -> float:
    """Gaussian Error Linear Unit — smoother alternative to ReLU."""
    return 0.5 * x * (1.0 + math.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * x ** 3)))


def apply_activation(M: Matrix, fn) -> Matrix:
    return [[fn(x) for x in row] for row in M]


# ── Softmax ────────────────────────────────────────────────────────────────
def softmax_row(row: Vector) -> Vector:
    max_val = max(row)
    exps = [math.exp(x - max_val) for x in row]
    total = sum(exps)
    return [e / total for e in exps]


def softmax_matrix(M: Matrix) -> Matrix:
    return [softmax_row(row) for row in M]


# ── Layer Normalization ────────────────────────────────────────────────────
def layer_norm(M: Matrix, eps: float = 1e-5) -> Matrix:
    """Apply layer normalization across the last dimension (d_model)."""
    normed: Matrix = []
    for row in M:
        mean = sum(row) / len(row)
        var = sum((x - mean) ** 2 for x in row) / len(row)
        normed.append([(x - mean) / math.sqrt(var + eps) for x in row])
    return normed


# ── Single Attention Head ──────────────────────────────────────────────────
def attention_head(
    X: Matrix,
    W_q: Matrix,
    W_k: Matrix,
    W_v: Matrix,
    d_k: int,
) -> Tuple[Matrix, Matrix]:
    """
    Compute scaled dot-product attention for one head.

    Attention(Q, K, V) = softmax(Q @ K^T / sqrt(d_k)) @ V
    """
    Q = mat_mul(X, W_q)
    K = mat_mul(X, W_k)
    V = mat_mul(X, W_v)

    # Q @ K^T
    scores = mat_mul(Q, transpose(K))
    # Scale
    scores = scale_matrix(scores, 1.0 / math.sqrt(d_k))
    # Softmax
    attn_weights = softmax_matrix(scores)
    # Weighted values
    output = mat_mul(attn_weights, V)
    return output, attn_weights


# ── Multi-Head Attention ───────────────────────────────────────────────────
class MultiHeadAttention:
    def __init__(self, d_model: int, num_heads: int):
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        # Initialise projection matrices for each head
        self.W_qs = [random_matrix(d_model, self.d_k) for _ in range(num_heads)]
        self.W_ks = [random_matrix(d_model, self.d_k) for _ in range(num_heads)]
        self.W_vs = [random_matrix(d_model, self.d_k) for _ in range(num_heads)]
        self.W_o = random_matrix(d_model, d_model)  # Output projection

    def forward(self, X: Matrix) -> Tuple[Matrix, List[Matrix]]:
        head_outputs: List[Matrix] = []
        all_weights: List[Matrix] = []

        for h in range(self.num_heads):
            out, weights = attention_head(X, self.W_qs[h], self.W_ks[h], self.W_vs[h], self.d_k)
            head_outputs.append(out)
            all_weights.append(weights)

        # Concatenate heads (along d_k dimension)
        seq_len = len(X)
        concat: Matrix = []
        for i in range(seq_len):
            row: Vector = []
            for h in range(self.num_heads):
                row.extend(head_outputs[h][i])
            concat.append(row)

        # Output projection
        output = mat_mul(concat, self.W_o)
        return output, all_weights


# ── Feedforward Network ───────────────────────────────────────────────────
class FeedForwardNetwork:
    def __init__(self, d_model: int, d_ff: int):
        self.W1 = random_matrix(d_model, d_ff)
        self.W2 = random_matrix(d_ff, d_model)

    def forward(self, X: Matrix) -> Matrix:
        hidden = mat_mul(X, self.W1)
        hidden = apply_activation(hidden, gelu)
        output = mat_mul(hidden, self.W2)
        return output


# ── Transformer Encoder Block ──────────────────────────────────────────────
class TransformerBlock:
    def __init__(self, d_model: int, num_heads: int, d_ff: int):
        self.mha = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForwardNetwork(d_model, d_ff)
        self.d_model = d_model

    def forward(self, X: Matrix) -> Tuple[Matrix, List[Matrix]]:
        # Sub-layer 1: Multi-Head Attention + Residual + LayerNorm
        normed1 = layer_norm(X)
        attn_out, attn_weights = self.mha.forward(normed1)
        residual1 = add_matrices(X, attn_out)

        # Sub-layer 2: Feedforward + Residual + LayerNorm
        normed2 = layer_norm(residual1)
        ff_out = self.ffn.forward(normed2)
        residual2 = add_matrices(residual1, ff_out)

        return residual2, attn_weights


# ── Demonstration ───────────────────────────────────────────────────────────
def format_matrix(M: Matrix, name: str, max_rows: int = 6, precision: int = 4) -> str:
    lines = [f"  {name} ({len(M)}×{len(M[0])}):"]
    for i, row in enumerate(M[:max_rows]):
        vals = "  ".join(f"{v:>{precision + 3}.{precision}f}" for v in row[:8])
        suffix = "  ..." if len(row) > 8 else ""
        lines.append(f"    [{vals}{suffix}]")
    if len(M) > max_rows:
        lines.append(f"    ... ({len(M) - max_rows} more rows)")
    return "\n".join(lines)


def run_demo() -> None:
    print("=" * 72)
    print("TRANSFORMER BLOCK — Multi-Head Attention + Feedforward Demo")
    print("=" * 72)

    # Configuration
    seq_len = 5       # Number of tokens
    d_model = 8       # Embedding dimension
    num_heads = 2     # Attention heads
    d_ff = 16         # Feedforward hidden dimension
    num_layers = 3    # Stacked transformer blocks

    print(f"\n  Configuration:")
    print(f"    Sequence length : {seq_len}")
    print(f"    d_model         : {d_model}")
    print(f"    Attention heads : {num_heads}")
    print(f"    d_k per head    : {d_model // num_heads}")
    print(f"    FFN hidden dim  : {d_ff}")
    print(f"    Stacked layers  : {num_layers}")

    # Mock input embeddings
    X = random_matrix(seq_len, d_model, scale=1.0)
    token_labels = ["[CLS]", "the", "cat", "sat", "[SEP]"]

    print(f"\n{format_matrix(X, 'Input Embeddings')}")

    # Stack multiple transformer blocks
    blocks = [TransformerBlock(d_model, num_heads, d_ff) for _ in range(num_layers)]

    current = X
    for layer_idx, block in enumerate(blocks):
        current, attn_weights = block.forward(current)
        print(f"\n{'─' * 60}")
        print(f"  Layer {layer_idx + 1} Output:")
        print(format_matrix(current, f"  Hidden State L{layer_idx + 1}"))

        # Show attention weights for head 0
        print(f"\n  Attention Weights (Head 1, Layer {layer_idx + 1}):")
        print(f"    {'':>8s}", end="")
        for label in token_labels:
            print(f" {label:>7s}", end="")
        print()
        for i, row in enumerate(attn_weights[0]):
            print(f"    {token_labels[i]:>8s}", end="")
            for w in row:
                print(f" {w:>7.4f}", end="")
            print()

    # Complexity analysis
    print(f"\n{'─' * 60}")
    print(f"  COMPLEXITY ANALYSIS:")
    print(f"    Self-attention : O(N²·d) = O({seq_len}²·{d_model}) = {seq_len**2 * d_model} ops")
    print(f"    Feedforward    : O(N·d·d_ff) = O({seq_len}·{d_model}·{d_ff}) = {seq_len * d_model * d_ff} ops")
    print(f"    Total per layer: {seq_len**2 * d_model + seq_len * d_model * d_ff} ops")
    print(f"    Total (×{num_layers} layers): {(seq_len**2 * d_model + seq_len * d_model * d_ff) * num_layers} ops")

    print(f"\n{'─' * 72}")
    print("  ARCHITECTURAL FLOW:")
    print("    Input → [LayerNorm → Multi-Head Attention → +Residual]")
    print("          → [LayerNorm → Feedforward (GELU)   → +Residual]")
    print("          → (repeat × N layers)")
    print("          → Final LayerNorm → Output")
    print("─" * 72)


if __name__ == "__main__":
    run_demo()
