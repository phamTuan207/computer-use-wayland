#!/bin/sh
# check-pre-push.sh - fail-closed scan of the pushed range.
# Runs as a pre-push hook and scans the pushed commits with gitleaks plus
# the exact-values grep over the pushed diff. This is the second local
# net: it catches commits made with --no-verify or made before the
# pre-commit hook was installed. Like every local hook it is skippable,
# so CI remains the enforcement layer.
# Requires the gitleaks binary on PATH (pinned v8.30.1, see
# docs/pii-prevention.md). Fail-closed when it is missing.
#
# How the pushed range is found: pre-commit does NOT forward the pre-push
# stdin lines to hooks (it parses them itself), so this script reads the
# range from the PRE_COMMIT_FROM_REF / PRE_COMMIT_TO_REF environment
# variables pre-commit sets for pre-push hooks. Fallbacks, in order:
# pre-push stdin lines (plain git-hook invocation), then the commits in
# HEAD that are not on any remote-tracking branch.
LIST="$HOME/.config/computer-use-wayland/sensitive-values.txt"
ZERO="0000000000000000000000000000000000000000"
EMPTY_TREE="4b825dc642cb6eb9a060e54bf8d69288fbee4904"

if [ ! -f "$LIST" ]; then
  echo "check-pre-push: sensitive-values list missing, blocking push (fail closed)"
  echo "check-pre-push: create it at $LIST (one literal value per line, 0600), then retry"
  exit 1
fi
CLEAN="$(mktemp)"
trap 'rm -f "$CLEAN"' EXIT INT TERM
sed -e 's/\r$//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' "$LIST" | grep -v '^$' > "$CLEAN"
if [ ! -s "$CLEAN" ]; then
  echo "check-pre-push: sensitive-values list is empty after cleaning, blocking push (fail closed)"
  exit 1
fi
if ! command -v gitleaks >/dev/null 2>&1; then
  echo "check-pre-push: gitleaks binary not found on PATH, blocking push (fail closed)"
  echo "check-pre-push: install gitleaks v8.30.1 (see docs/pii-prevention.md), then retry"
  exit 1
fi

STATUS=0
# Scan one pushed range: gitleaks over the commits plus the exact-values
# grep over the diff. $1 is the log-opts value, $2 and $3 are the diff ends.
scan() {
  _log_opts="$1"; _from="$2"; _to="$3"; _label="$4"
  if ! gitleaks git . --config .gitleaks.toml --redact --ignore-gitleaks-allow --log-opts="$_log_opts" --exit-code 1; then
    echo "check-pre-push: gitleaks found a finding in pushed range $_label"
    STATUS=1
  fi
  if git diff "$_from" "$_to" | grep '^+' | grep -v '^+++' | grep -F -f "$CLEAN" > /dev/null; then
    echo "check-pre-push: pushed diff contains a known personal value (range $_label)"
    STATUS=1
  fi
}

# Scan exactly a set of commits (first push, no common base): --no-walk
# keeps git log from following ancestors into the whole history, which
# carries historical findings. $1 is the space-separated commit list.
scan_no_walk() {
  _pushed="$1"
  [ -n "$_pushed" ] || return 0
  _newest="$(printf '%s' "$_pushed" | awk '{print $1}')"
  _oldest="$(printf '%s' "$_pushed" | awk '{print $NF}')"
  _from="$(git rev-parse "$_oldest^" 2>/dev/null || printf '%s' "$EMPTY_TREE")"
  scan "--no-walk $_pushed" "$_from" "$_newest" "$_oldest..$_newest (first push)"
}

SCANNED=0
if [ -n "$PRE_COMMIT_FROM_REF" ] && [ -n "$PRE_COMMIT_TO_REF" ]; then
  scan "$PRE_COMMIT_FROM_REF..$PRE_COMMIT_TO_REF" "$PRE_COMMIT_FROM_REF" "$PRE_COMMIT_TO_REF" "$PRE_COMMIT_FROM_REF..$PRE_COMMIT_TO_REF"
  SCANNED=1
elif [ ! -t 0 ]; then
  while read -r _local_ref local_sha _remote_ref remote_sha; do
    [ -n "$local_sha" ] || continue
    SCANNED=1
    if [ "$remote_sha" = "$ZERO" ]; then
      BASE="$(git merge-base HEAD origin/main 2>/dev/null || true)"
      if [ -n "$BASE" ]; then
        scan "$BASE..$local_sha" "$BASE" "$local_sha" "$BASE..$local_sha"
      else
        scan_no_walk "$(git rev-list "$local_sha" --not --remotes 2>/dev/null | tr '\n' ' ')"
      fi
    else
      scan "$remote_sha..$local_sha" "$remote_sha" "$local_sha" "$remote_sha..$local_sha"
    fi
  done
fi
if [ "$SCANNED" = "0" ]; then
  # No range from pre-commit or stdin (for example a first push where
  # pre-commit reports all-files): scan the commits not on any remote.
  scan_no_walk "$(git rev-list HEAD --not --remotes 2>/dev/null | tr '\n' ' ')"
fi

exit "$STATUS"
