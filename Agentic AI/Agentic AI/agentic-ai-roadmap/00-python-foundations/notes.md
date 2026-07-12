# Phase 00: Python Foundations

## 🎯 Why This Matters
For a Java developer, Python can feel deceptively simple. It lacks the strict compilation phase and verbose type system of Java, which makes it fast to write but easy to break in production if not handled correctly. As an AI Engineer, you will write Python 95% of the time, orchestrating LLM calls, handling unstructured JSON data, and exposing models via APIs. Mastering Python's data structures, type hints, async ecosystem, and web frameworks (like FastAPI) is the bedrock before you even touch an LLM.

---

## 🏗️ 0.1 Core Data Structures

In Java, you have the `Collections` framework (`List`, `Map`, `Set`). Python has native, heavily optimized syntax for these. Because AI development involves constant JSON manipulation, Python's `dict` (dictionary) and `list` are your most used tools.

### 💡 Java Analogy
*   `ArrayList<String>` ➡️ `list` e.g., `["A", "B"]`
*   `HashMap<String, Object>` ➡️ `dict` e.g., `{"name": "Alice"}`
*   `stream().filter().map().collect()` ➡️ List Comprehensions `[x.upper() for x in items if x]`

### 👨‍💻 Code Example
```python
# List comprehension (like Java streams)
names = ["Alice", "Bob", "Charlie"]
upper_names = [n.upper() for n in names if n.startswith("A")] 
# Result: ['ALICE']

# Dictionary (like HashMap)
user = {
    "name": "Alice",
    "metadata": {"role": "admin"}
}
# Safe access (prevents KeyError)
role = user.get("metadata", {}).get("role", "guest")
```

### 🚨 Common Java-Dev Mistakes
> [!WARNING]
> **Mutable Defaults**: Never use an empty list `[]` or dict `{}` as a default argument in a function. In Python, default arguments are evaluated *once* when the function is defined, not every time it's called. Instead, use `None` and initialize inside the function.
> **KeyError vs. NullPointerException**: Accessing a missing key in a dict via `user["age"]` throws a `KeyError` immediately (crashing your app). In Java, `map.get("age")` would return `null`. Use `user.get("age", "default")` in Python for safe access.

---

## 🛠️ 0.2 Functions & Type Hints

Python 3 introduced Type Hints (`typing` module). They don't enforce types at runtime (like Java does), but they allow IDEs (like PyCharm/VSCode) and static checkers (like `mypy`) to catch errors before execution.

### 💡 Java Analogy
*   `public String greet(String name)` ➡️ `def greet(name: str) -> str:`
*   `Optional<String>` ➡️ `Optional[str]` or `str | None` (Python 3.10+)
*   `void` ➡️ `None`

### 👨‍💻 Code Example
```python
from typing import Optional, Dict, Any

def create_message(content: str, role: str = "user", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    msg: Dict[str, Any] = {"role": role, "content": content}
    if metadata:
        msg["metadata"] = metadata
    return msg
```

### 🚨 Common Java-Dev Mistakes
> [!WARNING]
> **Ignoring Type Hints**: As a Java dev, you rely on the compiler. In Python, if you skip type hints, you lose all autocomplete and safety nets when passing complex DTOs to LLMs. Always type-hint function signatures.

---

## 📦 0.3 OOP: Classes & Dataclasses

Python is multi-paradigm, but OOP is still widely used, especially in LangChain. 

### 💡 Java Analogy
*   `Interface` ➡️ `ABC` (Abstract Base Class) with `@abstractmethod`
*   `record` or Lombok `@Data` ➡️ `@dataclass` or Pydantic `BaseModel`
*   `super()` ➡️ `super()`

### 👨‍💻 Code Example
```python
from pydantic import BaseModel, Field
from typing import List

class LLMRequest(BaseModel):
    model: str = "claude-sonnet-4-6"
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    messages: List[dict] = []

# This auto-validates types and boundaries
req = LLMRequest(messages=[{"role": "user", "content": "Hi"}])
print(req.model_dump_json()) # Converts DTO to JSON
```

> [!NOTE]
> **Pydantic is the new POJO**: In modern Python AI apps, Pydantic `BaseModel` is the standard for data validation (similar to Java's `javax.validation` / Hibernate Validator).

---

## ⚡ 0.4 Async Programming

AI apps are heavily I/O bound (waiting for LLM APIs, Vector DBs, etc.). Synchronous code will block your server. Python's `asyncio` is essential.

### 💡 Java Analogy
*   `CompletableFuture<T>` ➡️ `async def` (returns a Coroutine)
*   `.join()` or `.get()` ➡️ `await`
*   `ExecutorService.invokeAll()` ➡️ `asyncio.gather()`

### 👨‍💻 Code Example
```python
import asyncio

async def fetch_data(url: str) -> dict:
    await asyncio.sleep(1) # Simulates network delay safely
    return {"url": url, "status": 200}

async def fetch_all(urls: list[str]):
    # Executes all fetch_data calls in parallel
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

### 🚨 Common Java-Dev Mistakes
> [!WARNING]
> **Mixing Sync and Async**: If you call a blocking function (like `requests.get()` or `time.sleep()`) inside an `async def` function, you freeze the entire single-threaded event loop! Always use async libraries (like `httpx` or `aiohttp`) inside async functions, or offload blocking calls to a thread pool.

---

## 🌐 0.5 FastAPI REST API

FastAPI is the Spring Boot of modern Python: fast, type-safe, and auto-generates Swagger/OpenAPI docs.

### 💡 Java Analogy
*   `@RestController` ➡️ `@app.get(...)` or `@app.post(...)`
*   `@RequestBody` ➡️ Pydantic `BaseModel` injected as a parameter
*   `Filter` / `Interceptor` ➡️ `@app.middleware("http")`

### 👨‍💻 Code Example
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Empty message")
    return {"response": f"Echo: {request.message}"}
```

---

## 📚 Key Terms Glossary
*   **List Comprehension**: A concise way to create lists using a single line of code (e.g., `[x for x in list if condition]`).
*   **Dictionary (Dict)**: Python's hash map. The fundamental building block of JSON and kwargs.
*   **Kwargs (`**kwargs`)**: Keyword arguments. Allows a function to accept any number of named arguments as a dictionary.
*   **Type Hinting**: Annotating variables and functions with expected types to aid static analysis.
*   **Event Loop**: The core of `asyncio` that schedules and runs asynchronous tasks (coroutines) on a single thread.
*   **Coroutine**: A special function defined with `async def` that can be paused and resumed using `await`.
*   **Pydantic**: A data validation library that uses Python type annotations.
*   **FastAPI**: A modern, high-performance web framework for building APIs with Python.
