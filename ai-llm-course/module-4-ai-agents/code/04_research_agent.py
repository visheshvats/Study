"""
MODULE 4 — PROJECT: Multi-Tool Research Agent
================================================
A production-style agent that can research topics using multiple tools,
maintain conversation context, and produce structured outputs.

This is the capstone project for Module 4 — it combines:
  - Function calling (Module 4.1)
  - Agent loop (Module 4.2)
  - RAG-style search (Module 3)
  - Structured output (Module 1)
  - All best practices

SETUP:
  pip install openai chromadb python-dotenv

RUN:
  python 04_research_agent.py

FEATURES:
  🔍 Web search (simulated)
  📚 Knowledge base search (ChromaDB)
  🧮 Calculator
  📝 Note taking
  💬 Interactive chat with agent memory
"""

import os
import json
import math
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ══════════════════════════════════════════════════════
# TOOLS
# ══════════════════════════════════════════════════════

class ResearchTools:
    """All tools available to the research agent."""

    def __init__(self):
        self.notes: list[dict] = []
        self._setup_knowledge_base()

    def _setup_knowledge_base(self):
        """Create a ChromaDB knowledge base with tech content."""
        self.chroma = chromadb.Client()
        self.kb = self.chroma.create_collection(name="research_kb")

        docs = [
            {"text": "Spring Boot 3.2 introduces support for virtual threads (Project Loom), enabling high-throughput applications with simple blocking code. Configure with spring.threads.virtual.enabled=true. This eliminates the need for reactive programming (WebFlux) in most I/O-bound applications. Performance benchmarks show 10x improvement in concurrent request handling.", "topic": "spring-boot"},
            {"text": "GraalVM native images compile Java applications ahead of time, producing standalone executables. Startup time drops from seconds to milliseconds, memory usage reduces by 50-80%. Spring Boot 3 has first-class support via spring-boot-maven-plugin. Trade-off: longer build times (2-5 minutes) and some reflection limitations.", "topic": "graalvm"},
            {"text": "Kafka Streams is a client library for building real-time stream processing applications. It provides stateful processing with local state stores (RocksDB), exactly-once semantics, and interactive queries. Unlike Spark Streaming, it doesn't require a separate cluster — it runs as a regular Java application inside your Spring Boot service.", "topic": "kafka"},
            {"text": "Apache Kafka 3.6 introduces the KRaft consensus protocol, eliminating ZooKeeper dependency. Tiered storage allows moving cold data to S3/GCS automatically. Consumer group protocol improvements reduce rebalancing time from seconds to milliseconds. The new consumer API provides better error handling and offset management.", "topic": "kafka"},
            {"text": "Kubernetes Horizontal Pod Autoscaler (HPA) scales based on CPU, memory, or custom metrics. For Spring Boot apps, expose custom metrics via Micrometer → Prometheus. Create HPA with: kubectl autoscale deployment myapp --cpu-percent=70 --min=2 --max=10. Use PodDisruptionBudget to ensure minimum replicas during deployments.", "topic": "kubernetes"},
            {"text": "Observability stack for microservices: Micrometer for metrics (integrates with Prometheus/Grafana), OpenTelemetry for distributed tracing (replaces Sleuth/Zipkin), and structured logging with ELK stack (Elasticsearch, Logstash, Kibana). Spring Boot 3 has built-in support for all three. Correlation IDs (traceId) enable request tracking across services.", "topic": "observability"},
            {"text": "Database migration strategies: Use Flyway or Liquibase for schema versioning. Blue-green deployments require backward-compatible migrations. Zero-downtime migration pattern: (1) Add new column, (2) Dual-write to old and new, (3) Migrate existing data, (4) Switch reads to new column, (5) Remove old column. Never do destructive migrations in a single step.", "topic": "database"},
            {"text": "API versioning strategies: URL versioning (/api/v1/users), header versioning (Accept: application/vnd.api.v1+json), or query parameter (?version=1). URL versioning is most common and explicit. For backward compatibility, keep deprecated endpoints alive for at least 2 major versions. Use OpenAPI/Swagger for documentation.", "topic": "api-design"},
        ]

        self.kb.add(
            documents=[d["text"] for d in docs],
            metadatas=[{"topic": d["topic"]} for d in docs],
            ids=[f"doc_{i}" for i in range(len(docs))],
        )

    def search_web(self, query: str) -> str:
        """Simulated web search with realistic results."""
        results_db = {
            "virtual threads java": [
                "Virtual threads in Java 21 allow millions of concurrent threads with minimal memory. Each virtual thread uses ~1KB vs 1MB for platform threads. Ideal for I/O-bound web services.",
                "Virtual threads use continuation-based scheduling. When a virtual thread blocks on I/O, the carrier thread is released to run other virtual threads.",
            ],
            "spring boot 2024": [
                "Spring Boot 3.3 (2024): Improved Docker Compose support, better SSL bundle configuration, enhanced support for testcontainers.",
                "Spring Framework 6.1: RestClient (new fluent HTTP client), improved AOT processing, better Kotlin support.",
            ],
            "microservices patterns": [
                "Key patterns: Saga pattern for distributed transactions, CQRS for read/write separation, Event sourcing for audit trails, Strangler fig for migrations.",
                "Anti-patterns: Distributed monolith, death star architecture, chatty services, shared databases.",
            ],
        }

        for key, results in results_db.items():
            if any(word in key for word in query.lower().split()[:3]):
                return json.dumps({"query": query, "results": results, "source": "web"})

        return json.dumps({"query": query, "results": [f"General information about: {query}"], "source": "web"})

    def search_knowledge_base(self, query: str, n_results: int = 3) -> str:
        """Search the internal knowledge base using ChromaDB."""
        results = self.kb.query(query_texts=[query], n_results=n_results)

        formatted = []
        for i in range(len(results["documents"][0])):
            formatted.append({
                "text": results["documents"][0][i],
                "topic": results["metadatas"][0][i]["topic"],
                "relevance": round(1 - results["distances"][0][i] / 2, 3),
            })

        return json.dumps({"query": query, "results": formatted, "source": "knowledge_base"})

    def calculate(self, expression: str) -> str:
        """Safe calculator with math functions."""
        try:
            safe = {"__builtins__": {}, "math": math, "abs": abs, "round": round, "sum": sum, "min": min, "max": max}
            result = eval(expression, safe)
            return json.dumps({"expression": expression, "result": result})
        except Exception as e:
            return json.dumps({"error": f"Calculation error: {str(e)}"})

    def save_note(self, title: str, content: str, tags: str = "") -> str:
        """Save a research note."""
        note = {
            "id": len(self.notes) + 1,
            "title": title,
            "content": content,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.notes.append(note)
        return json.dumps({"status": "saved", "note": note})

    def get_notes(self) -> str:
        """Retrieve all saved notes."""
        if not self.notes:
            return json.dumps({"notes": [], "message": "No notes saved yet."})
        return json.dumps({"notes": self.notes, "count": len(self.notes)})

    def get_current_datetime(self) -> str:
        """Get current date and time."""
        now = datetime.now()
        return json.dumps({"datetime": now.isoformat(), "day": now.strftime("%A")})


# Tool definitions for OpenAI
TOOL_DEFS = [
    {"type": "function", "function": {
        "name": "search_web",
        "description": "Search the web for information about a topic. Best for current trends, comparisons, and general knowledge.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "Search query (be specific for better results)"}
        }, "required": ["query"]},
    }},
    {"type": "function", "function": {
        "name": "search_knowledge_base",
        "description": "Search our internal knowledge base for technical documentation about Spring Boot, Kafka, Kubernetes, databases, API design, and observability.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "Technical search query"},
            "n_results": {"type": "integer", "description": "Number of results (default: 3)"},
        }, "required": ["query"]},
    }},
    {"type": "function", "function": {
        "name": "calculate",
        "description": "Evaluate math expressions. Supports math module functions (sqrt, sin, cos, log, etc.).",
        "parameters": {"type": "object", "properties": {
            "expression": {"type": "string", "description": "Math expression (e.g., 'math.sqrt(144)', '2**10')"}
        }, "required": ["expression"]},
    }},
    {"type": "function", "function": {
        "name": "save_note",
        "description": "Save a research note with title, content, and optional tags. Use this to record findings.",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string", "description": "Note title"},
            "content": {"type": "string", "description": "Note content (markdown supported)"},
            "tags": {"type": "string", "description": "Comma-separated tags (e.g., 'spring,java,performance')"},
        }, "required": ["title", "content"]},
    }},
    {"type": "function", "function": {
        "name": "get_notes",
        "description": "Retrieve all previously saved research notes.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "get_current_datetime",
        "description": "Get the current date, time, and day of the week.",
        "parameters": {"type": "object", "properties": {}},
    }},
]


# ══════════════════════════════════════════════════════
# RESEARCH AGENT
# ══════════════════════════════════════════════════════

class ResearchAgent:
    """
    A multi-tool research agent with conversation memory.
    
    Combines all patterns from Module 4:
    - ReAct loop (think → act → observe)
    - Multiple tools (search, KB, calculator, notes)
    - Conversation memory (multi-turn)
    - Cost tracking
    """

    SYSTEM_PROMPT = """You are a senior software engineering research assistant specializing in Java, Spring Boot, Kafka, databases, and cloud-native architecture.

CAPABILITIES:
- Search the web for current information
- Search the internal knowledge base for technical documentation
- Do calculations
- Save and retrieve research notes

BEHAVIOR RULES:
1. Think step by step before using tools
2. Use the knowledge base for internal documentation, web search for external/current info
3. Always cite your sources (web search vs knowledge base)
4. Save important findings as notes when asked
5. Be concise, technical, and practical
6. If asked about something you can't find, say so honestly"""

    def __init__(self):
        self.tools = ResearchTools()
        self.messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        self.total_tokens = 0
        self.tool_calls_count = 0

        # Map tool names to methods
        self.tool_map = {
            "search_web": self.tools.search_web,
            "search_knowledge_base": self.tools.search_knowledge_base,
            "calculate": self.tools.calculate,
            "save_note": self.tools.save_note,
            "get_notes": self.tools.get_notes,
            "get_current_datetime": self.tools.get_current_datetime,
        }

    def chat(self, user_input: str) -> str:
        """Process a user message through the agent loop."""
        self.messages.append({"role": "user", "content": user_input})

        max_iterations = 10
        for iteration in range(max_iterations):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                tools=TOOL_DEFS,
                tool_choice="auto",
            )

            message = response.choices[0].message
            self.total_tokens += response.usage.total_tokens

            if message.tool_calls:
                self.messages.append(message)

                for tool_call in message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    self.tool_calls_count += 1

                    print(f"    🔧 {fn_name}({json.dumps(fn_args)[:60]})")

                    fn = self.tool_map.get(fn_name)
                    result = fn(**fn_args) if fn else json.dumps({"error": "Unknown tool"})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
            else:
                self.messages.append(message)
                return message.content

        return "Research agent reached max iterations."

    def get_stats(self) -> dict:
        return {
            "total_tokens": self.total_tokens,
            "tool_calls": self.tool_calls_count,
            "messages": len(self.messages),
            "notes": len(self.tools.notes),
        }


# ══════════════════════════════════════════════════════
# INTERACTIVE DEMO
# ══════════════════════════════════════════════════════

def run_demo():
    """Run pre-defined research tasks."""
    agent = ResearchAgent()

    tasks = [
        "Research virtual threads in Spring Boot. What are the key benefits and how do I enable them?",
        "Compare Kafka's KRaft mode with the old ZooKeeper approach. Save the comparison as a note.",
        "How should I set up observability for my Spring Boot microservices? What tools do I need?",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"\n  {'═'*55}")
        print(f"  📌 Task {i}: {task[:60]}...")
        print(f"  {'─'*55}")

        answer = agent.chat(task)

        print(f"\n  🤖 {answer[:300]}...")

    stats = agent.get_stats()
    print(f"\n  {'═'*55}")
    print(f"  📊 Session stats:")
    print(f"     Tokens: {stats['total_tokens']:,}")
    print(f"     Tool calls: {stats['tool_calls']}")
    print(f"     Notes saved: {stats['notes']}")


def run_interactive():
    """Interactive chat with the research agent."""
    agent = ResearchAgent()

    print(f"\n  💡 Commands:")
    print(f"     /notes   — Show saved notes")
    print(f"     /stats   — Show session stats")
    print(f"     /quit    — Exit\n")

    while True:
        try:
            user_input = input("  👤 You: ").strip()
            if not user_input:
                continue

            if user_input == "/quit":
                break
            elif user_input == "/notes":
                notes = json.loads(agent.tools.get_notes())
                if notes.get("notes"):
                    for n in notes["notes"]:
                        print(f"\n    📝 [{n['id']}] {n['title']}")
                        print(f"       {n['content'][:100]}")
                        if n.get("tags"):
                            print(f"       Tags: {', '.join(n['tags'])}")
                else:
                    print("    No notes saved.")
                print()
                continue
            elif user_input == "/stats":
                s = agent.get_stats()
                print(f"\n    Tokens: {s['total_tokens']:,} | Tools: {s['tool_calls']} | Notes: {s['notes']}\n")
                continue

            answer = agent.chat(user_input)
            print(f"\n  🤖 {answer}\n")

        except (KeyboardInterrupt, EOFError):
            break

    print("\n  👋 Goodbye!\n")


def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🔬 Multi-Tool Research Agent                ║")
    print("║  MODULE 4 PROJECT                            ║")
    print("║                                              ║")
    print("║  Tools: Web Search, Knowledge Base,          ║")
    print("║  Calculator, Notes, DateTime                 ║")
    print("╚══════════════════════════════════════════════╝\n")

    print("  Choose mode:")
    print("  1. Run demo (pre-defined research tasks)")
    print("  2. Interactive chat\n")

    try:
        choice = input("  Enter 1 or 2: ").strip()
    except (KeyboardInterrupt, EOFError):
        choice = "1"

    if choice == "2":
        run_interactive()
    else:
        run_demo()

    print("\n  ✅ Module 4 Project complete!")
    print("     This agent demonstrates:")
    print("     • ReAct loop with 6 tools")
    print("     • ChromaDB knowledge base (RAG)")
    print("     • Multi-turn conversation memory")
    print("     • Note-taking for research organization")
    print("     • Cost tracking and guardrails\n")


if __name__ == "__main__":
    main()
