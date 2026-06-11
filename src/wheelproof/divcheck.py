"""Wheel/sdist divergence census.

For each package whose sdist is known to build: build a wheel FROM the
published sdist and compare its payload against the maintainer's own published
pure wheel for the same version. If they differ, the wheel and sdist on PyPI
came from different trees — a quiet supply-chain integrity question nobody
measures.

Verdicts:
- identical: payloads match exactly
- diverged: payload differs (raw file lists recorded; classification of
  benign causes — version stamps, generated code — happens at analysis time,
  never silently here)
- no-pure-wheel: platform wheels only, out of scope
- build-fail / fetch-error: couldn't establish a comparison

Resumable JSONL. Container-only (executes setup.py from PyPI).
"""

from __future__ import annotations

import json
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import scan as scan_mod
from . import verify as verify_mod


def check_one(name: str) -> dict:
    row = {"package": name}
    try:
        version, url = scan_mod._latest_sdist(name)
        row["version"] = version
        blob = scan_mod._fetch(url, max_bytes=scan_mod.MAX_SDIST_BYTES)
    except Exception as exc:
        row.update(verdict="fetch-error", error=str(exc)[:200])
        return row
    try:
        with tempfile.TemporaryDirectory(prefix="wp-div-") as tmp:
            root = scan_mod._extract_sdist(blob, Path(tmp))
            out = Path(tmp) / "ours"
            out.mkdir()
            try:
                ours = verify_mod.build_wheel(root, out)
            except verify_mod.BuildError as exc:
                row.update(verdict="build-fail", error=str(exc)[-300:])
                return row
            wheel_name, wheel_version = ours.name.split("-")[0:2]
            try:
                published = verify_mod.fetch_published_wheel(wheel_name, wheel_version, Path(tmp))
            except verify_mod.BuildError as exc:
                row.update(verdict="no-pure-wheel", error=str(exc)[:150])
                return row
            report = verify_mod.compare(verify_mod.read_wheel(published), verify_mod.read_wheel(ours))
            if report.passed:
                row["verdict"] = "identical"
            else:
                row.update(
                    verdict="diverged",
                    only_in_published=report.payload_only_a[:20],
                    only_in_sdist_build=report.payload_only_b[:20],
                    content_differs=report.payload_changed[:20],
                    entry_points_changed=report.entry_points_changed,
                )
    except Exception as exc:
        row.update(verdict="fetch-error", error=f"unexpected: {exc}"[:200])
    return row


def _stable_check(name: str, runs: int) -> dict:
    row = check_one(name)
    if runs < 2 or row.get("verdict") not in ("identical", "diverged"):
        return row
    second = check_one(name)
    keys = ("verdict", "only_in_published", "only_in_sdist_build", "content_differs", "entry_points_changed")
    if any(row.get(k) != second.get(k) for k in keys):
        return {"package": name, "verdict": "UNSTABLE",
                "run1": {k: row.get(k) for k in keys}, "run2": {k: second.get(k) for k in keys}}
    row["stable_runs"] = 2
    return row


def run(buildcheck_jsonl: Path | None, output: Path, workers: int = 3,
        limit: int | None = None, names: list[str] | None = None, runs: int = 1) -> None:
    if names is None:
        names = []
        for line in buildcheck_jsonl.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("builds") is True:
                names.append(r["package"])
    if limit:
        names = names[:limit]
    done: set[str] = set()
    if output.exists():
        for line in output.read_text().splitlines():
            try:
                done.add(json.loads(line)["package"])
            except (json.JSONDecodeError, KeyError):
                continue
    todo = [n for n in names if n not in done]
    print(f"{len(names)} buildable, {len(done)} already checked, {len(todo)} to go", file=sys.stderr)

    counts: dict[str, int] = {}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a") as out, ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_stable_check, n, runs): n for n in todo}
        for i, future in enumerate(as_completed(futures), 1):
            row = future.result()
            out.write(json.dumps(row) + "\n")
            out.flush()
            counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
            print(f"[{i}/{len(todo)}] {row['package']}: {row['verdict']}", file=sys.stderr)
    print("done: " + json.dumps(counts), file=sys.stderr)
