# W-ZENPROOF2-FIX redteam review (independent attack)

Reviewer: Redteam, independent (not W-ZENPROOF2-FIX, not
COORD-CLICK-9, not the council reviewers). Report goes to Muse
tong, not directly to Pham Tuan. No live Zen tab was opened,
navigated, or deleted. No fix file was edited. No reviewer was
spawned by me. No em dash or en dash anywhere in this file.
No personal info.

## 0. Verdict: GO WITH CONDITIONS

The fix closes the observed run 2 incident (the persistent
not-current state), the 16 tests pass on my independent re-run,
and the only two DELETE sites are the open handler and cmd_close.
But I found a reproducible path (F1) where the same damage
(owner tab navigated, then deleted by cleanup) still occurs, via
a race the fix does not close. The trigger has no realistic actor
in this deployment, so this is not AMEND, but the hardening is a
few lines and the consequence is the exact incident the fix exists
to prevent, so it must be applied (or explicitly accepted in
writing) before the live proof. F2 and F3 are the other
conditions, listed in section 5.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:16 +07, T+0m: task received. Read the fix log and the 4
  commits.
- 20:18 +07, T+2m: read zen-tab.py, run2.py, the test file.
- 20:20 +07, T+4m: read zen_dom.py list_tabs, _try_restore,
  _verify_selected, tab_at; zen_backend.py _resolve_target,
  dom_observe, dom_act; the run 2 incident log.
- 20:22 +07, T+6m: re-ran the test suite, 16/16 OK. Verified
  the working tree is clean for the fix files.
- 20:23 +07, T+7m: repro F1 (TOCTOU) confirmed, owner tab
  deleted by cleanup. Repro F2 (backend first match plus index
  shift) confirmed, both parts.
- 20:25 +07, T+9m: review written, committing.

## 2. What I verified as correct

The fix does close the observed run 2 incident. The incident
regression test (new tab never current plus explicit select
fails) proves open raises before any navigate or DELETE, the
owner URL is unchanged, zero deletions, the owner tab is still
current, and the new tab is left as an un-navigated about:blank.
I re-ran the suite myself: Ran 16 tests in 0.002s, OK.

The two DELETE sites are the only ones. Grep over the driver,
the runner, zen_dom.py, zen_backend.py, and code_exec.py finds
DELETE /window only at zen-tab.py:286 (open exception handler)
and zen-tab.py:333 (cmd_close). There is no DELETE in run2.py.

The handler is correct for every exception raised after a
successful navigate on the right tab (H1 mismatch, readyState
not complete, no #msg-input rect, viewport gate): the current
tab IS the scratch tab, so DELETE is correct. When _url raises,
cur_url is None and nothing is deleted (fail-closed).

The pre-check refuses when a fixture tab already exists, so a
stale scratch tab cannot make URL identity ambiguous at open
time. _find_in_scan refuses on duplicate URL matches (proven
by repro F2 part A, first half). _switch verifies the switch by
handle after POST (zen-tab.py:148-157). _restore_original never
guesses: a missing or ambiguous original URL is reported with
original_missing or original_ambiguous flags and the current tab
is left as Zen activated it.

The fixture static H1 is 'Clone thread'
(tests/two_vision_fixture.html line 12) and the JS sets it to
'Clone zen thread', so the H1 gate correctly distinguishes a
loaded clone from a page whose JS never ran.

## 3. Findings

### F1 (HIGH): TOCTOU between the (c) current check and POST /url; the handler identifies the scratch tab by URL only

Files and lines: zen-tab.py:188-200 (the (c) check), :203-204
(POST /url navigate), :216-220 (post-navigate URL check),
:221-229 (H1 and readyState checks), :273-292 (open exception
handler), :286 (DELETE in the handler), run2.py:539-575
(cleanup calls cmd_close by TARGET and original_url).

Mechanism. Fix (c) verifies current == new_handle, then POST
/url navigates the current tab. The check and the navigate are
two separate HTTP calls. If the current tab changes in between
(an external switch, another Marionette session, or a Zen focus
change), POST /url navigates the WRONG tab. The post-navigate
checks cannot catch it: if the wrong tab is the owner tab, it
now shows the fixture URL (the URL check passes), the fixture
JS runs there (the H1 check passes), and readyState is complete
(the readyState check passes). The open returns ok. Then the
runner's cleanup calls cmd_close(TARGET, original_url), which
finds the owner tab by the fixture URL and DELETEs it. The
restore then fails with original_missing because the owner URL
is gone.

The handler has the same hole. It deletes when the current
tab's URL contains the substring. It never checks the current
handle against new_handle. So an owner tab navigated to the
fixture URL IS the fixture tab by the handler's own definition.
The URL identity is circular: it cannot distinguish the
scratch tab from an owner tab that was navigated to the fixture
URL. The fix does not re-verify the current handle after the
navigate either: after POST /url it reads _url, H1, and
readyState, but never _current(z) == new_handle.

Repro. /tmp/redteam-repro-f1.py (a FakeSession subclass that
flips current back to the owner tab inside the POST /url call,
after the (c) check passed; select_new=False,
select_works=True, so the explicit-select path is taken).
Output, verbatim:

- focus reverted to owner tab just before POST /url (after the
  (c) check passed)
- cmd_open returned ok = True, selected_by = explicit-select,
  open url = file:///home/james/computer-use-wayland/tests/
  two_vision_fixture.html?clone=zen
- owner tab url now = file:///home/james/computer-use-wayland/
  tests/two_vision_fixture.html?clone=zen
- new tab url now = about:blank
- cmd_close ok = True, result = {'ok': True, 'count_before': 3,
  'count_after': 2, 'original_missing': True,
  'original_ambiguous': False, 'current_title': '',
  'current_url': 'https://example.com/'}
- tabs after close = ['https://example.com/', 'about:blank'],
  owner tab still present = False, deleted urls =
  [file:///home/james/computer-use-wayland/tests/
  two_vision_fixture.html?clone=zen]

So the open reports success on the owner tab, and cleanup
deletes it. That is the run 2 damage, reproduced through the
fix.

Severity. The trigger is a window of about one HTTP round-trip
and has no realistic actor in this deployment: the owner is
away, a single lane runs, no other Marionette session touches
Zen, and Zen does not auto-switch tabs. So this is NOT the
observed incident (which was a persistent wrong state, now
caught). But the consequence is the exact incident the fix
exists to prevent, and the hardening is cheap. Hence GO WITH
CONDITIONS, not GO and not AMEND.

Hardening (condition C1). After POST /url, verify _current(z)
== new_handle in addition to the URL check. In the open
exception handler, delete only when the current handle ==
new_handle AND the URL contains the substring (new_handle and
current_before are both in scope in cmd_open). Add the F1 repro
as a regression test: a fake that flips current between the
verify read and the navigate must end with zero deletions and
the owner tab intact. If the coordinator judges the race
un-triggerable and wants to proceed without the hardening, that
must be recorded as an explicit written acceptance, not a
silent skip. Note the hardening turns a potential owner-tab
delete into a recoverable navigate-away at worst: the tab
content is still changed, but the tab survives and the chat
survives server-side. The WebDriver protocol offers no atomic
verify-and-navigate, so a residual risk remains in principle;
the hardening narrows it to detection plus damage limitation.

### F2 (MEDIUM): backend _resolve_target picks the FIRST match and uses a handle-list index from a second scan; the fix's "never pick blindly" does not extend to the backend

Files and lines: scripts/zen_backend.py:189-208
(_resolve_target), :248 (dom_observe calls it), :471 onwards
(dom_act does not re-resolve the tab), scripts/zen_dom.py:
624-640 (tab_at), run2.py:476-490 (phase 4 send, no re-switch
and no snapshot URL gate), :431-475 (phase 3 switch plus probe
gate).

Mechanism A, first match. _resolve_target iterates list_tabs
and returns the FIRST tab whose title, url, or handle contains
the target substring. It never checks for duplicates.
zen-tab.py's _find_in_scan raises on duplicates. Same tab list,
two different answers. A duplicate fixture tab (for example a
stale ?clone=zen2 tab, which also contains the substring
'two_vision_fixture.html?clone=zen') makes the backend silently
operate on the stale tab.

Mechanism B, index shift. _resolve_target finds the match at
index i in scan 1, then calls session.tab_at(i), which does a
SECOND scan and returns the entry now at index i. If a tab
closes between the two scans, the index shifts and tab_at
returns a different tab. _resolve_target returns it without
re-checking that it matches the target.

Why the runner is only partly protected. Phase 3 does
tab('switch', TARGET) first (refuses on ambiguity) and gates
the probe snapshot URL via parse_probe_line, so a duplicate is
caught before the probe. But phase 4 (the send) does NOT
re-switch and does NOT gate the snapshot URL; it trusts the
phase-3 switch from a previous process. dom_observe resolves
the target for the snapshot metadata only and does not select
the tab; dom_act dispatches input into the CURRENT tab without
re-verifying it is the snapshot's tab. So a duplicate fixture
tab appearing between phase 3 and phase 4 makes the send go to
the wrong fixture tab, and the assert (bubble text) would still
pass there, giving a possible false PASS.

Consequence. Wrong-fixture-tab send, possible false PASS. NOT
an owner-tab write: an owner tab's title, URL, or handle cannot
contain the fixture substring unless the owner opened the
fixture. So this is a correctness hole, not a safety hole of
the same class as F1.

Repro. /tmp/redteam-repro-f2.py (stub session with list_tabs
plus tab_at, calling the real ZenDomBackend._resolve_target).
Part A output, verbatim: _find_in_scan RAISED: URL
'two_vision_fixture.html?clone=zen' matches 2 tabs, refusing
to pick one; _resolve_target returned url =
file:///home/james/computer-use-wayland/tests/
two_vision_fixture.html?clone=zen2; that is the STALE
?clone=zen2 tab: True. Part B output, verbatim: churn: fixture
tab closed between scans; _resolve_target returned url =
https://example.com/; that is example.com, NOT the fixture:
True; no re-check that the returned tab matches: True.

Hardening (condition C2). In run2.py phase 4, call tab('switch',
TARGET) immediately before the send program, and print plus
gate the SEND_PROGRAM snapshot URL with the same target check
as the probe (parse_probe_line). That closes the send's
cross-process trust. The stronger option is to make
_resolve_target refuse on ambiguity (a backend change); the fix
explicitly chose no backend change, so the runner-side gate is
the condition, and the backend first-match should be recorded
as a known limitation.

### F3 (MEDIUM): FakeSession does not model several real Marionette states, so fail-closed paths are unproven

Files and lines: tests/test_zenproof2_fix.py FakeSession.list_tabs
(a pure read, no switching, no restore), scripts/zen_dom.py:
641-713 (list_tabs switches through every tab, restores the
original, can produce error entries, can stop on a hang),
:597-608 (_try_restore does not verify the switch took effect,
unlike _verify_selected at :610-622).

Gaps.

(a) Error entries. Real list_tabs can return {"handle": ...,
"error": ...} entries with no URL (a tab whose title or URL
read fails). _find_in_scan skips them. The fake never produces
them. Consequence: if the existing fixture tab is unreadable,
cmd_open's pre-check passes (no fixture URL found) and a
second fixture tab is opened; cmd_close reports already_closed
while the scratch tab still exists (the runner's
count_restored flag would detect the count mismatch, but the
tab is left open).

(b) Scan restore failure. Real list_tabs restores the original
tab in a finally block, and _try_restore does NOT verify the
switch took effect (no _verify_selected call). If the restore
POST returns success but the current tab stays on the
last-scanned tab, list_tabs returns normally with the wrong tab
current. The fake's list_tabs never switches, so this is
untested. In cmd_open the (c) check mitigates it (it re-reads
current and compares to new_handle). In cmd_list it is NOT
mitigated: cmd_list returns 'current' from the scan, and the
runner's phase 1 captures original_url from the entry matching
that current handle, so a silent restore failure makes the
runner capture the WRONG owner tab's URL as original_url. No
tab is deleted, but the restore target is wrong and cleanup
would report original_restored True for the wrong tab.

(c) Evaluate is not fully tab-aware in the fake. readyState
always returns 'complete' and metrics and rect always return
fixture values regardless of the current tab, while the H1 read
is tab-aware. So the fake cannot catch a case where the driver
evaluates in the wrong tab and passes on canned values. (The F1
repro works around this because the fake's POST /url actually
navigates the owner tab, so the H1 read is genuinely from the
fixture page.)

(d) Handle-list churn. _scan fetches handles twice (list_tabs
internally, then _handles after), so the entries and the full
handle list are from different moments (see F4). The fake never
models churn.

Hardening (condition C3). Extend FakeSession to model (a) an
error entry for the fixture tab and (b) a list_tabs whose
restore leaves the wrong tab current, and add tests proving
the pre-check, close, and handler behavior in those states.
This is a test-coverage condition; the code paths are
fail-closed by reading, but unproven.

### F4 (LOW): _scan "same moment" claim is inaccurate

File and line: zen-tab.py:88-97 (_scan returns z.list_tabs(),
_handles(z)).

list_tabs fetches the handle list at its own start, switches
through every tab (which takes time), and restores; _handles
fetches the list again after list_tabs returns. So the entries
and the full handle list come from two different moments,
separated by the whole scan. The docstring says "One scan only,
so the entry and the handle list come from the same moment."
That is not true.

Consequence: if a tab opens or closes during the scan,
_full_handle raises 'no handle starts with prefix' and the
command fails (fail-closed, spurious refusal). Not a safety
hole. Fix the docstring, or fetch the handle list once and pass
it through. Note only.

### Notes (not findings)

N1. The explicit select is tried once, with no retry. A
transient select failure causes a refusal (fail-closed).
Availability choice, not a hole.

N2. The substring 'two_vision_fixture.html?clone=zen' also
matches '?clone=zen2' (a different clone). The pre-check
refuses on any match, so a ?clone=zen2 tab blocks the run
(fail-closed, availability). Not a safety hole.

N3. Handle 8-char prefix collision is negligible (random
UUIDs, about 2^-32 per pair). _full_handle raising on
ambiguity is the correct fail-closed behavior.

N4. The handler's _switch(z, current_before) after a DELETE is
best-effort and swallowed; current_before is captured in the
same session, so it is valid there. No issue.

## 4. What I could not break

The observed run 2 incident (persistent not-current state) is
closed: the (c) check plus the incident regression test prove
open refuses before any navigate or DELETE. I re-ran the suite
myself: 16/16 OK.

The handler is correct for every exception raised after a
successful navigate on the right tab. The pre-check,
_find_in_scan ambiguity refusal, _switch handle verification,
and _restore_original no-guess behavior are all correct as
written. The only two DELETE sites are zen-tab.py:286 and
:333.

## 5. Conditions for GO (all before the live proof)

C1 (F1). Apply the post-navigate handle re-check plus the
handler handle check, and add the F1 repro as a regression
test; re-run the suite. Or record an explicit written
acceptance of the residual race, with the reasoning that no
actor can trigger it in this deployment.

C2 (F2). In run2.py phase 4, re-switch to the scratch tab by
URL immediately before the send, and print plus gate the
SEND_PROGRAM snapshot URL with the same target check as the
probe. Record the backend first-match as a known limitation.

C3 (F3). Extend the fake to model error entries and a
silently-failed scan restore, and add tests for the pre-check,
close, and handler in those states.

## 6. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received 20:16 +07, 22/11/2026. Branch todolist-push,
  repo ~/workspace/computer-use-wayland, HEAD at review start
  4dafe17.
- Commits reviewed: 6d751b9 (zen-tab fix), f0dd5ec (run2 fix),
  014938b (16 unit tests), 4dafe17 (fix log). Verified by git
  log and git show --stat for each commit.
- Test suite re-run 20:22 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 16 tests in 0.002s, OK.
  Working tree clean for the fix files (only the pre-existing
  dirty tests/realistic/clone1-batch3/results.json and untracked
  files from other workers, never touched).
- DELETE sites, grep 20:20 +07: only zen-tab.py:286 and :333.
  No DELETE in run2.py, zen_dom.py, zen_backend.py,
  code_exec.py.
- Repro F1, run 20:23 +07: python3 /tmp/redteam-repro-f1.py.
  Output quoted in full in F1 above. Result: cmd_open ok True
  on the owner tab, cmd_close deleted the owner tab, owner tab
  still present False, original_missing True.
- Repro F2, run 20:23 +07: python3 /tmp/redteam-repro-f2.py.
  Output quoted in full in F2 above. Result part A:
  _find_in_scan raises, _resolve_target returns the stale
  ?clone=zen2 tab. Result part B: _resolve_target returns
  example.com after the fixture tab closes between scans.
- Fixture read 20:22 +07: tests/two_vision_fixture.html line 12,
  static H1 'Clone thread'; JS sets 'Clone zen thread'.
- Repro scripts are not committed; they live in /tmp
  (/tmp/redteam-repro-f1.py, /tmp/redteam-repro-f2.py). Their
  outputs are quoted in F1 and F2 above.
- No live Zen tab was opened, navigated, or deleted. No fix
  file was edited. No reviewer was spawned.
- Review file: improvements/w-zenproof2-fix-redteam-review.md
  (this file). Commit hash in the report to Muse tong.
