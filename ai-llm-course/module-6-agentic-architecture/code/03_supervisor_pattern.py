"""
MODULE 6 — Example 3: Supervisor Pattern
==========================================
A manager agent that delegates to workers, reviews output,
and re-assigns if quality isn't good enough.

Like a Kubernetes controller loop:
  Observe → Decide → Act → Repeat

SETUP:
  pip install openai python-dotenv

RUN:
  python 03_supervisor_pattern.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# ══════════════════════════════════════════════════════
# WORKER AGENTS
# ══════════════════════════════════════════════════════

def code_writer(task: str, feedback: str = "") -> str:
    """Worker that writes code based on a task description."""
    context = ""
    if feedback:
        context = f"\n\nPrevious attempt received this feedback:\n{feedback}\nPlease address all feedback points."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a Java/Spring Boot developer. Write clean, production-ready code. "
                "Include proper error handling, logging, and Javadoc comments. "
                "Follow SOLID principles and Spring best practices."
            )},
            {"role": "user", "content": f"Write code for: {task}{context}"},
        ],
        temperature=0.3,
        max_tokens=600,
    )
    return response.choices[0].message.content


def code_reviewer(code: str, requirements: str) -> dict:
    """Worker that reviews code and provides structured feedback."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "You are a senior code reviewer. Review the code against requirements. "
                "Return JSON with this structure:\n"
                "{\n"
                '  "approved": true/false,\n'
                '  "score": 1-10,\n'
                '  "issues": ["issue 1", "issue 2"],\n'
                '  "strengths": ["strength 1"],\n'
                '  "feedback": "summary for the developer"\n'
                "}\n"
                "Be strict but fair. Score 7+ means approved."
            )},
            {"role": "user", "content": (
                f"Requirements: {requirements}\n\n"
                f"Code to review:\n{code}"
            )},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


# ══════════════════════════════════════════════════════
# SUPERVISOR AGENT
# ══════════════════════════════════════════════════════

class Supervisor:
    """
    Manager that oversees the write → review → rewrite loop.
    
    Architecture:
      Supervisor assigns task → Writer writes code
      → Reviewer reviews → Supervisor decides:
        → If approved: Done!
        → If rejected: Writer rewrites with feedback
        → If max attempts: Accept best attempt
    
    Java Analogy: Like a CI/CD pipeline with human review —
    PR → Build → Test → Review → Approve/Request Changes → Merge
    """

    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.history = []

    def run(self, task: str) -> dict:
        """Run the supervised code generation loop."""
        print(f"\n  👔 Supervisor: Starting task")
        print(f"  📌 Task: {task}\n")

        best_code = ""
        best_score = 0
        feedback = ""

        for iteration in range(1, self.max_iterations + 1):
            print(f"  {'─'*50}")
            print(f"  🔄 Iteration {iteration}/{self.max_iterations}")

            # Step 1: Writer writes (or rewrites with feedback)
            print(f"  ✍️  Writer: {'Writing' if iteration == 1 else 'Rewriting with feedback'}...")
            code = code_writer(task, feedback)
            print(f"     Generated {len(code.split())} words of code")

            # Step 2: Reviewer reviews
            print(f"  🔍 Reviewer: Analyzing code...")
            review = code_reviewer(code, task)
            score = review.get("score", 0)
            approved = review.get("approved", False)
            feedback = review.get("feedback", "")
            issues = review.get("issues", [])

            print(f"     Score: {score}/10 | Approved: {'✅' if approved else '❌'}")
            if issues:
                for issue in issues[:3]:
                    print(f"     ⚠️  {issue}")

            # Track best attempt
            if score > best_score:
                best_score = score
                best_code = code

            self.history.append({
                "iteration": iteration,
                "score": score,
                "approved": approved,
                "issues_count": len(issues),
            })

            # Step 3: Supervisor decides
            if approved or score >= 7:
                print(f"\n  👔 Supervisor: ✅ Code approved (score: {score}/10)")
                return {
                    "status": "approved",
                    "code": code,
                    "score": score,
                    "iterations": iteration,
                    "history": self.history,
                }

            if iteration < self.max_iterations:
                print(f"  👔 Supervisor: ❌ Sending back for revision")
                print(f"     Feedback: {feedback[:100]}...")

        # Max iterations reached — use best attempt
        print(f"\n  👔 Supervisor: ⚠️ Max iterations reached. Using best attempt (score: {best_score}/10)")
        return {
            "status": "max_iterations_reached",
            "code": best_code,
            "score": best_score,
            "iterations": self.max_iterations,
            "history": self.history,
        }


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  👔 Supervisor Pattern                       ║")
    print("║  Delegate → Review → Revise → Approve        ║")
    print("╚══════════════════════════════════════════════╝")

    supervisor = Supervisor(max_iterations=3)

    task = (
        "Create a Spring Boot REST controller for a UserService with: "
        "GET /users (paginated list), GET /users/{id}, POST /users (with validation), "
        "DELETE /users/{id}. Include proper exception handling with @ControllerAdvice, "
        "and input validation with Jakarta Validation annotations."
    )

    result = supervisor.run(task)

    print(f"\n  {'═'*55}")
    print(f"  📊 RESULT:")
    print(f"  {'═'*55}")
    print(f"  Status: {result['status']}")
    print(f"  Score: {result['score']}/10")
    print(f"  Iterations: {result['iterations']}")

    print(f"\n  📜 Iteration History:")
    for h in result["history"]:
        icon = "✅" if h["approved"] else "❌"
        print(f"    Round {h['iteration']}: Score {h['score']}/10 {icon} ({h['issues_count']} issues)")

    print(f"\n  💻 Generated Code:")
    print(f"  {'─'*55}")
    # Show first 20 lines
    for line in result["code"].split("\n")[:25]:
        print(f"  {line}")
    print(f"  ...")

    print(f"\n  ✅ Supervisor Pattern takeaways:")
    print(f"     • Writer + Reviewer = iterative improvement")
    print(f"     • Supervisor controls the loop (max iterations)")
    print(f"     • Quality improves with each iteration")
    print(f"     • Like PR review: Submit → Review → Revise → Merge\n")


if __name__ == "__main__":
    main()
