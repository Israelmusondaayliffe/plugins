#!/usr/bin/env bash
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENGINE="$PLUGIN_ROOT/skills/last30days/scripts/last30days.py"

choose_python() {
  local candidate
  if [[ -n "${LAST30DAYS_PYTHON:-}" ]]; then
    printf '%s\n' "$LAST30DAYS_PYTHON"
    return
  fi

  for candidate in python3.14 python3.13 python3.12; do
    if command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"
      return
    fi
  done

  if command -v uv >/dev/null 2>&1; then
    candidate="$(uv python find '>=3.12' 2>/dev/null || true)"
    if [[ -n "$candidate" && -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return
    fi
  fi

  printf '%s\n' "No Python 3.12+ runtime found. Install Python 3.12 or run: uv python install 3.12" >&2
  exit 2
}

PYTHON_BIN="$(choose_python)"
exec "$PYTHON_BIN" "$ENGINE" "$@"
