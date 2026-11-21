# Worker CLICK3-FSPEED log: SPEED position response to the joint adjudication DRAFT

Owner: Pham Tuan. Role: final discussion participant holding the SPEED-REVIEW
position. The original SPEED-REVIEW worker completed and cannot receive
follow-ups, so I hold its position from its log:
improvements/worker-speed-review-log.md, commit a4ecb49 (212 lines).
Decision criterion (owner standing rule 06:07): the final result must be
the MOST ACCURATE and the FASTEST; cost is IRRELEVANT.
Evidence standard (owner 06:34, Lauren Tan standard): every claim carries
real measured numbers; where evidence is missing I say so plainly.
Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in this
file. No personal info. Evidence with every claim. Wall-clock
Asia/Ho_Chi_Minh plus elapsed time. Commit with an explicit pathspec
immediately after staging, never plain git commit, never git add -A.
Verify every push with git ls-remote. Never ydotool. This is a review
response, not my own work, so no self-healing question arises.

## 0. Log and inputs read in full

- 06:37 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push. Fetched first; local HEAD was 7b1006a at start.
- 06:37-06:40 (T+0-3m): read in full, in order: SPEED-REVIEW
  (improvements/worker-speed-review-log.md, a4ecb49), ARCH-REVIEW
  (improvements/worker-arch-review-log.md, 074c1d7), GROUNDING-REVIEW
  (improvements/worker-grounding-review-log.md, d1fc4e9),
  CODEX-BREAKTHROUGH (improvements/codex-breakthrough-report.md,
  2596287, 138 lines, Vietnamese), the joint adjudication DRAFT
  (improvements/worker-click3-adjudication-log.md, 9d23834), D1
  (improvements/worker-click3-d1-review-log.md, 37f457e), D2
  (improvements/worker-click3-d2-review-log.md, 6d1bf04), D3
  (improvements/worker-click3-d3-review-log.md, 14fc139), RTD
  (improvements/worker-click3-rtd-review-log.md, e96b2ff), X1
  (improvements/worker-click3-x1-response-log.md, 0cf601c), X2
  (improvements/worker-click3-x2-response-log.md, d5b205d), X3
  (improvements/worker-click3-x3-response-log.md, 2b0c73c), XRT
  (improvements/worker-click3-xrt-response-log.md, 6cb3f95).
- 06:40 +07 (T+3m): state check before writing. Branch had moved past
  the draft HEAD 72120aa: HEAD at writing is 2864be4 (probe-p8 log).
  AMEND4 items 7 (49081aa) and 8 (af0fa87) landed since the draft.
  PROBE-P8 returned BLOCKED (3790901). PROBE-P3 returned NOT-RUN
  (7b1006a). PROBE-S2 staged the bench files (c5311ce, 7f3a70b) and
  reports the Y1b 3 fails still open. No PROBE-S0 or PROBE-S1 result
  exists in the record yet (no matching commits found).
- 06:40-06:55 +07 (T+3-18m): wrote this log.

## 1. The 460x correction: CONCEDE, in full, with the corrected S0 expectation

SPEED concedes. The 460x figure is dead, and the 0.01s multiplexed
figure that produced it is withdrawn, not defended.

The evidence against it is now measured four ways and pooled:

- Fresh leg, 7 samples, all rc=0: SPEED 4.43/4.93/4.48s (mean 4.6s),
  D1 5.29s, D2 5.06s, D3 4.447s, RTD 4.61s. Range 4.43-5.29s,
  mean about 4.8s. SPEED's fresh leg reproduces everywhere; that
  half of SPEED's measurement was right.
- Multiplexed leg, 11 samples, all rc=0 with the master verified
  alive: D1 0.94/1.18/1.29s (n=3, master verified alive with
  ssh -O check) plus a real command 0.91s; D3 8 samples across two
  methods, 0.914-1.455s, mean about 1.25s. Range 0.91-1.46s, mean
  about 1.15s (XRT V-X9 pooled count).
- D1's failed-fast diagnosis fits SPEED's figure exactly: in D1's own
  first attempt, when the master had NOT come up, the mux call
  returned in 0.01s with rc=255, a failed-fast connection, not a fast
  one. SPEED's log reports 0.01s x3 with no return codes and no
  master-liveness check, so SPEED's readings cannot be distinguished
  from failed-fast. SPEED cannot now determine post hoc whether its
  master was up; the log records "master setup worked first try" but
  no rc and no liveness check, and that is insufficient. The figure
  is withdrawn.
- D2's "order of hundreds" hedge is superseded with it: D2 disclosed
  it as trusted, not re-measured, and two independent re-measurements
  refute it.

Corrected S0 expectation, converged across D1, D3, RTD, X1, X2, X3,
XRT, and the draft (section 1, S0 row; V-A6):

- Saving about 3.2-3.5s per connection, about 3.5-5x, not 460x.
- Per act-now (3 connects): about 16s becomes about 5-6s, not about
  2s. Per observe (2 connects): about 6-8s saved.
- Per-task: SPEED's 1.6x estimate on a CL2-MSG-class task was built
  on 0.01s and is WITHDRAWN, not to be quoted. D1's revised roughly
  1.3-1.4x stands as the working figure until a recompute on the
  corrected numbers.
- The residual about 1.1-1.2s per call is per-session sshd and shell
  setup on the laptop, which multiplexing does not remove. Its exact
  composition (shell startup, PAM, systemd user session setup) is
  UNMEASURED; D1's R2 open probe names it, and it bounds every
  transport design, including the Broker. SPEED accepts that the
  residual is itself an argument for S1 and A1, as D3 and RTD note:
  the Broker and the daemon avoid per-call sshd sessions entirely,
  which multiplexing cannot.

What the concession does NOT change, and SPEED defends this part with
evidence: the direction of S0, and the fresh-SSH tax itself. The tax
is real (7 fresh samples, 4.43-5.29s), the saving is real (about
3.2-3.5s per connection, 11 mux samples), the change is a wrapper
config plus watchdog with fail-safe fallback to fresh SSH, and no
agent-logic code change. S0 stays ADOPT, do now, first. The soak test
moves from a gate to advisory (RTD, D2, X1, X2, X3, draft agree):
it runs in parallel, a master death falls back to fresh SSH, slow
but correct. Two implementation requirements from RTD are accepted
into S0: the watchdog must be per-socket, not global (a half-dead
master can hang rather than fail cleanly; ControlPersist=600 can
leave a stale master holding a dead Tailscale route), and master
death must be logged.

SPEED also notes, for the record, what SPEED got wrong beyond the
number: SPEED's log treated "relay alive" (PID 1821, socket exists)
as evidence the S1 path was ready, and never mentioned the Y1b BLOCK.
Both omissions are conceded in sections 2 and 3 below. SPEED's
structural claims that survive unchallenged: the 87.8% local
measurement does not transfer to the remote VM-agent path (tc02-t1
gap 722.955s of 823s was measured with a local helper, no SSH hop
in it), and transport is a second, unmeasured tax in the current
remote loop. No reviewer disputes either.

## 2. Draft verdicts on S0-S3 and the six deletions: SPEED's per-proposal verdicts

SPEED's own ten items, judged against the draft. Tally for SPEED's
own rows: ADOPT 3 (S0, D1, D2), MODIFY 6 (S1, S2, S3, D3, D5, D6),
REJECT 0 in full (one part inside D4 is rejected and is named).

| ID | Proposal | SPEED verdict | Evidence and reasoning |
|----|----------|---------------|------------------------|
| S0 + D1 | Step 0 persistent SSH multiplexing, do now / delete fresh SSH per call | ADOPT on CORRECTED numbers | Section 1. Fresh 4.43-5.29s (7 samples), mux 0.91-1.46s (11 samples, rc=0, master verified alive). Saving about 3.2-3.5s per connection, about 3.5-5x. Per act-now about 16s to about 5-6s. Fallback explicit, master-death logging, per-socket watchdog, soak advisory in parallel. Agree with the draft. |
| S1 + D3 | Step 1 act-now over the persistent relay broker / delete per-batch session spawn | MODIFY, proof-first (was ADOPT) | SPEED CONCEDES the ADOPT. The per-batch spawn is a real tax (0.4-2.1s session start) plus a real failure mode (20s deadline, timeout never falls back, council 1 B1), and the relay is alive (PID 1821, socket exists). But liveness is not a client path: X1/X2/X3/RTD verified zero references to session_remote or Broker in first_action.py or cu.py (grep 0 hits), so S1 is a BUILD, not a switch, and the VM reaches the relay only through SSH, so it needs an SSH-tunneled broker client. Single-owner socket semantics under concurrent VM workers are unexamined (serialize or refuse). Gate: prove one live batch end to end over the broker from the VM first, then delete the per-batch spawn; keep the spawn as fallback until proven. Session-level pill (keep the overlay server) lands in the same step. Agree with the draft. |
| S2 + D5 | Step 2 DOM-first plus code-exec plus checkpoint verification, CU_CODE_EXEC=1 on / delete per-action model call as the default | MODIFY, gated (was ADOPT) | SPEED CONCEDES the blanket flip. The flag-off finding is real and verified live (CU_CODE_EXEC unset on the laptop; D1, D2, D3 probes agree; F2b log mentions act-now 15 times, code-exec 0 times). But SPEED never mentioned the Y1b BLOCK, and it kills the flip as stated: Y1b council 3 BLOCKED Phase A on 84b88bb, 14/20 probes passing, 3 real fails, 2 probe artifacts (commit 9d9bd63; XRT V-X2 confirms no later commit unblocks Phase A). The worst fail for a live flip is 2b: code_exec wall preemption, elapsed 6.20s, ok=True with NO error, silent success. Flipping a known-broken executor onto live tasks trades live-task accuracy for rollout speed, which fails the 06:07 criterion. Gate (B2, draft): fixture bench green, plus the 3 Y1b real fails fixed (1e f-string chr NameError; 2a codemode wall preemption, error raised only after the C loop finished; 2b silent success), plus flip for ONE live task class (clone chat sends) with act-now as fallback, measure, then expand. The "10x path" label is corrected to 3-5x on SPEED's own honest limit (30-60s if vision reading dominates; mechanism about 1s, model inference unmeasured). D5 follows S2: code-exec becomes the default for the proven task class first, expand on measurement. Agree with the draft. |
| S3 | Step 3 laptop-side task runner, only if Step 2 plateaus | MODIFY, fold into A1; plateau defined numerically first | S3 substantially overlaps A1: a laptop-side runner that grounds, acts, and verifies locally and streams back compact state IS the A1 driver daemon approached from the other side. One design decision, not two builds. SPEED agrees with the draft and with RTD/X1/X2/X3: the plateau criterion must be defined NUMERICALLY BEFORE the S2 flip starts (threshold, run count, decision owner), so the trigger is not argued later. An undefined plateau either never triggers or triggers on one bad run. The numbers themselves are set from the fixture bench plus first live runs baseline, not invented in this log. Decision owner is the coordinator (draft section 6). |
| D2 | Delete scp for JSON files | ADOPT for transport | JSON over the persistent channel (or in-process calls) replaces scp per step; each scp costs a fresh about 5s SSH. Scope condition, agreed with the draft and all four cross-responses: files stay as the audit and evidence trail (persisted observation artifacts, JSON plus JPEG, written by the driver); what dies is files as the transport, not files as the record. The JPEG still travels for the human VISION 2 check until the persistent channel carries bytes. Keep file IPC only as the fallback transport when no Broker is reachable. |
| D4 | Delete screen-scope after-capture as produced today | ADOPT the scope-match half; the delete-entirely half is REJECTED | Proven defective by construction (first_action.py:656 hardcodes cu.observe_screen, overwriting desktop_act's scope-matching after-capture at cu.py:2083-2091; V-A7, all four reviewers agree). Adopted shape, triple-sourced plus AMEND4 item 12: return BOTH after (scope-matching, chainable) and after_screen (full monitor, verification only, documented non-chainable); move the scope check before the overlay attempt; add a regression test. Execution DEFERRED to AMEND4 item 12, already in flight on two lanes; the rewrite track consumes it and does not duplicate it. REJECTED part: deleting the envelope after image entirely. It loses the human-visible evidence and the frame-change signal for a saving of about 0.25s, which is noise; that trade fails the 06:07 criterion on accuracy. The scope-as-capability refusal deletion (cu.py:1648/1649, screen observations refuse key/type) is sequenced WITH P2, not with this fix (D3's timing, agreed by X1/X2/X3/RTD and the draft): while actions are still pixel-addressed, the refusal protects typing against a screen observation; once actions are element-ref addressed, scope is irrelevant and the refusal can go. Agree with the draft. |
| D6 | Delete 120s freshness window as a gate on DOM work | MODIFY, scoped (was ADOPT as stated) | SPEED CONCEDES the correction. For DOM-grounded work, re-read the DOM (0.030s) instead of refusing for staleness; the window is a patch for vision coordinates, not a law. But the refusal at cu.py:773 also guards against future-clock observations, and a blanket delete removes the clock-skew guard (RTD, accepted by X1/X2/X3 and the draft). Gate: keep the future-clock refusal, drop only the age refusal for DOM paths. Keep the window for pixel-addressed work, where staleness is real and the refusal protects against acting on a dead frame. |

SPEED's stance on the draft rows that touch SPEED's claims:

- A1 (Layer 0 driver daemon): MODIFY, staged prototype. Agree with
  the draft. The direction is right and S3 folds into it, but the
  full-replacement claim has no existence proof (RTD C2, accepted by
  X1/X2/X3): session_driver.py runs cu.main() per command,
  code_exec.py is an in-process program model not a daemon,
  dom_act.py still grounds through image points, cdp.mjs drives
  agent-managed Chromium only, the bench is unrun. "Exists" means a
  file exists, not that the composition works. B6 stands as the gate:
  a staged prototype must prove snapshot/execute/verify end to end
  on one live ws2 clone chat before anything is deleted.
- A5 (delete one-shot SSH loop): MODIFY. Agree with the draft.
  Persistent-first is right; the word "only" is REJECTED, because
  the VM reaches the relay only through SSH, and if the broker dies,
  one-shot SSH is how the relay gets restarted. Fresh SSH stays as
  the documented fallback AND the recovery path.
- A6 (delete file-based observation/action IPC): ADOPT for transport.
  Agree with the draft (see D2 row above).
- A7/P4 (after-image scope fix): ADOPT the both-fields shape. Agree
  with the draft (see D4 row above).
- A8 (delete pixel-band verification for structured targets): MODIFY,
  sequenced behind P5. Agree with the draft. Deleting before the DOM
  assert set exists leaves actions with NO verification, which is
  worse than weak verification. The band is admitted
  necessary-not-sufficient (cu.py:1023-1076) and the DOM value check
  is sufficient and 100-1000x cheaper (0.002-0.015s), but the assert
  must exist and be mandatory per action type first.
- P1 (DOM/a11y default router): ADOPT. Agree with the draft. Encode
  the router in code as one function returning the perception
  source; fail closed to the labeled screenshot fallback; a
  per-target routing table proven per target before the default
  flips; a log line on every routing decision, so drift back to
  screenshots is visible instead of silent. Interim honest state:
  Brave tasks still route to screenshots until P3 lands.
- P2 (element-ref action interface): MODIFY. Agree with the draft.
  Direction right and highest-leverage code change after P3: the
  round trip exact DOM rect to exact screen point to lossy image
  point and back is proven wasteful from source (fastpath.py:195-243,
  dom_act.py:312, cu.py:1000-1005). B5 STANDS, narrowed: the
  collision limb is closed by landing (AMEND4 items 2-4 landed at
  HEAD 72120aa: c1ea773, 62b740e, 72120aa; item 4's message records
  BrowserAdapter does not exist, so the surface was narrower than
  B5 stated), and the stale-ref disagreement protocol is now the
  single outstanding gate. P2 starts only when the protocol is
  specified (refuse, re-plan, or click stale, per case, plus the
  lifecycle across a multi-action plan).
- P3 (Brave relaunch experiment): ADOPT as a controlled experiment.
  Agree with the draft. Single highest-leverage unblocker. Status
  at writing: NOT-RUN (PROBE-P3, 7b1006a), clone1 batch 9 open since
  06:01, Brave untouched; P3 feasibility is UNDECIDED, no measured
  evidence for or against. Re-run only in a real quiet window.
- P5 (DOM verification mandatory): MODIFY. Agree with the draft.
  Mandatory PER ACTION TYPE as its assert lands, plus an explicit
  per-action exception list (scroll position, hover state) where DOM
  assert is impossible and pixel stays the only signal. The blanket
  mandate is BLOCKED as stated: the assert set does not exist for
  every action type (focus_check and type_check are still optional
  hooks, D1 V13), and a blanket mandate now means false refusals on
  working flows or vacuous asserts. The V11 wording dispute is
  settled on the opt-in-hooks ground (draft section 2 item (f)):
  arm_typed_flag with a MutationObserver EXISTS in zen_dom.py and is
  CALLED from dom_act.py:433-434, so RTD's phrasing is not adopted
  as phrased; the remaining open question is narrow (whether the
  production code-exec path reaches that call for every type action)
  and belongs to the P5 implementer.
- P6 (measure the vision call): ADOPT, with the specification fix,
  bundled with S0. Agree with the draft. Capture is 15-30ms and DOM
  rects 0.030s, but the model read that locates the target is seconds
  and timed nowhere. Specification fix from RTD, accepted by all
  four cross-responses: the model call happens in the calling agent's
  loop, outside cu.py, so the timestamp points must be named
  (observation delivered to the agent vs located target returned)
  and the owner of the logging is the harness, not cu.py. Until that
  number is in the logs, every speed claim about the screenshot path
  is incomplete, and nobody may claim the 10s target is met.
- P7 (session handover protocol): MODIFY. Agree with the draft.
  First answer whether Marionette-only suffices (the benchmark
  already runs Marionette-only, harvest plus input, and zen_dom
  harvest IS Marionette). Write the handover protocol only if a task
  genuinely needs BiDi for grounding plus Marionette for input. A
  handover costs 4-7s per switch (BiDi new 1.51-2.77s fresh,
  Marionette attach 2.65-4.12s), comparable to the SSH tax being
  deleted.
- P8 (Zen chrome Marionette context test): ADOPT as a probe; now
  ANSWERED. PROBE-P8 (3790901, 06:37 +07) returned BLOCKED live:
  HTTP 500, "unsupported operation", "System access is required.
  Start Zen with the MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment
  variable set to enable it", on the live Zen PID 496121, session
  acquire 0.01s, content eval 0.00s, no restart performed. This
  independently reproduces the C12 probe (03:27:26 +07, same HTTP
  500, same message). Consequence, per the draft: keep screenshots
  ONLY for Zen chrome UI and record that boundary explicitly. No
  further time spent on this path without an owner-approved Zen
  restart. AT-SPI cannot see Zen, so that path stays closed.
- P9 (keep one screenshot for the human): ADOPT. Agree with the
  draft. VISION 2 is the agent's final sanity check reported to the
  human, not the owner looking directly (RTD wording correction).
  Cost about 0.25s plus one vision read, noise against the total.
- A2 (pixels demoted to fallback-only): ADOPT, with the sequencing
  constraint. Agree with the draft. Demote only after the router
  (P1) and its fallback trigger are proven; Zen chrome UI stays
  pixel-primary until P8 proves a structured path, and P8 has now
  returned BLOCKED, so Zen chrome UI stays pixel-primary.
- A3 (delete session supervisor tree): MODIFY. Agree with the draft.
  Delete only when the driver demonstrably holds scope plus cancel
  latch plus lock on a live run (B4 lift). The F1 failure cluster is
  partly environment faults, not supervisor-design faults; deleting
  the tree does not delete those modes.
- A4 (delete overlay daemon server): MODIFY. Agree with the draft.
  Session-level pill first (acquire once per task, server KEPT,
  measured; this removes the 315-349ms per-batch overlay tax
  without touching visibility), then driver-owned pill only with
  proof it shows and clears, including no stale or missing pill when
  the driver dies mid-task, then delete the server (B3 lift).
- A9 (coordinate model to one system): ADOPT for structured targets.
  Agree with the draft. Depends on AMEND4 items 5-6 landing (origin
  staleness); item 1 already landed (cc964b2) as the prerequisite.
  The one conversion still needs a correct absolute viewport origin
  and scale factors re-read per ground (C12 proved
  window-relative vs absolute origin is a live trap).
- A10 (acceptance test, 0-vision live benchmark): ADOPT as staged,
  per the draft. SPEED sides with the draft and XRT against
  X1/X2/X3 on the live 2-vision rung. See section 4.

## 3. How SPEED's proposals relate to CODEX-BREAKTHROUGH

CODEX-BREAKTHROUGH landed after the councils reviewed (2596287, 138
lines, Vietnamese, independent Codex audit; read in full). SPEED
judges it against the same criterion (06:07) and against the draft's
blocking findings. It is not a tie-breaker by default (RTD C1,
accepted by X1/X2/X3/XRT and the draft): a fourth reading of the same
evidence base is still the same evidence base. But CB independently
verified code from source (cu.py, first_action.py, code_exec.py,
a11y.py, zen_dom.py, session_remote.py, session_driver.py, the error
file, and a read-only JSONL aggregate of act-now), and where it adds
new measurement reasoning SPEED answers it on the merits.

### CB-7 (latency measurement fixes): SPEED accepts the correction, S0 verdict unchanged

CB-7 finds three measurement defects, all verified from source:

- first_action.py records order_to_overlay_ms from when the Python
  wrapper starts, not from when the user issues the command on the
  VM (lines 339-400). The code records no timestamp for the first
  pointer action.
- target_breached compares the TOTAL batch duration against the 30s
  threshold (lines 495-498), so the flag does not measure
  first-action latency at all.
- No local record supports the claim that 11.6s of 12.26s is SSH
  dispatch. The act-now log starts after the command has reached the
  laptop, so it cannot measure SSH. A different record (service
  11.611s, gap 1208.942s, speed-proto-pick4-summary.md:38) is a
  different measurement and proves nothing about the SSH share.

SPEED CONCEDES the F2b attribution: the "dispatch 11.620s is 95%
SSH/scp" reading of F2b (12.262s total, dispatch 11.620s, observe
0.233s, Python 0.060s, overlay 0.349s) is an inference, not a
measurement from local logs, and SPEED cited it as if it were
measured. The F2b log measures the laptop-side envelope, not the
VM-to-laptop leg.

What the concession does NOT touch: SPEED's S0 arithmetic does not
rest on F2b. SPEED measured the VM-to-laptop leg directly with fresh
SSH probes (4.43/4.93/4.48s, confirmed by D1 5.29s, D2 5.06s, D3
4.447s, RTD 4.61s), and the per-call saving (about 3.2-3.5s per
connection, 11 mux samples at 0.91-1.46s) is composed from those
direct measurements, not from the F2b log. CB-7 therefore corrects
SPEED's citation, not SPEED's verdict. SPEED agrees with CB-7's
prescription in full: measure VM-to-laptop dispatch separately with
the same workload, fresh SSH vs connection reuse. That is exactly
what PROBE-S0 (SSH soak) must report, and what P6 must report for
the model leg. Until then, SPEED's per-task figures stay estimates
built on direct per-connection measurements, and SPEED says so.

CB-7's own numbers corroborate SPEED's laptop-side envelope range:
199-line JSONL aggregate, p50 order-to-overlay 337.5ms, max 368.4ms;
p50 total wrapper 2.288s, max 6.95s; 195 session path, 4 fallback,
0 timeout; 167 envelope ok=true, 32 ok=false. SPEED's act-now
envelopes (1672/1729/2850ms) sit in the same range. The 5
source=captured observations in that aggregate also corroborate the
scope-substitution hazard CB 2.2 names.

### CB-6 (long-lived session driver): SPEED agrees, it confirms S1 and the A1/S3 fold

CB-6 finds, independently from source, that act-now builds a cu.py
session per invocation (first_action.py:172-178, 403-405) instead of
using the session_remote broker and JSON-lines session-driver
(session_remote.py:460-520, session_driver.py:59-75), and that
zen_dom likewise opens and closes a session per command. CB-6
requires one owner of pointer, overlay, and browser session, with a
sequential queue, and no competing BiDi plus Marionette clients
because the record shows two protocols share one Zen slot.

SPEED agrees. CB-6 is an independent confirmation of S1/D3 (the
per-batch spawn is a tax plus a failure mode) and of the S3-into-A1
fold (one session owner, one broker, one driver). It also sharpens
the S1 build: the broker path from the VM needs an SSH-tunneled
client, because the VM reaches the laptop socket only through SSH,
and the single-owner socket semantics under concurrent VM workers
(serialize or refuse) must be specified before the spawn is deleted.
That is the draft's S1 MODIFY gate, which SPEED accepts in section 2.
CB-6 does not change any SPEED verdict; it independently re-derives
the S1 direction from code CB read itself.

### CB-4 (batch growth by proven validity; 90% per-click math): SPEED accepts as a constraint on S2

CB-4 computes that if per-click hit rate is 90%, the probability all
20 clicks are right first try is about 12.2% under independence, and
about 3.4% for 32 clicks (CB notes real errors correlate, so this is
illustrative, not a prediction). CB's rule: batch size should grow
only as the executor proves the next steps are still valid, not
because more coordinates can be packed into one observation. CB 2.4
adds the mechanism: desktop and code-exec accept up to 32 actions
per batch (cu.py:1013-1019, code_exec.py:187-192), guards check
focus, window, geometry, and screen before acting, but no guard
checks that the first click opened the right page, focused the right
field, or that earlier steps did not make later coordinates stale.
After-capture happens only at the end of the batch.

SPEED accepts CB-4 as a binding constraint on how S2/D5 is
implemented, and it changes how SPEED states S2. SPEED's S2 value is
fewer MODEL CALLS (2-3 per task), not more actions per observation.
A code-exec program that blindly runs 32 actions on one stale
observation repeats the act-now failure mode CB 2.4 names. The S2
program must therefore carry, per step, preconditions before the
action and postconditions after it, with stop-at-first-failure, and
the batch must grow only as the executor proves each next step still
valid. That is what S2's "checkpoint verification" means in SPEED's
position, and it is why the draft's S2 gating (fixture bench, Y1b
fixes, one task class first, measure) is the way CB-4 is honored:
the one-class flip measures whether the verified batch actually
lands, instead of assuming it. CB-4 also cuts against any reading of
ARCH's "one vision drives max actions" as maximizing batch size;
SPEED sides with CB here: maximize VERIFIED actions per model call,
not actions per observation. No SPEED verdict changes; the S2
implementation requirement is tightened.

### CB-8 (evidence discipline): SPEED agrees, it strengthens the draft's ladder and B2

CB 2.8/2.9: the fixture form run in real Zen reached 0.64s and 15
steps, but the page is a fixture simulating the Polygon flow, not
the Polygon upload task, and the report itself records no baseline
on the same task. 13/13 verified actions cannot become a 90%
commitment for other apps. The todolist marks held-out app plus
independent agent PARTIAL, and J10 (real think-time) OPEN. DONE is
the state of a specific piece of evidence, not the general state of
a feature. CB 2.9 adds a repo-hygiene finding: the installed code is
not reproducible from the checkout (first_action.py is untracked,
the installed cu.py has two act-now branches the checkout lacks,
HEAD behind 622 commits on the remote-tracking ref at CB's checkout).

SPEED agrees in full. CB-8 strengthens three draft positions SPEED
already holds: the acceptance ladder (fixture first, then live, the
fixture pass alone repeats the F1a/F2b pattern); the B2 gate (a
never-run bench cannot substitute for fixing known fails); and the
requirement that S2's 3-5x be measured live on one task class before
expansion. SPEED's own honest limits already said Step 2's numbers
are composed from separately measured parts (DOM 0.030s, code-exec
merged, benchmark script on main), not from one end-to-end run.
CB-8 also means SPEED's DOM numbers (66 rects median 0.030s, 5
clicks all landed, verify 0.002-0.015s) are single-source (clone2
batch 7, RTD C1 applies) and must be re-measured in the fixture
bench, not quoted as proven. CB's Wilson 95% interval on E2 (17/29,
40.7%-74.5%) means vision 58.6% is a small-sample estimate; SPEED's
direction rests also on the independent G30/G31 cases (64px and 75px
misses, 45px eyeball error), not on E2 alone. On CB 2.9, SPEED notes
for the finalizer: before the benchmark becomes a release gate, lock
the source commit, the installed artifact, and the log of the same
build into one manifest.

Other CB findings SPEED endorses as supporting the draft:

- CB 2.1 (ok=true on input-sent, not target-verified): cu.py
  desktop checks know only the pointer position (cu.py:1541-1549),
  and first_action.py:422-439 maps cu.py ok into envelope ok=true.
  A click on the right pixel but into empty space can report
  success. SPEED agrees: this is why the S2 flip must carry
  verification, and why P1/P5 precede S2 (section 4).
- CB 2.2 (scope changes between steps): _fresh_observation
  substitutes a screen capture without re-framing coordinates
  (first_action.py:289-315); J40 records a window-observation point
  used on a screen image missing by about (+45,+12)px while the
  command still returned ok. SPEED agrees: this supports the A7/P4
  both-fields fix and sequencing the scope-refusal deletion with P2.
- CB 2.3 (vision scale story refuted; image inputs non-uniform):
  screen 1920x1200 scale 1, yet observe caps at 960px width
  (cu.py:2303) while act-now captures at max_width=1920
  (first_action.py:313), and JPEG q90 (cu.py:807-863). The model
  sees different resolutions by path. SPEED agrees: this supports
  DOM-first, and the non-uniform inputs strengthen the case that
  vision errors are partly input variance, not only model error.
- CB 2.5 (many backends, no common executor; zen_dom eval
  unrestricted): code-exec DOM windows are Chromium-only and gated
  on CU_CODE_EXEC=1 (code_exec.py:41-53, 69-77, 92-103); zen_dom
  eval runs unrestricted JavaScript in the current tab
  (zen_dom.py:151-155, 221-245); a11y traversal caps at 500 nodes
  or 2s, returns at most 80 items, truncated flag (a11y.py:83-104).
  SPEED agrees: this supports P2/A1, and the unrestricted eval point
  is a safety note for S2 (the code-exec allowlisted API only; eval
  stays out of the agent default).
- CB 2.10 (overlay flicker unproven, think-time unmeasured):
  overlay idle shows 0 repaint and 0 event in the measurements, but
  the LIQUID background test never ran because the plugin was not
  loaded; J10 think-time stays OPEN. SPEED agrees: neither SSH nor
  screenshots should be blamed for those until each phase is
  measured separately, which is P6's job.

## 4. Order of work and acceptance ladder: SPEED agrees with the draft, with two notes

SPEED agrees with the draft's order (section 2, steps 0-11) and its
acceptance ladder (section 3). The points that matter from SPEED's
position:

### S2 gating (fixture bench plus Y1b fixes plus one task class)

Agree in full. The gate has three limbs, in order: (a) run the
fixture 2-vision bench green; (b) fix the 3 Y1b real fails (1e, 2a,
2b); (c) flip the flag for ONE live task class (clone chat sends)
with act-now as fallback, measure, then expand. A fixture bench pass
alone does not fix the 3 real fails, and the bench has never run at
all (BUILD ONLY, V-A3), so the program's gate cannot be an unrun
script. SPEED's original S2 ADOPT carried only the bench gate; B2
kills it, and SPEED concedes (section 2). Status at writing, from
PROBE-S2: the bench files are now on todolist-push (c5311ce,
7f3a70b), but the runtime is missing on the VM (no .venv, no
selenium, no Firefox/Chromium binary, no tools dir), and the 3 Y1b
fails are STILL OPEN at the 06:36 check (no setitimer, SIGALRM, or
child-process preemption in codemode.py or code_exec.py; "chr" is in
neither SAFE_BUILTINS list, codemode.py line 37, code_exec.py line
107). Gate (b) is not met. Gate (a) cannot run until the runtime is
installed, which is environment setup, not a bench edit.

### P1/P5 before S2

Agree with the draft (section 2 item (b)) and with X3, against X2's
"S2 before P1/P2/P5" and against D1's original S2-first order. S2 is
"DOM-first plus code-exec plus checkpoint verification", and the
checkpoint verification part IS P5. Flipping S2 without P5 means
flipping code-exec while DOM verification is still optional hooks
(D1 V13, first_action.py:597-613), a window in which the live loop
runs code-exec with pixel-band verification only. P1 (router) and P5
(mandatory DOM verification per action type as asserts land) are
rewiring of existing code with no collision, so doing them first
costs one small step and removes that window. X2's order is rejected
for P1/P5 but accepted for P2: the S2 one-class flip does not depend
on P2, and P2 is collision-blocked until B5 lifts, so S2 precedes P2.
Full order: fixture bench run plus Y1b fixes, then P1/P5, then the S2
one-class flip, then P2.

### Acceptance ladder (A10): SPEED sides with the draft and XRT

The draft's ladder: rung 1 (required, first) fixture 2-vision
benchmark; final gate (required, last) live 0-vision benchmark on
real ws2 clone chats; live 2-vision kept only as a diagnostic option
if the live 0-vision run fails. B1 is LIFTED (draft section 5).

SPEED agrees, against X1/X2/X3, who retain live 2-vision as a
required middle rung. SPEED's reasons, on the evidence, not on vote
count (C1: agreement is not independent confirmation):

- In the bench design VISION 1 is a DOM harvest, not a screenshot,
  and VISION 2 is a human look at the threads; the machine never
  locates from pixels in either form. Live 2-vision and live
  0-vision-with-P9-screenshot are the same machine behavior; they
  differ only in whether the human looks at live threads or at a
  screenshot, and the P9 screenshot IS the human outcome check in
  the 0-vision run.
- The councils' stated purpose for the rung ("the live 2-vision run
  is the proof that DOM works on real Messenger pages") is served
  equally by the live 0-vision run itself, which also runs DOM on
  real Messenger pages and scores by DOM outcome (V12 sent-bubble
  gate).
- Under the 06:07 criterion a gate must protect accuracy or speed
  measurably. The extra run buys replication and localization, not a
  distinct proof, at a cost of about 0.25s plus one model read for
  VISION 2. SPEED accepts that cost as a diagnostic, not as a gate.
- The V11-observer limb of B1 is conceded as non-load-bearing for
  benchmark scoring (XRT section 3, accepted by the draft): the
  bench scores by DOM outcome through the V12 sent-bubble gate, not
  through the production V11 MutationObserver flag.

SPEED's conditions on the live run, all from the draft: P3 closed
first (otherwise it falls back to screenshots and proves nothing);
quiet window with clone coordination; owner approval per run (the
bench's --live plus --confirm-live gates plus plan-URL gate); agreed
test messages so the clones' working threads are not polluted. What
the fixture run does NOT prove is recorded as a gap, not papered
over: a fixture pass alone repeats the F1a/F2b pattern (pass on the
exercise, unproven on the real task).

### SPEED's two notes on the draft's order

- Note 1: the fixture bench run (step 3) can run in parallel with
  the P3 experiment (step 2), because it needs no quiet window and
  no live coordination (headless Firefox, local fixture). It may run
  as soon as S0 lands. The draft already allows this; SPEED states
  it explicitly because PROBE-S2 is already staged and waiting on
  runtime install.
- Note 2: the numerical plateau (step 6, before the S2 flip) must be
  set from the fixture bench plus first live runs baseline, not
  guessed in this log or in the draft. Form per RTD: Step 2 live
  median wall time above a stated threshold for a stated number of
  runs after the flag flip, decision owner the coordinator. Until
  the definition exists, the A1/S3 decision cannot trigger.

### AMEND4 sequencing

CONTINUE, slower, per the owner 06:09 TWO TRACKS rule. Agree with
the draft (section 4) and all four cross-responses. Triage: first
items 5, 6, 7, 8, 12 (items 1-4 done at HEAD 72120aa; items 7 and 8
have since landed as 49081aa and af0fa87, so the remaining first
batch at HEAD 2864be4 is items 5, 6, 12); then items 9, 10; item 11
(doc fix) any time. Kill rule at reconciliation: items the rewrite
deletes get killed; an item the rewrite subsumes is verified against
the new code, not assumed gone. B2/B5 findings go into the round-3
review. The two tracks run in sequence per item on shared files, not
in parallel on the same functions.

## 5. What probe evidence would change SPEED's verdicts

The probes named in the brief (PROBE-S0 SSH soak, PROBE-S1 broker
batch, PROBE-S2 fixture bench plus one-class flip) are running in
parallel; their results are not in yet, except where noted. SPEED
states in advance what each result would change, so no result can be
read as confirming a verdict it does not support.

### PROBE-S0 (SSH soak, 1-day, ControlMaster survival): what would change S0

- If the master survives 24h with ControlPersist and the per-socket
  watchdog, with fallback rate near zero and no hangs, S0 is DONE
  on the corrected numbers (about 3.5-5x per connection, per act-now
  about 16s to about 5-6s). Nothing further is owed on S0.
- If masters die or hang at a rate that makes fallback common, S0's
  expected saving falls toward fresh-SSH cost, and the S1/A1 urgency
  rises, because the residual about 1.1-1.2s per call plus the
  fallback rate bounds S0's value. A master that HANGS (rather than
  failing cleanly) is worse than one that dies: it costs more than
  fresh SSH. That outcome would keep S0 ADOPT but move the
  per-socket watchdog from an implementation requirement to a
  blocking fix, and would accelerate S1.
- If the soak shows a mux cost materially lower than 0.91-1.46s under
  some setup (different flags, warmer master), SPEED would revise
  the 3.5-5x upward, but only on rc=0 plus master-verified-alive
  evidence. No uninstrumented reading counts after the 460x
  correction.
- The R2 probe (what exactly costs the about 1.1-1.2s residual:
  shell startup, PAM, systemd user session setup) bounds every
  transport design, including the Broker. If the residual turns out
  to be mostly shell startup, a persistent shell per master removes
  part of it and S0's saving grows; if it is mostly sshd/PAM, only
  the Broker removes it, which strengthens S1.
- CB-7's demand applies here: PROBE-S0 must report VM-to-laptop
  dispatch separately (same workload, fresh SSH vs connection
  reuse), not bundle it into a laptop-side envelope.

### PROBE-S1 (broker batch, one live batch over the broker from the VM): what would change S1

- If one live batch proves end to end over the broker from the VM,
  with the single-owner socket semantics under concurrent VM workers
  answered (serialize or refuse) and the session-level pill measured
  in the same step, S1's MODIFY becomes ADOPT and D3 (delete the
  per-batch spawn) follows. The per-batch spawn is then deleted, and
  the spawn stays only as fallback.
- If the broker path fails, serializes badly under concurrent VM
  workers, or the SSH-tunneled client proves fragile, S1 stays
  MODIFY and the per-batch spawn stays as the live mechanism. S0
  remains the transport win, and the A1 daemon design must answer
  the same concurrency question before it can claim the transport.
- If the S1 proof shows the overlay 0.35s per batch is the largest
  remaining item after S1 (as RTD notes), the session-level pill
  (acquire once per task, server kept) becomes the next step, not a
  driver-owned pill, because visibility must not be touched before
  it is measured.

### PROBE-S2 (fixture bench plus one-class flip): what would change S2

- If the fixture bench passes AND the 3 Y1b real fails are fixed AND
  the one-class live flip measures model-call count and wall time at
  or better than the 3-5x expectation (30-60s vs the about 100s best,
  on unmeasured model inference), S2 expands to the next task class
  on measurement. That is the B2 lift, and it is the only path from
  MODIFY to ADOPT for S2.
- If the fixture bench fails, or the bench shows DOM grounding on
  the fixture is slower than clone2's single-source numbers (0.030s
  for 66 rects), SPEED's S2 timing claims get recomposed from the
  new measurement, and the S2 flip does not proceed until the bench
  passes. A fixture pass alone does not fix the 3 real fails; gate
  (b) is independent of gate (a).
- If the one-class flip plateaus above target (model inference
  dominates at 30-60s or more, with no further mechanism win), the
  numerical plateau triggers the A1/S3 decision. That is the S3
  gate doing its job, not a failure of S2: S2 was the measurement
  that proved the plateau.
- If P6 (vision-call measurement) shows model inference is the floor
  (2-3 calls at 10-30s each, total 30-60s regardless of transport),
  the 10s target is unreachable by any mechanism change, and the
  program must say so plainly and re-scope to model-call reduction
  only. No mechanism claim survives that measurement.
- If an independent re-measurement contradicts the DOM bench timings
  or the mux numbers (X3 section 7), the affected rows (P2, S2, A1,
  S0) are re-judged on the new measurement. A fourth citation of the
  same numbers changes nothing (C1).

### Probe status at writing (measured, not assumed)

- PROBE-P8: DONE, BLOCKED (3790901). See section 2, P8 row. The Zen
  chrome boundary is settled: screenshots stay for Zen chrome UI
  only, explicitly recorded.
- PROBE-P3: NOT-RUN (7b1006a). Clone1 batch 9 open since 06:01,
  Brave PID 7356 running and untouched. P3 feasibility is UNDECIDED.
  Re-run only when batch 9 is complete with a final report commit,
  no new clone1 batch is assigned, and no clone1 commits are in
  flight.
- PROBE-S2: STAGED, NOT GREEN. Bench files are on todolist-push
  (c5311ce, 7f3a70b, unedited from origin/main). Runtime is missing
  on the VM (no .venv, no selenium, no Firefox/Chromium binary, no
  tools dir). Y1b 3 fails STILL OPEN at the 06:36 check. Neither S2
  gate limb is met at writing.
- PROBE-S0 / PROBE-S1: NO RESULT YET in the record. No matching
  commits found at writing. SPEED's verdicts above do not assume
  their outcomes.

## 6. SPEED's order of work (agreed with the draft, steps 0-11)

0. S0 plus P6, now. Persistent SSH multiplexing with explicit
   fallback, master-death logging, per-socket watchdog; P6
   vision-call measurement with the timestamp points and harness
   owner specified in section 2. Gate to step 1: fallback explicit
   and watchdog in place. The 1-day soak test starts the same day
   and runs IN PARALLEL, advisory, not a gate.
1. AMEND4 continues in parallel, slower, per the owner 06:09 TWO
   TRACKS rule. Item 12 (A7/P4) lands via the in-flight run; verify
   the regression test. Gate: the rewrite track makes no parallel
   edits to the same functions AMEND4 is working on.
2. P3 Brave relaunch experiment plus P8 Zen chrome probe, in a real
   quiet window between clone batches, coordinator-owned, never
   mid-batch. P8 is DONE (BLOCKED, see section 5); P3 re-runs when
   clone1 batch 9 completes. Gate to any live DOM work: P3 passes
   (login intact, /json/list shows the Muse tab, one fill plus assert
   on a scratch input) or the Chromium fallback is proven with its
   own login-persistence check. No live-task migration until then.
   If P3 fails, re-plan around Zen Marionette only and report it
   plainly.
3. Fixture 2-vision bench run. Bring the bench onto todolist-push
   first (done: c5311ce, 7f3a70b); install the runtime (selenium plus
   Firefox plus geckodriver at the hardcoded paths) next. This step
   does not depend on P3 and may run in parallel with step 2. Gate
   to step 6: the fixture run passes.
4. Fix the 3 Y1b real fails on code-exec (1e, 2a, 2b). Gate to step 6:
   the fails are fixed (B2 lift, part 1).
5. P1 router plus P5 asserts per action type. Gate to step 6: the
   router logs its routing decisions, and the P5 assert set covers
   the S2 task class (clone chat sends).
6. Define the numerical plateau (coordinator, before the flip), then
   the S2 flip for ONE live task class (clone chat sends) with
   act-now as fallback. Measure model-call count and wall time.
   Gate to expansion: measured on one class; expand only on
   measurement.
7. P2 element-ref interface rewrite, after B5 lifts (stale-ref
   protocol specified; items 2-4 landed limb satisfied at HEAD
   72120aa). A9 one-system coordinates land in this step (depends on
   AMEND4 items 5-6). The scope-as-capability refusal deletion lands
   in this step, not with A7. Gate to step 8: P2 proven on the S2
   task class with DOM verification mandatory.
8. S1 broker path proof from the VM on one live batch, then delete
   the per-batch spawn. Session-level pill (server kept) in the same
   step. P7's Marionette-only question is answered before any
   handover protocol is written. Gate to step 9: one live batch
   proven end to end over the broker from the VM.
9. A1/S3 merged daemon/runner decision, only after steps 0-8 are
   measured and the plateau definition is applied. The prototype
   must prove snapshot/execute/verify end to end on one live ws2
   clone chat (B6 lift). Gate to step 10: prototype proven.
10. A3/A4/A5 deletions last, each gated on its replacement proving
    (A3: driver holds scope plus cancel latch plus lock; A4:
    session-level pill measured, then driver-owned pill crash proof,
    then delete the server; A5: broker proven on the VM path with
    one-shot SSH kept as recovery).
11. Acceptance: fixture 2-vision (step 3), then live 0-vision on real
    ws2 clone chats as the final gate (section 4), after P3 and P2.
    Live 2-vision is a diagnostic only if the live 0-vision run
    fails.

## 7. Acceptance test

SPEED adopts the draft's ladder (section 3 of the draft):

- Rung 1 (required, first): fixture 2-vision benchmark. Headless
  Firefox, local fixture. Pass criteria: the script's own gates
  (V12 sent-bubble gate after each message, scoring by OUTCOME in
  the thread DOM, never point-in-box). This rung does not depend on
  P3 and may run as soon as S0 lands. Status at writing: files
  staged, runtime missing, never run.
- Final gate (required, last): live 0-vision benchmark on the REAL
  ws2 clone chats (clone1 Brave plus clone2 Chrome). DOM harvest,
  plan, execute, DOM verify, zero screenshots in the machine loop.
  Pass criteria: accuracy at least 90%, scored by DOM outcome (V12
  sent-bubble gate, message in the thread DOM, never point-in-box);
  total wall time measured end to end including transport. One final
  screenshot is kept as unscored human evidence (P9); it must not
  feed the score. Conditions: P3 closed first; quiet window with
  clone coordination; owner approval per run; agreed test messages
  so the clones' working threads are not polluted.
- Diagnostic option (not a rung): live 2-vision. If the live
  0-vision run fails, the team may run live 2-vision to localize
  (script vs DOM path). It is not required before the final gate.

What the fixture run does NOT prove, recorded as a gap not papered
over: a fixture pass alone repeats the F1a/F2b pattern (pass on the
exercise, unproven on the real task). The live run is the proof the
fixture cannot give, because the real tasks fail on Brave on ws2,
where the DOM path does not reach yet (P3).

## 8. What STOPS (SPEED's stop conditions)

- S0 stops or reverts if the soak shows masters HANG (not fail
  clean) at a rate that makes the loop worse than fresh SSH. The
  fallback is the current behavior, so the stop is a revert, not a
  breakage. No other condition stops S0; it is the only unconditional
  adopt.
- S2 stops on B2: the 3 Y1b real fails unfixed, or the bench unrun.
  No blanket flip, no expansion past one task class without
  measurement, and no 10s claim until P6 measures model inference.
- P2 stops on B5: the stale-ref disagreement protocol unspecified.
  (The AMEND4 items 2-4 limb is satisfied at HEAD 72120aa.)
- A1/S3 stops on B6 (no prototype proof on one live ws2 clone chat)
  and on an undefined plateau. An undefined plateau never triggers
  or triggers on one bad run; either way the decision does not
  happen.
- A3/A4/A5 deletions stop on B3/B4: replacements unproven, pill
  visibility unproven, cancel/stop path missing, recovery path
  missing.
- The live 0-vision run stops if P3 fails (Brave refuses the
  debugging port on its default profile AND the Chromium migration
  is too disruptive): re-plan around Zen Marionette only, report it
  plainly, do not work around it silently. It also stops without
  owner approval per run or without a quiet window.
- Global stop: if P6 shows model inference is the floor and no
  mechanism change moves total wall time, stop claiming mechanism
  wins and re-scope the program to model-call reduction only.
- What stops SPEED's own claims: any new independent re-measurement
  contradicting the mux numbers or the DOM bench timings re-opens
  the affected rows (P2, S2, A1, S0). A fourth citation of the same
  numbers changes nothing (C1).

## 9. What SPEED got wrong (record, for the adjudication)

- The 460x figure and the 0.01s multiplexed readings: withdrawn in
  full (section 1). SPEED recorded no return codes and no
  master-liveness check, and D1 reproduced exactly 0.01s with
  rc=255 when the master had not come up. The per-task 1.6x estimate
  built on 0.01s is withdrawn with it; D1's roughly 1.3-1.4x stands
  as the working figure until a recompute.
- The F2b "95% SSH dispatch" attribution: an inference cited as a
  measurement (CB-7). The F2b log measures the laptop-side envelope,
  not the VM-to-laptop leg. SPEED's S0 arithmetic survives on its
  own direct fresh-SSH probes, but the citation is corrected.
- S1 ADOPT treated "relay alive" as "path proven": wrong. Zero
  Broker references exist in first_action.py or cu.py, so S1 is a
  build, not a switch. S1 moves to MODIFY, proof-first.
- S2 ADOPT never mentioned the Y1b BLOCK (9d9bd63). SPEED checked
  the code-exec gate lines but not the verdict record, and cited
  84b88bb only as a Pick 1 merge commit. The blanket flip is
  blocked; S2 moves to MODIFY, gated on bench plus Y1b fixes plus
  one task class.
- D6 as stated (blanket delete of the 120s window on DOM work) did
  not separate the age refusal from the future-clock refusal at
  cu.py:773. D6 moves to MODIFY, scoped, future-clock refusal kept.
- SPEED's log said the soak test was "owed before calling Step 0
  done". The soak is advisory, running in parallel, because the
  fresh-SSH fallback makes it non-blocking (RTD, D2, X1, X2, X3,
  draft agree).

## 10. Evidence index

- SPEED log: improvements/worker-speed-review-log.md (a4ecb49).
- ARCH log: improvements/worker-arch-review-log.md (074c1d7).
- GROUNDING log: improvements/worker-grounding-review-log.md
  (d1fc4e9).
- CODEX-BREAKTHROUGH report:
  improvements/codex-breakthrough-report.md (2596287, 138 lines).
- Adjudication DRAFT: improvements/worker-click3-adjudication-log.md
  (9d23834).
- D1: improvements/worker-click3-d1-review-log.md (37f457e).
- D2: improvements/worker-click3-d2-review-log.md (6d1bf04).
- D3: improvements/worker-click3-d3-review-log.md (14fc139).
- RTD: improvements/worker-click3-rtd-review-log.md (e96b2ff).
- X1: improvements/worker-click3-x1-response-log.md (0cf601c).
- X2: improvements/worker-click3-x2-response-log.md (d5b205d).
- X3: improvements/worker-click3-x3-response-log.md (2b0c73c).
- XRT: improvements/worker-click3-xrt-response-log.md (6cb3f95).
- Probe status at writing: PROBE-P8 BLOCKED (3790901, HTTP 500,
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required); PROBE-P3 NOT-RUN
  (7b1006a, clone1 batch 9 open since 06:01); PROBE-S2 staged
  (c5311ce bench, 7f3a70b fixture, runtime missing, Y1b 3 fails
  still open at 06:36 check); PROBE-S0 and PROBE-S1 no result yet.
- AMEND4 landed state at HEAD 2864be4: items 1-4 landed at draft
  HEAD 72120aa (cc964b2, c1ea773, 62b740e, 72120aa); items 7
  (49081aa) and 8 (af0fa87) landed since; items 5, 6, 12 still in
  flight.
- Y1b BLOCK: commit 9d9bd63 (14/20, 3 real fails 1e/2a/2b).
- Numbers used: fresh SSH 4.43-5.29s (7 samples, mean about 4.8s);
  mux 0.91-1.46s (11 samples, rc=0, master verified alive, mean
  about 1.15s); saving about 3.2-3.5s per connection, about 3.5-5x
  (460x dead); per act-now about 16s to about 5-6s; per-task about
  1.3-1.4x working figure (SPEED's 1.6x withdrawn); residual about
  1.1-1.2s per call, composition unmeasured (D1 R2); vision 17/29
  first-try 58.6%, Wilson 95% 40.7%-74.5% (CB), pointer error
  0.5-0.9px; DOM 66 rects median 0.030s, 5 clicks all landed, verify
  0.002-0.015s (single-source, clone2 batch 7, C1 applies); F2b
  order-to-overlay 12.262s (dispatch 11.620s, observe 0.233s, Python
  0.060s, overlay 0.349s; the 95% SSH attribution is an inference,
  CB-7); overlay acquire 315-349ms; tc02-t1 gap 722.955s (87.8%)
  vs service 37.721s (4.6%), local helper, no SSH hop; CB JSONL 199
  lines, p50 order-to-overlay 337.5ms, max 368.4ms, p50 wrapper
  2.288s, max 6.95s, 195 session path, 4 fallback, 0 timeout, 167
  ok=true, 32 ok=false; CB 90% math, 20 clicks about 12.2%, 32
  clicks about 3.4% all-correct first try under independence,
  illustrative only.
