# Methods — revised after batch 1 (2026-06-11)

The pipeline, with every revision the first batch forced.

## 1. Detect: static scan is a candidate generator, nothing more

`scan` flags risk markers. Batch 1 ground truth: **14 of 26** static
pkg_resources flags were false positives (guarded imports, pinned build deps),
and the filter entirely missed the ez_setup breakage class (dropbox, impyla)
because the fatal import is inside a vendored bootstrap, not setup.py.

Revisions:
- scan now flags `ez-setup` and `use_2to3` in top-level setup.py as high
- nothing is called "broken" until step 2 says so

## 2. Verify brokenness: `buildcheck` — build the ORIGINAL sdist

The definitive gate. Download the sdist, build it against latest setuptools in
a clean container, record builds/fails + cause. Only build-verified failures
go on the broken-now list, with the 14 static false positives published
alongside as a calibration warning.

## 3. Fix: smallest possible patch, verified both ways

Minimal unbreak (delete vacuous require()s, importlib.metadata for
pkg_resources probes, delete ez_setup bootstraps) — NOT a full pyproject
conversion, which is corpus material. Gate: unpatched sdist fails, patched
sdist builds, in the same clean container. (Wheel-diff is impossible here —
no baseline exists when the original doesn't build. Future: diff against the
last *published* wheel.)

## 4. Triage upstream BEFORE filing — batch 1's biggest lesson

For each verified-broken package, in order:
1. **Repo archived?** → no PR possible; patch is distro/corpus material
   (batch 1: albumentations).
2. **setup.py gone at HEAD?** → product moved on; no upstream path
   (batch 1: docker-compose v1).
3. **Fixed at HEAD but unreleased?** → file a RELEASE REQUEST issue, not a PR.
   Cheapest possible ask and the most effective thing we did: omegaconf
   (38.4M dl/mo) and hydra (15.5M) shipped fixes within HOURS, and hydra came
   back from dormancy. The ask was "release what you already have."
4. **Open PR/issue already covering it?** → join it, don't duplicate.
   Batch 1 failure: we filed cx_Oracle#677 unaware of pre-existing #674.
   Check `gh pr list`/`gh issue list` + search for "pkg_resources" BEFORE filing.
5. **Maintainer formally says wontfix/EOL?** → record it; the package joins
   the "permanently broken on PyPI by upstream decision" set, which is itself
   publishable data.

## 5. Send: GitHub only, human-authorized, reply-obligated

- No email, ever: the July 2025 PyPI phishing campaign used exactly the
  "your package has a problem" shape with metadata-harvested addresses.
- One PR/issue per project. Body: one-line repro
  (`docker run --rm python:3.12 pip install --no-binary :all: <pkg>`),
  the verification statement, what the patch does, and where it came from.
- LLM assistance disclosed via Co-Authored-By trailers.
- Every send is a human decision; replies get answered; outcomes get
  independently verified before being celebrated (we rebuilt omegaconf 2.3.1
  and hydra 1.3.3 from source before thanking the maintainer).
- Reply log lives in outreach/README.md.

## Outcome taxonomy (batch 1 actuals)

| outcome | example | next action |
|---|---|---|
| fixed-by-release | omegaconf, hydra | verify, thank, record |
| PR merged | (none yet) | verify next release |
| wontfix / EOL | cx_Oracle | record; user remediation note |
| archived / no upstream | albumentations, docker-compose v1 | distro material |
| silent | html5lib, imgaug, ... | leave alone; the artifact still helps the next visitor |

## verify-published (v2 gate, added 2026-06-12)

Baseline = the maintainer's own published pure wheel, not a fresh build. Works
for packages whose source tree no longer builds. First live run (the 12
broken-now patches): 6 byte-identical passes (albumentations, docker-compose,
dropbox, html5lib, impyla, wirerope — the strongest claim a patch can carry),
1 correctly out-of-scope (cx-oracle, platform wheels only), and 5 divergences
in three classes:

- **version-stamp files** (decopatch `_version.py`): setuptools_scm stamps
  differ between the maintainer's build and an sdist rebuild. Benign.
- **generated code** (omegaconf/hydra ANTLR parsers): generator version/host
  nondeterminism. Benign but irreducible without pinning the generator.
- **wheel/sdist divergence** (sql-formatter ships `release.py` in the wheel
  but not the sdist; imgaug ships `imgaug/external/README.md`): the published
  wheel was built from a tree that does not match the published sdist. NOT
  benign — this is its own quiet supply-chain finding, and a future census
  candidate: how many of the top 5,000 packages' wheels diverge from their
  sdists?

## v4 revisions (2026-06-13, after batches 3-4 and the divergence census)

**The pristine-HEAD test is mandatory before any HEAD patch is written.**
Batch 4's discriminator: build pristine HEAD (full sdist->wheel) first. It
reclassified 4 of 9 "PR candidates" as fixed-at-HEAD (cheaper release-request),
and caught agents "adapting" patches onto wbond repos for a bug HEAD no longer
had. Sequence is now: pristine test -> classify -> only then patch. Never hand
an agent "apply the equivalent fix" without pristine-fail evidence of what, if
anything, is still broken.

**`python -m build` full-chain (sdist, then wheel FROM that sdist) is the only
honest gate.** Wheel-only builds are blind to the entire incomplete-sdist class
— hubspot/pytest-hacc HEAD would have "passed" a wheel-only check while their
sdists were unbuildable.

**One fix, two artifacts.** The released-sdist patch (hardcoded version is
fine — the version is a constant of that artifact) and the HEAD PR patch
(version must be read dynamically — HEAD moves) are different deliverables
with different verification.

**New outcome category: release-tooling artifact.** Published sdist omits
files that HEAD sdists include (posthog's version.py, hubspot's VERSION).
No code change exists to request; the issue says so explicitly: "the next
release built the normal way fixes this."

**Two-bug PRs.** When upstream fixed the released bug at HEAD but introduced
a new sdist bug (certvalidator/ocspbuilder readme.md), the PR fixes the new
one and the text credits the old fix and asks for the release — both messages
in one artifact, no nagging.

**Uniform failure means harness bug.** Every time ALL items failed identically
(9/9 "FAILS" from a container path mismatch; the canary's first-run false
"AXE DROPPED" from its own malformed package), the fault was ours. Diagnostic
rule: identical failure across heterogeneous items -> suspect the harness
before believing the result. Canaries need positive controls.

**Numbers that travel get two runs.** The divergence census shipped only after
all 98 findings reproduced with exact file-list agreement in an independent
run. Single-run numbers stay in the workshop.

**CLA pre-check on corporate repos** (grep CONTRIBUTING for CLA before
filing): the human whose name signs the PR should know the gate exists before
the bot tells them.

**Ship the remedy with the finding.** The divergence report went out alongside
`divcheck --package <name>` self-audit mode. An ecosystem-level finding plus a
one-command self-check reads as a gift; the finding alone reads as an audit.
