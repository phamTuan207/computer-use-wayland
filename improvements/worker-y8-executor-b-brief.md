# E1 executor B brief (DELIBERATED condition), test-05 contact book (Worker Y8, frozen v2)

You are the EXECUTOR in a controlled experiment, condition B (DELIBERATED). A team has already deliberated and written you ONE plan. You execute ONLY that plan. You do not re-deliberate, you do not improvise, you do not improve the plan.

## Inputs

- ONLY the plan file: /tmp/e1/plan-test-05.md (read it fully first)
- Driver reference: /tmp/e1/worker-y8-driver-reference.md (read it fully; it holds the command format and the shared rules)

## FORBIDDEN paths (reading any of these makes your run INVALID)

Do NOT read the task spec (~/workspace/computer-use-wayland/tests/realistic/agy-q2/test-05-contact-book.md). Do NOT read the fixture HTML (~/workspace/computer-use-wayland/tests/realistic/agy-q2/fixtures/test-05-contact-book.html). Do NOT read /tmp/e1/plans/ (the drafts). Do NOT read /tmp/e1/run-a-report.md or any A run report. Do NOT read any other agent work. Reading the spec or fixture would break the experiment.

## Environment (already running when you start)

- Driver: /tmp/e1/step.sh '<json>'. One call = one driver command. See the driver reference for the command list.
- Fixture URL: http://127.0.0.1:8767/test-05-contact-book.html
- Click policy (shared): real click first, click_js only after a real-click retry fails. EXCEPTION, plan-given: where the plan gives an explicit click_js command for a step (plan step 31, the star), run exactly that click_js command. That is a plan command, not your choice.

## QUOTING RULE (read before your first driver command)

The JSON is passed to step.sh inside a single-quoted shell word, so the JSON text must contain NO single-quote character anywhere, in any field (js, css, text, url, el). Write every JS string literal with double quotes, written as \" in the JSON text. A single quote anywhere inside the JSON ends the shell quoting, is stripped, and reaches Marionette as a JS SyntaxError, which Marionette reports as HTTP 500 in a few milliseconds while the driver, geckodriver, and port 4451 are all alive. Symptom: HTTP 500 in 2 to 4 ms on an eval or click_js, driver stack alive, is the quoting trap until proven otherwise. Never wrap the shell argument in double quotes (that makes $ and backticks live). Worked example, correct: `{"cmd":"eval","js":"return document.querySelector(\"#contacts-count\").textContent"}`. Incorrect (the trap): the same command with '#contacts-count' in single quotes.

## Procedure

1. First action: run `date "+%F %T %Z"` and record it as your start time. Only AFTER that, read your inputs. Create your run report file /tmp/e1/run-b-report.md and append one line per action as you go (plan step number, command, result, ms, error if any). List every file you read, in order, at the top of the report.
2. Execute the plan literally, step by step, in order. Where the plan gives an exact command, run exactly that command. One driver command per plan step; do not batch several plan commands into one tool call, and never batch across a check step. Where the plan gives a check with an exact expected value, verify against exactly that value. Where the plan gives an error-handling rule, follow it.
3. Do not re-decide. Do not look up a better selector. Do not change the step order. Do not add steps. Your job is to execute, not to fix the plan.
4. FIRST STEP after the plan's step 2 (new_tab): run the diagnose eval on YOUR OWN tab and proceed past plan step 2 only if it is VISIBLE. Exact JS: `{"cmd":"eval","js":"return (function(){var cs=getComputedStyle(document.body);var r=document.body.getBoundingClientRect();var cc=document.querySelector(\"#contacts-count\");return{readyState:document.readyState,htmlClassList:Array.from(document.documentElement.classList),bodyVis:cs.visibility,bodyOpacity:cs.opacity,bodyDisplay:cs.display,rect:{w:r.width,h:r.height},innerLen:document.body.innerText.length,hasFocus:document.hasFocus(),visState:document.visibilityState,countText:cc?cc.textContent.trim():null};})()"}`. VISIBLE means bodyVis "visible" AND bodyOpacity not "0" AND bodyDisplay not "none" AND countText present. If hidden, STOP immediately, record INFRA-SUSPECT with the full returned JSON, and do not run any more driver commands except delete_session in cleanup (step 7). Do NOT remove any class yourself. Do NOT retry on a new tab yourself. Record this as a stop before plan step 3, not as a plan step failure.
5. If a plan step is impossible as written (selector not found after the retry the plan allows, or a check differs after the retry the plan allows), record it as a PLAN DEFECT with the plan step number, follow the plan fallback if it has one, otherwise continue to the next plan step. Never invent a success.
6. Final verification: run exactly the verification steps the plan gives (plan steps 48-56, including the eval call to window.__agyVerify()) and record the full returned values BEFORE closing anything. Decide PASS or FAIL from these reads.
7. Cleanup: close ONLY your own tab (close_tab), then delete_session. Never close any other tab. Never touch any other tab. If you stopped early under step 4 (INFRA-SUSPECT), leave the tab open exactly as it is and still run delete_session; do not close it (the coordinator inspects it).
8. Last action: run `date "+%F %T %Z"`, record it as your end time, finish the report file (start time, end time, total steps run, every error, misclick, or PLAN DEFECT with plan step number, every ambiguous timeout, the file list, final evidence, PASS/FAIL), then stop.
9. In your final message, report: start and end times, PASS/FAIL, the number of driver commands you ran, and every error, misclick, or PLAN DEFECT.

## Rules

- Do NOT read the task spec. Do NOT read the fixture HTML. Do NOT read /tmp/e1/plans/ (the drafts). You see ONLY the final plan file. Reading the spec or fixture would break the experiment.
- Do NOT read any other agent work.
- If step.sh fails twice in a row with any error, STOP and record STOPPED (DRIVER SUSPECT) with the time and the failing command. Do not label it DRIVER DEAD yourself and do not restart Zen, geckodriver, or the driver yourself. The coordinator classifies it after liveness checks.
- Never invent a result. Unknown is UNVERIFIED, never a pass.
