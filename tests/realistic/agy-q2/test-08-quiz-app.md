# test-08-quiz-app.md

## Test ID
test-08-quiz-app

## Topic
Interactive quiz application: multi-question progression, timer and progress tracking, selecting multiple-choice answers, correcting accidental option selection, backwards and forwards navigation, quiz submission, score calculation, and result persistence.

## Context
the owner is completing the systems architecture certification module.
The workstation runs an offline quiz interface (fixtures/test-08-quiz-app.html).
There are 5 questions covering HTTP protocols, Wayland architecture, data structures, CSS compositing, and Unix signals.
The user must navigate question by question, select correct answers, correct an accidental selection on question 3 from "Linked List" to "Hash Table", navigate back to verify question state persistence, submit the quiz, verify the 5/5 (100%) score display, and save the verified results.

## Timing
- Baseline start time: 2026-11-21 17:20:00 Asia/Ho_Chi_Minh
- Expected duration: 150 seconds elapsed
- Maximum allowable latency: 260 seconds elapsed

## Goal
Answer all 5 questions correctly (with error correction on Q3), navigate back and forward to check state retention, submit quiz with 5/5 score, and save results.

## Exact steps
1. Open fixture tests/realistic/agy-q2/fixtures/test-08-quiz-app.html in the browser.
2. Verify quiz title and initial question 1 ("Which HTTP status code represents 'Created'?") is visible.
3. Verify progress indicator (id "progress-text") displays "Question 1 of 5".
4. Click radio option for "201 Created" (id "opt-q1-201").
5. Click "Next Question" button (id "btn-next-question").
6. Verify question 2 text displays "What is the primary role of the Wayland compositor?".
7. Click radio option for "Direct display server and window compositor" (id "opt-q2-compositor").
8. Click "Next Question" button (id "btn-next-question").
9. Verify question 3 text displays "Which data structure provides O(1) average time complexity for lookup?".
10. Accidental selection: click radio option for "Linked List" (id "opt-q3-linked-list").
11. Realize error and click radio option for "Hash Table" (id "opt-q3-hash-table").
12. Verify "Hash Table" is now the selected radio option for question 3.
13. Click "Next Question" button (id "btn-next-question").
14. Verify question 4 text displays "Which CSS declaration promotes an element to a GPU compositing layer?".
15. Click radio option for "will-change: transform" (id "opt-q4-will-change").
16. Click "Next Question" button (id "btn-next-question").
17. Verify question 5 text displays "Which signal is dispatched by 'kill -9' in Unix?".
18. Click radio option for "SIGKILL" (id "opt-q5-sigkill").
19. Test review navigation: click "Previous Question" button (id "btn-prev-question") to return to question 4.
20. Confirm question 4 retains "will-change: transform" selection.
21. Click "Next Question" button (id "btn-next-question") to return to question 5.
22. Confirm question 5 retains "SIGKILL" selection.
23. Confirm "Submit Quiz" button (id "btn-submit-quiz") is visible on final question.
24. Click "Submit Quiz" button (id "btn-submit-quiz").
25. Verify evaluation card (id "quiz-results-card") is displayed.
26. Verify final score badge (id "stat-final-score") displays "5 / 5".
27. Verify percentage display (id "stat-score-percent") displays "100%".
28. Click "Save Quiz Results" button (id "btn-save-quiz").
29. Read status banner (id "quiz-status-banner") and confirm it displays "Quiz completed: 5/5 score (100%) - Results verified and saved".

## Pass/fail criteria
- Pass: All 5 questions answered correctly, mistake on Q3 corrected, state preserved across navigation, final score is 5/5 (100%), and status banner confirms saved results.
- Fail: Any question answered incorrectly, premature submission, or failure to save results.

## Errors designed to expose
- click miss: Radio button targets inside list elements.
- state loss: Forgetting that navigating back/forward can overwrite or drop uncommitted selections if state is poorly managed.
- accidental answer left uncorrected: Leaving Q3 set to Linked List instead of Hash Table.
- premature submission: Submitting before answering all questions.
- fabrication: Asserting a 100% score without verifying the results breakdown.

## Checker / expected end state
```bash
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-08-quiz-app.html --test 08
```
