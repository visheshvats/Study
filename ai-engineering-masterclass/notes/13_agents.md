# Topic 13: Agents

> **Java Analogy:** An AI agent is like a `ScheduledExecutorService` running a `while(true)` loop: observe state → reason (LLM call) → pick a tool → execute it → observe result → repeat. Think of it as a self-driving `CommandLineRunner` that calls `@Service` methods based on LLM-driven decisions.

---

## What This Is (Plain English)

An agent is an LLM wrapped in a loop that can autonomously call tools, observe results, and decide what to do next — until a goal is achieved. Instead of a single prompt→response interaction, the agent takes multi-step actions: "Search the database, then call the API, then format the report, then email it." It's the difference between a calculator (one input → one output) and a project manager (goal → plan → execute → iterate).

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Agent** | A `Runnable` with an LLM brain inside a `while(!done)` loop |
| **ReAct loop** | `while(true) { think(); act(); observe(); }` |
| **Tool registry** | `Map<String, Function<JsonNode, String>>` — named functions the agent can call |
| **Tool call** | The LLM outputs structured JSON: `{"tool": "query_db", "args": {"sql": "SELECT..."}}` — like an RPC call |
| **Observation** | The tool result fed back as context — like a callback response |
| **Memory** | Short-term: conversation history in context window. Long-term: Redis/vector DB for cross-session state. |
| **Orchestrator** | The control loop that manages the agent's lifecycle — like a `TaskScheduler` |
| **Max iterations** | `for (int i = 0; i < MAX_STEPS; i++)` — safety bound to prevent infinite loops |

---

## Agent Architecture (ReAct Pattern)

```java
public class AgentOrchestrator {
    private final ChatLanguageModel llm;
    private final Map<String, Tool> tools;
    private static final int MAX_ITERATIONS = 10;

    public String run(String goal) {
        List<Message> history = new ArrayList<>();
        history.add(systemMessage(goal, tools.values()));

        for (int i = 0; i < MAX_ITERATIONS; i++) {
            // REASON: Ask LLM what to do next
            ChatResponse response = llm.chat(history);

            if (response.hasToolCalls()) {
                // ACT: Execute the chosen tool
                for (ToolCall call : response.toolCalls()) {
                    Tool tool = tools.get(call.name());
                    String result = tool.execute(call.arguments());

                    // OBSERVE: Feed result back
                    history.add(toolResultMessage(call.name(), result));
                }
            } else {
                // DONE: LLM produced a final answer
                return response.text();
            }
        }
        return "Agent exceeded maximum iterations.";
    }
}
```

---

## Code Bridge — Full Agent with Spring AI

```java
@Service
public class BankingAgent {

    @Bean
    public ChatClient agentClient(ChatClient.Builder builder) {
        return builder
            .defaultSystem("""
                You are a banking support agent. You have access to tools
                to look up account info, check transactions, and initiate refunds.
                Always verify the account number before taking action.
                Never initiate a refund without explicit user confirmation.
                """)
            .defaultTools(
                new AccountLookupTool(accountService),
                new TransactionHistoryTool(txnService),
                new RefundTool(refundService)
            )
            .build();
    }
}

// Tool definition using Spring AI
@Component
public class AccountLookupTool implements Function<AccountRequest, AccountResponse> {

    @Override
    @Description("Look up bank account details by account number")
    public AccountResponse apply(AccountRequest request) {
        return accountService.findByAccountNumber(request.accountNumber());
    }

    record AccountRequest(
        @Description("10-digit bank account number") String accountNumber
    ) {}
    record AccountResponse(String name, double balance, String status) {}
}
```

### Multi-Agent Pattern

```java
@Service
public class MultiAgentRouter {
    private final Map<String, Agent> agents = Map.of(
        "payments", new PaymentsAgent(),
        "loans", new LoansAgent(),
        "investments", new InvestmentsAgent()
    );

    public String handleQuery(String query) {
        // Router agent classifies the query
        String department = routerLlm.generate(
            "Classify this query into: payments, loans, investments. Query: " + query
        ).trim().toLowerCase();

        // Delegate to specialist agent
        Agent specialist = agents.getOrDefault(department, agents.get("payments"));
        return specialist.run(query);
    }
}
```

---

## Production Safety Checklist

```java
public class AgentSafety {
    // 1. Iteration limit
    private static final int MAX_STEPS = 10;

    // 2. Token/cost budget
    private static final int MAX_TOKENS = 50_000;
    private int tokensUsed = 0;

    // 3. Timeout
    private static final Duration TIMEOUT = Duration.ofSeconds(60);

    // 4. Duplicate detection
    private final Set<String> previousActions = new HashSet<>();

    // 5. Human-in-the-loop for sensitive actions
    private static final Set<String> SENSITIVE_TOOLS = Set.of("initiate_refund", "delete_account");

    public boolean shouldContinue(ToolCall action) {
        if (tokensUsed >= MAX_TOKENS) return false;
        String actionKey = action.name() + ":" + action.arguments();
        if (previousActions.contains(actionKey)) return false;  // Duplicate!
        previousActions.add(actionKey);
        return true;
    }

    public boolean requiresApproval(ToolCall action) {
        return SENSITIVE_TOOLS.contains(action.name());
    }
}
```

---

## Interview-Ready Summary

- An agent is an LLM in a reason→act→observe loop that autonomously calls tools to achieve a goal.
- ReAct pattern: Think (LLM reasoning) → Act (tool execution) → Observe (result injection) → Repeat.
- Tools are registered as named functions with JSON Schema inputs — the LLM decides when to call them.
- Safety: max iterations, token budgets, timeouts, duplicate detection, human approval gates.
- In Java: Spring AI `ChatClient` with `@Tool` functions or LangChain4j `AiServices`.
- Multi-agent: router agent classifies queries, specialist agents handle domain tasks.
- Always log every step for debugging — agent failures are hard to reproduce.
