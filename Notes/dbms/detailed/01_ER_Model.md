# 1. Entity-Relationship (ER) Model — Detailed GATE CSE Guide

> **GATE Weightage:** 2–4 marks almost every year. This is your foundation — every other DBMS topic builds on your understanding of ER diagrams.

---

## What is the ER Model?

Imagine you're building a database for a university. Before you jump into creating tables in SQL, you need to first **plan** what data you'll store and how different pieces of data relate to each other. That's exactly what the ER Model helps you do.

The **Entity-Relationship (ER) Model** was introduced by **Peter Chen in 1976**. Think of it as a **blueprint** for your database — just like an architect draws a blueprint before constructing a building. The ER model gives you a visual, graphical way to design the structure of your database.

**Key idea:** The ER model works at the **conceptual level** — it doesn't care about which database software you'll use (MySQL, PostgreSQL, Oracle, etc.). It only cares about **what** data exists and **how** it's connected.

**Why should you care for GATE?**
- You'll get questions asking you to count the **minimum number of tables** from an ER diagram
- You'll need to identify **keys** after conversion
- You'll need to understand **participation constraints** and **cardinality**
- Questions on **weak entities** appear regularly

---

## Entities — The "Things" in Your Database

### What is an Entity?

An **entity** is simply a "thing" or "object" in the real world that you want to store information about. It must be **distinguishable** from other things — meaning you can tell one apart from another.

**Examples of entities:**
- A **student** named Amit with Roll No 101
- A **book** titled "Database Systems" with ISBN 978-0-13-187325-4
- An **employee** named Priya with Employee ID E001

### What is an Entity Set?

An **entity set** is a collection of all entities of the same type. Think of it like a **category** or **class**.

- The entity set `Student` contains ALL students: Amit, Priya, Rahul, etc.
- The entity set `Book` contains ALL books in the library
- The entity set `Employee` contains ALL employees in the company

**In an ER diagram:** Entity sets are drawn as **rectangles**.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Student    │     │    Course    │     │  Department  │
└──────────────┘     └──────────────┘     └──────────────┘
```

> **Think of it this way:** An entity is like a specific row in a future table. An entity set is like the entire table.

---

## Attributes — Describing Your Entities

### What is an Attribute?

An **attribute** is a property or characteristic that describes an entity. Every entity in an entity set has the same set of attributes (but different values).

**Example:** The entity set `Student` might have these attributes:
- `Roll_No` — 101, 102, 103, ...
- `Name` — "Amit", "Priya", "Rahul", ...
- `DOB` — "2000-01-15", "1999-03-22", ...
- `Age` — 24, 25, ...
- `Phone_Numbers` — {9876543210, 8765432109}, ...

**In an ER diagram:** Attributes are drawn as **ovals** connected to their entity rectangle by a line.

```
        (Roll_No)    (Name)    (DOB)
            │          │        │
            └──────┬───┘────────┘
                   │
            ┌──────┴───────┐
            │   Student    │
            └──────────────┘
```

### Types of Attributes — This is Important for GATE!

Not all attributes are the same. There are **5 types** you need to know:

---

#### 1. Simple (Atomic) Attribute

An attribute that **cannot be divided** further. It holds a single, indivisible value.

**Examples:**
- `Roll_No` = 101 (just a number, can't be split)
- `Gender` = "Male" (single value)
- `Pincode` = 560001

**ER Symbol:** A plain oval → `(Roll_No)`

---

#### 2. Composite Attribute

An attribute that **can be divided** into smaller sub-attributes, each with its own meaning.

**Example:** `Name` can be split into:
- `First_Name` = "Amit"
- `Middle_Name` = "Kumar"
- `Last_Name` = "Sharma"

Similarly, `Address` can be split into:
- `Street` = "MG Road"
- `City` = "Bangalore"
- `State` = "Karnataka"
- `Pincode` = 560001

**ER Symbol:** An oval with sub-ovals branching from it:
```
            (Name)
           /  |  \
    (First) (Mid) (Last)
```

> **For GATE:** When converting to a relational table, you include the **leaf-level (simple) sub-attributes**, NOT the composite attribute itself. So the table would have columns `First_Name`, `Middle_Name`, `Last_Name` — NOT a column called `Name`.

---

#### 3. Derived Attribute

An attribute whose value can be **calculated (derived) from other attributes**. It is NOT stored in the database — it's computed whenever needed.

**Examples:**
- `Age` can be calculated from `DOB` and today's date → `Age = Current_Year - Birth_Year`
- `Total_Marks` can be calculated from individual subject marks
- `Experience` can be calculated from `Date_of_Joining`

**ER Symbol:** A dashed oval → `- - (Age) - -`

```
  ╌╌╌╌╌╌╌╌╌
  ╎  Age   ╎
  ╌╌╌╌╌╌╌╌╌
```

> **For GATE:** Derived attributes are **NEVER included** in the relational table. If a question asks you to map an ER diagram to tables and you include a derived attribute, that's **wrong**.

---

#### 4. Multi-Valued Attribute

An attribute that can hold **multiple values** for a single entity.

**Examples:**
- A student can have **multiple phone numbers**: {9876543210, 8765432109}
- A person can have **multiple degrees**: {B.Tech, M.Tech, PhD}
- An employee can have **multiple skills**: {Java, Python, SQL}

**ER Symbol:** A double oval → `((Phone_Numbers))`

```
  ╔══════════════════╗
  ║  Phone_Numbers   ║
  ╚══════════════════╝
```

> **For GATE:** Multi-valued attributes are converted into a **separate table** during ER-to-relational mapping. This is a common source of "how many tables" questions.

---

#### 5. Key Attribute

An attribute (or set of attributes) that **uniquely identifies** each entity in the entity set. No two entities can have the same value for a key attribute.

**Examples:**
- `Roll_No` uniquely identifies each student
- `Aadhaar_Number` uniquely identifies each person
- `ISBN` uniquely identifies each book

**ER Symbol:** An oval with the attribute name **underlined** → `(R̲o̲l̲l̲_̲N̲o̲)`

> **Important:** An entity set can have **multiple key attributes** (i.e., multiple candidate keys). For example, a `Student` might be uniquely identified by either `Roll_No` OR `Aadhaar_Number`.

---

### Summary Table of Attribute Types

| Type | Can be split? | Multiple values? | Stored? | ER Symbol |
|---|---|---|---|---|
| **Simple** | No | No | Yes | Plain oval |
| **Composite** | Yes (into sub-parts) | No | Sub-parts stored | Oval with branches |
| **Derived** | — | No | **No** (computed) | Dashed oval |
| **Multi-valued** | — | **Yes** | Separate table | Double oval |
| **Key** | — | No | Yes | Underlined oval |

> **Note:** An attribute can be a combination: e.g., a **composite multi-valued** attribute (like `Address` that is multi-valued where each address has sub-parts like Street, City, etc.)

---

## Relationships — How Entities Connect

### What is a Relationship?

A **relationship** is an association or connection between two or more entities. It describes how entities interact with each other.

**Examples:**
- Student **enrolls in** Course
- Employee **works for** Department  
- Author **writes** Book
- Patient **visits** Doctor

### What is a Relationship Set?

Just like an entity set is a collection of similar entities, a **relationship set** is a collection of similar relationships.

The relationship set `Enrolls` contains all individual enrollment relationships:
- (Amit, DBMS) — Amit enrolls in DBMS
- (Amit, OS) — Amit enrolls in OS
- (Priya, DBMS) — Priya enrolls in DBMS

**In an ER diagram:** Relationships are drawn as **diamonds** connected to the participating entity rectangles.

```
┌──────────┐         ◇──────────◇         ┌──────────┐
│ Student  │─────────│ Enrolls  │─────────│  Course  │
└──────────┘         ◇──────────◇         └──────────┘
```

### Relationship Attributes (Descriptive Attributes)

Relationships can also have their own attributes! These are properties that belong to the **relationship itself**, not to either entity.

**Example:** The `Enrolls` relationship between Student and Course might have:
- `Grade` — The grade a student received in a course (e.g., "A", "B+")
- `Enrollment_Date` — When the student enrolled

Why is `Grade` a relationship attribute and not a Student or Course attribute?
- It doesn't belong to just the student (a student has different grades in different courses)
- It doesn't belong to just the course (different students get different grades)
- It belongs to the **combination** of (Student, Course) — the enrollment relationship

---

### Degree of a Relationship

The **degree** tells you how many entity sets participate in a relationship.

#### Unary (Degree 1) — Recursive Relationship

An entity set is related to **itself**. The entity participates in the relationship in **different roles**.

**Example:** `Employee` manages `Employee`
- Every manager is an employee
- Every subordinate is an employee
- But they play **different roles**: "supervisor" and "subordinate"

```
          ┌─────────────┐
          │  Employee   │
          └──┬──────┬───┘
    (super-  │      │  (sub-
     visor)  │      │  ordinate)
          ◇──┘──────┘──◇
          │  Manages   │
          ◇────────────◇
```

> **GATE Point:** In recursive relationships, you MUST specify the **role** of each participation, otherwise the diagram is ambiguous.

#### Binary (Degree 2)

The most common type — two entity sets participate.

**Example:** Student **enrolls in** Course, Employee **works in** Department

#### Ternary (Degree 3)

Three entity sets participate in a single relationship.

**Example:** A `Supplier` supplies a `Part` to a `Project`

This is different from three separate binary relationships! A ternary relationship captures the **combination of all three** — which supplier provides which part to which project.

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Supplier │     │   Part   │     │ Project  │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     └────────────┬───┘────────────────┘
                  │
           ◇─────┴─────◇
           │  Supplies  │
           ◇────────────◇
```

> **⚠️ GATE Trap:** A ternary relationship is NOT the same as three binary relationships. A ternary relationship can express constraints that three binaries cannot. For example: "Supplier S1 supplies Part P1 to Project Pr1" — this three-way association is lost if you break it into binary pairs.

#### N-ary (Degree n)

A relationship involving `n` entity sets. Ternary is a special case where n=3.

---

## Cardinality Constraints (Mapping Cardinality)

### What is Cardinality?

**Cardinality** defines the **maximum number** of relationship instances that an entity can participate in. It answers the question: "How many entities on one side can be associated with how many on the other side?"

There are four types for binary relationships:

---

### One-to-One (1:1)

**Each entity** in A is associated with **at most one** entity in B, and **each entity** in B is associated with **at most one** entity in A.

**Real-world examples:**
- Person ↔ Passport (each person has at most one passport, each passport belongs to one person)
- Country ↔ Capital (each country has one capital, each capital belongs to one country)
- CEO ↔ Company (at a given time, each company has one CEO)

**Visual:**
```
A side                          B side
┌─────┐                       ┌─────┐
│ a1  │───────────────────────│ b1  │
│ a2  │───────────────────────│ b2  │
│ a3  │                       │ b3  │  (a3 may not participate)
└─────┘                       └─────┘
    Each A maps to at most 1 B
    Each B maps to at most 1 A
```

---

### One-to-Many (1:N)

**Each entity** in A can be associated with **many** entities in B, but **each entity** in B is associated with **at most one** entity in A.

**Real-world examples:**
- Department → Employees (one department has many employees, each employee belongs to one department)
- Mother → Children (one mother has many children, each child has one mother)
- Course → Students enrolled (assuming no concurrent sections)

**Visual:**
```
A side (1)                     B side (N)
┌─────┐                       ┌─────┐
│ a1  │───────────────────┬───│ b1  │
│     │───────────────┬───│───│ b2  │
│     │───────────┬───│───│───│ b3  │
│ a2  │───────┬───│───│───│   │ b4  │
│     │───┬───│───│───│───│   │ b5  │
└─────┘   │   │   │   │   │  └─────┘
          └───┘───┘   └───┘
    Each A maps to many Bs
    Each B maps to at most 1 A
```

---

### Many-to-One (N:1)

The reverse of 1:N — **each entity** in A is associated with **at most one** entity in B, but **each entity** in B can be associated with **many** entities in A.

**Example:** Employees → Department (many employees belong to one department)

This is the same as 1:N but viewed from the other direction.

---

### Many-to-Many (M:N)

**Each entity** in A can be associated with **many** entities in B, AND **each entity** in B can be associated with **many** entities in A.

**Real-world examples:**
- Students ↔ Courses (a student takes many courses, a course has many students)
- Authors ↔ Books (an author writes many books, a book can have many authors)
- Actors ↔ Movies (an actor acts in many movies, a movie has many actors)

**Visual:**
```
A side (M)                     B side (N)
┌─────┐                       ┌─────┐
│ a1  │───────────────────┬───│ b1  │
│     │───────────────┬───│───│ b2  │
│ a2  │───────────┬───│───│   │     │
│     │───────┬───│───│───│───│ b3  │
│ a3  │───┬───│───│───│   │   │     │
│     │───│───│───│───│───│───│ b4  │
└─────┘   │   │   │   │   │  └─────┘
          └───┘───┘───┘───┘
    Each A maps to many Bs
    Each B maps to many As
```

---

### GATE Formula: Minimum Number of Tables from Cardinality

This is one of the **most frequently asked** GATE question types. Learn this table by heart:

| Relationship Type | Participation Constraint | Minimum Tables | How? |
|---|---|---|---|
| **1:1** | Both sides **Total** | **1** | Merge everything into one table |
| **1:1** | One side Total, other Partial | **2** | Merge FK into the total participation side |
| **1:1** | Both sides **Partial** | **2** | Merge FK into either side (NULLs possible) |
| **1:N** | N-side is Total | **2** | Merge FK into N-side |
| **1:N** | N-side is Partial | **2** or **3** | 2 if you allow NULLs on N-side, 3 if you keep a separate table |
| **M:N** | Any participation | **3** | **ALWAYS** need a separate relationship table |

> **⚠️ The Golden Rule:** M:N relationships **ALWAYS** require a separate table. You can NEVER merge an M:N relationship into either entity table. This is because one row in entity A maps to multiple rows in entity B and vice versa — you can't represent that with a single FK column.

**Why can you merge 1:1 but not M:N?**

Think about it with an example:
- **1:1 (Person ↔ Passport):** Each person has exactly one passport. So you can add a `PassportNo` column to the Person table. Done! One FK column is enough.
- **M:N (Student ↔ Course):** A student takes MANY courses. You can't add just one `CourseID` column to Student — you'd need multiple! And a Course has many students, so you can't add just one `StudentID` to Course either. You NEED a separate table `Enrollment(StudentID, CourseID)` to handle the many-to-many mapping.

---

## Participation Constraints — Must or May?

While cardinality says "how many," participation says "must or may."

### Total Participation (Existence Dependency)

**Every** entity in the entity set **must** participate in at least one relationship instance. No entity is allowed to exist without being in the relationship.

**Example:** "Every employee MUST work in a department."
- There cannot be an employee who doesn't belong to any department.

**ER Symbol:** A **double line** connecting the entity to the relationship diamond.

```
┌──────────┐         ◇──────────◇         ┌──────────┐
│ Employee │═════════│ works_in │─────────│   Dept   │
└──────────┘         ◇──────────◇         └──────────┘
     Total participation                 Partial participation
     (every employee MUST                (some depts MAY
      work in a dept)                     have no employees)
```

### Partial Participation

**Some** entities **may** or **may not** participate in the relationship. It's optional.

**Example:** "Not every employee manages a department." (Only some employees are managers.)

**ER Symbol:** A **single line** connecting the entity to the relationship.

---

### (min, max) Notation — A More Precise Way

Instead of just saying "total" or "partial," we can be more specific using **(min, max)** notation on each entity's participation edge.

- `min` = minimum number of relationship instances an entity MUST participate in
- `max` = maximum number of relationship instances an entity CAN participate in

**Rules:**
- `min = 0` → **Partial** participation (entity may not participate)
- `min ≥ 1` → **Total** participation (entity must participate)
- `max = 1` → Entity participates in at most one relationship
- `max = N` → Entity can participate in many relationships (unbounded)

**Example with (min, max):**
```
Employee (1, 1) ───< works_in >─── (5, N) Department
```
This means:
- Each Employee works in exactly **1** department (min=1, max=1) → Total participation, 1:1 from employee side
- Each Department has **at least 5** and potentially unlimited employees (min=5, max=N) → Total participation, many from dept side

Let's look at another example:
```
Employee (0, 1) ───< manages >─── (1, 1) Department
```
This means:
- Each Employee manages **at most 1** department, and may manage **none** (min=0, max=1) → Partial participation
- Each Department has **exactly 1** manager (min=1, max=1) → Total participation

> **GATE Tip:** When you see (min, max) notation, quickly translate:
> - min=0 → partial, min≥1 → total
> - max=1 → single valued, max=N → multivalued

---

## Weak Entity Sets — Entities That Can't Stand Alone

### The Problem

Sometimes, an entity doesn't have enough attributes to uniquely identify itself. It depends on another entity for its identity.

### What is a Weak Entity?

A **weak entity** is an entity that:
1. **Cannot be uniquely identified** by its own attributes alone
2. **Depends on another entity** (called the **owner** or **identifying entity**) for its existence
3. Is connected to its owner through an **identifying relationship**

### Example — Understanding Weak Entities

Consider an employee and their dependents (family members covered by insurance):

- **Employee** has `EmpID` (unique — no two employees have the same ID)
- **Dependent** has `Name` (but "Amit" could be a dependent of many employees)
  - Dependent "Amit" of Employee 101 is DIFFERENT from Dependent "Amit" of Employee 205
  - So `Name` alone doesn't uniquely identify a dependent
  - We need the **combination** of the Employee's ID and the Dependent's name

### Key Terminology

| Term | Definition | ER Symbol |
|---|---|---|
| **Weak Entity** | Entity that can't identify itself | **Double rectangle** ║ ║ |
| **Strong (Owner) Entity** | Entity that provides identification | Regular rectangle │ │ |
| **Identifying Relationship** | Connects weak entity to its owner | **Double diamond** ◆◆ |
| **Discriminator (Partial Key)** | Attribute(s) of weak entity that distinguish it among dependents of the SAME owner | **Dashed underline** |
| **Primary Key of Weak Entity** | = Owner's PK + Discriminator | Composite key |

### ER Diagram for Weak Entity

```
                                          ╔══════════════╗
┌──────────────┐     ◆════════════◆       ║  Dependent   ║
│   Employee   │═════║    has     ║═══════║              ║
│   (EmpID)    │     ◆════════════◆       ║  (D̲e̲p̲_̲N̲a̲m̲e̲)  ║
└──────────────┘                          ║  (DOB)       ║
                                          ╚══════════════╝
```

**Primary Key of Dependent** = (EmpID, Dep_Name)
- `EmpID` comes from the owner (Employee)
- `Dep_Name` is the discriminator (distinguishes dependents of the SAME employee)

### Important Rules for Weak Entities

1. **A weak entity ALWAYS has total participation** in its identifying relationship.
   - Why? Because a weak entity CANNOT exist without its owner. If the owner is deleted, the weak dependent must also be deleted.
   - If you see a weak entity with partial participation in its identifying relationship, **the diagram is wrong**.

2. **The identifying relationship is always 1:N** (from owner's perspective).
   - Owner is on the 1-side (one employee can have many dependents)
   - Weak entity is on the N-side (each dependent belongs to one employee)

3. **Weak entities can be chained.**
   - A weak entity can be the owner of another weak entity.
   - Example: `Building` (strong) → `Floor` (weak, disc: FloorNo) → `Room` (weak, disc: RoomNo)
   - PK of Room = (BuildingID, FloorNo, RoomNo)

> **⚠️ GATE Pitfall:** Don't confuse a weak entity with an entity that has a foreign key. A weak entity lacks its OWN unique identifier. An entity with a foreign key HAS its own primary key — the FK is just for referencing another table.

---

## Specialization & Generalization (Extended ER / EER)

### The Idea

Sometimes entities have subtypes. For example, in a university:
- Some `Persons` are `Students`, some are `Faculty`, some are `Staff`
- A `Vehicle` can be a `Car`, `Truck`, or `Motorcycle`

We need a way to represent this "IS-A" hierarchy.

### Specialization (Top-Down Approach)

**Specialization** means starting with a general entity set and defining **subgroups** based on distinguishing characteristics.

**Example:**
```
                ┌──────────┐
                │  Person  │
                │ (PID,    │
                │  Name,   │
                │  DOB)    │
                └────┬─────┘
                     │
                   ╱ ISA ╲
                  ╱       ╲
           ┌─────┴──┐  ┌──┴───────┐
           │Student  │  │ Employee │
           │(GPA,    │  │(Salary,  │
           │ Major)  │  │ Dept)    │
           └─────────┘  └──────────┘
```

- `Student` **IS-A** `Person` — it inherits all attributes of Person (PID, Name, DOB) plus has its own attributes (GPA, Major)
- `Employee` **IS-A** `Person` — inherits PID, Name, DOB, plus has Salary, Dept

### Generalization (Bottom-Up Approach)

The opposite of specialization. You start with multiple entity sets and **combine** them into a higher-level entity set by identifying common attributes.

**Example:** You notice `Car` and `Truck` both have `VehicleID`, `Make`, `Model`, `Year`. So you generalize them into `Vehicle`.

> **Important:** Specialization and Generalization are **inverse processes**. The resulting ER diagram looks identical — the difference is only in the design direction (top-down vs. bottom-up).

### Constraints on Specialization/Generalization

#### Completeness Constraint: Total vs. Partial

| Constraint | Meaning | Example |
|---|---|---|
| **Total** | Every superclass entity MUST belong to at least one subclass | Every Person MUST be either a Student or Employee (nobody is "just a Person") |
| **Partial** | A superclass entity MAY not belong to any subclass | Some Persons might be neither Student nor Employee (e.g., a Visitor) |

**ER Symbol:**
- Total → **double line** from superclass to ISA triangle
- Partial → **single line**

#### Disjointness Constraint: Disjoint vs. Overlapping

| Constraint | Meaning | Example |
|---|---|---|
| **Disjoint (d)** | An entity can belong to **at most one** subclass | A vehicle is either a Car OR a Truck, not both |
| **Overlapping (o)** | An entity can belong to **multiple** subclasses simultaneously | A person can be both a Student AND an Employee (e.g., a Teaching Assistant) |

### GATE Formula: Number of Tables for ISA Hierarchy

This is frequently asked:

| Completeness | Disjointness | Min Tables | Explanation |
|---|---|---|---|
| **Total** | **Disjoint** | **Number of subclasses** | No need for superclass table — every entity is in some subclass, and no entity is in multiple. Superclass attributes pushed into subclass tables. |
| **Total** | **Overlapping** | **1 + Number of subclasses** | Need superclass table to avoid duplicating shared attributes for entities in multiple subclasses |
| **Partial** | **Disjoint** | **1 + Number of subclasses** | Need superclass table for entities not in any subclass |
| **Partial** | **Overlapping** | **1 + Number of subclasses** | Need superclass table for both reasons |

**Example:**
- Person (PID, Name) with Student (GPA) and Employee (Salary)
- Total + Disjoint: Only 2 tables: Student(PID, Name, GPA), Employee(PID, Name, Salary)
- Partial + Overlapping: 3 tables: Person(PID, Name), Student(PID, GPA), Employee(PID, Salary)

---

## Aggregation — When Relationships Need Relationships

### The Problem

Sometimes you need to create a relationship between an entity and **another relationship**. But in standard ER, relationships can only connect entities, not other relationships.

### The Solution: Aggregation

**Aggregation** treats a relationship (along with its participating entities) as a **higher-level entity**, which can then participate in other relationships.

### Example

Scenario:
- An `Employee` works on a `Project` → relationship `works_on`
- A `Manager` monitors which employees work on which projects → the `Manager` monitors the `works_on` relationship

Without aggregation, you can't directly show that a Manager monitors the Employee-Project combination. With aggregation:

```
  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
  │                                           │
  │ ┌──────────┐   ◇──────────◇   ┌────────┐ │
  │ │ Employee │───│ works_on │───│Project │ │
  │ └──────────┘   ◇──────────◇   └────────┘ │
  │                                           │
  └ ─ ─ ─ ─ ─ ─ ─ ─ ─┬─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘
             (treated as one entity)
                       │
                 ◇─────┴─────◇
                 │  monitors │
                 ◇───────────◇
                       │
               ┌───────┴────────┐
               │    Manager     │
               └────────────────┘
```

The dashed rectangle groups the `Employee-works_on-Project` relationship into a single **aggregated entity** that can participate in the `monitors` relationship with `Manager`.

---

## Mathematical Foundations for GATE

### Maximum Number of Relationships

In a binary relationship between entity sets A and B:

| Cardinality | Max Relationship Instances |
|---|---|
| **1:1** | min(|A|, |B|) |
| **1:N** (1 on A side) | |B| |
| **M:N** | |A| × |B| |

**Example:** If |Student| = 100 and |Course| = 20:
- M:N enrollment → max 100 × 20 = 2,000 enrollments possible
- 1:N (each student takes one course) → max 100 enrollments

### For n-ary relationships

Among entity sets E₁, E₂, ..., Eₙ with sizes n₁, n₂, ..., nₙ:
- Maximum relationship instances = n₁ × n₂ × ... × nₙ

---

## Common Pitfalls — Avoid These Mistakes

### Pitfall 1: Confusing Cardinality with Participation

Many students mix these up. They are **different concepts**:

| | Cardinality | Participation |
|---|---|---|
| **What it answers** | "How many can be connected?" | "Must it be connected?" |
| **Values** | 1:1, 1:N, M:N | Total or Partial |
| **Analogy** | "How many friends can you have?" | "Must you have at least one friend?" |

### Pitfall 2: Weak Entity Without Total Participation

**Wrong:** Drawing a weak entity with a single line (partial participation) to its identifying relationship.
**Correct:** Weak entity ALWAYS has **total participation** (double line) in its identifying relationship.

### Pitfall 3: Forgetting the Discriminator in Weak Entity PK

**Wrong:** PK of Dependent = Dep_Name
**Correct:** PK of Dependent = (EmpID, Dep_Name) — must include the owner's PK!

### Pitfall 4: Treating Composite as Multi-valued

These are completely different:
- **Composite:** One value that has internal structure → `Name` = "Amit Kumar Sharma" → parts: First, Middle, Last
- **Multi-valued:** Multiple independent values → `Phone` = {9876, 8765, 7654}

### Pitfall 5: Merging M:N Relationships

**Never** try to merge an M:N relationship into either entity table. It ALWAYS requires a separate table.

### Pitfall 6: Ignoring Roles in Recursive Relationships

In `Employee manages Employee`, you MUST specify roles (supervisor, subordinate). Otherwise, you can't distinguish the two participations.

---

## Revision Table — Quick Reference

| Concept | Key Point | ER Symbol |
|---|---|---|
| Entity | Object in real world | Rectangle |
| Weak Entity | Can't identify itself, depends on owner | **Double** Rectangle |
| Attribute | Property of entity | Oval |
| Key Attribute | Uniquely identifies entity | **Underlined** Oval |
| Multi-valued | Multiple values possible | **Double** Oval |
| Derived | Computed, NOT stored | **Dashed** Oval |
| Composite | Divisible into sub-parts | Oval with sub-ovals |
| Relationship | Association between entities | Diamond |
| Identifying Relationship | Links weak entity to owner | **Double** Diamond |
| Total Participation | Entity MUST participate | **Double** Line |
| Partial Participation | Entity MAY participate | Single Line |
| Specialization/Generalization | ISA hierarchy | Triangle with "ISA" |
| Aggregation | Treating a relationship as an entity | Dashed rectangle around relationship |

---

## Quick-Fire GATE Formulas

```
Min tables for 1:1 (Both Total)     = 1
Min tables for 1:1 (One Total)      = 2
Min tables for 1:1 (Both Partial)   = 2
Min tables for 1:N                  = 2 (merge FK into N-side)
Min tables for M:N                  = 3 (ALWAYS separate table)
Weak entity PK                     = Owner PK + Discriminator
Max relationships in M:N           = |A| × |B|
Max relationships in 1:1           = min(|A|, |B|)
Each multi-valued attribute        = 1 extra table
Derived attributes                 = 0 (never stored)

ISA (Total + Disjoint)    = subclasses only
ISA (all other combos)    = 1 + subclasses
```

---

*Next: [02 — Relational Database Model →](../02_Relational_Database_Model.md)*
