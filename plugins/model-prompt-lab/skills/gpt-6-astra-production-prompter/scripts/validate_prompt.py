#!/usr/bin/env python3
"""Run focused static checks for a provisional GPT-6 Astra prompt."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_input() -> tuple[str, str | None]:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?")
    parser.add_argument("--text")
    parser.add_argument("--target-host", choices=("codex",), help="Use the recorded Codex qualification; this does not qualify API or other hosts")
    args = parser.parse_args()
    if bool(args.path) == bool(args.text):
        parser.error("provide either a prompt file or --text")
    text = args.text if args.text is not None else Path(args.path).read_text(encoding="utf-8")
    return text, args.target_host


def main() -> int:
    text, target_host = load_input()
    lower = text.lower()
    failures: list[str] = []
    warnings: list[str] = []

    # Exact Codex model ID observed and independently qualified on 2026-09-04.
    # See references/field-evidence.md. Other hosts and aliases remain unverified.
    verified_slugs = {"gpt-6-astra"} if target_host == "codex" else set()
    invented_slugs = [slug for slug in re.findall(r"\bgpt[-_.]?6[-_.]astra(?:[-_.][a-z0-9]+)*\b", lower) if slug not in verified_slugs]
    if invented_slugs:
        failures.append("unverified Astra model slug for the selected target; use the exact qualified Codex ID with --target-host codex, or name GPT-6 Astra in prose pending host verification")

    lines = [re.sub(r"^[\s*\d.)-]+", "", line.strip()).lower() for line in text.splitlines()]
    repeated = sorted({line for line in lines if len(line) > 30 and lines.count(line) > 1})
    if repeated:
        warnings.append(f"{len(repeated)} repeated instruction line(s) found")

    emphasis = len(re.findall(r"\b(?:critical|must|always)\b", lower))
    if emphasis > 4:
        warnings.append(f"{emphasis} strong-emphasis terms found; keep absolute wording for real invariants")

    interface_signals = ("interface", "website", "site", "dashboard", "app ui", "frontend")
    if any(signal in lower for signal in interface_signals):
        restraint_signals = ("do not add", "only the requested", "no extra", "not a landing page")
        if not any(signal in lower for signal in restraint_signals):
            warnings.append("interface prompt has no explicit scope-restraint line")

    if "computer use" in lower or "computer control" in lower:
        if not any(signal in lower for signal in ("verify", "evidence", "completion condition", "success")):
            warnings.append("computer-control prompt does not name a completion or verification surface")

    result = {"valid": not failures, "failures": failures, "warnings": warnings}
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
