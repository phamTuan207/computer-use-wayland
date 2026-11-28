# Worker Y2b log: agy generates 10 new hard realistic tests (agy-y2b)

- Worker: Y2b (Muse, driving agy via agy-hypr)
- Started: 2026-11-21 ~18:09 +07
- Driver: agy via ~/.local/bin/agy-hypr (keyring only reachable inside graphical logind session). Each invocation max 10 min, continuation prompts for longer work.
- Target: tests/realistic/agy-y2b/ on branch todolist-push, 10 tests, 15-40 steps each.
- Reason: Worker Z1 (opencode) BLOCKED, 0 tests: nvidia deepseek-v4.1-flash EOL 2026-11-16, opencode free tier "Free usage limit reached". Z1 topics reassigned here. See improvements/worker-z1-opencode-log.md (commit 26aac48).
- Sequencing: do NOT start agy until Worker Y2 finishes its own agy batch (tests/realistic/agy-y2/). Two agy runs fight over the same graphical session. Poll repo for Y2 completion (10 tests in tests/realistic/agy-y2/ or final report in improvements/worker-y2-agy-log.md).
- Hard rule (from Y2, supersedes the agy-q2 hook pattern): NO self-simulating __verify() hooks in fixtures. check.mjs verifies by reading raw DOM directly, expected values hard-coded in the checker, never in the fixture. simulate.mjs executes the spec steps via puppeteer to prove fixtures pass.
- Suite layout (copy agy-q2): README.md, check.mjs, simulate.mjs, check-dashes.py, test-XX-<slug>.md specs, fixtures/test-XX-<slug>.html.
- No em/en dashes anywhere. No personal info in any commit. agy generates only; independent runner verifies later.

## Y2 status polling
- 18:09: Y2 NOT done. tests/realistic/agy-y2/ does not exist yet; Y2 log shows Batch 1 (tests 01-05) still pending. Doing non-agy prep (this draft) while waiting.

## Drafted specs (ready to paste into agy prompts)

### test-01-git-workflow (terminal git UI)
Goal: branch feature/login, 2 commits, merge with 1 conflict resolved, clean status.
Fixture: terminal-style git UI, repo "computer-use-wayland", branches main + feature/login, files auth.js, README.md, login.html, style.css.
Steps (30): open fixture, verify current branch main and status clean; click New Branch, type feature/login, create; verify branch switched; stage auth.js + login.html; type commit message "Add login form", commit, verify log shows commit c1a2b3c; stage style.css, commit "Style login page" (d2e4f6a); switch to main; stage README.md, commit "Hotfix typo" (e3f5a7b); MISTAKE: click Merge while still on feature/login (button disabled / error "already on feature/login"), recover by switching to main first; click Merge feature/login; conflict on auth.js appears; click Resolve, choose "Keep both" (ours + theirs lines); click Commit Merge; verify log shows 4 commits in order, branch list shows main + feature/login, status clean, conflict banner gone.
Expected end state: log length 4, last commit "Merge branch feature/login", status "working tree clean", no conflict markers in auth.js content (contains both "validate()" and "sanitize()").
Timing: 180s expected, 300s max.

### test-02-music-player (playlist)
Goal: playlist "Focus Mix 2026", 5 tracks in, reorder, favorite 2, remove 1, save with 4 tracks.
Fixture: player UI, library of 8 tracks with durations, queue panel, volume slider, shuffle/repeat toggles.
Steps (28): open fixture, verify queue empty and total 0:00; type playlist name "Focus Mix 2026"; add tracks in order: "Rain Code" 3:12, "Night Compile" 4:05, "LoFi Kernel" 2:48, "Deep Focus" 5:21, "Morning Build" 3:16; verify queue count 5 and total 18:42; click track 3 to play, verify now-playing "LoFi Kernel" and progress starts; click Next, verify "Deep Focus"; click Previous, verify "LoFi Kernel"; MISTAKE: click Remove on "Night Compile" by accident, then click Undo, verify count back to 5; click Move Down on "Rain Code", verify it is now position 2; favorite "Deep Focus" and "Morning Build" (star toggles); set volume slider to 70; toggle Shuffle ON then OFF; remove "Morning Build" deliberately, verify count 4 and total 15:26; click Save Playlist; verify banner "Playlist 'Focus Mix 2026' saved with 4 tracks".
Expected end state: queue ["Night Compile", "Rain Code", "LoFi Kernel", "Deep Focus"], favorites 1 ("Deep Focus"), volume 70, shuffle off, banner text exact.
Timing: 180s expected, 300s max.

### test-03-password-manager (vault)
Goal: unlock vault, add github entry with generated 16-char password, edit, search, lock, unlock, delete 1, end with 5 entries.
Fixture: vault UI locked by default, 4 entries (gmail, facebook, netflix, bank), master password field, generator panel, search box.
Steps (30): open fixture, verify vault locked and entry list hidden; type wrong master password "wrongpass", click Unlock, verify error "Incorrect master password"; MISTAKE: type correct password but click outside (nothing happens), recover by clicking Unlock; type "correct-horse-2026", click Unlock, verify 4 entries shown; click Add Entry; type site "github.com", username "phamtuan207"; click Generate Password, verify generated password length 16 and strength "Strong"; click Copy Password, verify toast "Password copied"; click Save Entry, verify count 5; click entry "bank", click Edit, change username to "phamtuan-bank", Save; type "bank" in search, verify 1 result; clear search, verify 5 entries; click Lock Vault, verify list hidden; unlock again with correct password, verify 5 entries; click entry "netflix", click Delete, confirm dialog Yes, verify count 4 and banner "Entry deleted".
Expected end state: 4 entries (gmail, facebook, bank with new username, github.com), vault unlocked, no error banner.
Timing: 180s expected, 300s max.

### test-04-maps-directions (route)
Goal: route [address redacted] to NEU, driving 8.4 km / 22 min, add stop, swap, save.
Fixture: maps UI, origin/destination inputs, mode buttons (driving/walking/transit), route options list, avoid-tolls toggle, stops panel.
Steps (26): open fixture, verify map empty and no route; type origin "[address redacted]"; type destination "NEU, Tran Dai Nghia"; click Driving; verify 3 route options listed, fastest 8.4 km / 22 min; click fastest route, verify summary "8.4 km, 22 min via Giai Phong"; click Add Stop, type "Hoan Kiem Lake", verify route updates to 9.1 km / 27 min; MISTAKE: click Avoid Tolls twice (on then off), verify toggle ends OFF and distance back to 9.1 km; switch mode to Walking, verify "7.9 km, 1h 38m"; switch back to Driving, verify 9.1 km / 27 min; click Swap, verify origin "NEU, Tran Dai Nghia" and destination "[address redacted]", distance still 9.1 km; click Save Route, type name "Home to NEU", Save; verify saved routes count 1 and banner "Route saved".
Expected end state: origin NEU, destination [address redacted], driving, 9.1 km / 27 min, 1 stop, 1 saved route, avoid-tolls off.
Timing: 150s expected, 300s max.

### test-05-calendar-recurring (weekly meeting)
Goal: weekly NCKH meeting Fridays 09:00-11:00, move one occurrence, retime series, delete one, end with 6 at 09:30 and 1 moved.
Fixture: calendar week view, 8 Friday occurrences (Nov 21, 28, Dec 5, 12, 19, 26, Jan 2, 9), event editor with This event / This and following / Entire series options.
Steps (29): open fixture, verify 8 occurrences of "NCKH meeting" Fridays 09:00-11:00; click Nov 28 occurrence, click Edit, choose "Only this event", change time to 10:00-12:00, Save, verify Nov 28 shows 10:00 and others still 09:00; click Dec 5 occurrence, click Edit, choose "Entire series", change start to 09:30, Save, verify Dec 5 onward show 09:30-11:30 and Nov 21 + Nov 28 unchanged; MISTAKE: click Delete on Dec 12 and choose "Entire series" in the confirm dialog, then Cancel at the last step, verify series still intact; click Delete on Dec 12, choose "Only this event", Confirm, verify Dec 12 gone and count 7; click Jan 2 occurrence, add note "Bring slides", Save; verify occurrence count 7, moved 1 (Nov 28 10:00), series time 09:30 for 6 occurrences.
Expected end state: 7 occurrences, Nov 21 09:00, Nov 28 10:00, Dec 5/19/26/Jan 2/Jan 9 09:30, Dec 12 absent, Jan 2 note "Bring slides".
Timing: 180s expected, 300s max.

### test-06-video-editor (timeline)
Goal: 3 clips, trim clip 2 to 8s, split clip 1 at 5s, fade transition, text overlay, audio -6dB, export 1080p, total 42s.
Fixture: editor UI, timeline with clip1 15s, clip2 12s, clip3 20s (total 47s), trim handles, split button, transitions panel, text overlay panel, audio slider, export dialog.
Steps (31): open fixture, verify 3 clips and total 47s; click clip2, set trim end to 8s, verify clip2 8s and total 43s; click clip1, click Split at 5s, verify 4 clips (clip1a 5s, clip1b 10s); MISTAKE: click Delete on clip3, then click Undo, verify 4 clips back and total 43s; select clip1b, click Add Transition, choose Fade, verify transition badge on clip1b; click Text Overlay, type "Intro", set position top-left, verify overlay listed; select clip2, set audio to -6 dB; click clip1a, set speed 1.0 (no change, verify duration still 5s); verify total 43s; click Export, choose 1080p, click Export, verify status "Exporting..." then "Export complete: 42s video" (1s fade overlap reduces total by 1s); verify export list count 1.
Expected end state: 4 clips (5s, 10s, 8s, 20s), 1 fade transition, 1 text overlay "Intro", audio -6dB on clip2, export complete 42s, 1 export in list.
Timing: 200s expected, 300s max.

### test-07-chat-search (messages)
Goal: search "deadline" 4 messages in 2 threads, filter sender Thinh, reply, pin, empty search "budget" 0 results.
Fixture: chat app, 3 threads (Hihihahahehe, AC 1 cau, NCKH team), 24 messages total, search box, sender filter, pin/reply buttons.
Steps (27): open fixture, verify 3 threads and 24 messages; click search, type "deadline", verify 4 results in 2 threads; click sender filter, choose "Thinh", verify 2 results; click first result, verify thread opens scrolled to message "deadline is Friday 17:00"; click Reply, type "Got it, will submit by 16:00", Send, verify message count 25 and reply shown; click Pin on the deadline message, verify pinned count 1; clear sender filter, verify 4 results again; type "budget" in search, verify 0 results and empty state "No messages found"; MISTAKE: click Delete on the pinned message, then Cancel the confirm dialog, verify message still there; clear search, verify 25 messages; click Pinned tab, verify 1 pinned message.
Expected end state: 25 messages, 1 pinned, search cleared, reply "Got it, will submit by 16:00" present in Hihihahahehe thread.
Timing: 150s expected, 300s max.

### test-08-pivot-table (sales)
Goal: pivot Region x Quarter, Sum(Revenue), verify cells and grand total 58,300, switch to Count, filter North.
Fixture: spreadsheet UI, 12 sales rows (Region North/South/East/West x Q1/Q2/Q3, Revenue values), pivot builder panel, result grid.
Steps (29): open fixture, verify 12 data rows; click Pivot Table; set Rows = Region, Columns = Quarter, Values = Sum(Revenue); click Build, verify grid shows 4 regions x 3 quarters; verify North Q1 = 12,400; verify South Q2 = 9,800; verify East Q3 = 6,100; verify Grand Total = 58,300; MISTAKE: set Values to Average by accident, verify Grand Total changes to 4,858, then set back to Sum, verify 58,300 again; change Values to Count, verify Grand Total = 12 and North Q1 = 2; change back to Sum; click Filter Region = North only, verify total 21,700 and only North row shown; clear filter, verify 58,300; click Export, verify toast "Pivot exported (flag only)".
Expected end state: pivot Sum(Revenue), all regions, grand total 58,300, North total 21,700, West Q2 = 7,300.
Timing: 180s expected, 300s max.

### test-09-file-manager-search-tag (files)
Goal: search *.pdf 5 files, tag 3 "thesis", filter tag 3, rename 1, move 2 to Archive, undo wrong move.
Fixture: file manager, 14 files (5 pdf, 4 docx, 3 png, 2 zip) across folders Home and Archive (Archive starts with 1 file), search box, tag panel, rename/move dialogs.
Steps (30): open fixture, verify 14 files in Home and 1 in Archive; type "*.pdf" in search, verify 5 results; select 3 pdfs (thesis-draft.pdf, thesis-final.pdf, thesis-notes.pdf), click Add Tag, type "thesis", Apply, verify tag badge on 3 files; click tag filter "thesis", verify 3 files shown; clear filter, verify 14 files; click thesis-draft.pdf, Rename to "thesis-v2.pdf", verify new name in list; select thesis-final.pdf and thesis-notes.pdf, click Move, choose Archive, verify Home count 12 and Archive count 3; MISTAKE: select report.docx and click Move to Archive, then click Undo, verify Home count back to 12 and Archive 3; type "thesis" in search, verify 3 results (2 in Archive, 1 in Home); click tag filter "thesis", verify 3 files.
Expected end state: Home 12 files, Archive 3 files, tag "thesis" on 3 files, thesis-v2.pdf exists, report.docx in Home.
Timing: 180s expected, 300s max.

### test-10-extension-settings (tab organizer)
Goal: enable extension, auto-group on, group by domain, exclude mail.google.com, shortcut Ctrl+Shift+G, dark mode, persist, reset one setting.
Fixture: browser extension settings page, extension "Tab Organizer" v2.4.1, toggles, dropdowns, shortcut input, exclude list, theme selector, reset buttons, save banner.
Steps (28): open fixture, verify extension status Disabled; click Enable, verify status Enabled; toggle Auto-Group ON, verify toggle on; set Group By dropdown to "Domain", verify selection; click Add Exclude, type "mail.google.com", Add, verify exclude list count 1; click shortcut input, type "Ctrl+Shift+G", verify field shows "Ctrl+Shift+G"; select Theme Dark, verify preview dark; MISTAKE: click Reset All, then Cancel the confirm dialog, verify all settings intact; click Save Settings, verify banner "Settings saved"; reload the page (fixture reload button), verify settings persisted (Enabled, Auto-Group on, Domain, 1 exclude, shortcut, Dark); click Reset next to Theme only, verify theme back to Light and other settings unchanged; click Save, verify banner again.
Expected end state: Enabled, Auto-Group on, Group By Domain, exclude list ["mail.google.com"], shortcut Ctrl+Shift+G, theme Light (after reset), save banner shown.
Timing: 150s expected, 300s max.

## agy prompt template (use after Y2 finishes)
Each batch prompt is a full instruction file written to /tmp/prompt-y2b-N.txt on the laptop, then run via agy-hypr. Prompt contents:
- Repo path on laptop: ~/workspace/computer-use-wayland, branch todolist-push.
- Build tests/realistic/agy-y2b/ with the layout of tests/realistic/agy-q2/ (README.md, check.mjs, simulate.mjs, check-dashes.py, test-XX-<slug>.md, fixtures/test-XX-<slug>.html) BUT with Y2's hard rule: check.mjs reads raw DOM directly with expected values hard-coded in the checker, NO __verify() hook in any fixture.
- Paste the drafted spec for each test in the batch verbatim (goal, steps with exact element IDs, expected end state, mistake + recovery, timing).
- Each fixture: standalone offline HTML, pure JS + CSS, no network, no CDN. All interactive elements need stable ids. Deterministic values only (no random, no Date.now in expected values).
- simulate.mjs must execute every spec step via puppeteer and end by calling the raw-DOM checker logic; `node simulate.mjs --all` must pass 10/10 before the batch is called done.
- check-dashes.py must pass (no em/en dashes anywhere in the suite).
- Commit in small commits on todolist-push, push as you go.
- Batch 1: tests 01-05. Batch 2: tests 06-10. If a batch does not finish in 10 min, continue with a continuation prompt naming exactly which files remain.

## Runs
### Batch 1 (tests 01-05), prompt /tmp/prompt-y2b-1.txt
- Launched: NEVER. Parent redirect 18:14: agy hit quota exhaustion (429 RESOURCE_EXHAUSTED at 18:10:55, resets ~28/11, 165h37m). Y2's batch is stuck on the same quota. Do NOT wait for Y2, do NOT invoke agy.
- Evidence seen by Y2b: /tmp/out-y2-1.log = "error: interrupted / AGY_HYPR_EXIT:124" (17:59); /tmp/out-y2-2.log = quota error 429 (18:10). No agy process running on the laptop at 18:14.
- New task instead: independently verify Y2's 10 tests (tests/realistic/agy-y2/) WITHOUT agy, static review + live headless execution. Full report: improvements/worker-y2b-verification.md.
- VERDICT: 8/10 PASS (01-06, 08, 10), 1 FAIL (07: toast "Root: 5 files" vs checker "Root: 3 files", spec miscounted, fixture is right), 1 CRASH (09: dead id #note-item-archived-draft, destroyed by renderList() at load; also a vacuous checker assertion). No __verify hooks anywhere; dashes PASSED; VM copies == laptop copies (md5, 22 files).
- My 10 generation topics move to Codex (per parent). Drafted specs stay in this log, ready to hand over.
### Batch 2 (tests 06-10), prompt /tmp/prompt-y2b-2.txt
- Launched: NEVER (same quota death).
