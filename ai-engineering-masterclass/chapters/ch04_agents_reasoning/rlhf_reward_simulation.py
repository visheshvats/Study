#!/usr/bin/env python3
"""
RLHF Reward Simulation — Path Scoring & Policy Gradient Optimization
======================================================================
Simulates Reinforcement Learning from Human Feedback (RLHF):

  1. Multiple candidate response paths are generated
  2. A reward model scores each path based on human preferences (+1 / -1)
  3. Policy gradients adjust generation probabilities toward higher-reward paths
  4. Demonstrates why RL optimizes surface patterns, not causal understanding

Run:
    python rlhf_reward_simulation.py
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

random.seed(42)


# ── Data Types ──────────────────────────────────────────────────────────────
@dataclass
class GenerationPath:
    """A single candidate response with token-level probabilities."""
    path_id: str
    tokens: List[str]
    log_probs: List[float]     # Log-probability of each token under the policy
    reward: float = 0.0        # Reward signal from human/reward model

    @property
    def total_log_prob(self) -> float:
        return sum(self.log_probs)

    @property
    def text(self) -> str:
        return " ".join(self.tokens)


@dataclass
class RewardSignal:
    """A human preference comparison between two responses."""
    preferred_id: str
    rejected_id: str
    score: float  # +1 for preferred, -1 for rejected
    feedback: str = ""


@dataclass
class PolicyUpdate:
    """A single gradient update to the policy."""
    path_id: str
    advantage: float
    gradient_magnitude: float
    direction: str  # "reinforce" or "suppress"


# ── Reward Model ───────────────────────────────────────────────────────────
class RewardModel:
    """
    Simulates a reward model trained on human preference data.
    Scores responses based on heuristic quality signals.
    """

    def __init__(self):
        # Positive quality signals
        self.positive_signals = [
            "accurate", "helpful", "clear", "detailed", "concise",
            "relevant", "safe", "factual", "structured", "step",
        ]
        # Negative quality signals
        self.negative_signals = [
            "wrong", "harmful", "vague", "verbose", "irrelevant",
            "unsafe", "hallucinated", "confused", "error", "incorrect",
        ]

    def score(self, path: GenerationPath) -> float:
        """
        Score a generation path on a scale of [-1, +1].
        In production, this is a trained neural network.
        """
        text = path.text.lower()
        score = 0.0

        # Count quality signals
        for signal in self.positive_signals:
            if signal in text:
                score += 0.2

        for signal in self.negative_signals:
            if signal in text:
                score -= 0.3

        # Reward appropriate length (penalize too short or too long)
        token_count = len(path.tokens)
        if 8 <= token_count <= 25:
            score += 0.1
        elif token_count > 40:
            score -= 0.15

        # Clamp to [-1, 1]
        return max(-1.0, min(1.0, score))

    def compare(self, path_a: GenerationPath, path_b: GenerationPath) -> RewardSignal:
        """Compare two paths and return a preference signal."""
        score_a = self.score(path_a)
        score_b = self.score(path_b)

        if score_a >= score_b:
            return RewardSignal(
                preferred_id=path_a.path_id,
                rejected_id=path_b.path_id,
                score=1.0,
                feedback=f"Path A ({score_a:.3f}) preferred over Path B ({score_b:.3f})",
            )
        else:
            return RewardSignal(
                preferred_id=path_b.path_id,
                rejected_id=path_a.path_id,
                score=1.0,
                feedback=f"Path B ({score_b:.3f}) preferred over Path A ({score_a:.3f})",
            )


# ── Policy (Token Generator) ──────────────────────────────────────────────
class TokenPolicy:
    """
    Represents the LLM's generation policy — a probability distribution
    over the vocabulary at each position.
    """

    def __init__(self, vocab: List[str], learning_rate: float = 0.01):
        self.vocab = vocab
        self.lr = learning_rate
        # Token preferences: higher = more likely to be generated
        self.preferences: Dict[str, float] = {w: 0.0 for w in vocab}
        self._update_history: List[PolicyUpdate] = []

    def generate_path(self, path_id: str, length: int = 15) -> GenerationPath:
        """Sample a generation path from the current policy."""
        tokens: List[str] = []
        log_probs: List[float] = []

        for _ in range(length):
            # Compute softmax probabilities
            scores = [self.preferences[w] + random.gauss(0, 0.3) for w in self.vocab]
            probs = self._softmax(scores)

            # Sample a token
            r = random.random()
            cumulative = 0.0
            selected_idx = 0
            for i, p in enumerate(probs):
                cumulative += p
                if r <= cumulative:
                    selected_idx = i
                    break

            tokens.append(self.vocab[selected_idx])
            log_probs.append(math.log(max(probs[selected_idx], 1e-10)))

        return GenerationPath(path_id=path_id, tokens=tokens, log_probs=log_probs)

    def update(self, path: GenerationPath, advantage: float) -> PolicyUpdate:
        """
        REINFORCE-style policy gradient update.

        ∇J(θ) ≈ Σ_t [ ∇log π(a_t|s_t) × A_t ]

        If advantage > 0: increase probability of these tokens
        If advantage < 0: decrease probability of these tokens
        """
        gradient_mag = 0.0
        for token in path.tokens:
            delta = self.lr * advantage
            self.preferences[token] += delta
            gradient_mag += abs(delta)

        direction = "reinforce" if advantage > 0 else "suppress"
        update = PolicyUpdate(
            path_id=path.path_id,
            advantage=advantage,
            gradient_magnitude=gradient_mag,
            direction=direction,
        )
        self._update_history.append(update)
        return update

    def top_tokens(self, k: int = 10) -> List[Tuple[str, float]]:
        """Return the top-k most preferred tokens."""
        sorted_prefs = sorted(self.preferences.items(), key=lambda x: x[1], reverse=True)
        return sorted_prefs[:k]

    @staticmethod
    def _softmax(scores: List[float]) -> List[float]:
        max_s = max(scores)
        exps = [math.exp(s - max_s) for s in scores]
        total = sum(exps)
        return [e / total for e in exps]


# ── PPO Trainer (Simplified) ──────────────────────────────────────────────
class PPOTrainer:
    """
    Simplified Proximal Policy Optimization loop for RLHF.

    Full PPO clips the probability ratio to prevent destructive updates:
        L_clip = min(r(θ) × A, clip(r(θ), 1-ε, 1+ε) × A)
    """

    def __init__(
        self,
        policy: TokenPolicy,
        reward_model: RewardModel,
        clip_epsilon: float = 0.2,
        kl_penalty: float = 0.01,
    ):
        self.policy = policy
        self.reward_model = reward_model
        self.clip_epsilon = clip_epsilon
        self.kl_penalty = kl_penalty
        self._training_log: List[Dict] = []

    def train_step(self, num_candidates: int = 4) -> Dict:
        """
        One PPO training step:
          1. Generate N candidate paths
          2. Score each with reward model
          3. Compute advantages (score - baseline)
          4. Update policy toward high-reward paths
        """
        # Generate candidates
        paths = [
            self.policy.generate_path(f"path_{i}", length=random.randint(10, 20))
            for i in range(num_candidates)
        ]

        # Score
        for path in paths:
            path.reward = self.reward_model.score(path)

        # Baseline = mean reward
        baseline = sum(p.reward for p in paths) / len(paths)

        # Update policy
        updates: List[PolicyUpdate] = []
        for path in paths:
            advantage = path.reward - baseline
            # KL penalty to prevent divergence from reference policy
            advantage -= self.kl_penalty * abs(path.total_log_prob)
            update = self.policy.update(path, advantage)
            updates.append(update)

        step_log = {
            "rewards": [p.reward for p in paths],
            "mean_reward": sum(p.reward for p in paths) / len(paths),
            "baseline": baseline,
            "updates": [(u.path_id, u.direction, f"{u.advantage:.4f}") for u in updates],
        }
        self._training_log.append(step_log)
        return step_log


# ── Demo ────────────────────────────────────────────────────────────────────
def run_demo() -> None:
    print("=" * 72)
    print("RLHF REWARD SIMULATION — Policy Gradient Optimization")
    print("=" * 72)

    # Vocabulary (mix of positive, negative, and neutral tokens)
    vocab = [
        "the", "answer", "is", "a", "detailed", "accurate", "clear",
        "step", "by", "helpful", "response", "to", "your", "question",
        "however", "note", "that", "incorrect", "wrong", "vague",
        "confused", "error", "harmful", "please", "consider", "following",
    ]

    # Initialize components
    policy = TokenPolicy(vocab, learning_rate=0.05)
    reward_model = RewardModel()
    trainer = PPOTrainer(policy, reward_model)

    # Training loop
    num_epochs = 8
    print(f"\n  Training for {num_epochs} epochs ({4} candidates per step)")
    print(f"  {'─' * 55}")

    for epoch in range(num_epochs):
        step_log = trainer.train_step(num_candidates=4)
        rewards = step_log["rewards"]
        mean_r = step_log["mean_reward"]
        bar = "█" * int((mean_r + 1) * 15)  # Scale [-1,1] to bar length
        print(f"  Epoch {epoch + 1:2d} | mean_reward={mean_r:+.4f} | "
              f"range=[{min(rewards):+.3f}, {max(rewards):+.3f}] | {bar}")

    # Show learned token preferences
    print(f"\n  {'─' * 55}")
    print("  LEARNED TOKEN PREFERENCES (after RLHF):")
    top = policy.top_tokens(k=15)
    for token, pref in top:
        direction = "▲" if pref > 0 else "▼" if pref < 0 else "─"
        bar = "█" * int(abs(pref) * 50)
        print(f"    {direction} {token:>12s}  {pref:+.4f}  {bar}")

    # Pairwise comparison demo
    print(f"\n  {'─' * 55}")
    print("  PAIRWISE PREFERENCE COMPARISON:")
    path_a = policy.generate_path("good_response", length=12)
    path_b = policy.generate_path("bad_response", length=12)
    path_a.reward = reward_model.score(path_a)
    path_b.reward = reward_model.score(path_b)
    comparison = reward_model.compare(path_a, path_b)

    print(f"    Path A: \"{path_a.text[:60]}...\"")
    print(f"      Score: {path_a.reward:+.4f}")
    print(f"    Path B: \"{path_b.text[:60]}...\"")
    print(f"      Score: {path_b.reward:+.4f}")
    print(f"    Verdict: {comparison.feedback}")

    # Critical insight: RL limitations
    print(f"\n{'═' * 72}")
    print("  CRITICAL INSIGHT — WHY RL DOESN'T CREATE UNDERSTANDING:")
    print("  ─────────────────────────────────────────────────────────")
    print("  RLHF optimizes the surface distribution of token sequences")
    print("  that humans rate highly. It does NOT build causal models.")
    print("")
    print("  Example: 'What is the probability of heads on a fair coin?'")
    print("  • The model learns to output '0.5' because that token sequence")
    print("    receives high reward, NOT because it understands probability.")
    print("  • It cannot simulate flipping a coin — it pattern-matches the")
    print("    statistical correlation between 'fair coin' and '0.5'.")
    print("")
    print("  RL adjusts WHICH tokens are generated, not WHETHER the model")
    print("  comprehends the physical or mathematical reality behind them.")
    print("═" * 72)


if __name__ == "__main__":
    run_demo()
