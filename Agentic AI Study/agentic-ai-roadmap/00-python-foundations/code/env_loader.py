"""env_loader.py — central configuration loader.

Put this import at the top of every file that needs secrets/config.

Java analogy
------------
This is the Python equivalent of Spring Boot reading `application.properties`
(or `application.yml`) and exposing values via `@Value` / `Environment`.
Here, `python-dotenv` reads a local `.env` file into process environment
variables, and `os.getenv` is your `environment.getProperty(...)`.

Why a module and not inline code?
Importing this module runs `load_dotenv()` exactly once (modules are cached
like singletons), so config is loaded the moment any file imports it.
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# load_dotenv() looks for a `.env` file walking up from the cwd.
# Returns True if a file was found and loaded, False otherwise.
# This is a no-op if the file is missing — perfectly fine for this phase,
# because none of the Phase 0 demos actually make a real network/LLM call.
_loaded = load_dotenv()
if _loaded:
    logger.info(".env file loaded successfully")
else:
    logger.info("No .env file found — using process environment only (OK for Phase 0)")


# --- Typed accessors -------------------------------------------------------
# os.getenv returns Optional[str] (None if unset) — like a Map.get that may
# return null. We surface them as module-level constants for convenience.
ANTHROPIC_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
OPENAI_KEY: str | None = os.getenv("OPENAI_API_KEY")
LANGCHAIN_KEY: str | None = os.getenv("LANGCHAIN_API_KEY")


def require_key(name: str) -> str:
    """Fetch a required environment variable or fail loudly.

    Java analogy: like a `@Value` with no default — fail fast on startup if a
    required property is missing, rather than NPE-ing deep in a request.

    Args:
        name: The environment variable name, e.g. ``"ANTHROPIC_API_KEY"``.

    Returns:
        The non-empty value of the variable.

    Raises:
        RuntimeError: If the variable is unset or blank.
    """
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not set. "
            f"Add it to your .env file (and NEVER commit that file)."
        )
    return value


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    # Demo: report which keys are present WITHOUT printing the secret values.
    # (Printing secrets to logs is exactly the kind of leak you must avoid.)
    for label, value in [
        ("ANTHROPIC_API_KEY", ANTHROPIC_KEY),
        ("OPENAI_API_KEY", OPENAI_KEY),
        ("LANGCHAIN_API_KEY", LANGCHAIN_KEY),
    ]:
        status = "SET" if value else "not set"
        logger.info("Config check — %s: %s", label, status)

    logger.info("env_loader demo complete. (No secrets were printed.)")
