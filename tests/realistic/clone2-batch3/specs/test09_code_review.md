# Test 09, code review diff

## Goal

Prove an agent can do a realistic pull request review in a real
browser on a fully offline page: read the PR header and status
badge, count diff lines by type from the DOM, switch between
changed files, post line comments through a composer, and submit
reviews under explicit rules, verifying every outcome from DOM
state, the badge, the comment counter, and the review history.

Fixture: fixtures/test09_code_review.html, fully offline, inline
CSS and JS. One PR, "Add retry logic to the payment client",
opened by alex-dev, status badge starting at Open. Three changed
files, src/retry.py with 10 diff lines (4 added, 2 removed,
4 context), src/client.py with 10 lines, tests/test_retry.py
with 8 lines. Every line is numbered and has a Comment button.
A toggle shows or hides unchanged context lines.

## Fixture review rules

- Posting a comment requires non-empty text. A posted comment
  appears under its line and increments the header comment
  counter by one.
- Submitting a review requires choosing Approve or Request
  changes. With no option chosen the submit is blocked, an error
  is shown, the badge does not change, and no history entry is
  added.
- Request changes additionally requires at least one posted
  comment or non-empty summary text. With comments present, an
  empty summary is allowed.
- The fixture allows multiple reviews. Each successful submit
  appends one entry to the review history with the decision and
  the summary (or "(no summary)"), clears the summary box and
  the radio choice, and moves the status badge to the latest
  decision, Approved or Changes requested. There is no lock
  after the first review.

## Steps

1. Start the browser and load the fixture.
2. Read the header, verify the PR title and that the badge
   starts at Open.
3. Count diff lines by type in file 1 from the DOM classes,
   expect 4 added, 2 removed, 4 context, 10 total.
4. Uncheck the context toggle, verify 0 context lines are
   visible in file 1.
5. Re-check the toggle, verify 4 context lines are visible.
6. Switch to file 2, verify file 2 is shown, file 1 is hidden,
   the header reads src/client.py, and line 4 is the added
   Session(timeout=10) line.
7. Switch back to file 1.
8. Open the comment composer on file 1 line 5, verify it opens
   under that line.
9. Type the first comment and post it.
10. Verify the comment text appears under line 5 and the
    comment counter reads 1.
11. Open the composer on file 1 line 9, type the second
    comment, and post it.
12. Verify the second comment appears under line 9 and the
    counter reads 2.
13. Click submit review with no option chosen, verify the
    submit is blocked: badge still Open, history still empty,
    error message shown.
14. Choose Request changes and submit with an empty summary.
    Per the fixture rules this is allowed because comments
    exist. Verify the badge becomes Changes requested and the
    history has one request entry.
15. Choose Approve, write an approval summary, and submit a
    second review.
16. Verify the badge becomes Approved and the history has two
    entries, the second an approve entry containing the
    approval summary text.

## Expected results

Every step ok, every check ok. Comment counter follows 0, 1, 2.
Badge follows Open, still Open after the blocked submit,
Changes requested after the first review, Approved after the
second review. History holds exactly the two successful
submissions, in order.

## Timing

Filled after the verification runs on this machine, headless
Firefox 160.0.1, geckodriver 0.37.1, Selenium venv:

- RESULT ok: true, two consecutive full passes
- Run 1: wall clock 2026-11-21T11:30:25Z to 2026-11-21T11:30:44Z,
  total elapsed 19.3142 s
- Run 2: wall clock 2026-11-21T11:30:52Z to 2026-11-21T11:31:15Z,
  total elapsed 22.8993 s
- Step count: 29, including browser_start
- Checks: 16 of 16 ok on both runs
- Notes: browser_start took 8.8851 s on run 1, most of the total
  variance between runs is browser start. All DOM steps after
  load were sub-second. File 1 counts read from the DOM were
  exactly 4 added, 2 removed, 4 context. The context toggle
  moved visible context lines in file 1 from 4 to 0 and back to
  4. The blocked submit left the badge at Open with an empty
  history, the request changes submit with comments and an
  empty summary succeeded per the fixture rules, and the second
  review (Approve) moved the badge to Approved with both
  history entries present in order.
