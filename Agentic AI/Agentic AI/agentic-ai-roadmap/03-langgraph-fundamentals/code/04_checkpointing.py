# Note: In a real environment, you would use:
# from langgraph.checkpoint.memory import MemorySaver
# memory = MemorySaver()
# graph = builder.compile(checkpointer=memory)

class MockMemorySaver:
    """Mocks the behavior of LangGraph's checkpointer."""
    def __init__(self):
        # Stores state snapshots keyed by thread_id
        self.storage = {}
        
    def get_state(self, thread_id: str) -> dict:
        return self.storage.get(thread_id, {"messages": []})
        
    def save_state(self, thread_id: str, state: dict):
        self.storage[thread_id] = state
        print(f"[Checkpointer] Saved state for thread '{thread_id}'")

class MockStateGraph:
    def __init__(self, checkpointer: MockMemorySaver):
        self.checkpointer = checkpointer
        
    def invoke(self, input_data: dict, config: dict):
        thread_id = config["configurable"]["thread_id"]
        
        # 1. Load state from memory
        state = self.checkpointer.get_state(thread_id)
        
        # 2. Append new input
        if "messages" in input_data:
            state["messages"].extend(input_data["messages"])
            
        # 3. Execute Graph (Mock LLM generating response based on full history)
        full_history_text = " ".join(state["messages"])
        if "alice" in full_history_text.lower():
            response = "Your name is Alice."
        else:
            response = "I don't know your name."
            
        state["messages"].append(response)
        print(f"[Graph Output]: {response}")
        
        # 4. Save state back to memory
        self.checkpointer.save_state(thread_id, state)
        return state

def demonstrate_checkpointing():
    print("--- 4. Persistent Memory (Checkpointing) ---")
    memory = MockMemorySaver()
    graph = MockStateGraph(checkpointer=memory)
    
    # User 1 (Alice) connects
    config_alice = {"configurable": {"thread_id": "session-alice-001"}}
    
    print("\n--- Turn 1 (Alice) ---")
    print("User: My name is Alice.")
    graph.invoke({"messages": ["My name is Alice."]}, config=config_alice)
    
    # A completely different User connects
    config_bob = {"configurable": {"thread_id": "session-bob-999"}}
    print("\n--- Turn 1 (Bob) ---")
    print("User: What is my name?")
    graph.invoke({"messages": ["What is my name?"]}, config=config_bob)
    
    # Alice reconnects later (simulating a new HTTP request)
    print("\n--- Turn 2 (Alice - Reconnected) ---")
    print("User: What is my name?")
    # The checkpointer automatically injects the old messages!
    graph.invoke({"messages": ["What is my name?"]}, config=config_alice)
    
    # Inspecting state
    print("\n--- Inspecting Checkpointer Database ---")
    alice_state = memory.get_state("session-alice-001")
    print(f"Alice's saved messages: {alice_state['messages']}")

if __name__ == "__main__":
    demonstrate_checkpointing()
