# 8. File Structures & Indexing — GATE CSE Complete Guide

> **GATE Weightage:** 3–5 marks. Questions test B/B+ tree operations (insertion, deletion, height, number of nodes), index computation (primary, secondary, dense, sparse), hashing, and I/O cost calculations.

---

## File Structures Overview

File organization determines how records are physically stored on disk. The choice of file structure affects **search time, insertion time, deletion time, and space utilization**.

---

## Key Definitions & Concepts

### Disk Basics

| Term | Definition |
|---|---|
| **Block (Page)** | The unit of data transfer between disk and memory. Typical size: 512B — 8KB |
| **Block Factor (bfr)** | Number of records that fit in one block = ⌊Block_Size / Record_Size⌋ |
| **Blocking Factor** | Same as block factor |
| **Number of Blocks** | Total blocks needed = ⌈Total_Records / bfr⌉ |

```
bfr = ⌊B / R⌋
Number of blocks = ⌈N / bfr⌉

where:
  B = Block size (bytes)
  R = Record size (bytes)
  N = Total number of records
```

> **⚠️ GATE Point:** Use **floor** for blocking factor (can't fit partial records), **ceiling** for number of blocks (need an extra block for remaining records).

---

## File Organizations

### 1. Heap (Unordered) File

- Records inserted at the **end of the file** (no ordering).
- **Search:** Linear scan → O(N/bfr) = O(b) block accesses (b = number of blocks)
  - Average case: **b/2** block accesses
  - Worst case: **b** block accesses
- **Insert:** O(1) — append to end
- **Delete:** Search + delete → O(b) (may leave holes → need periodic reorganization)

### 2. Sequential (Ordered / Sorted) File

- Records sorted on a **search key** (ordering field).
- **Search (on ordering key):** Binary search → O(log₂ b) block accesses
- **Search (on non-ordering key):** Linear scan → O(b)
- **Insert:** Expensive — need to maintain order → O(b) (shift records)
- **Delete:** Search + delete → O(log₂ b) + reorganization

### 3. Hash File

- A **hash function** h(K) maps the search key K to a **bucket address**.
- Each bucket = one or more blocks.
- **Search:** O(1) — compute hash, go to bucket (ideal case)
- **Insert:** O(1) — compute hash, insert in bucket
- **Overflow handling:** Chaining or linear probing

---

## Indexing

An **index** is a data structure that speeds up retrieval of records based on specific fields.

### Index Classification

| Criteria | Types |
|---|---|
| **On ordering** | Primary Index, Clustering Index, Secondary Index |
| **On density** | Dense Index, Sparse Index |
| **On levels** | Single-level, Multi-level (B-tree, B+ tree) |

---

### Primary Index

- Built on a **sorted file** using the **primary key** (ordering key).
- **One index entry per block** (not per record) — uses the **first record** of each block as the anchor.
- **Sparse index** (one entry per block).
- Number of index entries = **number of data blocks** = ⌈N/bfr⌉

```
Index entries = ⌈N / bfr_data⌉
Index blocks  = ⌈Index_entries / bfr_index⌉

Search cost = log₂(Index_blocks) + 1
              (binary search on index + 1 block access to data)
```

---

### Clustering Index

- Built on a **sorted file** using a **non-key ordering field** (field with duplicate values).
- One index entry per **distinct value** of the clustering field.
- **Sparse index**.

```
Index entries = Number of distinct values of the clustering field
```

---

### Secondary Index

- Built on a **non-ordering field** (file may or may not be sorted, but NOT on this field).
- **Dense index** — one index entry **per record** (or per distinct value with pointer list).
- Can be on a **key** (unique values) or **non-key** (duplicates).

```
Secondary Index (on key):
  Index entries = N (one per record)
  Index blocks = ⌈N / bfr_index⌉
  Search cost = log₂(Index_blocks) + 1

Secondary Index (on non-key):
  Dense: one entry per record → N entries
  Or: one entry per distinct value → extra level of indirection
```

> **⚠️ GATE Key Comparisons:**

| Index Type | On Which File | On Which Field | Sparse/Dense | One Entry Per |
|---|---|---|---|---|
| **Primary** | Sorted | Ordering key | **Sparse** | Block |
| **Clustering** | Sorted | Ordering non-key | **Sparse** | Distinct value |
| **Secondary (key)** | Any | Non-ordering key | **Dense** | Record |
| **Secondary (non-key)** | Any | Non-ordering non-key | **Dense** | Record or distinct value |

---

### Dense vs. Sparse Index

| Dense | Sparse |
|---|---|
| One entry for **each record** | One entry for **each block** |
| Works on **sorted or unsorted** files | Works **only on sorted** files |
| More space, faster lookup | Less space, slower lookup |
| Secondary indexes are always dense | Primary indexes are sparse |

> **⚠️ GATE Trap:** A sparse index can **only** be built on a **sorted file** (ordered on the index field). Dense indexes work on any file.

---

### Multi-Level Index

When the index itself is large, we create an **index on the index**.

```
Level 1 (outer index): Sparse index on Level 0
Level 2: Sparse index on Level 1
...
Until the top level fits in 1 block.

Number of levels = ⌈log_{bfr_index}(Index_entries_level_0)⌉
Search cost = Number of levels + 1 (data block access)
```

This leads us to **B-trees** and **B+ trees** — balanced multi-level indexes.

---

## B-Tree

A **balanced** multi-way search tree where:
- Each node is a disk block.
- Each node has **at most p pointers** and **p-1 keys** (p = order of the tree).
- Internal nodes contain both **keys and data pointers**.

### Properties of B-Tree of Order p

| Property | Value |
|---|---|
| Max keys per node | p − 1 |
| Max children per node | p |
| Min children (root, if not leaf) | 2 |
| Min children (internal, non-root) | ⌈p/2⌉ |
| Min keys (internal, non-root) | ⌈p/2⌉ − 1 |
| All leaves at same level | **Yes** (balanced) |

### Computing Order p

```
Node size = Block size
Each node contains:
  (p-1) keys × key_size +
  p × pointer_size +
  (p-1) × data_pointer_size ≤ Block_size

Solve for maximum p.
```

### B-Tree Height & Record Count

For a B-Tree of order p and height h (root at level 0):

```
Max records = p^h − 1
            (each node has up to p-1 keys)

Min records (with minimum fill):
  Level 0 (root): at least 1 key → 2 children
  Level 1: at least 2 × ⌈p/2⌉ − 1 keys
  ...

Max keys at level i = p^i × (p-1)
```

---

## B+ Tree (GATE Favourite)

The most widely used index structure in commercial DBMS.

### Differences from B-Tree

| Feature | B-Tree | B+ Tree |
|---|---|---|
| Data pointers | In **all** nodes | Only in **leaf** nodes |
| Key duplication | No key duplication | Keys may be **duplicated** in internal nodes |
| Leaf nodes linked | No | **Yes** (linked list for range queries) |
| Internal nodes | Keys + data pointers + child pointers | Keys + child pointers only |
| Sequential access | Requires inorder traversal | Efficient via leaf-level linked list |

### B+ Tree of Order p (Internal Node Order)

**Internal Node:**
```
Contains: (p-1) keys and p child pointers
Structure: [P₁ | K₁ | P₂ | K₂ | ... | K_{p-1} | P_p]
```

**Leaf Node (order q):**
```
Contains: (q-1) keys, (q-1) data pointers, 1 next-leaf pointer
Structure: [K₁|D₁ | K₂|D₂ | ... | K_{q-1}|D_{q-1} | P_next]
```

### Computing Orders

**Internal node order p:**
```
(p-1) × key_size + p × tree_pointer_size ≤ Block_size
p × (key_size + tree_pointer_size) ≤ Block_size + key_size
p = ⌊(Block_size + key_size) / (key_size + tree_pointer_size)⌋
```

**Leaf node order q:**
```
(q-1) × (key_size + data_pointer_size) + tree_pointer_size ≤ Block_size
q = ⌊(Block_size - tree_pointer_size) / (key_size + data_pointer_size)⌋ + 1
```

### B+ Tree Properties

| Property | Value |
|---|---|
| Max keys per internal node | p − 1 |
| Min keys per internal node (non-root) | ⌈p/2⌉ − 1 |
| Max children per internal node | p |
| Min children per internal node (non-root) | ⌈p/2⌉ |
| Root (if not leaf) | Min 2 children, min 1 key |
| Max keys per leaf | q − 1 |
| Min keys per leaf | ⌈(q−1)/2⌉ |
| All leaves at same depth | **Yes** |

### Height Calculations

**Maximum records in B+ Tree of height h and order p (internal), q (leaf):**

```
Max leaf nodes = p^(h-1)  (if root is at height h)
Max records = p^(h-1) × (q-1)
```

**Or equivalently with root at level 0:**
```
With height = h levels (0 to h-1):
  Leaf level = h-1
  Max leaf nodes = p^(h-1)
  Max records = p^(h-1) × (q-1)
```

**Minimum height for N records:**
```
h ≥ ⌈log_p(N/(q-1))⌉ + 1
```
(But typically just compute level by level.)

**Search cost:** h block accesses (1 per level) + 1 (data block) = h + 1

> **⚠️ GATE Note:** Some textbooks count height from 1 (root = height 1). Others from 0. Read the question carefully!

### B+ Tree Insertion

```
1. Find the appropriate leaf node.
2. If the leaf has space → insert key in order.
3. If the leaf is full → SPLIT:
   a. Create a new leaf node.
   b. Distribute keys: first ⌈(q-1+1)/2⌉ = ⌈q/2⌉ keys stay, rest go to new node.
   c. COPY the middle key up to the parent.
4. If the parent is full → SPLIT the parent:
   a. Distribute keys and pointers.
   b. PUSH the middle key up (not copy — for internal nodes, key moves up).
5. If splitting propagates to root → create new root (height increases by 1).
```

> **⚠️ GATE Critical Distinction:**
> - **Leaf split:** COPY middle key to parent (key remains in leaf).
> - **Internal node split:** PUSH middle key to parent (key moves out of the node).

### B+ Tree Deletion

```
1. Find and delete the key from the leaf.
2. If the leaf has at least ⌈(q-1)/2⌉ keys → done.
3. If underflow (too few keys):
   a. Try to BORROW from adjacent sibling (redistribute).
   b. If borrowing fails → MERGE with sibling (combine two nodes, remove an entry from parent).
4. Propagate changes upward if parent underflows.
```

---

## Hashing

### Static Hashing
- Fixed number of buckets.
- Hash function: h(K) → bucket number (0 to M-1).
- **Problem:** As data grows, overflow chains become long → poor performance.

### Dynamic Hashing (Extendible Hashing)
- Hash table grows/shrinks dynamically.
- Uses a **directory** of pointers to buckets.
- **Global depth** and **local depth** control when to split/double.

```
If bucket overflows and local depth < global depth:
    Split the bucket, increment local depth
If bucket overflows and local depth = global depth:
    Double the directory, then split the bucket
```

### Linear Hashing
- Buckets split in a **linear, round-robin** order (not just the overflowing bucket).
- No directory needed.

---

## Mathematical Foundations

### Cost Calculations (Summary)

| Operation | Heap File | Sorted File | Primary Index | B+ Tree |
|---|---|---|---|---|
| **Search (equality)** | b/2 avg, b worst | log₂(b) | log₂(bᵢ) + 1 | h + 1 |
| **Search (range)** | b | log₂(b) + range | log₂(bᵢ) + range | h + range |
| **Insert** | 1 (+ 1 for read) | log₂(b) + b/2 | log₂(bᵢ) + 1 (+ split) | h + 1 (+ split) |
| **Delete** | b/2 + 1 | log₂(b) + b/2 | log₂(bᵢ) + 1 | h + 1 (+ merge) |

Where:
- b = number of data blocks
- bᵢ = number of index blocks
- h = height of B+ tree

### Fan-out
```
Fan-out = p = order of the tree
         = average number of children per internal node

Higher fan-out → shorter tree → fewer disk accesses → better performance
```

---

## GATE Specific Focus Points

### 1. Computing Maximum Records for Given B+ Tree Height

**Example:** B+ tree with p=200 (internal), q=100 (leaf), height=3.

```
Level 0 (root): 1 node
Level 1: up to 200 nodes (max children of root)
Level 2 (leaves): up to 200 × 200 = 40,000 leaf nodes

Max records = 40,000 × (100-1) = 40,000 × 99 = 3,960,000
```

### 2. Minimum Nodes at Each Level

Using minimum fill factors:

```
Level 0 (root): 1 node, at least 2 children
Level 1: at least 2 nodes, each with at least ⌈p/2⌉ children
Level 2: at least 2 × ⌈p/2⌉ nodes
...
Level i: at least 2 × ⌈p/2⌉^(i-1) nodes (for i ≥ 1)
```

### 3. Block Accesses After Index

After finding a record through an index, you still need **1 more block access** to read the actual data block (unless the index is clustered and you're already in the right block).

### 4. Secondary Index with Duplicates

When a secondary index is on a non-key field:
- Dense index: one entry per record → might need to access **many different data blocks** (records with the same key value may be scattered).
- In the worst case: cost = number of matching records (each in a different block).

> **⚠️ GATE Trap:** Secondary index on non-key field doesn't benefit from sequential access — records are scattered across blocks!

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| "Sparse index works on unsorted files" | **No.** Sparse index requires a **sorted** file |
| "B-tree and B+ tree are the same" | **No.** B+ tree stores data pointers only in leaves, has leaf linking |
| "B+ tree leaf split PUSHES key up" | **No.** Leaf split **COPIES** key to parent. Internal split PUSHES |
| "Primary index has one entry per record" | **No.** Primary index has one entry per **block** (sparse) |
| "Height of B+ tree = number of levels" | Depends on counting convention. Check if height starts from 0 or 1 |
| "Binary search on index = log₂(N)" | Binary search on **index blocks**, not records: log₂(⌈N/bfr⌉) |
| "More levels of index = worse performance" | With B+ tree, each level = one disk access. Few levels even for billions of records |
| "Hash index supports range queries" | **No.** Hash index supports only **equality** searches |

---

## 3 Worked Examples

### Example 1: Block and Index Calculation (Easy)

**Q:** A file has 100,000 records. Record size = 200 bytes. Block size = 4096 bytes. Key size = 20 bytes. Block pointer = 10 bytes.

Calculate:
(a) Blocking factor
(b) Number of data blocks
(c) Number of primary index entries and index blocks
(d) Binary search cost on data file vs. primary index

**Solution:**

(a) bfr = ⌊4096 / 200⌋ = **20 records/block**

(b) Data blocks = ⌈100,000 / 20⌉ = **5,000 blocks**

(c) Primary index:
- Index entries = 5,000 (one per block)
- Index entry size = key + block pointer = 20 + 10 = 30 bytes
- bfr_index = ⌊4096 / 30⌋ = 136 entries/block
- Index blocks = ⌈5,000 / 136⌉ = **37 blocks**

(d) Search costs:
- Binary search on data file: ⌈log₂(5000)⌉ = **13 block accesses**
- Binary search on primary index: ⌈log₂(37)⌉ + 1 = 6 + 1 = **7 block accesses**

---

### Example 2: B+ Tree Order and Height (Medium)

**Q:** Block size = 512 bytes. Key size = 10 bytes. Data pointer = 8 bytes. Block pointer = 6 bytes. Total records = 1,000,000.

Find: (a) Order of internal node (p), (b) Order of leaf node (q), (c) Height needed.

**Solution:**

(a) Internal node: (p-1) × 10 + p × 6 ≤ 512
```
10p - 10 + 6p ≤ 512
16p ≤ 522
p = ⌊522/16⌋ = 32
```
**p = 32**

(b) Leaf node: (q-1) × (10 + 8) + 6 ≤ 512
```
18(q-1) + 6 ≤ 512
18(q-1) ≤ 506
q-1 ≤ 28.1
q-1 = 28, so q = 29
```
**q = 29** (max 28 keys per leaf)

(c) Height for 1,000,000 records:
- Max records per leaf = q - 1 = 28
- Need at least ⌈1,000,000 / 28⌉ = 35,715 leaf nodes
- Level 0: 1 root, max 32 children
- Level 1: max 32 nodes → 32 × 32 = 1,024 children
- Level 2: max 1,024 nodes → 1,024 × 32 = 32,768 children
- Level 3 (leaves): need 35,715 > 32,768... need one more level
- Actually: 32³ = 32,768 < 35,715 → need height 4 (levels 0-3)
- Check: 32² × 32 = 32,768 leaves at level 3... not enough.
- Height = 4: 32³ = 32,768 at level 3 → 32⁴/32 = 32,768 leaves, still < 35,715
- Actually root doesn't contribute to leaves alone.

Let me recalculate:
- height h (root = level 1, leaves = level h)
- Max leaves at height h = p^(h-1)
- p^(h-1) ≥ ⌈N/(q-1)⌉ = 35,715
- 32^2 = 1,024 < 35,715
- 32^3 = 32,768 < 35,715
- 32^4 = 1,048,576 > 35,715

**Height = 5** (or 4 if counting from 0)

Search cost = 5 + 1 = **6 block accesses** (for 1 million records!)

---

### Example 3: Secondary Index Cost (GATE Level)

**Q:** A file has 10,000 records sorted on field A. Block size = 1024 bytes. Record size = 100 bytes. A secondary index is built on field B (non-key, 50 distinct values). Key size = 10 bytes. Pointer = 6 bytes.

How many block accesses to find all records with B = 'x'?

**Solution:**

- bfr = ⌊1024/100⌋ = 10 records/block
- Data blocks = ⌈10,000/10⌉ = 1,000 blocks
- Records with B = 'x' ≈ 10,000/50 = 200 records (on average)
- Secondary index is on non-ordering field → records with same B value are **scattered**.
- In the **worst case**, each record is in a different block → **200 block accesses** for data.

Index search:
- Dense secondary index: 10,000 entries
- Index entry size = 10 + 6 = 16 bytes
- bfr_index = ⌊1024/16⌋ = 64
- Index blocks = ⌈10,000/64⌉ = 157
- Binary search on index: ⌈log₂(157)⌉ = 8

**Total cost = 8 + 200 = 208 block accesses**

> With a primary/clustering index on B, records would be contiguous, costing only 8 + ⌈200/10⌉ = 8 + 20 = 28 block accesses. This shows why clustering matters!

---

## Revision Table

| Concept | Key Property |
|---|---|
| **Heap File** | Unordered, O(b) search, O(1) insert |
| **Sorted File** | O(log₂ b) search on sort key |
| **Primary Index** | Sparse, on ordering key, 1 entry per block |
| **Clustering Index** | Sparse, on ordering non-key |
| **Secondary Index** | Dense, on non-ordering field |
| **Sparse Index** | Only on sorted files, 1 entry per block |
| **Dense Index** | On any file, 1 entry per record |
| **B-Tree** | Data pointers in all nodes |
| **B+ Tree** | Data only in leaves, leaves linked, keys duplicated |
| **Leaf split** | COPY key to parent |
| **Internal split** | PUSH key to parent |
| **Min children (non-root)** | ⌈p/2⌉ |
| **Min keys (non-root)** | ⌈p/2⌉ − 1 |
| **Static Hashing** | Fixed buckets, overflow chains |
| **Extendible Hashing** | Directory doubles when needed |
| **Hash Index** | Equality only, NO range queries |

---

## Quick-Fire GATE Formulas

```
Blocking factor:     bfr = ⌊B/R⌋
Data blocks:         b = ⌈N/bfr⌉
Primary index entries: = b (one per block)
Secondary index entries: = N (one per record, dense)

B+ Tree:
  Internal order p: (p-1)×K + p×P ≤ B
  Leaf order q:     (q-1)×(K+D) + P ≤ B
  Max records:      p^(h-1) × (q-1)
  Search cost:      h + 1 (levels + data block)

Heap search:     b/2 (avg), b (worst)
Sorted search:   log₂(b)
Index search:    log₂(index_blocks) + 1
B+ tree search:  h + 1

bfr = floor   (can't fit partial records)
blocks = ceil  (need extra block for remaining)
```

---

*← [07 — Transactions & Concurrency](07_Transactions_and_Concurrency.md) | [09 — GATE Practice Set →](09_GATE_Practice_Set.md)*
