#!/usr/bin/env bash
#   Sync this folder to GitHub (angietd94/mbo-tracker) in a safe, repeatable way
#   ▸ If the remote moved ahead, we rebase; if histories diverged we stop & tell you.

set -euo pipefail
IFS=$'\n\t'

########################################
# USER SETTINGS – change once
########################################
GITHUB_USERNAME="angietd94"
REPO_NAME="mbo-tracker"
DEFAULT_BRANCH="main"             # or 'master'
AUTHOR_NAME="Angelica Tacca"
AUTHOR_EMAIL="angelicataccadughetti@gmail.com"
########################################

# 0. Personal-access token
: "${GITHUB_TOKEN:=$(read -rsp 'GitHub Personal Access Token: ' _tok && echo $_tok && echo)}"

REMOTE="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
REMOTE_AUTH="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

# 1. Init repo on first run
if [[ ! -d .git ]]; then
  git init
  git switch -c "${DEFAULT_BRANCH}"
  git config user.name  "${AUTHOR_NAME}"
  git config user.email "${AUTHOR_EMAIL}"
  git remote add origin "${REMOTE}"
fi

# 2. Fetch latest remote state
git fetch --prune origin "${DEFAULT_BRANCH}" || true   # tolerate empty remote

# 3. Fast-forward or rebase if needed
if git show-ref --verify --quiet "refs/remotes/origin/${DEFAULT_BRANCH}"; then
  LOCAL=$(git rev-parse "${DEFAULT_BRANCH}")
  REMOTEHEAD=$(git rev-parse "origin/${DEFAULT_BRANCH}")
  BASE=$(git merge-base "${DEFAULT_BRANCH}" "origin/${DEFAULT_BRANCH}")

  if [[ "$LOCAL" = "$REMOTEHEAD" ]]; then
    echo "✓ Local branch already up to date."
  elif [[ "$LOCAL" = "$BASE" ]]; then
    echo "↻ Remote is ahead — pulling..."
    git pull --rebase --autostash origin "${DEFAULT_BRANCH}"
  elif [[ "$REMOTEHEAD" = "$BASE" ]]; then
    echo "⟳ Local is ahead — will push after committing."
  else
    echo "⚠️  Local and remote have diverged."
    echo "    Please resolve manually (merge or rebase) and re-run the script."
    exit 1
  fi
fi

# 4. Ignore common secret files
touch .gitignore
for p in '.env' '*.pem' '*.key' '*.crt' '*.log' '*.sqlite' '*.db'; do
  grep -qxF "$p" .gitignore || echo "$p" >> .gitignore
done
[[ -f .env ]] && cp -n .env .env.backup 2>/dev/null || true

# 5. Stage & commit anything new
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Sync $(date '+%F %T')"
else
  echo "• Nothing to commit."
fi

# 6. Push (fast-forward) to remote
echo "🚀  Pushing to GitHub (${DEFAULT_BRANCH})…"
git push "${REMOTE_AUTH}" "${DEFAULT_BRANCH}"  \
        --follow-tags --set-upstream

echo "✅  Done – see ${REMOTE}"
