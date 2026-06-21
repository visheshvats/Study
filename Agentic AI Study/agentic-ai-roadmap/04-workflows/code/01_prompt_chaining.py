"""01_prompt_chaining.py - sequential LCEL prompt chaining (Phase 4.1).

PATTERN: Prompt Chaining. Take ONE input, push it through a fixed sequence of
LLM steps where each step's OUTPUT becomes the next step's INPUT. Here:

    article --> [extract 5 key points] --> [2-sentence summary] --> [headline]

Java analogy: this is a Unix pipe (`cat | grep | sort`) or a `Stream` chain
(`stream.map(...).map(...).map(...)`), or Spring Integration's pipes-and-filters
where each handler transforms the message and hands it to the next channel. The
LCEL `|` operator is literally an overloaded pipe: `prompt | llm | parser`
composes a "prompt the model, then parse its text" runnable, exactly like
composing `Function`s with `andThen`.

WHEN TO USE: when each step *depends on* the previous step's result. Do NOT use
chaining for independent subtasks - that wastes latency (run them in parallel
instead; see 03_parallelization.py).

OFFLINE BY DEFAULT
------------------
USE_MOCK = True runs a deterministic FakeChatModel with NO API key and NO
network. It demonstrates the chaining MECHANICS (output->input wiring, LCEL
piping, error handling between steps) without calling Anthropic. Flip to False
and export ANTHROPIC_API_KEY for the real model. See build_llm().

Run it (offline):      python 01_prompt_chaining.py
Real model:            set USE_MOCK = False, then export ANTHROPIC_API_KEY
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# USE_MOCK: the offline switch.
#   True  -> deterministic FakeChatModel, no API key, no network (default).
#   False -> real ChatAnthropic(model="claude-sonnet-4-6"), needs ANTHROPIC_API_KEY.
# ---------------------------------------------------------------------------
USE_MOCK = True


class FakeChatModel(Runnable):
    """Deterministic, offline stand-in for ChatAnthropic.

    A real chat model takes messages (or, via LCEL, a formatted prompt value)
    and returns an AIMessage. We reproduce just enough of that contract:
    `.invoke(prompt_value) -> AIMessage`. We subclass `Runnable` so the LCEL
    `prompt | llm | parser` pipe accepts it exactly like a real ChatAnthropic
    (the `|` operator only composes Runnables - a plain class is rejected).

    To keep the demo meaningful, we sniff which STAGE of the chain we are in by
    looking at the prompt text and return stage-appropriate canned output, so the
    output->input wiring is visibly correct without a real model.

    Java analogy: a hand-rolled test double / Mockito stub that returns canned
    responses based on its argument - here implementing the `Runnable` interface
    so it is a drop-in for the real component.
    """

    # Runnable.invoke signature is (self, input, config=None, **kwargs). LCEL
    # passes the formatted PromptValue as `input`.
    def invoke(self, input: Any, config: Any = None, **kwargs: Any) -> AIMessage:  # noqa: A002
        text = _messages_to_text(input).lower()

        # Stage 1: "extract ... key points"
        if "key point" in text and "extract" in text:
            return AIMessage(
                content=(
                    "1. The system cut average response latency by 40%.\n"
                    "2. A new caching layer absorbs most repeat queries.\n"
                    "3. Costs dropped because fewer calls hit the model.\n"
                    "4. Reliability improved via automatic retries.\n"
                    "5. The rollout was incremental behind a feature flag."
                )
            )
        # Stage 2: "executive summary"
        if "executive summary" in text:
            return AIMessage(
                content=(
                    "A new caching and retry layer cut latency by 40% and reduced "
                    "model costs. The team shipped it incrementally behind a feature "
                    "flag to keep the rollout safe."
                )
            )
        # Stage 3: "headline"
        if "headline" in text:
            return AIMessage(content="Caching Layer Slashes Latency 40 Percent And Cuts Costs")

        # Fallback - should not happen in this demo.
        return AIMessage(content="[MOCK] unrecognised prompt stage")


def _messages_to_text(messages: Any) -> str:
    """Flatten whatever LCEL hands the model into a single string.

    When you pipe `ChatPromptTemplate | llm`, the model's `.invoke` receives a
    PromptValue (which exposes `.to_messages()`), not a raw list. We normalise
    both shapes so the FakeChatModel can inspect the text.
    """
    if hasattr(messages, "to_messages"):
        messages = messages.to_messages()
    if isinstance(messages, (list, tuple)):
        parts: List[str] = []
        for m in messages:
            content = getattr(m, "content", m)
            parts.append(str(content))
        return "\n".join(parts)
    return str(messages)


def build_llm() -> Any:
    """Return the chat model. Mock by default; real ChatAnthropic when asked.

    Java analogy: a factory method / `@Bean` that returns a stub in the 'test'
    profile and the real client in 'prod'.
    """
    if USE_MOCK:
        logger.info("Using FakeChatModel (offline, no API key).")
        return FakeChatModel()

    # --- Real model path -----------------------------------------------------
    # pip install langchain-anthropic ; export ANTHROPIC_API_KEY=...
    from langchain_anthropic import ChatAnthropic

    logger.info("Using real ChatAnthropic(model='claude-sonnet-4-6').")
    return ChatAnthropic(model="claude-sonnet-4-6")


# A single parser reused by every step: pulls the plain `.content` text out of
# the AIMessage so the next prompt template can interpolate it as a string.
parser = StrOutputParser()
llm = build_llm()


# ---------------------------------------------------------------------------
# THE THREE STEPS. Each is an LCEL runnable: prompt | llm | parser.
# The `|` is the pipe: format the prompt, send to the model, parse to a string.
# ---------------------------------------------------------------------------
step1_extract = (
    ChatPromptTemplate.from_template(
        "Extract exactly 5 key points from this article as a numbered list:\n\n{article}"
    )
    | llm
    | parser
)

step2_summarize = (
    ChatPromptTemplate.from_template(
        "Write a 2-sentence executive summary from these key points:\n\n{key_points}"
    )
    | llm
    | parser
)

step3_headline = (
    ChatPromptTemplate.from_template(
        "Write ONE punchy headline for this summary. No punctuation at end:\n\n{summary}"
    )
    | llm
    | parser
)


def analyze_article(article: str) -> Dict[str, str]:
    """Run the 3-step chain. OUTPUT of each step is the INPUT of the next.

    The key idea: `key_points` (a string) is fed into step2 as `{key_points}`,
    and `summary` is fed into step3 as `{summary}`. That output->input handoff
    IS the chaining pattern.

    Error handling between steps (the org's "no failure should silently kill the
    pipeline" rule, and notes.md's mistakes list): each `.invoke` is wrapped so a
    failure in one step is logged with which stage failed and re-raised as a
    clear error, rather than producing a confusing downstream crash. In a real
    system you might instead fall back to a degraded result here (see exercise 2).

    Java analogy: a service method composing three calls, each in its own
    try/catch that adds context before rethrowing - never swallowing the cause.
    """
    if not article or not article.strip():
        raise ValueError("article must be non-empty")

    try:
        key_points = step1_extract.invoke({"article": article})
    except Exception as exc:  # noqa: BLE001 - we re-raise with context
        logger.exception("Chain failed at STEP 1 (extract key points)")
        raise RuntimeError("prompt chain failed at step 1 (extract)") from exc
    logger.info("[step 1] extracted key points (%d chars)", len(key_points))

    try:
        summary = step2_summarize.invoke({"key_points": key_points})
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chain failed at STEP 2 (summarize)")
        raise RuntimeError("prompt chain failed at step 2 (summarize)") from exc
    logger.info("[step 2] wrote summary (%d chars)", len(summary))

    try:
        headline = step3_headline.invoke({"summary": summary})
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chain failed at STEP 3 (headline)")
        raise RuntimeError("prompt chain failed at step 3 (headline)") from exc
    logger.info("[step 3] wrote headline")

    return {"key_points": key_points, "summary": summary, "headline": headline}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    article = (
        "Our platform team spent the last quarter on a performance overhaul. They "
        "added a caching layer in front of the model, introduced automatic retries "
        "for transient failures, and shipped the whole thing incrementally behind a "
        "feature flag. Average response latency fell by roughly 40 percent, and "
        "because fewer requests now reach the model, monthly costs dropped as well."
    )

    results = analyze_article(article)

    # Print each STAGE so the output->input handoff is visible end to end.
    print("\n=== PROMPT CHAINING: 3 stages ===\n")
    print("STAGE 1 - KEY POINTS:")
    print(results["key_points"])
    print("\nSTAGE 2 - EXECUTIVE SUMMARY:")
    print(results["summary"])
    print("\nSTAGE 3 - HEADLINE:")
    print(results["headline"])
    print("\n=== done ===")


if __name__ == "__main__":
    main()
