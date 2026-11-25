# pwa-send.py URL resolution fix (2026-11-25)

## The bug
Both pages on each CDP port are now titled "Muse", so title-substring matching
could not tell the PWA apart from the regular chat tab on the same port.
`pwa-send.py clone1` failed with "NO PAGE for title clone1", and the same for
clone2. Found by the internal-watchdogs worker, 25/11 ~10:39.

Live state at fix time (from /json/list):
- Brave 9224: page "Muse" at https://muse.ai/ (mei) and page "Muse" at
  https://muse.ai/?__pwa=1 (clone1)
- Chromium 9223: page "Muse" at https://muse.ai/ (mochi) and page "Muse" at
  https://muse.ai/?__pwa=1 (clone2)

## The fix
Target resolution is now by URL only, never by title:
- PWA (clone1, clone2): URL contains muse.ai and "__pwa=1"
- Chat tab (mei, mochi): URL contains muse.ai and NOT "__pwa=1"
- The driver takes a match spec "pwa:<name>" or "chat:<name>" instead of a
  title substring. <name> is only the agent display name for the status action.
- pwa-send.py now has 4 recipients: clone1 (pwa:clone1), clone2 (pwa:clone2),
  mei (chat:mei), mochi (chat:mochi). Mei and mochi are normally messaged
  through the daemon (send.py); they are recipients here only so read/status
  resolution works for the shared agents watch. Mei's tab is never confused
  with clone1's PWA tab, and mochi's tab is never confused with clone2's PWA
  tab. Never use clone1's tab as a mei target.
- Targets are still resolved dynamically via /json/list at call time. No
  target ID is hardcoded. The CLI interface is unchanged:
  `pwa-send.py <agent> "message"` and `pwa-send.py <agent> --action <action>`.

## Live verification (25/11, after the fix)
- Status checks, all ok=true with the correct target URL:
  - clone1: https://muse.ai/?__pwa=1, status "clone1 | Updating watchdog"
  - clone2: https://muse.ai/?__pwa=1, status "clone2 | is warming up"
  - mei: https://muse.ai/, status "mei | Updating todo list"
  - mochi: https://muse.ai/, status "mochi | Checking branch"
- Test send to clone1: ok=true, sent=true, textareaCleared=true, confirmed
  delivered by re-read (message in clone1's transcript).
- Test send to clone2: ok=true, sent=true, textareaCleared=true, confirmed
  delivered by re-read (message in clone2's transcript).
- No test messages were sent to mei or mochi (read-only status checks only).

## Files
- improvements/pwa-driver.js (fixed)
- improvements/pwa-send.py (fixed)
- The live copies are ~/workspace/pwa-driver.js and ~/workspace/pwa-send.py.
