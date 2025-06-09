#!/usr/bin/env bash
# Sync this folder to the existing GitHub repo angietd94/mbo-tracker
set -euo pipefail

# ───── USER SETTINGS ───────────────────────────────────────────────
GITHUB_USERNAME="angietd94"
REPO_NAME="mbo-tracker"
DEFAULT_BRANCH="main"          # change to 'master' if you prefer
AUTHOR_NAME="Angelica Tacca"
AUTHOR_EMAIL="angelicataccadughetti@gmail.cm"
# ───────────────────────────────────────────────────────────────────

# 0. Make sure we have a token (repo scope) in $GITHUB_TOKEN
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  read -rsp "GitHub Personal Access Token: " GITHUB_TOKEN
  echo
fi

REMOTE="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
REMOTE_AUTH="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

# 1. Initialise git only once
if [[ ! -d .git ]]; then
  git init
  git checkout -b "${DEFAULT_BRANCH}"
  git config user.name  "${AUTHOR_NAME}"
  git config user.email "${AUTHOR_EMAIL}"
  git remote add origin "${REMOTE}"
fi

# 2. Ignore secrets
touch .gitignore
for p in '.env' '*.pem' '*.key' '*.crt' '*.log' '*.sqlite' '*.db'; do
  grep -qxF "$p" .gitignore || echo "$p" >> .gitignore
done
[[ -f .env ]] && cp -n .env .env.backup 2>/dev/null || true

# 3. Commit any changes
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Sync $(date '+%F %T')"
fi

# 4. Force-sync remote branch to match local exactly
echo "🚀  Pushing to GitHub (${DEFAULT_BRANCH})…"
git push -u "${REMOTE_AUTH}" "${DEFAULT_BRANCH}" --force-with-lease

echo "✅  Done – view at ${REMOTE}"
