"""Unsupervised batch conversion: scan results -> convert -> verify -> corpus entries.

Selects packages with at least one high-severity finding from a batch-scan JSONL,
then per package: fetch latest sdist, extract, convert in a copy, run the
wheel-diff gate. One result directory per package under the corpus dir:

    corpus/<name>/result.json     always — status + detail + metadata drift
    corpus/<name>/pyproject.toml  on pass — the proven conversion

Statuses: pass, verify-fail, convert-error, build-error, fetch-error.
Resumable: packages with an existing result.json are skipped. Every step is
timeboxed (py2cfg 120s, each wheel build 600s) so a hostile or broken sdist
cannot stall the run. Run this inside a container — it executes arbitrary
setup.py code from PyPI.
"""

from __future__ import annotations

import json
import sys
import tempfile
import traceback
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import convert as convert_mod
from . import scan as scan_mod
from . import verify as verify_mod


def select_high(results_jsonl: Path) -> list[str]:
    names = []
    for line in results_jsonl.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if "error" in record:
            continue
        if any(f["severity"] == "high" for f in record.get("findings", [])):
            names.append(record["package"])
    return names


def _drift(report: verify_mod.Report) -> dict:
    return {
        "metadata_only_original": [list(t) for t in report.metadata_only_a],
        "metadata_only_converted": [list(t) for t in report.metadata_only_b],
        "metadata_body_changed": report.metadata_body_changed,
        "distinfo_changed": report.distinfo_changed,
    }


def convert_one(name: str, corpus: Path) -> dict:
    entry = {"package": name}
    try:
        version, url = scan_mod._latest_sdist(name)
        entry.update(version=version, sdist_url=url)
        blob = scan_mod._fetch(url, max_bytes=scan_mod.MAX_SDIST_BYTES)
    except Exception as exc:
        entry.update(status="fetch-error", detail=f"{type(exc).__name__}: {exc}")
        return entry

    try:
        with tempfile.TemporaryDirectory(prefix="wheelproof-bc-") as tmp:
            root = scan_mod._extract_sdist(blob, Path(tmp))
            if root == Path(tmp):
                entry.update(status="fetch-error", detail="sdist has no single root dir")
                return entry
            outdir = Path(tmp) / (root.name + "-converted")
            try:
                convert_mod.convert(root, outdir)
            except convert_mod.ConvertError as exc:
                entry.update(status="convert-error", detail=str(exc)[:500])
                return entry
            try:
                report = verify_mod.verify(root, outdir)
            except verify_mod.BuildError as exc:
                # head says WHICH tree failed (original vs converted); tail has the error
                entry.update(status="build-error", detail=str(exc)[:150] + " ||| " + str(exc)[-1200:])
                return entry
            if report.passed:
                entry.update(status="pass", drift=_drift(report))
                pkgdir = corpus / name
                pkgdir.mkdir(parents=True, exist_ok=True)
                (pkgdir / "pyproject.toml").write_text(
                    (outdir / "pyproject.toml").read_text(errors="replace")
                )
            else:
                entry.update(
                    status="verify-fail",
                    detail={
                        "payload_only_original": report.payload_only_a,
                        "payload_only_converted": report.payload_only_b,
                        "payload_changed": report.payload_changed,
                        "entry_points_changed": report.entry_points_changed,
                    },
                )
    except Exception as exc:  # unexpected — record, never crash the run
        entry.update(status="convert-error", detail=f"unexpected: {traceback.format_exc()[-500:]}")
    return entry


def run(results_jsonl: Path, corpus: Path, workers: int = 2, limit: int | None = None) -> None:
    names = select_high(results_jsonl)
    if limit:
        names = names[:limit]
    todo = [n for n in names if not (corpus / n / "result.json").exists()]
    print(f"{len(names)} selected, {len(names) - len(todo)} already done, {len(todo)} to go", file=sys.stderr)

    counts: Counter[str] = Counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(convert_one, n, corpus): n for n in todo}
        done = 0
        for future in as_completed(futures):
            entry = future.result()
            name = entry["package"]
            pkgdir = corpus / name
            pkgdir.mkdir(parents=True, exist_ok=True)
            (pkgdir / "result.json").write_text(json.dumps(entry, indent=2) + "\n")
            counts[entry["status"]] += 1
            done += 1
            print(f"[{done}/{len(todo)}] {name}: {entry['status']}", file=sys.stderr)

    print("done: " + ", ".join(f"{k}={v}" for k, v in counts.most_common()), file=sys.stderr)


def summarize(corpus: Path) -> str:
    entries = []
    for result in sorted(corpus.glob("*/result.json")):
        entries.append(json.loads(result.read_text()))
    counts = Counter(e["status"] for e in entries)
    lines = [
        "# corpus summary",
        "",
        f"- packages attempted: {len(entries)}",
    ]
    for status, count in counts.most_common():
        lines.append(f"- {status}: {count} ({count / len(entries):.0%})")
    lines += ["", "## verify-fail packages (need eyes)", ""]
    lines += [f"- {e['package']}" for e in entries if e["status"] == "verify-fail"]
    return "\n".join(lines) + "\n"
