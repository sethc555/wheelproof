"""Adopt a proven conversion from the corpus into a source tree — with the gate.

The corpus is pull, not push; this is the puller. For a package's source tree
(an extracted sdist or a repo checkout at the corpus-verified version):

1. fetch corpus/<package>/pyproject.toml + result.json (local corpus dir, or
   the public repo over HTTPS),
2. snapshot the pristine tree,
3. back up setup.py/setup.cfg (.adopted-bak) and install the pyproject.toml,
4. run the wheel-diff gate: pristine build vs adopted build,
5. on PASS keep the change; on FAIL revert everything (unless --force).

Adoption without the gate is just trust; the gate is the point.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

from . import verify as verify_mod

RAW_BASE = "https://raw.githubusercontent.com/sethc555/wheelproof/main/corpus"


class AdoptError(RuntimeError):
    pass


def _fetch_entry(package: str, corpus: Path | None) -> tuple[str, dict]:
    if corpus is not None and (corpus / package / "pyproject.toml").exists():
        toml_text = (corpus / package / "pyproject.toml").read_text()
        meta = json.loads((corpus / package / "result.json").read_text())
        return toml_text, meta
    try:
        def get(name: str) -> str:
            req = urllib.request.Request(
                f"{RAW_BASE}/{package}/{name}", headers={"User-Agent": "wheelproof-adopt"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode()

        return get("pyproject.toml"), json.loads(get("result.json"))
    except Exception as exc:
        raise AdoptError(
            f"no corpus entry for {package!r} (local corpus missing it and {RAW_BASE} fetch failed: {exc})"
        ) from exc


def adopt(srcdir: Path, package: str, corpus: Path | None = None, force: bool = False) -> bool:
    toml_text, meta = _fetch_entry(package, corpus)
    print(f"corpus entry: {meta['package']} {meta.get('version', '?')} "
          f"({meta.get('provenance', 'mechanical conversion')})")

    if (srcdir / "pyproject.toml").exists():
        raise AdoptError(f"{srcdir} already has a pyproject.toml — adopt refuses to overwrite")
    if not (srcdir / "setup.py").exists() and not (srcdir / "setup.cfg").exists():
        raise AdoptError(f"{srcdir} has no setup.py/setup.cfg — nothing to migrate")

    with tempfile.TemporaryDirectory(prefix="wp-adopt-") as tmp:
        pristine = Path(tmp) / "pristine"
        shutil.copytree(srcdir, pristine, symlinks=True)

        moved = []
        for legacy in ("setup.py", "setup.cfg"):
            f = srcdir / legacy
            if f.exists():
                f.rename(srcdir / f"{legacy}.adopted-bak")
                moved.append(legacy)
        (srcdir / "pyproject.toml").write_text(toml_text)

        def revert() -> None:
            (srcdir / "pyproject.toml").unlink()
            for legacy in moved:
                (srcdir / f"{legacy}.adopted-bak").rename(srcdir / legacy)

        try:
            report = verify_mod.verify(pristine, srcdir)
        except verify_mod.BuildError as exc:
            if not force:
                revert()
                raise AdoptError(f"verification could not run, reverted: {exc}") from exc
            print(f"warning: gate could not run ({exc}); kept due to --force", file=sys.stderr)
            return False

        verify_mod.print_report(report, "pristine", "adopted")
        if report.passed:
            print(f"adopted: pyproject.toml installed, {', '.join(moved)} -> *.adopted-bak")
            return True
        if force:
            print("gate FAILED but kept due to --force — this tree carries no proof", file=sys.stderr)
            return False
        revert()
        raise AdoptError(
            "wheel-diff gate FAILED (tree probably differs from the corpus-verified "
            f"version {meta.get('version', '?')}); everything reverted"
        )
