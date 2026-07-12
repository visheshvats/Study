import json
import re

# --- Mock LLM for demonstration ---
def ask_llm(user_message: str, system: str = "") -> str:
    if "Few-Shot" in system:
        if "crashes" in user_message: return "BUG"
        if "dark mode" in user_message: return "FEATURE_REQUEST"
        return "QUESTION"
    
    if "Chain of Thought" in system:
        return "THOUGHT: 3 calls left, costs 2 per operation. 3 divided by 2 is 1 with remainder. \nANSWER: 1 operation"
        
    if "Structured JSON" in system:
        # Intentionally adding markdown formatting to simulate real LLM behavior
        return "```json\n{\n  \"name\": \"Alice\",\n  \"skills\": [\"Java\", \"Spring\"]\n}\n```"
    
    return "Unknown Prompt"

# ---------------------------------------------------------

def demonstrate_few_shot():
    print("\n--- Pattern 1: Few-Shot Prompting ---")
    few_shot_system = """You classify customer feedback. (Few-Shot)
    Categories: BUG, FEATURE_REQUEST, PRAISE, QUESTION
    
    Examples:
    Feedback: "The app crashes when I open settings"
    Category: BUG
    
    Feedback: "Would love a dark mode option"
    Category: FEATURE_REQUEST
    
    Return ONLY the category word."""
    
    category = ask_llm("Why can't I export to PDF?", few_shot_system)
    print(f"Result: {category}")

def demonstrate_chain_of_thought():
    print("\n--- Pattern 2: Chain of Thought ---")
    cot_prompt = """Solve the problem step by step. (Chain of Thought)
    Format:
    THOUGHT: <your reasoning>
    ANSWER: <final answer only>"""
    
    result = ask_llm("A user has 3 API calls remaining. Each operation costs 2 calls. How many?", cot_prompt)
    print(result)

def demonstrate_structured_json():
    print("\n--- Pattern 3: Structured JSON Output ---")
    json_system = """Extract structured data and return ONLY valid JSON. (Structured JSON)"""
    
    raw = ask_llm("Alice is a 28-year-old Java developer with 5 years of experience.", json_system)
    print("Raw LLM Output:")
    print(raw)
    
    # Defensive JSON parsing
    def extract_json(text: str) -> dict:
        # Strip markdown fences if present
        clean = re.sub(r'```(?:json)?|```', '', text).strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON"}

    data = extract_json(raw)
    print("\nParsed Data:")
    print(f"Skills array: {data.get('skills')}")

if __name__ == "__main__":
    demonstrate_few_shot()
    demonstrate_chain_of_thought()
    demonstrate_structured_json()
