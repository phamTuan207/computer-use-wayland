# Plan, task 4, settings

Goal: notifications on, dark mode on, language Vietnamese,
volume 70, font size 16, saved.

## Alternatives considered

1. Set the volume slider by clicking at the 70 percent position.
   Click position maps to value only approximately on a range
   input, so the saved value can land off target.
2. Focus the slider and use arrow keys counted from the live
   value (starts at 20, so 50 presses right). Exact, at the cost
   of more key actions inside one batch.

Chosen: alternative 2 for the slider, plain clicks and a select
for the rest, one batch, middle checkpoint before saving.

## Steps

```json
[
  {"op": "checkpoint", "name": "start"},
  {"op": "click", "id": "set-notify"},
  {"op": "click", "id": "set-dark"},
  {"op": "select", "id": "set-lang", "value": "vi"},
  {"op": "set_range", "id": "set-volume", "value": 70},
  {"op": "type", "id": "set-font", "text": "16"},
  {"op": "checkpoint", "name": "middle"},
  {"op": "click", "id": "set-save"},
  {"op": "checkpoint", "name": "end"}
]
```
