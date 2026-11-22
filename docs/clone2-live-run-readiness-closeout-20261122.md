# Live-run readiness closeout, batch 11 task 2

Date: 2026-11-22, 08:51-09:15 +07. Verdict: still NOT READY, but
narrower. The DOT 9 task 2 readiness check
(docs/clone2-live-run-readiness-clone1-20261122.md, 2afbde5 + fix
7d256ae) returned NOT READY with 11 missing items. This closeout
closes 4 of them (the ones closable from this machine, by
correcting the docs against primary sources) and leaves 7 open,
each with its owner and the exact step that would close it.
Nothing here was run live; no live run has happened.

Sources verified for this closeout (all read before writing):
- Readiness report: docs/clone2-live-run-readiness-clone1-20261122.md,
  319 lines, 2afbde5 + fix 7d256ae.
- Runbook before: docs/two-vision-live-runbook-20261122.md, 794
  lines, d2f6c40 + fix 2b98747. After: 1098 lines.
- Workflow doc before: docs/two-vision-benchmark-workflow-20261122.md,
  660 lines. After: 747 lines. Checklist section 10 rewritten
  in place (10.1, 10.2, 10.3, 10.4, 10.5).
- Script: tests/two_vision_bench.py, 868 lines, commit c267411
  (unchanged).
- AMEND4 item 12 code at todolist-push tip 65a2df6, 22/11:
  scripts/first_action.py (_scope_after def line 337, scope
  check before overlay lines 600-624, after-capture lines
  875-892); scripts/cu.py (G28 screen_scope line 1773, raise
  line 1775; _after_capture def line 2235, result['after']
  line 2241; a11y subparser line 2906, query requires --pid
  line 3150, --name/--role line 3151; STATE line 30);
  scripts/a11y.py (app lines 57-60, observe line 83, query
  line 118). Line numbers drift as the coordinator's lane
  lands commits; re-verify before citing.
- CDP building blocks: scripts/cdp.mjs and scripts/
  chromium_cli.py exist on both main and todolist-push.
- Messenger input name: searched both branches for any
  recorded DOM or a11y read of the live input (aria-label,
  saved observation JSON, a11y dump). None exists.

## What closed (4 items)

1. Runbook section 9 corrected for AMEND4 item 12. The code
   fix IS built on todolist-push (cbab398): the envelope
   carries BOTH `after` (scope-matching, chainable, built by
   _scope_after, first_action.py:337, stored at line 890) and
   `after_screen` (verification only, lines 880-883). The
   scope check fires before the overlay (lines 600-624,
   return 1 before the overlay acquire). The stale
   first_action.py "661-662" citation is fixed (those lines
   are now the G28 substitution refusal; the after-capture
   is at 875-892), the G28 citation is fixed (cu.py
   1773-1775, not 1665-1667), the _after_capture citation is
   fixed (cu.py 2235-2244, not 2102-2109), and the a11y
   citations are fixed (cu.py subparser 2906, query
   3150-3151, not 2773 and 3016-3020). The TESTREPAIR item
   12 residual is recorded: a scope-less meta WITH a window
   is treated as window scope. Caveat kept: the fix is on
   todolist-push, not necessarily installed on the laptop,
   so the guard stays mandatory on pre-amend code, and the
   runbook now requires recording which code version the
   laptop runs.
2. Checklist 10 contradictions fixed (all 4): 10.1 login-wall
   mode now says v12-timeout after typing into the email
   field, not no-message-input-in-inventory; 10.2 harvest
   now says it does NOT verify thread/bubble selectors;
   10.2 "ONE Zen instance" replaced with the G3 shape
   (Brave/Chrome on ws2) versus the option A shape
   (script's Firefox, two windows, one account); 10.1
   fresh-workdir rationale now says the false PASS comes
   from the V12 pre-check, not the ledger. The runbook and
   the checklist now agree.
3. Checklist 10.3 now complete as a definition: method
   (a11y query with the AT-SPI pid from `a11y apps`, never
   the hyprctl client pid), generation rule (fresh
   timestamp-based run_id, freshness from generation),
   record requirement (run log). The two-part dry probe
   procedure is written in runbook section 5, testing pid
   mapping and bubble exposure separately. The probe itself
   is UNRUN and stays open (item below).
4. VISION 2 monitor named (eDP-2, expected; confirm live
   with `hyprctl -j monitors`) and the run log file named
   (<run-dir>/run-log.md, every look logged with its time),
   in runbook sections 8 and 11 and workflow doc 10.4
   and 10.5.

## What is still open (7 items, each with owner and closer)

1. Live-shape decision (coordinator). Both procedures are
   written in full in runbook section 13: option B
   (primary, CDP driver to the real Brave/Chrome chats on
   ws2) and option A (fallback, script's Firefox with a
   pre-seeded logged-in profile). The account holding the
   two threads is still undecided in any repo record.
2. If option B: the CDP driver build. Building blocks
   exist (scripts/cdp.mjs: CDP transport with
   Runtime.evaluate, DOM.getBoxModel, harvest; scripts/
   chromium_cli.py: tab listing over DevTools HTTP), but
   no wiring from tests/two_vision_bench.py to cdp.mjs
   exists, and the user's own Brave/Chrome sessions run
   without a remote debugging port (verified 2026-11-18:
   no DevToolsActivePort file, nothing listening on 9222),
   so no CDP client can attach to them as they run today.
   Attaching needs the browsers relaunched with a debug
   port (coordinator decision) plus the driver build. The
   CDP input path on the Messenger contenteditable input
   is UNVERIFIED and needs a dry send first (the
   computer-use TYPE action silently failed on this exact
   input in Brave, CL1-MSG2, 9/9 executed, input stayed
   empty; CDP Input is a different path, but the warning
   stands).
3. If option A: a verified pre-seeded logged-in profile.
   No such profile exists yet; the account is undecided.
   Procedure is written (runbook section 13.2, steps 1-7).
4. Dry probe of the a11y freshness method (runbook
   section 5): UNRUN. Premise A (Messenger bubbles
   exposed through the a11y tree on Brave/Chrome) is
   UNVERIFIED; premise B (hyprctl pid is the AT-SPI pid)
   is contradicted by prior evidence
   (improvements/speed-proto-pick4-summary.md:15). Run
   the two-part probe on the laptop before the first
   live run.
5. Live Messenger input name verified against the real
   DOM: the aria-label is UNKNOWN. Only evidence is
   visual-only (two screenshot reads of the "Message"
   placeholder, worker-cl1msg-log.md:23 and
   worker-cl1msg2-log.md:18). No DOM or a11y read of the
   input exists anywhere in the repo. The runbook now has
   the rule for a non-"Message" name (stop, record the
   actual name, do not proceed). Closer: a live DOM read
   of the real input before the run.
6. Method approval (coordinator) and thread URLs, thread
   selector, bubble selector (coordinator). Both are
   coordinator decisions with no repo record yet.
7. Unbuilt script features, unchanged from the runbook:
   textNew in the V12 gate, pre-send reservation, V11
   MutationObserver flag, D3 ref stability. All listed in
   runbook section 12; none was built by this task.

Standing checks, not closable in advance: live lane must
be free at run time; live measurement of the 90% accuracy
bar is owed by the run itself (synthetic grounding is 7/7
= 100%, live proof does not exist yet).

## Hard constraint, kept

Rung 2 acceptance still runs on the real clone chats on
ws2, NOT the Firefox fixture, under either live-shape
option. Nothing in this closeout substitutes the fixture
for the live run.
