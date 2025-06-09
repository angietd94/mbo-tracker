#!/usr/bin/env bash
#
# upload_to_github.sh  —  push a whole folder to angietd94/mbo-tracker (branch: main)
#
#   Usage:  ./upload_to_github.sh /full/path/to/mbo            # commits everything
#           GITHUB_TOKEN=ghp_xxx ./upload_to_github.sh ~/mbo   # token via env-var
#
set -euo pipefail
IFS=$'\n\t'

########################################
# USER SETTINGS (edit once)
########################################
GITHUB_USERNAME="angietd94"
REPO_NAME="mbo-tracker"
BRANCH="main"                              # we only push here
AUTHOR_NAME="Angelica Tacca"
AUTHOR_EMAIL="angelicataccadughetti@gmail.com"

# Anything that should NEVER be committed (keep this short!)
ALWAYS_IGNORE=(
  ".env" "*.pem" "*.key" "*.crt"
)
########################################

# ─── ARGUMENT CHECKS ──────────────────────────────────────────────
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /full/path/to/folder-to-sync" >&2
  exit 1
fi
WORK_DIR=$(realpath "$1")
if [[ ! -d "$WORK_DIR" ]]; then
  echo "❌  $WORK_DIR is not a directory" >&2
  exit 1
fi

# ─── TOKEN ───────────────────────────────────────────────────────
: "${GITHUB_TOKEN:=$(read -rsp 'GitHub Personal Access Token: ' _tok && echo $_tok && echo)}"

REMOTE="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
REMOTE_AUTH="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

# ─── GIT INIT / CONFIG (runs once) ───────────────────────────────
cd "$WORK_DIR"
if [[ ! -d .git ]]; then
  git init
  git switch -c "$BRANCH"
  git config user.name  "$AUTHOR_NAME"
  git config user.email "$AUTHOR_EMAIL"
  git remote add origin "$REMOTE"
fi

# ─── ENSURE DEFAULT BRANCH EXISTS REMOTELY ───────────────────────
git fetch --prune origin "$BRANCH" || true

# ─── OPTIONAL: ignore a *small* set of secrets ───────────────────
if [[ ${#ALWAYS_IGNORE[@]} -gt 0 ]]; then
  touch .git/info/exclude   ## keeps ignore rules *out* of the repo itself
  for p in "${ALWAYS_IGNORE[@]}"; do
    grep -qxF "$p" .git/info/exclude || echo "$p" >> .git/info/exclude
  done
fi

# ─── REBASE IF REMOTE IS AHEAD, OTHERWISE JUST CARRY ON ──────────
if git show-ref --quiet "refs/remotes/origin/$BRANCH"; then
  git pull --rebase --autostash origin "$BRANCH"
fi

# ─── ADD EVERYTHING, COMMIT, PUSH ────────────────────────────────
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Sync $(date '+%F %T')"
else
  echo "• Nothing new to commit."
fi

echo "🚀  Pushing to GitHub ($BRANCH)…"
git push --follow-tags --set-upstream "$REMOTE_AUTH" "$BRANCH"

echo "✅  All done – check $REMOTE/tree/$BRANCH"
