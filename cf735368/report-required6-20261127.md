# CF735368 trial report, required 6 problems (27/11/2026)

Task: solve + submit Hieu's 10 final-exam problems in Codeforces
contest 735368 (group EoMGcsRgKH) to check for errors and assess
difficulty before the Sun 29/11/2026 exam. This report covers the
required first 6. Exam problems 7-10 (optional) are NOT covered yet.

## Access status (read first)

Codeforces access FAILED: the owner's Zen profile renders anonymous
on Codeforces (stored session invalid server-side; Cloudflare itself
is passable with the Fix B holder shim). No login was attempted by
the driver lane (no password entry per brief). **No Codeforces
verdict exists for any problem in this report.** All verdicts below
are local full-suite results against the Drive test sets (Plan B).

Plan B sources: Drive folder "2. Cuoi khoa" holds 15 problem
packages (5 Nhan biet, 4 Thong hieu, 3 Van dung, 3 VDC), each with a
statement doc, a setter solution.c, and a testcases.zip. Contest
735368 holds 10 of the 15; exact membership could not be confirmed
without Codeforces login. Best-supported composition (Thong hieu
testcases are lettered F-I): A-E = 5 Nhan biet, F-I = 4 Thong hieu,
J = 1 more. The required-6 scope used here is therefore the 5 Nhan
biet problems plus Yeu va Ghet CLB (F). If the contest order
differs, the remaining 9 Drive problems still get checked in the
optional phase, so full coverage lands before 29/11 either way.

Method: Codex (gpt-6-luna) solved each problem blind from the
statement, tested locally (samples + self-made edge cases), then
the coordinator re-ran every solution on the VM against the full
Drive test suite (expected outputs: stored Polygon answers where
present, otherwise the setter's solution.c compiled as reference).
Clone2 reviewed statements independently (difficulty + error flags).
Difficulty ratings are AI-estimated, calibrated on 3 already-used
CF26 Nhan biet anchors (both lanes rated all 3 anchors Nhan biet,
matching the known category).

## Summary table

| Problem | Verdict (local suite) | Difficulty intended vs assessed (AI-estimated) | Errors (severity) | Action for Hieu |
|---|---|---|---|---|
| bao-nhieu-bi | PASS 80/80 vs setter ref | Nhan biet vs Nhan biet (both lanes) | **BLOCKING**: statement index base undeterminable, no sample. Tests are consistent 1-based (verified). | Fix statement before exam: state 1-based i/j ranges, add one sample. |
| tong-ket-nam-hoc | PASS 80/80 vs setter ref | Nhan biet vs Nhan biet (both lanes) | MINOR: no sample; rounding rule unstated (verified: 0/80 tests hit an exact half, so no live trap). | Add a sample; optionally state rounding rule. |
| di-tim-bai-de-nhat | PASS 30/30 vs stored answers | Nhan biet vs Nhan biet (both lanes) | NONE | None. |
| keo-con | PASS 30/30 vs stored answers | Nhan biet vs Nhan biet (both lanes) | MINOR: setter solution.c in Drive does not compile (variable `a` redeclared). Stored answers are fine. | Replace/fix solution.c in Drive; confirm the Polygon solution compiles. |
| bubble-sort | PASS 30/30 vs stored answers | Nhan biet vs Nhan biet (both lanes) | MINOR: statement recap lost symbols in Drive extraction; sample output has trailing spaces (checker tolerance unverified). Coverage OK (N=1, sorted present). | Restore recap text; confirm checker whitespace tolerance. |
| yeu-va-ghet-clb | PASS 50/50 vs setter ref | Thong hieu vs Thong hieu (Clone2) / Nhan biet (Codex) - disagreement recorded | NONE in statement/tests (coverage verified thorough). Difficulty one level below intended per Codex lane. | None required. Note the difficulty disagreement. |

## Per-problem detail

### bao-nhieu-bi (Nhan biet) - PASS 80/80, BLOCKING statement flag

- Solution: read m x n matrix, print it, print A[i][j]. Codex assumed
  1-based i/j from the visible statement fragments; the coordinator
  verified all 80 test queries use i, j in [1,100] and the 1-based
  solution matches the setter reference on every test. The setter's
  semantics are 1-based.
- BLOCKING (statement, Clone2): the index ranges in the Drive
  statement are mangled ("(0 < i <= m)", "(0 < <= n)") and there is
  no sample, so a student cannot determine 1-based vs 0-based.
  Concrete divergence: matrix [[5,7],[9,11]], query i=1, j=1 prints
  5 (1-based) vs 11 (0-based). All 80 tests grade this ambiguity.
  The tests themselves are internally consistent; the statement is
  what must be fixed before the exam.
- MINOR: input layout for i, j implied not stated; "line 1 / line 2"
  output wording is loose for an m-line print; element value range
  unstated.

### tong-ket-nam-hoc (Nhan biet) - PASS 80/80, MINOR flags

- Solution: average, max, count of scores >= 5.0, printed with one
  decimal. Matches setter reference token-wise on all 80 tests.
- MINOR (Clone2): rounding at exact halves (printf %.1f rounds
  half-to-even; schoolbook rounds half-up; e.g. average 7.25 prints
  7.2 vs 7.3). Coordinator check: 0 of 80 tests produce an exact
  half for average or max, so the trap does not fire on the current
  test set. No sample ships with the statement. Coursework
  scaffolding text ("write functions that...") is mixed into the
  judge spec.

### di-tim-bai-de-nhat (Nhan biet) - PASS 30/30, NONE

- Codeforces 1030A. Both samples recomputed correct. Setter
  solution matches stored answers 30/30; our solution matches 30/30.
  Statement, constraints, output complete and consistent.

### keo-con (Nhan biet) - PASS 30/30, MINOR flag

- Range sum [A, B], 0-based, N up to 10^6. All 3 samples recomputed
  correct. Our solution matches stored answers 30/30.
- MINOR (coordinator finding): the setter's solution.c in Drive
  does not compile: `int a[n];` (array) followed by `int a, b;`
  redeclares `a`. The stored Polygon answers exist and are
  consistent with an independent solution, so the contest problem
  itself is most likely fine; the Drive solution file is broken
  and should be replaced. Whether the Polygon-side solution is the
  same broken file could not be checked (no access).
- Cosmetic MINOR (Clone2): story paragraph attaches "(0 <= i < N)"
  to the Ci definition; the input section is clear, so no real risk.

### bubble-sort (Nhan biet) - PASS 30/30, MINOR flags

- Simulate bubble sort, print array after each of N-1 passes.
  Sample recomputed by simulation, matches. Setter solution matches
  stored answers 30/30; our solution matches 30/30.
- MINOR (Clone2): the algorithm recap lost its symbols in the Drive
  doc extraction (the output section still pins behavior exactly,
  so solvable as written; restore for students). Sample output
  lines carry trailing spaces; if the checker is not
  whitespace-tolerant, student output without trailing spaces could
  be judged wrong (unverifiable without Codeforces access).
  Coverage verified by coordinator: N=1 present (1 test),
  already-sorted present (4 tests).

### yeu-va-ghet-clb (Thong hieu) - PASS 50/50, difficulty disagreement

- Frequency counting; output least-frequent and most-frequent member
  IDs, ties by smallest ID, least-frequent must appear at least
  once. Both samples recomputed correct (including the max tie).
  Our solution matches setter reference 50/50. Coordinator coverage
  check: 1445 cases across 50 tests, including 375 min-frequency
  ties, 463 n=1 cases, 1254 sparse-large-ID cases. Statement and
  tests are clean.
- Difficulty disagreement (recorded, not averaged): Clone2 rated
  Thong hieu (matches intended): the min-over-present-IDs rule and
  the tie-break direction flip are adaptations a recall-only student
  gets wrong. Codex rated Nhan biet: "small enough for a
  straightforward ordered map". One level apart; Clone2's reading
  matches the intended category.

## Prioritised fix list for Hieu

1. **bao-nhieu-bi statement (BLOCKING)**: restore the index ranges
   (1-based: 0 < i <= m, 0 < j <= n) and add one sample with the
   query line. Without this, the problem grades a guess.
2. **keo-con Drive solution.c**: replace the uncompilable file
   (rename the query variables, e.g. `int x, y;`); confirm the
   Polygon solution compiles and matches the stored answers.
3. **tong-ket-nam-hoc**: add one sample showing the one-decimal
   format; optionally state the rounding rule (no test currently
   hits an exact half, verified).
4. **bubble-sort**: restore the recap symbols in the statement;
   confirm the checker tolerates trailing-space differences.
5. Optional: note the yeu-va-ghet-clb difficulty disagreement
   (one lane reads it as Nhan biet); no change needed unless the
   exam balance depends on it.

## What was NOT checked

- **No Codeforces verdicts.** Login failed (anonymous session);
  nothing was submitted. All verdicts above are local full-suite
  runs against Drive test sets. If owner login is arranged, real
  submissions can still be made from the committed solutions.
- **Contest membership**: which exact 10 of the 15 Drive problems
  are in contest 735368, and their contest order, are unconfirmed.
  The required-6 scope follows the best-supported composition
  (5 Nhan biet + F). The remaining 9 Drive problems are unchecked
  so far (optional phase, after this report).
- **Polygon-side configuration**: checker type (special judge for
  the float-output problem tong-ket-nam-hoc; whitespace tolerance
  for bubble-sort), Polygon solution files, and time limits on
  Codeforces hardware. Local runs were all fast (well under 1s per
  test except bubble-sort output volume), but that is not a
  Codeforces time-limit proof.
- **Statement samples on Codeforces** may differ from the Drive
  docs (the Drive docs are the source used here; bao-nhieu-bi and
  tong-ket-nam-hoc docs ship no samples).

## Artifacts

- Statements: cf735368/problem-<slug>.md (15 files, commit cb8bd087)
- Solutions + test logs + difficulty: cf735368/solutions/<slug>/
  (commits 806dce3c, 2a476272, 1bb20fbf, be7f25eb, 71df212b, ef22f669)
- Anchor ratings: cf735368/solutions/anchor-ratings.txt
- Independent review: cf735368/clone2-review.md
- FCC capability probe (PASS, gate for blind re-solve duty):
  cf735368/fcc-probe-result.md (commit 1e470472). No blind re-solve
  was triggered: no suite mismatches occurred.
- Calibration + rubric: cf735368/calibration-and-rubric.md
- Event log: master event log, sources cf735368-coordinator,
  cf735368-driver, cf735368-codex, cf735368-fcc-probe.
