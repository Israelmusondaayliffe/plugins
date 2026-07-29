#!/usr/bin/env python3
"""Initialize a Gauntlet project workspace."""

import sys

from gauntletctl import main


if __name__ == "__main__":
    raise SystemExit(main(["init", *sys.argv[1:]]))
