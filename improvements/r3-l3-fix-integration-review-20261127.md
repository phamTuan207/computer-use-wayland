# R3-L3 post-run fix-integration review (27/11/2026)

Owner order 18:18-18:19 26/11: during R3-L3, record only; after the run
closes, council reviews the full record, redteam challenges, and only the
best, most essential fixes get integrated. R3-L3 closed 04:49 27/11 at
Rule-A 52 PASS / 1 FAIL (bars 50/52 and 51/53 both met).

Method: coordinator evidence pack (14 candidates) from the master event
log (laptop ~/agent-event-log/events.log, 1410 fix/error lines for
25-27/11), per-task reports, grades ledger, daily notes, improvements
dirs, and the error tracker; 3 independent council reviewers on separate
slices; 1 redteam reconciling and killing weak candidates. Working files:
fix-review-evidence-pack-20261127.md, fix-review-council1/2/3-20261127.md,
fix-review-redteam-20261127.md (same directory).

## Ranked integration list (reconciled R-numbers)

| # | Fix | Impact | Risk | Verdict |
|---|-----|--------|------|---------|
| R1 | Signal hygiene: state-write helper (task_start + runner identity PID-or-session, cleared at drive end), heartbeat/state cadence during long drives, timeout-watch completed-task guard (two signals), Muse-lane timeout by subagent close, liveness suppression inside task deadline | High: prevents wrong-kill of live panes and unkillable drives; kills false liveness alarms | Medium: watch bodies + checklist; dry-run kill test required | INTEGRATE |
| R2 | Keybind-first hard rule in repo brief template (docs only) | High: steers every future drive | Low | INTEGRATE |
| R6 | Tab-cleanup guardrail: recorded completed-task tabs only, allowlist, dry-run list, pinned/essential never matched | High: prevents repeat owner-tab loss (24-tab over-close created Task 56) | Low-Med: throwaway-profile test | INTEGRATE |
| R5 | Tier A checker regression tests (bilingual json, R3-021 CSV, DP-02 detail lines, R3-072 pipe table, R3-076 labels) + mutation controls + narrow union broadening the tests prove | High: removes tiebreakers and scorer overrides | Low: union-only acceptance | INTEGRATE |
| R4 | Overlay session-owner hide on final release PAIRED with explicit show in _show_label session branch, two-cycle test | Med-High: fixes lying pill status | Med: unpaired hide would create invisible-pill risk (redteam kill); paired + two-cycle test required | INTEGRATE (paired only) |
| R3 | Fail-closed pill gate in BiDi session start/stop, mirroring cdp.mjs, plus spawn preflight rule | High: makes pill rule structural | Med: gate-induced outage possible; preflight required | INTEGRATE |
| R7 | Act-now fail-loud on stale/captured observation with window-space points, fixture test | High: kills silent-miss class corrupting evidence | Med | INTEGRATE |
| R8 | Machine-layer drive anomalies (laptop only): single stdin redirect, launcher keybind, terminal close keys, SSH pipe-drop expectation, grim default output | Med: proven recurrences | Low: laptop docs only | INTEGRATE (corroborated only) |
| R9 | Evidence collect checks: duplicate-file detection, missing-screenshot rejection, timestamp precision tolerance, snapshot subdir/manifest handling | Med: cheap detection | Low | INTEGRATE |
| R10 | Cloudflare holder safe residue: hash pin in probe, probe result in every drive report, dirty probe = stop | Med | Low | INTEGRATE (residue only) |
| R11 | Holder lifecycle brief rules; session-guardian preflight; lane procedure table | Med | Low: brief text | INTEGRATE |
| R12 | Fixture and answer-key freshness preflight (absorbs old C14) | Med | Low: process | INTEGRATE |
| R24 | Wrong-keybind verification rule: verify against live config, never defaults alone | Med | Low: brief text | INTEGRATE |
| R13 | Focus-theft verify line, park-move rule correction, Ctrl+Shift+T guard narrowing | Med | Low-Med | DEFER (batch with R11 follow-up) |
| R14 | Ops cleanup: foreign untitled docs tab (R3-046 leftover), leftover window sweep | Low-Med | Low: verify-first | DEFER (after R6) |
| R15 | Speed-daemon diagnosis (45 starts verified; cause unknown; instrument exit reason + supervisor heartbeat first) | High if solved | High blind | DEFER (diagnosis first) |
| R16 | Browser memory threshold alert + boundary-only restart procedure | Med | Med: restart authority is owner's | DEFER (alert first) |
| R17 | Zen folder operations without vision | High if proven | High unverified | DEFER (laptop proof owed) |
| R18 | Pill label unification | Med | Low | OWNED ELSEWHERE (separate worker) |
| R19 | Ledger-push watch posture | Med | Security posture | OWNER DECISION |
| R20 | Session-store decoder presence on laptop | Low | Low | DEFER (laptop batch) |
| R21 | Cross-VM verdict channel standardization | Low | Low | DEFER |
| R22 | PII scan manual-review class | Med | Security | OWNER DECISION |
| R23 | Marionette/BiDi session hygiene experiment (Arm F) | Low | Low | DEFER |

## Key evidence (per item, short)

- R1: heartbeat log stopped 02:18:50 27/11 while coordinators worked to
  04:48; liveness false alarms ~2.5h. R3-078 honest record: task_start/
  runner_pid never recorded. Task 56: Muse-lane runner has no OS PID by
  design, coordinator never closed the subagent at 30 min (73-min overrun).
  25/11 near-miss: stale task_start would have let a literal watch kill the
  live FCC pane (PID 22399) at 13:56:22.
- R2: grep keybind/vision in docs/brief-template.md = empty (27/11);
  machine layer already carries the rule (keybinds.md rule 9,
  fastest-paths.md line 5, 27/11).
- R6: 26/11 02:15 cleanup closed 24 tabs incl. 5 essentials + 3 pinned;
  Task 56 was created to repair it.
- R5: R3-002 rerun Tier A FAIL on English format (fixed 25/11, bilingual
  union verified in tier-a-check.py lines 97-103); remaining false
  negatives: R3-021 header, R3-072 pipes, R3-076 labels, DP-02 brief defect.
- R4: overlay.py session-owner _show_label never sends "show" (only
  "label"); final release never sends "hide"; pill stuck ON, status lies
  (verified 25/11 10:59, 11:01). Unpaired hide = invisible-pill risk.
- R3: zen_dom.py has zero pill references (verified); pill proven only via
  manual acquire/release wrapper (G-44).
- R7: tracker J35/J40 silent screen-fallback in act-now (root of click
  misses); R3 evidence in council3 slice.
- R8: per-task anomaly blocks: Super-only refused 4x, Alt+F4 no-close 2x,
  duplicate stdin redirects 3x (R3-075/076/082), SSH broken pipe on
  detached launch (benign), colon unsupported XKB (R3-078).
- R9: snapshot traps: manifest self-hash, top-level-only collect,
  *.png gitignore, naming (council2 slice); fabrication detection existed
  but sealing enforcement was the gap.
- R10: holder exists at improvements/fixb-evidence/holder-fixb.mjs
  (not /tmp-only); probe webdriver inconsistency (true vs false) unexplained.
- R17: Clone2 research DONE 27/11 (report
  improvements/zen-folder-tool-research-20261127.md, tools
  improvements/zen-sidebar/: zen_live.py, zen_sessions.py,
  test_zen_sidebar.py; commits c045bfe4, 8bc66191 on todolist-push).
  Recommended route: live Marionette chrome JS (folder.addTabs,
  gZenWorkspaces.changeWorkspaceWithID, gBrowser.pinTab). Laptop
  throwaway-profile verification still owed; integrate only after proof.
- R15: daemon.log shows 45 starts; supervisor exists but its log is empty;
  deaths 26/11 (7x) and 27/11 (2x+), cause unknown.

## Rejected (do not integrate as written)

- Tier A bilingual parse as new work: already fixed 25/11 (verified).
  Remainder is R5 tests.
- Liveness "read a second signal" standalone fix: all three signals froze
  during Task 56 while the coordinator was alive; root fix is writer
  cadence (R1).
- Evidence-fabrication "hard gate" as sketched: detection existed and
  fired; no enforcement point designed. Mechanical parts live in R9.
- brief_check enforcement line for R2: over-engineering; template line
  suffices.
- Any speed-daemon supervisor rewrite before diagnosis: blind change can
  mask the cause or double-start.
- Answer-key freshness as a standalone item: absorbed by R12.

## Owner-decision items (team must not decide)

1. R19 ledger-push watch: approving validators in the flagged worktree,
   or moving validation to a clean checkout (evidence-chain safety posture).
2. R10 durable Cloudflare direction: shipping the webdriver shim as
   default tooling, integrating into zen_cli.py, or splitting the daily
   browser from the automation browser (bot-evasion scope, direction).
3. R16 browser restart authority: granting any watch power to restart
   the browser (session restore, owner tabs at stake).
4. R22 PII scan loosening: any allowlist/manual-review class for evidence
   (personal-data handling; default stays conservative).
5. R15 service-manager supervision for the speed-daemon: lifecycle change
   for messaging infrastructure (diagnosis is team work; the move is not).

## Error tracker recount

~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md: 167 numbered
items (A9 B14 C8 D5 E3 G29 H3 I46 J50) + 7 unnumbered F bullets. The
memory figure 121 done / 17 open / 138 total is exact for scope A1-J21
only. Full file: 144 done / 23 open headings (22 work items). R3-L3
evidence: A7/A8 still live (fabrication recurred 25/11), H3 narrowed but
not closed, G28 recurred; J12/J23/E1/E2 superseded-closed.

## Integration log (filled as items land)

All commits on todolist-push, ls-remote verified. Final tip 914ad171.

- R18 pill label unification: aa176f2b (separate worker, landed first).
- Review deliverable + council/redteam files: 2b4259c8.
- R2 + R11 + R12 + R24 (brief template): d78a07c0. brief_check still runs.
- R1 signal hygiene + R10 residue: 27da702d. signal-hygiene.py verdict
  helper + test (6/6 PASS on fake fixtures: completed-task guard,
  deadline suppression, Muse-lane close action); timeout-watch and
  liveness-watch cron bodies updated via cron.update and read back;
  coordinator checklist state-write discipline.
- R5 Tier A: 2ad856d5. 35 regression tests green; checker PASS on the
  real R3-021/072/076/DP-02 snapshots; mutation controls red.
- R9 + R7: 2102887b (1a9bbe3f R9, 2102887b R7). Collect tests ALL PASS;
  first_action suite 98 tests OK (94 pre-existing + 4 new). Note: R9
  duplicate detection FAILs collect on identical non-empty content
  under two names (intended fail-loud; zero-byte exempt).
- R4 + R3: 914ad171. Overlay two-cycle test passes; zen_cli 20 tests,
  zen_dom 52 tests OK. Live two-cycle screenshot test on the laptop
  still owed (owner screen; only when needed).
- R6 tab guardrail: agents-watch cron body (step 6) + laptop machine
  layer (fastest-paths.md lines 110-138); logic test PASS (dry-run
  close list = recorded task tabs only; pinned/essential/owner/active
  kept). Live throwaway-profile test deliberately skipped (focus
  disturbance risk); headless Marionette scratch-profile proof is a
  separate follow-up if wanted.
- R8 machine-layer anomalies: laptop fastest-paths.md (R8 block) +
  keybinds.md golden rules 10-12, corroborated items only, each cited.

Deferred with owners recorded: R13 (batch with R11 follow-up), R14 ops
cleanup (after R6, verify-first), R15 daemon diagnosis (instrument
first), R16 (alert first; restart authority is owner's), R17 Zen folder
tooling (Clone2 artifact exists: improvements/zen-sidebar/, commits
c045bfe4 + 8bc66191; laptop throwaway-profile proof owed before any
integration), R20/R21/R23 (laptop batch / process / experiment).
Owner-decision items: R19, R10 durable direction, R16 restart
authority, R22, R15 service-manager move (section above).
