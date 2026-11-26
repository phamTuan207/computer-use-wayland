# CF735368 independent review, clone2 lane

All difficulty ratings in this review are AI-estimated, made with the
rubric in calibration-and-rubric.md (Nhan biet / Thong hieu / Van dung /
VDC). Reviewer: clone2, independent and repo-only. Method: rated from
the extracted statements in this folder only; no solver-lane material
was consulted (the fcc-probe files were not read). Every sample that
ships with a statement was recomputed, by hand and, for the simulation
and counting problems, with a throwaway script. Review date:
2026-11-27.

## 1. Calibration anchors

Known category for all three anchors: Nhan biet.

- **Anchor 1, Bubble Sort: Nhan biet (AI-estimated).** The task is a
  direct simulation of the exact algorithm taught in the lesson: run
  the passes, print the array after each one. No rubric dimension
  pushes it up: one concept (the taught sort), no insight beyond
  recall, constraints (N up to 2000, 10s) do not punish the naive
  O(N^2), and the large output volume is formatting, not difficulty.
- **Anchor 2, Di tim bai de nhat: Nhan biet (AI-estimated).** A single
  linear scan with a flag over n up to 100 values in {0, 1}, printing
  EASY or HARD. This is the floor of the rubric: one loop, one
  condition, no edge cases beyond n = 1. No dimension pushes it up.
- **Anchor 3, Keo Con: Nhan biet (AI-estimated).** One range sum over
  a single query [A, B]: one loop, or a prefix sum the student may
  choose but is not forced to use. N up to 10^6 with a 5s limit is
  generous for a single pass, and the maximum possible sum
  (10^6 x 1000 = 10^9) fits a signed 32-bit int, so there is no
  overflow insight hiding in the constraints. No dimension pushes
  it up.

Calibration result: this lane agrees with the known category on all
three anchors, with no dimension cited as pushing any anchor higher.

## 2. Ratings for the 6 required problems

### bao-nhieu-bi: Nhan biet (AI-estimated). Intended: Nhan biet. Match.

Concepts: one taught concept, 2D arrays (read an m x n matrix, print
it, read one cell by its indices). Insight beyond the template: none;
the lookup is the definition of array indexing. Edge-case density:
minimal (m, n up to 100, no arithmetic, no overflow possible).
Constraint pressure on a naive solution: none, any direct
implementation passes. Implementation length: about 20 lines. The
problem's real defect is its statement, not its difficulty (see the
BLOCKING flag in section 3).

### tong-ket-nam-hoc: Nhan biet (AI-estimated). Intended: Nhan biet. Match.

Concepts: 1D array traversal computing three aggregates in one pass
(sum for the average, maximum, count of values at least 5.0), n up to
10. Insight beyond the template: none; each aggregate is a taught
pattern and they do not interact. Edge-case density: low; the only
subtlety is output rounding to one decimal, a formatting detail, not
a concept (flagged MINOR in section 3). Constraint pressure: none.
Implementation length: about 20 lines.

### di-tim-bai-de-nhat: Nhan biet (AI-estimated). Intended: Nhan biet. Match.

Identical to calibration anchor 2 (Codeforces 1030A). One scan, one
flag, one word of output. Concepts: loop plus conditional. No insight,
no edge cases beyond n = 1, no constraint pressure, about 10 lines.

### keo-con: Nhan biet (AI-estimated). Intended: Nhan biet. Match.

Identical to calibration anchor 3. One query, one inclusive range
sum, 0-based indices stated consistently in the input section.
Concepts: array plus loop (prefix sum optional, not required).
Edge cases: A = B and the full range, both covered by the samples.
No constraint pressure (single pass at N = 10^6 inside 5s is
comfortable; the sum fits int32). About 12 lines.

### bubble-sort: Nhan biet (AI-estimated). Intended: Nhan biet. Match.

Identical to calibration anchor 1. Direct simulation of the taught
algorithm, printing the array after each of exactly N-1 passes.
Concepts: nested loops and swaps only. Insight: none, and the output
spec removes the one possible variation (an early-exit variant would
print fewer lines on nearly sorted input; the statement mandates
exactly N-1 lines, and full scans versus shrinking-range scans give
identical per-pass arrays, so the simulation is unambiguous).
Edge cases: N = 1 means zero output lines. Constraint pressure:
none (N up to 2000, 10s). About 15 lines plus printing.

### yeu-va-ghet-clb: Thong hieu (AI-estimated). Intended: Thong hieu. Match.

Concepts: frequency counting (array indexed by ID up to 10^6, or a
map), then one scan selecting the minimum-frequency and
maximum-frequency IDs. Why this is one level above Nhan biet: the
selection is an adaptation of the plain min/max template in two ways
that a recall-only student gets wrong. First, the minimum is over
IDs that actually appear (frequency at least 1); scanning the whole
frequency array naively returns an absent ID with frequency 0, and
the statement has to call this out explicitly. Second, both extrema
break ties by smallest ID, which flips the comparison direction for
the maximum (strictly greater keeps the first, i.e. smallest, ID) and
must be applied consistently. Edge-case density: moderate (n = 1
gives x = y; all IDs equal; ties at both extrema; per-test reset of
the frequency array across t up to 100 tests, with total n bounded
by 2 x 10^5). Constraint pressure: mild; counting is linear and the
sum-of-n bound keeps it cheap, but a careless full-array rescan per
test is the kind of thing the 1s limit exists to discourage. Why not
Van dung: it is still a single concept with a small adaptation, no
second technique is combined and no algorithm choice is forced.
Implementation length: about 30 lines.

## 3. Statement and test flags

Severity scale: BLOCKING means a solver cannot reliably produce the
expected output from the statement as written (concrete failing input
or recomputed sample mismatch required); MINOR means the statement is
solvable but has a trap, a gap, or a test-coverage need; NONE means
checked and clean.

### bao-nhieu-bi: BLOCKING

- BLOCKING, index base is undeterminable and there is no sample. The
  statement's index ranges were mangled in extraction ("(0 < i <= m)",
  "(0 < <= n)" with the variable missing), and the file ships no
  sample input/output at all, so a solver cannot tell whether the
  query indices i, j are 1-based or 0-based. Concrete divergence:
  matrix [[5, 7], [9, 11]] with query i = 1, j = 1 must print 5 under
  the 1-based reading and 11 under the 0-based reading. The expected
  answers come from the setter's solution.c, which solvers cannot
  see, so the ambiguity decides pass/fail on all 80 tests. Fix:
  restore the index ranges in the statement and add one sample.
- MINOR, input layout for i and j is not pinned (one line after the
  matrix is implied, never stated), and the output description labels
  the whole matrix print as "line 1" and the count as "line 2", which
  is loose wording for an m-line print. Harmless under a token-based
  checker, confusing for students.
- MINOR, no value range is stated for the matrix elements (counts are
  presumably non-negative integers). State it.

### tong-ket-nam-hoc: MINOR

- MINOR, rounding trap at exact halves. Output must be rounded to
  one decimal; the setter's C solution (printf "%.1f" style) rounds
  an exactly representable half to even, while schoolbook rounding
  rounds half up. Concrete case: n = 2, scores 7.0 and 7.5, average
  exactly 7.25; printf prints 7.2, schoolbook rounding gives 7.3.
  Students solving in C with printf match the setter by accident;
  anyone rounding manually may not. Fix: either avoid exact-half
  averages in the tests or state the rounding rule.
- MINOR, no sample input/output ships with the statement, so the
  one-decimal format (e.g. trailing zero, "7.0") is shown nowhere.
- MINOR, the statement mixes coursework scaffolding ("write functions
  that...") into the judge spec. Harmless for grading, worth cleaning
  if the statement is reused.

### di-tim-bai-de-nhat: NONE

Both samples recomputed and correct: (3; 0 0 1) gives HARD, (1; 0)
gives EASY. Statement, constraints (n up to 100, values 0/1), and
output are complete and consistent with CF 1030A.

### keo-con: NONE (one cosmetic MINOR)

All three samples recomputed and correct: 5 + 9 + 10 = 24 for
[1, 3]; 3 for [1, 1]; 16 for the full range [0, 6]. Constraints and
0-based indexing are consistent between the story and the input
section, and the maximum sum fits int32 (verified above), so there
is no hidden overflow trap. Cosmetic MINOR: in the story paragraph
the range "(0 <= i < N)" is attached to the Ci definition where it
reads as a constraint on the values; the input section states the
real constraints clearly, so this cannot mislead a careful reader.

### bubble-sort: MINOR

Sample recomputed by simulation and matches exactly, all 5 lines
(full-scan passes; the shrinking-range variant produces the same
per-pass arrays, so the sample does not hide an ambiguity).
- MINOR, the algorithm recap lost its symbols in extraction ("the
  algorithm consists of [missing] passes; in pass [missing]...").
  The output section still pins the behavior (exactly N-1 lines,
  line i is the array after pass i), so the problem is solvable as
  written, but the recap should be restored for students.
- MINOR, the sample output lines carry trailing spaces. If the
  checker is not whitespace-tolerant, expected outputs generated
  the same way are fine but student output without trailing spaces
  could be judged wrong; confirm the checker normalizes whitespace.
- MINOR, test coverage: include N = 1 (zero output lines) and an
  already sorted array (all N-1 lines identical); both are cheap
  and they pin the no-early-exit rule.

### yeu-va-ghet-clb: MINOR (coverage only; statement itself is clean)

Both samples recomputed and correct, including the tie-break in
sample 2 (IDs 10 and 20 tie at frequency 2, smaller ID 10 wins) and
the note's explanation. Statement is complete: it explicitly says
the least-frequent member must appear at least once, states the
tie-break, and gives the sum-of-n bound. Coverage recommendations,
all MINOR:
- Include a tie at the MINIMUM frequency (the note only demonstrates
  a tie at the maximum); e.g. two IDs appearing once each, smaller
  ID must win x.
- Include n = 1 (x = y = the single ID) and a test where every
  occurrence is the same ID.
- Include a test with sparse large IDs (near 10^6) so solutions that
  scan the frequency array from index 0 and forget the at-least-once
  rule return an absent ID and fail visibly.

## 4. Summary

| Problem | Intended | Clone2 rating (AI-estimated) | Match | Flags |
|---|---|---|---|---|
| bao-nhieu-bi | Nhan biet | Nhan biet | yes | BLOCKING (index base, no sample), 2 MINOR |
| tong-ket-nam-hoc | Nhan biet | Nhan biet | yes | 3 MINOR (rounding halves, no sample, scaffolding) |
| di-tim-bai-de-nhat | Nhan biet | Nhan biet | yes | NONE |
| keo-con | Nhan biet | Nhan biet | yes | NONE (1 cosmetic MINOR) |
| bubble-sort | Nhan biet | Nhan biet | yes | 3 MINOR (extraction gaps, trailing spaces, coverage) |
| yeu-va-ghet-clb | Thong hieu | Thong hieu | yes | MINOR (test coverage only) |

Difficulty calibration: this lane's ratings match the intended
category on all 6 required problems and on all 3 anchors. The one
issue that should block use until fixed is bao-nhieu-bi: its index
base cannot be determined from the statement and it has no sample,
so its 80 tests would grade an ambiguity, not the students.
