# AI Engineering Masterclass

> **A production-grade learning repository covering the complete architecture of modern AI systems — from raw tokens to deployed agent frameworks.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

---

## 🎯 What Is This?

This repository is a self-contained, hands-on textbook that teaches the **core architectures of modern AI** through working code, rigorous explanations, and production engineering insights. Every concept is accompanied by a functional Python script you can run immediately — no API keys, no cloud accounts, no GPU required.

**Target audience:** Software engineers transitioning to AI/ML engineering who want to understand *how things actually work under the hood*, not just how to call an API.

---

## 📚 Repository Structure

```
ai-engineering-masterclass/
│
├── AI_ENGINEERING_MASTERCLASS.md       # Complete textbook (20 topics, LaTeX equations)
├── README.md                           # You are here
│
├── chapters/
│   ├── ch01_text_semantics_tokens/     # Foundations: tokenization, vectors, attention
│   │   ├── tokenization_demo.py        # BPE, morphological, and whitespace tokenizers
│   │   ├── vector_embeddings.py        # Cosine similarity, nearest neighbours, analogies
│   │   └── attention_weights.py        # "Apple" disambiguation via scaled dot-product attention
│   │
│   ├── ch02_training_engines/          # Training paradigms: SSL, Transformers, fine-tuning
│   │   ├── self_supervised_mask.py     # BERT-style masking pipeline with loss computation
│   │   ├── transformer_block.py        # Multi-head attention + feedforward from scratch
│   │   └── finetuning_dataset.jsonl    # 5-row production JSONL for supervised alignment
│   │
│   ├── ch03_runtime_context/           # Runtime: prompting, RAG, vector DBs, context mgmt
│   │   ├── few_shot_templates.py       # Template registry with token budgets
│   │   ├── rag_pipeline.py             # End-to-end retrieval-augmented generation
│   │   ├── vector_db_client.py         # HNSW approximate nearest-neighbour search
│   │   ├── mcp_server/
│   │   │   └── readme.md               # Model Context Protocol specification
│   │   └── context_manager.py          # Sliding window + summary compression
│   │
│   ├── ch04_agents_reasoning/          # Agents: orchestration, RLHF, chain-of-thought
│   │   ├── agent_orchestrator.py       # ReAct loop with tool registry
│   │   ├── rlhf_reward_simulation.py   # PPO training with reward scoring
│   │   └── chain_of_thought_specs.py   # Step-validated reasoning chains
│   │
│   └── ch05_optimization_efficiency/   # Optimization: SLMs, distillation, quantization
│       ├── slm_benchmarks.py           # Model comparison tables and cost analysis
│       ├── model_distillation.py       # KL-divergence teacher-student training
│       └── quantization_fixtures.py    # FP32 → INT8 with symmetric/asymmetric modes
│
└── capstone_project/
    ├── app/                            # Application modules (extensible)
    ├── config/                         # Configuration files (extensible)
    └── main.py                         # CLI entry point linking all chapters
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (standard library only — zero external dependencies)
- Any operating system (Linux, macOS, Windows)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ai-engineering-masterclass.git
cd ai-engineering-masterclass

# No pip install needed — all scripts use Python standard library only!
```

### Run Individual Demos

```bash
# Chapter 1: Tokenization
python chapters/ch01_text_semantics_tokens/tokenization_demo.py

# Chapter 1: Vector Embeddings
python chapters/ch01_text_semantics_tokens/vector_embeddings.py

# Chapter 1: Attention Mechanism
python chapters/ch01_text_semantics_tokens/attention_weights.py

# Chapter 2: Self-Supervised Masking
python chapters/ch02_training_engines/self_supervised_mask.py

# Chapter 2: Transformer Architecture
python chapters/ch02_training_engines/transformer_block.py

# Chapter 3: Few-Shot Prompting
python chapters/ch03_runtime_context/few_shot_templates.py

# Chapter 3: RAG Pipeline
python chapters/ch03_runtime_context/rag_pipeline.py

# Chapter 3: Vector Database (HNSW)
python chapters/ch03_runtime_context/vector_db_client.py

# Chapter 3: Context Window Management
python chapters/ch03_runtime_context/context_manager.py

# Chapter 4: Agent Orchestrator
python chapters/ch04_agents_reasoning/agent_orchestrator.py

# Chapter 4: RLHF Simulation
python chapters/ch04_agents_reasoning/rlhf_reward_simulation.py

# Chapter 4: Chain of Thought
python chapters/ch04_agents_reasoning/chain_of_thought_specs.py

# Chapter 5: SLM Benchmarks
python chapters/ch05_optimization_efficiency/slm_benchmarks.py

# Chapter 5: Knowledge Distillation
python chapters/ch05_optimization_efficiency/model_distillation.py

# Chapter 5: Quantization
python chapters/ch05_optimization_efficiency/quantization_fixtures.py
```

### Run the Capstone (All Chapters)

```bash
# Run all chapters
python capstone_project/main.py all

# Run a specific chapter
python capstone_project/main.py 1    # Chapter 1 only
python capstone_project/main.py 3    # Chapter 3 only
```

---

## 📖 Learning Path

| Phase | Chapter | Topics | Duration |
|-------|---------|--------|----------|
| **Foundation** | Ch 1 | LLMs, Tokenization, Vectors, Attention | 2-3 hours |
| **Training** | Ch 2 | Self-Supervised Learning, Transformers, Fine-Tuning | 2-3 hours |
| **Runtime** | Ch 3 | Prompting, RAG, Vector DBs, MCP, Context Engineering | 3-4 hours |
| **Reasoning** | Ch 4 | Agents, RLHF, Chain of Thought, Reasoning Models | 2-3 hours |
| **Production** | Ch 5 | SLMs, Distillation, Quantization | 2-3 hours |

**Total estimated study time: 12-16 hours**

---

## 🏗️ Design Principles

1. **Zero Dependencies**: Every script runs with Python's standard library. No `pip install` required.
2. **Functional Code**: No TODO blocks, no placeholder functions. Every script produces output.
3. **Production Patterns**: Code follows real-world architectural patterns used in production AI systems.
4. **Progressive Complexity**: Each chapter builds on the previous one.
5. **Visual Output**: Every demo prints formatted tables, diagrams, and analysis to the terminal.

---

## 📝 The Textbook

The companion textbook [`AI_ENGINEERING_MASTERCLASS.md`](./AI_ENGINEERING_MASTERCLASS.md) provides:

- **20 deep-dive topics** covering the full AI engineering stack
- **Intuitive analogies** making complex concepts accessible
- **LaTeX equations** for mathematical precision
- **Production tips and critical pitfalls** from real-world experience
- **Architecture diagrams** for system-level understanding

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-topic`)
3. Ensure all scripts run without errors
4. Submit a pull request with clear documentation

---

## 📄 License

MIT License — see [LICENSE](./LICENSE) for details.
