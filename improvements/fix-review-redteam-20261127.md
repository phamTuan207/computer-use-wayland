# R3-L3 post-run fix-integration review: redteam (27/11/2026)

Independent challenge of the coordinator evidence pack (C1-C14) and the three
council reviews. No implementation. Spot checks run 27/11 against live files:
tier-a-check.py, overlay.py, indicator.py, zen_dom.py, brief-template.md,
daemon.log, improvements/fixb-evidence/. Ponytail applies: smallest complete
change, one small test for non-trivial logic, never cut validation or safety.

Note on numbering: each council reviewer numbered new candidates C15+
independently, so numbers collide across reviews. Section 3 reconciles all
candidates by content into one list (R-ids). Council references below name
the reviewer (C1r = council1, C2r = council2, C3r = council3).

## 1. Kill attempts on the council top items

### 1.1 C2 state task_start / runner identity (all councils rank 1-2)
- Verdict: SURVIVES, but the fix as worded in the pack and in C2r Rank 1
  ("record runner PID at every task start") is wrong for the Muse lane.
  C2r's own error E3 and C1r error 8 prove it: Muse-lane runners have a
  session id and no OS PID by design. A helper that demands a PID will
  either block every Muse-lane start or record a fake value.
- Kill attempt on the completed-task guard: if a per-task row is ever
  written early or backfilled (both happened in this run, see C12), a
  guard that treats "row exists" as "not running" can mask a real hang
  and disable the timeout kill exactly when it is needed. The guard
  must require two signals (row exists AND drive-end recorded, or row
  timestamp after task_start) and must be dry-run tested with a fake
  live runner before it may kill or spare anything real.
- Smallest correct fix: state-write helper records task_start plus
  runner identity (PID where one exists, session id otherwise) at start,
  clears both at drive end; timeout watch enforces Muse-lane timeouts
  by closing the subagent, not by PID kill; completed-task guard as
  above. Integrate-now with that revision only.

### 1.2 C1 heartbeat lapse (C1r rank 1, C3r folds into C2)
- Verdict: SURVIVES only as part of the C2 helper. C1r's preferred
  option (b) alone (watch reads state last_updated) does not survive
  C1r's own evidence: error 7 in C1r shows all three signals stale
  after 03:31 27/11 during the Task 56 drive while the coordinator
  was verified alive. Reading a second stale signal still false-alarms.
  C1r rank 8 (threshold shorter than task limit) is the same defect:
  during any silent drive longer than the threshold, every signal
  looks dead.
- Root fix is writer-side cadence: the coordinator (or the C2 helper)
  touches state/heartbeat during long drives, and the watch suppresses
  alerts while a task is inside its deadline with a live runner.
  Watch-side option (b) is a useful second signal, not the fix.
- Integrate-now as one signal-hygiene change with C2 and C12. Do not
  ship option (b) alone and call C1 done.

### 1.3 C3 keybind-first rule in repo brief template (all councils)
- Verdict: SURVIVES. Verified: grep for keybind in
  docs/brief-template.md returns 0 hits. Docs-only, generic wording,
  zero drive risk.
- Kill attempt on C3r's addition (a matching check in brief_check.py):
  briefs are generated per task from the template; a checker that
  greps each generated brief for the sentence adds a failure mode
  (briefs rejected for wording drift) with no proven benefit. The
  template line is the smallest complete change. Reject the checker
  line; integrate the template line only.

### 1.4 C9 fail-closed pill gate in BiDi path (C3r rank 2, C2r rank 4, C1r rank 6)
- Verdict: SURVIVES with a sequencing condition the councils understate.
  Verified: zen_dom.py contains zero overlay/pill references; cdp.mjs
  already implements the fail-closed pattern to copy.
- Kill attempt: fail-closed converts pill flakiness into total drive
  outage. C2r rank 5 documents overlay spawn fragility (30s spawn vs
  15s deadline, killed R3-049 attempt 1). Landing C9 before the spawn
  preflight (configerrors empty before acquire) means the first stale
  config error blocks every BiDi drive with no workaround except
  disabling the gate, which is how gates die. Land the zero-risk
  preflight rule first or in the same batch, and give the refusal a
  clear error message so runners stop instead of retrying blindly.
- Also note: C7 (pill label unification) is owned by a separate worker
  editing overlay label logic. C8 and C9 touch the same file area.
  Coordinate landing order so two workers do not edit overlay.py
  concurrently.

### 1.5 C8 overlay.py final-release hide (C1r rank 5, C3r rank 5, C2r rank 6)
- Verdict: KILLED AS SKETCHED. The evidence is real (verified in
  overlay.py apply_holders, lines 309-321: empty holders plus owner
  session returns visible false with no hide sent). The fix is
  incomplete in a way no council caught.
- The session-owner show path (_show_label, lines 285-307) never sends
  "show". It sends only "label" via session_label, then probes with
  session_live, which itself sends "show" as a side effect. If the
  daemon now sends "hide" on final release, the next acquire depends
  on that probe side effect to re-show. That coupling is fragile: any
  refactor of session_live, or a label call that succeeds while the
  indicator stays hidden, produces the worst lie (status visible true,
  pill invisible, agent driving unseen). That is fail-unsafe, the
  opposite of the current fail-safe stuck-on bug.
- Verified: indicator.py does accept "hide" (serve validates hide/show/
  move/label; request expects "hidden"). So a hide path exists. But the
  safe fix is a pair: send hide on final release AND make the session
  branch of _show_label send "show" explicitly after "label", with a
  two-cycle test (acquire, release, acquire again, pill visible both
  times, gone after second release, screenshot verified). A
  single-cycle test, as all three councils sketch, would pass even
  with the re-show bug latent.
- Integrate-now only with the paired fix and two-cycle test. Otherwise
  defer; a stuck-on pill is safer than an invisible one.

### 1.6 Tier A remaining brittleness (C2r rank 2 as C15, C3r rank 10 as C16)
- Verdict: SURVIVES. Verified in tier-a-check.py: CSV row count uses
  lines minus 1 (header assumed, breaks headerless R3-021 shape);
  image regex requires filename followed by whitespace then size
  (breaks pipe-table R3-072 shape). C4 (bilingual json parse) is
  already fixed, verified lines 97-103 union Vietnamese plus three
  English forms; all councils correctly reject C4 as new work.
- Kill attempt on scope: union-style broadening only grows acceptance,
  so it cannot turn a correct FAIL into a PASS on values, but it can
  accept a wrong-shaped report that happens to contain the right
  numbers. That is acceptable for an aid (the checker is not the
  judge), provided each broadening ships with a mutation control
  (wrong values still FAIL). C2r and C3r both require this; keep it
  as a hard condition.
- Honest sizing: the run is closed. Value is future Tier A tasks only.
  Still cheap and testable in this session. Integrate-now.

### 1.7 Evidence-fabrication gate (C1r rank 7 as C15; absent in pack, C2r, C3r)
- Verdict: DOWNGRADE. The error class is real and was the largest of
  the run. But the proposed fix does not match the proven cause.
  C1r's own evidence shows the collect-evidence gate already existed
  and fired (event log: collect-evidence FAIL, 0 timestamped
  screenshots). Fabrication still reached grading, which means the
  gap was enforcement at sealing, not detection. C3r's tracker review
  states the proven remedy plainly: rules alone did not prevent it;
  lane reassignment did.
- A stricter gate with no named enforcement point (who blocks the
  seal, what happens on FAIL) is more checklist. Integrate only the
  cheap, mechanical parts now: duplicate-file detection and
  missing-screenshot rejection as tests in the collect step, plus the
  runner self-check list already adopted 26/11. Defer any "hard gate"
  claim until the enforcement point is designed and tested with a
  known-bad fixture that must be refused at seal time.

### 1.8 Tab-cleanup guardrail (C1r rank 4 as C16, C2r rank 13 as C21)
- Verdict: SURVIVES. One over-close removed owner pinned and essential
  tabs and created a whole extra counted task (about 73 min). The
  safe method (explicit URL allowlist, batch 1) is already proven in
  the run record, so the fix codifies existing practice rather than
  inventing one. Deny-list plus dry-run list step, tested on a
  throwaway profile. Integrate-now. Note C2r ranks it 13 while C1r
  ranks it 4; redteam sides with C1r on severity (owner data loss
  risk beats frequency), but it is a small change either way.

### 1.9 Cloudflare holder preservation (C3r rank 4 as C15; C1r rank 11 as C17; C2r rank 18 as C26)
- Verdict: DOWNGRADE from C3r rank 4. C3r claims the holder "lives
  only in /tmp on the laptop". Verified false in part:
  improvements/fixb-evidence/holder-fixb.mjs exists in the worktree
  with probe and drive logs beside it. Preservation of the artifact
  is largely done; what remains is landing it as an opt-in helper in
  scripts/ and integrating the preload into zen_cli.py BidiSession
  start (currently untouched, per the 26/11 redteam record).
- Two further problems. First, C2r rank 18 documents a probe
  inconsistency (webdriver true on R3-100 via one path, false via
  another) with unknown cause. Landing an inconsistently probed shim
  as a shipped helper before that is explained risks false confidence.
  Second, expanding bot-detection evasion from brief discipline to
  shipped default tooling is a computer-use direction decision.
  Owner-decision-shaped (see section 5). Defer the landing; integrate
  now only the safe residue C1r names: pin the shim hash in the probe,
  record the probe result in every drive report, dirty probe equals
  stop. Resolve the probe inconsistency read-only first.

### 1.10 Act-now silent fallback (C3r rank 8 as C17; missed by pack, C1r, C2r)
- Verdict: SURVIVES, and redteam ranks it higher than C3r does. It is
  the proven mechanism behind the largest tracker error class (click
  misses from coordinate-space shift, envelope still reads success).
  A silent miss is unrecoverable; a loud refusal is not.
- Kill attempt: failing loud will raise refusal counts until workers
  learn fresh-observe discipline. That is the correct trade, but the
  change touches the act path, so it needs a held-out fixture test
  (stale-observation fixture must refuse, fresh fixture must pass)
  before landing. Integrate-now with that test as a hard condition.

### 1.11 Overlay spawn fragility and holder error swallowing (C2r ranks 5 and 7 as C16, C17)
- Verdict: SURVIVES in part. The preflight rule (configerrors empty
  before acquire, object-form dispatch only) is zero risk and should
  land with C9 (see 1.4). The code fix (non-blocking spawn or timeout
  alignment) addresses a symptom whose root cause (stale Lua config
  error) was already cleared live; changing daemon startup timing
  without a reproduced failure risks masking real indicator failures.
  Defer the code change; integrate the preflight.
- Holder error swallowing: brief rules (never timeout-kill the holder,
  stop via stop file, poll session creation) integrate now. The code
  change (log error, exit non-zero) can break callers that ignore exit
  codes; log first, exit-code change after a caller audit. Defer code.

## 2. Candidates missed or mis-ranked

- Missed by pack and two councils: act-now silent fallback (1.10).
  Only C3r found it. It outranks several items all councils put in
  their top 5, because silent wrong clicks corrupt evidence quality
  for every vision-assisted drive.
- Missed interaction: C8 re-show coupling (1.5). All councils sketch
  the same one-line hide fix; none traced the session show path.
- Mis-ranked high: C3r C15 Cloudflare preservation at rank 4 (1.9).
  Artifact already in the worktree; landing is owner-shaped.
- Mis-ranked high: C1r C15 fabrication gate at rank 7 as a gate (1.7).
  Detection existed; enforcement and lane assignment were the fix.
- Mis-ranked low: tab-cleanup guardrail at C2r rank 13 (1.8). Rare
  but owner-data-loss class; cheap. Belongs in the first batch.
- Zen folder tooling: the parent brief states independent research is
  done and tools are built but unverified on the laptop. This review
  found no folder-tool artifact in the improvements directory to
  verify that claim. Treat as unverified until a throwaway-profile
  laptop test exists (create folder, move tab, restart browser,
  folder persists, owner tabs untouched). Defer; do not integrate on
  the strength of the claim alone.
- C6 is a tab inside the main window, not a separate window (C2r E4,
  verified against coordinator notes). Ops cleanup must target one
  tab with the allowlist method, after the guardrail lands.

## 3. Reconciled candidate list (collisions resolved by content)

R1. Signal hygiene: state-write helper (task_start plus runner identity
    PID-or-session, cleared at drive end), heartbeat/state cadence
    during long drives, timeout-watch completed-task guard (two
    signals), Muse-lane timeout by subagent close, liveness
    suppression inside task deadline. Sources: pack C1, C2, C12;
    C1r ranks 1, 2, 8, 14, 15; C2r ranks 1, 9, 10, 11; C3r ranks 1, 6, 7.
R2. Keybind-first hard rule in repo brief template (docs only).
    Sources: pack C3; all councils.
R3. Fail-closed pill gate in BiDi session start/stop, mirroring
    cdp.mjs, plus spawn preflight rule. Sources: pack C9; C2r rank 5
    step 1.
R4. Overlay session-owner hide on final release PAIRED with explicit
    show in _show_label session branch, two-cycle test. Sources: pack
    C8; redteam revision 1.5.
R5. Tier A checker: regression tests (bilingual json, R3-021 CSV,
    DP-02 detail lines, R3-072 pipe table, R3-076 labels) with
    mutation controls, plus narrow union broadening the tests prove.
    Sources: pack C4 (done part), C2r rank 2, C3r rank 10.
R6. Tab-cleanup guardrail: recorded completed-task tabs only,
    allowlist, dry-run list, pinned/essential never matched.
    Sources: C1r rank 4, C2r rank 13.
R7. Act-now fail-loud on stale/captured observation with window-space
    points, fixture test. Sources: C3r rank 8.
R8. Machine-layer drive anomalies (laptop only): single stdin
    redirect, launcher keybind, terminal close keys, SSH pipe-drop
    expectation, grim default output. Generic brief lines only where
    machine-independent. Sources: pack C11; C1r rank 9; C2r ranks 8, 15;
    C3r rank 9. Unverified items (dock click, file picker) need
    per-task citations before landing.
R9. Evidence collect checks: duplicate-file detection,
    missing-screenshot rejection, timestamp precision tolerance,
    snapshot subdir and manifest handling. Sources: C1r rank 7
    (mechanical part), C2r rank 14.
R10. Cloudflare holder: hash pin in probe, probe result in every
     drive report, dirty probe equals stop; probe inconsistency
     investigation (read-only). Landing as shipped helper deferred
     to owner. Sources: C3r rank 4, C1r rank 11, C2r rank 18.
R11. Holder lifecycle brief rules (stop file, never timeout-kill,
     poll session creation); session-guardian preflight and lane
     procedure table. Sources: C2r rank 7, C1r rank 12.
R12. Fixture and answer-key freshness preflight (absorbs pack C14).
     Sources: C1r rank 13, C2r rank 20, C3r rank 18.
R13. Focus-theft verify line and park-move rule correction,
     Ctrl+Shift+T guard narrowing. Sources: C3r ranks 11, 12, 13.
R14. Ops cleanup: foreign untitled docs tab, leftover window sweep
     (report-only line, close after unsaved-content check). Sources:
     pack C6, C1r ranks 19, 20, C2r rank 16, C3r rank 14.
R15. Speed-daemon diagnosis (instrument exit reason and supervisor
     heartbeat first; 45 starts verified in daemon.log). Sources:
     pack C10; all councils defer.
R16. Browser memory threshold alert and boundary-only restart
     procedure. Sources: C1r rank 18, C2r rank 17, C3r rank 16.
R17. Zen folder operations without vision. Sources: pack C5.
R18. Pill label unification. Sources: pack C7. Owned elsewhere.
R19. Ledger-push watch posture. Sources: pack C13. Owner decision.
R20. Session-store decoder presence on laptop. Sources: C1r rank 22.
R21. Cross-VM verdict channel standardization. Sources: C2r rank 19.
R22. PII scan manual-review class for task-created doc URLs.
     Sources: C2r rank 21. Security-shaped; see section 5.
R23. Marionette/BiDi session hygiene experiment (Arm F). Sources:
     C3r rank 17.
R24. Wrong keybind documentation verification rule (verify against
     live config, never defaults alone). Sources: C1r rank 10.

## 4. Final sets

### Integrate-now (essential, testable in this session)
1. R1 signal hygiene helper plus watch guards, dry-run kill test with
   fake runner and completed-task fixture. Reason: prevents both
   observed kill failures (wrong-kill and unkillable) and the false
   liveness alarms; every future task passes through here.
2. R2 keybind-first template line. Reason: docs only, steers every
   future drive, zero risk.
3. R6 tab-cleanup guardrail, throwaway-profile test. Reason: prevents
   repeat owner-tab loss; proven method, cheap.
4. R5 Tier A tests plus proven narrow broadening, mutation controls.
   Reason: removes tiebreakers and scorer overrides; union-only.
5. R4 overlay hide/show pair, two-cycle screenshot test. Reason: fixes
   lying status without creating an invisible-pill risk. Land before
   or with R3, and coordinate with the R18 label worker.
6. R3 BiDi fail-closed pill gate plus spawn preflight. Reason: makes
   the pill rule structural; preflight prevents gate-induced outage.
7. R7 act-now fail-loud, stale/fresh fixture test. Reason: kills the
   silent-miss class that corrupts evidence.
8. R8 corroborated machine-layer items only (single stdin redirect,
   launcher, terminal close, grim default). Reason: proven recurrences,
   laptop docs only.
9. R9 mechanical collect checks with sealed-fixture tests. Reason:
   cheap detection; no enforcement claim.
10. R10 safe residue (hash pin, probe in report, dirty-probe stop)
    and R11 brief rules, R12 preflight process, R24 verification rule.
    Reason: process and brief text, no drive-path code.

### Defer (real, blocked on diagnosis, proof, sequencing, or owner)
- R10 landing of the Cloudflare holder as shipped helper and any
  durable browser split. Reason: owner direction plus unresolved
  probe inconsistency.
- R15 speed-daemon fix. Reason: cause unknown; instrument first.
  Supervisor under a service manager is a lifecycle change, decide
  after diagnosis.
- R16 browser auto-restart. Reason: restart authority and session
  handling are owner direction; alert and procedure first.
- R17 Zen folder tooling. Reason: no verified artifact found;
  throwaway-profile laptop proof required; owner-tab risk.
- R18 pill label unification. Reason: owned by a separate worker;
  coordinate file landing order with R4/R3.
- R19 ledger-push watch. Reason: owner decision (section 5).
- R14 ops cleanup. Reason: do after R6 lands, verify-first, one tab.
- R20, R21, R23. Reason: laptop tooling batch, process formalization,
  and a bounded experiment respectively; none blocks the batch.
- Overlay spawn code change and holder exit-code change. Reason:
  root cause already cleared live; caller audit owed first.

### Reject (do not integrate as written)
- Pack C4 bilingual parse as new work. Reason: already fixed 25/11,
  verified in code; remainder is R5 tests.
- C3r brief_check enforcement line for R2. Reason: failure mode with
  no proven benefit; template line suffices.
- C1r option (b) as a standalone C1 fix. Reason: second stale signal;
  root fix is writer cadence in R1.
- C1r fabrication "hard gate" as sketched. Reason: detection existed;
  no enforcement point designed. Mechanical parts live in R9.
- Pack C14 as a standalone item. Reason: absorbed by R12 preflight.
- Any supervisor rewrite for the speed-daemon before diagnosis.
  Reason: blind change can mask the cause or double-start.

## 5. Owner-decision-shaped items (team must not decide)

1. R19 ledger-push watch: approving execution of validators in the
   flagged worktree, or moving validation to a clean checkout,
   changes the evidence-chain safety posture. Owner decides.
2. R10 durable Cloudflare direction: shipping the webdriver shim as
   default tooling, integrating it into zen_cli.py, or splitting the
   daily browser from the automation browser. Bot-evasion scope and
   computer-use direction. Owner decides. The safe residue in
   section 4 does not expand scope and may proceed.
3. R16 browser restart authority: granting any watch the power to
   restart the browser (session restore, owner tabs at stake).
   Owner decides.
4. R22 PII scan loosening: any allowlist or manual-review class that
   lets previously held-out evidence into snapshots touches personal
   data handling. Owner decides; default stays conservative.
5. R15 service-manager supervision for the speed-daemon: changing
   lifecycle and restart semantics of messaging infrastructure.
   Diagnosis is team work; the lifecycle move is the owner's call.

## 6. Council errors found (beyond pack errors already catalogued)

1. All councils: C8 fix sketched as a one-line hide with a
   single-cycle test. Misses the re-show coupling in _show_label
   (section 1.5). Highest-severity miss in the set.
2. C3r: Cloudflare holder described as /tmp-only. The holder, probe,
   and drive logs are present in improvements/fixb-evidence/.
   Preservation urgency overstated; rank 4 not sustained.
3. C1r: option (b) ranked as the C1 fix while C1r's own error 7 and
   rank 8 show writer cadence and threshold-vs-deadline are the
   defect. Option (b) alone re-creates the false alarm on the next
   long drive.
4. C2r: Rank 1 text says "record runner PID" while its own E3 proves
   the Muse lane has no PID by design. The rank-1 fix must be
   worded as runner identity plus subagent-close enforcement.
5. C1r: fabrication gate proposed without an enforcement point,
   against its own evidence that the existing gate fired and
   fabrication still passed. Lane reassignment, not detection, was
   the proven remedy.
6. C3r: brief_check enforcement for the keybind rule is
   over-engineering for a template-inherited line.
7. Pack errors confirmed by this review (councils already caught
   them; listed so the record is complete): C4 already fixed;
   C13 intermittent, last OK 02:48 27/11 not 23:48; C10 understated
   (45 daemon starts verified); C6 is a tab not a window; C11
   duplicate-redirect count is 3 not 2; C2 Task 56 null-PID framing
   conflates by-design session identity with a recording failure.

No council claim was found fabricated. The disagreements above are
scope, sequencing, and one missed code interaction (C8).
