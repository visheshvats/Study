# 5. Relational Algebra & Calculus — Detailed GATE CSE Guide

> **GATE Weightage:** 3–5 marks. You'll be asked to write RA expressions, evaluate query results, calculate output sizes, and understand equivalences between expressions.

---

## What is Relational Algebra?

Imagine you have data in tables and want to ask questions like "Give me all students in CS department" or "Which students are enrolled in ALL courses?" **Relational Algebra (RA)** gives you a way to express these queries using mathematical operations.

RA is a **procedural query language** — it tells you **HOW** to retrieve data step by step. This is different from SQL, which is declarative (tells you WHAT you want, not how to get it).

**Key property — Closure:** Every RA operation takes one or more relations (tables) as input and produces a **new relation** as output. This means you can **chain operations** — the output of one operation becomes the input of the next.

Think of it like a **pipeline**: Table → Operation → New Table → Another Operation → Another New Table ...

---

## The 6 Fundamental Operations

Codd defined **exactly 6 fundamental operations**. Every other operation (join, division, intersection, etc.) can be built from these 6.

---

### 1. Selection (σ) — "Pick Rows"

**What it does:** Filters rows based on a condition. It keeps only the rows where the condition is TRUE.

**Symbol:** σ (sigma)

**Syntax:** `σ_condition(Relation)`

**Analogy:** Think of selection as the WHERE clause in SQL.

**Example:**

Given table `Student`:
| Roll | Name | Age | Dept |
|---|---|---|---|
| 101 | Amit | 20 | CS |
| 102 | Priya | 22 | EC |
| 103 | Rahul | 19 | CS |
| 104 | Sneha | 21 | ME |

```
σ_(Age > 20)(Student) =
```
| Roll | Name | Age | Dept |
|---|---|---|---|
| 102 | Priya | 22 | EC |
| 104 | Sneha | 21 | ME |

```
σ_(Dept = 'CS' AND Age < 20)(Student) =
```
| Roll | Name | Age | Dept |
|---|---|---|---|
| 103 | Rahul | 19 | CS |

**Properties:**
- **Input:** 1 relation with n tuples → **Output:** 0 to n tuples (only removes rows, never adds)
- **Degree stays the same** (same number of columns)
- **Commutative:** σ_c1(σ_c2(R)) = σ_c2(σ_c1(R)) = σ_(c1 AND c2)(R)
- **Idempotent:** σ_c(σ_c(R)) = σ_c(R)

> **GATE Tip:** Selection can only **reduce** the number of tuples, never increase.

---

### 2. Projection (π) — "Pick Columns"

**What it does:** Selects specific columns and **removes duplicates** from the result.

**Symbol:** π (pi)

**Syntax:** `π_(list of columns)(Relation)`

**Analogy:** Think of projection as the SELECT clause in SQL (but with automatic DISTINCT).

**Example:**

```
π_(Name, Dept)(Student) =
```
| Name | Dept |
|---|---|
| Amit | CS |
| Priya | EC |
| Rahul | CS |
| Sneha | ME |

What if we project only on Dept?
```
π_(Dept)(Student) =
```
| Dept |
|---|
| CS |
| EC |
| ME |

Notice: Even though there are 2 CS students (Amit and Rahul), CS appears **only once** because projection removes duplicates!

**Properties:**
- **Input:** n tuples → **Output:** 1 to n tuples (never more — can only reduce due to duplicate removal)
- **Degree changes** — equals the number of projected attributes
- **REMOVES DUPLICATES** — This is the key difference from SQL's SELECT (which does NOT remove duplicates by default)

> **⚠️ GATE Critical Distinction:**
> - In **Relational Algebra**: π always removes duplicates (set semantics)
> - In **SQL**: SELECT does NOT remove duplicates unless you use DISTINCT (bag semantics)

---

### 3. Union (∪) — "Combine Rows from Two Tables"

**What it does:** Returns all tuples that appear in R, S, or both. Removes duplicates.

**Syntax:** `R ∪ S`

**Requirement:** R and S must be **union compatible** — same number of columns, and corresponding columns have compatible domains.

**Example:**

CS_Students:
| Roll | Name |
|---|---|
| 101 | Amit |
| 103 | Rahul |

EC_Students:
| Roll | Name |
|---|---|
| 102 | Priya |
| 103 | Rahul |

```
CS_Students ∪ EC_Students =
```
| Roll | Name |
|---|---|
| 101 | Amit |
| 102 | Priya |
| 103 | Rahul |

Rahul appears in both, but only **once** in the result (duplicates removed).

**Properties:**
- **Output size:** max(|R|, |S|) ≤ |R ∪ S| ≤ |R| + |S|
- **Commutative:** R ∪ S = S ∪ R
- **Associative:** (R ∪ S) ∪ T = R ∪ (S ∪ T)

---

### 4. Set Difference (−) — "Rows in R but NOT in S"

**What it does:** Returns tuples that are in R but not in S.

**Syntax:** `R − S`

**Example:**
```
CS_Students − EC_Students =
```
| Roll | Name |
|---|---|
| 101 | Amit |

(Rahul is in both, so he's excluded. Amit is only in CS, so he remains.)

**Properties:**
- **Output size:** 0 ≤ |R − S| ≤ |R|
- **NOT Commutative:** R − S ≠ S − R (in our example, S − R = {Priya} ≠ {Amit})
- **NOT Associative**

> **GATE Key Fact:** Set difference is the **only non-monotone** fundamental operation. This means adding tuples to S can REMOVE tuples from the result (R − S). All other operations are monotone — adding input can only add or maintain output.

---

### 5. Cartesian Product (×) — "Every Row Paired with Every Other Row"

**What it does:** Combines every tuple in R with every tuple in S.

**Syntax:** `R × S`

**Example:**

R:
| A | B |
|---|---|
| 1 | 2 |
| 3 | 4 |

S:
| C | D |
|---|---|
| x | y |
| p | q |
| r | s |

```
R × S =
```
| A | B | C | D |
|---|---|---|---|
| 1 | 2 | x | y |
| 1 | 2 | p | q |
| 1 | 2 | r | s |
| 3 | 4 | x | y |
| 3 | 4 | p | q |
| 3 | 4 | r | s |

Each row in R is paired with EVERY row in S.

**Properties:**
- **Output tuples:** |R × S| = |R| × |S| = 2 × 3 = 6 (ALWAYS exact, no variation)
- **Output columns:** degree(R) + degree(S) = 2 + 2 = 4
- **Commutative and Associative**

> Cartesian product by itself is rarely useful — it's usually followed by a selection (which gives us a join).

---

### 6. Rename (ρ) — "Give New Names"

**What it does:** Renames a relation or its attributes.

**Syntax:**
- `ρ_S(R)` — rename relation R to S
- `ρ_(A,B,C)(R)` — rename attributes to A, B, C
- `ρ_S(A,B,C)(R)` — rename both relation and attributes

**Why is rename needed?** For self-joins! If you want to join a table with itself, you need two copies with different names.

**Example:** Find pairs of students in the same department:
```
ρ_S1(Student) ⋈_(S1.Dept = S2.Dept AND S1.Roll ≠ S2.Roll) ρ_S2(Student)
```

---

## Derived Operations — Built from the 6 Fundamentals

### Intersection (∩)

**R ∩ S** = tuples in BOTH R and S

**Expressed as:** `R ∩ S = R − (R − S)`

| Property | Value |
|---|---|
| Output size | 0 to min(|R|, |S|) |
| Commutative | Yes |
| Associative | Yes |

---

### Natural Join (⋈) — The Most Important Derived Operation

**What it does:** Combines two relations by automatically matching on **ALL common attributes**, then removes duplicate columns.

**How it works (step by step):**
1. Compute Cartesian product R × S
2. Select only rows where common attributes are equal
3. Project out duplicate common columns

**Example:**

Student:
| Roll | Name | DeptID |
|---|---|---|
| 101 | Amit | D1 |
| 102 | Priya | D2 |
| 103 | Rahul | D1 |

Department:
| DeptID | DeptName |
|---|---|
| D1 | CS |
| D2 | EC |
| D3 | ME |

```
Student ⋈ Department =
```
| Roll | Name | DeptID | DeptName |
|---|---|---|---|
| 101 | Amit | D1 | CS |
| 102 | Priya | D2 | EC |
| 103 | Rahul | D1 | CS |

Notice:
- The join automatically matched on `DeptID` (the common attribute)
- `DeptID` appears only once (duplicate column removed)
- D3 (ME) doesn't appear because no student has DeptID = D3

**Output size:** 0 (no matches) to |R| × |S| (every row matches every other)

**Special cases:**
- If R and S have **no common attributes** → Natural join = Cartesian product
- If R and S have **all attributes in common** → Natural join = Intersection
- Common attributes that are **automatically** equated. You have NO control over which attributes are used.

> **⚠️ GATE Trap:** Natural join potentially matches on attributes you didn't intend to match. If both tables happen to have a column named "Name" for completely different purposes, natural join will match on it! Use explicit join conditions to avoid this.

---

### Theta Join (⋈θ) and Equi Join

**Theta Join:** `R ⋈_θ S = σ_θ(R × S)` — Cartesian product followed by selection on condition θ.

θ can be any boolean condition: =, <, >, ≤, ≥, ≠

**Equi Join:** A theta join where θ uses only **equality (=)** comparisons.

**Key difference from natural join:** Theta/equi join does NOT remove duplicate columns.

---

### Outer Joins — Preserving Unmatched Rows

Regular (inner) join **loses** unmatched rows. Outer joins **keep** them by filling in NULLs.

**Example:**

Student:
| Roll | DeptID |
|---|---|
| 101 | D1 |
| 102 | D2 |
| 103 | D4 |  ← D4 doesn't exist in Department!

Department:
| DeptID | DeptName |
|---|---|
| D1 | CS |
| D2 | EC |
| D3 | ME |   ← No student in ME!

**Natural (Inner) Join:** Loses Roll 103 (no matching dept) and D3 (no matching student)
```
| 101 | D1 | CS |
| 102 | D2 | EC |
```

**Left Outer Join (⟕):** Keeps ALL rows from the LEFT table
```
| 101 | D1 | CS   |
| 102 | D2 | EC   |
| 103 | D4 | NULL |   ← Preserved! DeptName = NULL
```

**Right Outer Join (⟖):** Keeps ALL rows from the RIGHT table
```
| 101  | D1 | CS |
| 102  | D2 | EC |
| NULL | D3 | ME |   ← Preserved! Roll = NULL
```

**Full Outer Join (⟗):** Keeps ALL rows from BOTH tables
```
| 101  | D1 | CS   |
| 102  | D2 | EC   |
| 103  | D4 | NULL |
| NULL | D3 | ME   |
```

---

### Division (÷) — "For All" Queries

Division answers the question: **"Which values of A are associated with ALL values of B?"**

**Syntax:** `R(A, B) ÷ S(B)`

**Result:** All values of A in R that are paired with **every** value of B in S.

**Formula:**
```
R ÷ S = π_A(R) − π_A((π_A(R) × S) − R)
```

**Detailed Example:**

Enrollment(StudentID, CourseID):
| StudentID | CourseID |
|---|---|
| S1 | C1 |
| S1 | C2 |
| S1 | C3 |
| S2 | C1 |
| S2 | C2 |
| S3 | C1 |
| S3 | C2 |
| S3 | C3 |

Required(CourseID):
| CourseID |
|---|
| C1 |
| C2 |
| C3 |

**Question:** Which students are enrolled in ALL required courses?

```
Enrollment ÷ Required = ?
```

**Step-by-step using the formula:**

1. **π_StudentID(Enrollment)** = {S1, S2, S3}

2. **π_StudentID(Enrollment) × Required** = every student paired with every required course:
   | StudentID | CourseID |
   |---|---|
   | S1 | C1 |
   | S1 | C2 |
   | S1 | C3 |
   | S2 | C1 |
   | S2 | C2 |
   | S2 | C3 |
   | S3 | C1 |
   | S3 | C2 |
   | S3 | C3 |

3. **(π_A(R) × S) − R** = "student-course pairs where the student is NOT enrolled":
   | StudentID | CourseID |
   |---|---|
   | S2 | C3 |

4. **π_StudentID of above** = {S2}

5. **Final answer** = {S1, S2, S3} − {S2} = **{S1, S3}**

S1 and S3 are enrolled in ALL three required courses. S2 is missing C3.

> **GATE Tip:** Division is the RA way to express **universal quantification** ("for all") queries. In SQL, these are done with double NOT EXISTS.

---

## Size Formulas — Critical for GATE NAT Questions

| Operation | Min Output Tuples | Max Output Tuples |
|---|---|---|
| σ_c(R) | 0 | \|R\| |
| π_L(R) | 1 | \|R\| |
| R ∪ S | max(\|R\|, \|S\|) | \|R\| + \|S\| |
| R ∩ S | 0 | min(\|R\|, \|S\|) |
| R − S | 0 | \|R\| |
| R × S | \|R\| × \|S\| (exact) | \|R\| × \|S\| (exact) |
| R ⋈ S (natural) | 0 | \|R\| × \|S\| |

**Why π_L(R) minimum is 1 (not 0)?**
Because if R is non-empty (has at least one tuple), projecting on any subset of columns produces at least one tuple. If R is empty, the minimum is 0.

> **GATE refinement:** For non-empty relations, the minimums above apply. If relations can be empty, min is always 0.

---

## Relational Calculus — Brief Overview

### Tuple Relational Calculus (TRC)

A **non-procedural** (declarative) language. You specify **WHAT** you want, not HOW to get it.

**Syntax:** `{ t | P(t) }` = "Set of all tuples t such that predicate P(t) is true"

**Example:** Find all CS students:
```
{ t | Student(t) ∧ t.Dept = 'CS' }
```

### Domain Relational Calculus (DRC)

Uses individual **domain variables** instead of tuple variables.

**Syntax:** `{ <x₁, x₂, ...> | P(x₁, x₂, ...) }` = "Set of value combinations satisfying P"

**Example:**
```
{ <n, a> | ∃r (Student(r, n, a, d) ∧ d = 'CS') }
```

### Codd's Theorem

> **Relational Algebra = Safe Tuple Relational Calculus = Safe Domain Relational Calculus**

All three have the **same expressive power**. Anything you can express in one, you can express in all three.

**What RA CANNOT express:**
- Recursive queries (transitive closure — e.g., "find all ancestors")
- Aggregation (COUNT, SUM, AVG)
- Sorting

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| "Projection doesn't remove duplicates" | In **RA**, projection REMOVES duplicates. In SQL, SELECT does not (unless DISTINCT) |
| "R ⋈ S always has |R|×|S| tuples" | That's the MAXIMUM. Minimum is 0 |
| "R − S = S − R" | Set difference is NOT commutative |
| "Natural join = Cartesian product" | Only true when there are NO common attributes |
| "Division doesn't need set difference" | Division REQUIRES set difference (the only non-monotone fundamental op) |
| "RA can do COUNT/SUM" | Standard RA cannot. Extended RA adds aggregation |
| "Theta join removes duplicate columns" | Only NATURAL join removes duplicates. Theta/equi join keeps all columns |

---

## Revision Table

| Operation | Symbol | Comm? | Assoc? | Dup Removal? | Key Property |
|---|---|---|---|---|---|
| Selection | σ | Yes | Yes | N/A | Filters rows |
| Projection | π | N/A | Limited | **Yes** | Filters columns |
| Union | ∪ | Yes | Yes | **Yes** | Combines rows |
| Intersection | ∩ | Yes | Yes | **Yes** | Common rows |
| Difference | − | **No** | **No** | N/A | Only non-monotone |
| Cart. Product | × | Yes | Yes | N/A | |R|×|S| always |
| Natural Join | ⋈ | Yes | Yes | N/A | Auto-match common attrs |
| Division | ÷ | **No** | **No** | N/A | "For all" queries |

---

*← [04 — Normalisation Deep Dive](04_Normalisation_Deep_Dive.md) | [06 — SQL Mastery →](06_SQL_Mastery.md)*
