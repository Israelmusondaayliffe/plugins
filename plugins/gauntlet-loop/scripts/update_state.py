#!/usr/bin/env python3
"""Apply a validated Gauntlet state transition."""

import sys

from gauntletctl import main


if __name__ == "__main__":
    raise SystemExit(main(["transition", *sys.argv[1:]]))
