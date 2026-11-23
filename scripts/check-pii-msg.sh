#!/bin/sh
# check-pii-msg.sh - fail-closed check of the commit message.
# Runs as a commit-msg hook: pre-commit passes the commit message file
# as $1. Greps the message for exact known personal values from the
# outside list, and runs gitleaks over the message text for the pattern
# rules (personal email, street address, phone, private IP).
# Requires the gitleaks binary on PATH (pinned v8.30.1, see
# docs/pii-prevention.md). Fail-closed when it or the list is missing.
MSG="$1"
LIST="$HOME/.config/computer-use-wayland/sensitive-values.txt"
if [ -z "$MSG" ] || [ ! -f "$MSG" ]; then
  echo "check-pii-msg: no commit message file given, blocking commit (fail closed)"
  exit 1
fi
if [ ! -f "$LIST" ]; then
  echo "check-pii-msg: sensitive-values list missing, blocking commit (fail closed)"
  echo "check-pii-msg: create it at $LIST (one literal value per line, 0600), then retry"
  exit 1
fi
CLEAN="$(mktemp)"
trap 'rm -f "$CLEAN"' EXIT INT TERM
sed -e 's/\r$//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' "$LIST" | grep -v '^$' > "$CLEAN"
if [ ! -s "$CLEAN" ]; then
  echo "check-pii-msg: sensitive-values list is empty after cleaning, blocking commit (fail closed)"
  exit 1
fi
if grep -F -f "$CLEAN" "$MSG" > /dev/null; then
  echo "check-pii-msg: commit message contains a known personal value"
  exit 1
fi
if ! command -v gitleaks >/dev/null 2>&1; then
  echo "check-pii-msg: gitleaks binary not found on PATH, blocking commit (fail closed)"
  echo "check-pii-msg: install gitleaks v8.30.1 (see docs/pii-prevention.md), then retry"
  exit 1
fi
gitleaks detect --source "$MSG" --no-git --config .gitleaks.toml --redact --ignore-gitleaks-allow --exit-code 1
