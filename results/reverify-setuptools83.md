# Corpus re-verification against setuptools 83.0.0

**Date:** 2026-07-10 · **Raw data:** [reverify-setuptools83.jsonl](reverify-setuptools83.jsonl)

A proof is a claim about a *build*, and the build environment drifts. Every
corpus conversion was originally proven under setuptools 82.x. setuptools has
since released **83.0.0**, so the corpus's central claim — *"this
`pyproject.toml` produces a wheel whose payload is byte-identical to the
`setup.py` build"* — was, until this run, unverified under the toolchain users
actually get today. Build isolation installs the latest setuptools by default,
so re-running the gate exercises 83.0.0.

**Method.** For each of the 959 `pass` entries: download the pinned sdist,
snapshot it pristine, install the corpus `pyproject.toml` in place of
`setup.py`/`setup.cfg`, build both trees, diff the wheels (`wheelproof adopt`,
i.e. the same gate that produced the corpus). Executed in a clean
`python:3.12` container, six shards in parallel.

## Result

| outcome | count | meaning |
|---|---:|---|
| **pass** | **948** | payload byte-identical under setuptools 83.0.0 |
| inconclusive | 10 | sdist already ships a `pyproject.toml`; `adopt` refuses to overwrite |
| **verify-fail** | **1** | `pywin32-ctypes` — a genuine defect (below) |

**The corpus holds under setuptools 83.0.0.** No conversion regressed because
of the setuptools bump. 948 of the 949 entries that could be evaluated still
produce byte-identical payloads.

## The 10 inconclusive entries

`folium`, `lkml`, `office365-rest-python-client`, `pycarlo`, `pyhumps`,
`python-utils`, `pyxtal`, `sagemaker-mlflow`, `selenium-wire`, `sparqlwrapper`.

These sdists ship a `pyproject.toml` *alongside* `setup.py`/`setup.cfg`, and
`adopt` refuses to overwrite an existing `pyproject.toml` by design. They were
not evaluated — this is a gap in the re-verification harness, not a failure.
It also means the corpus currently holds conversions for packages `adopt` can
never install into; worth deciding whether such entries belong.

## The one real failure: `pywin32-ctypes` 0.2.3

This entry was recorded as `pass`. It is not one, and it never was. **The
original proof was contaminated.**

`setup.py` rewrites the version file at *module top level*:

```python
version = (HERE / 'VERSION').read_text().strip()
filename = (HERE / 'win32ctypes' / 'version.py').write_text(f'__version__ = "{version}"\n')
```

So merely **executing** `setup.py` mutates the source tree — and
`setuptools-py2cfg` executes `setup.py` during conversion. By the time the
pristine baseline was snapshotted, `version.py` had already been rewritten, so
both sides matched and the gate passed.

Re-verified from an untouched sdist, they do not match. The sdist ships
`win32ctypes/version.py` with **CRLF** endings; the pristine build regenerates
it with **LF**; the `pyproject.toml`-only build has no `setup.py` to run and
packages the CRLF copy verbatim. Payloads differ on `win32ctypes/version.py`.

It **fails identically under setuptools 82.0.1 and 83.0.0**, which is what
proves it is a latent gate defect rather than a setuptools regression.

`pywin32-ctypes` performs build-time code generation and therefore belongs in
the *refuse loudly* bucket, not the corpus. Its entry is reclassified
`verify-fail` and its unproven `pyproject.toml` has been withdrawn.

## What this run teaches

The gate is only as clean as its baseline. A converter that **executes**
`setup.py` can mutate the tree it is about to be compared against, and a
top-level side effect in `setup.py` turns the wheel-diff into a comparison of
a tree with itself. The defensible fix is to snapshot the pristine tree
*before* any conversion tool touches it, and to re-verify from that snapshot —
which is exactly what re-verifying from a fresh sdist does.

One false `pass` in 959 (0.1%) survived the original gate. It was found by
re-running the gate, not by reading the conversion. That is the method working.
