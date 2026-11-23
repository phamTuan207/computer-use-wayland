# AMEND4 reconciliation log (worker RECONCILE-AMEND4)

Worker RECONCILE-AMEND4, independent reconciliation worker for
coordinator COORD-CLICK-3. Owner: the owner (repo-facing name).
Branch: todolist-push. Task received 08:12 22/11/2026 Asia/Ho_Chi_Minh.
All times below are Asia/Ho_Chi_Minh wall clock unless noted.
Elapsed: 08:12 to about 08:30, about 18 minutes of wall time plus two
full-discover runs (VM 208s, Codex 129s).

## Scope and method

Reconcile the TWO independent AMEND4 implementations at their FINAL
states, not mid-repair snapshots. Base: f0ddd41 (round-2 redteam, 13
findings F1-F13, 15 proof tests in tests/test_click3_redteam2.py).

- VM lane: branch todolist-push, HEAD 77c72be (remote HEAD verified
  08:12 by ls-remote: 77c72be38f4473d470fadde7bbbb5344f8931504). The VM
  AMEND4-only endpoint is 0668327 (item-4 follow-up, last AMEND4 fix
  commit); later work on top is S0-IMPL 18f2304, DOMZEN-FIX 5dcf2b31,
  Y1B-RPC fd63a7d, TEST-REPAIR 43b27a1..77c72be. Per-item comparison
  uses f0ddd41..0668327 for the VM AMEND4 fix and f0ddd41..06a34e8 for
  Codex; the final-state comparison uses 77c72be vs 06a34e8.
- Codex lane: branch amend4-codex, HEAD 06a34e8 (remote HEAD verified
  08:12 by ls-remote: 06a34e8610a9467c3884f6dd7a567293c747da45; laptop
  worktree ~/workspace/cu-amend4-codex verified at 06a34e8
  with a clean status). Read-only: no file in the Codex lane was
  modified. Its tests were run via SSH on the laptop worktree only.
  Two probe scripts were written to /tmp on the laptop
  (/tmp/relay_probe.py, /tmp/band_probe.py), outside the worktree.

Worktrees (clean, pinned HEADs; the dirty shared checkout was never
used as a base): /tmp/reconcile-vm-head at 77c72be,
/tmp/reconcile-vm-amend4 at 0668327, /tmp/reconcile-codex at 06a34e8.
The stale .git/rebase-merge dir and the staged changes in the shared
checkout (tests/test_click3_redteam2.py, tests/test_zen_dom.py) were
left untouched, per the task constraints.

Sources read in full: improvements/worker-click3-amend4-log.md
(VM AMEND4, 6f54a4e), improvements/worker-click3-testrepair-log.md
(TEST-REPAIR, 77c72be), the Codex AMEND4 log at
06a34e8:improvements/worker-codex-amend4-log.md, and the per-file
diffs f0ddd41..0668327 and f0ddd41..06a34e8 for scripts/cu.py,
scripts/dom_act.py, scripts/zen_dom.py, scripts/first_action.py,
scripts/cdp.mjs and the test files.

Standing rules honored: full access, no em dash (U+2014) or en dash
(U+2013) anywhere in this file (grep-checked after writing), never
ydotool, no personal info in repo files (owner name the owner only),
log everything with wall-clock + elapsed, explicit pathspec commits,
never plain git commit, never git add -A, every push verified with
git ls-remote. No fabrication: every claim below cites a diff, a line
number, or a test run I performed myself, except where explicitly
marked as taken from another worker's log.

Worktree lesson (recorded because it polluted my first numbers): a
fresh `git worktree add` contains only tracked files, so it lacks the
untracked build artifacts the suites need (native/pointer,
native/wtype, and the generated native/keyboard-protocol.c/.h and
native/pointer-protocol.c/.h, which exist in the main checkout but
are not in git). My first VM RT2 run in the fresh worktree showed
Ran 51 FAILED (errors=41), all inherited DesktopPreflight tests
erroring for the missing helpers; my first VM full discover showed
Ran 1951, failures=2, errors=5 including a test_wtype_native
setUpClass cc error for the missing keyboard-protocol.c. Copying
those artifacts in (the same step TEST-REPAIR took) fixed both, and
the final numbers below come from the fixed worktree. A clean
discover from a fresh worktree MUST copy the untracked native
artifacts first, or the numbers are environmental, not HEAD evidence.

## Per-item table (12 items)

"VM" is the VM AMEND4 fix at 0668327 unless "head" is noted.
"Codex" is the Codex fix at 06a34e8. "Verdict" is the reconciliation
verdict for the item: SAME means the same fix in substance (wording
or helper shape may differ); DIFFERENT means a different mechanism
with the same or a different outcome, judged in the row.

| # | Item (findings) | VM fix | Codex fix | Same / different | Verdict |
| --- | --- | --- | --- | --- | --- |
| 1 | Geometry (F9/F10) | check_viewport_geometry gains factor=None, REQUIRED (raises when absent, fail-closed); exactness check absolute == window + moz*factor within 0.5 px; containment in screen px (size*factor). viewport_origin passes size as-is in BOTH branches and passes factor. (cc964b2) | check_viewport_geometry gains scale_factor=1 (DEFAULT 1, silent when absent); exactness within 1e-6; containment via relative_css = (absolute - window)/factor; plus a new integer-size requirement (window size must use integer logical/CSS px). viewport_origin passes size as-is and passes scale_factor=factor. (ddf5673) | DIFFERENT in the factor contract; SAME outcome on F9/F10 (both pass) | SAME outcome. Prefer the VM shape: Codex's default-1 re-admits the F10 hole at the API level (a caller that forgets the factor silently gets factor-1 behavior). All current callers pass the factor on both lanes, so the difference is latent, not live. |
| 2 | Gate traversal (F8/F11/F12/F13) | Shared _FIND_JS (pierce + framesOf, depth cap 5, frames by contentWindow presence, cross-origin fail-closed) returning one element; separate _DEEP_ACTIVE_JS and _FRAME_POINT_JS; all helpers (locate, hit_check, focus_check, field_value, verify_typed, arm_typed_flag, sent_bubble_contains, harvest) use it. Added 2 faithful-shim node tests in test_zen_dom.py. (c1ea773) | Shared _FIND_JS returning an ARRAY of {element, doc, offsetX, offsetY, scaleX, scaleY} with frame offsets and scaling, depth 32, seen-set; all helpers use it; harvest uses the offsets for nested-frame rects instead of a framePoint walk. No faithful-shim tests added (its R7 run is the frozen 3 tests). (fee4a29) | DIFFERENT implementation; SAME outcome (F8/F11/F12/F13 + R7 pass on both) | SAME outcome. Codex's offset-carrying find is the more complete nested-frame shape; the VM single-element find plus framePoint walk is simpler and equally proven by the same tests. Either is acceptable; no merge action needed. |
| 3 | Band anchor (F4) | _input_line_changed gains y_range (field y-range when given, else symmetric anchor +- 12); grounded_y_range mirrors grounded_x_range; type_y_ranges threaded in item 4. The original RT2 test left failing (symmetry proof). TEST-REPAIR repaired it with y_range=(100, 120). (62b740e, 43b27a1) | _input_line_changed gains y_range AND an asymmetric fallback band [anchor-12, anchor+1) when no y_range is given, plus an anchor_x +-6/7 neighborhood when no x_range is given. Passes the ORIGINAL F4 test with no y_range. (199b10a) | DIFFERENT | KEEP VM. See F4 decision below. |
| 4 | Range wiring (F5) | type_x_ranges AND type_y_ranges threaded through CLI act, CodeExecBackend.act (best-effort grounding), and the first_action fallback. Band-only verification WITHOUT ranges still verifies (documented empty-field contract kept). The original F5 behavior test left failing (direct desktop_act call, threading cannot affect it). TEST-REPAIR rewrote it in two halves (wiring spy + direct call with the spied ranges). (72120aa, 0668327, 43b27a1) | Ranges threaded via a grounded_type_ranges helper through CodeExecBackend.act, CLI act, and the first_action fallback, PLUS require_type_ranges=True on all three, PLUS the narrowed fallback band from item 3. desktop_act sets verified=False, basis 'unscoped-input-band', when any paired group lacks an x or y range. Passes the ORIGINAL F5 behavior test. (9975660) | DIFFERENT | KEEP VM. See F5 decision below. |
| 5 | Region fallback (F2) | _window_origin requires window_bounds (raises DomActError, region fallback removed); locate_point also requires window_bounds; fixtures gained window_bounds. The original F2 test left failing (errors with the refusal, no assertRaises). TEST-REPAIR replaced the ground call with assertRaises. (b44a5ea, 43b27a1) | _window_origin requires window_bounds (same refusal, region fallback removed); locate_point also requires window_bounds. The original F2 test still ERRORS on this lane (DomActError, no assertRaises). (96ea721, 81963fa) | SAME outcome (refuse), minor wording differences in the error text | SAME. Both lanes refuse region-only grounding; both leave the original F2 test erroring as written. |
| 6 | Stale origin (F3) | ZenSession.live_window_origin (hyprctl clients -j by address, fallback activewindow -j; returns None when hyprctl is unavailable, never raises) + _check_window_not_moved in ground_input and ground_many_one_shot: refuse on origin mismatch, SKIP the check when live is None. The original F3 test left failing (contradictory assertions, 1271 px apart). TEST-REPAIR split it (stale-value documentation + ground-time refusal test). (b44a5ea, 43b27a1) | assert_window_origin_current(meta) in zen_dom.py, called from ground_input, ground_many_one_shot, and locate_point: re-reads via cu.window/cu.bounds, compares the FULL 4-value bounds, raises ZenDomError when unreadable or changed; returns silently when scope != 'window'. The original F3 test still FAILS on this lane (1271 px assertion). (d8136dc) | DIFFERENT mechanism; SAME outcome on the proof test (refusal) | DIFFERENT, both acceptable, with a trade-off. Codex is fail-closed on unreadable (stricter) and compares full bounds (stricter than origin-only), but it fails closed on any environment without hyprctl (it would refuse grounding on this VM) and skips non-window scope silently. VM degrades gracefully (skip when unreadable). Recommend the VM shape for portability; Codex's full-bounds compare is a possible hardening, not a required one. |
| 7 | Typed flag (F6/F7) | AMEND4: window.__agentCuTyped REMOVED entirely; closure + locked getter '__agentCuTypedValue' (fixed name) on the element; re-arm trust branch returns True when a non-configurable getter exists; typed_flag requires last-trusted == current value. (49081aa) TEST-REPAIR C7 at head: per-arm unpredictable name '__agentCuTypedValue_' + secrets.token_hex(8), recorded in session._typed_flag_props[selector]; re-arm trust branch DELETED; typed_flag returns False when never armed on this session; pre-locked-getter test added. (ee883bc) | Closure-backed recorder: frozen object '__agentCuTypedRecorder' on the element (read/reset, non-writable, non-configurable); arm re-arms by reset() when a frozen recorder exists, else returns False; the legacy window.__agentCuTyped map is KEPT (inert, never trusted) and window.__agentCuMutated is kept; verify_typed JS returns null unless trusted.value === current value (flag-gated verify); typed_flag only checks recorder.read() is non-null (does NOT compare the value). (b9fb33a) | DIFFERENT | KEEP VM (head form). See F6 decision below. |
| 8 | set_value (F1) | cdp.mjs read-back compares against the SANITIZED form (char codes via String.fromCharCode, no regex escapes); input strips CR/LF, textarea normalizes CRLF/CR to LF; maxLength pre-check still used the RAW length at AMEND4 (fixed at head by TEST-REPAIR C8: pre-check now measures sanitized.length). (af0fa87, 7372ddd) | cdp.mjs read-back compares against the sanitized form (regex form); maxLength pre-check ALREADY measured the sanitized length in AMEND4; PLUS url/email ASCII-whitespace trim; the snapshot fakes (FakeInput/FakeTextarea) model sanitization, and newline set_value cases were added to cdp_snapshot.mjs. (0eb3429) | SAME outcome; Codex is a SUPERSET at AMEND4 (maxLength + url/email trim) | SAME. VM caught up on maxLength at head (C8). One open micro-gap: VM head cdp.mjs does NOT trim url/email whitespace; Codex does (per the HTML Standard url/email states). Worth adopting as a small follow-up; it does not change the F1 verdict. |
| 9 | Supply-chain tests (C2 A3) | 3 tests: grounded_x_range unit, focus_type forwards x+y ranges to act_fn, first_action fallback supplies both ranges. (44c15bb) | grounded ranges test (x+y in one), focus_type forwards ranges, first_action fallback supplies ranges, PLUS relay fixture updates so the session fakes accept the new range arguments (c0c049e). (b2b59a9, c0c049e) | SAME shape; Codex covers the relay fixtures too | SAME. |
| 10 | Snapshot events (C1 G4) | Changed-value case added to cdp_snapshot.mjs: 'hello' to 'world' fires input then change, in order. (e912ad4) | Same changed-value case, PLUS newline set_value cases in the same file. (d6ed904) | SAME, Codex slightly broader | SAME. |
| 11 | Design docs (C3 G3/G4) | V4 caret promise removed from the bundle line and step 4 (with a B18 drop note kept); tab-switch protocol kept visible marked SUPERSEDED; benchmark target bullet added (clone1 Brave + clone2 Chrome on ws2). Minor inconsistency: the V2 clause still says "contenteditable innerText + caret offset". (8d75135) | V4 dropped (bundle line and step 4, "V4 caret position is out of scope per B18"); V2 clause also drops "caret offset"; tab-switch paragraph REWRITTEN in place to the new benchmark target (old text gone). (8c065f6) | SAME substance, different wording | SAME. Codex's wording is cleaner (no leftover "caret offset" in V2); VM's keep-visible SUPERSEDED marking preserves history. No merge action needed. |
| 12 | Act-now envelope (CL1-SWEEP) | _scope_after helper (first_action.py:337 at head): after = scope-matching (result_after when its scope matches, else a FRESH window capture via cu.observe; scopeless WINDOW meta treated as window scope per TEST-REPAIR C12); after_screen = screen capture, documented non-chainable; pre-overlay refusal ONLY when scope == 'screen' explicitly (scopeless metas not refused). 4 item-12 tests + 3 TEST-REPAIR tests. (cbab398, 2ec3d67) | Inline scope_after = session/fallback result['after'] (no fresh re-capture when result_after is absent or scope-mismatched); envelope after = compact _observation_reference (id, observation, scope, window, window_bounds, monitor, monitor_box), after_screen = screen reference; pre-overlay refusal when scope != 'window' (STRICTER: scopeless metas refused with scope_mismatch). 3 item-12 tests. (f4c0482) | SAME design; VM more COMPLETE | SAME design, VM shape kept. Codex gap: when no result after exists (or it is scope-mismatched), its envelope after is None instead of a fresh window capture; and its stricter pre-overlay refusal rejects scopeless metas that the VM lane deliberately accepts (pre-scope observations). Recommend the VM shape. |

## F4 decision: KEEP VM (y_range contract + TEST-REPAIR test repair)

Codex's mechanism, precisely from its diff (scripts/cu.py,
_input_line_changed, f0ddd41..06a34e8): when no y_range is given,
the band is [anchor_y - 12, anchor_y + 1), i.e. the 12 px ABOVE the
click plus the click line itself, instead of the symmetric
anchor_y +- 12; when no x_range is given, the band is the
anchor_x +- 6/7 neighborhood instead of the full width. With the
F4 geometry (anchor 118, pixels at y=126 and y=110, x_range
(100, 300)): [106, 119) excludes 126 and includes 110, so the
original test passes with no y_range passed. Verified live on the
laptop worktree: _input_line_changed with the F4 pixels returns
False (band probe, /tmp/band_probe.py).

Control check: the mechanism is a heuristic fitted to the test
geometry, not field-anchored. A click-anchored band cannot know
field boundaries, so narrowing it by fiat trades one
mis-attribution for a false-fail risk: a field spanning y 106..130
clicked at y 118 with text at y 126 (the SAME field, below the
click) would false-fail under the Codex band, while the VM
symmetric band (or a supplied y_range) passes it. No suite test
covers that shape on either lane; the argument follows directly
from the code, and I state it as code-derived, not test-proven.
The VM y_range contract is field-anchored (the grounded rect
decides), and TEST-REPAIR repaired the test itself with
y_range=(100, 120), which is the correct repair: the two pixels
are symmetric about the anchor (both 8 px away), so only the
field's y-range can distinguish them. Verdict: keep the VM repair;
do not adopt the Codex asymmetric fallback band.

## F5 decision: KEEP VM (threading + TEST-REPAIR wired-path test); REJECT the Codex "or" branch

Codex's mechanism has TWO parts, both from its diff
(f0ddd41..06a34e8):

(a) require_type_ranges gate. desktop_act gains
require_type_ranges=False; CodeExecBackend.act, the CLI act path,
and the first_action fallback all pass require_type_ranges=True.
Inside desktop_act, when require_type_ranges is set and any paired
type group lacks an x or y range, verified=False with basis
'unscoped-input-band' and note "no complete grounded target-field
rect was supplied". The ranges themselves come from
dom_act.grounded_type_ranges (new helper).

(b) Narrowed fallback band (item 3 above): the direct-call F5
behavior test passes through this part alone, because the F5
pixels (x 0..11 at y=10, click at x=15) leave only 3 pixels inside
the anchor_x neighborhood (x 9..11), below min_pixels 4. Verified
live on the laptop worktree: _input_line_changed with the F5
pixels returns False (band probe).

Control check on (a), run live on the Codex lane at 06a34e8: the
relay test test_click_type_verifies_through_input_line_band FAILS
(Ran 1 test, FAILED, code 1 != 0). A probe replaying the exact
relay shape through the relay ( /tmp/relay_probe.py) returns code
1, ok False, type_verified False, basis 'unscoped-input-band',
error_code 'type_unverified'. Isolation probe: the narrowed band
ALONE returns True for the relay pixels (click (5,5), pixels x
6..11 at y=5), so the gate is the SOLE cause of the relay failure,
not the band narrowing. The gate fires on EVERY CLI / code-exec
click+type batch without --dom-selector (ranges None), so on the
Codex lane the pixel band as a standalone verification channel is
dead on those paths: a batch whose text did land still reports
type_verified False. That is exactly the break the VM lane
deliberately rejected (AMEND4 log item 4; TEST-REPAIR F5 comment),
and the relay test is the live proof.

Third shape considered: adopt the narrowed fallback band WITHOUT
the gate (it passes both the F5 behavior test and the relay test
in isolation). Rejected: it changes the documented fallback
contract (anchor +- 12 symmetric, full width when no range) for
all unwired batches and false-fails same-field text below the
click line (see F4); the VM shape (grounded range when known,
documented fallback when not) preserves the contract. The gate
also buys nothing on the wired path (see the F5 DOM-gate finding
below: the DOM type_check already decides there). Verdict: keep
the VM repair; do not adopt the Codex gate or the narrowed band.

## F6 decision: KEEP VM (TEST-REPAIR head form); REJECT the Codex flag-gated verify JS

Codex's mechanism, precisely from its diff (scripts/zen_dom.py,
f0ddd41..06a34e8): the legacy window.__agentCuTyped map is KEPT
(inert, never trusted) so the F6 forge line
`window.__agentCuTyped['#msg-input'] = true;` does not throw; the
authority is a frozen recorder '__agentCuTypedRecorder' on the
element (read/reset, non-writable, non-configurable); verify_typed
JS returns null unless trusted.value === current value, which
makes out['value'] null so the original assertNotEqual(value,
'hello') passes; typed_flag itself only checks recorder.read()
is non-null and does NOT compare the value.

Control checks, all from source or live runs on the Codex lane:

1. before=None contract broken in production. Codex verify_typed
   JS (zen_dom.py, the verify_typed evaluate) returns null
   whenever no trusted record exists, REGARDLESS of before; the
   Python side returns False on a None result. The VM contract
   (kept in the AMEND4 log item 7 and in TEST-REPAIR) is
   equality-only when before is None, so a pre-filled field
   verifies. The break is MASKED by the fake: FakeWdSession's
   verify_typed branch returns a dict {value, editable, trusted}
   (trusted None when untyped) instead of null, so the Python
   before=None path skips the flag check and
   test_field_value_and_verify_typed passes on the fake while
   production JS would return False. No production caller uses
   before=None today (the only production caller is
   dom_act._verify, always with a before value), so the break is
   latent, not live, but it is a contract change with zero suite
   coverage on the Codex lane. The VM rejection reason stands.

2. typed_flag alone is sticky on Codex. After one trusted event
   recording 'h', typed_flag returns True even after a page
   script sets 'hello'; the sticky protection lives only in
   verify_typed, not in typed_flag. The VM typed_flag compares
   last-trusted to current value, so a caller using typed_flag
   alone is protected. F7 passes on both lanes, but through
   different components (Codex: verify gates; VM: flag gates).

3. Pre-lock residual: Codex's recorder name is FIXED
   ('__agentCuTypedRecorder'), so a page that knows it can
   pre-define a frozen forged recorder (no-op reset + forged
   read) before the arm and defeat the flag; the arm trusts a
   frozen recorder with a reset function. The VM head (TEST-REPAIR
   C7) installs the getter under a per-arm unpredictable name
   ('__agentCuTypedValue_' + secrets.token_hex(8)), records it in
   session._typed_flag_props[selector], and deleted the re-arm
   trust branch, so pre-locking is impossible without the token.
   The VM head is strictly stronger on item 7. (The AMEND4 VM
   fixed-name form had the same pre-lock residual; C7 closed it.)

TEST-REPAIR's F6 form is kept: the forge line is guarded in
try/catch (a forgery attempt that throws is itself evidence the
surface is gone), the value assertion is assertEqual(value,
'hello') with assertFalse(flag) (the field's value IS 'hello';
the flag is the discriminator, not the value), and no flag-gated
verify JS is adopted. Verdict: keep the VM repair.

## Relay-test answer (question 3)

Yes: test_click_type_verifies_through_input_line_band still FAILS
on the Codex lane at 06a34e8, confirmed live (not only from
Codex's log): Ran 1 test, FAILED (failures=1), code 1 != 0. The
replayed probe returns ok False, type_verified False, basis
'unscoped-input-band', error_code 'type_unverified'. Why: the
require_type_ranges=True in the CLI act path (cu.py main, no
--dom-selector, so type_x_ranges/type_y_ranges are None) makes
desktop_act refuse the band-only result. The narrowed band is NOT
the cause (isolation probe: _input_line_changed returns True for
the relay pixels). On the VM head the relay test passes (session
suites Ran 150 OK, including test_session_continuation). Codex's
fix did not change in a way that saves the relay: its own log
already reports this failure, and my live re-run at the fixed
HEAD confirms it unchanged.

## Test-count arithmetic (question 4)

Confirmed by running each suite on each lane:

- Base test_first_action count: 64 on both lanes. (VM 68 - 4
  item-12 tests; Codex 67 - 3 item-12 tests.)
- VM at cbab398 (AMEND4 item 12): Ran 68 OK (64 + 4 item-12
  tests: test_session_after_is_scope_matching_not_screen,
  test_fallback_after_is_scope_matching_not_screen,
  test_after_without_result_after_captures_fresh_window,
  pre-overlay scope refusal test).
- Codex at 06a34e8: Ran 67 OK (64 + 3 item-12 tests:
  test_after_preserves_input_scope_and_labels_screen_capture,
  test_fallback_returns_desktop_act_after_as_chainable,
  test_screen_scoped_key_refuses_before_overlay). No
  fresh-capture test: that is exactly the Codex item-12 gap
  (no re-capture when result_after is absent).
- VM head at 77c72be: Ran 71 OK (68 + 3 TEST-REPAIR C12 tests:
  test_scope_after_prefers_result_after_for_scopeless_window_meta,
  test_scope_after_mismatched_result_after_recaptures_window,
  test_scope_after_screen_input_reuses_screen_without_recapture).
- 71 - 67 = 4 = 1 (item-12 test gap) + 3 (TEST-REPAIR scope
  tests). Arithmetic reconciled exactly.
- RT2: VM head Ran 51 OK (49 + 1 F3 split + 1 maxlength test).
  Codex Ran 49 FAILED (failures=1 F3, errors=1 F2): Codex passes
  13 of the 15 original RT2 proof tests (F4/F5-behavior/F6 pass
  by contract change; F2 errors and F3 fails as written).
- Neighbors, VM head: test_zen_dom 42 + test_dom_act 19 +
  test_type_verification 61 + test_click2_redteam 71 +
  test_codemode 26 = Ran 219 OK (one combined run).
  Codex: test_zen_dom 42 + test_dom_act 18 +
  test_type_verification 59 + test_click2_redteam 71 = Ran 190 OK
  (one combined run). The dom_act gap (19 vs 18) is the VM
  grounded_x_range unit test shape vs Codex's combined
  grounded-ranges test; the type_verification gap (61 vs 59) is
  the VM item-3 band tests vs Codex's narrower band-test set.

## Full discover, both lanes at fixed HEADs (question 5)

VM lane at 77c72be, clean worktree /tmp/reconcile-vm-head
(native helpers + generated protocol files copied in; see the
worktree lesson above), command from tests/:
`PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py"`.
Result: Ran 1974 tests in 207.962s, FAILED (failures=2, errors=4,
skipped=17). The 2 failures are test_browser_image
test_persist_false_returns_rgb_without_state (RGB and RGBA): the
meta carries extra keys jpeg_quality/jpeg_subsampling that the
test expectation lacks. Proven later-lane, not AMEND4: the test
passes at 0668327, the test file is UNCHANGED between 0668327 and
77c72be, and only scripts/cu.py changed there (S0-IMPL J37 codec
separation added the keys). The 4 errors are exactly the AMEND4
baseline pre-existing errors (test_a11y_skeleton import,
test_cursor_file setUpClass g++ -std=c++26,
test_perf_evidence x2 missing benchmark JSON). Zero AMEND4
failures, zero EPERM/tempfile failures (no EPERM line in the log).
An earlier attempt in the same worktree before copying the
generated protocol files gave Ran 1951, failures=2, errors=5
(the extra error was test_wtype_native setUpClass for the missing
keyboard-protocol.c); that number is superseded by the clean
1974 run and is recorded here only so the two numbers are not
confused.

Codex lane at 06a34e8, laptop worktree
~/workspace/cu-amend4-codex (clean status verified),
same discover command, run detached on the laptop. Result: Ran
1925 tests in 129.287s, FAILED (failures=2, errors=4, skipped=2).
The 2 failures are the F3 stale-origin test (contradictory
assertions) and the relay band test (require_type_ranges gate).
The 4 errors are test_a11y_skeleton, the F2 region-fallback test
(DomActError, no assertRaises), and test_perf_evidence x2. This
matches Codex's own log exactly (1925, 2+4+2) and was
independently re-run at the fixed HEAD. No tempfile/EPERM
failures appear in the Codex log.

The 1974 - 1925 = 49 test gap is later-lane test additions on
the VM lane (S0 bundle + ssh_mux suites, TEST-REPAIR tests, Y1B
tests), not AMEND4 items. The skipped gap (17 vs 2) is the same
later-lane composition difference; the VM 17 matches the AMEND4
baseline skipped count exactly.

## F5 DOM-gate verification (question 6)

Confirmed from source at VM head 77c72be (scripts/cu.py, exact
lines): the DOM type_check block is at line 2110
(`if has_type and error is None and type_check is not None:`);
a failed check sets error plus error_code_override =
'type_unverified' at line 2117; the pixel-band block is at line
2279 (`if has_type and error is None and 'after' in result:`)
and its first branch at line 2280 takes the dom-value basis when
type_dom_verified is True, skipping the band code. So through
the full wired path the band is never the decider: on a DOM
pass the band is skipped (dom-value basis); on a DOM fail the
error is already set, so the line-2279 block is skipped
entirely. The wired paths all supply type_check:
CodeExecBackend.act at cu.py:2759 (dom_act.dom_hooks, when
dom_session + dom_selector are given), the CLI act path at
cu.py:3085-3088 (dom_act.open_dom_hooks), and the first_action
fallback at first_action.py:788-791 (dom_act.open_dom_hooks),
and all three also thread the grounded ranges. The band decides
only when type_check is None (direct desktop_act calls, the
relay test, unwired batches). TEST-REPAIR's finding is therefore
confirmed as stated (cu.py:2280 / 2110-2117 / 2279 all match).
It does NOT change the F5 verdict (keep VM); it strengthens it:
the require_type_ranges gate buys nothing on the wired path
(the DOM already decides there) and only kills the unwired
path, which is where the band is the only channel.

## S0 regression confirmation (question 7)

Confirmed from source and by test run. At the S0 tree 18f2304,
`def _scope_after` is ABSENT from scripts/first_action.py
(line 337 holds `def _dispatch_ms` in its place) while the call
site at line 875 still calls `_scope_after(...)`, so every
run() that reaches the envelope after-capture hits NameError.
At the AMEND4 tree 0668327 the def exists (line 328); at head
77c72be it exists (line 337, restored by TEST-REPAIR 2ec3d67
with the scopeless-window fix), call site at line 887. Test
run at head: test_first_action Ran 71 OK (my own run in the
clean worktree). The S0-tree numbers (Ran 68, failures=25,
errors=9) are TEST-REPAIR's measured numbers, quoted from its
log; I did not re-run the S0 tree myself, so I do not present
them as my own measurement. The second S0 breakage (FakeCu
missing CAPTURE_MAX_WIDTH) is likewise TEST-REPAIR's finding,
fixed in the same commit by adding CAPTURE_MAX_WIDTH = 960 to
the fake, mirroring scripts/cu.py:66.

Lesson, recorded for the coordinator: S0-IMPL's 129-suite green
did not cover test_first_action. Its own log says the 129-test
suite ran "37 ok / 92 tempfile-setup errors / 0 failures" under
the VM-wide EPERM file-write outage, so the suite signal was
already degraded, and test_first_action was not in that 129
set at all. A landing whose suite does not include the
first_action suite can delete _scope_after and stay green.
Follow-up owed (not mine to do here): the S0 landing check
should name test_first_action explicitly, and the 2
browser_image failures above (S0 J37 meta keys) are a second
instance of the same class (a later-lane change breaking a
suite it did not run).

## Later-lane diffs distinguished (not AMEND4)

Between the VM AMEND4 endpoint 0668327 and head 77c72be,
scripts + tests changed by 2871 insertions / 205 deletions
across 18 files. The AMEND4-relevant later changes are:
DOMZEN-FIX 5dcf2b31 (return values from 7 zen_dom helpers;
the return prefix broke 9-10 node harness tests, repaired by
TEST-REPAIR A/A2 with the bare-return wrap), S0-IMPL 18f2304
(SSH mux + measurement bundle; deleted _scope_after, see
question 7; added the jpeg keys that break the 2
browser_image tests), Y1B-RPC fd63a7d + 17fdb9b (snippets run
in a forked child; TEST-REPAIR D amended the codemode
builtins-pin test to capture via a temp file), TEST-REPAIR B
(the 5 defective-test repairs, including the F4/F5/F6
decisions this log keeps), C8 (maxLength on sanitized length),
C12 (_scope_after restore + 3 scope tests), C7 (per-arm
random typed-flag property name). None of these were
re-litigated except where they interact with an AMEND4 item,
as above.

## Open micro-gaps (for the coordinator, not verdicts)

1. VM head cdp.mjs lacks Codex's url/email ASCII-whitespace
   trim in set_value sanitization. Small follow-up; F1 stands.
2. VM item-11 wording keeps "caret offset" in the V2 clause
   while dropping V4; Codex's wording is cleaner. Cosmetic.
3. Item-1 factor contract: adopt the VM fail-closed factor
   (already the VM shape); Codex's scale_factor=1 default is
   the only open divergence on item 1 and is latent.
4. Item-6 stale check: VM skip-when-unreadable vs Codex
   fail-closed-on-unreadable plus full-bounds compare. The
   VM shape is recommended for portability; the full-bounds
   compare is an optional hardening.
5. The 2 browser_image failures at VM head (S0 J37) and the
   S0 suite-coverage lesson in question 7 belong to the S0
   lane, not AMEND4; flagged here because the full discover
   surfaced them.

## Verdicts summary (for the coordinator)

- Items 1, 2, 5, 9, 10, 11: SAME outcome on both lanes (items
  1 and 2 differ in implementation only).
- Item 6: DIFFERENT mechanism, SAME outcome; keep the VM
  shape (portability), Codex full-bounds compare optional.
- Item 8: SAME; Codex was a superset at AMEND4, VM caught up
  at head except the url/email trim (open micro-gap 1).
- Item 12: SAME design; keep the VM shape (fresh-capture
  branch + scopeless handling; Codex leaves after=None when
  no result after exists).
- F4: KEEP VM (y_range contract). Codex asymmetric fallback
  band rejected (heuristic, not field-anchored).
- F5: KEEP VM (threading + TEST-REPAIR wired-path test).
  Codex require_type_ranges gate REJECTED (breaks the relay
  test live; kills the band-only channel on unwired paths).
  Narrowed fallback band alone also rejected (contract change,
  below-click false-fail risk).
- F6: KEEP VM (TEST-REPAIR head form, per-arm random name).
  Codex flag-gated verify JS REJECTED (breaks the before=None
  contract in production, masked by the fake; typed_flag
  alone stays sticky; fixed recorder name is pre-lockable).
- Relay test: still FAILS on the Codex lane at 06a34e8
  (basis 'unscoped-input-band'); passes on the VM head.
- Counts: test_first_action VM 71 OK vs Codex 67 OK
  (arithmetic reconciled: 1 item-12 test gap + 3 TEST-REPAIR
  tests). Full discover: VM 1974 (failures=2 S0-caused,
  errors=4 pre-existing) vs Codex 1925 (failures=2 F3+relay,
  errors=4 incl. F2). Zero AMEND4 failures on the VM head.

## Evidence index (runs I performed)

- ls-remote 08:12: todolist-push 77c72be38f4473d470fadde7bbbb5344f8931504,
  amend4-codex 06a34e8610a9467c3884f6dd7a567293c747da45.
- Laptop worktree check: 06a34e8, clean status.
- Codex test_first_action: Ran 67 OK (laptop, 08:14).
- Codex relay test: Ran 1 FAILED (laptop, 08:15); probe
  /tmp/relay_probe.py: code 1, basis 'unscoped-input-band'.
- Codex band probe /tmp/band_probe.py: relay pixels True, F5
  pixels False, F4 pixels False.
- Codex RT2: Ran 49 FAILED (failures=1 F3, errors=1 F2)
  (laptop, 08:16).
- Codex full discover: Ran 1925 in 129.287s, FAILED
  (failures=2, errors=4, skipped=2) (laptop, detached,
  finished 08:19).
- VM head test_first_action: Ran 71 OK; RT2: Ran 51 OK
  (after copying untracked native artifacts; first attempt
  showed 41 environmental errors, see worktree lesson).
- VM head neighbors: zen_dom + dom_act + type_verification +
  session_continuation + session_policy Ran 150 OK; zen_dom +
  dom_act + type_verification + click2_redteam + codemode Ran
  219 OK; node cdp_snapshot.mjs exit 0.
- Codex neighbors: zen_dom + dom_act + type_verification +
  click2_redteam Ran 190 OK.
- VM head full discover (clean): Ran 1974 in 207.962s,
  FAILED (failures=2, errors=4, skipped=17). Earlier
  attempt Ran 1951, failures=2, errors=5 (wtype artifact
  error), superseded.
- AMEND4-tree check: test_browser_image + test_wtype_native
  at 0668327: Ran 9, FAILED (errors=1, wtype only);
  test_browser_image passes there.
- No em dash or en dash in this file (grep-checked before
  commit).
