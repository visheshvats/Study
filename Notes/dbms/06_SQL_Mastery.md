# 6. SQL Mastery — GATE CSE Complete Guide

> **GATE Weightage:** 3–5 marks. Questions involve writing or interpreting SQL queries, understanding NULL handling, aggregate functions, GROUP BY/HAVING, nested subqueries, and DML/DDL distinctions.

---

## SQL Overview

**SQL (Structured Query Language)** is a **declarative** query language for relational databases. Unlike Relational Algebra (procedural), SQL specifies **what** data is needed, not **how** to retrieve it.

SQL is divided into:
| Category | Full Form | Examples |
|---|---|---|
| **DDL** | Data Definition Language | CREATE, ALTER, DROP, TRUNCATE |
| **DML** | Data Manipulation Language | SELECT, INSERT, UPDATE, DELETE |
| **DCL** | Data Control Language | GRANT, REVOKE |
| **TCL** | Transaction Control Language | COMMIT, ROLLBACK, SAVEPOINT |

> **⚠️ GATE Key Distinction:** SQL uses **bag (multiset) semantics** — duplicates are allowed by default. Relational Algebra uses **set semantics** — no duplicates.

---

## Key Definitions & Concepts

### DDL — Data Definition Language

#### CREATE TABLE

```sql
CREATE TABLE Student (
    Roll_No   INT          PRIMARY KEY,
    Name      VARCHAR(50)  NOT NULL,
    Age       INT          CHECK (Age >= 18),
    DeptID    INT,
    FOREIGN KEY (DeptID) REFERENCES Department(DeptID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);
```

#### Constraints in DDL

| Constraint | Meaning |
|---|---|
| `PRIMARY KEY` | Uniquely identifies each row; NOT NULL + UNIQUE |
| `FOREIGN KEY` | References PK of another table |
| `UNIQUE` | No duplicate values (NULLs allowed, multiple NULLs allowed in most RDBMS) |
| `NOT NULL` | Value cannot be NULL |
| `CHECK` | Boolean condition on values |
| `DEFAULT` | Specifies a default value |

> **⚠️ GATE Pitfall:** `UNIQUE` allows NULLs (in standard SQL). `PRIMARY KEY` does not.

#### ALTER TABLE

```sql
ALTER TABLE Student ADD Email VARCHAR(100);
ALTER TABLE Student DROP COLUMN Email;
ALTER TABLE Student MODIFY Age INT DEFAULT 18;
```

#### DROP vs. TRUNCATE vs. DELETE

| Command | What it does | Type | Rollback? | WHERE clause? |
|---|---|---|---|---|
| `DROP` | Removes table structure + data | DDL | ❌ No | ❌ No |
| `TRUNCATE` | Removes all rows, keeps structure | DDL | ❌ No | ❌ No |
| `DELETE` | Removes specific rows | DML | ✅ Yes | ✅ Yes |

> **⚠️ GATE Point:** TRUNCATE is DDL (auto-commits). DELETE is DML (can be rolled back within a transaction).

---

### DML — Data Manipulation Language

#### INSERT

```sql
INSERT INTO Student VALUES (1, 'Amit', 20, 101);
INSERT INTO Student (Roll_No, Name) VALUES (2, 'Priya');
```

#### UPDATE

```sql
UPDATE Student SET Age = 21 WHERE Roll_No = 1;
UPDATE Student SET DeptID = 102 WHERE DeptID = 101;
```

#### DELETE

```sql
DELETE FROM Student WHERE Age < 18;
DELETE FROM Student;  -- Deletes ALL rows (but keeps table)
```

---

### SELECT — The Core of SQL

#### Basic Syntax

```sql
SELECT [DISTINCT] column_list
FROM table_list
[WHERE condition]
[GROUP BY column_list]
[HAVING condition]
[ORDER BY column_list [ASC|DESC]]
[LIMIT n];
```

#### Order of Execution (Logical)

```
1. FROM       → Identify tables
2. WHERE      → Filter rows (before grouping)
3. GROUP BY   → Group rows
4. HAVING     → Filter groups (after grouping)
5. SELECT     → Choose columns / compute expressions
6. DISTINCT   → Remove duplicate rows
7. ORDER BY   → Sort results
8. LIMIT      → Restrict output count
```

> **⚠️ GATE Critical:** WHERE is applied **BEFORE** grouping. HAVING is applied **AFTER** grouping. Column aliases in SELECT are NOT available in WHERE.

---

### Aggregate Functions

| Function | Description | Ignores NULL? |
|---|---|---|
| `COUNT(*)` | Counts all rows | **No** (counts NULLs) |
| `COUNT(col)` | Counts non-NULL values | **Yes** |
| `SUM(col)` | Sum of non-NULL values | **Yes** |
| `AVG(col)` | Average of non-NULL values | **Yes** |
| `MAX(col)` | Maximum value | **Yes** |
| `MIN(col)` | Minimum value | **Yes** |

> **⚠️ GATE Critical:** `COUNT(*)` counts ALL rows including NULLs. `COUNT(col)` ignores NULLs. This is a **very common trap**.

**Example:**
```
Table: Employee(EmpID, Salary)
Data: (1, 50000), (2, NULL), (3, 60000)

COUNT(*)       = 3
COUNT(Salary)  = 2
SUM(Salary)    = 110000
AVG(Salary)    = 110000/2 = 55000  (NOT 110000/3!)
```

> **⚠️ GATE Trap:** AVG divides by count of **non-NULL** values, not total rows.

---

### GROUP BY & HAVING

```sql
SELECT DeptID, COUNT(*) AS EmpCount, AVG(Salary) AS AvgSal
FROM Employee
WHERE Salary > 30000         -- Filter individual rows FIRST
GROUP BY DeptID              -- Then group
HAVING COUNT(*) >= 5;        -- Then filter groups
```

**Rules:**
- Every column in SELECT (that's not inside an aggregate) **MUST** be in GROUP BY.
- HAVING can only reference columns in GROUP BY or aggregate functions.
- WHERE **cannot** use aggregate functions. HAVING **can**.

---

### NULL Handling in SQL — GATE Favourite Topic

SQL uses **three-valued logic**: TRUE, FALSE, **UNKNOWN**.

**Any comparison with NULL yields UNKNOWN:**
```sql
5 > NULL     → UNKNOWN
NULL = NULL  → UNKNOWN
NULL != NULL → UNKNOWN
```

**Truth Tables:**

| A | B | A AND B | A OR B | NOT A |
|---|---|---|---|---|
| T | U | **U** | **T** | F |
| F | U | **F** | **U** | T |
| U | U | **U** | **U** | **U** |

> **⚠️ GATE Critical Rule:** WHERE clause only passes rows where condition evaluates to **TRUE**. Rows with **UNKNOWN** or **FALSE** are **filtered out**.

**Testing for NULL:**
```sql
WHERE Salary IS NULL        -- Correct ✅
WHERE Salary IS NOT NULL    -- Correct ✅
WHERE Salary = NULL         -- WRONG ❌ (always UNKNOWN)
```

---

### Joins in SQL

```sql
-- CROSS JOIN (Cartesian Product)
SELECT * FROM R, S;
SELECT * FROM R CROSS JOIN S;

-- INNER JOIN (Natural)
SELECT * FROM R NATURAL JOIN S;

-- INNER JOIN (with condition)
SELECT * FROM R JOIN S ON R.A = S.A;
SELECT * FROM R INNER JOIN S ON R.A = S.A;

-- LEFT OUTER JOIN
SELECT * FROM R LEFT OUTER JOIN S ON R.A = S.A;

-- RIGHT OUTER JOIN
SELECT * FROM R RIGHT OUTER JOIN S ON R.A = S.A;

-- FULL OUTER JOIN
SELECT * FROM R FULL OUTER JOIN S ON R.A = S.A;
```

> **GATE Point:** `FROM R, S WHERE R.A = S.A` is equivalent to `FROM R INNER JOIN S ON R.A = S.A`.

---

### Subqueries (Nested Queries)

#### Types

| Type | Description |
|---|---|
| **Scalar subquery** | Returns a single value |
| **Row subquery** | Returns a single row |
| **Table subquery** | Returns a table (multiple rows/columns) |
| **Correlated subquery** | References outer query — re-executed for each outer row |

#### IN, EXISTS, ANY, ALL

```sql
-- IN: Check membership in a set
SELECT * FROM Student WHERE DeptID IN (SELECT DeptID FROM Department WHERE Budget > 100000);

-- EXISTS: True if subquery returns at least one row
SELECT * FROM Student S WHERE EXISTS (SELECT 1 FROM Enrolls E WHERE E.StudentID = S.Roll_No);

-- ANY / SOME: True if comparison is true for at least one subquery row
SELECT * FROM Student WHERE Age > ANY (SELECT Age FROM Student WHERE DeptID = 101);

-- ALL: True if comparison is true for ALL subquery rows
SELECT * FROM Student WHERE Age > ALL (SELECT Age FROM Student WHERE DeptID = 101);
```

**Key equivalences:**
```
x IN (subquery)     ≡  x = ANY (subquery)
x NOT IN (subquery) ≡  x != ALL (subquery)
```

> **⚠️ GATE Critical Trap (NOT IN with NULLs):**
> If the subquery returns any NULL, `NOT IN` returns **no results** (everything becomes UNKNOWN)!
```sql
-- If subquery returns {1, 2, NULL}:
5 NOT IN (1, 2, NULL) → 5 != 1 AND 5 != 2 AND 5 != NULL
                       → TRUE AND TRUE AND UNKNOWN
                       → UNKNOWN → Row is EXCLUDED!
```
> Use `NOT EXISTS` instead of `NOT IN` to avoid this trap.

---

### Set Operations in SQL

```sql
SELECT ... FROM R
UNION              -- Removes duplicates
SELECT ... FROM S;

SELECT ... FROM R
UNION ALL          -- Keeps duplicates
SELECT ... FROM S;

SELECT ... FROM R
INTERSECT          -- Common rows
SELECT ... FROM S;

SELECT ... FROM R
EXCEPT             -- In R but not in S (called MINUS in Oracle)
SELECT ... FROM S;
```

> **GATE Point:** UNION, INTERSECT, EXCEPT remove duplicates by default (set semantics). Use `ALL` to keep duplicates.

---

### Views

```sql
CREATE VIEW CS_Students AS
SELECT Roll_No, Name, Age
FROM Student
WHERE DeptID = (SELECT DeptID FROM Department WHERE DeptName = 'CS');
```

- Views are **virtual tables** — query is stored, not data.
- Views are **updatable** only under strict conditions:
  - Single table, no aggregates, no GROUP BY, no DISTINCT, no subqueries.
- Views with joins or aggregates are generally **NOT updatable**.

---

## Mathematical Foundations

### SQL to Relational Algebra Correspondence

| SQL | Relational Algebra |
|---|---|
| `SELECT DISTINCT A, B FROM R` | π_(A,B)(R) |
| `SELECT * FROM R WHERE c` | σ_c(R) |
| `SELECT * FROM R, S` | R × S |
| `SELECT * FROM R NATURAL JOIN S` | R ⋈ S |
| `SELECT * FROM R UNION SELECT * FROM S` | R ∪ S |
| `SELECT * FROM R EXCEPT SELECT * FROM S` | R − S |

> **Key Difference:** SQL's SELECT (without DISTINCT) = **bag projection** (duplicates kept). RA's π = **set projection** (duplicates removed).

---

## GATE Specific Focus Points

### 1. Correlated vs. Non-Correlated Subqueries

| Type | Execution | Performance |
|---|---|---|
| **Non-Correlated** | Inner query runs **once** | Faster |
| **Correlated** | Inner query runs **for each outer row** | Slower |

```sql
-- Non-correlated: subquery is independent
SELECT * FROM Student WHERE DeptID IN (SELECT DeptID FROM Department WHERE Budget > 100000);

-- Correlated: subquery references outer query
SELECT * FROM Student S WHERE EXISTS (
    SELECT 1 FROM Enrolls E WHERE E.StudentID = S.Roll_No
);
```

### 2. HAVING vs. WHERE

```sql
-- WRONG: Cannot use aggregate in WHERE
SELECT DeptID, COUNT(*) FROM Employee WHERE COUNT(*) > 5 GROUP BY DeptID;  -- ERROR!

-- CORRECT: Use HAVING for aggregate conditions
SELECT DeptID, COUNT(*) FROM Employee GROUP BY DeptID HAVING COUNT(*) > 5;
```

### 3. Natural Join Danger

```sql
-- If R(A, B, C) and S(B, C, D):
-- NATURAL JOIN equates BOTH B and C
-- If you only want to join on B, use explicit JOIN ON
SELECT * FROM R JOIN S ON R.B = S.B;
```

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| `COUNT(*)` ignores NULL | **No.** `COUNT(*)` counts ALL rows. Only `COUNT(col)` ignores NULL |
| `AVG` divides by total rows | **No.** `AVG` divides by count of **non-NULL** values |
| `NULL = NULL` is TRUE | **No.** It's **UNKNOWN**. Use `IS NULL` |
| `NOT IN` with NULLs works fine | **No.** NULLs make `NOT IN` return empty. Use `NOT EXISTS` |
| `UNIQUE` doesn't allow NULLs | `UNIQUE` allows NULLs (multiple NULLs in most RDBMS) |
| `WHERE` can use aggregates | **No.** Use `HAVING` for aggregate conditions |
| `SELECT` can list columns not in `GROUP BY` | **Only** if they're inside aggregate functions |
| `TRUNCATE` can be rolled back | **No.** TRUNCATE is DDL (auto-commit). DELETE can be rolled back |
| `ORDER BY` affects which rows are returned | **No.** It only affects **display order**, not filtering |

---

## 3 Worked Examples

### Example 1: Aggregate Query (Easy)

**Q:** Find departments with more than 3 employees earning above 50000.

```sql
SELECT DeptID, COUNT(*) AS HighEarners
FROM Employee
WHERE Salary > 50000          -- Filter rows first
GROUP BY DeptID               -- Group by department
HAVING COUNT(*) > 3;          -- Filter groups
```

---

### Example 2: NULL Handling (Medium — GATE Classic)

**Q:** Given table `R(A, B)` with data:

| A | B |
|---|---|
| 1 | NULL |
| 2 | 3 |
| 3 | NULL |
| 4 | 5 |

What does this return?

```sql
SELECT COUNT(*), COUNT(B), SUM(B), AVG(B) FROM R;
```

**Solution:**
| Function | Value | Explanation |
|---|---|---|
| `COUNT(*)` | **4** | Counts all rows (including NULLs) |
| `COUNT(B)` | **2** | Counts non-NULL values of B |
| `SUM(B)` | **8** | 3 + 5 = 8 (ignores NULLs) |
| `AVG(B)` | **4** | 8 / 2 = 4 (divides by non-NULL count) |

---

### Example 3: Correlated Subquery with NOT EXISTS (GATE Level)

**Q:** Find students who are enrolled in **ALL** courses offered by the 'CS' department.

```sql
SELECT S.Roll_No, S.Name
FROM Student S
WHERE NOT EXISTS (
    -- Courses in CS that this student is NOT enrolled in
    SELECT C.CourseID
    FROM Course C
    WHERE C.DeptID = (SELECT DeptID FROM Department WHERE DeptName = 'CS')
    AND NOT EXISTS (
        SELECT 1
        FROM Enrolls E
        WHERE E.StudentID = S.Roll_No
        AND E.CourseID = C.CourseID
    )
);
```

**Logic:** This implements **universal quantification** ("for all") using **double negation**:
- "Student is enrolled in ALL CS courses"
- = "There does NOT EXIST a CS course in which the student is NOT enrolled"

This is the **SQL equivalent** of the **division (÷)** operator in Relational Algebra.

---

## Revision Table

| Concept | Key Point |
|---|---|
| **SELECT** | Bag semantics (duplicates allowed). Use DISTINCT for set semantics |
| **WHERE** | Filters rows BEFORE grouping. Cannot use aggregates |
| **GROUP BY** | Groups rows. SELECT columns must be in GROUP BY or aggregates |
| **HAVING** | Filters groups AFTER grouping. CAN use aggregates |
| **NULL comparisons** | Any comparison with NULL → UNKNOWN. Use IS NULL / IS NOT NULL |
| **COUNT(*)** | Counts all rows including NULLs |
| **COUNT(col)** | Counts only non-NULL values |
| **AVG** | Divides by non-NULL count, not total rows |
| **NOT IN** | Fails with NULLs — use NOT EXISTS instead |
| **TRUNCATE** | DDL, cannot rollback. DELETE is DML, can rollback |
| **View** | Virtual table. Updatable only under strict conditions |
| **UNION** | Removes duplicates. UNION ALL keeps duplicates |

---

*← [05 — Relational Algebra & Calculus](05_Relational_Algebra_and_Calculus.md) | [07 — Transactions & Concurrency →](07_Transactions_and_Concurrency.md)*
