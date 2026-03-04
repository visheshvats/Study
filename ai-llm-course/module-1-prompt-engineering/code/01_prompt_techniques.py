"""
MODULE 1 — Example 1: Prompt Engineering Techniques Side-by-Side
================================================================
Compares Zero-shot, Few-shot, and Chain-of-Thought prompting.

SETUP:
  pip install openai python-dotenv
  OPENAI_API_KEY in .env

RUN:
  python 01_prompt_techniques.py
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask(messages: list, temperature: float = 0.3) -> str:
    """Helper to call the LLM."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=500,
    )
    return response.choices[0].message.content


# ──────────────────────────────────────────────────────
# TECHNIQUE 1: ZERO-SHOT
# No examples, just ask directly.
# ──────────────────────────────────────────────────────
def demo_zero_shot():
    print("=" * 60)
    print("TECHNIQUE 1: Zero-Shot Prompting")
    print("=" * 60)
    print("No examples given — the LLM relies on its training.\n")

    # Simple zero-shot classification
    result = ask([
        {"role": "user", "content": (
            "Classify the following customer review as POSITIVE, NEGATIVE, or NEUTRAL.\n\n"
            "Review: 'The delivery was fast but the packaging was damaged.'\n\n"
            "Classification:"
        )}
    ])
    print(f"  Review:  'The delivery was fast but the packaging was damaged.'")
    print(f"  Result:  {result}")

    # Zero-shot works well for well-known tasks
    result2 = ask([
        {"role": "user", "content": "Translate to French: 'The microservice is down.'"}
    ])
    print(f"\n  Translate: 'The microservice is down.'")
    print(f"  Result:    {result2}")


# ──────────────────────────────────────────────────────
# TECHNIQUE 2: FEW-SHOT
# Provide examples to establish the pattern.
# ──────────────────────────────────────────────────────
def demo_few_shot():
    print("\n" + "=" * 60)
    print("TECHNIQUE 2: Few-Shot Prompting")
    print("=" * 60)
    print("Provide examples so the LLM learns the expected pattern.\n")

    # Using assistant messages as examples (the proper way)
    result = ask([
        {"role": "system", "content": (
            "You classify Java exceptions into categories: "
            "NULL_SAFETY, CONCURRENCY, IO, CASTING, BOUNDS, OTHER"
        )},
        # Example 1
        {"role": "user", "content": "NullPointerException in UserService.getUser()"},
        {"role": "assistant", "content": "NULL_SAFETY"},
        # Example 2
        {"role": "user", "content": "ConcurrentModificationException in OrderProcessor"},
        {"role": "assistant", "content": "CONCURRENCY"},
        # Example 3
        {"role": "user", "content": "FileNotFoundException: config.yml not found"},
        {"role": "assistant", "content": "IO"},
        # Example 4
        {"role": "user", "content": "ClassCastException: String cannot be cast to Integer"},
        {"role": "assistant", "content": "CASTING"},
        # Now the actual question
        {"role": "user", "content": "ArrayIndexOutOfBoundsException at line 42 in DataLoader"},
    ])
    print(f"  Input:  'ArrayIndexOutOfBoundsException at line 42 in DataLoader'")
    print(f"  Result: {result}")

    # Few-shot with a custom format
    result2 = ask([
        {"role": "user", "content": (
            "Convert Java log lines to structured format.\n\n"
            "Examples:\n"
            "---\n"
            "Input: 2024-01-15 ERROR PaymentService - Transaction failed for userId=123\n"
            "Output: {\"date\": \"2024-01-15\", \"level\": \"ERROR\", \"service\": \"PaymentService\", "
            "\"message\": \"Transaction failed\", \"userId\": \"123\"}\n"
            "---\n"
            "Input: 2024-01-15 WARN OrderService - Retry attempt 3 for orderId=456\n"
            "Output: {\"date\": \"2024-01-15\", \"level\": \"WARN\", \"service\": \"OrderService\", "
            "\"message\": \"Retry attempt 3\", \"orderId\": \"456\"}\n"
            "---\n"
            "Now convert:\n"
            "Input: 2024-01-16 INFO AuthService - Login successful for userId=789 from ip=10.0.0.1\n"
            "Output:"
        )}
    ])
    print(f"\n  Log line converted to JSON:")
    print(f"  {result2}")


# ──────────────────────────────────────────────────────
# TECHNIQUE 3: CHAIN OF THOUGHT (CoT)
# Force the LLM to reason step by step.
# ──────────────────────────────────────────────────────
def demo_chain_of_thought():
    print("\n" + "=" * 60)
    print("TECHNIQUE 3: Chain of Thought (CoT)")
    print("=" * 60)
    print("Step-by-step reasoning improves accuracy on complex tasks.\n")

    problem = (
        "A Spring Boot application has 3 microservices. "
        "Service A calls Service B with a 200ms timeout. "
        "Service B calls Service C with a 150ms timeout. "
        "Service C takes 100ms to process. "
        "Network latency between each service is 20ms. "
        "What is the total response time for Service A, and will any timeout occur?"
    )

    # WITHOUT CoT
    result_no_cot = ask([
        {"role": "user", "content": problem}
    ])
    print(f"  ❌ WITHOUT Chain of Thought:")
    print(f"  {result_no_cot[:300]}")

    # WITH CoT
    result_with_cot = ask([
        {"role": "user", "content": (
            f"{problem}\n\n"
            "Think step by step:\n"
            "1. Calculate the time for Service C\n"
            "2. Calculate the time for Service B (including waiting for C)\n"
            "3. Calculate the time for Service A (including waiting for B)\n"
            "4. Check each timeout constraint\n"
            "5. Provide the final answer"
        )}
    ])
    print(f"\n  ✅ WITH Chain of Thought:")
    print(f"  {result_with_cot[:500]}")


# ──────────────────────────────────────────────────────
# TECHNIQUE 4: ROLE PROMPTING
# Assign a role to get domain-specific responses.
# ──────────────────────────────────────────────────────
def demo_role_prompting():
    print("\n" + "=" * 60)
    print("TECHNIQUE 4: Role Prompting")
    print("=" * 60)
    print("Same question, different roles = different answers.\n")

    question = "Should we move our Spring Boot monolith to microservices?"

    roles = [
        ("Startup CTO (10 engineers)", 
         "You are a startup CTO with a 10-person engineering team. Be pragmatic."),
        ("Enterprise Architect (FAANG)", 
         "You are an enterprise architect at a FAANG company. Think at scale."),
        ("DevOps Lead", 
         "You are a DevOps lead focused on deployment and operations."),
    ]

    for title, system in roles:
        result = ask([
            {"role": "system", "content": system},
            {"role": "user", "content": question}
        ])
        print(f"\n  🎭 {title}:")
        print(f"  {result[:250]}...")


# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 MODULE 1: Prompt Engineering Techniques\n")

    demo_zero_shot()
    demo_few_shot()
    demo_chain_of_thought()
    demo_role_prompting()

    print("\n✅ Experiment complete! Try modifying the examples and roles.\n")
