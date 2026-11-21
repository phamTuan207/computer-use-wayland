# Worker ZT-A log: Zen ordinary-user test scenarios (2026-11-21)

Author: Worker ZT-A (Muse test author). Executor: Worker ZT-B (separate, blind).
Owner order 22:26 21/11: a dedicated test team simulates an ordinary user in
Zen, finds every error, feeds them into fixing. Scenarios run AFTER F3
reports Zen restored. Times are Asia/Ho_Chi_Minh, wall-clock + elapsed.

## Timeline

- 22:28:37 start. Repo ~/workspace/computer-use-wayland on todolist-push,
  in sync with origin. Working tree: tests/realistic/run_batch3.py modified
  (Y14b's work, not mine, untouched). Scenario file absent.
- 22:29 read tests/realistic/codex-y5/test-01-git-workflow.md for the
  scenario format convention (ID, Topic, Context, Timing, Goal, Exact steps,
  Pass/fail criteria, Errors designed to expose).
- 22:30 wrote improvements/zen-ordinary-user-tests-20261121.md chunk 1
  (10,212 bytes): header, executor rules (blind, composite, protected tabs,
  cleanup, evidence, health gate, one runner), tools, findings F-001
  (OWNER-REPORTED 22:25 Zen unclickable) and F-002 (OWNER-REPORTED 22:25
  workspace switching strange errors), ZT-00 health gate, ZT-01, ZT-02,
  ZT-03.
- 22:31 appended chunk 2 (7,123 bytes): ZT-04 bookmark, ZT-05 workspace
  switch and back, ZT-06 download PDF, ZT-07 fill and submit form.
- 22:32 appended chunk 3 (6,616 bytes): ZT-08 back/forward/reload, ZT-09
  many tabs + reopen, ZT-10 sidebar switching + collapse, run order and
  reporting, traceability (J1-J6 + todolist 4.7-4.12, recorded by Muse),
  what this file is not. Total about 24 KB, 10 scenarios + gate.
- 22:32 spawned 4 reviewers in parallel: council 1 (realism), council 2
  (composite coverage), council 3 (blind fairness + executability + safety),
  redteam (break the scenarios). Each writes its verdict to
  improvements/worker-zta-council-N.md / worker-zta-redteam.md. None may
  modify the scenario file.

## Notes

- No personal info in the scenario file: no real name, no email address.
  The Gmail tab is listed only as "Gmail inbox".
- No em or en dashes in the file. Click coordinates come from DOM rects,
  never from vision estimates (calibration lesson).
- Parent already added the 22:25 errors to the todolist (4.7-4.12) and the
  error summary file (J1-J6). This file cross-references them; the todolist
  and error-file updates are not duplicated here.
- Owner went to sleep 22:27. Overnight work, do not disturb.
- Never ydotool.

- 22:31 council 2 (composite coverage) completed, verdict AMEND. File:
  improvements/worker-zta-council-2.md. 15 required changes R1-R15.
  Headline: no scenario misses a channel on paper, but 8 of 11 fail in
  substance (token, mislabelled, conditional, or no-op channel). Systemic
  flaw R1: the "DOM rects, never vision" rule is impossible for browser
  chrome (address bar, sidebar, toolbar, dialogs), which has no DOM rect;
  must split the rule (DOM rects for page content, fresh-observe coords
  with saved screenshot for chrome). Other highlights: ZT-00 mouse absent
  and curl check passes on 200 and 404; ZT-02 DOM label false (find bar is
  chrome); ZT-03 mouse conditional; ZT-04 DOM mislabelled for chrome UI;
  ZT-05 mouse is a no-op move plus unverifiable body click; ZT-06 CLI
  strongest, ZT-07 DOM strongest; ZT-08/09/10 CLI is a single token
  hyprctl. Repeated hyprctl pattern adds nothing in 9 scenarios.
  Waiting for council 1, council 3, redteam before applying any fix, so
  their line numbers stay valid.

- 22:31 council 1 (realism) completed, verdict AMEND. File:
  improvements/worker-zta-council-1.md. 14 required changes R1-R14.
  Headline: ZT-06 BLOCKED as written, its only URL (W3C dummy PDF)
  returns 404, verified twice by GET and HEAD at about 22:30; replacement
  URL must be verified HTTP 200 with PDF content-type first, and it is
  not a document a real user would download. httpbin.org/forms/post
  returns 200 now but is a developer service no ordinary user visits, and
  one outage fails ZT-07, ZT-08, ZT-09 together. example.com appears in
  the gate plus 8 scenarios; keep it only in the gate. Harness-like steps
  flagged (ZT-01 L103/L115, ZT-03 L166, ZT-04 L194/L202, ZT-02 L141,
  ZT-06 L268/L274, ZT-07 L312, ZT-08/ZT-09 arbitrary chains). R14:
  curl/hyprctl/Marionette checks are instrumentation, not user behaviour,
  and must be marked [CHECK] separately. ZT-05 and ZT-10 GO (ZT-05 with
  a relabel).
  Still waiting for council 3 and redteam before applying fixes.

- 22:31 council 3 (blind fairness + executability + safety) completed,
  verdict AMEND, do not run as-is. File:
  improvements/worker-zta-council-3.md. 11 blind/executability items
  A1-A11 + 8 safety items S1-S8. Headlines: the file breaks its own blind
  rule (no exact zen_dom.py invocation ever given, no complete
  computer-use act click command; ZT-01 step 6 and ZT-03 step 3 name no
  exact element); L41-44 DOM-rects rule is unexecutable for chrome clicks
  (same systemic flaw as council 2 R1); ZT-00 step 2 contradicts itself
  (200 required, then 404 normal); ZT-02 step 5 asks Marionette to read
  the find-bar count, which is chrome and uncheckable; ZT-05 hardcodes
  workspaces 1/2; timings optimistic (maxima sum 51 min, 9 min left in
  the 60 min cap); safety: cleanup is count-only never identity, every
  Ctrl+W is blind, protected list stale/incomplete, ZT-04 can delete a
  pre-existing bookmark, ZT-06 rm is unconditional, ZT-00 has no fail-path
  cleanup. All text fixes, AMEND not BLOCK.
  Still waiting for redteam before applying fixes.

- 22:32 council 2 (composite coverage) completed, verdict AMEND.
  improvements/worker-zta-council-2.md, 15 required changes R1-R15.
- 22:32 council 1 (realism) completed, verdict AMEND.
  improvements/worker-zta-council-1.md, 14 required changes R1-R14.
  ZT-06 BLOCKED as written: W3C dummy PDF 404, verified twice.
- 22:32 council 3 (blind fairness + executability + safety) completed,
  verdict AMEND. improvements/worker-zta-council-3.md, A1-A11 + S1-S8.
- 22:32 redteam completed, verdict BLOCK (live-data risk: blind Ctrl+W
  can close an owner tab). improvements/worker-zta-redteam.md, R-01 to
  R-30, 6 blockers R-01-R-06.
- 22:33 read all four verdict files in full. Reconciled overlaps (the
  chrome-click contradiction appears in all four; the ZT-00 step 2
  contradiction in three; count-only cleanup in two).
- 22:34 verified the ZT-06 replacement URL before writing it in:
  https://www.irs.gov/pub/irs-pdf/fw9.pdf returns HTTP 200,
  Content-Type application/pdf, 140,815 bytes, real PDF 1.7 (GET check
  + file). Rejected: africau sample.pdf (202 + text/html, not a PDF),
  gutenberg 11-pdf.pdf (503), learningcontainer sample (404).
  orimi pdf-test.pdf is 200 + application/pdf but is another test file;
  the IRS tax form is a real document a real user downloads. Also
  confirmed the exact zen_dom.py CLI (list, eval, locate, kill-hung)
  and the act action schema (click x/y, type text, key keys array).
- 22:35 rewrote the scenario file as v2 (658 lines, about 36.5 KB),
  applying every required change:
  * Systemic: chrome-click rule split (DOM rects for page content,
    fresh-observe coords + named anchor + saved screenshot for chrome);
    exact zen_dom.py and act commands in Tools; [CHECK] tagging with
    the INCONCLUSIVE rule (curl control fails = inconclusive, not FAIL);
    poll rule (500 ms); pre-close title check before EVERY Ctrl+W;
    identity cleanup from a ZT-00 step 0 full tab snapshot; protected
    set = snapshot; host tagging ([CLI laptop], absolute paths);
    timings revised (ZT-00 120 s, ZT-07 300 s, ZT-09 300 s, total
    about 45 min expected, 90 min max); one retry only on
    network-control failure.
  * ZT-00: step 0 snapshot + baseline count; step 2 fixed to 200-or-404
    passes; step 4 mouse click on the address bar (no Ctrl+L fight);
    step 1 flag string is diagnostic only; fail-path cleanup added.
  * ZT-01: Ctrl+L only in step 1; step 6 pins the "Vietnam" link.
  * ZT-02: step 5 is [OBSERVE] with an exact count observable, no
    click on the match; Escape verified; ps CLI check.
  * ZT-03: one deterministic middle-click path, no fallback; Ctrl+Tab
    defined as a switch test, not a destination; per-press pre-close.
  * ZT-04: bookmarks the Wikipedia article; pre-check for an existing
    bookmark; library is a [CHECK] via Ctrl+Shift+O only; delete
    verifies title AND URL and compares row counts.
  * ZT-05: relabelled as a Hyprland test (F-002); measured workspace
    numbers N/M; h1-centre click with performance.now() reload guard.
  * ZT-06: IRS fw9.pdf; both title and render required; pre-existing
    file moved aside, never deleted; mtime-checked download and delete;
    one path for the download button and the panel click.
  * ZT-07: reframed honestly (httpbin is a test service, no public
    login-free echo form exists); placeholder values Nguyen Van A /
    0901234567; keyboard-only select; per-field retype-once rule;
    Alt+Left back step deleted; ends on the result page.
  * ZT-08: three Wikipedia articles on one topic; exact titles at every
    step; reload proved by performance.now() T2 < T1; curl control.
  * ZT-09: same topic chain; activation order relaxed with explicit
    navigation; LIFO reopen asserted; per-press pre-close checks.
  * ZT-10: step 3 is [OBSERVE] with an exact 10-character observable;
    F-001 branch expands via the toggle or fails at step 3; toggle
    identified by tooltip, state recorded after the first click;
    hyprctl clients geometry check; 5 s poll window.
  * example.com now appears only in ZT-00; httpbin only in ZT-07;
    no w3.org/dummy.pdf references remain.
- 22:36 verification of v2: 658 lines; 0 em dashes, 0 en dashes;
  example.com 1 occurrence (ZT-00 only); httpbin 4 occurrences (ZT-07
  only); dummy.pdf 0; 11 pre-close check mentions; fw9.pdf GET 200 +
  application/pdf + 140,815 bytes + file reports PDF 1.7. One leftover
  "Save or Done" is only an example of the dialog button label, not a
  branch: the step records the exact label as shown.

- 22:37 commit 1 pushed and verified: a5a5553
  (a5a5553d8694357842d18e15896f98abe9511308), todolist-push, 5 files,
  1456 insertions: scenario v2 + 4 verdict files. ls-remote confirms
  todolist-push at a5a5553. No other worker's files touched
  (docs/zen-error-fix-todolist-20261121.md, scripts/cursor_session.py,
  scripts/cursor_theme.py, worker-f2 log left alone).

## Done

Scenario file improvements/zen-ordinary-user-tests-20261121.md (v2, 658
lines) is committed and ready for the executor ZT-B. ZT-B runs only after
F3 reports Zen restored. Findings F-001 and F-002 (owner-reported 22:25)
are the first entries and are re-checked by ZT-10/ZT-01 and ZT-05.
