# OPTIMAL FIX METHOD: one systematic method for the whole error pile

Written 23:15-23:30 +07 Sat 2026-11-21 by Worker OPT (method coordinator). Branch todolist-push. No live tests, no laptop driving. No em dashes or en dashes anywhere.

## 0. Scope, status, and how to read this file

This is the ONE method for the whole error pile in the computer-use-wayland project (session/guardian startup, silence/slow first action, overlay visibility, Marionette/browser slot, Zen wedge/workspace, pill measurement, test design). It replaces per-error fumbling. It is concrete: commands, files, gates. It is not advice.

Sources incorporated, in order:
- Council M1 verdict: improvements/opt-council-m1-verdict.md (classes A, B, C).
- Council M2 verdict: improvements/opt-council-m2-verdict.md (methods D, E, F, G, commit method CM-1 to CM-6).
- Council ORDER verdict: improvements/opt-council-order-verdict.md (queue O-1 to O-7, test design, logging standard, commit method section 4).
- Redteam M verdict: improvements/opt-redteam-m-verdict.md (22 consolidated amendments AM-1 to AM-22, applied below; 3 struck items, section 12).
- Evidence bases: improvements/opt-crawl-src-20261121.md, improvements/opt-crawl-web-20261121.md, improvements/opt-crawl-zen-20261121.md, plus per-source annexes in improvements/opt-crawl-web-sources/ (S01-S14).
- Live state at write time: Y13r2 BLOCK (2fee242, B1-B4 + 5 amend, Y13g spawned to fix); re.py deletion root cause solved (Y13r2 redteam self-deleting shim A6e, VMFIX c16dd4e); H3 gate resolved (Y6 retry after Y13); F3 slot recurrence 22:56:12; merge 0ac4311 done 23:05, main HEAD 5c94e6c, graph 456 (target 240 exceeded).

Evidence contract (Lauren Tan, no exceptions): every claim in this file cites a file:line, a commit hash, or a log line. A claim without a citation is not a fact; it is a gap, and section 14 lists it as one. A method that assumes an unproven fact is marked AMEND (add the exact proof step) or KILL (the assumption is load-bearing and unprovable). Nothing in this file was executed as a live test by its author; execution belongs to the ranked workers, verification belongs to an independent checker, never the generator.

How to use this file: find your error class (sections 2-8), run its procedure in order, stop at the first gate that fails, and follow section 12 (stop/redirect/kill) instead of improvising. Do not skip steps. Skipping steps produces garbage code (owner order 22:48).

Standing bans: never ydotool. Fastest path first: CLI first, then DOM, mouse last. Omarchy menu and workspace switching by COMMAND, never by mouse click on bar buttons. Never drive the laptop live except through a ranked live run with its gates green. Never stop or redirect a running worker from this file; section 12 names who decides.

## 1. Ranking and fix order (amended ORDER queue)

Readiness judge: Worker OPT (AM-14). The judge names the written checklist (the gate list per run) and logs the decision with the gate states at decision time. Roles are sequential, not parallel lanes (AM-17): the 3-role test rule (generator, executor, checker) runs in sequence inside the 2-parallel-lane fleet cap.

Rank 1: F3 restore + slot-health rule (AM-6). Cleanup only with a post-close slot check after EVERY close batch. Rank 1 closes only on a G-RESTORE verification taken AFTER the last tab-close of the rank, with no tab-close between verification and closure. Keep-list is 14 real tabs + 1 sacrificial (not 28; the 28-tab target is struck, section 12). The 22:56:12 recurrence proves the rank-1 cleanup itself re-wedges the slot, so AM-6 is the single most urgent amendment in this file.
Rank 2: F1 + F2 cluster, F1 before F2 proof. F1 activation is gated on precondition 0 (slot health after the last tab-close) plus a proven lock wrapper (section 2). F2 act-now default is gated on the B1 pointer, the B3 classifier re-verification, and a measured 20s deadline (section 3).
Rank 3: ZT-B blind run. Gated on the ZT-05 rewrite to hl.dsp form (section 6), the G-12 fix (section 8), and the AM-6 slot rule.
Rank 4: Y6 pill retry. Runs AFTER Y13 (H3 resolution). A1-A10 whole, load-only trial first, A3 marker settled per AM-12 before the 4-8 hours of A1-A10 work are spent (section 7).
Rank 5: Y13 live. Gated on Y13g's deliverable: fix diff + fresh re-review. Y13g has zero observable output (no log file, no commits) at write time; the stall rule in section 12 applies (record the stall, reassign, do not let rank 5 wait on an invisible worker).
Rank 6: Y14 live.
Rank 7: A1 pilot.
Rank 8: Hidden-body decisive experiment. Gated on the AM-13 Phase 2 sentence and the AM-22 pre-flight measurement (section 8).
Rank 9: Clone2 heavy batch.
Rank 10: Y1b.
Rank 11: Scrub. AM-15: name the scrub date and owner and price the re-clone (every agent re-clones), or defer plainly after the final test and say the final test is then the last work item, not the last executed item. The PII scope count (71 lines / 45 files) is uncited until the sweep is cited.
Rank 12: Final test LAST. Independent Codeforces contest, 5 problems via Polygon, no Hieu permissions, no effect on anyone, goal 5 problems live in the contest, tight per-step time logging.

Parked: E1 fresh comparison (AM-16: set a review date, or state explicitly that parking is permanent pending the owner re-opening it). Track 2 / speed loop (paused, resumes only on council + redteam unanimous agreement). Super I (deferred). 2.1.7 I7 video (needs the owner to re-send the original file). Pending user decisions. Zen keybinds recording (owner order 23:03, deferred, low: machine-specific layer, local-only, never repo; ZK probe 81a3bc4).

## 2. Class A: session / guardian startup failure

Root cause (proven, F1 Layers 1-4, SRC section 1): check_guard at scripts/cursor_theme.py:122-124 gets `unknown request` with exit 0 from an unloaded plugin; the login loader failed at manifest_validation (scripts/visuals.py:258-274) because laptop optics (09a8df7, blur 0.0) and manifest pin (d27ad0a, blur 0.10) were two different stale commits vs b2afcd1 (blur 0.15). F1's diagnostic fix is committed (5033c9d). New candidate from SRC: indicator.listen() at scripts/indicator.py:125-135 binds without unlinking a stale socket, so a hard-killed guardian can block the next start; test it before any other new A candidate is opened.

Procedure (M1 A steps, as amended by REDTEAM-M):
- A1, verify the d27ad0a sha: CLOSED. Redteam verified `git show d27ad0a:native/hyprglass-local-optics.lua | sha256sum` = 674441ea, matching the pin exactly. Record the closure; the step is done. Do not re-execute it.
- A2, code gaps in the diagnostic path: AM-1. Strike items A1-A6 (they landed in 392bc09 at 22:55:43 +07 and 5b11696 at 22:56:44 +07). Keep A7 only: assert the exact envelope string `session guardian startup failed: cursor guard reply is not valid JSON` in stdout in tests/test_cursor_session.py, replacing the `not valid JSON` substring assertion at line 791. Re-pin line citations to current code (guard_reply scripts/cursor_theme.py:104, supervise scripts/cursor_session.py:212). Require an independent re-run of the tests; F1's "34 OK" claims are self-reported and do not count.
- A3, durability re-pin check: SURVIVES. Add the check to sync-installed/setup so a future optics/manifest drift is caught at install time. The check must fail loudly WITHOUT failing the login itself; that distinction is the step's falsifier.
- A4, live activation under preconditions 1-8: AM-2. Add precondition 0: slot health verified AFTER the last tab-close, immediately before activation (POST /session once, or BiDi getTree). Precondition 1 (Zen PID stable after F3 sign-off) cannot be met while the slot re-wedges within seconds of a tab close (F3 log 22:56:12), so precondition 0 is load-bearing. Prove the lock-holding wrapper exists as a file with a path before step 4 runs, or record that activate-cursor-guard.py:63 already holds the lock and no wrapper is needed. No wrapper file is cited anywhere yet (Skeptic P-6).
- A5, proof of restoration: SURVIVES. The falsifier is well-formed: any one of session still dies, cu-cursor status still `unknown request`, pill never appears.
- A6, gate the session on hyprglass active: AM-3. Quantify the shader warm-up window in seconds with a measurement, decide marker-publish vs code gate, and name the refusal behavior (what the session prints, what the remedy is, whether a bypass exists) before the gate lands. This step needs its own council + redteam first, as the M1 verdict already says.
- A7, tracked recurrence follow-up: SURVIVES. Process step; the cost of skipping it is the next optics change repeating the incident.

Fastest verification path: CLI first (`git show <sha>:<path> | sha256sum`, `cu-cursor status`, log grep), then DOM (none for this class), mouse last (never for this class). Evidence required: the sha output, the exact envelope string in test output, the precondition-0 slot check output saved to a file, the wrapper file path.

## 3. Class B: silence / slow first action

Root cause (proven, SRC section 2): the 5-minute silence was agent-side, not code slowness (no path sleeps minutes). The old chain is observe (120s freshness) -> session (15s ready + 2s registered) -> act, with no overlay and no progress reporting. The owner order (22:21) sets the bar: FAST + CONTINUOUS ops + overlay MUST show; target under 30s from order to first visible action. Biggest structural gap: timing.py, step_watchdog.py, drive_log.py exist with tests but are imported by NOTHING on the live path (only live_metrics.py / task_chain.py reference them, and nothing imports those). That is why J5 left no timing record. Wire them into the live path, or record a reasoned rejection, before any new B timing claim is made.

Procedure (M1 B steps, as amended by REDTEAM-M):
- B1, act-now as the default path: AM-4. The code is landed (a576e69, 8d1f775), but the gate is not met: the old `act` path prints no pointer to act-now in its refusal text (grep `act-now` in scripts/cu.py hits only lines 2311 and 2491). Add the act-now pointer to the require_session refusal text (scripts/cu.py:2599-2602), or strike the B1 gate. Record in the M1 verdict that the F2 rehearsal ran while G-F1-BEFORE-F2 was NOT green (F1 activation pending), so the rehearsal evidence covers the fallback path only.
- B2, overlay gate in code on both paths: SURVIVES. No overlay, no action, on either path. Note the cold-start dependency: daemon up to 15s plus liquid warm-up up to 30.0s can exceed the 30s target before any action (SRC B7a); B6 must settle the constants from measurement.
- B3, 20s deadline + fallback: AM-5. The 20s constant is unmeasured. The classifier has a dead branch (`Expecting value`, post-392bc09). session_live() returns False on any transient socket error and can authorize a replay while a session is live (scripts/overlay.py:146-161, scripts/first_action.py:296). Re-verify is_session_start_failure (scripts/first_action.py:157-177) against post-392bc09 error strings, one test per branch by an independent checker. Measure the session-start distribution (at least 10 starts, cold and warm) before the 20s deadline goes live as the default. Test the transient-socket case for session_live().
- B4, rehearsal on a harmless composite task: AM-6. The prescribed task (open a tab, navigate, close only that tab) collides with the 22:56 finding: closing a window/new-created tab is the prime suspect for re-wedging the slot. Add a post-close slot check (POST /session once, or a BiDi getTree) before the rehearsal is called done.
- B5, measure and publish timings: SURVIVES.
- B6, re-set constants from the measured distribution: SURVIVES. Note: one rehearsal run gives n=1, not a distribution; the worker must state how many runs make a distribution before claiming it.
- AM-21, late binding (WEB S6, orphaned by every council): adopt Chronotope late binding in M1 B (re-read the DOM rect immediately before dispatch, record E/O/D/A clocks) or record a reasoned rejection. Do not leave the WEB crawl's synthesis step 2 undecided. Evidence for it: OSWorld-Human (planning/reflection 75-94% of latency, later steps 3x), TOCTOU gap mean 6.51s with PUSV 100% interception under 0.1s, Chronotope late binding 0/100 to 100/100 with no extra model call. Converges on: decide on element identity, bind coordinates late from a fresh DOM read, re-verify pre-dispatch, cut LLM calls per step.

Fastest verification path: CLI first (timing logs, session-start distribution from the log, classifier unit tests), then DOM (fresh DOM read immediately before dispatch), mouse last (the rehearsal itself, once, with the post-close slot check). Evidence required: the distribution (n stated), one test per classifier branch, the transient-socket test, the post-close slot check output.

## 4. Class C: overlay visibility (never shows, flicker)

Root cause (proven, SRC section 3): the plain `act` path never touches the overlay, so the 22:17 click was invisible by construction. Every observation hides+shows the pill (scripts/cu.py:921,958 via capture_clean), 4-6 toggles per batch. The strongest I12 candidate is in native code: any stdin command arriving during a redraw QUITS the indicator (native/indicator.c:371-378 and redraw() line 244), and session-owned natives have no respawn (daemon respawn covers daemon-owned only). The daemon 2s monitor re-send is provably inert (duplicate show/label are no-ops in the native). Liquid-mode flicker itself is still UNPROVEN; the cited flicker log file does not exist in the VM repo (gap G3). Y6 pill measurement retry must precede any flicker fix.

Procedure (M1 C steps, as amended by REDTEAM-M):
- C1, never shows (5 steps): AM-7. Step 3 (watchdog live proof) must specify daemon-owned indicator only, with the session alive through the proof: the daemon respawns only daemon-owned natives; session-owned natives have no respawn and kill the session instead (scripts/cursor_session.py:166).
- C2, flicker (4 steps): SURVIVES. Split C1 (class A spine + hyprglass gate + watchdog-respawn proof + E1 logging) and C2 (measure ONLY in the nested Hyprland, owner choice C, four-cell repaint counts, never load hyprglass live, veto V1). Note: the repaint count does not observe the overlapping-command quit (SRC C7, native/indicator.c:371-378), the strongest code-level candidate for I12; no verdict says which experiment covers it, so the C2 worker must name the experiment that covers it before running.
- Falsified, do not revive without new E1 evidence: indicator-at-idle, screenshots-cause-flicker. Both are recorded as already falsified in M1; reviving either without new E1 evidence is a method violation.

Fastest verification path: CLI first (native code read, daemon vs session ownership from scripts/cursor_session.py:166), then DOM (none for this class), mouse last (never for measurement; nested-only for C2). Evidence required: the ownership of the killed indicator, the saved repaint counts, the named experiment for the overlapping-command quit.

## 5. Class D: Marionette / browser slot (browserElement is null)

Root cause (proven, ZEN section D): the throw site is driver.sys.mjs line 4616 `browserElement.namespaceURI` with no null check, called unchecked from #registerWindow line 4640, looped over all tabs by newSession line 2707. Lazy tabs are proven NOT the cause (restart works with about 52 lazy tabs). Prime suspect (unproven): a tab mid-removal with null linkedBrowser from the pass-1 cleanup teardown (DELETE /session while current was a discarded tab). Strongest new evidence: F3 slot recurrence 22:56:12, POST 500 again 7 seconds after close3 closed window/new-created tabs.

Procedure (M2 D steps, as amended by REDTEAM-M):
- D-1, BiDi liveness probe first; POST once. On the exact `browserElement is null` 500, diagnose before anything else.
- D-3, diagnose: AM-9 teeth. The worker that observes a slot failure saves the BiDi getTree + tab list to files BEFORE any other step and names the file paths in its log. D-3 was not executed at the 22:56 recurrence (no getTree file); that is a method violation to record, not a gap to re-litigate.
- D-4, restart by the F3-proven sequence: snapshot tab list first, `pkill -TERM`, zero processes, zen-ai relaunch, verify 200/2828. POST once more.
- D-6, durable repo-code fixes, pulled EARLIER in the execution order on cost grounds (AM-9): the restart tax is about 2-3 minutes plus one unflushed tab per occurrence, paid 7 times in one evening. The fixes: zen_dom.py geckodriver log to file + PID file (run_live.py already has both; zen_dom.py has neither), and run_live.py WD takes the shared zen_dom.lock (currently run_live.py never takes zen_dom.lock, so "one runner at a time" is prose, not code).
- D-7: STRUCK. The 28-tab target (13 real + 14 about:blank + 1 httpbin + 1 BiDi fixture, 22:10 baseline) contradicts F3's executed cleanup (AFTER 15 tabs, 14 real + 1 sacrificial, 22:54-22:56) under the owner steer to delete tabs definitely no longer used. Replaced by AM-6 (section 1, rank 1): 14 real tabs + 1 sacrificial, blanks closed, plus the provenance rule: never close window/new-created tabs via Marionette teardown without a post-close slot check (POST /session once, or BiDi getTree) after EVERY close batch.
- D-2, omni.ja patch veto: AM-8. Restate the veto on its cited grounds only (repack on every Zen update, restart already clears the zombie). The signature premise is uncited (opt-council-m2-mechanism.md:35 is the only occurrence); either cite a source for it or strike it. BiDi-only was falsified twice and stays falsified.

Fastest verification path: CLI first (BiDi getTree, POST /session, pkill, zen-ai relaunch, curl 200/2828), then DOM (none for this class), mouse last (never; the 22:44 rail click proved the far-left rail is the Omarchy dock, not a workspace switch). Evidence required: the saved getTree + tab list file paths, the restart verification output, the post-close slot check output after every close batch.
