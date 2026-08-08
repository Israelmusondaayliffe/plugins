"""Conservative explicit-activation classifier for Sol Advisor routing regressions."""

from __future__ import annotations

import re


EXPLICIT_ACTIVATION = (
    re.compile(r"(?:^|[.!]\s+)(?:please\s+)?use\s+(?:the\s+)?sol(?:[-\s]+)advisor\b", re.IGNORECASE),
    re.compile(
        r"(?:^|[.!]\s+)(?:please\s+)?run\s+(?:this|the\s+task)\s+as\s+(?:a\s+)?multi[-\s]thread\s+session\b",
        re.IGNORECASE,
    ),
)
REVOCATION = re.compile(
    r"\b(?:do\s+not|don't|never|no\s+longer)\s+(?:use|activate|run)\s+(?:the\s+)?(?:sol(?:[-\s]+)advisor|it|this)\b|\bactually\s*,?\s*no\b",
    re.IGNORECASE,
)


def is_explicit_activation(request: str) -> bool:
    """Return true only for an unrevoked imperative activation request."""
    if not isinstance(request, str) or not request.strip():
        return False
    return not REVOCATION.search(request) and any(pattern.search(request) for pattern in EXPLICIT_ACTIVATION)
