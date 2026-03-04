# Round 2 — OOP + Design Thinking

## 1. Explain encapsulation with a practical example.

**Encapsulation** is bundling data (variables) and methods (behavior) together and restricting direct access to the object's internal state. It protects integrity.

**Example: Bank Account**
*   **Bad:** `account.balance = -500;` (Direct access allows invalid state).
*   **Good (Encapsulated):**
    *   field `private double balance;`
    *   method `public void withdraw(double amount) { if(amount > 0 && amount <= balance) balance -= amount; }`
    
Encapsulation ensures the `balance` can never be negative or modified arbitrarily without validation logic.

## 2. Explain polymorphism beyond “method overriding”.

Polymorphism = "Many Forms".
1.  **Ad-hoc Polymorphism (Overloading):** `print(int i)` vs `print(String s)`. Same name, different logic based on types.
2.  **Subtype Polymorphism (Overriding):** `Animal a = new Dog(); a.makeSound();` (Calls Dog's version).
3.  **Parametric Polymorphism (Generics):** `List<T>` works for `List<String>`, `List<Integer>`, etc. The code "takes on the form" of the type provided.
4.  **Coercion Polymorphism:** Automatic casting, e.g., `double d = 5;` (int 5 behaves as double 5.0).

## 3. What is the Liskov Substitution Principle (LSP) in simple terms?

**Definition:** Subtypes must be substitutable for their base types without breaking the application.
**Simple Rule:** If it looks like a Duck (Parent) and quacks like a Duck, but needs batteries (Child), you have violated LSP.

**Violation Example:**
*   Class `Rectangle { setWidth, setHeight }`
*   Class `Square extends Rectangle`.
*   If you have a function `resize(Rectangle r)` that sets width to 10 and expects height to stay same, passing a `Square` (where setting width also changes height) will break the logic.

A subclass should extend capability, not reduce it or change the rules of the parent.

## 4. How would you model a Bank Account class to avoid invalid states?
Use **Encapsulation + Invariants**.
```java
public class BankAccount {
    private final String accountNumber; // Immutable identity
    private BigDecimal balance; // BigDecimal for money (never double!)

    public BankAccount(String accNum, BigDecimal initialDeposit) {
        if (initialDeposit.compareTo(BigDecimal.ZERO) < 0) throw new IllegalArgumentException("No debt allowed");
        this.accountNumber = accNum;
        this.balance = initialDeposit;
    }

    public synchronized void deposit(BigDecimal amount) {
        if (amount.signum() <= 0) throw new IllegalArgumentException("Must deposit positive amount");
        balance = balance.add(amount);
    }
    
    // Withdraw check essentially prevents invalid state (negative balance) ...
}
```

## 5. Where would you use the Strategy pattern in real apps?

**Strategy:** Defines a family of algorithms, encapsulates each one, and makes them interchangeable.

**Real Application:** Payment Processing.
*   **Interface:** `PaymentStrategy { pay(amount); }`
*   **Impls:** `CreditCardStrategy`, `PayPalStrategy`, `CryptoStrategy`.
*   **Usage:** The ShoppingCart class takes a `PaymentStrategy` at runtime. user clicks "Pay with PayPal", we inject the PayPal strategy. We don't need `if (type == PAYPAL)` logic everywhere.

## 6. Explain Factory vs Builder and when each is better.

*   **Factory Pattern:**
    *   **Focus:** Creating a single object instance, hiding the complex instantiation logic or subclass selection.
    *   **Use when:** You have a hierarchy (Shape -> Circle, Square) and want to decouple the client from the specific class. `Shape s = ShapeFactory.getShape("CIRCLE");`
*   **Builder Pattern:**
    *   **Focus:** Constructing a complex object step-by-step.
    *   **Use when:** Object has many parameters (some optional). Avoids "Telescoping Constructor" problem (`new Pizza(size, cheese, pepperoni, null, null, null...)`).
    *   `Pizza p = new Pizza.Builder().setSize("L").addCheese().build();`

## 7. What is the difference between DTO vs Entity vs VO?

*   **Entity:**
    *   Has an Identity (ID). Mutable.
    *   Mapped to a DB table (JPA/Hibernate).
    *   Lifecycle managed by persistence context.
    *   Ex: `User` table row.
*   **VO (Value Object):**
    *   No Identity. Defined by its attributes. Immutable.
    *   Equality based on values.
    *   Ex: `Money(10, "USD")`, `GPS(lat, lon)`. `Money(10, "USD")` is equal to another `Money(10, "USD")`.
*   **DTO (Data Transfer Object):**
    *   Pojo container to move data between processes/layers (e.g., Backend -> Frontend).
    *   No business logic. Can be a flat projection of multiple Entities.
    *   Ex: `UserProfileDTO` (contains specific fields from User entity + Address entity).
