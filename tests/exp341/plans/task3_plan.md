# Plan, task 3, signup wizard

Goal: complete the signup with a valid email and reach the
confirmation code ACC-2026-OK, with the account email
user@example.com, display name Test User, age 30.

## Alternatives considered

1. Trust the prefilled email and password and click Next. Planning
   inspection of the fixture shows the prefilled email has no @
   sign and the prefilled password is 5 characters, under the 8
   minimum stated in the page hint. This path bounces twice on
   validation.
2. Fix both fields up front in step 1, then walk the wizard in one
   batch per step. No validation bounce, checkpoints at the step
   boundaries confirm the wizard advanced.

Chosen: alternative 2. Both defects are visible in the DOM before
any action, so planning removes both retries.

## Steps

```json
[
  {"op": "checkpoint", "name": "start"},
  {"op": "type", "id": "w-email", "text": "user@example.com"},
  {"op": "type", "id": "w-pass", "text": "longenough1"},
  {"op": "click", "id": "w-next1"},
  {"op": "checkpoint", "name": "middle"},
  {"op": "type", "id": "w-name", "text": "Test User"},
  {"op": "type", "id": "w-age", "text": "30"},
  {"op": "click", "id": "w-next2"},
  {"op": "click", "id": "w-confirm"},
  {"op": "checkpoint", "name": "end"}
]
```
