# Batch 12 task 2: close the 5 open readiness gaps, prepare rung 2

Date: 2026-11-22, 10:51-11:20 +07. Verdict: still NOT READY.
New count: 3 fully closed, 4 partial, 3 open, 2 standing
(was 2 / 3 / 5 / 2 after batch 11 task 2). Numbering matches
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
  1277 lines. After this task: 1650 lines.
- Workflow doc before: docs/two-vision-benchmark-workflow-20261122.md,
  798 lines. After this task: 914 lines.
- Script before: tests/two_vision_bench.py, 868 lines, commit
  c267411. After this task: 1200 lines, commit f49851f.
- Design doc: docs/clone2-one-vision-design-20261122.md,
  section 4.2 (textNew is the V12 gate with a before
  snapshot), section 4.3.2 (pre-send reservation), section 7.
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

All four features are built in the script (commit f49851f)
and fixture-verified (see section 2). textNew in the V12
gate (COUNT_JS, before-snapshot count per window in main(),
gate passes only on a NEW bubble past the pre-Enter
baseline); pre-send reservation (intent written as
"sending" after the V1 readback and before Enter,
reconciled to "sent" or "failed-unverified" after the
gate; a later run finding status "sending" refuses with
retry-blocked-reservation); V11 MutationObserver flag
(OBSERVER_JS armed before typing, mutation delta recorded
per send); D3 ref stability (REF_CHECK_JS re-resolves the
ref before input and fails fast with ref-stale when tag,
role or name changed, nearest live textboxes listed);
cross-window check (after both sends each thread must
hold only its own message).

What remains is live proof: the fixture proof is not a
live proof. VISION 2 stays for the 2-vision run until a
live run passes with textNew; rung 2 drops it by
definition (section 4).

Honest limits of the build, recorded here so nobody
over-reads it:
- The reservation closes the process-death gap only when
  the same ledger is reused (same workdir or --ledger). A
  fresh workdir has an empty ledger, so the run_id
  freshness check still stands.
- The pre-check skip changed: it now skips only when the
  ledger says the intent was already sent AND the bubble
  is visible. A stale bubble with no ledger record does
  NOT skip; the send proceeds and the textNew gate
  requires a new bubble. With a fresh workdir a reused
  run_id now sends a second identical bubble instead of
  skipping (honest: the gate proves a new bubble landed,
  but still a duplicate the procedure forbids). With a
  shared workdir the ledger's "sent" record still skips.
- The D3 check compares tag, role and name at the ref. An
  element replaced by an identical twin (same tag, role,
  name, different identity) still passes it; the HCU
  guard and the V1 readback are the backstops.
- The V11 observer counts mutations on document.body. A
  send that types but never appends a bubble shows 0
  mutations (proven by the no-send fixture run); the flag
  is evidence, not a gate.

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

### Gap 6 (input name): OPEN

The aria-label is still UNKNOWN. No DOM or a11y read of
the live Messenger input exists anywhere in the repo, and
none was invented here. What changed: rung 2 runs with
--strict-input-name, so a wrongly named input fails closed
with input-name-mismatch before any send instead of being
typed into silently (proven: plan input_name "Zzz" fails
closed, no ledger file written, nothing typed). But the
flag checks the name against the plan's input_name, and
the plan's input_name is still "Message" from visual-only
evidence (two screenshot reads in the CL1-MSG logs), so
the name itself is only closed by the live harvest-first
DOM read at run time (runbook section 14 step 1 records
the harvested aria-label and placeholder per window in
the run log). Owner: operator, on the laptop, before the
run.

### Gap 7 (a11y dry probe): OPEN

Still UNRUN. The probe commands were re-verified against
the code at todolist-push tip da46c4c (scripts/a11y.py
observe() keeps only elements with actions, editable, or
in skeleton mode; describe() records name/role/actions
only, never text content; query() calls observe() without
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
~/workspace/tools/batch12-t2/ (logs/ and runs/),
profiles deleted after each run, /tmp ended at 5 percent,
no Firefox left running.

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
unverified) is unchanged in code: the failed-unverified
block still runs before the sent-skip, and the reservation
block runs after it. It was not re-run here; the fix-pass
logs for it are in ~/workspace/tools/two_vision_fixpass/.

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

Note for the coordinator: batch 12 task 3 (sibling task,
endpoint naming rule + guard test for the port-split) is
the authority on debug-port endpoints for option B; the
rung 2 procedure requires a distinct debug port per
browser, passed explicitly, never the default.

## 4. Rung 2 procedure (runbook section 14)

Live 0-vision on the real clone chats at ws2, option A
fallback. Written step by step in runbook section 14:
prerequisites (14.0), harvest-first with frames census
(14.1), the live run with --strict-input-name (14.2),
DOM-only pass criteria (14.3: textNew gate counts,
cross-window check, accuracy >= 90%, wall time end to
end, visions_used 0 operator-recorded), stop conditions
(14.4, including retry-blocked-reservation, ref-stale,
input-name-mismatch and cross-window contamination),
preserve and report (14.5), and what rung 2 still needs
(14.6).

What 0-vision means, exactly: the agent takes zero
observations during the run. No VISION 1 inventory read
by the agent and no VISION 2 look at the threads. The
agent reads only the script's JSON results and the run
log. The script's hardcoded visions_used: 2 in
results.json does NOT apply to rung 2; rung 2 records
visions_used 0 in the run log, by the operator. A final
visual sanity check, if the user asks for one, is outside
the run and must be logged with its time.

Hard constraint, kept: rung 2 acceptance runs on the real
clone threads, NOT the Firefox fixture, under either live
shape.

## 5. What remains (still NOT READY)

- OPEN (3): gap 6 input name (live DOM read at run time),
  gap 7 a11y dry probe (UNRUN, operator, before the first
  live run), gap 8 method approval + thread URLs/selectors
  (coordinator; decision packet in section 3).
- PARTIAL (4): checklist 10 contradictions (doc done),
  10.3 definition (dry probe open), live-shape procedures
  (coordinator decision + verification of the picked
  option open), cross-origin frames (census built, live
  check owed at run time).
- STANDING (2): live lane free, live measurement of the
  90% bar (measured by the run itself).
- CLOSED (3): AMEND4 item 12 runbook section 9, VISION 2
  monitor + run log named, script features (gap 9).

No live run can happen until the coordinator supplies the
decision packet and the operator closes gaps 6 and 7 at
run time. The runbook section 12 and the closeout carry
the same counts (3 / 4 / 3 / 2).

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
- This report and the closeout dated note: committed together.

All commits small and pushed one at a time. 0 em/en
dashes, no personal information.
