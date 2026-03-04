# Round 1 — Core Java (Warm-up + Fundamentals)

## 1. What’s the difference between JDK, JRE, JVM?

They form the three layers of the Java platform structure:

*   **JVM (Java Virtual Machine):** The abstract machine that actually executes the Java bytecode. It provides the runtime environment but does not contain any development tools or standard libraries by itself (conceptually). It is platform-dependent (you have a Windows JVM, Linux JVM, etc.).
*   **JRE (Java Runtime Environment):**  `JVM + Core Libraries (rt.jar for Java 8, modules for 9+)`. It is what you need to **run** a Java application. It doesn't contain compilers or debuggers.
*   **JDK (Java Development Kit):** `JRE + Development Tools (javac, debugger, javadoc, etc.)`. This is what developers need to write and compile Java code.

**Relationship:** JDK ⊇ JRE ⊇ JVM.

## 2. Explain stack vs heap with a real example.

These are the two main memory areas in the JVM.

*   **Stack Memory:**
    *   Used for static memory allocation and implementation of threads.
    *   Contains **primitive values** specific to a method and **references** to objects in the Heap.
    *   Access is essentially LIFO (Last In First Out).
    *   Strictly managed: when a method exits, its stack frame is popped, and local variables are seemingly "lost".
    *   **Fast** access.

*   **Heap Memory:**
    *   Used for dynamic memory allocation.
    *   Stores **all actual Objects** (Object instances) and JRE classes.
    *   Objects here are globally accessible (if you have the reference).
    *   Managed by **Garbage Collection**.

**Example:**
```java
public void method() {
    int x = 10;           // stored in Stack
    Person p = new Person(); 
    // 'p' (reference) is in Stack.
    // The actual 'Person' object is created in Heap.
}
```

## 3. What are pass-by-value semantics in Java? (Use an object example.)

**Java is strictly Pass-by-Value.** There is no "Pass-by-Reference" in Java.

*   **Primitives:** The actual value (e.g., `5`) is copied. Changing the copy inside the method doesn't affect the original.
*   **Objects:** The **reference** (the address pointer) is copied by value. You get a copy of the key to the house, but it still opens the same house.

**Example:**
```java
void modify(Dog d) {
    d.setName("Fido"); // Works! Modifies the object on Heap via the copied reference.
    d = new Dog("Rex"); // Does NOT affect original 'd'. Only changes the local pointer.
}
```
If Java were pass-by-reference, the second line would reassign the caller's variable to the new Dog "Rex", but it doesn't.

## 4. Difference between == and .equals()? When can .equals() be unsafe?

*   **`==` Operator:**
    *   Checks for **reference equality** (memory address) for objects.
    *   Checks for **value equality** for primitives.
*   **`.equals()` Method:**
    *   Checks for **logical equality** (content). By default (in Object class), it behaves like `==` unless overridden (like in String, Integer).

**When is `.equals()` unsafe?**
When called on a `null` object.
```java
String s = null;
if (s.equals("test")) { ... } // Throws NullPointerException
```
**Fix:** Use constant on left: `"test".equals(s)` or `Objects.equals(s, "test")`.

## 5. Why is String immutable? What benefits does it give?

String is immutable because once created, its value cannot be changed. If you change it, a new String object is created.

**Benefits:**
1.  **String Constant Pool:** Saves memory. Multiple references can point to the same "Hello" literal. If one could change it, it would corrupt others.
2.  **Thread Safety:** Immutable objects are inherently thread-safe. No synchronization needed.
3.  **Security:** Strings are used for class loading, network connections, file paths. If mutable, a malicious user could change access paths after validation.
4.  **HashCode Caching:** Since content doesn't change, the hash code is calculated once and cached, making it great for HashMap keys.

## 6. String, StringBuilder, StringBuffer — when to use which?

*   **String:** Use when value will not change. (Immutable).
*   **StringBuilder:** Use for string manipulation (concatenation, appending) in a **single-threaded** environment. (Mutable, Fast, Not Synchronized).
*   **StringBuffer:** Use for string manipulation in a **multi-threaded** environment. (Mutable, Slower, All methods are `synchronized`).

**Modern Rule:** Almost always use `StringBuilder` inside methods unless you specifically share the buffer across threads.

## 7. What is the String constant pool? What happens with new String("a")?

The String Constant Pool (SCP) is a special area in the Heap (since Java 7) to store unique string literals.

**Scenario:** `String s = new String("a");`
1.  **Step 1:** JVM checks the SCP. If "a" is not there, it creates a string object "a" in the Pool.
2.  **Step 2:** The `new` keyword explicitly forces the creation of a **second** object on the standard Heap.
3.  **Step 3:** `s` refers to the Heap object, NOT the Pool object.

So, `new String("a")` creates **two** objects (if "a" wasn't in pool) or one heap object (if "a" was already in pool).

## 8. Explain method overloading vs overriding with rules.

**Method Overloading (Compile-time Polymorphism):**
*   Same method name, **different parameter list** (type, number, or order).
*   Return type **doesn't matter** for distinguishing overload.
*   Happens in the same class.

**Method Overriding (Runtime Polymorphism):**
*   Same method signature (name + params) in **Parent** and **Child** class.
*   **Rules:**
    1.  Access modifier cannot be more restrictive (e.g., Parent: `protected` -> Child: `private` is FAIL).
    2.  Return type must be covariant (same or subclass).
    3.  Exceptions: Cannot throw new/broader checked exceptions. Can throw unchecked or fewer/narrower checked exceptions.

## 9. What are access modifiers and what do they mean for inheritance?

*   **public:** Accessible everywhere.
*   **protected:** Accessible in same package + **subclasses** (even in different packages). Crucial for inheritance.
*   **default (no modifier):** Accessible only in same package.
*   **private:** Accessible only in the same class.

**Inheritance note:** You cannot override a private method because it's not visible to the child class.

## 10. final keyword for variable, method, class — explain all 3 cases.

*   **final variable:** Constant. Cannot be reassigned. (For objects, reference is constant, but state can change).
*   **final method:** Cannot be Overridden by subclasses. used to lock down behavior.
*   **final class:** Cannot be Inherited (e.g., `String`, `Integer`). prevent extension.

## 11. Difference between abstract class vs interface (modern Java perspective).

| Feature | Abstract Class (AC) | Interface (I) |
| :--- | :--- | :--- |
| **State** | Can have instance variables (state). | Stateless (only `public static final` constants). |
| **Methods** | abstract + concrete methods. | `default`, `static` (Java 8+), `private` (Java 9+), and abstract. |
| **Constructor** | Yes. | No. |
| **Inheritance** | Single inheritance (`extends`). | Multiple inheritance (`implements`). |
| **Purpose** | "Is-A" relationship. Shared base functionality. | "Can-Do" capability / Contract. |

**Modern:** Interfaces are more powerful with default methods, allowing "mixin" behavior, but they still lack instance state.

## 12. What is static initialization? When does a static block run?

Static initialization sets up static variables. A **static block** (`static { ... }`) is a block of code executed **once** when the class is **loaded** into the JVM by the ClassLoader.

It runs **before**:
*   The main method.
*   Any instance initialization block.
*   Any constructor.

## 13. What is composition vs inheritance? When do you prefer composition?

*   **Inheritance (Is-A):** White box reuse. `Car extends Vehicle`. Rigid. Changes in parent affect child.
*   **Composition (Has-A):** Black box reuse. `Car has a Engine`. Flexible.

**Prefer Composition:**
*   When you want to reuse code but not the "type".
*   To avoid the "fragile base class" problem.
*   To change behavior dynamically at runtime (Strategy Pattern).
*   Java doesn't support multiple inheritance of classes; composition allows mixing multiple behaviors.

## 14. Explain inner classes (static nested vs non-static inner).

*   **Non-static Inner Class:**
    *   Associated with an **instance** of the outer class.
    *   Has implicit reference (pointer) to the outer `this`.
    *   Cannot exist without an outer instance.
    *   `Outer o = new Outer(); Outer.Inner i = o.new Inner();`
*   **Static Nested Class:**
    *   Associated with the **class** itself.
    *   Behaves like a standard top-level class, just nested for packaging convenience.
    *   No automatic access to valid instance members of Outer.
    *   `Outer.Nested n = new Outer.Nested();`

## 15. What is autoboxing/unboxing and what bugs can it cause?

**Autoboxing:** Automatic conversion of primitive to Wrapper (int -> Integer).
**Unboxing:** Automatic conversion of Wrapper to primitive (Integer -> int).

**Bugs:**
1.  **NullPointerException:** Unboxing a `null` Integer throws NPE.
    ```java
    Integer x = null;
    int y = x; // Crash!
    ```
2.  **Performance:** Creating unnecessary objects in loops.
3.  **Comparison:** `==` compares references for Wrappers.
    ```java
    Integer a = 1000, b = 1000;
    sysout(a == b); // False (different objects)
    ```

## 16. What is type casting? When do you get ClassCastException?

Converting one type to another.

*   **Upcasting:** Child -> Parent (Implicit, always safe).
*   **Downcasting:** Parent -> Child (Explicit, risky).

**ClassCastException:** Occurs at **runtime** during downcasting if the actual object is NOT an instance of the target class.
```java
Object s = "Hello";
Integer i = (Integer) s; // Compiles, but Throws ClassCastException
```

## 17. What is immutability and how do you create an immutable class?

An object whose state cannot change after construction.

**How to create:**
1.  Make class `final` (so methods can't be overridden).
2.  Make all fields `private` and `final`.
3.  No setters.
4.  Initialize all fields via constructor.
5.  **Important:** If a field is a mutable object (like a Date or List), do NOT return the reference directly in getters. Return a deep copy or use `Collections.unmodifiableList`.
