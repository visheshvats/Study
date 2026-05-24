#!/usr/bin/env python3
"""
AI Engineering Masterclass — Capstone Application
====================================================
Clean application entry-point that demonstrates an integrated pipeline
linking code samples from all five chapters:

  Ch1: Tokenization → Embedding → Attention
  Ch2: Self-Supervised Training → Transformer Blocks
  Ch3: RAG Pipeline → Context Management
  Ch4: Agent Orchestration → Chain of Thought
  Ch5: Benchmarking → Distillation → Quantization

Run:
    python main.py
"""

import sys
import os

# Add parent directory to path for chapter imports
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)


def separator(title: str) -> None:
    print(f"\n{'━' * 72}")
    print(f"  {title}")
    print(f"{'━' * 72}")


def run_chapter_1():
    """Chapter 1: Foundations of Text, Semantics, and Tokens"""
    separator("CHAPTER 1 — Text, Semantics, and Tokens")
    try:
        from chapters.ch01_text_semantics_tokens.tokenization_demo import run_demo as tok_demo
        tok_demo()
    except Exception as e:
        print(f"  [tokenization_demo] {e}")

    try:
        from chapters.ch01_text_semantics_tokens.vector_embeddings import run_demo as vec_demo
        vec_demo()
    except Exception as e:
        print(f"  [vector_embeddings] {e}")

    try:
        from chapters.ch01_text_semantics_tokens.attention_weights import run_demo as attn_demo
        attn_demo()
    except Exception as e:
        print(f"  [attention_weights] {e}")


def run_chapter_2():
    """Chapter 2: Training Paradigms & Core Engines"""
    separator("CHAPTER 2 — Training Paradigms & Core Engines")
    try:
        from chapters.ch02_training_engines.self_supervised_mask import run_demo as mask_demo
        mask_demo()
    except Exception as e:
        print(f"  [self_supervised_mask] {e}")

    try:
        from chapters.ch02_training_engines.transformer_block import run_demo as xfmr_demo
        xfmr_demo()
    except Exception as e:
        print(f"  [transformer_block] {e}")


def run_chapter_3():
    """Chapter 3: Dynamic Runtime & Context Engineering"""
    separator("CHAPTER 3 — Dynamic Runtime & Context Engineering")
    try:
        from chapters.ch03_runtime_context.few_shot_templates import run_demo as fst_demo
        fst_demo()
    except Exception as e:
        print(f"  [few_shot_templates] {e}")

    try:
        from chapters.ch03_runtime_context.rag_pipeline import run_demo as rag_demo
        rag_demo()
    except Exception as e:
        print(f"  [rag_pipeline] {e}")

    try:
        from chapters.ch03_runtime_context.vector_db_client import run_demo as vdb_demo
        vdb_demo()
    except Exception as e:
        print(f"  [vector_db_client] {e}")

    try:
        from chapters.ch03_runtime_context.context_manager import run_demo as ctx_demo
        ctx_demo()
    except Exception as e:
        print(f"  [context_manager] {e}")


def run_chapter_4():
    """Chapter 4: Autonomy, Logic, and Reasoning"""
    separator("CHAPTER 4 — Autonomy, Logic, and Reasoning")
    try:
        from chapters.ch04_agents_reasoning.agent_orchestrator import run_demo as agent_demo
        agent_demo()
    except Exception as e:
        print(f"  [agent_orchestrator] {e}")

    try:
        from chapters.ch04_agents_reasoning.rlhf_reward_simulation import run_demo as rlhf_demo
        rlhf_demo()
    except Exception as e:
        print(f"  [rlhf_reward_simulation] {e}")

    try:
        from chapters.ch04_agents_reasoning.chain_of_thought_specs import run_demo as cot_demo
        cot_demo()
    except Exception as e:
        print(f"  [chain_of_thought_specs] {e}")


def run_chapter_5():
    """Chapter 5: Systems Optimization & Cost Management"""
    separator("CHAPTER 5 — Systems Optimization & Cost Management")
    try:
        from chapters.ch05_optimization_efficiency.slm_benchmarks import run_demo as slm_demo
        slm_demo()
    except Exception as e:
        print(f"  [slm_benchmarks] {e}")

    try:
        from chapters.ch05_optimization_efficiency.model_distillation import run_demo as dist_demo
        dist_demo()
    except Exception as e:
        print(f"  [model_distillation] {e}")

    try:
        from chapters.ch05_optimization_efficiency.quantization_fixtures import run_demo as quant_demo
        quant_demo()
    except Exception as e:
        print(f"  [quantization_fixtures] {e}")


def main():
    """Execute all chapter demos or a specific chapter."""
    print("╔" + "═" * 70 + "╗")
    print("║" + " AI ENGINEERING MASTERCLASS — Capstone Application ".center(70) + "║")
    print("║" + " From Tokens to Production Systems ".center(70) + "║")
    print("╚" + "═" * 70 + "╝")

    # Parse command-line arguments
    chapters = {
        "1": ("Chapter 1: Text, Semantics, Tokens", run_chapter_1),
        "2": ("Chapter 2: Training & Engines", run_chapter_2),
        "3": ("Chapter 3: Runtime & Context", run_chapter_3),
        "4": ("Chapter 4: Agents & Reasoning", run_chapter_4),
        "5": ("Chapter 5: Optimization", run_chapter_5),
    }

    if len(sys.argv) > 1:
        selection = sys.argv[1]
        if selection in chapters:
            name, fn = chapters[selection]
            print(f"\n  Running: {name}")
            fn()
        elif selection == "all":
            for key in sorted(chapters.keys()):
                _, fn = chapters[key]
                fn()
        else:
            print(f"\n  Usage: python main.py [1|2|3|4|5|all]")
            print(f"\n  Available chapters:")
            for key, (name, _) in chapters.items():
                print(f"    {key}: {name}")
    else:
        print("\n  Available chapters:")
        for key, (name, _) in chapters.items():
            print(f"    {key}: {name}")
        print(f"\n  Usage:")
        print(f"    python main.py 1       # Run Chapter 1 only")
        print(f"    python main.py all     # Run all chapters")
        print(f"\n  Running all chapters...\n")
        for key in sorted(chapters.keys()):
            _, fn = chapters[key]
            fn()

    print(f"\n{'═' * 72}")
    print("  ✅ Capstone execution complete.")
    print("═" * 72)


if __name__ == "__main__":
    main()
