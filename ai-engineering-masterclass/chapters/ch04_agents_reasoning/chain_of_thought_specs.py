#!/usr/bin/env python3
"""
Chain of Thought Specifications — Sequential Reasoning Validation
===================================================================
A multi-step execution abstraction that forces explicit sequential
breakdown before emitting a final solution. Implements:

  • Structured reasoning chain with validation gates
  • Intermediate scratchpad generation
  • Step-dependency tracking
  • Token-cost vs accuracy trade-off analysis
  • Automatic reasoning verification

Run:
    python chain_of_thought_specs.py
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import time


# ── Data Types ──────────────────────────────────────────────────────────────
class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ReasoningStep:
    """A single step in the chain of thought."""
    step_id: str
    description: str
    reasoning: str = ""
    result: Any = None
    status: StepStatus = StepStatus.PENDING
    validation_fn: Optional[Callable] = None
    depends_on: List[str] = field(default_factory=list)
    token_cost: int = 0
    execution_ms: float = 0.0

    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute this reasoning step and validate the result."""
        start = time.perf_counter()

        # Generate reasoning (simulated)
        self.token_cost = len(self.reasoning) // 4 if self.reasoning else 10

        # Validate if validator exists
        if self.validation_fn:
            try:
                self.status = StepStatus.PASSED if self.validation_fn(self.result, context) else StepStatus.FAILED
            except Exception:
                self.status = StepStatus.FAILED
        else:
            self.status = StepStatus.PASSED

        self.execution_ms = (time.perf_counter() - start) * 1000
        return self.status == StepStatus.PASSED


@dataclass
class ChainResult:
    """The final result of a chain-of-thought execution."""
    final_answer: Any
    steps: List[ReasoningStep]
    total_tokens: int
    total_time_ms: float
    passed: bool
    accuracy_score: float


# ── Chain of Thought Engine ────────────────────────────────────────────────
class ChainOfThought:
    """
    Orchestrates multi-step reasoning with validation gates.

    Flow:
      Step 1: Parse problem → validate understanding
      Step 2: Identify approach → validate feasibility
      Step 3: Execute solution → validate intermediate results
      Step 4: Verify answer → validate against constraints
      Step 5: Format output → validate completeness
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self._steps: List[ReasoningStep] = []
        self._context: Dict[str, Any] = {}

    def add_step(self, step: ReasoningStep) -> "ChainOfThought":
        """Add a reasoning step to the chain (fluent API)."""
        self._steps.append(step)
        return self

    def set_context(self, key: str, value: Any) -> "ChainOfThought":
        self._context[key] = value
        return self

    def execute(self) -> ChainResult:
        """Execute all steps in order, respecting dependencies."""
        start = time.perf_counter()
        total_tokens = 0

        if self.verbose:
            print(f"\n  ┌{'─' * 58}┐")
            print(f"  │{'CHAIN OF THOUGHT EXECUTION':^58}│")
            print(f"  └{'─' * 58}┘")

        for step in self._steps:
            # Check dependencies
            deps_met = all(
                self._get_step(dep_id).status == StepStatus.PASSED
                for dep_id in step.depends_on
                if self._get_step(dep_id) is not None
            )

            if not deps_met:
                step.status = StepStatus.SKIPPED
                if self.verbose:
                    print(f"  ⏭  Step {step.step_id}: SKIPPED (unmet dependencies)")
                continue

            # Execute step
            step.status = StepStatus.RUNNING
            if self.verbose:
                print(f"\n  ▶  Step {step.step_id}: {step.description}")
                print(f"     Reasoning: {step.reasoning[:70]}...")

            passed = step.execute(self._context)
            total_tokens += step.token_cost

            # Store result in context for downstream steps
            self._context[f"step_{step.step_id}_result"] = step.result

            if self.verbose:
                icon = "✅" if passed else "❌"
                print(f"     Result: {step.result}")
                print(f"     {icon} Status: {step.status.value} | "
                      f"Tokens: {step.token_cost} | Time: {step.execution_ms:.1f}ms")

            if not passed:
                if self.verbose:
                    print(f"  ⛔ Chain halted at step {step.step_id}")
                break

        # Compute final result
        elapsed = (time.perf_counter() - start) * 1000
        passed_steps = sum(1 for s in self._steps if s.status == StepStatus.PASSED)
        accuracy = passed_steps / len(self._steps) if self._steps else 0.0

        final_step = self._steps[-1] if self._steps else None
        final_answer = final_step.result if final_step and final_step.status == StepStatus.PASSED else None

        return ChainResult(
            final_answer=final_answer,
            steps=self._steps,
            total_tokens=total_tokens,
            total_time_ms=elapsed,
            passed=all(s.status == StepStatus.PASSED for s in self._steps),
            accuracy_score=accuracy,
        )

    def _get_step(self, step_id: str) -> Optional[ReasoningStep]:
        for s in self._steps:
            if s.step_id == step_id:
                return s
        return None


# ── Problem Solvers ────────────────────────────────────────────────────────
def solve_math_word_problem() -> ChainResult:
    """
    Solve: "A store sells apples at $3 each and oranges at $5 each.
    If a customer buys 4 apples and 7 oranges, and pays with a $100 bill,
    how much change do they receive?"
    """
    chain = ChainOfThought(verbose=True)

    chain.set_context("problem", (
        "A store sells apples at $3 each and oranges at $5 each. "
        "A customer buys 4 apples and 7 oranges, pays with $100."
    ))

    # Step 1: Parse the problem
    chain.add_step(ReasoningStep(
        step_id="1",
        description="Parse problem — identify quantities and relationships",
        reasoning="Extract: apple_price=$3, orange_price=$5, apple_qty=4, "
                  "orange_qty=7, payment=$100. Goal: compute change.",
        result={"apple_price": 3, "orange_price": 5, "apple_qty": 4, "orange_qty": 7, "payment": 100},
        validation_fn=lambda r, ctx: all(k in r for k in ["apple_price", "orange_price", "payment"]),
    ))

    # Step 2: Calculate apple cost
    chain.add_step(ReasoningStep(
        step_id="2",
        description="Calculate cost of apples: 4 × $3",
        reasoning="apple_cost = apple_qty × apple_price = 4 × 3 = 12",
        result=12,
        depends_on=["1"],
        validation_fn=lambda r, ctx: r == 4 * 3,
    ))

    # Step 3: Calculate orange cost
    chain.add_step(ReasoningStep(
        step_id="3",
        description="Calculate cost of oranges: 7 × $5",
        reasoning="orange_cost = orange_qty × orange_price = 7 × 5 = 35",
        result=35,
        depends_on=["1"],
        validation_fn=lambda r, ctx: r == 7 * 5,
    ))

    # Step 4: Total cost
    chain.add_step(ReasoningStep(
        step_id="4",
        description="Calculate total cost: apples + oranges",
        reasoning="total = apple_cost + orange_cost = 12 + 35 = 47",
        result=47,
        depends_on=["2", "3"],
        validation_fn=lambda r, ctx: r == ctx.get("step_2_result", 0) + ctx.get("step_3_result", 0),
    ))

    # Step 5: Calculate change
    chain.add_step(ReasoningStep(
        step_id="5",
        description="Calculate change: payment - total",
        reasoning="change = payment - total = 100 - 47 = 53",
        result=53,
        depends_on=["4"],
        validation_fn=lambda r, ctx: r == 100 - ctx.get("step_4_result", 0) and r >= 0,
    ))

    # Step 6: Final verification
    chain.add_step(ReasoningStep(
        step_id="6",
        description="Verify: change + total = payment",
        reasoning="Verification: 53 + 47 = 100 ✓. The answer is $53.",
        result="The customer receives $53 in change.",
        depends_on=["5"],
        validation_fn=lambda r, ctx: "53" in str(r),
    ))

    return chain.execute()


def solve_logic_puzzle() -> ChainResult:
    """
    Solve: "Three friends (Alice, Bob, Carol) each have a different pet
    (cat, dog, fish). Alice doesn't have the cat. Bob doesn't have the
    dog or the fish. What pet does each person have?"
    """
    chain = ChainOfThought(verbose=True)

    # Step 1: Parse constraints
    chain.add_step(ReasoningStep(
        step_id="1",
        description="Parse constraints from the problem",
        reasoning="Constraints: (1) Alice ≠ cat, (2) Bob ≠ dog, (3) Bob ≠ fish. "
                  "Each person has exactly one pet; each pet belongs to exactly one person.",
        result={"alice_not": ["cat"], "bob_not": ["dog", "fish"]},
        validation_fn=lambda r, ctx: "bob_not" in r and len(r["bob_not"]) == 2,
    ))

    # Step 2: Deduce Bob's pet
    chain.add_step(ReasoningStep(
        step_id="2",
        description="Deduce Bob's pet by elimination",
        reasoning="Bob ≠ dog AND Bob ≠ fish. Pets are {cat, dog, fish}. "
                  "Therefore Bob = cat (only option remaining).",
        result={"bob": "cat"},
        depends_on=["1"],
        validation_fn=lambda r, ctx: r.get("bob") == "cat",
    ))

    # Step 3: Deduce Alice's pet
    chain.add_step(ReasoningStep(
        step_id="3",
        description="Deduce Alice's pet",
        reasoning="Alice ≠ cat (given). Bob = cat (from step 2). "
                  "Remaining pets for Alice: {dog, fish}. No constraint eliminates "
                  "either, but we need Carol's constraint too. Alice can have dog or fish.",
        result={"remaining_for_alice": ["dog", "fish"]},
        depends_on=["2"],
        validation_fn=lambda r, ctx: len(r.get("remaining_for_alice", [])) == 2,
    ))

    # Step 4: Deduce Carol's pet
    chain.add_step(ReasoningStep(
        step_id="4",
        description="Assign remaining pets",
        reasoning="No additional constraints on Alice or Carol. "
                  "Possible assignments: Alice=dog, Carol=fish OR Alice=fish, Carol=dog. "
                  "Without further constraints, both are valid. Choosing the first valid assignment.",
        result={"alice": "dog", "bob": "cat", "carol": "fish"},
        depends_on=["3"],
        validation_fn=lambda r, ctx: (
            set(r.values()) == {"cat", "dog", "fish"} and
            r.get("bob") == "cat" and r.get("alice") != "cat"
        ),
    ))

    return chain.execute()


# ── Token Cost Analysis ────────────────────────────────────────────────────
def analyze_token_costs(results: List[Tuple[str, ChainResult]]) -> None:
    """Compare token costs between CoT and direct answers."""
    print(f"\n{'═' * 72}")
    print("  TOKEN COST vs ACCURACY ANALYSIS:")
    print(f"{'═' * 72}")
    print(f"  {'Problem':<25s}  {'Steps':>5s}  {'Tokens':>7s}  {'Time (ms)':>9s}  {'Accuracy':>8s}  {'Pass':>5s}")
    print(f"  {'─' * 70}")

    for name, result in results:
        print(f"  {name:<25s}  {len(result.steps):>5d}  {result.total_tokens:>7d}  "
              f"{result.total_time_ms:>9.1f}  {result.accuracy_score:>7.0%}  "
              f"{'✅' if result.passed else '❌':>5s}")

    # Comparison with hypothetical direct answer
    print(f"\n  {'─' * 70}")
    print(f"  Hypothetical direct answer (no CoT):")
    print(f"  {'Direct Math':<25s}  {'1':>5s}  {'15':>7s}  {'0.5':>9s}  {'~70%':>8s}  {'?':>5s}")
    print(f"  {'Direct Logic':<25s}  {'1':>5s}  {'20':>7s}  {'0.5':>9s}  {'~50%':>8s}  {'?':>5s}")
    print(f"\n  INSIGHT: CoT uses 3-5x more tokens but dramatically improves")
    print(f"  accuracy on multi-step problems. The trade-off is justified when")
    print(f"  correctness matters more than latency/cost.")


# ── Demo ────────────────────────────────────────────────────────────────────
def run_demo() -> None:
    print("=" * 72)
    print("CHAIN OF THOUGHT — Sequential Reasoning Validation")
    print("=" * 72)

    # Problem 1: Math word problem
    print(f"\n{'━' * 72}")
    print("  PROBLEM 1: Math Word Problem")
    print(f"{'━' * 72}")
    math_result = solve_math_word_problem()
    print(f"\n  FINAL ANSWER: {math_result.final_answer}")

    # Problem 2: Logic puzzle
    print(f"\n{'━' * 72}")
    print("  PROBLEM 2: Logic Puzzle")
    print(f"{'━' * 72}")
    logic_result = solve_logic_puzzle()
    print(f"\n  FINAL ANSWER: {logic_result.final_answer}")

    # Token cost analysis
    analyze_token_costs([
        ("Math Word Problem", math_result),
        ("Logic Puzzle", logic_result),
    ])

    # Architecture diagram
    print(f"\n{'═' * 72}")
    print("  CHAIN OF THOUGHT ARCHITECTURE:")
    print("  ┌────────────────────────────────────────────────────┐")
    print("  │  Problem                                          │")
    print("  │    ▼                                               │")
    print("  │  Step 1: Parse ──── Validate ──── ✅/❌           │")
    print("  │    ▼                                               │")
    print("  │  Step 2: Plan ───── Validate ──── ✅/❌           │")
    print("  │    ▼                                               │")
    print("  │  Step 3: Solve ──── Validate ──── ✅/❌           │")
    print("  │    ▼                                               │")
    print("  │  Step 4: Verify ─── Validate ──── ✅/❌           │")
    print("  │    ▼                                               │")
    print("  │  Final Answer (only if ALL gates pass)            │")
    print("  └────────────────────────────────────────────────────┘")
    print("═" * 72)


if __name__ == "__main__":
    run_demo()
