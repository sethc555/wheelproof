#!/usr/bin/env bash
# Re-verify the corpus in clean python:3.12 containers, N shards in parallel.
#
#   tools/reverify.sh <tag> [shards] [-- extra reverify.py args]
#
# e.g.  tools/reverify.sh setuptools84 8
#       tools/reverify.sh smoke 1 -- --only adagio adal --keep-output
#
# Output: results/reverify-<tag>.shard<i>.jsonl (resumable; re-run to continue),
# merge with:  cat results/reverify-<tag>.shard*.jsonl > results/reverify-<tag>.jsonl
#
# Build isolation inside the container installs the *latest* setuptools from
# PyPI, so the run exercises whatever setuptools is current on the run date.
# The setuptools version actually used is recorded in results/reverify-<tag>.env.
set -euo pipefail
cd "$(dirname "$0")/.."

TAG=${1:?tag}; SHARDS=${2:-6}; shift $(( $# >= 2 ? 2 : $# ))
[[ "${1:-}" == "--" ]] && shift
EXTRA=("$@")

IMAGE=python:3.12
CACHE=wheelproof-reverify-pip   # docker named volume (root-owned, so pip actually caches)
mkdir -p results

# Record the toolchain build isolation will pull today.
docker run --rm -v "$CACHE":/root/.cache/pip -e PIP_ROOT_USER_ACTION=ignore $IMAGE bash -c \
  'pip download -q --no-deps -d /tmp/st setuptools build wheel >/dev/null; ls /tmp/st; python -V; date -u' \
  > "results/reverify-$TAG.env"
cat "results/reverify-$TAG.env"

for i in $(seq 0 $((SHARDS-1))); do
  docker run --rm --name "wp-reverify-$TAG-$i" \
    -v "$PWD":/wp:ro -v "$PWD/results":/out -v "$CACHE":/root/.cache/pip \
    -e PYTHONUNBUFFERED=1 -e PYTHONPATH=/wp/src -e PIP_ROOT_USER_ACTION=ignore -e PIP_DISABLE_PIP_VERSION_CHECK=1 \
    $IMAGE bash -c "
      pip install -q build 2>&1 | grep -v '^$' ;
      python /wp/tools/reverify.py --corpus /wp/corpus \
        --output /out/reverify-$TAG.shard$i.jsonl --shard $i --shards $SHARDS ${EXTRA[*]}" \
    > "results/reverify-$TAG.shard$i.log" 2>&1 &
done
wait
echo "done: $(cat results/reverify-$TAG.shard*.jsonl | wc -l) records"
