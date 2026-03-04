"""
MODULE 0 — Example 2: Basic Prompt Patterns
=============================================
Shows different ways to prompt an LLM and how structure affects output.

SETUP:
  1. pip install openai python-dotenv
  2. Create a .env file:  OPENAI_API_KEY=sk-your-key-here
  3. Run: python 02_basic_prompts.py

KEY LESSON:
  The WAY you ask is as important as WHAT you ask.
  This is the foundation of Prompt Engineering (Module 1).
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask(prompt: str, system: str = None, temperature: float = 0.3) -> str:
    """Helper function to call the LLM with less boilerplate."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=300,
    )
    return response.choices[0].message.content


def vague_vs_specific():
    """
    LESSON: Specific prompts give better results.
    
    Java Analogy: A vague prompt is like a poorly written JIRA ticket.
    A specific prompt is like a well-defined API contract.
    """
    print("=" * 60)
    print("EXAMPLE 1: Vague vs Specific Prompts")
    print("=" * 60)

    # ❌ Vague prompt
    vague = ask("Tell me about Kafka")
    print(f"\n❌ Vague: 'Tell me about Kafka'")
    print(f"   Response: {vague[:200]}...")

    # ✅ Specific prompt
    specific = ask(
        "Explain Apache Kafka's consumer group rebalancing mechanism "
        "in 3 bullet points for a Spring Boot developer."
    )
    print(f"\n✅ Specific: 'Explain Kafka consumer group rebalancing...'")
    print(f"   Response: {specific[:300]}")


def unstructured_vs_structured():
    """
    LESSON: Ask for structured output to get parseable responses.
    
    This is CRITICAL for production systems where you need to
    parse the LLM output programmatically.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Unstructured vs Structured Output")
    print("=" * 60)

    # ❌ Unstructured — hard to parse
    unstructured = ask("What are the SOLID principles?")
    print(f"\n❌ Unstructured:")
    print(f"   {unstructured[:200]}...")

    # ✅ Structured — easy to parse
    structured = ask(
        "List the SOLID principles. "
        "Return ONLY a JSON array where each item has: "
        "'letter', 'name', 'one_line_explanation'. "
        "No markdown, no explanation outside the JSON."
    )
    print(f"\n✅ Structured (JSON):")
    print(f"   {structured[:400]}")


def role_prompting():
    """
    LESSON: Giving the LLM a role changes its behavior dramatically.
    
    Java Analogy: This is like @Profile("production") vs @Profile("dev").
    Same code, different behavior based on context.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Role Prompting")
    print("=" * 60)

    question = "Should I use microservices?"

    # Role 1: Startup CTO
    answer1 = ask(
        question,
        system="You are a startup CTO with 3 engineers. Be practical and concise."
    )
    print(f"\n🧑‍💻 Startup CTO says:")
    print(f"   {answer1[:200]}")

    # Role 2: Enterprise Architect
    answer2 = ask(
        question,
        system="You are an enterprise architect at a Fortune 500 bank. Be thorough."
    )
    print(f"\n🏢 Enterprise Architect says:")
    print(f"   {answer2[:200]}")


def context_matters():
    """
    LESSON: Providing context dramatically improves output quality.
    
    This is the foundation of RAG (Module 3) — giving the LLM
    relevant information before asking a question.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Context Matters")
    print("=" * 60)

    # ❌ No context
    no_context = ask("What's the best approach for our payment service?")
    print(f"\n❌ Without context:")
    print(f"   {no_context[:200]}...")

    # ✅ With context (this is basically what RAG does automatically)
    with_context = ask(
        "Given the following system context:\n"
        "- We use Spring Boot 3.2 with Java 21\n"
        "- Payments go through Stripe API\n"
        "- We have 10K transactions/day\n"
        "- We use PostgreSQL with event sourcing\n"
        "- Current latency is 200ms p99\n\n"
        "What's the best approach for making our payment service more resilient?"
    )
    print(f"\n✅ With context:")
    print(f"   {with_context[:300]}")


# ──────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 MODULE 0: Basic Prompt Patterns\n")

    vague_vs_specific()
    unstructured_vs_structured()
    role_prompting()
    context_matters()

    print("\n✅ Key takeaway: HOW you prompt matters as much as WHAT you prompt.")
    print("   We'll go much deeper in Module 1: Prompt Engineering.\n")
