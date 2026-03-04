"""
MODULE 0 — Example 4: Build a Simple Chatbot
==============================================
A conversational chatbot that maintains history.

SETUP:
  1. pip install openai python-dotenv rich
  2. Create a .env file:  OPENAI_API_KEY=sk-your-key-here
  3. Run: python 04_chatbot.py

KEY CONCEPTS DEMONSTRATED:
  1. Conversation history (list of messages)
  2. System prompt (sets personality)
  3. Streaming responses (token-by-token output)
  4. Token usage tracking

JAVA ANALOGY:
  This is like building a REST controller that maintains session state.
  The "messages" list is our session — it accumulates the full conversation.
  
  @RestController
  class ChatController {
      List<Message> conversationHistory = new ArrayList<>();
      
      @PostMapping("/chat")
      ResponseEntity<String> chat(@RequestBody String userMessage) {
          conversationHistory.add(new Message("user", userMessage));
          String response = callLLM(conversationHistory);
          conversationHistory.add(new Message("assistant", response));
          return ResponseEntity.ok(response);
      }
  }
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ──────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────

MODEL = "gpt-4o-mini"
TEMPERATURE = 0.7
MAX_TOKENS = 500

# System prompt — defines the chatbot's personality and behavior
# This is the MOST important prompt. It runs before every response.
SYSTEM_PROMPT = """You are a friendly and knowledgeable AI teaching assistant \
specializing in helping Java/Spring Boot developers learn AI and LLM concepts.

Rules:
- Explain AI concepts using Java/Spring Boot analogies when possible
- Keep answers concise but thorough
- Use code examples when helpful
- If you don't know something, say so honestly
- Format responses with markdown for readability
"""


def create_initial_messages() -> list:
    """
    Initialize the conversation with just the system prompt.
    
    The messages list is the ENTIRE context the LLM sees.
    Every time we call the API, we send ALL messages.
    
    Structure:
    [
        {"role": "system",    "content": "You are..."},     ← Always first
        {"role": "user",      "content": "Hello"},          ← User's message
        {"role": "assistant", "content": "Hi there!"},      ← LLM's response
        {"role": "user",      "content": "Next question"},  ← User's next message
        ...
    ]
    """
    return [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]


def chat(messages: list, user_input: str) -> str:
    """
    Send a message and get a response.
    
    IMPORTANT: We send the ENTIRE conversation history every time.
    This is how the LLM "remembers" context — it doesn't actually
    remember anything, it re-reads the full history each time.
    
    This is why context window size matters!
    """
    # Add user's message to history
    messages.append({"role": "user", "content": user_input})

    # Call the API with full conversation history
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    # Extract the assistant's reply
    assistant_message = response.choices[0].message.content

    # Add assistant's reply to history (so next call includes it)
    messages.append({"role": "assistant", "content": assistant_message})

    # Return response and usage stats
    return assistant_message, response.usage


def chat_streaming(messages: list, user_input: str) -> str:
    """
    Same as chat(), but streams the response token-by-token.
    This gives a much better UX — like ChatGPT's typing effect.
    
    Java Analogy: This is like using Server-Sent Events (SSE) or 
    WebFlux Flux<String> instead of returning a complete ResponseEntity.
    """
    messages.append({"role": "user", "content": user_input})

    # stream=True makes the API return chunks as they're generated
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=True,  # ← This is the magic
    )

    # Collect the full response while printing each chunk
    full_response = ""
    print("\n🤖 ", end="", flush=True)

    for chunk in stream:
        # Each chunk contains a small piece of the response
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            full_response += delta

    print()  # New line after response

    # Add complete response to history
    messages.append({"role": "assistant", "content": full_response})
    return full_response


def print_help():
    """Print available commands."""
    print("""
╭──────────────────────────────────────────╮
│  COMMANDS                                │
│  /clear  — Reset conversation history    │
│  /history — Show conversation history    │
│  /tokens — Show token usage info         │
│  /help   — Show this help                │
│  /quit   — Exit the chatbot              │
╰──────────────────────────────────────────╯
    """)


def main():
    """Main chatbot loop."""
    print("╔══════════════════════════════════════════════╗")
    print("║  🤖 AI Learning Assistant                    ║")
    print("║  Module 0: Your First Chatbot                ║")
    print("║                                              ║")
    print("║  Type your questions about AI/LLM concepts.  ║")
    print("║  Type /help for commands.                    ║")
    print("╚══════════════════════════════════════════════╝")

    messages = create_initial_messages()
    total_tokens_used = 0

    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()

                if command == "/quit":
                    print("\n👋 Goodbye! Keep learning AI!\n")
                    break

                elif command == "/clear":
                    messages = create_initial_messages()
                    total_tokens_used = 0
                    print("🗑️  Conversation cleared.")

                elif command == "/history":
                    print(f"\n📜 Conversation history ({len(messages)} messages):")
                    for i, msg in enumerate(messages):
                        role = msg["role"].upper()
                        content = msg["content"][:80] + ("..." if len(msg["content"]) > 80 else "")
                        print(f"  [{i}] {role}: {content}")

                elif command == "/tokens":
                    print(f"\n📊 Total tokens used this session: {total_tokens_used}")
                    print(f"   Messages in history: {len(messages)}")
                    print(f"   Estimated cost (GPT-4o-mini): ${total_tokens_used * 0.00000015:.6f}")

                elif command == "/help":
                    print_help()

                else:
                    print(f"❓ Unknown command: {command}. Type /help for options.")
                continue

            # Send to LLM and get response (non-streaming version)
            response, usage = chat(messages, user_input)
            total_tokens_used += usage.total_tokens

            print(f"\n🤖 {response}")
            print(f"\n   ℹ️  Tokens: {usage.total_tokens} (in:{usage.prompt_tokens} out:{usage.completion_tokens})")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("   Make sure your OPENAI_API_KEY is set in .env")


if __name__ == "__main__":
    main()
