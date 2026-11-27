# Worker J work log - post-reboot remaining items - 21/11/2026

All times Asia/Ho_Chi_Minh, wall-clock + elapsed.

## 15:21 - Start, laptop state after reboot
- Zen PID 11292, started 15:19, flags --remote-debugging-port=9222 --marionette present. Fresh process, old BiDi leak gone.
- Port 9222 responds (httpd.js page). Relay session_remote.py serve PID 1821 running since 15:17 (direct process, systemd unit inactive).
- .desktop verified: zen.desktop Exec lines all carry --remote-debugging-port=9222 --marionette. Live proof: Zen launched with flags after reboot. Item 1.3.3 VERIFIED.
- Installed copy ~/.local/share/agent-computer-use/scripts/ has NO overlay.py, NO zen_dom.py. Deploy needed (2.2.6).
- Laptop repo HEAD 3eebe66, behind VM todolist-push 2555fbb. Uncommitted changes present (Worker A2 + G work: indicator.c, indicator_state.h, calibration-grid.html, e2 scripts, redteam docs, fix-run log). Must commit + sync before merge.

## 15:24-15:26 - Item 1.1.1 Puppeteer BiDi click re-test (post-reboot, live Zen)
- Run 1 (15:24): connect 121ms, 5 tabs, new_tab 85ms, goto 92ms, read_dom 21ms (counter 0). v1 page.click: counter STILL 0 (112ms) FAIL. v2 evaluate el.click(): counter 1 (7ms) WORKS. v3 failed with my script bug (createCDPSession does not exist in BiDi mode).
- Run 2 (15:25, v3 fixed to page.mouse.click): connect 54ms, 6 tabs, new_tab 48ms, goto 73ms, read_dom 28ms. v1 page.click: counter 0 (81ms) FAIL again. v2 evaluate: counter 1 (12ms) WORKS. v3 page.mouse.click at rect center (45.6, 124.8): counter stayed 1 (8ms), did NOT increment to 2, FAIL.
- CONCLUSION 1.1.1: reboot did NOT fix Puppeteer BiDi click. Pointer clicks via BiDi (page.click AND page.mouse.click) do NOT trigger the button handler on live Zen. JS evaluate el.click() works (7-12ms). Root cause unknown (possibly unfocused tab/window, or BiDi pointer events not dispatching trusted clicks). Fix direction confirmed: DOM locate + OS-level real mouse click (hybrid), or JS click where hover is not needed. Item 1.1.1 DONE.
- Cleanup note: test leaves one extra about:blank tab (Zen respawns a blank tab when a BiDi-opened tab is closed; closing via BiDi did not reduce the count from 6). Harmless, user can close it. No other user tabs touched. Overlay acquired/released around each run, pill showed "Worker J via BiDi".
- Lesson: tests/puppeteer_bidi.mjs navigates pages[0] (the user's first tab). NEVER run it against live Zen. Use tests/bidi_click_retest.mjs (new tab) instead.

## 15:26-15:28 - Item 1.1.2 firefox-mcp live test (connect-existing, live Zen)
- Install: npm install @mozilla/firefox-mcp@0.11.0 in /tmp/firefox-mcp-test, 3.37s, version 0.11.0 confirmed. Marionette port 2828 LISTENING on the live Zen.
- Run 1 (full procedure): initialize 100ms, tools/list 36 tools (basic preset; list_console_messages NOT in basic, needs developer preset). list_pages 1594ms (3 pages). new_page 105ms (fixture, page [2]). take_snapshot 15ms, button uid=e3 found. click_by_uid 59ms ("click e3"). Counter verification via snapshot regex FAILED (my regex, not the click). fill_by_uid 38ms. evaluate_script 6ms returned "mcp-test" (fill VERIFIED). screenshot_page error: saveTo outside allowed location (needs --unrestricted-save-paths, my test bug). close_page error: pageIdx required (my test bug). close_firefox_session 6ms. Total 1973ms.
- Run 2 (focused click verification): counter_before "0" (11ms). click_by_uid 33ms. counter_after_click "1" (3ms) VERIFIED. screenshot 22ms, 16.6KB saved. close_page 56ms ("closed [2]"). Total 417ms.
- CONCLUSION 1.1.2: firefox-mcp WORKS on live Zen via connect-existing. Its click_by_uid DOES trigger the button handler, unlike Puppeteer BiDi page.click. Likely difference: Selenium/Marionette element click vs BiDi input.performActions. firefox-mcp is a viable driver: maintained by Mozilla, click works, timings 3-154ms per call. Item 1.1.2 DONE.

## 15:28 - Item 1.1.3 Selenium on live Zen
- Fixture /tmp/zen_selenium_fixture.html was wiped by reboot, restored from tests/fixtures/zen_selenium_fixture.html. geckodriver 0.37.1 present.
- FULL PASS, 11/11 steps, total 0.278s: start 5.5ms, create_session 2.8ms (browser firefox 1.24.2b), maximize 0.8ms (1863x1176 REAL viewport, not 0x0), list_tabs 0.7ms (29 handles), open_new_tab 122.5ms, read_dom 30.9ms (16 elements), type 21.2ms (verified read-back), click 63.4ms (output "clicked:zen marionette test" VERIFIED), close_new_tab 25.4ms (29 handles after), delete_session 2.8ms, browser alive 0.3ms.
- CONCLUSION 1.1.3: Selenium WORKS FULLY on live Zen. The 0x0 viewport issue only affected Marionette-opened temp Zen windows, not the live Zen. Click works via Marionette element click. Item 1.1.3 DONE.
- Phase 1 re-test summary: Puppeteer BiDi pointer click FAILS (JS click works), firefox-mcp WORKS (click verified, 3-154ms/call), Selenium WORKS (11/11, 0.278s). Primary driver stays zen-mcp 1.2.3 (2-20ms); firefox-mcp and Selenium are working fallbacks with verified clicks.

## 15:28-15:31 - Deploy (2.2.6) via sync-installed.py
- First sync run failed: "visuals manifest is missing or unsafe" (staged native/visuals.json missing). Root cause: visuals.json is a GENERATED file, absent from the repo; the blur 0.15 change in hyprglass-local-optics.lua changed its hash, so the installed manifest (profile_sha256 545455d3...) no longer matched the repo lua (9a151634...).
- Fix: copied installed manifest into the repo checkout, ran scripts/refresh-visuals-manifest.py with the installed hyprglass .so; refresh validated all fields and updated profile_sha256 to 9a151634... (match True). visuals.json is gitignored, sync reads it from disk.
- Second sync run SUCCEEDED: "Installed sync published and verified", 314 managed files, --check exit 0, release ledger 20261121-153056-467165-b0c17acd3e.json.
- Verified: installed indicator binary 50320 bytes Nov 21 15:30 (new build), installed lua blur_strength = 0.15, overlay acquire/release from the INSTALLED copy works (label "Worker J via BiDi", visible true, then daemon exiting, visible false). Item 2.2.6 DONE.

## 15:31-15:35 - Item 2.2.3 E2 phase B animated backdrop
- Hyprland 0.57.2 running, plugins: ONLY hyprbars. hyprglass is NOT loaded.
- hyprland.conf has NO hyprglass references at all (no plugin load, no exec-once). hyprglass.so exists only in backups (full-1791544423, sync-20261116 snapshots).
- Deployed-binary idle check (from the interrupted 60s hold, daemon.log metrics): windows at 15:33:25/26/27 all paint_callbacks 0, surface_commits 0, idle_paint_callbacks 0. Only commits are the show/hide transitions themselves (15:33:28 window: 2 paints, 2 commits, 1 hide command = the release). Third confirmation the indicator does not repaint at idle.
- CONCLUSION 2.2.3: animated-backdrop test CANNOT run in this session. It needs loading a backup hyprglass.so into the live compositor plus configuring LIQUID mode, which risks crashing the user's compositor while the user works. Recorded as BLOCKED: needs a dedicated test window with the user's explicit handover, or a login-time plugin config decision by the user. E1 logging is in place to capture any recurrence. The indicator itself is proven not to repaint at idle (3 measurements).

## 15:38-15:50 +07: tick todo + merge todolist-push vao main (5.2, 5.4)
- 15:38: tick 11 muc trong todo file (1.1.1, 1.1.2, 1.1.3 update, 1.3.2, 1.3.3, 2.2.3 BLOCKED note, 2.2.6 DEPLOYED, 3.4.2, 5.1, 5.2, 5.3 FINAL). Todo: 110/115. Commit 2363d2a, push bi reject (worker khac push song song), fetch + merge f5fa913 (mang ve a0ce8b7 worker-k README), push OK. HEAD luc do 625507f (code-mode commit cua worker khac, da co san tren remote).
- 15:40: test tren VM: test_overlay.py pass, Phase 3 runner 42/42 pass (6 file test, goi moi ham test_*).
- 15:42: merge vao main (worktree cu-jpegq90-land): fast-forward main len 2e558f7 (clone1 report), merge origin/todolist-push -> CONFLICT 3 file: scripts/overlay.py (add/add), tests/test_overlay.py (add/add), improvements/fix-run-20261121.md.
  - overlay.py/test_overlay.py: lay ban MAIN (cung hon: validation agent/method/pid, holder_id, label sanitize; CLI tuong thich acquire/release/status/stop). Da verify diff hai ban truoc khi chon.
  - fix-run: hunk 1 lay HEAD (2.2.4/2.2.6 chi tiet hon), hunk 2 lay HEAD + chen entry E2 05:30 theo thu tu thoi gian + note cap nhat vao Final report section.
  - native/indicator.c + scripts/indicator.py: conflict them (khong thay trong merge output dau, phat hien qua git diff --check). indicator.c: 5 hunk, ca hai ben bo sung cho nhau (main: label routing; todolist-push: E1 metrics + present_failures). Resolve bang regex lay theirs -> SAI: regex an mat 2 hunk co HEAD side rong (format string tail + args intro cua report_metrics), lam hong ham. Phat hien khi doc lai file merged (format string dut doan, thieu wall/args). Sua tay theo ban todolist-push, verify: diff merged vs TODO chi con status handler + busy check cua main; brace count giong het TODO (37/38, checker lech 1 o ca hai parent). indicator.py: lay ours (chi khac format, logic giong nhau); verify merged == main (main la superset: watchdog + status).
- 15:46: test tren cay merged: 46/46 pass (Phase 3 + overlay + indicator). build.py khong chay tren VM (thieu gtk4-layer-shell dev libs) -> C chi verify bang doc + diff, khong claim build pass.
- 15:47: commit merge 96438bb, push main OK, verified ls-remote 96438bb. Tick 5.4 -> commit 7340bc3, push OK. Todo: 111/115. Cap nhat final report (merge done) -> commit abb51bf, push OK. Main hien tai abb51bf.
- 15:49: laptop repo KHONG dong bo: dang o detached HEAD 56f5af4 (viec prefetch H6 cua worker khac), co file sua chua commit (live-test-log.md, scripts/cu.py) + untracked. origin/main tren laptop con cu (851423b, chua fetch). KHONG ep sync, khong dong vao. He qua: overlay.py da deploy tren laptop (15:31, ban todolist-push) hien stale so voi main (ban main co validation + holder_id). Redeploy bang sync-installed.py la follow-up, chi lam khi laptop repo sach hoac worker kia xong.
- Con lai sau merge: 2.1.7 (unmeasurable), 2.1.10 (partial), 2.2.3 (BLOCKED), 3.4.1 E1 (untested). 111/115 done.
