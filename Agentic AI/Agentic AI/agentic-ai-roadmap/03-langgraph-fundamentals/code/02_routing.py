from typing import TypedDict, Literal
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# --- Mock LLM ---
class MockChatAnthropic:
    def invoke(self, messages: list) -> AIMessage:
        text = str([m.content for m in messages]).lower()
        if "classify" in text:
            if "invoice" in text or "money" in text: return AIMessage(content="billing")
            if "bug" in text or "error" in text: return AIMessage(content="technical")
            return AIMessage(content="general")
        
        # Responses for specialist nodes
        if "engineer" in text: return AIMessage(content="[Tech Expert] Have you tried turning it off and on again?")
        if "billing" in text: return AIMessage(content="[Billing Expert] Let me check your last invoice.")
        return AIMessage(content="[General] How can I help you today?")

llm = MockChatAnthropic()
# ----------------

class RouterState(TypedDict):
    query: str
    category: str    # "technical" | "billing" | "general"
    response: str

# ─── Classification node ───
def classify(state: RouterState) -> dict:
    prompt = f"Classify this query: {state['query']}"
    result = llm.invoke([HumanMessage(content=prompt)])
    category = result.content.strip().lower()
    print(f"[Node: classify] Determined category: '{category}'")
    return {"category": category}

# ─── Specialist nodes ───
def handle_technical(state: RouterState) -> dict:
    print("[Node: technical] Handling technical query...")
    reply = llm.invoke([SystemMessage(content="engineer"), HumanMessage(content=state["query"])])
    return {"response": reply.content}

def handle_billing(state: RouterState) -> dict:
    print("[Node: billing] Handling billing query...")
    reply = llm.invoke([SystemMessage(content="billing"), HumanMessage(content=state["query"])])
    return {"response": reply.content}

def handle_general(state: RouterState) -> dict:
    print("[Node: general] Handling general query...")
    reply = llm.invoke([HumanMessage(content=state["query"])])
    return {"response": reply.content}

# ─── Router function — returns the name of the NEXT NODE ───
def route(state: RouterState) -> Literal["technical", "billing", "general"]:
    """Conditional Edge logic."""
    cat = state.get("category", "general")
    if cat in ("technical", "billing"):
        return cat
    return "general"

def demonstrate_routing():
    print("--- 2. Conditional Routing Graph ---")
    
    class MockRouterGraph:
        def invoke(self, state: dict):
            # 1. Entry Point
            state.update(classify(state))
            
            # 2. Conditional Edge
            next_node = route(state)
            print(f"[Router] Routing to node: -> {next_node}")
            
            # 3. Destination Nodes
            if next_node == "technical":
                state.update(handle_technical(state))
            elif next_node == "billing":
                state.update(handle_billing(state))
            else:
                state.update(handle_general(state))
                
            return state

    graph = MockRouterGraph()
    
    print("\nTest 1: Billing Query")
    r1 = graph.invoke({"query": "My invoice shows the wrong amount", "category": "", "response": ""})
    print(f"Final Reply: {r1['response']}")
    
    print("\nTest 2: Tech Query")
    r2 = graph.invoke({"query": "I am getting a 500 server error", "category": "", "response": ""})
    print(f"Final Reply: {r2['response']}")

if __name__ == "__main__":
    demonstrate_routing()
