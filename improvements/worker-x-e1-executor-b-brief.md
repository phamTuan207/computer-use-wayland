# E1 executor B brief (DELIBERATED condition), test-05 contact book

You are the EXECUTOR in a controlled experiment, condition B (DELIBERATED). A team has already deliberated and written you ONE plan. You execute ONLY that plan. You do not re-deliberate, you do not improvise, you do not improve the plan.

## Inputs

- ONLY the plan file: /tmp/e1/plan-test-05.md (read it fully first)
- Driver reference: ~/workspace/computer-use-wayland/tests/realistic/hand_drive.py (read the docstring and the command handlers, so you know the command format)

## Environment (already running when you start)

- Driver: /tmp/e1/step.sh '<json>'. One call = one driver command. It prints one JSON result line: {"ok": true, "result": ..., "ms": N} or {"ok": false, "error": ...}.
- Fixture URL: http://127.0.0.1:8767/test-05-contact-book.html
- Commands: {"cmd": "new_session"} ; {"cmd": "new_tab", "url": "..."} (opens a NEW tab, switches to it explicitly, waits for load plus 1s settle; returns a handle prefix) ; {"cmd": "find", "css": "..."} (returns an element id) ; {"cmd": "clear", "el": "..."} ; {"cmd": "type", "el": "...", "text": "..."} ; {"cmd": "click", "el": "..."} (real Marionette click; fails if the element is not interactable) ; {"cmd": "click_js", "js": "document.querySelector('...')"} (scrollIntoView plus JS click, fallback for elements Marionette cannot click) ; {"cmd": "eval", "js": "..."} (runs JS, returns the value) ; {"cmd": "text", "css": "..."} (returns textContent) ; {"cmd": "value", "css": "..."} (returns an input value) ; {"cmd": "close_tab"} (closes the CURRENT tab only) ; {"cmd": "delete_session"}.
- Zen is live on this machine. The driver talks to it through Marionette. Never use ydotool. Never use any other browser automation. Never open a browser window yourself.
- Element ids returned by find are reused by clear/type/click. After any action that re-renders the DOM (save, delete, filter), old element ids are STALE: find elements again (the plan says when).

## Procedure

1. First action: run `date "+%F %T %Z"` and record it as your start time. Create your run report file /tmp/e1/run-b-report.md and append one line per action as you go (plan step number, command, result, ms, error if any).
2. Execute the plan literally, step by step, in order. Where the plan gives an exact command, run exactly that command. Where the plan gives a check with an exact expected value, verify against exactly that value. Where the plan gives an error-handling rule, follow it.
3. Do not re-decide. Do not look up a better selector. Do not change the step order. Do not add steps. Your job is to execute, not to fix the plan.
4. If a plan step is impossible as written (selector not found after the retry the plan allows, or a check differs after the retry the plan allows), record it as a PLAN DEFECT with the plan step number, follow the plan fallback if it has one, otherwise continue to the next plan step. Never invent a success.
5. Final verification: run exactly the verification steps the plan gives (including the eval call to window.__agyVerify() if the plan includes it) and record the full returned values BEFORE closing anything. Decide PASS or FAIL from these reads.
6. Cleanup: close ONLY your own tab (close_tab), then delete_session. Never close any other tab. Never touch any other tab.
7. Last action: run `date "+%F %T %Z"`, record it as your end time, finish the report file (start time, end time, total steps run, every error, misclick, or PLAN DEFECT with plan step number, final evidence, PASS/FAIL), then stop.
8. In your final message, report: start and end times, PASS/FAIL, the number of driver commands you ran, and every error, misclick, or PLAN DEFECT.

## Rules

- Do NOT read the task spec. Do NOT read the fixture HTML. Do NOT read /tmp/e1/plans/ (the drafts). You see ONLY the final plan file. Reading the spec or fixture would break the experiment.
- Do NOT read any other agent work.
- If step.sh times out twice in a row, record DRIVER DEAD with the time and stop. Do not restart Zen, geckodriver, or the driver yourself.
- Never invent a result. Unknown is UNVERIFIED, never a pass.
