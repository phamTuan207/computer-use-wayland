# CF735368 independent review round 2, clone2 lane (remaining 9 problems)

All difficulty ratings in this review are AI-estimated, made with the
rubric in calibration-and-rubric.md (Nhan biet / Thong hieu / Van dung /
VDC), calibrated against the round-1 anchors. Reviewer: clone2,
independent and repo-only. Method: rated from the extracted statements
in this folder only; the parallel solver lane's ratings were not read
or waited for, and the solutions folder was not consulted. Every
sample that ships with a statement was recomputed, by hand and with
throwaway scripts (brute force for game-pick, a value model for
ghep-bong, a derived closed form for chuoi-melodic, exhaustive
permutation check for the oan-tu-ti sample). Review date: 2026-11-27.

## 1. Ratings and justifications

### tin-nhan-to-tinh: Thong hieu (AI-estimated). Intended: Thong hieu. Match.

Concepts: one pass over a string (|S| up to 10^5) tracking the current
run of identical characters and the best run seen. Insight beyond the
taught template: small but real bookkeeping adaptation; the best run
must be replaced only on a strictly longer run so the first of equal
length wins (the stated tie rule), and the final run must be flushed
after the loop, the classic place this exercise goes wrong.
Edge-case density: moderate for its size (single character, whole
string one run, tie between runs, longest run at the very end).
Constraint pressure: none, one linear pass. Implementation length:
about 15 lines. Squarely the rubric's "string processing with
conditions" Thong hieu example.

### ung-dung-hen-ho: Thong hieu (AI-estimated, provisional). Intended: Thong hieu. Match on the visible text only.

The visible condition is: count pairs whose two fate indices sum to a
multiple of the lucky number K. Concepts: remainder classes modulo K
plus frequency counting over the classes (pairs inside class 0, pairs
across classes r and K-r, with the self-pairing care those classes
need). Insight: the naive O(n^2) pair enumeration must be replaced by
counting per remainder class, a standard but genuine adaptation;
the statement itself notes the answer can exceed 32-bit int.
Edge-case density: moderate (the r = K-r classes, K = 1, duplicate
values). Constraint pressure and implementation length cannot be
assessed: the extraction lost every numeric constraint (see the
BLOCKING flag in section 2). On the visible structure this is Thong
hieu; if the missing second condition or the missing constraints add
a second technique or real pressure, the rating would need revisiting.
About 20 lines for the visible problem.

### quy-tac-tinh-yeu: Thong hieu (AI-estimated). Intended: Thong hieu. Match.

Concepts: a two-phase scan implementing the 37 percent rule exactly
as specified: m = (37 * n) / 100 by integer division, prefix maximum
over the first m candidates (with max_score = -1 when m = 0), then a
linear search from position m + 1 for the first score strictly
greater than max_score, falling back to position n when nobody beats
it. Insight beyond the template: none in method, the procedure is
spelled out step by step; the difficulty is fidelity, not discovery.
Edge-case density: the highest among the Thong hieu set (m = 0 for
n <= 2, strict versus non-strict comparison, the fallback rule, the
1-based output position), and each case is pinned by the statement.
Constraint pressure: none (n up to 10^5, one pass). Implementation
length: about 15 lines. It sits at the boundary with Nhan biet; the
multi-phase structure and its four special cases are what keep it at
Thong hieu under the rubric's "minor edge cases" clause.

### giai-cuu-jerry: Van dung (AI-estimated, low end). Intended: Van dung. Match.

Concepts combined: parity classification plus combinatorial pair
counting. A pair has an even sum exactly when both elements share a
parity, so the answer is C(even, 2) + C(odd, 2); the double loop a
fundamentals student reaches for first is O(N^2). Insight: the
counting formula must be derived, the statement gives no hint of
method. Edge-case density: low once the formula is known (all one
parity, N = 1 gives 0). Constraint pressure: real and explicit; the
subtask ladder gives 60 percent of tests at N <= 10^3, where brute
force passes, and reserves 40 percent for N <= 10^5, where it times
out, which is the rubric's Van dung signature. Implementation
length: about 10 lines after the derivation. The low-end note: a
lane that weights the single-insight aspect above the concept
combination and constraint pressure could defensibly call this Thong
hieu; this lane records Van dung because two rubric markers for that
level (2+ concepts combined, constraints force the right complexity)
are both present.

### game-pick: Van dung (AI-estimated). Intended: Van dung. Match.

Task: choose a value x that occurs in the array, delete every
occurrence of x, and in the remaining sequence count adjacent pairs
whose difference exceeds k; minimize that count, ties to the
smallest x. Concepts: adjacency analysis on an array plus an
efficiency insight: deleting x only changes adjacencies at the
occurrences of x (their neighbours become adjacent), so each
candidate value can be scored from its occurrence positions instead
of rescanning the whole array. Insight beyond the template: the
local-effect decomposition, including runs of consecutive x values
(deleting a run merges its two outer neighbours) and end-of-array
occurrences. Edge-case density: high for this set (runs, ends, the
empty remaining sequence when every element equals x, k = 0, ties).
Constraint pressure: real; per-candidate rescans are about 10^10 at
n = 10^5 and only the 40 percent subtask (n <= 10^3) tolerates them.
Implementation length: about 40 lines with the bookkeeping done
carefully. Sample verified by brute force: removing 3, 4, or 5
leaves 2 bad pairs each, removing 6 leaves 0, output 6.

### ghep-bong: Van dung (AI-estimated, low end). Intended: Van dung. Match.

Task: insert balls of types 1, 2, 3 (yellow, orange, red) one by
one; whenever the box holds 2 yellows they merge into 1 orange, and
2 oranges merge into 1 red; answer q queries asking the total number
of balls in the box after the i-th insertion. Insight: the process
is a binary counter. Merging preserves total value when yellow = 1,
orange = 2, red = 4, so after any prefix the box holds
(V mod 2) yellows, ((V / 2) mod 2) oranges and V / 4 reds, where V is
the prefix sum of values; equivalently, simulate three counters with
carry propagation and record the total after each insertion, then
answer queries in O(1). A literal simulation over a list of balls,
rescanning for mergeable pairs, is O(n^2) and fails at n, q = 10^5.
Edge-case density: moderate (cascading merges from one insertion,
queries unsorted and repeated, reds never merging further).
Constraint pressure: moderate, it punishes the wrong model rather
than the wrong constant. Implementation length: about 20 lines.
Sample verified against the value model: queries 3, 5, 6, 8, 10 give
3, 3, 4, 5, 6 exactly. The low-end note mirrors giai-cuu-jerry: the
counter simulation is natural once seen, but seeing it is the
problem, and that is what the rubric prices at this level.

### chuoi-melodic: VDC (AI-estimated). Intended: VDC. Match.

Task: positions divisible by any kept ai become 1 in a binary string
of length 10^18; delete as few array elements as possible so the
result is melodic (periodic, and exactly one 1 in the first minimal
period). The derivation the solver must find: the set of 1 positions
is the union of the multiples of the kept values; for the string to
have minimal period p with exactly one 1 per period, that set must
be exactly the multiples of p, which happens if and only if every
kept value is a multiple of the smallest kept value d (then the
1 set is exactly the multiples of d, since d itself is kept, and the
minimal period is d). So for each distinct d in the array, the best
kept set with minimum d is all elements divisible by d, and the
answer is n minus the largest such count. Concepts composed:
string periodicity, divisibility structure, and optimization over
subsets, behind a 10^18 length that rules out any simulation.
Edge cases: duplicate values (present in sample 1), n = 1 (always
melodic, 0 deletions), all elements equal. Constraint pressure:
ai up to 10^9 with sum of n at most 5000 over all tests makes the
O(n^2) divisibility check per test the intended cost. Implementation
length: about 30 lines once the characterization is proven, which
is the VDC pattern exactly (short code, non-trivial insight).
All four samples verified against the derived rule: 2, 0, 1, 2.

### rut-gon-phan-so: Thong hieu (AI-estimated). Intended: VDC. MISMATCH, two levels.

Task: letters of p are numerator variables, letters of q are
denominator variables; a letter occurrence in q can cancel one
identical occurrence in p. Decide whether cancelling can leave the
numerator spelling exactly "six" and the denominator empty. The
cancellation is forced, not a choice: the denominator must end
empty, so every q letter must cancel against an identical p letter,
and the numerator remainder is then determined as the multiset
difference of the two letter-count vectors. The whole problem is:
count letters in both strings (26 counters), check q is a
sub-multiset of p, and check the difference equals {s: 1, i: 1,
x: 1}. Concepts: one (frequency counting) with the small adaptation
of viewing cancellation as count subtraction, the same family as
tin-nhan-to-tinh and yeu-va-ghet-clb. Insight beyond the template:
recognizing the forced structure, a single step. Edge-case density:
low (a letter over-represented in q, remainder with extra letters).
Constraint pressure: none at all (n, m <= 100, t <= 100; anything
quadratic passes). Implementation length: about 20 lines. Under the
rubric this cannot reach Van dung, let alone VDC: no combined
techniques, no complexity pressure, no non-trivial insight. The VDC
filing appears to price the fraction story rather than the
computation. All five samples recomputed and correct (YES, NO, YES,
NO, NO), and the sample-2 explanation's leftover multiset (numerator
"s", denominator "mi") also recomputes exactly.

### oan-tu-ti: VDC (AI-estimated). Intended: VDC. Match.

Task: Giang will play Rock x times, Scissors y times, Paper z times
in an unknown order; Huy must commit to a full sequence in advance
such that against every ordering of Giang's moves, Huy's wins are
at least Giang's wins; any valid sequence is accepted and one is
guaranteed to exist. Concepts: worst-case (minimax) reasoning over
permutations plus a constructive existence argument; there is no
taught template for "choose a sequence that is robust against all
orderings", and the solver must find the counting invariant that
makes a construction provably safe (the adversary's best response
to a fixed Huy sequence is an assignment problem over the two move
count vectors, and the construction must cap that maximum at 0).
Edge-case density: high (zero counts for some moves, which the
first sample exercises with x = y = 0; t up to 1000 tests with
x, y, z <= 100 each). Constraint pressure: the sizes are small, the
pressure is purely conceptual, which is the VDC signature here.
Implementation length: short once the construction is known, long
to discover. Sample verified exhaustively: for test 2 (1, 1, 2) the
given answer SPSS has worst case Giang wins minus Huy wins equal
to 0 over all distinct orderings of Giang's multiset, so it is
valid; sample 1 also checks out by hand.

## 2. Statement and test flags

Severity scale: BLOCKING means a solver cannot reliably produce the
expected output from the statement as written (concrete failing
input or recomputed sample mismatch required); MINOR means solvable
but with a trap, a gap, or a test-coverage need; NONE means checked
and clean.

### tin-nhan-to-tinh: NONE

Sample recomputed and correct (runs of aabbcccdddeeeff peak at 3,
first longest run is "ccc", matching the note). Statement is
complete: tie rule stated, output format two lines stated.
Coverage recommendation, MINOR: include a test whose longest run
ends at the final character and a single-character string; both are
cheap and they pin the two classic failure points.

### ung-dung-hen-ho: BLOCKING

- BLOCKING, the statement is incomplete in extraction and cannot be
  solved as written. It announces TWO conditions ("thoa man dong
  thoi hai dieu kien") but only one survives extraction (the sum of
  the two fate indices is divisible by the lucky number); the second
  condition's text is missing entirely, along with every formula.
  The sample is consistent with the surviving condition alone
  (n = 4, K = 3, values 1 2 4 5: pairs (1,2), (1,5), (2,4), (4,5)
  by value give 4, matching the output), but if the missing
  condition excludes any pair the visible condition admits, every
  such test diverges and solvers cannot know. The note's pair list
  is also blanked (pairs shown as ": (chia het cho 3)"), so the
  missing condition cannot be reconstructed from the examples.
- BLOCKING (same root cause), all numeric constraints are missing:
  the input section's variable names and ranges for n, K and Ai
  were dropped ("hai so nguyen duong va (, )"), so solvers cannot
  even size their arrays or choose a complexity. Fix: re-extract
  this statement from the Drive doc with its formulas intact
  before the problem is used.

### quy-tac-tinh-yeu: NONE

Sample recomputed and correct (n = 6, m = 2, max_score = 8, first
score above 8 is at position 5). The statement pins every edge case
explicitly: integer division for m, m = 0 gives max_score = -1,
strictly greater, fallback to position n. Coverage recommendation,
MINOR: include n <= 2 (m = 0), a test where nobody beats max_score,
and a test where a later score equals max_score exactly (must not
be chosen).

### giai-cuu-jerry: MINOR

Sample recomputed and correct (odds 1, 3, 5 and evens 2, 4 give
C(3,2) + C(2,2) = 4, and the listed pairs match). Statement is
complete. One MINOR flag: no 64-bit warning. The maximum answer at
N = 10^5 is C(10^5, 2) = 4,999,950,000, which overflows a signed
32-bit int; unlike ung-dung-hen-ho, this statement never warns that
the result can exceed int. Students answering in int will silently
overflow on the large subtask. Fix: add the same note hen-ho has,
or state a 64-bit integer in the output spec.

### game-pick: MINOR

Sample recomputed by brute force and correct, and it also settles
the one real ambiguity: boredom must be counted on adjacencies of
the sequence AFTER deletion (under the alternative reading, pairs
of the original array not touching x, removing 4 would score 0 and
win as the smaller value, contradicting the sample output 6).
MINOR flags: (1) the statement never defines the boredom measure as
a count of offending adjacent pairs in so many words; it is
inferable and sample-confirmed, but one explicit sentence would
remove the doubt. (2) Coverage: include an array where every element
is equal (remaining sequence empty, 0 bad pairs), an x forming a
long consecutive run, and a tie between two values so the
smallest-x rule is exercised.

### ghep-bong: MINOR

Sample recomputed via the value model and correct on all five
queries. Statement is complete about the merge rules, including
that reds do not merge further (no rule is given for them, and the
sample's totals confirm reds accumulate). MINOR flags: (1) the
output layout is unspecified ("gom q so"); the sample prints the
answers space-separated on one line, so state that, or confirm the
checker is whitespace-insensitive. (2) Coverage: include a query
sequence with repeated and out-of-order indices, and an insertion
run that forces a double cascade (yellow completing both a yellow
pair and the resulting orange pair).

### chuoi-melodic: NONE

Statement is mathematically complete (both definitions given with
worked examples), constraints include the sum-of-n bound, and all
four samples recompute correctly under the derived characterization
(all kept values multiples of the kept minimum), agreeing with the
printed explanations. Coverage recommendation, MINOR: include
duplicate-heavy arrays, n = 1, and an array of distinct large primes
(answer n - 1) to pin the optimization direction.

### rut-gon-phan-so: NONE for the statement; category flag recorded in section 1

All five samples and the explanations recompute exactly (verified
by count vectors, including sample 2's leftovers). Statement is
complete, including the one-occurrence cancellation rule. The only
flag is the difficulty filing itself: intended VDC versus assessed
Thong hieu, a two-level mismatch the coordinator should record;
the problem is a sound Thong hieu exercise and needs no statement
fix.

### oan-tu-ti: MINOR (grading harness, not the statement)

Statement is complete and the samples verify (sample 2 checked
exhaustively over Giang's orderings). MINOR flag with a condition:
this is an any-valid-answer constructive problem, so grading must
verify the property (simulate the worst case, or check the known
invariant), not diff the output against a stored string. The file
header says answers for this test set are generated by the setter's
solution.c; if those generated strings are ever used as literal
expected outputs, correct alternative sequences would be marked
wrong, which would make this flag BLOCKING in effect. Confirm a
special judge or verifier is wired for this problem.

## 3. Summary

| Problem | Intended | Clone2 rating (AI-estimated) | Match | Flags |
|---|---|---|---|---|
| tin-nhan-to-tinh | Thong hieu | Thong hieu | yes | NONE (coverage MINOR) |
| ung-dung-hen-ho | Thong hieu | Thong hieu (provisional) | yes, on visible text | BLOCKING (second condition and all constraints lost in extraction) |
| quy-tac-tinh-yeu | Thong hieu | Thong hieu | yes | NONE (coverage MINOR) |
| giai-cuu-jerry | Van dung | Van dung | yes | MINOR (no 64-bit warning) |
| game-pick | Van dung | Van dung | yes | MINOR (measure wording, coverage) |
| ghep-bong | Van dung | Van dung | yes | MINOR (output layout, coverage) |
| chuoi-melodic | VDC | VDC | yes | NONE (coverage MINOR) |
| rut-gon-phan-so | VDC | Thong hieu | NO, two levels lower | none on statement; category mismatch |
| oan-tu-ti | VDC | VDC | yes | MINOR (needs a special judge, not literal diffs) |

Two items for the coordinator: ung-dung-hen-ho must be re-extracted
before use (its statement is missing a condition and all
constraints), and rut-gon-phan-so is misfiled by two levels (a clean
Thong hieu counting exercise filed as VDC). Every sample in this
round was recomputed; no sample mismatch was found in any of the 9
problems.
