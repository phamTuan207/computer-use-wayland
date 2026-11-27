# W-SYNC: laptop tree sync, CB-9 drift (COORD-CLICK-6 item 9)

Worker: W-SYNC. Date: 2026-11-22. All times Asia/Ho_Chi_Minh, wall clock.
Repo: computer-use-wayland, branch todolist-push.
Rule followed: only sync code. No restart of Zen, Brave, Chromium, or any
session of the owner. No tab opened or switched in the user's Zen.

## 1. Repo baseline (VM and laptop at the same commit)

VM checkout, 17:49:29 +07:
- Command: `cd ~/workspace/computer-use-wayland && git fetch origin && git pull --ff-only origin todolist-push`
- Output: `Already up to date.`
- HEAD: `ab7c7a5ec3ce8a81c0fe3cfcc1ac5a1d99db8e06`
- Log top: `ab7c7a5 docs: COORD-CLICK-6 log, resume 17:47, 8 lanes spawned`

Laptop repo, 17:49:55 +07, before pull:
- HEAD was `9ec713c2a6a803c75e41d7e6f99cd335330779ef` (log top `9ec713c C5-STEP9: Zen pointer delegate wiring`).
- Command: `git fetch origin` then `git pull --ff-only origin todolist-push`
- Output: `9ec713c..ab7c7a5 todolist-push -> origin/todolist-push`, then HEAD `ab7c7a5ec3ce8a81c0fe3cfcc1ac5a1d99db8e06`.
- Result: laptop repo now at the same commit as the VM repo, `ab7c7a5`.

Note: the first VM `git pull --ff-only` (no args) failed with
`fatal: Cannot fast-forward to multiple branches.` The explicit
`git pull --ff-only origin todolist-push` worked. VM HEAD is `ab7c7a5`.

## 2. Installed tree before sync: drifted, last sync at 9ec713c

Deploy manifest on the laptop
(`~/.local/share/agent-computer-use/deploy-manifest.json`), read about 17:50 +07:
- `source_commit`: `9ec713c2a6a803c75e41d7e6f99cd335330779ef`
- `synced_wall`: `2026-11-22 15:56:10 +07`
- `managed_files`: 649
- `ledger_path`: `.../releases/20261122-155610-859821-9ec713c2a6.json`

Check, about 17:50 +07:
- Command: `python3 scripts/sync-installed.py --check`
- Output: `sync-installed: error: latest release ledger source identity differs from the current checkout`
- Exit code: 1.

## 3. Drift inventory before sync (full hash loop, about 17:51 +07)

Command (laptop repo `ab7c7a5`, installed root
`~/.local/share/agent-computer-use`):
`git ls-files scripts native skill tests docs README.md LICENSE | while read f; do ... sha256sum repo file vs installed file ...; done`

Result: 54 drift entries, 11 files with different content plus 43 files
missing from the installed tree. Zero extra-file check here, the sync
check below covers extras.

Files with different content (12-char sha256 prefixes, repo vs installed):
- `docs/zen-error-fix-todolist-20261121.md` repo=a4c8d487111e inst=e73e9d510e6c
- `scripts/code_exec.py` repo=f85ee4a77924 inst=070250e8b347
- `scripts/cu.py` repo=6b18f8407dfa inst=83806309f7d5
- `scripts/s2_flip_live.py` repo=6b238e039b21 inst=b38777e59d2a
- `tests/cdp_validation.mjs` repo=5483354b5bc4 inst=b565c687e51d
- `tests/realistic/codex-y5-manifest.json` repo=26c2541ea691 inst=fdb48a38d9b2
- `tests/realistic/codex-y5/SHIPPED.md` repo=e964c6774a7d inst=684ea6fde200
- `tests/realistic/launch_y13.py` repo=4641fdb00a7a inst=04381a967265
- `tests/realistic/regen_codex_y5_manifest.py` repo=2199d575fcc0 inst=78eac1ba114a
- `tests/realistic/run_codex_y5.py` repo=7121a427ba28 inst=93f57ff477cc
- `tests/test_s2_flip_wiring.py` repo=22c3c2951046 inst=094b45ac108e

Files missing from the installed tree (43):
- `scripts/snippets/manifest.json`, `scripts/snippets/two-windows.py` (2)
- `tests/realistic/clone1-batch3/` whole new suite: README.md,
  lib/browser.mjs, lib/server.mjs, results.json, run_all.mjs, plus
  t01-terminal, t02-spreadsheet, t03-video-call, t04-email-client,
  t05-file-manager, t06-calendar, t07-code-editor, t08-settings-panel
  (README.md, check.mjs, fixture.html each), t09-multi-window (README.md,
  check.mjs, detail.html, fixture.html, prefs.html),
  t10-music-player (README.md, check.mjs, fixture.html) (37)
- `tests/test_snippets.py`, `tests/test_y6c5_positive_gate.py`,
  `tests/y1b_phaseb_real_run.py`, `tests/y1b_probes_rewritten.py` (4)

Full hashes of the headline files before sync (about 17:51 +07):
- `scripts/cu.py` repo=`6b18f8407dfa2a3242d7782884e112e6312ac1d00f555cc645c0501521d64c59`
  inst=`83806309f7d58136e3f97ea22406e36694bf54ef653812a4f875c2cb6e8185a1`
- `scripts/first_action.py` repo=inst=`9fee1242b691e8a94bffa61c9e23d0e2004d3eb07c2bf34a405c046b769da07a`
  (already in sync; the 06:40 first_action.py drift was fixed by the 15:56 sync)
- `scripts/code_exec.py` repo=`f85ee4a779241cc68f9abf3d65189f1bbfb167363caaffa8b791ae7cce852f19`
  inst=`070250e8b347fba9b6ac25ccacf69feb17ea66809e7811e762e03b617df4f7f5`
- `scripts/s2_flip_live.py` repo=`6b238e039b2185665b75640f00757dce18f5139f5c6b1b245d8c3575552744e3`
  inst=`b38777e59d2a2e7c727b6ea6f7a9cfd5f98d431f0e9d018db711bcc8e5ddf1e6`
- `scripts/session_remote.py` repo=inst=`d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4`
- `scripts/browser_worker.py` repo=inst=`3e69858751a326d4c0df61a08cb76e65eaf903ac992d8f6a61c4f60b2377e7bc`
- `scripts/zen_cli.py` repo=inst=`c0ef311b091c06728a6d500da8c1bfcf6fa2a7ed44f0a46ef9d12a46a93ced03`

What the cu.py drift was (diff `9ec713c..ab7c7a5`, 9 lines):
comment plus help text for the P2 persistent port, Brave endpoint
`http://[::1]:9223` corrected to `http://127.0.0.1:9224`. The relay
session default fix (`scripts/session_driver.py` relay() forces
`cu.BROWSER_ENDPOINT` to `http://127.0.0.1:9223`, 9222 is Zen BiDi)
was already identical in the installed tree before this sync.

Note on `tests/realistic/clone1-batch3/results.json`: the installed tree
had no copy (MISSING). The VM working tree holds a modified, uncommitted
copy of that file. It is not mine, I did not commit it, and the sync
source was the laptop repo committed version, so the VM modification
played no part in this sync.

## 4. Relay and browser state before sync (about 17:51 +07)

Relay status (`python3 scripts/session_remote.py status`):
- `{"ok":true,"broker":"running","broker_generation":"411cfadf0b32da29387fe9dbb59e1886","loaded_code_sha256":"d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4","started_git_head":"9ec713c2a6a803c75e41d7e6f99cd335330779ef","state":"idle","owner":null,"driver":"idle","guardian":"idle","cancelled":false,"recovery":"none","next_sequence":1,"active_sequence":null}`
- `loaded_code_sha256` equals the repo `session_remote.py` hash, so no
  relay restart was needed for this sync.

Listening ports (same command run):
- `127.0.0.1:9222` zen-bin pid 14625 (the owner Zen, BiDi)
- `127.0.0.1:9223` chromium pid 18451 (agent Chromium)
- `127.0.0.1:9224` brave pid 17681 (agent Brave, persistent CDP)

## 5. Sync run (detached, 17:52:18 to 17:52:22 +07, elapsed about 4 s)

Launch, 17:52:15 +07 VM time:
- Command: `cd ~/computer-use-wayland && setsid nohup python3 scripts/sync-installed.py > /tmp/wsync-sync-20261122.log 2>&1 < /dev/null & disown`
- Laptop log first line: `2026-11-22 17:52:18 +07 SYNC_START`
- The sync ran detached because SSH sessions to the laptop die after
  about 30 s. Polling used short SSH calls only.

Sync log (`/tmp/wsync-sync-20261122.log`, laptop):
- `Snapshot: ~/.local/share/agent-computer-use/backups/sync-20261122-175218-845410-f1141526`
- Staged build and installed build both printed `pointer built`,
  `indicator built`, `modifiers built`, `wtype built` (plus the known
  wtype unused-parameter warnings).
- `Release ledger: ~/.local/share/agent-computer-use/releases/20261122-175222-261514-ab7c7a5ec3.json`
- `Deploy manifest: ~/.local/share/agent-computer-use/deploy-manifest.json`
- `Installed build script: ~/.local/share/agent-computer-use/scripts/build.py`
- `--check: exit 0 (692 managed files; 11 preserved-history exceptions)`
- `Installed sync published and verified.`

Deploy manifest after sync:
- `source_commit`: `ab7c7a5ec3ce8a81c0fe3cfcc1ac5a1d99db8e06`
- `synced_wall`: `2026-11-22 17:52:22 +07`
- `managed_files`: 692
- `ledger_path`: `.../releases/20261122-175222-261514-ab7c7a5ec3.json`

No relay restart happened: broker code (`session_remote.py`) was
unchanged, and the broker generation stayed `411cfadf...` after the
sync (see section 8). No browser was restarted: all three PIDs in
section 4 are unchanged after the sync (see section 8).

## 6. Post-sync drift verification (about 17:52 +07)

Same full hash loop as section 3, re-run after the sync:
- Output: `LOOP_DONE` with zero `DIFF` lines. All tracked files under
  scripts, native, skill, tests, docs, README.md, LICENSE now match
  the repo at `ab7c7a5`.

Independent check:
- Command: `python3 scripts/sync-installed.py --check`
- Output: `--check: exit 0 (692 managed files)` plus
  `Preserved-history exceptions: CREW.md, docs/automation-cursor-design.md, docs/browser-worker-performance.md, docs/indicator-validation.md, docs/local-optics.md, docs/performance-report.md, docs/research-performance.md, docs/session-startup-report.md, docs/wayland-optimization.md, skill/references/validation.md, tests/latest-results.json`
- Exit code: 0.

Full hashes after sync (about 17:54 +07, all equal to the repo hashes
in section 3):
- `scripts/cu.py` inst=`6b18f8407dfa2a3242d7782884e112e6312ac1d00f555cc645c0501521d64c59`
- `scripts/first_action.py` inst=`9fee1242b691e8a94bffa61c9e23d0e2004d3eb07c2bf34a405c046b769da07a`
- `scripts/code_exec.py` inst=`f85ee4a779241cc68f9abf3d65189f1bbfb167363caaffa8b791ae7cce852f19`
- `scripts/s2_flip_live.py` inst=`6b238e039b2185665b75640f00757dce18f5139f5c6b1b245d8c3575552744e3`
- `scripts/session_remote.py` inst=`d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4`

## 7. Browser observe through the broker (17:53:33 to 17:54:15 +07)

Method: the broker client in `scripts/session_remote.py`
(`start` / `request` / `result` / `finish`) over the relay socket
`/run/user/1000/computer-use-wayland/relay.sock`. No `--endpoint`
was passed on any browser command, so every command used the relay
session default endpoint. That is the exact path that used to 404
on 9222 (Zen BiDi) before the fix.

Lease handling: the first `start` with a lease file under `/tmp`
failed with `{"ok":false,"error":"unsafe_lease_directory"}` because
the lease directory must be owned 0700. I used
`~/wsync-lease-dir` (mode 0700) instead. The first `request` failed
with `{"ok":false,"error":"unsafe_file"}` because the request file
was 0644; `chmod 600` fixed it. Both failures happened before any
session work and left no state behind.

Session start, 17:53:33 +07:
- Command: `python3 scripts/session_remote.py start --owner w-sync --lease-file ~/wsync-lease-dir/lease.json`
- Output: `{"ok":true,"status":"starting","generation":"cb770f0c102467de35993b049355cd92","owner":"w-sync"}`
- Exit code: 0.

Browser tabs, request 17:53:49 +07, result 17:53:54 +07:
- Request: `{"args":["browser","tabs"]}`, sequence 1.
- Request output: `{"ok":true,"status":"accepted","sequence":1}`
- Result output: `{"ok":true,"status":"completed","sequence":1,"response":{"returncode":0,"result":[{"id":"1154C84F7DF2D69318C5EE1FE4D9EAD7","title":"Chat - mochi","url":"https://muse.ai/"}],"session_continues":true}}`
- One tab, in the agent Chromium. No 404, no session failure.

Browser observe, request 17:54:02 +07, result 17:54:06 +07:
- Request: `{"args":["browser","observe","--target","1154C84F7DF2D69318C5EE1FE4D9EAD7"]}`, sequence 2, no `--endpoint`.
- Request output: `{"ok":true,"status":"accepted","sequence":2}`
- Result output (first 3000 chars): `{"ok":true,"status":"completed","sequence":2,"response":{"returncode":0,"result":{"snapshot":"3e74655b-6ef","title":"Chat - mochi","url":"https://muse.ai/","elements":[refs e1 through e36 visible before the 3000-char truncation, ...]}}}`
  (Tab title quoted with its dash normalized to a hyphen.)
- Observe completed with returncode 0 and a real DOM snapshot. No 404.
  (Element names and page content from the observed tab are not copied
  into this log; only the snapshot id, tab title, URL, and the fact
  that elements were returned are recorded here.)

Session finish, 17:54:15 +07:
- Command: `python3 scripts/session_remote.py finish --lease-file ~/wsync-lease-dir/lease.json`
- Output: `{"ok":true,"status":"finished","generation":"cb770f0c102467de35993b049355cd92","driver":"stopped","guardian":"clean","error":null}`
- Exit code: 0. The finished session is the same generation that was started.

## 8. State after the probe (about 17:54 +07)

Relay status:
- `{"ok":true,"broker":"running","broker_generation":"411cfadf0b32da29387fe9dbb59e1886","loaded_code_sha256":"d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4","started_git_head":"9ec713c2a6a803c75e41d7e6f99cd335330779ef","state":"finished","owner":"w-sync","generation":"cb770f0c102467de35993b049355cd92","driver":"stopped","guardian":"clean","cancelled":false,"recovery":"none","next_sequence":3,"active_sequence":null,"error":null,"stop_reason":"explicit_finish"}`
- Broker generation unchanged (`411cfadf...`): the relay was not
  restarted at any point. `started_git_head` still reads `9ec713c`
  because that is the head recorded when the relay process started;
  the loaded broker code hash matches the repo, and every driver
  spawned from now on runs the synced installed tree.

Listening ports, same PIDs as before the sync:
- `127.0.0.1:9224` brave pid 17681
- `127.0.0.1:9222` zen-bin pid 14625
- `127.0.0.1:9223` chromium pid 18451

No driver process left (`pgrep -af "session-driver|cu.py session"`
matched only the probing shell itself). Temporary lease directory
`~/wsync-lease-dir` (held the lease secret) was removed after the
finish: `LEASE_DIR_REMOVED`.

## 9. Verdict

- Drift before sync: 54 entries (11 content diffs, 43 missing files),
  installed tree at `9ec713c`, repo at `ab7c7a5`.
- Drift after sync: zero. Full hash loop clean, `sync-installed.py
  --check` exit 0, 692 managed files, 11 preserved-history exceptions
  (by design, not drift).
- Browser observe through the broker: works. `browser tabs` and
  `browser observe` with no explicit endpoint both completed with
  returncode 0 through the relay session default (agent Chromium on
  9223). No 404 anywhere in the probe.
- Remaining notes, not drift:
  (a) The relay process `started_git_head` label still reads `9ec713c`;
  that label only changes when the relay process restarts, and no
  restart was needed or done.
  (b) The 11 preserved-history exceptions are intentional per
  `sync-installed.py` and are not drift.
  (c) The VM working tree still holds an unrelated modified
  `tests/realistic/clone1-batch3/results.json` (uncommitted, not mine);
  it was not committed and played no part in this sync.
- Not done, by order: no restart of Zen, Brave, or Chromium (PIDs
  unchanged), no tab opened or switched in Zen, no owner session
  restarted or disturbed. The only session started was my own
  `w-sync` broker session, and it was finished cleanly.
