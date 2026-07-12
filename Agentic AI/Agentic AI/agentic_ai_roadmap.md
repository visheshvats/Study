# 🚀 Agentic AI Implementation Plan
## Java Backend Developer → AI Engineer
### Complete Study Notes | Code Examples | Diagrams

---

> **How to use this in your AI IDE:**
> Paste this full document as context. Then prompt per phase:
> *"I'm a Java developer on Phase [N]. Based on these notes and code stubs, help me [build / expand / debug]. Fill in all TODO sections, add proper error handling, and explain Java analogies."*

---

## ⏱️ Timeline at a Glance

| Phase | Topic | Duration |
|-------|-------|----------|
| 0 | Python Foundations | 1 week |
| 1 | LLM & Prompt Engineering | 1 week |
| 2 | RAG Core | 1 week |
| 3 | LangGraph Fundamentals | 1.5 weeks |
| 4 | Workflows | 1.5 weeks |
| 5 | Orchestrators | 1 week |
| 6 | Evaluator & Optimizer | 1 week |
| 7 | Human in the Loop | 0.5 week |
| 8 | Advanced RAG | 1 week |
| 9 | Debugging & Observability | 0.5 week |
| 10 | Production Engineering | ongoing |
| 11 | Scaling & Architecture | ongoing |

**Total: ~10–12 weeks to production-level**

---

## 🗺️ Full Learning Path

```mermaid
flowchart TD
    P0["🐍 Phase 0\nPython Foundations\n1 week"] --> P1
    P1["🤖 Phase 1\nLLM & Prompts\n1 week"] --> P2
    P2["📚 Phase 2\nRAG Core\n1 week"] --> P3
    P3["🕸️ Phase 3\nLangGraph\n1.5 weeks"] --> P4
    P4["🔄 Phase 4\nWorkflows\n1.5 weeks"] --> P5
    P5["🎯 Phase 5\nOrchestrators\n1 week"] --> P6
    P6["⚖️ Phase 6\nEvaluator\n1 week"] --> P7
    P7["👤 Phase 7\nHITL\n0.5 week"] --> P8
    P8["🔬 Phase 8\nAdvanced RAG\n1 week"] --> P9
    P9["🔍 Phase 9\nDebugging\n0.5 week"] --> P10
    P10["🏭 Phase 10\nProduction\nongoing"] --> P11
    P11["📈 Phase 11\nScaling\nongoing"]

    style P0 fill:#4CAF50,color:#fff
    style P3 fill:#6C63FF,color:#fff
    style P10 fill:#FF5722,color:#fff
    style P11 fill:#FF5722,color:#fff
```

---

## 🔄 Java → Python Quick Reference (Keep This Handy)

| Java | Python | Notes |
|------|--------|-------|
| `SpringBoot @RestController` | `FastAPI router` | Same REST model |
| `@RequestBody` POJO / DTO | `Pydantic BaseModel` | Built-in validation |
| `CompletableFuture<T>` | `async / await` | Nearly identical mental model |
| `ExecutorService.invokeAll()` | `asyncio.gather()` | Run many tasks in parallel |
| `Maven / Gradle` | `pip + requirements.txt` | Or `pyproject.toml` |
| `Interface` | `Protocol` / `ABC` | Duck typing common instead |
| `Stream.map().collect()` | List comprehension `[f(x) for x in xs]` | |
| `Optional<T>` | `T \| None` or `Optional[T]` | Python 3.10+ union syntax |
| `try { } catch (Exception e) { }` | `try: ... except Exception as e:` | |
| `@Slf4j / log.info()` | `import logging; logger.info()` | |
| `HashMap<K,V>` | `dict` | First-class citizen in Python |
| `record` / Lombok `@Data` | `@dataclass` | |

---

## 📦 Global Project Setup

```bash
# 1. Create virtual environment (like Maven project scope)
python -m venv agentic-env
source agentic-env/bin/activate        # Linux/Mac
# agentic-env\Scripts\activate         # Windows

# 2. Install all core dependencies
pip install fastapi uvicorn httpx pydantic python-dotenv
pip install anthropic openai
pip install langchain langchain-community langchain-anthropic langchain-openai
pip install langgraph
pip install chromadb faiss-cpu
pip install langsmith
pip install redis

# 3. Save
pip freeze > requirements.txt
```

```bash
# .env  (NEVER commit this file!)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agentic-ai-dev
```

```python
# env_loader.py  — put this at top of every file
from dotenv import load_dotenv
import os

load_dotenv()
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
```

---

---

# ═══════════════════════════════════
# PHASE 0 — Python Foundations
# ═══════════════════════════════════
> **Duration:** 1 week
> **Goal:** Build a REST API, call an LLM API, handle errors properly

---

## 0.1 Core Data Structures

```python
# === JAVA vs PYTHON DATA STRUCTURES ===

# --- Lists ---
# Java: List<String> names = new ArrayList<>(Arrays.asList("Alice","Bob"));
names = ["Alice", "Bob", "Charlie"]
names.append("Dave")           # add()
names.remove("Bob")            # remove()
names[0]                       # get(0)
len(names)                     # size()

# --- Dicts (HEAVILY used in AI/LLM work — JSON everywhere) ---
# Java: HashMap<String, Object> user = new HashMap<>(); user.put("name","Alice");
user = {
    "name": "Alice",
    "role": "user",
    "metadata": {"session_id": "abc123"}
}

# Access patterns
user["name"]                   # Direct — raises KeyError if missing
user.get("age", "unknown")     # Safe access with default
user["metadata"]["session_id"] # Nested
list(user.keys())              # keySet()
list(user.values())            # values()
user.items()                   # entrySet()

# Dict comprehension
# Java: stream.collect(Collectors.toMap(k -> k, v -> v.toUpperCase()))
scores = {"Alice": 95, "Bob": 87}
upper_keys = {k.upper(): v for k, v in scores.items()}

# --- List comprehensions ---
# Java: names.stream().filter(n -> n.startsWith("A")).collect(Collectors.toList())
a_names = [n for n in names if n.startswith("A")]

# Java: names.stream().map(String::toUpperCase).collect(Collectors.toList())
upper = [n.upper() for n in names]

# Conditional expression (ternary)
# Java: int result = x > 0 ? x : -x;
result = x if x > 0 else -x

# --- JSON handling ---
import json

data = {"model": "claude-sonnet-4-6", "max_tokens": 1024, "messages": []}

json_str   = json.dumps(data, indent=2)    # Jackson: objectMapper.writeValueAsString()
parsed     = json.loads(json_str)          # Jackson: objectMapper.readValue()

with open("config.json") as f:
    config = json.load(f)                  # Read from file

with open("output.json", "w") as f:
    json.dump(data, f, indent=2)           # Write to file
```

---

## 0.2 Functions & Type Hints

```python
from typing import Optional, List, Dict, Any, Tuple

# Java: public String greet(String name, int times) { return ...; }
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times

# Optional param + complex return
def create_message(
    content: str,
    role: str = "user",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    msg: Dict[str, Any] = {"role": role, "content": content}
    if metadata:
        msg["metadata"] = metadata
    return msg

# *args (varargs), **kwargs (named params map)
def build_prompt(*parts: str, separator: str = "\n\n") -> str:
    return separator.join(parts)

result = build_prompt("Context:", "Answer:", "Reasoning:", separator="\n---\n")

# Error handling
def safe_parse_json(text: str) -> Tuple[Optional[dict], Optional[str]]:
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, str(e)

data, error = safe_parse_json('{"valid": true}')
if error:
    print(f"Parse failed: {error}")
```

---

## 0.3 OOP: Classes & Dataclasses

```python
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from typing import List, Optional
from abc import ABC, abstractmethod

# --- @dataclass — like Java record / Lombok @Data ---
@dataclass
class ChatMessage:
    role: str
    content: str
    tokens: int = 0
    metadata: dict = field(default_factory=dict)   # Mutable default!

msg = ChatMessage(role="user", content="Hello!")
print(msg.role)      # user

# --- Pydantic BaseModel — validated DTO, used everywhere in LangChain ---
class LLMRequest(BaseModel):
    model: str = "claude-sonnet-4-6"
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    messages: List[dict] = []
    system: Optional[str] = None

req = LLMRequest(
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.5
)
print(req.model_dump())        # to dict
print(req.model_dump_json())   # to JSON string

# --- Abstract base class (Java Interface equivalent) ---
class BaseAgent(ABC):
    def __init__(self, name: str, model: str = "claude-sonnet-4-6"):
        self.name = name
        self.model = model

    @abstractmethod
    def run(self, query: str) -> str:
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

# --- Inheritance ---
class ResearchAgent(BaseAgent):
    def __init__(self, name: str, sources: List[str] = None):
        super().__init__(name)
        self.sources = sources or []

    def run(self, query: str) -> str:
        return f"[{self.name}] Researching '{query}' from {self.sources}"

agent = ResearchAgent("WebBot", sources=["google", "bing"])
print(agent.run("What is RAG?"))
```

---

## 0.4 Async Programming

```python
import asyncio
import httpx
from typing import List

# Java: CompletableFuture<String> = CompletableFuture.supplyAsync(() -> fetch(url))
# Python:
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

# Parallel execution — Java: CompletableFuture.allOf(f1, f2, f3).join()
async def fetch_all(urls: List[str]) -> List[dict]:
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]

# Async generator (streaming)
async def stream_tokens(prompt: str):
    # Simulates streaming token-by-token
    words = prompt.split()
    for word in words:
        await asyncio.sleep(0.05)   # simulate network delay
        yield word + " "

# Consume stream
async def print_stream():
    async for token in stream_tokens("Hello streaming world"):
        print(token, end="", flush=True)

# Entry point
if __name__ == "__main__":
    asyncio.run(print_stream())
```

---

## 0.5 FastAPI REST API

```python
# main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uvicorn, uuid, logging

logger = logging.getLogger(__name__)
app = FastAPI(title="Agentic AI Gateway", version="1.0.0")

# --- Models (like Spring @RequestBody / @ResponseBody DTOs) ---
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tokens_used: int

# --- In-memory store (replace with Redis in Phase 11) ---
sessions: dict = {}

# --- Middleware: request logging ---
from fastapi import Request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"← {response.status_code}")
    return response

# --- Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session_id = request.session_id or str(uuid.uuid4())

    # TODO: Replace with actual LLM call in Phase 1
    response_text = f"Echo: {request.message}"

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        tokens_used=len(request.message.split())
    )

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

# Run with: uvicorn main:app --reload
# Swagger UI: http://localhost:8000/docs
```

---

## ✅ Phase 0 Checklist
- [ ] Write a Python class hierarchy with `ABC`
- [ ] Use `async/await` with `asyncio.gather()` for parallel HTTP calls
- [ ] Build a FastAPI endpoint with Pydantic validation and error handling
- [ ] Handle `try/except` in async functions correctly
- [ ] Create `.env` + `requirements.txt` for the project

---

---

# ═══════════════════════════════════
# PHASE 1 — LLM & Prompt Foundations
# ═══════════════════════════════════
> **Duration:** 1 week
> **Goal:** Deep understanding of how LLMs work, prompting techniques, and function calling

---

## Core Concepts Diagram

```mermaid
graph TD
    subgraph LLM_API["LLM API Call"]
        SYS["System Prompt\n(Personality / Instructions)"] --> MODEL["LLM\nclaude-sonnet-4-6"]
        USR["User Messages\n(Conversation history)"] --> MODEL
        TEMP["Temperature\n0 = deterministic\n1 = creative"] --> MODEL
        CTX["Context Window\nMax tokens in + out"] --> MODEL
        MODEL --> OUT["Response\nText | Tool Call | Both"]
    end
```

> **Key insight for Java devs:** The LLM API is **stateless** — like a pure function. You must send the full conversation history on every call. There is no server-side session. You manage state yourself.

---

## 1.1 Basic LLM API Call

```python
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()   # Reads ANTHROPIC_API_KEY automatically

# Simple single call
def ask_llm(
    user_message: str,
    system: str = "You are a helpful AI assistant.",
    temperature: float = 0.7
) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text

# Multi-turn conversation — YOU manage history
def chat_with_history(messages: list[dict], system: str = "") -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system,
        messages=messages     # Full history every time!
    )
    assistant_reply = response.content[0].text

    # Append reply to history (caller is responsible for this)
    messages.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply

# Usage
history = []
history.append({"role": "user", "content": "My name is Alice. Remember that."})
r1 = chat_with_history(history, system="You have a good memory.")

history.append({"role": "user", "content": "What is my name?"})
r2 = chat_with_history(history)   # Correctly returns "Alice"
print(r2)
```

---

## 1.2 Prompt Engineering Patterns

```python
# ─── Pattern 1: Few-Shot Prompting ───
few_shot_system = """You classify customer feedback.
Categories: BUG, FEATURE_REQUEST, PRAISE, QUESTION

Examples:
Feedback: "The app crashes when I open settings"
Category: BUG

Feedback: "Would love a dark mode option"
Category: FEATURE_REQUEST

Feedback: "Absolutely love how fast it loads!"
Category: PRAISE

Return ONLY the category word."""

category = ask_llm("Why can't I export to PDF?", few_shot_system)
print(category)  # QUESTION or BUG

# ─── Pattern 2: Chain of Thought ───
cot_prompt = """Solve the problem step by step.
Format:
THOUGHT: <your reasoning>
ANSWER: <final answer only>"""

result = ask_llm(
    "A user has 3 API calls remaining. Each operation costs 2 calls. How many operations can they do?",
    cot_prompt
)

# ─── Pattern 3: Structured JSON Output ───
json_system = """Extract structured data and return ONLY valid JSON.
No markdown code fences. No preamble. Raw JSON only.

Schema:
{
  "name": string,
  "age": number | null,
  "skills": string[],
  "experience_years": number | null
}"""

raw = ask_llm("Alice is a 28-year-old Java developer with 5 years of experience.", json_system)

import json, re
def extract_json(text: str) -> dict:
    # Strip markdown fences if present
    clean = re.sub(r'```json|```', '', text).strip()
    return json.loads(clean)

data = extract_json(raw)
print(data["skills"])   # ['Java']
```

---

## 1.3 Streaming Responses

```python
# ─── Terminal streaming ───
def stream_to_terminal(prompt: str):
    print("Assistant: ", end="", flush=True)
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for chunk in stream.text_stream:
            print(chunk, end="", flush=True)
    print()  # newline at end

# ─── FastAPI SSE streaming endpoint ───
from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class StreamRequest(BaseModel):
    message: str

@app.post("/chat/stream")
async def chat_stream(request: StreamRequest):
    async def generate():
        # Run blocking Anthropic stream in thread pool
        import asyncio
        loop = asyncio.get_event_loop()

        def _stream():
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": request.message}]
            ) as stream:
                for text in stream.text_stream:
                    yield text

        for chunk in _stream():
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## 1.4 Tool / Function Calling

```python
import json
from typing import Any

# ─── Define tools (what the LLM can invoke) ───
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

# ─── Tool implementations (your actual business logic) ───
def search_knowledge_base(query: str, max_results: int = 3) -> list:
    # TODO: Replace with real search
    return [{"id": 1, "title": f"Article about {query}", "snippet": "..."}]

def create_ticket(title: str, priority: str, description: str) -> dict:
    # TODO: Replace with real ticketing API
    return {"ticket_id": "TKT-001", "status": "CREATED", "title": title}

TOOL_REGISTRY = {
    "search_knowledge_base": search_knowledge_base,
    "create_ticket": create_ticket,
}

# ─── Agentic loop ───
def run_tool_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            # LLM decided to call a tool
            tool_block = next(b for b in response.content if b.type == "tool_use")
            tool_name   = tool_block.name
            tool_input  = tool_block.input

            print(f"🔧 Tool called: {tool_name}({tool_input})")

            # Execute the tool
            fn = TOOL_REGISTRY.get(tool_name)
            tool_result = fn(**tool_input) if fn else {"error": "Unknown tool"}

            # Feed result back
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": json.dumps(tool_result)
                }]
            })
        else:
            # Final answer
            return next(b.text for b in response.content if hasattr(b, "text"))

result = run_tool_agent("I need to create a HIGH priority ticket: Login fails for enterprise users")
print(result)
```

---

## ✅ Phase 1 Checklist
- [ ] Make a basic LLM call with system + user messages
- [ ] Implement multi-turn chat managing history manually
- [ ] Use few-shot prompting for a classifier
- [ ] Parse structured JSON from LLM output
- [ ] Build streaming endpoint in FastAPI
- [ ] Build a tool-calling agent with 2+ tools

---

---

# ═══════════════════════════════════
# PHASE 2 — RAG Core (Data Injection)
# ═══════════════════════════════════
> **Duration:** 1 week
> **Goal:** Build RAG systems from basic to conversational to multi-document

---

## RAG Architecture

```mermaid
flowchart LR
    subgraph INGEST["🏗️ Indexing (One-time)"]
        D["📄 Documents\nPDF / CSV / Web"] --> L["Loaders"]
        L --> S["Text Splitter\nchunks + overlap"]
        S --> E["Embeddings Model\ntext → vector"]
        E --> V[("🗄️ Vector DB\nChroma / FAISS")]
    end

    subgraph QUERY["🔍 Retrieval + Generation (Per Query)"]
        Q["User Query"] --> QE["Embed Query\nsame model"]
        QE --> R["Top-K Retrieval\nCosine Similarity"]
        V --> R
        R --> CTX["Context + Query\n→ Prompt"]
        CTX --> LLM["☁️ LLM"]
        LLM --> ANS["✅ Answer"]
    end

    style V fill:#6C63FF,color:#fff
    style LLM fill:#FF6B6B,color:#fff
```

---

## 2.1 Document Loading

```python
from langchain_community.document_loaders import (
    PyPDFLoader,
    DirectoryLoader,
    CSVLoader,
    WebBaseLoader,
    TextLoader,
)
from langchain_core.documents import Document

# ─── PDF ───
pdf_loader = PyPDFLoader("./docs/user_manual.pdf")
pdf_docs = pdf_loader.load()
print(f"Pages loaded: {len(pdf_docs)}")
print(f"Metadata: {pdf_docs[0].metadata}")  # {'source': ..., 'page': 0}

# ─── Entire folder ───
dir_loader = DirectoryLoader(
    "./docs/",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader,
    show_progress=True
)
all_docs = dir_loader.load()

# ─── Web page ───
web_loader = WebBaseLoader("https://docs.anthropic.com/en/docs/about-claude/models")
web_docs = web_loader.load()

# ─── CSV ───
csv_loader = CSVLoader(
    "./data/products.csv",
    metadata_columns=["product_id", "category"]
)
csv_docs = csv_loader.load()

# ─── Manual document ───
custom = Document(
    page_content="The refund window is 30 days from purchase date.",
    metadata={"source": "policy_v2", "section": "returns", "year": 2024}
)
```

---

## 2.2 Text Splitting

```python
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)

# ─── RecursiveCharacterTextSplitter — USE THIS BY DEFAULT ───
# Splits on: \n\n → \n → ". " → " " → character (priority order)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,       # ~750 words
    chunk_overlap=200,     # Keep context across boundaries
    length_function=len,
)

chunks = splitter.split_documents(pdf_docs)
print(f"Chunks created: {len(chunks)}")

# Understand what overlap does:
# Chunk 1: "...The policy applies to all purchases made after Jan 2024."
# Chunk 2: "made after Jan 2024. Refunds must be..." ← overlap preserves boundary context

# ─── Token-based (use when you need exact token counts) ───
token_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=64)
token_chunks = token_splitter.split_documents(pdf_docs)

# ─── Why chunk size matters ───
# Too large:   → context window fills fast, less precise retrieval
# Too small:   → chunks lack context, meaning is lost
# Rule of thumb: 500-1500 chars, overlap = 10-20% of chunk_size
```

---

## 2.3 Embeddings & Cosine Similarity

```python
from langchain_openai import OpenAIEmbeddings
import numpy as np

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# What embeddings ARE:
# High-dimensional vector (1536 dims) that encodes MEANING
# Similar meanings → small cosine distance

texts = [
    "Python is a programming language",   # tech
    "Django is a Python web framework",   # tech — similar to above
    "A snake is a reptile with no legs",  # unrelated
]
vecs = [embeddings.embed_query(t) for t in texts]

def cosine_sim(a: list, b: list) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

print(f"Python vs Django: {cosine_sim(vecs[0], vecs[1]):.3f}")  # ~0.87 HIGH
print(f"Python vs snake:  {cosine_sim(vecs[0], vecs[2]):.3f}")  # ~0.30 LOW
```

---

## 2.4 Vector Store

```python
from langchain_community.vectorstores import Chroma, FAISS

# ─── Chroma (great for dev, persists to disk) ───
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="product_docs",
    persist_directory="./chroma_db"    # Survives restarts
)

# Reload existing store
vectorstore = Chroma(
    collection_name="product_docs",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# Retrieval modes
retriever_basic   = vectorstore.as_retriever(search_kwargs={"k": 4})
retriever_mmr     = vectorstore.as_retriever(
    search_type="mmr",                 # Max Marginal Relevance — reduces redundancy
    search_kwargs={"k": 6, "fetch_k": 20}
)

# Metadata filtering
retriever_filtered = vectorstore.as_retriever(
    search_kwargs={
        "k": 4,
        "filter": {"section": "returns"}  # Only return policy chunks
    }
)

# ─── FAISS (faster inference, in-memory) ───
faiss_store = FAISS.from_documents(chunks, embeddings)
faiss_store.save_local("./faiss_index")
faiss_loaded = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
```

---

## 2.5 Basic RAG Chain (LCEL)

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

llm = ChatAnthropic(model="claude-sonnet-4-6")

RAG_PROMPT = ChatPromptTemplate.from_template("""
Answer the question based ONLY on the context below.
If the answer is not in the context, say "I don't have that information."
Do NOT make up information.

Context:
{context}

Question: {question}

Answer:""")

def format_docs(docs) -> str:
    return "\n\n---\n\n".join(
        f"[Source: {d.metadata.get('source','unknown')}]\n{d.page_content}"
        for d in docs
    )

# LCEL chain (pipe syntax — like Java method chaining)
rag_chain = (
    {
        "context": retriever_basic | format_docs,
        "question": RunnablePassthrough()
    }
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("What is the return policy?")
print(answer)
```

---

## 2.6 Conversational RAG

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    return_messages=True,
    k=5           # Keep last 5 exchanges
)

conv_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever_basic,
    memory=memory,
    return_source_documents=True,
    verbose=False
)

# Turn 1
r1 = conv_chain.invoke({"question": "What is the return policy?"})
print(r1["answer"])
sources1 = [d.metadata["source"] for d in r1["source_documents"]]

# Turn 2 — "it" correctly resolved to "the return" via history
r2 = conv_chain.invoke({"question": "How long does it take to process?"})
print(r2["answer"])
```

---

## ✅ Phase 2 Checklist
- [ ] Load PDFs, CSVs, and web pages into `Document` objects
- [ ] Split with chunk overlap and inspect chunk boundaries
- [ ] Compute cosine similarity between embeddings manually
- [ ] Persist a ChromaDB store and reload it
- [ ] Build a basic LCEL RAG chain
- [ ] Build conversational RAG with memory

---

---

# ═══════════════════════════════════
# PHASE 3 — LangGraph Fundamentals
# ═══════════════════════════════════
> **Duration:** 1.5 weeks
> **Goal:** Build stateful agents using graph-based (state machine) architecture

---

## LangGraph Mental Model

```mermaid
stateDiagram-v2
    [*] --> Node_A : Entry Point
    Node_A --> Node_B : Edge (unconditional)
    Node_A --> Node_C : Conditional Edge
    Node_B --> Node_A : Loop
    Node_C --> [*] : END

    note right of Node_A
        Node = function(state) → partial_state
        Edge = transition rule
        State = shared TypedDict
        Conditional = routing function
    end note
```

> **Java analogy:** LangGraph is like `spring-statemachine` — each state is a function that transforms a shared context object (the "State"). Edges are transitions. Conditional edges are guards.

---

## 3.1 Basic State Graph

```python
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages   # Appends, not replaces
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

llm = ChatAnthropic(model="claude-sonnet-4-6")

# ─── State definition ───
# TypedDict = what data the graph carries between nodes
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]  # add_messages = append-only
    step_count: int
    context: str

# ─── Nodes (pure functions: State → partial State) ───
def process_node(state: AgentState) -> dict:
    response = llm.invoke(state["messages"])
    return {
        "messages": [response],       # add_messages will append this
        "step_count": state["step_count"] + 1
    }

def enrich_context_node(state: AgentState) -> dict:
    last_msg = state["messages"][-1]
    return {"context": f"Processed: {last_msg.content[:50]}..."}

# ─── Build graph ───
builder = StateGraph(AgentState)

builder.add_node("process",  process_node)
builder.add_node("enrich",   enrich_context_node)

builder.set_entry_point("process")
builder.add_edge("process", "enrich")
builder.add_edge("enrich", END)

graph = builder.compile()

# ─── Run ───
result = graph.invoke({
    "messages": [HumanMessage("What is LangGraph?")],
    "step_count": 0,
    "context": ""
})
print(result["context"])
print(f"Steps: {result['step_count']}")
```

---

## 3.2 Conditional Edges (Routing)

```python
from typing import Literal

class RouterState(TypedDict):
    query: str
    category: str    # "technical" | "billing" | "general"
    response: str

# ─── Classification node ───
def classify(state: RouterState) -> dict:
    prompt = f"""Classify this query into one of: technical, billing, general
Query: {state['query']}
Return ONLY the category word."""
    result = llm.invoke([HumanMessage(content=prompt)])
    return {"category": result.content.strip().lower()}

# ─── Specialist nodes ───
def handle_technical(state: RouterState) -> dict:
    reply = llm.invoke([
        SystemMessage("You are a senior software engineer."),
        HumanMessage(state["query"])
    ])
    return {"response": reply.content}

def handle_billing(state: RouterState) -> dict:
    reply = llm.invoke([
        SystemMessage("You are a billing support specialist."),
        HumanMessage(state["query"])
    ])
    return {"response": reply.content}

def handle_general(state: RouterState) -> dict:
    reply = llm.invoke([HumanMessage(state["query"])])
    return {"response": reply.content}

# ─── Router function — returns the name of the NEXT NODE ───
def route(state: RouterState) -> Literal["technical", "billing", "general"]:
    cat = state["category"]
    return cat if cat in ("technical", "billing") else "general"

# ─── Build ───
builder = StateGraph(RouterState)
builder.add_node("classify",  classify)
builder.add_node("technical", handle_technical)
builder.add_node("billing",   handle_billing)
builder.add_node("general",   handle_general)

builder.set_entry_point("classify")
builder.add_conditional_edges("classify", route, {
    "technical": "technical",
    "billing":   "billing",
    "general":   "general",
})
builder.add_edge("technical", END)
builder.add_edge("billing",   END)
builder.add_edge("general",   END)

graph = builder.compile()
result = graph.invoke({"query": "My invoice shows wrong amount", "category": "", "response": ""})
print(f"Category: {result['category']} | Reply: {result['response'][:100]}")
```

---

## 3.3 ReAct Agent with Tools

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
import math, json

@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression safely. Supports basic arithmetic and math functions."""
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

@tool
def get_stock_price(ticker: str) -> str:
    """Get the current stock price for a ticker symbol."""
    # TODO: Replace with real API (Alpha Vantage, Yahoo Finance, etc.)
    mock_prices = {"AAPL": 189.50, "GOOG": 2750.30, "MSFT": 415.20}
    price = mock_prices.get(ticker.upper(), None)
    return json.dumps({"ticker": ticker, "price": price, "currency": "USD"}) if price else f"Unknown ticker: {ticker}"

@tool
def search_docs(query: str) -> str:
    """Search the product documentation for information."""
    # TODO: Replace with actual vector store retrieval
    return f"[Doc search: '{query}'] Found: The feature supports up to 100 concurrent users."

# ─── Create ReAct agent (Reasoning + Acting loop) ───
agent = create_react_agent(llm, tools=[calculator, get_stock_price, search_docs])

result = agent.invoke({
    "messages": [HumanMessage("What is 15% of AAPL stock price? Also how many concurrent users does the product support?")]
})

for msg in result["messages"]:
    print(f"\n[{msg.__class__.__name__}]: {str(msg.content)[:200]}")
```

---

## 3.4 Persistent Memory (Checkpointing)

```python
from langgraph.checkpoint.memory import MemorySaver

# ─── MemorySaver = in-process (dev only) ───
# Use PostgresSaver / RedisSaver in production (Phase 11)
memory = MemorySaver()

class ChatState(TypedDict):
    messages: Annotated[List, add_messages]

def chat_node(state: ChatState) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}

builder = StateGraph(ChatState)
builder.add_node("chat", chat_node)
builder.set_entry_point("chat")
builder.add_edge("chat", END)

# Compile WITH checkpointer — state persists per thread_id
graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "session-alice-001"}}

# Turn 1
graph.invoke({"messages": [HumanMessage("My name is Alice.")]}, config)

# Turn 2 — state auto-restored from checkpoint
r = graph.invoke({"messages": [HumanMessage("What is my name?")]}, config)
print(r["messages"][-1].content)  # "Your name is Alice."

# Inspect state at any time
snapshot = graph.get_state(config)
print(f"Messages in memory: {len(snapshot.values['messages'])}")
print(f"Next node: {snapshot.next}")
```

---

## ✅ Phase 3 Checklist
- [ ] Build a 3-node StateGraph and trace state through it
- [ ] Implement conditional routing to 3+ branches
- [ ] Create a ReAct agent with calculator + search tools
- [ ] Add `MemorySaver` and test multi-turn memory
- [ ] Print graph as Mermaid: `print(graph.get_graph().draw_mermaid())`

---

---

# ═══════════════════════════════════
# PHASE 4 — Workflows
# ═══════════════════════════════════
> **Duration:** 1.5 weeks
> **Goal:** Stop building chatbots — start building **systems**

---

## Workflow Patterns

```mermaid
flowchart TD
    subgraph PC["Pattern 1: Prompt Chaining"]
        A1[Input] --> B1[Extract\nKey Points] --> C1[Summarize] --> D1[Generate\nHeadline] --> E1[Output]
    end

    subgraph RT["Pattern 2: Router"]
        A2[Input] --> B2{Classifier}
        B2 -->|code| C2[Code Expert]
        B2 -->|biz| D2[Biz Analyst]
        B2 -->|general| E2[Generalist]
    end

    subgraph PL["Pattern 3: Parallelization"]
        A3[Input] --> B3[Sentiment]
        A3 --> C3[Topics]
        A3 --> D3[Readability]
        B3 --> E3{Combine}
        C3 --> E3
        D3 --> E3
    end
```

---

## 4.1 Prompt Chaining (LCEL)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()

# Step 1: Extract key points
step1 = (
    ChatPromptTemplate.from_template(
        "Extract exactly 5 key points from this article as a numbered list:\n\n{article}"
    )
    | llm | parser
)

# Step 2: Write executive summary
step2 = (
    ChatPromptTemplate.from_template(
        "Write a 2-sentence executive summary from these key points:\n\n{key_points}"
    )
    | llm | parser
)

# Step 3: Create headline
step3 = (
    ChatPromptTemplate.from_template(
        "Write ONE punchy headline for this summary. No punctuation at end:\n\n{summary}"
    )
    | llm | parser
)

# ─── Chain them — output of each becomes input of next ───
def analyze_article(article: str) -> dict:
    key_points = step1.invoke({"article": article})
    summary    = step2.invoke({"key_points": key_points})
    headline   = step3.invoke({"summary": summary})

    return {
        "key_points": key_points,
        "summary":    summary,
        "headline":   headline
    }

results = analyze_article("Long article text here...")
print(f"Headline: {results['headline']}")
```

---

## 4.2 Router Pattern (LangGraph)

```python
class WorkflowState(TypedDict):
    input: str
    route: str
    output: str

def classify_input(state: WorkflowState) -> dict:
    prompt = f"""Classify into: code, business, creative
Input: {state['input']}
Return ONLY the label."""
    result = llm.invoke([HumanMessage(content=prompt)])
    return {"route": result.content.strip().lower()}

def code_handler(state: WorkflowState) -> dict:
    r = llm.invoke([
        SystemMessage("You are a senior software architect."),
        HumanMessage(state["input"])
    ])
    return {"output": r.content}

def business_handler(state: WorkflowState) -> dict:
    r = llm.invoke([
        SystemMessage("You are an MBA-level business analyst."),
        HumanMessage(state["input"])
    ])
    return {"output": r.content}

def creative_handler(state: WorkflowState) -> dict:
    r = llm.invoke([
        SystemMessage("You are a creative writing expert."),
        HumanMessage(state["input"])
    ])
    return {"output": r.content}

def router(state: WorkflowState) -> str:
    return state["route"] if state["route"] in ("code","business") else "creative"

builder = StateGraph(WorkflowState)
for name, fn in [("classify",classify_input),("code",code_handler),("business",business_handler),("creative",creative_handler)]:
    builder.add_node(name, fn)

builder.set_entry_point("classify")
builder.add_conditional_edges("classify", router, {"code":"code","business":"business","creative":"creative"})
for n in ("code","business","creative"):
    builder.add_edge(n, END)

router_graph = builder.compile()
```

---

## 4.3 Parallelization (Fan-out / Fan-in)

```python
import asyncio

async def analyze_parallel(text: str) -> dict:
    """Run 3 analysis tasks in parallel — 3x faster than sequential"""

    async def sentiment() -> str:
        r = await asyncio.to_thread(llm.invoke, [HumanMessage(
            f"Rate sentiment 1-10 with a one-line reason:\n{text}"
        )])
        return r.content

    async def topics() -> str:
        r = await asyncio.to_thread(llm.invoke, [HumanMessage(
            f"List 5 main topics as JSON array. Return raw JSON only:\n{text}"
        )])
        return r.content

    async def readability() -> str:
        r = await asyncio.to_thread(llm.invoke, [HumanMessage(
            f"Rate readability for a general audience (1=very hard, 10=very easy) with brief explanation:\n{text}"
        )])
        return r.content

    # Fan-out: all 3 run concurrently
    sent, top, read = await asyncio.gather(sentiment(), topics(), readability())

    # Fan-in: combine results
    return {"sentiment": sent, "topics": top, "readability": read}

# LangGraph fan-out node
class ParallelState(TypedDict):
    text: str
    sentiment: str
    topics: str
    readability: str
    combined_report: str

def run_parallel_analysis(state: ParallelState) -> dict:
    results = asyncio.run(analyze_parallel(state["text"]))
    return results

def combine_results(state: ParallelState) -> dict:
    report = f"""
# Document Analysis Report

## Sentiment
{state['sentiment']}

## Topics
{state['topics']}

## Readability
{state['readability']}
"""
    return {"combined_report": report}
```

---

## ✅ Phase 4 Checklist
- [ ] Build a 3-step LCEL prompt chain
- [ ] Create a router with 3 specialist branches
- [ ] Run 3+ LLM calls in parallel with `asyncio.gather`
- [ ] Build a document analyzer combining all patterns

---

---

# ═══════════════════════════════════
# PHASE 5 — Orchestrators (Multi-Agent)
# ═══════════════════════════════════
> **Duration:** 1 week
> **Goal:** Build systems where agents coordinate to solve complex tasks

---

## Multi-Agent Architecture

```mermaid
graph TD
    U["👤 User"] --> ORC["🎯 Orchestrator\nDecompose + Delegate + Synthesize"]

    ORC --> R["🔍 Researcher\nGathers information"]
    ORC --> W["✍️ Writer\nCreates content"]
    ORC --> ED["✏️ Editor\nReviews + refines"]
    ORC --> AN["📊 Analyst\nData insights"]

    R --> ORC
    W --> ORC
    ED --> ORC
    AN --> ORC

    ORC --> U

    style ORC fill:#FF6B6B,color:#fff
    style R  fill:#4ECDC4,color:#fff
    style W  fill:#45B7D1,color:#fff
```

---

## 5.1 Worker + Orchestrator Pattern

```python
from langchain_core.messages import SystemMessage, HumanMessage
from typing import List, Dict
import json, re

# ─── Worker Agent ───
class WorkerAgent:
    def __init__(self, name: str, specialty: str, instructions: str = ""):
        self.name = name
        self.specialty = specialty
        self.instructions = instructions or f"You are a {specialty} specialist."
        self.llm = ChatAnthropic(model="claude-sonnet-4-6")

    def run(self, task: str, context: str = "") -> str:
        messages = [SystemMessage(content=self.instructions)]
        if context:
            messages.append(HumanMessage(content=f"Context:\n{context}"))
        messages.append(HumanMessage(content=f"Task:\n{task}"))

        response = self.llm.invoke(messages)
        print(f"  ✅ [{self.name}] completed task")
        return response.content

# ─── Orchestrator Agent ───
class OrchestratorAgent:
    def __init__(self, workers: List[WorkerAgent]):
        self.workers: Dict[str, WorkerAgent] = {w.name: w for w in workers}
        self.llm = ChatAnthropic(model="claude-sonnet-4-6")

    def plan(self, goal: str) -> List[Dict]:
        plan_prompt = f"""
Break down this goal into ordered subtasks. Assign each to the best available worker.
Available workers: {list(self.workers.keys())}
Goal: {goal}

Return ONLY valid JSON array (no markdown):
[
  {{"step": 1, "worker": "WorkerName", "task": "specific instruction", "depends_on": []}},
  {{"step": 2, "worker": "WorkerName", "task": "specific instruction", "depends_on": [1]}}
]"""
        response = self.llm.invoke([HumanMessage(content=plan_prompt)])
        json_text = re.sub(r'```json|```', '', response.content).strip()
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return [{"step": 1, "worker": list(self.workers.keys())[0], "task": goal, "depends_on": []}]

    def execute(self, plan: List[Dict]) -> Dict[int, str]:
        results = {}
        for step in sorted(plan, key=lambda x: x["step"]):
            step_num = step["step"]
            worker_name = step["worker"]
            task = step["task"]

            # Gather context from dependencies
            dep_context = "\n\n".join(
                f"Step {d} result:\n{results[d]}"
                for d in step.get("depends_on", [])
                if d in results
            )

            if worker_name in self.workers:
                results[step_num] = self.workers[worker_name].run(task, dep_context)
            else:
                results[step_num] = f"Error: worker '{worker_name}' not found"

        return results

    def synthesize(self, goal: str, step_results: Dict[int, str]) -> str:
        synthesis_prompt = f"""
Original goal: {goal}

Worker outputs:
{json.dumps(step_results, indent=2)}

Synthesize these into a final comprehensive response."""
        return self.llm.invoke([HumanMessage(content=synthesis_prompt)]).content

    def run(self, goal: str) -> str:
        print(f"\n🎯 Goal: {goal}")
        plan = self.plan(goal)
        print(f"📋 Plan: {len(plan)} steps")
        results = self.execute(plan)
        return self.synthesize(goal, results)

# ─── Usage ───
orchestrator = OrchestratorAgent([
    WorkerAgent("Researcher", "research", "Find facts and data. Be specific and cite sources."),
    WorkerAgent("Writer",     "writing",  "Write clear, engaging content based on provided research."),
    WorkerAgent("Editor",     "editing",  "Review content for clarity, grammar, and logical flow."),
])

final = orchestrator.run("Write a 300-word blog post about the benefits of RAG in enterprise AI")
print(f"\n🎉 Final Output:\n{final}")
```

---

## ✅ Phase 5 Checklist
- [ ] Build a `WorkerAgent` class with specialty injection
- [ ] Build an `OrchestratorAgent` that creates and executes a plan
- [ ] Implement dependency-aware step execution
- [ ] Build a Blog Generator (Researcher → Writer → Editor)
- [ ] Understand when NOT to use multi-agent (avoid over-engineering)

---

---

# ═══════════════════════════════════
# PHASE 6 — Evaluator & Optimizer
# ═══════════════════════════════════
> **Duration:** 1 week
> **Goal:** Build self-improving AI workflows with quality gates

> ⚠️ **This is where 90% of developers stop. You must not.**

---

## Evaluation Loop

```mermaid
flowchart LR
    GEN["Agent\nGenerates Output"] --> EVAL{LLM Judge\nScores 1-10}
    EVAL -->|Score ≥ 7\nPASS| OK["✅ Accept\n& Return"]
    EVAL -->|Score < 7\nFAIL| FB["📝 Structured\nFeedback"]
    FB --> RETRY["🔄 Retry with\nFeedback"]
    RETRY --> GEN

    style EVAL fill:#FFD700,color:#000
    style OK   fill:#4CAF50,color:#fff
    style RETRY fill:#FF5722,color:#fff
```

---

## 6.1 LLM-as-Judge

```python
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
import json

class EvalResult(BaseModel):
    score: int = Field(ge=1, le=10, description="Quality score 1-10")
    passed: bool = Field(description="True if score >= 7")
    strengths: List[str] = Field(description="What the output does well")
    issues: List[str] = Field(description="Specific problems found")
    improvements: List[str] = Field(description="Concrete suggestions for improvement")

eval_parser = PydanticOutputParser(pydantic_object=EvalResult)

def judge_output(
    task: str,
    output: str,
    criteria: str = "accuracy, completeness, clarity, conciseness"
) -> EvalResult:

    judge_prompt = f"""You are a strict quality evaluator. Be objective and critical.

TASK:
{task}

OUTPUT TO EVALUATE:
{output}

EVALUATION CRITERIA: {criteria}

Score 1-10 (7+ = acceptable for production).
Penalize: vague claims, missing information, poor structure, hallucinations.

{eval_parser.get_format_instructions()}"""

    response = llm.invoke([HumanMessage(content=judge_prompt)])

    try:
        return eval_parser.parse(response.content)
    except Exception:
        return EvalResult(
            score=4, passed=False,
            strengths=[], issues=["Evaluation parsing failed"],
            improvements=["Retry"]
        )
```

---

## 6.2 Self-Improving Retry Loop

```python
def generate_with_quality_gate(
    task: str,
    max_retries: int = 3,
    pass_threshold: int = 7
) -> dict:
    history = []
    feedback = ""

    for attempt in range(1, max_retries + 1):
        print(f"\n🔄 Attempt {attempt}/{max_retries}")

        # Build prompt (include feedback on retries)
        prompt = task
        if feedback:
            prompt += f"\n\n⚠️ IMPORTANT — Improve based on this feedback:\n{feedback}"

        output = llm.invoke([HumanMessage(content=prompt)]).content

        # Evaluate
        evaluation = judge_output(task, output)
        print(f"   Score: {evaluation.score}/10 | Passed: {evaluation.passed}")

        history.append({
            "attempt": attempt,
            "score": evaluation.score,
            "output_preview": output[:100]
        })

        if evaluation.passed or attempt == max_retries:
            return {
                "output": output,
                "evaluation": evaluation,
                "attempts": attempt,
                "history": history,
                "success": evaluation.passed
            }

        # Prepare feedback for next attempt
        feedback = (
            f"Issues found:\n" + "\n".join(f"- {i}" for i in evaluation.issues) +
            f"\n\nSuggestions:\n" + "\n".join(f"- {s}" for s in evaluation.improvements)
        )

result = generate_with_quality_gate(
    task="Write a 2-sentence explanation of vector embeddings for a Java developer.",
    max_retries=3
)
print(f"\n✅ Final (score {result['evaluation'].score}/10):\n{result['output']}")
```

---

## 6.3 Hallucination Detection

```python
def check_hallucination(claim: str, source_context: str) -> dict:
    prompt = f"""
Determine if this claim is supported by the provided context.

CLAIM: {claim}

CONTEXT: {source_context}

Is the claim:
A) SUPPORTED — directly stated in context
B) INFERRED — reasonably inferred from context
C) UNSUPPORTED — not in context or contradicts it

Return JSON only:
{{"verdict": "SUPPORTED"|"INFERRED"|"UNSUPPORTED", "reason": "brief explanation"}}"""

    result = llm.invoke([HumanMessage(content=prompt)])
    return json.loads(re.sub(r'```json|```', '', result.content).strip())

# Usage in RAG pipeline
def rag_with_hallucination_check(query: str, retriever) -> str:
    docs = retriever.invoke(query)
    context = "\n".join(d.page_content for d in docs)

    answer = rag_chain.invoke(query)

    # Check key claims in the answer
    verdict = check_hallucination(answer, context)

    if verdict["verdict"] == "UNSUPPORTED":
        return f"[⚠️ Low confidence] {answer}"
    return answer
```

---

## ✅ Phase 6 Checklist
- [ ] Build `EvalResult` Pydantic schema
- [ ] Implement `judge_output()` with structured scoring
- [ ] Build `generate_with_quality_gate()` retry loop
- [ ] Add hallucination detection to your RAG chain
- [ ] Track improvement across retry attempts

---

---

# ═══════════════════════════════════
# PHASE 7 — Human in the Loop (HITL)
# ═══════════════════════════════════
> **Duration:** ~0.5 week
> **Goal:** Build agents that pause for human approval before proceeding

---

## HITL Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant G as LangGraph
    participant H as Human Reviewer

    U->>G: Submit task
    G->>G: Generate draft
    G-->>H: ⏸️ INTERRUPT — Review draft
    H->>G: Approve / Reject / Edit
    alt Approved
        G->>G: Continue with draft
    else Rejected with feedback
        G->>G: Revise based on feedback
    end
    G->>U: Final output
```

---

## 7.1 HITL with LangGraph Interrupt

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class HITLState(TypedDict):
    task: str
    draft: str
    approved: bool
    feedback: str
    final: str

def generate_draft(state: HITLState) -> dict:
    response = llm.invoke([HumanMessage(content=f"Complete this task:\n{state['task']}")])
    return {"draft": response.content}

def request_review(state: HITLState) -> dict:
    # This node is a placeholder — execution is interrupted BEFORE it runs
    # Human provides input via graph.invoke({"approved": ..., "feedback": ...}, config)
    return {}

def apply_decision(state: HITLState) -> dict:
    if state.get("approved", False):
        return {"final": state["draft"]}

    # Revise with feedback
    revision = llm.invoke([HumanMessage(
        content=f"Revise this based on feedback.\n\nOriginal:\n{state['draft']}\n\nFeedback:\n{state['feedback']}"
    )])
    return {"final": revision.content}

builder = StateGraph(HITLState)
builder.add_node("generate", generate_draft)
builder.add_node("review",   request_review)
builder.add_node("decide",   apply_decision)

builder.set_entry_point("generate")
builder.add_edge("generate", "review")
builder.add_edge("review",   "decide")
builder.add_edge("decide",   END)

memory = MemorySaver()
graph  = builder.compile(
    checkpointer=memory,
    interrupt_before=["review"]   # ← PAUSE HERE for human input
)

config = {"configurable": {"thread_id": "hitl-session-001"}}
initial = {"task": "Draft a refund policy for a SaaS product", "draft": "", "approved": False, "feedback": "", "final": ""}

# ─── Step 1: Run until interrupt ───
graph.invoke(initial, config)
draft = graph.get_state(config).values["draft"]
print(f"\n📝 Draft for review:\n{draft[:300]}...")

# ─── Step 2: Human review (simulate — in prod, this comes from UI/webhook) ───
approved = input("\nApprove? (y/n): ").strip().lower() == "y"
feedback = "" if approved else input("Enter feedback: ")

# ─── Step 3: Resume ───
final_result = graph.invoke({"approved": approved, "feedback": feedback}, config)
print(f"\n✅ Final:\n{final_result['final']}")
```

---

## ✅ Phase 7 Checklist
- [ ] Build a HITL graph with `interrupt_before`
- [ ] Resume graph execution with human-provided state
- [ ] Build a web endpoint that exposes draft for review and resumes on POST
- [ ] Implement an "admin approval" workflow for high-risk actions

---

---

# ═══════════════════════════════════
# PHASE 8 — Advanced RAG
# ═══════════════════════════════════
> **Duration:** 1 week
> **Goal:** RAG that adapts, self-corrects, and reasons about retrieval

---

## Advanced RAG Decision Flow

```mermaid
flowchart TD
    Q["Query"] --> ADAP{Adaptive RAG\nNeed retrieval?}
    ADAP -->|Yes| RET["Retrieve Docs"]
    ADAP -->|No — LLM knows| GEN["Generate Direct"]
    RET --> GRADE{Corrective RAG\nGrade quality}
    GRADE -->|Relevant ≥2| RAG_GEN["Generate\nfrom Docs"]
    GRADE -->|Insufficient| WSEARCH["🌐 Web Search\nSupplement"]
    WSEARCH --> RAG_GEN
    RAG_GEN --> HCHECK{Hallucination\nCheck}
    HCHECK -->|Grounded| ANS["✅ Answer"]
    HCHECK -->|Hallucinated| RET

    style ADAP  fill:#6C63FF,color:#fff
    style GRADE fill:#FF6B6B,color:#fff
    style HCHECK fill:#FFD700,color:#000
```

---

## 8.1 Adaptive RAG

```python
def needs_retrieval(query: str) -> bool:
    """Decide: can LLM answer from knowledge, or do we need docs?"""
    prompt = f"""Does this question require looking up specific documents or data,
or can it be answered from general knowledge?

Question: {query}

Answer ONLY: yes_retrieval or no_retrieval"""

    result = llm.invoke([HumanMessage(content=prompt)])
    return "yes" in result.content.lower()

def adaptive_rag(query: str, retriever) -> str:
    if needs_retrieval(query):
        print("🔍 Using retrieval...")
        return rag_chain.invoke(query)
    else:
        print("🧠 Using LLM knowledge directly...")
        return llm.invoke([HumanMessage(content=query)]).content
```

---

## 8.2 Corrective RAG (CRAG)

```python
from langchain_core.documents import Document

def grade_doc_relevance(query: str, doc: Document) -> bool:
    prompt = f"""Is this document relevant to the query?
Query: {query}
Document excerpt: {doc.page_content[:400]}
Answer ONLY: yes or no"""
    result = llm.invoke([HumanMessage(content=prompt)])
    return result.content.strip().lower() == "yes"

def corrective_rag_pipeline(query: str, retriever) -> str:
    # Step 1: Retrieve
    raw_docs = retriever.invoke(query)
    print(f"Retrieved {len(raw_docs)} documents")

    # Step 2: Grade for relevance
    relevant = [d for d in raw_docs if grade_doc_relevance(query, d)]
    print(f"Relevant after grading: {len(relevant)}")

    # Step 3: Correct if insufficient
    if len(relevant) < 2:
        print("⚠️ Insufficient — supplementing with web search")
        # TODO: Use Tavily / SerpAPI for real search
        web_result = Document(
            page_content=f"[Web Search Result for '{query}'] ... relevant web content here ...",
            metadata={"source": "web_search"}
        )
        relevant.append(web_result)

    # Step 4: Generate
    context = "\n\n---\n\n".join(d.page_content for d in relevant)
    sources  = list({d.metadata.get("source","unknown") for d in relevant})

    answer = llm.invoke([HumanMessage(
        content=f"Answer based on this context:\n\n{context}\n\nQuestion: {query}"
    )]).content

    return f"{answer}\n\n*Sources: {', '.join(sources)}*"
```

---

## 8.3 Agentic RAG (Multi-Source)

```python
@tool
def search_pdf_docs(query: str) -> str:
    """Search internal PDF knowledge base."""
    docs = retriever_basic.invoke(query)
    return "\n---\n".join(d.page_content[:300] for d in docs[:3])

@tool
def search_web(query: str) -> str:
    """Search the web for current information."""
    # TODO: Integrate Tavily API
    return f"[Web results for '{query}']: Placeholder web content."

@tool
def query_database(sql_description: str) -> str:
    """Query the product database."""
    # TODO: Connect to real DB
    return f"[DB result for '{sql_description}']: 42 records found."

# Agentic RAG — agent decides WHICH retrieval source to use
agentic_rag_agent = create_react_agent(
    llm,
    tools=[search_pdf_docs, search_web, query_database]
)

result = agentic_rag_agent.invoke({
    "messages": [HumanMessage("What are our current subscription prices and what do competitors charge?")]
})
```

---

## ✅ Phase 8 Checklist
- [ ] Implement `needs_retrieval()` adaptive gate
- [ ] Build Corrective RAG with document grading
- [ ] Set up Tavily or SerpAPI for real web search
- [ ] Build Agentic RAG with 3+ retrieval tools
- [ ] Build Multi-source RAG (PDF + Web + DB)

---

---

# ═══════════════════════════════════
# PHASE 9 — Debugging & Observability
# ═══════════════════════════════════
> **Duration:** ~0.5 week
> **Goal:** Understand what your agent is doing and precisely why it fails

---

## 9.1 LangSmith Tracing

```python
import os

# Set BEFORE any LangChain imports
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"]    = "ls__your_key"
os.environ["LANGCHAIN_PROJECT"]    = "agentic-ai-dev"

# After this, ALL LangChain/LangGraph calls auto-trace to https://smith.langchain.com
# Zero code change needed — traces appear automatically

# Add custom metadata to traces
from langsmith import traceable

@traceable(name="My RAG Pipeline", metadata={"version": "1.2"})
def my_pipeline(query: str) -> str:
    return rag_chain.invoke(query)
```

---

## 9.2 State Inspection

```python
# Inspect graph state at any checkpoint
config = {"configurable": {"thread_id": "debug-001"}}

# Current state
state = graph.get_state(config)
print(f"Current values: {state.values}")
print(f"Next node:      {state.next}")
print(f"Created at:     {state.created_at}")

# Full history (all states since start)
for snapshot in graph.get_state_history(config):
    step = snapshot.metadata.get("step", 0)
    node = snapshot.metadata.get("source", "unknown")
    msg_count = len(snapshot.values.get("messages", []))
    print(f"Step {step:02d} | Node: {node:20s} | Messages: {msg_count}")
```

---

## 9.3 Structured Logging

```python
import logging
import json
import time
from functools import wraps
from datetime import datetime

# Configure (like Spring Boot Logback)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"agent_{datetime.now().strftime('%Y%m%d')}.log")
    ]
)
logger = logging.getLogger("agentic-ai")

# Decorator to log any node automatically
def logged_node(node_name: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(state: dict) -> dict:
            t0 = time.perf_counter()
            logger.info(f"→ [{node_name}] State keys: {list(state.keys())}")
            try:
                result = fn(state)
                elapsed = time.perf_counter() - t0
                logger.info(f"← [{node_name}] Done in {elapsed:.2f}s")
                return result
            except Exception as e:
                logger.error(f"✗ [{node_name}] FAILED: {e}", exc_info=True)
                raise
        return wrapper
    return decorator

# Usage
@logged_node("process_query")
def process_node(state: AgentState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}
```

---

## 9.4 Token Tracking

```python
from anthropic import Anthropic

client = Anthropic()

class TokenTracker:
    def __init__(self):
        self.total_input = 0
        self.total_output = 0
        # Approximate pricing (check Anthropic pricing page for current)
        self.input_price_per_mtok  = 3.0   # $ per million tokens
        self.output_price_per_mtok = 15.0

    def track(self, response) -> dict:
        inp  = response.usage.input_tokens
        out  = response.usage.output_tokens
        self.total_input  += inp
        self.total_output += out

        cost = (inp / 1_000_000 * self.input_price_per_mtok +
                out / 1_000_000 * self.output_price_per_mtok)

        return {
            "this_call": {"input": inp, "output": out, "cost_usd": round(cost, 6)},
            "session_total": {
                "input": self.total_input,
                "output": self.total_output,
                "cost_usd": round(
                    self.total_input  / 1_000_000 * self.input_price_per_mtok +
                    self.total_output / 1_000_000 * self.output_price_per_mtok, 4
                )
            }
        }

tracker = TokenTracker()

def tracked_llm_call(messages: list) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1024, messages=messages
    )
    usage = tracker.track(response)
    logger.info(f"Token usage: {usage}")
    return response.content[0].text
```

---

## ✅ Phase 9 Checklist
- [ ] Set up LangSmith and verify traces appear
- [ ] Inspect full state history for a multi-step graph
- [ ] Add `@logged_node` decorator to all graph nodes
- [ ] Track token usage + estimated cost per session
- [ ] Build a debug mode that pretty-prints state at each step

---

---

# ═══════════════════════════════════
# PHASE 10 — Production Engineering
# ═══════════════════════════════════
> **Duration:** Ongoing
> **Goal:** Make your agents reliable, safe, and cost-efficient

---

## 10.1 Rate Limiting + Exponential Backoff

```python
import asyncio
import time
from collections import deque
from functools import wraps

class TokenBucketLimiter:
    """Thread-safe rate limiter — like a Java Semaphore with time window"""
    def __init__(self, calls_per_minute: int):
        self.limit = calls_per_minute
        self.calls = deque()

    async def acquire(self):
        now = time.monotonic()
        # Evict calls older than 60s
        while self.calls and self.calls[0] < now - 60:
            self.calls.popleft()

        if len(self.calls) >= self.limit:
            wait = 60.0 - (now - self.calls[0]) + 0.1
            logger.warning(f"Rate limit reached — waiting {wait:.1f}s")
            await asyncio.sleep(wait)

        self.calls.append(time.monotonic())

limiter = TokenBucketLimiter(calls_per_minute=50)

def retry_on_error(max_retries: int = 3, base_delay: float = 1.0, backoff: float = 2.0):
    """Decorator: exponential backoff retry (like Spring Retry @Retryable)"""
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    await limiter.acquire()
                    return await fn(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (backoff ** attempt)
                    logger.warning(f"Attempt {attempt+1} failed: {e}. Retry in {delay:.1f}s")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

@retry_on_error(max_retries=3)
async def resilient_llm_call(prompt: str) -> str:
    # Call LLM with rate limiting + retry
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

---

## 10.2 Embedding Cache

```python
import hashlib
from typing import Optional
from collections import OrderedDict

class LRUEmbeddingCache:
    """LRU cache for embeddings — reduces API cost significantly"""
    def __init__(self, max_size: int = 5000):
        self._cache: OrderedDict[str, list] = OrderedDict()
        self.max_size = max_size
        self.hits = self.misses = 0

    def _key(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, text: str) -> Optional[list]:
        k = self._key(text)
        if k in self._cache:
            self._cache.move_to_end(k)  # LRU: move to end = recently used
            self.hits += 1
            return self._cache[k]
        self.misses += 1
        return None

    def set(self, text: str, embedding: list):
        k = self._key(text)
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)  # Evict least recently used
        self._cache[k] = embedding

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total, 3) if total else 0.0

embedding_cache = LRUEmbeddingCache()

def embed_with_cache(text: str, model) -> list:
    cached = embedding_cache.get(text)
    if cached:
        return cached
    vec = model.embed_query(text)
    embedding_cache.set(text, vec)
    return vec
```

---

## 10.3 Input/Output Guardrails

```python
import re
from typing import Tuple

class Guardrails:
    _INJECTION = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"forget\s+(all\s+)?previous",
        r"you\s+are\s+now\s+",
        r"new\s+persona",
        r"DAN\s+mode",
        r"jailbreak",
    ]
    _SENSITIVE_OUTPUT = [
        r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",  # Credit card
        r"\b\d{3}-\d{2}-\d{4}\b",                      # SSN
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}",  # Email
    ]

    @classmethod
    def validate_input(cls, text: str) -> Tuple[bool, str]:
        if len(text) > 10_000:
            return False, "Input exceeds 10,000 character limit"
        for pattern in cls._INJECTION:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Potential prompt injection detected"
        return True, "ok"

    @classmethod
    def sanitize_output(cls, text: str) -> str:
        for pattern in cls._SENSITIVE_OUTPUT:
            text = re.sub(pattern, "[REDACTED]", text, flags=re.IGNORECASE)
        return text

# FastAPI integration
@app.post("/chat/safe")
async def safe_chat(request: ChatRequest):
    is_safe, reason = Guardrails.validate_input(request.message)
    if not is_safe:
        raise HTTPException(status_code=400, detail=reason)

    raw = await resilient_llm_call(request.message)
    return {"response": Guardrails.sanitize_output(raw)}
```

---

## ✅ Phase 10 Checklist
- [ ] Add `TokenBucketLimiter` around all LLM calls
- [ ] Wrap LLM calls with `@retry_on_error` decorator
- [ ] Add `LRUEmbeddingCache` to your retrieval pipeline
- [ ] Add input guardrails (injection detection, length check)
- [ ] Add output sanitization (PII redaction)
- [ ] Log token cost per request

---

---

# ═══════════════════════════════════
# PHASE 11 — Scaling & Architecture
# ═══════════════════════════════════
> **Duration:** Ongoing
> **Goal:** Design production-grade systems

---

## Enterprise Architecture Diagram

```mermaid
graph TB
    subgraph CLIENTS["Client Layer"]
        WEB["🌐 Web App"]
        MOB["📱 Mobile"]
        EXT["🔌 3rd Party\nAPI Clients"]
    end

    subgraph GW["Gateway Layer"]
        APIGW["API Gateway\n• Auth / JWT\n• Rate Limiting\n• SSL Termination"]
    end

    subgraph APP["Application Layer"]
        ORCH_SVC["Orchestrator Service\nFastAPI"]
        W1["Agent Worker 1"]
        W2["Agent Worker 2"]
        W3["Agent Worker N"]
    end

    subgraph STATE["State & Cache Layer"]
        REDIS[("🟥 Redis\n• Session State\n• Embedding Cache\n• Rate Limit Counters")]
        PG[("🐘 PostgreSQL\n• LangGraph Checkpoints\n• Audit Logs")]
    end

    subgraph DATA["Data Layer"]
        VECTO[("🔵 Vector DB\nPinecone / Weaviate")]
        S3[("☁️ S3\nRaw Documents")]
    end

    subgraph OBS["Observability"]
        SMITH["LangSmith\nTracing"]
        PROM["Prometheus\n+ Grafana"]
    end

    WEB --> APIGW
    MOB --> APIGW
    EXT --> APIGW
    APIGW --> ORCH_SVC
    ORCH_SVC --> W1 & W2 & W3
    ORCH_SVC <--> REDIS
    ORCH_SVC <--> PG
    W1 & W2 & W3 --> VECTO & S3
    ORCH_SVC --> SMITH & PROM
```

---

## 11.1 Redis Session State

```python
import redis
import json
from datetime import timedelta

class SessionStore:
    def __init__(self, host="localhost", port=6379, ttl_minutes=60):
        self.r   = redis.Redis(host=host, port=port, decode_responses=True)
        self.ttl = timedelta(minutes=ttl_minutes)

    def _key(self, session_id: str) -> str:
        return f"session:{session_id}"

    def save(self, session_id: str, state: dict):
        self.r.setex(
            self._key(session_id),
            self.ttl,
            json.dumps(state, default=str)
        )

    def load(self, session_id: str) -> Optional[dict]:
        data = self.r.get(self._key(session_id))
        return json.loads(data) if data else None

    def extend(self, session_id: str):
        self.r.expire(self._key(session_id), int(self.ttl.total_seconds()))

    def delete(self, session_id: str):
        self.r.delete(self._key(session_id))

session_store = SessionStore()

# In FastAPI endpoint
@app.post("/chat/stateful")
async def stateful_chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    state = session_store.load(session_id) or {"messages": [], "context": {}}

    state["messages"].append({"role": "user", "content": request.message})
    reply = await resilient_llm_call(request.message)
    state["messages"].append({"role": "assistant", "content": reply})

    session_store.save(session_id, state)
    return {"response": reply, "session_id": session_id}
```

---

## 11.2 PostgreSQL Checkpointing (Production)

```python
# Switch from MemorySaver → PostgresSaver for persistent state
# pip install langgraph-checkpoint-postgres

from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:password@localhost:5432/agent_db"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()   # Creates langgraph_checkpoints table

    # Same graph, now with persistent checkpointing
    production_graph = builder.compile(checkpointer=checkpointer)

    # State survives server restarts!
    config = {"configurable": {"thread_id": "user-alice-session-42"}}
    result = production_graph.invoke(
        {"messages": [HumanMessage("Hello, I'm back!")]},
        config
    )
```

---

## 11.3 Background Task Queue

```python
# pip install celery redis
from celery import Celery

celery_app = Celery(
    "agent_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def run_research_task(self, task_id: str, query: str, user_id: str):
    try:
        # Long-running agent task in background
        result = orchestrator.run(query)
        session_store.save(f"result:{task_id}", {"status": "done", "result": result})
        return {"task_id": task_id, "status": "completed"}
    except Exception as exc:
        raise self.retry(exc=exc)

# FastAPI: submit task and return immediately
@app.post("/research/async")
async def submit_research(request: ChatRequest):
    task_id = str(uuid.uuid4())
    task = run_research_task.delay(task_id, request.message, "user-123")
    return {"task_id": task_id, "status": "queued", "celery_id": task.id}

@app.get("/research/{task_id}")
async def get_result(task_id: str):
    result = session_store.load(f"result:{task_id}")
    if not result:
        return {"status": "processing"}
    return result
```

---

## ✅ Phase 11 Checklist
- [ ] Set up Redis and implement `SessionStore`
- [ ] Switch to `PostgresSaver` for LangGraph checkpoints
- [ ] Run Celery worker and submit a background research task
- [ ] Draw your final system architecture diagram
- [ ] Load test with 10+ concurrent sessions

---

---

# 🎯 Final Projects — Build These

| # | Project | Phases Used | Complexity |
|---|---------|------------|------------|
| 1 | **Chat with PDF** (FastAPI + RAG) | 0, 1, 2 | ⭐⭐ |
| 2 | **Multi-doc Research Agent** | 0-4 | ⭐⭐⭐ |
| 3 | **Blog Generator** (Planner + Writer + Editor) | 0-5 | ⭐⭐⭐ |
| 4 | **Self-correcting RAG API** | 0-6, 8-10 | ⭐⭐⭐⭐ |
| 5 | **Enterprise RAG with HITL Review** | All phases | ⭐⭐⭐⭐⭐ |

---

# 📚 Key Libraries Reference

| Library | Purpose | Command |
|---------|---------|---------|
| `anthropic` | Anthropic Claude API | `pip install anthropic` |
| `openai` | OpenAI GPT API | `pip install openai` |
| `langchain` | LLM chains, RAG, tools | `pip install langchain` |
| `langchain-anthropic` | Anthropic LangChain integration | `pip install langchain-anthropic` |
| `langgraph` | Agent state machines | `pip install langgraph` |
| `chromadb` | Local vector DB | `pip install chromadb` |
| `faiss-cpu` | Fast similarity search | `pip install faiss-cpu` |
| `fastapi` | REST API | `pip install fastapi uvicorn` |
| `pydantic` | Data validation | `pip install pydantic` |
| `httpx` | Async HTTP client | `pip install httpx` |
| `langsmith` | Observability & tracing | `pip install langsmith` |
| `redis` | Session state & cache | `pip install redis` |
| `celery` | Background task queue | `pip install celery` |

---

# 🤖 IDE Prompt Templates

### General Phase Prompt
```
I am a Java backend developer learning Agentic AI (Python).
Current phase: Phase [N] — [Phase Name]
My notes are below. Please:
1. Expand all TODO sections with full implementations
2. Add proper error handling throughout
3. Explain concepts with Java analogies where helpful
4. Help me build the mini-project at the end of this phase
5. Point out common pitfalls Java developers hit in Python

[PASTE PHASE SECTION HERE]
```

### Debug Prompt
```
I am building an Agentic AI system with LangGraph.
Problem: [describe what's wrong]
Expected: [what should happen]
Actual: [what's happening]
Current state snapshot: [paste state]
Graph structure: [describe nodes/edges]

Help me debug this step by step.
I am a Java developer — Java analogies help.
```

### Architecture Review Prompt
```
Review my Agentic AI system design:
[paste your design]

I'm a Java/Spring Boot developer, familiar with:
- Microservices, REST APIs, message queues
- Spring State Machine, Spring Retry
- Redis, PostgreSQL, Kafka

Review for: correctness, scalability, cost efficiency, reliability.
Suggest improvements using patterns I'd recognize from Java.
```

### Code Review Prompt
```
Review this Python/LangGraph code.
I am a Java developer — flag:
1. Python anti-patterns I might have brought from Java
2. Missing error handling
3. Performance issues (sync where async needed, etc.)
4. Security issues

Code:
[paste your code]
```

---

*Generated from: "Complete Agentic AI Roadmap (0 → Production Engineer)" by @dhruvtechbytes*
*Tailored for Java Backend Developers | All examples use Python + Anthropic Claude + LangChain/LangGraph*
