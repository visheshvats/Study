# Mini-Quiz #1: Answers

## Strategy, Observer, Command

---

## Question 1: Pattern Identification

**Answer: Strategy Pattern**

**Why:**
- Multiple algorithms (Regular, Prime, VIP shipping calculations)
- Need to swap at runtime
- Client chooses which algorithm to use

```java
interface ShippingStrategy {
    double calculate(double weight, double distance);
}

class RegularShipping implements ShippingStrategy { }
class PrimeShipping implements ShippingStrategy { }
class VIPShipping implements ShippingStrategy { }
```

> ❌ NOT Observer (no event notification needed)  
> ❌ NOT Command (no undo/queue needed)

---

## Question 2: Code Analysis

### a) What pattern?
**Observer Pattern**
- `PaymentProcessor` is the Subject
- `PaymentObserver` list are the Observers
- `onPaymentCompleted()` is the notification method

### b) Non-blocking in Spring Boot?

```java
@Component
public class EmailNotifier implements PaymentObserver {
    
    @Async  // ← Makes it non-blocking!
    @Override
    public void onPaymentCompleted(Payment p) {
        // Runs in separate thread
        emailService.sendReceipt(p);
    }
}

// Don't forget to enable async!
@SpringBootApplication
@EnableAsync
public class Application { }
```

---

## Question 3: True or False

| # | Statement | Answer | Explanation |
|---|-----------|--------|-------------|
| 1 | Strategy is useful for undo functionality | **FALSE** | Command pattern is for undo. Strategy swaps algorithms. |
| 2 | Observer creates tight coupling | **FALSE** | Observer creates LOOSE coupling. Subject only knows interface. |
| 3 | Command stores request as object | **TRUE** | That's the core purpose of Command pattern. |
| 4 | `@EventListener` implements Observer | **TRUE** | Spring's event system is Observer pattern. |
| 5 | Strategy and Command both encapsulate behavior, but Command stores state | **TRUE** | Command needs state to support undo/redo. |

---

## Question 4: Fill in the Blanks

| Pattern | Key Interface Method(s) | Stores State? |
|---------|------------------------|---------------|
| Strategy | `calculate()` / `execute()` (single method) | Usually **NO** (stateless) |
| Observer | `update()` / `onEvent()` | **NO** (stateless) |
| Command | `execute()` and `undo()` | **YES** (for undo) |

---

## Question 5: Design Challenge

### Pattern Combination: **Command + (optionally) Strategy**

```
┌─────────────────────────────────────────────────────────────┐
│                      AdminDashboard                          │
│                                                              │
│  ┌─────────────────┐    ┌──────────────────────────────┐   │
│  │ CommandInvoker  │    │      Command History         │   │
│  │ (max 10 items)  │───▶│ [Cmd1, Cmd2, ... Cmd10]     │   │
│  └────────┬────────┘    └──────────────────────────────┘   │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              <<interface>> PriceCommand             │   │
│  │  +execute()  +undo()                                │   │
│  └─────────────────────────────────────────────────────┘   │
│           △                          △                      │
│           │                          │                      │
│  ┌────────┴────────┐      ┌─────────┴──────────┐          │
│  │ChangePriceCmd   │      │BulkDiscountCmd     │          │
│  │-productId       │      │-productIds[]       │          │
│  │-oldPrice        │      │-oldPrices[]        │          │
│  │-newPrice        │      │-discountPercent    │          │
│  └─────────────────┘      └────────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Implementation:

```java
// Command with undo
public class ChangePriceCommand implements PriceCommand {
    private String productId;
    private double oldPrice;
    private double newPrice;
    
    @Override
    public void execute() {
        this.oldPrice = productService.getPrice(productId);
        productService.setPrice(productId, newPrice);
    }
    
    @Override
    public void undo() {
        productService.setPrice(productId, oldPrice);
    }
}

// Invoker with limited history
public class AdminCommandInvoker {
    private final Deque<PriceCommand> history = new ArrayDeque<>();
    private static final int MAX_HISTORY = 10;
    
    public void execute(PriceCommand cmd) {
        cmd.execute();
        history.push(cmd);
        if (history.size() > MAX_HISTORY) {
            history.removeLast();  // Remove oldest
        }
    }
    
    public void undo() {
        if (!history.isEmpty()) {
            history.pop().undo();
        }
    }
}
```

### Why this works:
- **Command** → Encapsulates each price change as an object
- **Undo support** → Each command stores old state
- **History limit** → Deque with max size of 10
- **Strategy (optional)** → If discount calculation varies (%, fixed amount, tiered)

---

## Score Yourself

| Questions Correct | Level |
|-------------------|-------|
| 5/5 | 🏆 Pattern Master! |
| 4/5 | 👍 Solid understanding |
| 3/5 | 📚 Review the missed patterns |
| <3 | 🔄 Re-read notes before continuing |

---

*Next up: Singleton Pattern (Creational) →*
