# ITEM8-MICROGAP log - AMEND4 item 8 url/email trim (VM lane)

- Worker: ITEM8-MICROGAP, for coordinator COORD-CLICK-3 (owner the owner)
- Task received: 2026-11-22 08:29:48 +07
- Fix commit pushed: 2026-11-22 08:36:25 +07
- Worktree: ~/workspace/cu-item8-microgap, clean worktree at pinned HEAD e1a4e77
- Base: todolist-push, HEAD e1a4e77 (RECONCILE-AMEND4)
- Branch pushed: item8-microgap
- Fix commit: 7177cdc6f6dd261cecb8af7518fa8793082442c3
- No em dash or en dash anywhere in files written or committed (checked with python scan for U+2014/U+2013)

## 1. Codex lane implementation (read-only, laptop worktree)

- Branch amend4-codex, HEAD 06a34e8, worktree /home/james/workspace/cu-amend4-codex, clean status.
- Commit 0eb3429 "fix: verify sanitized browser field values", files: scripts/cdp.mjs, tests/cdp_snapshot.mjs.
- scripts/cdp.mjs set_value (Codex form, regex):
  - stripped = requested.replace(/[\r\n]/g, '')
  - expectedValue = INPUT ? (type url/email ? stripped.replace(/^[\t\n\f\r ]+|[\t\n\f\r ]+$/g, '') : stripped) : requested.replace(/\r\n?/g, '\n')
  - maxLength pre-check measures expectedValue.length; read-back compares e.value against expectedValue.
- tests/cdp_snapshot.mjs: FakeInput/FakeTextarea model the engine sanitization (same regex trim for url/email); newline set_value cases added (input 'one\r\ntwo\rthree\n' to 'onetwothree', textarea to 'one\ntwo\nthree\n').
- Codex added NO url/email trim test case: grep for url/email in its tests/cdp_snapshot.mjs finds only the fake (line 14). The trim was implemented but unexercised on the Codex lane.
- Codex Python fake (tests/test_click3_redteam2.py) has no url/email trim either (grep finds no url/email there). The Python path was not part of Codex's change.

## 2. HTML Standard verification (source)

- Fetched https://html.spec.whatwg.org/multipage/input.html, crawled 2026-11-22 01:31 UTC.
- Email state (4.10.5.1.5), value sanitization algorithm, quoted from the source: split on commas, strip leading and trailing ASCII whitespace from each resulting token, rejoin with a single comma. The multiple-email change steps likewise strip leading and trailing ASCII whitespace from each value.
- ASCII whitespace per the Infra Standard: TAB U+0009, LF U+000A, FF U+000C, CR U+000D, SPACE U+0020.
- Note: the fetched rendering of the URL state section (4.10.5.1.4) does not restate its sanitization-algorithm paragraph in the crawled text, so the URL rule is established by the live probe below, not by a quoted URL paragraph. The email rule is quoted from the source.
- F1 live-confirm reference: improvements/fcc-f1-live-confirm.md, commit f4dcfa3. Chromium 130 headless, 2026-11-22 06:01:51 to 06:15:00 +07 (789 s). Results: input strips \n and \r (a\nb, a\r\nb, a\rb all read back "ab"); textarea normalizes CRLF/CR to LF.

## 3. Live url/email trim probe (laptop Chromium, F1 method)

- Command (SSH via ~/workspace/ssh-laptop.sh, two short calls under 30 s):
  - wrote /tmp/item8-probe.html (9 inputs, script sets values, records JSON in pre#result)
  - chromium --headless --disable-gpu --dump-dom file:///tmp/item8-probe.html
- Chromium 157.0.8103.38 Arch Linux. Results:

| id | type | set | got |
| --- | --- | --- | --- |
| u1 | url | "  https://example.com  " | "https://example.com" |
| u2 | url | "\thttps://example.com\t" | "https://example.com" |
| u3 | url | "https://exa\nmple.com" | "https://example.com" |
| u4 | url | "   " | "" |
| e1 | email | "  a@b.com  " | "a@b.com" |
| e2 | email | "\ta@b.com\t" | "a@b.com" |
| e3 | email | "a@b.com\r\n" | "a@b.com" |
| t1 | text (control) | "  hello  " | "  hello  " (NOT trimmed) |
| uml | url maxlength=5 | "  abc  " | "abc" |

- Conclusions: url/email trim leading/trailing spaces and tabs; internal newline stripped; text input does NOT trim; maxLength interplay confirmed live ('  abc  ' is 7 raw chars but lands as 'abc' under maxLength 5), so the pre-check must measure the TRIMMED length, exactly where Codex put it.

## 4. VM lane scope check (no Python path)

- Grep of scripts/cu.py, scripts/zen_dom.py, scripts/first_action.py for sanitization/maxLength: no Python code computes set_value sanitization or a field maxLength (only an unrelated subgoal_policy schema). Python set_value goes through scripts/cdp.mjs.
- VM Python fake in tests/test_click3_redteam2.py lines 569-576 models input CR/LF strip and textarea CRLF normalization only, same as the Codex lane. Left untouched: no RT test exercises url/email set_value, and Codex's change did not touch it.

## 5. Failing-first proof test

- Edited tests/cdp_snapshot.mjs only (fake + cases), before touching scripts/cdp.mjs.
- Fake: adopted the Codex sanitization-modeling FakeInput/FakeTextarea verbatim.
- Cases added: Codex newline cases (input, textarea) plus 5 trim cases: url trim with space+tab, email trim with tab+spaces, text no-trim control, url maxLength 5 with '  abc  ', all-whitespace url to ''.
- Run: `node tests/cdp_snapshot.mjs`, exit 1. First failure at line 223 (urlField ok assert): result {"ok":false,"completed":0,"error":"value verification failed","mutation_may_have_occurred":true}. The fake trimmed to 'https://example.com' while cdp.mjs compared read-back against the untrimmed form. Gap proven live in the test harness.

## 6. Fix (scripts/cdp.mjs, same place Codex put it)

- Same sanitized/expectedValue computation in the set_value template. Kept the VM char-code style (no regex escapes in the template, per the existing comment).
- `const sanitized` to `let sanitized`; after the CR/LF strip / textarea normalization ternary, added for INPUT url/email a trim loop over char codes 9 (TAB), 12 (FF), 32 (SPACE) at both ends, before the maxLength pre-check and the read-back.
- Equivalence proof: Codex trims [\t\n\f\r ] from the CR/LF-stripped value; \n (10) and \r (13) are already gone, so the effective set is {\t, \f, space} = char codes 9, 12, 32. Identical result.
- Known limitation inherited from Codex (out of scope): for email with `multiple`, the spec strips each comma-separated token; this fix trims only the whole value ends, matching Codex. No `multiple` handling exists in the set_value path on either lane.
- Diff: scripts/cdp.mjs +22/-8 lines (comment + let + 6-line trim block), tests/cdp_snapshot.mjs +52/-2 lines.

## 7. Verification (worktree at e1a4e77, before/after)

Baselines (pristine e1a4e77):

- node tests/cdp_snapshot.mjs: exit 0
- python3 -m unittest tests.test_cdp_snapshot: Ran 2 tests, OK
- python3 -m unittest tests.test_first_action: Ran 71 tests, OK
- python3 -m unittest tests.test_click3_redteam2: Ran 51 tests, FAILED (errors=41, 0 failures)
- python3 -m unittest tests.test_zen_dom: Ran 42 tests, FAILED (errors=4, 0 failures)

After the fix (same commands):

- node tests/cdp_snapshot.mjs: exit 0 (new trim cases pass)
- python3 -m unittest tests.test_cdp_snapshot: Ran 2 tests, OK
- python3 -m unittest tests.test_first_action: Ran 71 tests, OK
- python3 -m unittest tests.test_click3_redteam2: Ran 51 tests, FAILED (errors=41, 0 failures), unchanged
- test_zen_dom not re-run after the fix (untouched file, see below)

Pre-existing failures, all confirmed unrelated:

- RT 41 errors: every one is `RuntimeError: private wtype helper is missing: <worktree>/native/wtype` (82 occurrences = 41 x 2 printings). native/wtype is a gitignored build artifact absent from the shared checkout too. Nothing to do with set_value.
- test_zen_dom 4 errors: `ModuleNotFoundError: No module named 'test_click3_redteam2'`, a standalone-run import-path quirk. Confirmed identical on pristine HEAD via git stash round-trip (stash, run, pop, diff unchanged).
- Shared checkout NOT used: ~/workspace/computer-use-wayland is at 24e0df9 (diverged from origin/todolist-push e1a4e77) with staged modifications to tests/test_click3_redteam2.py and tests/test_zen_dom.py that are not mine. Its suite results differ (redteam2 failures=8 errors=1, first_action failures=25 errors=9) because of its own dirty state. I ran nothing that modifies it and touched neither file.

## 8. Commits and pushes

- Fix commit 7177cdc: `git add scripts/cdp.mjs tests/cdp_snapshot.mjs` then `git commit scripts/cdp.mjs tests/cdp_snapshot.mjs -m ...` (explicit pathspec both times, never plain git commit, never git add -A).
- Push: `git checkout -b item8-microgap` then `git push -u origin item8-microgap`.
- Verified 2026-11-22 08:36:25 +07: `git ls-remote origin item8-microgap` returned 7177cdc6f6dd261cecb8af7518fa8793082442c3 refs/heads/item8-microgap.
- Push target note: pushed to new branch item8-microgap, NOT to todolist-push. origin/todolist-push is e1a4e77, but the local todolist-push branch in the shared checkout has diverged (24e0df9, ahead 2 behind 10), so pushing there would have made that branch non-fast-forwardable. The coordinator can merge or cherry-pick 7177cdc.
- This log file is committed separately with an explicit pathspec (see final report for its hash and ls-remote verification).
