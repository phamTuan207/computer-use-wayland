# Worker C5-INPUT-INVEST log: Chromium CDP Input.dispatchMouseEvent stall, S2 flip

Owner: the owner. Coordinator: COORD-CLICK-5. Investigates the
Chromium Input stall from the step 6 S2 flip (worker C4-S2-FLIP).
This worker did NOT do the flip. Code and log analysis only in this
phase: no live CDP calls, no workspace switches, no sends into any
real thread. Repo ~/workspace/computer-use-wayland, branch
todolist-push. No em dash or en dash anywhere in this file. No
personal info.

## 0. Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from task receipt)

- 10:42 +07, T+0m: task received. VM HEAD fccf367, origin
  todolist-push fetched, HEAD fccf367 confirmed.
- 10:42 +07, T+0m: read the flip log
  (improvements/worker-click4-s2-flip-log.md, 669 lines) in full
  and all 5 run JSONs (improvements/s2-flip-runs/run-1..5.json).
- 10:43 +07, T+1m: traced the Input path through scripts/cdp.mjs,
  scripts/code_exec.py, scripts/cu.py, scripts/session_driver.py,
  scripts/browser_worker.py, scripts/dom_act.py, scripts/dom_asserts.py.
- 10:44 +07, T+2m: checked the P3 probe log for prior Chromium
  Input evidence and the workspace record.
- 10:45 +07, T+3m: checked origin/todolist-push for the C5-VISIBILITY
  log commit: NOT present. New head 0dc0dbe is a coordinator log
  only (batches queued, 0 workers completed). Visibility result
  pending, recorded as OPEN in section 4.
- 10:47 +07, T+5m: analysis complete, verdict written. Log written
  for commit.

## 1. What failed, exactly (from the raw JSONs, not the summary)

- Median wall 33166.9ms over 5 runs (33061.9, 33121.8, 33166.9,
  33655.6, 33953.2). Brave 5/5 verified, Chromium 0/5, 0 model
  calls, per-send 5/10, per-run 0/5.
- Chromium program elapsed per run: 5103.7, 5106.3, 5104.5, 5105.8,
  5102.6 ms. Brave program elapsed per run: 163.7, 154.0, 150.1,
  134.8, 133.0 ms (dom_act 72, 51, 53, 48, 41 ms).
- Chromium log line, runs 2-5 identical: "dom_act ok False
  completed 0 ms 5003 error CDP timeout: Input.dispatchMouseEvent".
  Run 1 names only "dom_act ok False completed 0 ms 5003" (the
  error print was added after run 1).
- Chromium V12 after every failure: 40 attempts, elapsed 10051 to
  10054 ms, items frozen at 40 in all 5 runs. Brave V12: attempt 1,
  items growing 41, 45, 47, 49, 51.
- Chromium observe: 70 elements, not truncated, every run. Brave
  observe: 53 to 56 elements, not truncated, every run.
- Chromium target id D1374C7C994D3DA72678E20C7FD099A0 on
  http://127.0.0.1:9223 in every run. Brave target id
  06074E282C000A95EF89CC9EBB8F9713 on http://[::1]:9223 in every
  run. P9 screenshot ok True for both browsers in all 5 runs.
- Isolated reproduction (flip log, run 2): /tmp/s2-diag2.mjs on the
  live Chromium tab. Runtime.evaluate 1 to 3 ms, scrollIntoView a
  no-op (rect top stays 1091), post-scroll evaluates 0 to 1 ms,
  bare Input.dispatchMouseEvent mouseMoved TIMES OUT at 5000 ms.
- Dry run 0 (flip log 10:08 +07, about 3 minutes before run 1):
  SECOND attempt PASS, both browsers sent, wall 15866.4 ms, CB-1
  all three True both browsers, completed 3. FIRST attempt also
  ran both programs ok True, completed 3 (only the V12 helper
  failed on a JSON parse). So Chromium fill SUCCEEDED twice on a
  scratch tab, then failed 5/5 on the live tab. This contrast is
  the single most important fact in this investigation (section 3,
  causes 1 and 2).

## 2. The exact Input path the flip used (call chain, timeout, session)

### 2.1 Chain, top to bottom

1. Harness scripts/s2_flip_live.py:231, oneshot_code_exec. One SSH
   call per send: `CU_CODE_EXEC=1 python3 <cu.py> session --
   python3 <cu.py> session-driver`, program on stdin as JSONL.
2. cu.py:3031-3034, `session-driver` command, calls
   session_driver.relay(sys.stdin, sys.stdout).
3. session_driver.py:61-71, relay(). It swaps cu.browser to
   BrowserWorker.request for the life of the driver session, then
   restores it. So inside one program, every dom_* call goes
   through ONE persistent node worker, not one node process per
   call. (cu.browser one-shot, cu.py:2435-2438, is used only by
   the broker path and by direct CLI calls, not by this program.)
4. browser_worker.py:28-30, first request spawns `node
   scripts/cdp.mjs --worker` (persistent, stdin/stdout JSON
   lines). Its deadline is cu.browser_timeout(request),
   cu.py:2427-2433: budget 5000 ms per action, plus 5000 plus
   timeout plus 5000 for an assert. For this program (fill, key
   Enter, assert timeout 3000): 5000 + 5000 + 13000 = 23000,
   timeout min(60, 35 + 23) = 58 s. The outer deadline is 58 s
   and never fired.
5. Program scripts/s2_flip_live.py:86-115, build_program. One
   program, unchanged for all runs and both browsers:
   dom_observe(target), ground the composer (role textarea or
   textbox, name Message), dom_act(snap, [fill, key Enter,
   assert on '[role="log"] > [data-message-item]:last-child']),
   print the dom_act line, assert_state(dom_act ok).
6. code_exec.py:861-911, _api_dom_act. P5 require_asserts runs
   before any CDP request (dom_asserts.require_asserts, available
   focus_check True, type_check True, sent_bubble False). Then
   CodeExecBackend.dom_act, cu.py:2901-2918, builds the request
   {operation act, endpoint, target, snapshot, actions} and calls
   browser(request), which is the worker request by now.
7. cdp.mjs handle(), operation act. Preflight validates all
   actions, then the loop runs them. Before each action it runs a
   Runtime.evaluate stale-snapshot guard (snapshot id, URL, 90 s
   age). That evaluate ANSWERED every time (else the error would
   name the stale snapshot, not the Input timeout).
8. fill, cdp.mjs:534-543. fill calls click(a) first.
   click(a), cdp.mjs:292-314: one Runtime.evaluate that does
   scrollIntoView, getBoundingClientRect, elementFromPoint hit
   test (RT R8 rule), and returns {x, y}. That evaluate ANSWERED
   (the point came back, the hit test passed, the error is not
   "element covered"). Then the FIRST Input call:
   `call('Input.dispatchMouseEvent', {type: 'mouseMoved', x, y})`,
   cdp.mjs:311. Then mousePressed and mouseReleased, lines
   312-313, which never ran.
9. cdp.mjs:60, the per-call timer inside createTransport.call():
   `setTimeout(..., 5000)` rejects with `CDP timeout: ` + method.
   The mouseMoved promise rejected at 5000 ms. dom_act elapsed
   5102 to 5106 ms is the 5000 ms timer plus about 100 ms
   overhead. completed 0, ok False, error
   "CDP timeout: Input.dispatchMouseEvent". key Enter and the
   trailing assert never ran.
10. The failed handle() returns ok False, so BrowserWorker.request
    closes the worker (browser_worker.py: close on ok False) and
    the session-driver ends. The harness then runs the independent
    V12 (fresh node process, Runtime.evaluate only, 2 to 3 ms per
    evaluate) and P9 (Page.captureScreenshot, ok True, about
    1.2 s).

### 2.2 The timeout value and what binds

- Binding timeout: 5000 ms, fixed, cdp.mjs:60, one timer per CDP
  call. No per-method override exists; mouseMoved, mousePressed,
  mouseReleased, dispatchKeyEvent, insertText, and every
  Runtime.evaluate share the same 5000 ms.
- Outer timeouts that did NOT bind: BrowserWorker deadline 58 s
  (section 2.1 step 4), SSH timeout 90 s
  (s2_flip_live.py:234), harness program wall 20 s
  (PROGRAM_WALL_SECONDS, unused for the one-shot path in the
  runs). The 5 s inner timer is the only one that fired.
- On timeout, cdp.mjs:60 sets usable=false and drops the pending
  entry, but does NOT set transportError and does NOT close the
  WebSocket. A late answer arriving after the timer would find
  no pending entry and be ignored (message handler returns
  early). So a timeout means "no answer within 5 s", and says
  nothing about whether the browser later processed the event.
  That gap matters for retry safety (section 5, fix c).

### 2.3 Session sharing: Input and Runtime share one session

- Inside one program, dom_observe and dom_act share ONE
  WebSocket to the target. cdp.mjs handle() keeps an `owner`
  connection keyed by [endpoint.href, target.id, debuggerUrl,
  target.url] and reuses it when the key matches and the
  connection is reusable. Observe creates it; act reuses it
  (same endpoint, same target, no navigation between them).
- Consequence: the Runtime.evaluate calls that answer in 1 to
  3 ms and the Input.dispatchMouseEvent call that never answers
  travel the SAME WebSocket, to the SAME target, in the SAME
  CDP session, inside the SAME node process. This is not a
  stale-session or broken-transport failure. One domain answers,
  the other does not, on a healthy socket.
- The reproduction is session-independent as well: diag2 ran as
  its own fresh node process with its own fresh WebSocket and
  reproduced the stall, and the V12 script (fresh process per
  run) answers Runtime.evaluate in 2 to 3 ms on the same target.
  Six fresh sessions fail Input identically (5 programs plus
  diag2); every session answers Runtime.

### 2.4 What dom_act.py is NOT in this path

- scripts/dom_act.py is the Marionette/Zen path (ZenSession plus
  cu.desktop_act, wtype keyboard). The flip's live path never
  calls it. Its exactly-once intent ledger (_sent_intents) and
  its pre-send sent-bubble check (focus_type) therefore do NOT
  protect the CDP path. The CDP path has no intent ledger and no
  pre-send already-sent check: a retry of dom_act after a
  timeout would re-run the whole fill with no record that the
  first attempt may have partially landed. That gap is load
  bearing for fix (c) in section 5.
- scripts/perception_router.py and scripts/dom_asserts.py are in
  the path only as routing (dom-chromium, 10/10 decisions) and
  the P5 gate (set_value and fill carry the same mandatory
  type_check and the same send assert shape,
  dom_asserts.py:26-29, 63-68, 99-113). The router never saw a
  failure: routing was dom-chromium in all 10 browser decisions.

## 3. Ranked causes (evidence for and against, from the logs and code)

### 3.1 Rank 1 (OPEN): occluded window, mouse input gated on visibility

- Claim: Chromium sits on workspace 2 while workspace 1 is
  active, so the occluded window's input pipeline does not
  dispatch synthetic mouse events. The mouse event waits on a
  compositor frame that an occluded page never produces, while
  Runtime.evaluate (main thread, no frame needed) answers in
  1 ms and Page.captureScreenshot (forces a frame) still works.
- FOR: Brave on active workspace 1 sends 5/5; Chromium on
  inactive workspace 2 fails 5/5 at the first mouse event, same
  program, same minutes. The failure is Input-domain-specific
  (Runtime 1 ms, Page screenshot ok, DOM observe 70 elements),
  which is exactly the signature of frame-gated input, not of a
  dead renderer. P3 log section 2.9 records Brave ending on
  workspace 1, not as-found workspace 2, so the browser and the
  workspace are confounded in every live run: Brave is the
  active-workspace browser in all 5 runs, Chromium the
  inactive-workspace browser in all 5 runs.
- AGAINST (strong, and it refines the claim): dry run 0 filled
  the Chromium composer TWICE on a scratch tab in the same
  window, on the same inactive workspace, minutes before run 1
  (flip log 10:08 +07). If window occlusion alone stalled Input,
  the scratch fill should have failed too. The claim survives
  only in a refined form: what differs between the scratch tab
  and the live tab is tab activation (cause 3.2) or page state
  (cause 3.3), not the window. Workspace occlusion alone is NOT
  sufficient to explain the data.
- VERDICT: OPEN, refined. The visibility worker's test (switch
  to workspace 2, re-run bare mouseMoved) decides the workspace
  form of this claim. If Input answers on workspace 2, the claim
  is confirmed in its workspace form and fix (a2) follows. If
  Input still stalls on workspace 2, the claim falls to its
  tab-activation form (cause 3.2), and the visibility worker
  must record whether the clone2 tab was the active tab when it
  tested.

### 3.2 Rank 2 (OPEN, most likely refinement): the clone2 tab is a background tab

- Claim: the clone2 tab is not the active tab in the Chromium
  window (a Stripe tab may be frontmost), so Input to a hidden
  page waits on frames that never come, while the scratch tab
  was the active tab and therefore accepted input.
- FOR: explains the dry-run contrast exactly. A scratch tab
  created by /json/new becomes the active tab; it accepted fill
  twice. The live tab then fails 5/5. The harness never records
  which tab is active: route_browser filters /json/list by URL
  prefix only (s2_flip_live.py:325-336) and never checks the
  active tab. /json/list carries no active flag, so no log can
  confirm or deny it. The Chromium window holds 4 page targets
  (clone2 plus 3 Stripe tabs, flip log section 3.8), so a
  background tab is a live possibility, not a guess about an
  empty window. P3 log line 317 records an unread-count prefix
  clearing "when the tab lost focus to the scratch tab", proving
  tab focus changes have observable effects on this exact page.
  Runtime, observe, V12, and screenshot all work on background
  tabs, which matches every observation.
- AGAINST: after close_scratch, focus should return to the
  previously active tab, which may well have been clone2; no
  log shows a Stripe tab taking focus. CDP input generally works
  on background tabs in headed mode when the window itself is
  visible, so background-tab alone is a weaker mechanism than
  background-tab PLUS occluded-window, and the two stack here.
- VERDICT: OPEN. Deciding diagnostic D-2 (section 5): on the
  live tab, read the active tab (Target.getTargets or the
  window's tab order), activate the clone2 tab with
  Target.activateTarget or /json/activate, then run bare
  mouseMoved. If it answers, cause 3.2 is confirmed and fix
  (a1) follows. If it still stalls with the tab active and the
  window on workspace 2, cause 3.2 is killed and only page
  state (3.3) or a deeper mechanism remains.

### 3.3 Rank 3 (KILLED as stated, narrow form OPEN): live-page state stalls input

- Claim: the muse.ai live page (streaming, timers, overlays,
  focus handling) stalls the input pipeline, while the blank
  scratch page does not.
- FOR: the page is the other difference between scratch (works)
  and live (fails), besides tab activation. Run 1 diagnosed "a
  transient 5 s main-thread stall on the clone2 tab, which is
  the ACTIVE work thread (clone2 is running batch 9)".
- AGAINST (decisive): Runtime.evaluate answers in 1 to 3 ms on
  the live tab during the stall, so the main thread is NOT
  stalled; the run-1 diagnosis is superseded by the run-2
  diag2 result. scrollIntoView is a no-op (rect top stays 1091)
  and post-scroll evaluates take 0 to 1 ms. The in-page hit
  test passes (elementFromPoint returns the TEXTAREA itself),
  so no overlay covers the composer. The thread was quiet during
  the measurement window: V12 items frozen at 40 across all 5
  runs (Brave items grew 41 to 51 in the same window), so no
  streaming was in flight. P9 screenshots render normally and
  observe returns 70 elements every run. A page-state stall
  would have to block ONLY the Input domain while leaving the
  main thread idle, the layout stable, and the render normal,
  and no such mechanism appears in the page or the code.
- VERDICT: KILLED in its main-thread-stall form. The narrow form
  (the app holds input focus or captures input in a way a blank
  page does not) stays OPEN only because it has not been tested,
  and it is decided by the same diagnostic as 3.2: if mouseMoved
  still stalls on the live tab AFTER tab activation AND workspace
  focus, while a fresh scratch tab in the same window answers,
  the narrow page-state form is the survivor.

### 3.4 Rank 4 (KILLED): CDP session or domain state (stale session, wedged domain, queued call)

- FOR: none in the logs. The error names a CDP method, which
  invites a session reading.
- AGAINST (decisive): every program runs in a fresh
  session-driver process with a fresh BrowserWorker and a fresh
  WebSocket (section 2.3). The failing mouseMoved is the FIRST
  Input call in its session: only two Runtime.evaluate calls
  precede it in the same handle() invocation, and both answered.
  No prior Input call exists to queue behind. diag2 reproduced
  the stall on a third, independent fresh session. Six fresh
  sessions fail identically at the first Input call. A wedged
  session cannot explain identical failure across six fresh
  sessions.
- VERDICT: KILLED. No session reset, worker restart, or
  reconnect will fix this; the flip already restarts the whole
  chain per send and it changes nothing.

### 3.5 Rank 5 (KILLED): transport, WebSocket, or endpoint confusion (wrong browser)

- FOR: the P3 port-split trap (both browsers on port 9223) makes
  this the first suspect in any Chromium failure.
- AGAINST (decisive): the JSONs show distinct endpoints per
  browser (Brave http://[::1]:9223, Chromium
  http://127.0.0.1:9223), distinct target ids, distinct observe
  counts (53 to 56 vs 70), and distinct outcomes. The same
  session that times out on Input answers Runtime.evaluate in
  1 to 3 ms and Page.captureScreenshot in about 1.2 s (P9 ok in
  all 5 runs). V12 on the same target answers in 2 to 3 ms per
  evaluate. The socket is healthy, the target is the right tab
  (composer rect 452, 1091, 622x24 matches the P3 harvest rect
  exactly), and only the Input domain is silent.
- VERDICT: KILLED. The P3 trap was handled (endpoint named per
  browser, loopback-only validation, url.startswith filter) and
  the failure is downstream of correct routing.

### 3.6 Rank 6 (KILLED as a fix, one probe left): the 5 s timeout is too short

- FOR: the only number in the error is 5000 ms, and a longer
  budget is a one-line change.
- AGAINST (decisive as a fix): the healthy identical program
  completes in 41 to 72 ms of dom_act time on Brave; 5000 ms is
  roughly 70 to 100 times headroom. The failure is deterministic
  5/5 over 20 minutes with completed 0 every time: no partial
  progress, no late answer observed, no run slower than 5106 ms
  (which would indicate a call that nearly made it). diag2's
  bare mouseMoved also times out at exactly 5000 ms. If the
  event were merely slow, some run would show it.
- VERDICT: KILLED as a root-cause fix. One 30 s probe is still
  worth running as a killer diagnostic (D-6, section 5): if a
  30 s mouseMoved also times out, the slowness reading is dead
  for good; if it answers, this ranking is wrong and the fix is
  a longer timeout, not a new mechanism.

### 3.7 Rank 7 (KILLED): renderer main-thread stall or busy tab

- FOR: run 1's original diagnosis.
- AGAINST (decisive): Runtime.evaluate 1 to 3 ms during the
  stall (diag2), V12 evaluates 2 to 3 ms immediately after each
  failure, items frozen at 40 (no streaming). The renderer main
  thread is idle and responsive throughout. Superseded by the
  run-2 diag2 result in the flip log itself.
- VERDICT: KILLED.

### 3.8 Rank 8 (KILLED-leaning, no evidence): a second CDP client interferes

- FOR: none in the logs. Raised here only because clone2 is a
  live agent session and a second attached client is the one
  interference the logs cannot see.
- AGAINST: CDP allows multiple clients and Input from one client
  is not serialized behind another. No second client appears in
  any log. The thread was quiet (items frozen at 40) during all
  5 runs. The stall reproduces identically in diag2, which
  attaches its own fresh session.
- VERDICT: KILLED-leaning. The check for the fix worker is cheap
  (list processes attached to 127.0.0.1:9223 at failure time);
  run it once alongside D-2 and stop mentioning it if it is
  empty.

### 3.9 Rank 9 (KILLED): wrong coordinates, covered element, off-viewport point

- FOR: none; the click path computes the point from the DOM rect.
- AGAINST: rect (452, 1091, 622x24), center (763, 1103), inside
  the 901x1176 window. The in-page hit test in click() passed
  (elementFromPoint returns the TEXTAREA itself) before any
  Input call; the error is the Input timeout, not "element
  covered". The same grounding sends on Brave and on the
  scratch tab.
- VERDICT: KILLED. scrollIntoView is also killed as a trigger:
  diag2 shows it is a no-op (rect top stays 1091) and the
  evaluate containing it answers in 1 ms.

### 3.10 Rank 10 (OPEN, subsumed): window focus, distinct from workspace

- Claim: the Chromium window never had keyboard focus during the
  runs (Zen on workspace 1 had it), and synthetic mouse input
  needs the window focused, not just visible.
- FOR: same correlation as 3.1 (Brave window focused, Chromium
  window not). AGAINST: same dry-run counter-evidence as 3.1
  (scratch fill worked with no window focus).
- VERDICT: OPEN as part of the visibility family. The deciding
  test must record hyprctl activewindow alongside the mouseMoved
  result, and must test focus plus tab activation jointly, or
  the two will stay confounded exactly as browser and workspace
  are confounded in the 5 runs.

## 4. The visibility hypothesis against the code

- There is NO visibility or focus precondition anywhere in the
  send path today. Grep over scripts/*.py and scripts/*.mjs
  finds no document.visibilityState, no document.hasFocus, no
  Page.bringToFront, and no Target.activateTarget. The only
  visibility checks are element-level: getBoundingClientRect
  non-zero size, computed visibility, and the in-page hit test
  (cdp.mjs:292-314, click; harvest hit rule, RT R8). A composer
  that is fully visible inside an occluded window, on a
  background tab, passes every check in the path, and then the
  first Input call stalls. The path is blind to exactly the
  condition that correlates with the failure.
- The step 5 CB-5 locate confirmation (dom_act.py confirm_locate)
  is also element-level (visible, interactive, uncovered, stable,
  unique) and does not apply to the CDP path at all: the flip
  program grounds from the cdp.mjs snapshot, not from dom_act.py.
  Nothing in the CDP path asks whether the window is visible,
  whether the tab is active, or whether the window is focused.
- C5-VISIBILITY status at 10:45 +07: its log commit does NOT exist
  on origin/todolist-push (head 0dc0dbe is a coordinator log only;
  coord log 10:40 +07 records 0 workers completed and VISIBILITY
  as the live lane). The visibility hypothesis is therefore marked
  OPEN in this verdict, with the pending result noted explicitly:
  if the visibility worker's log lands after this commit, the
  coordinator should read its verdict against section 3.1 here.
  This investigation did NOT block waiting for it, per the task.

## 5. Fix options, ranked, with failing-first diagnostics (written out, not executed)

No code changes in this task. Each diagnostic below is a written
plan: the exact commands, the pass condition, and what it decides.
Nothing here was run.

### 5.1 Rank 1 fix (a1): CDP-level tab activation, no screen change

- What: before the program runs, activate the clone2 tab with
  Target.activateTarget (or the HTTP /json/activate/<id>) and
  bring it to front with Page.bringToFront, both over the
  existing CDP session. No Hyprland call, no workspace switch,
  no visible change to the user's screen.
- What it fixes: cause 3.2 (background tab). If the stall is
  tab-activation, this is the whole fix, and it preserves the S2
  promise of background sends.
- Cost: one CDP call before the program (milliseconds), plus a
  precondition check in the send path (record the active tab,
  activate if needed, re-check). No new mechanism, no program
  change, no re-measurement of the program itself: the flip
  program stays byte-identical.
- What could go wrong: activating the tab may change the page's
  unread-count prefix or focus state (P3 observed the prefix
  clearing on tab focus change); that is cosmetic on a test
  thread and must be noted, not feared. If the cause is
  workspace occlusion instead, (a1) does nothing and the stall
  persists, which is itself the diagnostic result.
- Failing-first diagnostic D-A1 (write out, do not run):
  on the laptop, in order: (1) read the active tab with a node
  script over http://127.0.0.1:9223 that calls
  Target.getTargets and prints which target is active; (2) call
  Target.activateTarget for D1374C7C994D3DA72678E20C7FD099A0,
  then Page.bringToFront on the same session; (3) run the bare
  mouseMoved from diag2 (/tmp/s2-diag2.mjs shape: Runtime.evaluate
  baseline, then one Input.dispatchMouseEvent mouseMoved with a
  5000 ms timeout) on the live tab. PASS condition: mouseMoved
  answers in under 100 ms. Then run the unchanged flip program
  once (run 6 shape, one browser, Chromium only). If it sends
  and V12 finds the bubble, (a1) is the fix: land the
  precondition, then re-run the full 5-run measurement. If
  mouseMoved still times out with the tab active, (a1) is dead
  and cause 3.2 is killed.

### 5.2 Rank 2 fix (a2): workspace visibility precondition

- What: before the program runs, switch Hyprland to workspace 2
  (focus the Chromium window), run the program, restore the
  as-found workspace. This is the fix the visibility hypothesis
  points at, and the C5-VISIBILITY worker is testing its premise
  live right now.
- What it fixes: cause 3.1 in its workspace form.
- Cost: the highest of the cheap fixes. It changes the user's
  screen on every send, serializes sends with the user's own use of the
  machine, and breaks the "background send" promise for this
  class. It also needs a restore step with as-found state recorded
  (active workspace, active window) and a failure path that still
  restores. While the user is asleep the screen change is free; while
  the user is awake it is a visible yank on every send.
- What could go wrong: a focus switch mid-program races with
  observe (rects read on workspace 2, acted on after a switch
  back); a crashed run leaves the machine on workspace 2; a send
  while the user is typing on workspace 1 steals the user's window. The
  precondition must be hold-focus-for-the-whole-program, not
  switch-focus-then-send.
- Failing-first diagnostic D-A2: exactly the C5-VISIBILITY test
  (switch to workspace 2, bare mouseMoved, record hyprctl
  activewindow and the active tab alongside the result). PASS
  condition: mouseMoved answers in under 100 ms on workspace 2
  while it timed out on workspace 1. If it answers, (a2) is
  confirmed and the coordinator decides whether the screen cost
  is acceptable for this class. If it still stalls, (a2) is dead
  and cause 3.1 in its workspace form is killed with it.

### 5.3 Rank 3 fix (b2): Input-free send, set_value plus JS-dispatched Enter

- What: change the program to set_value (native setter plus
  synthetic input/change events, pure Runtime.evaluate, no Input
  domain call) followed by a JS-dispatched Enter (a KeyboardEvent
  with key Enter, bubbles true, cancelable true, dispatched via
  Runtime.evaluate on the composer), or a JS .click() on the
  send button if the snapshot shows one. Trailing assert
  unchanged. Zero Input.* calls in the whole program.
- What it fixes: everything in the visibility family at once,
  whatever its exact form. If synthetic mouse input is gated on
  visibility, this program never asks for synthetic mouse input.
  It keeps S2 viable for this class without touching the user's
  screen.
- Cost: a program change, so it needs its own dry run and a fresh
  5-run measurement (the 33.2 s median must not be reused: those
  runs did not complete). The P5 gate already accepts set_value
  plus key Enter plus trailing assert (code_exec.py:873-887,
  dom_asserts.py:26-29), but a JS-dispatched Enter is NOT a key
  action, so the fix worker must check require_asserts accepts
  the new shape (a set_value followed by a JS Enter may need the
  assert table extended, or the Enter dispatched inside an
  evaluate step the validator allows).
- What could go wrong: (1) the app may ignore non-trusted
  events: React handlers fire for dispatched events (React
  listens at the root container), but app code that checks
  event.isTrusted would drop them, and only a live probe can
  tell. (2) set_value's native setter plus synthetic input event
  may not register with the app's controlled component; the
  read-back inside cdp.mjs proves the DOM value, not the app's
  state. (3) Double-send on retry: if a first attempt's
  set_value plus Enter lands late after a timeout, a retry would
  send the message twice, and the CDP path has no intent ledger
  (section 2.4). Mitigation is mandatory, not optional: a
  pre-send V12 already-sent check (the CDP equivalent of
  dom_act.py focus_type) before any retry, and no retry inside a
  scored run.
- Failing-first diagnostic D-B (write out, do not run):
  (1) scratch tab first: seed a scratch tab on the Chromium
  endpoint, run set_value plus JS Enter with a unique test
  string, assert the bubble appears. This proves the mechanism
  only. (2) Read the live snapshot for a send/submit button
  (role button near the composer); record whether the JS .click()
  variant exists as a fallback. (3) ONE live probe on the clone2
  tab with a unique IGNORE-TEST message, V12 immediately after,
  then a second V12 read 10 s later to catch a late duplicate.
  PASS condition: exactly one bubble, found on attempt 1.
  (4) Only then, a fresh 5-run measurement with the new program.
  If step (3) finds zero bubbles, (b2) is dead for this app and
  the isTrusted question is answered against it. If step (3)
  finds two bubbles, the retry rule (no retry inside a scored
  run, pre-send V12 check) becomes a precondition for any
  further work, not a footnote.
- Variant (b1), set_value plus CDP key Enter, ranks BELOW (b2)
  and must not be assumed: key Enter is Input.dispatchKeyEvent
  (cdp.mjs:390-414), also in the Input domain, and whether
  dispatchKeyEvent stalls on this tab is UNTESTED. Diagnostic
  D-B1: bare dispatchKeyEvent (a harmless key) on the live tab
  before any (b1) attempt. If dispatchKeyEvent answers and
  dispatchMouseEvent does not, the stall is mouse-specific and
  (b1) is viable; if it also stalls, (b1) is dead and only (b2)
  remains.

### 5.4 Rank 4 fix (d1): screenshot as a frame pump (one probe, speculative)

- What: call Page.captureScreenshot immediately before the
  mouseMoved, on the theory that the forced frame lets a queued
  mouse event through. P9 proves screenshots work on this tab
  (ok True, about 1.2 s).
- Cost: one probe, about 1 s. If it worked it would be the
  cheapest in-path workaround. But it is speculative (no evidence
  a single forced frame unblocks a queued event), it would have
  to run before every Input call, and it papers over the cause
  instead of removing it.
- Diagnostic D-D1: on the live tab, captureScreenshot, then bare
  mouseMoved with a 5000 ms timeout. PASS: mouseMoved answers
  in under 100 ms. FAIL: it times out, and the idea is dropped.

### 5.5 Rank 5 fix (c): longer timeout or retry (last)

- What: raise the cdp.mjs per-call timeout from 5000 ms to
  30000 ms, and/or retry the dom_act once after a timeout.
- What it fixes: nothing about the cause. It helps only if the
  stall is a slow queue that eventually drains, for which there
  is no evidence (section 3.6).
- Cost: 30 s burned per failure instead of 5 s (6 times slower
  failure, and the 5-run median would rise past the 60 s plateau
  threshold on failure alone). Retry adds a real double-send
  risk: the timed-out mouseMoved may land late, and a retried
  fill does ctrl+a plus insertText (which replaces, not
  duplicates, so the type itself is idempotent-ish) but a
  retried Enter after a late-landing first Enter sends the
  message twice. The CDP path has no intent ledger
  (section 2.4), so a retry without a pre-retry V12 check is
  unsafe for any send.
- Diagnostic D-C: a single 30 s mouseMoved probe on the live tab.
  If it answers, this ranking is wrong and a longer timeout is
  the fix. If it times out at 30 s, the slowness reading is dead
  for good. Do not land a longer timeout without this probe.

### 5.6 Rejected (not ranked): headless Chromium, Marionette/Zen path

- A headless Chromium with the same profile would dodge window
  occlusion by construction, but it is a new browser deployment
  (profile, login, session restore), not a fix to the send path.
  That is step 9 territory, not a cheap fix. The Marionette/Zen
  path cannot drive chats that live in Chromium and Brave.
  Both are rejected for this fix round.

## 6. What the stall means for the step 9 prototype

- YES, this is the prototype's first target IF the cheap fixes
  fail. The stall is a concrete mechanism fault, not a slow
  median: the Input channel is unusable on an occluded or
  backgrounded target while Runtime, DOM, Accessibility, and
  Page all answer. A prototype that cannot send to a backgrounded
  tab on an inactive workspace has not solved the problem the
  flip exposed. The prototype's first target should be named
  exactly that: an input channel that works on occluded windows.
  Its natural first shapes are (b2) JS-event submission and (d1)
  frame-pumped CDP input, in that order.
- NO, step 9 is NOT the first lever. Two cheaper fixes stand in
  front of it: (a1) tab activation (no screen change, no program
  change) and (b2) the Input-free send (program change, no screen
  change). Either one, if its diagnostic passes, keeps S2 viable
  for this class and re-opens the flip with a fresh 5-run
  measurement. The prototype is the fallback if (a1), (a2), and
  (b2) all fail their diagnostics, and its acceptance set must
  include the occluded-window case explicitly (a send to a
  backgrounded tab on an inactive workspace, scored by V12),
  or it will repeat this failure on its first live run.
- What S2 proved regardless of the fix: the Brave half (5/5,
  dom_act 41 to 72 ms, V12 attempt 1) proves the mechanism works
  when the Input domain answers. The failure is confined to one
  channel on one target state. The DO NOT EXPAND verdict stands
  until a fix re-opens the class with a fresh 5-run measurement;
  the 33.2 s median must not be quoted as a pass, because those
  runs did not complete.

## 7. Commit record

- Log file: improvements/worker-click5-input-invest-log.md
  (this file).
- Sources read: flip log (669 lines), run-1..5 JSONs,
  scripts/cdp.mjs (641 lines), scripts/code_exec.py
  (_api_dom_act, require_asserts), scripts/cu.py (browser,
  browser_timeout, CodeExecBackend.dom_act), scripts/
  session_driver.py (relay, BrowserWorker swap),
  scripts/browser_worker.py, scripts/dom_act.py (Zen path, not
  used here), scripts/dom_asserts.py, scripts/s2_flip_live.py
  (build_program, oneshot, run), P3 probe log (workspace and
  port-split sections), COORD-CLICK-5 log (0dc0dbe).
- Branch todolist-push, base fccf367 at task start, head 0dc0dbe
  at 10:47 +07 (coordinator log only, no visibility log yet).
- No live CDP calls, no workspace switches, no sends, no code
  changes in this task.
