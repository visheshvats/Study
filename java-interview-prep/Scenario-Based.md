# Scenario-Based (Java + DBMS System Design)

## 1. Your API is slow: query takes 5 seconds. How do you debug end-to-end?

**Step-by-Step Debugging:**
1.  **Isolate Component:** Is it the Application (GC, CPU) or the Database?
2.  **Inspect Logs:** Check latency metrics (APM tools like NewRelic/Datadog or simple timestamp logs).
3.  **Database Analysis:**
    *   **Explain Plan:** Run `EXPLAIN SELECT ...` to see if it uses an Index.
    *   **Indexing:** If it's a Full Table Scan, add an index.
    *   **Locking:** Check if the query is waiting on a lock held by another transaction.
4.  **Application Analysis:**
    *   **N+1 Problem:** Are we making 5000 small DB calls instead of 1 joining call?
    *   **Payload:** Are we fetching 10MB of data when we only need ID and Name?

## 2. You see duplicate payments in DB. How do you design idempotency?

**Idempotency:** Making multiple identical requests has the same effect as making a single request.

**Design:**
1.  **Idempotency Key:** Client generates a unique UUID (e.g., `req_123`) for every payment attempt and sends it in the Header.
2.  **Storage:** Server checks a dedicated key-value store (Redis) or DB table for `req_123`.
    *   If **exists**: Return previous success response immediately. Do NOT process.
    *   If **not exists**: Lock the specific key, store `req_123` as "PROCESSING", execute payment logic.
3.  **Completion:** Update status to "COMPLETED".

## 3. Two services update the same row frequently—how do you prevent lost updates?

**Optimistic Locking:**
1.  Add a `version` (int) column to the table.
2.  **Read:** `SELECT id, data, version FROM table WHERE id=1` (Returns version=5).
3.  **Update:**
    ```sql
    UPDATE table 
    SET data='new', version=version+1 
    WHERE id=1 AND version=5;
    ```
4.  **Check:** Check row count.
    *   If 1: Success.
    *   If 0: Someone else updated it (Version is now 6). Throw `OptimisticLockException` and retry the whole operation options.

## 4. High traffic read-heavy endpoint: what caching strategy do you use?

**Strategy:** Look-Aside Cache (Lazy Loading).

1.  **Read:** App checks Cache (Redis).
    *   **Hit:** Return data. (Fast).
    *   **Miss:** Read from DB. Write to Cache with a generic TTL (Time To Live). Return data.
2.  **Write:** Update DB first. Then **Invalidate** (delete) the cache entry. (Better than updating cache, avoids race conditions).

**For massive scale:** Use a CDN for static assets and "Read Replicas" for the DB.

## 5. Your users table is 200M rows. How do you design search/filter and indexing?

A standard SQL `LIKE %term%` will be dead slow. B-Trees are bad for fuzzy search.

**Design:**
1.  **Offload Search:** Use **Elasticsearch** (or Solr). Sync User DB to ES.
2.  **Indexing:** Create an Inverted Index in ES on searchable fields (name, email).
3.  **Flow:**
    *   App queries ES -> Gets IDs.
    *   App queries DB -> `SELECT * FROM Users WHERE id IN (...)`.
    (Or store necessary display data in ES directly to skip DB lookup).

## 6. You need consistent balance updates in banking-like system. How do you ensure correctness?

**Transactions + Pessimistic Locking.**
Assume we must prevent `Balance < 0` strictly.

1.  **Transaction Start.**
2.  **Select for Update:**
    ```sql
    SELECT balance FROM Accounts WHERE id=1 FOR UPDATE;
    ```
    This puts a **Write Lock** on the row. No other transaction can read or write to this row until we commit.
3.  **Business Logic:** Check logic, calculate new balance.
4.  **Update:** Update row.
5.  **Commit.** Releases lock.

*Note: Pessimistic locking reduces concurrency but guarantees correctness for critical financial data.*
