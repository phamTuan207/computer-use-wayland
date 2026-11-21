# t09-diff-review: review a pull request diff

## Context

A code review page for PR #42 with 2 files and 12 diff lines. Lines can
be filtered by file, searched with highlights, and commented on inline.
Threads take replies and can be resolved. Hunks can be stepped through.
A review needs a verdict and a summary, and reviews and threads persist.

## Goal

Find lines by filter and search, comment and reply, resolve a thread,
walk the hunks, submit two reviews, and prove everything persists.

## Steps (24)

1. Open the fixture.
2. Clear the saved review and reload.
3. Check 2 files and 12 lines are shown.
4. Filter to auth.js and check 6 lines.
5. Clear the file filter.
6. Search the diff for token and check 4 lines, 4 highlights, and the
   search info text.
7. Clear the search.
8. Click the await getToken line and check the comment form opened.
9. Type and submit the comment.
10. Check the thread appears with the text and the count is 1.
11. Open the reply box, type and send a reply.
12. Check the reply appears and the count is 2.
13. Resolve the thread and check it hides.
14. Enable show resolved and check the thread is visible with its text.
15. Disable show resolved and add a second comment on the signal line.
16. Check the comment count is 3.
17. Go to the next hunk twice and check the current hunk is api.js.
18. Go to the previous hunk and check the current hunk is auth.js.
19. Submit a review with no verdict and check the error.
20. Choose Request changes, type a summary, and submit.
21. Check the status is Changes requested and the history has 1 review.
22. Choose Approve, type a summary, and submit.
23. Check the status is Approved and the history has 2 reviews.
24. Reload the page and check the status and comments persist.

## Pass

All 24 steps run, filter and search find the right lines, comments,
replies, and resolve work, hunk navigation lands on the right file,
both reviews submit with the right status, and everything persists.

## Fail

Any step above fails, a search count is wrong, a thread is lost, the
wrong hunk is current, or a review does not stick.
