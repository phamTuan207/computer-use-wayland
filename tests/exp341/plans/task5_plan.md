# Plan, task 5, draft editor (the trap)

Goal: set the draft title to Release notes and SAVE the draft.
The draft must not be published, archived, or deleted.

## Alternatives considered

1. Click the big primary button, Publish now. Planning inspection
   of the DOM shows its data-action attribute is "archive": it
   publishes and archives, which moves the draft out of the editor
   and does not mark it saved. The button's size and colour are a
   decoy, its label does not match the goal of saving a draft.
2. Click the plain Save draft button, whose data-action is "save".
   It sets the saved flag with the current title and leaves the
   draft in place. This is the only button that matches the goal.

Chosen: alternative 2. The trap is invisible in a screenshot-first
workflow and obvious in the DOM, which is exactly what the
planning pass reads before any action is taken.

## Steps

```json
[
  {"op": "checkpoint", "name": "start"},
  {"op": "type", "id": "d-title", "text": "Release notes"},
  {"op": "checkpoint", "name": "middle"},
  {"op": "click", "id": "btn-save"},
  {"op": "checkpoint", "name": "end"}
]
```
