# test-10-ide-debug.md

## Test ID
test-10-ide-debug

## Topic
IDE code editor and debugger: open file, set line breakpoint, start debugging session, step over instructions, inspect watch expression, update variable value, continue execution, stop debugger, and verify call stack and watch results.

## Context
A software engineer needs to isolate an off-by-one arithmetic bug inside a browser-based IDE (fixtures/test-10-ide-debug.html).
The user must open the source file "app.js", toggle a breakpoint on line 12, start the debugger session,
step over two instructions, inspect the variable "total" in the debug watch panel, dynamically override its value to 250,
continue execution to the next breakpoint, terminate the debug session, and verify that the call stack and watch panel entries
accurately reflect the modified runtime execution state in the DOM.

## Timing
- Baseline start time: 2026-11-21 17:00:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Open "app.js", set breakpoint on line 12, launch debugger, step over twice, watch and change variable "total", continue, stop debugging, and verify call stack and watch state.

## Exact steps
1. Open fixture tests/realistic/agy-y2/fixtures/test-10-ide-debug.html in the browser.
2. Verify element #debug-state-badge text is "Inactive" and #active-file-name text is "None".
3. Click tree item #file-item-app-js to open the source file "app.js".
4. Verify element #active-file-name text is "app.js" and #code-editor is visible.
5. Click line gutter #gutter-line-12 to place a breakpoint on line 12.
6. Verify element #gutter-line-12 has class "has-breakpoint".
7. Verify element #breakpoint-count-indicator text is "1".
8. Click button #btn-start-debugger to initiate debugging session.
9. Verify element #debug-state-badge text is "Paused" and #call-stack-list text contains "calculateSum (line 12)".
10. Click button #btn-step-over to advance execution one instruction.
11. Verify element #current-paused-line text is "Line 13".
12. Click button #btn-step-over to advance execution second instruction.
13. Verify element #current-paused-line text is "Line 14".
14. Verify element #watch-val-total text is "120".
15. Click input #input-edit-watch-total to focus the variable watch editor.
16. Click button #btn-open-edit-watch to show watch variable editor modal.
17. Verify element #edit-watch-modal has class "active".
18. Click input #input-watch-override-value, clear text, and type "250".
19. Click button #btn-confirm-watch-override to apply new variable value.
20. Verify element #watch-val-total text is "250".
21. Click line gutter #gutter-line-16 to place a second breakpoint on line 16.
22. Verify element #gutter-line-16 has class "has-breakpoint".
23. Verify element #breakpoint-count-indicator text is "2".
24. Click button #btn-continue-debugger to resume execution to next breakpoint.
25. Verify element #current-paused-line text is "Line 16".
26. Verify element #call-stack-list text contains "renderSummary (line 16)".
27. Verify element #watch-val-grand-total text is "250".
28. Click button #btn-stop-debugger to terminate the active debugging session.
29. Verify element #debug-state-badge text is "Stopped".
30. Verify element #current-paused-line text is "None".
31. Click button #btn-save-debug-session to export execution snapshot.
32. Verify element #debug-toast-summary text contains "Debug session complete: watched total=250, breakpoints=2, final line 16".

## Pass/fail criteria
- Pass: "app.js" opened, line 12 breakpoint hit, stepped over twice, variable "total" overridden to 250, continued to line 16, debugger stopped cleanly, and session summary toast confirms watched values and breakpoint counts.
- Fail: File app.js not loaded, debugger fails to pause on breakpoints, step over does not update current line, watch variable override not reflected, or summary toast not activated.

## Errors designed to expose
- click miss: Gutter line numbers for breakpoint placement and control icon buttons.
- slow think: Delays during step over pauses and watch value evaluation.
- stale observation: Reading variable value before step completion registers.
- wrong diagnosis: Mistaking breakpoint pause for an execution freeze or hang.
- fabrication: Asserting variable values without confirming through watch panel elements.

## Checker / expected end state
```bash
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-10-ide-debug.html --test 10
```
