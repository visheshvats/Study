"""
MODULE 1 — Example 2: Structured Output
=========================================
Force the LLM to return parseable structured data.

This is CRITICAL for production systems where LLM output feeds into
downstream code (save to DB, send to API, display in UI).

SETUP:
  pip install openai python-dotenv pydantic
  OPENAI_API_KEY in .env

RUN:
  python 02_structured_output.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ──────────────────────────────────────────────────────
# METHOD 1: Prompt-based JSON (works with any LLM)
# ──────────────────────────────────────────────────────
def method_prompt_based():
    """
    Ask for JSON in the prompt itself.
    Works with any model but output is NOT guaranteed to be valid JSON.
    
    Java Analogy: This is like hoping the client sends valid JSON
    without using @Valid — it usually works but can fail.
    """
    print("=" * 60)
    print("METHOD 1: Prompt-Based JSON (any LLM)")
    print("=" * 60)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You extract bug report data from text. "
                "Return ONLY valid JSON. No markdown, no explanation.\n"
                "Schema: {\"title\": str, \"severity\": \"CRITICAL|HIGH|MEDIUM|LOW\", "
                "\"component\": str, \"steps_to_reproduce\": [str], \"expected\": str, \"actual\": str}"
            )},
            {"role": "user", "content": (
                "Users are reporting that the payment page crashes when they click "
                "'Submit' with an expired credit card. The page shows a white screen. "
                "This is happening on Chrome and Firefox. It should show an error message "
                "saying 'Card expired, please use a different card.' This affects 15% of "
                "checkout attempts and is causing revenue loss."
            )}
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content
    print(f"\n  Raw output:\n  {raw}")

    # Parse and validate
    try:
        parsed = json.loads(raw)
        print(f"\n  ✅ Valid JSON! Severity: {parsed['severity']}")
        print(f"  Steps: {len(parsed.get('steps_to_reproduce', []))} steps extracted")
    except json.JSONDecodeError as e:
        print(f"\n  ❌ Invalid JSON: {e}")


# ──────────────────────────────────────────────────────
# METHOD 2: response_format parameter (OpenAI specific)
# ──────────────────────────────────────────────────────
def method_response_format():
    """
    Use OpenAI's response_format parameter to FORCE JSON output.
    The model is constrained to only produce valid JSON.
    
    Java Analogy: This is like using @Valid + @RequestBody — the
    framework guarantees valid JSON structure.
    """
    print("\n" + "=" * 60)
    print("METHOD 2: response_format Parameter (guaranteed JSON)")
    print("=" * 60)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You analyze Java code and return a code review in JSON format.\n"
                "Include: issues (array of {type, severity, line, description, fix}), "
                "overall_score (1-10), summary."
            )},
            {"role": "user", "content": '''
Review this Java code:

public class UserService {
    public User getUser(String id) {
        User user = userRepository.findById(id);
        return user.getName().toUpperCase();
    }
    
    public void deleteUser(String id) {
        userRepository.deleteById(id);
        System.out.println("User deleted: " + id);
    }
    
    public String getPassword(String userId) {
        return userRepository.findById(userId).getPassword();
    }
}
'''}
        ],
        temperature=0,
        response_format={"type": "json_object"},  # ← FORCES valid JSON output
    )

    result = json.loads(response.choices[0].message.content)
    print(f"\n  Overall Score: {result.get('overall_score', 'N/A')}/10")
    print(f"  Issues Found: {len(result.get('issues', []))}")
    for issue in result.get("issues", []):
        print(f"    [{issue.get('severity', '?')}] {issue.get('description', '')[:80]}")


# ──────────────────────────────────────────────────────
# METHOD 3: Few-shot for consistent format
# ──────────────────────────────────────────────────────
def method_few_shot_format():
    """
    Use few-shot examples to teach the EXACT output format you want.
    Most reliable method for non-JSON structured output.
    """
    print("\n" + "=" * 60)
    print("METHOD 3: Few-Shot Structured Output")
    print("=" * 60)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "Convert natural language API requirements into Spring Boot "
                "controller method signatures. Follow the exact format shown."
            )},
            # Example 1
            {"role": "user", "content": "Create an endpoint to get a user by their ID"},
            {"role": "assistant", "content": (
                "@GetMapping(\"/users/{id}\")\n"
                "public ResponseEntity<UserDTO> getUserById(\n"
                "    @PathVariable Long id\n"
                ") { }"
            )},
            # Example 2
            {"role": "user", "content": "Create an endpoint to search users by name with pagination"},
            {"role": "assistant", "content": (
                "@GetMapping(\"/users/search\")\n"
                "public ResponseEntity<Page<UserDTO>> searchUsers(\n"
                "    @RequestParam String name,\n"
                "    @RequestParam(defaultValue = \"0\") int page,\n"
                "    @RequestParam(defaultValue = \"20\") int size\n"
                ") { }"
            )},
            # Actual request
            {"role": "user", "content": (
                "Create an endpoint to update a user's email, "
                "requiring authentication and accepting JSON body"
            )},
        ],
        temperature=0,
    )

    print(f"\n  Generated Spring Boot endpoint:")
    print(f"  {response.choices[0].message.content}")


# ──────────────────────────────────────────────────────
# METHOD 4: Multiple structured extractions in one call
# ──────────────────────────────────────────────────────
def method_batch_extraction():
    """
    Extract multiple structured entities from unstructured text.
    Common in data pipelines and document processing.
    """
    print("\n" + "=" * 60)
    print("METHOD 4: Batch Entity Extraction")
    print("=" * 60)

    unstructured_text = """
    Meeting Notes - Q4 Planning
    Date: Jan 15, 2025
    
    Attendees: Sarah (Engineering VP), Mike (Product), Lisa (DevOps)
    
    Key Decisions:
    - Migrate payment service to Kafka by March 2025. Budget: $50K. Owner: Sarah.
    - Hire 3 senior backend engineers. Budget: $450K/yr. Owner: Mike.
    - Set up monitoring with Grafana dashboards. Deadline: Feb 2025. Owner: Lisa.
    
    Action Items:
    - Sarah to draft migration plan by Jan 22
    - Mike to post job listings by Jan 18
    - Lisa to evaluate Grafana vs Datadog by Jan 20
    
    Next meeting: Jan 22, 2025
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "Extract structured data from meeting notes. Return JSON with:\n"
                "{\n"
                '  "meeting_date": "YYYY-MM-DD",\n'
                '  "attendees": [{"name": str, "role": str}],\n'
                '  "decisions": [{"description": str, "owner": str, "budget": str, "deadline": str}],\n'
                '  "action_items": [{"assignee": str, "task": str, "due_date": "YYYY-MM-DD"}],\n'
                '  "next_meeting": "YYYY-MM-DD"\n'
                "}"
            )},
            {"role": "user", "content": unstructured_text}
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    print(f"\n  Meeting: {result.get('meeting_date')}")
    print(f"  Attendees: {len(result.get('attendees', []))}")
    print(f"  Decisions: {len(result.get('decisions', []))}")
    print(f"  Action Items: {len(result.get('action_items', []))}")
    print(f"\n  Full JSON:")
    print(f"  {json.dumps(result, indent=2)}")


# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 MODULE 1: Structured Output Techniques\n")

    method_prompt_based()
    method_response_format()
    method_few_shot_format()
    method_batch_extraction()

    print("\n✅ Key takeaway: Always use structured output in production!")
    print("   response_format={'type': 'json_object'} is your best friend.\n")
