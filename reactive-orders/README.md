# Reactive Orders API - Interview Prep Project

A sample Spring WebFlux project demonstrating reactive patterns, clean architecture, and testing.

## How to Run

1. **Start MongoDB**:
   ```bash
   docker-compose up -d
   ```
2. **Run Application**:
   ```bash
   ./mvnw spring-boot:run
   ```

## Interview Notes

### Concept: Reactive Programming
Reactive programming is an asynchronous programming paradigm concerned with data streams and the propagation of change.
In Spring WebFlux, it's about building non-blocking, event-driven applications that can handle a massive number of concurrent connections with a small number of threads.

- **Publisher**: The source of data (Mono/Flux).
- **Subscriber**: The component consuming data.
- **Subscription**: The link between the two.
- **Processor**: Acts as both.

### Key Types
- **Mono<T>**: Emits 0 or 1 item.
- **Flux<T>**: Emits 0 to N items.

### Why WebFlux over Spring MVC?
Spring MVC (blocking I/O) assigns a thread per request. If I/O is slow (DB, API), that thread blocks (waits). High concurrency = many threads = high context switching overhead.
Spring WebFlux (non-blocking I/O) uses a small number of event loop threads. When I/O starts, the thread is released. specific "Callback" resumes when I/O finishes. Efficient for high-latency/high-concurrency apps.

**Wait for Step 1 for more details on Domain modeling.**

### Step 1: Domain & DTOs
**Q: Why separate DTOs from Entities?**
**A**: Decoupling. Entities represent the database schema. DTOs represent the API contract. They evolve independently. Using Entities in the API exposes internal db structure and can lead to over-posting vulnerabilities.

**Q: How does Validation work in WebFlux?**
**A**: Similar to MVC! Use `jakarta.validation` annotations (`@NotNull`, `@Min`) on DTOs. In annotated controllers, add `@Valid` to the method argument. In functional endpoints, you rely on a `Validator` instance to manually check, or throw `WebExchangeBindException`.

### Step 2: Reactive Repositories
**Q: How does `ReactiveMongoRepository` differ from `MongoRepository`?**
**A**: Return types! Reactive repo returns `Mono<T>` (for findOne) and `Flux<T>` (for findAll). Normal repo returns `T` or `List<T>`. Calling a method on a reactive repo *does nothing* until you subscribe (data is pulled, not pushed).

**Q: In `DataInitializer`, why do we need `.subscribe()`?**
**A**: Because reactive streams are **lazy** (Cold Publishers). Nothing happens until a subscriber requests data. If we just called `productRepository.save(...)` without `.subscribe()`, the database call would never execute.

### Step 3: Domain Services
**Q: What is the difference between `flatMap` and `concatMap`?**
**A**: `flatMap` triggers inner publishers eagerly and interleaves their results (non-deterministic order). `concatMap` waits for each inner publisher to complete before starting the next (preserves order). In `OrderService`, we use `flatMap` to fetch/update products in parallel for efficiency.

**Q: How do you handle errors in a middle of a reactive chain?**
**A**: Use operators like `onErrorResume` to provide a fallback, `onErrorMap` to translate exceptions, or `switchIfEmpty` to handle cases where a `Mono` completes with no value. In our flow, we use `Mono.error()` to break the chain if stock is low.

**Q: Is the stock deduction transactionally safe in MongoDB?**
**A**: In this simple implementation, no. Reactive MongoDB supports transactions, but it requires replica sets and `TransactionalOperator`. For interviews, mention that without transactions, you'd use atomic updates (`$inc` with `$gte` check in Mongo) to ensure thread-safety without heavy locks.


