# Corpus re-verification against setuptools 84.0.0

**Date:** 2026-08-17 · **Raw data:** [reverify-setuptools84.jsonl](reverify-setuptools84.jsonl) · **Toolchain:** [reverify-setuptools84.env](reverify-setuptools84.env)

Second re-verification, same reason as the [first](reverify-setuptools83.md):
a proof is a claim about a build, and the build environment drifted again.
setuptools **84.0.0** shipped 2026-08-08 (compiler/distutils decoupling;
newline-separated `keywords`/`platforms` now split with a deprecation warning;
`Extension` became a dataclass). Build isolation pulls it by default, so every
corpus conversion was, until this run, unverified under the toolchain users
actually get.

**Method.** Identical to the 83 run, now scripted and committed as
[`tools/reverify.py`](../tools/reverify.py) + [`tools/reverify.sh`](../tools/reverify.sh)
(the 83 runner was ad hoc and lost). For each of the 958 `pass` entries:
download the pinned sdist from PyPI, extract untouched, run `wheelproof adopt`
(snapshot pristine → swap in the corpus `pyproject.toml` → build both →
diff wheels). Clean `python:3.12` containers, 8 shards, ~15 minutes wall.
The isolated build environment resolved to `setuptools-84.0.0`,
`wheel-0.48.0`, `build-1.5.0` on Python 3.12.14.

## Result

| outcome | count | meaning |
|---|---:|---|
| **pass** | **948** | payload byte-identical under setuptools 84.0.0 |
| inconclusive | 10 | sdist already ships a `pyproject.toml`; `adopt` refuses to overwrite |
| verify-fail | 0 | |
| build-error | 0 | |

**The corpus holds under setuptools 84.0.0.** Every one of the 948 evaluable
entries still produces a byte-identical payload; the result is entry-for-entry
identical to the 83.0.0 run (the only delta is `pywin32-ctypes`, reclassified
`verify-fail` after that run and therefore no longer in the input set).

The 10 inconclusive entries are the same 10 as before (`folium`, `lkml`,
`office365-rest-python-client`, `pycarlo`, `pyhumps`, `python-utils`,
`pyxtal`, `sagemaker-mlflow`, `selenium-wire`, `sparqlwrapper`). Note the
83 raw data recorded them as `verify-fail` while its writeup called them
inconclusive; this run's data uses `inconclusive` explicitly. The `adopt`
guard gap (PLAN.md) is still open.

## What 84.0.0 could have broken, and didn't

The corpus is pure-Python conversions, so the compiler refactor is out of
scope by construction. The one change with metadata reach — newline-separated
`keywords`/`platforms` are now split into items — would surface in the gate
as `metadata_body_changed`, but only if pristine and converted trees fed
setuptools different keyword strings; both sides build under the same
setuptools, so a converter that copied the field verbatim cancels out. Zero
metadata warnings were promoted to failures. If a future release rejects
those fields outright, the corpus entries that carry them fail on *both*
sides — that shows up as `build-error`, not silent drift.

Canary as of the same day: dash/uppercase `setup.cfg` keys **still build**
under 84.0.0. The second removal has not landed.
