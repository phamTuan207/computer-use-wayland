# Worker Y11: live metrics wiring log (H2/I8)

Worker Y11, Muse instrumentation engineer. Task: close the Y3 gap audit
finding (improvements/worker-y3-fcc-verification.md, commit 4153371):
H2 think time and I8 hit rate had NO live measurement. Think-time
instrumentation (scripts/timing.py) was never wired into a live run;
hit-rate measurement (scripts/hit_rate.py) was calibration-only.

All times Asia/Ho_Chi_Minh, 21/11/2026.

## Design (frozen before implementation)

- Design doc: improvements/worker-y11-design.md (20,077 bytes).
- Council + redteam verdicts (4 agents, spawned 18:52):
  - improvements/worker-y11-council-1-think-time.md (18:55): AMEND.
    think_s = null with think_source="scripted", never 0; H2 stays
    OPEN until a real agent-driven run produces agent-source think rows.
  - improvements/worker-y11-council-2-hit-rate.md (18:54): AMEND.
    Rename/re-scope to pointer-occlusion and intercept rate; vision
    grounding NOT measured by this oracle. Pre-click elementFromPoint
    probe. Descendant = hit only if inert; ancestor = miss.
  - improvements/worker-y11-redteam.md (18:55, 26,211 bytes): BLOCK
    with 8 holes B1-B8, each with trigger scenario and cheapest fix.
    Unblock condition: all 8 cheapest fixes landed in the design doc
    before implementation. Done.
  - improvements/worker-y11-council-3-integration-schema.md (18:56):
    AMEND. Single writer, exact schema, run_id format, live-proof
    acceptance (A12).
- Honesty rules baked in: scripted think_s null; the click record is a
  SELECTOR-DELIVERY rate, not a vision grounding hit rate; fail-open
  metrics (never fails a test); one writer via jsonlutil.append_jsonl;
  TimingLogger and hit_rate.append_attempt/summarize never called on
  the live path.

## Implementation

- scripts/live_metrics.py (new, 25,842 bytes): LiveMetrics sole
  writer, PROBE_JS pre-click probe, slugify + per-run collision
  registry (6-hex sha1 suffix), classify_probe, record_click (probe
  authoritative, exception path logs a miss), record_type (post-type
  read-back), begin_step/note_action/note_wait/note_exec/finish_step,
  summary (statistics.median; actions_per_call null when model_calls
  is 0; UNRELIABLE flag at js+eval share >10% or any DOM-to-JS retry).
  Fixes applied after first write: _CURRENT sentinel for envelope,
  record_click stores test in memory, live_log attribute.
- tests/realistic/run_live.py (edited): live_metrics import bootstrap;
  _CURRENT_METRICS global; _metered decorator with _meter_depth guard
  (outermost driver call only); _action_detail (identifiers/lengths
  only, never text/paths); diagnose_body renamed to
  _diagnose_body_impl with a wait-metered wrapper (Y4d diagnose code,
  _DIAG_JS, goto/refresh choke points untouched); WD.click rewritten
  (probe after scroll+find, before click; click_attempt row after
  outcome incl. exception path); type_text post-type read-back;
  goto/refresh/switch/new_tab explicit note_action in finally +
  explicit _note_wait around settle sleeps; Runner.step restructured
  (begin_step, _CURRENT_METRICS set/clear, finish_step in finally,
  think_s=None think_source="scripted"); run_one gains metrics=None;
  main creates one LiveMetrics (LIVE_METRICS env or
  default_metrics_path(LOG_PATH), LIVE_RUN_ID env or generated),
  writes exactly one summary in finally; stdout RESULT/SUMMARY lines
  unchanged. run_live.py is copied frozen into /tmp/worker-*-server/
  dirs on the laptop, so live_metrics.py must be shipped alongside
  it for the proof run.
- tests/realistic/hand_drive.py (edited): docstring + imports,
  _cmd_detail, main() rewritten with --metrics-path/--test/--run-id/
  --operator flags; per-command metrics (t_arrive_epoch, gap vs
  prev_print_epoch, think_s only from self-reported decided_at epoch,
  model_calls via note_model_calls, begin_step before execution,
  _finish closure emitting one action row + finish_step with
  think_source="hand" and extra inter_command_gap_s/cmd_len/operator);
  find stores find_css[el]=css; click branch runs pre-click probe via
  stored css and record_click incl. exception path; click_js/eval
  captured via _cmd_detail; summary in outer finally on quit/EOF/
  error. NOTE: the first full main() rewrite edit failed at ~19:00
  (old_text mismatch); redone as smaller targeted edits, all applied.
- Scope: run_live.py + hand_drive.py only this task. Sibling runners
  (run_agyq2, run_agy_y2, run_agyq, run_fcck) deferred as follow-up;
  Y8/Y9 are mid-flight on those files.

## Unit verification (headless, 21/11 19:09)

Commands:

```
python3 -m py_compile scripts/live_metrics.py tests/realistic/run_live.py tests/realistic/hand_drive.py
python3 -c "import sys; sys.path.insert(0,'scripts'); sys.path.insert(0,'tests/realistic'); import live_metrics, run_live, hand_drive; print('import-ok')"
python3 tests/realistic/hand_drive.py --help
python3 -m unittest tests.test_live_metrics -v
python3 -m unittest tests.test_timing tests.test_hit_rate
```

Outputs:

```
COMPILE-OK
import-ok
usage: hand_drive.py [-h] [--metrics-path METRICS_PATH] [--test TEST]
                     [--run-id RUN_ID] [--operator {human,agent}]
Ran 22 tests in 0.013s
OK
Ran 7 tests in 0.003s
OK
```

- tests/test_live_metrics.py (new, 22 tests): single-writer parse
  clean + exactly one summary row; slugify examples (incl.
  "#btn-save-board" accepted via slugify while hit_rate.append_attempt
  rejects it); scripted think_s None + medians null + actions_per_call
  null; metrics=None Runner log_step rows identical to a no-metrics
  run (ts stripped); unwritable path degrades without raising;
  torn-tail quarantine; two LiveMetrics different run_ids; summary hit
  math + js/eval exclusion; UNRELIABLE flag (>10% and DOM-to-JS
  retry); hit classification cases (exact, inert-descendant contains,
  clickable-descendant miss, ancestor miss, occlusion miss,
  pointer-events-none miss, null miss, exception-path logging);
  wait/exec buckets sum within act_s; envelope fields on every row;
  schema 1.
- Three failures found and fixed during the run (tests doing their
  job, not test bugs alone): (1) js/eval share at exactly 10% did not
  flag unreliable (threshold is strictly >10%; test used 9 dom + 1 js
  = exactly 10%, changed to 8 dom + 1 js = 11.1%); (2) same for eval;
  (3) REAL BUG in LiveMetrics.__init__: parent-is-a-file was not
  detected because the mkdir guard skipped when parent.exists() was
  true; fixed with an explicit is_dir() check raising
  NotADirectoryError, which the constructor catches and degrades to
  disabled.
- Existing tests still pass: tests.test_timing + tests.test_hit_rate
  7/7.
- run_live.py diff sanity: _DIAG_JS, choke points, switch-handle
  check, RESULT/SUMMARY prints, all run_tXX/run_fXX functions intact;
  AST parse OK.

## Live proof run (PENDING, queued behind Y9)

- Live slot queue (exclusive, one runner at a time): Y4d DONE 18:53
  (commit 1e3901c) -> Y8 E1 A/B (running, pre-flight wait until
  19:05:40, head beebe50 at 19:10 check) -> Y9 agy-y2 live (prep
  done, no live driving yet) -> Y11 proof run -> Y6b.
- At 19:10, origin/todolist-push head was beebe50 (Y8 E1 log v2.1).
  Y9 has NOT reported completion. No Zen driving done by Y11 yet.
- Proof plan (per C3 A12): after Y9 reports completion, ship
  live_metrics.py alongside run_live.py into the proof server dir on
  the laptop, run t01 + f01 with metrics on. Acceptance:
  verify_jsonl == [], exactly one summary row, step rows match
  log_step one-to-one by test+step, click_attempt count equals
  WD.click call count, js clicks only in js_clicks, RESULT/SUMMARY
  stdout identical to a metrics-off run of the same tests,
  wait_s + exec_s <= act_s per step.
- Honest note for the report: the proof run is scripted, so its
  summary carries think_s null and H2 stays OPEN; the proof closes
  the wiring gap, not H2.

## Commit

- Branch: todolist-push.
- Files committed (Y11 only; run_agy_y2.py uncommitted changes in the
  shared checkout belong to Y9 and were NOT touched or committed):
  scripts/live_metrics.py, tests/realistic/run_live.py,
  tests/realistic/hand_drive.py, tests/test_live_metrics.py,
  improvements/worker-y11-council-1-think-time.md,
  improvements/worker-y11-council-2-hit-rate.md,
  improvements/worker-y11-council-3-integration-schema.md,
  improvements/worker-y11-design.md, improvements/worker-y11-redteam.md,
  improvements/worker-y11-live-metrics-log.md.
- Commit hash: (filled below after push; verify with ls-remote).

## Follow-ups (not this task)

- Wire sibling runners (run_agyq2, run_agy_y2, run_agyq, run_fcck)
  per C3 Q4/A8; route Y9WD.click_el/type_in through the probe or
  record as excluded.
- Y10 fixer for clone1-batch3 t05/t09/t10 defects (planned by parent
  after Y3's report; spawn NOT confirmed, verify with parent).
