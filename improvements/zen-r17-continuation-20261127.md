# R17 continuation: zen_live.py throwaway-profile proof, the Marionette pinned-dump error, and RDP vs Marionette coverage (clone2, 2026-11-27)

Scope: task R17 continuation for the Zen folder tool research
(improvements/zen-folder-tool-research-20261127.md). Three
parts: (1) run the live Marionette tool
improvements/zen-sidebar/zen_live.py against a real Zen on a
throwaway profile on clone2's own machine; (2) explain the
Marionette pinned-tabs dump error recorded during the R14
cleanup; (3) delineate RDP versus Marionette coverage after
the 2026-11-27 switch to RDP as the primary route.

Method: Zen Browser 1.24.3b (Linux x86_64, BuildID
20261118023529, on Firefox 160) extracted from the official
release tarball on this VM, launched under Xvfb (DISPLAY
only, no --headless flag) with
--marionette on a fresh throwaway profile. The stock tool was
run first, unmodified. Each failure was isolated in sequence,
with ground truth read from this build's own Marionette server
code inside the extracted omni.ja (server.sys.mjs,
driver.sys.mjs, evaluate.sys.mjs). A fixed copy of the client
was built up one fix at a time (copies v1 to v4, kept locally
with the full proof log) and the final copy ran introspect,
list (the pinned dump), pin and create-folder live. The other
seven subcommands share the fixed transport and prelude, but
their payloads were not run live. Coexistence and leaked-session scenarios were
run against the fixed client. The tool's unit suite was run
as shipped. All errors below are quoted verbatim from the
runs; timings are wall clock. No repo code was changed; the
fix list in section 4 is evidence for the integrating lane.
The draft then went through three council reviewers and one
redteam, all independent; their corrections (timing ranges,
build scoping of the D1 claim, sourcing of the switch facts,
and the BiDi boundary) are folded in.

## Verdict

The pinned dump works on Zen 1.24.3b, but not with the
shipped client. The stock zen_live.py fails deterministically
against this build's Marionette while executing its first
command: four defects are stacked in the client, plus one
launch-environment gate, and a stock run dies at the first of
them. That first defect is the best-supported explanation
for the R14 failure, proven by reproduction here and still
an inference about R14 (section 3.5). With the four client
fixes and the launch variable set, the operation that failed
in R14 runs cleanly in about 75 ms, and the operations
exercised live run at 68 to 131 ms per call.

The coexistence caveat from the folder-tool research is
confirmed in its weak form and disproven in its strong form
on this build: while any client holds Marionette's single
connection, other clients are refused, but a killed client's
session is reaped on disconnect and no Zen restart is needed
(section 2).

After the RDP switch, zen_live.py cannot attach to the
owner's live Zen at all, because the live launch no longer
opens a Marionette listener. Marionette remains the route
for throwaway profiles launched with --marionette and for
the geckodriver lane; RDP owns the live session (section 5).

## 1. The proof setup

- Tarball extract: about 11 s. `zen --version`: "Mozilla Zen
  1.24.3b" (642 ms).
- Launch attempt 1 (no D-Bus session bus): Zen started but
  stalled before profile creation; the Marionette port never
  opened in 180 s of polling. Zen on this VM needs a D-Bus
  session bus; dbus-launch is absent, dbus-run-session works.
  Environment note, not a tool defect.
- Launch attempt 2 (dbus-run-session, --profile throwaway,
  --marionette, --no-remote, DISPLAY on Xvfb): Marionette
  listening about 2.5 s after launch.
- Launch attempt 3 (same, plus the system-access variable of
  section 3): port open about 1 s after launch (warm).
- Unit suite as shipped: 20 tests ran, OK, 0.220 s. Why that
  green suite coexists with a dead live path is section 3.6.

## 2. Scenario results (Zen 1.24.3b, throwaway profile)

zen_live.py has no dedicated pinned-dump subcommand; `list`
is the dump that reports every tab with pinned, essential,
workspace and folder state, and the R14 context (verifying
owner essentials and pinned tabs after a cleanup close)
matches `list`. All pinned-dump runs below are `list`.

| Scenario | Result | Verbatim error / timing |
|---|---|---|
| Stock client, idle server (the stock client, as run in R14) | FAIL, deterministic | `ValueError: invalid literal for int() with base 10: b''` (86 ms, exit 1) |
| Fixed client (v4), clean single client, 2 pins + 1 folder created live | WORKS | rc=0; list 73-77 ms, introspect 97 ms, pin 85-97 ms, create-folder 131 ms |
| Fixed client, second client while a session is held | FAIL while held | `MarionetteError: connection closed by server` (59 ms; server closes the 2nd connection before the greeting) |
| Fixed client after holder SIGKILLed mid-session (leaked slot) | WORKS immediately | rc=0, 79 ms; server reaps the session on connection drop, NO Zen restart needed |
| Fixed client after holder's clean close | WORKS immediately | rc=0, 72 ms |

State creation for the baseline: three tabs opened
(example.com, example.org, iana.org), two pinned, one folder
created, which ends holding two tabs (iana.org plus the
fresh tab createFolder opens inside it). The dump after
changes shows both pins, the folder with its tab count, and
correct per-tab workspace, folder and pinned fields.

Two Zen semantics a dump consumer must know, observed live:
createFolder also opens a fresh tab inside the new folder,
and folder member tabs report "pinned": true (Zen folders
live in the pinned region). Tab count went 4 to 5 across the
folder creation; that is Zen behaviour, not a tool error.

Coexistence, precisely: the server accepts a second TCP
connection and immediately closes it without a greeting while
a connection is active, so the second client fails inside
its greeting read with "connection closed by server". The
block clears the moment the holder disconnects, cleanly or
by SIGKILL; the session is reaped on connection drop
(verified by two list calls after the one kill, 79 ms and
68 ms). The strong form of the caveat, a leaked slot that
needs a Zen restart, does not reproduce on this build.

## 3. The defect stack, in the order a user hits it

### D1 (primary): the greeting is length-prefixed and the client mis-parses it

The real server sends its greeting as a length-prefixed
frame, verbatim bytes:

```
b'50:{"applicationType":"gecko","marionetteProtocol":3}'
```

The client's _read_greeting() runs json raw_decode over the
raw buffer. raw_decode parses the leading "50" as a complete
JSON number and stops, leaving `:{...}` in the buffer. The
first frame read then partitions on ":" and calls int(b''),
raising, verbatim:

```
ValueError: invalid literal for int() with base 10: b''
```

raised in _read_frame during new_session(). Every stock run
against this build's Marionette (Zen 1.24.3b, Firefox 160)
on an idle server fails here, with the same error on every
retry. Against a busy server the stock client fails even
earlier, inside the greeting fill, because the server closes
the second connection before sending a greeting (section 2);
the busy-server case was not run with the stock client.

### D2: command names drifted to the namespaced forms

With only D1 fixed, newSession reaches the server and fails,
verbatim (frame payload):

```
{'error': 'invalid session id', 'message': 'WebDriver session does not exist, or is not active', ...}
```

Ground truth from this build's server.sys.mjs dispatch: every
command except "WebDriver:NewSession" asserts an existing
session first, and the driver command table contains only
namespaced names: WebDriver:NewSession, WebDriver:DeleteSession,
WebDriver:ExecuteAsyncScript, Marionette:SetContext. The
stock client's short names (newSession, setContext,
executeAsyncScript, deleteSession) do not exist in this
build. Parameter shapes are unchanged (setContext reads
parameters.value; executeAsyncScript reads parameters.script,
.args, .sandbox); only the names drifted.

### Launch gate: chrome context needs a launch variable

With D1 and D2 fixed, the session opens and setContext fails,
verbatim:

```
{'error': 'unsupported operation', 'message': 'System access is required. Start Zen with the "MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1" environment variable set to enable it.', ...}
```

Chrome-context (system principal) work in this build requires
Zen to be launched with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1.
This is a launch-protocol requirement, not a client defect,
and the stock client never reaches it. Whether the laptop's
zen-ai launcher sets this variable is UNVERIFIED from this
VM; the laptop live test owed by the folder-tool research
must check it, because a D1/D2-fixed client fails here next
if it is not set.

### D3: the ops table is built eagerly and crashes on other subcommands' arguments

With the session and context working, every subcommand dies
in run_op, verbatim:

```
AttributeError: 'Namespace' object has no attribute 'to'
```

run_op builds the entire ops dict literal eagerly; entries
for other subcommands dereference args.to, args.tab_url,
args.tab_url_multi, args.label, args.folder and args.index,
which argparse only defines for the subcommand actually
chosen. In the stock client this bug is masked by D1.

### D4: the async completion callback no longer exists

With D1 to D3 fixed, dispatch succeeds and every operation
hangs to, verbatim:

```
{'error': 'script timeout', 'message': 'Timed out after 30000 ms', ...}
```

(30,080 ms wall.) The payloads signal completion by calling
marionetteScriptFinished(v). That name appears nowhere in
this build's Marionette code; the modern mechanism appends
the completion callback as the last script argument,
arguments[arguments.length - 1]. The payload's try/catch
swallows the ReferenceError, so done() silently no-ops and
no completion is ever signalled. Deterministic, every run.

### 3.5 Attribution of the R14 failure

The exact R14 error string was never recorded; the only
record (improvements/r3-l3-fix-integration-review-20261127.md)
says the pinned dump "failed with a raw Marionette client
error" and was "retried with the same error". Ranked causes,
from the evidence above:

1. D1, proven here and sufficient alone. It fires on every
   stock run against an idle server, same error on retry,
   which matches the R14 record's two clauses (a raw
   Marionette client error, the same on retry; the record
   holds no error string to match against). One assumption
   is named plainly: the laptop's Zen build at R14 cleanup
   time is recorded nowhere, and this attribution assumes
   its Marionette also sent the length-prefixed greeting,
   as protocol 3 servers do and as 1.24.3b does here. R14
   was the tool's first live run (the folder-tool README
   states it had "not run against any live profile yet"),
   so R14 was the first occasion the bug could surface.
2. D2, proven here; it would have been the next failure.
3. The launch gate, proven here; relevant to the laptop, not
   reachable by the stock client in R14.
4. D3 and D4, proven here; later gates in sequence.
5. Coexistence, contributor only. It can produce an
   intermittent failure of a FIXED client if another
   Marionette consumer (for example a geckodriver lane) is
   connected at that moment. It cannot explain a stock-client
   failure, because the stock client fails at D1 with the
   server completely free.

Standing recommendation, repeated from the RDP review: any
live failure must capture the verbatim error at the time it
happens. R14's unrecorded error cost this whole isolation
exercise; D1's attribution is proven by reproduction, but it
is still an inference about R14, not a quotation.

### 3.6 Why 20 of 20 unit tests stayed green

The fake server in test_zen_sidebar.py encodes the wrong
wire format and the obsolete protocol, so the suite passes
while the live path is dead:

- The fake server sends the greeting UNPREFIXED (line 279)
  while the real server sends it length-prefixed.
- The fake server answers the short command names, and
  test_handshake_and_execute ASSERTS them (line 323:
  ["newSession", "setContext", "executeAsyncScript"]). The
  tests lock in the obsolete protocol.
- No test calls run_op() or main(), so D3 is untested.
- Payload tests assert JS contents as strings; nothing
  executes a payload against a real Marionette, so D4 is
  invisible.

## 4. What a real fix to zen_live.py requires

Evidence-based, from the working v4 copy (kept locally as
proof; applying it is the integrating lane's step):

- Parse the greeting as a length-prefixed frame, the same
  framing as _read_frame.
- Use the namespaced command names: WebDriver:NewSession,
  Marionette:SetContext, WebDriver:ExecuteAsyncScript,
  WebDriver:DeleteSession. Parameter shapes are unchanged.
- Make run_op's ops table lazy (or read arguments with
  getattr defaults) so unrelated subcommand arguments are
  not dereferenced.
- Replace marionetteScriptFinished(v) with
  arguments[arguments.length - 1](v) in the prelude's done().
- Launch protocol: MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 in the
  Zen launch environment; on this VM Zen also needs a D-Bus
  session bus (dbus-run-session) or startup stalls before
  the listener opens.
- Fix the tests to match reality: the fake server must send
  the greeting length-prefixed and assert the namespaced
  command names; add a run_op smoke test.
- Cosmetic: results now arrive WebDriver-wrapped as
  {"value": ...} instead of the bare value the old protocol
  returned; the CLI prints it as-is.

## 5. RDP versus Marionette coverage after the switch

The switch was executed on 2026-11-27 (commit 91547db1;
switch facts per the coordinator's switch record,
improvements/r10-switch-report-20261127.md, and the landing
report, improvements/r10-landing-report-20261127.md; the RT
figures below are from the RDP lane's records):
the owner's live Zen now launches flag-free via zen-human
with --profile and --start-debugger-server only, with no
--remote-debugging-port and no --marionette on the human
path; the channel registry has one selected channel,
zen-rdp-owner; the split profile is fallback; 65 tabs were
restored with an identical sessionstore hash and zero tab
loss.

Consequences for coverage:

- **RDP (Firefox Remote Debugging Protocol) is the primary
  route for the live session.** It carries the Zen internals
  work the folder tool pioneered: RT-03 proved internals via
  the RDP parent target on a throwaway profile, reads at
  median 0.6 ms, writes with read-back and revert. RT-20
  scoping is done and hardened (unit 29 of 29, live
  throwaway 19 of 19). RT-06 DevTools concurrency passed
  321 of 322 (the one failure is noSuchActor when closing
  DevTools kills the held consoleActor). RT-21 real-profile
  acceptance was partial pass. The RDP toolkit's own defects
  are recorded in the independent review
  (improvements/zen-rdp-clone2-review-20261127.md) and are
  not repeated here.
- **Marionette no longer reaches the owner's live Zen.**
  There is no Marionette listener on the human path, so
  zen_live.py cannot attach to it. Any procedure that still
  assumes zen_live.py against the live profile is void; the
  folder and workspace operations it demonstrated are being
  carried by the RDP parent-target route: internals are
  proven there on a throwaway profile (RT-03) and
  real-profile acceptance is partial (RT-21), so the full
  transfer is part of what the still-owed laptop test
  settles.
- **Marionette remains the route where it is launched.**
  Profiles started with --marionette: throwaway test
  profiles like this proof, the geckodriver lane in
  scripts/zen_dom.py, and pre-switch-style launches. The
  four client fixes in section 4 are what make that route
  usable on current Zen; without them the Marionette lane
  is dead on 1.24.3b regardless of which profile it targets.
- **Trusted input stays on the OS lane.** Neither protocol
  replaces the Wayland input protocols for trusted keyboard
  and pointer work; that boundary is unchanged by the
  switch.
- **BiDi does not reach the live session either.** The
  post-switch zen-human launch carries no
  --remote-debugging-port, so the zen_cli.py BiDi lane runs
  against a dedicated agent profile (ports scanned from
  9222 upward, per the split-adoption record), not against
  the owner's live Zen. The pre-switch standing record
  (BiDi on 9222 and Marionette on 2828 via the old launcher)
  no longer describes any entry point.

Still owed, unchanged by this proof: the laptop live test
from the folder-tool research section 5, on the owner's
machine and current laptop Zen build, now with two extra
checks from this report: whether the laptop launcher sets
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 (only relevant if a
Marionette route is used there), and the same pinned-dump
operation through the RDP route that now owns it.

## 6. Timing summary (wall clock)

- Tarball extract about 11 s; Zen --version 642 ms.
- Launch without a D-Bus session: Marionette never opened
  in 180 s of polling.
- Launch under dbus-run-session: Marionette listening about
  2.5 s after launch; with the system-access variable, about
  1 s (warm).
- Stock failures: 86 ms each. Script-timeout failure:
  30,080 ms. All successful fixed-client operations: 68 to
  131 ms (the 59 ms call was the refused coexistence
  attempt).
- Unit tests: 20 tests, 0.220 s, OK (374 ms wall).

Full proof log, verbatim error files, helper scripts and the
fixed client copies are kept locally with clone2 (r17-out/)
and are available to the coordinator on request. No personal
information in this document.
