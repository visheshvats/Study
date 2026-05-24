# 3. ER to Relational Model Mapping — Detailed GATE CSE Guide

> **GATE Weightage:** 1–2 marks. Questions focus on "How many minimum tables?" and "What is the primary key of the resulting table?"

---

## Why Do We Need Mapping?

You've designed a beautiful ER diagram — but databases don't understand ER diagrams. Databases understand **tables, columns, and keys**. So you need to **convert** (map) your ER diagram into a relational schema (set of tables).

This conversion has **well-defined rules** — it's not guesswork. There's a systematic 7-step algorithm that works for any ER diagram.

**The big question GATE asks:** "Given this ER diagram, what is the **minimum number of tables** needed?"

To answer this, you need to understand each mapping rule and when you can **merge** tables to reduce the count.

---

## Step-by-Step Mapping Rules

### Step 1: Map Strong (Regular) Entity Sets

**Rule:** Each strong entity set becomes a **separate table**.

**How to handle attributes:**

| Attribute Type | What to do |
|---|---|
| **Simple** | Include as a column |
| **Composite** | Include only the **leaf (simple)** sub-attributes, NOT the composite parent |
| **Derived** | **EXCLUDE** (never store derived attributes — they're computed) |
| **Multi-valued** | **EXCLUDE** for now (handled separately in Step 6) |
| **Key** | Becomes the **PRIMARY KEY** of the table |

**Detailed Example:**

ER Entity:
```
Employee
  - EmpID (key)
  - Name (composite: FName, LName)
  - DOB (simple)
  - Age (derived from DOB)
  - Phone_Numbers (multi-valued)
  - Address (composite: Street, City, State, Pincode)
```

Resulting Table:
```sql
CREATE TABLE Employee (
    EmpID        INT PRIMARY KEY,  -- Key attribute → PK
    FName        VARCHAR(50),      -- Leaf of composite "Name"
    LName        VARCHAR(50),      -- Leaf of composite "Name"
    DOB          DATE,             -- Simple attribute
    -- Age is EXCLUDED (derived)
    -- Phone_Numbers handled in Step 6 (multi-valued)
    Street       VARCHAR(100),     -- Leaf of composite "Address"
    City         VARCHAR(50),      -- Leaf of composite "Address"
    State        VARCHAR(50),      -- Leaf of composite "Address"
    Pincode      INT               -- Leaf of composite "Address"
);
```

Notice:
- `Name` column doesn't appear — its sub-parts `FName` and `LName` do
- `Age` is completely absent (it's derived from DOB)
- `Phone_Numbers` will be handled later (Step 6)
- `Address` column doesn't appear — its sub-parts do

---

### Step 2: Map Weak Entity Sets

**Rule:** Each weak entity becomes a **separate table**, with a special primary key.

**How:**
1. Include all simple attributes of the weak entity
2. Include the **primary key of the owner (strong) entity** as a **foreign key**
3. The **primary key** of the weak entity table = **Owner's PK + Discriminator (Partial Key)**

**Detailed Example:**

ER:
```
Strong Entity:  Employee (EmpID PK)
Weak Entity:    Dependent (Dep_Name discriminator, Relationship, DOB)
Identifying Relationship: "has_dependent" (1:N from Employee to Dependent)
```

Resulting Table:
```sql
CREATE TABLE Dependent (
    EmpID         INT,               -- Owner's PK (Foreign Key)
    Dep_Name      VARCHAR(50),       -- Discriminator (Partial Key)
    Relationship  VARCHAR(20),       -- Simple attribute
    DOB           DATE,              -- Simple attribute
    PRIMARY KEY (EmpID, Dep_Name),   -- Composite PK = Owner PK + Discriminator
    FOREIGN KEY (EmpID) REFERENCES Employee(EmpID)
        ON DELETE CASCADE            -- If employee is deleted, dependents go too
);
```

**Why CASCADE on delete?** Because a weak entity CANNOT exist without its owner. If the employee is gone, their dependents must be removed too.

**Why is PK composite?** Because `Dep_Name` alone isn't unique (multiple employees might have dependents named "Amit"). But `(EmpID, Dep_Name)` IS unique — Employee 101's "Amit" is different from Employee 205's "Amit."

---

### Step 3: Map Binary 1:1 Relationships

This is where it gets interesting — and where you can reduce the number of tables!

**The core idea:** In a 1:1 relationship, each entity on one side maps to at most one entity on the other side. So instead of creating a separate table, you can **add a foreign key** to one of the entity tables.

**But which side gets the FK?** It depends on the **participation constraints:**

---

#### Case A: Both Sides Have Total Participation

**Both** entities MUST participate.

**Example:** Every Person has exactly one Passport, and every Passport belongs to exactly one Person.

**Strategy:** Merge EVERYTHING into ONE table!

```sql
-- Instead of Person and Passport tables:
CREATE TABLE Person_Passport (
    PID         INT PRIMARY KEY,
    PersonName  VARCHAR(50),
    DOB         DATE,
    PassportNo  VARCHAR(20) UNIQUE,  -- From Passport entity
    IssueDate   DATE,                -- From Passport entity
    ExpiryDate  DATE                 -- From Passport entity
);
```

**Tables needed: 1** (merged)

**Why is this okay?** Since EVERY person has a passport and EVERY passport belongs to a person, there's a perfect 1:1 correspondence. No NULLs will ever appear. So merging wastes no space.

---

#### Case B: One Side Total, One Side Partial

**Example:** Every Department has exactly one Manager (total on Department), but not every Employee is a Manager (partial on Employee).

**Strategy:** Add the FK to the **total participation side** (the side that MUST participate).

```sql
-- Employee table (no change)
CREATE TABLE Employee (
    EmpID  INT PRIMARY KEY,
    Name   VARCHAR(50)
);

-- Department table (FK added here — total participation side)
CREATE TABLE Department (
    DeptID       INT PRIMARY KEY,
    DeptName     VARCHAR(50),
    ManagerEmpID INT UNIQUE,    -- FK to Employee + UNIQUE (1:1)
    FOREIGN KEY (ManagerEmpID) REFERENCES Employee(EmpID)
);
```

**Tables needed: 2**

**Why the total side?** If we put the FK on the partial side (Employee), most employees would have `ManagerOf = NULL` (since most aren't managers). That wastes space. But on the total side (Department), EVERY row has a valid FK value — no NULLs!

> **⚠️ GATE Point:** Notice the `UNIQUE` constraint on the FK. This is essential for 1:1 — without it, multiple departments could reference the same manager, violating the 1:1 constraint.

---

#### Case C: Both Sides Partial

**Strategy:** You can either:
1. Add FK to either side (with NULLs) → **2 tables**
2. Create a separate relationship table → **3 tables**

**For GATE: the minimum is 2.** (Merge FK into either side, accepting NULLs.)

---

### Step 4: Map Binary 1:N Relationships

**Rule:** Add the primary key of the **1-side** as a **foreign key** in the **N-side** table.

**Why the N-side?** Think about it:
- On the 1-side (e.g., Department), each department has many employees. You can't add a column `EmployeeID` to Department — which employee's ID would you put there?
- On the N-side (e.g., Employee), each employee belongs to ONE department. So you CAN add a column `DeptID` to Employee — and each row has exactly one value.

**Example:**
```
Department (1) ←—works_in—→ (N) Employee
```

```sql
CREATE TABLE Department (
    DeptID    INT PRIMARY KEY,
    DeptName  VARCHAR(50)
);

CREATE TABLE Employee (
    EmpID    INT PRIMARY KEY,
    Name     VARCHAR(50),
    DeptID   INT,                -- FK from 1-side's PK
    FOREIGN KEY (DeptID) REFERENCES Department(DeptID)
);
```

**Tables needed: 2** (no separate relationship table!)

> **⚠️ GATE Critical Rule:** In 1:N, the FK ALWAYS goes on the **N-side** (many side). If you put it on the 1-side, you'd need multiple values in one cell, violating the atomicity requirement.

**What about relationship attributes?** They also go into the N-side table.

**Example:** If `works_in` has an attribute `Start_Date`:
```sql
CREATE TABLE Employee (
    EmpID      INT PRIMARY KEY,
    Name       VARCHAR(50),
    DeptID     INT,
    Start_Date DATE,           -- Relationship attribute
    FOREIGN KEY (DeptID) REFERENCES Department(DeptID)
);
```

---

### Step 5: Map Binary M:N Relationships

**Rule:** Create a NEW, SEPARATE table for the relationship.

**Why can't we merge?** Because:
- A student takes MANY courses → Can't put just one CourseID in Student table
- A course has MANY students → Can't put just one StudentID in Course table
- You NEED a separate table to represent all the (Student, Course) pairs

**The relationship table contains:**
1. The PKs of both entities as **foreign keys**
2. The combination of both FKs as the **primary key**
3. Any **relationship attributes**

**Example:**
```
Student (M) ←—Enrolls(Grade)—→ (N) Course
```

```sql
CREATE TABLE Student (
    SID   INT PRIMARY KEY,
    Name  VARCHAR(50)
);

CREATE TABLE Course (
    CID    INT PRIMARY KEY,
    Title  VARCHAR(100)
);

CREATE TABLE Enrolls (
    SID    INT,
    CID    INT,
    Grade  CHAR(2),              -- Relationship attribute
    PRIMARY KEY (SID, CID),      -- Composite PK = both FKs
    FOREIGN KEY (SID) REFERENCES Student(SID),
    FOREIGN KEY (CID) REFERENCES Course(CID)
);
```

**Tables needed: 3** (ALWAYS for M:N)

> **⚠️ This is THE most important rule for GATE minimum table questions:** M:N = ALWAYS a separate table. No exceptions. No merging.

---

### Step 6: Map Multi-Valued Attributes

**Rule:** Each multi-valued attribute becomes a **separate table**.

**Why?** A multi-valued attribute means one entity can have MULTIPLE values. You can't put multiple values in one cell (violates 1NF's atomicity). So you create a separate table where each value gets its own row.

**The new table contains:**
1. The entity's **primary key** as a **foreign key**
2. The **multi-valued attribute** as a column
3. **Primary key** = FK + the multi-valued attribute

**Example:**
```
Employee(EmpID PK, Name, Phone_Numbers{multi-valued})
```

```sql
CREATE TABLE Employee (
    EmpID  INT PRIMARY KEY,
    Name   VARCHAR(50)
);

CREATE TABLE Emp_Phone (
    EmpID         INT,
    Phone_Number  VARCHAR(15),
    PRIMARY KEY (EmpID, Phone_Number),
    FOREIGN KEY (EmpID) REFERENCES Employee(EmpID)
);
```

**Data example:**
```
Employee:          Emp_Phone:
EmpID | Name       EmpID | Phone_Number
101   | Amit       101   | 9876543210
102   | Priya      101   | 8765432109
                   102   | 7654321098
                   102   | 6543210987
                   102   | 5432109876
```

Amit has 2 phones, Priya has 3 phones — each in a separate row.

---

### Step 7: Map N-ary Relationships (n > 2)

**Rule:** Create a separate table for the relationship. The PK depends on cardinality.

**For ternary (3-way) relationships:**

The relationship table contains:
1. **PKs of ALL participating entities** as foreign keys
2. Any relationship attributes
3. The **primary key** is determined by cardinality:
   - If ALL sides are **many**: PK = all FKs combined
   - If some side is **1**: that entity's FK is **NOT** part of the PK

**Why exclude the 1-side from PK?**

Suppose Supplier supplies Part to Project, and each (Supplier, Part) pair supplies to at most 1 Project (Project is 1-side):
- `(S1, P1)` → `Pr1` (fixed — this pair goes to one project)
- `(S1, P2)` → `Pr3`
- `(S2, P1)` → `Pr2`

The combination `(SupplierID, PartID)` already uniquely determines `ProjectID`. Adding ProjectID to the PK would be redundant.

```sql
CREATE TABLE Supplies (
    SID      INT,
    PID      INT,
    ProjID   INT,
    Quantity INT,
    PRIMARY KEY (SID, PID),        -- Project is 1-side → excluded from PK
    FOREIGN KEY (SID) REFERENCES Supplier(SID),
    FOREIGN KEY (PID) REFERENCES Part(PID),
    FOREIGN KEY (ProjID) REFERENCES Project(ProjID)
);
```

---

## The Master Formula: Minimum Number of Tables

Here's the complete formula for counting minimum tables:

```
Min Tables = Strong Entities
           + Weak Entities
           + M:N Relationships
           + Multi-valued Attributes
           + n-ary Relationships (n ≥ 3)
           - Merges from 1:1 (both total)
```

**What does NOT add tables:**
- 1:N relationships → merge FK into N-side → no new table
- 1:1 relationships → merge FK into appropriate side → no new table
- Simple/Composite attributes → become columns, not tables
- Derived attributes → excluded entirely

**What reduces tables:**
- 1:1 with both total participation → can merge two entities into one table → subtract 1

### Quick Decision Flowchart

```
For each component in the ER diagram, ask:

Is it a Strong Entity?
  └→ +1 table

Is it a Weak Entity?
  └→ +1 table (PK = owner PK + discriminator)

Is it a 1:1 Relationship?
  ├→ Both Total → Can merge into 1 table (net: −1 from the two entities)
  ├→ One Total → Add FK to total side (+0 tables)
  └→ Both Partial → Add FK to either side (+0 tables)

Is it a 1:N Relationship?
  └→ Add FK to N-side (+0 tables)

Is it an M:N Relationship?
  └→ +1 table (ALWAYS)

Is it a Multi-valued Attribute?
  └→ +1 table

Is it a Ternary+ Relationship?
  └→ +1 table

Is it a Derived Attribute?
  └→ +0 (excluded)
```

---

## Self-Referencing (Recursive) Relationships

When an entity set has a relationship with **itself**, you need special handling.

**Example:** Employee supervises Employee

```sql
CREATE TABLE Employee (
    EmpID          INT PRIMARY KEY,
    Name           VARCHAR(50),
    SupervisorID   INT,                  -- FK referencing same table
    FOREIGN KEY (SupervisorID) REFERENCES Employee(EmpID)
);
```

**Data example:**
```
EmpID | Name    | SupervisorID
101   | Amit    | 105           -- Amit is supervised by Priya
102   | Rahul   | 105           -- Rahul is supervised by Priya
105   | Priya   | NULL          -- Priya has no supervisor (top of hierarchy)
```

> **Key Point:** The two FK columns represent the two **roles** in the recursive relationship. Here, `EmpID` is the "subordinate" role and `SupervisorID` is the "supervisor" role.

---

## Mapping ISA (Generalization/Specialization) Hierarchies

There are multiple strategies:

### Method 1: Separate Tables (Most Common in GATE)

```sql
-- Superclass table
CREATE TABLE Person (
    PID   INT PRIMARY KEY,
    Name  VARCHAR(50),
    DOB   DATE
);

-- Subclass tables (PK is also FK to superclass)
CREATE TABLE Student (
    PID   INT PRIMARY KEY,              -- Same as Person's PK
    GPA   DECIMAL(3,2),
    Major VARCHAR(50),
    FOREIGN KEY (PID) REFERENCES Person(PID)
);

CREATE TABLE Employee (
    PID    INT PRIMARY KEY,
    Salary DECIMAL(10,2),
    Dept   VARCHAR(50),
    FOREIGN KEY (PID) REFERENCES Person(PID)
);
```

**Tables: 3 (1 superclass + 2 subclasses)**

### Method 2: Merge Into Subclasses (Only for Total + Disjoint)

```sql
-- NO Person table!
CREATE TABLE Student (
    PID   INT PRIMARY KEY,
    Name  VARCHAR(50),      -- Inherited from Person
    DOB   DATE,             -- Inherited from Person
    GPA   DECIMAL(3,2),
    Major VARCHAR(50)
);

CREATE TABLE Employee (
    PID    INT PRIMARY KEY,
    Name   VARCHAR(50),     -- Inherited from Person
    DOB    DATE,            -- Inherited from Person
    Salary DECIMAL(10,2),
    Dept   VARCHAR(50)
);
```

**Tables: 2 (subclasses only)**

This works ONLY when:
- **Total:** Every person IS a student or employee (no "just persons")
- **Disjoint:** No person is BOTH a student and employee

If it were overlapping (a person can be both), you'd duplicate their Name and DOB in both tables — which is redundant and error-prone. That's why overlapping requires the superclass table.

---

## Common Pitfalls

### Pitfall 1: Including Derived Attributes

**Wrong:** Adding an `Age` column when `DOB` exists and `Age` is derived.
**Correct:** Exclude `Age` entirely. It's computed from DOB.

### Pitfall 2: Including Composite Attribute as a Column

**Wrong:** `CREATE TABLE Employee (..., Name VARCHAR(100), ...)`
**Correct:** `CREATE TABLE Employee (..., FName VARCHAR(50), LName VARCHAR(50), ...)`
Include only the leaf sub-attributes.

### Pitfall 3: FK on Wrong Side of 1:N

**Wrong:** Adding `EmployeeID` column to Department table in a 1:N (Dept→Emp) relationship.
**Correct:** Adding `DeptID` column to Employee table. The FK goes on the **N-side**.

### Pitfall 4: Merging M:N Relationships

**Wrong:** Trying to add `CourseIDs` column to Student table.
**Correct:** Creating a separate Enrollment table. M:N ALWAYS needs a separate table.

### Pitfall 5: Wrong PK for Weak Entity

**Wrong:** PK = Dep_Name (discriminator only)
**Correct:** PK = (EmpID, Dep_Name) = Owner PK + Discriminator

### Pitfall 6: Wrong PK for N-ary Relationship

**Wrong:** Always making PK = all FKs
**Correct:** Exclude FKs of 1-side entities from the PK

---

## 3 Worked Examples (Step by Step)

### Example 1: Simple Mapping (Easy)

**ER Diagram:**
- Student(Roll_No PK, Name, DOB)
- Course(CID PK, Title, Credits)
- Enrolls: M:N with attribute Grade

**Solution:**
1. Student → Table: `Student(Roll_No PK, Name, DOB)` ← 1 table
2. Course → Table: `Course(CID PK, Title, Credits)` ← 1 table
3. Enrolls (M:N) → Table: `Enrolls(Roll_No FK, CID FK, Grade)`, PK = (Roll_No, CID) ← 1 table

**Total: 3 tables** ✅

---

### Example 2: Complex ER with Multiple Features (Medium)

**ER Diagram:**
- Entity: `Department(DeptID PK, DeptName)`
- Entity: `Employee(EmpID PK, Name, Phone{MV})`
- `works_in`: 1:N (Dept:Emp), Total on Employee
- `manages`: 1:1 (Emp:Dept), Total on Department
- Weak Entity: `Dependent(Dep_Name disc., DOB)` of Employee

**Step-by-step counting:**
1. `Department` → 1 table
2. `Employee` → 1 table
3. `works_in` (1:N) → Merge FK(DeptID) into Employee (N-side) → +0
4. `manages` (1:1, total on Dept) → Merge FK(ManagerEmpID) into Department → +0
5. `Dependent` (weak) → 1 table, PK = (EmpID, Dep_Name)
6. `Phone` (multi-valued) → 1 table, PK = (EmpID, Phone)

**Total: 4 tables**

```sql
Department(DeptID PK, DeptName, ManagerEmpID FK UNIQUE)
Employee(EmpID PK, Name, DeptID FK)
Dependent(EmpID FK, Dep_Name, DOB)  -- PK: (EmpID, Dep_Name)
Emp_Phone(EmpID FK, Phone)          -- PK: (EmpID, Phone)
```

---

### Example 3: Ternary Relationship with 1-Side (GATE Level)

**ER Diagram:**
- Supplier(SID PK) — M side
- Part(PID PK) — M side
- Project(ProjID PK) — 1 side (each Supplier-Part pair → at most 1 Project)
- Ternary relationship: `Supply(Quantity)`

**Solution:**
1. Supplier → 1 table
2. Part → 1 table
3. Project → 1 table
4. Supply (ternary) → 1 table
   - PK = (SID, PID) — EXCLUDE ProjID from PK because Project is 1-side
   - ProjID is a regular FK/attribute (not in PK)

```sql
Supplier(SID PK, SName)
Part(PID PK, PName)
Project(ProjID PK, ProjName)
Supply(SID FK, PID FK, ProjID FK, Quantity)  -- PK: (SID, PID)
```

**Total: 4 tables**

---

## Revision Table

| ER Component | Mapping | PK Strategy | Extra Tables |
|---|---|---|---|
| Strong Entity | Separate table | Entity's key | +1 |
| Weak Entity | Separate table | Owner PK + Discriminator | +1 |
| 1:1 (Both Total) | Merge into 1 table | Combined | −1 (net) |
| 1:1 (One Total) | FK on total side | — | +0 |
| 1:N | FK on N-side | — | +0 |
| M:N | **ALWAYS** separate table | Both PKs combined | +1 |
| Multi-valued Attr | Separate table | Entity PK + MV attr | +1 |
| Derived Attr | EXCLUDE | — | +0 |
| Composite Attr | Use leaf sub-attrs only | — | +0 |
| N-ary (n≥3) | Separate table | All PKs minus 1-side | +1 |
| Recursive Rel | Two FK columns with role names | — | +0 (for 1:N) |
| ISA (Total+Disjoint) | Subclass tables only | Superclass PK | = subclasses |
| ISA (other) | Superclass + subclass tables | Superclass PK | = 1 + subclasses |

---

*← [02 — Relational Database Model](02_Relational_Database_Model.md) | [04 — Normalisation Deep Dive →](04_Normalisation_Deep_Dive.md)*
