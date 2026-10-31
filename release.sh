#!/usr/bin/env bash
# release.sh <x.y>        — on a new branch release-v<x.y> from a fresh origin/main, stamp
#                           ledgerboard.py's first line with the release and its hash, run the
#                           checks, and commit "Release v<x.y>". Push it and PR it like any change.
# release.sh --tag <x.y>  — after that PR has squash-merged, with HEAD at origin/main (main in the
#                           anchor's checkout, or `git checkout --detach origin/main` in a worktree,
#                           which cannot hold main): check that the module's header names v<x.y> and
#                           is intact, and tag v<x.y>. What the tag needs is checked, not the branch's
#                           name: a clean tree, HEAD at origin/main, the header, no such tag.
#
# The header is  # ledgerboard v<x.y> sha256:<sha256 of every byte after the first line>
# — the release travels inside the file, so a consumer's copy proves which release it is
# (fixtures/run.py --check-header). Between releases a PR that changes the module may leave the
# header as it is: only a tagged commit's header is checked. Pushes nothing.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
tag=0
if [ "${1:-}" = "--tag" ]; then tag=1; shift; fi
v="${1:-}"
[[ "$v" =~ ^[0-9]+\.[0-9]+$ ]] || { echo "usage: release.sh [--tag] <major.minor>" >&2; exit 2; }
[ -z "$(git status --porcelain)" ] || { echo "the tree is not clean" >&2; exit 2; }
git fetch -q origin
git rev-parse -q --verify "refs/tags/v$v" >/dev/null && { echo "v$v exists" >&2; exit 2; }

if [ "$tag" = 1 ]; then
    [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "HEAD is not origin/main — pull, or: git checkout --detach origin/main" >&2; exit 2; }
    head -1 ledgerboard.py | grep -q "^# ledgerboard v$v sha256:" || { echo "the header does not name v$v" >&2; exit 2; }
    python3 fixtures/run.py --check-header
    git tag -a "v$v" -m "ledgerboard v$v"
    echo "tagged v$v — now: git push origin v$v"
    exit 0
fi

git checkout -q -b "release-v$v" origin/main
python3 - "$v" <<'PY'
import hashlib, sys
p = "ledgerboard.py"
raw = open(p, "rb").read()
first, rest = raw.split(b"\n", 1)
assert first.startswith(b"# ledgerboard "), first
open(p, "wb").write(f"# ledgerboard v{sys.argv[1]} sha256:{hashlib.sha256(rest).hexdigest()}\n".encode() + rest)
PY
python3 fixtures/run.py --check-header
python3 fixtures/run.py
python3 -m unittest discover -s tests -q
git commit -qm "Release v$v" -- ledgerboard.py
echo "committed Release v$v on release-v$v — push it, PR it, merge it, then: ./release.sh --tag $v"
