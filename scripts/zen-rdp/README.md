# Zen RDP toolset (scripts/zen-rdp)

Generic, stdlib-only client for the Firefox Remote Debugging Protocol
(RDP) as exposed by Zen Browser, plus its per-update smoke test. This
is the Phase 1 fast DOM lane of the R10 seamless-control decision:
attach, evaluate read/write, navigate, tab list, and a fail-loud
webdriver probe, on a flag-free Zen session (debugger server started
via `--start-debugger-server` plus devtools prefs). Trusted OS input
and screenshots stay on the computer-use lane; this toolset sends no
OS input.

**Optional, opt-in, default off.** Nothing in the repo enables this
lane. It runs only when an operator explicitly launches a browser
with the debugger server and invokes these scripts against it. The
silent-attach switch (`devtools.debugger.prompt-connection=false`)
is an owner security decision recorded in the machine layer, never a
repo default.

## Files

- `rdp_client.py` - RDP client with tool-enforced tab scoping
  (RT-20): per-session tab scope (descriptor ids and/or URL glob
  patterns; AND semantics when both are given), credential-tab
  denylist with explicit approvals (ON by default in the CLI;
  `--scope-config` patterns override; `--no-denylist` disables with
  a loud warning recorded in the report; lazy tabs reporting an
  empty URL count as denylisted), JSON drive report (probe, tab
  diff, refusals, approvals, action counts, retry count, parent
  evaluates, lock holder). Unscoped sessions are refused unless
  `--unscoped-test` is passed explicitly (throwaway/test only).
  Parent-process (chrome JS) evaluate requires `--allow-parent` and
  is audited in the drive report. Raw `request()` refuses
  evaluate/navigate packet types; they must go through the guarded
  methods. Large string results (longString grips) are fetched in
  full. Single-drive lock: `--lock-file` / `RDP_LOCK_FILE` flock()s
  the file for the session and refuses a second client. Fail-closed
  port-owner guard: an explicit `--profile-marker` is required
  before attach (test-only escape: `--allow-unmarked-test-attach`,
  warns loudly). Tab-pinned re-attach: when a target swap (e.g.
  DevTools close) kills the held console actor with `noSuchActor`,
  evaluate/navigate re-attach to the same tab (canonical descriptor
  id with URL verification, URL fallback, never selected-pick) and
  retry once (RT-06).
- `rdp_smoke.py` - per-update smoke test (RT-05/RT-18). Runs after
  every Zen update, before agent use resumes. Fail-loud, fail-closed:
  stops at the first failed check, prints one JSON object, exits with
  a distinct nonzero code per check (port owner, attach, webdriver
  probe, evaluate, parent-target Zen internals, loopback bind,
  navigate to about:blank; latency is informational). Takes `--port`
  and `--profile-marker` as required arguments; it never guesses a
  port. The navigate check replaces the attached tab content: run
  smoke on a throwaway or tasked tab, never a valued owner tab.
- `test_scope_unittest.py` - unit tests (fake transport, no browser):
  scoping, denylist + approvals, drive-report diff, fail-closed
  marker, noSuchActor retry pinning.
- `test_rdp_smoke.py` - unit test for the smoke bind parser and
  exit-code map (no browser).
- `test_rdp_client.py` - small live self-test against a throwaway
  browser (see its docstring for the fixture contract).

## Machine layer (not in this repo)

Everything machine-specific lives on the laptop machine layer only:

- RDP prefs / applied `user.js` set for the owner profile.
- The port registry (channel name, port, owner, purpose, profile
  marker, selected flag, last smoke result). Fail-closed rule: no
  channel selected in the registry = no drive; never guess a port;
  drive only the selected channel, and only after `rdp_smoke.py`
  passes on that exact port + profile marker.
- Scope-config JSON files (real scope patterns and credential-tab
  denylist entries; the schema and generic defaults are in
  `rdp_client.py`).
- The registry-driven wrapper path for owner drives MUST set
  `--lock-file` (or `RDP_LOCK_FILE`) so exactly one drive holds the
  owner session at a time, and MUST pass a scope plus the denylist
  (default-on) for every owner drive. `--unscoped-test`,
  `--no-denylist`, and `--allow-unmarked-test-attach` are forbidden
  on the owner channel.
- Drive reports and smoke JSON output (they carry tab lists, URLs,
  pids, and cmdlines).

This directory carries only generic code: no ports, pids, profile
paths, or personal values.

## Running the smoke test

Against a browser already launched with the debugger server (port
and marker read from the machine-layer port registry, never guessed):

```
python3 rdp_smoke.py --port <rdp-port> --profile-marker <profile-dir>
```

Exit 0 means all checks passed. A failure on the webdriver probe or
the parent-target check after a Zen update is kill-criterion
evidence (see below): the RDP lane stays down and the interim split
continues; do not retry-drive on a failed smoke.

Unit tests (no browser):

```
python3 -m unittest test_scope_unittest -v
python3 test_rdp_smoke.py
```

## Decision and kill criteria

Route choice, acceptance test, and kill criteria live in
`../../improvements/r10-seamless-decision-20261127.md`. In short:
one Zen update breaking this toolset (probe not clean, or a
human-path block on the acceptance panel), or 7 days broken,
retires the lane to the interim split automatically; actor
breakage on two consecutive updates requiring client rewrites
retires the RDP lane. The interim split remains the operating
configuration until acceptance passes on the real profile.
