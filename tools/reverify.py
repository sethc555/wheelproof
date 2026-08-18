"""Re-verify every corpus `pass` entry against whatever setuptools build
isolation installs today.

A proof is a claim about a *build*, and the build environment drifts. This
re-runs the same gate that produced the corpus (`wheelproof adopt`: pristine
sdist vs. sdist-with-corpus-pyproject, wheels diffed) from an untouched sdist.

Run inside a clean container via tools/reverify.sh; this file is the per-shard
worker. Output is resumable JSONL, one record per package:

  {"package", "version", "status": pass|verify-fail|build-error|inconclusive|
   fetch-error, "detail": <first line of error, if any>}

"inconclusive" = the sdist already ships a pyproject.toml, which `adopt`
refuses to overwrite (a known harness gap, see PLAN.md).
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from wheelproof import adopt as adopt_mod
from wheelproof import scan as scan_mod
from wheelproof import verify as verify_mod

PYPI_JSON = "https://pypi.org/pypi/{name}/{version}/json"


def sdist_url(meta: dict) -> str:
    if meta.get("sdist_url"):
        return meta["sdist_url"]
    data = json.loads(scan_mod._fetch(PYPI_JSON.format(name=meta["package"], version=meta["version"])))
    for u in data.get("urls", []):
        if u.get("packagetype") == "sdist":
            return u["url"]
    raise scan_mod.ScanError(f"{meta['package']} {meta['version']} publishes no sdist")


def classify(exc: Exception) -> tuple[str, str]:
    msg = str(exc)
    first = msg.strip().splitlines()[0] if msg.strip() else type(exc).__name__
    if "already has a pyproject.toml" in msg:
        return "inconclusive", first
    if "gate FAILED" in msg:
        return "verify-fail", first
    if "could not run" in msg or isinstance(exc, verify_mod.BuildError):
        return "build-error", first
    return "error", first


def run_one(package: str, corpus: Path, keep_output: bool) -> dict:
    meta = json.loads((corpus / package / "result.json").read_text())
    rec = {"package": package, "version": meta.get("version")}
    t0 = time.monotonic()
    try:
        url = sdist_url(meta)
        blob = scan_mod._fetch(url, max_bytes=200 * 2**20)
    except Exception as exc:
        rec.update(status="fetch-error", detail=str(exc).splitlines()[0][:300])
        return rec
    with tempfile.TemporaryDirectory(prefix="wp-rv-") as tmp:
        try:
            root = scan_mod._extract_sdist(blob, Path(tmp) / "src")
        except Exception as exc:
            rec.update(status="fetch-error", detail=f"extract: {exc}"[:300])
            return rec
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                ok = adopt_mod.adopt(root, package, corpus=corpus, force=False)
            rec["status"] = "pass" if ok else "verify-fail"
        except Exception as exc:  # AdoptError, BuildError, anything else
            status, detail = classify(exc)
            rec.update(status=status, detail=detail[:300])
            if keep_output:
                rec["output"] = buf.getvalue()[-4000:]
    rec["seconds"] = round(time.monotonic() - t0, 1)
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True, help="JSONL, appended; already-done packages are skipped")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--only", nargs="*", help="restrict to these packages (smoke test)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--keep-output", action="store_true", help="store build/gate output for non-pass records")
    args = ap.parse_args(argv)

    entries = sorted(
        p.name for p in args.corpus.iterdir()
        if (p / "result.json").exists()
        and json.loads((p / "result.json").read_text()).get("status") == "pass"
    )
    if args.only:
        entries = [e for e in entries if e in set(args.only)]
    entries = entries[args.shard::args.shards]
    if args.limit:
        entries = entries[: args.limit]

    done: set[str] = set()
    if args.output.exists():
        for line in args.output.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["package"])
    todo = [e for e in entries if e not in done]
    print(f"shard {args.shard}/{args.shards}: {len(entries)} entries, {len(done)} done, {len(todo)} to run", flush=True)

    with args.output.open("a") as out:
        for i, pkg in enumerate(todo, 1):
            rec = run_one(pkg, args.corpus, args.keep_output)
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"[{args.shard}] {i}/{len(todo)} {pkg} {rec.get('version')} -> {rec['status']} ({rec.get('seconds', '?')}s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
