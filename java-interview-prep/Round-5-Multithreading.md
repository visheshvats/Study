# Round 5 — Multithreading + Concurrency

## 1. Process vs thread.

*   **Process:** Independent program in execution. Has its own separate memory space (Heap). Heavyweight context switch.
*   **Thread:** Light-weight process within a process. Shares memory (Heap) with other threads in the same process but has its own Stack. Fast context switch.

## 2. What is the Java memory model? What is “visibility”?

**JMM (Java Memory Model)** defines how threads interact through memory.
*   **Problem:** Threads cache variables in local CPU registers for speed.
*   **Visibility:** The guarantee that changes made to a variable by one thread are visible to other threads directly. Without explicit synchronization (volatile, synchronized), Thread A might write X=1, but Thread B still sees cached X=0.

## 3. What problems does volatile solve? What it does not solve?

*   **Solves: Visibility.** It forces reads and writes to go directly to Main Memory avoiding CPU caches. "Happens-before" relationship.
*   **Does NOT Solve: Atomicity.**
    *   `volatile int count = 0; count++;` is NOT thread-safe. `count++` is 3 steps (read, modify, write). Parallel threads can overwrite each other.

## 4. Difference between synchronized method vs block.

*   **Method:** Locks on `this` object (if instance) or `Class` object (if static) for the **entire duration** of the method.
*   **Block:** Locks on a **specific object** for a **specific section** of code. Preferable for performance (Critical Section minimization).
    ```java
    synchronized(lockObj) { ... }
    ```

## 5. What is a race condition? Give a real example.

Two threads access a shared resource concurrently, and the final outcome depends on the timing/ordering of execution.

**Example:** Check-Then-Act.
`if (account.balance >= 100) { account.withdraw(100); }`
Thread A checks (true). Context Switch.
Thread B checks (true).
Thread B withdraws (balance=0).
Thread A resumes and withdraws again (balance=-100).

## 6. Deadlock — conditions + how to prevent.

**Deadlock:** Two threads wait for each other to release a lock forever.

**Conditions:**
1.  Mutual Exclusion.
2.  Hold and Wait.
3.  No Preemption.
4.  Circular Wait.

**prevention:** Break the Circular Wait. **Order the Locks.** Always acquire Lock A before Lock B in all threads.

## 7. wait() vs sleep() vs join().

*   **wait():** Object method. Releases the lock. Thread waits until notified. Must be in synchronized block.
*   **sleep():** Thread method. Keeps the lock. Pauses execution for time T.
*   **join():** Thread method. "Wait for this thread to die". `t1.join()` causes current thread to pause until `t1` finishes.

## 8. Why must wait() be called inside a synchronized context?

Because `wait()` releases the lock associated with the object. If you don't own the lock (aren't synchronized), you can't release it. It throws `IllegalMonitorStateException`. Also needed to prevent "Lost Wakeup Problem" (race condition between checking condition and waiting).

## 9. Explain ThreadLocal and a real use-case.

**ThreadLocal:** Provides thread-local variables. Each thread accessing the variable gets its own independent copy.

**Use-Case:**
1.  **User Context:** Storing User ID in a Web Request handling thread (Spring Security uses this).
2.  **SimpleDateFormat:** Valid legacy formatters were not thread-safe. Giving one per thread avoided synchronization cost.

## 10. Explain ExecutorService and thread pool types.

Framework to decouple task submission from execution.
*   **FixedThreadPool(N):** N threads. Queue fills up if busy. Good for server load control.
*   **CachedThreadPool:** Creates threads as needed. Kills idle ones. Good for many short-lived tasks. Danger: Can create infinite threads and crash OOM.
*   **SingleThreadExecutor:** 1 thread. Serial execution. Good for ordering constraints.

## 11. What is Callable vs Runnable?

*   **Runnable:** `void run()`. Cannot return value. Cannot throw checked exception.
*   **Callable:** `V call()`. Returns a Result. Can throw Exception. Used with `Future`.

## 12. Future vs CompletableFuture — why CF is better?

*   **Future:** Blocking. `future.get()` halts the thread until result arrives. No way to chain actions or manually complete it.
*   **CompletableFuture (Java 8):** Non-blocking (Callback style). Push based.
    *   Chaining: `.thenApply()`, `.thenAccept()`.
    *   Combining: `.allOf()`, `.anyOf()`.
    *   Exception handling built-in.

## 13. Explain CountDownLatch vs CyclicBarrier.

*   **CountDownLatch:** "Wait for N events". One-shot. Once count reaches zero, gate opens. Cannot be reset. (e.g., Wait for DB, Cache, and API services to start before opening traffic).
*   **CyclicBarrier:** "Wait for N threads to meet at a point". Reusable. If 3 threads wait, they all block until the 3rd arrives, then all proceed. (e.g., Parallel processing chunks of a matrix, then merging).

## 14. What is a ReentrantLock and when you prefer it over synchronized?

A manual lock interface.
**Advantages over synchronized:**
1.  **Fairness:** Can enable strict ordering (longest waiting thread gets lock).
2.  **TryLock:** `lock.tryLock()` attempts to get lock but returns immediately if unavailable (avoids blocking forever).
3.  **Interruptible:** Can be interrupted while waiting.

## 15. How does ConcurrentHashMap achieve better concurrency?

It uses **Lock Stripping** (segments) in Java 7 or **CAS (Compare-And-Swap) + Node Locking** in Java 8+.
Instead of locking the *entire* map (like Hashtable), it only locks the specific **bucket** being written to. Reads never block. writes block only that bucket.

## 16. What is the difference between parallel stream and normal stream? When not to use it?

*   **Parallel Stream:** Uses ForkJoinPool to split task into chunks and run on multiple cores. `list.parallelStream()`.
*   **When NOT to use:**
    1.  Small dataset (overhead of splitting > gain).
    2.  Dependent tasks (stateful operations).
    3.  IO-bound tasks (Parallel stream uses the common pool; blocking it kills performance for everyone).
