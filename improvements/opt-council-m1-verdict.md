# Council OPT-M1 VERDICT: one optimal fix method per class
# Council OPT-M1 (3 voices: mechanism, evidence, safety). Written to be attacked
# by redteam. Every claim carries file:line or a runnable-evidence citation.
# Sources: error file LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md, todolist
# docs/zen-error-fix-todolist-20261121.md, F1/F2/VMFIX logs, repo code read here.
# OPT-SRC crawl file did not exist at council start (22:50 +07); no OPT-SRC
# position to agree or disagree with yet. Gap recorded. No em/en dashes.

## How this verdict was reached
Three voices debated from primary sources. Voice 1 (mechanism) traced each class
to exact failing points in code. Voice 2 (evidence) set the proof bar and named
one falsifier per candidate method. Voice 3 (safety) vetoed every move whose worst
failure is unbounded while the owner sleeps. A method survived only if all three
voices agreed: the mechanism is exact, the proof is measurable, and the worst
failure is bounded. Full papers: improvements/opt-council-m1-mechanism.md,
opt-council-m1-evidence.md, opt-council-m1-safety.md. Council log:
improvements/worker-opt-council-m1-log.md.

## CLASS A: session/guardian startup failure
## Verdict: repair the drift, guard the reply, name the cause, activate only under
## preconditions 1-8, and make the repair durable. Exactly one method, 8 steps.

### A step 1. Verify the A5 correction on the laptop repo (5 minutes, read-only)
Run `git show d27ad0a:native/hyprglass-local-optics.lua | sha256sum` on the
laptop repo and compare with the old pin 674441ea. If it matches, correct the F1
log Layer 4 line to the two-stale-commits story (optics from 09a8df7, manifest
pin from d27ad0a, both stale against b2afcd1). If it does not match, the pin
origin stays unexplained and is recorded as such. Gate: the log correction (or
the unexplained verdict) is committed before step 2. File: laptop repo only,
no VM change. Falsifier: none, this is a fact check, not a fix.

### A step 2. Fix the remaining code gaps in the diagnostic path (VM, tests first)
Files: scripts/cursor_theme.py guard_reply (lines 99-113) and
scripts/cursor_session.py supervise (lines 210-260).
- A1: drain settle. Wait for guardian exit plus join the drain thread before
  reading guard_errors (council 1 A1, redteam R6).
- A2: name the cause on driver registration failure too (line 260), with the
  same drained tail (council 1 A2, redteam R8).
- A3: catch UnicodeDecodeError alongside JSONDecodeError in guard_reply, and
  use errors='replace' on the drain pipe (council 1 A3, redteam R5).
- A4: distinguish truncated JSON from a missing backend in guard_reply; a
  truncated reply must not prescribe the activation remedy (redteam R4).
- A5: larger deque/tail so the root cause cannot be pushed out by cleanup lines
  (redteam R7).
- A6: redact 32-hex tokens in the supervise tail and guard_reply echo (redteam
  R11).
- A7: exact-envelope assertion in the Lifecycle test: assert the string
  'session guardian startup failed: cursor guard reply is not valid JSON' in
  stdout, not just that the text appears via the tee (council 1 A4).
Tests: extend tests/test_cursor_theme.py and tests/test_cursor_session.py. Run
the VM suite; note that test_cursor_session.py does not compile on VM Python
3.12 (pre-existing SyntaxError, line 570), so session tests run on the laptop
(Python 3.14.10) and are labeled laptop-only. Generator (F1) writes code and
tests; an independent checker runs them; F1 never judges its own tests.
Gate: VM theme tests green plus laptop session tests green, committed in small
pieces, each pushed at once.

### A step 3. Durability: a re-pin check in sync-installed/setup (VM + laptop)
The drift repair (F1 plan A, done 22:37) is an uncommitted change on gitignored
files in a repo at detached HEAD 56f5af4. Any checkout, reset, clean, or fresh
clone wipes it (redteam R2). Add a check, run by sync-installed.py and setup,
that compares the installed manifest profile_sha256 and library pins against
the repo optics file sha256 and fails LOUDLY on mismatch, naming both values
and the refresh command (scripts/refresh-visuals-manifest.py). Also add a
login-time loader-failure detector: the next login must surface a loader
failure instead of failing silently to /dev/null (redteam R1; the 30s
single-shot gate, R10, gets a retry or a loud report of a missed window).
Gate: the check fails on a deliberately drifted fixture and passes on the
repaired state, in a test. This step is what makes step 4 durable; without it
the next optics change repeats the exact incident.

### A step 4. Live activation, only under F1 council 2 preconditions 1-8, in order
Preconditions (LOG, improvements/worker-f1-council-2.md): 1. sequence after F3
sign-off, Zen PID stable, single operator, no parallel driving. 2. same-minute
pre-flight: ABI match, plugin list exactly hyprbars 1.0, configerrors empty, no
session/token/socket dir, .so shas match filenames and manifest, ldd 0 not
found on both. 3. run the INSTALLED-tree activation scripts, glass then guard,
abi from the manifest, profile-sha256 9a151634, no other step between them.
4. hold owner_lock across the whole glass plus guard sequence (build the
lock-holding wrapper FIRST, because activate-glass.py takes no lock today).
5. half-state recovery agreed in advance: never re-run activate-glass after a
partial success, guard-only retry, longer wait for slow shaders, re-query the
plugin list before any retry, never blind retry a load. 6. corrected proof:
fresh observe first, one click at the center of the already-active tab only,
skip the click if the active tab is the whiteboard or has unsaved state,
workspace/menu moves by command only, verify via cursorpos plus a second fresh
observe, clean stop and clean desktop check. 7. crash contingency: if the
compositor dies or the desktop freezes, stop, report to the parent at once,
relaunch nothing blindly. 8. durability follow-up tracked (this verdict step 3).
Files run: scripts/activate-glass.py then scripts/activate-cursor-guard.py
(installed tree). Safety vetoes V1-V4 apply: no other live load, no parallel
driver, no bar clicks, no driving if the owner is at the keyboard.

### A step 5. Proof of restoration (live, same window as step 4)
All of it: plugin list shows hyprglass + computer-use-cursor + hyprbars;
`hyprctl cu-cursor status` returns JSON; socket exists; a session starts and
prints `ready`; the pill appears in a fresh observe; one planned click lands,
verified by cursorpos plus a second fresh observe; clean stop, pill gone,
desktop clean. Also prove the loader: run visuals.py mid-session, it must fail
at fresh_login_gate, NOT at manifest_validation.
Falsifier: after a correct glass-then-guard load with green pre-flight, the
session still dies, or `cu-cursor status` still answers `unknown request`, or
the pill never appears. Any one kills the "only unloaded plugins" claim and
sends the investigation back to the guardian code.

### A step 6. Gate the session on hyprglass active (redteam R3)
File: scripts/cursor_session.py guardian path (and/or publish the require-liquid
marker in the installed tree). A session must refuse to start, with a named
error, when glass is paused or crashed, instead of starting pill-less. The gate
must distinguish "glass not loaded" from "glass loading" (shader warm-up
window, F1 council 2 F9), and the refusal must name the state and the remedy.
This step needs its own council + redteam before it lands, because a too-strict
gate breaks working sessions. It is part of the class A method, not a separate
fix, because without it class C1 returns through a second door.
Falsifier: a session completes actions with no pill in a fresh observe.

### A step 7. Track the recurrence (council 1 A6)
Open a tracked follow-up: the next optics change must re-pin both manifests
(installed AND laptop repo) via scripts/refresh-visuals-manifest.py, and the
step 3 check must run in CI or pre-commit. Until that lands, the root cause is
not durably fixed and class A is not declared complete, even if step 5 passes.

### A step 8. Commit discipline for class A
Each sub-step above is its own commit, pushed at once (see the COMMIT METHOD
section below). No batching. The live activation (step 4) is one commit for the
lock wrapper plus one commit for the log of the activation itself, each pushed
immediately after the step completes.

## CLASS B: silence / slow first action
## Verdict: make act-now the DEFAULT path, overlay first, 20s session deadline,
## fallback only on session-start failure, <30s order-to-first-visible-action.
## Exactly one method, 7 steps.

### B step 1. Wire act-now as the default command path (VM, code already exists)
Files: scripts/first_action.py (F2, new) and scripts/cu.py (act-now subcommand).
The default entry for any pointer action becomes: overlay acquire first, then
session attempt with a hard 20s deadline, then actions. The old path (observe,
then session with a 15s supervise wait, then act, with require_session at
scripts/cu.py lines 2599-2602 refusing everything without a session) stays
available only as an explicit fallback flag, never as the default. No agent
brief, prompt, or runbook may invoke the old path without naming why. The
Lauren Tan rule applies: a repeated mistake becomes a deterministic rule, never
a reminder. Speed is structural, not a decision.
Gate: `computer-use act-now --help` works on the VM and on the laptop, and the
old `act` path prints a pointer to act-now in its refusal text.

### B step 2. Enforce the overlay gate in code on both paths
File: scripts/first_action.py acquire_overlay (lines 68-90). Overlay acquire is
a PRECONDITION of any pointer action, session path and direct Pointer path
alike. If the overlay cannot be shown, the run REFUSES loudly with a clear
error and executes nothing. Never act invisibly (safety veto V5). The pill must
be verified VISIBLE in a fresh observe before the first click, not just by the
acquire reply, because an acquire reply alone does not prove a visible pill
(F2 log 22:25: holders.json can be empty with no daemon running).
Gate: a test where the overlay acquire fails and the run refuses with zero
pointer movement (extend tests/test_first_action.py; the 21 existing tests
already cover the acquire-fail refusal on the VM).

### B step 3. Bound the session attempt and define the fallback exactly
File: scripts/first_action.py attempt_session (lines 112-124, process-group kill
on timeout) and is_session_start_failure (lines 153-176). The session attempt
has a hard 20s deadline. On a session-START failure only (guardian never ready,
guardian error named, timeout with no live session), fall back to the same
desktop_act the session path uses, with the overlay already on, and log the
bypass with the guardian error, the deadline, and the path taken. On ANY other
failure (act refusal, screen-change refusal, timeout with a live session), do
NOT fall back; the actions may have partially run and must never be replayed
blind (safety veto V6). After each click, verify pointer position within 3px.
Release the overlay at the end. Return the JSON envelope: path taken, timings
(order -> overlay-on, order -> first move, order -> first click), pill_shown
flag, bypass reason if any. Append the JSONL timing log.
Gate: VM tests green (21/21 already) plus one new test per fallback predicate
branch. The 20s constant is a chosen value, not a measured one; step 6 measures
whether it is right.

### B step 4. Rehearse on a harmless composite task set by an independent agent
The rehearsal task is COMBINED (DOM + CLI + mouse + keyboard in one task) and
set by an independent agent who does not know the implementation (owner test
rule 22:23; ZT-A scenarios or a fresh setter). It runs AFTER F3 sign-off on Zen
restore and AFTER class A step 5 proves a session can start, because the
rehearsal measures the fast path, not the broken session. The task is harmless
by design: open a new tab, navigate to example.com, close only that tab. Never
rehearse on a real Polygon page, a real contest, or any page with unsaved state.
At most one planned pointer click, on the already-active tab only, never on the
bar (owner 22:45). Safety vetoes V3, V4, V7 apply: stop at once if human input
is observed; commands only for workspace/menu; touch no owner tab or session.
Gate: rehearsal runs only when G-F1-BEFORE-F2 is green (todolist gate: measure
F2 only when F1 is green).

### B step 5. Measure and publish the timings
Recorded for the rehearsal: order timestamp, overlay-on timestamp, first move
timestamp, first click timestamp, the JSON envelope, the JSONL timing log entry,
and a fresh observe showing the pill plus the landed click. Targets: order to
first visible action under 30s (owner 22:21); no gap over 60s between visible
actions while the task runs. Publish the numbers in the F2 log, not in chat
only. No narration before each step (owner 22:21 correction); the overlay itself
reports progress, and the pill label must track the step (evidence paper B
candidate 3, unmeasured until the rehearsal shows it).
Falsifier: order-to-first-visible-action over 30s with the overlay on, or a pill
absent from the after-capture, or a fallback that replays an act failure. Any
one kills "act-now is fast enough" or "act-now is safe" and forces a re-measure
of the bottleneck (observe capture, agent think, session deadline) before any
further claim.

### B step 6. Re-set the constants from the measured distribution
After the rehearsal, set the session deadline and the 30s target from measured
numbers, not from guesses. If successful session starts cluster above 20s, the
deadline converts successes into fallbacks and must move. If the rehearsal lands
well under 30s, the next target comes from the measured distribution. If a floor
above 30s appears that no path beats (observe capture + agent think alone exceed
30s on a cold start), the target is wrong and must be re-set from the measured
floor, not defended. Think time (H2) is instrumented in this run (G-H2); until
an agent-driven run measures it, no claim about think time as the bottleneck is
made for class B.
Gate: one commit with the measured distribution and the re-set constants, pushed
at once.

### B step 7. Commit discipline for class B
Each sub-step above is its own commit, pushed at once (see the COMMIT METHOD
section below). The rehearsal log entry is its own commit, pushed immediately
after the run, never batched at the end of the day.

## CLASS C: overlay never shows / flicker
## Verdict: two phenomena, two methods. C1 (never shows) is fixed by the class A
## spine plus a hyprglass gate plus a watchdog proof. C2 (flicker) is measured
## ONLY in the nested Hyprland, never on the live compositor. Exactly one method
## per phenomenon, 5 steps for C1, 4 steps for C2.

### C1 step 1. Fix the session spine first (class A steps 1-5)
Most C1 cases are class A: the session is dead, so the pill is never created
(I12: worker alive, broker and relay running, overlay gone). No separate C1 fix
is attempted until class A step 5 passes. A C1 report after class A is green
points at the second mechanism below, not at the guardian.

### C1 step 2. Gate the session on hyprglass active (class A step 6, repeated here
### because it is the C1 fix)
A paused or crashed glass plus a loaded guard starts a session with no pill
(redteam R3). Implement the gate in scripts/cursor_session.py (or publish the
require-liquid marker in the installed tree), with the warm-up distinction from
class A step 6, under its own council + redteam before landing.
Falsifier: a session completes actions with no pill in a fresh observe.

### C1 step 3. Live-proof the watchdog respawn (todolist 2.2.4, proof still owed)
Unit tests pass (test_daemon_respawns_dead_native,
test_daemon_keeps_live_native). The live proof: kill the indicator ONCE during
a hold, show the pill returns in a fresh observe, with timestamps. If it
respawns more than once or spawns a duplicate pill, stop and log; never let a
respawn loop run unattended overnight. File: scripts/overlay.py
Daemon._ensure_native(). This proof runs after class A step 5, in the same live
window if F3 sign-off still holds, otherwise in its own window.
Falsifier: killing the indicator during a hold and the pill does NOT return, or
returns only after the holder releases and re-acquires.

### C1 step 4. E1 per-event logging stays on
E1 logging (added for the flicker work) records every indicator event with
timestamps, so any future overlay loss is captured instead of estimated. The
logs are checked, not just collected: after every live run, the log is read for
indicator events during the run. A run with an overlay loss and no E1 record is
an incomplete run.

### C1 step 5. Commit discipline for C1
Each sub-step above is its own commit, pushed at once. The watchdog live proof
is its own commit with timestamps, pushed immediately after the run.

### C2 step 1. Never load hyprglass live to chase the flicker (safety veto V1)
Todolist 2.2.3 is BLOCKED for the live compositor for exactly this reason:
loading a backup plugin risks crashing Hyprland while the owner works. This
veto is permanent for tonight and is not negotiable by any worker. Any proposal
to "just try loading it live" is rejected without debate.

### C2 step 2. Measure only in the nested Hyprland (owner choice C, 18:24)
Preconditions (Y6r AMEND): fix A1-A10 plus a fresh re-review before any retry.
Then, in the nested compositor only: load hyprglass (Y6e nested LOAD TEST PASS
21:57 is the loader proof, not the flicker proof), animated backdrop ON, LIQUID
mode, E1 per-event logging running, same optics profile 9a151634. Count
repaints/commits per second over at least 60s idle and 60s driving-equivalent.
Repeat with animated backdrop OFF and with LIQUID OFF, same counts. The
hypothesis predicts a high repaint rate only in the animated + LIQUID cell.
Before the measurement, verify isolation: live Hyprland 1515 untouched, no live
windows moved, no input grabbed; check `hyprctl clients` before and after, and
abort if any live window changes.
Falsifier: 0 repaints in the animated + LIQUID cell, or equal repaint rates
across all four cells. Either kills the compositor-loop hypothesis and the
investigation restarts from the E1 logs, with the indicator re-opened as a
suspect only if the E1 logs show indicator events during a flicker.
Transfer gap, stated plainly: the nested compositor has no owner windows, no
real backdrop, and no real workload. A nested 0 does not prove the live desktop
is clean; it only falsifies the hypothesis under those conditions.

### C2 step 3. Do not re-litigate settled candidates
Two candidates are DEAD and must not be revived without new E1 log evidence:
(1) the indicator repaints at idle: 0 idle paints in 122 one-second windows,
32/32 frames pill pixel-identical, 60s idle with no events (todolist 2.2.1);
(2) screenshots cause the flicker: Muse observed every 10-30s, which cannot
cause ~10Hz flicker (todolist 2.2.5, I20 retraction). The flicker rate itself
(~10Hz, I10) was only a user estimate, never measured; the C2 measurement is
the first real frequency count. The pill blur increase (0.0 to 0.15, todolist
4.1) is a taste change, not a flicker fix, and must never be cited as one.

### C2 step 4. Commit discipline for C2
Each sub-step above is its own commit, pushed at once. The measurement result
is its own commit with the four-cell counts, pushed immediately after the run.
