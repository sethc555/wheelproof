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

## Execution order
1. Verify: existing PRs (A), HEAD states (B) — container builds, no public action
2. Prep: patches + forks for C and D
3. Sends: human-authorized, per METHODS.md
