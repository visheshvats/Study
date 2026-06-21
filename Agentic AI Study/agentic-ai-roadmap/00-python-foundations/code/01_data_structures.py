"""01_data_structures.py — Python core data structures for a Java dev.

Covers lists, dicts, comprehensions, the ternary expression, and JSON I/O.
Every snippet is mapped to its Java/Stream/Jackson equivalent in comments.

Run it:  python 01_data_structures.py
"""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lists  ~  java.util.ArrayList<E>
# ---------------------------------------------------------------------------
def list_demo() -> list[str]:
    """Demonstrate list operations vs ArrayList methods."""
    # Java: List<String> names = new ArrayList<>(Arrays.asList("Alice","Bob","Charlie"));
    names: list[str] = ["Alice", "Bob", "Charlie"]

    names.append("Dave")  # Java: names.add("Dave")
    names.remove("Bob")   # Java: names.remove("Bob")
    first = names[0]      # Java: names.get(0)   — NOTE: 0-indexed, like Java
    count = len(names)    # Java: names.size()

    logger.info("first=%s, count=%d, names=%s", first, count, names)
    return names


# ---------------------------------------------------------------------------
# Dicts  ~  java.util.HashMap<K,V>   (the workhorse of all LLM/JSON code)
# ---------------------------------------------------------------------------
def dict_demo() -> dict[str, Any]:
    """Demonstrate dict access patterns vs HashMap methods."""
    # Java: Map<String,Object> user = new HashMap<>(); user.put("name","Alice"); ...
    user: dict[str, Any] = {
        "name": "Alice",
        "role": "user",
        "metadata": {"session_id": "abc123"},
    }

    direct = user["name"]                     # Java: map.get("name") — but raises KeyError if absent
    safe = user.get("age", "unknown")         # Java: map.getOrDefault("age", "unknown")
    nested = user["metadata"]["session_id"]   # Nested map access
    keys = list(user.keys())                  # Java: new ArrayList<>(map.keySet())
    values = list(user.values())              # Java: new ArrayList<>(map.values())
    entries = list(user.items())              # Java: map.entrySet()

    logger.info("direct=%s safe=%s nested=%s", direct, safe, nested)
    logger.info("keys=%s values=%s entries=%s", keys, values, entries)
    return user


# ---------------------------------------------------------------------------
# Comprehensions  ~  Stream API (map / filter / collect)
# ---------------------------------------------------------------------------
def comprehension_demo(names: list[str]) -> None:
    """Show list & dict comprehensions vs Java Streams."""
    # Java: names.stream().filter(n -> n.startsWith("A")).collect(toList());
    a_names = [n for n in names if n.startswith("A")]

    # Java: names.stream().map(String::toUpperCase).collect(toList());
    upper = [n.upper() for n in names]

    # Dict comprehension —
    # Java: scores.entrySet().stream()
    #            .collect(toMap(e -> e.getKey().toUpperCase(), Map.Entry::getValue));
    scores = {"Alice": 95, "Bob": 87}
    upper_keys = {k.upper(): v for k, v in scores.items()}

    logger.info("a_names=%s upper=%s upper_keys=%s", a_names, upper, upper_keys)


# ---------------------------------------------------------------------------
# Ternary (conditional expression)  ~  Java's `cond ? a : b`
# ---------------------------------------------------------------------------
def ternary_demo() -> int:
    """Demonstrate the conditional expression.

    NOTE: the source guide had a bug — it used `x` before defining it.
    Here we define `x` first so the example actually runs (computes abs(x)).
    """
    x = -7  # FIX: source referenced undefined `x`; define it first.
    # Java: int result = x > 0 ? x : -x;
    result = x if x > 0 else -x
    logger.info("x=%d -> result=%d (manual abs)", x, result)
    return result


# ---------------------------------------------------------------------------
# JSON  ~  Jackson ObjectMapper
# ---------------------------------------------------------------------------
def json_demo() -> dict[str, Any]:
    """Round-trip JSON to a string and to a temp file."""
    data: dict[str, Any] = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "messages": [],
    }

    # Jackson: objectMapper.writeValueAsString(data)
    json_str = json.dumps(data, indent=2)
    # Jackson: objectMapper.readValue(json, Map.class)
    parsed = json.loads(json_str)
    logger.info("serialized %d chars; round-tripped model=%s", len(json_str), parsed["model"])

    # File round-trip using a temp dir so the demo leaves no junk behind.
    # `with open(...)` is Python's try-with-resources — auto-closes the file.
    tmp = Path(tempfile.gettempdir()) / "phase0_config.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)  # write to file
    with tmp.open(encoding="utf-8") as f:
        config = json.load(f)         # read from file
    logger.info("wrote+read %s, max_tokens=%d", tmp.name, config["max_tokens"])
    tmp.unlink(missing_ok=True)       # cleanup
    return parsed


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    names = list_demo()
    dict_demo()
    comprehension_demo(names)
    ternary_demo()
    json_demo()
    logger.info("Data structures demo complete.")
