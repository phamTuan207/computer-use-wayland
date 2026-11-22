# W-ZENPROOF2: Zen pointer delegate live proof, run 2 (close R13)

Owner: Pham Tuan. Coordinator: COORD-CLICK-9. Worker: W-ZENPROOF2.
Repo ~/workspace/computer-use-wayland, branch todolist-push.
No em dash or en dash anywhere in this file. No personal info.
Report goes to COORD-CLICK-9, not directly to Pham Tuan.

## 0. Task receipt and sources read (before any live touch)

- Task received 19:55:04 +07, 22/11/2026. T+0m.
- Laptop is free: Pham Tuan hung may 19:10 22/11, not at the machine.
  Per task order, ignore every idle/activity signal (IdleHint, input,
  focus, mouse, keyboard) as fake, do not gate live work on idle
  checks, keep running. Order 19:11 22/11.
- Sources read before running, procedure and R13 pass criteria
  recorded here verbatim from them:
  - improvements/w-zen-delegate-liveproof-prep.md (W-ZENPREP, prep
    cb741fe, fix B 161de2a, run kit 2d1dc82, run 1 abort d2ba7db):
    procedure phases 0-7, scratch target
    tests/two_vision_fixture.html?clone=zen, title 'Clone zen thread',
    message/intent fresh per run, viewport gate P2.4 (innerWidth and
    innerHeight > 0, hasFocus true, elementFromPoint non-null) before
    any input, send program phase 4 (set_value, focus, key Enter with
    ref, assert), pass only when dom_act ok True, completed 4, error
    None, post-checks P5.1 (bubble present, bubbles exactly [MESSAGE],
    input empty, input_events >= 1), retry already-sent P5.2, delayed
    count 1 after 10s P5.3, P9 screenshot reviewed by sight P5.4,
    cleanup P6 (scratch tab closed, handle count restored, current tab
    restored to owner tab, Zen alive, slot free).
  - R13 definition (prep file section 10.7, coord-click-6-log.md):
    run 1 aborted phase 1 because the active window was mochi
    Chromium on ws2 (0x56307e202df0) and mei Brave was also live on
    ws2; Zen on ws1 (0x56307e2771d0) was not active; focusing Zen
    would yank the visible workspace away from two live agent lanes.
    Coordinator decision then: do NOT authorize the focus switch;
    live proof WAITS until the mei/mochi lanes are idle, then rerun.
    R13 is closed by this run only when: (a) liveness check (ps plus
    relay state, P1.5 fix 902ffbe) shows NO live lane holds the
    machine, and (b) the full send program then passes every phase
    4/5 criterion live on Zen. A P1.1 abort on a still-live lane
    would leave R13 open, not closed.
  - R14 cleared by W-GECKO (0cb2b20): geckodriver 0.37.1 at
    /home/james/.local/bin/geckodriver, sha256 f831b7e6...,
    default now prefers that persistent path; minimal Marionette
    verify 18:11:01 +07 ok, 18 handles. P1.5 cleared by W-GECKO
    (902ffbe): liveness from ps plus relay state, leases evidence
    only, 13/13 unit tests.
  - Final direction: improvements/worker-click3-final-direction-log.md
    (read, grep R13/zenproof: no separate R13 pass criteria beyond
    the coord log decision above; the live proof waits for the same
    idle condition).
  - Todolist docs/zen-error-fix-todolist-20261121.md: item 4.29 pill
    must show on any agent control (hard rule 18:30); gate 4.29 met
    by W-PILLVERIFY2 (9ac4dcd, live pill render PASS after 8f600b9).
    Pill must show during this proof; verify with grim before and
    during, stop at once if the pill is not visible.
  - Run 1 abort lesson: do not re-run with the same intent/message
    after a send; run 1 sent nothing, but this is run 2 with fresh
    intent c5-zen-delegate-r2 and fresh message
    ZEN-DELEGATE-R2-IGNORE-TEST (G0d), so no ledger reuse at all.
- Hard rules restated: never close or navigate any tab of Pham Tuan
  (18:23); pill must show on any agent control (18:30); no
  self-review, no self-fix of my own failure (19:15: if proof FAILS,
  report and stop, an independent worker fixes via council 3 plus
  redteam); no em dash; no ydotool; no personal info on GitHub; no
  self-grading; log continuously with wall-clock Asia/Ho_Chi_Minh
  plus elapsed; if stuck 15 minutes with no progress, record it.
- Commit rule: git add with explicit pathspec AND git commit -m
  with explicit pathspec, never bare commit, never add -A, never
  amend. Push at once, verify with git ls-remote.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from 19:55:04 +07)

- 19:55:40 +07, T+0m: VM HEAD 71e807a (W-PILLFIX-CLOSEOUT), origin
  9ac4dcd (W-PILLVERIFY2). Local one commit ahead of origin, both
  children of fd77698. git merge --ff-only failed (diverged).
- 19:56 +07, T+1m: git rebase onto origin/todolist-push produced
  HEAD 394a989 (same W-PILLFIX-CLOSEOUT content, rebased onto
  9ac4dcd). History now linear on origin. Verified: diff 71e807a to
  394a989 is exactly the w-pillverify2-log.md addition (200 lines),
  no content lost. Pre-existing dirty tree untouched: modified
  tests/realistic/clone1-batch3/results.json (not mine, never
  commit), plus 8 untracked improvements files from other workers
  (not mine, never commit).
- 19:56 to 19:59 +07, T+1m to T+4m: phase 0 gates (section 2).
  Laptop as-found read-only checks (section 3): no live lane by
  ps plus relay (relay idle, owner null), active window is the
  Pick 4 fixture Chromium on ws2 with no driver behind it.
- 19:59 +07, T+4m: run-2 runner written (section 2, geckodriver
  check fix). Two laptop checkouts found: /home/james/workspace/
  computer-use-wayland at 9ac4dcd (current, pill fix present) and
  /home/james/computer-use-wayland at 331523f (old, contains fix B,
  R14, P1.5, missing only pill fix 8f600b9, dirty overlay/indicator
  files from another lane). Relay serve cwd is the old checkout,
  so live sessions run from the old checkout. Decision: do NOT
  touch either laptop checkout (the old one has another lane's
  dirty files and the live relay runs from it; the new one was
  synced by W-PILLVERIFY2 for CDP pill verify). The runner uses
  the old checkout paths, as run 1 did; both checkouts resolve
  geckodriver to /home/james/.local/bin/geckodriver and both
  fixture shas match. Session-path pill showed in 6 sessions at
  18:43 with the old code (W-F4FIX); pill will be verified live
  with grim during this run, stop at once if absent.
- (log continues below as the run proceeds)

## 2. Phase 0 gates (VM, no live touch)

- G0a PASS, 19:56 +07: `python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec` returned Ran 177
  tests in 12.992s, OK (zen_pointer 17 including the 2
  RealSignatureTests from fix B, p2_element_ref 100, code_exec 60).
  Fix B commit 161de2a is an ancestor of HEAD.
- G0b PASS, 19:58:56 +07: probe program and send program (run 2
  text, message ZEN-DELEGATE-R2-IGNORE-TEST) both pass
  code_exec.validate_program with no exception.
- G0c PASS, 19:56 +07: `sha256sum tests/two_vision_fixture.html`
  on the VM = 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5a
  f72fba6cbf, matching the manifest.
- G0d PASS: fresh intent c5-zen-delegate-r2, fresh message
  ZEN-DELEGATE-R2-IGNORE-TEST for run 2.
- Runner run 2: improvements/c5-zenproof-runs/c5-zen-delegate-
  run2.py, copied from the run 1 runner, diff limited to: run
  number 2, message/intent R2, workdir /tmp/c5-zenproof-2, run-2
  .json, p9-zen-r2.png, plus ONE functional change: the phase 1
  geckodriver check. The prep procedure P1.3 asked for
  /tmp/geckodriver, but R14 (0cb2b20) moved the default to the
  persistent ~/.local/bin/geckodriver and /tmp/geckodriver no
  longer exists on the laptop (verified 19:57 +07, "No such file
  or directory"; resolved path via zen_dom on the laptop prints
  /home/james/.local/bin/geckodriver True for both checkouts).
  The old check would false-abort every run, so the run 2 runner
  asks zen_dom itself for the resolved path and requires the file
  to exist there. py_compile OK. This is a check alignment with
  the landed R14 fix, not a change to the delegate or the proof
  program.

## 3. Phase 1 laptop as-found checks

(to be filled)

## 4. Pill verification

(to be filled)

## 5. Phase 2 scratch tab + viewport gate

(to be filled)

## 6. Phase 3 pre-select + read-only probe

(to be filled)

## 7. Phase 4 send program

(to be filled)

## 8. Phase 5 post-checks + P9

(to be filled)

## 9. Phase 6 cleanup and restore

(to be filled)

## 10. Verdict

(to be filled)

## 11. Evidence appendix (Lauren Tan: command, output, commit hash, time)

(to be filled)
