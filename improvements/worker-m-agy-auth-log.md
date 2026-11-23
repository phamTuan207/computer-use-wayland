# Worker M: agy authentication investigation - 21/11/2026

## Question

Why does `agy` work when the user types it in his terminal, but fail with
"authentication required" when Muse runs it over SSH, even though he is
already logged in? Find the root cause for both situations and a way to
reproduce his working login via SSH.

## Answer in one paragraph

The OAuth token is alive in gnome-keyring, the keyring is unlocked and
reachable from SSH, but agy only reads the keyring when the process runs
inside the graphical session (audit sessionid 1, logind type wayland).
Processes started over SSH get a fresh logind session (type tty) and agy
never even attempts keyringAuth there: zero keyring mentions in the log.
Exporting DBUS_SESSION_BUS_ADDRESS, WAYLAND_DISPLAY, DISPLAY and every
XDG_SESSION_* variable does not help, because the gate is the real
logind/audit session, not env vars. The fix that works, verified twice:
dispatch the agy run through Hyprland so it becomes a child of the
graphical session. Helper installed at ~/.local/bin/agy-hypr
on the laptop; usage: write the prompt to a file, run
`agy-hypr <prompt-file> [output-log]` over SSH.

## Evidence

### The token is alive and in the keyring

- Keyring item exists: label "Password for 'antigravity' on 'gemini'",
  service gemini, username antigravity. Listed from SSH with
  python3 secretstorage: collection locked False, 11 items.
- 15:16:22 today: keyringAuth loaded the Nov 14 token (expired=true),
  browser.go refreshed it, new expiry 2026-11-21 16:16:21.
- 15:21:50 today (user terminal, PID 13282): keyringAuth loaded token,
  expiry 2026-11-21 16:16:21, expired=false. Then:
  `ChainedAuth: authenticated via keyring (effective: keyring)`.
- gnome-keyring-daemon PID 1150 running, control dir /run/user/1000/keyring.
- Default keyring is Default_Keyring (modified today 15:19 at login).
- ~/.config/antigravity/credential-user-scope is 17 bytes, no @ sign,
  plain alnum/punct, not a token, not an email. It is a scope marker.
- ~/.config/antigravity/plugin-secrets.json does NOT exist. The
  "file-based secret storage" line in the logs is the PLUGIN auth store,
  not the main OAuth token store. The main token lives in the keyring.

### The discriminator is the session, not the mode or the TTY

Keyring mentions per agy log file, 21/11:

| log | context | keyring | ChainedAuth |
|---|---|---|---|
| 151622 15:16:22 | user terminal after reboot, interactive | 2 | 1 |
| 152150 15:21:50 | user terminal, PID 13282, interactive | 2 | 1 |
| 152239 15:22:39 | SSH, DBUS exported, -p | 0 | 0 |
| 152319 15:23:19 | SSH, -p | 0 | 0 |
| 153335 15:33:35 | SSH + PTY (script), -p | 0 | 0 |
| 153557 15:35:57 | SSH + PTY (script), interactive REPL | 0 | 0 |
| 153641 15:36:41 | SSH, full desktop env exported, -p | 0 | 0 |
| 153902 15:39:02 | Hyprland child (fix), -p | 2 | 1 |

- Interactive vs print mode does NOT matter: the SSH interactive REPL
  also says "You are currently not signed in" and offers login methods.
- TTY vs no TTY does NOT matter: with a PTY, -p goes to interactive
  OAuth (prints a Google OAuth URL, waits 60s) instead of failing fast,
  but still never touches the keyring.
- Env vars do NOT matter: exporting DBUS_SESSION_BUS_ADDRESS,
  WAYLAND_DISPLAY, DISPLAY, XDG_SESSION_TYPE=wayland,
  XDG_CURRENT_DESKTOP, DESKTOP_SESSION, XDG_SESSION_DESKTOP,
  XDG_SESSION_CLASS, XDG_SEAT changed nothing (0 keyring mentions).
- Audit sessionid: agy in user terminal = 1, kitty = 1, SSH bash = 157.
  logind: session 2 = Type wayland, Seat seat0, VTNr 1, State active.
  SSH sessions are transient logind sessions of Type tty.
- No gcloud installed, no ~/.config/gcloud/, so AGY_ADC_AUTH is
  unavailable. No GEMINI_API_KEY in shell configs (name search only,
  values never read). Those are alternative auth paths, not the fix used.

### The fix, verified twice

Method: run agy as a child of Hyprland via hyprctl dispatch. Note:
`hyprctl dispatch exec ...` is broken in Hyprland 0.57.2 Lua (the string
form gets wrapped as hl.dispatch(...) and fails to parse, and
hl.dsp.exec does not exist). The working form is a Lua function:
`hyprctl dispatch 'function() os.execute("/path/to/runner.sh") end'`
(verified: this form created the test file, the other three forms did not).

Test 1, 15:39: agy -p "Reply with exactly the word OK" dispatched via
Hyprland. Output: OK. Log cli-20261121_153902.log shows keyringAuth
loaded token expired=false and ChainedAuth authenticated via keyring.

Test 2, 15:40: helper ~/.local/bin/agy-hypr with a real task
(create /tmp/agy-hypr-proof.txt with two exact lines, reply DONE).
Output: DONE, exit 0. Proof file contained exactly the two lines.
So agy via the helper authenticates AND does real tool work over SSH.

### The helper

Installed at ~/.local/bin/agy-hypr (laptop only, not in repo).
A copy of the same script is saved as ~/workspace/agy-hypr-helper.sh
on the VM for reference. Usage from SSH:

```
printf 'your prompt' > /tmp/prompt.txt
~/.local/bin/agy-hypr /tmp/prompt.txt /tmp/out.log
```

It discovers the Hyprland instance signature dynamically
(ls /run/user/1000/hypr/), dispatches a runner script through hyprctl,
waits up to 10 minutes, prints agy's output and returns its exit code.
The prompt goes in a file to avoid quoting hell through the Lua layer.
Run it detached (setsid nohup ... & disown) for long tasks, like fcc.

### Caveats and limits

- The token in the keyring expires 2026-11-21 16:16:21. It was refreshed
  automatically this morning from the expired Nov 14 token, so refresh
  works while the refresh token is alive. If a future run fails with
  "authentication required" again, the refresh token may have died
  (Google test-mode refresh tokens can expire after 7 days) and the user
  must do one fresh interactive OAuth login in his terminal.
- The helper launches agy as a Hyprland child: it is visible in `ps`
  as a child of Hyprland, not of the SSH session. It does not touch the
  user's terminal, tabs, or windows.
- The OAuth URL printed by the PTY test is NOT reproduced here (it
  contains single-use state/code values; the flow was interrupted by
  timeout and no credentials were created).
- No credential value was read, stored, or printed anywhere in this
  investigation. Only labels, attributes, expiry times and pass/fail
  outcomes were recorded.

## Timeline (wall-clock Asia/Ho_Chi_Minh, 21/11/2026)

- 15:31 task received.
- 15:32-15:33 env comparison, keyring listing, log analysis.
- 15:33 PTY test: -p under script prints OAuth URL, waits, times out.
- 15:35 interactive SSH+PTY test: REPL says "not signed in".
- 15:36 full desktop env export test: still 0 keyring mentions.
- 15:38 hyprctl Lua function dispatch verified with a touch test.
- 15:39 Test 1 (OK) via Hyprland dispatch: PASS, keyringAuth runs.
- 15:40 Test 2 (real file task) via agy-hypr helper: PASS, exit 0.
- 15:41 cleanup of test files, report written.
