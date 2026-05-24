# 9. GATE Practice Set — DBMS Comprehensive Question Bank

> **15 High-Quality GATE-Level Questions** — 5 MCQs, 5 MSQs, 5 NATs
> Covering all 8 modules with detailed step-by-step solutions.

---

## Instructions

| Type | Format | Marking |
|---|---|---|
| **MCQ** (Multiple Choice Question) | Exactly **one** correct answer | +2 for correct, −⅔ for wrong |
| **MSQ** (Multiple Select Question) | **One or more** correct answers | +2 for all correct, 0 otherwise (no partial/negative) |
| **NAT** (Numerical Answer Type) | Type a number (integer or decimal) | +2 for correct, 0 for wrong (no negative marking) |

---

## Questions

---

### Q1. [MCQ] — ER Model & Minimum Tables

Consider an ER diagram with:
- 3 strong entity sets: `A`, `B`, `C`
- 1 weak entity set: `D` (owner: `A`)
- 1 M:N relationship between `A` and `B`
- 1 1:N relationship between `B` and `C` (total participation on C side)
- 1 1:1 relationship between `A` and `C` (total participation on both sides)
- Entity `B` has one multi-valued attribute

What is the **minimum** number of tables required in the relational schema?

**(A)** 5
**(B)** 6
**(C)** 7
**(D)** 8

---

### Q2. [MCQ] — Normalisation (Normal Form Identification)

Consider a relation R(A, B, C, D, E) with the following functional dependencies:

```
AB → C
C  → D
D  → E
```

The candidate key(s) of R is/are `{A, B}`. What is the **highest normal form** of R?

**(A)** 1NF
**(B)** 2NF
**(C)** 3NF
**(D)** BCNF

---

### Q3. [MCQ] — SQL NULL Handling

Consider the following table `Employee`:

| EmpID | Salary |
|---|---|
| 1 | 50000 |
| 2 | NULL |
| 3 | 60000 |
| 4 | NULL |
| 5 | 40000 |

What is the output of the following query?

```sql
SELECT COUNT(*) - COUNT(Salary) AS Result FROM Employee;
```

**(A)** 0
**(B)** 2
**(C)** 3
**(D)** 5

---

### Q4. [MCQ] — Concurrency Control (Conflict Serializability)

Consider the following schedule S involving three transactions T₁, T₂, T₃:

```
S: R₁(A)  R₂(B)  W₃(A)  W₁(B)  R₃(B)  W₂(A)
```

Which of the following statements is **TRUE** about schedule S?

**(A)** S is conflict serializable, equivalent to T₁ T₂ T₃
**(B)** S is conflict serializable, equivalent to T₁ T₃ T₂
**(C)** S is conflict serializable, equivalent to T₃ T₁ T₂
**(D)** S is NOT conflict serializable

---

### Q5. [MCQ] — B+ Tree

A B+ tree of order **p = 4** (max 3 keys per internal node, max 4 children) and leaf order **q = 4** (max 3 key-pointer pairs per leaf). What is the **maximum** number of records that can be indexed by a B+ tree of **height 3** (root at level 1, leaves at level 3)?

**(A)** 48
**(B)** 64
**(C)** 192
**(D)** 256

---

### Q6. [MSQ] — Relational Algebra Properties

Which of the following statements about relational algebra operations are **TRUE**?

**(A)** Natural join is commutative and associative.
**(B)** Set difference (R − S) is commutative.
**(C)** If R has n tuples and S has m tuples, then R ⋈ S (natural join) always has n × m tuples.
**(D)** Projection (π) removes duplicate tuples from the result.
**(E)** The division operation (÷) can be expressed using the fundamental operations including set difference.

---

### Q7. [MSQ] — Transaction Recoverability

Consider the following schedule:

```
S: R₁(X)  W₁(X)  R₂(X)  R₁(Y)  W₂(X)  C₂  W₁(Y)  C₁
```

Which of the following are **TRUE**?

**(A)** S is recoverable.
**(B)** S is irrecoverable.
**(C)** S is cascadeless.
**(D)** S avoids cascading rollback.
**(E)** T₂ reads data written by T₁.

---

### Q8. [MSQ] — Normalisation Properties

Which of the following statements are **TRUE** regarding database normalisation?

**(A)** Every relation with two attributes is always in BCNF.
**(B)** BCNF decomposition always preserves all functional dependencies.
**(C)** 3NF decomposition (synthesis algorithm) always guarantees both lossless join and dependency preservation.
**(D)** If all attributes of a relation are prime, it is at least in 3NF.
**(E)** A relation in 3NF is always in BCNF.

---

### Q9. [MSQ] — SQL Semantics

Consider the table `Student(Roll, Name, Dept, CGPA)` with data:

| Roll | Name | Dept | CGPA |
|---|---|---|---|
| 1 | Amit | CS | 8.5 |
| 2 | Priya | CS | 9.0 |
| 3 | Rahul | EC | NULL |
| 4 | Sneha | CS | 8.5 |
| 5 | Karan | EC | 7.5 |

Which of the following queries return **exactly 2 rows**?

**(A)**
```sql
SELECT Dept, AVG(CGPA) FROM Student GROUP BY Dept;
```

**(B)**
```sql
SELECT * FROM Student WHERE CGPA > 8.0 AND Dept = 'CS';
```

**(C)**
```sql
SELECT DISTINCT CGPA FROM Student WHERE Dept = 'CS';
```

**(D)**
```sql
SELECT * FROM Student WHERE CGPA NOT IN (SELECT CGPA FROM Student WHERE Dept = 'EC');
```

---

### Q10. [MSQ] — File Structures & Indexing

Which of the following statements are **TRUE**?

**(A)** A sparse index can be built only on a sorted (ordered) file.
**(B)** A secondary index on a non-key field is always a dense index.
**(C)** Hash-based indexing supports efficient range queries.
**(D)** In a B+ tree, data pointers are stored only in the leaf nodes.
**(E)** During a leaf node split in a B+ tree, the middle key is **pushed up** (moved) to the parent.

---

### Q11. [NAT] — Counting Super Keys

Consider a relation R(A, B, C, D, E, F) with candidate keys `{A, B}` and `{C, D, E}`.

The total number of super keys of R is _________.

---

### Q12. [NAT] — Relational Algebra Result Size

Consider two relations:
- R(A, B) with **6 tuples**: {(1,2), (1,3), (2,3), (2,4), (3,4), (3,5)}
- S(B, C) with **4 tuples**: {(2,x), (3,y), (4,z), (6,w)}

The number of tuples in R ⋈ S (natural join on B) is _________.

---

### Q13. [NAT] — B+ Tree Height

A B+ tree has internal node order **p = 100** and leaf node order **q = 50**. The file has **10,000,000** (10 million) records.

What is the **minimum height** of the B+ tree required to index all records? (Count the root as height 1.)

_________ 

---

### Q14. [NAT] — Candidate Keys Count

Consider a relation R(A, B, C, D) with functional dependencies:

```
A  → B
BC → D
D  → A
```

The total number of candidate keys of R is _________.

---

### Q15. [NAT] — Block Access Cost

A sequential (sorted) file contains **200,000** records. Each record is **250 bytes**. The block size is **2048 bytes**. A primary index is built on the file.

The index entry size is **14 bytes** (key + block pointer).

How many block accesses are needed for a search using the primary index? (Binary search on index + 1 for data block access.)

_________

---

---

## Solution Key

---

### Solution Q1: Minimum Tables — ER Model

**Counting tables:**

| Component | Table(s) | Explanation |
|---|---|---|
| Strong entity A | 1 | Standard mapping |
| Strong entity B | 1 | Standard mapping |
| Strong entity C | 1 | Standard mapping |
| Weak entity D (owner A) | 1 | Separate table, PK = A's PK + discriminator |
| M:N (A–B) | 1 | M:N always needs separate table |
| 1:N (B–C), total on C | 0 | Merge FK into C (N-side, total participation) |
| 1:1 (A–C), both total | −1 | Can merge A and C into one table |
| Multi-valued attr of B | 1 | Separate table for multi-valued attribute |

Wait — let's reconsider. If we merge A and C (1:1, both total), that's one table. But C also receives FK from the 1:N with B. Let's be careful:

- A and C merge into one table (call it AC): covers strong entities A and C, the 1:1 relationship.
- B: 1 table.
- 1:N (B–C): FK goes into C-side, which is now in the AC table → 0 extra tables.
- D (weak entity of A): 1 table.
- M:N (A–B): 1 separate table.
- Multi-valued attr of B: 1 separate table.

**Total = 1 (AC) + 1 (B) + 1 (D) + 1 (M:N) + 1 (MV attr) = 5**

**Answer: (A) 5** ✅

---

### Solution Q2: Normal Form Identification

**Step 1: Candidate Keys**
- (AB)⁺ = {A,B} → A→? No direct. AB → C → D → E → {A,B,C,D,E} ✅
- No proper subset of {A,B} works: A⁺ = {A}, B⁺ = {B}
- **CK = {A, B}**

**Step 2: Prime/Non-Prime**
- Prime: {A, B}
- Non-prime: {C, D, E}

**Step 3: Check Normal Forms**

Check AB → C: AB is a superkey ✅ (satisfies BCNF)
Check C → D: C is NOT a superkey ❌. Is D prime? No ❌. But is C a proper subset of CK? No, C is not part of CK at all.
- This is a **transitive dependency**: AB → C → D → E
- Violates 3NF (non-prime determined by non-superkey, and D is not prime)

But wait — is it at least 2NF? 
- Partial dependency = non-prime depends on proper subset of CK.
- A → ? No FD with just A on LHS. B → ? No FD with just B on LHS.
- So no partial dependency. → **2NF satisfied** ✅

The FD C → D violates 3NF (transitive dependency of non-prime on non-superkey).

**Answer: (B) 2NF** ✅

---

### Solution Q3: SQL COUNT with NULLs

```sql
SELECT COUNT(*) - COUNT(Salary) AS Result FROM Employee;
```

- `COUNT(*)` = 5 (counts all rows, including NULLs)
- `COUNT(Salary)` = 3 (counts only non-NULL Salary values: 50000, 60000, 40000)
- Result = 5 − 3 = **2**

**Answer: (B) 2** ✅

---

### Solution Q4: Conflict Serializability — Precedence Graph

**Schedule:** R₁(A) R₂(B) W₃(A) W₁(B) R₃(B) W₂(A)

**Step 1: Find all conflicts on same data item**

**Data item A:**
- R₁(A) vs W₃(A): T₁ before T₃ → **T₁ → T₃**
- R₁(A) vs W₂(A): T₁ before T₂ → **T₁ → T₂**
- W₃(A) vs W₂(A): T₃ before T₂ → **T₃ → T₂**

**Data item B:**
- R₂(B) vs W₁(B): T₂ before T₁ → **T₂ → T₁**
- W₁(B) vs R₃(B): T₁ before T₃ → **T₁ → T₃**

**Step 2: Precedence Graph**
```
T₂ → T₁ → T₃ → T₂  ← CYCLE!

Edges: T₁→T₃, T₁→T₂, T₃→T₂, T₂→T₁, T₁→T₃
Cycle: T₂ → T₁ → T₂ (via T₂→T₁ and T₁→T₂)
```

Cycle exists → **NOT conflict serializable**.

**Answer: (D) S is NOT conflict serializable** ✅

---

### Solution Q5: B+ Tree Maximum Records

- Order p = 4 (max 4 children, 3 keys per internal node)
- Leaf order q = 4 (max 3 key-pointer pairs per leaf)
- Height = 3 (root at level 1, leaves at level 3)

**Level 1 (root):** 1 node, max 4 children
**Level 2:** max 4 nodes, each with max 4 children = 16 children
**Level 3 (leaves):** max 16 leaf nodes

Max records = 16 × (q − 1) = 16 × 3 = **48**

Alternatively: max leaves = p^(h-1) = 4^(3-1) = 4² = 16
Max records = 16 × 3 = 48

**Answer: (A) 48** ✅

---

### Solution Q6: Relational Algebra Properties

**(A) Natural join is commutative and associative.** → **TRUE** ✅
- R ⋈ S = S ⋈ R, and (R ⋈ S) ⋈ T = R ⋈ (S ⋈ T)

**(B) Set difference is commutative.** → **FALSE** ❌
- R − S ≠ S − R in general

**(C) Natural join always has n × m tuples.** → **FALSE** ❌
- Natural join can have 0 to n×m tuples. It equals n×m only when all common attribute values match (which is the Cartesian product case).

**(D) Projection removes duplicate tuples.** → **TRUE** ✅
- In relational algebra (set semantics), projection removes duplicates.

**(E) Division can be expressed using fundamentals including set difference.** → **TRUE** ✅
- R ÷ S = π_A(R) − π_A((π_A(R) × S) − R)

**Answer: (A), (D), (E)** ✅

---

### Solution Q7: Transaction Recoverability

**Schedule:** R₁(X) W₁(X) R₂(X) R₁(Y) W₂(X) C₂ W₁(Y) C₁

**Step 1: Data flow analysis**
- T₁ writes X (W₁(X)), then T₂ reads X (R₂(X)) → **T₂ reads from T₁** ✅

**(E) is TRUE** ✅

**Step 2: Recoverability**
- T₂ reads from T₁, so T₁ must commit **before** T₂ for recoverability.
- C₂ (T₂ commits) comes **before** C₁ (T₁ commits).
- **T₂ commits before T₁ → IRRECOVERABLE!** ❌

**(B) is TRUE** ✅ (irrecoverable)
**(A) is FALSE** ❌

**Step 3: Cascadeless?**
- T₂ reads X written by T₁ **before** T₁ commits → NOT cascadeless ❌

**(C) is FALSE** ❌
**(D) is FALSE** ❌ (cascadeless = avoids cascading rollback; same thing)

**Answer: (B), (E)** ✅

---

### Solution Q8: Normalisation Properties

**(A) Every relation with two attributes is always in BCNF.** → **TRUE** ✅
- With 2 attributes, the possible FDs are: A→B, B→A, AB→ (trivial). None can violate BCNF (the LHS is always a superkey or the FD is trivial).

**(B) BCNF decomposition always preserves all FDs.** → **FALSE** ❌
- Classic counter-example: R(Student, Course, Instructor) with FDs {SC→I, I→C}. BCNF decomposition loses SC→I.

**(C) 3NF synthesis guarantees lossless join and dependency preservation.** → **TRUE** ✅
- This is a standard theorem.

**(D) If all attributes are prime, relation is at least in 3NF.** → **TRUE** ✅
- 3NF: for X→A, either X is superkey OR A is prime. If all attributes are prime, the second condition always holds.

**(E) A relation in 3NF is always in BCNF.** → **FALSE** ❌
- Counter-example: R(A,B,C) with FDs {AB→C, C→B}. CKs = {AB, AC}. C→B satisfies 3NF (B is prime) but violates BCNF (C is not a superkey).

**Answer: (A), (C), (D)** ✅

---

### Solution Q9: SQL Queries Returning Exactly 2 Rows

**Data:**
| Roll | Name | Dept | CGPA |
|---|---|---|---|
| 1 | Amit | CS | 8.5 |
| 2 | Priya | CS | 9.0 |
| 3 | Rahul | EC | NULL |
| 4 | Sneha | CS | 8.5 |
| 5 | Karan | EC | 7.5 |

**(A)** `SELECT Dept, AVG(CGPA) FROM Student GROUP BY Dept;`
- Groups: CS → AVG(8.5, 9.0, 8.5) = 8.667, EC → AVG(NULL, 7.5) = 7.5 (NULL ignored)
- **2 rows** ✅

**(B)** `SELECT * FROM Student WHERE CGPA > 8.0 AND Dept = 'CS';`
- Roll 1: 8.5 > 8.0 ∧ CS ✅
- Roll 2: 9.0 > 8.0 ∧ CS ✅
- Roll 4: 8.5 > 8.0 ∧ CS ✅
- **3 rows** ❌

**(C)** `SELECT DISTINCT CGPA FROM Student WHERE Dept = 'CS';`
- CS CGPAs: 8.5, 9.0, 8.5 → DISTINCT: {8.5, 9.0}
- **2 rows** ✅

**(D)** `SELECT * FROM Student WHERE CGPA NOT IN (SELECT CGPA FROM Student WHERE Dept = 'EC');`
- Subquery: CGPAs from EC = {NULL, 7.5}
- NOT IN with NULL in subquery → **every comparison becomes UNKNOWN!**
- `CGPA NOT IN (NULL, 7.5)` = `CGPA ≠ NULL AND CGPA ≠ 7.5` = `UNKNOWN AND ...` = UNKNOWN
- **0 rows!** ❌ (This is the classic NOT IN with NULL trap!)

**Answer: (A), (C)** ✅

---

### Solution Q10: File Structures & Indexing

**(A) A sparse index can be built only on a sorted file.** → **TRUE** ✅
- Sparse index has one entry per block. If the file is unsorted, you can't locate records between anchors.

**(B) A secondary index on a non-key field is always dense.** → **TRUE** ✅
- Secondary index on non-key: must have an entry for each record (or each distinct value with a pointer list), making it dense.

**(C) Hash-based indexing supports efficient range queries.** → **FALSE** ❌
- Hash functions destroy ordering. Hash indexes support only **equality** lookups.

**(D) In B+ tree, data pointers are stored only in leaf nodes.** → **TRUE** ✅
- This is the defining property of B+ trees vs. B-trees.

**(E) During leaf node split in B+ tree, middle key is PUSHED UP.** → **FALSE** ❌
- In leaf split, the middle key is **COPIED** up (it remains in the leaf). PUSH is for internal node splits.

**Answer: (A), (B), (D)** ✅

---

### Solution Q11: Counting Super Keys [NAT]

R(A, B, C, D, E, F) — 6 attributes
CK₁ = {A, B}, CK₂ = {C, D, E}

Using Inclusion-Exclusion:

```
|CK₁| = 2, |CK₂| = 3
|CK₁ ∪ CK₂| = |{A, B, C, D, E}| = 5
n = 6

Super keys from CK₁ = 2^(6-2) = 2⁴ = 16
Super keys from CK₂ = 2^(6-3) = 2³ = 8
Super keys from CK₁∪CK₂ = 2^(6-5) = 2¹ = 2

Total = 16 + 8 − 2 = 22
```

**Answer: 22** ✅

---

### Solution Q12: Natural Join Result Size [NAT]

R(A, B): {(1,2), (1,3), (2,3), (2,4), (3,4), (3,5)}
S(B, C): {(2,x), (3,y), (4,z), (6,w)}

Natural join on common attribute B:

| R tuple | B value | Matching S tuples | Join tuples |
|---|---|---|---|
| (1, **2**) | 2 | (2, x) | (1, 2, x) |
| (1, **3**) | 3 | (3, y) | (1, 3, y) |
| (2, **3**) | 3 | (3, y) | (2, 3, y) |
| (2, **4**) | 4 | (4, z) | (2, 4, z) |
| (3, **4**) | 4 | (4, z) | (3, 4, z) |
| (3, **5**) | 5 | — (no match) | — |

S tuple (6, w) → B=6 has no match in R.

**Total join tuples = 5**

**Answer: 5** ✅

---

### Solution Q13: B+ Tree Minimum Height [NAT]

- Internal order p = 100, Leaf order q = 50
- Records = 10,000,000

Max key-pointer pairs per leaf = q − 1 = 49
Min number of leaves needed = ⌈10,000,000 / 49⌉ = 204,082

**Checking heights (root = height 1):**

```
Height 1 (root only, which is a leaf): max records = 49. Not enough.

Height 2: root = 1, max children = 100, leaves = 100
  Max records = 100 × 49 = 4,900. Not enough.

Height 3: levels = root + 1 internal + leaves
  Max leaves = 100 × 100 = 10,000
  Max records = 10,000 × 49 = 490,000. Not enough.

Height 4: 
  Max leaves = 100 × 100 × 100 = 1,000,000
  Max records = 1,000,000 × 49 = 49,000,000 > 10,000,000. ✅
```

**Answer: 4** ✅

---

### Solution Q14: Candidate Keys Count [NAT]

R(A, B, C, D) with FDs: A → B, BC → D, D → A

**Step 1: Find attributes appearing only on LHS, only on RHS, both, neither**
- LHS: A, B, C, D
- RHS: B, D, A
- Only on LHS: **C** (C never appears on RHS alone)
- C must be in every candidate key.

**Step 2: Find closure of C**
- C⁺ = {C} — no FD has only C on LHS. Not sufficient.

**Step 3: Try C with each other attribute**
- (AC)⁺ = {A, C} → A→B → {A, B, C} → BC→D → {A, B, C, D} ✅ → **AC is a CK**
- (BC)⁺ = {B, C} → BC→D → {B, C, D} → D→A → {A, B, C, D} ✅ → **BC is a CK**
- (CD)⁺ = {C, D} → D→A → {A, C, D} → A→B → {A, B, C, D} ✅ → **CD is a CK**

**Step 4: Verify no single attribute is a CK**
- A⁺ = {A, B} ❌, B⁺ = {B} ❌, C⁺ = {C} ❌, D⁺ = {D, A, B} ❌

**Step 5: Are there any other 2-attribute CKs?**
- (AB)⁺ = {A, B} → ... we need C → not a superkey without C. ❌
- Actually AB⁺ = {A,B} → A→B (already have B)... no way to get C. ❌
- (AD)⁺ = {A, D} → A→B → {A, B, D} → can't get C. ❌
- (BD)⁺ = {B, D} → D→A → {A, B, D} → can't get C. ❌

So CKs with C: AC, BC, CD. All have size 2 and none is a subset of another.

**Candidate Keys = {AC, BC, CD}**

**Answer: 3** ✅

---

### Solution Q15: Block Access Cost with Primary Index [NAT]

**Given:**
- Records = 200,000
- Record size = 250 bytes
- Block size = 2048 bytes
- Index entry size = 14 bytes

**Step 1: Data file calculations**
```
bfr = ⌊2048 / 250⌋ = ⌊8.192⌋ = 8 records/block
Data blocks = ⌈200,000 / 8⌉ = 25,000 blocks
```

**Step 2: Primary index calculations**
```
Primary index entries = 25,000 (one per data block — sparse index)
bfr_index = ⌊2048 / 14⌋ = ⌊146.28⌋ = 146 entries/block
Index blocks = ⌈25,000 / 146⌉ = ⌈171.23⌉ = 172 blocks
```

**Step 3: Search cost**
```
Binary search on index = ⌈log₂(172)⌉ = ⌈7.43⌉ = 8
Data block access = 1

Total = 8 + 1 = 9 block accesses
```

**Answer: 9** ✅

---

## Score Card

| Q# | Type | Topic | Answer |
|---|---|---|---|
| Q1 | MCQ | ER Model / Mapping | **(A) 5** |
| Q2 | MCQ | Normalisation | **(B) 2NF** |
| Q3 | MCQ | SQL (NULLs) | **(B) 2** |
| Q4 | MCQ | Concurrency (Serializability) | **(D) Not conflict serializable** |
| Q5 | MCQ | B+ Tree | **(A) 48** |
| Q6 | MSQ | Relational Algebra | **(A), (D), (E)** |
| Q7 | MSQ | Transaction Recovery | **(B), (E)** |
| Q8 | MSQ | Normalisation Properties | **(A), (C), (D)** |
| Q9 | MSQ | SQL Semantics | **(A), (C)** |
| Q10 | MSQ | File Structures | **(A), (B), (D)** |
| Q11 | NAT | Counting Super Keys | **22** |
| Q12 | NAT | Natural Join Size | **5** |
| Q13 | NAT | B+ Tree Height | **4** |
| Q14 | NAT | Candidate Keys Count | **3** |
| Q15 | NAT | Index Block Access Cost | **9** |

---

## Topic Coverage Summary

| Topic | Questions |
|---|---|
| ER Model | Q1 |
| Relational Model | Q11 |
| ER-to-Relational Mapping | Q1 |
| Normalisation | Q2, Q8, Q14 |
| Relational Algebra | Q6, Q12 |
| SQL | Q3, Q9 |
| Transactions & Concurrency | Q4, Q7 |
| File Structures & Indexing | Q5, Q10, Q13, Q15 |

---

*← [08 — File Structures & Indexing](08_File_Structures_and_Indexing.md) | [🏠 Index](README.md)*
