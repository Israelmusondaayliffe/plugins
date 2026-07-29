#!/usr/bin/env python3
"""Validate a Gauntlet project workspace."""

import sys

from gauntletctl import main


if __name__ == "__main__":
    raise SystemExit(main(["validate", *sys.argv[1:]]))
