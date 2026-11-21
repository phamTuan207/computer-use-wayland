# E1 driver reference (shared by both executor briefs, Worker Y8)

Read this fully before your first driver command. It is the same file for both arms.

## Environment

- Driver: /tmp/e1/step.sh '<json>'. One call = one driver command. It prints one JSON result line: {"ok": true, "result": ..., "ms": N} or {"ok": false, "error": ...}.
- Fixture URL: http://127.0.0.1:8767/test-05-contact-book.html
- Commands: {"cmd": "new_session"} ; {"cmd": "new_tab", "url": "..."} (opens a NEW tab, switches to it explicitly, waits for load plus 1s settle; returns a handle prefix) ; {"cmd": "find", "css": "..."} (returns an element id) ; {"cmd": "clear", "el": "..."} ; {"cmd": "type", "el": "...", "text": "..."} ; {"cmd": "click", "el": "..."} (real Marionette click; fails if the element is not interactable) ; {"cmd": "click_js", "js": "document.querySelector('...')"} (scrollIntoView plus JS click, fallback for elements Marionette cannot click) ; {"cmd": "eval", "js": "..."} (runs JS, returns the value) ; {"cmd": "text", "css": "..."} (returns textContent) ; {"cmd": "value", "css": "..."} (returns an input value) ; {"cmd": "close_tab"} (closes the CURRENT tab only) ; {"cmd": "delete_session"}.
- Zen is live on this machine. The driver talks to it through Marionette. Never use ydotool. Never use any other browser automation. Never open a browser window yourself.
- Element ids returned by find are reused by clear/type/click. After any action that re-renders the DOM (save, delete, filter), old element ids are STALE: find elements again.
- Selects: set through eval with JS value plus dispatching a change event (Marionette typing does not work reliably on a select).
- Click policy (SHARED, both arms): real click first. click_js only after a real-click retry fails. Never go click_js-first, except where your brief or plan gives an explicit click_js command for that step.

## Rules that apply to both arms

- Date command FIRST, then all file reads. Your first action is `date "+%F %T %Z"`, recorded as your start time. Only after that do you read your inputs. No file read may precede the date command.
- One driver command per tool call. Never batch several step.sh invocations into one tool call (for example a shell loop). Each step.sh call is its own tool call.
- Retry rule, split by failure kind. Clean failures (element not found, or an error that proves non-execution) may retry once after re-finding the element. Ambiguous timeouts (step.sh timed out, unknown whether the command ran) must re-read state first (eval the DOM) and retry only if the state shows the command did not take effect. Record every ambiguous timeout separately with its step number.
- DRIVER DEAD: if step.sh fails twice in a row with any error (timeout or immediate error, including "fifo missing"), record DRIVER DEAD with the time and stop. Do not restart Zen, geckodriver, or the driver yourself.
- Never invent a result. Unknown is UNVERIFIED, never a pass.
- File-read attestation: list every file you read in your run report, in order. The coordinator audits your event stream for reads of forbidden paths.
- In your final message, report: start and end times, PASS/FAIL, the number of driver commands you ran, and every error, misclick, or (for B) PLAN DEFECT.
