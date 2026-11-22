# Endpoint naming rule, batch 12 task 3 (P3 port split follow-up)

Work window 2026-11-22 10:54-11:00 +07 (03:54-04:00Z). Read-only source:
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
and resolver gaps below are still open, and the guard test in this
batch catches them.

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

## 3. Why localhost is forbidden: measured, not asserted

/etc/hosts on this VM maps localhost to both families:

    127.0.0.1 localhost
    ::1 localhost ip6-localhost ip6-loopback

And socket.getaddrinfo('localhost', 9223) on this VM, measured
2026-11-22 10:54 +07, returns ::1 first, then 127.0.0.1. A client
connecting to localhost:9223 therefore reaches Brave, while a
resolver that hardcodes the 127.0.0.1 default reaches Chromium.
Two correct-looking implementations disagree about which browser
localhost:9223 is, which is the definition of ambiguous. The
guard test pins this: test_localhost_resolves_to_ipv4_while_machine_prefers_ipv6
asserts the naive answer (127.0.0.1:9223) against the machine's
first getaddrinfo answer (::1) and they differ.

## 4. Known live endpoints

| Browser | Endpoint | Owner | Evidence |
|---|---|---|---|
| Brave | http://[::1]:9223 | clone1 | P3 probe log improvements/worker-click4-p3-probe-log.md section 2.5 (commit 924ec3f): ss shows [::1]:9223 LISTEN, users (("brave", pid=935106)); /json/version says Chrome/157.0.8103.79 (Brave's build); /json/list serves the clone1 tab 06074E282C000A95EF89CC9EBB8F9713, "(2) Chat - clone1". |
| Chromium | http://127.0.0.1:9223 | clone2 | Same log, section 2.5: ss shows 127.0.0.1:9223 LISTEN, users (("chromium", pid=8059)); /json/version says Chrome/157.0.8103.38; /json/list serves the clone2 tab D1374C7C994D3DA72678E20C7FD099A0, "(3) Chat - clone2". Chromium started Nov 21, profile ~/.config/chromium/Default. |
| Zen | Marionette 127.0.0.1:2828, not CDP | n/a | S2 flip log section 3.7: Zen alive (zen-bin PID 496121), Marionette on 127.0.0.1:2828. cu.py browser observe is CDP-only; Zen has no CDP endpoint in this registry. Do not add one by analogy. |

The S2 flip runs 1-5 (improvements/s2-flip-runs/run-1..5.json) corroborate
the split in the live direction: every run records brave on
http://[::1]:9223 outcome sent (V12 found True) and chromium on
http://127.0.0.1:9223 outcome failed-unverified (CDP timeout
Input.dispatchMouseEvent, 5000 ms). The two endpoints behaved as two
different browsers across all five runs, which is only possible
because they are two different browsers.

Adding a browser: pick a free port, start it with an explicit
--remote-debugging-port, record `ss -ltnp` plus /json/version plus
the tab list, add one row to KNOWN_ENDPOINTS in
scripts/endpoint_names.py, and add a resolve test for it. Never
reuse a port across families, never add a browser by editing a call
site to use a bare port.

## 5. What the S2 harness already fixed

Commit 350934a on todolist-push ("C4-S2-FLIP wiring: code-exec
--endpoint, S2 flip harness v2, wiring tests", 2026-11-22 02:48 +07):

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
   (lines 2440-2456) allows hostname in ('localhost', '127.0.0.1',
   '::1'), and browser_start (line 2459) enforces the same rule.
   scripts/cdp.mjs line 120 accepts the same three hostnames, and
   line 142 accepts them for the debugger WebSocket. So
   'http://localhost:9223' passes every check in the stack and then
   reaches whichever family the resolver prefers, which on this VM
   is ::1 (section 3). The wiring tests cover non-loopback refusal
   (test_non_loopback_endpoint_refused) and bad-port refusal
   (test_bad_port_refused) but never test localhost. Guard:
   test_localhost_host_is_rejected, test_localhost_forms_are_rejected.
2. A missing port silently defaults to 9223. scripts/cu.py line 2452
   and browser_start line 2464 both do `port=url.port or 9223`. An
   endpoint written without a port is accepted and lands on
   whichever browser holds 9223 in the resolved family. Guard:
   test_missing_port_is_rejected_no_silent_default,
   test_url_without_port_is_rejected.
3. No browser-identity check anywhere. Nothing verifies the process
   at an endpoint is the named browser. browser_start fetches
   /json/version only to check aliveness, and a live listener that
   is not ours is reused as-is (reused True). The P3 probe proved
   identity only by comparing version strings (.38 Chromium vs .79
   Brave) and ss users, and the harness never reads either. If the
   laptop state drifts (Brave relaunched without the flag, Chromium
   taking [::1]:9223), the harness trusts its dict and silently
   drives the wrong browser. The guard test does NOT fix this
   either; it fixes the spec layer. A live identity check (read
   /json/version, compare the Browser string against the registry
   row before the first send) is the follow-up, recorded here as
   open work, not built in this batch.
4. The `browser` CLI path skips validation. scripts/cu.py lines
   3308-3314 pass `args.endpoint or BROWSER_ENDPOINT` straight into
   the CDP request without calling _validate_browser_endpoint; only
   cdp.mjs enforces loopback, and it accepts localhost (gap 1).
   Guard: the resolver in scripts/endpoint_names.py is the single
   place a caller should validate through; the port can wire it in.
5. The V12 and P9 helpers are unverifiable from the repo.
   scripts/s2_flip_live.py passes the endpoint as argv to
   /tmp/s2-v12.mjs and /tmp/s2-p9.mjs, which are laptop /tmp files,
   not in the repo on any branch. Their endpoint handling cannot be
   checked from here; the harness performs no validation on that
   path. Stated as UNVERIFIED, not assumed safe.
6. Main is behind on the same gaps. On main, scripts/cu.py has no
   _validate_browser_endpoint at all and its default BROWSER_ENDPOINT
   is 'http://127.0.0.1:9222' (line 35), while scripts/cdp.mjs line
   120 accepts localhost exactly like the todolist-push copy. The
   resolver and guard test in this batch are self-contained (pure
   stdlib, no cu.py or cdp.mjs dependency) precisely so they run on
   main and port cleanly.

## 7. The guard test

File: tests/test_endpoint_naming_guard.py, 29 tests, all passing.
Resolver: scripts/endpoint_names.py (KNOWN_ENDPOINTS registry,
resolve_endpoint, parse_endpoint_ref, plus naive_resolve, the old
behavior kept only to demonstrate the trap).

Run, 2026-11-22 10:54:45 +07 (03:54:45Z), repo venv python:
`python3 -m unittest tests.test_endpoint_naming_guard -v`
Ran 29 tests in 0.014 s (first run 0.005 s), OK. Wall 0.169 s
including interpreter start. Log: ~/workspace/tools/b12t3/guard-pass.log.

What the 29 tests cover: correct resolution for both browsers;
same port, different endpoints; missing/unknown browser; localhost
host in both resolvers; swapped loopback family both directions;
missing host, missing port (string and None), wrong port, bad port
range, non-loopback host, missing owner, owner mismatch, registry
completeness; bare port, localhost forms, URL without port, URL
without a browser, swapped-family URL, non-http scheme,
non-loopback URL, fully-qualified refs; the naive trap (bare-port
Brave intent lands on Chromium; localhost answer disagrees with
the machine's resolver order; naive ignores the browser name;
naive accepts a missing port); and the guard itself (all 9
ambiguous specs rejected by the guard, all 9 let through by the
naive resolver).

Failing-first, 2026-11-22 10:54:38 +07: the same 25 guard tests run
with the resolvers swapped to the naive behavior (scratch runner
~/workspace/tools/b12t3/failing-first-run.py, log
~/workspace/tools/b12t3/failing-first.log): Ran 25 tests, FAILED
(failures=19), elapsed 0.0072 s. The 6 that pass against the naive
resolver are the positive-resolution tests (fully-qualified specs
resolve to plausible URLs); every rejection test fails, because the
naive resolver never rejects. That is the proof the guard is
load-bearing: wired to the old behavior, it fails 19 of 25.

## 8. Porting note

Deliverables are on main, ready to port: scripts/endpoint_names.py
plus tests/test_endpoint_naming_guard.py plus this doc. Porting to
todolist-push is the coordinator's decision; nothing was ported in
this batch. When ported, the natural wiring is for cu.py
_validate_browser_endpoint to reject 'localhost' and a missing port
(gaps 1 and 2), and for the `browser` CLI path to call the
validator (gap 4). The live identity check (gap 3) is separate open
work and is not claimed here.
