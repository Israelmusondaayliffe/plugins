#!/usr/bin/env python3
"""Record current Gauntlet resource consumption."""

import sys

from gauntletctl import main


if __name__ == "__main__":
    raise SystemExit(main(["usage", *sys.argv[1:]]))
