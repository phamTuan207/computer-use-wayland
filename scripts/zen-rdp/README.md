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
  the file for the session and refuses a second client. The holder
  records pid + process start time in the file; refusals classify
  the recorded holder (alive / stale record / pid reused); the fd
  is O_CLOEXEC + O_NOFOLLOW with an ownership check; the path inode
  is re-checked after flock; a failed attach releases the lock
  (see `LOCK-MAP.md`). Fail-closed
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
- `test_act.py` - unit tests for the P2a ambiguity-refusing act:
  descriptor validation, single-eval script contract, verdict
  handling (true count / candidatesTruncated), refusal envelope
  shape with retry=unsafe, CLI pre-connect validation (no browser).
- `test_lock.py` - unit tests for the single-drive lock hardening:
  holder identity (pid + process start time), stale-record
  classification, release on failed attach, CLOEXEC, symlink
  refusal, replaced-inode detection (no browser).
- `LOCK-MAP.md` - every file lock in the stack: who takes it, what
  it fences, holder records, and stale behavior (I20 substitute).

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
python3 -m unittest test_scope_unittest test_envelope test_act test_lock test_redaction -v
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

## CLI output contract (I1, envelope v1)

`rdp_client.py` prints exactly one JSON envelope on stdout:

```json
{"version": "1", "ok": true, "command": "tabs",
 "result": {"tabs": [...], "selected_index": 0},
 "error": null,
 "disposition": {"delivery": "delivered_verified",
                 "retry": "not_applicable"}}
```

On failure `ok` is false, `result` is null (except act refusals
and wait timeouts, which carry their verdict in `result`), and
`error` carries
`code` (closed set: unscoped_refused, scope_refused,
denylist_refused, lock_held, lock_unavailable,
raw_packet_refused, parent_evaluate_refused,
port_owner_mismatch, scope_config_invalid,
profile_marker_required, not_attached, tab_not_found,
attach_failed, evaluate_failed, transport_error,
runtime_error, unexpected, target_ambiguous,
target_not_found, target_not_editable, bad_selector,
act_target_required, act_action_invalid,
act_value_required, act_value_unexpected), `message`, and the same
`disposition` object. Delivery vocabulary: `not_delivered`,
`delivery_uncertain`, `delivered_unverified`,
`delivered_verified`. Retry vocabulary: `safe` (nothing was
sent), `unsafe` (input may have landed; never replay),
`not_applicable`. Per command: reads (probe/tabs/report)
succeed as delivered_verified; eval/peval/navigate succeed as
delivered_unverified (JS ran / navigate sent, page effect not
verified by the tool, including whether a navigate actually
changed the page); bench succeeds as delivered_verified (it
polls to load). Refusals and pre-send failures are
not_delivered/safe; post-send action failures are
delivery_uncertain/unsafe.

Exit codes: 0 success, 1 runtime error, 2 usage/parse error
(argparse, scope/approval validation, the manual refusals).
The historical `ERROR: ...` line still goes to stderr.

Migration: consumers that parsed the old bare payload should
read `result` instead, branch on `error.code` (never message
text), and treat exit 1 vs 2 as runtime vs usage.
`--legacy-output` restores the old behavior exactly (bare
payload, stderr-only errors, exit 2 on any error) as a compat
shim. The library API (RDPClient, RDPError) is unchanged.

## Ambiguity-refusing act (P2a)

`act` is the only act path that resolves a target by descriptor.
One eval script counts ALL visible matches for the descriptor
(role/name/text/selector/label, ANDed; exact match after
whitespace normalization, case-insensitive) and acts only when
the count is exactly 1. There is no first-match fallback.

```
rdp_client.py --port <rdp-port> --profile-marker <profile-dir> \
  --scope-url-pattern '<pattern>' act --text Action click
rdp_client.py ... act --role button --name Submit click
rdp_client.py ... act --label Name type 'Bench User'
```

The count is the true count over the examined pool. When the
pool exceeds the scan cap (10000 elements) the verdict carries
`candidatesTruncated: true` and `count` is a lower bound; a
silently capped count is never reported. On refusal the
envelope is `ok: false` with code `target_ambiguous` /
`target_not_found` / `target_not_editable` / `bad_selector`,
`result` carries the verdict (count, candidatesTruncated, up to
10 candidate summaries, the descriptor echo), delivery is
`delivered_verified` (the script ran and its verdict arrived),
and retry is `unsafe`: act commands are never replayed, because
a lost response cannot distinguish a refusal from a landed
click. A transport failure mid-act is `delivery_uncertain` /
`unsafe` by the same rule. Success is `delivered_unverified`
(JS ran; page effect not verified by the tool), like `eval`.
`--wait-for` / `--wait-timeout` apply after a successful act,
as with `eval`. Refusals are recorded in the drive report
(`act_refusals`).

The descriptor is the I3 ref content: snapshot refs carry
role+name, and `act` is the act-time resolver for that shape
(one ref system, two resolvers). The snapshot-time resolver
(persistent registry + cross-call digest) is P2b, gated on its
settling tests; it is not part of this command. Text search
covers actionable elements only (links, buttons, form controls,
labels, role/tabindex/contenteditable elements), not arbitrary
divs. `type` sets the value via the native setter plus
input/change events (the measured 52 ms class path), on
input/textarea targets only.

## Post-action waits (I17)

`--wait-for EXPR --wait-timeout SECONDS` after `navigate` or
`eval` polls the JS expression until truthy. There is no
default timeout: the caller names the budget, so a 2 s failure
never silently becomes a 30 s one. On expiry the envelope
error code is `wait_timeout` and `result` still carries the
action's own outcome (`action_result`), because the action
landed; only the wait expired. Rule of thumb: use wait-for
when the next step needs page state that settles
asynchronously (rendered text, a route change); use I6-style
post-action verification when the question is whether the
action itself took effect; use I10 auto-wait on the a11y lane
for element readiness before acting. Never use a fixed sleep
in place of any of the three.
