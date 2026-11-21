# Plan, task 6, cart

Goal: Keyboard x2 and Mouse x1 in the cart, discount code SAVE10
applied, total 112.50.

## Alternatives considered

1. Add the Keyboard once, then use the cart line + button to raise
   its quantity to 2. Works, but the + button only exists after
   the first render and its selector depends on cart state.
2. Click the product Add button twice for the Keyboard. The add
   handler increments the same counter, no state dependent
   selector needed, one less distinct element to locate.

Chosen: alternative 2, then Mouse once, then the code, with the
middle checkpoint after the items are in and before the code, so a
wrong quantity is caught before money is involved.

## Steps

```json
[
  {"op": "checkpoint", "name": "start"},
  {"op": "click", "id": "add-kbd"},
  {"op": "click", "id": "add-kbd"},
  {"op": "click", "id": "add-mouse"},
  {"op": "checkpoint", "name": "middle"},
  {"op": "type", "id": "code", "text": "SAVE10"},
  {"op": "click", "id": "apply-code"},
  {"op": "checkpoint", "name": "end"}
]
```
