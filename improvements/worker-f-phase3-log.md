# Worker F - Phase 3 fix log (Codex errors C1-C8, upload errors B1-B14, process D1-D5)
# Start: 2026-11-21 06:37 +07 (Asia/Ho_Chi_Minh). Rule: one small piece = one small commit, push immediately. No ydotool. No em/en dashes. Log wall-clock + elapsed for every step.

## Verification before writing code (06:37-06:45 +07, elapsed 00:08)
- C1 (120s expiry): ALREADY enforced in both loops. cu.py `_valid_capture_identity` refuses age outside 0..120s (line 745), called by `validate_desktop_observation`; code_exec.py raises at 120s (lines 550, 603). What is missing: a unit test proving it. Fix = test only.
- C2 (after-click shows old page): REAL gap. desktop_act sleeps 0.08s then takes one after-capture; a navigation click has not loaded yet. Fix = settle re-capture after navigation-candidate actions.
- C3 (Ctrl+T): REAL gap. No guard anywhere. Fix = refuse Ctrl+T when the target window class is zen, in desktop_act preflight.
- C4/C5 (Commit Changes location, /problem/<id> 404): procedural knowledge, no code. Fix = Polygon runbook doc.
- C6 (ydotool ban in every brief): checklist has it, but no machine-checkable template. Fix = brief template + brief_check.py.
- C7 (static screen): tooling exists (timing.py, step_watchdog.py, drive_log.py, overlay.py). Gap = narrate-before-acting rule not in the brief template. Fix = template rule + wire references.
- C8 (no cleanup after use): guardian cleans up, but nothing VERIFIES clean after finish/stop. Fix = session_cleanup.py --check.
- B1-B14: no Polygon code in repo at all. Fix = runbook doc (source: QUY-TRINH-UP-DE-POLYGON-CODEFORCES-2026-11-20.md, read in full 06:45) + polygon_checks.py validator. B9 hover_click already exists in cdp.mjs (verify + reference). B14 "verification fail means stop" already a tripwire in claim_check.py (verify + reference).
- D1: already in checklist (I39). D2/D3/D4/D5: missing from checklist. Fix = add to checklist + brief template.
