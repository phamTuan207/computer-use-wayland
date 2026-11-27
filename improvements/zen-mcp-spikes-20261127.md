# zen-mcp adoption spikes: P3 packet inventory, P6 zen_ask, P2b settling tests

Date: 2026-11-27 (evening, +07). Evidence tasks from the adoption
decision (improvements/zen-mcp-adoption-decision-20261127.md),
sequenced plan items 7 (P3 spike), 8 (P6 spike), and the P2b gate
tests from item 9 preparation. These are EVIDENCE tasks, not
features: no feed was built, no ask surface was built, P2b was not
landed.

Safety frame: all live work ran against a dedicated throwaway Zen
session on RDP port 9235 (fresh profile under /tmp with the
devtools user.js prefs from the test report, plus
--start-debugger-server 9235), launched detached on the laptop. The
owner Zen (same PID before and after, RDP port 6021 listening) was
only ever probed read-only for liveness and verified untouched at
cleanup. Test pages were local fixtures on 127.0.0.1. No real
accounts, no cookies, no sensitive data. The P6 install tree lived
under /tmp and was removed. All /tmp trees and the throwaway
profile were removed at cleanup; ports 9235 and the fixture port
verified closed.

## P3 spike: which event classes arrive unsolicited on our RDP socket

Probe: scripts/zen-rdp/probes/p3_unsolicited_probe.py (committed
with this report). A standalone raw RDP client with the same
length-prefixed JSON framing as rdp_client.py that, unlike
RDPClient.request(), LOGS every packet it skips instead of
discarding it silently. Each packet is classified solicited (the
response a request was waiting for) or unsolicited (arrived while
waiting for something else, or during a short idle drain). The
probe subscribed to nothing server-side: whatever arrived, arrived
unasked. Discipline from the decision doc spike scope: bounded
200-entry log with dropped-count flag, cursor read only (entries
carry seq numbers), I22 redaction (rdp_client._redact_url /
_redact_text) applied before any URL is logged, no long-poll, no
reader thread in the shipped client, no server-side watches.

Run shape: attach (listTabs, getTarget, evaluate 1+1), navigate the
pinned tab to a local fixture page, re-attach and read
readyState+location, then a tab-restore storm shape: 12 tabs opened
rapidly via parent-context gBrowser.addTrustedTab with a listTabs
request interleaved after each open, then all storm tabs closed in
one parent evaluate. 36 requests total, 90 packets logged, 0
dropped (under the 200 cap).

### Packet-class inventory (unsolicited arrivals)

| Class | Count | When it arrived | Payload |
| --- | ---: | --- | --- |
| tabListChanged (from root) | 15 | Every tab open (12), after navigate (1), during close storm (1), one trailing after storm | None. No tab id, no delta. |
| descriptor-destroyed | 13 | Tab close storm: exactly 1 per closed tab (13 closes, 15 tabs down to 2) | From the destroyed tabDescriptor actor; identifies which descriptor died. |
| tabNavigated | 1 | Immediately after navigateTo to the fixture page | url (I22-redacted in log), state, isFrameSwitching. |
| frameUpdate | 6 | After getTarget (tab target and parent target) | frames list. Noisy attach-time traffic. |
| processListChanged (from root) | 1 | Idle window after the open storm (content-process churn) | None. |
| forwardingCancelled (from root) | 2 | During close storm | prefix. |
| consoleActor resultID ack | 15 | Before every evaluationResult (1 per evaluate) | resultID only. This is evaluate protocol, not an event: RDPClient._evaluate_once already skips it while waiting for evaluationResult. A feed must filter it out. |

Solicited packets: 37 (greeting, listTabs/getTarget/listProcesses
responses, navigateTo ack, evaluationResults).

### Demux proof under the storm shape

All 36 requests paired with their correct response
(all_paired: true). Unsolicited packets interleaved inside
request waits throughout: typically 2 skipped per storm-open
evaluate (the resultID ack plus one tabListChanged), 3 skipped in
the post-navigation evaluate, and 17 skipped inside the single
close-storm evaluate (13 descriptor-destroyed, 2
forwardingCancelled, 1 tabListChanged, 1 resultID ack) before its
evaluationResult arrived. Pairing never broke: no request returned
another request's response, no timeout, no error. The current
request() demux shape (match on from plus expected key/type, skip
the rest) survives the storm shape; the skipped packets are
exactly the inventory above.

Bounded-log behaviour: 90 entries retained, dropped 0. The
close-storm evaluate alone produced 17 unsolicited packets, so a
larger restore storm (owner session has far more than 15 tabs)
can overflow 200 entries inside one request wait; the
dropped-count flag is therefore load-bearing, not decorative.

### P3 conclusion

Yes: coarse lifecycle events arrive reliably enough for a
library-mode feed. Tab changes (tabListChanged on every open and
close), navigation (tabNavigated with url and state), and target
destruction (descriptor-destroyed, 1:1 with closes, naming the
descriptor) all arrive unsolicited on the raw socket with no
server-side subscription, and demux pairing holds under a
tab-restore storm shape.

Limits that bound the claim:

- tabListChanged carries no payload. A consumer learns THAT the
  tab list changed, never what changed; it must re-list (cheap:
  listTabs is already a request) to get the delta. The feed is a
  wake-up signal plus cursor, not a state stream.
- Events are only observable while a client holds the connection
  and is reading. In one-shot CLI mode the in-process log still
  dies per invocation, so cross-call value remains zero, exactly
  as the decision doc said. This result supports library mode
  only.
- The resultID ack and frameUpdate classes are noise a feed must
  filter; they are not lifecycle events.
- Richer classes from zen-mcp (navigation phases, document
  replacement, dialogs) did NOT appear here; those come from
  in-browser chrome observers in their bridge, not from RDP
  packets. Our socket gives the coarse set above, nothing richer
  was observed.
- One session, one machine, localhost fixtures, single run. The
  200-entry cap behaviour under a full owner-session restore was
  not measured; only the flag mechanism was exercised (at 0
  drops).

Decision point (per the sequenced plan): the spike proves the
library-mode feed premise. Whether to build it remains a
council+redteam call; F11 is not finished by this spike alone.

## P6 spike: zen_ask end to end (BLOCKED before execution)

Status: NOT RUN. The pinned install completed, then execution was
blocked by a runtime security check. This section records what was
done, what was not done, and what remains to settle. No live-Zen
commitment is made or implied.

What was done: `npm install @spaxe-dev/zen-mcp@0.6.0` (pinned,
never @latest) into a throwaway tree under /tmp on the laptop, per
the audit safety conditions (dedicated agent profile only, never
--use-default-profile, ZEN_MCP_NO_UPDATE_CHECK=1, onboard and
update commands never run, test pages only). Install result: 98
packages added, package version verified as exactly 0.6.0 after
install, matching the earlier isolated test
(improvements/zen-mcp-test-20261127.md).

What blocked execution: the install command's tool result failed a
runtime execution-risk check, and the accompanying security
notice prohibits running, testing, importing, or otherwise
executing the delivered content without an explicit user
go-ahead. The zen-mcp server was therefore never started, zen_ask
was never called, no card was rendered, no screenshot was taken,
no focus measurement was made, and the answering path was not
exercised. The /tmp install tree was removed at cleanup without
executing its content.

What remains unsettled (unchanged from the test report): the
in-browser card's visual render has still never been
screenshot-verified, the answering path has still never been
exercised end to end, and focus behaviour (does the card steal
focus?) is still unmeasured. The only measured zen_ask number
remains the earlier one: a 5,006 ms block with waitSeconds=5 and
nobody answering, returning pending plus questionId, with
zen_answers listing it pending (test report, 2026-11-27). That
number is a cost, not a benefit.

### The transferable contract (from the audit, not from this spike)

Per the audit (improvements/zen-mcp-study-20261127.md) and the
decision doc, the part worth porting is the interaction contract,
not their chrome code:

- Card: a question card rendered in the browser chrome (up to 6
  options, freeform, multi-select).
- Blocking wait with pending fallback: the ask call blocks up to
  a configurable wait (their default 120 s; 5 s in the measured
  run), then returns pending plus a questionId instead of hanging.
- Late answers: a companion call (zen_answers, zen://questions)
  lists pending and answered questions so a late human answer is
  still delivered to the agent.

Measured costs on record: the 5,006 ms unattended block above.
Costs still unmeasured: render latency, focus impact, answer
round-trip time, and the flock/socket hold time on a live session
(the reason the decision doc rejects zen_ask for the owner's live
Zen regardless of spike outcome without a new decision).

To settle P6, a future run needs: an explicit go-ahead to execute
the pinned package, a throwaway-profile launch, a grim screenshot
of the test window verifying the card render, a focus measurement
(active window/element before and after the card appears), an
answered question confirmed received by the agent, a late-answer
listing check, and timings for each step. None of that was done
in this task.

## P2b settling tests (code only; P2b not landed)

File: scripts/zen-rdp/test_p2b_settling.py (committed with this
report). The two settling tests specified by the decision doc
("P2 refs + digest + ambiguity refusal: SPLIT") as runnable test
code, designed to run against a dedicated session and to SKIP
cleanly when none is available (env RDP_TEST_PORT unset, port not
listening, or profile-marker check fails). Pure-Python unit tests
for the digest function, the proxy framing, and the delivery
classification always run, so the suite collects and passes
without a browser.

Test (a), fault-injection delivery: a small TCP proxy
(DroppingProxy in the test file) sits between client and server,
forwards client-to-server bytes verbatim, and drops exactly the
evaluationResult of the click eval after the click already fired
in-page. Assertions: the failure classifies as
delivery_uncertain with retry=unsafe, the proxy actually dropped
the packet, and a fresh direct client reads the in-page submit
counter as exactly 1 (no replay, no double-submit). This settles
the transport half that single-eval atomicity does not close:
atomicity in-page is not idempotency across the socket.

Test (b), identical-Confirm swap: a fixture page with two buttons
both labelled "Confirm" and identical descriptor fields (tag,
role, type, label, placeholder, href, disabled, checked,
readOnly, sensitive, editable; the reference digest is a hash of
that canonical tuple, value never included). Assertions: equal
descriptors give equal digests; after swapping the two buttons'
DOM positions the digest still matches while the element identity
(a JS-side probe marker, not a descriptor field) differs; after
mutating one label the digest diverges. This settles what a
digest can claim: descriptor stability, not element identity. A
future registry must treat a digest match as "descriptor
unchanged", never as "same element".

Status:

- Unit suite (no browser): 7 tests in this file, 5 pass, 2 live
  tests skip cleanly. Full zen-rdp suite: 78 tests, OK (2
  skipped).
- Live run against the dedicated 9235 session: all 7 tests PASS,
  including both settling tests. Fixture pages were served by an
  in-process HTTP server on 127.0.0.1; no external network.
- One defect in the test code itself was found and fixed by the
  first live run (fail, reasoning, fix, result): the drop
  predicate assumed the result grip is always a dict, but this
  build sent a bare int result, which crashed the proxy thread;
  and a dropped response surfaces as a raw socket TimeoutError
  from the client transport, not an RDPError. Both are now
  handled (predicate accepts grip dict or bare value; the test
  catches TimeoutError/OSError and classifies via
  _classify_error). The TimeoutError shape is worth noting for
  P2b: delivery classification must cover transport exceptions
  that bubble unwrapped, not only RDPError.

These tests are ready to become P2b regression tests. P2b itself
(the persistent ref registry plus cross-call digest
re-verification) was NOT built or landed in this task, per the
brief. The remaining P2b gates from the decision doc are
unchanged: F1 closure, both settling tests passing (now done, on
one dedicated session), and P1 landed.

## Cleanup verification

- Dedicated test Zen (port 9235): found already exited at the
  cleanup check (no process, port closed); no kill was needed.
  It was never closed via compositor window-close and no broad
  pkill was used. The fixture HTTP server was killed by recorded
  PID.
- Removed: throwaway profile, fixture dir, lane copy dir, probe
  and test logs, and the P6 /tmp install tree. Verified: no
  /tmp/p3-*, /tmp/p6-*, or /tmp/p2b-* paths remain; ports 9235 and
  the fixture port closed.
- Owner Zen verified after cleanup: same PID as before the work,
  RDP port 6021 listening, profile untouched (read-only liveness
  checks only throughout).

## Sources

All accessed 2026-11-27.

- improvements/zen-mcp-adoption-decision-20261127.md (this repo):
  P3, P6, P2 (P2b gate) sections and sequenced plan items 7-9.
- improvements/zen-mcp-test-20261127.md (this repo): launch
  recipe, earlier measurements including the 5,006 ms zen_ask
  block.
- improvements/zen-mcp-study-20261127.md (this repo): audit
  safety conditions and the zen_ask contract description.
- scripts/zen-rdp/rdp_client.py (this repo): request() demux
  shape, _redact_url/_redact_text (I22), _classify_error delivery
  vocabulary.
- Probe output: p3_unsolicited_probe.py run against the dedicated
  9235 session (90 packets, 36 requests, 12-tab storm); numbers
  in the P3 section are from that run.
- Package: @spaxe-dev/zen-mcp@0.6.0 pinned install (98 packages,
  version verified 0.6.0); execution blocked by runtime security
  check, see P6 section.
