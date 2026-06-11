# Batch 2 triage — 2026-06-11

From the buildcheck census (results/broken-now-v2.md), deduped against batch 1.
Per METHODS.md: before ANY send, read the repo's open PRs/issues for prior art
(the count column in the raw triage is noisy — humans/agents must read hits).

## Release-request candidates — likely fixed/migrated at HEAD (13)
Verify at HEAD first (build the repo!), then file 'please cut a release'.

- [A] **jproperties** (pkg_resources) — Tblue/python-jproperties [NO-SETUP-PY-AT-HEAD]
- [A*] **colour** (setuptools internal API) — vaab/colour [SIGNATURE-GONE-AT-HEAD]
- [A*] **shyaml** (setuptools internal API) — 0k/shyaml [SIGNATURE-GONE-AT-HEAD]
- [C] **autogluon-common** (reads unshipped _setup_utils.py) — autogluon/autogluon [NO-SETUP-PY-AT-HEAD]
- [C] **autogluon-core** (reads unshipped _setup_utils.py) — autogluon/autogluon [NO-SETUP-PY-AT-HEAD]
- [C] **autogluon-features** (reads unshipped _setup_utils.py) — autogluon/autogluon [NO-SETUP-PY-AT-HEAD]
- [C] **autogluon-tabular** (reads unshipped _setup_utils.py) — autogluon/autogluon [NO-SETUP-PY-AT-HEAD]
- [C] **boto3-type-annotations** (reads unshipped README.md) — alliefitter/boto3_type_annotations [NO-SETUP-PY-AT-HEAD]
- [C] **causallib** (reads unshipped requirements.txt) — BiomedSciAI/causallib [NO-SETUP-PY-AT-HEAD]
- [C] **ccxt** (reads unshipped README.md) — ccxt/ccxt [NO-SETUP-PY-AT-HEAD]
- [C] **opik** (reads unshipped README.md) — comet-ml/opik [NO-SETUP-PY-AT-HEAD]
- [D] **ics** (undeclared import attr) — C4ptainCrunch/ics.py [NO-SETUP-PY-AT-HEAD]
- [D] **resend** (undeclared import typing_extensions) — resendlabs/resend-python [SIGNATURE-GONE-AT-HEAD]

## PR candidates — breakage still present at HEAD (20)
Each needs: prior-art read -> minimal patch -> verify (unpatched fails, patched builds) -> fork+branch.

- [A] **python-xlib** (pkg_resources) — python-xlib/python-xlib
- [B] **click-spinner** (py3.12/stdlib removal) — click-contrib/click-spinner
- [B] **strenum** (py3.12/stdlib removal) — irgeek/StrEnum
- [B] **token-bucket** (py3.12/stdlib removal) — falconry/token-bucket
- [C] **alpaca-trade-api** (reads unshipped requirements.txt) — alpacahq/alpaca-trade-api-python
- [C] **aws-psycopg2** (reads unshipped version.txt) — AbhimanyuHK/aws-psycopg2
- [C] **delta-spark** (reads unshipped version.sbt) — delta-io/delta
- [C] **hubspot-api-client** (reads unshipped VERSION) — HubSpot/hubspot-api-python
- [C] **markdown-to-mrkdwn** (reads unshipped README.md) — fla9ua/markdown_to_mrkdwn
- [C] **pyquaternion** (reads unshipped VERSION.txt) — KieranWynn/pyquaternion
- [C] **pytest-homeassistant-custom-component** (reads unshipped requirements_test.txt) — MatthewFlamm/pytest-homeassistant-custom-component
- [C] **python3-logstash** (reads unshipped README.md) — israel-fl/python3-logstash
- [C] **spacy-language-detection** (reads unshipped version.txt) — davebulaval/spacy-language-detection
- [C] **torchtnt** (reads unshipped requirements.txt) — pytorch/tnt
- [D] **certvalidator** (undeclared import asn1crypto) — wbond/certvalidator
- [D] **lunarcalendar** (undeclared import dateutil) — wolfhong/LunarCalendar
- [D] **ocspbuilder** (undeclared import asn1crypto) — wbond/ocspbuilder
- [D] **posthoganalytics** (undeclared import version) — posthog/posthog-python
- [D] **rank-bm25** (undeclared import version) — dorianbrown/rank_bm25
- [D] **requests-auth-aws-sigv4** (undeclared import requests) — andrewjroth/requests-auth-aws-sigv4

## No upstream path (5)

- **boto** (undeclared import boto.vendored.six.moves) — ARCHIVED/STILL-PRESENT-AT-HEAD
- **databricks-dlt** (reads unshipped version.py) — no repo
- **ocspresponder** (reads unshipped README.md) — REPO-404
- **twirp** (reads unshipped version.txt) — no repo
- **wmi** (reads unshipped README.rst) — no repo

## Notes
- autogluon-*: monorepo — root setup.py check is unreliable; per-package dirs
  need a manual look before classifying. The sdist bug (unshipped _setup_utils.py)
  is real either way.
- delta-spark/torchtnt: monorepo sdist-publishing bugs; fix belongs in their
  release tooling, frame the issue that way.
- boto: ARCHIVED + dead since 2018 — permanently-broken bucket with cx_Oracle.
