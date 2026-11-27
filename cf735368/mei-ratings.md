# Mei independent difficulty ratings, CF735368 tiebreak

All ratings AI-estimated. Method: rated from the four problem statements
plus cf735368/calibration-and-rubric.md only. I did not read
cf735368/clone2-review.md, cf735368/clone2-review-2.md, the solutions
folder, or any lane report before rating.

Disclosure: during an unrelated watchdog check at 07:18 on 2026-11-27,
before this assignment existed, I ran a grep over the Clone2 review
round 2 commit that returned two short lines mentioning rut-gon-phan-so
(its category flag recorded in section 1, and the flag concerned the
difficulty filing, intended VDC versus assessed). I did not read the
full review. My rut-gon-phan-so rating below is derived from the
statement itself; the coordinator may weigh that partial exposure as
it sees fit.

## Calibration anchors (rated first, per rubric protocol)

- Bubble Sort: Nhan biet. Direct simulation of a taught algorithm,
  N-1 passes printing the array. No insight beyond recall.
- Di tim bai de nhat: Nhan biet. Single linear scan with a flag,
  print EASY or HARD. The easiest conditional pattern.
- Keo Con: Nhan biet. One loop or prefix sum over a single range,
  taught pattern, generous limit. No miscalibration: all three
  anchors match their known Nhan biet category.

## 1. Giai Cuu Jerry: Thong hieu

- The parity insight is the whole step: a_i + a_j is even exactly
  when both are odd or both even, so the answer is C(odd,2) +
  C(even,2) from one linear scan.
- That is one concept with a small adaptation (count by parity class
  instead of enumerating pairs), matching Thong hieu, not a
  combination of two techniques or a known algorithm in a new setting.
- The 60/40 constraint split punishes naive O(N^2) on 40% of tests,
  but the fix is the same single insight, and the only edge case is
  64-bit output (up to about 5e9 pairs).
- Drive folder says Van dung; I rate one level lower.

## 2. Rut Gon Phan So: Thong hieu

- The problem is a multiset comparison: count letters in p and q,
  cancel one-for-one, then the numerator must be exactly {s,i,x}
  and the denominator empty.
- That is one taught concept (frequency counting) plus a small
  adaptation (exact target multiset plus the empty-denominator
  condition), matching Thong hieu.
- Constraints are tiny (n, m <= 100, t <= 100) and punish no naive
  solution; there is no second technique, no optimization, and no
  non-trivial insight chain.
- Drive folder says VDC; I rate two levels lower.

## 3. Chuoi Melodic: VDC

- The solver must translate "melodic" into 1s exactly at multiples
  of some period p, then prove p must itself be a kept element and
  every kept element must be a multiple of p.
- That reduces the problem to max over distinct values v of the
  count of array elements divisible by v, with answer n minus
  that max.
- The chain is several non-obvious reasoning steps about an
  infinite string, with no taught template to recall, matching VDC.
- Drive folder says VDC; I agree.

## 4. Tin Nhan To Tinh: Nhan biet

- One linear scan tracking the current run and the best run solves
  it directly; the statement even spells out the leftmost tie-break,
  so no adaptation is needed.
- No trick, no second concept, no edge case beyond a one-character
  string; a student who attended the lesson recalls the pattern.
- That is direct application of one taught concept, matching
  Nhan biet.
- Drive folder says Thong hieu; I rate one level lower.
