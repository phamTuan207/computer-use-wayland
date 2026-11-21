# Worker CLICK2-AMEND2 log (amend round 2 implementer)

Branch: todolist-push. Task start 2026-11-22 03:17 +07 (t+0m). VM only
(code + tests). No live laptop driving, no browser tasks, never ydotool.
No em dash (U+2014) or en dash (U+2013) anywhere in any file written by
this worker. All times wall-clock Asia/Ho_Chi_Minh, elapsed from task
start. Coordinator: COORD-CLICK-2. Live C12 probe runs in parallel
(CLICK2-C12PROBE); item B is finalized AFTER reading its log, per the
03:19 follow-up. Do not run any live probe from this worker.

## 03:17 +07 (t+0m) Start, read first

Read: C1/C2/C3 review logs, RT log (worker-click2-rt-log.md; the file
named worker-click2-rt-review-log.md in the brief does not exist, the
redteam log is worker-click2-rt-log.md), tests/test_click2_redteam.py
(23 tests), scripts/dom_act.py, scripts/zen_dom.py, scripts/fastpath.py,
scripts/cu.py desktop_act region, scripts/first_action.py fallback,
tests/test_dom_act.py, tests/test_zen_dom.py, tests/test_type_verification.py,
tests/test_keyboard_preflight.py harness.

Consolidated fix list A-S from the brief; mapping to findings:
A = C1 F1/F3 + C2 F1 + C3 fix 1 (wire DOM hooks, caret/focus-ring/hover
regression tests, per-type-group band + focus gate, downgrade R1 claim).
B = C12 (window origin + DPR/zoom + AT-SPI cross-check + rewrite 7
accuracy cases); PENDING on the live probe log.
C = _input_line_changed size mismatch None + type_anchor click-only +
off-line-click doc. D = zen_dom list CLI traceback. E = verify_typed
trailing whitespace. F = relay band coverage. G = terminal-None DOM
pass preserved. H = verify-before-Enter. I = exactly-once ledger + V12.
J = stale DOM re-validation + HCU live guard as code. K = hit_check
interactive child. L = shadow DOM/iframe. M = V11 MutationObserver flag.
N = CDP endpoint 9222 + cdp.mjs set_value prefill. O = zen_cli lock +
tab-switch protocol. P = DPR/zoom term (with B). Q = design gaps
(one-shot harvest, CDP getBoxModel + AX tree, Mantis defer, step-6
owner, VISION 1 wording, one vs two Zen instances). R = item-12
numbering. S = never quote synthetic 7/7 as live accuracy.
