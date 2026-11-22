# W-SOAK log: S0 1-day soak status, read-only check

Owner: Phạm Tuấn. Branch: todolist-push. Worker: W-SOAK, for COORD-CLICK-6, queue item 17.
Check window: 2026-11-22 17:49:30 +07 to 17:52 +07 (Asia/Ho_Chi_Minh). All times wall-clock +07 unless noted.
Method: read-only. No config change, no master restart, no new soak, no touching the laptop GUI, no ydotool. Short SSH commands only. One fresh SSH probe, one mux liveness check, local ps/ls/cron reads.

## 0. Verdict (status at 17:50:43 +07)

- Soak master: DEAD. No S0 master process, no control socket, liveness check rc=255.
- Continuous life from the 06:41 start: NO. The run was broken at least twice by VM restarts (about 07:51 and 17:11 +07).
- Longest documented continuous keepalive-master life: 50 minutes (07:00 to 07:50, pid 25435), with 40 minutes strictly confirmed by PROBE-S0 and the last 10 minutes (t+45, t+50) recorded only by S0-IMPL, see section 4.
- Last known-alive sighting of any S0 master: 14:29:44 +07, pid 26834, from state.json. Unattributed, no log rows, not proof of a soak.
- Laptop path: ALIVE. Fresh SSH works (2.754s, rc=0). The death is on the VM side, not the laptop.
- Keepalive ServerAliveInterval=15 did hold while a master lived (soak-B: 9/9 confirmed fast ticks, zero deaths, vs plain soak A: 11/11 deaths). That proves keepalive over about 1 hour, not over 1 day. No 1-day claim can be made.

## 1. Live checks run now (commands, outputs, elapsed)

Repo baseline, run 17:49:30 +07:
- `git fetch origin` then `git pull --ff-only`: Already up to date. HEAD 05140c10d180ce7d26548df0f5b6f9c4d431e316, branch todolist-push. Elapsed about 5s for both calls.

Check 1, mux liveness, run 17:50:43 +07, elapsed 93ms:
- Command: `python3 scripts/ssh_mux.py check` (liveness only, no restart, no state write; scripts/ssh_mux.py:364, check is liveness only).
- Output verbatim: `{"alive": false, "check_rc": 255, "pid": null, "wall": "2026-11-22 17:50:43 +07"}`, process rc=1.
- Socket check same minute: `ls -la /tmp/cm-s0-*` and `ls -la /tmp/cm-*`: No such file or directory. No socket exists.

Check 2, process list, run 17:49:55 +07 and 17:51:15 +07:
- Command: `ps aux | grep -E "ssh|soak|mux" | grep -v grep`.
- Output 17:49:55: empty, no ssh process at all.
- Output 17:51:15: two plain fresh ssh invocations by sibling workers (pid 7048, MEI/MOCHI CDP observe loop; pid 7051, date plus desktop file reads). Both are transient fresh connects, no ControlMaster, no -N, no mux socket. No soak runner, no master, no python soak process in either poll.

Check 3, fresh SSH path probe, run 17:50:58 to 17:51:01 +07, elapsed 2754ms:
- Command: `~/workspace/ssh-laptop.sh 'echo SOAK-CHECK-ALIVE; hostname; date "+%F %T %Z"'`.
- Output verbatim: SOAK-CHECK-ALIVE, omarchy, 2026-11-22 17:51:02 +07, fresh_rc=0.
- Elapsed 2754ms for one fresh connect. Faster than the PROBE-S0 fresh baseline (mean 4.667s, n=10) and the S0-IMPL run 2 fresh mean (4.711s), plausibly less contention now (campaign paused 16:32 to 17:47, only 8 lanes respawned at 17:47). One sample only, not a new baseline. It proves the laptop is awake and the path works. It created no master and no socket: ssh-laptop.sh carries no ControlMaster options, and `ls /tmp/cm-*` after the probe still reports no such file.

Check 4, VM boot time, run 17:51:15 +07:
- Command: `uptime; who -b; cat /proc/stat | grep btime`.
- Output: up 40 min, system boot Nov 22 10:11 (UTC), btime 1795342260. That is 17:11 +07. The VM rebooted at about 17:11 +07, a second restart after the about 07:51 restart recorded by PROBE-S0 and S0-IMPL. Any master from before 17:11 is dead by definition, and no master was started after the boot (no ssh master process, no socket).

Check 5, S0 state file, read 17:49:55 +07:
- File: ~/.cache/agent-computer-use/ssh-mux/state.json, mtime 2026-11-22 07:29:44 UTC, that is 14:29:44 +07.
- Content verbatim: `{"master_last_seen_wall": "2026-11-22 14:29:44 +07", "master_pid": 26834}`.
- Directory listing: only state.json, no master.log, no ssh-mux.jsonl. No master_death row was ever logged by ssh_mux.py (ensure/watchdog logs a death to ssh-mux.jsonl before restarting; that file does not exist). So no ssh_mux.py death was ever recorded, and the 14:29:44 write is the last known-alive sighting of master 26834.

Check 6, watchdog cron, read 17:50 +07:
- Command: cron.list.
- Result: no S0 mux watchdog cron exists. The only watchdogs are watchdog-liveness-check (5 min, agent liveness) and watchdog-zen-20m (20 min, Zen agent check). Nothing was scheduled to check or restart the S0 master. The ssh_mux.py watchdog() code exists (scripts/ssh_mux.py:343), but no cron calls it.

## 2. History from the PROBE-S0 log (read, not re-measured)

Source: improvements/worker-probe-s0-log.md, final commit 39e1450, and improvements/worker-s0-impl-log.md, commit 8817a90. Both read in full at 17:49 +07.

- Soak A (plain master, no keepalive), started 06:41:20 +07, pid 13662. t+0 sample 06:41:28, 0.894s, rc=0. Then 11 consecutive fallback ticks t+5 to t+55 (06:46:32 to 07:37:26), each 4.461s to 5.929s, each with a new master pid. Plain master died 11 times in 55 minutes and never survived a 5 minute gap. Cause isolated: idle TCP killed after about 60 to 90s on the VM to laptop path.
- Idle A/B test, 06:53 to 06:58 +07. Plain master A (pid 21199): dead by t90 (5.582s fallback, new pid 23325), dead again by t300. Keepalive master B (pid 21189, ServerAliveInterval=15): alive at t90 (1.172s, same pid) and t300 (0.883s, same pid). Finding F5, controlled A/B.
- Soak-B (keepalive master, ServerAliveInterval=15), started 07:00:06 +07, pid 25435. PROBE-S0 confirms 9 ticks t+0 to t+40 (07:00:13 to 07:40:21), all rc=0, all same pid, mean 0.958s. S0-IMPL section 7 additionally records t+45 (07:45, 1.822s) and t+50 (07:50, 1.078s), same pid, read from soak-b.jsonl before it was wiped. See section 4 for the discrepancy.
- About 07:51 +07: VM restart wiped /tmp (soak runners, sockets, logs all gone). The 60 minute soak-B was NOT completed: 40 minutes confirmed by its owner, 50 minutes claimed by S0-IMPL. No soak process was restarted after that restart, as far as any repo record shows: zero commits after 07:53 mention soak, mux, or watchdog (git log 08:00 to 17:50, 57 commits, grep for soak|mux|s0|watchdog returns nothing).

## 3. The gap: 07:51 to 17:50 +07 (what is known, what is not)

- Known: S0 master 26834 was seen alive at 14:29:44 +07 by an ensure_master call (state.json, section 1 check 5). That is about 6 hours 39 minutes after soak-B started and about 3 hours 20 minutes before this check.
- Not known: who started master 26834, when it started, what kept it alive, whether it ever died and restarted, or whether any soak runner existed after 07:51. No repo file names pid 26834 (grep for 26834 across improvements/ and scripts/ returns nothing). No soak log rows exist after 07:50. No soak runner process exists now. No watchdog cron exists. The 14:29:44 sighting is a single last-seen timestamp, not a soak record, and I do not treat it as one.
- Known: the VM rebooted at 17:11 +07 (section 1 check 4). Even if master 26834 lived from its start to 17:11, its continuous life ended there at the latest. No master started after the reboot.

## 4. Discrepancies and open items (evidence only, not diagnosis)

- D1: PROBE-S0 lists 9 confirmed soak-B ticks (t+0 to t+40); S0-IMPL lists 11 (adds t+45 1.822s and t+50 1.078s). The source file soak-b.jsonl was wiped in the 07:51 restart, so the two extra rows cannot be re-verified from the file. Either way the soak-B run ended at 07:51, uncompleted.
- D2: master 26834, last seen 14:29:44 +07, has no owner in any repo record. Whether it was a soak continuation, a step 8/10 test use, or another worker's ensure call is unknown from the records I can see.
- D3: the final direction calls this a "1-day soak" (worker-click3-final-direction-log.md:226) but also says "soak ends about 07:41 +07". The 60 minute soak-B plan and the 1-day label do not match. The coordinator brief for this check says the 1-day soak started about 06:41. On the evidence, no 1-day continuous run exists: the longest continuous keepalive-master life on record is 50 minutes.

## 5. Recommendations (recommendations only, nothing done)

- R1: Do not report the 1-day soak as passed or as running. It is dead as of 17:50:43 +07, and it never ran a continuous day.
- R2: If a real 1-day soak is still wanted, start it as a NEW run, not a resume: fresh master with ServerAliveInterval=15 via setsid/nohup (never ssh -f), a named owner (PROBE-S0 owns follow-up per the brief), a watchdog cron every 5 minutes calling scripts/ssh_mux.py watchdog, and tick rows logged to ~/workspace (persistent) instead of /tmp (wiped by both restarts today).
- R3: The re-review should settle D1 (9 vs 11 soak-B ticks) on testimony, since the file is gone.
- R4: Note the second VM restart at 17:11 +07 to the coordinator: any /tmp-based master or soak is wiped by restarts, and two restarts happened today.

## 6. Commit record

- Log commit: (hash recorded in the follow-up commit, same pattern as PROBE-S0 commit b4b9224).
