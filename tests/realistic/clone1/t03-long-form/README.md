# t03-long-form: long multi-field form

## Context

A problem setter creates a new problem on a judge site. The creation
form has 14 fields: title, short name, time limit, memory limit,
difficulty, problem type, tags, statement, input format, output format,
sample input, sample output, checker, and author notes. Required fields
are title, statement, sample input, and sample output, and the limits
must be numbers in range.

## Goal

Submit the form empty and see validation errors, then fill all 14
fields correctly and reach the success summary.

## Steps

1. Open the fixture page.
2. Click `Create problem` with the form empty.
3. Read the error list.
4. Fill all 14 fields with valid values.
5. Click `Create problem` again.
6. Read the success summary.

## Pass conditions

- The empty submit shows at least 4 errors, naming title, statement,
  sample input, and sample output.
- After filling all fields, the summary contains the title and states
  that 14 fields were received.
- No error remains after the successful submit.

## Fail conditions

- The empty submit shows no errors, or fewer than 4.
- The successful submit still shows errors.
- The summary is missing or does not contain the title.

## Notes

The fixture validates in the page. No data leaves the machine. The
browser run is Playwright Chromium; the same flow on Firefox or Zen
is UNVERIFIED.
