# WebExtension bridge install guide

Date: 2026-11-21. Bridge version: 0.2.0. Paths below assume the repo
is checked out; the bridge lives in `tests/webext-native-bridge/`.
All commands run on the laptop with a real Firefox or Zen. Nothing
here was verified on this machine, because it has no Firefox or Zen
binary and no `~/.mozilla` profile. Browser-side steps are marked
UNVERIFIED until run on the laptop.

## What gets installed

Two pieces, both local only:

1. A native messaging host manifest at
   `~/.mozilla/native-messaging-hosts/computer_use_bridge.json`. It
   points at `tests/webext-native-bridge/host/cu_bridge_host.py` and
   allows only the extension id `cu-bridge@example.local`.
2. The extension itself, `tests/webext-native-bridge/extension/`
   (Manifest V2, persistent background page). It is loaded
   temporarily for testing, or signed and force-installed for
   permanent use.

No files are written anywhere else by the installer, except the
optional `distribution/policies.json` described below.

## Install, step by step

### 1. Install the host manifest

From the bridge folder:

```sh
cd tests/webext-native-bridge
python3 install.py
python3 install.py --check
```

`--check` verifies the manifest exists, parses, points at an existing
executable host, and allows the extension id. It prints `CHECK OK`
lines and exits 0, or `CHECK FAIL` lines and exits 1.

Zen reads the same `~/.mozilla` registration as Firefox. Do not
write a copy under `~/.zen`: other projects tried that and it did
not work, and the fix was to move the manifest back to `.mozilla`.
Flatpak Zen is the exception: the manifest and the host must also be
visible inside the sandbox, so copy both into the Flatpak home
before running the installer there.

### 2. Load the extension temporarily (testing)

1. Open `about:debugging#/runtime/this-firefox`.
2. Choose Load Temporary Add-on.
3. Pick `tests/webext-native-bridge/extension/manifest.json`.
4. Open the background console (Inspect on the extension card) and
   confirm the line `[cu-bridge] connected to native host
   computer_use_bridge`, with a timestamp.

Temporary add-ons last until the browser restarts. This is the fast
path for testing, and it is the only path that needs no signing.

### 3. Smoke test the bridge

From a terminal, with the browser open:

```sh
python3 host/cu_bridge_client.py --port 18711 '{"id": 1, "op": "listTabs"}'
python3 host/cu_bridge_client.py --port 18711 '{"id": 2, "op": "host.status"}'
```

`listTabs` should return the real open tabs. `host.status`
reports `pending`, `uptime_s`, `timeouts`, and `errors` counters.
The client prints the reply as JSON and the round trip wall-clock
and elapsed time on stderr. It exits 0 when the reply has
`"ok": true`, else 1.

Try one DOM op against a real tab, for example on a page with a
heading:

```sh
python3 host/cu_bridge_client.py --port 18711 '{"id": 3, "op": "snapshot", "tabId": 1, "maxNodes": 20}'
```

Replace `tabId` with the id from `listTabs`. Record the wall-clock
and elapsed time per op; no timing for a real Zen is claimed yet.

### 4. Permanent install (signed build)

Temporary load does not survive a browser restart. Two permanent
paths exist:

Path A, signed unlisted build (recommended):

```sh
npm install -g web-ext
cd tests/webext-native-bridge
python3 install.py --sign
```

`--sign` builds the extension zip with `web-ext build` and prints
the exact `web-ext sign --channel unlisted` step. Signing needs
AMO API keys from addons.mozilla.org; never store them in the repo.
After signing, force-install the signed `.xpi`:

```sh
python3 install.py --policies <browser-dir> --xpi <signed.xpi>
```

`<browser-dir>` is the directory holding the browser binary, for
example the Zen install directory on the laptop. This writes
`<browser-dir>/distribution/policies.json` with an
`ExtensionSettings` entry that force-installs the extension id from
the `.xpi` file URL. Restart the browser for policies to apply.

Path B, unsigned add-ons allowed (Nightly or Developer Edition
only): set `xpinstall.signatures.required` to false in
`about:config`, then load the extension from
`about:debugging` as in step 2 and use the "Install Add-on From
File" path, or keep the temporary load and re-install after each
restart. Do not turn signatures off in a daily profile.

Neither permanent path is verified here. Record which path was
chosen on the laptop and whether the extension survived a restart.

## Uninstall

```sh
cd tests/webext-native-bridge
python3 install.py --uninstall
```

This removes only the manifest file at
`~/.mozilla/native-messaging-hosts/computer_use_bridge.json`. The
host script stays on disk. Then remove the extension from
`about:addons`, and if policies were used, delete the
`ExtensionSettings` entry from
`<browser-dir>/distribution/policies.json` and restart the browser.

To verify removal: `python3 install.py --check` must fail with
`CHECK FAIL: manifest missing`, and the extension must be gone from
`about:addons`.

## Troubleshooting

- `CHECK FAIL: manifest missing`: run `python3 install.py` again,
  then `--check`. Check that `$HOME` is the same home the browser
  runs under.
- `CHECK FAIL: host path is not executable`: run
  `chmod +x tests/webext-native-bridge/host/cu_bridge_host.py`,
  then `--check`.
- `CHECK FAIL: host path missing`: the repo moved since install.
  Re-run `python3 install.py` from the new checkout location.
- Background console shows no `[cu-bridge] connected` line: the
  manifest is missing or wrong, or the host crashed on start. Run
  `python3 install.py --check` first, then run the host by hand
  with `python3 host/cu_bridge_host.py` and read its stderr log.
  The host logs every error with a UTC timestamp.
- `native port disconnected` in the background console: the host
  died. The background script counts the death, logs it with a
  timestamp, and reconnects with backoff (1s, 2s, 5s, 10s, 30s),
  which relaunches the host. If it keeps dying, read the host
  stderr log; a common cause is a bad manifest path or a host
  script that fails to parse.
- Agent request returns `timed out waiting for browser reply`: the
  tab did not answer within `CU_BRIDGE_TIMEOUT_S` (default 30 s).
  The host logs the timeout with id and op. Check whether the tab
  is a page the content script cannot run in (internal `about:`
  pages, restricted pages). Those fail with a clear error, not
  silently.
- Agent request returns `tab reply timed out after 25000 ms`: the
  background script gave up on the tab before the host did. Same
  checks as above.
- `waitFor timed out`: the selector never matched a visible
  element within the timeout. Check the selector with a `snapshot`
  first, and raise `timeoutMs` (max 120000).
- `upload` returns `element is not a file input`: the selector
  must match an `<input type="file">`. The file bytes travel as
  base64 in the request; keep files small, the host refuses any
  request over 1 MB.
- `snapshot` returns `truncated: true`: raise `maxNodes` (max
  1000) or page through the snapshot. Replies over 1 MB are
  refused by the host.
- Extension loads but `listTabs` returns an empty list: the
  browser may be running with a different profile. Load the
  extension in the profile that owns the tabs.
- Flatpak Zen: the manifest and host must be visible inside the
  sandbox. Install both into the Flatpak home and re-run the
  installer there.

## Security notes

The TCP port binds loopback only and has no authentication, so any
local process can drive the browser through it. That is the same
trust model as the loopback BiDi port in `scripts/zen_cli.py`.
Only run it on a machine where local processes are trusted, and do
not forward the port. The native host only accepts the extension id
`cu-bridge@example.local`, and the manifest only allows that id.
