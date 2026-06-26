# wheelproof

**Migration you can check, not trust.**

setuptools is removing its deprecated surface: `pkg_resources` is gone as of
v82.0.0 (2026-02-08), and the dash-separated `setup.cfg` keys that broke 12,000+
packages in the reverted March 2025 attempt are past their announced 2026-03-03
cutoff and can be removed in any release. The packages that will burn worst are
the dead tail — maintainers gone, `setup.py` frozen years ago.

wheelproof is a scanner, a verify-gated converter, and a corpus of proven
fixes, built around one idea: **a packaging migration is trustworthy only if the
artifact proves itself.** You don't review the conversion — you build both
versions and diff the wheels.

**[Read the writeup](WRITEUP.md)** — the census, the method, and what actually
moves maintainers (spoiler: release requests beat PRs, 4-to-0).

## Findings (top 5,000 PyPI packages by downloads, scanned 2026-06)

- **1,153 (24%)** fail to build from sdist under the announced removals
  ([results/top-summary.md](results/top-summary.md), raw data
  [results/top.jsonl](results/top.jsonl))
- **100 are verified broken today** — every at-risk package's sdist was
  actually built; only a quarter of the failures are the setuptools story, the
  rest is older quiet rot (incomplete sdists, Python 3.12 removals, undeclared
  build deps) ([results/broken-now-v2.md](results/broken-now-v2.md)); verified
  fixes in [outreach/sdist-patches/](outreach/sdist-patches/), upstream
  PRs/issues tracked in [outreach/](outreach/) — five fixes already released
  (omegaconf, hydra, token-bucket, impyla, click-spinner) and one PR merged
  (resend); a valkey-py release is committed for the py.typed sdist gap
- **959 (83%) of the doomed packages have execution-proven conversions** in
  [corpus/](corpus/) — a `pyproject.toml` per package whose wheel is
  byte-identical in payload to the original `setup.py` build

## Commands

```
wheelproof scan <package>        # is this PyPI package at risk? (JSON out)
wheelproof batch --top N         # scan the top-N packages, resumable JSONL
wheelproof summary <jsonl>       # markdown report of a batch scan
wheelproof convert <srcdir>      # setup.py/setup.cfg -> pyproject.toml, verify-gated
wheelproof batch-convert <jsonl> # convert+verify every high-severity package
wheelproof verify <a> <b>        # build both source trees, diff the wheels
wheelproof verify-published <d>  # diff a build against the maintainer's published wheel
wheelproof adopt <pkg> <srcdir>  # install a corpus conversion, gated by wheel-diff
wheelproof buildcheck <jsonl>    # build every at-risk sdist — the broken-now gate
wheelproof divcheck --package X  # does X's published wheel match its sdist?
wheelproof corpus-summary <dir>  # pass/fail report of a corpus
```

## Why wheel-diff is the whole trick

Generation is cheap — by hand, by tools, by LLMs — and maintainers are drowning
in unverified machine output. The scarce good is *proof*. `verify` builds each
tree in isolation (`python -m build --wheel`), unpacks both wheels, and
compares:

- **payload** (everything outside `*.dist-info/`): must match by content hash, exactly
- **entry points**: compared parsed, must match (runtime behavior)
- **metadata** (`METADATA`): diffed field-wise, reported as warnings
- **noise** (`RECORD`, `WHEEL: Generator`): ignored

Exit 0 = payloads identical. A conversion that fails the gate is a labeled work
item, never a deliverable. The gate has caught real defects at every stage of
this project: conversions that silently dropped data files, leaked test suites
into wheels, lost console scripts, or shipped pure-Python wheels missing their
C extensions.

## How conversions are produced

`convert` deliberately writes no novel translation logic. It chains existing
tools — [setuptools-py2cfg](https://github.com/gvalkov/setuptools-py2cfg) for
static `setup.py`, [ini2toml](https://ini2toml.readthedocs.io/) for
`setup.cfg` — then repairs their known output defects (semicolon-joined list
values, dropped `find_packages` excludes, dropped string-form entry points,
deprecated dash keys passed into `[project]`, missing readme content-types,
dead test keys in `[tool.setuptools]`) and gates the result through `verify`.

Packages the chain can't handle (dynamic `setup.py`) were converted by LLM
agents whose proposals were **independently verified by the same wheel-diff
gate** — self-reports counted for nothing; 282 of 327 proposals survived.
Every corpus entry records its provenance in `result.json`. Packages that
can't be converted faithfully (C extensions, versioneer build-time rewrites,
build-time code generation) are refused loudly, not half-converted.

## Using the corpus

`corpus/<package>/pyproject.toml` is a drop-in replacement for that package's
`setup.py`/`setup.cfg` **at the version named in `result.json`** (delete the
legacy files when adopting it). Each was verified against that version's sdist.
The corpus is pull, not push: maintainers, distros, and forks take what's
useful — `wheelproof adopt <package> <srcdir>` does the pull for you, gated by
the same wheel-diff (it reverts itself if the proof fails). The conversion files and patches are trivial configuration; treat them
as available under the upstream project's own license to remove any friction.

## Caveats, honestly

- Verification compares against a freshly built baseline. Packages whose
  *original* build is already broken have no baseline; their patches in
  `outreach/sdist-patches/` were instead verified as "unpatched fails, patched
  builds." Diffing against the last *published* wheel is future work.
- `scan`'s static findings are candidates, not verdicts — build verification
  found 14 false positives among 26 static pkg_resources flags. Anything this
  repo states as "verified" was executed, not inferred.
- `convert`, `verify`, and `batch-convert` execute `setup.py` code from PyPI.
  Run them in a container.

## Requirements

Python ≥ 3.11. `verify` needs [`build`](https://pypi.org/project/build/);
`convert` needs `ini2toml[full]`, `setuptools-py2cfg`, and `toml`.

## License

MIT. Commits in this repo were authored with LLM assistance (disclosed via
Co-Authored-By trailers); every artifact that matters is machine-verified
rather than trusted.
