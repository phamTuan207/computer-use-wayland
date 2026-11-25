# R3-L3 Phase 0 prepare: fixture and checker gates (G-39, G-45, G-36, G-47, G-46, G-37)

- Date: 2026-11-25, ~09:00 to ~09:20 +07.
- Worker: Phase 0 prepare worker (fixture and checker gates only).
- Scope: this report covers ONLY the six gates named above. The run was NOT started. No run task was run.
- No em dash or en dash in this file. No personal info in this file.
- Delivery: this file is UNCOMMITTED. The parent commits it.

## G-39. R3-089 fixture refresh: DONE, verified

- Location: laptop `~/rung3/nd09-logs` (via `~/workspace/ssh-laptop.sh` only, never direct ssh).
- Before refresh: log-01..06 dated 2026-11-22 19:20 (still inside 7 days), log-07..12 dated 2026-11-13 19:20. `find -mtime -7` already returned 6, but the refresh was done anyway to reset the clock for the run.
- Refresh done 2026-11-25 08:59:42 +07: `touch -d "1 day ago" log-01..06`, `touch -d "10 days ago" log-07..12`.
- After refresh: log-01..06 mtime 2026-11-24 08:59, log-07..12 mtime 2026-11-15 08:59.
- Verification: `find ~/rung3/nd09-logs -mtime -7` returns exactly 6 files (log-01..06). Count confirmed with `find -mtime -7 -type f | wc -l` = 6.
- Consequence: the 6 recent files stay inside the 7-day window until 2026-12-01 08:59, well past position 49 (R3-089). The hard expiry 2026-11-29 19:20 from the plan is now moot for this run; no mid-run refresh is needed. The merged R3-047/R3-089 watch cron still re-checks before position 49.

## G-45. R3-040-retry-s1 quarantine: DONE (VM and laptop)

Stale R3-L2 evidence found in TWO places, both quarantined by MOVE (kept, not deleted, for audit):

VM (`~/workspace/rung3-snapshots/`, the live R3-L3 snapshot root):
- `R3-040-retry-s1/` (dated 2026-11-23 19:08-19:09: Wayback 429 screenshots, current-nasa.yml, manifest.sha256) and `R3-040-retry-s1.tar.gz` (2026-11-23 19:25, 1,688,679 bytes) moved to `~/workspace/rung3-quarantine-r3l2/`.
- README written at `~/workspace/rung3-quarantine-r3l2/README.md` (DO NOT SCORE notice).
- Verified: `~/workspace/rung3-snapshots/` no longer contains any `retry-s1` entry; the legitimate empty `R3-040-L3/` dir is untouched.

Laptop (`~/rung3-snapshot/`, singular, NOT the snapshot root):
- `R3-040-retry-s1/` AND `R3-040-retry-s2/` (both dated 2026-11-24 02:08-02:09, identical R3-L2 retry evidence) moved to `~/rung3-quarantine-r3l2/` on the laptop. Retry-s2 is the same stale evidence for the same task, so it was quarantined too.
- README written at `~/rung3-quarantine-r3l2/README.md` on the laptop.
- Verified: `~/rung3-snapshot/` now holds only `R3-002-s1`.

OPEN FLAG (not in this gate's scope, for the coordinator): laptop `~/rung3-snapshot/R3-002-s1` is also stale R3-L2 evidence (same `-s1` naming) and is still in place. It is a different task, so it was left alone, but a scorer browsing the laptop snapshot dir could still pick it up. Recommend quarantining it the same way before task 1.

## G-36. Tier A checker verification: DONE, 10/10 PASS

- Checker: ONE driver script covers all Tier A tasks: `rung3-ci/tier-a-check.py` (no separate script per task). It defaults to the frozen key `docs/rung3-answer-keys.json`.
- Frozen key verified before the trial runs: sha256 `5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8`, matches the frozen hash. The key holds Tier A entries for all 10: R3-002 (json-errors), R3-007 (unit-conversion), R3-013 (regex-counts), R3-014 (color-rgb), R3-021 (sql-order-total), R3-072 (image-sizes), R3-076 (report-consistency), R3-082 (calculations), DP-02 (keyword-counts), DP-05 (sql-join).
- Trial snapshots: built in `/tmp/tier-a-trial/` from the FROZEN key values by `/tmp/tier-a-trial-gen.py` (correct evidence per key, so the checker must PASS). R3-076 used the preserved 23/11 trial evidence (4 d42 files, internally consistent).
- Trial-run outputs (all exit 0, verdict PASS, key_hash 5059f6c4, reasons []):
  - R3-002 PASS, R3-007 PASS, R3-013 PASS, R3-014 PASS, R3-021 PASS (2 evidence files incl. ket-qua-truy-van.csv), R3-072 PASS, R3-076 PASS, R3-082 PASS, DP-02 PASS (13 evidence files: bao-cao.txt plus dp02-01..12.txt, recount verified), DP-05 PASS.
- Negative controls (all behave correctly):
  - NEG-R3-002 (one wrong column, 27 to 28): FAIL exit 1, reason `missing JSON error at line 1 col 27`.
  - NEG-R3-082 (one wrong result, 71 to 72): FAIL exit 1, reason `calculation (14 + 6) * 4 - 9: result 72.0, expected 71`.
  - Stale 23/11 trial evidence for R3-007 run against the frozen key: FAIL exit 1, reasons `missing input 12 km`, `8 miles`, `7 kg`, `30 C`, `5 L`. Same holds for R3-013 and R3-082 trial dirs (different sample inputs/expressions than the frozen key).
  - Missing evidence dir: SKIP exit 2, reason `evidence folder missing`.
- Honest note on method: the first attempt at the two mutation controls had a shell bug (the file was truncated before being read, so both controls tested an EMPTY ket-qua.txt instead of a single wrong value). Both still returned FAIL, but for the wrong reason. The controls were rebuilt correctly (read first, then write) and re-run; the FAIL outputs above are from the corrected re-run.
- Finding for the coordinator: the preserved 23/11 trial evidence does NOT match the frozen R3-L3 keys (R3-007 inputs, R3-013 sample text, R3-082 expressions all differ). That is expected (the trial ran before the freeze, and R3-082/R3-013 contents were replaced by FREEZE-2), but it means no scorer may grade from trial memory. The checker rejects that evidence, which is the correct behavior.

## G-47. Backup assignment check: PASS (19 script checks, exit 0)

- Script: `/tmp/g47-backup-check.py` (checks the repo copy `rung3-run-log/du-phong.txt`, the laptop copy `/tmp/du-phong-laptop.txt` fetched by SSH, and the frozen list `docs/rung3-list-100-tasks.md`).
- Results, all PASS:
  - Live table is exactly 5, in fixed order: medium DP-03, DP-06, DP-07; hard DP-02; very hard DP-05.
  - No backup used yet (Cap da dung section reads `(chua co)`).
  - Each backup's difficulty matches the frozen list: DP-02 kho, DP-03 trung binh, DP-05 rat kho, DP-06 trung binh, DP-07 trung binh.
  - DP-01 is NOT in the live table; the retired notice is present (`DP-01 DA NGHI HUU, KHONG DUNG`, `DP-01 khong nam trong bang du phong R3-L3`).
  - DP-04 is absent from du-phong.txt entirely.
  - Repo and laptop backup tables are byte-identical.
  - Simulated assignment: first unused medium is DP-03, first unused hard is DP-02, first unused very hard is DP-05; after DP-03 is consumed the next medium is DP-06; after all 3 mediums are consumed there is no medium backup left (escalate); after DP-02 is consumed there is no hard backup left (escalate).
- NOTE (not a failure, needs a re-sync): the repo and laptop copies differ in ONE line, the tip stamp: repo says tip `ccd83e5`, laptop says tip `d58d3da`. The backup table itself is identical, so the assignment is unaffected, but the file header's claim that the two copies are `giong nhau tung byte` is currently false, and the state file's earlier claim of a byte-identical sync (sha256 3648a7d5) matches neither current copy. Recommend the coordinator re-sync the laptop copy from the repo copy before task 1.
- NOTE (script bug, fixed during the check): the first run of the check script failed 2 checks because its regex only matched single-word difficulties and missed `trung binh` and `rat kho`. The parser was fixed (the data was never wrong) and the re-run passed 19/19.

## G-46. Precondition 6 disposition: PUBLISHED below

All 5 candidates are medium (trung binh). Positions from `rung3-run-log/thu-tu-chay.txt` run order. Basis: frozen key notes (`docs/rung3-answer-keys.md`) plus `du-phong.txt` plus the coordinator state file.

| Task | Pos | Group | Disposition | Evidence / re-check point | Backup if invalid |
|---|---|---|---|---|---|
| R3-011 | 11 | medium | PENDING (leans valid) | timeanddate.com. Curl 403 (Cloudflare) 23/11 19:23, but curl 24/11 06:10 returned 200, and the browser opened the site normally 24/11 14:26 +07; Mochi confirmed loads normally 24/11 17:19 +07. Re-check: at run time, browser blocked after at least 2 attempts at different times plus independent scorer confirmation. | DP-03 if first medium invalid in run order |
| R3-028 | 24 | medium | PENDING (leans valid) | Same shared timeanddate.com cause as R3-011 (see below). Re-check point is the same run-time browser proof. | DP-06 if R3-011 already took DP-03 |
| R3-036 | 27 | medium | PENDING (leans valid) | Same shared timeanddate.com cause. Re-check point is the same run-time browser proof. | DP-07 if DP-03 and DP-06 already taken |
| R3-046 | 33 | medium | PENDING (leans valid) | Same shared timeanddate.com cause. Re-check point is the same run-time browser proof. | NONE if it is the 4th timeanddate invalid (see below) |
| R3-047 | 34 | medium | PENDING (leans invalid) | Project Gutenberg down for maintenance, browser-verified by Mochi 24/11 17:29 +07 (same maintenance as in R3-L2). Re-check: browser check of gutenberg.org right before position 34. If still down, declare INVALID. If back, run normally. | First unused medium at that point (DP-03 if still free, else DP-06, else DP-07) |

Shared-cause ruling (frozen key, R3-011 note): if browser checks prove timeanddate.com is blocked (one shared cause for all 4 tasks), the 4 tasks count as 1 invalid EVENT against both caps (total 5, per group 2). A curl 403 alone is NEVER sufficient proof. Each invalid task still needs its own medium backup; only 3 medium backups exist (DP-03, DP-06, DP-07) for 4 tasks, so a 4th timeanddate invalid leaves the sample with no replacement (per list section 8). The cap question is currently moot because the site loads in the browser; it revives only if the site blocks again at run time.

Group-cap consequence (recorded): at most 2 medium invalids before the run stops. If the shared cause is proven, the 4 timeanddate tasks count as 1 event against the cap, so the cap is not breached by them alone. If no shared cause is proven, invalids count per task: a 3rd medium invalid (from any of these 5, or any other medium task) STOPS the run, and only the owner decides whether to continue. Interaction to watch: R3-047 (position 34) runs AFTER R3-046 (position 33). If the timeanddate block hits first and consumes DP-03, DP-06, DP-07, then a later R3-047 invalid has no medium backup left and leaves the sample. The owner is notified at invalid 3, 4, and 5.

## G-37. Timeout rule verification: FILE CONTRADICTED THE RULE, FIXED (uncommitted)

- Finding: `rung3-run-log/r3-l3-timeout-watch.md` (written 2026-11-24 17:30 +07) stated the OLD rule: a timed-out task is graded from the evidence that exists at the timeout, PASS or FAIL if checkable, FAIL if too incomplete, and `the timeout itself is not a verdict`. That contradicts the resolved rule (re-plan G-37, execution plan sections 2 and 6).
- Fix applied to the file (NOT committed; the parent commits): a resolved-rule header was added at the top, and every old-rule statement was replaced:
  - Deadline note now says partial evidence is kept for the record only and is never graded.
  - Kill procedure step 4: the snapshot is kept for the record only, never graded. Step 5: the manifest gate runs for the record; the gate result does not change the verdict. Step 6: the verdict is FAIL on timeout.
  - The PARTIAL-EVIDENCE RULE section is kept but marked SUPERSEDED, with the old rule quoted and the resolved rule stated in force.
  - The R3-003 watch-list line (`stops and is graded on what exists`) now reads `stops and is FAIL on timeout`.
- Verification after the fix: `grep` for `graded on what exists`, `grade normally`, `graded as-is`, `not a verdict` returns zero hits. The file now states, in its header: over 30 minutes is FAIL, stop, log, never graded from partial evidence; a timed-out task with a failed gate is FAIL (incomplete); a timed-out task with a passed gate is still FAIL on timeout, with the evidence kept for the record.
- Remaining inconsistency in the same file, FLAGGED not fixed (outside G-37 scope, belongs to G-43): kill procedure step 3 still says `pkill -f "codex exec" (or kill the PID recorded at launch)`. Re-plan G-43 requires kills by exact recorded PID only, never pkill -f. The coordinator should fix that line before task 1.
- Worktree note: `git status --porcelain` shows one other modified file I did NOT touch: `improvements/r3-l3-replan-final-20261124.md` (another Phase 0 worker's concurrent edit). My only worktree change is the timeout file plus this report. The parent should commit only the intended paths with explicit pathspecs.

## Open items for the coordinator / parent (before task 1)

1. Commit this report and the timeout-rule fix (explicit pathspec on add and commit, verify `git status --porcelain` first).
2. Re-sync laptop `~/du-phong.txt` from the repo copy (tip stamp `d58d3da` vs `ccd83e5`).
3. Quarantine laptop `~/rung3-snapshot/R3-002-s1` (stale R3-L2 evidence, same hazard class as G-45).
4. Fix the `pkill -f "codex exec"` line in `r3-l3-timeout-watch.md` to exact-PID-only (G-43).
5. G-46 re-checks are live at run time: timeanddate.com browser proof if any of R3-011/028/036/046 blocks, Gutenberg browser check right before position 34.
