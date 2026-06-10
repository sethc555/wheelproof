# Broken now — verified sdist build failures against current setuptools

setuptools v82.0.0 (2026-02-08) removed pkg_resources. Each package below was
**actually built** from its latest sdist in a clean python:3.12 container with
default build isolation (which installs latest setuptools) on 2026-06-09, and
**failed with `ModuleNotFoundError: No module named 'pkg_resources'`**.
This is not a prediction; these builds fail today.

## Verified broken (12):

- **albumentations** 2.0.8
- **cx-oracle** 8.3.0
- **decopatch** 1.4.10
- **docker-compose** 1.29.2
- **dropbox** 12.0.2
- **html5lib** 1.1
- **hydra-core** 1.3.2
- **imgaug** 0.4.0
- **impyla** 0.23.0
- **omegaconf** 2.3.0
- **sql-formatter** 0.6.2
- **wirerope** 1.0.0

## Import pkg_resources in setup.py but still build (14):
guarded imports or pinned build requirements — listed for completeness, not at issue

- asyncpg
- clickclick
- elastic-apm
- google-apitools
- humanfriendly
- macholib
- makefun
- py-ubjson
- pyannote-audio
- pytest-cases
- stone
- supervisor
- tinytuya
- uvloop

Method: candidates = packages whose setup.py imports pkg_resources, from the
wheelproof top-5000 scan (results/top.jsonl); each candidate then build-verified.
Raw results: results/broken-verified.json.
