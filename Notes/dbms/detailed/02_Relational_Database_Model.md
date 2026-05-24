# 2. Relational Database Model — Detailed GATE CSE Guide

> **GATE Weightage:** 2–4 marks. This topic is the theoretical backbone of SQL and databases. Questions test your ability to find candidate keys, count super keys, and understand integrity constraints.

---

## What is the Relational Model?

Imagine a **spreadsheet** with rows and columns. That's essentially what the relational model is — a way to organize data into **tables** (called "relations" in formal terminology).

The **Relational Model** was proposed by **Edgar F. Codd** in **1970** while working at IBM. Before this, databases were hierarchical or network-based (complex and rigid). Codd's model was revolutionary because it was simple, mathematical, and powerful.

**Key insight:** In the relational model, ALL data is stored in **tables** (relations). Each table has **columns** (attributes) and **rows** (tuples). That's it! No pointers, no hierarchies, no networks — just tables.

---

## Understanding Relations (Tables)

### The Formal Definition

A **relation** is a **set of tuples** (rows), where each tuple has the same structure defined by the **schema** (column definitions).

Let's break this down with an example:

**Relation: Student**

| Roll_No | Name | Age | Dept |
|---|---|---|---|
| 101 | Amit | 20 | CS |
| 102 | Priya | 21 | EC |
| 103 | Rahul | 20 | CS |

In formal terms:
- **Relation name:** Student
- **Schema:** Student(Roll_No, Name, Age, Dept)
- **Attributes (columns):** Roll_No, Name, Age, Dept — there are 4 attributes
- **Tuples (rows):** (101, "Amit", 20, "CS"), (102, "Priya", 21, "EC"), etc. — there are 3 tuples
- **Degree (Arity):** 4 (number of columns)
- **Cardinality:** 3 (number of rows)

### Schema vs. Instance

Think of it like a **form template** vs. **filled forms**:

| Term | What is it? | Analogy | Changes? |
|---|---|---|---|
| **Schema** | The structure/design of the table | A blank form template | Rarely (fixed design) |
| **Instance** | The actual data in the table at a point in time | Filled-out forms | Frequently (data changes) |

The schema says: "This table has Roll_No (integer), Name (string), Age (integer), Dept (string)."
The instance says: "Right now, there are 3 students: Amit, Priya, and Rahul."

### Domain

A **domain** is the set of allowed values for an attribute. Think of it as the **data type + constraints**.

**Examples:**
- Domain of `Roll_No` = positive integers (1, 2, 3, ...)
- Domain of `Name` = strings up to 50 characters
- Domain of `Age` = integers from 1 to 150
- Domain of `Dept` = {"CS", "EC", "ME", "CE", "EE"}

The **domain constraint** says: every value in a column must come from its defined domain. You can't put "hello" in the Age column if its domain is integers.

### Important Properties of Relations

Since a relation is mathematically a **set** of tuples, it inherits properties of sets:

| Property | Meaning | Example |
|---|---|---|
| **No duplicate tuples** | Every row must be unique (at least in one attribute) | Can't have two identical rows |
| **Order of tuples doesn't matter** | {row1, row2} = {row2, row1} | Rows aren't "first" or "second" |
| **Order of attributes doesn't matter** (logically) | Columns can be in any order | Name can be before or after Age |
| **Attribute values are atomic** | Each cell has ONE indivisible value | No lists, no sets, no sub-tables in a cell |

> **⚠️ GATE Distinction — Relations vs. SQL Tables:**
> This is a subtle but important difference:
> - **Relations** (mathematical): No duplicates, no order, strictly atomic values
> - **SQL Tables**: CAN have duplicate rows (unless explicitly prevented), DO have an order, may have some non-atomic features
>
> When a GATE question says "relation," it means the mathematical definition. When it says "table" in SQL context, duplicates might be possible.

### NULL Values

**NULL** represents missing, unknown, or inapplicable information. It's a special marker, not a value.

**Examples of why NULL exists:**
- A student's phone number is **unknown** (they haven't provided it yet)
- An employee's passport number is **inapplicable** (they don't have a passport)
- A product's discount is **undefined** (no discount scheme exists yet)

**Critical rules about NULL:**
```
NULL ≠ 0          (NULL is not zero)
NULL ≠ ""         (NULL is not an empty string)
NULL ≠ NULL       (you can't compare NULLs — the result is UNKNOWN)
NULL + 5 = NULL   (any arithmetic with NULL gives NULL)
```

> We'll dive deep into how SQL handles NULL in the SQL chapter. For now, just remember: NULL means "we don't know."

---

## Keys — The Heart of the Relational Model

Keys are the **most important concept** in the relational model. They identify rows, link tables, and enforce data integrity. GATE loves testing your understanding of keys!

### Understanding Keys Through an Analogy

Think of a classroom of students. How do you uniquely identify each student?
- By their **Roll_No** — unique to each student ✅
- By their **Aadhaar_Number** — also unique ✅
- By their **Name** — might NOT be unique (two students could be named "Amit") ❌
- By their **Name + DOB** combination — probably unique ✅ (unlikely two people have the same name AND same birthday)

Each of these "identifiers" represents a different type of key.

---

### Super Key

A **super key** is ANY set of attributes that can uniquely identify every tuple (row) in a relation. There is NO minimality requirement.

**Think of it as:** "A combination of columns that, if you look at those columns only, every row is different."

**Example with Student(Roll_No, Name, Age, Dept):**

The following are ALL super keys:
- `{Roll_No}` — unique by itself ✅
- `{Roll_No, Name}` — adding Name to Roll_No is still unique ✅
- `{Roll_No, Age}` — still unique ✅
- `{Roll_No, Name, Age}` — still unique ✅
- `{Roll_No, Name, Age, Dept}` — the entire set is always a super key ✅

**Key observation:** If X is a super key, then **any superset of X** is also a super key. Adding more attributes to a unique identifier can never make it non-unique.

> **Every relation has at least one super key:** the set of ALL attributes (because a relation has no duplicate rows by definition, so the combination of all attributes must be unique).

---

### Candidate Key

A **candidate key** is a **minimal super key** — a super key from which you **cannot remove any attribute** without losing the uniqueness property.

**Think of it as:** "The smallest possible combination of columns that still uniquely identifies every row."

**Example:**
- `{Roll_No}` is a candidate key — it's a super key, and you can't remove anything from it (it's already just one attribute)
- `{Roll_No, Name}` is NOT a candidate key — it's a super key, but you can remove `Name` and `{Roll_No}` alone is still unique → so {Roll_No, Name} is not minimal

**A relation can have MULTIPLE candidate keys.** For example:
- Student(Roll_No, Aadhaar, Name, Dept)
  - CK₁ = {Roll_No} — unique identifier
  - CK₂ = {Aadhaar} — also a unique identifier
  - Both are candidate keys because both are minimal super keys

> **GATE Tip:** "Candidate key" literally means "candidate for being the primary key" — there are multiple candidates, and you pick one.

---

### Primary Key

The **primary key** is the candidate key that is **chosen** by the database administrator (DBA) to be the main identifier for the table.

**Rules:**
1. Exactly **ONE** primary key per table (even if there are multiple candidate keys)
2. Primary key values **cannot be NULL** (entity integrity constraint)
3. Primary key values must be **unique** (key constraint)

**Example:**
```
Student(Roll_No PK, Aadhaar, Name, Dept)
```
Here, `Roll_No` is chosen as the primary key. `Aadhaar` becomes an alternate key.

### Alternate Key

Any candidate key that is **NOT chosen** as the primary key.

In our example, `Aadhaar` is an alternate key (it could have been the PK, but we chose Roll_No instead).

### Composite Key

A key that consists of **two or more attributes**. The individual attributes may not be unique by themselves, but their **combination** is unique.

**Example:**
```
Enrollment(StudentID, CourseID, Grade)
```
- `StudentID` alone is not unique (a student enrolls in many courses)
- `CourseID` alone is not unique (many students enroll in a course)
- `{StudentID, CourseID}` together is unique (a student enrolls in a specific course only once)
- So {StudentID, CourseID} is a composite candidate key

---

### Foreign Key

A **foreign key** is an attribute (or set of attributes) in one table that **references the primary key** of another table. It creates a **link** between two tables.

**Rules:**
1. The foreign key value MUST exist as a primary key value in the referenced table, **OR** it can be **NULL** (if allowed)
2. A foreign key CAN reference its own table (self-referencing)
3. A foreign key CAN be part of the primary key of its own table

**Example:**
```
Department(DeptID PK, DeptName)
Student(Roll_No PK, Name, DeptID FK → Department)
```

The `DeptID` in Student is a foreign key that references `DeptID` in Department.

- If Department has: {CS, EC, ME}
- Then Student's DeptID can only be: CS, EC, ME, or NULL
- Student with DeptID = "AIML" would violate the foreign key constraint (because "AIML" doesn't exist in Department)

> **⚠️ Common Misconception:** "Foreign keys can never be NULL."
> This is **FALSE!** A foreign key CAN be NULL (unless it also has a NOT NULL constraint or is part of the primary key). A NULL FK means "this student is not assigned to any department yet."

---

### Prime vs. Non-Prime Attributes

This distinction becomes critical in normalisation (Chapter 4):

| Type | Definition | Example |
|---|---|---|
| **Prime Attribute** | An attribute that appears in **at least one** candidate key | If CKs are {A,B} and {A,C}, then A, B, C are prime |
| **Non-Prime Attribute** | An attribute that does NOT appear in ANY candidate key | If CKs are {A,B}, then C, D, E are non-prime |

**Why this matters:** Normalisation rules (especially 2NF and 3NF) treat prime and non-prime attributes differently.

---

## Counting Super Keys — GATE Favourite!

This is one of the most frequently asked question types. Let's master it step by step.

### The Basic Formula

If a candidate key has **k** attributes and the total relation has **n** attributes:

```
Number of super keys containing this CK = 2^(n - k)
```

**Why?** The CK's k attributes MUST be present (they're the key). The remaining (n - k) attributes can each independently be present or absent (2 choices each). So: 2 × 2 × ... × 2 = 2^(n-k).

**Example:**
```
R(A, B, C, D, E)   →  n = 5
CK = {A, B}         →  k = 2

Super keys containing {A, B} = 2^(5-2) = 2^3 = 8
```

These 8 super keys are:
{A,B}, {A,B,C}, {A,B,D}, {A,B,E}, {A,B,C,D}, {A,B,C,E}, {A,B,D,E}, {A,B,C,D,E}

### When There Are Multiple Candidate Keys — Inclusion-Exclusion Principle

If a relation has two candidate keys CK₁ and CK₂, the super keys from CK₁ and CK₂ may **overlap** (some super keys contain both CK₁ and CK₂). To avoid double-counting, use the **inclusion-exclusion principle**:

```
Total Super Keys = |SK(CK₁)| + |SK(CK₂)| − |SK(CK₁ ∪ CK₂)|
```

Where:
- |SK(CK₁)| = super keys containing CK₁ = 2^(n - |CK₁|)
- |SK(CK₂)| = super keys containing CK₂ = 2^(n - |CK₂|)
- |SK(CK₁ ∪ CK₂)| = super keys containing BOTH CK₁ and CK₂ = 2^(n - |CK₁ ∪ CK₂|)

### Detailed Worked Example

**Q:** R(A, B, C, D, E) with candidate keys {A, B} and {A, C}. Find all super keys.

**Step 1:** Identify the parameters.
- n = 5 (total attributes)
- CK₁ = {A, B}, |CK₁| = 2
- CK₂ = {A, C}, |CK₂| = 2
- CK₁ ∪ CK₂ = {A, B, C}, |CK₁ ∪ CK₂| = 3

**Step 2:** Calculate super keys from each CK.
- Super keys from CK₁ = 2^(5-2) = 8
- Super keys from CK₂ = 2^(5-2) = 8
- Super keys from CK₁ ∪ CK₂ = 2^(5-3) = 4

**Step 3:** Apply inclusion-exclusion.
- Total = 8 + 8 - 4 = **12**

**Verification (listing all 12):**
From {A,B}: {AB, ABC, ABD, ABE, ABCD, ABCE, ABDE, ABCDE}
From {A,C}: {AC, ACD, ACE, ABCD, ABCE, ACDE, ABCDE}
Wait — ABCD, ABCE, ABCDE appear in both lists. After removing duplicates:
{AB, ABC, ABD, ABE, AC, ACD, ACE, ABCD, ABCE, ABDE, ACDE, ABCDE} = **12** ✅

### For Three or More Candidate Keys

Extend the inclusion-exclusion:
```
|SK| = Σ|SK(CKᵢ)| − Σ|SK(CKᵢ ∪ CKⱼ)| + Σ|SK(CKᵢ ∪ CKⱼ ∪ CKₖ)| − ...
```

This follows the general inclusion-exclusion formula. For 3 CKs:
```
Total = |SK₁| + |SK₂| + |SK₃| − |SK₁₂| − |SK₁₃| − |SK₂₃| + |SK₁₂₃|
```

---

## Finding Candidate Keys — The Systematic Approach

Given a relation R and a set of functional dependencies F, here's how to find ALL candidate keys:

### Step-by-Step Algorithm

**Step 1: Categorize attributes**

Look at which sides of FDs each attribute appears on:

| Category | Appears on | Role | In CK? |
|---|---|---|---|
| **L-only** | Only on LEFT side of FDs | Always determines other attrs | **MUST** be in every CK |
| **R-only** | Only on RIGHT side of FDs | Always determined, never determines | **NEVER** in any CK |
| **Both** | On both LEFT and RIGHT | Sometimes determines, sometimes determined | **MAY** be in some CKs |
| **Neither** | Not in any FD | Independent | **MUST** be in every CK |

> **Key insight:** "L-only" and "Neither" attributes MUST be in every candidate key (because no FD can derive them from other attributes).

**Step 2: Start with must-be attributes**

Take all "L-only" and "Neither" attributes. Call this set M (must-be set).

**Step 3: Check if M is a superkey**

Compute M⁺ (closure of M under the given FDs). If M⁺ = all attributes → M is the **only** candidate key. Done!

**Step 4: If M is not a superkey**

Try adding **one "Both" attribute** at a time to M:
- For each "Both" attribute X: compute (M ∪ {X})⁺
- If it covers all attributes → M ∪ {X} is a candidate key
- If not → try combinations of two "Both" attributes, etc.

### Detailed Example

**Q:** R(A, B, C, D, E) with FDs: A → B, BC → D, D → E

**Step 1: Categorize:**
- A: LHS of A→B. Not on RHS. → **L-only**
- B: RHS of A→B. LHS of BC→D. → **Both**
- C: LHS of BC→D. Not on RHS. → **L-only**
- D: RHS of BC→D. LHS of D→E. → **Both**
- E: RHS of D→E. Not on LHS anywhere alone. → **R-only**

**Step 2: Must-be set = {A, C}** (L-only attributes)

**Step 3: Compute {A,C}⁺:**
- Start: {A, C}
- A → B: A ∈ {A,C} → add B → {A, B, C}
- BC → D: BC ⊆ {A,B,C} → add D → {A, B, C, D}
- D → E: D ∈ {A,B,C,D} → add E → {A, B, C, D, E} ✅ All attributes!

**{A, C}⁺ = {A, B, C, D, E}** → {A, C} is a superkey.

**Step 4: Is {A, C} minimal?** Check subsets:
- {A}⁺ = {A, B} (only A→B applies) ≠ all attributes ❌
- {C}⁺ = {C} (no single C FD) ≠ all attributes ❌

So neither A nor C alone works → {A, C} IS minimal → **{A, C} is a candidate key.**

Since the must-be set itself is a CK, and there are no "Both" attributes that need to be added, **{A, C} is the ONLY candidate key.**

---

## Attribute Closure (X⁺) — Explained Simply

### What is Attribute Closure?

Given a set of functional dependencies F, the **closure of a set of attributes X** (written X⁺) is the set of **ALL attributes** that can be determined from X using the FDs.

**Intuition:** "If I know the values of attributes in X, what other attribute values can I figure out?"

### The Algorithm (with detailed walkthrough)

```
X⁺ = X    (start with what you know)

Repeat:
    For each FD: A → B in F:
        If all attributes of A are already in X⁺:
            Add all attributes of B to X⁺
Until X⁺ doesn't change anymore
```

### Worked Example

**R(A, B, C, D, E)**, FDs: A → BC, B → D, CD → E

**Find {A}⁺:**

| Iteration | X⁺ | FD applied | Reason |
|---|---|---|---|
| Start | {A} | — | Start with A |
| 1 | {A, B, C} | A → BC | A is in X⁺, so we can determine B and C |
| 2 | {A, B, C, D} | B → D | B is in X⁺, so we can determine D |
| 3 | {A, B, C, D, E} | CD → E | Both C and D are in X⁺, so we can determine E |
| 4 | {A, B, C, D, E} | — | No change → stop |

**{A}⁺ = {A, B, C, D, E}** = ALL attributes → A is a super key!
Since A is a single attribute, it's automatically minimal → **A is a candidate key.**

### Uses of Attribute Closure

1. **Check if X is a super key:** If X⁺ = all attributes → Yes
2. **Check if X → Y holds:** If Y ⊆ X⁺ → Yes, the FD X → Y is implied
3. **Find candidate keys:** Find minimal X such that X⁺ = all attributes

---

## Integrity Constraints — Rules That Keep Your Data Clean

### 1. Domain Constraint

Every attribute value must belong to its **defined domain** (allowed set of values).

**Example:** If `Age` is defined as an integer between 0 and 150, then inserting `Age = -5` or `Age = "twenty"` would violate the domain constraint.

This is the most basic constraint — like type checking in programming.

### 2. Key Constraint (Entity Integrity Constraint)

Two rules combined:
1. **No two tuples** can have the same primary key value → **Uniqueness**
2. **No attribute** of the primary key can be **NULL** → **Not-NULL**

**Why can't PK be NULL?** The whole purpose of a primary key is to identify a row. If the PK is NULL, you can't identify the row. It's like having a person with no name, no ID, nothing — you just can't refer to them.

### 3. Referential Integrity Constraint (Foreign Key Constraint)

If a foreign key in table A references table B's primary key, then:
- Every non-NULL FK value in A **must exist** as a PK value in B
- The referenced PK value must be **valid and existing**

**Example:**
```
Department:  DeptID = {CS, EC, ME}
Student:     DeptID FK = CS ✅, EC ✅, NULL ✅, AIML ❌ (doesn't exist!)
```

### What Happens When You Violate Referential Integrity?

There are two scenarios where violations can occur:

**Scenario 1: DELETE a referenced row**
If you delete the Department "CS" and there are students with DeptID = "CS", what should happen?

**Scenario 2: UPDATE a referenced PK**
If you change Department's DeptID from "CS" to "CSE", what about students with DeptID = "CS"?

SQL provides these options:

| Action | What happens | Example |
|---|---|---|
| **CASCADE** | The change automatically propagates to all referencing rows | Delete CS dept → all CS students are also deleted |
| **SET NULL** | FK in referencing rows is set to NULL | Delete CS dept → CS students' DeptID becomes NULL |
| **SET DEFAULT** | FK in referencing rows is set to a default value | Delete CS dept → CS students' DeptID becomes "General" |
| **RESTRICT / NO ACTION** | The operation is **rejected** if references exist | Can't delete CS dept while students exist with DeptID = CS |

### 4. Tuple Constraint (Check Constraint)

A condition that every tuple must satisfy.

**Example:**
```sql
CHECK (Age >= 18)             -- Every student must be at least 18
CHECK (Salary > 0)            -- Salary must be positive
CHECK (End_Date > Start_Date) -- End date must be after start date
```

---

## Common Pitfalls — Avoid These!

### Pitfall 1: "Primary key can be NULL"

**WRONG!** The primary key can **NEVER** be NULL. This is the entity integrity constraint. If you need NULLs, the attribute cannot be the PK.

### Pitfall 2: "Foreign key can never be NULL"

**Also WRONG!** A foreign key CAN be NULL (unless it's also part of the PK or has a NOT NULL constraint). A NULL FK simply means "not associated with any entity in the referenced table."

### Pitfall 3: "A table can have only one candidate key"

**WRONG!** A table can have **multiple** candidate keys. You choose ONE as the primary key; the rest become alternate keys.

### Pitfall 4: "Super key = Candidate key"

**WRONG!** Every candidate key IS a super key, but not vice versa. A candidate key is a **minimal** super key. {A,B,C} might be a super key, but if {A} alone is also a super key, then {A,B,C} is NOT a candidate key (because it's not minimal).

### Pitfall 5: "A relation can have duplicate rows"

**Not in the relational model!** A relation is a SET of tuples — sets don't have duplicates. (SQL tables CAN have duplicates, but that's SQL deviating from the pure relational model.)

### Pitfall 6: Counting super keys by listing instead of formula

For large relations, listing all super keys is impractical. Use the **2^(n-k)** formula with **inclusion-exclusion** for multiple CKs. This is the expected approach in GATE.

---

## Revision Table

| Concept | Definition | Key Property |
|---|---|---|
| **Relation** | Set of tuples (table) | No duplicates, order irrelevant |
| **Schema** | Structure (column names + types) | Fixed design |
| **Instance** | Current data (rows) | Changes over time |
| **Domain** | Allowed values for an attribute | Type checking |
| **Super Key** | Set of attrs that uniquely identifies | May not be minimal |
| **Candidate Key** | Minimal super key | No proper subset is also a key |
| **Primary Key** | Chosen candidate key | Cannot be NULL, exactly one per table |
| **Foreign Key** | References PK of another table | CAN be NULL, enforces referential integrity |
| **Prime Attribute** | Part of some candidate key | Important for normalisation |
| **Non-Prime** | Not part of any candidate key | Important for normalisation |
| **Entity Integrity** | PK cannot be NULL | Ensures identifiability |
| **Referential Integrity** | FK must match existing PK or be NULL | Links tables |

---

## Quick-Fire GATE Formulas

```
Number of super keys (1 CK of size k, n total attrs):
    = 2^(n - k)

Number of super keys (2 CKs):
    = 2^(n-|CK₁|) + 2^(n-|CK₂|) − 2^(n-|CK₁ ∪ CK₂|)

Max possible tuples over domain d with n attributes:
    = d^n

Max possible relations:
    = 2^(d^n)    (each tuple is either present or not)

Finding CKs:
    1. L-only / Neither attrs → MUST be in every CK
    2. R-only attrs → NEVER in any CK
    3. Compute closure → check if superkey → check minimality
```

---

*← [01 — ER Model](01_ER_Model.md) | [03 — ER to Relational Mapping →](03_ER_to_Relational_Mapping.md)*
