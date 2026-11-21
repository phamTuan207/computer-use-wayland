# Worker CLICK-RT log (redteam review of the CLICK-FIX diff)

Branch: todolist-push. Target: commit e4082ff (CLICK-FIX: G28 loud refusal, type verification, zen_dom TimeoutError, ime trace in envelope; 8 files, +824/-38). Read-only on the fix code: no fix file modified. No laptop driving, no live browser, no ydotool. All attacks run offline on the VM against the real code at e4082ff, using the repo's own test harnesses. Demo script: /tmp/click-rt-demos.py (not committed; outputs quoted below). No em/en dashes in this log.

## Step log (wall-clock Asia/Ho_Chi_Minh + elapsed from task start 01:39:09)

- 01:39:09 +07 (t+0s) Start. Repo at ~/workspace/computer-use-wayland, branch todolist-push, HEAD e4082ff at start.
- 01:39-01:41 (t+0-2m) Read the fix diff (scripts/cu.py, scripts/first_action.py, scripts/zen_dom.py), the fix log (e4082ff), the SRC log (050272d: conversion proof, G28 staleness-only trigger, verification asymmetry), the sweep log (affaf54), and the probe log (fa289eb, Stage A).
- 01:41-01:44 (t+2-5m) Read the touched code in full at HEAD: first_action.py run() and _fresh_observation (lines 292-560), cu.py desktop_act (lines 1487-1880), image_point (995), keyboard_groups (1111), literal_keyboard (1161-1260), zen_dom.py _wd/tab_at/list_tabs (140-260). Checked callers of desktop_act (cu.py:2254, 2543; first_action.py:563), callers of list_tabs (only the zen_dom CLI list/tab subcommands; codemode uses locate only; zen_cli has its own BiDi list_tabs; F3 evidence scripts use raw _wd), session_cmd (first_action.py:175-180, no --no-after), is_completed_capture_error (cu.py:1363-1367).
- 01:44-01:45 (t+5-6m) Ran the fix's own suites: python3 -m unittest test_first_action test_type_verification test_zen_dom test_keyboard_preflight: 139 tests, OK.
- 01:45-01:46 (t+6-7m) Ran /tmp/click-rt-demos.py (7 attacks). All 7 succeed; outputs quoted under each finding.
- 01:46 (t+7m) Noted HEAD moved while I worked: 9350db7 CODEX-DEMO ("Codex sent the clone1 message, Muse failed on a grounding error (input point 64px above the field)"). My target stays e4082ff as tasked; the G30 live status changed elsewhere, the defects below stand on the code alone.

## Findings

### R1 (GATING, type verification false-passes on the exact incident shape)

Claim under attack: after a type batch, an unchanged after-capture frame fails the batch, so a re-run of Stage A would now report ok False with error_code type_unverified (fix log, 01:35:06 entry).

What the code actually checks (scripts/cu.py:1847): `result['frame_bytes_changed'] = result['after']['pixel_sha256'] != meta['pixel_sha256']`, where meta is the PRE-BATCH observation. The verification block (cu.py:1861-1871) then sets type_verified from that one bit. The baseline is pre-batch, not pre-type, so any click in the same batch sets the bit: title-bar click changes the active window chrome, input click shows a caret and focus ring. Stage A, CL1-MSG batch 3, and the CL1-MSG2 retry ALL contain clicks before typing, so the check measures "the batch changed the screen", not "the text landed".

Demo D2 (repo's own harness, test_keyboard_preflight.DesktopPreflight, where cu.run_cancelable is stubbed to return '' so wtype never runs and NO text is delivered anywhere):
- click(10,10) + type 'hello', after frame hash differs by fixture: ok=True, completed=2, type_verified=True. ATTACK SUCCEEDS.
- Same batch, after frame hash unchanged: ok=False, type_verified=False, error_code=type_unverified. The verdict flips on the frame hash alone, never on whether typing delivered anything.

Consequences:
- The fix log's Stage A claim is unproven and, by this mechanism, likely false. No test covers a click+type batch whose frame changed by the click but not by typing; test_type_verification.py only covers type-only batches (test_type_batch_changed_frame_verifies passes because the fixture hash says "changed", while the harness delivered zero text).
- A type into the WRONG field, or a type that opens an autocomplete dropdown, also passes: any pixel change anywhere in the frame verifies.
- The code comment (cu.py:1851-1856) admits "animations also change the frame" but understates it: the batch's own clicks are the confound, not ambient animation. Note the repo already has a targeted helper, _action_points_changed (cu.py, near line 1005), which diffs a 48x48 patch around action points with a threshold; the verification does not use it, and a type action has no x,y to anchor a patch to (the anchor would have to be the preceding click point).

Required fix: verify the typed text, not the whole frame. Minimum credible shape: diff the patch around the last pointer target before vs after typing (using the existing patch-diff helper), or read the field content (DOM/CDP where available). Until then, do NOT claim Stage A, batch 3, or the retry would now fail; correct the fix log sentence that says so, and add a test for the click+type shape with a frame changed by the click only.

### R2 (GATING, residual demonstrated: pointer-only batch on a substituted screen observation)

Demo D1, real cu.image_point with the CL1-MSG2 numbers (window region [2533,914,901,1176], image 901x1176, monitor eDP-2 box [2464,902,1920,1200]):
- (250,1037) on the GIVEN window observation -> global (2783.0, 1951.0), correct (probe P1/P2 0-1px).
- Same (250,1037) on the SUBSTITUTED screen observation -> global (2714.0, 1939.0). Error dx=-69, dy=-12, exactly the window offset inside the monitor.
- cu.py move() (cu.py:1614-1620) computes gx,gy from the meta it was given and checks cursorpos against THOSE coords (3px tolerance), so a cursorpos read of (2714.0, 1939.0) passes by construction. Cursorpos verification cannot catch a wrong-origin click: it is self-consistent with the wrong target.

Envelope on stale obs 8fef498445d2 (age 114s) + pointer-only click + session ok (repo's TestRun harness): code=0, ok=True, path=session, completed=1, fallback_reason=None, error=None, observation.source='captured', observation.given_observation_rejected={given_id 8fef498445d2, age_s 114.0, reason stale}. The rejection is visible ONLY in that nested field. The repo's own test (test_first_action.py, test_stale_given_observation_pointer_only_proceeds_recorded) asserts fallback_reason is None on this path, so the silence is baked in as expected behavior.

This was a known residual flagged by the fix log itself, and proceeding is per the SRC spec, so this is not a spec violation. It is a live silent-misdirection hole all the same: the "never silent" claim fails for the pointer path, and any consumer reading ok/completed (the normal contract) sees a clean success while the click lands 69px left and 12px up of the intended point, with no top-level signal at all.

Required fix: at minimum set fallback_reason (or an equivalent top-level flag) on the pointer-only proceed path too, so the substitution is visible without deep-inspecting envelope['observation']. The stronger fix, a refusal for pointer batches whose coordinates are window-image coordinates, is a spec decision for Muse, not something this review can impose; but the top-level flag is not optional.

### R3 (act-now envelope drops type_verified and error_code on both paths)

Demo D4 (TestRun harness):
- Session path, session stdout carries ok False, error 'type verification failed...', error_code 'type_unverified', type_verified False: envelope code=1, ok=False, error text present, but 'type_verified' in envelope: False and 'error_code' in envelope: False.
- Fallback path, desktop_act returns the same fields: same drop. first_action.py:574-579 copies only ok, completed, ime_state_trace, error.

Consequence: the fix log's discriminator procedure tells a live agent to read "type_verified True/False (frame changed or not)" from the envelope. That field does not exist in the act-now envelope, so the procedure as written cannot be executed. Only the error string survives, and only when ok is False.

Required fix: copy type_verified and error_code from the session result and from the fallback desktop_act result into the envelope on both paths (None when absent, so the field is always present).

### R4 (G28 refusal message advises a remedy that cannot type)

Demo D5: loud_substitution_refusal (first_action.py:357-379) tells the agent: "omit --observation and write coordinates for the screen". A type batch with no observation takes a screen capture, and desktop_act refuses key/type on screen scope (cu.py:1497, demonstrated in the harness: PreflightRefusal 'screen observations support pointer actions only; use a window or accessibility target for typing'). The advised remedy fails with the same scope refusal the message was written to replace.

Required fix: on the key/type refusal path, offer only the fresh-window-observation remedy. The screen-coordinates option applies only to pointer-only batches, but this message is shown exactly on the key/type path.

### R5 (zen_dom _wd still lets malformed responses escape raw)

The module docstring (scripts/zen_dom.py:31-34) claims every WebDriver call converts TimeoutError, OSError, and URLError into ZenDomError "so a hung Marionette tab-switch never escapes raw". The except clause (zen_dom.py:166) covers only those three. Demo D3a, mocked urlopen:
- Response body b'not json': raw json.JSONDecodeError escapes _wd (json.loads at zen_dom.py:159 is outside the try's except set). ATTACK SUCCEEDS.
- urlopen raising http.client.BadStatusLine: raw BadStatusLine escapes (HTTPException is not OSError or URLError). ATTACK SUCCEEDS.
- The same escape applies to evaluate/locate through _wd, and to KeyError when a response lacks "value" (current_handle, _read_current_tab, list_tabs index ["value"]).
- The F3b case itself (TimeoutError) IS converted, and the conversion tests pass, so this is a gap in the "never raw" claim, not a failure of the F3b fix.

Required fix: widen _wd to convert JSON decode failures and http.client.HTTPException (and KeyError on a missing "value") into ZenDomError, or correct the docstring to name exactly what is converted.

### R6 (zen_dom tab_at/list_tabs swallow a failed restore, leaving the wrong tab selected)

Demo D3b (FakeWdSession subclass where the restore POST raises ZenDomError): tab_at(2) returns the tab dict with no error, but session.current is 'ccc33333' while the original was 'aaa11111'. The finally blocks (zen_dom.py:229-233 for tab_at, 242-247 for the full scan) swallow the restore failure with `except ZenDomError: pass`. The docstring promises "the original tab is restored". Any later evaluate/locate then runs in the wrong tab, silently.

Required fix: surface a restore failure (raise, or return/include a restore_error on the entry) instead of swallowing it. Same for the full-scan finally.

### R7 (zen_dom full scan on a wedged session burns one timeout per handle)

Demo D3c: list_tabs on a fully wedged session returns 3 error entries after 4 switch attempts (one per handle plus restore). At the 30s default timeout (zen_dom.py:79) that is up to 120s for 3 tabs and 540s for 17 tabs, versus the old code dying at the first hang (30s). F3b proved a hang means the session is wedged and only a restart clears it (Arm E), so the later attempts are near-certain to hang too. The per-handle catch is the Arm D v2 diagnostic pattern, not a production listing strategy.

Required fix: stop the scan after the first hang (or enforce a scan time budget) and report the wedge, instead of attempting every handle.

### R8 (tab_at's "handle order is tab order" rests on one data point and is unverified)

tab_at (zen_dom.py:196-206) and the `tab` CLI help assert "Handle order is tab order (proven in F3b Arm A run 3)". What Arm A run 3 proved: handles[8] was the example.com tab in one session with 17 handles (worker-f3b-restart-log.md, 23:35:31). One tab, one run. It does not prove handle order equals visual tab order in general (tab drags, restores, and pinned tabs reorder visuals without reordering creation-ordered handles), and it sits next to the sweep's own warning (affaf54: "sidebar shows fewer rows than BiDi, order differs, never infer a row from a BiDi index"). tab_at also does not verify the switched tab's title/URL, unlike the Arm A pattern it cites, which verified the URL after switching.

Required fix: verify the switched tab (title/URL) in tab_at, or downgrade the claim (handle-list index, not visual tab index; can go stale between calls) and document it.

### R9 (minor, docstring overclaims the G28 refusal)

first_action.py module docstring (lines 56-61): a stale/missing/unreadable given observation "is NEVER silently replaced by a screen capture that the batch then acts on (G28): the run refuses loudly instead". Pointer-only batches ARE acted on after substitution (R2). Same overclaim in the _fresh_observation docstring ("the caller (run) must refuse loudly on it instead of acting on the substitute"). Required fix: scope both docstrings to key/type batches.

### R10 (minor, noted, no change demanded)

- Verification is skipped, not failed, when after_capture is False (ok True, type_verified None, repo test asserts this) and when terminal_address is None (after-capture skipped, 'after' absent, type_verified absent entirely, ok True). The CLI guards --no-after with a final assert action (cu.py:1103) and code-exec guards no_after with a DOM assert, so the bypass is guarded at the callers, not in desktop_act itself. Note it; do not present type_verified as always present.
- Age check uses the max session deadline, not actual attempt time (first_action.py:292-325): age 70s + deadline 60s refuses a batch that would finish in seconds. Conservative by design (redteam A6); a real attempt budget would be less refusal-prone, but no valid run was found refused outright beyond this edge.
- list_tabs calls current_handle() before the range check (zen_dom.py:208-216): an out-of-range `tab 99` pays a round trip first and can raise a transport error instead of the clear out-of-range error. Move the range check first.

## False-refusal hunt (G28): no hard false refusal found

- The refusal fires only when a given observation was rejected AND the batch has key/type actions (first_action.py:481-492), before any session attempt, naming id, age, and reason, setting fallback_reason, returning 1. A fresh given observation with typing still reaches the session (tested).
- The trigger covers all three rejection reasons (stale, unreadable, incomplete), matching the SRC spec as written ("given but obs_source is captured and the batch contains key/type actions"). "Staleness-only" in the SRC log describes what triggers substitution in the old code, not a narrower refusal trigger.
- The early return does NOT leak the pill: run()'s finally block releases the overlay on every path including the refusal return (first_action.py, finally block after the try).
- Key-only batches that need no coordinates (Escape, Ctrl+Tab) are refused on a stale observation, but they also failed before the fix (desktop_act refuses key on screen scope), so this is a louder failure, not a new one.

## Type-verification false-fail hunt: no strong live false-fail constructed

Plausible classes, mechanism-level only: text lands outside the captured region (input below the fold, covered by a popup), text lands but renders pixel-identical (trailing whitespace, combining-only input), or the skip paths in R10 (type_verified absent, ok True). I did not demonstrate a live false-fail; the false-pass in R1 is the demonstrated defect, and it is the dangerous direction for this incident (a "verified" stamp on a failed send).

## ime_state_trace surfacing: verified clean, no finding

- Contents are phase/state/state_source/status only, 'im' always None, no typed text, no window titles, no PII (cu.py literal_keyboard, 1161-1260; TraceContracts tests). Bounded in practice (3 entries per keyboard group, at most 32 actions). first_action copies it only when it is a list, on session and fallback paths alike (first_action.py:514-520, 576-578). No leak, no envelope breakage found.

## What the fix gets right (verified, not just unattacked)

- G28 loud refusal for key/type batches works as specified, with the batch-2 114s case tested exactly (test_first_action.py).
- zen_dom TimeoutError/OSError/URLError conversion works for the F3b hang case; per-handle scan catch works; tab_at targets without scanning (2 POSTs: target, restore).
- Type verification correctly does not apply to key-only or pointer-only batches, does not mask execution errors (error path skips verification), sets next_step DESKTOP_REOBSERVE, and does not count as a completed-capture success (no capture_error is set, and _is_completed_capture requires one).
- 139 tests pass (test_first_action, test_type_verification, test_zen_dom, test_keyboard_preflight).

## Verdict: AMEND

Required fixes before this diff can be presented as closing the silent type failure:
- R1: redesign type verification to check the typed text or the input region, not the whole pre/post frame hash; correct the fix-log Stage A claim; add a click+type test with a frame changed by the click only.
- R2: surface the pointer-only substitution top-level (fallback_reason or equivalent flag); do not leave ok True with fallback_reason None on a substituted observation.
- R3: copy type_verified and error_code into the act-now envelope on both paths.
- R4: reword the refusal message so the screen-coordinates remedy is not offered on the key/type path.
- R5: convert JSON decode and HTTPException escapes in zen_dom _wd into ZenDomError, or correct the "never raw" docstring.
- R6: surface tab restore failures instead of swallowing them.
- R7: stop the full tab scan after the first hang (or add a scan budget).
- R8: verify the switched tab in tab_at, or downgrade the handle-order claim.
- R9: scope the G28 docstrings to key/type batches.
- R10 is noted, no change demanded.

Not BLOCK because nothing that worked before regresses (no production caller of list_tabs breaks; 139 tests pass; the G28, zen_dom TimeoutError, and ime surfacing fixes work), and the type check is a strict improvement for type-only batches on a static screen. But the diff as landed does NOT fix the incident shape it was built for (R1), and its type_verified stamp will mislead on exactly that shape, so it must not be claimed as the fix for the silent-send failure until R1 lands.
