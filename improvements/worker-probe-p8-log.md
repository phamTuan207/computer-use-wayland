# PROBE-P8 log: Marionette chrome context on live Zen, no restart

Worker: PROBE-P8. Coordinator: COORD-CLICK-3. Owner: Pham Tuan.
Branch: todolist-push. All times wall-clock Asia/Ho_Chi_Minh + elapsed.
Probe script: /tmp/probe-p8.py on the laptop (copy at ~/workspace/probe-p8.py
on the VM), run detached via setsid nohup, log at /tmp/probe-p8.log.

Standing rules recorded in this log, as briefed:
- No-self-healing rule (05:56): when Muse itself errors or fails, an
  INDEPENDENT worker investigates, names the cause and finds the fix.
  Muse does not self-diagnose or self-fix. This probe only measures and
  reports; it diagnoses nothing and fixes nothing.
- First-principles rule (06:01): ask whether the design was wrong from
  the start and rewrite if evidence proves a better path. Applied here
  as a question only: the chrome-context path is closed without a
  restart, so the design consequence is to keep screenshots ONLY for
  Zen chrome UI and record that boundary explicitly (P8 fallback).

## Question (GROUNDING-REVIEW d1fc4e9, P8)

Does Marionette chrome context (set_context("chrome")) work on the live
Zen WITHOUT a restart, as a DOM path for Zen's own UI (sidebar, urlbar,
tabs)? AT-SPI cannot see Zen (C12 probe), so if chrome context works the
last screenshot-only surface falls. The C12 note says chrome-context eval
is blocked without a Zen restart. This probe re-tests live, fresh, with
its own measured numbers, and does NOT restart Zen or change any setting.

## 06:36:54 +07 (+00.0s) pre-checks (SSH, short commands)

- Zen alive: PID 496121, `/opt/zen-browser-bin/zen-bin
  --remote-debugging-port=9222 --marionette`. Same process the C12 probe
  used (started 17:37 on 21/11, never restarted since).
- Marionette listening: 127.0.0.1:2828, owned by zen-bin PID 496121.
- `MOZ_REMOTE_ALLOW_SYSTEM_ACCESS` ABSENT from Zen environ
  (read /proc/496121/environ, grep MOZ_REMOTE, no match). Pre-evidence
  only, not the verdict: the live moz/context call below is the test.
- geckodriver 0.37.1 at /tmp/geckodriver on the laptop (not in PATH,
  same as the shipped default in scripts/zen_dom.py line 68).
- No geckodriver process running: the single remote session slot was
  free, no wait needed.

## 06:37:41 +07 (+47s) probe run (detached, /tmp/probe-p8.log)

Method: reuse the shipped driver scripts/zen_dom.py ZenSession
(geckodriver --connect-existing, marionette-port 2828, wd-port 4444),
then POST /session/{id}/moz/context {"context": "chrome"} via its _wd
helper. Content sanity eval first, to prove the session works at all.

Full log, verbatim:

```
[06:37:41 +07 +00000.0s] PROBE-P8 start wall=06:37:41 2026-11-22 UTC+07:00
[06:37:41 +07 +00000.0s] Zen PID 496121, --remote-debugging-port=9222 --marionette, Marionette 127.0.0.1:2828, geckodriver 0.37.1 /tmp/geckodriver
[06:37:41 +07 +00000.0s] MOZ_REMOTE_ALLOW_SYSTEM_ACCESS ABSENT from Zen environ (checked /proc/496121/environ before this run)
[06:37:41 +07 +00000.0s] session acquire attempt 1/10
[06:37:41 +07 +00000.0s] session acquired in 0.01s sessionId=c6e5b6d2...
[06:37:41 +07 +00000.0s] STEP1 content sanity eval 0.00s: {'mozInnerScreenX': 240, 'mozInnerScreenY': 8, 'title': 'Welcome!', 'url': 'https://zen-browser.app/welcome/'}
[06:37:41 +07 +00000.0s] STEP2 moz/context -> chrome FAILED in 0.00s: HTTP 500 on POST /session/c6e5b6d2-7781-4fce-89eb-cf09d06b93b2/moz/context: {"value":{"error":"unsupported operation","message":"System access is required. Start Zen with the \"MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1\" environment variable set to enable it.","stacktrace":"RemoteError@chrome://remote/content/shared/RemoteError.sys.mjs:14:8\nWebDriverError@chrome://remote/content/shared/webdriver/Errors.sys.mjs:169:5\nUnsupportedOperationError@chrome://remote/content/shared/webdri
[06:37:41 +07 +00000.0s] RESULT: BLOCKED, chrome context NOT available in this running Zen without a restart. No chrome DOM reachable. No restart performed, no setting changed.
[06:37:41 +07 +00000.0s] session DELETE sent in 0.00s, slot left free
```

Notes on the numbers:
- Session acquire 0.01s, first attempt, no busy wait. The one-session
  slot was free; step 4 of the brief (wait up to 10 min if busy) was
  not triggered.
- STEP1 content eval 0.00s: title 'Welcome!', url
  https://zen-browser.app/welcome/, mozInnerScreenX=240,
  mozInnerScreenY=8. The session itself works; only the chrome-context
  switch fails. The mozInner values match the C12 probe exactly
  (240, 8), third independent confirmation of that geometry.
- STEP2 failed in 0.00s: an immediate refusal, not a timeout. The
  stacktrace tail is cut at 400 chars by the _wd helper in
  scripts/zen_dom.py; the error and message above it are complete.
- Total probe run under 1s. Total time from first check to verified
  teardown about 2 min, far inside the 30 min time-box.

## 06:38:22 +07 (+88s) teardown verification

- No geckodriver process remains (pgrep -x geckodriver: none).
- Session lock free: flock LOCK_EX|LOCK_NB on
  ~/.cache/agent-computer-use/zen_dom.lock acquired and released.
- Zen untouched: still PID 496121, no restart, no setting changed, no
  chrome UI change (read-only probe, and the chrome eval never ran
  because the context switch itself was refused).

## Verdict: BLOCKED

Marionette chrome context does NOT work on the live Zen without a
restart. Exact error, HTTP 500, error "unsupported operation",
message: "System access is required. Start Zen with the
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable set to enable
it." No chrome DOM is reachable: no urlbar value, no tab list, no
sidebar read. The gate is the missing env var in the running Zen
process, confirmed two ways (absent from /proc/496121/environ, and
the live 500).

This independently reproduces the C12 probe result (03:27:26 +07 on
22/11, same HTTP 500, same message) on the same still-running Zen
process, so the boundary is stable, not a one-off.

Consequence per P8: keep screenshots ONLY for Zen chrome UI and record
that boundary explicitly. The only path to chrome context is a Zen
restart with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1, which this probe did
not do (it would kill owner tabs and the session) and which is a
decision for the owner, not for a probe. AT-SPI remains closed too
(C12: Zen never registered accessibility). No further time spent on
this path in this probe.

## Evidence index

- Probe script: /tmp/probe-p8.py on the laptop, copy at
  ~/workspace/probe-p8.py on the VM (not committed, scratch only).
- Probe log: /tmp/probe-p8.log on the laptop, quoted verbatim above.
- Prior result reproduced: improvements/worker-click2-c12probe-log.md,
  03:27:26 +07 run 2 (same HTTP 500, same message).
- Driver used: scripts/zen_dom.py ZenSession (todolist-push HEAD
  49081aa at probe time), geckodriver 0.37.1, Marionette port 2828.
- Commit of this log: (filled at commit time).
