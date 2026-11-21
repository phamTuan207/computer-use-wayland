# agy-q2 live rerun report, 2026-11-21

Worker Y4d. Runner `tests/realistic/run_agyq2.py` (diagnose-first ladder per
Y4b's design, council + redteam reviewed), driver `tests/realistic/run_live.py`.
Live on the owner's Zen, owner away (handover 18:24 +07, token
`/tmp/worker-y4d-handover.json` on the laptop). One fresh WebDriver session
per test. Raw logs on the laptop: `/tmp/worker-y4-run-2.log` (final run),
`/tmp/worker-y4-run-1.log` (first run), `/tmp/worker-y4-live-2.jsonl`.

## Headline

**10/10 clean passes, 0 flagged, 0 failed. Total 49,885 ms.**
`passed` counts clean passes only; flagged passes are counted separately and
there were none. Exit code 0.

## Per-test results, final run (run 2, 18:50-18:51 +07)

| test | result | ms | note |
|------|--------|----|------|
| q01 whiteboard | PASS | 5599 | |
| q02 recipe app | PASS | 5067 | checker case fix, see below |
| q03 habit tracker | PASS | 5012 | |
| q04 budget tracker | PASS | 4775 | |
| q05 contact book | PASS | 4828 | |
| q06 file converter | PASS | 4834 | checker whitespace fix, see below |
| q07 weather dashboard | PASS | 4787 | |
| q08 quiz app | PASS | 5142 | |
| q09 pomodoro timer | PASS | 4942 | |
| q10 markdown editor | PASS | 4899 | |

Suite JSON: `{"suite": "agy-q2", "passed": 10, "flagged": 0,
"total_passed": 10, "failed": 0, "total": 10, "total_ms": 49885,
"hidden_body_encounters": 0, "bootstrap_intervention":
{"tz_hidden_removed": false, "hidden_body_encounters": 0},
"tracked_item": "improvements/transparent-zen-defect-tracked-item.md"}`.

## Hidden-body / Transparent Zen verdict

**0 hidden-body encounters across both runs (20 tests total). No tz-hidden
class was ever sighted. The Transparent Zen mechanism was NOT confirmed
live in this rerun.** The diagnose-first ladder ran on every navigation
(`diagnose_body` after each goto/refresh, VISIBLE every time); the poll,
removal, and rebootstrap-recovery paths never fired for a real hidden body.
That is a clean bill for the browser during these two runs, not proof the
extension is innocent: V1 stays the prime suspect from Y4b's code evidence,
and the decisive experiment (Council C design) is still the way to prove or
refute it. The tracked item for the extension defect is
`improvements/transparent-zen-defect-tracked-item.md` (OPEN, decision owed).

## Run 1 (18:47-18:48 +07): 8/10, both failures were checker bugs

| test | result | ms | failure |
|------|--------|----|---------|
| q02 | FAIL | 5111 | check `"4 tbsp olive oil" in norm(ing)`; actual text was `4 tbsp Olive oil` |
| q06 | FAIL | 4848 | checks `txt(badge) == "Downloaded"`; actual textContent was `"\n Downloaded\n"` |

Both are checker bugs, not app bugs, proven against the fixtures:

- q02: fixture `test-02-recipe-app.html:146` stores the ingredient as
  `{ name: 'Olive oil', qty: 2, unit: 'tbsp' }`. At 4 servings the app
  correctly renders `4 tbsp Olive oil`. The check demanded lowercase
  `olive oil` while `norm()` only collapses whitespace, it never
  lowercases. Fix: `"4 tbsp olive oil" in norm(ing).lower()`.
- q06: fixture `test-06-file-converter.html:193` renders the badge as
  `${item.downloaded ? 'Downloaded' : 'Ready'}` inside a template literal
  with newlines, so `txt()` (raw textContent) returns
  `"\n Downloaded\n"`. The app did mark both files Downloaded; the exact
  `== "Downloaded"` comparison was too strict. Fix: compare
  `norm(txt(...)) == "Downloaded"` for both badges.

Both fixes were applied and verified live in run 2 (q02 PASS, q06 PASS).
Run 1 suite: passed 8, flagged 0, failed 2, total_ms 49741, exit 1.

## Findings beyond the headline

1. **The shared bootstrap tab does not survive its session.** Every test
   (10/10 in both runs) printed `shared tab gone, rebootstrap`, and the
   suite-end cleanup hit `no such window` for all 10 rebootstrap tabs.
   Observed fact: a tab created inside a WD session is gone by the next
   session. Most likely mechanism: Marionette `DELETE /session` closes the
   session's current top-level window (the bootstrap tab was the current
   window at its session's exit, even though it was removed from
   `opened_tabs`). The suite still ran correctly because `rebootstrap_tab`
   creates a fresh visible tab per test, but the "shared tab" design is
   currently fictional. Follow-up: either keep one session alive for the
   whole suite, or accept per-test bootstrap tabs and say so.
2. **Preflight caught two real bugs before the run.** (a) The BiDi
   liveness probe used `/json/version`, a Chrome path that 404s on
   Firefox/Zen; fixed to `GET /` (200, httpd.js root page). (b) The
   Hyprland signature was not in the compositor's environ (UWSM launch);
   fixed by discovering it from `$XDG_RUNTIME_DIR/hypr/<signature>/` and
   verifying the socket with a real AF_UNIX connect. Preflight positive
   test (under flock + token): PREFLIGHT OK. Negative test (no flock):
   refuses. Both on the laptop.
3. **First launch crashed on a latent `_DIAG_JS` bug.** Marionette
   `/execute/sync` runs the script as a function body, so the bare IIFE
   `(() => {...})()` evaluated and discarded its value; `d.eval(_DIAG_JS)`
   returned None and `diagnose_body` crashed on `snap1.get(...)`. Fixed
   with a top-level `return` plus None-sample guards in `diagnose_body`
   (a null sample is now FIXTURE_FAILURE, never a crash). Proven live by
   a probe: full snapshot dict, VISIBLE, tzHidden False, rafTicks 3.

## What was implemented (Y4b design + council/redteam fixes)

- `diagnose_body` + classification (VISIBLE, TZ_STUCK_V1, OTHER_HIDDEN,
  FIXTURE_FAILURE; no V2), double sample 300 ms apart when hidden.
- `WD.goto`/`refresh`/`new_tab` diagnose after settle and raise
  `INFRA: hidden-body` by default; `allow_hidden=True` only on ladder paths.
- Recovery ladder in `ensure_visible`: poll 2.0 s, remove tz-hidden (class +
  `--zen-logo-path`, flag only on verified removal), rebootstrap, 8.0 s
  enforced deadline, FIXTURE_FAILURE raises without burning tabs.
- Flagged-pass accounting: `passed` is clean-only, `flagged` separate,
  `SUITE FLAGGED` headline when flagged > 0 or a bootstrap intervention
  occurred; tracked item cited in the suite JSON.
- Preflight fail-closed: handover token (env + fresh token file, per-test
  re-check, 4 h expiry), BiDi + Marionette liveness, Hyprland IPC SAFETY
  gate (labeled safety, not incident detector), fixture loopback, stale
  geckodriver sweep by PID (orphans only, cmdline re-verified before
  SIGKILL), lock check accepting POSIX/FLOCK/OFDLCK (flock is FLOCK).
- Session hygiene: geckodriver log in append mode, PID file, cleanup on
  session-POST failure, exception-proof teardown.
- Switch-away step and repaint step removed; no V2 anywhere; no real click
  as a recovery probe; no user tab ever switched to (registry of known
  test-tab handles only).

Review: council 1 (diagnose), council 2 (ladder + accounting), council 3
(preflight, BLOCK), redteam (BLOCK). All required fixes applied; the two
BLOCKs were the FLOCK lock filter and the owner-away token. Review papers:
`improvements/worker-y4d-council-1-diagnose.md`,
`improvements/worker-y4d-council-2-ladder.md`,
`improvements/worker-y4d-council-3-preflight.md`,
`improvements/worker-y4d-redteam.md`.

## Gaps, stated plainly

- The ladder's poll / removal / rebootstrap-for-hidden paths never fired
  for a real hidden body in these runs, so the recovery itself is still
  unproven live (only the diagnose + visible path and the rebootstrap for
  a missing tab ran). The decisive experiment is the proof, not this rerun.
- The shared-tab finding (item 1 above) means each test paid a fresh-tab
  creation; per-test wall time (~4.8-5.6 s) includes it.
- Run 1's first launch crashed before any test (the `_DIAG_JS` bug); the
  fixed code is what ran in both scored runs.
