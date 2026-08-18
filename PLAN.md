# wheelproof roadmap

> **STATE 2026-08-17** (last substantive change 2026-07-10; watchman still running daily): Phases 1–4 shipped. Corpus is public: 1,154 entries,
> **958 pass** (636 mechanical + 322 LLM-pass, each independently wheel-diff
> verified), 120 convert-error, 43 build-error, 32 verify-fail. The scan covers
> the top 5,000 by downloads (1,153 at risk); `buildcheck` proved 100 broken
> today; `divcheck` added a published-wheel/sdist divergence census
> (results/divergence.md).
>
> **Corpus re-verified against setuptools 83.0.0** (2026-07-10,
> results/reverify-setuptools83.md): 948/949 evaluable entries still produce
> byte-identical payloads — no setuptools-83 regression. The run caught one
> false `pass` (pywin32-ctypes): its `setup.py` rewrites `version.py` at module
> top level, so the converter's own execution of `setup.py` contaminated the
> pristine baseline. Reclassified verify-fail, `pyproject.toml` withdrawn.
> **Lesson: snapshot the baseline before any conversion tool touches the tree.**
>
> **Phase 5 — outreach (the current work, and the best result).** 12
> verified-broken packages taken upstream via GitHub PRs/issues only.
> **Seven fixes released** (omegaconf 2.3.1, hydra 1.3.3, token-bucket 0.4.0,
> impyla 0.24.0, click-spinner 0.2.0, dropbox 12.1.0, drf-nested-routers 0.95.3
> — the last from the divergence census, and the maintainer automated his
> whole release pipeline in response) + one PR merged (resend). The other 24
> open threads have had zero maintainer response since 2026-06-11.
> Release requests beat PRs; two maintainers independently re-ran our repro and
> confirmed it. See outreach/README.md for the full reply log.
>
> **Live watch:** `tools/watchman-cron.sh` runs daily (canary + 33 threads).
> Canary as of 2026-08-17: dash/uppercase setup.cfg keys **still build** under
> setuptools **84.0.0** — the second removal has not landed.
>
> **Resume options:** (a) triage the 31 verify-fails — likely systematic
> py2cfg/ini2toml translation gaps worth fixing once; (b) the 8 open PRs have
> sat ~1mo with no maintainer reply (html5lib's repo is dormant since Feb 2024
> and its AppVeyor CI fails on every recent PR — the PR route may be dead for
> the deadest tail); (c) Phase 1 hardening below.

Context: setuptools retries its deprecated-config removal in 2026
(https://www.clientserver.dev/p/setuptools-follows-through-on-a-deprecation,
https://setuptools.pypa.io/en/latest/history.html). The dead tail of PyPI — packages
with gone maintainers — is exactly the set that can't fix itself.

Deadline state (verified 2026-06-09 against the setuptools changelog):
- pkg_resources: REMOVED in v82.0.0 (2026-02-08) — already live; build-time importers
  are broken against current setuptools today
- setup.py install / easy_install: deadline 2025-10-31, enforced
- dash/uppercase setup.cfg keys (the 12k-package breaker of Mar 2025, reverted in
  78.0.2): warning text set the cutoff at 2026-03-03 — now past due, NOT yet
  re-applied as of v82.0.1 (2026-03-09). Can land in any release without further
  notice. Build isolation pulls latest setuptools by default, so it hits every
  unpinned legacy package the day it ships.

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
- [x] walk the top-N PyPI packages by downloads (2026-06: top 5,000 scanned →
      results/top.jsonl, results/top-summary.md; 1,153 at risk)
- [ ] dependency-aware ranking: at-risk packages weighted by reverse-dependency count
      (libraries.io / deps.dev data) — a broken leaf matters less than a broken root
- [ ] publish the at-risk list as a static page + JSON, refreshed on cron
      (JSON exists; no static page yet)
- [ ] "is anyone home" signal: last release date, last commit, maintainer count
      (dead + at-risk + many-dependents = the triage queue). Partially covered by
      `headcheck` (patch vs release-request) and `cla-check`.

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
- [x] verify-gated LLM pass for setup.py the chain can't handle (2026-06-10:
      327 proposals, 282 survived the gate; self-reports counted for nothing)
- [ ] optional diffoscope HTML report on verify failures
- [x] batch mode: scan -> convert -> verify -> emit per-package result dir
      (`batch-convert`; corpus/<pkg>/{pyproject.toml,result.json})

## Phase 4 — corpus

The deliverable that serves the ecosystem without burdening it:
- [x] public repo of verified conversions (per-package: original ref, converted
      pyproject.toml, verify report, wheel hashes) — corpus/, 959 proven entries
- [x] no unsolicited PRs to maintained projects — the corpus is pull, not push.
      Maintainers, distros, and forks take what they want when they want it.
      `adopt` is the puller; outreach was opt-in, one issue/PR per project.
- [ ] for the truly dead + heavily-depended-on: candidates for adoption
      (EmeritOSS model), decided case by case, by a human. Live case:
      html5lib (34.9M dl/mo, dormant since 2024-02, PR #598 unanswered).
- [x] re-verify the corpus whenever setuptools moves — a proof is a claim about
      a build, and the build environment drifts. (2026-07-10 vs setuptools
      83.0.0: 948/949 pass; caught 1 false pass. Re-run on each major bump.)
- [ ] snapshot the pristine tree *before* the converter runs — `setuptools-py2cfg`
      executes `setup.py`, and a top-level side effect there can mutate the very
      baseline the gate compares against (found via pywin32-ctypes).
- [ ] `adopt` refuses trees that already ship a `pyproject.toml`, so 10 corpus
      entries can never be adopted. Decide: drop them, or add a `--replace` path.
- [ ] `result.json` has two schemas (mechanical entries carry `sdist_url`;
      LLM-pass entries carry only `provenance` + version). Backfill `sdist_url`,
      or document it — tools that assume the key silently skip a third of the corpus.

## Non-goals

- Not a build backend. Not a setuptools fork. Not a PR cannon.
- No fuzzy "probably equivalent" verification — a diff is exact or it's listed.
