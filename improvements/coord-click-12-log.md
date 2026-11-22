# COORD-CLICK-12 log - ZT-B run 4, live verification of F1 + F2 fixes

## Verdict: FAIL, new F3 blocks the send

ZT-B run 4 (21:58:22 to ~21:59:07 +07, wall 39.3s, outcome error) FAIL.
Phases 1-3 PASS. Phase 4 send refused with a NEW error, "point outside
observed image", error_type sandbox, program elapsed 1123.553ms,
completed null, log only PROBE. No input sent. P5 not reached, no P9.
Per the brief, the worker STOPPED and reported; no fix attempted.

## F1: PASS, proven live

tabs_before in run-4.json carries "current_fallback": true. The phase 1
scan again returned an empty entry for the current tab (the same
transient artifact as run 3 attempt 1), and the direct-read fallback in
zen-tab.py resolved it to the Calendar tab
(https://calendar.google.com/calendar/u/1/r/week). Phase 1 PASS instead
of aborting "could not identify the current tab". The open section
confirms title_before "Lich Google - Tuan 16 thang 11, 2026" and the
Calendar url_before.

## F2: PARTIAL PASS, closure refusal gone but settle not measured

No "dimension closure fails" error anywhere in run-4.json or stdout.
The send snapshot went through the settled viewport_origin and passed
the geometry gate. Program elapsed rose from 677ms (run 3) to 1123ms,
consistent with the settle loop polling, but that is only consistent,
not a measurement of settle.
Honest limitation: last_viewport_settle (reads, settled moz, elapsed
ms) lives only on the ZenSession object in the oneshot process and does
NOT appear in the envelope, dom_act result, or any log. The worker
checked: no caller of viewport_origin in zen_backend.py or dom_act.py
reads or logs it. Run 4 cannot report the settle reads/elapsed numbers.
To get those numbers needs a fix to surface it in the envelope, or a
diagnostic calling viewport_origin directly.

## F3 (new): "point outside observed image"

Raised at scripts/cu.py:1030 in image_point(meta, x, y), when the point
lies outside the observed image dimensions (iw, ih) from
validate_coordinate_metadata(meta). The worker identified only the
raise site; no further diagnosis of which point or which frame is off,
no fix, per the STOP and report order.

## Safety accounting (coordinator verified independently)

- Tab count 18 before, 18 after, identical URL sets, current restored
  to the Calendar tab (fresh list: current tab is "Lich Google - Tuan
  16 thang 11, 2026", https://calendar.google.com/calendar/u/1/r/week;
  the handle differs across sessions because Marionette handles are
  ephemeral per session, as proven earlier; the URL is the ground
  truth). Only the scratch fixture tab was opened and closed.
- Cleanup reported ok false ("Browsing context has been discarded"),
  the known amend-4 open item (post-DELETE verification read hits a
  discarded context; the real DELETE succeeded). Reproduced 2 runs in
  a row (run 3, run 4).
- Pill covered every control: acquire 21:57:30 holder S2-flip:204881
  visible true, pre-run grim sight-verified pill top center
  "S2-flip via CDP", runner re-checked the holder before send, release
  ok. Final overlay status holders {}, visible false. No live driver
  left.
- The Muse tab closed in run 2 was NOT reopened (no muse.ai URL in
  the tab list).
- Window bounds [2509, 914, 925, 1176]: still narrowed 925 wide, so
  run 4 did prove the F2 closure is gone on the real narrowed window.
- Fixture sha matches (147494cda4...). The other worker's dirty file
  tests/realistic/clone1-batch3/results.json untouched.

## Deviation from the parent brief (recorded)

The parent brief said copy run2.py. The worker copied run3.py instead,
on my instruction. Run3.py is the latest fixed runner: it carries the
grim Wayland-env prefix fix (cff51d0) and the pill gate
(pill_setup/recheck/release, PILL_SLEEP_PID env) that run2.py lacks.
Copying run2.py would have regressed the pill grim (bare grim over SSH
fails "failed to create display") and lost the pill gate. The copy is
otherwise verbatim except the run number, intent/message, and WORKDIR.

## Commits (todolist-push, ls-remote verified)

- 1448dc3: run 4 runner (copy of run3.py, fresh R4 intent/message).
- 8ea0d6e: run 4 log + results (run-4.json, list-after-r4.txt).
- This log: coord-click-12-log.md (commit below).
- run-4.json sha256:
  0925e148137ae560fc9addae2735a02066dcfafb41ff35f1eec274d089602a22.
- Pill-pre grim not committed (.gitignore blocks *.png, same as run 3);
  /tmp/c5-zenproof-4/pill-pre-r4.png, sha256
  98755c11a31a5a11bf2d53534133a25a267560f9d5268fae518efb46fde552a5.

## Decisions needed from Muse tong

1. F3 "point outside observed image": diagnose and fix via an
   independent worker + council/redteam review.
2. Surface last_viewport_settle into the envelope, if settle
   reads/elapsed numbers are wanted as run evidence.
3. cmd_close spurious error (open item, reproduced 2 runs in a row).
4. Re-run (R5, new intent/message) only after F3 lands and is reviewed.
5. A1 resume order: still held, remains Muse tong's only (per
   COORD-CLICK-11; not issued here).
