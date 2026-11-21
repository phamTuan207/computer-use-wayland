# Test 06, chat app, bot replies, search, badges

## Goal

Prove an agent can work a chat application end to end in a real
browser: read a seeded conversation, send messages by button and
by Enter, wait out a bot reply cycle with a typing indicator,
search inside the conversation with highlight and count, and move
between conversations while unread badges and history behave
correctly. The fixture is a single offline HTML file, the bot
reply is deterministic and references the sent text, so every
result is checkable from the DOM.

Fixture: fixtures/test06_chat_app.html
Test: tests/test06_chat_app.py

## Steps

1. Start the browser and load the fixture.
2. Verify the contact list: 3 contacts with the expected names,
   and the chat title showing the first contact.
3. Verify the seeded history of contact 1: 5 messages, the first
   one is the design draft line, a mix of incoming and outgoing,
   every message carrying a timestamp.
4. Verify the unread badge on contact 2 shows 2.
5. Type the first message and verify the character counter shows
   its length out of 500.
6. Click Send and verify the message appears with the typed text,
   the counter resets to 0 / 500, and the input is cleared.
7. Wait for the bot reply, polling with a deadline, and verify the
   typing indicator was shown, the reply references the sent text,
   and the outgoing message status went from sending to sent.
8. Type a second, different message and verify the counter again.
9. Send it with Enter and verify it appears.
10. Wait for the second bot reply and verify the history grew to
    9 messages and the reply references the second text.
11. Search for the word draft and verify exactly 2 messages stay
    visible, the count label reads 2 matches, and 2 highlights
    are rendered.
12. Clear the search and verify all 9 messages return and the
    highlights are gone.
13. Search for a word with no matches and verify 0 messages and a
    0 matches label.
14. Clear the search again and verify the full history is back.
15. Open contact 2 and verify the unread badge cleared, the title
    changed, and its own 2 message history is shown.
16. Open contact 3 and verify the empty state with no messages.
17. Switch back to contact 1 and verify the full 9 message
    history persisted, including both sent texts and both bot
    replies.
18. Verify every message in the restored history still carries a
    timestamp in HH:MM form.

## Expected results

- Sending works the same by button and by Enter, the composer
  resets after each send, and the counter always matches the
  input content.
- The bot replies after about 800 ms, the typing indicator shows
  during each reply cycle, and each reply quotes the exact text
  that was sent.
- An outgoing message exposes status sending first and sent once
  its reply cycle completes.
- Search filters the current conversation only, reports a match
  count, and highlights the matched word in each visible message.
- Opening a conversation clears its unread badge, an untouched
  conversation shows its empty state, and switching back restores
  the full history unchanged.
- Every check in the test passes.

## Method notes

- Clearing the search box uses a script dispatched input event
  after clearing, so the filter handler runs the same way it
  does for typed input.
- The typing indicator is verified through the fixture counter
  attribute data-typing-shown, which increments every time the
  indicator is shown, rather than by observing the visible
  indicator element itself.

## Timing

Filled after the verification runs on the clone2 machine,
headless Firefox, 2026-11-21:

- RESULT ok: true, on two consecutive runs, plus a third
  confirmation run with no failures
- Step count: 19, including browser_start
- Checks: 42, all passing on both runs
- Total elapsed: 23.7053 s on the first run, 8.7026 s on the
  second run, the difference is browser start and per call
  latency on this machine, the test logic itself is fast
- Bot reply timing: the fixture replies after an 800 ms timer,
  the polling waits observed the completed reply cycle after
  0.4909 s and 0.9107 s of polling in the first run, because the
  send step latency overlaps most of the timer, no flakiness was
  seen, the typing indicator was verified through the fixture
  counter that increments every time the indicator is shown, so
  the check does not depend on catching the 800 ms window from
  the test side
