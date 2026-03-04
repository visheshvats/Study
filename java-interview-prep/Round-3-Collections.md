# Round 3 — Collections Framework (Common)

## 1. HashMap vs Hashtable vs ConcurrentHashMap.

| Feature | HashMap | Hashtable | ConcurrentHashMap |
| :--- | :--- | :--- | :--- |
| **Thread Safe** | No. | Yes (synchronized methods). | Yes (Bucket-level locking / CAS). |
| **Null keys/values** | Allow 1 null key, many values. | No nulls allowed. | No nulls allowed. |
| **Performance** | High. | Slow (global lock). | Very High (concurrent reads). |
| **Use Case** | General purpose (non-threaded). | Legacy (Obsolete). | High concurrency. |

## 2. How does HashMap work internally? (hash, bucket, collision)

1.  **Key.hashCode()**: Calculate hash of the key.
2.  **Index**: `hash % capacity` (actually `(n-1) & hash` for bitwise speed) determines which "bucket" (index of array) to use.
3.  **Collision**: If bucket is empty, store node. If bucket is full (collision), it checks `equals()` against existing keys.
4.  **Chaining**: If `equals()` is false, it appends the new node to the LinkedList (or Red-Black Tree in Java 8+) in that bucket. If true, it overwrites value.

## 3. What triggers HashMap rehash/resize?

When the number of entries exceeds `Capacity * Load Factor`.
*   **Default Capacity:** 16
*   **Default Load Factor:** 0.75
*   **Trigger:** When size > 12 (16 * 0.75), strict resizing happens within `put()` operation.
*   **Process:** New array of double size (32) is created. All existing entries are recalculated (rehashed) and moved to new buckets. Expensive operation!

## 4. How does Java handle hash collisions in modern versions?

**Java 7:** Only LinkedList chaining. Worst case search `O(n)` if all keys hash to same bucket (DoS attack vulnerability).
**Java 8+:** If bucket size grows beyond threshold (TREEIFY_THRESHOLD = 8), the LinkedList is converted to a **Red-Black Tree**.
*   **Benefit:** Search performance improves from `O(n)` to `O(log n)`.

## 5. Why should hashCode() and equals() be consistent? What breaks otherwise?

**Contract:** If `a.equals(b)` is true, `a.hashCode()` MUST be `b.hashCode()`.

**If broken:**
You put an object in HashMap. It goes to Bucket X based on Hash1.
You try to `get()` it using an "equal" object. If Hash2 is different, HashMap looks in Bucket Y and returns `null`. You lose your data essentially.

## 6. ArrayList vs LinkedList — give real use-cases.

*   **ArrayList (Dynamic Array):**
    *   Fast Random Access `get(index)`: `O(1)`.
    *   Slow Insert/Delete in middle: `O(n)` (shifting elements).
    *   **Use:** Read-heavy, list size known, accessing by index. 90% of cases.
*   **LinkedList (Doubly Linked List):**
    *   Slow Random Access: `O(n)` (traversal).
    *   Fast Insert/Delete (if you have the iterator/node): `O(1)`.
    *   **Use:** Queue/Deque implementations. Frequent additions/deletions at the beginning or middle.

## 7. HashSet internally uses what? Why no duplicates?

**Internally:** `HashSet` uses a `HashMap`.
*   **Add:** When you call `set.add(value)`, it essentially calls `map.put(value, PRESENT)`.
*   **PRESENT:** A dummy object value.
*   **Uniqueness:** Since HashMap keys must be unique, the Set (which uses the keys) automatically ensures no duplicates. `put` returns the old value (if any), allowing `add` to return false on duplicate.

## 8. TreeSet/TreeMap sorting rules: Comparable vs Comparator.

*   **Comparable (Natural Ordering):**
    *   Class implements `Comparable<T>` interface.
    *   Override `compareTo(T o)`.
    *   Structure: Definition is **inside** the class (e.g., Integer, String).
    *   `Collections.sort(list);`

*   **Comparator (Custom Ordering):**
    *   Separate class/lambda implements `Comparator<T>`.
    *   Override `compare(T o1, T o2)`.
    *   Structure: Definition **outside** the class.
    *   Can have multiple strategies (SortByName, SortByAge).
    *   `new TreeMap<>(new SortByAgeComparator());`

## 9. When do you get ConcurrentModificationException?

When you iterate over a collection (using Iterator or for-each) and modify the collection structure (add/remove) **directly** using the collection's methods (not the Iterator's remove method).

```java
for(String s : list) {
    if(s.equals("A")) list.remove(s); // BOOM! CME
}
```
**Fix:** Use `Iterator.remove()` or removeIf (Java 8) or `CopyOnWriteArrayList`.

## 10. What’s the difference between fail-fast vs fail-safe iterators?

*   **Fail-Fast (ArrayList, HashMap):**
    *   Checks a `modCount` flag. If changed during iteration, throws CME immediately.
    *   Works on original collection.
*   **Fail-Safe (ConcurrentHashMap, CopyOnWriteArrayList):**
    *   Does NOT throw CME.
    *   Works on a clone or snapshot of data, or uses a sophisticated weakly consistent iterator (ConcurrentHashMap).
    *   You might not see the latest updates.

## 11. Time complexity of searching in HashMap “average” vs “worst case”?

*   **Average Case:** `O(1)`. Direct hash lookup.
*   **Worst Case:** `O(log n)` (Java 8+) or `O(n)` (Java 7).
    *   Happens if all keys have Hash Collision (bad hash function).
