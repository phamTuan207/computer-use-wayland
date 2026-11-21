# E1 driver reference (shared by both executor briefs, Worker Y8)

Read this fully before your first driver command. It is the same file for both arms.

## Environment

- Driver: /tmp/e1/step.sh '<json>'. One call = one driver command. It prints one JSON result line: {"ok": true, "result": ..., "ms": N} or {"ok": false, "error": ...}.
- Fixture URL: http://127.0.0.1:8767/test-05-contact-book.html
- Commands: {"cmd": "new_session"} ; {"cmd": "new_tab", "url": "..."} (opens a NEW tab, switches to it explicitly, waits for load plus 1s settle; returns a handle prefix) ; {"cmd": "find", "css": "..."} (returns an element id) ; {"cmd": "clear", "el": "..."} ; {"cmd": "type", "el": "...", "text": "..."} ; {"cmd": "click", "el": "..."} (real Marionette click; fails if the element is not interactable) ; {"cmd": "click_js", "js": "document.querySelector(\"...\")"} (scrollIntoView plus JS click, fallback for elements Marionette cannot click) ; {"cmd": "eval", "js": "..."} (runs JS, returns the value; the JS runs as a function body, so a value-returning eval MUST start with `return` - a bare expression or IIFE returns null) ; {"cmd": "text", "css": "..."} (returns textContent) ; {"cmd": "value", "css": "..."} (returns an input value) ; {"cmd": "close_tab"} (closes the CURRENT tab only) ; {"cmd": "delete_session"}.
- Zen is live on this machine. The driver talks to it through Marionette. Never use ydotool. Never use any other browser automation. Never open a browser window yourself.
- Element ids returned by find are reused by clear/type/click. After any action that re-renders the DOM (save, delete, filter), old element ids are STALE: find elements again.
- Selects: set through eval with JS value plus dispatching a change event (Marionette typing does not work reliably on a select).
## QUOTING RULE (read before your first driver command)

The JSON is passed to step.sh inside a single-quoted shell word, so the JSON text must contain NO single-quote character anywhere, in any field (js, css, text, url, el). Write every JS string literal with double quotes, written as \" in the JSON text. A single quote anywhere inside the JSON ends the shell quoting, is stripped, and reaches Marionette as a JS SyntaxError, which Marionette reports as HTTP 500 in a few milliseconds while the driver, geckodriver, and port 4451 are all alive. Symptom: HTTP 500 in 2 to 4 ms on an eval or click_js, driver stack alive, is the quoting trap until proven otherwise. Never wrap the shell argument in double quotes (that makes $ and backticks live). Worked example, correct: `{"cmd":"eval","js":"return document.querySelector(\"#contacts-count\").textContent"}`. Incorrect (the trap): the same command with '#contacts-count' in single quotes.

- Click policy (SHARED, both arms): real click first. click_js only after a real-click retry fails. Never go click_js-first, except where your brief or plan gives an explicit click_js command for that step.

## Rules that apply to both arms

- Date command FIRST, then all file reads. Your first action is `date "+%F %T %Z"`, recorded as your start time. Only after that do you read your inputs. No file read may precede the date command.
- One driver command per tool call. Never batch several step.sh invocations into one tool call (for example a shell loop). Each step.sh call is its own tool call.
- Retry rule, split by failure kind. Clean failures (element not found, or an error that proves non-execution) may retry once after re-finding the element. Ambiguous timeouts (step.sh timed out, unknown whether the command ran) must re-read state first (eval the DOM) and retry only if the state shows the command did not take effect. Record every ambiguous timeout separately with its step number.
- DRIVER SUSPECT: if step.sh fails twice in a row with any error (timeout or immediate error, including "fifo missing"), STOP and record STOPPED (DRIVER SUSPECT) with the time and the failing command. Do not label it DRIVER DEAD yourself and do not restart Zen, geckodriver, or the driver yourself. The coordinator classifies it after liveness checks, and first inspects the failed command's JS for single quotes (the quoting trap).
- Never invent a result. Unknown is UNVERIFIED, never a pass.
- File-read attestation: list every file you read in your run report, in order. The coordinator audits your event stream for reads of forbidden paths.
- In your final message, report: start and end times, PASS/FAIL, the number of driver commands you ran, and every error, misclick, or (for B) PLAN DEFECT.
