# t06-chat-app: chat across two contacts

## Context

A team chat app with two contacts, Alice and Bob. Messages send, a
simulated reply arrives after a short delay with a typing indicator,
emoji insert into the composer, file attach adds a message, search
filters the thread, own messages can be edited and deleted, and unread
badges count replies that arrive while another thread is open.

## Goal

Chat with Alice, use emoji and attach, search, edit, delete, then chat
with Bob and prove the unread badge works.

## Steps (40)

1. Open the fixture.
2. Check Alice starts with 2 messages.
3. Type a message to Alice.
4. Send it.
5. Check the own message appears.
6. Check the own message text.
7. Check the typing indicator shows.
8. Wait for the Alice reply.
9. Check the reply arrived.
10. Check the typing indicator cleared.
11. Pick an emoji from the picker.
12. Check the emoji is in the input.
13. Type a message with the emoji.
14. Send it with Enter.
15. Check the emoji message was sent.
16. Wait for the reply to the emoji message.
17. Check 6 messages are shown after the second reply.
18. Attach a file.
19. Check the attachment message.
20. Search for shipping.
21. Check the search leaves 1 visible message.
22. Clear the search.
23. Check all 7 messages show again.
24. Open edit on the first own message.
25. Edit the message text.
26. Save the edit.
27. Check the edited text is saved.
28. Delete the first own message.
29. Check the count dropped by 1.
30. Switch to Bob.
31. Check Bob's thread has 1 message.
32. Check the title says Bob.
33. Type a message to Bob.
34. Send it to Bob.
35. Switch back to Alice before the reply.
36. Wait for the Bob unread badge.
37. Check the Bob badge is 1.
38. Switch to Bob again.
39. Check the badge cleared after opening and Bob's reply is visible.
40. Check every message shows a time.

## Pass

All 40 steps run, replies arrive with the typing indicator first,
emoji and attach work, search filters and restores, edit and delete
change the thread, and the unread badge counts and clears correctly.

## Fail

Any step above fails, a reply never arrives, the badge is wrong, or a
message is lost.
