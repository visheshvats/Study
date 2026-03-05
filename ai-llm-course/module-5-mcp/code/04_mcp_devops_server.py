"""
MODULE 5 — PROJECT: DevOps MCP Server
========================================
A production-style MCP server for DevOps operations.

This is the capstone project for Module 5 — a realistic MCP server
that a DevOps team could actually deploy for AI-assisted operations.

FEATURES:
  🔍 Log search and analysis
  📊 Service health monitoring
  🚀 Deployment status tracking
  📋 Incident management
  📈 Performance metrics
  📄 Configuration resources
  💬 DevOps prompt templates

SETUP:
  pip install mcp

RUN:
  npx @modelcontextprotocol/inspector python 04_mcp_devops_server.py

CONFIGURE IN CLAUDE DESKTOP:
  {
    "mcpServers": {
      "devops": {
        "command": "python",
        "args": ["/full/path/to/04_mcp_devops_server.py"]
      }
    }
  }

JAVA ANALOGY:
  This is like building a Spring Boot REST microservice,
  but instead of HTTP endpoints, we expose MCP tools/resources
  that AI applications can discover and use.
"""

from mcp.server.fastmcp import FastMCP
import json
import random
from datetime import datetime, timedelta

mcp = FastMCP(
    name="devops-assistant",
    version="1.0.0",
)


# ══════════════════════════════════════════════════════
# SIMULATED INFRASTRUCTURE DATA
# ══════════════════════════════════════════════════════

class InfraData:
    """Simulates real infrastructure data sources."""

    SERVICES = {
        "api-gateway": {"status": "healthy", "cpu": 34, "memory": 55, "rps": 1200, "p99_ms": 45, "version": "2.1.0", "replicas": 3},
        "user-service": {"status": "healthy", "cpu": 42, "memory": 61, "rps": 800, "p99_ms": 120, "version": "3.4.1", "replicas": 2},
        "order-service": {"status": "degraded", "cpu": 87, "memory": 78, "rps": 450, "p99_ms": 890, "version": "2.8.0", "replicas": 2},
        "payment-service": {"status": "healthy", "cpu": 28, "memory": 45, "rps": 200, "p99_ms": 230, "version": "4.0.2", "replicas": 3},
        "notification-service": {"status": "healthy", "cpu": 15, "memory": 32, "rps": 150, "p99_ms": 50, "version": "1.5.0", "replicas": 1},
        "search-service": {"status": "healthy", "cpu": 55, "memory": 70, "rps": 300, "p99_ms": 180, "version": "2.2.0", "replicas": 2},
    }

    LOGS = [
        {"timestamp": "2024-03-15T14:23:01Z", "service": "order-service", "level": "ERROR", "message": "Connection pool exhausted: HikariPool-1 - Connection is not available, request timed out after 30000ms"},
        {"timestamp": "2024-03-15T14:23:15Z", "service": "order-service", "level": "ERROR", "message": "Failed to process order #12847: org.springframework.dao.DataAccessResourceFailureException"},
        {"timestamp": "2024-03-15T14:23:32Z", "service": "order-service", "level": "WARN", "message": "Circuit breaker 'paymentService' is OPEN, falling back to queued processing"},
        {"timestamp": "2024-03-15T14:24:01Z", "service": "api-gateway", "level": "WARN", "message": "Upstream service 'order-service' returning 503, applying rate limiting"},
        {"timestamp": "2024-03-15T14:24:05Z", "service": "payment-service", "level": "INFO", "message": "Payment processed successfully for order #12845, amount: $149.99"},
        {"timestamp": "2024-03-15T14:24:10Z", "service": "user-service", "level": "INFO", "message": "User session created for user_id=38291, JWT expires in 3600s"},
        {"timestamp": "2024-03-15T14:24:22Z", "service": "notification-service", "level": "INFO", "message": "Email sent to user_38291@example.com, template: order_confirmation"},
        {"timestamp": "2024-03-15T14:25:01Z", "service": "order-service", "level": "ERROR", "message": "Transaction rollback: Could not commit JPA transaction; nested exception: connection timeout"},
        {"timestamp": "2024-03-15T14:25:30Z", "service": "search-service", "level": "INFO", "message": "Elasticsearch reindex completed: 15,234 documents in 4.2s"},
    ]

    DEPLOYMENTS = [
        {"service": "payment-service", "version": "4.0.2", "status": "success", "deployed_at": "2024-03-15T10:00:00Z", "deployed_by": "alice", "environment": "production"},
        {"service": "user-service", "version": "3.4.1", "status": "success", "deployed_at": "2024-03-14T14:00:00Z", "deployed_by": "bob", "environment": "production"},
        {"service": "order-service", "version": "2.8.0", "status": "success", "deployed_at": "2024-03-13T16:00:00Z", "deployed_by": "carol", "environment": "production"},
        {"service": "api-gateway", "version": "2.1.0", "status": "rolled_back", "deployed_at": "2024-03-12T11:00:00Z", "deployed_by": "alice", "environment": "production"},
    ]

    INCIDENTS = []

    @classmethod
    def create_incident(cls, **kwargs):
        incident_id = f"INC-{random.randint(1000, 9999)}"
        incident = {"id": incident_id, "created_at": datetime.now().isoformat(), "status": "open", **kwargs}
        cls.INCIDENTS.append(incident)
        return incident


# ══════════════════════════════════════════════════════
# TOOLS — DevOps Operations
# ══════════════════════════════════════════════════════

@mcp.tool()
def search_logs(query: str, service: str = "", level: str = "", minutes_ago: int = 60) -> str:
    """Search application logs by keyword, service name, and severity level.
    
    Args:
        query: Search keyword to find in log messages
        service: Filter by service name (optional, e.g., 'order-service')
        level: Filter by log level (DEBUG, INFO, WARN, ERROR) (optional)
        minutes_ago: How many minutes back to search (default: 60)
    """
    results = []
    for log in InfraData.LOGS:
        if query.lower() in log["message"].lower():
            if service and service.lower() not in log["service"].lower():
                continue
            if level and level.upper() != log["level"]:
                continue
            results.append(log)

    return json.dumps({
        "query": query,
        "filters": {"service": service or "all", "level": level or "all", "minutes": minutes_ago},
        "count": len(results),
        "logs": results,
    })


@mcp.tool()
def check_service(service_name: str) -> str:
    """Get detailed health status of a specific service including CPU, memory, latency, and replica count.
    
    Args:
        service_name: Name of the service (e.g., 'order-service', 'api-gateway')
    """
    service = InfraData.SERVICES.get(service_name)
    if not service:
        return json.dumps({"error": f"Service '{service_name}' not found", "available": list(InfraData.SERVICES.keys())})

    alerts = []
    if service["cpu"] > 80:
        alerts.append(f"⚠️ HIGH CPU: {service['cpu']}% (threshold: 80%)")
    if service["memory"] > 75:
        alerts.append(f"⚠️ HIGH MEMORY: {service['memory']}% (threshold: 75%)")
    if service["p99_ms"] > 500:
        alerts.append(f"⚠️ HIGH LATENCY: p99={service['p99_ms']}ms (threshold: 500ms)")

    return json.dumps({
        "service": service_name,
        **service,
        "alerts": alerts,
        "checked_at": datetime.now().isoformat(),
    })


@mcp.tool()
def check_all_services() -> str:
    """Get a quick health overview of all services. Returns status, CPU, and any alerts."""
    overview = []
    for name, info in InfraData.SERVICES.items():
        status_icon = "🟢" if info["status"] == "healthy" else "🟡" if info["status"] == "degraded" else "🔴"
        alerts = []
        if info["cpu"] > 80:
            alerts.append("HIGH_CPU")
        if info["p99_ms"] > 500:
            alerts.append("HIGH_LATENCY")
        overview.append({
            "service": name,
            "status": f"{status_icon} {info['status']}",
            "cpu": f"{info['cpu']}%",
            "p99": f"{info['p99_ms']}ms",
            "alerts": alerts or ["none"],
        })
    return json.dumps({"services": overview, "total": len(overview), "checked_at": datetime.now().isoformat()})


@mcp.tool()
def get_recent_deployments(count: int = 5) -> str:
    """Get the most recent deployments with their status.
    
    Args:
        count: Number of recent deployments to show (default: 5)
    """
    deployments = InfraData.DEPLOYMENTS[:count]
    return json.dumps({"deployments": deployments, "count": len(deployments)})


@mcp.tool()
def create_incident_report(title: str, severity: str, affected_service: str, description: str, suspected_cause: str = "") -> str:
    """Create an incident report for a production issue.
    
    Args:
        title: Short, descriptive incident title
        severity: P0 (critical), P1 (high), P2 (medium), P3 (low)
        affected_service: Name of the affected service
        description: Detailed description of the incident and impact
        suspected_cause: Suspected root cause if known (optional)
    """
    if severity not in ["P0", "P1", "P2", "P3"]:
        return json.dumps({"error": "Severity must be P0, P1, P2, or P3"})

    incident = InfraData.create_incident(
        title=title,
        severity=severity,
        affected_service=affected_service,
        description=description,
        suspected_cause=suspected_cause,
    )
    return json.dumps(incident)


@mcp.tool()
def scale_service(service_name: str, replicas: int) -> str:
    """Scale a service to a specific number of replicas.
    
    ⚠️ This modifies infrastructure. Use with caution.
    
    Args:
        service_name: Name of the service to scale
        replicas: Desired number of replicas (1-10)
    """
    if service_name not in InfraData.SERVICES:
        return json.dumps({"error": f"Service '{service_name}' not found"})
    if not 1 <= replicas <= 10:
        return json.dumps({"error": "Replicas must be between 1 and 10"})

    old_replicas = InfraData.SERVICES[service_name]["replicas"]
    InfraData.SERVICES[service_name]["replicas"] = replicas

    return json.dumps({
        "service": service_name,
        "action": "scale",
        "old_replicas": old_replicas,
        "new_replicas": replicas,
        "status": "scaling_in_progress",
        "estimated_time": "30 seconds",
    })


# ══════════════════════════════════════════════════════
# RESOURCES — Read-only Data
# ══════════════════════════════════════════════════════

@mcp.resource("infra://services/dashboard")
def services_dashboard() -> str:
    """Complete infrastructure dashboard with all service metrics."""
    lines = ["# Infrastructure Dashboard", f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]

    for name, info in InfraData.SERVICES.items():
        icon = "🟢" if info["status"] == "healthy" else "🟡" if info["status"] == "degraded" else "🔴"
        lines.append(f"## {icon} {name} v{info['version']}")
        lines.append(f"- Status: {info['status']} | Replicas: {info['replicas']}")
        lines.append(f"- CPU: {info['cpu']}% | Memory: {info['memory']}%")
        lines.append(f"- RPS: {info['rps']} | P99: {info['p99_ms']}ms")
        lines.append("")

    return "\n".join(lines)


@mcp.resource("infra://runbook/high-cpu")
def runbook_high_cpu() -> str:
    """Runbook for handling high CPU alerts."""
    return """# Runbook: High CPU Alert

## Symptoms
- CPU usage > 80% sustained
- Increased response latency
- Possible request timeouts

## Diagnosis Steps
1. Check if it's a traffic spike: `check_service <service>`
2. Search for error loops: `search_logs "exception" --service <service>`
3. Check recent deployments: `get_recent_deployments`

## Mitigation
1. **If traffic spike**: Scale horizontally: `scale_service <service> <replicas+2>`
2. **If error loop**: Check logs for the root cause, may need rollback
3. **If resource leak**: Restart pods (schedule rolling restart)
4. **If sustained load**: Optimize code or add caching

## Escalation
- If not resolved in 15 min → Page team lead
- If P0 → Immediately create incident report
"""


@mcp.resource("infra://runbook/connection-pool")
def runbook_connection_pool() -> str:
    """Runbook for database connection pool issues."""
    return """# Runbook: Connection Pool Exhaustion

## Symptoms
- "Connection is not available" errors in logs
- HikariCP pool timeout exceptions
- Service returning 503 errors

## Diagnosis
1. Check HikariCP metrics: active, idle, pending connections
2. Look for long-running queries: Check pg_stat_activity
3. Check for connection leaks: Look for unclosed connections

## Mitigation
1. **Immediate**: Increase pool size (max 20 for typical service)
2. **If leak**: Restart service to release connections
3. **If slow queries**: Add missing indexes, optimize queries
4. **Long-term**: Add connection pool monitoring to Grafana

## Configuration
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 10000
      idle-timeout: 300000
```
"""


# ══════════════════════════════════════════════════════
# PROMPTS — Templates
# ══════════════════════════════════════════════════════

@mcp.prompt()
def investigate_incident(service_name: str, symptom: str) -> str:
    """Investigate a production incident step by step.
    
    Args:
        service_name: The service experiencing issues
        symptom: What's happening (e.g., 'high latency', '503 errors')
    """
    return f"""You are a senior SRE investigating a production incident.

Service: {service_name}
Symptom: {symptom}

Follow this investigation procedure:
1. First, check the service health using check_service('{service_name}')
2. Search for recent error logs using search_logs with the service filter
3. Check recent deployments using get_recent_deployments
4. Read the relevant runbook if available

After gathering data, provide:
- Root cause analysis (top 3 possibilities)
- Immediate action plan
- Whether to create an incident report (and at what severity)
- Long-term prevention recommendations"""


@mcp.prompt()
def daily_standup_report() -> str:
    """Generate a daily infrastructure standup report."""
    return """You are a DevOps engineer preparing the daily infrastructure report.

Using the available tools and resources:
1. Check all services health (check_all_services)
2. Review recent deployments (get_recent_deployments)
3. Look for any ERROR logs in the last 60 minutes

Generate a concise standup report with:
- Overall infrastructure status (green/yellow/red)
- Any services needing attention
- Recent deployments and their status
- Action items for today"""


# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    mcp.run()
