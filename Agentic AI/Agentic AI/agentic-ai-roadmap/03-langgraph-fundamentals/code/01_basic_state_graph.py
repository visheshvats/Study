from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import HumanMessage, AIMessage

# --- Mock LLM ---
class MockChatAnthropic:
    def invoke(self, messages: List) -> AIMessage:
        last_user_msg = [m.content for m in messages if isinstance(m, HumanMessage)][-1]
        return AIMessage(content=f"Mocked Response to: '{last_user_msg}'")

llm = MockChatAnthropic()
# ----------------

# ─── State definition ───
# TypedDict = what data the graph carries between nodes
class AgentState(TypedDict):
    # 'operator.add' acts like LangGraph's add_messages. 
    # It appends to the list instead of overwriting it.
    messages: Annotated[List, operator.add] 
    step_count: int
    context: str

# ─── Nodes (pure functions: State → partial State) ───
def process_node(state: AgentState) -> dict:
    print("[Node: process_node] Executing...")
    response = llm.invoke(state["messages"])
    
    # We return ONLY the fields we want to update
    return {
        "messages": [response],       # 'operator.add' will append this automatically
        "step_count": state.get("step_count", 0) + 1
    }

def enrich_context_node(state: AgentState) -> dict:
    print("[Node: enrich_context_node] Executing...")
    last_msg = state["messages"][-1]
    return {"context": f"Processed message: {last_msg.content[:50]}..."}

def demonstrate_graph():
    print("--- 1. Basic State Graph ---")
    
    # ─── Build graph ───
    # Note: In a real environment, you would use:
    # from langgraph.graph import StateGraph, END
    # But to keep this script 100% runnable without the langgraph dependency installed,
    # we mock the builder pattern conceptually.
    
    class MockGraphRunner:
        def invoke(self, initial_state: dict):
            print("\nStarting Graph Execution...")
            state = dict(initial_state)
            
            # 1. Execute 'process' node
            update1 = process_node(state)
            state["messages"] = state.get("messages", []) + update1["messages"]
            state["step_count"] = update1["step_count"]
            
            # 2. Execute 'enrich' node
            update2 = enrich_context_node(state)
            state["context"] = update2["context"]
            
            print("Graph Execution Complete.\n")
            return state

    graph = MockGraphRunner()
    
    # ─── Run ───
    result = graph.invoke({
        "messages": [HumanMessage(content="What is LangGraph?")],
        "step_count": 0,
        "context": ""
    })
    
    print("--- Final State ---")
    print(f"Context: {result['context']}")
    print(f"Total Steps: {result['step_count']}")
    print(f"Messages count: {len(result['messages'])}")

if __name__ == "__main__":
    demonstrate_graph()
