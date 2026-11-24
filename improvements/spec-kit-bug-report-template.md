# Bug Report: [SHORT SLUG, e.g. codex-tui-stall]

**Date**: [DATE]

**Reporter**: [who found it]

**Status**: assess / fix / test / closed

**Related run or task**: [e.g. A1 run 92f2ffff, R3-047, or "none, found in probe"]

> This template is the team's bug flow (assess -> fix -> test), adapted from spec-kit's
> bug-fixing process. One bug, one file. The final verdict is `verified`, `partial`,
> or `failed`. Only `verified` confirms a successful fix.

## 1. Symptom

What broke, when it first appeared, and what the user or runner observed. Quote the
exact error text and give the wall-clock time.

- Symptom: [one line]
- First seen: [date + time, Asia/Ho_Chi_Minh]
- Exact error: "[verbatim error]"
- Impact: [what it blocks, e.g. "A1 executors cannot start a TUI session" or
  "R3-047 cannot read gutenberg.org"]

## 2. Reproduction (live)

Exact steps that reproduce the bug, run live, with commands and outputs. A bug that
cannot be reproduced live is recorded as unreproduced, not as fixed.

- Step 1: [command or action]
- Observed: [output, with timing]
- Step 2: [command or action]
- Observed: [output, with timing]
- Reproduced: yes / no / intermittent (how many times out of how many tries)

## 3. Cause assessment

Root cause, with evidence. List what was ruled out and how.

- Root cause: [one paragraph, with the evidence that proves it]
- Evidence: [log excerpt, file, hash, or probe result that pins the cause]
- Ruled out: [each candidate and the evidence that rules it out, e.g.
  "rate limit: the limit was already 100% while sessions worked; `codex exec` used
  tokens at 100% and worked"]
- Honest negative: [what is still unknown, stated plainly, e.g. "the exact blocking
  call inside session_init is not identified"]

## 4. Fix

What changed, where, and in which commit. If the fix is a prompt/brief change rather
than code, quote the changed lines.

- Change: [what changed]
- Files: [paths]
- Commit: [hash, branch]
- Why this fix follows from the cause: [one line]

## 5. Verification (live test)

A live test that proves the fix, run after the fix landed. Record the command, the
timing, and the result. The test must be a realistic task, not a synthetic unit test.

- Test: [what was run, exact command or task]
- Result: [output, timing, exit code]
- Evidence: [log file, screenshot, or evidence dir]
- Verdict: **verified** / **partial** / **failed**
  - `verified`: the original symptom is gone in the live test.
  - `partial`: the symptom is reduced but still appears in some case (name the case).
  - `failed`: the symptom persists; the fix did not work.

## 6. Regression note

What could break because of this fix, and how it was checked.

- Risk: [what might regress]
- Checked by: [test or probe, with result]
- Follow-up: [anything still open, e.g. "upstream fix needed; do not re-test the TUI
  until a release claims a thread-start fix"]

## 7. History

- [DATE] Symptom first seen.
- [DATE] Assessment written.
- [DATE] Fix landed (commit).
- [DATE] Live test, verdict.
