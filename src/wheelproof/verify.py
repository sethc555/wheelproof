"""Build two source trees and diff the resulting wheels.

Comparison rules:
- payload (everything outside *.dist-info/): content hashes must match exactly
- entry_points.txt: must match exactly (it changes runtime behavior)
- METADATA: compared field-wise, order-insensitive; differences are warnings
- WHEEL: compared after dropping the Generator line; differences are warnings
- RECORD: ignored (contains hashes of files we already compare directly)

Exit/return semantics: a verification passes iff payload and entry points are
identical. Metadata drift is reported but does not fail the check.
"""

from __future__ import annotations

import email.parser
import hashlib
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

IGNORED_DISTINFO = {"RECORD"}


class BuildError(RuntimeError):
    pass


@dataclass
class WheelContents:
    path: Path
    payload: dict[str, str]  # archive name -> sha256
    entry_points: str | None
    metadata_fields: list[tuple[str, str]]  # (lowercased field, value), sorted
    metadata_body: str
    distinfo_other: dict[str, str]  # name within dist-info -> sha256


@dataclass
class Report:
    payload_only_a: list[str] = field(default_factory=list)
    payload_only_b: list[str] = field(default_factory=list)
    payload_changed: list[str] = field(default_factory=list)
    entry_points_changed: bool = False
    metadata_only_a: list[tuple[str, str]] = field(default_factory=list)
    metadata_only_b: list[tuple[str, str]] = field(default_factory=list)
    metadata_body_changed: bool = False
    distinfo_changed: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not (
            self.payload_only_a
            or self.payload_only_b
            or self.payload_changed
            or self.entry_points_changed
        )

    @property
    def has_warnings(self) -> bool:
        return bool(
            self.metadata_only_a
            or self.metadata_only_b
            or self.metadata_body_changed
            or self.distinfo_changed
        )


def build_wheel(srcdir: Path, outdir: Path) -> Path:
    cmd = [sys.executable, "-m", "build", "--wheel", "--outdir", str(outdir), str(srcdir)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise BuildError(
            f"wheel build failed for {srcdir}\n--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
        )
    wheels = sorted(outdir.glob("*.whl"))
    if len(wheels) != 1:
        raise BuildError(f"expected exactly one wheel in {outdir}, found {len(wheels)}")
    return wheels[0]


def read_wheel(whl: Path) -> WheelContents:
    payload: dict[str, str] = {}
    entry_points: str | None = None
    metadata_fields: list[tuple[str, str]] = []
    metadata_body = ""
    distinfo_other: dict[str, str] = {}

    with zipfile.ZipFile(whl) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = info.filename
            data = zf.read(name)
            parts = name.split("/")
            if parts[0].endswith(".dist-info") and len(parts) > 1:
                # normalize away the dist-info dir name; version strings may
                # legitimately differ in normalization between the two builds
                inner = "/".join(parts[1:])
                if inner in IGNORED_DISTINFO:
                    continue
                if inner == "entry_points.txt":
                    entry_points = data.decode("utf-8", "replace")
                elif inner == "METADATA":
                    msg = email.parser.Parser().parsestr(data.decode("utf-8", "replace"))
                    metadata_fields = sorted((k.lower(), v) for k, v in msg.items())
                    metadata_body = msg.get_payload() or ""
                elif inner == "WHEEL":
                    lines = [
                        line
                        for line in data.decode("utf-8", "replace").splitlines()
                        if not line.startswith("Generator:")
                    ]
                    distinfo_other[inner] = hashlib.sha256(
                        "\n".join(sorted(lines)).encode()
                    ).hexdigest()
                else:
                    distinfo_other[inner] = hashlib.sha256(data).hexdigest()
            else:
                payload[name] = hashlib.sha256(data).hexdigest()

    return WheelContents(
        path=whl,
        payload=payload,
        entry_points=entry_points,
        metadata_fields=metadata_fields,
        metadata_body=metadata_body,
        distinfo_other=distinfo_other,
    )


def compare(a: WheelContents, b: WheelContents) -> Report:
    report = Report()

    names_a, names_b = set(a.payload), set(b.payload)
    report.payload_only_a = sorted(names_a - names_b)
    report.payload_only_b = sorted(names_b - names_a)
    report.payload_changed = sorted(
        n for n in names_a & names_b if a.payload[n] != b.payload[n]
    )

    report.entry_points_changed = a.entry_points != b.entry_points

    fields_a, fields_b = set(a.metadata_fields), set(b.metadata_fields)
    report.metadata_only_a = sorted(fields_a - fields_b)
    report.metadata_only_b = sorted(fields_b - fields_a)
    report.metadata_body_changed = a.metadata_body.strip() != b.metadata_body.strip()

    keys = set(a.distinfo_other) | set(b.distinfo_other)
    report.distinfo_changed = sorted(
        k for k in keys if a.distinfo_other.get(k) != b.distinfo_other.get(k)
    )

    return report


def print_report(report: Report, label_a: str, label_b: str) -> None:
    def section(title: str, items: list) -> None:
        print(f"  {title}:")
        for item in items:
            print(f"    {item}")

    if report.passed:
        print(f"PASS: payloads identical ({label_a} vs {label_b})")
    else:
        print(f"FAIL: payloads differ ({label_a} vs {label_b})")
        if report.payload_only_a:
            section(f"only in {label_a}", report.payload_only_a)
        if report.payload_only_b:
            section(f"only in {label_b}", report.payload_only_b)
        if report.payload_changed:
            section("content differs", report.payload_changed)
        if report.entry_points_changed:
            print("  entry_points.txt differs (runtime behavior change)")

    if report.has_warnings:
        print("warnings (metadata drift, does not fail verification):")
        if report.metadata_only_a:
            section(f"METADATA fields only in {label_a}", [f"{k}: {v}" for k, v in report.metadata_only_a])
        if report.metadata_only_b:
            section(f"METADATA fields only in {label_b}", [f"{k}: {v}" for k, v in report.metadata_only_b])
        if report.metadata_body_changed:
            print("  METADATA body (long description) differs")
        if report.distinfo_changed:
            section("dist-info files differ", report.distinfo_changed)


def verify(dir_a: Path, dir_b: Path) -> Report:
    with tempfile.TemporaryDirectory(prefix="wheelproof-") as tmp:
        out_a = Path(tmp) / "a"
        out_b = Path(tmp) / "b"
        out_a.mkdir()
        out_b.mkdir()
        wheel_a = build_wheel(dir_a, out_a)
        wheel_b = build_wheel(dir_b, out_b)
        return compare(read_wheel(wheel_a), read_wheel(wheel_b))
