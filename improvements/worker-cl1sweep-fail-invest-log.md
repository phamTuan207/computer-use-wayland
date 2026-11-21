# CL1SWEEP-FAIL-INVEST: independent investigation of Muse's 05:49 Enter failure

Worker: CL1SWEEP-FAIL-INVEST (independent, under the no-self-healing rule, reinforced 05:56).
Task: verify or refute Muse's self-diagnosis of the failed Enter keypress during CL1-SWEEP. Do not take his word for it.
Date: 2026-11-22, investigation ~06:00 +07. All times Asia/Ho_Chi_Minh.

## Verdict

Muse's diagnosis is CONFIRMED as factually correct but INCOMPLETE: it stops one level short of the root cause.
His claim: he used a full-screen after-image as the observation, and screen observations refuse key actions (G28).
Independent check: TRUE. But the deeper cause is structural: act-now ALWAYS returns a screen-scoped after-image by construction, even when the input observation was window-scoped. Reusing ANY act-now after-image for a key/type step will ALWAYS fail. The tool sets the trap; Muse walked into it. His self-diagnosis names the operator error and misses the tool defect underneath. That is exactly the bias the no-self-healing rule guards against: not fabrication, but depth.

## Evidence re-derived (not taken from Muse's log)

### 1. The failed call: observation was screen-scoped, action was a key action

- Action file ~/workspace/cl1sweep-enter1.json, read directly: `[{"keys":["Return"],"type":"key"}]`. A key action, nothing else.
- Observation 8716a28d6388.json, fetched from the laptop and read directly:
  - scope = "screen", image_size = [1920, 1200], region = [2464, 902, 1920, 1200], monitor_box = [2464, 902, 1920, 1200], max_width = 1920, NO window field.
  - This is a full-screen observation, confirmed from the JSON itself, not from the log.
- The retry observation 0b78b458b8f3.json, read directly:
  - scope = "window", window = 0x55705383d420, image_size = [901, 1176], region = [2533, 914, 901, 1176], max_width = 960.
  - This is a genuine window observation. The retry succeeded with it.
- Images corroborate the timeline: cl1sweep-obs4.jpg (the 8716 after-image) shows the draft "Cho chay, lam sweep di" still sitting in clone1's input with the send arrow, no blue bubble in the thread: nothing was sent. cl1sweep-obs5.jpg (after the successful Enter) shows the blue bubble "Cho chay, lam sweep di" at 5:49 AM, input empty, clone1 Connected and typing.

### 2. The gate in source: preflight refusal, before any side effect

- scripts/cu.py, desktop_act, line 1649 (repo todolist-push, read directly):
  - `screen_scope = meta.get('scope') == 'screen'`
  - `if screen_scope and any(a['type'] in ('key','type') for a in actions): raise ValueError('screen observations support pointer actions only; use a window or accessibility target for typing')`
- The raise happens in preflight, before coordinate validation and before any action runs. That matches the observed failure exactly: ok false, completed 0, error string identical, total 998ms (fast fail, no action attempted). Nothing was typed or sent, and nothing could have been: the refusal is fail-closed.
- This is the known G28 rule. The error message itself is good: it names the fix (use a window or accessibility target).

### 3. Why the after-image was screen-scoped: the structural cause Muse missed

- scripts/first_action.py, act-now implementation, read directly: after the action batch runs, the envelope's `after` is ALWAYS captured with `cu.observe_screen(env, args.screen, max_width=1920, persist=True)`. The input observation's scope is never consulted.
- Proof the 8716 after-image came from exactly that call: its max_width = 1920, matching the hardcoded 1920 in first_action.py. A genuine window observe uses max_width = 960 (as 0b78 shows).
- The scope-matching after-capture already exists and is discarded: cu.py desktop_act lines 2083-2091 capture the after with `observe_screen(...) if screen_scope else observe_window(...)` and store it in result['after']. But first_action.py never copies result['after'] into the envelope; it overwrites envelope['after'] with its own screen capture. A grep for `result['after']` / `result.get('after')` in first_action.py returns nothing.
- Consequence: EVERY act-now after-image is screen-scoped, always, for every input scope. The after-image is a verification artifact (full monitor, pill state visible) that looks exactly like a chainable observation: same schema, has an id and an observation path. Nothing labels it non-chainable. Any operator who reuses it for a key/type step hits the G28 refusal, deterministically.
- Consistency proof across runs: CL2-MSG's after-image f2bdb0d34ead (03:51 click) is ALSO scope = screen, image_size [1920, 1200], verified from the laptop JSON. Same trap existed then; it did not bite only because the next steps used fresh window observes.

### 4. Contributing cause: the method's "fresh observe" step was skipped

- The Codex-demo method requires a fresh observation before each act. Muse reused the click's after-image as the next observation instead of taking a fresh window observe. The after-image is fresh in TIME (seconds old) but wrong in SCOPE. "Fresh observe" must mean a fresh WINDOW observe, never a reused after-image. The log shows he knew the rule (he used fresh window observes for the click and the retry) and took the shortcut exactly once, at the Enter step.

## Root cause (named)

Primary: act-now (scripts/first_action.py) unconditionally returns a screen-scoped after-image, discarding desktop_act's scope-matching after-capture. The after-image is therefore categorically unusable as the observation for any subsequent key/type step, but nothing in its shape signals that.
Contributing: operator reused the after-image as the next observation instead of taking a fresh window observe, violating the method's fresh-observe step.

## Fix and prevention

### Code fix (recommended, removes the trap at the source)

In scripts/first_action.py, make the act-now after-capture match the input observation's scope: when the input was a window observation, capture the after with observe_window on the same window; use observe_screen only when the input was screen-scoped. Alternatively, copy desktop_act's result['after'] (already scope-matching) into the envelope instead of re-capturing.
Trade-off to preserve: the full-screen after has verification value (pill state, both windows visible). Return BOTH: `after` (scope-matching, chainable) and `after_screen` (full monitor, verification only, documented non-chainable). That keeps both uses without the trap.
Also: move the scope check earlier. Today the G28 refusal fires after the overlay acquire and session attempt (998ms wasted). A scope assertion in first_action.py before the overlay step would fail faster and cheaper.

### Procedure fix (immediate, no code change, must enter the act-now method)

Hard rule: NEVER reuse an act-now `after` image as the `--observation` for a subsequent call. ALWAYS take a fresh `computer-use observe --window <addr>` before any key/type step.
Cheap preflight self-check, to be done by the operator before every act-now call that contains key/type actions: read the observation JSON and assert scope == "window" (or "accessibility"). If scope == "screen", re-observe the window first. One JSON read; it would have caught this failure before the call.
Regression test to add: run act-now with a click on a fixture window, feed the returned after id back as the observation for a key action, and assert the outcome matches the intended behavior (after the code fix: succeeds; before it: preflight refusal). Plus a unit test that act-now's after scope matches its input scope.

### What Muse recorded vs what is needed

Muse recorded: "never use a full-screen after-image as the observation for a key action." Correct, but it is a procedure patch on a tool defect that will trap the next operator. The code fix above is the real prevention. His retry (fresh window observe) was correct and sufficient for the task, and he logged the failure honestly with timestamps; the gap is depth, not honesty.

## Impact on the upcoming 2-vision benchmark

NONE on the script's execution path. tests/two_vision_bench.py (868 lines, origin/main, read directly) never calls `computer-use` act-now: it drives via WebDriver (driver.execute_script harvest, click_at via driver, send_one via driver), verifies via DOM bubble checks (V12 gate), and its only subprocess is launching the browser. The act-now after-image trap cannot fire inside the script.
Caveat: the LIVE run is still gated on method approval, and any manual computer-use steps around the benchmark (an operator opening chats or verifying visually with act-now) could still hit the trap. Put the procedure rule (never reuse after-images for key/type; assert scope == window first) in the benchmark runbook as a guard for the operator, even though the script itself is immune. Note the benchmark's vision steps are DOM harvests, which is the direction the 02:02 one-vision goal wants.

## Evidence list

- ~/workspace/cl1sweep-direct-log.md (Muse's log, times 05:46:18 to 05:49:53)
- ~/workspace/cl1sweep-enter1.json: `[{"keys":["Return"],"type":"key"}]`
- /home/james/.cache/agent-computer-use/8716a28d6388.json: scope screen, [1920, 1200], max_width 1920, no window field
- /home/james/.cache/agent-computer-use/0b78b458b8f3.json: scope window, 0x55705383d420, [901, 1176], max_width 960
- /home/james/.cache/agent-computer-use/f2bdb0d34ead.json: scope screen, [1920, 1200] (CL2-MSG after-image, same pattern)
- ~/workspace/cl1sweep-obs4.jpg: draft in input, no bubble (nothing sent)
- ~/workspace/cl1sweep-obs5.jpg: blue bubble 5:49 AM, input empty (sent)
- scripts/cu.py desktop_act line 1649: G28 preflight refusal; lines 2083-2091: scope-matching after-capture (discarded by caller)
- scripts/first_action.py ~line 656: after always `observe_screen(..., max_width=1920)`; no use of result['after']
- tests/two_vision_bench.py (origin/main, 868 lines): WebDriver-only, no act-now calls
