# W-ZENPROOF2-F1-FIX log: direct-read fallback for the current tab (F1, run 3)

Task received 21:37:09 +07, 2026-11-22. Worker W-ZENPROOF2-F1-FIX,
independent fix for ZT-B run 3 attempt 1 (COORD-CLICK-10).
Branch todolist-push, HEAD at start 8b0b32d. No live proof run,
no Zen tab touched, no reviewer spawned.

## 1. The failure (evidence, not trust)

- Run 3 attempt 1, launched 21:27:33 +07, wall 13.8s, outcome
  error, "could not identify the current tab". No tab opened,
  no input sent, cleanup skipped.
- `improvements/c5-zenproof-runs/run-3-attempt1.json`: tabs_before
  count 18, current handle 41cc71d7, and its scan entry is
  `{"handle": "41cc71d7", "error": "HTTP 500 on GET
  /session/5127488a-9a55-42db-8ddd-8da572654db5/title:
  {\"value\":{\"error\":\"unexpected alert open\",\"message\":
  \"Unexpected alert dialog detected. Performed handler
  \"dismiss\"\"..."}`. No title, no URL on the entry. The
  runner's phase 1 loop sets original_url from that entry,
  gets None, and raises.
- Diagnosis (run-3 log section 4, read-only): second list
  21:28:43 reproduced the empty entry; direct diagnostic
  21:29:34 (diag-current-tab.py, fresh ZenSession, no tab
  switch, only GET /window, /url, /title plus one JS
  evaluate) read the current tab as the healthy visible
  Calendar tab, URL
  https://calendar.google.com/calendar/u/1/r/week, readyState
  complete; third list 21:30:25 resolved the URL, 0 empty
  entries. The empty scan entry is a transient scan-read
  artifact, not a dead tab. Attempt 2 then passed phase 1
  with the same Calendar tab as current.
- Mechanism: `zen_dom.list_tabs` switches through every tab
  and records a per-handle failure as an error entry with no
  URL, then restores the original tab. The title read for the
  current tab failed once (HTTP 500, unexpected alert open;
  Marionette dismissed the alert). The scan never re-reads
  that tab, so phase 1 had no URL for the original tab.

## 2. The fix

File: `improvements/c5-zenproof-runs/zen-tab.py` only (plus
tests). No runner change: phase 1 reads the same `list`
response, so a resolved entry flows through unchanged.

New helper `_resolve_current_entry(z, tabs, current_prefix)`,
called from `cmd_list`:

- Fires only when the scan entry for the current tab exists
  but carries no usable URL (missing, non-string, or '').
  When the scan already resolved the URL, nothing is re-read.
- Direct read in the SAME session: after a successful scan
  the current window is the restored original tab, so GET
  /url + /title needs no switch. This is strictly stronger
  than a fresh-session read (the coordinator's manual
  diagnostic), because the handle check proves identity: a
  new session could not prove the current tab is the same
  one as in the scan (handles are ephemeral per session).
- Verification, all required, fail-closed: handle read 1,
  URL read 1, handle read 2, URL read 2; both handle reads
  equal each other and the scan's current prefix; both URL
  reads equal and non-empty. Any mismatch, empty URL, or
  failed read leaves the entry untouched and resolved False,
  so the caller aborts exactly as before the fix.
- The title is evidence only and may legitimately be ''
  (about:blank), so a failed title read still resolves with
  title '' instead of refusing. The title is read after the
  URL reads; a tab change in between is caught by the
  second handle read.
- Boundary, deliberate: a scan with NO entry at all for the
  current tab is NOT synthesized. The fallback only patches
  an entry the scan returned; a missing entry still aborts.
  Synthesizing would inflate the list count (len(tabs)) and
  break the runner's count_restored accounting.
- `cmd_list` returns `current_fallback: True` when the
  fallback fires, so the runner's tabs_before records that
  the URL came from a direct read, not the scan. The patched
  entry keeps the standard {handle, title, url} shape (the
  error key is dropped).
- Module docstring `list` line updated to mention the
  fallback.

What the fix does NOT do (out of scope, noted for review):
- It does not detect the silent restore failure (Redteam
  F3b, pinned test): if list_tabs restored the wrong tab
  silently, the fallback resolves THAT tab, same as the
  scan would with a URL present. The fallback does not make
  F3b worse; fixing F3b needs a pre-scan current comparison,
  a different change.
- It does not touch `_scan`, `_resolve_url`, `cmd_open`, or
  `cmd_close`: their callers already fail closed on an
  unreadable entry (pre-check skips it, restore reports
  original_missing / scan_error).

## 3. Tests (7 new, all in tests/test_zenproof2_fix.py, ZenTabFixTest)

- test_list_fallback_resolves_empty_current_entry: the F1
  repro. Current tab's URL in error_entry_urls, so the scan
  entry is {handle, error}; cmd_list patches it to the
  owner URL + title, sets current_fallback True, count
  unchanged, error key gone.
- test_list_fallback_does_not_fire_when_scan_resolves_url:
  no flag, current entry unchanged, a non-current error
  entry left untouched.
- test_list_fallback_refuses_when_current_handle_changes:
  GET /window flips to another tab after the scan's current
  read (H1 prefix mismatch). Entry untouched, no flag.
- test_list_fallback_refuses_when_second_handle_read_differs:
  flip between the two fallback handle reads (H1 != H2).
  Entry untouched, no flag.
- test_list_fallback_refuses_when_url_reads_disagree: the
  two URL reads return different URLs. Entry untouched.
- test_list_fallback_refuses_when_direct_read_raises: GET
  /url raises in the fallback. Entry untouched.
- test_list_fallback_does_not_synthesize_missing_entry:
  boundary pin. Scan drops the current entry; the list
  keeps the scan's entries and count, no flag.

Honest note on the baseline: on the old code (git stash of
zen-tab.py only, tests kept), exactly 1 of the 7 new tests
fails: the happy-path fallback test. The 6 refusal/boundary
tests pass on old code too, because with no fallback there
is nothing to accept wrongly. They are guards on the NEW
code's checks, not regression guards against the old code.
Proven to bite by mutation: with the handle check and the
URL-agreement check removed (temporary /tmp edit, restored
after), 3 of the 4 refusal tests fail (both handle tests +
the URL-disagree test); the direct-read-raises test still
passes, since it exercises the exception path the mutation
did not touch.

## 4. Verification (all self-run, commands + outputs)

- Targeted: `python3 -m unittest tests.test_zenproof2_fix`
  Ran 51 tests (44 old + 7 new), OK.
- Baseline: old code + new test file, Ran 7, FAILED
  (failures=1), exactly the happy-path test. Stash popped,
  diff restored.
- Mutation: checks removed, Ran 4 refusal tests, FAILED
  (failures=3). Restored from /tmp backup, suite 51/51 OK
  again, diff identical.
- G0a: `python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec` Ran 177
  tests in 12.536s, OK.
- G0b: code_exec.validate_program on PROBE_PROGRAM and
  SEND_PROGRAM, both run2 and run3 runners, all 4 validate
  OK (Module).
- Full suite: detached, log /tmp/w-zenproof2-f1-fullsuite.log
  (result recorded in section 5; first launch failed on the
  invocation, `discover -s tests -t .` needs an importable
  start dir, relaunched as `discover -s tests`).
- 0 em dash (U+2014) and 0 en dash (U+2013) in both changed
  files, counted by python.
- Fixture untouched: sha256 of tests/two_vision_fixture.html
  is 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, identical to FIXTURE_SHA. git diff shows only the
  two intended files (plus the pre-existing dirty
  tests/realistic/clone1-batch3/results.json from another
  worker, untouched, not committed).
- NOT verified (needs a live run, out of scope for this
  fix): whether the fallback resolves the F1 read on the
  live narrowed window; whether the alert that caused the
  HTTP 500 recurs. Re-run of the proof is run 4, fresh
  intent/message, only after this fix (and the F2 fix) land
  and are reviewed.

## 5. Full suite result

`python3 -m unittest discover -s tests`, detached, log
/tmp/w-zenproof2-f1-fullsuite.log: Ran 2377 tests in
226.101s, FAILED (failures=1, errors=2, skipped=17).
The 3 are exactly the known environment errors, same as
the amend-2/amend-3 baselines: ERROR setUpClass
test_cursor_file.CursorFileTests (g++ C++26), ERROR +
FAIL test_tc02_controller.Tc02MenuBarTests x2 (tesseract
unavailable). 0 new regressions. Ran 2377 is 2370 + 7 new
tests from this fix.

## 6. Commits

PENDING; filled in after push + ls-remote verify.
