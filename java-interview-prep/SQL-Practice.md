# SQL Practice

## 1. Find the 2nd highest salary from an employee table.

```sql
-- Solution 1: Subquery
SELECT MAX(salary) FROM Employee 
WHERE salary < (SELECT MAX(salary) FROM Employee);

-- Solution 2: Limit/Offset
SELECT salary FROM Employee 
ORDER BY salary DESC 
LIMIT 1 OFFSET 1;

-- Solution 3: Dense Rank (Best for ties)
SELECT salary FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rnk 
    FROM Employee
) WHERE rnk = 2;
```

## 2. Get top N per group (highest salary per department).

Using Window Functions (`ROW_NUMBER()` or `RANK()`):
```sql
SELECT dept_id, employee_id, salary
FROM (
    SELECT dept_id, employee_id, salary, 
           ROW_NUMBER() OVER(PARTITION BY dept_id ORDER BY salary DESC) as rnk
    FROM Employee
) e
WHERE rnk <= N;
```

## 3. Find duplicate rows based on (email) and keep only latest.

Assuming `id` is auto-increment.
```sql
DELETE FROM Users 
WHERE id NOT IN (
    SELECT MAX(id) 
    FROM Users 
    GROUP BY email
);
```

## 4. Join: list all customers and their orders, including customers with no orders.

We need a **LEFT JOIN** to keep all Customers.

```sql
SELECT c.customer_name, o.order_id 
FROM Customers c
LEFT JOIN Orders o ON c.customer_id = o.customer_id;
```

## 5. Given orders(order_id, user_id, amount, created_at), find monthly revenue trend.

```sql
SELECT 
    DATE_FORMAT(created_at, '%Y-%m') as month,
    SUM(amount) as total_revenue
FROM orders
GROUP BY DATE_FORMAT(created_at, '%Y-%m')
ORDER BY month;
```

## 6. Find users who made purchases on consecutive days.

Self-join approach:
```sql
SELECT DISTINCT a.user_id
FROM Orders a
JOIN Orders b ON a.user_id = b.user_id
WHERE DATEDIFF(b.created_at, a.created_at) = 1;
```
Or using `LEAD()`:
```sql
SELECT DISTINCT user_id
FROM (
    SELECT user_id, created_at, 
           LEAD(created_at) OVER (PARTITION BY user_id ORDER BY created_at) as next_order
    FROM Orders
) t
WHERE DATEDIFF(next_order, created_at) = 1;
```

## 7. Find “inactive users” who haven’t ordered in last 90 days.

```sql
SELECT user_id FROM Users
WHERE user_id NOT IN (
    SELECT distinct user_id 
    FROM Orders 
    WHERE created_at > NOW() - INTERVAL 90 DAY
);
```
Or `LEFT JOIN` where order is NULL.

## 8. Given logs table, find sessions with duration > X.

Assuming logs have `session_id`, `start_time`, `end_time`.
```sql
SELECT session_id, (end_time - start_time) as duration
FROM logs
WHERE (end_time - start_time) > X;
```
If logs are separate rows (Start event, End Event), you group by `session_id` and subtract `MIN(time)` from `MAX(time)`.

## 9. Explain difference between WHERE vs HAVING.

*   **WHERE:** Filters rows **before** aggregation (Grouping).
*   **HAVING:** Filters groups **after** aggregation.

```sql
SELECT dept, SUM(salary) 
FROM emp 
WHERE active = 1          -- Filter rows first
GROUP BY dept 
HAVING SUM(salary) > 1000 -- Filter result groups later
```
