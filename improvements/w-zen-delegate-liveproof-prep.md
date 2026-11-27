# W-ZENPREP: Zen pointer delegate live proof, preparation only

Owner: the owner. Coordinator: COORD-CLICK-6. Worker: W-ZENPREP.
Repo ~/workspace/computer-use-wayland, branch todolist-push, HEAD
05140c1 at start (verified equal to origin/todolist-push, section 1).
No em dash or en dash anywhere in this file. No personal info.

## Amendment 22/11/2026 (W-ZENPROOF2-AMEND): title premise corrected

Run 2 of this proof (W-ZENPROOF2) closed the owner's Muse chat tab
because the procedure and the driver identified the scratch tab by
document.title ('Clone zen thread'), but the fixture title is the
static 'Two-vision benchmark fixture': the fixture JS only sets the
H1 text. The scratch tab is now identified by URL substring
('two_vision_fixture.html?clone=zen'), the H1 text is a content
confirmation only, and the document title is evidence only, never
a gate. Every stale title-gated step in this file was corrected to
the URL-substring target (full stale list in
improvements/w-zenproof2-fix-council-3-review.md section 6.1 and
improvements/w-zenproof2-amend-log.md). The fixed driver
(zen-tab.py) also verifies the new tab was actually made current
before any navigate or DELETE, re-verifies the current tab right
after the navigate, requires the tab count to grow by exactly 1,
and deletes in the open exception handler only when the current
tab is the fixture tab by URL AND by handle. The next proof copies
the fixed run 2 runner (c5-zen-delegate-run2.py); run 1
(c5-zen-delegate-run.py) must not be re-run as-is. On a 'not made
current' refusal, the leftover empty about:blank tab is closed by
hand in the Zen UI, never via Marionette, and the open is not
retried in a loop. When the owner tab carries the fixture URL
after a refused open, the coordinator navigates it back to the
Muse thread by hand in the Zen UI, never via a Marionette
navigate or DELETE, and verifies the pre-check passes before the
next run (Council 1 C1, amend 2: the leftover after a refused
open is not always an empty about:blank tab).

## 0. Scope: preparation only, no live run

This file prepares the live proof of the Zen pointer delegate
(scripts/zen_pointer.py, commit 9ec713c). It contains the full
step by step procedure, the scratch target specification, the
verification checklist, and the risk register. It contains NO
live run: no tab was opened, switched, or navigated in the owner's Zen, no focus was taken, no input was sent to the live
browser, and no SSH session to the laptop was opened in this
task. the owner is using the machine and using Zen right now,
so the live proof itself is deferred by design, not by accident.

What the delegate is, in one paragraph: ZenPointerDelegate
translates Zen DOM actions plus their screen points into desktop
actions through CodeExecBackend.act, stamping each with the scope
plus observation_id of one fresh window observation per batch.
begin_batch focuses the Zen window first, then observes it once.
The mapping is click, double_click, focus, confirm_click,
hover_click to a desktop click at the point; fill and set_value
to click plus type; key to a desktop key with no point; move,
hover, scroll to their desktop forms; drag refuses because a
single point cannot express from and to. A failed or incomplete
desktop act returns False; a CB-2 refusal from act propagates.
The backend calls begin_batch once per batch in dom_act, skipped
for read-only batches (wait and assert only). cu.py code-exec
wires it when CU_DOM_BACKEND=zen.

Status at the end of this prep task: unit proven, live proof NOT
proven, and NOT runnable as written. Three pre-live findings in
section 4 block the run: the shipped (b1) program is CDP shaped
and fails on Zen before the Enter is dispatched (finding A); the
backend calls sent_bubble_contains with two arguments while the
real session takes one, which raises TypeError after the Enter
is sent (finding B); and a Marionette opened tab on live
windowed Zen may have a 0x0 viewport, which needs a go or no-go
gate before any input (finding C). A fourth item (finding D) is
a procedure load bearer, not a bug: dom_observe harvests the
CURRENT tab, so the scratch tab must be pre-selected as current
before the program runs. Nothing in this file claims the live
proof passed. The coordinator assigns the fixes and the run
window; this file only makes both ready.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from task receipt)

- 17:49:23 +07, T+0m: task received. VM HEAD 05140c1.
- 17:49:29 +07, T+0m: git fetch origin, HEAD equals
  origin/todolist-push (05140c10d180ce7d26548df0f5b6f9c4d431e316).
  Plain `git pull --ff-only` failed with "Cannot fast-forward to
  multiple branches" because the local config tracks several
  branches; the explicit `git fetch origin todolist-push` returned
  no new objects and `git rev-parse origin/todolist-push` equals
  local HEAD, so there was nothing to fast-forward. Recorded
  honestly instead of claimed as a clean pull.
- 17:49:40 +07, T+0m: found the delegate by grep: commit 9ec713c,
  scripts/zen_pointer.py, tests/test_zen_pointer.py.
- 17:49:52 +07, T+0m: re-ran tests.test_zen_pointer plus
  tests.test_p2_element_ref: 115 tests, OK, 0.181s.
- 17:49:55 to 17:50:08 +07, T+1m: re-ran all three suites
  (zen_pointer, p2_element_ref, code_exec): 175 tests, OK,
  12.449s unittest time, 12.651s wall. Individual counts:
  test_zen_pointer 15 OK, test_p2_element_ref 100 OK,
  test_code_exec 60 OK (section 3).
- 17:50 to 17:53 +07, T+1m to T+4m: read the wiring in full:
  scripts/zen_pointer.py (138 lines), scripts/zen_backend.py
  dom_observe, _screen_point, _revalidate, _dispatch, _verify,
  dom_act, _resolve_target, scripts/cu.py code-exec wiring
  (lines 3147-3175), focus (lines 590-606), CodeExecBackend
  observe_window and act (lines 2862-2935), scripts/code_exec.py
  _api_dom_act, api_dom_observe, _validate_dom_actions,
  scripts/element_ref.py is_send_action, scripts/zen_dom.py
  ZenSession, sent_bubble_contains, verify_typed, focus_check,
  scripts/s2_flip_live.py build_program_set_value,
  tests/two_vision_fixture.html, the step 9 log
  (improvements/worker-click5-step9-log.md, sections 7, 8, 10,
  11), the step 10 prep log, docs/zen-dom-control-comparison.md,
  tests/zen_selenium_attach.py, and the P2 amend fix log section
  8 (first live Zen run, 13:22:29 +07).
- 17:52:52 +07, T+3m: repro run 1 (finding A): the shipped (b1)
  program shape, key action with no ref, stops the batch at
  action_index 2 with stale-ref element_missing before any Enter
  dispatch. Elapsed 273ms.
- 17:53:05 +07, T+4m: repro run 2 (finding B): the unit-test
  shape, key action with ref, raises TypeError at
  zen_backend.py:455, sent_bubble_contains called with two
  arguments against the real one-argument session. Elapsed under
  1s. Full tracebacks in section 4.
- 17:53:15 +07, T+4m: printed the shipped (b1) builder output;
  confirmed the key line carries no ref and dom_observe is
  called with no scope.
- 17:53:36 +07, T+4m: the proposed Zen program (section 5, phase
  4) passes code_exec._validate_dom_actions and
  dom_asserts.require_asserts with no exception; is_send_program
  True; is_send_action True for the key.
- 17:54 to 17:57 +07, T+5m to T+8m: wrote this file, then commit
  and push (section 9).

Pre-existing dirty tree, not mine, not touched: modified
tests/realistic/clone1-batch3/results.json (the task brief says
do not commit it), plus six untracked improvements files
(codex-discuss-prompt.md, fcc-discuss-prompt-run2.md,
fcc-discuss-prompt.md, multi-agent-deliberation-idea-20261121.md,
muse-coordinate-accuracy-20261120.md,
worker-y14b-fix6-redteam.md). This task commits exactly one
file, improvements/w-zen-delegate-liveproof-prep.md, with an
explicit pathspec.

## 2. Sources re-read (file, lines, commit)

- scripts/zen_pointer.py, 138 lines, commit 9ec713c (C5-STEP9:
  Zen pointer delegate wiring). Read in full.
- tests/test_zen_pointer.py, 269 lines, commit 9ec713c. Read in
  full. 15 tests: 12 DelegateUnitTests plus 3 BackendWiringTests.
- scripts/zen_backend.py: set_pointer lines 154-161; dom_start
  lines 91-115; _resolve_target lines 189-208; dom_observe lines
  233-317; _screen_point lines 319-336; _revalidate lines 338-384;
  _dispatch lines 389-398; _verify lines 426-470; dom_act lines
  471-700 (begin_batch call lines 503-505, read-only skip lines
  500-502).
- scripts/cu.py: focus lines 590-606; CodeExecBackend
  observe_window lines 2862-2867; act lines 2874-2935; code-exec
  Zen wiring lines 3147-3175 (CU_DOM_BACKEND=zen builds
  ZenDomBackend, then set_pointer with ZenPointerDelegate around
  CodeExecBackend, focus_fn lambda to focus).
- scripts/code_exec.py: api_dom_observe lines 1358-1373;
  _api_dom_act lines 1375-1448; _bound_dom_snapshot lines
  1285-1300; _bind_dom_snapshot lines 1266-1283.
- scripts/zen_dom.py: DEFAULT_MARIONETTE_PORT 2828, DEFAULT_WD_PORT
  4444, GECKODRIVER /tmp/geckodriver, LOCK_PATH
  ~/.cache/agent-computer-use/zen_dom.lock (lines 71-76);
  ZenSession __enter__ lines 455-490 (geckodriver
  --connect-existing, one session, file lock, session delete in
  finally); sent_bubble_contains lines 1296-1325 (one argument,
  text); verify_typed lines 1158-1207; focus_check lines
  1118-1140; harvest lines 1325-1386; list_tabs and tab_at lines
  600-690 (tab_at switches then restores the original tab).
- scripts/s2_flip_live.py: build_program_set_value lines 136-185
  (landed 4-action (b1) shape); COMPOSER_ROLES line 91
  (textarea, textbox, input); oneshot_code_exec lines 292-322;
  LAPTOP_CU line 70 (~/computer-use-wayland/scripts/
  cu.py); LAPTOP_REMOTE line 71.
- scripts/element_ref.py: is_send_action lines 167-176;
  SNAPSHOT_MAX_AGE_SECONDS 120 line 29.
- scripts/dom_asserts.py: ASSERTS key entry line 72 (assert
  sent_bubble, mandatory); require_asserts and assert_for lines
  131-160.
- tests/two_vision_fixture.html, 2014 bytes, sha256
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf
  (matches the C4 bench manifest, deploy-manifest.json lines
  23-25, and the step 9 held-out runs 90 and 91).
- improvements/worker-click5-step9-log.md: section 7 (delegate
  wiring, 15 tests, 175 OK), section 8 (live (b1) runs 0-5:
  Chromium 5/5, program elapsed 123-161ms, wall 22-25s on sends;
  Brave fill 3/5 with the mouseMoved stall), section 10 (held-out
  run 91 PASS, wall 33286.8ms, retry already-sent, delayed count
  1), section 11 (Zen delegate live proof DEFERRED, no clean
  venue, owner asleep at the time), section 0 (focus rule
  C5-FOCUS-INCIDENT, window map 15:21 +07, relay and broker
  notes, /tmp persistence lesson: use persistent paths
  ~/c5-step9-run with copies on the VM).
- improvements/worker-click5-p2-amend-fix-log.md section 8: first
  live Zen run, CU_DOM_BACKEND=zen, PASSED 13:22:29 +07, wall
  2.49s, program dom_start plus dom_observe('Example Domain',
  'body') plus dom_act wait 2000ms then click on ref 'body',
  result no_pointer_delegate (pointer was None then), no input
  dispatched at any point. Marionette tab switched to Example
  Domain before the run (13:21:42) and restored to Welcome!
  after (13:22:46). Command shape on the laptop, inside
  `computer-use session`: CU_CODE_EXEC=1 CU_DOM_BACKEND=zen
  python3 /tmp/c5-amend-zen.py, which wrote the program file
  (mode 600) and ran scripts/cu.py code-exec --program
  /tmp/c5-amend-zen-program.txt --intent '...' --wall-seconds 45.
- docs/zen-dom-control-comparison.md section 3: Selenium plus
  geckodriver on live windowed Zen, Marionette opened tab reports
  window.innerWidth and innerHeight 0, document.hasFocus false,
  elementFromPoint null at every point, "Element could not be
  scrolled into view". Section 7: one remote session TOTAL per
  Zen instance (shared across BiDi and Marionette); a hung client
  leaked the slot for 1h51m on 21/11 and only a Zen restart
  cleared it. Section 9: DOM for locate and read, real mouse for
  click.
- tests/zen_selenium_attach.py lines 124-149: the safe new-tab
  sequence, POST /session/{id}/window/new {"type": "tab"} then
  POST /session/{id}/url {"url": fixture}, wait for readyState
  complete, then close with DELETE /session/{id}/window and
  delete the session. Never navigates, types into, or clicks on
  any existing tab.

## 3. What is proven, what is not

Proven, re-run in this task (not trusted from the log):

- Command, 17:49:55 +07: `python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec` on the VM. Output: `Ran 175 tests in
  12.449s`, `OK`. Wall 12.651s, 17:49:55 to 17:50:08 +07.
  Individual counts re-checked separately: test_zen_pointer 15
  OK in 0.014s, test_p2_element_ref 100 OK in 0.132s,
  test_code_exec 60 OK in 12.494s. Total 15 plus 100 plus 60
  equals 175, matching the step 9 claim.
- The backend integration tests in test_zen_pointer.py drive
  the landed (b1) program through the delegate against fakes
  and verify the DOM postconditions plus the screen point:
  field center (200, 215) plus verified origin (2749, 922)
  equals (2949, 1137). The verified origin comes from the A1/A2
  fix (commit fd9237a): check_viewport_geometry prefers a
  supplied verified moz inner on every branch.
- Fixture identity: `sha256sum tests/two_vision_fixture.html`
  on the VM returned
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf,
  the C4 bench manifest hash. The file the live proof will open
  is the same file the held-out run 91 passed against.

NOT proven, and not claimed here:

- No live Zen input has ever been sent through the delegate.
  The 13:22:29 +07 live Zen run used pointer None and refused
  with no_pointer_delegate before any input. The step 9 log
  section 11 records the delegate live proof as deferred.
- The unit tests pass against fakes whose signatures differ
  from the real session in at least one place (finding B). A
  green unit suite is not a live proof, and this file does not
  treat it as one.
- No timing exists for the Zen delegate path on live Zen: no
  program elapsed, no wall time, no observe cost. The budgets
  in section 5 are extrapolated from the CDP (b1) runs and the
  13:22 read-only Zen run, and are labeled as budgets, not
  measurements.

## 4. Pre-live findings: three blockers, one load bearer

### Finding A (BLOCKER): the shipped (b1) builder program is CDP shaped and fails on Zen before the Enter

Evidence, read from the code:

- scripts/s2_flip_live.py build_program_set_value emits
  `snap = dom_observe("TABID")` with no scope argument.
  scripts/zen_backend.py dom_observe lines 242-246 raises
  ZenDomError ("dom_observe on Zen requires a scope: a
  non-empty CSS selector to bind the snapshot to") when scope
  is missing. The shipped program cannot even observe on Zen.
- The emitted key action is `{"type": "key", "keys": ["Enter"],
  "scope": ..., "observation_id": ...}` with no ref and no
  selector. scripts/zen_backend.py dom_act resolves the
  selector per action as `action.get('ref') or
  action.get('selector')` and revalidates EVERY non-wait action
  before dispatch, including keys. A key with no selector
  revalidates against None and fails.
- The emitted assert action uses `"selector": "#thread
  .bubble:last-child"`, which does resolve, so only the key is
  affected by this finding.

Repro, run on the VM 17:52:52 +07 (no live browser, no SSH,
no pointer; the session and the desktop backend are the test
fakes, only the action shapes are the shipped ones):

- Command: `python3 /tmp/zen-delegate-verify-repro.py` with the
  program in the shipped shape (set_value, focus, key with no
  ref, assert).
- Output: dom_act returned `{'ok': False, 'completed': 2, ...
  {'action_index': 2, ... 'verified_basis': 'stale-ref:
  element_missing', ... 'error': {'code': 'stale_ref', 'reason':
  'element_missing', 'selector': None, ... 'batch_stopped':
  True}}`. The batch stopped at action_index 2, the key, before
  any Enter dispatch. The set_value and focus actions completed
  (completed 2). Elapsed 273ms.
- Consequence on live: the run would type the test message into
  the field, focus it, then refuse the Enter and report
  stale-ref. The message would sit unsent in the scratch field,
  and the run would report FAIL with a misleading reason (the
  element is not missing, the action has no selector).

Fix shape (proposed, NOT landed in this task): write the Zen
program separately from the CDP builder, as section 5 phase 4
does: `dom_observe('two_vision_fixture.html?clone=zen', '#msg-input', 80)` and a
key action carrying `"ref": "#msg-input"`. The alternative fix
is backend side (skip revalidation for key actions, since a key
has no element to revalidate), which is a coordinator decision
because it changes the protocol for every caller, not only this
run. Either fix must be re-verified by the section 5 phase 0
gates before any live attempt.

### Finding B (BLOCKER): _verify calls sent_bubble_contains with the wrong arity, TypeError after the Enter is sent

Evidence, read from the code:

- scripts/zen_dom.py line 1296: `def sent_bubble_contains(self,
  text)` takes ONE argument, the message text. Every other
  caller in production passes one argument (scripts/dom_act.py
  lines 739 and 851; tests/test_zen_dom.py lines 799-800).
- scripts/zen_backend.py lines 450-451 and 455 call it with TWO
  arguments: `session.sent_bubble_contains(selector,
  assert_spec.get('text', ''))` and
  `session.sent_bubble_contains(selector, text)`.
- tests/test_p2_element_ref.py line 957 defines the fake as `def
  sent_bubble_contains(self, selector, text)`, two arguments, so
  the 15 unit tests pass while the live path is broken. The fake
  matches the backend call, not the real session.
- The key action in the (b1) batch IS a send action:
  element_ref.is_send_action returns True for a key Enter after
  a type in the same batch (verified live in the check below),
  so _verify takes the sent-bubble branch for it.
- dom_act does NOT wrap the per-action _verify call in
  try/except (zen_backend.py line 660 is a bare call; only the
  trailing after-observe is wrapped). A TypeError there
  propagates out of dom_act as an uncaught exception, so the
  program gets no dom_act result dict at all.

Repro, run on the VM 17:53:05 +07 (same fakes, except the
session's sent_bubble_contains was patched to the REAL
one-argument signature):

- Command: `python3 /tmp/zen-delegate-verify-repro.py` with the
  key action carrying ref '#c5-text' (the unit-test shape).
- Output, traceback in order: File
  ".../scripts/zen_backend.py", line 660, in dom_act,
  `verified, basis = self._verify(`; File
  ".../scripts/zen_backend.py", line 455, in _verify, `ok =
  session.sent_bubble_contains(selector, text)`; `TypeError:
  real_shape_sent_bubble_contains() takes 2 positional arguments
  but 3 were given`. The script also printed the signatures:
  real `(self, text)`, fake `(self, selector, text)`,
  is_send_action True. State at raise: field value 'hello',
  sent bubbles ['hello'], 3 desktop act calls already made.
- Consequence on live: the Enter WOULD be sent (the bubble
  exists in the fake state), but the run reports an exception
  instead of ok, and the program never reaches its trailing
  assert or its `assert_state(res.get("ok") is True)` line.
  Worse, the failure looks like a crash, not a verification
  failure, which misleads diagnosis. The fix is one line (drop
  the selector argument at both call sites, or change the
  session to accept it), plus a test that pins the real
  signature: the fake must define the one-argument form, or a
  test must assert inspect.signature of the real method. That
  test is missing today, which is how the mismatch shipped with
  green tests. The coordinator assigns the fix; this task does
  not land it.

### Finding C (GATE, not a bug): a Marionette opened tab on live windowed Zen may have a 0x0 viewport

Evidence, read from the docs (no live re-measurement in this
task, because measuring it needs the live Zen):

- docs/zen-dom-control-comparison.md section 3, Selenium plus
  geckodriver on live windowed Zen: the Marionette opened tab
  reports window.innerWidth and innerHeight 0,
  document.hasFocus false, elementFromPoint null at every point,
  even though the window is mapped, visible, and focused, and
  getBoundingClientRect returns correct rects. Element clicks
  fail with "Element could not be scrolled into view". The
  suspected cause is that Zen's own tab management never
  selects the Marionette opened tab, so Gecko never allocates
  it a viewport. Headless Zen passed the same steps, so this is
  a live windowed Zen quirk.
- Consequence for the live proof: if the scratch tab has no
  viewport, the delegate's screen point clicks are meaningless
  (the field rects exist in DOM but no point on screen maps to
  them), and _revalidate would likely fail on visible or
  interactive checks before any click. The procedure therefore
  gates on a viewport check (section 5, phase 2, step 2.4)
  BEFORE any input, and aborts the run if it fails. An abort
  there is a BLOCKED result, not a FAIL of the delegate: it
  proves nothing about the delegate either way, and the
  coordinator decides the next step (for example, opening the
  tab through Zen's own UI instead of Marionette, which is a
  bigger disturbance and needs its own approval).
- The 13:22:29 +07 live Zen run does not settle this: it used
  an EXISTING tab (Example Domain), not a Marionette opened
  one, and it dispatched no input.

### Finding D (LOAD BEARER): dom_observe harvests the CURRENT tab, so the scratch tab must be pre-selected

Evidence, read from the code:

- scripts/zen_backend.py _resolve_target lines 189-208 returns
  `session.tab_at(index)` for a matched tab. scripts/zen_dom.py
  tab_at and list_tabs switch to the requested handle, read it,
  then RESTORE the original tab (lines 600-690). After
  _resolve_target returns, the current tab is the original tab
  again.
- scripts/zen_backend.py dom_observe lines 251-253 then calls
  `session.harvest([scope])`, which evaluates JS in the CURRENT
  tab. So dom_observe on a target that is not current harvests
  the WRONG tab. The same current-tab dependence holds for
  _revalidate (locate_confirmed), _verify (verify_typed,
  focus_check, sent_bubble_contains), and the after-observe.
- The 13:22:29 +07 live run worked around this by switching
  Marionette to Example Domain BEFORE the run (13:21:42) and
  restoring Welcome! after (13:22:46). The step 9 log states
  the reason explicitly: dom_observe's tab_at restores the
  original tab, so the harvest reads the CURRENT tab.
- Procedure consequence (section 5, phase 3): before the
  program runs, a small driver switches the Marionette current
  tab to the scratch tab and verifies the current URL contains
  the fixture substring; after the program, the same driver
  restores the current tab to the owner's original tab by URL
  and verifies the current URL equals the original URL. The switch is
  visible in Zen's UI (risk R3), and the restore is part of
  cleanup, not an afterthought.

## 5. Live proof procedure (phases 0 to 7)

Run condition (updated 17:55 +07): the owner handed the machine
over at 17:55 and is not touching it. The original brief's ban on
live runs is lifted by COORD-CLICK-6 for this run only. If the owner returns to the machine mid-run, STOP at once (cancel latch
or Ctrl-C the driver), restore the user's tab, close the scratch tab,
record the aborted run, and do not resume without a new go-ahead.
All laptop work goes over SSH via ~/workspace/ssh-laptop.sh,
short commands only; any long job runs detached (setsid nohup ...
and disown) and is polled with short commands. Never run two Zen
drivers in parallel: Zen allows ONE remote session total, and a
second session fails or wedges the slot (finding C background).

Laptop paths used below: repo ~/computer-use-wayland,
cu.py ~/computer-use-wayland/scripts/cu.py, run dir
~/c5-zenproof-run/ (persistent home path, per the step 9 lesson:
do NOT trust /tmp persistence on the laptop for live-run
drivers). VM paths: this repo, runner
improvements/c5-zenproof-runs/c5-zen-delegate-run.py (to be
written by the runner, modeled on
improvements/c5-step9-runs/c5-heldout-fixture.py).

### Phase 0: gates on the VM, no live touch

- G0a: findings A and B fixed (section 4), fix commit recorded,
  then `python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec` returns 175 OK.
  FAIL means stop, no live attempt.
- G0b: program validation check (the exact phase 4 program,
  section 5 phase 4): `code_exec._validate_dom_actions` plus
  `dom_asserts.require_asserts` with available sent_bubble False
  must pass with no exception; is_send_program True. This check
  passed 17:53:36 +07 for the program text in this file; re-run
  it after any program edit, and refuse to run a program that
  fails it.
- G0c: `sha256sum tests/two_vision_fixture.html` on the VM must
  equal 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf.
- G0d: the run intent is fresh (c5-zen-delegate-r1 for run 1;
  r2, r3 for repeats) and the message is fresh
  (ZEN-DELEGATE-R1-IGNORE-TEST). A reused intent with the same
  target refuses the second send in one driver process (intent
  ledger, step 9 item 3), which would false-fail a repeat run.

### Phase 1: laptop as-found checks (SSH, short commands)

- P1.1: export HYPRLAND_INSTANCE_SIGNATURE from
  `ls /run/user/1000/hypr/ | head -n1` in the SSH session, then
  `hyprctl -j clients` and `hyprctl -j activewindow`. Record:
  Zen window address, workspace (expected ws1), geometry
  [x, y, w, h], and the active window address. If Zen is not on
  ws1 or not the active window, ABORT. Do not move windows.
- P1.2: record the current Marionette tab without changing
  anything visible: `python3
  ~/computer-use-wayland/scripts/zen_dom.py list`.
  It must exit 0 and list the tabs (titles and urls only, no
  content). Record the tab count, the current tab URL and title
  (the owner's tab, to restore in phase 6 by URL, never by
  handle: handles are ephemeral per session), and the full title
  list. If it fails with "another process already
  holds the Zen remote session", ABORT: the single session slot
  is held by someone else.
- P1.3: `ls -l /tmp/geckodriver` must exist (zen_dom.py default
  GECKODRIVER). If it is missing, ABORT and report it; do not
  install anything on the laptop without a coordinator decision.
- P1.4: `sha256sum
  ~/computer-use-wayland/tests/two_vision_fixture.html`
  must equal the manifest hash from G0c. If the laptop checkout
  is behind, sync it first (`git -C
  ~/computer-use-wayland fetch origin` then fast
  forward to the commit that holds this prep file) and re-check
  the hash. On mismatch after sync, ABORT.
- P1.5: no other live lane holds the machine: `ps aux | grep -E
  'session-driver|session_remote' | grep -v grep` must show no
  other session-driver, and `ls
  ~/.cache/agent-computer-use/*.lease` must show no live lease
  from another owner. If another lane is live, ABORT and wait;
  never run two live lanes at once (step 9 run 2 hit broker busy
  under contention).
- P1.6: confirm the handover still holds: if anything in P1.1
  to P1.5 shows the owner active on the machine (a changed
  active window, a new tab, typing), ABORT and re-check with the
  coordinator.

### Phase 2: open the scratch tab, viewport gate

- P2.1: transfer the tab driver to the laptop (scp with the
  same options as ~/workspace/ssh-laptop.sh, into
  ~/c5-zenproof-run/zen-tab.py), then verify its sha256 on the
  laptop matches the VM copy. Fallback transfer: git pull on the
  laptop if the driver is committed. Never type the driver in
  by hand.
- P2.2: run the driver: open a ZenSession, record the tab count
  and current URL, open a NEW tab (POST
  /session/{id}/window/new {"type": "tab"}), verify the tab
  count grew by exactly 1 and the new tab was actually made
  current (one explicit select if needed; if the new tab still
  is not current, refuse outright, no navigate, no close),
  navigate it to
  file://~/computer-use-wayland/tests/two_vision_fixture.html?clone=zen
  (POST /session/{id}/url), re-verify the current tab is still
  the new tab right after the navigate, wait for
  document.readyState complete (10s budget), verify the
  navigated URL contains 'two_vision_fixture.html?clone=zen'
  and the H1 text is 'Clone zen thread' (content confirmation
  that the clone JS ran; the document title is the static
  'Two-vision benchmark fixture' and is never a gate), then
  delete the session in finally. Expected: new handle recorded,
  tab count +1, URL contains the fixture substring, H1 'Clone
  zen thread', readyState complete. The driver must never
  navigate, type into, or click on any existing tab. Budget
  30s. On timeout or wrong URL/H1: close the new tab only if
  the current tab is the fixture tab by URL and by handle,
  delete the session, ABORT.
- P2.3: the driver also records the field rect: harvest
  ['#msg-input'] on the scratch tab and record the rect plus
  the window bounds. This is evidence only; the backend
  re-grounds at run time.
- P2.4 VIEWPORT GATE (finding C), same driver, before any
  input: evaluate in the scratch tab (a) window.innerWidth
  greater than 0 and window.innerHeight greater than 0, (b)
  document.hasFocus true, (c) document.elementFromPoint at the
  #msg-input center is non-null. ALL must pass. If any fails:
  ABORT the run, close the scratch tab, restore the current tab
  to the owner's tab, delete the session, and report BLOCKED
  (0x0 viewport), not FAIL. No input is sent on a failed gate,
  ever. Do not retry the gate in a loop.

### Phase 3: pre-select the scratch tab, read-only probe

- P3.1: run the tab driver with the switch action: switch the
  Marionette current tab to the scratch tab by URL (finding D),
  verify the current URL contains
  'two_vision_fixture.html?clone=zen' and the H1 text is 'Clone
  zen thread', delete the session in finally. Budget 30s. If the
  switch does not take effect, ABORT (close scratch tab,
  restore, report).
- P3.2: focus rule (C5-FOCUS-INCIDENT): in the SAME SSH call
  immediately before the probe, `hyprctl -j activewindow` must
  show the Zen window address from P1.1. If it shows anything
  else, STOP and do not send. Re-verify after any gap over 60s.
- P3.3: read-only probe program through the SAME transport as
  the send (this proves CU_DOM_BACKEND=zen reaches the driver
  before any input exists to lose):
  `dom_start()` then `snap = dom_observe('two_vision_fixture.html?clone=zen',
  '#msg-input', 80)` then print the snapshot. No dom_act, no
  input. Expected: ok, snapshot id zen-1, snapshot URL contains
  'two_vision_fixture.html?clone=zen', one element with ref
  '#msg-input'. The snapshot title is evidence only (the static
  'Two-vision benchmark fixture'), never a gate. If dom_observe
  fails, or the snapshot URL does not contain the fixture
  substring, ABORT: the backend is not reading the scratch tab
  (finding D) or the env did not propagate. If the env did not
  propagate, the fallback is the 13:22 shape: run the driver on
  the laptop inside `computer-use session` as `CU_CODE_EXEC=1
  CU_DOM_BACKEND=zen python3 <driver>`, with the driver invoking
  `scripts/cu.py code-exec` directly. Do not debug the transport
  live with an input program.
- P3.4: pre-checks via an eval driver on the scratch tab:
  window.__bubblePresent(MESSAGE) false,
  window.__sentBubbles() empty, document.getElementById
  ('msg-input').value empty. If the message is already present,
  ABORT: pick a fresh message and intent and restart from
  phase 2, never send into a dirty fixture.

### Phase 4: the send program

Exact program text (Zen form, NOT the CDP builder output; the
differences are findings A and D: scope on dom_observe, ref on
the key, target by URL substring, no role grounding loop
because Zen snapshots carry ref == selector with no role or
name enrichment):

```
dom_start()
snap = dom_observe('two_vision_fixture.html?clone=zen', '#msg-input', 80)
res = dom_act(snap, [
    {"type": "set_value", "ref": "#msg-input", "text": "ZEN-DELEGATE-R1-IGNORE-TEST", "scope": "two_vision_fixture.html?clone=zen", "observation_id": snap["snapshot"]},
    {"type": "focus", "ref": "#msg-input", "scope": "two_vision_fixture.html?clone=zen", "observation_id": snap["snapshot"]},
    {"type": "key", "ref": "#msg-input", "keys": ["Enter"], "scope": "two_vision_fixture.html?clone=zen", "observation_id": snap["snapshot"]},
    {"type": "assert", "selector": "#thread .bubble:last-child", "text": "ZEN-DELEGATE-R1-IGNORE-TEST", "timeout_ms": 3000, "scope": "two_vision_fixture.html?clone=zen", "observation_id": snap["snapshot"]},
])
print("dom_act ok", res.get("ok"), "completed", res.get("completed"), "ms", res.get("execution_ms"), "error", res.get("error"))
assert_state(res.get("ok") is True, "dom_act failed")
```

Note (Council 3 G1, amend 2): the program above is the recorded
RUN-1 program (message ZEN-DELEGATE-R1-IGNORE-TEST, no PROBE
print). The run-2 program in c5-zen-delegate-run2.py adds the
PROBE print after dom_observe (Redteam F2), which phase 4 gates
on. Copy run2.py, never copy this listing into a run: a program
copied from this listing would fail phase 4 after the send
('send program printed no snapshot line').

- P4.1: focus re-check in the SAME SSH call immediately before
  the send (same rule as P3.2). Then run the program from the
  VM runner through oneshot session-driver with
  `CU_CODE_EXEC=1 CU_DOM_BACKEND=zen` on the remote command
  line, intent 'c5-zen-delegate-r1', --wall-seconds 45. The
  program file on the laptop is mode 600. Expected wall 25-35s
  by analogy with held-out run 91 (33.3s) and the live (b1)
  runs (22-25s); budget 90s (the harness oneshot SSH timeout).
  Record the envelope verbatim (ok, elapsed_ms, error, log,
  wall_ms) into the run JSON on the VM.
- P4.2: expected result: dom_act ok True, completed 4, error
  None. Per-action expectations: set_value verified True with
  basis dom-value; focus ok True with basis
  no-dom-postcondition:focus (this is the exception-list path:
  _verify has no focus branch, so the focus action passes on
  sent plus received plus the no-dom-postcondition basis, not
  on focus_check; do NOT record it as a focus_check pass);
  key verified True with basis sent-bubble (after fix B); assert
  verified True with basis dom-value. Any other result is FAIL.
  Any exception (including TypeError) is FAIL, with the
  traceback recorded verbatim. No second send attempt in the
  same run: if the program fails after the Enter, do NOT re-run
  it with the same intent (the ledger would refuse it anyway);
  go to phase 5 checks to establish what actually happened,
  then decide with the coordinator.

### Phase 5: post-checks, retry refusal, delayed recount, P9

- P5.1: post-checks via the eval driver: __bubblePresent
  (MESSAGE) true, __sentBubbles() exactly [MESSAGE],
  msg-input value empty, __inputEvents at least 1. All must
  hold or the run is FAIL (failed-unverified), even if dom_act
  reported ok.
- P5.2: no-double-send on retry (step 9 gate item): read the
  pre-send bubble check again; it must be true, so the outcome
  is already-sent and the program is NOT re-run. Record
  bubbles_after_refusal, which must still be exactly [MESSAGE].
- P5.3: wait 10s, then delayed recount: __sentBubbles() filtered
  to MESSAGE must have count 1.
- P5.4: P9 evidence: `grim -g "<x>,<y> <w>x<h>" <workdir>/
  p9-zen-r1.png` on the laptop, geometry from the P1.1 Zen
  window bounds; copy the PNG to the VM and review it by sight.
  PASS only when the screenshot shows the green bubble with the
  message, the input empty, and the status 'sent:
  ZEN-DELEGATE-R1-IGNORE-TEST'. A P9 that cannot be captured
  (grim fails, geometry stale) is recorded as P9 FAILED with
  the cause, and the run is failed-unverified on evidence
  grounds even if the DOM checks passed.

### Phase 6: cleanup and restore

- P6.1: tab driver with the close action: close the scratch tab
  by URL (driver close action: switch current to the scratch
  tab by URL, DELETE /session/{id}/window), verify the tab
  count is back to the P1.2 as-found count, restore the current
  tab to the owner's original tab URL from P1.2, verify the
  current URL equals the original URL, delete the session in
  finally. Budget 60s.
- P6.2: verify Zen is alive: `hyprctl -j clients` shows the
  same Zen window address and geometry as P1.1; `python3
  scripts/zen_dom.py list` exits 0 (which also proves the
  session slot is free and the lock is released). If the slot
  is held (list fails with the lock message), run the kill-hung
  path (`python3 scripts/zen_dom.py kill-hung`) once, re-list,
  and record it; if it still fails, report it as an open item
  and do NOT restart Zen without a coordinator decision.
- P6.3: record the final window map and confirm it matches
  as-found except for the scratch tab being gone. The fixture
  file is never modified. Run artifacts stay in
  ~/c5-zenproof-run/ on the laptop and in the run JSON plus P9
  on the VM, both committed as evidence.

### Phase 7: record, commit, push

- P7.1: append section 10 (live results) to this file with the
  run JSON summary, the P9 verdict, the wall times, and the
  commit hashes of the fix and the runner.
- P7.2: commit with an explicit pathspec (this file, the run
  JSON, the runner, the drivers), push at once, verify with
  `git ls-remote origin todolist-push`. Never commit
  tests/realistic/clone1-batch3/results.json. Never use a bare
  `git commit` or `git add -A`.

Time budget for the whole live proof: about 10 to 12 minutes
wall (phases 1-3 about 5 minutes, phase 4 expected 25-35s with
a 90s budget, phase 5 about 1.5 minutes including the 10s
delayed wait, phase 6 about 2 minutes), plus phase 0 and phase
7 on the VM. These are budgets from analogous runs, not
measurements of this path.

## 6. Scratch target specification

- File: tests/two_vision_fixture.html in this repo, 2014 bytes,
  sha256 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf
  (C4 bench manifest). Opened as file://~/
  computer-use-wayland/tests/two_vision_fixture.html?clone=zen.
  The ?clone=zen query makes the fixture JS set the H1 text to
  'Clone zen thread' (the document title stays the static
  'Two-vision benchmark fixture') and the thread dataset to
  clonezen, which keeps this run distinguishable from the
  Chromium held-out run (?clone=1).
- Content: h1 'Clone zen thread'; #thread div (empty at open);
  #msg-input (input type text, placeholder Message, aria-label
  Message, autocomplete off); #send-btn (aria-label Send);
  #search-input (aria-label Search); #emoji-btn (aria-label
  Emoji); #status div (empty at open). Behavior: Enter in
  #msg-input appends a .bubble div with the text, sets status
  to 'sent: <text>', clears the input, refocuses the input.
  Verification hooks: window.__sentBubbles() returns the bubble
  texts; window.__bubblePresent(text) checks membership;
  window.__inputEvents counts input events on #msg-input.
- Position: a NEW tab in Zen on ws1, appended last in the tab
  strip. The Zen window stays where it is (full width on ws1
  as found in P1.1), never moved, never resized, never closed.
  No other window is touched. The scratch tab is the Marionette
  current tab only from phase 3 to phase 6, and only for this
  run.
- Message and intent: message 'ZEN-DELEGATE-R1-IGNORE-TEST'
  (run 1; R2, R3 for repeats, always with the IGNORE-TEST
  marker); intent 'c5-zen-delegate-r1' (fresh per run).
- Lifecycle: opened in phase 2, used in phases 3-5, closed in
  phase 6. Never navigated to any other URL. No existing tab is
  navigated, typed into, clicked, or closed at any point.
- Cleanup: section 5 phase 6. The only durable traces are the
  run artifacts (run JSON and P9 on the VM, driver scripts and
  STATE observations on the laptop) plus this log. The fixture
  file is read-only throughout.

## 7. Verification checklist (for the runner, tick each line with its evidence)

Gates (phase 0):
- [ ] G0a: fix B landed, commit hash recorded, unit suites 175 OK re-run.
- [ ] G0b: program validation check passes for the exact phase 4 program text.
- [ ] G0c: fixture sha on the VM matches the manifest hash.
- [ ] G0d: fresh intent and fresh message for this run number.
Laptop as-found (phase 1):
- [ ] P1.1: Zen on ws1, address and geometry recorded, activewindow is Zen.
- [ ] P1.2: zen_dom.py list exits 0; tab count and owner's current tab recorded.
- [ ] P1.3: /tmp/geckodriver exists on the laptop.
- [ ] P1.4: fixture sha on the laptop matches the manifest hash.
- [ ] P1.5: no other session-driver and no other live lease.
- [ ] P1.6: handover still holds (no sign of the owner active).
Scratch tab (phase 2):
- [ ] P2.2: new tab opened and made current (tab count +1), navigated URL contains the fixture substring, H1 'Clone zen thread', readyState complete.
- [ ] P2.3: #msg-input rect recorded.
- [ ] P2.4: viewport gate passes (innerWidth and innerHeight
  greater than 0, hasFocus true, elementFromPoint non-null), or
  the run is BLOCKED with no input sent.
Probe (phase 3):
- [ ] P3.1: Marionette current is the scratch tab (URL verified).
- [ ] P3.2: activewindow is Zen in the same SSH call before the probe.
- [ ] P3.3: read-only probe ok, snapshot URL contains the fixture substring, count 1, ref '#msg-input' (snapshot title is evidence only).
- [ ] P3.4: pre-checks pass (bubble absent, bubbles empty, input empty).
Send (phase 4):
- [ ] P4.1: focus re-checked in the same SSH call; envelope recorded verbatim.
- [ ] P4.2: dom_act ok True, completed 4, error None; set_value
  dom-value True; focus ok True with no-dom-postcondition:focus;
  key sent-bubble True; assert dom-value True.
Post-checks (phase 5):
- [ ] P5.1: bubble present, bubbles exactly [MESSAGE], input empty, input_events at least 1.
- [ ] P5.2: retry outcome already-sent, bubbles still exactly [MESSAGE], no re-run.
- [ ] P5.3: delayed count 1 after 10s.
- [ ] P5.4: P9 reviewed by sight, PASS (bubble, empty input, status line).
Cleanup (phase 6):
- [ ] P6.1: scratch tab closed, tab count back to as-found, current tab restored to the owner's tab (URL verified).
- [ ] P6.2: Zen alive, same window address and geometry, zen_dom.py list exits 0 (slot free).
- [ ] P6.3: final window map matches as-found except the scratch tab gone.
Record (phase 7):
- [ ] P7.1: section 10 written with the run JSON summary, P9 verdict, wall times, commit hashes.
- [ ] P7.2: committed with an explicit pathspec, pushed, verified with git ls-remote.

## 8. Risk register (running while the owner uses the machine)

The run condition for this proof is the handover: the owner
handed the machine over at 17:55 +07 and is not touching it.
The risks below are written for the case where that condition
breaks (the user returns mid-run) and for the disturbances the run
causes even under a handover. The procedure aborts on any of
them rather than pushing through.

- R1 Focus steal. begin_batch focuses the Zen window through
  hyprctl. If the owner is on another workspace or another
  window when the program runs, the focus call yanks the user to
  ws1 Zen. Mitigation: P1.1 and the P3.2/P4.1 same-call
  activewindow checks; abort unless Zen is already active.
  If the user returns mid-run, stop at once (section 5 header).
- R2 Real pointer clicks at screen points. The delegate moves
  the real pointer and clicks at the field center, and types
  real keystrokes. If the owner moves the mouse, clicks, or
  types during the batch, input can land in the user's UI instead of
  the scratch field. The batch is short (program elapsed
  123-161ms on the CDP path; Zen is unmeasured), but the race
  is real between the fresh observation and the act. Mitigation:
  handover window only; one batch only; the cancel latch
  (Escape or `computer-use cancel`) stops the driver; the
  typed text is a marked test string, never the user's content.
  Residual: a click that lands on the user's tab while the user is
  interacting is the worst case, which is why the handover
  condition is load bearing, not decorative.
- R3 Visible tab switch. Opening the scratch tab and switching
  the Marionette current tab to it changes what Zen shows;
  during the run the user's Zen displays the fixture, not the user's tab.
  Mitigation: restore immediately in phase 6 and verify the
  current URL; keep the visible disturbance to the run
  duration (about 10 minutes wall, most of it checks, the
  visible switch itself only phases 3-6).
- R4 Typing into the wrong field. If the field rect moved
  between observe and act, _revalidate refuses (stale-ref) or
  re-grounds once on the fresh rect when the identity is
  confirmed by the distinguishing state. The typed text is a
  marked test string. Residual: the re-ground path acts on a
  moved rect once; the mitigation is the pre-check that the
  scratch tab is current and the viewport gate.
- R5 A send escapes the fixture. The only send in the program
  is the test message into the local file fixture, never into a
  messenger or any live chat. The intent ledger refuses a
  second send under the same intent in one driver process, and
  the phase 5 retry check refuses a re-run when the bubble is
  already present. No other tab is ever a target.
- R6 Single remote session leak. Zen allows ONE remote session
  total across BiDi and Marionette. Every driver in this
  procedure deletes its session in finally. If a driver dies
  without deleting, the slot leaks and only a Zen restart
  clears it (21/11 precedent: a hung client held it 1h51m).
  Mitigation: one driver at a time, session delete in finally,
  phase 6 verifies the slot is free with a fresh list call,
  kill-hung exists as a one-shot recovery. Never restart Zen
  without a coordinator decision.
- R7 Marionette hang wedges the session. A hang on one tab
  switch stops the scan and only a restart clears it (F3b Arm
  E). Mitigation: timeouts on every step (30s geckodriver
  status, 30s ZenDom timeout, 45s wall-seconds, 90s SSH
  timeout), abort on the first hang, never retry a hung session
  in a loop.
- R8 Screenshot observation captures the user's screen. begin_batch
  screenshots the Zen window through observe. Mitigation: the
  observation runs only after the scratch tab is current, so
  the capture shows the fixture; observation files stay in
  STATE (mode 0700) on the laptop. If the activewindow check
  fails, no observation runs at all.
- R9 Broker and session contention. Step 9 run 2 hit broker
  busy under a concurrent lane. Mitigation: P1.5 checks for
  other session-drivers and leases before starting; refuse fast
  on busy and retry once after the holder finishes.
- R10 The 0x0 viewport (finding C). The fresh tab may have no
  viewport, which makes screen-point clicks meaningless.
  Mitigation: the P2.4 gate aborts before any input; an abort
  there is BLOCKED, not FAIL.
- R11 The code findings (A and B). If unfixed, the run fails
  (A: stale-ref before the Enter, message left unsent in the
  field; B: TypeError after the Enter is sent, run reports an
  exception while the bubble exists). Mitigation: phase 0 gates
  require both fixed and re-verified on the VM first. Never
  debug live.
- R12 The user's work loss. None is expected by design: no navigation
  of the user's tabs, no typing into the user's tabs, no closing of the user's tabs,
  no browser restart, no profile change. The only tab opened
  and closed is the scratch tab. If any step touches one of the user's
  tabs by mistake, STOP, record exactly what happened, restore
  the user's tab, and report it before doing anything else.

## 9. Evidence appendix (Lauren Tan standard: command, output, commit hash, time)

Prep evidence, all on the VM unless stated:

- `git fetch origin` then `git rev-parse HEAD` and `git
  rev-parse origin/todolist-push`, 17:49:29 +07: both
  05140c10d180ce7d26548df0f5b6f9c4d431e316. Plain `git pull
  --ff-only` failed ("Cannot fast-forward to multiple
  branches"); explicit fetch showed nothing new.
- `python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref`, 17:49:52 +07: Ran 115 tests in
  0.181s, OK.
- `python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec`, 17:49:55 to
  17:50:08 +07: Ran 175 tests in 12.449s, OK, wall 12.651s.
  Individually: test_zen_pointer 15 OK in 0.014s,
  test_p2_element_ref 100 OK in 0.132s, test_code_exec 60 OK in
  12.494s.
- `sha256sum tests/two_vision_fixture.html`, 17:50 +07:
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf,
  matching the C4 bench manifest and deploy-manifest.json.
- Repro run 1 (finding A), `python3
  /tmp/zen-delegate-verify-repro.py`, 17:52:52 +07, elapsed
  273ms: dom_act ok False, completed 2, action_index 2
  stale-ref element_missing, selector None, batch stopped
  before any Enter dispatch. Script at
  /tmp/zen-delegate-verify-repro.py (not committed; it is a
  prep scratch file).
- Repro run 2 (finding B), same command, 17:53:05 +07:
  TypeError at zen_backend.py:455, sent_bubble_contains called
  with two arguments against the real one-argument session,
  propagating out of dom_act line 660. State at raise: field
  'hello', bubbles ['hello'], 3 desktop act calls made.
- Builder output check, 17:53:15 +07: the shipped (b1) key line
  carries no ref; dom_observe is called with no scope.
- Program validation check, 17:53:36 +07: the section 5 phase 4
  program passes _validate_dom_actions and require_asserts with
  no exception; is_send_program True; is_send_action True.
- Commit record for this file: to be filled in section 10
  after the commit (commit hash, push verification via
  git ls-remote).
- No live run was made in the prep task. No Zen tab was opened,
  switched, or navigated. No SSH session to the laptop was
  opened. No input was sent anywhere.

## 10. Live results: run 1 aborted in phase 1, two new blockers, STOPPED per instruction

### 10.1 What changed after section 9 was written

- 17:55 +07: the owner handed the machine over and stopped
  touching it. COORD-CLICK-6 lifted the original brief's ban on
  live runs for this task only and ordered the live proof to run
  per the section 5 procedure, with the standing condition: if
  a new risk appears during the run, stop, record it, and report
  back instead of forcing the run.
- Correction to section 4: the sentence "The coordinator
  assigns the fix" is superseded. Finding B was fixed by
  W-ZENPREP itself under the follow-up order, because phase 0
  gate G0a requires it before any live attempt. Fix commit
  161de2a, see 10.3.
- Correction to section 0: the prep file now also records the
  live attempt and its stop, per the follow-up order.

### 10.2 Commit incident on the prep commit (rule violated, no content lost)

- The prep commit cb741fe (17:58:44 +07) was made with a bare
  `git commit` (explicit `git add` only). It swept two files
  another worker had staged in the shared checkout:
  docs/brief-template.md (+7 lines, a J21 workspace-switching
  note) and docs/zen-error-fix-todolist-20261121.md (1
  insertion, 1 deletion). The task brief forbids a bare git
  commit; this was my error, and it is the shared-checkout
  hazard from the workspace log (a plain commit sweeps another
  worker's staged-but-uncommitted file).
- No content was lost: both diffs are preserved verbatim in
  cb741fe, and the working tree kept the owners' unstaged
  parts. No history rewrite was done: another worker pushed
  44b9a80 on top of cb741fe within a minute, so a reset would
  have diverged the shared branch for a larger harm than the
  incident itself.
- Rule going forward, applied to every later commit in this
  task: `git add` with an explicit pathspec AND `git commit -m
  ... -- <explicit pathspec>`, so only the named files commit.
  Verified: the fix commit 161de2a and the run kit commit
  2d1dc82 each contain exactly their intended files.

### 10.3 Finding B fixed, tests-first (gate G0a)

- Failing-first test added to tests/test_zen_pointer.py
  (RealSignatureTests, 2 tests): one pins the real signature
  of ZenSession.sent_bubble_contains to (self, text) via
  inspect.signature; the other drives the (b1) program through
  the delegate against a RealShapeFakeSession with the real
  one-argument form. Run 18:00:02 +07, before the fix: 2 tests,
  FAILED (errors=1), TypeError at zen_backend.py:455, the exact
  failure from the prep repro.
- Fix: scripts/zen_backend.py lines 450-451 and 455 drop the
  selector argument (sent_bubble_contains now takes the text
  only); tests/test_p2_element_ref.py line 957, the fake, is
  fixed to the one-argument form with a comment naming finding
  B. No other caller used the two-argument form (grep: only
  the two backend call sites; dom_act.py and test_zen_dom.py
  already pass one argument).
- Suites after the fix, 18:00:08 to 18:00:21 +07: `python3 -m
  unittest tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec tests.test_zen_dom tests.test_dom_act
  tests.test_step5_p1p5` returned Ran 275 tests in 12.868s, OK
  (zen_pointer 17, p2_element_ref 100, code_exec 60, plus
  zen_dom, dom_act, step5_p1p5). Wall 13.124s.
- Commit 161de2a988d7e1568a759271e4b177c0ee32c129, pushed,
  verified with git ls-remote (origin/todolist-push equals
  161de2a at push time). Finding A needs no code change: the
  section 5 phase 4 program is written in Zen form (scope on
  dom_observe, ref on the key), and it passed
  code_exec.validate_program on the VM at 18:02:37 +07 (both
  the send program and the probe program).

### 10.4 Run kit (gate G0b)

- Commit 2d1dc82a77748326818d1509c769eeb0fc738734, pushed,
  verified with git ls-remote. Two files:
  improvements/c5-zenproof-runs/c5-zen-delegate-run.py (VM
  runner, 408 lines) and improvements/c5-zenproof-runs/zen-tab.py
  (laptop tab driver, 236 lines). Both pass py_compile; both
  programs pass code_exec.validate_program (18:02:37 +07).
  The runner reuses Harness.ssh over the mux and a oneshot
  session-driver with CU_DOM_BACKEND=zen on the remote command
  line; the driver opens one ZenSession per subcommand and
  deletes it in finally.

### 10.5 Run 1: aborted in phase 1, 18:02:53 to 18:02:57 +07

- Command: `python3
  improvements/c5-zenproof-runs/c5-zen-delegate-run.py`, run
  from the repo root on the VM.
- Result JSON (improvements/c5-zenproof-runs/run-1.json, same
  record as /tmp/c5-zenproof-1/run-1.json, minified):
  outcome error, error "active window is not Zen
  (0x56307e202df0); aborting", cleanup skipped, wall_ms
  3473.8, model_calls 0. The runner exit code was 1 (the
  command pipeline reported the tail exit code instead; the
  JSON outcome is authoritative).
- What happened: phase 1 found the Zen window in the clients
  list, then the activewindow check (procedure P1.1) found the
  active window is 0x56307e202df0, not Zen, and aborted before
  any tab was opened, any session was started, or any input
  was sent. No scratch tab exists. No input was sent anywhere.
  The abort is the procedure working as designed, not a
  failure of the delegate.
- Checklist status for run 1: G0a PASS (fix landed, 275 OK),
  G0b PASS (both programs validate), G0c PASS (fixture sha on
  the VM matches), G0d PASS (fresh intent and message), P1.1
  FAIL (active window is not Zen, abort). All later boxes are
  untested, not failed.

### 10.6 Read-only findings after the abort (no live input, SSH reads only)

Window map, 18:04:02 +07, `hyprctl -j clients` (grep for
address, class, title, workspace name):

- 0x56307e21b2d0: org.omarchy.herdrdrop, special:herdrdrop
  (floating terminal).
- 0x56307e4c2f90: brave-origin, ws2, title "Chat - mei - Brave
  Origin" (mei's live chat window).
- 0x56307e202df0: chromium, ws2, title "Chat - mochi -
  Chromium", the ACTIVE window (confirmed twice: the run 1
  abort at 18:02:53 and a direct activewindow read at
  18:03:11, both show the same address).
- 0x56307e2771d0: zen, ws1, title "Chat - Muse - Zen
  Browser" (the owner's Zen, on ws1 as expected, not active).

Other live lanes, 18:03:40 +07: `ps aux | grep -E
'session-driver|session_remote' | grep -v grep` shows NO
session-driver running. The relay serve process is up
(session_remote.py serve, PID 3913, since 17:19) and idle, and
mcp_bridge.py (PID 1911, since 17:14). Lease files in
~/.cache/agent-computer-use/ are all stale (timestamps 16:04
to 16:31, from the step 9 runs), with no live driver holding
them.

Fixture on the laptop, 18:03:43 +07: `sha256sum
~/computer-use-wayland/tests/two_vision_fixture.html`
returned 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf,
matching the manifest. The laptop checkout is ready on this
point.

### 10.7 New risk R13 (STOP reason 1): the active window belongs to another live agent lane

- The active window is mochi's Chromium chat on ws2, and mei's
  Brave chat is also live on ws2. Both replaced the clones at
  17:55 (mei for clone1, mochi for clone2, same procedures under
  new names). Focusing the Zen window would switch the visible
  workspace from ws2 to ws1, away from two live agent lanes.
- The procedure gate P1.1 exists for exactly this: never yank
  focus while someone else works. The handover covers the owner, not the mei and mochi lanes. Whether mochi's work is
  CDP-driven (workspace switches harmless) or desktop-input
  driven (a focus switch redirects its clicks) was not verified,
  and verifying it would itself mean probing another lane's live
  session, which is out of scope for this worker.
- Decision needed from COORD-CLICK-6: either schedule a run
  window where the mei and mochi lanes are idle, or authorize
  the focus switch explicitly after checking with those lanes,
  or run the proof with the P1.1 gate relaxed by a coordinator
  decision recorded here. W-ZENPREP does not relax the gate
  unilaterally.

### 10.8 New risk R14 (STOP reason 2): geckodriver is missing from the whole laptop

- 18:03:43 +07: `ls -l /tmp/geckodriver` returned "No such
  file or directory". 18:04:04 +07: `which geckodriver` found
  nothing; no binary at ~/geckodriver*,
  ~/.local/bin/geckodriver, /usr/local/bin/geckodriver,
  or /opt/geckodriver; `find ~ -maxdepth 3 -name
  '*gecko*'` returned nothing. The only geckodriver reference
  on the laptop is the test script's GECKO = "/tmp/geckodriver"
  constant.
- scripts/zen_dom.py defaults GECKODRIVER to /tmp/geckodriver,
  and ZenSession starts it with subprocess.Popen. With no
  binary, no Marionette session can start at all: the tab
  driver, the probe, and the send would all fail at session
  creation with FileNotFoundError. The 13:22:29 +07 live Zen run
  used /tmp/geckodriver, which has since vanished, consistent
  with the step 9 lesson that /tmp does not persist on the
  laptop.
- Decision needed from COORD-CLICK-6: source a geckodriver
  binary for the laptop at a PERSISTENT home path (not /tmp)
  and point ZEN_GECKODRIVER at it, or restore the /tmp copy
  with the knowledge that it can vanish again. Installing a
  binary on the laptop is outside this run's mandate, so
  W-ZENPREP stopped instead of installing one.

### 10.9 Procedure bug found: the P1.5 lease check is too strict

- The procedure's P1.5 says abort when any *.lease file exists
  under ~/.cache/agent-computer-use/. The 18:03:40 +07 read
  shows stale lease files from 16:04 to 16:31 (step 9 runs)
  with no live driver behind them. As written, P1.5 would
  false-abort every future run on these leftovers.
- Fix for the next attempt (runner change, not yet landed):
  drop the lease-file existence check; decide liveness from
  the ps check (no session-driver process) plus the relay
  state, and treat a lease file as stale unless a live driver
  holds it. The run 1 abort happened before P1.5, so this bug
  did not affect run 1; it is recorded here so the next run
  does not trip on it.

### 10.10 What the coordinator must decide (three items, in order)

1. Run window: schedule the proof when the mei and mochi lanes
   are idle, or authorize the ws2 to ws1 focus switch
   explicitly (R13). Until then, do not re-run: the P1.1 gate
   will abort again on the same active window.
2. Geckodriver: source the binary at a persistent laptop path
   and set ZEN_GECKODRIVER, or restore /tmp/geckodriver (R14).
   Without it, phase 2 cannot even open its first session.
3. Runner fix: land the P1.5 correction (liveness from ps plus
   relay state, not lease file existence) before the next
   attempt, so stale leases do not false-abort it.

### 10.11 Bottom line (no self-grading)

- The Zen pointer delegate remains unit proven only (175 OK
  at prep, 275 OK after the finding B fix). The live proof was
  NOT run, NOT passed, and NOT failed: run 1 aborted in phase
  1 on a safety gate, before any input, with zero disturbance
  (no tab opened, no focus taken, no input sent). The two
  blockers (R13 active window belongs to mochi, R14 no
  geckodriver on the laptop) are measured facts with commands,
  outputs, and times above, not guesses. The procedure, the
  fix, the run kit, and the aborted run are all committed and
  pushed; the next attempt needs the three decisions in 10.10.

### 10.12 Time log, continued

- 17:58:40 +07, T+9m: prep file finished (877 lines, 0 em or
  en dashes, owner named only as the owner throughout).
  Commit cb741fe 17:58:44 +07, pushed, verified with git
  ls-remote. Commit incident recorded in 10.2.
- 18:00:02 +07, T+11m: failing-first RealSignatureTests, 1
  error (TypeError at zen_backend.py:455). Fix applied.
  18:00:08 to 18:00:21 +07, T+11m to T+12m: 275 tests OK.
  Commit 161de2a, pushed, verified with git ls-remote.
- 18:02:31 +07, T+13m: run kit files compile; both programs
  pass code_exec.validate_program (18:02:37 +07). Commit
  2d1dc82, pushed, verified with git ls-remote.
- 18:02:53 to 18:02:57 +07, T+13m: run 1 aborted in phase 1,
  wall 3.5s, outcome error, no input sent.
- 18:03:11 to 18:04:04 +07, T+14m to T+15m: read-only checks
  (active window, clients, live processes, leases, fixture
  sha, geckodriver search). R13 and R14 established. STOP
  decision taken per the follow-up order: do not force the run.
- 18:04:29 +07, T+15m: run-1.json record verified identical
  to the runner output (same parsed JSON).
- This section written and committed after that. Commit hash:
  recorded in the git log for this file (git log --
  improvements/w-zen-delegate-liveproof-prep.md); the push is
  verified with git ls-remote, and the exact hash is reported
  to COORD-CLICK-6 in the handoff.
