# Redteam round 2 MOCHI-B2-6: independent break attempt on the close-out fix round

Owner: the owner. Redteam: MOCHI-B2-6 redteam round 2, independent of the worker and of redteam round 1.
Branch: todolist-push. Worktree: ~/workspace/mochi-b2-6-work, HEAD 5611813 (detached).
Target: the 5 close-out fix commits on base 82d2f9a: 8ee4de1 (node whitespace-only token and TAB/FF cases),
afce25e (Python FakeInput url whole-trim branch plus url case), adc7ae3 (Python whitespace-only token and
TAB/FF cases), 25c4253 (manifest verify reporting correction plus line coordinates), 5611813 (P1 eight
inputs, .value step, m2 gate, m5 I-1, m6 NBSP, m7 VT, P2 sketch, soften 3.3, R-2/R-3 notes).
Start: 2026-11-23 00:46 +07 (Asia/Ho_Chi_Minh, task received 00:46:26 +07). All times below are wall-clock +07
unless noted. Standing rules: no em dash (U+2014) or en dash (U+2013) anywhere in this
file, no personal info, never ydotool, no live browser run by this redteam, no file
deleted, no worker file modified, no push. Only this file is created by this redteam.
Commit method: git add -- improvements/mochi-b2-6-redteam-2-log.md then git commit -m,
never git commit -- paths.

Docs read in full before work: improvements/mochi-b2-6-redteam-log.md (round 1, commit 342f1ba),
improvements/mochi-b2-6-council-1-log.md (5923497), improvements/mochi-b2-6-council-2-log.md (82d2f9a),
improvements/mochi-b2-6-council-3-log.md (7ea8190), improvements/lauren-tan-workflow-20261122.md (all),
git diff 82d2f9a HEAD for the 3 changed files, plus first-hand reads of scripts/cdp.mjs lines 575-650,
tests/cdp_snapshot.mjs lines 1-40 and 240-280, tests/test_click3_redteam2.py lines 895-1001, and
improvements/mochi-b2-6-final-log.md section 4 P1 lines 437-515 and section 5. No worker or
council conclusion was used as proof: every attack below was built from the code and the log text
read first-hand in this session.

## 0. Finish conditions (evidence contract, Lauren Tan)

Written BEFORE any check below was run. A confident reply without evidence is a red
flag. "Inconclusive" is honest, not a pass. This redteam does NOT grade its own
attacks: outputs below are facts (commands, outputs, hashes, times); the coordinator
grades the verdict.

| # | Check (command) | Finish condition (expected output) |
| --- | --- | --- |
| RT2-C1 | node tests/cdp_snapshot.mjs (HEAD 5611813) | exit 0, all regressions pass |
| RT2-C2 | cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2; plus the new named test alone | Ran 52 tests, OK; named test alone Ran 1 test, OK |
| RT2-C3 | Discrimination for the NEW pins, in a scratch copy (/tmp/mochi-b2-6-rt2, plain copy, no .git): (a) node FakeInput email branch changed to drop empty tokens, run node suite; (b) node FakeInput email trim changed to SPACE-only, run node suite; (c) Python FakeInput email branch changed to drop empty tokens, run the named Python test; (d) Python FakeInput url branch removed, run the named Python test; then restore each file and re-run. Real worktree untouched. | Each broken fake fails its suite (node exit 1 at the new case, Python FAILED failures=1). Restored files pass (node exit 0, Python OK). git status in the real worktree clean apart from this log file before and after. |
| RT2-C4 | Edge probes in the scratch copy, through BOTH harnesses (node cases appended to a copy of tests/cdp_snapshot.mjs; Python cases through the named test driver shape). Expected values from spec 4.10.5.1.5 as fetched in round 1 plus the template code read first-hand above. | Template and both fakes agree on every probe, or the divergence is named with exact values: email token starting with TAB, email token starting with FF, email token ending in VT (kept, VT 11 is not ASCII whitespace), email token ending in NBSP (kept), url ending in TAB, url ending in FF, url ending in VT (kept), url ending in NBSP (kept), url with inner TAB kept, email token ending in NEL (kept), mid-token LF (both strip, I-1 divergence, still open), url with maxLength refusing. Any template-vs-fake mismatch is a break. |
| RT2-C5 | Manifest verify re-run, twice: (a) at HEAD 5611813 in the real worktree: python3 scripts/bench_manifest.py verify --manifest deploy-manifest.json --repo . (b) at adc7ae3 in a clean temp worktree (git worktree add /tmp/mochi-b2-6-rt2-adc adc7ae3), same command. | (a) exit 1, 6 FAIL categories: source_commit, source_content_sha256, git_status_clean (only this untracked log file), artifact firefox, firefox_bin, geckodriver. (b) exit 1, git_status_clean ok, 5 FAILs remaining: source_commit (manifest d7d569b, repo adc7ae3), source_content_sha256 (manifest 92891523..., repo 7324498d...), artifact firefox, firefox_bin, geckodriver. If (b) differs, the section 5 correction claim is wrong. |
| RT2-C6 | Final-log fact check for the close-out claims: grep -n for multiWsToken :265, multiTabFf :271, new-case block :240-274 in tests/cdp_snapshot.mjs; Python url branch :910-913, url_trim :957-958, multi_ws_token :959-960, multi_tab_ff :961-962, test ends :998, module guard :1001 in tests/test_click3_redteam2.py; python scan for U+2014 and U+2013 in the 3 changed files plus the final log plus this log; git cat-file for 8ee4de1, afce25e, adc7ae3, 25c4253, 5611813, 82d2f9a; file counts tracked (git ls-files) and on-disk separately after clearing __pycache__. | Every coordinate matches or the drift is named exactly; dash counts 0; all hashes exist; counts reported as tracked and on-disk separately. |
| RT2-C7 | P1 wording audit (read-only): read final-log section 4 P1 step 1 through step 5 and check self-consistency: the eight ids listed, the m5 decider wording in step 3, the verdict wording in step 4, the m6/m7 expected values against the spec (NBSP and VT are not ASCII whitespace), the .value step, the m2 gate. | Either every step is mutually consistent, or the exact contradictory lines are quoted with line numbers. |
| RT2-C8 | Template-vs-fake check for the P1 m6/m7 inputs in the scratch copy (same probes as RT2-C4, NBSP and VT token ends, both harnesses). | Both harnesses land the NBSP-kept and VT-kept forms the final log predicts for P1, or the mismatch is named. |

Verdict rule (fixed before running checks): PHA DUOC only if a check shows the fix's
behavior, or a final-log claim, is wrong, with a runnable reproduction (command plus
output). INCONCLUSIVE for any question about real-engine behavior, because no live
browser run is allowed for this redteam; those stay open as gaps in procedure P1.

## 1. Attack plan (built from the code, not from worker or council claims)

A1. Fake pins that pass no matter what. The new node and Python cases pin whitespace-only
tokens and TAB/FF token ends. Attack: break each fake in exactly the way the pin should
catch (drop empty tokens, trim SPACE only, remove the url branch) and confirm the suite
fails. If a broken fake still passes, the pin is fake and the fix commit proves nothing.
A2. The url branch the Python fake just gained. Attack: probe url ends the new branch may
trim wrong (TAB, FF, VT, NBSP, NEL), url with an inner TAB, and url against maxLength, in
both harnesses, and compare template against each fake character by character. The Python
branch trims char codes 9, 10, 12, 13, 32 while the template trims 9, 12, 32 after the
CR/LF strip; the 10/13 entries are dead code after the strip, but any other set difference
is a live divergence.
A3. Token starts, not just token ends. The new pins cover a token ENDING in TAB or FF and
a middle token that is whitespace-only. Attack: tokens STARTING with TAB or FF, where a
one-sided trim bug would hide.
A4. VT and NBSP, the P1 m6/m7 inputs. Attack: probe VT (11) and NBSP (160) token ends in
both harnesses before trusting the P1 expected values. VT is not ASCII whitespace per the
spec (TAB 9, LF 10, FF 12, CR 13, SPACE 32), so both template and fakes must KEEP it; if
either trims it, the P1 expectation is wrong.
A5. Manifest correction claim. The section 5 correction asserts a clean-tree verify at
adc7ae3 exits 1 with git_status_clean ok and 5 FAILs, repo digest 7324498d. Attack:
reproduce it exactly in a clean temp worktree at adc7ae3. A wrong digest or a different
FAIL set breaks the correction that was supposed to fix council 2 and 3 F1.
A6. Close-out coordinates. The final log now cites new line numbers for every close-out
addition. Attack: re-grep every one; a wrong coordinate in the correction round is a
second-order log error.
A7. P1 self-consistency. The new P1 has eight inputs and makes m5 a decider rather than a
gate. Attack: read steps 1-5 against each other and check the verdict line can ever be
true as written.
A8. Wording 3.3. The softened trust-pyramid text now says the two checks are NOT
independent and only P1 catches common-mode error. Attack: check the softened sentence
against what the checks actually prove, and check whether any sentence still overclaims.

## 2. Results

All times +07. Scratch copies under ~/workspace/mochi-b2-6-rt2-scratch (NOT /tmp:
 /tmp is 99 percent full, 11M free, and the first git worktree add there failed with
 "Could not reset index file to revision 'HEAD'"; the scratch dir holds copy/ (plain
 cp -r of scripts, tests, improvements, deploy-manifest.json), adc/ (clean git worktree
 at adc7ae3), and rt2-probe.mjs). Real worktree git status stayed clean apart from 2
 untracked review logs (this file plus improvements/mochi-b2-6-rereview-log.md, written
 by a concurrent reviewer, not by this redteam) through every check. No worker file
 was modified; the only writes outside this log are scratch copies and the adc temp
 worktree, both outside the worktree.

### 2.1 RT2-C1 and RT2-C2: suites pass on HEAD 5611813 (PASS, not a break)

- node tests/cdp_snapshot.mjs, 00:48:18 +07, 1.1s, exit 0: "all cdp snapshot,
  redaction, fill, payload, no_after and scope regressions pass".
- cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2,
  00:48:22 +07, 1.626s: "Ran 52 tests in 1.626s, OK".
- Named test alone, same minute, 0.174s: "Ran 1 test in 0.174s, OK".

### 2.2 RT2-C3: discrimination for the NEW pins, all four legs fail when broken (PASS, not vacuous)

Scratch copy ~/workspace/mochi-b2-6-rt2-scratch/copy, files restored to HEAD copies
after each leg (diff-verified by re-running the suites to green):

- (a) Node fake drops empty tokens (filter token !== '' added to the email branch):
  node exit 1, 00:49:47 +07, first failure at tests/cdp_snapshot.mjs:256:8, the
  multiEmptyToken ok assert, error 'value verification failed'. The new multiWsToken
  case pins the same rule; the first failing assert is the older empty-token case.
- (b) Node fake trims SPACE only (regex replaced by /^ +| +$/g): node exit 1,
  first failure at tests/cdp_snapshot.mjs:238:8, error 'value verification failed'.
  Restored node file: node exit 0.
- (c) Python fake drops empty tokens (filter added to the email branch string):
  named test 0.139s, "Ran 1 test, FAILED (failures=1)".
- (d) Python fake url branch removed (exactly the 4 url-branch lines deleted,
  the "this._value = s;" line kept, verified by grep): named test 0.136s,
  "Ran 1 test, FAILED (failures=1)", failure at the url_trim assert,
  "url whole-value trim failed: {'ok': False, 'error': 'value verification
  failed', 'events': [], 'value': '  https://example.com/a,b  '}". A first
  attempt at this leg removed 5 lines (the _value assignment as well) and also
  failed; it was discarded as imprecise and redone exactly, and the redone run
  above is the one reported. Restored Python file: named test 0.139s, OK.
The new pins are not fake: every broken fake fails its suite, and each restored
file passes.

### 2.3 RT2-C4 and RT2-C8: edge probes, both harnesses (no break; I-1 still open)

Standalone probe ~/workspace/mochi-b2-6-rt2-scratch/rt2-probe.mjs (real template
extracted from the scratch scripts/cdp.mjs exactly as the Python test extracts it,
run through the node FakeInput and the Python FakeInput side by side), 00:50:57 +07,
14 RT2 lines, agree=true on every line:

- rt2_tab_start email TAB + 'a@b.com,c@d.com': both ok true, 'a@b.com,c@d.com'.
- rt2_ff_start email FF + 'a@b.com,c@d.com': both ok true, 'a@b.com,c@d.com'.
- rt2_vt_end email 'a@b.com VT, c@d.com': both ok true, 'a@b.com VT,c@d.com',
  VT kept. This is the P1 m7 input; the harness behavior matches the P1 expected
  value.
- rt2_nbsp_end email 'a@b.com NBSP, c@d.com': both ok true, 'a@b.com NBSP,c@d.com',
  NBSP kept. This is the P1 m6 input; the harness behavior matches the P1 expected
  value.
- rt2_url_tab url TAB ends: both ok true, 'https://example.com'.
- rt2_url_ff url FF ends: both ok true, 'https://example.com'.
- rt2_url_vt url VT ends: both ok true, VT kept at both ends.
- rt2_url_nbsp url NBSP ends: both ok true, NBSP kept at both ends.
- rt2_url_inner_tab url 'https://example.com/a TAB b': both ok true, inner TAB kept.
- rt2_nel_end email 'a@b.com NEL, c@d.com': both ok true, NEL kept.
- rt2_crlf_mid email 'a@b LF .com, c@d.com': both ok true, 'a@b.com,c@d.com'.
  DIVERGENCE FROM THE SPEC LETTER, same as round 1 I-1: the email sanitization
  algorithm has no newline-strip step, so the spec-letter result keeps the LF
  mid-token. The template strips CR/LF globally first and both fakes do the same,
  so no harness case can catch a live engine that follows the spec letter. Still
  open, live-only, verdict inconclusive, not a break. P1 m5 is now the decider
  for it, but see finding F1: the P1 verdict line contradicts the decider.
- rt2_url_maxlen url maxLength 2, '  abc  ': both ok false, 'value exceeds
  maxlength', value ''. The url branch goes through the same maxLength pre-check.
- rt2_tab_only_token email 'a@b.com, TAB ,c@d.com': both ok true, 'a@b.com,,c@d.com'.
- rt2_ff_only_token email 'a@b.com, FF ,c@d.com': both ok true, 'a@b.com,,c@d.com'.
No template-vs-fake mismatch on any probe. The Python url branch trims char codes
9, 10, 12, 13, 32 while the template trims 9, 12, 32 after the CR/LF strip; the
10/13 entries are dead code after the strip, and the probes show no observable
difference, including url VT and NBSP ends where a set difference would have shown.

### 2.4 RT2-C5: manifest verify re-run (correction claim CONFIRMED, with a reproducibility note)

- (a) At HEAD 5611813 in the real worktree, 00:48:26 +07, exit 1, 6 FAILs:
  source_commit (manifest d7d569b, repo 5611813), source_content_sha256 (manifest
  92891523..., repo 7324498d...), git_status_clean (status lists this untracked log
  file and the concurrent rereview log), artifact firefox, firefox_bin, geckodriver.
  Matches the corrected row 11 condition (6 FAIL categories).
- (b) At adc7ae3 in a clean temp worktree, first attempt (fresh checkout, no
  generated files on disk), 00:48:59 +07, exit 1, git_status_clean ok, 5 FAILs, but
  repo source_content_sha256 was 21a7eaf5..., NOT the 7324498d... the final log
  claims. That looked like a break of the section 5 correction. It is not: reading
  scripts/sync-installed.py _source_bundle (lines 166-200) shows the digest is
  computed over git ls-files under MANAGED_DIRS plus GENERATED_FILES (native
  pointer-protocol.c/.h, keyboard-protocol.c/.h, pointer, wtype, and others) IF
  THEY EXIST ON DISK. The fresh checkout lacks those 6 ignored build artifacts,
  which exist in the real worktree. After copying exactly those 6 files from the
  real worktree into the adc worktree (git status still empty, CLEAN), re-run
  00:49:30 +07, exit 1: FAIL source_commit (manifest d7d569b, repo adc7ae3), FAIL
  source_content_sha256 (manifest 92891523..., repo 7324498d...), ok
  git_status_clean (status=''), FAIL artifact firefox, firefox_bin, geckodriver.
  That is byte-for-byte the section 5 correction claim: git_status_clean ok and
  5 FAILs remaining with repo digest 7324498d. The correction in commit 25c4253
  is TRUE. The first-attempt mismatch is recorded honestly here because it matters:
  the digest is disk-state sensitive through ignored generated files, so a verifier
  on a fresh checkout gets 21a7eaf5 and could wrongly conclude the log is wrong.
  The final log says "on a fully clean tree (git status empty)" without mentioning
  that the generated files must be present. See residual R-1.
- Side note: the first git worktree add for (b) failed twice in /tmp ("Could not
  reset index file to revision 'HEAD'", "unable to write file tests/...") because
  /tmp is 99 percent full (11M free). The adc worktree was then created under
  ~/workspace/mochi-b2-6-rt2-scratch/adc instead. No files were deleted to make
  room.

### 2.5 RT2-C6: final-log fact check for the close-out claims (verified)

- tests/cdp_snapshot.mjs: multiWsToken at :265, multiTabFf at :271, last assert of
  the new-case block at :274, const textField at :275, so the block :240-274 is
  exact. The log claim (multiWsToken :265, multiTabFf :271, block :240-274) is
  exact.
- tests/test_click3_redteam2.py: url branch :910-913 (else-if :910, while loops
  :911-912, slice :913), url_trim :957-958, multi_ws_token :959-960, multi_tab_ff
  :961-962, last assert :997-998, module guard at :1001. The log claims
  (:910-913, :957-958, :959-960, :961-962, ends :998, guard :1001) are all exact.
  Seven cases in the named test: multi_spaces, single_comma, multi_maxlen,
  multi_over, url_trim, multi_ws_token, multi_tab_ff. Exact.
- Dash scan (python byte counts): U+2014 0 and U+2013 0 in scripts/cdp.mjs,
  tests/cdp_snapshot.mjs, tests/test_click3_redteam2.py,
  improvements/mochi-b2-6-final-log.md, and this log.
- Hashes exist as commits: 8ee4de1, afce25e, adc7ae3, 25c4253, 5611813, 82d2f9a
  (git cat-file -t, all 'commit').
- File counts, after clearing __pycache__ dirs (gitignored transient, 0 remain):
  tracked 1546 (git ls-files), on-disk 1554 files (find -type f, excluding .git).
  Reconciled exactly: 1546 tracked + 2 untracked (this log, the concurrent
  rereview log) + 6 ignored native build artifacts = 1554. (An initial find count
  of 1648 entries included 94 directories plus the '.' root entry; .gitattributes
  and .gitignore were excluded by the './.git*' pattern, which accounts for the
  remaining 2. The file-only count above is the clean number.)

### 2.6 RT2-C7: P1 wording audit (BREAK, finding F1)

P1 step 1 lists all eight ids (m1 :459, m2 :461, m3 :469, m4 :471, m5 :473, m6 :483,
m7 :487, control m0 :491). The .value step, the m2 explicit gate, and the m6/m7
expected values (NBSP and VT kept, both confirmed in-harness in section 2.3) are
all correct. The break is the verdict line. Step 3 (final log lines 498-501):

  "3. Read pre#result JSON. Stop condition: m0-m4, m6, m7 match the
     expected values above, and m5 is recorded verbatim with its
     decider outcome (stripped: I-1 closed as engine-confirmed;
     kept: template and fakes must be corrected)."

Step 4 (final log lines 506-508):

  "4. Evidence to collect: the probe HTML file, the full JSON output,
     the Chromium version, the time log (+07), and one verdict line
     (PASS with all eight matched, or FAIL naming the mismatched id
     and its actual value)."

Step 3 makes m5 a decider with no match condition: it is recorded verbatim, and
either outcome has a named consequence. Step 4 demands "PASS with all eight
matched". The two cannot both hold, under EITHER live outcome for m5:

- Live strips the LF: step 3 says I-1 closes as engine-confirmed (a good outcome
  for the probe), but m5 does not match its spec-text expected value (LF kept), so
  step 4 says FAIL.
- Live keeps the LF: all eight match, so step 4 says PASS, but step 3 says the
  template and both fakes must be corrected, which is not a PASS outcome for the
  fix.

A runner following the procedure as written must choose between step 3 and step 4;
there is no verdict line that is correct under both steps. This is in commit
5611813, the commit whose stated purpose is to fix P1. See finding F1.

### 2.7 A8: wording 3.3 audit (no overclaim found)

Section 3.3 now reads: "What the two checks prove is template-vs-fake drift",
followed by the correction that the two checks are NOT independent in the sense
that matters, a shared misreading passes both silently, and only the live probe P1
catches a common-mode spec error, with the Blink Multiple() divergence as the
concrete instance and m2 as the case most likely to FAIL live. No sentence in 3.3
still claims the wrong outcome is unexpressible. The softening in 5611813 is
accurate and complete as written.

## 3. Findings

### F1 (BREAK, log, commit 5611813): P1 verdict line contradicts the m5 decider

Coordinates: improvements/mochi-b2-6-final-log.md lines 498-508 (step 3 at :498-501,
step 4 verdict line at :506-508).
Reproduction (read-only, no live run): read lines 498-508 of the final log at HEAD
5611813. Step 3 defines the stop condition as m0-m4, m6, m7 matching, with m5
recorded verbatim as a decider. Step 4 defines the verdict line as "PASS with all
eight matched". Section 2.6 above shows the contradiction holds under both live
outcomes for m5: stripped gives step-3 good outcome with step-4 FAIL; kept gives
step-4 PASS with a step-3 must-correct outcome. The procedure has no executable
verdict condition as written. Fix: rewrite the step 4 verdict line to match step 3,
for example "PASS with m0-m4, m6, m7 matched and m5 recorded with its decider
outcome (stripped: I-1 closed; kept: template and fakes must be corrected), or
FAIL naming the mismatched id and its actual value". No code change is needed for
F1; it is a one-line log correction, but it is in the very commit that claims to
fix P1, so the close-out round does not leave P1 executable as written.

### R-1 (residual, not a break): manifest digest depends on ignored generated files on disk

Coordinates: scripts/sync-installed.py _source_bundle lines 166-200 (GENERATED_FILES
added when present on disk); final log section 5 correction bullet ("at HEAD
adc7ae3, on a fully clean tree (git status empty) ... repo 7324498d...").
Reproduction: fresh worktree at adc7ae3 without the 6 native generated files gives
repo digest 21a7eaf5 (00:48:59 +07, section 2.4); with the 6 files copied from the
real worktree it gives 7324498d (00:49:30 +07), exactly as claimed. The log claim
is true in the worker tree state, but "fully clean tree (git status empty)" does
not state the precondition (the 6 ignored native build artifacts present on disk),
and git status does not show ignored files. A verifier on a fresh checkout will
measure a different digest and may wrongly conclude the log is false. Suggested
note: record that the digest was measured with the generated native files present.
No fix to the manifest or the code is needed.

### I-1 (INCONCLUSIVE, carried from round 1, still open): mid-token CR/LF

Coordinates: scripts/cdp.mjs global CR/LF strip (lines 594-596 in round 1 numbering),
tests/cdp_snapshot.mjs FakeInput, tests/test_click3_redteam2.py Python FakeInput.
Reproduction (scratch probe rt2_crlf_mid, section 2.3): input 'a@b LF .com, c@d.com'
gives 'a@b.com,c@d.com' in both harnesses, while the spec-letter result keeps the
LF mid-token. P1 m5 is now the decider for this, but F1 means the P1 verdict line
cannot be executed as written, so I-1 has no executable closure path until F1 is
fixed. No live browser was run by this redteam, so I-1 stays inconclusive.

### What was checked and found correct (for the record)

The whitespace-only token and TAB/FF pins discriminate in both harnesses (RT2-C3);
the Python url whole-trim branch is correct on every probed url end (TAB, FF, VT,
NBSP, inner TAB) and goes through the maxLength pre-check (RT2-C4); the manifest
correction claim reproduces exactly with the generated files present (RT2-C5); every
close-out line coordinate in the final log is exact (RT2-C6); the 3.3 softening is
accurate (section 2.7); no em dash or en dash in any changed file; all 5 fix
commit hashes exist; file counts reconcile exactly (1546 tracked, 1554 on disk).

## 4. Verdict and recommendations

Verdict: PHA DUOC, at the log level, by finding F1. The code in the 5 fix commits
survived every behavioral attack that could be run without a live browser: the new
pins discriminate, template and both fakes agree on all 14 edge probes, the url
branch is correct, and the manifest correction claim reproduces exactly. But the
close-out round's headline commit 5611813, whose stated purpose is to fix P1,
leaves P1 with a self-contradictory verdict line: step 3 makes m5 a decider with
no match condition, step 4 demands "PASS with all eight matched", and no live
outcome for m5 satisfies both steps. A procedure whose verdict condition cannot
be executed as written is broken as written, and this is the procedure the whole
close-out round depends on for live closure of I-1.

Recommendations for the coordinator (no code changed by this redteam):
1. Fix F1 with a one-line log correction to the step 4 verdict line, matching step 3
   (suggested wording in finding F1), and commit it as its own log-only commit.
2. Add the R-1 note to the section 5 correction: the adc7ae3 digest 7324498d was
   measured with the 6 ignored native generated files present on disk.
3. After F1 is fixed, P1 is executable as written and I-1 can close live through m5.
4. No code change is owed for this round: the pins, the url branch, and the manifest
   reporting all verified.

## 5. Evidence table (command, output, hash, Vietnam time, elapsed)

- RT2-C1: node tests/cdp_snapshot.mjs, HEAD 5611813, 00:48:18 +07, 1.1s,
  exit 0, "all cdp snapshot, redaction, fill, payload, no_after and scope
  regressions pass".
- RT2-C2: cd tests, PYTHONPATH=../scripts:. python3 -m unittest
  test_click3_redteam2, 00:48:22 +07, 1.626s, "Ran 52 tests in 1.626s, OK";
  named test alone 0.174s, "Ran 1 test in 0.174s, OK".
- RT2-C3a: scratch copy, node fake drops empty tokens, 00:49:47 +07, node
  exit 1, first failure tests/cdp_snapshot.mjs:256:8, 'value verification failed'.
- RT2-C3b: scratch copy, node fake trims SPACE only, node exit 1, first failure
  tests/cdp_snapshot.mjs:238:8, 'value verification failed'. Restored node file:
  node exit 0.
- RT2-C3c: scratch copy, Python fake drops empty tokens, named test 0.139s,
  "Ran 1 test, FAILED (failures=1)".
- RT2-C3d: scratch copy, Python fake url branch removed (exactly 4 lines,
  _value assignment kept), named test 0.136s, FAILED (failures=1) at the
  url_trim assert, value '  https://example.com/a,b  '. First imprecise
  attempt (5 lines removed) discarded and redone. Restored file: named test
  0.139s, OK.
- RT2-C4/C8: standalone probe ~/workspace/mochi-b2-6-rt2-scratch/rt2-probe.mjs,
  00:50:57 +07, 14 RT2 lines, agree=true on every line (TAB/FF token starts
  trimmed, VT and NBSP token ends kept, url TAB/FF trimmed, url VT/NBSP kept,
  url inner TAB kept, NEL kept, mid-token LF stripped by both, url maxLength 2
  refuses, TAB-only and FF-only tokens land as empty tokens).
- RT2-C5a: manifest verify at HEAD 5611813, 00:48:26 +07, exit 1, 6 FAILs:
  source_commit, source_content_sha256 (repo 7324498d...), git_status_clean
  (this log plus the concurrent rereview log), artifact firefox, firefox_bin,
  geckodriver.
- RT2-C5b: manifest verify at adc7ae3, clean temp worktree
  ~/workspace/mochi-b2-6-rt2-scratch/adc, fresh checkout 00:48:59 +07, exit 1,
  git_status_clean ok, 5 FAILs, repo digest 21a7eaf5 (fresh checkout lacks the
  6 generated native files); with the 6 files copied from the real worktree,
  00:49:30 +07, exit 1, git_status_clean ok, 5 FAILs, repo digest 7324498d,
  exactly as the final log claims. /tmp worktree adds failed first (99 percent
  full, 11M free); the adc worktree was created under ~/workspace instead.
- RT2-C6: coordinates verified exact (multiWsToken :265, multiTabFf :271,
  block :240-274; Python url :910-913, url_trim :957-958, multi_ws_token
  :959-960, multi_tab_ff :961-962, test ends :998, guard :1001); dash scan
  0/0 in all 5 files; 6 hashes exist as commits; counts tracked 1546 and
  on-disk 1554 files after clearing __pycache__ (1546 + 2 untracked + 6
  ignored, reconciled exactly).
- RT2-C7: P1 audit, final log lines 459-508: eight ids present, .value step,
  m2 gate, m6/m7 expectations correct; step 3 (:498-501) vs step 4 (:506-508)
  contradiction, finding F1.
- Real worktree git status clean apart from 2 untracked review logs at every
  check. No worker file modified, no push, no live run, no file deleted except
  gitignored __pycache__ dirs cleared before counting, per the brief.

Elapsed: task received 00:46:26 +07; docs and diff read by 00:48 +07;
RT2-C1 and RT2-C2 00:48 +07; RT2-C5a 00:48 +07; RT2-C5b 00:48-00:49 +07;
RT2-C3 00:49-00:50 +07; RT2-C4/C8 probe 00:50-00:51 +07; fact checks and log
write 00:51-00:53 +07.

## 6. Commit record (this redteam's own commit, no push)

(TODO: filled after commit.)
