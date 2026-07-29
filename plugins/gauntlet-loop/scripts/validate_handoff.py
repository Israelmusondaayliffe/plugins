#!/usr/bin/env python3
"""Validate a Gauntlet session handoff."""

import sys

from gauntletctl import main


if __name__ == "__main__":
    raise SystemExit(main(["validate-handoff", *sys.argv[1:]]))
