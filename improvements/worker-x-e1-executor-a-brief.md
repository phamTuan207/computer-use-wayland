# E1 executor A brief (DIRECT condition), test-05 contact book

You are the EXECUTOR in a controlled experiment, condition A (DIRECT). You decide each step yourself and you drive the live browser. There is no plan: you read the task spec, you decide the exact commands, you run them, you verify, you recover from errors yourself.

## Inputs

1. Task spec: ~/workspace/computer-use-wayland/tests/realistic/agy-q2/test-05-contact-book.md (read it fully first)
2. Fixture: ~/workspace/computer-use-wayland/tests/realistic/agy-q2/fixtures/test-05-contact-book.html (read it to confirm every selector: static ids, JS-generated ids, modal behavior, dropdown values, the star element, the delete confirmation, search and filter behavior, the banner text)
3. Driver reference: ~/workspace/computer-use-wayland/tests/realistic/hand_drive.py (read the docstring and the command handlers)

## Environment (already running when you start)

- Driver: /tmp/e1/step.sh '<json>'. One call = one driver command. It prints one JSON result line: {"ok": true, "result": ..., "ms": N} or {"ok": false, "error": ...}.
- Fixture URL: http://127.0.0.1:8767/test-05-contact-book.html
- Commands: {"cmd": "new_session"} ; {"cmd": "new_tab", "url": "..."} (opens a NEW tab, switches to it explicitly, waits for load plus 1s settle; returns a handle prefix) ; {"cmd": "find", "css": "..."} (returns an element id) ; {"cmd": "clear", "el": "..."} ; {"cmd": "type", "el": "...", "text": "..."} ; {"cmd": "click", "el": "..."} (real Marionette click; fails if the element is not interactable) ; {"cmd": "click_js", "js": "document.querySelector('...')"} (scrollIntoView plus JS click, fallback for elements Marionette cannot click) ; {"cmd": "eval", "js": "..."} (runs JS, returns the value) ; {"cmd": "text", "css": "..."} (returns textContent) ; {"cmd": "value", "css": "..."} (returns an input value) ; {"cmd": "close_tab"} (closes the CURRENT tab only) ; {"cmd": "delete_session"}.
- Zen is live on this machine. The driver talks to it through Marionette. Never use ydotool. Never use any other browser automation. Never open a browser window yourself.
- Element ids returned by find are reused by clear/type/click. After any action that re-renders the DOM (save, delete, filter), old element ids are STALE: find elements again.
- Selects: set through eval with JS value plus dispatching a change event (Marionette typing does not work reliably on a select).
- A click on a table row fails; click the cell inside instead. The same interactability rule applies to small icons: prefer click_js for the star icon if a real click fails.

## Procedure

1. First action: run `date "+%F %T %Z"` and record it as your start time. Create your run report file /tmp/e1/run-a-report.md and append one line per action as you go (step number, command, result, ms, error if any).
2. Run new_session, then new_tab with the fixture URL. This opens ONLY your own new tab. Confirm you are in the fixture tab by reading #contacts-count (expect "6").
3. Run localStorage.clear() through eval (precaution; the fixture keeps state in memory and a fresh tab is already fresh state).
4. Work through the 28 spec steps in order, deciding each exact command yourself. Verify each check step against the exact expected value from the spec; if a check differs, retry once after re-finding the element, then record the failure and continue with the next step (do not invent a success, do not skip verification).
5. On any {"ok": false} result: retry the same command once after re-finding the element; if it fails again, use click_js for clicks; if that fails, record the error with the step number and continue. Never claim a step passed when its verification read failed or differed.
6. Final verification, before closing anything: read the banner text, the contacts count, Bob phone, David favorite state, and run eval "return window.__agyVerify()" and record its full returned JSON. Decide PASS or FAIL from these reads (pass = exactly the spec pass criteria).
7. Cleanup: close ONLY your own tab (close_tab), then delete_session. Never close any other tab. Never touch any other tab.
8. Last action: run `date "+%F %T %Z"`, record it as your end time, finish the report file (start time, end time, total steps run, every error or misclick with step number, final evidence, PASS/FAIL), then stop.
9. In your final message, report: start and end times, PASS/FAIL, the number of driver commands you ran, and every error or misclick.

## Rules

- Do NOT read any other agent work. Do NOT read /tmp/e1/plans/ or any plan file. This condition is direct: you decide.
- If step.sh times out twice in a row, record DRIVER DEAD with the time and stop. Do not restart Zen, geckodriver, or the driver yourself.
- Never invent a result. Unknown is UNVERIFIED, never a pass.
