# test-04-email-compose.md

## Test ID
test-04-email-compose

## Topic
Email compose workflow: recipient addressing, CC toggle, attachment selection, draft persistence, accidental removal recovery, and message dispatch.

## Context
A project coordinator needs to dispatch a quarterly summary report to their team.
The workstation runs a local browser-based webmail client (fixtures/test-04-email-compose.html).
The user must compose a new message addressed to "team@example.com", add CC recipient "audit@example.com",
set subject "Q4 report", attach "report.pdf" via simulated file picker, save the message as a draft,
close and reopen the draft from the drafts folder, accidentally remove the attachment, recover by re-attaching
"report.pdf", send the message, and verify that the Sent folder counter increments from 12 to 13.

## Timing
- Baseline start time: 2026-11-21 17:00:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Compose email to "team@example.com", CC "audit@example.com", subject "Q4 report", attach "report.pdf",
save draft, close composer, reopen from drafts, delete and restore attachment, send email, and verify Sent count 13.

## Exact steps
1. Open fixture tests/realistic/agy-y2/fixtures/test-04-email-compose.html in the browser.
2. Verify element #sent-folder-counter text is "12" and #drafts-folder-counter text is "0".
3. Click button #btn-compose-mail to launch the email composer.
4. Verify element #compose-pane has class "open".
5. Click input #input-recipient-to and type "team@example.com".
6. Click button #btn-add-cc to display the CC input field.
7. Verify element #cc-group is visible.
8. Click input #input-recipient-cc and type "audit@example.com".
9. Click input #input-mail-subject and type "Q4 report".
10. Click textarea #input-mail-body and type "Attached is the Q4 performance overview.".
11. Click button #btn-open-attachment-picker to open the file selection modal.
12. Verify modal #attachment-picker-modal has class "active".
13. Click option #file-option-report-pdf to choose "report.pdf".
14. Click button #btn-confirm-attach-file to attach the selected file.
15. Verify element #attached-files-list contains element #attachment-chip-report.
16. Verify element #attachment-counter text is "1".
17. Click button #btn-save-draft-mail to store the message as a draft.
18. Verify element #drafts-folder-counter text is "1".
19. Click button #btn-close-composer to close composer pane.
20. Verify element #compose-pane has class "hidden".
21. Click folder item #nav-folder-drafts to open drafts folder view.
22. Click row #draft-entry-q4 to reopen the saved draft.
23. Verify element #compose-pane has class "open" and #input-mail-subject value is "Q4 report".
24. Simulate mistake: click button #btn-remove-attachment-report to remove the attachment.
25. Verify element #attachment-counter text is "0" and #attached-files-list is empty.
26. Recovery: click button #btn-open-attachment-picker to restore the document.
27. Click option #file-option-report-pdf to select "report.pdf" again.
28. Click button #btn-confirm-attach-file to reattach.
29. Verify element #attachment-counter text is "1" and #attachment-chip-report is present.
30. Click button #btn-dispatch-send to send the email.
31. Verify element #compose-pane has class "hidden".
32. Verify element #toast-alert text contains "Email sent to team@example.com with attachment report.pdf".
33. Verify element #sent-folder-counter text is "13".

## Pass/fail criteria
- Pass: Email sent to "team@example.com", subject "Q4 report", "report.pdf" attached, Sent folder counter incremented to 13, and confirmation toast displayed.
- Fail: Compose not completed, attachment missing, draft workflow not executed, Sent count not incremented, or confirmation toast missing.

## Errors designed to expose
- click miss: Small attachment delete buttons and sidebar folder items.
- slow think: Delays during draft saving, modal interactions, and reopening.
- stale observation: Reading Sent count before folder counters refresh in the DOM.
- wrong diagnosis: Overlooking the draft reopen step and drafting a new email from scratch.
- fabrication: Asserting email was sent without checking the updated Sent folder badge.

## Checker / expected end state
```bash
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-04-email-compose.html --test 04
```
