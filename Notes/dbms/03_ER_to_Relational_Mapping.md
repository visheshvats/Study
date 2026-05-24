# 3. ER to Relational Model Mapping — GATE CSE Complete Guide

> **GATE Weightage:** 1–2 marks. Questions ask for the minimum number of tables, correct schema mapping, or identifying primary/foreign keys after conversion.

---

## ER to Relational Mapping Overview

Converting an ER diagram to a relational schema is a **systematic, rule-based** process. The goal is to translate entities, relationships, and constraints into **tables, columns, and keys** while preserving all semantic information.

---

## Key Definitions & Concepts

### Mapping Rules — Step by Step

The standard algorithm (by Elmasri & Navathe) has **7 steps**:

---

### Step 1: Map Strong (Regular) Entity Sets

- Each **strong entity** becomes a **separate table**.
- All **simple attributes** become columns.
- **Composite attributes**: include only the **leaf (simple component) attributes**.
- **Derived attributes**: **do NOT include** (they are computed).
- **Multi-valued attributes**: handled separately in Step 6.
- The **primary key** of the entity becomes the **primary key** of the table.

**Example:**
```
Entity: Employee(EmpID, Name(FName, LName), Age, DOB)

Table: Employee(EmpID PK, FName, LName, DOB)
  → Name is composite → use FName, LName
  → Age is derived from DOB → excluded
```

---

### Step 2: Map Weak Entity Sets

- Each **weak entity** becomes a **separate table**.
- Include **all simple attributes** of the weak entity.
- Include the **primary key of the owner entity** as a **foreign key**.
- **Primary key** of weak entity table = **Owner's PK + Discriminator (Partial Key)**.

**Example:**
```
Owner Entity: Employee(EmpID PK)
Weak Entity: Dependent(Dep_Name discriminator, Relationship, DOB)

Table: Dependent(EmpID FK, Dep_Name, Relationship, DOB)
  PK = (EmpID, Dep_Name)
```

---

### Step 3: Map Binary 1:1 Relationship Sets

Three approaches (choose based on participation):

| Participation | Strategy | Tables Needed |
|---|---|---|
| **Both Total** | Merge both entities and the relationship into **one table** | **1** |
| **One Total** | Add FK to the **total participation side** | **2** |
| **Both Partial** | Either add FK to one side (with NULLs) → **2**, OR create separate relationship table → **3** |

**Preferred approach (GATE standard):** Add the FK to the side with **total participation** to avoid NULLs.

**Example (One Total):**
```
Employee(EmpID PK) —1:1— manages —— Department(DeptID PK)
(Employee: partial, Department: total — every dept has exactly one manager)

Table Employee(EmpID PK, Name, ...)
Table Department(DeptID PK, DeptName, ManagerID FK → Employee)
  → FK added to Department (total participation side)
```

---

### Step 4: Map Binary 1:N Relationship Sets

- Add the **primary key of the 1-side** as a **foreign key** in the **N-side** table.
- Also add any **relationship attributes** to the N-side table.
- **No separate table needed** (unless N-side has partial participation and you want to avoid NULLs).

**Example:**
```
Department(DeptID PK) —1:N— works_in —— Employee(EmpID PK)

Table Employee(EmpID PK, Name, DeptID FK → Department)
  → FK added to Employee (N-side)
```

> **⚠️ GATE Key Rule:** In 1:N, the FK always goes on the **N-side** (many side).

---

### Step 5: Map Binary M:N Relationship Sets

- Create a **new separate table** (relationship table / junction table).
- Include the **primary keys of both entities** as **foreign keys**.
- The **primary key** of the new table = **combination of both FKs**.
- Also include any **relationship attributes**.

**Example:**
```
Student(SID PK) —M:N— Enrolls(Grade) —— Course(CID PK)

Table Enrolls(SID FK, CID FK, Grade)
  PK = (SID, CID)
```

> **⚠️ Critical:** M:N relationships **ALWAYS** require a separate table. You cannot merge them.

---

### Step 6: Map Multi-Valued Attributes

- Create a **new table** for each multi-valued attribute.
- Include the **primary key of the entity** as a **foreign key**.
- Include the **multi-valued attribute** as a column.
- **Primary key** = FK + the multi-valued attribute.

**Example:**
```
Employee(EmpID PK, Phone_Numbers{multi-valued})

Table Employee(EmpID PK, Name, ...)
Table Emp_Phone(EmpID FK, Phone_Number)
  PK = (EmpID, Phone_Number)
```

---

### Step 7: Map N-ary (n > 2) Relationship Sets

- Create a **new table** for the relationship.
- Include the **primary keys of all participating entities** as **foreign keys**.
- The **primary key** of the relationship table depends on cardinality:
  - If all sides are **many**: PK = all foreign keys combined.
  - If some side is **1**: that FK is **NOT** part of the PK (it becomes a regular FK).
- Include any **relationship attributes**.

**Example:**
```
Ternary: Supplier(SID) —— Supplies(Qty) —— Part(PID) —— Project(ProjID)
All M:N:P

Table Supplies(SID FK, PID FK, ProjID FK, Qty)
  PK = (SID, PID, ProjID)
```

---

## Mathematical Foundations

### Minimum Number of Tables — Master Formula

This is the **most frequently tested** concept from ER-to-Relational mapping.

**Base count:**
```
Tables = (Number of Strong Entities)
       + (Number of Weak Entities)
       + (Number of M:N Relationships)
       + (Number of Multi-valued Attributes)
       + (Number of n-ary Relationships where n ≥ 3)
       - (Merges due to 1:1 with total participation)
```

**Detailed Rules:**

| Component | Contributes Tables |
|---|---|
| Each Strong Entity | 1 |
| Each Weak Entity | 1 |
| M:N Binary Relationship | 1 (separate table) |
| 1:N Binary Relationship | 0 (merge FK into N-side) |
| 1:1 (Both Total) | −1 (merge into one table) |
| 1:1 (One Total) | 0 (merge FK into total side) |
| 1:1 (Both Partial) | 0 (merge FK into either side, allow NULLs) or +1 (separate table) |
| Each Multi-valued Attribute | 1 |
| Each n-ary Relationship (n≥3) | 1 |

---

## GATE Specific Focus Points

### 1. Key of Relationship Table in N-ary Relationships

For an n-ary relationship among E₁, E₂, ..., Eₙ:
- The **default PK** of the relationship table = all participating entity PKs.
- **Exception:** If entity Eᵢ is on the **1-side** of the relationship, then its PK is **excluded** from the relationship table's PK (it becomes a regular FK/attribute, functionally determined by the others).

**Example:**
```
Employee(EmpID) —N— works_on —N— Project(ProjID)
Each (Employee, Project) pair has at most 1 location.
Location(LocID) is on the 1-side.

Relationship table: Works_On(EmpID, ProjID, LocID)
  PK = (EmpID, ProjID)  ← LocID is NOT in PK (1-side)
```

### 2. Self-Referencing (Recursive) Relationships

- The **same entity** appears twice with different **roles**.
- Add **two FK columns** referencing the **same PK** but with different attribute names (role names).

**Example:**
```
Employee(EmpID PK) — supervises(1:N) — Employee

Table Employee(EmpID PK, Name, SupervisorID FK → Employee)
  → SupervisorID references EmpID of the same table
```

### 3. Handling ISA (Generalization/Specialization)

**Method 1 — Separate Tables for Each (Most Common):**
- Superclass: `Person(PID PK, Name, ...)`
- Subclass: `Student(PID PK/FK, GPA, ...)`
- Subclass: `Employee(PID PK/FK, Salary, ...)`
- PK of subclass = PK of superclass (also FK referencing superclass)

**Method 2 — Single Table (if Total & Disjoint):**
- `Person(PID, Name, Type, GPA, Salary, ...)`
- Contains NULLs for inapplicable attributes.

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| Including derived attributes in table | **Never** include derived attributes — they are computed |
| Including composite attribute as-is | Include only the **leaf/simple sub-attributes** |
| Putting FK on wrong side of 1:N | FK goes on the **N-side** (many side) |
| Merging M:N into entity table | **Always** create a separate table for M:N |
| Forgetting multi-valued attribute table | Each multi-valued attribute → separate table |
| Wrong PK for weak entity table | PK = **Owner's PK + Discriminator** |
| Wrong PK for relationship table | For M:N: both FKs. For n-ary: exclude 1-side FKs |
| Counting tables wrong with 1:1 merges | 1:1 with both total participation → can merge into 1 table |

---

## 3 Worked Examples

### Example 1: Simple Mapping (Easy)

**Q:** Map the following to relational schema:
```
Student(Roll_No PK, Name, DOB)
Course(CID PK, Title, Credits)
Enrolls — M:N with attribute Grade
```

**Solution:**
```
Table Student(Roll_No PK, Name, DOB)
Table Course(CID PK, Title, Credits)
Table Enrolls(Roll_No FK, CID FK, Grade)
  PK = (Roll_No, CID)
```
**Tables needed: 3**

---

### Example 2: Complex ER Diagram (Medium)

**Q:** Consider:
- Entity `Department(DeptID PK, DeptName)`
- Entity `Employee(EmpID PK, Name, Phone_Numbers{MV})`
- Relationship `works_in` — 1:N (Dept:Emp), total participation on Employee
- Relationship `manages` — 1:1 (Emp:Dept), total participation on Department
- Weak Entity `Dependent(Dep_Name disc., DOB)` of Employee via `has_dependent`

How many minimum tables?

**Solution:**
1. `Department` → 1 table
2. `Employee` → 1 table (merge `works_in` FK here — N-side)
3. `works_in` → 0 (merged into Employee)
4. `manages` → 0 (merge `ManagerEmpID` FK into Department — total participation side)
5. `Dependent` → 1 table (weak entity)
6. `has_dependent` → 0 (merged into Dependent)
7. `Phone_Numbers` → 1 table (multi-valued attribute)

**Total = 4 tables**

```
Department(DeptID PK, DeptName, ManagerEmpID FK)
Employee(EmpID PK, Name, DeptID FK)
Dependent(EmpID FK, Dep_Name, DOB)  PK = (EmpID, Dep_Name)
Emp_Phone(EmpID FK, Phone_Number)   PK = (EmpID, Phone_Number)
```

---

### Example 3: Ternary Relationship Mapping (GATE Level)

**Q:** Consider a ternary relationship `Supply` among:
- `Supplier(SID PK)` — many side
- `Part(PID PK)` — many side
- `Project(ProjID PK)` — 1 side (each Supplier-Part pair supplies to at most 1 project)

With relationship attribute `Quantity`.

Map to relational schema and identify PK of Supply table.

**Solution:**
```
Table Supplier(SID PK, SName, ...)
Table Part(PID PK, PName, ...)
Table Project(ProjID PK, ProjName, ...)
Table Supply(SID FK, PID FK, ProjID FK, Quantity)
  PK = (SID, PID)
```

**Why PK = (SID, PID)?**
- Project is on the **1-side**: each (Supplier, Part) pair maps to at most **one** Project.
- So `ProjID` is **functionally determined** by `(SID, PID)`.
- Therefore `ProjID` is NOT in the PK.

**Total Tables = 4**

---

## Revision Table

| ER Component | Relational Mapping | PK Strategy |
|---|---|---|
| Strong Entity | Separate table | Entity's PK |
| Weak Entity | Separate table with owner's PK | Owner PK + Discriminator |
| 1:1 Relationship (Total) | Merge FK into total side | — |
| 1:1 (Both Total) | Can merge into 1 table | Combined |
| 1:N Relationship | FK on N-side | — |
| M:N Relationship | Separate table | Both PKs combined |
| Multi-valued Attr | Separate table | Entity PK + MV Attr |
| Composite Attr | Use leaf attributes only | — |
| Derived Attr | **Exclude** | — |
| n-ary Relationship | Separate table | All PKs minus 1-side |
| ISA / Generalization | Separate table per subclass | Superclass PK inherited |
| Recursive Relationship | Two FK columns with role names | — |

---

## Quick Mapping Decision Tree

```
Is it a Strong Entity?
  → YES → Create table, PK = entity PK

Is it a Weak Entity?
  → YES → Create table, PK = owner PK + discriminator

Is it a 1:1 Relationship?
  → Both Total → Merge all into 1 table
  → One Total → Add FK to total side
  → Both Partial → Add FK to either side (allow NULLs)

Is it a 1:N Relationship?
  → Add FK to N-side

Is it an M:N Relationship?
  → Create separate table, PK = both FKs

Is it a Multi-valued Attribute?
  → Create separate table, PK = entity PK + MV attr

Is it a Ternary+ Relationship?
  → Create separate table, PK = all FKs minus 1-side FKs
```

---

*← [02 — Relational Database Model](02_Relational_Database_Model.md) | [04 — Normalisation Deep Dive →](04_Normalisation_Deep_Dive.md)*
