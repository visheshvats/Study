# 4. Normalisation — Deep Dive — Detailed GATE CSE Guide

> **GATE Weightage:** 4–6 marks — one of the **highest-weighted** DBMS topics! You'll get questions on identifying normal forms, finding candidate keys from FDs, computing canonical covers, testing lossless join decomposition, and applying BCNF/3NF algorithms.

---

## What is Normalisation and Why Do We Need It?

Imagine you have a single, big table that stores EVERYTHING:

```
StudentCourseEnrollment:
| Roll | Name  | Age | CourseID | CourseName | Instructor | Grade |
|------|-------|-----|---------|------------|------------|-------|
| 101  | Amit  | 20  | CS301   | DBMS       | Prof. X    | A     |
| 101  | Amit  | 20  | CS302   | OS         | Prof. Y    | B+    |
| 102  | Priya | 21  | CS301   | DBMS       | Prof. X    | A+    |
| 103  | Rahul | 20  | CS303   | CN         | Prof. Z    | B     |
```

This looks simple, but it has **serious problems:**

### Problem 1: Insertion Anomaly

What if you want to add a new course "AI" taught by "Prof. W," but **no student has enrolled yet**? You can't! Because `Roll` and `Name` are required (they're part of the key), and you don't have that data. **You're forced to insert NULL for student info** just to record a new course.

### Problem 2: Deletion Anomaly

If Rahul (the ONLY student in CN) drops the course, you delete his row. But now — **oops!** — you've also lost ALL information about the CN course and Prof. Z! That course data is gone forever.

### Problem 3: Update Anomaly

What if Prof. X changes the course name from "DBMS" to "Database Systems"? You'd have to update **every single row** where CourseID = CS301. Miss one row, and your database is inconsistent — some rows say "DBMS," others say "Database Systems."

### The Solution: Normalisation

**Normalisation** fixes these problems by:
1. **Splitting** one big table into **smaller, focused tables**
2. Each table stores **one type of fact** (no mixing student info with course info)
3. Tables are linked through **foreign keys**

After normalisation:
```
Student(Roll PK, Name, Age)
Course(CourseID PK, CourseName, Instructor)
Enrollment(Roll FK, CourseID FK, Grade)  PK = (Roll, CourseID)
```

Now:
- ✅ You can add a new course without needing a student
- ✅ Deleting a student's enrollment doesn't lose course info
- ✅ Changing a course name requires updating just ONE row in Course table

---

## Functional Dependencies (FDs) — The Foundation

### What is a Functional Dependency?

A **functional dependency** X → Y means:

> "If two rows have the **same value** for attributes X, they **must have the same value** for attributes Y."

Or more intuitively:

> "If I know the value of X, I can **uniquely determine** the value of Y."

**Example:** `Roll_No → Name`
- If Roll_No = 101, the Name is ALWAYS "Amit" (never sometimes "Amit" and sometimes "Raj")
- Knowing the Roll_No **determines** the Name

**Example:** `{StudentID, CourseID} → Grade`
- Knowing both the student AND the course determines the grade
- But StudentID alone doesn't determine Grade (a student has different grades in different courses)

### How to Tell if an FD Holds

Look at ALL possible rows in the relation (not just the current data). An FD X → Y holds if:

> For **every** pair of rows t₁ and t₂: if t₁[X] = t₂[X], then t₁[Y] = t₂[Y]

This is about the **meaning** of the data, not just a coincidence in current values.

**Example that LOOKS like an FD but isn't:**
```
| Roll | Age |
|------|-----|
| 101  | 20  |
| 102  | 21  |
| 103  | 22  |
```
All ages are different, so it LOOKS like `Age → Roll`. But this is just coincidence! Another student could have Age=20 (same as Roll 101), meaning Age doesn't uniquely determine Roll in general.

### Types of Functional Dependencies

| Type | Meaning | Example |
|---|---|---|
| **Trivial** | RHS is a subset of LHS: X → Y where Y ⊆ X | AB → A (always true, useless) |
| **Non-trivial** | RHS has at least one attr NOT in LHS | AB → C |
| **Completely Non-trivial** | LHS and RHS have no common attributes | A → B where A ∩ B = ∅ |
| **Full FD** | Y depends on the **entire** X, not just a part | AB → C, but neither A→C nor B→C holds |
| **Partial FD** | Y depends on a **proper subset** of X | AB → C, and A → C also holds |
| **Transitive FD** | X → Y → Z (Y is not a superkey, Y doesn't determine X) | Roll→Dept, Dept→DeptHead, so Roll→DeptHead transitively |

> **Why do these types matter?** Each type of "bad" FD corresponds to a violation of a specific normal form:
> - Partial FD → Violates **2NF**
> - Transitive FD → Violates **3NF**

---

## Armstrong's Axioms — Deriving New FDs

Given a set of FDs F, we often need to find ALL FDs that are logically implied by F. Armstrong's Axioms are the rules for doing this:

### The Three Axioms

| Axiom | Name | Rule | Intuition |
|---|---|---|---|
| 1 | **Reflexivity** | If Y ⊆ X, then X → Y | "If you know all of X, you definitely know any part of X" |
| 2 | **Augmentation** | If X → Y, then XZ → YZ | "Adding the same info to both sides preserves the dependency" |
| 3 | **Transitivity** | If X → Y and Y → Z, then X → Z | "If A determines B, and B determines C, then A determines C" |

### Derived Rules (You Can Derive These from the Three Axioms)

| Rule | Statement | How to Remember |
|---|---|---|
| **Union** | If X → Y and X → Z, then X → YZ | "Combine what you can determine" |
| **Decomposition** | If X → YZ, then X → Y and X → Z | "Split what you can determine" |
| **Pseudo-transitivity** | If X → Y and WY → Z, then WX → Z | "Extended chain" |

**These axioms are:**
- **Sound:** They never produce an incorrect FD (everything derived is valid)
- **Complete:** They can derive EVERY valid FD (nothing is missed)

**Simple example:**
Given: A → B, B → C
By Transitivity: A → C ✅ (derived new FD!)
By Augmentation of A → B with D: AD → BD ✅

---

## Attribute Closure (X⁺) — Step by Step with Detail

The **closure of attribute set X** (written X⁺) under a set of FDs F is the set of ALL attributes that X functionally determines.

### Algorithm

```
Input: Set of attributes X, set of FDs F
Output: X⁺ (closure of X)

1. Initialize: X⁺ = X
2. Repeat until no change:
   a. For each FD (A → B) in F:
      - If A ⊆ X⁺ (all attributes of A are already in X⁺):
        - Add all attributes of B to X⁺
3. Return X⁺
```

### Detailed Walkthrough

**Given:** R(A, B, C, D, E, F), FDs: A → B, BC → D, E → CF, D → E

**Find {A, B}⁺:**

| Step | X⁺ so far | FD checked | Does LHS ⊆ X⁺? | Action |
|---|---|---|---|---|
| Init | {A, B} | — | — | Start |
| 1 | {A, B} | A → B | A ∈ {A,B}? ✅ | B already in X⁺ — no change |
| 2 | {A, B} | BC → D | BC ⊆ {A,B}? ❌ (C missing) | Skip |
| 3 | {A, B} | E → CF | E ∈ {A,B}? ❌ | Skip |
| 4 | {A, B} | D → E | D ∈ {A,B}? ❌ | Skip |
| — | {A, B} | — | No change → STOP | — |

**{A, B}⁺ = {A, B}** — AB doesn't determine anything beyond itself!

**Now find {A, B, C}⁺:**

| Step | X⁺ so far | FD checked | Does LHS ⊆ X⁺? | Action |
|---|---|---|---|---|
| Init | {A, B, C} | — | — | Start |
| 1 | {A, B, C} | A → B | ✅ | No change (B already there) |
| 2 | {A, B, C} | BC → D | BC ⊆ {A,B,C}? ✅ | Add D → {A, B, C, D} |
| 3 | {A, B, C, D} | E → CF | ❌ | Skip |
| 4 | {A, B, C, D} | D → E | D ∈ {A,B,C,D}? ✅ | Add E → {A, B, C, D, E} |
| — | Repeat scan: |  |  |  |
| 5 | {A, B, C, D, E} | E → CF | E ∈ X⁺? ✅ | Add C, F → {A, B, C, D, E, F} |
| 6 | All attributes! | — | No more changes | STOP |

**{A, B, C}⁺ = {A, B, C, D, E, F}** = ALL attributes ✅

So {A, B, C} is a super key. Is it minimal (a candidate key)? We showed above that {A, B}⁺ = {A, B} (not a superkey), and we'd need to check {A, C} and {B, C} too.

---

## Canonical Cover (Minimal Cover) — Simplified

### What is a Canonical Cover?

Given a set of FDs F, the **canonical cover** Fc is a **simplified version** that:
1. Is **equivalent** to F (implies exactly the same FDs)
2. Has no **redundant FDs** (can't remove any)
3. Has no **extraneous attributes** on the LHS (can't simplify any LHS)
4. Every FD has a **single attribute** on the RHS

Think of it as **cleaning up** your FDs — removing unnecessary stuff while keeping the same information.

### Algorithm (Step by Step)

**Step 1: Single RHS**
Break every FD to have just one attribute on the right side.
```
A → BCD  becomes  A → B, A → C, A → D
```

**Step 2: Remove Extraneous LHS Attributes**
For each FD like `ABC → D`, check if any attribute on the LHS is unnecessary:
- Can we remove A? Check if {BC}⁺ (under current FDs) includes D. If yes → A is extraneous, remove it.
- Can we remove B? Check if {AC}⁺ includes D. If yes → B is extraneous, remove it.
- Can we remove C? Check if {AB}⁺ includes D. If yes → C is extraneous, remove it.

**Step 3: Remove Redundant FDs**
For each FD `X → A` in the current set, check if removing it changes anything:
- Temporarily remove `X → A` from the set
- Compute X⁺ under the remaining FDs
- If A ∈ X⁺ → the FD is redundant (can be derived from others) → remove it permanently

**Step 4: Combine FDs with Same LHS**
```
A → B and A → C  becomes  A → BC
```

### Example

**Given:** F = {A → BC, B → C, A → B, AB → C}

**Step 1: Single RHS**
A → B, A → C, B → C, A → B (duplicate — remove), AB → C

So: {A → B, A → C, B → C, AB → C}

**Step 2: Remove Extraneous LHS in AB → C**
- Can we remove A from AB → C? Check {B}⁺ = {B, C} (using B → C). Does C ∈ {B}⁺? ✅ YES!
- So A is extraneous in AB → C. Change AB → C to B → C (but we already have B → C). So AB → C becomes redundant.
- Remove AB → C. Now: {A → B, A → C, B → C}

**Step 3: Remove Redundant FDs**
- Check A → C: Remove it temporarily. {A → B, B → C}. Compute A⁺ = {A, B, C}. Does C ∈ A⁺? ✅ YES! So A → C is redundant.
- Remove A → C. Now: **{A → B, B → C}**

**Step 4: Combine same LHS** — nothing to combine.

**Canonical Cover: Fc = {A → B, B → C}** ✅

---

## Normal Forms — The Hierarchy

Normal forms measure how "clean" your table design is. Higher normal forms have fewer anomalies.

```
1NF ⊂ 2NF ⊂ 3NF ⊂ BCNF ⊂ 4NF ⊂ 5NF

Every BCNF table is also in 3NF.
Every 3NF table is also in 2NF.
Every 2NF table is also in 1NF.
```

---

### First Normal Form (1NF)

**Requirement:** All attribute values must be **atomic** (single, indivisible values). No sets, no lists, no repeating groups, no nested tables within cells.

**Violates 1NF:**
```
| Roll | Name  | Phones              |
|------|-------|---------------------|
| 101  | Amit  | {9876, 8765, 7654}  |  ← Multi-valued! NOT atomic!
```

**Satisfies 1NF (Option 1: Separate rows):**
```
| Roll | Name  | Phone |
|------|-------|-------|
| 101  | Amit  | 9876  |
| 101  | Amit  | 8765  |
| 101  | Amit  | 7654  |
```

**Satisfies 1NF (Option 2: Separate table — better):**
```
Student(Roll, Name)     Phones(Roll FK, Phone)
```

> **Simple test:** If every cell in the table contains exactly one value → 1NF is satisfied.

---

### Second Normal Form (2NF)

**Requirement:** The table is in **1NF** AND there is **no partial dependency** of any non-prime attribute on any candidate key.

**What is a partial dependency?** A non-prime attribute depends on a **proper subset** (part) of a candidate key.

**When to worry:** Only when the candidate key is **composite** (has 2+ attributes). If all candidate keys are single attributes, partial dependency is IMPOSSIBLE → the table is automatically in 2NF!

**Example that violates 2NF:**
```
Enrollment(StudentID, CourseID, StudentName, Grade)
CK = {StudentID, CourseID}

FD: StudentID → StudentName    ← PARTIAL dependency!
    (StudentName depends on PART of the CK, not the whole CK)

FD: {StudentID, CourseID} → Grade  ← FULL dependency (OK)
```

`StudentName` depends only on `StudentID`, not on the full key `{StudentID, CourseID}`. This is a partial dependency → violates 2NF.

**Fix:** Remove the partial dependency by decomposing:
```
Student(StudentID PK, StudentName)
Enrollment(StudentID FK, CourseID, Grade)  PK = (StudentID, CourseID)
```

Now `StudentName` is in its own table, depending on the full PK (`StudentID`). The partial dependency is eliminated.

> **GATE Quick Check for 2NF:**
> 1. Are ALL candidate keys single attributes? → **Automatically 2NF** ✅
> 2. If any CK is composite → check if any non-prime attribute depends on a subset of that CK

---

### Third Normal Form (3NF)

**Requirement:** For every non-trivial FD **X → A** in the relation:
1. **X is a super key**, OR
2. **A is a prime attribute** (part of some candidate key)

**Equivalently:** No non-prime attribute is **transitively dependent** on any candidate key.

**What is a transitive dependency?**
```
CK → X → A
where:
  - X is NOT a superkey
  - A is NOT a prime attribute
  - X does NOT functionally determine the CK (otherwise X would be a superkey)
```

**Example that violates 3NF:**
```
Employee(EmpID PK, DeptID, DeptName)
CK = {EmpID}

FD: EmpID → DeptID      (OK — EmpID is a superkey)
FD: DeptID → DeptName   (PROBLEM!)
    DeptID is NOT a superkey ❌
    DeptName is NOT a prime attribute ❌
    → Violates BOTH conditions of 3NF → violates 3NF!

The transitive chain: EmpID → DeptID → DeptName
(DeptName transitively depends on EmpID through DeptID)
```

**Fix:** Decompose to remove the transitive dependency:
```
Employee(EmpID PK, DeptID FK)
Department(DeptID PK, DeptName)
```

Now `DeptID → DeptName` is in the Department table where `DeptID` IS the superkey. ✅

> **GATE Quick Check for 3NF:** For every non-trivial FD X → A:
> - Is X a superkey? → ✅ OK
> - If not, is A a prime attribute? → ✅ OK (this is the exception that makes 3NF weaker than BCNF)
> - If neither → ❌ Violates 3NF

---

### Boyce-Codd Normal Form (BCNF)

**Requirement:** For every non-trivial FD **X → A**:
- **X MUST be a super key.** Period. No exceptions.

BCNF is **stricter** than 3NF because it drops the exception "or A is a prime attribute."

### The Critical Difference: 3NF vs. BCNF

| 3NF | BCNF |
|---|---|
| X → A: X is superkey **OR** A is prime | X → A: X **MUST** be superkey |
| Allows "A is prime" exception | **No exceptions** |

**When does a relation satisfy 3NF but NOT BCNF?**

Only when there exists an FD `X → A` where:
- X is NOT a superkey (violates BCNF)
- BUT A IS a prime attribute (satisfies 3NF's exception)

**Classic GATE Example:**
```
R(Student, Course, Instructor)

FDs:
  {Student, Course} → Instructor    (a student in a course has one instructor)
  Instructor → Course               (each instructor teaches one course)

CKs:
  {Student, Course}⁺ = all attrs ✅ → CK₁
  {Student, Instructor}⁺ = {Student, Instructor} → Instructor → Course → all ✅ → CK₂

Prime attributes: Student, Course, Instructor (ALL attributes are prime!)

Check BCNF:
  {Student, Course} → Instructor: {Student, Course} is a superkey ✅
  Instructor → Course: Instructor is NOT a superkey ❌ → Violates BCNF!

Check 3NF:
  Instructor → Course: Course IS a prime attribute ✅ → Satisfies 3NF!

Conclusion: 3NF but NOT BCNF.
```

---

### Fourth Normal Form (4NF) — Brief

**Requirement:** For every non-trivial **multi-valued dependency (MVD)** X →→ Y:
- X must be a super key.

A **multi-valued dependency** X →→ Y exists when the set of Y values associated with X is **independent** of other attributes.

> **For GATE:** 4NF is rarely tested in depth. Know the definition and understand that it handles multi-valued dependencies, which functional dependencies can't capture.

---

## Quick Normal Form Decision Algorithm

For any relation, to find the highest normal form:

```
Step 1: Find ALL candidate keys
Step 2: Identify prime and non-prime attributes
Step 3: For EACH non-trivial FD X → A:
   │
   ├── Is X a superkey?
   │   └── YES → This FD satisfies BCNF (and lower) ✅
   │
   └── NO (X is not a superkey):
       │
       ├── Is A a prime attribute?
       │   └── YES → This FD satisfies 3NF (but NOT BCNF)
       │
       └── NO (A is non-prime):
           │
           ├── Is X a proper subset of some candidate key?
           │   └── YES → This is a PARTIAL dependency → Violates 2NF!
           │
           └── NO → This is a TRANSITIVE dependency → Violates 3NF (but satisfies 2NF)

Step 4: The OVERALL normal form = the LOWEST (weakest) result among all FDs
```

---

## Decomposition — Splitting Tables

### Two Critical Properties

When you decompose a relation R into R₁ and R₂, you MUST check two properties:

#### 1. Lossless Join Decomposition

**Meaning:** When you JOIN R₁ and R₂ back together, you get **exactly R** — no extra (spurious) tuples.

**Test (for binary decomposition):**

A decomposition of R into R₁ and R₂ is **lossless** if and only if:

```
(R₁ ∩ R₂) → (R₁ − R₂)    is in F⁺
      OR
(R₁ ∩ R₂) → (R₂ − R₁)    is in F⁺
```

**In simple words:** The **common attributes** of R₁ and R₂ must be a **superkey** of at least one of the two decomposed relations.

**Example:**
```
R(A, B, C), FD: A → B
Decompose into R₁(A, B) and R₂(A, C)

R₁ ∩ R₂ = {A}
A⁺ = {A, B}  → A is a superkey of R₁(A, B) ✅
→ Lossless decomposition! ✅
```

**Counter-example:**
```
R(A, B, C), FD: A → B
Decompose into R₁(A, B) and R₂(B, C)

R₁ ∩ R₂ = {B}
B⁺ = {B}  → B is NOT a superkey of R₁(A, B) OR R₂(B, C) ❌
→ LOSSY decomposition! ❌ (joining may produce spurious tuples)
```

#### 2. Dependency Preservation

**Meaning:** Every original FD can be verified by looking at **individual tables** — you don't need to join tables to check any FD.

**Why it matters:** If an FD spans across two tables, every INSERT requires joining those tables to verify the FD — which is expensive and impractical.

**Test:** For each FD X → Y:
- Check if ALL attributes of X and Y are in the **same** decomposed table Rᵢ
- If yes → this FD is preserved ✅
- If no → you need a more detailed check using projected FDs

> **⚠️ GATE Critical Theorem:**
> | Algorithm | Lossless? | Dependency Preserving? |
> |---|---|---|
> | **3NF Synthesis** | ✅ ALWAYS | ✅ ALWAYS |
> | **BCNF Decomposition** | ✅ ALWAYS | ❌ NOT ALWAYS |
>
> This means: You can ALWAYS achieve 3NF with both lossless and dependency preserving properties. But for BCNF, you might have to sacrifice dependency preservation.

---

## BCNF Decomposition Algorithm

```
Result = {R}

While some relation Rᵢ in Result is NOT in BCNF:
    1. Find an FD X → Y that violates BCNF in Rᵢ
       (X is not a superkey of Rᵢ)
    2. Compute X⁺ within Rᵢ
    3. Replace Rᵢ with TWO relations:
       a. Rᵢ₁ = X⁺ (all attributes determined by X in Rᵢ)
       b. Rᵢ₂ = (Rᵢ − X⁺) ∪ X (remaining attributes plus X to maintain the link)
    4. Check both new relations for BCNF, repeat if needed
```

**This is ALWAYS lossless** (because X is a superkey of Rᵢ₁).

---

## 3NF Synthesis Algorithm

```
Step 1: Compute the canonical cover Fc
Step 2: For each FD X → A in Fc:
            Create a relation schema Rᵢ(X ∪ {A})
Step 3: Combine relations with the same left-hand side
            (e.g., A → B and A → C become one relation R(A, B, C))
Step 4: If no relation in the result contains a candidate key of the original R:
            Add a new relation containing any one candidate key
```

**This is ALWAYS both lossless AND dependency preserving.**

---

## Important Theorems for GATE

1. **Every 2-attribute relation is ALWAYS in BCNF.** (With only 2 attributes, no FD can violate BCNF — the LHS is always a superkey or the FD is trivial.)

2. **If all candidate keys are single attributes → At least 2NF.** (Partial dependency requires a composite CK.)

3. **If all attributes are prime → At least 3NF.** (The 3NF exception "A is prime" always applies.)

4. **If only one candidate key exists → 3NF ≡ BCNF.** (The 3NF exception for prime attrs can't kick in with only one CK unless overlapping CKs create the situation.)

5. **BCNF decomposition: always lossless, NOT always dependency-preserving.**

6. **3NF synthesis: always lossless AND dependency-preserving.**

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| "No partial dep → 3NF" | No partial dep → **2NF only**. Still need to check transitive dep for 3NF |
| "3NF = BCNF" | BCNF is stricter (no prime attr exception) |
| "BCNF always preserves deps" | **Not always.** Only 3NF guarantees both lossless + dep preservation |
| "Canonical cover is unique" | **No.** Different reduction orders can give different (but equivalent) canonical covers |
| "2-attribute relation can violate BCNF" | **Never.** Every 2-attr relation is in BCNF |
| "Single-attribute CK → 3NF" | Only guarantees **2NF** (no partial dep), not 3NF |

---

## Revision Table

| Normal Form | Requirement | Violation |
|---|---|---|
| **1NF** | Atomic values | Multi-valued or composite attributes in cells |
| **2NF** | 1NF + no partial deps | Non-prime depends on subset of CK |
| **3NF** | X→A: X is superkey OR A is prime | Transitive dep of non-prime on non-superkey |
| **BCNF** | X→A: X MUST be superkey | Any FD where LHS is not a superkey |
| **4NF** | X→→Y: X must be superkey | Non-trivial MVD where LHS is not superkey |

---

*← [03 — ER to Relational Mapping](03_ER_to_Relational_Mapping.md) | [05 — Relational Algebra & Calculus →](05_Relational_Algebra_and_Calculus.md)*
