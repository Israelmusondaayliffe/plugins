#!/usr/bin/env python3
"""Assemble the final Gauntlet evidence report."""

import sys

from gauntletctl import main


if __name__ == "__main__":
    raise SystemExit(main(["evidence", *sys.argv[1:]]))
