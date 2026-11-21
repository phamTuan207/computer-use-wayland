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

## 6. Class E: Zen wedge / workspace switching

Root cause status: J1 mechanism UNPROVEN (no click attempted during the wedge). J2 has no captured symptom at all. The far-left rail is the Omarchy dock, not Zen workspaces: F3's 22:42-22:45 clicks proved (15,30) is the app launcher and Logo+1 opens the system menu, which makes F3 the likely actor in the owner-reported 22:44 workspace-1 click that opened the Omarchy menu. Two workspace systems are conflated in the record (Hyprland vs Zen-internal); the latter has no test. F1 guardian failure (check_guard JSONDecodeError on "unknown request", exit 0) is a separate wedge that looks identical to the owner; wedge and slot stay separate until a capture proves otherwise.

Procedure (M2 E steps, as amended by REDTEAM-M):
- E-1, workspace switching: AM-10. Turn E-1 into a LIVE PROBE, not just a config read: run `hl.dsp.focus({ workspace = "N" })`, verify with activeworkspace + clients + screenshot, save the outputs. The string exists in repo precedent (hyprctl dispatch 'hl.dsp.focus({ workspace = "N" })', tests/browser_field_live.py line 98 and others), but no live run proves it switches workspaces on this Hyprland 0.57.2, and F3 introspection shows hl.dsp.workspace has NO goto/switch.
- E-3, Zen keybinds: AM-10. Make E-3 conditional on the E-1 probe passing. Cite the local-only keybind record (ZK probe, commit 81a3bc4: customKeys.json in the Zen profile, 3 customized keys, file + defaults merge, never on the repo) rather than any repo file, per the owner order 23:03. Zen keybind recording is deferred, low priority, machine-specific layer only.
- Launcher command, found by F3: `omarchy-menu toggle root`, SUPER+SPACE, ~/.config/hypr/bindings.lua (F3 log 22:50). ZEN G-06 is closed. Record it here so no worker re-derives it by clicking.
- E-4, wedge-signature capture: AM-11. A restart without a signature is called a safety violation, but no enforcement names who checks it; the 22:56 recurrence produced no signature either. Name the enforcer: the checker role verifies the signature files exist before any restart is approved. Capture the wedge signature BEFORE any restart, every time, no exceptions.
- E-2, E-5, E-6: SURVIVE as written in the M2 verdict.
- ZT-05 steps 2, 3, 5 rewritten from Super+M/N keybinds to the hl.dsp form before ZT-B runs. J2 fix is gated on the ZT-05 observation. Zen-internal workspaces need a new scenario or a recorded out-of-scope decision.

Fastest verification path: CLI first (hyprctl activeworkspace + clients, the hl.dsp command form, the launcher command from config), then DOM (none for this class), mouse last (never for workspace switching; the 22:45 CLI-first order stands). Evidence required: the saved E-1 probe outputs, the wedge signature files, the checker approval before any restart.

## 7. Class F: pill measurement 2.2.3 (Y6r A1-A10)

Root cause status: F1 dead ABI proven fixed at link level (.so md5 78ac1023, ldd 0 not found). Y6r reversal confirmed: the profile config WAS applied on parse 2 (layers.enabled true, default false, optics.lua only setter); U6 is a deterministic false-fail gate; manual `nest hyprctl reload` must NOT be added (redteam wins, R2). The retry dies first at the ldd pre-flight because the y6e conf was never staged as the active conf (A1). The liquid gate is proven blind as code fact. Pill measurement itself is still UNPROVEN; no arms ever ran live. Y6 retry runs AFTER Y13 (H3 resolution).

Procedure (M2 F steps, as amended by REDTEAM-M):
- Adopt Y6r A1-A10 whole. Load-only trial first (F-8). Fresh re-review before any measurement.
- A1 staging, with saved ldd output (new-conf ldd output was never saved, gap G-10; saving it is part of A1, not an afterthought). A3 positive marker in nest optics.lua only. U6 replaced by a positive gate (A2). AMEND4/AMEND5 ported (A5).
- No manual reload (R2 confirmed by independent re-argument). Falsifier: marker absent in the F-8 load-only trial promotes reload to the next test.
- AM-12, the second most urgent amendment in this file: the A3 marker proves the calls returned, NOT layer registration or values. Either strengthen the marker with a registration read-back after layer() returns, or downgrade ORDER O-2 to "proves the calls returned" and keep the registration question open after the retry. Settle this BEFORE the 4-8 hours of A1-A10 fix work are spent. Note the n=1 caveat on parse-2 determinism; the F-8 load-only trial is the test that settles it.

Fastest verification path: CLI first (ldd output saved, parse-2 config read, marker grep), then DOM (none for this class), mouse last (never). Evidence required: the saved ldd output, the A3 marker output, the registration read-back (or the written downgrade of O-2).

## 8. Class G: hidden-body experiment + blind test design

Root cause status: V1 badly wounded, not dead (R's "no class" is two concordant records, output never saved). V2 dead as stated (CSS visibility interpolation rule, two sources). Third mechanism sketch recorded (grouping-rule / unreadable-sheet blind scan). Four record corrections stand: switch-away never tested, "cleared by itself" mislabelled, bootstrap mechanism story false, geckodriver-kill causation unproven. Y13r2 BLOCK (2fee242, B1-B4 + 5 amend); Y13g is fixing per the redteam paper, then a fresh re-review runs.

Procedure (M2 G steps, as amended by REDTEAM-M):
- Adopt the Y4b diagnose-first fix design (V2 category removed, repaint and switch-away steps removed, flagged passes counted separately) plus the 6-phase decisive experiment (old-versus-new pair is the key capture; V1 refuted by one saved counterexample) plus the ZT-A v2 blind composite suite.
- AM-13: add one sentence to G-7 Phase 2: switch-away-and-back is a diagnostic on a test tab with the owner away, never a recovery step, and must not be copied into the fix ladder. This reconciles G-2's switch-away removal with G-7 Phase 2, which includes switch-away-and-back on the same hidden tab.
- Close G-12 (ZT-00 step-4 wording, wrong zen_dom.py path) before ZT-B runs. G-9's ZT-B run is blocked on G-12, which is still open.
- Cite the H3 acceptance in a council paper or log entry, not only MEMORY.md 22:57. Name Y13g's deliverable (fix diff + fresh re-review) as the rank-5 gate item; Y13g has zero observable output (no log file, no commits) at write time.
- AM-22: measure the diagnose_body pre-flight false-positive rate and perturbation cost on healthy tabs BEFORE O-6 becomes a gate on ranks 5-7. The measurement is owed (Skeptic P-12); O-6 makes the pre-flight a gate on every live run at ranks 5-7, so an unmeasured gate is a method violation.
- G-1, G-3, G-4, G-5, G-6, G-8 survive as written in the M2 verdict; the V1 burden placement is correct.

Fastest verification path: CLI first (diagnose_body snapshot, BiDi getTree, saved counterexample), then DOM (the old-versus-new pair capture), mouse last (never for diagnosis). Evidence required: the saved counterexample (V1 refutation), the Phase 2 diagnostic outputs, the pre-flight false-positive measurement.

## 9. Test design (blind, composite, generator never tests its own work)

Rules (ORDER section 2, as amended by AM-17):
- Tests are composite and blind: the ZT-A v2 blind composite suite (ZT-01 to ZT-10 + ZT-00 health gate) is the template. The generator never runs its own tests; an independent executor runs them, an independent checker cross-checks. A claim of "fixed" without a passing live task test is worth 0 points.
- Roles are sequential, not parallel lanes (AM-17). The three-roles-three-workers rule is unreconciled with the 2-parallel-lane fleet cap unless the roles run in sequence; state the sequence in every brief or the rule is unimplementable under the cap.
- Late binding (WEB S6 + AM-21): decide on element identity, bind coordinates late from a fresh DOM read, re-verify pre-dispatch, cut LLM calls per step. Adopt it in class B (section 3) or record a reasoned rejection. Do not leave it undecided.
- Replay control, state variation, end-state grading (WEB class f, Agentic Frontier / D'Oro): a replay script scores 71.1% vs 70.6% OSWorld, but DigiWorld's 3.2M configs drop replay to 6.90% vs model 45.7%. A test that a replay script can pass is not a test of the agent; vary the state, grade the end state.
- Marionette probes (WEB class d, Bugzilla 2081625): probe for the hello greeting and fail in 4-6ms instead of a silent 60s hang. Bugzilla 1682062 backs the never-close-the-selected-tab rule (section 5).
- Overlay/pill visibility (WEB class c): NO PUBLISHED FIX exists, only open Hyprland issue 15738. The fix must be local and live-proven; no web source substitutes for the nested measurement in section 4.
- A1 pilot (frozen 18:46, clone1 review 28 holes / 3 blockers, commit 1ddac2d): resume only after the blockers are addressed and the preconditions hold (written order naming 12 run-ids, broker SOLO + idle, relay verified, Layer-2 probes, checker cross-check).

## 10. Logging standard (continuous event logging, with enforcement)

Rules (ORDER section 3, as amended by AM-17 and AM-20):
- Every agent appends EVERY event to its log file AS IT HAPPENS: wall-clock Asia/Ho_Chi_Minh + elapsed, command, target, outcome, coordinates for clicks. Never batched at the end. The log must answer any owner question (who did what, when, with what result). If the owner asks and the log cannot answer, the logging failed, not the owner.
- Enforcement (AM-17): the brief template carries the logging line, and the checker role runs a log-completeness check before any verdict is accepted. A verdict with an incomplete log is not accepted. Until the enforcement runs, the standard is unenforced prose; say so in the brief if the checker is absent.
- Pre-commit review (AM-20): `git diff --cached --stat` reviewed before every commit, recorded in the log. This is the check that prevents another 26366a9 (section 11).
- Owner order 23:01 (overnight reporting): big errors, blockers, and anything needing the owner's decision are reported AT ONCE, overnight, not held for the morning. Routine work stays silent; results are reported in the morning. The coordinator escalates a redteam KILL, a rank-1 recurrence, or a stalled gate worker the moment it is known.
- Lessons go in both places (standing rule): a generic version in the repo, a detailed version on the laptop, no personal info in the repo. Self-deleting shims are a hazard class: the Y13r2 shim A6e deleted re/__init__.py by mistake (globals().update overwrote __file__ before os.remove); any self-deleting shim must be redteamed for __file__ overwrite before use.

## 11. Commit method (small, many, push immediately, merge to main)

Rules (ORDER section 4 + M2 CM-1 to CM-6, as amended by AM-19 and AM-20):
- One step = one commit. Push immediately after each step. Verify each push via ls-remote, or via fetch + merge-base ancestry check when the remote moves fast. A "remote rejected" message can be a race artifact: verify ancestry before assuming loss (proven live: d0fa2a1 landed despite a lock error).
- The graph counts ONLY default-branch (main) commits on the UTC day. This is now empirically confirmed, not just asserted: merge 0ac4311 (313 commits) moved the graph from 145 to 456 at 23:05 (main HEAD 5c94e6c). todolist-push commits do not move it. Merge to main early and often; Worker MERGE owns the merges; every merge is verified via ls-remote AND the graph is re-checked after, not assumed.
- Target 240 is EXCEEDED (456 at 23:05). Archive the 4.3 deadline arithmetic (gap about 95, 68 minutes left); do not repair it. The commit method's remaining value is reviewability, not the count. Say so in every brief from now on, or the pressure to commit small-and-many continues past its payoff.
- Hygiene: `git status` before every commit. `git commit --only` for your own files (new files: `git add` only your exact path first, since --only fails on untracked paths). Never force-remove a live .git/index.lock; wait, re-check, retry. On push rejection, fetch + rebase --autostash + push again (preserves other workers' unstaged files in the shared tree); `git pull --rebase` is refused when the shared tree holds other workers' unstaged changes, so do not stash blindly.
- Pre-commit cached-diff review (AM-20): `git diff --cached --stat` before every commit, recorded in the log. On record: commit 26366a9 violated Rule 3 by sweeping improvements/worker-y14b-fix4-council-1.md (+329 lines) into an OPT log commit. The review exists to prevent recurrence.
- Post-merge content check (AM-20): after every merge, check the conflicted files for content, not just the merge result. The 23:05 merge resolved 3 conflicts by keeping both sides; the suite ran 1618 tests with 3 fail + 5 error, all pre-existing in baseline, 0 regression, +124 tests. A keep-both-sides resolution without a content check is an unreviewed merge.
- Resolve the 136-vs-145 tooltip gap with a second timed GraphQL read, or drop the cache explanation. Do not keep an unexplained 9-count gap in the method.
- Quality first: council + redteam complete on every fix, no shortcuts, no skipped steps.

## 12. Stop / redirect / kill rules (when a method is proven wrong, what replaces it)

- Kill on 15 minutes of no progress: stop and report, never retry silently. The watchdog reports directly to Muse, never via a coordinator (a stuck coordinator can never silence its own stall flags). Y13g has zero observable output at write time: record the stall and reassign per this rule rather than letting rank 5 wait on an invisible worker.
- AMEND means the method stands only with the exact amendment; executing it as written is wrong or wasteful. KILL means the method must not be executed, and the verdict names what replaces it. REDTEAM-M killed NOTHING outright. The three struck items inside surviving methods are:
  - STRUCK-1: M1 A step 2 items A1-A6 as prescriptions. Done in code (392bc09, 5b11696). Executing them again is wasted work with merge-conflict risk on scripts/cursor_session.py. Replaced by AM-1 (keep A7 only).
  - STRUCK-2: M2 D-7's 28-tab target. Contradicts the executed cleanup and the owner steer. Replaced by AM-6 (14 real + 1 sacrificial).
  - STRUCK-3: ORDER 4.3 deadline arithmetic (gap about 95, 68 minutes left). Target exceeded (456 at 23:05). Archived, not repaired.
- Closest kill candidate (NOT killed): the F no-reload ruling's status as "settled" rests on parse-2 determinism from one load run (n=1). Kill it only if the F-8 load-only trial shows the marker absent AND the reload is then refused as well. Its falsifier (marker absent in the F-8 trial promotes reload to the next test) is well-formed, so it stands until the trial runs.
- When a gate fails, stop at that gate and follow this section instead of improvising: name the failed gate, the evidence, and the replacement (the amendment, the re-review, or the reassign). A worker that invents a new step at a failed gate is violating the method.
- When a method is proven wrong by a live result, the replacement comes from a fresh council + redteam, not from the worker that ran it. The generator never re-grades its own failure.
- Do not stop or redirect a running worker from this file. Only the owner, Muse, or the kill rule (15 minutes, no progress) stops a worker, and the stop is logged with the reason.

## 13. Clone management (clone2-watch)

- Cron clone2-watch, every 15 minutes (set up 22:55): check GitHub first, switch workspace only when clone2 is silent more than 15 minutes or more than 1 hour unchecked; approve or nudge only for clone2's work, never money, never delete data, never personal info; switch back to workspace 1 after. Clone2-watch is another consumer of the command-switch method (section 6): workspace switches by command, never by clicking the rail.
- Clones never ask the owner directly; they write questions into a file for Muse to answer.
- The fleet cap is 2 parallel lanes per workstream. Clone batches are sequential inside the cap; a batch is handed out before the current one ends so the fleet never idles.
- Owner order 23:01 applies to clones too: a clone that hits a big error, a blocker, or a decision it cannot make reports it at once through its log and its coordinator; routine progress waits for the morning report.

## 14. Open items, gaps, and what this method does not decide

Open questions (ORDER): Q-1 open (scrub owner + date, AM-15). Q-2 open in ORDER, answered here by AM-14 (readiness judge is Worker OPT). Q-3 partly answered (the merge works, 0ac4311; the cadence for the next merge is still unwritten). Q-4 open (H2 fallback trigger owner + definition of usable think values). Q-5 partly closed (launcher found; workspace command unproven live until the E-1 probe runs). Q-6 CLOSED (deleter named: Y13r2 shim A6e; VMFIX c16dd4e).

ORDER claims A-1 to A-8: A-1 partly answered (a fallback-path partial proof exists, F2 4/4; the partial-proof bar is still undefined). A-2 open, see O-3/AM-14. A-3 open, see O-5/AM-15. A-4 open, P-12 measurement owed, see AM-22. A-5 answered in practice (one big merge worked) but the cadence is unwritten. A-6 open, see O-7/AM-16. A-7 open, unowned trigger. A-8 open, see O-2/AM-12 and F.

ZEN gaps still open: G-02 (run_live.py WD never takes zen_dom.lock), G-03 (wedge mechanism), G-05 (Zen-internal workspaces, no scenario), G-07 (ZT-B has not run), G-08 (no pre-restart snapshot for the 22:36 restart), G-10 (new-conf ldd output never saved), G-11 (run_live.py ensure_visible replacement unverified), G-12 (ZT-00 text drift + wrong path), G-15 (22:03-22:06 trigger), G-16 (Obsidian Web Clipper unexamined). Closed: G-01 (M2 direct read of TabManager.sys.mjs:39-41), G-04 (Y13r2 final 2fee242 BLOCK), G-06 (launcher found by F3), G-09 (F1 council 3 AMEND).

SRC gaps: G1 laptop native/require-liquid state unverified; G2 live plugin state after the 22:36 Zen restart not re-probed; G3 flicker log file missing on VM; G4 Y6r A1-A10 not enumerated item by item (closed in substance by M2 F adopting A1-A10 whole); G5 F1 council-3/redteam not read line by line; G6 J21 click attribution unknown (narrowed by the F3 rail finding in section 6, not closed); G7 clone2-watch cron is operational, not code; G8 SOLVED (re.py deleter, Y13r2 shim A6e, VMFIX c16dd4e).

Y13r2 BLOCK items (B1-B4 + 5 amend, commit 2fee242): B1 entry .pyc forge via -m/import makes verify lie; B2 stdlib shadowing 9/15 names; B3 tokenizer misses -m/flag/doi names; B4 -m bricks ship. Y13g is fixing per the redteam paper; a fresh re-review runs after. H3 gate: accepted Y13r2 proposal (5a2b69d NO VERDICT + runner-quiet/ports check counts as the done marker leg for this run, gate text kept, Y6 retry after Y13). G-10's H3 resolution must be cited in a council paper or log entry, not only MEMORY.md 22:57 (AM-13).

What this method does not decide: the Y6 retry success criterion until AM-12 is settled; the 20s deadline until AM-5 measures the distribution; the warm-up window until AM-3 measures it; the diagnose_body pre-flight gate until AM-22 measures it; the scrub date until AM-15 names it; the E1 review date until AM-16 sets it. Each is named with its owner step, not left as a silent assumption.

Method maintenance: this file is amended only by a new council + redteam cycle, one section per commit, same as its creation. A worker that finds this file wrong opens a redteam item with file:line evidence; it does not edit the file directly.
