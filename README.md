# wheelproof

**Migration you can check, not trust.**

Setuptools is retrying its deprecated-config removal in 2026. Last time (2025) it broke
12,000+ packages, pins didn't hold because build isolation re-resolves setuptools, and
the whole thing got reverted. The packages that will burn worst are the dead tail —
maintainers gone, `setup.py`/`setup.cfg` frozen in 2017.

wheelproof is three tools around one idea: a packaging migration is trustworthy only if
the artifact proves itself. You don't review the conversion — you **build both versions
and diff the wheels**.

```
wheelproof scan <package>      # is this PyPI package at risk from the 2026 removals?
wheelproof convert <srcdir>    # setup.py/setup.cfg -> pyproject.toml   [planned]
wheelproof verify <a> <b>      # build both source trees, diff the wheels
```

## Why wheel-diff is the whole trick

LLMs make conversions cheap to generate and the ecosystem is drowning in unverified
machine output. The scarce good is *proof*. A wheel built from the original tree and a
wheel built from the converted tree should contain byte-identical payloads and
equivalent metadata. When they do, the conversion carries its own evidence — a hash
comparison, not a code review. No burned-out maintainer has to vouch for it.

`verify` builds each tree in isolation (`python -m build --wheel`), unpacks both wheels,
and compares:

- **payload** (everything outside `*.dist-info/`): must match by content hash, exactly
- **metadata** (`METADATA`): diffed field-wise, order-insensitive, reported as warnings
- **noise** (`RECORD`, `WHEEL: Generator`): ignored — these legitimately differ

Exit code 0 = payloads identical.

## What `scan` flags

Against a package's latest sdist from PyPI:

- no `pyproject.toml`, or one without `[build-system]` (legacy build path)
- dash-separated or uppercase keys in `setup.cfg` `[metadata]`/`[options]`
  (the exact thing the 2026 retry removes)
- `pkg_resources` imports (removal slated since 2025-11-30)
- `distutils` imports (gone from stdlib since 3.12)
- `setup_requires` / `tests_require` / `test` command usage

Output is JSON — pipe it, aggregate it, publish the at-risk list.

## Status

v0. `scan` and `verify` work; `convert` is the next milestone — see [PLAN.md](PLAN.md).
Stdlib-only at runtime; `verify` shells out to `python -m build` (pip install build).

## Requirements

Python ≥ 3.10. For `verify`: the [`build`](https://pypi.org/project/build/) package.

## License

MIT
