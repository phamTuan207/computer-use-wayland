# RUN REPORT: agy-y2 suite LIVE on Zen (Y9b, independent runner)

- Date: 2026-11-21, launched 20:28:42 +07, finished about 20:30:04 +07
- Runner: Worker Y9b (Muse), independent of the suite generator (Y2)
  and the fix verifier (Y7)
- Verdict: **10/10 PASS, 0 flagged, 0 failed**

## Result

| Test | Outcome | Elapsed | JSONL rows | Checks | Clicks | Types |
|------|---------|---------|------------|--------|--------|-------|
| 01 tmux session | PASS | 7765 ms | 43 | 21 | 13 | 3 |
| 02 network settings | PASS | 7945 ms | 45 | 23 | 16 | 1 |
| 03 photo editor | PASS | 7935 ms | 39 | 20 | 14 | 0 |
| 04 email compose | PASS | 7782 ms | 41 | 16 | 14 | 4 |
| 05 spreadsheet chart | PASS | 7658 ms | 40 | 10 | 10 | 14 |
| 06 video call | PASS | 7820 ms | 48 | 26 | 15 | 3 |
| 07 file manager | PASS | 8065 ms | 41 | 13 | 20 | 2 |
| 08 devtools | PASS | 7706 ms | 42 | 23 | 13 | 3 |
| 09 notes sync | PASS | 7810 ms | 44 | 19 | 14 | 5 |
| 10 IDE debug | PASS | 7603 ms | 38 | 21 | 11 | 1 |
| **Total** | **10/10** | **78089 ms** | **421** | **192** | **140** | **36** |

- Suite JSON: passed 10, flagged 0, total_passed 10, failed 0,
  fixture_unavailable 0, total 10. total_ms 78089, suite_wall_ms
  81987. Marionette calls 1424 (all Y9WD sessions before the suite
  JSON). Tokens UNMEASURED (Python runner, no LLM calls).
  Observation cost UNMEASURED. VCR false. Stall 37.4 ms (ladder
  time only; no hidden body encountered).
- Exit code: 0 by the plan rule (clean + flagged == total). The
  detached launch did not capture the process exit code directly;
  the suite JSON (passed 10, failed 0), the 10 "final verify PASS"
  lines, zero FAIL lines, and zero tracebacks in the 597-line
  stdout log are the evidence. No re-runs: every test attempt 1,
  superseded_attempts [].

## Command and ship (frozen, runnable evidence)

- Launch (laptop, detached, under flock):
  `cd /tmp/worker-y9-server && LIVE_SERVER_ROOT=/tmp/worker-y9-server LIVE_SERVER_PORT=8769 LIVE_LOG=/tmp/worker-y9-live.jsonl WD_PORT=4449 LIVE_OWNER_AWAY=1 flock -w 60 ~/.cache/agent-computer-use/zen_dom.lock -c "python3 run_agy_y2.py all > /tmp/worker-y9-stdout.log 2>&1"`
- Ship commit 4e7a414 on todolist-push. Manifest md5
  7f744edddf14ff39e912691812fdb6bc (26 files, 0 mismatches,
  --verify-manifest exit 0, verified on the VM and the laptop
  before launch). Runner md5 2add2a0bf68bb77d5d3fa01d691bcffc,
  run_live.py md5 84fa106c253d5e7f16daccf2ce3f14a5 (from 1e3901c,
  the Y4d live-proven base), suite from 30a72e5.
- Slot release (Y9 plan section 5, amended marker): commit feb3fb7
  "Y8 E1: B single-arm observation execution complete, v2.1
  comparison closed" plus the "E1 EXECUTION COMPLETE" log line
  naming both arms' FINAL states, "no comparative verdict", and
  "live slot released to Y9"; Y4d direct marker 1e3901c. Launch-time
  live checks passed (no geckodriver, no runner processes, Y8 ports
  4451/8767 free, my ports 8769/4449 free, Zen PID 27958 alive).
- Handover token /tmp/worker-y9-handover.json written at launch
  (asserted_at_unix 1795267723, basis: owner handed the machine
  over 18:24 21/11, out of the house).

## Hidden body

- **0 hidden-body encounters, tz-hidden never sighted.** Bootstrap
  intervention: none (intervened false, tz_hidden_removed false,
  hidden_body_encounters 0). All 10 fixtures opened VISIBLE on the
  first attempt. The "body renders visible (no hidden-body
  incident)" check passed on all 10 tests.
- Consequence: the decisive hidden-body experiment (Y4b design:
  htmlClass + rAF ticks on the SAME hidden tab at the SAME minute)
  is STILL owed. Like Y4d's rerun (10/10, 0 encounters), this run
  proves the suite passes on a healthy browser, not that the
  recovery ladder works. The tracked item
  (improvements/transparent-zen-defect-tracked-item.md) stays OPEN.

## Y7's surviving doubts, live evidence

1. test-07 cannot prove delete/restore happened (skip hole):
   CLOSED on this run by the intermediate checks, which are
   PASS-gating r.check() calls. Step 24 checks passed: "row img4
   hidden after delete: hidden", "trash counter 1: 1", "trash row
   img4 present in trash table". Step 28 check passed: "trash
   counter 0 after restore: 0". A skip of steps 23-29 would fail
   these checks (counter would read 0 at step 24, not 1). They
   passed, so delete and restore ran. The final verify alone still
   cannot detect a skip; the closure rests on the intermediate
   checks, as the plan states.
2. test-09 delete assertion bypassable off-spec via the save-handler
   rename branch: spec steps run exactly. Step 33 body check
   passed with the pinned value "Milk, Eggs, Bread, Apples"
   ("primary body has Apples: Milk, Eggs, Bread, Apples"). The
   step 7 save used the rename branch as required; no save happens
   after the archived note is selected (steps 29-34 are click,
   delete, view, finalize), so the bypass cannot trigger on the
   spec path. The step 10 pre-append assert also passed ("body is
   Milk Eggs Bread before append: Milk, Eggs, Bread").
3. test-07 Root count depends on the move set being exactly img1-3:
   move set was correct. Inventory toast: "Root: 5 files, Archive:
   3 files, Trash: 0 files, Folder Processed created". Root 5, not
   6. No wrong-move-set signal.
4. simulate --all aborts on first crash: not applicable live. No
   crash occurred; all 10 tests ran in one process, each wrapped,
   and the runner continued through the suite.

## Integrity guard

- Held on all 10 tests (expected failures on the untouched fixture
  before steps): 01: 8, 02: 10, 03: 9, 04: 4, 05: 12, 06: 7,
  07: 6, 08: 7, 09: 6, 10: 8. No guard-defect test, no
  fixture-unavailable outcome.

## Gaps and plan defects

- Known fixture gap (carried in the suite JSON gaps list):
  test-10 step 15 click #input-edit-watch-total SKIPPED, reason
  "fixture gap: input display:none, no handler, simulator also
  skips it". A test-10 PASS never implies step 15 was performed.
  Pre-registered in the plan, not a surprise.
- PLAN DEFECTs: none found. No step failure, no check failure, no
  infra event, no re-run, no abort-rule trigger.
- Minor observation, not a defect: the plan (section 3) also asks
  for a suite-end screenshot at /tmp/worker-y9-shots/suite-end.png;
  it was NOT produced (only the 10 per-test shots exist). The
  evidence leg is the per-test shots, all present. The suite-end
  cleanup printed "tab cleanup failed ... (harmless)" 404s for
  already-closed registered test tabs; no user tab was involved
  (all handles were registered test tabs) and the tabs were
  returned to about:blank. The one HTTP 404 in the server log is
  favicon.ico.

## Teardown

- Runner PID 339447 and geckodriver PID 339599 both gone by
  20:30:16. Zen PID 27958 alive. Ports 8769, 4449, 4451, 8767 all
  free. Test tabs returned to about:blank. Lock released (no flock
  holder). No stray processes.

## What this run does NOT prove

- Hidden-body recovery (0 encounters; see above).
- Anything about the E1 comparison or the Y11 metrics proof; this
  run is the agy-y2 suite only.
- That a future run on a hidden-body tab would recover; the ladder
  paths never fired for a real hidden body.

## Evidence files (repo, todolist-push)

- tests/realistic/live-run-y9-agy-y2-20261121.stdout.log (597 lines,
  md5 a2bb091ad251adc8f1b46579a5853729, matches laptop original)
- tests/realistic/live-run-y9-agy-y2-20261121.jsonl (421 rows, md5
  c4cb677bf0703eb2e1c77db266576143, matches laptop original)
- tests/realistic/live-run-y9-agy-y2-shots/ (10 PNGs, md5s verified
  against laptop originals)
- improvements/worker-y9b-agy-y2-live-log.md (this run's log)
- Ship: commit 4e7a414; runner run_agy_y2.py 3013 lines.
