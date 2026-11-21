# Worker PROBE-S2 log: SPEED Step 2 feasibility probe

Owner: Pham Tuan. Probe: fixture 2-vision bench + one-class CU_CODE_EXEC=1 flip test.
Branch: todolist-push. Start: 2026-11-22 06:36 +07 (Asia/Ho_Chi_Minh).
Standing rules recorded here per brief: no-self-healing rule (2026-11-22 05:56,
dang: when Muse itself errors or fails, an INDEPENDENT worker investigates,
names the cause and finds the fix; Muse does not self-diagnose or self-fix,
even for small in-task errors; hand the log and everything to other workers
to meet, research, propose and fix, avoid bias) and first-principles rule
(2026-11-22 06:01, dang: think from first principles; some things should
not exist at all, or should be different, or were wrong from the start;
if needed, remove and rewrite; applies to all work, especially AMEND4
and the improvement method: do not only patch bugs, ask whether the
original design was right, drop what is extra, rewrite when evidence
shows it is needed).
No em dash or en dash in this file, per standing rule. No personal info.

## 06:36 +07 | Start state

- HEAD todolist-push: 49081aa AMEND4 item 7: R10 flag redesign, closure
  plus locked getter (F6/F7).
- tests/two_vision_bench.py: ABSENT on todolist-push. Present on
  origin/main, 868 lines, last touched c267411 (batch 9 task 1).
- tests/two_vision_fixture.html: ABSENT on todolist-push. Present on
  origin/main, 48 lines, blob bac2702efa375ad330cce8130df40d8025d86261.
- Bench runtime on this VM: NO .venv, NO selenium in system python3,
  NO firefox/chromium binary, NO /home/hatch/workspace/tools/ at all.
  Bench hardcodes FF=/home/hatch/workspace/tools/firefox/firefox and
  GD=/home/hatch/workspace/tools/geckodriver, headless Firefox via
  Marionette port 2828 + BiDi 9223, selenium attach with
  --connect-existing. Network OK (Mozilla 302, PyPI 200, 2026-11-21
  23:36 UTC). Disk 100G free. So the bench cannot run as-is; the
  runtime (selenium + Firefox + geckodriver at the hardcoded paths)
  must be installed first. That is environment setup, not a bench edit.

## 06:37 +07 | Y1b status (from repo, no fix attempted)

- Verdict: council 3, commit 9d9bd63 (2026-11-21 11:22 UTC),
  file improvements/worker-y1b-verdict-council-3.md: OVERALL Phase A
  BLOCK on 84b88bb, 14/20 probes PASS, 3 real fails (1e, 2a, 2b),
  2 probe artifacts (4a, 4b), 1 allowed exception (2e).
- 1e negative controls, real gap: codemode f-string fails
  NameError: name 'chr' is not defined; code_exec f-string fails
  the same way.
- 2a codemode wall preemption, real gap: elapsed 7.20s (Y1b 5.26s,
  Council 1 6.70s), error raised only AFTER the C loop finished;
  probe needs elapsed at most 4.0s.
- 2b code_exec wall preemption, real gap: elapsed 6.20s (Y1b 5.31s,
  Council 1 9.63s), ok=True with NO error, silent success.
- Latest Y1b watch entry (improvements/worker-y1b-codex-watch-log.md,
  18:35 +07 21/11): "Phase A BLOCK verdict stands unchanged." Codex
  poll 4 at 18:33 +07: HEAD still 84b88bb, Phase B in progress.
- Code-level re-check at this HEAD (06:36 +07 22/11): no setitimer,
  SIGALRM, or child-process preemption mechanism in scripts/codemode.py
  or scripts/code_exec.py (grep finds only the BANNED_NAMES mention
  of subprocess); "chr" is in NEITHER SAFE_BUILTINS list
  (codemode.py line 37, code_exec.py line 107). No commit after
  84b88bb touches the executors for these gaps (later executor-adjacent
  commits 714e4f9 / cff27b2 are snippet-registry features only).
- Conclusion: the 3 Y1b real fails 1e/2a/2b are STILL OPEN. Gate (b)
  of the S2 flip (adjudication draft 9d23834) is NOT met.

## 06:40 +07 | Step 1 commits pushed and verified

- c5311ce bench file only (blob 80b00469 matches origin/main, 868
  lines). 7f3a70b fixture file only (blob bac2702e matches
  origin/main, 48 lines). Push: 49081aa..7f3a70b, then a concurrent
  probe-p3 push 7b1006a landed on top within seconds; my commits
  are ancestors of HEAD, git ls-remote origin todolist-push =
  7b1006a = local HEAD. Verified.
- Note: probe-p3 log (7b1006a) says clone1 batch 9 open since 06:01,
  Brave untouched, NOT-RUN. That is a laptop-side live run; the
  fixture bench below runs headless Firefox on this VM and does
  not touch the laptop.

## 06:41 +07 | Bench runtime installed (environment, not a bench edit)

- System pip is PEP 668 blocked; created venv /tmp/probe-s2-venv,
  selenium 4.53.0 installed there. No repo .venv exists, so this
  is the equivalent of the bench docstring's "repo venv python".
- Firefox: Mozilla latest tarball (XZ, 90,943,956 bytes), extracted
  full directory to /home/hatch/workspace/tools/firefox/, version
  Mozilla Firefox 160.0.1. First copy failed (stub alone, missing
  firefox-bin); fixed by copying the whole directory.
- Geckodriver: GitHub API rate-limited for this egress IP, so the
  API lookup failed; direct release download of v0.36.0 worked
  (2,306,404 bytes), geckodriver 0.36.0.
- Both hardcoded bench paths now exist: FF and GD as above.

## 06:42 +07 | Step 2: fixture bench run

- Command: /tmp/probe-s2-venv/bin/python tests/two_vision_bench.py
  --fixture --mode run --workdir /home/hatch/probe-s2-work
  --out /home/hatch/probe-s2-work/results.json
  (workdir moved off /tmp, see the first-attempt failure below;
  --fixture is the default local-chat-fixture plan, no live flag,
  no real thread touched.)
- First attempt 06:40:02-06:40:17 +07, workdir /tmp/two_vision_bench,
  FAILED at the inventory write: OSError Errno 28 No space left on
  device. Cause measured: /tmp is a 512M tmpfs at 100%, filled by
  my own setup files (/tmp/firefox 331M, firefox.tar.bz2 87M,
  /tmp/probe-s2-venv 59M, bench profile 27M). The run itself had
  reached VISION 1 harvest fine (clone1 4 elements 0.069s, clone2
  4 elements 0.0844s) before the write failed. Fix: removed only
  my own /tmp files (firefox extract + tarball + geckodriver
  files + old bench workdir), /tmp back to 12% used, and reran
  with --workdir /home/hatch/probe-s2-work (100G free disk).
  No bench code touched. This is environment setup, not a bench
  result, and not a self-heal of a Muse failure: the bench never
  ran to a verdict on the first attempt.
- Second attempt 06:40:30-06:40:41 +07, EXIT 0, outer wall 11,305 ms.
  Full JSON log lines (UTC wall, elapsed_s from monotonic clock):
  - browser_launch_manual 1.011s, pid 12865
  - marionette_attach_session 6.0037s
  - window_opened clone1 7.748s, clone2 8.7758s
    (file:///home/hatch/workspace/computer-use-wayland/tests/
    two_vision_fixture.html?clone=1/2)
  - vision1_harvest_one_shot clone1 0.0343s, 4 elements; clone2
    0.0876s, 4 elements
  - vision1_inventory_written 9.2479s,
    path /home/hatch/probe-s2-work/inventory.json
  - send_ok_v12 clone1 0.6904s, intent
    bench-20261121T234030Z-86e8d8:clone1
  - send_ok_v12 clone2 0.6807s, intent
    bench-20261121T234030Z-86e8d8:clone2
  - benchmark_finished outcome PASS, wall_s 10.8596,
    out /home/hatch/probe-s2-work/results.json
- results.json: run_id bench-20261121T234030Z-86e8d8, mode run,
  live false, instances one, visions_used 2, outcome PASS,
  wall_s 10.8596. Step 1 clone1 status sent, elapsed_s 0.6904,
  v1_value_ok true, v11_input_events 47, v12_gate_ok true.
  Step 2 clone2 status sent, elapsed_s 0.6807, v1_value_ok true,
  v11_input_events 47, v12_gate_ok true. Ledger confirms both
  intents sent with the BENCH-TEST messages.
- GATE (a) VERDICT: PASS. First ever run of the fixture 2-vision
  bench: 2/2 sends, both V12-gated, total 10.86s. Note the wall
  is dominated by browser launch + Marionette attach (about 7s)
  and window opening; the two guarded sends cost 0.69s + 0.68s.
  VISION 1 harvests cost 0.03s + 0.09s. The 10x claim is about
  the send path, not the one-off browser setup.

## 06:41 +07 | Step 3: Y1b status, final (no fix attempted)

- STILL OPEN, all three: 1e (chr NameError), 2a (codemode wall
  preemption absent, 7.20s), 2b (code_exec wall preemption absent,
  6.20s silent ok=True). Sources: verdict council 3 commit
  9d9bd63; watch log latest entry 18:35 +07 21/11 "Phase A BLOCK
  verdict stands unchanged"; code-level re-check at this HEAD
  (no chr in either SAFE_BUILTINS, no setitimer/SIGALRM/child
  preemption in either executor); no executor fix commit after
  84b88bb. Fixing Y1b is a separate commission, not done here.

## 06:41 +07 | Step 4: flag flip decision, DO NOT FLIP

- Adjudication draft 9d23834, row S2+D5, gating conditions IN
  ORDER: (a) run the fixture 2-vision bench green; (b) fix the
  3 Y1b real fails; (c) flip the flag for ONE live task class
  (clone chat sends) with act-now as fallback, measure, then
  expand. Quote: "A fixture bench pass alone does not fix the
  3 real fails." Section 2 item (b): full order is fixture bench
  run plus Y1b fixes, then P1/P5, then the S2 one-class flip,
  then P2.
- Gate (a) PASSED this probe (10.86s, 2/2 V12-gated). Gate (b)
  FAILED (3 real fails still open, see Step 3). Therefore the
  S2 flip is NOT authorized: CU_CODE_EXEC was NOT flipped, no
  one-class live task was run, no test target was touched.
  Reason: flipping code-exec on while council 3 BLOCKED Phase A
  on the executor itself (2b: silent success past the wall
  budget, ok=True with no error) would violate the gate order
  the draft states explicitly. The next step belongs to the
  Y1b fix commission, then P1/P5, then the flip.
- Laptop contention: not tested, not needed. No live run was
  attempted, so the 10-minute wait rule never triggered. The
  fixture bench runs headless Firefox on this VM only. Note for
  the record: probe-p3 (7b1006a) reported clone1 batch 9 open
  since 06:01, so a laptop-side run was active during this probe.

## 06:42 +07 | Commits and verification

- Bench commit c5311ce (only tests/two_vision_bench.py), fixture
  commit 7f3a70b (only tests/two_vision_fixture.html), pushed
  49081aa..7f3a70b, verified via git ls-remote (remote then moved
  to 7b1006a by a concurrent probe-p3 push; my commits are
  ancestors of HEAD).
- This log: committed with explicit pathspec only
  (improvements/worker-probe-s2-log.md), after fetch + rebase
  check; push verified via git ls-remote. HEAD at log commit:
  recorded below at commit time.


## 06:38 +07 | Step 1: bring bench onto todolist-push

- Command: git checkout origin/main -- tests/two_vision_bench.py
  (bench file only, unedited; blob verified against origin/main
  after checkout). Separate commit, explicit pathspec only.
- Fixture tests/two_vision_fixture.html also absent on this branch
  and required by the bench (FIXTURE absolute path points at it);
  brought in the same way as a SECOND separate commit of only
  that file, stated plainly here.
