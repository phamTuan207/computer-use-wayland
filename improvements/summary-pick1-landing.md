# Pick 1 landing summary (Track 2, 19/11)

- Date: 2026-11-19 17:30 +07
- Owner: the owner
- Approval: Pick 1 landing APPROVED by the owner at 17:18, rule: if it is measured better than the old version, land it, do not ask.
- Base: origin/main 21684e7 (docs: add shayxo port execution report).
- Branch: pick1-landing, merged to main with --no-ff. Merge commit is recorded in the campaign live-test-log.
- Relay: NOT restarted. No live broker measurement during landing. Speed-swarm checkout untouched (D1 worker active).

## What Pick 1 is

Code execution as the action. One short allowlisted program per model call replaces the 4 to 5 think calls of the baseline loop (windows, observe, act, verify observe) with one program-writing think call plus a finish confirmation. Behind flag CU_CODE_EXEC=1, default OFF.

## Scope landed (only this)

Cherry-picked from speed-swarm (HEAD a56ce5a), in order:

- 93798ed pick1: code execution as the action, allowlisted interpreter (M1)
- 8ce88b9 pick1: narrow cu.py seam for code-exec (M1), plus the session_driver.py allowlist line from the same commit
- ffa7acc pick1: allow code-exec through the broker envelope (M1)
- 17dcd9f pick1: count only the program lines toward the trace step budget
- 94e9ca3 pick1: tests that API-implementation lines do not count, budget still catches runaways
- d86e88c docs: add Pick 1 P3/P4 program template
- 92f3fbd fix: poll Pick 1 file assertions within budgets
- e4064a4 test: cover Pick 1 P3/P4 template races
- 73bc427 docs: note P3 directory assertions
- 4a01163 docs: record Pick 1 P3/P4 fix results (report file only, see notes)

Files changed vs 21684e7 (8 files, +1375/-2): scripts/code_exec.py (new), scripts/cu.py (seam only), scripts/session_driver.py (1-line allowlist), scripts/session_remote.py (1-line allowlist only), tests/test_code_exec.py (new), tests/test_session_remote.py (+2 envelope tests), improvements/pick1-program-template.md (new), improvements/pick1-p34fix-report.md (new).

## Explicitly NOT landed (stay on speed-swarm)

A1 DOM code-exec (FAILED its success bar), the envelope-validator fix (invalid_arg_type), the actions-JSON fix, the brokerfix diagnostics and preflight retry, Pick 2, Pick 3, Pick 4, masking, CLI-Anything.

## Verification (a): tests, main baseline vs after landing

Run on the laptop in the landing worktree, unittest, Python 3.14.10.

- Main baseline (HEAD 21684e7): test_session_remote 43 tests OK (15.0s). Full suite 1104 tests in 86.4s: 9 failures, 66 errors, 1 skipped.
- After landing: test_code_exec 32 tests OK (10.2s). test_session_remote 45 tests OK (14.6s, 43 baseline + 2 new Pick 1 envelope tests). Full suite 1138 tests in 96.9s: 9 failures, 66 errors, 1 skipped.
- The FAIL/ERROR sets are IDENTICAL (diff of the sorted lists is empty, 75 lines each). Zero new failures. The 9 failures and 66 errors are pre-existing on main (DoctorCliTests run shadowing, FullRestoreEnvelope missing native/wtype in a fresh worktree, wtype/IME environment errors).

## Verification (b): live re-measure holds, from the records (no live re-run)

- Rerun 19/11 04:00-04:17 (report section 3): P1 wall 48.65s to 18.89s (-61%), think 46.81s to 17.38s (-63%), calls 5 to 2. P2 wall 28.16s to 10.18s (-64%), think 26.21s to 8.59s (-67%), calls 5 to 2. Mean P1-P4 wall 37.54s to 17.59s (-53%), think 35.41s to 15.43s (-56%).
- P3/P4 re-measure 19/11 06:06-06:17 (fixed template): 2/2 SUCCESS on retry, P3 wall 20.72s, P4 20.58s (excl. dwell). Attempt 1 of each failed on a preflight screen-changed flake, then the IDENTICAL program passed on retry. Pick 1 overall 4/4 SUCCESS.
- Brokerfix verify 19/11 07:48: P3 attempt-1 SUCCESS wall 25.15s/think 17.16s, P4 attempt-1 SUCCESS wall 19.25s/think 12.48s, 0 retries, 0 refusals, 0 session deaths. P4 file byte-exact (128 B, sha256 a6e58cb9...).
- Honest caveats, kept from the records: the 07:48 attempt-1 success ran with the brokerfix preflight fix also live, which is NOT part of this landing. The preflight retry path was NOT exercised live in that run (no brightness shift occurred), so the retry is proven only by unit and in-process tests. The attempt-1 flake from the 06:06 re-measure is a follow-up, not a landing blocker (report section 1). All verdicts are PROVISIONAL (non-Astra, Astra 6 out of credit).

## Landing notes

- e50da19 (trace-budget fix log line) is log-only, no code. Skipped as a cherry-pick; its substance is the 17dcd9f/94e9ca3 fix already landed. The landing itself is logged in the campaign live-test-log instead.
- 4a01163 touched live-test-log.md (conflicted, main log has diverged) and pick1-p34fix-report.md. Only the report file was landed; the log hunks were dropped (log restored to main version).
- 8ce88b9 conflicted in scripts/cu.py at the a11y parser: main has operations apps/observe/drill/act, speed-swarm had Pick 4 query/ground plus --name/--role/--limit/--address. Resolution kept main a11y line and added only the code-exec parser lines. No Pick 4 code leaked in (grep for query/ground in the cu.py diff is empty).
- scripts/session_remote.py diff vs main is exactly the 1-line COMMANDS allowlist addition. No invalid_arg_type, no diagnostics.
- Desktop check after tests: read-only hyprctl clients, no test terminal left behind, Jarvis and Zen untouched.
