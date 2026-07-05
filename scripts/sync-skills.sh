#!/usr/bin/env bash
# sync-skills.sh — pull the latest shared skills from GitHub.
# Run on either account's machine. Safe to run repeatedly.
# Point REPO_DIR at your local clone of stu-shared-skills.
set -euo pipefail
REPO_DIR="${1:-$HOME/stu-shared-skills}"

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "No git repo at $REPO_DIR. Clone it first:"
  echo "  git clone git@github.com:<your-username>/stu-shared-skills.git \"$REPO_DIR\""
  exit 1
fi

cd "$REPO_DIR"
echo "[sync-skills] pulling latest…"
git pull --ff-only
echo "[sync-skills] done. In Claude Code run:  /plugin marketplace update stu-shared-skills"
