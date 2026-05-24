# 2. Relational Database Model — GATE CSE Complete Guide

> **GATE Weightage:** 2–4 marks. Questions test key identification (candidate keys, super keys), counting keys, integrity constraints, and understanding relational model fundamentals.

---

## Relational Database Model Overview

The **Relational Model** was proposed by **E.F. Codd (1970)** at IBM. It represents the database as a collection of **relations (tables)**. Each relation has a well-defined schema (structure) and an instance (data). It is the theoretical foundation for **SQL** and modern RDBMS.

---

## Key Definitions & Concepts

### Relation (Table)
- A relation is a **set of tuples** (rows), each conforming to the same **schema** (column definitions).
- Since it is a **set**, there are **no duplicate tuples** and **order of tuples does not matter**.
- **Degree** (Arity) = Number of attributes (columns).
- **Cardinality** = Number of tuples (rows).

### Schema vs. Instance
| Term | Definition |
|---|---|
| **Relational Schema** | The structure: relation name + attribute names + domains. E.g., `Student(Roll_No, Name, Age)` |
| **Relational Instance** | A snapshot of the data at a particular time (set of tuples) |

### Domain
- The set of **allowed values** for an attribute.
- E.g., Domain of `Age` = {1, 2, ..., 150} (positive integers)
- **Domain constraint:** Every value in a column must come from its domain.

### Tuple
- A single row in a relation.
- An **ordered list of values**, one for each attribute.

### NULL Values
- Represents **unknown**, **missing**, or **inapplicable** data.
- NULL ≠ 0, NULL ≠ empty string, NULL ≠ NULL.

---

## Keys — The Heart of the Relational Model

### Super Key
- A **set of attributes** that can **uniquely identify** every tuple in a relation.
- Every relation has at least one super key (the set of all attributes).

### Candidate Key
- A **minimal super key** — no proper subset of it is also a super key.
- A relation can have **multiple** candidate keys.

### Primary Key
- One candidate key **chosen** by the DBA to be the main identifier.
- **Cannot contain NULL** values.
- Only **one** primary key per relation.

### Alternate Key
- Candidate keys that are **not selected** as primary key.

### Foreign Key
- An attribute (or set of attributes) in one relation that **references the primary key** of another relation.
- Establishes a **referential integrity constraint** between two tables.
- A foreign key **can be NULL** (unless also part of the primary key).
- A foreign key **can reference its own table** (self-referencing).

### Composite Key
- A key consisting of **two or more attributes**.

### Prime vs. Non-Prime Attributes
| Type | Definition |
|---|---|
| **Prime Attribute** | An attribute that is part of **any** candidate key |
| **Non-Prime Attribute** | An attribute that is **not** part of any candidate key |

---

## Mathematical Foundations

### Counting Super Keys and Candidate Keys

This is a **very frequently asked GATE question type**.

**Given:** A relation R(A, B, C, D, E) with candidate keys `{A, B}` and `{C, D}`.

**Step 1: Count Super Keys from one candidate key**

If a candidate key has `k` attributes and the total number of attributes is `n`:
- Number of super keys **containing** that candidate key = **2^(n-k)**
- Because the remaining `(n-k)` attributes can either be included or not.

**Step 2: For multiple candidate keys, use Inclusion-Exclusion**

For candidate keys CK₁ and CK₂:
```
|SuperKeys| = |S(CK₁)| + |S(CK₂)| - |S(CK₁ ∪ CK₂)|
```

**Worked Computation:**
- R has 5 attributes: A, B, C, D, E
- CK₁ = {A, B} → Super keys containing {A,B} = 2^(5-2) = 2³ = **8**
- CK₂ = {C, D} → Super keys containing {C,D} = 2^(5-2) = 2³ = **8**
- CK₁ ∪ CK₂ = {A, B, C, D} → Super keys containing {A,B,C,D} = 2^(5-4) = 2¹ = **2**
- Total super keys = 8 + 8 - 2 = **14**

### General Formula (Two Candidate Keys)
```
Total Super Keys = 2^(n - |CK₁|) + 2^(n - |CK₂|) - 2^(n - |CK₁ ∪ CK₂|)
```

### Maximum Candidate Keys
- In a relation with `n` attributes, the maximum number of candidate keys of size `k` = **C(n, k)** = n! / (k! × (n-k)!)
- Specifically, maximum candidate keys of size 1 = n, size 2 = C(n,2), etc.

### Maximum Number of Super Keys (Single CK of size k)
```
Number of super keys = 2^(n - k)
```

---

## Integrity Constraints

### 1. Domain Constraint
- Every attribute value must belong to its **defined domain**.
- Example: `Age` must be a positive integer.

### 2. Key Constraint (Entity Integrity Constraint)
- **No two tuples** can have the same value for the primary key.
- Primary key attributes **cannot be NULL**.

### 3. Referential Integrity Constraint
- A foreign key value must either:
  - Match an existing primary key value in the referenced relation, OR
  - Be **NULL** (if allowed).

### 4. Tuple Constraint (Check Constraint)
- A condition that must hold for every tuple.
- Example: `Age >= 18`

### Referential Integrity — Violation Handling

| Operation on Referenced Table | Action Options |
|---|---|
| **DELETE** a referenced tuple | CASCADE, SET NULL, SET DEFAULT, RESTRICT/NO ACTION |
| **UPDATE** the referenced PK | CASCADE, SET NULL, SET DEFAULT, RESTRICT/NO ACTION |

| Action | Meaning |
|---|---|
| **CASCADE** | Propagate the change to all referencing tuples |
| **SET NULL** | Set the FK to NULL in referencing tuples |
| **SET DEFAULT** | Set the FK to a default value |
| **RESTRICT / NO ACTION** | Reject the operation if references exist |

---

## Relational Model Properties

| Property | Explanation |
|---|---|
| No duplicate tuples | A relation is a **set** |
| Tuple order irrelevant | {t₁, t₂} and {t₂, t₁} are the same relation |
| Attribute order irrelevant (logically) | Columns can be in any order |
| Attribute values are **atomic** | **1NF requirement** — no multi-valued or composite attributes |
| Each attribute has a domain | Values must come from a pre-defined set |

---

## GATE Specific Focus Points

### 1. Closure of a Set of Attributes
Given a set of **Functional Dependencies (FDs)** F, the **closure of an attribute set X** (denoted **X⁺**) is the set of all attributes functionally determined by X.

**Algorithm to find X⁺:**
```
X⁺ = X
repeat:
    for each FD: A → B in F:
        if A ⊆ X⁺:
            X⁺ = X⁺ ∪ B
until X⁺ does not change
```

**Why this matters:** If X⁺ contains **all attributes** of the relation, then X is a **super key**.

### 2. Finding All Candidate Keys

**Algorithm:**
1. Identify attributes that appear **only on the LHS** of FDs → These MUST be in every candidate key.
2. Identify attributes that appear **only on the RHS** → These are NEVER in any candidate key.
3. Identify attributes on **both sides** or **neither side** → May or may not be in candidate keys.
4. Start with the "must-be" set, compute closure. If it covers all attributes → it's the only CK.
5. If not, add one "maybe" attribute at a time and check closure.

### 3. Number of Relations/Tables
- A relation schema defines the **structure**.
- An **instance** (extension) is the current set of tuples.
- The number of possible relations over a domain:
  - If each attribute has domain of size `d` and there are `n` attributes:
  - Total possible tuples = **d^n**
  - Total possible relations (subsets of tuples) = **2^(d^n)**

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| "Primary key can be NULL" | **NO.** Primary key can **never** be NULL |
| "Foreign key cannot be NULL" | **YES it can** (unless it's also a PK or has NOT NULL constraint) |
| "A table can have only one candidate key" | A table can have **multiple** candidate keys |
| "Super key = Candidate key" | Every CK is a super key, but not vice versa. CK is **minimal** |
| "Counting super keys = counting CKs" | Use **2^(n-k)** for super keys, different approach for CKs |
| "Order of tuples matters" | **No.** Relations are **sets** — order is irrelevant |
| "A relation can have duplicate rows" | **No.** A relation is a set — no duplicates (SQL tables CAN have duplicates, but relations cannot) |
| Confusing relation (math) with SQL table | SQL tables allow duplicates and ordering; relations do not |

---

## 3 Worked Examples

### Example 1: Finding Candidate Keys (Easy)

**Q:** R(A, B, C, D) with FDs: `A → B`, `B → C`, `C → D`

**Solution:**
- A⁺ = {A} → apply A→B → {A,B} → apply B→C → {A,B,C} → apply C→D → {A,B,C,D} ✅
- A⁺ = all attributes → **A is a candidate key.**
- Can B be a CK? B⁺ = {B,C,D} ≠ all attributes. ❌
- **Candidate Key = {A}**

---

### Example 2: Counting Super Keys (Medium — GATE Favourite)

**Q:** R(A, B, C, D, E) with candidate keys `{A, B}` and `{A, C}`. Find the total number of super keys.

**Solution:**
Using Inclusion-Exclusion:
- |CK₁| = 2, |CK₂| = 2, |CK₁ ∪ CK₂| = |{A, B, C}| = 3, n = 5
- Super keys from CK₁ = 2^(5-2) = 8
- Super keys from CK₂ = 2^(5-2) = 8
- Super keys from CK₁ ∪ CK₂ = 2^(5-3) = 4
- Total = 8 + 8 - 4 = **12**

---

### Example 3: Integrity Constraint Violations (GATE Level)

**Q:** Given:
```
Department(DeptID PK, DeptName)
Employee(EmpID PK, Name, DeptID FK → Department)
```

Which of the following operations will **NOT** violate referential integrity?

(a) INSERT into Employee with DeptID = 999 (no such dept)
(b) DELETE from Department where DeptID = 10 (employees exist with DeptID=10)
(c) INSERT into Employee with DeptID = NULL
(d) UPDATE Employee SET DeptID = 999

**Solution:**
- (a) Violates RI — FK value 999 doesn't exist in Department ❌
- (b) Violates RI — Employees reference DeptID=10 ❌ (unless CASCADE)
- (c) **Does NOT violate RI** — FK can be NULL ✅
- (d) Violates RI — FK value 999 doesn't exist ❌

**Answer: (c)**

---

## Revision Table

| Concept | Definition | Key Property |
|---|---|---|
| **Super Key** | Set of attributes that uniquely identifies tuples | May not be minimal |
| **Candidate Key** | Minimal super key | No proper subset is a super key |
| **Primary Key** | Selected candidate key | Cannot be NULL, exactly one per table |
| **Foreign Key** | References PK of another table | Can be NULL, enforces RI |
| **Prime Attribute** | Part of some candidate key | — |
| **Non-Prime Attribute** | Not part of any candidate key | — |
| **Domain Constraint** | Values must be from defined domain | Basic type checking |
| **Entity Integrity** | PK cannot be NULL | Ensures identifiability |
| **Referential Integrity** | FK must match existing PK or be NULL | Links tables |

---

## Quick-Fire GATE Formulas

```
Super keys from CK of size k (n attributes) = 2^(n-k)

Two CKs: |SK| = 2^(n-|CK₁|) + 2^(n-|CK₂|) - 2^(n-|CK₁ ∪ CK₂|)

Max possible tuples (domain d, n attrs) = d^n

Max possible relations = 2^(d^n)

Attribute closure: X⁺ algorithm (iterative)

CK identification: LHS-only attributes MUST be in CK
```

---

*← [01 — ER Model](01_ER_Model.md) | [03 — ER to Relational Mapping →](03_ER_to_Relational_Mapping.md)*
