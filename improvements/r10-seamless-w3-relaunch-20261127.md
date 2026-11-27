# R10 seamless-control spike W3 - attach-on-demand relaunch measurement (27/11/2026)

Route under test: owner browses flag-free; when an agent is called, Zen
relaunches flagged (session restore), the agent works, then Zen relaunches
flag-free. Measured on a throwaway headed profile on the laptop (ws2, pill
visible throughout). Owner live Zen (PID 439493, flag-free) was never
signalled, navigated, or closed; every kill was by recorded pid with a
cmdline check containing the throwaway profile path. No compositor
window-close was used. ydotool was not used.

Prior context: r10-stage1-report-20261127.md priced boundary-restart with
"observed Zen relaunch to usable session (minutes)"; r10-stage2-decision-
20261127.md rejected boundary-restart unanimously as dominated. This spike
tests whether that pricing and rejection still hold.

## Verdict in one paragraph

One agent call under this route costs about 1 second of window absence on
each restart (about 2 seconds total, plus the agent's own working time),
but the agent cannot attach over BiDi for about 46.5 seconds after the
flagged relaunch (Marionette attaches in about 6 seconds). Restore fidelity
is high: 19 of 20 tabs, typed form text, and scroll position all survive
exactly, verified at page level; JS heap state is lost (by construction),
the first tab is replaced by a blank tab in this throwaway ad-hoc profile,
and the previously active tab is not re-activated (a New Tab is active
instead). During the whole agent session the owner's browsing in that same
session is flagged (navigator.webdriver = true), which is the Stage 2 leg-1
failure. The Stage 2 rejection still holds, but its "minutes to usable"
pricing is wrong and should be corrected to seconds-to-window /
46.5s-to-BiDi-attach.

## Setup

Throwaway profile /tmp/r10-w3-profile (removed after measurement),
user.js: browser.startup.page=3 (restore previous session),
zen.welcome-screen.seen=true, warnOnClose off, updates off. 20 tabs:
form.html (typed text, not submitted), scroll.html (scrolled to 2500),
jsstate.html (counter clicked to 7, localStorage control set),
15 filler pages, https://example.com/, https://example.org/.
Before-truth recorded by BiDi read in the setup instance and by
session-file decode (mozlz4 via python-lz4): formName
"W3-FORM-TEXT-20261127", formNote "W3 note line survives restart?",
scrollY 2500, counter 7, lsControl "LS-VALUE-42".

Cycles measured (run2, clean): setup flagged, baseline flag-free cold
start of the same profile, Cycle A flag-free to flagged, Cycle B flagged
to flag-free, Cycle C and D repeat the pair. Run3/run4 repeated the
fidelity setup with real key-event typing and the form tab not in
position 0. Run5-run9 chased page-level readback of restored tabs
(failure chain below).

## Timing table (run2; seconds from launch command unless noted)

| Launch | Window visible | BiDi listen | BiDi session.new OK | Marionette session | Close (SIGTERM to exit) |
|---|---|---|---|---|---|
| Setup flagged (fresh profile) | 1.02 | 1.02 | 46.47 | - | 0.03 |
| Baseline flag-free | 0.51 | - | - | - | 0.03 |
| Cycle A flagged | 1.02 | 1.02 | 46.51 | - | 0.03 |
| Cycle B flag-free | 1.02 | - | - | - | 0.03 |
| Cycle C flagged | 1.02 | 1.02 | 46.56 | - | 0.03 |
| Cycle D flag-free | 1.02 | - | - | - | 0.03 |
| Run4 flagged (repeat) | 1.01 | - | 46.57 | - | 0.03 |
| Run5/run6 flagged | - | - | - | 5.92 / 5.62 | 0.03 |

Notes:
- "Window visible" is hyprctl clients showing the new pid's window.
  Screenshots at settle (window + 4s) show the sidebar tab list already
  restored (lazy tabs listed, active tab is a New Tab).
- BiDi attach latency is consistent at 46.5s across five flagged
  launches (46.47, 46.51, 46.51, 46.56, 46.57). The port listens at
  about 1s; the delay is inside session.new. Cause not isolated here.
  Marionette session creation on the same launches took 5.6-5.9s from
  launch, so the 46.5s is BiDi-specific, not browser startup.
- Every close exited 0.03s after SIGTERM with rc=-15 (killed by the
  signal, no graceful exit code). Session files were already flushed
  by periodic collection (setup waited 20s before closing). A real
  boundary-restart must guarantee collection before SIGTERM, or tab
  changes from the last collection interval (default about 15s) risk
  loss. Untested here: a tab opened less than 15s before close.
- Baseline (flag-free relaunch of the same warm profile) isolates
  restart overhead: flag-free and flagged window times are the same
  (about 1s); the flagged overhead is entirely the attach wait.

Owner-visible interruption per agent call: about 0.03s + 1.0s (restart
to flagged) + agent attach wait (46.5s BiDi / about 6s Marionette,
window present and browsable meanwhile) + agent work time (flagged
browsing) + 0.03s + 1.0s (restart back to flag-free). Window-absent
time totals about 2 seconds.

## Fidelity table

| State | Before | After cycles (page-level read, run9) | Verdict |
|---|---|---|---|
| Tab list (20) | 20 URLs/titles | 19 real tabs + 1 blank (tab 0 replaced) | 19/20 survive |
| Form name field | W3-FORM-TEXT-20261127 | W3-FORM-TEXT-20261127 | SURVIVES exact |
| Form note field | W3 note line survives restart? | same | SURVIVES exact |
| Scroll position | 2500 | 2500 | SURVIVES exact |
| JS heap counter | 7 | 0 | LOST (new process) |
| localStorage control | LS-VALUE-42 | LS-VALUE-42 | SURVIVES (profile DB) |
| Active tab | Form tab active at close | New Tab active | NOT restored as active |

Evidence layers:
- Session-file decode after every close (run2, 6 snapshots): zen-
  sessions.jsonlz4 consistently 19 tabs, recovery.jsonlz4 20 entries
  with about:blank replacing tab 0; scroll stored as "0,2500" in both
  files across all cycles; formdata stored with full values when typed
  with real key events (run3/run4), empty when set by synthetic JS
  (run2 - method artifact, see failure chain).
- Screenshots (run2 Cycle A, run9 launch): sidebar shows restored tabs
  (Example Domain x2, fillers, JS State, Scroll, Form in run9) with a
  New Tab active.
- Page-level read (run9, OS click activation then Marionette evaluate):
  form both fields exact, scrollY 2500, counter 0, lsControl intact.
  This read happened after multiple restarts (setup, flag-free,
  flagged, flag-free, plus run5-run8 flagged launches on the same
  profile), so survival is cumulative, not single-restart only.
- Tab 0 loss: in run2 the form tab was tab 0 (navigated startup tab)
  and was the one replaced by about:blank; in run3/run4 filler-04 was
  tab 0 and was the one missing from zen-sessions.jsonlz4 while the
  form tab survived. The loss follows position 0, not the page type.
  Caveat: this is an ad-hoc --profile throwaway. A registered-profile
  relaunch may behave differently (the owner's real relaunch today was
  reported elsewhere as 65 tabs restored, none lost - not measured by
  this spike). Tab-0 loss needs a registered-profile test before it is
  generalized.

## Agent-attach reality on restored tabs (design-relevant)

Restored tabs are lazy: present in the sidebar and session files, but
with no loaded document until activated. Consequences measured:
- BiDi browsingContext.getTree on a restored flagged instance lists
  1 context (the active New Tab), not 20 (run2 Cycles A/C, run4).
- BiDi input.performActions Ctrl+Tab (correct U+E009/U+E004 codes)
  produced no tab switch and no error (run4, 30 steps, still 1 tab).
- Marionette lists all 20 handles with correct URLs/titles, but
  switch_to_handle does not load the pending document; evaluate reads
  about:blank even after a 20s wait (run5/run6).
- JS location.href assignment to file:// from the blank tab is denied
  (null principal, run7). WebDriver navigate loads the page fresh but
  without stored form/scroll restore data (run8: form empty,
  localStorage intact).
- OS-level sidebar click (computer-use, pill visible) loads the tab
  with restore data applied (run9 - the only route that worked).

For the seamless route this means: after a flagged relaunch, an agent
that needs the owner's restored tabs cannot reach them through BiDi or
Marionette alone on this build; activation needs an OS-level click (or
a browser mechanism not found here). Fresh-page agent work (the frozen
R3-L3 pattern) is unaffected.

## Failure chain (no silent skips)

1. Run1 stopped and discarded: close check mistook a zombie /proc
   entry for a hung browser (60s waits, meaningless SIGKILLs), the
   session parser used the Firefox windows[] shape on Zen's tabs[]
   file, and a parallel worker's 19 probe tabs entered the throwaway
   browser through the shared BiDi port 9333 after the setup record
   (session file showed 38-39 tabs). Driver fixed (Popen wait, Zen
   parsers, JSON-string evaluates, foreign-tab guard); run1 logs kept
   on the laptop during the spike, evidence summarized here.
2. Run2 formdata capture failed (note stored empty, name missing)
   because values were set by synthetic JS events. Real key-event
   typing (run3/run4) captures correctly. Recorded as method artifact.
3. Run3 record-activate failed: input.performActions "invalid
   argument" (literal 'Control'/'Tab' key names). Fixed to Unicode
   codes; run4 then showed the keys are accepted but do not switch
   tabs. Run3 also leaked its flagged instance on phase failure; the
   next launch collided (90s window timeout, recovery file showed 40
   tabs from the double launch). Fixed with try/finally close in run4.
4. Run6 killed mid-run by the operator (20s wait per tab, outcome
   already clear); its geckodriver leaked and caused run7's first
   "Session is already started" failure. Stale geckodriver killed by
   pid after cmdline check; run7 rerun proceeded.
5. Run9 first click rejected twice (wait 3000ms over the 2000ms cap;
   full-resolution coordinates outside the 960-wide observation).
   Both corrected; clicks then succeeded (ok=true, input_sent=true).

## Cleanup verification

Throwaway Zen processes: none remain (ps checked after each run and at
the end). Geckodriver: none remain. Ports 9333/2828/4445: free. Pill:
released (holders empty, visible=false). Profile /tmp/r10-w3-profile
and work dir /tmp/r10-w3 removed from the laptop. Owner Zen PID 439493
alive at every phase check and at the end, flag-free cmdline unchanged.
Evidence on the VM: ~/workspace/r10-seamless-w3/ (run2 results.json,
measure.log, record-setup.json, screenshots 00-05; run3/, run4/, run5/,
run8/, run9/ subdirs with logs, records, screenshots; driver scripts
measure.py, measure3.py, measure5.py, measure6.py, measure7.py,
measure8.py, bidi-helper.mjs, bidi-helper3.mjs, read9.py,
make-pages.py).

## Answer to the Stage 2 question

Boundary-restart pricing corrected: relaunch to a visible window with
restored tab list is about 1 second, not minutes. The real costs are
(a) 46.5s BiDi attach latency per agent call (about 6s via Marionette),
(b) flagged browsing for the owner during the entire agent session
(Stage 2 leg-1 failure, unchanged), (c) JS heap state loss and
active-tab reset on every cycle, (d) one tab lost per restore in this
ad-hoc profile (position 0; registered-profile behavior untested),
(e) restored owner tabs unreachable to BiDi/Marionette agents without
OS-level activation. On (b) alone the Stage 2 rejection stands; this
spike removes the "minutes" argument from it and replaces it with the
attach-latency and activation numbers above.
