# Phase 10 — Production Engineering

> **Goal:** make your agents reliable, safe, and cost-efficient.
> **Duration:** ongoing — this is the work that never quite finishes.

---

## Why this matters

You can stand up an agent demo in an afternoon. It calls the model, it answers, the room claps. Then it meets production and three things that the demo never had to care about become the entire job: **reliability**, **safety**, and **cost control**.

- **Reliability.** Real networks drop packets. Providers return 429s and 503s. If your agent treats the first failed call as fatal, your "working" demo becomes a flaky service that pages you at 2am. Reliability is the discipline of expecting failure and absorbing it — rate limiting so you don't *cause* the failures, and retries-with-backoff so you survive the ones you didn't cause.
- **Safety.** The moment a user can type into your agent, someone will try to make it misbehave — talk it out of its instructions, or coax it into emitting data it shouldn't. Safety is the validation layer between the open internet and your model, and the scrubber between your model and the response.
- **Cost control.** Every model and embedding call is metered. A demo makes ten calls; production makes ten million. Without a cache you are paying full price to compute the same embedding for "reset my password" a thousand times a day.

None of this is new to you — it is exactly the operational hardening you already do for any Spring Boot service that talks to a flaky downstream. The vocabulary maps almost one-to-one:

| Production concern | This phase's tool | Your Java toolkit |
|---|---|---|
| Don't overwhelm the provider | `TokenBucketLimiter` | **Bucket4j** `Bucket`, **Resilience4j** `RateLimiter` |
| Survive transient failures | `retry_on_error` decorator | **Spring Retry** `@Retryable` + `@Backoff`, **Resilience4j** `Retry` |
| Stop paying for repeat work | `LRUEmbeddingCache` | **Caffeine** `Cache`, Spring `@Cacheable` |
| Reject hostile / scrub leaking output | `Guardrails` | a validation `Filter` / `HandlerInterceptor`, or a **WAF** |

The rest of these notes walk each one in prose, then close with the mistakes I most often see Java developers make on their first production agent, and a glossary.

---

## 10.1 — Rate limiting + exponential backoff

There are two distinct jobs here, and conflating them is the first mistake. **Rate limiting** is *proactive*: it stops you from sending more traffic than the provider allows, so you never trip the limit in the first place. **Retry with backoff** is *reactive*: when a call fails anyway — because of a transient server hiccup, a timeout, or a limit you couldn't predict — it tries again, sensibly. You want both. Rate limiting is the seatbelt; backoff is the airbag.

### The token-bucket limiter

`TokenBucketLimiter` (in `code/01_rate_limiting_backoff.py`) keeps a sliding 60-second window of call timestamps in a `deque`. Before each call you `await limiter.acquire()`. It evicts timestamps older than the window, and if the window is already full it computes exactly how long until the oldest call ages out and `await asyncio.sleep`s for that long. When the sleep returns, a slot is free, and the call proceeds.

This is the same contract as **Bucket4j**: you `acquire()` a permit before doing work, and if none is available you wait. The difference from a Java `Semaphore` is the *time window* — permits aren't returned when work finishes, they expire on a clock. That is precisely the "N calls per minute" shape that LLM providers publish.

One detail that matters in async land: the wait is `await asyncio.sleep(...)`, **never** `time.sleep(...)`. More on why in the mistakes section, but the short version is that `time.sleep` would freeze the entire event loop and stall every other in-flight request. I also wrap the check-then-sleep in an `asyncio.Lock` so that when a burst of coroutines hits a full window, they queue cleanly instead of all reading "there's room!" at the same instant.

### The retry decorator

`retry_on_error` is a decorator — the Pythonic equivalent of Spring Retry's `@Retryable`. Wrap any async function with it and failures are retried with **exponential backoff**: the wait grows as `base_delay * backoff ** attempt`, capped at `max_delay`. The decorator calls `limiter.acquire()` on *every* attempt, so retries are themselves rate-limited.

Two design choices are worth calling out because they're the difference between a retry policy that helps and one that makes an outage worse:

1. **Jitter.** After computing the exponential delay we multiply it by a small random factor (e.g. ±25%). Without jitter, a hundred clients that all failed at the same millisecond will all wait *exactly* 2 seconds and then retry in perfect unison — a self-inflicted "thundering herd" that re-triggers the very overload they were backing off from. Jitter spreads them out. (This is the lesson of AWS's classic "Exponential Backoff And Jitter" post.)
2. **Selective retry.** The decorator only catches the exception types you list in `retry_on` (here, `TransientLLMError`). A `FatalLLMError` — our stand-in for a 400/401/403 — propagates immediately. Retrying a malformed request or a bad API key is pointless: it will fail identically every time and just burns your **retry budget**. This is the direct analogue of Spring Retry's `retryFor` / `noRetryFor`.

### resilient_llm_call

`resilient_llm_call` ties it together: a single function, decorated with `@retry_on_error`, that rate-limits and retries one model call. In the file it wraps a **mock** that fails twice then succeeds, so you can watch backoff work with no API key and no spend. A commented `_real_llm_create` shows exactly how to swap in the real `AsyncAnthropic` client and, crucially, how to map the SDK's exceptions onto `TransientLLMError` vs `FatalLLMError` so the retry policy stays correct.

---

## 10.2 — Embedding cache

Embeddings have a property that makes caching almost unfairly effective: they are **content-addressable**. The same input text always produces the same vector. So the *second* time anyone embeds "What are your store hours?", the correct answer is already sitting in memory — recomputing it is pure waste.

And repeats are not rare. Real traffic is heavily skewed (Zipf-like): a handful of queries and document chunks recur constantly, while a long tail appears once. The demo in `code/02_embedding_cache.py` models this with a weighted query stream and measures the result — it lands around an **82% hit rate**, meaning roughly four out of five embedding calls were served for free from the cache.

### Why this saves *real* money (and latency)

Every embedding call is billed per token and adds network latency to your hot path. A cache converts a hit from "round-trip API call you pay for" into "in-process dictionary lookup that's effectively free and instant." At an 82% hit rate you've cut your embedding bill by ~82% *and* removed that latency from four of every five requests. In most agent stacks this is the single highest-leverage cost lever available — and it's a few dozen lines of code.

### LRUEmbeddingCache

The implementation is an `OrderedDict` behaving as an **LRU cache**, which is the exact mental model of **Caffeine**'s `maximumSize` cache:

- The key is `sha256(text)` — a stable content hash. (Hashing also keeps keys a fixed 64 chars no matter how long the input.)
- On a hit, `move_to_end` marks the entry most-recently-used; `hits` increments.
- On a miss we compute, then `set`. If the cache is at `max_size`, `popitem(last=False)` evicts the **least**-recently-used entry first.
- `hit_rate` is a simple `hits / (hits + misses)` — the number you should be graphing in production.

The bound is the entire point. `move_to_end` ≈ Caffeine bumping recency; `popitem(last=False)` ≈ Caffeine evicting the coldest entry. The mock embed function is deterministic (hash-seeded), which mirrors the real model's contract and is what makes caching *correct* rather than merely fast.

---

## 10.3 — Input / output guardrails

Guardrails are the validation layer that sits on both sides of the model. Think of them as a Spring `HandlerInterceptor` (or a WAF rule set) for an LLM: one filter inspects what comes *in*, another rewrites what goes *out*.

### Input guardrail — injection detection + length cap

`Guardrails.validate_input` does the cheap check first (a hard **length cap** — both a cost control and a crude DoS defence) and then scans the text against a list of compiled **prompt-injection** signatures: "ignore all previous instructions", "you are now…", "DAN mode", "reveal your system prompt", and so on. A match returns `(False, reason)` and the endpoint answers **HTTP 400**. Note the filter logs *which pattern* matched but never echoes the offending user text back — you don't want to mirror an attack payload into your logs or your response.

### Output guardrail — PII / secret redaction

`Guardrails.sanitize_output` runs the model's reply through a list of `(pattern, tag)` pairs and replaces anything that *looks like* sensitive data — credit-card numbers, US SSNs, emails, phone numbers, API-key-shaped strings — with a typed marker like `[REDACTED_CC]`. Pattern **ordering matters**: the 16-digit card is matched before the phone pattern so a card number isn't half-eaten by the phone regex. This is your last line of defence before bytes leave the process.

### The honest caveat: regex is necessary, not sufficient

I want to be blunt here because it's where well-meaning teams get a false sense of security. Regex guardrails catch the **known, lexical** attacks — the ones spelled out in plain text. They do **not** stop a determined adversary who paraphrases the injection, base64-encodes it, splits it across turns, or writes it in another language. Treat the regex layer as the cheap first tier of *defence in depth*. In production you layer on top of it: tightly scoped tool/permission grants, a moderation or classifier model, output schema validation, and a human in the loop for anything genuinely risky. The regexes are real and they run offline — they're just not the whole story.

### The FastAPI integration

`/chat/safe` wires the pipeline together: `validate_input` → (block with 400 if unsafe) → model call → `sanitize_output` → response. The request body is a Pydantic model with `min_length`/`max_length` on the `message` field, so validation happens at *two* layers (Pydantic + the guardrail) — that's the "belt and suspenders" you'd get from Bean Validation `@Size` plus a service-level check. The file ships an offline `TestClient` smoke test in `__main__` that proves all three behaviours with no server and no network: valid input returns 200 with PII redacted, an injection attempt returns 400, and an empty message is rejected at the validation layer (422).

---

## ⚠️ Common Java-dev mistakes

These are the ones I see most often when a strong Spring engineer ships their first production agent. None are about Python syntax — they're about the operational reflexes that don't transfer cleanly.

- **No rate limiting → 429 storms.** Firing calls as fast as your code can loop will trip the provider's limit, and once you're throttled, naive retries pile *more* traffic onto an already-rejecting endpoint. Gate every call behind the limiter, the same way you'd never hammer a downstream without a Resilience4j `RateLimiter`.
- **Retrying non-idempotent or non-retryable errors.** Retrying a 400 (bad request) or 401 (bad key) is pure waste — it will fail identically every time. Worse, blindly retrying a *non-idempotent* action (one that has side effects, like "charge the card") can execute it multiple times. Scope your retries to transient, safe-to-repeat failures, exactly as `retryFor`/`noRetryFor` does in Spring Retry.
- **No jitter → thundering herd.** Fixed backoff means every failing client retries in lockstep and re-creates the outage. Always add jitter. This is the one experienced backend devs are most surprised they got wrong.
- **Unbounded cache → memory leak.** A plain `dict` that grows with every unique query never stops growing and eventually OOM-kills the process. This is a real incident, not a theoretical one. Bound the cache (`max_size`) and evict LRU — i.e. use the equivalent of Caffeine's `maximumSize`, never a bare map.
- **Treating regex guardrails as the *only* defence.** Pattern matching is necessary but not sufficient. Shipping it as your complete safety story gives a false sense of security; pair it with scoped permissions, a moderation model, and human review for risky actions.
- **Logging the very PII you just redacted.** It is painfully easy to redact a credit-card number in the response and then log the *raw* model output one line above for "debugging." Redact before you log, and never log the offending input on a guardrail block either.
- **Blocking the event loop in an async retry.** Calling `time.sleep()` inside an `async` function freezes the *entire* event loop — every other concurrent request stalls for the duration. In async code the backoff wait must be `await asyncio.sleep()`. There is no `Thread.sleep()` equivalent that only pauses "this request"; one loop serves them all.

---

## Key terms

- **Rate limiting** — capping how many calls you send in a time window so you stay under a provider's quota. Proactive.
- **Token bucket** — a rate-limiting model where permits ("tokens") refill over time; you spend one per call and wait when the bucket is empty. (Here implemented as a sliding window of timestamps, which gives the same per-minute behaviour.)
- **Exponential backoff** — increasing the wait between retries geometrically (`base * factor^attempt`) so a struggling service gets progressively more breathing room.
- **Jitter** — adding randomness to backoff delays so many clients don't retry in perfect sync and re-create the overload (the "thundering herd").
- **Idempotency** — the property that doing an operation twice has the same effect as doing it once. Only idempotent operations are safe to retry blindly.
- **Retry budget** — the finite total of retry attempts you're willing to spend; wasting it on non-retryable errors leaves none for the failures that would actually recover.
- **LRU cache** — "Least Recently Used": a bounded cache that evicts the entry untouched for the longest when it needs room.
- **Cache hit rate** — `hits / (hits + misses)`. The headline metric for how much work (and money) your cache is saving.
- **Prompt injection** — an attack where user-supplied text tries to override the system's instructions ("ignore previous instructions", "you are now…").
- **Guardrail** — a validation/transformation layer around the model: input checks that reject hostile or oversized requests, output checks that scrub sensitive data.
- **PII redaction** — detecting personally identifiable information (cards, SSNs, emails, phone numbers, secrets) in output and replacing it with a placeholder before it leaves the service.
