# COORD-CLICK-10 log - live sequence ZT-B, G-PILL retry, A1 prep, rung 3 prep

Coordinator: COORD-CLICK-10. Repo ~/workspace/computer-use-wayland, branch todolist-push.
Roadmap order, one lane at a time: (1) ZT-B blind run, (2) G-PILL retry, (3) A1 resume prep,
(4) rung 3 prep. Single lane, quiet machine, owner away from the machine.
Rule: never close/navigate the user's tabs; pill must show on any agent control; full time log
(wall-clock Asia/Ho_Chi_Minh + elapsed); small commits, push immediately; report to Muse tong
only, never to the owner. On any failure (tab closed, pill missing, error): STOP the sequence
and report to Muse tong. No em dash in this file.

## 0. Pre-checks (21:23-21:24 +07, T+0m)

- VM repo todolist-push HEAD 074d1fe. Amend4 commits present (a05ca0d, fda0788, 1389752);
  pill amend3 code e7e973e present. Dirty file tests/realistic/clone1-batch3/results.json
  untouched (another worker's). Untracked improvement files untouched (other lanes).
- Laptop: Zen PID 14625 alive (9222 + marionette, since 17:34); relay session_remote.py
  PID 70985 alive (relay.sock 18:32); Brave 9224 + Chromium 9223 alive.
- Overlay: holders {}, owner none, visible false, pill off. Daemon PID 160727 dead:
  expected idle state after the 21:21 hand cleanup of the stale S2-flip bare holder
  (holders 0, daemon idle-exits). First acquire in ZT-B must restart it; if the pill
  does not appear on acquire, STOP.
- Q-J1 residual pinned: needs concurrent tab churn (forbidden by single-lane + quiet
  machine), risk low.

## 1. ZT-B blind run (NEW run 3)

- 21:24 +07, T+1m: W-ZT-B spawned (run 3, new run number, new intent/message, copy of
  fixed run2.py; never run 1). Waiting for result.

## 2. ZT-B run 3 result: FAIL (21:27-21:33 +07)

- Attempt 1 (21:27:33, wall 13.8s): abort phase 1, "could not identify the current tab".
  Scan entry for the current tab read title '' and url ''. Direct session read 21:29:34
  proved the tab is the healthy visible Calendar tab (readyState complete); third list
  21:30:25 resolved the URL (0 empty entries). Retried per run-2 attempt-1 precedent.
  No tab opened, no input sent. Pill released ok.
- Attempt 2 (21:31:13, wall 38.8s): phases 1-3 all PASS. Open ok (count 18 to 19,
  explicit-select, URL + H1 verified, viewport_ok true). Probe ok. Phase 4 send REFUSED
  by the backend before any desktop act: dimension closure fails, mozInner [274, 66] +
  inner [677, 1160] exceeds window size [925, 1176] (gaps -26, -50); reported mozInner
  displaced from the true viewport origin (pixel proof a42ef12: true origin (240, 8) on
  the live narrowed window). No set_value, no focus, no key, nothing typed, no bubble.
- Root cause F2: Zen narrowed to 925 wide (window bounds [2509, 914, 925, 1176], half of
  run 2's 1863), OmaCal tiled beside it on ws1. Reported mozInner moved +21/+36 between
  the open harvest [253, 30] and the send snapshot [274, 66], displaced (+34, +58) from
  the true origin (240, 8). Unproven whether it also fails on full-width Zen; run 2
  never reached phase 4.
- Safety: tab count 18 before, 18 after, identical URL sets, current restored to Calendar
  tab. Only the scratch fixture tab opened and closed. Cleanup reported an error
  ("Browsing context has been discarded") but the independent end-state list 21:32:51
  proves the DELETE succeeded and only its success report was masked (known amend-4 open
  item, reproduced live). Pill covered every control (2 grims sight-verified, holder
  re-checked before send). Final pill holders {}, visible false. No live driver left.
  Muse tab closed in run 2 NOT reopened. No stop condition fired during the run itself
  (no 'not made current' refusal, no owner tab harmed, pill visible throughout).
- Q-J1 residual NOT triggered: no concurrent churn; all set-difference checks passed.
- Runner-side fix in run3.py (commit cff51d0): bare grim over SSH fails ("failed to create
  display"); both grim calls now carry the XDG_RUNTIME_DIR/WAYLAND_DISPLAY prefix
  (W-PILLVERIFY2 method). Run 2 never reached phase 5, so its bare P9 grim was never
  exercised.
- Commits: cff51d0 (runner), a4a8900 (log + results), ls-remote verified a4a8900.

## 3. Coordinator independent verification (21:34-21:36 +07)

- run-3.json read: matches the worker report exactly (open ok 18 to 19, probe ok, program
  ok false with the dimension-closure error, outcome error, cleanup ok false with the
  discarded-context error, pill_release ok, wall 38811.6ms, fixture sha matches).
- Git: cff51d0 + a4a8900 exist, a4a8900 is an ancestor of origin/todolist-push, ls-remote
  a4a8900ead13f6ae68a96978e4707ff880ad2fa5.
- Laptop end state: overlay status holders {}, visible false, pill off, clean. Independent
  tab list via zen-tab.py list: count 18, URL sets identical to tabs_before, current is
  the Calendar tab. (CDP /json/list on 9222 returned an empty body, Zen does not serve
  Chrome /json/list; used the Marionette list instead.)
- Run3 log (418 lines) corroborates: pill acquire 1 21:26:07, grim 1 sight-verified pill
  VISIBLE top center "S2-flip via CDP", attempt 1 21:27:33 wall 13.8s, pill acquire 2
  21:30:50, grim 2 sight-verified, attempt 2 21:31:13 wall 38.8s, final state pill
  holders {} visible false.
- Note: my read of run-3-attempt1.json was flagged by the runtime safety check, so I
  grounded the F1 finding in the worker handoff report + run-3.json + the run3 log, and
  took no action from that file. The F1 verdict does not depend on it.

## 4. STOP decision (21:36 +07)

- Sequence STOPPED at step 1 per the coordinator brief (on any error, stop the sequence
  and report to Muse tong). Steps 2-4 (G-PILL retry, A1 prep, rung 3 prep) NOT run.
- Decisions needed from Muse tong:
  1. F2 fork: fix the geometry origin computation on the narrowed window (independent
     worker + council/redteam, no self-fix), or restore Zen to full width by moving the
     OmaCal tiling (OmaCal state belongs to another lane).
  2. F1: direct-read fallback for the original URL when the scan entry is empty
     (independent fix + review; identification logic is safety-critical).
  3. Whether G-PILL retry, A1 prep, rung 3 prep proceed now or wait for the fixes.
     Re-run of ZT-B only after fixes land and are reviewed, as fresh run 4 with fresh
     intent/message.
