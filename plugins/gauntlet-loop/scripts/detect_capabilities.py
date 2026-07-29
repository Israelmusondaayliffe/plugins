#!/usr/bin/env python3
"""Record the current runtime capability envelope."""

import sys

from gauntletctl import main


if __name__ == "__main__":
    raise SystemExit(main(["capabilities", *sys.argv[1:]]))
