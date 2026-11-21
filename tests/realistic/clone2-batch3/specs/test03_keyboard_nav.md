# Test 03, keyboard only navigation

## Goal

Complete a multi section checkout style flow in a real browser
using only the keyboard. No mouse press API is used anywhere in
the test. Focus position is proven at every stop by a focus
indicator element on the page that shows the id of the currently
focused element, updated on focusin.

Fixture: fixtures/test03_keyboard_nav.html, fully offline, inline
CSS and JS only. It has a header nav with 4 links, a form section
(name, email, quantity, a shipping radio pair), an accordion with
3 sections, a data table with 3 selectable rows, and a confirm
area with a checkbox and a submit button ending in a success
message. Interactive elements are reachable by Tab in DOM order
and have visible focus styles.

## Steps

1. Start the browser and load the fixture.
2. Verify the focus indicator reads none before any key press.
3. Press Tab once, verify focus is on nav-home.
4. Press Tab three more times, verify focus passes nav-products
   and nav-help and lands on nav-contact, in that order.
5. Press Shift Tab, verify focus moves back to nav-help.
6. Press Tab, verify focus returns to nav-contact.
7. Press Tab to field-name, type the buyer name into the focused
   field, verify the field value.
8. Press Tab to field-email, type the email, verify the value.
9. Press Tab to field-qty, type 3, verify the value.
10. Press Tab to the shipping radio group, verify focus is on the
    checked radio ship-std, press Arrow Down, verify focus moves
    to ship-exp and ship-exp is selected.
11. Press Tab to acc-btn-1, press Enter, verify the first
    accordion panel expanded.
12. Press Tab to acc-btn-2, press Space, verify the second
    accordion panel expanded.
13. Press Tab twice, past acc-btn-3, verify focus is on row-1.
14. Press Tab to row-2, press Enter, verify row-2 is the selected
    row.
15. Press Tab twice, past row-3, verify focus is on
    confirm-check.
16. Press Tab to submit-btn, press Enter with the terms checkbox
    still unchecked, verify an error is shown and focus moved to
    the first invalid field, confirm-check.
17. Press Space, verify the checkbox is now checked.
18. Press Tab to submit-btn, press Enter, verify the success
    message is shown and names the buyer and row-2.
19. Verify final state: success still visible, selected row kept,
    email kept.
20. Self check: scan the test source and verify it contains no
    mouse press API usage.

## Expected results

- Every focus stop matches the indicator readout exactly, in DOM
  order: nav-home, nav-products, nav-help, nav-contact, back to
  nav-help, nav-contact, field-name, field-email, field-qty,
  ship-std, ship-exp by arrow key, acc-btn-1, acc-btn-2, acc-btn-3
  passed, row-1, row-2, row-3 passed, confirm-check, submit-btn,
  focus forced back to confirm-check on the invalid submit, then
  submit-btn again.
- The invalid submit shows the terms error and moves focus to the
  unchecked checkbox instead of succeeding.
- The valid submit shows a success message naming the buyer and
  the selected row row-2.
- All checks pass and the RESULT line reports ok true.

## Timing

Filled after the verification run on this machine.

- Browser: Firefox headless through the batch 3 harness.
- Result: PASS, RESULT ok true, run at wall clock
  2026-11-21T11:27:54Z to 2026-11-21T11:28:09Z.
- Elapsed: 14.978 s total for the whole test including browser
  start.
- Steps: 21, including browser_start.
- Checks: 36, all ok.
