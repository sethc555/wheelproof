"""wheelproof command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="wheelproof",
        description="Prove Python packaging migrations by building both trees and diffing the wheels.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="scan a PyPI package's sdist for 2026 setuptools-removal risk")
    p_scan.add_argument("package", help="package name on PyPI")

    p_verify = sub.add_parser("verify", help="build two source trees and diff the wheels")
    p_verify.add_argument("dir_a", type=Path, help="original source tree")
    p_verify.add_argument("dir_b", type=Path, help="converted source tree")

    p_convert = sub.add_parser("convert", help="convert setup.py/setup.cfg to pyproject.toml [planned]")
    p_convert.add_argument("srcdir", type=Path)

    p_batch = sub.add_parser("batch", help="scan many packages, resumable JSONL output")
    p_batch.add_argument("--top", type=int, help="scan the top N packages by downloads")
    p_batch.add_argument("--file", type=Path, help="newline-separated package names")
    p_batch.add_argument("--output", type=Path, default=Path("scan-results.jsonl"))
    p_batch.add_argument("--workers", type=int, default=8)

    p_summary = sub.add_parser("summary", help="markdown summary of a batch JSONL file")
    p_summary.add_argument("results", type=Path)

    args = parser.parse_args(argv)

    if args.command == "scan":
        from . import scan

        try:
            result = scan.scan(args.package)
        except scan.ScanError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(result.to_json())
        return 0

    if args.command == "verify":
        from . import verify

        for d in (args.dir_a, args.dir_b):
            if not d.is_dir():
                print(f"error: {d} is not a directory", file=sys.stderr)
                return 1
        try:
            report = verify.verify(args.dir_a, args.dir_b)
        except verify.BuildError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        verify.print_report(report, str(args.dir_a), str(args.dir_b))
        return 0 if report.passed else 1

    if args.command == "convert":
        print("convert is not implemented yet — see PLAN.md phase 3", file=sys.stderr)
        return 2

    if args.command == "batch":
        from . import batch, scan as scan_mod

        if args.top:
            try:
                names = batch.top_packages(args.top)
            except Exception as exc:
                print(f"error fetching top-packages list: {exc}", file=sys.stderr)
                return 1
        elif args.file:
            names = [n.strip() for n in args.file.read_text().splitlines() if n.strip()]
        else:
            print("error: need --top N or --file", file=sys.stderr)
            return 1
        batch.batch_scan(names, args.output, workers=args.workers)
        return 0

    if args.command == "summary":
        from . import batch

        if not args.results.exists():
            print(f"error: {args.results} not found", file=sys.stderr)
            return 1
        print(batch.summarize(args.results))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
