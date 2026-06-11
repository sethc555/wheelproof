# Outreach state — the 12 verified-broken packages

*Prepared and SENT 2026-06-10 (user-authorized). Live links:*

PRs: html5lib/html5lib-python#598, aleju/imgaug#872, oracle/python-cx_Oracle#677,
smarie/python-decopatch#40, PabloRMira/sql_formatter#183, youknowone/wirerope#32
Issues: dropbox/dropbox-sdk-python#528, facebookresearch/hydra#3207,
cloudera/impyla#616, omry/omegaconf#1315

Watch for replies — these now have a human obligation attached.

All 12 sdist patches verified: patched sdist builds a wheel against setuptools 82
in a clean python:3.12 container; unpatched fails with
`ModuleNotFoundError: No module named 'pkg_resources'`.
(hydra-core/omegaconf verified with Java present — their ANTLR-at-build-time
requirement predates the breakage and is unrelated.)

## PR-ready — branch pushed to fork, `gh pr create` away (6)

| package | dl/month | upstream | branch |
|---|---|---|---|
| html5lib | 34.9M | html5lib/html5lib-python | sethc555/html5lib-python `fix/setuptools-82-pkg-resources` |
| imgaug | 1.0M | aleju/imgaug | sethc555/imgaug `fix/setuptools-82-pkg-resources` |
| cx-oracle | n/a* | oracle/python-cx_Oracle | sethc555/python-cx_Oracle `fix/setuptools-82-pkg-resources` |
| decopatch | n/a* | smarie/python-decopatch | sethc555/python-decopatch `fix/setuptools-82-pkg-resources` |
| sql-formatter | n/a* | PabloRMira/sql_formatter | sethc555/sql_formatter `fix/setuptools-82-pkg-resources` |
| wirerope | n/a* | youknowone/wirerope | sethc555/wirerope `fix/setuptools-82-pkg-resources` |

*pypistats rate-limited; fetch before sending.

All six patches applied to HEAD without conflict (none touched setup.py since
their last release). Five patched HEADs build-verified in container; cx-oracle's
HEAD needs `git submodule update --init` (odpi/) to build — pre-existing, noted
in the PR text below. Each commit message already contains the full
justification + verification statement.

PR title: `Fix sdist build under setuptools >= 82 (pkg_resources removed)`

PR body template:
> setuptools 82.0.0 (2026-02-08) removed `pkg_resources`. Since pip's default
> isolated build installs the latest setuptools, `pip install <pkg>` from sdist
> now fails with `ModuleNotFoundError: No module named 'pkg_resources'`.
> Reproduce: `docker run --rm python:3.12 pip install --no-binary :all: <pkg>`.
> This is the smallest change that removes the dependency; behavior otherwise
> unchanged. Verified: with this patch the sdist builds a wheel against
> setuptools 82 in a clean python:3.12 container.
> (cx-oracle only: HEAD additionally needs the odpi submodule to build —
> unrelated to this change; the released sdist bundles it.)

## Fixed at HEAD, never released — ask for a release, not a PR (4)

| package | dl/month | upstream | ask |
|---|---|---|---|
| omegaconf | 38.4M | omry/omegaconf | release: 2.3.0 sdist (2022) broken; fix sits unreleased |
| hydra-core | 15.5M | facebookresearch/hydra | release: 1.3.2 sdist broken |
| dropbox | 2.5M | dropbox/dropbox-sdk-python | release: 12.0.2 sdist broken (ez_setup) |
| impyla | n/a* | cloudera/impyla | release: 0.23.0 sdist broken (ez_setup) |

Issue title: `Released sdist no longer installs from source (setuptools >= 82); fix exists at HEAD — please cut a release`
Body: reproduce command as above + note that the repo HEAD already removed
pkg_resources/ez_setup, so no code change is requested — only a release.

## No upstream path (2)

- **albumentations** (5.5M/mo): repo ARCHIVED — PRs impossible. Sdist patch
  lives at /tmp/prfix (copy into corpus if wanted). Successor fork exists
  (AlbumentationsX); distros patch downstream.
- **docker-compose v1** (1.3M/mo): setup.py no longer exists upstream (v2 is Go).
  Sdist patch is distro-only material.

## Channel guidance

GitHub PRs/issues only — the July 2025 PyPI phishing campaign used exactly the
"your package has a problem" email shape with metadata-harvested addresses; cold
email is now indistinguishable from that attack. One PR/issue per project, sent
by a human who will answer replies.
