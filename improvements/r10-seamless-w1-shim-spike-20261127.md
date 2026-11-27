# R10 seamless W1 spike report (2026-11-27)

Spike for the coordinator decision: seamless same-session agent control of
Zen without Cloudflare blocks. Starting point: pinned Proxy shim (sha256
bb49ff3f...630b8) passes the Cloudflare panel but has a toString tell, and
Google search entry still challenges.

Worker: r10-seamless-w1. All tests in headed throwaway profiles on ws2,
same machine, same IP, same day (12:14-12:51 +07). Ports: BiDi 9444,
Marionette 2848 (9333/2838 were held by a parallel W3 lane, pid 459519,
never touched). Owner live Zen PID 439493 never signalled, navigated, or
closed; verified alive after every run. Test instances killed only by
recorded pid after cmdline profile check. No compositor window-close.
ydotool banned throughout. Real-keyboard steps used computer-use act-now
with --label "Computer use active" (pill visible), with a focus-pid
assertion before every batch.

## Headline results

1. **Best shim: v3-proxy-patch-exact** (Proxy getter + Proxy-patched
   Function.prototype.toString returning byte-exact native strings).
   Probe verdict CLEAN, page-realm String(getter) byte-identical to
   native, pristine-realm attack leaks only the anonymous form (no
   source). It strictly dominates the pinned v1 shim.
2. **Google entry isolation resolved: input method is NOT the cause,
   active BiDi session is NOT the cause.** Flagged browsers block on
   Google with BiDi input (3/3), with real keyboard + session (3/3),
   and with real keyboard + no session (2/2). Flag-free + real keyboard
   + no session passes (2/2). The block tracks the launcher flags (or
   flag-correlated signals beyond page-visible navigator.webdriver).
   No JS shim variant fixes Google entry, including CLEAN-grade v2/v3.
3. **Pre-existing tabs:** shim does not reach already-loaded documents.
   script.evaluate install fixes the live value but cannot unsee what
   early page scripts already read (early=true recorded). Preload +
   reload gives early=false.
4. **Panel:** fresh-profile raw challenges P1+P2 (void rule satisfied);
   fresh v3 passes P1, challenges P2 (n=1 per cell, Cloudflare scoring
   is probabilistic). Warmed-profile v2 passed P1/P2/P5/C1 with raw P1
   also passing that hour (warmth anomaly, stated plainly below).

## Test 1: shim variants vs probe + detection checks

Driver: `w1-driver.mjs --mode variants` (BiDi, flagged throwaway).
Probe expression and verdict vocabulary reused from
`r10-webdriver-probe.mjs`. Extra checks per variant: getter name,
String(getter), Function.prototype.toString.call(getter),
String(Function.prototype.toString), pristine iframe attack (fresh
about:blank iframe realm: its own navigator.webdriver, its getter
toString, pristine toString applied to parent getter and to parent
Function.prototype.toString), Worker realm read, race page (earliest
inline script + dynamic iframe).

Native reference (control, no shim): webdriver=true (DIRTY), getter
name "get webdriver", String(getter) is the multi-line native form
`function webdriver() {\n    [native code]\n}`.

| Variant | Probe | String(getter), page realm | Pristine toString on getter | Pristine toString on toString fn | Iframe wd | Race early | Worker wd |
|---|---|---|---|---|---|---|---|
| control-noshim | DIRTY | native multi-line | native multi-line | native | true | true | no property |
| v1-proxy (pinned) | SHIMMED | anonymous `function () {...}` | anonymous | native | false | false | no property |
| v2-named-nopatch | SHIMMED | SOURCE `get webdriver() { return false; }` | SOURCE | native | false | false | no property |
| v2-named-patch | CLEAN* | single-line native form | SOURCE LEAK | PATCH SOURCE LEAK | false | false | no property |
| v2-proxy-patch | CLEAN* | single-line native form | anonymous | PATCH SOURCE LEAK | false | false | no property |
| v3-proxy-patch-exact | CLEAN | EXACT native multi-line | anonymous | anonymous | false | false | no property |

\* CLEAN by the probe regex (`^function webdriver\(\)`), but the returned
string is single-line while true native is multi-line, so an
exact-compare checker in the page realm still catches v2. v3 returns
byte-exact strings for both the getter and Function.prototype.toString
itself, closing the page-realm exact-compare check.

Findings, stated plainly:

- **Preload covers iframes and wins the race.** Every shim variant:
  iframe navigator.webdriver=false, earliest inline script reads false,
  dynamic iframe reads false. Worker realm has no webdriver property at
  all in this build (undefined), shim or not.
- **Pristine-realm limit (honest):** a JS-level shim cannot be perfect
  against a pristine realm's genuine Function.prototype.toString. Best
  achievable (v3): pristine reads show the anonymous native form
  `function () {\n    [native code]\n}` for both getter and patched
  toString. That leaks "name missing" but no source code. Named-getter
  variants leak full source under the same attack and are strictly
  worse. Plain-function toString patches leak their own source; the
  Proxy-wrapped patch (v3) does not.
- Shim hashes: v1 bb49ff3f...630b8 (316 B, pinned, verified),
  v2-named-nopatch 85172a8d... (386 B), v2-named-patch 455206c6...
  (673 B), v2-proxy-patch 66e89d09... (603 B), v3 cf22533a... (682 B).
  Full hashes in `results-variants.jsonl` / `results-variants2.jsonl`.

## Test 2: Google entry isolation (the A5 caveat)

Entry path (normal user): real keyboard Ctrl+L, type google.com, Enter,
type query into the homepage search box, Enter; or BiDi equivalent
(google.com homepage, BiDi key actions). No deep links to
google.com/search?q=... as entry proof. Queries: "weather hanoi",
"timeanddate weekday calculator", "codeforces" (session arms);
"weather hanoi", "codeforces" (no-session arms).

| Arm | Input | Session | Shim | Result |
|---|---|---|---|---|
| flagged | BiDi input.performActions | yes | v2-proxy-patch | 3/3 ENTRY-CHALLENGE (google.com/sorry) |
| flagged | real keyboard (act-now) | yes | v2-proxy-patch | 3/3 ENTRY-CHALLENGE |
| flagged | real keyboard | NO session | none possible | 2/2 BLOCKED (unusual-traffic wall, screenshot) |
| flag-free | real keyboard | NO session | n/a (native false) | 2/2 PASS (SERP loads, screenshot) |

Isolation conclusion: A5's caveat is resolved. Input method does not
matter (BiDi 3/3 blocked, real keyboard 3/3 blocked, same browser,
same shim). Active session does not matter (flagged no-session still
blocked). What remains is the flagged launch itself: with no session
there is no shim, so navigator.webdriver is natively true there; with
a session the shim makes it false with a CLEAN probe, and Google still
blocks. So Google's block is driven by flag-correlated signals beyond
the page-visible webdriver value that any JS shim can rewrite. A
seamless same-session design that keeps flags on the human's browser
should expect Google search entry to keep challenging; DDG entry (as
in A5 Entry B and Test 4 here) is the working search path under flags.

Note: raw evidence screenshots of the Google wall contain the IP line
Google prints; it is not reproduced in this report text.

## Test 3: pre-existing tab coverage

Browser launched with `file:///tmp/r10w1/prepage.html` loaded BEFORE
session.new (page records `window.__early = navigator.webdriver` in
its earliest inline script). Then holder attach (session.new +
addPreloadScript with v2-proxy-patch).

| Stage | Probe | __early (already-run script) | Now |
|---|---|---|---|
| (i) as-is, before shim | DIRTY | true | true |
| (ii) after script.evaluate shim install | CLEAN | true (unchanged) | false |
| (iii) after preload + reload | CLEAN | false | false |

Limit stated plainly: evaluate-install fixes the live value in an
already-loaded document, but any page script that already ran may have
read true and acted on it; that cannot be undone. Only reload (or a
fresh navigation) under an installed preload gives early=false.
Seamless same-session control therefore needs either evaluate-install
on attach (accepting the early-read limit) or a reload of open tabs.

## Test 4: panel re-run with best shim

Entry: DuckDuckGo homepage, type query, Enter, click first result for
the target domain, wait, read (15s + re-read on challenge). Sites:
P1 timeanddate, P2 coolors, P5 codeforces, C1 example.com.

Warmed profile (profile-w1, after Test 1-3 activity), v2-proxy-patch:

| Site | v2-proxy-patch | Raw control |
|---|---|---|
| P1 | PASS | PASS (anomaly, see below) |
| P2 | PASS | not run warmed |
| P5 | PASS | - |
| C1 | PASS | - |

Fresh profiles per arm (run4, after the welcome-screen pref fix):

| Site | Raw (fresh) | v3 (fresh) |
|---|---|---|
| P1 | CHALLENGE-CF "Just a moment..." | PASS |
| P2 | CHALLENGE-CF "Just a moment..." | CHALLENGE-CF "Just a moment..." |

Reading, honestly: the fresh raw control challenges on both sites, so
the fresh test is not void, and it replicates A5's morning result. The
shim clearly shifts the outcome (fresh v3 passes P1 where raw
challenges; warmed v2 passed all four sites), but fresh v3 still
challenged on P2 once. With n=1 per cell and probabilistic Cloudflare
scoring, the correct claim is "shim removes the webdriver trigger for
this challenge class and passes most of the time", not a guarantee.
The warmed raw P1 PASS (vs A5 raw CHALLENGE twice that morning, and
fresh raw CHALLENGE at midday) is most plausibly cookie/IP warmth in
the reused profile; it weakens the warmed run as standalone causal
evidence, which is why the fresh run was done.

## Failure chains (recorded, not skipped)

- **Port collision:** first launch used BiDi 9333, already held by a
  parallel W3 lane (profile /tmp/r10-w3-profile, pid 459519). Symptom:
  NS_ERROR_SOCKET_ADDRESS_IN_USE, session.new "session not created".
  Decision: W1 moved to 9444/2848; W3 instance never touched.
- **setsid pid race:** `$!` after `setsid nohup ... &` sometimes names
  a dead parent, so stop-by-pid missed the real browser. Fix: resolve
  the real main pid by cmdline profile match (excluding contentproc)
  at launch; stop still verifies cmdline before kill.
- **Fresh-profile entry failures (run2, run3):** BiDi typing into DDG
  homepage never submitted, screenshots failed ("unable to capture
  screen"), browsingContext.create timed out, and real-keyboard Google
  attempts sat on Zen's first-run welcome page. Root cause: Zen
  welcome screen (`zen.welcome-screen.seen` unset in fresh profiles;
  Firefox's browser.aboutwelcome.enabled does not gate it). Fix:
  `user_pref("zen.welcome-screen.seen", true)` in throwaway prefs.
  Run4 with the fix produced valid fresh panel + no-session results.
  Both arms failed identically pre-fix, so no shim signal was lost or
  fabricated; failed JSONL kept as `results-panel-run2-failed.jsonl`
  and `results-panel-fresh.jsonl`.

## Recommendation for the coordinator decision

- Adopt **v3-proxy-patch-exact** as the shim if a JS-level shim is
  used: byte-exact page realm, minimal pristine leak (anonymous form
  only), covers iframes and wins the parse-time race, worker realm
  clean by absence.
- Same-session seamless control via holder preload is viable for
  Cloudflare-panel-class sites, with two stated limits: pre-existing
  documents need evaluate-install (early-read limit) or reload; and
  Google search entry stays blocked under flags regardless of shim.
  Plan search entry via DDG under flags, or keep human browsing
  flag-free for Google.
- Do not oversell: a site that runs pristine-realm toString checks can
  still detect that a shim exists (anonymous form). Closing that last
  tell needs a below-JS layer (extension at document_start still runs
  in page realm variants; chrome-privileged or native change), which
  is the Alternative 3 build question from Stage 1, not this spike.

## Evidence

VM `~/workspace/r10-seamless-w1/` (pulled from laptop `/tmp/r10w1/`):

- `results-variants.jsonl`, `results-variants2.jsonl` (Test 1, incl. v3)
- `results-preexisting.jsonl` (Test 3)
- `results-google-bidi.jsonl`, `results-google-real.jsonl` (Test 2 session arms)
- `results-panel.jsonl` (warmed panel), `results-panel-fresh4.jsonl`
  (fresh panel), `results-panel-run2-failed.jsonl`,
  `results-panel-fresh.jsonl` (pre-fix failures, kept)
- `shots/` : google-bidi-q1..3, google-real-q1..3,
  google-nosession4-free-q1..2, google-nosession4-flag-q1..2,
  panel-v2-proxy-patch-P1/P2/P5/C1, panel-raw-control-P1,
  panel-none-P1/P2, panel-v3-proxy-patch-exact-P1/P2 (plus run2/run3
  invalid welcome-page shots google-nosession*, google-nosession3*)
- Driver + scripts: `w1-driver.mjs`, `run-all.sh`, `run2.sh`,
  `run3.sh`, `run4.sh`, `launch-w1.sh`, `stop-w1.sh`, `act-w1.sh`,
  `prepage.html`
- Event log: master event log entries tagged `r10-seamless-w1`.

## Cleanup verification

After run4: no W1 processes remain (ps grep clean), BiDi 9444 and
Marionette 2848 closed, owner Zen 439493 alive and untouched, only
zen main process on the box is the owner's. Throwaway profiles remain
under laptop `/tmp/r10w1/profile-*` for evidence; no test windows left
on ws2 by this worker (instances stopped by pid, never by compositor
close).

## Caveats

- One machine, one IP, one day, n=1-3 per cell. Cloudflare and Google
  scoring are probabilistic and time-varying; treat outcomes as
  today's readings.
- Probe CLEAN certifies only the listed signals (webdriver value,
  descriptor, getter toString form, doc attribute, plugins length,
  known globals). It does not certify TLS, IP reputation, or behavior.
- Google no-session flagged arm necessarily has webdriver=true (no
  shim without a session); its block alone would be ambiguous, but
  combined with shimmed+session 6/6 blocked it isolates flags over
  input/session.
