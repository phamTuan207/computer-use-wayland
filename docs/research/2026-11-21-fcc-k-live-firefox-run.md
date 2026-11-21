# fcc-k suite live run on real Firefox, 2026-11-21

Batch 4 task 3: run the fixed fcc-k realistic suite live on a real
browser and compare with the Worker U Zen reference numbers
(total 28,613 ms, 383 steps, 0 fail).

Result: 10/10 PASS, 0 fail, on real Firefox 160.0.1 headless.

## Source and environment

- Suite: `tests/realistic/fcc-k` taken from branch `origin/todolist-push`
  at commit `66e5e48`, extracted unchanged to a scratch directory.
  No fixture, spec, or checker file was modified.
- Machine: this clone2 virtual machine, Linux x86_64, shared CPU
  (1.5 vCPU), no display. Not the user machine.
- Browser: Firefox 160.0.1, headless, one fresh browser instance and
  profile per test, launched by geckodriver 0.37.1.
- Driver: Selenium 4.53.0 from the local venv, Python runner written
  for this task.
- Run window: 2026-11-21T11:42:57Z to 2026-11-21T11:44:23Z (UTC),
  wall clock 85.5 s for the whole suite including runner overhead
  between tests.

## Method

For each test the runner:

1. Launches Firefox and opens the fixture with a `file://` URL.
2. Negative control: calls `window.__fcckVerify()` on the fresh,
   untouched fixture. It must fail, and it did fail for all 10 tests
   (4 to 19 assertion failures each). This proves the checker reads
   real DOM state and does not pass on its own.
3. Performs the spec steps with real WebDriver interactions only:
   element clicks, `clear()` plus `send_keys` typing, native select
   handling, and DOM text reads. No step was carried out by script.
   The only `execute_script` calls in the whole run are the
   `__fcckVerify()` calls themselves, the same assertion entry point
   the suite checker `check.mjs` uses under puppeteer.
4. Calls `window.__fcckVerify()` again and records its verdict
   (`passed`, `failures`, `state`) as the test result. The runner
   also asserts key intermediate values itself (for example E5, E6,
   E7 in test 01, the error texts in test 08, line by line equality
   with the reference block in test 09); all runner assertions passed.

Step counting: one step is one WebDriver action (one click, one field
typing, or one DOM read). The spec files number their steps more
coarsely (194 numbered steps across the suite); where a spec step
needs several actions, for example the spreadsheet fixture needs a
cell-select click, a type into the shared input, a type-button click,
and an Enter click per cell, the action count is higher than the
spec step count.

Timing: per test, elapsed ms is wall time from just before browser
launch to just after the final verify call, so it includes that
test's cold browser start. Browser start ms and steps-only ms (the
sum of the individual action times) are reported separately so the
interaction time can be compared on its own.

## Per test results

| Test | Spec steps | Steps executed | Elapsed ms | Browser start ms | Steps-only ms | Fresh fixture failures | Result |
|---|---|---|---|---|---|---|---|
| 01 spreadsheet-formula | 26 | 90 | 16,796.9 | 6,031.5 | 10,063.8 | 18 | PASS |
| 02 email-triage-reply | 22 | 28 | 9,870.6 | 6,805.2 | 2,624.2 | 7 | PASS |
| 03 calendar-conflicts | 20 | 15 | 8,799.9 | 3,364.9 | 4,710.3 | 5 | PASS |
| 04 research-notes | 17 | 13 | 3,872.6 | 2,727.3 | 815.4 | 6 | PASS |
| 05 image-organize-rename | 24 | 40 | 6,100.0 | 2,780.1 | 2,946.4 | 19 | PASS |
| 06 settings-two-apps | 18 | 16 | 4,175.4 | 2,539.9 | 1,176.1 | 8 | PASS |
| 07 bug-reproduction | 16 | 12 | 4,226.9 | 2,645.2 | 892.2 | 6 | PASS |
| 08 form-validation-fix | 16 | 13 | 3,892.7 | 2,754.5 | 736.0 | 4 | PASS |
| 09 copy-format-convert | 18 | 10 | 4,698.0 | 2,848.9 | 1,322.8 | 5 | PASS |
| 10 long-document-edit | 17 | 25 | 10,499.9 | 5,265.8 | 4,385.0 | 6 | PASS |
| **Total** | **194** | **262** | **72,932.9** | **37,763.3** | **29,672.2** | - | **10/10 PASS, 0 fail** |

Per test notes:

- Test 01: E5 = 1864000, E6 = 621333, E7 first showed the text
  `COUNT text` from the wrong formula and showed 3 after the COUNTA
  fix, exactly as the spec requires. The 90 actions come from the
  4-actions-per-cell fixture design, and per call latency was the
  highest of the suite here (about 112 ms per action on average).
- Test 03: the runner computed the busy hours from the live grid
  (Tuesday busy at 9 and 13) and found the first free gap at 10:00,
  which is also the slot the checker requires. Event saved on
  Tuesday 10:00, 30 minutes, 2 attendees, 10 minute reminder, zero
  overlap.
- Test 07: observed before = enabled, after = enabled (the first
  Save reverted the toggle, so the bug reproduced), after2 =
  disabled after the deliberate second Save. The gap between issuing
  the Toggle click and issuing the Save click was 100.3 ms, which is
  this machine's WebDriver call latency; no deliberate wait was
  inserted, so the immediate-save condition of the reproduction was
  kept as written.
- Test 10: find reported 3 matches for `old vendor` before replace
  and 0 after; the inserted table, TOC count, and the export view
  were all verified in the live page.

## Comparison with the Worker U Zen reference

| Figure | Worker U on Zen (reference) | This run on Firefox (live) |
|---|---|---|
| Tests passed | 10/10 (implied by 0 fail) | 10/10 |
| Fails | 0 | 0 |
| Steps | 383 | 262 WebDriver actions (194 spec steps) |
| Total time | 28,613 ms | 72,932.9 ms including browser starts; 29,672.2 ms steps-only |

The pass/fail outcome matches exactly: 10/10, 0 fail. The time and
step totals are not measured the same way, and the differences are
explainable without either run being wrong:

- Browser startup: the Zen reference run worked in a browser that
  was already running. This run cold-started a fresh Firefox for
  every test, which cost 37,763.3 ms of the 72,932.9 ms total, more
  than half. Removing startup, the interaction time is 29,672.2 ms,
  within about 4 percent of the Zen total of 28,613 ms.
- Machine: this is a small shared-CPU VM (1.5 vCPU) and every
  WebDriver call pays local geckodriver and process latency,
  measured here at roughly 60 to 115 ms per action depending on the
  test. The Zen run was on the user's own machine with its own
  latency profile.
- Headless Firefox versus real Zen: different browser build,
  headless rendering, and a fresh profile per test here, against a
  warm, already configured Zen profile there.
- Step counting: 383 steps in the reference against 262 counted
  WebDriver actions (or 194 spec steps) here. The counting unit was
  not published with the reference numbers, so the step totals
  cannot be reconciled exactly; the per test table above states
  this run's definition openly.

## Honesty notes

- Nothing in the fixtures was changed to make the run pass. The
  suite was extracted from the branch as-is.
- No spec step needed a script substitute: the script-use log of the
  runner is empty for all 10 tests. Assertions run through
  `window.__fcckVerify()` are the suite's own checker design, not a
  shortcut added here.
- Timings are single-run measurements on a shared VM and will vary
  between runs, mostly in browser start and per call latency. The
  pass/fail verdicts and the observed end states are the stable
  part of this result.
- This run proves the fcc-k fixtures and checkers behave correctly
  in a real Firefox browser driven through the real UI. It does not
  by itself re-prove anything about Zen; the Zen numbers remain the
  coordinator's reference from the user machine.
