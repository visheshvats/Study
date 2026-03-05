"""
MODULE 5 — Example 3: MCP Server with Tools + Resources + Prompts
===================================================================
A more complete MCP server that demonstrates all 3 primitives.

This simulates a "Team Dashboard" MCP server that gives AI
access to team metrics, project data, and common prompts.

SETUP:
  pip install mcp

RUN:
  npx @modelcontextprotocol/inspector python 03_mcp_server_resources.py
"""

from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime, timedelta
import random

mcp = FastMCP(
    name="team-dashboard",
    version="1.0.0",
)


# ══════════════════════════════════════════════════════
# SIMULATED DATA (would come from real APIs in production)
# ══════════════════════════════════════════════════════

TEAM_MEMBERS = {
    "alice": {"name": "Alice Chen", "role": "Senior Backend", "sprint_points": 13, "prs_open": 2},
    "bob": {"name": "Bob Kumar", "role": "DevOps Engineer", "sprint_points": 8, "prs_open": 1},
    "carol": {"name": "Carol Smith", "role": "Frontend Lead", "sprint_points": 11, "prs_open": 3},
    "dave": {"name": "Dave Lee", "role": "Junior Backend", "sprint_points": 5, "prs_open": 1},
}

SERVICES = {
    "user-service": {"status": "healthy", "cpu": 45, "memory": 62, "uptime": "14d 3h", "version": "2.3.1"},
    "order-service": {"status": "healthy", "cpu": 38, "memory": 55, "uptime": "14d 3h", "version": "1.8.0"},
    "payment-service": {"status": "degraded", "cpu": 89, "memory": 78, "uptime": "2h 15m", "version": "3.1.2"},
    "notification-service": {"status": "healthy", "cpu": 12, "memory": 30, "uptime": "14d 3h", "version": "1.2.0"},
}


# ══════════════════════════════════════════════════════
# TOOLS — Actions the AI can take
# ══════════════════════════════════════════════════════

@mcp.tool()
def check_service_health(service_name: str) -> str:
    """Check the health status of a specific service.
    
    Returns CPU usage, memory usage, uptime, and version.
    
    Args:
        service_name: Name of the service (e.g., 'user-service', 'payment-service')
    """
    service = SERVICES.get(service_name)
    if not service:
        available = list(SERVICES.keys())
        return json.dumps({"error": f"Service '{service_name}' not found", "available": available})
    
    return json.dumps({
        "service": service_name,
        **service,
        "checked_at": datetime.now().isoformat(),
    })


@mcp.tool()
def get_team_member_stats(member_id: str) -> str:
    """Get sprint statistics for a team member.
    
    Args:
        member_id: Team member ID (e.g., 'alice', 'bob')
    """
    member = TEAM_MEMBERS.get(member_id)
    if not member:
        available = list(TEAM_MEMBERS.keys())
        return json.dumps({"error": f"Member '{member_id}' not found", "available": available})

    return json.dumps({
        "member_id": member_id,
        **member,
    })


@mcp.tool()
def create_incident(title: str, severity: str, affected_service: str, description: str) -> str:
    """Create an incident report for a service issue.
    
    Args:
        title: Short incident title
        severity: Severity level (P0, P1, P2, P3)
        affected_service: Name of the affected service
        description: Detailed description of the incident
    """
    incident = {
        "id": f"INC-{random.randint(1000, 9999)}",
        "title": title,
        "severity": severity,
        "affected_service": affected_service,
        "description": description,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "assigned_to": "on-call team",
    }
    return json.dumps(incident)


@mcp.tool()
def get_sprint_summary() -> str:
    """Get the current sprint summary with team velocity and progress."""
    total_points = sum(m["sprint_points"] for m in TEAM_MEMBERS.values())
    total_prs = sum(m["prs_open"] for m in TEAM_MEMBERS.values())
    
    return json.dumps({
        "sprint": "Sprint 24",
        "days_remaining": 5,
        "total_story_points": total_points,
        "completed_points": int(total_points * 0.65),
        "open_prs": total_prs,
        "team_size": len(TEAM_MEMBERS),
        "on_track": total_points * 0.65 >= total_points * 0.5,
    })


# ══════════════════════════════════════════════════════
# RESOURCES — Read-only data
# ══════════════════════════════════════════════════════

@mcp.resource("dashboard://services/overview")
def services_overview() -> str:
    """Overview of all service health statuses."""
    lines = ["# Service Health Dashboard\n"]
    for name, info in SERVICES.items():
        icon = "🟢" if info["status"] == "healthy" else "🟡" if info["status"] == "degraded" else "🔴"
        lines.append(f"{icon} **{name}** v{info['version']} — CPU: {info['cpu']}% | RAM: {info['memory']}% | Up: {info['uptime']}")
    return "\n".join(lines)


@mcp.resource("dashboard://team/overview")
def team_overview() -> str:
    """Overview of the team and sprint progress."""
    lines = ["# Team Overview — Sprint 24\n"]
    for mid, info in TEAM_MEMBERS.items():
        lines.append(f"- **{info['name']}** ({info['role']}) — {info['sprint_points']} pts | {info['prs_open']} open PRs")
    
    total = sum(m["sprint_points"] for m in TEAM_MEMBERS.values())
    lines.append(f"\n**Total velocity:** {total} story points")
    return "\n".join(lines)


@mcp.resource("config://oncall-schedule")
def oncall_schedule() -> str:
    """Current on-call rotation schedule."""
    today = datetime.now()
    return json.dumps({
        "current_week": {
            "primary": "alice",
            "secondary": "bob",
            "start": (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d"),
            "end": (today + timedelta(days=6 - today.weekday())).strftime("%Y-%m-%d"),
        },
        "next_week": {
            "primary": "carol",
            "secondary": "dave",
        },
        "escalation": ["On-call → Team Lead (Alice) → Engineering Manager → VP"],
    })


# ══════════════════════════════════════════════════════
# PROMPTS — Pre-built templates
# ══════════════════════════════════════════════════════

@mcp.prompt()
def incident_analysis(service_name: str, error_message: str) -> str:
    """Analyze an incident and suggest root cause and fix.
    
    Args:
        service_name: The affected service
        error_message: The error or symptom observed
    """
    return f"""You are a senior SRE analyzing a production incident.

Service: {service_name}
Error: {error_message}

Please provide:
1. Likely root cause (top 3 possibilities)
2. Immediate mitigation steps
3. Long-term fix recommendations
4. What monitoring should be added to catch this earlier

Base your analysis on common patterns for this type of service and error."""


@mcp.prompt()
def sprint_retro() -> str:
    """Generate talking points for a sprint retrospective."""
    return """You are a Scrum Master preparing for a sprint retrospective.

Based on the team's sprint data and service health data available through the dashboard, 
please prepare:

1. **What went well** — services that stayed healthy, work completed on time
2. **What could improve** — any degraded services, blockers, velocity concerns
3. **Action items** — specific, measurable improvements for next sprint

Use the team overview and service health data to support your points.
Ask the team to use the check_service_health and get_sprint_summary tools for data."""


# ══════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run()
