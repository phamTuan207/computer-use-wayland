# test-07-chat-search.md

## Test ID
test-07-chat-search

## Topic
Chat message search with sender and date filters, jumping to a result, starring, and forwarding.

## Context
A moderator needs to find the exact release checklist message in Team Chat Search, narrow it by sender and day, open the result, star it, and forward it to Release Room. The sender filters include a deliberate wrong choice that returns a different message before recovery. The fixture is tests/realistic/codex-y5/fixtures/test-07-chat-search.html.

## Timing
- Baseline start time: 2026-11-21 18:21:00 Asia/Ho_Chi_Minh
- Expected duration: 240 seconds elapsed
- Maximum allowable latency: 360 seconds elapsed

## Goal
Open the Build Bot message "Release checklist is ready for review." from 2026-10-12, star it, and forward it to Release Room.

## Exact steps
1. Open tests/realistic/codex-y5/fixtures/test-07-chat-search.html in the browser.
2. Verify #search-result-count text is "0", #active-message-text text is "No message selected", and #active-room text is "None".
3. Type "Release checklist" into #search-query-input; its value must be "Release checklist".
4. Click button #btn-search-messages; #search-result-count must become "3".
5. Verify #filter-summary text is "3 matching messages", #btn-open-result-m1 text is "Jump to result", and #btn-open-result-m2 text is "Jump to result".
6. Mistake: select value "Design Bot" in #sender-filter; the selected value must be "Design Bot".
7. Click button #btn-apply-filters; #search-result-count must become "1".
8. Verify #filter-summary text is "1 matching message" and #btn-open-result-m3 text is "Jump to result".
9. Recovery: select value "Build Bot" in #sender-filter; the selected value must be "Build Bot".
10. Click button #btn-apply-filters; #search-result-count must become "2".
11. Verify #filter-summary text is "2 matching messages" and #btn-open-result-m1 text is "Jump to result".
12. Type "2026-10-12" into #from-date-input; its value must be "2026-10-12".
13. Type "2026-10-12" into #to-date-input; its value must be "2026-10-12".
14. Click button #btn-apply-filters; #search-result-count must become "1".
15. Verify #filter-summary text is "1 matching message" and #btn-open-result-m1 text is "Jump to result".
16. Click button #btn-open-result-m1; #active-message-text must become "Release checklist is ready for review.".
17. Verify #active-message-sender text is "Build Bot", #active-message-date text is "2026-10-12", and #active-room text is "Build Room".
18. Click button #btn-star-message; #star-status must become "Starred".
19. Verify #star-status text is "Starred".
20. Click button #btn-forward-message; #forward-modal must become visible with heading text "Forward message".
21. Type "Release Room" into #forward-room-input; its value must be "Release Room".
22. Click button #btn-confirm-forward; #forward-status must become "Forwarded to Release Room".
23. Verify #search-result-count text is "1", #active-message-text text is "Release checklist is ready for review.", #star-status text is "Starred", #forward-status text is "Forwarded to Release Room", #forwarded-count text is "1", and #active-room text is "Release Room".

## Pass/fail criteria
- Pass: The matching Build Bot message from October 12 is active, starred, and forwarded once to Release Room.
- Fail: The wrong sender result is forwarded, the message date differs, the message is not starred, or the forward count is not one.

## Errors designed to expose
- click miss: Search, filter, star, and forward controls occupy separate compact panels.
- slow think: Search results change after sender and date filters are applied.
- stale observation: The first sender filter leaves a single result that must not be mistaken for the target.
- wrong diagnosis: The wrong sender choice returns a valid but incorrect result and must be corrected.
- fabrication: Sender, date, message text, destination room, and forward count have exact DOM checks.

## Checker / expected end state
```bash
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-07-chat-search.html --test 07
```
