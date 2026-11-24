# R3-L3 readiness check, 2026-11-24

Check window: 21:21-21:38 +07, 2026-11-24. Elapsed about 17 minutes.
Scope: hooks, tools, CI, and infrastructure for the R3-L3 run on 2026-11-25.
Every item below was verified live in this window. No test message was sent
to any scorer. No owner tab was closed or navigated. Zen was not restarted.

Verdict: NOT FULLY READY. 3 FAILs, all in the scorer-messaging chain
(daemon dead, Chromium down, stale scorer target). Everything else is
green except 3 PARTIALs. The run cannot start until the 3 FAILs are fixed.
Fixes are listed per item and in section 7.

Score: 21 PASS, 3 FAIL, 3 PARTIAL, out of 27 sub-checks.

## 1. Rung 3 scripts: PASS (9/9)

Worktree `r3l3-run-wt`, head `5a1d7052`.

- All 10 `rung3-ci/*.py` scripts compile (`python3 -m py_compile`): PASS.
- `verify-list.py`: PASS, `RESULT: 62 pass, 0 pending, 0 fail`, exit 0.
- `check-key-hash.py`: PASS, JSON hash `5059f6c4...` matches the recorded
  value in `rung3-run-log/thu-tu-chay.txt`, exit 0. The `.md` key file
  hashes to `21f8b61a...` (sha256sum, confirmed).
- `validate-ledger.py rung3-run-log/R3-L3-grades.jsonl`: PASS,
  `ledger valid: 1 row(s), 0 errors`. Independent JSON parse confirms 1
  row, a flagged TEST row (`task_id` R3-TEST, `test_row` true), never a
  grade.
- `snapshot.py --name`: PASS. Synthetic evidence dir snapshotted to
  `/tmp/r3test-snap/R3-TEST-L3` with a manifest (2 files, sha256 per file).
  Test used a temp root only, the real snapshot tree was not touched.
- `manifest-gate.py --snapshot <synthetic> --task R3-TEST`: PASS, exit 0.
- `audit-scan.py`: PASS on a clean verdict (exit 0, no forbidden reads),
  and correctly FAILs (exit 1) on a verdict that reads the run ledger.
- Snapshot dirs: PASS. 60 empty `-L3` dirs exist under
  `~/workspace/rung3-snapshots/`. The only non-empty entry is the
  pre-existing `R3-040-retry-s1` retry evidence, which is not a run dir.

## 2. Runners: PASS (2/2)

- FCC runner, tmux session `r3-fcc-runner-L3` on the laptop: PASS. Session
  exists (created 2026-11-24 17:18:33), pane shows an idle READY prompt
  after its last completed work (1m 21s, done 17:20).
- Codex exec: PASS, proven live. `codex --no-daemon -m gpt-6-luna
  --sandbox danger-full-access -C /home/james exec --skip-git-repo-check`
  printed exactly `CODEX-PROOF-OK`, 7,394 tokens used, codex 0.172.0.
  Run detached on the laptop, log `/tmp/codex-proof-20261124.log`.

## 3. Zen 1.24.3b: PASS with 2 PARTIALs

- Running: PASS. PID 788926 since 20:44, launched with
  `--remote-debugging-port=9222 --marionette`.
- Version and BuildID: PASS. `application.ini` shows `Version=1.24.3b`
  and `BuildID=20261118023529`. The BiDi `session.new` reply confirms the
  same (`browserName` zen, `browserVersion` 1.24.3b,
  `moz:buildID` 20261118023529).
- BiDi port 9222: PASS. `session.new` works (two sessions created and
  ended cleanly in this check). Note: the WebSocket endpoint is
  `ws://127.0.0.1:9222/session` (HTTP 101 there). The bare `/` path only
  serves an httpd.js placeholder page and the Chrome-style `/json/*`
  endpoints return 404, which is expected for a Firefox-based browser.
- Marionette port 2828: PARTIAL. The port is live and answers the greeting
  (`applicationType` gecko, `marionetteProtocol` 3), but `newSession` gets
  no reply at all in two attempts (12s and 15s timeouts, zero bytes back).
  No other client is connected to 2828 or 9222, so it is not a held
  session. Cause is unproven. BiDi is the working primary control path,
  so this does not block the run, but the fallback path is unproven.
- Update-off lock: PASS. In the active profile (the one holding
  `.parentlock`), `app.update.enabled` is false and
  `remote.prefs.recommended` is false.
- Council prefs from commit `77b24932`: PARTIAL. All 13 prefs are present
  in `user.js` (1566 bytes, backup `user.js.bak-council-20261124` present).
  9 of 13 are effective in `prefs.js`. 4 are absent from `prefs.js`:
  `dom.max_chrome_script_run_time`, `telemetry.fog.init_on_shutdown`,
  `browser.tabs.unloadOnLowMemory`, and
  `threads.lower_mainthread_priority_in_background.enabled`. The most
  likely cause is that these prefs do not exist in this build, so the
  browser ignores those `user.js` lines. They are harmless no-ops, all
  performance or telemetry niceties, none load-bearing for the run.
  Impact: low.

## 4. Scorer daemon messaging: FAIL (both scorers down)

Read-only checks only. No message was sent to either scorer.

- Speed daemon process: FAIL. Dead. Its socket refuses connections, and
  both recorded PIDs (daemon 2135, supervisor 7817) are gone. Last log
  line is 19:18:11 `daemon_listening`. The daemon died sometime after
  19:18 with no death logged, and the supervisor is dead too, so nothing
  restarts it. The 15-minute watchdog cron is disabled (see section 5),
  so the death went unnoticed for about 2 hours.
- Mochi (Chromium, port 9223): FAIL. Chromium is not running at all on
  the laptop (no process, no listener on 9223). `read.py --recipient
  mochi` fails with `ECONNREFUSED 127.0.0.1:9223`, and the send probe
  crashes the same way. The stored target ID is unresolvable until
  Chromium is back, and target IDs change on every restart, so it must
  be resolved dynamically after relaunch.
- Mei (Brave, port 9224): FAIL, recoverable. Brave is alive on 9224, but
  the stored target ID is stale: it is not in the target list. The live
  tab is `F0857EB317D3027975B6F70658AB666A` ("Chat - clone1", muse.ai).
  Direct read of that tab works: 47 items, 31 assistant messages, latest
  messages are the scorer's R3-L3 risk mitigations report (committed as
  `a587580`). The send probe against the live tab succeeds: the composer
  grounds (TEXTAREA, label "Message") in 37 ms. So the read path and the
  send path are both provable with the new target ID. An actual send was
  not tested, by design (no test messages).

## 5. Tonight-only watchdogs: PASS (5/5)

From the scheduler, checked 21:31 +07.

- `tonight-coordinator-stall-watch`: enabled, interval 15m, last run
  21:28:21 succeeded, next 21:41:56.
- `tonight-clone1-progress-watch`: enabled, interval 15m, last run
  21:14:56 succeeded, one run in flight at check time, next 21:41:56.
- `tonight-zen-laptop-health-watch`: enabled, interval 15m, last run
  21:28:13 succeeded, next 21:41:56.
- `tonight-worker-process-watch`: enabled, interval 15m, last run
  21:27:23 succeeded, next 21:41:56.
- `mei-mochi-15m-watchdog`: still disabled, as required.

## 6. CI: PASS on head, 1 historical note

Repo `computer-use-wayland`, branch `todolist-push`, head `5a1d7052`
(21:28:56 +07).

- Latest push: `secret-scan` (gitleaks v8.30.1) SUCCESS, `rung3-checks`
  SUCCESS. Both workflows green on head.
- Key hash: PASS (see section 1). Verify-list: 62 pass (see section 1).
  Local re-runs match CI.
- Historical note, not blocking: the 14:02 push (range `a587580..c7d5eebf`)
  failed `secret-scan` with 1 finding. Reproduced locally with gitleaks
  8.30.1 on the same range: rule `private-ip`, file
  `improvements/discord-cli/WORKLOG.md` line 89, commit `2ee670a7`. The
  flagged value is a private Tailscale (CGNAT-range) address inside an
  error message, not a credential. It is still in history, and later
  push-scoped scans pass because they scan only new commits. The same
  address also appears in the head tree in two other files. Severity for
  the run: low. It does not block the run, but it breaks the
  no-personal-info posture.

## 7. Not ready: list and fixes

1. FAIL, scorer daemon dead. Fix: restart it with
   `~/workspace/speed-daemon/daemon.sh restart`, then confirm with
   `daemon.sh status` and a socket connect. Also find why the supervisor
   died with it, or the daemon can die silently again. Do the restart
   AFTER fix 3, so it loads the corrected target IDs.
2. FAIL, Chromium (Mochi) not running. Fix: relaunch Chromium with
   remote debugging on port 9223 and the profile that holds the scorer
   chat tab, so the tab restores. Then list `127.0.0.1:9223/json/list`
   and take the new page target ID for the scorer tab. Do not launch
   with a fresh profile (the tab would be lost). Do not close or
   navigate any existing tab.
3. FAIL, Mei target ID stale. Fix: update the target ID for mei to
   `F0857EB317D3027975B6F70658AB666A` in both
   `~/workspace/speed-daemon/daemon.py` and
   `~/workspace/speed-daemon/read.py` (both hardcode the old ID), then
   restart the daemon (fix 1). After that, re-run `read.py --recipient
   mei` and `--recipient mochi` plus the send probe for both, and only
   then call messaging ready. A real send is still unproven until the
   coordinator's next real message goes through.
4. PARTIAL, Marionette `newSession` hangs. Fix: coordinator to
   investigate before the run (possible stale modal dialog in Zen or a
   Zen/Firefox-160 quirk). Do NOT restart Zen to fix this. BiDi works,
   so treat BiDi as primary and Marionette as unproven fallback.
5. PARTIAL, 4 council prefs not effective. Fix: coordinator to confirm
   the 4 prefs in `about:config` during the run (read-only check), or
   drop/replace them with current-build equivalents. No restart needed.
   Low impact.
6. NOTE, historical gitleaks finding in history. Fix: scrub the private
   address from `improvements/discord-cli/WORKLOG.md` (and the two other
   head-tree files) in a new commit, replacing it with a placeholder.
   History rewrite is a separate owner decision on a shared branch. The
   weekly full-history scan (Mondays 06:00, not a required check) is the
   triage signal for the rest.
