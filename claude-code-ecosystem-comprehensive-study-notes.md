# Claude Code Ecosystem: Comprehensive Study Notes

## About These Notes

These notes reconstruct the lecture in its original chronological order while correcting obvious caption errors. In particular:

- “cloud,” “claw,” and similar caption variants are normalized to **Claude**.
- “ID” is normalized to **IDE**.
- “wipe coding” is normalized to **vibe coding**.
- File and command names are normalized where their intended form is clear, such as **CLAUDE.md**, **settings.json**, and **MCP**.

The lecture is an engineering course on the **Claude ecosystem**, especially **Claude Code**. It is not a general survey of artificial-intelligence theory. Product names, model names, plan prices, interfaces, and experimental flags are presented as demonstrated in the lecture and may change over time.

---

# 1. Course Scope and Learning Objectives

The course moves beyond introductory prompting and code generation. Its goal is to explain how Claude can participate in real software-development and knowledge-work workflows.

The main objectives are to learn how to:

1. Integrate Claude Code with an existing project.
2. use Claude to understand and maintain a codebase.
3. increase development productivity without removing human oversight.
4. create specialized agents and subagents.
5. manage multiple concurrent Claude sessions with **Agent View**.
6. coordinate collaborating workers with **Agent Teams**.
7. encode repeatable workflows as **skills**.
8. extend Claude through **plugins**, external tools, and MCP integrations.
9. manage project context and persistent instructions through **CLAUDE.md**.
10. use planning, permissions, verification, and human approval to control agentic work.

The instructor assumes only a modest amount of Python knowledge, although many principles apply to other languages and to non-programming tasks.

> **Core course principle:** AI-assisted development is not merely asking a model to produce code. It is the disciplined design of context, permissions, tools, plans, verification steps, and human approval around an agentic system.

## 1.1 Intended Audience

The workflow is presented as useful to:

- software developers joining or maintaining an existing project;
- developers building a product from scratch;
- technical leads reviewing code and coordinating parallel tasks;
- data and business analysts;
- managers handling reports, invoices, spreadsheets, and administrative files;
- non-programmers who need a local AI assistant for structured knowledge work.

## 1.2 Human-in-the-Loop Development

The instructor repeatedly emphasizes that Claude should operate under human supervision.

The human can:

1. approve or reject tool use;
2. interrupt execution;
3. add missing context;
4. revise the requirement;
5. change the selected model;
6. inspect edits before accepting them;
7. request tests or other verification;
8. decide whether a result is ready to commit or ship.

> **Human-in-the-loop (HITL):** A control pattern in which an AI system can propose or perform actions, but a human remains part of the decision and verification loop, especially at consequential steps.

### Key Takeaways

- The course focuses on project-level AI engineering, not isolated prompt tricks.
- Productivity comes from context, reusable workflows, tooling, and controlled autonomy.
- Human review remains necessary because an agent can make mistakes.

---

# 2. The Claude Product Ecosystem

The lecture distinguishes three principal working surfaces.

## 2.1 Claude Chat

**Claude Chat** is the general conversational interface. It supports tasks such as:

- asking and answering questions;
- writing and editing content;
- generating code;
- analyzing text and images;
- searching the web when the relevant capability is available;
- using projects and artifacts to organize richer work.

Concepts learned in Claude Code—good context, explicit requirements, tools, and reusable instructions—also improve work in Chat.

## 2.2 Claude Cowork

> **Claude Cowork:** A desktop-based AI assistant that receives access to a selected local folder and carries out multi-step knowledge-work tasks over the files in that folder.

The instructor demonstrates a folder containing dummy business materials:

- PDF invoices;
- an expense tracker spreadsheet;
- product inventory;
- other administrative files.

Example workflow:

1. Select a local folder.
2. Grant Claude access.
3. Ask Claude to analyze the folder.
4. Let it discover and classify the contents.
5. Ask for invoice details and a report.
6. Respond to clarification questions such as desired report format or which invoices to include.
7. inspect the resulting summary or artifact.

This demonstrates an **agentic workflow** rather than a one-shot answer: the assistant examines files, loads tools, asks for missing decisions, and constructs an output.

Practical uses mentioned include:

- invoice tracking;
- identifying active clients;
- salary and employee administration;
- spreadsheet reporting;
- rapid folder summaries;
- recurring managerial analysis.

Security remains visible through file-access indicators and approval requests. Access should be granted only to folders appropriate for the task.

## 2.3 Claude Code

Claude Code is the central subject of the lecture.

> **Claude Code:** An agentic coding tool that can inspect a codebase, edit files, execute commands, use external tools, and interact with the developer’s environment under configured permissions and human approval.

It can be used from:

- a terminal;
- an IDE such as VS Code or Cursor;
- the Claude desktop application;
- supported browser experiences.

The instructor prefers an IDE plus terminal for development because this makes it easier to:

- see the project tree;
- review file changes;
- observe command execution;
- inspect tests;
- compare generated code with existing code;
- retain close control over the development process.

## 2.4 Projects and Artifacts

The lecture briefly identifies two organizational ideas:

- **Projects** provide a durable body of context for a continuing area of work.
- **Artifacts** present generated outputs—such as a report—in a viewable, reusable form.

These features help turn an unstructured chat into a workspace with persistent context and inspectable deliverables.

## 2.5 Subscription and Version Caveat

The instructor discusses free, Pro, and Max plans and recommends a paid tier for sustained Claude Code and Cowork usage. These statements are demonstrations of the product state at lecture time, not timeless technical facts. Before purchasing, verify current:

- pricing;
- usage limits;
- included products;
- available models;
- regional availability.

### Key Takeaways

- Chat is the broad conversational surface.
- Cowork is oriented toward file-based desktop knowledge work.
- Claude Code is an agentic development environment with project and tool access.
- Product access, prices, and model availability are version-dependent.

---

# 3. First Project-Onboarding Use Case

The instructor opens an existing repository containing LangChain tutorial notebooks, a Python entry point, and dependency files. This represents a common professional scenario: a developer joins a team and inherits a project rather than starting with an empty repository.

## 3.1 Starting Claude in the Project

Open a terminal at the repository root and start Claude:

~~~powershell
claude
~~~

On first entry, Claude may ask whether the user trusts the folder. Trust is consequential because Claude Code can potentially read files and, depending on permission settings, edit them or run commands.

An initial onboarding prompt can be:

~~~text
Analyze this entire project and explain:
1. its purpose,
2. its directory structure,
3. the main execution flow,
4. important dependencies,
5. how to run and test it,
6. any areas that require clarification.
~~~

Claude then gathers context by listing directories, reading documentation, inspecting source files, and possibly requesting permission to execute read-only shell commands.

## 3.2 AI-Assisted Knowledge Transfer

In a conventional team, a new member often waits for a colleague to provide knowledge transfer. Claude can accelerate the first pass by generating:

- a project overview;
- a module map;
- a description of entry points;
- dependency explanations;
- likely development commands;
- questions that should still be taken to the team.

This does not make human domain knowledge unnecessary. Claude can explain what is present in the repository, but it may not know:

- undocumented business rules;
- historical design decisions;
- production incidents;
- informal team conventions;
- pending changes that exist outside the repository.

The correct use is therefore **AI-assisted onboarding**, followed by targeted discussion with maintainers.

## 3.3 Asking Focused Code Questions

After the broad analysis, a developer can narrow the question:

~~~text
Explain main.py function by function. Identify inputs, outputs, side effects,
dependencies, error paths, and how this file participates in the project.
~~~

Focused requests reduce unnecessary scanning and generally produce more precise answers.

### Key Takeaways

- Start Claude from the intended repository root so the project boundary is clear.
- Use broad analysis for orientation, then ask narrow questions about specific files or symbols.
- Treat AI-generated knowledge transfer as a starting map, not a substitute for undocumented team knowledge.

---

# 4. Claude Code as an Agentic System

## 4.1 Agentic Coding Tool

The word **agentic** is central. A normal text model maps an input to an output. An agentic coding tool surrounds the model with:

- project context;
- file-reading and editing tools;
- command execution;
- web or documentation retrieval;
- state and memory;
- permission boundaries;
- an iterative control loop.

The lecture describes Claude Code as an **agentic harness** around the model: the model supplies reasoning and generation, while the harness supplies the environment in which useful software actions can occur.

## 4.2 The Agentic Loop

The loop has three recurring phases:

1. **Gather context**
   - inspect relevant files;
   - read persistent instructions;
   - search the repository;
   - examine command output;
   - ask the user for missing information.

2. **Take action**
   - edit or create a file;
   - execute a command;
   - call a tool;
   - delegate a focused task;
   - produce an explanation or plan.

3. **Verify results**
   - run tests;
   - inspect compiler or runtime output;
   - compare the change with the request;
   - check linting or type errors;
   - ask the human to review.

If verification fails, the loop repeats with the new evidence.

~~~pseudocode
function solve(request, project):
    state <- initialize(request, project)

    while not done(state):
        context <- gather_context(state)
        proposed_action <- reason(request, context, state)
        approved_action <- request_approval_if_needed(proposed_action)

        if approved_action is rejected:
            state <- incorporate_human_feedback(state)
            continue

        observation <- execute(approved_action)
        verification <- verify(request, observation, project)
        state <- update(state, observation, verification)

        if verification is satisfactory:
            return final_result(state)

        state <- incorporate_failure_evidence(state, verification)
~~~

### Formalization

Let $C_t$ be the context at iteration $t$, $A_t$ the selected action, and $O_t$ the resulting observation. The loop can be represented as:

$$
A_t = \pi(R, C_t, S_t)
$$

$$
O_t = E(A_t)
$$

$$
C_{t+1}, S_{t+1} = U(C_t, S_t, O_t, H_t)
$$

where:

- $R$ is the user requirement;
- $\pi$ is the model-plus-agent policy;
- $E$ is the execution environment;
- $S_t$ is current task state;
- $H_t$ is optional human feedback;
- $U$ updates context and state.

Completion occurs when a verification function crosses an acceptance threshold:

$$
V(R, O_t) \ge \tau
$$

This is a study formalization of the lecture’s loop, not an equation claimed as a Claude implementation detail.

## 4.3 Different Requests Exercise Different Parts of the Loop

- A question about a codebase may require mostly context gathering.
- A code modification requires gathering and action.
- A bug fix may cycle repeatedly through all three stages.
- A research request may call web or documentation tools before generating a result.
- A high-risk command may pause at the human-approval boundary.

## 4.4 The Human Is Part of the Loop

The user can intervene at any stage:

- interrupt an incorrect direction;
- add missing requirements;
- correct a false assumption;
- deny a command;
- change tools or models;
- demand stronger verification.

A good workflow does not wait until the final answer to correct the agent. Early intervention prevents incorrect assumptions from propagating into many edits.

### Key Takeaways

- Claude Code combines an LLM with tools, context, execution, memory, and controls.
- Its core operational pattern is gather context → act → verify → repeat.
- Errors become new observations that can guide the next iteration.
- Human feedback is an input to the loop, not merely a final quality check.

---

# 5. Installation, Authentication, and Security

## 5.1 Installation

The lecture directs learners to the official Claude Code documentation and to select the command appropriate to their platform:

- macOS;
- Linux;
- Windows Subsystem for Linux;
- Windows PowerShell;
- Windows Command Prompt.

Because installation commands change, the notes do not preserve a possibly stale captioned command. The durable process is:

1. consult the current official documentation;
2. use the command for the correct shell and operating system;
3. confirm that the **claude** command is available;
4. start it from a trusted project directory.

## 5.2 Initial Login

The demonstrated first-run sequence is:

1. run **claude**;
2. select a terminal theme;
3. select an eligible login method or organization plan;
4. complete browser-based authorization;
5. return to the terminal;
6. accept or adjust recommended terminal settings;
7. confirm whether the current project folder is trusted.

## 5.3 Security Warnings

The lecture surfaces three important risks.

### Model Error

Claude can produce incorrect code, misunderstand a requirement, or make an unsuitable edit. Review remains required.

### Command Execution

A command can alter the project, expose information, or affect the system. Permission prompts should be treated as genuine security decisions rather than clicked through automatically.

### Prompt Injection

> **Prompt injection:** Malicious or misleading instructions embedded in data that an AI system reads, designed to redirect the system away from the user’s intended policy or task.

A repository, webpage, document, issue, or dependency note could contain untrusted instructions. Therefore:

- use Claude only with code and files appropriate to the task;
- inspect sensitive commands;
- use least-privilege tool access;
- do not expose secrets unnecessarily;
- distinguish repository content from trusted user instructions.

## 5.4 Trust Boundary

The selected project folder is a practical trust boundary. Before granting access, ask:

1. Does the folder contain credentials or personal data?
2. Is every file from a trusted source?
3. Does the task require write access?
4. Does it require network access?
5. Can the work be completed with read-only tools?

### Key Takeaways

- Use current official installation instructions for the actual platform.
- Authentication links the CLI to the user’s eligible Claude account.
- Folder trust, tool permissions, and command approval are security controls.
- Grant only the minimum access required for the task.

---

# 6. Models, Modes, Tools, and Sessions

## 6.1 Model Selection

The lecture demonstrates the model picker:

~~~text
/model
~~~

It describes model choices in terms of:

- capability for complex work;
- speed for simple questions;
- suitability for everyday tasks;
- size of the available context window;
- possible additional usage cost.

The demonstrated names and limits are time-sensitive. The lasting selection rule is:

| Workload | Preferred model characteristic |
|---|---|
| architecture, difficult debugging, large changes | highest reasoning capability |
| routine edits and common development tasks | balanced capability and latency |
| simple retrieval or quick answers | fastest adequate model |
| very large repository or long conversation | sufficient context capacity |

The most capable or largest-context model is not automatically optimal. Cost, latency, and task difficulty matter.

## 6.2 Interaction Modes

The interface cycles modes with the demonstrated keyboard control, including:

- **normal/default interaction**;
- **accept-edits mode**;
- **plan mode**.

> **Plan mode:** A mode in which Claude investigates and designs an implementation plan without immediately carrying out unrestricted project edits.

Plan mode is especially useful when:

- the task is ambiguous;
- the change spans many files;
- architecture must be agreed before implementation;
- research is needed;
- the developer wants an inspectable plan artifact.

Example:

~~~text
Create a detailed plan for a Jupyter notebook that teaches vectorless RAG
using Python and the PageIndex library. Save a copy as plan.md.
Do not implement until the plan is reviewed.
~~~

During planning, Claude may search the web, inspect a repository, and request approval to use tools. After approval, the plan can be copied into the project and used as an execution checklist.

## 6.3 Tool Categories

The lecture asks Claude to enumerate available tools and identifies these broad categories:

### File and Repository Tools

- read a file;
- search for files or text;
- edit or write a file;
- edit notebook content.

### Execution Tools

- run shell commands;
- use Bash or PowerShell according to the environment;
- execute tests, scripts, or development commands.

### Retrieval Tools

- fetch a specified webpage;
- perform web search;
- retrieve documentation through an installed integration.

### Delegation and Planning Tools

- create or invoke specialized subagents;
- explore a codebase;
- create a plan;
- manage task state.

### MCP and Integration Tools

- connect to external services made available through MCP servers or plugins.

Tool availability depends on version, environment, installed integrations, and policy.

## 6.4 Context Inspection

The demonstrated command is:

~~~text
/context
~~~

It visualizes how the context window is being used by components such as:

- the system prompt;
- tool definitions;
- project memory;
- skill descriptions;
- conversation history;
- reserved compaction buffer;
- remaining free space.

If the total context capacity is $B$, a useful accounting model is:

$$
B = T_{\text{system}} + T_{\text{tools}} + T_{\text{memory}} +
T_{\text{skills}} + T_{\text{conversation}} + T_{\text{buffer}} +
T_{\text{free}}
$$

Again, this is an explanatory budget equation. The exact internal accounting is product-dependent.

## 6.5 Context Compaction

Long sessions eventually accumulate too much detail. **Compaction** compresses prior conversation or work into a smaller representation so the agent can continue.

Benefits:

- frees context capacity;
- preserves the essential task state;
- avoids restarting from scratch.

Risk:

- details omitted from the compact summary may no longer influence later reasoning.

Important requirements and decisions should therefore also live in durable artifacts such as:

- **CLAUDE.md**;
- a task plan;
- architecture documentation;
- issue descriptions;
- tests.

## 6.6 Resuming a Prior Session

The transcript demonstrates reopening a recent conversation with a resume option, shown as:

~~~powershell
claude -r
~~~

The resumed session restores prior conversational context. Exact CLI flags can change, so confirm the installed version’s help when necessary.

### Key Takeaways

- Select a model based on task complexity, speed, context, and cost.
- Use plan mode to separate investigation and design from implementation.
- Tools turn model output into concrete project actions.
- Context is finite; inspect it, compact when needed, and store critical facts durably.
- Resume functionality can restore an earlier project conversation.

---

# 7. Persistent Project Instructions with CLAUDE.md

## 7.1 Definition

> **CLAUDE.md:** A persistent instruction file that Claude Code automatically loads into context so the user does not need to repeat important project guidance in every session.

Without persistent project memory, a new session may have to rediscover:

- what the repository does;
- its architecture;
- how to install dependencies;
- how to run tests;
- style and review conventions;
- which APIs or patterns the team prefers.

That repeated scanning costs time and context tokens.

## 7.2 Creating the File

The lecture demonstrates:

~~~text
/init
~~~

Claude analyzes the repository and proposes a **CLAUDE.md** containing useful project guidance. The user reviews and approves the edit.

## 7.3 Instruction Scopes

The lecture distinguishes three scopes.

| Scope | Typical file/location | Intended audience | Usually committed? |
|---|---|---|---|
| project/team | **CLAUDE.md** in the repository | everyone working in the project | yes |
| local/personal project | **CLAUDE.local.md** in the project | one developer on one project | no |
| user/global | Claude configuration under the user profile | the user across projects | no |

The precise discovery path can vary by version, but the conceptual scopes are important.

### Project Scope

Use for shared facts:

- project purpose;
- repository layout;
- standard commands;
- code conventions;
- required verification;
- architectural constraints.

### Local Project Scope

Use for private, machine-specific, or personal preferences:

- local service ports;
- personal workflow reminders;
- a machine-specific path;
- instructions that should not be committed.

Do not put secrets into instruction files.

### User/Global Scope

Use for preferences that should apply across projects:

- general response style;
- personal coding conventions;
- cross-project safety preferences.

Global instructions should remain generic. Project-specific rules in global memory may create incorrect behavior in unrelated repositories.

## 7.4 Recommended Contents

A useful project file can include:

~~~markdown
# Project Purpose

What the repository builds and who uses it.

## Architecture

Major modules, boundaries, and execution flow.

## Setup

Dependency installation and local configuration.

## Common Commands

- development server
- unit tests
- integration tests
- formatter
- linter
- type checker

## Engineering Conventions

Naming, error handling, logging, API, notebook, and documentation rules.

## Verification Requirements

Tests or checks that must pass before a task is considered complete.

## Constraints

Files not to edit, deprecated patterns to avoid, and security requirements.
~~~

## 7.5 Quality Rules for Persistent Memory

CLAUDE.md should be:

- concise enough to load repeatedly;
- accurate and maintained;
- written as actionable instructions;
- free of temporary chat history;
- free of credentials;
- consistent with actual project commands.

An inaccurate instruction file is worse than no instruction file because it makes the same error persistent.

### Key Takeaways

- CLAUDE.md supplies durable project context at the start of sessions.
- Use project, local, and global scopes for different audiences.
- Store stable operational facts and conventions, not secrets or transient discussion.
- Review generated instructions before committing them.

---

# 8. Subagents

## 8.1 Definition

> **Subagent:** A specialized Claude instance spawned to perform a focused task in its own context window and return a result, usually a concise summary, to the calling session.

The main session delegates a well-bounded assignment. The subagent does not automatically inherit the entire conversation; it receives the prompt and context provided to it. It performs its work independently and sends its result back.

The lecture likens subagents to coworkers:

- each receives a focused assignment;
- each can have specialized instructions and tools;
- each works in a separate context;
- the manager receives the final finding.

## 8.2 Built-In Agent Types

The demonstrated environment includes built-in roles such as:

- **Explore** — investigates a repository or searches for relevant implementation details;
- **Plan** — designs an approach before implementation;
- **General purpose** — handles a wider variety of delegated work;
- **Claude Code Guide** — answers product and usage questions;
- **Status Line Setup** — helps configure the terminal status display.

Names and built-in availability are version-dependent.

## 8.3 Why Use a Subagent?

### Context Isolation

A large repository search may produce thousands of lines of intermediate output. A subagent can consume that output in its own context and return a short synthesis. This protects the main session from irrelevant detail.

If the raw investigation produces $N$ tokens and the returned summary has $n$ tokens, then the main-context reduction is approximately:

$$
\Delta T = N - n
$$

The separate work still consumes usage; it simply avoids polluting the main reasoning context.

### Specialization

A custom agent can encode:

- a role;
- a method;
- relevant tools;
- review criteria;
- output format;
- project memory.

Examples include:

- code-quality reviewer;
- security reviewer;
- test author;
- notebook lesson reviewer;
- documentation updater;
- pull-request reviewer.

### Parallelism

Independent tasks can run concurrently. For example:

1. one agent audits a middleware notebook;
2. another checks a retrieval notebook;
3. another reviews tests.

The main session later combines their results.

## 8.4 When Not to Use a Subagent

Delegation has overhead. Do not spawn a subagent when:

- the exact file is already known and only needs to be read;
- the answer is a one-line lookup;
- a single symbol search will resolve the question;
- the task is so tightly coupled to the main reasoning that separation would lose important context.

Use the smallest mechanism that can reliably perform the task.

## 8.5 Creating a Custom Subagent

The lecture uses:

~~~text
/agents
~~~

The workflow is:

1. Open the agent library.
2. choose **Create a new agent**.
3. choose the scope:
   - project, or
   - personal/user.
4. describe the agent’s job and when it should be used.
5. optionally let Claude generate the initial specification.
6. choose a tool set.
7. choose a model.
8. choose a visual color or label.
9. choose memory scope.
10. review and save the generated definition.

## 8.6 Scope

### Project Agent

Stored with the project, typically under a Claude configuration folder. It can be shared with the team and version-controlled when appropriate.

### Personal Agent

Available to one user across projects. It is useful for reusable personal workflows but should not encode assumptions valid for only one repository.

## 8.7 Least-Privilege Tool Selection

The example creates a **Code Improvement Advisor** that scans files and suggests changes to:

- readability;
- performance;
- maintainability;
- best-practice compliance.

Because the desired output is advice, not automatic modification, the instructor grants read-only tools rather than all tools.

> **Least privilege:** Give an agent only the capabilities necessary to perform its stated task.

This lowers the chance of unintended edits or execution.

## 8.8 Agent Definition Structure

The generated Markdown file conceptually contains front matter plus a system prompt:

~~~markdown
---
name: code-improvement-advisor
description: >
  Use when the user requests code-quality, readability, performance,
  or best-practice recommendations.
tools:
  - Read
  - Glob
  - Grep
model: sonnet
memory: project
---

You are a senior code improvement advisor.

## Method

1. Inspect the relevant project files.
2. Identify issues and assign severity.
3. Explain why each issue matters.
4. Show the current code.
5. propose an improved version.
6. Do not edit files unless explicitly authorized.
~~~

The actual schema and tool identifiers should follow the installed Claude Code version. The essential design fields are:

- **name**;
- **description and trigger conditions**;
- **tools**;
- **model**;
- **memory scope**;
- **system instructions and methodology**.

## 8.9 Running the Advisor

The lecture assigns:

~~~text
Review the code of the entire project and provide suggestions.
~~~

The agent:

1. reads project files;
2. applies its review methodology;
3. categorizes findings by severity;
4. returns recommendations;
5. leaves files unchanged because the session is in plan mode and the agent is advisory.

This separation between **review** and **modification** is valuable. A team can inspect the report, select issues, then authorize a different phase to implement them.

## 8.10 Subagent Execution Model

~~~pseudocode
function delegate(task, agent_specification):
    child_context <- create_isolated_context()
    child_context.add(agent_specification)
    child_context.add(task)

    child_result <- run_agentic_loop(child_context)
    summary <- compress_for_parent(child_result)

    return summary
~~~

### Key Takeaways

- A subagent is an isolated, specialized worker.
- It protects the main context, supports specialization, and enables parallel work.
- Delegation is worthwhile for substantial focused tasks, not trivial lookups.
- Tool permissions should match the role; an advisor often needs only read access.
- A strong agent definition specifies when to use it, what it may do, how it works, and how it reports.

---

# 9. Agent View: Managing Multiple Sessions

## 9.1 The Problem

Without a centralized view, a developer may open one terminal for each task:

- update documentation;
- review tests;
- run a code-quality audit;
- investigate a bug.

As the number of tasks grows, tracking prompts, approvals, and completions across terminals becomes cumbersome.

## 9.2 Definition

> **Agent View:** A single-screen interface for dispatching and monitoring multiple Claude Code sessions, seeing which are working, which require user input, and which are complete.

The lecture launches it with:

~~~powershell
claude agents
~~~

## 9.3 Session States

The view groups work into states such as:

- **Working** — the session is actively processing;
- **Needs input** — the session is paused for permission or clarification;
- **Completed** — the task has finished.

This is a state-management dashboard, not simply a combined transcript.

## 9.4 Parallel Task Example

The instructor dispatches tasks such as:

~~~text
Update README.md with a detailed section about Agent View in Claude Code.
~~~

and:

~~~text
Review the unit tests in test_example.py and report issues.
~~~

Both proceed concurrently. If a task needs permission to read or edit a file, it moves to **Needs input**. The developer selects it, responds, and returns to the background list.

The demonstrated background command is:

~~~text
/bg
~~~

## 9.5 Running Custom Agents

Agent View can also launch the custom **Code Improvement Advisor**. This combines:

- reusable specialization from the subagent definition;
- concurrent execution;
- centralized status tracking.

## 9.6 Operational Discipline

Parallel execution introduces collision risks. Good task decomposition should ensure:

- separate files or clearly separated responsibilities;
- explicit ownership;
- no two sessions silently rewriting the same section;
- a final integration and test step;
- human review of each result.

Agent View does not itself eliminate merge conflicts or inconsistent architectural choices.

### Key Takeaways

- Agent View manages many Claude sessions from one place.
- The developer can distinguish active, blocked, and completed work at a glance.
- Approval remains task-specific even when jobs run in the background.
- Parallel tasks should have clear boundaries and a final integration check.

---

# 10. Agent Teams

## 10.1 From Hierarchical Delegation to Collaboration

The lecture contrasts two organizational patterns.

### Traditional Subagent Hierarchy

1. A main agent spawns independent subagents.
2. Each subagent performs its assignment.
3. Each returns a result to the main agent.
4. The main agent combines the results.

Communication primarily follows:

$$
\text{Main} \leftrightarrow \text{Subagent}_i
$$

Subagents do not necessarily communicate with one another.

### Collaborative Agent Team

1. A lead agent creates a team.
2. The lead creates a shared task list.
3. persistent teammates claim or receive tasks.
4. Teammates update task status.
5. Teammates communicate with one another.
6. dependencies and handoffs are coordinated.
7. The lead consolidates the result and shuts down the team.

Communication can include:

$$
\text{Lead} \leftrightarrow \text{Teammate}_i
$$

and peer-to-peer paths:

$$
\text{Teammate}_i \leftrightarrow \text{Teammate}_j
$$

## 10.2 Definition

> **Agent Team:** A lead agent plus persistent named teammates that coordinate over a shared task list and can communicate during a multi-step assignment.

The key difference is not merely the number of agents. It is the presence of:

- persistence across turns;
- shared task visibility;
- inter-agent communication;
- explicit dependencies;
- coordinated ownership.

## 10.3 Comparison

| Dimension | Independent subagents | Agent team |
|---|---|---|
| structure | hierarchical | collaborative |
| lifetime | often one focused run | persistent across multiple turns |
| communication | mainly with caller | lead plus peer-to-peer |
| task visibility | assignment-specific | shared task list |
| coordination | parent combines results | teammates coordinate and hand off |
| best fit | focused, independent work | complex, interdependent work |
| token cost | generally lower | generally higher |

## 10.4 Why Teams Cost More

Let $W_i$ be useful task work by teammate $i$, $M_{ij}$ communication between teammates $i$ and $j$, and $L$ lead coordination. A simplified token-cost model is:

$$
T_{\text{team}} \approx \sum_{i=1}^{n} W_i +
\sum_{i \ne j} M_{ij} + L
$$

Independent subagents have less peer communication:

$$
T_{\text{subagents}} \approx \sum_{i=1}^{n} W_i + L'
$$

Therefore, when collaboration messages are substantial:

$$
T_{\text{team}} > T_{\text{subagents}}
$$

This higher cost can be justified when coordination improves correctness or prevents duplicated work.

## 10.5 Enabling the Experimental Feature

At lecture time, Agent Teams is experimental. The instructor enables it in a Claude configuration **settings.json**:

~~~json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
~~~

The exact flag and support status can change. Experimental features may have:

- unstable interfaces;
- incomplete behavior;
- higher usage;
- new failure modes;
- changed configuration requirements.

## 10.6 Typical Team Lifecycle

~~~pseudocode
function run_team(complex_goal):
    team <- create_team(lead)
    tasks <- decompose(complex_goal)
    publish_shared_task_list(team, tasks)

    teammates <- spawn_required_roles(tasks)

    while unfinished_tasks_exist(tasks):
        for teammate in teammates concurrently:
            teammate.claim_ready_task()
            teammate.perform_work()
            teammate.update_status()
            teammate.message_peers_if_dependency_or_handoff()

        lead.monitor_blockers()
        lead.resolve_or_escalate_dependencies()

    result <- lead.consolidate(teammate_outputs)
    request_graceful_shutdown(teammates)
    delete_team(team)
    return result
~~~

## 10.7 Notebook-Review Demonstration

The first demonstration creates two teammates:

- a middleware notebook reviewer;
- a vectorless-RAG notebook reviewer.

Each claims its task, reviews a different notebook, marks completion, and sends findings to the lead. The lead verifies that both tasks are complete, consolidates the findings, requests graceful shutdown, and deletes the team.

## 10.8 Writer–Reviewer Demonstration

The second demonstration updates **README.md** with an Agent Teams section.

Roles:

- **Writer** — drafts and inserts the section.
- **Reviewer** — reviews the section after the writer finishes.

The review task depends on the writing task. The reviewer correctly waits rather than reviewing a nonexistent section. After the writer marks its task complete, the lead messages or wakes the reviewer.

This illustrates dependency-aware orchestration:

$$
\text{Write section} \rightarrow \text{Review section}
$$

The tasks may belong to a team, but they are not necessarily simultaneous. Correct parallel systems respect dependency order.

## 10.9 Internal Coordination Concepts

The lecture identifies operations conceptually equivalent to:

- team creation;
- teammate spawning;
- task creation;
- task claiming;
- task-status update;
- direct messaging;
- shutdown approval;
- team deletion.

The user ordinarily describes the goal; Claude Code uses the coordination tools internally.

## 10.10 When to Choose Teams

Use a team when:

- the goal naturally decomposes into roles;
- tasks have meaningful dependencies;
- teammates must exchange discoveries;
- shared task visibility prevents duplicated work;
- a writer/reviewer or implementer/tester relationship improves quality.

Prefer independent subagents when:

- tasks are unrelated;
- only final results need consolidation;
- peer communication adds little value;
- cost or latency is a primary constraint.

### Key Takeaways

- Agent Teams use a collaborative structure rather than simple fire-and-return delegation.
- Shared tasks, persistent workers, and direct messages enable coordination.
- Teams are appropriate for complex, interdependent work.
- Communication and coordination consume additional tokens.
- Dependency-aware scheduling is as important as parallelism.
- The demonstrated feature is experimental and must be verified against the current product version.

---

# 11. Skills

## 11.1 Definition

> **Skill:** A reusable, versioned collection of instructions, resources, and examples that teaches Claude Code how to complete a specific type of task.

A skill turns a frequently repeated procedure into a durable workflow. Instead of re-explaining the process in every prompt, the user invokes the skill or writes a request whose intent matches it.

## 11.2 Skill Execution Flow

1. The user requests a task.
2. Claude reasons about the request and project context.
3. Claude selects the most relevant skill.
4. The skill supplies workflow instructions.
5. Claude invokes any necessary tools, resources, or plugins.
6. Claude formats and returns the result.

~~~pseudocode
function answer_with_skills(request, available_skills, context):
    skill <- select_most_relevant(request, available_skills, context)

    if skill exists:
        instructions <- load(skill)
        result <- execute_workflow(instructions, request, context)
    else:
        result <- execute_general_agent_loop(request, context)

    return result
~~~

## 11.3 Appropriate Skill Use Cases

Create a skill when a task:

- occurs repeatedly;
- follows a stable sequence;
- has a standard output structure;
- needs the same reference material;
- must consistently use a particular integration;
- benefits from a shared team convention.

Examples:

- research a technical topic;
- retrieve current open-source documentation;
- review a pull request;
- generate a lesson notebook;
- update project documentation;
- produce a standardized code-quality report.

## 11.4 Project Skill Structure

The lecture creates project skills under a Claude configuration folder:

~~~text
.claude/
└── skills/
    └── research-topic/
        └── SKILL.md
~~~

Caption casing varies, but a canonical skill definition is conventionally named **SKILL.md**.

## 11.5 Anatomy of a Research Skill

A normalized example based on the demonstration:

~~~markdown
---
name: research-topic
description: >
  Research a technical topic using Exa when available and web search as a
  fallback. Return key points and traceable sources.
---

# Research Topic

## Input

- The topic or question to research.
- Optional scope, recency, and source constraints.

## Procedure

1. Clarify the topic only if ambiguity materially changes the result.
2. Search with Exa.
3. If Exa is unavailable or unauthenticated, use web search.
4. Prefer primary and authoritative sources.
5. Reconcile conflicting claims.
6. Separate sourced facts from inference.

## Output

- concise answer;
- key points;
- important caveats;
- source links.
~~~

The lecture invokes the skill with a slash command followed by the topic, for example:

~~~text
/research-topic What are LLM gateways?
~~~

## 11.6 Skill Selection and Specificity

A good skill description helps Claude decide when it applies. It should identify:

- the task class;
- intended inputs;
- expected outputs;
- required tools;
- fallback behavior;
- exclusions.

A vague description such as “useful research helper” can cause poor routing. A precise description such as “research current technical topics using Exa with web-search fallback and return cited findings” is easier to select correctly.

## 11.7 Skills Versus One-Off Prompts

| One-off prompt | Skill |
|---|---|
| written for one session | reusable |
| instructions may drift | versioned and reviewable |
| little discovery metadata | description supports selection |
| context lives in conversation | workflow lives in files/resources |
| hard to standardize across a team | can encode a shared procedure |

### Key Takeaways

- Skills encode repeatable procedures as reusable, reviewable assets.
- Claude can choose a skill from request intent and context.
- Good skills specify inputs, steps, tools, fallbacks, and output format.
- Use a skill for stable recurring work, not every ad hoc question.

---

# 12. Plugins and External Integrations

## 12.1 Definition

> **Plugin:** A packaged integration that provides tools, resources, or capabilities to Claude Code through a standard interface.

Plugins connect the agentic environment to specialized services. Examples discussed include:

- Exa for search and content extraction;
- GitHub-oriented operations;
- Playwright browser automation;
- Context7 for current library documentation.

## 12.2 Plugin Call Flow

~~~pseudocode
function use_plugin(user_request):
    plugin <- choose_capability(user_request)
    plugin_input <- construct_arguments(user_request)
    external_result <- plugin.call(plugin_input)
    final_answer <- interpret_and_format(external_result)
    return final_answer
~~~

The model does not merely forward a question. It must:

1. choose the appropriate integration;
2. construct valid inputs;
3. receive external results;
4. interpret them in project context;
5. report the answer.

## 12.3 Skills and Plugins Are Different

| Concept | Primary purpose |
|---|---|
| skill | defines **how to perform a repeatable workflow** |
| plugin | supplies **an external capability or integration** |
| tool | the callable operation exposed to the agent |
| MCP server | a standardized provider through which tools/resources may be exposed |

A skill can call one or more plugin-provided tools:

$$
\text{Request} \rightarrow \text{Skill workflow} \rightarrow
\text{Plugin tool} \rightarrow \text{External result} \rightarrow
\text{Formatted answer}
$$

The skill is the procedure; the plugin is a capability used by that procedure.

## 12.4 Discovering and Installing Plugins

The lecture demonstrates the plugin interface:

~~~text
/plugins
~~~

From the marketplace or discovery view, the user can:

1. inspect available integrations;
2. view installed plugins;
3. install an integration;
4. authenticate if required;
5. reload plugins so newly installed tools become available.

Some integrations also provide a command that can be pasted into Claude Code. Installation and authentication are separate operations.

## 12.5 Authentication

The Exa example is installed but initially cannot be called because one-time authentication has not completed. The skill falls back to ordinary web search.

This teaches two important lessons:

1. **Installed does not mean ready.** A plugin may still require an API key, login, consent, or session reload.
2. **Workflows need fallbacks.** A research skill should say what to do when a preferred provider is unavailable.

Never place API secrets in:

- committed project instructions;
- skill examples;
- source code;
- screenshots or chat prompts.

Use the integration’s supported credential mechanism.

## 12.6 Exa Research Example

The research skill is designed to:

1. accept a topic;
2. call Exa for search and extraction;
3. use web search if Exa is unavailable;
4. synthesize the results;
5. return key points and sources.

When Exa authentication fails, Claude reports the limitation and proceeds with the fallback. Transparent degradation is better than pretending that the preferred tool ran successfully.

## 12.7 Context7 Documentation Example

The lecture installs a Context7 plugin to retrieve up-to-date documentation for open-source libraries.

Example request:

~~~text
Using the Context7 plugin and the current LangChain documentation,
explain how to create deep agents with Python.
~~~

Claude:

1. loads the integration’s tools;
2. resolves the relevant library;
3. queries current documentation;
4. summarizes concepts and code patterns.

This is valuable because library APIs evolve. Retrieval from a current documentation provider reduces reliance on potentially stale model memory.

## 12.8 Open-Source Documentation Skill

The instructor then turns the procedure into another reusable skill:

~~~text
.claude/
└── skills/
    └── open-source-documentation/
        └── SKILL.md
~~~

Its purpose is to:

- accept a library name and user question;
- call Context7;
- retrieve recent documentation;
- return current explanations and examples.

A normalized invocation is:

~~~text
/open-source-documentation LangChain: show the current way to develop agents
~~~

## 12.9 Reliability Considerations

Plugins introduce external dependencies:

- service availability;
- API changes;
- credentials;
- rate limits;
- billing;
- network access;
- source quality.

A robust plugin-backed skill should define:

1. the preferred integration;
2. authentication expectations;
3. a fallback;
4. source-quality rules;
5. failure reporting;
6. output validation.

### Key Takeaways

- Plugins extend Claude Code with external capabilities.
- A skill can orchestrate plugin tools as part of a repeatable workflow.
- Installation, authentication, and tool loading are distinct states.
- Context7 demonstrates current-documentation retrieval; Exa demonstrates research search.
- Tool failures should be surfaced clearly and handled through explicit fallbacks.

---

# 13. Integrated Architecture

The lecture’s components can be understood as a layered system.

~~~text
User requirement
    |
    v
Claude Code agentic loop
    |
    +-- persistent context: CLAUDE.md / local / user memory
    |
    +-- mode: normal / accept edits / plan
    |
    +-- reusable procedure: skill
    |       |
    |       +-- built-in file, search, execution, or web tool
    |       +-- plugin/MCP-provided external tool
    |
    +-- delegation: specialized subagent
    |
    +-- concurrency dashboard: Agent View
    |
    +-- collaborative orchestration: Agent Team
    |
    v
Action, observation, verification, and human approval
    |
    v
Reviewed project change or knowledge artifact
~~~

## 13.1 Responsibility of Each Layer

| Layer | Main question answered |
|---|---|
| user prompt | What outcome is needed? |
| CLAUDE.md and memory | What stable context and rules apply? |
| model and agent loop | How should the system reason, act, and verify? |
| mode | Is the system planning, proposing edits, or implementing? |
| skill | What repeatable procedure should be followed? |
| tool/plugin/MCP | What concrete capability is needed? |
| subagent | What focused work should be isolated or delegated? |
| Agent View | How are multiple sessions monitored? |
| Agent Team | How do persistent workers coordinate? |
| human approval | Which consequential actions are authorized? |

## 13.2 Context Engineering

> **Context engineering:** The deliberate selection, organization, persistence, and compression of information supplied to an AI system so it can act accurately and efficiently.

The lecture illustrates context engineering through:

- repository access;
- CLAUDE.md;
- local and global memory;
- isolated subagent contexts;
- context inspection;
- compaction;
- plugin-based retrieval;
- shared team task state.

More context is not always better. Good context is:

- relevant;
- authoritative;
- current;
- compact;
- appropriately scoped.

## 13.3 A Rigorous Task Pattern

For a consequential project change:

1. **Define the requirement**
   - state the outcome;
   - name constraints;
   - define acceptance criteria.

2. **Load durable context**
   - review CLAUDE.md;
   - confirm repository commands;
   - identify sensitive boundaries.

3. **Choose execution mode**
   - use plan mode for ambiguity or broad changes;
   - use direct execution only when scope is clear.

4. **Select the right mechanism**
   - direct tool for a trivial operation;
   - skill for a repeatable workflow;
   - subagent for isolated specialization;
   - Agent View for independent parallel sessions;
   - Agent Team for collaboration and dependencies.

5. **Apply least privilege**
   - read-only for analysis;
   - editing only when required;
   - execution or network access only when justified.

6. **Execute and observe**
   - inspect tool calls and errors;
   - intervene when assumptions are wrong.

7. **Verify**
   - run tests;
   - review diffs;
   - validate generated reports;
   - check the result against acceptance criteria.

8. **Persist useful knowledge**
   - update documentation or tests;
   - refine the skill or agent if the workflow will recur;
   - keep project memory accurate.

### Key Takeaways

- Claude Code is a layered system, not only a chat model.
- Context, procedure, capability, delegation, and approval solve different problems.
- Choose the simplest adequate orchestration mechanism.
- Verification and durable knowledge are required to convert an AI action into reliable engineering work.

---

# 14. Common Failure Modes and Corrective Practices

## 14.1 Blindly Approving Every Tool Call

**Failure:** Treating permission prompts as a nuisance.

**Correction:** Read the proposed action, target, and effect. Approve only what the task requires.

## 14.2 Giving Every Agent Every Tool

**Failure:** An advisory agent can edit files or execute commands unnecessarily.

**Correction:** Apply least privilege. The lecture’s code advisor is intentionally read-only.

## 14.3 Using Agents for Trivial Retrieval

**Failure:** Spawning an isolated worker to read a known file or find one symbol.

**Correction:** Use direct reading or search for simple operations.

## 14.4 Starting Implementation Before Agreement

**Failure:** A broad requirement causes many premature edits.

**Correction:** Use plan mode, save an inspectable plan, and obtain approval.

## 14.5 Letting Context Become Noisy

**Failure:** Large searches and raw output consume the main context.

**Correction:** delegate broad investigation to a subagent, request a synthesis, compact long sessions, and persist critical facts separately.

## 14.6 Stale Persistent Instructions

**Failure:** CLAUDE.md contains obsolete commands or architecture.

**Correction:** Treat it as maintained project documentation and review it alongside code changes.

## 14.7 Confusing Skills with Plugins

**Failure:** Expecting a plugin to define an entire workflow, or expecting a skill alone to supply external data.

**Correction:** A skill describes the process; a plugin provides a capability that the process can call.

## 14.8 Assuming Installation Implies Authentication

**Failure:** An installed integration is called before credentials or login are configured.

**Correction:** verify installation, authentication, loading, and a simple test call separately.

## 14.9 Parallel Edit Collisions

**Failure:** Multiple sessions or teammates edit the same file without ownership or sequencing.

**Correction:** assign clear boundaries, represent dependencies, and perform final integration review.

## 14.10 Treating Experimental Features as Stable

**Failure:** Building a critical workflow around an experimental flag without checking current support.

**Correction:** verify documentation, expect interface changes, and retain a simpler fallback workflow.

### Key Takeaways

- Most failures come from poor scope, excessive privilege, weak context, or missing verification.
- Parallelism must be designed around ownership and dependencies.
- External integrations have operational states and failure modes.
- Persistent instructions and experimental features require maintenance.

---

# 15. Practical Command and File Reference

The following table records commands demonstrated or described in the lecture. Exact syntax may vary by installed version.

| Purpose | Demonstrated command or action |
|---|---|
| start Claude Code in current project | **claude** |
| initialize project instructions | **/init** |
| select a model | **/model** |
| inspect context use | **/context** |
| manage/create subagents | **/agents** |
| open plugin management | **/plugins** |
| return to background task list in Agent View | **/bg** |
| resume a prior session | **claude -r** |
| launch Agent View | **claude agents** |
| switch interaction modes | demonstrated with **Shift+Tab** |

Important files:

| File/folder | Role |
|---|---|
| **CLAUDE.md** | shared repository instructions |
| **CLAUDE.local.md** | personal instructions for one project |
| user-level Claude configuration | cross-project personal instructions |
| **.claude/agents/** | project agent definitions |
| **.claude/skills/** | project skill definitions |
| **.claude/settings.json** | project Claude settings and demonstrated experimental flag |
| **plan.md** | inspectable implementation plan created for reference |

### Key Takeaways

- Slash commands expose common management functions inside a Claude session.
- Configuration files make context, roles, workflows, and settings durable.
- Check current help and documentation when a command differs from the lecture.

---

# 16. Final Synthesis

The lecture’s central progression is:

1. use Claude as a file-aware assistant;
2. understand Claude Code as an agentic loop;
3. establish project context with CLAUDE.md;
4. inspect and manage models, tools, sessions, and context;
5. delegate focused work to subagents;
6. monitor independent concurrent work through Agent View;
7. coordinate interdependent workers through Agent Teams;
8. encode recurring procedures as skills;
9. extend those procedures through plugins and current external data;
10. keep a human responsible for permissions, correctness, and final acceptance.

> **Final principle:** Reliable AI-assisted engineering is achieved by combining clear requirements, scoped context, least-privilege tools, appropriate delegation, explicit verification, and human judgment.

## Final Key Takeaways

- Claude Code is an agentic development harness around a language model.
- The operational loop is context gathering, action, verification, and iteration.
- CLAUDE.md reduces repeated project discovery and standardizes team guidance.
- Subagents isolate specialized work; Agent View monitors concurrent sessions.
- Agent Teams add persistent peer coordination for complex dependencies.
- Skills encode repeatable workflows; plugins supply external capabilities.
- Context and token budgets are resources that must be engineered.
- Approval prompts, trust boundaries, and prompt-injection awareness are essential.
- AI output becomes professional engineering work only after deliberate verification.
