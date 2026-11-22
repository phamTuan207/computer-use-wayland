# Worker C4-P3-PROBE log: P3 Brave relaunch controlled experiment

Owner: Pham Tuan. Coordinator: COORD-CLICK-4. Branch: todolist-push.
Probe target: FINAL direction (worker-click3-final-direction-log.md) section 1.2
P3 row, section 3 step 2 (P3 paragraph), section 6 worker 5, section 7 (P3
re-run owner). Prior probe PROBE-P3 (7b1006a) was NOT-RUN: clone1 batch 9 open.
This run re-attempts it in the first real quiet window.

Result: PASS. Brave accepts --remote-debugging-port on its existing profile,
session restores, clone1 tab and login intact, CDP observe plus harvest plus
fill plus assert all pass against the relaunched Brave, composer is NOT in
shadow DOM. One operational caveat, not a failure: port 9223 IPv4 was already
held by the pre-existing agent-managed Chromium, so Brave listened on
[::1]:9223 only (section 2.5). No rollback was needed for the experiment
itself; the planned revert to no-flag was still executed at the end (section
2.8) to close the CDP exposure.

## Standing rules recorded

- No em dash (U+2014) or en dash (U+2013) anywhere in this file.
- No personal info (no real name, email, address, schedule, photo, account,
  password, token) in this file or any commit.
- Never ydotool. Full access. Never click blindly; if a step fails, log the
  failure and stop that step, do not push through.
- No-self-healing rule (05:56, 22/11): on a Muse failure an INDEPENDENT worker
  investigates; this log records evidence only.
- Safety rule for this probe: NEVER touch Brave mid-batch. Run ONLY in a quiet
  window (clone1 between batches, no new batch assigned, Brave confirmed idle).
- Scratch input only. Never type into clone1's or clone2's real chat threads.
  No chat content is quoted in this log; only structural counts and element
  roles are recorded.

## Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from probe start)

- 08:52 +07, t+0s: probe start. Repo ~/workspace/computer-use-wayland,
  branch todolist-push.
- 08:48-08:52, t-4m to t+0s: preconditions verified (section 0). Log file
  skeleton plus rollback plan written BEFORE any Brave state change.
- 08:50:08-08:50:16, t-2m: SIGTERM to Brave main PID 7356, exit confirmed.
- 08:50:27: Brave relaunched with --remote-debugging-port=9223, new main PID
  935106.
- 08:50:44-08:54:49: first CDP round, later determined to be against the
  pre-existing Chromium on 127.0.0.1:9223, not Brave (section 2.5). Includes
  the stale laptop cdp.mjs finding and the scp of the current copy.
- 08:55:43-08:55:52: port discovery (ss) and Brave list on [::1]:9223.
- 08:56:07-08:56:30: full CDP round against the relaunched Brave
  ([::1]:9223): observe, harvest, fill plus assert, independent read-back.
- 08:56:43-08:57:22: scratch tabs closed, stray blank tab closed, Brave tab
  set confirmed back to the single Muse tab.
- 08:57:39-08:57:54: Brave reverted (relaunch WITHOUT the flag, PID 940441),
  CDP exposure closed, Chromium untouched.
- 08:58:07-08:58:39: two failed attempts to move the Brave window back to
  workspace 2 (hl.dsp has no movetoworkspace); step stopped, deviation
  recorded (section 2.9).
- 08:59 +07, t+7m: probe end, log written.

## 0. Preconditions (verified BEFORE touching anything)

### 0.1 Clone1 has no open batch

- git fetch origin, 08:52 +07. origin/main HEAD 495cfc6 "coord: batch 11 to
  clone2, 3 tasks (RT2 defective repair, readiness gaps, discover + Y1b
  check), 08:50 22/11".
- Clone1 batch 9 was MOVED to clone2 at 07:03 +07, commit e32f8f2 "coord:
  move batch 9 from clone1 (stall 61 min, nudge unanswered) to clone2".
  Acknowledged cc94dc0 07:09. DOT 9 moved to clone2, commit 05d0ab1 07:09.
- Clone1 STALL 158 min at the 08:38 watchdog log (02dad13). Clone1 silent
  since about 06:00:50 +07 (out of tokens, per the brief).
- No new clone1 batch assigned since 07:03: the only batch assignment
  commits since then are clone2 batch 10 (done 07:49, fae9b9c) and clone2
  batch 11 (08:50, 495cfc6). git log origin/main --grep=clone1 shows only
  watchdog stall notes, no assignment.
- VERDICT: precondition MET. Clone1 has no open batch; its batch 9 work now
  lives with clone2, whose chat is Chrome, not Brave.

### 0.2 Brave idle on the laptop (workspace 2)

- Read-only SSH check 08:48:52 +07 via ~/workspace/ssh-laptop.sh.
- Brave main process PID 7356, /opt/brave-origin-bin/brave, started Nov 21,
  profile-directory=Default, --app-id=hichoggbhebpgpgcbcgfpkjmohpcflhh,
  wrapper PID 7347 (/opt/brave-origin-bin/brave-origin).
- Two "Muse" windows on workspace 2, both titled "Muse" (CORRECTED from the
  skeleton, which called both Brave; the ps evidence below shows one is
  Chromium):
  - Window 5570538ed160, class chrome-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default,
    pid 8059, at 3448,914, size 901,1176, visible, mapped. This is the
    Chromium window (see section 2.5), not Brave.
  - Window 55705383d420, class brave-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default,
    pid 7356. This is the Brave window, the P3 target.
- Active workspace is 1 (Zen Browser, "Welcome! - Zen Browser"), not 2.
  No typing or active use in progress on workspace 2. Machine handed over
  (owner asleep, not at home), verified anyway as briefed.
- Session files exist and are recent: ~/.config/BraveSoftware/Brave-Origin/
  Default/Sessions/ holds Session_13439771128214984 and
  Tabs_13439722769041035, updated Nov 22 04:45. Session Storage updated
  Nov 21 15:19.
- VERDICT: precondition MET. Brave idle, workspace 2 quiet.

### 0.3 Tooling on the laptop

- Node v26.13.1 on the laptop (checked 08:49:42 +07).
- scripts/cdp.mjs exists on the laptop at ~/computer-use-wayland/scripts/
  cdp.mjs, 25177 bytes, dated Nov 19 06:01. Laptop tree HEAD 56f5af4 (behind
  the VM). This copy turned out to be STALE (no harvest operation, section
  2.3). The probe used the current VM copy scp'd to /tmp/p3-cdp.mjs
  (39620 bytes); the installed laptop tree was NOT modified.
- Agent-managed Chromium profiles exist on the laptop:
  ~/.config/chromium and ~/.config/google-chrome (for the step 5
  login-persistence note only; no browser was launched by this probe).

## 1. ROLLBACK PLAN (stated BEFORE the window, before any Brave state change)

If any step below fails, or the tab/login is not intact after relaunch, roll
back immediately and report FAIL with evidence. Do not proceed past a failed
verification step.

1. Kill the debug-port Brave instance: SIGTERM to the Brave main PID (the
   relaunched PID, recorded in the time log), wait up to 10 s for exit,
   verify with ps that no brave main process remains. SIGTERM is graceful
   so session files flush; do NOT use SIGKILL unless SIGTERM fails to exit
   in 10 s.
2. Relaunch Brave EXACTLY as found, without the flag, detached:
   /opt/brave-origin-bin/brave-origin with the original flags from the
   pre-relaunch ps line: --ozone-platform=wayland
   --ozone-platform-hint=wayland --password-store=gnome-libsecret
   --enable-features=TouchpadOverscrollHistoryNavigation,
   AcceleratedVideoDecodeLinuxGL,VaapiIgnoreDriverChecks,OverlayScrollbar
   --load-extension=/usr/share/omarchy/default/chromium/extensions/copy-url,
   /usr/share/omarchy/default/chromium/extensions/yt-dlp,
   /usr/share/omarchy/default/chromium/extensions/whatsapp-slim
   --use-gl=angle --use-angle=gl --ignore-gpu-blocklist
   --no-default-browser-check --profile-directory=Default
   --app-id=hichoggbhebpgpgcbcgfpkjmohpcflhh
   Command: setsid nohup <above> > /tmp/p3-brave-rollback.log 2>&1 < /dev/null &
   disown. Then verify via hyprctl clients that the "Muse" window returns
   on workspace 2.
3. Session restore: Brave restores the app window and tabs from the
   Sessions dir (Session_ files current as of Nov 22 04:45, section 0.2).
   If Brave shows a restore prompt, the window still restores from the
   same session files; record what appears and do NOT clear profile data.
4. Re-login cost if the session is lost: the Messenger login for the
   clone1 account would need re-authentication. I hold no credentials for
   that account and will NOT attempt a login myself. Re-login is a manual
   step for the owner (or the coordinator with the saved login). A lost
   session is a FAIL outcome with evidence, not something to work around
   silently.
5. If Brave will not start at all after rollback: leave it closed, do NOT
   delete or modify any profile file, record the exact error from the log,
   and report FAIL. Profile files under
   ~/.config/BraveSoftware/Brave-Origin/ are never deleted by this probe.
6. End state: after the probe measurements, relaunch Brave WITHOUT the
   flag (same rollback command) to return the machine exactly to its
   as-found state and CLOSE the CDP exposure. Reason: CDP on port 9223
   exposes the logged-in browser to any local process (security
   consideration, section 5). The flag can be re-enabled by one relaunch
   whenever the step 11 live run needs it; the re-enable cost is one
   relaunch, already proven by this probe.

## 2. Experiment steps

### 2.1 Relaunch Brave with --remote-debugging-port=9223

- 08:50:08 +07: `kill -TERM 7356` via ssh-laptop.sh. 08:50:16: `ps -p 7356`
  empty, no brave main process remains. Graceful exit in under 8 s.
- 08:50:27: relaunched detached (setsid nohup, same flags as found plus
  --remote-debugging-port=9223, log /tmp/p3-brave-debug.log). New main PID
  935106, command line confirmed to carry --remote-debugging-port=9223.
- 08:50:44: hyprctl clients shows the Brave "Muse" window back (pid
  935106, class brave-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default), now on
  workspace 1 (it opened on the active workspace, not ws2; see section
  2.9). The Chromium "Muse" window (pid 8059) is untouched on ws2.

### 2.2 First /json/list and first CDP round (MISATTRIBUTED, corrected below)

- 08:50:44: `curl http://127.0.0.1:9223/json/list` answered. /json/version:
  Browser Chrome/157.0.8103.38, Protocol-Version 1.3.
- 08:50:58: one page tab: id D1374C7C994D3DA72678E20C7FD099A0, title
  "(3) Chat - clone2", URL https://muse.ai/?__pwa=1. Login intact (the
  authenticated chat page loaded, not a login redirect).
- 08:51:37-08:51:51: created a scratch tab via PUT /json/new (id
  36FE9E563FFBB8B64EF04363657A500C). Note: /json/new IGNORED the url
  parameter (both data:text/html and file:///tmp/p3-scratch.html came back
  as about:blank). Scratch content was seeded instead with a small node
  script over the tab WebSocket (Runtime.evaluate document.write of a form
  with #scratch input, #scratch2 textarea, #sendbtn button). Seed confirmed
  08:52:19 (document.title "P3-SCRATCH").
- 08:52:30: cdp.mjs observe (laptop copy) on the scratch tab: exit 0,
  snapshot fa1d9a88-13b, title P3-SCRATCH, 3 elements (input, textarea,
  button), truncated false, iframes 0.
- 08:52:42: cdp.mjs harvest on the scratch tab FAILED: exit 1,
  {"ok":false,"completed":0,"error":"unknown operation"}.
- 08:53:39: cdp.mjs act (fill #scratch with "P3-SCRATCH-OK" plus assert
  value) on the scratch tab: exit 0, {"ok":true,"completed":2,
  "execution_ms":15,"after_skipped":true}. Independent read-back 08:53:51
  via Runtime.evaluate: document.getElementById("scratch").value is
  "P3-SCRATCH-OK".
- 08:54:03: observe on the real tab: exit 0, 67 ms, 77 elements, truncated
  false, iframes 2, composer present as a textarea named "Message".
- 08:54:20: harvest on the real tab (still the stale laptop copy? No, see
  section 2.3: the harvest at 08:54:20 ran AFTER the scp at 08:53:15, so
  it used the current copy): exit 0, 122 ms, ok true. textarea composer
  rect equals box_model exactly, matches true. AX tree 76 nodes.
- These results are all VALID measurements, but they are measurements of
  the Chromium process on 127.0.0.1:9223, not of Brave. See section 2.5
  for the discovery and the correction.

### 2.3 Stale laptop cdp.mjs (CB-9 drift, confirmed live)

- Laptop copy: 25177 bytes, operations list at line 118 is only
  ['tabs','observe','act'], no 'harvest'. Laptop tree HEAD 56f5af4.
- VM repo copy: 39620 bytes, operations ['tabs','observe','act',
  'harvest'], 5 harvest mentions.
- Fix used by this probe: scp of the VM copy to /tmp/p3-cdp.mjs on the
  laptop (SCP-OK, 08:53:15, 39620 bytes, 5 harvest mentions). All harvest
  and act runs after 08:53:15 used /tmp/p3-cdp.mjs. The installed laptop
  tree (~/computer-use-wayland) was NOT modified; syncing it is the step 8
  worker's job, not this probe's.
- Consequence recorded: the harvest at 08:53:28 on the scratch tab (exit 0,
  75 ms, ok true, all three selectors with box_model matching the JS rect)
  used the current copy. The earlier observe and act runs used the stale
  laptop copy but those operations exist in both copies and behaved
  identically.

### 2.4 Shadow-DOM check on the real composer (Chromium round)

- Page shadow-root count via Runtime.evaluate, 08:54:37: exactly 1 shadow
  root on the page, host NEXT-ROUTE-ANNOUNCER (a framework internal
  element), 1 textarea on the page. The composer is NOT inside it.
- Harvest result (section 2.2): composer textarea rect {x 451.5, y 1091,
  width 622, height 24} equals box_model exactly, matches true; the 1x1
  input likewise has a real box_model; no contenteditable element exists.
- Conclusion for the Chromium round: no shadow-DOM gap for the composer.
  The PARTIAL outcome defined in the direction does NOT trigger here.

### 2.5 Port discovery: 127.0.0.1:9223 was Chromium all along (CORRECTION)

- 08:54:49: `ps aux | grep chrome` showed PID 8059 is
  /usr/lib/chromium/chromium with --remote-debugging-port=9223 on its
  command line, started Nov 21, profile ~/.config/chromium/Default,
  --app-id=hichoggbhebpgpgcbcgfpkjmohpcflhh. It is the agent-managed
  Chromium, already CDP-enabled since Nov 21, and it hosts the clone2
  chat tab.
- 08:55:43: `ss -ltnp` settles it:
  - 127.0.0.1:9223 LISTEN, users (("chromium", pid=8059, fd=91)).
  - [::1]:9223 LISTEN, users (("brave", pid=935106, fd=102)).
- /tmp/p3-brave-debug.log: "bind() failed: Address already in use (98)"
  for the IPv4 socket, then "DevTools listening on
  ws://[::1]:9223/devtools/browser/c448236d-ec51-4ccb-8bf1-d86aefbb182f".
  Brave accepted the flag and listened, but only on IPv6 loopback because
  IPv4 9223 was taken.
- /json/version on 127.0.0.1:9223 said Chrome/157.0.8103.38 (Chromium);
  on [::1]:9223 it says Chrome/157.0.8103.79 (Brave's build). The two
  version strings prove the two listeners are different browsers.
- CORRECTION: every result in section 2.2 was measured against the
  Chromium process, not Brave. The section 2.2 results stand as evidence
  for the agent-managed Chromium path (which is itself a live P3-relevant
  configuration), but they are NOT Brave evidence. The Brave evidence is
  section 2.6, re-run in full after this discovery.

### 2.6 Full CDP round against the relaunched Brave ([::1]:9223)

- 08:55:52: `curl "http://[::1]:9223/json/list"`: one page tab, id
  1563355BC86478EBAF3D0BDA179767FD, title "(2) Chat - clone1", URL
  https://muse.ai/?__pwa=1. The relaunched Brave restored its tab: the
  clone1 chat, logged in (authenticated page, not a login redirect).
  Session restore PROVEN. No rollback needed.
- 08:56:07: observe on the Brave tab (current /tmp/p3-cdp.mjs): exit 0,
  73 ms, title "(2) Chat - clone1", snapshot d23240ba-0cc, 51 elements,
  truncated false, iframes 0, composer present as e26 textarea named
  "Message".
- 08:56:07: harvest on the Brave tab: exit 0, 108 ms, ok true. textarea
  composer rect {x 141, y 496, width 314, height 24} equals box_model
  exactly, matches true. input (1x1) likewise has a real box_model.
  No contenteditable element. AX tree 50 nodes.
- 08:56:18: scratch tab created in Brave via PUT /json/new (id
  B9F8732C71B4BC830BEA6ED590A3931F, about:blank again, same /json/new
  url-parameter behavior). Seeded with the IPv6 variant of the seed script
  (title "P3-SCRATCH" confirmed).
- 08:56:30: observe on the Brave scratch tab: exit 0, 70 ms, 3 elements,
  snapshot a8c9fea2-19b. Harvest: exit 0, 77 ms, ok true, all three
  selectors with box_model present. Act (fill #scratch with
  "P3-SCRATCH-OK" plus assert value): exit 0, 81 ms, {"ok":true,
  "completed":2,"execution_ms":12,"after_skipped":true}. Independent
  read-back: "P3-SCRATCH-OK".
- No typing ever touched a real chat thread. All fills went to scratch
  tabs that were closed afterwards.

### 2.7 Shadow-DOM check on the Brave composer (decisive)

- The Brave/clone1 composer is a plain TEXTAREA in the light DOM
  (document.querySelector("textarea") finds it; harvest box_model is real
  and equals the JS rect). The page's single shadow root belongs to a
  framework announcer element, not to any interactive element.
- The direction's PARTIAL definition ("Messenger composer sits in shadow
  DOM and CDP returns null box_model") does NOT trigger. Note on wording:
  the Brave tab is muse.ai (the Muse web app), not messenger.com, so the
  literally-named "Messenger composer" is not present in this Brave
  instance; the check was run on the composer actually in use by the clone
  chats, which is the muse.ai textarea composer, and it is NOT shadow-DOM
  hosted. A messenger.com shadow-DOM check would need a Messenger tab,
  which does not exist in this Brave profile.
- Conclusion: CDP works for the composer, no shadow-DOM fallback needed
  for this task class.

### 2.8 Cleanup and revert (rollback plan end state)

- 08:56:43: closed both scratch tabs (Chromium 36FE9E56..., Brave
  B9F8732C...; both "Target is closing"). Chromium tab list after close:
  only "(3) Chat - clone2". Brave list showed the Muse tab plus a stray
  about:blank tab (id 475E977121DC9AD9F32C474E1DAF9BF6, NOT my scratch tab
  id; it appeared during the probe, origin unknown, possibly opened by the
  app window when the scratch tab was created). Closed it too.
- 08:57:22: Brave tab list confirmed back to exactly one page tab:
  id 1563355BC86478EBAF3D0BDA179767FD, title "Muse",
  URL https://muse.ai/?__pwa=1. Title changed from "(2) Chat - clone1"
  to "Muse" during the probe (same tab id, same URL; most likely the
  unread-count prefix clearing when the tab lost focus to the scratch tab).
  Login intact, no action needed.
- 08:57:39: Brave reverted per the rollback plan: SIGTERM to 935106 (exit
  confirmed), relaunched WITHOUT --remote-debugging-port, new main PID
  940441, command line confirmed flag-free.
- 08:57:54: final verification: Brave no longer listens on [::1]:9223
  (curl fails, expected); Chromium 8059 still listens on 127.0.0.1:9223
  and still serves "(3) Chat - clone2"; hyprctl clients shows both Muse
  windows back (Chromium pid 8059 on ws2, Brave pid 940441).
- /tmp files left on the laptop (scratch only, no profile changes):
  /tmp/p3-scratch.html, /tmp/p3-cdp.mjs, /tmp/p3-seed.mjs,
  /tmp/p3-seed6.mjs, /tmp/p3-read.mjs, /tmp/p3-read6.mjs,
  /tmp/p3-observe.json, /tmp/p3-harvest.json, /tmp/p3-brave-debug.log,
  /tmp/p3-brave-rollback.log. No profile file was created, modified, or
  deleted by this probe except through the browsers' own normal session
  writes.

### 2.9 Known deviation: Brave window on workspace 1, not 2

- The relaunched Brave window opened on the active workspace (1) instead
  of its as-found workspace (2). Two attempts to move it back failed:
  - 08:58:07: `hyprctl dispatch movetoworkspace 2,address:0x55705383d420`
    failed, Lua parse error (string dispatchers are broken on Hyprland
    0.57.2, per the standing lesson).
  - 08:58:25: `hl.dsp.window.movetoworkspace({ workspace = 2, address =
    "0x55705383d420" })` failed, "attempt to call a nil value (field
    'movetoworkspace')".
  - 08:58:39: `hl.dsp.movetoworkspace({ workspace = 2, address =
    "0x55705383d420" })` failed, same nil-value error.
- Per the standing rule the step was stopped, not pushed through. The
  Brave window is intact on workspace 1 (same tab, same login, only the
  workspace differs). Moving it back is a one-click job for the owner or
  a later worker that knows the right hl.dsp call. Recorded here so the
  coordinator is not surprised.

## 3. Chromium fallback login-persistence check (migration note only)

Not executed as a migration; the evidence below is read-only (cookie
counts from a COPY of the Cookies file; no cookie values were read).

- The agent-managed Chromium (PID 8059, /usr/lib/chromium/chromium,
  --remote-debugging-port=9223, started Nov 21, profile
  ~/.config/chromium/Default) is ALREADY logged in and serving the clone2
  chat on 127.0.0.1:9223. It has been live since Nov 21. There is no
  migration to perform and no re-login needed for the Chromium path:
  re-login cost is ZERO, already paid.
- Cookie counts in ~/.config/chromium/Default/Cookies (393216 bytes,
  live, mtime Nov 22 08:54): .muse.ai 12 rows, muse.ai 2 rows,
  platform.muse.ai 3 rows, .facebook.com 5 rows, messenger.com 0 rows.
  (First query 08:54:49 also showed .google.com 18, .youtube.com 29, and
  other hosts; only the relevant hosts are listed here.)
- ~/.config/google-chrome has NO Default profile (only a
  NativeMessagingHosts dir); it is unused. The live Chromium profile is
  ~/.config/chromium.
- Consequence for the program: the CDP path to a logged-in clone chat
  ALREADY EXISTS today on 127.0.0.1:9223 (Chromium, clone2 thread). What
  P3 newly proves is the Brave side: Brave also accepts the flag and
  restores the clone1 thread, on [::1]:9223 while 9223/IPv4 is taken, or
  on a free port such as 9224. For the step 11 live run the endpoint must
  be named per browser: 127.0.0.1:9223 is Chromium/clone2,
  [::1]:9223 (or a fresh free port) is Brave/clone1. A run that assumes
  "port 9223 is Brave" will silently drive the wrong browser.

## 4. Security consideration

- CDP on port 9223 exposes the logged-in browser to any local process:
  any process on the laptop can list tabs, read page DOM, and drive input
  as the logged-in user, with no authentication. During this probe Brave
  listened on [::1]:9223 for about 7 minutes (08:50-08:57); that listener
  is now closed (Brave relaunched without the flag).
- STANDING exposure, not created by this probe: the agent-managed Chromium
  has listened on 127.0.0.1:9223 since Nov 21 and still does. Any local
  process can drive the logged-in clone2 chat through it right now. The
  coordinator should record this as a known standing exposure (or close it
  when the live run does not need it). This probe did not open it and did
  not close it; it only used it after discovering it, and it left it
  exactly as found.

## 5. Verdict

PASS. Evidence, one line each:

- Brave relaunch with the flag: Brave relaunched with
  --remote-debugging-port=9223 on its existing Default profile, PID 935106,
  session restored, clone1 tab and login intact.
- /json/list: Brave on [::1]:9223 lists the clone1 tab
  (1563355BC86478EBAF3D0BDA179767FD, muse.ai, logged in).
- Observe: exit 0, 73 ms, 51 elements, composer present.
- Harvest: exit 0, 108 ms, composer box_model equals JS rect.
- Fill plus assert on scratch input in Brave: exit 0, 81 ms,
  execution_ms 12, independent read-back "P3-SCRATCH-OK".
- Shadow-DOM: composer is a light-DOM TEXTAREA with a real box_model;
  the page's only shadow root is a framework announcer. PARTIAL does not
  trigger.
- Chromium fallback: already logged in on 127.0.0.1:9223 since Nov 21;
  re-login cost zero.

Caveats carried forward (not failures):

1. Port 9223 IPv4 belongs to the pre-existing Chromium; Brave fell back
   to [::1]:9223. The step 11 live run must name the endpoint per browser
   or give Brave a free port (for example 9224).
2. The laptop cdp.mjs is stale (no harvest); the current copy was scp'd to
   /tmp and used. The installed laptop tree is still behind the VM tree.
3. /json/new ignores its url parameter; scratch tabs start as about:blank
   and need content seeded via Runtime.evaluate.
4. Brave window ended on workspace 1, not as-found workspace 2 (two
   hl.dsp move forms failed; section 2.9).
5. A stray blank tab appeared in Brave during the probe; closed, tab set
   restored to one tab.
6. The Chromium 127.0.0.1:9223 listener is a standing local exposure
   since Nov 21 (section 4).

What this unblocks: P3 gates ONLY the step 11 live acceptance run
(FINAL direction section 1.2 P3 row). That gate is now met for the
clone-chat class: both clone chats are CDP-reachable (Brave/clone1 via a
relaunch with a free port, Chromium/clone2 already live on 127.0.0.1:9223),
and the composer is DOM-addressable with a real box_model. No re-plan
around Zen Marionette only is needed on P3 grounds.

## 6. Commit

- Log file: improvements/worker-click4-p3-probe-log.md (this file).
- Commit hash: 924ec3fc4a7105128e7c43a1a12195a009a2c023.
- Push verification: git ls-remote origin todolist-push returned
  924ec3fc4a7105128e7c43a1a12195a009a2c023, matching local HEAD.
- Commit-record update: this line added in a follow-up commit (see below).
