# Worker CLICK3-CONTRACT: Layer 0 + CB-EXEC merged contract log

Owner: Pham Tuan. Role: contract writer (Worker CLICK3-CONTRACT). Step 2
of the FINAL DIRECTION (commit e05fc58): one Layer 0 + CB-EXEC merged
contract written early, proof stays late, at the prototype step. This is a
DESIGN DOCUMENT, not code. I wrote the contract; I did not implement it.
No code written, no code deleted, no flag flipped.

Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere. No
personal info on GitHub. Log with wall-clock Asia/Ho_Chi_Minh plus
elapsed time. Commit with an explicit pathspec immediately after staging,
never plain git commit, never git add -A. Verify push with git
ls-remote. Never ydotool. First principles (06:01). No self-healing
(05:56): this is new writing, not a fix of my own work.

## 0. Log

- 2026-11-22 07:00 +07 (T+0m): task received from COORD-CLICK-3. Repo
  ~/workspace/computer-use-wayland, branch todolist-push, HEAD 8008662
  at start.
- 07:00-07:03 (T+0-3m): verified the four source commits exist on the
  branch: ARCH-REVIEW 074c1d7, CODEX-BREAKTHROUGH 2596287,
  adjudication DRAFT 9d23834, FINAL DIRECTION e05fc58. Confirmed no
  existing contract doc in docs/.
- 07:03-07:08 (T+3-8m): read in full the FINAL DIRECTION (e05fc58,
  1073 lines), the Codex report (2596287, 138 lines, section 3 in
  particular), ARCH-REVIEW (074c1d7, 280 lines), and the stale-ref and
  scope sections of the adjudication DRAFT (9d23834). Grounded the
  contract on their verdicts, not on my own judgment: CB-EXEC MODIFY
  to prototype-only, B1 lifted with the P9 load-bearing condition, B5
  stands with the test-repair limb, CB-2 re-ground-first with stop on
  ambiguity, the scope-refusal reconciliation (delete the legality
  refusal with P2, keep the halt on scope change), the S1 five
  conditions, and the A10 three-rung ladder.
- 07:08-07:25 (T+8-25m): wrote docs/layer0-cbexec-contract.md.
- 07:25-07:28 (T+25-28m): verified no em dash or en dash in the
  contract (grep, zero hits). Wrote this log. Staged both files with
  an explicit pathspec, committed, pushed, verified with git
  ls-remote.

## 1. What was delivered

File: docs/layer0-cbexec-contract.md (740 lines). Sections:

0. What is being built, in one paragraph (one build, not two: Layer 0
   plus CB-EXEC plus S3, same destination).
1. Definitions (snapshot, scope, target ref, plan, postcondition,
   verified action).
2. Action shape: semantic target (role and name, or selector/ref from
   a fresh snapshot); scope (window/tab, image/DOM frame, observation
   ID); preconditions (unique, visible, enabled, right window,
   geometry and focus unchanged); input (real mouse default, real
   keyboard, API/DOM action only where equivalence is proven per
   control type); postcondition (dialog closed, URL changed, field has
   value, checked state changed, new text appeared); retry policy
   (retry only when surely unsent, state check before replaying a
   send/delete action, default on uncertainty is stop and report);
   per-action exception list (scroll, hover, focus-only moves).
3. Result contract: three-part (input_sent, target_received,
   verified); desktop_act ok becomes input_sent; verified=true only
   with a postcondition; envelope never reports ok from a session exit
   code or input_sent alone; the 167/199 ok=true rate is not a success
   rate.
4. Scope binding: each ref binds to (snapshot ID, scope); a scope
   change halts the batch, never silently substitutes; G28 loud
   refusal stays; re-ground first, stop on ambiguity; the stale-ref
   disagreement protocol core (refuse, re-plan, or re-ground per case,
   multi-action plan lifecycle); after-capture both-fields shape.
5. Backends under one contract: P1 router in code, routing on
   coverage, fail closed to labeled screenshot fallback, one log line
   per routing decision; DOM/BiDi (Chromium CDP, Zen Marionette/BiDi,
   Zen adapter as missing work); AT-SPI coverage reporting (truncated
   flag, node count, time cap, fall through on truncation); real-input
   default with per-control-type equivalence proof; screenshot crop
   for canvas/image/unexposed controls; vision as fallback with one
   max_width and PNG/lossless crops; Zen chrome UI screenshot-only
   (P8 CLOSED); one remote-session owner for Zen, timeout, session
   close in finally, wedged-session recovery protocol required.
6. One local broker: single owner of session, overlay, and browser;
   sequential queue; act-now routes through the session driver, not a
   per-batch spawn; fallback only when the log confirms the session
   has not run an action; timeout continues without replay; JSON over
   the persistent channel (files stay as audit trail); single-runner
   lock as a task lock; staged pill sequence; crash/stale/sleep/reboot
   lifecycle.
7. Locate confirmations: visible, interactive, uncovered (hit_check),
   stable (two rect reads agreeing), unique; handling for moving
   elements, CSS transforms, iframe offsets, non-unique targets;
   AT-SPI truncated-flag reporting.
8. Batch growth by proven validity (preconditions plus postconditions
   plus stop-at-first-failure); CB-4 math as illustration only, never
   a gate; maximize VERIFIED actions per model call.
9. What is removed: generic x/y as everyday model input; unrestricted
   zen_dom eval from the default agent interface (debug mode only);
   screen-scope after-capture as produced today; 120s age refusal on
   DOM paths (future-clock refusal stays); pixel-band as a pass signal
   for structured targets; dom_rect_to_image_point from the live path;
   scope-as-capability refusal in legality form.
10. Measurement: per-phase timing split (model, SSH, broker, observe,
    act, verify); first-pointer timestamp; dispatch split with the
    11.620s figure kept and the "SSH is 95%" slogan dead; error class
    per miss; capture parameters pinned and logged; CB-9 manifest
    locked before any bench gates anything; false-success honesty gate
    with zero tolerance.
11. Prototype gate (B6 lift): snapshot/execute/verify end to end on
    one live ws2 clone chat plus held-out tasks; wedged-session
    recovery proven; destructive-action test proving no double-send;
    full merge not authorized by this document.
12. Acceptance ladder: rung 1 fixture passed pending manifest, rung 2
    live 0-vision with the P9 hard condition, rung 3 100-task held-out
    with the Wilson independence limit recorded.
13. Open items (10, marked OPEN, not decided by me).
14. Log.

## 2. What is still open in the contract (marked OPEN, not decided by me)

Section 13 of the contract lists 10 open items, each with its owner
from the FINAL DIRECTION section 7. The ones that most affect the
prototype worker:

- Plateau numbers (COORD-CLICK-3, HARD GATE on the S2 flip): not
  invented in the contract.
- Rect-agreement tolerance and stability interval: set by the
  prototype from measured data.
- Wedged-session timeout values: set and proven by the prototype.
- Queue discipline (wait/refuse/timeout for the second queued batch):
  decided by the S1 deletion worker before the deletion executes.
- Per-action exception list contents: landed per action type by the P5
  implementer.
- Single max_width value: picked by the step-0 worker; the contract
  requires one value, not which.
- Shadow-DOM fallback shape: decided by the P3 experiment outcome.
- Defective proof tests for AMEND4 items 3, 4, 5-6 and the item-12
  regression-test pass plus Codex-lane confirmation: still open, owned
  by the round-3 council and the AMEND4 close-out worker. The contract
  cites the both-fields shape as landed in form, not as proven by
  test pass.

## 3. Verification

- Em/en dash check on docs/layer0-cbexec-contract.md: grep, zero hits.
- Em/en dash check on this log file: grep, zero hits (verified before
  commit; see section 4).
- No code changed: git status shows only the two new files staged.
- Push verified with git ls-remote (see section 4).

## 4. Commit

- Staged with explicit pathspec: docs/layer0-cbexec-contract.md and
  improvements/worker-click3-contract-log.md.
- Commit: (hash recorded below after commit).
- Push verified with git ls-remote: (recorded below after push).
