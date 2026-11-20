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

## 3.1.1 C1 (06:47-06:52 +07, elapsed 00:05)
- Wrote tests/test_phase3_c1.py (4 tests). All pass. No code change needed: the guard already exists. Commit ceff51c, pushed.

## 3.1.2 C2 (06:52-07:00 +07, elapsed 00:08)
- Added `_is_navigation_candidate` + `_settle_after_capture` to scripts/cu.py; wired into desktop_act after-capture (one 400ms settle re-capture when the batch may navigate; keeps the newer frame when the hash changed). Tests tests/test_phase3_c2.py (5 tests). All 9 Phase 3 tests pass. Commit 6be6784, pushed.

## 3.1.3 C3 (07:00-07:08 +07, elapsed 00:08)
- Added `_is_zen_ctrl_t` + `_refuse_zen_ctrl_t` to scripts/cu.py; wired into desktop_act preflight (raises PreflightRefusal before any focus/input). Tests tests/test_phase3_c3.py (6 tests). All pass. Commit 92944da, pushed.
- Live verified 07:08 +07: Zen Hyprland class is exactly `zen` (hyprctl clients on the laptop), so the guard matches the real window.

## 3.1.6/3.1.7/3.3 C6, C7, D1-D5 (07:08-07:20 +07, elapsed 00:12)
- Wrote docs/brief-template.md (canonical brief header: task, source workflow, saved method, all lessons, progress/blockers/stalls incl. C7 narrate + overlay acquire/release, verify-don't-invent, Zen rules, channels/process D1-D5, ban list, Polygon section) and scripts/brief_check.py (checker CLI, 16 always rules + 8 Polygon rules, exit 0/1). Tests tests/test_phase3_brief.py (5 tests; template itself passes, with and without --task polygon). Extended docs/worker-brief-checklist.md with section 9 (D1-D5, C7). Commit aa114b2, pushed.
- C7 verified, no new code: narrate rule in template section 5 + checklist section 9; scripts/timing.py, drive_log.py, step_watchdog.py (STEP_TIMEOUT 210s, HEARTBEAT 300s), overlay.py all exist and are referenced.

## 3.2 B1-B14 + C4, C5 (07:20-07:45 +07, elapsed 00:25)
- Wrote docs/polygon-upload-runbook.md from the workflow file (all B1-B14 rules with exact fixes; C4 Commit Changes at end of right column under ADDED changes, press End; C5 /problem/<id> 404, enter via Dashboard > View Problems > Continue left link; B9 hover_click; B14 verification-failed is NOT a stop rule; B5 new package per revision, procedural).
- Wrote scripts/polygon_checks.py (offline validator: B1 .cpp, B2 short name, B3 duplicates by hash, B4 contiguous 1..N, B6 hash link, B7 english, B8 $ balance, B12 zip inputs only, B13 count). Tests tests/test_phase3_polygon.py (10 tests).
- Real-data verification against the actual CF26 upload files: all 3 problems pass B1/B2/B4/B7/B8/B13; the validator correctly flags the B12 error in all 3 original zips (they contain .a answer files) and found a real duplicate [21, 28] in the P2 test set. Commit 2f0510d, pushed.

## 3.1.8 C8 (07:45-07:55 +07, elapsed 00:10)
- Wrote scripts/session_cleanup.py (--check verifies: no session.json, no indicator-*.sock, no stop-* markers, no overlay holders, no cursor_session guard process; --clean only prunes dead holders and orphaned stop markers, never kills a live guardian blindly). Tests tests/test_phase3_cleanup.py (5 tests, fake STATE dir + fake proc list). Commit 8636f21, pushed.

## Phase 3 DONE (07:55-08:00 +07)
- All 35 Phase 3 tests pass (C1 4, C2 5, C3 6, brief 5, polygon 10, cleanup 5).
- Ticked all 26 Phase 3 checkboxes in docs/zen-error-fix-todolist-20261121.md (3.1.1-3.1.8, 3.2.1-3.2.13, 3.3.1-3.3.5), with fix references per line. B9 has no checkbox in the list; noted as verified (hover_click, scripts/cdp.mjs 362-400) in the file. Synced the VM copy ~/workspace/zen-error-fix-todolist-20261121.md. Commit fa89ff1, pushed.
- Remaining unticked in the file: only 3.4.1-3.4.3 (E1-E3, general directions; E2 in progress in Phase 1, E3 PAUSED). Out of Phase 3 scope.
- Still needing live proof: C2 settle timing (400ms) on a real slow page load; C3 guard live-fire (a real Ctrl+T attempt into Zen must refuse); polygon_checks.py against a fresh real problem dir on the next upload; session_cleanup.py --check run on the laptop after a real session ends (needs the relay running; it is currently down).
