# 2-vision benchmark live-run runbook

Date: 2026-11-22. Status: PREPARATION ONLY. No live run has happened,
and no live run may happen from this runbook alone: the live run is
the coordinator's acceptance test, and nobody runs it live until the
coordinator says run. The script and the workflow doc are built only.
Updated 22/11 by the batch 11 task 2 closeout (section 9 corrected
for AMEND4 item 12, section 13 added with both live-shape options,
section 12 rewritten with current statuses; verdict still NOT READY,
see docs/clone2-live-run-readiness-closeout-20261122.md).
Updated 22/11 by batch 12 task 2 (section 14 added with the rung 2
0-vision procedure; textNew, pre-send reservation, V11, D3 and the
frames census built in the script, commit f49851f; verdict still
NOT READY, see docs/clone2-batch12-readiness-closeout-20261122.md).
Updated 22/11 by the batch 12 task 2 fix pass (council 1 + 2,
redteam: exact +1 textNew gate, duplicate-bubble failure, run
registry, zero-send runs never score PASS, thread-missing fail
fast, D3 tag/aria-label/placeholder, thread-scoped V11,
contained cross-window matching, distinct messages; script
commit c1b623b; verdict still NOT READY, counts now 3 closed,
5 partial, 2 open, 2 standing).
Updated 22/11 by fix pass 2 (round-2 council 1 + 2, redteam
BROKEN with 4 HIGH, redteam 4/4: intent binding, sent-bubble-
absent refusal, gate settle, harvest never binds the registry,
ledger state machine, outcome rule on vanished threads;
script commit 00ce862; verdict still NOT READY, counts still
3 closed, 5 partial, 2 open, 2 standing).

Sources read for this runbook (all verified before writing):
- Assignment: batch 10 task 3, coord/clone2.md line 868, commit
  422f4b0 (06:01 22/11). Decision G3 is stated there and nowhere
  else in the repo; see section 2.
- Script: tests/two_vision_bench.py, 868 lines, commit c267411
  (pin as first written; updated batch 12 task 2 to 1200 lines,
  commit f49851f, hardened in the fix pass to 1637 lines,
  commit c1b623b, hardened again in fix pass 2 to 1939 lines,
  commit 00ce862, see section 3).
- Workflow doc: docs/two-vision-benchmark-workflow-20261122.md,
  1121 lines, checklist section 10 (added batch 9 task 2, fixed
  batch 9 task 2 fix pass).
- One-vision design: docs/clone2-one-vision-design-20261122.md,
  792 lines (731 at c267411, updated in the batch 12 task 2
  fix pass and again in fix pass 2).
- Operator guard: improvements/worker-cl1sweep-fail-invest-log.md,
  commit 5f5a2fd on origin/todolist-push (CL1-SWEEP investigation,
  ~06:00 22/11). See section 9.
- Window layout on ws2: improvements/worker-cl1msg-log.md,
  00:46 22/11, on origin/todolist-push. See section 2.
- Accuracy bar: improvements/worker-coord-click2-log.md, line 32
  ("one vision must drive max actions at accuracy >= 90%") and
  line 38 (grounding accuracy 7/7 = 100% synthetic, bar >= 90%).

## 0. Blockers first: read this before anything else

This runbook does NOT make a live run possible today. The
current missing list is in section 12 (3 closed, 5 partial,
2 open, 2 standing, as of the batch 12 task 2 fix pass 2).
The four blockers below are the shape of the gap; do not
work around them by improvisation.

1. The script cannot drive the live chats as they exist today.
   It always launches its own fresh headless Firefox with a fresh
   profile (launch_browser, script lines 535-566). There is no
   attach-to-existing-browser option, no profile reuse, and no
   login step anywhere in the argument list. A fresh profile is
   logged out of Messenger, so a live run as specified would hit
   the login wall and FAIL, but NOT with
   no-message-input-in-inventory and NOT fail-closed and safe.
   A login page has visible email and password inputs, which
   HARVEST_JS inventories as textboxes, and find_input (script
   lines 524-533) returns the first visible textbox when none
   is named "Message", so it picks the email field. The script
   then clicks it, types the bench text into it (the V1 readback
   passes, the text IS in the field), Enter submits the login
   form, and the V12 gate times out after 5 s because no thread
   container exists. The outcome is FAIL with clone1 v12-timeout
   (intent failed-unverified) and clone2 not-executed, plus two
   side effects the operator must expect: the bench text typed
   into a login email field, and an Enter that submits a login
   attempt with garbage credentials. The
   no-message-input-in-inventory error (main, script line 1686,
   run mode; the harvest-mode occurrence is line 1644)
   fires only when a page has zero visible textboxes, which a
   login page does not satisfy. An attach-to-Zen mode does not
   exist, and neither does a logged-in profile or a login step.
   The two live-shape options that would close this gap are
   written in full in section 13; the coordinator decides
   which one runs. Rung 2 (section 14) closes the typing hazard
   a different way: it runs with --strict-input-name, so the
   script refuses to type into a textbox whose name does not
   contain the plan's input_name, and fails closed with
   input-name-mismatch before any send.
2. Under decision G3 the live threads are in Brave (clone1) and
   Chrome (clone2) on workspace ws2. The script drives only
   Firefox and cannot attach to Brave, Chrome, or Zen. No path
   exists today for the script's browser to reach those threads.
3. The V12 gate is now a textNew gate (batch 12 task 2, script
   commit f49851f, hardened in fix pass c1b623b): main() takes a
   before-snapshot count per window before any send (recorded
   evidence only, never consulted by the gate), and the gate
   passes only when the count grows to exactly the pre-Enter
   gate_baseline + 1 (COUNT_JS, script line 177), so a stale
   bubble from an earlier run cannot pass a new send, and a
   double append fails as duplicate-bubble instead of passing
   silently. The gate is appearance-based, not causal: it proves
   a bubble with the exact text appeared after the baseline, not
   that our Enter caused it (an echo or incoming message with
   identical text would pass it; mitigation is unique message
   text plus a free live lane). Fixture-proven: stale
   fixture run PASS with before_count 1 and gate_count 2 per
   window, and the no-send fixture run FAILS v12-timeout with
   gate_count stuck at 1. The pre-send reservation is also
   built: the intent is written as "sending" after the V1
   readback passes and before the Enter keypress, and a later
   run finding status "sending" refuses with
   retry-blocked-reservation. A failed retry never overwrites a
   "sent" or "sending" ledger record with "failed" (fix pass).
   The cross-window check is built: after both sends each
   thread must hold only its own message, matching foreign
   bubbles by containment on the raw bubble texts, so a
   sender-prefixed rendering still counts. The 2-vision run in
   this runbook keeps 2 visions (section 8); rung 2 is 0-vision
   during the step-2 run invocation, with the step-1 harvest
   read as pre-run preparation outside the budget (section 14).
4. The run_id freshness check is an operator check AND a script
   check. The shared run registry binds a run_id to the ledger
   path of its first run: a reused run_id in a fresh workdir is
   REFUSED before the browser starts (exit 2). A same-workdir
   retry that only skips already-sent intents scores FAIL with
   zero sends this run, not PASS, unless the operator passes
   --allow-resume explicitly. The runbook freshness check in
   section 5 still stands as the human backstop: never reuse a
   run_id on a live thread.

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

- Script: tests/two_vision_bench.py, 1939 lines, commit 00ce862.
  Run `git log --oneline -1 -- tests/two_vision_bench.py` and
  confirm it prints 00ce862.
- Workflow doc: docs/two-vision-benchmark-workflow-20261122.md,
  1121 lines. Checklist section 10 in that doc is the
  prerequisite checklist this runbook executes.
- Design doc: docs/clone2-one-vision-design-20261122.md,
  792 lines, commit 00ce862 (updated in the batch 12 task 2
  fix pass and again in fix pass 2).
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
shape (workflow doc section 5; script validate_plan, line 1111):

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
must have a messages entry; the two messages must be distinct,
non-empty strings (identical messages make a correct run FAIL
the cross-window check, because it identifies messages by text
alone). Plan file:// URLs are normalized
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
  (the --instances one shape, option A: the script's own
  Firefox). Two instances are not
  implemented and --instances two is refused (exit 2). Under
  option B (primary, CDP driver to Brave/Chrome on ws2) the
  run uses two browsers, not one instance; see section 13.

## 5. Step 0: run_id freshness check (do this first)

This is the run_id-reuse hole (workflow doc 10.3), now closed
in code and still checked by hand. The message text is derived
from run_id. Since the batch 12 fix pass the script's V12
pre-check skips only when the ledger says this intent was
already sent (status "sent") AND the bubble is visible: with a
fresh workdir the ledger is empty, so a reused run_id does NOT
skip, it sends a second identical bubble instead. Two script
guards now block the reuse: the shared run registry refuses a
run_id bound to a different ledger path before the browser
starts, and a same-workdir retry that only skips scores FAIL
with zero sends this run unless --allow-resume is passed. The
operator check still stands as the human backstop, because the
registry is per-machine (a run_id first used on another machine,
or after the registry file was wiped, is not refused). The
operator checks it by hand, before the run, for both threads.
Fixture threads do not persist, so the live-thread part of this
cannot be reproduced or tested on the fixture.

1. Generate a fresh run_id for this attempt. Never reuse a
   run_id from a previous attempt, including a failed one. The
   script's default format is bench-<UTC timestamp>-<6 hex>
   (default_plan, script line 1223, run_id line 1226); the checklist example
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

   Hard limit on this method, found by the fix-pass redteam
   (do not ignore it): scripts/a11y.py observe() (lines
   83-117) only keeps an element in its returned list if it
   has actions, is editable, or the observe runs in skeleton
   mode (`if skeleton or item['actions'] or
   item.get('editable')`), and describe() records ref, role,
   name, path, actions, plus editable/extents/state flags, and
   never text content. query() calls
   observe() without skeleton and then filters that already
   pruned list by name substring. A Messenger bubble is
   static text: no actions, not editable. It is dropped
   before query() ever sees it, so a bubble-text query
   returns matched 0 even when bubbles are fully exposed in
   the tree. The method as specified can only find text that
   is the NAME of an element that survives the filter (an
   input, a button, anything with actions). Whether a
   bubble's text is exposed as an accessible name at all is
   UNVERIFIED, and the query as written cannot answer it.
   A miss therefore proves nothing about exposure: it may
   mean the text is not in the thread, the text is outside
   the bounded observe, the text is not carried as a name,
   or the element was pruned by the filter. A hit proves the
   text is present somewhere in that app's accessibility
   tree, not that it is a bubble in the thread (substring
   match on a11y names is not the V12 gate's exact
   textContent === text check on a bubble inside the thread
   container). Until a working bubble-text query is
   demonstrated on the laptop (see the dry probe below),
   this check cannot catch a reused run_id, and freshness
   rests on generation alone. A visual search of the thread
   is only a fallback with the same limit: a visual search
   that finds nothing does not prove the text is absent,
   and a bubble sitting in scrollback, missed by a visual
   search, still cannot prove a reused run_id absent: a bubble
   sitting in scrollback, missed by a visual search, is still
   a stale bubble the script's own pre-check would have to see.
   The zero-send false PASS this check existed to prevent
   (reused run_id, zero new sends, outcome PASS) is now closed
   in code anyway: a run with zero fresh sends scores FAIL
   unless --allow-resume, and a reused run_id in a fresh
   workdir is REFUSED by the run registry. If in doubt, do the a11y query; if the query
   cannot run, record that and rely on the fresh
   generation.

   Dry probe of this method (do this once, before the first
   live run, and record the result in the run log; it has
   NOT been run yet). Test the two premises separately, so a
   failure tells you which premise broke. A single query
   cannot do both: a raise identifies a pid failure and a
   hit proves both, but a miss is three-way ambiguous
   (bubbles not exposed, text outside the bounded observe,
   or the chosen known text wrong), so the probe below
   separates them with independent steps.
   - Part 1, pid mapping and app presence: run
     `computer-use a11y apps` and confirm Brave and Chrome
     both appear with PIDs. If either is absent, the method
     fails at step 1: the only count on record is "a11y apps
     lists only 6 registered apps"
     (improvements/speed-proto-pick4-summary.md:15), with
     no Brave/Chrome named, and the probe has no way past
     an absent app; record the absence and fall back to
     fresh generation plus a visual search. If both appear,
     prove the pid mapping with an element that survives
     the observe() filter: query for a KNOWN name that has
     actions or is editable (for example the message input
     itself, name "Message", which is editable, or a named
     button visible in the thread). A hit proves the pid is
     right and the tree is readable. If it raises "exact
     app PID required", the pid is wrong; re-list with
     `a11y apps` and use the listed pid, never the hyprctl
     client pid.
   - Part 2, bubble exposure: only after Part 1 hits, test
     whether bubble text is searchable at all. Pick a bubble
     text that is currently VISIBLE in the thread (read it
     from the thread by eye and record exactly how it was
     read) and query for it with the a11y query above. On a
     miss, retry once with a second currently-visible bubble
     text before concluding anything, so a wrong first
     choice does not decide the outcome. Then run a skeleton
     observe (`computer-use a11y observe --pid <atspi-pid>
     --skeleton`, which keeps every visited element) and
     search the returned snapshot JSON for the same text.
     A hit in either proves bubble text is searchable on
     that browser. A miss in both does NOT prove bubbles
     are unexposed: the text may sit outside the bounded
     observe, or may not be carried as an accessible name
     at all (describe() records ref, role, name, path,
     actions, plus editable/extents/state flags, and never
     text content). In
     that case the a11y method is unusable for freshness
     on that browser until a working query is demonstrated;
     fall back to fresh generation plus a visual search,
     and record that the method failed.
   Until this probe runs and Part 2 hits, premise A
   (bubble exposure) is UNVERIFIED and premise B (pid
   mapping) is contradicted by prior evidence for other
   apps; the freshness check rests on generation alone,
   which the runbook states plainly in step 2 above.
   Under option A (section 13.2, script's Firefox, no
   Brave/Chrome) this a11y method does not apply at all:
   there are no Brave/Chrome a11y targets, so freshness
   rests on generation alone plus a visual check of the
   threads in the script's Firefox after the harvest-first
   step.
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
   reason is record-keeping, not the ledger: with a fresh
   workdir the ledger is empty, so a reused run_id is now
   REFUSED by the run registry before the browser starts
   (same machine); the old false PASS needed a shared workdir
   with a "sent" ledger record, and even that now scores FAIL
   without --allow-resume. The fresh workdir matters because
   the ledger, results,
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
  not by the script. FAIL if and only if no visible textbox
  named "Message" exists in a window, or the picked message
  input's name does not contain "Message". Unrelated visible
  textboxes (a "Search" box, an "Email" field on a login
  page) do not fail the check by themselves: the fixture's
  own passing inventory lists a visible textbox named
  "Search" alongside one named "Message". The script itself
  gives no warning here: in run mode find_input silently picks the first visible textbox,
  so this human judgment is the only guard against typing
  into a login field (see section 0 item 1), unless the run
  uses --strict-input-name, which makes the script refuse a
  wrongly named input itself (rung 2, section 14). If either
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
  line 107), so an aria-label other than "Message" takes
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
  outcome: in harvest mode without --strict-input-name the
  script returns HARVEST-ONLY and never emits the
  no-message-input-in-inventory error (find_input is only
  called in run mode, and in harvest mode only when
  --strict-input-name is passed, script line 1644). Do not hand-log-in
  inside the script's browser unless the coordinator
  explicitly orders that step: which account sends is a
  coordinator decision (assumption, no repo evidence: one
  profile holds one Messenger session, i.e. a Firefox
  profile holds one set of Messenger cookies, treat as one
  session until verified live), and improvising a login
  invents it.

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
  (exactly 2 windows, distinct URLs, non-empty run_id,
  distinct non-empty messages per window). A
  refused plan exits 2 and starts no browser.
- The script launches its own fresh headless Firefox with a
  fresh profile under <run-dir>/profile (option A shape;
  under option B the CDP driver replaces launch_browser,
  see section 13.1 step 5) and refuses if ports
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
  The script's outcome rule (main, script line 1594) is PASS
  iff exactly 2 sent this run AND exactly 2 windows AND no
  cross-window contamination. A run in which both steps only
  skip on already-sent intents scores FAIL (zero sends this
  run), unless the operator passes --allow-resume to score a
  resume run explicitly.
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
  total is auditable. The script records visions_used in
  results.json from the --visions-used flag (default 2,
  script line 1438), never a measured count. Do
  not cite it as a measured count; the
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
  Both are now built and fixture-proven (batch 12 task 2,
  script commit f49851f, hardened in fix pass c1b623b): the
  textNew gate counts past the pre-Enter gate_baseline, and
  the cross-window check runs after both sends. That proposal is still NOT in effect for the 2-vision
  run in this runbook, which keeps 2 visions: the fixture
  proof is not a live proof, and the live run is what proves
  the gate on a real page. Rung 2 (section 14) is 0-vision by
  definition and drops VISION 2 entirely; the one-vision
  proposal can be revisited after a live run with textNew
  passing.
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
- Root cause (on pre-item-12 code; item 12 fixed this,
  see the dated correction below): act-now ALWAYS returned
  a screen-scoped after-image by construction, even when
  the input observation was window-scoped.
  scripts/first_action.py (after-capture at lines 875-893
  at todolist-push tip e702398, 22/11; the investigation
  cites ~line 656 at commit 5f5a2fd) captures the
  screen-scope after with
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
  todolist-push tip e702398, 22/11, the G28 rule; screen_scope
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
  before all side effects: on pre-amend code the overlay
  acquire and session attempt happen first (998 ms wasted),
  which is why the investigation recommends moving the scope
  check earlier (a scope assertion in first_action.py before
  the overlay step would fail faster and cheaper). That
  earlier check now exists: AMEND4 item 12 added it in
  first_action.py lines 600-627 (comment at 600: "the scope
  check runs BEFORE the
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
(scripts/first_action.py at todolist-push tip e702398):
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
overlay (first_action.py lines 600-627, see the gate bullet
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
  run, if present (option A only; under option B there is no
  <run-dir>/profile) (/tmp is a 512M tmpfs; stale Firefox
  profiles have filled it to 100% before).
- Report the outcome with the run_id and wall time: outcome
  (PASS/FAIL), per-step statuses, visions_used as recorded in
  results.json (--visions-used flag, default 2, script line
  1438, not a measured count), plus the operator's own look
  count from the run log
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
after the batch 12 task 2 fix pass (see
docs/clone2-batch12-readiness-closeout-20261122.md): 3
fully closed, 5 partial, 2 open, 2 standing. The numbering
here matches the closeout report exactly. Mapping to the
readiness report's 11 items: closed are readiness 1, 9 and
8 (item 9, script features, built in batch 12 task 2);
partial are readiness 2, 3, 4, 5 plus item 10 (cross-origin
frames, census built, live check owed); open are item 7
(readiness 3, probe part) and item 8 (readiness 6, 7);
standing are readiness 10 and 11. (Correction:
an earlier version of this header called the frames item
"item 12"; it is item 10 in this section and in the
closeout.)

CLOSED (3):
1. Runbook section 9 corrected for AMEND4 item 12
   (cbab398): the code fix IS built on todolist-push,
   `after` is scope-matching and chainable, `after_screen`
   is verification only, the scope check fires before the
   overlay (first_action.py lines 600-627). The guard stays
   mandatory on pre-amend code; record which code version
   the laptop runs. (Readiness item 1.)
2. VISION 2 monitor named (eDP-2, expected; confirm live
   with `hyprctl -j monitors`) and the run log file named
   (<run-dir>/run-log.md, every look logged with its time).
   The eDP-2 attribution is one inference step: the only
   repo record naming eDP-2 is a ws1 observe
   (worker-cl1msg2-log.md:14); the ws2 box matches it, so
   eDP-2 is expected, not proven, and the live check stands.
   (Readiness item 9.)

9. Script features (owner: whoever builds them), BUILT in
   batch 12 task 2 (script commit f49851f, hardened in fix
   pass c1b623b and again in fix pass 2, commit 00ce862,
   script 1939 lines, fixture-verified, logs in
   ~/workspace/tools/batch12-t2-fixpass2/):
   textNew in the V12 gate (COUNT_JS, script line 177;
   before-snapshot count per window in main() is recorded
   evidence only, the gate passes only on exactly one NEW
   bubble past the pre-Enter gate_baseline, settles a full
   second after first sighting it, and a double append,
   synchronous or delayed 700 ms, fails as duplicate-bubble;
   stale fixture PASS with before_count 1 and gate_count 2,
   no-send fixture FAILS v12-timeout with gate_count stuck
   at 1; the gate is appearance-based, not causal); pre-send
   reservation (intent written as "sending" after the V1
   readback and before Enter, reconciled to "sent" or
   "failed-unverified" after the gate; a later run finding
   status "sending" refuses with retry-blocked-reservation,
   proven by the driver test with and without a visible
   bubble; a failed retry never overwrites a "sent" or
   "sending" record; the ledger state machine makes "sent"
   terminal and the reservation atomic under one lock);
   intent binding (every mark records the message text,
   thread URL and selectors, and a changed plan refuses
   with retry-blocked-intent-changed; a recorded "sent"
   intent whose bubble is absent refuses with
   retry-blocked-sent-bubble-absent instead of re-sending);
   run registry (a reused run_id in a fresh workdir is
   REFUSED before the browser starts; a zero-send retry
   scores FAIL unless --allow-resume; the registry binds
   only in run mode, never in harvest mode, so the rung 2
   harvest-then-run shape works; results.json records
   registry_enabled and registry_path, so a run that
   bypassed the registry with --no-run-registry or
   --run-registry is visible in its own record); V11
   MutationObserver flag (OBSERVER_JS armed before typing,
   thread-scoped, counting mutation records; happy path
   shows v11_mutations 1 and v11_mutation_flag true,
   no-send shows 0 and false; contenteditable typing with
   a no-op Enter shows 0 on the fixture, because the fixture
   input sits outside the #thread container, so the
   thread-scoped observer cannot see its typing mutations;
   on a live page, if the message input sits inside the
   thread container, typing alone would move the count,
   which is why the flag stays evidence only, never a pass
   criterion); D3 ref stability (REF_CHECK_JS
   re-resolves the ref before input and fails fast with
   ref-stale when tag, role, name, aria-label or
   placeholder changed, nearest live textboxes listed;
   proven by the driver test, renamed input, 0 bubbles;
   tag swap and placeholder-only rename both fail);
   HCU guard compares against the harvested center unless
   the page scrolled (moved input fails geometry-moved);
   cross-window check (after both sends each thread must
   hold only its own message, matching foreign bubbles by
   containment on the raw texts; proven by the driver test,
   injected foreign bubble and prefixed foreign bubble
   detected; the outcome rule also fails the run when a
   thread vanished after the gates or holds no bubble with
   its own message); thread-missing fails fast (-1 preserved,
   never collapsed to 0). Scope: all of this is built for
   the Marionette script path (option A) only. Under option
   B the CDP driver does not exist yet and none of these
   features exist there (section 13.1 item 1); gap 9 is
   CLOSED as a build for the Marionette path, not for the
   live run as a whole. What remains is live proof: the
   fixture proof is not a live proof, and the VISION 2
   removal stays conditional until a live run passes with
   textNew. (Readiness item 8.)

PARTIAL (5: the doc part is done, a live or build part
remains):
3. Checklist 10 contradictions fixed in the workflow doc
   (login-wall mode, harvest selector checking, "ONE Zen
   instance", ledger rationale in 10.1). The runbook and
   the checklist now agree on those four. What remains:
   the workflow doc section 5 Step 0 ledger sentence is
   fixed in this pass (it said the same wrong rationale),
   and the shape-conditional wording (one-instance and
   Firefox paths) is qualified by live shape in this pass.
   (Readiness item 2.)
4. Checklist 10.3 now complete as a definition: method
   (a11y query with the AT-SPI pid from `a11y apps`),
   generation rule (fresh timestamp-based run_id), record
   requirement (run log). What remains: the dry probe
   procedure is written in section 5 but the probe itself
   is UNRUN, and the probe method as first written cannot
   work (see item 7 below for the observe() filter limit);
   the probe is redesigned in this pass. (Readiness
   item 3, definition done, probe open.)
5. Live-shape procedures written for both options
   (section 13). What remains: the coordinator's decision
   (option B or option A), the account decision, and the
   verification of whichever option is picked (CDP driver
   build for B, verified pre-seeded profile for A).
   (Readiness item 5.)
10. Cross-origin frames in the Messenger web app, tooling
    built, live check owed: the frames census is built into
    the script (FRAMES_JS, script line 229; one evaluate per
    window in the harvest, results["frames"] per window).
    Fixture-proven on the iframe variant: 1 frame per window,
    accessible true, and the input inside the frame is NOT
    inventoried (4 items per window), which demonstrates the
    limit the census exists to catch. Two honest limits: on
    file:// URLs the origin reads "null" (Firefox treats
    file origins as opaque), so the accessible flag, not the
    origin field, is the operative signal on the fixture;
    and file:// cannot reproduce a cross-origin frame at
    all, so the live check on the real Messenger page is
    still owed. What remains: the operator runs the census
    as part of the harvest-first step on the live page
    (section 14 step 1) and stops on any cross-origin frame
    (accessible false), or on a same-origin frame holding
    the input or thread. This affects both options:
    HARVEST_JS and the cdp.mjs snapshot both evaluate in
    the top frame. (New item, from the DOM/a11y crawl log,
    open verification item 6.)

6. Live Messenger input name verified against the real
   DOM (owner: operator, on the laptop, before the run):
   the aria-label is UNKNOWN, no DOM or a11y read of the
   input exists in the repo. What the fix pass closed: the
   procedure is now mechanized, not only written. HARVEST_JS
   records aria-label and placeholder as separate fields per
   item, so inventory.json carries the actual aria-label
   when the harvest reads it; --strict-input-name now also
   checks the harvested names in harvest mode and refuses
   with input-name-mismatch before any send, so no operator
   read of inventory.json is needed for the check; the
   picked name, aria-label and placeholder per window are
   logged and recorded in results["harvest_inputs"]. What
   remains: the live value itself. The plan's input_name is
   still "Message" from visual-only evidence, and the
   aria-label is only closed by the live harvest-first DOM
   read (section 6 rule: FAIL iff no visible textbox named
   "Message" exists, record the actual name on a mismatch).
   When the harvested name comes from the placeholder, the
   aria-label itself stays UNKNOWN. (Readiness item 4.)

OPEN (2):
7. Dry probe of the a11y freshness method (owner:
   operator, on the laptop, before the first live run):
   UNRUN, and the method as first written cannot work.
   scripts/a11y.py observe() only keeps elements with
   actions, editable, or in skeleton mode, and describe()
   records ref, role, name, path, actions, plus
   editable/extents/state flags, and never text content;
   query() filters that pruned list by name substring, so
   a bubble (static text, no actions, not editable) is
   dropped before query() sees it. The probe is redesigned
   in section 5 (Part 1: pid mapping with a filter
   surviving element; Part 2: bubble exposure tested
   explicitly with a skeleton observe, a miss proving
   nothing). Until Part 2 hits, freshness rests on
   generation alone. Premise A (bubble exposure) is
   UNVERIFIED; premise B (hyprctl pid is the AT-SPI pid)
   is contradicted by prior evidence. Under option A this
   method does not apply at all (no Brave/Chrome targets).
   The probe commands were re-verified against the code
   in batch 12 task 2 (todolist-push tip da46c4c:
   scripts/a11y.py observe() filter and query() unchanged,
   scripts/cu.py a11y subparser at line 2996, query
   requires --pid plus --name or --role); the probe itself
   is still UNRUN, nothing here ran it.
   (Readiness item 3, probe part.)
8. Method approval (owner: coordinator) and thread URLs,
   thread selector, bubble selector (owner: coordinator).
   Both are coordinator decisions with no repo record yet.
   What batch 12 task 2 prepared without closing this: the
   decision packet is written in the batch 12 report
   (docs/clone2-batch12-readiness-closeout-20261122.md,
   section 3) and reproduced in full in section 14.0 below,
   listing exactly what the coordinator must supply and in
   what format, including the option B vs option A decision
   and the account for option A. The fix pass extended the
   packet with four more items the run needs: who generates
   the run_id and its value, the option A binary path and
   the script re-pin it forces, the debug port per browser
   under option B, and the live-lane-free confirmation.
   Fix pass 2 added an eleventh item: who may authorize a
   resume run on the same run_id with --allow-resume, who
   the operator is, and where the run artifacts are
   preserved.
   (Readiness items 6 and 7.)

STANDING (2, checked at run time, not closable in advance):
11. Live lane must be free: no BASELINE2 or other live run
    running, and no other agent holding the laptop browser.
    The installed laptop code must still be the pre-amend
    code if a baseline is still owed. (Readiness item 10.)
12. Live measurement of the 90% accuracy bar: no live
    measurement exists yet. Synthetic grounding is 7/7 =
    100%; the live proof is owed, and the run itself must
    produce it. This is measured by the run, not a
    prerequisite to start. (Readiness item 11.)

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
clone threads, NOT the Firefox fixture, under either
option (ws2 with Brave/Chrome applies to option B only;
option A runs the threads in the script's Firefox).

### 13.1 Option B (primary): CDP driver to the real Brave/Chrome chats

Keeps G3. The script gains a CDP driver and drives the
live Brave/Chrome windows directly, using the Messenger
sessions that are already logged in there. No login step,
no profile copy.

What exists today (verified 22/11):
- scripts/cdp.mjs exists on main and todolist-push: a
  dependency-free CDP adapter (Node >=22) with
  Runtime.evaluate and a snapshot that returns rects via
  getBoundingClientRect, plus CDP Input click/type. It is
  the transport behind `computer-use browser observe/act`.
  On todolist-push only, it also has a harvest operation
  (line 227) with a DOM.getBoxModel cross-check (line 276)
  and Accessibility.getFullAXTree (line 253). On main it
  has NONE of those three: no harvest operation, no
  DOM.getBoxModel, no getFullAXTree (its operations are
  tabs/observe/act). DOM.getBoxModel and
  Accessibility.getFullAXTree are still open, per the
  bench script's own TODO (tests/two_vision_bench.py
  lines 61-64). A harvest on main returns rects for the
  requested scope's interactive elements, capped at 80
  with a truncated flag; "every actionable element" is
  not promised on either branch.
- scripts/chromium_cli.py exists on main and todolist-push:
  a repo-owned Chromium CLI wrapper that lists tabs over
  the DevTools HTTP endpoints. Default endpoint differs
  by branch: http://127.0.0.1:9222 on main,
  http://127.0.0.1:9223 on todolist-push (the whole
  main-vs-todolist-push diff of this file is the port).
  The repo contradicts itself on the port: scripts/cu.py
  lines 32-40 say the agent-managed Chromium lives on
  9223 and 9222 is Zen's BiDi port, so a run with the
  main default hits 9222, which per cu.py is Zen's BiDi
  listener, not a Chromium debug port. Always pass
  --endpoint explicitly per browser; never rely on the
  default.
- The one-vision design doc already maps the harvest and
  gate onto CDP calls (DOM.getBoxModel,
  Accessibility.getFullAXTree) in principle.

What does NOT exist, and blocks this option:
1. No wiring from tests/two_vision_bench.py to cdp.mjs.
   The script is Marionette-only; nothing in it speaks
   CDP. The driver build must implement, at minimum: a
   harvest equivalent (cdp.mjs harvest on todolist-push,
   or the snapshot plus the missing harvest operation on
   main), a send chain (click/type via CDP Input or
   Runtime.evaluate), the V12 gate (Runtime.evaluate for
   the bubble check), the HCU guard (live geometry and
   focus re-check before input), the V1 readback, V11,
   and the exactly-once pre-check, reusing the outcome
   rule. The ledger is a Python in-process class in
   tests/two_vision_bench.py while cdp.mjs runs as a
   separate Node process (cu.py:1829 spawns `node
   scripts/cdp.mjs`), so "reusing the ledger" across
   processes needs wiring that does not exist; it is not
   asserted here.
2. The user's own Brave/Chrome sessions cannot be
   attached to as they run today. What is verified:
   the user's own Chromium runs WITHOUT a remote
   debugging port (verified 2026-11-18: no
   DevToolsActivePort file, nothing listening on 9222,
   scripts/chromium_cli.py header lines 15-18). Brave
   and Chrome debug-port state was never checked: it is
   UNVERIFIED, expected-but-unproven. Check live before
   asserting option B requires a relaunch (DevToolsActivePort
   in each browser's profile dir, listening ports).
   Attaching needs Brave and Chrome relaunched with a
   debug port, which changes the live sessions and is a
   coordinator decision. Further caveat, from the DOM/a11y
   crawl log (improvements/worker-click-crawl-doma11y-log.md,
   open verification item 4): per the CDP skill docs,
   Chrome/Brave refuse the --remote-debugging-port flag on
   the default user data directory and need a custom
   profile, and the debug port cannot be enabled on an
   already-running browser (relaunch required). That
   conflicts with driving the user's already-logged-in
   Brave; verify the Linux behavior live before building
   on it. A custom profile would NOT carry the login
   session, so the relaunch path may defeat its own
   purpose.
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
   relaunch; assign a distinct debug port per browser
   and record the endpoint (port) per browser. Check
   the ports against the script's Marionette port 2828
   and BiDi port 9223 for collisions. Record how the two
   thread tabs and the logins are preserved across the
   relaunch; that preservation procedure is still open.
   Do NOT run `computer-use browser start` as a shortcut:
   it launches an agent-managed Chromium (cu.py
   Popen chromium --user-data-dir=... --remote-debugging-port=...),
   not the user's Brave/Chrome.
2. Verify attach: list tabs via chromium_cli.py with
   --endpoint per browser (never the default) and confirm
   the two thread tabs are visible.
3. Run the dry probe: harvest both threads through the
   CDP driver, confirm both inputs visible and named
   per the live DOM name (section 6), then a dry send
   of a bench string into one thread and a V12 gate
   check, proving the CDP input path works. The dry send
   IS a live message, so it is not free: it must use its
   own run_id, its own workdir and ledger, and its text
   must differ from the rung 2 plan messages (a distinct
   bench string, recorded in the run log with its run_id),
   or the rung 2 pre-check will see a stale bubble with no
   ledger record for that text and send a second copy of
   the same text. The decision packet (section 14.0) must
   name the dry send's text, run_id and ledger before the
   probe runs. Until the CDP driver exists with the
   exactly-once features of section 12 item 9, the dry
   send has no ledger at all, and it must not run.
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
   preserve the profile directory. The script has NO
   binary-path flag (its arg parser offers no --firefox,
   --binary, or --geckodriver; FF/GD are module constants,
   script lines 49-50), so "record the laptop binary path
   live" consumes nothing as written: on the laptop the
   script needs an edit to FF/GD (which changes the
   section 3 pin, 00ce862, and must be reviewed and
   re-pinned when it lands) or the exact /home/hatch
   paths to exist there. Record the laptop binary path and
   which of those two it is. The profile holds a live
   session: local only, never push it to the repo, never
   copy it into any shared artifact.
3. Verify the profile: launch Firefox with it and confirm
   both threads load. Sessions expire; re-verify before
   each run.
4. Before the run, copy the profile into <run-dir>/profile,
   excluding the disk cache: cache2 and startupCache.
   There is NO `Cache` directory in a Firefox profile
   (verified live 22/11 with the bundled Firefox 160: a
   fresh profile contains cache2 and storage, no Cache),
   so excluding "Cache" excludes nothing. Do NOT exclude
   storage/ or cookies.sqlite: they may hold the session.
   Measure the copy size live (`du -sh <run-dir>/profile`)
   before the run: /tmp is a 512M tmpfs and the copy
   budget is NOT proven to hold (even an empty profile is
   about 23M). launch_browser does makedirs with exist_ok
   and launches with -profile <profile>, so a pre-seeded
   profile is used as-is.
5. Verify the COPIED profile, not just the master: launch
   Firefox with <run-dir>/profile and confirm both threads
   load. Profile portability is an assumption, not
   evidence: no repo record addresses whether a copied
   Firefox profile carries a logged-in Messenger session.
   If the copy does not load logged in, stop; the
   procedure fails here.
6. Coordinator supplies the plan (thread URLs, thread
   selector, bubble selector) for that account's two
   threads.
7. Run steps 0, 1, 2 per the runbook. The harvest-first
   step is the live check that the session works, but it
   cannot rely on the "Message" name until the live DOM
   name verification (section 6) is closed: until then a
   harvest showing no "Message" input is ambiguous (login
   wall versus a differently-named input) and the run
   must stop, not proceed. Once the name is DOM-verified
   live, Message inputs visible means logged in; a login
   wall means the session is dead, stop.
8. After the run, delete the profile copy from /tmp (512M
   tmpfs), keep the master profile local for re-runs.

Option C (not a procedure, listed so the choice is
explicit): move the threads to Zen and build an attach
mode (Zen relaunched with -marionette, geckodriver
--connect-existing, proven on the Firefox stand-in in
batch 1). Requires the script to gain an attach mode and
the coordinator to relaunch Zen on the laptop.

## 14. Rung 2: live 0-vision benchmark

Rung 2 is the acceptance test for the rewrite, as defined
in improvements/worker-arch-review-log.md section 4: a
0-vision live benchmark, same shape as the 2-vision
benchmark but against the REAL clone chats on ws2 (not the
local fixture in headless Firefox): DOM harvest, plan,
execute, DOM verify, zero screenshots in the loop, accuracy
>= 90%, total wall time measured end to end including
transport. Vision is used only for a final visual sanity
check if the user asks for one.

What 0-vision means here, exactly: the agent takes zero
observations during the step-2 run invocation. No VISION 2
look at the threads at the end, and no inventory read by the
agent during the run (the script still runs its one-shot DOM
harvest per window; a DOM evaluate the agent never reads is
a cheap DOM read, not a vision). The step-1 harvest-first
inventory read IS a DOM harvest read, so it counts as 1
vision of pre-run preparation outside the step-2 budget,
under section 8's own definition ("one DOM harvest the agent
reads"); the 0 counts the run invocation only, the same
accounting the 2-vision run already uses (section 6 operator
reads inventory text; section 8 counts only the in-run
harvest as VISION 1). The agent reads only the script's JSON
results (outcome, per-step statuses, counts) and the run
log during step 2. That is why rung 2 needs the script to check
programmatically what the 2-vision run leaves to operator
judgment: the --strict-input-name flag (a wrongly named
input fails closed instead of being typed into), the
textNew V12 gate (a stale bubble cannot pass a new send),
the pre-send reservation (a crashed attempt cannot be
re-sent blindly), the D3 ref check (a renamed input fails
fast), the cross-window check (a message in the wrong
thread fails the run), and the frames census (the harvest
records every frame per window in results.json, and the
operator stops the run on any cross-origin frame or any
frame holding the input or thread; the census itself never
fails the run in code, it is recorded evidence the
operator must read). All six are built for the Marionette
script path in script commit f49851f, hardened in fix
pass c1b623b and again in fix pass 2, commit 00ce862, and
fixture-proven; see section 12 item 9 and item 10. Under
option B the CDP driver does not exist yet and none of
the six exist there. The 2-vision run in sections 6-8
keeps its two agent looks; rung 2 drops both by
definition.

Note on the 0-vision scoping above: the acceptance test
as written in the arch-review log says "0-vision live
benchmark" without scoping, and the scoping used here
(0 during the step-2 run invocation, the step-1 harvest
read counted as 1 vision of pre-run preparation) narrows
that acceptance criterion. The narrowing is proposed
here, not decided: it needs coordinator approval before
a rung 2 run is scored against it.

Hard constraint, kept: rung 2 acceptance runs on the real
clone threads, NOT the Firefox fixture, under either live
shape. The fixture runs in this runbook prove the script
only; they are not rung 2.

### 14.0 Prerequisites (all must hold before step 1)

1. Coordinator decision: the method is approved for a live
   run, and the live shape is picked (option B primary,
   section 13.1, or option A fallback, section 13.2). The
   coordinator's decision packet is listed in the batch 12
   report (docs/clone2-batch12-readiness-closeout-20261122.md,
   section 3). No decision, no run.
2. Coordinator supplies the live plan: two real thread URLs
   (must differ), thread selector and bubble selector per
   thread, and the run_id. The script validates the plan
   before any browser starts (exactly 2 windows, distinct
   URLs, non-empty run_id, distinct non-empty messages) and
   refuses otherwise (exit 2).
3. Script pin: tests/two_vision_bench.py at commit 00ce862,
   1939 lines. Any other hash means an unreviewed change
   sits on top; stop and report.
4. Live lane free: no BASELINE2 or other live run running,
   no other agent holding the laptop browser. Confirm with
   the coordinator; do not guess.
5. Run machine ready: the script's Firefox binary,
   geckodriver and venv at the hardcoded paths (script
   lines 49-50) under option A; under option B the CDP
   driver and debug ports instead (section 13.1). /tmp has
   room (512M tmpfs; `df -h /tmp`) and, under option A,
   ports 2828 and 9223 are free; under option B the
   per-browser debug ports are free instead (one distinct
   port per browser, recorded, checked against 2828 and
   9223). A fresh --workdir per run.
6. Under option A, the pre-seeded logged-in profile is
   verified (section 13.2 steps 2-5): the COPIED profile
   loads logged in with both threads reachable. Under
   option B, both browsers are relaunched with distinct
   debug ports, the tabs are listed per browser, and the
   dry send proves the CDP input path types into the
   contenteditable input (section 13.1 steps 1-3).
7. The run_id is fresh by generation (timestamp-based,
   never reused, including from a failed attempt). The
   run_id freshness check in section 5 still applies:
   with textNew the gate itself no longer passes on a
   stale bubble, and the run registry refuses a reused
   run_id in a fresh workdir while a same-workdir retry
   scores FAIL without --allow-resume, but the registry
   is per-machine, so the hand check is still required as
   the backstop. Record the check in the run log. Under
   option A the a11y method does not apply (no
   Brave/Chrome targets); freshness rests on generation
   plus the harvest-first DOM read.

Decision packet (reproduced here so a runbook-only reader
sees the same list; the batch 12 report, section 3, is
the same 11 items):
1. Method approval: yes or no for a live run of the
   2-vision benchmark (sections 6-8) or rung 2 (section
   14), for a named run_id.
2. Live shape: option B (primary, CDP driver to the real
   Brave/Chrome chats on ws2) or option A (fallback,
   script's Firefox with a pre-seeded logged-in profile).
   If option B: the CDP driver build (whoever builds it)
   and the debug-port relaunch decision. If option A: the
   account holding the two threads.
3. Thread URLs: two real thread URLs, one per clone, must
   differ. Thread selector and bubble selector per thread
   (the default bubble selector is fixture-shaped; a live
   plan MUST override it, the V12 gate requires exact
   textContent === text).
4. input_name per thread (default "Message", from
   visual-only evidence; the live harvest-first read
   verifies it, gap 6).
5. v12_gate_s (default 5 s; raise it only if the live
   thread is slow to render, and record the value used).
6. Confirmation of --confirm-live for the named run_id.
7. run_id owner and value: who generates the run_id for
   this run and what its value is (timestamp-based, never
   reused, including from a failed attempt). The script
   binds the run_id to the ledger path of its first run in
   the shared registry; a reused run_id in a fresh workdir
   is REFUSED, so the value must be fresh and the owner
   must be named. The registry path is the default
   ~/.cache/two_vision_bench/run_registry.json; never pass
   --no-run-registry or --run-registry on a live run.
8. Option A binary path: the laptop Firefox binary and
   geckodriver paths the script must use (FF/GD are module
   constants, script lines 49-50; an edit changes the
   section 3 pin and must be reviewed and re-pinned when it
   lands), and whether the exact /home/hatch paths exist on
   the laptop instead.
9. Debug port per browser under option B: one distinct
   port per browser (Brave, Chrome), recorded, checked
   against 2828 and 9223. Batch 12 task 3 (sibling task,
   endpoint naming rule + guard test for the port-split) is
   the authority on debug-port endpoints; the rung 2
   procedure requires a distinct debug port per browser,
   passed explicitly, never the default.
10. Live-lane-free confirmation: no BASELINE2 or other live
    run running, and no other agent holding the laptop
    browser, confirmed with the coordinator for this run_id.
11. Resume authorization, operator, and artifact
    destination: who may authorize a resume run on the
    same run_id with --allow-resume (item 7 says a run_id
    is never reused, including from a failed attempt; a
    resume run is the one exception, and it needs a named
    authorizer and evidence the run_id was genuinely sent
    before, per section 14.3), who the operator is (who
    runs steps 0 and 1 and the hand checks on the laptop),
    and where the run artifacts are preserved after the
    run (section 14.5 requires them out of /tmp
    immediately; name the destination).

### 14.1 Step 1: harvest-first (before any send)

Run --mode harvest with the live plan first, with
--strict-input-name so the script itself checks the
harvested names (mechanized, fix pass): a wrongly named
input fails closed with input-name-mismatch before any
send, and no operator read of inventory.json is needed
for the check. The frames census is read from
results.json:

```
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --plan <live-plan.json> --mode harvest \
  --live --confirm-live --strict-input-name \
  --workdir <harvest-dir> --print-inventory
```

Required outcomes before proceeding, all read from
<harvest-dir>/results.json and <harvest-dir>/inventory.json,
no agent look at the threads:
- Outcome HARVEST-ONLY, exit 0. Any other outcome stops
  the run.
- results.json "frames" for each window: no frame with
  accessible false (a cross-origin frame), and no frame
  at all holding the input or thread. If the inventory
  shows no visible textbox named "Message" in either
  window, STOP: the input may be inside a frame, behind
  the login wall, or differently named. Do not proceed,
  do not guess.
- The inventory lists, in each window, a visible textbox
  whose name contains "Message" (case-insensitive). The
  script decides this in harvest mode with
  --strict-input-name (fails closed on a mismatch); the
  operator records the picked name, aria-label and
  placeholder per window from results.json
  "harvest_inputs" (inventory.json carries aria-label and
  placeholder as separate fields per item). FAIL if and
  only if no visible textbox named "Message" exists in a
  window, or the picked message input's name does not
  contain "Message". Unrelated visible textboxes do not
  fail it. On a mismatch, stop, record the actual name in
  the run log, do not proceed. The live DOM name
  verification (section 12 item 6) is supplied by this
  read: record the harvested resolved name, aria-label and
  placeholder per window in the run log. When the resolved
  name comes from the placeholder, the aria-label itself
  stays UNKNOWN. Note the step-1 read of inventory.json
  is pre-run preparation outside the 0-vision step-2
  budget (section 14 intro); it is recorded in the run
  log as 1 vision of preparation.
- The harvest does NOT verify thread_selector or
  bubble_selector (they are only touched inside send_one
  via the gate, after typing). The selectors stay
  unverified until the first V12 gate, so the first send
  is the first real selector test: a wrong selector means
  the message may be typed but unseen (v12-timeout, intent
  failed-unverified, check the thread by hand, new run_id).
- If the harvest shows a login wall (visible textboxes
  named "Email" and "Password", no textbox named
  "Message"), the run is FAIL before anything is sent and
  the blocker in section 0 stands. Do not hand-log-in
  inside the script's browser unless the coordinator
  explicitly orders that step.

### 14.2 Step 2: the live run (0-vision)

Only after steps 0 (section 5) and 1 (14.1) pass, the live
lane is free, and the coordinator has said run for this
run_id. One command, with --strict-input-name and
--visions-used 0 (so results.json records 0, not the
2-vision default). This command is the OPTION A
invocation: it runs the script's Marionette/Firefox path
(launch_browser). Under OPTION B the CDP driver replaces
launch_browser per section 13.1 step 5, and this command
as written is NOT the option-B run: running it verbatim
under option B launches headless Firefox against the real
threads, hits the login wall, and fails closed via
--strict-input-name. Do not run it verbatim under option B.

```
~/workspace/tools/venv/bin/python tests/two_vision_bench.py \
  --plan <live-plan.json> --mode run \
  --live --confirm-live --strict-input-name --visions-used 0 \
  --workdir <run-dir>
```

What the script does, in order, with no agent look in
between: VISION 1 one-shot harvest per window (DOM reads
only); frames census per window; before-snapshot counts
per window (recorded evidence only, not the gate
baseline); strict input-name check
(fails closed with input-name-mismatch before any send);
plan-once send chain per clone (D3 ref check first, then
scroll, HCU guard on the harvested center unless the page
scrolled, real pointer click, focus check, V11 observer
armed before typing, type, V1 readback, pre-send
reservation written as "sending", Enter, textNew V12 gate
requiring exactly one NEW bubble past the pre-Enter
gate_baseline, a double append failing as
duplicate-bubble); stop at the first failure,
later steps recorded not-executed; cross-window check
after both sends; outcome by DOM read only.

The agent does not type, click, send, observe, or look at
anything during the run. The operator's job is the checks
around it (steps 0 and 1, and reading results.json after),
not the sends.

### 14.3 Pass criteria (DOM only)

- Harvest: PASS iff the harvest-first step (14.1) passed:
  HARVEST-ONLY, both inputs visible and named "Message",
  no cross-origin frame, no input hidden in a frame.
- Sends: PASS iff both steps report "sent" in results.json,
  each with v12_gate_ok true, gate_count exactly
  gate_baseline + 1 (exactly one NEW bubble landed, not a
  stale one and not a double append), and reservation
  "sending" reconciled to "sent" in the ledger
  (<run-dir>/ledger.json is the source for that check; a
  step record only carries reservation "sending").
  v11_mutations is recorded evidence only (thread-scoped
  mutation-record count) and is NOT a pass criterion: it is
  entailed by gate success and can be true on gate failure
  (an incoming message), so it proves nothing on its own.
  input_cleared_after_enter is recorded the same way. A
  step reporting "skipped-already-sent" never scores PASS
  on a fresh run: the outcome rule requires 2 sends this
  run. A resume run scores PASS only when the operator
  passes --allow-resume explicitly and the run log shows
  this run_id was genuinely sent before (a retry after a
  crash, not a fresh run); on a fresh run_id a skip means
  the run_id was reused, and the run is FAIL on procedure.
- Cross-window: PASS iff results.json "cross_window_check"
  shows foreign 0 in both threads (each thread holds only
  its own message). Any foreign count above 0 fails the
  run even when both sends report sent.
- Accuracy bar: 90% or more (coordinator's bar, click2 log
  line 32). With 2 sends, 2/2 = 100% passes and 1/2 = 50%
  fails the bar, so in practice PASS requires both
  messages. There is no partial pass. Precision note, as
  in section 8: the bar is about grounding accuracy per
  action, while this runbook operationalizes it as
  message-delivery rate (2/2 messages landed); with 2
  sends only 100% or 50% is possible, so the bar cannot
  distinguish 90% grounding accuracy from 100%. The
  criterion as stated measures delivery, not grounding
  accuracy. Live accuracy is what this run measures; it
  is owed, not claimed.
- Wall time: total wall time measured end to end including
  transport. Record the operator-side command wall time
  (shell `time` around the run command, or start and end
  timestamps in the run log) as the end-to-end figure; the
  script-internal wall_s in results.json (monotonic time
  from after arg parsing to benchmark_finished) excludes
  interpreter and import startup and pre-t_start work, but
  includes the browser launch (launch_browser runs after
  t_start is set), so cite it only as the script-internal
  portion. The arch-review acceptance test requires it
  measured, not estimated.
- Vision count: 0 during the step-2 run invocation. The
  agent reads no observation and no inventory text during
  the run. The step-1 harvest-first inventory read is
  pre-run preparation outside the budget and is recorded
  in the run log as 1 vision of preparation (section 14
  intro); the operator's look count for the run itself is
  0 by definition. If the user asks for a final visual
  sanity check, that look is outside the run and must be
  logged in the run log with its time; it does not change
  the 0-vision count of the run itself. Pass
  --visions-used 0 on the step-2 command so results.json
  records 0; the 2-vision default must not be cited as
  rung 2's vision count.

### 14.4 Stop conditions (abort, do not push on)

- Stop at the first failed step. The script does this
  itself; do not restart the chain mid-run.
- If a send ends in v12-timeout, STOP. Check the thread by
  hand. Never re-run with the same run_id: the ledger
  marks the intent failed-unverified and refuses the
  retry. To retry, fix the thread/bubble selectors first,
  then use a NEW run_id and repeat the freshness check
  (section 5).
- If a send ends in retry-blocked-reservation, STOP. A
  previous attempt reserved the intent but never
  reconciled it; the message may have landed. Check the
  thread by hand, use a NEW run_id, never re-send the
  same intent.
- If a send ends in ref-stale, STOP. The input was renamed
  or replaced between harvest and send. Re-harvest with a
  fresh run_id; do not click the stale ref.
- If a send ends in input-name-mismatch, STOP before
  anything is sent. Record the actual name; the plan's
  input_name is wrong for this thread.
- If the cross-window check shows contamination, the run
  is FAIL even if both sends report sent. Report which
  thread holds the foreign message; do not re-send to
  "make up" for it.
- If either thread becomes unreachable, or the browser
  crashes, STOP and report the state (which intents are
  sent, which are failed-unverified or still "sending")
  before doing anything else. A click landing on the wrong
  window has no script check that detects it, so it is an
  operator-observed stop, not a script trigger: if the run
  log or the V1 readback shows input typed into the wrong
  window, stop the same way.
- If --confirm-live was not explicitly given by the
  coordinator for this run, STOP. The script refuses
  without it, and the URL gate refuses any non-fixture
  plan without both --live and --confirm-live.
- If the harvest-first step fails (no textbox named
  "Message" in either window, login wall, cross-origin
  frame), STOP before any send.
- If the plan validation refuses (exit 2), STOP. Fix the
  plan. Do not bypass the validation.
- A value-mismatch means nothing was sent (Enter was not
  pressed). A v12-timeout means the message may have been
  typed and may have landed unseen, so the thread must be
  checked by hand. Do not treat them the same.

### 14.5 After the run: preserve and report

- Preserve the full log, results.json, inventory.json, and
  ledger.json out of /tmp IMMEDIATELY (fix-pass logs were
  once lost to a /tmp wipe). Also preserve the plan file
  used, the harvest-first results.json, and the run_id
  freshness check record from section 5.
- Delete the profile/ dir under the run workdir after the
  run, if present (option A only; under option B there is
  no <run-dir>/profile) (/tmp is a 512M tmpfs; stale Firefox
  profiles have filled it to 100% before).
- Report the outcome with the run_id and wall time:
  outcome (PASS/FAIL), per-step statuses with
  before_count, gate_baseline, gate_count, v11_mutations,
  v11_mutation_flag and reservation per step,
  cross_window_check, frames census, and visions_used 0
  (--visions-used 0 on the step-2 command, so results.json
  records 0). Never edit a result file after the run.
- Confirm no Firefox process was left running and /tmp has
  room again.

### 14.6 What rung 2 still needs (not closable here)

- Coordinator decisions (section 12 item 8): method
  approval, thread URLs/selectors, option B vs option A,
  account for option A. The decision packet is in the
  batch 12 report, section 3.
- Live DOM name verification (section 12 item 6): closed
  only by the harvest-first read in step 1, at run time.
- A11y dry probe (section 12 item 7): UNRUN. Under option
  B it is the only executable freshness check besides
  generation; under option A it does not apply.
- Frames live check (section 12 item 10): closed only by
  the harvest-first census on the live page, at run time.
- Live lane free (section 12 item 11) and live measurement
  of the 90% bar (section 12 item 12): checked and
  measured by the run itself.

## 15. Sources

- Batch 10 assignment: coord/clone2.md line 868, commit
  422f4b0.
- Batch 11 task 2 closeout: docs/
  clone2-live-run-readiness-closeout-20261122.md (verdict
  still NOT READY, exact remaining items listed there and
  in section 12 above).
- Script: tests/two_vision_bench.py (1939 lines, 00ce862);
  FF/GD lines 49-50; HARVEST_JS line 72; GATE_JS line 156;
  COUNT_JS line 177; OBSERVER_JS line 203; FRAMES_JS line
  229; REF_CHECK_JS line 248; TEXTS_JS line 1154; find_input
  lines 524-533; launch_browser lines 535-566; send_one line
  682; harvest_window line 1126; frames_census line 1135;
  thread_texts line 1164; bubble_count_for line 1172;
  cross_window_check line 1183; default_plan run_id line
  1226; validate_plan line 1283;
  registry_check_and_record line 1367; URL gate lines
  1533-1541; visions_used flag line 1438, recorded line
  1581; outcome rule lines 1883-1892;
  no-message-input-in-inventory lines 1644 (harvest mode)
  and 1686 (run mode).
- Batch 12 task 2: docs/clone2-batch12-readiness-closeout-20261122.md
  (textNew, pre-send reservation, V11, D3, frames census,
  rung 2 procedure; verdict still NOT READY); script
  commit f49851f, hardened in fix pass c1b623b and again in
  fix pass 2, commit 00ce862; fixture logs and artifacts in
  ~/workspace/tools/batch12-t2/, ~/workspace/tools/batch12-t2-fixpass/
  and ~/workspace/tools/batch12-t2-fixpass2/.
- Workflow doc: docs/two-vision-benchmark-workflow-20261122.md
  (1121 lines); section 5 plan shape; section 6 failure
  meanings; section 9 C12 not used; section 10 checklist.
- Design doc: docs/clone2-one-vision-design-20261122.md
  (792 lines, c267411; updated in the batch 12 task 2 fix
  pass and again in fix pass 2); section 1 vision budget; section 3
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
  57-60 (app, exact app PID required), lines 83-117
  (observe, keeps only elements with actions, editable,
  or in skeleton mode; describe records ref, role, name,
  path, actions, plus editable/extents/state flags, and
  never text content); scripts/cu.py line 2906
  (a11y subparser), lines 3150-3151 (query requires
  --pid plus --name or --role), all todolist-push tip
  e702398 (on main the same code is at cu.py lines 2332
  and 2519-2520); scripts/cu.py line 30 (STATE,
  ~/.cache/agent-computer-use).
- Operator-guard code pins (todolist-push tip e702398,
  22/11; line numbers drift as the coordinator's lane
  lands commits, re-verify before citing): scripts/cu.py
  lines 1773-1775 (G28 raise), lines 2235-2244
  (scope-matching _after_capture, result['after'] at 2241);
  scripts/first_action.py line 337 (_scope_after def),
  lines 600-627 (scope check before the overlay),
  lines 875-893 (after-capture: observe_screen at 878,
  envelope['after_screen'] at 880-883, envelope['after']
  at 890).
- CDP building blocks for option B: scripts/cdp.mjs
  (dependency-free CDP adapter, Runtime.evaluate, snapshot
  with rects via getBoundingClientRect, CDP Input
  click/type; harvest with DOM.getBoxModel cross-check and
  Accessibility.getFullAXTree exist on todolist-push only,
  lines 227, 253, 276, NOT on main); scripts/
  chromium_cli.py (tab listing over DevTools HTTP, --endpoint
  flag; default http://127.0.0.1:9222 on main,
  http://127.0.0.1:9223 on todolist-push; the repo
  contradicts itself on the port, cu.py lines 32-40 say the
  agent-managed Chromium is 9223 and 9222 is Zen's BiDi
  port).
- VISION 2 monitor: improvements/worker-cl1msg2-log.md
  (screen eDP-2, region [2464,902,1920,1200]).
- Cross-origin frames and the Brave debug-port caveat:
  improvements/worker-click-crawl-doma11y-log.md (open
  verification items 4 and 6).
