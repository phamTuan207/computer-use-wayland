# R3-037 rerun grade, scorer A

- Task: R3-037 (Tier B), WHOIS lookup of 2 domains on who.is
- Rerun: yes (R3-L3 rerun snapshot)
- Runner: Codex (session 01a22033-5509-7530-991d-b41adea7467f), per brief; not contacted
- Scorer: scorerA (substitute independent, Mochi resting)
- Scorer session ID cf20647f-e904-4f95-87cd-efc06ab15fe7
- Scored at: 2026-11-28T10:48:09+07:00
- Verdict: INVALID

## Independence declaration

I graded independently from the snapshot and key section only; I did not read any other scorer's verdict or contact the runner. Mochi (scorer 1) is resting; I am a substitute independent scorer.

I did not read R3-L3-grades.jsonl, R3-L3-reruns.jsonl, the original snapshot rung3-snapshots/R3-037-L3/, any verdict files, or any coordinator state. I did not run the task and did not write the task or key.

## Key verification

- docs/rung3-answer-keys.md sha256 computed: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60. Matches the brief value.
- docs/rung3-answer-keys.json sha256 computed: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8. Matches the brief value.
- Key section used: "## R3-037 (Tier B)" in the md file; json tiers["R3-037"] = "B", allocated["R3-037"] domains = [example.com, wikipedia.org].
- Task text used: R3-037 section in docs/rung3-list-100-tasks.md, plus the section 1 invalid definition.

Tier B criteria applied: 2 domains in order (1. example.com, 2. wikipedia.org); per domain record registrar, registration date, expiry date, name servers, status (valid or expired); values live at run time on who.is; ground truth is the WHOIS result screenshots; scoring evidence is 2 result screenshots plus ket-qua.txt, cross-checked against the screenshots. Task Pass needs both rows correct with 2 screenshots; Fail includes missing domain, wrong registrar or expiry, wrong status, missing screenshot, or an undeclared different WHOIS site.

## Snapshot hash verification

Snapshot: rung3-run-log/rung3-snapshots/R3-037-L3-rerun/

- manifest.json declared manifest_sha256: ef682d715087649fb155b10da1139347d7b98a703ec5d81cdef48dd7b4564c55. Matches the brief value.
- manifest.json file sha256 (for transparency): 4b3e18cab8c352f2c3979a391803b30a33394d4fa36dd54d0fce41f6131459ff. The manifest_hash recorded in scorerA.json is the declared manifest_sha256 value, as instructed.
- Per-file verification: all 35 files listed in manifest.json recomputed and matched their recorded sha256. Zero mismatches. Files verified: attempt1-aborted/completion-report.txt, attempt1-aborted/drive.log, attempt1-aborted/end_time.txt, attempt1-aborted/pill-active.png, attempt1-aborted/pill-gone.png, attempt1-aborted/rdp-smoke.json, attempt1-aborted/start_time.txt, attempt1-aborted/tabs-before.json, attempt2-aborted/completion-report.txt, attempt2-aborted/drive.log, attempt2-aborted/end_time.txt, attempt2-aborted/pill-gone.png, attempt2-aborted/rdp-smoke.json, attempt2-aborted/start_time.txt, back-action.json, block-evidence.txt, click-whois-actions.json, completion-report.txt, drive.log, end_time.txt, enter-whois-actions.json, example.com-2026-11-28T103603+0700.jpg, fix-ddg-query-actions.json, ket-qua.txt, pill-gone.png, rdp-smoke.json, search-commit-actions.json, search-example-actions.json, search-suggestion-actions.json, search-wikipedia-actions.json, start_time.txt, type-example-actions.json, type-wikipedia-actions.json, wikipedia.org-block-2026-11-28T103834+0700.jpg, zoom-out-actions.json.

## Run window and timestamps

- start_time.txt: 2026-11-28T10:29:41+07:00
- end_time.txt: 2026-11-28T10:44:34+07:00
- Manifest mtimes: all 35 files fall between 2026-11-28T10:45:16+07:00 and 2026-11-28T10:46:33+07:00, which is after end_time.txt. They cluster within about 77 seconds, including start_time.txt itself (mtime 10:45:54, content 10:29:41), so these mtimes are snapshot copy times, not original creation times. Recorded honestly: on a literal mtime-versus-window check, no file falls inside the window, but this is a packaging artifact affecting every file equally, and all content hashes verify.
- Embedded evidence timestamps do fall inside the window: example.com screenshot filename 2026-11-28T103603+0700, wikipedia.org block screenshot filename 2026-11-28T103834+0700, and drive.log internal entries span 10:29:41 to 10:44:34 +07:00. The Tier B key makes the screenshots the ground truth and does not list file mtime as a pass criterion, so this artifact does not change the verdict. Flagged here for the coordinator.

## Evidence judged (screenshots and ket-qua.txt)

Judged from the screenshots and ket-qua.txt. drive.log and completion-report.txt were treated as runner self-report context only, except drive.log timestamps used for the block-causation question as instructed.

- example.com-2026-11-28T103603+0700.jpg shows who.is result: Registrar RESERVED-Internet Assigned Numbers Authority; Created August 14, 1995; Expires August 13, 2027; Nameservers elliott.ns.cloudflare.com and hera.ns.cloudflare.com; Domain Status clientDeleteProhibited, clientTransferProhibited, clientUpdateProhibited.
- ket-qua.txt row 1 (example.com) records the same registrar, registration date August 14, 1995, expiry August 13, 2027, both name servers, and status still valid as of 2026-11-28. Fully consistent with the screenshot and correct in key order (first domain).
- wikipedia.org-block-2026-11-28T103834+0700.jpg shows who.is page for wikipedia.org with banner: Information Blocked. Access to WHOIS information for the domain wikipedia.org has been restricted. No registrar, dates, name servers, or status are shown.
- ket-qua.txt row 2 (wikipedia.org) records registrar, dates, and name servers as unavailable and status blocked, INVALID candidate. block-evidence.txt records the same URL (https://who.is/whois/wikipedia.org), page title, visible text, no Ray ID, and the screenshot hash 48f0759d5709df422aa5c6dfb3cc3cc02bfed0ca9732d82b85f63c1e1c06181c, which matches the manifest entry.
- ket-qua.txt has the required 2 rows. The runner used who.is, not an undeclared substitute site. Order matches the key.

So the first domain is complete and correct; the second domain has no obtainable WHOIS fields because the service withheld them. PASS is therefore impossible. The question is FAIL versus INVALID.

## INVALID assessment (was the block caused by the runner)

Section 1 invalid definition: if the service changes interface, closes, is inaccessible, or shows a bot-check or reCAPTCHA page, the scorer records the task invalid, not counted in the sample. Task step 1 likewise: on reCAPTCHA or human verification, stop, record in the result file, task invalid per section 1. Per the brief's scorer rule, a service block counts as INVALID only when not caused by runner behavior (rapid repeat requests, many tabs, hammering count as FAIL).

Request cadence from drive.log timestamps (context for causation only):
- 10:35:05 example.com search submitted (one earlier click attempt at 10:34:53 was refused before input, so no request landed); result visible 10:35:39; screenshot saved 10:36:27.
- 10:36:54 wikipedia.org entered in the visible who.is form and Search clicked; block observed 10:37:34.
- Total WHOIS queries in the run: 2, exactly the task minimum, about 2 minutes apart, in one own task tab. After the block the runner made no further requests, waited 60 seconds, saved the block screenshot at 10:39:23, and stopped.

That is normal user behavior for this task, not rapid repeats, many tabs, or hammering. The block text is domain-specific (restricted for wikipedia.org), not a generic rate-limit or CAPTCHA page.

Independent fetch check by this scorer (text fetch via browser.open; crawler copies, so weighed accordingly, a text fetch may differ from the live browser result):
- https://who.is/whois/wikipedia.org (crawled 2026-11-13): returns only the generic About WHOIS boilerplate. No registrar, dates, name servers, or status. The exact Information Blocked banner text does not appear in the text copy, but no usable WHOIS data is served either.
- https://who.is/whois/example.com (crawled 2026-11-24): returns full WHOIS data identical to the runner screenshot (same registrar, created August 14, 1995, expires August 13, 2027, same two name servers, same statuses).

The asymmetry supports a who.is restriction specific to wikipedia.org, reproducible without any runner involvement, rather than throttling caused by this run. The runner recorded the block in ket-qua.txt and block-evidence.txt with a timestamped screenshot and stopped, as the task requires.

Conclusion: the block was not caused by the runner. Under section 1 the task is INVALID (service inaccessible for the second domain), not FAIL.

## Verdict

INVALID. example.com is fully correct against its screenshot, but who.is restricts WHOIS access for wikipedia.org; the runner made only the 2 required queries at normal cadence, stopped after the block, and documented it with a screenshot, so the failure to obtain the second domain is a service restriction outside runner control.
