# Module 3: Command Pattern

## 🎯 Pattern 3: Command

### What Problem It Solves
Encapsulates a request as an object, allowing you to **parameterize, queue, log, and undo** operations. Decouples the invoker (button, scheduler) from the receiver (actual business logic).

### When to Use / When NOT to Use

| ✅ Use When | ❌ Avoid When |
|-------------|--------------|
| Need undo/redo functionality | Simple direct method calls suffice |
| Queue or schedule operations | No need for history/queuing |
| Log/audit all operations | Adds unnecessary complexity |
| Implement transactions/macros | One-off operations |
| Decouple invoker from receiver | Tight coupling is acceptable |

### UML Diagram (ASCII)

```
┌─────────────┐       ┌────────────────────┐
│   Invoker   │──────▶│   <<interface>>    │
│ (Controller)│       │      Command       │
└─────────────┘       ├────────────────────┤
                      │ +execute()         │
                      │ +undo()            │
                      └────────────────────┘
                                 △
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
   ┌────────┴───────┐  ┌─────────┴────────┐  ┌───────┴────────┐
   │ PlaceOrderCmd  │  │ CancelOrderCmd   │  │ RefundOrderCmd │
   ├────────────────┤  ├──────────────────┤  ├────────────────┤
   │ -receiver      │  │ -receiver        │  │ -receiver      │
   │ -orderData     │  │ -orderId         │  │ -orderId       │
   │ +execute()     │  │ +execute()       │  │ +execute()     │
   │ +undo()        │  │ +undo()          │  │ +undo()        │
   └────────┬───────┘  └──────────────────┘  └────────────────┘
            │
            ▼
   ┌────────────────┐
   │   Receiver     │
   │ (OrderService) │
   └────────────────┘
```

---

## Code Examples

### Command Interface

```java
public interface OrderCommand {
    void execute();
    void undo();
}
```

### Concrete Commands

```java
// Place Order Command
public class PlaceOrderCommand implements OrderCommand {
    private final OrderService orderService;
    private final OrderRequest orderRequest;
    private String createdOrderId;  // For undo
    
    public PlaceOrderCommand(OrderService orderService, OrderRequest orderRequest) {
        this.orderService = orderService;
        this.orderRequest = orderRequest;
    }
    
    @Override
    public void execute() {
        this.createdOrderId = orderService.createOrder(orderRequest);
        System.out.println("Order created: " + createdOrderId);
    }
    
    @Override
    public void undo() {
        if (createdOrderId != null) {
            orderService.cancelOrder(createdOrderId);
            System.out.println("Order cancelled: " + createdOrderId);
        }
    }
}

// Cancel Order Command
public class CancelOrderCommand implements OrderCommand {
    private final OrderService orderService;
    private final String orderId;
    private Order previousState;  // For undo
    
    public CancelOrderCommand(OrderService orderService, String orderId) {
        this.orderService = orderService;
        this.orderId = orderId;
    }
    
    @Override
    public void execute() {
        this.previousState = orderService.getOrder(orderId);
        orderService.cancelOrder(orderId);
        System.out.println("Order cancelled: " + orderId);
    }
    
    @Override
    public void undo() {
        if (previousState != null) {
            orderService.restoreOrder(previousState);
            System.out.println("Order restored: " + orderId);
        }
    }
}

// Apply Discount Command
public class ApplyDiscountCommand implements OrderCommand {
    private final OrderService orderService;
    private final String orderId;
    private final double discountPercent;
    private double previousTotal;
    
    public ApplyDiscountCommand(OrderService orderService, String orderId, double discountPercent) {
        this.orderService = orderService;
        this.orderId = orderId;
        this.discountPercent = discountPercent;
    }
    
    @Override
    public void execute() {
        this.previousTotal = orderService.getOrderTotal(orderId);
        orderService.applyDiscount(orderId, discountPercent);
        System.out.printf("Applied %.0f%% discount to order %s%n", discountPercent, orderId);
    }
    
    @Override
    public void undo() {
        orderService.setOrderTotal(orderId, previousTotal);
        System.out.println("Discount reverted for order: " + orderId);
    }
}
```

### Invoker with History (Undo/Redo)

```java
public class OrderCommandInvoker {
    private final Deque<OrderCommand> history = new ArrayDeque<>();
    private final Deque<OrderCommand> redoStack = new ArrayDeque<>();
    
    public void executeCommand(OrderCommand command) {
        command.execute();
        history.push(command);
        redoStack.clear();  // Clear redo after new command
    }
    
    public void undo() {
        if (!history.isEmpty()) {
            OrderCommand command = history.pop();
            command.undo();
            redoStack.push(command);
        } else {
            System.out.println("Nothing to undo!");
        }
    }
    
    public void redo() {
        if (!redoStack.isEmpty()) {
            OrderCommand command = redoStack.pop();
            command.execute();
            history.push(command);
        } else {
            System.out.println("Nothing to redo!");
        }
    }
}
```

### Demo

```java
public class CommandDemo {
    public static void main(String[] args) {
        OrderService orderService = new OrderService();
        OrderCommandInvoker invoker = new OrderCommandInvoker();
        
        // Execute commands
        OrderRequest request = new OrderRequest("user123", List.of("item1", "item2"));
        invoker.executeCommand(new PlaceOrderCommand(orderService, request));
        // Output: Order created: ORD-001
        
        invoker.executeCommand(new ApplyDiscountCommand(orderService, "ORD-001", 10));
        // Output: Applied 10% discount to order ORD-001
        
        // Undo last command
        invoker.undo();
        // Output: Discount reverted for order: ORD-001
        
        // Redo
        invoker.redo();
        // Output: Applied 10% discount to order ORD-001
        
        // Undo all
        invoker.undo();
        invoker.undo();
        // Output: Discount reverted...
        // Output: Order cancelled: ORD-001
    }
}
```

---

## Spring Boot Integration

### Using Command Pattern with REST Controller

```java
// Command Registry - Factory for commands
@Component
public class OrderCommandFactory {
    
    private final OrderService orderService;
    
    public OrderCommandFactory(OrderService orderService) {
        this.orderService = orderService;
    }
    
    public OrderCommand createPlaceOrderCommand(OrderRequest request) {
        return new PlaceOrderCommand(orderService, request);
    }
    
    public OrderCommand createCancelCommand(String orderId) {
        return new CancelOrderCommand(orderService, orderId);
    }
    
    public OrderCommand createDiscountCommand(String orderId, double percent) {
        return new ApplyDiscountCommand(orderService, orderId, percent);
    }
}

// Invoker as a Service (with session-based history)
@Service
@Scope(value = "session", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class SessionCommandInvoker extends OrderCommandInvoker {
    // Each user session has its own undo history!
}

// Controller uses Command pattern
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    private final OrderCommandFactory commandFactory;
    private final SessionCommandInvoker invoker;
    
    @PostMapping
    public ResponseEntity<String> createOrder(@RequestBody OrderRequest request) {
        OrderCommand cmd = commandFactory.createPlaceOrderCommand(request);
        invoker.executeCommand(cmd);
        return ResponseEntity.ok("Order created");
    }
    
    @PostMapping("/{orderId}/discount")
    public ResponseEntity<String> applyDiscount(
            @PathVariable String orderId,
            @RequestParam double percent) {
        OrderCommand cmd = commandFactory.createDiscountCommand(orderId, percent);
        invoker.executeCommand(cmd);
        return ResponseEntity.ok("Discount applied");
    }
    
    @PostMapping("/undo")
    public ResponseEntity<String> undoLastAction() {
        invoker.undo();
        return ResponseEntity.ok("Last action undone");
    }
    
    @PostMapping("/redo")
    public ResponseEntity<String> redoLastAction() {
        invoker.redo();
        return ResponseEntity.ok("Action redone");
    }
}
```

### Async Command Execution (Job Queue)

```java
@Service
public class AsyncCommandExecutor {
    
    private final BlockingQueue<OrderCommand> commandQueue = new LinkedBlockingQueue<>();
    
    @Async
    @Scheduled(fixedDelay = 100)
    public void processCommands() {
        OrderCommand command = commandQueue.poll();
        if (command != null) {
            try {
                command.execute();
            } catch (Exception e) {
                command.undo();  // Compensate on failure
            }
        }
    }
    
    public void queueCommand(OrderCommand command) {
        commandQueue.offer(command);
    }
}
```

---

## Pitfalls & Anti-patterns

| ❌ Pitfall | ✅ Fix |
|-----------|-------|
| Commands with too much logic | Keep execute() thin; delegate to receiver |
| Not storing enough state for undo | Save all state needed to revert |
| Memory leak from infinite history | Limit history size (e.g., last 50 commands) |
| Undo in wrong order | Use stack (LIFO) for history |
| Commands holding stale references | Use IDs instead of object references |

---

## 🎤 Interview Questions

### Q1: How is Command different from Strategy?
> **Strategy** swaps algorithms for the SAME operation. **Command** encapsulates DIFFERENT operations as objects. Strategy = "different ways to calculate price", Command = "different actions like create, cancel, refund".

### Q2: Real-world examples of Command pattern?
> 1. **Runnable/Callable** in Java - encapsulates task to execute later
> 2. **Transaction rollback** - commands with compensating actions
> 3. **GUI undo/redo** - text editors, Photoshop
> 4. **Message queues** - messages are commands to process
> 5. **Spring Batch jobs** - each step is a command

### Q3: How would you implement macro recording using Command?
> Store executed commands in a list. To replay the macro, iterate and call `execute()` on each:
> ```java
> List<Command> macro = new ArrayList<>();
> macro.add(new SelectAllCommand());
> macro.add(new CopyCommand());
> macro.add(new PasteCommand());
> // Replay
> macro.forEach(Command::execute);
> ```

---

## 📝 Practice Task: TextEditorCommands

Build a simple text editor with undo/redo:

1. Create `TextEditor` class with a `StringBuilder content` and methods:
   - `insert(int position, String text)`
   - `delete(int start, int end)`
   - `getText()`
2. Create `EditorCommand` interface with `execute()` and `undo()`
3. Implement:
   - `InsertCommand` - inserts text at position
   - `DeleteCommand` - deletes text between positions (store deleted text for undo!)
4. Create `EditorInvoker` with undo/redo stacks
5. Demo: Insert "Hello World", delete "World", undo, redo

---

## Pattern Comparison Table

| Aspect | Strategy | Observer | Command |
|--------|----------|----------|---------|
| **Purpose** | Swap algorithms | React to changes | Encapsulate requests |
| **Key feature** | Runtime algorithm selection | Pub/Sub notification | Undo/queue/log |
| **Relationship** | 1:1 (context:strategy) | 1:N (subject:observers) | N:1 (commands:receiver) |
| **State** | Usually stateless | Stateless observers | Stateful (for undo) |
| **Spring example** | Multiple service impls | `@EventListener` | `Runnable`, transactions |

---

*Completed 3 patterns! → Mini-Quiz #1 is next!*
