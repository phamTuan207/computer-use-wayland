# Worker I log: Super Z and every Zen launch path to AI-optimized Zen

Date: 2026-11-21. Start 15:21:30 +07, done 15:26 +07. Elapsed about 5 min.
Task: user order, Super Z also launches Zen, make EVERY way of launching Zen
on the laptop (except terminal commands) point to the AI-optimized Zen
(--remote-debugging-port=9222 --marionette).

## 15:21:30 +07 (t+0s): laptop state after reboot

- Zen PID 11292 running since 15:19 with flags:
  /opt/zen-browser-bin/zen-bin --remote-debugging-port=9222 --marionette
- BiDi port 9222 responds (httpd.js page). Chromium 9223 responds
  (Chrome/157.0.8103.38).
- So the .desktop edit from 02:55 works for whatever path launched this
  instance. The question was which paths it does NOT cover.

## 15:21-15:23: inventory of launch paths

- Super Z: ~/.config/hypr/bindings.lua:42
  o.bind("SUPER + Z", "Browser", { omarchy = "browser" })
  It does NOT run zen directly. It calls the Omarchy "browser" action,
  which runs /usr/bin/omarchy-launch-browser.
- omarchy-launch-browser (read in full): gets default browser
  (zen.desktop) via omarchy-cmd-default-browser, searches data dirs
  (~/.local/share first, then /usr/local/share, /usr/share) for
  applications/zen.desktop, then extracts ONLY the binary path with
  sed -n 's/^Exec=\([^ ]*\).*/\1/p', DISCARDS all arguments, and launches
  via omarchy-cmd-browser-handoff (Chromium-only, exits 1 for Zen) then
  systemd-run --user uwsm-app -- <binary>.
  THE BYPASS: the .desktop flags never reach Super Z. Super Z launched
  Zen WITHOUT the flags. The running flagged instance (PID 11292) was
  launched by another path (app launcher), not Super Z.
- Omarchy default binds, same bypass: SUPER+SHIFT+RETURN,
  SUPER+SHIFT+B (browser), SUPER+SHIFT+ALT+B (browser --private).
- Default browser: zen.desktop. mimeapps.list maps text/html, http,
  https and others to zen.desktop. xdg-open goes through the .desktop.
- User .desktop ~/.local/share/applications/zen.desktop: 4 main Exec
  lines had flags. Gap: the ProfileManager action had NO flags
  (Exec=/opt/zen-browser-bin/zen-bin --ProfileManager %u).
- System .desktop /usr/share/applications/zen.desktop: NO flags on any
  line. Cannot edit: sudo needs a password, and the user must never be
  asked for one. It is SHADOWED by the user .desktop in every XDG lookup
  (~/.local/share is searched first), so no live path reaches it unless
  the user .desktop is deleted. Recorded as a known limitation, not fixed.
- Autostart ~/.config/hypr/autostart.lua: no zen entries.
- Waybar: no zen or browser references. Dock pins: Nautilus, chromium,
  omawrite, kitty, brave webapp, deepseek webapp, windows-vm, X, YouTube.
  Zen is NOT pinned in the dock, so the dock is not a Zen launch path.
- No walker or rofi configs reference zen; launchers read .desktop files.
- Private flag probe: zen-bin --help | grep -c MOZ_LOG = 3, so
  omarchy-launch-browser maps --private to --private-window for Zen.
  Any fix must preserve this.

## 15:24: the fix, wrapper script

Created ~/.local/bin/zen-ai (561 bytes, chmod +x):

  #!/bin/bash
  # zen-ai: Zen Browser with AI agent control flags (BiDi + Marionette).
  # Every non-terminal launch path resolves here via zen.desktop Exec=.
  if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    exec /opt/zen-browser-bin/zen-bin "$@"
  fi
  exec /opt/zen-browser-bin/zen-bin --remote-debugging-port=9222 --marionette "$@"

Why a wrapper and not a binding change: omarchy-launch-browser strips
Exec arguments, so flags in the .desktop can never reach Super Z. A
wrapper as the Exec binary survives the strip, because the strip keeps
exactly the binary path. One change covers every path that reads the
.desktop: Super Z, the three Omarchy default browser binds, app
launcher, xdg-open, desktop actions. The --help passthrough keeps the
private-window probe output identical to plain zen-bin --help.

Backed up the .desktop to zen.desktop.bak-20261121-superz, then
repointed all 5 Exec lines to the wrapper with sed. Result:
- line 4 (main): Exec=~/.local/bin/zen-ai %u
- line 239 (new-window): Exec=~/.local/bin/zen-ai %u
- line 354 (new-blank-window): Exec=~/.local/bin/zen-ai --blank-window %u
- line 469 (new-private-window): Exec=~/.local/bin/zen-ai --private-window %u
- line 584 (profilemanager): Exec=~/.local/bin/zen-ai --ProfileManager %u
- 0 Exec lines still point at the raw binary.

## 15:24-15:25: verification (all passed)

1. omarchy-launch-browser sed extraction on the new .desktop returns
   ~/.local/bin/zen-ai. Super Z now resolves to the wrapper.
2. omarchy-cmd-default-browser still returns zen.desktop.
3. Wrapper --help probe: zen-ai --help | grep -c MOZ_LOG = 3, identical
   to plain zen-bin --help. Private-window detection preserved.
4. command -v resolves the wrapper path.
5. End-to-end headless test, temp profile, detached:
   zen-ai --profile /tmp/zen-ai-test-prof --headless --screenshot
   /tmp/zen-ai-test.png about:blank
   First attempt failed ("Could not find profile folder") because the
   profile dir did not exist. Retried after mkdir -p. Observed cmdline:
   /opt/zen-browser-bin/zen-bin --remote-debugging-port=9222
   --marionette --profile /tmp/zen-ai-test-prof --headless --screenshot
   /tmp/zen-ai-test.png about:blank
   Screenshot created (5763 bytes). The RemoteAgent ERROR in the log is
   the expected port 9222 bind conflict with the running Zen (it already
   holds 9222), harmless for the test. 0 leftover test processes, temp
   profile, screenshot and log removed after the test.
6. User Zen PID 11292 untouched through all of this, still running with
   flags, BiDi port still responds.

## What still needs the user

A live Super Z fresh-launch test needs Zen closed first (with Zen
already running, Super Z only focuses the existing window and the flags
are irrelevant). I did NOT close his Zen. The chain is verified by code
reading, the exact sed extraction, the --help probe, and the headless
end-to-end run. The user can confirm live by closing Zen and pressing
Super Z, then checking ps shows the flags.

## Known limitations (honest)

- /usr/share/applications/zen.desktop has no flags and cannot be edited
  (sudo needs a password). It is shadowed by the user .desktop, so no
  live path reaches it. If the user .desktop is ever deleted, the
  fallback would launch unflagged Zen.
- Terminal launches (zen, zen-bin, /opt/zen-browser-bin/zen-bin) are
  explicitly excluded by the user and still launch unflagged Zen.
- The dock check via SSH first failed (OMARCHY_PATH unbound), retried
  with the var set and read from shell.json: Zen is not pinned, so the
  dock is not a Zen path.
