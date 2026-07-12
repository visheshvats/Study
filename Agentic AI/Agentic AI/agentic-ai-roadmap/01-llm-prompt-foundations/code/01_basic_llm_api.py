import os
from typing import List, Dict

# In a real environment, you would use:
# from anthropic import Anthropic
# from dotenv import load_dotenv
# load_dotenv()
# client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# --- Mocking the Anthropic Client for this exercise ---
class MockAnthropicClient:
    def create_message(self, messages: List[Dict], system: str = "", **kwargs) -> str:
        last_msg = messages[-1]['content'].lower()
        if "name" in last_msg and "alice" in last_msg:
            return "I will remember that your name is Alice."
        elif "my name" in last_msg:
            # Look back in history
            for msg in messages:
                if "alice" in msg['content'].lower():
                    return "Your name is Alice."
            return "I don't know your name."
        return f"Echo response to: {last_msg}"

client = MockAnthropicClient()

# ---------------------------------------------------------

def chat_with_history(messages: List[Dict], system: str = "") -> str:
    """
    Demonstrates manual history management.
    The LLM API is stateless; you MUST pass the full array every time!
    """
    print(f"--- Sending {len(messages)} messages to LLM ---")
    
    # In reality: response = client.messages.create(model="claude-...", messages=messages, system=system)
    assistant_reply = client.create_message(messages=messages, system=system)
    
    # Append reply to history (caller is responsible for this!)
    messages.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply

if __name__ == "__main__":
    # Java Devs: Think of this list as your in-memory session.
    history = []
    
    print("\n[Turn 1]")
    history.append({"role": "user", "content": "Hi, my name is Alice. Remember that."})
    r1 = chat_with_history(history, system="You have a good memory.")
    print(f"Assistant: {r1}")
    
    print("\n[Turn 2]")
    history.append({"role": "user", "content": "What is my name?"})
    # If we didn't pass 'history' here, the LLM wouldn't know!
    r2 = chat_with_history(history)
    print(f"Assistant: {r2}")
    
    print("\nFinal History State:")
    import json
    print(json.dumps(history, indent=2))
