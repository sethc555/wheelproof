# Batch 2 action plan — after prior-art reads (2026-06-11)

30 repos read (open AND closed issues/PRs). The reads reshaped everything:
half of these breakages were already known, fixed, or refused — filing blind
would have duplicated seven existing PRs.

## A. Support existing stalled fix PRs (7) — verify them, comment with proof
The wheelproof move inverted: someone else wrote the fix, it sits unreviewed;
we add independent build-verification to unstick it. No new PRs.
- colour: vaab/colour#66 (d2to1 removal, open since 2023)
- shyaml: 0k/shyaml#67 (same, cites exact ImportError)
- python-xlib: python-xlib/python-xlib#290 (+ issue #286; dormant since 2023)
- strenum: irgeek/StrEnum#34 (+ issue #38; maintainer unresponsive)
- boto3-type-annotations: #12 (+ issue #17; dormant)
- torchtnt: pytorch/tnt#960 (+ issue #959; zero maintainer comments)
- autogluon: #5688 (PEP 621 migration; + issue #3730)

## B. Fixed in repo, never released (7) — release-request issues
The omegaconf/hydra play. Verify HEAD/PR actually builds first.
- jproperties (pyproject at HEAD since 2024, no release)
- resend (typing_extensions import dropped incidentally in #149)
- ics (hatch migration merged 2022 — FOUR YEARS unreleased)
- token-bucket (falconry/token-bucket#24 merged 2023-07, never released)
- python3-logstash (#10 MANIFEST.in fix merged 2020 — SIX YEARS unreleased)
- ocspbuilder (partial fix committed after issue #8 (2016!), never released)
- causallib (#79 claims shipped in v0.10.0 — but our census FAILED v0.10.0;
  verify carefully, possibly sdist regression to report)

## C. Clear to file — no prior art (11) — patch + verify + PR (or issue+PR)
- opik (breakage persists at HEAD, monorepo README path)
- pytest-homeassistant-custom-component, aws-psycopg2, hubspot-api-client,
  markdown-to-mrkdwn, spacy-language-detection (incomplete sdists)
- rank-bm25, requests-auth-aws-sigv4, certvalidator, posthoganalytics
  (undeclared build imports)
- click-spinner (3.12/versioneer; repo seeking maintainers)

## D. Join existing open issues with a fix (2)
- pyquaternion: issue #64 open since 2020 (VERSION.txt missing) — PR + link
- lunarcalendar: issue #11 open since 2019 (exact breakage) — PR + link

## E. Record as upstream-refused / deprecated (3)
- delta-spark: maintainer states PyPI tarball "not designed to build" (#997)
- alpaca-trade-api: deprecated for alpaca-py, maintenance ended 2022
- ccxt: exact report #16220 closed as STALE (not refused) — candidate for a
  fresh, verified, fix-attached re-raise; judgment call

## Verification results (2026-06-11, container, sdist->wheel gate)

A — stalled PRs VERIFIED working (support-comment ready):
- colour#66 OK, shyaml#67 OK, python-xlib#290 OK, strenum#34 OK, torchtnt#960 OK
- boto3-type-annotations#12 INSUFFICIENT — setup.py still reads ../README.md
  which escapes the sdist; needs a different fix (moves to patch bucket)
- autogluon#5688 not verified (monorepo build deferred)

B — HEADs VERIFIED building (release-request ready):
- jproperties OK, ics OK, token-bucket OK, python3-logstash OK
- causallib HEAD OK — but the v0.10.0 sdist on PyPI fails (reads unshipped
  requirements.txt): the fix is merged yet the published artifact is broken.
  Ask = republish (0.10.1), not just release.
- resend HEAD STILL BROKEN (typing_extensions import persists) — patch bucket
- ocspbuilder HEAD STILL BROKEN (partial 2016 fix incomplete) — patch bucket

## Pre-send deep scan (2026-06-11) — second-pass prior art on the send list itself

- python3-logstash: open issue #12 "New PyPI release" since 2020 — JOIN it with
  verification comment; do NOT file a new issue.
- ics: maintainer is aware (release timeline lives in #245, closed #437 points
  there) and himself recommends the `ical` package as the alternative. A new
  release-request would be noise. SKIP; recorded as aware-but-blocked.
- strenum#34: thread already has pings incl. a Homebrew maintainer (2025-11)
  patching downstream. Our comment adds verification, not another ping — keep,
  worded accordingly.
- colour#66, shyaml#67, python-xlib#290, tnt#960: zero comments — clear.
- jproperties, token-bucket, causallib: no existing release issues — clear.

REVISED SEND LIST (9): 5 PR-support comments (colour#66, shyaml#67,
python-xlib#290, strenum#34, tnt#960) + 3 new release-request issues
(jproperties, token-bucket, causallib-republish) + 1 join-comment
(python3-logstash#12).

## Execution order
1. Verify: existing PRs (A), HEAD states (B) — container builds, no public action
2. Prep: patches + forks for C and D
3. Sends: human-authorized, per METHODS.md
