# 8. File Structures & Indexing — Detailed GATE CSE Guide

> **GATE Weightage:** 3–5 marks. Questions involve computing B/B+ tree orders, heights, block access costs, and understanding index types (primary, secondary, dense, sparse).

---

## Why Do We Need File Structures and Indexing?

A database stores data on a **hard disk** (or SSD). The disk is MUCH slower than RAM — reading data from disk can be **100,000 times slower** than reading from memory.

The key insight: Disks read/write data in fixed-size chunks called **blocks** (typically 4KB-8KB). Even if you need just one byte, the disk reads an entire block. So the number of **block accesses** (how many times we read from disk) determines query performance.

**Goal of file organization and indexing:** Minimize the number of **block accesses** needed to find the data you want.

**Analogy:** Finding a word in a dictionary:
- **Without an index (heap file):** Read every page from the beginning → very slow
- **Sorted file (sequential):** Use binary search — jump to the middle, then narrow down → faster
- **With an index (like a book index):** Look up the word in the index, go directly to the page → fastest!

---

## Disk Basics — Understanding Blocks

### What is a Block?

A **block** (also called a **page**) is the smallest unit of data transfer between disk and memory. Think of it like a shipping container — you can't ship half a container.

- Typical block size: **512 bytes to 8 KB** (4096 bytes = 4KB is common)
- Every read/write operation transfers at least one full block

### Blocking Factor (bfr) — How Many Records Fit in One Block?

```
bfr = ⌊Block_Size / Record_Size⌋
```

We use **floor** (⌊⌋) because you can't fit a partial record in a block. The leftover space in the block is wasted.

**Example:**
- Block size = 4096 bytes
- Record size = 200 bytes
- bfr = ⌊4096 / 200⌋ = ⌊20.48⌋ = **20 records per block**
- Wasted space per block = 4096 - (20 × 200) = 4096 - 4000 = **96 bytes**

### Number of Blocks Needed

```
Number of blocks = ⌈N / bfr⌉
```

We use **ceiling** (⌈⌉) because even if the last block is partially filled, you still need that block.

**Example:**
- N = 100,000 records
- bfr = 20
- Blocks = ⌈100,000 / 20⌉ = **5,000 blocks**

> **⚠️ GATE Memory Aid:** Use **floor** for blocking factor (can't split records), **ceiling** for number of blocks (need extra block for leftovers).

---

## File Organizations

### 1. Heap (Unordered) File

Records are stored in **no particular order**. New records are inserted at the **end of the file**.

**Analogy:** A pile of papers on your desk — no sorting, just dumped on top.

| Operation | Cost (Block Accesses) | Explanation |
|---|---|---|
| **Search** (average) | **b/2** | Must scan blocks one by one; on average, find it halfway |
| **Search** (worst) | **b** | Must scan ALL blocks (item might be in the last block or absent) |
| **Insert** | **2** | Read last block (1), write updated block (1) — append to end |
| **Delete** | **b/2 + 1** | Search (b/2) + write updated block (1) |

Where b = total number of blocks.

**When to use:** When you frequently insert data and rarely search (e.g., logging systems).

---

### 2. Sequential (Sorted / Ordered) File

Records are sorted on a specific field called the **ordering key**.

**Analogy:** A dictionary — words are in alphabetical order.

| Operation | Cost on Ordering Key | Cost on Non-Ordering Key |
|---|---|---|
| **Search** | **⌈log₂(b)⌉** (binary search) | **b** (linear scan — sorting doesn't help) |
| **Insert** | **⌈log₂(b)⌉ + b/2** (find spot + shift records) | Same |
| **Delete** | **⌈log₂(b)⌉ + b/2** (find + shift) | Same |

**Why binary search works here:**
- The data is sorted, so you can jump to the middle block
- If your target is smaller → search the first half
- If your target is larger → search the second half
- Each step eliminates half the blocks → log₂(b) steps

**Example:**
- 5000 blocks → binary search = ⌈log₂(5000)⌉ = ⌈12.29⌉ = **13 block accesses**

Compare with heap file: 2500 average accesses. Sorted file is **~200x faster** for search!

---

### 3. Hash File

A **hash function** h(key) maps the search key to a **bucket number**. Each bucket is one or more blocks.

**Analogy:** A library where books are shelved by the first letter of the author's last name. Want books by "Smith"? Go directly to the "S" section.

| Operation | Cost (ideal) | Explanation |
|---|---|---|
| **Equality Search** | **1-2** block accesses | Compute hash → go to bucket → read |
| **Range Search** | **b** (entire file) | Hash destroys ordering → can't do range queries |
| **Insert** | **1-2** | Compute hash → write to bucket |

> **⚠️ GATE Key Point:** Hash indexes support ONLY **equality queries** (WHERE x = 5). They do NOT support range queries (WHERE x > 5 AND x < 10) because the hash function scatters related values across different buckets.

---

## Indexing — The Key to Fast Queries

### What is an Index?

An **index** is like the index at the back of a textbook — it tells you which page to go to for a specific topic. Instead of reading the entire book, you look up the topic in the index, get the page number, and go directly there.

A database index works the same way: it maps **key values** to the **block location** of the record. Instead of scanning the entire file, you search the (much smaller) index to find where the record is.

### Why is an Index Smaller Than the Data File?

An index entry contains only:
- The **key value** (a few bytes)
- A **pointer** to the data block (a few bytes)

Total index entry: typically 10-20 bytes vs. record size of 100-500 bytes. So the index file is **much smaller**, meaning faster searches.

---

## Types of Indexes

### Classification 1: By Relationship to File Organization

#### Primary Index

- Built on a **sorted file** using the **ordering key** (the field the file is sorted on)
- Has **one index entry per data block** (not per record!) — uses the first record of each block as an "anchor"
- This is a **sparse** index

```
Index:                          Data File (sorted by EmpID):
┌─────────┬──────────┐         ┌─────────────────────────────┐
│ Key     │ Block Ptr│         │ Block 1: [101, Amit] [105, Priya] │
│ 101     │ →Block 1 │────────>│          [108, Rahul]             │
│ 201     │ →Block 2 │         ├─────────────────────────────┤
│ 301     │ →Block 3 │────┐    │ Block 2: [201, Sneha] [205, Karan]│
└─────────┴──────────┘    │    │          [210, Meera]             │
                          │    ├─────────────────────────────┤
                          └───>│ Block 3: [301, Vijay] [305, Nita] │
                               │          [309, Dev]               │
                               └─────────────────────────────┘
```

**Key properties:**
- One entry per **block** (not per record) → sparse
- Number of index entries = number of data blocks
- Only works because the file is **sorted** on the index key

#### Clustering Index

- Built on a **sorted file** using a **non-key** field (field with duplicate values)
- One index entry per **distinct value** of the clustering field
- Also a **sparse** index

**Example:** Data sorted by DeptID (which has duplicates: CS, CS, CS, EC, EC, ME):
```
Index entry: CS → Block where CS records start
Index entry: EC → Block where EC records start
Index entry: ME → Block where ME records start
```

#### Secondary Index

- Built on a field that the file is **NOT sorted on**
- Can be on any file (sorted or unsorted), any field
- Has **one index entry per record** (dense) — because you can't predict where records are
- Records with the same field value could be **scattered across many blocks**

**Why dense (one entry per record)?** In a sparse index, you can use the sorted order to binary search between anchor points. But if the file isn't sorted on the index field, records are scattered randomly — you need a pointer to each individual record.

### Classification 2: Dense vs. Sparse

| | Dense Index | Sparse Index |
|---|---|---|
| **Entry count** | One per **record** | One per **block** |
| **Works on** | Any file (sorted or unsorted) | **Only sorted files** |
| **Space** | More (larger index) | Less (smaller index) |
| **Lookup speed** | Faster (direct to record) | Slightly slower (search within block) |
| **Example** | Secondary index | Primary index |

> **⚠️ GATE Trap:** A sparse index can ONLY be built on a **sorted file**. If the file is unsorted, you MUST use a dense index. This is because with a sparse index, you jump to the block and then scan within the block — this only works if the records are in order!

---

### Summary of Index Types

| Index Type | Built On | Sorted On | Sparse/Dense | Entries = |
|---|---|---|---|---|
| **Primary** | Sorted file | Ordering key | **Sparse** | Number of data blocks |
| **Clustering** | Sorted file | Ordering non-key | **Sparse** | Number of distinct values |
| **Secondary (key)** | Any file | Non-ordering key | **Dense** | Number of records |
| **Secondary (non-key)** | Any file | Non-ordering non-key | **Dense** | Number of records |

---

## Multi-Level Indexes — Indexing the Index

If the index itself is very large (takes many blocks), searching it with binary search still requires log₂(index_blocks) accesses. Can we do better?

**Solution:** Build an **index on the index**! The outer index is a sparse index on the inner index (which is sorted by key).

```
Level 2 (outer index):  [Very small — might fit in 1-2 blocks]
    ↓
Level 1 (inner index):  [Smaller than data file, sorted]
    ↓
Level 0 (data file):    [Large, sorted on key]
```

**Each level reduces the search by a factor of bfr_index** (blocking factor of the index).

```
Number of levels = ⌈log_{bfr_i}(entries_at_level_0)⌉
Total search cost = Number of levels + 1 (for data block)
```

This naturally leads to **B-Trees** and **B+ Trees** — balanced tree structures that implement multi-level indexing efficiently.

---

## B-Tree — The Balanced Multi-way Search Tree

### What is a B-Tree?

A B-tree is a **self-balancing** tree where:
- Each node corresponds to a **disk block**
- Internal nodes contain both **keys** and **data pointers** (pointers to actual records)
- All leaf nodes are at the **same depth** (perfectly balanced)
- Operations (search, insert, delete) are all O(log n)

### B-Tree of Order p

**"Order p"** means each node can have **at most p children** (and thus at most **p-1 keys**).

```
Internal Node Structure:
┌────┬────┬────┬────┬────┬────┬────┐
│ P₁ │ K₁ │ P₂ │ K₂ │ P₃ │ K₃ │ P₄ │   (order 4: max 3 keys, 4 children)
└────┴────┴────┴────┴────┴────┴────┘
  │         │         │         │
child    child     child     child
(< K₁)  (K₁-K₂)  (K₂-K₃)  (> K₃)
```

- Pᵢ = pointer to i-th child subtree
- Kᵢ = i-th key value
- Data pointers (to actual records) associated with each Kᵢ

### Properties

| Property | Value |
|---|---|
| Max keys per node | p - 1 |
| Max children per node | p |
| Min children (root, if not leaf) | 2 |
| Min children (non-root internal) | ⌈p/2⌉ |
| Min keys (non-root internal) | ⌈p/2⌉ - 1 |
| All leaves at same depth | Always |

---

## B+ Tree — The Industry Standard (GATE Favourite!)

### How is a B+ Tree Different from a B-Tree?

The B+ tree is the **most widely used** index structure in real databases (MySQL InnoDB, PostgreSQL, Oracle, etc.).

| Feature | B-Tree | B+ Tree |
|---|---|---|
| **Data pointers** | In ALL nodes (internal + leaf) | **Only in leaf nodes** |
| **Internal nodes** | Keys + data pointers + child pointers | **Keys + child pointers only** |
| **Key duplication** | No — each key appears exactly once | **Keys can be duplicated** (copy in internal nodes) |
| **Leaf nodes linked** | No | **Yes — linked list** |
| **Sequential access** | Requires tree traversal | **Efficient via leaf linked list** |
| **Fan-out** | Lower (nodes store data pointers → less space for children) | **Higher** (no data pointers in internal nodes → more children per node) |

**Why B+ Trees are better:**
1. **Higher fan-out** → shorter tree → fewer disk accesses
2. **All data at leaves** → predictable search cost (always traverse root to leaf)
3. **Linked leaves** → efficient range queries (just follow the linked list)

### B+ Tree Structure

**Internal Node (order p):**
```
┌────┬────┬────┬────┬────┬────┬────┐
│ P₁ │ K₁ │ P₂ │ K₂ │ P₃ │ K₃ │ P₄ │
└────┴────┴────┴────┴────┴────┴────┘
  │                            │
  children                   children
(All keys < K₁)           (All keys ≥ K₃)
```

**Leaf Node (order q):**
```
┌─────────┬─────────┬─────────┬──────┐
│ K₁ | D₁ │ K₂ | D₂ │ K₃ | D₃ │ Pnext│
└─────────┴─────────┴─────────┴──────┘
    │          │          │          │
    data       data       data    next leaf
    record     record     record  (linked list)
```

- Kᵢ = search key values
- Dᵢ = data pointers (to actual records on disk)
- Pnext = pointer to the **next leaf node** (for range queries)

### Computing Orders

**Internal node order p:**
A node must fit in one block. Each node contains (p-1) keys and p child pointers.

```
(p-1) × key_size + p × child_pointer_size ≤ block_size

Solving for p:
p × key_size - key_size + p × pointer_size ≤ block_size
p × (key_size + pointer_size) ≤ block_size + key_size
p = ⌊(block_size + key_size) / (key_size + pointer_size)⌋
```

**Leaf node order q:**
A leaf node contains (q-1) key-data pointer pairs plus one next-leaf pointer.

```
(q-1) × (key_size + data_pointer_size) + next_pointer_size ≤ block_size

Solving for q:
q-1 ≤ (block_size - next_pointer_size) / (key_size + data_pointer_size)
q = ⌊(block_size - next_pointer_size) / (key_size + data_pointer_size)⌋ + 1
```

### Worked Example: Computing Orders

**Given:** Block size = 4096 bytes, Key = 10 bytes, Data pointer = 8 bytes, Tree pointer = 6 bytes

**Internal order p:**
```
(p-1) × 10 + p × 6 ≤ 4096
10p - 10 + 6p ≤ 4096
16p ≤ 4106
p = ⌊4106/16⌋ = ⌊256.625⌋ = 256
```

**Leaf order q:**
```
(q-1) × (10 + 8) + 6 ≤ 4096
18(q-1) ≤ 4090
q-1 ≤ 227.2
q = 228
Max keys per leaf = q-1 = 227
```

---

### B+ Tree Height and Capacity

**Maximum number of records for a tree of height h:**

| Level | Max Nodes | Role |
|---|---|---|
| 0 (root) | 1 | Internal |
| 1 | p | Internal |
| 2 | p² | Internal |
| ... | ... | ... |
| h-1 (leaves) | p^(h-1) | Leaf |

```
Max records = p^(h-1) × (q-1)

Where:
  p = internal node order
  q = leaf node order
  h = height (root = level 0, or height counts from 1 — check context!)
```

**Example (continued):** p = 256, q = 228, height = 3 (root at height 1):
```
Max leaves = 256^(3-1) = 256² = 65,536 leaf nodes
Max records = 65,536 × 227 = 14,876,672 ≈ 15 million records!
```

With just 3 levels (3 disk accesses), a B+ tree can index **15 million records**!

### Search Cost

```
Search cost = h (traverse h levels) + 1 (read data block)
           = height + 1 block accesses
```

For our example: 3 + 1 = **4 block accesses** for 15 million records. Compare with:
- Heap file: 750,000/2 = 375,000 avg accesses!
- Binary search on sorted file: log₂(750,000) ≈ 20 accesses

B+ tree wins by a huge margin!

---

### B+ Tree Insertion — Key Mechanics

**Step 1:** Find the correct leaf node (traverse from root down).

**Step 2:** If the leaf has space → insert the key in sorted order. Done!

**Step 3:** If the leaf is **full** → **SPLIT**:
1. Create a new leaf node
2. Distribute keys: first ⌈q/2⌉ keys stay, rest go to new leaf
3. **COPY** the middle key up to the parent (key STAYS in the leaf too!)

**Step 4:** If the parent is full → **SPLIT the parent**:
1. Distribute keys and pointers
2. **PUSH** the middle key up to the grandparent (key MOVES OUT of the node!)

**Step 5:** If splitting propagates all the way to the root and the root is full → split the root and create a **new root**. Tree height increases by 1.

> **⚠️ GATE Critical Distinction:**
> - **Leaf split:** Middle key is **COPIED** up (stays in the leaf because data pointers are in leaves)
> - **Internal node split:** Middle key is **PUSHED** up (moves out of the node to the parent)
>
> This is a frequently tested point!

---

### B+ Tree Deletion — Key Mechanics

**Step 1:** Find and delete the key from the leaf.

**Step 2:** If the leaf still has enough keys (≥ ⌈(q-1)/2⌉) → Done!

**Step 3:** If the leaf has too few keys (**underflow**):
- Try to **borrow** (redistribute) a key from an adjacent sibling
  - If sibling has extra keys → borrow one → update parent key
- If borrowing fails → **merge** with sibling
  - Combine two nodes into one → remove an entry from the parent
  
**Step 4:** Propagate changes upward if the parent underflows.

---

## Hashing — Brief

### Static Hashing
- Fixed number of buckets
- Problem: as data grows, buckets overflow → long chains → poor performance

### Extendible Hashing (Dynamic)
- Uses a **directory** that doubles in size as needed
- **Global depth:** number of bits used by the directory
- **Local depth:** number of bits used by each bucket
- When a bucket overflows: split the bucket, possibly double the directory

### Linear Hashing
- Splits buckets in **round-robin order** (not necessarily the overflowing one)
- No directory needed
- Gradually expands the hash table

---

## Cost Comparison Summary

| Operation | Heap | Sorted | Primary Index | B+ Tree |
|---|---|---|---|---|
| **Equality Search** | b/2 | log₂(b) | log₂(b_i) + 1 | h + 1 |
| **Range Search** | b | log₂(b) + range | log₂(b_i) + range | h + range |
| **Insert** | 2 | log₂(b) + b/2 | log₂(b_i) + 1 (+ split) | h + 1 (+ split) |
| **Delete** | b/2 + 1 | log₂(b) + b/2 | log₂(b_i) + 1 | h + 1 (+ merge) |

Where b = data blocks, b_i = index blocks, h = B+ tree height.

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| "Sparse index works on unsorted files" | ❌ Sparse requires sorted file |
| "B-tree = B+ tree" | ❌ B+ tree has data only in leaves + leaf linking |
| "Leaf split PUSHES key up" | ❌ Leaf split COPIES, internal split PUSHES |
| "Primary index has one entry per record" | ❌ Primary index is sparse: one entry per BLOCK |
| "Hash index supports range queries" | ❌ Hash supports ONLY equality queries |
| "More index levels = slower" | ❌ Each level = 1 disk read; B+ trees are very shallow |
| "Secondary index is fast for range queries on non-key" | ❌ Records are scattered — each record might be in a different block |

---

## Quick-Fire GATE Formulas

```
Blocking factor:       bfr = ⌊B/R⌋   (floor)
Data blocks:          b = ⌈N/bfr⌉   (ceiling)

Primary index entries: = b (one per block, sparse)
Secondary index entries: = N (one per record, dense)

B+ Tree Internal order p:
  (p-1)×K + p×P ≤ B  →  p = ⌊(B+K)/(K+P)⌋

B+ Tree Leaf order q:
  (q-1)×(K+D) + P ≤ B  →  q = ⌊(B-P)/(K+D)⌋ + 1

Max records: p^(h-1) × (q-1)
Search cost: h + 1
```

---

*← [07 — Transactions & Concurrency](07_Transactions_and_Concurrency.md) | [09 — GATE Practice Set →](09_GATE_Practice_Set.md)*
