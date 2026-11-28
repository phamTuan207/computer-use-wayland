# E1 executor A2 brief (DIRECT condition, second observation), test-05 contact book (Worker Y8b, frozen v2.1)

You are the EXECUTOR in a controlled experiment, condition A (DIRECT), SECOND observation (A2). You decide each step yourself and you drive the live browser. There is no plan: you read the task spec, you decide the exact commands, you run them, you verify, you recover from errors yourself. You are a fresh process: you have no knowledge of any first attempt.

## Inputs

1. Task spec: ~/workspace/computer-use-wayland/tests/realistic/agy-q2/test-05-contact-book.md (read it fully)
2. Fixture: ~/workspace/computer-use-wayland/tests/realistic/agy-q2/fixtures/test-05-contact-book.html (read it to confirm every selector: static ids, JS-generated ids, modal behavior, dropdown values, the star element, the delete confirmation, search and filter behavior, the banner text)
3. Driver reference: /tmp/e1/worker-y8-driver-reference.md (read it fully; it holds the command format and the shared rules)

## FORBIDDEN paths (reading any of these makes your run INVALID)

Do NOT read any other agent work. Do NOT read /tmp/e1/plan-test-05.md, /tmp/e1/draft-*.md, /tmp/e1/plans/, or improvements/worker-x-e1-plan-test-05.md (the merged deliberated plan, in the repo or on the laptop). Do NOT read /tmp/e1/run-b-report.md or any B run report. Do NOT read the first attempt's artifacts: /tmp/e1/run-a-report.md, /tmp/e1/events-a.jsonl, /tmp/e1/out.log. If you stumble on plan content by accident, stop, record it, and do not use it.

## Environment (already running when you start)

- Driver: /tmp/e1/step.sh '<json>'. One call = one driver command. See the driver reference for the command list.
- Fixture URL: http://127.0.0.1:8767/test-05-contact-book.html
- Click policy (shared): real click first, click_js only after a real-click retry fails. This applies to the star icon too: attempt the real click first, then fall back to click_js only if it fails.

## Procedure

1. First action: run `date "+%F %T %Z"` and record it as your start time. Only AFTER that, read your inputs. Create your run report file /tmp/e1/run-a2-report.md and append one line per action as you go (step number, command, result, ms, error if any). List every file you read, in order, at the top of the report.
2. Run new_session, then new_tab with the fixture URL. This opens ONLY your own new tab.
3. FIRST STEP after new_tab: run the diagnose eval on YOUR OWN tab and proceed only if it is VISIBLE. Exact JS: `{"cmd":"eval","js":"return (function(){var cs=getComputedStyle(document.body);var r=document.body.getBoundingClientRect();var cc=document.querySelector('#contacts-count');return{readyState:document.readyState,htmlClassList:Array.from(document.documentElement.classList),bodyVis:cs.visibility,bodyOpacity:cs.opacity,bodyDisplay:cs.display,rect:{w:r.width,h:r.height},innerLen:document.body.innerText.length,hasFocus:document.hasFocus(),visState:document.visibilityState,countText:cc?cc.textContent.trim():null};})()"}`. VISIBLE means bodyVis "visible" AND bodyOpacity not "0" AND bodyDisplay not "none" AND countText present. If hidden, STOP immediately, record INFRA-SUSPECT with the full returned JSON, and do not run any more driver commands except close_tab and delete_session in cleanup (step 8). Do NOT remove any class yourself. Do NOT retry on a new tab yourself.
4. Run localStorage.clear() through eval (precaution; the fixture keeps state in memory and a fresh tab is already fresh state).
5. Work through the 28 spec steps in order, deciding each exact command yourself. Verify each check step against the exact expected value from the spec; if a check differs, retry once after re-finding the element, then record the failure and continue with the next step (do not invent a success, do not skip verification).
6. On any {"ok": false} result: follow the split retry rule in the driver reference (clean failure retries once after re-finding; ambiguous timeout re-reads state first). If a real click still fails, use click_js. If that fails, record the error with the step number and continue. Never claim a step passed when its verification read failed or differed.
7. Final verification, before closing anything: perform the FIXED final-read list, in this order, and record every returned value: banner text from #contact-status-banner (expect "Directory saved: 6 contacts (1 favorite)"); visible count from #contacts-count (expect "6"); search value from #contact-search (expect ""); group value from #filter-contact-group (expect "all"); Bob phone text from #phone-bob-martin (expect "+1-555-9999"); David favorite DOM read via eval (expect {"starActive": true, "cardFavorite": true}); Spam Bot absence read via eval (expect {"cardPresent": false, "namePresent": false}); Frank DOM read via eval (expect {"cardPresent": true, "name": "Frank Sinatra", "group": "Engineering", "email": "frank.s@example.com", "phone": "+1-555-0106", "notes": "Vocal Architect"}); then eval "return window.__agyVerify()" and record its full returned JSON. Decide PASS or FAIL from these reads (pass = every fixed read matches AND __agyVerify returns passed: true, failures: [], score: 1, and state equal to {"saved": true, "contactCount": 6, "favCount": 1, "bobPhone": "+1-555-9999", "banner": "Directory saved: 6 contacts (1 favorite)"}).
8. Cleanup: close ONLY your own tab (close_tab), then delete_session. Never close any other tab. Never touch any other tab. If you stopped early under step 3 (INFRA-SUSPECT), leave the tab open exactly as it is and still run delete_session; do not close it (the coordinator inspects it).
9. Last action: run `date "+%F %T %Z"`, record it as your end time, finish the report file (start time, end time, total steps run, every error or misclick with step number, every ambiguous timeout, the file list, final evidence, PASS/FAIL), then stop.
10. In your final message, report: start and end times, PASS/FAIL, the number of driver commands you ran, and every error or misclick.

## Rules

- Do NOT read any other agent work. Do NOT read any plan file (see FORBIDDEN paths above).
- If step.sh fails twice in a row with any error, record DRIVER DEAD with the time and stop. Do not restart Zen, geckodriver, or the driver yourself.
- Never invent a result. Unknown is UNVERIFIED, never a pass.
