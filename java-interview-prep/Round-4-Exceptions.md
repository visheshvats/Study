# Round 4 — Exceptions

## 1. Checked vs unchecked exceptions — why does Java have both?

*   **Checked Exceptions (`Exception` subclass):**
    *   **Intent:** Represent recoverable conditions outside the program's control (File I/O, Network calls).
    *   **Rule:** Compiler forces you to `try-catch` or `throws`.
    *   **Philosophy:** "You must acknowledge this might fail."
*   **Unchecked Exceptions (`RuntimeException` subclass):**
    *   **Intent:** Represent programming errors (NullPointer, IndexOutOfBounds).
    *   **Rule:** Compiler does not enforce handling.
    *   **Philosophy:** "Fix your code, don't catch this."

**Why both?** To distinguish between "system failure you can't predict but should handle" (Checked) vs "developer incompetence/logic error" (Unchecked).

## 2. throw vs throws.

*   **`throw`**:
    *   Used **inside a method**.
    *   Actually throws the exception instance.
    *   `if (age < 18) throw new IllegalArgumentException("Too young");`
*   **`throws`**:
    *   Used in **method signature**.
    *   Declares that this method *might* throw these exceptions only (mainly for Checked exceptions).
    *   `public void readFile() throws IOException { ... }`

## 3. What happens if finally has a return?

**It overrides everything.**
If the `try` block returns 10, but the `finally` block returns 20, the method returns **20**. The `finally` block creates a "pending" return that overwrites the previous one. This is considered bad practice (swallows exceptions if they occurred in try).

```java
try {
    return 1;
} finally {
    return 2; // Method returns 2
}
```

## 4. Difference between Error and Exception.

They both extend `Throwable`.

*   **`Exception`**: Conditions that a reasonable application might want to catch and recover from (e.g., JSON parse error).
*   **`Error`**: Serious problems that a reasonable application should **not** try to catch (e.g., `OutOfMemoryError`, `StackOverflowError`). Usually indicates JVM trouble.

## 5. How do you design custom exceptions for a service layer?

1.  **Hierarchy:** Create a base `BaseServiceException` (Runtime or Checked depending on philosophy).
2.  **Specificity:** Create specific subclasses: `UserNotFoundException`, `InsufficientFundsException`.
3.  **Context:** Add fields to hold metadata (errorCode, userId) for easier debugging/logging.
4.  **Wrappers:** When catching low-level exceptions (SQLException), wrap them in your high-level custom exception to avoid leaking implementation details.

```java
public class ServiceException extends RuntimeException {
    private String errorCode;
    public ServiceException(String msg, String code) { super(msg); this.errorCode = code; }
}
```
