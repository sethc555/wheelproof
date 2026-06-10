"""Batch scanning over many PyPI packages, with resumable JSONL output.

Package list source: hugovk's top-pypi-packages dataset (BigQuery-derived,
refreshed monthly). Results append to a JSONL file, one object per package;
re-running with the same output file skips packages already scanned.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from pathlib import Path

from . import scan

TOP_URL = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages.min.json"


def top_packages(n: int) -> list[str]:
    data = json.loads(scan._fetch(TOP_URL))
    rows = data.get("rows", [])
    return [row["project"] for row in rows[:n]]


def _scan_one(name: str) -> dict:
    try:
        result = scan.scan(name)
    except Exception as exc:  # record and move on; one bad sdist must not stop the run
        return {"package": name, "error": f"{type(exc).__name__}: {exc}"}
    return json.loads(result.to_json())


def batch_scan(names: list[str], output: Path, workers: int = 8) -> None:
    done: set[str] = set()
    if output.exists():
        for line in output.read_text().splitlines():
            try:
                done.add(json.loads(line)["package"])
            except (json.JSONDecodeError, KeyError):
                continue
    todo = [n for n in names if n not in done]
    print(f"{len(done)} already scanned, {len(todo)} to go", file=sys.stderr)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a") as out, ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_scan_one, name): name for name in todo}
        completed = 0
        for future in as_completed(futures):
            record = future.result()
            out.write(json.dumps(record) + "\n")
            out.flush()
            completed += 1
            status = "ERROR" if "error" in record else ("AT-RISK" if record.get("at_risk") else "ok")
            print(f"[{completed}/{len(todo)}] {record['package']}: {status}", file=sys.stderr)


def summarize(path: Path) -> str:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    scanned = [r for r in records if "error" not in r]
    errors = [r for r in records if "error" in r]
    at_risk = [r for r in scanned if r.get("at_risk")]
    high = [
        r for r in scanned if any(f["severity"] == "high" for f in r.get("findings", []))
    ]
    finding_counts = Counter(
        f["code"] for r in scanned for f in r.get("findings", [])
    )

    lines = [
        f"# wheelproof scan summary — {path.name}",
        "",
        f"- packages scanned: {len(scanned)} ({len(errors)} errors/skips)",
        f"- **high severity: {len(high)}** ({len(high) / len(scanned):.0%}) — sdist build breaks under the 2026 removals" if scanned else "- nothing scanned",
        f"- at risk incl. medium: {len(at_risk)} ({len(at_risk) / len(scanned):.0%}) — medium = uses removed APIs (pkg_resources/distutils) or legacy build path" if scanned else "",
        "",
        "## findings by type",
        "",
        "| finding | count |",
        "|---|---|",
    ]
    for code, count in finding_counts.most_common():
        lines.append(f"| {code} | {count} |")

    if at_risk:
        lines += ["", "## at-risk packages", ""]
        for r in sorted(at_risk, key=lambda r: r["package"]):
            codes = ", ".join(sorted({f["code"] for f in r["findings"] if f["severity"] in ("high", "medium")}))
            lines.append(f"- **{r['package']}** {r['version']}: {codes}")

    if errors:
        lines += ["", "## errors / skips", ""]
        for r in sorted(errors, key=lambda r: r["package"]):
            lines.append(f"- {r['package']}: {r['error']}")

    return "\n".join(lines) + "\n"
