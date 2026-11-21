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
