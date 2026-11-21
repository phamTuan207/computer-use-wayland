# Worker SPEED-REVIEW log: independent first-principles latency review of computer-use
# Task start 06:03 +07 Sun 2026-11-22. All times wall-clock Asia/Ho_Chi_Minh + elapsed from task start.
# Independent: no coordination with other workers, no following the current method, question everything.
# No em/en dashes. No personal info. Evidence with every claim.

## 06:03 task start + what I read first
- Brief: from first principles, what would make total wall time 10x smaller? What should not exist?
- Read in full: improvements/worker-f2b-live-session-log.md (F2b proof run 00:19-00:20),
  improvements/worker-f1a-activation-log.md (F1a activation + 5-step proof),
  scripts/first_action.py (719 lines, the act-now path), scripts/code_exec.py head + API list,
  scripts/fastpath.py head, improvements/live-test-log.md sections on the 10x review (lines 1070-1105, 1550-1570).
- Live probes run 06:04-06:06 (cheap, safe, no GUI driving): one in-session laptop script
  (python startup, observe cost, listening ports, relay socket, code-exec flag) + fresh-SSH vs
  ControlMaster timing (3 samples each) + repo checks (Pick 1 commits, two_vision_bench.py on main).

## 1. THE MEASURED BUDGET (my probes, 06:04-06:06 +07)
### 1a. Transport: a fresh SSH connection costs 4.6s; a multiplexed one costs 0.01s
- Fresh `ssh-laptop.sh true`, 3 samples, python-timed: 4.43s, 4.93s, 4.48s. Mean 4.6s.
  Path: VM exec -> tailscale-proxy.py (HTTPS CONNECT to runtime egress proxy, port 3130)
  -> Tailscale -> laptop SSH handshake. Every fresh ssh-laptop.sh call pays this.
- Same no-op over a ControlMaster persistent connection (master started with -M -S /tmp/cm-speed.sock,
  3 samples): 0.01s, 0.01s, 0.01s. 460x cheaper. Master setup worked first try; exit clean.
- Consequence per agent step in the CURRENT loop (every step is fresh SSH + scp):
  - One observe from the VM: SSH out 4.6s + observe on laptop 0.25s + scp image back 4.6s = ~9.5s.
  - One act-now from the VM: scp actions in 4.6s + SSH run 4.6s + scp after-image back 4.6s = ~13.8s
    of connects + ~1.7-2.9s laptop work = ~16s per call.
  - CL2-MSG (4m03s, 3 act-now calls + 3 observes + 3 scp-backs, ~9 SSH connections):
    transport alone is roughly 60-90s of the 243s. The rest is model think + harness overhead.
  - F2b order-to-overlay 12.262s = dispatch 11.620s (95%) + observe 0.233s + Python 0.060s
    + overlay 0.349s. The overlay itself is 349ms; the dispatch is the cost.

### 1b. Laptop-side mechanism is cheap (all sub-second except the session spawn)
- Observe screen on laptop: capture_ms 26.5ms, command real 0.255s (probe 06:04:11,
  image 1920x1200, 305343 bytes). Window observe similar (F2b: 0.233s).
- act-now laptop-side envelope totals (live runs): 1672ms, 1729ms, 2850ms (1-5 action batches).
  Overlay acquire 315-349ms. Session start 0.4s (broker, H1-OPT driver log) to 1.8-2.1s (10x review).
  Python startup ~0.06s (F2b) to ~0.25s.
- DOM grounding (clone2 batch 7, measured live): one-shot rect sweep, all 66 element coordinates,
  Marionette median 0.030s; one snapshot drove 5 clicks, all 5 hit; verify by one DOM read 0.005-0.015s.
  DOM coordinates cost ~0.03s where a vision read costs a full image + model inference.
- Relay: session_remote.py is a reconnectable single-owner Unix-socket broker; relay PID 1821 alive.
  Socket /run/user/1000/agent-computer-use/cursor-guard.sock exists. NO TCP listener for it:
  `ss -ltnp` on the laptop shows no computer-use port (only fcc-server 8082, opencode 4096,
  Zen 2828, chromium 40783, DNS, SSH 22). The VM can reach the relay ONLY through SSH.

### 1c. The 87.8% gap, re-checked (not re-measured; the prior measurement has a known hole)
- 10x review (live-test-log.md): tc02-t1 gap 722.955s (87.8% of 823s) vs service 37.721s (4.6%);
  session start 1.8-2.1s, negligible. Verdict then: the bottleneck is the serialized
  think-observe-think loop, NOT broker/transport/observation. Amdahl bound: making every local
  transaction free improves t3 only 1.15x.
- The honest limit, stated in the same review: "logs cannot split the gap into model inference vs
  image reading vs SSH (no inference timestamps; L3 helper runs session_remote.py locally, so no
  SSH hop is even measured)". The 87.8% was measured with a LOCAL helper. It does not contain
  the SSH tax at all.
- H1-OPT per-step timings (driver.log, local broker): gaps between executor requests 13s, 23s, 42s,
  2m48s, 20s, 12s, 51s, 1m11s, 47s, 45s, 15s; broker requests return in 0.1-0.5s. Locally, the
  gap really is think time, not transport.
- MY CORRECTION: the "transport is not the bottleneck" verdict does not transfer to the CURRENT
  VM-agent path. The current loop pays ~9.5s per observe and ~16s per act-now, of which ~85-90%
  is SSH connect overhead that the 10x review never measured. In the current path transport is
  roughly 25-35% of wall time (CL2-MSG estimate), not 4.6%. Cutting transport to zero is worth
  about 1.6x on a CL2-MSG-class task by itself, and it is nearly free. It is not 10x alone,
  and the 10x review was right that fewer model calls is the main lever. Both are true at once:
  the review measured the local loop correctly, and the production loop has since moved to a
  remote loop where transport is a second, unmeasured tax.

## 2. WHAT SHOULD NOT EXIST (first principles)
### 2a. A fresh SSH connection per call. Cost 4.6s, paid 3 times per act-now, twice per observe.
- First principle: a connection is setup, not work. Setup paid per unit of work is pure waste.
- It should not exist. One persistent connection, multiplexed, for the whole task (measured 0.01s).
- Proof it works: ControlMaster test above, 3/3 at 0.01s. Fail-safe: if the master dies, the next
  command falls back to a fresh connect (slow but correct). Open question I did NOT prove: whether
  a master survives the historical "SSH dies ~30s" behaviour over hours; a 1-day soak test is owed.

### 2b. scp round trips for JSON files. Cost: one fresh SSH connection each (4.6s).
- First principle: the actions file and the observation JSON are a few hundred bytes. Shipping them
  as files over separate SSH connections is the most expensive possible way to move them.
- They should not exist as separate transfers. Send the JSON over the same persistent channel
  (stdin over the multiplexed SSH, or a broker RPC). The VM already has the observation JSON in
  memory; scp-ing it back and forth is ceremony.

### 2c. A fresh session (guardian + driver spawn) per act-now batch.
- first_action.py attempt_session() spawns `python3 cu.py session -- python3 cu.py act ...` as a
  subprocess on every call, with a 20s deadline. Session start is 0.4-2.1s of a 1.7-2.9s call,
  and the 20s deadline is a whole failure mode (timeout never falls back, per council 1 B1).
- First principle: a session is a lease on the seat for the duration of a task, not per batch.
  It should live for the whole task; batches go to the persistent session through the relay broker
  that already exists (session_remote.py, relay PID 1821 alive). act-now spawning a session per
  batch is using the broker's tool without the broker.
- Saving: ~0.4-1s per call plus the timeout failure mode. Small alone; it matters because it is
  per call, and because it is the part that can wedge (guardian startup failure was the F1 root cause).

### 2d. The screen-scope after-capture. Cost: one extra observe (~0.25s) plus a defective artifact.
- Proven independently by CL1SWEEP-FAIL-INVEST (commit 5f5a2fd): first_action.py ALWAYS captures
  the envelope `after` with cu.observe_screen(..., max_width=1920), regardless of input scope,
  overwriting desktop_act's scope-matching after-capture (cu.py:2083-2091). Every act-now
  after-image is screen-scoped by construction; reusing one for a key/type step ALWAYS fails.
- First principle: an artifact that cannot be chained and misleads the next step should not be
  produced in that form. Either scope-match it or stop producing it (the next step re-observes
  anyway). The investigator's best shape stands: return BOTH `after` (scope-matching, chainable)
  and `after_screen` (verification only, documented non-chainable).

### 2e. The per-action model call (the 87.8%). Cost: everything else combined is small next to it.
- First principle: the model is the scarcest resource in the loop (seconds to minutes per call,
  vs milliseconds for mechanism). A loop that spends one model call per action spends the
  scarcest resource at the highest frequency. That is backwards.
- It should not exist as the default. The replacement is already built and already won: code-exec
  (scripts/code_exec.py, Track 2 Pick 1 M1, merged, commits 714e4f9, 84b88bb, 2e2aeff): one short
  program per model call, persistent local interpreter, allowlisted API (windows, observe, act,
  dom_*), verification asserts, same safety invariants as the normal loop.
- THE GAP BETWEEN DECIDED AND DONE: code-exec is behind the opt-in flag CU_CODE_EXEC=1, and the
  flag is OFF in the live path. My probe 06:04: `env | grep CU_CODE` on the laptop returned nothing;
  the installed tree has code_exec.py and the cu.py subparser, but no live run uses it: the F2b log
  mentions act-now 15 times and code-exec 0 times; CL2-MSG and CL1-SWEEP all ran act-now. The 10x
  review ADOPTED checkpointed scripts; the implementation landed; the live loop never switched on.
  That is the single biggest free win available: flip the flag and drive the live loop through
  code-exec, instead of debating the next optimization.

### 2f. The 120s observation freshness window as a design constraint.
- The window exists because vision-derived coordinates go stale. DOM rects do not go stale the same
  way: they are re-read in 0.030s. A loop grounded in DOM does not need a 120s window, a
  re-observe, or a stale-refusal path (G28). The window is a patch for vision-based coordinates,
  not a law of the system. With DOM grounding + DOM verification, freshness stops being a
  constraint and becomes a cheap re-read.

## 3. THE BREAKTHROUGH, CONCRETELY, IN THREE STEPS
### Step 0 (no rewrite, do it now): persistent SSH multiplexing. Measured 460x on connect cost.
- Change ssh-laptop.sh to use ControlMaster: `-o ControlMaster=auto -o ControlPath=/tmp/cm-%r@%h:%p
  -o ControlPersist=600` plus a tiny watchdog that restarts the master if it dies.
- Expected, from my measurements: per act-now 16s -> ~2s (laptop work only); per observe 9.5s -> ~0.3s.
  Per-task wall roughly 1.6x better on a CL2-MSG-class task, zero code changes to agent logic.
  Risk: master lifecycle over hours is unproven (see honest limits). Mitigation: fall back to fresh
  SSH on any multiplex failure; the fallback is the current behaviour, so nothing gets worse.

### Step 1 (small rewrite): act-now over the persistent relay broker.
- Talk to the relay (Unix socket, already alive) instead of spawning `cu.py session` per batch.
  JSON goes over the same channel (no scp). After-capture scope-matched or dropped (2d).
- Expected: per-batch mechanism ~0.5s (overlay 0.35s is then the largest single item, and the pill
  itself is worth questioning next: a 350ms indicator per batch is a tax the owner never asked to
  pay per batch; a session-level pill, acquired once per task, is the first-principles shape).
- This is the 10x review's DEFERRED item ("persistent broker-client connection"). The deferral
  reason then was that transport was not the bottleneck locally. That reason no longer holds for
  the remote VM-agent path (section 1c). Un-defer it.

### Step 2 (the 10x path, already built, switch it on): DOM-first + code-exec + checkpoint verification.
- One DOM snapshot (0.030s) grounds ALL coordinates. One code-exec program (1 model call) runs ALL
  actions. One DOM verification read (0.005-0.015s) plus one vision check at the end. Total mechanism
  ~1s; model calls 2-3. This is exactly the 2-vision benchmark shape (tests/two_vision_bench.py on
  origin/main, commits c267411, 9a15647; drives via WebDriver, never calls act-now, so the
  after-image trap cannot fire inside it).
- Actions: set CU_CODE_EXEC=1 in the live path; drive the live loop through code-exec; use the
  2-vision benchmark as the gate (it runs after the AMEND sign-off, per owner sequencing).
- Expected: a tc02-class task at mechanism ~1s + 2-3 model calls. Whether that lands at the 10s
  target depends on model inference time, which I did not measure (see honest limits). If vision
  reading dominates, expect 30-60s, which is still 3-5x better than the ~100s best and 15-25x better
  than the 823s t1. The mechanism stops being the argument; the model call count is the whole game.

### Step 3 (zero rebuild, only if Step 2 plateaus): laptop-side task runner.
- The 10x review's zero-rebuild sketch, restated: the VM sends a task plan (JSON) ONCE over the
  persistent channel; a laptop-side runner (state machine) executes it locally (DOM grounding,
  actions, checkpoint verification) and streams back compact state, not images, at checkpoints;
  the model intervenes only on deviation. No SSH per step, no image per step, no session per batch.
- This removes all three taxes at once (transport, session spawn, per-action model calls). It is a
  rewrite, and the owner has authorized rewrites when the evidence supports them. The evidence
  supports it only if Step 2 plateaus above target; do Step 2 first, measure, then decide.

## 4. WHAT I WOULD DELETE OUTRIGHT (first principles, no hedging)
- Fresh SSH per call: delete. Persistent multiplexed connection instead.
- scp for JSON files: delete. Same-channel transfer instead.
- Per-batch session spawn: delete. One session per task via the relay broker.
- Screen-scope after-capture as produced today: delete or scope-match. Never ship a non-chainable
  artifact labelled as the result of the batch.
- The per-action think-observe-think loop as the default: delete. Code-exec programs with
  checkpoint verification are the default; the stepwise loop is the fallback for unknown shapes only.
- The 120s freshness window as a gate on DOM-grounded work: delete for that path. Re-read the DOM
  (0.030s) instead of refusing for staleness.

## 5. HONEST LIMITS (what I did not prove)
- I did NOT measure model inference time. There are no inference timestamps available from here,
  and the 10x review states the same limit. My 10x claim for Step 2 assumes 2-3 model calls at
  roughly 10-30s each. If vision reading dominates, the end-to-end lands at 30-60s, not 10s.
  The mechanism can be ~1s; the model is the remaining unknown, and it is the majority of the
  remaining wall time under every design I propose.
- ControlMaster long-run stability is unproven. SSH historically dies after ~30s of idleness on
  this path; a master with ControlPersist may or may not survive that. I measured 3/3 at 0.01s
  in one minute. A 1-day soak test is owed before calling Step 0 done.
- I did not run the 2-vision benchmark live (not my brief; it runs after the AMEND sign-off).
  Step 2's numbers are composed from separately measured parts (DOM 0.030s, code-exec merged,
  benchmark script on main), not from one end-to-end run.
- The per-task 1.6x estimate for Step 0 is computed from CL2-MSG's shape (3 cycles, ~9 SSH
  connections). Tasks with fewer steps gain less; tasks with more steps gain more.
- The overlay acquire (315-349ms) is the largest remaining laptop-side item after Steps 0-1.
  I did not measure whether a session-level pill (acquire once per task) is safe; that needs a
  council decision, not a unilateral change, because the pill is the owner's visibility into the run.

## 6. VERDICT
- The mechanism is already fast. Observe costs 0.25s on the laptop, DOM rects 0.030s, broker
  requests 0.1-0.5s, overlay 0.35s. The wall time is spent in three taxes the mechanism does not
  need: fresh SSH connections (4.6s each, ~85% of every remote call), per-batch session spawns,
  and one model call per action (87.8% in the local measurement, still the majority remotely).
- The 10x path is not a mystery and not a new invention. It is: persistent connection (measured
  460x on connect cost) + code-exec already built and merged (switch it on) + DOM grounding
  already measured (0.030s for 66 rects) + the 2-vision benchmark already scripted. The work is
  switching the live loop onto the parts that already exist, not building new ones.
- If the evidence says rewrite a lot, say so plainly: the laptop-side task runner (Step 3) is the
  rewrite, and it is justified only if Step 2 plateaus. Do Step 0 today, Step 1 next, Step 2 as
  the gate, Step 3 only on measured plateau. The one thing that should not wait is Step 0: a
  460x measured win with a fail-safe fallback has no reason to sit undeployed.
- Numbers used: fresh SSH 4.43/4.93/4.48s, mux 0.01s x3, observe 0.255s command / 26.5ms capture,
  act-now envelopes 1672/1729/2850ms, overlay 315-349ms, DOM sweep 66 rects median 0.030s,
  DOM verify 0.005-0.015s, F2b order-to-overlay 12.262s (dispatch 11.620s), tc02-t1 gap 722.955s
  (87.8%) vs service 37.721s (4.6%), S1 checkpointed pattern ~27s vs 823s (14-27x).
