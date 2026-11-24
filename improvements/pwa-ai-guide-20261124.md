# PWA AI guide - Muse / mimeo on the Omarchy laptop

For future agents. Verified live 2026-11-24 ~20:03-20:08 Asia/Ho_Chi_Minh.
Owner opens Muse and mimeo as PWAs. Both are ONE web app (muse.ai) installed in two browsers.
Companion reference: `~/workspace/machine-opt-20261124/pwa-identity.md` (Worker P, CDP proof + identity).
Helper scripts live on the laptop in `/home/james/machine-opt/`.

## Identity (stable - find by class, never by workspace alone)

- App-id (both PWAs): `hichoggbhebpgpgcbcgfpkjmohpcflhh`
- URL: `https://muse.ai/?__pwa=1`
- Muse PWA (Brave): class `brave-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default`, title `Muse`, StartupWMClass `crx_hichoggbhebpgpgcbcgfpkjmohpcflhh`
- mimeo PWA (Chromium): class `chrome-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default`, title `mimeo`, same StartupWMClass
- Live 2026-11-24 20:08: Muse window address `0x56307ed95750`, workspace 2, PID 375357, mapped True, size 901x1176, at [2533, 914]. mimeo NOT running (Chromium down since ~19:23).
- Workspace is NOT enforced by any Hyprland rule (no rule mentions the PWA class). The PWA sits on ws2 because the owner put it there. Always find by CLASS, never assume ws2.

## Launch config (do not change without the owner)

- Muse: `/home/james/.local/bin/brave-origin-intel --profile-directory=Default --app-id=hichoggbhebpgpgcbcgfpkjmohpcflhh`
  - Desktop entry: `~/.local/share/applications/brave-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default.desktop` (Name=Muse)
  - Wrapper `brave-origin-intel`: exports `LIBVA_DRIVER_NAME=iHD`, mesa GLX/EGL vars, then `exec /usr/bin/brave-origin --remote-debugging-port=9224 "$@"`
  - `/usr/bin/brave-origin` reads `~/.config/brave-origin-flags.conf` and prepends those flags (Wayland, gnome-libsecret, VA-API features, Omarchy extensions, ANGLE GL, ignore-gpu-blocklist, no-default-browser-check).
- mimeo: `/home/james/.local/bin/chromium-intel --profile-directory=Default --app-id=hichoggbhebpgpgcbcgfpkjmohpcflhh`
  - Desktop entry: `~/.local/share/applications/chrome-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default.desktop` (Name=mimeo)
  - Wrapper `chromium-intel`: same env vars, then `exec /usr/bin/chromium --remote-debugging-port=9223 "$@"`
  - `~/.config/chromium-flags.conf` has NO CDP flag (clean, no duplicate).
- Brave version live: 157.1.99.57 (Chrome/157.0.8103.79). Brave total RSS ~1.7 GB (whole instance, PWA renderer ~350 MB).
- Install confirmed in profile: `~/.config/BraveSoftware/Brave-Origin/Default/Web Applications/Manifest Resources/hichoggbhebpgpgcbcgfpkjmohpcflhh/` and `~/.config/chromium/Default/Web Applications/Manifest Resources/hichoggbhebpgpgcbcgfpkjmohpcflhh/`.

## CDP (proven, prefer over pixels)

- Muse / Brave: `127.0.0.1:9224`, UP. `/json/version`: Browser Chrome/157.0.8103.79, Protocol 1.3.
  - Page target: id `F0857EB317D3027975B6F70658AB666A`, type `page`, title `Chat - clone1`, url `https://muse.ai/?__pwa=1`. (Target ids change per launch; always re-list, never hardcode.)
  - Browser WS: `ws://127.0.0.1:9224/devtools/browser/6b70a2b9-36d8-4b7d-8df0-e4528868ca60`
  - Control PROVEN by Worker P 20:04 via read-only `Runtime.evaluate` (returned document.title + location.href). No typing, clicking, or navigation was done.
  - Also present: 3 Stripe iframes (js.stripe.com / m.stripe.network). Not agent targets.
- mimeo / Chromium: `127.0.0.1:9223`, DOWN (Chromium closed). Mochi's tab lives in this instance, so it is unreachable until Chromium is back.
- How to drive: list targets with `curl -s http://127.0.0.1:9224/json/list` (or :9223), pick the entry with `"type": "page"`, use its `"webSocketDebuggerUrl"`. Node 26 on the laptop has a global `WebSocket` (no package needed). Python has NO `websocket`/`websockets` lib on the laptop. Prefer CDP over screenshots/mouse: no focus steal, exact state.
- CDP is loopback-only (127.0.0.1). From the VM, reach it over SSH (ssh-laptop.sh), never over the tailnet directly.

## Helper scripts (laptop, /home/james/machine-opt/)

- `pwa-find.sh` (Worker P): prints Hyprland PWA windows + both CDP `/json/list` page targets. Read-only. Run: `~/workspace/ssh-laptop.sh '/home/james/machine-opt/pwa-find.sh'`
- `pwa-focus.sh muse|mimeo` (this task): focuses the PWA window by class via `hyprctl dispatch focuswindow address:<addr>`. If the PWA is not running, it prints NOT RUNNING + the launch command and exits 1. It NEVER launches a browser on its own.
  - Verified 20:08: `pwa-focus.sh muse` -> `FOCUSED muse 0x56307ed95750` (rc 0). `pwa-focus.sh mimeo` -> `NOT RUNNING` (rc 1, correct).
- GUI env for any hyprctl call: `XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/ | head -n1)`

## What changed tonight (2026-11-24, all reversible, running apps unaffected)

By Worker P (20:03-20:05):
- Desktop entries gained `Keywords=` + `Comment=` (launcher searchability). Backups `*.bak-pwaopt-20261124`.
- `/home/james/machine-opt/pwa-find.sh` created and verified. `pwa-identity.md` written on the VM.

By this task (20:04-20:08):
- `~/.config/brave-origin-flags.conf`: removed the duplicate `--remote-debugging-port=9224` line (it was ALSO in `brave-origin-intel`, so Brave got the flag twice). Backup `~/.config/brave-origin-flags.conf.bak-pwaopt-20261124`. Before: flag in both files, cmdline showed it twice. After: flag only in `brave-origin-intel` (grep count 1). Effect: next Brave launch only, running Brave untouched (verified PID 375357 alive, PWA window intact after the edit).
- Both PWA desktop entries gained `StartupNotify=true` + `Categories=Network;Chat;`. Backups `*.bak-pwaopt2-20261124`. `desktop-file-validate` passes (only pre-existing Keywords warnings). Effect: next launch only.
- `/home/james/machine-opt/pwa-focus.sh` created (1368 bytes, +x) and tested (see above).

## What NOT to touch

- Never close, navigate, reload, or type into the owner's PWA windows/tabs unless the task explicitly orders it. Clone1 works in the Muse PWA; Mochi's tab is in the mimeo/Chromium instance.
- Never restart Brave or Chromium to "fix" CDP (a restart kills the session and the owner's tabs). Never kill Brave while the owner may be using it.
- Never relaunch mimeo/Chromium on your own: it opens the owner's mimeo session and needs the owner (or an explicit relaunch order).
- Never reinstall or re-register either PWA. Both desktop entries and profile installs are correct.
- Never use ydotool. SSH dies ~30s: keep remote commands short, run long jobs detached.
- Never push personal info to GitHub. The app-id and ports above are app config, not personal data.

## Pending / left for later

- mimeo/Chromium relaunch (restores Mochi's tab + CDP 9223): needs the owner or an explicit order. Do NOT auto-relaunch.
- Flag dedup takes effect at the NEXT Brave launch only. Verify then: `ps` cmdline should show `--remote-debugging-port=9224` exactly once.
- Cold-start time of the PWA was NOT measured tonight (cannot launch a second instance of the same app-id; it would just focus the existing window, and restarting Brave is forbidden). Method for tomorrow: close the PWA, time `gtk-launch` of the desktop entry until the window maps (`hyprctl clients` shows mapped True), record it.
- mimeo window class `chrome-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default` is INFERRED from the .desktop filename and the Brave pattern, not observed live (Chromium down). Confirm it when mimeo runs again.
- No Hyprland window rule pins the PWA to ws2. If the owner wants it pinned, add a rule (e.g. `windowrulev2 = workspace 2, class:brave-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default`) - needs the owner's say-so, not done.
