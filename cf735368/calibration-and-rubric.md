# CF735368 difficulty calibration anchors + rubric

All difficulty ratings in this task are AI-estimated. Rating protocol
(team decision A4): each rating lane first rates the 3 calibration
anchors below with this rubric, then rates the contest problems
independently. Ratings are held by the coordinator until both lanes
have written. Disagreements over one level are recorded explicitly,
never averaged silently.

## Rubric (4 levels, matching CF26 exam categories)

- **Nhan biet (Recognition)**: direct application of one taught
  concept; straightforward simulation or loop; no trick; a student who
  attended the lesson solves it by recalling the pattern.
- **Thong hieu (Understanding)**: one concept but requires
  understanding why it works or a small adaptation (e.g. prefix sum
  with a twist, sorting with a custom comparator, string processing
  with conditions); minor edge cases.
- **Van dung (Application)**: combine 2+ concepts, or apply a known
  algorithm to a new setting (greedy, two pointers, binary search on
  answer, simple DP); edge cases matter; constraints force the right
  complexity.
- **VDC (high application)**: non-trivial insight, optimization, or
  composition of techniques; multiple edge cases; wrong complexity
  times out; requires genuine problem-solving beyond the taught
  template.

Rating dimensions to consider per problem: concepts needed, insight
required beyond the taught template, edge-case density, whether
constraints punish a naive solution, implementation length.

## Calibration anchors (already-used CF26 problems, known category)

All three anchors are from the CF26 "Nhan biet" set (Drive folder
"2. Cuoi khoa" > "Nhan biet"; uploaded by the owner for CF26).
Known category for all three: **Nhan biet**.

### Anchor 1: Bubble Sort (Nhan biet)

- Limits: 10s, 256MB. N up to 2000, distinct Ai, 0 <= Ai < N.
- Task: simulate bubble sort; after each of the N-1 passes, print the
  whole array. Output exactly N-1 lines.
- Why Nhan biet: the algorithm is taught in the lesson; the problem
  is a direct simulation of it. No insight beyond recalling the
  algorithm.

### Anchor 2: Di tim bai de nhat / In Search of an Easy Problem (Nhan biet)

- Limits: 1s, 256MB. n up to 100, each answer 0 (easy) or 1 (hard).
- Task: print "EASY" if all answers are 0, else "HARD" (Codeforces
  1030A).
- Why Nhan biet: single linear scan with a flag; the easiest possible
  conditional problem.

### Anchor 3: Keo Con / Candies range sum (Nhan biet)

- Limits: 5s, 256MB. N up to 10^6, Ci up to 1000, one query [A, B].
- Task: print sum of C[A..B] inclusive.
- Why Nhan biet: one loop (or prefix sum) over a single range; taught
  pattern, generous time limit.

## Calibration check

A lane that rates any anchor above Nhan biet is miscalibrated; it
must state which rubric dimension pushes the anchor up, and the
coordinator records the disagreement. Anchor ratings are part of the
deliverable (they prove the rubric was applied, not just cited).
