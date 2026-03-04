# Round 7 — JVM, GC, Performance (Advanced)

## 1. What happens when you run a Java program (class loading steps)?

1.  **Loading:** ClassLoader reads the `.class` file byte stream and maps it into the Runtime Data Area (Method Area).
2.  **Linking:**
    *   **Verification:** Checks bytecode validity (security).
    *   **Preparation:** Allocates static variables with default values (int=0, ref=null).
    *   **Resolution:** Replaces symbolic references with direct memory references.
3.  **Initialization:** Runs static blocks (`static {}`) and assigns actual static values.
4.  **Execution:** `main()` is called.

## 2. Explain Young gen / Old gen idea at a high level.

**Generational Hypothesis:** "Most objects die young."
*   **Young Generation (Eden + Survivor Spaces):** Where new objects are born. GC here is frequent and fast ("Minor GC").
*   **Old Generation (Tenured):** Objects that survived several Minor GCs are moved here. GC here is infrequent and slow ("Major GC").
*   **PermGen / Metaspace:** Stores Class metadata (not heap objects).

## 3. What are GC pauses and how do you reduce them?

**"Stop The World" (STW):** The JVM pauses ALL application threads to mark/cleanup memory.
*   **Reduce by:**
    1.  **Allocating less:** Reduce temporary object creation (String creation, iterator loops).
    2.  **Tuning Heap size:** Too small = frequent GC. Too big = long pauses.
    3.  **Choosing GC:**
        *   **G1GC:** Default in modern Java. Balanced throughput/latency.
        *   **ZGC / Shenandoah:** Ultra-low latency (sub-millisecond pauses) for huge heaps.

## 4. Memory leak in Java — how can it happen despite GC?

GC only removes **unreachable** objects. A leak happens when you hold a reference to an object you *think* you are done with, but the code still references it.

**Common Causes:**
1.  **Static Collections:** Adding objects to a `static List` and never removing them. It grows forever.
2.  **Listeners/Callbacks:** Registering a listener but never modifying unregistering it. The publisher holds a reference to the listener.
3.  **Cached Connections:** Not closing DB connections or Streams properly.
4.  **ThreadLocal:** Not clearing ThreadLocal variables in thread pools (Tomcat web apps).

## 5. OutOfMemoryError: Metaspace vs heap OOM — difference.

*   **Heap OOM (`Java heap space`):** Your application created too many Objects (Data). You need to analyze the Heap Dump.
*   **Metaspace OOM (`Metaspace`):** You loaded too many Classes (Code). Common in applications using dynamic class generation (CGLib, Hibernate proxies, hot reloading).

## 6. How do you debug high CPU usage in a Java service? Steps/tools.

1.  **Top command:** Find the PID of the Java process consuming high CPU.
2.  **Thread identification:** Run `top -H -p <PID>` to see specific *threads* consuming CPU. Get the Thread ID (TID) (decimal).
3.  **Convert TID to Hex:** (e.g., 100 -> 0x64).
4.  **Take Thread Dump:** Run `jstack <PID> > dump.txt`.
5.  **Analyze:** Search for the Hex TID (`nid=0x64`) in the dump.
    *   Directly points to the line of code running in a tight loop.
