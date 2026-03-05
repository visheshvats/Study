"""
MODULE 4 — Example 3: Planning Agent
======================================
An agent that PLANS before acting — creates a step-by-step plan,
then executes each step, adapting if something goes wrong.

This is more structured than a pure ReAct agent and better
for complex, multi-step tasks.

SETUP:
  pip install openai python-dotenv

RUN:
  python 03_planning_agent.py

ARCHITECTURE:
  User Task
       │
       ▼
  ┌──────────┐
  │  PLANNER  │  ← LLM creates step-by-step plan
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │ EXECUTOR  │  ← Executes each step using tools
  │ (loop)    │     Adapts plan if step fails
  └────┬─────┘
       │
       ▼
  Final Result
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ══════════════════════════════════════════════════════
# TOOLS
# ══════════════════════════════════════════════════════

def search_web(query: str) -> str:
    """Simulated web search."""
    results = {
        "spring boot 3 features": "Spring Boot 3.2: Virtual threads support, GraalVM native images, Micrometer tracing, improved Docker support.",
        "java 21 features": "Java 21: Virtual threads (Project Loom), pattern matching, record patterns, sequenced collections.",
        "kafka vs rabbitmq 2024": "Kafka: High throughput, event streaming, log-based. RabbitMQ: Lower latency, complex routing, traditional messaging.",
        "microservices best practices": "Use API Gateway, circuit breakers, distributed tracing, centralized logging, service mesh for advanced cases.",
    }
    for key, value in results.items():
        if any(word in key for word in query.lower().split()[:3]):
            return json.dumps({"query": query, "results": [value]})
    return json.dumps({"query": query, "results": ["No results found for this query."]})


def analyze_data(data: str, analysis_type: str = "summary") -> str:
    """Simulated data analysis."""
    return json.dumps({
        "analysis_type": analysis_type,
        "input_preview": data[:100],
        "result": f"Analysis ({analysis_type}) completed. Key findings: The data indicates significant trends in the described area.",
    })


def write_report(title: str, sections: str) -> str:
    """Create a structured report."""
    return json.dumps({
        "title": title,
        "sections": sections,
        "status": "created",
        "word_count": len(sections.split()),
    })


TOOLS_IMPL = {
    "search_web": search_web,
    "analyze_data": analyze_data,
    "write_report": write_report,
}

TOOL_DEFS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information on a topic.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Search query"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_data",
            "description": "Analyze text data with a specific analysis type (summary, comparison, trends).",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "Data to analyze"},
                    "analysis_type": {"type": "string", "enum": ["summary", "comparison", "trends"]},
                },
                "required": ["data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_report",
            "description": "Create a structured report with a title and content sections.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Report title"},
                    "sections": {"type": "string", "description": "Report content (markdown formatted)"},
                },
                "required": ["title", "sections"],
            },
        },
    },
]


# ══════════════════════════════════════════════════════
# PLANNING AGENT
# ══════════════════════════════════════════════════════

class PlanningAgent:
    """
    An agent that creates a plan, then executes it step by step.
    
    Architecture:
      Phase 1: PLAN — LLM creates numbered steps
      Phase 2: EXECUTE — Agent loop runs each step
      Phase 3: SYNTHESIZE — Combine all results
    
    Java Analogy: Like a Spring Batch job with dynamic step generation.
    The "job" is planned at runtime based on the task.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def _log(self, icon: str, text: str):
        if self.verbose:
            print(f"    {icon} {text}")

    def create_plan(self, task: str) -> list[str]:
        """Phase 1: Use LLM to create an execution plan."""
        self._log("📋", "Creating plan...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "You are a planning agent. Given a task, create a step-by-step "
                    "execution plan. Each step should be a concrete, actionable item. "
                    "Return JSON: {\"steps\": [\"Step 1: ...\", \"Step 2: ...\"]}\n"
                    "Keep plans to 3-5 steps. Be specific about what tool to use in each step.\n"
                    "Available tools: search_web, analyze_data, write_report"
                )},
                {"role": "user", "content": f"Task: {task}"}
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        plan = json.loads(response.choices[0].message.content)
        steps = plan.get("steps", [])

        self._log("📋", f"Plan created with {len(steps)} steps:")
        for i, step in enumerate(steps, 1):
            self._log("  ", f"{i}. {step}")

        return steps

    def execute_step(self, step: str, context: str = "") -> str:
        """Phase 2: Execute a single step using tools."""
        messages = [
            {"role": "system", "content": (
                "You are executing a specific step in a plan. "
                "Use the available tools to complete this step. "
                "Be concise and focused on this one step.\n"
                f"Previous context: {context[:500]}" if context else ""
            )},
            {"role": "user", "content": f"Execute this step: {step}"},
        ]

        # Agent loop for this step
        for _ in range(5):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOL_DEFS,
                tool_choice="auto",
            )

            message = response.choices[0].message

            if message.tool_calls:
                messages.append(message)
                for tool_call in message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    self._log("🔧", f"{fn_name}({json.dumps(fn_args)[:60]})")

                    result = TOOLS_IMPL.get(fn_name, lambda **k: '{"error":"unknown"}')(**fn_args)
                    self._log("📋", f"→ {result[:80]}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
            else:
                return message.content

        return "Step execution timed out."

    def synthesize(self, task: str, step_results: list[dict]) -> str:
        """Phase 3: Combine all step results into a final answer."""
        results_text = "\n\n".join(
            f"Step {r['step_num']}: {r['step']}\nResult: {r['result']}"
            for r in step_results
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "Synthesize the results from all executed steps into "
                    "a clear, comprehensive answer to the original task. "
                    "Be concise and well-structured."
                )},
                {"role": "user", "content": (
                    f"Original task: {task}\n\n"
                    f"Step results:\n{results_text}\n\n"
                    f"Provide the final synthesized answer:"
                )}
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content

    def run(self, task: str) -> str:
        """Run the complete planning agent pipeline."""
        self._log("🎯", f"Task: {task}\n")

        # Phase 1: Plan
        steps = self.create_plan(task)

        # Phase 2: Execute each step
        step_results = []
        context = ""

        for i, step in enumerate(steps, 1):
            self._log("▶️ ", f"\n--- Executing Step {i}/{len(steps)} ---")
            self._log("📌", step)

            result = self.execute_step(step, context)
            step_results.append({
                "step_num": i,
                "step": step,
                "result": result,
            })

            # Build context for next step
            context += f"\nStep {i} result: {result[:200]}"

            self._log("✅", f"Step {i} complete")

        # Phase 3: Synthesize
        self._log("🔗", "\n--- Synthesizing final answer ---")
        final = self.synthesize(task, step_results)

        return final


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  📋 Planning Agent                            ║")
    print("║  Plan → Execute → Synthesize                  ║")
    print("╚══════════════════════════════════════════════╝")

    agent = PlanningAgent()

    # Task: Research and compare
    print(f"\n{'='*55}")
    print("TASK: Technology comparison research")
    print(f"{'='*55}")

    result = agent.run(
        "Research Spring Boot 3 and Java 21 features. "
        "Compare them with the current microservices best practices. "
        "Write a brief technology adoption report."
    )

    print(f"\n{'='*55}")
    print("📝 FINAL REPORT:")
    print(f"{'='*55}")
    print(result)

    print(f"\n\n{'='*55}")
    print("✅ Planning agent is better for complex tasks because:")
    print("  • Creates a clear plan upfront (transparency)")
    print("  • Each step is focused and manageable")
    print("  • Can adapt plan if a step fails")
    print("  • Easier to debug (which step went wrong?)")
    print("  • Better cost control (predictable # of steps)\n")


if __name__ == "__main__":
    main()
