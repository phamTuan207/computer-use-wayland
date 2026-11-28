# Worker Y11b: live metrics proof run log (t01 + f01, metrics ON)

Worker Y11b, Muse live runner. Task: run the metrics proof for the
live_metrics.py wiring Y11 built (commit 91d3cd2). Ship live_metrics.py
+ run_live.py into the proof server dir on the laptop, run t01 + f01
with metrics ON, live on Zen. Acceptance per C3 A12.

All times Asia/Ho_Chi_Minh, 21/11/2026. No ydotool, no em/en dash,
no personal info. Evidence contract: exact command + output/log,
commit hash, timed run log.

## 0. Slot claim

- 20:30 +07: Y9b finished agy-y2 live 10/10 (commit 7f547c6) and
  released the live slot. Parent (Muse) assigned the slot to Y11b.
- 20:33:17 laptop check: Zen PID 27958 alive (BiDi 9222 HTTP 200,
  Marionette 2828 listening); no runner processes
  (`pgrep -af "run_.*\.py|hand_drive|run_live"` empty); no fixture
  server on 8765/8767/8771, no geckodriver listening. Slot FREE,
  Y11b is the only live runner. (Y13r is review-only, Y15 is VM
  headless; neither drives Zen.)

## 1. Ship manifest (todolist-push HEAD 7f547c6)

Proof server dir: /tmp/worker-y11b-server on the laptop.
Shipped from the VM repo at HEAD 7f547c6 (run_live.py last changed
in 91d3cd2, the Y11 wiring commit; live_metrics.py likewise).

VM staging: /tmp/y11b-ship, md5s:

```
d8e2b14d7456b2866790f4a87ec1919e  run_live.py
ccf30b19e39b21643c7fada0946f9a82  live_metrics.py
3a2ed1af4cf75c21d21ab7f2dbdac620  jsonlutil.py
5fb5a960b2a7831e5bcbac5e36abfd53  hit_rate.py
48e7b95b32f44b97a82668dfc5f2bac2  timing.py
2b6eda97036af51510b7eefe6d36dd93  fcc-k/test-01-spreadsheet.html
```

live_metrics.py needs jsonlutil.py, hit_rate.py, timing.py in the
same dir (it inserts its own parent into sys.path and imports them);
all five .py files shipped together.

Fixture note: clone1 fixtures are NOT in the repo (git ls-files
shows no clone1 fixture). t01-upload-single/fixture.html exists
only on the laptop at /tmp/worker-p-server/clone1/t01-upload-single/
(md5 94d57988d58b9b4c74335ca2e1e7801e, the file Worker P ran).
It is copied laptop-local into the proof server dir.
The fcc-k file on the laptop server (/tmp/worker-p-server/fcc-k/,
md5 c77aba93, dated 15:48) is STALE: it predates the S fix
(cbbb748, 16:30 +07) that the repo now carries. The proof ships the
REPO version (2b6eda97, byte-identical to the laptop repo checkout
at ~/workspace/computer-use-wayland). Both the metrics-on
run and the metrics-off baseline run use the same shipped bytes, so
the A12 comparison stays valid either way.

## 2. Laptop ship + import gate (Y14 note: verify import BEFORE the slot run)

- 20:34 +07: tarball sent (VM /tmp/y11b-ship -> laptop
  /tmp/worker-y11b-server), extracted. t01 dir copied laptop-local
  from /tmp/worker-p-server/clone1/t01-upload-single/.
- 20:35:08 md5sum -c MANIFEST.md5: all 6 files OK.
  clone1/t01-upload-single/fixture.html md5 94d57988d58b9b4c74335ca2e1e7801e.
- Import gate, 20:35: `python3 -c "import live_metrics, run_live"`
  from the server dir -> import-ok, live_metrics resolved to
  /tmp/worker-y11b-server/live_metrics.py. LiveMetrics constructed
  OK (run 20261121-203509-344944-244acf). (The cleanup os.remove in
  that one-liner raised FileNotFoundError because LiveMetrics
  creates the file lazily on first write, not at construction;
  construction itself succeeded, which is what the gate checks.)
- Rigorous bootstrap check: `python3 -c "import run_live"` from the
  server dir -> run_live.live_metrics is the server-dir module,
  LiveMetrics class present. Default metrics path
  /tmp/worker-p-live-metrics.jsonl (sibling of default LIVE_LOG).
  GATE PASSED. No silent metrics-off.
- Proof run env (explicit paths, so P's logs are not clobbered):
  LIVE_SERVER_ROOT=/tmp/worker-y11b-server, LIVE_SERVER_PORT=8765,
  WD_PORT=4445, LIVE_LOG=/tmp/worker-y11b-live.jsonl,
  LIVE_METRICS=/tmp/worker-y11b-live-metrics.jsonl.
  Wrapped in flock -w 60 on ~/.cache/agent-computer-use/zen_dom.lock
  (one-runner rule; run_live.py itself does not take the lock).

## 3. Metrics-ON proof run (t01 + f01, live Zen)

- Launched 20:35:33 +07, detached under flock. Finished 20:35:40
  (f01 finished_at 13:35:40Z). Wall ~7 s.
- t01 PASS, 6 steps, 4 checks, elapsed 2693 ms. f01 PASS, all
  checks (E2 540000, E3 574000, E4 750000, E5 1864000, E6 621333,
  E7 3), elapsed 3634 ms. SUMMARY 2/2 passed, total_ms=6327.
- Step log /tmp/worker-y11b-live.jsonl (12,718 B, 76 rows).
  Metrics /tmp/worker-y11b-live-metrics.jsonl (70,162 B, 201 rows):
  metrics were written, NOT silent-off.
  Run id 20261121-203533-345281-457f08.
- Note: the fcc-k fixture shipped is the repo (S-fixed) version,
  and f01 passed live on it, including the COUNT -> COUNTA
  correction path. The stale laptop-server copy was NOT used.

## 4. Metrics-OFF baseline run (same tests, same shipped bytes)

- Launched 20:36:15 +07, finished 20:36:21. t01 PASS 2675 ms,
  f01 PASS 3564 ms, SUMMARY 2/2 passed, total_ms=6239.
  LIVE_LOG=/tmp/worker-y11b-live-off.jsonl (12,714 B, 76 rows),
  LIVE_METRICS=off (the one "metrics" line in its stdout is the
  expected "[metrics] OFF (LIVE_METRICS=off)" stderr line).
- No leftover processes after either run; fixture server and
  geckodriver both down; Zen alive (BiDi 9222 HTTP 200).
  Cleanup check 20:38:18. Slot released.

## 5. Acceptance (C3 A12) - ALL PASS

Analysis script /tmp/y11b-accept.py (kept on the laptop),
run 20:37:25 +07, exit 0. Independent WD.click count by AST on
the shipped runner: run_t01 1 call site, run_f01 2 call sites
(loop over 18 rows + select E7) = 20 calls.

- A1 verify_jsonl empty: PASS (bad=[]).
- A2 exactly one summary row: PASS (count=1).
- A3 step rows match log_step 1:1: PASS (76/76), ok flags agree,
  off-run steps identical (76).
- A4 click_attempt == WD.click calls: PASS (20/20), all hit,
  all backend dom. Summary clicks.attempts/hits 20/20.
- A4f js_clicks_excluded == 1 (TRAP click_js): PASS.
- A4g eval_clicks_excluded == 26 (18 press-type + 6 press-Enter
  + 2 correction): PASS.
- A4h UNRELIABLE flag: FIRES BY DESIGN (js+eval share 57% >
  10%, reason "js+eval click share 57% exceeds 10%", share
  0.574). f01 legitimately drives most clicks through d.eval
  (press type/Enter buttons); the flag is the honest disclosure
  that the 20/20 selector-delivery rate must not be read as an
  overall action success rate. Not a wiring failure.
- A5 RESULT/SUMMARY identical modulo timing: PASS (3 lines each).
- A5b step stdout identical modulo elapsed ms + per-run tab-handle
  UUID in open-fixture detail: PASS (89 lines each).
- A6 wait_s + exec_s <= act_s every step: PASS (0 violations).
- A7 scripted think: PASS (all think_s null, think_source
  scripted, think_median_s null, model_calls 0,
  actions_per_call null).
- A8 type_attempt == 20 (18 cells + 1 correction + t01 title):
  PASS, hits 20/20.
- A9 summary: PASS (tests [t01, f01], tests_total 2,
  tests_pass 2, steps 76, steps_ok 76, metrics_dropped 0).
- Row totals: 201 rows = 76 step + 84 action + 20 click_attempt
  + 20 type_attempt + 1 summary.

First analysis run had 8 FAILs; all 8 were errors in MY expected
counts in the script, not wiring defects, each re-derived from the
shipped test code before correcting: the rows list has 18 cells,
not 17 (so 20 clicks, 20 types, 26 eval-clicks); summary "tests"
is a list of ids, not a count; the open-fixture tab handle UUID
differs per run by design; UNRELIABLE fires by design at 57%
share. The corrected script re-ran ALL PASS. No test file or
runner file was modified to make the checks pass.

## 6. Verdict

PROOF PASS. The live_metrics.py wiring is proven live on real Zen:
the metrics file parses clean, has exactly one summary, step rows
match log_step 1:1, click_attempt count equals the WD.click call
count, js/eval clicks are excluded and disclosed, RESULT/SUMMARY
stdout is unchanged by metrics, and every step obeys
wait+exec <= act. metrics_dropped 0.

H2 STAYS OPEN, as designed: this was a scripted run, think_s is
null on every step. The proof closes the wiring gap, not H2. Only
an agent-driven run (hand-drive with an agent operator, or a
future agent runner) producing real think values closes H2.
I8 stays partially closed: the measured rate is the
selector-delivery rate (20/20, pointer occlusion/intercept on
selector-resolved clicks), not the vision grounding hit rate;
calibration E2 (58.6%) remains the only vision number.

Evidence committed in this repo (tests/realistic/):
live-run-y11b-proof-20261121.jsonl (step log, on),
live-run-y11b-proof-20261121-metrics.jsonl (201 rows),
live-run-y11b-proof-20261121-off.jsonl (baseline step log),
live-run-y11b-proof-20261121.stdout.log,
live-run-y11b-proof-20261121-off.stdout.log.
Laptop originals remain at /tmp/worker-y11b-live*.jsonl,
/tmp/worker-y11b-stdout*.log, /tmp/y11b-accept.py, server dir
/tmp/worker-y11b-server (frozen ship, md5s in section 1).
