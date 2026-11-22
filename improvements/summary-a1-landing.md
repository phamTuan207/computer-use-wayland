# A1 landing summary: DOM code-exec generalized to browser tasks (Track 2, 19/11)

Owner: the owner. Worker: Luna 6 Max (A1 landing worker). Merge: see git log.
Per the owner's LAND IF BETTER standing rule (17:18): measured better than
the old version, landed to main, no asking.

## What landed

A1 generalizes Pick 1 code-exec to browser tasks via DOM-first operations.
Landing branch `a1-landing`, 7 cherry-picked commits from speed-swarm HEAD
8152c86, on top of origin/main 453adc4 (Pick 1 landed):

- d955d74 docs: A1 DOM code-exec design and template
- 83f4224 feat: DOM operations in `scripts/code_exec.py` (`api_dom_start`,
  `api_dom_tabs`, `api_dom_observe`, `api_dom_act`, `api_dom_assert`) plus
  `dom_start`/`dom_tabs`/`dom_observe`/`dom_act` on `CodeExecBackend` in
  `scripts/cu.py`
- 03795bc test: cover DOM code-exec operations
- f95807d fix: focus address bar with Ctrl+L before typing URL in D1 program
- 52480e7 fix: `api_dom_start` polls `windows()` until a chromium window
  appears, bounded 10s at 0.2s (D1 startup race: `browser_start` returns
  once CDP answers, the Wayland window can map later; wait costs no
  API-call budget, fails closed with `CodeExecError` instead of `IndexError`)
- 2fbc732 test: cover the dom_start window-readiness wait
- 663be6f docs: dom_start in the D1 template, P1/P2 blocks in the Pick 1
  template

6 files, +939/-5 vs main. No dependency on the non-landed fixes: no A1 hunk
references envelope-validator, actions-JSON, brokerfix diagnostics or
preflight-retry symbols; `scripts/code_exec.py` is byte-identical to the
version measured in the re-measure (diff vs 663be6f empty for code_exec,
tests and A1 docs); the cherry-picks applied cleanly onto main with no
conflicts. Excluded, still on speed-swarm only: the A1 re-measure docs
(8152c86, a56ce5a), envelope-validator fix, actions-JSON fix, brokerfix
diagnostics/preflight retry, Pick 2/3/4, masking.

## Verification (a): tests, main baseline vs after landing

Run on the VM in the landing worktree, unittest, Python 3.12.3
(`python3 -m unittest discover -s tests -p 'test_*.py'`).
Note: the laptop Python 3.14 counts differ (Pick 1 landing: 1138 tests);
the comparison that matters is same-machine before vs after.

- Main baseline (HEAD 453adc4): 1098 tests in 116.6s: 9 failures, 68
  errors, 16 skipped.
- After landing: test_code_exec 50 tests OK, test_session_remote 45 tests
  OK (95 together, 28.5s). Full suite 1116 tests in 110.6s: 9 failures,
  68 errors, 15 skipped.
- The FAIL/ERROR sets are IDENTICAL (diff of the sorted lists is empty,
  77 lines each). Zero new failures. The 18 new tests are the A1 DOM
  tests (test_code_exec 32 to 50); one previously skipped test now runs.
  The 9 failures / 68 errors are pre-existing on main (DoctorCliTests,
  FullRestoreEnvelope, wtype/IME environment errors).

## Verification (b): live re-measure holds FROM THE RECORDS (no live re-run)

Sources: `improvements/summary-a1-remeasure.md` (commit 8152c86) and run
dir `/tmp/speed-a1-20261119/remeasure/` on the laptop
(`baseline/summary-baseline.md`, `codeexec/summary-codeexec.md`), both
checked before merging. Re-measure worker f5b4ab5a, 17:41, verdict PASS
success bar (PROVISIONAL, non-Astra).

| Task | Baseline wall | Code-exec wall | Baseline calls | Code-exec calls |
|---|---:|---:|---:|---:|
| D1 | 107.068s | 58.340s (-48.7s, -46%) | 10 | 2 |
| P1 mean | 33.225s | 16.643s (-50%) | 5 | 2 |
| P2 mean | 35.364s | 16.567s (-53%) | 5 | 2 |

D1 passed on attempt 1 with no IndexError and no program retry (the race
fix works live). 0 refusals, 0 misclicks, 0 session deaths in both arms.
Honest limits from the record: n=1 for D1 per arm, n=2 for P1/P2 per arm;
think variance visible; no precise speedup factor claimed, direction
consistent across all 5 tasks and both pairs. The code-exec walls still
carry a post-result verify gap (D1 49.427s of 55.960s think); a
program-side visual confirmation would cut it, but that is a new pick,
not this fix.

## Notes

- Relay NOT restarted, no live broker run, speed-swarm checkout untouched.
- No live test window on the desktop; nothing to clean up.
