# 4. Normalisation — Deep Dive — GATE CSE Complete Guide

> **GATE Weightage:** 4–6 marks (one of the **highest-weighted** DBMS topics). Questions test normal form identification, finding candidate keys from FDs, canonical cover, decomposition properties (lossless join, dependency preservation), and BCNF/3NF decomposition.

---

## Normalisation Overview

**Normalisation** is the process of organizing a relational schema to **minimize redundancy** and **eliminate anomalies** (insertion, deletion, update). It works by decomposing relations based on **functional dependencies (FDs)**.

**Anomalies caused by poor design:**

| Anomaly | Problem |
|---|---|
| **Insertion Anomaly** | Cannot insert data without unrelated data (e.g., can't add a department without an employee) |
| **Deletion Anomaly** | Deleting data causes loss of unrelated data |
| **Update Anomaly** | Changing one fact requires updating multiple rows |

---

## Key Definitions & Concepts

### Functional Dependency (FD)

- A constraint between two sets of attributes: **X → Y**
- Meaning: For any two tuples t₁, t₂, if t₁[X] = t₂[X], then t₁[Y] = t₂[Y].
- "X **functionally determines** Y" or "Y is **functionally dependent** on X."
- X = **determinant**, Y = **dependent**.

**Types:**
| Type | Definition | Example |
|---|---|---|
| **Trivial FD** | Y ⊆ X (RHS is subset of LHS) | AB → A |
| **Non-trivial FD** | Y ⊄ X (at least one attr in RHS not in LHS) | AB → C |
| **Completely Non-trivial** | X ∩ Y = ∅ | A → B (no overlap) |
| **Full FD** | X → Y, but no proper subset of X determines Y | AB → C (neither A→C nor B→C) |
| **Partial FD** | X → Y, and some proper subset of X also determines Y | AB → C, but A→C also holds |
| **Transitive FD** | X → Y and Y → Z (Y is not a superkey, Y ↛ X) | A → B → C |

---

### Armstrong's Axioms (Sound & Complete)

These are the **inference rules** for deriving all possible FDs from a given set.

| Axiom | Rule | Notation |
|---|---|---|
| **Reflexivity** | If Y ⊆ X, then X → Y | (trivial dependencies) |
| **Augmentation** | If X → Y, then XZ → YZ | (add same attrs to both sides) |
| **Transitivity** | If X → Y and Y → Z, then X → Z | (chain dependencies) |

**Derived Rules (from Armstrong's Axioms):**

| Rule | Statement |
|---|---|
| **Union** | If X → Y and X → Z, then X → YZ |
| **Decomposition** | If X → YZ, then X → Y and X → Z |
| **Pseudo-transitivity** | If X → Y and WY → Z, then WX → Z |
| **Composition** | If X → Y and A → B, then XA → YB |

> **⚠️ Key Property:** Armstrong's Axioms are both **sound** (never generate incorrect FDs) and **complete** (can derive ALL valid FDs).

---

### Attribute Closure (X⁺)

The **closure of attribute set X** under FD set F is the set of all attributes functionally determined by X.

**Algorithm:**
```
X⁺ = X
repeat:
    for each FD: A → B in F:
        if A ⊆ X⁺:
            X⁺ = X⁺ ∪ B
until X⁺ does not change
return X⁺
```

**Uses:**
1. **Check if X is a super key:** X⁺ = all attributes of R
2. **Check if X → Y holds:** Y ⊆ X⁺
3. **Find candidate keys:** Minimal X such that X⁺ = all attributes

---

### Canonical Cover (Minimal Cover / Fc)

A **minimal set of FDs** equivalent to F (same closure) with:
1. No **redundant FDs** (removing any FD changes the closure).
2. No **extraneous attributes** on the LHS of any FD.
3. Each FD has a **single attribute** on the RHS.

**Algorithm to find Canonical Cover:**
```
Step 1: Decompose all FDs to have single attribute on RHS
        (using decomposition rule)

Step 2: Remove extraneous (redundant) attributes from LHS
        For each FD X → A:
            For each attribute B in X:
                If A ∈ (X - B)⁺ under current FDs:
                    Remove B from X

Step 3: Remove redundant FDs
        For each FD X → A:
            If A ∈ X⁺ under (F - {X → A}):
                Remove X → A from F

Step 4: Combine FDs with same LHS using union rule
```

> **⚠️ GATE Pitfall:** The order of removing extraneous attributes matters — you may get different (but equivalent) canonical covers. All are correct.

---

## Normal Forms Hierarchy

```
1NF ⊂ 2NF ⊂ 3NF ⊂ BCNF ⊂ 4NF ⊂ 5NF
```

Every relation in BCNF is also in 3NF, 2NF, and 1NF.

---

### First Normal Form (1NF)

**Definition:** A relation is in **1NF** if:
- All attributes have **atomic (indivisible) values**.
- No multi-valued attributes, no composite attributes, no nested relations.
- There is a **defined primary key**.

**Violation Example:**
```
Student(Roll, Name, Phones)
  (1, "Amit", {9876, 9123})  ← Phones is multi-valued → NOT 1NF
```

**Fix:** Create separate table for phones or separate rows.

---

### Second Normal Form (2NF)

**Definition:** A relation is in **2NF** if:
1. It is in **1NF**, AND
2. **No non-prime attribute** is **partially dependent** on any candidate key.

**Partial Dependency:** A non-prime attribute depends on a **proper subset** of a candidate key.

> **⚠️ Key Insight:** If ALL candidate keys are **single attributes** (not composite), the relation is **automatically in 2NF** (partial dependency is impossible).

**Violation Example:**
```
R(StudentID, CourseID, StudentName, Grade)
CK = {StudentID, CourseID}

FD: StudentID → StudentName  ← Partial dependency!
    (StudentName depends on part of the CK)
```

**Fix:** Decompose:
```
R1(StudentID, StudentName)
R2(StudentID, CourseID, Grade)
```

---

### Third Normal Form (3NF)

**Definition:** A relation is in **3NF** if for every non-trivial FD **X → A**:
1. **X is a super key**, OR
2. **A is a prime attribute** (part of some candidate key).

**Equivalently:** No **non-prime attribute** is **transitively dependent** on any candidate key.

**Transitive Dependency:** CK → X → A where X is not a superkey.

**Violation Example:**
```
R(EmpID, DeptID, DeptName)
CK = {EmpID}
FDs: EmpID → DeptID, DeptID → DeptName

EmpID → DeptID → DeptName  ← Transitive dependency!
DeptID → DeptName violates 3NF:
  DeptID is not a superkey AND DeptName is not a prime attribute.
```

**Fix:**
```
R1(EmpID, DeptID)
R2(DeptID, DeptName)
```

---

### Boyce-Codd Normal Form (BCNF)

**Definition:** A relation is in **BCNF** if for every non-trivial FD **X → A**:
- **X is a super key**. (That's it — no exception for prime attributes.)

> **⚠️ GATE Critical Difference: 3NF vs. BCNF**
> - 3NF allows FD X → A where A is a **prime attribute** even if X is not a superkey.
> - BCNF does NOT allow this exception.
> - BCNF ⊂ 3NF: Every BCNF relation is in 3NF, but NOT vice versa.

**When does 3NF ≠ BCNF?**
- When there exists an FD like **X → A** where **X is NOT a super key** but **A IS a prime attribute**.
- This satisfies 3NF (condition 2) but violates BCNF.

**Classic Example:**
```
R(Student, Course, Instructor)
FDs: {Student, Course} → Instructor
     Instructor → Course

CKs: {Student, Course} and {Student, Instructor}

Check Instructor → Course:
  Instructor is NOT a superkey → Violates BCNF
  But Course IS a prime attribute → Satisfies 3NF

Conclusion: R is in 3NF but NOT in BCNF.
```

---

### Fourth Normal Form (4NF)

**Definition:** A relation is in **4NF** if for every non-trivial **Multi-Valued Dependency (MVD)** X →→ Y:
- **X is a super key**.

**Multi-Valued Dependency (MVD):** X →→ Y means the set of Y values associated with an X value is independent of the other attributes.

> **GATE Tip:** 4NF is rarely tested in depth. Know the definition and one example.

---

## Decomposition Properties

When decomposing a relation R into R₁ and R₂, two critical properties must be checked:

### 1. Lossless Join (Lossless Decomposition)

**Definition:** A decomposition is **lossless** if joining R₁ and R₂ back produces **exactly R** (no spurious tuples).

**Test for Binary Decomposition** (R into R₁ and R₂):

A decomposition is lossless if and only if:
```
(R₁ ∩ R₂) → (R₁ - R₂)   is in F⁺
          OR
(R₁ ∩ R₂) → (R₂ - R₁)   is in F⁺
```

**In simple terms:** The **common attributes** must be a **super key** of at least one of the decomposed relations.

> **⚠️ GATE Favourite Rule:** Check if `R₁ ∩ R₂` is a super key of R₁ OR R₂.

**Example:**
```
R(A, B, C), FD: A → B
Decompose into R₁(A, B) and R₂(A, C)
R₁ ∩ R₂ = {A}
A⁺ = {A, B} → A is a superkey of R₁(A, B) ✅
→ Lossless decomposition ✅
```

### 2. Dependency Preservation

**Definition:** A decomposition is **dependency preserving** if all original FDs can be checked by looking at **individual decomposed tables** without needing to join.

**Test:**
For each FD X → Y in F:
- Check if X → Y can be enforced using only the attributes of **some single** Rᵢ.
- More precisely, compute X⁺ using only FDs whose attributes are **entirely within** some Rᵢ.

**Formal:**
```
(F₁ ∪ F₂ ∪ ... ∪ Fₖ)⁺ = F⁺
where Fᵢ = projection of F onto Rᵢ's attributes
```

> **⚠️ GATE Critical Theorem:**
> - **3NF decomposition** can always be made **both lossless and dependency preserving**.
> - **BCNF decomposition** is always **lossless** but may **NOT** be dependency preserving.
> - It is **impossible** to always achieve BCNF with dependency preservation.

---

## BCNF Decomposition Algorithm

```
Result = {R}
while some Rᵢ in Result is not in BCNF:
    Find an FD X → Y that violates BCNF in Rᵢ
    Compute X⁺ in Rᵢ
    Replace Rᵢ with:
        Rᵢ₁ = X⁺ (all attributes determined by X within Rᵢ)
        Rᵢ₂ = X ∪ (Rᵢ - X⁺) (X plus remaining attributes)
```

**Property:** Always produces a **lossless** decomposition (because X is a key of Rᵢ₁).

---

## 3NF Decomposition Algorithm (Synthesis Method)

```
Step 1: Find the canonical cover Fc of F.
Step 2: For each FD X → A in Fc:
            Create a relation Rᵢ(X, A)
Step 3: Combine relations with same key.
Step 4: If no relation contains a candidate key of R:
            Add a relation containing any candidate key.
```

**Property:** Always produces a decomposition that is **both lossless and dependency preserving**.

---

## GATE Specific Focus Points

### Quick Normal Form Identification

**Decision Algorithm:**
```
Step 1: Find all candidate keys.
Step 2: Identify prime and non-prime attributes.
Step 3: For each non-trivial FD X → A:
    - Is X a superkey?
        → YES: This FD satisfies BCNF (and all lower NFs).
        → NO: Is A a prime attribute?
            → YES: Satisfies 3NF but NOT BCNF.
            → NO: Is X a proper subset of some CK?
                → YES: Violates 2NF (partial dependency).
                → NO: Violates 3NF (transitive dependency).
```

### Summary Decision Table

| FD X → A | X is superkey? | A is prime? | Highest NF satisfied |
|---|---|---|---|
| X → A | ✅ Yes | — | **BCNF** |
| X → A | ❌ No | ✅ Yes | **3NF** (not BCNF) |
| X → A | ❌ No | ❌ No, X is proper subset of CK | **1NF** (violates 2NF — partial dep) |
| X → A | ❌ No | ❌ No, X is not a subset of CK | **2NF** (violates 3NF — transitive dep) |

> **⚠️ GATE Trap:** The **overall** NF of the relation is determined by the **weakest** (lowest NF) among ALL FDs.

---

### Important Theorems for GATE

1. **Every 2-attribute relation is in BCNF** (always — no FD can violate BCNF with just 2 attributes).
2. **If all candidate keys are single attributes → relation is at least in 2NF** (no partial dependency possible).
3. **If there are no non-prime attributes → relation is in 3NF** (every attribute is prime — the exception condition always holds).
4. **BCNF decomposition may not preserve dependencies.**
5. **3NF synthesis always preserves dependencies AND is lossless.**
6. **A relation with only one candidate key is in 3NF iff it is in BCNF** (the 3NF exception for prime attributes cannot kick in with only one CK unless another FD creates more CKs).

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| "If there's no partial dependency, it's in 3NF" | **Wrong.** No partial dep → 2NF. Still need to check transitive dep for 3NF |
| "3NF = no transitive dependency" | Only for non-prime attributes. FD X→A where A is prime doesn't violate 3NF |
| "BCNF and 3NF are the same" | BCNF is **stricter**. 3NF allows X→A when A is prime and X is not a superkey |
| "BCNF decomposition preserves all FDs" | **Not always.** BCNF decomposition can lose dependencies |
| "Canonical cover is unique" | **No.** Different canonical covers are possible depending on reduction order |
| "1NF means having a primary key" | 1NF means **atomic attribute values**. Having a PK is a separate relational model requirement |
| Confusing partial with transitive | Partial: non-prime depends on **subset of CK**. Transitive: non-prime depends on **non-key via chain** |

---

## 3 Worked Examples

### Example 1: Find Normal Form (Easy)

**Q:** R(A, B, C, D), FDs: A → B, A → C, A → D. Find the highest normal form.

**Solution:**
- A⁺ = {A, B, C, D} → A is a CK.
- Can any proper subset of A determine all attrs? A is a single attribute. So CK = {A}.
- Prime: {A}. Non-prime: {B, C, D}.
- Check each FD: A → B, A → C, A → D → A is a superkey ✅
- **All FDs have a superkey on LHS → BCNF**

---

### Example 2: 3NF but not BCNF (Medium — GATE Classic)

**Q:** R(A, B, C), FDs: AB → C, C → B. Find the highest normal form.

**Solution:**
- Find CKs:
  - (AB)⁺ = {A, B, C} → AB is a CK ✅
  - (AC)⁺ = A, C → apply C→B → {A, B, C} → AC is a CK ✅
  - A⁺ = {A} ❌, B⁺ = {B} ❌, C⁺ = {B, C} ❌
- CKs = {AB, AC}
- Prime = {A, B, C} (ALL attributes are prime!)

- Check FDs:
  - AB → C: AB is a superkey ✅ (satisfies BCNF)
  - C → B: C is NOT a superkey ❌ (violates BCNF)
    BUT B IS a prime attribute ✅ (satisfies 3NF)

- **Answer: 3NF (but NOT BCNF)**

---

### Example 3: Full Decomposition (GATE Level)

**Q:** R(A, B, C, D, E), FDs: A → BC, CD → E, B → D, E → A. Find all candidate keys and decompose into 3NF.

**Solution:**

**Step 1: Find Candidate Keys**
- Attributes only on LHS: none exclusively (A is on both sides via E→A)
- Let's try A⁺ = {A} → apply A→BC → {A,B,C} → apply B→D → {A,B,C,D} → apply CD→E → {A,B,C,D,E} ✅
- A is a CK.
- E⁺ = {E} → apply E→A → {A,E} → apply A→BC → {A,B,C,E} → apply B→D → {A,B,C,D,E} ✅
- E is a CK.
- B⁺ = {B,D} ❌. C⁺ = {C} ❌. D⁺ = {D} ❌.
- (CD)⁺ = {C,D,E} → {A,C,D,E} → {A,B,C,D,E} ✅ → CD is a CK.
- (BC)⁺ = {B,C,D} → {B,C,D,E} → {A,B,C,D,E} ✅ → BC is a CK.
- **CKs = {A, E, CD, BC}** (verify no subsets of CD/BC work — C alone: ❌, D alone: ❌, B alone: ❌)

**Step 2: Canonical Cover**
- A → BC → decompose: A → B, A → C
- CD → E
- B → D
- E → A
- Check extraneous attributes: none removable.
- Check redundant FDs: none redundant.
- Fc = {A → B, A → C, CD → E, B → D, E → A}
- Combine same LHS: Fc = {A → BC, CD → E, B → D, E → A}

**Step 3: 3NF Synthesis**
- From A → BC: R₁(A, B, C)
- From CD → E: R₂(C, D, E)
- From B → D: R₃(B, D)
- From E → A: R₄(E, A)
- Check: R₁ contains candidate key A ✅ (no extra relation needed)

**Final 3NF decomposition: {R₁(A,B,C), R₂(C,D,E), R₃(B,D), R₄(E,A)}**
- Lossless ✅, Dependency preserving ✅

---

## Revision Table

| Normal Form | Condition | Key Rule |
|---|---|---|
| **1NF** | Atomic values, defined PK | No multi-valued/composite attrs |
| **2NF** | 1NF + no partial dependencies | Non-prime must fully depend on entire CK |
| **3NF** | For X→A: X is superkey OR A is prime | No transitive dep of non-prime on CK |
| **BCNF** | For X→A: X MUST be superkey | No exceptions — stricter than 3NF |
| **4NF** | For X→→Y: X must be superkey | Eliminates MVD-based redundancy |

| Property | 3NF Decomposition | BCNF Decomposition |
|---|---|---|
| Lossless Join | ✅ Always | ✅ Always |
| Dependency Preserving | ✅ Always | ❌ Not always |
| Algorithm | Synthesis (canonical cover) | Decomposition (iterative) |

---

## Quick-Fire GATE Formulas

```
Armstrong's Axioms:  Reflexivity, Augmentation, Transitivity
Derived Rules:       Union, Decomposition, Pseudo-transitivity

Closure X⁺:         Iterative algorithm
Canonical Cover:     Single RHS → Remove extraneous LHS → Remove redundant FDs

Lossless test:       (R₁ ∩ R₂) must be superkey of R₁ or R₂

2-attribute relation → Always BCNF
All CKs single attribute → At least 2NF
All attributes prime → At least 3NF
3NF = BCNF when only one candidate key exists
```

---

*← [03 — ER to Relational Mapping](03_ER_to_Relational_Mapping.md) | [05 — Relational Algebra & Calculus →](05_Relational_Algebra_and_Calculus.md)*
