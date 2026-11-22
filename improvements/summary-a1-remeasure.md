# A1 re-measure after the D1 startup-race fix, 2026-11-19

Owner: the owner. Worker: Luna 6 Max. Verdict: PASS success bar (PROVISIONAL, non-Astra).
All 10 tasks (5 baseline + 5 code-exec) passed functionally. Code-exec wins on every
task: fewer calls AND lower wall, with 0 refusals, 0 misclicks, 0 session deaths in
both arms. The D1 race fix works live: D1 passed on attempt 1 with no IndexError
and no program retry.

## What changed since the A1 live run

- Fix (commit 52480e7): `api_dom_start` in `scripts/code_exec.py` now polls
  `windows()` until a `chromium` window appears, bounded to 10s at 0.2s
  intervals. Root cause: `browser_start` returns once CDP answers, but the
  Wayland window can map later. Polls go straight to `backend.windows()`,
  so the wait costs no API-call budget; cancellation and the wall-clock
  budget are checked every poll; a window that never appears fails closed
  with `CodeExecError` instead of `IndexError`.
- Tests (commit 2fbc732): `test_code_exec` 47 to 50 tests, all pass.
  `FakeDomBackend` now lists a chromium window; `FakeSlowDomBackend`
  reveals it only after N polls. New tests: wait for appearance, raise
  when it never appears, full D1 program shape on the slow fake (9 API
  calls, proving the wait costs no budget).
- Templates (commit 663be6f): D1 program in
  `improvements/a1-dom-program-template.md` now starts with `dom_start()`
  plus the success assert (the exact program measured in the A1 live run);
  `improvements/pick1-program-template.md` gains the missing P1 (`df -h /`)
  and P2 (`python3 -c "print(144/150*100)"`) code blocks, byte-identical
  to the A1 live run programs with the terminal title kept as
  speed-pick1-term.
- Suites (same 6 as the A1 implement run): before 166 tests, 5 failures;
  after 169 tests, 5 failures; sorted FAIL/ERROR set identical
  (sha256 9d2bf0e6a73b02020e951f5789e689efb7b37ee6242e4b64029b18460d44d0dd),
  the same 5 pre-existing test_session_driver.DoctorCliTests failures.
- Repo HEAD for the re-measure: 663be6f on branch speed-swarm. Main untouched.

## How the re-measure ran

- Run dir /tmp/speed-a1-20261119/remeasure/, arms baseline/ and codeexec/,
  same timed.py wrapper, broker SOLO, fresh session and fresh lease per
  task. Fixture verified present, 320 bytes, sha256 ddfc86fa (not recreated).
- Baseline arm (flag OFF, clean env, relay MainPID 252588, started_git_head
  663be6f): DOM-first D1 (browser start/tabs/observe/act/assert, desktop
  act only for Ctrl+L navigation) plus P1/P2 twice each (P1a, P2a, P1b, P2b)
  in terminal speed-a1r-term. Summary: remeasure/baseline/summary-baseline.md.
- Code-exec arm (drop-in a1.conf CU_CODE_EXEC=1 + CU_PICK4_FASTPATH=1,
  relay MainPID 273102, started_git_head 663be6f): smoke code-exec ok true
  (1 API call, 2.157 ms), then D1 + P1/P2 twice each from the templates.
  Summary: remeasure/codeexec/summary-codeexec.md.
- Wall is start submit to VERIFIED. Think is driver-ready (or previous
  result) to next task submit, plus the post-result gap to VERIFIED.
  Service is start to driver-ready plus task request service. Model calls
  are task operation requests plus finish, excluding start and status polling.

## Per-task numbers (walls and thinks independently recomputed from records.jsonl)

| Task | Baseline wall | Code-exec wall | Baseline think | Code-exec think | Baseline calls | Code-exec calls |
|---|---:|---:|---:|---:|---:|---:|
| D1 | 107.068s | 58.340s | 104.566s | 55.960s | 10 | 2 |
| P1a | 35.023s | 18.963s | 33.344s | 17.466s | 5 | 2 |
| P2a | 37.743s | 17.140s | 35.947s | 15.539s | 5 | 2 |
| P1b | 31.426s | 14.323s | 29.718s | 12.817s | 5 | 2 |
| P2b | 32.985s | 15.994s | 31.173s | 14.362s | 5 | 2 |

Means: P1 baseline 33.225s vs code-exec 16.643s (-16.582s, -50 percent);
P2 baseline 35.364s vs code-exec 16.567s (-18.797s, -53 percent);
D1 107.068s vs 58.340s (-48.728s, -46 percent).

Code-exec detail: D1 in-program elapsed 1504.913 ms, 9 API calls, attempt 1,
think-before-code-exec 6.533s; P1a 626.681 ms, P2a 716.412 ms, P1b 632.797 ms,
P2b 758.749 ms, 4 API calls each. Baseline D1 used 9 task requests;
code-exec D1 used 1. Refusals, misclicks, session deaths: 0 / 0 / 0 in
both arms (the only ok:false results in either arm are the benign Alt+F4
close acts reporting "window no longer exists" after the window closed).

## Reading the numbers honestly

- The strict-wall bar is met on every task, and the call-count bar too
  (D1 10 to 2, P1/P2 5 to 2). The mechanism is the same as the A1 live run
  pointed at: program-composition think is small (think-before-code-exec
  3.7 to 6.5s) versus one think step per desktop operation in the baseline.
- The code-exec walls still carry a post-result verify gap (D1 49.427s,
  P1/P2 9 to 14s): the worker reads the verify image after the program
  returns before logging VERIFIED. The baseline walls end at the verify
  result (verify gap about 0), with image reading falling into the finish
  think outside the wall. Even with that asymmetry included against
  code-exec, every code-exec wall is lower. On a time-to-program-result
  cut the gap would be wider, not narrower.
- n=1 for D1 per arm, n=2 for P1/P2 per arm. Think variance is visible
  (baseline P1a 35.023s vs P1b 31.426s; code-exec P1a 18.963s vs P1b
  14.323s). No precise speedup factor is claimed; the direction is
  consistent across all 5 tasks and both pairs.
- Compared with the A1 live code-exec arm: D1 strict wall 128.736s (with
  retry) is now 58.340s attempt 1; P1 30.769s is now 18.963s / 14.323s;
  P2 19.387s is now 17.140s / 15.994s. The D1 improvement is the race fix
  removing the retry and diagnosis dwell; P1/P2 moved with think variance.

## Teardown

- Both arms: every task session finished clean (finished, driver stopped,
  guardian clean), Chromium closed via Alt+F4 and verified gone, the
  speed-a1r-term terminal closed, desktop Jarvis only, broker free.
  The baseline worker noted its own a1r-baseline kitty as pre-existing to
  its arm; it closed with its codex exit. Relay restored to clean env
  after the code-exec arm (drop-in removed, restart, no CU vars,
  started_git_head 663be6f, broker idle). Main stays FROZEN.

## Open

- The code-exec verify gap (reading the verify image after the program
  returns) is now the largest remaining think slice on D1 (49.427s of
  55.960s). A program-side visual confirmation that removes the
  post-result image read would cut it, but that is a new pick, not this fix.
- Verdicts are PROVISIONAL (non-Astra); Astra 6 is out of credit.
