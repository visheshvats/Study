#!/usr/bin/env python3
"""
Model Distillation — Teacher-Student Knowledge Transfer Simulation
====================================================================
Simulates the knowledge distillation process where a large "teacher" model
transfers its learned representations to a smaller "student" model by:

  1. Generating soft probability targets (softmax with temperature)
  2. Computing Kullback-Leibler (KL) divergence between distributions
  3. Optimizing the student via a combined hard + soft target loss
  4. Tracking convergence across training epochs

Run:
    python model_distillation.py
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

random.seed(42)


# ── Type Aliases ───────────────────────────────────────────────────────────
Distribution = List[float]  # Probability distribution over vocabulary


# ── Temperature-Scaled Softmax ─────────────────────────────────────────────
def softmax(logits: List[float], temperature: float = 1.0) -> Distribution:
    """
    Softmax with temperature scaling.

    σ(z_i) = exp(z_i / T) / Σ_j exp(z_j / T)

    Higher temperature → softer (more uniform) distribution
    Lower temperature  → sharper (more peaked) distribution
    T = 1.0 → standard softmax
    """
    scaled = [z / temperature for z in logits]
    max_val = max(scaled)
    exps = [math.exp(z - max_val) for z in scaled]
    total = sum(exps)
    return [e / total for e in exps]


# ── KL Divergence ──────────────────────────────────────────────────────────
def kl_divergence(p: Distribution, q: Distribution) -> float:
    """
    Kullback-Leibler divergence: D_KL(P || Q) = Σ P(x) · log(P(x) / Q(x))

    Measures how much information is lost when Q is used to approximate P.
    Always ≥ 0; equals 0 only when P == Q.
    """
    kl = 0.0
    for pi, qi in zip(p, q):
        if pi > 1e-10 and qi > 1e-10:
            kl += pi * math.log(pi / qi)
    return kl


# ── Cross-Entropy Loss ────────────────────────────────────────────────────
def cross_entropy(target_idx: int, predictions: Distribution) -> float:
    """Standard cross-entropy loss against a hard label."""
    return -math.log(max(predictions[target_idx], 1e-10))


# ── Distillation Loss ─────────────────────────────────────────────────────
def distillation_loss(
    student_logits: List[float],
    teacher_logits: List[float],
    hard_label: int,
    temperature: float = 4.0,
    alpha: float = 0.7,
) -> Tuple[float, float, float]:
    """
    Combined distillation loss:

    L = α · T² · D_KL(teacher_soft || student_soft) + (1 - α) · CE(hard_label, student)

    where:
      α     = weight on soft targets (typically 0.5–0.9)
      T     = temperature for softening distributions
      T²    = scaling factor to match gradient magnitudes

    Returns: (total_loss, soft_loss, hard_loss)
    """
    # Soft targets from teacher and student
    teacher_soft = softmax(teacher_logits, temperature)
    student_soft = softmax(student_logits, temperature)

    # KL divergence (soft target loss)
    soft_loss = kl_divergence(teacher_soft, student_soft) * (temperature ** 2)

    # Cross-entropy (hard target loss)
    student_hard = softmax(student_logits, temperature=1.0)
    hard_loss = cross_entropy(hard_label, student_hard)

    # Combined loss
    total = alpha * soft_loss + (1 - alpha) * hard_loss

    return total, soft_loss, hard_loss


# ── Mock Models ────────────────────────────────────────────────────────────
@dataclass
class MockModel:
    """A simplified neural network represented by logit biases."""
    name: str
    parameter_count: str
    vocab_size: int
    logit_biases: List[float] = field(default_factory=list)
    learning_rate: float = 0.1

    def __post_init__(self):
        if not self.logit_biases:
            self.logit_biases = [random.gauss(0, 0.5) for _ in range(self.vocab_size)]

    def predict(self, input_features: List[float]) -> List[float]:
        """Generate logits (simplified: bias + input dot product effect)."""
        # Simple: logits = biases + small perturbation from input
        logits = [
            b + sum(f * random.gauss(0, 0.1) for f in input_features[:3])
            for b in self.logit_biases
        ]
        return logits

    def update(self, gradients: List[float]) -> None:
        """Apply gradient updates to biases."""
        for i in range(len(self.logit_biases)):
            self.logit_biases[i] -= self.learning_rate * gradients[i]


def create_teacher(vocab_size: int) -> MockModel:
    """Create a well-trained teacher model (strong, peaked distributions)."""
    teacher = MockModel("GPT-4-Teacher", "200B", vocab_size, learning_rate=0.0)
    # Teacher has learned strong preferences
    teacher.logit_biases = [random.gauss(0, 2.0) for _ in range(vocab_size)]
    return teacher


def create_student(vocab_size: int) -> MockModel:
    """Create an untrained student model (weak, flat distributions)."""
    return MockModel("Phi-3-Student", "3.8B", vocab_size, learning_rate=0.15)


# ── Training Loop ─────────────────────────────────────────────────────────
@dataclass
class TrainingMetrics:
    epoch: int
    total_loss: float
    soft_loss: float
    hard_loss: float
    kl_div: float
    student_accuracy: float
    teacher_accuracy: float


def train_distillation(
    teacher: MockModel,
    student: MockModel,
    training_data: List[Tuple[List[float], int]],  # (input_features, hard_label)
    epochs: int = 20,
    temperature: float = 4.0,
    alpha: float = 0.7,
) -> List[TrainingMetrics]:
    """Run the distillation training loop."""
    history: List[TrainingMetrics] = []

    for epoch in range(epochs):
        epoch_total, epoch_soft, epoch_hard = 0.0, 0.0, 0.0
        student_correct, teacher_correct = 0, 0

        for features, label in training_data:
            teacher_logits = teacher.predict(features)
            student_logits = student.predict(features)

            # Compute loss
            total, soft, hard = distillation_loss(
                student_logits, teacher_logits, label, temperature, alpha
            )
            epoch_total += total
            epoch_soft += soft
            epoch_hard += hard

            # Check accuracy
            teacher_pred = max(range(len(teacher_logits)), key=lambda i: teacher_logits[i])
            student_pred = max(range(len(student_logits)), key=lambda i: student_logits[i])
            if teacher_pred == label:
                teacher_correct += 1
            if student_pred == label:
                student_correct += 1

            # Compute pseudo-gradients (simplified)
            teacher_soft = softmax(teacher_logits, temperature)
            student_soft = softmax(student_logits, temperature)
            gradients = [
                alpha * (sq - tq) * temperature + (1 - alpha) * (sq - (1.0 if i == label else 0.0))
                for i, (sq, tq) in enumerate(zip(student_soft, teacher_soft))
            ]
            student.update(gradients)

        # Compute KL divergence on last example
        teacher_dist = softmax(teacher.predict(training_data[-1][0]))
        student_dist = softmax(student.predict(training_data[-1][0]))
        kl = kl_divergence(teacher_dist, student_dist)

        n = len(training_data)
        metrics = TrainingMetrics(
            epoch=epoch + 1,
            total_loss=epoch_total / n,
            soft_loss=epoch_soft / n,
            hard_loss=epoch_hard / n,
            kl_div=kl,
            student_accuracy=student_correct / n,
            teacher_accuracy=teacher_correct / n,
        )
        history.append(metrics)

    return history


# ── Demo ────────────────────────────────────────────────────────────────────
def run_demo() -> None:
    print("=" * 72)
    print("MODEL DISTILLATION — Teacher-Student Knowledge Transfer")
    print("=" * 72)

    vocab_size = 10
    vocab = [f"tok_{i}" for i in range(vocab_size)]

    # Create models
    teacher = create_teacher(vocab_size)
    student = create_student(vocab_size)

    print(f"\n  Teacher: {teacher.name} ({teacher.parameter_count} params)")
    print(f"  Student: {student.name} ({student.parameter_count} params)")
    print(f"  Vocab  : {vocab_size} tokens")

    # 1. Temperature effect
    print(f"\n{'─' * 60}")
    print("  TEMPERATURE EFFECT ON SOFTMAX DISTRIBUTION:")
    print(f"{'─' * 60}")
    sample_logits = [2.5, 1.0, 0.5, -0.5, -1.0, 0.8, 1.5, -0.2, 0.3, -1.5]
    for T in [0.5, 1.0, 2.0, 4.0, 8.0]:
        dist = softmax(sample_logits, T)
        bar = " ".join(f"{p:.3f}" for p in dist)
        entropy = -sum(p * math.log(max(p, 1e-10)) for p in dist)
        print(f"  T={T:<4.1f}  H={entropy:.3f}  [{bar}]")

    # 2. Generate training data
    training_data: List[Tuple[List[float], int]] = []
    for _ in range(50):
        features = [random.gauss(0, 1) for _ in range(5)]
        # Teacher's predicted label (what teacher would output)
        teacher_logits = teacher.predict(features)
        label = max(range(vocab_size), key=lambda i: teacher_logits[i])
        training_data.append((features, label))

    # 3. Train
    print(f"\n{'─' * 60}")
    print("  DISTILLATION TRAINING (T=4.0, α=0.7)")
    print(f"{'─' * 60}")
    print(f"  {'Epoch':>5s}  {'Total':>8s}  {'Soft':>8s}  {'Hard':>8s}  "
          f"{'KL Div':>8s}  {'Student':>8s}  {'Teacher':>8s}")
    print(f"  {'─' * 55}")

    history = train_distillation(
        teacher, student, training_data,
        epochs=20, temperature=4.0, alpha=0.7,
    )

    for m in history:
        bar = "█" * int(m.student_accuracy * 20)
        print(f"  {m.epoch:>5d}  {m.total_loss:>8.4f}  {m.soft_loss:>8.4f}  {m.hard_loss:>8.4f}  "
              f"{m.kl_div:>8.4f}  {m.student_accuracy:>7.0%}  {m.teacher_accuracy:>7.0%}  {bar}")

    # 4. Final comparison
    print(f"\n{'─' * 60}")
    print("  FINAL DISTRIBUTION COMPARISON (last training example):")
    print(f"{'─' * 60}")
    features, label = training_data[-1]
    teacher_logits = teacher.predict(features)
    student_logits = student.predict(features)
    teacher_dist = softmax(teacher_logits)
    student_dist = softmax(student_logits)

    print(f"  {'Token':<8s}  {'Teacher':>8s}  {'Student':>8s}  {'Delta':>8s}")
    for i in range(vocab_size):
        delta = student_dist[i] - teacher_dist[i]
        marker = " ◀─ target" if i == label else ""
        print(f"  {vocab[i]:<8s}  {teacher_dist[i]:>8.4f}  {student_dist[i]:>8.4f}  "
              f"{delta:>+8.4f}{marker}")

    final_kl = kl_divergence(teacher_dist, student_dist)
    print(f"\n  Final KL Divergence: {final_kl:.6f}")
    print(f"  (0.0 = perfect match; lower = better)")

    # Architecture summary
    print(f"\n{'═' * 72}")
    print("  DISTILLATION ARCHITECTURE:")
    print("  ┌──────────────┐     Soft Targets (T>1)")
    print("  │   Teacher    │─────────────────────────┐")
    print("  │  (200B, FP16)│                         │")
    print("  └──────────────┘                         ▼")
    print("  ┌──────────────┐     ┌───────────────────────────────┐")
    print("  │   Student    │────▶│ Loss = α·T²·KL(teacher||student) │")
    print("  │  (3.8B, INT4)│     │      + (1-α)·CE(hard_label)     │")
    print("  └──────────────┘     └───────────────────────────────┘")
    print("                              │")
    print("                     ∇ Backpropagate gradients")
    print("                     to student weights only")
    print("═" * 72)


if __name__ == "__main__":
    run_demo()
