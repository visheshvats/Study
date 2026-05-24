# 1. Entity-Relationship (ER) Model — GATE CSE Complete Guide

> **GATE Weightage:** 2–4 marks almost every year. Questions typically test cardinality constraints, minimum number of tables from an ER diagram, and identification of weak entities.

---

## ER Model Overview

The **Entity-Relationship (ER) Model** is a high-level conceptual data model proposed by **Peter Chen (1976)**. It provides a graphical notation for representing the logical structure of a database. It is used during the **conceptual design phase** of database design and is independent of any specific DBMS.

**Why it matters for GATE:** You will be asked to count minimum tables, identify keys, resolve ambiguities in participation/cardinality, and map ER diagrams to relational schemas.

---

## Key Definitions & Concepts

### Entity
- An **entity** is a "thing" or "object" in the real world that is distinguishable from other objects.
- An **entity set** is a collection of similar entities (e.g., all students).
- Represented as a **rectangle** in ER diagrams.

### Attributes
- Properties that describe an entity.
- Represented as **ovals** connected to their entity rectangle.

| Attribute Type | Symbol | Description | Example |
|---|---|---|---|
| **Simple** | Plain oval | Atomic, indivisible | `Roll_No` |
| **Composite** | Oval with sub-ovals | Can be divided into sub-parts | `Name` → `First`, `Last` |
| **Derived** | Dashed oval | Computed from other attributes | `Age` (from `DOB`) |
| **Multi-valued** | Double oval | Can hold multiple values | `Phone_Numbers` |
| **Key Attribute** | Oval with underline | Uniquely identifies an entity | `Student_ID` |

### Relationship
- An **association** among two or more entities.
- Represented as a **diamond** in ER diagrams.
- A **relationship set** is a set of relationships of the same type.
- Relationships can also have **descriptive attributes** (e.g., `Date_of_Enrollment` on an "Enrolls" relationship).

### Relationship Degree
- **Unary (Recursive):** Entity related to itself (e.g., Employee `manages` Employee).
- **Binary:** Between two entity sets (most common).
- **Ternary:** Among three entity sets.
- **n-ary:** Among n entity sets.

---

## Cardinality Constraints (Mapping Cardinality)

Defines the number of entities to which another entity can be associated via a relationship.

| Type | Notation | Meaning | Example |
|---|---|---|---|
| **1:1** | 1 — 1 | One entity in A maps to at most one in B | Person ↔ Passport |
| **1:N** | 1 — N | One entity in A maps to many in B | Department → Employees |
| **N:1** | N — 1 | Many entities in A map to one in B | Employees → Department |
| **M:N** | M — N | Many in A map to many in B | Students ↔ Courses |

### GATE Formula: Minimum Number of Tables

This is a **very frequently asked** question type.

| Relationship Type | Participation | Min Tables Required |
|---|---|---|
| **1:1** | Both Total | **1** (merge all into one table) |
| **1:1** | One Total, One Partial | **2** (merge relationship into total-participation side) |
| **1:1** | Both Partial | **2** (merge relationship into either side) — but **3** is also correct if you don't merge |
| **1:N** | N-side Total | **2** (merge relationship into N-side) |
| **1:N** | N-side Partial | **3** (keep relationship separate) or **2** (merge into N-side with NULLs) |
| **M:N** | Any | **3** (always need a separate relationship table) |

> **⚠️ GATE Trap:** For M:N relationships, you **always** need a separate table. You can NEVER merge an M:N relationship into either entity table.

---

## Participation Constraints

### Total Participation (Existence Dependency)
- Every entity in the entity set **must** participate in at least one relationship.
- Represented by a **double line** connecting entity to relationship.
- Example: Every `Employee` **must** work in a `Department`.

### Partial Participation
- Some entities **may not** participate in any relationship.
- Represented by a **single line**.
- Example: Not every `Employee` manages a `Department`.

### (min, max) Notation
- A more precise way to express constraints: `(min, max)` on each entity's participation.
- `min = 0` → Partial participation.
- `min ≥ 1` → Total participation.
- `max = 1` → At most one.
- `max = N` → Unbounded.

**Example:**
```
Employee (1, N) ——< works_in >—— (1, 1) Department
```
- Each Employee works in exactly 1 Department → `(1,1)`
- Each Department has at least 1 Employee → `(1,N)`

---

## Weak Entity Sets

- A **weak entity** cannot be uniquely identified by its own attributes alone.
- It **depends** on a **strong (owner) entity** via an **identifying relationship**.
- Represented by a **double rectangle**.
- The identifying relationship is a **double diamond**.
- The weak entity has a **partial key (discriminator)** shown as a **dashed underline**.
- The **primary key** of a weak entity = PK of owner entity + discriminator of weak entity.

**Example:**
```
[Employee] ===< has >===[[Dependent]]
   EmpID                    Dep_Name (partial key)

PK of Dependent = (EmpID, Dep_Name)
```

> **⚠️ GATE Pitfall:** A weak entity **always has total participation** in its identifying relationship. If a question shows a weak entity with partial participation, the diagram is **invalid**.

> **⚠️ GATE Pitfall:** A weak entity can be the **owner** of another weak entity (chained weak entities). In that case, the PK propagates through the chain.

---

## Specialization & Generalization (EER)

### Specialization (Top-Down)
- Defining sub-entities (subclasses) from a higher-level entity (superclass) based on distinguishing features.
- Example: `Person` → `Student`, `Employee`

### Generalization (Bottom-Up)
- Combining multiple lower-level entities into a single higher-level entity.
- Example: `Car`, `Truck` → `Vehicle`

### Completeness Constraints
| Constraint | Meaning |
|---|---|
| **Total** | Every superclass entity **must** belong to at least one subclass. Shown with **double line**. |
| **Partial** | A superclass entity **may not** belong to any subclass. Shown with **single line**. |

### Disjointness Constraints
| Constraint | Meaning |
|---|---|
| **Disjoint (d)** | An entity can belong to **at most one** subclass. |
| **Overlapping (o)** | An entity can belong to **multiple** subclasses. |

### GATE Formula: Number of Tables for Generalization/Specialization

| Scenario | Tables Needed |
|---|---|
| Total & Disjoint | Minimum = **number of subclasses** (no need for superclass table) |
| Total & Overlapping | **1 + number of subclasses** (need superclass table to avoid redundancy) |
| Partial & Disjoint | **1 + number of subclasses** |
| Partial & Overlapping | **1 + number of subclasses** |

---

## Aggregation

- Used when a **relationship needs to participate in another relationship**.
- The entire relationship (along with its participating entities) is treated as a **higher-level entity**.
- Represented by drawing a **dashed rectangle** around the relationship and its entities.

**Example:** An `Employee` works on a `Project` (relationship: `works_on`). A `Manager` monitors the `works_on` relationship → Aggregation needed.

---

## Mathematical Foundations

### Counting Relationships in an Entity Set

- If entity set A has `m` entities and B has `n` entities:
  - Max **1:1** relationships = `min(m, n)`
  - Max **1:N** relationships (1 side is A) = `n` (each B maps to one A)
  - Max **M:N** relationships = `m × n`

### Degree of a Relationship
- Number of entity sets participating in the relationship.
- A relationship of degree `d` among entity sets E₁, E₂, ..., E_d with n₁, n₂, ..., n_d entities:
  - Maximum possible relationship instances = `n₁ × n₂ × ... × n_d`

---

## GATE Specific Focus Points

1. **Self-referential (recursive) relationships** — An entity participates in a relationship with itself. Each participation has a distinct **role** (e.g., `Employee` → `supervisor`, `subordinate`).
2. **Ternary vs. three binary relationships** — A ternary relationship captures constraints that **cannot** always be captured by three binary relationships. GATE loves testing this distinction.
3. **Identifying relationship** — Must connect a weak entity to its owner. Always **1:N** (owner is 1 side, weak entity is N side) with **total participation** on the weak side.
4. **Derived attributes** are **never stored** in the database — they are computed on the fly.

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| Confusing cardinality with participation | Cardinality = "how many", Participation = "must or may" |
| Assuming weak entity can exist without owner | Weak entity has **total participation** — it MUST have an owner |
| Forgetting discriminator in weak entity PK | PK = Owner's PK + Discriminator |
| Treating composite attributes as multi-valued | Composite = structured parts; Multi-valued = multiple values |
| Merging M:N into an entity table | M:N **always** requires a separate relationship table |
| Ignoring roles in recursive relationships | Must specify roles to distinguish participations |

---

## 3 Worked Examples

### Example 1: Basic ER Identification (Easy)

**Q:** A `Student` has attributes `Roll_No` (key), `Name`, `DOB`, `Age`, and `Phone_Numbers`. Identify each attribute type.

**Solution:**
| Attribute | Type |
|---|---|
| `Roll_No` | **Key attribute** (uniquely identifies) |
| `Name` | Could be **Simple** or **Composite** (`First_Name`, `Last_Name`) |
| `DOB` | **Simple** |
| `Age` | **Derived** (computed from `DOB`) |
| `Phone_Numbers` | **Multi-valued** (a student can have multiple phones) |

---

### Example 2: Minimum Tables (Medium — GATE Favourite)

**Q:** Consider the following ER diagram:
- Entity `Person` (PK: `PID`)
- Entity `Passport` (PK: `PassportNo`)
- Relationship `has` — **1:1** with **total participation on both sides**

What is the minimum number of tables required?

**Solution:**
- 1:1 + Both Total → We can merge everything into **1 table**.
- Table: `Person_Passport(PID, Name, ..., PassportNo, IssueDate, ...)`
- **Answer: 1**

---

### Example 3: Weak Entity & Ternary Relationship (GATE Level)

**Q:** Consider entities `Course`, `Section` (weak, discriminator: `SecNo`), and `Instructor`. `Section` is a weak entity of `Course`. `Instructor` teaches `Section`. How many minimum tables are needed?

**Solution:**
1. `Course(CourseID, CourseName, ...)` — Strong entity → 1 table
2. `Section(CourseID, SecNo, Room, ...)` — Weak entity → 1 table (PK = `CourseID + SecNo`)
3. Relationship `teaches(InstructorID, CourseID, SecNo)` — This is effectively a relationship between `Instructor` and `Section`.
   - If an instructor teaches at most one section (1:N from section to instructor), merge FK into `Section`.
   - If M:N, need separate table.
4. `Instructor(InstructorID, Name, ...)` — 1 table

- **Minimum tables (assuming 1:N): 3** (merge `teaches` into `Section`)
- **Minimum tables (assuming M:N): 4** (separate `teaches` table)

---

## Revision Table

| Concept | Key Point | ER Symbol |
|---|---|---|
| Entity | Object in the real world | Rectangle |
| Weak Entity | Cannot be identified alone | Double Rectangle |
| Attribute | Property of entity | Oval |
| Key Attribute | Uniquely identifies entity | Underlined Oval |
| Multi-valued | Multiple values | Double Oval |
| Derived | Computed from others | Dashed Oval |
| Composite | Divisible into parts | Oval with sub-ovals |
| Relationship | Association between entities | Diamond |
| Identifying Relationship | Links weak to owner entity | Double Diamond |
| Total Participation | Must participate | Double Line |
| Partial Participation | May participate | Single Line |
| Specialization/Generalization | ISA hierarchy | Triangle with "ISA" |
| Aggregation | Relationship in relationship | Dashed rectangle around relationship |

---

## Quick-Fire GATE Formulas

```
Min tables for 1:1 (Both Total)     = 1
Min tables for 1:1 (One Total)      = 2
Min tables for 1:1 (Both Partial)   = 2
Min tables for 1:N                  = 2 (merge into N-side)
Min tables for M:N                  = 3 (always separate table)
Weak entity PK                     = Owner PK + Discriminator
Max relationships (M:N) in |A|=m, |B|=n  = m × n
```

---

*Next: [02 — Relational Database Model →](02_Relational_Database_Model.md)*
