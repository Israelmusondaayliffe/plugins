#!/usr/bin/env python3
"""Create a durable Gauntlet session handoff."""

import sys

from gauntletctl import main


if __name__ == "__main__":
    raise SystemExit(main(["handoff", *sys.argv[1:]]))
