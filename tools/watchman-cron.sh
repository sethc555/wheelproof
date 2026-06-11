#!/bin/bash
# Daily: canary + threads. Sundays: also recheck broken packages.
cd "$(dirname "$0")/.." || exit 1
{
  echo "=== watchman run $(date -u '+%F %T UTC') ==="
  PYTHONPATH=src python3 -c "
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
