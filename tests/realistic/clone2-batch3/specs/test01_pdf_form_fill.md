# Test 01, PDF form fill

## Goal

Prove an agent can complete a PDF style application form in a real
browser: read the initial empty state, recover from a fully invalid
submit, fill every field while a live page preview mirrors the
values, fix a validation error, and finish with a verifiable
submission, reference code, summary, and a downloadable text copy
of the submitted values. The fixture is fully offline, one HTML
file simulating a PDF form viewer and editor.

Fixture: fixtures/test01_pdf_form_fill.html
Test: tests/test01_pdf_form_fill.py

## Steps

1. Start the browser and load the fixture.
2. Verify the initial state: name and email fields empty, preview
   shows the placeholders (not provided) and (not selected), and
   the success panel is hidden.
3. Click submit with the empty form.
4. Read the error summary: it must list every invalid field, full
   name, email, date of birth, country, account type, signature,
   and agree, and the success panel must stay hidden.
5. Type the full name, Nguyen Van An. The preview mirrors it and
   the full name error clears live.
6. Type an invalid email, notanemail. The preview mirrors it and
   the email error is present in the summary.
7. Clear the email and type the valid vanan@example.com. The
   email error clears and the preview shows the corrected value.
8. Set the date of birth to 1990-05-15. The field value and the
   preview both read 1990-05-15.
9. Select the country Japan. The preview mirrors Japan.
10. Choose the Business account type radio. It is selected and
    the preview mirrors Business.
11. Type the notes text. The preview mirrors it.
12. Type the signature, the full name again. The preview mirrors
    it.
13. Check the agree checkbox. It is selected and the preview
    agree line reads Yes.
14. Verify the form is fully valid: the form reports valid, the
    submit button is enabled, no errors remain, and the error
    summary is hidden.
15. Submit the form. The success panel becomes visible.
16. Read the reference code and verify its format, REF- followed
    by 8 uppercase letters or digits.
17. Read the success summary and verify it contains every typed
    value: name, email, date of birth, country, account type,
    notes, and the reference code.
18. Read the download link: its href is a data URI, and the
    decoded content contains the submitted name, email, and
    reference code.

## Expected results

- Every validation rule fires on the empty submit, and errors
  clear field by field as values are corrected, without another
  submit attempt.
- The PDF preview mirrors each field as it is filled.
- A valid submit shows the success panel with a reference code
  matching REF- plus 8 uppercase alphanumeric characters.
- The read only summary equals what was typed, and the data URI
  download contains the same values as text.
- The test prints RESULT with ok true.

## Timing

Verified run on the clone2 machine, headless Firefox, real
browser through Selenium:

- Date: 2026-11-21
- Wall clock: 2026-11-21T11:27:10Z to 2026-11-21T11:27:34Z
- Total elapsed: 23.6972 s
- Steps: 19, including browser start, all ok
- Checks: 32, all ok
- RESULT: ok true
