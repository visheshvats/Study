#!/usr/bin/env python3
"""
Self-Supervised Masking — Mask-Prediction Data Pipeline
========================================================
Simulates the core self-supervised pre-training objective used by BERT-style
models: randomly mask tokens in a text sequence and train the model to
reconstruct the originals.

Covers:
  • Random masking with configurable probability
  • Three-way masking strategy ([MASK] / random replace / keep)
  • Batch pipeline with padding and attention masks
  • Loss computation via cross-entropy over masked positions only

Run:
    python self_supervised_mask.py
"""

import math
import random
from typing import Dict, List, Tuple

random.seed(42)

# ── Toy Vocabulary ──────────────────────────────────────────────────────────
VOCAB: Dict[str, int] = {
    "[PAD]": 0, "[MASK]": 1, "[CLS]": 2, "[SEP]": 3,
    "the": 4, "cat": 5, "sat": 6, "on": 7, "mat": 8,
    "dog": 9, "ran": 10, "across": 11, "field": 12,
    "a": 13, "big": 14, "small": 15, "red": 16, "blue": 17,
    "quickly": 18, "slowly": 19, "jumped": 20, "over": 21,
    "lazy": 22, "fox": 23, "brown": 24, "fence": 25,
}
ID_TO_TOKEN = {v: k for k, v in VOCAB.items()}
VOCAB_SIZE = len(VOCAB)


# ── Masking Strategy ────────────────────────────────────────────────────────
def apply_masking(
    token_ids: List[int],
    mask_prob: float = 0.15,
    mask_token_id: int = 1,
) -> Tuple[List[int], List[int], List[bool]]:
    """
    BERT-style masking:
      80% of selected positions → [MASK]
      10% of selected positions → random token
      10% of selected positions → keep original

    Returns:
        masked_ids   — token IDs after masking
        labels       — original token IDs at masked positions (-100 elsewhere)
        mask_flags   — boolean flags indicating which positions were masked
    """
    masked_ids = list(token_ids)
    labels = [-100] * len(token_ids)
    mask_flags = [False] * len(token_ids)

    for i, tid in enumerate(token_ids):
        # Never mask special tokens
        if tid in (0, 2, 3):
            continue

        if random.random() < mask_prob:
            labels[i] = tid
            mask_flags[i] = True
            r = random.random()
            if r < 0.80:
                masked_ids[i] = mask_token_id       # Replace with [MASK]
            elif r < 0.90:
                masked_ids[i] = random.randint(4, VOCAB_SIZE - 1)  # Random token
            # else: keep original (10%)

    return masked_ids, labels, mask_flags


# ── Padding & Attention Mask ────────────────────────────────────────────────
def pad_sequence(token_ids: List[int], max_len: int) -> Tuple[List[int], List[int]]:
    """Pad to fixed length; return (padded_ids, attention_mask)."""
    pad_len = max_len - len(token_ids)
    padded = token_ids + [0] * pad_len
    attn_mask = [1] * len(token_ids) + [0] * pad_len
    return padded, attn_mask


# ── Cross-Entropy Loss (masked positions only) ─────────────────────────────
def mock_cross_entropy_loss(
    predictions: List[List[float]],
    labels: List[int],
) -> float:
    """
    Compute average negative log-likelihood loss over masked positions.
    predictions[i] is a probability distribution over the vocabulary for position i.
    """
    total_loss = 0.0
    count = 0
    for i, label in enumerate(labels):
        if label == -100:
            continue
        prob = predictions[i][label]
        total_loss += -math.log(max(prob, 1e-10))
        count += 1
    return total_loss / max(count, 1)


def generate_mock_predictions(seq_len: int, vocab_size: int) -> List[List[float]]:
    """Generate a mock softmax output (uniform + noise)."""
    preds = []
    for _ in range(seq_len):
        raw = [random.random() for _ in range(vocab_size)]
        total = sum(raw)
        preds.append([r / total for r in raw])
    return preds


# ── Data Pipeline ───────────────────────────────────────────────────────────
def tokenize_sentence(sentence: str) -> List[int]:
    """Convert a sentence to token IDs with [CLS] and [SEP]."""
    words = sentence.lower().split()
    ids = [VOCAB.get(w, 1) for w in words]
    return [2] + ids + [3]  # [CLS] ... [SEP]


def build_batch(sentences: List[str], max_len: int = 12) -> None:
    """Full pipeline: tokenize → mask → pad → compute loss."""
    print(f"\n{'─' * 60}")
    print(f"  Processing batch of {len(sentences)} sentences (max_len={max_len})")
    print(f"{'─' * 60}")

    batch_loss = 0.0
    for idx, sentence in enumerate(sentences):
        token_ids = tokenize_sentence(sentence)
        masked_ids, labels, mask_flags = apply_masking(token_ids)
        padded_ids, attn_mask = pad_sequence(masked_ids, max_len)
        padded_labels = labels + [-100] * (max_len - len(labels))

        # Mock model predictions
        preds = generate_mock_predictions(max_len, VOCAB_SIZE)
        loss = mock_cross_entropy_loss(preds, padded_labels)
        batch_loss += loss

        # Display
        original_tokens = [ID_TO_TOKEN.get(t, "?") for t in token_ids]
        masked_tokens = [ID_TO_TOKEN.get(t, "?") for t in masked_ids]
        masked_positions = [i for i, f in enumerate(mask_flags) if f]

        print(f"\n  Sentence {idx + 1}: \"{sentence}\"")
        print(f"    Original  : {original_tokens}")
        print(f"    Masked    : {masked_tokens}")
        print(f"    Mask pos  : {masked_positions}")
        print(f"    Attn mask : {attn_mask}")
        print(f"    Loss      : {loss:.4f}")

    avg_loss = batch_loss / len(sentences)
    print(f"\n  Batch average loss: {avg_loss:.4f}")
    print(f"  (Random baseline ≈ {-math.log(1/VOCAB_SIZE):.4f} for vocab={VOCAB_SIZE})")


# ── Demo ────────────────────────────────────────────────────────────────────
def run_demo() -> None:
    print("=" * 72)
    print("SELF-SUPERVISED MASKING — Mask-Prediction Pipeline Demo")
    print("=" * 72)
    print("\nObjective: Randomly mask ~15% of tokens and train to reconstruct.")
    print("Strategy : 80% [MASK], 10% random replace, 10% keep unchanged.")

    sentences = [
        "the cat sat on the mat",
        "a big dog ran across the field",
        "the brown fox jumped over the lazy dog",
        "the small blue cat slowly sat on the red mat",
    ]

    build_batch(sentences)

    # Demonstrate mask ratio statistics
    print(f"\n{'─' * 60}")
    print("  Masking Statistics (1000 trials on sentence 1)")
    print(f"{'─' * 60}")
    test_ids = tokenize_sentence(sentences[0])
    mask_counts = [0] * len(test_ids)
    trials = 1000
    for _ in range(trials):
        _, _, flags = apply_masking(test_ids)
        for i, f in enumerate(flags):
            if f:
                mask_counts[i] += 1
    tokens = [ID_TO_TOKEN.get(t, "?") for t in test_ids]
    print(f"  {'Token':>10s}  {'Mask %':>8s}  Visual")
    for tok, count in zip(tokens, mask_counts):
        pct = count / trials * 100
        bar = "█" * int(pct / 2)
        print(f"  {tok:>10s}  {pct:>7.1f}%  {bar}")

    print("\n" + "-" * 72)
    print("KEY INSIGHT:")
    print("  Self-supervised learning requires NO human labels. The raw text")
    print("  itself provides the supervision signal — mask a word, predict it")
    print("  back. This scales to trillions of tokens at a fraction of the")
    print("  cost of manual annotation.")
    print("-" * 72)


if __name__ == "__main__":
    run_demo()
