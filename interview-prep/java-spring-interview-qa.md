# Java & Spring Boot Interview Q&A

---

## 🔹 Spring / Spring Boot

### 1. How can we change the language of a Java application using Locale and MessageSource?

```java
// 1. Create message property files
// src/main/resources/messages.properties (default)
greeting=Hello
// src/main/resources/messages_fr.properties
greeting=Bonjour
// src/main/resources/messages_hi.properties
greeting=नमस्ते

// 2. Configure MessageSource (auto-configured in Spring Boot)
@Configuration
public class LocaleConfig {
    
    @Bean
    public LocaleResolver localeResolver() {
        SessionLocaleResolver resolver = new SessionLocaleResolver();
        resolver.setDefaultLocale(Locale.ENGLISH);
        return resolver;
    }
    
    @Bean
    public LocaleChangeInterceptor localeChangeInterceptor() {
        LocaleChangeInterceptor interceptor = new LocaleChangeInterceptor();
        interceptor.setParamName("lang"); // ?lang=fr
        return interceptor;
    }
}

// 3. Use MessageSource in controller
@RestController
public class GreetingController {
    
    @Autowired
    private MessageSource messageSource;
    
    @GetMapping("/greet")
    public String greet(Locale locale) {
        return messageSource.getMessage("greeting", null, locale);
    }
}
```

**Usage:** `GET /greet?lang=fr` → returns "Bonjour"

---

### 2. Does Locale get initialized automatically in a Spring Boot controller?

**Yes!** Spring automatically resolves `Locale` from:
1. `Accept-Language` header (default)
2. Session attribute (if `SessionLocaleResolver` configured)
3. Cookie (if `CookieLocaleResolver` configured)
4. URL parameter (if `LocaleChangeInterceptor` configured)

```java
@GetMapping("/greet")
public String greet(Locale locale) {  // Auto-injected by Spring!
    return messageSource.getMessage("greeting", null, locale);
}
```

---

### 3. How to install Spring Tool Suite (STS) on Ubuntu?

```bash
# Method 1: Snap (Recommended)
sudo snap install spring-tool-suite --classic

# Method 2: Download manually
wget https://download.springsource.com/release/STS4/4.x.x/dist/e4.xx/spring-tool-suite-4-x.x.x.RELEASE-linux.gtk.x86_64.tar.gz
tar -xvzf spring-tool-suite-*.tar.gz
cd sts-4.x.x.RELEASE
./SpringToolSuite4

# Method 3: As Eclipse Plugin
# In Eclipse: Help → Eclipse Marketplace → Search "Spring Tools"
```

---

### 4. What is the difference between @Component and @Service?

| Aspect | @Component | @Service |
|--------|------------|----------|
| **Purpose** | Generic stereotype for any Spring bean | Semantic marker for service layer |
| **Functionality** | Identical (both are beans) | Identical |
| **Why use @Service?** | - | Code readability, AOP targeting, future Spring features |

```java
@Component  // Generic - use for utilities, helpers
public class EmailValidator { }

@Service    // Semantic - indicates business logic layer
public class OrderService { }
```

> 💡 **Rule:** Use `@Service` for business logic, `@Repository` for DAO, `@Component` for everything else.

---

### 5. What is the difference between @Controller and @RestController?

| Aspect | @Controller | @RestController |
|--------|-------------|-----------------|
| **Returns** | View name (HTML template) | Response body (JSON/XML) |
| **Equivalent to** | `@Controller` | `@Controller` + `@ResponseBody` |
| **Use case** | MVC web apps | REST APIs |

```java
@Controller
public class WebController {
    @GetMapping("/home")
    public String home(Model model) {
        return "home";  // Returns view: home.html
    }
}

@RestController
public class ApiController {
    @GetMapping("/api/users")
    public List<User> getUsers() {
        return userService.findAll();  // Returns JSON
    }
}
```

---

### 6. What are bean scopes in Spring Boot?

| Scope | Description | Use Case |
|-------|-------------|----------|
| **singleton** (default) | One instance per Spring container | Stateless services |
| **prototype** | New instance every injection | Stateful objects |
| **request** | One instance per HTTP request | Request-scoped data |
| **session** | One instance per HTTP session | User session data |
| **application** | One instance per ServletContext | App-wide config |
| **websocket** | One instance per WebSocket | WebSocket handlers |

```java
@Component
@Scope("prototype")
public class ShoppingCart { }

@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestContext { }
```

---

### 7. How is a prototype bean handled inside Spring context when injected into a singleton bean?

**Problem:** Prototype bean is created ONCE when singleton is instantiated, defeating the purpose.

```java
@Service  // Singleton
public class OrderService {
    @Autowired
    private ShoppingCart cart;  // ❌ Same cart instance always!
}
```

**Solutions:**

```java
// Solution 1: ObjectFactory / ObjectProvider
@Service
public class OrderService {
    @Autowired
    private ObjectProvider<ShoppingCart> cartProvider;
    
    public void process() {
        ShoppingCart cart = cartProvider.getObject();  // New instance each time
    }
}

// Solution 2: Lookup method injection
@Service
public abstract class OrderService {
    @Lookup
    protected abstract ShoppingCart getCart();  // Spring overrides this
}

// Solution 3: Scoped Proxy
@Component
@Scope(value = "prototype", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class ShoppingCart { }
```

---

### 8. What is Singleton in Spring Boot?

**Spring Singleton ≠ GoF Singleton Pattern**

| Aspect | GoF Singleton | Spring Singleton |
|--------|---------------|------------------|
| **Scope** | One per JVM/ClassLoader | One per Spring ApplicationContext |
| **Creation** | Private constructor + static | Spring container manages |
| **Multiple instances** | Not possible | Possible with multiple contexts |

```java
// Spring Singleton (default scope)
@Service
public class OrderService { }  // One instance per Spring context

// Traditional Singleton (not recommended in Spring)
public class LegacySingleton {
    private static final LegacySingleton INSTANCE = new LegacySingleton();
    private LegacySingleton() {}
    public static LegacySingleton getInstance() { return INSTANCE; }
}
```

> 💡 **Best Practice:** Let Spring manage singletons; don't create manual singletons.

---

## 🔹 Core Java

### 9. What is the difference between sleep() and wait() in threads?

| Aspect | `sleep()` | `wait()` |
|--------|-----------|----------|
| **Class** | `Thread` | `Object` |
| **Lock release** | ❌ Keeps lock | ✅ Releases lock |
| **Wake up** | After time expires | `notify()` / `notifyAll()` |
| **Must be in synchronized** | No | Yes (must own monitor) |
| **Purpose** | Pause execution | Inter-thread communication |

```java
// sleep() - Just pause, keep lock
synchronized(lock) {
    Thread.sleep(1000);  // Still holds lock!
}

// wait() - Release lock and wait for signal
synchronized(lock) {
    lock.wait();  // Releases lock, waits for notify()
}
```

---

### 10. What is dynamic method dispatch in Java?

**Runtime polymorphism** where the method to call is determined at runtime based on the actual object type, not reference type.

```java
class Animal {
    void speak() { System.out.println("Animal speaks"); }
}

class Dog extends Animal {
    @Override
    void speak() { System.out.println("Dog barks"); }
}

public class Demo {
    public static void main(String[] args) {
        Animal animal = new Dog();  // Reference: Animal, Object: Dog
        animal.speak();  // Output: "Dog barks" (decided at runtime!)
    }
}
```

> JVM uses **vtable (virtual method table)** to resolve which method to call.

---

### 11. What is the diamond problem in Java and how is it resolved?

**Problem:** Multiple inheritance ambiguity when two parent classes have same method.

```
        Interface A
       /           \
  Interface B    Interface C
       \           /
        Class D (Diamond!)
```

**Java's Solution:**

```java
interface A {
    default void hello() { System.out.println("A"); }
}

interface B extends A {
    default void hello() { System.out.println("B"); }
}

interface C extends A {
    default void hello() { System.out.println("C"); }
}

// Must override to resolve ambiguity!
class D implements B, C {
    @Override
    public void hello() {
        B.super.hello();  // Explicitly choose B's implementation
        // Or provide own implementation
    }
}
```

**Rules:**
1. Class method wins over interface default method
2. More specific interface wins (child over parent)
3. If ambiguous, must override explicitly

---

### 12. Explain cloning in Java

Cloning creates a copy of an object using `Cloneable` interface and `clone()` method.

```java
public class Employee implements Cloneable {
    private String name;
    private Address address;  // Reference type
    
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();  // Shallow clone
    }
}

// Usage
Employee emp1 = new Employee("John", new Address("NYC"));
Employee emp2 = (Employee) emp1.clone();
```

**Requirements:**
1. Implement `Cloneable` marker interface
2. Override `clone()` method
3. Handle `CloneNotSupportedException`

---

### 13. What is the difference between shallow clone and deep clone?

| Aspect | Shallow Clone | Deep Clone |
|--------|---------------|------------|
| **Primitives** | Copied by value | Copied by value |
| **Objects** | Reference copied (same object) | New objects created |
| **Independence** | Changes reflect in both | Completely independent |

```java
// Shallow Clone (default)
@Override
protected Object clone() throws CloneNotSupportedException {
    return super.clone();  // address points to SAME object
}

// Deep Clone
@Override
protected Object clone() throws CloneNotSupportedException {
    Employee cloned = (Employee) super.clone();
    cloned.address = new Address(this.address.getCity());  // NEW object
    return cloned;
}
```

```
Shallow:  emp1.address ──┬──► [Address Object]
          emp2.address ──┘

Deep:     emp1.address ────► [Address Object 1]
          emp2.address ────► [Address Object 2]
```

---

### 14. Explain Singleton design pattern in Java and other common design patterns

**Singleton:** Ensures only one instance exists.

```java
// Thread-safe Singleton (Bill Pugh)
public class Singleton {
    private Singleton() {}
    
    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }
    
    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}

// Enum Singleton (Best - handles serialization)
public enum ConfigManager {
    INSTANCE;
    public void loadConfig() { }
}
```

**Other Common Patterns:**

| Pattern | Category | Purpose |
|---------|----------|---------|
| Factory Method | Creational | Create objects without specifying class |
| Builder | Creational | Step-by-step complex object construction |
| Adapter | Structural | Convert interface to another |
| Decorator | Structural | Add behavior dynamically |
| Strategy | Behavioral | Swap algorithms at runtime |
| Observer | Behavioral | Notify on state changes |

---

### 15. What is Adapter design pattern and where is it used?

**Purpose:** Converts one interface to another that client expects.

```java
// Legacy system
class OldPaymentGateway {
    void processOldPayment(String cardNumber, double amount) { }
}

// New interface we want to use
interface PaymentProcessor {
    void pay(PaymentRequest request);
}

// Adapter bridges the gap
class PaymentAdapter implements PaymentProcessor {
    private OldPaymentGateway oldGateway;
    
    @Override
    public void pay(PaymentRequest request) {
        oldGateway.processOldPayment(request.getCard(), request.getAmount());
    }
}
```

**Real-world uses:**
- `Arrays.asList()` - adapts array to List
- `InputStreamReader` - adapts InputStream to Reader
- Spring's `HandlerAdapter` - adapts controllers to DispatcherServlet
- JDBC drivers - adapt database protocols to JDBC interface

---

### 16. What is the difference between Adapter and Decorator design pattern?

| Aspect | Adapter | Decorator |
|--------|---------|-----------|
| **Purpose** | Convert interface | Add behavior |
| **Interface** | Changes interface | Same interface |
| **Focus** | Compatibility | Enhancement |
| **Wraps** | Incompatible class | Same type |

```java
// Adapter - CHANGES interface
class ArrayListAdapter implements Queue {
    private ArrayList<T> list;
    void enqueue(T item) { list.add(item); }
}

// Decorator - SAME interface, adds behavior
class EncryptedOutputStream extends OutputStream {
    private OutputStream wrapped;
    void write(byte[] data) {
        wrapped.write(encrypt(data));  // Add encryption
    }
}
```

---

## 🔹 Microservices & System Design

### 17. How would you design a highly scalable product architecture?

```
                            ┌─────────────────┐
                            │   CDN (Static)  │
                            └────────┬────────┘
                                     │
┌──────────┐    ┌────────────────────▼────────────────────┐
│  Client  │───►│         API Gateway / Load Balancer     │
└──────────┘    │    (Kong, AWS ALB, Nginx, Envoy)        │
                └────────────────────┬────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ Order Service │          │ Product Service│          │ User Service  │
│ (3 instances) │          │ (3 instances) │          │ (3 instances) │
└───────┬───────┘          └───────┬───────┘          └───────┬───────┘
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│  Redis Cache  │          │  Redis Cache  │          │  Redis Cache  │
└───────┬───────┘          └───────┬───────┘          └───────┬───────┘
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ PostgreSQL    │          │ PostgreSQL    │          │ PostgreSQL    │
│ (Primary +    │          │ (Read Replicas│          │ (Sharded)     │
│  Replicas)    │          │               │          │               │
└───────────────┘          └───────────────┘          └───────────────┘
                                     │
                            ┌────────▼────────┐
                            │  Kafka/RabbitMQ │
                            │ (Async Comms)   │
                            └─────────────────┘
```

**Key principles:**
1. **Horizontal scaling** - Add more instances, not bigger servers
2. **Stateless services** - Store state in Redis/DB
3. **Database per service** - Avoid shared DB
4. **Async communication** - Use message queues for decoupling
5. **Caching** - Redis/Memcached at multiple layers
6. **Load balancing** - Distribute traffic evenly

---

### 18. Does adding cache and additional databases make a system scalable?

**Not automatically!** They help, but proper design is key.

| Component | Helps Scalability If... | Hurts If... |
|-----------|------------------------|-------------|
| **Cache** | Used for frequent reads, proper invalidation | Cache stampede, stale data issues |
| **More DBs** | Proper sharding strategy, read replicas | No sharding = just more maintenance |
| **Read Replicas** | Read-heavy workloads | Write-heavy (replicas lag behind) |

**What actually makes systems scalable:**
1. Stateless services
2. Horizontal scaling capability
3. Async processing for heavy tasks
4. Smart caching strategy (not just "add cache")
5. Database sharding/partitioning

---

### 19. What is a highly available system?

**Definition:** System that remains operational even when components fail.

**Measured by:** Uptime percentage (e.g., 99.99% = 52 min downtime/year)

| Availability | Downtime/Year | Called |
|--------------|---------------|--------|
| 99% | 3.65 days | Two nines |
| 99.9% | 8.76 hours | Three nines |
| 99.99% | 52 minutes | Four nines |
| 99.999% | 5 minutes | Five nines |

**How to achieve:**
1. **Redundancy** - No single point of failure
2. **Load balancers** - Multiple with failover
3. **Database replication** - Primary-replica setup
4. **Multi-region deployment** - Survive region outages
5. **Health checks** - Auto-remove unhealthy instances
6. **Circuit breakers** - Prevent cascade failures

---

### 20. What happens if the load balancer goes down?

**Problem:** Load balancer is a single point of failure!

**Solutions:**

```
┌─────────────────────────────────────────┐
│         DNS (Round-Robin or           │
│         GeoDNS with health checks)      │
└──────────────────┬──────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌─────────────────┐   ┌─────────────────┐
│  Load Balancer  │   │  Load Balancer  │ (Standby/Active-Active)
│     (Primary)   │◄─►│    (Secondary)  │
└────────┬────────┘   └────────┬────────┘
         │                     │
         └──────────┬──────────┘
                    ▼
            ┌───────────────┐
            │   Services    │
            └───────────────┘
```

1. **Active-Passive (Failover):** Secondary takes over via VRRP/Keepalived
2. **Active-Active:** Both handle traffic, DNS distributes
3. **Cloud LB:** AWS ALB/NLB are inherently highly available
4. **DNS failover:** Health check removes failed LB IP

---

### 21. What design patterns are used in microservices architecture?

| Pattern | Purpose | Tool/Implementation |
|---------|---------|---------------------|
| **API Gateway** | Single entry point | Kong, Spring Cloud Gateway |
| **Service Discovery** | Find service instances | Eureka, Consul, K8s Services |
| **Circuit Breaker** | Handle failures gracefully | Resilience4j, Hystrix |
| **Saga** | Distributed transactions | Orchestration or Choreography |
| **CQRS** | Separate read/write models | Event Sourcing + Read DBs |
| **Event Sourcing** | Store events, not state | Kafka + Event Store |
| **Sidecar** | Cross-cutting concerns | Envoy, Istio |
| **Bulkhead** | Isolate failures | Thread pools, pods |
| **Strangler Fig** | Gradual migration | Route traffic incrementally |

---

### 22. How should communication happen between Order service and Invoice service?

**Prefer ASYNC for decoupling:**

```
┌──────────────┐     Kafka/RabbitMQ     ┌────────────────┐
│ Order Service│────────────────────────►│ Invoice Service│
└──────────────┘   OrderCreatedEvent     └────────────────┘
```

```java
// Order Service publishes event
@Service
public class OrderService {
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafka;
    
    public Order createOrder(OrderRequest req) {
        Order order = saveOrder(req);
        kafka.send("order-events", new OrderCreatedEvent(order));
        return order;
    }
}

// Invoice Service consumes event
@Service
public class InvoiceConsumer {
    @KafkaListener(topics = "order-events")
    public void handleOrderCreated(OrderCreatedEvent event) {
        invoiceService.createInvoice(event.getOrderId());
    }
}
```

**When to use SYNC (REST/gRPC):**
- Invoice data needed immediately in response
- Simple, low-latency requirements
- Use Circuit Breaker pattern!

---

### 23. Can one database be used for multiple microservices? Explain.

**Short answer: NO (anti-pattern)**

| Shared DB Problems | Impact |
|-------------------|--------|
| Tight coupling | Can't deploy independently |
| Schema changes | Breaking changes affect all |
| Scaling | Can't scale services independently |
| Technology lock-in | All must use same DB |

**Acceptable exceptions:**
1. **Read replicas** - Multiple services read from same replica
2. **Migration phase** - Temporary during decomposition
3. **Shared reference data** - Rarely-changing lookup tables

**Proper approach:**
```
Order Service ────► Orders DB
                         │
                         │ (Events via Kafka)
                         ▼
Invoice Service ──► Invoices DB (has order_id reference)
```

---

### 24. If invoice is created synchronously and order fails, how would you handle it?

**Saga Pattern with Compensation:**

```java
// Orchestrator-based Saga
@Service
public class OrderSaga {
    
    public void createOrderWithInvoice(OrderRequest req) {
        String orderId = null;
        String invoiceId = null;
        
        try {
            // Step 1: Create Order
            orderId = orderService.createOrder(req);
            
            // Step 2: Create Invoice
            invoiceId = invoiceService.createInvoice(orderId);
            
            // Step 3: Confirm Order (if all succeeded)
            orderService.confirmOrder(orderId);
            
        } catch (Exception e) {
            // Compensating transactions
            if (invoiceId != null) {
                invoiceService.cancelInvoice(invoiceId);
            }
            if (orderId != null) {
                orderService.cancelOrder(orderId);
            }
            throw new OrderFailedException(e);
        }
    }
}
```

**Better: Choreography-based (Event-Driven)**
```
Order Created → Invoice Service creates invoice
                     ↓
             Invoice Created → Order confirmed
                     OR
             Invoice Failed → Order cancelled
```

---

## 🔹 Kafka

### 25. If there are two consumer groups and a topic receives a message, which consumer group will listen to it?

**BOTH consumer groups receive the message!**

```
                    ┌────────────────┐
                    │     Topic      │
                    │  (3 partitions)│
                    └───────┬────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌──────────┐    ┌──────────┐    ┌──────────┐
     │Partition0│    │Partition1│    │Partition2│
     └────┬─────┘    └────┬─────┘    └────┬─────┘
          │               │               │
    ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐
    │           │   │           │   │           │
    ▼           ▼   ▼           ▼   ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Group A │ │Group B │ │Group A │ │Group B │
│Consumer│ │Consumer│ │Consumer│ │Consumer│
└────────┘ └────────┘ └────────┘ └────────┘
```

**Key rules:**
- **Across groups:** Every group gets every message
- **Within group:** Each partition → exactly one consumer
- **If 4 consumers in group but 3 partitions:** 1 consumer is idle

---

## 🔹 Security

### 26. What is the difference between OAuth2 and JWT?

| Aspect | OAuth 2.0 | JWT |
|--------|-----------|-----|
| **What is it?** | Authorization FRAMEWORK | Token FORMAT |
| **Purpose** | Delegates access rights | Transports claims securely |
| **Relationship** | Protocol | Can be used as OAuth token |
| **Contains** | Defines flows, scopes, grants | Header, Payload, Signature |

```
OAuth 2.0 Flow:
User → Authorization Server → Access Token (can be JWT!) → Resource Server

JWT Structure:
xxxxx.yyyyy.zzzzz
  │      │      │
Header Payload Signature
```

**They work together:**
- OAuth2 defines HOW to get tokens
- JWT defines WHAT the token looks like

```java
// JWT as OAuth2 access token
@Bean
public JwtDecoder jwtDecoder() {
    return NimbusJwtDecoder.withJwkSetUri(jwkSetUri).build();
}
```

---

## 🔹 Spring Data JPA

### 27. What is the difference between CrudRepository and JpaRepository?

```
Repository (marker)
      │
      ▼
CrudRepository (CRUD operations)
      │
      ▼
PagingAndSortingRepository (+ pagination/sorting)
      │
      ▼
JpaRepository (+ JPA-specific: flush, batch, etc.)
```

| Feature | CrudRepository | JpaRepository |
|---------|----------------|---------------|
| `save()`, `findById()`, `delete()` | ✅ | ✅ |
| Pagination & Sorting | ❌ | ✅ |
| `flush()`, `saveAndFlush()` | ❌ | ✅ |
| `deleteInBatch()` | ❌ | ✅ |
| `getOne()` / `getReferenceById()` | ❌ | ✅ |

```java
// Use JpaRepository for full features
public interface UserRepository extends JpaRepository<User, Long> {
    Page<User> findByStatus(String status, Pageable pageable);
}
```

---

## 🔹 Build Tools (Maven)

### 28. What is the difference between mvn package and mvn install?

```
mvn package   → Compiles + Tests + Creates JAR/WAR in target/
mvn install   → Does package + Copies to ~/.m2/repository (local repo)
```

| Phase | Output Location | Use Case |
|-------|-----------------|----------|
| `package` | `target/app.jar` | Build artifact for deployment |
| `install` | `~/.m2/repository/` | Share with other local projects |

---

### 29. What is the difference between mvn install and mvn deploy?

```
mvn install → Local repository (~/.m2)
mvn deploy  → Remote repository (Nexus, Artifactory, Maven Central)
```

| Command | Repository | Purpose |
|---------|------------|---------|
| `install` | Local `~/.m2` | Use in other projects on same machine |
| `deploy` | Remote (Nexus) | Share with team/production |

```xml
<!-- In pom.xml for deploy -->
<distributionManagement>
    <repository>
        <id>nexus-releases</id>
        <url>https://nexus.company.com/repository/releases</url>
    </repository>
</distributionManagement>
```

---

## 🔹 Database

### 30. Why do we need normalization in databases?

**Purpose:** Organize data to reduce redundancy and improve integrity.

| Problem | Without Normalization | With Normalization |
|---------|----------------------|-------------------|
| **Redundancy** | Customer address repeated in every order | Address stored once |
| **Update anomaly** | Change address in 100 orders | Change in 1 place |
| **Insert anomaly** | Can't add customer without order | Customer exists independently |
| **Delete anomaly** | Delete order = lose customer | Customer preserved |

**Normal Forms:**
- **1NF:** Atomic values, no repeating groups
- **2NF:** 1NF + no partial dependencies
- **3NF:** 2NF + no transitive dependencies

> ⚠️ **Trade-off:** Over-normalization = too many JOINs = slow reads. Sometimes denormalize for performance!

---

### 31. What are the drawbacks of indexing?

| Drawback | Explanation |
|----------|-------------|
| **Storage overhead** | Indexes take disk space (sometimes 10-20% of table) |
| **Slower writes** | INSERT/UPDATE/DELETE must update indexes too |
| **Maintenance** | Need periodic rebuilding/reindexing |
| **Wrong index hurts** | Bad index = full scan anyway + overhead |
| **Too many indexes** | Optimizer confuses, write penalty |

**Best practices:**
- Index columns used in WHERE, JOIN, ORDER BY
- Avoid indexing low-cardinality columns (gender, status)
- Use composite indexes carefully (order matters!)
- Monitor unused indexes: `pg_stat_user_indexes`

---

## 🔹 Interview Preparation

### 32. Design product architecture for high scalability

*(See question #17 for detailed architecture diagram)*

**Key points to mention:**
1. **Microservices** - Independent, deployable units
2. **API Gateway** - Single entry, auth, rate limiting
3. **Horizontal scaling** - Kubernetes/ECS auto-scaling
4. **Async communication** - Kafka for event-driven
5. **Caching layer** - Redis for hot data
6. **Database strategy** - DB per service, read replicas, sharding
7. **CDN** - Static assets at edge
8. **Observability** - Prometheus, Grafana, ELK stack

---

### 33. Self-Introduction Template (Based on Experience)

```
"Hi, I'm [Name], a Java developer with 5 years of experience specializing 
in Spring Boot microservices.

Currently, I'm working on [e-commerce REST APIs] where I:
- Design and implement scalable services handling [X requests/day]
- Work with [Kafka for async processing, Redis for caching]
- Follow [clean architecture/domain-driven design] principles

In my previous role at [Company], I [specific achievement]:
- Led migration from monolith to microservices
- Reduced API latency by 40% through caching strategies
- Implemented CI/CD pipelines using Jenkins/GitLab

I'm passionate about [clean code, design patterns, system design] and 
constantly explore [new technologies/patterns] to improve my craft.

I'm excited about this opportunity because [specific reason about company/role]."
```

**Tips:**
- Keep it under 2 minutes
- Include metrics where possible
- End with something specific about the company
- Practice until it feels natural

---

*Good luck with your interviews! 🚀*
