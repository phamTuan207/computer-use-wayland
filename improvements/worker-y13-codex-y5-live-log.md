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

## Run results (filled at run time)
- Not run yet. Per-test results, total wall time, steps, hidden-body
  encounters with diagnosis, and the test-04 step 22 observation go
  here, plus the RUN-REPORT-CODEX-Y5-20261121.md report.
