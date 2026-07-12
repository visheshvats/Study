# Phase 01: LLM & Prompt Foundations

## 🎯 Why This Matters
For a backend Java developer used to predictable REST APIs and fixed database schemas, integrating LLMs requires a complete mental shift. LLM APIs (like OpenAI or Anthropic) are inherently **stateless, non-deterministic, and context-dependent**. If you don't manage the conversation history, construct robust prompts, and enforce structured outputs (like JSON), your AI system will hallucinate or fail randomly. This phase teaches you how to reliably control the LLM's behavior and link it back to your traditional backend logic via Function Calling (Tools).

---

## 🧠 1.1 The LLM API is Stateless

In Spring Boot web apps, you might rely on `@SessionAttributes` or a Redis-backed session to remember a user's state. LLM APIs do not have sessions. You must send the *entire conversation history* with every single request.

### 💡 Java Analogy
*   **System Prompt** ➡️ Application Configuration/Global Constants. Defines the core persona.
*   **Context Window** ➡️ Maximum heap size per request. If you send too much history, the API throws an error (or you pay massive costs).
*   **Temperature** ➡️ Randomness factor. `0.0` is like a strict deterministic function; `1.0` is highly creative.

### 👨‍💻 Code Example: Managing History
```python
# In Java, you might rely on a session. Here, we pass the List explicitly.
history = [
    {"role": "system", "content": "You are a database expert."},
    {"role": "user", "content": "I need to write a SQL query for finding active users."},
    {"role": "assistant", "content": "Sure, use SELECT * FROM users WHERE active = true;"},
    {"role": "user", "content": "Can you add a date filter to that?"} 
    # The LLM needs the previous messages to know what "that" refers to!
]
```

### 🚨 Common Java-Dev Mistakes
> [!WARNING]
> **Assuming the LLM "Remembers"**: Developers often make a call, get a result, and make a second call saying "now do X to the previous result" without passing the previous result in the context. The LLM will fail because it has amnesia between calls. Always maintain an append-only log of messages.

---

## 📝 1.2 Prompt Engineering Patterns

To get predictable outputs from a non-deterministic model, you use specific structures. 

### 💡 Java Analogy
*   **Few-Shot Prompting** ➡️ Writing Unit Tests. You give the LLM "given/when/then" examples so it understands the expected format.
*   **Structured JSON Output** ➡️ `@ResponseBody`. Forcing the LLM to return JSON so you can deserialize it into a Pydantic `BaseModel` (or POJO).

### 👨‍💻 Code Example: Few-Shot Pattern
```python
few_shot_prompt = """
Extract the sentiment from the review. Return ONLY the word POSITIVE or NEGATIVE.

Review: "The app crashed on startup."
Sentiment: NEGATIVE

Review: "I love the new dark mode!"
Sentiment: POSITIVE

Review: "It's too slow."
Sentiment:
"""
# The LLM will reliably complete the pattern with "NEGATIVE".
```

---

## 🌊 1.3 Streaming Responses

Because LLMs generate text token by token (like someone typing), responses can take seconds. To prevent UI timeouts and improve UX, you stream the response chunks immediately.

### 💡 Java Analogy
*   **Streaming** ➡️ Server-Sent Events (SSE) in Spring WebFlux or `ResponseBodyEmitter`. 

### 👨‍💻 Code Example: FastAPI SSE
```python
from fastapi.responses import StreamingResponse

# Generating chunks dynamically
async def token_generator():
    yield "data: Hello\n\n"
    yield "data: World\n\n"
    yield "data: [DONE]\n\n"

# In your FastAPI route
@app.get("/stream")
async def stream():
    return StreamingResponse(token_generator(), media_type="text/event-stream")
```

---

## 🔧 1.4 Tool / Function Calling

This is the bridge between AI and traditional software. You give the LLM a JSON schema of tools (functions) it can call. If the LLM decides it needs real-time data (e.g., checking a database), it outputs a "Tool Call" command. Your Python code executes the actual function and feeds the result back to the LLM.

### 💡 Java Analogy
*   **Tool Schema** ➡️ A Swagger/OpenAPI definition of your internal Service methods.
*   **Agentic Loop** ➡️ A `while` loop that acts like a microservice orchestrator, passing data between the LLM and your internal APIs.

### 👨‍💻 Code Example: The Tool Loop Concept
```python
# 1. LLM says: "I need to call get_weather(location='Tokyo')"
# 2. Your Python code intercepts this.
weather_data = get_weather("Tokyo") # Executes real business logic
# 3. You send weather_data back to the LLM.
# 4. LLM reads it and says: "The weather in Tokyo is 75 degrees."
```

### 🚨 Common Java-Dev Mistakes
> [!WARNING]
> **Security Risks with Tools**: Never give an LLM a tool that executes raw SQL or deletes data without a Human-in-the-Loop check. LLMs can be manipulated (Prompt Injection) to call tools maliciously. Treat LLM tool requests as untrusted user input.

---

## 📚 Key Terms Glossary
*   **Context Window**: The maximum amount of text (measured in tokens) the LLM can process in a single request (input + output).
*   **Token**: A chunk of text the LLM reads. 1 token ≈ 0.75 words.
*   **System Prompt**: The overriding instructions given to the LLM that dictate its behavior, tone, and constraints.
*   **Few-Shot Prompting**: Providing a few examples in the prompt to demonstrate the desired output format.
*   **Chain of Thought (CoT)**: Forcing the LLM to explain its reasoning step-by-step *before* giving the final answer, which drastically improves accuracy.
*   **Function Calling / Tools**: The capability of an LLM to request the execution of an external function by returning a structured JSON object matching a predefined schema.
*   **Server-Sent Events (SSE)**: A simple protocol used to stream token updates from the backend to the frontend UI.
