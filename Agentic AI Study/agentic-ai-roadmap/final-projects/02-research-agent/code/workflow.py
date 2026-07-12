"""
Parallel sub-analysis + synthesis. Phase 4 sections 4.1 and 4.3.
analyze_parallel fans out independent analyses with asyncio.gather (offline-safe).
"""
from __future__ import annotations

import asyncio
import time
from typing import Dict

import mock_kit


async def _sentiment(text: str) -> str:
    await asyncio.sleep(0.2)  # simulate an LLM call
    pos = sum(w in text.lower() for w in ("support", "priority", "growth", "includes"))
    return f"{'positive' if pos >= 2 else 'neutral'} ({pos} positive cues)"


async def _topics(text: str) -> str:
    await asyncio.sleep(0.2)
    toks = [t for t in mock_kit.tokenize(text) if len(t) > 4]
    top = sorted(set(toks), key=toks.count, reverse=True)[:5]
    return ", ".join(top)


async def _key_claims(text: str) -> str:
    await asyncio.sleep(0.2)
    claims = [s.strip() for s in text.split(".") if any(c.isdigit() for c in s)]
    return f"{len(claims)} quantitative claim(s)"


async def analyze_parallel(text: str) -> Dict[str, str]:
    """Fan-out 3 analyses concurrently, fan-in the results."""
    sent, top, claims = await asyncio.gather(_sentiment(text), _topics(text), _key_claims(text))
    return {"sentiment": sent, "topics": top, "key_claims": claims}


def synthesize(question: str, findings: str, analyses: Dict[str, str]) -> str:
    """Combine agent findings + analyses into a final answer (MockLLM offline)."""
    return mock_kit.MockLLM().synthesize(question, findings, analyses)


if __name__ == "__main__":
    txt = "Our Pro plan costs 49 dollars with priority support and 100 GB storage."
    t0 = time.perf_counter()
    res = asyncio.run(analyze_parallel(txt))
    print(f"parallel analyses in {time.perf_counter() - t0:.2f}s (≈0.2s, not 0.6s):", res)
