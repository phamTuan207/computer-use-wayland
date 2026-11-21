# Batch 6 task 1: ZT-01..ZT-10 blind run on local Firefox (PARTIAL, BLOCKED)

Report by batch 6 task 1 agent. Source file:
improvements/zen-ordinary-user-tests-20261121.md at origin/todolist-push
tip e4082ff, revision v2 (22:34 21/11). All numbers below come from runs
or files read this session (22/11 01:38 to 02:05 +07). No em dash or
en dash in this file.

## Verdict summary

| Scenario | Verdict | Evidence |
|---|---|---|
| ZT-00 gate | FAIL as written, ADAPTED gate not yet run | Ctrl+L navigation does nothing headless (proved); BiDi goto to example.com works after a TLS trust fix (proved 02:03 +07); Wikipedia goto timed out once (30 s) |
| ZT-01 | NOT RUN | blocked by the gate outcome + the approval timeout below |
| ZT-02 | NOT RUN | same |
| ZT-03 | NOT RUN | same |
| ZT-04 | NOT RUN | same |
| ZT-05 | NOT APPLICABLE | no Hyprland, no hyprctl, no workspaces on this machine |
| ZT-06 | NOT RUN | same as ZT-01 |
| ZT-07 | NOT RUN | same as ZT-01 |
| ZT-08 | NOT RUN | same as ZT-01 |
| ZT-09 | NOT RUN | same as ZT-01 |
| ZT-10 | NOT APPLICABLE | no Zen sidebar in stock Firefox; F-001 cannot be re-tested here |

No scenario was faked. Nothing below claims a run that did not happen.

## Environment facts (verified this session)

- Firefox 160.0.1 re-downloaded 01:40 +07 from the Mozilla download
  service (pinned 160.0.1 build). Tarball
  ~/workspace/firefox-160.0.1.tar.xz, 90,943,956 bytes, exactly the
  batch 3 size. Extracted to ~/workspace/firefox (home disk, not
  /tmp, because /tmp is a 512M tmpfs). `firefox --version` prints
  Mozilla Firefox 160.0.1, exit 0.
- /tmp/firefox was gone at 01:39 +07 (VM restart wiped /tmp), as the
  brief said. Note: a Firefox at /tmp/firefox appeared again around
  02:00 +07 owned by another agent's exec session (pid 12112, port
  1935x). I did not touch it.
- Memory at 01:39 +07: total 7934M, free 144M, available 469M. At
  01:58 +07 after cleanup: free 545M, available 2098M. Firefox
  headless screenshot test at 01:40 +07: exit 0, screenshot
  /tmp/ff-b6-test.png 5,763 bytes, no minidump. Firefox starts now;
  the 21/11 segfault window (10 attempts, 90 min) is over for the
  moment.
- Internet works from curl: en.wikipedia.org 301, the Ho Chi Minh
  City article 200 in 1.18 s, httpbin.org/forms/post 200,
  irs.gov fw9.pdf 200, example.com 200 (checked 01:41 +07).
- No ~/workspace/ssh-laptop.sh on this machine, so the ZT file's
  laptop route (zen_dom.py, hyprctl, computer-use CLI, the owner's
  real Zen) does not exist here. This run is a local stock-Firefox
  adaptation only. It is NOT a Zen result.
- Driver: puppeteer-core 24.43.1 from ~/workspace/b5t5-scratch over
  WebDriver BiDi, fresh profile per scenario. Runner script:
  ~/workspace/b6t1/zt_run.mjs (syntax checked OK). It was built but
  its scenarios have NOT run yet, except ZT-00 once (see below).

## ZT-00 gate run (01:43:58 to 01:44:08 +07, 17,960 ms)

- Step 0 baseline tab list: PASS, 1 tab, title "" (about:blank).
- Step 2 BiDi port answers: PASS, curl http://127.0.0.1:PORT/ 200.
- Step 4 Ctrl+L, type example.com, Enter: the page stayed
  about:blank, title "" after 10 s of polling.
- Step 5 title "Example Domain" within 10 s: FAIL, title "".
- Verdict: BLOCKED (gate failed, per the file's rule 9).
- Result file: ~/workspace/b6t1-results/ZT-00.json.

## Finding F-B6-01: Ctrl+L does nothing in headless Firefox (proved)

Reproduced in a separate diagnostic at 01:47 +07: after Ctrl+L,
typing "example.com", Enter, and waiting 3 s, location.href was
still about:blank and title "". Headless Firefox has no address
bar, so the chrome shortcut has nowhere to go. Every ZT scenario
navigates with Ctrl+L + type + Enter, so that exact path cannot
run headless. The runner adapts navigation to BiDi goto (same
checked outcome: the right page loads with the right title) and
records the adaptation. This is an environment limitation, not a
browser defect and not a test fix.

## Finding F-B6-02: HTTPS fails in fresh Firefox profiles (proved, then fixed)

- At 01:47 +07, BiDi goto to https://example.com failed with:
  Protocol error (browsingContext.navigate): unknown error,
  NS_ERROR_GENERATE_FAILURE, SEC_ERROR_UNKNOWN_ISSUER.
- Root cause, verified 01:49 +07: all traffic on this machine goes
  through an egress proxy that re-signs TLS with a local CA. curl
  verifies OK because it uses the machine CA bundle, which
  includes that CA. Firefox uses its own NSS store and did not
  trust the CA, so every HTTPS site failed with
  SEC_ERROR_UNKNOWN_ISSUER. No earlier batch hit this because
  batch 5 drove only local http fixtures.
- Fix, verified 02:03 +07: prepare each fresh profile with
  certutil before launch: `certutil -N -d sql:PROFILE
  --empty-password`, then `certutil -A -n "Hatch Sandbox Egress CA"
  -t "CT,C,c" -i /usr/local/share/ca-certificates/hatch-egress-ca.crt
  -d sql:PROFILE`. After that, BiDi goto to https://example.com
  returned title "Example Domain" (href https://example.com/).
  The user.js pref security.enterprise_roots.enabled=true alone did
  NOT fix it (tested 01:56 +07, same SEC_ERROR_UNKNOWN_ISSUER).
- The runner script (zt_run.mjs) does NOT yet include the certutil
  profile preparation step. That step must be added before any
  scenario runs, or every HTTPS navigation will fail the same way.
- Note: the egress proxy address and its credential appear in this
  machine's environment variables. They are not reproduced here.

## Finding F-B6-03: Wikipedia goto timed out once (30 s, 02:03 +07)

After the TLS fix, BiDi goto to
https://en.wikipedia.org/wiki/Ho_Chi_Minh_City with waitUntil load
and a 30 s timeout threw "Navigation timeout of 30000 ms exceeded".
example.com had loaded fine seconds earlier in the same session.
Cause unknown: possibly proxy slowness, page weight, or load from
the other agent's Firefox running concurrently. Not retried yet.
Needs one clean re-test before any scenario verdict depends on it.

## Other verified environment behaviours

- Ctrl+T new tab and Ctrl+W close in headless Firefox: NOT YET
  TESTED. The diagnostic that was to test them aborted at the
  Wikipedia goto timeout (see F-B6-03). The runner closes tabs
  with Ctrl+W first and falls back to BiDi page.close(), recording
  which mechanism closed the tab.
- Firefox caps concurrent BiDi sessions ("Maximum number of active
  sessions"). Two leftover Firefox processes from crashed
  diagnostics blocked a later connect. Lesson recorded: every run
  must kill its own Firefox (browser.close + SIGKILL on the exact
  pid it spawned) and never pkill by pattern, because other
  agents run Firefox on this machine too.
- Headless screenshots capture the viewport only, never browser
  chrome (address bar, find bar, toolbar, sidebar, bookmark
  library, download panel). Any ZT step that checks chrome by
  screenshot is therefore NOT APPLICABLE headless, and the report
  must say so instead of passing or failing it.

## Zen-only steps that cannot run on stock headless Firefox

These are NOT APPLICABLE here, recorded in the runner already:

- ZT-03 step 4, ZT-09 step 5 (sidebar X), ZT-10 steps 3-6: the Zen
  sidebar does not exist in stock Firefox. F-001 (owner-reported
  unclickable Zen, sidebar collapsed to icons) cannot be re-tested
  by this run at all.
- ZT-04 steps 2-7: bookmark star, Ctrl+D dialog, library
  Ctrl+Shift+O. All browser chrome, no BiDi read of the bookmark
  store.
- ZT-05 all steps: Hyprland workspace switching (owner-reported
  F-002). No Hyprland, no hyprctl, no workspaces here.
- ZT-02 steps 3, 5, 6 (find bar visible in screenshot): chrome
  not rendered headless. The runner uses window.find('population')
  as a DOM-level proxy and marks the scenario INCONCLUSIVE on the
  chrome part.
- ZT-06 step 6 (download panel entry): chrome. The runner opens
  the downloaded file directly instead.
- ZT-08 steps 4-6 (toolbar Back/Forward buttons): chrome. The
  runner verifies the same history moves by keyboard Alt+Left and
  Alt+Right in steps 6b and 8.

## What is still owed for this task

1. Add the certutil profile preparation to zt_run.mjs launch
   (profile DB create + CA import before Firefox starts).
2. Re-test the Wikipedia goto once, cleanly, with no other
   Firefox running.
3. Test Ctrl+T and Ctrl+W in headless Firefox (diag script exists
   at ~/workspace/b6t1/diag_tls.mjs, needs a rerun).
4. Run ZT-00 (adapted gate), then ZT-01..ZT-10 in order, one
   fresh Firefox per scenario, results to
   ~/workspace/b6t1-results/<scenario>.json, screenshots to
   ~/workspace/b6t1-results/shots/.
5. Fill in this report from those result files.

## Approval timeout (02:04 +07)

The action that ran the TLS diagnostic (node diag_tls.mjs) returned
with a notice that an approval for it was not answered in time.
The command itself completed and its output is quoted above
(example.com loaded, Wikipedia goto timed out). I did not retry
any part of it after that notice. If a further run needs that
approval, it still needs to be given.

## Files

- Runner: ~/workspace/b6t1/zt_run.mjs (syntax OK, scenarios not run)
- Gate result: ~/workspace/b6t1-results/ZT-00.json
- Diagnostics: ~/workspace/b6t1/diag_ctrlL.mjs,
  ~/workspace/b6t1/diag_ctrlL2.mjs, ~/workspace/b6t1/diag_ctrlL3.mjs,
  ~/workspace/b6t1/diag_tls.mjs (logs in /tmp/diag2.log,
  /tmp/diag3.log, /tmp/diag4.log)
- Firefox: ~/workspace/firefox (160.0.1), tarball
  ~/workspace/firefox-160.0.1.tar.xz (90,943,956 bytes)
