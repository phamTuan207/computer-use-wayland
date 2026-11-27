# Redteam review: R10 seamless-control landing (27/11/2026)

Independent redteam attack on switching the operating configuration
from the interim two-profile split to the RDP lane (route 3c) on the
owner flag-free Zen session. Question: why would the switch fail,
break, or endanger the owner browsing, data, or accounts? Builders
assumed optimistic; claims tested against evidence.

Scope read: decision doc
(`r3l3-run-wt/improvements/r10-seamless-decision-20261127.md`),
L1-L6 landing reports, landed code in
`r3l3-run-wt/scripts/zen-rdp/` (`rdp_client.py`, `rdp_smoke.py`,
tests, README), and cited JSON/JSONL evidence. Unit tests re-run by
this reviewer: `test_scope_unittest` 17/17 PASS, `test_rdp_smoke`
PASS. No laptop access, no owner Zen touched, no commits.

Evidence labels used per attack:

- PROVEN: demonstrated by live evidence or by direct code inspection
  of the landed files (the flaw exists today).
- PLAUSIBLE: mechanism is real in code/evidence, trigger not yet
  observed live.
- SPECULATION: possible in principle, no supporting evidence in the
  packet. Flagged as such, never load-bearing.

Verdicts per attack: **blocks landing** (switch must not happen
until fixed or explicitly waived by the owner in writing),
**condition** (land only with the stated operating constraint),
**acceptable risk** (evidence supports living with it).

## Summary of what the builders got right

Fairness first, because several headline claims survive attack:

- Google entry under the exact RDP pref set with agent attached:
  W4 throwaway 3/3 SERPs, L6 real profile 5/5 SERPs, no
  unusual-traffic wall. This is the leg Route 1 failed 6/6 flagged.
  Kill criterion 6 (RDP Google-entry failure) is genuinely not
  triggered.
- Webdriver probe CLEAN native-false on throwaway and real profile
  (L6 `smoke-real.json`, `steps.json` step1/step7). No shim needed;
  flag-free RDP does not set `navigator.webdriver`.
- Loopback-only bind verified repeatedly (`ss` 127.0.0.1:6021,
  non-loopback connect refused, L6 step7). Remote network attach is
  not the problem. Local attach is (Attack 2).
- Zen-internals control via parent target is real on throwaway
  (L1: 5 reads, 3 write families, read-back + revert). The API
  surface exists and is fast.
- Concurrency holds in the tested shapes (L2: 321/322 evaluates OK
  across DevTools open/console/close; L6 step6: 31/31 + typing
  intact). Background-tab RDP work does not steal focus.
- Restore of `user.js`/`prefs.js` is sha256-proven (L6
  `restore.json`). The acceptance run did not strand the owner
  profile in RDP config.

The landing problem is not that RDP fails to work. It is that the
safety envelope around same-session control (who may attach, which
tabs an agent may touch, what happens with two agents, what stops
a broken update from being driven) is voluntary and procedural in
the landed code, while the decision doc requires it to be
tool-enforced and fail-closed. Details below.

---

## Attack 1: P2 coolors CHALLENGE-CF means the owner will hit challenges in daily browsing

- Severity: Medium (usability, not safety)
- Evidence class: PROVEN that challenges are probabilistic; the
  daily-rate extrapolation is SPECULATION on this packet.
- Verdict: **acceptable risk**, with a reporting condition.

Evidence. W4 throwaway panel (valid landings): P1 timeanddate 1/2
(one CHALLENGE-CF, one PASS on sequential visits, warmth possible),
P2 coolors PASS, P5 codeforces PASS, C1 example.com PASS; flagged-raw
control CHALLENGE-CF on both P1 and P2 (W4 report, Cloudflare panel
+ control tables). L6 real profile: SERPs 5/5 PASS; landings P1
PASS, P2 coolors CHALLENGE-CF ("Just a moment..."), P5 PASS, C1
PASS, Q5 SERP-only PASS (`step2-panel.json`, `steps.json` step2);
control flagged-raw CHALLENGE-CF on P1 and P2 (`control.json`).

Analysis. Combined valid landings under RDP: P1 2/3 PASS, P2 1/2
PASS, P5 2/2, C1 2/2. Roughly 2 challenges in 9 landings, all on
Cloudflare-fronted sites, none on Google SERPs. Crucially, P2
challenged under BOTH RDP and flagged control in L6, and P1
challenged under flagged in both runs but passed under RDP in L6.
The evidence supports "RDP lane is strictly better than flagged on
this panel" and "Google entry works". It does NOT support any daily
challenge rate for the owner, for three reasons:

1. No flag-free, no-RDP human baseline arm was run. Without it, the
   P2 challenge cannot be attributed to RDP prefs vs IP reputation
   vs coolors policy vs profile warmth. Coolors may challenge this
   IP for a plain human too. The packet cannot distinguish.
2. Acceptance step 2 requires "cold repeats across different
   hours". L6 ran one warm session (14:36-15:11, same IP, same
   profile with cookies/history). That requirement is unmet; step 2
   is PARTIAL by its own text, which L6 honestly reports.
3. n is 1-2 per site. Cloudflare decisions are known-probabilistic
   (W4 P1 split on sequential visits proves it). A 25% point
   estimate from n=4 real-profile landings has no predictive value
   for the owner week.

Control-arm caveat: L6 control legs both errored in `zen_cli open`
("window.open did not produce a new tab") yet recorded title "Just
a moment..." (`control.json`). The challenge verdicts are plausible
but the control method is sloppy; the void rule is satisfied only
weakly. W4 control (cleaner) carries the weight.

What this does not do: it does not block landing. The decision doc
pre-registered "panel probabilistic, no never-blocked claim" and
set the kill line at Google-entry failure, not panel perfection.
The owner daily path that matters (search) passes. Condition: any
landing announcement must state the probabilistic panel result
plainly (P2 challenged on real profile) and must not claim
"never blocked". A cold-repeat panel across hours is still owed
before anyone quotes a pass rate.

## Attack 2: Silent attach is unauthenticated local code execution in the owner logged-in browser (RT-04)

- Severity: Critical (account takeover surface)
- Evidence class: PROVEN.
- Verdict: **blocks landing** until the owner decision is recorded
  in writing, per the decision doc own requirement.

Evidence. Config: `devtools.debugger.prompt-connection=false` +
`devtools.debugger.remote-host=127.0.0.1` (L4 report section 4,
generic RDP pref set). L6 step7: "Unrelated local process
attach+evaluate succeeded silently" (`steps.json` step7,
`unrelated_attach: attach+evaluate ok (1+1=2)`). Decision doc,
"What remains before landing": RT-04 silent-attach acceptance is
"an owner-level security decision, NOT yet recorded. Landing
requires it in writing." L6 report step7 asserts "recorded as
RT-04 owner-accepted behavior (14:00)" but cites no record file,
message, or registry field. This reviewer found no written record
in the packet. The two statements conflict; the decision doc
requirement is unmet on evidence provided.

Threat analysis. Loopback-only bind stops remote network attackers.
It stops nobody local. Any process that can open a TCP connection
to 127.0.0.1:6021 and speak length-prefixed JSON RDP gets:

- `evaluateJSAsync` in any tab origin: read DOM, call authenticated
  APIs with the owner cookies (HttpOnly cookies are not readable
  via `document.cookie`, but same-origin `fetch` rides them),
  exfiltrate page content, submit forms.
- Parent-process target evaluate (chrome JS): full browser
  privilege. L1 proves workspace/folder/tab manipulation; chrome
  JS can in principle reach sessionstore, preferences, and login
  manager APIs. The packet does not test credential extraction and
  this review does not claim it was demonstrated; the privilege
  level is the point. PLAUSIBLE for full credential access,
  PROVEN for tab/session control.
- No authentication, no per-client token, no audit log on the
  server side. RDP with prompt disabled has no client identity.
  The drive report is written by the client, voluntarily.

Who are "local processes" on this machine? By standing rule the
fleet runs agent CLIs with full access (Codex danger-full-access,
FCC skip-permissions, opencode). Any compromised dependency, build
script, MCP server, or misbehaving agent with shell access is
already local code execution; RDP attach upgrades that to browser
session takeover without touching profile files on disk. Browser
extensions are a lesser vector (WebExtension APIs cannot open raw
TCP; `fetch` to the RDP port speaks HTTP, not RDP framing), and
websites cannot open raw TCP either. The realistic attackers are
native local processes and the agent fleet itself. That includes
the well-meaning case: any agent that can run `rdp_client.py`
unscoped (Attack 3) is indistinguishable from an attacker to the
server.

Mitigations present: loopback bind (real), port-owner guard
(client-side only; stops the client attaching to the wrong server,
does nothing to stop other clients). No server-side mitigation
exists in Firefox RDP for this mode.

This is exactly why the decision doc made it an owner decision.
Technical work cannot close it; only informed owner acceptance
(or a different design, e.g. prompt-connection=true with its UX
cost, or an authenticating proxy, neither built) closes it.
Landing the switch without that record would silently convert the
owner daily browser into a local-RPC endpoint. Block.

## Attack 3: RT-20 scoping is voluntary, default-off where it matters, and bypassable inside the landed client

- Severity: High (credential-tab protection is the stated purpose)
- Evidence class: PROVEN (code inspection + live evidence).
- Verdict: **blocks landing** in default configuration; **condition**
  if a machine-layer wrapper enforces scope + denylist and refuses
  unscoped owner-port sessions.

The builders claim "tool-enforced tab scoping". The landed code
enforces scope only on the cooperative high-level path, and the
safe configuration is opt-in. Bypass inventory, all in
`scripts/zen-rdp/rdp_client.py` unless noted:

1. **Unscoped is allowed.** Empty `Scope` matches everything
   (`Scope.matches`, line 115). Construction prints
   `UNSCOPED_WARNING` (line 220) and proceeds. CLI prints the
   warning (line 817) and proceeds. The only fail-closed check is
   the port marker. An agent that forgets `--scope-*` gets every
   tab including credential tabs, with a stderr warning as the
   entire control. L3 report admits enforcement "constrains this
   tool sessions, not other local processes". True, and weaker: it
   does not even constrain this tool unless asked.
2. **Denylist default OFF.** `_build_scope` (line 747) enables
   patterns only from `--scope-config` or `--use-default-denylist`
   (line 758). Default CLI has no denylist. L6 step3 enabled it
   explicitly; nothing in the landed defaults requires it. README
   describes the denylist without foregrounding default-off.
3. **Raw `request()` is unguarded.** `RDPClient.request` (line 309)
   sends any RDP packet to any actor with no `_guard` call. Guards
   live in `get_target` (line 395/401), `evaluate` (line 478),
   `navigate` (line 523). Any code importing the client can call
   `request({"to":"root","type":"listProcesses"})`, get the parent
   target, and evaluate chrome JS (pattern in `rdp_smoke.py`
   `parent_evaluate`, line 73, which itself never calls `_guard`).
   Scope is a convention for callers who use the wrapper methods.
4. **Lazy tabs evade the denylist.** On the real profile most owner
   tabs are lazy; RDP reports `url=''` (L6 `drive-step3.json`
   tabs_before: Gmail, Calendar, Todoist, Reddit, YouTube all
   `url: ""`). `_url_matches` returns False for empty URL (line 74),
   so no denylist pattern can hit, and URL scope can never match.
   A tab-id-scoped attach to a lazy Gmail tab passes `_guard` with
   an empty URL. The credential check is void exactly where the
   owner credentials live (pinned lazy tabs). PROVEN by evidence
   file.
5. **Guard reads a stale snapshot (TOCTOU).** `_guard_current`
   (line 281) checks `self._current_tab` URL, refreshed only by
   `list_tabs`/`get_target`. `evaluate` does not refresh before
   guarding. If the owner clicks a link in the tasked tab, or the
   page self-navigates (history API, redirect), evaluates keep
   passing against the old URL until the next list. L3 Known
   limits admits the history-API case; owner-click navigation is
   the same bug with a human trigger. PLAUSIBLE trigger, PROVEN
   mechanism.
6. **URL scope is not a destination allowlist.** `navigate` guards
   the current tab and denylist-checks the destination, but never
   checks the destination against URL scope patterns. A tab scoped
   to `*page-a*` can be navigated anywhere non-denylisted; the
   post-navigate `get_target` refusal is swallowed (`navigate`
   tail try/except). Scope answers "which tab may I start on",
   not "where may I take it". Acceptable if understood; dangerous
   if operators believe URL scope confines browsing.
7. **Substring matching over-matches.** `_url_matches` without
   wildcards is case-insensitive substring. Scope pattern
   `example.com` matches `example.com.attacker.example` and
   `evil-example.com`. Denylist `auth` matches `author` pages
   (false positive, safe direction). Scope false positives are
   the unsafe direction. PLAUSIBLE; no exploitation observed.
8. **`list_tabs` disclosure is unscoped by design.** Any session,
   however narrowly scoped, enumerates every tab URL/title in the
   window (needed for diff). Drive reports persist the full list.
   A scoped agent still learns the owner tab inventory (titles
   include mail counts, document names). Minor privacy leak,
   PROVEN by design.
9. **`bench` is destructive unscoped.** `bench` (line 686)
   attaches to the selected tab and navigates it to `about:blank`
   / local / real URLs repeatedly. On the owner session unscoped,
   `bench` destroys the active tab content. Only an operator-
   supplied scope prevents it, and URL-pattern scope breaks bench
   legs by design (L3 limit), pushing operators toward tab-id or
   unscoped bench. PROVEN by code.
10. **`tabs` + `report` probe side effect.** `drive_report`
    (line 622) calls `get_target()` + `probe_webdriver()`
    (evaluates) as a side effect of reporting. `tabs --drive-report`
    therefore evaluates in the selected tab even though the
    subcommand presents as read-only inventory. Guarded, but
    surprising; on an out-of-scope selected tab the refusal is
    recorded as probe error rather than failing the command.

None of this makes scoping useless: L3 live 21/21 and L5 scoped
refusal prove the cooperative path works, and the drive report is
genuine audit value. But "tool-enforced" overclaims. As landed,
RT-20 is a seatbelt that must be buckled per invocation, with the
buckle optional. For a same-session lane whose entire risk is
credential tabs, the operating configuration must make scope +
denylist mandatory (wrapper refuses unscoped on the owner port,
machine-layer scope-config always passed, denylist on). Until
that wrapper exists and is the only supported entry, landing
relies on every future agent remembering flags. Block in default
form.

## Attack 4: Positional tab ids let an agent act on the wrong owner tab

- Severity: High (wrong-tab action on live owner session)
- Evidence class: PROVEN (observed live in L6).
- Verdict: **blocks landing** for tab-id scope across connections;
  **condition**: URL-only scope (no tab ids) enforced for owner
  drives, plus URL verification in re-attach.

Evidence. L6 failure chains, attempt 2: "canonical-id diff assumed
stable descriptor ids; ids are POSITIONAL (insertion shifts later
ids), so the harness attached to the wdprobe tab (read-only probe
only, no writes)". Attempt 1 similarly picked an owner tab via
full-actor comparison; the scoped client refused (good) but the
harness intent was wrong. L3 Known limits assumed "numbering
follows tab creation order" and "observed stable"; L6 disproves
stability across tab-set changes. Landed code: `_canon_tab_id`
(line 84) strips the connection prefix leaving `tabDescriptorN`;
`Scope.matches` (line 115) accepts on id match OR URL match.

Why it bites in real drives:

- CLI usage is one process per command (fresh connection each
  time). An agent records `tabDescriptor11` from `tabs`, the owner
  opens or closes any earlier tab, the next CLI call's
  `tabDescriptor11` is a different page. Tab-id-only scope (the
  form L6 step3 itself used, `drive-step3.json` scope tab_ids)
  then authorizes evaluate/navigate on the wrong tab, and the
  guard passes because the positional id matches. No URL check
  exists to catch it.
- Adding URL patterns does NOT fix it: `matches` is OR, so an id
  hit short-circuits URL verification. Only URL-only scope (zero
  tab ids) is robust, and nothing in the CLI warns when tab ids
  are used cross-session.
- Credential approvals are keyed by the same positional ids
  (`_approval_note`). An approval recorded for a login tab can
  migrate to whatever tab later occupies that position.
- `_reattach_pinned` (line 431) looks up the pinned tab by
  canonical id FIRST and only falls back to exact URL if the id
  is absent. After an insertion shift, the id is present but
  wrong; re-attach lands on the wrong tab and never consults the
  URL. Worse, `list_tabs` refreshes `_pinned_url` by id lookup,
  so the pin URL itself follows the shifted id. The RT-06 retry
  (Attack 6) inherits this wrong-tab hazard.
- `_tab_diff` (line 200) keys before/after by positional id.
  Owner tab churn mid-session produces phantom added/removed/
  navigated entries, undermining the drive report as proof that
  "zero owner tabs" were touched. L6 step3 diff is valid only
  because no churn occurred during that held session.

Within a single held connection with no tab churn, ids are exact
(L3/L5/L6 held sessions worked). The hazard is cross-connection
and churn cases, which are the normal CLI pattern and the normal
owner behavior (owner opens tabs while agent works; that is the
seamless premise). Fix direction (not implemented): require URL
patterns for owner drives, make scope AND (id must match AND URL
must match when both given), verify pinned URL on re-attach
before accepting id hit, and key diffs by URL+title where ids
shift. Until then, tab-id scope on the owner session is unsafe.

## Attack 5: Parent-process target is completely unscoped, and internals control is not in the landed client

- Severity: High
- Evidence class: PROVEN.
- Verdict: **blocks landing** of any internals claim; tab-lane
  landing **condition**ed on parent access being removed from
  agent reach or brought under scope + audit.

Evidence. Landed `rdp_client.py` contains no parent-target API at
all (grep: no `listProcesses`, no parent evaluate). Internals
control was proven by throwaway harness code: L1 `l1_parent.py`
(listProcesses -> getTarget -> evaluate, with longString fetching)
and L6 phase harness. The only parent code in the landed set is
`rdp_smoke.py` `parent_evaluate` (line 73): general-purpose chrome
evaluate with no `_guard`, no scope, no drive-report entry. Smoke
itself attaches unscoped (`run_smoke`, line 107: `RDPClient(port,
host, timeout)` with no scope) and evaluates in the selected
(owner active) tab for checks (b)-(d) before probing.

Consequences:

- Tab scope gives zero protection against parent evaluate. Chrome
  JS can enumerate and manipulate every tab via `gBrowser`,
  switch workspaces, pin/unpin, read sessionstore. An agent (or
  any local process, Attack 2) with parent reach bypasses RT-20
  entirely. The decision doc positions parent target as "first
  choice" for internals; the landed toolset neither provides it
  safely nor prevents it.
- Acceptance step 5 (internals leg) is therefore satisfied only
  at harness level. Agents landing on the toolset cannot do
  internals work through a supported, scoped API; they must copy
  harness patterns (unscoped `request()` calls, Attack 3.3) or
  use the flagged escape hatch. The seamless claim for internals
  asks is unlanded.
- Smoke parent check (e) verifies only `typeof` for three
  globals. It proves reach, not control, and exercises the
  unscoped path on the owner session at every update check
  (read-only typeof today; the function accepts arbitrary expr).

Either parent access is in scope for the lane (then it needs
scoping, approval, and audit at least as strict as credential
tabs, since it is strictly more powerful) or it is out of scope
(then the lane must not claim internals, and smoke should not
normalize unscoped chrome evaluate). Current state is neither:
powerful, unscoped, and absent from the client API. Block for
internals; condition for tab lane.

## Attack 6: DevTools-close noSuchActor retry is unit-proven, live-unfired

- Severity: Medium
- Evidence class: PROVEN that live firing is unobserved in landed
  code; PLAUSIBLE mid-task disruption.
- Verdict: **acceptable risk** with monitoring condition.

Evidence. L2 observed exactly one `noSuchActor` in 322 evaluates
(`eval-loop-run2.jsonl` seq 34: `{'error': 'noSuchActor',
'message': 'No such actor for ID: ...consoleActor3'}`), on a
DevTools-close + tab-switch transition (Ctrl+Shift+K), not on
plain F12 close. L2 run4 clean F12 cycle: 93/93 OK. L5 landed-code
live cycle: 60 evaluates, 0 errors, retries 0; retry path proven
only by 4 unit tests against `FakeRDPTransport`
(`test_scope_unittest.TestNoSuchActorRetry`, re-run PASS by this
reviewer). L6 step6: 31/31 OK, no firing. Landed retry:
`evaluate` (line 475) and `navigate` (line 518) catch
`_is_no_such_actor` (line 152, substring match), `_reattach_pinned`,
retry once; second failure raises (unit-proven).

What breaks if it fires mid-task on the real profile:

- Single evaluate: retry re-executes once. If the dead-actor
  request never executed (expected semantics), retry is safe. The
  packet contains no evidence of double execution. Idempotence
  risk is low for reads; for JS writes (DOM set, JS click) a
  double-fire would be visible but not catastrophic. SPECULATION
  either way; fake transport assumes non-execution.
- Navigate: `_navigate_send` (line 504) tries target actor then
  descriptor actor. L5 unit test had to fail BOTH actors to reach
  retry, meaning real single-actor death may be absorbed by the
  fallback without retry. Double-navigate to same URL is harmless.
- Multi-step task: one retry covers one swap. Owner toggling
  DevTools repeatedly, or swap + immediate second swap, raises
  and aborts the task mid-flow (e.g., after OS click, before
  readback). `wait_load` (line 564) is resilient (swallows,
  re-attaches periodically); bare evaluate sequences are not.
- Wrong-tab migration via positional pin (Attack 4) is the sharp
  edge: retry after owner tab churn can land on the wrong tab
  silently. That composition (swap + churn) is PLAUSIBLE, not yet
  observed.
- Fake-vs-real mismatch: unit fake returns `{"error":
  "noSuchActor"}`; real packet nests error + message (L2 log).
  `_is_no_such_actor` substring-matches `str(e)`, and
  `_evaluate_once` wraps as `evaluate error: {...}`, so real text
  matches. This reviewer confirms the real L2 error string
  contains `noSuchActor`. Matching logic is sound; unproven part
  is only the live re-attach sequence (listTabs + getTarget
  against a real swapped target), which L2 harness did manually
  (recovered, but landed on background tab via selected-pick;
  landed code fixes pick to pinned, untested live).

Frequency is low (~1 per DevTools close+switch, 0 per plain F12
close in samples). Owner DevTools use during agent drives will
eventually fire it. Condition: first live firing on owner session
must be captured in drive report (`retries` field exists) and
reviewed; tasks should prefer `wait_load`-style resilient reads
around owner-active periods. Not a landing block.

## Attack 7: Update fragility: smoke misses plausible breakage, registry fail-closed is procedural, watch not applied

- Severity: High (kill criteria 1, 2, 4 depend on this)
- Evidence class: PROVEN gaps (code + report inspection).
- Verdict: **blocks landing** of the operating switch until the
  per-update gate is mechanized; toolset code itself may land
  unselected.

RDP actors are internal Firefox APIs; Zen updates can rename
actors, reshape packets, rename prefs, or change Zen internals.
Smoke checks (`rdp_smoke.py` `run_smoke`, line 107): (a) port
owner, (b) attach + 1+1, (c) webdriver probe, (d) evaluate + DOM
count, (e) parent typeof x3, (f) loopback bind, (g) latency info.
Blind spots against plausible breakage:

1. **Navigate never smoked.** No `navigateTo`/`wait_load` check.
   An update breaking navigation passes smoke; agents fail
   mid-task on owner session. Fail-open for a core lane verb.
2. **Internals depth never smoked.** (e) checks `typeof` only.
   L1 control depends on method names/signatures
   (`createAndSaveWorkspace`, `changeWorkspaceWithID`,
   `folder.delete`, etc.). Renames keep typeof `object` and pass
   smoke while writes break.
3. **Attach-to-wrong-tab passes.** (b) attaches to selected tab
   and checks 1+1. A change in `listTabs` selected semantics or
   ordering still passes; agents then act on wrong tabs (compounds
   Attack 4).
4. **Scope/denylist/retry/report never smoked.** Update cannot
   break client-side guards directly, but actor shape changes
   (descriptor format) can silently break `_canon_tab_id` matching
   (regex `^[^.]+\.conn\d+\.(tabDescriptor\d+)$`, line 84). Smoke
   would pass while scoped drives refuse everything (fail-closed,
   safe) or, worse, approvals mis-match. Untested either way.
5. **Detectability beyond probe.** Probe checks webdriver value/
   type/getter prefix + doc attr + 4 globals (`probe_webdriver`,
   line 591). A new pref side effect or automation global visible
   to Cloudflare/Google passes probe and smoke. Kill criterion 1
   includes "human-path block on acceptance panel"; acceptance
   step 8 requires "probe + Google spot check". Smoke has no
   Google/panel check. Step 8 as built is incomplete.
6. **Probe false-fail risk (safe direction).** Getter check
   requires prefix `function webdriver()`. A Firefox formatting
   change false-fails smoke and downs the lane until client fix.
   Fail-closed, acceptable, but counts toward "7 days broken"
   kill criterion if maintenance lags.

Registry + fail-closed design. Registry JSON (L4) states the
right rule ("No channel selected = no drive... refuse"), owner
named (Muse parent). But: the client never reads the registry
(`--port` is a bare CLI arg); `zen-rdp-owner.profile_marker` is
still null ("Set at landing"); smoke script path is "recorded at
landing"; L4 section 5 watch integration is explicitly "propose
only; coordinator applies" via cron update + verify. None of the
mechanism exists yet. Kill criterion 4 (no named maintenance
owner staffed -> build does not start) is half-met: owner named
on paper, automation not applied, per-update smoke not wired to
version-change detection in any landed artifact this reviewer can
inspect.

Launch integration also unbuilt: permanent switch requires owner
launch to always pass `--start-debugger-server` + applied
`user.js` prefs (machine layer). L6 proved the temporary form and
restore; the permanent wrapper, registry selection flip, and
marker setting are all future coordinator acts. Until they exist
and are verified (cron.view after update, smoke on owner channel
post-flip), "fail-closed" is a document, not a control. The
toolset can land in repo unselected (as L5 left it); the
operating-configuration switch cannot.

## Attack 8: Restore integrity: prefs proven, history/sessionstore residue unexamined

- Severity: Low-Medium (acceptance-run hygiene; not a landing
  safety block)
- Evidence class: PROVEN for prefs/tab-list; PLAUSIBLE for
  history/cookie residue (mechanism certain, impact minor).
- Verdict: **acceptable risk** for the acceptance run; reporting
  condition for any "untouched" claim.

Evidence. L6 `restore.json`: `user.js` + `prefs.js` sha256_ok
true, tabs 57 unique (url,title) pairs before/after with 0
missing/extra (65 total incl. duplicates), ports down, new pid
flag-free, probe CLEAN. Step3 diff: zero owner tabs closed/
navigated in active window (12 -> 12).

Residue the verification does not cover:

- **Places history.** Tasked tabs visited google.com,
  timeanddate, coolors, codeforces, example.com, accuweather in
  the owner profile. Closing tabs does not delete history.
  Owner history now contains acceptance visits. Harmless, but
  "tabs match record" must not be read as "profile untouched".
- **Step4 lazy-tab load.** Owner YouTube tab was loaded via
  `gBrowser.selectedTab` selection (L6 step4 method). That is a
  real touch: network fetch, cookie updates, selected-tab change,
  sessionstore loaded-state change. Report discloses it honestly
  ("URL unchanged, no reload, no writes"); "no writes" means no
  JS writes, not no browser state change. Selected index after
  restore is unverified (comparison is (url,title) sets only).
- **Sessionstore internals.** Verification compares tab counts
  and (url,title) pairs, not per-tab history stacks, scroll,
  form data, workspace selection, or pinned state beyond count.
  Step5 pin/unpin of tasked tab was reverted with read-back;
  workspace switch was not performed on real profile (good).
- **Window scope.** RDP sees active-window tabs (11-12); record
  has 65 across 3 workspaces. "Zero owner tabs" is proven for the
  active window only. Parent counts (3 workspaces) corroborate
  structure, not per-tab state in other workspaces.
- **wdprobe touch.** Attempt-2 harness attached read-only to the
  wdprobe owner tab. Probe evaluates are reads; no residue
  expected. Disclosed in report. Fine.

For landing (permanent config), history sharing is inherent to
same-session control and presumably accepted. For the acceptance
run specifically, restore claims should be quoted precisely:
prefs identical, tab list identical, history polluted with test
visits, one lazy tab loaded. No block.

## Attack 9: Multi-agent drives of one live session are uncoordinated (RT-23)

- Severity: High if multi-agent seamless is claimed; Medium if
  landing is explicitly single-agent.
- Evidence class: PROVEN absence of locking; PLAUSIBLE
  interference (focus contention already observed on OS lane).
- Verdict: **blocks landing** for multi-agent use; **condition**:
  single-agent lock (procedural or file lock) until RT-23 designed.

Evidence. Decision doc lists RT-23 (session locking, undesigned)
under "What remains before landing". L3 Known limits: "two scoped
clients can still attach concurrently". Landed client has no lock
file, no registry lock, no connection exclusivity (RDP server
accepts multiple connections; L6 smoke desc_actor `conn79` shows
connection churn is normal). Parallel-worker evidence shows the
OS-lane version of contention: L2 Test2 run1 typing refused due
to L3 window focus; L5 focus miss to another worker pid. RDP
removes the focus signal that made contention visible: two agents
can evaluate/navigate the same tab silently, interleaving DOM
writes, racing navigations, and corrupting each other's drive
reports (each `tabs_before` snapshot attributes the other agent
navigations to itself or to "owner churn"). Parent-target
workspace switch by one agent disrupts the other agent tab
context entirely. No error need occur; wrong data is the failure
mode (agent A reads page B after agent B navigated).

The fleet operating model is multi-agent by default (coordinator
+ workers + clones). A seamless lane without locking invites the
exact silent interference the split profile prevented by
isolation. Minimum landing condition: exactly one RDP drive at a
time on the owner session, enforced by a lock the wrapper checks
(not by brief discipline), with drive reports naming the holder.
RT-23 design remains owed.

## Attack 10: Speed claims hold for DOM verbs, not for real user-path tasks

- Severity: Low (expectation-setting, not safety)
- Evidence class: PROVEN numbers; generalization PLAUSIBLE at best.
- Verdict: **acceptable risk**; headline must be narrowed.

Evidence. L6 `speed.json` / step9, n=1 each, same day back-to-back:
(a) example.com+title RDP 0.162s vs split BiDi 1.3s; (c) DOM
write+readback 0.083s vs 1.106s; (b) Google "weather hanoi" +
click + title RDP 39.3s completed (AccuWeather) vs baseline 6.3s
BLOCKED at google.com/sorry (incomplete). L6 honestly attributes
(b) to OS-input batches (~4-5s each: observe+focus+act). Decision
doc RT-07 note (adopted): micro-benchmarks never scored alone;
acceptance measures end-to-end.

Analysis. (a)/(c) prove the RDP DOM lane is ~8-13x faster than
per-call BiDi for navigate/read/write verbs. That is real and
matches W4/L3/L5 latency class (evaluate ~0.5ms). (b) proves the
opposite for trusted-input user-path tasks: total time is
dominated by computer-use batches, which RDP does not accelerate.
The baseline (b) number is time-to-failure, not time-to-task, so
no speed ratio exists for (b); the honest statement is "RDP lane
completes a task the flagged lane cannot complete at all, in
39s". Real agent tasks mix both: speedup depends on verb mix.
Tasks needing screenshots, trusted clicks, typing, upload
pickers (RT-02 suite untested: upload/clipboard/drag/Turnstile)
pay OS-lane cost regardless. Single-run n=1 timings with no
repeats, no variance, and unclear attach inclusion in (a) cannot
support a general "seamless is faster" headline. Narrow claim
that evidence supports: "DOM read/write/navigate verbs are
sub-millisecond to ~150ms via RDP vs ~1s via split BiDi; end-to-
end user-path tasks remain OS-lane-bound." No block; do not sell
the switch on speed for click-heavy work.

## Attack 11: Large evaluates return grip objects, not content (longString)

- Severity: Medium (silent data loss in real tasks)
- Evidence class: PROVEN by code inspection + L1 live encounter.
- Verdict: **condition**: fix or document before agents rely on
  page-text reads.

Evidence. L1 discovery: `gBrowser` key dump (12,472 chars)
returned as RDP longString grip, not plain string; L1 harness
fixed by substring fetching (`l1_parent.py` lines 70-108). Landed
client `_unwrap` (line ~464) returns grip dict unchanged for any
type other than boolean/number/string/null/undefined. No
longString handling exists in landed `rdp_client.py` (grep:
no `longString`, no `substring` request). Smoke DOM check reads a
count (number), so smoke passes while real reads of
`document.body.innerText` / `outerHTML` on large pages return
`{"type":"longString",...}` without text. Agent receives a dict
where it expects a string; downstream code may stringify the grip
and proceed on garbage, or fail confusingly. L3/L5/L6 tasks used
short evaluates (titles, counts, markers) and never hit it.
Fix is known (port L1 substring logic); absence is a landing
completeness gap, not a safety block. Condition: land the fix or
explicitly limit supported evaluate sizes in README + briefs.

## Attack 12: Operational footguns: weak port-owner auth, smoke on owner tab, escape-hatch normalization

- Severity: Medium-Low individually; collectively they erode the
  fail-closed story.
- Evidence class: PROVEN mechanisms; exploitation PLAUSIBLE.
- Verdict: **condition** (harden before switch; none alone blocks
  toolset landing unselected).

1. **Port-owner marker is substring auth.** `check_port_owner`
   (line 157) passes if marker string appears anywhere in the
   listener cmdline. Owner marker at landing will be a profile-dir
   substring (L6 smoke used `ae59l0ak`). Any local process can
   include that string in argv and bind the port first; client
   then attaches to the impostor. Realistically the browser binds
   first at launch, so risk is low; but the guard proves "some
   process mentioning the profile", not "the owner Zen". Check-
   then-connect is also TOCTOU (ss snapshot, then socket connect).
2. **Smoke evaluates in owner active tab before probe.** Order
   (b) evaluate -> (c) probe means a post-update session that
   turned detectable still receives evaluates during smoke.
   Harmless payloads (1+1, counts), but the pattern (drive first,
   verify after) is backwards for a gate. Minor.
3. **Test escape hatch in production CLI.**
   `--allow-unmarked-test-attach` (line 776) skips the only
   fail-closed check with a warning. Necessary for unit/throwaway
   work; on the owner machine it is one flag away from unguarded
   attach. Acceptable if wrapper never passes it; flag it in
   briefs as banned for owner drives.
4. **Escape hatch (flagged relaunch) remains the internals
   fallback.** Decision doc keeps Route 2 mechanics as logged
   escape hatch. L1/L6 reduce need, but RT-02 gaps (upload,
   clipboard, drag, Turnstile) and any parent-write beyond
   pin/unpin on real profile (workspace switch throwaway-only)
   may still force flagged relaunch with W3 costs (46.5s BiDi,
   heap loss). Seamless claim must keep the asterisk until RT-02
   suite passes via OS lane.
5. **Screenshot lane unchanged.** RDP has no screenshot actor
   (W4: 4 methods refused). OS grim full-output captured wrong
   windows in L1 multi-window ws2; window-scoped observe is
   required. Landing does not improve screenshots; briefs must
   not assume RDP screenshots exist.

---

## Bottom-line recommendation

**Do not switch the operating configuration to the RDP lane yet.
Land the toolset unselected (as L5 left it); keep the interim
split as operating configuration.**

The RDP lane works: Google passes, probe is clean, DOM verbs are
fast, internals are reachable, concurrency holds in tested
shapes, restore is clean. What blocks the switch is the safety
envelope the decision doc itself requires before landing:

Must close before switch (blocks):

1. RT-04 written owner acceptance of silent attach on file
   (Attack 2). L6 14:00 assertion without a record does not meet
   the decision doc "in writing" bar.
2. Mandatory scoping on owner drives: wrapper/registry entry that
   refuses unscoped sessions and denylist-off sessions on the
   owner port; URL-only scope (tab-id scope banned cross-
   connection) or AND semantics with URL verification; lazy-tab
   (`url=''`) credential handling defined (Attack 3, 4).
3. Parent-target disposition: scoped + audited API or explicit
   exclusion with internals claim withdrawn; smoke unscoped
   chrome evaluate justified or removed (Attack 5).
4. Mechanized update gate: cron watch applied + verified
   (cron.view), registry marker set, smoke extended (navigate +
   Google spot check) or step 8 honestly narrowed, launch wrapper
   always starting the server (Attack 7).
5. Single-drive lock for the owner session until RT-23 designed
   (Attack 9).

Conditions / fixes that should land with or before switch:

- longString handling ported from L1 (Attack 11).
- Drive-report diff robust to id shift; bench banned or scoped
  on owner session (Attacks 3, 4).
- Cold-repeat panel across hours before quoting pass rates;
  P2 challenge disclosed in landing note (Attack 1).
- First live noSuchActor firing captured and reviewed (Attack 6).
- Speed headline narrowed to DOM verbs (Attack 10).
- RT-02 isTrusted suite (upload, clipboard, drag, Turnstile)
  run via OS lane, or seamless claim narrowed in writing.

Acceptable risks once the above close: probabilistic Cloudflare
challenges (Google path proven), low-rate actor-swap retries,
acceptance-run history residue, OS-lane-bound end-to-end speed.

If the owner explicitly waives items 1-5 in writing with the
risks above understood, the switch becomes an informed risk
acceptance rather than an engineering claim. On current evidence,
presenting the switch as "acceptance passed, safe to flip" would
overclaim: L6 itself reports PARTIAL PASS (step 2 partial, step 8
procedure-ready), registry ALL UNSELECTED, and the decision doc
remaining list (RT-04 record, RT-20 enforcement depth, RT-23,
RT-02 depth, watch application) is still open. The builders
recorded these honestly. The redteam verdict is to believe them.

Redteam reviewer, 27/11/2026. English only. No GitHub commits.
No laptop access. No owner contact.
