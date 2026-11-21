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
