# R3-L3 fix-integration review: evidence pack (coordinator working file, 27/11/2026)

Run closed 04:49 27/11, Rule-A 52 PASS / 1 FAIL, bars 50/52 and 51/53 both met.
During the run the rule was record-only (owner 18:18-18:19 26/11). This pack lists
every candidate fix with its evidence pointer. Council ranks by impact (time saved,
errors prevented) and risk. Redteam challenges. Only council+redteam-agreed top items
get integrated, each with a test.

## Candidate fixes

### C1. Heartbeat-log writer lapse
- Evidence: rung3-run-log/r3-l3-heartbeat.log last line 2026-11-27T02:18:50+07:00
  (epoch24 R3-094 drive completed) while coordinators kept working to 04:48.
  Liveness watch fired false positives every 5 min for ~2.5h (heartbeat age reached
  139m). Earlier divergence notes 25/11 (daily-note): "heartbeat log appears stale
  relative to state file"; "if the coordinator is meant to write heartbeats, the
  missing file should be fixed or the watch's signal source redefined to the state file".
- Fix options: (a) coordinator writes heartbeat on every state update; (b) liveness
  watch treats fresh state-file last_updated as liveness. Watch bodies live in
  ~/workspace/goals/zen-i-u-khi-n-c-t-i-a-b-i-agent-v-muse/crons/.

### C2. State-file task_start / runner_pid gap
- Evidence: per-task report R3-078 honest record (26/11 22:20 drive): coordinator
  never recorded task_start/runner_pid; timeout watcher had no PID. Task 56
  (27/11 03:28) runner_pid null blocked the timeout kill for 70+ min. 25/11 near-miss:
  stale task_start would have let a literal watch kill FCC pane PID 22399 (live,
  idle) at 13:56:22; multiple daily-note entries. Also stale codex fields (PID
  302252, 293714) after attempts ended.
- Fix: enforce fresh task_start + runner PID at every task start, both cleared at
  drive end; timeout watch must treat completed task (per-task row exists / drive
  end recorded) as not running. Where: coordinator checklist + state-write helper
  + timeout-watch body.

### C3. Keybind-first hard rule missing from repo brief template
- Evidence: grep keybind/vision/screenshot in
  ~/workspace/computer-use-wayland/docs/brief-template.md = empty (27/11).
  Machine layer fixed 27/11 by independent worker (keybinds.md rule 9 +
  fastest-paths.md line 5): "whatever can be done with a keybind or command, use
  the keybind/command. Limit vision/screenshot use to cross-checks only."
  Owner hard rule 27/11. Repo-side version owed (record-only rule deferred it).
- Fix: add the hard rule to docs/brief-template.md (+ skill references if the
  template points there). Repo text stays generic, no machine specifics.

### C4. Tier A checker bilingual parse
- Evidence: rung3-ci/tier-a-check.py check_json_errors regex
  `dong loi\s+(\d+)\s*,\s*cot loi\s+(\d+)` (line ~97) parses Vietnamese only.
  R3-002 re-run ledger note 25/11: "Tier A checker FAIL (0 positions parsed;
  checker regex expects Vietnamese 'dong loi N, cot loi M', runner wrote English)"
  while values were correct; needed tiebreaker.
- Fix: accept English forms too ("line N, column M", "error at line N col M",
  "line N col M"). One small test with both languages + mutation control.

### C5. Zen folder/tab operations without vision
- Evidence: Task 56 runner slow, vision-heavy, step-by-step clicking; owner
  redirected to drag-drop 04:24 27/11. No API for Zen folders (BiDi does not
  expose them; sidebar is browser chrome). Clone2 researching independently
  (owner order 04:34 27/11, council+redteam+crawler+last30days, build if needed).
- Fix: coordinate with Clone2; integrate only what Clone2 research + laptop
  verification (throwaway profile) proves. Do NOT duplicate.

### C6. Foreign Google Docs window cleanup on ws2
- Evidence: untitled Google Docs window from R3-046 attempt 1 (26/11 ~17:09)
  still on ws2; visible in owner photo 04:22 27/11 ("Tai lieu khong co tieu de").
  Cleanup owed after drives, never mid-drive. Run is closed now.
- Fix: close the window (verify it is the foreign untitled doc first; never close
  owner tabs). Operational cleanup, not code.

### C7. Pill label unification
- Evidence: owner saw "codex via codex" 17:16 26/11; rule re-confirmed 17:41:
  all labels only "Computer use active". Assigned to a separate independent
  worker; overlay code untouched mid-run.
- Fix: DO NOT DUPLICATE. Note status only.

### C8. overlay.py release bug: pill stuck visible
- Evidence: daily-note 25/11 finding: when pill owner is `session`, the last
  release returns visible=false but never sends `hide` to the session indicator;
  pill stays on screen (verified 10:59, 11:01 25/11, again after Codex attempt 1).
  Fail-safe direction (stuck ON) but status lies. Cleared manually 11:03:16.
  No mechanism code changed during run.
- Fix: send hide on final release; test acquire/release cycle ends with pill gone
  (grim verify). Repo: scripts/overlay.py (computer-use-wayland).

### C9. No fail-closed pill gate in BiDi driver path
- Evidence: daily-note 25/11 caveat: zen_dom.py has no overlay hook (unlike
  cdp.mjs); pill proven via MANUAL acquire/release wrapper (G-44). A BiDi worker
  that forgets the wrapper drives with no pill, violating "pill must show on any
  agent control".
- Fix: add overlay acquire/release inside the BiDi session start/stop (fail-closed:
  refuse to drive if pill cannot show), or a lint/gate that rejects unwrapped
  drives. Test: drive without wrapper must fail or auto-wrap.

### C10. Speed-daemon repeated deaths
- Evidence: deaths 26/11 ~09:28, 11:43, 13:26, 15:43, 17:41 (supervisor only),
  ~19:42, ~21:44 (VM replacement); 27/11 before 01:42, ~03:42. Cause unknown.
  Restarts by zen-health watch each time; messaging gaps while down.
- Fix: investigate cause (logs in ~/workspace/speed-daemon/), add self-restart
  robustness or a supervisor that actually supervises. Needs diagnosis first.

### C11. Recurring drive anomalies (machine-layer knowledge gaps)
- Evidence (per-task reports, 5 anomaly blocks + event log):
  - Super-only key refused, recurred 4x (fix: Super+Space launcher).
  - Alt+F4 does not close Kitty/Foot (fix: Ctrl+D / Super+Q).
  - Duplicate stdin redirects kill detached launch, 2x (R3-075, R3-076).
  - Driver launch SSH broken pipe ~36s, recurred (benign, detached runner alive).
  - Colon refused as unsupported XKB in nvim (R3-078).
  - Computer-use session driver exit mid-drive "Unknown process id" (R3-072 area).
  - Dock click opened Bar Folder panel not Files; file picker stuck in /tmp.
- Fix: machine-layer fastest-paths/keybinds additions (laptop only) + brief
  template generic lines where applicable (e.g. single stdin redirect on launch).

### C12. Per-task report file not written early in run
- Evidence: daily-note 25/11: per-task report file zero rows, mtime 09:03:30,
  though R3-001 graded 14:17:58; reporting-chain trigger (b) AND-rule masked it.
  Later in run the file was written (rows to 04:48 27/11).
- Fix: coordinator writes per-task row at grade time (checklist item); or watch
  trigger (b) uses OR with a grace window. Related to C1/C2 signal hygiene.

### C13. Ledger-push watch blocked
- Evidence: hourly runs blocked by execution-risk notice on ~/workspace/r3l3-run-wt
  (validate/cross-check/git steps not run; plain reads only). Last OK 23:48 26/11.
  gh-api fallback rewrite needs owner confirmation (not raised).
- Fix: owner-decision-shaped (changes how ledger pushes run). List for owner.

### C14. Answer-key freshness (R3-004)
- Evidence: daily-note 25/11 error summary: R3-004 key go1.14.3 vs live go1.27.4;
  both scorers accepted on substance.
- Fix: key-refresh check at freeze time for version-sensitive tasks. Process item.

## Sources read for this pack
- rung3-run-log/r3-l3-per-task-reports.log (tail + anomaly blocks)
- rung3-run-log/r3-l3-coordinator-state.json (closure state)
- rung3-run-log/r3-l3-heartbeat.log (tail, last 02:18:50 27/11)
- rung3-run-log/R3-L3-grades.jsonl (60 rows; R3-002 re-run note)
- Master event log extract: /tmp/eventlog-fix-25-27.txt (1410 lines, 25-27/11)
- rung3-ci/tier-a-check.py (regex line ~97)
- docs/brief-template.md (grep empty for keybind/vision)
- Error tracker: ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md
  (905 lines; 121 done / 17 open / 138 total as of 23/11 per memory; recount owed)

## Standing constraints for integration
- Ponytail: smallest complete change, one small test for non-trivial logic.
- NEVER ydotool. No personal info anywhere (deterministic PII check).
- Keybind/command first, vision cross-check only.
- Test like a normal user for user-facing claims.
- Repo commits: explicit pathspec, verify via ls-remote. Machine layer: laptop only.
- Owner-decision items (security, personal data, computer-use direction) listed,
  not decided.
