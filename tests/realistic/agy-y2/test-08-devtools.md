# test-08-devtools.md

## Test ID
test-08-devtools

## Topic
Browser developer tools: open console drawer, evaluate expression, filter network requests by URL pattern, inspect HTTP 404 failed request body, clear console logs, and verify log count and table row state.

## Context
A web developer needs to debug API integration issues inside a simulated browser devtools panel (fixtures/test-08-devtools.html).
The user must open the devtools drawer, evaluate a JavaScript console command that logs an expression result, filter network network logs
by the query substring "api", inspect a failed HTTP 404 response payload inside the detail viewer, clear the console history,
and verify that the console log history and network request table rows match expected post-debug state in the DOM.

## Timing
- Baseline start time: 2026-11-21 17:00:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Open devtools, execute console expression, filter network by "api", inspect 404 request response body, clear console, and verify console and network table state.

## Exact steps
1. Open fixture tests/realistic/agy-y2/fixtures/test-08-devtools.html in the browser.
2. Verify element #devtools-panel has class "collapsed" and #devtools-toggle-btn text contains "Open DevTools".
3. Click button #devtools-toggle-btn to reveal developer tools.
4. Verify element #devtools-panel has class "expanded".
5. Click tab #tab-console to activate the JavaScript console tab.
6. Verify element #view-console is visible and #console-log-count text is "0".
7. Click input #input-console-eval and type "window.appVersion".
8. Click button #btn-eval-console to evaluate command.
9. Verify element #console-output-log text contains "v2.4.1".
10. Verify element #console-log-count text is "1".
11. Click tab #tab-network to navigate to the network monitor.
12. Verify element #view-network is visible and #network-total-count text is "6".
13. Click input #input-network-filter and type "api".
14. Click button #btn-apply-network-filter to filter requests.
15. Verify element #network-visible-count text is "3".
16. Verify element #row-req-api-users is visible.
17. Verify element #row-req-api-checkout is visible.
18. Click row #row-req-api-checkout to select the failed HTTP 404 request.
19. Verify element #request-detail-pane has class "open".
20. Verify element #detail-status-code text is "404 Not Found".
21. Click tab #tab-detail-response to switch to the response payload viewer.
22. Verify element #detail-response-body text contains "endpoint deprecated".
23. Click button #btn-close-detail to dismiss the network inspector side panel.
24. Verify element #request-detail-pane has class "closed".
25. Click tab #tab-console to return to the JavaScript console.
26. Verify element #view-console is visible.
27. Simulate mistake: click button #btn-clear-console to wipe console history.
28. Verify element #console-log-count text is "0" and #console-output-log text is empty.
29. Click input #input-console-eval and type "console.log('ready')".
30. Click button #btn-eval-console to record clean startup state.
31. Verify element #console-log-count text is "1".
32. Click tab #tab-network to verify network filters remain intact.
33. Verify element #network-visible-count text is "3".
34. Click button #btn-save-devtools-report to persist diagnostic logs.
35. Verify element #devtools-toast-summary text contains "DevTools diagnostics: 1 logs, 3 filtered network rows, error 404 checked".

## Pass/fail criteria
- Pass: DevTools opened, console expression evaluated, network filtered by "api" to 3 rows, 404 error response body inspected, console cleared and refreshed, and diagnostic toast verifies 1 log and 3 filtered rows.
- Fail: DevTools drawer fails to expand, network filter yields incorrect count, 404 payload not opened, or summary toast not activated.

## Errors designed to expose
- click miss: Small drawer toggle tab, sub-tabs inside DevTools, and table row selectors.
- slow think: Delays during response payload inspection and filter text entry.
- stale observation: Reading network row count before filter takes effect.
- wrong diagnosis: Mistaking 404 status indicator for an application crash instead of clicking it to inspect response body.
- fabrication: Asserting error message without opening the response tab.

## Checker / expected end state
```bash
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-08-devtools.html --test 08
```
