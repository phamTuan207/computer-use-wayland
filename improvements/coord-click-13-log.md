# COORD-CLICK-13: ZT-B run 5, live verify F1+F2+F3

Coordinator: COORD-CLICK-13. Worker: W-ZT-B (same lane as runs 3-4).
Repo ~/workspace/computer-use-wayland, branch todolist-push.
No em dash or en dash anywhere in this file. No personal info.
Report goes to Muse tong, not directly to the owner.

## 0. Task

Run ZT-B run 5: live verify the F1+F2+F3 fixes for Zen
tab-handling. Machine quiet (owner confirmed 23:58 the user is not
touching the machine, false alarm). Single lane. Run 5 is a NEW
run number with a NEW intent and message, copied from the run 4
runner (run3.py lineage, grim-env fix cff51d0 + pill gate).
NEVER run 1 or run 3.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from 23:59:14 +07 22/11)

- 23:59:14 +07 22/11, T+0m: task received. VM HEAD 311eacd.
- 00:00 +07 23/11, T+1m: run5.py created from run4.py
  (renames only), G0a 180 OK, G0b programs validate, G0c
  fixture sha matches. Commit e510909 created.
- 00:00 +07, T+1m: push rejected (remote moved to c597a29,
  mochi's B2-3 cumulative patch). Rebase --autostash onto
  origin/todolist-push; the other worker's dirty file
  tests/realistic/clone1-batch3/results.json untouched
  (diff sha e59d1849 identical before and after). Push
  succeeded, ls-remote e510909019f3f04e909a7ca09d5b4eb0c345a45d.
- 00:01 +07, T+2m: laptop as-found checks. Zen
  0x56307e2771d0 ws1, bounds [2509, 914, 1863, 1176] full
  width. 19 tabs (not 18; owner reopened Chat - Muse).
  Laptop repo at 4cf115c, fast-forwarded to 8e9c9d9 (F3 fix
  confirmed present). Fixture sha matches, geckodriver
  present, pill OFF, fixture server HTTP 200.
- 00:02:25 +07, T+3m: pill acquired, holder S2-flip:283479,
  visible true. Pre-run grim sight-verified (pill visible
  top center). Focus Zen ok.
- 00:02:57 +07, T+3m: run 5 launched detached,
  PILL_SLEEP_PID=283479.
- 00:03:38 +07, T+4m: run 5 finished, wall 40963.3ms,
  outcome error, phase 4 'action_failed' / 'dom-value'.
  No input sent. Pill released ok.
- 00:04 +07, T+5m: end-state verified (count 19, URL sets
  identical, current restored to Chat - Muse, no fixture
  tab, pill off, Zen alive).
- 00:05 +07, T+6m: evidence copied to repo, logs written,
  STOP per the task, report to Muse tong.

## 2. Run 5 result: FAIL, new error F4

- Phases 1-3 PASS. Phase 4 FAIL.
- F1: NOT EXERCISED (fallback did not fire; scan read
  worked). Already proven live in run 4.
- F2: dimension-closure refusal GONE (same as run 4).
  Settle numbers still not surfaced.
- F3: PASS as far as the run reaches. The "point outside
  observed image" error is GONE (0 occurrences in run-5.json
  and the runner log). The send reached the dom_act step
  past the point-validation. The point conversion works.
- F4 (new): {'code': 'action_failed', 'reason': 'dom-value'},
  completed 0. The first action (set_value on #msg-input)
  failed before any action completed. No input sent.
  'dom-value' is the verification basis in scripts/cu.py
  type verification (lines around 1753-1800, 2263, 2313,
  2382, 3337). Root cause NOT determined; no self-fix.
- Phase 5 untested. Cleanup ok false (known spurious
  close error, amend-4 open item, 3rd run in a row); the
  DELETE did succeed (verified by independent list).
- Safety: no owner tab closed or navigated (19 before, 19
  after, identical URL sets, current restored); only the
  scratch fixture tab was opened and closed; no input sent
  anywhere; pill covered every control.

## 3. What this means for the roadmap

- ZT-B is NOT done. Run 5 proves F3 (point conversion)
  but hits a new failure F4 in the set_value step.
- Next: F4 needs an independent fix worker plus council
  and redteam review, same route as F1/F2/F3. Then re-run
  as a fresh run number (R6) with a fresh intent/message.
- The cmd_close spurious-error open item (amend 4) is
  reproduced for the third run in a row; it should ride
  the same fix route.
- The last_viewport_settle surfacing (reads, settled moz,
  elapsed ms) is still an open follow-up if the settle
  numbers are wanted as run evidence.
- A1 resume stays HELD (single-lane, ZT-B unresolved).
  Rung 3 still waits on ZT-B (and on mochi's B2-3
  cumulative patch verification, which is a separate lane).

## 4. Evidence (Lauren Tan: command, output, commit hash, time)

- Runner commit e510909, ls-remote
  e510909019f3f04e909a7ca09d5b4eb0c345a45d. VM and laptop
  fast-forwarded to 8e9c9d9 before the run.
- G0a: Ran 180 tests in 14.644s, OK.
- Pill acquire 00:02:25 +07, holder S2-flip:283479,
  visible true. Pre-run grim /tmp/c5-zenproof-5/
  pill-pre-r5.png, 532983 bytes, sha256
  f771a97a6fc20fc9d47dfc1f4fc2b158702868cd918bbbbc5421b3b62f543de2,
  pill visible by sight.
- Run 5, launched 00:02:57 +07, wall 40963.3ms, outcome
  error. JSON improvements/c5-zenproof-runs/run-5.json,
  sha256 b1f441de15a9f2bcac096729e2eea4c37025012b2f6cf5110387ce6198284188.
  Program elapsed 1632.208ms.
- End-state list, 00:04 +07:
  improvements/c5-zenproof-runs/list-after-r5.txt, count 19,
  URL sets identical, current restored to Chat - Muse.
- Run log: improvements/c5-zenproof-runs/
  c5-zen-delegate-run5-log.md.
- No input was sent anywhere in this task. No owner tab was
  navigated or closed. No Zen restart, no kill-hung.
