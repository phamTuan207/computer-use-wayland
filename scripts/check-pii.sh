#!/bin/sh
# check-pii.sh - fail-closed exact-value check on added lines only.
# The list lives OUTSIDE the repo and is never committed.
# Blank lines and leading/trailing whitespace are stripped from the list
# before grepping: an empty grep pattern matches every line, so a single
# blank line used to block every commit. If the list is empty after
# cleaning, the commit is blocked with a clear message.
LIST="$HOME/.config/computer-use-wayland/sensitive-values.txt"
if [ ! -f "$LIST" ]; then
  echo "check-pii: sensitive-values list missing, blocking commit (fail closed)"
  echo "check-pii: create it at $LIST (one literal value per line, 0600), then retry"
  exit 1
fi
CLEAN="$(mktemp)"
trap 'rm -f "$CLEAN"' EXIT INT TERM
# Trim leading/trailing whitespace (and CR), drop blank lines.
sed -e 's/\r$//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' "$LIST" | grep -v '^$' > "$CLEAN"
if [ ! -s "$CLEAN" ]; then
  echo "check-pii: sensitive-values list is empty after cleaning, blocking commit (fail closed)"
  echo "check-pii: add at least one literal value per line to $LIST, then retry"
  exit 1
fi
if git diff --cached -U0 | grep '^+' | grep -v '^+++' | grep -F -f "$CLEAN" > /dev/null; then
  echo "check-pii: staged diff contains a known personal value"
  exit 1
fi
exit 0
