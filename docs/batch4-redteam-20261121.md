# Batch 4 redteam report: batch 2 and batch 3 deliverables, 2026-11-21

Scope: every batch 2 and batch 3 deliverable plus the batch 2/3 report
itself (coord/clone1.md at 6599706, plus the d5223c1 supplement).
Method: assume flawed until proven otherwise. Recomputed every number
I checked from disk, re-ran every suite I could, read the new code,
checked the git history, and verified external claims against live
sources. I fixed nothing. I modified no file except this report.
(One side effect: my realistic runner re-runs rewrote the three
results.json files; I restored all three to HEAD with git checkout
right after. Working tree is clean apart from other agents' files.)

Repo HEAD during this audit: beffa19. Batch 2/3 base: 1c7d252.
Date: 2026-11-21, times UTC unless noted.

## Summary counts

- Wrong fact: 5
- Unverified claim stated as done: 6
- Real bug: 11
- Minor: 5
- Total findings: 27

The most important findings are B1, B2 and B3. The MCP server type
tool cannot type into a textarea (verified live), the MCP server dies
on one oversized line (verified live), and the three download test
flakes share one root cause in the fixtures (immediate revoke or
remove of the download trigger after click).

## Wrong fact

### W1. Four line counts are each off by one, same direction

- coord/clone1.md says scripts/mcp_server.py is 633 lines. It is 632
  lines (splitlines count, file ends with newline).
- coord/clone1.md says tests/test_mcp_server.py is 278 lines. It is 277.
- coord/clone1.md says tests/atspi_probe.py is 289 lines. It is 288.
- coord/clone1.md says docs/research/2026-11-21-atspi-zen-control.md
  is 272 lines. It is 271.
- The correctly counted files in the same report (scrub plan 282 lines
  and 10367 bytes, personal audit 214 lines, todo audit 375 lines,
  RUN-REPORT 113 lines, RUN-LOG 16 lines, clip.mp4 120176 bytes) all
  recompute exactly, so this is a systematic plus-one error in the
  four files above, not a counting method difference. Severity is
  low, but four wrong numbers in one report is a pattern, not a typo.

### W2. Wrong file path for the bridge content test

- coord/clone1.md, batch 2 task 1 section, says the check is
  content_node_test.mjs and implies the path
  tests/webext-native-bridge/extension/content_node_test.mjs.
  That path does not exist; node fails with MODULE_NOT_FOUND.
- The real path is tests/webext-native-bridge/content_node_test.mjs
  (no extension/ segment). The count claim is right (16 checks, 0
  failures, re-run by me), only the path is wrong. Anyone following
  the report's path cannot run the test.

### W3. PR #1 merge state contradicts itself inside the same report

- The PR review section says GitHub shows mergeable UNKNOWN.
- The scrub plan section says PR #1 has mergeState CLEAN.
- Both cannot hold at the same moment: CLEAN implies mergeable.
- Current live state from gh pr view 1: state OPEN, mergeable
  UNKNOWN, mergeStateStatus UNKNOWN, 0 reviews. The CLEAN claim is
  now contradicted and cannot be verified retroactively. The two
  agents who wrote the two sections likely checked at different
  moments while GitHub was still computing, but the report presents
  both as fact with no timestamp.

### W4. The AT-SPI stack the report says the machine "now has" is gone

- coord/clone1.md, "Ghi chu them", says the machine now has
  at-spi2-core 2.52.0 and pyatspi 2.46.1.
- Checked 2026-11-21 about 11:30 UTC: python3 -c "import pyatspi"
  fails with ModuleNotFoundError. /usr/libexec/at-spi-bus-launcher
  does not exist. dpkg shows only at-spi2-common 2.52.0 and
  libatk-bridge2.0 2.52.0 still installed. at-spi2-core,
  python3-pyatspi, gir1.2-atspi-2.0, dbus-x11 and the gi module are
  all gone. Xvfb, xdotool 3.20160805.1 and /tmp/firefox (Firefox
  160.0.1, verified with --version) survive.
- The apt installs did not survive the VM restart; only files under
  /tmp and home persist. The probe cannot run now without a full
  reinstall. Any claim that the stack is available on this machine
  is false as of this audit. This is also why batch 5 task 2 (a
  self-contained probe) is necessary, not optional.

### W5. Batch2 t10 README summary sentence contradicts its own list

- tests/realistic/clone1-batch2/t10-dashboard/README.md line 60
  says "All 39 steps run".
- The same README's numbered list has 40 items (1 to 40), and the
  checker prints 40 steps (verified in my standalone t10 run).
- The report's "40" is right; the README sentence is wrong by one.

## Unverified claim stated as done

### U1. "10 passed, 0 failed" is a single-run result, not a stable one

- Batch 1 (tests/realistic/clone1): agent run 10/10, wall 41534 ms.
  My independent re-run, 2026-11-21 about 11:25 UTC: 8 passed,
  2 failed (t07-download-check and t10-login-upload-download, both
  "download.saveAs: canceled"), wall 32211 ms.
- Batch 2: agent 10/10 twice; coordinator re-run 9/10 (t10,
  "download.path: canceled"); my re-run 10/10, wall 44193 ms.
- Batch 3: agent 10/10; coordinator re-runs 9/10 then 8/10; my
  re-run 10/10, wall 39500 ms.
- The committed results.json files prove the instability: batch2
  committed file shows 9/10, batch3 committed file shows 8/10,
  while the report headlines the agent's 10/10 runs. The report
  does disclose the coordinator re-runs, so this is not hidden,
  but the "10/10" headline is not reproducible and the root cause
  was not found (see B3, which finds it).
- First attempt note: my first runner attempts failed 0/10 because
  /tmp/realistic-b2-scratch (the playwright-core install the
  runners depend on) no longer exists after the VM restart. I
  reinstalled playwright-core 1.55.0 in /tmp/realistic-redteam-
  scratch (2 s) and re-ran. The runners have no committed
  package.json and depend on a /tmp install that does not survive
  restarts; that dependency is not documented in the run docs.

### U2. AT-SPI live numbers have no raw logs and could not be reproduced

- docs/research/2026-11-21-atspi-zen-control.md reports: find_app
  11.0-31.9 ms, full walk 71 nodes 15.4-29.9 ms, onboarding dismiss
  and Increment click 0.2-0.3 ms, setTextContents returns True
  with read-back empty, four keysym variants failing, keycodes
  30/48 producing wrong characters, xdotool control working.
- No log file for any of these runs exists in the repo. The
  coordinator tried to reproduce the probe 3 times on 2026-11-21
  and failed at find_app every time (30 s timeout). I did not
  retry the full session setup; the stack is gone now (see W4),
  so reproduction currently requires a reinstall first.
- The 0.2-0.3 ms click timing is suspiciously fast for a D-Bus
  round trip through the AT-SPI bus and should not be quoted
  without a log.
- What I could verify: Bug 2087495 is real (Bugzilla, RESOLVED
  FIXED, 161 Branch, inverted IsTextRole() guard, exactly as the
  doc describes), Firefox 160.0.1 exists at /tmp/firefox, the
  tarball is exactly 90943956 bytes as claimed, and py_compile
  passes on tests/atspi_probe.py. The bug explanation is correct;
  the live timing numbers are single-source and unverified.

### U3. Single-source timing and load claims, no longer checkable

- "Load average 7.68, 9 agent running in parallel" during the
  batch 1 run; "16.0 s" for the earlier batch 1 run; "t06 was
  also run standalone 3 times after its fix, all pass". None of
  these has a surviving log (results.json was overwritten by the
  later 41534 ms run). They may be true, but they cannot be
  checked now. Do not quote them as verified.

### U4. Codemode "60 ops" does not match the committed tree

- docs/code-mode-search-describe.md and the report say the token
  numbers were measured with 60 ops.
- At commit 03fbbb7 (the codemode commit) scripts/ holds 59
  .py/.mjs/.sh files; scripts/mcp_server.py was added only in the
  later commit 98edc39. The 60th op came from a sibling agent's
  uncommitted file present in the working tree at measurement time.
- The token numbers (7292 chars, 1823.0 estimate) recompute exactly
  against the current 60-op tree, but against the committed 59-op
  tree the catalog would be about 7216 chars, about 1804.0
  estimate. The doc's numbers are stale relative to its own commit
  by about 19 tokens. Minor, but the doc should state which tree
  it was measured against.

### U5. Personal audit "five 15-char sk- tokens" not reproduced

- docs/personal-info-audit-20261121.md says five 15-char "sk-"
  tokens were found, all inside a ".json" filename in log lines.
- I searched improvements/live-test-log.md for sk- tokens of that
  length and found none (the only match is the feature name
  "sk-verification", not a token). The audit's raw totals (1075
  regex matches, 167 placeholders, 908 real-looking, 36 unique
  matches classified by hand) are single-source with no surviving
  match list. The headline findings of the audit (name 71 lines in
  45 files, email at 25 branch tips) I verified independently and
  they check out (see Verified correct). This one detail does not.

### U6. Scrub plan ".git 6.0M" is stale

- docs/email-history-scrub-plan.md says .git is 6.0M. It is 7.5M
  now (du -sh .git). The plan was written before later commits
  grew the repo. Time-sensitive number, not an error at write
  time, but the plan should not state it as a fixed fact.

## Real bug

### B1. MCP server type() fails on textarea and contenteditable (verified live)

- File: scripts/mcp_server.py, type(), the inline JS.
- The JS always takes the setter from
  window.HTMLInputElement.prototype, even for a textarea or any
  other element, because that descriptor exists and the || fallback
  never runs.
- Calling the input setter on a textarea throws TypeError:
  Illegal invocation. I verified this in Chromium 1254 with the
  exact JS logic copied from the file: input works (before "" after
  "hello"), textarea throws Illegal invocation, contenteditable div
  throws Illegal invocation.
- The fake backend masks this completely (it just sets a value in
  a dict), and the report's type verification ("before '' after
  'Ada'") ran only against the fake backend's #name input.
- The tool's description says "Type text into an element". In
  practice it can only type into <input>. Every multi-line field
  in the realistic tests (chat app, code editor, email compose)
  would fail through this tool. Fix: pick the setter from the
  element's own prototype chain (check tagName first), or fall
  back to direct assignment when the setter throws.

### B2. MCP server dies on one oversized line (verified live)

- File: scripts/mcp_server.py, serve(), line 581.
- A single line longer than MAX_LINE_BYTES (8 MB) raises
  ValueError("invalid MCP message size or framing") with no
  handler around it, so the whole server exits with code 1 and a
  traceback. I verified live: after a 9 MB line the process exit
  code is 1, stderr ends with the ValueError traceback at line 581,
  and the next write gets BrokenPipeError.
- One malformed or oversized message from a client should produce
  a JSON-RPC error and keep the server alive, not kill it. The
  server also reads with readline(MAX+1), so a longer line would
  be split across reads and corrupt framing even without the raise.

### B3. Download fixtures race the browser (root cause of all download flakes)

- Files: tests/realistic/clone1/t07-download-check/fixture.html
  line 44, tests/realistic/clone1/t10-login-upload-download/
  fixture.html line 74, tests/realistic/clone1-batch2/t10-dashboard/
  fixture.html lines 223-231.
- Batch 1 t07 and t10 do a.click() then immediately
  URL.revokeObjectURL(a.href) in the same task. Batch 2 t10 does
  a.click() then immediately a.remove().
- If the browser has not started reading the blob by the time the
  trigger is destroyed, Chromium cancels the download and
  Playwright reports "download.saveAs: canceled" (batch 1) or
  "download.path: canceled" (batch 2). Under load the browser
  loses this race more often, which is exactly the observed
  pattern: my batch 1 run failed t07 and t10, the coordinator's
  batch 2 re-run failed t10, all with the same error.
- The coordinator's conclusion ("flaky under load") describes the
  symptom but misses the cause. The cause is in the fixtures, it
  is deterministic in structure, and it is fixable: delay the
  revoke/remove (for example setTimeout 1000 ms) or do not revoke
  at all. Batch 3 t10's failure ("position not reset after next")
  is a different timer flake and is not covered by this finding.

### B4. AT-SPI probe logs final_readback ok=True unconditionally

- File: tests/atspi_probe.py, main(), the mode full tail.
- log("final_readback", True, paragraph=..., counter_seen=...) is
  called with ok=True no matter what paragraph_text returns and
  no matter whether counter_seen is False.
- The process exit code is still driven by the ok flag, so the
  exit code is correct, but a reader of the JSON log sees a
  passing verification step for a check that may have failed.
  A log line that always says ok is not a verification.

### B5. AT-SPI probe may type into the wrong field

- File: tests/atspi_probe.py, main(), mode type/full.
- field = find(app, role="entry") takes the first entry in
  depth-first order. The Firefox chrome (address bar combo box
  with an entry child) comes before web content in the tree, so
  the first entry found may be the address bar, not the fixture's
  "Name" field.
- The code logs field.name but never asserts it is the intended
  field. The doc's typing results therefore rest on an unchecked
  assumption about tree order. I could not run the probe to test
  this (see W4), so this is a risk, not a proven mis-target.

### B6. Batch3 t09 clickAndClose can mask a failed click

- File: tests/realistic/clone1-batch3/t09-multi-window/check.mjs,
  clickAndClose helper (lines 55-63).
- It swallows any error containing "has been closed" as long as
  the close event fires. If the popup closes for a reason other
  than the click landing (or the click never reaches the button),
  the helper still passes and the failure only surfaces later as
  a confusing assertion ("main window missing dark class after
  prefs dark"), which is exactly what the very next full run after
  the fix produced (8/10 run, committed results.json).
- The helper trades a loud failure for a quiet one. It should
  verify the click's effect (for example the postMessage result)
  before treating the close as success.

### B7. Codemode search: docstring promise vs actual limit, plus weak guarantees

- File: scripts/codemode_search.py, search_ops().
- Docstring: "Empty query returns every op sorted by name." In
  fact it returns at most limit (default 10). Verified: search ""
  returns total 60 but only 10 results.
- describe_op() docstring promises total output under 2000 chars,
  but the code only truncates head to 2 lines once and then returns
  whatever is left. Current worst case across all 60 ops is 957
  chars, so the promise holds today by luck, not by enforcement.
- _tags() uses substring matching, so tags can come from inside
  unrelated words (for example "drive" matched inside "driver",
  "session" inside "session-owned"). Mostly benign today, but the
  mechanism can produce misleading tags as scripts are added.

### B8. Codemode registry errors escape as raw JSONDecodeError

- File: scripts/codemode_search.py, list_snippets() and
  get_snippet().
- The module docstring says CodemodeSearchError covers an
  "unreadable registry", but a malformed snippets/registry.json
  raises a raw json.JSONDecodeError, and a missing file raises
  FileNotFoundError. Only the unknown-name path raises
  CodemodeSearchError. Callers catching CodemodeSearchError will
  miss the corrupt-registry case.

### B9. MCP session_start can leak the lock and the browser session

- File: scripts/mcp_server.py, ZenBackend.session_start().
- After zen.__enter__() succeeds, the code calls
  self.manager.record_open(). If record_open raises (for example
  a disk error writing the log), the exception propagates out of
  session_start with self.zen set and the lock held, and nothing
  releases either. The ZenSession constructor itself cannot raise
  (it only stores arguments, verified in scripts/zen_dom.py), and
  the __enter__ failure path does release, so this window is
  narrow, but it is a real leak path on the success path.

### B10. MCP screenshot base64 decode sits outside the error handler

- File: scripts/mcp_server.py, Server.call_tool().
- base64.b64decode(image) runs after the try block that converts
  tool exceptions to ToolError. Corrupt base64 from the live
  backend would raise ValueError out of call_tool, which serve()
  turns into a JSON-RPC protocol error (-32000) instead of an
  isError tool result. Only reachable with corrupt live data, but
  the docstring promises tool errors always come back as isError.

### B11. MCP initialize accepts any protocol version

- File: scripts/mcp_server.py, Server.handle().
- initialize returns the client's protocolVersion verbatim with no
  validation or negotiation. A client asking for a version the
  server does not implement gets a silent yes. Lenient, not a
  crash, but it is not version negotiation.

## Minor

### M1. "0 long dash in all changed files" is imprecisely worded

- coord/clone1.md intro claims 0 long dash characters in all
  changed and created files.
- improvements/live-test-log.md was changed by commit 1c7d252
  (one line deleted) and contains pre-existing long dash
  characters. I verified all 11446 added lines in the batch 2/3
  diff contain 0 long dash characters, so nothing was added, but
  the blanket claim as worded is false for that one file. The
  accurate claim is "no long dash added".

### M2. Remote branch count arithmetic is off by one in one place

- Batch 3 task 1 section says "32 ref (main, origin/HEAD, 30
  remote branch)". The scrub plan section says "31 remote branch".
  The repo has 31 remote-tracking branches (30 non-main plus
  origin/main) plus origin/HEAD. The audit doc itself says 31
  branch tips, which is right. The "30 remote branch" figure is
  wrong by one.

### M3. MCP doc per-test timing does not match my re-run

- docs/mcp-server.md says each fake backend test takes about
  80-90 ms including server spawn, suite about 1.4 s.
- My re-run: 12 tests OK in 2.698 s, about 225 ms per test. The
  agent's own first run was 6.373 s and the second 1.372 s, so
  timings move a lot with load (council agents were running
  during my re-run). Load-dependent, not a fabrication, but the
  doc states the numbers without noting load sensitivity.

### M4. Committed results.json times do not match the report's quoted times

- The report quotes the agents' per-test times for batch 2 and
  batch 3. The committed results.json files hold the
  coordinator's later re-runs instead (batch 2: 9/10, wall 31626
  ms; batch 3: 8/10, wall 32968 ms), with different per-test
  times. The report discloses the re-runs, so nothing is hidden,
  but a reader comparing the files to the report will find
  different numbers with no note in the files explaining which
  run they are.

### M5. AT-SPI probe small issues

- tests/atspi_probe.py: counter_before is computed (find text "0")
  and never used; find() for role "text" name "0" is unlikely to
  match the fixture's "Counter: 0" paragraph.
- find_app logs a "desktop False" line on every 1 s poll
  iteration, up to 30 noise lines per failed run.
- do_type_keysyms sends keysyms without verifying focus. The
  report's phrase about an "Action activate with STATE_FOCUSED
  True" check does not appear in the code.
- The probe has no offline self-test mode, unlike the clone2
  prototype it was reviewed against. That is exactly what makes
  it unreproducible without a live Firefox and bus (see U2).

## Verified correct (survived the hunt)

- Token numbers recompute exactly against the current tree:
  catalog 7292 chars, 1823.0 estimate; "dom locate" 90.2, saved
  1732.8; "session" 251.0, saved 1572.0; "polygon" 59.5, saved
  1763.5. search "dom locate" returns zen_dom first. describe
  zen_dom is 598 chars with entry points.
- Test counts: codemode 40 tests (19 new plus 21 old), all pass;
  MCP 12 tests, all pass; Shayxo contract 17 tests, 6 fail,
  confirming the audit. content_node_test 16 checks, 0 failures.
  Bridge Python suite 16 tests, all pass.
- File counts: 37 files in each of clone1-batch2 and clone1-batch3.
  Clip mp4 is 120176 bytes and ffprobe says 10.000000 s. Batch 2
  lib/server.mjs has HTTP Range 206 support and mp4/vtt MIME
  types. Step counts in every README numbered list match the
  report (batch 2: 36, 35, 35, 36, 36, 40, 27, 40, 24, 40;
  batch 3: 20, 19, 19, 19, 20, 17, 17, 16, 12, 20), except the
  t10 batch 2 summary sentence (see W5).
- Todo audit: 92 E plus 15 W plus 4 N equals 111 rows. Spot
  checks pass: overlay-flicker-work-log-20261121.md does not
  exist; Daemon._ensure_native exists nowhere in scripts/ (only
  named in the todolist itself); all 10 cited commits exist;
  blame commits 2045020 (2026-11-18) and 3f29fe3 (2026-11-19)
  exist.
- Personal audit: 71 name lines in 45 files at 1c7d252 recomputed
  exactly (66 short form plus 5 diacritic form), and the doc's
  own list sums to 71 lines and 45 files. Email at 25 branch tips
  was correct at audit time (commit 6ce5a75 still carries it);
  today it is 24 because coord-clone2-setup tip c936fcd moved
  past the fix. Scrub plan gmail.com mentions: 5. Audit doc: 2.
- PR #1 review: all six file line counts at 6ce5a75 recompute
  exactly (394, 261, 386, 383, 346, 26). Issues 1 and 2 confirmed
  in the code at that commit. Fixture is 717 bytes. Trial merge
  of 6ce5a75 into 1c7d252 is clean (re-verified by me in a scratch
  worktree, removed afterwards).
- Bug 2087495 verified on Bugzilla: RESOLVED FIXED, 161 Branch,
  inverted IsTextRole() guard, exactly as the AT-SPI doc says.
- Firefox 160.0.1 verified with --version; tarball exactly
  90943956 bytes. Main had 432 commits at 1c7d252. The scrub
  plan's 431 rewritten-count reasoning is sound (a46b3c68 is a
  4073-line sync, only 1c7d252 becomes empty after replace-text).
  Zero tags on the repo. The email fix commit 1c7d252 deletes
  exactly 1 line.
- RUN-LOG-20261121.jsonl: 16 lines, all valid JSON. Committed
  batch 1 results.json matches the report (10 passed, wall 41534,
  per-test times identical, stderr empty, failures empty).
- Snippets registry programs are byte-identical to the four .py
  files. No full email address in any new file. No short or full
  name form in any new deliverable file except coord files quoting
  the assignment. No long dash in any of the 11446 added lines.
- MCP no-browser check verified by me: session_start fails clean
  in 0.011 s with a clear error and isError true (the doc says
  about 0.15 s; mine was faster because no geckodriver exists at
  /tmp/geckodriver at all).

## What I ran (my own numbers, 2026-11-21)

- python3 -m unittest tests.test_codemode_search
  tests.test_codemode: 40 tests, OK, 0.104 s suite.
- python3 tests/test_mcp_server.py: 12 tests, OK, 2.698 s.
- python3 -m unittest tests.test_glass_shayxo_contract: 17 tests,
  6 failures.
- node tests/realistic/clone1/run_all.mjs: 8 passed, 2 failed
  (t07, t10, download.saveAs canceled), wall 32211 ms.
- node tests/realistic/clone1-batch2/run_all.mjs: 10 passed,
  0 failed, wall 44193 ms.
- node tests/realistic/clone1-batch3/run_all.mjs: 10 passed,
  0 failed, wall 39500 ms.
- node tests/webext-native-bridge/content_node_test.mjs: 16
  checks, failures 0.
- python3 -m unittest tests.test_webext_native_bridge: 16 tests,
  OK, 7.613 s.
- Chromium textarea test with the exact type() JS: input OK,
  textarea TypeError Illegal invocation, contenteditable
  TypeError Illegal invocation.
- MCP oversized line test: 9 MB line, server exit code 1,
  ValueError at mcp_server.py line 581.
- MCP no-browser session_start: 0.011 s, clean isError.
- ffprobe clip.mp4: duration 10.000000 s.
