"""Scan a PyPI package's latest sdist for 2026 setuptools-removal risk.

Findings and severities:
- no-pyproject (high): no pyproject.toml at all — pure legacy build path
- no-build-system (medium): pyproject.toml exists but has no [build-system] table
- setup-cfg-deprecated-keys (high): dash-separated or uppercase option names in
  setup.cfg [metadata]/[options*] — the exact removal setuptools retries in 2026
- pkg-resources (medium): imports pkg_resources (removal slated since 2025-11-30)
- distutils (medium): imports distutils (gone from stdlib since Python 3.12)
- setup-requires (low), tests-require (low), test-command (low): long-deprecated
  setuptools features
"""

from __future__ import annotations

import configparser
import io
import json
import re
import tarfile
import tempfile
import tomllib
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

PYPI_JSON = "https://pypi.org/pypi/{name}/json"
USER_AGENT = "wheelproof/0.1 (+https://github.com/sethc555)"
MAX_PY_FILES = 500  # cap source-grep work on pathological sdists
MAX_SDIST_BYTES = 100 * 2**20

IMPORT_RE = {
    "pkg-resources": re.compile(r"^\s*(?:import|from)\s+pkg_resources\b", re.M),
    "distutils": re.compile(r"^\s*(?:import|from)\s+distutils\b", re.M),
}
SETUP_PY_FATAL_RE = {
    # ez_setup bootstraps pkg_resources internally; use_2to3 removed in setuptools 58
    "ez-setup": re.compile(r"^\s*(?:import|from)\s+ez_setup\b|\buse_setuptools\s*\(", re.M),
    "use-2to3": re.compile(r"\buse_2to3\s*[=:]"),
}
SETUP_FEATURE_RE = {
    "setup-requires": re.compile(r"\bsetup_requires\s*[=:]"),
    "tests-require": re.compile(r"\btests_require\s*[=:]"),
}
# imports under these paths are informational, not build/runtime risk
NOISE_PATH_RE = re.compile(
    r"(^|/)(tests?|testing|_vendor|vendored[^/]*|vendor|docs?|examples?|benchmarks?)(/|$)",
    re.I,
)


@dataclass
class Finding:
    code: str
    severity: str
    detail: str


@dataclass
class ScanResult:
    package: str
    version: str
    sdist_url: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def at_risk(self) -> bool:
        return any(f.severity in ("high", "medium") for f in self.findings)

    def to_json(self) -> str:
        return json.dumps(
            {
                "package": self.package,
                "version": self.version,
                "sdist_url": self.sdist_url,
                "at_risk": self.at_risk,
                "findings": [
                    {"code": f.code, "severity": f.severity, "detail": f.detail}
                    for f in self.findings
                ],
            },
            indent=2,
        )


class ScanError(RuntimeError):
    pass


def _fetch(url: str, max_bytes: int | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        if max_bytes is not None:
            declared = resp.headers.get("Content-Length")
            if declared and int(declared) > max_bytes:
                raise ScanError(f"sdist too large ({int(declared) // 2**20} MB > cap)")
            data = resp.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise ScanError("sdist too large (exceeded cap while reading)")
            return data
        return resp.read()


def _latest_sdist(name: str) -> tuple[str, str]:
    try:
        data = json.loads(_fetch(PYPI_JSON.format(name=name)))
    except Exception as exc:
        raise ScanError(f"could not fetch PyPI metadata for {name!r}: {exc}") from exc
    version = data["info"]["version"]
    for entry in data.get("urls", []):
        if entry.get("packagetype") == "sdist":
            return version, entry["url"]
    raise ScanError(f"{name} {version} publishes no sdist")


def _extract_sdist(blob: bytes, dest: Path) -> Path:
    bio = io.BytesIO(blob)
    if tarfile.is_tarfile(bio):
        bio.seek(0)
        with tarfile.open(fileobj=bio) as tf:
            tf.extractall(dest, filter="data")
    else:
        bio.seek(0)
        with zipfile.ZipFile(bio) as zf:
            zf.extractall(dest)
    roots = [p for p in dest.iterdir() if p.is_dir()]
    if len(roots) == 1:
        return roots[0]
    return dest


def _check_pyproject(root: Path, findings: list[Finding]) -> None:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        findings.append(
            Finding("no-pyproject", "high", "no pyproject.toml — pure legacy build path")
        )
        return
    try:
        doc = tomllib.loads(pyproject.read_text(encoding="utf-8", errors="replace"))
    except tomllib.TOMLDecodeError as exc:
        findings.append(Finding("pyproject-unparseable", "high", f"pyproject.toml does not parse: {exc}"))
        return
    if "build-system" not in doc:
        findings.append(
            Finding("no-build-system", "medium", "pyproject.toml has no [build-system] table")
        )


def _check_setup_cfg(root: Path, findings: list[Finding]) -> None:
    cfg_path = root / "setup.cfg"
    if not cfg_path.exists():
        return
    parser = configparser.ConfigParser()
    parser.optionxform = str  # preserve case so we can detect uppercase keys
    try:
        parser.read_string(cfg_path.read_text(encoding="utf-8", errors="replace"))
    except configparser.Error as exc:
        findings.append(Finding("setup-cfg-unparseable", "medium", f"setup.cfg does not parse: {exc}"))
        return
    bad: list[str] = []
    for section in parser.sections():
        if section != "metadata" and not section.startswith("options"):
            continue
        for option in parser.options(section):
            if "-" in option or any(c.isupper() for c in option):
                bad.append(f"[{section}] {option}")
    if bad:
        findings.append(
            Finding(
                "setup-cfg-deprecated-keys",
                "high",
                "dash-separated/uppercase keys slated for 2026 removal: " + ", ".join(bad),
            )
        )
    raw = cfg_path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"^\s*\[test\]|\btest_suite\s*=", raw, re.M):
        findings.append(Finding("test-command", "low", "uses deprecated test command/test_suite"))


def _check_sources(root: Path, findings: list[Finding]) -> None:
    seen: dict[str, tuple[str, str]] = {}  # code -> (severity, example path)
    feature_seen: dict[str, str] = {}
    count = 0
    for py in root.rglob("*.py"):
        if count >= MAX_PY_FILES:
            break
        count += 1
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(py.relative_to(root))
        severity = "low" if NOISE_PATH_RE.search(rel) else "medium"
        for code, pattern in IMPORT_RE.items():
            current = seen.get(code)
            if (current is None or (current[0] == "low" and severity == "medium")) and pattern.search(text):
                seen[code] = (severity, rel)
        if py.name == "setup.py":
            for code, pattern in SETUP_FEATURE_RE.items():
                if code not in feature_seen and pattern.search(text):
                    feature_seen[code] = rel
            if "/" not in rel:  # top-level setup.py only
                for code, pattern in SETUP_PY_FATAL_RE.items():
                    if pattern.search(text):
                        findings.append(Finding(code, "high", f"used in {rel}"))
    for code, (severity, rel) in seen.items():
        qualifier = "" if severity == "medium" else " (test/vendored path — informational)"
        findings.append(Finding(code, severity, f"imported in {rel}{qualifier}"))
    for code, rel in feature_seen.items():
        findings.append(Finding(code, "low", f"used in {rel}"))


def scan(name: str) -> ScanResult:
    version, url = _latest_sdist(name)
    result = ScanResult(package=name, version=version, sdist_url=url)
    blob = _fetch(url, max_bytes=MAX_SDIST_BYTES)
    with tempfile.TemporaryDirectory(prefix="wheelproof-scan-") as tmp:
        root = _extract_sdist(blob, Path(tmp))
        _check_pyproject(root, result.findings)
        _check_setup_cfg(root, result.findings)
        _check_sources(root, result.findings)
    return result
