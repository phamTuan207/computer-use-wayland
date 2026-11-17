#!/bin/sh
set -eu

if ! repo_root=$(git rev-parse --show-toplevel 2>/dev/null); then
    printf '%s\n' 'error: not inside a git checkout' >&2
    exit 1
fi
repo_root=$(cd "$repo_root" && pwd -P)
current_dir=$(pwd -P)
if [ "$current_dir" != "$repo_root" ]; then
    printf '%s\n' 'error: run this script from the repository root' >&2
    exit 1
fi

hook="$repo_root/scripts/git-hooks/pre-commit"
if [ ! -f "$hook" ] || [ ! -x "$hook" ]; then
    printf '%s\n' "error: pre-commit hook is missing or not executable: $hook" >&2
    exit 1
fi

git config core.hooksPath scripts/git-hooks
printf '%s\n' 'Installed repository pre-commit hook at scripts/git-hooks/pre-commit'
