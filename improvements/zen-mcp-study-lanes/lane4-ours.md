# Lane 4: inventory of OUR OWN Zen control channel (scripts/zen-rdp)

Scope: read-only inventory of the landed state on todolist-push
(tip a831e250, integration phase landing, fetched 2026-11-27).
Primary sources read in full or in the cited ranges:
scripts/zen-rdp/rdp_client.py (1676 lines), scripts/zen-rdp/README.md,
scripts/zen-rdp/rdp_smoke.py, scripts/zen-rdp/LOCK-MAP.md (listed),
scripts/a11y.py (357 lines), improvements/zen-sidebar/zen_live.py
(559 lines) and README, improvements/zen-rdp-clone2-review-20261127.md
(the F1-F12 review), improvements/integration-review-20261127.md
(the A/B/C/F findings) plus the fix commits that landed after both
reviews (notably c29beb63 "Redteam fix batch A" and 6b943977).

Line numbers below are for rdp_client.py at a831e250 unless another
file is named.

## 1. Transport and connection

- Protocol: Firefox Remote Debugging Protocol (RDP), hand-rolled
  stdlib-only Python client. No WebDriver, no Marionette, no BiDi
  in this channel. Wire format is the RDP length-prefixed JSON
  framing (`<len>:<json>`), implemented in _send/_recv/_fill
  (rdp_client.py:833-855). One TCP socket per client object, one
  request in flight at a time (sequential request/response loop in
  request(), 856-881).
- Endpoint: TCP to 127.0.0.1 by default (host parameter, port is a
  required CLI argument, never guessed and never defaulted). The
  browser side is a Zen session launched with
  `--start-debugger-server` plus devtools prefs; the silent-attach
  switch (devtools.debugger.prompt-connection=false) is an owner
  machine-layer decision, not a repo default (README "Zen RDP
  toolset"). The port itself, the channel registry (channel name,
  port, owner, profile marker, selected flag, last smoke result)
  and all scope configs live in the machine layer on the owner's
  laptop, not in the repo (README, "Machine layer").
- Attach sequence: socket connect + greeting read in __init__
  (672-688); check_port_owner before connect in the CLI (main,
  1635-1637); attach() = listTabs + getTarget (1016-1024). The
  client caches descriptor actor, target actor and console actor.
- Attach gates (fail-closed, all before or at session start):
  - Port-owner gate: --profile-marker is required; check_port_owner
    (404-439) finds the listening pid via `ss -tlnp` and requires
    the marker substring in /proc/<pid>/cmdline. Empty marker is
    refused. Test-only escape --allow-unmarked-test-attach warns
    loudly.
  - Scope gate: an unscoped session is refused in RDPClient.__init__
    (646-652) unless unscoped_test=True is passed explicitly (loud
    warning, recorded in the drive report).
  - Single-drive lock: optional --lock-file / RDP_LOCK_FILE flock
    for the whole session (716-780, hardened per LOCK-MAP.md:
    holder record is pid + /proc start time, O_CLOEXEC + O_NOFOLLOW,
    ownership check, inode re-check after flock, release on failed
    attach). The machine-layer wrapper MUST set it for owner drives;
    the client itself does not force it.
- Evaluation contexts, exactly two:
  - Content context: evaluate() sends evaluateJSAsync to the held
    tab's consoleActor (1069-1107). This is arbitrary JavaScript in
    the page.
  - Parent/chrome context: parent_evaluate() resolves the
    parent-process target (listProcesses -> getTarget ->
    consoleActor, 1099-1147) and evaluates chrome JS there. Gated
    by allow_parent=True (CLI --allow-parent); every call is
    recorded in the drive report (count + first 80 chars of the
    expression). Chrome JS bypasses tab scope by design; the gate
    plus the audit record are the fence.
- Session handling: stateful, one attached tab pinned per client
  (canonical tab id + URL, set in get_target, 981-983). On a target
  swap that kills the console actor (noSuchActor), evaluate and
  navigate re-attach pinned to the same tab with URL verification
  and retry exactly once (_reattach_pinned, 985-1014; never falls
  back to the selected tab). Sessions are short-lived CLI
  invocations or library objects; there is no daemon, no session
  persistence, no reconnect protocol beyond the pinned re-attach.
- No OS input: the toolset sends no trusted OS input and no
  screenshots; input and screenshots stay on the computer-use lane
  (README, first section).

## 2. Capability surface

CLI subcommands (rdp_client.py main, 1525-1548): 7.

| Command | What it does |
|---|---|
| probe | webdriver cleanliness probe (probe_webdriver) |
| tabs | listTabs inventory with redacted snapshot + selected index |
| report | build (and optionally write) the JSON drive report |
| eval | evaluate JS in the attached tab's content context |
| peval | evaluate JS in the parent (chrome) context, gated |
| navigate | navigateTo the attached tab |
| bench | latency benchmark (attach/evaluate/navigate timings) |

Library operations on RDPClient (the real surface; the CLI is a
thin wrapper): list_tabs, get_target / attach / refresh_target,
evaluate, parent_evaluate, navigate, wait_for (I17 post-action JS
poll), wait_load (poll readyState + URL substring, with pinned
re-attach), probe_webdriver, drive_report / write_drive_report,
request (raw RDP packets, with evaluateJSAsync and navigateTo
refused unless called from the guarded methods, 856-867), close.
Grouped:

- Read/inventory (3): tabs listing, drive report, webdriver probe.
  There is NO DOM snapshot or DOM dump command: page content is
  read only by running arbitrary JS through eval (for example
  document.querySelectorAll('*').length in smoke/bench;
  innerText/outerHTML reads arrive as longString grips and are
  fetched in full by _fetch_long_string, 1038-1061).
- Act (3): eval (arbitrary content JS, so clicks/writes are
  possible but only as hand-written JS), peval (arbitrary chrome
  JS), navigate.
- Wait (2): wait_for, wait_load.
- Session/safety (4): attach with pinning, pinned re-attach,
  single-drive lock, bench (destructive, throwaway-only).
- Smoke test (separate script, rdp_smoke.py): 8 checks (port owner,
  attach, webdriver probe, evaluate round-trip, parent-target Zen
  internals typeof gZenWorkspaces/gBrowser/gZenFolders, loopback
  bind, latency informational, navigate to about:blank), fail-loud
  with a distinct exit code per check; run after every Zen update
  before agent use resumes.

Total: 7 CLI commands, about 12 library operations. Deliberately
small and low-level: it is a transport plus safety shell, not a
browser-automation API.

Adjacent channels in the same repo (not zen-rdp, relevant to the
comparison):

- scripts/a11y.py: AT-SPI accessibility lane for the whole desktop
  (any app by pid, including Zen). A stdin/stdout JSON worker with
  6 operations: apps, observe, query, ground, drill, act. observe
  walks the AT-SPI tree into a snapshot file with per-element refs
  and a snapshot_id; refs can be snapshot-qualified (I3,
  parse_ref). act performs semantic actions by ref: click (native
  AT-SPI action) and set_text (with read-back verification),
  through wait_actionable auto-wait (I10). ground re-resolves a ref
  to fresh screen extents. Snapshots expire after 90 s and carry
  completeness accounting (complete/incomplete/read_errors, I5/I15).
- improvements/zen-sidebar/zen_live.py: Marionette prototype
  (port 2828, chrome context, requires
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 at browser launch). 11 ops plus
  preflight: introspect, list (workspaces, tabs, folders dump via
  chrome JS), switch-workspace, move-workspace, create-folder,
  move-folder, leave-folder, move-folder-space, pin, unpin,
  move-tab. This is where workspace/folder manipulation lives; it
  is a research prototype in improvements/, not part of the landed
  scripts/ channel, and per the RDP switch it cannot attach to the
  owner's live Zen (which launches without Marionette).
- improvements/zen-sidebar/zen_sessions.py: offline editor for
  zen-sessions.jsonlz4 (sidebar state since Zen 1.18), with a gated
  safe procedure. Not a live channel.

## 3. Safety machinery

- Error envelope (I1, rdp_client.py:235-337 and README "CLI output
  contract"): exactly one JSON envelope on stdout, version "1",
  with ok, command, result, error{code, message, disposition} and
  disposition{delivery, retry}. Error codes are a closed set (17
  named in the README: unscoped_refused, scope_refused,
  denylist_refused, lock_held, lock_unavailable,
  raw_packet_refused, parent_evaluate_refused,
  port_owner_mismatch, scope_config_invalid,
  profile_marker_required, not_attached, tab_not_found,
  attach_failed, evaluate_failed, transport_error, runtime_error,
  unexpected; plus wait_timeout, wait_timeout_required and
  wait_timeout_invalid added by I17 and the fix batch). Delivery
  vocabulary: not_delivered, delivery_uncertain,
  delivered_unverified, delivered_verified (plus unknown in the
  code comment). Retry vocabulary: safe (nothing sent),
  unsafe (may have landed, never replay), not_applicable. Exit
  codes 0/1/2 (success / runtime / usage). --legacy-output restores
  the pre-envelope contract. Consumers are told to branch on
  error.code, never message text.
- Tab scope (RT-20): per-session Scope of descriptor ids and/or
  URL glob patterns, AND semantics when both given (339-373).
  Acting on a tab (getTarget/evaluate/navigate) is scope-gated;
  list_tabs is always allowed for discovery. Scope refusals are
  recorded for the drive report.
- Credential denylist: ON by default in the CLI. Default patterns
  are 9 substrings (rdp_client.py:68-71): login, signin, sign-in,
  account, auth, oauth, password, checkout, payment. Matching is
  _url_matches (209-216): glob when the pattern contains * or ?,
  else case-insensitive substring. Checked on the current tab for
  evaluate/navigate and on the destination URL for navigate
  (1166-1196). Lazy tabs reporting an empty URL count as
  denylisted (fail-closed). Escape requires an explicit per-tab
  approval: --allow-credential-tab plus --approval-note, both
  mandatory together; approvals used are recorded. --no-denylist
  disables with a loud warning recorded in the report; a scope
  config's patterns replace the defaults wholesale.
- Redaction (I22, 447-596): _redact_url redacts sensitive query
  parameter values in tab snapshots and drive reports. Parameter
  names are matched after normalization (percent-decode, lowercase,
  split on separators and camelCase humps, whole-token stem match
  against stems: token, secret, password, passwd, pass, auth,
  session, csrf, otp, code, key, credential, bearer, jwt, saml,
  assertion, ticket, signature, private, jsessionid), so
  accessToken, csrf_token, api-key and %74oken all hit while
  innocent names like zipcode survive. Also covered: userinfo
  passwords in the authority, ;-separated path parameters
  (jsessionid), nested pairs inside values (next=/cb?token=...),
  percent-encoded nested pairs, and URLs embedded in free text
  (_redact_text, applied recursively to the whole drive report).
  Scope matching internally keeps raw URLs; only output bytes are
  redacted. Known residual: a fragment with no "=" or "&" in it is
  passed through verbatim (see C1 status below), and evaluate()
  result bytes are out of scope by design (the agent asked for
  them).
- Audit: the drive report (1294-1350) records generated_at,
  session start, port, scope, unscoped_test flag, denylist state
  (enabled, disabled_via_flag, patterns), parent_evaluates
  (80-char prefixes + timestamps), lock file + holder pid, probe
  result, tabs_before/tabs_after snapshots (redacted), tab diff,
  denylist hits, scope refusals, approvals used and configured,
  action counts, retry count. It is written only when a report
  path is configured (--drive-report, or the report subcommand);
  close() writes it on session end when a path is set (1352-1366).
- Other fences: raw request() refuses evaluateJSAsync/navigateTo
  packet types so scope cannot be bypassed at the packet layer;
  bench refuses to run without the explicit unscoped-test opt-in
  and a port-owner marker; the smoke test is fail-closed per check.
- Kill criteria (README): one Zen update breaking the toolset, or
  7 days broken, retires the lane; actor breakage on two
  consecutive updates retires it permanently.

### Known defects and current fix status (landed code, a831e250)

From the integration review (8bf5e850), fixed by c29beb63 and
6b943977 before the landing merge:

- A1 (I1 classification branches on message text; a page exception
  containing "pinned tab" classified as attach_failed/safe):
  FIXED. _classify_error (276-300) now checks the "evaluate
  exception" / "evaluate error" prefix BEFORE the refusal needles
  and returns evaluate_failed / delivery_uncertain / unsafe, with a
  comment stating page exception text can never classify as a safe
  refusal. Residual: classification of the remaining classes is
  still substring-based by design (the needles are the client's
  own refusal strings).
- A2 (navigate success labelled delivered_verified without any URL
  comparison): FIXED by honest labelling. _success_disposition
  (303-310) returns delivered_unverified for eval, peval and
  navigate; the README contract says the same. navigate() still
  does not compare the resulting URL (1166-1210; its re-read
  swallows exceptions), and that is now disclosed by the label
  instead of overstated.
- C1 (I22 never redacted the URL fragment; OAuth implicit-flow
  tokens passed through): FIXED. _redact_url (540-567) now runs
  fragment pairs through _redact_query_pairs when the fragment
  contains "=" or "&". Residual: a fragment without "=" or "&"
  (bare token or SPA route) is preserved verbatim.
- C2 (redaction matched exact parameter names only): FIXED, see
  the normalized stem matching above.
- F7 (I10 enabled gated, not polled, in scripts/a11y.py): FIXED
  (6b943977). wait_actionable (a11y.py:253-296) polls the disabled
  state until the 1 s cap, fails fast on stale trees, and also
  checks VISIBLE plus SHOWING (the F8 minor).
- F1 (a11y snapshot could certify an incomplete walk at the
  80-item cap): FIXED. observe() (a11y.py:118-124) sets
  truncated=True at the cap with an explicit comment, and
  incomplete includes it.
- F11 (I17 wait_for swallows every evaluate exception as not-yet,
  no terminal-state detection): PARTIALLY FIXED. The wait now has
  its own error code (wait_timeout), the CLI validates the budget
  (wait_timeout_required / wait_timeout_invalid), and a timeout
  preserves the action's own outcome in result.action_result. But
  wait_for itself (1212-1234) still treats every exception as
  not-yet, so a dead tab still burns the full budget; and its
  per-poll evaluate timeout is still hardcoded at 5 s (the F12
  minor).
- F13 (wait_timeout classification keys on the "wait_for timeout"
  message substring): STILL PRESENT (line 294), low risk because
  the string is generated by the client itself.

From the earlier RDP toolkit review (966a54c7, findings F1-F12);
no fix commits for these appear in the landed history, and the
code at a831e250 confirms:

- F1 HIGH (page exception text containing "noSuchActor" makes
  evaluate execute twice; _navigate_send also re-sends navigateTo
  to the descriptor actor after ANY target-actor error): STILL
  OPEN. evaluate() (1069-1082) retries on any RDPError whose text
  contains "noSuchActor" (_is_no_such_actor, 399-401), and
  _evaluate_once embeds the page-controlled exception text in that
  error string (1105). _navigate_send (1148-1166) still falls
  through to the second actor on any exception. Note the interplay
  with A1: the envelope now classifies such an error correctly,
  but the double execution itself is unchanged.
- F2 MODERATE (longString silent corruption): STILL OPEN.
  _fetch_long_string (1038-1061) breaks on a packet from the
  longString actor before checking whether it is an error packet,
  advances pos by the requested chunk size regardless of the
  actual substring length, and never verifies the assembled length
  against the grip's declared length.
- F3 MODERATE (navigate pin race; wait_load hides the re-attach
  refusal until timeout): STILL OPEN structurally. navigate()'s
  tail is unchanged (0.05 s sleep, exception-swallowing re-read);
  wait_load (1236-1261) now attempts a pinned re-attach when a tab
  is pinned, which mitigates but does not remove the race.
- F4 MODERATE (guard checks a cached URL; a tab that navigates
  itself after attach is evaluated against its old URL): STILL
  OPEN, documented in the landing report as an accepted residual
  (TOCTOU guard snapshot). _guard_current (828-831) still reads
  _current_tab, refreshed only by list_tabs/get_target.
- F5 HIGH as a class (denylist is a nine-word substring net):
  STILL OPEN. Same 9 patterns, no percent-decoding or other
  normalization before matching, redirect targets never checked,
  page content never inspected; sso, session, logon and
  non-English paths still pass. Scope URL patterns share the
  substring over-match (a pattern "example.com" also matches
  example.com.attacker.test). It is a heuristic net and should be
  described as one.
- F6 MEDIUM (parent-evaluate audit does not reliably persist):
  STILL OPEN in substance. Records are 80-char prefixes with no
  results; they reach disk only when a drive report path was set,
  so a peval run without --drive-report leaves no persistent
  trace; the report does not record that --allow-parent was
  enabled for a session with no parent evaluates, nor that the
  port-owner check was skipped via --allow-unmarked-test-attach.
- F7 MEDIUM (bench destructive, no lock, no report): PARTIALLY
  FIXED. bench (1368-1394) now refuses without the explicit
  unscoped-test opt-in and requires the port-owner marker (or the
  explicit unmarked-test flag). It still takes no lock file and
  writes no drive report.
- F8 MEDIUM (smoke runs with every fence down against the owner
  profile): UNCHANGED by design; rdp_smoke.py still constructs the
  client unscoped with allow_parent and no denylist, and navigates
  the selected tab to about:blank. The only control is procedural
  (README warning to use a throwaway/tasked tab); no in-tool guard
  was added.
- F9 MODERATE (evaluation results are not correlated to their
  sender; a late evaluationResult can be consumed by the next
  evaluate): STILL OPEN. _evaluate_once (1084-1097) accepts the
  first evaluationResult packet without checking its sender.
- F10 LOW (port-owner check is a hint): STILL OPEN.
  check_port_owner (404-439) matches any ss line carrying
  ":<port>", takes the first pid= on it, tests a cmdline substring
  once before connect, and embeds 300 chars of cmdline in the
  refusal message.
- F11 LOW (drive_report() has live side effects and re-pins):
  STILL OPEN. drive_report (1294-1320) performs live list_tabs,
  get_target (which re-pins) and probe evaluates, mutating the
  audit data it reports; the report command is not read-only.
- F12 LOW (smaller items): _open_parent still falls back to the
  first listed process when none is marked isParent (1109);
  approval keys are still tried as both tab ids and URL patterns
  (_approval_note, 813-826); a scope config's denylist still
  replaces the defaults wholesale (with the reverse error handled:
  an empty config list falls back to the defaults, _build_scope
  1438-1471).

## 4. What our channel does NOT have

- No MCP interface. scripts/zen-rdp exposes a Python library and a
  CLI only. (The repo does have scripts/mcp_bridge.py, but that
  serves the wider computer-use CLI surface, not this RDP channel;
  no MCP tool wraps the RDP operations.)
- No semantic element-interaction layer on the Zen DOM. Content
  interaction is raw JavaScript through eval: no element refs, no
  snapshot-qualified DOM nodes, no click/type-by-element API, no
  DOM snapshot command. Semantic interaction exists only on the
  separate AT-SPI lane (scripts/a11y.py: observe/query with refs,
  resolve, wait_actionable, act click/set_text), which sees the
  browser as a desktop accessibility tree, not as a DOM, and is
  not Zen-specific.
- No in-browser ask UI. Nothing injects UI into Zen, no
  zen_ask-style prompt, no page-side agent presence.
- No browser event stream. The client is strict request/response;
  unsolicited RDP packets (for example tabListChanged) are skipped
  inside request() while waiting for a reply (871-878) and are
  never surfaced. No event subscription, no console/log listener,
  no navigation or tab event feed.
- Spaces/Folders are not first-class context in zen-rdp. The RDP
  client has no workspace or folder operations at all; Zen
  internals (gZenWorkspaces, gZenFolders) are reachable only as
  raw chrome JS through the gated peval, and the smoke test only
  checks their typeof. Workspace/folder operations exist only in
  the Marionette prototype zen_live.py (improvements/, 11 ops:
  switch/move workspace, create/move/leave folder,
  move-folder-space, pin/unpin, move-tab, list, introspect), which
  cannot attach to the owner's current live Zen launch (no
  Marionette), plus the offline zen_sessions.py editor. Neither is
  part of the landed scripts/ channel.
- No screenshots, no OS input, no downloads/uploads handling, no
  cookie/storage API, no network interception. All by design:
  those stay on other lanes.
- No multi-tab concurrency: one client, one pinned tab, one
  request in flight; parallel drives are fenced out by the
  single-drive lock rather than supported.

## 5. Platform and testing

- Platform: the owner's Linux machine (Wayland session). The code
  is Linux-shaped: /proc/<pid>/stat and /proc/<pid>/cmdline
  parsing, `ss -tlnp`, fcntl.flock, pyatspi/AT-SPI for the a11y
  lane. zen-rdp itself is stdlib-only Python 3, no pip
  dependencies. Developed and unit-tested on clone2's Linux VM;
  live drives run on the owner's laptop through the machine-layer
  registry and wrapper.
- Test suites in the landed tree (test-method counts from the
  files at a831e250):
  - scripts/zen-rdp: test_scope_unittest.py 29 (scoping, denylist
    and approvals, drive-report diff, fail-closed marker,
    noSuchActor retry pinning, fake transport, no browser),
    test_envelope.py 18 (envelope and disposition),
    test_lock.py 14 (lock hardening), test_redaction.py 10.
    test_rdp_smoke.py is a script-style check of the smoke bind
    parser and exit-code map; test_rdp_client.py is a live
    self-test against a throwaway browser. Subtotal 71 unittest
    methods plus the two script checks.
  - scripts/a11y.py: tests/test_a11y.py 37, tests/test_a11y_cli.py
    2, tests/test_a11y_skeleton.py 13. Subtotal 52.
  - improvements/zen-sidebar: test_zen_sidebar.py 30 (zen_live and
    zen_sessions).
  - During the integration review, lanes A and B ran the zen-rdp
    and a11y suites green on clone2's VM (49 zen-rdp tests OK in
    the combined run recorded there, 39 a11y tests OK); the counts
    above are the landed files' method counts, which grew with the
    fix batches.
- Operational testing: rdp_smoke.py is the per-update gate (8
  checks, distinct exit codes); the R10 decision record carries
  acceptance and kill criteria for the lane.
