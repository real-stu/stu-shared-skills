#!/usr/bin/env bash
# push-skills.sh — commit and push local skill changes so the other account gets them.
set -euo pipefail
REPO_DIR="${1:-$HOME/stu-shared-skills}"
MSG="${2:-Update shared skills}"
cd "$REPO_DIR"
git add -A
if git diff --cached --quiet; then
  echo "[push-skills] nothing to commit."
  exit 0
fi
git commit -m "$MSG"
git push
echo "[push-skills] pushed. Other account: run scripts/sync-skills.sh (or /plugin marketplace update)."
