# Council Member 3 verdict: Y4d preflight, session hygiene, INFRA abort rule

- Reviewer: Council Member 3 (scope: session hygiene + fail-closed preflight + abort rule only)
- Date: 2026-11-21
- Reviewed: uncommitted working-tree diff of `tests/realistic/run_live.py` and `tests/realistic/run_agyq2.py` (branch `todolist-push`), checked against `improvements/worker-y4b-hidden-body-root-cause.md` (fix design section)
- Verdict: **BLOCK**

Three blocking defects, each proven by reading the code or by a live probe below. The rerun must not start until F1, F2 and F3 are fixed and re-reviewed. F4 to F9 are also required before the rerun; none of them is optional, but none of them alone would stop the run the way F1 does.

## 1. WD orphan fix (run_live.py)

### What passes

- Status endpoint timeout: the `while/else` at lines 203-214 calls `self._cleanup()` in the `else` branch and then raises. Pass.
- Session POST failure: lines 215-223 wrap the POST in `try/except`, call `self._cleanup()`, re-raise. Pass.
- PID file is written before any failure can occur in the covered paths: line 202 (`Path(...).write_text(str(self.proc.pid))`) runs immediately after `Popen` (lines 197-201), before the status loop and the session POST. Pass.
- `_cleanup` (lines 235-270) removes the PID file and closes the log on all paths that reach it, including when called from the `__enter__` else-branch. The log close (lines 259-264) and the PID unlink (lines 265-270) are each guarded by a `None` check and set to `None` after, so a double `_cleanup` closes the handle exactly once and unlinks exactly once. Pass.
- Teardown order in `_cleanup` is correct: session delete and proc terminate/wait (lines 236-258) happen before the log close, so no write races the close. Pass.
- Sequential second `WD()` on the same port is safe in the narrow sense: the PID file is overwritten with the new pid and unlinked at cleanup, so no stale PID confusion. See F6 for the evidence problem.

### What fails

- F4a: if `Path.write_text` at line 202 raises (disk full, `/tmp` read-only), the proc is already started and the exception propagates out of `__enter__` with no cleanup. The result is an orphaned geckodriver with NO PID file, so the preflight sweep can never find it. This is the exact orphan the fix was written to kill.
- F4b: `self.session = resp["value"]["sessionId"]` at line 224 sits OUTSIDE the session POST `try` block. A malformed session response (missing `value` or `sessionId`) raises `KeyError` with no cleanup: orphaned proc, PID file left behind (sweepable, but still an orphan).
- F5a: if `Popen` itself raises (missing geckodriver binary), the log handle opened at line 196 is never closed. Small leak, but it is a failure path with no cleanup.
- F5b: `_cleanup` is not exception-proof. `self.proc.terminate()` at line 253 is not inside a `try`; if it raises (proc died between `poll()` and `terminate()`), `_cleanup` aborts before the log close and PID unlink, leaving a stale PID file and an open handle. Every caller of `_cleanup` assumes it cannot raise.
- F6: the log is opened `"wb"` at line 196, so every new `WD()` (one per test in `run_agyq2.py` main) truncates the previous session's geckodriver log. If a test fails and the next test starts, the failing session's evidence is destroyed before anyone reads it. Use append mode or a per-session log.

## 2. Preflight fail-closed (run_agyq2.py, lines 1097-1213)

Preflight runs before `bootstrap_tab` (main, lines 1224-1231), so nothing opens a tab before it passes. That ordering is correct.

### (a) Owner-away: pass

Line 1109: `if os.environ.get("LIVE_OWNER_AWAY") != "1": raise RuntimeError(...)`. Explicit env only. A grep for `LIVE_OWNER_AWAY` across the repo finds no other reference and no inference path (no idle check, no silence check, no Hyprland-error check) anywhere in the runner. Pass, with one minor gap: the fix design (`improvements/worker-y4b-council-fix.md:73`) requires the log to record that idle time was NOT independently verified when no idle source is available. The implementation logs nothing of the kind. See F9.

### (b) Zen liveness: pass, with a noted limit

- BiDi 9222, lines 1113-1122: `urlopen("http://127.0.0.1:9222/json/version", timeout=5)`, non-200 raises inside the `try` and is re-raised as `PREFLIGHT`. Fail closed. Timeout 5 s is sane.
- Marionette 2828, lines 1121-1128: `socket.create_connection(("127.0.0.1", 2828), timeout=5)`, any exception re-raised as `PREFLIGHT`. Fail closed. Timeout 5 s is sane.
- No warn-and-continue anywhere in this function. Pass.
- Limit (not a required fix): a TCP connect proves the port listens, not that Marionette answers protocol. A wedged-but-listening Marionette passes this check. Accepted for this rerun; the session POST in `WD.__enter__` is the real protocol probe.

### (c) Fixture server loopback: pass

Lines 1128-1138 check `base + "/agy-q2/fixtures/test-01-whiteboard.html"` with timeout 5 and require status 200. `base` comes from `start_server()` (`run_live.py:479-496`), which returns `http://127.0.0.1:{SERVER_PORT}`, so this is a true loopback check of the exact fixture file the tests use. Pass.

### (d) Stale-geckodriver sweep: one BLOCK, one required fix, minors

- Orphan test as written is correct for the cases it can see: lines 1152-1157 read ppid from `/proc/<pid>/stat`, treat ppid 1 (reparented to init) as orphan and kill, treat a live parent (`ppid != 1` and `/proc/<ppid>` exists) as live and raise `PREFLIGHT`. A zombie parent still exists in `/proc`, so it refuses, which is the conservative direction. Pass.
- F3 (BLOCK): when `/proc/<pid>/stat` is unreadable, ppid is `None` (lines 1152-1154), `parent_alive` is `False` (lines 1155-1156), and execution falls through to the kill branch (lines 1164-1167). That kills on unknown parentage, which is the UNSAFE direction for live-driver protection. The likely cause is an exit race (pid died between the `kill(pid, 0)` check and the stat read), in which case the SIGTERM raises `ProcessLookupError` and is harmless. But if stat is unreadable for any other reason, this SIGTERMs then SIGKILLs a process whose orphan status was never verified. Fix: on ppid `None`, re-check liveness; if still alive, raise `PREFLIGHT` (refuse); if dead, unlink the PID file and continue.
- Garbage PID file (lines 1140-1146): `int(...)` raises, the code does `continue` silently and leaves the file in place forever. Safe for killing (it kills nothing unknown) but silent and permanently littering. Fix: unlink the unreadable file and log it. See F8.
- Kill sequence (lines 1164-1170): SIGTERM, sleep 1, `kill(pid, 0)` probe, SIGKILL if still alive, `ProcessLookupError` treated as dead. Correct. Minor gap: after SIGKILL there is no confirmation the process actually died before the PID file is unlinked. SIGKILL is reliable, so this is a note, not a fix.
- `PermissionError` on `kill(pid, 0)` (lines 1147-1151) is treated as "not alive" and the PID file is unlinked. A live foreign-owned driver would lose its only PID record. Unlikely in practice (runner and driver run as the same user); note only.
- `/proc/<pid>/stat` ppid parsing via `.split()[3]` (line 1152) breaks if the comm field (field 2, in parentheses) contains spaces, shifting every index. Geckodriver's comm has no spaces in practice. Fix with the robust parse (after the last `)`). See F7.

### (e) Lock check via /proc/locks: BLOCK

- Field indices are correct. Real `/proc/locks` format, verified live on this machine: `1: FLOCK  ADVISORY  WRITE 14729 00:58:31615 0 EOF`, so `parts[4]` is the pid and `parts[5]` is `dev:inode` (line 1192 `rsplit(":", 1)[1]` and line 1196 `int(parts[4])` are right).
- F1 (BLOCK): line 1189 requires `parts[1] == "POSIX"`. Locks taken by `flock(2)` appear in `/proc/locks` as type `FLOCK`, not `POSIX`. The documented launch is the `flock` CLI (`improvements/worker-y4-run-log.md:49`: `flock -w 1800 ~/.cache/agent-computer-use/zen_dom.lock -c "python3 run_agyq2.py ..."`). Proven live on this machine with a real `fcntl.flock` exclusive hold: the code-as-written POSIX-only filter returns holders `[]`, while a FLOCK-aware filter returns `[15122]` (the holder pid). Consequence: preflight raises "no flock holder on zen_dom.lock" on EVERY correctly launched run. As written, preflight can never pass under its own documented launch method. Fix: accept `parts[1] in ("POSIX", "FLOCK", "OFDLCK")`.
- Ancestor walk (lines 1199-1204): `while pid > 1`, read ppid, add to set, `break` on error. It terminates: pids strictly decrease toward 1, and any read failure breaks. The no-holder and wrong-holder branches (lines 1205-1213) both raise, so a run NOT launched under flock fails closed. Pass, with two notes: the same `.split()[3]` fragility as (d) (line 1201, arbitrary ancestor comms), and the set excludes the process itself, so if the runner ever held the lock directly (`os.getpid()` as holder) it would falsely refuse. Include `os.getpid()` in the set. See F7.
- Lock file missing (lines 1177-1181) and `/proc/locks` unreadable (lines 1183-1186) both raise. Fail closed. Pass.

## 3. INFRA abort rule (run_agyq2.py main, lines 1260-1286)

- F2 (BLOCK): `infra_blocked` is NOT reset on a pass. It is only touched inside the `except` branch (lines 1267-1272): incremented on `"INFRA:"`, reset to 0 on a non-INFRA failure. A passing test never touches it. Sequence INFRA-fail, PASS, INFRA-fail therefore increments to 2 and aborts, even though the two INFRA failures were NOT consecutive tests. That contradicts the design ("two consecutive infra-blocked tests abort the suite") and can abort a healthy run. Fix: reset `infra_blocked = 0` on the success path (a `try/else` on the `TESTS[tid]` call, or an explicit reset after the `try` when no exception fired). Same hole on the session-creation-failure path, which `continue`s (lines 1240-1258) without resetting `infra_blocked`: INFRA-fail, session-fail, INFRA-fail would also abort. Reset there too.
- `"INFRA:"` is matched on the right string: line 1267 tests `"INFRA:" in str(exc)`, the raw exception message from `open_fixture` (`"INFRA: hidden-body ..."`, lines 305-310), NOT the `"runner: ..."` wrapper, which is appended to `r.failures` after the match (line 1265). Pass. Optional tightening: use `startswith("INFRA:")` instead of substring, so a message that merely mentions INFRA cannot false-positive.
- Abort breaks AFTER appending the second failing summary: lines 1275-1286 append the summary to `results` and print it, THEN check `abort_infra` and `break`. The report is complete and the suite totals include both failures. Pass.

## 4. Hyprland IPC omission: agree as a detector, add as a safety gate

I agree with the omission AS AN INCIDENT DETECTOR. The root-cause paper is explicit: the wedge is an unproven correlate, wrong layer for a CSS value, persists through the clear, absent from incident 1. It must never be labeled an incident detector. The implementation is right to leave it out in that role.

But the same paper allows it "at most as a fail-closed safety gate, labeled as one" (root-cause paper, fix design section). The incident 2 record shows why that gate matters: the physical keyboard and mouse stopped responding for about 1 minute during probe tab navigation. No other preflight check covers compositor input delivery: BiDi and Marionette listening does not prove Hyprland will deliver focus and input correctly. Add a timeout-guarded Hyprland IPC liveness check (for example `hyprctl version` via subprocess with a 10 s timeout, never a bare call, since the wedge symptom IS `hyprctl` hanging), labeled SAFETY in the log and in the error message, failing closed on timeout or error. See F9.

## Required fixes (exact)

- F1 (BLOCK, run_agyq2.py:1189): change the `/proc/locks` type filter from `parts[1] != "POSIX"` to `parts[1] not in ("POSIX", "FLOCK", "OFDLCK")`. Re-prove with a live `flock` hold before the rerun: the check must find the holder.
- F2 (BLOCK, run_agyq2.py:1260-1283): reset `infra_blocked = 0` on a passing test (try/else) and on the session-creation-failure `continue` path, so only two INFRA failures with no intervening pass or session failure abort.
- F3 (BLOCK, run_agyq2.py:1152-1162): when ppid is `None` (stat unreadable), re-check liveness; if the pid is still alive, raise `PREFLIGHT` and refuse; only unlink and continue when it is actually dead. Never kill on unknown parentage.
- F4 (run_live.py:191-225): wrap everything after `Popen` in `__enter__` in one try/except with `_cleanup()` on any exception, covering the PID `write_text` (line 202) and the `sessionId` extraction (line 224), or move line 224 inside the existing session POST try block.
- F5 (run_live.py:196, 235-270): make `_cleanup` exception-proof by wrapping the proc teardown so a `terminate()` raise cannot skip the log close and PID unlink; close the log handle if `Popen` raises.
- F6 (run_live.py:196): open the geckodriver log in append mode (`"ab"`) or use a per-session log, so each test's `WD()` does not truncate the previous session's evidence.
- F7 (run_agyq2.py:1152, 1201): parse ppid from `/proc/<pid>/stat` after the last `)` instead of `.split()[3]`; add `os.getpid()` to the ancestor set.
- F8 (run_agyq2.py:1140-1146): on an unreadable (garbage) PID file, unlink it and log the fact instead of silently continuing.
- F9 (run_agyq2.py preflight): add a timeout-guarded Hyprland IPC liveness check as a labeled SAFETY gate (fail closed, 10 s timeout, never a bare `hyprctl` call), and log that idle time was not independently verified (fix design, council-fix.md:73).

## Out of scope (not judged here)

`diagnose_body`, the `ensure_visible` recovery ladder, `rebootstrap_tab`, `bootstrap_tab` verification, and the flagged-pass accounting belong to other council members. This verdict covers only session hygiene, fail-closed preflight, and the abort rule. Nothing in this file judges whether the diagnose-first design itself is correct.
