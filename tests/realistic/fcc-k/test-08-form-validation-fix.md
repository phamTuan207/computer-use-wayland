# test-08-form-validation-fix.md

## Test ID
test-08-form-validation-fix

## Topic
Form with validation errors: submit, read errors, fix each, resubmit.

## Context
Pham Tuan fills a local registration form that has field-level validation. The
first submit intentionally fails with multiple errors (empty required fields,
bad email format, password too short, password mismatch). The agent must submit,
read each validation error message, fix the offending fields one at a time, and
resubmit until all errors clear. This tests reading error text precisely,
locating fields by their error association, and iterative correction.

## Goal
Fill the registration form, submit to reveal 4 validation errors, fix each error
field, resubmit, and reach a clean success state with zero remaining errors.

## Exact steps
1. Open the form fixture `fixtures/test-08-form.html` in the local browser
   (offline, file:// URL).
2. Verify the form is visible with fields: Full name, Email, Password, Confirm
   password, and a Submit button.
3. Type a full name into the Full name field.
4. Leave Email empty for now (this triggers an error on submit).
5. Type a short password (4 characters) into Password (triggers too-short).
6. Type a different value into Confirm password (triggers mismatch).
7. Click Submit.
8. Read all validation error messages shown (expect 3-4 errors).
9. Fix the Email field: type a valid email address.
10. Fix the Password field: type a longer password (>= 8 characters).
11. Fix the Confirm password field: type the same password as step 10.
12. Click Submit again.
13. Read remaining errors (expect fewer).
14. If any error remains, fix that field and resubmit (repeat until zero
    errors).
15. Confirm a success message appears and no error text remains.
16. Read back all field values as the final state.

## Pass/fail criteria
- Pass: first submit shows errors, each error field fixed and cleared on
  resubmit, success message shown, zero remaining errors, final field values
  correct.
- Fail: an error never cleared, submit succeeds while an error is visible,
  wrong field edited, final values wrong.

## What to time
- Per-step wall time for each type/click/read (16 steps, ~20 field actions).
- Total wall time from step 1 to step 16.
- Number of submit attempts and time per attempt (error-fix iteration count).
- Time re-reading error list after each submit (stale observation check).

## Errors designed to expose
- click miss: clicking the wrong field, Submit before all fields are filled.
- slow think: long pause between reading an error and fixing the field.
- stale observation: reading the error list after fixing but before resubmitting,
  trusting old errors.
- wrong diagnosis: concluding validation failed when the same value was retyped
  with a different case.
- fabrication: claiming an error cleared without resubmitting and reading.

## Checker / expected end state
Checker script: `tests/realistic/fcc-k/check.mjs --fixture
fixtures/test-08-form.html --test 08`.
Expected end state: form valid (name filled, valid email, password >= 8 chars,
confirm matches), success message shown, zero validation errors, final values
recorded.