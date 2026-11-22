# W-SOAKRESTART log: S0 soak master restarted as a NEW run

Owner: the owner. Branch: todolist-push. Worker: W-SOAKRESTART, for COORD-CLICK-7.
Run id: soak-restart-20261122-1900. All times wall-clock Asia/Ho_Chi_Minh (+07) unless noted.
Method: read-only checks plus one master start plus one detached tick loop. No cron
created, no laptop writes, no process killed, no live browser work, no ydotool.
Team order 19:03 22/11 applies: work autonomously, Lauren Tan evidence standard
(command plus output plus commit hash plus time log), continuous logging, measure
everything. The continuous log for this run is ~/workspace/s0-soak-restart-ticks.jsonl
(one row every 5 min, persistent in ~/workspace, not /tmp).

## 0. Verdict so far (19:01 +07)

- Old master: DEAD at check 19:00:27 +07, same as W-SOAK found at 17:50:43 +07.
  No process, no socket, liveness check rc=255.
- New master: ALIVE since 19:00:35 +07, pid 27441, same pid at every check so far.
- Tick loop: ALIVE, pid 27497, first tick row 19:00:54 +07, via mux, same master pid.
- Short monitoring (t+6): DONE, 19:06:37 +07. Master 27441 alive continuously
  for 6 min 02 s, same pid at every check, 2 tick rows plus 2 manual mux
  samples, zero deaths, zero restarts. See section 6.

## 1. Launch command, exact (step 1)

Source of truth: scripts/ssh_mux.py, master_argv(), read in full before starting.
The start was done through the S0 implementation's own path, which calls
start_master(): setsid plus nohup plus master_argv(), stdin from /dev/null,
detached, then polls -O check up to 30s. No `ssh -f` anywhere (PROBE-S0 F1:
`-f` masters refuse mux sessions and die in 1-2 min).

Command run, 19:00:30 +07:

```
cd ~/workspace/computer-use-wayland && python3 scripts/ssh_mux.py ensure
```

Effective master argv (from master_argv(), verified in the live ps output,
section 4):

```
ssh -o BatchMode=yes -o ConnectTimeout=25 -o StrictHostKeyChecking=accept-new
  -o IdentitiesOnly=yes
  -o ProxyCommand=python3 /home/hatch/workspace/tailscale-proxy.py %h %p
  -i /home/hatch/.ssh/id_ed25519
  -o ControlMaster=yes -o ControlPath=/tmp/cm-s0-%r@%h:%p
  -o ControlPersist=600 -o ServerAliveInterval=15 -o ServerAliveCountMax=3
  -N james@100.70.92.52
```

Key properties: ServerAliveInterval=15 (the load-bearing option, idle test B),
ControlPersist=600, ControlMaster=yes, socket /tmp/cm-s0-james@100.70.92.52:22.
Repo HEAD at start: c97d617 (checked by git log, 18:59 +07; fetch showed up to
date, see section 2 note). Prior art: soak-B master pid 25435, same keepalive
form, 07:00:06 +07, 9 confirmed ticks, 40 min (worker-probe-s0-log.md).

## 2. State before restart (step 2), 19:00:27 +07

Commands and verbatim outputs:

- `date`: 2026-11-22 12:00:27 UTC, that is 19:00:27 +07.
- `uptime; who -b`: up 1:49, system boot Nov 22 10:11 UTC, that is 17:11 +07.
  Same second VM restart W-SOAK found (17:11 +07). No new restart since.
- `ps aux | grep -E "ssh|mux|soak" | grep -v grep`: empty, rc=1. No ssh process.
- `ls -la /tmp/cm-s0-* /tmp/cm-*`: No such file or directory, both patterns.
- `python3 scripts/ssh_mux.py check`: `{"alive": false, "check_rc": 255,
  "pid": null, "wall": "2026-11-22 19:00:27 +07"}`, process rc=1.
- `cat ~/.cache/agent-computer-use/ssh-mux/state.json`: `{"master_last_seen_wall":
  "2026-11-22 14:29:44 +07", "master_pid": 26834}`. Unchanged since W-SOAK.
  Directory held only state.json, no ssh-mux.jsonl, no master.log.
- `git fetch origin` plus `git log --oneline -3` at 18:59 +07: HEAD c97d617,
  branch todolist-push. Dirty/untracked files in the tree (results.json plus
  untracked improvements drafts) are other lanes' work, NOT touched here.

Conclusion: master still dead, exactly as W-SOAK reported at 17:50:43 +07.
No master started after the 17:11 +07 VM reboot.

## 3. Start (step 3), 19:00:30 to 19:00:35 +07

- Command: `python3 scripts/ssh_mux.py ensure` (section 1), issued 19:00:30 +07.
- Output verbatim: `{"alive": true, "death_logged": true, "pid": 27441,
  "restarted": true, "wall": "2026-11-22 19:00:35 +07"}`, process rc=0.
- Elapsed: about 5 s (12:00:30 to 12:00:35 UTC).
- Master pid: 27441. Start wall: 2026-11-22 19:00:35 +07.
- The ensure call logged the old death first (previous pid 26834, check rc 255)
  and then the restart, both in ~/.cache/agent-computer-use/ssh-mux/ssh-mux.jsonl
  (verbatim rows in section 4).

## 4. Verify t+0 (step 4), 19:00:38 to 19:00:39 +07

All checks pass. Verbatim outputs:

- Process, `ps -o pid,ppid,etime,args -p 27441`: PID 27441, PPID 1, ELAPSED 00:03,
  full cmdline matches the section 1 master argv exactly (ControlMaster=yes,
  ControlPath=/tmp/cm-s0-%r@%h:%p, ControlPersist=600, ServerAliveInterval=15,
  ServerAliveCountMax=3, -N james@100.70.92.52). PPID 1 means fully detached,
  reparented to init, not attached to my session.
- Socket, `ls -la /tmp/cm-s0-*`: `srw------- 1 root root 0 Nov 22 12:00
  /tmp/cm-s0-james@100.70.92.52:22`. Socket exists.
- Liveness, `python3 scripts/ssh_mux.py check`: `{"alive": true, "check_rc": 0,
  "pid": 27441, "wall": "2026-11-22 19:00:38 +07"}`, process rc=0.
- Mux sample, `python3 scripts/ssh_mux.py run -- echo SOAK-RESTART-T0-ALIVE`:
  `{"master_pid": 27441, "rc": 0, "restarted": false, "secs": 0.558,
  "stderr": "", "stdout": "SOAK-RESTART-T0-ALIVE\n", "via": "mux",
  "wall": "2026-11-22 19:00:39 +07"}`, process rc=0. Same pid, via mux,
  0.558s (in the PROBE-S0 mux band, mean 1.339s; fast sample, not a new claim).
- State file after start: `{"master_last_seen_wall": "2026-11-22 19:00:38 +07",
  "master_pid": 27441, "master_started_wall": "2026-11-22 19:00:35 +07"}`.
- Death/restart log, `cat ~/.cache/agent-computer-use/ssh-mux/ssh-mux.jsonl`:
  `{"check_rc": 255, "event": "master_death", "previous_pid": 26834,
  "socket": "/tmp/cm-s0-%r@%h:%p", "wall": "2026-11-22 19:00:30 +07"}` then
  `{"event": "master_restart", "new_pid": 27441, "previous_pid": 26834,
  "wall": "2026-11-22 19:00:35 +07"}`.
- Master log, `tail -5 ~/.cache/agent-computer-use/ssh-mux/master.log`: empty,
  no stderr output, clean start.

## 5. Tick loop (keeps the master alive, logs rows to ~/workspace)

Why a ticker is needed: the master carries ControlPersist=600, so with no
client use for 600s it exits on its own. One mux `true` every 300s resets
that timer and proves the master is still the same pid. Without a ticker
(or a watchdog cron) this restart would die idle in about 10 minutes, same
failure mode as the plain soak A.

- Script: ~/workspace/s0-soak-restart-tick.sh (1286 bytes, written with
  muse.write, chmod +x). Loop: `python3 scripts/ssh_mux.py run -- true`,
  append one row `WALL tick_rc=RC <mux JSON>` to
  ~/workspace/s0-soak-restart-ticks.jsonl, sleep 300, repeat.
- Tick file: ~/workspace/s0-soak-restart-ticks.jsonl, persistent in
  ~/workspace (survives /tmp wipes; ~/workspace persists across VM restarts).
  NOT /tmp, per W-SOAK recommendation R2.
- Launch, 19:00:53 +07: `setsid nohup bash ~/workspace/s0-soak-restart-tick.sh
  > ~/workspace/s0-soak-restart-tick.log 2>&1 < /dev/null & disown`.
- Tick loop pid: 27497, verified 19:01:05 +07 (`bash
  /home/hatch/workspace/s0-soak-restart-tick.sh`, in sleep 300) and again
  19:01:21 +07 in a FRESH exec session (PPID 27493, the exited launch shell,
  elapsed 00:27). The loop survived the launch session exiting, which is the
  detachment proof in practice. Note: the launch exec reported an output
  drain timeout because the runtime saw the detached children; the outputs
  were all delivered and the loop was verified alive afterwards, so nothing
  was re-launched and nothing was killed.
- First tick row, 19:00:54 +07: `2026-11-22 12:00:54 UTC tick_rc=0
  {"master_pid": 27441, "rc": 0, "restarted": false, "secs": 0.61,
  "stderr": "", "stdout": "", "via": "mux", "wall": "2026-11-22 19:00:54 +07"}`.
  Same master pid, via mux, 0.61s.
- Master re-check at tick launch, 19:01:05 +07: check alive true, rc 0,
  pid 27441. Tick log file (stdout of the loop): empty so far, no errors.
- Death visibility: if the master dies, the tick itself restarts it via
  ssh_mux.py run (ensure) and the row shows via=fresh-fallback plus
  restarted=true plus a new master_pid, so deaths stay visible in the tick
  rows instead of being hidden. No death has been recorded so far.
- Stop (for later, not done now): `pkill -f s0-soak-restart-tick.sh` stops
  the loop only, not the master. To stop the master: `python3
  scripts/ssh_mux.py stop`.

## 6. Short monitoring (step 5), t+6, 19:06:37 to 19:06:38 +07

Method: `sleep 300` then check plus mux run plus ps plus tick file plus socket
(exec session proc_26ae25ed68c9, started 19:01:30 +07, completed 19:06:38 +07,
duration 300785ms, exit 0). Verbatim outputs:

- Time: 2026-11-22 12:06:37 UTC MONITOR-T6, that is 19:06:37 +07.
- Master, `ps -o pid,ppid,etime,args -p 27441`: PID 27441, PPID 1, ELAPSED 06:02,
  cmdline identical to section 1 (ControlMaster=yes, ServerAliveInterval=15,
  same socket, same host). Same pid as at start, 6 min 02 s continuous life.
- Tick loop, `ps -o pid,ppid,sid,etime,args -p 27497`: PID 27497, PPID 27493,
  SID 27497, ELAPSED 05:43. SID equals its own pid, so it is a session leader
  in its own session, fully detached from every exec session that has since
  exited. Still running.
- Liveness, `python3 scripts/ssh_mux.py check`: `{"alive": true, "check_rc": 0,
  "pid": 27441, "wall": "2026-11-22 19:06:37 +07"}`, process rc=0.
- Mux sample, `python3 scripts/ssh_mux.py run -- echo SOAK-RESTART-T6-ALIVE`:
  `{"master_pid": 27441, "rc": 0, "restarted": false, "secs": 0.567,
  "stderr": "", "stdout": "SOAK-RESTART-T6-ALIVE\n", "via": "mux",
  "wall": "2026-11-22 19:06:38 +07"}`. Same pid, via mux, 0.567s.
- State file: `{"master_last_seen_wall": "2026-11-22 19:06:37 +07",
  "master_pid": 27441, "master_started_wall": "2026-11-22 19:00:35 +07"}`.
- Tick file, 2 rows, both tick_rc=0, both via mux, both master_pid 27441:
  row 1, 19:00:54 +07, secs 0.61; row 2, 19:05:55 +07, secs 0.527. Second tick
  landed 301 s after the first, on schedule (300 s sleep plus about 1 s run).
- Socket, `ls -la /tmp/cm-s0-*`: `srw------- 1 root root 0 Nov 22 12:00
  /tmp/cm-s0-james@100.70.92.52:22`. Still exists.
- ssh-mux.jsonl: no new rows since section 4 (no death, no restart). Only the
  two rows from the start (master_death prev 26834, master_restart new 27441).

Result: master ALIVE at t+6, same pid, zero deaths, zero restarts, 2 tick rows
plus 2 manual mux samples all via mux. This proves a fresh 6-minute continuous
run, NOT a 1-day soak. Longer life is for the tick rows to show over time,
and it still depends on the tick loop plus the VM staying up (section 7).

## 7. Watchdog cron proposal (NOT created, needs a decision)

- NOT created: no cron job and no scheduled job was made in this task, per
  the brief (not authorized).
- Why one is still wanted: the tick loop dies on a VM restart (two restarts
  happened today, about 07:51 and 17:11 +07), and nothing restarts the master
  after a reboot. A 5-minute watchdog cron calling `python3
  scripts/ssh_mux.py watchdog` from the repo would restart the master and
  log the death, exactly as W-SOAK recommended (R2). The tick loop covers
  idle death only while the VM stays up; the cron covers reboots too.
- Proposal for Muse tong to decide: create a 5-minute cron running
  `python3 /home/hatch/workspace/computer-use-wayland/scripts/ssh_mux.py
  watchdog` (single-shot check plus restart, same log rows as section 4).
  Until that decision, this run depends on the tick loop plus the VM staying up.

## 8. Limits kept

- No cron or scheduled job created. No laptop writes (no restart, no sync,
  no browser). No process killed. No live browser work. No ydotool.
- No self-grading: this log records evidence only. COORD-CLICK-7 verifies
  independently whether the master is alive and whether the run counts.
- No personal info in this file. No em dash or en dash in this file.
- Only this file is written in the repo. The tick script and tick rows live
  in ~/workspace (outside the repo) and are NOT committed.

## 9. Commit record

- Log commit: b2502b6a953b3d80e8b9ed12379133c2250c17ee ("W-SOAKRESTART: S0 soak
  master restarted as new run, pid 27441, alive t+6"), 1 file, 217 insertions,
  pushed ba4b298..b2502b6, verified with `git ls-remote origin todolist-push`
  at about 19:08 +07, local HEAD matches remote.
- Commit method: `git add -- improvements/w-soak-restart-log.md` then `git
  commit -m` (no pathspec on commit), per the hard git rule. The dirty
  results.json (another lane's) and other untracked drafts were NOT touched.
- Pre-commit checks: 0 em dash, 0 en dash in the file (Python count, 218
  lines at first write, 217 insertions committed); fetch plus pull --ff-only
  showed Already up to date at ba4b298 before staging.
- This section was filled after the push, committed separately (small commits,
  per the 19:03 team order).
