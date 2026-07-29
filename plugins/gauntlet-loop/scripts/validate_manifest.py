#!/usr/bin/env python3
"""Validate the Gauntlet plugin manifest through the bundle contract."""

from pathlib import Path
import sys

from verify_bundle import verify


if __name__ == "__main__":
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    result = verify(root)
    manifest_errors = [error for error in result["errors"] if "manifest" in error]
    print("manifest valid" if not manifest_errors else "\n".join(manifest_errors))
    raise SystemExit(0 if not manifest_errors else 1)
