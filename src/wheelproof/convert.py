"""setup.py/setup.cfg -> pyproject.toml, by wrapping existing tools, gated by verify.

Per PLAN.md phase 3 this module writes no novel translation logic:
- setuptools-py2cfg turns a static setup.py into setup.cfg
- ini2toml (setup.cfg profile) turns setup.cfg into PEP 621 pyproject.toml
- wheelproof.verify is the acceptance gate — a conversion that doesn't build a
  payload-identical wheel is a failure, not a deliverable

The original tree is never mutated; conversion happens in a copy.

Caveat: py2cfg *executes* setup.py and verify executes builds. Only run on
source you'd pip-install anyway.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from . import verify as verify_mod

BUILD_SYSTEM_SNIPPET = """\
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

"""


class ConvertError(RuntimeError):
    pass


def _py2cfg(setup_py: Path) -> str:
    exe = Path(sys.executable).parent / "setuptools-py2cfg"
    cmd = [str(exe)] if exe.exists() else ["setuptools-py2cfg"]
    env = dict(os.environ)
    # setup.py often imports its own package for __version__
    env["PYTHONPATH"] = str(setup_py.parent.resolve()) + os.pathsep + env.get("PYTHONPATH", "")
    try:
        proc = subprocess.run(
            cmd + [setup_py.name],
            capture_output=True, text=True, cwd=setup_py.parent, env=env, timeout=120,
        )
    except subprocess.TimeoutExpired:
        raise ConvertError(f"setuptools-py2cfg timed out on {setup_py}")
    if proc.returncode != 0 or not proc.stdout.strip():
        raise ConvertError(
            f"setuptools-py2cfg failed on {setup_py} (dynamic setup.py? flag as manual)\n{proc.stderr}"
        )
    return proc.stdout


def _merge_cfg(base: str, overlay: str) -> str:
    """Overlay sections/options from `overlay` onto `base`, returning ini text."""
    import configparser
    import io

    merged = configparser.ConfigParser()
    merged.optionxform = str
    merged.read_string(base)
    over = configparser.ConfigParser()
    over.optionxform = str
    over.read_string(overlay)
    for section in over.sections():
        if not merged.has_section(section):
            merged.add_section(section)
        for option in over.options(section):
            merged.set(section, option, over.get(section, option, raw=True))
    buf = io.StringIO()
    merged.write(buf)
    return buf.getvalue()


def _filter_cfg(cfg_text: str) -> tuple[str, list[str]]:
    """Keep only setuptools packaging sections; return (text, dropped sections)."""
    import configparser
    import io

    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read_string(cfg_text)
    dropped = []
    for section in parser.sections():
        if section == "metadata" or section.startswith("options"):
            continue
        parser.remove_section(section)
        dropped.append(section)
    buf = io.StringIO()
    parser.write(buf)
    return buf.getvalue(), dropped


def _postfix_cfg(cfg_text: str, setup_py: Path | None) -> str:
    """Repair known setuptools-py2cfg output defects (wrapper glue, not translation).

    - [options.package_data]-style values are emitted '; '-joined on one line,
      which setuptools reads as a single bogus glob -> data files vanish
    - find_packages(exclude=[...]) loses its exclude list -> tests leak into wheels
    - string-form entry_points= are dropped entirely (only dict form is handled)
    """
    import ast
    import configparser
    import io
    import textwrap

    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read_string(cfg_text)

    # NOT install_requires/extras_require: there ';' is an environment marker
    for section in ("options.package_data", "options.exclude_package_data", "options.packages.find"):
        if parser.has_section(section):
            for option in parser.options(section):
                value = parser.get(section, option, raw=True)
                if ";" in value:
                    items = [v.strip() for v in value.split(";") if v.strip()]
                    parser.set(section, option, "\n".join(items))

    if setup_py is not None and setup_py.exists():
        tree = ast.parse(setup_py.read_text(errors="replace"))

        find_call_kwargs: dict[str, list[str]] = {}
        entry_points_node = None
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            if name in ("find_packages", "find_namespace_packages"):
                for kw in node.keywords:
                    if kw.arg in ("exclude", "include"):
                        try:
                            values = list(ast.literal_eval(kw.value))
                        except (ValueError, SyntaxError):
                            continue
                        find_call_kwargs[kw.arg] = [str(v) for v in values]
            if name == "setup":
                for kw in node.keywords:
                    if kw.arg == "entry_points":
                        entry_points_node = kw.value

        if find_call_kwargs and parser.get("options", "packages", fallback="").strip() in ("find:", "find_namespace:"):
            section = "options.packages.find"
            if not parser.has_section(section):
                parser.add_section(section)
            for key, values in find_call_kwargs.items():
                if not parser.has_option(section, key):
                    parser.set(section, key, "\n".join(values))

        if entry_points_node is not None and not parser.has_section("options.entry_points"):
            if isinstance(entry_points_node, ast.Constant) and isinstance(entry_points_node.value, str):
                ep = configparser.ConfigParser()
                ep.optionxform = str
                ep.read_string(textwrap.dedent(entry_points_node.value))
                parser.add_section("options.entry_points")
                for group in ep.sections():
                    lines = [f"{k} = {ep.get(group, k, raw=True)}" for k in ep.options(group)]
                    parser.set("options.entry_points", group, "\n".join(lines))
            elif not isinstance(entry_points_node, ast.Dict):
                raise ConvertError(
                    "entry_points present in setup.py but lost by py2cfg and not "
                    "statically recoverable — flag as manual"
                )

    buf = io.StringIO()
    parser.write(buf)
    return buf.getvalue()


def _cfg_to_toml(cfg_text: str) -> str:
    try:
        # full (tomlkit) driver crashes on bare `license = MIT` in ini2toml 0.15
        from ini2toml.api import LiteTranslator
    except ImportError as exc:
        raise ConvertError("ini2toml not installed — pip install 'ini2toml[full]' toml") from exc
    return LiteTranslator().translate(cfg_text, profile_name="setup.cfg")


def convert(srcdir: Path, outdir: Path) -> Path:
    """Convert a copy of srcdir at outdir. Returns outdir. Does not verify."""
    if outdir.exists():
        raise ConvertError(f"{outdir} already exists, refusing to overwrite")
    if (srcdir / "pyproject.toml").exists():
        doc = tomllib.loads((srcdir / "pyproject.toml").read_text(errors="replace"))
        if "project" in doc:
            raise ConvertError(
                f"{srcdir} already has a [project] table — nothing to convert"
            )

    shutil.copytree(srcdir, outdir, symlinks=True)

    setup_cfg = outdir / "setup.cfg"
    setup_py = outdir / "setup.py"
    if setup_py.exists():
        # metadata may live in setup.py even when a setup.cfg stub exists
        # (six: setup.cfg holds only flake8/bdist_wheel) — py2cfg wins per section
        cfg_text = _py2cfg(setup_py)
        if setup_cfg.exists():
            cfg_text = _merge_cfg(setup_cfg.read_text(errors="replace"), cfg_text)
    elif setup_cfg.exists():
        cfg_text = setup_cfg.read_text(errors="replace")
    else:
        raise ConvertError(f"{srcdir} has neither setup.cfg nor setup.py")

    cfg_text = _postfix_cfg(cfg_text, setup_py if setup_py.exists() else None)
    cfg_text, dropped = _filter_cfg(cfg_text)
    if dropped:
        # lint/tool config doesn't affect the wheel; the verify gate proves it
        print(f"note: dropped non-packaging setup.cfg sections: {', '.join(dropped)}", file=sys.stderr)
    toml_text = _cfg_to_toml(cfg_text)
    if "[build-system]" not in toml_text:
        toml_text = BUILD_SYSTEM_SNIPPET + toml_text

    existing = outdir / "pyproject.toml"
    if existing.exists():
        # keep tool config (black/mypy/etc.) below the generated tables
        toml_text = toml_text.rstrip() + "\n\n" + existing.read_text(errors="replace")
    existing.write_text(toml_text)

    # the converted tree must not fall back to the legacy files
    if setup_cfg.exists():
        setup_cfg.unlink()
    if setup_py.exists():
        setup_py.unlink()
    return outdir


def convert_and_verify(srcdir: Path, outdir: Path) -> tuple[Path, verify_mod.Report]:
    convert(srcdir, outdir)
    report = verify_mod.verify(srcdir, outdir)
    return outdir, report
