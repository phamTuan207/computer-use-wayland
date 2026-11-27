# Worker F1 log: session guardian startup failure
# Owner order 22:18 21/11/2026: full team, full power, fix the big errors first.
# Symptom: `computer-use session` dies in 0.46s, "session guardian startup failed",
# no pill/overlay ever appears. Direct Pointer click works (22:17, 0.31s, cursor
# 2598,1174, no miss) but bypasses the session, so no pill. All times +07.
# Times below are wall-clock Asia/Ho_Chi_Minh + elapsed.

## 22:19 test start
- VM repo todolist-push HEAD 5792a82. Installed tree
  ~/.local/share/agent-computer-use/scripts/ md5-identical to the VM
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
(`~/computer-use-wayland`) because `visuals-login.lua` runs that copy.

Layer 4 (THE DRIFT - root): the laptop repo is stale vs the setup-published
state, in three fields. Laptop repo is at detached HEAD 56f5af4 (predates the
blur-0.15 commit b2afcd1, Nov 20 20:40) with uncommitted changes; it must NOT
be force-synced.
- Laptop optics file: sha256 `545455d3...` = commit 09a8df7 (blur 0.0, shayxo
  Legacy Chrome params). The user ORDERED blur 0.15 on Nov 21 (G11: pill read
  as almost transparent).
- Laptop manifest `profile_sha256`: `674441ea...` = commit d27ad0a (blur 0.10
  bottle candidate), verified 22:50 by `git show d27ad0a:native/hyprglass-local-optics.lua | sha256sum`
  = 674441ea1b7d27f347aa8e31224ac5a8fcd923fc22ae75e65a0936ad8acc17c9. CORRECTED
  22:50 (council 1 A5): the earlier claim that it matched no known optics
  version was WRONG. The true drift was subtler: the laptop optics file was
  from 09a8df7 (blur 0.0) while the manifest pin was from d27ad0a (blur 0.10),
  so optics and manifest came from two different stale commits, and both were
  stale against b2afcd1 (blur 0.15).
- Laptop manifest `library`: hyprglass-`d086bc43...`.so (older build).
Setup-published state (installed tree `~/.local/share/agent-computer-use/`):
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
  `~/computer-use-wayland/native/visuals-login.lua` (gitignored,
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

## 22:42-22:48 - Council 2 (live safety) verdict: AMEND

Verdict file: improvements/worker-f1-council-2.md (280 lines, 0 em/en dashes,
not yet committed at verdict time). Council 2 verified the root cause chain
and the code fix independently, live and read only. The code fix is sound.
The drift repair was the right repair and is proven on disk and in the loader
log. The live activation is the risky step, because a plugin load crash kills
the whole compositor with the owner asleep. Verdict AMEND: the activation may
proceed only after all 8 numbered preconditions are met, in order.

New facts from council 2's live checks:
- Zen was restarted by F3 (old PID 27958 dead, new PID 426338), with remote
  debugging and marionette up. Live clients are 4 windows, including a Zen
  window titled Offline Whiteboard App. All prior tab coordinates are stale.
- Owner order 22:45 (MEMORY.md): open the Omarchy menu and switch workspaces
  by COMMAND (hyprctl dispatch, hl.dsp form; find the exact launcher command
  from config), NEVER by clicking workspace/menu buttons on the bar.
  Fastest-path-first: CLI first, mouse last. Source: the owner saw a stray
  click open the Omarchy menu around 22:44; the 22:44:32 photo shows no menu
  open anymore; F2/F3 logs do not record the click; unidentified which worker.
  The proof must contain at most the one planned click and no bar clicks.
- The reload step re-applies optics from the LAPTOP REPO copy (hyprland.lua:54
  dofiles visuals-login.lua), not the installed copy. Both are 9a151634 now,
  so it is safe tonight, and it is a second reason the drift repair had to
  cover the laptop repo copy.
- Installed scripts/indicator.py is newer than the laptop repo copy (metrics,
  label command, capture nesting); the liquid gate logic is identical, so the
  activation gates are unaffected. A future repo-to-installed sync would
  regress it. Follow up, not a precondition.
- The laptop manifest pin 674441ea matches commit d27ad0a (blur 0.10), verified
  22:50. CORRECTED 22:50 (council 1 A5): the earlier "matched no known optics
  version, suggests a manual edit" line was WRONG. The drift was two stale
  commits (optics 09a8df7, pin d27ad0a), not a mystery pin.

Findings F1-F10 (full text in the verdict file):
- F1. Plugin load dlopens in-process; a segfault kills Hyprland PID 1515
  outright with every window and unsaved work. No sandbox, no snapshot, no
  auto recovery. Mitigated by exact ABI, clean ldd, and the prior successful
  load of these exact binaries on instance 1795086072. Residual risk low but
  nonzero while the owner sleeps.
- F2. activate-glass.py takes no owner_lock and no session/token check, unlike
  the guard script and visuals.py. Concurrent runs can both pass the pre-load
  check. A retry after partial success fails closed at setup_baseline with a
  misleading message.
- F3. TOCTOU on the .so files: digest computed, then loaded by path with no
  re-hash; post-load asserts check only name/author/version, not the loaded sha.
- F4. Half-loaded rollback gap: glass ok but reload refused or wait_for_profile
  timeout leaves glass loaded with no rollback and no documented recovery.
- F5. Hyprctl timeouts (5s glass, 10s guard) leave load state unknown; a blind
  retry could double load.
- F6. Reload applies laptop repo optics, not installed optics (see above).
- F7. Indicator drift (see above).
- F8. Proof click coordinates stale, target unknown (Zen restarted, whiteboard
  live, F3 may still be restoring, owner order 22:45).
- F9. Shader warm-up can exceed the 8s wait; a first guard refusal may mean
  slow shaders only.
- F10. No written crash contingency for a dead compositor while the owner sleeps.

Preconditions 1-8 (all required, in order, before the live activation):
1. Sequence after F3 sign-off, Zen PID stable, single operator, no parallel driving.
2. Same-minute pre-flight: ABI match, plugin list exactly hyprbars 1.0,
   configerrors empty, no session/token/socket dir, .so shas match filenames
   and manifest, ldd 0 not found on both.
3. Run the installed-tree activation scripts, glass then guard, abi from the
   manifest, profile-sha256 9a151634, no other step between them.
4. Hold owner_lock across the whole glass plus guard sequence; no concurrent
   writers to the plugins dir, no sync-installed during it. NOTE: this needs
   implementation, activate-glass.py takes no lock today. F1 must build the
   lock-holding wrapper before the activation.
5. Half-state recovery agreed in advance: never re-run activate-glass after a
   partial success, guard-only retry, longer wait for slow shaders, re-query
   the plugin list before any retry, never blind retry a load.
6. Corrected proof: fresh observe first, one click at the center of the
   already-active tab only, skip the click if the active tab is the whiteboard
   or has unsaved state, workspace/menu moves by command only, verify via
   cursorpos plus a second fresh observe, clean stop and clean desktop check.
7. Crash contingency: if the compositor dies or the desktop freezes, stop,
   report to the parent at once, relaunch nothing blindly.
8. Durability follow-up (tracked, not a precondition): re-pin check in
   sync-installed/setup, reconcile indicator.py, make the silent loader
   failure visible. The root cause is not durably fixed until that lands.

Status: waiting on council 1, council 3 and redteam verdicts. The live
activation stays gated until all four verdicts are adjudicated and the
preconditions are met.

## 22:47:53 - Owner rule: log EVERY event as it happens
Owner rule 22:47: log EVERY event with time, nothing omitted. From now on,
append EVERY action to the log file AS IT HAPPENS (wall-clock Asia/Ho_Chi_Minh
+ elapsed, what was done, target, outcome, coordinates for clicks). Never batch
the log at the end. When the owner asks, the answer must be in the log, never
"I don't know". This entry starts that practice. All entries below carry
wall-clock times.

## 22:47 - Council 1 + redteam verdicts arrived (both AMEND)
- 22:47:44Z (22:47 +07): redteam completed. Verdict AMEND, 13 findings R1-R13,
  file improvements/worker-f1-redteam.md (222 lines, 0 em/en dashes).
- 22:47:26Z (22:47 +07): council 1 completed. Verdict AMEND, 6 required changes
  A1-A6, file improvements/worker-f1-council-1.md.
- Council 3 still running at 22:47. Council 2 already AMEND (22:42-22:48,
  recorded above). Live activation stays gated until all four verdicts are
  adjudicated and the AMEND items are addressed.
- 22:47:53: owner rule received (log every event as it happens, see above).

### Council 1 required changes A1-A6 (AMEND)
- A1. Drain race in supervise (cursor_session.py:247-250): guard_errors is read
  the instant select reports, with no wait for guardian exit and no join of
  the drain thread, so the envelope can still be bare on a fast death. Require
  a short guardian-exit wait plus drain-thread join before reading the tail.
- A2. driver registration failed (line 260) carries no detail. Require the same
  drained tail there.
- A3. guard_reply misses UnicodeDecodeError (cursor_theme.py:100-101). Verified
  live on the VM: non-UTF8 bytearray replies escape as a raw UnicodeDecodeError,
  bypassing the named error on the socket path. Require catching it alongside
  JSONDecodeError.
- A4. The new Lifecycle test does not isolate fix D: the asserted text also
  arrives via the guardian stderr tee, so it passes even if supervise raised
  the old bare error. Require asserting the exact envelope string
  'session guardian startup failed: cursor guard reply is not valid JSON' in stdout.
- A5. LOG ERROR, Layer 4: the old pin 674441ea DOES match a known optics
  version, commit d27ad0a (blur 0.10). The true drift was optics from 09a8df7
  versus a manifest pin from d27ad0a, two different stale commits. The log must
  be corrected. (F1 to verify the sha on the laptop repo before correcting.)
- A6. Recurrence is untracked: the fix is diagnostic only, and nothing stops
  the sync from re-pinning only the installed manifest again at the next optics
  change. Require a tracked follow-up before live activation is declared complete.
- Other findings (not blocking): guard_reply over-attributes every non-JSON
  reply to a missing backend; session_remote.py wraps the named error in a
  generic BrokerError; mid-run guardian death is still silent (exit 1, no
  message); test_cursor_session.py cannot compile on VM Python 3.12
  (pre-existing SyntaxError at line 570), so all session-test evidence is
  laptop-only; one flaky BrokenPipeError in the theme tests observed once,
  then 5/5 passes, pre-existing and unrelated.
- Bottom line from council 1: the root-cause chain is proven live, the fix is
  correct in design, but it must not be presented as restoring sessions. Until
  plan B live activation runs, sessions still fail, only with a clearer error now.

### Redteam findings R1-R13 (AMEND, ranked by severity in the file)
- R1 (High): loader still fails silently at login. The fix only improves the
  session error message. visuals-login.lua fires visuals.py once via hl.exec_cmd
  to /dev/null with the exit code never recorded. The next optics edit without
  a re-pin repeats the exact incident. Also check-visuals-manifest.py only runs
  in the pre-commit hook, and the b2afcd1 commit message admits the manifest
  was absent from that checkout, so the hook is structurally blind to this
  drift class.
- R2 (High): drift repair is not durable. The optics fix is an uncommitted
  change in a repo at detached HEAD 56f5af4; the manifest is gitignored local
  state. Any checkout, reset, clean, or fresh clone wipes it. It was done by
  manual copy, not via the existing refresh-visuals-manifest.py.
- R3 (High): session never gates on hyprglass. check_guard only checks
  cu-cursor. liquid_available is consulted only by activation, and Native fails
  closed on missing glass only when the require-liquid marker exists, which is
  gitignored and absent from the installed tree (verified). Paused or crashed
  glass plus loaded guard starts a session with no pill, the original symptom
  returning silently with a successful session.
- R4 (Medium-high): guard_reply misdiagnoses truncated JSON as a missing
  backend. Verified on the VM: a truncated '{"ok": true, ...' reply yields
  "backend may not be loaded" plus the activation remedy, which then fails
  confusingly because setup_baseline rejects an inventory already containing
  hyprglass.
- R5 (Medium): drain thread dies silently on non-UTF8 stderr. Verified with a
  test program: one 0xff byte raises UnicodeDecodeError (a ValueError subclass),
  the except (OSError, ValueError) swallows it, the deque stays empty, and the
  real cause is lost, making the error opaque again.
- R6 (Medium): no drain settle before composing the detail. No wait or join
  before reading the deque, and guard.stderr.close() in finally can discard
  buffered lines. Exact-pattern simulation: 0 empty in 300 trials; variant:
  1 partial in 200, so the window is small but real.
- R7 (Medium): deque maxlen 32 plus detail[-1200:] can drop the root cause.
  Guardian finally cleanup lines are appended after the root traceback and can
  push it out of the window.
- R8 (Medium): second gate and mid-session guard death still opaque. driver
  registration failed carries no detail; mid-session guard death ends with
  outcome 1 and no message. Same bug class as gate 1, unfixed at gates 2 and 3.
- R9 (Medium): root-cause claim overstates proof. Only the profile mismatch was
  proven to throw. The old library d086bc43 (verified self-consistent, hash
  matches name) was never shown to pass liquid_available; the old pin 674441ea
  matches no known optics version and its origin is unexplained.
- R10 (Low-medium): 30-second fresh-login gate is single-shot with no retry.
  A slow boot past 30s leaves plugins unloaded for the whole login, silently.
- R11 (Low): no redaction in the supervise tail or guard_reply echo, unlike
  visuals.py _loader_log. A truncated busy reply can carry a partial token;
  tee writes raw stderr unsanitized.
- R12 (Low): test_cursor_session.py does not compile on VM Python 3.12
  (SyntaxError, too many statically nested blocks, line 570), so the new
  Lifecycle test was only run on the laptop and could not be independently
  re-run here.
- R13 (Low): lock message misleads when activation holds owner_lock ("another
  automation session is active").
- Required fixes, in order: R1 login-time loader-failure detection plus manifest
  check in sync/setup; R2 durable repair via commit/rebase and scripted re-pin;
  R3 session gate on hyprglass active (or publish require-liquid); R4
  distinguish truncated JSON from missing backend; R5 errors='replace' on the
  drain pipe; R6 join drain thread before composing detail; R7 larger
  deque/tail; R8 name the cause at registration and mid-session death; R9 close
  the d086bc43 and 674441ea gaps; R10 retry or report a missed 30s window; R11
  redact 32-hex tokens; R12 make the session tests compile on VM Python 3.12;
  R13 correct the lock message.
- Redteam note on plan B: the live activation may proceed as the correct remedy,
  but positive proof must include a hyprglass-active check (R3), not only
  cu-cursor status and the socket. Do not declare the fix complete until R1
  through R5 are fixed.

## 22:46-22:48 - Owner orders: optimal method, log everything, Lauren Tan, no cut steps
- 22:46-22:47: owner order (OPTIMAL METHOD + LOG EVERYTHING): too many errors,
  stop working sloppily (wastes time); gather ALL agents, each agent spawns
  many crawlers + council + redteam to argue, find the ONE MOST OPTIMAL FIX
  METHOD for the whole pile of errors. Log TIME AND EVENTS, NOTHING OMITTED
  (append continuously as you work, never batch at the end), so when the owner
  asks, never say "I don't know". Worker OPT (coordinator) spawned; all 6
  running workers told to log continuously.
- 22:48: owner order (LAUREN TAN, KHONG CAT BUOC): continue, follow the Lauren
  Tan structure, stick to it tightly, DO NOT cut steps or it produces garbage
  code. Owner is going to sleep; work overnight, do not stop, do not disturb;
  report results in the morning. OPT told: the optimal method must follow the
  Lauren Tan structure exactly (evidence contract, council + redteam, small and
  many commits, generator never runs its own tests, kill rules, continuous
  logging), no shortcuts.
- F1 note: this task already follows that structure (evidence contract, council
  1/2/3 + redteam, small commits, generator F1 does not run its own tests as
  the judge, continuous logging from 22:47:53). The OPT coordinator is a
  separate fleet effort for the whole error pile; F1 continues its assigned
  guardian fix inside it.

## 22:48-22:49 - Read council 1 + redteam verdict files, verify A5 claim
- 22:48: read improvements/worker-f1-council-1.md in full (AMEND, A1-A6 + F1-F9).
- 22:49: read improvements/worker-f1-redteam.md in full (AMEND, R1-R13, dated
  about 22:50 +07).
- Both verdicts verified as real files in the VM repo, uncommitted, 0 em/en
  dashes claimed. Council 1 verified the root-cause chain live at every layer
  except the A5 detail. Redteam verified the drift repair on disk and the
  d086bc43 library file exists and hashes to its own name.
- A5 (council 1) + R9 (redteam) correction pending verification: the old pin
  674441ea is claimed to match commit d27ad0a (blur 0.10 bottle candidate),
  meaning the drift was optics from 09a8df7 (blur 0.0) vs a manifest pin from
  d27ad0a (blur 0.10), two different stale commits, both stale against b2afcd1
  (blur 0.15). F1 to verify `git show d27ad0a:native/hyprglass-local-optics.lua
  | sha256sum` in the VM repo before correcting the log. If it matches, the
  log Layer 4 line "674441ea matches no known optics version" is wrong and
  must be corrected to the two-stale-commits story. The repair itself stays
  correct either way.
- Adjudication (deferred until council 3 lands): A1/R6 drain race (wait for
  guardian exit + join drain thread), A2/R8 registration + mid-session death
  naming, A3/R5 UnicodeDecodeError + errors='replace', A4 exact envelope
  assertion in the Lifecycle test, R3 session gate on hyprglass active,
  R4 truncated JSON vs missing backend, R7 larger deque/tail, R11 32-hex
  redaction, R12 test file compile on VM 3.12, R1/R2/A6 durability follow-up
  (re-pin check in sync/setup, loader-failure visibility), R10 30s gate retry
  or report, R13 lock message. Redteam: do not declare the fix complete until
  R1-R5 are fixed.
- Council 3 still running at 22:49. Live activation stays gated.

## 22:50 - A5 verified and log corrected
- 22:50: verified council 1 A5 in the VM repo: `git show
  d27ad0a:native/hyprglass-local-optics.lua | sha256sum` =
  674441ea1b7d27f347aa8e31224ac5a8fcd923fc22ae75e65a0936ad8acc17c9, EXACTLY the
  old laptop manifest pin. `git log --oneline -1 d27ad0a` = "fix(glass): bottle
  candidate at refrPx 9.35px (DEPTH_DP 11.0), blur 0.10". The next optics
  commit on that path is b2afcd1 (blur 0.15). A5 CONFIRMED.
- 22:50: corrected the two wrong lines in this log (Layer 4, line ~108, and the
  council-2 notes section, line ~326): the pin is d27ad0a, the drift was two
  stale commits (optics 09a8df7 blur 0.0 vs pin d27ad0a blur 0.10), both stale
  against b2afcd1 blur 0.15. The repair itself is unchanged and still correct.
  R9's d086bc43 part: the old library was verified self-consistent (hash
  matches name) but was never shown to pass liquid_available; that gap is
  recorded, not claimed fixed.
- Next: commit the two verdict files + this log update (3 small commits),
  then adjudicate all four verdicts once council 3 lands and implement the
  AMEND code fixes (A1-A4, R3-R8, R11, R12) with re-tests.

## 22:51 - Verdict files + log committed and pushed (3 commits)
- 22:51: committed council-1 verdict (2acbb67, 216 insertions), redteam
  verdict (88aeef2, 222 insertions), log update (218b223, 196 insertions,
  5 deletions). Pushed: remote todolist-push a230ac3..218b223, ls-remote
  confirms HEAD 218b223f2f4f098695a1fccf45266bd8450d09eb.
- 22:51: dash check (python3, exact U+2014/U+2013 count): council-1 0/0,
  redteam 0/0, log 0/0. The earlier shell grep counts (163/166/464) were a
  quoting artifact ($'...' not interpreted, bracket matched digits), not real
  dashes.
- 22:51: council-3.md exists on disk (201 lines, header shows Verdict: AMEND,
  role tests and user-visible behavior) but its completion handoff has NOT
  arrived yet and the agent is still listed running, so it was NOT committed.
  Commit it only after the handoff confirms delivery.
- Next: adjudicate all four verdicts once council 3 lands, then implement the
  AMEND code fixes (A1-A4, R3-R8, R11, R12) with re-tests, then the live
  activation gated on F3 sign-off.

## 22:52 - Council 3 verdict read (AMEND) + full adjudication of all four verdicts
- 22:52: read improvements/worker-f1-council-3.md in full (201 lines, verdict
  AMEND, role tests and user-visible behavior). File ends cleanly with a
  bottom line, so it is fully written, but its completion handoff has NOT
  arrived yet and the agent is still listed running, so it is NOT committed
  yet. Commit it when the handoff confirms delivery.
- Council 3 independently re-verified: theme tests 34 OK on VM 5x; session
  tests 34 OK on laptop 30.574s; theme 34 OK on laptop 0.126s; laptop scripts
  match VM by md5 (cursor_session.py 5d6c580a, cursor_theme.py 502a4941);
  neg.out matches the log word for word; test file does not compile on VM
  3.12 (pre-existing, parent fails at line 566 too); no em/en dashes in the
  diff or the four changed files; FAKE status_garbage faithful.
- Council 3 findings C3-1 to C3-8: 1. Lifecycle test does not prove the
  envelope names the cause (same as A4, stronger: parse stdout as JSON,
  assert the error field contains 'not valid JSON' and 'may not be loaded',
  plus assert the bare message never appears alone). 2. The remedy in the
  error message is partly wrong and partly unrunnable (NEW, important):
  activate-glass.py needs a library path + --abi + --profile-sha256,
  activate-cursor-guard.py needs a library path + --abi, visuals.py refuses
  outside the first 30s of fresh login (so re-run visuals.py cannot fix a
  running session, only the next login), and activate-cursor-guard.py refuses
  unless glass is already available (order matters). Required: rewrite the
  remedy to name runnable commands with required arguments and pinned
  values, or point at the log plan B commands, and say plainly the loader
  only runs at next login. 3. Supervise tail race (same as A1/R6). 4. Second
  live failure layer has no test: Guard.__init__ would throw FileNotFoundError
  on the missing socket directory even if check_guard passed; the FAKE always
  provides a guard socket. Required: add one Lifecycle case for the missing
  socket directory, asserting fail closed with the cause named in the
  envelope, or record explicitly in the log that this layer is unproven and
  why the live positive test covers it. 5. Python 3.12 failure gates the new
  test (same as R12). Required: fix the nesting in
  test_cleanup_exceptions_cannot_skip_restore, or split the new Lifecycle
  test into a 3.12-compatible file, or record a pinned minimum Python
  version. 6. 34 OK claim is luck dependent: pre-existing flake in
  test_wrong_token_oversize_framing_and_drop_all_fail_closed (BrokenPipeError
  at cursor_theme.py:148 in the drop case; the test accepts RuntimeError and
  ConnectionResetError but not BrokenPipeError; measured pre-fix 5/50,
  post-fix about 5/95 overall). Required: accept BrokenPipeError in the drop
  case, or make the server close cleanly, then re-run the suite until green
  ten times in a row before quoting a pass count. 7. Duplication: the message
  appears twice by design (stderr via tee + JSON envelope on stdout); the
  log says neg.err was empty in the live run, which does not match the tee
  design, so either the live harness did not capture session stderr or the
  tee line went elsewhere. Not a blocker; the live positive run should record
  both streams separately. 8. The message leads with decoder jargon; lead
  with the cause, keep the raw reply as parenthetical detail.
- Council 3 exact positive proof (5 steps, for plan B after activation):
  plugin list shows hyprglass + computer-use-cursor + hyprbars; cu-cursor
  status returns JSON with active true and the session token; socket dir
  exists; fresh observe during the session with the pill visible (fresh
  observe id, not reused); prove the pill is the session pill (indicator
  pid + state dir token matching the session); stop cleanly, fresh observe,
  pill gone, no stray indicator; start a second time, pill returns; one
  harmless click through the session on an already selected tab row,
  re-checked in a fresh observe first, verified by cursorpos + fresh observe;
  record stdout and stderr separately for the whole run.

### ADJUDICATION (all four verdicts: council 1 AMEND, council 2 AMEND, council 3 AMEND, redteam AMEND)
The fix design and the root-cause chain are proven. No reviewer says the
fix is wrong or must be reverted. Every verdict is AMEND, and the required
items converge on one second round of code fixes, then the live activation.
Items agreed by two or more reviewers (implement in round 2):
- Drain race (A1 = R6 = C3-3): on the startup failure path, wait for the
  guardian to exit, then join the drain thread with a short bounded timeout,
  before composing the detail. Join before closing guard.stderr.
- Registration gate (A2 = R8 part): include the drained tail in 'driver
  registration failed' too.
- Non-UTF8 (A3 = R5): catch UnicodeDecodeError in guard_reply alongside
  JSONDecodeError; open the drain pipe with errors='replace'.
- Envelope assertion (A4 = C3-1): Lifecycle test must parse stdout as JSON
  and assert the error field contains 'not valid JSON' and 'may not be
  loaded', and assert the bare message never appears alone.
- Test file on 3.12 (R12 = C3-5): fix the nesting in
  test_cleanup_exceptions_cannot_skip_restore so the file compiles on VM
  Python 3.12, or split the new Lifecycle test into a 3.12-compatible file.
- A5/R9 log correction: DONE 22:50 (d27ad0a verified, log corrected,
  committed 218b223).
Single-reviewer required items (implement in round 2):
- R3 (High): gate the session on hyprglass active. The guardian must check
  indicator.liquid_available before print('ready') and fail closed naming
  glass, or publish the require-liquid marker so Native fails closed.
  Positive proof must include a hyprglass-active check, not only cu-cursor
  status and the socket.
- R4: guard_reply must distinguish truncated JSON (raw starts with { or [,
  JSON fails: say truncated or corrupt, show the decoder position, do NOT
  prescribe activation) from a missing backend (plainly non-JSON reply such
  as 'unknown request').
- R7: larger deque (32 to 200) and larger tail (1200 chars up), or keep first
  lines and last lines instead of only the last 1200 chars.
- R8: name the cause on mid-session guard death (print the guard death cause
  when guard.poll() is not None mid-session).
- R11: redact 32-hex tokens in the supervise tail and in guard_reply output,
  strip control characters before echoing.
- C3-2: rewrite the remedy in the error message to name runnable commands
  with required arguments and pinned values (or point at the log plan B
  commands), say plainly the loader only runs at next login, and state the
  order (glass before guard). C3-8: lead with the cause, raw reply as
  parenthetical detail.
- C3-4: add one Lifecycle case for a loaded status reply with a missing
  socket directory, asserting fail closed with the cause named in the
  envelope (or record explicitly that this layer is unproven and why the
  live positive test covers it).
- C3-6: accept BrokenPipeError in the drop case of
  test_wrong_token_oversize_framing_and_drop_all_fail_closed, then re-run the
  suite until green ten times in a row before quoting a pass count.
- F2 (council 1): session_remote.py wraps the named error in a generic
  BrokerError; include str(error) in the BrokerError message.
- R13: correct the lock message when activation holds owner_lock.
- C3-7: live positive run records stdout and stderr separately (settles the
  duplication question).
Tracked follow-ups (named here, land separately, not blockers for round 2
code but required before the fix is declared complete):
- A6/R1/R2: recurrence. Make setup or sync re-pin the repo manifest and
  optics together with the installed copies on every optics change, or make
  the loader refuse to run with a stale pin at setup time; run
  check-visuals-manifest.py inside sync-installed.py and setup.py on every
  sync; add a post-login self-check so a loader failure is noticed at login,
  not at first use; make the drift repair durable (move the laptop repo
  forward to a commit containing the blur 0.15 optics, or commit the optics
  change, and re-pin through refresh-visuals-manifest.py).
- R10: 30-second fresh-login gate is single-shot; retry the loader once after
  a short delay, or add the post-login check so a missed window is noticed
  immediately.
- F3/F6: mid-run guardian death is silent (covered by R8); pre-existing second
  wait without a timeout in the finally block (note only, pre-existing).
- F1 (council 1): guard_reply mislabels any non-JSON reply as a missing
  backend; covered by R4 (name the missing backend only when the reply is
  exactly 'unknown request').
- F4/F5: restore swallows the named error by design (acceptable); first_action.py
  still matches (verified by reading, no fallback regression).
Plan: round 2 code fixes in the VM repo, re-run theme tests on the VM (10x
green per C3-6) and session tests on the laptop, re-run the live negative
test, commit each increment, then the live activation (plan B) gated on F3
sign-off and the council-2 preconditions, then the positive proof per
council 3 (5 steps, stdout and stderr recorded separately).

## 22:49 - Owner order: commit EVEN MORE and EVEN SMALLER (240 target)
- 22:49: owner order: GitHub graph now has 136 contributions, need to reach
  240 before end of day. Commit EVEN MORE and EVEN SMALLER: every small step
  is its own commit, push immediately when done, do not accumulate. Apply
  immediately to my work.
- F1 note: the 136 is the GitHub graph contribution count (the earlier 189
  commits + 1 PR = 190 was the todolist-push commit count). The target is
  the same: 240 before 24:00. Round 2 (the AMEND fixes) will be sliced into
  many tiny commits, one per fix step, each pushed immediately with
  ls-remote verification, instead of one big fix commit.
- Round 2 slice plan (each line = one commit + push):
  1. guard_reply catches UnicodeDecodeError (A3).
  2. guard_reply distinguishes truncated JSON from missing backend (R4).
  3. guard_reply remedy rewrite: runnable commands with required arguments
     and pinned values, loader only at next login, glass before guard
     (C3-2), and lead with the cause (C3-8).
  4. Redaction helper: 32-hex tokens + control chars stripped in guard_reply
     and the supervise tail (R11).
  5. Drain pipe errors='replace' (R5).
  6. Deque maxlen 32 to 200, tail 1200 chars up (R7).
  7. Drain settle: wait for guardian exit + join drain thread before
     composing the detail (A1/R6/C3-3).
  8. Registration gate includes the drained tail (A2/R8 part 1).
  9. Mid-session guard death prints the cause (R8 part 2).
  10. Hyprglass gate: guardian checks indicator.liquid_available before
      print('ready'), fail closed naming glass (R3).
  11. session_remote.py BrokerError includes str(error) (F2).
  12. Lock message corrected when activation holds owner_lock (R13).
  13. Lifecycle test asserts the exact envelope in stdout as JSON (A4/C3-1).
  14. Lifecycle case for a loaded status reply with a missing socket
      directory (C3-4).
  15. BrokenPipeError accepted in the drop case (C3-6).
  16. Test file nesting fixed so it compiles on VM Python 3.12 (R12/C3-5).
  17. Re-run theme tests on the VM 10x green + session tests on the laptop,
      re-run the live negative test, log the evidence.
- Council-3.md still uncommitted (handoff not arrived yet); commit it the
  moment its handoff confirms delivery.

## 22:49-22:51 - Owner correction: graph counts main branch, UTC day, not todolist-push
- 22:49-22:51: owner correction: the GitHub graph only has 136 contributions
  on 21/11 (tooltip), not 190 as counted. The 190 count used the wrong time
  window: 190 was the +07 day (re-counted 22:51 as 201 commits + 1 PR), the
  graph counts by UTC day (144 commits + 1 PR = 145 at 22:51). The graph only
  counts commits on the DEFAULT branch (main); todolist-push has 290 commits
  on UTC 21/11 but they do NOT count. Worker MERGE spawned to merge
  todolist-push into main to push the graph count past 240.
- F1 correction to my 22:49 log entry: the "190 was the todolist-push commit
  count" line was wrong. 190 was the +07-day count. My todolist-push commits
  do not count toward the graph until MERGE merges them into main. I keep
  committing small on todolist-push (that is what MERGE will merge); I do NOT
  merge to main myself, MERGE owns that.
- 22:50-22:51: tab state changed again. Restarting Zen restored the 39
  fixture tabs (owner's 22:50 screenshot); F3 is re-running the FULL cleanup
  with the same keep-list (28 real tabs). The live slot is busy with F3's
  cleanup. F1 does NO live driving in this round; round 2 is code fixes plus
  VM and laptop tests only. The live activation and positive proof wait for
  F3 to finish the cleanup and sign off, and the proof click coordinates must
  be re-read from a fresh observe at that time.

## 22:53 - Round 2 commit A: guard_reply rewrite (A3 + R4 + C3-2 + C3-8 + R11)
- 22:53: rewrote scripts/cursor_theme.py guard_reply. Catches
  (json.JSONDecodeError, UnicodeDecodeError) (A3, council 1 verified the
  non-UTF8 socket bypass live). Distinguishes truncated or corrupt JSON
  (reply starts with { or [, decoder position included when available) from
  a missing backend (R4); the truncated case says the backend may still be
  loaded and prescribes no activation. The message now leads with the cause
  (C3-8) and the remedy names runnable commands with required arguments and
  where the pinned values live (native/visuals.json library/abi/
  profile_sha256), points at this log plan B for the exact commands, states
  the order (glass first, then guard), and says plainly the fresh-login
  loader only runs at the next login and cannot fix a running session (C3-2).
  Added redact_text (R11): 32-hex tokens become [redacted], control
  characters stripped, applied to the shown reply.
- 22:53: updated tests/test_cursor_theme.py. The existing missing-backend
  test regex now matches the new word order ('may not be loaded' before
  'not valid JSON'). Added
  test_guard_reply_distinguishes_truncated_json_non_utf8_and_redacts_tokens:
  truncated JSON says 'truncated or corrupt JSON' and never 'may not be
  loaded'; non-UTF8 bytes get the named error, not a raw UnicodeDecodeError;
  a 32-hex token in the reply is redacted, never echoed.
- 22:53: VM test evidence: python3 -m unittest tests.test_cursor_theme,
  35 tests OK in 0.245s (34 + 1 new). Run once; the 10x green re-run per
  C3-6 comes after the drop-case flake fix.

## 22:54-22:55 - Round 2 commit B1: drain pipe errors='replace', deque 200, tail 4000 (R5 + R7)
- 22:54: edited scripts/cursor_session.py supervise. Popen now passes
  errors='replace' (R5), so one non-UTF8 byte on guardian stderr no longer
  kills the drain thread and loses the tail. guard_errors deque maxlen 32 to
  200 and the startup tail cut 1200 to 4000 chars (R7), so a long traceback
  plus finally cleanup lines no longer push the root cause out of the window.
- 22:54: R5 probe evidence (/tmp/f1-r5-probe.py, VM python 3.12). A child
  writing b'cause: \xff\n' to stderr: with errors=None the reader raises
  UnicodeDecodeError and the tail is lost; with errors='replace' the line is
  delivered as 'cause: U+FFFD'. The first probe attempt was inconclusive
  (shell quoting ate the child code, the child printed a traceback instead);
  the second probe, written to a file to avoid quoting, proves the fix.
  py_compile scripts/cursor_session.py OK. grep confirms the three lines
  (228 errors='replace', 237 maxlen=200, 250 detail[-4000:]).
- 22:55: owner note (fleet, not F1): clone2-watch cron set up (15m). If
  clone2 is silent over 15m, Muse checks workspace 2, approves what it needs
  or prompts it to keep working, then switches back to workspace 1. Approve
  or nudge only for clone2 work, never money, data deletion, or PII. No
  effect on F1; F1 does no live driving in this round.

## 22:56-22:57 - Round 2 commit B2: drain settle before reading the tail (A1/R6/C3-3 + A2/R8)
- 22:56: edited scripts/cursor_session.py supervise. Added _settle_drain():
  wait for the guardian to exit (0.5s), then join the drain thread (0.5s),
  before the tail is read. Called at both failure gates: the startup gate
  (A1/R6/C3-3, the exact race fix D exists to remove) and the driver
  registration gate, which now includes the drained tail in the error
  instead of the bare 'driver registration failed' (A2/R8 part 1). The
  drain thread is now kept in a named variable (drain_thread) instead of
  an anonymous thread.
- 22:56: laptop evidence. scp of the new cursor_session.py to
  /tmp/f1-test/scripts/ OK, md5 1687ffa8624c35b770a671252fc891e0. Session
  tests run detached (SSH dies ~30s): 34 tests OK in 29.698s
  (/tmp/f1-test/b2.log), no unittest process left running. py_compile on the
  VM OK before that. grep confirms _settle_drain at lines 248, 258, 270.
- 22:56: push-race lesson from B1. The B1 push printed "remote rejected
  (cannot lock ref, is at 22c3b35 but expected 9b8ddc4b)" yet the commit
  LANDED: verified three ways (git branch -r --contains 5b11696 shows
  origin/todolist-push; merge-base --is-ancestor 5b11696 origin/todolist-push
  says YES; git log shows it in the range). The shared branch moves fast
  and a push can report a transient lock rejection while the commit still
  lands. Ground truth is ls-remote + branch --contains + merge-base, not
  the push exit message. After a fetch + fast-forward merge, local HEAD
  and remote HEAD are both a96b47c (OPT-WEB S13).
- 22:57: fleet notes (not F1). Y13r2 DONE, verdict BLOCK: 4 new blockers
  (B1 .pyc forge via -m/import, B2 stdlib shadowing 9/15 names, B3
  tokenizer missing -m/flag/renames, B4 -m breaks ship) + 5 amends; Y13g
  spawned to fix per the redteam paper, then a new re-review. The VM
  python re/__init__.py deletion cause is SOLVED: it was the Redteam Y13r2
  self-deleting shim (A6e) deleting the wrong file (globals().update
  overwrote __file__ before os.remove), NOT a stray process. VMFIX restored
  it durably (c16dd4e). So the "VM python deletion cause still unknown"
  item in F1's final report is now resolved. H3 gate: accept Y13r2's
  proposal (5a2b69d NO VERDICT + runner-quiet/ports check is enough as the
  done marker leg, keep the gate text, Y6 retry after Y13). No effect on
  F1's code fixes; the live queue is further backed up.

## 22:58-23:01 - Round 2 commit B3: mid-session guard death names the cause, tail redacted (R8 + R11)
- 22:58: edited scripts/cursor_session.py supervise. Added _tail(): the
  drained tail passed through cursor_theme.redact_text (32-hex tokens become
  [redacted], control characters stripped) and truncated to 4000 chars, used
  by both failure gates (R11, uniform instead of the raw detail). Split the
  mid-session loop: a guard death (guard.poll() is not None) now settles the
  drain, prints 'session guardian died mid-session: <tail>' to stderr, and
  terminates the driver; the cancel latch and stop file keep their old
  silent path (R8 part 2). The import is the existing lazy pattern
  (import cursor_theme inside supervise); cursor_theme does not import
  cursor_session, so there is no cycle.
- 22:58: laptop evidence. scp OK, md5 edee3bc45f7e07a5c8d943bfadcf4bef.
  The scp+launch command exited 255 with 'client_loop: send disconnect:
  Broken pipe' (the known SSH-die-after-~30s), but the LAUNCHED marker was
  printed, so the detached test started. Session tests: 34 tests OK in
  30.337s (/tmp/f1-test/b3.log), no unittest process left. py_compile on the
  VM OK before that.
- 22:58: the mid-session death message path itself has no unit test (it
  needs a guardian that dies mid-session, which the FAKE does not do); it is
  covered by the 34-test no-regression run and by code review. The live
  positive proof will exercise the session lifecycle end to end.
- 23:01: owner note (fleet, applies all night): the user is going to sleep, but
  any error or anything that really needs the user should still be reported at
  once, not held until morning. Big errors, blockers, and things needing
  the user's decision get reported immediately; routine work runs silently and is
  reported in the morning. F1 has no blocker right now; if the live
  activation hits one, it goes to the parent at once.

## 23:05-23:24 - Round 2 commit C: hyprglass gate (R3) + FAKE + tests, via a regression and its diagnosis
- 23:05: owner note (fleet): MERGE DONE, graph 456, target 240 EXCEEDED.
  main HEAD 5c94e6c (merge 0ac4311 todolist-push 313 commits + 0c473f9),
  3 conflicts kept both sides, suite 1618 tests: 3 fail + 5 error (all
  pre-existing at baseline, 0 regression, +124 tests). Graph UTC 21/11:
  455 commits + 1 PR = 456. The commit-count pressure is off; small
  commits continue as good practice, and MERGE will pick them up.
- 23:05: owner note (deferred, low): Zen keybinds. Worker KB is gathering
  all keybinds (Omarchy + Hyprland + Zen) and integrating them into the
  computer-use board ON THE MACHINE (local-only, not pushed to the repo).
  The owner asked why the watch fumbled when the Omarchy skill has it all;
  the answer: skill_search 'omarchy' returns 0 results, there is no
  Omarchy skill in the catalog; the keybinds live in the Hyprland/Omarchy
  config on the machine, not in a skill. Not F1 work.
- 23:14: fleet note: F3 DONE, slot re-wedged 22:56:12. Marionette root cause
  proven from source (driver.sys.mjs #registerWindow 4639 passes null into
  #registerBrowser 4616); restart 22:36 fixed it (session 0.1s); cleanup
  redo 22:54-22:56 closed 55 tabs, 14 real tabs left, 0 fixture tabs.
  J21 = F3's click (the app-launcher button, not workspace 1). Slot
  re-wedged, zombie NOT proven, council 3x AMEND + redteam BLOCK (B7: 4
  close methods not yet tried). Restart 2 approved (F3b, baseline first,
  right-click Close Tab first, then Arms A/B/C). Live Y13/Y14 blocked
  tonight. F1's live activation needs a healthy slot for the proof click,
  so it waits on F3b. AGENTS.md 23:19 records the proven workspace command:
  hyprctl dispatch "hl.dsp.focus({ workspace = 2 })" switches in ~1s.
- 23:16: fleet note: OPT DONE. The single optimal fix method is at
  improvements/optimal-fix-method-20261121.md (202 lines, 6 commits,
  verified). Order: F3 slot-health > F1+F2 > ZT-B > Y6 pill > Y13 live >
  Y14 live > A1 > hidden-body > clone2 heavy > Y1b > scrub > final test
  LAST. OPT said Y13g had 0 output (WRONG in part: the log
  worker-y13g-fix-log.md EXISTS, just no commit yet; Y13g still active).
  Clone2-watch MISS 23:16: the owner did not see Muse switch workspace to
  approve, so the user switched. Cause: the cron run 23:11:56 was STILL
  RUNNING (5+ minutes, no log, no result), so no workspace switch happened.
  Fix: stop the stuck run, check ws2 at once per the owner's order. Not F1.

### C3 regression, diagnosis, and fix (23:04-23:24)
- 23:04: first full run of the R3 gate + FAKE (c3.log) FAILED badly: many
  F/E in the progress line, run still going after 90s (normal ~30s). I
  killed it with pkill (too early, losing the failure summary; lesson: let
  a failing run finish and read its summary instead of killing it).
- 23:06: single-test run (c3-single.log) gave the first real clue: the
  envelope error was "module 'cursor_theme' has no attribute
  'redact_text'". Cause: /tmp/f1-test/scripts/cursor_theme.py was STALE
  (md5 502a4941, the 5033c9d version, grep 0 for redact_text). I had scp'd
  cursor_session.py and test_cursor_session.py after Commit A but never
  cursor_theme.py, so the test runtime lacked redact_text, which B3's
  _tail() calls. Lesson: when a fix touches a helper (redact_text in
  cursor_theme.py), deploy ALL the files it touches to the test bundle,
  not just the file under test. Fixed by scp'ing cursor_theme.py (grep 1).
- 23:07: re-ran the single test (c3-single2.log). New error, the real one:
  "session guardian startup failed: another automation session is active"
  plus "session recovery ownership changed; current owner must restore".
  The first subtest TIMED OUT at 8s (the session hung), leaving its
  guardian holding the lock, so the second subtest failed on the lock.
  The hang was reproducible (c3-single3.log, same 13.216s, same errors).
- 23:08-23:12: diagnosis. The FAKE hyprglass branch is FAST (0.016s per
  call, rc 0, valid JSON, proven on the laptop), so the gate itself was not
  slow. A ps snapshot caught the orphaned guardian (PID 470001, parent 1)
  from the timed-out first subtest, still running. I added a faulthandler
  timeout to the LAPTOP copy only (via a patch script file, after an inline
  python -c mangled the quotes and broke the file; the file was restored
  by re-scp). The faulthandler dump (c3-diag2.log) proved the hang:
  the guardian was stuck in indicator.Native.__init__ (line 73) calling
  activation_checks.wait_for_profile (line 27, and line 14 in check_output
  waiting in select). Root cause: Native.__init__ calls wait_for_profile
  (30s timeout) whenever _valid_liquid is True. Before my FAKE change,
  _valid_liquid was False in the test env (hyprglass status exited 1), so
  wait_for_profile was never called. My FAKE made _valid_liquid True, so
  Native now called wait_for_profile, which polls `hyprctl configerrors`
  and requires it to return empty before it even checks liquid_available.
  The FAKE did not handle `configerrors`, so check_output raised
  CalledProcessError every iteration, the loop ran the full 30s, and the
  test timed out at 8s. The R3 gate (placed AFTER Native) was never even
  reached. Two defects, one root: the gate was after Native, and the FAKE
  lacked configerrors.
- 23:12: fix. (1) Moved the R3 gate BEFORE indicator.Native (right after
  cursor_theme.apply), so a down or warming-up backend fails fast with a
  named cause instead of hanging 30s in wait_for_profile. (2) Added a
  `configerrors` branch to the FAKE (returns empty, rc 0), so
  wait_for_profile returns fast when the backend is ready. Verified on
  the VM: FAKE compiles, configerrors rc 0 empty, hyprglass status rc 0
  valid JSON; py_compile cursor_session.py OK.
- 23:13: re-ran the full suite (c3b.log): 35 tests in 32.603s, FAILED
  (2 failures + 3 errors), no hang. The 2 R3-test failures: my assertion
  released()==[] was wrong, the guard lease is created BEFORE the gate, so
  cleanup releases it and the list holds the token (glass_down: 1 token,
  glass_pending: 2, accumulated across subtests). The 3 cleanup-test
  errors: the R3 gate calls indicator.liquid_available, which spawns a
  subprocess, but that test patches session.os.read globally, which breaks
  subprocess communication, so liquid_available returned False and the
  gate raised. That test already stubs every guardian dependency (Native,
  listen, check_guard, apply, snapshot, hotkey, signal, select, os.read,
  restore); it needed liquid_available stubbed too.
- 23:14: fix. (1) R3 test: assert released() grows by exactly 1 per
  subtest (before+1), proving the lease is released, not leaked, on the
  failure path. (2) Cleanup test: patch indicator.liquid_available to
  return True. BUT adding a third manager to the inner with pushed the
  file over the compiler static-nesting limit even on Python 3.14
  (SyntaxError at line 590). That is the R12/C3-5 defect biting again.
- 23:15: fix. Refactored test_cleanup_exceptions_cannot_skip_restore to
  use contextlib.ExitStack (sequential enter_context calls, no giant
  nested with), including the liquid_available stub with a comment. This
  ALSO fixes R12/C3-5: the file now compiles on VM Python 3.12.3
  (py_compile OK), where it previously failed at line 566/570.
- 23:16: re-ran the full suite (c3d.log): 35 tests in 32.212s, OK. All
  green. The R3 gate, the FAKE branches, the R3 test, and the cleanup
  test refactor are all proven on the laptop (Python 3.14.10).

## 23:24-23:32 - Round 2 D1/D2/E1/E2/E3: remaining review fixes, each its own commit
- D1 (F2, session_remote.py:323-326): the BrokerError message 'cursor
  backend is not idle and ready' swallowed the check_guard detail, which
  now names the missing backend. The message now carries str(error):
  f'cursor backend is not idle and ready: {error}'. No test asserted the
  exact old message (only a stale .pyc matched the grep).
- D2 (R13, cursor_session.py:80 + test_sync_installed.py:229): the lock
  message now reads 'another automation session or plugin activation is
  active', because the lock is also held by plugin activation (the
  lock-holding wrapper), not only by a running session. The sync-installed
  test assertion was updated to the new string; test_visuals.py uses the
  regex 'another automation', which still matches.
- E1 (A4/C3-1, test_unloaded_backend): the Lifecycle test now parses
  stdout as JSON and asserts the error field contains 'not valid JSON'
  and 'may not be loaded', and is not the bare 'session guardian startup
  failed'. The old combined out+err assertion would pass even if
  supervise raised the old bare error, because the text also arrives via
  the guardian stderr tee.
- E2 (C3-4, cursor_theme.py Guard.__init__ + new Lifecycle test): the
  missing-socket layer is now PROVEN, not recorded as unproven. Guard
  now catches FileNotFoundError from directory.lstat() and path.lstat()
  and raises a named RuntimeError ('cursor guard socket directory is
  missing' / 'cursor guard socket is missing', with the reload remedy),
  instead of surfacing a raw ENOENT. New test
  test_missing_guard_socket_fails_closed_and_names_the_cause removes the
  socket directory after setUp (check_guard still passes, the FAKE
  reports the backend idle and ready), launches, and asserts fail closed
  with 'cursor guard socket' in the envelope. The GuardServer keeps its
  bound socket on the unlinked inode; tearDown tolerates the unlink.
- E3 (C3-6, test_cursor_theme.py): the drop case now accepts
  BrokenPipeError alongside RuntimeError and ConnectionResetError (the
  pre-existing flake, about 5/95 runs, a write racing the close). The
  missing-socket case in test_private_directory_and_socket_are_required
  now asserts the named RuntimeError ('cursor guard socket is missing')
  instead of OSError, matching the E2 code fix.
- E4 (R12/C3-5): DONE in commit a152f31 (ExitStack refactor). The test
  file compiles on VM Python 3.12.3, where it previously failed at line
  566/570.
- VM evidence 23:32: theme tests 35 OK in 0.181s; py_compile OK for
  session_remote.py, cursor_session.py, cursor_theme.py,
  test_cursor_session.py, test_cursor_theme.py, test_sync_installed.py.

## 23:33-23:36 - Re-verification of round 2 (D1/D2/E1/E2/E3 + C): all green
- VM theme tests: 10 runs in a row, all OK (C3-6 requirement met).
  Each run 35 tests. Before the 10x, one run showed 35 OK in 0.181s.
- Laptop: deployed the 5 changed files to /tmp/f1-test (scp, md5s
  9208afee cursor_session.py, 3bf3d391 cursor_theme.py, ea1da781
  session_remote.py, 7611a2b6 test_cursor_session.py, 8449e774
  test_cursor_theme.py) and ran the session + theme suites together:
  71 tests in 34.575s, OK (e-verify.log). That is 36 session tests
  (35 + the new E2 missing-socket test) + 35 theme tests. The E1
  envelope assertion, the E2 missing-socket naming + test, and the E3
  BrokenPipeError acceptance are all proven live on the laptop.
- Fleet note 23:33 (KB DONE): Worker KB finished. No Omarchy skill
  exists (independent search 0 results). The cause of the workspace
  fumbling: fastest-paths.md on the machine had the WRONG workspace
  command (string dispatcher `hyprctl dispatch workspace N`, proven
  broken live 23:32 rc=7); the correct command is hl.dsp.focus, proven
  23:19. KB integrated 250 Omarchy/Hyprland binds + 85 Zen into the
  on-machine computer-use build (keybinds.md + keybinds.json,
  local-only); fastest-paths fixed 6 broken lines; the repo gained
  scripts/hypr_cmd.py + tests 13/13 OK (commit 9e9b811). Still unproven:
  move-to-workspace, absolute resize, {omarchy/panel/ipc/menu} table
  forms (keypress-only), Zen has no CLI. Not F1 work, but the
  hl.dsp.focus command is now the proven workspace move for the live
  activation (council-2 precondition 6).

## 23:35-23:36 - Live negative test, round 2 (PROVES the new message live)
- Fresh observe 23:35:21 id 50cf368e61ea (capture 30.184ms, Zen window
  0x557052b62dd0, title "Example Domain - Zen Browser", region
  [2509,914,1863,1176], monitor eDP-2). Ran the exact original failing
  command: `computer-use session -- computer-use act --observation
  50cf368e61ea --actions '[{"type":"click","x":135,"y":272}]'`.
  Result RC=1 in 0.220s.
- stdout (JSON envelope): {"ok": false, "error": "session guardian
  startup failed: cursor backend may not be loaded (guard reply is not
  valid JSON, got: unknown request); load glass first, then the guard:
  scripts/activate-glass.py <library> --abi <abi> --profile-sha256
  <profile-sha256> and scripts/activate-cursor-guard.py <library> --abi
  <abi>, with the pinned values from native/visuals.json (library, abi,
  profile_sha256); see improvements/worker-f1-guardian-fix-log.md plan B
  for the exact commands. The fresh-login loader scripts/visuals.py only
  runs at the next login, it cannot fix a running session."}
- stderr: the same message, via the guardian stderr tee (as designed).
  C3-7 is settled: the tee DOES write to stderr. The 22:39 run's empty
  neg.err was a capture artifact of that run's harness, not the tee
  failing. This run recorded stdout and stderr separately
  (/tmp/f1-neg2.out, /tmp/f1-neg2.err on the laptop).
- The message now leads with the cause (C3-8), names runnable commands
  with required arguments and where the pinned values live (C3-2), states
  the order (glass first, then guard), and says plainly the loader only
  runs at the next login. The failure is at check_guard (the guard reply),
  which runs before the R3 gate, so the gate is not reached until the
  guard plugin is loaded. That ordering is correct.
- Round-2 scripts are deployed to the installed tree (md5-verified):
  cursor_session.py 9208afee, cursor_theme.py 3bf3d391,
  session_remote.py ea1da781, matching the VM repo exactly.

## 23:36-23:44 - Lock-holding wrapper (council-2 precondition 4)
- Built scripts/activate-session-backend.py. It holds
  cursor_session.owner_lock() across the whole glass + guard sequence
  (activate-glass.py takes no lock on its own, so two concurrent runs
  could both pass the pre-load check; the guard CLI holds the lock only
  for its own step). The pinned values come from native/visuals.json
  (library, cursor_guard_library, abi, profile_sha256) unless overridden
  on the command line. After both loads it verifies: the plugin list
  shows hyprglass + computer-use-cursor, cu-cursor status answers, and
  hyprglass is ready (liquid_available ready=True). Glass runs first,
  then the guard, in that order; a glass failure skips the guard.
- Tests: tests/test_activate_session_backend.py, 3 tests, all OK on the
  VM (0.003s). The lock-held proof is real: each fake activation tries
  to acquire owner_lock() itself and records that it raised
  'another automation session or plugin activation is active', proving
  the wrapper held the lock during both calls. The test loads the
  hyphenated wrapper module via importlib (a plain import cannot name
  a file with hyphens). A third test proves the lock is released after
  activation, and a glass failure skips the guard.
- The wrapper is the tool for plan B (the live activation). The
  activation itself is NOT run yet: it is gated on council-2
  preconditions 1-8 in order, and precondition 1 needs F3 sign-off and
  a free live slot. The Marionette slot re-wedged 22:56:12 and F3b
  (restart 2) has not reported an outcome yet, so the live activation
  waits. No plugin load is attempted tonight until that gate clears.

## 23:44-23:52 - Durability (R1/R2): the sync ALREADY validates the manifest
- I first added a _check_visuals_manifest step to sync-installed.py
  main(), then REVERTED it: it was redundant. The sync already has
  _validate_manifest (since dbaba59, Nov 16), called from
  _required_staged_files during _sync, which raises SyncError('visuals
  manifest profile_sha256 does not match hyprglass-local-optics.lua')
  on a stale pin. My new step could never add value: if the existing
  check passes, mine passes too; if it fails, _sync raises before mine
  runs. Dead code, removed. Lesson: read the existing validation before
  adding a new one.
- So the F1 drift was NOT a missing-check problem. The check existed
  since Nov 16, before the blur-0.15 drift (Nov 20). The drift happened
  because the repo's manifest and optics drifted WITHOUT a sync being
  run on the laptop repo: the optics file stayed at 09a8df7 (blur 0.0)
  while the manifest pinned d27ad0a (blur 0.10), two different stale
  commits, and no sync ran to catch the mismatch. The b2afcd1 change
  re-pinned the INSTALLED manifest but never the repo manifest. The
  durability gap is therefore the manual re-pin step
  (refresh-visuals-manifest.py) not being run whenever the optics
  change, not a missing sync check. That step stays a tracked
  follow-up: wire the re-pin into the optics-change workflow (or into
  setup.py), and add the post-login self-check (R1) so a loader
  failure is noticed at login, not at first use.
- What I DID land: a regression test in test_sync_installed.py
  (test_stale_visuals_manifest_fails_the_sync) proving the sync fails
  on a stale manifest pin, pinning the pre-existing _validate_manifest
  as a guard. Sync-installed.py itself is unchanged (git diff empty).
  Evidence: 9 sync tests OK in 2.007s on the VM, including the new one.
- The remaining tracked durability items (not done tonight): R10 (the
  30s fresh-login gate is single-shot, no retry; add a retry or a
  post-login check so a missed window is noticed), and the re-pin
  workflow above. The R3 gate, the wrapper, and the loader repair are
  the parts that are done and proven.

## 23:39-23:53 - F1 status: all code work done and proven; live activation GATED on F3b
- F3b status at 23:39: the slot is HEALED (restart step 3, Zen PID
  479395, website-open PASS), Arms A, B, C all PASS (no single factor
  wedges the slot), Arm D LAUNCHED 23:38:48 and still in flight, no
  verdict yet. F3b is actively driving the browser. Council-2
  precondition 1 (F3 sign-off, Zen PID stable, single operator, no
  parallel driving) is NOT met, so the live activation (plan B) does
  NOT run now. The activation is ready: the lock-holding wrapper is
  built, tested, and deployed to the installed tree, the pinned values
  are in native/visuals.json, and the pre-flight + half-state recovery
  + crash contingency are written in council-2. When F3b signs off,
  run: python3 scripts/activate-session-backend.py (installed tree),
  then the positive proof (council-3, 5 steps).
- Everything F1 could do without the live activation is DONE and
  committed (todolist-push, all pushes ls-remote verified):
  root cause (4 layers, proven live), drift repair, round-1 fix
  (guard_reply + supervise tail), round-2 fixes (drain settle, drain
  errors='replace', larger deque/tail, mid-session death naming, R3
  hyprglass gate, FAKE branches, ExitStack refactor fixing the 3.12
  compile, BrokerError cause, lock message, envelope assertion,
  missing-socket naming + test, BrokenPipeError), the lock-holding
  wrapper, and the sync manifest regression test.
- Evidence: VM theme tests 35 OK x10 in a row; laptop session + theme
  71 tests OK in 34.575s; sync tests 9 OK; wrapper tests 3 OK; live
  negative test round 2 (23:35, fresh observe 50cf368e61ea, RC=1 in
  0.220s) shows the new named error with runnable remedy on both
  stdout (JSON envelope) and stderr (tee). The 22:39 negative test
  showed the round-1 message; the 23:35 test shows the round-2 message.
- Reviews: council 1, council 2, council 3, redteam, all AMEND, all
  required items addressed except the two tracked durability
  follow-ups, which are NOT blocking the activation but ARE required
  before the fix is declared complete: R10 (the 30s fresh-login gate
  is single-shot, no retry; add a retry or a post-login check so a
  missed window is noticed) and the re-pin workflow (run
  refresh-visuals-manifest.py whenever the optics change; the sync
  already validates the manifest, so the gap is the manual re-pin
  step, not a missing check).
- F1 commits this session (todolist-push): 392bc09 (A), 5b11696 (B1),
  9b9e0b0 (B2), 26fd1ce (B3), e7913d5 (C1 gate), a152f31 (C2 FAKE +
  tests), a5b3c02 (council 3), cc6bc9a (D1), ceae45d (D2), b3fac91
  (E1/E2/E3), e0f3229 (log), ab67173 (wrapper), 0246a69 (sync
  regression test). Plus the round-1 commits 5033c9d, 708bef0,
  e84e329, f3e32e5, 2acbb67, 88aeef2, 218b223, e52d477, 86c4a01,
  7af9658.

## BATCH 7 CORRECTION, 22/11/2026 (clone2 task 3, violation V1)
- The H3 gate line in this log (line 862, "H3 gate: accept Y13r2's proposal...") cites no acceptance artifact: the acceptance is recorded only as "per MEMORY.md 22:57" in four other places (improvements/opt-council-m2-verdict.md:90 and :107, improvements/opt-crawl-src-20261121.md:148, improvements/optimal-fix-method-20261121.md:198). Checked 22/11/2026: MEMORY.md exists on no branch and never existed in git history on any branch; the proposal commit 5a2b69d itself exists (Y13r2 NO VERDICT run), but no council paper, log entry, or owner message in the repo records who accepted the proposal. The redteam already flagged this (opt-redteam-m-skeptic.md:58 P-33, opt-redteam-m-verdict.md:33,81 AM-13); the method file itself requires the acceptance to be cited in a council paper or log entry, not only MEMORY.md 22:57.
- Corrected status: the H3 gate acceptance is UNVERIFIED from repo evidence. The gate decision must be re-recorded in a council paper or log entry by the coordinator before the Y13 live run treats it as resolved.
- Note: not every MEMORY.md 22:57 citation is equally broken. The re.py deleter claim citing the same entry is independently corroborated in-repo by the VMFIX commit c16dd4e. Only the H3 acceptance lacks any in-repo corroboration.
- W-EVID SOURCE LOCATED, 22/11/2026 (COORD-CLICK-6 item 13, part a): the 22:57 entry survives in the coordinator memory log on this VM, ~/memory/2026-11-21.md:2653 (section "Quyet dinh H3 gate (Muse, sau de xuat Y13r2)") and :2917 (entry 22:57). ~/MEMORY.md itself has no 22:57 H3 entry. The source says Muse (coordinator) accepted the Y13r2 proposal (5a2b69d NO VERDICT + runner-quiet/ports check as the marker leg for this run, gate text unchanged, Y6 retry after Y13; Y6e load test not accepted). No owner message accepts H3 specifically. A draft proposal for the acceptance record is at improvements/w-evidence-h3-draft.md. W-EVID did NOT write the acceptance record; only Muse tong may write it, per AM-13. Full detail: improvements/w-evidence-remaining-log.md.
