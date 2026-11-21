# OPT-M2 Council Voice 2: EVIDENCE

- Council: OPT-M2, Voice 2 (evidence). Parent: Worker OPT.
- Branch: todolist-push. Date: 2026-11-21, written 22:55 to 23:05 +07.
- Method: for every candidate method, state what proof it needs, what observation would falsify it, and what is still unmeasured. No live tests run by this council. Every claim carries a file:line or runnable-evidence citation.
- Sibling crawl note: improvements/opt-crawl-zen-20261121.md NOW EXISTS (37 lines, crawl 22:49-23:00 +07, read in full 22:54). It is an evidence base only, no method. This voice AGREES with its premise corrections P1, P3, P5, P6 in full, and with P2 as stated (Y13r2 log exists but is IN PROGRESS, redteam still running, verdict PENDING). No disagreement on substance: the file makes no method claim to disagree with. One correction it forces on this council: the tab cleanup scope is 39 RESURRECTED fixture tabs, not the 15 tabs of cleanup2 (P3, from MEMORY.md 22:49-22:51 and the owner screenshot 22:50); F3 is re-running the FULL cleanup with the same 28-real-tab keep-list. The verdict must use 39 as the scope and 28 as the target count.

## D. Marionette browserElement-null slot

### Candidate D-1 (adopted): client-side avoidance + restart ladder

- Proof the method needs, in order:
  1. The exact error string on POST /session: HTTP 500 with `TypeError: can't access property "namespaceURI", browserElement is null`. Recorded 5 times (22:06, 22:10, 22:12, 22:20, 22:31) in improvements/worker-f3-marionette-slot-log.md, event log. Any other string is a different failure and the ladder must not run.
  2. BiDi liveness before the restart: BiDi `session.new` plus `browsingContext.getTree` answers. F3 log states BiDi worked throughout the outage. If BiDi also fails, the diagnosis is class E (Zen wedged), not class D, and the ladder stops.
  3. The restart itself, with PIDs and times logged: `pkill -TERM` on the old zen-bin PID, zero zen/gecko processes verified, relaunch via the zen-ai wrapper detached, 9222 returns 200 and 2828 LISTEN. Proven once: F3 log 22:36:24 (pkill -TERM PID 27958, clean exit after 1s), 22:36:48 (new PID 426338), 22:37:32 (session created in 0.1s, id dfd532f5-7423-4e11-9171-f35410d0a73e, list_tabs 67 tabs in 7.7s).
  4. Post-restart health: `list_tabs` returns the full ordered list, example.com navigation renders with title "Example Domain" (F3 log 22:40, PASS), one tab click lands with measured miss (F3 log 22:41:39, 29ms, 1.0px miss).
  5. Cleanup completion: full ordered title + URL list BEFORE and AFTER the cleanup, count 67 to 28 (13 real tabs plus 14 about:blank plus 1 httpbin plus 1 BiDi fixture 40301, per the 22:10 baseline in MEMORY.md; scope corrected to 39 resurrected fixture tabs by OPT-ZEN P3). Any real tab missing from the after-list is a FAIL and the run stops.
- Falsifier: POST /session returns the same 500 AFTER a fresh restart with a fresh tabbrowser. That kills the zombie-tab theory outright, because the restart rebuilds the tabbrowser and the null tab cannot survive it. Second falsifier: the null recurs within the same session after a completed cleanup, which would show the cleanup itself creates zombies and G-TAB ordering is not sufficient.
- Still unmeasured: the identity of the null tab (never captured; destroyed by the restart); the 22:03 to 22:06 trigger (unproven); whether BiDi `getTree` can enumerate a tab whose `linkedBrowser` is null (unknown, never tested); whether a second null can recur (zero observations either way).

### Candidate D-2 (rejected): patch driver.sys.mjs inside omni.ja

- Proof it would need: a repacked omni.ja that loads, survives a Zen restart, survives a Zen update or is re-applied by a documented step, and makes POST /session succeed with a null tab present (a direct test: inject a null-linkedBrowser tab, then POST). None of this exists. The mechanism paper already shows the patch buys nothing the ladder does not buy, because the restart clears the zombie anyway.
- Falsifier (already met): the restart alone fixed the slot (F3 log 22:37:32). A patch is only justified if the ladder fails, and it has not failed once.
- Still unmeasured: whether a repacked omni.ja keeps its signature valid; whether Zen updates overwrite it silently. Do not measure these now; they are costs, not evidence for the method.

### Candidate D-3 (rejected): BiDi only, drop Marionette

- Proof it would need: a BiDi pointer click that moves the counter. Todolist 1.1.1 records the opposite twice (v1 counter STILL 0, v3 stayed 1). Falsified already by two live runs. No further proof needed.

## E. Zen wedge / workspace switching

### Candidate E-1 (adopted): read-config-first command method + wedge signature capture

- Proof the method needs, in order:
  1. The exact workspace-switch command in hl.dsp form and the exact Omarchy launcher command, read from the Hyprland/Omarchy config on the laptop, quoted verbatim in the fix log with file and line. No guessed string counts. The working form is proven once for window close: `hyprctl dispatch 'hl.dsp.window.close()'` (todolist G4, 2.7.4). No workspace-switch string appears in any primary source read by this council; that absence is itself recorded.
  2. Return to Hyprland workspace 1 by that command, verified by `hyprctl activeworkspace` reporting 1 and `hyprctl clients` showing Zen on workspace 1, plus a screenshot showing Zen visible. F3 open items 1-2 list exactly this.
  3. Wedge signature, captured BEFORE any future restart: `hyprctl clients`, `hyprctl workspaces`, `hyprctl activewindow`, Zen PID and flags, BiDi `browsingContext.getTree`, one Marionette POST attempt with its exact error. The 22:25 wedge has none of this, which is why its mechanism is unknown.
  4. Re-test by ZT-05 and ZT-10 (improvements/zen-ordinary-user-tests-20261121.md): ZT-05 round trips Super+M then Super+N with hyprctl checks after each switch; ZT-10 requires tab rows to show at least 10 characters of title and the collapse toggle identified by tooltip before any click. Both re-test owner-reported F-001 (unclickable Zen) and F-002 (workspace errors).
- Falsifier for the common-cause reading (wedge and slot share one cause): a future wedge in which Marionette POST succeeds while Zen is unclickable, or a future slot failure in which Zen stays fully clickable. Either observation splits the two classes for good. Until one appears, the verdict keeps them separate.
- Falsifier for the command method: the config contains no workspace-switch binding in hl.dsp form, or the recorded command switches to the wrong workspace. Then the method stops and reports, it does not guess a second string.
- Still unmeasured: the wedge mechanism itself (zero signature captures); the exact hl.dsp workspace call; whether Zen-internal workspace switching works at all (never tested; F3 log notes it is a separate item).

## F. Pill measurement 2.2.3 (Y6 A1-A10 + retry)

### Candidate F-1 (adopted): Y6r adjudicated fix list A1-A10, no manual reload

- Proof each item needs (from improvements/worker-y6r-rereview-log.md, adjudication R1-R8 and fix list A1-A10):
  - A1 staging: laptop copy of the y6e conf md5 9ccb27017ab63a9d2bce1d9651425d3b, ldd on the conf plugin path rc=0, ldd output SAVED to a file (Y6e's own run has no saved ldd log; Y6r Council 2 required it). Without the saved output, A1 is not proven.
  - A2 positive gate: poll $NEST_LOG for the applied marker up to 15 s after the version check; fail on timeout with a log tail; re-run plugin-list/version checks after the marker; require `features.layers.enabled == true` in parsed status JSON as a second positive signal. The parse-1 "not ready" marker is EXPECTED, not a failure.
  - A3 positive marker: nest copy of optics.lua ONLY prints a success line AFTER config() and layer() return (for example `Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 mask=contour namespace=computer-use-indicator`), pulled to the repo with md5. Never edit live native/hyprglass-local-optics.lua (blur 0.0).
  - A4 record correction: Y6e log line 561, Y6r V4/V5, Council 2 section 1g, Council 3 F3 corrected to "profile config applied on parse 2 (layers.enabled true, proven); layer() registration and material values unproven until the positive marker lands". Also correct the hook's false liquid-gate comment.
  - A5 AMEND4 + AMEND5 ported into the v3 runner (skip-var unset check, live-config no-load-path walk, live plugin list before/after identity), with the fix worker verifying the exact delta first (the runner already has partial teardown equivalents).
  - A6 supporting gates: nest `hyprctl configerrors` empty after profile application; record `hyprglass stats` (contourRebuilds) before and after arms as corroboration, not a gate.
  - A7: NO manual `nest hyprctl reload` added. Proof of compliance is the diff: no reload line in the fix.
  - A8 load-only trial first (no pill, no arms): positive marker plus layers.enabled true plus configerrors empty plus live before/after identical. First amended run must show the positive marker before the liquid gate or stop.
  - A9 fresh council + redteam re-review of the fix diff before any measurement run. The retry worker must NOT run the pill measurement on an unreviewed fix.
  - A10: no saved-log marker counts as parse evidence (ofstream buffering; saved logs are 188-line flushed prefixes). Use the fresh per-instance log.
- Falsifier for the adopted method: the load-only trial shows the positive marker ABSENT after the version check. That falsifies R1's determinism claim in practice and promotes the manual reload (or the timer) from rejected hypothesis to next test. Second falsifier: the marker present but `features.layers.enabled` false, which would break the R1 proof chain (default false plus only-setter optics.lua) and reopen the whole profile question.
- Falsifier for the rejected reload (Y6r Council 1 primary): already met by R1. Parse 2 applies the profile deterministically (pin diff lines 6270, 6507, 1913-1915; status layers.enabled true at 21:57:14; optics.lua the only setter). A reload cannot add what is already applied, and it introduces the unprobed O1 risk (duplicate layer() registration on parse 3, overwrite vs error).
- Still unmeasured: whether layer() registration succeeded in the Y6e run; whether the blur/refraction material values landed (no status field exposes them); whether nested shaders reach ready within the 60 s liquid window (only pending at 7 s observed, Y6r open item O3); the pill arms themselves (never run live); the laptop copy md5 of the load-test script (Y6r open item O4, blocked until the VM Python/SSH repair, which F3 completed 22:29-22:31 and VMFIX confirmed with dpkg -V clean per todolist P0).
- Precondition proof (G-VMFIX, todolist line 33): `import re` works on the VM plus SSH_OK before any laptop-side step. F3 repaired /usr/lib/python3.12/re/__init__.py 22:29-22:31 (16,315 B from CPython 3.12 branch). The root cause of the file loss is still unknown; that is a separate investigation, not a blocker for the retry once the check passes.

## G. Hidden-body decisive experiment + composite/blind test design

### Candidate G-1 (adopted): Y4b fix design + 6-phase decisive experiment + ZT-A v2 blind composite design

- Proof the fix design needs (from improvements/worker-y4b-hidden-body-root-cause.md):
  - `diagnose_body` captures, in one eval and one snapshot, saved to disk with timestamps: readyState, documentElement classList (tz-hidden, tz-initialized), body computed visibility/opacity/display plus html visibility, body inline style, transition property/duration/delay, body rect, innerText length (corroboration only), hasFocus/visibilityState, URL. Sample twice 300 ms apart when hidden. The saving is the point: the original sin was unsaved probe output (R's "no class" was never saved, so V1 is wounded but not falsified).
  - Classification with V2 removed: VISIBLE, TZ_STUCK_V1, OTHER_HIDDEN, FIXTURE_FAILURE. Class-absent plus computed-hidden is OTHER_HIDDEN, never V2.
  - Recovery ladder within an 8 s budget per tab opening, each step logged: poll 250 ms up to 2.0 s; remove tz-hidden exactly as removeLoadingScreen does (test tab only, test origin only, logged as intervention); bootstrap tab fallback; then `INFRA: hidden-body`, never a fixture failure; two consecutive infra-blocked tests abort the suite.
  - Flagged passes counted separately: a test passing only after `removed-tz-hidden` is a FLAGGED pass, never folded into the headline count.
- Proof the decisive experiment needs (6 phases, Y4b design):
  - Phase 2 old-versus-new pair: the SAME hidden tab re-captured immediately after a NEW tab opens. This single pair is the most important capture in the whole experiment.
  - V1 PROVEN only if: a hidden tab shows `tz-hidden` in htmlClass at 5 s and every later capture while hidden, rAF ticks flowing, opacity 0, zero reproductions in the disabled arm, and the old tab staying hidden after new tabs go visible.
  - V1 REFUTED by one clean counterexample: hidden tab, no `tz-hidden`, output saved. That single saved observation ends V1.
  - Stale-driver PROVEN only by orphan present plus old-tab re-check after the kill. Incident 2 already refutes it as a necessary cause (fresh port 4448, no geckodriver running at the 18:05 check, state cleared with no kill).
  - If a hidden tab appears with the extension disabled, no orphan, rAF flowing, and no `tz-hidden`, then V1, V2, and stale-driver are all out at once and the cause is unknown with a complete capture. That outcome is a SUCCESS for the experiment.
  - Stop rule: no reproduction after the full Phase 1 and Phase 4 loops means INCONCLUSIVE, not negative. The state is intermittent.
- Proof the composite/blind design needs (improvements/zen-ordinary-user-tests-20261121.md, ZT-A v2):
  - ZT-00 health gate first, all steps 0 to 7 pass. Step 3 (Marionette session creation) is the deciding check; the known "browserElement is null" failure is a gate failure, not a pass.
  - Blind execution: ZT-B has not seen the scenarios (no ZT-B report file existed at OPT-ZEN crawl time, P6). Any executor who has read this file cannot run it blind.
  - Cleanup is identity, not count: the title set after each scenario must equal the pre-scenario title set AND the count must match. Pre-close check before EVERY Ctrl+W: DOM active title must equal the expected test-tab identity or STOP.
  - [CHECK] steps are instrumentation: a failed control (curl, hyprctl, ps) makes the scenario INCONCLUSIVE, not FAIL, except the two safety gates (identity cleanup, pre-close check), where failure is a FAIL and the executor stops.
  - Per-scenario channel checklist filled in: DOM steps, CLI steps, mouse steps, keyboard steps. A scenario that did not use all four channels is reported as such and does not claim composite coverage. Total run maximum 90 minutes.
- Falsifier for the whole G method: the experiment runs to completion with zero reproductions AND the disabled arm also shows zero. That does not falsify the fix design (the harness defense still stands), but it leaves the cause unknown and forbids any claim that the incident is fixed. A green rerun is never evidence the browser is healthy (Y4b verdict).
- Still unmeasured: everything about the cause. Zero positive sightings of tz-hidden on a hidden tab; zero saved htmlClass outputs during a hidden tab; zero opacity readings; zero screenshots of the logo pulse markers; whether any hidden tab ever cleared (old hidden tabs were never re-checked in either incident); whether switch-away-and-back un-hides a hidden tab (zero observations in either direction; probe_y4d never tested it and probe_q05d never executed the switch). The experiment exists to fill exactly these gaps, in this order.

## Commit method (evidence for the verdict section)

- What the graph actually counts (MEMORY.md 22:49-22:51 correction, OPT GraphQL verification 22:52): the GitHub contributions graph counts the UTC day on the DEFAULT branch (main) only. At 22:51 it showed 144 commits + 1 PR = 145 for UTC 21/11, while the local +07 day showed 201 commits + 1 PR = 202. todolist-push held 290 commits on UTC 21/11 and they did NOT count. Therefore a working-branch commit, however small, moves the graph by zero until it is merged to main.
- Proof the commit method needs: every push verified via `git ls-remote` (remote HEAD hash equals local HEAD hash); every merge to main verified the same way on main; the graph number re-checked by tooltip/GraphQL after merges, not assumed. The gap to 240 at 22:52 was about 95 on the UTC-day count.
- Falsifier: a merge to main after which the graph count does not move. That would show the counting rule is different from the stated one and the method must stop and re-verify instead of merging blindly.
- Still unmeasured: the exact graph count after the MERGE worker's first merge (pending at this writing). The verdict must make the re-check a step, not an assumption.
