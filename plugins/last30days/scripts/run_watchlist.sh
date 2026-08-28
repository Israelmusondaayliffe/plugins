#!/usr/bin/env bash
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WATCHLIST="$PLUGIN_ROOT/skills/last30days/scripts/watchlist.py"

if [[ -n "${LAST30DAYS_PYTHON:-}" ]]; then
  PYTHON_BIN="$LAST30DAYS_PYTHON"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.12)"
elif command -v uv >/dev/null 2>&1; then
  PYTHON_BIN="$(uv python find '>=3.12' 2>/dev/null || true)"
else
  PYTHON_BIN=""
fi

if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
  printf '%s\n' "No Python 3.12+ runtime found. Install Python 3.12 or run: uv python install 3.12" >&2
  exit 2
fi

exec "$PYTHON_BIN" "$WATCHLIST" "$@"
