# t01-pdf-form: fill a PDF-style form

## Context

A community relief application is published as a 3-page form, like a
fillable PDF: page 1 applicant details, page 2 household details, page 3
signature. The form validates each page, requires a drawn signature, and
saves the submitted record so it survives a reload.

## Goal

Complete the whole form, recover from the validation errors, sign with
the mouse, submit, and prove the record is saved.

## Steps (36)

1. Open the fixture.
2. Check the page title.
3. Fill full name.
4. Fill ID number.
5. Fill an invalid email.
6. Try to go to page 2.
7. Expect an email error.
8. Confirm the form stays on page 1.
9. Fix the email.
10. Go to page 2.
11. Confirm page 2 is shown.
12. Fill street address.
13. Fill city.
14. Fill postcode.
15. Fill monthly income.
16. Select employment type.
17. Check declaration 1.
18. Try to go to page 3 without declaration 2.
19. Expect a declaration 2 error.
20. Check declaration 2.
21. Go to page 3.
22. Confirm page 3 is shown.
23. Try to submit without a signature.
24. Expect a signature error.
25. Draw a signature on the canvas with the mouse.
26. Submit the application.
27. Wait for the confirmation panel.
28. Check the application ID format, RF- plus 6 hex digits.
29. Check the summary shows the name.
30. Check the summary shows the income.
31. Check the summary shows the email.
32. Reload the page.
33. Confirm the record persists after reload.
34. Check the application ID is the same after reload.
35. Start a new application.
36. Confirm the form resets to page 1.

## Pass

All 36 steps run, no validation error appears after it is fixed, the
confirmation shows an ID in the right format, the summary contains the
entered values, the record persists after reload, and reset returns to
page 1.

## Fail

Any step above fails, an expected error does not appear, the ID format
is wrong, the summary misses a value, the record is lost on reload, or
reset does not return to page 1.
