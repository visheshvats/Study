"""
MODULE 6 — PROJECT: Content Production Pipeline (Multi-Agent System)
=====================================================================
A complete multi-agent system that combines Router + Pipeline + Supervisor.

This is the capstone project for Module 6 — everything comes together:
  - Router classifies the content type
  - Pipeline agents handle research → drafting → editing
  - Supervisor ensures quality with review loops
  - Parallel-capable design for future enhancement

SETUP:
  pip install openai python-dotenv

RUN:
  python 04_content_pipeline.py

ARCHITECTURE:
  User Request
       │
       ▼
  ┌──────────────────────────────────────┐
  │          ORCHESTRATOR                 │
  │  (Routes, manages state, decides)    │
  └──┬──────────┬──────────────┬────────┘
     │          │              │
     ▼          ▼              ▼
  ┌──────┐  ┌──────┐     ┌────────┐
  │Rsrch │  │Writer│────▶│Reviewer│
  │Agent │  │Agent │◀────│Agent   │
  └──────┘  └──────┘     └────────┘
                              │
                              ▼ (if approved)
                         ┌────────┐
                         │ SEO    │
                         │ Agent  │
                         └────────┘
                              │
                              ▼
                        Final Output
"""

import os
import json
from dataclasses import dataclass, field
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# ══════════════════════════════════════════════════════
# SHARED STATE
# ══════════════════════════════════════════════════════

@dataclass
class ContentState:
    """Shared state for the content production pipeline."""
    topic: str
    content_type: str = ""           # blog, tutorial, comparison
    research: str = ""
    outline: str = ""
    draft: str = ""
    review_feedback: str = ""
    final_content: str = ""
    seo_metadata: dict = field(default_factory=dict)
    iteration: int = 0
    max_iterations: int = 2
    status: str = "pending"           # pending, researching, writing, reviewing, publishing
    agent_log: list = field(default_factory=list)

    def log(self, agent: str, action: str, detail: str = ""):
        self.agent_log.append({
            "agent": agent,
            "action": action,
            "detail": detail[:100],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        })


# ══════════════════════════════════════════════════════
# SPECIALIST AGENTS
# ══════════════════════════════════════════════════════

def classifier_agent(state: ContentState) -> ContentState:
    """Classifies the content type to adjust the pipeline."""
    state.log("Classifier", "Classifying content type")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "Classify the content type. Return JSON:\n"
                '{"type": "blog|tutorial|comparison|how-to", "tone": "technical|casual|formal", '
                '"audience": "beginner|intermediate|advanced"}'
            )},
            {"role": "user", "content": state.topic},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    meta = json.loads(response.choices[0].message.content)
    state.content_type = meta.get("type", "blog")
    state.log("Classifier", f"Type: {state.content_type}", json.dumps(meta))
    return state


def research_agent(state: ContentState) -> ContentState:
    """Deep research on the topic."""
    state.status = "researching"
    state.log("Researcher", "Starting research")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a technical research specialist. Provide comprehensive research "
                "on the given topic. Include:\n"
                "- 5-7 key facts/insights with specifics (numbers, versions, comparisons)\n"
                "- Current trends and best practices (2024-2025)\n"
                "- Common misconceptions\n"
                "- Practical examples\n"
                "Target: software engineers"
            )},
            {"role": "user", "content": f"Research: {state.topic}"},
        ],
        temperature=0.5,
        max_tokens=500,
    )

    state.research = response.choices[0].message.content
    state.log("Researcher", "Research complete", f"{len(state.research.split())} words")
    return state


def writer_agent(state: ContentState) -> ContentState:
    """Writes or rewrites based on feedback."""
    state.status = "writing"
    is_rewrite = bool(state.review_feedback)
    state.log("Writer", "Rewriting with feedback" if is_rewrite else "Writing first draft")

    feedback_context = ""
    if is_rewrite:
        feedback_context = (
            f"\n\nPREVIOUS DRAFT:\n{state.draft}\n\n"
            f"REVIEWER FEEDBACK (address ALL points):\n{state.review_feedback}"
        )

    type_instructions = {
        "blog": "Write an engaging blog post with a strong hook, clear sections, and actionable takeaways.",
        "tutorial": "Write a step-by-step tutorial with numbered instructions, code examples, and explanations.",
        "comparison": "Write a balanced comparison with pros/cons, use cases, and a recommendation.",
        "how-to": "Write a practical how-to guide with prerequisites, steps, and troubleshooting tips.",
    }

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                f"You are a technical writer. {type_instructions.get(state.content_type, type_instructions['blog'])}\n"
                "Target: software engineers. Tone: practical and direct.\n"
                "Include code examples where appropriate. Keep under 500 words for this demo."
            )},
            {"role": "user", "content": (
                f"Topic: {state.topic}\n"
                f"Content type: {state.content_type}\n\n"
                f"Research:\n{state.research}"
                f"{feedback_context}\n\n"
                f"Write the content:"
            )},
        ],
        temperature=0.7,
        max_tokens=600,
    )

    state.draft = response.choices[0].message.content
    state.log("Writer", "Draft complete", f"{len(state.draft.split())} words")
    return state


def reviewer_agent(state: ContentState) -> ContentState:
    """Reviews the draft and gives structured feedback."""
    state.status = "reviewing"
    state.iteration += 1
    state.log("Reviewer", f"Review iteration {state.iteration}")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a senior content editor. Review the draft and return JSON:\n"
                "{\n"
                '  "approved": true/false,\n'
                '  "quality_score": 1-10,\n'
                '  "strengths": ["..."],\n'
                '  "improvements_needed": ["..."],\n'
                '  "feedback_for_writer": "specific, actionable feedback"\n'
                "}\n\n"
                "Approve if score >= 7. Be strict but constructive."
            )},
            {"role": "user", "content": (
                f"Topic: {state.topic}\n"
                f"Content type: {state.content_type}\n\n"
                f"Draft to review:\n{state.draft}"
            )},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    review = json.loads(response.choices[0].message.content)
    approved = review.get("approved", False)
    score = review.get("quality_score", 0)

    state.review_feedback = review.get("feedback_for_writer", "")
    state.log("Reviewer", f"Score: {score}/10 {'✅' if approved else '❌'}")

    if approved or score >= 7:
        state.status = "approved"
    elif state.iteration >= state.max_iterations:
        state.status = "max_iterations"
    else:
        state.status = "needs_revision"

    return state


def seo_agent(state: ContentState) -> ContentState:
    """Generates SEO metadata for the final content."""
    state.status = "publishing"
    state.log("SEO", "Generating metadata")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "Generate SEO metadata for the content. Return JSON:\n"
                "{\n"
                '  "title": "SEO-optimized title (50-60 chars)",\n'
                '  "meta_description": "Compelling description (150-160 chars)",\n'
                '  "keywords": ["keyword1", "keyword2", ...],\n'
                '  "slug": "url-friendly-slug"\n'
                "}"
            )},
            {"role": "user", "content": f"Generate SEO metadata for:\n{state.draft[:300]}"},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    state.seo_metadata = json.loads(response.choices[0].message.content)
    state.final_content = state.draft
    state.status = "complete"
    state.log("SEO", "Metadata generated")
    return state


# ══════════════════════════════════════════════════════
# ORCHESTRATOR
# ══════════════════════════════════════════════════════

class ContentOrchestrator:
    """
    Orchestrates the multi-agent content pipeline.
    
    Flow:
      Classify → Research → Write → Review ─┐
                              ↑   (if rejected) │
                              └──────────────────┘
                              (if approved) → SEO → Done
    """

    def run(self, topic: str) -> ContentState:
        """Execute the full content production pipeline."""
        state = ContentState(topic=topic)

        print(f"  📌 Topic: {topic}\n")

        # Stage 1: Classify
        print(f"  ▶ Stage 1: Classification")
        state = classifier_agent(state)
        print(f"    Type: {state.content_type}")

        # Stage 2: Research
        print(f"\n  ▶ Stage 2: Research")
        state = research_agent(state)
        print(f"    ✅ Research gathered")

        # Stage 3+4: Write → Review loop
        while True:
            print(f"\n  ▶ Stage 3: Writing {'(revision)' if state.iteration > 0 else '(first draft)'}")
            state = writer_agent(state)
            print(f"    ✅ Draft: {len(state.draft.split())} words")

            print(f"\n  ▶ Stage 4: Review (iteration {state.iteration + 1})")
            state = reviewer_agent(state)

            if state.status == "approved":
                print(f"    ✅ APPROVED!")
                break
            elif state.status == "max_iterations":
                print(f"    ⚠️  Max iterations reached, proceeding with current draft")
                break
            else:
                print(f"    ❌ Needs revision, sending back to writer...")

        # Stage 5: SEO
        print(f"\n  ▶ Stage 5: SEO Optimization")
        state = seo_agent(state)
        print(f"    ✅ SEO metadata generated")

        return state


# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🏭 Content Production Pipeline              ║")
    print("║  MODULE 6 PROJECT — Multi-Agent System       ║")
    print("╚══════════════════════════════════════════════╝\n")

    orchestrator = ContentOrchestrator()

    topic = "How to implement distributed tracing in Spring Boot microservices using OpenTelemetry"

    result = orchestrator.run(topic)

    # Display results
    print(f"\n  {'═'*55}")
    print(f"  📝 FINAL CONTENT")
    print(f"  {'═'*55}")
    print(f"\n{result.final_content}")

    print(f"\n  {'═'*55}")
    print(f"  🔍 SEO METADATA")
    print(f"  {'═'*55}")
    print(f"  {json.dumps(result.seo_metadata, indent=2)}")

    print(f"\n  {'═'*55}")
    print(f"  📊 PIPELINE STATS")
    print(f"  {'═'*55}")
    print(f"  Content type: {result.content_type}")
    print(f"  Review iterations: {result.iteration}")
    print(f"  Final status: {result.status}")
    print(f"  Word count: {len(result.final_content.split())}")

    print(f"\n  📜 Agent Activity Log:")
    for entry in result.agent_log:
        print(f"    [{entry['timestamp']}] {entry['agent']:12s} → {entry['action']}")

    print(f"\n  ✅ Multi-Agent Pipeline combines:")
    print(f"     • Router (Classifier picks content type)")
    print(f"     • Pipeline (Research → Write → SEO)")
    print(f"     • Supervisor (Write ↔ Review loop)")
    print(f"     • Shared state (ContentState flows through all agents)")
    print(f"     • Activity logging (trace every agent decision)\n")


if __name__ == "__main__":
    main()
