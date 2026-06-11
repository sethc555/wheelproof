"""Empirically determine which packages' ORIGINAL sdists fail to build today.

The definitive broken-now gate. Static scan findings are candidates only —
the first batch found 14/26 static pkg_resources flags were false positives
(guarded imports, pinned build deps), and missed the ez_setup breakage class
entirely. So: download the sdist, build it against latest setuptools, record
the verdict. Resumable JSONL, container-only (executes setup.py from PyPI).
"""

from __future__ import annotations

import json
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import scan as scan_mod
from . import verify as verify_mod


def select_at_risk(results_jsonl: Path) -> list[str]:
    names = []
    for line in results_jsonl.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if "error" not in record and record.get("at_risk"):
            names.append(record["package"])
    return names


def check_one(name: str) -> dict:
    row = {"package": name}
    try:
        version, url = scan_mod._latest_sdist(name)
        row["version"] = version
        blob = scan_mod._fetch(url, max_bytes=scan_mod.MAX_SDIST_BYTES)
    except Exception as exc:
        row.update(builds=None, error=f"fetch: {exc}"[:200])
        return row
    try:
        with tempfile.TemporaryDirectory(prefix="wheelproof-bc-") as tmp:
            root = scan_mod._extract_sdist(blob, Path(tmp))
            out = Path(tmp) / "out"
            out.mkdir()
            try:
                verify_mod.build_wheel(root, out)
                row["builds"] = True
            except verify_mod.BuildError as exc:
                text = str(exc)
                row["builds"] = False
                if "pkg_resources" in text:
                    row["cause"] = "pkg_resources"
                elif "use_2to3" in text:
                    row["cause"] = "use_2to3"
                elif "timed out" in text:
                    row["cause"] = "timeout"
                else:
                    row["cause"] = "other"
                row["error"] = text[:120] + " ||| " + text[-500:]
    except Exception as exc:
        row.update(builds=None, error=f"extract: {exc}"[:200])
    return row


def run(results_jsonl: Path, output: Path, workers: int = 3) -> None:
    names = select_at_risk(results_jsonl)
    done: set[str] = set()
    if output.exists():
        for line in output.read_text().splitlines():
            try:
                done.add(json.loads(line)["package"])
            except (json.JSONDecodeError, KeyError):
                continue
    todo = [n for n in names if n not in done]
    print(f"{len(names)} at-risk, {len(done)} already checked, {len(todo)} to go", file=sys.stderr)

    output.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    with output.open("a") as out, ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(check_one, n): n for n in todo}
        for i, future in enumerate(as_completed(futures), 1):
            row = future.result()
            out.write(json.dumps(row) + "\n")
            out.flush()
            verdict = "BUILDS" if row.get("builds") else (
                f"FAILS ({row.get('cause','?')})" if row.get("builds") is False else "ERROR"
            )
            counts[verdict.split(" ")[0]] = counts.get(verdict.split(" ")[0], 0) + 1
            print(f"[{i}/{len(todo)}] {row['package']}: {verdict}", file=sys.stderr)
    print("done: " + json.dumps(counts), file=sys.stderr)
