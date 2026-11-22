# Worker C5-ITEMS56 log: diagnose the Codex live-confirm AMEND4 items 5-6 FAIL

Role: independent diagnosis of the Codex live-confirm failure. Codex ran
the confirmation; I diagnose its failure. No code changes in this task.
Report to the COORD-CLICK-5 coordinator only, never message the user.
Owner asleep since 06:52 with a headache; Muse holds full authority.

Standing rules: wall-clock Asia/Ho_Chi_Minh plus elapsed time on every
log entry. No em dash (U+2014) or en dash (U+2013) anywhere. No personal
info on GitHub. Commit with explicit pathspec only, immediately after
staging, never plain git commit, never git add -A. Verify every push
with git ls-remote. Never ydotool.

Task start: 2026-11-22 10:42:28 +07 (T+0m).

## 0. Primary sources read (T+0m to T+8m)

- Codex log, read in full: `git show
  origin/live-confirm-codex:improvements/worker-codex-live-confirm-log.md`
  (commit b57f499, 118 lines). Verdicts: F1 sanitization PASS, item 8
  URL/email trimming PASS, AMEND4 items 5-6 origin re-read FAIL.
- Source at 6614c3a, read in full for the three stage modules:
  scripts/zen_dom.py (1216 lines), scripts/dom_act.py (634 lines),
  scripts/fastpath.py (272 lines).
- Probe script, read verbatim from the laptop:
  /tmp/click4-live-confirm-probe.py, SHA-256
  efb016ed8ae84d80515a90855422a7f8e71fc965229cddc0f0cf8ea8bf5e0b3d,
  matching the SHA in the Codex log. It still exists on the laptop.
- Landing commit b44a5ea, diff read in full (309 lines). b44a5ea is an
  ancestor of 6614c3a (verified with git merge-base --is-ancestor).
- Executed-source check: SHA-256 of scripts/zen_dom.py,
  scripts/dom_act.py, scripts/fastpath.py, scripts/cdp.mjs at 6614c3a
  matches the executed SHAs recorded in the Codex log exactly
  (zen_dom 07580eb6..., dom_act d7c9bffe..., fastpath 1122ddd5...,
  cdp.mjs 6725891d...). The code that failed is the code at 6614c3a.
  No source drift between the log and the worktree.

## 1. What the Codex probe actually ran in the origin stage

The coordinator brief said the stage was to run
dom_act._check_window_not_moved, then ZenSession.viewport_origin, then
fastpath.dom_rect_to_screen_point. The probe script shows one more call
first, and a monkeypatch the brief does not mention. Verbatim order in
the probe (stage 'origin_reread', started 09:20:25 +07 at 0.121s,
stopped 0.130s, total stage 0.009s):

1. `rect = session.locate('#lc4-text')` (scratch input in the fixed host
   div on the pre-existing about:blank tab). Outside the monkeypatched
   block. If it returns None the probe raises RuntimeError
   ('scratch_rect_missing'); if its evaluate fails it raises
   ZenDomError via _wd.
2. `meta` built from the FRESH hyprctl capture taken at 0.025s:
   `{'window': <address>, 'window_bounds': [2509, 914, 925, 1176],
   'monitor_box': [2464, 902, 1920, 1200]}`. The meta's window origin
   and size are the LIVE values, not a stale observation.
3. `zen_dom.subprocess.run` monkeypatched with `record_run`, which
   records every `hyprctl -j clients` call (matching-window count and
   live origin) and delegates to the original run.
4. `dom_act._check_window_not_moved(session, meta, [2509, 914])`.
5. `session.viewport_origin([2509, 914], [925, 1176], [2464, 902, 1920, 1200])`.
6. `fastpath.dom_rect_to_screen_point(rect, computed_origin, factor)`
   with factor = session.last_scale_factor.

The harness recorded only `harness_error = {'stage': 'origin_reread',
'type': 'ZenDomError'}`. The exception MESSAGE and traceback were
discarded, and `origin_reads`, `moz_inner`, `inner_size`,
`computed_absolute_viewport_origin`, and the fastpath point are only
written to the output on success, so none of them survived the
failure. That is procedure defect P1 below: the single most
diagnostic value (the message) was thrown away by the probe.

Live window record from the Codex run (hyprctl -j clients, 0.025s):
address 0x557052b62dd0, origin [2509, 914], size [925, 1176],
monitor_box [2464, 902, 1920, 1200]. Verified still current at
10:47:15 +07 (same address, same origin, same size, workspace 1):
the window has not moved since the Codex run.

## 2. Raise-site inventory at 6614c3a (source alone)

### 2a. dom_act._check_window_not_moved: CANNOT raise ZenDomError

- scripts/dom_act.py:99-113. Its only raise is line 109, a
  DomActError ('window moved since the observation'), raised only when
  the live re-read returns a non-None origin different from the meta
  origin.
- Its helper _live_window_origin (dom_act.py:73-97) NEVER raises: the
  session call sits inside try/except Exception returning None, and a
  non-callable or malformed result also yields None. The caller then
  skips the check.
- The session method it calls, ZenSession.live_window_origin
  (zen_dom.py:741-785), NEVER raises either: the whole body is inside
  try/except Exception returning None (hyprctl missing, window not
  found, unparsable output all yield None).
- The probe's monkeypatched record_run can raise inside
  live_window_origin (json.loads on bad hyprctl stdout), but that
  raise is swallowed by the same blanket except and yields None.
- CONCLUSION: call 4 in section 1 is EXCLUDED as the raise site by
  the recorded exception type. If it had refused, the type would be
  DomActError. It either passed (live [2509, 914] equals meta
  [2509, 914]) or was skipped (live None). Either way it did not
  raise the recorded ZenDomError.

### 2b. fastpath.dom_rect_to_screen_point: CANNOT raise ZenDomError

- scripts/fastpath.py:152-180. Its only raises are ValueError:
  line 173 ('viewport_origin must be two numbers [x, y]') and
  line 177 ('scale_factor must be a positive number'), plus ValueError
  from _rect_center_float (lines 141-148) for a non-numeric or
  non-positive rect.
- CONCLUSION: call 6 in section 1 is EXCLUDED by the recorded type.
  A fastpath failure would have been recorded as ValueError.

### 2c. ZenSession.viewport_origin: CAN raise ZenDomError, 12 sites

- scripts/zen_dom.py:668-740. Raise sites, in execution order:
  1. Line 693: window_origin is None ('viewport_origin needs the
     Hyprland window origin'). NOT APPLICABLE: the probe passed
     [2509, 914].
  2. Lines 415/421/424 via self.evaluate -> _wd (zen_dom.py:393-427):
     malformed WebDriver response (no 'value' member), HTTP error on
     the execute/sync call, transport failure (timeout, OSError,
     URLError, HTTPException, JSON decode). A 10s-timeout hang is
     EXCLUDED by the 9ms stage time; a fast HTTP error (e.g. a
     javascript error from the evaluate script) is possible but has
     no deterministic mechanism here, and the same session's
     evaluates succeeded immediately before (item 8 ended 0.121s)
     and immediately after (cleanup scratch removal and tab restore
     both succeeded).
  3. Line 709: the 9-number read is malformed ('viewport origin read
     is not nine numbers'). Requires a None/bool/non-number in the
     moz/DPR/inner/outer slots (index 3, screenPixelsPerCSSPixel,
     is exempt). No deterministic mechanism on a live about:blank
     tab: innerWidth/innerHeight/outerWidth/outerHeight/DPR are
     always numbers there.
  4. check_viewport_geometry (zen_dom.py:104-213), called at line
     734-736 with factor from the same read:
     - Line 149: a pair is not two numbers. NOT APPLICABLE: all
       inputs are numbers by construction (window origin/size from
       hyprctl ints, absolute computed from numbers, inner from JS
       numbers).
     - Line 154: factor required (F10). Requires BOTH
       screenPixelsPerCSSPixel invalid AND devicePixelRatio invalid.
       The C12 probe measured both as 1 on this Zen; no mechanism
       for both to fail at once on about:blank.
     - Line 165: mozInnerScreen negative. Requires a negative live
       moz pair. No mechanism for a window fully on-monitor at
       [2509, 914].
     - Line 167: window/inner size non-positive. Requires innerWidth
       or innerHeight <= 0, or a non-positive passed window size.
       The passed size [925, 1176] is positive; a live inner size
       of 0 would need a zero-area viewport.
     - Line 172: DIMENSION CLOSURE FAILS (moz + inner exceeds window
       size, right_gap < 0 or bottom_gap < 0). This is the only
       geometry check with a live-data-dependent failure mode that
       does not need an insane value: it fails when the live
       mozInner + inner size exceeds the passed window size on
       either axis. With the C12 chrome layout (sidebar ~240, right
       gap ~8, top gap ~8) the live numbers would be moz (240, 8),
       inner (677, 1160) for a 925x1176 window, gap 8 on both axes,
       PASS. Closure fails only if the live layout at 09:20 did
       not fit the live window (viewport sticking past the window
       edge), which the probe's lost metrics cannot confirm or
       refute from the log alone.
     - Line 181: exactness (absolute != window + moz*factor).
       UNREACHABLE from viewport_origin: absolute is computed by
       exactly that formula two lines earlier, so the check is
       tautological for this caller.
     - Line 188: absolute outside the window rect. UNREACHABLE when
       closure holds (closure implies containment at factor >= 1
       for non-negative moz); reachable only together with a
       closure failure.
     - Line 199: monitor_box shape. NOT APPLICABLE: the probe passed
       [2464, 902, 1920, 1200].
     - Line 204: absolute outside the monitor box. Requires absolute
       outside [2464, 902, 1920, 1200]; with window origin
       [2509, 914] and any sane moz (a few hundred px) the absolute
       origin is ~(2749, 922), inside. Reachable only with a wild
       moz value.
- CONCLUSION: viewport_origin is a live candidate. Within it, the
  only deterministic (non-transient) failure mode is the dimension
  closure check at line 172; the evaluate-failure modes need a
  transient Marionette fault with no deterministic mechanism.

### 2d. ZenSession.locate: CAN raise ZenDomError (the omitted call)

- scripts/zen_dom.py:573-592. locate() runs one evaluate of the
  _FIND_JS traversal (pierce open shadow roots, then same-origin
  frames to depth 5) plus getBoundingClientRect, and returns the rect
  or None. Its only ZenDomError path is the evaluate -> _wd raises
  (lines 415/421/424): a transport failure, an HTTP error (the JS
  throwing), or a malformed response. A None return would have been
  recorded as RuntimeError ('scratch_rect_missing'), not ZenDomError,
  so locate either returned a rect or raised ZenDomError.
- The traversal JS is the FIRST use of the AMEND4 item 2 find()
  helper in this probe run (F1/item 8 used plain querySelector
  evaluates). No deterministic throw is visible in the script for a
  plain input in a fixed host div on about:blank, but unlike the
  other calls it had never been exercised in this session before
  the origin stage.
- CONCLUSION: locate is the second live candidate, via a transient
  evaluate failure only. No deterministic mechanism is visible in
  the source.

### 2e. Timing cross-check (9ms stage)

- Per-evaluate cost in this same session, from the Codex time log:
  F1 baseline 0.068-0.081s for 4 evaluates (~3ms each); item 8
  0.102-0.121s for 8 evaluates (~2.4ms each). One hyprctl -j
  clients call costs roughly 2-4ms.
- Call sequence cost if the failure is in viewport_origin's
  geometry check: locate (~3ms) + hyprctl re-read (~3ms) +
  viewport_origin evaluate (~3ms) = ~9ms, matching the observed
  0.121-0.130s exactly.
- If the failure were in locate, the stage would have ended after
  ~3ms (about 0.124s), not 0.130s. Timing therefore FAVORS a
  viewport_origin failure over a locate failure, but evaluate
  latency varies by a few ms, so this is suggestive, not proof.

## 3. Narrowed verdict from source alone (T+8m)

- EXCLUDED by exception type: _check_window_not_moved (DomActError
  only) and fastpath.dom_rect_to_screen_point (ValueError only).
- REMAINING: session.locate('#lc4-text') or
  session.viewport_origin([2509, 914], [925, 1176], [2464, 902,
  1920, 1200]).
- LEADING HYPOTHESIS: viewport_origin's dimension closure check
  (zen_dom.py:172), on live numbers the log did not preserve. The
  timing fits, the mechanism is deterministic, and it is the only
  check in the stage that can fail on plausible-but-unrecorded live
  geometry. ALTERNATIVE: a transient Marionette evaluate fault in
  locate or in viewport_origin's own read, which no log evidence can
  confirm or refute.
- The source analysis does NOT pin the raise site. One live
  diagnostic is required (section 5). UPDATE after the diagnostic
  (section 5a/6): the site IS pinned, viewport_origin ->
  check_viewport_geometry line 172, dimension closure, and the
  source-only leading hypothesis in this section was correct.

## 4. Procedure defects found in the Codex probe (not code defects)

- P1: the harness records only {'stage', 'type'} for the failure
  and drops str(exc) and the traceback. The message names the exact
  check ('dimension closure fails: ...' vs 'transport failure ...'
  vs 'not nine numbers'), which would have pinned the site without
  any re-run. Every future live-confirm harness must record the
  message.
- P2: origin_reads, moz_inner, inner_size, outer_size,
  computed_absolute_viewport_origin, and the fastpath point are
  only written to the output on success. On failure the evidence
  that would decide the geometry question is lost, even though
  session.last_display_metrics IS set before the geometry check
  inside viewport_origin and survives a failure. Evidence must be
  emitted on the failure path too.
- P3 (minor): the coordinator brief's stage description omits the
  session.locate call that runs first in the stage, and the
  monkeypatched record_run. A diagnosis from the brief alone would
  miss a candidate call.

## 5. Live diagnostic (ONE run, gated on C5-VISIBILITY)

- Gate: run ONLY after the C5-VISIBILITY worker's log commit
  (improvements/worker-click5-visibility-log.md) exists on
  origin/todolist-push. That worker switches workspaces on the same
  laptop; my diagnostic reads Zen geometry and viewport metrics on
  ws1 and must not run while ws2 is focused. RESOLVED 10:54 +07:
  the visibility log commit exists, a9511de (255 lines, committed
  10:52:08 +07). Its last workspace switch back to ws1 was
  10:45:32-10:45:53; live check at 10:54:32 +07 confirmed ws1
  active and the Zen window unchanged at [2509, 914] [925, 1176].
  (The visibility log carries no explicit "ws1 restored"
  final-state line; the live workspace check is the confirmation.)
  Gate checks before resolution: 10:47, 10:48, 10:49, 10:50 +07,
  no visibility log commit; origin todolist-push HEAD then was
  5127ce5, later 4e3b42d.
- Diagnostic script: ~/workspace/c5-items56-probe.py, SHA-256
  8eb04d1ef24d1bfe6c850a624b5a82d817ab5f025d052a50214d85795ff0b29a,
  parses OK. Copied to the laptop as /tmp/click5-items56-probe.py,
  SHA verified identical after the copy. It mirrors the probe's
  origin stage call for call on a pre-existing about:blank Zen tab
  with scratch fields only, but runs each of the four calls
  independently and records per call: ok value or type + message +
  traceback, plus origin_reads and session.last_display_metrics /
  last_scale_factor even on failure. No real thread, no
  submission, no click, no Brave, no Chromium endpoint, no
  workspace switch.
- Worktree state for the run: /tmp/click4-live-confirm HEAD is
  b57f499 (the Codex log commit), not 6614c3a, but the on-disk
  scripts are byte-identical to the Codex executed SHAs (verified
  before the run: zen_dom 07580eb6..., dom_act d7c9bffe...,
  fastpath 1122ddd5..., cdp.mjs 6725891d...). b57f499 only adds the
  log file. Clean tree. The diagnostic therefore ran the same code
  the Codex probe ran.

## 5a. Diagnostic result (ONE run, 2026-11-22 10:55:04-10:55:08 +07)

Test command: `timeout 25s python3 /tmp/click5-items56-probe.py`
(exit status 1, elapsed 0.079s, run start 10:55:04 +07, end
10:55:08 +07). Verdict FAIL, reproduced deterministically.

Per-call results (from the run JSON):

- locate('#c5-text'): OK, 1.9ms. Rect {x: 12, y: 12, width: 420,
  height: 28, center_x: 222, center_y: 26}. EXONERATED.
- dom_act._check_window_not_moved: OK, 3.8ms. origin_reads has 1
  entry, matching_windows 1, live_origin [2509, 914] equals the meta
  origin. EXONERATED.
- ZenSession.viewport_origin: FAIL, 3.5ms. ZenDomError with message:
  "dimension closure fails: mozInner [274, 66] + inner [677, 1160]
  exceeds window size [925, 1176] (gaps -26, -50); the viewport
  origin cannot be window-relative with these numbers". Traceback
  pins zen_dom.py:172 in check_viewport_geometry, called from
  viewport_origin line 737. THIS IS THE RAISE SITE.
- fastpath.dom_rect_to_screen_point: skipped (no computed origin to
  convert). Never ran.
- Live metrics captured on the failure path:
  session.last_display_metrics = {moz_inner: [274, 66], inner_size:
  [677, 1160], outer_size: [925, 1176], device_pixel_ratio: 1,
  screen_pixels_per_css_pixel: null, zoom: 1};
  session.last_scale_factor = 1. (screenPixelsPerCSSPixel null is
  why the factor fell back to DPR 1; the null itself is normal on
  this Zen and is not the failure.)
- Cleanup: scratch_removed true, original_tab_restored true,
  session_closed true. Scratch tab index 9. Active window during
  the run: Brave (ws1 active, as after the visibility restore).

Arithmetic: right_gap = 925 - 677 - 274 = -26; bottom_gap =
1176 - 1160 - 66 = -50. Both negative, so the closure check at
zen_dom.py:172 raised.

Timing cross-check, now quantitative: per-call times sum to
1.9 + 3.8 + 3.5 = 9.2ms, matching the Codex stage time of 9ms
(0.121-0.130s). A locate failure would have ended the Codex stage
after about 2ms; a _check failure would have been DomActError.
The Codex failure was in viewport_origin.

Comparison with the C12 probe (03:36, same window address
0x557052b62dd0, same origin [2509, 914], size 1863x1176): moz
(240, 8), inner (1615, 1160), outer (1863, 1176), gaps +8/+8,
PASS. Since then the window narrowed 1863 to 925 wide (innerWidth
tracked the shrink exactly: 1615 - 938 = 677), innerHeight stayed
1160, but moz grew +34 in x and +58 in y. The viewport SIZE
matches the old chrome (240, 8); the viewport POSITION matches
new chrome (274, 66). Position and size now describe different
chrome states, and they disagree by exactly the negative gaps
(-26, -50). Which Zen UI element grew the chrome (sidebar strip,
top bar, or other) is NOT identified by this diagnostic; the
numbers prove the inconsistency, not the element.

## 6. Verdict

- WHICH CALL RAISED: ZenSession.viewport_origin, via
  check_viewport_geometry dimension closure (scripts/zen_dom.py:172,
  called from viewport_origin line 737). PINNED by live reproduction
  with the exception message and traceback.
- WHY (mechanism): the live Firefox reports mozInner (274, 66) plus
  inner size (677, 1160) against a window size of (925, 1176). The
  validator requires moz + inner <= window size on both axes (gaps
  >= 0). The live numbers exceed on both axes (gaps -26, -50), so
  the validator refuses to return the origin it already computed
  internally, (2509 + 274, 914 + 66) = (2783, 980). The browser is
  stably in this state: the same window geometry failed the same
  way 95 minutes apart (09:20 Codex run, 10:55 this diagnostic).
- ATTRIBUTION TO 09:20: HIGH confidence the Codex failure was this
  same closure failure: same code (SHAs verified identical), same
  window geometry, same stage, same exception type, same 9ms timing
  (per-call sum 9.2ms), deterministic reproduction. Not absolute
  proof, because the 09:20 message was discarded (defect P1).
- CODE OR ENVIRONMENT OR PROCEDURE: code defect AND environment
  trigger; NOT a live-confirm procedure defect.
  - CODE: the defect is NOT in the items 5-6 landing (b44a5ea).
    Its code behaved correctly live: _check_window_not_moved
    passed (live origin equals meta origin) and window_bounds was
    present and used. The defect is in the PRE-EXISTING geometry
    validator, check_viewport_geometry (zen_dom.py:104-213, from
    the C12 / AMEND4-item-1 work): its dimension-closure model
    (the viewport must fit inside the window with non-negative
    gaps) is false for the current live Zen state. Firefox
    genuinely reports a viewport extending 26px past the window's
    right edge and 50px past its bottom edge while reporting the
    window itself as 925x1176 (outerWidth agrees). A validator
    that refuses a real, stable browser state is a code defect.
  - ENVIRONMENT: Zen's chrome state changed between the C12 probe
    (03:36, moz (240, 8), PASS) and the Codex run (09:20, FAIL):
    the window narrowed 1863 to 925 wide and moz grew to (274, 66).
    The validator was proven only against the old chrome state and
    never re-checked against the new one.
  - PROCEDURE: the live-confirm run was conducted correctly
    (fresh live hyprctl meta, correct call order, stop after the
    first failure per rule, scratch-only, cleanup true). Defects
    P1/P2 hampered diagnosis only; they did not cause the failure.

## 7. Fix shape

- FILE: scripts/zen_dom.py, functions check_viewport_geometry
  (lines 104-213) and viewport_origin (lines 668-740). NO change
  is needed in scripts/dom_act.py (the items 5-6 landing) or in
  scripts/fastpath.py.
- WHAT MUST CHANGE: the closure model must account for the real
  chrome state instead of refusing it. The fixer must first
  identify WHY moz grew: read moz/inner/outer while toggling Zen
  UI states (sidebar strip, top bar, bookmarks toolbar) and compare
  a plain tab against the scratch tab, to find which element moved
  moz from (240, 8) to (274, 66) without shrinking the viewport.
  Then EITHER (a) correct the model so the validator compares
  against the right quantities (for example derive the expected
  gaps from outerWidth/outerHeight and the actual chrome, or accept
  the overflow when the computed origin independently verifies),
  OR (b) replace the hard closure refusal with a verified-origin
  path: compute the absolute origin and verify it against an
  independent instrument (screenshot pixel edges of a known
  element, as the C12 probe did with its one real click; AT-SPI
  cannot see Zen) before trusting it. The fix must NOT simply
  delete the closure check: the check is the guard that catches
  factor-forgotten origins (F9/F10), so any relaxation needs a
  replacement guard that still refuses a factor error.
- Do NOT fix it by changing the live window (resizing Zen back to
  1863 wide or hiding chrome). That would mask the defect; the
  validator must handle the window as it is.
- EVIDENCE THAT WOULD PROVE THE FIX: (1) the origin stage re-run
  live on THIS window (same address 0x557052b62dd0, same geometry
  [2509, 914] [925, 1176]) returns PASS with computed origin
  (2783, 980) and the fastpath point, with the message and metrics
  emitted on both the success and failure paths; (2) an independent
  cross-check of the computed origin (screenshot pixel edges or one
  real click, C12-style) confirming the rect center maps to the
  true screen position; (3) the existing unit tests still catch
  F9/F10 (a factor-forgotten origin is still refused), with the
  validator regression suite passing unchanged in strength; (4) the
  C12-state geometry (moz (240, 8), inner (1615, 1160), window 1863)
  still passes.

## 8. Blocking statement

- STEP 7 P2/A9: BLOCKED. A9 converts CSS px rects to screen points
  using the absolute viewport origin from viewport_origin, and
  viewport_origin raises ZenDomError on the live Zen window in its
  current state, so the A9 conversion chain cannot run live at all.
  No P2/A9 live verification can pass on this window until the
  validator is fixed. Unit and fake tests are unaffected; the block
  is live-only. The failure is window-state-dependent (the C12
  state passed, the current state fails), so a fix validated only
  on a different window state does not count; validation must be
  on this window, address, and geometry.
- B5 LIMB (ii) JUDGMENT: NOT blocked. That limb is about whether
  the five defective RT2 proof tests (F2, F3, F4, F5-behavior, F6)
  were repaired or re-verified; C5-B5-VERIFY judged it MET on
  todolist-push (commit 3724f52), and this diagnosis exonerates
  the items 5-6 landing code itself. BUT the limb's purpose
  (confidence that items 5-6 are correct) does not cover this
  failure: the live defect is in the shared validator the items
  5-6 code depends on, not in the landing or its tests. Step 7
  therefore carries a separate live-blocker that B5 limb (ii) does
  not dispose of. The coordinator should track the validator
  closure defect as its own open item; it must be fixed (or the
  window state understood and the validator corrected) before
  step 7 live work proceeds.

## 9. Completion

- Diagnostic run finished 10:55:08 +07; log completed 10:58 +07.
  Total task elapsed about 16 minutes from 10:42:28 +07.
  No code changed. No retry of the full live-confirm suite. No
  chat thread, Brave, or Chromium clone2 endpoint touched. One live
  diagnostic run only, after the visibility gate opened.
  Diagnostic script copies: VM ~/workspace/c5-items56-probe.py and
  laptop /tmp/click5-items56-probe.py, both SHA-256
  8eb04d1ef24d1bfe6c850a624b5a82d817ab5f025d052a50214d85795ff0b29a.
