
## 19:47-19:55 21/11: redteam 1 verdict BLOCK, D1-D5 applied, commit c7199ee

Redteam 1 (plan review, 411-line version) returned BLOCK with 5 decisive
holes, all fixed in code + plan, commit c7199ee on todolist-push, verified
in the branch (ancestor of todolist-push, head 8888f22 is Y8b council 3).

- D1 (deterministic): ArrowRight/ArrowDown PUA codes swapped in the first
  draft. W3C: Right U+E014, Down U+E015. Fixed in run_batch3.py
  (KEY_ARROW_RIGHT \uE014, KEY_ARROW_DOWN \uE015) and plan. Preflight
  (i) now asserts the recorded e.key strings are exactly ArrowRight and
  ArrowDown. Verified by import check.
- D2 (deterministic): t09 absolute handle counts 3/1 copied from
  check.mjs, which runs in a fresh Playwright context. Live handles()
  returns every tab/window in the attached Zen. Fixed: handles_before
  captured at t09 start, +2 at two-popups, baseline at end. Verified:
  'n == 3' and 'n == 1' gone from run_b3_t09.
- D3: t10 sampler Promise unproven + no fail-closed rule. Spec claim is
  correct (W3C Execute Script 13.2.1; Marionette bug 1398095, Firefox
  67), but this Zen's geckodriver was unverified. Fixed: preflight
  (vii) Promise eval returns 42 + bare-IIFE control returning null;
  sample_position_min raises RuntimeError on None/non-numeric, never
  defaults to 0. Verified in source.
- D4: hidden-body ladder prescribed fixture reload on swap for popup
  tabs. Fixed in plan text (main tabs only; popups allow_swap=False,
  persistent hidden is INFRA). The code already passed allow_swap=False
  for popups, verified.
- D5: window.open popup transfer unproven (t09 popups are windows, not
  tabs). Fixed: preflight (viii) opens a real window.open popup from a
  click on #probe-popup-btn, switches, asserts visible, closes, asserts
  the handle count returns to baseline. New file
  tests/realistic/run_batch3_probe_popup.html.
- Sixth bug found during the fix (inspection, not redteam): run_preflight
  opened "/probe.html", a file that does not exist. Fixed to
  "/run_batch3_probe.html" with the tab handle captured for the
  switch-back. The first fix attempt died on its first assert (it
  assumed the wrong URL) and wrote nothing; the failure was caught by
  the verification inspect. Also fixed in the same pass: the probe page
  edit had broken the main <script> tag (repaired, JS syntax OK via
  node new Function check).
- Line-by-line verification (redteam demand): run_batch3.py diffed
  against all 10 check.mjs files. t04 #empty visible and t06 #form-day
  label 'June 12, 2026' are both present in the runner (plan text was
  summary-level). No assert in any check.mjs found missing. Details-only
  differences: t01 historyLines counts non-empty lines vs check.mjs
  regex; t10 supplementary D1 diagnostic does not affect the verdict.
- Redteam 1 stale claims noted: it read the plan before run_batch3.py
  existed ("no code exists") and before Y12 reported. Y12 HAS reported
  (897ca17, SOUND WITH NOTED DEFECTS, D1 only).
- Redteam 2 spawned 19:55 to review run_batch3.py itself before the
  slot opens (verdict file improvements/worker-y14-redteam2-verdict.md).
  Slot still closed: Y8b holds it (E1 arm A failed twice), then Y9,
  Y11 proof, Y6b, Y13, then Y14. Y9 READY per MEMORY.md 19:34
  (diff2 fixes in 7e7996d, ship frozen 4e7a414, laptop re-ship green).
  Y15 D1 fix not yet landed on main at last check.
