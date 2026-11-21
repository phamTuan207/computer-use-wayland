# t04-email-client: email client workflow

## Context

A demo mail client with Inbox, Starred, Sent, and Trash folders.
The inbox starts with 3 messages, 2 unread. The user can search,
open messages (which marks them read), star, compose and send,
delete to trash, and mark all read.

## Goal

Work through a realistic mail session: find a message by search,
read it, star another, send a new message, delete one to trash,
clear the unread count, and check the Starred folder.

## Steps

1. Open the fixture page, check Inbox has 3 messages and 2 unread.
2. Search `invoice`, check 1 message shows with the right subject.
3. Clear the search, check 3 messages show again.
4. Open the first message, check the subject and body in the reader.
5. Check the unread count drops to 1.
6. Go back to the list, star the second message.
7. Check the Starred count is 1.
8. Compose a message to team@example.org with subject `Demo report`.
9. Send it, check the toast reads `Message sent.` and Sent is 1.
10. Open the Sent folder, check the message is listed.
11. Open the Inbox, open the third message (System maintenance).
12. Delete it from the reader.
13. Check Inbox is 2 and Trash is 1.
14. Open Trash, check the deleted message is there.
15. Open the Inbox, click Mark all read, check unread is 0.
16. Search `nomatch`, check 0 messages and the empty state shows.
17. Clear the search, open Starred, check 1 message is listed.
18. Unstar it from the list, check the Starred count is 0.
19. Open the Inbox, check the folder title is `Inbox`.

## Pass conditions

- Every count, toast, subject, and body above matches.
- Search filters the list and the empty state appears for no match.
- Sent and Trash folders hold exactly the messages the flow produced.

## Fail conditions

- Any count or message text differs from the expected value.
- A sent or deleted message is missing from its folder.
- Opening a message does not mark it read.

## Notes

All addresses use the reserved example.org domain and are demo
values, not real accounts. No mail is sent and no data leaves the
machine. The browser run is Playwright Chromium; the same flow on
Firefox or Zen is UNVERIFIED.
