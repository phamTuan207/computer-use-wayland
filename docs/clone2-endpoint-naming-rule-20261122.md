# Endpoint naming rule, batch 12 task 3 (P3 port split follow-up)

Work window 2026-11-22 10:54-11:00 +07 (03:54-04:00Z). Fix pass
2026-11-22 11:05-11:20 +07: council 1/2/3 ISSUES plus redteam BROKEN,
all corrections applied and re-verified against primary sources
(see section 7 for the updated counts). Read-only source:
origin/todolist-push, HEAD 3724f52 at read time. Deliverables on main:
scripts/endpoint_names.py (the resolver), tests/test_endpoint_naming_guard.py
(the guard test). Nothing ported to todolist-push; porting is the
coordinator's decision.

## 1. The incident, in one paragraph

Port 9223 is two browsers. On the laptop, Chromium (clone2 chat) has
listened on 127.0.0.1:9223 since Nov 21, and Brave (clone1 chat), when
relaunched with --remote-debugging-port=9223, could not bind IPv4
because 9223 was taken, so it listened on [::1]:9223 only. A run that
assumes "port 9223 is Brave" silently drives Chromium instead. The P3
probe found this the hard way: its first CDP round measured the
Chromium tab (title "(3) Chat - clone2") and believed it was Brave,
until `ss` and /json/version proved otherwise. The S2 flip harness
fixed the harness-level form of this in commit 350934a; the validator
and resolver gaps below are still open. The guard test in this batch
catches them only inside the new module (scripts/endpoint_names.py),
which nothing in production calls yet: the production paths below
still accept localhost and port-less endpoints today, and wiring the
resolver into them is the follow-up (section 8). The guard is
load-bearing for the module, not for the live stack.

## 2. The rule

Every endpoint reference names a browser, and carries four fields,
all required:

| Field | Rule |
|---|---|
| browser | A registry key in scripts/endpoint_names.py KNOWN_ENDPOINTS: 'brave' or 'chromium'. Unknown browser: register it first, never guess. |
| host | An IP literal, '127.0.0.1' or '::1'. Never 'localhost'. |
| port | An integer 1..65535, always written out. Never defaulted. |
| owner | The chat or purpose the browser serves, e.g. 'clone1' for Brave, 'clone2' for Chromium. |

Canonical form is the CDP URL the resolver returns: 'http://[::1]:9223'
for Brave, 'http://127.0.0.1:9223' for Chromium. A reference that
fails any field is rejected with EndpointAmbiguityError, never
repaired by guessing.

Forbidden forms, each rejected by the resolver:

- A bare port: '9223', ':9223'. A port alone names no browser.
- 'localhost' in any form: 'localhost', 'localhost:9223',
  'http://localhost:9223'. See section 3 for the proof that
  localhost names no single browser.
- A URL without a port: 'http://[::1]', 'http://127.0.0.1'. The
  old code defaulted a missing port to 9223, which is exactly the
  port two browsers share.
- A host plus port with no browser name. Host plus port alone do
  not name a browser; the caller must state which browser it
  expects, and the host and port are checked against that
  browser's registry row.
- A swapped loopback family: brave on 127.0.0.1, chromium on ::1.
  That is the P3 trap written as a spec, and it is rejected, not
  silently corrected.
- A non-loopback host, a non-http scheme, a port outside 1..65535.
- Anything more than a bare endpoint: a URL carrying userinfo,
  a path, a query, or a fragment. The reference must be exactly
  host plus port; extra parts are rejected, not silently dropped.

## 3. Why localhost is forbidden: measured, not asserted

/etc/hosts on this VM maps localhost to both families:

    127.0.0.1 localhost
    ::1 localhost ip6-localhost ip6-loopback

And socket.getaddrinfo('localhost', 9223) on this VM, measured
2026-11-22 10:54 +07, returns both answers, ::1 and 127.0.0.1. The
proof is the two answers, not their order: the order is
resolver-dependent (glibc RFC 6724 sorting, /etc/gai.conf), so a
machine with IPv4-first resolution lists 127.0.0.1 first and the
same reference resolves to the other browser. Whichever family
comes first, localhost names no single browser, because the answer
depends on the resolver, not on the reference. The guard test pins
this order-independently: test_localhost_answer_depends_on_the_resolver
asserts both families are present in the getaddrinfo answers and
that the naive answer (127.0.0.1:9223) matches only one of them.

The mechanism is worse than order alone. Live experiment on this
VM, 2026-11-22 11:05 +07 (scripts preserved in
~/workspace/tools/b12t3/localhost-fallback.py and
localhost-fallback.mjs): with listeners on both families of one
port, Python urllib and Node fetch both reach ::1; with the ::1
listener stopped, both fall back to 127.0.0.1 and succeed. So
localhost:9223 means "whichever browser is up", not one browser:
if Brave is down, a localhost reference silently reaches Chromium,
and vice versa. (An earlier redteam claim that Node fetch does not
fall back did not reproduce on Node 24: the experiment shows fetch
reaching v4 after v6 stops.)

One correction to the naive model in scripts/endpoint_names.py:
naive_resolve rewrites bare 'localhost:9223' to 127.0.0.1:9223, but
that is a hypothetical hardcoding resolver, not the old stack. The
real pre-fix stack passed a localhost endpoint unchanged to
cdp.mjs, whose fetch resolves it through the OS (::1 first on this
VM, i.e. Brave). The old stack's real localhost answer was Brave,
not Chromium. The rule does not depend on which answer is right:
any resolver that turns localhost into one family disagrees with
some other correct-looking resolver, and the fallback experiment
shows the answer can change at runtime too.

## 4. Known live endpoints

| Browser | Endpoint | Owner | Evidence |
|---|---|---|---|
| Brave | http://[::1]:9223 | clone1 | P3 probe log improvements/worker-click4-p3-probe-log.md section 2.5 (commit 924ec3f) for ss and version: ss shows [::1]:9223 LISTEN, users (("brave", pid=935106)); /json/version says Chrome/157.0.8103.79 (Brave's build). The clone1 tab itself is section 2.6: /json/list serves tab 1563355BC86478EBAF3D0BDA179767FD, "(2) Chat - clone1". (The tab 06074E282C000A95EF89CC9EBB8F9713 in the S2 flip run JSONs is a different Brave launch, relaunch 10:02 +07, PID 987006.) |
| Chromium | http://127.0.0.1:9223 | clone2 | Same log: ss (section 2.5) shows 127.0.0.1:9223 LISTEN, users (("chromium", pid=8059)); /json/version says Chrome/157.0.8103.38. The clone2 tab is section 2.2: /json/list serves tab D1374C7C994D3DA72678E20C7FD099A0, "(3) Chat - clone2". Chromium started Nov 21, profile ~/.config/chromium/Default. |
| Zen | Marionette 127.0.0.1:2828, not CDP | n/a | S2 flip log section 3.7: Zen alive (zen-bin PID 496121), Marionette on 127.0.0.1:2828. cu.py browser observe is CDP-only; Zen has no CDP endpoint in this registry. Do not add one by analogy. |

The S2 flip runs 1-5 (improvements/s2-flip-runs/run-1..5.json) corroborate
the split in the live direction: every run records brave on
http://[::1]:9223 outcome sent (V12 found True) and chromium on
http://127.0.0.1:9223 outcome failed-unverified. The chromium failure
is a dom_act timeout of about 5000 ms in all five runs (5002-5003 ms
in the program log, elapsed 5102-5106 ms); runs 2-5 name the sub-step
in the log ("CDP timeout: Input.dispatchMouseEvent"), while run 1
records only the 5003 ms timeout without naming it. The two endpoints
behaved as two different browsers across all five runs, which is only
possible because they are two different browsers.

Adding a browser: pick a free port, start it with an explicit
--remote-debugging-port, record `ss -ltnp` plus /json/version plus
the tab list, add one row to KNOWN_ENDPOINTS in
scripts/endpoint_names.py, and add a resolve test for it. Never
reuse a port across families, never add a browser by editing a call
site to use a bare port.

Moving a browser to a new port: edit the existing row, do not add a
second one. The P3 log itself suggests giving Brave a free port such
as 9224 (probe log lines 375, 418); following that suggestion means
changing the `brave` row's port to 9224, re-recording `ss` plus
/json/version evidence for the new listener, and updating the tests
that pin the old port (test_wrong_port_is_rejected and
test_registry_covers_both_live_browsers, which pins port 9223). One
row per browser cannot represent a transition period or two instances
of the same browser; during a move, the old row is wrong from the
moment the browser restarts, so the move and the row edit must land
together.

## 5. What the S2 harness already fixed

Commit 350934a on todolist-push ("C4-S2-FLIP wiring: code-exec
--endpoint, S2 flip harness v2, wiring tests", 2026-11-22 09:48 +07, 02:48Z):

- scripts/s2_flip_live.py lines 76-79: a BROWSERS dict names the
  endpoint per browser ('brave' -> 'http://[::1]:9223', 'chromium' ->
  'http://127.0.0.1:9223'). Every use in the harness (route_browser
  line 301, send_browser line 362, seed_scratch line 419,
  close_scratch line 432, P9 capture line 501) looks the endpoint up
  from that dict by browser key; no call site writes a port literal.
- scripts/s2_flip_live.py line 562: --browser is restricted to
  choices ['brave', 'chromium', 'both']. There is no --endpoint flag
  on the harness at all, so a caller cannot pass an ambiguous
  endpoint into it.
- scripts/s2_flip_live.py line 8 (docstring): "Never assume port
  9223 is Brave."
- scripts/cu.py: --endpoint added to the code-exec subparser (line
  3003), validated loopback-only by _validate_browser_endpoint and
  applied to that program only, with the retained default restored
  in a finally (lines 3081-3092), exactly like the browser tabs
  one-command override. Before this fix, code-exec had no endpoint
  flag and every program drove the default 127.0.0.1:9223, so a
  program aimed at Brave would silently drive Chromium; the flip
  log section 4.1 calls this "the P3 trap in code form".
- tests/test_s2_flip_wiring.py: 9 tests, 9/9 OK per the flip log
  section 4.1 (override reaches the backend and restores the
  default; no flag keeps the default; non-loopback and bad-port
  endpoints refuse before any program runs).

## 6. What is still missing, and what the guard test catches

The harness fix is by construction: hardcoded constants in one file,
plus a CLI with no endpoint flag. It is not a validating resolver,
and the layers underneath it still accept ambiguous specs. Each gap
below is quoted from todolist-push at HEAD 3724f52, and each is
covered by a guard test in tests/test_endpoint_naming_guard.py.

1. The validator accepts localhost. scripts/cu.py _validate_browser_endpoint
   (lines 2440-2457) allows hostname in ('localhost', '127.0.0.1',
   '::1'), and browser_start (line 2459) enforces the same rule.
   scripts/cdp.mjs line 120 accepts the same three hostnames, and
   line 142 accepts them for the debugger WebSocket. So
   'http://localhost:9223' passes every check in the stack and then
   reaches whichever family the resolver prefers (section 3: on this
   VM that is ::1, and either client falls back to the other family
   if the first refuses). The wiring tests cover non-loopback refusal
   (test_non_loopback_endpoint_refused) and bad-port refusal
   (test_bad_port_refused) but never test localhost. Guard:
   test_localhost_host_is_rejected, test_localhost_forms_are_rejected,
   test_uppercase_localhost_gets_the_localhost_message.
2. A missing port silently defaults to 9223. scripts/cu.py line 2452
   and browser_start line 2464 both do `port=url.port or 9223`. An
   endpoint written without a port is accepted and lands on
   whichever browser holds 9223 in the resolved family. Guard:
   test_missing_port_is_rejected_no_silent_default,
   test_url_without_port_is_rejected.
3. No automated browser-identity check. Nothing in the harness or
   the stack asserts the process at an endpoint is the named browser
   before acting on it. browser_start fetches /json/version only to
   check aliveness, and a live listener that is not ours is reused
   as-is (reused True). The run JSONs do carry identity evidence
   after the fact (per-browser tab_title and target_id: run 1 brave
   "(2) Chat - clone1" 06074E282C000A95EF89CC9EBB8F9713, chromium
   "Chat - clone2" D1374C7C994D3DA72678E20C7FD099A0, same pattern in
   runs 2-5), and a swapped endpoint would show the wrong title
   under the browser key, but no code asserts on it. The P3 probe
   proved identity only by comparing version strings (.38 Chromium
   vs .79 Brave) and ss users, and the harness never reads either.
   If the laptop state drifts (Brave relaunched without the flag,
   Chromium taking [::1]:9223), the harness trusts its dict and
   silently drives the wrong browser. The guard test does NOT fix
   this either; it fixes the spec layer. A live identity check (read
   /json/version, compare the Browser string against the registry
   row before the first send) is the follow-up, recorded here as
   open work, not built in this batch.
4. The `browser` CLI path skips validation for non-start operations.
   scripts/cu.py line 3313 (the request dict for observe/tabs/act)
   passes `args.endpoint or BROWSER_ENDPOINT` straight into the CDP
   request without calling _validate_browser_endpoint; only cdp.mjs
   enforces loopback, and it accepts localhost (gap 1). The start
   branch (lines 3308-3311) is different: it passes the endpoint to
   browser_start, which does enforce the loopback rule (still
   accepting localhost and defaulting a missing port, gaps 1-2).
   Guard: the resolver in scripts/endpoint_names.py is the single
   place a caller should validate through; the port can wire it in.
5. The V12, P9, and seed helpers are unverifiable from the repo.
   scripts/s2_flip_live.py passes the endpoint as argv to
   /tmp/s2-v12.mjs (LAPTOP_V12, line 72), /tmp/s2-p9.mjs (LAPTOP_P9,
   line 73), and /tmp/s2-seed.mjs (LAPTOP_SEED, line 74), which are
   laptop /tmp files, not in the repo on any branch. Their endpoint
   handling cannot be checked from here; the harness performs no
   validation on that path. Stated as UNVERIFIED, not assumed safe.
6. Main is behind on the same gaps. On main, scripts/cu.py has no
   _validate_browser_endpoint at all and its default BROWSER_ENDPOINT
   is 'http://127.0.0.1:9222' (line 35), while scripts/cdp.mjs line
   120 accepts localhost exactly like the todolist-push copy. Main's
   browser_start (scripts/cu.py line 1838) also accepts localhost
   (line 1842) and defaults a missing port to 9222 (line 1843), and
   main's warm_browser.py launches on 9222 on a missing port (line
   210) while its validate_endpoint defaults a missing port to 80
   (line 89). The resolver and guard test in this batch are
   self-contained (pure stdlib, no cu.py or cdp.mjs dependency)
   precisely so they run on main and port cleanly.
7. warm_browser.py has the same two gaps in its own validator.
   scripts/warm_browser.py validate_endpoint (lines 83-95, both
   branches) accepts localhost (LOOPBACK_HOSTS, line 60, includes
   it) and defaults a missing port to 80 (`port = url.port or 80`,
   line 89), while _launch_chromium (line 210) defaults a missing
   port to 9223 on todolist-push and 9222 on main. It is on the live
   path: browser_start calls warm_browser.ensure_warm (cu.py line
   2496), and ensure_warm, new_task_context, and status all route
   through validate_endpoint. The validate-80 vs launch-9223 split
   means a no-port endpoint passes validation but is probed and
   launched on a different port.
8. chromium_cli.py has the same two gaps. Its validate_endpoint
   (line 108) accepts localhost (LOOPBACK_HOSTS, line 86) and
   defaults a missing port to 80 (line 114); DEFAULT_ENDPOINT is
   'http://127.0.0.1:9223' (line 78) behind a --endpoint global flag
   (line 630); ws_connect (line 239) accepts localhost for the
   debugger WebSocket, defaults a missing port to 80 (line 245),
   then does socket.create_connection((url.hostname, port)) (line
   251), which resolves per-system (::1 first here).
9. The broker/relay path has no endpoint validation at all.
   scripts/session_remote.py contains no 'endpoint' string: the
   relay passes broker commands through with no endpoint check.
   scripts/session_driver.py relay() hardcodes cu.BROWSER_ENDPOINT
   to 'http://127.0.0.1:9223' on todolist-push (line 72) and to
   'http://127.0.0.1:9222' on main (line 71) for the whole relay
   session. Any broker command without an explicit --endpoint runs
   against that hardcoded default with no browser name; on main the
   default is port 9222. The S2 harness's own broker calls pass
   --endpoint explicitly, so the harness is not exposed, but the
   path is.

## 7. The guard test

File: tests/test_endpoint_naming_guard.py, 35 tests, all passing.
Resolver: scripts/endpoint_names.py (KNOWN_ENDPOINTS registry,
resolve_endpoint, parse_endpoint_ref, plus naive_resolve, the old
defaults kept only to demonstrate the trap, with its localhost leg
labelled as a hypothetical, not the old stack, see section 3).

Run, 2026-11-22 11:09:15 +07 (04:09:15Z), repo venv python:
`python3 -m unittest tests.test_endpoint_naming_guard -v`
Ran 35 tests in 0.005 s, OK. Log:
~/workspace/tools/b12t3/guard-pass2.log. (The first version ran 29
tests in 0.014 s, log ~/workspace/tools/b12t3/guard-pass.log; the
fix pass added 6 tests.)

What the 35 tests cover: correct resolution for both browsers;
same port, different endpoints; missing/unknown browser; localhost
host in both resolvers (including uppercase LOCALHOST getting the
localhost message); swapped loopback family both directions;
missing host, missing port (string and None), wrong port, bad port
range, non-loopback host, missing owner, owner mismatch, registry
completeness; bare port, localhost forms, URL without port, URL
without a browser, swapped-family URL, non-http scheme,
non-loopback URL, userinfo, path/query/fragment, unhashable browser,
out-of-range and non-numeric port messages, fully-qualified refs;
the naive trap (bare-port Brave intent lands on Chromium; the
localhost answer depends on the resolver; naive ignores the browser
name; naive accepts a missing port); and the guard itself (all 9
ambiguous specs rejected by the guard, all 9 let through by the
naive resolver).

Failing-first, 2026-11-22 11:09 +07: the same guard tests run with
the resolvers swapped to the naive behavior (scratch runner
~/workspace/tools/b12t3/failing-first-run.py, log
~/workspace/tools/b12t3/failing-first2.log): Ran 31 tests, FAILED
(failures=25), elapsed 0.025 s. The 6 that pass against the naive
resolver are: brave resolves, chromium resolves,
same-port-different-endpoints, fully-qualified refs resolve,
registry completeness, and naive-lets-every-ambiguous-spec-through
(the meta-test, which passes by construction because it asserts
the naive resolver lets specs through). Every rejection test fails,
because the naive resolver never rejects. That is the proof the
guard is load-bearing for the new module: wired to the old
behavior, it fails 25 of 31. It is not proof about production:
production does not call this module yet (section 1), so the
production paths in section 6 still accept what the guard rejects,
and wiring the resolver in is the follow-up.

Fix-pass note: one council 1 correction was checked and REJECTED,
not applied. It claimed the override block's save line
(previous_endpoint=BROWSER_ENDPOINT) sits at line 3080, outside
the doc's cited range 3081-3092. The save is at line 3081, inside
the cited range (verified by direct read of cu.py lines 3078-3084
on todolist-push). The citation stands as written.

## 8. Porting note

Deliverables are on main, ready to port: scripts/endpoint_names.py
plus tests/test_endpoint_naming_guard.py plus this doc. Porting to
todolist-push is the coordinator's decision; nothing was ported in
this batch. When ported, the natural wiring is for cu.py
_validate_browser_endpoint to reject 'localhost' and a missing port
(gaps 1 and 2), and for the `browser` CLI path to call the
validator (gap 4). One limit on that wiring: _validate_browser_endpoint
takes only a URL string, so the resolver's core check (browser name
plus owner against the registry) cannot be expressed through the
current validator signature; the validator or its call sites need a
browser argument for the full rule to apply, and the `browser` CLI
path has no browser-name argument to pass today. On main the
validator does not exist at all (gap 6), so the port target is
todolist-push, where it does. The live identity check (gap 3) is
separate open work and is not claimed here.
