# Worker Y13 live log: codex-y5 on Zen (2026-11-21 +07)

## Prep timeline (all times Asia/Ho_Chi_Minh, wall clock)
- ~19:20: plan v1 written (improvements/worker-y13-codex-y5-live-plan.md).
- ~19:20-19:35: council 1/2/3 + redteam reviewed plan v1 (papers in improvements/).
- ~19:35: plan v2 adjudicated (all findings adopted, none rejected).
  Commit c5ac985, pushed, origin/todolist-push verified at c5ac985.
  Ports changed 8770/4450 -> 8771/4452 (redteam M5: P used WD 4450).
- ~19:35-19:50: runner written (tests/realistic/run_codex_y5.py).
  Sources read line by line: run_agy_y2.py (2866 lines, Y9), run_live.py
  at 1e3901c (1802 lines, md5 84fa106c253d5e7f16daccf2ce3f14a5),
  codex-y5 check.mjs + simulate.mjs + all 10 specs + fixture spot checks.
- ~19:50: self-checks (commands + outputs below).
- ~19:52: manifest generated mechanically (26 files, run_live md5 pinned
  to 1e3901c 84fa106c...), SHIPPED.md written.
- ~19:53: runner + manifest + SHIPPED.md committed as 7923877, pushed,
  origin/todolist-push verified at 7923877.
- ~19:53: re-review spawned (Council A harness, Council B drivers,
  Redteam). Papers due: improvements/worker-y13-rereview-council-a.md,
  worker-y13-rereview-council-b.md, worker-y13-rereview-redteam.md.
  Gate: NO live driving until the re-review passes or its findings are
  fixed and re-verified.

## Self-check evidence (VM, headless, no Zen)
- `python3 -m py_compile tests/realistic/run_codex_y5.py` -> PY_COMPILE_OK.
- Ported verify transcription (runtime values, not source text):
  equal() 77/77 identical to check.mjs, check() 7/7 identical.
  `node --check` on the wrapped ported JS -> JS_SYNTAX_OK.
- STEP_COUNTS mechanically recounted from the written drivers:
  01: 86, 02: 47, 03: 63, 04: 58, 05: 59, 06: 76, 07: 51, 08: 57,
  09: 58, 10: 69 (total 624 primitives). Every spec step number 2..N
  appears in at least one primitive name per driver.
- Manifest dry run on a staged ship dir (/tmp/y13-ship-test, 27 files):
  `python3 run_codex_y5.py --verify-manifest` ->
  {"manifest_ok": true, "files_checked": 26, "mismatches": [],
   "manifest_md5": "3606fe843abe3d0db2da5ef1a8bd4f71"}, exit 0.
- Negative manifest cases (all refuse, exit 2):
  B1 exact (26 entries, 25 unique: test-08 spec dropped, test-07 spec
  duplicated) -> "duplicate manifest path:
  codex-y5/test-07-chat-search.md"; tampered fixture -> md5 mismatch;
  path escape "../escape.py" -> "manifest path escapes ship dir";
  non-dict manifest -> "manifest is not an object"; dropped file (25
  entries) -> count mismatch. Good ship restored afterwards, exit 0.

## Queue state (checked ~19:53, git fetch origin todolist-push)
- HEAD: 7923877 (Y13 runner commit).
- No Y6c commits exist yet. Y6c (Wayland-nested run) has not started.
- Y8b E1: A2 FAIL, identical quoting trap (ad64bc6); council 2 + 3 +
  redteam verdicts in (4849fec, 8888f22, 8d0fe98, c1b285a). Still live.
- Y9 agy-y2: READY, re-shipped 4e7a414 (diff2 BLOCK fixed in 7e7996d),
  waiting for the slot.
- Y12 DONE 19:33 (897ca17): merged batch-3 SOUND WITH NOTED DEFECTS,
  D1 t10 sampler tolerance hole; Y15 spawned to fix D1, must land on
  main before Y14 runs live.
- Y14: redteam 1 BLOCK D1-D5 applied (c7199ee), redteam 2 spawned.
- Live queue: Y8b E1 -> Y9 agy-y2 -> Y11b proof -> Y6c nested ->
  Y13 codex-y5 (me) -> Y14 batch-3. One runner at a time.

## Launch gate (exact, from plan v2)
Drive Zen ONLY after ALL of: (1) re-review passes (or findings fixed +
re-verified); (2) Y6c completion marker on todolist-push (commit
matching ^Y6c.*(nested|Wayland).*(complete|DONE|verdict|REPRODUCED|
NOT REPRODUCED) touching an improvements/worker-y6c-*.md file);
(3) Muse's go order, fresh, at run time; (4) launch-time checks in
order (marker, runner-quiet process check incl. hand_drive_e1.py +
codex executor, predecessor ports free, flock -w 60, preflight).
Poll cadence every 15 min at most; 4h without a Y6c marker -> report
to Muse instead of launching. Never wait silently.

## Re-review Council B (drivers) - BLOCK, ~19:49
- Paper: improvements/worker-y13-rereview-council-b.md (23,673 bytes).
- Verdict BLOCK. Drivers spec-faithful (step coverage, action sequences
  vs simulate.mjs, primitives, ported verify 1:1, WALL_CAPS, no dashes).
- F1 (BLOCKER) - step-count audit unsatisfiable: _audit_count counted
  the harness body-visible r.check (op "check", logged unconditionally
  while audit disabled), so jsonl_n = mem_n + 1 on every clean run.
  FIXED: _AUDIT_EXCLUDED_STEPS filter in _audit_count excludes
  "check: body renders visible (no hidden-body incident)".
  Verified: simulated clean-run JSONL (48 primitives + body check +
  guard/goto/eval noise) -> _audit_count("02", 1) = 48.
- F2 (BLOCKER) - STEP_COUNTS wrong for 02 and 07: my first grep missed
  `x = r.step(...)` assignments (run_02 "11 read first playlist track",
  run_07 "20 read forward modal heading"). FIXED: "02": 48, "07": 52
  (total 626). Verified: corrected recount matches the table exactly.
- F3 (SHOULD-FIX) - _reload_settings ignored the swap flag: a swapped
  ladder leaves an empty tab and the persistence wait_for times out as
  a live failure. FIXED: raise INFRA when swapped, before wait_for;
  main() now also matches ": INFRA:" in the message (r.step wraps
  raises as "step failed: ...: RuntimeError: INFRA: ..."). Verified:
  wrapped INFRA matches, live-failure message does not.
- Council A (harness) + Redteam still running at fix time; their
  findings will be adjudicated when they land, in a follow-up commit.

## Re-review Council A (harness) + Redteam - BLOCK, ~19:50-20:00

Papers: improvements/worker-y13-rereview-council-a.md (27,287 bytes,
BLOCK, 3 BLOCKER + 6 SHOULD-FIX + 2 NIT, reviewed 7923877) and
improvements/worker-y13-rereview-redteam.md (48,998 bytes, BLOCK,
6 HIGH + 7 MEDIUM + 3 LOW, reviewed 7923877, tree-moved note: HEAD
moved to 0540c0a mid-review). Both adjudicated in full below; every
fix was re-verified mechanically on the FINAL bytes (runner md5
f28b5da5fd2b02b15cc9a18bac636fe0, launcher md5
3898bc59e35f99ddef47d13350ced014, manifest md5
d3e71259dd7a5de3fab663534724428c, 27 files).

### Council A findings (all fixed)
- F1 (BLOCKER) - manifest stale for the runner itself: committed
  runner md5 f570134d, manifest wanted 9a7c6ace. Root cause: I edited
  the runner AFTER generating the manifest (the _read_shipped edits).
  FIXED: manifest regenerated from final bytes (see below).
- F2 (BLOCKER) - audit +1 leak: DUPLICATE of Council B F1, already
  fixed in 60996e8. Re-verified on final bytes: audit simulation
  10/10 (jsonl == STEP_COUNTS for every test).
- F3 (BLOCKER) - STEP_COUNTS 02/07 wrong: DUPLICATE of Council B F2,
  already fixed in 60996e8. Re-verified: AST recount matches the
  table exactly, total 626.
- F4 (SHOULD-FIX) - runner-quiet process check not wired into code.
  FIXED: launch_y13.py performs it before flock (pgrep patterns for
  run_*.py / hand_drive_e1.py, own ancestry excluded, codex matches
  warn only) AND preflight re-checks it after the lock (redteam H5).
  Verified: launcher dry run refuses on a dummy run_foo.py process.
- F5 (SHOULD-FIX) - park removal loop was dead code placed AFTER
  opened_tabs was reset to []. FIXED: moved BEFORE the close loop,
  with a loud WARNING log if a registered tab is ever found in
  opened_tabs (a bookkeeping bug; the close loop would otherwise
  close a keeper test tab).
- F6 (SHOULD-FIX) - guard treated a non-dict verify result as
  "guard held, proceed". FIXED: verify_test now sets eval_nondict,
  and open_fixture raises GuardInconclusiveError on it.
- F7 (SHOULD-FIX) - wall cap post-hoc only. FIXED: Y13Runner.step /
  check enforce the cap per primitive (raise before executing, with
  the primitive name + elapsed); the post-hoc check stays as a
  backstop. Verified: 400s elapsed on a 360s cap raises
  "wall cap exceeded: 400s > 360s at primitive 'probe'"; under-cap
  and bootstrap (no cap) pass through.
- F8 (SHOULD-FIX) - timeout match broader than the pinned wording.
  FIXED: narrowed to ("timed out" / TimeoutError / URLError) exactly.
- F9 (SHOULD-FIX) - _reload_settings tolerated ANY click error; at
  step 26 the persistence wait_for passes on STALE text from step 21.
  FIXED: window.__y13_reload_probe marker set before the click; a
  surviving marker raises a step failure (the reload did not land).
  Verified with a fake driver: raise+reload -> tolerance path;
  raise+no reload -> "marker survived" raise; ok+reload -> reloaded.
- F10 (NIT) - no handover re-check before a re-run attempt. FIXED:
  _check_handover at the top of every attempt; on failure the run
  aborts with exit 2.
- F11 (NIT) - fixture-unavailable leaves infra_blocked unchanged vs
  plan v2 "resets on any non-INFRA failure". NO CODE CHANGE (fail-safe
  direction, Y9 precedent); reconciled by amending plan v2 instead
  (see redteam M5 below).

### Redteam findings (all fixed, except where noted)
- H1 (audit) - FIXED by 60996e8, verified by the redteam on those
  bytes; re-verified here on final bytes (audit sim 10/10, AST
  recount matches). CLOSED.
- H2 (manifest) - FIXED by regenerating from final bytes (below).
  CLOSED.
- H6 (reload swap) - FIXED by 60996e8, verified by the redteam by
  diff. CLOSED.
- H3 (step-26 reload unprovable) - same defect as Council A F9.
  FIXED by the marker proof. CLOSED (fake-driver test above).
- H4 (diagnose conflates no-body with eval transport failure) -
  FIXED: new _proven_no_body(diag) helper (a snapshot with hasBody
  false AND readyState complete, and no snapshot with a body);
  applied at all 3 ladder raise sites AND in main's mid-test
  handler. A transport error is now INFRA (re-run); only a
  positively proven no-body document is fixture-unavailable. The
  wait_for / wait_ready masking is covered by the post-failure
  diagnose + this split (the base is frozen and cannot surface the
  underlying error itself). Verified: 6-case unit test, all correct.
- H5 (queue procedural) - FIXED: (a) runner-quiet process check in
  preflight; (b) own ports 8771/4452 in the launcher's port check
  (a second Y13 is refused); (c) optional Y6c marker check in the
  launcher (--repo / Y13_REPO: git fetch + exact marker patterns,
  refuses when no marker; skipped without a repo, operator asserts
  via Y13_GO). Verified: launcher dry runs refuse on own-port 8771
  answering and on --repo with no marker present.
- M1 (manifest trusts a self-consistent ship; extra files pass) -
  FIXED in part: _verify_manifest now refuses unexpected files
  (allowlist = manifest paths + manifest + SHIPPED.md +
  __pycache__; planted live_metrics.py + functools.py and a planted
  EXTRA.md both refuse, exit 2). The manifest-md5 pin is DECLINED
  with reason: it is self-referential (the pin lives in the runner,
  the runner is in the manifest, so changing the pin changes the
  manifest md5; no fixed point exists). The pin lives outside the
  ship instead: SHIPPED.md + the commit + this log record the
  manifest md5, verified by the agent at ship time via git.
- M2 (wall cap resets per attempt) - FIXED: cumulative cap. main()
  offsets r.t0 by the prior attempt's elapsed, so the per-primitive
  and post-hoc checks measure cumulative time; the summary keeps
  elapsed_ms per attempt (plan C3 F1) and adds cumulative_elapsed_ms.
  Verified: 200s cumulative passes, 370s on a 360s cap trips.
- M3 (FIXTURE-UNAVAILABLE inside r.step not matched) - FIXED:
  ": FIXTURE-UNAVAILABLE" substring match added in main, like
  ": INFRA:".
- M4 (outcome "pass" with failing checks) - FIXED: outcome set to
  "failed" when r.failures is non-empty and no exception was raised,
  before the audit block.
- M5 (infra_blocked reset rule) - RECONCILED by amending plan v2:
  the fail-safe rule is now written in the plan (fixture-unavailable
  / guard outcomes leave the streak unchanged, Y9 precedent).
- M6 (handover fingerprint is metadata, not content) - FIXED:
  sha256 of the token file bytes. Verified: a same-size rewrite
  with restored mtime is refused ("handover token changed mid-run").
- M7 (start_server failure escapes as a traceback) - FIXED: wrapped
  in main with the structured-failure pattern (suite JSON with
  server_failed, return 2). Verified: a stale server holding 8771
  gives the structured JSON, exit 2, no traceback.
- L1 (": INFRA:" substring match fragile) - FIXED: Y13Runner.step
  now re-raises the ORIGINAL exception for INFRA: / FIXTURE-
  UNAVAILABLE (mechanism-based classification); the substring
  matches in main stay as defense in depth. Verified: INFRA and
  FIXTURE-UNAVAILABLE unwrap, a plain ValueError stays wrapped.
- L2 (SHIPPED.md not in the manifest) - covered by the M1 allowlist
  (SHIPPED.md is allowlisted and its manifest md5 is recorded in the
  commit + this log). No further action.
- L3 (smoke-test tab never driven) - noted, no fix required (test
  tab only, cleaned at suite end).

### Transcription re-check (corrected method)
- First attempt compared RAW Python source text against check.mjs
  and produced 9 false diffs (the ported JS lives inside a Python
  '''...''' literal, so its \n escapes are doubled in the file).
  That was a methodology error in the check, not a runner bug.
- Corrected check on the PARSED _VERIFY_JS value (imported module):
  14 single-backslash \n, 0 double-backslash. Runtime comparison
  under node (stub document, all 10 ids, empty + WRONG + exact-value
  maps): 20 comparisons, 0 diffs, EQUIVALENT. The redteam's own
  transcription check (123 lines identical) agrees.

### Final mechanical gates (exact shipping bytes, 20:11 +07)
- py_compile runner + launcher: OK.
- Manifest regenerated LAST from final bytes: 27 files, md5
  d3e71259dd7a5de3fab663534724428c; runner f28b5da5, launcher
  3898bc59, run_live 84fa106c (1e3901c pin holds).
- Staged ship /tmp/y13-ship-final --verify-manifest: exit 0,
  manifest_ok true, 27 files.
- Negative manifest cases (7/7 refuse, exit 2): tamper, escape,
  non-dict, dropped, B1 exact (duplicate run_codex_y5.py + dropped
  spec), extra top-level .py (live_metrics.py + functools.py),
  extra file in the suite dir.
- Audit simulation with the real _audit_count: 10/10 (jsonl ==
  STEP_COUNTS for every test). AST recount matches the table,
  total 626.
- Launcher dry runs (final ship at /tmp/worker-y13-server, 5/5):
  no Y13_GO refuses; dummy run_foo.py refuses; own port 8771
  answering refuses; --repo with no Y6c marker refuses; all clear
  passes the launcher checks and hands off to the runner (manifest
  OK, served files OK, preflight fails on BiDi 9222 as expected on
  the VM, no Zen here).
- Dash check: zero em/en dashes in the runner, launcher, SHIPPED.md,
  both re-review papers, the plan, and this log.

### Queue state, 20:11 +07
- No Y6c completion marker on todolist-push (git log with the exact
  marker patterns returns nothing; no Y6c commits at all). Y8b is
  live on B1-v2.2 (launched 20:06:32). Queue order unchanged:
  Y8b -> Y9 -> Y11b -> Y6c -> Y13. Still waiting for the slot;
  the launch gate (marker + Muse's go order + launch-time checks)
  has not opened.

## Run results (filled at run time)
- Not run yet. Per-test results, total wall time, steps, hidden-body
  encounters with diagnosis, and the test-04 step 22 observation go
  here, plus the RUN-REPORT-CODEX-Y5-20261121.md report.
