#!/usr/bin/env python3
"""Verify that protected Markdown material is unchanged after prose editing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


PATTERNS = {
    "fenced_blocks": re.compile(r"^```[^\n]*\n.*?^```\s*$", re.MULTILINE | re.DOTALL),
    "block_quotes": re.compile(r"(?:^>[^\n]*(?:\n|$))+", re.MULTILINE),
    "inline_code": re.compile(r"(?<!`)`[^`\n]+`(?!`)"),
    "markdown_links": re.compile(r"\[[^\]\n]+\]\([^)\n]+\)"),
}


def protected_material(text: str) -> dict[str, list[str]]:
    """Return protected segments in their source order by category."""
    return {
        name: [match.group(0) for match in pattern.finditer(text)]
        for name, pattern in PATTERNS.items()
    }


def compare_protected(before: str, after: str) -> dict[str, object]:
    """Compare protected segments without judging surrounding prose."""
    before_segments = protected_material(before)
    after_segments = protected_material(after)
    changed = [
        name
        for name in PATTERNS
        if before_segments[name] != after_segments[name]
    ]
    return {
        "valid": not changed,
        "changed_categories": changed,
        "before_counts": {name: len(items) for name, items in before_segments.items()},
        "after_counts": {name: len(items) for name, items in after_segments.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    before = args.before.read_text(encoding="utf-8")
    after = args.after.read_text(encoding="utf-8")
    result = compare_protected(before, after)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
