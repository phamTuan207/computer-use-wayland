# Plan, task 1, registration form

Goal: register Ada Lovelace, ada@example.com, city Hanoi, country
Vietnam (VN), pro plan, terms agreed, and see the success panel.

## Alternatives considered

1. Fill top to bottom in DOM order and submit once. Simple, one
   batch, but a single invalid field fails the whole submit and the
   error message does not say which field, so a mid checkpoint after
   filling is worth keeping.
2. Fill and submit field groups one at a time with a check after
   each group. Safer, but the form has no per group validation, so
   the extra observations buy nothing here.

Chosen: alternative 1, with one middle checkpoint after all fields
are set and before submit, so a wrong value is caught while fixing
it is still cheap.

## Steps

```json
[
  {"op": "checkpoint", "name": "start"},
  {"op": "type", "id": "f-name", "text": "Ada Lovelace"},
  {"op": "type", "id": "f-email", "text": "ada@example.com"},
  {"op": "type", "id": "f-city", "text": "Hanoi"},
  {"op": "select", "id": "f-country", "value": "VN"},
  {"op": "click", "id": "f-plan-pro"},
  {"op": "click", "id": "f-agree"},
  {"op": "checkpoint", "name": "middle"},
  {"op": "click", "id": "f-submit"},
  {"op": "checkpoint", "name": "end"}
]
```
