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

## 7. Soak test: 60 minutes, samples every 10 minutes (IN PROGRESS at interim commit)

Soak master: auto-master 13517 stopped cleanly (`-O exit`, rc=0), then a fresh
setsid/nohup master started 06:41:20 +07, pid 13662, check rc=0.
Soak runner: /tmp/probe-s0/soak.py, launched FULLY DETACHED
(`setsid nohup python3 /tmp/probe-s0/soak.py > /tmp/probe-s0/soak.log 2>&1 < /dev/null &`,
pid 13679). Plan: 7 samples at t=0,10,20,30,40,50,60 min plus a `true` keepalive
every 5 min (keeps idle gap under ControlPersist=600), each row logged to
/tmp/probe-s0/soak.jsonl with time, secs, rc, master liveness (check rc).

Sample t+0: 2026-11-22 06:41:28 +07, 0.894s, rc=0, check_rc=0.
Soak ends ~07:41 +07. Progress at 07:00 +07 (plain master, ControlPersist=600,
5-min keepalives, NO ServerAliveInterval):

```
t+0  sample    06:41:28  0.894s rc=0  (master 13662, fast mux)
t+5  keepalive 06:46:32  4.461s rc=0  (master now 15331: 13662 DEAD, fallback)
t+10 sample    06:51:38  5.596s rc=0  (master now 19847: 15331 DEAD, fallback)
t+15 keepalive 06:56:42  4.621s rc=0  (master now 23606: 19847 DEAD, fallback)
```

Every tick after t+0 paid full fresh cost. Master 19847 was confirmed dead by
direct check at 06:52:33 +07 (check rc=255, socket gone, no mux master in ps),
under 1 minute after its creation at 06:51:38. The plain master does not survive
even one 5-minute idle gap in this environment. Root cause isolated in section 13:
idle TCP is killed after ~60-90s somewhere on the VM to laptop path.

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

## 10. Verdict (interim, pending both soaks completing)

- S0 AS SPECIFIED (plain persistent mux, ControlPersist only) is NOT FEASIBLE as a
  saving at real cadences: the master dies after ~60-90s idle (section 13), so at
  5-10 minute spacing every use pays full fresh cost (~4.5s). The plain soak
  (section 7) shows 3/3 ticks after t+0 falling back to fresh.
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
- Open: the 60-minute soaks (plain, section 7, and keepalive, section 13) decide
  the long-run picture. If the keepalive master survives 60 min, the verdict above
  is final. If it dies too, S0 needs a master watchdog/restart loop on top.

## 11. Log commit record

- Interim log commit: 90eb8be40d42ffa35c72343778764a7affa4ea25 (2026-11-22 ~06:44 +07),
  pushed c3bf5e0..90eb8be, verified in remote history (ancestor of HEAD 8d0e38a
  after sibling pushes; git ls-remote origin todolist-push matched local HEAD
  7124f1e at verify time, before siblings pushed on top).
- Second interim log commit (idle-death experiment + soak progress): (filled after commit).
- Final log commit: (filled after both soaks complete).

## 12. Closing section (filled after both soaks complete)

- Plain soak samples (t+0..t+60): t+0 0.894s, t+5 4.461s, t+10 5.596s, t+15 4.621s,
  rest pending (ends ~07:41 +07).
- Keepalive soak-B samples: t+0 0.903s (master 25435), rest pending (ends ~08:00 +07).
- Master survived 60 min (plain): NO (died 3 times in the first 15 min).
- Master survived 60 min (keepalive): (pending).
- Final verdict: (pending soak-B).

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
10 min, keepalive every 5 min), t+0 sample 07:00:13 +07: 0.903s rc=0 master 25435.
Ends ~08:00:12 +07. If it survives, S0-with-keepalive is proven for 60 min.

Context note: at 06:52 +07 the owner went to sleep (headache) with full authority
to Muse (MEMORY.md update). If the laptop sleeps mid-soak, masters may die for
that unrelated reason; a fresh connect failing would be the tell. Fresh connects
still succeed at 07:00, so the laptop is awake as soak-B starts.
