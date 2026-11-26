# Boundary browser restart procedure (R16, decided 2026-11-27)

Source decision: `improvements/team-decisions-20261127.md`, Item 4
(R16). This document is the generic procedure. Machine-specific
commands and paths live in the machine layer on the operator's
machine, never in this repo.

## Authority split (hard rules)

- **No watch ever kills or restarts a live browser.** No scheduled
  watch (cron) holds kill-live authority over a running browser.
  Watches are simple loops with a proven false-alarm record; kill
  power over the owner's browser repeats the tab over-close failure
  class (R6) with a bigger blast radius.
- **Revive-dead only.** The browser health watch may relaunch the
  browser only when BOTH hold: no browser process exists, AND the
  automation ports (BiDi and Marionette) are down on two consecutive
  checks. Every revive is logged with the full chain (fail,
  reasoning, tried, decision, fix, result). Reviving an already-dead
  browser destroys nothing that is not already destroyed.
- A live-browser restart is initiated deliberately by the coordinator
  on duty or a human agent, at a task boundary, never mid-drive, and
  never by a watch.

## Memory pressure

- Read-only threshold alert at **8 GB RSS (uncalibrated
  placeholder)**, plus a growth-rate alert (GB/h) in the health
  watch. The threshold predates any growth data; record RSS plus
  system headroom at every task boundary to calibrate it.
- The alert's human is the coordinator on duty. If nobody acts, the
  accepted outcome is stated plainly: the browser stays as is (or
  down, with revive-dead covering the dead case) until the next human
  or agent session, and session restore happens on next launch.

## Boundary restart procedure

Run deliberately at a task boundary, never mid-drive.

1. **Record.** Dump the open tabs, including pinned and essential
   tabs, via a BiDi list dump to a file before any restart. Where the
   BiDi list cannot see pinned/essential status, also decode the
   session file (mozlz4 container; requires the Python `lz4`
   package) and record pinned/essential state from it. The record
   file is the restore checklist for step 3.
2. **Restart.** Restart through the wrapper (the browser CLI's
   session stop/start for dedicated sessions; the owner's live
   browser only via its normal relaunch path, initiated by the
   coordinator or a human, never by a watch).
3. **Verify.** All of: automation ports up; the control pill visible
   ("Computer use active"); session restore happened; the owner's
   essential tabs present after; the open tabs match the record file
   from step 1, including pinned tabs.

## Agent-initiated tooling restarts

The same record-before / verify-after checklist and the R6 guardrail
govern restarts an agent initiates for tooling reasons (for example
offline session-file surgery), whoever initiates them:

- Offline session edits run only while the browser is fully closed,
  with a timestamped backup outside the profile, referential-
  integrity validation before and after, round-trip verification of
  the written file, and automatic restore of the backup if
  verification fails (the `zen_sessions.py` pattern).
- Prerequisite: the mozlz4 decoder (Python `lz4` package) installed
  and verified against a real session file. Verified 2026-11-27 on
  the operator's machine: a 3,060,932-byte pre-cleanup sessionstore
  decoded to 3,840,796 bytes of valid JSON (size match, 1 window,
  54 tabs).

## R6 guardrail (tab cleanup)

Tab cleanup is allowlist-only: only recorded, completed-task tabs
may be closed. Pinned and essential tabs are never matched, never
closed, never navigated. The control pill is visible during any
agent control of the machine, by any method.

## Drill requirement

This procedure is not "ready" until a throwaway-profile drill passes
on the real mechanism: open recorded tabs including a pinned tab in
a throwaway browser profile, run the procedure end to end (record,
restart, verify), and confirm restore and pill. The drill result is
logged to the master event log with the full chain. Until the drill
passes, treat the procedure as unproven and do not use it on a live
profile.

Drill status: PASSED 2026-11-27 on a throwaway profile (record,
restart, verify end to end; pinned tab persisted; pill confirmed by
screenshot). Drill findings folded into the procedure above: the
BiDi list under-records lazy-restored (unloaded) tabs, so the
session-file decode is the complete record; a first-run profile
stopped too early yields empty session files, so allow collection
time after opening tabs before recording or stopping.
