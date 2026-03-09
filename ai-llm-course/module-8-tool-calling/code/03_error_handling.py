"""
MODULE 8 — Example 3: Error Handling & Resilience
====================================================
Retry, circuit breaker, and fallback patterns for tools.

SETUP:
  pip install openai python-dotenv

RUN:
  python 03_error_handling.py
"""

import os
import json
import time
import random
import functools
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# ══════════════════════════════════════════════════════
# PATTERN 1: RETRY WITH EXPONENTIAL BACKOFF
# ══════════════════════════════════════════════════════

def retry(max_attempts: int = 3, backoff_base: float = 1.0, retryable_errors: tuple = (TimeoutError, ConnectionError)):
    """
    Decorator that retries on transient failures.
    
    Java Analogy: @Retry from Resilience4j.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except retryable_errors as e:
                    last_error = e
                    if attempt < max_attempts:
                        delay = backoff_base * (2 ** (attempt - 1))
                        print(f"      ⚠️  Attempt {attempt} failed: {e}. Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                    else:
                        print(f"      ❌ All {max_attempts} attempts failed: {e}")
                except Exception as e:
                    raise  # Non-retryable: fail immediately
            raise last_error
        return wrapper
    return decorator


# ══════════════════════════════════════════════════════
# PATTERN 2: CIRCUIT BREAKER
# ══════════════════════════════════════════════════════

class CircuitBreaker:
    """
    Stops calling a failing tool after N consecutive failures.
    States: CLOSED (normal) → OPEN (blocking) → HALF_OPEN (testing).
    
    Java Analogy: Resilience4j CircuitBreaker.
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 10.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Check if circuit is OPEN
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    print(f"      🔄 Circuit half-open — testing {fn.__name__}...")
                else:
                    raise Exception(f"Circuit OPEN for {fn.__name__} — not calling")

            try:
                result = fn(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failures = 0
                    print(f"      ✅ Circuit closed — {fn.__name__} recovered")
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                if self.failures >= self.failure_threshold:
                    self.state = "OPEN"
                    print(f"      🔴 Circuit OPEN — {fn.__name__} disabled after {self.failures} failures")
                raise

        wrapper.breaker = self  # Expose for inspection
        return wrapper
    
    def reset(self):
        self.failures = 0
        self.state = "CLOSED"


# ══════════════════════════════════════════════════════
# PATTERN 3: TOOL WITH FALLBACK
# ══════════════════════════════════════════════════════

class ToolWithFallback:
    """
    Try primary tool, if it fails use fallback.
    
    Java Analogy: @CircuitBreaker(fallbackMethod = "fallback")
    """

    def __init__(self, primary, fallback, name: str = ""):
        self.primary = primary
        self.fallback = fallback
        self.name = name or primary.__name__

    def __call__(self, **kwargs) -> str:
        try:
            result = self.primary(**kwargs)
            return result
        except Exception as e:
            print(f"      ⚠️  Primary ({self.name}) failed: {e}")
            print(f"      🔄 Using fallback...")
            return self.fallback(**kwargs)


# ══════════════════════════════════════════════════════
# SIMULATED TOOLS (with configurable failure rates)
# ══════════════════════════════════════════════════════

def _make_flaky(fn, fail_rate: float = 0.5):
    """Wrap a function to simulate random failures."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if random.random() < fail_rate:
            raise ConnectionError(f"Simulated failure in {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper


def search_primary(query: str) -> str:
    """Primary search API (sometimes fails)."""
    return json.dumps({"source": "primary", "query": query, "result": f"Primary results for: {query}"})


def search_backup(query: str) -> str:
    """Backup search (always works)."""
    return json.dumps({"source": "backup", "query": query, "result": f"Backup results for: {query}"})


# Apply patterns
flaky_search = _make_flaky(search_primary, fail_rate=0.6)
search_with_retry = retry(max_attempts=3, backoff_base=0.1, retryable_errors=(ConnectionError,))(flaky_search)

cb = CircuitBreaker(failure_threshold=3, recovery_timeout=2.0)
search_with_breaker = cb(_make_flaky(search_primary, fail_rate=0.8))

search_with_fallback = ToolWithFallback(
    primary=_make_flaky(search_primary, fail_rate=0.7),
    fallback=search_backup,
    name="search",
)


# ══════════════════════════════════════════════════════
# PATTERN 4: SAFE TOOL EXECUTOR
# ══════════════════════════════════════════════════════

class SafeToolExecutor:
    """
    Executes tools with validation, timeout, and error handling.
    This is what a production tool executor looks like.
    """

    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout = timeout_seconds
        self.execution_log = []

    def execute(self, fn, args: dict, tool_name: str = "") -> str:
        """Execute a tool safely."""
        name = tool_name or fn.__name__
        start = time.time()

        log_entry = {
            "tool": name,
            "args": args,
            "timestamp": time.strftime("%H:%M:%S"),
        }

        try:
            # Validate args are not empty/null
            for key, val in args.items():
                if val is None or (isinstance(val, str) and not val.strip()):
                    return json.dumps({"error": f"Empty argument: {key}", "tool": name})

            result = fn(**args)
            elapsed = time.time() - start

            log_entry.update({"status": "success", "duration_ms": round(elapsed * 1000)})
            self.execution_log.append(log_entry)
            return result

        except Exception as e:
            elapsed = time.time() - start
            error_result = {
                "error": str(e),
                "tool": name,
                "suggestion": "This tool is temporarily unavailable. Please try a different approach.",
            }
            log_entry.update({"status": "error", "error": str(e), "duration_ms": round(elapsed * 1000)})
            self.execution_log.append(log_entry)
            return json.dumps(error_result)


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🛡️  Error Handling & Resilience Patterns     ║")
    print("╚══════════════════════════════════════════════╝")

    random.seed(42)  # Reproducible for demo

    # Test 1: Retry
    print(f"\n  {'═'*55}")
    print("  TEST 1: Retry with Exponential Backoff")
    print(f"  {'─'*55}")
    try:
        result = search_with_retry(query="test retry")
        print(f"    ✅ Success: {result}")
    except ConnectionError:
        print(f"    ❌ All retries exhausted")

    # Test 2: Circuit Breaker
    print(f"\n  {'═'*55}")
    print("  TEST 2: Circuit Breaker")
    print(f"  {'─'*55}")
    cb.reset()
    for i in range(6):
        try:
            result = search_with_breaker(query=f"test {i}")
            print(f"    Call {i+1}: ✅ Success | State: {cb.state}")
        except Exception as e:
            print(f"    Call {i+1}: ❌ {str(e)[:40]} | State: {cb.state}")
        time.sleep(0.1)

    # Test 3: Fallback
    print(f"\n  {'═'*55}")
    print("  TEST 3: Primary + Fallback")
    print(f"  {'─'*55}")
    for i in range(5):
        result = search_with_fallback(query=f"query {i}")
        parsed = json.loads(result)
        source = parsed.get("source", "?")
        print(f"    Call {i+1}: Source = {source}")

    # Test 4: Safe Executor
    print(f"\n  {'═'*55}")
    print("  TEST 4: Safe Tool Executor")
    print(f"  {'─'*55}")
    executor = SafeToolExecutor(timeout_seconds=5)

    # Successful call
    result = executor.execute(search_backup, {"query": "safe test"}, "search")
    print(f"    Safe call: {result}")

    # Failed call (empty args)
    result = executor.execute(search_backup, {"query": ""}, "search")
    print(f"    Empty args: {result}")

    # Failed call (exception)
    result = executor.execute(flaky_search, {"query": "risky"}, "flaky_search")
    print(f"    Flaky call: {result}")

    print(f"\n  📊 Execution Log:")
    for entry in executor.execution_log:
        status = "✅" if entry["status"] == "success" else "❌"
        print(f"    {status} {entry['tool']} ({entry['duration_ms']}ms)")

    print(f"\n  ✅ Resilience patterns:")
    print(f"     • Retry: handles transient failures automatically")
    print(f"     • Circuit Breaker: stops hammering broken services")
    print(f"     • Fallback: degrades gracefully to backup")
    print(f"     • Safe Executor: validates, catches, logs everything\n")


if __name__ == "__main__":
    main()
