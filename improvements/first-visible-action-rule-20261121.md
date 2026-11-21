# First visible action rule (2026-11-21)

Owner order 22:18, correction 22:21, method 22:22, test rule 22:23.
`computer-use act-now` enforces this rule in code when used. It is a
deterministic rule, not a reminder (Lauren Tan: a repeated mistake
becomes a deterministic rule), but only inside `act-now`: `act` and
direct `desktop_act` remain callable with no overlay gate, so adoption
is by brief until entry-point enforcement lands. (Council 3, R1.)

## The weakness it fixes

On 2026-11-21 the owner ordered a tab click via computer-use at 22:11:30.
The first click landed at 22:17, 0.31 s, cursor 2598,1174, no miss. The
~5.5 minutes before it were silent diagnosis: sequential source reads and
retries with nothing moving on the screen and no pill. The owner waited
3+ minutes and called it out. The weakness is not the action. It is the
silent diagnosis before the first visible action.

Root causes (proven, file/line + live evidence in
improvements/worker-f2-silence-fix-log.md):

- R1: no structural fast path. The agent's default loop is research-first.
- R2: the session guardian fails fast (the cursor guard is not loaded in
  the live Hyprland: `hyprctl cu-cursor status` returns `unknown request`,
  rc 0; `cursor_theme.py:99` json.loads raises; `cursor_session.py:230`
  raises `session guardian startup failed`). The error is swallowed, so
  the agent diagnosed a 0.5 s failure for minutes.
- R3: the overlay is not tied to any action. `act` requires a session
  (`cu.py:2595`); the pill exists only inside a live session; the direct
  Pointer path never acquires the overlay. Any session failure means an
  invisible run.
- R4: observe (max age 120 s) -> session (guardian, up to 15 s) -> act is
  three serial failure points before any visible action.

## The rule (owner's three requirements, in priority order)

1. FAST. Any live computer-use task must produce a visible move or pill
   within 30 s of the order. Target: order to first visible action under
   30 s. The 30 s is a target measured post-hoc from the envelope, not a
   code-enforced bound: `FIRST_VISIBLE_ACTION_TARGET_MS = 30000` is
   defined in `first_action.py` but the envelope carries no pass/fail
   verdict against it yet (follow-up: add a target verdict to the
   envelope). Tonight's baseline was ~330 s. The published reference point:
   the mean observation-to-action gap on real OSWorld workloads is 6.51 s
   (arXiv 2604.18860); a single naive loop step is 4-8 s
   (datarekha latency engineering). 30 s is generous against those and
   binding against tonight.
2. CONTINUOUS. No idle gap between actions. While the user watches, a run
   with no visible action for more than 60 s is a failure. The 60 s bound
   is a stated expectation measured post-hoc from the JSONL timestamps;
   no watchdog enforces it in code yet (follow-up: a gap watchdog).
   Diagnosis happens after the overlay is up, or in parallel with it,
   never as a long silent phase first. Ordering, exact: the overlay
   comes first; the first pointer move follows as soon as the session
   attempt resolves or times out (deadline 20 s).
3. OVERLAY MUST BE VISIBLE. The pill is on from the first visible action
   until the task ends, on BOTH paths (session and fallback). The overlay
   itself is what reports to the user what is happening. Narration before
   each step is NOT required (owner correction 22:21). A brief status
   after the fact is fine, but narration is not the mechanism.

## Companion rules (owner, same night, bind the same runs)

- CLI FIRST (22:45). Open the Omarchy menu and switch workspaces by
  COMMAND, never by clicking the bar. Fastest-path-first: CLI before
  mouse, mouse last. The menu command is `omarchy-menu toggle root`
  (from the Omarchy config). Switching workspaces by command: SOLVED
  23:19 (AGENTS.md): `hyprctl dispatch "hl.dsp.focus({ workspace = 2 })"`
  switches workspaces in ~1 s (ws1 to ws2 and ws2 to ws1 both verified).
  The older J23 note (hl.dsp.workspace is a table, no goto/switch) is
  superseded: `hl.dsp.workspace.goto` FAILS because goto is a Lua
  reserved word (rc 7); the working form is hl.dsp.focus with a
  workspace argument. Focusing a window also works and switches to its
  workspace: `hyprctl dispatch 'hl.dsp.focus({ window =
  "address:0x..." })'` (repo pattern, cu.py:541; proven 22:51,
  activeWs 1). Never use the plain string form `hyprctl dispatch
  workspace 1` (broken in Hyprland 0.57.2 Lua).
- LOG EVERY EVENT (22:47). Append every action to the worker log AS IT
  HAPPENS (wall-clock Asia/Ho_Chi_Minh + elapsed, what, target,
  outcome, coordinates for clicks). Never batch the log at the end.
  When the owner asks, the answer must be in the log, never "I don't
  know".
- COMMIT SMALL AND MANY (22:40, 22:49). Every small step is its own
  commit, pushed immediately. The graph counts only the default branch
  (main) by UTC day; todolist-push commits reach the graph via the
  MERGE worker. Keep committing small on todolist-push.
- LAUREN TAN, NO CUTTING STEPS (22:48). Evidence contract, council +
  redteam, small commits, generator never runs its own tests, kill
  rules, continuous logging. No shortcuts.

## Typing needs a window observation (proven 22:53)

A SCREEN observation supports pointer actions only. `desktop_act`
(cu.py:1475) refuses any batch containing type/key actions on a screen
observation: "screen observations support pointer actions only; use a
window or accessibility target for typing". So for any batch that types,
pass a WINDOW observation (`observe --window 0x...`). A typing batch
given a screen observation is refused, not executed, and the caller must
re-run with a window observation; the 30 s guarantee depends on this
precondition. The refusal is an uncaught ValueError from `desktop_act`
(cu.py:1475), so it exits 1 with a traceback, not exit 2 (exit 2 is only
the overlay-unavailable refusal). It is loud, but not a clean refusal.
Follow-up (code hardening, not required for GO): catch the `desktop_act`
refusal in the fallback branch and return exit 1 with a clean JSON
envelope instead of a traceback. Follow-up (not implemented here):
`act-now` could auto-capture a window observation of the focused window
when the batch types and the given observation is a screen observation;
until then, the caller must pass the window observation.

## Zen urlbar click does not focus (HYPOTHESIS, 2/2, not proven)

In this Zen layout, a mouse click on the sidebar-top urlbar/search field
lands exactly (cursorpos verified 0 px error on run 2) but did NOT focus
the field for URL entry in 2/2 attempts, and typing after the click went
nowhere. The keyboard path works: Ctrl+L focuses the urlbar, then type +
Enter navigates (Example Domain loaded). This is a HYPOTHESIS, not a
proven Zen UI finding (redteam A7): the 2 attempts used an identical
target, identical coords (120,60), and an identical sequence shape
(Ctrl+N, then click, then type, then Enter). No variation separates
click delivery from Zen behavior: no hover dwell before the click
(desktop_act moves then clicks immediately, zero dwell; run 4 waited
500 ms after Ctrl+N but the click itself still had zero dwell), no
control click on a known-focusable field, no double-click, no click
without the preceding Ctrl+N (new-tab settle race), and the field
identity was read off a screenshot, not from DOM or a11y. The blind
type after a click that does not focus goes wherever focus happens to
be; desktop_act verifies cursor position, not focus. So a step that
needs a URL must focus the urlbar with Ctrl+L for now, and ZT-00 step
4 as written (mouse click the address bar) stays blocked (the mouse
path did not navigate 2/2). Discriminating probes before calling it
proven: hover 100 ms then click; click a control text field; click
the urlbar without a preceding Ctrl+N; double-click. Record which
probe changes the outcome. Act-now delivery itself is exonerated
(coordinate conversion and press/release are correct).

## The mechanism (code, not a reminder)

`computer-use act-now` (`scripts/first_action.py`) is the command that
enforces the rule when used (it is not yet the default entry point:
`act` and direct `desktop_act` have no overlay gate; see the header).
It runs in this order: overlay first; the move follows as soon as the
session attempt resolves or times out (deadline 20 s):

1. Acquire the overlay FIRST (`overlay.py` acquire, agent + method).
   The pill is visible within about a second of the command starting.
   If the overlay cannot be shown, the run REFUSES loudly (exit 2) and
   never acts invisibly. This is the tool-enforced gate, the same design
   as dsh-computer-use-win (input refused while the indicator is down)
   and @agent-sh/computer-use-linux (server-driven indicator).
2. Capture a fresh observation when none is given (or the given one is
   stale, over 120 s). Fast, direct, no session needed.
3. Attempt the session with a hard deadline (default 20 s). If it
   reaches ready, the batch runs through it.
4. On a session-START failure only (guardian error, cursor-guard error,
   or a timeout with no live session), fall back to the direct Pointer
   path: the same `desktop_act` the session path uses, with the overlay
   already on. Log the bypass with the guardian's real error.
5. NEVER replay an act failure. If the session started and the batch
   failed (screen changed, focus changed, any act refusal), the actions
   may have partially run. Report the error and re-observe. No fallback.
6. Capture an after-observation and release the overlay. Print a JSON
   envelope (path, order-to-overlay ms, order-to-action-start ms, total
   ms, session error, fallback reason, completed count, after id) and
   append the same record to `STATE/first-action-YYYYMMDD.jsonl`.

## Measurement

Every live run records order-to-first-visible-action in the envelope and
the JSONL log. The rehearsal target is the same as the rule: first visible
action under 30 s, overlay visible in the after-capture, click landed,
no gap over 60 s. Scope, plainly (council 2, Finding 2): act-now timings
start at command start. They exclude agent decision and observation time,
so the under-30 s rule from a user order is NOT yet demonstrated end to
end. The ~330 s baseline is end to end (thinking + diagnosis before any
command ran); the act-now numbers are command-internal. The 333 ms figure
is the session-attempt start (order_to_session_attempt_ms, renamed from
order_to_action_start_ms), not the first pointer move; the first pointer
move is bounded by the total batch time (0.87-2.0 s). The rehearsal test
is a COMBINED test (DOM + CLI + mouse + keyboard in one task), set by an
independent agent (owner rule 22:23). The test-taker never sets their own
test.

Rehearsal measured (ZT-00 via act-now, 2026-11-21 22:44-23:01, live Zen,
owner asleep, no user present):

- Gate steps 0-3 PASS (67 tabs listed, zen-bin PID 426338 alive, curl
  127.0.0.1:9222/ 200, Marionette session created). The slot later
  re-broke at 22:56 (browserElement null again; F3 owns it).
- act-now run 1 (screen obs, batch with typing): REFUSED in 638 ms.
  Overlay acquired in 356 ms. The refusal is correct: a screen
  observation cannot type (cu.py:1475).
- act-now run 2 (window obs, Ctrl+N + click urlbar + type + Enter):
  OK, fallback, 4/4, 1477 ms. Overlay 333 ms. Pill "Muse via act-now"
  visible in the after-capture. Click landed exactly on run 2
  (cursorpos 2629,974 = target, 0 px error), read 22:56:33 about 60 s
  after run 2 finished, with no pointer move recorded in between; run
  4 has no cursorpos check. Navigation did NOT happen (urlbar
  click does not focus; see above).
- act-now run 3 (window obs, Ctrl+L + type + Enter): OK, fallback,
  3/3, 1592 ms. Overlay 314 ms. Pill visible in the after-capture
  (viewed). Navigation WORKED (Example Domain loaded, urlbar shows
  example.com, tab title Example Domain).
- act-now run 4 (window obs, Ctrl+N + wait 500 ms + click urlbar +
  type example.org + Enter): OK, fallback, 5/5, 1998 ms. Overlay
  346 ms. Pill visible in the after-capture (viewed). Navigation did
  NOT happen (urlbar click, 2/2 fail).
- act-now run 5 (window obs, Ctrl+W): OK, fallback, 1/1, 865 ms.
  Overlay 330 ms. Pill visible in the after-capture (viewed). Ctrl+W
  ran; active tab became Welcome!. The close is verified only as
  'active tab became Welcome!', not as 'my Example Domain tab closed'
  (tab identities confounded by F3's concurrent cleanup; see below).
- vs tonight's baseline: ~330 s of silent diagnosis before the first
  click. act-now: overlay in 314-346 ms, session attempt starts in
  ~330 ms, whole batches in 0.87-2.0 s. That is the fix, measured
  command-internally (the end-to-end under-30 s rule from a user order
  is not yet demonstrated; see the scope note above).
- ZT-00 verdict: INCONCLUSIVE as a scenario (step 4 mouse path blocked
  by the Zen urlbar behavior; step-7 set check unverifiable tonight
  because Marionette re-broke, the sessionstore is stale, and F3's
  concurrent cleanup confounded the tab identities: F3's cleanup_full
  launched 22:54:22 and closed 52 tabs, 68 to 16; live count 14-17,
  not 67-68). The act-now fix itself is proven on its own claims,
  scoped to the fallback path (all 4 OK runs took the fallback; the
  session path is untested in this rehearsal).

## What this rule does NOT do

- It does not fix the guardian (F1 owns the cursor-guard loading).
  Until F1 lands, the fallback is the working path, and every fallback
  is logged with the guardian's error so F1's fix is measurable.
- It does not change `act`, `observe`, or `desktop_act`. The fallback
  reuses `desktop_act` unchanged, including its preflight re-observe,
  screen-change check, and 3 px pointer verification. Speed never skips
  the settle/verify steps: cua-speedrun proved a faster environment
  without settling makes the agent slower (99.02 s vs 89.54 s), because
  screenshots arrive before the redraw.
- It does not add narration. The overlay is the report.

## Limits, recorded honestly

- On the session path, `act` does not print its result JSON, so the
  envelope's session-path `ok` is the command exit code, not the action
  result. The after-capture is the verification. Follow-up: make `act`
  print its result JSON.
- The overlay daemon's `wayland_env()` looks for the Hyprland signature
  in `/run/user/1000/hyprland`, but the live dir is `/run/user/1000/hypr/`.
  The pill still works (the indicator needs WAYLAND_DISPLAY, not the
  signature), so this is not fixed here. Follow-up: correct the dir.
