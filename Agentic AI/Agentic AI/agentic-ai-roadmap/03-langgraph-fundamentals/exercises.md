# Phase 03: Practice Exercises

These exercises test your ability to think in graphs, design state structures, and implement routing logic in LangGraph.

## Exercise 1: State Reducers (Easy)
**Scenario**: You want to track the total number of API calls made during a graph execution. 
**Task**: Define a `TypedDict` State that includes a field `api_calls: int`. In LangGraph, if you don't use an `Annotated` reducer, returning `{"api_calls": 5}` overwrites the old value. Write the definition for `api_calls` using `Annotated` and the `operator.add` function so that returning `{"api_calls": 1}` *adds* 1 to the existing total.
> *Hint*: `import operator` and look up how `Annotated[int, operator.add]` works.

## Exercise 2: Implementing a Conditional Edge (Medium)
**Scenario**: You have a graph that checks a user's subscription status.
**Task**: Write a routing function `route_user(state: dict) -> str` that inspects `state["is_premium"]`. If `True`, route to `"premium_node"`. If `False`, route to `"free_node"`. Then write the Python code to add this conditional edge to a `builder` object coming from `"check_sub_node"`.
> *Hint*: `builder.add_conditional_edges("check_sub_node", route_user, {"premium_node": "premium_node", "free_node": "free_node"})`

## Exercise 3: The "Infinite Loop" Bug (Medium)
**Scenario**: A junior developer built a ReAct agent graph with two nodes: `llm_node` and `tool_node`. `llm_node` always routes to `tool_node`, and `tool_node` always routes to `llm_node`. 
**Task**: Explain in 2 sentences why this causes a catastrophic failure, and describe how a Conditional Edge from `llm_node` should be implemented to fix it.
> *Hint*: The LLM node needs to check a specific property (like `stop_reason` or the existence of a tool call) to decide whether to go to the tool node or to the `END` node.

## Exercise 4: Manual Checkpoint Inspection (Hard)
**Scenario**: You are debugging a graph that uses `MemorySaver`. 
**Task**: Assume `graph` and `config = {"configurable": {"thread_id": "1"}}` are defined. Write a Python snippet that retrieves the current state of the graph, prints the `messages` array, and prints the name of the `next` node waiting to execute.
> *Hint*: Use the `graph.get_state(config)` method.

## Exercise 5: Building a Fallback Node (Hard)
**Scenario**: Sometimes an LLM throws an exception (e.g., API rate limit).
**Task**: Create a node function `fallback_node(state: dict) -> dict` that simply appends a system message: "I am experiencing technical difficulties. Please try again." to the `messages` list. Explain conceptually how you might route to this node if the main `llm_node` fails.
> *Hint*: LangGraph doesn't catch raw Python exceptions automatically in basic setups. You usually wrap the `llm.invoke` in a `try/except` block inside the `llm_node` itself, or use advanced LangGraph error handling techniques.
