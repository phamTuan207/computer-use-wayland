# Redteam MOCHI-B2-6: independent break attempt on the email multiple per-token trim fix

Owner: the owner. Redteam: MOCHI-B2-6 redteam, independent of the worker.
Branch: todolist-push. Worktree: ~/workspace/mochi-b2-6-work, HEAD 5ee043d (detached).
Target: the fix in 3 commits (3532bfd scripts/cdp.mjs, e500923 tests/cdp_snapshot.mjs,
d88a472 tests/test_click3_redteam2.py) and the final log improvements/mochi-b2-6-final-log.md
(607 lines, commit b0876ca). Base for the diff: 0400e86.
Start: 2026-11-23 00:24 +07 (Asia/Ho_Chi_Minh, task received 00:24:43 +07). All times below are wall-clock +07
unless noted. Standing rules: no em dash (U+2014) or en dash (U+2013) anywhere in this
file, no personal info, never ydotool, no live browser run by this redteam, no file
deleted, no worker file modified, no push. Only this file is created by this redteam.
Commit method: git add -- improvements/mochi-b2-6-redteam-log.md then git commit -m,
never git commit -- paths.

Docs read in full before work: improvements/lauren-tan-workflow-20261122.md (all),
improvements/mochi-b2-6-final-log.md (all, 607 lines), git diff 0400e86 HEAD for the
3 fix files, plus first-hand reads of scripts/cdp.mjs lines 540-670, tests/cdp_snapshot.mjs
lines 1-120 and 231-265, tests/test_click3_redteam2.py lines 700-976. No worker or
council conclusion was used: every attack below was built from the code and the spec
text fetched fresh in this session.

Spec source (fetched fresh by this redteam, not taken from the worker):
https://html.spec.whatwg.org/multipage/input.html, crawled 2026-11-22 17:26 UTC.
Email state 4.10.5.1.5, value sanitization algorithm (lines 1355-1368 of the fetched
text): split on commas the element's value, strip leading and trailing ASCII whitespace
from each resulting token, if any, and let the element's values be the (possibly empty)
resulting list of (possibly empty) tokens, maintaining the original order; set the
element's value to the concatenation of the values separated by a single U+002C COMMA.
The algorithm has no newline-strip step and no empty-token removal step. The multiple
change steps (same section, lines 1335-1349) are a separate user-change algorithm that
strips each value and rejoins, consistent with sanitization. The value IDL setter
(lines 4936-4956) sets the value, sets the dirty value flag, then invokes the
sanitization algorithm: it has no maxLength step and no newline step. The maxLength rule
(lines 3663-3664) constrains only the length of the value of the element's value
content attribute, not a script set through the value IDL attribute.

## 0. Finish conditions (evidence contract, Lauren Tan)

Written BEFORE any check below was run. A confident reply without evidence is a red
flag. "Inconclusive" is honest, not a pass. This redteam does NOT grade its own
attacks: outputs below are facts (commands, outputs, hashes, times); the coordinator
grades the verdict.

| # | Check (command) | Finish condition (expected output) |
| --- | --- | --- |
| R-C1 | node tests/cdp_snapshot.mjs (HEAD 5ee043d) | exit 0, all regressions pass |
| R-C2 | cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2; plus the new named test alone | Ran 52 tests, OK; named test alone Ran 1 test, OK |
| R-C3 | Discrimination in a scratch copy (/tmp/mochi-b2-6-rt): replace scripts/cdp.mjs with the 0400e86 version, run node tests/cdp_snapshot.mjs and the new Python test; then restore the HEAD version and re-run both. Real worktree untouched. | Old template: node exit 1, first failure at the multiEmail ok assert; Python new test FAILED (failures=1). Restored template: node exit 0, Python new test OK. git status in the real worktree clean before and after. |
| R-C4 | Edge probes in the scratch copy, through BOTH harnesses (node cases appended to a copy of tests/cdp_snapshot.mjs; Python cases through the new test's driver shape). Expected values from spec 4.10.5.1.5 as fetched above. | NBSP token ends kept, VT kept, FF trimmed, CR/LF at token ends trimmed, only-commas ',,,' preserved, only-whitespace '   ' lands '', whitespace-commas ' , , ' lands ',,', 9000-char email token ok true, url '  https://example.com/a,b  ' lands 'https://example.com/a,b'. Mid-token newline 'a@b\n.com, c@d.com': template and fake give 'a@b.com,c@d.com' while the spec letter gives 'a@b\n.com,c@d.com', recorded as a divergence, verdict inconclusive pending a live engine check. Python driver url case expected to FAIL, proving the Python FakeInput has no url branch. |
| R-C5 | Final-log fact check: grep -n line numbers for the 3 fix files; python scan for U+2014 and U+2013 in the 3 files; git show 0400e86 grep for multiple; git cat-file for 3532bfd, e500923, d88a472, b0876ca, 5ee043d; file counts tracked (git ls-files) and on-disk separately after clearing __pycache__. | Line numbers match the log within a few lines or the drift is named exactly; dash counts 0; R8 grep result matches the log; all hashes exist; counts reported as tracked and on-disk separately. |
| R-C6 | Spec re-verification (this session, browser fetch above). | Email sanitization text, value setter steps, and maxLength scope as quoted in the spec paragraph above. |

Verdict rule (fixed before running checks): PHA DUOC only if a check shows the fix's
behavior, or a final-log claim, is wrong, with a runnable reproduction (command plus
output). INCONCLUSIVE for any question about real-engine behavior, because no live
browser run is allowed for this redteam; those stay open as gaps in procedure P1.

## 1. Attack plan (built from the code, not from worker or council claims)

A1. Fake versus template, same mistake twice. The template writes the RAW text through
the native setter and read-back compares e.value against its own sanitized computation.
Both harnesses use a fake setter that implements the same rule the template computes.
If template and fake share one misreading of the spec, every test passes and the live
engine still disagrees. Attack: compare both against the spec text fetched fresh
(section above), token by token, and probe the edges where a shared misreading would
hide: non-ASCII whitespace (NBSP, VT), FF, CR/LF at token ends and mid-token, empty
tokens, only-commas, only-whitespace, very long values.
A2. multiple flag is decorative. Neither the template nor either fake reads multiple.
The Python driver sets el.multiple but nothing consumes it; the node element passes
multiple:true but FakeInput never reads it. Attack: confirm by code read and by a
probe that flipping multiple changes nothing, and judge whether that matters (it does
not, if the rule is truly unconditional per spec, but the test name then overclaims
multiple coverage).
A3. maxLength edges. The pre-check refuses when sanitized.length exceeds maxLength.
Attack: boundary cases at exactly maxLength and maxLength minus 1, plus the spec
question of whether a script set should refuse at all (value setter has no maxLength
step, section above).
A4. url branch regression. The old shared url-or-email branch was split; the url
branch must keep whole-value trim and must not gain per-token behavior. Attack: url
with an inner comma and surrounding spaces through both harnesses.
A5. Vacuousness. Attack: the new tests must FAIL on the old template (R-C3) and must
FAIL if the fake is broken the other way (fake trims whole value only). If either
does not fail, the test is vacuous.
A6. Sibling paths. Attack: grep the whole repo for any other email sanitization or
set_value path (zen_dom.py, cu.py, fill) that the fix left unpatched.
A7. Final-log facts. Attack: re-verify every checkable claim in the log (line
numbers, hashes, dash scan, R8 grep, counts) rather than trusting it.
A8. P1 coverage. Attack: list the P1 probe inputs in final-log section 4 and check
whether any of them would catch a divergence on the edges in A1; a probe that cannot
catch the divergence is a gap in the log, even if the fix itself is unproven either
way.

## 2. Results

All times +07. Scratch copy /tmp/mochi-b2-6-rt (plain copy of the worktree, no .git).
Real worktree git status stayed clean apart from 4 untracked review logs (3 council
logs plus this file) through every check.

### 2.1 R-C1 and R-C2: suites pass on HEAD 5ee043d (PASS, not a break)

- node tests/cdp_snapshot.mjs, 00:29:06 +07, 3.7s, exit 0: "all cdp snapshot,
  redaction, fill, payload, no_after and scope regressions pass".
- cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2,
  00:29:14 +07, 4.1s: "Ran 52 tests in 4.110s, OK".
- Named test alone, same minute, 0.314s: "Ran 1 test in 0.314s, OK".

### 2.2 R-C3: discrimination round-trip, reproduced (PASS, not vacuous)

Scratch copy with scripts/cdp.mjs replaced by the 0400e86 version:
- node tests/cdp_snapshot.mjs, 00:30:26 +07, exit 1. First failure at
  tests/cdp_snapshot.mjs:247:8, the multiEmail ok assert, error
  'value verification failed', mutation_may_have_occurred true. Exactly the
  failing-first shape the final log claims.
- Python named test, same minute, 0.273s: "Ran 1 test, FAILED (failures=1)",
  AssertionError with {'ok': False, 'error': 'value verification failed',
  'events': [], 'value': 'a@b.com,c@d.com'}. The fake landed the per-token
  form while the old template expected the whole-trim form.
Scratch copy with the HEAD template restored (verified identical to HEAD by
diff, no output):
- node tests/cdp_snapshot.mjs, 00:30:43 +07, exit 0.
- Python named test, 0.300s: "Ran 1 test, OK".
The new tests are not vacuous: they fail on the old template in both
harnesses and pass on the fixed template.

### 2.3 R-C4: edge probes, both harnesses (no break; one inconclusive divergence)

Node harness, scratch copy with 13 probe cases appended to
tests/cdp_snapshot.mjs, 00:31:17 +07, exit 0, full suite plus probes:
- rt_nbsp 'a@b.com NBSP, c@d.com': ok true, value 'a@b.com NBSP,c@d.com',
  length 16, events input then change. NBSP kept, as the spec requires
  (NBSP is not ASCII whitespace). Template and fake agree.
- rt_vt 'a@b.com VT, c@d.com': ok true, VT kept ('a@b.com VT,c@d.com').
  Template and fake agree, spec agrees (VT is not ASCII whitespace).
- rt_ff FF at token ends: ok true, 'a@b.com,c@d.com'. FF trimmed, spec agrees.
- rt_crlf_ends 'a@b.com CRLF, c@d.com': ok true, 'a@b.com,c@d.com'. Spec
  agrees (LF and CR are ASCII whitespace at token ends).
- rt_crlf_mid 'a@b LF .com, c@d.com': ok true, value 'a@b.com,c@d.com'.
  DIVERGENCE FROM THE SPEC LETTER: the email sanitization algorithm
  (lines 1355-1368, fetched this session) has no newline-strip step, so
  the spec-letter result is 'a@b LF .com,c@d.com' with the LF kept
  mid-token. The template strips CR/LF globally before the email branch
  (pre-existing, line 594-596) and the fake strips them in its setter, so
  template and fake agree and no harness case can catch this. See I-1.
- rt_only_commas ',,,': ok true, ',,,' preserved. Spec agrees
  (possibly-empty tokens are kept).
- rt_only_ws '   ': ok true, value '', events [] (no change from the
  initial '', so no input/change, consistent with the unchanged-text rule).
- rt_ws_commas ' , , ': ok true, ',,'. Spec agrees.
- rt_long (9003-char landed value): ok true, value length 9003, events
  input then change. No length break.
- rt_url '  https://example.com/a,b  ': ok true,
  'https://example.com/a,b'. Url whole-trim keeps the inner comma: no
  regression from splitting the branch.
- rt_nomultiple (same input as the multiple case, multiple false): ok true,
  'a@b.com,c@d.com', identical to the multiple case. Confirms A2: multiple
  is never read anywhere in the exercised path. Correct per spec (the rule
  is unconditional), see R-2.
- rt_maxlen0_empty (maxLength 0, ''): ok true, ''.
- rt_maxlen0_nonempty (maxLength 0, 'a@b.com'): ok false, 'value exceeds
  maxlength', value stays ''. Boundary behaves as designed.

Standalone probe /tmp/mochi-b2-6-rt-probe.mjs (real template extracted from
the scratch scripts/cdp.mjs exactly as the Python test extracts it, run
through the node fake and the Python fake side by side): all 11 shared
cases give identical ok/value/events under both fakes EXCEPT rt_url, see
R-1. In particular rt_crlf_mid gives 'a@b.com,c@d.com' under both fakes
(same I-1 divergence), rt_nbsp and rt_vt keep the character under both
fakes, rt_only_commas and rt_ws_commas match the spec under both fakes.
First run of this probe had a probe bug (HTMLInputElement stayed wired to
the node fake, so the Python url case wrongly passed); fixed by assigning
HTMLInputElement = Fake per runCase, matching what the real Python driver
does (var HTMLInputElement = FakeInput), and re-run. The corrected run is
the one reported here (22 RT lines).

### 2.4 A5 second leg: breaking the fake fails the suite (not vacuous)

Scratch copy, node FakeInput email branch changed to whole-value trim only
(line 19 replaced, url branch untouched): node tests/cdp_snapshot.mjs,
00:32:10 +07, exit 1, first failure again at tests/cdp_snapshot.mjs:247:8,
'value verification failed'. The node cases discriminate fake behavior too:
a fake that models the old rule fails. Scratch file then restored identical
to the HEAD file (diff empty).

### 2.5 R-C5: final-log fact check (verified, with immaterial line drift)

- scripts/cdp.mjs: email branch if at line 597, split at 605, join at 610,
  maxLength pre-check at 617. The log says header comment 581-592 and email
  branch 598-611; actual spans are header 579-593 and branch if at 597 with
  code 605-610. Drift of 1-2 lines, immaterial, recorded as R-4.
- tests/cdp_snapshot.mjs: new cases at lines 245-261 (multiEmail 245,
  singleEmailComma 250, multiEmptyToken 254, multiMaxField 258). The log
  says 235-261; lines 235-238 are the pre-existing emailField case. The new
  block itself starts at the comment on line 240. Immaterial, recorded
  as R-4.
- tests/test_click3_redteam2.py: new test def at line 870, ends at 975.
  Log claim 870-975 exact.
- Dash scan (python byte counts): U+2014 0 and U+2013 0 in scripts/cdp.mjs,
  tests/cdp_snapshot.mjs, tests/test_click3_redteam2.py, and
  improvements/mochi-b2-6-final-log.md. Log claim verified.
- R8 grep at 0400e86: git show 0400e86:scripts/cdp.mjs has no 'multiple'
  (rc 1); git show 0400e86:tests/cdp_snapshot.mjs has only line 497, the
  scope-selector test line. Log claim verified exactly.
- Hashes exist as commits: 3532bfd, e500923, d88a472, b0876ca, 5ee043d,
  0400e86 (git cat-file -t, all 'commit').
- File counts, after clearing __pycache__ dirs (gitignored transient):
  tracked 1542 (git ls-files), on-disk 1552 excluding .git. The +10 is
  4 untracked review logs (3 council logs plus this file) and 6 ignored
  native build artifacts (native/pointer, native/wtype, keyboard-protocol
  and pointer-protocol .c/.h). Note __pycache__ regenerates on test runs
  (scripts/__pycache__ was present again after the runs above).

### 2.6 A6 sibling paths (closed, no second path to patch)

grep for email across scripts/ finds email handling only in scripts/cdp.mjs
(set_value template). No email sanitization exists in scripts/zen_dom.py or
scripts/cu.py. The fill action (scripts/cdp.mjs:676) uses real
Input.insertText, so the engine sanitizes natively and no template rule
applies. The fix covers the only template that models sanitization.

### 2.7 A8 P1 coverage (gap G-1 in the final log)

P1 probe inputs (final log lines 393-401): m1 '  a@b.com , c@d.com TAB',
m2 'a@b.com, b@c.com', m3 'a@b.com,,c@d.com', m4 maxlength 15 with the m1
input, control m0 url '  https://example.com  '. None contains a mid-token
CR or LF, NBSP, VT, only-commas, or only-whitespace. P1 as written would
PASS even if the live engine kept mid-token newlines (I-1), because no
input exercises that edge. P1 needs one more input to close I-1, see the
recommendation in section 4.

### 2.8 R-C6: spec re-verification (done, see the spec paragraph at the top)

Email sanitization text, value setter steps, and maxLength scope were read
fresh from the spec in this session (crawled 2026-11-22 17:26 UTC) and match
the worker's quote. The worker's spec reading is correct: per-token trim,
unconditional, empty tokens kept, single-comma rejoin. The multiple change
steps are a separate user-change algorithm and do not contradict it.

## 3. Findings

### I-1 (INCONCLUSIVE, the only open break attempt): mid-token CR/LF

Coordinates: scripts/cdp.mjs:594-596 (global CR/LF strip for INPUT, before
the email branch) and the email branch at 597-610; tests/cdp_snapshot.mjs:14
(FakeInput setter strips CR/LF first); tests/test_click3_redteam2.py:910-912
(Python FakeInput strips CR/LF first).
Reproduction (scratch only): node probe rt_crlf_mid, input
'a@b LF .com, c@d.com', gives ok true, value 'a@b.com,c@d.com' in both
harnesses. The spec-letter result is 'a@b LF .com,c@d.com' (the email
sanitization algorithm has no newline-strip step; LF is ASCII whitespace
only at token ends). Template and fake agree with each other, so no test in
either harness can catch a live engine that follows the spec letter. Real
engines almost certainly strip newlines on single-line input assignment, but
this redteam ran no live browser and cannot prove it either way. Verdict:
inconclusive, not a break. Closes only with a live probe input (see
section 4, P1 addition).

### R-1 (residual, latent, proven): Python FakeInput has no url branch

Coordinates: tests/test_click3_redteam2.py:910-912 (email test FakeInput:
email branch only). The F1 and maxlength drivers have their own FakeInputs
with no email or url handling at all.
Reproduction (scratch probe /tmp/mochi-b2-6-rt-probe.mjs, corrected run):
rt_url with fake py gives ok false, error 'value verification failed',
value '  https://example.com/a,b  ' (fake landed the raw value, template
expected the trimmed form), while fake node gives ok true,
'https://example.com/a,b'. No url case exists in the Python suite today,
so nothing fails today; the divergence is latent. If a url case is ever
added to the Python driver, it fails for a fake reason. Fix: give the
Python FakeInput the same url whole-trim branch the node fake has
(tests/cdp_snapshot.mjs:20-21).

### R-2 (residual, proven, not a defect): multiple is never read

Coordinates: scripts/cdp.mjs:597 (branch reads e.type only),
tests/cdp_snapshot.mjs:14-21 (FakeInput reads this.type only),
tests/test_click3_redteam2.py:923 (el.multiple set, never read).
Reproduction: rt_nomultiple gives byte-identical results to the multiple
case in both harnesses (node probe and standalone probe, 'a@b.com,c@d.com',
ok true). This is correct per spec (the sanitization rule is unconditional),
so it is not a break. It does mean the test name overclaims: the suite
proves the unconditional rule, and a future regression that gated the trim
on multiple would not be caught by any case, because no case outcome depends
on the flag. Consider one case that asserts the multiple and non-multiple
results are equal by construction, or rename the test to say unconditional.

### R-3 (residual, pre-existing policy, not introduced by B2-6)

The maxLength pre-check (scripts/cdp.mjs:617) refuses a set whose sanitized
length exceeds maxLength. The spec value setter (lines 4936-4956, fetched
this session) has no maxLength step, and the maxLength rule (lines
3663-3664) constrains only the value content attribute: a script set
through the value IDL attribute lands over-long and the element merely
suffers too-long validity. So the new multi_over case (maxLength 14, ok
false, 'value exceeds maxlength') pins a refusal the engine would not
make. This policy predates B2-6 (TESTREPAIR-C8, adjudicated then) and
applies to every input type, so it is not a break of the B2-6 fix; it is
recorded here because the task brief named maxLength edges as an attack
direction and the new test inherits the policy. Re-grading C8 belongs to
the council, not this redteam.

### R-4 (immaterial): final-log line-number drift

Header comment 579-593 (log says 581-592), email branch if at 597 (log says
598-611), node new-case block 240-261 (log says 235-261, including the
pre-existing emailField case at 235-238). All other checked claims verified
exact (section 2.5). No content claim is wrong.

### R-5 (coverage gap, not a break): events asserted for 1 of 4 cases

Only multiEmail (node, line 249) and multi_spaces (Python) assert events
input then change. The empty-token and maxlen cases assert no events. The
rt_only_ws probe shows the unchanged-value case correctly fires no events,
so the behavior is sound; the gap is assertion coverage only.

### G-1 (gap in the final log, not in the fix): P1 cannot catch I-1

See section 2.7. P1 as written has no input that distinguishes the
template's global CR/LF strip from the spec-letter email algorithm.

## 4. Verdict and recommendations

Verdict: KHONG PHA DUOC. The fix (3532bfd, e500923, d88a472) survived every
attack that could be run without a live browser: the spec reading is
correct (verified fresh from the spec text), template and fakes agree with
the spec on NBSP, VT, FF, CR/LF at token ends, empty tokens, only-commas,
only-whitespace, very long values, and the url branch, the tests fail on the
old template in both harnesses and fail when the fake is broken, and no
sibling set_value path was left unpatched. The final log's checkable claims
verified exact except immaterial line drift (R-4).

Recommendations for the coordinator (no code changed by this redteam):
1. Close I-1 by adding one input to P1 before the fix is quoted as
   live-proven: m5, type email, multiple, set 'a@b LF .com, c@d.com',
   and record the live read-back verbatim without adjusting the expected
   value to fit. If live keeps the LF, the template's global CR/LF strip
   and both fakes must be corrected to the live behavior; if live strips
   it, I-1 closes as engine-confirmed.
2. Add the url whole-trim branch to the Python FakeInput (R-1) so the
   Python driver is a faithful engine model for url as well as email.
3. Add one P1 input each for NBSP and VT token ends, or record them as
   harness-only (they agree everywhere already, so this is cheap
   completeness, not a gate).
4. Leave R-3 (maxLength refusal policy) to the council; it predates B2-6.

## 5. Evidence table (command, output, hash, Vietnam time, elapsed)

- R-C1: node tests/cdp_snapshot.mjs, HEAD 5ee043d, 00:29:06 +07, 3.7s,
  exit 0, "all cdp snapshot, redaction, fill, payload, no_after and scope
  regressions pass".
- R-C2: cd tests, PYTHONPATH=../scripts:. python3 -m unittest
  test_click3_redteam2, 00:29:14 +07, 4.1s, "Ran 52 tests in 4.110s, OK";
  named test alone 0.314s, "Ran 1 test, OK".
- R-C3 old template (scratch /tmp/mochi-b2-6-rt, scripts/cdp.mjs from
  0400e86): node exit 1, 00:30:26 +07, first failure
  tests/cdp_snapshot.mjs:247:8, 'value verification failed'; Python named
  test 0.273s, FAILED (failures=1), value 'a@b.com,c@d.com'.
- R-C3 restored template (scratch, diff-verified identical to HEAD): node
  exit 0, 00:30:43 +07; Python named test 0.300s, OK.
- R-C4 node probes (scratch, 13 cases appended): 00:31:17 +07, exit 0,
  RT lines in /tmp/rt-probe-node.log (NBSP kept length 16, VT kept, FF
  trimmed, CR/LF ends trimmed, mid-token LF stripped to 'a@b.com,c@d.com',
  ',,,' preserved, '   ' lands '', ' , , ' lands ',,', long value length
  9003 ok true, url 'https://example.com/a,b', nomultiple identical,
  maxlen0 empty ok, maxlen0 nonempty refused).
- R-C4 standalone probe (/tmp/mochi-b2-6-rt-probe.mjs, corrected run):
  22 RT lines in /tmp/rt-probe-py.log; both fakes agree on all cases
  except rt_url, where fake py gives ok false, 'value verification
  failed', value '  https://example.com/a,b  '.
- A5 broken fake (scratch, node FakeInput email whole-trim only): node
  exit 1, 00:32:10 +07, first failure tests/cdp_snapshot.mjs:247:8.
  Scratch file restored identical to HEAD (diff empty).
- R-C5 fact check: grep -n line numbers, dash scan 0/0 in all 4 files,
  R8 grep at 0400e86 (no multiple in scripts/cdp.mjs, only line 497 in
  tests/cdp_snapshot.mjs), 6 hashes exist as commits, counts tracked 1542
  and on-disk 1552 after clearing __pycache__.
- R-C6 spec fetch: https://html.spec.whatwg.org/multipage/input.html,
  crawled 2026-11-22 17:26 UTC; email sanitization lines 1355-1368, value
  setter lines 4936-4956, maxLength lines 3663-3664, multiple change steps
  lines 1335-1349.
- Real worktree git status clean apart from 4 untracked review logs at
  every check. No worker file modified, no push, no live run, no file
  deleted except gitignored __pycache__ dirs cleared before counting, per
  the brief.

Elapsed: task received 00:24:43 +07; docs and diff read by 00:29 +07;
R-C1 and R-C2 00:29 +07; R-C3 00:30-00:31 +07; R-C4 and A5 00:31-00:32 +07;
fact checks and log write 00:32-00:35 +07.

## 6. Commit record (this redteam's own commit, no push)

- This log file: improvements/mochi-b2-6-redteam-log.md, commit
  342f1bae8b2e493b14aba2f9d5f57cd0289f4221 (342f1ba). The hash line was
  filled by a follow-up commit on this same file. No push was made
  (per the brief).

