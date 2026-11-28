# R3-037 rerun scorer B grade

- Task: R3-037 (Tier B), rerun
- Runner: Codex (session 01a22033-5509-7530-991d-b41adea7467f)
- Scorer: scorerB (substitute independent, Mochi resting)
- Scorer session ID bc98c157-e056-4d5f-bcf6-32c322012f24
- Scored at: 2026-11-28T10:48:05+07:00
- Verdict: INVALID

## Key and hash checks

- Answer key markdown sha256 computed 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60, matches the expected value in the brief.
- Answer key JSON sha256 computed 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, matches the expected value in the brief.
- Snapshot manifest hash field is ef682d715087649fb155b10da1139347d7b98a703ec5d81cdef48dd7b4564c55, matches the expected value in the brief.
- Every file listed in manifest.json was recomputed and matches its listed sha256 and size. Result: 35 of 35 OK, 0 mismatches, 0 missing.

Per-file verification (all OK):

- attempt1-aborted/completion-report.txt - OK
- attempt1-aborted/drive.log - OK
- attempt1-aborted/end_time.txt - OK
- attempt1-aborted/pill-active.png - OK
- attempt1-aborted/pill-gone.png - OK
- attempt1-aborted/rdp-smoke.json - OK
- attempt1-aborted/start_time.txt - OK
- attempt1-aborted/tabs-before.json - OK
- attempt2-aborted/completion-report.txt - OK
- attempt2-aborted/drive.log - OK
- attempt2-aborted/end_time.txt - OK
- attempt2-aborted/pill-gone.png - OK
- attempt2-aborted/rdp-smoke.json - OK
- attempt2-aborted/start_time.txt - OK
- back-action.json - OK
- block-evidence.txt - OK
- click-whois-actions.json - OK
- completion-report.txt - OK
- drive.log - OK
- end_time.txt - OK
- enter-whois-actions.json - OK
- example.com-2026-11-28T103603+0700.jpg - OK
- fix-ddg-query-actions.json - OK
- ket-qua.txt - OK
- pill-gone.png - OK
- rdp-smoke.json - OK
- search-commit-actions.json - OK
- search-example-actions.json - OK
- search-suggestion-actions.json - OK
- search-wikipedia-actions.json - OK
- start_time.txt - OK
- type-example-actions.json - OK
- type-wikipedia-actions.json - OK
- wikipedia.org-block-2026-11-28T103834+0700.jpg - OK
- zoom-out-actions.json - OK

## Key criteria applied

Tier B key for R3-037 requires 2 domains in order, example.com then wikipedia.org. For each domain the runner must record registrar, registration date, expiry date, name servers, and status (valid or expired), with live who.is values at run time. The truth is the WHOIS result screenshots. Evidence is 2 result screenshots plus ket-qua.txt, cross-checked against the screenshots. The task Pass line requires both rows complete with correct registrar, expiry date, name servers, and status, plus 2 screenshots. The Fail line covers missing domain, wrong expiry or registrar, wrong status, missing screenshot, or a different WHOIS site without note. The key also says that if the page shows reCAPTCHA or a human verification request, stop, record it in ket-qua.txt, and the task is invalid under section 1. Section 1 defines an invalid task when the service is inaccessible or shows a bot check or reCAPTCHA, excluded from the denominator. The scorer rule in the brief adds that a service block is INVALID only when it is not caused by runner behavior such as rapid repeat requests, many tabs, or hammering, which count as FAIL.

## Evidence grading

### example.com - complete and correct

Screenshot example.com-2026-11-28T103603+0700.jpg shows the who.is result for example.com: Registrar RESERVED-Internet Assigned Numbers Authority, Created August 14, 1995, Expires August 13, 2027, Name servers elliott.ns.cloudflare.com and hera.ns.cloudflare.com, Domain Status clientDeleteProhibited, clientTransferProhibited, clientUpdateProhibited. File ket-qua.txt row 1 records the same registrar, registration date August 14, 1995, expiry date August 13, 2027, both name servers, and status still valid as of 2026-11-28. Every field matches the screenshot. The status is consistent with an expiry in 2027. This domain alone would pass.

### wikipedia.org - service block, correctly recorded

Screenshot wikipedia.org-block-2026-11-28T103834+0700.jpg shows the who.is page for wikipedia.org with a red notice: Information Blocked, Access to WHOIS information for the domain wikipedia.org has been restricted. No registrar, dates, name servers, or status are shown. File ket-qua.txt row 2 records Registrar unavailable, Registration date unavailable, Expiry date unavailable, Name servers unavailable, Status blocked, INVALID candidate, WHOIS access restricted, and names both evidence screenshots. File block-evidence.txt records the URL https://who.is/whois/wikipedia.org, the page title, the visible block text, no Ray ID, the screenshot name and its sha256 48f0759d5709df422aa5c6dfb3cc3cc02bfed0ca9732d82b85f63c1e1c06181c, and that further requests were stopped. The ket-qua.txt row matches the screenshot. The runner did not invent values and did not switch to another WHOIS site. Because the second domain has no WHOIS fields, the task cannot be PASS under the Tier B key.

### Was the block caused by the runner? No.

Drive log cadence (drive.log, context for timing only, verdict rests on screenshots and ket-qua.txt): the example.com search was submitted around 10:35:05 to 10:35:39 +07:00 and the result was visible at 10:35:39. The wikipedia.org form was submitted at 10:36:54, about 75 seconds later, and the block was observed at 10:37:34. That is one wikipedia.org request, one task tab, normal sequential lookup of the two required domains. There were no repeat submits, no retries after the block, and no parallel tabs hammering who.is. The runner waited 60 seconds, saved the block screenshot at 10:39:23, wrote ket-qua.txt at 10:39:50, and stopped. The two aborted attempts archived in the snapshot made zero who.is queries: attempt1-aborted/drive.log and attempt2-aborted/drive.log both stopped on tab scoping before any domain lookup, so they cannot have triggered a rate limit. The block also hit only wikipedia.org immediately after a successful example.com lookup on the same service, which fits a domain-specific restriction rather than an IP rate limit caused by cadence. On this evidence the block was not caused by runner behavior.

Independent check: a text fetch of https://who.is/whois/wikipedia.org returned a cached copy crawled 2026-11-13 with only the About WHOIS boilerplate and no registrar, dates, or name servers. It did not reproduce the live Information Blocked wording and it is not a live browser result, so it carries limited weight. It does not contradict the block claim, since it also shows no WHOIS fields for wikipedia.org. The verdict rests on the snapshot screenshot, not on this fetch.

### Run window check

start_time.txt contains 2026-11-28T10:29:41+07:00 and end_time.txt contains 2026-11-28T10:44:34+07:00. Content timestamps fall inside that window: the example.com screenshot filename is 10:36:03, the wikipedia.org block screenshot filename is 10:38:34, and drive.log entries run from 10:29:41 to 10:44:34. Filesystem mtimes in the snapshot are copy times from packaging, ranging 10:45:16 to 10:46:33 +07:00, shortly after end_time, so a strict filesystem-mtime-inside-window test fails for every file including start_time.txt itself. That is a snapshot copy artifact. Hashes match the manifest and internal timestamps are consistent, so this does not undermine the evidence.

## Verdict reasoning

PASS is impossible because wikipedia.org has no registrar, expiry date, name servers, or status. FAIL would require a runner error such as wrong values, a missing screenshot, an unrecorded site switch, or a runner-caused block. None is present: both screenshots exist, ket-qua.txt has 2 rows in the required order, the example.com values are correct, the wikipedia.org row honestly records the restriction, and the cadence shows a single normal query with no hammering. The service made the second lookup inaccessible, which is the section 1 invalid case. Verdict: INVALID.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read any other scorer's verdict or contact the runner. Mochi (scorer 1) is resting; I am a substitute independent scorer.
