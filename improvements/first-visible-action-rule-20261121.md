# First visible action rule (2026-11-21)

Owner order 22:18, correction 22:21, method 22:22, test rule 22:23.
This rule binds every live computer-use run. It is a deterministic rule,
not a reminder (Lauren Tan: a repeated mistake becomes a deterministic
rule).

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
   30 s. Tonight's baseline was ~330 s. The published reference point:
   the mean observation-to-action gap on real OSWorld workloads is 6.51 s
   (arXiv 2604.18860); a single naive loop step is 4-8 s
   (datarekha latency engineering). 30 s is generous against those and
   binding against tonight.
2. CONTINUOUS. No idle gap between actions. While the user watches, a run
   with no visible action for more than 60 s is a failure. Diagnosis
   happens after the first visible action, or in parallel with it, never
   as a long silent phase first.
3. OVERLAY MUST BE VISIBLE. The pill is on from the first visible action
   until the task ends, on BOTH paths (session and fallback). The overlay
   itself is what reports to the user what is happening. Narration before
   each step is NOT required (owner correction 22:21). A brief status
   after the fact is fine, but narration is not the mechanism.

## The mechanism (code, not a reminder)

`computer-use act-now` (`scripts/first_action.py`) is the default command
for a live action batch. It enforces the rule in this order:

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
no gap over 60 s. The rehearsal test is a COMBINED test (DOM + CLI +
mouse + keyboard in one task), set by an independent agent (owner rule
22:23). The test-taker never sets their own test.

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
