"""Pristine-HEAD check: the mandatory first step before patching anything.

Given a git URL or local checkout: full-chain build (sdist, then wheel FROM
that sdist) of the PRISTINE tree. The verdict decides everything downstream:

- builds  -> if the released sdist is broken, this is fixed-at-HEAD or a
             release-tooling artifact: file a release request, write NO patch
- fails   -> a patch against HEAD is justified; the error tail says for what

Run inside a container — this executes the repo's setup.py.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from . import verify as verify_mod


def headcheck(target: str, subdir: str | None = None) -> dict:
    row: dict = {"target": target}
    with tempfile.TemporaryDirectory(prefix="wp-head-") as tmp:
        if target.startswith(("http://", "https://", "git@")):
            clone = Path(tmp) / "repo"
            proc = subprocess.run(
                ["git", "clone", "--depth", "50", target, str(clone)],
                capture_output=True, text=True, timeout=600,
            )
            if proc.returncode != 0:
                row.update(verdict="clone-failed", error=proc.stderr[-300:])
                return row
            subprocess.run(["git", "-C", str(clone), "fetch", "--tags", "--quiet"],
                           capture_output=True, timeout=300)
            src = clone
        else:
            src = Path(target)
            if not src.is_dir():
                row.update(verdict="error", error=f"{target} is not a directory or URL")
                return row
        if subdir:
            src = src / subdir
        out = Path(tmp) / "out"
        out.mkdir()
        proc = subprocess.run(
            [sys.executable, "-m", "build", "--outdir", str(out), str(src)],
            capture_output=True, text=True, timeout=verify_mod.BUILD_TIMEOUT * 2,
        )
        if proc.returncode == 0:
            row["verdict"] = "pristine-head-builds"
            row["guidance"] = ("HEAD is healthy. If the RELEASED sdist is broken, do not patch: "
                               "file a release request (fixed-at-HEAD or release-tooling artifact).")
        else:
            blob = proc.stdout + proc.stderr
            row["verdict"] = "pristine-head-fails"
            row["error"] = blob[-500:]
            row["guidance"] = "A minimal patch against HEAD is justified; fix exactly what the error shows."
    return row
