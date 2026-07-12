import json
from typing import Any, Dict, List

# ─── Define tools (what the LLM can invoke) ───
# This is JSON Schema, which Anthropic and OpenAI use to understand your functions.
TOOLS = [
    {
        "name": "search_knowledge_base",
        "description": "Search internal knowledge base for information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 3}
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_ticket",
        "description": "Create a support ticket",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
                "description": {"type": "string"}
            },
            "required": ["title", "priority", "description"]
        }
    }
]

# ─── Tool implementations (your actual Python logic) ───
def search_knowledge_base(query: str, max_results: int = 3) -> list:
    print(f"[Executing] search_knowledge_base(query='{query}', max_results={max_results})")
    # In a real app, this would query Elasticsearch, ChromaDB, etc.
    return [{"id": 1, "title": f"Article about {query}", "snippet": "Login issues are usually caused by expired tokens."}]

def create_ticket(title: str, priority: str, description: str) -> dict:
    print(f"[Executing] create_ticket(title='{title}', priority='{priority}')")
    # In a real app, this calls JIRA or ServiceNow APIs.
    return {"ticket_id": "TKT-999", "status": "CREATED", "title": title}

# Map tool names to actual functions
TOOL_REGISTRY = {
    "search_knowledge_base": search_knowledge_base,
    "create_ticket": create_ticket,
}

# ─── Mocking the LLM API for demonstration ───
class MockToolLLM:
    def create_message(self, messages: List[Dict], tools: List[Dict]) -> Dict:
        """Mocks an LLM deciding to use a tool or returning text."""
        last_msg = messages[-1]['content'].lower()
        
        # Scenario 1: LLM decides to create a ticket
        if "ticket" in last_msg and "login" in last_msg:
            return {
                "stop_reason": "tool_use",
                "content": [
                    # A dummy text block sometimes precedes tool calls
                    type('obj', (object,), {'type': 'text', 'text': 'I will create a ticket for you.'})(),
                    # The actual tool use block
                    type('obj', (object,), {
                        'type': 'tool_use', 
                        'id': 'tool_123', 
                        'name': 'create_ticket', 
                        'input': {
                            'title': 'Login Failure', 
                            'priority': 'HIGH', 
                            'description': 'User cannot login'
                        }
                    })()
                ]
            }
            
        # Scenario 2: LLM processes the tool result and gives final answer
        if messages[-1]['role'] == 'user' and isinstance(messages[-1]['content'], list):
            if messages[-1]['content'][0].get('type') == 'tool_result':
                result = json.loads(messages[-1]['content'][0]['content'])
                return {
                    "stop_reason": "end_turn",
                    "content": [type('obj', (object,), {'text': f"I've created the ticket. The ID is {result['ticket_id']}."})()]
                }
                
        return {
            "stop_reason": "end_turn",
            "content": [type('obj', (object,), {'text': "How can I help?"})()]
        }

mock_client = MockToolLLM()

# ─── The Agentic Loop ───
def run_tool_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    print("--- Starting Agentic Loop ---")
    while True:
        # In reality: response = client.messages.create(...)
        response = mock_client.create_message(messages=messages, tools=TOOLS)

        if response["stop_reason"] == "tool_use":
            # The LLM paused generation to ask us to run a tool
            tool_block = next(b for b in response["content"] if getattr(b, 'type', '') == "tool_use")
            tool_name   = tool_block.name
            tool_input  = tool_block.input
            tool_id     = tool_block.id

            print(f"🤖 LLM requested tool: {tool_name}")

            # Execute the local Python function
            fn = TOOL_REGISTRY.get(tool_name)
            tool_result = fn(**tool_input) if fn else {"error": "Unknown tool"}

            # Feed the result BACK to the LLM
            # 1. Append the LLM's tool request
            messages.append({"role": "assistant", "content": response["content"]})
            # 2. Append our tool result as the User
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": json.dumps(tool_result)
                }]
            })
            print("🔁 Feeding result back to LLM...")
            # Loop continues...
            
        else:
            # Final text answer
            text_block = next(b for b in response["content"] if hasattr(b, "text"))
            return text_block.text

if __name__ == "__main__":
    final_answer = run_tool_agent("I need to create a HIGH priority ticket: Login fails for enterprise users")
    print(f"\n✅ Final LLM Answer: {final_answer}")
