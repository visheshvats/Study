"""
MODULE 6 — Example 2: Pipeline Pattern
=========================================
Agents run in sequence, each transforming the output.
Like a Spring Batch job: Reader → Processor → Writer.

SETUP:
  pip install openai python-dotenv

RUN:
  python 02_pipeline_pattern.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# ══════════════════════════════════════════════════════
# SHARED STATE (flows through the pipeline)
# ══════════════════════════════════════════════════════

class PipelineState:
    """Shared state between pipeline agents."""
    def __init__(self, topic: str):
        self.topic = topic
        self.research = ""
        self.outline = ""
        self.draft = ""
        self.edited = ""
        self.metadata = {}


# ══════════════════════════════════════════════════════
# PIPELINE AGENTS (each does one thing well)
# ══════════════════════════════════════════════════════

def research_agent(state: PipelineState) -> PipelineState:
    """Agent 1: Research the topic and gather key points."""
    print("  ▶ Stage 1: Research Agent")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a research specialist. Given a topic, provide 5-7 key facts "
                "and insights. Be concise and factual. Focus on practical, actionable "
                "information that a software engineer would find useful. "
                "Format as a numbered list."
            )},
            {"role": "user", "content": f"Research this topic thoroughly: {state.topic}"},
        ],
        temperature=0.5,
        max_tokens=400,
    )

    state.research = response.choices[0].message.content
    print(f"    ✅ Found key points")
    return state


def outline_agent(state: PipelineState) -> PipelineState:
    """Agent 2: Create a structured outline from research."""
    print("  ▶ Stage 2: Outline Agent")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a content strategist. Given research notes, create a clear "
                "outline for a technical blog post. Include:\n"
                "- Title\n"
                "- Introduction hook\n"
                "- 3-4 main sections with subpoints\n"
                "- Conclusion\n"
                "Keep it structured and scannable."
            )},
            {"role": "user", "content": (
                f"Topic: {state.topic}\n\n"
                f"Research notes:\n{state.research}\n\n"
                f"Create a blog post outline:"
            )},
        ],
        temperature=0.3,
        max_tokens=400,
    )

    state.outline = response.choices[0].message.content
    print(f"    ✅ Outline created")
    return state


def writer_agent(state: PipelineState) -> PipelineState:
    """Agent 3: Write the first draft from the outline."""
    print("  ▶ Stage 3: Writer Agent")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a technical writer. Write a concise, engaging blog post "
                "from the given outline. Target audience: software engineers. "
                "Style: practical, direct, with code examples where relevant. "
                "Keep it under 400 words for this demo."
            )},
            {"role": "user", "content": (
                f"Topic: {state.topic}\n\n"
                f"Outline:\n{state.outline}\n\n"
                f"Research:\n{state.research}\n\n"
                f"Write the blog post:"
            )},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    state.draft = response.choices[0].message.content
    print(f"    ✅ Draft written ({len(state.draft.split())} words)")
    return state


def editor_agent(state: PipelineState) -> PipelineState:
    """Agent 4: Edit and polish the draft."""
    print("  ▶ Stage 4: Editor Agent")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a senior editor. Polish the draft by:\n"
                "1. Fixing grammar and clarity\n"
                "2. Improving the hook/introduction\n"
                "3. Making technical content more accessible\n"
                "4. Adding a compelling conclusion\n"
                "5. Ensuring consistent tone\n\n"
                "Return ONLY the polished post, no commentary."
            )},
            {"role": "user", "content": (
                f"Edit and polish this draft:\n\n{state.draft}"
            )},
        ],
        temperature=0.3,
        max_tokens=500,
    )

    state.edited = response.choices[0].message.content
    state.metadata = {
        "topic": state.topic,
        "word_count": len(state.edited.split()),
        "stages_completed": 4,
    }
    print(f"    ✅ Edited ({len(state.edited.split())} words)")
    return state


# ══════════════════════════════════════════════════════
# PIPELINE ORCHESTRATOR
# ══════════════════════════════════════════════════════

def run_pipeline(topic: str) -> PipelineState:
    """
    Execute the pipeline: Research → Outline → Write → Edit.
    
    Each agent transforms the shared state sequentially.
    Like Spring Batch: ItemReader → ItemProcessor → ItemWriter.
    """
    state = PipelineState(topic)

    # The pipeline is just a list of functions
    pipeline = [
        research_agent,
        outline_agent,
        writer_agent,
        editor_agent,
    ]

    for agent_fn in pipeline:
        state = agent_fn(state)

    return state


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  ⛓️  Pipeline Pattern — Content Creation      ║")
    print("║  Research → Outline → Write → Edit           ║")
    print("╚══════════════════════════════════════════════╝\n")

    topic = "Why Java developers should learn about virtual threads in Java 21"

    print(f"  📌 Topic: {topic}\n")
    print(f"  {'─'*55}")

    state = run_pipeline(topic)

    print(f"\n  {'═'*55}")
    print(f"  📝 FINAL OUTPUT:")
    print(f"  {'═'*55}")
    print(f"\n{state.edited}")

    print(f"\n  {'═'*55}")
    print(f"  📊 Metadata: {json.dumps(state.metadata, indent=2)}")

    print(f"\n  ✅ Pipeline Pattern takeaways:")
    print(f"     • Each agent has ONE focused job")
    print(f"     • Output flows sequentially through stages")
    print(f"     • State accumulates as it passes through")
    print(f"     • Easy to add/remove/reorder stages\n")


if __name__ == "__main__":
    main()
