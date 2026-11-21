# OPT-ZEN evidence base: Marionette / Zen / workspace / pill / hidden-body

- Crawler: OPT-ZEN (Muse source crawler for Worker OPT). Evidence base ONLY. No final method here; councils write that.
- Date: 2026-11-21, crawl 22:49-23:00 +07. Repo: ~/workspace/computer-use-wayland, branch todolist-push.
- Method: read end to end the listed code paths and logs, cite file:line for every claim. Generator rule: read and cite only, no live tests, no laptop driving, no session starts, no mouse clicks, no ydotool. Read-only laptop reads allowed; none were needed, all sources below are VM repo copies unless marked laptop.
- Commit discipline (owner rule 22:49, relayed 22:53): every small step is its OWN commit, pushed immediately, never batched. One file section = one commit. Each push verified via git ls-remote. Graph note (MEMORY.md 22:49-22:51 correction): the GitHub graph counts the UTC day on the default branch (main) only, so todolist-push commits do not move the graph cell; Worker MERGE merges todolist-push into main for the graph count. The per-section commit discipline still applies here as method, and feeds the method file COMMIT METHOD section.
- No em/en dashes in this file. Commas, periods, or short hyphens only.

## 0. Scope and sources read in full

- scripts/zen_dom.py (249 lines, read in full)
- tests/realistic/run_live.py (1802 lines: diagnose + WD sections read in full at lines 199-404, 461-690; function map grepped for the rest)
- tests/realistic/run_agyq2.py (ensure_visible lines 351-470, bootstrap_tab + preflight lines 1282-1400+)
- tests/realistic/run_codex_y5.py (preflight lines 3652-3700, ensure_visible line 1161, bootstrap_tab line 3480)
- improvements/worker-y4b-hidden-body-root-cause.md (114 lines, read in full)
- improvements/worker-y6r-rereview-log.md (195 lines, read in full)
- improvements/worker-y6e-rebuild-load-log.md (588 lines, read in full)
- improvements/zen-ordinary-user-tests-20261121.md (658 lines: purpose, rules, tools, findings F-001/F-002, ZT-00, ZT-01, ZT-05 read in full; ZT-02/03/04/06/07/08/09/10 by section headers + spot reads)
- improvements/worker-y13r-rereview-log.md (77 lines, read in full)
- improvements/worker-y13r2-rereview-log.md (read in full, head + tail)
- improvements/worker-f2-silence-fix-log.md (403 lines: sections 1-3 + tail read in full)
- improvements/worker-f3-marionette-slot-log.md (read in full)
- improvements/worker-f1-guardian-fix-log.md (head + tail; root-cause section grepped)
- ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md (section 12 J1-J6 + section 13 J7-J21, read in full)
- docs/zen-error-fix-todolist-20261121.md (roadmap lines 11-18, gates line 33, decisions line 34, 2.2.3 line 74, 4.7-4.14 lines 188-195, 4.17 line 198, 4.28 line 209)
- improvements/worker-y6b-run-nested-wayland-v2.sh (v3 runner: ldd pre-flight lines 153-162, U6 lines 298-305)
- scripts/indicator.py (liquid gate lines 195-260)
- ~/workspace/zen_tab_cleanup/source/driver.sys.mjs-FIREFOX_160_0_RELEASE (160,552 B, 4,794 lines: lines 384, 2700-2712, 2845-2855, 3538-3548, 4433-4445, 4608-4650 read verbatim)

## 0.1 Premise corrections (task brief vs record at crawl time)

- P1. Task brief says F3 has NO log file yet. WRONG at crawl time. improvements/worker-f3-marionette-slot-log.md exists and is committed (8a5b18a, "F3: live event log, Marionette root cause + restore + 22:43 click-miss"). F3's log is the primary source for class D and E below.
- P2. Task brief lists "Y13r2 main log missing" as an example evidence gap. WRONG as stated. improvements/worker-y13r2-rereview-log.md EXISTS, but it is IN PROGRESS at last write: redteam still running, final verdict PENDING, synthesis not yet written (section 6 "Pending"). The gap is not absence, it is incompleteness. See gap G-04.
- P3. Task brief says F3 restarted Zen 22:36, new PID 426338, 67 tabs. CONFIRMED by F3 log lines 22:36:24-22:38:32 and by F2 log 22:44 (zen_dom.py list returned 67 tabs). Update from MEMORY.md 22:49-22:51: the restart RESURRECTED 39 fixture tabs (sessionstore 22:04 predates the pass-1 cleanup), and F3 is re-running the FULL cleanup with the same keep-list (28 real tabs). The cleanup scope is therefore 39 resurrected tabs, not the 15 tabs of cleanup2.
- P4. Task brief says Y13r2 main log missing and F3 log missing. Both corrected above. No other brief premise was falsified by the read.
- P5. Task brief says "Y6r AMEND A1-A10 (profile WAS applied via config() parse 2, no manual reload, y6e conf never staged as active conf, retry dies at ldd pre-flight)". CONFIRMED by worker-y6r-rereview-log.md adjudication R1/R2/R4 and fix list A1-A10.
- P6. Task brief says "ZT-A scenarios done (658 lines, 10 composite blind scenarios ZT-01..ZT-10 + ZT-00 health gate)". CONFIRMED by zen-ordinary-user-tests-20261121.md line count 658 and section headers. ZT-B has NOT run them yet (no ZT-B report file found in improvements/ at crawl time). See gap G-07.
