# Redteam attack report: Worker Y13 codex-y5 live plan v1

Target: improvements/worker-y13-codex-y5-live-plan.md (v1, 2026-11-21 ~19:20 +07)
Attacker: Redteam for the Y13 live run. Method: read the plan, all 10 specs,
check.mjs, all 10 fixtures, run_agyq2.py, run_agy_y2.py, run_live.py at
1e3901c and at HEAD, worker-y4d-rerun-log.md, worker-y5-codex-log.md, the
Y6b v2 nested launcher, and the Y9 manifest. Every finding below cites the
file and line or spec step where it bites. No em dash or en dash is used in
this report. No personal info is included.

Verdict counts: 7 HIGH, 9 MEDIUM, 4 LOW. Three further items were checked
and found clean; they are listed at the end, not counted as attacks.

Do NOT edit the plan or any runner file on the basis of this report. Do NOT
commit anything. This report is the attack only.

## HIGH

### H1. The Y9 park is claimed but not in the copy list, and the base WD has no park (attack 2)

Severity: HIGH.

Mechanism: the plan says "Sessions exit parked on a sacrificial about:blank
tab (Y9 park pattern) so DELETE /session closes the throwaway, never the
shared test tab and never a user tab." The park lives in exactly one place:
class Y9WD in tests/realistic/run_agy_y2.py lines 358-418
(_park_before_exit, plus __exit__ calling it). The plan's copy list names
only functions from run_agyq2.py (_check_handover, _hyprland_signature,
start_server, select_option, select_by_text, clear_input, set_date, txt,
count, has_class, is_checked, norm, _log_diag, rebootstrap_tab,
ensure_visible, _recheck_shared_tab, open_fixture, bootstrap_tab, preflight,
main). None of those is the park. run_agyq2.py contains zero occurrences of
"park". The plan also says the new file is "self-contained except the run_live
import (WD, Runner, diagnose_body, log_step, start_server)", so the WD in use
is the BASE WD from run_live.py at 1e3901c. The base WD._cleanup (run_live.py
1e3901c, _cleanup) closes every handle in opened_tabs, then issues DELETE
/session. Y4d proved live that DELETE /session closes the session's current
top-level window (worker-y4d-rerun-log.md, finding 1: shared tab gone 10/10
in both runs, suite-end cleanup hit "no such window" for all 10 rebootstrap
tabs).

Consequences for the runner as specified:

1. The shared tab dies at the end of test 01, and again after every test.
   open_fixture then prints "shared tab gone, rebootstrap" and opens a fresh
   tab per test. The "shared tab" design is fictional, exactly as Y4d found.
   Cost is a rebootstrap per test plus one orphaned tab per test, not a
   wrong verdict, but the plan's headline claim ("never the shared test tab")
   is false.
2. bootstrap_tab itself kills its own tab: it creates a WD, opens the new
   tab, removes the handle from opened_tabs, runs ensure_visible, then its
   finally block calls wd.__exit__(), which issues DELETE /session while the
   new shared tab is current. Any tz-hidden removal intervention performed
   during bootstrap is then wasted on a tab that is immediately closed, and
   the BOOTSTRAP INTERVENTION log line describes a dead tab.
3. User-tab close on the error paths. Construct the sequence: test N opens
   its session while the current window is a user tab (this is the state
   after the previous session's DELETE closed the shared tab and the current
   window fell back). open_fixture finds r.tab not in d.handles(), calls
   rebootstrap_tab, and rebootstrap fails (all 3 new tabs open hidden, or
   the deadline passes). open_fixture raises INFRA. The finally block calls
   wd.__exit__() with opened_tabs empty and the current window no longer a
   test tab (every test tab in this path is dead or already closed), so
   DELETE /session closes a user tab. The same hole exists at suite end:
   run_agyq2.py main opens a fresh WD session and switches to each handle in
   bootstrap_tabs | _TEST_TABS; if every switch fails (all tabs dead), the
   session exits with the user tab current and DELETE /session closes it.
   A third instance is _recheck_shared_tab as copied from run_agyq2.py: it
   opens a fresh WD, switches to the old tab, and if the switch raises, the
   with-block exit deletes the session while a user tab is current.

Evidence: tests/realistic/run_agy_y2.py lines 372-418 (park);
tests/realistic/run_agyq2.py lines 1296-1335 (bootstrap_tab) and 1560-1640
(main, finally wd.__exit__(), suite-end cleanup);
worker-y4d-rerun-log.md finding 1.

Fix direction (for the plan author, not applied here): name Y9WD (or its
_park_before_exit) explicitly in the copy list, or state that the runner
subclasses WD with the park; add a pre-exit assertion that the current
handle is a registered test tab or the sacrificial tab, and refuse to
DELETE /session otherwise; never let a fresh diagnostic session exit while
a user tab is current.

### H2. The plan's "r.step check" wording invites the r.step False-return trap (attack 7)

Severity: HIGH.

Mechanism: the step-mapping table says '"Verify #x text is ...": r.step
check via d.text + exact trimmed compare (end state) or norm() compare
(intermediate, recorded).' In run_live.py at 1e3901c, Runner.step raises
only on exception and IGNORES a False return value (step code: ok is set
from the try/except only; a lambda returning False logs ok True). Runner.check
is the method that records a failed condition (check appends to failures and
prints CHECK FAIL, without raising). run_agyq2.py drivers use r.check for
verifies and r.step for actions (example: run_q01, lines 560-650). Y9's file
documents this exact trap in open_fixture: "the old r.step('check body
visible') logged ok True even when the body was hidden, because Y9Runner.step
only fails on exception and ignores a False return."

If the Y13 driver author follows the plan's literal wording and implements a
spec verify as r.step("verify X", "check", lambda: txt(...) == expected),
every False verify is logged ok and recorded nowhere. All 269 step verifies
become fiction in one choice. The end-state ported verifyTest remains a
backstop (it appends failures via final_verify), so a wrong end state is
still caught, but any intermediate failure the end state does not reflect
is silently dropped. The plan never states "verifies MUST be r.check (or an
r.step whose lambda raises on False)". The warning was in front of the
author: run_agy_y2.py is in the plan's READ FIRST list and documents the
trap in its own open_fixture comment.

Evidence: plan step-mapping table, "Verify #x text is" row;
tests/realistic/run_agy_y2.py open_fixture comment on the r.step trap;
run_live.py 1e3901c Runner.step and Runner.check.

### H3. The plan mandates d.text where the copied helper uses eval textContent, and test-01 step 26 breaks on it (attack 3)

Severity: HIGH.

Mechanism: the plan's mapping says step verifies use d.text. d.text in
run_live.py is GET /element/{id}/text, the WebDriver rendered-text endpoint.
The copied helper txt() in run_agyq2.py line 229 does the opposite: it evals
"return el ? el.textContent : null". Rendered text and textContent differ
exactly on multi-line content inside an element without pre-wrap: a literal
newline in a text node under white-space normal collapses to a space in
rendered text, while textContent preserves it.

The bite is test-01 step 26: "#conflict-markers text is exactly
'<<<<<<< feature/cleanup\nmode=preview\n=======\nmode=stable\n>>>>>>> main'".
The fixture sets it by textContent (test-01 fixture, render(): "ids('#conflict-
markers').textContent = conflict ? '<<<<<<< feature/cleanup\nmode=preview
\n=======\nmode=stable\n>>>>>>> main' : ..."). The element is a plain
"<p id=\"conflict-markers\" class=\"muted\">" (fixture line 33). The fixture
CSS gives white-space pre-wrap ONLY to pre elements ("pre{white-space:
pre-wrap...}"); the p has no pre-wrap. So d.text returns the markers with
newlines collapsed to spaces, and the plan's mandated exact compare fails
deterministically even though the DOM is correct. The end-state verifyTest
does not assert #conflict-markers at all (check.mjs test 01 has no
conflict-markers assertion), so nothing rescues the step. The plan's only
escape is the norm() deviation path (norm collapses all whitespace, so it
would pass), but the plan does not name step 26 as needing norm(), and norm()
would also pass if the fixture rendered the markers with spaces instead of
newlines, so the check is weakened either way.

Note the fixtures were otherwise built to avoid this: #terminal-output,
#branch-list, #git-log-list are pre elements; #occurrence-summary is a pre;
#playlist-track-list and #timeline-order carry white-space pre-line. Step 26
is the single multi-line verify on a plain p. The plan's Q2 ("exact trimmed
textContent or norm?") shows the author sensed the tension but the mapping
table still mandates d.text, which is neither.

Evidence: plan step-mapping table; tests/realistic/run_agyq2.py line 229
(txt); tests/realistic/codex-y5/fixtures/test-01-git-workflow.html lines 7,
33, 63; tests/realistic/codex-y5/test-01-git-workflow.md step 26.

### H4. The mid-test hidden-body rule is claimed but unimplemented, and test-10 reload is the concrete instance (attack 5)

Severity: HIGH.

Mechanism: the plan says "A hidden body found mid-test (on any step failure)
is INFRA, not a step failure." Nothing in the copied harness implements that
sentence. ensure_visible (the ladder: diagnose, poll 2.0 s, verified
tz-hidden removal, rebootstrap, 8.0 s enforced deadline) is called only in
open_fixture, bootstrap_tab, and rebootstrap_tab. No driver calls it between
steps, and no step-failure path diagnoses the body. In run_agyq2.py main, a
step failure raises "step failed: ..." which does NOT start with "INFRA:", so
main counts it as a live failure, resets infra_blocked to 0, and grants no
re-run. The only post-failure diagnose is _recheck_shared_tab, and it runs
only after INFRA failures, never after a step failure.

Walk the ladder on a test-05 mid-test hidden encounter: it never runs. A
hidden body in test-05 would surface at the next step as a Marionette error
("could not be scrolled into view") or an empty d.text read, Runner.step
would raise, the test would FAIL as a live failure, infra_blocked would reset
to 0, no re-run would be allowed, hidden_body_encounters would not increment
(only ensure_visible and _log_diag increment it), and the report would show a
live FAIL with no hidden-body diagnosis. The plan's ABORT section would then
be wrong about its own run.

The concrete instance in this suite is test-10, the only test with a
mid-test navigation. Steps 21 and 26 click #btn-reload-settings, whose
handler is location.reload() (fixture line 79). A reload is a new document;
the extension content script runs again at document_start and can re-inject
tz-hidden. The plan's step mapping for these steps is "click
#btn-reload-settings, then wait_ready + 1s settle + diagnose_body (no
d.refresh())". diagnose_body only diagnoses; it does not run the ladder. If
the body is hidden after the reload, the next step verifies (step 22, step 27)
read via d.text, and WebDriver rendered text on visibility:hidden content
returns empty, so the verifies fail as live failures. The hidden-body
encounter is never counted, never triggers poll, removal, or rebootstrap, and
is misclassified as a test failure. Note also that the plan's test-10
sequence never says what to do with a non-VISIBLE diagnose result: there is
no branch for it.

Evidence: plan ABORT section and test-10 mapping rows;
tests/realistic/run_agyq2.py lines 351-470 (ensure_visible call sites: only
open_fixture lines 515-545 and bootstrap line 1303) and main lines 1560-1600
(INFRA prefix check, infra_blocked reset);
tests/realistic/codex-y5/fixtures/test-10-extension-settings.html line 79.

### H5. The queue gate is unspecified, the flock is blind to most runners, and the Y6c completion marker is undefined (attack 6)

Severity: HIGH.

Mechanism: the plan's queue gate is three parts: (a) flock on
zen_dom.lock, (b) "a runner-quiet process check (no other runner processes
on the laptop)", (c) "wait for Muse's go order at run time". None of (b) is
specified: no process list, no port list, no definition of "quiet", no
re-check cadence. The only concrete runner-quiet pattern available is Y6b v2
(improvements/worker-y6b-run-nested-wayland-v2.sh lines 148-163): pgrep for
"run_agyq2.py|run_live.py|run_agyq.py|run_agy_y2.py|run_fcck.py" plus a
geckodriver check plus mpv/foot. That pattern is blind to the E1 runner: E1
drives through /tmp/e1/hand_drive_e1.py (a sed copy of hand_drive.py) with a
Codex executor process (arm A launched 19:17:04, codex PID 282880 per the Y8
E1 log), neither of which matches run_*.py or geckodriver alone (the E1
geckodriver on 4451 would match the geckodriver check only while it is up;
between arms it is down while the executor still holds the slot). It is also
blind to any runner whose filename is not in the list: run_codex_y5.py
(Y13 itself), Y11b's proof runner (name unknown, likely derived from HEAD
run_live.py, which contains zero flock references), and Y14's runner (name
unknown).

Construct the race using only the gates the plan names. Y13 preflight passes
at T0: the flock is free (E1 does not hold zen_dom.lock; Y6b redteam proved
only Y4-style runners enforce it, and E1's lock behavior was unverified),
the process check sees no run_*.py process (E1's executor is a codex process
driving hand_drive_e1.py), and Muse's go order was given on a stale report.
Y8b arm B starts at T0+30 s while Y13 is mid-suite. Both sessions drive the
same Zen through the shared Marionette port 2828. The visible tab is shared:
when the E1 driver switches tabs, Y13's next d.click can fail "could not be
scrolled into view" (the Y4 probe v4 failure mode for a non-current tab) or
act on a stale current window. Y13's per-test handover re-check does not
re-check runner-quiet, so Y13 never notices; the failures are logged as live
step failures. The reverse race is the same: Y13 starts while Y11b's proof
run is live, because Y11b's runner may not hold the flock at all.

Separately, the plan says "I poll todolist-push for Y6c's completion marker"
but never names the marker (no file, commit message, or branch), and sets no
timeout. If Y6c never spawns or never writes the marker, Y13 waits forever
with no decision rule. If the marker is written at prep time rather than at
run completion, Y13 starts early into Y6c's live nested run, whose nest tiles
over the live screen and steals the visible tab.

Evidence: plan Slot/queue section; improvements/worker-y6b-redteam.md
(flock section, only run_agyq2.py enforces it; E1/Y9 lock behavior
unverified); improvements/worker-y6b-run-nested-wayland-v2.sh lines 148-165
(quiet-check pattern); improvements/worker-y8-e1-execution-log.md line 48
(arm A launched 19:17:04).

### H6. The copy list cannot build the runner the plan describes, and the park is live-unproven (attacks 2 and 8)

Severity: HIGH.

Mechanism: the plan's Runner design section describes three headline
mechanisms: the Y9 park, the 1:1 ported verifyTest, and the integrity guard.
None of the three lives in run_agyq2.py, the plan's sole named copy source.
The park is Y9WD in run_agy_y2.py (lines 358-418). The ported verify and
the integrity guard are verify_test, final_verify, and the guard block in
run_agy_y2.py open_fixture (lines 1047-1175). run_agyq2.py has no
verify_test, no final_verify, and no integrity guard; its drivers verify with
r.check and txt() only. So the runner as specified cannot be built from the
listed copy source alone. Either the author also intends to copy from
run_agy_y2.py without saying so (underspecified, and the transcription of
_VERIFY_JS plus the guard is then unreviewed), or the runner as specified
lacks the park, the verify, and the guard entirely, in which case the plan's
pass criteria ("ALL spec steps pass AND the ported verifyTest passes") have
no implementation.

The live-proof status makes it worse: Y9 has not run yet (its slot is still
ahead of Y13 in the queue the plan itself states). The park therefore has
zero live runs. The plan treats it as a proven pattern ("Y9 park pattern")
when it is an untested subclass override. If Y9's run finds the park broken
(for example new_tab("about:blank") failing, or the park closing the wrong
tab), Y13 inherits the break with no re-review trigger in the plan.

Evidence: plan Runner design section and copy list; grep of
tests/realistic/run_agyq2.py (no "park", no "verify_test", no
"IntegrityGuard"); tests/realistic/run_agy_y2.py lines 358-418 and 1047-1175.

### H7. The handover token is hardcoded to Y4d's file with a 4h window, and the plan names no writer, path, or renewal (attacks 6 and 8)

Severity: HIGH.

Mechanism: _check_handover in run_agyq2.py (line 68) hardcodes
HANDOVER_FILE = /tmp/worker-y4d-handover.json with HANDOVER_MAX_AGE_S = 4
hours, and requires LIVE_OWNER_AWAY=1 plus a token younger than 4h. Y4d's
token was written ~18:44 on 21/11 with basis "owner handover 18:24", so it
expires ~22:44. The plan copies _check_handover verbatim and says the token
is "re-checked before every test (4h max age)", but never says who writes
Y13's token, at what path, on what basis, or what happens at expiry. If Y13
copies the path verbatim, preflight refuses to run once the slot opens after
~22:44, and every per-test re-check refuses too, so the run aborts with exit
2 and zero tests driven. If Y13 writes its own token at prep time (~19:20)
asserting the same 18:24 basis, the wall is ~23:20 instead. Either way the
plan's other rule, "Drive Zen ONLY after Y6c completes", has no clock bound,
and the queue ahead (Y9, Y11b, Y6c) can easily push the slot past the wall.
The two rules conflict and the plan resolves the conflict nowhere. There is
also no launch command in the plan, so LIVE_OWNER_AWAY=1 is not shown set
anywhere; a launch that forgets it fails preflight the same way.

Evidence: tests/realistic/run_agyq2.py lines 65-68 and 139-161
(_check_handover); plan Preflight and Slot/queue sections (no token path,
writer, or renewal rule named).

## MEDIUM

### M1. Base pin: the code is airtight, but the justification overstates the evidence and the manifest has a gap (attack 1)

Severity: MEDIUM.

What was checked: the full 1e3901c-to-HEAD diff of tests/realistic/
run_live.py (415 insertions, 66 deletions, 17 hunks). Every hunk is Y11
live-metrics wiring: the live_metrics import loop, _metered decorators,
_probe_click, the type_text post-type read-back, the diagnose_body wrapper,
Runner and run_one metrics plumbing, and main() metrics setup. With metrics
off (live_metrics import fails, metrics None), every wrapper is a
pass-through and there is no outcome-changing behavior difference. The pin's
md5 was verified independently: git show 1e3901c:tests/realistic/run_live.py
md5s to 84fa106c253d5e7f16daccf2ce3f14a5, matching the plan. The _DIAG_JS
top-level return fix is present at 1e3901c (line 93, "return (() => {").

The holes are evidential and procedural, not code:

1. "Proven 10/10 twice" is wrong for this md5. Y4d run 1 was 8/10 and run 2
   was 10/10 (worker-y4d-rerun-log.md timeline 18:47-18:51), both on the same
   run_live.py bytes. That is one 10/10 run, not two. The "twice" counts the
   runner file's two runs, not the base's.
2. "To be proven a third time by Y9" is a future event, not evidence. Y9 has
   not run. Y9's own manifest does pin run_live.py to 1e3901c (md5
   84fa106c, tests/realistic/agy-y2-manifest.json), so the third proof is
   plausible, but it does not exist at plan time.
3. Mixed-ship hazard: if the ship dir ever contains live_metrics.py next to
   run_live.py (for example a whole-tree copy, or run_live.py taken from HEAD
   by mistake), HEAD's code activates metrics, and every click then pays an
   extra pre-click probe eval and every type pays an extra value() read-back.
   Both are fail-open and read-only, so the expected outcome change is
   latency only, but the plan's manifest covers "every shipped file" without
   stating that live_metrics.py must be ABSENT, and without a ship-time
   re-verification of the run_live.py md5 from git. Y9's own log (line 258)
   records that a "byte-identical to 1e3901c" claim already went stale once
   after its check, which is exactly the drift this invites.
4. The manifest pins run_live.py but not the transcribed sources. The ladder,
   rebootstrap, preflight, and park are COPIED by transcription into a new
   file, so a transcription error in any of them is invisible to the md5
   check. The plan's only check on the new runner is a headless Python syntax
   check, which is the same class of review that let the _DIAG_JS bug survive
   council review in Y4d.

### M2. Visibility verifies have no mapped primitive, and the fixtures use the hidden attribute, not a class (attack 4)

Severity: MEDIUM.

Mechanism: seven spec steps verify visibility with no primitive in the
plan's step-mapping table: test-03 steps 6 and 17 ("#entry-editor must become
visible"), test-06 step 3 ("#import-modal must become visible"), test-07
step 20 ("#forward-modal must become visible with heading text 'Forward
message'"), test-09 step 12 ("#tag-panel must become visible"), test-10
steps 8, 16, 23 ("#site-access-page / #options-page must become visible").
All of these elements are shown and hidden with the hidden attribute
(fixture code sets el.hidden = false), not with a class. The plan's helper
list includes has_class but no visibility primitive is named in the table,
and d.visible() (run_live.py, rect plus display plus visibility) is never
mentioned. If the driver author guesses has_class(x, "visible"), every one
of these seven steps fails, because no "visible" class exists in these
fixtures. The plan's Q8 asks council to name unmappable steps, but the
plan's own table omits the whole visibility category, so the gap is in the
plan, not only in council review.

Related: several buttons start hidden and are unhidden by a prior step
(test-01 #btn-use-incoming, #btn-use-ours, #btn-undo-conflict-resolution,
hidden until the merge conflict at step 21; test-03 #btn-edit-entry,
#btn-delete-entry, #btn-undo-delete, hidden until an entry exists or is
deleted; test-05 #btn-undo-calendar-delete, hidden until a delete). A
Marionette click on a hidden element raises "could not be scrolled into
view". The sequences are synchronous in the fixtures (the unhide happens in
the same handler as the prior step), so they should work if the prior step
really ran, but the driver has no wait or retry if the unhide lags, and no
mapping entry says how the driver confirms the button is clickable before
clicking it.

Evidence: plan step-mapping table (no visibility row); fixtures:
test-03 lines 16, 51, 57; test-06 lines 14, 52; test-07 lines 15, 59;
test-09 lines 17, 58; test-10 (hidden toggles in the open-sites and
open-options handlers); test-01 line 34; test-05 lines 84, 92.

### M3. Test-06 step 13: the click is load-bearing and the plan's specific line omits it (attack 4)

Severity: MEDIUM.

Mechanism: step 13 reads "Click button #btn-select-forest, then replace
#playhead-input value with '5'." The click is not decorative. After step 11
(add city), the fixture's selectedId is the city clip (addToTimeline sets
selectedId = clip.id). Step 14 splits the SELECTED clip at the playhead.
Without the step 13 click, step 14 splits the 8-second city clip at 5 into
5+3, and step 15's verify (order "Forest A-roll (5 sec), Forest A-roll
(7 sec), City B-roll (8 sec)") fails. The plan's general rule ("Click #x,
then replace #y: two steps, in order") does cover this, but the plan's
specific line reads "test-06 steps 13/17/22 (replace input values):
type_text", which read literally drops the click for step 13. This is the
same trap that already bit Y5's own verifier: worker-y5-codex-log.md,
harness bug 1 (test-06): "click-replace action set the value but never
clicked the button first. Fixed: click, then set value, then fire
input/change." The plan reproduces the exact ambiguity that cost Y5 a
verification round. Steps 17 and 22 are replace-only and do not need a
click (selection persists from step 16), so grouping all three under one
"replace" label is what hides the difference.

Evidence: plan step-mapping table; tests/realistic/codex-y5/test-06-
video-editor.md step 13; fixture lines 64, 69-78 (addToTimeline sets
selectedId; split uses selectedId); worker-y5-codex-log.md harness bug 1.

### M4. No step-count audit: omitting the mistake and recovery steps can still PASS (attack 7)

Severity: MEDIUM.

Mechanism: the plan requires "ALL spec steps pass" but provides no mechanism
proving the driver executed all 269 steps. r.check records failures without
raising, and r.step raises only on exception, so a driver that silently
omits steps produces no failure for the omitted steps; only the step log
would show the gap, and nothing in the plan audits the log's step count per
test. Trace test-04: a driver that omits steps 13-16 (the toll-route mistake
and the avoid-tolls recovery) and steps 19-22 (save, verify, reverse,
verify) but drives steps 3-12 and 23-27 would still reach the correct end
state only if the reverse happened, which it did not, so step 27 would
fail. But a driver that omits ONLY steps 13-16 (mistake and recovery) while
driving everything else reaches the correct end state: origin Harbor, dest
Workshop, toll avoidance was never turned on, find-routes at step 23 returns
2 routes instead of 1, so step 23's verify (count "1") fails. The end-state
verify would still pass (it does not assert the route count). Narrower:
omit steps 15-16 only (the checkbox click and its verify) while keeping the
rest: step 23 expects count "1" and fails, so it is caught. The genuinely
uncovered omission is subtler: the final verifyTest asserts end state only,
so any intermediate behavior whose effect is overwritten by a later step is
unproven by a pass. Example: test-04 steps 13-14 (choose the toll route,
verify its summary) are fully overwritten by steps 15-18; a driver that
skips them still passes everything. The suite would then report 10/10 while
never having exercised the toll-mistake path the test was designed to
expose. The plan counts steps in the log but never audits "did run_04 emit
all 27 steps". The weak step-22 check itself cannot manufacture a suite PASS
on its own, because steps 20 and 21 are non-vacuous (step 20 verifies the
saved text is present, so the state at step 22 is provably non-fresh; if the
reverse handler failed to clear the saved route, step 22 fails loudly), but
that containment rests on the driver actually executing steps 20 and 21,
which nothing audits.

Evidence: plan thresholds ("A test passes only if ALL spec steps pass");
run_live.py 1e3901c Runner.check (records, no raise) and summary
(pass = zero failures); test-04 steps 13-22.

### M5. WD port 4450 exactly equals P's earlier WD port, and the plan's collision check omits P and E1 (attack 9)

Severity: MEDIUM.

Mechanism: the plan claims "no collision with Y4d 8768/4448 or Y9 8769/4449"
for server 8770 and WD 4450. The E1 experiment log records "P used
4450/8765, R used 8766" (improvements/worker-x-e1-experiment-log.md line 20).
P's WD port is exactly 4450, the port Y13 chose. E1 uses WD 4451 and HTTP
8767, adjacent but distinct. The plan never mentions P, R, or E1 in its port
section. If a geckodriver from P is still bound to 4450 on the laptop, Y13's
geckodriver fails to bind, session creation fails, wd_failures increments,
and the run aborts after two consecutive session failures with zero tests
driven. The preflight stale-geckodriver sweep (copied from run_agyq2.py)
globs /tmp/geckodriver-*.pid and kills only PIDs whose parent is dead, so a
live P driver would be spared and Y13 would still fail to bind; an orphaned
P driver would be killed, which is the desired outcome but is also a
cross-runner kill the plan never acknowledges. P's current liveness could not
be determined from this VM; the ship-time check must be: ss -ltn for 4450
and 8770, pgrep -af geckodriver, and the /tmp/geckodriver-4450.pid file,
before launch. A second, smaller hole: run_live.py start_server reuses a
live server on the port only when a hardcoded clone1 fixture path answers;
on port 8770 a stale Y13 server from a previous attempt would answer 404
for that probe, so start_server would try to bind 8770 again and die with
EADDRINUSE, and the plan names no handling for it.

Evidence: plan Ports row; improvements/worker-x-e1-experiment-log.md line
20; tests/realistic/run_agyq2.py preflight sweep (glob /tmp/geckodriver-
*.pid, parent check).

### M6. The reload click can raise after navigation, and the plan has no tolerance for it (attacks 4 and 5)

Severity: MEDIUM.

Mechanism: test-10 steps 21 and 26 click #btn-reload-settings, whose handler
calls location.reload() synchronously during click dispatch. The reload
button is the only click in the suite whose handler navigates the page away.
Marionette's element-click command can return an error when the document
unloads mid-command (stale element or dead object), even though the reload
itself happened. The plan's mapping is "click #btn-reload-settings, then
wait_ready + 1s settle + diagnose_body", with no tolerance for a click error
on these two steps and no instruction to treat a navigation-related click
error as success-then-wait. If d.click raises, r.step records FAIL, raises,
and aborts test-10, even though the page did reload and the subsequent
verifies would have passed. The plan explicitly rejects d.refresh() as an
alternative but offers no third path for a click that raises post-navigation.

Evidence: plan test-10 mapping rows; fixture test-10-extension-settings.html
line 79 (onclick location.reload()); test-10 spec steps 21 and 26.

### M7. Test-05 walk: no mid-test navigation exists, so the ladder can never fire mid-test, and a hidden body would be misclassified (attack 5)

Severity: MEDIUM.

Mechanism: test-05 has no reload, no navigation, and no new-document load
after open_fixture. By the known Transparent Zen mechanism (content script
at document_start adds tz-hidden; removal is async with no timeout), a
genuine hidden body can only appear at document load, which open_fixture's
ladder already covers. A mid-test hidden encounter in test-05 would therefore
require a mechanism outside the known one (for example a late re-injection
or a Marionette failure that looks like a hidden body). If it happens, the
ladder never runs: no ensure_visible call exists between test-05 steps 1 and
26, the poll (2.0 s), the verified removal, and the rebootstrap are all
unreachable, and the step fails as a live failure, resets infra_blocked to
0, and gets no re-run. The plan's claim that a mid-test hidden body is INFRA
is therefore false for test-05 in particular: the classification depends on a
diagnose-on-failure step that does not exist in the copied code. The honest
statement is that test-05's exposure is confined to load time (covered) and
to unknown mechanisms (uncovered), and the plan should say that instead of
claiming a general mid-test INFRA rule.

Evidence: test-05 spec (no reload or navigation step); run_agyq2.py
ensure_visible call sites (open_fixture and bootstrap only); plan ABORT
section.

### M8. No contingency if Y9 fails or the queue stalls, and the D1 revisit trigger is the wrong event (attack 8)

Severity: MEDIUM.

Mechanism: the plan's queue is Y8b, then Y9, then Y11b, then Y6c, then Y13.
Every link depends on the previous runner's completion, but the plan states
no decision rule for a failure anywhere in the chain. If Y9's run FAILS, does
Y13 still run? The plan does not say. The D1 revisit clause says "Revisit
ONLY if Y11b's proof run passes before my run AND the council agrees the API
diff is safe." The trigger is Y11b passing, not Y9 failing. So a Y9 failure
that disproves the 1e3901c base (for example a run_live.py bug Y9 hits) does
not trigger any revisit, and Y13 would proceed on a base just disproved. A
Y9 failure that stalls the queue (no completion, no marker) leaves Y13
polling todolist-push with no timeout and no escalation rule. The plan also
does not state what Y13 does with Y9's findings if Y9's run finds the park
broken (see H6): there is no "if Y9 reports the park broken, do not use the
park" branch.

Evidence: plan Base pin D1 and Slot/queue sections; queue order in the plan
vs the live queue (Y8b E1, Y9, Y11b, Y6c, Y13).

### M9. The ported verify's return discipline is unspecified, and there is no pre-suite live-eval smoke test (attack 3)

Severity: MEDIUM.

Mechanism: check.mjs verifyTest is page.evaluate((testId) => {...; return
{passed, failures, score, state};}), an arrow function with a return inside.
The Marionette port must preserve a value return: either keep the arrow
function and invoke it, or paste the body as a top-level script with a
top-level return. run_live.py at 1e3901c documents the trap in a comment:
"the top-level return is REQUIRED. Marionette /execute/sync runs the script
as the body of an anonymous function, so a bare IIFE expression evaluates and
discards its value (the call returns null). Every value-returning script in
this file needs the explicit top-level return; _DIAG_JS shipped without it
and diagnose_body crashed on a None snapshot on the first live run." Y9's
_VERIFY_JS ends with a top-level "return {passed: ..., failures, state};"
and its verify_test passes testId via arguments[0]. The Y13 plan says only
"1:1 port ... executed via Marionette eval" and never specifies the wrapping
or the return discipline, and never cites the _DIAG_JS lesson for its own
port. If the port wraps the body in a bare IIFE without a return, d.eval
returns None, and the integrity guard does guard["passed"] on None, which
raises TypeError inside open_fixture. That aborts the test as a runner error
with a confusing traceback, and it would repeat identically for all 10 tests,
wasting the live slot. The integrity guard IS a live eval of the verify, but
it runs inside the suite, per test, after the slot starts; there is no
30-second pre-suite smoke eval of the ported verify and of diagnose_body on
the laptop before test 01, which is the exact lesson Y4d recorded ("a
diagnose helper needs one live eval before the suite trusts it").

Evidence: plan "1:1 port" paragraph (no wrapping specified);
tests/realistic/run_live.py 1e3901c _DIAG_JS comment;
tests/realistic/run_agy_y2.py lines 1040-1052 (_VERIFY_JS return) and
1058-1152 (guard does guard["passed"] with no None handling);
worker-y4d-rerun-log.md finding 3.

## LOW

### L1. The value() trim divergence is theoretical here (attack 3)

Severity: LOW.

Mechanism: check.mjs value() reads .value.trim(); Marionette d.value returns
the raw property value with no trim. No fixture value in this suite has
leading or trailing whitespace (generated password "Cedar!9-Glass?", config
values, dates, "900", "2026-11-23"), so the divergence bites nowhere. The
password input (#entry-password-input, type=password) and the readonly
clipboard buffer (#clipboard-buffer) both return their values through the
property read. Recorded so the port author does not "fix" it by adding a
trim that would mask a real trailing-whitespace defect.

### L2. The date-input claim is verified for test-05 and test-07 but documented only for test-05 (attack 4)

Severity: LOW.

Mechanism: the plan's fixture facts document test-05 #event-start-date as a
plain text input and Q7 asks council to confirm it. Test-07 #from-date-input
and #to-date-input are also plain text inputs (placeholder YYYY-MM-DD, no
type attribute), verified in the fixture, but the plan never mentions them.
The "none seen in the fixtures" claim for type=date inputs is therefore
asserted, not evidenced, for the rest of the suite. No live risk was found:
all date-typed values in the suite are plain text inputs, and type_text is
the right primitive for them.

### L3. Y6c nested uses no TCP ports, but it still hazards the live screen (attack 9)

Severity: LOW.

Mechanism: the Y6b v2 nested launcher (improvements/worker-y6b-run-nested-
wayland-v2.sh) was grepped for port numbers: it uses Wayland sockets
(WAYLAND_DISPLAY, XDG_RUNTIME_DIR), grim, mpv, and foot, and binds no TCP
port. There is no port collision between Y6c and Y13 (8770/4450/2828). The
residual hazard is not ports: the nested run tiles its window over the live
screen, so a queue violation (Y13 driving while Y6c's nest is up) would break
Y13's clicks through focus and visibility, not through ports. The plan's
queue order (Y13 after Y6c) is the only protection, and it is coordination,
not a mechanism (see H5).

### L4. Y14 was spawned after the plan was written, and its ports are unknown (attack 9)

Severity: LOW.

Mechanism: a memory update recorded at 19:20 on 21/11 states Y14 was spawned
to run the batch-3 fixes live on Zen, queued after Y13, extending the live
queue to Y8b E1, Y9, Y11b, Y6c, Y13, Y14. The Y13 plan (written ~19:20)
does not mention Y14. No Y14 plan file exists yet in improvements/, so its
server, WD, and ship-dir choices are unknown and cannot be checked for
collision with 8770/4450 or /tmp/worker-y13-server. Y13's plan should state
the ship-time check for Y14's future ports and the requirement to leave the
machine clean (ports free, no geckodriver, shared tabs returned to
about:blank) for Y14, since Y14 runs immediately after.

## Checked, no hole found

1. Test-06 split and trim arithmetic (attack 4): 12-second forest split at
   playhead 5 gives 5+7; trim tail to 2 gives 5+2+8=15; undo restores 5+7+8
   =20; trim tail to 6 gives 5+6+8=19. The fixture's split and apply-trim
   handlers read #playhead-input and #trim-duration-input values at click
   time (fixture lines 69-87), and snapshot() copies the timeline but not
   selectedId, so the tail stays selected across undo. The arithmetic and
   the state hand-off are correct as specified.
2. Test-08 pivot refresh sequencing (attack 4): refresh reads the source
   input values at click time (fixture: "totals[row.category] +=
   Number(el(row.selector).value)"), so the step 19 stale-state check (pivot
   stays 600/2000 before refresh) is meaningful, and step 20 refresh to 900
   follows. Source values sum to 5200 overall and 2300 for South after the
   edit (600 replaced by 900, plus 1400). Correct as specified.
3. Test-02 shuffle determinism (attack 4): the shuffle handler uses a fixed
   order array (night-shift, quiet-circuit, paper-planes, low-tide) filtered
   to current tracks; no Math.random or Date.now in any fixture. The step 18
   expected order is deterministic.
4. Step count: the spec step totals (34, 22, 29, 27, 26, 36, 23, 21, 24, 27)
   sum to 269 as the plan claims.

## Sharpest three (for the parent)

1. H1: the Y9 park is not in the copy list and the base WD has no park, so
   DELETE /session closes the shared tab after every test and can close a
   user tab on the rebootstrap-failure and suite-end paths.
2. H7: the handover token is hardcoded to Y4d's file with a 4h window
   expiring ~22:44, the plan names no writer or renewal, and the
   wait-for-slot rule can push the run past the wall, so preflight may
   refuse to start the run at all.
3. H5: the queue gate is unspecified and blind: the flock does not cover E1,
   Y11b, Y6c, or Y14, and the only concrete process pattern misses E1's
   driver and executor entirely, so a second live runner can start
   undetected mid-suite.
