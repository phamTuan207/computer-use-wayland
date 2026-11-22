# Live-run readiness closeout, batch 11 task 2 (fix pass)

Date: 2026-11-22, 08:51-09:30 +07. Verdict: still NOT READY.
Count after the fix pass: 2 fully closed, 3 partial, 5 open,
2 standing. The DOT 9 task 2 readiness check
(docs/clone2-live-run-readiness-clone1-20261122.md, 2afbde5 + fix
7d256ae) returned NOT READY with 11 missing items. The first
closeout claimed 4 closed and 7 open; council 1, 2, 3 and the
redteam broke that count, and this fix pass corrects it.
Nothing here was run live; no live run has happened.

Numbering in this report matches runbook section 12 exactly
(items 1-12). Mapping to the readiness report's 11 items:
fully closed are readiness 1 (section 9 / AMEND4 item 12) and
readiness 9 (VISION 2 monitor + run log named); partial are
readiness 2 (checklist 10 contradictions), 3 (10.3 definition
+ dry probe), 5 (live-shape procedures); open are readiness 4
(input name), 6 (method approval), 7 (thread URLs/selectors),
8 (unbuilt features), plus new item 10 (cross-origin frames,
from the DOM/a11y crawl log, not in the readiness report);
standing are readiness 10 (live lane free) and 11 (90% bar
live measurement).

Sources verified for this closeout (all read before writing):
- Readiness report: docs/clone2-live-run-readiness-clone1-20261122.md,
  319 lines, 2afbde5 + fix 7d256ae.
- Runbook before: docs/two-vision-live-runbook-20261122.md, 794
  lines, d2f6c40 + fix 2b98747. After the closeout: 1098 lines.
  After this fix pass: see the fix-pass commit.
- Workflow doc before: docs/two-vision-benchmark-workflow-20261122.md,
  660 lines. After the closeout: 747 lines. After this fix pass:
  see the fix-pass commit. Checklist section 10 rewritten
  in place (10.1, 10.2, 10.3, 10.4, 10.5).
- Script: tests/two_vision_bench.py, 868 lines, commit c267411
  (unchanged).
- AMEND4 item 12 code at todolist-push tip e702398, 22/11:
  scripts/first_action.py (_scope_after def line 337, scope
  check before overlay lines 600-627, after-capture lines
  875-893); scripts/cu.py (G28 screen_scope line 1773, raise
  line 1775; _after_capture def line 2235, result['after']
  line 2241; a11y subparser line 2906, query requires --pid
  line 3150, --name/--role line 3151; STATE line 30);
  scripts/a11y.py (app lines 57-60, observe lines 83-117,
  query line 118). On main the same a11y code is at cu.py
  lines 2332 and 2519-2520. Line numbers drift as the
  coordinator's lane lands commits; re-verify before citing.
- CDP building blocks: scripts/cdp.mjs and scripts/
  chromium_cli.py exist on both main and todolist-push, but
  their capabilities differ by branch (see item 5 below).
- Messenger input name: searched both branches for any
  recorded DOM or a11y read of the live input (aria-label,
  saved observation JSON, a11y dump). None exists.

## Fully closed (items 1-2)

1. Runbook section 9 corrected for AMEND4 item 12. The code
   fix IS built on todolist-push (cbab398): the envelope
   carries BOTH `after` (scope-matching, chainable, built by
   _scope_after, first_action.py:337, stored at line 890) and
   `after_screen` (verification only, lines 880-883). The
   scope check fires before the overlay (lines 600-627,
   return 1 at 627, overlay acquire at 630). The stale
   first_action.py "661-662" citation is fixed (those lines
   are now the G28 substitution refusal; the after-capture
   is at 875-893), the G28 citation is fixed (cu.py
   1773-1775, not 1665-1667), the _after_capture citation is
   fixed (cu.py 2235-2244, not 2102-2109), and the a11y
   citations are fixed (cu.py subparser 2906, query
   3150-3151, not 2773 and 3016-3020). The TESTREPAIR item
   12 residual is recorded: a scope-less meta WITH a window
   is treated as window scope. Caveat kept: the fix is on
   todolist-push, not necessarily installed on the laptop,
   so the guard stays mandatory on pre-amend code, and the
   runbook now requires recording which code version the
   laptop runs. (Readiness item 1.)
2. VISION 2 monitor named (eDP-2, expected; confirm live
   with `hyprctl -j monitors`) and the run log file named
   (<run-dir>/run-log.md, every look logged with its time),
   in runbook sections 8 and 11 and workflow doc 10.4
   and 10.5. The eDP-2 attribution is one inference step:
   the only repo record naming eDP-2 is a ws1 observe
   (worker-cl1msg2-log.md:14); the ws2 box matches it, so
   eDP-2 is expected, not proven, and the live check stands.
   (Readiness item 9.)

## Partial (items 3-5: the doc part is done, a live or build part remains)

3. Checklist 10 contradictions fixed (readiness item 2).
   The four flagged contradictions are fixed in workflow
   doc section 10 (login-wall mode, harvest selector
   checking, "ONE Zen instance", ledger rationale), and the
   runbook and the checklist now agree on those four. What
   remains, found by the fix-pass reviewers: the workflow
   doc section 5 Step 0 ledger sentence still carried the
   same wrong rationale (fixed in this pass: the false PASS
   comes from the V12 pre-check, not the ledger); workflow
   10.4 still attributed a missing harvest input to
   no-message-input-in-inventory, which harvest mode never
   emits (fixed in this pass: the FAIL is an operator
   judgment, the error fires only in run mode); and the
   one-instance and Firefox-path wording is now qualified
   by live shape (option A only, option B uses two
   browsers).
4. Checklist 10.3 definition complete, dry probe open
   (readiness item 3). The definition is complete: method
   (a11y query with the AT-SPI pid from `a11y apps`),
   generation rule (fresh timestamp-based run_id), record
   requirement (run log). What remains: the dry probe
   procedure is written in runbook section 5 but the probe
   itself is UNRUN, and the probe method as first written
   cannot work (see item 7 below for the observe() filter
   limit). The probe is redesigned in this pass.
5. Live-shape procedures written for both options
   (readiness item 5). Both procedures are written in full
   in runbook section 13: option B (primary, CDP driver to
   the real Brave/Chrome chats on ws2) and option A
   (fallback, script's Firefox with a pre-seeded logged-in
   profile). What remains:
   - The coordinator's decision (option B or option A) and
     the account decision (owner: coordinator).
   - If option B: the CDP driver build (owner: whoever
     builds it). Building blocks exist but differ by branch,
     and the first closeout overstated them:
     scripts/cdp.mjs on main has NO harvest operation, NO
     DOM.getBoxModel, NO Accessibility.getFullAXTree (its
     operations are tabs/observe/act; snapshot returns rects
     via getBoundingClientRect, capped at 80 with a truncated
     flag); the harvest with DOM.getBoxModel cross-check
     (line 276) and Accessibility.getFullAXTree (line 253)
     exists on todolist-push only. DOM.getBoxModel and
     Accessibility.getFullAXTree are still open per the bench
     script's own TODO (tests/two_vision_bench.py lines
     61-64). scripts/chromium_cli.py default endpoint is
     http://127.0.0.1:9222 on main and http://127.0.0.1:9223
     on todolist-push; the repo contradicts itself on the
     port (cu.py lines 32-40 say the agent-managed Chromium
     is 9223 and 9222 is Zen's BiDi port), so --endpoint must
     be passed explicitly per browser. No wiring from
     tests/two_vision_bench.py to cdp.mjs exists; the driver
     build must implement harvest, send chain, V12 gate, HCU
     guard, V1 readback, V11, and the exactly-once pre-check,
     and the ledger is a Python in-process class while cdp.mjs
     runs as a separate Node process, so cross-process ledger
     reuse needs wiring that does not exist. The no-debug-port
     evidence covers Chromium only (verified 2026-11-18: no
     DevToolsActivePort file, nothing listening on 9222);
     Brave/Chrome debug-port state is UNVERIFIED and must be
     checked live before asserting option B requires a
     relaunch. Further caveat: Chrome/Brave refuse the
     --remote-debugging-port flag on the default user data
     directory and need a custom profile, and the debug port
     cannot be enabled on an already-running browser
     (improvements/worker-click-crawl-doma11y-log.md, open
     verification item 4); a custom profile would NOT carry
     the login session. The CDP input path on the Messenger
     contenteditable input is UNVERIFIED and needs a dry send
     first.
   - If option A: a verified pre-seeded logged-in profile
     (owner: operator, on the laptop). No such profile exists
     yet. The procedure was corrected in this pass: the script
     has NO binary-path flag (FF/GD are module constants,
     script lines 49-50), so the laptop needs an edit to FF/GD
     (changing the section 3 pin) or the exact /home/hatch
     paths to exist; the cache exclusion is cache2 and
     startupCache, NOT a `Cache` directory (no such directory
     exists in a Firefox profile, verified live 22/11);
     storage/ and cookies.sqlite must NOT be excluded (they
     may hold the session); the copy size must be measured
     live (512M /tmp budget unproven, an empty profile is
     about 23M); and the COPIED profile must be verified to
     load logged in, since profile portability is an
     assumption, not evidence.

## Still open (items 6-10)

6. Live Messenger input name verified against the real DOM
   (owner: operator, on the laptop, before the run): the
   aria-label is UNKNOWN. Only evidence is visual-only (two
   screenshot reads of the "Message" placeholder,
   worker-cl1msg-log.md:23 and worker-cl1msg2-log.md:18).
   No DOM or a11y read of the input exists anywhere in the
   repo. The runbook now has the rule for a non-"Message"
   name (stop, record the actual name, do not proceed).
   Closer: a live DOM read of the real input before the run.
   (Readiness item 4.)
7. Dry probe of the a11y freshness method (owner: operator,
   on the laptop, before the first live run): UNRUN, and
   the method as first written cannot work. scripts/a11y.py
   observe() (lines 83-117) only keeps elements with
   actions, editable, or in skeleton mode, and describe()
   records name/role/actions only, never text content;
   query() calls observe() without skeleton and filters that
   already pruned list by name substring, so a bubble
   (static text, no actions, not editable) is dropped before
   query() sees it. A bubble-text query returns matched 0
   even when bubbles are fully exposed. The probe is
   redesigned in runbook section 5: Part 1 proves the pid
   mapping with an element that survives the filter (a
   named button or the editable message input), with a
   branch for Brave/Chrome absent from `a11y apps` (only 6
   registered apps on record, none named Brave/Chrome);
   Part 2 tests bubble exposure explicitly with a skeleton
   observe, and a miss in both proves nothing definitive.
   Until Part 2 hits, freshness rests on generation alone.
   Premise A (bubble exposure) is UNVERIFIED; premise B
   (hyprctl pid is the AT-SPI pid) is contradicted by prior
   evidence. Under option A this method does not apply at
   all (no Brave/Chrome targets). (Readiness item 3, probe
   part.)
8. Method approval (owner: coordinator) and thread URLs,
   thread selector, bubble selector (owner: coordinator).
   Both are coordinator decisions with no repo record yet.
   (Readiness items 6 and 7.)
9. Unbuilt script features (owner: whoever builds them):
   textNew in the V12 gate, pre-send reservation, V11
   MutationObserver flag, D3 ref stability. All listed in
   runbook section 12; none was built by this task.
   (Readiness item 8.)
10. Cross-origin frames in the Messenger web app (owner:
    operator, on the laptop, before the run): DOM rects
    cannot reach cross-origin iframes from parent JS
    (same-origin policy); BiDi browsing-context-scoped calls
    or vision remain the fallback
    (improvements/worker-click-crawl-doma11y-log.md, open
    verification item 6). The Messenger web app used in the
    benchmark must be checked for cross-origin frames before
    the benchmark runs. This affects both options: HARVEST_JS
    and the cdp.mjs snapshot both evaluate in the top frame.
    (New item, found by the fix-pass redteam; not in the
    readiness report.)

## Standing (items 11-12, checked at run time, not closable in advance)

11. Live lane must be free (readiness item 10): no BASELINE2
    or other live run running, and no other agent holding
    the laptop browser.
12. Live measurement of the 90% accuracy bar (readiness item
    11): no live measurement exists yet. Synthetic grounding
    is 7/7 = 100%; the live proof is owed, and the run itself
    must produce it. This is measured by the run, not a
    prerequisite to start.

## Hard constraint, kept

Rung 2 acceptance still runs on the real clone threads,
NOT the Firefox fixture, under either live-shape option
(ws2 with Brave/Chrome applies to option B only; option A
runs the threads in the script's Firefox). Nothing in this
closeout substitutes the fixture for the live run.
