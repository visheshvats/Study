"""
Input/output guardrails. See Phase 10 (10-production-engineering) section 10.3.
"""
from __future__ import annotations

import re
from typing import Tuple


class Guardrails:
    _INJECTION = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"you\s+are\s+now\s+",
        r"jailbreak",
        # TODO: add more patterns + an allowlist to reduce false positives.
    ]
    _SENSITIVE = [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        # TODO: add credit-card / email / phone patterns as needed.
    ]

    @classmethod
    def validate_input(cls, text: str) -> Tuple[bool, str]:
        """Reject over-long or injection-looking input."""
        # TODO: length cap + scan cls._INJECTION; return (ok, reason)
        raise NotImplementedError

    @classmethod
    def sanitize_output(cls, text: str) -> str:
        """Redact sensitive patterns from the model's output."""
        # TODO: re.sub each cls._SENSITIVE pattern -> "[REDACTED]"
        raise NotImplementedError


if __name__ == "__main__":
    print("Implement validate_input/sanitize_output.")
