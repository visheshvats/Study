# Module 2: Observer Pattern

## 🎯 Pattern 2: Observer

### What Problem It Solves
Notifies multiple objects automatically when something changes. Eliminates tight coupling between the object that changes and objects that need to react. Perfect for **event-driven systems**.

### When to Use / When NOT to Use

| ✅ Use When | ❌ Avoid When |
|-------------|--------------|
| Multiple objects need to react to state changes | Only one listener exists (direct call is simpler) |
| Publishers shouldn't know about subscribers | Order of notification matters critically |
| Building event-driven/reactive systems | Update cascades could cause infinite loops |
| Decoupling UI from business logic | Simple synchronous updates suffice |

### UML Diagram (ASCII)

```
┌─────────────────────┐           ┌────────────────────────┐
│  <<interface>>      │           │    <<interface>>       │
│     Subject         │           │      Observer          │
├─────────────────────┤           ├────────────────────────┤
│ +attach(observer)   │◀─────────▶│ +update(event)         │
│ +detach(observer)   │           └────────────────────────┘
│ +notifyAll()        │                      △
└─────────────────────┘                      │
          △                     ┌────────────┼────────────┐
          │                     │            │            │
┌─────────┴──────────┐   ┌──────┴─────┐ ┌────┴────┐ ┌─────┴──────┐
│   OrderService     │   │EmailNotifier│ │ SMSAlert │ │InventoryMgr│
│ (ConcreteSubject)  │   └────────────┘ └──────────┘ └────────────┘
├────────────────────┤
│ -observers: List   │
│ -state             │
└────────────────────┘
```

---

## Code Examples

### Observer Interface

```java
// Generic event for flexibility
public interface OrderObserver {
    void onOrderEvent(OrderEvent event);
}

// Event object (immutable)
public record OrderEvent(
    String orderId,
    OrderStatus status,
    String customerEmail,
    double totalAmount
) {}

public enum OrderStatus {
    CREATED, PAID, SHIPPED, DELIVERED, CANCELLED
}
```

### Subject (Publisher)

```java
public class OrderService {
    private final List<OrderObserver> observers = new ArrayList<>();
    
    public void subscribe(OrderObserver observer) {
        observers.add(observer);
    }
    
    public void unsubscribe(OrderObserver observer) {
        observers.remove(observer);
    }
    
    private void notifyObservers(OrderEvent event) {
        for (OrderObserver observer : observers) {
            observer.onOrderEvent(event);
        }
    }
    
    // Business method that triggers notifications
    public void placeOrder(String orderId, String email, double amount) {
        // ... order logic ...
        System.out.println("Order " + orderId + " placed!");
        
        OrderEvent event = new OrderEvent(orderId, OrderStatus.CREATED, email, amount);
        notifyObservers(event);
    }
    
    public void shipOrder(String orderId, String email, double amount) {
        System.out.println("Order " + orderId + " shipped!");
        
        OrderEvent event = new OrderEvent(orderId, OrderStatus.SHIPPED, email, amount);
        notifyObservers(event);
    }
}
```

### Concrete Observers

```java
public class EmailNotifier implements OrderObserver {
    @Override
    public void onOrderEvent(OrderEvent event) {
        System.out.printf("📧 Sending email to %s: Order %s is %s%n",
            event.customerEmail(), event.orderId(), event.status());
    }
}

public class SMSNotifier implements OrderObserver {
    @Override
    public void onOrderEvent(OrderEvent event) {
        // Only notify for important statuses
        if (event.status() == OrderStatus.SHIPPED || 
            event.status() == OrderStatus.DELIVERED) {
            System.out.printf("📱 SMS: Your order %s has been %s%n",
                event.orderId(), event.status());
        }
    }
}

public class InventoryManager implements OrderObserver {
    @Override
    public void onOrderEvent(OrderEvent event) {
        if (event.status() == OrderStatus.CREATED) {
            System.out.printf("📦 Reserving inventory for order %s%n", event.orderId());
        } else if (event.status() == OrderStatus.CANCELLED) {
            System.out.printf("📦 Releasing inventory for order %s%n", event.orderId());
        }
    }
}

public class AnalyticsTracker implements OrderObserver {
    @Override
    public void onOrderEvent(OrderEvent event) {
        System.out.printf("📊 Analytics: Order %s | Status: %s | Amount: $%.2f%n",
            event.orderId(), event.status(), event.totalAmount());
    }
}
```

### Demo

```java
public class ObserverDemo {
    public static void main(String[] args) {
        OrderService orderService = new OrderService();
        
        // Subscribe observers
        orderService.subscribe(new EmailNotifier());
        orderService.subscribe(new SMSNotifier());
        orderService.subscribe(new InventoryManager());
        orderService.subscribe(new AnalyticsTracker());
        
        // Place an order - all observers get notified
        orderService.placeOrder("ORD-001", "john@example.com", 299.99);
        
        System.out.println("\n--- Shipping Order ---\n");
        
        // Ship order - observers react differently
        orderService.shipOrder("ORD-001", "john@example.com", 299.99);
    }
}
```

**Output:**
```
Order ORD-001 placed!
📧 Sending email to john@example.com: Order ORD-001 is CREATED
📦 Reserving inventory for order ORD-001
📊 Analytics: Order ORD-001 | Status: CREATED | Amount: $299.99

--- Shipping Order ---

Order ORD-001 shipped!
📧 Sending email to john@example.com: Order ORD-001 is SHIPPED
📱 SMS: Your order ORD-001 has been SHIPPED
📊 Analytics: Order ORD-001 | Status: SHIPPED | Amount: $299.99
```

---

## Spring Boot Integration

### Using ApplicationEventPublisher (Built-in Observer!)

```java
// 1. Define the Event
public class OrderCreatedEvent extends ApplicationEvent {
    private final String orderId;
    private final String customerEmail;
    private final double amount;
    
    public OrderCreatedEvent(Object source, String orderId, String email, double amount) {
        super(source);
        this.orderId = orderId;
        this.customerEmail = email;
        this.amount = amount;
    }
    // getters...
}

// 2. Publisher (Subject)
@Service
public class OrderService {
    private final ApplicationEventPublisher eventPublisher;
    
    public OrderService(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }
    
    public void placeOrder(String orderId, String email, double amount) {
        // ... business logic ...
        eventPublisher.publishEvent(new OrderCreatedEvent(this, orderId, email, amount));
    }
}

// 3. Observers (Listeners) - Spring discovers these automatically!
@Component
public class EmailNotificationListener {
    
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        System.out.println("📧 Sending email for order: " + event.getOrderId());
    }
}

@Component
public class InventoryListener {
    
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        System.out.println("📦 Reserving inventory for: " + event.getOrderId());
    }
}

// 4. Async Observers (non-blocking)
@Component
public class AnalyticsListener {
    
    @Async
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        // Runs in separate thread - doesn't block order placement
        System.out.println("📊 Tracking analytics asynchronously...");
    }
}
```

> 🔑 **Spring Tip:** Use `@Async` + `@EnableAsync` for observers that shouldn't block the main flow!

### Using @TransactionalEventListener

```java
@Component
public class EmailListener {
    
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void sendEmail(OrderCreatedEvent event) {
        // Only sends email AFTER transaction commits successfully
        // Prevents sending emails for rolled-back orders!
    }
}
```

---

## Pitfalls & Anti-patterns

| ❌ Pitfall | ✅ Fix |
|-----------|-------|
| Memory leaks (observers not unsubscribed) | Use `WeakReference` or ensure cleanup |
| Observer modifies subject during update | Make events immutable; queue changes |
| Notification order dependency | Document order or use priority system |
| Long-running observers block publisher | Use `@Async` or message queues |
| Too fine-grained events | Batch events or use debouncing |
| Circular notifications | Track notification state; use flags |

---

## 🎤 Interview Questions

### Q1: What's the difference between Observer and Pub/Sub?
> **Observer** is typically in-process with direct references between subject and observers. **Pub/Sub** uses a message broker/channel as intermediary, enabling cross-process/network communication. Pub/Sub is more decoupled but adds infrastructure complexity.

### Q2: How does Spring's `@EventListener` implement Observer?
> Spring's `ApplicationEventPublisher` is the Subject. Classes with `@EventListener` methods are discovered via component scanning and registered as observers. When `publishEvent()` is called, Spring iterates through all matching listeners and invokes them. Use `@Async` for non-blocking notifications.

### Q3: How do you prevent memory leaks with observers?
> 1. Always provide an `unsubscribe()` mechanism and call it during cleanup
> 2. Use `WeakReference<Observer>` in the subject's list
> 3. In Spring, listeners tied to `@Component` lifecycle are managed automatically
> 4. For manual observers, implement `DisposableBean` or use `@PreDestroy`

---

## 📝 Practice Task: StockPriceObserver

Build a stock price notification system:

1. Create `StockPriceSubject` that tracks a stock symbol and price
2. Create interface `StockObserver` with `onPriceChange(symbol, oldPrice, newPrice)`
3. Implement observers:
   - `PriceAlertObserver` → prints alert if price changes > 5%
   - `LoggingObserver` → logs every price change
   - `TradingBotObserver` → prints "BUY" if price drops > 10%, "SELL" if rises > 10%
4. Demo with price updates: $100 → $95 → $85 → $90

---

## Strategy vs Observer Quick Comparison

| Aspect | Strategy | Observer |
|--------|----------|----------|
| **Purpose** | Choose algorithm | React to changes |
| **Relationship** | 1 context → 1 strategy | 1 subject → N observers |
| **Who initiates** | Client selects strategy | Subject notifies automatically |
| **Spring use** | Multiple `@Component` implementations | `@EventListener` |

---

*Next: Command Pattern → Then Mini-Quiz #1!*
