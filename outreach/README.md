# Outreach state — the 12 verified-broken packages

*Prepared and SENT 2026-06-10 (user-authorized). Live links:*

PRs: html5lib/html5lib-python#598, aleju/imgaug#872, oracle/python-cx_Oracle#677,
smarie/python-decopatch#40, PabloRMira/sql_formatter#183, youknowone/wirerope#32
Issues: dropbox/dropbox-sdk-python#528, facebookresearch/hydra#3207,
cloudera/impyla#616, omry/omegaconf#1315

Watch for replies — these now have a human obligation attached.

Reply log:
- 2026-07-31 drf-nested-routers#392: **FIXED — alanjds released 0.95.3** after
  automating the release pipeline (PR #401: "we should not see these kind of
  issues anymore"); "thanks @sethc555 for the nudge." Twice asked us to check
  the result (07-23 TestPyPI, 07-31 PyPI). Verified 2026-08-17: published
  wheel has zero `.pyc`, sdist ships `pyproject.toml` (PEP 621, setuptools>=61)
  and builds under setuptools 84.0.0 with a payload byte-identical to the
  published wheel. Issue closed. Seventh fix; first from the divergence census
  (batch 3) rather than the setuptools-82 breakage set. We replied 2026-08-17
  confirming the verification.
- 2026-07-10 dropbox#528: **FIXED — AndreyVMarkelov released 12.1.0** and
  independently re-ran our repro against the released sdist under setuptools
  82.0.1: builds, installs, imports cleanly. Issue closed as completed. 2.5M
  dl/mo unbroken; second maintainer to corroborate a wheelproof verification
  rather than take it on trust. Verified on PyPI (sdist+wheel, 2026-07-10).
- 2026-06-26 dropbox#528: Dropbox (shuyck) triaged — "We're looking into it and
  we'll follow up here once we have an update." → resolved 2026-07-10 (above).
- 2026-06-23 click-spinner#32: **FIXED — bfontaine released 0.1.11 then 0.2.0**
  (same day; switched setup.py→uv, Travis→GH Actions, CI py3.8–3.14). A new
  maintainer took over (after yoavram's ownership-transfer offer) and shipped.
  Closed as completed; 0.2.0 sdist+wheel verified on PyPI 2026-06-23.
- 2026-06-19 impyla#616: **FIXED — csringhofer (Cloudera) released 0.24.0**
  ("Finally released 0.24.0. Closing this issue."), confirming the 0.24a1 alpha
  fix we verified earlier. Issue closed. Was the last outstanding "promised" item.
- 2026-06-16 valkey-py#262: maintainer (mkmkme) — "I am aware of this and will
  push new libvalkey-py and valkey-py as soon as possible (hopefully this
  weekend)." Release committed; py.typed present in wheel since 6.2.0rc1 but
  missing from the last released sdist (6.1.1). NOT YET SHIPPED as of 2026-06-23
  (PyPI still valkey 6.1.1 / libvalkey 4.0.1 — soft ETA slipped); watch PyPI.
- 2026-06-15 resend-python#216: **MERGED by drish** ("thanks for the
  contribution") — first merged-PR outreach win (others were maintainer-cut
  releases). Lands for users at resend's next release.
- 2026-06-15 posthog#660: **CLOSED** by marandaneto (pointed at
  README_ANALYTICS.md) — `posthoganalytics` twin acknowledged as a documented
  separate distribution; no code fix, maintainer-closed.
- 2026-06-15 click-spinner#32: owner (yoavram) declined a release, instead
  offered co-maintainer/ownership transfer. → resolved 2026-06-23: new
  maintainer bfontaine released 0.2.0 (see top of log).
- 2026-06-17 opik#7065: after closing our #7036, maintainer (jverre) re-opened
  the same fix as his own PR #7065, then closed it unmerged (branch since
  deleted). Maintainer carried the change but neither PR merged — opik sdist
  fix still unresolved upstream.
- 2026-06-11 cx_Oracle#677: WONTFIX by maintainer (anthony-tuininga) — cx_Oracle
  is EOL, no releases ever planned; duplicate of pre-existing #674 (prior-art
  lesson: check open PRs, not just HEAD). cx-oracle joins docker-compose v1 in
  the "permanently broken sdist on PyPI by upstream decision" bucket;
  remediation for users = setuptools<82 in build env or migrate to
  python-oracledb. We closed-with-thanks.
- 2026-06-11 wirerope#32: CodeRabbit bot review passed (trivial), no human yet.
- 2026-06-11 omegaconf#1315: **FIXED — omry released 2.3.1** within hours;
  independently verified (clean py3.12 container, source install succeeds).
  38.4M dl/mo unbroken.
- 2026-06-14 posthog#660: PostHog (dustinbyrne) triaged — scoped to the
  `posthoganalytics` twin distribution (main `posthog` package unaffected);
  we replied confirming scope + that it still has public PyPI consumers.
- 2026-06-14 drf-nested-routers#392: maintainer (alanjds) — "Thanks a lot for
  the report. Let's cut a new release..." Another release agreed. → released
  0.95.3 on 2026-07-31 (above).
- 2026-06-14 impyla#616: third-party user independently confirmed our
  verification of 0.24a1 and asked for the stable release ETA — first
  community corroboration of a wheelproof finding.
- 2026-06-12 token-bucket#29: **FIXED — vytas7 (Falcon core) released 0.4.0**
  ("This is now resolved fixed"), after first agreeing "it is time for release
  after almost 5 years." sdist (0.3.0) failed to build on py3.12; 0.4.0 builds.
- 2026-06-12 impyla#616: maintainer (csringhofer, Cloudera) — 0.24 release
  planned soon; 0.24a1 alpha already fixes it (independently verified).
  → resolved 2026-06-19, 0.24.0 released (see top of log).
- 2026-06-11 hydra#3207: **FIXED — omry released 1.3.3** ("Hydra was dormant
  for a while and is now maintained again"); independently verified. 15.5M dl/mo.

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
| omegaconf | 38.4M | omry/omegaconf | ✅ FIXED: 2.3.1 released 2026-06-11, verified |
| hydra-core | 15.5M | facebookresearch/hydra | ✅ FIXED: 1.3.3 released 2026-06-11, verified |
| dropbox | 2.5M | dropbox/dropbox-sdk-python | ✅ FIXED: 12.1.0 released 2026-07-10 |
| impyla | n/a* | cloudera/impyla | ✅ FIXED: 0.24.0 released 2026-06-19 |

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
