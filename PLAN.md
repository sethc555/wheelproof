# wheelproof roadmap

> **PAUSED 2026-06-09 — resume here:** Phase 3 batch mode. Run convert across the
> 1,153 high-severity packages from results/top.jsonl (filter `at_risk` + any
> high finding), count the verify pass rate. That number — "N of 1,153 doomed
> packages convert mechanically with proof" — is the headline for any writeup
> and the seed of the Phase 4 corpus. Everything below Phase 3's first checkbox
> is built and tested; .venv has build/ini2toml/setuptools-py2cfg/toml.

Context: setuptools retries its deprecated-config removal in 2026
(https://www.clientserver.dev/p/setuptools-follows-through-on-a-deprecation,
https://setuptools.pypa.io/en/latest/history.html). pkg_resources removal slated from
2025-11-30. The dead tail of PyPI — packages with gone maintainers — is exactly the
set that can't fix itself.

## Phase 1 — verify core (DONE, v0)

The moat. Build two source trees, diff the wheels, classify differences
(payload / metadata / noise). Everything else depends on this being airtight.

Hardening still owed:
- [ ] sdist-vs-sdist verify mode (some packages publish no wheels)
- [ ] multi-wheel matrix (platform/abi tags) — compare like-to-like
- [ ] normalize known-benign METADATA churn (Metadata-Version bumps, license-file
      field renames) with an explicit allowlist, never a fuzzy match
- [ ] machine-readable verify report (JSON) alongside human output

## Phase 2 — scan at scale

Single-package scan works. Scale it:
- [ ] walk the top-N PyPI packages by downloads (use the BigQuery-derived
      top-pypi-packages dataset, refreshed monthly)
- [ ] dependency-aware ranking: at-risk packages weighted by reverse-dependency count
      (libraries.io / deps.dev data) — a broken leaf matters less than a broken root
- [ ] publish the at-risk list as a static page + JSON, refreshed on cron
- [ ] "is anyone home" signal: last release date, last commit, maintainer count
      (dead + at-risk + many-dependents = the triage queue)

## Phase 3 — convert

setup.py/setup.cfg -> pyproject.toml. **Prior-art check (2026-06-09): do not write a
converter.** The mechanical path exists:
- `ini2toml` (abravalheri — a setuptools maintainer) does setup.cfg -> pyproject.toml
  (https://ini2toml.readthedocs.io/en/latest/setuptools_pep621.html)
- `setuptools-py2cfg` does static setup.py -> setup.cfg
  (https://github.com/gvalkov/setuptools-py2cfg)
- pypa/setuptools#3214 discussed auto-conversion but it never became a batch effort
- diffoscope (reproducible-builds.org) is the generic deep comparator; verify stays
  opinionated about *this* migration's benign drift, but can emit diffoscope HTML
  reports for failures

So the strategy, in order of reliability:
1. **Wrap, don't write**: py2cfg + ini2toml chained, each output gated by Phase 1
   verify. Covers the static fraction of the tail with zero novel translation code.
2. **Model-assisted for dynamic setup.py**: LLM pass only where the chain fails,
   output only ever accepted via verify. Generation is cheap; the wheel diff is the gate.
3. **Refuse loudly**: truly dynamic builds (custom build_ext, code-generating
   setup.py) get flagged "manual," not half-converted.

- [x] verify-gated wrapper around setuptools-py2cfg + ini2toml (2026-06-09: six, toml, webencodings PASS)
- [ ] verify-gated LLM pass for setup.py the chain can't handle
- [ ] optional diffoscope HTML report on verify failures
- [ ] batch mode: scan -> convert -> verify -> emit per-package result dir

## Phase 4 — corpus

The deliverable that serves the ecosystem without burdening it:
- [ ] public repo of verified conversions (per-package: original ref, converted
      pyproject.toml, verify report, wheel hashes)
- [ ] no unsolicited PRs to maintained projects — the corpus is pull, not push.
      Maintainers, distros, and forks take what they want when they want it.
- [ ] for the truly dead + heavily-depended-on: candidates for adoption
      (EmeritOSS model), decided case by case, by a human.

## Non-goals

- Not a build backend. Not a setuptools fork. Not a PR cannon.
- No fuzzy "probably equivalent" verification — a diff is exact or it's listed.
