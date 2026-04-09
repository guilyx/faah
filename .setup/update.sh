#!/usr/bin/env bash
# Update faah to latest (git pull) and re-run dependency checks.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if [[ ! -d "${ROOT}/.git" ]]; then
  printf 'faah update: not a git checkout: %s\n' "$ROOT" >&2
  exit 1
fi

cd "$ROOT"

if ! command -v git >/dev/null 2>&1; then
  printf 'faah update: git not found on PATH\n' >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  printf 'faah update: working tree is dirty; commit/stash first.\n' >&2
  git status --porcelain >&2 || true
  exit 1
fi

branch=$(git rev-parse --abbrev-ref HEAD)
printf 'faah update: updating %s (%s)\n' "$ROOT" "$branch"

if [[ -f "${ROOT}/VERSION" ]]; then
  printf 'faah update: current version %s\n' "$(head -n1 "${ROOT}/VERSION")"
fi

git fetch --prune origin
git pull --ff-only

if [[ -f "${ROOT}/VERSION" ]]; then
  printf 'faah update: updated version %s\n' "$(head -n1 "${ROOT}/VERSION")"
fi

printf '\nfaah update: running dependency report\n'
"${ROOT}/.setup/install.sh" --check-deps

