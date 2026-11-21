# Worker F1 log: session guardian startup failure
# Owner order 22:18 21/11/2026: full team, full power, fix the big errors first.
# Symptom: `computer-use session` dies in 0.46s, "session guardian startup failed",
# no pill/overlay ever appears. Direct Pointer click works (22:17, 0.31s, cursor
# 2598,1174, no miss) but bypasses the session, so no pill. All times +07.
# Times below are wall-clock Asia/Ho_Chi_Minh + elapsed.

## 22:19 test start
- VM repo todolist-push HEAD 5792a82. Installed tree
  /home/james/.local/share/agent-computer-use/scripts/ md5-identical to the VM
  repo for cu.py, cursor_session.py, cursor_theme.py, indicator.py,
  cancel_hotkey.py. No version skew; the fix goes in the repo and deploys via
  sync-installed.py (or exact-path copy).
- Ruled out by the parent before F1: no SNAPSHOT (session.json absent), no
  cancel latch (status cancelled:false), no stale session processes (only the
  relay PID 1821 serving since 15:17), no stale geckodriver. Observe works
  over bare SSH (22:13:53, 41.6ms).

## Findings (code read + live probes)
- Guardian startup order (cursor_session.py guardian): owner_lock ->
  SNAPSHOT check -> cancel latch -> cursor_theme.snapshot(env) ->
  cursor_theme.check_guard(env) -> write SNAPSHOT -> hotkey_on ->
  cursor_theme.apply(env) [Guard.__init__] -> indicator.listen ->
  indicator.Native -> print('ready'). Supervise waits 15s for 'ready';
  instant death means an early step threw (supervisor swallows stderr).
- `hyprctl cu-cursor status` on the LIVE session returns "unknown request"
  with rc=0. Live plugin list: hyprbars ONLY. The cursor-guard Hyprland
  plugin is not loaded, and /run/user/1000/agent-computer-use/ does not
  exist at all (no cursor-guard.sock).
- cursor_theme.check_guard runs `hyprctl cu-cursor status` then
  guard_reply() which json.loads the reply: "unknown request" is not JSON,
  so it throws JSONDecodeError. That is the prime suspect for the FIRST throw.
- Guard.__init__ would throw next (FileNotFoundError on the missing socket
  dir) even if check_guard passed.
- The pinned cursor-guard library EXISTS: plugins/cursor-guard-06712eaf...
  .so (454,824 B, Nov 15), named in native/visuals.json as
  cursor_guard_library. activate-cursor-guard.py is the first-load path, but
  it REFUSES unless indicator.liquid_available(env) is true, i.e. hyprglass
  loaded + active + version 1.1.1-cu.1 + versionCheck match. The live
  session has NO hyprglass loaded either (hyprbars only).
- No `cu-cursor` / `cursor-guard` lines in hyprland.conf or conf.d: plugin
  loads are first-load manual steps, not login-persistent. Live Hyprland
  PID 1515 alive since 03:05:59 today; the plugins were never re-activated
  after that restart. Broker sessions worked before 03:05 (mimo B2 ~00:45);
  none proven after. That is the current root-cause hypothesis, to be proven
  by the step probe below.

## Step probe (guardian startup steps, individually, with tracebacks)

## 22:22-22:33 - Owner method: read source + crawl, then fix at the root

Owner order 22:22 (MEMORY.md F TEAM): read all related source + crawl (web, repo history, upstream, similar projects) to find the root cause, origin, reason, record file/line + evidence, then fix at the root. No guessing, no retrying around it. Applied to F1/F2/F3.
Owner rule 22:23 (TEST DESIGN, standing): future tests must be composite (DOM + CLI + mouse + keyboard in one test), test-maker must not know the questions (independent test-designer), applies to Y13/Y14 live, A1, final test, any new test. Still under Lauren Tan process.
Owner status 22:25-22:27: Zen WEDGED (cannot click/open any website, photo 22:25, PID 27958 alive). F3 ordered to restore Zen. ZT team writing ~10 composite blind user scenarios (ZT-B runs after F3 restores). New errors J1-J6 added (todolist 4.7-4.12). Owner went to sleep 22:27; work overnight, do not disturb.

## Root cause - COMPLETE, proven end to end (22:19-22:33)

Layer 0 (user-visible): `computer-use session` dies in 0.46s with
`{"ok": false, "error": "session guardian startup failed"}`, no pill, no reason.

Layer 1 (code defect): `scripts/cursor_theme.py:99-108` (`guard_reply` + `check_guard`).
`check_guard` runs `hyprctl cu-cursor status` via `command()` (check_output, raises
only on non-zero exit) and passes raw stdout to `guard_reply`, which does
`json.loads(raw)` unconditionally. When the cursor-guard plugin is not loaded,
Hyprland answers `unknown request` with EXIT CODE 0, so no subprocess exception
is raised; instead `json.loads("unknown request")` throws
`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`.
PROVEN live in the step probe 22:19 (check_guard THROW, 0.004s, traceback in
probe). The guardian dies before `print('ready')` (`cursor_session.py:145-146`),
so `supervise` (`cursor_session.py:225-231`) raises the opaque
`RuntimeError('session guardian startup failed')` and the CLI reports only that.
The guardian's real cause is swallowed: `supervise` pipes the guardian's stdout
only, stderr is inherited, never captured into the error envelope.

Layer 2 (runtime state): neither plugin is loaded in the live compositor.
`hyprctl -j plugin list` = hyprbars only. `hyprctl cu-cursor status` =
`unknown request` (rc 0). No `/run/user/1000/agent-computer-use/` dir, no
cursor-guard.sock (the plugin owns that socket; `Guard.__init__` would throw
FileNotFoundError next, proven in the probe). Plugins load only via manual
first-load scripts; nothing re-loads them after a compositor restart.

Layer 3 (login loader failed): the fresh-login loader DID run at this
compositor's login (spawn 2026-11-21T08:17:29Z = 15:17:29 +07, 4s after
compositor start 15:17:25, inside the 30s fresh-login window) but FAILED at
`manifest_validation` with `ValueError: profile does not match the pinned
optics source`. Evidence: loader log
`~/.cache/agent-computer-use/logs/visuals.jsonl` last record, instance
`11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825` (the CURRENT
instance, matches the observe), stage `manifest_validation`, time 1795249050.
stderr log `visuals-stderr.log` corroborates (same instance tuple, then
`visuals: profile does not match the pinned optics source`). The previous
instance (1795201820) failed the SAME way; the one before (1795086072)
SUCCEEDED (stage complete, glass 199153ae, guard 06712eaf).
Failing check: `scripts/visuals.py::_login` -
`if manifest['profile_sha256'] != hashlib.sha256(OPTICS.read_bytes()).hexdigest():
raise ValueError('profile does not match the pinned optics source')`,
OPTICS = `<repo>/native/hyprglass-local-optics.lua`, manifest =
`<repo>/native/visuals.json`, both read from the LAPTOP repo
(`/home/james/computer-use-wayland`) because `visuals-login.lua` runs that copy.

Layer 4 (THE DRIFT - root): the laptop repo is stale vs the setup-published
state, in three fields. Laptop repo is at detached HEAD 56f5af4 (predates the
blur-0.15 commit b2afcd1, Nov 20 20:40) with uncommitted changes; it must NOT
be force-synced.
- Laptop optics file: sha256 `545455d3...` = commit 09a8df7 (blur 0.0, shayxo
  Legacy Chrome params). The user ORDERED blur 0.15 on Nov 21 (G11: pill read
  as almost transparent).
- Laptop manifest `profile_sha256`: `674441ea...` - matches NO known optics
  version (checked 09a8df7=545455d3, 9ecc167=71a52904, 78b0615=a3cd50e9).
- Laptop manifest `library`: hyprglass-`d086bc43...`.so (older build).
Setup-published state (installed tree `/home/james/.local/share/agent-computer-use/`):
- optics sha256 `9a151634...` = commit b2afcd1 (blur 0.15).
- manifest pins `profile_sha256` 9a151634 + `library` hyprglass-`199153ae...`.so.
- installed optics sha256 verified = 9a151634. Installed manifest diff vs laptop
  manifest: exactly the 2 fields (library, profile_sha256).
The b2afcd1 commit message says: "No visuals.json manifest in this checkout,
so no pin to refresh here; the install/sync re-pins profile_sha256." The sync
re-pinned the INSTALLED manifest but the LAPTOP REPO's manifest (a gitignored
local file) was never re-pinned, and the laptop repo's optics file was never
updated to b2afcd1. So the login loader has failed at manifest_validation since
the blur-0.15 change, glass was never loaded, the guard was never loaded, and
every session since has died at check_guard.
Both plugin .so files are loadable NOW: pinned glass 199153ae ldd resolves
libaquamarine.so.15 + libhyprgraphics.so.5 (0 not found); Y6e rebuild also
resolves; cursor-guard 06712eaf full ldd = 0 not found (libXcursor, libstdc++,
libm, libgcc_s, libc, libXrender, libXfixes, libX11, libxcb, libXau, libXdmcp).
(The Y6c "dead ABI" finding was about vendor-dir/backup binaries, not these
pinned builds.) Live abiHash = `11cbc6c5..._aq_0.16_hu_0.14_hg_0.6_hc_0.1_hlg_0.6`,
exactly the manifest `abi`. Activation gates will pass on version/ABI.

Crawl evidence (corroborates the mechanism, not the local drift):
- hyprglass docs (git.nnstdios.com/hyprnux/hyprglass): "A paused hyprglass
  ... has no `hyprctl hyprglass` command: `hyprctl hyprglass status` answers
  `unknown request`." - upstream-documented: an unloaded plugin's custom
  hyprctl command answers "unknown request".
- Hyprland wiki (wiki.hypr.land/hyprland-plugins/using-plugins): plugins load
  via `hyprctl plugin load path` / `hl.plugin.load(path)` / `hyprpm reload`;
  "add `hyprpm reload` to your Hyprland config's autostarts to have plugins
  loaded at startup" - plugins are NOT persistent across restarts unless the
  config reloads them. Our repo loads plugins only via first-load scripts.
- cjennings dotfiles (git.cjennings.net, 2026-11-01): "Under a Lua config
  `hyprctl keyword` answers `unknown request` and exits 0" - confirms hyprctl
  exits 0 on an unknown request, so the caller must read the reply; the author
  wrote a guard scanning for exactly this bug class ("a stale call fails
  silently on the desktop while every test passes"). Same class as check_guard.
- Repo history: `617ac2a fix: hold the agent cursor throughout computer-use
  sessions` introduced `cu-cursor`; `72ea6ef fix: require agent cursor before
  starting computer-use sessions` made it a hard gate; `0ba9584 WIP:
  computer-use 0.57.2 port + fresh-login fix (round 1)` is the latest touch.
  No commit guards the plugin-missing case in check_guard or re-pins the
  laptop-repo manifest after an optics change.
- Login seam: `~/.config/hypr/hyprland.lua` dofiles
  `/home/james/computer-use-wayland/native/visuals-login.lua` (gitignored,
  laptop-local). That file: if hyprglass 1.1.1-cu.1 already loaded, apply
  optics; else `hl.on("hyprland.start", hl.exec_cmd(python3 visuals.py
  <laptop-repo visuals.json>))`. `agent_computer_use_glass.lua` is a stub:
  "Legacy visuals retired; repository setup owns the fresh-login profile."
  Prior diagnosis (live-test-log.md:464, :2601): the login loader's failure is
  silent because `hl.exec_cmd` redirects child stdout/stderr to /dev/null and
  never records the exit code; the loader's own jsonl + stderr logs are the
  only record. `visuals.py` itself captures stderr to
  `~/.cache/agent-computer-use/logs/visuals-stderr.log` and spawns to
  `visuals-spawn.jsonl` (added by commits cb23219, be552a4, 8cde64c).

## VM incident blocking SSH (22:26-22:31, fixed)

SSH to the laptop broke at ~22:26: `tailscale-proxy.py` failed with
`AttributeError: module 're' has no attribute 'compile'`. Cause:
`/usr/lib/python3.12/re/__init__.py` was MISSING from the VM's system Python
(`re` imported as a namespace package). `dpkg -V libpython3.12-minimal`
reported exactly that ONE missing file; nothing else damaged. The `re/` dir
mtime was Nov 21 15:25; last successful SSH was ~22:24, so the deletion window
is unclear (mtime anomaly noted, not resolved). Restored 22:31: downloaded the
authentic file from CPython v3.12.3 tag
(raw.githubusercontent.com/python/cpython/v3.12.3/Lib/re/__init__.py),
md5 `14c5eb10123bc6623861305257e1c156` EXACTLY matches dpkg's expected md5 for
`usr/lib/python3.12/re/__init__.py`, installed with sudo (644, root:root).
Verified: `python3 -c "import re"` OK, `dpkg -V libpython3.12-minimal` clean,
SSH to laptop OK (22:31:17 +07). apt is NOT usable for this (azure.archive
unreachable). Flag to parent: the deletion cause is unknown; no other system
file is affected.

## Fix plan (root, all layers)

A. Repair the drift (laptop-local, verified, no git ops): copy installed optics
   (sha 9a151634) over laptop-repo optics; copy installed manifest over
   laptop-repo manifest. Verify: sha256(laptop optics) = 9a151634, diff of the
   two manifests empty. This makes the login loader pass manifest_validation
   at the next login. (The laptop repo stays at detached HEAD 56f5af4; only
   these two gitignored/local-state files change.)
B. Live restoration (needs the live slot; F3 is restoring Zen now - sequence
   after F3, do not drive the screen concurrently): run the designed
   first-loads on the live compositor with the corrected values:
   `activate-glass.py <199153ae .so> --abi <manifest abi>
   --profile-sha256 9a151634` (profile read from the installed tree, already
   matches), then `activate-cursor-guard.py <06712eaf .so> --abi <manifest abi>`.
   Verify: plugin list shows hyprglass + computer-use-cursor + hyprbars,
   `hyprctl cu-cursor status` returns JSON, socket exists.
C. Code fix 1 (`scripts/cursor_theme.py:99-108`): validate the hyprctl reply
   before json.loads; on a non-JSON reply raise a clear RuntimeError naming
   the missing plugin + the activation commands. Mirror the guarded pattern
   already used in `activate-glass.py` (try/except JSONDecodeError ->
   RuntimeError('invalid compositor version response')).
D. Code fix 2 (`scripts/cursor_session.py:210-231` supervise): pipe the
   guardian's stderr and include its last lines in the startup-failure error,
   so a future death names its cause.
E. Proof (live, after B): session start; pill in a fresh observe (scp + view);
   ONE harmless click on the already-selected tab row (re-check the row in a
   fresh observe first - F3 may have restarted Zen); verify via cursorpos +
   fresh observe; clean stop; desktop clean (pill gone, no stray processes).
   Also prove the loader's manifest validation now passes: run visuals.py
   mid-session, it must fail at fresh_login_gate (age >> 30s), NOT at
   manifest_validation.
F. Council (3 voices) + redteam over the diff + this plan before the live
   activation (B). Commit on todolist-push, ls-remote verify.

## 22:35-22:42 - Code fix implemented, tested, deployed, live-proven (negative)

Owner target 22:40: whole team to 240 commits before 24:00 today (now 189
commits + 1 PR = 190, need ~51). Every small step done = commit + push at
once, never accumulate. Quality still first, council + redteam complete.
VMFIX DONE (22:40): SSH restored durably. VMFIX confirms F1 fixed the right
file (re/__init__.py from CPython 3.12.3, dpkg -V clean, observe 22:38 ok);
the root cause of the deletion is still UNKNOWN; the guardian failure is NOT
due to re, it is the cursor-guard plugin not loaded, F1 is fixing it.

### Drift repair (A) - DONE 22:37, proven
Copied installed optics (sha 9a151634) over laptop-repo optics and installed
manifest over laptop-repo manifest. After: laptop optics sha = 9a151634,
manifest diff empty, `git diff --stat` = 7 lines (6 insertions, 1 deletion),
exactly commit b2afcd1. Proof: re-ran the login loader mid-session; it now
fails at stage `fresh_login_gate` (compositor age >> 30s), NOT at
`manifest_validation`, for the current instance 1795249046 (loader log record
time 1795275379). The loader will pass manifest_validation at the next login.

### Code fix (C + D) - DONE 22:36-22:41
- `scripts/cursor_theme.py:99-113` (`guard_reply`): catch JSONDecodeError and
  raise a clear RuntimeError naming the reply (truncated, decoded for the
  bytes/bytearray socket path) and the remedy (activate-glass.py +
  activate-cursor-guard.py, or re-run visuals.py). Covers all three callers:
  check_guard (hyprctl status), restore (hyprctl release), Guard.receive
  (socket). First version missed the bytes case: the socket path passes a
  bytearray, so `raw.strip()[:120]` raised TypeError and broke
  `test_command_responses_are_bounded_framed_and_token_checked` ('garbage').
  Fixed by decoding bytes/bytearray as UTF-8 with replace before formatting.
  Test comment updated to the new behavior.
- `scripts/cursor_session.py:210-231` (`supervise`): pipe the guardian's
  stderr, drain it on a daemon thread into a deque (maxlen 32), include the
  tail in the startup-failure RuntimeError. First version swallowed the
  guardian's stderr warnings on the success path and broke
  `test_hotkey_failure_warns_but_driver_runs` ('warning:' not in err). Fixed
  by TEEING every drained line to the supervisor's stderr as it arrives, so
  warnings stay visible exactly as when the guardian inherited stderr.
- Tests added: `test_guard_reply_names_missing_backend_on_non_json_reply`
  (test_cursor_theme.py, str + bytes + bytearray + check_guard paths);
  `test_unloaded_backend_names_missing_plugin_and_never_starts_driver`
  (test_cursor_session.py, FAKE hyprctl `status_garbage` flag prints
  'unknown request' with exit 0, asserts the driver never runs and the error
  names the missing backend).

### Test evidence
- VM (python 3.12): `tests.test_cursor_theme` 34 tests OK (0.17s).
- `tests/test_cursor_session.py` does NOT compile on the VM's Python 3.12:
  `SyntaxError: too many statically nested blocks` at line 566 (the
  `test_cleanup_exceptions_cannot_skip_restore` with-statement). PRE-EXISTING:
  the file is unmodified in the working tree (last touches 0ba9584, e3d2cc7).
  The laptop runs Python 3.14.10, where it compiles. Flagged, not fixed here
  (out of F1 scope; needs a Python-version note or a test refactor).
- Laptop (python 3.14.10, /tmp/f1-test copy): targeted run 36 tests OK, then
  37 tests OK after the tee fix (new test + hotkey test + missing/busy test +
  full test_cursor_theme). Full file run 1: 34 tests, 1 FAILURE
  (hotkey warning swallowed, my regression, fixed by the tee). Full file run
  2 (after tee): 34 tests OK in 29.7s.
- Deploy verified by md5: installed cursor_theme.py 502a4941...,
  cursor_session.py 088e30de... (before tee) then 5d6c580a... (after tee),
  matching the VM repo exactly after each copy.

### Live negative test (22:39) - PROVES fixes 1 + 2 live
Fresh observe 22:39:21 id 0b8810350e2a (capture 39ms). Ran the exact original
failing command: `computer-use session -- computer-use act --observation
0b8810350e2a --actions '[{"type":"click","x":135,"y":272}]'`. Result RC=1:
`{"ok": false, "error": "session guardian startup failed: cursor guard reply
is not valid JSON (got: unknown request); the cursor backend may not be loaded,
load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or
re-run the fresh-login loader scripts/visuals.py"}`. Before the fix (22:19)
the same command gave only `{"ok": false, "error": "session guardian startup
failed"}`. The guardian's cause now reaches the error envelope; stderr empty
(the message is in the envelope, as designed).

### Still to do
- Council (3 voices) + redteam over the fix diff + the live activation plan.
- Live activation (B) + proof (E), gated on review GO and the live slot (F3
  is restoring Zen; do not drive the screen concurrently).
- Commit + push in small increments now (owner 240 target): code + tests,
  then this log.
