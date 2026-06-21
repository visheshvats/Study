# Phase 0 — Python Foundations (Notes)

> Audience: an enterprise Java developer (Spring Boot, microservices, JPA) moving into Agentic AI.
> Goal of this phase: build a REST API, be ready to call an LLM API, and handle errors properly.

## Why this matters

You already know how to build production services. The hard part of agentic AI is *not* learning a new language from scratch — it is mapping what you already do in Java onto Python's idioms, and accepting that the AI ecosystem (LangChain, LangGraph, Pydantic, FastAPI) is overwhelmingly Python-first. If you fight Python and try to write Java in it, you will be slow and your code will look foreign to every example you read. If you learn the five or six idioms in this phase well, the rest of the roadmap becomes a matter of wiring libraries together.

Three things dominate agent code: **dictionaries**, **async I/O**, and **validated models**. Almost everything an LLM returns is JSON, and in Python JSON is just nested `dict`/`list` — so dictionaries are the lingua franca, the way `HashMap<String,Object>` shows up everywhere in loosely-typed Java code, but more so. Agents spend most of their wall-clock time *waiting* on network calls (LLM APIs, vector stores, tools), so `asyncio` is how you fan those calls out concurrently without spinning up thread pools. And because LLM output is untrusted text, **Pydantic** models are how you validate it at the boundary — the same instinct that makes you put `@Valid` on a Spring `@RequestBody`.

The deliverable mindset for this phase is "production-first." That means type hints on every signature, real error handling, structured logging instead of stray `print` calls, and configuration loaded from the environment rather than hard-coded. None of this is busywork: in later phases you will be orchestrating multi-step agents where a swallowed exception or a blocking call hidden inside an async path can quietly stall the whole system.

Treat the code in the `code/` folder as the source of truth — these notes explain *why*, the files show *how*, and each file runs offline so you can execute and tinker without any API keys.

---

## Global project setup (the part before Phase 0)

| Concept | Python | Java analogy |
|---|---|---|
| Project / dependency scope | `python -m venv agentic-env` then activate it | A Maven/Gradle project boundary — an isolated dependency space so projects don't collide |
| Declare dependencies | `pip install ...` then `pip freeze > requirements.txt` | `pom.xml` / `build.gradle` dependency block; `requirements.txt` is the resolved lockfile |
| Externalized config | `.env` file + `python-dotenv` | `application.properties` / `application.yml` |
| Read a config value | `os.getenv("ANTHROPIC_API_KEY")` | `environment.getProperty(...)` / `@Value` |

A **virtual environment** is the single most important habit to adopt on day one. Without it, `pip install` mutates a global interpreter and every project shares (and breaks) the same dependencies — imagine if every Maven project on your machine wrote into one shared `~/.m2` with no versioning. Create one per project, activate it, install into it.

The `.env` file holds secrets (API keys) and **must never be committed** — add it to `.gitignore` immediately. The `env_loader.py` helper reads it once at import time. In `code/env_loader.py` I've extended the source's two-line loader into a small module with a `require_key()` "fail fast on missing config" helper and logging that reports which keys are present *without ever printing their values* — leaking a key into a log line is a real incident, not a hypothetical.

---

## 0.1 Core data structures

Python's built-in containers map cleanly onto the Java Collections you reach for daily, but the syntax is lighter and comprehensions replace the Stream API.

| Python | Java | Note |
|---|---|---|
| `list` (`["a","b"]`) | `ArrayList<E>` | Ordered, mutable, **0-indexed** like Java |
| `dict` (`{"k": v}`) | `HashMap<K,V>` | The JSON workhorse of all LLM code |
| `names.append(x)` / `.remove(x)` | `add` / `remove` | |
| `names[0]` / `len(names)` | `get(0)` / `size()` | |
| `d["k"]` | `map.get("k")` | **Raises `KeyError` if absent** (not `null`) |
| `d.get("k", default)` | `map.getOrDefault("k", default)` | Safe access |
| `d.keys()` / `.values()` / `.items()` | `keySet` / `values` / `entrySet` | |

The biggest mental shift is **comprehensions**, which replace the Stream pipelines you already think in:

| Java Stream | Python comprehension |
|---|---|
| `names.stream().filter(n -> n.startsWith("A")).collect(toList())` | `[n for n in names if n.startswith("A")]` |
| `names.stream().map(String::toUpperCase).collect(toList())` | `[n.upper() for n in names]` |
| `stream.collect(toMap(k -> k.toUpperCase(), v -> v))` | `{k.upper(): v for k, v in scores.items()}` |

Read a comprehension right-to-left in Stream terms: the `for ... in` is your stream source, the trailing `if` is `filter`, and the leading expression is `map`. The ternary, `result = x if x > 0 else -x`, is Java's `x > 0 ? x : -x` with the operands reordered (value-first). **Note:** the source guide used `x` before defining it; in `01_data_structures.py` I define `x = -7` first so the example actually runs.

For JSON, `json.dumps`/`json.loads` are your `objectMapper.writeValueAsString`/`readValue`, and `json.dump`/`json.load` are the file variants. The `with open(...) as f:` block is Python's **try-with-resources** — the file closes automatically at the end of the block, exception or not.

---

## 0.2 Functions & type hints

Functions are first-class and signatures read much like Java methods, with a couple of superpowers.

| Feature | Python | Java |
|---|---|---|
| Typed signature | `def greet(name: str, times: int = 1) -> str:` | `String greet(String name, int times)` |
| Default arguments | `times: int = 1` | No native support — you overload methods |
| Optional type | `Optional[Dict[str, Any]]` / `dict \| None` | `Optional<Map<String,Object>>` |
| Varargs | `*args` (`*parts: str`) | `String... parts` |
| Named-param map | `**kwargs` | No direct equivalent |

The critical caveat: **type hints are not enforced at runtime.** Python will happily run `greet(123)`. Hints exist for your IDE, for `mypy` (a separate static checker — think of it as `javac`'s type pass run on demand), and for libraries like Pydantic/FastAPI that *do* act on them. So treat hints as mandatory documentation-plus-tooling, not as a guarantee.

Python has **no checked exceptions**. A common, very un-Java pattern you'll see in agent code is returning a `(value, error)` tuple — `safe_parse_json` returns `(data, None)` on success and `(None, "message")` on failure, forcing the caller to inspect the error explicitly (closer to Go than to Java). The alternative is to `try/except` at the call site, which is the more Pythonic choice for truly exceptional cases.

---

## 0.3 OOP: classes, dataclasses, Pydantic, ABCs

Python gives you three distinct tools where Java blends them into "classes + annotations + interfaces." Knowing which to reach for is half the battle.

| Tool | Python | Java analogy | When to use |
|---|---|---|---|
| `@dataclass` | auto `__init__`/`__repr__`/`__eq__` | `record` / Lombok `@Data` | Plain internal data holder, no validation needed |
| Pydantic `BaseModel` | declarative validation + (de)serialization | DTO + Bean Validation (`@Valid`, `@Min`, `@Max`) | Anything crossing a boundary: API bodies, LLM output, config |
| `ABC` + `@abstractmethod` | abstract base with required methods | `interface` / abstract class | Defining an agent/tool contract subclasses must fulfill |

A **`@dataclass`** is the lightweight option: decorate a class, declare typed fields, and Python generates the constructor, `repr`, and equality for you — exactly like a Java `record`. The one trap (covered below) is mutable defaults: use `field(default_factory=dict)`, never `metadata: dict = {}`.

A **Pydantic `BaseModel`** is what you'll use most in this ecosystem. `Field(default=1024, ge=1, le=4096)` is declarative validation equivalent to `@Min(1) @Max(4096)`, and unlike a plain dataclass it **runs validation on construction** — passing `temperature=5.0` raises a `ValidationError` immediately. `model_dump()` gives you a dict and `model_dump_json()` a JSON string, the way Jackson serializes a DTO. Because LLMs return untrusted text, Pydantic is your primary defense at the boundary.

An **`ABC`** (Abstract Base Class) with `@abstractmethod` is Python's interface. Instantiating `BaseAgent` directly raises `TypeError` because `run` is abstract — the same protection as `new SomeInterface()` failing to compile. `super().__init__(...)` is your `super(...)` call, and overriding `__repr__` is overriding `toString()`. In `03_oop_classes_dataclasses.py` I extended the source to *demonstrate* each guarantee: the Pydantic validation actually fires, and the abstract class actually refuses to instantiate.

---

## 0.4 Async programming

This is the section where Java intuition helps the most *and* misleads the most. `asyncio` is **single-threaded cooperative concurrency**, not a thread pool.

| Python | Java |
|---|---|
| `async def fetch(): ...` | a method returning `CompletableFuture<T>` |
| `await x` | `.join()` / `.get()` — but yields the loop instead of blocking a thread |
| `asyncio.gather(*tasks, return_exceptions=True)` | `CompletableFuture.allOf(...).join()` + collect |
| `async for token in stream(...)` | reactive `Flux<String>` / streaming `Publisher` |
| `asyncio.run(main())` | the `public static void main` entry point |

The model: there is **one event loop on one thread**. When a coroutine hits `await`, it voluntarily hands control back to the loop, which runs other ready coroutines while the first one waits on I/O. This is why agent code can issue dozens of concurrent LLM/tool calls cheaply — no thread per call. `asyncio.gather` fans out and joins, and `return_exceptions=True` means one failed call doesn't cancel the rest; failures come back as exception objects you filter out (versus handling each future's `.exceptionally(...)` before `allOf` in Java).

The cardinal sin: calling a **blocking** function inside async code. `time.sleep(1)` or a blocking JDBC call freezes the *entire* loop and every concurrent coroutine with it, because there's only one thread. Always use the awaitable equivalent (`await asyncio.sleep(1)`, an async HTTP client like `httpx.AsyncClient`, an async DB driver). An **async generator** (`yield` inside `async def`, consumed with `async for`) models LLM token streaming — `04_async_basics.py` simulates this offline so it runs with no network.

---

## 0.5 FastAPI REST API

FastAPI maps almost one-to-one onto Spring Boot Web, and its automatic Swagger UI will feel like springdoc.

| FastAPI | Spring Boot |
|---|---|
| `@app.post("/chat", response_model=ChatResponse)` | `@PostMapping("/chat")` on a `@RestController` |
| Pydantic request model param | `@RequestBody` DTO + `@Valid` |
| `response_model=...` | declared return DTO, serialized to JSON |
| `raise HTTPException(status_code=400, ...)` | `throw new ResponseStatusException(BAD_REQUEST, ...)` |
| `@app.middleware("http")` | a servlet `Filter` / `OncePerRequestFilter` |
| `uvicorn` | the embedded server (Tomcat/Netty) |
| `/docs` (auto Swagger) | springdoc / Swagger UI |

The flow: a request hits the middleware (logging), FastAPI binds and **validates** the JSON body against the Pydantic model (a bad `temperature` returns `422` automatically — you never write that check), then your handler runs business rules and returns a `ChatResponse` that FastAPI serializes. Endpoints are `async def` so they cooperate with the event loop.

In `05_fastapi_app.py` I replaced the source's `# TODO: Replace with actual LLM call in Phase 1` with a clearly-marked **mock** (`[MOCK] <message uppercased>`) and left a commented block showing exactly where the real `AsyncAnthropic` call drops in during Phase 1. The file's `__main__` block runs an **offline smoke test** using FastAPI's `TestClient` (the `MockMvc` analogue) so you can `python 05_fastapi_app.py` and watch all four endpoints respond — valid, empty-message 400, and out-of-range 422 — without starting a server.

---

> ## ⚠️ Common Java-dev mistakes
>
> - **Mutable default arguments.** `def f(items=[])` creates ONE list shared across every call — state leaks between invocations. Use `def f(items=None)` then `items = items or []`. Same rule for dataclass fields: `field(default_factory=list)`, never `= []`.
> - **`==` vs `is`.** `==` compares value (your `equals()`); `is` compares identity (your `==` reference check). Use `is` only for `None`/`True`/`False`. Writing `if x == None` works but `if x is None` is correct and idiomatic.
> - **Forgetting `await`.** Calling `async_fn()` without `await` returns a coroutine object that never runs — no error, just silently nothing happens. The closest Java mistake is creating a `CompletableFuture` and never calling `.join()`.
> - **Blocking calls inside async.** `time.sleep`, blocking HTTP, blocking JDBC freeze the entire single-threaded event loop. Use `asyncio.sleep`, `httpx.AsyncClient`, async DB drivers.
> - **Expecting checked exceptions.** Python has none. Nothing forces you to handle a failure — be deliberate about `try/except` or the `(value, error)` tuple pattern at boundaries.
> - **GIL misconceptions.** The Global Interpreter Lock means threads don't give you true CPU parallelism for pure-Python code. It does NOT hurt I/O-bound work — and async I/O (what agents do) sidesteps it entirely. For CPU-bound work, use `multiprocessing`, not threads.
> - **1-indexing.** Python is **0-indexed** like Java, but slicing is exclusive on the upper bound: `xs[0:2]` yields indices 0 and 1, not 2. Negative indices (`xs[-1]` = last) have no Java equivalent.
> - **Truthiness.** Empty containers (`[]`, `{}`, `""`), `0`, and `None` are all "falsy." `if not items:` is the idiomatic "is empty or null" — but be careful, it also fires on `0` and `""` when you may have meant `is None`.

---

## Key terms

| Term | One-line definition |
|---|---|
| **dataclass** | A class decorated with `@dataclass` that auto-generates `__init__`/`__repr__`/`__eq__`; Python's `record` / Lombok `@Data`. |
| **Pydantic BaseModel** | A base class that turns typed fields into a validated, (de)serializable DTO; validation runs on construction. |
| **type hint** | An annotation (`x: int`, `-> str`) used by IDEs/mypy/Pydantic but not enforced by the interpreter at runtime. |
| **coroutine** | The object returned by calling an `async def` function; runs only when awaited or scheduled on the loop. |
| **event loop** | The single-threaded scheduler that runs ready coroutines and resumes them when their awaited I/O completes. |
| **async/await** | Keywords to define (`async def`) and suspend on (`await`) coroutines, yielding the loop instead of blocking a thread. |
| **ABC** | Abstract Base Class — a class with `@abstractmethod`s that can't be instantiated directly; Python's interface. |
| **comprehension** | Compact `[expr for x in xs if cond]` syntax for building lists/dicts/sets; replaces Java Stream map/filter/collect. |
| **f-string** | A string literal prefixed with `f` that interpolates expressions inline, e.g. `f"Hi {name}"`; like `String.format`. |
| **virtual environment** | An isolated per-project Python interpreter + dependency space created with `venv`; like a Maven/Gradle project scope. |
