import json
from typing import Optional, List, Dict, Any, Tuple

# Java: public String greet(String name, int times) { return ...; }
def greet(name: str, times: int = 1) -> str:
    """A simple function with type hints and a default argument."""
    return f"Hello, {name}! " * times

# Optional param + complex return
def create_message(
    content: str,
    role: str = "user",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Creates a message dictionary.
    Notice the safe handling of the optional 'metadata' argument.
    """
    msg: Dict[str, Any] = {"role": role, "content": content}
    if metadata:
        msg["metadata"] = metadata
    return msg

# *args (varargs), **kwargs (named params map)
def build_prompt(*parts: str, separator: str = "\n\n") -> str:
    """
    *parts takes any number of positional arguments (like String... parts in Java).
    """
    return separator.join(parts)

# Error handling
def safe_parse_json(text: str) -> Tuple[Optional[dict], Optional[str]]:
    """
    Returns a Tuple (Data, Error Message). 
    This pattern is common in Go and sometimes used in Python to avoid throwing exceptions.
    """
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, str(e)

if __name__ == "__main__":
    print("--- Greeting ---")
    print(greet("Alice", 2))
    
    print("\n--- Create Message ---")
    msg = create_message("How does RAG work?", metadata={"session_id": "123"})
    print(msg)
    
    print("\n--- Build Prompt (*args) ---")
    result = build_prompt("Context: ...", "Answer:", "Reasoning:", separator="\n---\n")
    print(result)
    
    print("\n--- Error Handling ---")
    data, error = safe_parse_json('{"valid": true}')
    if error:
        print(f"Parse failed: {error}")
    else:
        print(f"Parsed safely: {data}")
        
    bad_data, bad_error = safe_parse_json('{"invalid": true')
    print(f"Handled expected error: {bad_error}")
