# Round 8 — Database + DBMS

## 1. What is normalization? Explain 1NF, 2NF, 3NF in your own words.

Normalization is the process of organizing data to reduce redundancy and anomalies.
*   **1NF (Atomic):** No repeating groups. Each cell holds a single value. Unique rows.
*   **2NF (No Partial Dependency):** Must be in 1NF. All non-key columns must rely on the **whole** primary key (not just part of a composite key).
*   **3NF (No Transitive Dependency):** Must be in 2NF. Non-key columns should not rely on other non-key columns. e.g., ZipCode implies City -> Move Zip/City to a separate table.

## 2. What is denormalization and why would you do it?

Adding redundancy back into the table structure (combining tables) to improve **Read Performance**.
*   **Why?** Normalization requires Joins. Joins are expensive. If you frequently read Customer Name + Address + Order Status together, keeping them in one "flat" table (or a materialized view) makes the query faster (O(1) read instead of O(N) join).

## 3. Primary key vs unique key vs candidate key vs composite key.

*   **Primary Key (PK):** Unique Identifier. Not Null. Only one per table. Clustered Index (usually).
*   **Unique Key (UK):** Unique values. Can handle Nulls (depending on DB). Multiple per table. Non-Clustered.
*   **Candidate Key:** Any column(s) that *could* be a Primary Key (e.g., Email, SSN, EmployeeID).
*   **Composite Key:** A PK made of two or more columns (e.g., OrderID + ProductID).

## 4. What is a foreign key and what does referential integrity mean?

*   **Foreign Key (FK):** A column that points to the Primary Key of another table. It links them.
*   **Referential Integrity:** The rule that the DB enforces: "You cannot point to something that does not exist." You can't add an Order for UserID=99 if User 99 doesn't exist. You can't delete User 99 if they have existing Orders (unless Cascade Delete is on).

## 5. What is an index? Why does it speed up reads but slow down writes?

**Index:** A B-Tree data structure (separate from table) that stores sorted keys and pointers to the row.
*   **Read Speed:** Binary Search O(log N) instead of Full Table Scan O(N).
*   **Write Speed:** Every INSERT/UPDATE/DELETE requires updating the Table file AND the Index structure (rebalancing the tree).

## 6. Clustered vs non-clustered index (conceptually).

*   **Clustered:** Determines the **physical order** of data on the disk. Like a Phonebook (sorted by name). Only 1 per table (usually PK). Leaf nodes contain the actual data.
*   **Non-Clustered:** Logical order. Like the Index at the back of a Textbook. Contains a pointer to the physical location (or Clustered key). Many per table.

## 7. B-Tree index vs Hash index — when each works best.

*   **B-Tree:** Best for **Range** queries (`>`, `<`, `BETWEEN`, `LIKE 'A%'`) and Sorting. Default in most DBs.
*   **Hash:** Best for **Exact Match** queries (`=` validation). O(1) lookup. Cannot do ranges or sorting. (Common in Redis, Memory storage engines).

## 8. ACID properties — explain with an example.

*   **Atomicity:** All or Nothing. (Transfer: Debit A, Credit B. If B fails, A rolls back).
*   **Consistency:** DB moves from valid state to valid state (Constraints met).
*   **Isolation:** Transactions occur independently. (See below).
*   **Durability:** Committed data is saved (disk) even if power fails.

## 9. What is a transaction isolation level? Dirty read / non-repeatable / phantom.

How much one transaction sees of another running transaction.
1.  **Read Uncommitted (Dirty Read):** You read uncommitted data (that might change back).
2.  **Read Committed (Non-Repeatable Read):** You only read committed execution. But re-reading the same row might show different data if someone updated it.
3.  **Repeatable Read (Phantom Read):** The row you read stays same. But running a range query again might show *new* rows (Phantoms). (MySQL Default).
4.  **Serializable:** No concurrency. Pure order. Slowest.

## 10. Deadlock in DB — how does it happen? how DB resolves?

Txn A locks Row 1, wants Row 2.
Txn B locks Row 2, wants Row 1.
**Resolution:** The DB Deadlock Detector wakes up, picks a "victim" (usually the smaller transaction), kills it (Rollback), and lets the other proceed.

## 11. What is pagination best practice for large data? (offset vs keyset)

*   **Offset Pagination (`OFFSET 10000 LIMIT 10`):** BAD for deep paging. DB must fetch 10010 rows and throw away 10000. Slow O(N).
*   **Keyset (Cursor) Pagination (`WHERE id > 10000 LIMIT 10`):** GOOD. Uses index to jump directly to ID 10000. Fast O(1) or O(log N).

## 12. Partitioning vs Sharding?

*   **Partitioning:** Splitting one table into smaller chunks **within the same DB instance** (e.g., Partition by Year).
*   **Sharding:** Splitting data across **multiple DB servers/machines**. (User IDs 1-1M -> Server A, 1M-2M -> Server B).

## 13. When would you use read replicas?

When your application is **Read-Heavy** (80% reads, 20% writes).
You write to Master. Replicates to Slaves (Async).
All Reads go to Slaves. Relieves load on Master.
**Trade-off:** Eventual Consistency (Slave might lag behind Master by milliseconds).
