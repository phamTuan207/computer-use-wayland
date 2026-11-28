# Pick 4 measurement, combined summary (PROVISIONAL, non-Astra)

- Owner: the repository owner. Repo: ~/computer-use-wayland, branch speed-swarm, HEAD c1b7034b452b24358206009c40bbf450d575da58 (briefs said 5d4d512; actual HEAD is c1b7034, branch behind 9, 4 files pre-modified, untouched).
- Relay: serving c1b7034, generation ff23539371b76bbe9e993d380d322a94. Shared drop-in speed-swarm.conf carries CU_CODE_EXEC=1 and CU_PICK4_FASTPATH=1. No drop-in created, no relay restart, no git touch, no Track 1 restore (coordinator overrides honored).
- Window: 2026-11-19 00:35 to 02:39 Asia/Ho_Chi_Minh. Prior-art survey read first (improvements/speed-prior-art.md): baseline anchor is think 34.2s of 36.4s wall (94 percent), so only model-think cuts can move the total; grounding aids only win if the model skips its own vision re-grounding.
- Run-1 arm1 files preserved in /tmp/speed-pick4-20261118/run1-blocked/.

## 1. Probe (scripted, flag ON, 00:35:18-00:35:28, about 10s wall)

Direct cu.py calls, not broker. Plus two supplements (00:37:47-00:39:09).

- Nautilus, flag ON: a11y observe returns 3 elements, all with extents, extents_coord screen. Query name Home matched 1, returned 1. Query role push button matched 0.
- Nautilus, flag OFF (supplement 2): observe returns 3 elements, 0 extents. Query name Home matched none. Extents are correctly gated by the flag.
- a11y ground (direct cu.py, twice): FAILS both times with "cannot tell whether extents are screen or window relative; use vision", even though observe returns extents_coord screen. Ground never returns a box or center.
- kitty, omacalc, omawrite, Zen: a11y observe fails with "exact app PID required; use a11y apps". That is a probe PID-lookup artifact (hyprctl window PID is not the AT-SPI app PID), not a verdict on those apps. a11y apps lists only 6 registered apps.
- No per-call latencies: the probe script records none, and the supplement timing was lost (bc missing on the laptop). All a11y calls complete in well under a second each; the whole supplement (4 calls plus a Nautilus launch) took under 4s. Latency is not the story here; availability is.
- Probe cleanup verified: no pick4-probe-term window remains. Desktop after probe: Jarvis, foot, Zen only.
- Browser snapshot latencies were not probed by the script (it has no browser section); D1 below covers the browser path live instead.

## 2. Arm 1 baseline (flag OFF in executor shell)

### Run 1: 0/4, all BLOCKED (00:51-01:09)

- P1 session started, then died: observe returned driver error "window no longer exists", windows retry rejected "task_stopped". Restart 1 and 2 failed (83 status polls, ok:false, state null).
- P2, P3, P4: one start attempt each, all failed the same way (83 polls, ok:false). Cause: Pick 1 and Pick 2 workers held the single-owner broker through the whole window (owners speed-base-p3, speed-pick1-smoke, pick2-p1, pick2-p2, pick2-p4 seen). The run-1 executor recorded BLOCKED after one failed start per task instead of retrying.
- Evidence preserved: run1-blocked/summary-arm1.md, records-arm1.jsonl, arm1-codex.log, decisions/sleeps logs.

### Run 2: 4/4 SUCCESS (01:36-02:07), the valid baseline

Task-start (session start submit) to verified end state, Asia/Ho_Chi_Minh.

| Task | Wall s | Service s | Gap (think) s | Result and evidence |
|---|---:|---:|---:|---|
| P1 C-03 | 281.494 | 1.503 | 320.646 | SUCCESS, free space 19G. Inflated: first kitty launch failed, windows-retry think 110.7s, first act stale-refused (observation older than 90s), retry ok. |
| P2 E-04 | 43.609 | 1.095 | 60.617 | SUCCESS, 96.0. Clean. |
| P3 B-01 | 43.857 | 1.914 | 472.755 | SUCCESS, all 4 dirs. Gap total includes a failed first start (broker held by pick2-p1), 120s logged wait, and a restart1 lifecycle after finish/status returned invalid_lease. Clean task portion is 43.857s. |
| P4 A-01 | 312.513 | 7.099 | 354.924 | SUCCESS, BYTE-EXACT True. Inflated: extra od-verify and byte-check acts (think 112.7s before od-verify, 69.7s before byte-check), 5 observes. |
| Mean | 170.368 | 2.903 | 302.236 | Sum task-start to verified 681.473s. Analyzer grand totals: service 11.611s, gap 1208.942s. |
| Clean pair P2+P3 mean | 43.733 | | | The robust center; P1 and P4 are inflated by incidentals, not by the loop. |

Notes: 6 windows, 12 observes, 8 act requests, 98 status polls (89 on P3). 2 act requests stale with completed 0. Teardown: Hyprland close ok, immediate check still saw the test client, force-killed PID 732724, final check 0 test windows. Shell flag check: CU_PICK4_FASTPATH unset, CU_CODE_EXEC unset, 0 pick flags.

## 3. Arm 2 fast path (flag ON, CU_PICK4_FASTPATH=1 only)

P1-P4 4/4 SUCCESS, G1 BLOCKED, D1 SUCCESS. 02:09-02:36.

| Task | Wall s | Service s | Gap (think) s | Result and evidence |
|---|---:|---:|---:|---|
| P1 C-03 | 114.219 | 0.887 | 113.307 | SUCCESS, 19G. 1 windows (retry after a missing envelope file), 1 observe, 1 act. |
| P2 E-04 | 42.323 | 0.931 | 41.424 | SUCCESS, 96.0. 1 observe, 1 act. No windows request (address reused). |
| P3 B-01 | 41.164 | 1.098 | 40.038 | SUCCESS, all 4 dirs. 1 observe, 1 act. |
| P4 A-01 | 121.943 | 1.400 | 120.494 | SUCCESS, exact 3 lines (visual check; Tesseract eng drops diacritics). 1 observe, 1 act. |
| Mean P1-P4 | 79.912 | 1.079 | 78.816 | Sum 319.649s. Analyzer grand totals (all 6 tasks): service 8.011s, gap 886.347s. |
| Clean pair P2+P3 mean | 41.744 | | | |

### G1 Nautilus grounding: BLOCKED, 281.253s (02:18:31-02:23:12)

- a11y query --pid 764773 --name Home through the broker returns request_error: unsupported_command. Retry after a fresh Nautilus observe returns the same error. a11y observe refresh also returns unsupported_command. One later observe refused with sequence_gap.
- Counts: a11y calls 3, all refused; ground calls 0; crop observes 0; full-window observes 2 accepted, none used for grounding; vision turns for grounding 0; fallbacks 0; no Home click occurred.
- The broker does not implement a11y commands at all. Separately, direct cu.py a11y ground fails on the coord-frame check (see probe). Both layers block the G1 fast path.

### D1 Chromium DOM-first: SUCCESS, 293.401s (02:24:50-02:29:44)

- Browser requests: 4 (start, tabs, DOM observe, DOM act). Browser observes with image: 0. Browser observes without image: 1. Browser acts: 1. Asserts: 1.
- DOM observe confirmed URL file:///tmp/speed-pick4-20261118/pick4-fixture.html and ref e2 as the "Show result" button. Browser act clicked e2 by ref. Assert #result contains pick4-ok returned ok true, completed 2.
- Screenshots: 2 desktop images, both needed to confirm the right window and focus before the desktop act on the address bar and before Alt+F4 close. The browser observe and browser act took no image.
- Think splits: browser-start 5.9s, windows 16.4s, tabs 6.9s, desktop-observe 7.8s, navigate-act 21.5s, browser-observe 7.5s, browser-act 13.2s, close-observe 45.8s, close-act 14.7s, windows-after-close 11.2s, finish 139.2s. Core DOM loop (observe plus act) is about 21s of think. The 139.2s finish think is executor overhead, not Pick 4.
- Teardown: Alt+F4 closed managed Chromium (PID 767756 gone), terminal and Nautilus closed via Hyprland object-form close, final hyprctl check test_windows_remaining 0.

## 4. Before/after

| Task | Arm1 wall s | Arm2 wall s | Delta s | Delta percent |
|---|---:|---:|---:|---:|
| P1 | 281.494 | 114.219 | -167.275 | -59 percent |
| P2 | 43.609 | 42.323 | -1.286 | -3 percent |
| P3 | 43.857 | 41.164 | -2.693 | -6 percent |
| P4 | 312.513 | 121.943 | -190.570 | -61 percent |
| Mean | 170.368 | 79.912 | -90.456 | -53 percent |
| Clean pair P2+P3 mean | 43.733 | 41.744 | -1.989 | -5 percent |

- Think-time saved: about 2s on the clean pair (P2+P3), which is the only honest comparison. The raw mean delta of 90.5s is incidental executor variance: arm1 P1 had a stale-act retry and a 110.7s windows-retry think; arm1 P4 did extra byte-verification rounds; arm2 P1/P4 did the minimal 1 observe plus 1 act. Pick 4 does not apply to these terminal screenshot tasks, exactly as predicted, and the numbers confirm no systematic change.
- G1: no before/after possible; the a11y path never reached the model through the broker.
- D1: no arm1 baseline exists (D1 is arm2-only), so no before/after. It proves DOM-first works with 0 browser screenshots; it does not prove a think-time saving.

## 5. Verdict: CONDITIONAL (PROVISIONAL, non-Astra)

- Terminal tasks: no change, as predicted. Pick 4 is not a terminal-task win.
- G1 a11y half: BLOCKED at two layers. The broker rejects a11y commands (unsupported_command), and direct a11y ground fails its coord-frame check despite extents_coord screen in the observe output. Landable only after broker a11y support plus a ground fix.
- D1 DOM half: WORKS. DOM snapshot carries rects/centers, click by ref plus DOM assert succeeds with 0 browser screenshots. Feasibility proven, speedup unproven (no baseline, wall dominated by executor think overhead).
- Overall: do not land Pick 4 as a think-time win on this evidence. Land the DOM-first browser path as a capability only if a baseline browser task is measured first; hold the a11y half until the broker and ground are fixed.

## 6. Blockers, cuts, and notes

- Blocker 1: single-owner broker shared by three parallel workers. Arm1 run 1 went 0/4 on contention; Pick 1 also lost its P4 to 11 refused starts; Pick 2 lost its arm-2 P3 to a BLOCKED-dirty stop and its P4 session failed with driver_command_failed. Reran arm1 once after Pick 1 and Pick 2 finished, with broker idle; run 2 went 4/4.
- Blocker 2: broker has no a11y command support (G1). Blocker 3: a11y ground coord-frame bug (probe).
- Cuts (standing order 4): cut the probe to presence plus correctness (no per-call latency harness, since all a11y calls are sub-second and latency is not the story); cut redundant status polling to the brief minimum; did not re-run arm1 a third time; did not chase Pick 2 leftover pick2-term window (another worker's window, left alone). Arm1 baseline was NOT cut (control kept intact); arm2 cut aggressively on P2-P4 (1 observe plus 1 act each).
- Desktop verified clean at 02:39 by this worker: Jarvis, foot, Zen only. Broker idle (finished pick4-fp-d1, stopped, cancelled false). /tmp/y-tuong.txt remains as the P4 end-state artifact; /tmp/hoc-ky-2 is gone.
- Files: probe log /tmp/speed-pick4-20261118/probe/probe.log; supplements probe/supplement.log, probe/supplement2.log; arm1 run-2 summary /tmp/speed-pick4-20261118/summary-arm1.md; arm1 run-1 evidence /tmp/speed-pick4-20261118/run1-blocked/; arm2 summary /tmp/speed-pick4-20261118/summary-arm2.md; this file /tmp/speed-pick4-20261118/summary-pick4.md.
