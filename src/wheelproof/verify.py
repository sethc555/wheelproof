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
    """The *package* failed to build. Callers classify this as a package defect."""


class HarnessError(RuntimeError):
    """The build *harness* is unusable (e.g. `python -m build` itself won't run).

    Deliberately NOT a BuildError: a sick harness must never be reported as
    "package fails to build". Found the hard way — a stray top-level `build/`
    directory shipped by an unrelated wheel shadowed PyPA `build` in user
    site-packages, and every recheck reported "still broken" for six weeks.
    """


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


BUILD_TIMEOUT = 600  # seconds per wheel build; unsupervised runs must not hang

_harness_checked = False


def check_harness() -> None:
    """Preflight: `sys.executable -m build` must be the real PyPA build. Cached."""
    global _harness_checked
    if _harness_checked:
        return
    proc = subprocess.run(
        [sys.executable, "-m", "build", "--version"], capture_output=True, text=True, timeout=120
    )
    if proc.returncode != 0 or not proc.stdout.startswith("build "):
        raise HarnessError(
            f"`{sys.executable} -m build --version` failed — the harness cannot build anything "
            f"(is PyPA `build` installed for this interpreter, and not shadowed by a stray "
            f"top-level `build/` package?)\n{(proc.stdout + proc.stderr).strip()[-500:]}"
        )
    _harness_checked = True


def build_wheel(srcdir: Path, outdir: Path) -> Path:
    check_harness()
    cmd = [sys.executable, "-m", "build", "--wheel", "--outdir", str(outdir), str(srcdir)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=BUILD_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise BuildError(f"wheel build timed out after {BUILD_TIMEOUT}s for {srcdir}")
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


def _parse_entry_points(text: str | None) -> dict | None:
    """Parse entry_points.txt so whitespace/ordering can't cause a false fail."""
    if text is None:
        return None
    import configparser

    parser = configparser.ConfigParser()
    parser.optionxform = str
    try:
        parser.read_string(text)
    except configparser.Error:
        return {"unparseable": text}
    return {
        group: {k: parser.get(group, k, raw=True).replace(" ", "") for k in parser.options(group)}
        for group in parser.sections()
    }


def compare(a: WheelContents, b: WheelContents) -> Report:
    report = Report()

    names_a, names_b = set(a.payload), set(b.payload)
    report.payload_only_a = sorted(names_a - names_b)
    report.payload_only_b = sorted(names_b - names_a)
    report.payload_changed = sorted(
        n for n in names_a & names_b if a.payload[n] != b.payload[n]
    )

    report.entry_points_changed = _parse_entry_points(a.entry_points) != _parse_entry_points(b.entry_points)

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


def fetch_published_wheel(name: str, version: str, dest: Path) -> Path:
    """Download the maintainer's own published pure wheel for name==version."""
    import json
    import urllib.request

    req = urllib.request.Request(
        f"https://pypi.org/pypi/{name}/{version}/json",
        headers={"User-Agent": "wheelproof/0.1"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    for entry in data.get("urls", []):
        if entry["packagetype"] == "bdist_wheel" and entry["filename"].endswith(
            ("-py3-none-any.whl", "-py2.py3-none-any.whl")
        ):
            blob_req = urllib.request.Request(entry["url"], headers={"User-Agent": "wheelproof/0.1"})
            with urllib.request.urlopen(blob_req, timeout=120) as blob:
                out = dest / entry["filename"]
                out.write_bytes(blob.read())
                return out
    raise BuildError(
        f"no pure (none-any) wheel published for {name}=={version} — "
        f"platform wheels are out of scope for published-baseline comparison"
    )


def verify_against_published(srcdir: Path) -> tuple[Report, str]:
    """Build srcdir and compare against the published PyPI wheel of the same
    name+version (parsed from the built wheel's filename). Baseline = the
    artifact users already receive, so this works even when the original
    source tree no longer builds."""
    with tempfile.TemporaryDirectory(prefix="wheelproof-pub-") as tmp:
        out = Path(tmp) / "ours"
        out.mkdir()
        ours = build_wheel(srcdir, out)
        name, version = ours.name.split("-")[0:2]
        published = fetch_published_wheel(name, version, Path(tmp))
        report = compare(read_wheel(published), read_wheel(ours))
        return report, f"{name}=={version} (published: {published.name})"


def verify(dir_a: Path, dir_b: Path) -> Report:
    with tempfile.TemporaryDirectory(prefix="wheelproof-") as tmp:
        out_a = Path(tmp) / "a"
        out_b = Path(tmp) / "b"
        out_a.mkdir()
        out_b.mkdir()
        wheel_a = build_wheel(dir_a, out_a)
        wheel_b = build_wheel(dir_b, out_b)
        return compare(read_wheel(wheel_a), read_wheel(wheel_b))
