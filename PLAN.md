# wheelproof roadmap

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

setup.py/setup.cfg -> pyproject.toml. Strategy, in order of reliability:
1. **Mechanical first**: setup.cfg is declarative — translate it with table-driven
   rules, no model involved. Covers a large fraction of the tail.
2. **Model-assisted for setup.py**: dynamic setup() calls get an LLM pass, but the
   output is only ever accepted via Phase 1 verify. Generation is cheap; the wheel
   diff is the gate.
3. **Refuse loudly**: packages with truly dynamic builds (C extensions with custom
   build_ext, code-generating setup.py) get flagged "manual," not half-converted.

- [ ] mechanical setup.cfg translator
- [ ] verify-gated LLM pass for setup.py
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
