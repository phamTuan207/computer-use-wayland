# R3-L3 Phase 0 prepare: messaging chain verification (gate G-23)

- Date: Wed 2026-11-25, checks run 09:00-09:03 +07
- Worker: Phase 0 prepare worker (messaging chain only)
- Verdict: **PASS, no blockers.** Mei and Mochi tabs live, logged in, readable and (Mochi) writable via the speed daemon. Daemon + supervisor alive, resilience proven.
- Note: the chain was NOT healthy on arrival. Three faults were found and fixed during this check (see "Faults found and fixed"). The run was not started and no run task was executed.

## 1. Target IDs (resolved dynamically, live)

Resolved from `http://127.0.0.1:9224/json/list` (Brave) and `http://127.0.0.1:9223/json/list` (Chromium) via `~/workspace/ssh-laptop.sh` at ~09:00 +07. Never hardcoded in the procedure; the values below are the observed live IDs, copied from the list output.

| Recipient | Browser / port | Tab title | Target ID |
|---|---|---|---|
| mei | Brave / 9224 | Chat — mei | `709E2AE0F1CE0F9C9B57536626782E2D` |
| mochi | Chromium / 9223 | Chat — mochi | `A25AA6F0370A00A174BC5304A333417D` |

- Clone tabs present but untouched and never used as targets: clone1 on 9224 (`07BBBD581778D6E75975752206106F10`), clone2 on 9223 (`F85C814E12C1F7B5E179206E204FBF4F`). The forbidden clone1 target from the brief (`F0857EB317D3027975B6F70658AB666A`) does not appear in the current list.
- Identity verified by direct read, not by title alone: mei's tab returned her R3-L3 prep messages (PR #253 merge, freeze hashes, R3-047 position 34 correction); mochi's tab returned her readiness/blocker notes (PR #341, PR #346, usage limit until 02:38 25/11, now passed).

## 2. read.py results (after target fix)

`python3 ~/workspace/speed-daemon/read.py --recipient <name>`

| Recipient | ok | total_items | assistant_count | elapsed_s |
|---|---|---|---|---|
| mei | true | 25 | 18 | 1.39-1.42 |
| mochi | true | 33 before test send, 34 after | 19 | 1.56-1.57 |

- Mei latest assistant message at check time: her verification of commit 5580aba (new scorer pairs, ledger pattern DP-0[123567]).
- Mochi latest assistant message at check time: her 21:39 update (2 of 3 FAILs fixed, Chromium back on 9223, waiting on Mei channel + 02:38 limit).
- Mei's tab was live on arrival: the owner-opened Brave chat is present and logged in. No owner action needed.

## 3. Daemon + supervisor PIDs

| Process | PID | Started | State at end of check |
|---|---|---|---|
| speed daemon (`daemon.py`) | **12541** | 2026-11-25 09:01:27 +07 (restarted by supervisor during resilience test; original restart 09:00:10 +07, pid 12056) | alive, `send.py --ping` ok, `send.py --status` ok, master_ok true, sends 0, failures 0 |
| supervisor (`supervisor.sh` loop) | **12133** | 2026-11-25 09:00:10 +07 | alive, watchdog cycle every 60s |

- On arrival BOTH were dead: pid files held stale 5108 (daemon) / 5157 (supervisor), `ps` found neither, `send.py --status` gave Connection refused, daemon.log last event was daemon_start 21:39:46 24/11 with no daemon_stop, supervisor.log empty, watchdog.log last entry 2026-11-23 06:58. Restarted with `daemon.sh start` + `supervisor.sh start` at 09:00:10 +07.
- Daemon status after restart: `started_hcm 2026-11-25 09:00:10 +07`, uptime 12.4s at first check, master_ok true.

## 4. Mochi test send + delivery confirmation

- Send: `send.py --recipient mochi --run 200 --message "Phase 0 prepare test G-23 (25/11): kiem tra kenh daemon toi mochi sau khi sua target ID. Khong can lam gi, khong can tra loi. Ma kiem tra: G23-0905"`
- Result: outcome=sent, verified=True, wall 09:00:49-09:00:50 +07, client elapsed 1.21s, daemon elapsed 1.205s, ssh 1204.8ms, node 76ms. Pill acquired + verified, released + release_verified. V12 found the sent bubble (role user, textLen 151).
- Delivery confirmed by INDEPENDENT re-read, not by the send receipt:
  - `read.py --recipient mochi`: total_items 33 -> 34, assistant_count unchanged at 19.
  - Direct all-bubbles CDP read (`/tmp/read-last.mjs`, dynamic target): total 34, last bubble index 34, role user, text verbatim: "You:Phase 0 prepare test G-23 (25/11): kiem tra kenh daemon toi mochi sau khi sua target ID. Khong can lam gi, khong can tra loi. Ma kiem tra: G23-0905". The message is the last bubble in Mochi's thread.
- Mochi's 02:38 usage limit has passed; she is unlocked. No reply to the test was requested and none is needed.
- Minor count note: the send's V12 counted 35 items immediately after Enter while the re-reads count 34. The extra item is a transient/empty bubble counted by the send path and filtered by the read path (read filters empty-text bubbles). Delivery itself is proven by the verbatim last-bubble text above, so this is a counting quirk, not a delivery gap.

## 5. Daemon resilience proof

- Kill: `kill 12056` at 09:01:18 +07 (daemon pid from the 09:00 restart).
- Supervisor response (watchdog.log): `daemon_down_restarting` 09:01:20, `daemon_restart` rc=0 up=true 09:01:28, new daemon pid 12541.
- Verified at 09:02:35 +07 (77s after kill, inside the 5-minute bar): new daemon pid 12541 alive, `send.py --ping` ok, `send.py --status` ok (started 09:01:27, uptime 68.8s, master_ok true). Supervisor pid 12133 still alive.
- Post-restart reads: `read.py --recipient mei` ok=true (25/18), `read.py --recipient mochi` ok=true (34/19). Downtime was ~9-10s (kill to listening).

## 6. Faults found and fixed during this check

1. **Stale target IDs in `daemon.py` and `read.py`.** Both hardcoded mei `FF64D264EB17D383F74F3E569A67D42F` and mochi `966FD5D4E1AB71B4C5C773612C07778C`; the live tabs now carry different IDs (see section 1). The browsers evidently restarted overnight (Mochi's own message records the previous target change at 21:39 24/11; the IDs changed again after that). Updated both files' RECIPIENTS to the dynamically resolved IDs. No commit made (parent commits).
2. **Daemon + supervisor both dead on arrival** (stale pid files 5108/5157, socket refused). Restarted both; see section 3.
3. **Laptop-side scripts missing from /tmp** (`/tmp/daemon-read.mjs`, `/tmp/daemon-send.mjs`, `/tmp/daemon-one-send.sh` all absent). Re-pushed `daemon-read.mjs` for the direct-read verification; the daemon's own startup re-installed the send scripts (its `ensure_laptop_files` path). The chain now works end to end, which proves the laptop files are back in place.

## 7. Blockers

None. Mei's tab is present and logged in; Mochi is unlocked (02:38 passed) and reachable; daemon + supervisor alive with proven auto-restart.

## 8. Follow-up recommendation (not done, for the parent to decide)

Target IDs change every browser restart, so `daemon.py` / `read.py` hardcoding them will break the chain again the next time Brave/Chromium restarts. The durable fix is to resolve the target by tab title (`Chat — mei` / `Chat — mochi`) from `/json/list` at send/read time instead of storing an ID. Flagging only; no code change made beyond restoring the current IDs.
