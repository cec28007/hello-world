#!/usr/bin/env bash
# Pull latest data from Tesla and commit the change. Run by the systemd timer.
# Assumes the repo is checked out with a remote that this host can push to
# (deploy key or PAT) on the dashboard branch.
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/hello-world}"
BRANCH="${BRANCH:-claude/tesla-ownership-dashboard-2wy9fm}"
BACKEND="${TESLA_BACKEND:-fleet}"

cd "$REPO_DIR"

git fetch --quiet origin "$BRANCH" || true
git checkout --quiet "$BRANCH"
git pull --quiet --rebase origin "$BRANCH" || true

python3 fetch_tesla.py "$BACKEND"

if ! git diff --quiet -- data.js; then
  git add data.js
  git commit -q -m "Auto: Tesla data $(date -u +%Y-%m-%d)"
  for i in 1 2 4 8; do
    git push origin "$BRANCH" && break
    echo "push failed, retrying in ${i}s..."; sleep "$i"
  done
  echo "Pushed updated data.js"
else
  echo "No change in data.js today"
fi
