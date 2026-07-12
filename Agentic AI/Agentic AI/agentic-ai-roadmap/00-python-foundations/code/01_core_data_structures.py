import json

# === JAVA vs PYTHON DATA STRUCTURES ===

def demonstrate_lists():
    print("--- Lists ---")
    # Java: List<String> names = new ArrayList<>(Arrays.asList("Alice","Bob"));
    names = ["Alice", "Bob", "Charlie"]
    names.append("Dave")           # add()
    names.remove("Bob")            # remove()
    
    print(f"First element: {names[0]}") # get(0)
    print(f"List size: {len(names)}")   # size()
    print(f"Final list: {names}\n")

def demonstrate_dicts():
    print("--- Dicts (Like Java HashMap) ---")
    # Java: HashMap<String, Object> user = new HashMap<>(); user.put("name","Alice");
    user = {
        "name": "Alice",
        "role": "user",
        "metadata": {"session_id": "abc123"}
    }

    # Access patterns
    print(f"Direct access (user['name']): {user['name']}")
    
    # Safe access with default (prevents KeyError)
    print(f"Safe access (user.get('age')): {user.get('age', 'unknown')}")
    
    # Nested access
    print(f"Nested access (user['metadata']['session_id']): {user['metadata']['session_id']}")
    
    print(f"Keys (keySet): {list(user.keys())}")
    print(f"Values (values): {list(user.values())}")
    print(f"Items (entrySet): {list(user.items())}\n")

def demonstrate_comprehensions():
    print("--- Comprehensions (Like Java Streams) ---")
    names = ["Alice", "Bob", "Charlie", "Dave"]
    
    # List comprehensions
    # Java: names.stream().filter(n -> n.startsWith("A")).collect(Collectors.toList())
    a_names = [n for n in names if n.startswith("A")]
    print(f"Names starting with A: {a_names}")

    # Java: names.stream().map(String::toUpperCase).collect(Collectors.toList())
    upper = [n.upper() for n in names]
    print(f"Uppercase names: {upper}")

    # Dict comprehension
    # Java: stream.collect(Collectors.toMap(k -> k, v -> v.toUpperCase()))
    scores = {"Alice": 95, "Bob": 87}
    upper_keys = {k.upper(): v for k, v in scores.items()}
    print(f"Dict comprehension: {upper_keys}\n")

def demonstrate_json():
    print("--- JSON Handling (Like Jackson ObjectMapper) ---")
    data = {"model": "claude-sonnet-4-6", "max_tokens": 1024, "messages": []}

    # Jackson: objectMapper.writeValueAsString()
    json_str = json.dumps(data, indent=2)
    print("Serialized to JSON string:")
    print(json_str)

    # Jackson: objectMapper.readValue()
    parsed = json.loads(json_str)
    print(f"Parsed back to dict: type is {type(parsed)}")

    # File operations (mocked writing/reading)
    with open("config_demo.json", "w") as f:
        json.dump(data, f, indent=2) # Write to file
    
    with open("config_demo.json", "r") as f:
        loaded_config = json.load(f) # Read from file
        print(f"Loaded from file: {loaded_config['model']}\n")

if __name__ == "__main__":
    demonstrate_lists()
    demonstrate_dicts()
    demonstrate_comprehensions()
    demonstrate_json()
