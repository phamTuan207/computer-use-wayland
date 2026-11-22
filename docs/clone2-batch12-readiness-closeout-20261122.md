# Batch 12 task 2: close the 5 open readiness gaps, prepare rung 2

Date: 2026-11-22. Build 10:51-11:20 +07; fix pass same day,
verification runs 11:37-11:42 +07 (04:37-04:42Z); fix pass 2
same day, verification runs 12:30-12:40 +07 (05:30-05:40Z,
driver re-run 05:33-05:36Z, baselines 05:37-05:39Z).
Verdict: still NOT READY.
New count: 3 fully closed, 5 partial, 2 open, 2 standing
(was 3 / 4 / 3 / 2 after the batch 12 task 2 build, 2 / 3 / 5 / 2
after batch 11 task 2). Numbering matches
runbook section 12 exactly. Nothing here ran live; no live
message was sent, and no live run has happened.

Assignment: batch 12 task 2, coord/clone2.md commit 0521d6c
(10:44 22/11). Close the 5 open gaps to the extent possible
without sending live messages, and prepare the rung 2 run
procedure (live 0-vision on the real clone chats at ws2)
with option A fallback. Any gap that can only be closed by
sending a live message is stated as such, not closed by
sending one.

Sources read before writing (all verified):
- Closeout: docs/clone2-live-run-readiness-closeout-20261122.md,
  249 lines, batch 11 task 2 (2 closed, 3 partial, 5 open,
  2 standing).
- Runbook before: docs/two-vision-live-runbook-20261122.md,
  1277 lines. After this task: 1650 lines. After the fix
  pass: 1783 lines. After fix pass 2: 1928 lines.
- Workflow doc before: docs/two-vision-benchmark-workflow-20261122.md,
  798 lines. After this task: 914 lines. After the fix
  pass: 1004 lines. After fix pass 2: 1121 lines.
- Script before: tests/two_vision_bench.py, 868 lines, commit
  c267411. After this task: 1200 lines, commit f49851f.
  After the fix pass: 1637 lines, commit c1b623b.
  After fix pass 2: 1939 lines, commit 00ce862.
- Design doc: docs/clone2-one-vision-design-20261122.md,
  764 lines at the fix pass, 792 lines after fix pass 2,
  commit 00ce862.
- Design doc: docs/clone2-one-vision-design-20261122.md,
  section 4.2 (textNew is the V12 gate; fix-pass dated note:
  the built baseline is the pre-Enter gate_baseline, not
  batch start), section 4.3.2 (pre-send reservation, now
  BUILT), section 7 (reservation, D3, V11 now BUILT).
- Rung 2 definition: improvements/worker-arch-review-log.md,
  section 4, on origin/todolist-push (acceptance test for
  the rewrite: a 0-vision live benchmark, same shape as the
  2-vision benchmark but against the REAL clone chats on
  ws2, DOM harvest, plan, execute, DOM verify, zero
  screenshots in the loop, accuracy >= 90%, total wall time
  measured end to end including transport; vision only for
  a final visual sanity check if the user asks for one).
- A11y probe code: scripts/a11y.py and scripts/cu.py on
  origin/todolist-push, tip da46c4c (observe() filter and
  query() unchanged; a11y subparser at cu.py line 2996,
  query requires --pid plus --name or --role).

## 1. Per-gap outcomes

### Gap 9 (unbuilt features): CLOSED as a build

All four features are built in the script (commit f49851f,
hardened in fix pass c1b623b and again in fix pass 2,
commit 00ce862) and fixture-verified (see
section 2). textNew in the V12 gate (COUNT_JS; the gate
passes only on exactly one NEW bubble past the pre-Enter
gate_baseline, settles a full second after first sighting
it, and a double append, synchronous or delayed 700 ms,
fails as duplicate-bubble); pre-send reservation (intent
written as "sending" after the V1 readback and before
Enter, reconciled to "sent" or "failed-unverified" after
the gate; a later run finding status "sending" refuses
with retry-blocked-reservation); V11 MutationObserver flag
(OBSERVER_JS armed before typing, thread-scoped, counting
mutation records per send); D3 ref stability
(REF_CHECK_JS re-resolves the ref before input and fails
fast with ref-stale when tag, role, name, aria-label or
placeholder changed, nearest live textboxes listed);
cross-window check (after both sends each thread must
hold only its own message, matching foreign bubbles by
containment on the raw texts); run registry (a reused
run_id in a fresh workdir is REFUSED before the browser
starts; the harvest never binds the registry, so the rung
2 harvest-then-run shape with the same run_id in
different workdirs works); intent binding (every ledger
mark records message, thread URL and selectors, and a
changed plan under the same run_id refuses with
retry-blocked-intent-changed); sent-bubble-absent refusal
(a recorded "sent" intent whose bubble is absent refuses
instead of re-sending).

What remains is live proof: the fixture proof is not a
live proof. VISION 2 stays for the 2-vision run until a
live run passes with textNew; rung 2 drops it by
definition (section 4).

Honest limits of the build, recorded here so nobody
over-reads it:
- The reservation closes the process-death gap only when
  the same ledger is reused (same workdir or --ledger). A
  fresh workdir has an empty ledger, so the run registry
  refuses that case outright and the run_id freshness
  check still stands as the human backstop.
- A failed retry never overwrites a "sent" or "sending"
  ledger record with "failed" (fix pass, council 1 issue
  1 and redteam F1). An exception after the reservation
  reconciles to failed-unverified instead of leaving
  "sending" sticky.
- The pre-check skip changed: it now skips only when the
  ledger says the intent was already sent AND the bubble
  is visible. A stale bubble with no ledger record does
  NOT skip; the send proceeds and the textNew gate
  requires a new bubble. A run with zero fresh sends
  scores FAIL, not PASS, unless --allow-resume is passed.
- The gate is appearance-based, not causal: it proves a
  bubble with the exact text appeared after the baseline,
  not that our Enter caused it. Mitigation is unique
  message text plus a free live lane. The gate baseline
  is the pre-Enter count, not the batch-start snapshot:
  before_count is recorded evidence only and the gate
  never consults it (design doc 4.2 dated note).
- The D3 check compares tag, role, name, aria-label and
  placeholder separately at the ref, and the HCU guard
  compares against the harvested center unless the page
  scrolled. An element replaced by an identical twin
  (same tag, role, name, different identity) still passes
  it; the HCU guard and the V1 readback are the backstops.
- The fix pass 2 hardening (intent binding, sent-bubble-absent
  refusal, 1.0 s gate settle, ledger state machine, registry
  and ledger corruption refusal) is on the Marionette path
  only. The CDP path for option B has no such code: the
  option B driver does not exist yet, so none of the
  exactly-once or gate guarantees are proven for it, and the
  rung 2 procedure under option B is a different build, not
  a rerun of this one.
- The V11 observer is scoped to the thread container and
  counts mutation records, not callbacks. A send that
  types but never appends a bubble shows 0 mutations on
  an input, and typing into a contenteditable input that
  never sends also shows 0 (proven by the CE no-send
  fixture run); the flag is recorded evidence, not a pass
  criterion. That CE proof is on the fixture's own
  contenteditable layout only: the live Messenger input is
  a different element in a different layout, so V11's
  behavior on the real input is UNVERIFIED until a live
  run records it.

### Gap 10 (cross-origin frames): PARTIAL

The tooling is built and the procedure is written; the
live check itself is still owed at run time. The frames
census is built into the harvest (FRAMES_JS, one evaluate
per window, results["frames"] per window) and
fixture-proven: the iframe variant harvests 4 items per
window (the input inside the frame is NOT inventoried,
which demonstrates the limit) and the census reports 1
frame per window, accessible true. The rung 2 procedure
(runbook section 14 step 1) runs the census on the live
page and stops on any cross-origin frame (accessible
false) or on an input hidden in a frame.

Two honest limits: on file:// URLs the origin reads
"null" (Firefox treats file origins as opaque), so the
accessible flag, not the origin field, is the operative
signal on the fixture; and file:// cannot reproduce a
cross-origin frame at all, so the live check on the real
Messenger page is still owed.

### Gap 6 (input name): PARTIAL

The aria-label is still UNKNOWN, and the live value is
only closed by the live harvest-first DOM read at run
time. What the fix pass closed: the procedure is now
mechanized, not only written. HARVEST_JS records
aria-label and placeholder as separate fields per item,
so inventory.json carries the actual aria-label when the
harvest reads it; --strict-input-name now also checks the
harvested names in harvest mode and refuses with
input-name-mismatch before any send, so no operator read
of inventory.json is needed for the check; the picked
name, aria-label and placeholder per window are logged
and recorded in results["harvest_inputs"] (proven by the
iframe-strict run: HARVEST-ONLY with both windows
recorded as name, aria-label and placeholder "Message").
When the harvested name comes from the placeholder, the
aria-label itself stays UNKNOWN. Owner for the remaining
live value: operator, on the laptop, before the run
(runbook section 14 step 1 records the harvested
aria-label and placeholder per window in the run log).

### Gap 7 (a11y dry probe): OPEN

Still UNRUN. The probe commands were re-verified against
the code at todolist-push tip da46c4c (scripts/a11y.py
observe() keeps only elements with actions, editable, or
in skeleton mode; describe() records ref, role, name,
path, actions, plus editable/extents/state flags, and
never text content; query() calls observe() without
skeleton and filters by name substring; scripts/cu.py
a11y subparser at line 2996, query requires --pid plus
--name or --role at lines 3254-3255). The probe procedure
in runbook section 5 stands as written (Part 1 pid
mapping with a filter-surviving element, Part 2 bubble
exposure with a skeleton observe). Nothing here ran the
probe: this VM has no AT-SPI session bus and no
Brave/Chrome targets to probe. Premise A (bubble
exposure) is UNVERIFIED; premise B (hyprctl pid is the
AT-SPI pid) is contradicted by prior evidence. Owner:
operator, on the laptop, before the first live run.
Under option A the method does not apply at all.

### Gap 8 (method approval, thread URLs/selectors): OPEN

Coordinator decisions with no repo record yet. Prepared,
not closed: the decision packet is in section 3 below,
listing exactly what the coordinator must supply and in
what format. Owner: coordinator.

## 2. Verification runs (fixture only, this VM)

All runs headless Firefox 160.0.1, repo venv python, one
run per case, each with its own --workdir under
/tmp/two_vision_bench/b12t2-*. Wall clock UTC, elapsed
from a monotonic clock. All logs, results.json,
inventory.json and ledger.json preserved in
~/workspace/tools/batch12-t2/ (logs/ and runs/). The
profile-deletion, /tmp percentage and no-Firefox claims
from the first version of this paragraph cannot be
verified from the preserved record (the preserved run
dirs hold no profile dirs and no df/ps artifact) and are
struck here, not repeated. The batch-12 run window end
was likewise corrected in the workflow doc (last run
finished 04:00:53.78Z per driver.log).

- Happy path with --strict-input-name (b12t2-happy): PASS,
  wall 15.3843 s (launch 4.2887 s, attach 5.4269 s, both
  slow from a contended shared VM, same shape, not a
  defect). Sends 1.8286 s and 0.5765 s. Both steps:
  before_count 0, gate_baseline 0, gate_count 1,
  reservation "sending" reconciled to "sent",
  v11_mutations 1, v11_mutation_flag true,
  v11_input_events 47. Cross-window check clean (own 1,
  foreign 0 per thread). Frames census empty per window.
- Exactly-once driver (b12t2-once): PASS. Call 1 sent in
  1.0249 s, 1 bubble; call 2 skipped-already-sent in
  0.0349 s, still 1 bubble.
- Stale bubble, textNew pass (b12t2-stale, fixed plan
  bench-stale-001, stale fixture): PASS, wall 8.1306 s.
  Both steps: before_count 1, count_at_precheck 1,
  gate_baseline 1, gate_count 2. The gate waited for a NEW
  bubble past the stale one; the old presence gate would
  have passed immediately.
- Stale bubble, textNew timeout (b12t2-nosend, fixed plan
  bench-stale-001, no-send fixture, 2 s gate): FAIL as
  designed, wall 8.5256 s, exit 1. Clone1 v12-timeout with
  gate_count 1 (stale bubble only, baseline 1, never grew),
  v11_mutations 0, v11_mutation_flag false, reservation
  "sending" reconciled to failed-unverified; clone2
  not-executed. This proves the gate does NOT pass on the
  stale bubble.
- Strict input name refusal (b12t2-strictbad, plan
  input_name "Zzz"): FAIL as designed, exit 1. Step 1
  input-name-mismatch (expected "Zzz", actual "Message",
  ref #msg-input), no ledger file written, nothing typed
  or sent.
- Iframe harvest (b12t2-iframe, --mode harvest):
  HARVEST-ONLY. 4 items per window; the input inside the
  iframe is NOT inventoried. Frames census: 1 frame per
  window, accessible true, origin "null".
- Batch 12 task 2 driver (b12t2-driver): PASS, wall
  7.3978 s. D3 ref-stale: renamed input, error ref-stale,
  0 bubbles, 2 nearest candidates listed. Cross-window:
  injected foreign bubble detected (clone2 foreign clone1
  1, clone1 foreign clone2 0). Reservation block: seeded
  status "sending" refused with retry-blocked-reservation
  both with no bubble (0 bubbles after) and with a visible
  bubble (still 1 bubble, no second send).

Regression check on the old behavior: the exactly-once
driver still passes, and the happy path still passes with
the new fields present. The old wrong-selector retry
behavior (run 1 v12-timeout, run 2 retry-blocked-
unverified) is unchanged in code: in send_one the
thread-missing check runs first, then the
failed-unverified block, then the reservation block, then
the intent-binding check, then the sent-skip (script
lines 744-826 at commit 00ce862). It was
not re-run here; the fix-pass logs for it are in
~/workspace/tools/two_vision_fixpass/.

Fix-pass verification runs (script commits c1b623b and
45315d5, 2026-11-22, verification window 11:36:49-11:42:41
+07 (04:36:49-04:42:41Z); same machine,
headless Firefox 160.0.1, repo venv python; all logs,
results.json, inventory.json and ledger.json preserved in
~/workspace/tools/batch12-t2-fixpass/. The run dirs still
contain their full profile/ dirs, so the profiles were
preserved, not deleted. The /tmp percentage and
no-Firefox claims from the first version of this
paragraph have no preserved df/ps artifact behind them
and are struck here, not repeated. Disclosure: the
fp-iframe-strict run below is the SECOND attempt. The
first attempt failed with harness_error "TypeError: log()
got multiple values for argument 'name'" (log ends
04:37:57Z, wall 5.5436 s); the colliding call was fixed in
the working tree between the attempts and folded into
commit c1b623b (04:43:37Z) with no mention in the
fix-pass report. The fix-pass runs therefore verified the
pre-commit working tree, not the commits; the committed
code was verified later by a fresh driver re-run on HEAD
(11/11 PASS) and by the fix pass 2 runs below.

- Happy path (fp-happy, --fixture): PASS, wall 10.3707 s,
  sends_this_run 2. Both steps: before_count 0,
  gate_baseline 0, gate_count 1, v11_mutations 1 with
  v11_scope "thread", input_cleared_after_enter true.
  Cross-window check clean (own 1, foreign 0 per thread).
- Stale bubble (fp-stale, fixed plan bench-fixpass-stale,
  stale fixture): PASS, wall 7.1252 s. Both steps:
  before_count 1, gate_baseline 1, gate_count 2.
- No-send (fp-nosend, fixed plan bench-fixpass-nosend,
  no-send fixture): FAIL as designed, wall 9.3197 s,
  exit 1. Clone1 v12-timeout with gate_count 1 (stale
  bubble only), v11_mutations 0, v11_scope "thread";
  clone2 not-executed.
- Strict input name (fp-strictbad, plan input_name "Zzz"):
  FAIL as designed, exit 1, wall 5.2949 s. Step 1
  input-name-mismatch, no ledger file written.
- Iframe harvest (fp-iframe, --mode harvest): HARVEST-ONLY,
  wall 5.4404 s. 4 items per window, 1 frame per window,
  accessible true, origin "null".
- Iframe harvest with --strict-input-name
  (fp-iframe-strict): HARVEST-ONLY (second attempt; the
  first attempt failed, see the disclosure above).
  harvest_inputs recorded for both windows (name,
  aria-label and placeholder "Message" each, ref
  #msg-input).
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

## 3. Decision packet for the coordinator (gap 8, prepared)

The coordinator must supply each of these before a live
run can be scheduled. Nothing here invents any of them.

1. Method approval: yes or no for a live run of the
   2-vision benchmark (runbook sections 6-8) or rung 2
   (runbook section 14), for a named run_id.
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
   the shared registry (default path
   /home/hatch/.cache/two_vision_bench/run_registry.json;
   there is no --registry-path flag, and no override flag
   for the registry path may be used live); a reused
   run_id in a fresh workdir is REFUSED, so the value must
   be fresh and the owner must be named.
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
11. Resume authorization: if this run is a resume of a
    failed attempt, the coordinator must name the failed
    run_id, the operator who hand-checked the threads, and
    the destination artifact for the resume report. A
    resume without this item is refused by the runbook
    (section 14.4): the ledger blocks re-sending a
    recorded intent, so a new run_id after a hand check is
    the only path, and it must be authorized, not assumed.

## 4. Rung 2 procedure (runbook section 14)

Live 0-vision on the real clone chats at ws2, option A
fallback. Written step by step in runbook section 14:
prerequisites (14.0), harvest-first with frames census
(14.1), the live run with --strict-input-name (14.2),
DOM-only pass criteria (14.3: textNew gate counts,
cross-window check, accuracy >= 90%, wall time end to
end including transport (operator-side command wall time;
wall_s is the script-internal portion), visions_used 0
via --visions-used 0 on the step-2 command), stop conditions
(14.4, including retry-blocked-reservation, ref-stale,
input-name-mismatch and cross-window contamination),
preserve and report (14.5), and what rung 2 still needs
(14.6).

What 0-vision means, exactly: the agent takes zero
observations during the step-2 run invocation. No VISION 2
look at the threads, and no inventory read by the agent
during the run. The step-1 harvest-first inventory read IS
a DOM harvest read, so it counts as 1 vision of pre-run
preparation outside the step-2 budget, under the runbook
section 8 definition; the 0 counts the run invocation only,
the same accounting the 2-vision run already uses. The
agent reads only the script's JSON results and the run
log during step 2. The step-1 name check is mechanized:
--strict-input-name now also checks the harvested names in
harvest mode, so no operator read of inventory.json is
needed for the check. Pass --visions-used 0 on the step-2
command so results.json records 0. A final
visual sanity check, if the user asks for one, is outside
the run and must be logged with its time.

Hard constraint, kept: rung 2 acceptance runs on the real
clone threads, NOT the Firefox fixture, under either live
shape.

Coordinator approval still owed on the 0-vision scoping:
the scoped definition (0 during the step-2 run
invocation, the step-1 harvest read as pre-run
preparation outside the budget) narrows the unscoped
"0-vision" acceptance label in the arch-review log, and
the runbook section 14 intro and the decision packet item
1 both carry that approval as an open item. Until the
coordinator approves the scoping, a rung 2 run cannot be
scored as a 0-vision pass against the arch-review label.

## 5. What remains (still NOT READY)

- OPEN (2): gap 7 a11y dry probe (UNRUN, operator, before
  the first live run), gap 8 method approval + thread
  URLs/selectors (coordinator; decision packet in
  section 3, now 11 items).
- PARTIAL (5): checklist 10 contradictions (doc done),
  10.3 definition (dry probe open), live-shape procedures
  (coordinator decision + verification of the picked
  option open), cross-origin frames (census built, live
  check owed at run time), input name (procedure
  mechanized, live value owed at run time).
- STANDING (2): live lane free, live measurement of the
  90% bar (measured by the run itself).
- CLOSED (3): AMEND4 item 12 runbook section 9, VISION 2
  monitor + run log named, script features (gap 9).

No live run can happen until the coordinator supplies the
decision packet and the operator closes gaps 6 and 7 at
run time. The runbook section 12 and the closeout carry
the same counts (3 / 5 / 2 / 2).

## 6. Commits

- f49851f: script features + new fixtures + driver
  (textNew, reservation, V11, D3, frames census, strict
  input name).
- e704d44: runbook rung 2 procedure, section 12 recount,
  script re-pin f49851f. (Merged with origin/main as
  00d9dee; the merge brought in only the coordinator's
  nudge to clone1, bdae91a, no instruction for clone2.)
- 8eeafbe: workflow doc batch 12 task 2 results, gap
  table, rung 2 pointers.
- c1b623b: fix-pass script changes (exactly-once holes
  F1/F2/F3/F5/F6/F7/F8/F9/F10/F11/F12, C1-2 thread-missing,
  registry, --visions-used, --allow-resume, disk guard,
  atomic results.json, mechanized harvest name check).
- 45315d5: fix-pass driver 11/11 plus double-append and
  CE no-send fixtures.
- dfea01b: fix pass 2 script changes (harvest never binds
  the registry; intent binding; sent-bubble-absent
  refusal; 1.0 s gate settle; outcome rule fails on
  thread-missing and own_count < 1; ledger state machine
  with atomic reserve; corrupt registry/ledger refused;
  --visions-used rejects negatives; validate_plan refuses
  substring messages; delayed-double fixture).
- 93e8f48: fix pass 2 driver fix (delayed-double test runs
  on the shared browser before the CLI tests, then the
  shared browser is quit; 19 tests).
- c58037e: merge origin/main (clone1 batch 11 task 2/3,
  watchdog logs; no conflicts).
- 00ce862: gate_settle_s recorded when the gate starts,
  not only on the pass path.
- b72ec65: fix pass 2 docs (runbook 1928 lines, workflow
  1121 lines, design doc 792 lines, all re-pinned at
  00ce862).
- (this report and the closeout dated note: committed
  together after this section.)

All commits small and pushed one at a time. 0 em/en
dashes, no personal information.

## 7. Fix-pass appendix: council + redteam verdicts and fixes

Council of 3 plus independent redteam ran on the batch 12
task 2 build (report 981a0b1, script f49851f). All four
verdicts arrived before the fix pass; every correction
below was applied and verified against primary sources
(code, fixture runs, preserved logs).

- Council 1: ISSUES, 1 critical, 1 major, 1 minor, plus
  2 notes. Critical: main() overwrote a "sending"
  reservation (and a "sent" record) with "failed", so a
  retry after one intervening run re-sent. Fixed: the
  failure mark now protects "failed-unverified", "sent"
  and "sending" (script lines 1552-1555); proven by the
  fix-pass driver F1 (ledger stays "sent" after a
  target-gone retry, next run skips). Major: COUNT_JS -1
  (thread missing) was collapsed to 0, so a recorded
  "sent" intent re-sent through a broken thread selector.
  Fixed: -1 is preserved and fails fast as thread-missing
  in the pre-check, the before-snapshot and the gate
  baseline (fix-pass driver C1-2). Minor: D3 did not
  compare tag. Fixed: tag, aria-label and placeholder are
  compared separately (fix-pass driver F6, F8). Notes:
  before_count is recorded evidence only, never consulted
  by the gate (docstring, comments and docs corrected);
  an exception between the reservation mark and the gate
  left "sending" forever (fixed: try/except reconciles to
  failed-unverified, and never overwrites a "sent" mark).
- Council 2: ISSUES, minor only. 5 findings, all doc
  pins and wording: workflow doc 747 lines corrected to
  914 (3 places in the runbook); the fix-pass edits then
  grew the workflow doc to 1004 lines, and the runbook
  citations were updated to 1004; validate_plan cited at
  ~line 600, correct 868 (now 1111 after the fix pass);
  runbook section 0 lead blockers still showed the old
  batch 11 count (updated to 3/4/3/2 in the fix pass;
  corrected to 3/5/2/2 only in fix pass 2, runbook commit
  b72ec65; the earlier claim that it was updated to
  3/5/2/2 in fix pass 1 was wrong, corrected by council 2
  in round 2); report section 2 block ordering corrected
  (failed-unverified, then reservation, then sent-skip);
  describe() wording corrected (records ref, role, name,
  path, actions, plus editable/extents/state flags, and
  never text content). One unverifiable detail noted, not
  a finding: the workflow section 7 run window end
  04:01:14Z has no preserved artifact behind it;
  corrected to 04:01:05Z (latest preserved results.json
  mtime).
- Redteam (council 3): BROKEN, 13 findings F1-F13, all
  reproduced live on the fixture. F1 (HIGH): a failed
  retry erased a "sent" record, then the script re-sent
  despite a visible identical bubble. Fixed by the
  failure-mark guard (fix-pass driver F1). F2 (HIGH): a
  run with zero new sends scored PASS. Fixed: outcome
  requires 2 sends this run unless --allow-resume
  (fix-pass driver F2). F3 (HIGH): same run_id with a
  fresh workdir re-sent. Fixed: shared run registry
  refuses it before the browser starts (fix-pass driver
  F3). F4 (MEDIUM): the gate is appearance-based, not
  causal. Fixed in docs (design doc 4.2 note, runbook
  14.3, report section 1) plus input_cleared_after_enter
  and thread-scoped V11 as recorded evidence (not causal
  proof: the gate proves a bubble appeared after the
  baseline, not that our Enter caused it; the wording
  "recorded causal ties" used in the first version of
  this paragraph was wrong and is corrected here). F5
  (MEDIUM): the gate was `>` not `== baseline+1`, so a
  double append passed silently. Fixed: exact +1, else
  duplicate-bubble (fix-pass driver F5). F6 (MEDIUM):
  D3 never compared tag. Fixed (F6). F7 (MEDIUM): the HCU
  guard compared the live rect against the fresh center
  from ensure_visible, not the harvest. Fixed: harvested
  center unless scrolled (F7). F8 (MEDIUM): D3 was blind
  to placeholder-only renames. Fixed: placeholder and
  aria-label compared separately (F8). F9 (MEDIUM):
  v11_mutation_flag is not evidence a send landed
  (counts any page mutation; contenteditable typing alone
  moves it; callback-batch count, not a mutation count).
  Fixed: observer is thread-scoped and counts records;
  the flag left the pass criteria (runbook 14.3) and is
  recorded evidence only (F9). F10 (MEDIUM):
  cross-window check was blind to a prefixed foreign
  bubble. Fixed: containment matching on raw texts, with
  the matching texts recorded (F10). F11 (MEDIUM):
  identical messages made a correct run FAIL the
  cross-window check. Fixed: validate_plan requires
  distinct messages (F11). F12 (LOW): the ledger had no
  locking. Fixed: flock + re-read inside the lock +
  atomic write. F13 (MEDIUM): the rung 2 "0-vision" label
  contradicted the runbook's own vision definition.
  Fixed: scoped wording (0 during the step-2 run
  invocation, step-1 harvest read is pre-run preparation
  outside the budget) plus the mechanized harvest name
  check and --visions-used 0, so 0 is recorded, not
  asserted. Minor note: a full /tmp made finish() leave a
  0-byte results.json. Fixed: disk-space guard plus
  atomic results.json write.
- Redteam 4/4: ISSUES, 9 corrections, all applied.
  (1) 0-vision claim vs section 8 definition: scoped
  wording in runbook 14 intro, 14.1, 14.3, report
  section 4, and the script help text. (2) Built textNew
  baseline is pre-Enter, not batch start as design doc
  4.2 specifies: dated note in design doc 4.2, main()
  comment and COUNT_JS comment fixed. (3) Step 1 cannot
  record "the harvested aria-label and placeholder":
  HARVEST_JS now emits them as separate fields, so
  inventory.json carries them; runbook 14.1 wording
  stands, verified by the iframe-strict run. (4) Section
  14.1 fail rule as written failed the fixture's own
  inventory (visible "Search" textbox): FAIL iff no
  visible textbox named "Message" exists, or the picked
  input's name does not contain "Message"; fixed in 14.1
  and section 6. (5) Wall time "including transport" is
  not what wall_s measures: operator-side command wall
  time is now the end-to-end figure; wall_s is the
  script-internal portion. (6) Decision packet omits four
  items: run_id owner/value, option A binary path and
  re-pin, per-browser debug ports, live-lane-free
  confirmation; all four added as packet items 7-10.
  (7) Section 14.2 command unqualified for option B:
  labeled as the option-A invocation, CDP substitution
  noted. (8) Stale pre-check descriptions and the wrong
  gate baseline in runbook section 5 and workflow
  sections 5, 10.1, 10.3: all fixed to the ledger-"sent"
  AND bubble-visible skip and the pre-Enter gate_baseline.
  (9) Design doc section 7 stale on reservation, D3, V11:
  dated note marking all three BUILT in f49851f,
  hardened in c1b623b, fixture-proven, live proof owed.

## 8. Fix pass 2 appendix: round-2 council + redteam verdicts and fixes

A second council of 3 plus an independent redteam ran on the
fix-pass build (report 6ab0c04, script c1b623b, driver
45315d5). All four verdicts arrived before fix pass 2; every
correction below was applied and verified against primary
sources (code, fixture runs, preserved logs). The four
verdicts:

- Council 1: ISSUES, 10 findings (script correctness,
  exactly-once, doc pins).
- Council 2: ISSUES, 16 findings (doc pins, line numbers,
  counts, cross-doc consistency).
- Council 3 (redteam): BROKEN, 15 findings, 4 HIGH.
- Redteam 4/4: ISSUES, 11 findings (re-derived appendix
  claims, blind-selector re-send, undisclosed
  mid-verification fix, 0-vision scoping needs coordinator
  approval, decision packet missing resume authorization).

Honesty note: the round-2 verdicts were delivered as
subagent reports in the session and are not preserved as
files in the repo, so this appendix records the verdicts
and the findings that drove the fix-pass-2 changes, each
with its fix and its verification, and does not pretend
to reproduce the full per-finding texts. The fixes are
traceable commit by commit below; the verification for
all of them is the fix pass 2 run set in section 2
(driver 19/19 PASS, baselines with timings).

Redteam HIGH findings, each fixed:

- H1: rung 2 as written cannot execute. Step 1 harvest
  bound the run_id to the harvest workdir in the shared
  registry, so step 2 in a fresh run dir was REFUSED.
  Fix: the harvest never binds the registry (script
  commit dfea01b); only run mode binds it. The rung 2
  harvest-then-run shape with the same run_id in
  different workdirs now works, proven by the fix-pass
  driver test (harvest-then-run succeeds) and by the
  runbook section 14 rewrite (commit b72ec65).
- H2: a recorded "sent" intent re-sent when the bubble
  count read 0 (fresh page load, unloaded thread).
  Fix: a recorded "sent" intent whose bubble is absent
  refuses with retry-blocked-sent-bubble-absent instead
  of re-sending (dfea01b). Proven by the fix-pass driver
  test (sent intent, no bubble, refusal, 0 sends) and
  recorded in workflow section 8 (F5 row) and runbook
  section 14.4.
- H3: an intent did not bind message text, thread URL,
  or selectors, so the same intent re-sent a different
  message under an edited plan. Fix: every ledger mark
  records message, thread URL and selectors, and a
  changed plan under the same run_id refuses with
  retry-blocked-intent-changed, the ledger keeping the
  original message (dfea01b). Proven by the fix-pass
  driver test (changed message refused, original kept).
- H4: the V12 gate broke on the first poll at baseline+1
  and never settled, so a delayed second append scored
  "sent" with two identical bubbles. Fix: the gate
  settles a full second after first sighting baseline+1
  (dfea01b, gate_settle_s recorded when the gate starts,
  commit 00ce862), and a delayed double append fails as
  duplicate-bubble. Proven by the new delayed-double
  fixture (second bubble after 700 ms) in the fix-pass
  driver test, and by the baselines (gate_settle_s 1.0
  on the happy path).

Redteam 4/4 findings, each fixed:

- Re-derived appendix claims: the fix-pass report's
  appendix repeated claims the evidence did not support
  (section 0 count, run window end, "causal ties").
  Fix: section 7 corrected (section 0 reached 3/5/2/2
  only in fix pass 2, not in fix pass 1), section 2
  window start corrected to 04:36:49Z, F4 wording
  corrected to recorded evidence, not causal proof.
- Blind-selector re-send: same shape as H2, reached
  through a broken thread selector. Fix: the
  thread-missing check runs first in the pre-check
  (script lines 744-826 at 00ce862), before the
  failed-unverified block; a "sent" intent with a broken
  selector fails as thread-missing, never re-sends.
- Undisclosed mid-verification fix: the fp-iframe-strict
  first attempt failed and was fixed in the working tree
  without mention. Fix: disclosed in workflow section 7
  and in report section 2 above (first attempt failed
  04:37:57Z, fix folded into c1b623b at 04:43:37Z; the
  fix-pass runs verified the pre-commit tree, the
  committed code was verified later).
- 0-vision scoping needs coordinator approval: the
  scoped definition narrows the unscoped arch-review
  acceptance label. Fix: the approval is now an open
  item in runbook section 14 intro, workflow section
  10.4, and report section 4 above; a rung 2 run cannot
  be scored as a 0-vision pass until the coordinator
  approves it.
- Decision packet missing resume authorization: a resume
  of a failed attempt had no authorized path. Fix:
  packet item 11 added (section 3 above): failed run_id,
  operator name, artifact destination; a resume without
  it is refused by the runbook.

Remaining findings, grouped (council 1 script
correctness and exactly-once; council 2 doc pins, line
numbers, counts and cross-doc consistency; redteam
non-HIGH findings):

- Ledger state machine: "sent" is terminal, reserve()
  is atomic under one lock, status() re-reads from disk,
  corrupt ledger and registry files are refused with
  exit 2, inventory.json writes are atomic, finish()
  never raises, pre-reservation exceptions are recorded
  as failed steps (dfea01b). Proven by the fix-pass
  driver corruption tests and the 19/19 run.
- Outcome rule: a run now fails when a thread is missing
  after the gates or holds no bubble with its own
  message, and outcome_note names the real failure
  instead of claiming both steps skipped (dfea01b).
  Proven by the fp2-nosend baseline (outcome_note "no
  sends this run: clone1:v12-timeout").
- results.json records registry_enabled and
  registry_path (dfea01b); --visions-used rejects
  negatives; validate_plan refuses substring messages
  (dfea01b). Proven by the driver tests and the happy
  baseline (registry_enabled true, default path).
- Doc pins re-based at 00ce862 (1939 lines) across the
  runbook (1928 lines), workflow (1121 lines) and
  design doc (792 lines): script line numbers, section
  0 count 3/5/2/2, section 13.1 dry-send run_id,
  section 14 decision packet (11 items), section 15
  re-pin, workflow section 7 window and housekeeping,
  section 8 F5 row, sections 10.1/10.3/10.4, design doc
  sections 1/4.1/4.2/4.3.3/4.3.4/5/7/8 (commit b72ec65).
  Verified by grep against the script at 00ce862 and by
  the line counts in the header of this report.

Fix pass 2 verification: section 2 above (happy, stale,
no-send, strict-bad, iframe, iframe-strict, once, b12t2
drivers, fix-pass driver 19/19 PASS, wall 157.1595 s).
No round-3 council was run for the fix-pass-2 changes:
fix pass 2 was the last work before the weekly usage cap
(12:14 22/11, capped until 02:38 Wed 25/11), and per the
coordinator's decision (commit 01089dd) no new work was
spawned. A round-3 council for the fix-pass-2 changes
remains open for the coordinator to dispatch.
