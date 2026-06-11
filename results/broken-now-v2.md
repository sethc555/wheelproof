# Broken now, v2 — build-verified census of the top-5000 at-risk set

Every at-risk package's ORIGINAL sdist (1,529 of them) was built against
latest setuptools in a clean python:3.12 container on 2026-06-11.
Result: 1,426 build, 100 fail. The failures, classified by cause:

## Tier A — setuptools 82 removed pkg_resources (12)

- **albumentations** 2.0.8 — pkg_resources removed (setuptools 82)
- **cx-oracle** 8.3.0 — pkg_resources removed (setuptools 82)
- **decopatch** 1.4.10 — pkg_resources removed (setuptools 82)
- **docker-compose** 1.29.2 — pkg_resources removed (setuptools 82)
- **dropbox** 12.0.2 — pkg_resources removed (setuptools 82)
- **html5lib** 1.1 — pkg_resources removed (setuptools 82)
- **imgaug** 0.4.0 — pkg_resources removed (setuptools 82)
- **impyla** 0.23.0 — pkg_resources removed (setuptools 82)
- **jproperties** 2.1.2 — pkg_resources removed (setuptools 82)
- **python-xlib** 0.33 — pkg_resources removed (setuptools 82)
- **sql-formatter** 0.6.2 — pkg_resources removed (setuptools 82)
- **wirerope** 1.0.0 — pkg_resources removed (setuptools 82)

## Tier B — Python 3.12 / setuptools stdlib removals (imp, SafeConfigParser/versioneer, use_2to3) (3)

- **click-spinner** 0.1.10 — Python 3.12 stdlib removal: SafeConfigParser (old versioneer)
- **strenum** 0.4.15 — Python 3.12 stdlib removal: SafeConfigParser (old versioneer)
- **token-bucket** 0.3.0 — Python 3.12 stdlib removal: imp module

## Tier C — sdist is incomplete: setup.py reads files not shipped in it (26)

- **alpaca-trade-api** 3.2.0 — sdist incomplete: setup.py reads unshipped requirements.txt
- **autogluon-common** 1.5.0 — sdist incomplete: setup.py reads unshipped _setup_utils.py
- **autogluon-core** 1.5.0 — sdist incomplete: setup.py reads unshipped _setup_utils.py
- **autogluon-features** 1.5.0 — sdist incomplete: setup.py reads unshipped _setup_utils.py
- **autogluon-tabular** 1.5.0 — sdist incomplete: setup.py reads unshipped _setup_utils.py
- **aws-psycopg2** 1.3.8 — sdist incomplete: setup.py reads unshipped version.txt
- **boto3-type-annotations** 0.3.1 — sdist incomplete: setup.py reads unshipped README.md
- **causallib** 0.10.0 — sdist incomplete: setup.py reads unshipped requirements.txt
- **ccxt** 4.5.57 — sdist incomplete: setup.py reads unshipped README.md
- **databricks-dlt** 0.3.0 — sdist incomplete: setup.py reads unshipped version.py
- **delta-spark** 4.2.0 — sdist incomplete: setup.py reads unshipped version.sbt
- **hubspot-api-client** 12.0.0 — sdist incomplete: setup.py reads unshipped VERSION
- **markdown-to-mrkdwn** 0.3.3 — sdist incomplete: setup.py reads unshipped README.md
- **ocspresponder** 0.5.0 — sdist incomplete: setup.py reads unshipped README.md
- **opik** 2.0.61 — sdist incomplete: setup.py reads unshipped README.md
- **pyobjc-framework-cocoa** 12.2 — macOS-only package on a Linux builder: NOT claimed broken (platform caveat)
- **pyobjc-framework-coreml** 12.2 — macOS-only package on a Linux builder: NOT claimed broken (platform caveat)
- **pyobjc-framework-quartz** 12.2 — macOS-only package on a Linux builder: NOT claimed broken (platform caveat)
- **pyobjc-framework-vision** 12.2 — macOS-only package on a Linux builder: NOT claimed broken (platform caveat)
- **pyquaternion** 0.9.9 — sdist incomplete: setup.py reads unshipped VERSION.txt
- **pytest-homeassistant-custom-component** 0.13.338 — sdist incomplete: setup.py reads unshipped requirements_test.txt
- **python3-logstash** 0.4.80 — sdist incomplete: setup.py reads unshipped README.md
- **spacy-language-detection** 0.2.1 — sdist incomplete: setup.py reads unshipped version.txt
- **torchtnt** 0.2.4 — sdist incomplete: setup.py reads unshipped requirements.txt
- **twirp** 0.0.7 — sdist incomplete: setup.py reads unshipped version.txt
- **wmi** 1.5.1 — sdist incomplete: setup.py reads unshipped README.rst

## Tier D — undeclared build-time imports (fail in any isolated build) (9)

- **boto** 2.49.0 — undeclared build-time import: boto.vendored.six.moves
- **certvalidator** 0.11.1 — undeclared build-time import: asn1crypto
- **ics** 0.7.3 — undeclared build-time import: attr
- **lunarcalendar** 0.0.9 — undeclared build-time import: dateutil
- **ocspbuilder** 0.10.2 — undeclared build-time import: asn1crypto
- **posthoganalytics** 7.18.1 — undeclared build-time import: version
- **rank-bm25** 0.2.2 — undeclared build-time import: version
- **requests-auth-aws-sigv4** 0.7 — undeclared build-time import: requests
- **resend** 2.30.1 — undeclared build-time import: typing_extensions

## Timeouts (unverified, likely heavy builds) (3)

- **grpcio** 1.81.0 — build timeout
- **lxml** 6.1.1 — build timeout
- **uv** 0.11.20 — build timeout

## Unclassified (need eyes) (20)

- **angr** 9.2.221 — (): uid not found: 1000' ERROR Backend subprocess exited when trying to invoke build_wheel
- **awslambdaric** 4.0.0 — atus 1. ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel
- **azure** 5.0.0 — 10646   ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel
- **azure-mgmt** 5.0.0 — 10646   ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel
- **colour** 0.1.5 — u mean: 'get_unpatched'? ERROR Backend subprocess exited when trying to invoke build_wheel
- **frida** 17.11.0 —  non-zero exit status 2. ERROR Backend subprocess exited when trying to invoke build_wheel
- **futures** 3.4.0 — ures']} ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel
- **google-api-python-client-stubs** 1.37.0 — _client_stubs-1.37.0 does not appear to be a Python project: no pyproject.toml or setup.py
- **llvmlite** 0.47.0 —  non-zero exit status 1. ERROR Backend subprocess exited when trying to invoke build_wheel
- **mecab-python3** 1.0.12 — irectory: 'mecab-config' ERROR Backend subprocess exited when trying to invoke build_wheel
- **mpi4py** 4.1.2 — nmpi-dev  # for Open MPI ERROR Backend subprocess exited when trying to invoke build_wheel
- **pprintpp** 0.4.0 — de: 'U' ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel
- **pygame** 2.6.1 — talled. ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel
- **pyhwpx** 1.7.2 —  동작합니다. ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel
- **pyobjc-core** 12.2 — o build ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel
- **pythonnet** 3.1.0 — o such file or directory ERROR Backend subprocess exited when trying to invoke build_wheel
- **shyaml** 0.6.2 — u mean: 'get_unpatched'? ERROR Backend subprocess exited when trying to invoke build_wheel
- **sklearn** 0.0.post12 — package ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel
- **unittest2** 1.1.0 — ject, got 'late_version' ERROR Backend subprocess exited when trying to invoke build_wheel
- **vobject** 0.9.9 — ERSION' ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel

## Environment-dependent (need system deps — NOT claimed broken; listed for honesty) (27)

- **awscrt** 0.34.1 — needs system deps (not claimed broken)
- **catboost** 1.2.10 — needs system deps (not claimed broken)
- **cchardet** 2.1.7 — needs system deps (not claimed broken)
- **ddtrace** 4.10.4 — needs system deps (not claimed broken)
- **dm-tree** 0.1.10 — needs system deps (not claimed broken)
- **fasttext-wheel** 0.9.2 — needs system deps (not claimed broken)
- **google-re2** 1.1.20251105 — needs system deps (not claimed broken)
- **hogql-parser** 1.3.69 — needs system deps (not claimed broken)
- **hydra-core** 1.3.3 — needs system deps (not claimed broken)
- **ibm-db** 3.2.9 — needs system deps (not claimed broken)
- **memray** 1.19.3 — needs system deps (not claimed broken)
- **mmcif** 1.1.1 — needs system deps (not claimed broken)
- **omegaconf** 2.3.1 — needs system deps (not claimed broken)
- **pi-heif** 1.4.0 — needs system deps (not claimed broken)
- **pillow-heif** 1.4.0 — needs system deps (not claimed broken)
- **plyvel** 1.5.1 — needs system deps (not claimed broken)
- **pycrypto** 2.6.1 — needs system deps (not claimed broken)
- **pygit2** 1.19.2 — needs system deps (not claimed broken)
- **pymssql** 2.3.13 — needs system deps (not claimed broken)
- **sasl** 0.3.1 — needs system deps (not claimed broken)
- **scipy** 1.17.1 — needs system deps (not claimed broken)
- **scs** 3.2.11 — needs system deps (not claimed broken)
- **tensorflow-metadata** 1.21.0 — needs system deps (not claimed broken)
- **tensorstore** 0.1.84 — needs system deps (not claimed broken)
- **uamqp** 1.6.11 — needs system deps (not claimed broken)
- **unicorn** 2.1.4 — needs system deps (not claimed broken)
- **xmlsec** 1.3.17 — needs system deps (not claimed broken)

## Caveats (read before quoting numbers)
- pyobjc-framework-* entries invoke macOS's sw_vers: platform mismatch, not breakage.
- **futures** is the Python-2 backport — failing on Python 3 is by design.
- **angr**'s failure ("uid not found") is a harness artifact, not the package.
- **colour** 0.1.5 fails on a setuptools-internal API (get_unpatched) — genuine
  new-setuptools breakage, belongs morally in Tier A.
- ENV tier (need system libs: llvm, mecab, xmlsec1, bazel...) is explicitly NOT
  claimed broken; a fuller builder image would reclassify some.

## Status notes
- Tier A includes the batch-1 set (PRs/issues filed, see outreach/README.md);
  NEW in v2: jproperties, python-xlib.
- omegaconf and hydra-core no longer appear: their 2026-06-11 releases fixed
  them (filed as facebookresearch/hydra#3207, omry/omegaconf#1315).
- Tiers B-D are broken for source installs regardless of the 2026 setuptools
  removals — older breakage nobody noticed, surfaced by the same census.
