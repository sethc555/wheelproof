# DRAFT — discuss.python.org / Packaging category
# Status: NOT POSTED. Seth reviews, edits, posts under his own account, or doesn't.
# Venue notes: lead with measurement, end with a tooling question, never a callout.

---

**Title: Measured: ~2% of the top-1000 PyPI packages publish wheels whose
payload doesn't match their sdist — should our tooling check this?**

I've been build-checking popular PyPI packages for source-install breakage
(context: the setuptools 82 `pkg_resources` removal quietly broke a number of
released sdists — that project is [wheelproof](https://github.com/sethc555/wheelproof),
all data and methods public). Along the way I ended up measuring something I
haven't seen measured before and would like the packaging community's read on it.

**Method.** For each package: download the published sdist, build a wheel from
it in a clean python:3.12 container, and compare that wheel's *payload* (every
file outside `*.dist-info/`, by content hash) against the maintainer's own
published pure wheel for the same version. Metadata differences are ignored;
`RECORD` and generator lines are ignored; platform-wheel-only packages are out
of scope. Every divergence was re-run independently and reproduced exactly.

**Results.**

- Top 1,000 packages by downloads: 805 comparable; **743 byte-identical**;
  after classifying out setuptools_scm version stamps (benign) and my own
  methodology artifact (sdist builds compile optional C extensions that pure
  wheels deliberately omit), **17 packages (2.1%) genuinely diverge**.
- A legacy-leaning population (1,529 packages flagged for old packaging
  patterns): roughly twice that rate.
- The divergences fall into recognizable classes: files present only in the
  wheel that no sdist build can produce (in some cases modules deleted from
  the project years ago, still shipping in wheels); test suites in wheels but
  excluded from sdists; stale `__pycache__` bytecode from old build
  environments; `py.typed` markers in wheels but missing from sdists (source
  installs silently lose typing); and a small number of wheels containing
  compiled binaries not derivable from the published source artifact.

Full classified data: [results/divergence.md](https://github.com/sethc555/wheelproof/blob/main/results/divergence.md).
Self-check for any maintainer: `wheelproof divcheck --package <name>` (one
command, runs in a container, exact output).

**Why I think it matters.** 1,830 byte-identical packages across both
populations show that exact wheel/sdist agreement is the *norm* — these
divergences are accidents of release tooling and dirty build trees, not
inherent variance. But the accidents have consequences: wheel users and
source builders (distros, `--no-binary` policies, platforms without wheels)
get *different code* for the same version, and nobody is told. Several
maintainers I've reported individual cases to were surprised and fixed them
immediately — the information simply didn't exist before.

**The question.** Is there appetite for making this a checked property
somewhere in the toolchain? Options that occurred to me, in increasing order
of ambition:

1. a `twine check`-style warning when an upload's wheel payload isn't
   derivable from the accompanying sdist (only feasible for pure wheels, and
   optional-C-extension packages need an escape hatch — my own false-positive
   class shows why);
2. a check in `build`/CI actions (cibuildwheel, pypa/gh-action-pypi-publish)
   comparing the artifacts they themselves just built;
3. longer-term, PyPI surfacing wheel/sdist agreement the way it surfaces
   other metadata.

I'm aware of the adjacent reproducible-builds work; this is a narrower and
much cheaper property than full reproducibility (same-tree-ness rather than
bit-for-bit determinism), which is maybe why it's tractable.

Corrections extremely welcome — preferably with a reproduction command; the
repo has the harness and all raw data. If the consensus is "known and not
worth checking," that's a useful answer too.

---
# END DRAFT
# Reviewer checklist for Seth:
# - No package is named in a "binaries" context (debugpy/tls-client appear
#   only in the linked report, with careful wording there).
# - The 14 false positives are disclosed as OUR artifact — keep that; it's
#   the credibility anchor.
# - Tone check: measurement + question. If any sentence reads as a callout,
#   cut it.
