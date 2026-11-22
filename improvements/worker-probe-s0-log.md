# Worker PROBE-S0 log: SPEED Step 0 feasibility probe (persistent SSH multiplexing)

Owner: Pham Tuan. Branch: todolist-push. Worker: PROBE-S0, for COORD-CLICK-3.
Started: 2026-11-22 06:35:59 +07 (Asia/Ho_Chi_Minh). All times below are wall-clock +07 unless noted.
Method: live tests on the owner laptop (omarchy, 100.70.92.52) via SSH. Timing probes only.
No GUI driving, no changes to owner files, no touching Zen/Brave/chats. No ydotool used anywhere.

Standing rules recorded here, as briefed:
- No-self-healing rule (2026-11-22 05:56, owner): when Muse itself errors or fails, an
  INDEPENDENT worker investigates, names the cause and finds the fix. Muse does not
  self-diagnose or self-fix. This probe only measures and reports; it does not fix S0.
- First-principles rule (2026-11-22 06:01, owner): ask whether the original design is
  right at all, drop what is surplus, rewrite when evidence shows it is needed.
- Evidence standard (owner, Lauren Tan standard): every claim carries the test command,
  its output, the commit hash and the time log. A proposal with no measured evidence
  does not count as feasible.

## 0. Setup

- Shared script NOT modified: ~/workspace/ssh-laptop.sh (read-only for this probe).
  It runs: ssh -o BatchMode=yes -o ConnectTimeout=25 -o StrictHostKeyChecking=accept-new
  -o IdentitiesOnly=yes -o ProxyCommand="python3 /home/hatch/workspace/tailscale-proxy.py %h %p"
  -i /home/hatch/.ssh/id_ed25519 james@100.70.92.52
- TEST wrapper (probe only): /tmp/probe-s0/ssh-mux-test.sh, same base options plus
  -o ControlMaster=auto -o ControlPath=/tmp/cm-probe-%r@%h:%p -o ControlPersist=600.
  Socket: /tmp/cm-probe-james@100.70.92.52:22.
- Timing harness: /tmp/probe-s0/measure.py (python time.perf_counter around subprocess,
  records secs + rc per sample, appends /tmp/probe-s0/results.jsonl).
- Master control: /tmp/probe-s0/master-ctl.sh {start|check|stop} (same base options,
  -O check / -O exit for liveness; liveness judged by return code, not speed).
- Local ssh: OpenSSH_9.6p1 Ubuntu-3ubuntu13.20. Runner uid 0 (root).
- Laptop check 06:36:13 +07: `~/workspace/ssh-laptop.sh 'echo ALIVE; hostname; date'`
  returned ALIVE, omarchy, rc=0. No stale /tmp/cm-probe-* socket at start (clean start).

## 1. Fresh SSH baseline: 10 samples, no-op `true`, via plain ssh-laptop.sh

Command: `PROBE_OUT=/tmp/probe-s0/results.jsonl python3 /tmp/probe-s0/measure.py ~/workspace/ssh-laptop.sh fresh-true 10 true`
Run: 2026-11-22 ~06:36:30 +07, total wall 46.8s. Output (verbatim):

```
fresh-true 1/10: 4.561s rc=0
fresh-true 2/10: 4.878s rc=0
fresh-true 3/10: 4.800s rc=0
fresh-true 4/10: 4.711s rc=0
fresh-true 5/10: 4.559s rc=0
fresh-true 6/10: 4.555s rc=0
fresh-true 7/10: 4.682s rc=0
fresh-true 8/10: 4.576s rc=0
fresh-true 9/10: 4.454s rc=0
fresh-true 10/10: 4.891s rc=0
fresh-true SUMMARY n=10 mean=4.667 min=4.454 max=4.891 rcs=[0 x10]
```

Fresh mean 4.667s, median 4.629s. Matches SPEED-REVIEW's fresh samples (4.43/4.93/4.48s).

## 2. Master start method matters: `ssh -M -f -N` master REFUSES mux sessions

Master 1, started 06:37:28 +07 with `master-ctl.sh start`
(`-o ControlMaster=yes -M -f -N`, i.e. ssh -f backgrounding):
socket existed, `-O check` rc=0, "Master running (pid=10759)".

Mux batch 1 (10x `true` via mux wrapper, ~06:38 +07):

```
mux-true 1/10: 5.165s rc=0 err='Master refused session request: Permission denied'
mux-true 2/10: 4.321s rc=0 err='Master refused session request: Permission denied'
mux-true 3/10: 4.542s rc=0 err='Master refused session request: Permission denied'
mux-true 4/10: 4.479s rc=0 err='Master refused session request: Permission denied'
mux-true 5/10: 5.461s rc=0 err='Master refused session request: Permission denied'
mux-true 6/10: 1.271s rc=0 err=''
mux-true 7/10: 1.298s rc=0 err=''
mux-true 8/10: 1.208s rc=0 err=''
mux-true 9/10: 1.217s rc=0 err=''
mux-true 10/10: 1.472s rc=0 err=''
```

Samples 1-5: master refused the session, client fell back to a fresh connect
(slow, ~4.5s, but rc=0, correct). Samples 6-10: fast mux (~1.2-1.5s).
After the batch, `-O check` reported a DIFFERENT master: "Master running (pid=11206)".
So master 10759 died mid-batch (within ~60s of starting, far short of ControlPersist=600)
and a client auto-created replacement master 11206, which then accepted mux sessions.

Reproduction, master 2, started 06:38:41 +07, same `-M -f -N` method, pid 11573,
check rc=0. Mux batch `mux-true-b`, 5 samples, new exec call:

```
mux-true-b 1/5: 5.077s rc=0 err='Master refused session request: Permission denied'
mux-true-b 2/5: 4.322s rc=0 err='Master refused session request: Permission denied'
mux-true-b 3/5: 5.370s rc=0 err='Master refused session request: Permission denied'
mux-true-b 4/5: 5.086s rc=0 err='Master refused session request: Permission denied'
mux-true-b 5/5: 4.848s rc=0 err='Master refused session request: Permission denied'
mux-true-b SUMMARY n=5 mean=4.941 min=4.322 max=5.370 rcs=[0 x5]
```

5/5 refused. And when the next command ran `master-ctl.sh stop`, it returned rc=255
"Control socket connect: No such file or directory": master 11573 was ALREADY dead
by then (lived under ~2 minutes). So the `-M -f -N` master form is doubly broken here:
it refuses every mux session AND dies on its own within ~1-2 minutes.

FINDING F1 (measured, reproduced 2/2): an explicitly started `ssh -M -f -N` master
does NOT multiplex on this VM-to-laptop path. Every session falls back to fresh cost.
Any S0 implementation that starts its master with `ssh -f` will measure ~4.5-5.4s
per connection and deliver zero saving. This is a separate failure from the 0.01s
failed-fast trap D1 caught.

## 3. Working master form: setsid nohup, no -f

Master 3, started 06:39:30 +07:
`setsid nohup ssh <same base opts> -o ControlMaster=yes -o ControlPath=/tmp/cm-probe-%r@%h:%p -o ControlPersist=600 -N james@100.70.92.52 > /tmp/probe-s0/master-A.log 2>&1 < /dev/null &`
(disowned; no -f flag). Check rc=0, pid 12018.

Mux batch `mux-true-A`, 3 samples: 0.985s, 1.577s, 1.249s, all rc=0, no refusal.
Mean 1.270s. Check rc=0 after. Same master then served the official batch below,
proving the setsid form survives across exec calls (unlike the -f form).

FINDING F2 (measured): the setsid/nohup master WITHOUT -f accepts mux sessions
reliably. S0 must start its master this way (or let the first ControlMaster=auto
client create it, which also worked: pid 11206, see section 2), never with `ssh -f`.

## 4. Multiplexed no-op: official 10 samples on healthy master 12018

Command: `PROBE_OUT=/tmp/probe-s0/results.jsonl python3 /tmp/probe-s0/measure.py /tmp/probe-s0/ssh-mux-test.sh mux-true 10 true`
Run: ~06:40 +07. Check rc=0 before and after ("Master running (pid=12018)" both times).

```
mux-true 1/10: 0.753s rc=0
mux-true 2/10: 1.561s rc=0
mux-true 3/10: 1.233s rc=0
mux-true 4/10: 1.265s rc=0
mux-true 5/10: 2.372s rc=0
mux-true 6/10: 1.350s rc=0
mux-true 7/10: 1.328s rc=0
mux-true 8/10: 1.294s rc=0
mux-true 9/10: 1.360s rc=0
mux-true 10/10: 1.307s rc=0
mux-true SUMMARY n=10 mean=1.382 min=0.753 max=2.372 rcs=[0 x10]
```

Healthy-mux pooled mean (18 accepted samples: this batch of 10, mean 1.382s,
plus mux-true-A 3 samples, mean 1.270s, plus batch-1 accepted samples 6-10,
1.271/1.298/1.208/1.217/1.472, mean 1.293s): 24.100/18 = 1.339s, median ~1.30s.
Sample 5 (2.372s) is an outlier; a concurrent probe (PROBE-S1, see section 8) was
running fresh SSH connects at the same time, which is the likely noise source.

## 5. Residual cost decomposition: what the ~1.3s consists of

All on healthy master 12018 (or its setsid successor), rc=0 throughout:

- `mux-check-only` (5x `-O check`, no remote exec at all, client plus socket only):
  0.088/0.020/0.075/0.021/0.087s, mean 0.058s. The multiplexing layer itself is ~0.06s.
- `mux-echo` (5x `echo PROBE-S0`, remote exec with output): mean 1.201s
  (0.799/1.457/1.245/1.246/1.257).
- `mux-bash-c` (5x `bash -c true`, explicit shell spawn): mean 1.283s
  (1.127/1.313/1.297/1.352/1.326).
- `mux-triple-true` (3x `true; true; true` in ONE session): mean 1.206s
  (0.851/1.299/1.467).

FINDING F3 (measured): the residual ~1.2-1.3s is a PER-SESSION cost, not per-command
and not shell startup. Three commands in one session cost the same as one
(1.206s vs 1.382s). An explicit extra shell adds nothing (bash -c true 1.283s
vs plain true 1.382s). The mux layer itself is only ~0.06s. So ~1.2s sits in
server-side session setup per new channel: sshd fork plus session negotiation
plus the round trips through the Tailscale proxy path. Batching commands into
one session is free; every NEW session costs ~1.2s no matter what it runs.
Consequence for S0: the saving is real but capped at ~3.3s per connection, and
act-now/observe code that opens a session per action still pays ~1.3s per action.

## 6. Master-death test: fallback is slow but correct, and self-heals

Master 12018, killed 06:40:59 +07 with `kill -TERM 12018`. After 2s:
ps showed no mux master, socket file gone, `-O check` rc=255
("Control socket connect: No such file or directory"). Dead, confirmed by rc.

One mux `true` after death: 4.269s, rc=0, no error. Fallback to a fresh connect,
slow but CORRECT (not the 0.01s rc=255 failed-fast trap).
After the fallback, `-O check` rc=0 and a NEW master existed, pid 13517
(socket recreated 23:41 UTC). ControlMaster=auto self-heals: the fallback
connection becomes the new master.

FINDING F4 (measured): master death costs one slow (~4.3s) but correct connection,
then service resumes at mux speed with a fresh auto-master. No manual recovery
needed IF clients use ControlMaster=auto. A client using ControlMaster=no or a
hardcoded -S path with no auto fallback would instead fail outright.

## 7. Soak test: 60 minutes, samples every 10 minutes (plain master; cut short by VM restart, section 14)

Soak master: auto-master 13517 stopped cleanly (`-O exit`, rc=0), then a fresh
setsid/nohup master started 06:41:20 +07, pid 13662, check rc=0.
Soak runner: /tmp/probe-s0/soak.py, launched FULLY DETACHED
(`setsid nohup python3 /tmp/probe-s0/soak.py > /tmp/probe-s0/soak.log 2>&1 < /dev/null &`,
pid 13679). Plan: 7 samples at t=0,10,20,30,40,50,60 min plus a `true` keepalive
every 5 min (keeps idle gap under ControlPersist=600), each row logged to
/tmp/probe-s0/soak.jsonl with time, secs, rc, master liveness (check rc).

Sample t+0: 2026-11-22 06:41:28 +07, 0.894s, rc=0, check_rc=0.
Full confirmed table (12 ticks, t+0..t+55; the t+60 sample due ~07:42:31 is
UNCONFIRMED, see the VM restart note in section 14):

```
t+0  sample    06:41:28  0.894s rc=0  (master 13662, fast mux)
t+5  keepalive 06:46:32  4.461s rc=0  (master now 15331: 13662 DEAD, fallback)
t+10 sample    06:51:38  5.596s rc=0  (master now 19847: 15331 DEAD, fallback)
t+15 keepalive 06:56:42  4.621s rc=0  (master now 23606: 19847 DEAD, fallback)
t+20 sample    07:01:48  5.322s rc=0  (master now 28155: 23606 DEAD, fallback)
t+25 keepalive 07:06:54  5.929s rc=0  (master now 35198: 28155 DEAD, fallback)
t+30 sample    07:12:00  5.707s rc=0  (master now 42080: 35198 DEAD, fallback)
t+35 keepalive 07:17:06  5.603s rc=0  (master now 52094: 42080 DEAD, fallback)
t+40 sample    07:22:11  4.920s rc=0  (master now 56446: 52094 DEAD, fallback)
t+45 keepalive 07:27:16  4.867s rc=0  (master now 60474: 56446 DEAD, fallback)
t+50 sample    07:32:21  5.027s rc=0  (master now 64331: 60474 DEAD, fallback)
t+55 keepalive 07:37:26  4.497s rc=0  (master now 66004: 64331 DEAD, fallback)
t+60 sample    ~07:42:31  UNCONFIRMED (log wiped by VM restart, section 14)
```

11 consecutive fallback ticks after t+0, each with a NEW master pid: the plain
master died 11 times in 55 minutes and never once survived a 5-minute gap.
Fallback mean 5.141s (56.550/11), slightly above the fresh baseline 4.667s
(fallback plus auto-master creation plus concurrent load). At 5-10 minute
cadence the plain mux delivers ZERO saving: every use costs a fresh connect.
Root cause isolated in section 13: idle TCP is killed after ~60-90s somewhere
on the VM to laptop path.

NOTE (soak harness bug, mine): soak.py reads the master pid with
`ps -eo pid,args | grep 'ssh: /tmp/cm-probe-'`, which matches only AUTO-created
masters (their cmdline is `ssh: /tmp/cm-probe-... [mux]`). A setsid -N master shows
its full ssh command line instead, so soak rows record master_pid as empty even
though the master is alive (check_rc=0 proves liveness). Master pid continuity is
therefore tracked by my manual polls (ps aux) at each check-in, not by the soak
rows. Timing and rc values in the soak rows are unaffected.

## 8. Concurrent activity noted (not fought, timing probes are harmless)

During this probe the VM and laptop were busy with sibling work. Seen in ps output:
- PROBE-S1 (sibling SPEED probe): master pid 13600,
  `ssh -M -S /tmp/cm-probe-s1-james@100.70.92.52:22 -o ControlPersist=600 -fN ...`,
  i.e. the same `-fN` master form section 2 shows refuses mux sessions.
- PROBE-S2 (sibling): committing improvements/worker-probe-s2-log.md (a1a672d).
- Other workers polling fcc/codex discuss logs on the laptop via ssh-laptop.sh.
This concurrency is a plausible noise source for the 2.372s mux outlier (section 4).
No interference with the measurements beyond that; no fight, no shared files touched.

## 9. Computed comparison (from the measured means above)

- Fresh mean: 4.667s (n=10, section 1).
- Healthy mux mean: 1.339s (n=18 accepted samples, section 4).
- Saving per connection: 4.667 - 1.339 = 3.328s.
- Ratio: 4.667 / 1.339 = 3.49x.
- Per act-now (3 connects): fresh 14.00s vs mux 4.02s, saving 9.98s.
- Per observe (2 connects): fresh 9.33s vs mux 2.68s, saving 6.66s.
- SPEED claim 460x (fresh ~4.6s vs mux 0.01s): REFUTED. The 0.01s figure is the
  failed-fast trap D1 caught (rc=255, master down); no live mux sample here or in
  D1/D3 came anywhere near 0.01s. Best single live mux sample: 0.753s.
- D1/D3 (~3.5-5x, mux ~0.94-1.29s): CONFIRMED. This probe lands at 3.49x, mux 1.339s,
  squarely in their range.

## 10. Verdict (FINAL, 07:52 +07; soaks cut short by VM restart, see section 14)

- S0 AS SPECIFIED (plain persistent mux, ControlPersist only) is NOT FEASIBLE as a
  saving at real cadences: the master dies after ~60-90s idle (section 13), so at
  5-10 minute spacing every use pays full fresh cost (~4.5-5.9s). The plain soak
  (section 7) shows 11/11 ticks after t+0 falling back to fresh.
- S0 WITH ONE ADDED OPTION (`-o ServerAliveInterval=15 -o ServerAliveCountMax=3`
  on the master) is FEASIBLE: same master survived 300s idle with mux speed at
  every sample (section 13, idle-B). Real delivery then: ~3.5x, ~3.3s saved per
  connection, residual ~1.3s per session that no multiplexing removes.
- Two hard requirements for the S0 implementation, both measured:
  (a) start the master with setsid/nohup (or let ControlMaster=auto create it),
  never `ssh -M -f -N` (refuses sessions, dies in ~1-2 min);
  (b) clients use ControlMaster=auto so master death self-heals with one
  slow correct fallback instead of a hard failure;
  (c) the master MUST carry ServerAliveInterval (15s) or it dies idle.
- Open: the 60-minute keepalive soak was NOT completed (40 min confirmed,
  section 13). If the coordinator wants a clean 60-minute keepalive run it is a
  fresh 60-minute job, not a resume. The verdict does not depend on it.

## 11. Log commit record

- Interim log commit: 90eb8be40d42ffa35c72343778764a7affa4ea25 (2026-11-22 ~06:44 +07),
  pushed c3bf5e0..90eb8be, verified in remote history (ancestor of HEAD 8d0e38a
  after sibling pushes; git ls-remote origin todolist-push matched local HEAD
  7124f1e at verify time, before siblings pushed on top).
- Second interim log commit: 4f378b0fdeef4917328f4e9073e3c2a8572e69d8
  (2026-11-22 ~07:01 +07), pushed 8008662..4f378b0, LOCAL == REMOTE at verify time.
- Final log commit: (filled after commit; see section 14).

## 14. VM restart cut both soaks short (07:51 +07) + final notes

- At ~07:51:37 +07 the VM restarted (uptime 1 min on recovery). /tmp was wiped:
  /tmp/probe-s0/ (wrappers, measure.py, results.jsonl, soak logs, idle logs),
  all /tmp/cm-* sockets, all ssh master processes dead. The plain soak runner and
  the soak-B runner were both killed. No soak processes remain (pgrep empty).
- What was lost: plain soak t+60 sample (due ~07:42:31, before the restart, but its
  log line is unverifiable) and soak-B ticks t+45..t+60 (t+45/t+50 may have run,
  t+55/t+60 never ran). All numbers in sections 7 and 13 are from tool outputs
  delivered into this session BEFORE the restart, not reconstructed from memory:
  plain soak 12 confirmed ticks, soak-B 9 confirmed ticks.
- What survived: this log file (~/workspace persists) and both interim commits,
  90eb8be and 4f378b0, both verified ancestors of origin/todolist-push.
  Nothing on the laptop was changed at any point; no cleanup needed there.
  No masters remain on the VM to stop.
- Meanwhile the fleet moved on: final direction landed 06:58 +07 (MEMORY.md,
  commit e05fc58): step 0 is S0 at 3.49x (corrected from 460x). An S0 implementation
  commit 4985b45 ("S0-IMPL: SPEED step 0 SSH mux + measurement bundle") landed on
  the local line during the soak. This probe's numbers are the adopted step-0
  figures. Whether that implementation carries ServerAliveInterval (finding F5
  says it must) is for its reviewer to check; this probe only measures and reports.
- Honest scope limit: the 60-minute keepalive soak was NOT completed (40 min
  confirmed). If the coordinator wants a clean 60-minute keepalive run, it is a
  fresh 60-minute job from a new master start, not a resume: the restart broke
  continuity. The verdict does not depend on it: 9/9 fast ticks over 40 min on
  one pid, plus the controlled 300s idle-B test, already prove the keepalive
  master survives real idle gaps, and 11 consecutive plain-master deaths prove
  the un-fixed form does not.

## 12. Closing section (FINAL, 07:52 +07, after VM restart cut both soaks short)

- Plain soak (section 7): 13 ticks planned, 12 confirmed (t+0..t+55, 55 min).
  6 confirmed samples (t+0,10,20,30,40,50): 0.894s then 5.596/5.322/5.707/4.920/5.027s.
  11/11 ticks after t+0 were fresh-connect fallbacks with a new master pid each time.
  Master survived 60 min (plain): NO. Died 11 times in 55 min.
- Keepalive soak-B (section 13): 13 ticks planned, 9 confirmed (t+0..t+40, 40 min),
  all on the SAME master pid 25435, all rc=0, mean 0.958s (8.625/9), samples-only
  mean 0.963s (t+0,10,20,30,40). Master survived 40 min (keepalive): YES, 9/9 ticks.
  Ticks t+45..t+60 never ran: the VM restart at ~07:51 killed the runner first.
- VM restart (section 14): the 60-minute soak-B was NOT completed. The 40-minute
  keepalive run plus the 300s controlled idle-B test is the evidence on record.
  A clean 60-minute keepalive re-run is possible if the coordinator wants it;
  this probe does not claim a completed 60-minute soak.
- Final verdict: S0 is FEASIBLE ONLY with ServerAliveInterval on the master
  (plus setsid/nohup start, never `ssh -f`, plus ControlMaster=auto clients).
  As specified without keepalives it delivers zero saving at real cadences.
  With keepalives it delivers 3.49x, 3.33s saved per connection, residual ~1.3s
  per session. 460x is refuted. These numbers match D1/D3 and are now the adopted
  step-0 figures in the final direction (MEMORY.md 06:58, commit e05fc58).

## 13. Idle-death experiment (added 07:00 +07): plain master dies idle, keepalive master lives

Cause hunt for the soak deaths (section 7). Two masters on separate sockets,
started in parallel 06:53:27 +07, same setsid/nohup form, one difference:
- A (plain): /tmp/cm-idle-A-..., no extra opts. Master pid 21199 at start.
- B (keepalive): /tmp/cm-idle-B-..., `-o ServerAliveInterval=15 -o ServerAliveCountMax=3`.
  Master pid 21189 at start.
Each timed `true` at t=0, after 90s idle, after 300s total idle. Full logs:
 /tmp/probe-s0/idle-A.log, /tmp/probe-s0/idle-B.log. Results (verbatim):

```
IDLE A: t0   06:53:33  1.141s rc=0  (master 21199, fast mux)
IDLE A: t90  06:55:10  5.582s rc=0  (master now 23325: 21199 DEAD, fallback)
IDLE A: t300 06:58:45  4.861s rc=0  (master now 24064: 23325 DEAD, fallback)
IDLE B: t0   06:53:33  1.135s rc=0  (master 21189, fast mux)
IDLE B: t90  06:55:05  1.172s rc=0  (master 21189, SAME, alive)
IDLE B: t300 06:58:36  0.883s rc=0  (master 21189, SAME, alive)
```

FINDING F5 (measured, controlled A/B, same minute, same path): a plain master dies
after 60-90s idle; the transport is killed somewhere on the VM to laptop path
(idle TCP timeout in the egress/Tailscale proxy chain; the proxy itself has no
documented idle timeout in its 82 lines, only a 30s connect timeout, so the kill
is downstream of it). ServerAliveInterval=15 defeats it completely: the same
master (pid 21189) served all three samples at mux speed through 300s idle.
ControlPersist=600 is IRRELEVANT here: the master never lives long enough to
reach its persist timeout. Any S0 without transport keepalives is dead on arrival
at any cadence slower than ~1 minute.

Follow-up: soak-B (ServerAliveInterval=15 master, own socket /tmp/cm-soakb-...,
master pid 25435, started 07:00:06 +07, check rc=0). Runner /tmp/probe-s0/soak-b.py,
launched fully detached, same 60-min cadence as the plain soak (7 samples every
10 min, keepalive every 5 min). Confirmed ticks (9, t+0..t+40, all master 25435):

```
t+0  sample    07:00:13  0.903s rc=0
t+5  keepalive 07:05:14  1.013s rc=0
t+10 sample    07:10:16  1.170s rc=0
t+15 keepalive 07:15:16  0.867s rc=0
t+20 sample    07:20:17  0.909s rc=0
t+25 keepalive 07:25:18  0.967s rc=0
t+30 sample    07:30:19  0.919s rc=0
t+35 keepalive 07:35:20  0.962s rc=0
t+40 sample    07:40:21  0.915s rc=0
t+45..t+60     NEVER RAN (VM restart ~07:51, section 14)
```

Mean 0.958s over 9 ticks, same pid throughout: the keepalive master survived
40 minutes and 9 uses with zero deaths and zero fallbacks. Contrast the plain
soak: 11 deaths in 55 min on the same path at the same time of day.

Context note: at 06:52 +07 the owner went to sleep (headache) with full authority
to Muse (MEMORY.md update). If the laptop sleeps mid-soak, masters may die for
that unrelated reason; a fresh connect failing would be the tell. Fresh connects
still succeed at 07:00, so the laptop is awake as soak-B starts.
