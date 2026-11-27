# CF735368 trial report, all 15 Drive problems (27/11/2026)

Task: solve + submit Hieu's 10 final-exam problems in Codeforces
contest 735368 (group EoMGcsRgKH) to check for errors and assess
difficulty before the Sun 29/11/2026 exam. This is the consolidated
report: it covers all 15 Drive packages (the required 6 from the
interim report `report-required6-20261127.md` plus the remaining 9),
so every candidate exam problem is checked regardless of which 10
are in the contest.

## Access status (read first)

Codeforces access FAILED: the owner's Zen profile renders anonymous
on Codeforces (stored session invalid server-side; Cloudflare itself
is passable with the Fix B holder shim). No login was attempted by
the driver lane (no password entry per brief). **No Codeforces
verdict exists for any problem.** All verdicts below are local
full-suite results against the Drive test sets (Plan B).

Plan B sources: Drive folder "2. Cuoi khoa" holds 15 problem
packages (5 Nhan biet, 4 Thong hieu, 3 Van dung, 3 VDC), each with a
statement doc, a setter solution.c, and a testcases.zip. Contest
735368 holds 10 of the 15; exact membership could not be confirmed
without Codeforces login. Best-supported composition: the Thong
hieu docs carry letter headings F (yeu-va-ghet-clb), G
(tin-nhan-to-tinh), H (ung-dung-hen-ho), I (quy-tac-tinh-yeu), so
A-E = 5 Nhan biet, F-I = 4 Thong hieu, J = 1 more (one of the Van
dung / VDC set). All 15 are checked here either way.

Method: Codex (gpt-6-luna) solved each problem blind from the
statement, tested locally (samples + self-made edge cases), then
the coordinator re-ran every solution on the VM against the full
Drive test suite (expected outputs: stored Polygon answers where
present, otherwise the setter's solution.c compiled as reference).
Clone2 reviewed statements independently in two rounds (difficulty
+ error flags). One Codex failure (oan-tu-ti) triggered a blind
re-solve by FCC per protocol. Difficulty ratings are AI-estimated,
calibrated on 3 already-used CF26 Nhan biet anchors (both lanes
rated all 3 anchors Nhan biet, matching the known category).
Multi-level difficulty disagreements were sent to Mei for a third
independent rating.

Correction to the interim report: two flags there (bao-nhieu-bi
BLOCKING, bubble-sort recap MINOR) were partly artifacts of Drive
text extraction (Google Docs equation objects are not exposed via
the Docs API). Formulas were recovered by PDF export on 27/11 and
the flags re-graded below; the recovered formulas are appended to
the statement files (commit 415d8dbd).

## Summary table

| Problem | Verdict (local suite) | Difficulty intended vs assessed (AI-estimated) | Errors (severity) | Action for Hieu |
|---|---|---|---|---|
| bao-nhieu-bi (NB) | PASS 80/80 vs setter ref | Nhan biet vs Nhan biet (both lanes) | MINOR (downgraded from BLOCKING after formula recovery): doc's j range malformed "(0 < <= n)"; input order muddled; no sample. Tests consistent 1-based (verified). | Fix the j range, state input order, add one sample. |
| tong-ket-nam-hoc (NB) | PASS 80/80 vs setter ref | Nhan biet vs Nhan biet (both lanes) | MINOR: no sample; rounding rule unstated (verified: 0/80 tests hit an exact half). | Add a sample; optionally state rounding rule. |
| di-tim-bai-de-nhat (NB) | PASS 30/30 vs stored answers | Nhan biet vs Nhan biet (both lanes) | NONE | None. |
| keo-con (NB) | PASS 30/30 vs stored answers | Nhan biet vs Nhan biet (both lanes) | MINOR: setter solution.c in Drive does not compile (variable `a` redeclared). Stored answers fine. | Replace/fix solution.c in Drive; confirm the Polygon solution compiles. |
| bubble-sort (NB) | PASS 30/30 vs stored answers | Nhan biet vs Nhan biet (both lanes) | MINOR: sample output trailing spaces (checker tolerance unverified). Recap-symbol flag was an extraction artifact (recovered: "n - 1" passes, pass "i"). | Confirm checker whitespace tolerance. |
| yeu-va-ghet-clb (TH, F) | PASS 50/50 vs setter ref | Thong hieu vs Thong hieu (Clone2) / Nhan biet (Codex) - 1-level disagreement | NONE in statement/tests (coverage verified thorough). | None required. Note the difficulty disagreement. |
| tin-nhan-to-tinh (TH, G) | PASS 50/50 vs setter ref | Thong hieu vs Thong hieu (Clone2) / Nhan biet (Codex, Mei) - 2 of 3 lanes one level below intended | NONE (coverage: single-char 2, end-run 7, ties 16). | None required; difficulty may sit at Nhan biet. |
| ung-dung-hen-ho (TH, H) | PASS 50/50 vs setter ref | Thong hieu vs Thong hieu (both lanes; Clone2 provisional pre-recovery) | MINOR (downgraded from Clone2 BLOCKING, which was an extraction artifact): the doc's Note says i <= j while the main text says i < j; setter implements i < j (verified: 47/50 tests have a 2*Ai % K == 0 case, independent i<j solver matched 50/50). | Fix the Note to i < j before the exam. |
| quy-tac-tinh-yeu (TH, I) | PASS 50/50 vs setter ref | Thong hieu vs Thong hieu (both lanes) | NONE (coverage: m=0 in 4, nobody-beats-max 17, equal-to-max 19). | None. |
| giai-cuu-jerry (VD) | PASS 81/81 vs setter ref | Van dung vs Van dung (Clone2) / Thong hieu (Mei) / Nhan biet (Codex) - lanes split across 3 levels | MINOR: no 64-bit warning; 21/81 tests have answer > int32 max (live overflow trap for students using int). | Add the 64-bit note (as ung-dung-hen-ho has). |
| game-pick (VD) | PASS 81/81 vs setter ref | Van dung vs Van dung (both lanes) | MINOR: boredom measure not defined in so many words (sample pins it: counted after deletion). Coverage: all-equal 9, long runs 10. | Add one sentence defining the measure. |
| ghep-bong (VD) | PASS 81/81 vs setter ref | Van dung vs Van dung (both lanes) | MINOR: output layout unspecified (sample prints space-separated on one line). Coverage: repeated queries 54/81, out-of-order 49/81. | State the output layout or confirm whitespace-insensitive checker. |
| chuoi-melodic (VDC) | PASS 81/81 vs setter ref | VDC vs VDC (Clone2, Mei) / Van dung (Codex) - 2 of 3 lanes = intended | NONE. Note: 79% of cases are n=1 (trivial); 3960 non-trivial cases remain, duplicates covered (743). | None required. Optionally rebalance case mix. |
| rut-gon-phan-so (VDC) | PASS 81/81 vs setter ref | VDC vs Thong hieu (Clone2, Mei) / Nhan biet (Codex) - all lanes below intended | NONE on statement/tests. Category mismatch: a frequency-counting exercise filed as VDC. | Refile as Thong hieu (or swap with a harder problem) if the exam balance matters. |
| oan-tu-ti (VDC) | Codex FAIL (invalid 71/81 files, condition checker); setter ref VALID 81/81; FCC blind re-solve VALID 81/81 | VDC vs VDC (Clone2) / Nhan biet (Codex, rating suspect: its solution was wrong) | MINOR (harness): any-valid-answer problem; grading must use a special judge / verifier, never literal diff against setter output. Statement itself is complete; a valid sequence always exists (constant-move strategy). | Confirm a special judge is wired on Polygon/Codeforces. |

## Per-problem detail (optional 9; required 6 in the interim report)

### tin-nhan-to-tinh (Thong hieu, G) - PASS 50/50, NONE

Longest run of identical characters; first longest wins ties.
Sample recomputed correct. Independent solution matches setter
reference 50/50. Coverage verified: single-character strings (2),
longest run ending at the final character (7), tie runs (16).
Difficulty: Clone2 Thong hieu (= intended); Codex and Mei both
Nhan biet (Mei: the statement spells out the tie-break, so no
adaptation is needed). Two of three lanes put it one level below
intended.

### ung-dung-hen-ho (Thong hieu, H) - PASS 50/50, MINOR (Note inconsistency)

Count pairs (i, j), 1 <= i < j <= N, with (Ai + Aj) % K == 0
(N <= 10^5, K <= 10^3, Ai <= 10^9). The Drive doc writes all
formulas as equation objects; the Docs API returns them empty, so
text extraction lost the second condition and every constraint
(Clone2 flagged BLOCKING on the extracted text). PDF export
recovered the full statement (see the recovery note in
problem-ung-dung-hen-ho.md, commit 415d8dbd). The doc itself is
complete. One real defect: the Note restates condition 1 as
"1 <= i <= j <= N" while the main text says i < j. The setter
implements i < j: 47 of 50 tests contain a value with
2*Ai % K == 0 (where i=j would add counts), and the independent
i<j solver matched the setter on all 50. Fix the Note. Difficulty:
Thong hieu, both lanes (Clone2 provisional on pre-recovery text).

### quy-tac-tinh-yeu (Thong hieu, I) - PASS 50/50, NONE

37-percent rule, fully specified (integer division, m=0 fallback,
strict >, fallback to position n). Sample recomputed correct.
Independent solution matches 50/50. Coverage: n<=2 (m=0) in 4
files, nobody-beats-max in 17, later-equal-to-max in 19.
Difficulty: Thong hieu, both lanes (= intended).

### giai-cuu-jerry (Van dung) - PASS 81/81, MINOR (64-bit warning)

Count pairs with even sum = C(even,2) + C(odd,2). Sample
recomputed correct. Independent solution matches 81/81.
Coverage: N=1 in 4 files, single-parity in 14; 21 of 81 tests
have answers above int32 max (max ~4,999,950,000 at N=10^5), and
the statement never warns about 64-bit (unlike ung-dung-hen-ho).
Students answering in int silently overflow on those tests.
Difficulty: lanes split across three levels - Clone2 Van dung
(= intended; two rubric markers: combined concepts + constraints
force O(N)), Mei Thong hieu (one concept, small adaptation; the
60/40 split punishes O(N^2) but the fix is the same single
insight), Codex Nhan biet (single-insight reading). Recorded as a
genuine borderline problem; intended Van dung is defensible but
the median lane reads Thong hieu.

### game-pick (Van dung) - PASS 81/81, MINOR (measure wording)

Choose a value x present in the array, delete all its occurrences,
minimize adjacent pairs (in the remaining sequence) with difference
> k; ties to smallest x. Sample verified by brute force (also pins
the after-deletion reading). Independent solution matches 81/81.
Coverage: all-equal arrays 9 files, runs of >=5 equal values 10.
The statement never defines the boredom measure as a count of
offending adjacent pairs in so many words; one sentence would
remove the doubt. Difficulty: Van dung, both lanes (= intended).

### ghep-bong (Van dung) - PASS 81/81, MINOR (output layout)

Ball merging = binary counter (yellow=1, orange=2, red=4); answer
q prefix queries. Sample verified against the value model.
Independent solution matches 81/81. Coverage: repeated query
indices in 54/81 files, out-of-order in 49/81. The output layout
is unspecified ("gom q so"); the sample prints space-separated on
one line. State it, or confirm a whitespace-insensitive checker.
Difficulty: Van dung, both lanes (= intended).

### chuoi-melodic (VDC) - PASS 81/81, NONE

Delete fewest elements so the multiples-union string is melodic;
the characterization (all kept values multiples of the kept
minimum) gives an O(n^2) divisibility count. All 4 samples
verified. Independent solution matches 81/81. Case mix: 19050
cases total, 15090 with n=1 (trivially 0 deletions), 743 with
duplicate values; the remaining ~3960 non-trivial cases still
discriminate. Difficulty: Clone2 and Mei VDC (= intended; Mei:
several non-obvious reasoning steps about an infinite string, no
taught template), Codex Van dung. Majority = intended.

### rut-gon-phan-so (VDC) - PASS 81/81, category mismatch

Cancel q letters against p; decide whether the remainder spells
exactly "six" with empty denominator. Forced multiset difference;
all 5 samples recomputed correct. Independent solution matches
81/81. Coverage: 3819 cases, 2172 YES, 1001 with q not a
sub-multiset of p. Statement and tests are clean. Difficulty:
intended VDC; Clone2 and Mei Thong hieu, Codex Nhan biet - all
three lanes below intended (frequency counting, n,m <= 100, no
complexity pressure). The VDC filing prices the story, not the
computation. (Mei discloses partial prior exposure: a watchdog
grep at 07:18 returned two lines of Clone2's round-2 review
mentioning this problem's category flag before her assignment
existed; her rating is derived from the statement, and Codex
independently rated even lower, so the below-intended verdict
does not rest on Mei alone.)

### oan-tu-ti (VDC) - lane failure, problem sound; special judge needed

Commit to a move sequence that never loses the win count against
any ordering of Giang's (x, y, z) moves; any valid sequence
accepted, existence guaranteed. The Codex lane's solution was
WRONG (inverted constant-move rule: played all-R when z >= y
instead of y >= z) and its test log falsely claimed PASS
(hand-computed expectations derived from its own wrong rule).
Coordinator condition checker (worst case over all orderings via
assignment problem): Codex invalid on 71/81 files; setter
reference valid on 81/81. A valid sequence always exists (play
all-R if y >= z, all-S if z >= x, all-P if x >= y). FCC blind
re-solve (statement only, commit eea0e316): VALID on all 81
files under the same checker, closing the A3 protocol - the
problem is sound and the Codex failure was lane-only.
Difficulty: Clone2 VDC (= intended); Codex
Nhan biet (discounted: its solution was wrong). Harness flag:
grading must verify the property with a special judge; literal
diff against setter-generated strings would mark correct
alternative sequences wrong.

## Difficulty summary (AI-estimated, all lanes)

- Match intended (all lanes): all 5 Nhan biet, quy-tac-tinh-yeu,
  ung-dung-hen-ho, game-pick, ghep-bong.
- Majority = intended: chuoi-melodic (Clone2, Mei VDC; Codex Van
  dung).
- One level below intended (Codex only): yeu-va-ghet-clb
  (Clone2 = intended Thong hieu).
- Majority one level below intended: tin-nhan-to-tinh (Codex,
  Mei Nhan biet; Clone2 = intended Thong hieu).
- Split across three levels: giai-cuu-jerry (Clone2 Van dung =
  intended, Mei Thong hieu, Codex Nhan biet). Median lane reads
  Thong hieu; intended is defensible.
- Below intended (all lanes): rut-gon-phan-so (intended VDC;
  Clone2, Mei Thong hieu; Codex Nhan biet).
- oan-tu-ti: Clone2 = intended VDC; Codex rating discounted
  (its solution was wrong).

Pattern: the Codex lane systematically rates one level low on
problems whose insight is a single standard trick (frequency
counting, parity formula, divisibility characterization); Clone2
tracks the intended categories closely except rut-gon-phan-so,
where every lane agrees the VDC filing is too high.

## Prioritised fix list for Hieu

1. **keo-con Drive solution.c does not compile** (variable `a`
   redeclared). Replace the file; confirm the Polygon solution
   compiles and matches the stored answers. (If the Polygon-side
   solution is the same file, the problem cannot be validated by
   the setter solution on Codeforces.)
2. **oan-tu-ti grading**: confirm a special judge / verifier is
   wired. Any-valid-answer problem; literal diffs against setter
   output would fail correct solutions.
3. **ung-dung-hen-ho Note**: change "1 <= i <= j <= N" to
   "1 <= i < j <= N" (main text and setter agree on i < j).
4. **bao-nhieu-bi statement**: fix the malformed size range
   "(0 < <= n)" to "(0 < j <= n)", state the input order (m n,
   matrix, then i j), add one sample.
5. **giai-cuu-jerry**: add the 64-bit warning (21/81 tests exceed
   int32).
6. **tong-ket-nam-hoc**: add one sample showing the one-decimal
   format; optionally state the rounding rule (no test hits an
   exact half, verified). Confirm the checker is a float-tolerant
   special judge.
7. **bubble-sort / ghep-bong**: confirm checker whitespace
   tolerance (trailing spaces in sample output; unspecified
   output layout).
8. **game-pick**: one sentence defining the boredom measure as a
   count of adjacent pairs (after deletion) with difference > k.
9. **rut-gon-phan-so difficulty**: refile as Thong hieu (both
   lanes) if the exam's difficulty balance matters.
10. Optional: chuoi-melodic case mix is 79% trivial n=1; harmless
    but could be rebalanced.

## What was NOT checked

- **No Codeforces verdicts.** Login failed (anonymous session);
  nothing was submitted. All verdicts are local full-suite runs
  against Drive test sets. If owner login is arranged, real
  submissions can still be made from the committed solutions.
- **Contest membership**: which exact 10 of the 15 Drive problems
  are in contest 735368, and their order, are unconfirmed (letters
  F-I in the docs support A-E NB + F-I TH + J). All 15 are checked
  here, so coverage does not depend on the answer.
- **Polygon-side configuration**: checker types (special judges
  for tong-ket-nam-hoc floats and oan-tu-ti any-valid answers,
  whitespace tolerance), Polygon solution files (keo-con), and
  time limits on Codeforces hardware. Local runs were fast (all
  suites completed in seconds on the VM), but that is not a
  Codeforces time-limit proof.
- **Statement samples on Codeforces** may differ from the Drive
  docs (the Drive docs are the source used here).
- **Student-level difficulty calibration**: ratings are
  AI-estimated against the CF26 rubric and anchors; no student
  data was used.

## Artifacts

- Statements: cf735368/problem-<slug>.md (15 files, commit cb8bd087;
  formula recovery notes commit 415d8dbd)
- Solutions + test logs + difficulty: cf735368/solutions/<slug>/
  (required 6: 806dce3c, 2a476272, 1bb20fbf, be7f25eb, 71df212b,
  ef22f669; optional 9: b2161d28, cf004ca1, 7665920b, 3b616732,
  61bc091b, 19d6de76, aeaefd72, 836b7209, 00c662ce)
- Anchor ratings: cf735368/solutions/anchor-ratings.txt,
  anchor-ratings-2.txt
- Independent reviews: cf735368/clone2-review.md (round 1),
  cf735368/clone2-review-2.md (round 2)
- FCC capability probe (PASS): cf735368/fcc-probe-result.md
  (commit 1e470472). FCC blind re-solve of oan-tu-ti:
  cf735368/solutions/oan-tu-ti-fcc/ (commit eea0e316, VALID 81/81)
- Mei tiebreak ratings: cf735368/mei-ratings.md (commit cc22d8aa)
- Interim report: cf735368/report-required6-20261127.md
  (commit 5fb01f99)
- Calibration + rubric: cf735368/calibration-and-rubric.md
- Event log: master event log, sources cf735368-coordinator,
  cf735368-driver, cf735368-codex, cf735368-codex2,
  cf735368-fcc-probe, cf735368-fcc-resolve.
