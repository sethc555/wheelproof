"""Watchman: detect the events that change what this project should do next.

Three sensors:
- canary: does the dash-key setup.cfg removal NOW fail against latest
  setuptools? Empirical, not changelog-reading: build a minimal package whose
  setup.cfg uses the doomed dash-separated keys. The day this flips to FAIL,
  1,153 packages break and the corpus stops being inventory.
- threads: did any outreach thread (outreach/threads.json) gain comments,
  close, or merge since last look?
- recheck: do any verified-broken packages NOW build (i.e., a fixing release
  shipped, like impyla 0.24)?

State lives in watchman-state.json (gitignored); events append to
WATCHMAN-ALERTS.md so the next session sees them. No sends, no pushes —
watchman only watches.
"""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CANARY_SETUP_CFG = """\
[metadata]
name = wheelproof-canary
version = 0.0.1
author-email = canary@example.invalid
description-file = README.md

[options]
py_modules = canary
"""


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _alert(repo_root: Path, line: str) -> None:
    alerts = repo_root / "WATCHMAN-ALERTS.md"
    existing = alerts.read_text() if alerts.exists() else "# Watchman alerts\n\n"
    alerts.write_text(existing + f"- {_now()}: {line}\n")
    print(f"ALERT: {line}")


def canary(repo_root: Path) -> bool:
    """Returns True if the axe has dropped (dash keys now fail)."""
    with tempfile.TemporaryDirectory(prefix="wp-canary-") as tmp:
        src = Path(tmp) / "canary"
        src.mkdir()
        (src / "setup.py").write_text("from setuptools import setup\nsetup()\n")
        (src / "setup.cfg").write_text(CANARY_SETUP_CFG)
        (src / "canary.py").write_text("x = 1\n")
        (src / "README.md").write_text("canary\n")
        import os

        proc = subprocess.run(
            ["docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}",
             "-e", "HOME=/tmp", "-v", f"{src}:/c", "python:3.12", "bash", "-c",
             "python -m venv /tmp/v && /tmp/v/bin/pip install -q build && "
             "/tmp/v/bin/python -m build --wheel --outdir /tmp/o /c"],
            capture_output=True, text=True, timeout=900,
        )
    version = subprocess.run(
        ["python3", "-c",
         "import json,urllib.request;"
         "print(json.load(urllib.request.urlopen('https://pypi.org/pypi/setuptools/json'))['info']['version'])"],
        capture_output=True, text=True,
    ).stdout.strip()
    if proc.returncode != 0:
        blob = proc.stdout + proc.stderr
        if any(s in blob for s in ("dash-separated", "author-email", "invalid option", "underscore")):
            _alert(repo_root,
                   f"**THE AXE DROPPED** — dash-separated setup.cfg keys now FAIL against "
                   f"setuptools {version}. 1,153 prepared fixes just became urgent. "
                   f"Activate: publish corpus pointer, re-run buildcheck, expect inbound.")
            return True
        _alert(repo_root,
               f"canary failed for an UNEXPECTED reason against setuptools {version} "
               f"(not the dash-key error) — investigate, do not assume the axe: "
               f"{blob.strip().splitlines()[-1][:160]}")
        return False
    print(f"canary: dash keys still build (setuptools {version})")
    # positive control: a deliberately broken package MUST fail, or the
    # harness itself is sick and "still fine" means nothing
    with tempfile.TemporaryDirectory(prefix="wp-canaryctl-") as tmp:
        src = Path(tmp) / "ctl"
        src.mkdir()
        (src / "setup.py").write_text("import nonexistent_module_wp_control\n")
        import os

        proc = subprocess.run(
            ["docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}",
             "-e", "HOME=/tmp", "-v", f"{src}:/c", "python:3.12", "bash", "-c",
             "python -m venv /tmp/v && /tmp/v/bin/pip install -q build && "
             "/tmp/v/bin/python -m build --wheel --outdir /tmp/o /c"],
            capture_output=True, text=True, timeout=900,
        )
        if proc.returncode == 0:
            _alert(repo_root,
                   "canary HARNESS UNHEALTHY: the deliberately-broken control package "
                   "BUILT — failure detection is not working; all 'still fine' verdicts "
                   "since the last healthy control are suspect")
    return False


def threads(repo_root: Path) -> int:
    threads_file = repo_root / "outreach" / "threads.json"
    state_file = repo_root / "watchman-state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    seen = state.setdefault("threads", {})
    changes = 0
    for t in json.loads(threads_file.read_text()):
        key = f"{t['repo']}#{t['number']}"
        proc = subprocess.run(
            ["gh", "api", f"repos/{t['repo']}/issues/{t['number']}",
             "--jq", '{state: .state, comments: .comments}'],
            capture_output=True, text=True, timeout=60,
        )
        if proc.returncode != 0:
            continue
        cur = json.loads(proc.stdout)
        old = seen.get(key)
        if old is not None and (cur["comments"] != old["comments"] or cur["state"] != old["state"]):
            _alert(repo_root,
                   f"thread {key}: {old['state']}/{old['comments']}c -> "
                   f"{cur['state']}/{cur['comments']}c — read and consider replying")
            changes += 1
        seen[key] = cur
    state_file.write_text(json.dumps(state, indent=2))
    print(f"threads: {len(seen)} watched, {changes} changed")
    return changes


def recheck(repo_root: Path) -> int:
    """Rebuild previously-broken packages' latest sdists; alert on newly-fixed."""
    from . import buildcheck as bc

    state_file = repo_root / "watchman-state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    fixed_seen = set(state.setdefault("fixed", []))
    rows = [json.loads(l) for l in (repo_root / "results" / "buildcheck.jsonl").read_text().splitlines()]
    broken = [r["package"] for r in rows if r.get("builds") is False and r["package"] not in fixed_seen]
    newly = 0
    for name in broken:
        row = bc.check_one(name)
        if row.get("builds") is True:
            _alert(repo_root,
                   f"**{name} {row.get('version','?')} now BUILDS** — a fixing release "
                   f"shipped; verify, thank if we have a thread, update broken-now-v2")
            fixed_seen.add(name)
            newly += 1
        print(f"recheck {name}: {'fixed' if row.get('builds') else 'still broken'}", file=sys.stderr)
    state["fixed"] = sorted(fixed_seen)
    state_file.write_text(json.dumps(state, indent=2))
    print(f"recheck: {len(broken)} rechecked, {newly} newly fixed")
    return newly
