# Batch 6 task 1: ZT-01..ZT-10 blind run on local Firefox (COMPLETE, runs 02:40 to 03:14 +07)

Report by batch 6 task 1 agent. Source file:
improvements/zen-ordinary-user-tests-20261121.md at origin/todolist-push
tip e4082ff, revision v2 (22:34 21/11). All numbers below come from runs
or files read this session (22/11 01:38 to 02:05 +07). No em dash or
en dash in this file.

Follow-up by batch 6 task 1 follow-up agent, 02:00 to 02:02 +07:
certutil profile prep added to the runner (step 1 done, syntax OK);
Wikipedia goto re-tested once more and timed out again (step 2 done,
F-B6-03 reproduced a second time); Ctrl+T / Ctrl+W still untested;
no scenario run yet; the run is now blocked on an exec approval that
timed out (see Approval timeout below).

Follow-up 2 by batch 6 task 1 follow-up 2 agent, 02:40 to 03:14 +07:
the approval timeout did NOT recur, no approval was requested or timed
out in this session, and all scenarios ZT-00..ZT-10 ran once each with
the runner as written. Results are in the updated table below and in
the Follow-up 2 section at the end of this file. A second diagnostic
(diag_wiki2.mjs, second Wikipedia navigation plus PDF button plus
select checks) was started at 03:15 +07 and aborted by the cron
execution timeout at 03:37 +07 with no output captured, so it produced
no evidence and was not retried.

## Verdict summary

| Scenario | Verdict | Evidence |
|---|---|---|
| ZT-00 gate | FAIL (adapted gate ran 02:40, 11,437 ms) | BiDi goto example.com PASS, title "Example Domain"; Ctrl+L NOT APPLICABLE headless (proved again); Ctrl+W on the last tab FAIL, tab count stayed 1 (F-B6-31) |
| ZT-01 | ERROR, 35,572 ms | Wikipedia goto timed out at 30 s, F-B6-03 third occurrence |
| ZT-02 | ERROR, 35,411 ms | Wikipedia goto timed out at 30 s, F-B6-03 fourth occurrence |
| ZT-03 | ERROR, 36,047 ms | Wikipedia goto timed out at 30 s, F-B6-03 fifth occurrence |
| ZT-04 | NOT APPLICABLE, 32,959 ms | Wikipedia article loaded in 24,305 ms, title PASS; bookmark star, Ctrl+D dialog, library all chrome, NOT APPLICABLE; cleanup FAIL (last-tab close, F-B6-31) |
| ZT-05 | NOT APPLICABLE, 5,425 ms | No Hyprland, no hyprctl, no workspaces on this machine |
| ZT-06 | FAIL, 11,557 ms | PDF renders PASS, title "Form W-9 (Rev. March 2024) - fw9.pdf"; viewer download button #download not found, F-B6-14; steps 5-8 not reached |
| ZT-07 | FAIL, 8,480 ms | Form present PASS, custname and custtel PASS, comments PASS; size select stayed "small" after ArrowDown, F-B6-18; submit step not reached |
| ZT-08 | ERROR, 48,126 ms | First article loaded, second goto (Vietnam) threw NS_ERROR_NET_RESET, F-B6-32 |
| ZT-09 | ERROR, 47,917 ms | First tab loaded, second tab goto (Vietnam) threw NS_ERROR_NET_RESET, F-B6-32 |
| ZT-10 | ERROR, 47,592 ms | First tab loaded, second tab goto (Vietnam) threw NS_ERROR_NET_RESET, F-B6-32 |

Counts over ZT-00..ZT-10 (11 runs): PASS 0, FAIL 3 (ZT-00, ZT-06, ZT-07),
ERROR 6 (ZT-01, ZT-02, ZT-03, ZT-08, ZT-09, ZT-10), NOT APPLICABLE 2
(ZT-04, ZT-05). No scenario passed as written. Nothing below claims a
run that did not happen.

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

## Finding F-B6-03: Wikipedia goto timed out twice (30 s, 02:03 and 02:01 +07)

After the TLS fix, BiDi goto to
https://en.wikipedia.org/wiki/Ho_Chi_Minh_City with waitUntil load
and a 30 s timeout threw "Navigation timeout of 30000 ms exceeded".
example.com had loaded fine seconds earlier in the same session.
Cause unknown: possibly proxy slowness, page weight, or load from
the other agent's Firefox running concurrently. Not retried yet.
Needs one clean re-test before any scenario verdict depends on it.

Second occurrence, follow-up re-test 02:01:44 +07: node diag_tls.mjs
ran 36 s (certutil -N: 0, -A: 0, BiDi up, example.com loaded with
title "Example Domain"), then the same Wikipedia goto threw the same
"Navigation timeout of 30000 ms exceeded". Two other headless Firefox
processes were running at the time (task 3 pid 18967 port 19794,
ls-preinit pid 19604 port 19108); neither was touched. Memory at
02:01 +07: free 142M, available 1157M. Log: /tmp/diag-followup.log.
The timeout is now reproduced twice, not once. Note that curl reached
the same article with 200 in 1.18 s at 01:41 +07, so the proxy can
reach Wikipedia fast; the BiDi goto with waitUntil load is the part
that stalls. A re-test with a longer timeout, or with waitUntil
domcontentloaded, is worth trying before any scenario depends on a
Wikipedia goto.

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
   (profile DB create + CA import before Firefox starts). DONE in the
   follow-up, 02:00 +07: prepProfileCerts() added (certutil -N then
   -A with trust CT,C,c, CA file
   /usr/local/share/ca-certificates/hatch-egress-ca.crt), called in
   main() after writeUserJs and before launchFirefox; the profile dir
   is removed first so every run starts from a truly fresh profile;
   if cert prep fails the runner writes BLOCKED and exits 2 without
   launching Firefox. Syntax checked OK (node --check). The certPrep
   result (nCode, aCode, ok) is recorded in every scenario JSON.
2. Re-test the Wikipedia goto once, cleanly, with no other
   Firefox running. DONE in the follow-up, 02:01:44 +07, but it timed
   out AGAIN (30 s), so F-B6-03 is now reproduced twice. A clean
   re-test with no other Firefox running, a longer timeout, or
   waitUntil domcontentloaded is still owed before any scenario
   verdict depends on a Wikipedia goto.
3. Test Ctrl+T and Ctrl+W in headless Firefox (diag script exists
   at ~/workspace/b6t1/diag_tls.mjs, needs a rerun). STILL OWED: the
   02:01 diag aborted at the Wikipedia timeout before reaching those
   lines.
4. Run ZT-00 (adapted gate), then ZT-01..ZT-10 in order, one
   fresh Firefox per scenario, results to
   ~/workspace/b6t1-results/<scenario>.json, screenshots to
   ~/workspace/b6t1-results/shots/. STILL OWED. The old ZT-00.json
   (pre-fix BLOCKED run) was preserved as ZT-00-pre-fix.json before
   any re-run, so a new ZT-00 run may overwrite ZT-00.json.
5. Fill in this report from those result files. STILL OWED (this
   file holds the follow-up findings so far, no scenario results).
6. Exec approval: the runs in steps 2-4 need the pending approval
   for running node commands that spawn Firefox (see Approval timeout
   below). Do not retry them until it is given.

## Approval timeout (02:04 +07)

The action that ran the TLS diagnostic (node diag_tls.mjs) returned
with a notice that an approval for it was not answered in time.
The command itself completed and its output is quoted above
(example.com loaded, Wikipedia goto timed out). I did not retry
any part of it after that notice. If a further run needs that
approval, it still needs to be given.

Second occurrence (02:01 +07, follow-up): the same command
(node diag_tls.mjs) again returned with userConfirmationRequired
true and userConfirmationStatus timed_out, while its output shows
the run itself completed in 36 s (certutil 0/0, BiDi up, example.com
loaded, Wikipedia timeout). Per the runtime instruction, the
unapproved part was not performed and must not be retried unless the
user asks for it again. I therefore did NOT retry the diagnostic and
did NOT start the ZT-00..ZT-10 scenario runs, because they run the
same kind of action (node spawning Firefox). The scenario runs are
blocked until that approval is given. The parent agent needs to
surface this to the user: the approval for running the Firefox
driver commands is still pending.

## Files

- Runner: ~/workspace/b6t1/zt_run.mjs (syntax OK, scenarios not run)
- Gate result: ~/workspace/b6t1-results/ZT-00.json
- Diagnostics: ~/workspace/b6t1/diag_ctrlL.mjs,
  ~/workspace/b6t1/diag_ctrlL2.mjs, ~/workspace/b6t1/diag_ctrlL3.mjs,
  ~/workspace/b6t1/diag_tls.mjs (logs in /tmp/diag2.log,
  /tmp/diag3.log, /tmp/diag4.log)
- Firefox: ~/workspace/firefox (160.0.1), tarball
  ~/workspace/firefox-160.0.1.tar.xz (90,943,956 bytes)

## Follow-up 2: all scenarios ran, 02:40 to 03:14 +07

Agent: batch 6 task 1 follow-up 2. The previous follow-up was blocked
because running node/Firefox commands returned an approval timeout
twice. In this session no approval was requested and none timed out:
the first run (ZT-00, 02:40:13 +07) executed at once, and every later
run did the same. The approval blocker from 02:01 and 02:04 +07 did not
recur. Runner: ~/workspace/b6t1/zt_run.mjs, unchanged from the
follow-up except nothing, certutil profile prep included, one fresh
Firefox 160.0.1 per scenario, one fresh profile per scenario. Every
result file is ~/workspace/b6t1-results/<scenario>.json, screenshots
in ~/workspace/b6t1-results/shots/.

### Run log (wall clock +07, elapsed from each result file)

Note on times: elapsedMs in each result file runs about 4 to 7 s
longer than the wallStart to wallEnd span, because it also covers
browser cleanup after wallEnd is stamped. Both numbers are quoted
exactly as recorded in the files.

- ZT-00, 02:40:13 to 02:40:18, 11,437 ms, verdict FAIL. Steps: baseline
  PASS, BiDi port PASS, Ctrl+L NOT APPLICABLE (href stayed
  about:blank), BiDi goto example.com DONE, title "Example Domain"
  PASS, pre-close check PASS, Ctrl+W close FAIL (closedBy none,
  before 1, after 1), title set restored FAIL. Cert prep ok (nCode 0,
  aCode 0). The old pre-fix ZT-00.json was preserved as
  ZT-00-pre-fix.json before this run, as planned.
- ZT-01, 02:40:51 to 02:41:22, 35,572 ms, verdict ERROR. Cert prep ok,
  launch ok, then the Wikipedia goto threw "Navigation timeout of
  30000 ms exceeded". No step recorded. Screenshot
  ZT-01-uncaught-error.png (7,393 bytes, blank viewport).
- ZT-02, 02:41:28 to 02:41:59, 35,411 ms, verdict ERROR. Same
  30 s Wikipedia goto timeout. Screenshot ZT-02-uncaught-error.png
  (76,304 bytes).
- ZT-03, 02:42:05 to 02:42:36, 36,047 ms, verdict ERROR. Same
  30 s Wikipedia goto timeout. Screenshot ZT-03-uncaught-error.png
  (76,304 bytes).
- Note: the exec service restarted while the ZT-01..ZT-03 batch result
  was being delivered (about 02:42 to 03:08 +07). All three result
  files were already on disk with the times above, so nothing was
  re-run and nothing was lost. No Firefox process was left running.
- ZT-04, 03:10:28 to 03:10:55, 32,959 ms, verdict NOT APPLICABLE.
  Article title PASS at elapsed 24,305 ms ("Ho Chi Minh City -
  Wikipedia", curl 200). Steps 2-7 NOT APPLICABLE (bookmark chrome).
  Pre-close check PASS, cleanup FAIL (closedBy none, last tab).
- ZT-05, 03:10:55 to 03:11:00, 5,425 ms, verdict NOT APPLICABLE. All
  six steps NOT APPLICABLE (no Hyprland).
- ZT-06, 03:11:09 to 03:11:14, 11,557 ms, verdict FAIL. PDF renders
  PASS at elapsed 4,403 ms (title "Form W-9 (Rev. March 2024) -
  fw9.pdf", viewer present, curl 200). Download dir clean PASS.
  Viewer download button FAIL (selector #download not found, rect
  null), finding F-B6-14 with screenshot ZT-06-step4-nobutton.png
  (275,306 bytes). Steps 5-8 not reached; no file was downloaded.
  Process exit code 1.
- ZT-07, 03:11:48 to 03:11:51, 8,480 ms, verdict FAIL. Form present
  PASS at elapsed 1,515 ms (curl 200). custname PASS ("Nguyen Van
  A"), custtel PASS ("0901234567"), size select FAIL (value stayed
  "small"), comments PASS ("Ordinary user test, no login, no
  account."). Finding F-B6-18 with screenshot ZT-07-fill-fail.png
  (46,128 bytes). Submit and echo steps not reached. Process exit
  code 1.
- ZT-08, 03:12:08 to 03:12:51, 48,126 ms, verdict ERROR. The failing
  goto was https://en.wikipedia.org/wiki/Vietnam with "Protocol
  error (browsingContext.navigate): unknown error Error:
  NS_ERROR_NET_RESET". No steps survive in the result file (see the
  note on lost step data below); the error URL shows the first
  article (Ho Chi Minh City) loaded and the second navigation failed.
- ZT-09, 03:12:57 to 03:13:40, 47,917 ms, verdict ERROR. Same
  NS_ERROR_NET_RESET on the Vietnam tab goto. First tab (Ho Chi Minh
  City) loaded, second tab failed.
- ZT-10, 03:13:46 to 03:14:29, 47,592 ms, verdict ERROR. Same
  NS_ERROR_NET_RESET on the Vietnam tab goto. First tab loaded,
  second tab failed.
- Control check 03:14:49 +07, after the runs: curl to the same
  Wikipedia article returned 200 in 0.80 s, example.com 200 in
  0.80 s. The proxy path was healthy at that moment. Memory then:
  free 524M, available 1,913M. No Firefox process left running.

### Finding F-B6-29: Wikipedia load time straddles the 30 s timeout (proved)

The Wikipedia article does load through BiDi, but slowly and with
wide variance. Measured in this session: ZT-04 title PASS at 24.3 s
after launch; ZT-01, ZT-02, ZT-03 goto timeouts at exactly 30 s;
diagnostic diag_wiki.mjs (03:09:19 to 03:09:52 +07) reached
domcontentloaded in 27 s after BiDi up (31 s after process start)
with title "Ho Chi Minh City - Wikipedia", readyState interactive,
and the load event fired 0.5 s later with zero pending resources.
Curl fetched the same article in 1.18 s at 01:41 +07 and 0.80 s at
03:14 +07, so the network path is fast and the delay sits in Firefox
or the BiDi navigation path under this proxy, not in the site. The
runner's goto uses waitUntil load with a 30 s timeout, so a page that
takes 24 to 31 s to load passes or fails by luck. That is why ZT-04
passed its navigation while ZT-01, ZT-02 and ZT-03 failed on the
identical first step. The scenarios were run as written and the
verdicts above stand; whether to re-run them with a longer timeout
or domcontentloaded is a decision for Muse, not a fix made here.

### Finding F-B6-30: Ctrl+T does nothing in headless Firefox (proved)

In diag_wiki.mjs at 03:09:52 +07, with one tab open, Ctrl+T left the
tab count at 1 (before 1, after 1). The Ctrl+W test in the same
diagnostic never ran because it was gated on a new tab appearing.
This matches F-B6-01 (Ctrl+L) and the ZT-00 Ctrl+W result: chrome
shortcuts for tab and address bar management do not work in headless
Firefox. Any ZT step that depends on Ctrl+T, Ctrl+W, Ctrl+Shift+T or
Ctrl+Tab cannot run as written headless; the runner already falls
back to BiDi page close where it can, and records which mechanism
closed each tab.

### Finding F-B6-31: the last tab cannot be closed, by Ctrl+W or by BiDi (proved)

ZT-00 step 7 (02:40:18 +07) and ZT-04 step 8 (03:10:55 +07) both
ended with closedBy none, tab count before 1, after 1. The runner
tries Ctrl+W, waits 800 ms, then page.close(), waits 400 ms, and
neither reduces the count from 1. Firefox keeps one tab open, and
Puppeteer replaces a closed last page with a fresh about:blank tab,
so the count never drops. The "title set restored" step therefore
fails as a consequence, comparing [""] with ["Example Domain"] or
["Ho Chi Minh City - Wikipedia"]. This is a runner artifact for the
single-tab case, not a browser defect: closing a non-last tab is a
different question, and ZT-03, ZT-09 and ZT-10 (which close non-last
tabs) never reached their close steps because their navigations
failed first. The ZT-00 FAIL verdict is driven by this artifact plus
nothing else; the gate navigation itself passed.

### Finding F-B6-32: second Wikipedia navigation in one session fails with NS_ERROR_NET_RESET (proved three times)

ZT-08, ZT-09 and ZT-10 each loaded the first Wikipedia article and
then failed on the second navigation, all to
https://en.wikipedia.org/wiki/Vietnam, all with NS_ERROR_NET_RESET
at the navigation commit step, at 03:12:51, 03:13:40 and 03:14:29
+07. Three occurrences in a row, three different scenarios, same
URL, same error. The first navigation in each session succeeded, so
this is not the TLS issue (F-B6-02, fixed) and not the 30 s timeout
(F-B6-03, different error). It looks like a connection reset on a
follow-up navigation through the proxy, but the cause was not
isolated: a diagnostic to repeat the two-navigation sequence
(diag_wiki2.mjs) was started at 03:15 +07 and aborted by the cron
execution timeout at 03:37 +07 with no output captured, so the
repeat test produced no evidence. This finding stays open until that
repeat test runs.

### Finding F-B6-14 (ZT-06): PDF viewer download button #download not found

Recorded by the runner at 03:11:14 +07. The PDF itself rendered
(title and #viewer present), but document.querySelector('#download')
returned nothing at elapsed 4,449 ms, immediately after the viewer
check passed. The screenshot ZT-06-step4-nobutton.png (275,306
bytes) shows the rendered PDF. Not yet distinguished whether the
button truly has no #download id in the BiDi-visible document, or
whether the check ran before the viewer toolbar finished building.
A follow-up check that waits 5 s and lists the viewer toolbar button
ids was planned in diag_wiki2.mjs and did not run (aborted, see
above).

### Finding F-B6-18 (ZT-07): select stays "small" after ArrowDown (proved once)

Recorded by the runner at 03:11:51 +07. The runner clicked the
[name=size] select, then pressed ArrowDown up to 5 times, reading
the value after each press. The value stayed "small" through all 5
presses, while the two text fields and the textarea filled correctly
by typing in the same session. A follow-up check of the option list
and of ArrowDown plus Enter behaviour was planned in diag_wiki2.mjs
and did not run (aborted, see above).

### Note: step data lost for the three ERROR scenarios

When a scenario function throws (uncaught goto error), the runner
main() catch handler writes a fresh ERROR result file with only the
verdict, error text and error screenshot. The steps recorded before
the throw are not included, so ZT-01, ZT-02, ZT-03, ZT-08, ZT-09 and
ZT-10 have steps [] in their JSON files even though ZT-08, ZT-09 and
ZT-10 had completed their first navigation. The failing URL in each
error field is the evidence used above. This is a runner logging gap
worth fixing before any re-run, so a re-run records partial steps.

### What is still owed for this task

1. Repeat diagnostic diag_wiki2.mjs (file exists at
   ~/workspace/b6t1/diag_wiki2.mjs, syntax checked OK): second and
   third Wikipedia navigations in one session, PDF viewer button ids
   after a 5 s wait, httpbin select ArrowDown plus Enter. It was
   aborted at 03:37 +07 by the cron execution timeout with no output.
   NOT RUN. It needs a fresh session and a run window longer than its
   worst case (about 4 minutes).
2. Decision for Muse: re-run ZT-01, ZT-02, ZT-03, ZT-08, ZT-09, ZT-10
   with a longer goto timeout (the page takes 24 to 31 s) or with
   waitUntil domcontentloaded, and fix the runner so ERROR result
   files keep the steps recorded before the throw. No re-run was done
   here, because changing the timeout would change the blind verdicts
   and that call belongs to Muse.
3. ZT-10 as written (Zen sidebar, owner-reported F-001) remains
   untested: its run failed on the Vietnam navigation before reaching
   any sidebar step, and stock Firefox has no Zen sidebar in any case.
4. The report file itself is complete for this follow-up. Do NOT edit
   coord/clone1.md from this task; the coordinator updates coord.

## Files (follow-up 2 additions)

- Results: ~/workspace/b6t1-results/ZT-00.json (re-run 02:40, pre-fix
  preserved as ZT-00-pre-fix.json), ZT-01.json, ZT-02.json,
  ZT-03.json, ZT-04.json, ZT-05.json, ZT-06.json, ZT-07.json,
  ZT-08.json, ZT-09.json, ZT-10.json (all 02:40 to 03:14 +07)
- Screenshots: ~/workspace/b6t1-results/shots/ (11 files, including
  ZT-06-step4-nobutton.png, ZT-07-fill-fail.png, the three
  uncaught-error shots for ZT-01..ZT-03, the three for ZT-08..ZT-10,
  and diag-wiki-final.png)
- Diagnostics: ~/workspace/b6t1/diag_wiki.mjs (ran 03:09, full output
  in F-B6-29 and F-B6-30 above), ~/workspace/b6t1/diag_wiki2.mjs
  (syntax OK, started 03:15, aborted 03:37 by the cron timeout, no
  output captured)
- Profiles: ~/workspace/b6t1-results/profiles/ZT-00..ZT-10,
  diag-wiki, diag-wiki2
