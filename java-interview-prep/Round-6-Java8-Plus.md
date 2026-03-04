# Round 6 — Java 8+ (Streams, Functional, Optional)

## 1. What is a functional interface? Examples.

An interface with **exactly one abstract method**.
It can have multiple default or static methods. It is the target type for Lambda expressions.

**Annotation:** `@FunctionalInterface` (compiler check).
**Examples:**
*   `Runnable` -> `void run()`
*   `Callable<V>` -> `V call()`
*   `Consumer<T>` -> `void accept(T t)`
*   `Function<T, R>` -> `R apply(T t)`
*   `Predicate<T>` -> `boolean test(T t)`
*   `Supplier<T>` -> `T get()`

## 2. map vs flatMap in streams with a real example.

*   **`map()`**: Transform Data. One-to-One.
    *   Input: `Stream<String>` (names).
    *   Operation: `s -> s.length()`.
    *   Result: `Stream<Integer>` (lengths).
*   **`flatMap()`**: Flatten Data. One-to-Many.
    *   Input: `List<User>`, where each User has `List<String> emails`.
    *   Goal: Get a stream of ALL emails.
    *   `users.stream().map(u -> u.getEmails())` -> returns `Stream<List<String>>` (Stream of Lists).
    *   `users.stream().flatMap(u -> u.getEmails().stream())` -> returns `Stream<String>` (Stream of single emails flattened).

## 3. filter, sorted, collect — explain laziness and pipeline.

*   **Pipeline:** Streams have 3 parts: Source -> Intermediate Ops -> Terminal Op.
*   **Laziness:** Intermediate operations (`filter`, `map`, `sorted`) do **NOT** execute until a terminal operation (`collect`, `forEach`) is invoked.
*   **Example:**
    ```java
    list.stream()
       .filter(s -> { print("Filtering"); return true; }) // Won't print yet
       .collect(Collectors.toList()); // Now it runs!
    ```

## 4. Collectors.groupingBy() — how does it work internally?

It collects elements into a `Map<K, List<V>>`.
*   You provide a classifier function (to generate the Key).
*   **Example:** Group employees by Department.
    ```java
    Map<Dept, List<Employee>> map = empList.stream()
        .collect(Collectors.groupingBy(Employee::getDepartment));
    ```
*   **Logic:** It iterates stream items, applies the classifier function to get the key, gets the list from that key in the map (or creates new ArrayList), and adds the item.

## 5. How do you handle nulls with Optional properly? What not to do?

**Goal:** Avoid `NullPointerException` (NPE).

**Proper Usage:**
*   Return `Optional<T>` from methods that might return "nothing" (e.g., `findUserById`).
*   use `.map()`, `.flatMap()`, `.ifPresent()`.
*   `Optional.ofNullable(val).orElse("default")`.

**What NOT to do:**
*   `if (opt.isPresent()) { return opt.get(); }` // Basically just a verbose null check!
*   Passing `Optional` as a method argument (bad design, overload instead).
*   Using `Optional` in class fields (not serializable).

## 6. Explain method references and when they improve readability.

Shorthand for a lambda calling a specific method. `::` operator.

*   `s -> System.out.println(s)` BECOMES `System.out::println`
*   `str -> Integer.parseInt(str)` BECOMES `Integer::parseInt`

**Improves readability:** Removes boilerplate parameter passing when you are just "passing it through".

## 7. What’s the difference between findFirst() and findAny()?

*   **`findFirst()`**: Deterministic. Returns the very first element in encounter order. (Important for ordered streams like Lists).
*   **`findAny()`**: Non-deterministic. Returns *any* element. (optimized for Parallel Streams, as the thread that finds "something" first can return immediately without waiting to check order).

## 8. Why are streams single-use?

A Stream implements `AutoCloseable` (conceptually) and represents a "flow" of data, not a container. Once you traverse it (call a terminal op), it is consumed. You cannot reuse it.
**Why?** To match Iterator design and support infinite streams (generators) where "resetting" might be impossible.

## 9. What are intermediate vs terminal operations?

*   **Intermediate:** Return a new Stream. Lazy. (filter, map, peek, distinct, limit).
*   **Terminal:** Retun a result (non-stream) or void. Trigger processing. (collect, forEach, reduce, count, anyMatch).
