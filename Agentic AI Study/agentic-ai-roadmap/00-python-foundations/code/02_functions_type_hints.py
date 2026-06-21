"""02_functions_type_hints.py — functions, defaults, *args/**kwargs, type hints.

Type hints in Python are advisory at runtime (the interpreter does NOT enforce
them) but power your IDE, mypy, and Pydantic/FastAPI — think of them as the
compile-time generics & method signatures you already trust in Java, except
checked by a separate tool (mypy) rather than javac.

Run it:  python 02_functions_type_hints.py
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


# Java: public String greet(String name, int times) { ... }
def greet(name: str, times: int = 1) -> str:
    """Return a greeting repeated ``times`` times.

    ``times: int = 1`` is a default argument — Java has no native default
    params, so you'd overload the method (greet(name) / greet(name, times)).
    """
    return f"Hello, {name}! " * times


def create_message(
    content: str,
    role: str = "user",
    metadata: Optional[dict[str, Any]] = None,  # Optional[X] == X | None
) -> dict[str, Any]:
    """Build a chat message dict.

    IMPORTANT (common Java-dev trap): the default is ``None``, NOT ``{}``.
    A mutable default like ``metadata: dict = {}`` is evaluated ONCE at
    function-definition time and shared across all calls — a classic Python
    footgun with no Java equivalent. Use ``None`` then create a fresh dict.
    """
    msg: dict[str, Any] = {"role": role, "content": content}
    if metadata:
        msg["metadata"] = metadata
    return msg


# *args == Java varargs (String...); **kwargs == an arbitrary named-param map.
def build_prompt(*parts: str, separator: str = "\n\n") -> str:
    """Join prompt fragments with a separator.

    Java: String build(String... parts) — but Python also gives you the
    keyword-only ``separator`` after the varargs, which Java cannot express.
    """
    return separator.join(parts)


def safe_parse_json(text: str) -> tuple[Optional[dict], Optional[str]]:
    """Parse JSON, returning ``(data, error)`` — a Go-style result tuple.

    Python has no checked exceptions, so a common pattern is to convert a
    risky call into an explicit ``(value, error)`` tuple the caller must
    inspect. Java would either throw a checked exception or return Optional.
    """
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, str(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    logger.info("greet -> %r", greet("Alice", times=2))

    msg = create_message("Hello", metadata={"session_id": "abc123"})
    logger.info("create_message -> %s", msg)

    # Prove the mutable-default trap is avoided: two calls don't share state.
    a = create_message("first")
    b = create_message("second")
    logger.info("independent messages? %s", a is not b and "metadata" not in a)

    prompt = build_prompt("Context:", "Answer:", "Reasoning:", separator="\n---\n")
    logger.info("build_prompt ->\n%s", prompt)

    data, error = safe_parse_json('{"valid": true}')
    logger.info("parse ok -> data=%s error=%s", data, error)

    bad_data, bad_error = safe_parse_json("{not json}")
    logger.info("parse bad -> data=%s error=%s", bad_data, bad_error)

    logger.info("Functions & type hints demo complete.")
