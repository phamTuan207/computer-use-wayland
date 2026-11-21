# Worker CLICK-C2 review log (council member 2 of 3)

Branch: todolist-push. Task: independent review of fix diff e4082ff
(8 files, +824/-38). Read-only on the fix code; no laptop driving; no
ydotool; no em/en dashes in this log or in any file written by this worker.

## 2026-11-22 01:38:56 +07 (t+0s)
Start. Repo at ~/workspace/computer-use-wayland, branch todolist-push,
HEAD e4082ff. Confirmed the diff stat matches the brief: 8 files,
824 insertions, 38 deletions.

## 2026-11-22 01:40 +07 (t+1m)
Read the root-cause logs: worker-click-src-log.md (050272d),
worker-click-probe-log.md (fa289eb), worker-click-fix-log.md (e4082ff).
Root causes as recorded:
- Conversion CORRECT (image_point cu.py:995 region origin, move cu.py:1602
  monitor_box normalize, probe P1 0px, P2 1px). The ~50px reading was a
  measurement artifact (grim excludes the pointer, no -c flag).
- G28: _fresh_observation substitutes a screen capture for a stale window
  observation (staleness only, age + 20s deadline over 120s); the refusal
  never named the substitution.
- Type never verified: completed+=1 on wtype exit; Stage A single 'X'
  never appeared with 6/6 clean.
- zen_dom _wd caught HTTPError only; raw TimeoutError escaped (F3b).

## 2026-11-22 01:44 +07 (t+5m)
Read the full diff e4082ff (cu.py, first_action.py, zen_dom.py).
Findings recorded in the verification section below.

## Verification (all checked against e4082ff, not HEAD)

### (1) G28 loud refusal, first_action.py
- _read_given_observation (new, lines 292-323) isolates the staleness-only
  trigger exactly as SRC specified: age + deadline_s over 120 s is stale;
  unreadable and incomplete are separate reasons. The 114 s batch-2 case
  (8fef498445d2, 114 + 20 = 134 over 120) is covered by a dedicated test.
- _fresh_observation now returns a 4-tuple (meta, path, source, rejected);
  the only production caller is run() line 461. No other caller exists
  (grep); test_phase3_c1 tests _valid_capture_identity, not this.
- run() refuses loudly before any session attempt for key/type batches
  (lines 478-489): message names given id, age, reason, and what to pass;
  session never attempted (test asserts sess not called, desktop_calls
  empty); fallback_reason set; the early return 1 sits inside the outer
  try, so the finally (line 603) still releases the overlay, appends the
  JSONL record, and prints the envelope. Cleanup preserved.
- ime_state_trace surfaced on both the session path (lines 512-519) and
  the fallback path (lines 576-578), success and failure alike; guarded
  by isinstance list checks. This closes the PROBE finding that the trace
  was absent from every act-now envelope.

### (2) Type verification, cu.py desktop_act
- has_type (lines 1601-1606) covers both group shapes from keyboard_groups
  (cu.py:1112): bare dict type actions (text starting with '-', ungrouped)
  and type dicts inside keyboard-group lists. keyboard_groups is the only
  producer of groups, assigned line 1505 before has_type is read.
- Verification (lines 1858-1872) reuses the pre-existing frame_bytes_changed
  signal (line 1847: after pixel_sha256 vs pre-action meta pixel_sha256),
  fails with error_code type_unverified and next_step re-observe when the
  frame is unchanged. The comment states the limit honestly: a changed
  frame is necessary, not sufficient (animations change it too). Key-only
  batches are exempt by design (a shortcut may change nothing visible).
- after_capture=False records type_verified None plus a skip note
  (lines 1812-1817) instead of letting ok rest on wtype exit alone.
- GAP (minor, same defect class): the other after_skipped path
  (lines 1832-1834, terminal_address None with expected_terminal_window
  'none'/'unbound', used by tc02_controller steps) sets after_skipped but
  no type_verified. A type batch there still reports ok on wtype exit
  alone with no verification record. Act-now never passes
  expected_terminal_window, so this does not touch the reported failure;
  it is a consistency gap in the fix's own coverage. Required item 2.

### (3) zen_dom.py TimeoutError handling + tab_at
- _wd (lines 147-170) converts TimeoutError, OSError, URLError to
  ZenDomError; HTTPError keeps its own branch first (it is a URLError
  subclass). socket.timeout is TimeoutError since 3.10, so it is covered.
  Matches the F3b root cause (raw TimeoutError escaped the HTTPError-only
  handler).
- tab_at / list_tabs(handle_index=) (lines 196-239): single-switch
  targeting, out-of-range raises ZenDomError, original tab restored in
  finally even on a hang. Full scan records a hung handle as an error
  entry and keeps going (Arm D v2 pattern). The per-handle except also
  lists TimeoutError/OSError, redundant after _wd conversion but harmless.
- No other callers of zen_dom.list_tabs exist: zen_cli.py:558 defines its
  own BiDi list_tabs(session); the fix log's "CLI and codemode locate
  stub" stands. No regression surface outside zen_dom.

### (4) Tests, run by me
- New suites from tests/ dir: 139 tests, OK (57 first_action + 7
  type_verification + 11 zen_dom + 32 keyboard_preflight, plus 32
  inherited DesktopPreflight tests re-run via the TypeVerification
  subclass).
- NOTE: running as `python3 -m unittest tests.test_type_verification`
  from the repo root fails to import (test_type_verification.py:17 does
  `from test_keyboard_preflight import ...`, which needs tests/ on
  sys.path). That is my invocation, not the repo's: the documented
  command is `python3 -m unittest discover -s tests -p 'test_*.py'`
  (README.md:434, docs/testing.md:6), and test_fast_observe.py:4 uses
  the same import style, so it is the pre-existing convention. Full
  discover result below.
- Fail-before reproduced exactly in a temp worktree at fa289eb with the
  new test files copied in (plus the untracked native/wtype binary, which
  a fresh worktree lacks; without it 21 harness errors are a setup
  artifact, not old-code behavior): test_first_action 2 failures +
  12 errors, test_type_verification 2 failures + 2 errors,
  test_zen_dom 8 errors, test_keyboard_preflight OK. All three match the
  fix log's claims. Worktree removed afterwards.

### (5) Hygiene and scope
- Em dash U+2014: 0 in the whole diff. En dash U+2013: 0.
- ydotool: 1 occurrence, the fix-log sentence "No ydotool used", a
  mention, not usage. No ydotool anywhere in code or tests.
- PII: none in code or tests. The only email-like string in the diff is
  the git author line, pre-existing repo convention.
- Coordinate conversion untouched: cu.py hunks are at 1598, 1797, 1832
  only. image_point (cu.py:995-999) and move() (cu.py:1602-1615) are not
  in the diff. The has_type block sits before def move, it does not
  modify it.
- Y13g untouched: the diff touches 8 files only, none Y13g; no change to
  _check_entry_pyc or any Y13g file. (Working-tree modification to
  worker-y13g-r2-redteam-log.md seen during this review belongs to other
  workers, not to e4082ff; not touched.)
- Other in-flight work noted, not read for this verdict: a C3 review
  commit 59acd36 landed on todolist-push during this review. My verdict
  below was reached from my own analysis before seeing that commit; I
  did not read the C3 log.

## 2026-11-22 01:47 +07 (t+8m)
Full discover run finished: 1718 tests in 292.6 s, FAILED (failures=2,
errors=2, skipped=17). All 10 touched-area modules pass individually
(test_first_action, test_type_verification, test_zen_dom,
test_keyboard_preflight, test_fast_observe, test_act_diagnostics,
test_guard_boundaries, test_pointer_safety, test_focus,
test_observation_contract: all OK). The 2 failures + 2 errors come
from modules outside the touched areas; identifying them now with a
second discover run captured to a file, to rule out a regression from
e4082ff before finalizing.

## 2026-11-22 01:49 +07 (t+10m)
Second discover run: same 1718 tests, same 2 failures + 2 errors.
Breakdown of the four:
- ERROR setUpClass test_cursor_file.CursorFileTests: g++ rejects
  -std=c++26 on this VM ("unrecognized command-line option").
  Toolchain environment issue, unrelated to e4082ff.
- ERROR + FAIL in test_tc02_controller.Tc02MenuBarTests (typed text
  checks): "tesseract is unavailable; refusing to assume text
  presence". Missing binary on this VM, unrelated to e4082ff.
- FAIL test_session_continuation.TypedRefusalRecovery.
  test_expired_observation_typed_refusal_then_observe_then_act_succeeds:
  THIS ONE IS CAUSED BY e4082ff, see the regression section below.

## REGRESSION (found 01:50-01:52 +07, verified against fa289eb)
- HEAD (e4082ff), single test and full module: FAIL at
  test_session_continuation.py:255, relay exit code 1, expected 0.
  The corrected act (fresh observation + type 'after refresh') now
  fails: desktop_act's new type verification sees the fake
  after-capture frame as unchanged and returns ok False with
  error_code type_unverified.
- Mechanism, confirmed from the test source: the test builds fresh and
  after from the SAME blank 20x20 image (write_observation, pixel
  hash of stored pixels), and post = dict(after). The after-capture
  mock returns post, whose pixel_sha256 equals the fresh observation's
  hash, so frame_bytes_changed is False. The sibling test
  (invalid-wait refusal then corrected type) passes because its post
  uses base_meta(pixel_sha256='1111'), a distinct hash.
- Base (fa289eb) single test: OK (run at 01:52, monotonic 169.9 s).
  The fix author's own harness update (test_keyboard_preflight:
  after_pixel_sha256='after-frame-changed') shows the intended pattern:
  fakes must simulate landed text. This test's fake was not updated.
  So the fix behaves as designed and the fake is unrealistic, but the
  fix lands a behavior change that breaks an existing passing test,
  which the fix author never saw because only 241 touched-area tests
  were run, not the full 1718 discover suite. Required item 3 below.
- CORRECTION to an intermediate reading, recorded honestly: my first
  base runs (01:50-01:51) failed this test at line 258 with refusal
  'capture_started_monotonic is invalid', which I first read as a
  pre-existing failure. It was not: the VM had restarted at about
  01:50 +07 (uptime 2 min, monotonic about 160 s), and the stale
  fixture sets capture_started_monotonic = monotonic() - 121 s, which
  goes negative when uptime is under 121 s. Once uptime grew past
  121 s the base run passes clean. Environment artifact of the
  restart, not a pre-existing failure. The regression conclusion above
  stands on the re-run, not on the artifact.

## 2026-11-22 01:46 +07 (late-arriving context, from MEMORY.md)
CODEX-DEMO proved the message failure's root cause is misreading the
click point by eye, not coordinates and not typing: Muse clicked
(250,1037), 64 px above the real input top edge (input y 1101-1164,
center (306,1132)); Codex re-read a fresh observe, clicked
(300,1132), saw the caret, typed, and sent. The Stage A type
hypothesis (contenteditable swallow) is refuted. This does not change
the verdict on e4082ff: the diff never claims to fix point-reading,
and type verification would have flagged those silent batches as
type_unverified instead of ok 6/6 and 9/9, which is exactly its
purpose. It strengthens the value of fix (2).

- The hazard is real and already proven by SRC's own arithmetic, not
  hypothetical: Brave window [2533,914,901,1176] inside monitor eDP-2
  [2464,902,1920,1200], offset (69,12). Point (250,1037) written for the
  window image lands at global (2783,1951); run against the substituted
  screen region it lands at (2714,1939), off by (-69,-12).
- cursorpos verification cannot catch it: move() verifies the pointer
  reached the global point the code computed, and (2714,1939) IS the
  point the code computed from the screen region. The check passes while
  the click lands 69,12 off the intended target. This is the same blind
  spot the type-verification fix removes for typing: verification of the
  wrong thing, reported ok.
- The mitigation in the diff is a nested envelope field,
  observation.given_observation_rejected (first_action.py:480), with
  fallback_reason left None and error None and ok True. An agent that
  checks only ok/completed, the exact pattern that let the silent type
  failure run 9/9 clean, will not see it. And the recording happens
  after the click: a mis-click is an irreversible side effect, not a
  reportable near-miss. CL1-MSG2's own P2 click (750,1150) opened a
  task-detail panel by grazing a task row; a 69px offset mis-click
  demonstrably triggers unintended UI actions.
- The fix's own stated principle contradicts the exception: the commit
  message says a rejected given observation is "never silently replaced";
  _fresh_observation's docstring says "the caller (run) must refuse
  loudly on it instead of acting on the substitute (G28)". For
  pointer-only batches run() does act on the substitute.
- The widening is one line: drop the has_keyboard gate at
  first_action.py:484 so any batch refuses when rejected is not None.
  The refusal message already covers the pointer-only case ("omit
  --observation and write coordinates for the screen"). No new machinery.
- Weighed alternative, stale screen observation: the widening also
  refuses a batch whose rejected observation was itself a screen
  observation, where the fresh screen capture shares the region and the
  coordinates would still be valid. Cost of refusing there is one
  re-observe round trip; the screen content is 100+ s old anyway and the
  session guard would likely refuse on screen change. No legitimate flow
  depends on proceeding, and no observation given at all (the documented
  default) is unaffected because rejected is None. Blanket refusal is
  simpler than carrying scope through the rejection dict, and correct.
- The procedural mitigation (observe and act-now in one SSH call, age
  under 100 s) makes the trigger rare, but rarity is not a fix for a
  silent wrong action of the same class G28 exists to prevent.
- JUDGMENT: the documented residual is NOT acceptable. The one-line
  widening is required now.

## VERDICT: AMEND
Required fixes (small, all inside the diff's own files):
1. Widen the G28 loud refusal to ALL batches when a given observation
   was rejected: drop the has_keyboard gate at first_action.py:484 so
   run() refuses before any session attempt for pointer-only batches
   too. Update the inline comment at first_action.py:466-477 (which
   says pointer-only batches proceed "per the SRC spec") and the
   _fresh_observation docstring if it still implies the exception.
   Flip tests/test_first_action.py:620
   (test_stale_given_observation_pointer_only_proceeds_recorded) to
   assert refusal: code 1, path 'refused', session not attempted,
   fallback_reason naming the stale observation. Re-run
   test_first_action; the other G28 tests are unaffected.
2. (Minor) Record the type-verification skip on the other after_skipped
   path: in desktop_act, scripts/cu.py:1832-1834 (terminal_address None,
   expected_terminal_window 'none'/'unbound'), set
   result['type_verified'] = None plus a type_verification note when
   has_type, matching the after_capture=False branch at cu.py:1812-1817.
   Add a test mirroring
   test_type_batch_after_capture_false_skips_verification.
3. (Regression) Update the expired-observation test's fake so the
   after-capture simulates landed text: in
   tests/test_session_continuation.py,
   test_expired_observation_typed_refusal_then_observe_then_act_succeeds,
   the post observation must carry a pixel_sha256 distinct from the
   fresh observation's hash (same pattern as the sibling test's
   base_meta(pixel_sha256='1111') and the test_keyboard_preflight
   harness after_pixel_sha256='after-frame-changed'). Then re-run
   test_session_continuation and the full discover suite; the full
   suite must show no fix-caused failures (the tesseract and g++
   failures are VM environment issues, recorded in this log).
Not required: no change to coordinate conversion (proven correct), no
change to Y13g, no change to the key/type refusal, the ime trace
surfacing, or the zen_dom handling, all of which are sound as landed.
Documented limitation, not a defect: type verification is necessary,
not sufficient (a frame changed by the click itself or by animation can
mask a silent type failure). The omnibox discriminator from the fix log
is the next diagnostic step for the app-layer fault, out of scope here.
