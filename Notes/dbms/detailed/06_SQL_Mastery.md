# 6. SQL Mastery — Detailed GATE CSE Guide

> **GATE Weightage:** 3–5 marks. Questions involve writing/interpreting SQL queries, NULL handling traps, aggregate function behavior, GROUP BY/HAVING logic, and nested subqueries.

---

## What is SQL?

**SQL (Structured Query Language)** is the standard language for interacting with relational databases. While Relational Algebra is theoretical, SQL is what you actually use in real databases like MySQL, PostgreSQL, Oracle, etc.

**Key difference from RA:** SQL is **declarative** — you tell the database **WHAT** you want, and it figures out **HOW** to get it (the query optimizer does this). RA is procedural — you specify the exact steps.

**Another key difference:** SQL uses **bag (multiset) semantics** by default — duplicates ARE allowed. RA uses set semantics — no duplicates. This is important for GATE!

### SQL Sub-Languages

| Category | Purpose | Commands | Can Rollback? |
|---|---|---|---|
| **DDL** (Data Definition) | Define/modify table structure | CREATE, ALTER, DROP, TRUNCATE | No (auto-commit) |
| **DML** (Data Manipulation) | Work with data | SELECT, INSERT, UPDATE, DELETE | Yes (within transaction) |
| **DCL** (Data Control) | Manage permissions | GRANT, REVOKE | — |
| **TCL** (Transaction Control) | Manage transactions | COMMIT, ROLLBACK, SAVEPOINT | — |

---

## DDL — Creating and Modifying Tables

### CREATE TABLE

```sql
CREATE TABLE Student (
    Roll_No    INT           PRIMARY KEY,
    Name       VARCHAR(50)   NOT NULL,
    Age        INT           CHECK (Age >= 16 AND Age <= 40),
    Email      VARCHAR(100)  UNIQUE,
    DeptID     INT           DEFAULT 1,
    FOREIGN KEY (DeptID) REFERENCES Department(DeptID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);
```

Let's understand each constraint:

| Constraint | What it does | NULL allowed? | Duplicate allowed? |
|---|---|---|---|
| `PRIMARY KEY` | Uniquely identifies each row | ❌ No | ❌ No |
| `NOT NULL` | Must have a value | ❌ No | ✅ Yes |
| `UNIQUE` | No duplicate values | ✅ Yes (multiple NULLs OK) | ❌ No |
| `CHECK` | Custom condition must be true | ✅ Yes (NULL makes check pass) | ✅ Yes |
| `DEFAULT` | Provides a default value if none given | ✅ Yes | ✅ Yes |
| `FOREIGN KEY` | Must reference valid PK in another table | ✅ Yes (unless NOT NULL) | ✅ Yes |

> **⚠️ GATE Trap:** `UNIQUE` allows NULLs, but `PRIMARY KEY` does not. This is because NULL ≠ NULL, so multiple NULLs are considered "different."

### DROP vs. TRUNCATE vs. DELETE

These three all "remove" data, but they work very differently:

| Feature | DELETE | TRUNCATE | DROP |
|---|---|---|---|
| **What it removes** | Specific rows (or all) | All rows | Entire table (structure + data) |
| **Type** | DML | DDL | DDL |
| **WHERE clause** | ✅ Yes | ❌ No | ❌ No |
| **Can be rolled back** | ✅ Yes | ❌ No (auto-commit) | ❌ No |
| **Triggers fired** | ✅ Yes | ❌ No | ❌ No |
| **Table structure after** | Still exists (empty) | Still exists (empty) | Gone |

> **GATE Question:** "Which operation cannot be rolled back?" → TRUNCATE and DROP (both DDL, auto-commit).

---

## SELECT — The Heart of SQL Queries

### Basic Syntax and Execution Order

```sql
SELECT [DISTINCT] column_list         -- 5. Choose columns
FROM table_list                        -- 1. Identify tables
[WHERE condition]                      -- 2. Filter individual rows
[GROUP BY column_list]                 -- 3. Group rows
[HAVING condition]                     -- 4. Filter groups
[ORDER BY column_list [ASC|DESC]]     -- 6. Sort results
[LIMIT n];                            -- 7. Limit output
```

**The order you WRITE it: SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY**

**The order the database EXECUTES it: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY**

**This is CRITICAL for understanding SQL behavior!**

Let's trace through an example:

```sql
SELECT Dept, COUNT(*) AS EmpCount
FROM Employee
WHERE Salary > 30000
GROUP BY Dept
HAVING COUNT(*) >= 3
ORDER BY EmpCount DESC;
```

**Execution steps:**

1. **FROM Employee** — Start with the entire Employee table  
2. **WHERE Salary > 30000** — Remove rows where Salary ≤ 30000  
3. **GROUP BY Dept** — Group remaining rows by department  
4. **HAVING COUNT(*) >= 3** — Remove groups with fewer than 3 members  
5. **SELECT Dept, COUNT(*)** — For each surviving group, output Dept and count  
6. **ORDER BY EmpCount DESC** — Sort by count, highest first  

---

## NULL Handling — The #1 GATE Trap Topic

### Three-Valued Logic

SQL doesn't use normal TRUE/FALSE logic. It uses **three-valued logic**: TRUE, FALSE, and **UNKNOWN**.

**Any comparison involving NULL produces UNKNOWN:**
```sql
5 > NULL      → UNKNOWN
NULL = NULL   → UNKNOWN (NOT TRUE!)
NULL != NULL  → UNKNOWN (NOT TRUE!)
NULL + 5      → NULL
NULL > 10     → UNKNOWN
```

### Truth Tables for Three-Valued Logic

Think of UNKNOWN as "maybe":

**AND:**
| A | B | A AND B |
|---|---|---|
| TRUE | UNKNOWN | **UNKNOWN** (TRUE and maybe = maybe) |
| FALSE | UNKNOWN | **FALSE** (FALSE and anything = FALSE) |
| UNKNOWN | UNKNOWN | **UNKNOWN** |

**OR:**
| A | B | A OR B |
|---|---|---|
| TRUE | UNKNOWN | **TRUE** (TRUE or anything = TRUE) |
| FALSE | UNKNOWN | **UNKNOWN** (FALSE or maybe = maybe) |
| UNKNOWN | UNKNOWN | **UNKNOWN** |

**NOT:**
| A | NOT A |
|---|---|
| TRUE | FALSE |
| FALSE | TRUE |
| UNKNOWN | **UNKNOWN** |

### The Golden Rule

> **WHERE only passes rows where the condition is TRUE.** Rows with UNKNOWN or FALSE are **filtered out.**

This means:
```sql
-- Given: Employee with Salary values: 50000, NULL, 60000, NULL, 40000

SELECT * FROM Employee WHERE Salary > 45000;
-- Returns: 50000, 60000 (the NULLs are EXCLUDED because NULL > 45000 = UNKNOWN)

SELECT * FROM Employee WHERE Salary <= 45000;
-- Returns: 40000 (NULLs EXCLUDED again!)

SELECT * FROM Employee WHERE Salary > 45000 OR Salary <= 45000;
-- Returns: 50000, 60000, 40000 (NULLs STILL EXCLUDED! UNKNOWN OR UNKNOWN = UNKNOWN)
```

> **⚠️ Shocking result:** `WHERE Salary > 45000 OR Salary <= 45000` does NOT return all rows! Rows with NULL Salary are excluded because the condition evaluates to UNKNOWN.

### Testing for NULL

```sql
-- CORRECT ways:
WHERE Salary IS NULL
WHERE Salary IS NOT NULL

-- WRONG way (NEVER use = or != with NULL):
WHERE Salary = NULL     -- Always UNKNOWN, never returns any row!
WHERE Salary != NULL    -- Always UNKNOWN, same problem!
```

---

## Aggregate Functions — Detailed Behavior

| Function | What it does | Handles NULL? | Example |
|---|---|---|---|
| `COUNT(*)` | Counts ALL rows | ❌ Counts NULLs too | 5 rows → 5 |
| `COUNT(col)` | Counts non-NULL values in column | ✅ Ignores NULLs | 3 non-NULL → 3 |
| `SUM(col)` | Sum of non-NULL values | ✅ Ignores NULLs | 50+NULL+60 = 110 |
| `AVG(col)` | Average of non-NULL values | ✅ Ignores NULLs | 110/2 = 55 (NOT 110/3!) |
| `MAX(col)` | Maximum non-NULL value | ✅ Ignores NULLs | max(50,NULL,60) = 60 |
| `MIN(col)` | Minimum non-NULL value | ✅ Ignores NULLs | min(50,NULL,60) = 50 |

### The COUNT(*) vs COUNT(col) Trap

**Given table:**
| EmpID | Salary |
|---|---|
| 1 | 50000 |
| 2 | NULL |
| 3 | 60000 |

```sql
SELECT COUNT(*) FROM Employee;         -- Returns 3 (counts ALL rows)
SELECT COUNT(Salary) FROM Employee;    -- Returns 2 (ignores NULL Salary)
```

### The AVG Trap

```sql
SELECT AVG(Salary) FROM Employee;
-- Salary values: 50000, NULL, 60000
-- AVG = (50000 + 60000) / 2 = 55000
-- NOT (50000 + 0 + 60000) / 3 = 36667!
-- NULL rows are EXCLUDED from both numerator AND denominator
```

> **GATE Tip:** AVG divides by the count of **non-NULL** values, not the total number of rows.

---

## GROUP BY and HAVING — Step by Step

### GROUP BY Rules

1. **Every column in SELECT** (that's NOT inside an aggregate function) **MUST be in GROUP BY**
2. You can have columns in GROUP BY that are NOT in SELECT
3. GROUP BY creates groups, and aggregates compute within each group

```sql
-- CORRECT:
SELECT Dept, COUNT(*), AVG(Salary)
FROM Employee
GROUP BY Dept;

-- WRONG (Name is not in GROUP BY and not in an aggregate):
SELECT Dept, Name, COUNT(*)
FROM Employee
GROUP BY Dept;  -- ERROR! Which Name to show for each group?
```

### HAVING vs WHERE — The Critical Difference

| | WHERE | HAVING |
|---|---|---|
| **When applied** | BEFORE grouping | AFTER grouping |
| **Filters** | Individual rows | Groups |
| **Can use aggregates?** | ❌ NO | ✅ YES |
| **Can use regular cols?** | ✅ YES | ✅ Only GROUP BY cols and aggregates |

```sql
-- WRONG: Aggregate in WHERE
SELECT Dept, COUNT(*)
FROM Employee
WHERE COUNT(*) > 5    -- ERROR! Can't use aggregate in WHERE
GROUP BY Dept;

-- CORRECT: Aggregate in HAVING
SELECT Dept, COUNT(*)
FROM Employee
GROUP BY Dept
HAVING COUNT(*) > 5;  -- Filter groups AFTER grouping
```

**Complete example showing both:**
```sql
SELECT Dept, AVG(Salary) AS AvgSal
FROM Employee
WHERE Age > 25           -- 1. First filter: keep only employees > 25 years old
GROUP BY Dept             -- 2. Then group by department
HAVING AVG(Salary) > 50000  -- 3. Then keep only groups with avg salary > 50000
ORDER BY AvgSal DESC;    -- 4. Sort remaining groups
```

---

## Subqueries (Nested Queries) — Detailed

### Non-Correlated Subquery

The inner query runs **independently** — it doesn't reference the outer query. It runs ONCE.

```sql
-- Find employees whose salary is above the company average
SELECT Name, Salary
FROM Employee
WHERE Salary > (SELECT AVG(Salary) FROM Employee);
```

The subquery `(SELECT AVG(Salary) FROM Employee)` runs once, returns one number (say 50000), and then the outer query becomes `WHERE Salary > 50000`.

### Correlated Subquery

The inner query **references the outer query** — it runs ONCE FOR EACH ROW of the outer query. Slower, but more powerful.

```sql
-- Find employees who earn more than the average of their department
SELECT E1.Name, E1.Salary, E1.Dept
FROM Employee E1
WHERE E1.Salary > (
    SELECT AVG(E2.Salary)
    FROM Employee E2
    WHERE E2.Dept = E1.Dept    -- References outer query!
);
```

For each employee in the outer query, the inner query computes the average salary of THAT employee's department.

### IN, NOT IN, EXISTS, NOT EXISTS

#### IN — "Is this value in the set?"
```sql
-- Students in departments with budget > 1M
SELECT * FROM Student
WHERE DeptID IN (SELECT DeptID FROM Department WHERE Budget > 1000000);
```

#### NOT IN — "Is this value NOT in the set?"
```sql
SELECT * FROM Student
WHERE DeptID NOT IN (SELECT DeptID FROM Department WHERE Budget > 1000000);
```

> **⚠️ GATE CRITICAL TRAP — NOT IN with NULLs:**

If the subquery returns any NULL value, `NOT IN` returns **NOTHING** (empty result)!

**Why?** Let's trace the logic:
```sql
-- Subquery returns: (1, 2, NULL)

-- For value 5:
5 NOT IN (1, 2, NULL)
= 5 != 1 AND 5 != 2 AND 5 != NULL
= TRUE  AND TRUE  AND UNKNOWN
= UNKNOWN
→ WHERE filters this out! Row excluded!

-- This happens for EVERY value! So NOT IN with NULL = empty result!
```

**Solution:** Use `NOT EXISTS` instead:
```sql
SELECT * FROM Student S
WHERE NOT EXISTS (
    SELECT 1 FROM Department D
    WHERE D.DeptID = S.DeptID AND D.Budget > 1000000
);
```

`NOT EXISTS` doesn't have the NULL problem because it checks for the existence of rows, not value equality.

#### ANY/SOME and ALL
```sql
-- Salary > ANY value in subquery (i.e., > at least one value = > MIN)
SELECT * FROM Employee WHERE Salary > ANY (SELECT Salary FROM Employee WHERE Dept = 'CS');

-- Salary > ALL values in subquery (i.e., > every value = > MAX)
SELECT * FROM Employee WHERE Salary > ALL (SELECT Salary FROM Employee WHERE Dept = 'CS');
```

**Equivalences:**
```
x IN (subquery)     ≡  x = ANY (subquery)
x NOT IN (subquery) ≡  x != ALL (subquery)
```

---

## Expressing "For All" in SQL — Double Negation

SQL doesn't have a "FOR ALL" keyword. Instead, you use **double negation**:

"Find students enrolled in **ALL** CS courses" becomes:
"Find students where there does **NOT EXIST** a CS course in which the student is **NOT** enrolled"

```sql
SELECT S.Roll_No, S.Name
FROM Student S
WHERE NOT EXISTS (
    SELECT C.CourseID
    FROM Course C
    WHERE C.Dept = 'CS'
    AND NOT EXISTS (
        SELECT 1
        FROM Enrollment E
        WHERE E.StudentID = S.Roll_No
        AND E.CourseID = C.CourseID
    )
);
```

This is the SQL equivalent of the **division (÷)** operator in Relational Algebra.

---

## Set Operations in SQL

```sql
-- UNION: combines results, removes duplicates
SELECT Name FROM Student UNION SELECT Name FROM Faculty;

-- UNION ALL: combines results, KEEPS duplicates
SELECT Name FROM Student UNION ALL SELECT Name FROM Faculty;

-- INTERSECT: common rows
SELECT Name FROM Student INTERSECT SELECT Name FROM Faculty;

-- EXCEPT (or MINUS in Oracle): in first but not second
SELECT Name FROM Student EXCEPT SELECT Name FROM Faculty;
```

> **GATE Point:** UNION, INTERSECT, EXCEPT remove duplicates by default (set semantics). Use ALL to keep duplicates (bag semantics).

---

## Views — Virtual Tables

A **view** is a stored query that acts like a virtual table. No data is physically stored — the query runs every time you access the view.

```sql
CREATE VIEW CS_Students AS
SELECT Roll_No, Name, Age FROM Student WHERE Dept = 'CS';

-- Use it like a regular table:
SELECT * FROM CS_Students WHERE Age > 20;
```

**Updatable views:** A view is updatable (you can INSERT/UPDATE/DELETE through it) only under strict conditions:
- Based on a single table
- No aggregates (COUNT, SUM, etc.)
- No GROUP BY or HAVING
- No DISTINCT
- No subqueries in SELECT
- No window functions

---

## Common Pitfalls Summary

| Pitfall | Reality |
|---|---|
| `COUNT(*)` ignores NULL | ❌ `COUNT(*)` counts ALL rows. Only `COUNT(col)` ignores NULL |
| `AVG` divides by total rows | ❌ Divides by count of NON-NULL values |
| `NULL = NULL` is TRUE | ❌ It's UNKNOWN. Use `IS NULL` |
| `NOT IN` with NULLs works fine | ❌ Returns empty set! Use `NOT EXISTS` |
| `WHERE` can use aggregates | ❌ Use `HAVING` for aggregate conditions |
| `TRUNCATE` can be rolled back | ❌ TRUNCATE is DDL, auto-commits |
| `UNIQUE` doesn't allow NULL | ❌ UNIQUE allows NULLs |
| SQL removes duplicates by default | ❌ SQL keeps duplicates by default (use DISTINCT to remove) |

---

*← [05 — Relational Algebra & Calculus](05_Relational_Algebra_and_Calculus.md) | [07 — Transactions & Concurrency →](07_Transactions_and_Concurrency.md)*
