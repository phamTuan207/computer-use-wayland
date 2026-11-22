# 2-vision benchmark live-run runbook

Date: 2026-11-22. Status: PREPARATION ONLY. No live run has happened,
and no live run may happen from this runbook alone: the live run is
the coordinator's acceptance test, and nobody runs it live until the
coordinator says run. The script and the workflow doc are built only.
Updated 22/11 by the batch 11 task 2 closeout (section 9 corrected
for AMEND4 item 12, section 13 added with both live-shape options,
section 12 rewritten with current statuses; verdict still NOT READY,
see docs/clone2-live-run-readiness-closeout-20261122.md).

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
   profile (launch_browser, script lines 265-296). There is no
   attach-to-existing-browser option, no profile reuse, and no
   login step anywhere in the argument list. A fresh profile is
   logged out of Messenger, so a live run as specified would hit
   the login wall and FAIL, but NOT with
   no-message-input-in-inventory and NOT fail-closed and safe.
   A login page has visible email and password inputs, which
   HARVEST_JS inventories as textboxes, and find_input (script
   lines 254-262) returns the first visible textbox when none
   is named "Message", so it picks the email field. The script
   then clicks it, types the bench text into it (the V1 readback
   passes, the text IS in the field), Enter submits the login
   form, and the V12 gate times out after 5 s because no thread
   container exists. The outcome is FAIL with clone1 v12-timeout
   (intent failed-unverified) and clone2 not-executed, plus two
   side effects the operator must expect: the bench text typed
   into a login email field, and an Enter that submits a login
   attempt with garbage credentials. The
   no-message-input-in-inventory error (main, script line 794)
   fires only when a page has zero visible textboxes, which a
   login page does not satisfy. An attach-to-Zen mode does not
   exist, and neither does a logged-in profile or a login step.
   The two live-shape options that would close this gap are
   written in full in section 13; the coordinator decides
   which one runs.
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
after each send. VISION 2 is one screen observe of the monitor
holding ws2 (one image showing both tiled windows, see
section 8); two window observes would themselves be 2 visions
for VISION 2 alone and break the budget, so they are not the
method. Outcome scoring is by message in thread (M1),
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
   (default_plan, script lines 543-544); the checklist example
   is bench-20261122-001. Use a fresh timestamp-based run_id
   and put it in the plan, in both messages, in exactly the
   form "BENCH-TEST clone1 <run_id>" and
   "BENCH-TEST clone2 <run_id>".
2. Check the clone1 thread for an existing bubble whose
   textContent is exactly "BENCH-TEST clone1 <run_id>".
   Check the clone2 thread for an existing bubble whose
   textContent is exactly "BENCH-TEST clone2 <run_id>".
   Freshness comes from generation, not from the check: a
   freshly generated timestamp-based run_id is fresh by
   construction, since no earlier run could have used that
   exact text. The check below can only catch a reused run_id;
   it cannot prove a run_id fresh.
   The only executable check on the Brave/Chrome threads is
   an accessibility-tree substring search, not the V12
   exact-text DOM check (the script's browser cannot reach
   the threads, blocker 1, and no DOM-read command for
   Brave/Chrome is specified anywhere in the repo). For each
   thread, take the AT-SPI application PID from `a11y apps`,
   NOT the hyprctl client pid: the hyprctl window PID is not
   the AT-SPI app PID (prior evidence, improvements/
   speed-proto-pick4-summary.md:15, for kitty, omacalc,
   omawrite, and Zen; same record at docs/redteam-council-
   20261121/worker2-todolist-redteam.md:185), and a11y
   observe(pid) raises "exact app PID required; use a11y
   apps" for any other pid (scripts/a11y.py app(), lines
   57-60). List the apps first, find the Brave (clone1) and
   Chrome (clone2) entries, and use their PIDs:

```
computer-use a11y apps
CU_PICK4_FASTPATH=1 computer-use a11y query --pid <atspi-pid> \
  --name "BENCH-TEST clone1 <run_id>"
```

   (and the same with clone2 and its own AT-SPI pid). This
   needs CU_PICK4_FASTPATH=1 (scripts/a11y.py query() refuses
   without it) and returns the elements whose accessibility-tree
   name contains the text (case-insensitive substring), up to
   20, from one bounded observe (500 nodes, 2 s, 80 items; the
   result carries a `matched` count and a `truncated` flag).
   Limits, stated plainly: a hit proves the text is present
   somewhere in that app's accessibility tree, not that it
   is a bubble in the thread (substring match on a11y names
   is not the V12 gate's exact textContent === text check
   on a bubble inside the thread container); a miss does
   NOT prove the text is absent, because the observe is
   bounded and scrollback content may not be in the tree,
   and whether Messenger bubbles are exposed through the
   a11y tree on Brave/Chrome is UNVERIFIED in any repo
   record. A visual search of the thread is only a fallback
   with the same limit: a visual search that finds nothing
   does not prove the text is absent, and a bubble sitting
   in scrollback, missed by a visual search, still produces
   the false PASS this check exists to prevent (reused
   run_id, zero new sends, outcome PASS). If in doubt, do
   the a11y query; if the query cannot run, record that and
   rely on the fresh generation.

   Dry probe of this method (do this once, before the first
   live run, and record the result in the run log; it has
   NOT been run yet). Test the two premises separately, so a
   failure tells you which premise broke:
   - Part 1, pid mapping: run `computer-use a11y apps` and
     confirm Brave and Chrome both appear with PIDs. Then
     run the a11y query above for a KNOWN existing bubble
     text (any real message already visible in each thread,
     not a bench string). If the query returns the known
     text, the pid mapping works and bubbles are exposed.
     If it raises "exact app PID required", the pid is
     wrong; re-list with `a11y apps` and use the listed
     pid, never the hyprctl client pid.
   - Part 2, bubble exposure: the Part 1 hit (or miss) for
     a known bubble text is itself the exposure test. A hit
     proves Messenger bubbles are exposed through the a11y
     tree on that browser; a miss for text that is visibly
     in the thread proves they are NOT exposed (or are
     outside the bounded observe), and the a11y method
     cannot be used for freshness on that browser: fall
     back to fresh generation plus a visual search, and
     record that the method failed.
   Until this probe runs, premise A (bubble exposure) is
   UNVERIFIED and premise B (pid mapping) is contradicted
   by prior evidence for other apps; the freshness check
   rests on generation alone, which the runbook states
   plainly in step 2 above.
3. If the exact text is found in either thread, the run_id is
   NOT fresh: discard it, generate a new one, update the plan
   and both messages, and check again from step 2.
4. Record the check in the run log: the run_id used, both
   threads checked, what was found (nothing, expected), and
   the time. A run_id that was never checked is not a fresh
   run_id.
5. Use a fresh --workdir per run (for example
   /tmp/two_vision_bench/live1 for the run, and a separate
   /tmp/two_vision_bench/harvest1 for the harvest-first step
   in section 6). Never reuse a live run's workdir. The
   reason is not the ledger: with a fresh workdir the ledger
   is empty, so a reused run_id does not reuse intents from
   the ledger; the false PASS comes from the V12 pre-check
   seeing the old bubble in the thread, not from the ledger.
   The fresh workdir matters because the ledger, results,
   and inventory of one run must not be confused with
   another's, and because the run's results.json would
   otherwise overwrite the harvest's HARVEST-ONLY
   results.json (steps 1 and 2 must use different workdirs,
   <harvest-dir> and <run-dir>).

## 6. Step 1: harvest-first (before any send)

Run --mode harvest with the live plan first, before any send
run. Confirm both message inputs are visible and named
"Message" in the inventory text. What this step can catch is
a missing or misnamed input; what it cannot catch is a wrong
thread or bubble selector (see the required outcomes below),
so do not read more into it than that. The URL gate applies
here too: a non-fixture plan needs both --live and
--confirm-live even for a harvest-only run, before any browser
starts.

```
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --plan <live-plan.json> --mode harvest \
  --live --confirm-live \
  --workdir <harvest-dir> --print-inventory
```

Required outcomes before proceeding:
- The harvest returns, in each window, a visible textbox
  named "Message" (the name contains "Message",
  case-insensitive, the same rule find_input uses), with a
  ref, rect, center, and role textbox. The harvest returns
  ALL inputs and buttons and does not identify message
  inputs; this check is decided by the operator reading the
  names in the inventory text (`[i] role 'name' ref=...`),
  not by the script. A textbox named "Email" or "Password",
  or any visible textbox whose name does not contain
  "Message", FAILS the check: stop, do not proceed to the
  send run. The script itself gives no warning here: in run
  mode find_input silently picks the first visible textbox,
  so this human judgment is the only guard against typing
  into a login field (see section 0 item 1). If either
  window has no textbox named "Message", the run is FAIL
  before anything is sent.
- Caveat on the name itself: the expected name "Message"
  is visual-only evidence, not a DOM read. Two independent
  screenshot reads in the CL1-MSG logs report the live
  Messenger input showing a "Message" placeholder
  (improvements/worker-cl1msg-log.md:23, "Message"
  placeholder at ~(142,1037); improvements/
  worker-cl1msg2-log.md:18, "Message" placeholder at
  ~(180,1026)). No DOM or a11y read of the live Messenger
  input exists anywhere in the repo (searched both branches
  22/11: no aria-label record, no saved observation JSON,
  no a11y dump of the input), so the real aria-label is
  UNKNOWN. HARVEST_JS takes the name as aria-label first,
  else placeholder, else textContent, else value (script
  line 106), so an aria-label other than "Message" takes
  precedence and breaks this rule. Rule for a non-"Message"
  name: if the harvest shows a visible textbox whose name
  is not "Message" and is not "Email"/"Password", STOP and
  record the actual name in the run log; do not proceed,
  do not guess. The name is only closed by a live DOM read
  of the real input before the run (read the input's
  aria-label and placeholder from the live DOM, or supply
  input_name in the plan and verify it against the live
  DOM in the harvest). Until that read happens, a harvest
  showing no "Message" input is ambiguous (login wall
  versus a differently-named input) and the run must stop,
  not proceed.
- The harvest-first step does NOT verify thread_selector or
  bubble_selector, and nothing in this runbook should claim
  it does. In --mode harvest, main() opens the windows, runs
  harvest_window per window, writes inventory.json, and
  returns HARVEST-ONLY; thread_selector and bubble_selector
  are never evaluated in that path. They are only touched
  inside send_one via GATE_JS, after typing. The selectors
  stay unverified until the first V12 gate, so the first
  send is the first real selector test: a wrong selector
  means the message may be typed but unseen (v12-timeout,
  intent failed-unverified, check the thread by hand, new
  run_id). Wrong selectors are the proven typed-but-unseen
  failure mode, and the harvest-first step does not catch
  them; it catches only a missing or misnamed input.
- If the harvest shows a login wall instead of a message
  input (visible textboxes named "Email" and "Password", no
  textbox named "Message"), the run is FAIL before anything
  is sent and the blocker in section 0 stands. This is a
  human judgment on the inventory text, not a script
  outcome: in harvest mode the script returns HARVEST-ONLY
  and never emits the no-message-input-in-inventory error
  (find_input is only called in run mode). Do not hand-log-in
  inside the script's browser unless the coordinator
  explicitly orders that step: which account sends is a
  coordinator decision (one profile holds one Messenger
  session), and improvising a login invents it.

## 7. Step 2: the live run

Only after steps 0 and 1 pass, the live lane is free, and the
coordinator has said run for this run_id. One command:

```
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --plan <live-plan.json> --mode run \
  --live --confirm-live \
  --workdir <run-dir>
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
  fresh profile under <run-dir>/profile and refuses if ports
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

- VISION 1 (harvest): PASS iff the one-shot harvest returns,
  in each window, a visible textbox named "Message" (the name
  contains "Message", case-insensitive), with a ref, rect,
  center, and role textbox. The harvest returns ALL inputs
  and buttons and does not identify message inputs; this
  criterion is decided by the operator reading the names in
  the inventory text, not by the script. On a login wall it
  returns login inputs and still satisfies the literal shape
  of the criterion, so the name rule is the whole check. If
  either window has no textbox named "Message", the run is
  FAIL before anything is sent.
- VISION 2 (outcome check): PASS iff both BENCH-TEST messages
  appear as bubbles in their threads. The script's V12 gates
  check this by DOM read after each send; the agent's VISION 2
  look at both threads once at the end is the independent
  confirmation. VISION 2 is one screen observe of the monitor
  holding ws2, which is eDP-2 on this laptop (monitor_box
  [2464, 902, 1920, 1200] in the CL1-SWEEP investigation;
  screen eDP-2, region [2464,902,1920,1200] in the CL1-MSG2
  log, improvements/worker-cl1msg2-log.md). Confirm live with
  `hyprctl -j monitors` before the run; if ws2 is on a
  different monitor that day, use that monitor and record it:

```
computer-use observe --screen eDP-2
```

  (monitor name from `hyprctl -j monitors`), which shows both
  tiled windows in one image, as the CL1-MSG log's screen
  observe did. One observe is one vision covering both
  threads. Two window observes would themselves be 2 visions
  for VISION 2 alone and break the budget, so they are not
  the method. The look is read-only: no key or type action
  follows it, so a screen observation is fine for looking
  (the section 9 guard binds key/type steps, not looks).
  Outcome scoring is by message in thread (M1),
  never by point-in-box.
- Overall: PASS iff both messages land. Any single failed step
  makes the run FAIL; the chain stops at the first failure.
  The script's outcome rule (main, script ~line 831) is PASS
  iff exactly 2 sent AND exactly 2 windows.
- Vision budget: total exactly 2 visions during the step-2
  run invocation. A vision is one agent read of an
  observation: one observe call whose image or text the agent
  reads, or one DOM harvest the agent reads. The 2 counted
  visions are VISION 1 (the script's one-shot DOM harvest per
  window, read by the agent) and VISION 2 (the one screen
  observe at the end). Step 0 and step 1 are pre-run
  preparation, outside the budget. The visual looks the
  runbook prescribes outside the run (the step-0 visual
  fallback search of both threads, the section 10 hand-check
  after a v12-timeout) are also outside the budget, but they
  must be recorded in the run log as extra looks, so the
  total is auditable. The script records visions_used: 2 in
  results.json, but that value is a hardcoded constant
  (script line 745, in the results dict literal), never
  updated by the script; it reads 2 no matter how many looks
  the operator took. Do not cite it as a measured count; the
  operator's look count comes from the run log. Do not take
  extra visual looks during the run; every intermediate check
  is a DOM read.
- Accuracy bar: 90% or more (coordinator's bar, click2 log
  line 32). With 2 sends, 2/2 = 100% passes and 1/2 = 50%
  fails the bar, so in practice PASS requires both messages.
  There is no partial pass. Precision note: the coordinator's
  bar is about grounding accuracy per action ("one vision
  must drive max actions at accuracy >= 90%"), while this
  runbook operationalizes it as message-delivery rate (2/2
  messages landed). With 2 sends only 100% or 50% is
  possible, so the bar cannot distinguish 90% grounding
  accuracy from 100%. The criterion as stated measures
  delivery, not grounding accuracy.
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
  was window-scoped. scripts/first_action.py (after-capture
  at lines 875-892 at todolist-push tip 65a2df6, 22/11;
  the investigation cites ~line 656 at commit 5f5a2fd)
  captures the after with
  `cu.observe_screen(env, args.screen, max_width=1920,
  persist=True)` and never consults the input observation's
  scope. desktop_act (scripts/cu.py lines 2235-2244 at
  current tip; _after_capture def at 2235, result['after']
  stored at 2241; the investigation cites 2083-2091 at commit
  5f5a2fd) already captures a scope-matching after in
  result['after'] (`observe_screen(...) if screen_scope else
  observe(...)`, note the code calls `observe`, not
  `observe_window`), but first_action.py never copies it into
  the envelope.
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
- The gate (scripts/cu.py desktop_act, lines 1773-1775 at
  todolist-push tip 65a2df6, 22/11, the G28 rule; screen_scope
  at 1773, raise at 1775; the line moved from 1649 when
  AMEND4 item 3, commit 62b740e, shifted cu.py by 18 lines,
  and later work shifted it again, and the investigation
  cites the pre-shift line 1649): `screen_scope =
  meta.get('scope') == 'screen'`;
  if screen_scope and any action is type key or type, raise
  ValueError('screen observations support pointer actions
  only; use a window or accessibility target for typing').
  The raise happens in desktop_act's preflight, before
  coordinate validation and before any action runs:
  fail-closed, 998 ms, nothing typed or sent. But it is not
  before all side effects: the overlay acquire and session
  attempt happen first (998 ms wasted), which is why the
  investigation recommends moving the scope check earlier (a
  scope assertion in first_action.py before the overlay step
  would fail faster and cheaper). That earlier check now
  exists: AMEND4 item 12 added it in first_action.py lines
  600-624 (comment at 600: "the scope check runs BEFORE the
  overlay"), refusing a key/type batch given a screen-scope
  observation with return 1 before the overlay acquire and
  the session attempt. So the 998 ms waste no longer occurs
  on the key/type path; the G28 raise in desktop_act is the
  second line of defence, not the first.
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
   assert the scope. The observation JSON lives under
   ~/.cache/agent-computer-use/<id>.json (STATE in
   scripts/cu.py line 30, XDG_CACHE_HOME or ~/.cache; the
   observe command prints the observation id, which is the
   <id> in the path, matching the investigation's evidence
   paths). If scope is "screen", re-observe the window
   first; do not proceed:

```
python3 -c "import json,sys; m=json.load(open(sys.argv[1])); assert m.get('scope') in ('window','accessibility'), m.get('scope')" ~/.cache/agent-computer-use/<id>.json
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

Dated correction, 22/11 (AMEND4 item 12 landed after this
runbook was written): the code fix that removes the trap at
the source IS built now, on todolist-push (commit cbab398,
06:46 22/11). The envelope now carries BOTH captures
(scripts/first_action.py at todolist-push tip 65a2df6):
`after` is the scope-matching capture, chainable (the next
act-now may reuse it as its observation), built by
_scope_after (def at line 337, docstring names AMEND4 item
12) and stored in envelope['after'] at line 890; it prefers
the action result's after (desktop_act already captures in
the input scope) and otherwise takes a fresh capture in the
input observation's scope. `after_screen` is the
full-monitor capture, for verification ONLY, documented
non-chainable (stored at lines 880-883, from the
observe_screen call at 878), and reusing a screen-scope
after-image for a key/type step still always fails
(CL1-SWEEP). The scope check now also fires before the
overlay (first_action.py lines 600-624, see the gate bullet
above), so a key/type batch given a screen-scope
observation is refused with return 1 before the overlay
acquire and the session attempt. One residual is recorded
in the _scope_after docstring itself: a scope-less meta
WITH a window is treated as window scope (TESTREPAIR item
12 residual), so an old observation without a scope field
still gets a window capture.
Caveat that keeps the guard necessary: item 12 is on
todolist-push, not necessarily installed on the laptop.
The run machine runs pre-amend code if a baseline is still
owed, so on the laptop as it stands today the trap is still
live and the guard in this section is still mandatory.
Record which code version the laptop actually runs before
any manual step: if it runs pre-amend code, the guard is
the only protection; if it runs post-item-12 code, the
envelope's `after` is chainable and `after_screen` is not,
and the hard rule still stands for `after_screen` (never
reuse it as an --observation for a key/type step).
Item 12 of the AMEND4 re-verification (batch 10 task 2)
covers the code side: act-now after-scope mismatch, envelope
after always screen-scoped, fix returns the scope-matching
chainable after and after_screen for verify only, scope check
before overlay. The AMEND4 driver log on todolist-push
records item 12 as landed (cbab398); the four regression
tests for it are in tests/test_first_action.py, failing-first
on the old code per the DOT 9 task 1 council review
(docs/clone2-council-round3-amend4-20261122.md).

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
- If the harvest-first step fails (no textbox named
  "Message" in either window, login wall instead of a
  message input), STOP before any send. Note the harvest
  cannot check the thread container; a wrong thread or
  bubble selector is caught only by the first V12 gate,
  after typing (v12-timeout, see the stop rule above).
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
  (PASS/FAIL), per-step statuses, visions_used as recorded in
  results.json (hardcoded 2, script line 745, not a measured
  count), plus the operator's own look count from the run log
  (<run-dir>/run-log.md, named here so the count is
  auditable; every look outside the run, including the
  step-0 visual fallback search and any section-10
  hand-check, must be logged there with its time), and which
  intents are sent vs failed-unverified.
- Never edit a result file after the run.
- Confirm no Firefox process was left running and /tmp has
  room again.

## 12. What is still missing or unimplemented

Consolidated, so nobody mistakes this runbook for readiness.
A live run cannot pass until these are closed or the
coordinator explicitly accepts them. Status as of 22/11,
after the batch 11 task 2 closeout (see
docs/clone2-live-run-readiness-closeout-20261122.md):
CLOSED items are marked so; OPEN items name their owner.

CLOSED by the closeout (doc fixes, verified against the
current todolist-push tip 65a2df6):
- Section 9 corrected for AMEND4 item 12 (cbab398): the
  code fix IS built on todolist-push, `after` is
  scope-matching and chainable, `after_screen` is
  verification only, the scope check fires before the
  overlay (first_action.py lines 600-624). The guard stays
  mandatory on pre-amend code; record which code version
  the laptop runs.
- Checklist 10 contradictions fixed in the workflow doc
  (login-wall mode, harvest selector checking, "ONE Zen
  instance", ledger rationale). The runbook and the
  checklist now agree.
- Checklist 10.3 now complete as a definition: method
  (a11y query with the AT-SPI pid from `a11y apps`),
  generation rule (fresh timestamp-based run_id), record
  requirement (run log). The dry probe procedure is
  written in section 5; the probe itself is UNRUN (open
  item below).
- VISION 2 monitor named (eDP-2, expected; confirm live
  with `hyprctl -j monitors`) and the run log file named
  (<run-dir>/run-log.md, every look logged with its time).

OPEN, still blocking a live run:
1. Live shape decision (coordinator): option B (primary,
   CDP driver to the real Brave/Chrome chats on ws2) or
   option A (fallback, script's Firefox with a pre-seeded
   logged-in profile). Both procedures are written in full
   in section 13. No live run until the coordinator picks
   one. Whichever is picked, the account holding the two
   threads is still undecided in any repo record.
2. If option B: the CDP driver build. Building blocks
   exist (scripts/cdp.mjs, a CDP transport with
   Runtime.evaluate, DOM.getBoxModel and harvest, used by
   `computer-use browser observe/act`; scripts/
   chromium_cli.py, tab listing over DevTools HTTP), but
   no wiring from tests/two_vision_bench.py to cdp.mjs
   exists, the script is Marionette-only today, and the
   user's own Brave/Chrome sessions run without a remote
   debugging port (verified 2026-11-18 for Chromium: no
   DevToolsActivePort file, nothing listening on 9222), so
   no CDP client can attach to them as they run today.
   Attaching needs the browsers relaunched with a debug
   port (coordinator decision) plus the driver build. The
   CDP input path on the Messenger contenteditable input
   is also UNVERIFIED and needs a dry send first.
3. If option A: a verified pre-seeded logged-in profile
   (log in once manually, verify both threads load,
   re-verify before each run; sessions expire). No such
   profile exists yet, and the account is undecided.
4. Dry probe of the a11y freshness method (section 5):
   UNRUN. Premise A (Messenger bubbles exposed through
   the a11y tree on Brave/Chrome) is UNVERIFIED; premise
   B (hyprctl pid is the AT-SPI pid) is contradicted by
   prior evidence. Run the two-part probe on the laptop
   before the first live run.
5. Live Messenger input name verified against the real
   DOM: the aria-label is UNKNOWN, no DOM or a11y read of
   the input exists in the repo. Read it live before the
   run (section 6 rule for a non-"Message" name: stop,
   record the actual name).
6. Method approval: the live run is gated on it (workflow
   doc header; CL1-SWEEP investigation caveat). The live
   run is the coordinator's acceptance test, not the
   operator's call.
7. Thread URLs, thread selector, and bubble selector:
   must come from the coordinator for the live threads.
   The script cannot invent them.
8. textNew in the V12 gate: NOT built. The gate is a
   presence check only; a stale bubble passes it. VISION 2
   removal is conditional on textNew being built and proven
   plus a cross-window check.
9. Pre-send reservation (exactly-once across a process
   death between send and ledger mark): OPEN work, in the
   design doc section 7 and as a TODO in the script's Ledger
   docstring. The failed-unverified retry block closes only
   the narrower v12-timeout case.
10. V11 MutationObserver flag: NOT built. The fixture counts
    input events in window.__inputEvents; a Messenger page
    needs a real observer armed before typing.
11. D3, ref stability on a mutating page: unaddressed
    (design doc section 7). The live threads are live chats
    that can mutate mid-run if the other clone or the owner
    sends a message between harvest and send. The HCU guard
    re-reads live geometry before input, so this is likely
    fail-closed, but no stale-ref fail-fast exists; the short
    chain and the guard are the mitigation, not a fix.

Standing pre-run checks (not closable in advance, checked
at run time):
- Live lane must be free: no BASELINE2 or other live run
  running, and no other agent holding the laptop browser.
  The installed laptop code must still be the pre-amend
  code if a baseline is still owed.
- Live measurement of the 90% accuracy bar: no live
  measurement exists yet. Synthetic grounding is 7/7 =
  100%; the live proof is owed, and the run itself must
  produce it. This is measured by the run, not a
  prerequisite to start.

NOT missing, to avoid confusion: the C12 adjudication does
NOT apply to this script's clicks and is NOT a prerequisite
(workflow doc section 9: clicks use getBoundingClientRect
viewport coordinates directly). C12 applies only to a future
Zen-attached variant whose clicks go through the conversion
layer.

## 13. Live-shape options: how the script reaches the real chats

The gap: under G3 the live threads are in Brave (clone1)
and Chrome (clone2) on ws2, and the script drives only its
own fresh headless Firefox. No procedure with the current
script can reach those threads. The coordinator decides
the live shape; both options below are prepared in full
so the decision can be made on complete procedures, not
on summaries. Rung 2 acceptance still runs on the real
clone chats on ws2, NOT the Firefox fixture, under either
option.

### 13.1 Option B (primary): CDP driver to the real Brave/Chrome chats

Keeps G3. The script gains a CDP driver and drives the
live Brave/Chrome windows directly, using the Messenger
sessions that are already logged in there. No login step,
no profile copy.

What exists today (verified 22/11):
- scripts/cdp.mjs exists on main and todolist-push: a
  dependency-free CDP adapter (Node >=22) with
  Runtime.evaluate, DOM.getBoxModel cross-check, and a
  harvest/snapshot that returns rects for every actionable
  element. It is the transport behind `computer-use browser
  observe/act`.
- scripts/chromium_cli.py exists on main and todolist-push:
  a repo-owned Chromium CLI wrapper that lists tabs over
  the DevTools HTTP endpoints (default http://127.0.0.1:9223,
  the agent-managed Chromium).
- The one-vision design doc already maps the harvest and
  gate onto CDP calls (DOM.getBoxModel,
  Accessibility.getFullAXTree) in principle.

What does NOT exist, and blocks this option:
1. No wiring from tests/two_vision_bench.py to cdp.mjs.
   The script is Marionette-only; nothing in it speaks
   CDP. The driver build must implement, at minimum: a
   harvest equivalent (cdp.mjs harvest), a send chain
   (click/type via CDP Input or Runtime.evaluate), and
   the V12 gate (Runtime.evaluate for the bubble check),
   reusing the ledger and the outcome rule.
2. The user's own Brave/Chrome sessions cannot be
   attached to as they run today. The user's own Chromium
   runs WITHOUT a remote debugging port (verified
   2026-11-18: no DevToolsActivePort file, nothing
   listening on 9222), so no CDP client can attach to
   his session. Attaching needs Brave and Chrome
   relaunched with a debug port, which changes the live
   sessions and is a coordinator decision.
3. The CDP input path on the Messenger contenteditable
   input is UNVERIFIED. The computer-use TYPE action
   silently fails on this exact input in Brave
   (CL1-MSG2: 9/9 executed, input stayed empty), and
   while CDP Input is a different path from wtype, the
   same input has already swallowed one synthetic input
   path. A dry send through the CDP driver must prove
   typing lands before any live run uses it.

Procedure, once the build lands and the browsers are
relaunched with a debug port:
1. Coordinator decides option B and the debug-port
   relaunch; record the endpoint (port) per browser.
2. Verify attach: list tabs via chromium_cli.py for each
   browser and confirm the two thread tabs are visible.
3. Run the dry probe: harvest both threads through the
   CDP driver, confirm both inputs visible and named
   per the live DOM name (section 6), then a dry send
   of a bench string into one thread and a V12 gate
   check, proving the CDP input path works.
4. Coordinator supplies the plan (thread URLs, thread
   selector, bubble selector) for the two live threads.
5. Run steps 0, 1, 2 per this runbook, with the CDP
   driver in place of launch_browser. The harvest-first
   step is the live check that the sessions work.

### 13.2 Option A (fallback): script's Firefox with a pre-seeded logged-in profile

Abandons G3's Brave/Chrome. The live run uses the
script's own Firefox, two windows, one Messenger account,
two threads (the two clones' threads under one account).
Which account holds the two threads is a coordinator
decision, still unmade in any repo record.

Procedure:
1. Coordinator decides option A and names the account.
2. On the run machine, launch the run machine's own
   Firefox binary with a fresh profile, log into
   Messenger manually once with that account, quit, and
   preserve the profile directory. Use the laptop's
   Firefox, not the script's hardcoded path
   (/home/hatch/workspace/tools/firefox/firefox, this
   VM's path, script lines 49-50); record the laptop
   binary path live. The profile holds a live session:
   local only, never push it to the repo, never copy it
   into any shared artifact.
3. Verify the profile: launch Firefox with it and confirm
   both threads load. Sessions expire; re-verify before
   each run.
4. Before the run, copy the profile into <run-dir>/profile,
   excluding cache (the Cache directory): /tmp is a 512M
   tmpfs and a full profile copy could exceed it.
   launch_browser does makedirs with exist_ok and launches
   with -profile <profile>, so a pre-seeded profile is
   used as-is.
5. Coordinator supplies the plan (thread URLs, thread
   selector, bubble selector) for that account's two
   threads.
6. Run steps 0, 1, 2 per the runbook. The harvest-first
   step is the live check that the session works, but it
   cannot rely on the "Message" name until the live DOM
   name verification (section 6) is closed: until then a
   harvest showing no "Message" input is ambiguous (login
   wall versus a differently-named input) and the run
   must stop, not proceed. Once the name is DOM-verified
   live, Message inputs visible means logged in; a login
   wall means the session is dead, stop.
7. After the run, delete the profile copy from /tmp (512M
   tmpfs), keep the master profile local for re-runs.

Option C (not a procedure, listed so the choice is
explicit): move the threads to Zen and build an attach
mode (Zen relaunched with -marionette, geckodriver
--connect-existing, proven on the Firefox stand-in in
batch 1). Requires the script to gain an attach mode and
the coordinator to relaunch Zen on the laptop.

## 14. Sources

- Batch 10 assignment: coord/clone2.md line 868, commit
  422f4b0.
- Batch 11 task 2 closeout: docs/
  clone2-live-run-readiness-closeout-20261122.md (verdict
  still NOT READY, exact remaining items listed there and
  in section 12 above).
- Script: tests/two_vision_bench.py (868 lines, c267411);
  FF/GD lines 49-50; default_plan run_id lines 543-544;
  normalize_file_url ~line 587; validate_plan ~line 600;
  URL gate ~lines 724-740; outcome rule ~line 831;
  launch_browser lines 265-296; find_input lines 254-262;
  no-message-input-in-inventory line 794; visions_used
  hardcoded at line 745.
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
- run_id freshness check: scripts/a11y.py lines 118-140
  (query, case-insensitive name substring, bounded observe,
  CU_PICK4_FASTPATH=1 required); scripts/a11y.py lines
  57-60 (app, exact app PID required); scripts/cu.py line
  2906 (a11y subparser), lines 3150-3151 (query requires
  --pid plus --name or --role); scripts/cu.py line 30 (STATE,
  ~/.cache/agent-computer-use).
- Operator-guard code pins (todolist-push tip 65a2df6,
  22/11; line numbers drift as the coordinator's lane
  lands commits, re-verify before citing): scripts/cu.py
  lines 1773-1775 (G28 raise), lines 2235-2244
  (scope-matching _after_capture, result['after'] at 2241);
  scripts/first_action.py line 337 (_scope_after def),
  lines 600-624 (scope check before the overlay),
  lines 875-892 (after-capture: observe_screen at 878,
  envelope['after_screen'] at 880-883, envelope['after']
  at 890).
- CDP building blocks for option B: scripts/cdp.mjs
  (dependency-free CDP adapter, Runtime.evaluate,
  DOM.getBoxModel, harvest/snapshot); scripts/
  chromium_cli.py (tab listing over DevTools HTTP,
  default http://127.0.0.1:9223).
- VISION 2 monitor: improvements/worker-cl1msg2-log.md
  (screen eDP-2, region [2464,902,1920,1200]).
