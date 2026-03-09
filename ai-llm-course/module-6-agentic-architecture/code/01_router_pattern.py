"""
MODULE 6 — Example 1: Router Pattern
=======================================
A classifier agent that routes requests to specialist agents.

Like a Spring Cloud Gateway — one entry point, routes to
the right microservice based on the request type.

SETUP:
  pip install openai python-dotenv

RUN:
  python 01_router_pattern.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# ══════════════════════════════════════════════════════
# SPECIALIST AGENTS (each has focused expertise)
# ══════════════════════════════════════════════════════

def code_agent(query: str) -> str:
    """Specialist for coding and technical questions."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a senior software engineer specializing in Java, Spring Boot, "
                "and microservices. Provide concise, practical code examples and explanations. "
                "Always include code snippets when relevant."
            )},
            {"role": "user", "content": query},
        ],
        temperature=0.3,
        max_tokens=400,
    )
    return response.choices[0].message.content


def data_agent(query: str) -> str:
    """Specialist for data, SQL, and analytics questions."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a data engineer expert in SQL, PostgreSQL, data modeling, "
                "and analytics. Provide optimized queries, schema designs, and data "
                "pipeline recommendations. Include SQL examples."
            )},
            {"role": "user", "content": query},
        ],
        temperature=0.3,
        max_tokens=400,
    )
    return response.choices[0].message.content


def devops_agent(query: str) -> str:
    """Specialist for DevOps, CI/CD, and infrastructure."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a DevOps/SRE expert in Docker, Kubernetes, CI/CD, "
                "and cloud infrastructure. Provide actionable steps, YAML configs, "
                "and shell commands. Focus on production best practices."
            )},
            {"role": "user", "content": query},
        ],
        temperature=0.3,
        max_tokens=400,
    )
    return response.choices[0].message.content


def general_agent(query: str) -> str:
    """Fallback for general questions."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Provide clear, concise answers."},
            {"role": "user", "content": query},
        ],
        temperature=0.5,
        max_tokens=300,
    )
    return response.choices[0].message.content


SPECIALIST_MAP = {
    "code": {"agent": code_agent, "icon": "💻", "name": "Code Agent"},
    "data": {"agent": data_agent, "icon": "📊", "name": "Data Agent"},
    "devops": {"agent": devops_agent, "icon": "🔧", "name": "DevOps Agent"},
    "general": {"agent": general_agent, "icon": "💬", "name": "General Agent"},
}


# ══════════════════════════════════════════════════════
# ROUTER AGENT (the classifier/dispatcher)
# ══════════════════════════════════════════════════════

def route_query(query: str) -> dict:
    """
    Uses LLM to classify the query and route to the right specialist.
    
    This is the Router Pattern — like an API Gateway deciding
    which microservice handles the request.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "Classify the user's question into exactly ONE category.\n"
                "Categories:\n"
                "- code: Programming, software design, Java, Spring Boot, APIs, code review\n"
                "- data: SQL, databases, data modeling, analytics, ETL, data pipelines\n"
                "- devops: Docker, Kubernetes, CI/CD, deployments, infrastructure, monitoring\n"
                "- general: Everything else\n\n"
                "Return JSON: {\"category\": \"...\", \"reasoning\": \"...\"}"
            )},
            {"role": "user", "content": query},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result


def multi_agent_router(query: str) -> str:
    """
    The complete router pipeline:
    1. Classify the query
    2. Route to the right specialist
    3. Return the specialist's answer
    """
    # Step 1: Route
    route = route_query(query)
    category = route.get("category", "general")
    reasoning = route.get("reasoning", "")

    # Step 2: Dispatch
    specialist = SPECIALIST_MAP.get(category, SPECIALIST_MAP["general"])

    print(f"    🔀 Router: {category} → {specialist['icon']} {specialist['name']}")
    print(f"    📝 Reasoning: {reasoning}")

    # Step 3: Specialist answers
    answer = specialist["agent"](query)
    return answer


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🔀 Router Pattern — Multi-Domain Agent      ║")
    print("╚══════════════════════════════════════════════╝")

    queries = [
        "How do I implement a circuit breaker in Spring Boot?",
        "Write a SQL query to find the top 5 customers by revenue",
        "How do I set up a Kubernetes HPA for auto-scaling?",
        "What's a good strategy for team retrospectives?",
    ]

    for query in queries:
        print(f"\n  {'═'*55}")
        print(f"  👤 Query: {query}")
        print(f"  {'─'*55}")

        answer = multi_agent_router(query)
        print(f"\n  🤖 Answer: {answer[:200]}...")

    print(f"\n\n  {'═'*55}")
    print(f"  ✅ Router Pattern takeaways:")
    print(f"     • One entry point, multiple specialists")
    print(f"     • LLM classifies → code routes → specialist answers")
    print(f"     • Each specialist has a focused, expert system prompt")
    print(f"     • Like API Gateway routing to microservices\n")


if __name__ == "__main__":
    main()
