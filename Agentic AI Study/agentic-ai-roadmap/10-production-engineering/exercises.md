# Phase 10 — Production Engineering · Exercises

Fresh problems, easy → hard. One-line hints, **no solutions**. Different angles from the checklist.

### 1. (Easy) Add jitter to the backoff
Modify the retry decorator so each wait is `base * backoff**attempt` **plus** a small random jitter.
*Hint: `delay += random.uniform(0, delay * 0.1)` — jitter de-synchronizes a fleet so they don't all retry on the same tick (thundering herd).*

### 2. (Easy) Per-model rate limits
Make the limiter configurable so `claude-opus` and `claude-haiku` get different per-minute budgets.
*Hint: a `dict[str, TokenBucketLimiter]` keyed by model name; `acquire(model)` picks the right bucket.*

### 3. (Medium) Measure cache hit rate under a realistic mix
Replay a query log with repeats through `embed_with_cache` and assert the hit rate exceeds a target.
*Hint: build a list with intentional duplicates, run it through, then read `cache.hit_rate` — like asserting a Caffeine cache's stats in a test.*

### 4. (Medium) Injection patterns + allowlist
Add two new prompt-injection patterns, then add an allowlist so a known-safe phrase that *contains* a
trigger word isn't falsely blocked.
*Hint: check the allowlist first and short-circuit; regex guardrails are necessary but not sufficient — tune for false positives.*

### 5. (Hard) Retry only retryable exceptions
Make `retry_on_error` accept a tuple of exception types; retry those, but re-raise everything else
immediately.
*Hint: `except retryable_excs as e:` retries, a bare `except Exception: raise` does not — never retry a non-idempotent or 4xx-class failure.*

### 6. (Hard) Redact a new PII type
Add phone-number redaction to the output guardrail **without** clobbering legitimate numbers like
order IDs or prices.
*Hint: a tighter regex anchored on phone formatting; add a test asserting `$1,299.00` and `ORDER-4821` survive while `+1 (415) 555-0132` is redacted.*
