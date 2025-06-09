#!/usr/bin/env bash
#   Sube TODO el contenido del directorio actual a angietd94/mbo-tracker (rama main)

set -euo pipefail
IFS=$'\n\t'

#####################################################
# CONFIGURACIÓN (edita una sola vez)
#####################################################
GITHUB_USERNAME="angietd94"
REPO_NAME="mbo-tracker"
BRANCH="main"
AUTHOR_NAME="Angelica Tacca"
AUTHOR_EMAIL="angelicataccadughetti@gmail.com"
#####################################################

# 1. Carpeta de trabajo = donde estés parado
WORK_DIR=$(pwd)

# 2. Token
: "${GITHUB_TOKEN:=$(read -rsp 'GitHub Personal Access Token: ' _tok && echo $_tok && echo)}"

REMOTE="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
REMOTE_AUTH="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

cd "$WORK_DIR"

# 3. Inicializar repo si hace falta
if [[ ! -d .git ]]; then
  git init
  git switch -c "$BRANCH"
  git config user.name  "$AUTHOR_NAME"
  git config user.email "$AUTHOR_EMAIL"
  git remote add origin "$REMOTE"
fi

# 4. Sincronizar con remoto (si existe)
git fetch --prune origin "$BRANCH" 2>/dev/null || true
git pull --rebase --autostash origin "$BRANCH" 2>/dev/null || true

# 5. Añadir absolutamente todo y commitear
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Sync $(date '+%F %T')"
else
  echo "• No hay cambios nuevos."
fi

# 6. Push
echo "🚀  Subiendo a GitHub ($BRANCH)…"
git push --follow-tags --set-upstream "$REMOTE_AUTH" "$BRANCH"

echo "✅  Listo – revisa $REMOTE/tree/$BRANCH"
