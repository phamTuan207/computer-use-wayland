# Worker Y4d rerun log: agy-q2 live, 2026-11-21

Task: implement Y4b's fix design in `run_live.py` / `run_agyq2.py`, then run
the full agy-q2 suite (10 tests) LIVE on the owner's Zen. Owner handed the
machine over 18:24 +07 (out of the house; any user-active signal fake).
Live-driving slot exclusive to Y4d for this rerun; Y8 (E1) waits for me.

## Timeline (Asia/Ho_Chi_Minh, 2026-11-21)

- ~18:25: implementation first pass done (diagnose-first ladder, recovery
  ladder, preflight, flagged-pass accounting). Syntax OK on VM.
  Laptop state verified: Zen alive, server 8768 serving fixtures, no
  geckodriver running.
- ~18:31-18:32: council (3) + redteam review completed. Council 1 APPROVE
  WITH FIXES, council 2 APPROVE WITH FIXES, council 3 BLOCK (FLOCK lock
  filter; infra reset; ppid-None kill), redteam BLOCK (same FLOCK bug;
  owner-away env-only; no tracked item for the extension defect).
  Papers: `improvements/worker-y4d-council-1-diagnose.md`,
  `improvements/worker-y4d-council-2-ladder.md`,
  `improvements/worker-y4d-council-3-preflight.md`,
  `improvements/worker-y4d-redteam.md`.
- ~18:33-18:40: fixes applied. Created tracked item
  `improvements/transparent-zen-defect-tracked-item.md` (OPEN). Rewrote
  `diagnose_body` (snap1 eval wrapped, snap2 error keeps snap1 class,
  tz-hidden check outside visibility branch, opacity hardening),
  `_diagnose_or_raise` (goto/refresh raise INFRA by default, allow_hidden
  opt-out only for ladder paths), `ensure_visible` (8.0 s enforced
  deadline, verified-removal flag, FIXTURE_FAILURE out of the ladder),
  `rebootstrap_tab` (registered handles only, guarded diagnose, close
  failed new tabs), `bootstrap_tab` (fresh tab, returns intervention
  info), `preflight` (handover token + Hyprland SAFETY gate + PID sweep
  + FLOCK lock check), `main` (handover re-check per test, infra reset
  on pass/session-failure, clean-only `passed`, SUITE FLAGGED headline).
- ~18:40: preflight standalone test on laptop, under flock + token:
  FAILED on BiDi `/json/version` (HTTP 404; Chrome path, does not exist
  on Firefox/Zen). Fixed to `GET /` (200). Retest: FAILED on Hyprland
  signature (not in the compositor's environ under UWSM). Fixed by
  discovering the signature from `$XDG_RUNTIME_DIR/hypr/<sig>/` and
  verifying the socket with a real AF_UNIX connect. Retest: PREFLIGHT OK.
  Negative test (no flock): refuses with "no flock holder". Both pass.
- ~18:44: handover token written on laptop
  (`/tmp/worker-y4d-handover.json`, basis: owner handover 18:24 +07).
  First launch: BOOTSTRAP FAILED, `AttributeError: 'NoneType' object has
  no attribute 'get'`, exit 2, no test ran.
- ~18:45: root cause found by probe: `d.eval(_DIAG_JS)` returned None on
  a fully loaded fixture page. Marionette `/execute/sync` runs the script
  as a function body, so the bare IIFE evaluated and discarded its value.
  `_DIAG_JS` was the only value-returning script in either file without
  a top-level `return` (audit of all `.eval(` call sites). Fixed with
  `return (() => {...})()` plus None-sample guards in `diagnose_body`
  (null sample is FIXTURE_FAILURE, never a crash) and defensive guards in
  `_log_diag` / post-remove check, and traceback printing on
  PREFLIGHT/BOOTSTRAP/RUNNER failures. Probe re-run: full snapshot dict,
  VISIBLE, tzHidden False, rafTicks 3.
- ~18:47-18:48: run 1 launched. 8/10 clean, 0 flagged, 2 failed (q02,
  q06), exit 1, total 49741 ms, 0 hidden-body encounters.
  Both failures adjudicated as checker bugs against the fixtures (q02:
  fixture stores `'Olive oil'`, check demanded lowercase; q06: badge
  textContent has surrounding whitespace from the template literal,
  exact `== "Downloaded"` too strict). Fixes: `norm(ing).lower()` for
  q02; `norm(txt(...)) == "Downloaded"` for both q06 badges. Run 1 logs
  preserved on laptop as `/tmp/worker-y4-run-1.log`,
  `/tmp/worker-y4-live-1.jsonl`.
- ~18:50-18:51: run 2 launched with the checker fixes. **10/10 clean,
  0 flagged, 0 failed, exit 0, total 49885 ms, 0 hidden-body encounters.**
  Run 2 logs preserved as `/tmp/worker-y4-run-2.log`,
  `/tmp/worker-y4-live-2.jsonl`. No runner processes left running.

## Per-test, run 2 (ms)

q01 5599 PASS, q02 5067 PASS, q03 5012 PASS, q04 4775 PASS, q05 4828 PASS,
q06 4834 PASS, q07 4787 PASS, q08 5142 PASS, q09 4942 PASS, q10 4899 PASS.

## Per-test, run 1 (ms)

q01 5607 PASS, q02 5111 FAIL (checker case), q03 5002 PASS, q04 4772 PASS,
q05 4820 PASS, q06 4848 FAIL (checker whitespace), q07 4837 PASS,
q08 5114 PASS, q09 4926 PASS, q10 4704 PASS.

## Hidden-body verdict

0 encounters in 20 tests. No tz-hidden sighted. Transparent Zen mechanism
NOT confirmed live. Ladder recovery paths never fired for a real hidden
body; only diagnose + visible ran. Decisive experiment (Council C design)
still owed for proof.

## Findings to carry forward

1. Shared bootstrap tab does not survive its session: 10/10 tests printed
   `shared tab gone, rebootstrap` in both runs; suite-end cleanup hit
   `no such window` for all 10 rebootstrap tabs. Most likely mechanism:
   Marionette `DELETE /session` closes the session's current top-level
   window. Rebootstrap per test covered it; the "shared tab" design is
   currently fictional. Follow-up: one session for the whole suite, or
   accept per-test tabs.
2. Preflight is genuinely fail-closed and was proven so on the laptop
   (positive + negative tests), but only after fixing two real bugs it
   caught itself (BiDi endpoint, Hyprland signature discovery).
3. The `_DIAG_JS` missing-return bug was latent since the first pass and
   survived council review (code review, no live run). Lesson: a diagnose
   helper needs one live eval before the suite trusts it.

## Files changed (this worker, commit scope)

- `tests/realistic/run_live.py`
- `tests/realistic/run_agyq2.py`
- `improvements/transparent-zen-defect-tracked-item.md` (new)
- `tests/realistic/RUN-REPORT-AGYQ2-20261121.md` (new)
- `improvements/worker-y4d-rerun-log.md` (this file, new)

Report: `tests/realistic/RUN-REPORT-AGYQ2-20261121.md`.
