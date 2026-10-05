#!/usr/bin/env bash
# One command for a run — a platform or both side by side, the whole regression or a module:
#   scripts/qa.sh <ios|android|both> <all|module|path> [--name NAME] [--sequential] [--dry-run] [-- pytest args]
# See scripts/qa.py (its --help) and PARALLEL-RUNS.md.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec uv run python scripts/qa.py "$@"
