# Live-run readiness check, 2-vision benchmark, clone1 side (DOT 9 task 2)

Date: 2026-11-22, 07:11-07:25 +07. Verdict: NOT READY. No live run has
happened, and no live run can happen from the runbook today. The
runbook itself says so (section 0, section 12). This check, done with
fresh eyes against the runbook, the script, the workflow doc, and the
code on origin/todolist-push, found the runbook mostly accurate but
stale in one major place, contradicting the checklist it claims to
execute, and missing a concrete procedure for the attach/profile gap.
Each missing item is listed in "What is still missing" below.

This is a self-check: the runbook (docs/two-vision-live-runbook-
20261122.md, 794 lines, commit 2b98747) was written by clone2 in
batch 10 task 3. I re-read it in full and verified every
load-bearing claim myself against the primary sources, not on trust.

Sources read:
- Runbook: docs/two-vision-live-runbook-20261122.md, 794 lines, 2b98747.
- Script: tests/two_vision_bench.py, 868 lines, commit c267411.
- Workflow doc: docs/two-vision-benchmark-workflow-20261122.md, 660 lines.
- Design doc: docs/clone2-one-vision-design-20261122.md, 731 lines, c267411.
- CL1-SWEEP investigation: improvements/worker-cl1sweep-fail-invest-log.md,
  commit 5f5a2fd on origin/todolist-push.
- AMEND4 item 12: commit cbab398 on origin/todolist-push (landed 06:46).
- Code pins on origin/todolist-push tip: scripts/cu.py, scripts/a11y.py,
  scripts/first_action.py.

## What the runbook gets right (verified, not rubber-stamped)

1. Script line citations, all spot-checked exact: FF/GD lines 49-50,
   GATE_JS line 153, find_input lines 254-262, launch_browser lines
   265-296, default_plan run_id lines 543-544, normalize_file_url
   line 587, validate_plan line 600, URL gate lines 724-740, outcome
   rule ~line 831, visions_used hardcoded line 745,
   no-message-input-in-inventory line 794, --instances two refused
   lines 696-697. VERIFY_JS reads innerText for contenteditable
   (lines 133, 477-482). Only subprocess is Popen line 279.
2. Login-wall failure mode: correct. HARVEST_JS inventories every
   input, and the role logic maps a non-button input (email,
   password) to textbox. find_input returns the first visible
   textbox when none is named "Message". So on a login page the
   script types into the email field, V1 readback passes, Enter
   submits the login form, and the V12 gate times out after 5 s.
   The outcome is FAIL with clone1 v12-timeout and clone2
   not-executed, plus bench text in a login email field and a
   login submit with garbage credentials. Not fail-closed and safe.
3. Harvest-first cannot verify selectors: correct. In --mode
   harvest, main() returns HARVEST-ONLY (line 777) without ever
   evaluating thread_selector or bubble_selector; they are only
   touched inside send_one (lines 409-410, 420, 502) via GATE_JS,
   after typing.
4. Operator guard substance: faithful to the investigation log.
   The G28 rule, the first_action observe_screen capture, the
   desktop_act scope-matching after-capture, and the evidence
   values (8716 scope screen [1920, 1200], retry 0b78 scope window
   [901, 1176], f2bdb0d34ead scope screen) all check out against
   the log and the code at commit 5f5a2fd.
5. Vision budget scoping, VISION 2 as one screen observe of the
   monitor holding ws2 (`computer-use observe --screen <monitor>`,
   flag exists at scripts/cu.py line 2758), the 90% bar degeneracy
   note, C12 not a prerequisite for this script's clicks, and the
   pre-seed nuance (launch_browser does makedirs exist_ok and
   launches with -profile <profile>) all verified.

## Finding 1 (major, stale): section 9 is wrong after AMEND4 item 12 landed

AMEND4 item 12 (commit cbab398, 06:46) landed 4 minutes after the
runbook fix pass (2b98747, ~06:42). Three statements in section 9
are now false on current todolist-push tip:

- "The code fix that would remove the trap at the source ... is NOT
  built." False now. The envelope now carries BOTH `after`
  (scope-matching, chainable, via _scope_after in
  scripts/first_action.py) and `after_screen` (full monitor,
  verification only, documented non-chainable). Four regression
  tests, failing-first on the old code, per the item 12 commit.
- "The raise ... is not before all side effects: the overlay acquire
  and session attempt happen first (998 ms wasted)." Item 12 moved
  the scope check before the overlay attempt: a key/type batch given
  a screen-scope observation is now refused before the overlay and
  the session attempt.
- The first_action.py citation "lines 661-662" is wrong at current
  tip: lines 661-662 are dom_act ground_input code. The after-capture
  is now at ~lines 730-750 (screen_meta at 735, envelope['after']
  at ~743-746). Item 12 shifted the file.

Caveat that keeps the guard necessary: item 12 is on
todolist-push, not necessarily installed on the laptop. The run
machine runs pre-amend code if a baseline is still owed, so on the
laptop as it stands today the trap is still live and the guard is
still mandatory. But the runbook must say that explicitly instead
of stating the fix "is NOT built" unconditionally, and the hard
rule must now distinguish `after` (chainable post-fix) from
`after_screen` (never chainable). The runbook needs a dated
correction, not a rewrite.

## Finding 2 (major, contradiction): the runbook contradicts checklist 10

The runbook says checklist section 10 "is the prerequisite
checklist this runbook executes", but checklist 10 in the workflow
doc still contains the false statements the runbook corrects, and
the runbook never flags the contradiction. An operator reading the
checklist alone gets the wrong instructions on the two most
safety-relevant claims:

- 10.1: "a live run as specified would hit the login wall and FAIL
  with no-message-input-in-inventory (fail-closed and safe...)" Wrong
  per runbook section 0 and Finding 1 above. The runbook corrects
  it in its own text but the checklist still says it.
- 10.2: "Run --mode harvest with the live plan first... confirm both
  inputs are visible and the thread container resolves against the
  real threads. Wrong selectors are the proven typed-but-unseen
  failure mode, and this cheap pre-check catches them before any
  typing." False; harvest never evaluates the selectors (Finding 3
  in the verification above). Runbook section 6 corrects it, the
  checklist still says it.
- 10.2: "Both windows live in ONE Zen instance with two windows."
  Stale relative to G3 (Brave/Chrome on ws2).
- 10.1: "the ledger keys on run_id, and a reused run_id reuses
  intents." Wrong reason; runbook section 5 step 5 corrects it
  (with a fresh workdir the ledger is empty; the false PASS comes
  from the V12 pre-check seeing the old bubble).

Fix: either a correction pass on workflow doc section 10, or an
explicit statement in the runbook that its sections 0, 5, and 6
supersede checklist 10.1 and 10.2. Until then, two authoritative
docs disagree on the login-wall behavior and on selector checking.

## Finding 3: checklist 10.3 is insufficient as written

10.3 prescribes "check both live threads for an existing bubble
with that text" with no method, no generation rule, and no record
requirement. The runbook's section 5 supplies all three, so the
runbook repairs 10.3. But the supplied method (a11y query) rests on
two unverified premises, and the runbook has no step to prove the
method works before relying on it:

- Premise A (stated as UNVERIFIED in the runbook, honestly):
  whether Messenger bubbles are exposed through the a11y tree on
  Brave/Chrome. The a11y query is a case-insensitive substring
  search on a11y names (scripts/a11y.py query(), lines 118-140,
  CU_PICK4_FASTPATH=1 required, one bounded observe: 500 nodes,
  2 s, 80 items), not the V12 exact-text check.
- Premise B (not flagged in the runbook): the hyprctl client pid
  must be the AT-SPI application pid that a11y observe(pid)
  expects (scripts/a11y.py line 83, app(pid)). Whether Hyprland's
  client pid maps to the right application for Chrome/Brave is
  untested in any repo record.
- Missing step: a dry probe of the method. Before the run, run the
  a11y query for a KNOWN existing bubble text on each thread; a hit
  proves bubbles are exposed and the pid mapping works. Without
  that probe, a miss in step 0 proves nothing, and freshness rests
  only on generation (which the runbook does state plainly).

Verdict on 10.3: sufficient as a rule once runbook section 5 is
followed, but only with the dry probe added and the two premises
recorded. The workflow doc's 10.3 text itself should carry the
method and the generation rule, not just the runbook.

## Finding 4: the "Message" name rule is fixture-derived, not live-verified

The name rule in runbook sections 6 and 8 (a visible textbox
named "Message", case-insensitive; "Email"/"Password" fails) is
the only guard against typing into a login field. Its only
evidence in the repo is the fixture itself (placeholder="Message",
aria-label="Message" in tests/two_vision_fixture.html). No repo
record gives the live Messenger input's name in HARVEST_JS terms
(aria-label, else placeholder, else textContent, else value). If
the live input is named something else, the operator's name rule
would FAIL a correct harvest, and in run mode find_input would
silently fall back to boxes[0], which may not be the message
input. The runbook does not flag the expected name itself as
unverified. Needs: a live DOM read of the real Messenger input's
name before the run (or a plan-supplied input_name verified
against the live DOM), and a stated rule for what the operator
does if the name is not "Message".

## Finding 5 (the blocker): no concrete procedure for the attach/profile gap

The runbook lists the gap (section 12 items 1-3) but proposes no
procedure to close it. Under G3 the threads are in Brave/Chrome
on ws2, and the script drives only its own fresh headless Firefox
with a fresh profile. No procedure with the current script can
reach those threads. The coordinator must first decide the live
shape. The concrete procedure below is the cheapest path that
exists; the other two options are builds, not procedures.

Proposed procedure, option A (script shape, pre-seeded profile):

1. Coordinator decides: the live run uses the script's own
   Firefox, two windows, one Messenger account, two threads (the
   two clones' threads under one account). This abandons G3's
   Brave/Chrome. Which account holds the two threads is a
   coordinator decision, still unmade in any repo record.
2. On the run machine, launch Firefox with a fresh profile, log
   into Messenger manually once with that account, quit, and
   preserve the profile directory. The profile holds a live
   session: local only, never push it to the repo, never copy it
   into any shared artifact.
3. Verify the profile: launch Firefox with it and confirm both
   threads load. Sessions expire; re-verify before each run.
4. Before the run, copy the profile into <run-dir>/profile.
   launch_browser does makedirs with exist_ok and launches with
   -profile <profile>, so a pre-seeded profile is used as-is.
5. Coordinator supplies the plan (thread URLs, thread selector,
   bubble selector) for that account's two threads.
6. Run steps 0, 1, 2 per the runbook. The harvest-first step is
   the live check that the session works: Message inputs visible
   means logged in; a login wall means the session is dead, stop.
7. After the run, delete the profile copy from /tmp (512M tmpfs),
   keep the master profile local for re-runs.

Options B and C (builds, not procedures, listed so the choice is
explicit):
- B: keep G3 (Brave/Chrome). Build a Chromium/CDP driver for the
  benchmark; the script is Marionette-only and has no CDP path.
- C: move the threads to Zen and build an attach mode (Zen
  relaunched with -marionette, geckodriver --connect-existing,
  proven on the Firefox stand-in in batch 1). Requires the script
  to gain an attach mode and the coordinator to relaunch Zen on
  the laptop.

Also still gated, not a procedure: method approval (workflow doc
header; CL1-SWEEP caveat). The live run is the coordinator's
acceptance test, not the operator's call.

## Minor findings

- VISION 2 monitor: the runbook says "the monitor holding ws2"
  without naming it. Laptop records put ws2 on eDP-2 (monitor_box
  [2464, 902, 1920, 1200] in the investigation). State eDP-2 as
  the expected monitor, with a live `hyprctl -j monitors` check.
- Run log artifact: section 11 requires the operator's look count
  from "the run log", but no run log file is named. Name it
  (for example <run-dir>/run-log.md) and require each look to be
  logged with time, so the count is auditable.
- The runbook's section 5 step 2 says the a11y query "needs
  CU_PICK4_FASTPATH=1". Verified in scripts/a11y.py query(). If
  the flag is off on the laptop the query raises; the runbook's
  fallback (record it, rely on fresh generation) covers this.

## What is still missing (consolidated)

1. Runbook section 9 correction for AMEND4 item 12: the code fix
   IS built on todolist-push (cbab398); `after` is now
   scope-matching and chainable, `after_screen` is verification
   only; the scope check now fires before the overlay; the
   first_action.py citation must move to ~lines 730-750. State
   which code version the laptop actually runs, since the guard
   is still mandatory on pre-amend code.
2. Workflow doc section 10 correction pass (or an explicit
   supersede statement in the runbook): 10.1 login-wall mode,
   10.2 selector checking and "ONE Zen instance", 10.1 ledger
   rationale.
3. Checklist 10.3: dry probe of the a11y method (query a known
   bubble text first), both premises recorded (bubble exposure,
   pid mapping), and the method + generation rule written into
   10.3 itself.
4. Live Messenger input name verified against the real DOM, and
   a rule for a non-"Message" name.
5. Coordinator decision on the live shape (option A, B, or C
   above) and, for option A, the account decision plus a verified
   pre-seeded logged-in profile.
6. Method approval for the live run.
7. Thread URLs, thread selector, bubble selector for the live
   threads, supplied by the coordinator.
8. textNew in the V12 gate (NOT built; VISION 2 stays), pre-send
   reservation, V11 MutationObserver flag, D3 ref stability (all
   already in runbook section 12; unchanged by this check).
9. VISION 2 monitor named (eDP-2 expected) and the run log file
   named (<run-dir>/run-log.md).
