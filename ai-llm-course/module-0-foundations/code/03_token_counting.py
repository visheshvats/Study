"""
MODULE 0 — Example 3: Token Counting & Cost Estimation
=======================================================
Learn how tokens work, count them, and estimate API costs.

SETUP:
  1. pip install tiktoken
  2. Run: python 03_token_counting.py

NO API KEY NEEDED — this runs entirely locally using the tiktoken library!

KEY LESSON:
  Understanding tokens is essential for:
  - Staying within context window limits
  - Estimating costs before making API calls
  - Optimizing prompts for efficiency
"""

import tiktoken


def show_tokenization():
    """
    Shows how text gets broken into tokens.
    
    Java Analogy: Think of this as a custom StringTokenizer that splits
    based on statistical patterns, not just whitespace.
    """
    print("=" * 60)
    print("EXAMPLE 1: How Tokenization Works")
    print("=" * 60)

    # Get the tokenizer for GPT-4o / GPT-4o-mini
    # Different models use different tokenizers!
    encoder = tiktoken.encoding_for_model("gpt-4o-mini")

    examples = [
        "Hello, world!",
        "Spring Boot simplifies Java web application development",
        "unhappiness",
        "API gateway load balancer microservices",
        "こんにちは世界",  # Japanese: uses more tokens per character
        "SELECT * FROM users WHERE id = 42;",
        '{"name": "John", "age": 30}',
    ]

    for text in examples:
        tokens = encoder.encode(text)
        token_strings = [encoder.decode([t]) for t in tokens]

        print(f"\n  Text:   \"{text}\"")
        print(f"  Tokens: {len(tokens)}")
        print(f"  Split:  {token_strings}")


def count_tokens_for_prompt():
    """
    Count tokens for a realistic prompt to estimate costs.
    
    GPT-4o-mini pricing (as of 2024):
      - Input:  $0.15 per 1M tokens
      - Output: $0.60 per 1M tokens
    
    GPT-4o pricing:
      - Input:  $2.50 per 1M tokens
      - Output: $10.00 per 1M tokens
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Cost Estimation")
    print("=" * 60)

    encoder = tiktoken.encoding_for_model("gpt-4o-mini")

    # A realistic system prompt + user message
    system_prompt = (
        "You are a senior Java Spring Boot architect. "
        "You explain concepts clearly using code examples. "
        "Always provide practical, production-ready advice. "
        "Format your responses using markdown."
    )

    user_message = (
        "I have a Spring Boot microservice that processes orders. "
        "It currently uses synchronous REST calls to the inventory service "
        "and payment service. Under high load (>1000 RPS), we're seeing "
        "timeout errors. Should I switch to event-driven architecture "
        "with Kafka? What are the trade-offs? "
        "Please provide a migration plan with code examples."
    )

    system_tokens = len(encoder.encode(system_prompt))
    user_tokens = len(encoder.encode(user_message))
    total_input_tokens = system_tokens + user_tokens

    # Estimate output (typically 2-4x the input for detailed answers)
    estimated_output_tokens = total_input_tokens * 3

    print(f"\n  System prompt tokens: {system_tokens}")
    print(f"  User message tokens:  {user_tokens}")
    print(f"  Total input tokens:   {total_input_tokens}")
    print(f"  Estimated output:     ~{estimated_output_tokens}")

    # Cost calculation
    models = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},      # per 1M tokens
        "gpt-4o":      {"input": 2.50, "output": 10.00},
    }

    print(f"\n  Cost per call:")
    for model, prices in models.items():
        input_cost = (total_input_tokens / 1_000_000) * prices["input"]
        output_cost = (estimated_output_tokens / 1_000_000) * prices["output"]
        total_cost = input_cost + output_cost
        print(f"    {model}: ${total_cost:.6f} per call")
        print(f"      At 10K calls/day: ${total_cost * 10000:.2f}/day")


def context_window_check():
    """
    Check if your content fits within a model's context window.
    
    This is critical when building RAG systems — you need to know
    how many document chunks you can fit alongside the prompt.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Context Window Capacity")
    print("=" * 60)

    encoder = tiktoken.encoding_for_model("gpt-4o-mini")

    # Model context windows
    context_windows = {
        "gpt-4o-mini": 128_000,
        "gpt-4o":      128_000,
        "gpt-3.5":     16_385,
    }

    # Simulate: system prompt + document chunks + user question
    system_prompt = "You are a helpful assistant that answers based on the provided documents."
    system_tokens = len(encoder.encode(system_prompt))

    # Simulate a document chunk (average 500 tokens each)
    sample_chunk = "Lorem ipsum " * 250  # ~500 tokens
    chunk_tokens = len(encoder.encode(sample_chunk))

    user_question = "Based on the documents, what is the main topic?"
    question_tokens = len(encoder.encode(user_question))

    # Reserve tokens for the response
    response_reserve = 2000  # Leave room for the answer

    print(f"\n  System prompt: {system_tokens} tokens")
    print(f"  Each chunk:    {chunk_tokens} tokens")
    print(f"  User question: {question_tokens} tokens")
    print(f"  Response reserve: {response_reserve} tokens")

    print(f"\n  How many document chunks can we fit?")
    for model, window in context_windows.items():
        available = window - system_tokens - question_tokens - response_reserve
        max_chunks = available // chunk_tokens
        print(f"    {model} ({window:,} tokens): ~{max_chunks} chunks")


def token_optimization_tips():
    """
    Practical tips for reducing token usage.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Token Optimization Tips")
    print("=" * 60)

    encoder = tiktoken.encoding_for_model("gpt-4o-mini")

    # Tip 1: Concise prompts use fewer tokens
    verbose = (
        "I would like you to please explain to me in great detail "
        "what the concept of dependency injection is and how it works "
        "in the Spring Boot framework for Java applications."
    )
    concise = "Explain dependency injection in Spring Boot. Be concise."

    verbose_tokens = len(encoder.encode(verbose))
    concise_tokens = len(encoder.encode(concise))

    print(f"\n  Tip 1: Be concise")
    print(f"    Verbose: {verbose_tokens} tokens")
    print(f"    Concise: {concise_tokens} tokens")
    print(f"    Savings: {verbose_tokens - concise_tokens} tokens ({(1 - concise_tokens/verbose_tokens)*100:.0f}%)")

    # Tip 2: JSON keys add up
    verbose_json = '{"customer_full_name": "John", "customer_email_address": "john@email.com"}'
    concise_json = '{"name": "John", "email": "john@email.com"}'

    print(f"\n  Tip 2: Shorter JSON keys")
    print(f"    Verbose keys: {len(encoder.encode(verbose_json))} tokens")
    print(f"    Concise keys: {len(encoder.encode(concise_json))} tokens")

    # Tip 3: Abbreviations in system prompts
    print(f"\n  Tip 3: At scale, every token saved multiplies")
    print(f"    Saving 50 tokens/call × 100K calls/day = 5M tokens/day")
    print(f"    At GPT-4o rates: ~$12.50/day saved")


# ──────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 MODULE 0: Token Counting & Cost Estimation\n")

    show_tokenization()
    count_tokens_for_prompt()
    context_window_check()
    token_optimization_tips()

    print("\n✅ Key takeaway: Understanding tokens helps you optimize cost and performance.")
    print("   Always count tokens before production deployment.\n")
