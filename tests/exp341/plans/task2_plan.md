# Plan, task 2, orders table

Goal: show only Books rows, sorted by amount high to low.

## Alternatives considered

1. Sort first, then filter. Sorting acts on all 12 rows, then the
   filter re-renders from the original data and loses the sort,
   because the fixture filter handler renders from its data array.
   This order fails.
2. Filter first, then sort the visible rows. The sort handler reads
   the rows currently in the table body, so it sorts exactly the
   filtered set. This order works.

Chosen: alternative 2, filter first, then sort.

Correction, added after council review: two honesty fixes to
this file. First, the filter handler detail in alternative 1
(renders from its data array) came from reading the fixture
source, not from a runtime DOM read; no DOM observation exposes
handler internals, so the planning step used source knowledge a
live agent would not have. Second, this file originally claimed
that a step by step agent only discovers the ordering trap
after a failed check. That did not match the arm A script that
actually ran: it filtered first and sorted second, and never
fell into the trap. The chosen order and the steps below are
unchanged.

## Steps

```json
[
  {"op": "checkpoint", "name": "start"},
  {"op": "select", "id": "filter-cat", "value": "Books"},
  {"op": "checkpoint", "name": "middle"},
  {"op": "click", "id": "sort-amount"},
  {"op": "checkpoint", "name": "end"}
]
```
