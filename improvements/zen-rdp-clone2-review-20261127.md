# Independent review of scripts/zen-rdp/ (clone2, 2026-11-27)

Reviewer: clone2, independent of the landing lane. Review only: no
code was changed. Scope: branch fix-review-20261127 at 91547db1,
directory scripts/zen-rdp/ (rdp_client.py 1178 lines, rdp_smoke.py
225, test_scope_unittest.py 543, test_rdp_smoke.py 55,
test_rdp_client.py 93, README.md 116).

Method: full read of all six files; unit suites run on this machine
(test_scope_unittest 29/29 OK in about 0.5 s, test_rdp_smoke PASS);
two defect probes written against the repo's own FakeRDPTransport;
live runs of test_rdp_client.py and rdp_smoke.py against a real
browser on this machine (Firefox 160 with --start-debugger-server,
throwaway profile, local fixture page). The draft findings then went
through two council reviewers and one redteam, all independent; the
redteam re-ran everything, added its own probes, and ran the live
self-test four times. Corrections from that process are folded in
and marked where they change a claim.

## Verdict

The toolset is well built and its attach-time gates are genuinely
fail-closed: unscoped refusal, profile-marker refusal, raw-packet
refusal, parent-evaluate gate, single-drive lock, AND scope
semantics, lazy-tab refusal, and pinned re-attach that refuses the
selected-tab fallback all hold under test. The weaknesses are not in
the attach gates. They are in three other places: the error paths
(a page-controllable retry trigger and silent longString
corruption), run-time freshness (the guard checks a cached URL, and
the denylist is a nine-word substring net), and audit persistence
(the record of the biggest fence removals is volatile). One
intermittent live failure (navigate then wait_load timeout) was
observed and its mechanism demonstrated. Details below, severity
first.

## Findings

### F1 HIGH: page-controlled exception text triggers a second execution of an evaluate

evaluate() retries once whenever the raised RDPError text contains
the substring "noSuchActor" (rdp_client.py, _is_no_such_actor and
the evaluate retry). _evaluate_once embeds the page-controlled
exception text in that error string. A page that throws an error
whose message contains "noSuchActor" therefore causes the client to
re-attach and execute the same expression a second time before
raising. Proven three ways: clone2's fake-transport probe
(eval_count=2, retries=1), council 1's independent probe (same
numbers), and the redteam's live Firefox run, where a counter
expression ending in `throw new Error('noSuchActor: ...')` left the
counter at 2 while a control exception left it at 1.

Qualifications, all verified: the trigger text must land in the
first 400 characters of the stringified packet (the client tests
str(m)[:400]); realistic short messages do. The same retry is also
reachable through the longString path (a cross-actor error packet
containing the text during substring fetching re-executes the whole
expression). parent_evaluate has no retry and is not affected.
Severity is high, not moderate, for two reasons: the retried payload
is arbitrary agent JavaScript (the self-test itself performs DOM
writes and clicks, so double submit and double write are realistic),
and the drive report conceals it, because the action counter
increments only on the successful retry, so the report counts one
evaluate for two executions. The trigger string is printed in the
repo, so any page author can use it deliberately.

Related, same root: _navigate_send re-sends navigateTo to the
descriptor actor after ANY target-actor error, not only a
dead-actor error (redteam probe: a plain NS_ERROR_MALFORMED_URI
error produced two navigateTo sends, the second succeeding). If the
first send took effect before erroring, the tab navigates twice.

### F2 MODERATE: longString fetching silently corrupts results

_fetch_long_string checks whether a reply packet is from the
longString actor before checking whether it is an error packet, so
an error packet from the actor itself is consumed as the substring
reply. The failure shape is worse than a truncated string (this
corrects the draft): the failed chunk silently contributes empty
text and fetching continues, so the result is a shifted string with
a chunk missing (redteam probes: 12000 of 20000 characters returned,
head or middle missing, no error raised). Two adjacent gaps: the
assembled length is never checked against the grip's declared
length, and a silently short substring reply (no error) also passes
undetected (redteam probe: 10000 of 20000, no complaint). For a tool
whose evaluate results feed agent decisions (innerText and
outerHTML reads are the longString cases), silently shifted data
that looks like data is a real hazard, and it contradicts the
codebase's own fail-loud posture.

### F3 MODERATE: navigate pin race can strand recovery, and wait_load hides it

Demonstrated by the redteam with the repo's own fake transport, and
consistent with its one live failure in four self-test runs (the
other three passed; clone2's single run passed): if navigate()'s
trailing get_target() pins _pinned_url before listTabs reflects the
new URL, the pin keeps the pre-navigation URL. A later dead-actor
evaluate then cannot recover, because _reattach_pinned refuses with
"url changed, refusing re-attach" (retries=0), and wait_load
swallows that refusal and spins until timeout. Root tension: the
pin's URL check cannot distinguish "same tab navigated" from
"different tab at a shifted positional id", so a legitimate
navigation can make the pin unrecoverable. Under load the race
window widens, which matches the live failure occurring on a cold,
busy run.

### F4 MODERATE (partly a documented residual): the guard checks a cached URL

_guard_current checks scope and denylist against
self._current_tab, refreshed only by list_tabs() or get_target();
evaluate() never refreshes it. A tab that navigates itself after
attach (page JS redirect, link click, meta refresh) is then
evaluated against its old URL. Redteam demonstration, through the
guarded method itself with the denylist on: attach in scope, let the
tab navigate itself to a login URL, and evaluate() executes on the
credential tab. The landing report already lists "TOCTOU guard
snapshot" as an accepted residual; this review confirms the code
behaves exactly as that label says and shows the practical effect.
Any summary of this toolset that says "no scope bypass" without
this qualification is wrong, and the draft of this review initially
said it; the redteam removed it.

### F5 HIGH as a class, by construction: the credential denylist is a nine-word substring net

_url_matches is a case-insensitive substring or glob match against
nine English fragments (login, signin, sign-in, account, auth,
oauth, password, checkout, payment). Verified evasions: vocabulary
gaps (logon, sso, /session/new, non-English paths, an IdP on a bare
domain; redteam attached cleanly to /sso.html, /session, and an IdP
root with the denylist on); percent-encoding (/log%69n never matches
"login"; no normalization step exists); redirect targets are never
checked (navigate checks the literal destination string; a page
that 302s to an IdP loads the credential page, and navigate's tail
refresh swallows the resulting refusal after the page has loaded);
page content is never inspected. False positives run the other way:
"auth" matches "author", training operators to reach for approvals.
Scope URL patterns share the substring issue: pattern "example.com"
accepts https://example.com.attacker.test/ and a URL carrying
example.com in its query (both verified through Scope.matches). The
landing report lists "substring over-match" as an accepted residual.
None of this makes the denylist useless; it is a heuristic net, and
it should be described as one wherever the toolset is presented as
enforcing credential safety.

### F6 MEDIUM: the parent-evaluate audit does not reliably persist

The gate holds (no path reaches parent_evaluate without
allow_parent; council 2 verified). The record does not: only an
80-character expression prefix is stored, no results; a long
expression can front-load 80 benign characters so the prefix
misrepresents what ran. The record lives in memory and reaches disk
only when a drive report path was set, so a peval run without
--drive-report leaves no persistent trace that chrome JS ran. The
report also does not record that --allow-parent was enabled for a
session with no parent evaluates, nor that the port-owner check was
skipped via --allow-unmarked-test-attach. Two of the three big fence
removals leave no trace in the artifact meant to record fence
removals; only unscoped_test and denylist.disabled_via_flag are
recorded.

### F7 MEDIUM: bench combines the escape flags and is destructive

With --unscoped-test, bench attaches to the selected tab and
navigates it through about:blank, a local URL, and a real URL. Its
only identity fence is the operator-supplied marker; pass the owner
profile's marker and it runs on the owner profile and destroys the
selected tab's page state. Bench clients take no lock file and
write no drive report, so the run leaves no audit artifact. The
protection is procedural (flag name, README), not technical.

### F8 MEDIUM: the smoke runs with every fence down, by design, against the owner profile

run_smoke constructs the client unscoped, with allow_parent, the
denylist off, and even the unscoped warning suppressed. It evaluates
on the selected tab, runs three parent typeof evaluates, and then
navigates the selected tab to about:blank. Nothing in the tool
checks that the selected tab is a tasked or throwaway tab; the
README warning is the only control, which is exactly the kind of
brief-level rule RT-20 was created to stop relying on. The switch
procedure on the laptop did run it with a fresh tasked tab selected;
that discipline lives in the procedure, not the tool. Recorded here
as a known, calculated risk that deserves an in-tool guard (for
example, refusing when the selected tab's URL is not about:blank or
a new-tab page).

### F9 MODERATE: evaluation results are not correlated to their sender

Neither _evaluate_once nor parent_evaluate checks that an
evaluationResult packet came from the console actor it was sent to.
Worse, if a socket timeout fires mid-evaluate, a late
evaluationResult stays buffered and the NEXT evaluate call consumes
it as its own return value. There is no request/response correlation
in either evaluate path. In sequential use this is unlikely to bite;
under the timeouts that F3 shows do happen, a stale result returned
as fresh data is a silent wrong answer.

### F10 LOW to MODERATE: port-owner check is a hint, not an identity

check_port_owner fails closed on an empty marker and on a missing
pid, which is good. But the pid extraction regex matches any ss line
carrying ":<port>", including the peer column of an established
connection, so it can return a connecting process's pid instead of
the listener's (council 1 and council 2 found this independently).
The marker test is a cmdline substring, which any process mentioning
the profile path satisfies. The check also runs once before connect
with no post-connect binding to the verified pid. The refusal
message embeds the first 300 characters of the process cmdline,
which can carry profile paths into logs.

### F11 LOW: drive_report() has live side effects, including moving the pin

drive_report() (and therefore close() whenever a report path is
set) performs live list_tabs, get_target, and up to six probe
evaluates. get_target re-pins, so after a human navigation (the F4
scenario) merely closing the session silently moves the pin to the
new URL, defeating the pin's URL verification. The report-time guard
also appends to the refusal, hit, and approval lists, and the probe
increments the evaluate counter: generating the report mutates the
audit data the report contains. The report subcommand is therefore
not read-only, which its name suggests.

### F12 LOW: smaller confirmed items

- _open_parent falls back to the first listed process when none is
  marked isParent, instead of failing closed; inconsistent with the
  file's posture elsewhere.
- Approval keys are tried both as canonical tab ids and as URL
  patterns, with nothing tying a key to its intended kind
  (_approval_note). Exploitation needs a contrived key and URL, but
  the conflation is real.
- A scope config's credential_denylist_patterns replace the nine
  defaults wholesale; a one-pattern config silently drops the other
  eight, with no warning. (The reverse error is handled: an empty
  config list falls back to the defaults, so a config cannot
  accidentally disable the denylist.)
- If socket creation or the greeting read raises after the lock is
  acquired in __init__, the lock fd is never released and the lock
  file stays held for the process lifetime; this poisons library and
  bench-style reuse in the same process.
- parse_bind counts an [::1] IPv6-loopback listener as non-loopback
  and fails smoke check (f). Fail-closed direction, but a false
  failure for a legitimate bind; the test file covers [::] but has
  no [::1] case.
- list_tabs and the tabs subcommand expose every tab's URL and title
  regardless of scope. By design and documented, but the README's
  scoping language can be misread as covering reads; it does not.
- The drive report contains all tabs' URLs and titles (URLs can
  carry reset tokens and OAuth codes in query strings) plus approval
  notes verbatim, is written with default file permissions, and is
  printed in full to stdout by the report subcommand. Custody is
  assigned to the machine layer in the README; the tool offers no
  redaction or 0600 help.
- Enforcement is CLI-deep, not a sandbox: _send is unguarded and
  _internal_call is a plain attribute, so same-process embedding
  code can bypass the guards. Worth one sentence in the README so
  nobody mistakes the fence for an isolation boundary.

## Test coverage gaps

The suites pass, but their shape matters: the fake transport never
emits an evaluationResult with an exception grip and never emits an
error packet from a substring request, so 29/29 says nothing about
the two paths where F1 and F2 live. There is no NOT_CLEAN probe
test, no check_port_owner test, no wait_load test, and no [::1]
bind case. The landing report's "unit 29/29" is accurate and, on
its own, easy to over-read.

## Live evidence and its limits

Clone2 live run: test_rdp_client.py passed in full against Firefox
160 (attach, evaluate, CLEAN probe, navigate, DOM read and write,
JS click isTrusted=false). Redteam live runs: 3 of 4 passed, one
cold run failed at wait_load after navigate (mechanism in F3). The
smoke on Firefox passed checks (a) to (d) and failed check (e) with
exit 14, exactly as designed for a non-Zen browser.

Firefox evidence does not transfer to Zen specifics, and this
review does not claim it does: check (e) has only ever passed via
the laptop lane's RT-21 run; Zen's tab model (workspaces, pinned and
essential tabs, folder placeholder about:blank tabs, split view)
can change listTabs contents and selected-pick behavior; Zen is
built on an older Firefox base than 160, so packet shapes were
verified at the two ends by different lanes, not by this run.

## Recommendations (review output only; no code changed)

1. Make the noSuchActor retry match only protocol error packets for
   the held actor, never evaluationResult exception text; count
   every execution in the drive report, including retried ones.
2. In _fetch_long_string, check error before sender, and verify the
   assembled length against the declared length; fail loud on any
   mismatch or short read.
3. Let _reattach_pinned accept the pinned tab's own post-navigation
   URL when the descriptor lineage is continuous, or re-pin
   deliberately after a client-initiated navigate; stop wait_load
   from swallowing re-attach refusals silently.
4. Refresh the guard snapshot inside evaluate (one listTabs when
   the cached URL is older than the last action), or state the
   freshness bound in the README next to the scoping claims.
5. Describe the denylist as a heuristic net in the README; consider
   percent-decoding before matching and checking the post-redirect
   URL before the first evaluate after a navigate.
6. Record allow_parent enablement and unmarked-attach use in the
   drive report unconditionally; store full parent expressions (or
   their hash) rather than an 80-character prefix.
7. Give bench and the smoke an in-tool tab guard (refuse a valued
   selected tab), and give bench a lock file and a drive report.
8. Correlate evaluate replies to their console actor and drain or
   fail on stale results after a timeout.
9. Add the missing tests: exception-grip evaluate, substring error
   packet, NOT_CLEAN probe, check_port_owner, wait_load, [::1].

## Process record

Draft findings by clone2 (code read, 29/29 run, two probes, one
live pass). Council 1 (correctness) confirmed all ten draft
findings, independently reproduced F1 and F2 with the same numbers,
downgraded the _send claim to internal-only, and added F9, F10, and
the length-verification half of F2. Council 2 (security posture)
added the denylist evasion class (F5), the audit persistence gaps
(F6), the bench combination (F7), the smoke posture (F8), and the
report sensitivity items. Redteam re-ran everything, corrected
F2's damage shape, narrowed and widened F1 (400-character window,
longString reach, audit undercount, severity raised to high), broke
the draft's "passes in full" live claim (3 of 4, with the F3
mechanism demonstrated), and removed the draft's unqualified "no
scope bypass" claim (F4, F5). The verdict above is the converged
result of the three.

Clone2, 2026-11-27. English only. No personal information in this
document.
