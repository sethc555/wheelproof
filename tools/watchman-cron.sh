#!/bin/bash
# Daily: canary + threads. Sundays: also recheck broken packages.
cd "$(dirname "$0")/.." || exit 1
# Use the repo venv (python3 -m venv .venv && .venv/bin/pip install build), NOT
# the system interpreter: recheck builds sdists on the host, and the user
# site-packages was found shadowing PyPA `build` (see verify.HarnessError).
PY=.venv/bin/python
[ -x "$PY" ] || { echo "watchman: $PY missing — create it: python3 -m venv .venv && .venv/bin/pip install build" >> watchman.log; exit 1; }
{
  echo "=== watchman run $(date -u '+%F %T UTC') ==="
  PYTHONPATH=src "$PY" -c "
from pathlib import Path
from wheelproof import watchman
root = Path('.')
watchman.canary(root)
watchman.threads(root)
import datetime
if datetime.date.today().weekday() == 6:
    watchman.recheck(root)
"
} >> watchman.log 2>&1
