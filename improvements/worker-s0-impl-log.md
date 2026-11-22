# Worker S0-IMPL log: SPEED Step 0 (persistent SSH multiplexing) + step-0 measurement bundle

Owner: Pham Tuan. Branch: todolist-push. Worker: S0-IMPL, for COORD-CLICK-3.
Started: 2026-11-22 07:02 +07 (Asia/Ho_Chi_Minh). All times wall-clock +07 unless noted.
Method: implement, then measure live. No em dash or en dash anywhere in this log or in any file touched.

## 0. Basis (read before writing code)

- FINAL direction e05fc58, section 1.3 S0 row and section 6 worker 2.
- PROBE-S0 interim 90eb8be: fresh 4.667s (n=10) vs mux 1.339s (n=18), 3.49x.
  Per act-now (3 connects) about 14s becomes about 4s, not about 2s.
  Per-task about 1.3-1.4x (D1). The 1.6x and 460x claims are DEAD.
- Hard requirements (all measured): (a) master via setsid/nohup WITHOUT -f
  (ssh -f masters refuse mux sessions and die in 1-2 min, reproduced 2/2);
  (b) ControlMaster=auto on clients (death self-heals with one slow correct
  fallback); (c) per-use liveness check plus restart-on-death;
  (d) ServerAliveInterval=15; (e) per-socket watchdog, not global;
  (f) log master death.
- Soak A (no ServerAliveInterval, /tmp/probe-s0/soak.jsonl): t+0 0.894s,
  t+5 4.461s, t+10 5.596s, t+15 4.621s. Master dead by the first 5-min
  keepalive; pid churns every sample. Keepalive every 5 min does NOT save
  a plain master.
- Idle test A/B (run 06:53-06:58, /tmp/probe-s0/idle-A.log, idle-B.log):
  A (plain master): t0 1.141s, t90 5.582s (dead, new pid 23325),
  t300 4.861s (dead again, new pid 24064). B (ServerAliveInterval=15):
  t0 1.135s, t90 1.172s (alive, same pid 21189), t300 0.883s (alive,
  same pid 21189). ServerAliveInterval=15 is the load-bearing option:
  without it a master dies inside 90 s idle; with it the same master
  survives 300 s idle.
- Soak B (ServerAliveInterval=15 master, /tmp/probe-s0/soak-b.jsonl):
  started 07:00:12, t+0 sample 0.903s, master pid 25435 alive. Ends
  about 08:00. Advisory, not a gate. Final numbers checked at the end
  of this task if the clock allows; interim status recorded in section 8.
- No repo Python file shells out to ssh today (grep: zero ssh/scp call
  sites in scripts/*.py). SSH reaches the laptop through
  ~/workspace/ssh-laptop.sh (outside the repo) and through probe wrappers
  in /tmp. So S0 lands as a repo-owned library plus shell drop-in, not as
  a patch to an existing call site. The deploy step (sync-installed.py)
  already has a release ledger; CB-9 adds the stable manifest on top of it.
- E2 calibration: 58.6% (17/29) measured across WIDTHS=(960,1280,1920)
  (tests/calibration_live.py:28). JPEG q90 4:4:4, measured max pixel error
  39 on a real 960-wide frame (cu.py save_observation comment). The 960
  width is the characterized one, so uniformity unifies at 960, not 1920.
- First principles (06:01): the residual 1.2-1.3s per session is
  server-side session setup per new channel (PROBE-S0 F3), not shell
  startup and not the mux layer (0.06s). Multiplexing caps at about
  3.3s saved per connection; batching commands into one session is free.
  Nothing in this step removes the residual; S1/broker is the next lever.
- No self-healing (05:56): this worker implements and measures. If the
  implementation itself fails in a way that needs diagnosis, that goes to
  an independent worker; this log records evidence only.

## 1. Scope decided (what lands in this step)

- S0: scripts/ssh_mux.py (library + CLI: ensure/check/run/stop/watchdog),
  scripts/ssh-laptop-mux.sh (shell drop-in), tests/test_ssh_mux.py.
  Own socket /tmp/cm-s0-%r@%h:%p, never a probe socket. State and death
  log under ~/.cache/agent-computer-use/ssh-mux/.
- P6 + CB-7 + CB-10 as ONE workstream: scripts/vision_measure.py
  (harness-owned VisionCallTimer: inference split, error class per miss,
  pinned capture params); first_action.py envelope gains dispatch_ms
  (--order-wall / CU_ORDER_WALL), first_pointer_ms (from desktop_act
  action_ms, new in cu.py), target_breached redefined on first-pointer
  time with an explicit basis, phase_ms split, capture_params per capture.
  Think time is recorded by the harness, never invented inside act-now.
  Overlay flicker stays UNPROBED here (LIQUID probe belongs to the A4
  worker); the phase split to measure it is in place.
- CB-3(a): one max_width. CAPTURE_MAX_WIDTH=960 in cu.py; observe and
  observe_screen default to it; first_action.py stops capturing at 1920
  (two call sites). E2-style recalibration is REQUIRED after this change
  and is OPEN (needs a vision model plus a live desktop; command recorded
  in section 7, not run here).
- CB-3(b): J37 codec separation. _action_points_changed counts a change
  only when the patch mean beats 6 AND the max pixel diff beats 50
  (codec ceiling 39 + margin, same 50 as _input_line_changed).
  screen_change_detail() reports mean, max, and codec_suspect. The
  desktop_act preflight treats a codec-only difference as no change.
- CB-5: zen_dom eval leaves the default CLI. `eval` requires --debug or
  CU_ZEN_DOM_DEBUG=1; otherwise a JSON refusal. evaluate() stays as the
  transport for harvest, locate, and hit_check.
- CB-9: sync-installed.py writes a stable <installed>/deploy-manifest.json
  at publish (source commit, source content digest, ledger path, installed
  artifact hashes, sync log path) and _check_release verifies it matches
  the latest ledger. Tested locally on the VM against a temp installed
  root; the laptop live-tree deploy is NOT done here (that is the S1 sync
  step; the live tree is mid-flight with clone work).

## 2. Implementation (files, in landing order)

- scripts/ssh_mux.py (new, 400 lines): SshMux library + CLI (ensure /
  check / run / stop / watchdog). Own socket /tmp/cm-s0-%r@%h:%p.
  Master argv: setsid/nohup, ControlMaster=yes, ControlPersist=600,
  ServerAliveInterval=15, ServerAliveCountMax=3, -N, NO -f anywhere.
  Clients: ControlMaster=auto on the same socket. ensure_master()
  runs -O check (liveness judged by rc, never by speed) and restarts
  a dead master, logging master_death (previous pid, check rc) plus
  master_restart to ~/.cache/agent-computer-use/ssh-mux/ssh-mux.jsonl.
  run() retries ONCE on a connection-level failure only, judged by
  stderr markers (control socket / master refused / connection
  refused|timed out|reset / no route / ssh: connect). A bare rc 255
  is deliberately NOT a connection failure: ssh passes a remote exit
  status of 255 through unchanged, so retrying on rc alone would
  re-run a command that already ran. A remote nonzero exit is never
  retried. watchdog() is a single-shot per-socket check plus restart,
  for cron every 5 min.
- scripts/ssh-laptop-mux.sh (new): shell drop-in, same base options
  as ~/workspace/ssh-laptop.sh plus the mux options. Never starts a
  master itself; ControlMaster=auto lets the first client create one.
- scripts/vision_measure.py (new): P6 harness module. VisionCallTimer
  (mark_observation_delivered / mark_inference_start /
  mark_inference_end / mark_target_returned) records vision_call_ms,
  inference_ms (None with an explicit not_split note when the harness
  cannot separate the model call), pinned capture params (max_width
  960, JPEG q90, subsampling 0), and error_class per miss
  (wrong_target / wrong_frame / unknown, never guessed).
  classify_miss() maps evidence to the class: stale frame or scope
  mismatch is wrong_frame; a different point on the right fresh
  frame is wrong_target; no point is unknown.
- scripts/cu.py: CAPTURE_MAX_WIDTH=960, CAPTURE_JPEG_QUALITY=90,
  CAPTURE_JPEG_SUBSAMPLING=0, CODEC_MAX_PIXEL_ERROR=50. observe and
  observe_screen default to CAPTURE_MAX_WIDTH. save_observation uses
  the constants and records jpeg_quality/jpeg_subsampling in meta
  (compact_result keeps them). desktop_act records action_ms per
  completed group ({index, type, ms} from batch start) in both result
  branches, for the CB-7 first-pointer read. J37: _action_points_changed
  now requires patch mean over 6 AND max pixel diff over 50; detail
  helper _action_points_change_detail reports max_patch_mean,
  max_pixel_diff, codec_suspect. screen_change_detail reports the
  strict verdict plus codec_suspect and reason. screen_changed keeps
  its old body (global mean over 3, or the patch rule). The preflight
  retry branch emits a preflight_codec_artifact diagnostic when the
  old-vs-settled comparison tripped only on codec-scale diffs.
- scripts/first_action.py: captures unified at cu.CAPTURE_MAX_WIDTH
  (two 1920 call sites plus the _scope_after 960 literal). Envelope
  gains dispatch_ms (from --order-wall / CU_ORDER_WALL, None when not
  provided/unparsable/skewed), first_pointer_ms (session path:
  order_to_session_attempt_ms + preflight_ms + first pointer
  action_ms, basis session_computed with the about 60ms child startup
  named as unrecorded; fallback path: measured in-process, basis
  fallback_measured), target_breached on first-pointer time with
  target_breached_basis (total_fallback when no pointer action
  completed or no action_ms), phase_ms (overlay_acquire_ms,
  observation_ms, session_attempt_ms, after_capture_ms), think_ms None
  with think_basis not_in_act_now, overlay_flicker unprobed, and
  capture_params on observation/after/after_screen.
- scripts/zen_dom.py (CB-5): eval subcommand requires --debug or
  CU_ZEN_DOM_DEBUG=1; otherwise a JSON refusal BEFORE any session
  opens. evaluate() untouched (transport for harvest/locate/hit_check).
  Usage line updated.
- scripts/sync-installed.py (CB-9): _write_deploy_manifest writes a
  stable <installed>/deploy-manifest.json at publish (source commit,
  source content digest, ledger path, installed root, synced wall,
  sync log staging-evidence.json, managed file count, installed
  artifacts). _verify_deploy_manifest runs in _check_release (live
  mode only): missing manifest warns (old tree, no gate may be
  quoted), mismatched manifest raises. --manifest mode prints it.
  The failure handler deletes the manifest of a rolled-back release
  (the restore then puts back the previous release's manifest when
  the snapshot had one).
- tests/test_ssh_mux.py (new, 12 tests): construction (no -f,
  setsid-form options, ControlMaster=auto, base options match
  ssh-laptop.sh), failure classification (markers vs remote 255),
  ensure (alive not restarted; dead logs death and restarts),
  run retry (once on connection failure; never on remote failure),
  watchdog delegates to ensure.
- tests/test_s0_bundle.py (new, 28 tests): vision timer split and
  miss classes, classify_miss, dispatch/first-pointer helpers,
  uniformity (960 everywhere, no 1920 left in first_action.py), J37
  codec cases (localized noise patch; whole-frame noise global limb;
  real change at/far from the point; identical frames), zen_dom eval
  gate (refused / --debug passes gate / env passes gate),
  deploy manifest (write/verify roundtrip, mismatch raises, missing
  warns), first_action envelope smoke through the G28 refusal path
  with fake cu/overlay (dispatch about 2000ms, phases, params,
  total_fallback basis).

## 3. Test runs (offline, VM)

- 2026-11-22 07:10 +07: python3 -m unittest tests.test_ssh_mux
  tests.test_s0_bundle: 39 tests, OK.
- First regression run (test_core, test_act_diagnostics,
  test_a1_preflight, test_live_metrics added, 129 tests total):
  2 failures, both in test_act_diagnostics, both caused by my
  first J37 draft, which put the max-pixel condition on the GLOBAL
  limb too. The existing tests pin the global limb mean-only on
  purpose: a stable uniform brightness shift (mean 3.5, max 4) must
  trigger exactly one settle retry, and two raw frames that disagree
  (mean 4) must refuse. Those tests are deliberate specifications,
  and the FINAL direction overturns only the REFUSAL on codec
  evidence (J37, old-vs-settled patch check), not the retry. I
  narrowed the fix: global limb stays mean-only (retry trigger,
  raw-vs-raw rule), patch limb carries the max rule. The two tests
  pass again after the narrowing; my J37 tests were rewritten to
  the final scheme (localized noise patch: screen_changed False,
  reason codec_scale_only; whole-frame noise: global limb trips,
  codec_suspect True, patch check False).
- Re-run after the narrowing, before the zen_dom clobber (section 4):
  129 tests, 1 error only (the zen_dom gate test, see section 4).
- 07:36 +07: 129-test re-run after the second gate re-apply:
  37 ok, 92 errors, 0 failures. All 92 errors are the EPERM
  tempfile setup failure (section 4), none in test logic. The 37
  passing include all 12 ssh_mux tests that do not touch tempfile
  and the 3 gate tests. A full green 129-test run is still owed
  once VM file writes recover; it is the one unclosed test item.
  No test has failed on logic since the J37 narrowing.

## 4. Incidents during this task (evidence, not diagnosis)

- 07:25 +07: the zen_dom CB-5 gate test failed on re-run with an
  empty stdout. Cause found in the working tree: my three zen_dom
  edits were gone, replaced by another worker's uncommitted
  `return (function...` changes (worker-domzen-fix-log.md, file
  mtime 00:17:18 UTC, after my edits at about 00:10 UTC). The
  branch had also moved: local HEAD 17fdb9b (Y1b fix 2a/2b),
  origin/todolist-push af0d0a2 (PROBE-DOMZEN). I re-applied the
  gate on top of the current file (their 7 `return (function`
  changes intact, diff 44 lines) and verified the refusal live
  (rc 1, JSON debug-only error). My cu.py / first_action.py /
  sync-installed.py edits were verified intact by grep counts.
  Per the brief I did NOT fetch + rebase at the start (missed step,
  recorded here); git fetch now fails, see next bullet.
- 07:30 +07: git fetch origin fails: "fatal: unable to write loose
  object file: Operation not permitted / unpack-objects failed".
  git ls-remote works (origin/todolist-push af0d0a2). Python file
  writes fail VM-wide at the same time: os.write raises
  PermissionError [Errno 1] Operation not permitted in /tmp,
  /var/tmp, /home/hatch, ~/workspace, ~/.cache (files created
  0-byte). Shell builtins (printf, touch) still write. tempfile
  reports "No usable temporary directory found". This is the
  2026-11-10 EPERM condition recurring (AGENTS.md said it cleared
  2026-11-12; it is back as of about 00:19 UTC). Consequence: the
  129-test re-run fails with 92 errors, all in tempfile setup, none
  in the test logic. The live S0 measurement below runs in pure
  shell because of this (no Python harness). The test suite must
  be re-run when writes recover; the code is unchanged since the
  last green run except the zen_dom re-apply (verified live) and
  the J37 narrowing (covered by the 129-test run's 1-error state:
  only the gate test failed, and only because the file was
  clobbered, not because of test logic).
- 07:37 +07: SECOND clobber of the same gate. grep for
  "debug-only" in scripts/zen_dom.py returned 0 hits; file mtime
  00:28:37 UTC; diff vs HEAD back to only the DOMZEN worker's 9
  insertions / 8 deletions. I re-applied the gate a second time.
  While verifying, a real bug in my own re-apply surfaced: the
  gate sat INSIDE the `with ZenSession(...)` block, so the session
  opened before the refusal fired. The first live check had masked
  this because /tmp/geckodriver existed then; by 07:37 it was
  gone, and the bare eval died with a FileNotFoundError traceback
  instead of the JSON refusal. Fix: the gate now sits BEFORE the
  `with` block, so a bare eval refuses in 162ms with the JSON
  error and rc 1 and never touches the browser. The error string
  also regained "(CB-5)", which the suite asserts and my re-apply
  had dropped. All 3 ZenDomEvalGateTest tests pass standalone
  (0.689s, OK). Lesson for the coordinator: two workers writing
  the same file in one shared checkout with no lock will keep
  clobbering each other; my only defense is to commit fast (see
  section 8).
- 07:40 +07: the DOMZEN worker committed 5dcf2b3 (07:36:30 +07,
  "DOMZEN-FIX: return values from 7 zen_dom helpers") WITHOUT my
  gate (their tree had no gate at commit time). That commit
  resolved the mixed-authorship problem: HEAD now holds their
  return-changes, worktree holds their changes PLUS my gate, so
  worktree-vs-HEAD for zen_dom.py is my gate only. BUT the index
  now stages a REVERT of their commit (cached diff 8 insertions /
  9 deletions, plain `(function(` over `return (function(`),
  cause unknown, not mine: my `git add -p` failed on an
  index.lock EPERM write before staging anything). A `git reset`
  to clear the staged revert also fails on the same EPERM
  (rc 128, index.lock write error). Do NOT run a plain
  `git commit` in this state: it would commit the revert and undo
  5dcf2b3. The index must be reset to HEAD first, then only my
  files staged with explicit pathspecs. (Evidence only; the cause
  of the staged revert is for an independent worker to name.)
- 07:40-07:42 +07: EPERM characterized further (evidence for the
  independent investigator). Shell writes work: printf 1 byte to
  /tmp and to .git OK, printf to .git/index.lock OK, head 200KB
  to /tmp OK. Python writes fail: os.write 4KB-200KB all EPERM
  (was OK at 07:40 for 1 byte, then failed minutes later). Git
  writes fail wholesale: `git reset` rc 128 (index.lock write
  error, 22+ consecutive failures), `git hash-object -w` rc 128
  ("unable to write loose object file"), same error as the
  07:30 `git fetch` failure. The .git/index is 127996 bytes;
  disk has 100G free. Pattern: the block is per-binary and
  time-varying (shell OK while Python and git fail; the DOMZEN
  worker's git commit succeeded 07:36:30). It is NOT write size
  (128KB head write OK, 4KB Python write EPERM) and NOT path
  (.git shell writes OK). Consequence: no commit or push is
  possible until git writes recover; retrying the reset-add-
  commit-push chain every few minutes. The work itself is
  complete in the working tree (see section 8).

## 5. Live measurements (S0, pure shell, stdout-captured)

Run 1 (07:25:24-07:28:24 +07, /tmp/s0-measure.sh): PARTLY VALID.
- Fresh n=10 via ~/workspace/ssh-laptop.sh `true`: 4860, 6055, 5455,
  4478, 4538, 4870, 5052, 4578, 4439, 4419 ms; mean 4874.4ms, all
  rc=0. Slightly slower than PROBE-S0 4667ms (contention: many
  workers SSHing at once). Valid.
- Mux n=10: INVALID. All 10 samples 3-9ms rc=126: the drop-in
  scripts/ssh-laptop-mux.sh was not executable (muse.write creates
  0644). rc=126 is "found but not executable"; the script never ran.
  My error: I never chmod +x a new script before measuring with it.
  The master DID start (pid 59797, "Master running"), and check-only
  n=5 is VALID: 48, 44, 47, 15, 21 ms (mux layer about 0.02-0.05s,
  matching PROBE-S0 0.058s). The death test in run 1 is also invalid
  (rc=126 never attempted the connection; the "No such file or
  directory" check line only confirms the killed master stayed dead
  with no client to heal it).
- Fix applied 07:30 +07: chmod +x ssh-laptop-mux.sh; direct smoke
  call rc=0 in 5.2s (fresh cost, no master alive, auto-master
  pid 63135 created), second call 1.04s total (mux speed). Master
  stopped cleanly (-O exit, socket gone). Run 2 relaunched 07:31
  +07 in foreground with stdout captured (no file redirect, so the
  EPERM cannot eat the numbers again).

## 6. Live measurements (S0, run 2)

Run 2 (07:30:59-07:34:16 +07, /tmp/s0-measure.sh, stdout-captured):
ALL VALID, all rc=0.
- Fresh n=10: 4487, 4970, 4637, 5104, 4664, 4933, 4615, 4622, 4471,
  4606 ms; mean 4710.9ms.
- Mux n=10 over the S0 master (pid 63907, setsid/nohup, no -f):
  941, 1336, 1279, 1201, 1270, 1324, 1264, 1511, 1319, 1231 ms;
  mean 1267.6ms.
- Check-only n=5 (-O check): 19, 18, 59, 15, 12 ms; mean 24.6ms
  (mux layer cost, matching PROBE-S0 0.058s).
- Death test: killed 63907; after-death mux 4547ms rc=0 (one slow
  correct fallback, ControlMaster=auto self-heal); new master
  pid 64188 per the -O check line; post-heal mux 1248ms rc=0.
- Idle 120s: master 64188 still alive per -O check; after-idle mux
  953ms rc=0.
- Derived: ratio 4710.9 / 1267.6 = 3.72x; saving 3443.3ms per
  connection. Per act-now (3 connects): fresh 14.13s vs mux 3.80s,
  saving 10.33s. Per observe (2 connects): saving 6.89s. Per-task
  about 1.3-1.4x (D1, unchanged).
- Cross-check: fresh 4710.9ms (run 2) vs 4874.4ms (run 1) vs 4667ms
  (PROBE-S0); mux 1267.6ms vs 1339ms (PROBE-S0, n=18). Ratio
  3.49-3.72x across all three measurements. The 1.6x and 460x
  claims stay dead.
- Note: the script's ps-based MASTER_PID printed empty after the
  death and idle steps. Auto-created masters show in ps as
  `ssh: /tmp/cm-s0-... [mux]` with no ControlPath= in argv, so the
  grep missed them. The -O check lines carry the pid (64188) and
  are the real evidence.

## 7. Soak B (advisory, ServerAliveInterval=15 master)

Master pid 25435 since 07:00:12 +07, /tmp/probe-s0/soak-b.jsonl.
t+15 0.867s, t+20 0.909s, t+25 0.967s, t+30 0.919s, t+35 0.962s,
t+40 0.915s, t+45 keepalive 1.822s, t+50 1.078s, all rc=0, same
pid. The t+45 keepalive is slower (contention: many workers
SSHing at once) but the master is alive (check_rc=0, same pid).
VERDICT: PASS (advisory). The master survived 50 minutes with
ServerAliveInterval=15, same pid throughout, every sample
0.87-1.82s. The soak file itself was lost in the ~07:51 service
restart that wiped /tmp (t+55 and t+60 rows unrecoverable), so
the verdict rests on the t+0..t+50 rows recorded here.

## 8. Commit record

Status 07:44 +07: NOT YET COMMITTED. Blocked by the VM-wide EPERM
file-write outage (section 4): every git write fails since about
07:30 +07 (`git reset` rc 128 index.lock, `git hash-object -w`
rc 128 loose object, `git fetch` same). The only known working
git window was the DOMZEN commit 5dcf2b3 at 07:36:30 +07. The
reset-add-commit-push chain was retried 20 times 07:38-07:39,
7 times 07:41-07:43, and once 07:43:23, all failing on the
`git reset` step. The work is complete in the working tree; only
the landing is blocked.

RECOVERY (for whoever runs it once git writes recover; run from
~/workspace/computer-use-wayland, branch todolist-push):
1. `git reset` (clears the staged revert of 5dcf2b3; verify with
   `git diff --cached --stat` showing EMPTY before proceeding).
   NEVER run a plain `git commit` before this step.
2. `git add` these 10 files ONLY, each by explicit pathspec,
   never `git add -A`:
   improvements/worker-s0-impl-log.md scripts/ssh_mux.py
   scripts/ssh-laptop-mux.sh scripts/vision_measure.py
   scripts/cu.py scripts/first_action.py scripts/zen_dom.py
   scripts/sync-installed.py tests/test_ssh_mux.py
   tests/test_s0_bundle.py
3. Verify: `git diff --cached --name-only` lists exactly those
   10; `git diff --cached -- scripts/zen_dom.py` shows only the
   CB-5 gate (no `return (function` removals); `git diff
   --cached --stat` must NOT include scripts/code_exec.py or
   any other worker's log file.
4. Commit with the message in the 07:41 chain attempt (subject
   "S0-IMPL: SPEED step 0 SSH mux + measurement bundle (P6,
   CB-7, CB-10, CB-3/J37, CB-5, CB-9)" plus the measured numbers
   and test status in the body).
5. `git push origin todolist-push`, then verify with
   `git ls-remote origin todolist-push` and record the hash here.

Log commit hash: 18f23048d33b89c569e43fd335f37ceaa599f926
(local commit first made as 4985b45 on top of 5dcf2b3, then
rebased onto origin tip 6e1324a with git merge-tree --write-tree
because a plain rebase was blocked by other workers' untracked
log files; the merged tree was verified to be exactly origin
plus my 10 files, 2156 insertions / 28 deletions, before the
commit-tree; the old 4985b45 is superseded, same content)
Push verified: 2026-11-22 about 07:53 +07,
`git ls-remote origin todolist-push` returns
18f23048d33b89c569e43fd335f37ceaa599f926.
Tests after landing: 129-test suite green (OK) at about 07:55
+07, after the service restart cleared the EPERM.
## 9. Post-push notes (07:51-07:56 +07)

- About 07:51 +07 the exec service restarted mid-loop. It wiped
  /tmp entirely (/tmp/probe-s0/soak-b.jsonl lost with the t+55
  and t+60 rows; /tmp/s0-measure.sh lost too) and it cleared the
  EPERM: git writes work again (fetch, add, commit, push all OK
  after the restart) and the 129-test suite runs green.
- The restart also left 6 AMEND4 log files absent from disk
  (worker-amend4-closeout-log.md, worker-click3-loglander-log.md,
  worker-click3-r3c1/r3c2/r3c3/r3rt-review-log.md). They were
  present as untracked files at 07:49 and gone by 07:52. Their
  content survives in the pushed commit 18f2304 (from origin's
  log-lander commits); I restored all 6 from HEAD with
  `git restore` and verified them present. The 7th file
  (worker-codex-amend4-driver-log.md) was never absent. A `git
  reset` first fixed the stale index (it still reflected
  5dcf2b3). After the restore, status shows only the two
  pre-existing uncommitted modifications (scripts/code_exec.py,
  Y1b worker; improvements/worker-probe-s0-log.md, PROBE-S0
  worker) plus untracked files. No other worker's work was
  touched.
- Stash left over: stash@{0}, "WIP on todolist-push: 17fdb9b",
  created 2026-11-22 00:15:45 UTC, holds ONLY my original
  zen_dom CB-5 gate (first version, longer comment, error
  string "eval is debug-only: arbitrary JS in the current tab
  is not a default agent primitive (CB-5)..."). That is the
  first clobber's mechanism: the gate was stashed, not just
  overwritten. Its content is superseded by the improved gate
  landed in 18f2304. I left the stash in place (it is not
  mine to drop); the coordinator should ask whoever created it
  whether to drop it.
- Follow-up commit for this log update: 8817a90
  ("S0-IMPL log: soak verdict, push record 18f2304, restart +
  file-restore notes"), pushed and verified with ls-remote
  2026-11-22 about 07:55 +07 (origin/todolist-push
  fd63a7d08cb23451f82a9acc4579da4e718839dd at that time).
