# Broken now — builds failing against current setuptools (>=82.0.0, 2026-02-08)

pkg_resources was removed from setuptools in v82.0.0. These packages import
pkg_resources from setup.py, so building their sdist in a default isolated
build environment (which installs latest setuptools) fails today — this is
not a future risk. Source: wheelproof scan of the top-5000 PyPI packages
by downloads, 2026-06-09.

**26 packages:**

- **albumentations** 2.0.8 (imported in setup.py)
- **asyncpg** 0.31.0 (imported in setup.py)
- **clickclick** 20.10.2 (imported in setup.py)
- **cx-oracle** 8.3.0 (imported in setup.py)
- **decopatch** 1.4.10 (imported in setup.py)
- **docker-compose** 1.29.2 (imported in setup.py)
- **dropbox** 12.0.2 (imported in ez_setup.py)
- **elastic-apm** 6.26.1 (imported in setup.py)
- **google-apitools** 0.5.35 (imported in ez_setup.py)
- **html5lib** 1.1 (imported in setup.py)
- **humanfriendly** 10.0 (imported in setup.py)
- **hydra-core** 1.3.2 (imported in setup.py)
- **imgaug** 0.4.0 (imported in setup.py)
- **impyla** 0.23.0 (imported in ez_setup.py)
- **macholib** 1.16.4 (imported in setup.py)
- **makefun** 1.16.0 (imported in setup.py)
- **omegaconf** 2.3.0 (imported in setup.py)
- **py-ubjson** 0.16.1 (imported in ez_setup.py)
- **pyannote-audio** 4.0.4 (imported in setup.py)
- **pytest-cases** 3.10.1 (imported in setup.py)
- **sql-formatter** 0.6.2 (imported in setup.py)
- **stone** 3.3.9 (imported in ez_setup.py)
- **supervisor** 4.3.0 (imported in setup.py)
- **tinytuya** 1.18.1 (imported in setup.py)
- **uvloop** 0.22.1 (imported in setup.py)
- **wirerope** 1.0.0 (imported in setup.py)
