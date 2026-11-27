# R10 switch report: RDP lane becomes the operating configuration (27/11/2026)

Switch executed 2026-11-27 15:35-15:42 +07 per
`r10-landing-report-20261127.md` (switch list) and
`r10-seamless-decision-20261127.md` (route 3c, RDP-primary). Owner
accepted silent attach (RT-04) 27/11 14:00; RT-21 acceptance was
PARTIAL PASS with kill criterion 6 not triggered; council verdict
LANDING-READY WITH CONDITIONS. Machine-specific values (profile
dir, ports in use, pids) live only in the laptop machine layer and
the VM record dir; this report carries the generic facts.

## Config before / after

Before: owner Zen flag-free via zen-human (plain zen-bin, no
debugger server), probe CLEAN, 65 tabs, no RDP prefs in user.js,
registry selected count 0. Interim two-profile split operating.

After:
- user.js gains the generic RDP pref set (remote-enabled,
  chrome.enabled, prompt-connection=false per RT-04,
  remote-host=127.0.0.1, remote-port). Backup of the pre-switch
  user.js kept in the machine layer switch backup dir.
- zen-human now execs zen-bin with `--profile <owner profile dir>`
  and `--start-debugger-server <registry port>`, still flag-free:
  NO --remote-debugging-port, NO --marionette on the human path.
  The --profile argument makes the registry marker match the
  cmdline (fail-closed smoke requirement).
- Registry: exactly one channel selected (zen-rdp-owner);
  last_smoke recorded from the landed-config smoke below;
  zen-agent-split purpose updated to FALLBACK.
- Machine-layer doc zen-profile-split.md gained a successor
  section: RDP lane is the operating configuration; the split is
  retained as fallback; kill path back documented there.

## Restart + tab restore verification

Record-before: sessionstore decode, 65 tabs (url+title multiset
hash recorded). SIGTERM to the recorded main pid after cmdline
check (main process, no contentproc, no automation flags); exited
in 2 s. Relaunched via zen-human fully detached. New process:
cmdline carries --profile + --start-debugger-server, probe verdict
CLEAN (flagged false), debugger port listening on 127.0.0.1 only.
Tab decode after settle: 65 tabs, hash identical to record-before.
Zero tab loss. No compositor window-close used anywhere.

## Smoke on the landed config (before any drive)

rdp_smoke.py exit 0, all checks PASS: (a) port owner = new Zen pid,
(b) attach, (c) webdriver false with native getter, verdict CLEAN,
(d) evaluate, (e) parent target Zen internals typeof object x3,
(f) loopback-only bind, (h) navigate complete, (g) latency
informational: attach-to-first-evaluate 23.0 ms, evaluate median
0.5 ms. Smoke ran with a fresh tasked tab selected so check (h)
touched only that tab. Result recorded in the registry.

## First supervised drive (real profile)

Discipline: URL-pattern scope only, credential denylist ON
(default), --lock-file set, no test flags, no --allow-parent.
Tasked tab opened and navigated via the OS-input lane (pill
visible, label "Computer use active"; Ctrl+N opens a new tab in
Zen, Ctrl+T is blocked by the tool guard). Drive: evaluate
document.title = "Example Domain"; navigate in-scope;
evaluate title + URL confirmed. Drive report: probe CLEAN
(native getter), scope URL-pattern, denylist enabled (not
disabled via flag), retries 0. Tasked tab closed via OS lane;
final sessionstore decode: 65 tabs, identical to record-before.

Two tool-guard corrections hit and handled during the drive prep
(recorded in the event log): Ctrl+T refused (use Ctrl+N), and an
act-now wait of 3000 ms refused (limit 2000). Neither touched
owner tabs.

## Rollback readiness

Backups in the laptop machine layer switch backup dir: user.js,
prefs.js, zen-human, registry, zen-profile-split.md (all
pre-switch, sha256 recorded in the VM record dir). Kill path:
restore those files, restart via zen-human, verify probe CLEAN +
tabs identical; the interim split resumes as operating
configuration. No rollback was needed: smoke passed on the first
landed-config run.

## State after switch

- Operating configuration: RDP lane on the flag-free owner
  session (same live session, seamless attach, silent per RT-04).
- Fallback: interim two-profile split (dedicated agent profiles,
  flagged lanes) retained; zen-ai escape hatch deliberate + logged
  only; Marionette chrome stays out of the owner session.
- R10 stays OPEN until the first post-update drill passes (smoke
  + Google spot check before agent use resumes after a Zen
  update; FAIL retires the lane to the split per kill criterion 1;
  the zen-laptop-health watch step 1b already runs the smoke on
  version change and now finds a selected channel).
- Evidence: VM record dir r10-switch-record-20261127/ (tab lists,
  smoke JSON, drive reports, OS-lane logs, screenshot); laptop
  /tmp/r10-switch/ (scripts, logs, backups); event log source
  r10-switch.

Coordinator, 27/11/2026. English only. No personal information in
this document; machine-specific configuration lives only on the
laptop machine layer.
