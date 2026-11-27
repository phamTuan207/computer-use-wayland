# Pilot results 2026-11-27: Q1, Q10, Q4, Q33

Environment for all pilots: this VM, Zen Browser 1.24.3b (BuildID
20261118023529, Firefox 160) from ~/workspace/tools/zen/extracted/zen/zen,
Xvfb on display :99, every browser run under dbus-run-session on a
throwaway profile. Logs: q1/log.txt and q1/log2.txt, q10/log.txt,
q4/log.txt, q33/log.txt in this directory. All times are wall clock as
logged. MOZ_REMOTE_ALLOW_SYSTEM_ACCESS was unset except where a pilot
says otherwise.

## Pilot 1. Q1, geckodriver --allow-system-access

Verdict: PROVEN. Promote to the integration queue.

Setup: geckodriver 0.37.1 (~/workspace/tools/geckodriver), Selenium
4.53.0 (~/workspace/tools/venv), script q1/q1_pilot.py. Each run creates
a session on a fresh throwaway profile, tries a chrome-only script
(`return Services.appinfo.name + '|' + Services.appinfo.version`) in
content context as a control, then switches to chrome context and runs
it again. The first attempt (q1/log.txt) also surfaced a harness
artifact: a not-yet-created profile directory made geckodriver fail
with "Failed to set preferences: unknown error"; the script now creates
the directory first, and the decisive run is q1/log2.txt.

Run A, no geckodriver flag, system access attempted through
moz:firefoxOptions args (Selenium add_argument lands in
moz:firefoxOptions.args): session creation rejected in 0.366 s with the
verbatim error:

  InvalidArgumentException: Message: Argument
  --remote-allow-system-access can't be set via capabilities

So on 0.37.1 the firefoxOptions route is not silently ignored, it is
refused outright at session creation.

Run A2, no flag and no firefoxOptions arg (control): session created in
9.193 s. Content-context script failed as expected in 0.023 s
("ReferenceError: Services is not defined"). set_context("chrome")
failed in 0.004 s with the verbatim error:

  WebDriverException: Message: System access is required. Start Zen
  with the "MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1" environment variable set
  to enable it.

Run B, geckodriver started with service_args ["--allow-system-access"],
no firefoxOptions arg: session created in 7.576 s, content control
failed as expected in 0.029 s, set_context("chrome") succeeded in
0.002 s, and the chrome-context script returned 'Zen|1.24.3b' in
0.045 s.

Success criterion from the queue (chrome context reachable only via the
geckodriver flag): MET. The three mechanisms are confirmed distinct:
capabilities arg refused, plain session blocked at SetContext, the
geckodriver flag works.

## Pilot 2. Q10, BiDi chrome-scope spike

Verdict: PROVEN, with one correction to the queue's launch recipe.
Promote to the integration queue with the recipe corrected.

Setup: Zen launched with --remote-debugging-port 9333 and
--remote-allow-system-access on a throwaway profile; client is a
stdlib-only WebSocket implementation (q10/wsclient.py, no pip
installs) driving WebDriver BiDi (q10/q10_spike.py, launcher
q10/run.sh). Two facts about the endpoint on this build: GET
/json/version returns 404 (the CDP HTTP endpoints are gone), and the
BiDi websocket is at ws://127.0.0.1:9333/session (the root path returns
an HTTP 200 info page, not a websocket upgrade).

Attempt 1, browser argument only, no env var: session.new succeeded
(1.822 s), content getTree succeeded (1.176 s, one about:blank
context), but browsingContext.getTree with {"moz:scope": "chrome"}
failed in 0.009 s with the verbatim BiDi error:

  error "unsupported operation", message "System access is required.
  Start Zen with the \"MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1\" environment
  variable set to enable it."

So for the BiDi chrome scope, the --remote-allow-system-access browser
argument alone does not satisfy the gate on Zen 1.24.3b; the check
(assert.hasSystemAccess in the BiDi browsingContext module) wants the
environment variable.

Attempt 2, same launch plus MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 in the
browser's environment: session.new 1.660 s; content getTree 0.916 s;
chrome getTree succeeded in 0.009 s and returned the browser window
context (url chrome://browser/content/browser.xhtml, moz:scope
"chrome") with one child chrome context (moz:name "sidebar").
script.evaluate in the chrome context returned 'Zen|1.24.3b' for
Services.appinfo (0.118 s). Read-only Zen-state dump through BiDi
evaluate, all successful: gZenWorkspaces, gZenFolders and gBrowser all
present as objects (0.001 s); workspace list returned one workspace
with active true (0.001 s); tab list returned the single about:blank
tab with pinned false and folder null (0.063 s); folder list returned
[] (0.005 s). session.end 0.011 s. Total spike wall time 4.597 s.

Success criterion (a chrome context is returned and a read-only dump
completes): MET. Caveat: the dump was taken on a fresh profile whose
whole state is one blank tab and no folders, so this proves the read
path, not a field-by-field equality check against the Marionette dump
on a rich profile; that comparison is the natural first integration
step. The queue entry's launch recipe should be corrected: require the
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable; the browser
argument by itself was not enough for BiDi.

## Pilot 3. Q4 remainder, zen_live_fixed4.py subcommands

Verdict: PARTIAL (six of the seven unproven subcommands pass cleanly;
move-tab executes but does not honor the requested index). Promote the
six; hold move-tab pending a Zen tab-order semantics check.

R17 had proven introspect, list, pin and create-folder. This pilot ran
the remaining seven against throwaway Marionette profiles (Zen with
--marionette and MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1), driver
q4/q4_driver.py, full log q4/log.txt. Results are wrapped by the client
as {"value": ...}; a payload carrying an "error" key counts as failure
regardless of exit code (see finding 1 below).

Passed, with timings:
- switch-workspace (run v2, 0.191 s): returned the active workspace
  uuid. The profile has a single workspace, so this exercised the call
  against the already-active workspace.
- move-workspace (v2, 0.210 s): returned the tab url and its workspace
  uuid. Introspect confirms gZenWorkspaces.moveTabToWorkspace is a
  function in this build. Single-workspace caveat as above.
- move-folder-space (v2, 0.190 s): returned folderId and workspace uuid
  (folder moved to the workspace it was already in; same caveat).
- leave-folder (v4, 0.172 s and again 0.345 s): returned folder null,
  with the payload note "raw ungroupTab; verify Zen folder bookkeeping
  followed".
- move-folder (v4, 0.128 s): returned the tab's folder set to the
  created folder id.
- unpin (v4, 0.176 s): after pin (0.142 s, pinned true), unpin returned
  pinned false.

Partial:
- move-tab (v4, 0.121 s): executed without error and returned
  {url, index: 2} after being asked for --index 0; the final list still
  shows the tab at index 2. The JS returns gBrowser.tabs.indexOf(tab)
  after gBrowser.moveTabTo (zen_live_fixed4.py lines 193-201), so the
  requested index was not honored in this layout (index 0 was occupied
  by the folder's pinned tab). The command path works; the semantics
  need one check against Zen's tab ordering rules before promotion.

Two side findings:
1. The CLI's exit code does not reflect payload errors. In runs v2 and
   v3, subcommands whose payload was {"error": "pickTab ... tab
   selector matched 0 tabs"} still exited 0, because main() checks
   result.get("error") while execute_async returns the payload nested
   under "value" (zen_live_fixed4.py, main, lines 336-343). Callers
   must inspect value.error themselves. (Those v2/v3 failures were a
   fixture problem in this pilot, not a client defect: the second
   fixture tab, example.com and then example.net, never navigated in
   the browser on this VM, its tab stayed at about:blank, and pickTab
   correctly matched 0 tabs. curl from the shell reaches both hosts
   with HTTP 200, so the cause is in-browser tab loading on this VM,
   not network reachability. v4 therefore ran all tab ops against the
   one tab that does load, example.org.)
2. create-folder adopts a blank tab into the new folder as a pinned
   member (folder tabCount 2 right after creating a folder around one
   tab; the adopted blank tab remains as the folder's tab after the
   real tab leaves). This matches the R17 note that createFolder opens
   a fresh tab inside the folder; integrators should expect it.

## Pilot 4. Q33, Marionette sequencing audit of zen_live_fixed4.py

Verdict: PARTIAL. The single-threaded use the CLI makes is strictly
one-in-flight by construction, and that part is proven. The queue's
stronger criterion (a shared client serializes concurrent commands and
never misattributes a response) is NOT met: measured silent
misattribution. Promote Q33 with the fix shape specified (a lock
around command(), or a documented one-client-per-thread rule).

Code audit (~/workspace/r17-out/zen_live_fixed4.py):
- The Marionette class holds one socket, one shared receive buffer and
  one shared message counter: lines 216-218 (self.sock, self.buf,
  self.msgid). There is no lock, threading or asyncio anywhere in the
  file (grep finds none).
- command() (lines 245-260) increments self.msgid, sendall()s the
  frame, then blocks in _read_frame() until a response arrives and
  raises MarionetteError if the response id does not equal self.msgid
  (lines 252-254). In a single thread this is strictly sequential: the
  next command cannot be sent before the previous response is read.
- The CLI layer is sequential too: run_op (lines 285-302) issues
  new_session, set_context, then exactly one execute_async; main()
  (lines 304-344) runs one subcommand per process.

Interleaving test (q33/q33_interleave.py, log q33/log.txt): two
threads share ONE Marionette object and fire execute_async
concurrently, thread A with an 800 ms script returning "AAA", thread B
with a 100 ms script returning "BBB", three rounds per run, two runs
(six rounds total). In no round did both threads receive their own
results. Outcomes:
- Three rounds: one thread received {'value': 'BBB'} correctly in
  about 0.14 to 0.17 s; the other raised "MarionetteError: response id
  3 does not match request id 4 for WebDriver:ExecuteAsyncScript"
  after a 30.0 s stall (the shared buffer and counter race; the
  socket timeout is 30 s).
- Three rounds: silent misattribution. One thread's execute_async
  returned {'value': 'BBB'} for its own "AAA" request with no error.
  Mechanism, from the code: both threads increment the shared
  self.msgid, so by the time the first thread checks, self.msgid
  already equals the second command's id, the check at line 252
  passes against the wrong frame, and the second command's result is
  returned as the first command's. (The test script's own
  misattribution detector compared the wrong field and printed "no";
  the logged raw tuples show the 'BBB' value in the A slot, which is
  the evidence relied on here.)

So the id check prevents misattribution only in single-threaded use.
Any future caller that shares one client across threads (the parallel
work Q33 wants routed to BiDi is safe, but a threaded Marionette
caller is not) can silently receive another command's result. The
minimal Ponytail fix is a threading.Lock wrapping the body of
command(), which restores the one-in-flight invariant the protocol
requires.

## Summary

| Pilot | Item | Verdict | Promote to integration queue |
|---|---|---|---|
| 1 | Q1 geckodriver --allow-system-access | PROVEN | Yes |
| 2 | Q10 BiDi chrome-scope spike | PROVEN (recipe correction: env var required, browser arg alone insufficient) | Yes, with the corrected launch recipe |
| 3 | Q4 zen_live remainder | PARTIAL (6 of 7 pass; move-tab index not honored) | Yes for the six; hold move-tab |
| 4 | Q33 Marionette sequencing | PARTIAL (sequential CLI proven; shared client misattributes silently under threads, 3 of 6 rounds) | Yes, with the lock fix specified |
