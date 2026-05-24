#!/usr/bin/env python3
"""
Few-Shot Templates — Dynamic In-Context Template Interpolation
===============================================================
A modular system for managing prompt templates that inject few-shot examples
at runtime. Supports:
  • Template registration with typed placeholders
  • Dynamic example selection based on task similarity
  • Token budget enforcement
  • Multiple output format specifications

Run:
    python few_shot_templates.py
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import re
import textwrap


# ── Data Structures ─────────────────────────────────────────────────────────
@dataclass
class FewShotExample:
    """A single input-output demonstration pair."""
    input_text: str
    output_text: str
    domain: str = "general"
    token_estimate: int = 0

    def __post_init__(self):
        # Rough token estimate: ~4 chars per token (English average)
        self.token_estimate = (len(self.input_text) + len(self.output_text)) // 4


@dataclass
class PromptTemplate:
    """A reusable prompt template with placeholders and few-shot slots."""
    name: str
    system_instruction: str
    task_prefix: str
    example_format: str      # Template for each few-shot example
    query_format: str        # Template for the final user query
    max_examples: int = 5
    max_tokens: int = 2000   # Token budget for the full prompt
    separator: str = "\n---\n"

    def render(
        self,
        query: str,
        examples: List[FewShotExample],
        variables: Optional[Dict[str, str]] = None,
    ) -> str:
        """Interpolate the full prompt with examples and query."""
        variables = variables or {}

        # System instruction with variable substitution
        system = self._interpolate(self.system_instruction, variables)
        task = self._interpolate(self.task_prefix, variables)

        # Select examples within token budget
        selected = self._budget_select(examples)

        # Render examples
        example_blocks = []
        for ex in selected:
            block = self.example_format.replace("{{input}}", ex.input_text)
            block = block.replace("{{output}}", ex.output_text)
            block = self._interpolate(block, variables)
            example_blocks.append(block)

        # Render query
        query_block = self.query_format.replace("{{query}}", query)
        query_block = self._interpolate(query_block, variables)

        # Assemble
        sections = [system, task]
        if example_blocks:
            sections.append(self.separator.join(example_blocks))
        sections.append(query_block)
        return "\n\n".join(sections)

    def _interpolate(self, template: str, variables: Dict[str, str]) -> str:
        """Replace {{key}} placeholders with variable values."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", value)
        return result

    def _budget_select(self, examples: List[FewShotExample]) -> List[FewShotExample]:
        """Greedily select examples within the token budget."""
        budget = self.max_tokens
        selected: List[FewShotExample] = []
        for ex in examples[: self.max_examples]:
            if budget - ex.token_estimate < 200:  # Reserve 200 tokens for query
                break
            selected.append(ex)
            budget -= ex.token_estimate
        return selected


# ── Template Registry ───────────────────────────────────────────────────────
class TemplateRegistry:
    """Central registry for managing prompt templates and example banks."""

    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        self._examples: Dict[str, List[FewShotExample]] = {}

    def register_template(self, template: PromptTemplate) -> None:
        self._templates[template.name] = template

    def add_examples(self, template_name: str, examples: List[FewShotExample]) -> None:
        if template_name not in self._examples:
            self._examples[template_name] = []
        self._examples[template_name].extend(examples)

    def build_prompt(
        self,
        template_name: str,
        query: str,
        variables: Optional[Dict[str, str]] = None,
        domain_filter: Optional[str] = None,
    ) -> str:
        """Build a complete prompt from template + examples + query."""
        template = self._templates[template_name]
        examples = self._examples.get(template_name, [])

        # Optional domain filtering
        if domain_filter:
            examples = [ex for ex in examples if ex.domain == domain_filter]

        return template.render(query, examples, variables)

    def list_templates(self) -> List[str]:
        return list(self._templates.keys())


# ── Pre-Built Templates ────────────────────────────────────────────────────
def create_sentiment_template() -> PromptTemplate:
    return PromptTemplate(
        name="sentiment_analysis",
        system_instruction=(
            "You are a sentiment analysis engine. Classify the sentiment of "
            "the given text as POSITIVE, NEGATIVE, or NEUTRAL. Respond with "
            "only the label and a confidence score."
        ),
        task_prefix="## Examples of sentiment classification:",
        example_format="Input: {{input}}\nSentiment: {{output}}",
        query_format="Input: {{query}}\nSentiment:",
        max_examples=4,
        max_tokens=1500,
    )


def create_code_review_template() -> PromptTemplate:
    return PromptTemplate(
        name="code_review",
        system_instruction=(
            "You are a senior {{language}} engineer conducting a code review. "
            "Identify bugs, performance issues, and style violations. "
            "Provide specific line-level feedback."
        ),
        task_prefix="## Previous review examples for reference:",
        example_format=(
            "### Code Snippet:\n```\n{{input}}\n```\n"
            "### Review:\n{{output}}"
        ),
        query_format=(
            "### Code Snippet:\n```\n{{query}}\n```\n"
            "### Review:"
        ),
        max_examples=3,
        max_tokens=2500,
    )


def create_sql_generator_template() -> PromptTemplate:
    return PromptTemplate(
        name="sql_generator",
        system_instruction=(
            "You are a SQL query generator. Given a natural language question "
            "and the database schema, produce a correct {{dialect}} SQL query. "
            "Use CTEs for complex queries. Always include comments."
        ),
        task_prefix="## Example queries for the {{schema_name}} schema:",
        example_format=(
            "Question: {{input}}\n"
            "SQL:\n```sql\n{{output}}\n```"
        ),
        query_format=(
            "Question: {{query}}\n"
            "SQL:\n```sql"
        ),
        max_examples=5,
        max_tokens=2000,
    )


# ── Demo ────────────────────────────────────────────────────────────────────
def run_demo() -> None:
    print("=" * 72)
    print("FEW-SHOT TEMPLATES — Dynamic In-Context Prompt Construction")
    print("=" * 72)

    registry = TemplateRegistry()

    # 1. Sentiment Analysis
    sentiment_template = create_sentiment_template()
    registry.register_template(sentiment_template)
    registry.add_examples("sentiment_analysis", [
        FewShotExample("The product arrived on time and works perfectly!", "POSITIVE (0.95)", "retail"),
        FewShotExample("Terrible customer service. Will never buy again.", "NEGATIVE (0.92)", "retail"),
        FewShotExample("The package was delivered to my address.", "NEUTRAL (0.88)", "retail"),
        FewShotExample("I absolutely love the new update! Great features.", "POSITIVE (0.97)", "tech"),
        FewShotExample("App crashes every time I open it. Frustrating.", "NEGATIVE (0.94)", "tech"),
    ])

    prompt = registry.build_prompt(
        "sentiment_analysis",
        query="The food was okay but the waiter was incredibly rude.",
        domain_filter="retail",
    )
    print(f"\n{'─' * 60}")
    print("  TEMPLATE: Sentiment Analysis (filtered to 'retail' domain)")
    print(f"{'─' * 60}")
    print(textwrap.indent(prompt, "  "))

    # 2. Code Review
    code_template = create_code_review_template()
    registry.register_template(code_template)
    registry.add_examples("code_review", [
        FewShotExample(
            "def get_user(id):\n    return db.query(f'SELECT * FROM users WHERE id={id}')",
            "🔴 **SQL Injection**: Line 2 uses f-string interpolation for SQL. "
            "Use parameterized queries: `db.query('SELECT * FROM users WHERE id=?', [id])`",
            "python",
        ),
        FewShotExample(
            "for i in range(len(items)):\n    result.append(transform(items[i]))",
            "⚠️ **Style**: Use list comprehension instead of manual loop+append:\n"
            "`result = [transform(item) for item in items]`",
            "python",
        ),
    ])

    prompt = registry.build_prompt(
        "code_review",
        query="passwords = open('users.csv').read()\nfor line in passwords.split('\\n'):\n    print(line)",
        variables={"language": "Python"},
    )
    print(f"\n{'─' * 60}")
    print("  TEMPLATE: Code Review (Python)")
    print(f"{'─' * 60}")
    print(textwrap.indent(prompt, "  "))

    # 3. SQL Generator
    sql_template = create_sql_generator_template()
    registry.register_template(sql_template)
    registry.add_examples("sql_generator", [
        FewShotExample(
            "How many orders were placed last month?",
            "-- Count orders from the previous calendar month\n"
            "SELECT COUNT(*) AS order_count\n"
            "FROM orders\n"
            "WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')\n"
            "  AND created_at < DATE_TRUNC('month', CURRENT_DATE);",
        ),
        FewShotExample(
            "Top 5 customers by total spend",
            "-- Rank customers by cumulative spend\n"
            "WITH customer_spend AS (\n"
            "    SELECT customer_id, SUM(amount) AS total\n"
            "    FROM orders\n"
            "    GROUP BY customer_id\n"
            ")\n"
            "SELECT c.name, cs.total\n"
            "FROM customer_spend cs\n"
            "JOIN customers c ON c.id = cs.customer_id\n"
            "ORDER BY cs.total DESC\n"
            "LIMIT 5;",
        ),
    ])

    prompt = registry.build_prompt(
        "sql_generator",
        query="Which products have never been ordered?",
        variables={"dialect": "PostgreSQL", "schema_name": "ecommerce"},
    )
    print(f"\n{'─' * 60}")
    print("  TEMPLATE: SQL Generator (PostgreSQL)")
    print(f"{'─' * 60}")
    print(textwrap.indent(prompt, "  "))

    # 4. Registry summary
    print(f"\n{'─' * 60}")
    print(f"  Registered templates: {registry.list_templates()}")
    print(f"{'─' * 60}")


if __name__ == "__main__":
    run_demo()
