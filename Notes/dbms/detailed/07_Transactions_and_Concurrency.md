# 7. Transaction Management & Concurrency Control — Detailed GATE CSE Guide

> **GATE Weightage:** 4–6 marks — one of the **highest-weighted** DBMS topics! You'll get questions on schedule serializability (drawing precedence graphs), recoverability classification, 2PL protocol verification, and timestamp-based protocol rules.

---

## What is a Transaction?

Imagine you're transferring ₹1000 from Account A to Account B in a banking system. This involves two steps:

1. **Deduct** ₹1000 from Account A: `A = A - 1000`
2. **Add** ₹1000 to Account B: `B = B + 1000`

What if the system crashes after Step 1 but before Step 2? Account A lost ₹1000, but Account B didn't receive it! The money has **disappeared** from the system!

A **transaction** groups these two operations into a single logical unit. The rule is: **Either BOTH steps complete, or NEITHER does.** If the system crashes after Step 1, the entire transaction is **rolled back** (undone), and Account A gets its ₹1000 back.

**Formally:** A transaction is a sequence of read and write operations on database items that forms a **single logical unit of work**.

**Notation:**
- `R(X)` — Read the value of database item X into memory
- `W(X)` — Write the value of X from memory to database

**Example transaction:**
```
T1: R(A)          -- Read A (say A = 5000)
    A = A - 1000  -- Compute new value (4000)
    W(A)          -- Write A back (A = 4000)
    R(B)          -- Read B (say B = 3000)
    B = B + 1000  -- Compute new value (4000)
    W(B)          -- Write B back (B = 4000)
```

---

## ACID Properties — The Four Guarantees

Every transaction must satisfy four properties, remembered by the acronym **ACID**:

### Atomicity — "All or Nothing"

Either ALL operations of the transaction complete, or NONE do.

**Analogy:** Like swallowing a pill — you either swallow the whole thing or nothing. You can't half-swallow it.

**Ensured by:** Recovery system using **undo/redo logs**

**What happens if the system crashes mid-transaction?**
- If the transaction had NOT committed → **Undo** all its changes (rollback)
- If the transaction HAD committed but changes weren't fully written to disk → **Redo** those changes

### Consistency — "Valid State to Valid State"

The database must go from one **valid state** to another valid state. All integrity constraints must hold before AND after the transaction.

**Example:** In a banking system, the total balance across all accounts must remain the same. If A + B = 8000 before the transfer, then A + B must still equal 8000 after.

**Ensured by:** The application programmer + integrity constraints defined in the schema

### Isolation — "No Interference"

Even though transactions run **concurrently** (at the same time), each transaction should feel like it's running **alone**. One transaction shouldn't see the intermediate (incomplete) changes of another.

**Why we need this:** If T1 is transferring money (A = A - 1000) and T2 reads A between T1's read and write, T2 sees an inconsistent value.

**Ensured by:** Concurrency control protocols (2PL, timestamps, etc.)

### Durability — "Once Committed, Always Committed"

Once a transaction is **committed** (successfully completed), its changes are **permanent** — even if the system crashes immediately after.

**Ensured by:** Write-Ahead Logging (WAL) and checkpointing

---

## Transaction States

A transaction goes through these states during its lifecycle:

```
                ┌─────────────┐
  Start ──────> │   ACTIVE     │ (executing read/write operations)
                └──────┬───────┘
                       │
                       │ (last operation executed)
                       ▼
               ┌───────────────────┐
               │ PARTIALLY         │ (finished executing, waiting for commit)
               │ COMMITTED         │
               └──┬──────────┬────┘
                  │          │
         (success)│          │(failure detected)
                  ▼          ▼
          ┌──────────┐  ┌────────┐
          │COMMITTED │  │ FAILED │
          └──────────┘  └────┬───┘
           (permanent!)       │ (rollback)
                             ▼
                       ┌──────────┐
                       │ ABORTED  │
                       └──────────┘
                       (changes undone,
                        restart possible)
```

---

## Schedules — Running Multiple Transactions

### What is a Schedule?

When multiple transactions run concurrently, their operations can be **interleaved** (mixed together). A **schedule** is a specific ordering of ALL operations from all concurrent transactions.

**Rule:** A schedule must preserve the **order of operations within each transaction** (you can't rearrange a transaction's own steps), but operations from DIFFERENT transactions can be interleaved.

### Serial Schedule

Operations from different transactions are **NOT interleaved**. One transaction finishes completely before the next begins.

```
Serial Schedule (T1 then T2):
R1(A) W1(A) R1(B) W1(B) R2(A) W2(A) R2(B) W2(B)
|_________T1___________|  |_________T2___________|
```

**Properties:**
- ✅ Always correct (no interference between transactions)
- ❌ Very slow (no parallelism — transactions wait for each other)

### Non-Serial (Concurrent) Schedule

Operations from different transactions ARE interleaved.

```
Non-serial Schedule:
R1(A) R2(A) W1(A) W2(A) R1(B) R2(B) W1(B) W2(B)
  T1    T2    T1    T2    T1    T2    T1    T2
```

**Properties:**
- ✅ Better performance (parallelism)
- ❓ May or may not be correct — need to check **serializability**

---

## Serializability — Is a Concurrent Schedule Correct?

A concurrent schedule is **correct** if it's **equivalent** to some serial schedule. This equivalence can be defined in two ways:

### Conflict Serializability

#### What are Conflicting Operations?

Two operations **conflict** if ALL THREE conditions are true:
1. They belong to **different transactions**
2. They access the **same data item**
3. **At least one** of them is a **WRITE**

| Pair | Same Item? | At least one Write? | CONFLICT? |
|---|---|---|---|
| R₁(A), R₂(A) | ✅ | ❌ (both read) | **No** ❌ |
| R₁(A), W₂(A) | ✅ | ✅ | **Yes** ✅ |
| W₁(A), R₂(A) | ✅ | ✅ | **Yes** ✅ |
| W₁(A), W₂(A) | ✅ | ✅ | **Yes** ✅ |
| R₁(A), W₂(B) | ❌ (different items) | ✅ | **No** ❌ |
| R₁(A), R₁(B) | — | — | **No** ❌ (same transaction!) |

> **Mnemonic for GATE:** **RR = No conflict. Everything else with same item and different transaction = Conflict.**

#### Why Do Conflicts Matter?

Two non-conflicting operations can be **swapped** without changing the result. But swapping conflicting operations MAY change the result.

#### Conflict Equivalence

Two schedules are **conflict equivalent** if you can convert one into the other by **swapping adjacent non-conflicting operations.**

#### Conflict Serializable

A schedule is **conflict serializable** if it is conflict equivalent to **some** serial schedule.

### Testing Conflict Serializability — The Precedence Graph

This is the standard algorithm for checking conflict serializability:

**Step 1:** Create a **node** for each transaction (T₁, T₂, T₃, ...).

**Step 2:** For each pair of conflicting operations:
- If Tᵢ's operation comes BEFORE Tⱼ's operation in the schedule → add edge **Tᵢ → Tⱼ**
- This means "Tᵢ must come before Tⱼ in any equivalent serial schedule"

**Step 3:** Check for **cycles** in the graph:
- **No cycle → Conflict serializable ✅** — Any topological sort of the graph gives an equivalent serial order
- **Cycle exists → NOT conflict serializable ❌**

### Detailed Worked Example

**Schedule:** `R₁(A) W₂(A) R₃(A) W₁(A) R₂(B) W₃(B)`

**Step 1: Identify conflicts**

| Op1 | Op2 | Same item? | Different Tx? | At least one Write? | Conflict? | Edge |
|---|---|---|---|---|---|---|
| R₁(A) | W₂(A) | ✅ A | ✅ T1,T2 | ✅ W₂ | ✅ | **T₁ → T₂** |
| R₁(A) | W₁(A) | ✅ A | ❌ same T1 | — | ❌ | — |
| R₁(A) | R₃(A) | ✅ A | ✅ | ❌ both read | ❌ | — |
| W₂(A) | R₃(A) | ✅ A | ✅ T2,T3 | ✅ W₂ | ✅ | **T₂ → T₃** |
| W₂(A) | W₁(A) | ✅ A | ✅ T2,T1 | ✅ both write | ✅ | **T₂ → T₁** |
| R₃(A) | W₁(A) | ✅ A | ✅ T3,T1 | ✅ W₁ | ✅ | **T₃ → T₁** |
| R₂(B) | W₃(B) | ✅ B | ✅ T2,T3 | ✅ W₃ | ✅ | **T₂ → T₃** |

**Step 2: Draw precedence graph**
```
T₁ → T₂ (from R₁(A) before W₂(A))
T₂ → T₃ (from W₂(A) before R₃(A))
T₂ → T₁ (from W₂(A) before W₁(A))  ← WAIT!
T₃ → T₁ (from R₃(A) before W₁(A))
T₂ → T₃ (from R₂(B) before W₃(B))  ← duplicate, already have it
```

**Graph:**
```
T₁ → T₂
T₂ → T₁   ← T₁→T₂→T₁ creates a CYCLE!
T₂ → T₃
T₃ → T₁
```

**Cycle: T₁ → T₂ → T₁** ❌

**Conclusion: NOT conflict serializable.**

---

### View Serializability — A Broader Definition

View serializability is a **weaker** (more permissive) notion. Some schedules that are NOT conflict serializable ARE view serializable.

**Three conditions for view equivalence of schedules S and S':**
1. **Initial reads:** Same transaction reads the initial value of each data item
2. **Updated reads:** If Tᵢ reads a value written by Tⱼ in S, the same must happen in S'
3. **Final writes:** Same transaction performs the final write of each data item

**Key relationship:**
```
Conflict Serializable ⊂ View Serializable ⊂ All Schedules

A schedule that is view serializable but NOT conflict serializable
must contain a BLIND WRITE (a write without a preceding read).
```

> **⚠️ GATE Facts:**
> - Testing conflict serializability: **Polynomial time** (precedence graph — O(n²))
> - Testing view serializability: **NP-complete** (computationally hard)
> - Thomas Write Rule produces view serializable (but not necessarily conflict serializable) schedules

---

## Recoverability — Can We Undo Safely?

Serializability ensures **correctness**. Recoverability ensures we can **recover** from failures.

### Irrecoverable Schedule — THE WORST

```
T₁: R₁(X) W₁(X)
T₂:              R₂(X) W₂(X) C₂    (T₂ commits!)
T₁:                                  ... (T₁ might abort!)
```

**Problem:** T₂ read X after T₁ wrote it. T₂ COMMITTED based on T₁'s data. But what if T₁ ABORTS later? T₂ used invalid (dirty) data and already committed — we CAN'T undo T₂'s commit!

**This is irrecoverable and MUST be avoided in any real system.**

### Recoverable Schedule

**Rule:** If T₂ reads data written by T₁, then T₁ must **commit before** T₂ commits.

```
T₁: R₁(X) W₁(X)                C₁    (T₁ commits first!)
T₂:              R₂(X) W₂(X)       C₂ (T₂ commits after T₁)
```

Now if T₁ decides to abort (before its commit), T₂ hasn't committed yet, so T₂ can be aborted too. ✅

### Cascadeless Schedule (Avoids Cascading Rollback)

**Rule:** T₂ reads data written by T₁ **only AFTER** T₁ has committed.

```
T₁: R₁(X) W₁(X) C₁                      (T₁ commits)
T₂:                   R₂(X) W₂(X) C₂    (T₂ reads only committed data)
```

**Why "cascadeless"?** Without this rule, if T₁ aborts:
- T₂ read dirty data from T₁ → must abort T₂
- If T₃ read data from T₂ → must abort T₃
- This creates a **cascade** of rollbacks — hence "cascadeless" = avoiding this

### Strict Schedule

**Rule:** T₂ neither **reads nor writes** a data item written by T₁ until T₁ commits or aborts.

This is the strictest (safest) level.

### The Hierarchy

```
Serial ⊂ Strict ⊂ Cascadeless ⊂ Recoverable ⊂ All Schedules

Most restrictive ────────────────────────> Least restrictive
(safest)                                   (most permissive)
```

> **⚠️ GATE Critical Point:** Serializability and recoverability are **INDEPENDENT** properties!
> - A schedule can be serializable but irrecoverable
> - A schedule can be recoverable but not serializable
> - Ideally, we want BOTH

---

## Concurrency Control — Ensuring Correctness

### Lock-Based Protocols

The idea: Before accessing a data item, a transaction must **acquire a lock** on it.

| Lock Type | Also Called | Who Can Also Lock the Same Item? |
|---|---|---|
| **Shared (S)** | Read Lock | Other transactions with S-locks ✅ (multiple readers OK) |
| **Exclusive (X)** | Write Lock | Nobody else ❌ (exclusive access) |

**Compatibility matrix:**

|  | S requested | X requested |
|---|---|---|
| **S held** | ✅ Grant | ❌ Wait |
| **X held** | ❌ Wait | ❌ Wait |

**In simple terms:** Multiple readers can coexist, but a writer needs exclusive access.

### Two-Phase Locking (2PL) — The Main Protocol

**Rule:** A transaction's locks must follow two phases:

1. **Growing Phase:** The transaction can **acquire** new locks but cannot **release** any.
2. **Shrinking Phase:** The transaction can **release** locks but cannot **acquire** any new ones.

The **lock point** is the moment when the transaction has acquired ALL its locks (the boundary between growing and shrinking phases).

```
       Growing Phase          │         Shrinking Phase
                              │
Lock-S(A)                     │
    Lock-X(B)                 │
        Lock-S(C)             │  ← Lock Point (maximum locks)
                              │  Unlock(A)
                              │      Unlock(C)
                              │          Unlock(B)
────────────────────────────────────────────────────────→ Time
```

**What 2PL guarantees:**

| Variant | Rule | Conflict Serializable? | Cascadeless? | Deadlock-Free? |
|---|---|---|---|---|
| **Basic 2PL** | Growing then shrinking | ✅ Yes | ❌ No | ❌ No |
| **Strict 2PL** | All **X-locks** released only at commit/abort | ✅ Yes | ✅ Yes | ❌ No |
| **Rigorous 2PL** | **ALL** locks released only at commit/abort | ✅ Yes | ✅ Yes | ❌ No |
| **Conservative 2PL** | ALL locks acquired BEFORE transaction starts | ✅ Yes | — | ✅ Yes |

> **⚠️ GATE Critical Points:**
> - 2PL guarantees **conflict serializability** ✅
> - 2PL does **NOT** prevent deadlocks ❌ (except conservative 2PL)
> - The serial order is determined by the **lock point order** of transactions

**Is this 2PL? — Quick Check Example:**
```
Lock-S(A)  Read(A)  Unlock(A)  Lock-X(B)  Write(B)  Unlock(B)
  grow       —       shrink       ← ACQUIRING IN SHRINKING PHASE!
```
❌ **NOT 2PL** — acquiring Lock-X(B) after releasing Lock-S(A)

```
Lock-S(A)  Read(A)  Lock-X(B)  Write(B)  Unlock(A)  Unlock(B)
  grow       —       grow         —       shrink      shrink
```
✅ **IS 2PL** — all acquires before all releases

---

### Timestamp-Based Protocol

Instead of locks, each transaction gets a **timestamp** (TS) when it starts. Older transactions have smaller timestamps.

Each data item X tracks:
- **W_TS(X):** Timestamp of the last transaction that WROTE X
- **R_TS(X):** Timestamp of the last transaction that READ X

**Rules:**

**When Tᵢ wants to READ X:**
```
If TS(Tᵢ) < W_TS(X):
    "I'm too old — someone younger already overwrote X"
    → ABORT Tᵢ and restart with a new timestamp
Else:
    Allow the read
    R_TS(X) = max(R_TS(X), TS(Tᵢ))
```

**When Tᵢ wants to WRITE X:**
```
If TS(Tᵢ) < R_TS(X):
    "Someone younger already read the old value — my write is too late"
    → ABORT Tᵢ
If TS(Tᵢ) < W_TS(X):
    "Someone younger already wrote X — my write is obsolete"
    → ABORT Tᵢ (or SKIP using Thomas Write Rule)
Else:
    Allow the write
    W_TS(X) = TS(Tᵢ)
```

**Properties:**
- ✅ Deadlock-free (no locks → no waiting → no deadlock)
- ✅ Conflict serializable (serial order = timestamp order)
- ❌ May cause starvation (repeated aborts of same transaction)
- ❌ NOT cascadeless (basic version)

**Thomas Write Rule:** Instead of aborting when TS(Tᵢ) < W_TS(X) during a write, just **skip the write**. The write is obsolete anyway — a newer transaction already wrote X. This results in **view serializable** (not necessarily conflict serializable) schedules.

---

## Deadlock Handling

### What is a Deadlock?

Two or more transactions are **waiting for each other** to release locks, and none can proceed.

```
T₁ holds Lock(A), wants Lock(B)
T₂ holds Lock(B), wants Lock(A)

T₁ waits for T₂ to release B
T₂ waits for T₁ to release A
→ Both wait forever! DEADLOCK!
```

### Detection: Wait-For Graph

1. Create a node for each active transaction
2. Add edge Tᵢ → Tⱼ if Tᵢ is **waiting for a lock** held by Tⱼ
3. **Cycle in the graph → Deadlock!**
4. Choose a **victim** transaction and abort it to break the cycle

### Prevention: Wait-Die and Wound-Wait

These use timestamps to prevent deadlocks before they happen:

**Setup:** Transaction Tᵢ requests a lock held by Tⱼ. Compare their timestamps.

**Wait-Die (Non-preemptive):**
```
If Tᵢ is OLDER (smaller TS) than Tⱼ:
    Tᵢ WAITS for Tⱼ to release    ("Old waits for young")
If Tᵢ is YOUNGER (larger TS) than Tⱼ:
    Tᵢ DIES (aborted, restarts)   ("Young dies")
```

**Wound-Wait (Preemptive):**
```
If Tᵢ is OLDER (smaller TS) than Tⱼ:
    Tᵢ WOUNDS Tⱼ (forces Tⱼ to abort)  ("Old attacks young")
If Tᵢ is YOUNGER (larger TS) than Tⱼ:
    Tᵢ WAITS for Tⱼ to release          ("Young waits for old")
```

> **Mnemonic:**
> - **Wait-Die:** Old waits, Young dies. (Requesting tx is older → wait; younger → die)
> - **Wound-Wait:** Old wounds, Young waits. (Requesting tx is older → wound; younger → wait)
>
> In BOTH schemes, the **younger** transaction is the one that gets aborted.

---

## SQL Isolation Levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|---|---|---|---|
| **READ UNCOMMITTED** | ✅ Possible | ✅ Possible | ✅ Possible |
| **READ COMMITTED** | ❌ Prevented | ✅ Possible | ✅ Possible |
| **REPEATABLE READ** | ❌ Prevented | ❌ Prevented | ✅ Possible |
| **SERIALIZABLE** | ❌ Prevented | ❌ Prevented | ❌ Prevented |

**Anomalies explained simply:**
- **Dirty Read:** Reading data from a transaction that hasn't committed yet (might be rolled back)
- **Non-Repeatable Read:** You read X, someone modifies and commits X, you read X again and get a different value
- **Phantom Read:** You run a query, someone inserts new matching rows and commits, you run the same query and get extra rows

---

## Common Pitfalls

| Pitfall | Correct Understanding |
|---|---|
| "2PL prevents deadlocks" | Only **Conservative** 2PL prevents deadlocks |
| "Conflict serializable = View serializable" | Every CS is VS, not vice versa |
| "Timestamp ordering causes deadlocks" | TS is **deadlock-free** (no waiting) |
| "Recoverable implies cascadeless" | Recoverable ⊃ Cascadeless (recoverable is weaker) |
| "Serializable implies recoverable" | They are **independent** properties |
| "Strict 2PL releases ALL locks at commit" | Only **X-locks**. Rigorous releases ALL locks |
| "Thomas Write Rule = Conflict Serializable" | TWR gives **View** serializable, not conflict |

---

## Revision Table

| Concept | Key Point |
|---|---|
| **ACID** | Atomicity, Consistency, Isolation, Durability |
| **Conflict Serializable** | Precedence graph has **no cycle** |
| **View Serializable** | Superset of conflict serializable; NP-complete to test |
| **Recoverable** | Read-from transaction commits **first** |
| **Cascadeless** | Read only **committed** data |
| **2PL** | Growing then shrinking → conflict serializable ✅ |
| **Strict 2PL** | X-locks until commit → cascadeless ✅ |
| **Rigorous 2PL** | ALL locks until commit |
| **Conservative 2PL** | All locks before start → deadlock-free ✅ |
| **Timestamp** | No locks → deadlock-free ✅; conflict serializable ✅ |
| **Wait-Die** | Old waits, young dies |
| **Wound-Wait** | Old wounds young, young waits |

---

*← [06 — SQL Mastery](06_SQL_Mastery.md) | [08 — File Structures & Indexing →](08_File_Structures_and_Indexing.md)*
