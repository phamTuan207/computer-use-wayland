# Batch 6 council 3: independent verification of task 1 partial report

Council 3, 03:09 to 03:14 +07 on 22/11/2026. Report under review:
docs/clone1-zen-ordinary-user-run-20261121.md (244 lines, PARTIAL,
last updated 02:12 +07 by the follow-up agent). I read the report,
then checked every claim I could with my own commands and with the
artifacts on disk. No em dash or en dash in this file.

## Verdict in one line

The report's environment claims and its code claims check out. Its
finding F-B6-01 and its TLS fix are corroborated by a later run
artifact, not by my own live run. The report is STALE: runs at
02:40-02:42 +07 that it does not cover changed three verdicts and
added one new finding (Ctrl+W fails headless). The report must be
updated from the four result JSONs before anyone relies on it.

## What I measured myself (03:09 +07)

- Firefox binary: /home/hatch/workspace/firefox/firefox exists,
  `firefox --version` prints Mozilla Firefox 160.0.1, exit 0.
- Headless screenshot test, fresh temp profile /tmp/ff-c3-check,
  timeout 25 s: exit 0, shot.png 5,763 bytes (same size as the task 1
  agent's 01:40 screenshot), minidump count 0, no crash. Memory at
  test time: total 7934M, free 218M, available 1599M.
- Tarball ~/workspace/firefox-160.0.1.tar.xz: 90,943,956 bytes,
  exact match to the report.
- CA file /usr/local/share/ca-certificates/hatch-egress-ca.crt:
  exists (symlink to /run/hatch/cell-anchors/hatch-egress-ca.pem).
- `which hyprctl`: exit 1, not found. No Hyprland on this machine.
- ~/.zen: does not exist. ~/.mozilla: does not exist. No Zen
  installed on this machine.
- ZT source file: improvements/zen-ordinary-user-tests-20261121.md
  exists on origin/todolist-push (blob 60f5c38). Headings ZT-00
  through ZT-10 all present, titles match the report's scenario
  list exactly (ZT-00 Health gate, ZT-01 article, ZT-02 search,
  ZT-03 new tab, ZT-04 bookmark, ZT-05 workspace, ZT-06 download,
  ZT-07 form, ZT-08 back/forward/reload, ZT-09 many tabs, ZT-10
  sidebar).
- /tmp was wiped again between 02:42 and 03:09 +07: /tmp/firefox
  is gone, and /tmp/diag2.log, diag3.log, diag4.log and
  diag-followup.log are all gone. The only surviving evidence for
  the diag phase is the report text itself plus the result JSONs
  under ~/workspace/b6t1-results/ (home disk persists).

## Claim by claim

### Environment facts: AGREE

Firefox 160.0.1 present and starting cleanly, tarball size exact,
memory tight but workable (free 218M, available 1599M at my test).
The 21/11 segfault window is over for the moment, confirmed by my
own screenshot run, exit 0, zero minidumps.

### ZT-05 NOT APPLICABLE (no Hyprland): AGREE

Verified from the machine: hyprctl not in PATH. The ZT file's
ZT-05 section is workspace switching, which cannot run here.

### ZT-10 NOT APPLICABLE (no Zen sidebar): AGREE

Verified from the machine: no ~/.zen, no Zen binary, stock Firefox
only. Owner-reported F-001 cannot be re-tested here. The runner
already records ZT-10 as NOT APPLICABLE for this reason.

### Certutil profile prep in the runner: AGREE (code read)

I read ~/workspace/b6t1/zt_run.mjs lines 100-118 and 895-915.
prepProfileCerts() runs `certutil -N -d sql:PROFILE
--empty-password`, then `certutil -A -n "Hatch Sandbox Egress CA"
-t "CT,C,c" -i /usr/local/share/ca-certificates/hatch-egress-ca.crt
-d sql:PROFILE`, and returns ok only when both exit codes are 0.
main() removes the profile dir first, writes user.js, calls
prepProfileCerts, and on failure writes a BLOCKED JSON and exits 2
without launching Firefox. The certPrep result (nCode, aCode, ok)
is recorded in every scenario JSON. This is exactly what the
report claims. Runner is 959 lines, node --check passed in my
session (I ran it only as a syntax check, no Firefox spawned).

### F-B6-02, HTTPS fails in fresh profiles, certutil fix works: AGREE, corroborated by run artifacts, not by my own live run

I did not run a live TLS check myself. The 02:40-02:42 run
artifacts corroborate the fix: all four JSONs (ZT-00..ZT-03) show
certPrep ok true with nCode 0 and aCode 0, launchOk true, and
ZT-00 step 5 title PASS with title "Example Domain" after a BiDi
goto to https://example.com. The fix works inside the runner.
The sub-claim that security.enterprise_roots.enabled=true alone
did NOT fix it has no surviving evidence (diag logs wiped); I
mark that sub-claim reported-but-unverified-by-council.

### F-B6-01, Ctrl+L does nothing headless: AGREE, corroborated by a run artifact, not by my own live run

I did not run the Ctrl+L test myself, and the original diag logs
are gone. But the 02:40 ZT-00.json, produced by the runner itself
rather than by the task 1 agent's diagnostic, records step
4-ctrl-l-type-enter as NOT APPLICABLE with hrefAfterCtrlL
"about:blank" and the note "Ctrl+L does nothing in headless
Firefox (no address bar); navigation below uses BiDi goto
instead". That is independent corroboration of the same behaviour
from a different run. AGREE.

### F-B6-03, Wikipedia goto times out: AGREE, and the count is now 5, not 2

The report says the timeout was reproduced twice (02:03 and 02:01
diags). Three more reproductions happened in the scenario runs at
02:41, 02:41 and 02:42 +07: ZT-01.json, ZT-02.json and ZT-03.json
all have verdict ERROR, error "Navigation timeout of 30000 ms
exceeded", elapsed 35,572 ms, 35,411 ms and 36,047 ms. I checked
the runner code: ZT-01 navigates to https://en.wikipedia.org/
(line 306), ZT-02 and ZT-03 to
https://en.wikipedia.org/wiki/Ho_Chi_Minh_City (lines 369, 415),
so all three timeouts are the same Wikipedia goto failure. The
report's count of 2 is stale; the true count is 5.

### ZT-00 pre-fix gate run: AGREE

ZT-00-pre-fix.json matches the report exactly: start 01:43:58
+07, verdict BLOCKED, elapsed 17,960 ms, steps 0 PASS, 2 PASS,
4 DONE, 5 FAIL. The preservation step worked.

## What the report misses: runs at 02:40-02:42 +07

Someone ran the fixed runner at 02:40:13 to 02:42:36 +07. The
report, last updated 02:12, does not cover these runs. I do not
know who ran them; the parent should identify the runner, because
the follow-up agent said scenario runs were blocked on an exec
approval, yet these runs happened.

- ZT-00.json (new, 2,690 bytes): verdict FAIL, elapsed 11,437 ms.
  Steps: 0 PASS, 2 PASS, 4-ctrl-l-type-enter NOT APPLICABLE
  (hrefAfterCtrlL about:blank), 4b-bidi-goto-example-com DONE,
  5-title-example-domain PASS ("Example Domain"),
  7-pre-close-check PASS, 7-ctrl-w-close FAIL (closedBy "none",
  1 tab before, 1 after), 7-title-set-restored FAIL. So the
  adapted gate FAILED, not for the Ctrl+L reason but because the
  tab would not close. The report's line "adapted gate not yet
  run" is now wrong.
- ZT-01.json, ZT-02.json, ZT-03.json (1,447 bytes each): verdict
  ERROR on navigation timeout, as above. The report's "NOT RUN"
  for ZT-01, ZT-02 and ZT-03 is now wrong; they ran and errored.
  Error screenshots exist in ~/workspace/b6t1-results/shots/
  (ZT-01-uncaught-error.png 7,393 bytes, ZT-02 and ZT-03
  76,304 bytes each).
- ZT-04..ZT-09: still not run, no JSONs. That part of the report
  is still correct.

## New finding from the 02:40 run: Ctrl+W does not close a tab headless (C3-01)

ZT-00 steps 7-ctrl-w-close FAIL and 7-title-set-restored FAIL at
02:40:18 +07: after Ctrl+W the tab count stayed 1 and the title
stayed "Example Domain". The report said Ctrl+T / Ctrl+W were
"NOT YET TESTED". That is now stale: there IS evidence, and it
says Ctrl+W fails headless, consistent with Ctrl+L failing for
the same reason (no chrome to receive the shortcut). Ctrl+T is
still untested. I did not run this myself; the evidence is the
recorded step output in ZT-00.json. (I do not call this F-B6-04:
the runner code already uses that name for the ZT-01 article
title finding.)

## Gaps and recommendations for the parent

1. Update the task 1 report from the four result JSONs before
   anyone relies on it: ZT-00 adapted gate FAIL (11,437 ms, Ctrl+W
   close fails), ZT-01/02/03 ERROR on Wikipedia navigation timeout,
   F-B6-03 count 5, and the new Ctrl+W finding.
2. Identify who ran the 02:40-02:42 scenarios and whether the exec
   approval the follow-up agent was blocked on is still pending
   for future runs. No approval timed out during my session; my
   screenshot test invoked the Firefox binary directly and needed
   no approval.
3. Future diagnostic logs should go under ~/workspace, not /tmp:
   /tmp was wiped twice in this batch (once before 01:39, once
   between 02:42 and 03:09), and every diag log from the task 1
   work is now gone. Only the ~/workspace result JSONs survived.
4. The Wikipedia goto is now the single blocker for ZT-01..ZT-09:
   every scenario's first navigation is a Wikipedia goto with a
   30 s timeout and waitUntil load, and it has failed 5 of 5 times
   through BiDi while curl reaches the same article in about 1 s.
   The next run should try a longer timeout or waitUntil
   domcontentloaded before any scenario verdict depends on it.
