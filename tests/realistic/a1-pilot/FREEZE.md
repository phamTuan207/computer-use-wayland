# A1 pilot freeze record (Council 3 section 5.3)

- Freeze commit: f31abcf ("A1 pilot: frozen plan, runbook, schema,
  blinded checker, manifest + unblinding scripts", 2026-11-21,
  branch todolist-push). This line and the pilot-log freeze line
  were added in a second commit that changes nothing else. The
  hashes below must not change between the two commits.
- Branch: todolist-push. Repo: computer-use-wayland.
- No live arm has run. No speedup is claimed.

## Frozen files (sha256)

- improvements/worker-a1-pilot-plan.md
  41edab956eecd1b6725ef675f69fa4dc962ce1919d52df6aa4f13b47543f616c
- tests/realistic/a1-pilot/runbook.md
  40548b81a41b850ebdffa48024fdb7ab50cde0f3e8d8eab17c247ff03ee8b815
- tests/realistic/a1-pilot/run-log-schema.md
  9f0de18f9a1cc8708bd7851d0172c3cc9f9ab0e28fcc04a02fffd1ea9ba3329f
- tests/realistic/a1-pilot/check_run.py
  0aeb355b4ec600aba6262436cdeadd6b89b75126514736e21c20051d6636eb6c
- tests/realistic/a1-pilot/preflight-probe.md
  cb62280205dcbc32f41bfc1da6ea6500a680648012b85ae3adaa32c07bfd32a2
- tests/realistic/a1-pilot/a1_manifest.py
  776393a238597da8c9c1bfa4734c9f51e3eae91c92aba6ade75cf5d1746c0f17
- tests/realistic/a1-pilot/a1_unblind.py
  a5750e452c211c996bb30a4e82fe6aa553e50d1f16291ae4b9c73533a273cef8
- tests/realistic/a1-pilot/checker-selftest/build_matrix.py
  c7aacef1156519d4b5247ced9e38c97df36fd967dc521df03b40272c10e5e298
- tests/realistic/a1-pilot/checker-selftest/run_matrix.py
  1bff602173b740cd4af7c4380dc6a6ab2546efb9f26ebee1da433c4b8a2ba674
- tests/realistic/a1-pilot/fixtures/pick4-fixture.html
  (md5 91b2f92945c167306a13ae32977a9bf3, 719 bytes)
  19b581d03e5e53189b5c0af552fbdf11d3673a0d5b8817a318ebf948d46a31d6
- tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html
  (md5 2b6eda97036af51510b7eefe6d36dd93, last changed at commit cbbb748)
  31494de474a765f14ba90b5089cf3d8514f2448e9ff24767505f0eb0a41db496
- tests/realistic/fcc-k/test-01-spreadsheet-formula.md
  4089bd2bf14c2b17939e5b191fd965dad29b4a9bb28f6f5e1f81c44a74045118

The checker self-test matrix expected outputs live under
tests/realistic/a1-pilot/checker-selftest/cases/ (frozen alongside the
matrix). The matrix result at freeze: 17/17 passed
(python3 run_matrix.py, 2026-11-21). Layer-1 preflight:
tests/test_a1_preflight.py, 7/7 PASS. test_code_exec suite: 53 tests OK.

## GO bar (full text, frozen)

GO (pilot GO: proceed to the confirmatory run, not adoption) only if ALL
of these hold:

Case B (f01), all four conditions:
1. Median wall time (CODE) at or below 0.70 times median wall time
   (STEP).
2. Pass rate (CODE) equal to or better than pass rate (STEP), passes
   out of 3.
3. Total recovery steps across the 3 runs (CODE) not higher than total
   recovery steps across the 3 runs (STEP).
4. Total composition think (CODE, sum over all program calls) is less
   than STEP median total think for that case.

Case A (Pick 4), feasibility gate: pass rate (CODE) equal or better
than pass rate (STEP), recovery steps (CODE) not higher than recovery
steps (STEP) in total across the 3 runs, and total composition think
(CODE) less than STEP median total think. Its median wall time is
reported as a diagnostic only, not a gate.

Additional rules: 2-of-3 rule (at least 2 of the 3 CODE runs in Case B
individually at least 20 percent below the STEP median wall);
dispersion rule (INCONCLUSIVE if (max-min)/median exceeds 50 percent
in any arm-case cell); flagged-run rule (2 or more flagged runs in one
arm-case cell means INCONCLUSIVE); INCONCLUSIVE as a third outcome.
Robustness check (every CODE run wall at or below the STEP median wall)
is mandatory reporting that sets the GO HIGH/LOW CONFIDENCE label, not
a gate.

Detection limit: at n=3 this pilot is powered to detect a 50% wall cut,
not a 30% cut. A NO-GO means "not proven at pilot scale", never
"batching does not work". A GO means "proceed to the confirmatory run",
never "a 30% speedup is proven".

## What is frozen

The amended pilot plan; the amended run-log schema; the amended
runbook; the frozen check_run.py; the checker self-test matrix and its
expected outputs; the frozen fixtures (pick4 md5
91b2f92945c167306a13ae32977a9bf3, f01 md5 2b6eda97036af51510b7eefe6d36dd93);
the f01 spec file; the GO bar above; the definitions in plan section 5A;
the program caps (8192 chars, Case A 1 planned + 1 recovery, Case B
2 planned + 1 recovery); the per-case run caps (Case A 15 min, Case B
60 min); the run order (stratified-randomized per pair, sealed in the
manifest); the invalidation rules; the unblinding procedure.

## Verification evidence at freeze

- Checker self-test matrix: 17/17 passed (run_matrix.py).
- Layer-1 preflight: tests/test_a1_preflight.py, 7/7 PASS in 0.002s.
- test_code_exec suite: 53 tests, OK.
- Manifest + unblinding scripts smoke-tested on synthetic data
  (GO, NO-GO, INCONCLUSIVE scenarios all correct with expected exit
  codes). Smoke harness lives in /tmp (not committed); the scripts
  themselves are frozen above.
- Case B program-length preflight: loop-shape draft 2,453 chars (70.1%
  headroom under 8192, about 18 of 32 API calls); unrolled shape 8,603
  chars (busts the cap by 411). Draft text deleted after measurement;
  only the counts are recorded in the plan.
- Independent checker review: FAIL (narrow, fixable), reviewer not
  Worker A1 and not the executor, report
  improvements/worker-a1-checker-review-20261121.md, commit 9cf6391.
  The reviewer re-ran the matrix (17/17 passed), hand-recomputed T01
  and T03 golden metrics line by line with a second independent
  implementation (all values matched), confirmed the working-tree
  sha256 of every reviewed file matched FREEZE.md, and confirmed
  check_run.py contains no "manifest" string and Stage 1 opens only
  end-state.json plus verify.png. Three diagnostic findings, none on
  any gate metric, all fixed before the freeze commit:
  F1 misclicks reported as numeric 0 (checker now emits
  misclick_lines plus a misclicks field of "none detected" at 0, and
  the unblinding script carries misclicks per run);
  F2 vcr_service doc conflict (schema amended to the plan reading,
  production ops are all act/observe lines, the final desktop observe
  counted in both verification and production);
  F3 gap-before wording (schema and plan now say the previous metric
  line, framing lines skipped).
  After the fixes the matrix was rebuilt and re-run: 17/17 passed.
  Layer-1 preflight re-run 7/7 PASS, test_code_exec suite 53 tests OK,
  manifest + unblinding smoke tests all passed. The real-run
  cross-check on Layer-2 preflight probe directories is still owed
  at resume (synthetic dirs only so far).
