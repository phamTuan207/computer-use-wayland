# PWA identity reference - Muse / mimeo (the owner's Omarchy laptop)

Verified live 2026-11-24 ~20:03-20:05 Asia/Ho_Chi_Minh by worker P (PWA optimization).
Do NOT edit Brave/Chromium flags or reinstall any PWA without the owner; this file is reference only.

## App identity (both PWAs are ONE app-id)

- App-id: `hichoggbhebpgpgcbcgfpkjmohpcflhh` (muse.ai PWA)
- URL: `https://muse.ai/?__pwa=1`
- Brave window class: `brave-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default`
- StartupWMClass (both desktop entries): `crx_hichoggbhebpgpgcbcgfpkjmohpcflhh`

## Launch commands

- Muse (Brave): `brave-origin-intel --profile-directory=Default --app-id=hichoggbhebpgpgcbcgfpkjmohpcflhh`
  - Wrapper: `/home/james/.local/bin/brave-origin-intel` -> `exec /usr/bin/brave-origin --remote-debugging-port=9224 "$@"`
  - Desktop entry: `~/.local/share/applications/brave-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default.desktop` (Name=Muse)
- mimeo (Chromium): `chromium-intel --profile-directory=Default --app-id=hichoggbhebpgpgcbcgfpkjmohpcflhh`
  - Wrapper: `/home/james/.local/bin/chromium-intel` -> `exec /usr/bin/chromium --remote-debugging-port=9223 "$@"`
  - Desktop entry: `~/.local/share/applications/chrome-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default.desktop` (Name=mimeo)
- Both wrappers also export `LIBVA_DRIVER_NAME=iHD`, `__GLX_VENDOR_LIBRARY_NAME=mesa`, `__EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/50_mesa.json`.
- Brave flags file `~/.config/brave-origin-flags.conf` already contains `--remote-debugging-port=9224` (so the flag appears twice on the Brave cmdline: flags.conf + wrapper). Do NOT edit flags files; a restart would be needed and the owner did not ask for one.

## CDP status (verified 2026-11-24 20:03-20:05 +07)

### Muse / Brave - UP, controllable

- Port: `127.0.0.1:9224` (LISTEN, confirmed via `ss -ltn`)
- `/json/version`: Browser `Chrome/157.0.8103.79`, Protocol `1.3`, V8 `15.7.112.43`
- Browser WS: `ws://127.0.0.1:9224/devtools/browser/6b70a2b9-36d8-4b7d-8df0-e4528868ca60`
- Page target: id `F0857EB317D3027975B6F70658AB666A`, type `page`, title `Chat — clone1`, url `https://muse.ai/?__pwa=1`
- Also present: 3 Stripe iframes (js.stripe.com / m.stripe.network) - not agent targets.
- Control probe (read-only `Runtime.evaluate`, returned `document.title + " | " + location.href`): returned `"Chat — clone1 | https://muse.ai/?__pwa=1"`. CDP control WORKS. No typing, clicking, or navigation was done.
- Main process PID: `375357` (`/opt/brave-origin-bin/brave ... --remote-debugging-port=9224 --profile-directory=Default --app-id=hichoggbhebpgpgcbcgfpkjmohpcflhh`); parent wrapper PID `375349` (`/bin/bash /opt/brave-origin-bin/brave-origin ...`).

### mimeo / Chromium - DOWN

- Port: `127.0.0.1:9223` NOT listening (`ss` shows only 9224); `curl http://127.0.0.1:9223/json/list` fails (connection refused).
- No `/usr/bin/chromium` process running (`pgrep -f chromium` matches only Brave binaries). Chromium was already down as of ~19:46 and still down at 20:05.
- mimeo was NOT relaunched (task forbids it; relaunching would also need the owner - it would open the user's mimeo session). To restore: run the mimeo launch command above, or click the mimeo desktop entry, then re-run `pwa-find.sh`.
- Note: mimeo's tab (Mochi's tab) lives in this Chromium instance, so Mochi's tab is unreachable until Chromium is back.

## Stable window identity (hyprctl, verified 2026-11-24 20:04 +07)

Hyprland env: `XDG_RUNTIME_DIR=/run/user/1000`, `WAYLAND_DISPLAY=wayland-1`, `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus`, `HYPRLAND_INSTANCE_SIGNATURE=11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795342782_301493614`

| PWA | address | class | title | workspace | PID | mapped |
| --- | --- | --- | --- | --- | --- | --- |
| Muse | `0x56307ed95750` | `brave-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default` | `Muse` | 2 | 375357 | True |
| mimeo | - (not running) | - | - | - | - | - |

Other windows seen at the same time (do NOT touch): Zen Browser (`zen`, ws 2, pid 404548, mapped True), `org.omarchy.herdrdrop` (pid 3726). Zen update is a separate coordinator's job.

## How an agent drives the PWA by CDP instead of pixel

1. One-shot status (no browser needed): `/home/james/machine-opt/pwa-find.sh` on the laptop (prints Hyprland window identity + both CDP `/json/list` page targets). Run via `~/workspace/ssh-laptop.sh '/home/james/machine-opt/pwa-find.sh'`.
2. List targets: `curl -s http://127.0.0.1:9224/json/list` (Muse) or `:9223` (mimeo). Pick the entry with `"type": "page"`; its `"id"` is the page target id and `"webSocketDebuggerUrl"` is the page WS URL.
3. Read-only probe: connect a WebSocket client (Node 26 on the laptop has a global `WebSocket`, no extra package needed; Python has no `websocket`/`websockets` lib installed) to the page WS URL and send `{"id":1,"method":"Runtime.evaluate","params":{"expression":"document.title","returnByValue":true}}`.
4. Full control (when a task needs it): same WS connection, `Runtime.evaluate` / `Page.*` / `Input.*` domain calls. Prefer CDP over screenshots/mouse: no focus steal, no pill needed for reads, exact state.
5. Rules: never navigate/reload/close the owner's tabs; never relaunch Brave/Chromium to "fix" CDP (a restart kills the session); SSH dies ~30s, so keep remote commands short and use the laptop helper script for repeated checks.

## What was changed (2026-11-24, reversible)

- `~/workspace/machine-opt-20261124/pwa-identity.md` (this file, VM) - new reference.
- `/home/james/machine-opt/pwa-find.sh` (laptop) - new helper script, executable, verified output 20:05 +07 (Muse window + CDP page shown, mimeo DOWN).
- Desktop entries gained `Keywords=` + `Comment=` lines (launcher searchability for AI/agent use; running apps unaffected, no restart):
  - `brave-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default.desktop`: `Keywords=AI;Muse;chat;assistant;` / `Comment=Muse AI chat PWA (Brave, CDP 9224)`
  - `chrome-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default.desktop`: `Keywords=AI;mimeo;Muse;chat;assistant;` / `Comment=mimeo AI chat PWA (Chromium, CDP 9223)`
  - Backups: same filenames + `.bak-pwaopt-20261124` in `~/.local/share/applications/`.
- Probe artifact `/tmp/cdp-probe.mjs` left on the laptop (ephemeral, harmless).

## Left for later (NOT done, needs restart or owner decision)

- mimeo/Chromium relaunch (would restore Mochi's tab + CDP 9223): needs the owner or an explicit relaunch order; do NOT auto-relaunch.
- Brave/Chromium flag edits (e.g. deduping the double `--remote-debugging-port=9224` from flags.conf + wrapper): needs a browser restart; cosmetic only, CDP already works.
- PWA reinstall / re-registration: not needed, both desktop entries exist and are correct.
- Zen: untouched by design (separate coordinator).
