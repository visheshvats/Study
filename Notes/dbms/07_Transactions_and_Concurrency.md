# 7. Transaction Management & Concurrency Control — GATE CSE Complete Guide

> **GATE Weightage:** 4–6 marks (one of the **highest-weighted** DBMS topics). Questions test ACID properties, schedule serializability (conflict & view), recoverability, 2PL, timestamp ordering, deadlock detection.

---

## Transaction Management Overview

A **transaction** is a logical unit of work that accesses and possibly modifies the contents of a database. It is a sequence of **read** and **write** operations on data items that must either execute **completely** or **not at all**.

**Notation:**
- `R(X)` — Read item X
- `W(X)` — Write item X

---

## Key Definitions & Concepts

### ACID Properties

| Property | Definition | Ensured By |
|---|---|---|
| **Atomicity** | Transaction executes **completely or not at all** ("all or nothing") | Recovery system (undo/redo logs) |
| **Consistency** | Transaction brings DB from one **valid state** to another | Application logic + integrity constraints |
| **Isolation** | Concurrent transactions execute as if they were **serial** (no interference) | Concurrency control (2PL, timestamps) |
| **Durability** | Once committed, changes **persist** even after system failure | Write-Ahead Logging (WAL), checkpointing |

---

### Transaction States

```
                  ┌──────────┐
        ┌────────>│  Active   │
        │         └────┬─────┘
        │              │ (read/write)
        │              v
        │         ┌──────────────┐
        │         │ Partially    │
        │         │ Committed    │
        │         └──┬───────┬──┘
        │            │       │
        │   (success)│       │(failure)
        │            v       v
        │    ┌──────────┐  ┌────────┐
        │    │ Committed │  │ Failed │
        │    └──────────┘  └───┬────┘
        │                      │
        │                      v
        │              ┌──────────┐
        └──────────────│ Aborted  │
                       └──────────┘
```

| State | Description |
|---|---|
| **Active** | Transaction is executing |
| **Partially Committed** | Final statement executed, awaiting commit |
| **Committed** | Changes permanently written (durable) |
| **Failed** | Error detected, cannot proceed |
| **Aborted** | Transaction rolled back, DB restored to prior state |

---

## Schedules

A **schedule** is a chronological ordering of operations from multiple concurrent transactions.

### Serial Schedule
- Transactions execute **one after another** with **no interleaving**.
- Always **correct** (consistent).
- Performance is poor (no concurrency).

### Concurrent (Non-Serial) Schedule
- Operations from different transactions are **interleaved**.
- May or may not be correct — needs to be checked for **serializability**.

---

## Serializability

A concurrent schedule is **serializable** if it is **equivalent** to some serial schedule.

### Conflict Serializability

#### Conflicting Operations
Two operations **conflict** if ALL three conditions are true:
1. They belong to **different transactions**.
2. They operate on the **same data item**.
3. **At least one is a Write** operation.

| Pair | Conflict? | Reason |
|---|---|---|
| R₁(X), R₂(X) | **No** | Both are reads — no conflict |
| R₁(X), W₂(X) | **Yes** | Read-Write conflict |
| W₁(X), R₂(X) | **Yes** | Write-Read conflict |
| W₁(X), W₂(X) | **Yes** | Write-Write conflict |

> **⚠️ GATE Mnemonic:** RR = No conflict. All others (RW, WR, WW) = Conflict.

#### Conflict Equivalence
Two schedules are **conflict equivalent** if one can be obtained from the other by **swapping non-conflicting adjacent operations**.

#### Conflict Serializable
A schedule is **conflict serializable** if it is conflict equivalent to **some serial schedule**.

### Testing Conflict Serializability — Precedence Graph (Serialization Graph)

**Algorithm:**
```
1. Create a node for each transaction.
2. For each pair of conflicting operations:
   - If Ti performs the operation BEFORE Tj:
     - Add edge Ti → Tj
3. If the graph has a CYCLE → NOT conflict serializable.
4. If the graph is ACYCLIC → Conflict serializable.
5. Any topological sort of the graph gives an equivalent serial order.
```

**Example:**
```
Schedule S: R1(A) R2(A) W1(A) W2(A) R1(B) R2(B) W1(B) W2(B)

Conflicts:
  R1(A) before W2(A) → T1 → T2
  R2(A) before W1(A) → T2 → T1
  (or check: W1(A) before W2(A) → T1 → T2, etc.)

T1 → T2 and T2 → T1  → CYCLE!
→ NOT conflict serializable.
```

---

### View Serializability

A weaker notion than conflict serializability.

Two schedules S and S' are **view equivalent** if:
1. **Initial Read:** If Tᵢ reads the initial value of X in S, then Tᵢ reads the initial value of X in S'.
2. **Updated Read:** If Tᵢ reads the value of X written by Tⱼ in S, then Tᵢ reads the value written by Tⱼ in S'.
3. **Final Write:** If Tᵢ performs the final write of X in S, then Tᵢ performs the final write of X in S'.

**Key Relationships:**
```
Conflict Serializable ⊂ View Serializable ⊂ All Schedules

Every conflict serializable schedule → also view serializable.
NOT every view serializable schedule → conflict serializable.
```

> **⚠️ GATE Trap:** A **blind write** (a write without a preceding read on the same item) can make a schedule view serializable but NOT conflict serializable.

> **GATE Fact:** Testing view serializability is **NP-complete**. Testing conflict serializability is **polynomial** (precedence graph).

---

## Recoverability of Schedules

### Irrecoverable Schedule
- Tⱼ reads data written by Tᵢ, and Tⱼ **commits before** Tᵢ.
- If Tᵢ later aborts, Tⱼ has used invalid data but already committed → **cannot undo Tⱼ** → irrecoverable.
- **Must be avoided!**

### Recoverable Schedule
- If Tⱼ reads data from Tᵢ, then Tᵢ must **commit before** Tⱼ commits.
- Ensures that if Tᵢ aborts, Tⱼ can be rolled back too.

### Cascadeless (Avoid Cascading Rollback) Schedule
- Tⱼ reads data written by Tᵢ **only after** Tᵢ has **committed**.
- No cascading rollbacks needed.

### Strict Schedule
- Tⱼ neither **reads nor writes** a data item written by Tᵢ **until** Tᵢ has committed or aborted.
- Simplifies recovery.

**Hierarchy:**
```
Strict ⊂ Cascadeless ⊂ Recoverable ⊂ All Schedules

Serial ⊂ Strict ⊂ Cascadeless ⊂ Recoverable
```

> **⚠️ GATE Key Relationships:**
> - Every strict schedule is cascadeless.
> - Every cascadeless schedule is recoverable.
> - An irrecoverable schedule is never acceptable.
> - Serializability and recoverability are **independent** properties — a schedule can be serializable but irrecoverable, or recoverable but not serializable.

---

## Concurrency Control Protocols

### 1. Lock-Based Protocols

#### Types of Locks
| Lock | Symbol | Allows |
|---|---|---|
| **Shared Lock (S-lock / Read lock)** | S | Multiple transactions can read simultaneously |
| **Exclusive Lock (X-lock / Write lock)** | X | Only one transaction can hold; no other locks allowed |

#### Lock Compatibility Matrix

| | S | X |
|---|---|---|
| **S** | ✅ Compatible | ❌ Conflict |
| **X** | ❌ Conflict | ❌ Conflict |

#### Lock Upgrade & Downgrade
- **Upgrade:** S-lock → X-lock (need exclusive access for writing)
- **Downgrade:** X-lock → S-lock (done writing, only reading now)

---

### 2. Two-Phase Locking (2PL)

**Definition:** A transaction follows 2PL if all **lock acquisitions** (growing phase) occur before all **lock releases** (shrinking phase).

```
Growing Phase:  Transaction acquires locks (no releases)
Lock Point:     Maximum number of locks held (turning point)
Shrinking Phase: Transaction releases locks (no new acquisitions)
```

**Properties:**
| Property | 2PL | Strict 2PL | Rigorous 2PL |
|---|---|---|---|
| **Ensures Conflict Serializability** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Prevents Deadlock** | ❌ No | ❌ No | ❌ No |
| **Cascadeless** | ❌ No | ✅ Yes | ✅ Yes |
| **Lock Release Rule** | After lock point | All **exclusive** locks held until commit/abort | **ALL** locks held until commit/abort |

**Variants:**

| Variant | Rule |
|---|---|
| **Basic 2PL** | Growing + shrinking phases. May NOT be recoverable |
| **Strict 2PL** | All **X-locks** released only at commit/abort. Cascadeless ✅ |
| **Rigorous 2PL** | **ALL locks** (S and X) released only at commit/abort. Strict ✅ |
| **Conservative 2PL** | All locks acquired **before** transaction starts. Deadlock-free ✅ |

> **⚠️ GATE Critical:**
> - 2PL guarantees **conflict serializability**.
> - 2PL does **NOT** prevent deadlocks (except conservative 2PL).
> - The serial order of a 2PL schedule is determined by **lock point order**.

---

### 3. Timestamp-Based Protocol

Each transaction Tᵢ gets a unique **timestamp TS(Tᵢ)** (usually the time it started).

**Rules for data item X:**
- **W_TS(X):** Timestamp of the last transaction that wrote X.
- **R_TS(X):** Timestamp of the last transaction that read X.

#### Read Operation R(Tᵢ, X):
```
If TS(Tᵢ) < W_TS(X):
    Tᵢ is trying to read a value already overwritten → ABORT Tᵢ
Else:
    Allow read, set R_TS(X) = max(R_TS(X), TS(Tᵢ))
```

#### Write Operation W(Tᵢ, X):
```
If TS(Tᵢ) < R_TS(X):
    A younger transaction already read the old value → ABORT Tᵢ
If TS(Tᵢ) < W_TS(X):
    A younger transaction already wrote X → ABORT Tᵢ
    (Thomas Write Rule: Skip the write instead of aborting)
Else:
    Allow write, set W_TS(X) = TS(Tᵢ)
```

**Properties:**
- Ensures **conflict serializability** (equivalent to serial order of timestamps).
- **Deadlock-free** (no locks, no waiting — either execute or abort).
- **NOT cascadeless** (basic version). May cause **starvation** (repeated aborts).

#### Thomas Write Rule
- If TS(Tᵢ) < W_TS(X) during a write: **skip the write** (don't abort).
- Reasoning: The write is **obsolete** — a newer transaction already wrote X.
- This makes the protocol more efficient.
- Results in **view serializable** (but not necessarily conflict serializable) schedules.

---

### 4. Validation-Based Protocol (Optimistic)

Three phases:
1. **Read Phase:** Transaction reads from DB, writes to private workspace.
2. **Validation Phase:** Check for conflicts with concurrent transactions.
3. **Write Phase:** If validation succeeds, apply changes to DB.

- Works well when conflicts are **rare** (optimistic assumption).
- Used in low-contention environments.

---

## Deadlock Handling

### Deadlock
- Two or more transactions are **waiting for each other** to release locks → none can proceed.

### Detection — Wait-For Graph
```
1. Create a node for each active transaction.
2. Add edge Tᵢ → Tⱼ if Tᵢ is waiting for a lock held by Tⱼ.
3. If the graph has a CYCLE → Deadlock exists.
4. Choose a victim transaction and abort it.
```

### Prevention

| Scheme | Rule | Who Dies? |
|---|---|---|
| **Wait-Die** | Older waits, younger dies (aborts) | **Younger** transaction is aborted |
| **Wound-Wait** | Older wounds (forces abort of) younger, younger waits | **Younger** transaction is aborted |

**Mnemonics:**
- **Wait-Die:** Old waits, Young dies.
- **Wound-Wait:** Old wounds, Young waits.

> **⚠️ GATE Trap:** In both schemes, the **younger** transaction is always the one that gets aborted. The difference is in **who initiates** the action.

| Scheme | Old requests lock held by Young | Young requests lock held by Old |
|---|---|---|
| **Wait-Die** | Old **waits** | Young **dies** (aborts) |
| **Wound-Wait** | Old **wounds** young (young aborted) | Young **waits** |

---

## Mathematical Foundations

### Number of Possible Schedules

For `n` transactions with `k₁, k₂, ..., kₙ` operations respectively:
```
Total possible schedules = (k₁ + k₂ + ... + kₙ)! / (k₁! × k₂! × ... × kₙ!)
```
(Multinomial coefficient — number of ways to interleave while preserving order within each transaction.)

### Number of Serial Schedules
```
n! (number of permutations of n transactions)
```

### Precedence Graph — Number of Edges
- For each data item X accessed by transactions Tᵢ and Tⱼ:
  - Check for conflicts: RW, WR, WW
  - Each conflict adds one directed edge (if not already present)

---

## GATE Specific Focus Points

### 1. Quick Serializability Check

**Step-by-step for any schedule:**
1. List all pairs of conflicting operations.
2. For each conflict, note which transaction comes first → add edge.
3. Check precedence graph for cycle.
4. No cycle → conflict serializable. The topological sort gives the equivalent serial order.

### 2. Schedule Properties Table

For a given schedule, determine ALL of these:
| Property | Check Method |
|---|---|
| **Conflict Serializable** | Precedence graph is acyclic |
| **View Serializable** | Check 3 conditions (initial reads, updated reads, final writes) |
| **Recoverable** | No Tⱼ commits before Tᵢ if Tⱼ read from Tᵢ |
| **Cascadeless** | Transaction reads only committed data |
| **Strict** | No transaction reads/writes data of uncommitting transaction |

### 3. Isolation Levels (SQL Standard)

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|---|---|---|---|
| **READ UNCOMMITTED** | Possible | Possible | Possible |
| **READ COMMITTED** | ❌ Prevented | Possible | Possible |
| **REPEATABLE READ** | ❌ Prevented | ❌ Prevented | Possible |
| **SERIALIZABLE** | ❌ Prevented | ❌ Prevented | ❌ Prevented |

| Anomaly | Description |
|---|---|
| **Dirty Read** | Reading data written by an uncommitted transaction |
| **Non-Repeatable Read** | Same read returns different values (another Tx modified & committed) |
| **Phantom Read** | Re-executing a query returns new rows (another Tx inserted & committed) |

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| "2PL prevents deadlocks" | **No.** 2PL prevents only non-serializable schedules. Conservative 2PL prevents deadlocks |
| "Conflict serializable = View serializable" | Conflict ⊂ View. Every conflict serializable is view serializable, not vice versa |
| "Thomas Write Rule ensures conflict serializability" | **No.** It ensures **view serializability**, not conflict |
| "Timestamp ordering causes deadlocks" | **No.** Timestamp ordering is **deadlock-free** (no waiting) |
| "Recoverable implies cascadeless" | **No.** Recoverable ⊂ Cascadeless. A recoverable schedule may still have cascading rollbacks |
| "Serializability implies recoverability" | **No.** They are **independent** properties |
| "Strict 2PL releases all locks at commit" | Only **X-locks** in strict 2PL. **Rigorous** 2PL releases ALL locks at commit |

---

## 3 Worked Examples

### Example 1: Precedence Graph (Easy)

**Q:** Is this schedule conflict serializable?
```
S: R1(A) W2(A) R2(B) W1(B)
```

**Solution:**
- Conflicts:
  - R1(A) and W2(A) → T1 → T2
  - R2(B) and W1(B) → T2 → T1
- Precedence Graph: T1 → T2 → T1 (CYCLE!)
- **Not conflict serializable** ❌

---

### Example 2: Recoverability Check (Medium)

**Q:** Is this schedule recoverable?
```
S: R1(A) W1(A) R2(A) W2(A) C2 C1
```

**Solution:**
- T2 reads A after T1 wrote A → T2 has read from T1.
- T2 commits (C2) **before** T1 commits (C1).
- **Irrecoverable!** ❌ (If T1 aborts, T2 used invalid data but already committed.)

To make it recoverable: move C1 before C2.

---

### Example 3: 2PL Verification (GATE Level)

**Q:** Does this schedule follow 2PL?
```
T1: Lock-S(A) Read(A) Lock-X(B) Write(B) Unlock(A) Unlock(B)
```

**Solution:**
```
Lock-S(A) → Growing
Lock-X(B) → Growing
Unlock(A) → Shrinking
Unlock(B) → Shrinking
```
- All locks acquired before any unlock → Growing phase then Shrinking phase.
- **Yes, follows 2PL** ✅

**But does this follow 2PL?**
```
T1: Lock-S(A) Read(A) Unlock(A) Lock-X(B) Write(B) Unlock(B)
```
- Lock-S(A) → Growing
- Unlock(A) → Shrinking
- Lock-X(B) → **Acquiring lock in shrinking phase!** ❌
- **Does NOT follow 2PL** ❌

---

## Revision Table

| Concept | Key Point |
|---|---|
| **ACID** | Atomicity, Consistency, Isolation, Durability |
| **Serial Schedule** | No interleaving — always correct, poor performance |
| **Conflict Serializable** | Precedence graph is acyclic |
| **View Serializable** | Superset of conflict serializable |
| **Recoverable** | Read-from Tx commits first |
| **Cascadeless** | Read only committed data |
| **Strict** | No R/W on uncommitted data |
| **2PL** | Ensures conflict serializability, NOT deadlock-free |
| **Strict 2PL** | X-locks until commit → cascadeless |
| **Rigorous 2PL** | All locks until commit → strict |
| **Conservative 2PL** | All locks before start → deadlock-free |
| **Timestamp** | Deadlock-free, conflict serializable |
| **Thomas Write Rule** | Skip obsolete writes → view serializable |
| **Wait-Die** | Old waits, young dies |
| **Wound-Wait** | Old wounds young, young waits |

---

*← [06 — SQL Mastery](06_SQL_Mastery.md) | [08 — File Structures & Indexing →](08_File_Structures_and_Indexing.md)*
