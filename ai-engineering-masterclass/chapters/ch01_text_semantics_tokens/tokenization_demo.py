#!/usr/bin/env python3
"""
Tokenization Demo — Sub-word / Suffix Splitting via Regex & Dictionary
=======================================================================
Demonstrates why naive whitespace splitting corrupts model performance and
how production tokenizers (BPE / WordPiece) handle morphological boundaries.

Run:
    python tokenization_demo.py
"""

import re
from collections import Counter
from typing import List, Tuple

# ── Vocabulary & Merge Table ────────────────────────────────────────────────
# A miniature byte-pair encoding vocabulary built from a toy corpus.
# Each entry maps a merged sub-word unit to the two pieces that formed it.
BPE_MERGES: List[Tuple[str, str]] = [
    ("l", "o"),       # lo
    ("lo", "w"),      # low
    ("e", "r"),       # er
    ("n", "e"),       # ne
    ("ne", "w"),      # new
    ("new", "er"),    # newer
    ("low", "er"),    # lower
    ("low", "est"),   # lowest
    ("i", "ng"),      # ing
    ("r", "un"),      # run
    ("run", "n"),     # runn
    ("runn", "ing"),  # running
]

BASE_VOCAB = set("abcdefghijklmnopqrstuvwxyz") | {"est", "ing", "er", "ed", "s"}


# ── Naive Whitespace Tokenizer ──────────────────────────────────────────────
def whitespace_tokenize(text: str) -> List[str]:
    """Split on spaces — the simplest (and worst) strategy."""
    return text.strip().split()


# ── Regex-Based Morphological Tokenizer ─────────────────────────────────────
# Pattern captures common English suffixes before falling back to stem chunks.
MORPHEME_PATTERN = re.compile(
    r"(?P<prefix>un|re|pre|dis|mis)?"        # optional prefix
    r"(?P<stem>[a-z]+?)"                      # minimal stem
    r"(?P<suffix>tion|sion|ment|ness|able|ible|ful|less|ous|ive|ing|ers|er|ed|ly|est|s)?$",  # suffix
    re.IGNORECASE,
)


def morphological_tokenize(word: str) -> List[str]:
    """Break a single word into prefix / stem / suffix tokens."""
    m = MORPHEME_PATTERN.match(word.lower())
    if not m:
        return [word.lower()]
    parts = [g for g in m.groups() if g]
    return parts if parts else [word.lower()]


# ── Mini BPE Tokenizer ──────────────────────────────────────────────────────
def _get_pairs(tokens: List[str]) -> Counter:
    """Count adjacent symbol pairs."""
    pairs: Counter = Counter()
    for i in range(len(tokens) - 1):
        pairs[(tokens[i], tokens[i + 1])] += 1
    return pairs


def bpe_tokenize(word: str, merges: List[Tuple[str, str]]) -> List[str]:
    """Apply byte-pair merges to a character-split word."""
    tokens = list(word.lower())
    for left, right in merges:
        merged = left + right
        i = 0
        new_tokens: List[str] = []
        while i < len(tokens):
            # Attempt to match the left+right pair at position i
            combined = tokens[i]
            if combined == left and i + 1 < len(tokens) and tokens[i + 1] == right:
                new_tokens.append(merged)
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        tokens = new_tokens
    return tokens


# ── Demonstration ───────────────────────────────────────────────────────────
def run_demo() -> None:
    corpus = (
        "The runners were running toward the lowest point of the newer valley "
        "while unhappiness threatened the joyfulness of the evening"
    )

    print("=" * 72)
    print("TOKENIZATION DEMO — Sub-Word & Suffix Splitting")
    print("=" * 72)

    # 1. Whitespace baseline
    ws_tokens = whitespace_tokenize(corpus)
    print(f"\n1. Whitespace tokens ({len(ws_tokens)} tokens):")
    print(f"   {ws_tokens}\n")

    # 2. Morphological regex split
    print("2. Morphological split (per word):")
    all_morphemes: List[str] = []
    for word in ws_tokens:
        clean = re.sub(r"[^a-zA-Z]", "", word)
        parts = morphological_tokenize(clean)
        all_morphemes.extend(parts)
        print(f"   {clean:>15s}  →  {parts}")
    print(f"   Total sub-word tokens: {len(all_morphemes)}\n")

    # 3. BPE split on selected words
    bpe_words = ["lower", "lowest", "newer", "running"]
    print("3. Byte-Pair Encoding (BPE) split:")
    for w in bpe_words:
        tokens = bpe_tokenize(w, BPE_MERGES)
        print(f"   {w:>10s}  →  {tokens}")

    # 4. Token-count comparison
    print("\n" + "-" * 72)
    print("KEY INSIGHT:")
    print("  Whitespace splitting treats 'runners' and 'running' as entirely")
    print("  unrelated tokens. Sub-word tokenization shares the stem 'run',")
    print("  letting the model generalise across morphological variants and")
    print("  dramatically shrink effective vocabulary size.")
    print("-" * 72)

    # 5. Vocabulary coverage analysis
    print("\n4. Vocabulary coverage comparison:")
    unique_ws = set(w.lower() for w in ws_tokens)
    unique_morph = set(all_morphemes)
    print(f"   Whitespace unique tokens : {len(unique_ws)}")
    print(f"   Morpheme unique tokens   : {len(unique_morph)}")
    print(f"   Reduction factor         : {len(unique_ws) / max(len(unique_morph), 1):.2f}x")
    print(f"   Shared sub-words         : {unique_morph & {'run', 'er', 'ing', 'est', 'low', 'new'}}")


if __name__ == "__main__":
    run_demo()
