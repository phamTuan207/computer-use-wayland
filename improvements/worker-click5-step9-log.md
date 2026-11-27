# Worker C5-STEP9 log: A1/S3/CB-EXEC merged prototype (b1 landing first)

Owner: the owner. Coordinator: COORD-CLICK-5. Repo
~/workspace/computer-use-wayland, branch todolist-push. This worker
did NOT do the S2 flip, the input fix, the P2 work, or step 8, so
this is independent work. No em dash or en dash anywhere in this
file. No personal info. Wall-clock Asia/Ho_Chi_Minh plus elapsed
time on every entry.

## 0. Task and starting point

- Task received 15:31 +07, Sun 2026-11-22 (T+0m). VM HEAD 0b59d9f
  at start.
- Final direction improvements/worker-click3-final-direction-log.md
  (commit e05fc58), section 3 step 9: A1/S3/CB-EXEC merged
  prototype, gate is snapshot/execute/verify end to end on one
  live ws2 clone chat plus held-out tasks, with the wedged-session
  recovery protocol specified and proven, and a destructive-action
  test proving no double-send on retry.
- (b1) landing spec as CORRECTED:
  docs/batch12-task2-b1-landing-spec-20261122.md on origin/main
  (fix commits 3962400 and eab0228 per batch 13 task 2 review
  F1-F13). Coordinator decision recorded here: option A
  (standalone focus action). The task brief orders the (b1) shape
  as set_value plus focus plus CDP Enter as a first-class shape,
  which is option A; option B (focus field inside set_value) is
  not built.
- Step 8 log improvements/worker-click5-step8-log.md (commit
  4eebc15): broker transport is the path (session_remote.py start
  --wait 300, broker_attempt); per-batch spawn deleted;
  session_cmd/attempt_session are loud stubs that raise.
- Focus rule (C5-FOCUS-INCIDENT, commit 2d198c4, section 7, read
  in full before any live run): verify `hyprctl -j activewindow`
  in the SAME SSH call immediately before each keystroke batch;
  re-verify after any gap over 60s; use only
  `hyprctl dispatch 'hl.dsp.focus({ window = "address:0x..."})'`;
  never the string dispatcher form; if focus errors or the window
  is wrong, STOP, do not send the key. Prefer CDP-only work with
  NO keystrokes. Laptop SSH only via ~/workspace/ssh-laptop.sh;
  long jobs detached (setsid nohup ... & disown), short checks
  only. Clone2-watch holds run :11:56, :26:56, :41:56, :56:56
  (hold about start+1m to start+2m40s); verify live, never rely
  on the schedule. LESSON: do NOT trust /tmp persistence on the
  laptop for live-run drivers; use persistent paths
  (~/c5-step9-run/) with copies on the VM. `computer-use act`
  needs the persisted STATE observation file, not observe stdout.
- Window map (re-list each run; verified live 15:21 +07 per the
  brief): ws1 Zen 0x557052b62dd0 (PID 496121) [2509, 914]
  [1863, 1176] full width; ws2 Brave 0x55705383d420 (PID 1185797)
  [3448, 914] [901, 1176]; ws2 Chrome 0x5570538ed160 (PID 8059)
  [2533, 914] [901, 1176]. Brave/Chrome classes are
  brave-/chrome-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default.
  hyprctl needs HYPRLAND_INSTANCE_SIGNATURE set in the SSH
  session (from /run/user/1000/hypr/). Do NOT move windows back
  unprompted. Test messages go into the clone1 and clone2
  threads ONLY. Relay: PID 1196429, loaded hash d490f369f6b7,
  head 1b5a6e6, state finished, owner c5-step8-drill (verify live
  before the first live run; the relay has no auto-restart,
  Restart=no).
- Session-level pill: BLOCKED on the CB-10 precondition. Do NOT
  touch the overlay server or the pill.

## 1. Time log

- 15:31 +07, T+0m: task received. Read the final direction
  (sections 1-3, step 9), the corrected (b1) spec in full
  (origin/main), the step 8 log in full, the FOCUS-INCIDENT
  section 7, the input-fix log sections 7.1-7.5, the input-invest
  log sections 2-3, the flip log section 5, the contract
  (docs/layer0-cbexec-contract.md sections 0-2), and the code:
  scripts/cdp.mjs (641 lines), scripts/dom_asserts.py (227),
  scripts/code_exec.py _validate_dom_actions and _api_dom_act
  and run(), scripts/cu.py browser whitelists and CodeExecBackend
  and code-exec command, scripts/s2_flip_live.py build_program,
  build_program_set_value, focus_enter, send_browser,
  scripts/zen_backend.py (delegate, dom_observe, _screen_point,
  dom_act), scripts/zen_dom.py check_viewport_geometry,
  scripts/element_ref.py, scripts/dom_act.py ledger,
  tests/cdp_validation.mjs, tests/test_s2_flip_wiring.py,
  tests/test_p2_element_ref.py (ValidatorLimitationTests,
  NoPointerDelegateTests).
- Baselines before any change: node tests/cdp_validation.mjs 3
  oks; python3 -m unittest tests.test_s2_flip_wiring 12/12 OK.
- Tests-first commit 05c11b9: (b1) failing-first tests
  (cdp_validation.mjs focus suite, wiring landed-program plus
  send-requires-focus plus whitelist-sync tests). Verified
  failing for the right reasons: cdp focus rejected as
  'unsupported action'; wiring 5 failures (no focus in the
  builder, no focus rule, no focus in the whitelists). Two
  test bugs found and fixed while proving the anchor: the
  set_value fake page lacked bare innerWidth/innerHeight
  globals (the visibility check reads them bare; ReferenceError
  inside the expression's try), and the after-snapshot replaces
  __agentCu, so the test holds the element reference directly.
- Code landing commit dc8449b, pushed, verified via
  git ls-remote (dc8449b6a4e0d80d5b5c18d54b540305c7d5b51a).
  After landing: node tests/cdp_validation.mjs 11 oks;
  test_s2_flip_wiring 19/19 OK; test_step5_p1p5 plus
  test_dom_act 75 OK; test_code_exec plus test_first_action
  plus test_session_driver plus test_p2_element_ref 268 OK.
  grep for LAPTOP_FOCUSENTER/focus_enter in scripts/ and tests/
  returns nothing (only a stale .pyc matches).

## 2. (b1) landing record, including the F7 decision

- Coordinator decision: option A (standalone focus action).
  The task brief orders the (b1) shape as set_value plus focus
  plus CDP Enter as a first-class shape, which is option A.
- F7 DECISION (recorded explicitly, as the task requires):
  helper Enter params vs landed key() params. The /tmp helper
  (improvements/s2-flip-b1-runs/c5-focusenter.mjs) sends code
  'Enter' on BOTH keyDown and keyUp, and text '\r' on keyDown
  ONLY (its keyUp carries no text). The landed key()
  (scripts/cdp.mjs:390-414) NEVER sends a `code` field for any
  key; it sends key, modifiers, windowsVirtualKeyCode, and
  nativeVirtualKeyCode only, and it sends the SAME params
  object, including text '\r', for BOTH keyDown and keyUp
  (lines 411-412). DECISION: key() is NOT changed. Both
  differences are harmless: the composer keys off e.key, and
  browsers ignore text on keyUp. Evidence: the landed key()
  Enter already sent 5/5 live on Brave (fill plus Enter, flip
  and reopen runs) and on scratch tabs (T2, input-fix log
  section 7.2). The decision is also recorded as a comment in
  the cdp.mjs focus branch. No silent key() change was made.
- What landed (commit dc8449b, 5 files, 98 insertions, 50
  deletions):
  - scripts/cdp.mjs: 'focus' in the action whitelist and the
    element-action list; focus branch after set_value (one
    Runtime.evaluate: unavailable checks, e.focus(),
    activeElement proof, zero Input methods). No change to
    key(), set_value, or fill.
  - scripts/code_exec.py: 'focus' in allowed and
    element_actions.
  - scripts/cu.py: 'focus' in the browser allowed set and the
    browser element-action check.
  - scripts/dom_asserts.py: 'focus' ASSERTS entry
    (focus_check, mandatory) plus the send-requires-focus rule
    in require_asserts (a send key with no preceding
    focus-establishing action raises DomAssertError; focus after
    the Enter does not satisfy it; fill is the explicit
    exception because it focuses internally through its click).
  - scripts/s2_flip_live.py: build_program_set_value emits the
    landed 4-action program [set_value, focus, key Enter,
    assert bubble] with P2 stamps on all 4 and the focus on the
    same composer ref as set_value; focus_enter and
    LAPTOP_FOCUSENTER removed; CB-1 for set_value is input_sent
    completed >= 3, target_received completed >= 1, verified =
    V12 found; phase-split 'focus-enter' bucketing and the
    --set-value/--chromium-set-value help texts updated.
- The old 2-action program shape is removed, not kept
  alongside: there is exactly one (b1) program shape.

## 3. Stall investigation (prototype first target)

- Question: the Chromium Input stall (Input.dispatchMouseEvent
  timeout, 5002-5003 ms, cause of the original flip's Chromium
  0/5). Prior state from the logs: D-B1 proved dispatchKeyEvent
  answers in 2 ms on the stuck tab while dispatchMouseEvent
  times out (input-fix log 7.1); cause 3.2 (background tab) is
  KILLED (the tab was active throughout); activation
  (Target.activateTarget plus Page.bringToFront) unstuck the tab
  ONCE then never again (0/5 runs plus 0/5 probes after, (a1)
  dead); workspace occlusion alone is NOT sufficient (the
  scratch tab accepted fill twice on the same inactive
  workspace). The deciding test the invest log prescribed (switch
  to workspace 2, re-run bare mouseMoved) was never run.
- Method (bounded, 15:44-15:48 +07): probe script
  improvements/c5-step9-runs/c5-stall-probe.mjs (copy on the
  laptop at ~/c5-step9-run/c5-stall-probe.mjs): fresh CDP
  session per run, Runtime.evaluate baseline, composer ground,
  key-event control, then bare mouseMoved at the composer center
  (286.5, 1103), 5 s timeout. Modes: reproduce, click (press
  plus release after the move), press-first (press/release
  before any move), scratch (fresh tab control), activate
  (not run: the (a1) evidence already kills it, and the
  press-first result below answers the same question more
  cheaply). As-found conditions verified live before the first
  run: Zen ws1 active, Chrome ws2 inactive, clone2 tab
  D1374C7C994D3DA72678E20C7FD099A0 (the same tab as the
  original stall). The :41:56 watch hold was waited out (the
  reproduce run started after it cleared, ws1 verified active).
- Results (11 probe runs, 15:44-15:48 +07):
  - Batch 1: reproduce mouseMoved 4 ms OK; reproduce mouseMoved
    TIMEOUT 5000 ms; click mode mouseMoved TIMEOUT 5001 ms,
    then mousePressed 2 ms OK, mouseReleased 2 ms OK,
    focus_after_click true (the composer gained focus, so the
    click WORKED despite the timed-out move); scratch fresh tab
    mouseMoved 14 ms OK.
  - Batch 2: press-first 3 runs: press 1 ms, release 1-2 ms,
    then mouseMoved 0-2 ms OK (3/3); reproduce mouseMoved 0 ms
    OK.
  - Batch 3 (saved as improvements/c5-step9-runs/
    stall-probe-batch1.jsonl): reproduce mouseMoved 1 ms OK;
    click mouseMoved 1 ms, press 2 ms OK; press-first moved
    0 ms, press 1 ms OK.
  - Totals: mouseMoved 8 ok (0-14 ms) and 2 timeouts (the 2
    timeouts were consecutive, runs 2-3 of batch 1);
    mousePressed/mouseReleased 8/8 ok (0-2 ms), including 2
    immediately after a timed-out move; key events 2 ms or
    better in every run; evaluate 0-3 ms in every run.
- VERDICT: the stall is FLAKY and intermittent, not a stable
  wedge. The Input domain is alive throughout (key answers,
  press/release answer even after a timed-out move, the click
  lands and focuses). The failing call is mouseMoved
  specifically, and only sometimes. Neither the workspace form
  (occlusion) nor the tab-activation form explains a 4 ms
  success followed by two 5000 ms timeouts followed by 0-2 ms
  successes on the same tab in the same conditions. The
  (b1) bypass remains the working path for sends.
- CHEAP-FIX CANDIDATE (identified, NOT landed in this step):
  the mouseMoved pre-step in cdp.mjs click() is the flaky call;
  mousePressed/mouseReleased answer reliably (8/8, 0-2 ms) and
  the press carries the coordinates, so dropping the move (or
  making it best-effort with a short timeout and proceeding to
  press anyway) is the candidate fix. It is NOT landed here
  because its proof needs live fill-path sends, which the (b1)
  proof gate does not cover, and the flakiness (8/10 moves
  answered) means 5 passing fill sends would not conclusively
  prove it either. Follow-up experiment for the coordinator:
  land drop-mousemoved (or best-effort move) behind the fill
  program, run at least 10 fill sends live on the clone2 tab,
  and compare against the 0/5 flip baseline; a hover-dependent
  target must keep its hover path (hover_click is separate and
  unaffected).

## 4. A1/A2 validator fix (section 6 of the brief)

- Commit fd9237a (tests plus code; the rewritten
  ValidatorLimitationTests were run first and failed 3/6 for
  the right reasons: a1 corrected, a1 logged, a4 refuses).
- Fix: check_viewport_geometry now PREFERS a supplied
  verified_moz_inner on EVERY branch. A wrong-but-self-
  consistent moz [250, 18] plus the true verified [240, 8]
  returns the verified origin [2749, 922], never the 10px-off
  moz-computed [2759, 932]; a verified value that fails its own
  checks refuses instead of falling back to the reported moz.
  viewport_origin records the normal-branch override in
  last_geometry_warnings. The residual is pinned openly in
  test_a2: with NO verified value supplied, a
  self-consistent-but-wrong moz is still undetectable, so the
  prototype must pass verified moz always. dom_act.py does not
  pass verified (its harvest path is unchanged by this fix).
- Tests: test_p2_element_ref plus test_zen_dom plus
  test_click3_redteam2, 193 OK.

## 5. CB-2 stamping in the agent loop (item 4)

- Commit 95d3822. first_action.stamp_actions stamps
  scope/observation_id from the observation meta into every
  action of a JSON batch (a new list; the input is not mutated;
  a meta without id or scope refuses; an action already bound
  to a different observation refuses instead of being silently
  re-stamped). broker_attempt writes the stamped copy to a
  sibling file in the state dir (the caller's actions file is
  never rewritten in place) and sends THAT file to the driver;
  the R1/W1 retry re-stamps with the FRESH meta before
  re-sending. The initial stamp happens before any broker start,
  so an unstampable meta refuses fast with no session started.
  Stamped files are removed in the finally.
- Proof (the test that fails without the stamp):
  test_act_request_carries_cb2_stamps fakes _broker_cli, reads
  the act envelope's --actions file from the request file, and
  asserts every action carries scope 'screen' and
  observation_id 'obs1'; without the stamping path the recorded
  file has neither field. test_retry_restamps_with_the_fresh_
  observation asserts the retried act carries 'obs2'.
  test_scope_less_meta_never_starts_a_session asserts the loop
  refuses before any broker CLI call. Tests-first: all 10 new
  tests failed before the fix (8 errors, 2 failures).
  test_first_action 94 OK. The desktop_act binding-when-present
  check stays as the backstop; the loop now supplies the stamps
  it was waiting for.

## 6. Intent ledger for the CDP path (item 3)

- Commit 42da581. code_exec._SENT_INTENTS is a module-level
  (target, intent) set. _api_dom_act runs in the parent (API
  calls marshal back from the forked child), so the set persists
  across run_program calls in one driver process and resets with
  it, matching the per-session scope of the JSON ledger. The
  check runs after validation and before any backend call; only
  a verified send (result ok True) is recorded, so a failed
  send can be retried with the same intent; a batch with no send
  key is not protected; intent None means no ledger.
  dom_asserts.is_send_program is the shared send predicate
  (Enter/Return after a type, fill, or set_value).
- Tests-first: the double-send refusal test failed before the
  fix (the second send went through and reached the backend);
  the allow-paths (different intent, no intent, retry after a
  failed send, non-send program) passed pre-fix and still pass.
  code_exec plus dom_act plus step5_p1p5: 116 OK.

## 7. Zen pointer delegate wiring (item 5)

- Commit 9ec713c. New scripts/zen_pointer.py:
  ZenPointerDelegate translates Zen DOM actions plus their
  screen points into desktop actions through
  CodeExecBackend.act, stamping each with the scope +
  observation_id of one fresh window observation per batch
  (begin_batch focuses the Zen window first, then observes; a
  meta without id, scope, or a persisted observation path
  refuses before any input). Mapping: click/double_click/focus/
  confirm_click/hover_click to a desktop click at the point,
  fill/set_value to click plus type, key to a desktop key (no
  point), move/hover/scroll to their desktop forms; drag
  refuses (a single point cannot express from/to). A failed or
  incomplete desktop act returns False; a CB-2 refusal from
  act propagates (a wrong stamp is a wiring bug, not a runtime
  condition).
- ZenDomBackend gains set_pointer (the delegate needs the
  CodeExecBackend, which needs the backend, so neither
  constructor can wire it) and calls begin_batch once per batch
  in dom_act, skipped for read-only batches (wait/assert only).
  cu.py code-exec wires it when CU_DOM_BACKEND=zen.
- Tests-first (the module did not exist): 15 tests, including
  the backend integration tests that drive the landed (b1)
  program through the delegate and verify the DOM
  postconditions (dom-value, sent-bubble) plus the screen point
  (field center (200, 215) plus verified origin (2749, 922) =
  (2949, 1137)). zen_pointer plus p2_element_ref plus
  code_exec: 175 OK.
- LIVE PROOF: still open. The clone chats live in Brave/Chrome,
  not Zen, so a Zen live proof needs a scratch target in Zen.
  Attempted in the live phase below if a clean venue exists;
  otherwise recorded as unit-proven with live proof deferred.

## 8. Live runs 1-5, the (b1) proof (16:04-16:17 +07)

Harness (VM): python3 scripts/s2_flip_live.py --run N
--chromium-set-value --message-prefix S2-LAND --workdir
/tmp/s2-land-N. All runs: 0 model calls. Evidence:
improvements/s2-flip-land-runs/run-N.json plus P9 PNGs.

Run 0 dry (16:04-16:05): wall 19.0s. Brave sent, fill, 93.3ms,
completed 3, CB-1 all True, V12 attempt 1. Chromium sent,
set_value, 91.5ms, completed 4, CB-1 all True, V12 attempt 1,
pre 0, delayed 1. P9 both True. Spec dry-run range 90-100ms:
both inside.

Run 1 (16:05:41-16:06:03): wall 22.2s. Brave sent, fill,
149.6ms, target 5BD079AA1C41FCF4AEAF867FB5ADB7E6, completed 3,
CB-1 all True, V12 attempt 1. Chromium sent, set_value,
143.9ms, target D1374C7C994D3DA72678E20C7FD099A0, completed 4,
CB-1 all True, V12 attempt 1, pre 0 (items 40), delayed 1
(items 43). Brave P9 FAILED (ok False, no PNG): the clone1 tab
id changed mid-run to 60CD968B6A1F22A05D66CBC8469B0D51. The send
itself verified (V12 + delayed count), so the P9 was re-captured
late (p9-run1-brave-late.png, 184,513 bytes) and reviewed: PASS,
the bubble renders as a blue user bubble.

Run 2: first attempt 16:07:59 FAILED at broker start, "busy"
(owner c5-rung2 held the broker; see section 9). Nothing was
sent, so the retry is safe. Retry 16:08:45-16:09:30, wall 25.3s.
Brave sent, fill, 163.2ms, target 60CD968B..., completed 3,
CB-1 all True, V12 attempt 1. Chromium sent, set_value,
160.5ms, completed 4, CB-1 all True, V12 attempt 1, pre 0
(items 49), delayed 1 (items 53). P9 both True.

Run 3 (16:10:03-16:10:56): wall 22.9s. Brave sent, fill,
177.2ms, target 60CD968B..., completed 3, CB-1 all True, V12
attempt 1. Chromium sent, set_value, 147.4ms, completed 4,
CB-1 all True, V12 attempt 1, pre 0 (items 55), delayed 1
(items 57). Brave P9 FAILED again (ok False): the [::1]:9223
endpoint was dead, Brave had been relaunched without the flag
at 16:10:31 by the concurrent worker (section 9). After my
relaunch with the flag (16:12-16:13, new tab id
243CEDC1B35C9CDE513418B1C2BD4F6C), the late P9
(p9-run3-brave-late.png, 187,799 bytes) was captured and
reviewed: PASS.

Run 4 (16:13:38-16:14:26): wall 36.1s. Brave FAILED-UNVERIFIED:
fill, 5098.2ms, "CDP timeout: Input.dispatchMouseEvent",
completed 0, CB-1 all False, V12 not found after 40 attempts.
Chromium sent, set_value, 123.1ms, completed 4, CB-1 all True,
V12 attempt 1, pre 0 (items 57), delayed 1 (items 59). P9 both
True (the Brave P9 shows the thread with no run-4 bubble).

Run 5 (16:15:13-16:17:15): wall 37.0s. Brave FAILED-UNVERIFIED
again: fill, 5095.0ms, same mouse timeout, completed 0, V12 not
found after 40 attempts. Chromium sent, set_value, 124.0ms,
completed 4, CB-1 all True, V12 attempt 1, pre 0 (items 59),
delayed 1 (items 61). P9 both True.

Totals. Chromium (b1) set_value: 5/5 sends. Program elapsed
143.9, 160.5, 147.4, 123.1, 124.0 ms, median 143.9 ms; dom_act
ms 50, 52, 53, 31, 32. The spec's live range was 110-145 ms:
the median sits inside it, but 2 of 5 runs exceed it (160.5,
147.4). Measured range is 123-161 ms; the spec range should be
widened to about 120-165 ms. The 2-action helper program in the
reopen measured 99-113 ms; the landed 4-action program is
longer by one focus plus one assert CDP round trip, so the
higher elapsed is expected, not a regression. Wall 22-25 s on
sends, 36-37 s on the two Brave-failure runs (the 5 s mouse
timeout plus the 10 s V12 retry loop).

Brave fill: 3/5 sends. Both failures are the SAME stall
signature (Input.dispatchMouseEvent, 5002-5003 ms) that section
3 investigated, now reproduced live on Brave's fill path, twice
in a row after three successes. The stall is cross-browser,
intermittent, and the (b1) bypass is immune: 5/5 with zero
mouse calls. This is the strongest evidence yet for the
section-3 verdict (flaky, not a stable wedge) and for the
follow-up experiment (drop or best-effort the mouseMoved
pre-step in click(), then 10+ live fill sends).

P9 review, all runs: every Chromium bubble (R1-R5) visually
verified as a blue user bubble in the clone2 thread; every
successful Brave bubble (R1 late, R2, R3 late) visually
verified in the clone1 thread; the run-4 and run-5 Brave P9s
confirm NO phantom bubble (the failed sends sent nothing, the
composer stayed empty). No DOM-vs-render mismatch anywhere.

EXPAND recommendation (for the coordinator): the (b1) shape
works, 5/5, 0 model calls. The fill path is the weak link,
3/5, with the mouse stall as the proven cause. The evidence
now argues for moving Brave to (b1) as well. The standing note
("Brave keeps fill") predates this data; this step's data says
the fill path fails 2 in 5 live sends on the same threads where
(b1) is 5/5. Coordinator decision, not taken here.

## 9. Live incidents and shared-broker contention

- Broker-busy collision (run 2, 16:07:59): broker start failed
  rc=1 {"ok":false,"error":"busy"}. Owner c5-rung2 held the
  broker (relay state finished, owner c5-rung2, generation
  1b6b5228174d8a0b7e90fa18724738f0). The harness refused fast
  before any send, so no double-send risk; the retry at
  16:08:45 succeeded once the relay was free. Queue discipline
  held under contention.
- Brave relaunches by the concurrent worker (C5-RUNG2, rung 2
  acceptance, which PASSED 10/10 at 16:21 per the MEMORY.md
  update below). Evidence: clone1 tab id 5BD079AA... at 16:03:49
  became 60CD968B... by 16:06:42 (run 1 P9 failed); Brave main
  PID 1234643 (my 16:02 relaunch, with flag) became 1245658 at
  about 16:10:31, relaunched WITHOUT the flag (no crash dump in
  Crashpad/completed, settings.dat mtime 16:10, so a relaunch,
  not a crash); later PID 1254668 on ws1; Brave closed entirely
  by 16:33. The rung2 worker's own messages in the clone1
  thread ("Da nhan du 5 run: S2-LAND R1, R2 Brave va C5-RUNG2
  R1 ALPHA, R2 BRAVO, R3 CHARLIE") confirm they were active in
  the same threads and received my R1/R2 Brave sends.
  Consequence for this step: two Brave P9 failures (runs 1 and
  3) were caused by the shared-browser cycling, not by the
  prototype; both were recovered with late captures.
- Chromium death and relaunch (16:29-16:31): Chromium PID 8059
  was gone by 16:29 (no process, no listener on 127.0.0.1:9223,
  no window). Cause not established (no crash evidence checked;
  the concurrent worker had been cycling browsers). Relaunched
  16:31 with the machine's standard flags plus
  --remote-debugging-port=9223 and the same app-id, profile
  ~/.config/chromium/Default. Verified: endpoint answers
  Chrome/157.0.8103.38; clone2 tab 8A19CF48F488FE89E685D9BB7A767A13
  present, URL https://muse.ai/?__pwa=1, login intact; window
  0x5570538ed160, same address and geometry as before, new PID
  1262765. Session restore proven for the third time.
- Brave rollback (owed, 16:34): relaunched WITHOUT the flag
  (exact P3 rollback command), new PID 1265855, window
  0x55705383d420, same address and geometry on ws2,
  [::1]:9223 dead (only 127.0.0.1:9223 listens). The machine is
  back to as-found: Zen ws1 full width, Brave ws2 901 wide, no
  flag, Chrome ws2 901 wide, with flag (as-found since Nov 21).
  Final window map 16:37:04: Zen 0x557052b62dd0 ws1 [2509, 914]
  [1863, 1176] PID 496121; Chrome 0x5570538ed160 ws2 [2533, 914]
  [901, 1176] PID 1262765; Brave 0x55705383d420 ws2 [3448, 914]
  [901, 1176] PID 1265855. Relay final state: finished, owner
  c5-heldout-91, generation e56535e84ecca4b62a36aec0c58725f9,
  driver stopped, explicit_finish.
- MEMORY.md updates received during this run: (16:01, dang)
  MAXIMIZE PARALLELISM, the 2-lane cap is lifted; (16:21)
  RUNG2 PASS 10/10, total wall 240.1 s, worker C5-RUNG2;
  (16:31, dang) clone2 is out of tokens, drop it, no more
  checks, clone2-watch-15m cron deleted. Consequence: the
  clone2-watch holds (:11:56, :26:56, :41:56, :56:56) are moot
  from here on; the browser cycling above was the rung-2
  acceptance runs, not a malfunction.

## 10. Held-out tasks (fixture bench)

- The fixture: tests/two_vision_fixture.html, batch 8, locked
  by the C4 bench manifest at sha256
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf
  (verified on the laptop before the run; same hash). A task
  this worker did not design: a fake clone thread with
  #msg-input (aria-label Message, type text), Enter appends a
  .bubble, window.__bubblePresent(text) verifies it.
- Runner: improvements/c5-step9-runs/c5-heldout-fixture.py, with
  helpers c5-fixture-seed.mjs and c5-eval.mjs (copies in
  ~/c5-step9-run/ on the laptop). It reuses the harness
  transport (Harness.broker for tabs + observe,
  Harness.oneshot_code_exec for the program) and the landed
  (b1) program, with the bubble assert selector swapped to the
  fixture's '#thread .bubble:last-child'. Verification is the
  fixture's own __bubblePresent / __sentBubbles, not the
  muse-specific V12/count helpers.
- Run 90 (16:23:35-16:24:37): FAILED, "composer not found in
  snapshot". The observe returned 4 elements, composer_present
  false. A probe observe showed why: the harvest maps <input
  type="text"> to role "input" (cdp.mjs line 211 uses the raw
  tag name as the role), and the (b1) grounding accepted only
  textarea/textbox. Elements: e1 role input name Message, e2
  role button name Send, e3 role input name Search, e4 role
  button name Emoji.
- Fix (failing-first): COMPOSER_ROLES = ('textarea', 'textbox',
  'input') in scripts/s2_flip_live.py, used by both program
  builders and the route_browser composer_present check. New
  test test_composer_grounding_accepts_text_input_role in
  tests/test_s2_flip_wiring.py executes the grounding head of
  both built programs against the fixture snapshot and asserts
  comp == 'e1'; it failed pre-fix with the same "composer not
  found in snapshot" and passes post-fix. Suites after the fix:
  test_s2_flip_wiring 20 OK; test_code_exec, test_first_action,
  test_session_driver, test_p2_element_ref 268 OK. Residual:
  a checkbox named "Message" would be mis-grounded, but
  set_value/focus fail loudly on a non-editable field, so it
  cannot send silently. The harvest's tag-name role mapping
  (text input to "input" instead of ARIA "textbox") is a known
  follow-up for a later step; changing the shared harvest has a
  wider blast radius and was not done here.
- Run 91 (16:31:49-16:32:28): PASS. Program ok True, elapsed
  93.645 ms, completed 4, log "dom_act ok True completed 4 ms
  12". Pre: bubble false, bubbles [], input_events 0. Post:
  bubble true, bubbles == [MESSAGE], input value empty,
  input_events 1. Retry: pre_present true, outcome
  already-sent, bubbles still exactly [MESSAGE] (no
  double-send). Delayed (10 s): count 1. P9 ok True; visual
  review PASSED (green bubble with the message, input empty,
  status "sent: C5-HELDOUT-R91-CHROMIUM-IGNORE-TEST"). Outcome
  sent, wall 33286.8 ms. Evidence:
  improvements/c5-step9-runs/heldout-run91.json and
  p9-heldout-run91-chromium.png (run 90's evidence is
  heldout-run90.json; the runner writes the JSON as run-90.json
  in its workdir, a filename slip, renamed on copy).
- The first run-91 attempt (16:29:10) failed at seed with
  ECONNREFUSED 127.0.0.1:9223 because Chromium was dead (see
  section 9); the retry after the Chromium relaunch passed.
- Selenium bench NOT re-run: /tmp/probe-s2-venv is gone and
  selenium is not installed on the VM, and the bench uses the
  old click/type/Enter chain, not the (b1) program, so it would
  not prove the prototype. The fixture run through the
  prototype's own transport is the held-out proof.

## 11. Zen delegate live proof: DEFERRED (recorded honestly)

No live Zen proof was attempted. Reason: no clean venue. The
clone chats live in Brave/Chrome; a Zen live proof needs a
scratch target in the user's Zen, which is the user's primary live
browser on ws1 (window 0x557052b62dd0, untouched throughout this
step). Opening a fixture tab there and driving desktop clicks
at screen points through the delegate would disturb the user's
workspace, and the owner is asleep. The delegate is unit-proven
(section 7: 15 tests, 175 OK with p2_element_ref and
code_exec, including backend integration tests that drive the
landed (b1) program through the delegate and verify the DOM
postconditions plus the screen point). Status: unit-proven,
live proof deferred. Not claimed as proven.

## 12. Wedged-session recovery

No dedicated wedge drill was run in step 9: the relay is shared
with the concurrent rung-2 work, and killing it mid-run would
disrupt another lane. Step 8's proof is cited instead: the
fallback drill proved relay-restart recovery (step-8 log,
section 6). Step-9 live recoveries observed: (a) the
broker-busy start refused fast and the retry succeeded once
the relay was free (section 9, queue discipline under
contention); (b) the Chromium process death, relaunch, and full
session restore (section 9); (c) the Brave relaunch cycles and
the rollback restore (section 9). The recovery protocol (lease
per run, broker start/finish, session restore from the profile)
held in all three. The gap (no dedicated wedge drill in step 9)
is recorded, not papered over.

## 13. Final numbers, commits, recommendation

- (b1) landing: tests commit 05c11b9, code commit dc8449b.
  NOTE: the two cdp_validation.mjs harness fixes from the (b1)
  work (bare innerWidth/innerHeight page globals; runFocusAdapter
  returns textarea) were in the working tree but NOT in commit
  05c11b9; the committed version fails the focus tests
  (verified: 05c11b9's file errors with an assertion diff,
  working tree passes 11/11). This final commit includes them.
- A1/A2 validator fix: fd9237a. CB-2 stamping: 95d3822. Intent
  ledger for CDP: 42da581. Zen pointer delegate: 9ec713c.
- Grounding fix (COMPOSER_ROLES) plus the grounding test:
  this commit (see below).
- Proof gate verdict: PASS for the (b1) prototype on the live
  clone chats (Chromium 5/5, Brave fill 3/5 with the stall as
  the proven cause) and on the held-out fixture (run 91 PASS,
  retry refused, delayed count 1). The gate's live ws2 clone
  chat plus held-out tasks are both proven with JSON + P9
  evidence in the repo.
- Open items for the coordinator: (1) Brave to (b1) or keep
  fill (evidence argues for (b1), section 8); (2) Zen delegate
  live proof deferred (section 11); (3) stall cheap-fix
  experiment (drop or best-effort mouseMoved in click(), then
  10+ live fill sends) now has live failure evidence (section
  8); (4) harvest ARIA role mapping follow-up (text input to
  "textbox", section 10); (5) spec live range widen to about
  120-165 ms (section 8); (6) no dedicated wedge drill in step
  9 (section 12).
- Test totals at the end of this step (after the fast-forward
  to origin a8dfab6): node tests/cdp_validation.mjs 11 checks;
  test_s2_flip_wiring 20 OK; test_code_exec, test_first_action,
  test_session_driver, test_p2_element_ref, test_zen_pointer,
  test_zen_dom, test_dom_act, test_step5_p1p5,
  test_click3_redteam2 all OK in one combined run.
