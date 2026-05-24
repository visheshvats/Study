# 5. Relational Algebra & Calculus — GATE CSE Complete Guide

> **GATE Weightage:** 3–5 marks. One of the most frequently tested topics. Questions involve writing RA expressions, evaluating query results, computing output size, and understanding equivalences.

---

## Relational Algebra Overview

**Relational Algebra (RA)** is a **procedural query language** — it specifies **how** to retrieve data by defining a sequence of operations on relations. Each operation takes one or more relations as input and returns a new relation as output (**closure property**).

---

## Key Definitions & Concepts

### Fundamental Operations (6 Basic)

There are **6 fundamental** operations from which all other operations can be derived:

| # | Operation | Symbol | Type | Input |
|---|---|---|---|---|
| 1 | **Selection** | σ (sigma) | Unary | 1 relation |
| 2 | **Projection** | π (pi) | Unary | 1 relation |
| 3 | **Union** | ∪ | Binary | 2 relations |
| 4 | **Set Difference** | − | Binary | 2 relations |
| 5 | **Cartesian Product** | × | Binary | 2 relations |
| 6 | **Rename** | ρ (rho) | Unary | 1 relation |

### Derived Operations

| Operation | Symbol | Expressed Using Fundamentals |
|---|---|---|
| **Intersection** | ∩ | R ∩ S = R − (R − S) |
| **Natural Join** | ⋈ | σ (R × S) with equality on common attrs, then project |
| **Theta Join** | ⋈θ | σ_θ(R × S) |
| **Equi Join** | ⋈ (with =) | Theta join where θ uses only = |
| **Semi Join** | ⋉ | π_R(R ⋈ S) |
| **Anti Join** | ▷ | R − π_R(R ⋈ S) |
| **Division** | ÷ | Special operation for "for all" queries |
| **Outer Joins** | ⟕, ⟖, ⟗ | Left, Right, Full outer joins |

---

## Detailed Operation Descriptions

### 1. Selection (σ) — "Horizontal Filter"

Selects **rows (tuples)** satisfying a condition.

```
σ_condition(R)
```

- Condition can use: =, ≠, <, >, ≤, ≥, AND (∧), OR (∨), NOT (¬)
- **Commutative:** σ_c1(σ_c2(R)) = σ_c2(σ_c1(R)) = σ_(c1 ∧ c2)(R)
- **Idempotent:** σ_c(σ_c(R)) = σ_c(R)

**Output size:**
- If |R| = n, output has between **0 and n** tuples.
- **Degree stays the same** (same number of columns).

**Example:**
```
σ_(Age > 20 ∧ Dept = 'CS')(Student)
```
Selects all students older than 20 in CS department.

---

### 2. Projection (π) — "Vertical Filter"

Selects **columns (attributes)** and **removes duplicates**.

```
π_(A1, A2, ...)(R)
```

- **Removes duplicate tuples** from the result (since result is a set/relation).
- **NOT idempotent in general:** π_A(π_B(R)) ≠ π_A(R) unless A ⊆ B.
- Successive projections: π_L1(π_L2(R)) = π_L1(R) **only if** L1 ⊆ L2.

**Output size:**
- If |R| = n with k distinct values for the projected attributes → output has **k ≤ n** tuples.
- **Degree = number of projected attributes.**

**Example:**
```
π_(Name, Dept)(Student)
```
Lists unique (Name, Dept) combinations.

---

### 3. Union (∪)

Combines tuples from two **union-compatible** (same degree, compatible domains) relations.

```
R ∪ S
```

- **Removes duplicates** (set semantics).
- |R ∪ S| ranges from **max(|R|, |S|)** to **|R| + |S|** (when no overlap).
- **Commutative:** R ∪ S = S ∪ R
- **Associative:** (R ∪ S) ∪ T = R ∪ (S ∪ T)

---

### 4. Set Difference (−)

Tuples in R but NOT in S.

```
R − S
```

- |R − S| ranges from **0** (if R ⊆ S) to **|R|** (if no overlap).
- **NOT Commutative:** R − S ≠ S − R
- **NOT Associative**

---

### 5. Cartesian Product (×)

Every tuple in R paired with every tuple in S.

```
R × S
```

- **Output tuples:** |R × S| = |R| × |S|
- **Output degree:** degree(R) + degree(S)
- **Commutative and Associative**

---

### 6. Rename (ρ)

Renames a relation or its attributes.

```
ρ_S(R)           → Rename relation R to S
ρ_S(A,B,C)(R)    → Rename relation to S with attributes A, B, C
ρ_(A,B,C)(R)     → Rename only attributes
```

---

## Join Operations (Detailed)

### Natural Join (⋈)

- Combines R and S based on **equality of common attributes**.
- Automatically selects matching tuples and **removes duplicate columns**.

```
R ⋈ S = π_(all unique attrs)(σ_(R.common = S.common)(R × S))
```

**Output size:**
- Minimum: **0** (no matching tuples)
- Maximum: **|R| × |S|** (every tuple matches every other — all common attr values same)

**Special cases:**
- If R and S have **no common attributes:** R ⋈ S = R × S
- If R and S have **all attributes in common:** R ⋈ S = R ∩ S

> **⚠️ GATE Key Point:** Natural join automatically equates ALL common attribute names. You can't control which attributes are used.

---

### Theta Join (⋈θ)

```
R ⋈_(θ) S = σ_θ(R × S)
```
- θ can be any boolean condition.
- When θ uses only **equality (=)** → **Equi Join**.
- Equi join **does NOT** remove duplicate columns (unlike natural join).

---

### Outer Joins

Handle **dangling tuples** (tuples that don't match during join) by padding with NULLs.

| Type | Symbol | Preserves |
|---|---|---|
| **Left Outer Join** | ⟕ | All tuples from **left** relation |
| **Right Outer Join** | ⟖ | All tuples from **right** relation |
| **Full Outer Join** | ⟗ | All tuples from **both** relations |

**Output size of Full Outer Join:**
```
|R ⟗ S| = |R ⋈ S| + (dangling R tuples) + (dangling S tuples)
```
- Minimum: max(|R|, |S|)
- Maximum: |R| × |S| + |R| + |S| - ... (corner cases)

> **⚠️ GATE Pitfall:** In natural join, unmatched tuples are **lost**. Outer joins **preserve** them with NULLs.

---

### Division (÷) — "For All" Queries

R(A, B) ÷ S(B) returns all values of A in R that are associated with **every** value of B in S.

```
R ÷ S = π_A(R) − π_A((π_A(R) × S) − R)
```

**Example:**
- R = (Student, Course) — enrollment records
- S = (Course) — set of required courses
- R ÷ S = Students enrolled in **ALL** required courses

> **GATE Tip:** Division is the RA way to express **"for all"** or **universal quantification** queries.

---

## Mathematical Foundations

### Size Formulas (GATE Favourite)

| Operation | Min Tuples | Max Tuples |
|---|---|---|
| σ_c(R) | 0 | \|R\| |
| π_L(R) | 1 | \|R\| |
| R ∪ S | max(\|R\|, \|S\|) | \|R\| + \|S\| |
| R ∩ S | 0 | min(\|R\|, \|S\|) |
| R − S | 0 | \|R\| |
| R × S | \|R\| × \|S\| | \|R\| × \|S\| (always exact) |
| R ⋈ S | 0 | \|R\| × \|S\| |
| R ÷ S | 0 | \|R\| / \|S\| (integer) |

### Degree (Number of Columns)

| Operation | Degree |
|---|---|
| σ_c(R) | degree(R) |
| π_L(R) | \|L\| (number of projected attrs) |
| R ∪ S / R ∩ S / R − S | degree(R) = degree(S) |
| R × S | degree(R) + degree(S) |
| R ⋈ S (natural) | degree(R) + degree(S) − \|common attrs\| |
| R ⋈θ S (theta) | degree(R) + degree(S) |

---

## Equivalence Rules (Query Optimization)

These are used by the **query optimizer** and tested in GATE:

| Rule | Statement |
|---|---|
| **Selection cascade** | σ_(c1 ∧ c2)(R) = σ_c1(σ_c2(R)) |
| **Selection commutativity** | σ_c1(σ_c2(R)) = σ_c2(σ_c1(R)) |
| **Projection cascade** | π_L1(π_L2(R)) = π_L1(R) if L1 ⊆ L2 |
| **Selection-projection commute** | π_L(σ_c(R)) = σ_c(π_L(R)) if c involves only attrs in L |
| **Join commutativity** | R ⋈ S = S ⋈ R |
| **Join associativity** | (R ⋈ S) ⋈ T = R ⋈ (S ⋈ T) |
| **Selection pushdown** | σ_c(R ⋈ S) = σ_c(R) ⋈ S if c involves only R's attrs |
| **Projection pushdown** | π_L(R ⋈ S) can push projection inside join |
| **De Morgan's for selection** | σ_(¬(c1 ∧ c2))(R) = σ_(¬c1 ∨ ¬c2)(R) |

> **GATE Tip:** The most important optimization: **Push selection as far down** as possible (reduces intermediate relation size).

---

## Relational Calculus (Brief)

### Tuple Relational Calculus (TRC)

**Non-procedural** — specifies **what** to retrieve, not **how**.

```
{ t | P(t) }
```
"Set of all tuples t such that predicate P(t) is true."

**Example:** Find all students with Age > 20:
```
{ t | Student(t) ∧ t.Age > 20 }
```

### Domain Relational Calculus (DRC)

Uses **domain variables** (individual attribute values) instead of tuple variables.

```
{ <x1, x2, ...> | P(x1, x2, ...) }
```

**Example:**
```
{ <n, a> | ∃r (Student(r, n, a) ∧ a > 20) }
```

### Safe Expressions
- A TRC/DRC expression is **safe** if it is guaranteed to produce a **finite result**.
- **Unsafe** expressions can potentially produce infinite results.
- Only **safe** expressions are allowed.

### Codd's Theorem
> **Relational Algebra = Safe Tuple Relational Calculus = Safe Domain Relational Calculus**
> All three have the **same expressive power**.

> **⚠️ GATE Point:** RA **cannot** express **recursive queries** (e.g., transitive closure), **aggregation**, or **sorting**. These require extensions.

---

## GATE Specific Focus Points

### 1. Expressing Queries in RA

**"Find students enrolled in ALL courses"** → Use **Division (÷)**

**"Find students NOT enrolled in any course"** → Use **Difference (−)**
```
π_StudentID(Student) − π_StudentID(Enrolls)
```

**"Find students enrolled in at least one course taught by Prof X"** → Use **Join + Selection + Projection**
```
π_StudentID(σ_(Instructor='X')(Enrolls ⋈ Course))
```

### 2. Counting Operations Output

This is a very common GATE question: "How many tuples in the result?"

**Trick:** Track carefully:
- Selection can only **reduce** tuples
- Projection can only **reduce** tuples (duplicate removal)
- Cross product **multiplies** tuples
- Union can yield between max(m,n) and m+n
- Natural join: between 0 and m×n

### 3. Monotone Operations

An operation is **monotone** if adding tuples to input can only add (or maintain) tuples in output.

| Monotone | Non-Monotone |
|---|---|
| σ, π, ∪, ×, ⋈ | − (set difference) |

> **GATE Tip:** Set difference is the **only non-monotone** fundamental operation.

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| "Projection doesn't remove duplicates" | In **RA**, projection **removes duplicates** (set semantics). In SQL, SELECT does NOT remove duplicates unless DISTINCT is used |
| "Natural join = Cartesian product" | Only when there are **no common attributes** |
| "R ⋈ S always returns |R|×|S| tuples" | That's only the MAX. Min is 0 |
| "R − S = S − R" | Set difference is **NOT commutative** |
| "Division can be expressed without −" | **No.** Division requires set difference, which is non-monotone |
| "RA can express aggregation" | **No.** Standard RA has no COUNT, SUM, AVG. Extended RA adds these |
| "Theta join removes duplicate columns" | **No.** Only **natural join** removes duplicate common columns |
| Forgetting union compatibility | Union, intersection, difference require **same degree and compatible domains** |

---

## 3 Worked Examples

### Example 1: Write RA Expression (Easy)

**Q:** Given `Employee(EmpID, Name, DeptID)` and `Department(DeptID, DeptName)`, find names of employees in the 'CS' department.

**Solution:**
```
π_Name(σ_(DeptName='CS')(Employee ⋈ Department))
```

Step-by-step:
1. Natural join Employee and Department on DeptID
2. Select tuples where DeptName = 'CS'
3. Project the Name attribute

---

### Example 2: Compute Result Size (Medium — GATE Favourite)

**Q:** R has 5 tuples, S has 4 tuples. R and S have 2 common attributes. What are the min and max number of tuples in R ⋈ S?

**Solution:**
- **Minimum = 0** (no matching tuples on common attributes)
- **Maximum = 5 × 4 = 20** (every tuple in R matches every tuple in S — possible if all common attribute values are the same)
- **Answer: Min = 0, Max = 20**

---

### Example 3: Division Operation (GATE Level)

**Q:** Given:
```
Enrolls(StudentID, CourseID):
(S1, C1), (S1, C2), (S1, C3),
(S2, C1), (S2, C2),
(S3, C1), (S3, C2), (S3, C3)

AllCourses(CourseID):
(C1), (C2), (C3)
```

Find `Enrolls ÷ AllCourses`.

**Solution:**
- Division finds students enrolled in **ALL** courses in AllCourses.
- S1: has C1, C2, C3 ✅
- S2: has C1, C2 (missing C3) ❌
- S3: has C1, C2, C3 ✅

**Result:**
```
(S1)
(S3)
```

**Using the formula:**
```
T = π_StudentID(Enrolls) = {S1, S2, S3}
U = (T × AllCourses) − Enrolls = {(S2,C3)}
π_StudentID(U) = {S2}
Answer = T − {S2} = {S1, S3}
```

---

## Revision Table

| Operation | Symbol | Commutative? | Associative? | Duplicate Removal? |
|---|---|---|---|---|
| Selection | σ | Yes (cascade) | Yes | N/A |
| Projection | π | N/A | Limited | **Yes** |
| Union | ∪ | Yes | Yes | **Yes** |
| Intersection | ∩ | Yes | Yes | **Yes** |
| Difference | − | **No** | **No** | N/A |
| Cart. Product | × | Yes | Yes | N/A |
| Natural Join | ⋈ | Yes | Yes | N/A |
| Division | ÷ | **No** | **No** | N/A |

---

*← [04 — Normalisation Deep Dive](04_Normalisation_Deep_Dive.md) | [06 — SQL Mastery →](06_SQL_Mastery.md)*
