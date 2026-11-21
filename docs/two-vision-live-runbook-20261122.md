# 2-vision benchmark live-run runbook

Date: 2026-11-22. Status: PREPARATION ONLY. No live run has happened,
and no live run may happen from this runbook alone: the live run is
the coordinator's acceptance test, and nobody runs it live until the
coordinator says run. The script and the workflow doc are built only.

Sources read for this runbook (all verified before writing):
- Assignment: batch 10 task 3, coord/clone2.md line 868, commit
  422f4b0 (06:01 22/11). Decision G3 is stated there and nowhere
  else in the repo; see section 2.
- Script: tests/two_vision_bench.py, 868 lines, commit c267411.
- Workflow doc: docs/two-vision-benchmark-workflow-20261122.md,
  660 lines, checklist section 10 (added batch 9 task 2, fixed
  batch 9 task 2 fix pass).
- One-vision design: docs/clone2-one-vision-design-20261122.md,
  731 lines, commit c267411.
- Operator guard: improvements/worker-cl1sweep-fail-invest-log.md,
  commit 5f5a2fd on origin/todolist-push (CL1-SWEEP investigation,
  ~06:00 22/11). See section 9.
- Window layout on ws2: improvements/worker-cl1msg-log.md,
  00:46 22/11, on origin/todolist-push. See section 2.
- Accuracy bar: improvements/worker-coord-click2-log.md, line 32
  ("one vision must drive max actions at accuracy >= 90%") and
  line 38 (grounding accuracy 7/7 = 100% synthetic, bar >= 90%).

## 0. Blockers first: read this before anything else

This runbook does NOT make a live run possible today. Four things
are still missing or unimplemented, listed here up front and again
in full in section 12. Do not work around them by improvisation.

1. The script cannot drive the live chats as they exist today.
   It always launches its own fresh headless Firefox with a fresh
   profile (launch_browser, script lines 269-294). There is no
   attach-to-existing-browser option, no profile reuse, and no
   login step anywhere in the argument list. A fresh profile is
   logged out of Messenger, so a live run as specified would hit
   the login wall and FAIL with no-message-input-in-inventory
   (fail-closed and safe, but not a passing run). An attach-to-Zen
   mode does not exist, and neither does a logged-in profile or a
   login step.
2. Under decision G3 the live threads are in Brave (clone1) and
   Chrome (clone2) on workspace ws2. The script drives only
   Firefox and cannot attach to Brave, Chrome, or Zen. No path
   exists today for the script's browser to reach those threads.
3. The V12 gate is a presence check only (GATE_JS, script
   line 153): it has no before-snapshot, so a bubble whose text
   was already in the thread when the batch started passes it.
   The textNew distinction is designed but not built, and the
   VISION 2 removal in the one-vision design doc is conditional
   on textNew being built and proven. This runbook keeps 2
   visions; see section 8.
4. The run_id freshness check is an operator check only. The
   script does not check run_id against thread history. Reusing
   a run_id on a live thread scores PASS with zero new sends;
   see section 5.

## 1. The run, in one paragraph

Two clones, two threads, two messages, two visions. VISION 1 is
one one-shot DOM harvest per window (never a screenshot). From
that inventory the script runs one fixed send chain: click the
clone1 input, type "BENCH-TEST clone1 <run_id>", Enter, click
the clone2 input, type "BENCH-TEST clone2 <run_id>", Enter.
VISION 2 is the agent looking at both threads once at the end
to confirm both bubbles, backed by the script's V12 DOM gates
after each send. Outcome scoring is by message in thread (M1),
never by point-in-box. PASS iff both messages land. The whole
run is driven by tests/two_vision_bench.py; the operator's job
is the checks around it, not the sends.

## 2. Decision G3: clone1 Brave + clone2 Chrome on ws2

What G3 says, verbatim from the assignment (coord/clone2.md:868,
batch 10, commit 422f4b0): "Theo quyet dinh G3: clone1 Brave +
clone2 Chrome tren ws2."

What the repo corroborates: the CL1-MSG log (00:46 22/11,
improvements/worker-cl1msg-log.md on origin/todolist-push)
records the same layout on the laptop: Brave 0x55705383d420 on
ws2, title "Muse" (clone1); Chrome 0x5570538ed160 on ws2,
title "Muse" (clone2); Zen 0x557052b62dd0 on ws1 intact.
The arch-review log (improvements/worker-arch-review-log.md)
states the acceptance test in the same shape: a live benchmark
against the REAL clone chats on ws2 (not the local fixture in
headless Firefox), DOM harvest, plan, execute, DOM verify, zero
screenshots in the loop, accuracy >= 90%, total wall time
measured end to end including transport.

What G3 does NOT say in any repo record: no separate G3 decision
document was found in the repo. Nothing in the repo records who
decided G3, when it was decided, which machine runs the script,
which account holds the two threads, or how the script's browser
gets a Messenger session. This runbook does not invent any of
that; those are open items in section 12.

Window addresses are session addresses. The Brave and Chrome
addresses above are from 00:46 22/11 and are stale by now.
Re-list the windows live before the run with:

```
hyprctl -j clients
```

Confirm Brave (clone1) and Chrome (clone2) are both on ws2 and
Zen is intact on ws1 before doing anything else. Never copy a
stale window address into a command.

## 3. Files and versions (pins)

Check these before the run. Any other hash means an unreviewed
change sits on top of the reviewed code; stop and report.

- Script: tests/two_vision_bench.py, 868 lines, commit c267411.
  Run `git log --oneline -1 -- tests/two_vision_bench.py` and
  confirm it prints c267411.
- Workflow doc: docs/two-vision-benchmark-workflow-20261122.md,
  660 lines. Checklist section 10 in that doc is the
  prerequisite checklist this runbook executes.
- Design doc: docs/clone2-one-vision-design-20261122.md,
  731 lines, commit c267411.
- The script hardcodes its browser paths (script lines 49-50):
  FF = /home/hatch/workspace/tools/firefox/firefox,
  GD = /home/hatch/workspace/tools/geckodriver. The run machine
  must have the Firefox binary, geckodriver, and venv at those
  paths. The fixture re-runs used the repo venv python:
  ~/workspace/tools/venv/bin/python.
- The script's only subprocess is launching Firefox
  (subprocess.Popen in launch_browser). It never calls
  `computer-use` act-now and never opens a BiDi session while
  the Marionette session is active (one-session rule).

## 4. The plan file

The coordinator supplies the live plan JSON. The script cannot
invent thread URLs or selectors. The plan has exactly this
shape (workflow doc section 5; script validate_plan, ~line 600):

```json
{
  "run_id": "bench-20261122-001",
  "windows": [
    {"label": "clone1", "url": "<clone1 thread URL>",
     "input_name": "Message",
     "thread_selector": "<thread container>",
     "bubble_selector": "<sent bubble selector>"},
    {"label": "clone2", "url": "<clone2 thread URL>",
     "input_name": "Message",
     "thread_selector": "<thread container>",
     "bubble_selector": "<sent bubble selector>"}
  ],
  "messages": {
    "clone1": "BENCH-TEST clone1 bench-20261122-001",
    "clone2": "BENCH-TEST clone2 bench-20261122-001"
  },
  "timeouts": {"v12_gate_s": 5}
}
```

Rules the script enforces (validate_plan, before any browser
starts; a violation refuses with exit 2 and sends nothing):
exactly 2 windows; the two URLs must differ (two windows on
the same URL would report PASS with both messages in one
thread); run_id must be a non-empty string; every window label
must have a messages entry. Plan file:// URLs are normalized
before the gate, so a ".." path cannot pass the gate textually
while pointing outside the fixture dir.

Rules the operator enforces (the script does not):
- The two URLs must be the two real thread URLs, one per clone,
  supplied by the coordinator. The two URLs must differ.
- thread_selector must point at the thread container.
  bubble_selector MUST be overridden for Messenger in the plan:
  the default (".bubble, [data-sender]") is fixture-shaped and
  the V12 gate requires exact textContent === text, so the
  default would fail closed live.
- The message input in each thread is a contenteditable textbox
  (the Messenger input type). The script's V1 check reads
  innerText for contenteditable elements; if a thread's input
  is a different control, say so in the plan and re-check the
  fixture variant first.
- v12_gate_s is set in the plan (5 s default; raise it only if
  the live thread is slow to render, and record the value used).
- Messages are bench strings only. Never put real user text,
  names, or personal information in a plan, inventory, ledger,
  log, or result file.
- Both windows live in ONE browser instance with two windows
  (the --instances one shape). Two instances are not
  implemented and --instances two is refused (exit 2).

## 5. Step 0: run_id freshness check (do this first)

This is the open run_id-reuse hole (workflow doc 10.3): the
message text is derived from run_id, and the script's V12
pre-check returns skipped-already-sent whenever the bubble text
is already in the thread, which the outcome counts as sent. So
reusing a run_id on a live thread reports PASS with zero new
sends. The script does not check run_id against thread history.
The operator checks it by hand, before the run, for both
threads. Fixture threads do not persist, so this cannot be
reproduced or tested on the fixture.

1. Generate a fresh run_id for this attempt. Never reuse a
   run_id from a previous attempt, including a failed one. The
   script's default format is bench-<UTC timestamp>-<6 hex>
   (default_plan, script lines 543-546); the checklist example
   is bench-20261122-001. Use a fresh timestamp-based run_id
   and put it in the plan, in both messages, in exactly the
   form "BENCH-TEST clone1 <run_id>" and
   "BENCH-TEST clone2 <run_id>".
2. Check the clone1 thread for an existing bubble whose
   textContent is exactly "BENCH-TEST clone1 <run_id>".
   Check the clone2 thread for an existing bubble whose
   textContent is exactly "BENCH-TEST clone2 <run_id>".
   The authoritative check is a DOM read of the thread (the
   same exact-text check the V12 gate performs). A visual
   search of the thread is only a fallback, and a visual
   search that finds nothing does not prove the text is
   absent; if in doubt, do the DOM read.
3. If the exact text is found in either thread, the run_id is
   NOT fresh: discard it, generate a new one, update the plan
   and both messages, and check again from step 2.
4. Record the check in the run log: the run_id used, both
   threads checked, what was found (nothing, expected), and
   the time. A run_id that was never checked is not a fresh
   run_id.
5. Use a fresh --workdir per run (for example
   /tmp/two_vision_bench/live1). Never reuse a live run's
   workdir: the ledger keys on run_id, and a reused run_id
   reuses intents.

## 6. Step 1: harvest-first (before any send)

Run --mode harvest with the live plan first, before any send
run. Confirm both inputs are visible and the thread container
resolves against the real threads. Wrong selectors are the
proven typed-but-unseen failure mode, and this cheap pre-check
catches them before any typing. The URL gate applies here too:
a non-fixture plan needs both --live and --confirm-live even
for a harvest-only run, before any browser starts.

```
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --plan <live-plan.json> --mode harvest \
  --live --confirm-live \
  --workdir <fresh-dir> --print-inventory
```

Required outcomes before proceeding:
- The harvest returns both message inputs, each visible, with
  a ref, rect, center, and role textbox. If either input is
  missing, the run is FAIL before anything is sent
  (no-message-input-in-inventory, fail-closed). Stop. Do not
  proceed to the send run.
- The thread container resolves for both windows (the
  thread_selector points at a real container, not an empty
  match).
- If the harvest shows a login wall instead of a textbox, the
  run is FAIL with no-message-input-in-inventory and the
  blocker in section 0 stands. Do not hand-log-in inside the
  script's browser unless the coordinator explicitly orders
  that step: which account sends is a coordinator decision
  (one profile holds one Messenger session), and improvising
  a login invents it.

## 7. Step 2: the live run

Only after steps 0 and 1 pass, the live lane is free, and the
coordinator has said run for this run_id. One command:

```
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --plan <live-plan.json> --mode run \
  --live --confirm-live \
  --workdir <fresh-dir>
```

What the flags do:
- --live and --confirm-live are BOTH required. --live without
  --confirm-live refuses with exit 2 and sends nothing. A
  custom plan with real thread URLs and no --live flag used to
  run the full send chain against those threads; the gate is
  now on the plan URLs, not the flag, and it refuses any
  non-fixture plan without both flags.
- --instances defaults to one and must stay one. --instances
  two is refused (exit 2) because two instances are not
  implemented.
- --live and --fixture together is refused (exit 2).
- The script validates the plan before any browser starts
  (exactly 2 windows, distinct URLs, non-empty run_id). A
  refused plan exits 2 and starts no browser.
- The script launches its own fresh headless Firefox with a
  fresh profile under <fresh-dir>/profile and refuses if ports
  2828 or 9223 are already held. A stale browser holding
  either port makes launch_browser refuse; kill the stale
  browser first, do not attach to it.
- /tmp has room (512M tmpfs; check `df -h /tmp`) and ports
  2828 and 9223 are free on the run machine before starting.

What the script does, in order: VISION 1 one-shot harvest per
window; plan-once send chain (click clone1 input, type, Enter,
click clone2 input, type, Enter) with the HCU live guard
re-checking each target's live geometry and focus right before
input; V12 gate after each send (sent bubble in the thread
DOM); stop at the first failure, later steps recorded
not-executed; exactly-once intents (ledger + V12 pre-check).
The operator does not type, click, or send anything by hand
during the run. All intermediate checks are DOM reads, not
extra screenshots; the vision budget is exactly 2 (section 8).

## 8. Pass criteria

- VISION 1 (harvest): PASS iff the one-shot harvest returns
  both message inputs, each visible, with a ref, rect, center,
  and role textbox. If either input is missing, the run is
  FAIL before anything is sent.
- VISION 2 (outcome check): PASS iff both BENCH-TEST messages
  appear as bubbles in their threads. The script's V12 gates
  check this by DOM read after each send; the agent's VISION 2
  look at both threads once at the end is the independent
  confirmation. Outcome scoring is by message in thread (M1),
  never by point-in-box.
- Overall: PASS iff both messages land. Any single failed step
  makes the run FAIL; the chain stops at the first failure.
  The script's outcome rule (main, script ~line 831) is PASS
  iff exactly 2 sent AND exactly 2 windows.
- Vision budget: total exactly 2 visions. VISION 1 is a DOM
  harvest, not a screenshot. VISION 2 is the one look at both
  threads at the end. Anything beyond 2 visions fails the
  budget, even if both messages land. The script records
  visions_used: 2 in results.json; the operator counts their
  own looks too. Do not take extra visual looks during the
  run; every intermediate check is a DOM read.
- Accuracy bar: 90% or more (coordinator's bar, click2 log
  line 32). With 2 sends, 2/2 = 100% passes and 1/2 = 50%
  fails the bar, so in practice PASS requires both messages.
  There is no partial pass.
- The one-vision design doc proposes removing VISION 2, but
  only conditionally: VISION 2 stays until textNew is built
  and the gate is proven to count only new bubbles, plus a
  cross-window check (each thread holds only its own message).
  That proposal is NOT in effect for this runbook. The live
  run uses 2 visions.
- Grounding accuracy on synthetic data is 7/7 = 100% (click2
  log line 38). That is a synthetic figure, not a live one.
  Live accuracy is what this run measures; it is owed, not
  claimed.

## 9. Operator guard (CL1-SWEEP investigation)

This guard binds the OPERATOR's manual computer-use steps
around the benchmark, not the script. The script is immune:
it drives via WebDriver only, never calls `computer-use`
act-now, and its only subprocess launches the browser
(investigation, section "Impact on the upcoming 2-vision
benchmark"). But any manual computer-use step around the
benchmark (opening a chat, verifying visually with act-now)
can hit the trap, so the guard is part of this runbook.

What the investigation proved (improvements/
worker-cl1sweep-fail-invest-log.md, commit 5f5a2fd on
origin/todolist-push, ~06:00 22/11):
- Verdict: the coordinator's self-diagnosis was CONFIRMED but
  INCOMPLETE. He used a full-screen after-image as the
  observation, and screen observations refuse key actions
  (G28). True, but one level short of the root cause.
- Root cause: act-now ALWAYS returns a screen-scoped
  after-image by construction, even when the input observation
  was window-scoped. scripts/first_action.py (~line 656)
  captures the after with
  `cu.observe_screen(env, args.screen, max_width=1920,
  persist=True)` and never consults the input observation's
  scope. desktop_act (scripts/cu.py lines 2083-2091) already
  captures a scope-matching after in result['after'], but
  first_action.py never copies it into the envelope.
- Evidence, re-derived from the laptop (not taken from the
  coordinator's log): the failed call was a key action,
  [{"keys":["Return"],"type":"key"}] (cl1sweep-enter1.json).
  Observation 8716a28d6388.json was scope "screen",
  image_size [1920, 1200], region [2464, 902, 1920, 1200],
  monitor_box [2464, 902, 1920, 1200], max_width 1920, NO
  window field. The retry observation 0b78b458b8f3.json was
  scope "window", window 0x55705383d420, image_size
  [901, 1176], region [2533, 914, 901, 1176], max_width 960.
  The retry succeeded. The CL2-MSG after-image f2bdb0d34ead
  (03:51 click) is ALSO scope "screen", [1920, 1200]: the
  same trap existed then and did not bite only because the
  next steps used fresh window observes.
- The gate (scripts/cu.py desktop_act, ~line 1649, the G28
  rule): `screen_scope = meta.get('scope') == 'screen'`;
  if screen_scope and any action is type key or type, raise
  ValueError('screen observations support pointer actions
  only; use a window or accessibility target for typing').
  The raise happens in preflight, before any side effect:
  fail-closed, 998 ms, nothing typed or sent.
- The after-image looks exactly like a chainable observation
  (same schema, has an id and an observation path) and
  nothing labels it non-chainable. An after-image is fresh
  in TIME (seconds old) but wrong in SCOPE. "Fresh observe"
  must mean a fresh WINDOW observe, never a reused
  after-image.

The hard rule, from the investigation's procedure fix:
NEVER reuse an act-now `after` image as the --observation
for a subsequent call. ALWAYS take a fresh
`computer-use observe --window <addr>` before any key/type
step.

Exact commands for every manual computer-use step that
contains a key or type action:

1. List the windows live and take the address from the live
   list, never from a stale record:

```
hyprctl -j clients
```

2. Take a fresh window observation for the target window:

```
computer-use observe --window <addr>
```

3. Before the act-now call, read the observation JSON and
   assert the scope. If scope is "screen", re-observe the
   window first; do not proceed:

```
python3 -c "import json,sys; m=json.load(open(sys.argv[1])); assert m.get('scope') in ('window','accessibility'), m.get('scope')" <observation.json>
```

4. Only then run the act-now call with that observation id
   as --observation. Never pass an act-now after-image id as
   --observation. Never reuse the after-image from the
   previous call, even if it is seconds old.

How to tell an after-image from a real window observation
(shape, not values to copy; addresses and regions change
per session): an act-now after-image is scope "screen",
max_width 1920, image [1920, 1200], and has NO window field.
A genuine window observation is scope "window", has a window
field (for example 0x55705383d420), and max_width 960. The
reliable check is the scope field in the JSON, not the size.

If a call fails with 'screen observations support pointer
actions only; use a window or accessibility target for
typing', the observation was screen-scoped. That is the G28
preflight refusal: nothing was typed or sent. Re-observe the
window fresh (step 2 above) and retry with the new
observation. Do not retry with the same observation id.

The code fix that would remove the trap at the source
(act-now after-capture matching the input scope, or returning
both `after` scope-matching and `after_screen` verification
only) is recommended in the investigation but is NOT built.
Until it lands, the procedure rule above is the only guard.
Item 12 of the AMEND4 re-verification (batch 10 task 2) covers
the code side: act-now after-scope mismatch, envelope after
always screen-scoped, fix returns the scope-matching
chainable after and after_screen for verify only, scope check
before overlay.

## 10. Stop conditions (abort the live run, do not push on)

- Stop at the first failed step. The script does this itself;
  do not restart the chain mid-run.
- If a send ends in v12-timeout, STOP. Check the thread by
  hand. Never re-run with the same run_id: the ledger marks
  the intent failed-unverified and refuses the retry. To
  retry, fix the thread/bubble selectors first, then use a
  NEW run_id and repeat the freshness check (section 5).
- If either thread becomes unreachable, or the browser
  crashes, or a click lands on the wrong window, STOP and
  report the state (which intents are sent, which are
  failed-unverified) before doing anything else. Do not
  re-send to "make up" for a lost message: a re-send without
  a V12-visible bubble is exactly how a duplicate happens.
- If --confirm-live was not explicitly given by the
  coordinator for this run, STOP. The script refuses without
  it, and the URL gate refuses any non-fixture plan without
  both --live and --confirm-live.
- If the run_id freshness check finds the text already in a
  thread, STOP before starting. Generate a new run_id and
  check again.
- If the harvest-first step fails (input missing, thread
  container does not resolve, login wall instead of a
  textbox), STOP before any send.
- If the plan validation refuses (exit 2), STOP. Fix the
  plan. Do not bypass the validation.
- If a manual computer-use step is about to use an
  observation whose scope is "screen" for a key or type
  action, STOP and re-observe the window first (section 9).
- A value-mismatch means nothing was sent (Enter was not
  pressed). A v12-timeout means the message may have been
  typed and may have landed unseen, so the thread must be
  checked by hand. Do not treat them the same.

## 11. After the run: preserve and report

- Preserve the full log, results.json, inventory.json, and
  ledger.json out of /tmp IMMEDIATELY (fix-pass logs were
  once lost to a /tmp wipe). Also preserve the plan file
  used and the run_id freshness check record from section 5.
- Delete the profile/ dir under the run workdir after the
  run (/tmp is a 512M tmpfs; stale Firefox profiles have
  filled it to 100% before).
- Report the outcome with the run_id and wall time: outcome
  (PASS/FAIL), per-step statuses, visions_used (must be 2),
  and which intents are sent vs failed-unverified.
- Never edit a result file after the run.
- Confirm no Firefox process was left running and /tmp has
  room again.

## 12. What is still missing or unimplemented

Consolidated, so nobody mistakes this runbook for readiness.
A live run cannot pass until these are closed or the
coordinator explicitly accepts them.

1. Attach-to-Zen mode (or any attach-to-existing-browser
   mode): NOT implemented. The script always launches its
   own fresh headless Firefox.
2. Logged-in profile / login step: does NOT exist. A fresh
   profile is logged out of Messenger.
3. Under G3 the live threads are in Brave (clone1) and
   Chrome (clone2) on ws2. The script drives only Firefox
   and cannot attach to Brave, Chrome, or Zen. No path exists
   today for the script's browser to reach those threads.
   Which account holds the two threads, and how the script's
   browser gets a Messenger session, are coordinator
   decisions that have not been made in any repo record.
4. textNew in the V12 gate: NOT built. The gate is a
   presence check only; a stale bubble passes it. VISION 2
   removal is conditional on textNew being built and proven
   plus a cross-window check.
5. Pre-send reservation (exactly-once across a process death
   between send and ledger mark): OPEN work, in the design
   doc section 7 and as a TODO in the script's Ledger
   docstring. The failed-unverified retry block closes only
   the narrower v12-timeout case.
6. run_id freshness check: operator-only, not in the script.
   The script never checks run_id against thread history.
7. Thread URLs, thread selector, and bubble selector: must
   come from the coordinator for the live threads. The script
   cannot invent them.
8. Method approval: the live run is gated on it (workflow
   doc header; CL1-SWEEP investigation caveat). The live run
   is the coordinator's acceptance test, not the operator's
   call.
9. Live lane must be free: no BASELINE2 or other live run
   running, and no other agent holding the laptop browser.
   The installed laptop code must still be the pre-amend
   code if a baseline is still owed.
10. V11 MutationObserver flag: NOT built. The fixture counts
    input events in window.__inputEvents; a Messenger page
    needs a real observer armed before typing.
11. No live measurement of the 90% accuracy bar exists yet.
    Synthetic grounding is 7/7 = 100%; the live proof is
    owed, not claimed.

NOT missing, to avoid confusion: the C12 adjudication does
NOT apply to this script's clicks and is NOT a prerequisite
(workflow doc section 9: clicks use getBoundingClientRect
viewport coordinates directly). C12 applies only to a future
Zen-attached variant whose clicks go through the conversion
layer.

## 13. Sources

- Batch 10 assignment: coord/clone2.md line 868, commit
  422f4b0.
- Script: tests/two_vision_bench.py (868 lines, c267411);
  FF/GD lines 49-50; default_plan run_id lines 543-546;
  normalize_file_url ~line 587; validate_plan ~line 600;
  URL gate ~lines 724-740; outcome rule ~line 831;
  launch_browser lines 269-294.
- Workflow doc: docs/two-vision-benchmark-workflow-20261122.md
  (660 lines); section 5 plan shape; section 6 failure
  meanings; section 9 C12 not used; section 10 checklist.
- Design doc: docs/clone2-one-vision-design-20261122.md
  (731 lines, c267411); section 1 vision budget; section 3
  coordinate chain; section 4.2 textNew; section 4.3.2
  pre-send reservation; section 7 open items.
- CL1-SWEEP investigation: improvements/
  worker-cl1sweep-fail-invest-log.md, commit 5f5a2fd on
  origin/todolist-push.
- Window layout: improvements/worker-cl1msg-log.md, 00:46
  22/11, on origin/todolist-push.
- Accuracy bar: improvements/worker-coord-click2-log.md,
  lines 32 and 38.
- Acceptance-test shape: improvements/
  worker-arch-review-log.md (0-vision live benchmark against
  the real clone chats on ws2).
