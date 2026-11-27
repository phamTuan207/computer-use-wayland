# R10 seamless W4: RDP-primary first slice + RT-01 blocking test (27/11/2026)

Worker W4. Scope: answer RT-01 (does Google entry and the Cloudflare
panel pass with the RDP debugger server actually running and an agent
attached?) and deliver the first production-shaped RDP slice (attach +
one fast action path, measured). All tests in headed throwaway profiles
on ws2, same machine, same IP, same day (13:03-13:31 +07). Ports: RDP
6021, BiDi control 9445, Marionette control 2859, local HTTP 8941 (all
verified free before binding). Owner live Zen PID 439493 never
signalled, navigated, or closed; verified alive after every phase.
Test instances killed only by recorded pid after cmdline profile check.
No compositor window-close. ydotool banned throughout. Real-keyboard
and OS-click steps used computer-use act-now with --label "Computer
use active" (pill visible), focus-pid asserted before every batch.
Zen build under test: 1.24.3b (same as W1/W2).

## Headline verdict

**Google passes with RDP running: YES, 3/3.** Address-bar search
(Ctrl+L, type query, Enter) loaded Google SERPs for all three W1
queries with the debugger server listening on 6021 and an RDP client
attached for the whole run. No unusual-traffic wall. This is the exact
test flagged launches failed 6/6 in W1. The flag-correlated Google
block does NOT reproduce under flag-free + RDP.

**Cloudflare panel under RDP: mostly pass, not clean.** Valid
landings: P1 timeanddate 1 pass / 1 challenge (two sequential visits,
same profile), P2 coolors PASS, P5 codeforces PASS, C1 example.com
PASS. Same-day flagged-raw control challenged on both P1 and P2, so
the panel test is NOT void. RDP removes the deterministic flagged
failure; Cloudflare scoring stays probabilistic (same band W1 found
for the v3 shim: "passes most of the time", not a guarantee).

**Slice works and is fast.** Attach-to-first-evaluate 3.0 ms median,
evaluate 0.5 ms median (n=12-20). RDP parent-process target reaches
Zen internals (gZenWorkspaces/gBrowser/gZenFolders all typeof object).
RDP screenshot: no actor on this build (honest FAIL; OS grim used).
Bind: 127.0.0.1 only, verified.

## RT-01 method (normal-user path)

(a) User entry point: address-bar search like a normal user (Ctrl+L,
type query, Enter; Zen default engine on this profile is Google,
client=firefox-b-d). Panel entry: google.com homepage, type query,
Enter, OS-click first result (link located by RDP DOM read, clicked
by real OS input). (b) Forbidden shortcuts honored: no
google.com/search?q= deep link as entry, no internal setters as proof.
RDP evaluate was used only to READ results (href/title/classify) and
to locate links for OS clicks. Classification reuses W1 vocabulary
(PASS / ENTRY-CHALLENGE / CHALLENGE-CF). Screenshots: grim full-output
per query/site (test window right side of ws2; owner window also in
frame, untouched).

Launch config (exact W2): flag-free + --start-debugger-server 6021 +
user.js prefs devtools.debugger.remote-enabled=true,
devtools.chrome.enabled=true,
devtools.debugger.prompt-connection=false,
devtools.debugger.remote-host=127.0.0.1,
devtools.debugger.remote-port=6021 (plus W2 base prefs incl.
zen.welcome-screen.seen=true). Fresh profile /tmp/r10w4-rdp. One RDP
connection held attached from probe-start through panel end.

### Google entry (3 queries, address-bar)

| Query | Method | Outcome | Landing |
|---|---|---|---|
| weather hanoi | address-bar | PASS | google.com/search SERP, weather card visible (shot rt01-google-q1.png, visually verified) |
| timeanddate weekday calculator | address-bar | PASS | google.com/search SERP |
| codeforces | address-bar | PASS | google.com/search SERP |

No homepage fallback was needed (default engine is Google). No
connection prompt appeared at attach or during browsing (attach
succeeded silently under prompt-connection=false; screenshots show no
debugger prompt; the only popup in shots is Zen's translate prompt in
q1, unrelated).

Probe reads (RDP evaluate, start + end + panel probes): webdriver
false, type boolean, getter `function webdriver() { [native code] }`
(multi-line native form), doc attribute null, plugins 5, no
automation globals. Verdict CLEAN every time.

### Cloudflare panel (Google search-then-click)

Valid-landing results (landing host verified per site):

| Site | Visit 1 (panel2) | Visit 2 (panel3/retry) | Verdict |
|---|---|---|---|
| P1 timeanddate | CHALLENGE-CF "Just a moment..." (held after 15 s re-read) | PASS (Weekday Calculator loaded, shot verified) | 1/2 split |
| P2 coolors | invalid landing (finder bug, see failure chains) | PASS coolors.co (shot verified) | PASS |
| P5 codeforces | invalid landing (finder bug) | PASS codeforces.com | PASS |
| C1 example.com | invalid landing (finder bug) | PASS example.com | PASS |

Reading honestly: visits were sequential on one profile, so P1 visit 2
may benefit from clearance warmth after visit 1 (W1 flagged the same
confound). n=1-2 per cell, one machine/IP/day. Claim supported:
"RDP config passes Google deterministically today (3/3) and passes
the panel at the same probabilistic rate class as the best shim,
clearly better than same-day raw (0/2)". Claim NOT supported: "no
Cloudflare block ever" - P1 challenged once under RDP.

### Control arm (same day, flagged-raw, BiDi 9445, no shim, DDG entry)

| Site | Outcome | webdriver |
|---|---|---|
| P1 timeanddate | CHALLENGE-CF "Just a moment..." (shot panel-none-P1.png, visually verified) | true |
| P2 coolors | CHALLENGE-CF "Performing security verification" | true |

Void rule: SATISFIED (control challenged on both sites; panel test
valid). Replicates W1 fresh-raw result.

## First slice: production-shaped RDP client

Client: `~/workspace/r10-seamless-w4/rdp_client.py` (stdlib only,
extends W2 w2_rdp*.py pattern). Self-test:
`~/workspace/r10-seamless-w4/test_rdp_client.py` (attach + evaluate +
probe + navigate + DOM read/write assert, exits nonzero on failure;
PASS recorded). Supporting harness in the same directory:
w4_common.py, rt01_driver.py, panel_rerun.py, p2_retry.py,
click_test.py, grid_test.py, tab_probe.py, obs_probe.py, probes.py,
launch-rdp.sh, stop-w4.sh, act-w4.sh, smoke*.sh, rt01.sh, slice.sh,
control.sh, www/slice.html. Evidence: logs/ (JSONL + bench/probes
JSON + run logs), shots/ (downscaled key shots; full-res grim PNGs
remain on laptop /tmp/r10w4/shots/).

Client surface: attach (connect, listTabs, getTarget), evaluate read
(DOM query), evaluate write (set input value; JS click with isTrusted
recorded false), navigate + wait-load polling. Port registry guard:
--port arg plus --profile-marker owner check via ss + /proc cmdline;
refuses (exit 2) if the listening pid is not the expected throwaway
browser. Fail-loud: probe_webdriver raises unless webdriver is native
false; CLI exits nonzero with a clear ERROR line on attach/probe
failure. Two W4-found robustness fixes are in the client: selected-tab
picking (see failure chains) and tabListChanged filtering.

### Latency table (medians, headed throwaway, bench2 run)

| Metric | Median | n | Notes |
|---|---|---|---|
| Attach-to-first-evaluate | 3.0 ms | 12 | Fresh TCP connect + listTabs + getTarget + evaluate 1+1, browser already running. First run of bench1 was 28.3 ms (cold connection); browser launch to port-open measured ~1 s in launch logs. |
| Evaluate trivial (1+1) | 0.5 ms | 20 | Held connection. Matches W2 0.4 ms class. |
| Evaluate DOM read | 0.3 ms | 20 | querySelectorAll count. |
| Navigate-to-load, local slice.html | 53.8 ms | 12 | Includes 50 ms wait-load poll granularity; actual load completes inside first poll window. |
| Navigate-to-load, example.com | 53.5 ms | 12 | Same poll bound. First-ever real navigate in the run took 5237 ms (cold DNS/TLS); median unaffected. |
| OS click (trusted lane) | ~2.2 s wall per act-now batch | smoke | Broker session attempt dominates; page records isTrusted=true. Budget OS lane in seconds, RDP lane in ms; never blend (Council A unknown 6). |

DOM write verified: input value set/read back; JS click isTrusted
false (expected; trusted input needs the OS lane, RT-02 stands for
RDP-only). OS click on the same button records isTrusted=true
(grid_test PASS, offset 186,8 = mozInnerScreen origin).

## Quick probes

(a) RDP screenshot: FAIL. root getScreenshotActor, root screenshot,
target screenshot, target captureScreenshot all return
unrecognizedPacketType on this build. Greeting traits advertise no
screenshot actor. Screenshot lane stays OS grim / computer-use
observe. (RT-03 screenshot leg: not available via RDP here.)

(b) RDP parent/chrome target: SURFACE FOUND (read-only typeof).
listProcesses returns the parent process descriptor (isParent=true);
getTarget gives parentProcessTarget with url
chrome://browser/content/browser.xhtml and a consoleActor. Evaluate
there: typeof gZenWorkspaces = "object", typeof gBrowser = "object",
typeof gZenFolders = "object". Same reads in tab content context:
undefined (expected). Depth beyond typeof (workspace list read/write)
was NOT attempted in this time-box; internals reachability is proven,
internals control is not.

(c) Bind check: PASS. ss -tlnp shows 127.0.0.1:6021 only (zen-bin
pid), confirmed in two runs. No 0.0.0.0 listener. (RT-04 loopback
leg verified for this launch config; silent-attach acceptance itself
remains an owner decision, untouched by this spike.)

## Failure chains (recorded, not skipped)

- Smoke1 self-test wait_load timeout: first navigate from about:blank
  replaces the windowGlobalTarget; polling the stale console never
  sees the new URL (page had loaded, HTTP 200 logged). Fix: navigate
  re-attaches; wait_load re-attaches periodically. Self-test PASS
  after fix.
- Smoke1/2 OS clicks all missed: client attached to tabDescriptor1
  (background, selected=false) while the visible tab was
  tabDescriptor2 (selected=true); listTabs msg["selected"] is null on
  this build and W2-style index-0 picking hits the background tab.
  switchToTab is unrecognized on the descriptor. Fix: pick the tab
  with selected=true. Click then landed first try (trusted=true).
  Observation image is JPEG with image_size field (my PNG-only
  finder fell back to region size; fixed to read image_size).
  mozInnerScreen read 0,0 once pre-settle, 186,8 settled.
- RT-01 attempt 1 driver exit 2: unsolicited root tabListChanged
  event matched the listTabs request filter (both from=root). Fix:
  require "tabs" key. Restarted fresh; attempt-1 profile discarded.
- Panel run 1 (in rt01_driver): finder hostname match returned null
  on Google SERPs (goto-wrapped links) - 4x NO-CLICK, SERPs all PASS.
  Finder v2 (href-includes) then false-hit site:-refinement links
  (P2/P5) and a Sign-in continue link (C1); those PASS labels were
  invalid landings and are superseded, not counted. Finder v3
  (direct-host, cite, guarded-includes) landed P1/P5/C1 validly.
- P2 center-click missed twice: Google language popup overlays the
  result block's right side; block-center click hit the popup.
  Fix: click near title (left+60). P2 then PASS validly.
- Bench1 navigate medians ~303 ms were an artifact of a 300 ms
  client settle sleep in navigate(); reduced to 50 ms and re-ran
  (bench2 ~53 ms, poll-bound). Both runs kept in logs/.
- Screenshot files per site were overwritten across panel runs
  (same filenames); surviving shots are last-run versions. JSONL
  read records preserve every visit's outcome regardless.

## Cleanup verification

All test instances dead (smoke/rdp/ctl profiles, pid+cmdline stops),
local HTTP server killed, ports 6021/9445/2859/8941 closed (ss
verified), no test processes remain, hyprctl clients show only the
owner Zen (439493, ws2) plus pre-existing non-test windows,
computer-use status ok (pill sessions finished, none held), owner
Zen 439493 alive and untouched at end. Throwaway profiles remain
under laptop /tmp/r10w4-* for evidence.

## Evidence labels

- VERIFIED: Google 3/3 PASS address-bar under RDP+attached (JSONL +
  shots); panel valid landings P1 1/2, P2/P5/C1 PASS; control P1+P2
  CHALLENGE-CF with webdriver=true (void rule satisfied); probe
  CLEAN native-false at start/end; client attach/evaluate/navigate/
  DOM-write + isTrusted split (JS false, OS true); latency medians
  above; parent-target typeof reads object x3; screenshot actor
  absent (4 methods refused); loopback-only bind x2; port-owner
  guard + fail-loud probe behavior (self-test PASS path; refusal
  paths code-reviewed, not separately fault-injected).
- ASSUMED: deeper Zen-internals control via parent target (only
  typeof proven); panel pass rate generalizes beyond today (n small,
  warmth possible on P1 visit 2).
- BLOCKED/FAILED honestly: RDP screenshot (no actor); P1 first-visit
  challenge under RDP (real outcome, not a harness failure).

## What this answers for the decision

RT-01/RT-08 (blocking): PASSED on Google (3/3, the leg R1 failed
6/6), panel probabilistic-pass with one P1 challenge. R3a-primary
survives its make-or-break spike. RT-03: internals reachable via RDP
parent target (typeof-level), screenshot not available via RDP (OS
lane covers). RT-02 stands: RDP evaluate clicks are untrusted; the
hybrid OS-input lane is required and proven here (trusted=true).
RT-04 loopback leg verified; silent-attach acceptance still needs
the recorded owner decision. Remaining before landing per redteam:
real-profile acceptance (RT-21), concurrency with owner DevTools
(RT-06), per-update RDP smoke + named owner (RT-05), credential/tab
scoping policy (RT-20). None of those are answered by this spike.

W4. English only. No GitHub commits made.
