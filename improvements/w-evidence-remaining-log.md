# W-EVID log: remaining evidence violations (COORD-CLICK-6, item 13)

- Worker: W-EVID, independent worker for COORD-CLICK-6.
- Task: the remaining part of the 13 evidence violations (clone1 audit
  docs/clone1-evidence-audit-full-20261121.md, commit 581736e, 3 HIGH /
  5 MEDIUM / 5 LOW; independently verified by clone2, commit ebf6ec8,
  all 13 UPHELD; batch 7 record corrections, commit 16c4196).
- Repo: ~/workspace/computer-use-wayland, branch todolist-push.
- Start: git fetch origin + git pull --ff-only, 17:49:32 +07 22/11/2026,
  HEAD already 05140c1, "Already up to date". Work 17:49-18:05 +07.
- Rules kept: full access; no ydotool (never invoked); no long dash in
  anything written here or in the repo files; explicit pathspec commits,
  no bare git commit, no git add -A; tests/realistic/clone1-batch3/
  results.json left untouched (dirty, not mine); no personal info on
  GitHub (one Gmail address found in a recovered file was redacted,
  see section 3); no Zen tab opened or switched (all laptop reads were
  short read-only ssh-laptop.sh commands, 2-3 s each).
- This log does not grade itself. Each section states what was verified,
  what was done, and what is still open, with commands, outputs, commit
  hashes, and times. The commit hash of this log file itself is in the
  W-EVID final report to COORD-CLICK-6 (it was committed together with
  the evidence below).

## 0. What "remaining" means (scope check first)

The three HIGH violations were record-corrected by batch 7, but their
underlying material was still missing (appendix at commit 8bfd83c:
"Nothing further is fixable from this machine for these three HIGHs").
This task's three parts are exactly those remainders:

- (a) H3 acceptance record (V1): only Muse tong may write it.
- (b) V2 logs (14 run/probe logs): only recoverable from the laptop.
- (c) V3 130/130 evidence (V3): not verifiable from the repo.

I also re-checked the other 10 violations at HEAD 05140c1 as a side
observation (section 4). They were NOT in my assigned scope and I did
not fix them; the parent should triage them.

## 1. Part (a): H3 acceptance record (V1) - DRAFT ONLY, NOT WRITTEN

### 1.1 Re-verification at HEAD 05140c1 (17:50-17:51 +07, elapsed 0-1 s per check)

- Command: `git cat-file -t 5a2b69d` -> output: `commit`.
  `git log -1 --format='%H %ci %s' 5a2b69d` -> output:
  `5a2b69da854ae62052cfe31137a4002be4f7c440 2026-11-21 13:49:28 +0000
  Y6c: nested v2 run BLOCKED at launch (F0 --socket/--wayland-fd, F1
  hyprglass ABI dead, U5b wrong log); NO VERDICT, probes + evidence`.
  The proposal exists. What exists is the proposal, not its acceptance.
- Command: `git log --all --oneline -- MEMORY.md` -> output: empty.
  `git ls-tree -r HEAD --name-only | grep -x MEMORY.md` -> output: empty.
  MEMORY.md is on no branch and never in git history. Batch 7 stands.
- The five repo sites still cite only "MEMORY.md 22:57" (grep, 17:50 +07):
  improvements/opt-council-m2-verdict.md:90 (G-10) and :107 (U-1),
  improvements/opt-crawl-src-20261121.md:148 (G8),
  improvements/optimal-fix-method-20261121.md:198,
  improvements/worker-f1-guardian-fix-log.md:862 (pre-batch-7 numbering;
  the batch 7 correction entry is now at line 1207 of that file).
- The batch 7 correction entry is present at
  improvements/worker-f1-guardian-fix-log.md:1207.

### 1.2 New finding: the 22:57 source text survives on this VM (17:51 +07)

- Command: `grep -rn "22:57" ~/memory/` and `grep -rn "H3 gate" ~/memory/`.
  Output: the entry exists in the coordinator daily memory note
  `~/memory/2026-11-21.md`, two places, verified by direct read:
- Line 2917, entry "(2026-11-21 22:57, Y13r2 BLOCK + re.py ROOT CAUSE
  SOLVED)", last sentence verbatim: "H3 gate: chap nhan de xuat Y13r2
  (5a2b69d NO VERDICT + kiem tra runner-quiet/ports moi duoc tinh la
  xong marker leg cho run nay, giu nguyen text gate, Y6 retry sau Y13)."
- Line 2653, section "### Quyet dinh H3 gate (Muse, sau de xuat Y13r2)":
  "Chap nhan de xuat cua Y13r2: ban ghi 5a2b69d NO VERDICT cong kiem tra
  moi runner-quiet/ports duoc tinh la xong marker leg cho run Y13 nay,
  giu nguyen van ban gate, Y6 retry xep sau Y13. Khong chap nhan Y6e
  load test lam tin hieu hoan thanh."
- `~/MEMORY.md` itself has no 22:57 H3 entry (grep "22:57" there returns
  only the 02:01 watchdog note about the audit). The entry lives in the
  daily note, not in the curated file.
- Consequence: the acceptance decision is recoverable as TEXT, but it is
  still not a repo record. The acceptor in the source is Muse (the
  coordinator), deciding after Y13r2's proposal. No owner message in
  the repo or in the memory log accepts H3 specifically. the owner said
  "Ok thoi may dua tu lam di nhe" after the Y13r2 report (same daily
  note, section "dang chot tu lam"); that is a general overnight
  go-ahead, not an H3 acceptance, and the draft says so.

### 1.3 What was done

- Prepared `improvements/w-evidence-h3-draft.md`: a DRAFT PROPOSAL with
  the located source quotes, the verified facts, the proposed exact
  wording for the record, what the record must NOT claim, and where it
  should go. The file is headed DRAFT, NOT A RECORD.
- Appended a dated W-EVID entry to
  improvements/worker-f1-guardian-fix-log.md (below the batch 7 entry)
  recording that the source text was located at
  memory/2026-11-21.md:2653 and :2917 and pointing to the draft. No
  existing line was changed. This append is evidence for the draft,
  not the acceptance record itself.
- Did NOT write the acceptance record. That is for Muse tong alone.

### 1.4 What is still needed

- Muse tong confirms the acceptor was Muse itself (not the owner, not
  a council vote), then copies the proposed wording into a council paper
  or log entry in the repo (per AM-13). Until then the H3 gate stays
  UNVERIFIED from repo evidence, even though the source text is now
  located.

## 2. Part (b): V2, the 14 F3 arm logs - NOT RECOVERABLE

### 2.1 Re-verification at HEAD 05140c1 (17:51 +07)

- The F3B log STEP 4/5 verdicts are present with inline session IDs:
  Arm A PASS session 0979bcf5, Arm B PASS 29183d85, Arm D PASS 2d3cd2de,
  Arm E FAIL wedge reproduced 6304b1d8
  (improvements/worker-f3b-restart-log.md, lines 64-85).
- Command: `grep -c "0979bcf5\|29183d85\|2d3cd2de\|6304b1d8"
  improvements/f3-evidence/full.log
  improvements/f3-evidence/result_full.json` -> output: 0 and 0.
  The full.log/result_full.json corroborate nothing about the arms.
- `improvements/f3-evidence/` holds exactly the same 14 files as at
  batch 7 (4 arm .py scripts, 2 bidi-tabs JSONs, cleanup_full.py,
  close3.py, full.log, parse_sessionstore.py, probe_session.py,
  rclick.py, result_full.json, verify_list.py). No run log.
- The batch 7 correction entry is present at
  improvements/worker-f3b-restart-log.md:130.

### 2.2 Laptop search (read-only ssh-laptop.sh, short commands, no Zen touch)

All times +07 22/11/2026. Each SSH call ran 2-3 s, well under the ~30 s
SSH death window. No tab was opened, switched, or clicked. No file was
written or deleted on the laptop.

- 17:51:27-17:51:29, elapsed 2 s. Command: list the laptop
  `~/workspace/computer-use-wayland/improvements/f3-evidence/` and
  `/tmp/arm_* /tmp/probe_* /tmp/relaunch*`. Output: the laptop
  f3-evidence/ has exactly the same 14 files as the repo, no run logs;
  /tmp has no arm_*/probe_*/relaunch* files.
- 17:51:34-17:51:37, elapsed 3 s. Command: `find ~/workspace /tmp
  -maxdepth 4` for the 14 exact names (arm_a_run2.log, probe_a2.log,
  arm_b_run.log, probe_b.log, probe_c.log, arm_d_run.log, probe_d.log,
  arm_d_run2.log, probe_d2.log, arm_e_run.log, probe_e.log, probe_f.log,
  probe_r3.log, relaunch-f3b.log). Output: no matches.
- 17:51:46-17:51:49, elapsed 3 s. Command: `find ~/workspace -maxdepth 6`
  for arm_*run*.log / probe_*.log / relaunch-f3b.log, plus `find
  ~/workspace /tmp -maxdepth 5` for the V3 names, plus `ls -d /tmp/judge`.
  Output: no V2 matches; no V3 matches; /tmp/judge does not exist.
- 17:52:00-17:52:02, elapsed 2 s. Command: `ls ~`, `find ~
  -maxdepth 2 -type d -name "*computer-use*"` (output truncated by the
  local head limit; the needed follow-ups were re-run below). The laptop
  holds many computer-use-wayland copies, so a bounded sweep of them
  was run next.
- 17:52:11-17:52:13, elapsed 3 s. Command: `find ~/workspace -maxdepth 4
  -name "*.log" -newermt "2026-11-21 23:29" ! -newermt "2026-11-21
  23:50"` (the F3B arm window, 23:29-23:50 21/11) plus laptop repo
  status. Output: no *.log file modified in that window under
  ~/workspace; laptop repo is todolist-push at 48c6aee (behind this VM's
  05140c1) with unrelated dirty/untracked files (left untouched).
- 17:52:19-17:52:22, elapsed 3 s. Command: `find ~/computer-use-wayland
  ~/computer-use-wayland-* ~/Work -maxdepth 4` for the V2 and V3 names.
  Output: no matches (SWEEP-DONE, zero paths).
- 17:52:47-17:52:49, elapsed 2 s. Command: `find ~ -maxdepth 2` for the
  V2 names (covers the remote-shell default cwd) plus `ls -d
  /tmp/opencode /tmp/opencode/multipage-l3` and `ls /tmp`. Output: no V2
  matches at home top level; /tmp/opencode exists but multipage-l3 does
  not.
- Same checks on this VM: `find ~/workspace /tmp -maxdepth 5` for
  arm_a_run2.log / probe_r3.log / relaunch-f3b.log -> no matches.

### 2.3 Conclusion for V2: NOT RECOVERABLE, re-run is the only path

- The 14 logs existed on the laptop at verdict time (23:35-23:44 21/11,
  the F3B log quotes session IDs from them) and are gone by 17:51 +07
  22/11. They are in no repo branch, no git history, no laptop copy
  searched, and no /tmp on either machine.
- Likely cause (inference, not verified): the laptop disk cleanup today
  (COORD-CLICK-6 log: disk cleaned, 17G free) and/or /tmp wipes removed
  them. The F3B log itself notes the runs were launched detached with
  relative log paths, so the files lived wherever the remote shell cwd
  was; every plausible cwd was searched.
- Appended a dated W-EVID entry to
  improvements/worker-f3b-restart-log.md (below the batch 7 entry)
  recording this failed retrieval with commands and times. No existing
  line was changed.
- What is needed for a full fix: a re-run of arms A-E with logs committed
  (the batch 7 alternative). That needs a live Zen slot while the owner
  is away from the machine; it was NOT done here (the user is using the
  machine now, and this task forbids Zen interaction).
- Status after this work: the arm verdicts still rest on the inline
  summary in the F3B log only. Unchanged, but now with the laptop
  retrieval attempt closed instead of open.

## 3. Part (c): V3, the 130/130 judge evidence - PARTIALLY RECOVERED

### 3.1 Re-verification at HEAD 05140c1 (17:52 +07, elapsed 7 s)

- Command: `git log --all --oneline --` for test-scores.md, test-cases.md,
  typing-fix-multipage-report.md, test-execution-report.md, stress.log,
  finish-record.json, start-readiness.json -> output: 0 commits each.
  None was ever in git history on any branch. Batch 7 stands.
- The verdict at improvements/live-test-log.md:991 and the batch 7
  correction entry at line 4231 are both present as written.
- scripts/plans/tc02-v1.json:9 holds expected_sha256
  8da1f5624c1b482bcdfae9d7c6883fdc52313dbe4120c2d1df2623ec5bcb9772.
  That corroborates the sentence hash, not the per-case scores.

### 3.2 New finding: 4 of the 5 report files survive on this VM (17:52-17:54 +07)

- Command: `find ~/workspace /tmp -maxdepth 4 -name "test-scores.md"`.
  Output: `/home/hatch/workspace/omarchy-tasks/cu-fix-20261114/improvements/test-scores.md`.
  That directory (NOT a git repository, checked 17:52 +07) holds:
  test-cases.md, test-scores.md, typing-fix-multipage-report.md,
  test-execution-report.md, plus tc02-evidence/ (19 files).
- Match checks against the judge's own description in live-test-log.md:
  test-scores.md is exactly 174 lines (judge: "rewritten, 174 lines");
  typing-fix-multipage-report.md is exactly 306 lines (judge: "Worker N,
  306 lines"); test-cases.md holds Test #1 to Test #13 (lines 57-514),
  in the same order as the scores table; the judge's run dir was the
  laptop /tmp/opencode/multipage-l3/, which is gone from the laptop
  (checked 17:52 +07, /tmp/opencode exists but multipage-l3 does not),
  so this VM mirror is the surviving copy.
- Recomputed from the recovered test-scores.md (17:54 +07): the per-case
  table has 13 rows, each 10 points; awk sum = 130. Exact.
  The tc02 row cites SHA 8da1f562... (3/3 trials byte-exact 50/50),
  matching scripts/plans/tc02-v1.json:9.
- The tc02-evidence/ dir is NOT judge evidence. Proof (17:54 +07):
  tc02/output/on-tap.txt hashes to b10ffde1... (the 45-byte failure
  file); byte-exact-read-back.json records exact_byte_match false,
  45 actual bytes vs 50 expected, checked 01:20:48 +07 17/11; the
  finish-record.json there has session generation b601278a... and owner
  tc02-overnight-fix-20261116-0105, while the judge's passing tc02
  trials have generations 320f5b16..., 7b514cc4..., 85adf101....
  Broker generation 7bcc844b matches in both runs (same broker), so it
  does not identify the run. tc02-evidence/ is the prior overnight-fix
  run mirror cited by test-execution-report.md; it corroborates the
  BASELINE (tc02 0/10 FAIL, total 0/130), not the pass. It is committed
  with that label, not as judge evidence.
- Still missing after the search: stress.log (0 hits in the source tree,
  0 on the laptop, 0 in git history); the 14 judge state.json files
  (0 in the source tree, 0 on the laptop, 0 in git history); the
  judge's tc02 finish-record.json and start-readiness.json for the
  passing L3 trials (the pair in tc02-evidence/ belongs to the prior
  run, see above); the 20 screenshots (no /tmp/judge on either machine;
  none of the 20 filenames cited in test-scores.md exists under the
  source tree, checked by basename; the 182 PNG files under the source
  tree are other images with different names).

### 3.3 What was done

- Copied the 4 report files and the tc02-evidence/ dir into the repo at
  improvements/v3-judge-evidence-20261117/ (cp, 17:54:39 +07).
- Verified byte-identical copies (17:54:39 +07): sha256sum match for
  test-cases.md, test-scores.md, test-execution-report.md; `diff -r`
  clean for tc02-evidence/ (19 files).
  Note: commit 69287aa holds 12 of the 19 tc02-evidence files; the 7
  PNG screenshots were left out by the repo .gitignore `*.png` rule and
  were committed in a follow-up commit with `git add -f` (the repo
  already tracks 45 PNG files, and the test-execution-report describes
  this mirror as including "7 key screenshots").
  Full hashes: test-cases.md
  21845505fc215cde026f1b7aec04a7c098e4ef1063392e262d1aaf947e4ef886;
  test-scores.md
  038650a2b2acd131fd8c50d2313f8308e3a6d2e7bc5a7a13074ed57907a9b237;
  test-execution-report.md
  ba6efca108e1623009fd555c127117a01ebbab8ef628e106393a6da0f8a0ab7f;
  typing-fix-multipage-report.md original
  eb34532319120f9fe0e7b4992a25489e5fe58a914fcde9a584d44f92ddf54fa7,
  committed copy (after redaction)
  54b0b84e63d3da58fdc33039055d4e31483db906fe96c50f516d49cb53632264.
- Redaction (17:54:42 +07): typing-fix-multipage-report.md:90 in the
  source contains the owner's personal Gmail address in the commit
  author line. It was replaced in the committed copy with the public
  noreply address already used in git history
  (phamTuan207). `diff` between
  source and committed copy shows only line 90. The address value is
  not written in this log or in the README.
- Wrote improvements/v3-judge-evidence-20261117/README.md with full
  provenance, the redaction record, the tc02-evidence warning, and the
  still-missing list.
- Appended a dated W-EVID recovery entry to improvements/live-test-log.md
  (below the batch 7 entry at line 4231), updating V3 from UNVERIFIABLE
  to PARTIALLY VERIFIABLE with the recovered and still-missing lists.
  No existing line was changed.

### 3.4 Corrected status of V3

- Before: UNVERIFIABLE from repo evidence (batch 7).
- Now: PARTIALLY VERIFIABLE. The verdict document itself
  (test-scores.md, 174 lines) is in-repo, its table recomputes to
  exactly 130, its case list matches test-cases.md #1-#13 in order,
  and its tc02 SHA matches scripts/plans/tc02-v1.json:9. What is still
  unverifiable from the repo is the raw per-trial evidence behind each
  per-case score: the 14 state.json files, stress.log, and the 20
  screenshots.
- Full fix still needs: those raw files from wherever they survive, or
  a re-run of the judge with evidence committed. No re-run was done here.

## 4. Side observations: V4-V13 status at HEAD 05140c1 (OUT OF SCOPE, for triage)

Checked 17:50-17:51 +07 while establishing scope. These were not assigned
to W-EVID and were not fixed here. The parent said most were handled;
the checks below say several still read as open. The parent decides
whether they need a follow-up worker.

- V4 (MEDIUM, det-finish logs): still local-only. `git ls-tree -r HEAD`
  shows only improvements/det-finish-implementation.md, no
  /tmp/det-finish-*.log files in the repo.
- V5 (MEDIUM, run_matrix.py total 17): STILL OPEN. Line 147 still
  `total = 17`; cases/ still holds 16 dirs (T01-T10, T11a, T11b, T13,
  T14, T15, T16), no T12. Checked 17:50:20 +07.
- V6 (MEDIUM, a1_unblind.py B3a): STILL OPEN as written. The line-226
  `code_wall_med = median(code_walls)` sits inside the
  `if len(code_thinks) == 3 and len(step_gaps) == 3:` branch with no
  guard on code_walls, and the UNMEASURED check above it only appends
  to inconclusive without returning early. Code reading only, no
  execution (same method as the audit).
- V7 (MEDIUM, Y12 logs): still local-only. No y12 run logs in the repo
  tree (only improvements/worker-y12-batch3-verify-log.md).
- V8 (MEDIUM, PR1 JSON): still local-only. No pr1-verify result file in
  the repo tree (only improvements/worker-pr1-verify-log.md).
- V9 (LOW-MEDIUM, worker-x 9/10 vs 9/20): STILL OPEN as written.
  improvements/worker-x-remaining-items-log.md:11 still says "Final full
  run 9/10 in 59,111 ms". No correction for the misquote was found in
  that file (grep, 17:50:32 +07).
- V10 (LOW, restage diff split): STILL OPEN as written.
  improvements/worker-y14b-restage-log.md:14 still says "(+240/-37,
  ...)" (the correct split is +213/-27 for check.mjs, +87/+10 for
  README.md, per the audit). No correction for the split was found.
- V11 (LOW, Y13g R2 ships/results): still local-only as the audit said
  (harnesses are committed under improvements/y13g-r2-verify/, staged
  ships and results are not in the repo).
- V12 (LOW-MEDIUM, commit 700144a): CHANGED since the audit. `git
  cat-file -t 700144a` now returns `commit`: 700144a83d8ced1e20195fe4ba5085e2f2989bb2,
  2026-11-17 16:47:40 +0000, "step3 prep: durable stream, safe trims,
  P0 probe (NOT deployed, NOT run)". It is the tip of a LOCAL branch
  step3-stream-prep on this VM; `git branch -r --contains 700144a`
  returns nothing and `git ls-remote origin` shows no step3 branch.
  So the object is now resolvable locally, but the branch is still
  unpublished. Partially resolved, not fully.
- V13 (LOW, speed swarm /tmp sources): still disclosed and labeled
  PROVISIONAL (improvements/speed-swarm-report.md:5, :13, :15). No fix
  needed by design; the disclosure stands.

## 5. Files delivered by W-EVID (commits and verification)

- Commit 1 (V3 recovery): improvements/v3-judge-evidence-20261117/
  (test-cases.md, test-scores.md, typing-fix-multipage-report.md
  redacted line 90, test-execution-report.md, tc02-evidence/ 12 files,
  README.md) plus the dated recovery append to
  improvements/live-test-log.md. Commit 69287aa.
- Commit 2 (V3 completion): the 7 tc02-evidence screenshots
  (git add -f, .gitignore override) plus the README.md note about them.
  Commit 7f30886. The V3 directory is now complete: 19 tc02-evidence
  files + 4 reports + README.
- Commit 3 (worker record): improvements/w-evidence-remaining-log.md
  (this file), improvements/w-evidence-h3-draft.md, plus the dated
  appends to improvements/worker-f3b-restart-log.md and
  improvements/worker-f1-guardian-fix-log.md. Commit hash: see the
  W-EVID final report.
- Both commits pushed immediately after creation; verified with
  `git ls-remote` (see the final report).
- NOT committed: tests/realistic/clone1-batch3/results.json (dirty,
  not mine). No other files were touched: `git status --short` before
  committing showed only the new W-EVID files plus the pre-existing
  dirty results.json and unrelated untracked files.

## 6. Handover summary (one line per remaining violation)

- V1/H3: record NOT written by W-EVID. Source text located
  (memory/2026-11-21.md:2653, :2917); draft prepared at
  improvements/w-evidence-h3-draft.md. Needs Muse tong to confirm the
  acceptor (Muse itself) and write the record.
- V2: NOT recoverable. 14 logs searched on the laptop (6 SSH calls,
  17:51-17:53 +07) and on this VM: zero hits. Needs a re-run of arms
  A-E with logs committed (live Zen slot, owner away).
- V3: PARTIALLY recovered. 4 of 5 report files now in-repo at
  improvements/v3-judge-evidence-20261117/ (test-scores.md recomputed
  130 exact). Still missing: stress.log, 14 state.json, the judge's
  tc02 finish/start JSONs, 20 screenshots. Needs those files or a
  judge re-run with evidence committed.
