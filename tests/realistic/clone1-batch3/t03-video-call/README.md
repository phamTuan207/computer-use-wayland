# t03-video-call: video call UI

## Context

A demo video call with a lobby and a call view. The call has three
participant tiles, mute and camera controls, hand raise, chat, screen
share, invite and remove, and leave and rejoin. No real camera or
microphone is used; tiles and states are simulated in the page.

## Goal

Join the call, exercise every control, and confirm the visible state
matches after each action.

## Steps

1. Open the fixture page, check the status is `Not in a call.`
2. Check the lobby is visible and the call view is hidden.
3. Click Join call, check the status is `In call: Weekly sync`.
4. Check the call view is visible with 3 participants.
5. Click Mute, check the mic state is `Muted` and the button reads `Unmute`.
6. Click Unmute, check the mic state is `Live` again.
7. Click Turn camera off, check the camera state and the tile style.
8. Click Turn camera on, check the camera state is back.
9. Click Raise hand, check the hand count is 1.
10. Click Lower hand, check the hand count is 0.
11. Send the chat message `Hello team`, check it appears in the log.
12. Send a second chat message, check both are in the log.
13. Click Share screen, check the share state and the screen tile.
14. Click Stop sharing, check the share state and the tile is gone.
15. Click Invite Cara, check the participant count is 4.
16. Click Remove on Cara's tile, check the count is back to 3.
17. Click Leave, check the status is `Left the call.` and the lobby returns.
18. Click Rejoin call, check the call is live again with 3 participants.
19. Click Leave again, check the status is `Left the call.`

## Pass conditions

- Every control above changes the visible state as described.
- Chat messages appear in order in the log.
- Participant counts track tiles added and removed.

## Fail conditions

- Any state, label, count, or tile does not match after an action.
- The call view is visible before joining or after leaving.

## Notes

No media devices are used. All state lives in the page. The browser
run is Playwright Chromium; the same flow on Firefox or Zen is
UNVERIFIED.
