# Topic 19: Distillation

> **Java Analogy:** Distillation is like writing a comprehensive Javadoc from a senior architect's codebase, then having a junior developer build a new, simpler implementation guided by those docs. The junior (student model) doesn't copy the code — they learn the *patterns and decisions* that made the senior's (teacher model's) code work, and reproduce them in a smaller, faster package.

---

## What This Is (Plain English)

Knowledge distillation trains a small "student" model to mimic a large "teacher" model. But instead of just copying the teacher's final answers, the student learns from the teacher's complete probability distribution — including the relative confidence between all possible answers. If the teacher says "cat" with 80% confidence and "kitten" with 15%, the student learns that "cat" and "kitten" are related alternatives, while "refrigerator" at 0.001% is completely irrelevant. This "dark knowledge" transfers the teacher's understanding far more effectively than hard labels alone.

---

## Java Engineer's Mental Model

| AI Concept | Java Equivalent |
|---|---|
| **Teacher model** | The production `@Service` with all the business logic — large, battle-tested, expensive to run |
| **Student model** | A stripped-down `@Component` that handles 80% of cases at 10× speed |
| **Soft targets** | Instead of `assertTrue(result == "cat")`, it's `assertSoftDistribution({cat: 0.8, kitten: 0.15, dog: 0.04, ...})` |
| **Temperature** | Controls how much detail the teacher reveals. High T = teacher shares nuanced reasoning. Low T = teacher gives sharp answers. |
| **KL divergence** | `Math.abs(teacherDistribution - studentDistribution)` summed across all possibilities. 0 = perfect match. |
| **Combined loss** | `α × softTargetLoss + (1-α) × hardLabelLoss` — learn from both the teacher AND ground truth |

---

## The Core Concept

### Without Distillation (Hard Labels)
```
Input: "The cat sat on the ___"
Label: "mat" (100% weight)
→ Student learns: "mat" is correct, everything else is wrong
→ Learns nothing about "rug", "carpet", "floor" also being plausible
```

### With Distillation (Soft Labels from Teacher)
```
Input: "The cat sat on the ___"
Teacher output (at temperature T=4):
  mat: 0.35, rug: 0.20, carpet: 0.15, floor: 0.10, ...
→ Student learns: "mat" is best, but "rug/carpet/floor" are related alternatives
→ This relational knowledge transfers generalization ability
```

---

## The Math (Simplified for Engineers)

```
Distillation Loss = α × T² × KL(teacher_soft || student_soft) 
                  + (1-α) × CrossEntropy(hard_label, student)

Where:
  α = 0.7 (weight on soft targets — teacher matters more)
  T = 4.0 (temperature — soften the distributions)
  T² = gradient magnitude correction (16× scaling)
  KL = Kullback-Leibler divergence (measures distribution mismatch)
```

**Temperature effect:**
- T=1: Teacher outputs 95% on top token → student learns almost nothing from other tokens
- T=4: Teacher outputs 35% on top, 20% on second → student learns rich relationships
- T=8: Too flat → noise dominates

---

## Why This Matters to You

As a Java engineer, you'll encounter distillation in two ways:

1. **Using distilled models:** Phi-3, Gemma-2, and many SLMs are distilled from larger models. Knowing this helps you understand their strengths (inherited capabilities) and weaknesses (inherited biases).

2. **API-based distillation:** You can distill GPT-4 into a fine-tuned GPT-4o-mini by:
   a. Running GPT-4 on your dataset → collecting outputs
   b. Using those outputs as training data for GPT-4o-mini fine-tuning
   c. Result: GPT-4-quality responses at GPT-4o-mini prices

### Practical Distillation Pipeline in Java

```java
@Service
public class DistillationDataGenerator {
    private final ChatLanguageModel teacher;  // GPT-4o ($2.50/1M)
    // Student will be: GPT-4o-mini fine-tuned ($0.15/1M)

    /**
     * Generate training data for distillation.
     * Run teacher on your production query distribution.
     * Use outputs as fine-tuning data for the student.
     */
    public void generateTrainingData(
        List<String> productionQueries, 
        Path outputPath
    ) throws IOException {
        try (var writer = Files.newBufferedWriter(outputPath)) {
            for (String query : productionQueries) {
                // Get teacher's high-quality response
                String teacherResponse = teacher.generate(query);

                // Format as fine-tuning data
                var training = Map.of("messages", List.of(
                    Map.of("role", "system", "content", SYSTEM_PROMPT),
                    Map.of("role", "user", "content", query),
                    Map.of("role", "assistant", "content", teacherResponse)
                ));

                writer.write(objectMapper.writeValueAsString(training));
                writer.newLine();
            }
        }
        // Upload this JSONL to OpenAI and fine-tune gpt-4o-mini
    }
}
```

---

## Distillation Approaches

| Approach | How It Works | When to Use |
|---|---|---|
| **Response distillation** | Student mimics teacher's final outputs | Simplest, most common. Use API-based teachers (GPT-4). |
| **Feature distillation** | Student mimics teacher's internal hidden states | Requires access to teacher weights. Academic/research use. |
| **On-policy distillation** | Generate data from student's mistakes, have teacher correct them | Best quality — focuses on student's actual weaknesses. |
| **Synthetic data distillation** | Teacher generates diverse training data from scratch | Useful when you lack real query data. |

---

## Cost-Benefit Calculation

```
Before distillation:
  GPT-4o at $2.50/1M tokens × 10M queries/month × 1K tokens/query
  = $25,000/month

After distillation (GPT-4o-mini fine-tuned):
  $0.30/1M tokens × 10M queries/month × 1K tokens/query
  = $3,000/month

Savings: $22,000/month = $264,000/year
One-time distillation cost: ~$500 (teacher API calls + fine-tuning)
ROI payback: < 1 day
```

---

## Interview-Ready Summary

- Distillation trains a small "student" model to mimic a large "teacher" model.
- Soft labels (teacher's full probability distribution) transfer richer knowledge than hard labels.
- Temperature scaling reveals the teacher's uncertainty and inter-class relationships.
- KL divergence measures how well the student matches the teacher's distribution.
- Practical approach: run GPT-4 on your queries → use outputs to fine-tune GPT-4o-mini.
- Cost savings can be 80-95% with minimal quality loss on targeted tasks.
- The student can never exceed the teacher on the training distribution — fix the teacher first if it has issues.
