# 2-vision benchmark workflow

Date: 2026-11-22. Status: script + workflow BUILT ONLY, no live run yet.
This benchmark is an acceptance test. It runs live ONLY after the
improved method is approved and the coordinator says run.

## 1. What it is

The combined design from improvements/worker-coord-click2-log.md
("The combined design"), as an executable script:
tests/two_vision_bench.py, with the dry-test fixture
tests/two_vision_fixture.html.

- VISION 1 builds the inventory: one-shot bulk DOM harvest per clone
  window (one evaluate per window, ref, role, name, rect, center,
  visibility, focused for every input + button), formatted as numbered
  compact text (Mantis pattern). VISION 1 is a DOM harvest, NOT a
  screenshot.
- Plan-once: the whole send sequence (click clone1 input, type, Enter,
  click clone2 input, type, Enter) is emitted as one program from the
  inventory.
- Guarded execution: HCU-style live guard re-checks each target's live
  geometry + focus right before input; stop at first failure, rest
  reported not-executed; exactly-once intent per send (ledger +
  V12 pre-check). The honest form of the exactly-once claim: a retry
  never re-sends a message the V12 pre-check can SEE in the thread.
  After a v12-timeout the same intent is never re-attempted, because
  the message may have landed unseen (the selectors are the only
  witness and they just failed to see it); the run marks the intent
  failed-unverified and a later run with the same intent refuses to
  re-send it. V12 finish gate after each send (sent bubble in the
  thread DOM).
- Scoring is by OUTCOME (message in the thread or not, M1), never by
  point-in-box. PASS iff both messages land in their threads.
- Total: exactly 2 visions. VISION 1 is the inventory read; VISION 2
  is the agent looking at both threads once at the end to confirm both
  bubbles. Everything between them is cheap DOM reads, zero extra
  observes. The script's V12 gates are the same outcome check done by
  DOM read.

## 2. Safety rules (read before any run)

- NEVER run live without the coordinator saying run. The script
  refuses live mode unless BOTH --live and --confirm-live are given,
  and the gate is on the plan URLs, not the flag: any plan URL
  outside the local fixture files under tests/ refuses without both
  flags, so a custom --plan cannot smuggle a live run past the gate.
  --confirm-live is only passed when the coordinator approved the run.
- --instances two is refused: the run always uses one browser
  instance with two windows under option A (the script's
  Firefox), and recording "two" in results would lie about
  what ran. Two instances are not implemented yet. Under
  option B (CDP driver to Brave/Chrome on ws2) the run uses
  two browsers, not one instance; see runbook section 13.
- NEVER type into a real thread in fixture mode. Fixture mode (the
  default) only opens tests/two_vision_fixture.html in headless
  Firefox on this VM.
- The live lane must be free (no BASELINE2 or other live run), and
  the installed laptop code must still be the pre-amend code if a
  baseline is still owed. Check with the coordinator first.
- No personal information in any plan, inventory, ledger, log, or
  result file. Test messages are bench strings only
  ("BENCH-TEST ..."), never real user text.
- No em dash or en dash in any file this workflow produces.

## 3. Prerequisites

- Headless Firefox 160.0.1 at ~/workspace/tools/firefox/firefox,
  geckodriver 0.37.1 at ~/workspace/tools/geckodriver, venv with
  Selenium 4.53 at ~/workspace/tools/venv. Run with
  ~/workspace/tools/venv/bin/python.
- One active remote session per browser instance (Firefox 160 rule,
  proved in batch 7 task 2): this script uses Marionette only and
  never opens a BiDi session while Marionette is active.

## 4. Files

- tests/two_vision_bench.py: the benchmark script (1939 lines after
  the batch 12 task 2 fix pass 2, commit 00ce862; first built in
  commit 072e060, fixes 9196744, fix pass 7e81213, plan
  validation 9a15647, pre-send reservation TODO c267411,
  textNew + reservation + V11 + D3 + frames census + strict
  input name f49851f, exactly-once fix pass c1b623b, fix
  pass 2 exactly-once holes 00ce862).
- tests/two_vision_fixture.html: local chat fixture. One page per
  clone (?clone=1, ?clone=2). A message input, a Send button, a
  thread div. Enter or Send appends a bubble with the typed text.
  Also a Search input and an Emoji button so the harvest is not
  trivial (4 inputs + buttons per window).
- Variant fixtures for the fix-pass tests (same page shape, one
  difference each): tests/two_vision_fixture_ce.html (message input
  is a contenteditable div, the Messenger input type),
  tests/two_vision_fixture_noid.html (message input has no id),
  tests/two_vision_fixture_belowfold.html (a 1500 px spacer above
  the input, so it sits below the fold),
  tests/two_vision_fixture_ce_nosend.html (contenteditable input,
  Enter is a no-op: typing mutates, no bubble),
  tests/two_vision_fixture_double.html (one Enter appends two
  identical bubbles),
  tests/two_vision_fixture_delayed_double.html (one Enter appends
  one bubble now and an identical second bubble 700 ms later;
  fix pass 2, the gate must settle a full second).
- Variant fixtures for the batch 12 task 2 tests:
  tests/two_vision_fixture_stale.html (a stale bubble carrying the
  fixed test message is seeded at load, one per clone),
  tests/two_vision_fixture_nosend.html (same stale seed, but Enter
  never appends a bubble), tests/two_vision_fixture_iframe.html
  (same-origin iframe holding its own message input, which the
  top-frame harvest must NOT list) plus
  tests/two_vision_fixture_frame.html (the iframe page).
- tests/two_vision_once_driver.py: exactly-once driver test. Calls
  send_one twice with the same intent in one browser session and
  records both calls plus the bubble count.
- tests/two_vision_b12t2_driver.py: batch 12 task 2 driver test.
  D3 ref-stale (rename the input, send_one must fail fast),
  cross-window check (inject a foreign bubble, the check must
  report it), pre-send reservation (seed status "sending", send_one
  must refuse with retry-blocked-reservation, with and without a
  visible bubble).
- tests/two_vision_fixpass_driver.py: fix-pass driver test, 19
  tests, all fixture only. F1 failed retry keeps a "sent" record,
  F2 zero-send runs score FAIL, F3 fresh-workdir run_id reuse is
  REFUSED, F5 double append fails duplicate-bubble, F6 tag swap
  and F8 placeholder rename fail D3, F7 moved input fails the HCU
  guard, F9 contenteditable typing with a no-op Enter times out
  with v11_mutations 0, F10 prefixed foreign bubble counts,
  F11 identical messages refused, C1-2 broken thread selector
  fails thread-missing. Fix pass 2 adds: harvest-then-run with
  the same run_id in different workdirs succeeds (registry binds
  only in run mode), a "sent" intent with no visible bubble
  refuses instead of re-sending, a changed message under the
  same run_id refuses with the original message kept in the
  ledger, a delayed double append fails duplicate-bubble after
  the 1.0 s settle, results.json records the registry state,
  substring messages are refused by validate_plan, a no-send
  run's outcome_note names the failure, and corrupt registry
  and ledger files are REFUSED with exit 2.
- Workdir (default /tmp/two_vision_bench, shared by runs unless
  --workdir is passed): inventory.json, ledger.json, results.json,
  profile/ (Firefox profile, delete after the run; /tmp is a 512M
  tmpfs and fills up fast). Pass a separate --workdir per run to
  keep each run's artifacts apart.

## 5. Step by step

### Step 0. Write the plan JSON (live runs only)

Fixture mode builds its own plan (unique run_id, BENCH-TEST
messages). A live plan looks like this:

```json
{
  "run_id": "bench-20261122-001",
  "windows": [
    {"label": "clone1", "url": "<thread 1 URL>",
     "input_name": "Message", "thread_selector": "<thread container>",
     "bubble_selector": "<sent bubble selector>"},
    {"label": "clone2", "url": "<thread 2 URL>",
     "input_name": "Message", "thread_selector": "<thread container>",
     "bubble_selector": "<sent bubble selector>"}
  ],
  "messages": {
    "clone1": "BENCH-TEST clone1 bench-20261122-001",
    "clone2": "BENCH-TEST clone2 bench-20261122-001"
  },
  "timeouts": {"v12_gate_s": 5}
}
```

- run_id must be unique per run. Freshness comes from
  generating a fresh timestamp-based run_id, not from the
  ledger. Since the batch 12 fix pass the script enforces
  freshness two ways: the shared run registry refuses a
  run_id bound to a different ledger path before the
  browser starts (a reused run_id in a fresh workdir is
  REFUSED, exit 2), and a same-workdir retry that only
  skips already-sent intents scores FAIL with zero sends
  this run unless --allow-resume is passed. The V12
  pre-check skips only when the ledger says the intent
  was already sent AND the bubble is visible; with a fresh
  workdir the ledger is empty, so a reused run_id would
  send a second identical bubble instead of skipping,
  which is why the registry refuses it. Since fix pass 2
  a recorded "sent" intent whose bubble is absent refuses
  with retry-blocked-sent-bubble-absent instead of
  re-sending, and a changed plan under the same run_id
  refuses with retry-blocked-intent-changed. The ledger keys
  intents by run_id within one workdir only. Since batch
  12 task 2 the V12 gate is a textNew gate: it passes only
  on exactly one NEW bubble past the pre-Enter
  gate_baseline, so a stale bubble alone can no longer pass
  a new send (see the batch 12 task 2 runs in section 7),
  and a double append fails as duplicate-bubble. The gate
  is appearance-based, not causal. The run_id freshness
  check is still required as the human backstop: the
  registry is per-machine, so a run_id first used on
  another machine is not refused.
- input_name is matched against the harvested textbox names; the first
  visible textbox is the fallback.
- thread_selector must point at the thread container. bubble_selector
  defaults to ".bubble, [data-sender]"; override it for Messenger.
  A wrong thread_selector fails the V12 gate loudly (the gate honors
  the selector; there is no fixture-helper shortcut). The gate also
  requires exact textContent === text, and the default bubble
  selector is fixture-shaped: a Messenger bubble's textContent may
  not equal the message exactly, so the default would fail closed
  live and a live plan MUST override bubble_selector.

### Step 1. VISION 1, harvest only (optional, recommended)

```sh
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --fixture --mode harvest --print-inventory \
  --workdir /tmp/two_vision_bench/runH
```

Writes inventory.json and prints the numbered compact text, for
example:

```
Window clone1: 4 inputs+buttons
[1] textbox 'Message' ref=#msg-input rect=(20,238,340x39) center=(190,257) visible=True focused=False
[2] button 'Send' ref=#send-btn rect=(364,238,59x39) center=(394,257) visible=True focused=False
```

The agent reads this text (VISION 1), picks the two message inputs,
and checks the refs, rects, and visibility before the run. Refs are
valid only within this inventory (gap D3): they are derived from the
live DOM of this run and must not transfer between runs.

### Step 2. Run the send chain

```sh
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --fixture --workdir /tmp/two_vision_bench/run1
```

For a live run (coordinator approval only):

```sh
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --live --confirm-live --plan /tmp/plan-live.json \
  --workdir /tmp/two_vision_bench/live1
```

Without --confirm-live the script refuses with exit code 2 and sends
nothing. The same refusal applies to a custom --plan whose URLs are
not the local fixture files: the gate is on the URLs, not the flag,
so --plan alone can never start a live run.

To reuse a saved inventory instead of harvesting again:

```sh
--inventory-in /tmp/two_vision_bench/runH/inventory.json
```

### Step 3. Read the results

- results.json: run_id, mode, live flag, outcome (PASS, FAIL, or
  HARVEST-ONLY), wall_s, and one record per step: window, intent_id,
  status (sent, skipped-already-sent, failed, not-executed),
  elapsed_s, error reason, v1_value_ok, v11_input_events,
  v11_mutations, v11_mutation_flag, before_count, gate_baseline,
  gate_count, reservation, v12_gate_ok. Plus before_counts and
  cross_window_check (each thread's own count and foreign counts)
  and frames (iframe census per window) at the top level.
  An outcome of PASS now also requires no cross-window
  contamination.
- STDOUT is JSONL, one line per step: wall clock (UTC) and elapsed
  seconds from a monotonic clock.
- Exit code: 0 PASS, 1 FAIL (benchmark outcome), 2 harness error or
  refused live run.
- VISION 2: look at both threads once and confirm both bubbles.
  The script's V12 gates already checked the same thing by DOM read;
  the agent's look is the independent outcome confirmation.

## 6. What each failure means

| Step status / error | Meaning |
| --- | --- |
| no-message-input-in-inventory | No visible textbox in a window's harvest. The program cannot be built; nothing is sent (fail-closed). |
| target-gone | The input vanished between inventory and guard. |
| not-visible / covered | V5 hit test failed: the rect center does not hit the input, or it is hidden. |
| geometry-moved | The input moved more than 2 px from the VISION 1 snapshot. The inventory is stale; re-harvest. |
| focus-failed | The click landed but activeElement is not the input. Nothing was typed. |
| value-mismatch | V1 readback: the field does not hold the typed text. Enter was not sent. For inputs and textareas the check reads value; for contenteditable elements it reads innerText (a div has no value property). |
| v12-timeout | No NEW bubble in the thread DOM within the gate timeout (textNew: the count must grow past the pre-Enter baseline; a stale bubble with the exact text does not pass). The message may still have been typed (check the thread); the run is FAIL and the ledger marks the intent failed-unverified. A retry of the same intent is REFUSED (see retry-blocked-unverified below): the message may have landed unseen. |
| retry-blocked-unverified | A later run with the same intent id found the ledger marked failed-unverified (a previous v12-timeout). Nothing is typed or sent. Fix the thread/bubble selectors and use a new run_id after manually checking the thread. |
| retry-blocked-reservation | A later run with the same intent id found the ledger marked "sending": a previous attempt wrote the pre-send reservation and never reconciled it (the process died between Enter and the ledger mark). Nothing is typed or sent. Check the thread by hand and use a new run_id; do not re-send the same intent. |
| ref-stale | The harvested input was renamed or replaced between harvest and send (tag, role, name, aria-label or placeholder changed). Nothing was clicked or typed. Re-harvest with a fresh run_id; the step record lists the nearest live textboxes. |
| input-name-mismatch | --strict-input-name is set and the picked input's name does not contain the plan's input_name. Nothing was typed or sent, and no ledger record was written. Fix the plan's input_name (rung 2 procedure, runbook section 14). |
| cross-window-contamination | After both sends, a thread holds the other window's message. The run is FAIL even when both sends report sent. Report which thread holds the foreign message; do not re-send to "make up" for it. |
| not-executed | A later step after a failure. The chain stopped at the first failure (Anthropic batch loop contract). |

## 7. Dry-test results (measured on this VM, headless Firefox 160.0.1)

Wall clock is UTC, elapsed from a monotonic clock. All runs used the
repo venv python. Fixture: 4 inputs + buttons per window.

- Happy path, 2 windows (final run, 2026-11-21T20:25:12Z to
  20:25:19Z): PASS, wall 6.1839 s total. Browser launch 1.0137 s,
  Marionette attach 2.7903 s, harvest 0.0883 s (clone1) and 0.0863 s
  (clone2) for 4 elements each, sends 0.7071 s (clone1) and 0.4448 s
  (clone2). Both V12 gates passed. Full log:
  /tmp/two_vision_bench/final.log, results in
  /tmp/two_vision_bench/final/results.json. (An earlier happy-path
  run, run1b, gave the same PASS with wall 6.2165 s and sends
  0.86 s / 0.39 s.) The original /tmp logs for these runs were lost
  when /tmp was wiped on 2026-11-22; the fix-pass re-runs below are
  preserved in ~/workspace/tools/two_vision_fixpass/ instead.
- Exactly-once (driver test tests/two_vision_once_driver.py, same
  intent twice in one browser session, run once2): first call "sent"
  in 0.5988 s, 1 bubble; second call "skipped-already-sent" in
  0.0153 s, still 1 bubble. PASS, wall 4.9248 s. Log, results.json,
  and ledger.json preserved in
  ~/workspace/tools/two_vision_fixpass/ (once2.log,
  once2.results.json, once2.ledger.json). The ledger holds one
  intent, bench-once-20261122:clone1, status sent, note
  bubble-already-present. The earlier 0.0026 s figure is WITHDRAWN:
  it had no preserved artifact and did not reproduce (council 1
  measured 0.0549 s for the second send on its own driver test).
  The old /tmp/two_vision_bench/once/ ledger is also withdrawn as
  evidence: it holds two DIFFERENT intent ids with two different
  message texts (two separate script runs, each with a fresh
  run_id), not the same intent twice.
- Stop-at-first-failure, 3-window plan with a wrong thread selector
  for clone2 (run3b, 2026-11-21T20:23:16Z to 20:23:27Z): FAIL as
  designed, wall 11.0567 s. Clone1 sent (0.69 s), clone2 failed
  v12-timeout after the 3 s gate (its message was typed into the
  fixture but the gate could not see it through the wrong selector),
  clone3 not-executed.
- Harvest-only (runH, 2026-11-21T20:23:38Z to 20:23:43Z):
  HARVEST-ONLY, wall 5.0420 s, 4 elements per window.
- Live refusal: --live without --confirm-live exits 2 and sends
  nothing (verified, no browser started).

Bugs found by the dry tests and fixed in the script (commit
9196744): (1) the harvest/verify/gate JS had no top-level return, so
Marionette returned None; (2) Ledger crashed when its workdir did
not exist yet; (3) the V12 gate used a fixture helper that ignored
the plan's thread selector, so a wrong selector passed silently;
(4) the exactly-once pre-check only ran when the ledger said sent,
so a retry after a failed gate could double-send; it now runs the
V12 pre-check before every send regardless of ledger status.

Fix pass (commit 7e81213), council 1 and 2 ISSUES plus redteam
BROKEN, all fixed and re-measured on this VM, headless Firefox
160.0.1, repo venv python. Every log, results.json, ledger.json,
and inventory.json is preserved in
~/workspace/tools/two_vision_fixpass/ (the /tmp workdirs from the
first fix-pass runs were lost when /tmp was wiped mid-task, so all
runs below were re-run and their artifacts copied out of /tmp
immediately):

- Happy path re-run (fix2): PASS, wall 8.4457 s. Browser launch
  3.5212 s (contended VM), Marionette attach 2.7635 s, harvest
  0.0225 s (clone1) and 0.0089 s (clone2) for 4 elements each, sends
  0.3717 s (clone1) and 0.5410 s (clone2). Both V12 gates passed.
- Contenteditable input (fix2-ce, fixture
  two_vision_fixture_ce.html): PASS, wall 6.6076 s, sends 0.5100 s
  and 0.2950 s. The V1 check now reads innerText for
  contenteditable elements; the redteam repro (FAIL
  value_check_failed, value null) no longer reproduces.
- Id-less input (fix2-noid, fixture
  two_vision_fixture_noid.html): PASS, wall 5.4565 s, sends 0.6510 s
  and 0.3963 s. The harvest ref for the id-less input is the valid
  CSS path
  "html:nth-of-type(1) > body:nth-of-type(1) > input:nth-of-type(1)";
  the redteam repro (harness_error, "not a valid selector", exit 2)
  no longer reproduces.
- Below-fold input (fix2-belowfold, fixture
  two_vision_fixture_belowfold.html, 1500 px spacer): PASS, wall
  5.4953 s, sends 0.7078 s and 0.4564 s. The send chain now scrolls
  first (ensure_visible) and guards on post-scroll geometry; the
  redteam repro (guard_failed "covered" in 0.018 s) no longer
  reproduces.
- Harvest-only re-run (fix2-harvest): HARVEST-ONLY, wall 4.3510 s.
- Stop-at-first-failure re-run (fix2-stop, 3-window plan, wrong
  thread selector for clone2): FAIL as designed, wall 9.2775 s.
  Clone1 sent, clone2 failed v12-timeout, clone3 not-executed.
- Wrong-selector retry (fix2-wrongsel, redteam runW repro, same
  plan and ledger twice): run 1 FAIL v12-timeout, ledger marks the
  intent failed-unverified; run 2 FAIL retry-blocked-unverified,
  nothing typed or sent, no second bubble. The double-send the
  redteam reproduced (2 identical bubbles) no longer happens.
- Plan-bypass refusal: a custom plan with a non-fixture URL and no
  --live flags is REFUSED with exit code 2 and sends nothing
  (bypass-refusal.log). The redteam repro (both messages sent,
  outcome PASS, live false) no longer reproduces.
- --instances two refusal: exit code 2, nothing recorded as "two"
  (instances2-refusal.log).
- Live refusal still holds: --live without --confirm-live exits 2
  and sends nothing (live-refusal.log).

Fixes in the script (commit 7e81213), all verified by the runs
above: (1) the live gate is on the plan URLs, not the flag; any URL
outside the local fixture files under tests/ refuses without both
--live and --confirm-live. (2) The V1 check reads innerText for
contenteditable elements and value otherwise. (3) Id-less elements
get a unique valid CSS path ref instead of the invalid
tag + '[' + i + ']' form. (4) The send chain scrolls first, then
guards on post-scroll geometry, and clicks at the guard-verified
center. (5) A v12-timeout marks the intent failed-unverified and a
later run with the same intent refuses to re-send it. (6)
--instances two is refused. (7) HARVEST_JS also inventories
[role="button"] and [role="textbox"] controls. (8) The dead
median() function is removed. (9) launch_browser refuses when the
Marionette/BiDi ports are already held by a stale browser, and
attach_driver retries the Selenium session creation. (10) All gaps
now have literal TODO comments in the script (D1, D2, D3, D4, D6,
F5, step-6 loop hygiene; D5 is closed by statement, VISION 1 is a
DOM harvest).

Re-run (batch 9 task 2, 2026-11-21T21:41:28Z to 21:42:33Z, same
machine, headless Firefox 160.0.1, repo venv python, one run per
case, each with its own --workdir under /tmp/two_vision_b9t2; all
logs, results.json, inventory.json, ledger.json and the six custom
plans preserved in ~/workspace/tools/two_vision_b9t2/, 41 files):

- Happy path (b9t2-happy): PASS, wall 8.9403 s. Launch 1.7713 s,
  attach 4.2165 s (slower than the 2.65 to 2.79 s recorded before;
  contended shared VM, same shape, not a defect), harvest 0.1055 s
  and 0.0171 s for 4 elements each, sends 0.8528 s and 0.4741 s.
  Both V12 gates passed.
- Harvest-only (b9t2-harvest): HARVEST-ONLY, wall 6.9131 s, 4
  elements per window.
- Contenteditable (b9t2-ce): PASS, wall 6.5993 s, sends 0.7269 s
  and 0.6163 s.
- Id-less (b9t2-noid): PASS, wall 6.4843 s, sends 0.7028 s and
  0.4735 s. The id-less input ref is the valid CSS path
  "html:nth-of-type(1) > body:nth-of-type(1) > input:nth-of-type(1)".
- Below-fold (b9t2-belowfold): PASS, wall 6.1782 s, sends 0.6145 s
  and 0.6186 s.
- Stop-at-first-failure (b9t2-stop, 3-window plan, wrong thread
  selector for clone2): FAIL as designed, wall 9.7904 s. Clone1
  sent, clone2 failed v12-timeout, clone3 not-executed.
- Wrong-selector retry (b9t2-wrongsel1 and b9t2-wrongsel2, same
  plan and ledger): run 1 FAIL, wall 8.2872 s, clone1 v12-timeout
  after the 3 s gate, ledger marks the intent failed-unverified;
  run 2 FAIL, wall 4.2119 s, clone1 retry-blocked-unverified in
  0.0083 s, nothing typed or sent, clone2 not-executed. No second
  bubble. Run 1's results.json was overwritten by run 2 (same
  workdir is the point of the test); run 1's outcome and wall are
  recorded in b9t2-wrongsel1.log and the ledger.
- Exactly-once driver (b9t2-once): PASS, wall 4.8139 s. Call 1
  sent in 0.6549 s, 1 bubble; call 2 skipped-already-sent in
  0.0511 s, still 1 bubble. The second-call time is consistent
  with council 1's independent 0.0549 s, not the withdrawn
  0.0026 s figure.
- Live refusal (b9t2-live-refusal): --live without --confirm-live
  exits 2, no browser started.
- --instances two refusal (b9t2-instances2): exit 2, nothing
  recorded as "two".
- Plan-bypass refusal (b9t2-bypass, custom plan with
  https://example.com URLs, no --live flags): exit 2, sends
  nothing, no browser started.

No drift found in this re-check: the script on main is still 783
lines, default workdir (/tmp/two_vision_bench), gate behavior,
contenteditable check, id-less refs, scroll-first guard, v12-timeout
retry block and --instances two refusal all match the code as read.
(The first sentence originally also cited this doc's own line count
as 379; the doc was 547 lines at commit e6ecdea, and the
self-referential count is dropped here because a doc stating its own
length goes stale on every edit. The task 2 agent's report also
stated 548 lines; the correct figure is 547. The script count is
also historical: the script is 868 lines after the batch 9 task 1
fix pass in commit c267411 (862 lines after the batch 9 task 2 fix
pass in commit 9a15647, plus a 6-line TODO comment); see the
fix-pass paragraph below.) The
preserved fix-pass numbers in this section recompute exactly from
~/workspace/tools/two_vision_fixpass/ (fix2 PASS 8.4457 s, fix2-ce
PASS 6.6076 s, fix2-noid PASS 5.4565 s, fix2-belowfold PASS
5.4953 s, fix2-stop FAIL 9.2775 s, fix2-harvest HARVEST-ONLY
4.3510 s, once2 PASS 4.9248 s, wrongsel run 1 FAIL and run 2
FAIL). No Firefox process was left running; profile dirs were
deleted after each run, /tmp ended at 2 percent used.

Incident during dry-testing: /tmp (512M tmpfs) filled to 100% from
stale Firefox profiles and was cleared by deleting only this
benchmark's own stale profiles plus stale .xpi files (no live
Firefox running at the time). Other agents' /tmp material was left
untouched. Delete the profile/ dir under each run workdir after the
run to avoid repeating this.

Fix pass (batch 9 task 2, commit 9a15647, script only). The council
and redteam review of this re-check found four false-PASS holes in
the script, all fixed here and verified live on the fixture:
(1) validate_plan runs before any browser starts and requires
exactly 2 windows, distinct URLs, a non-empty run_id, and a
message for each window label; an empty plan used to report PASS
(0 sent == 0 windows), a one-window plan PASSED with one message,
and two windows on the same URL PASSED with both messages in one
thread. (2) Plan file:// URLs are normalized (os.path.normpath)
before the live gate, so a ".." path can no longer pass the gate
textually while pointing outside tests/. (3) The outcome rule now
requires exactly 2 sent AND exactly 2 windows. The old 3-window
stop plan (b9t2-stop) is now refused by the exactly-2-windows
rule; the stop test below uses a 2-window plan instead.

Fix-pass verification runs (2026-11-21T21:54:35Z to 21:55:43Z, same
machine, headless Firefox 160.0.1, repo venv python, artifacts in
~/workspace/tools/two_vision_b9t2_fix/, profiles deleted after):

- Happy path (fix-happy): PASS, wall 8.0933 s. Launch 1.2636 s,
  attach 4.5709 s (slower than the 2.65 to 2.79 s range; contended
  shared VM, same shape, not a defect), harvest 0.0901 s and
  0.0065 s for 4 elements each, sends 0.5303 s and 0.6443 s.
  Both V12 gates passed.
- Empty plan (fix-empty): REFUSED exit 2, "plan needs exactly 2
  windows (got 0)", no browser started.
- One-window plan (fix-one): REFUSED exit 2, "plan needs exactly
  2 windows (got 1)", no browser started.
- Same-URL plan (fix-sameurl, both windows on
  ?clone=1): REFUSED exit 2, "the two plan windows must point at
  different URLs", no browser started.
- ".." path plan (fix-dotdot, one URL
  tests/../../tmp/rt-bypass.html): REFUSED exit 2 by the URL gate
  (normalized URL outside tests/), no browser started. The
  redteam repro (both messages sent, outcome PASS) no longer
  reproduces.
- Stop-at-first-failure, 2-window plan (fix-stop2, wrong thread
  selector for clone2): FAIL as designed, wall 10.1698 s. Clone1
  sent, clone2 failed v12-timeout, no clone3 step exists anymore.
- Harvest-only (fix-harvest): HARVEST-ONLY, wall 5.1561 s, 4
  elements per window.
- Exactly-once driver (fix-once): PASS, wall 5.8881 s. Call 1 sent
  in 0.5481 s, 1 bubble; call 2 skipped-already-sent in 0.0038 s,
  still 1 bubble.

FIXED in the script by the fix pass (see the UPDATE below):
reusing a run_id on a live thread no longer reports PASS with
zero new sends (redteam finding 4). The message text is
derived from run_id and the V12 pre-check skips only when the
ledger says the intent was already sent AND the bubble is
visible. Fixture threads do not persist across fresh page
loads, so the live-thread part of this cannot be reproduced
on the fixture; it follows from the code. The checklist now
requires verifying the run_id is fresh against both live
threads before the run.

UPDATE, batch 12 task 2: the gate half of this hole is now FIXED
by the textNew gate (script commit f49851f). With a fresh workdir
(empty ledger) a reused run_id no longer skips: the send proceeds
and the gate passes only on exactly one NEW bubble past the
pre-Enter gate_baseline, proven by the stale-fixture run below
(before_count 1, gate_count 2, PASS with a genuinely new bubble).
UPDATE, fix pass (script commit c1b623b): the remaining halves
are now closed in code too. The shared-workdir half: a retry
that only skips scores FAIL with zero sends this run unless
--allow-resume is passed. The fresh-workdir half: the run
registry refuses a reused run_id bound to a different ledger
path before the browser starts. What remains is the hand
check itself, because the registry is per-machine, so the
freshness check in section 10.3 still stands. The pre-send
reservation also closes the crash variant:
a process death between Enter and the ledger mark leaves status
"sending", and a later run refuses with retry-blocked-reservation
instead of skipping.

Batch 12 task 2 verification runs (2026-11-22T03:59:09Z to
04:00:53.78Z, last run finished per driver.log; the preserved
results.json files share a bulk-copy mtime of 04:01:04.96Z.
The 04:01:14Z end time first written here has no preserved
artifact behind it, corrected by council 2. Same machine,
headless Firefox 160.0.1, repo venv python, one run per case,
each with its own --workdir under /tmp/two_vision_bench/b12t2-*;
all logs, results.json, inventory.json and ledger.json
preserved in ~/workspace/tools/batch12-t2/. The workdirs were
under /tmp and are gone, so the profile-deletion, /tmp
percentage and no-Firefox claims from the first version of
this paragraph cannot be verified from the preserved record
and are struck here, not repeated):

- Happy path with --strict-input-name (b12t2-happy): PASS, wall
  15.3843 s (launch 4.2887 s, attach 5.4269 s, both slow from a
  contended shared VM, same shape, not a defect). Sends 1.8286 s
  and 0.5765 s. Both steps: before_count 0, gate_baseline 0,
  gate_count 1, reservation "sending" reconciled to "sent",
  v11_mutations 1, v11_mutation_flag true, v11_input_events 47.
  Cross-window check clean (own 1, foreign 0 per thread).
  Frames census empty per window.
- Exactly-once driver (b12t2-once): PASS. Call 1 sent in 1.0249 s,
  1 bubble; call 2 skipped-already-sent in 0.0349 s, still
  1 bubble.
- Stale bubble, textNew pass (b12t2-stale, fixed plan
  bench-stale-001, stale fixture): PASS, wall 8.1306 s. Both
  steps: before_count 1, count_at_precheck 1, gate_baseline 1,
  gate_count 2. The gate waited for a NEW bubble past the stale
  one; the old presence gate would have passed immediately.
- Stale bubble, textNew timeout (b12t2-nosend, fixed plan
  bench-stale-001, no-send fixture, 2 s gate): FAIL as designed,
  wall 8.5256 s, exit 1. Clone1 v12-timeout with gate_count 1
  (stale bubble only, baseline 1, never grew), v11_mutations 0,
  v11_mutation_flag false, reservation "sending" reconciled to
  failed-unverified; clone2 not-executed. This proves the gate
  does NOT pass on the stale bubble.
- Strict input name refusal (b12t2-strictbad, plan input_name
  "Zzz"): FAIL as designed, exit 1. Step 1 input-name-mismatch
  (expected "Zzz", actual "Message", ref #msg-input), no ledger
  file written, nothing typed or sent.
- Iframe harvest (b12t2-iframe, --mode harvest): HARVEST-ONLY.
  4 items per window: the input inside the iframe is NOT
  inventoried, as designed (top frame only). Frames census: 1
  frame per window, accessible true, origin "null" (file://
  origins are opaque in Firefox, so the accessible flag, not
  the origin field, is the operative signal on the fixture).
- Batch 12 task 2 driver (b12t2-driver): PASS, wall 7.3978 s.
  D3 ref-stale: renamed input, error ref-stale,
  0 bubbles, 2 nearest candidates listed. Cross-window:
  injected foreign bubble detected (clone2 foreign clone1 1,
  clone1 foreign clone2 0). Reservation block: seeded status
  "sending" refused with retry-blocked-reservation both with
  no bubble (0 bubbles after) and with a visible bubble
  (still 1 bubble, no second send).

Fix-pass verification runs (script commits c1b623b and
45315d5, 2026-11-22, verification window 11:36:49-11:42:41 +07
(fp-happy wall_start 04:36:49Z, fix-pass driver log ends
04:42:41Z); same machine, headless Firefox 160.0.1,
repo venv python; all logs, results.json, inventory.json and
ledger.json preserved in ~/workspace/tools/batch12-t2-fixpass/.
The run dirs still contain their full profile/ dirs, so the
profiles were preserved, not deleted. The /tmp percentage and
no-Firefox claims from the first version of this paragraph
have no preserved df/ps artifact behind them and are struck
here, not repeated. Disclosure: the fp-iframe-strict run below
is the SECOND attempt. The first attempt failed with
harness_error "TypeError: log() got multiple values for
argument 'name'" (log ends 04:37:57Z, wall 5.5436 s); the
colliding call was fixed in the working tree between the
attempts and folded into commit c1b623b (04:43:37Z) with no
mention in the fix-pass report. The fix-pass runs therefore
verified the pre-commit working tree, not the commits; the
committed code was verified later by a fresh driver re-run
on HEAD (11/11 PASS, see the fix pass 2 runs below, and the
report section 7 appendix):

- Happy path (fp-happy, --fixture): PASS, wall 10.3707 s,
  sends_this_run 2. Both steps: before_count 0,
  gate_baseline 0, gate_count 1, v11_mutations 1 with
  v11_scope "thread", input_cleared_after_enter true.
  Cross-window check clean (own 1, foreign 0 per thread).
- Stale bubble (fp-stale, fixed plan bench-fixpass-stale,
  stale fixture): PASS, wall 7.1252 s. Both steps:
  before_count 1, gate_baseline 1, gate_count 2.
- No-send (fp-nosend, fixed plan bench-fixpass-nosend,
  no-send fixture): FAIL as designed, wall 9.3197 s, exit 1.
  Clone1 v12-timeout with gate_count 1 (stale bubble only),
  v11_mutations 0, v11_scope "thread"; clone2 not-executed.
- Strict input name (fp-strictbad, plan input_name "Zzz"):
  FAIL as designed, exit 1, wall 5.2949 s. Step 1
  input-name-mismatch, no ledger file written.
- Iframe harvest (fp-iframe, --mode harvest): HARVEST-ONLY,
  wall 5.4404 s. 4 items per window, 1 frame per window,
  accessible true, origin "null".
- Iframe harvest with --strict-input-name (fp-iframe-strict):
  HARVEST-ONLY (second attempt; the first attempt failed,
  see the disclosure above). harvest_inputs recorded for both windows
  (name, aria-label and placeholder "Message" each, ref
  #msg-input); the mechanized name check passes without
  any operator read of inventory.json.
- Exactly-once driver (fp-once): PASS. Call 1 sent in
  0.6451 s, 1 bubble; call 2 skipped-already-sent in
  0.0056 s, still 1 bubble.
- Batch 12 task 2 driver (fp-b12t2): PASS (D3 ref-stale,
  cross-window, reservation block all pass).
- Fix-pass driver (fp-driver, tests/
  two_vision_fixpass_driver.py): 11/11 PASS, wall 54.0356 s.
  F1: a failed retry leaves the "sent" ledger record intact
  and the next run skips instead of re-sending. F2: a retry
  run with zero fresh sends scores FAIL (PASS only with
  --allow-resume). F3: the same run_id in a fresh workdir is
  REFUSED, exit 2, no results.json and no ledger.json
  written. F5: a double append fails as duplicate-bubble
  (gate_count 2, ledger failed-unverified). F6: a tag swap
  fails D3 as ref-stale. F7: a moved input fails the HCU
  guard as geometry-moved dx=0.0 dy=50.0. F8: a
  placeholder-only rename fails D3 as ref-stale. F9:
  contenteditable typing with a no-op Enter times out with
  v11_mutations 0 and v11_scope "thread". F10: a foreign
  bubble with a sender prefix counts as contamination.
  F11: identical messages are refused by validate_plan.
  C1-2: a "sent" intent with a broken thread selector fails
  as thread-missing, ledger stays "sent", 0 bubbles.

Fix pass 2 verification runs (script commits dfea01b,
93e8f48 and 00ce862, 2026-11-22, verification window
12:30-12:40 +07 (05:30-05:40Z); same machine, headless
Firefox 160.0.1, repo venv python; all logs, results.json,
inventory.json and ledger.json preserved in
~/workspace/tools/batch12-t2-fixpass2/. The driver ran
against the committed code (temp HOME for a fresh registry,
so the fix-pass-1 bindings did not collide; the baseline
CLI runs used the real default registry with fresh
bench-fixpass2-* run_ids). The run dirs still contain their
full profile/ dirs, so the profiles were preserved, not
deleted. /tmp was at 90 percent at the end of the runs
(55M free), measured by df; no Firefox was left running
(0 marionette matches, 0 listeners on 2828/9223 at the end):

- Happy path (fp2-happy, --fixture): PASS, wall 9.0674 s,
  sends_this_run 2. Both steps: before_count 0,
  gate_baseline 0, gate_count 1, gate_settle_s 1.0,
  v11_mutations 1 with v11_scope "thread",
  input_cleared_after_enter true. registry_enabled true,
  registry_path the default
  /home/hatch/.cache/two_vision_bench/run_registry.json.
  Cross-window check clean (own 1, foreign 0 per thread).
- Stale bubble (fp2-stale, fixed plan bench-fixpass2-stale,
  stale fixture): PASS, wall 9.3794 s. Both steps:
  before_count 1, gate_baseline 1, gate_count 2.
- No-send (fp2-nosend, fixed plan bench-fixpass2-nosend,
  no-send fixture): FAIL as designed, wall 11.0997 s,
  exit 1, 0 sends. Clone1 v12-timeout, clone2
  not-executed; outcome_note now names the failure
  ("no sends this run: clone1:v12-timeout") instead of
  claiming both steps skipped.
- Strict input name (fp2-strictbad, plan input_name "Zzz"):
  FAIL as designed, exit 1, wall 5.3623 s. Step 1
  input-name-mismatch, no ledger file written.
- Iframe harvest (fp2-iframe, --mode harvest): HARVEST-ONLY,
  wall 5.2999 s. 4 items per window, 1 frame per window,
  accessible true, origin "null".
- Iframe harvest with --strict-input-name
  (fp2-iframe-strict): HARVEST-ONLY, wall 5.0358 s.
  harvest_inputs recorded for both windows (name,
  aria-label and placeholder "Message" each, ref
  #msg-input).
- Exactly-once driver (fp2-once): PASS, wall 7.2159 s.
- Batch 12 task 2 driver (fp2-b12t2): PASS, wall 6.6402 s.
- Fix-pass driver (fp2-driver, tests/
  two_vision_fixpass_driver.py): 19/19 PASS, wall
  157.1595 s. New in fix pass 2: harvest-then-run with the
  same run_id in different workdirs succeeds; a "sent"
  intent with no visible bubble refuses with
  retry-blocked-sent-bubble-absent; a changed message under
  the same run_id refuses with retry-blocked-intent-changed
  and the ledger keeps the original message; a delayed
  double append (700 ms) fails as duplicate-bubble after
  the 1.0 s settle; results.json records registry_enabled
  and registry_path; substring messages are refused;
  outcome_note names the failure; corrupt registry and
  ledger files are REFUSED with exit 2. The first full
  driver run failed only on the delayed-double test, and
  only on gate_settle_s being recorded solely on the pass
  path; the field is now recorded when the gate starts
  (commit 00ce862) and the re-run passed 19/19.

## 8. Known gaps (F5/D1-D6, TODOs, from the combined design)

Marked as TODO in the script where they apply; the review round
revises them. None of these blocks the dry test, but a live run
must not claim them done.

| Gap | State in this script | What is still open |
| --- | --- | --- |
| F5 bulk harvest | Built here as one evaluate per window. | Brave CDP DOM.getBoxModel / Accessibility.getFullAXTree in scripts/cdp.mjs; production V11 MutationObserver flag (batch 12 task 2 BUILT in this script: OBSERVER_JS armed before typing, thread-scoped, counting mutation records; the fixture counter window.__inputEvents is kept alongside it; the flag is recorded evidence only, not a pass criterion). |
| F5 V12 gate | Built here (sent-bubble check after each send). Since batch 12 task 2 it is a textNew gate: COUNT_JS with a pre-Enter gate_baseline, passing only on exactly one NEW bubble (baseline + 1); a double append fails as duplicate-bubble instead of passing silently. The gate is appearance-based, not causal. Cross-window check after both sends matches foreign bubbles by containment on the raw texts. | No V12 gate exists in production code; this script is the first implementation. Live proof of the gate is still owed (fixture proof only). |
| F5 exactly-once ledger | Built here (ledger file + V12 pre-check before every send). Since batch 12 task 2 the pre-check skips only when the ledger says the intent was already sent and the bubble is visible, and the pre-send reservation is built: the intent is written as "sending" before Enter and reconciled after the gate; a later run finding "sending" refuses with retry-blocked-reservation. Since the fix pass: a failed retry never overwrites a "sent" or "sending" record; the run registry refuses a reused run_id in a fresh workdir; a zero-send retry scores FAIL unless --allow-resume; ledger writes are locked. Since fix pass 2: every ledger mark binds the message text, thread URL and selectors, and a changed plan refuses; a recorded "sent" intent whose bubble is absent refuses instead of re-sending; "sent" is terminal in the ledger state machine and the reservation is atomic under one lock. | Needs review-round approval. A v12-timeout now marks the intent failed-unverified and a later run with the same intent refuses to re-send it, so a typed-but-unseen message cannot double-send on retry. A fresh page load with an empty thread no longer re-sends a recorded intent: it refuses with retry-blocked-sent-bubble-absent, and only a new run_id after a hand check can send again. The reservation closes the process-death gap only when the same ledger is reused. |
| F5 BiDi/Marionette handover | Not built. Script is Marionette-only. | No handover protocol exists under the one-session constraint. |
| F5 step-6 loop hygiene | Not built. | Prompt caching, diff-gated re-observation, downscale to token tier, context editing, low effort, adaptive waiting: unowned, agent-harness concerns. |
| D1 one-session sequencing | Marionette-only; BiDi session.new cost is known (1.5-2.8 s cold, 0.014 s warm, batch 7 task 2). | Sequencing for a live run that needs both protocols is unspecified. |
| D2 HCU guard owner | The guard lives in hcu_guard() in this script. | No production component owns the guard. |
| D3 Mantis numbering | Refs are DOM-derived per run; the doc warns they must not transfer. Since batch 12 task 2 send_one re-resolves the ref before input and fails fast with ref-stale when tag, role, name, aria-label or placeholder changed, listing the nearest live textboxes. The HCU guard compares against the harvested center unless the page scrolled. | Ref stability on a mutating Messenger page is proven only on the fixture (renamed input); a live mutation mid-run is still unobserved. Id-less elements now get a unique CSS path ref instead of the invalid tag + '[' + i + ']' form. |
| D4 exactly-once | Mechanized here (ledger + pre-check + failed-unverified retry block). Since batch 12 task 2 also the pre-send reservation and the textNew gate. | Needs the review round; see the F5 ledger row. |
| D5 VISION 1 is DOM | Stated in the script docstring and here. | Nothing open; do not call the harvest a screenshot. |
| D6 one vs two instances | One instance, two windows. --instances two is REFUSED until two instances exist; it is never recorded in results as if it ran. | Unspecified which the live run uses; two instances need a second Marionette attach. |

## 9. What is NOT done (do not claim it)

- No live run has happened. The script has only ever run against
  the local fixture in headless Firefox on this VM.
- No Zen numbers. Every timing above is Firefox 160.0.1 as a
  stand-in; real Zen timings are UNVERIFIED until the laptop run.
- No Messenger selectors. The live plan needs real thread URLs,
  thread selectors, and bubble selectors, which only the coordinator
  can supply for the live run. The V12 gate requires exact
  textContent === text and the default bubble selector is
  fixture-shaped, so a live plan MUST override bubble_selector.
- The harvest inventories native controls plus [role="button"] and
  [role="textbox"] controls. Plain links and role-less divs are not
  inventoried; the "every input + button" claim does not cover them.
- The C12 conversion layer (viewport origin, DPR) is NOT used by
  this script: clicks use viewport coordinates from
  getBoundingClientRect directly, the same shape as the batch 7
  bench. Live Zen clicks need the C12 adjudication (batch 8 task 3)
  before the coordinates can be trusted on the laptop.
- ensure_visible scrolls only for vertical out-of-view (center
  above or below the viewport); horizontal out-of-view is not
  handled. Fail-closed via the HCU hit test, so not a hole, but a
  live target off the side of the viewport would fail the guard
  instead of scrolling into view.

## 10. Live-run prerequisites checklist (added batch 9 task 2)

This is a preparation checklist only. The live run is the
coordinator's acceptance test; nobody runs it live until the
coordinator says run, and this script has never run live.

### 10.1 Workspace state (check before anything else)

- [ ] Repo on main, script tests/two_vision_bench.py at the
  reviewed commit (1939 lines after the batch 12 task 2 fix
  pass 2, commit 00ce862). Run `git log --oneline -1 --
  tests/two_vision_bench.py` and confirm it prints 00ce862: any
  other hash means an unreviewed change sits on top of it.
- [ ] BLOCKER, open: the script launches its own fresh headless
  Firefox with a fresh profile (main() calls launch_browser; no
  attach-to-existing-browser option, no profile reuse, no login
  step anywhere in the argument list), so it cannot use the laptop
  Zen's login state.
  A fresh profile is logged out of Messenger, so a live run as
  specified would hit the login wall and FAIL with v12-timeout,
  NOT with no-message-input-in-inventory and NOT fail-closed and
  safe: on a login page the script types the bench text into the
  email field (find_input returns the first visible textbox when
  none is named "Message"), Enter submits the login form, and the
  V12 gate times out after 5 s. The no-message-input-in-inventory
  error fires only when a page has zero visible textboxes, which
  a login page does not satisfy. Rung 2 closes this typing hazard
  a different way: it runs with --strict-input-name (runbook
  section 14), so the script refuses to type into a textbox
  whose name does not contain the plan's input_name and fails
  closed with input-name-mismatch before any send. The 2-vision
  run does not pass the flag and keeps the hazard documented
  here. The live run needs one of the
  two live-shape options in runbook section 13 (option B, a CDP
  driver to the real Brave/Chrome chats on ws2; or option A, a
  logged-in profile pre-seeded into <run-dir>/profile) before it
  can pass. Until the coordinator picks one, do NOT present Zen
  login as the readiness condition. Assumption, no repo
  evidence: one profile holds one Messenger session (a
  Firefox profile holds one set of Messenger cookies),
  so both windows in the one-instance shape share the same
  login; the two clones are two threads under one account
  in this shape. Treat as one session until verified live.
  The run machine must have the Firefox binary, geckodriver and
  venv at the script's hardcoded paths (FF and GD in the script
  header, lines 49-50) under option A; under option B the run
  needs the CDP driver and debug ports instead, not the
  script's Firefox paths (runbook section 13).
- [ ] The live lane is free: no BASELINE2 or other live run is
  running, and no other agent holds the laptop browser. Confirm
  with the coordinator; do not guess.
- [ ] The installed laptop code is still the pre-amend code if a
  baseline is still owed. Do not sync the amend over the laptop
  before the baseline runs. Record which code version the laptop
  actually runs before any manual step (runbook section 9
  requires this); the pre-amend item above states a condition
  with no verification method unless the version is recorded.
- [ ] The C12 adjudication (batch 8 task 3) does NOT apply to
  this script's clicks and is NOT a prerequisite for this run:
  section 9 states the C12 conversion layer is not used here
  (clicks use getBoundingClientRect viewport coordinates
  directly), so requiring C12 settled would block a run that does
  not need it. C12 applies only to a future Zen-attached variant
  whose clicks go through the conversion layer.
- [ ] /tmp has room (512M tmpfs; check `df -h /tmp`) and ports
  2828 and 9223 are free on the run machine. A stale browser
  holding either port makes launch_browser refuse.
- [ ] A fresh --workdir per run (for example
  /tmp/two_vision_bench/live1). Never reuse a live run's workdir:
  the ledger, results, and inventory of one run must not be
  confused with another's, and the run's results.json would
  otherwise overwrite the harvest's HARVEST-ONLY results.json
  (runbook steps 1 and 2 must use different workdirs,
  <harvest-dir> and <run-dir>). The reason is record-keeping,
  not the registry: the harvest never binds the registry
  (fix pass 2), so a harvest-then-run with the same run_id in
  different workdirs is the rung 2 shape and works; the
  registry binds only in run mode, and a reused run_id in a
  fresh workdir is REFUSED by it before the browser starts
  (same machine). The old false PASS needed a shared workdir
  with a "sent" ledger record, and even that now scores FAIL
  without --allow-resume.

### 10.2 Both clones' chats

- [ ] The coordinator supplies the two real thread URLs, one per
  clone window, plus the thread selector and bubble selector for
  each. The two URLs must differ: the script now refuses a plan
  whose two windows point at the same URL, because both messages
  would land in one thread and still report PASS. The script
  cannot invent selectors; a wrong selector fails the V12 gate
  loudly, but only after the message was already typed; a
  typed-but-unseen message is exactly what the retry block and
  the hand-check exist for.
- [ ] Both threads are open and reachable before the run starts.
  If either thread is unreachable, abort before starting: do not
  start a live run with a half-known target. (The laptop Zen
  login is NOT the readiness condition: the script drives its own
  fresh Firefox, never the laptop Zen; see the blocker item in
  10.1. What matters is the script's own browser's Messenger
  session, which does not exist yet.)
- [ ] Run --mode harvest with the live plan first, before any
  send run: confirm both inputs are visible and named "Message"
  in the inventory text (operator judgment on the names, not a
  script outcome). The harvest does NOT verify thread_selector
  or bubble_selector: in --mode harvest main() returns
  HARVEST-ONLY without ever evaluating them; they are only
  touched inside send_one via GATE_JS, after typing. The
  selectors stay unverified until the first V12 gate, so the
  first send is the first real selector test. Wrong selectors
  are the proven typed-but-unseen failure mode, and the
  harvest-first step does not catch them; it catches only a
  missing or misnamed input. Caveat on the name itself: the
  expected name "Message" is visual-only evidence (two
  screenshot reads in the CL1-MSG logs), the real aria-label
  is UNKNOWN, no DOM read of the live input exists in the
  repo. If the harvest shows a visible textbox whose name is
  not "Message" and is not "Email"/"Password", STOP and
  record the actual name; the name is only closed by a live
  DOM read before the run (runbook section 6).
- [ ] The message input in each thread is a contenteditable
  textbox (the Messenger input type). The script's V1 check reads
  innerText for contenteditable elements; if a thread's input is
  a different control, say so in the plan and re-check the
  fixture variant first.
- [ ] Both windows live in ONE browser instance with two windows
  under option A (the --instances one shape, the script's own
  Firefox). Two instances are not implemented
  and --instances two is refused. Under G3 the live shape is
  Brave (clone1) + Chrome (clone2) on ws2, which the script
  cannot drive today; under the fallback option A it is the
  script's own Firefox with two windows and one Messenger
  account. The live shape is the coordinator's decision
  (runbook section 13); do not write "ONE Zen instance" here,
  that shape is stale relative to G3.

### 10.3 Exact message contents

This subsection is written for the option B shape (Brave/Chrome
on ws2). Under option A (script's Firefox, no Brave/Chrome)
it does not apply: there are no Brave/Chrome a11y targets, so
freshness rests on generation alone plus a visual check of the
threads in the script's Firefox after the harvest-first step.

- [ ] The plan JSON carries a unique run_id (for example
  bench-20261122-143022-a1b2c3, in the script's timestamp
  format bench-<UTC timestamp>-<6 hex>; the older example
  bench-20261122-001 is shape-only, not the script's format)
  and the two messages in exactly this form:
  "BENCH-TEST clone1 <run_id>" and "BENCH-TEST clone2 <run_id>".
  Generation rule: generate a fresh timestamp-based run_id for
  this attempt and never reuse a run_id from a previous
  attempt, including a failed one. Freshness comes from
  generation, not from the check: a freshly generated
  timestamp-based run_id is fresh by construction, since no
  earlier run could have used that exact text.
- [ ] Verify the run_id is fresh before the run: check both live
  threads for an existing bubble with that text. Method: the
  only executable check on the Brave/Chrome threads is an
  accessibility-tree substring search, not the V12 exact-text
  DOM check. Take the AT-SPI application PID from
  `computer-use a11y apps` for each browser (NOT the hyprctl
  client pid: the hyprctl window PID is not the AT-SPI app
  PID, improvements/speed-proto-pick4-summary.md:15), then run
  `CU_PICK4_FASTPATH=1 computer-use a11y query --pid
  <atspi-pid> --name "BENCH-TEST clone1 <run_id>"` (and the
  same for clone2). Hard limit: scripts/a11y.py observe()
  only keeps elements with actions, editable, or in skeleton
  mode, and describe() records ref, role, name, path,
  actions, plus editable/extents/state flags, and never
  text content, so a bubble (static text, no actions, not
  editable) is dropped before query() sees it. The method as
  specified can only find text that is the NAME of an element
  that survives the filter; whether a bubble's text is exposed
  as an accessible name at all is UNVERIFIED. A hit proves the
  text is present somewhere in that app's accessibility tree,
  not that it is a bubble in the thread; a miss proves nothing
  about exposure. If the exact text is found in either thread,
  the run_id is NOT fresh: discard it, generate a new one,
  update the plan and both messages, and check again. The
  message text is derived from run_id, and the script's V12
  pre-check skips only when the ledger says the intent was
  already sent and the bubble is visible, so a reused run_id
  with a fresh workdir does not skip: it is REFUSED by the
  run registry before the browser starts (same machine), and
  a same-workdir retry that only skips scores FAIL without
  --allow-resume. A recorded "sent" intent whose bubble is
  absent refuses instead of re-sending, and a changed plan
  under the same run_id refuses with the original message
  kept in the ledger. UPDATE, batch 12 task 2: the gate half of
  this hole is now fixed by the textNew gate (the gate passes
  only on exactly one NEW bubble past the pre-Enter
  gate_baseline), so a stale bubble alone can no longer pass
  a new send, proven by the stale-fixture run below
  (before_count 1, gate_count 2, PASS with a genuinely new
  bubble). UPDATE, fix pass: the registry and the outcome
  rule close the remaining halves in code (see section 5);
  what remains is the hand check itself, because the
  registry is per-machine. UPDATE, fix pass 2: the harvest
  never binds the registry, so the rung 2 harvest-then-run
  shape with different workdirs works; the gate settles a
  full second after first sighting, so a delayed double
  append fails; the ledger binds message, URL and
  selectors, so an edited plan cannot send under an old
  run_id.
- [ ] Dry probe of the a11y method (run once, before the first
  live run; UNRUN as of 22/11). Test the two premises
  separately with independent steps (a single query cannot do
  both: a raise identifies a pid failure, a hit proves both,
  but a miss is three-way ambiguous). Part 1, pid mapping and
  app presence: run `computer-use a11y apps` and confirm
  Brave and Chrome both appear with PIDs; if either is
  absent, the method fails at step 1 (only 6 registered apps
  on record, no Brave/Chrome named). Then prove the pid
  mapping with an element that survives the observe()
  filter: query for a KNOWN name that has actions or is
  editable (for example the message input itself, name
  "Message", which is editable). Part 2, bubble exposure:
  only after Part 1 hits, query for a bubble text that is
  currently VISIBLE in the thread (record how it was read);
  on a miss, retry once with a second visible bubble text,
  then run a skeleton observe (`computer-use a11y observe
  --pid <atspi-pid> --skeleton`) and search the snapshot
  JSON for the same text. A hit in either proves bubble text
  is searchable on that browser. A miss in both proves
  nothing definitive (bounded observe, or text not carried
  as a name), and the method is unusable for freshness until
  a working query is demonstrated. Premise A (bubble
  exposure) is UNVERIFIED; premise B (hyprctl pid is the
  AT-SPI pid) is contradicted by prior evidence. Full
  procedure in runbook section 5.
- [ ] Record requirement: record the check in the run log
  (<run-dir>/run-log.md): the run_id used, both threads
  checked, what was found (nothing, expected), the dry-probe
  result, and the time. A run_id that was never checked is not
  a fresh run_id.
- [ ] Test messages are bench strings only. Never put real user
  text, names, or personal information in a plan, inventory,
  ledger, log, or result file.
- [ ] bubble_selector is overridden for Messenger in the plan
  (the default ".bubble, [data-sender]" is fixture-shaped and the
  V12 gate requires exact textContent === text, so the default
  would fail closed live). v12_gate_s is set in the plan
  (5 s default; raise it only if the live thread is slow to
  render, and record the value used).

### 10.4 PASS/FAIL criteria

- [ ] VISION 1 (harvest): PASS iff the one-shot harvest returns
  both message inputs, each visible, with a ref, rect, center and
  role textbox. If either input is missing, the run is FAIL
  before anything is sent (operator judgment on the inventory
  text, not a script error: in harvest mode without
  --strict-input-name the script returns HARVEST-ONLY and never
  emits no-message-input-in-inventory; with --strict-input-name
  it checks the harvested names itself and fails closed with
  no-message-input-in-inventory or input-name-mismatch. That
  error fires in run mode whenever find_input is called). Caveat: the expected input name "Message" is
  visual-only evidence (two screenshot reads in the CL1-MSG
  logs); the real aria-label is UNKNOWN and no DOM read of the
  live input exists in the repo. A harvest showing a visible
  textbox whose name is not "Message" and is not
  "Email"/"Password" means STOP and record the actual name
  (runbook section 6).
- [ ] VISION 2 (outcome check): PASS iff both BENCH-TEST
  messages appear as bubbles in their threads. The script's V12
  gates check this by DOM read after each send; the agent's
  VISION 2 look at both threads once at the end is the
  independent confirmation. VISION 2 is one screen observe of
  the monitor holding ws2, which is eDP-2 on this laptop
  (monitor_box [2464, 902, 1920, 1200]); confirm live with
  `hyprctl -j monitors`. This is the option B shape. Under
  option A the threads run in headless Firefox, so there is
  no ws2 screen to observe: VISION 2 as a screen observe does
  not exist there, and the V12 DOM gates are the outcome
  check; the option-A VISION 2 procedure is still open (runbook
  section 12 item 5). Rung 2 is 0-vision by the scoped definition
  in runbook section 14 (0 during the step-2 run invocation;
  the step-1 harvest read is 1 vision of pre-run preparation)
  and drops VISION 2 entirely: the textNew gate, cross-window
  check and strict input name replace the agent looks, and the
  outcome is read from results.json. That scoping narrows the
  unscoped "0-vision" acceptance label in the arch-review log
  and needs coordinator approval before a rung 2 run is scored
  against it.
  Outcome scoring is by message in
  thread (M1), never by point-in-box.
- [ ] Overall: PASS iff both messages land. Any single failed
  step makes the run FAIL; the chain stops at the first failure
  and later steps are recorded not-executed. The script now
  refuses any plan that is not exactly 2 windows with distinct
  URLs and distinct non-empty messages, before the browser
  starts, so an empty or one-window plan cannot report PASS.
  A run with zero fresh sends scores FAIL unless
  --allow-resume is passed.
- [ ] Per-step failure meanings are in section 6. A
  value-mismatch means nothing was sent (Enter was not pressed);
  a v12-timeout means the message may have been typed and may
  have landed unseen, so the thread must be checked by hand.

### 10.5 Stop conditions (abort the live run, do not push on)

- [ ] Stop at the first failed step. The script does this
  itself; do not restart the chain mid-run.
- [ ] If a send ends in v12-timeout, STOP. Check the thread by
  hand. Never re-run with the same run_id: the ledger marks the
  intent failed-unverified and refuses the retry. To retry, fix
  the thread/bubble selectors first, then use a NEW run_id.
- [ ] If either thread becomes unreachable, or the browser
  crashes, or a click lands on the wrong window, STOP and report
  the state (which intents are sent, which are failed-unverified)
  before doing anything else. Do not re-send to "make up" for a
  lost message: a re-send without a V12-visible bubble is exactly
  how a duplicate happens.
- [ ] If --confirm-live was not explicitly given by the
  coordinator for this run, STOP. The script refuses without it,
  and the URL gate refuses any non-fixture plan without both
  --live and --confirm-live.
- [ ] After the run, preserve the full log, results.json,
  inventory.json and ledger.json out of /tmp immediately (the
  fix-pass logs were once lost to a /tmp wipe), delete the
  profile/ dir if present (option A only; under option B there
  is no <run-dir>/profile), and report the outcome with the
  run_id and wall time. The operator's look count comes from
  the run log (<run-dir>/run-log.md); every look outside the
  run must be logged there with its time. Never edit a result
  file after the run.
