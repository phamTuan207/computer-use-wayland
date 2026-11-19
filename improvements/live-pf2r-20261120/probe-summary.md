# ADOPTION PROBE - page prefetch root cause, proven live (harness-prefetch ac3882b)

Coordinator-run, zero model calls. Session pf2r-probe-adopt, generation
921ef558fb30dfd51bd0bddccc015762, wall 2026-11-20 05:28:55-05:29:17 +07.
Driver: run-adopt-probe.sh, log: /tmp/live-pf2r-20261120/pf2r-adopt-probe/probe-driver.log.
Relay env CU_PRECAPTURE=0, started_git_head ac3882b.

## Question
The method arm prefetched ok:true (tab 6691BF08...) but open returned prefetched:false
with a fresh tab (86350AA5...), 3.205s after the prefetch, inside the 30s TTL, no error.
Why did open not adopt the prefetched tab?

## Code hypothesis (read before probing)
scripts/chromium_cli.py, ac3882b, `_prefetched_target` (line 714): adoption requires
`target.get("url") == record["url"]` AND `state["url"] == record["url"]` AND
`ready == "complete"`. `validate_url` returns the raw string unchanged, so the record URL
is "https://example.com" (no trailing slash). Chromium reports the loaded tab URL and
`location.href` as "https://example.com/" (with trailing slash). The string comparison
fails deterministically before the ready check is ever reached.

## Results
- Test A (replication, no slash, 3s sleep): prefetch ok:true, tab
  9884E6155426FBFA70B8FB611E382985. Tabs listed immediately after the prefetch show that
  tab with url "https://example.com/" and title "Example Domain" (page already loaded).
  Open: prefetched:false, fresh tab FE7D4D3E93CF22BFB67ED6E05AADDB2C, load_ms 55.363.
  Replicates the method arm exactly.
- Test B (trailing slash, 3s sleep): prefetch https://example.com/ ok:true, tab
  7BA0263640DED4A190CFAFCFB4CD5D09. Open https://example.com/: prefetched:TRUE, tab
  7BA0263640DED4A190CFAFCFB4CD5D09, THE SAME TAB ID, load_ms 13.512. ADOPTION CONFIRMED.
  The only difference from test A is the trailing slash.
- Test C (control, no slash, 12s sleep): prefetch ok:true, tab
  481DE5E10E3D417A0614FADD1BE260E7. Open after 12s: prefetched:false, fresh tab
  B2D31797E25A2892918FFC246AFF0387, load_ms 52.591. Still no adoption after 12 seconds:
  the readyState hypothesis is RULED OUT.

## Conclusion
Root cause PROVEN: the adoption gate compares raw URL strings and fails whenever
Chromium normalizes the URL (bare domain gains a trailing slash). It is not a timing
issue. Adoption load_ms 13.512 vs fresh-load 55.363 / 52.591: adoption saves ~40ms of
navigation time on this tiny page. Fix needed: normalize URLs before comparing in
`_prefetched_target` (and in the record lookup in `cmd_open`), e.g. default an empty
path to "/". Workaround until fixed: pass the URL in its normalized form.

## Teardown
All opened tabs closed (the two already-closed prefetched tabs returned 404 as expected,
cmd_open closes a failed-adoption target itself). Finish ok, driver stopped, guardian
clean, chromium windows remaining 0.
