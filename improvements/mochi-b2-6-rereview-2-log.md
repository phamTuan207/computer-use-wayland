# B2-6 re-review round 2 (narrow): fix round 2, items 1 and 2 only

Reviewer: re-review agent (not the writer of the change). Worktree
~/workspace/mochi-b2-6-work, HEAD fe1d407 (detached). No push, no
live run, no file deleted, no worker file modified. This log is the
reviewer's own artifact, committed by the reviewer itself.

Scope, narrow, exactly as briefed: only 2 items, no re-run of the
suite, no re-review of the whole round. Round 2 changed only
improvements/mochi-b2-6-final-log.md, in 2 commits on base
9e77f0f: b98fa56 (item 1) and fe1d407 (item 2). Prior re-review
dd32265 and redteam round 2 2b25cad already graded the whole of
fix round 1 and left only these 2 items.

Read first: improvements/lauren-tan-workflow-20261122.md, in full,
before any check. Grader never the writer. "Inconclusive" is
honest, not a pass.

## 0. Finish conditions, written BEFORE the scored checks

Task received 00:56 +07, 2026-11-23. Finish conditions written
00:56 +07, 2026-11-23, before scored checks RR2-C1 to RR2-C6
below. (The git log and the two diffs were read for orientation
before this section was written; the scored checks below are the
checks that decide the verdict, and each records its own command,
output, hash, Vietnam time, and elapsed.)

Overall verdict is PASS only if BOTH items pass. If either item
fails or is inconclusive, the verdict is CHUA PASS (or
INCONCLUSIVE) with the specific finding named.

MUC 1 (RR-F1 = RT2-F1) passes only if ALL of these hold:
- RR2-C1: git diff 9e77f0f..fe1d407 -- improvements/
  mochi-b2-6-final-log.md shows exactly 2 hunks, both in the
  final log, and b98fa56 touches only the P1 step 4 verdict
  line (4 insertions, 2 deletions, 1 file).
- RR2-C2: the new step 4 verdict line at HEAD (final log lines
  507-510) states PASS with m0-m4, m6, m7 matched and m5
  recorded with its decider outcome, or FAIL naming the
  mismatched id and its actual value.
- RR2-C3: the new line is compatible with step 3 (final log
  lines 498-503) and with the m5 definition (lines 473-482):
  step 3 stop condition is m0-m4, m6, m7 match, m5 recorded
  verbatim with its decider outcome (stripped: I-1 closed as
  engine-confirmed; kept: template and fakes must be
  corrected). The verdict line must stand under BOTH live
  outcomes for m5: stripped LF gives I-1 closed; kept LF
  gives template and fakes must be corrected. Either outcome
  must yield the PASS branch, never a forced FAIL, and never
  a PASS that contradicts step 3.
- RR2-C4: no other line in P1 (steps 1 to 5, final log lines
  439-518) is changed by round 2 or contradicted by the new
  line. Read the whole of P1 steps 1 to 5 at HEAD.

MUC 2 (RR-N1 = RT2-R-1) passes only if ALL of these hold:
- RR2-C5: fe1d407 touches only the section 5 correction (5
  insertions, 1 file), adding the digest note at final log
  lines 672-676, and the note says: digest 7324498d at adc7ae3
  measured with the 6 native generated files, ignored by git,
  present on disk; a clean checkout without those 6 files
  gives digest 21a7eaf5; git status does not show ignored
  files, so record this precondition with the digest.
- RR2-C6: the note matches the prior independent measurements
  (re-review dd32265 RR-N1 and redteam 2b25cad R-1: 7324498d
  with the 6 files present, 21a7eaf5 in a fresh checkout
  without them, at adc7ae3 / same HEAD), and it contradicts
  no other claim in section 5, in particular the correction
  bullet (final log lines 664-671: fully clean tree, git
  status empty, 5 FAILs, repo 7324498d) and the native
  helpers paragraph (binaries gitignored, git status clean
  after the build).

Light checks only, related to the 2 changed lines: read the
files, grep coordinates, dash scan U+2014/U+2013 = 0 on the
final log and on this log. No suite re-run, no live run.

Expected hashes: base 9e77f0f, item 1 b98fa56, item 2 fe1d407,
HEAD fe1d407970d61dcf94bedd214803bddbbc533b65.

## 1. Checks (command, output, hash, Vietnam time, elapsed)

- RR2-C1, 00:57:05 +07: git diff 9e77f0f..fe1d407 --stat, plus
  git show b98fa56 --stat and git show fe1d407 --stat. Output:
  round 2 total 1 file changed, 9 insertions, 2 deletions,
  exactly 2 hunks, both in improvements/mochi-b2-6-final-log.md.
  b98fa56: 1 file, 4 insertions, 2 deletions. fe1d407: 1 file,
  5 insertions, 0 deletions. HEAD
  fe1d407970d61dcf94bedd214803bddbbc533b65. No other file
  touched by round 2. Elapsed seconds.
- RR2-C2/C3/C4, 00:57:08 +07: read P1 steps 1 to 5 at HEAD
  (final log lines 439-518), raw lines 473-510 quoted in the
  check output. Step 3 (:498-503): stop condition m0-m4, m6,
  m7 match, m5 recorded verbatim with its decider outcome
  (stripped: I-1 closed as engine-confirmed; kept: template
  and fakes must be corrected); any mismatch on m0-m4, m6, m7
  stops the procedure. New step 4 verdict line (:507-510):
  PASS with m0-m4, m6, m7 matched and m5 recorded with its
  decider outcome (stripped: I-1 closed; kept: template and
  fakes must be corrected), or FAIL naming the mismatched id
  and its actual value. Elapsed seconds.
- RR2-C5/C6, 00:57:14 +07: read section 5 lines 640-680 at
  HEAD. Correction bullet (:659-671) unchanged: fully clean
  tree, git status empty, verify still exits 1, git_status_
  clean ok, 5 FAILs, repo 7324498d. New note (:672-676):
  digest 7324498d at adc7ae3 measured while the 6 native
  generated files, ignored by git, were present on disk; a
  clean checkout without those 6 files gives digest 21a7eaf5;
  git status does not show ignored files, so record this
  precondition with the digest. Cross-check: scripts/
  sync-installed.py _source_bundle (:166-200) adds a
  GENERATED_FILES entry only when present on disk, so the
  digest is disk-state sensitive, as RR-N1 said. On-disk
  count now, git ls-files --others --ignored --exclude-
  standard, exactly 6: native/keyboard-protocol.c, native/
  keyboard-protocol.h, native/pointer, native/pointer-
  protocol.c, native/pointer-protocol.h, native/wtype.
  git status --short shows only this untracked log file, so
  the 6 ignored files are invisible to git status, as the
  note says. Elapsed seconds.
- Dash scan, 00:57:26 +07: python3 count of U+2014 and
  U+2013. Final log 0 and 0. This log 0 and 0 (re-run after
  the final append, before commit; see evidence table).
  No suite re-run, no live run, no worker file modified.

Note on method for MUC 2: the two digest values were NOT
re-measured in this round. They rest on two prior
independent measurements that agree exactly: re-review
dd32265 RR-N1 (7324498d with the 6 files present, 21a7eaf5
in a fresh checkout without them) and redteam 2b25cad R-1
(same two digests at adc7ae3, 7324498d reproduced by
copying the 6 files into the fresh checkout). This round
checked that the note quotes those values exactly, that
the count 6 matches the ignored files on disk now, and
that the note contradicts no section 5 claim. That is the
right level for a log-only note whose numbers were already
measured twice independently.

## 2. Findings

- RR2-F1 (MUC 1, RR-F1 = RT2-F1): FIXED. The new step 4
  verdict line matches step 3 exactly in structure and in
  both m5 outcomes. Stripped LF: step 3 says I-1 closed as
  engine-confirmed, step 4 says I-1 closed, under the PASS
  branch. Kept LF: step 3 says template and fakes must be
  corrected, step 4 says the same, under the PASS branch.
  The FAIL branch (naming the mismatched id and its actual
  value) can only name an id from the matched set m0-m4,
  m6, m7, because step 3 gives m5 no match condition and
  step 4 puts both m5 outcomes in the PASS branch. A runner
  following steps 3 and 4 as written now reaches the same
  verdict under either live outcome, which is what RR-F1
  required. The new wording is the exact wording RR-F1
  suggested as the fix.
  Two shorthand differences, recorded as observations, not
  findings: step 4 says "I-1 closed" where step 3 says
  "I-1 closed as engine-confirmed", and step 4 says
  "template and fakes must be corrected" where the m5
  definition (:480-482) says "the template global strip
  and both fakes must be corrected". Neither changes the
  referent or the outcome: step 3 defines the full phrases,
  step 4 is the verdict-line shorthand for the same two
  outcomes, and there is no other template or fake in
  scope. No correction needed.
- RR2-N1 (MUC 2, RR-N1 = RT2-R-1): FIXED. The note quotes
  7324498d and 21a7eaf5 exactly as measured twice before,
  names the precondition (6 native generated files present
  on disk), names the clean-checkout value, and states why
  it matters (git status does not show ignored files). The
  count 6 matches the ignored files on disk now, listed
  under RR2-C5/C6. No contradiction with any other section
  5 claim: the correction bullet says "fully clean tree
  (git status empty)" and git_status_clean ok, which
  concerns tracked and untracked files only; ignored files
  do not affect git status, and the note now says so
  explicitly. The native helpers paragraph (binaries
  gitignored, git status clean after the build) is
  consistent with the same 6 files being present.
- No other P1 line affected: the round 2 diff touches only
  the step 4 verdict line in P1, and only the note in
  section 5. Steps 1, 2, 3, 5 read as before, mutually
  consistent with the new step 4.

## 3. Verdict

PASS. Both narrow items are fixed as written: MUC 1, the P1
step 4 verdict line now stands under both live outcomes for
m5 and matches step 3; MUC 2, the section 5 digest note is
correct, matches the two prior independent measurements,
and contradicts no other section 5 claim. No new finding.
The prior verdicts (re-review dd32265 CHUA PASS on RR-F1,
redteam 2b25cad PHA DUOC on F1) are closed by this round
for these two items. Live confirmation (P1) remains owed
before the fix is quoted as live-proven, exactly as the
final log already states; this PASS is a log-level PASS,
not a live PASS.

## 4. Evidence table (command, output, hash, Vietnam time, elapsed)

- RR2-C1: git diff 9e77f0f..fe1d407 --stat, 00:57:05 +07,
  1 file, 9 insertions, 2 deletions, 2 hunks. HEAD
  fe1d407970d61dcf94bedd214803bddbbc533b65.
- RR2-C2/C3/C4: read final log lines 439-518, 00:57:08
  +07, step 3 :498-503, new step 4 :507-510, both m5
  outcomes under PASS.
- RR2-C5/C6: read final log lines 640-680, 00:57:14 +07,
  note :672-676; git ls-files --others --ignored, exactly
  6 ignored native files on disk; git status shows only
  this untracked log.
- Dash scan: python3 U+2014/U+2013 count, final log 0/0,
  this log 0/0, run before commit (see commit record).
- Elapsed: task received 00:56 +07; finish conditions
  written 00:56 +07; checks 00:57 +07; log written and
  committed 00:58 +07 (see commit record for the exact
  hash and time).

## 5. Commit record

- This log: improvements/mochi-b2-6-rereview-2-log.md, commit
  6d7d5b6077c2e6901db55de68022c688b625ad19 (6d7d5b6),
  committed 2026-11-23 00:57:51 +07. The hash line was filled
  by a follow-up commit on this same file.
- No push by this reviewer. No worker file modified, no
  file deleted, no live run.
