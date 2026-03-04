"""
MODULE 0 — Example 1: Calling an LLM API
==========================================
This script shows how to call the OpenAI API (GPT model).

SETUP:
  1. pip install openai python-dotenv
  2. Create a .env file:  OPENAI_API_KEY=sk-your-key-here
  3. Run: python 01_call_llm_api.py

JAVA ANALOGY:
  This is like calling a REST API with RestTemplate/WebClient.
  The OpenAI API is just a POST request to https://api.openai.com/v1/chat/completions
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env file (like @Value in Spring Boot)
load_dotenv()

# Create the client (like creating a RestTemplate bean)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def basic_call():
    """
    The simplest possible LLM API call.
    
    This is equivalent to this curl:
    
    curl https://api.openai.com/v1/chat/completions \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "What is Java?"}]
      }'
    """
    print("=" * 60)
    print("EXAMPLE 1: Basic API Call")
    print("=" * 60)

    # The API call — this is the core of everything
    response = client.chat.completions.create(
        model="gpt-4o-mini",         # Which model to use
        messages=[                    # The conversation (list of messages)
            {
                "role": "user",       # Who is speaking: "system", "user", or "assistant"
                "content": "Explain what Java is in 2 sentences."  # The actual text
            }
        ],
        temperature=0.7,             # Creativity (0=deterministic, 2=very random)
        max_tokens=100,              # Maximum response length
    )

    # Extract the response text
    answer = response.choices[0].message.content

    # Print results
    print(f"\nModel: {response.model}")
    print(f"Answer: {answer}")
    print(f"\nToken Usage:")
    print(f"  Input tokens:  {response.usage.prompt_tokens}")
    print(f"  Output tokens: {response.usage.completion_tokens}")
    print(f"  Total tokens:  {response.usage.total_tokens}")


def call_with_system_prompt():
    """
    System prompts set the LLM's behavior/personality.
    
    Think of system prompt as the @Configuration for the LLM.
    It runs BEFORE the user's message and shapes all responses.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: With System Prompt")
    print("=" * 60)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            # System prompt — sets behavior (like a @Configuration bean)
            {
                "role": "system",
                "content": (
                    "You are a senior Java architect. "
                    "Explain everything using Java/Spring Boot analogies. "
                    "Keep answers concise."
                )
            },
            # User prompt — the actual question
            {
                "role": "user",
                "content": "What is an embedding in AI?"
            }
        ],
        temperature=0.3,  # Lower = more focused, factual
    )

    print(f"\nAnswer: {response.choices[0].message.content}")


def temperature_comparison():
    """
    Shows how temperature affects output.
    Run this multiple times to see the difference!
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Temperature Comparison")
    print("=" * 60)

    prompt = "Write one creative sentence about coding."

    for temp in [0.0, 0.7, 1.5]:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=50,
        )
        print(f"\n  Temperature {temp}: {response.choices[0].message.content}")


# ──────────────────────────────────────────
# Run all examples
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 MODULE 0: Calling an LLM API\n")

    basic_call()
    call_with_system_prompt()
    temperature_comparison()

    print("\n✅ Done! Try modifying the prompts and temperatures.")
