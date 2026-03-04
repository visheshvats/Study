# Module 1: SOLID Refresher + Strategy Pattern

## ⚡ SOLID Quick Reference

| Principle | One-liner | E-commerce Example |
|-----------|-----------|-------------------|
| **S**ingle Responsibility | One class = one reason to change | `OrderService` handles orders, not emails |
| **O**pen/Closed | Open for extension, closed for modification | Add new `PaymentMethod` without touching existing code |
| **L**iskov Substitution | Subtypes must be substitutable for base types | `CreditCardPayment` works wherever `Payment` is expected |
| **I**nterface Segregation | Many specific interfaces > one fat interface | `Payable`, `Refundable` instead of `IDoEverything` |
| **D**ependency Inversion | Depend on abstractions, not concretions | Inject `PaymentGateway` interface, not `StripeGateway` class |

> 💡 **Interview Tip:** SOLID violations are the #1 reason patterns exist. Strategy fixes OCP violations.

---

## 🎯 Pattern 1: Strategy

### What Problem It Solves
Eliminates `if-else` / `switch` hell when you have **multiple algorithms** for the same task. Makes adding new behaviors trivial without modifying existing code (OCP!).

### When to Use / When NOT to Use

| ✅ Use When | ❌ Avoid When |
|-------------|--------------|
| Multiple algorithms for same operation | Only 2-3 fixed options that never change |
| Algorithms change independently | Algorithm is trivial (just use a lambda) |
| Need runtime algorithm switching | Adds complexity for no benefit |

### UML Diagram (ASCII)

```
┌─────────────────┐         ┌────────────────────┐
│     Context     │────────▶│  <<interface>>     │
│ (OrderService)  │         │  PricingStrategy   │
├─────────────────┤         ├────────────────────┤
│ -strategy       │         │ +calculatePrice()  │
│ +setStrategy()  │         └────────────────────┘
│ +executeStrategy│                   △
└─────────────────┘                   │
                        ┌─────────────┼─────────────┐
                        │             │             │
               ┌────────┴───┐  ┌──────┴─────┐  ┌────┴────────┐
               │ RegularPrice│  │ VIPDiscount│  │ FlashSale   │
               └────────────┘  └────────────┘  └─────────────┘
```

---

## Code Examples

### Strategy Interface

```java
public interface PricingStrategy {
    double calculatePrice(double basePrice, int quantity);
}
```

### Concrete Strategies

```java
public class RegularPricing implements PricingStrategy {
    @Override
    public double calculatePrice(double basePrice, int quantity) {
        return basePrice * quantity;
    }
}

public class VIPPricing implements PricingStrategy {
    private static final double DISCOUNT = 0.15; // 15% off
    
    @Override
    public double calculatePrice(double basePrice, int quantity) {
        return basePrice * quantity * (1 - DISCOUNT);
    }
}

public class FlashSalePricing implements PricingStrategy {
    private static final double DISCOUNT = 0.30; // 30% off
    
    @Override
    public double calculatePrice(double basePrice, int quantity) {
        return basePrice * quantity * (1 - DISCOUNT);
    }
}
```

### Context Class

```java
public class OrderService {
    private PricingStrategy pricingStrategy;
    
    public OrderService(PricingStrategy pricingStrategy) {
        this.pricingStrategy = pricingStrategy;
    }
    
    public void setPricingStrategy(PricingStrategy pricingStrategy) {
        this.pricingStrategy = pricingStrategy;
    }
    
    public double calculateOrderTotal(double basePrice, int quantity) {
        return pricingStrategy.calculatePrice(basePrice, quantity);
    }
}
```

### Demo

```java
public class StrategyDemo {
    public static void main(String[] args) {
        OrderService orderService = new OrderService(new RegularPricing());
        
        double basePrice = 100.0;
        int quantity = 3;
        
        System.out.println("Regular: $" + orderService.calculateOrderTotal(basePrice, quantity));
        // Output: Regular: $300.0
        
        orderService.setPricingStrategy(new VIPPricing());
        System.out.println("VIP: $" + orderService.calculateOrderTotal(basePrice, quantity));
        // Output: VIP: $255.0
        
        orderService.setPricingStrategy(new FlashSalePricing());
        System.out.println("Flash Sale: $" + orderService.calculateOrderTotal(basePrice, quantity));
        // Output: Flash Sale: $210.0
    }
}
```

---

## Spring Boot Integration

```java
@Service
public class PricingService {
    private final Map<String, PricingStrategy> strategies;
    
    // Spring injects ALL PricingStrategy implementations automatically!
    public PricingService(List<PricingStrategy> strategyList) {
        this.strategies = strategyList.stream()
            .collect(Collectors.toMap(
                s -> s.getClass().getSimpleName().replace("Pricing", "").toUpperCase(),
                Function.identity()
            ));
    }
    
    public double calculate(String customerType, double price, int qty) {
        return strategies.getOrDefault(customerType, new RegularPricing())
                         .calculatePrice(price, qty);
    }
}

// Mark each strategy as a Spring component
@Component
public class VIPPricing implements PricingStrategy { ... }
```

> 🔑 **Spring Boot Magic:** Constructor injection with `List<Interface>` auto-collects all beans!

---

## Pitfalls & Anti-patterns

| ❌ Pitfall | ✅ Fix |
|-----------|-------|
| Too many tiny strategies | Combine related logic; use lambdas for trivial cases |
| Strategy knows about Context | Keep strategies stateless and independent |
| Hardcoding strategy selection | Use factory or Spring DI to select strategies |
| Not using `@FunctionalInterface` | For single-method strategies, leverage lambdas |

---

## 🎤 Interview Questions

### Q1: How does Strategy differ from State pattern?
> Both change behavior at runtime, but **Strategy** lets the client choose the algorithm explicitly, while **State** transitions happen internally based on object's state. Strategy = "I want this algorithm", State = "My state determines my behavior".

### Q2: Can you implement Strategy with lambdas in Java 8+?
> Yes! If the strategy interface has one method, mark it `@FunctionalInterface` and pass lambdas:
> ```java
> OrderService order = new OrderService((price, qty) -> price * qty * 0.9);
> ```

### Q3: How would you inject strategies in Spring Boot without `if-else`?
> Use constructor injection with `List<Strategy>` or `Map<String, Strategy>`. Spring collects all beans implementing the interface. Use `@Qualifier` or a naming convention to select at runtime.

---

## 📝 Practice Task: ShippingStrategy

Implement a `ShippingStrategy` for e-commerce:

1. Create interface `ShippingStrategy` with `double calculateCost(double weight, double distance)`
2. Implement 3 strategies:
   - `StandardShipping` → $5 base + $0.50/kg + $0.10/km
   - `ExpressShipping` → $15 base + $1.00/kg + $0.25/km  
   - `FreeShipping` → $0
3. Create `ShippingService` using strategy injection
4. Write a `main()` demo

---

*Next: Observer Pattern*
