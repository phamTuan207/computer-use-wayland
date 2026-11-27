# PWA CDP full checklist: drive the Muse / mimeo PWA without mouse or vision

Date: 2026-11-24, ~20:27-20:40 Asia/Ho_Chi_Minh. Owner: the owner.
Scope: Muse PWA (clone1, Brave, CDP 9224) and mimeo PWA (clone2, Chromium, CDP 9223),
on the Omarchy laptop, reached over SSH. CDP only, no computer-use, no ydotool,
no mouse, no vision for any step below.

## Verdict

CDP drives the PWA for almost everything an agent needs. 11 of 15 checklist
features work live. 2 fail (reply, react) because the message "More options"
menu never opens under CDP synthetic events; those need a real mouse click.
1 is partial (stop: presence detection works, the click itself is untested by
design, it would kill the agent's current generation). 1 (endcall) was not
tested separately because the call action's end step uses the same click.

## Tools

- Driver: `~/workspace/pwa-driver.js` (Node, no dependencies, global WebSocket).
  Runs on the laptop via SSH. Usage: `node pwa-driver.js <port> <title-substring>
  <action> [args...]`. Resolves the target by URL/title via /json/list, never
  hardcodes target IDs. Actions: send, read, status, list, search, attach,
  unattach, newchat, back, call, endcall, reply, react, stop, panel, raw.
- Wrapper: `~/workspace/pwa-send.py` (reusable, on the VM). Usage:
  `pwa-send.py clone1 "message"` to send, or `pwa-send.py clone1 --action
  <action> [args...]` for any driver action. It ships the driver to the laptop
  over SSH (stdin pipe, sha256-verified) and runs it with Node. Exit 0 on ok.

## Live evidence: send

- clone1, ~20:27 (previous worker 07e29904): sent "CDP send test, no mouse
  used. No action needed, keep working on your current task." Verified by CDP
  read: owner bubble with the exact text (mid e6897363-e0ff-4ab9-90a6-).
  clone1 replied: "Noted, no action on the test. Diff work is running again
  via the GitHub API route instead of the flagged clone: 22 commits, 169
  files, +10,937/-1,174 lines, not truncated."
- clone2, ~20:39 (this session): sent "CDP send test, no mouse used. No
  action needed, ignore this test message." Driver returned ok=true,
  sent=true, textareaCleared=true. Verified by CDP read: owner bubble with
  the exact text (mid ce24e232-cdab-4e56-9618-). clone2 is locked (usage limit,
  resets 02:38 Wed 25/11), so it cannot reply; the send path itself is proven.
- clone2, ~20:40 (wrapper test): sent "Wrapper test, no mouse used. No
  action needed, ignore this test message." via `pwa-send.py clone2 "..."`.
  Driver returned ok=true, sent=true, textareaCleared=true. Verified by CDP
  read via the wrapper: owner bubble with the exact text (mid
  268bd99f-76fc-439a-9d9c-). This proves the wrapper's message quoting works.

## Feature checklist (all run live on clone1 unless noted)

| Feature | CDP? | CDP command | Live evidence |
|---|---|---|---|
| send | YES | Runtime.evaluate to focus textarea, Input.insertText, Input.dispatchKeyEvent Enter | clone1 + clone2, exact text in transcript, textarea cleared |
| read messages | YES | Runtime.evaluate on [data-message-id], sender from id prefix | clone1 last 6, clone2 last 4, sender + text correct |
| read status | YES | Runtime.evaluate on the header box | clone1 "Completing red-team review", clone2 "Out of usage" |
| list chats | YES (after fix) | Runtime.evaluate on nav[aria-label="Side chats"] innerText | clone1: Main chat + 1 side chat "Run frontend agent kit tasks". clone2: none, empty state text |
| search | YES | click Search button, Input.insertText, read [role=dialog], Escape | clone1 query "Zen": returned the Zen 1.24.3b R3-L3 Report Space + main chat excerpt |
| attach file | YES | DOM.enable, DOM.getDocument, DOM.querySelector input[type=file], DOM.setFileInputFiles | clone1: /tmp/pwa-attach-test.txt shown in composer as "pwa-attach-test \| .txt" |
| unattach | YES | Runtime.evaluate click remove-attachment button | clone1: composer back to "Message" |
| new side chat | YES | click hamburger, click nav button[2] | clone1: header "New side chat \| Call \| clone1 \| Connected" |
| back to main chat | YES | click "Back to main chat" button | clone1: hasMainChat=true |
| call | YES | click Call button, read controls, click End call | clone1: controls [Mute call audio, Cancel call, End call], ended=true, no End call button after |
| end call | SAME PATH | click "End call" button | Not tested separately; the call action's end step uses the same click and returned ended=true |
| reply to a message | NO | n/a | More options menu never opens under CDP synthetic events (see below) |
| react to a message | NO | n/a | Same root cause as reply (see below) |
| stop generation | PARTIAL | Runtime.evaluate detects the Stop button | Correctly reports "no Stop button (agent idle)" when clone1 is idle. The click itself is untested by design: it would kill the agent's current generation. Use --force only when that is intended. |
| switch panel | YES (after fix) | click button by aria-label OR text content | "Chats" clicked, viewChanged=true |

## What CDP cannot do (with fallback)

- reply / react: the message "More options" button accepts a synthetic
  MouseEvent click (the driver reports CLICKED), but no menu ever appears.
  Probed 4 ways in a single CDP session (immediate read, 1s wait, hover +
  click, full button list after click): zero menu items (Reply, React, Copy,
  Delete, Edit, Forward) appear in the DOM. The menu most likely needs a
  trusted user gesture or a hover state that synthetic events do not provide.
  Fallback: a real mouse click via computer-use (act-now) to open the menu,
  then CDP can click the menu item. That is the only feature pair that still
  needs the mouse.
- stop click: untested by design, not by failure. The detection works. Only
  use --force when killing the agent's current generation is intended.

## Driver fixes made during this session

1. `panel`: now matches a button by aria-label OR by text content. Before,
   "Chats" failed (NO BTN) because the Chats nav button has no aria-label,
   only the text "ChatsOpen chat and side chats".
2. `list`: now opens the side-chats nav (hamburger) and reads
   nav[aria-label="Side chats"]. Before, it ran a timestamp regex over all
   buttons in the document and returned approval-history items instead of
   chats. Note: the nav is a toggle, so `list` expects it closed on entry;
   if a previous probe left it open, close it with Escape first.

## State changes left behind (for the owner)

- clone1 PWA: one empty side chat "New side chat" created by the newchat
  test. It is empty and harmless; delete it from the Chats panel if unwanted.
- clone1 transcript: one test message from the previous worker ("CDP send
  test, no mouse used..."), clone1 already replied "Noted".
- clone2 transcript: two test messages ("CDP send test..." and "Wrapper
  test..."), both marked "no action needed, ignore". clone2 is locked and
  cannot reply until 02:38 Wed 25/11.
- Laptop /tmp: /tmp/pwa-attach-test.txt (one-line harmless text) and
  /tmp/pwa-driver.js (the shipped driver). Both in /tmp, safe to delete.
- No tabs or windows were closed, navigated, or reloaded. No browser was
  restarted. No mouse or vision was used for any CDP step.

## How to use from now on

- Send a message: `python3 ~/workspace/pwa-send.py clone1 "text"` or
  `python3 ~/workspace/pwa-send.py clone2 "text"`.
- Any other action: `python3 ~/workspace/pwa-send.py clone1 --action
  <action> [args...]`. See the wrapper docstring for the full list.
- The wrapper re-ships the driver on every run, so edits to
  ~/workspace/pwa-driver.js take effect immediately.
