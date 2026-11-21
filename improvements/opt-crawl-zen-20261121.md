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

## D. Marionette browserElement-null slot (J3, todolist 4.10)

Failing call: POST /session to geckodriver --connect-existing (Marionette port 2828), HTTP 500, `TypeError: can't access property "namespaceURI", browserElement is null`. Observed 22:06, 22:10, 22:12, 22:20, 22:31 (F3 log event table). It blocked cleanup2 (15 tabs left, then 39 resurrected tabs after restart) and every live run after 22:06. Fixed at the symptom level by the Zen restart 22:36 (session created in 0.1s, id dfd532f5-7423-4e11-9171-f35410d0a73e, 67 tabs listed in 7.7s). No root-cause fix has landed; the restart cleared the state, it did not fix the code.

### D1. Null browserElement dereferenced with no null check (PROVEN, source-verbatim)

- File: ~/workspace/zen_tab_cleanup/source/driver.sys.mjs-FIREFOX_160_0_RELEASE (shipped driver extracted from the laptop top-level omni.ja, 160,552 B, 4,794 lines; upstream cross-check FIREFOX_160_0_RELEASE, line numbers identical, per F3 log).
- Line 4608-4623: `#registerBrowser(browserElement)` opens with a comment block, then line 4616 `browserElement.namespaceURI != XUL_NS` dereferences the argument with NO null check. A null input throws exactly the observed TypeError. This is the throw site.
- Line 4634-4645: `#registerWindow(win, {registerBrowsers})` line 4640 passes `TabManager.getBrowserForTab(tab)` unchecked into `#registerBrowser` for every tab in `tabBrowser.tabs`.
- Line 2707: `newSession` loops every window and every tab with `registerBrowsers: true` (`this.#registerWindow(win, { registerBrowsers: true })`). ONE null browser kills the whole session creation. There is no try/catch around the loop and no skip of null browsers.
- Contrast, same file: line 2849 `getBrowserForTab(tab)` result is used at line 3543 `#registerBrowser(contentBrowser)` in a different path, and line 4437-4445 `getBrowserForTab` result feeds `NavigableManager.getIdForBrowser(contentBrowser)` with no null guard either. The null-blind pattern is repeated, but only the newSession path (line 2707) runs at session creation, so only it blocks the slot.
- What a fix must change: driver.sys.mjs is SHIPPED Firefox code, not repo code, so the repo cannot patch it in place. Fix options for councils: (a) guard at OUR call boundary, impossible, the throw is inside newSession before any of our code runs; (b) prevent the null tab from existing at session time, by cleaning up zombie/discarded tabs before POST /session, or by restarting Zen when the slot reports this exact error; (c) avoid newSession entirely for health checks, use BiDi `session.new` + `browsingContext.getTree`, which do NOT call `#registerBrowser` (F3 log: BiDi worked throughout the wedge). (d) Upstream: file or adopt an upstream guard, `if (!browserElement) continue` in `#registerWindow`, but that is outside this repo and cannot be deployed by us. The durable repo-level fix is therefore (b) plus (c): detect this exact 500, classify it as a slot-wedge, and recover by the proven restart path, with the pre-restart zombie-tab cleanup attempted first.

### D2. getBrowserForTab returns null for unloaded / removed tabs (PROVEN by F3 log citation, source file NOT in VM copy)

- F3 log cites `TabManager.sys.mjs` lines 39-41: `getBrowserForTab(tab)` returns `tab?.linkedBrowser ?? null`. `getBrowsers()` excludes unloaded tabs and filters nulls, but `#registerWindow` does NOT use it.
- Evidence gap: TabManager.sys.mjs itself was NOT read by this crawl (not present in the VM copy at ~/workspace/zen_tab_cleanup/source/). The citation rests on F3's log alone. See gap G-01.
- Upstream anchors cited by F3 log: Bug 1366988 (2017, same `be.namespaceURI` access, same error family). Bug 1342723: `removeTab` sets `aTab.linkedBrowser = null`.
- What a fix must change: same as D1. Any repo-side fix must either remove the null-linked tab before newSession, or bypass newSession (BiDi), or restart Zen. There is no repo file that can null-check inside `#registerBrowser`.

### D3. Lazy tabs do NOT cause the null (PROVEN by the restart, F3 corrected theory 22:38)

- F3 log: "lazy tabs do NOT break `#registerBrowser` (their `linkedBrowser` exists; proven by the restart, Marionette works with about 52 lazy tabs present)".
- Supporting datum: after restart, `list_tabs` returned 67 tabs in 7.7s with titles empty (lazy), and POST /session succeeded in 0.1s. The same lazy population that was present during the wedge now works.
- Consequence: any fix that closes or un-lazies tabs to "fix" the slot is misdirected. The null tab is a different population from lazy tabs.

### D4. Prime suspect: a tab mid-removal / browser element destroyed (UNPROVEN)

- F3 log corrected theory (22:38): "The null tab was most likely a tab mid-removal / whose browser element was destroyed (prime suspect, UNPROVEN: the pass-1 cleanup teardown, sacrificial-tab open failed 404 'Browsing context has been discarded', DELETE /session ran while current was a discarded tab). The pre-restart tabbrowser held a zombie tab element with null `linkedBrowser` from about 22:06 through 22:31. The restart rebuilt the tabbrowser fresh and cleared it."
- Supporting chain, each link sourced: pass-1 cleanup deleted 39 fixture tabs and ended with the session DELETE while current was a discarded tab (F3 log + MEMORY.md 22:10 tab-cleanup entry: "DELETE /session khi current la tab da dong se de lai Zen o trang thai tab chet"). The 22:03 to 22:06 change trigger is still unproven (F3 log: "The 22:03 to 22:06 change trigger is still unproven").
- Related datum: F2 log section 2 R5: /tmp/zen_tab_cleanup/out6.log 22:19:52 still contains `browserElement is null` (grep count 2). The 22:17 direct Pointer click did NOT fix the slot.
- What a fix must change: the cleanup teardown in the runner and in scripts/zen_dom.py. (a) Open the sacrificial tab FIRST, before closing any tab (todolist gate G-TAB already states this: "mo tab hy sinh TRUOC khi dong tab; ket thuc session luc dang focus tab song"). (b) End the session while focused on a LIVE tab, never on a discarded one. (c) scripts/zen_dom.py `_cleanup` (lines 144-168) deletes the session but does not verify the current tab is live first; tests/realistic/run_live.py `WD._cleanup` (lines 521-568) switches to each opened tab and DELETEs it, then DELETEs the session, with no live-tab check before the session DELETE. Both need the G-TAB ordering enforced in code, not in prose. (d) Add a pre-session probe: if POST /session returns this exact 500, run the zombie-tab diagnosis (BiDi getTree, list tab elements) before restarting, so the next occurrence leaves evidence instead of only a restart.

### D5. Session-creation failure orphans geckodriver and blocks the slot (PROVEN, fixed in run_live.py, NOT fixed in zen_dom.py)

- tests/realistic/run_live.py `WD.__enter__` lines 461-514: the except block after Popen calls `self._cleanup()` and re-raises, with the comment "Any failure after Popen (PID write, status wait, session POST, malformed session response) must clean up: without this the geckodriver is orphaned (__exit__ never runs) and blocks the session slot for later runners." The geckodriver log goes to a file in APPEND mode, not DEVNULL, and the PID is recorded at /tmp/geckodriver-{WD_PORT}.pid (lines 465-471) so preflight can sweep verified orphans by PID.
- scripts/zen_dom.py `ZenSession.__enter__` lines 87-118: on POST /session failure it calls `self._cleanup()` and raises, which DOES terminate geckodriver. BUT the geckodriver is started with stdout/stderr to DEVNULL (lines 101-105), so a failed session leaves NO geckodriver log, and NO PID file is written. The orphan risk here is lower than run_live.py, but the evidence loss is total: a failed zen_dom.py session cannot be diagnosed from any log.
- Contrast: run_live.py `WD._wd` lines 570-581 raises RuntimeError with the HTTP body (first 300 chars), so the 500 text reaches the runner log. zen_dom.py `_wd` lines 170-183 raises ZenDomError with the body (first 400 chars). Both preserve the error text; only run_live.py preserves the geckodriver log and PID.
- What a fix must change: scripts/zen_dom.py: (a) geckodriver log to a file in append mode, same as run_live.py lines 463-471; (b) write a PID file so preflight can sweep orphans; (c) keep the __enter__ cleanup on POST failure, already present. This is a small, mechanical fix, and it is the only D-class fix that lives in repo code rather than in procedure.

### D6. Single-session slot: BiDi and Marionette share one slot, a leak blocks ALL remote control (PROVEN, zen_dom.py docstring + code)

- scripts/zen_dom.py lines 1-13: "Owns the ONE remote session a Zen instance allows (BiDi and Marionette share a single session slot; a leaked session blocks ALL remote control until Zen restarts, see docs/zen-dom-control-comparison.md section 7)." Rules enforced: one session at a time across all processes (file lock), session ALWAYS deleted in a finally block, geckodriver started per session and terminated with it.
- Enforcement: `ZenSession.__enter__` lines 88-98 takes an exclusive non-blocking flock on ~/.cache/agent-computer-use/zen_dom.lock (LOCK_PATH lines 44-47) and raises ZenDomError if another process holds it. `__exit__` lines 135-138 calls `_cleanup`.
- Gap in the lock: the flock is per-process and non-blocking, but run_live.py WD does NOT take the zen_dom.lock at all. It uses only its own PID file (/tmp/geckodriver-{WD_PORT}.pid) and port-keyed paths. Two runners (zen_dom.py-based and run_live.py-based) can therefore race for the single slot with no shared lock. The preflight single-session lock check in run_agyq2.py (line 1323 docstring: "single-session lock check (zen_dom.lock must show an exclusive flock held by an ancestor of this process)") assumes the lock exists, but run_live.py never creates it. See gap G-02 and class G.
- What a fix must change: (a) run_live.py WD must take the same zen_dom.lock (same path, same flock semantics) before starting geckodriver; (b) the preflight lock check must fail closed when no lock holder is found, not pass on a missing file; (c) document the lock path in one place, not two.
