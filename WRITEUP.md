# I build-checked the top 5,000 PyPI packages. 100 are broken right now.

*2026-06-12 · [repo](https://github.com/sethc555/wheelproof) · all claims in this
post are backed by data files in this repository and public GitHub threads*

## The hook

On June 10th I filed a GitHub issue against omegaconf — a configuration library
that gets 38 million downloads a month — saying its released sdist couldn't be
installed from source anymore, that the fix already existed unreleased in the
repo, and that no code change was needed: just a release. I included a one-line
reproduction:

```
docker run --rm python:3.12 pip install --no-binary :all: omegaconf
```

The maintainer released the fix within hours. Same day, same maintainer, same
story for Hydra — Meta's ML configuration framework, 15M downloads/month —
with a bonus: *"Hydra was dormant for a while and is now maintained again."*

That was the third day of this project. This post is about the other 98 broken
packages, the method, and what actually moves maintainers.

## Why packages are quietly breaking

setuptools is finally removing its deprecated surface. `pkg_resources` was
removed in v82.0.0 (February 2026). The dash-separated `setup.cfg` keys that
broke 12,000+ packages in the reverted March 2025 attempt are past their
announced cutoff and can be re-removed in any release. Because pip's default
isolated build installs the *latest* setuptools, the day a removal ships, every
unpinned legacy package breaks everywhere simultaneously — but only on the
**source-install path**. Wheel users feel nothing. The people who bleed are
distros, Homebrew, conda-forge, Yocto, air-gapped environments, reproducible
builds, and any platform without prebuilt wheels. They bleed quietly, one at a
time, and patch downstream.

## The census

I scanned the top 5,000 PyPI packages by downloads ([results/top.jsonl](results/top.jsonl)):
**1,529 (32%) carry legacy-build risk markers**, 1,153 of them severe.

Static flags turned out to be nearly useless as verdicts: of 26 packages whose
setup.py imports pkg_resources, **14 build fine anyway** (guarded imports,
pinned build requirements). So the real census is empirical: I built every
at-risk package's actual sdist against current setuptools in a clean container
([results/buildcheck.jsonl](results/buildcheck.jsonl)).

**Of 1,529 at-risk packages, exactly 100 verifiably fail to build today** —
and the breakdown surprised me ([results/broken-now-v2.md](results/broken-now-v2.md)):

| count | cause |
|---|---|
| 12 | pkg_resources removal (the "expected" breakage) |
| 26 | **incomplete sdists** — setup.py reads files never shipped (ccxt, delta-spark, AutoGluon, opik…) |
| 9 | undeclared build-time imports — broken in any isolated build |
| 3 | Python 3.12 stdlib removals (`imp`, `SafeConfigParser`) |
| 50 | environment-dependent, timeouts, or needing eyes — honestly bucketed, not claimed |

The setuptools story I went looking for is a *quarter* of the verified
breakage. The bigger story is packaging rot that predates it: sdists published
from monorepos missing their own files, builds that have never worked in
isolation, fixes merged years ago and never released. Several of these had open
issues since 2019–2020 with zero maintainer responses — diffuse harm with no
aggregator.

## The method: migration you can check, not trust

The ecosystem's allergy to machine-generated contributions is rational. FFmpeg
calls AI-generated security reports "CVE slop"; libxml2's maintainer quit over
unpaid triage of exactly this. Generation is cheap. **Verification is the
scarce good.** So every artifact here carries machine-checkable proof:

- **Conversions**: build the original tree and the converted tree, unpack both
  wheels, require byte-identical payloads. 959 of 1,153 doomed packages now
  have proven `pyproject.toml` conversions in [corpus/](corpus/). The gate
  caught real defects at every stage: conversions that silently dropped data
  files, leaked test suites into wheels, lost console scripts, shipped
  pure-Python wheels missing their C extensions.
- **LLM assistance, gated identically**: packages with dynamic setup.py were
  converted by LLM agents; **282 of 327 proposals survived independent
  wheel-diff verification** (86%), self-reports counting for nothing, and 42
  were honest refusals (C extensions, build-time codegen). Provenance is
  recorded per package.
- **Breakage claims**: nothing is called broken until its sdist actually fails
  in a clean container. The 14 static false positives are published alongside
  the findings as a calibration warning.

## What actually moves maintainers

19 outreach actions over two batches, every claim verified before sending.
Results so far:

1. **"Please cut a release" beats pull requests, 4-to-0.** Where a fix was
   already merged but unreleased, a release-request issue worked almost every
   time: omegaconf (hours), Hydra (hours), impyla (Cloudera: 0.24 planned,
   alpha verified), token-bucket (Falcon maintainer: "I agree it is time for
   release after almost 5 years"). My actual PRs? Zero merges so far. Asking
   someone to ship what they already wrote respects their authority and costs
   them minutes; sending code invokes review obligations they may have no
   capacity for. The highest-leverage contribution to a dormant project is
   often *no code at all*.
2. **Verification comments unstick stalled PRs.** Several repos already had
   correct fixes sitting unreviewed for 1–3 years (one with a Homebrew
   maintainer pleading for a merge). I checked each PR out, built it in a
   container, and posted the proof. That's a contribution with zero
   slop-surface: no new code, just evidence.
3. **Prior-art discipline, twice.** Before filing anything: search open AND
   closed issues and PRs. My one duplicate (cx_Oracle — an existing PR I
   missed, plus a formal EOL wontfix) taught the rule; the second pass caught
   a five-year-old release request I would otherwise have duplicated, and a
   maintainer who already recommends a successor package.
4. **GitHub only, never email.** The July 2025 PyPI phishing campaign used
   metadata-harvested emails with exactly the "your package has a problem"
   shape. A cold email with a fix attached is now indistinguishable from an
   attack. Public, signed, verifiable threads or nothing.
5. **Verify outcomes before celebrating.** I rebuilt omegaconf 2.3.1 and Hydra
   1.3.3 from source before thanking anyone.

## Honest caveats

- Source installs are a small fraction of installs; the harm is real but
  concentrated in infrastructure users, and the counterfactual is acceleration
  (maintainers would likely have fixed things eventually) rather than rescue.
- The corpus (959 proven conversions) has no confirmed adopters yet. Its value
  is contingent on the dash-key removal shipping, or on distros discovering it.
- Conversions were verified against the *released sdist*; repos drift.
- Everything here executes untrusted setup.py code — containers only.
- This work was done with heavy LLM assistance (disclosed in every commit via
  Co-Authored-By), one person supervising, in four days. The entire premise is
  that this is safe *only* because every artifact is machine-verified rather
  than trusted. I would not have filed a single issue on model say-so — and
  the recheck rounds caught model errors that would have made messages
  factually wrong.

## What's next

A watcher for the setuptools release that re-removes the dash keys (the day it
ships, 1,153 packages' worth of prepared fixes stop being inventory); a
verify-against-published-wheel gate for packages whose baseline build is
already broken; the remaining unreported-breakage patches; and the same
architecture pointed at a bigger target: autotools → Meson, where the long
tail is larger, the verification harness doesn't exist, and the moat is the
same — **migration you can check, not trust.**

*Data, code, methods: [github.com/sethc555/wheelproof](https://github.com/sethc555/wheelproof).
Corrections welcome — preferably with a reproduction command.*
