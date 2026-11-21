# test-06-video-call.md

## Test ID
test-06-video-call

## Topic
Video call web application: join meeting, audio/video toggle controls, screen sharing, hand raise, chat messaging, leave and rejoin, participant and state verification.

## Context
A remote engineer needs to participate in a team sync call using a web-based video conferencing client (fixtures/test-06-video-call.html).
The user must enter the meeting room "Sprint Planning", mute and unmute the microphone, turn off and turn back on the camera,
initiate screen sharing then stop sharing, raise hand, send a message in the meeting chat sidebar, leave the call, rejoin the call,
and verify that participant counts and device status indicators in the DOM accurately reflect the final meeting state.

## Timing
- Baseline start time: 2026-11-21 17:00:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Join meeting "Sprint Planning", toggle mute/unmute mic, toggle camera off/on, share and unshare screen, raise hand, send chat message, leave and rejoin meeting, and verify DOM participant count and audio/video badges.

## Exact steps
1. Open fixture tests/realistic/agy-y2/fixtures/test-06-video-call.html in the browser.
2. Verify element #call-status-badge text is "Lobby" and #participant-count text is "0".
3. Click input #input-meeting-id and type "Sprint Planning".
4. Click input #input-display-name and type "James".
5. Click button #btn-join-meeting to enter the video conference.
6. Verify element #call-status-badge text is "Connected" and #participant-count text is "4".
7. Verify element #room-name-display text is "Sprint Planning".
8. Click button #btn-toggle-mic to mute the microphone.
9. Verify element #mic-status-indicator text is "Muted" and #mic-status-indicator has class "muted".
10. Click button #btn-toggle-mic to unmute the microphone.
11. Verify element #mic-status-indicator text is "Unmuted" and #mic-status-indicator has class "active".
12. Click button #btn-toggle-cam to turn off the camera.
13. Verify element #cam-status-indicator text is "Camera Off" and #cam-status-indicator has class "off".
14. Click button #btn-toggle-cam to turn the camera back on.
15. Verify element #cam-status-indicator text is "Camera On" and #cam-status-indicator has class "active".
16. Click button #btn-share-screen to initiate screen sharing.
17. Verify element #screenshare-modal has class "active".
18. Click option #screen-option-desktop to select full desktop sharing.
19. Click button #btn-confirm-screenshare to start sharing.
20. Verify element #screen-share-banner text contains "Screen sharing active" and element #screen-share-banner is visible.
21. Click button #btn-stop-screenshare to terminate screen sharing.
22. Verify element #screen-share-banner has class "hidden".
23. Click button #btn-raise-hand to signal hand raise.
24. Verify element #hand-raise-indicator has class "raised" and #hand-raise-indicator text is "Hand Raised".
25. Click button #btn-open-chat to open the side chat drawer.
26. Verify element #chat-sidebar has class "open".
27. Click input #input-chat-message and type "Ready for updates".
28. Click button #btn-send-chat to dispatch the chat message.
29. Verify element #chat-message-list text contains "Ready for updates".
30. Click button #btn-leave-meeting to disconnect from the call.
31. Verify element #call-status-badge text is "Disconnected" and #rejoin-prompt-panel is visible.
32. Click button #btn-rejoin-meeting to reconnect to the meeting.
33. Verify element #call-status-badge text is "Connected" and #participant-count text is "4".
34. Click button #btn-save-call-summary to generate final call status log.
35. Verify element #call-summary-toast text contains "Meeting Sprint Planning: 4 participants, audio active, video active".

## Pass/fail criteria
- Pass: Successfully joined meeting "Sprint Planning", toggled mic and camera states, shared and stopped screen share, raised hand, posted chat message, cleanly left and rejoined call, participant count is 4, and summary toast confirms connected status.
- Fail: Cannot join room, mic or camera toggles do not persist state, chat message not recorded in DOM, participant count wrong after rejoin, or call summary toast not activated.

## Errors designed to expose
- click miss: Small toolbar icon buttons for mic, cam, screen share, and hand raise.
- slow think: Delays during reconnect and modal dismiss interactions.
- stale observation: Reading participant count before reconnect handshake completes.
- wrong diagnosis: Mistaking temporary leave state for complete app failure instead of clicking rejoin.
- fabrication: Asserting chat was sent without inspecting chat-message-list DOM entries.

## Checker / expected end state
```bash
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-06-video-call.html --test 06
```
