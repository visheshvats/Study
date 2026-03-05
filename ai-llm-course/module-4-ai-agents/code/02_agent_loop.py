"""
MODULE 4 — Example 2: Build an Agent Loop from Scratch
========================================================
A complete ReAct agent with NO FRAMEWORKS — just OpenAI + Python.

This shows that an agent is just:
  while True:
      response = LLM(messages, tools)
      if response.has_tool_call:
          result = execute(tool_call)
          messages.append(result)
      else:
          return response.text

SETUP:
  pip install openai python-dotenv

RUN:
  python 02_agent_loop.py
"""

import os
import json
import math
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ══════════════════════════════════════════════════════
# TOOLS — These are the "superpowers" of our agent
# ══════════════════════════════════════════════════════

class ToolBox:
    """
    Collection of tools the agent can use.
    
    Java Analogy: This is like a @Service layer.
    Each method is a service that the controller (LLM) can invoke.
    """

    @staticmethod
    def calculate(expression: str) -> str:
        """Evaluate a math expression safely."""
        try:
            safe_dict = {"__builtins__": {}, "math": math, "abs": abs, "round": round}
            result = eval(expression, safe_dict)
            return json.dumps({"result": result, "expression": expression})
        except Exception as e:
            return json.dumps({"error": f"Cannot evaluate '{expression}': {str(e)}"})

    @staticmethod
    def get_current_time() -> str:
        """Get the current date and time."""
        now = datetime.now()
        return json.dumps({
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
        })

    @staticmethod
    def search_knowledge(query: str) -> str:
        """Search an internal knowledge base (simulated)."""
        kb = {
            "spring boot": "Spring Boot 3.2 is the latest version, requires Java 17+. Key features: auto-config, embedded server, actuator.",
            "kafka": "Apache Kafka 3.6 is current. Use with Spring Kafka 3.1. Default partitions: 1. Max message size: 1MB.",
            "docker": "Use multi-stage builds. Base image: amazoncorretto:21-alpine. Don't run as root. Use .dockerignore.",
            "kubernetes": "Use kubectl apply -f deployment.yaml. Readiness probe: /actuator/health. Resource limits recommended.",
            "postgresql": "Version 16 is latest. Use HikariCP pool (default in Spring Boot). Index strategy: B-tree for equality, GIN for JSONB.",
        }

        results = []
        for key, value in kb.items():
            if any(word in key for word in query.lower().split()):
                results.append({"topic": key, "info": value})

        if results:
            return json.dumps({"results": results})
        return json.dumps({"results": [], "message": f"No results for '{query}'"})

    @staticmethod
    def create_note(title: str, content: str) -> str:
        """Create a note (simulated — would write to file/DB in production)."""
        note = {
            "id": abs(hash(title)) % 10000,
            "title": title,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "status": "created",
        }
        return json.dumps(note)

    @staticmethod
    def list_files(directory: str = ".") -> str:
        """List files in a directory (limited to current dir for safety)."""
        try:
            import pathlib
            path = pathlib.Path(directory)
            if not path.exists():
                return json.dumps({"error": f"Directory '{directory}' not found"})
            files = [
                {"name": f.name, "type": "file" if f.is_file() else "dir", "size": f.stat().st_size if f.is_file() else None}
                for f in sorted(path.iterdir())
                if not f.name.startswith(".")
            ][:20]  # Limit to 20 items
            return json.dumps({"directory": str(path), "files": files, "count": len(files)})
        except Exception as e:
            return json.dumps({"error": str(e)})


# Tool registry — maps names to implementations
TOOL_REGISTRY = {
    "calculate": ToolBox.calculate,
    "get_current_time": ToolBox.get_current_time,
    "search_knowledge": ToolBox.search_knowledge,
    "create_note": ToolBox.create_note,
    "list_files": ToolBox.list_files,
}

# Tool definitions for OpenAI
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression. Supports basic math, math module functions (sqrt, sin, cos, etc.), abs, and round.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression (e.g., 'math.sqrt(144)', '2**10', '3.14 * 5**2')"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date, time, and day of the week.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Search the internal knowledge base for information about technologies like Spring Boot, Kafka, Docker, Kubernetes, PostgreSQL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (e.g., 'spring boot version', 'kafka configuration')"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Create a note with a title and content. Use this to save important findings or summaries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the note"},
                    "content": {"type": "string", "description": "Content of the note"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories in the current directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory path (default: current directory)"}
                },
            },
        },
    },
]


# ══════════════════════════════════════════════════════
# THE AGENT — The core loop
# ══════════════════════════════════════════════════════

class Agent:
    """
    A ReAct agent built from scratch.
    
    The entire agent is just a while loop:
      1. Ask LLM what to do
      2. If tool call → execute → feed result back
      3. If text response → we're done
    """

    def __init__(
        self,
        system_prompt: str = None,
        max_iterations: int = 10,
        verbose: bool = True,
    ):
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.system_prompt = system_prompt or (
            "You are a helpful assistant with access to tools. "
            "Use tools when you need factual data or need to perform actions. "
            "Think step by step before using tools. "
            "After getting tool results, provide a clear, concise answer."
        )
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.total_tokens = 0

    def _log(self, icon: str, text: str):
        """Print formatted log message."""
        if self.verbose:
            print(f"    {icon} {text}")

    def run(self, user_input: str) -> str:
        """
        Run the agent loop for a user query.
        
        This is THE core of every AI agent — ~20 lines of actual logic.
        Everything else is polish.
        """
        self.messages.append({"role": "user", "content": user_input})
        self._log("👤", f"User: {user_input}")

        for iteration in range(1, self.max_iterations + 1):
            self._log("🔄", f"--- Iteration {iteration}/{self.max_iterations} ---")

            # Ask LLM what to do next
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )

            message = response.choices[0].message
            self.total_tokens += response.usage.total_tokens

            # Case 1: LLM wants to call tools
            if message.tool_calls:
                self.messages.append(message)

                for tool_call in message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    self._log("🔧", f"Tool: {fn_name}({json.dumps(fn_args)[:80]})")

                    # Execute the tool
                    if fn_name in TOOL_REGISTRY:
                        try:
                            result = TOOL_REGISTRY[fn_name](**fn_args)
                        except Exception as e:
                            result = json.dumps({"error": str(e)})
                    else:
                        result = json.dumps({"error": f"Unknown tool: {fn_name}"})

                    self._log("📋", f"Result: {result[:100]}")

                    # Feed result back to LLM
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

            # Case 2: LLM gives text response → we're done
            else:
                self._log("🤖", f"Answer: {message.content[:150]}...")
                self._log("📊", f"Total tokens used: {self.total_tokens}")
                self.messages.append(message)
                return message.content

        return "Max iterations reached. Please try a simpler query."


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🤖 ReAct Agent — Built from Scratch         ║")
    print("║  No frameworks, just OpenAI + Python          ║")
    print("╚══════════════════════════════════════════════╝")

    # Test 1: Single tool
    print(f"\n{'='*55}")
    print("TEST 1: Simple tool usage")
    print(f"{'='*55}")
    agent1 = Agent()
    agent1.run("What time is it right now?")

    # Test 2: Multi-step reasoning
    print(f"\n{'='*55}")
    print("TEST 2: Multi-step reasoning")
    print(f"{'='*55}")
    agent2 = Agent()
    agent2.run(
        "Calculate the area of a circle with radius 7.5, "
        "then save the result in a note called 'Circle Calculation'."
    )

    # Test 3: Research task
    print(f"\n{'='*55}")
    print("TEST 3: Research + summarize")
    print(f"{'='*55}")
    agent3 = Agent()
    agent3.run(
        "Look up information about Spring Boot and Kafka in our knowledge base. "
        "What versions are current and how do they work together?"
    )

    # Test 4: No tools needed
    print(f"\n{'='*55}")
    print("TEST 4: Direct answer (no tools)")
    print(f"{'='*55}")
    agent4 = Agent()
    agent4.run("What is the difference between REST and GraphQL?")

    print(f"\n{'='*55}")
    print("✅ Key insights:")
    print("  • The agent loop is just ~20 lines of logic")
    print("  • LLM DECIDES what tool to use (or none)")
    print("  • Multi-step tasks work naturally via the loop")
    print("  • Max iterations prevent infinite loops\n")


if __name__ == "__main__":
    main()
