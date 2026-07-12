import math
import json

# Note: In a real environment, you would use:
# from langchain_core.tools import tool
# from langgraph.prebuilt import create_react_agent
#
# @tool
# def calculator(expression: str) -> str: ...

# Mocking the `@tool` decorator behavior conceptually
def calculator(expression: str) -> str:
    """Evaluate a math expression safely."""
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def get_stock_price(ticker: str) -> str:
    """Get the current stock price for a ticker symbol."""
    mock_prices = {"AAPL": 189.50, "GOOG": 2750.30, "MSFT": 415.20}
    price = mock_prices.get(ticker.upper(), None)
    if price:
        return json.dumps({"ticker": ticker, "price": price, "currency": "USD"})
    return f"Unknown ticker: {ticker}"

def demonstrate_react_agent():
    print("--- 3. ReAct Agent with Tools ---")
    print("In LangGraph, 'create_react_agent' builds a complex graph behind the scenes.")
    print("It loops between an LLM Node and a Tool Execution Node until the LLM stops asking for tools.\n")
    
    query = "What is 15% of AAPL's stock price?"
    print(f"[User]: {query}")
    
    # Mocking the ReAct loop trace:
    print("\n[Graph Trace]")
    print("1. [Node: agent] LLM reasons: 'I need to find AAPL stock price first.'")
    print("   -> Invokes tool: get_stock_price('AAPL')")
    
    stock_res = get_stock_price("AAPL")
    print(f"2. [Node: tools] Tool returns: {stock_res}")
    
    print("3. [Node: agent] LLM reasons: 'Price is 189.5. Now I need 15% of that.'")
    print("   -> Invokes tool: calculator('189.5 * 0.15')")
    
    calc_res = calculator("189.5 * 0.15")
    print(f"4. [Node: tools] Tool returns: {calc_res}")
    
    print(f"5. [Node: agent] LLM reasons: 'I have the final answer.'")
    print(f"   -> Final Output: 15% of AAPL stock price is ${calc_res}")

if __name__ == "__main__":
    demonstrate_react_agent()
