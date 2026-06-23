"""
04_token_tracking.py — Phase 9.4: token tracking + cost (offline-safe mock response).

WHAT THIS SHOWS
    Every Anthropic response carries `response.usage.input_tokens` /
    `.output_tokens`. Tracking them is your Micrometer + cost monitoring: a per-call
    counter plus a running session total, turned into dollars. Tokens are billed
    PER MTOK (per MILLION tokens), priced separately for input vs output —
    output is typically several times pricier, so a chatty agent emitting long
    answers can be your biggest line item. Cost = tokens / 1_000_000 * price_per_mtok.

OFFLINE NOTE
    No API key and no network. We define a MOCK response object that exposes
    `.usage.input_tokens` / `.usage.output_tokens` exactly like the real Anthropic
    SDK, so the cost math is demonstrated locally. To go live, see TODO markers in
    `tracked_llm_call`.

    Run:  python 04_token_tracking.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("phase9.tokens")


# ─────────────────────────────────────────────────────────────────────────────
# Typing: the minimal shape TokenTracker needs from a response. The real Anthropic
# Message satisfies this structurally — `usage.input_tokens` / `usage.output_tokens`.
# ─────────────────────────────────────────────────────────────────────────────
class _Usage(Protocol):
    input_tokens: int
    output_tokens: int


class _HasUsage(Protocol):
    usage: _Usage


# ── MOCK response objects (offline stand-in for an Anthropic Message) ─────────
@dataclass(frozen=True)
class MockUsage:
    """Mirrors `response.usage` from the Anthropic SDK."""

    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class MockResponse:
    """Offline stand-in exposing `.usage` (and `.content` text) like a real Message.

    TODO(real): delete this and use the SDK's Message returned by
        client.messages.create(...). It already has `.usage.input_tokens` etc.
    """

    usage: MockUsage
    text: str = "(mock answer)"


# ─────────────────────────────────────────────────────────────────────────────
# TokenTracker — the metric/cost collector. Per-call sample + running session total.
# ─────────────────────────────────────────────────────────────────────────────
class TokenTracker:
    """Accumulate token usage and compute USD cost per call and per session.

    Java analogy: a pair of Micrometer Counters (input, output) plus a derived
    cost gauge you can alert on — wired up before the bill ever arrives.
    """

    def __init__(
        self,
        input_price_per_mtok: float = 3.0,    # $ per MILLION input tokens
        output_price_per_mtok: float = 15.0,  # $ per MILLION output tokens (note: ~5x)
    ) -> None:
        self.total_input = 0
        self.total_output = 0
        # TODO(real): keep these in sync with the Anthropic pricing page for your model.
        self.input_price_per_mtok = input_price_per_mtok
        self.output_price_per_mtok = output_price_per_mtok

    def _cost(self, inp: int, out: int) -> float:
        """Dollars for `inp` input + `out` output tokens at the configured rates."""
        return (
            inp / 1_000_000 * self.input_price_per_mtok
            + out / 1_000_000 * self.output_price_per_mtok
        )

    def track(self, response: _HasUsage) -> dict[str, Any]:
        """Record one response's usage and return a per-call + session-total summary."""
        inp = response.usage.input_tokens
        out = response.usage.output_tokens
        self.total_input += inp
        self.total_output += out

        return {
            "this_call": {
                "input": inp,
                "output": out,
                "cost_usd": round(self._cost(inp, out), 6),
            },
            "session_total": {
                "input": self.total_input,
                "output": self.total_output,
                "cost_usd": round(self._cost(self.total_input, self.total_output), 4),
            },
        }


# A single shared tracker, like a singleton MeterRegistry bean.
tracker = TokenTracker()


def tracked_llm_call(messages: list[dict[str, str]]) -> str:
    """Make a (mock) LLM call, record its token cost, and return the text.

    TODO(real): replace the mock with the real SDK call —
        from anthropic import Anthropic
        client = Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1024, messages=messages,
        )
        ... return response.content[0].text
    The rest of this function (track + log) stays identical.
    """
    # Offline: synthesize usage proportional to message size so numbers feel real.
    prompt_chars = sum(len(m["content"]) for m in messages)
    response = MockResponse(
        usage=MockUsage(input_tokens=prompt_chars * 2, output_tokens=prompt_chars),
    )

    usage = tracker.track(response)
    logger.info("Token usage: %s", usage)  # ≈ recording a Micrometer sample at INFO
    return response.text


def main() -> None:
    """Run three tracked calls, then assert the session math is correct."""
    logger.info("Token tracking demo (offline mock responses)")
    logger.info(
        "Pricing: input=$%.2f/MTok  output=$%.2f/MTok (output ~%.0fx input)",
        tracker.input_price_per_mtok,
        tracker.output_price_per_mtok,
        tracker.output_price_per_mtok / tracker.input_price_per_mtok,
    )

    # Three calls of increasing size.
    tracked_llm_call([{"role": "user", "content": "hi"}])
    tracked_llm_call([{"role": "user", "content": "explain token tracking briefly"}])
    tracked_llm_call([{"role": "user", "content": "now explain it in much more detail please"}])

    # ── Verify the session total = sum of calls, and cost matches the formula. ──
    # Re-derive expected cost independently so the assertion is a real check.
    expected_cost = round(
        tracker.total_input / 1_000_000 * tracker.input_price_per_mtok
        + tracker.total_output / 1_000_000 * tracker.output_price_per_mtok,
        4,
    )
    reported_cost = tracker.track(
        MockResponse(usage=MockUsage(input_tokens=0, output_tokens=0))
    )["session_total"]["cost_usd"]

    assert reported_cost == expected_cost, (reported_cost, expected_cost)
    assert tracker.total_input > 0 and tracker.total_output > 0

    print("\n=== SESSION SUMMARY ===")
    print(f"Total input tokens : {tracker.total_input:,}")
    print(f"Total output tokens: {tracker.total_output:,}")
    print(f"Estimated cost     : ${expected_cost:.4f}")
    print("Assertion passed: session cost equals tokens/1e6 * price_per_mtok. ✓")


if __name__ == "__main__":
    main()
