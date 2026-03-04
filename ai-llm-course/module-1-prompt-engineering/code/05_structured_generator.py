"""
MODULE 1 — PROJECT: Structured Response Generator
====================================================
A production-grade tool that converts natural language requests
into structured, validated outputs.

USE CASE:
  Your company gets unstructured support tickets via email.
  This tool extracts structured data, classifies priority,
  routes to the right team, and generates a response draft.

  This is a REAL pattern used in production at companies like
  Zendesk, Freshdesk, and Intercom.

SETUP:
  pip install openai python-dotenv rich
  OPENAI_API_KEY in .env

RUN:
  python 05_structured_generator.py

CONCEPTS DEMONSTRATED:
  1. System prompt design
  2. Few-shot prompting
  3. Structured JSON output
  4. Input/output validation
  5. Multi-step pipeline (decomposition)
  6. Temperature tuning per task
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ──────────────────────────────────────────────────────
# STEP 1: Extract structured data from ticket
# ──────────────────────────────────────────────────────

def extract_ticket_data(raw_ticket: str) -> dict:
    """
    Extract structured fields from an unstructured support ticket.
    
    Uses: System prompt + JSON response_format + Low temperature (factual task)
    
    Java Analogy: Like a DTO mapper that converts unstructured
    request body text into a validated TicketDTO.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """You extract structured data from support tickets.

Return JSON with exactly these fields:
{
  "customer_name": string or null,
  "customer_email": string or null,
  "product": string or null,
  "issue_summary": string (1 sentence),
  "issue_details": string (key technical details),
  "error_messages": [string] (any error messages mentioned),
  "steps_taken": [string] (what the customer already tried),
  "environment": {
    "os": string or null,
    "browser": string or null,
    "version": string or null
  },
  "urgency_indicators": [string] (words suggesting urgency)
}

If a field cannot be determined from the ticket, use null."""},
            {"role": "user", "content": raw_ticket}
        ],
        temperature=0,  # Factual extraction → deterministic
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


# ──────────────────────────────────────────────────────
# STEP 2: Classify priority and route
# ──────────────────────────────────────────────────────

def classify_and_route(ticket_data: dict) -> dict:
    """
    Classify the ticket priority and determine routing.
    
    Uses: Few-shot prompting for consistent classification
    
    Java Analogy: Like a @Service with classification logic,
    but instead of if-else rules, we use LLM reasoning.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """You classify support tickets and route them.

Return JSON:
{
  "priority": "P0_CRITICAL" | "P1_HIGH" | "P2_MEDIUM" | "P3_LOW",
  "category": "BUG" | "FEATURE_REQUEST" | "QUESTION" | "ACCOUNT" | "BILLING",
  "team": "engineering" | "product" | "billing" | "account_management",
  "estimated_response_time": string,
  "requires_escalation": boolean,
  "reasoning": string (why this classification)
}

Classification rules:
- P0: System down, data loss, security breach, >100 users affected
- P1: Major feature broken, workaround exists, revenue impact
- P2: Minor bug, cosmetic issue, single user affected
- P3: Question, feature request, documentation"""},
            # Few-shot example 1
            {"role": "user", "content": json.dumps({
                "issue_summary": "Payment processing completely down",
                "urgency_indicators": ["URGENT", "all customers", "revenue loss"],
                "error_messages": ["500 Internal Server Error"]
            })},
            {"role": "assistant", "content": json.dumps({
                "priority": "P0_CRITICAL",
                "category": "BUG",
                "team": "engineering",
                "estimated_response_time": "15 minutes",
                "requires_escalation": True,
                "reasoning": "Payment system down affects all customers and revenue"
            })},
            # Few-shot example 2
            {"role": "user", "content": json.dumps({
                "issue_summary": "Button color looks wrong on dark mode",
                "urgency_indicators": [],
                "error_messages": []
            })},
            {"role": "assistant", "content": json.dumps({
                "priority": "P3_LOW",
                "category": "BUG",
                "team": "engineering",
                "estimated_response_time": "48 hours",
                "requires_escalation": False,
                "reasoning": "Cosmetic issue, no functional impact"
            })},
            # Actual ticket
            {"role": "user", "content": json.dumps({
                "issue_summary": ticket_data.get("issue_summary"),
                "urgency_indicators": ticket_data.get("urgency_indicators", []),
                "error_messages": ticket_data.get("error_messages", []),
            })},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


# ──────────────────────────────────────────────────────
# STEP 3: Generate response draft
# ──────────────────────────────────────────────────────

def generate_response(ticket_data: dict, classification: dict) -> str:
    """
    Generate a professional response draft.
    
    Uses: Role prompting + structured context + moderate temperature
    
    Java Analogy: Like a template engine (Thymeleaf) but dynamic —
    the LLM generates contextual content instead of filling templates.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"""You are a professional customer support agent.

Write a response email for a {classification['priority']} support ticket.

TONE RULES:
- P0/P1: Urgent, empathetic, action-oriented. Acknowledge impact immediately.
- P2: Professional, helpful, solution-focused.
- P3: Friendly, informative, thorough.

STRUCTURE:
1. Greeting (use customer name if available)
2. Acknowledge the issue (show you understand)
3. What you're doing about it
4. Next steps / ETA
5. Sign-off

Keep it concise. Max 150 words."""},
            {"role": "user", "content": (
                f"Customer: {ticket_data.get('customer_name', 'Customer')}\n"
                f"Issue: {ticket_data.get('issue_summary')}\n"
                f"Details: {ticket_data.get('issue_details')}\n"
                f"Priority: {classification['priority']}\n"
                f"Team: {classification['team']}\n"
                f"ETA: {classification['estimated_response_time']}"
            )}
        ],
        temperature=0.5,  # Some creativity for natural writing, but not too much
    )

    return response.choices[0].message.content


# ──────────────────────────────────────────────────────
# MAIN PIPELINE
# ──────────────────────────────────────────────────────

def process_ticket(raw_ticket: str) -> dict:
    """
    Full pipeline: Raw ticket → Structured data → Classification → Response
    
    Pipeline architecture:
    
    Raw Ticket Text
         │
         ▼
    ┌──────────────┐
    │  1. EXTRACT   │  (temperature=0, JSON output)
    │  Structured   │
    │  data         │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  2. CLASSIFY  │  (temperature=0, few-shot, JSON output)
    │  Priority +   │
    │  routing      │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  3. GENERATE  │  (temperature=0.5, role prompting)
    │  Response     │
    │  draft        │
    └──────┬───────┘
           │
           ▼
    Final Result (all combined)
    """
    print("\n  📨 Processing ticket...")
    print("  " + "─" * 50)

    # Step 1: Extract
    print("  Step 1/3: Extracting structured data...")
    ticket_data = extract_ticket_data(raw_ticket)
    print(f"    ✅ Found: {ticket_data.get('issue_summary', 'N/A')}")

    # Step 2: Classify
    print("  Step 2/3: Classifying priority and routing...")
    classification = classify_and_route(ticket_data)
    print(f"    ✅ Priority: {classification.get('priority')} → {classification.get('team')}")

    # Step 3: Generate response
    print("  Step 3/3: Generating response draft...")
    response_draft = generate_response(ticket_data, classification)
    print(f"    ✅ Response generated ({len(response_draft)} chars)")

    return {
        "timestamp": datetime.now().isoformat(),
        "raw_ticket": raw_ticket[:200] + "...",
        "extracted_data": ticket_data,
        "classification": classification,
        "response_draft": response_draft,
    }


# ──────────────────────────────────────────────────────
# DEMO
# ──────────────────────────────────────────────────────

def main():
    # Sample support tickets (realistic examples)
    tickets = [
        # Ticket 1: High urgency production issue
        """
        From: sarah.chen@acmecorp.com
        Subject: URGENT - Dashboard not loading for entire team
        
        Hi Support,
        
        Since this morning around 9 AM EST, our entire engineering team (25 people)
        cannot access the analytics dashboard. We get a spinning loader and then
        this error: "Error 503: Service Unavailable - upstream connect error."
        
        We've tried:
        - Clearing browser cache
        - Different browsers (Chrome, Firefox, Safari)
        - Different networks (office and VPN)
        
        This is blocking our sprint review today and we need this resolved ASAP.
        We're on the Enterprise plan.
        
        Environment: Chrome 120, macOS Sonoma, Dashboard v3.2
        
        Thanks,
        Sarah Chen
        VP of Engineering, AcmeCorp
        """,

        # Ticket 2: Low priority question
        """
        Hey there,
        
        Quick question - is there a way to export my dashboard data to CSV? 
        I looked through the docs but couldn't find it. Would be nice to have 
        for our monthly reports.
        
        Thanks!
        Mike
        """,
    ]

    for i, ticket in enumerate(tickets, 1):
        print(f"\n{'='*60}")
        print(f"TICKET #{i}")
        print(f"{'='*60}")

        result = process_ticket(ticket)

        print(f"\n  {'─'*50}")
        print(f"  📊 RESULTS:")
        print(f"  {'─'*50}")
        print(f"  Priority:    {result['classification']['priority']}")
        print(f"  Category:    {result['classification']['category']}")
        print(f"  Team:        {result['classification']['team']}")
        print(f"  ETA:         {result['classification']['estimated_response_time']}")
        print(f"  Escalation:  {result['classification']['requires_escalation']}")
        print(f"  Reasoning:   {result['classification']['reasoning']}")

        print(f"\n  📧 DRAFT RESPONSE:")
        print(f"  {'─'*50}")
        for line in result['response_draft'].split('\n'):
            print(f"  {line}")

        print(f"\n  📋 EXTRACTED DATA:")
        print(f"  {'─'*50}")
        ed = result['extracted_data']
        print(f"  Customer:  {ed.get('customer_name', 'N/A')}")
        print(f"  Email:     {ed.get('customer_email', 'N/A')}")
        print(f"  Product:   {ed.get('product', 'N/A')}")
        print(f"  Summary:   {ed.get('issue_summary', 'N/A')}")
        if ed.get('error_messages'):
            print(f"  Errors:    {', '.join(ed['error_messages'])}")
        if ed.get('steps_taken'):
            print(f"  Tried:     {', '.join(ed['steps_taken'])}")


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════╗")
    print("║  📮 Structured Response Generator            ║")
    print("║  MODULE 1 PROJECT                            ║")
    print("║                                              ║")
    print("║  Pipeline: Extract → Classify → Respond      ║")
    print("╚══════════════════════════════════════════════╝")

    main()

    print("\n✅ Project complete!")
    print("   This 3-step pipeline demonstrates real production patterns:")
    print("   • Structured extraction (temperature=0, JSON mode)")
    print("   • Few-shot classification (consistent categorization)")
    print("   • Role-based generation (contextual responses)")
    print("   • Prompt decomposition (3 simple prompts > 1 complex prompt)\n")
