# Task 2: change-only observation, discriminating test

Date: 2026-11-20 00:46-00:55 +07. Worker: live-measure (Task 2-4 run).
Owner: Pham Tuan. Branch: change-only-obs 6995a8c. Relay MainPID 1045797,
started_git_head 6995a8c, CU_CODE_EXEC=1 (drop-in codeexec.conf), broker idle.
Suite gate: CITED, not re-run. HEAD 6995a8c matches the triple A/B gate exactly
(1352 tests, 7F/0E/2S, failset identical to the 1339-test clean baseline).

## Verdict: BLOCKED-by-mechanism

The diff detection works live, but the diff crop never reaches the executor
through the code-exec envelope, so no token saving is possible through this
harness path as built. No wall arms were run: per the brief, a blocked
mechanism gets evidence, not a wall number.

## Live probe (scripted, no model calls)

Run dir on the laptop: /tmp/live-co2-20261120/ (probe1.py, smoke + probe
envelopes, records.jsonl, timed.py + analyze.py copied from the triple A/B
co-method arm, md5 82176e2a4b84691a1584ed68ce82953f).
Session co2-probe2, generation 942b73f83732ad441c305b37ede7ae25.
Probe wall 00:51:30.644-00:51:33.475 (2.831s start to finish). Smoke PASS
(windows only, 1 API call, 1.582ms). Probe request service 1.596s,
in-program elapsed 1527.72ms, 7 API calls. Terminal co2-term
(0x5564a6607d40, 924x1176), closed after the probe, desktop clean.

Program shape: observe_change_only(window) -> act type "x" (one char, no
newline) -> observe_change_only(previous) -> act type newline (runs "x") ->
observe_change_only(previous) -> observe_change_only(previous) with no act.

## Results

| Observe | Mode | Changed tiles | Fraction | Bbox |
| --- | --- | --- | --- | --- |
| First (no previous) | full | 96/96 | 1.000 | [0, 0, 924, 1176] |
| After typing "x" | diff | 2/96 | 0.021 | [0, 580, 162, 163] |
| After Enter ("x" runs) | diff | 3/96 | 0.031 | [0, 580, 162, 310] |
| No act between | none | 0/96 | 0.000 | None |

Detection works: a one-character change fires mode diff at fraction 0.021,
well under the 0.35 full-frame threshold, and a no-change observe correctly
returns mode none. The triple A/B never saw diff mode only because terminal
commands repaint most tiles (fractions 0.812-0.865 there); a small localized
change discriminates cleanly.

## The delivery gap (live evidence, from records.jsonl probe-diff)

1. In memory, the crop EXISTS. In-program diagnostics survived the envelope:
   probe_image_present=true, probe_thumb_present=true, and probe_keys lists
   "image" and "thumbnail" among the diff result keys.
2. The envelope DROPS it. The returned variables contain NO verify, verify2,
   or obs variable at all (machine-checked: verify in vars False, verify2 in
   vars False, obs in vars False). Cause in code: code_exec _jsonable_copy
   drops any dict value that is not JSON-able, and a PIL Image is not
   JSON-able, so the whole diff-result dict is dropped from the variables.
   The none-mode result verify3 DOES survive intact, with image None and
   thumbnail None, because None is JSON-able. That contrast is the proof.
3. The executor still gets FULL frames only. The probe-diff record lists 3
   images, all full 924x1176 frames: 894109 + 894109 + 894055 bytes,
   total 2,682,273 bytes. probe_obs_image and verify_image are full-frame
   paths (894055 and 894109 bytes on disk). Zero crop bytes anywhere.
   The full frame is bound by api_observe_change_only (result["observation"]),
   so the executor verifies from the full frame, exactly as the triple A/B
   co-method arm did.
4. No in-program workaround exists. The code-exec sandbox allowlist excludes
   .save and .size (attribute not allowlisted), `type` is a banned name, and
   imports are rejected, so a program cannot persist the crop itself.
   The fix must be harness-side: persist the crop and thumbnail to files
   and return their paths in the envelope (no code changed in this task;
   main stays frozen).

## Consequence

Change-only observation as built cannot save tokens or wall time through the
code-exec path: the crop is computed and then discarded, and the full frame
is captured and delivered anyway. A wall A/B of change-only vs full observe
would measure two identical full-frame deliveries. Do not re-run P1-P4 on
this branch until the harness persists the crop. The detection side (tile
hashing, 0.35 threshold, none mode) is proven live and needs no rework.

## Incidents

- First probe run 00:50:27 failed on my envelope typo (a colon inside the
  args list made invalid Python, so the smoke/probe JSON files were never
  written). Session started and finished clean; no broker requests sent.
- Second run 00:50:55 reused the finished lease file, so timed.py start
  replayed the old finished outcome and polled forever. Killed by head
  closing the pipe; lease dir removed; third run with a fresh lease
  (co2-probe2) succeeded. Lease files are single-use: never reuse one after
  a finish or restart.

## State after Task 2

Main checkout detached 6995a8c (codeexec.conf drop-in present). Relay
MainPID 1045797, CU_CODE_EXEC=1, started_git_head 6995a8c. Broker finished,
owner co2-probe2, free for the next arm. Desktop clean (herdrdrop + Zen
Pill fixture only). Laptop main checkout still carries the stashed
latency-probe log entries (stash WIP on 56f5af4 + /tmp/live-co2-20261120-laptop-log.diff);
they are merged into the log at the end, after main returns to 56f5af4.
