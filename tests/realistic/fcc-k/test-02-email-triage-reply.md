# test-02-email-triage-reply.md

## Test ID
test-02-email-triage-reply

## Topic
Email triage + reply drafting.

## Context
Pham Tuan opens a local offline email client fixture and finds an inbox of
mixed messages: a vendor quote, a customer complaint, an internal meeting
request, and two newsletters. The agent must triage by marking read/unread,
archiving newsletters, flagging the complaint, then draft a reply to the vendor
quote with corrected pricing, attach nothing, and send. The task forces reading
of message bodies, multi-message state changes, and composing a new message with
multiple fields filled in.

## Goal
Triage 6 messages (mark read, archive 2 newsletters, flag complaint, star
vendor quote), then compose and send a reply to the vendor quote with a price
correction, and confirm the reply appears in Sent.

## Exact steps
1. Open the email fixture `fixtures/test-02-email.html` in the local browser
   (offline, file:// URL).
2. Verify the inbox list shows exactly 6 messages with subjects and senders.
3. Click message 1 (vendor quote) to open it; read the quoted price.
4. Mark message 1 as read (click the read toggle).
5. Click message 2 (customer complaint); read the complaint body.
6. Flag message 2 as important (click the flag star).
7. Click message 3 (internal meeting request); read date and time.
8. Mark message 3 as read.
9. Click message 4 (newsletter); read subject only.
10. Archive message 4 (click archive button).
11. Click message 5 (newsletter); read subject only.
12. Archive message 5.
13. Click message 6 (vendor quote follow-up); mark as read and star it.
14. Click Compose / New message button.
15. In the reply draft, set To to the vendor address from message 1.
16. Set Subject to `Re: vendor quote - price correction`.
17. Click the body field and type the correction paragraph (at least 3 sentences
    quoting the original price 45000 and the corrected price 42000).
18. Click Send.
19. Open the Sent folder (click Sent in the sidebar).
20. Verify the new reply is the top message in Sent with the corrected subject.
21. Return to Inbox and confirm message 4 and message 5 are no longer listed.
22. Confirm message 2 still shows the flag star and message 1 shows as read.

## Pass/fail criteria
- Pass: 6 messages triaged, 2 archived (absent from inbox), complaint flagged,
  vendor starred, reply sent and present in Sent with corrected subject and
  body mentioning both prices.
- Fail: a message clicked but not opened, archive clicked but message still
  present, reply missing from Sent, wrong To address, body missing prices.

## What to time
- Per-step wall time for each click/type/read (22 steps, ~30 field actions).
- Total wall time from step 1 to step 22.
- Time from opening message 1 to sending the reply (reply latency).
- Time spent re-reading the inbox after archive (stale observation check).

## Errors designed to expose
- click miss: clicking the wrong message row or the wrong sidebar folder.
- slow think: long pause between reading a price and typing the correction.
- stale observation: trusting an old inbox screenshot after archiving, so the
  agent thinks message 4 is gone when it is still there.
- wrong diagnosis: concluding send failed because the reply is not visible in
  Inbox (it is in Sent).
- fabrication: claiming a message was archived or flagged without reading the
  UI state.

## Checker / expected end state
Checker script: `tests/realistic/fcc-k/check.mjs --fixture
fixtures/test-02-email.html --test 02`.
Expected end state: inbox contains messages 1,2,3,6 only (4 and 5 archived);
message 2 flagged, message 1 read, message 6 read+starred; Sent contains one
reply with subject `Re: vendor quote - price correction` to the vendor address
whose body includes both the original and corrected price.