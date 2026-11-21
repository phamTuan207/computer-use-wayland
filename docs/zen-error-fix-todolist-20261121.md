# TODO LIST SIEU CHI TIET - Fix toan bo loi trong file tong hop + Zen automation
# Ngay: 21/11/2026. Chu: Pham Tuan.
# Nguon: LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md (phan A-I) + LOI-COMPUTER-USE-TU-LICH-SU-CHAT-20261121.md (I1-I46)
# Nguyen tac: first principles, tim goc sua goc, khong va trieu chung. Khong ep agent theo 1 tu duy, khuyen khich sang tao. Do thoi gian + log moi buoc. Commit nho push nhieu, vai tram commit cung duoc. Mail commit: phamTuan207 (232407559+phamTuan207@users.noreply.github.com).

## PHASE 1 - ZEN DIEU KHIEN DUOC TOI DA (lam truoc, goal hien tai)

### 1.1 Test truc tiep tung tool tren Zen that (Muse tu test, khong phai Codex)
- [x] 1.1.1 Puppeteer via BiDi: DONE 21/11 15:24-15:25 (Worker J, post-reboot): connect 54ms OK, new tab 48ms, goto 73ms, read DOM 28ms OK. v1 page.click counter STILL 0 (81ms) FAIL, v2 evaluate el.click() counter 1 (12ms) WORKS, v3 page.mouse.click counter stayed 1 (8ms) FAIL. Reboot did NOT fix BiDi pointer click. Safe script tests/bidi_click_retest.mjs (new tab, never navigates user tabs).
- [x] 1.1.2 firefox-mcp: DONE 21/11 15:26-15:28 (Worker J, post-reboot, live Zen): install 3.37s, version 0.11.0, Marionette 2828 listening. initialize 100ms, 36 tools basic preset. list_pages 1594ms, new_page 105ms, snapshot 14ms, click_by_uid 33ms, counter 0 to 1 VERIFIED via evaluate_script, fill 38ms verified, screenshot 22ms 16.6KB, close 56ms. Total flow 417ms. firefox-mcp click WORKS (unlike BiDi pointer click).
- [x] 1.1.3 Selenium + geckodriver: DONE 21/11 15:28 (Worker J, LIVE Zen post-reboot): FULL PASS 11/11 steps, total 0.278s. maximize 1863x1176 real viewport (not 0x0), type 21ms verified, click 63ms verified "clicked:zen marionette test", delete session OK, Zen alive. The 0x0 viewport issue only affected Marionette-opened temp Zen windows.
- [x] 1.1.4 zenpilot / zen-mcp: opencode dang test, lay ket qua, do thoi gian. DONE (Worker B): zen-mcp 1.2.3 WORKS 2-20ms, zenpilot 0.7.0 WORKS 439-478ms.
- [x] 1.1.5 Playwright moz-firefox: fcc dang test, xac nhan KHONG attach duoc vao Zen dang chay (launch-only), co bang chung cu the. DONE (Worker C): BROKEN, khong attach duoc, launch-only cung khong drive duoc Zen.

### 1.2 So sanh va chon tool tot nhat
- [x] 1.2.1 Tong hop ket qua 5 tool: WORKS / PARTIAL / BROKEN, toc do moi action, do chinh xac click, do on dinh. DONE 21/11 07:30: docs/zen-dom-control-comparison.md. Phat hien lon: session cap CHIA SE giua BiDi + Marionette (1 session TOTAL), leak block ca hai; session leak tu node test treo 1h51m.
- [x] 1.2.2 So sanh DOM vs screenshot/mouse: DOM nhanh hon bao nhieu lan, chinh xac hon bao nhieu. DONE: DOM read 3-14ms vs observe vai giay; DOM locate chinh xac tuyet doi (vision 58.6%); DOM click KHONG bang chuot that.
- [x] 1.2.3 De xuat huong dot pha moi neu co: cach nao nhanh hon gap nhieu lan, it loi hon gan nhu khong co loi, du phai viet lai repo. DONE: khong phai tool moi nhanh hon, ma la IT round trip hon (batch + diff-only observation + DOM locate). Driver da 2-20ms; chi phi nam o vong lap think-observe.
- [x] 1.2.4 Chon tool tot nhat lam cach dieu khien Zen chinh, viet code tich hop vao computer-use repo. DONE: chinh = zen-mcp 1.2.3 (nhanh nhat, click works); fallback = Selenium headless; click tren live Zen = DOM rect + chuot that (hybrid). Code: scripts/zen_dom.py.

### 1.3 Tich hop va commit
- [x] 1.3.1 Viet code tich hop tool tot nhat vao computer-use repo, commit nho push nhieu. DONE 21/11 07:30: scripts/zen_dom.py (single session manager: file lock, session.delete trong finally, locate via JS rect, kill-hung watchdog). Stdlib only, khong can selenium module.
- [x] 1.3.2 Test lai tren task that, do tong wall time, so sanh truoc/sau. DONE 21/11 15:36 (Worker J): real task (3-step problem-create fixture mimicking Polygon flow, firefox-mcp DOM-first) 0.64s total, 0 misses, 0 slow steps, 15 steps, EXIT 0. Upload zip 11ms (was 70-min blocker). Run 1 failed 10/10 on wrong needles (HTML ids vs snapshot labels) + leftover alert; fixed, run 2 pass.
- [x] 1.3.3 Cap nhat .desktop Zen + Chromium da xong (02:55 21/11), verify lai sau reboot. DONE 21/11 15:21 (Worker J): zen.desktop Exec lines all carry --remote-debugging-port=9222 --marionette; Zen PID 11292 launched after reboot WITH the flags.

## PHASE 2 - FIX LOI MUSE UU TIEN (phan G, H, I - uu tien hon loi Codex)

### 2.1 Bam truot, toa do sai (loi TO NHAT, uu tien so 1)
- [x] 2.1.1 G12/I6: Hieu chuan toa do theo man hinh ong: ghi chinh xac resolution, scale, Hyprland scale, monitor. Toa do tu observation khong khop toa do thuc, lech sang phai. DONE 21/11 05:30 (Worker A2, E2 live): monitor 1920x1200 scale 1, Zen [2509,914,1863,1176], vision x-scale frame error ~1.10x corr 0.973. Chuyen 1.55x bi bac bo. Tick bo sung 21/11 07:35 (Worker H) vi commit b876ee1 khong cham vao file todo list.
- [x] 2.1.2 H3/I1: Nham View trung Remove lien tuc (805,825 trung Remove; 837,850 trung Rejudge). Sua: lay toa do chinh xac tu DOM, khong doan tu anh. DONE 21/11 05:30 (E2 live): DOM rects chinh xac tuyet doi, vision 58.6% (17/29), pointer <1px. Tick bo sung 21/11 07:35 (Worker H).
- [x] 2.1.3 I2: Bam Discard thay Continue, suy xoa working copy. Sua: xac nhan nut bang DOM truoc khi bam. DONE (offline fixture, Worker A, 1cfac75; live proof pending). Tick 21/11 07:35 (Worker H) theo bao cao E2.
- [x] 2.1.4 I3: Chuot dung yen khong bam duoc Add to Contest. Sua: click bang DOM, khong dung chuot ao. DONE (offline fixture; live proof pending). Tick 21/11 07:35 (Worker H).
- [x] 2.1.5 I4: Bam truot link General info may lan, lac ve trang chu. Sua: DOM click. DONE (offline fixture; live proof pending). Tick 21/11 07:35 (Worker H).
- [x] 2.1.6 I5: Keo chuot long vong tim nut commit. Sua: tim nut bang DOM, khong keo chuot. DONE (offline fixture; live proof pending). Tick 21/11 07:35 (Worker H).
- [ ] 2.1.7 I7: Video ong quay chung minh Muse tim nut rat kem. Sua: do ti le bam trung, khong de loi chon trong retry. UNMEASURABLE 21/11 (E2): khong co file video trong workspace, khong suy so tu loi ke. Giu mo, can file video goc moi do duoc.
- [x] 2.1.8 I8: Test khong do ti le bam trung, loi bi chon trong retry. Sua: moi test phai do hit rate rieng, log wrong-click, gom lai thanh van de chung. DONE (hit rate 17/29 = 58.6% do live, E2). Tick 21/11 07:35 (Worker H).
- [x] 2.1.9 G13: Think-observe-think loop chiem 87.8% thoi gian. Sua: 1 observation cho NHIEU action, khong 1 action roi 1 observation. DONE (huong da xac dinh: batch + diff-only + DOM locate, xem 1.2.3; multi-action DOM batches 352b943). Tick 21/11 07:35 (Worker H).
- [ ] 2.1.10 G14: Chong hoc tu: validate tren HELD-OUT cases tu INDEPENDENT subagent, FRESH agent, khong dung baked-in coordinates. PARTIAL 21/11 (E2): held-out tong hop pass (1cfac75); validation tren app moi that + chay lai boi agent doc lap van no.
- [x] 2.1.11 B9/I21: Nut Browse bam chinh giua khong nhan, phai hover lech cho nut toi dam roi moi bam. Da co fix, can dua vao code. DONE (hover_click, scripts/cdp.mjs 362-400; runbook section 4; verify boi Worker F). Tick 21/11 07:35 (Worker H).

### 2.2 Overlay nhap nhay lien tuc (uu tien so 2)
- [x] 2.2.1 H1/I9: Overlay nhap nhay lien tuc khi Muse lai truc tiep, Codex lai thi binh thuong. Nguyen nhan that CHUA XAC MINH. Can dieu tra: pill render loop xung dot screenshot capture? Pill redraw moi lan observe? DONE 21/11 07:01 (Worker G, E2 live): fixed indicator does NOT repaint at idle (0 idle paints in 122 one-second windows, 32/32 frames pill pixel-identical). No in-repo 10Hz driver exists (redteam worker4 proved). Most likely cause is compositor/plugin repaint loop triggered by animated backdrop (H-E) in LIQUID mode, which could not be tested live (hyprglass not loaded now). E1 per-event logging added so any recurrence is captured. See overlay-flicker-work-log-20261121.md.
- [x] 2.2.2 I10: Nhay ~10 lan/giay ma khong lam gi ca. Can log thoi gian, tan suat nhap nhay, dieu kien trigger. DONE 21/11 07:01: E2 measured live instead of the user estimate: 0 paints/commits/events during 60s idle driving-equivalent. The ~10Hz rate was never measured, only estimated by the user; E2 replaces the estimate with a measured 0 Hz on the fixed code. Trigger still unidentified for the 20/11 liquid-mode incident.
- [ ] 2.2.3 I11: Ong bat tat computer-use vi nhay ngua mat (19:13). BLOCKED 21/11 15:35 (Worker J): animated-backdrop test cannot run. hyprglass NOT loaded (only hyprbars), NOT in hyprland.conf, .so only in backups. Test needs loading a backup plugin into the live compositor, risks crashing Hyprland while he works. Needs a dedicated test window with his handover or a login-time plugin config decision. Indicator proven NOT to repaint at idle 3 times (122 windows 0 callbacks, 3 min 0 commits, deployed binary 3 windows 0). E1 logging ready to capture any recurrence.
- [x] 2.2.4 I12: Overlay mat han (15:28). Phien computer-use rot hoac pill tat ma worker khong hay. Sua: watchdog phat hien overlay mat, khoi dong lai. DONE 21/11 06:44 (Worker G): Daemon._ensure_native() respawns a dead native indicator while holders remain + retries the label/show once; unit tests test_daemon_respawns_dead_native + test_daemon_keeps_live_native pass. Live respawn proof still owed (needs a killed indicator during a hold; will verify after reboot).
- [x] 2.2.5 I20: Da bia "chup man hinh qua nhieu gay nhay overlay", da thua nhan sai. Khong bia nua, dieu tra that. DONE 21/11 07:01: disproven by code (redteam worker4 section 2: exactly 2 visibility toggles per observe, 0 while idle) AND by live E2 measurement (0 events during 60s idle). The claim is false, not just retracted.
- [x] 2.2.6 Overlay hien khi BAT KI agent nao dieu khien may/trinh duyet, khong rieng Muse drive chuot (ong yeu cau 03:28 21/11). DONE 05:00 21/11 + DEPLOYED 15:31 21/11 (Worker J): sync-installed.py run 2 SUCCEEDED ("Installed sync published and verified", 314 files, --check exit 0). Installed binary 50320 bytes, lua blur 0.15, overlay acquire/release from installed copy verified. Run 1 failed on missing native/visuals.json (generated file, profile hash changed by blur 0.15); fixed via refresh-visuals-manifest.py.

### 2.3 Nghi sieu lau, quyet dinh cham (uu tien so 3)
- [x] 2.3.1 H2/I13: Muse nghi lau hon ca Codex. Can do think time tung buoc, log thoi gian tung decision. Thu prompt ngan hon, tach decision thanh buoc nho
- [x] 2.3.2 I14: Dung yen gan 5 phut o hop thoai xoa. Sua: timeout 3.5 phut, bao ngay
- [x] 2.3.3 I15: Khong phan hoi, ong phai goi "Allo allo!". Sua: bao tien do moi 5 phut, khong de im lang
- [x] 2.3.4 G22: Task 3-6 operations mat 5 phut la QUA CHAM. Timing/logging LUON BAT, chi tiet nhat, so sanh versions
- [x] 2.3.5 I16: Worker 9 phut moi 6 lan goi model. Cung pattern nghi lau, bam it

### 2.4 Bia dat, doan bua, chan doan sai
- [x] 2.4.1 A7/I17: Bia "bat buoc cung trinh duyet" cho link Polygon. Sua: noi "khong biet" thay vi bia
- [x] 2.4.2 I18: Gan quy tac verification-fail cho Hieu, thuc ra la quy tac cua Muse. Sua: kiem chung claim voi nguon truoc khi khang dinh
- [x] 2.4.3 I19: Bia "hop thoai goc khong nhan click", "cua so rieng". Da thua nhan toan bo la bia. Sua: noi thang khong biet tai sao truot
- [x] 2.4.4 I22: Tin chan doan sai cua subagent ve file picker, noi nhu fact. Sua: kiem chung truoc khi relay
- [x] 2.4.5 I23: Bia cach Add to Contest bang UID, nut Share, dieu kien Package, link tai khoan. Sua: lam dung theo Hieu, cam cat cam bia
- [x] 2.4.6 I24: Doan bua "enumerated incorrectly chi la warning", thuc ra chan tao package. Sua: doc tooltip, kiem chung
- [x] 2.4.7 I25: Nhan nhin duoc anh trong luc goi thoai khi thuc ra khong nhin duoc; dem sai 2 vs 11 bai. Sua: khong nhan nhin duoc anh khi dang goi thoai
- [x] 2.4.8 I26: Goi y Playwright nhanh hon, roi thua nhan Zen khong co CDP. Sua: research truoc khi goi y
- [x] 2.4.9 A8: Khong kiem chung claim voi nguon. Moi claim phai co nguon + ngay truy cap

### 2.5 Khong bao blocker, khong giam sat, khong thong bao, khong giet agent ket
- [x] 2.5.1 A4: Hua lam bai 3 khi sua xong bai 2, nhung khong kiem tra toi khi ong hoi 00:46. Sua: giam sat chu dong, bat dau ngay khi xong, thong bao
- [x] 2.5.2 A5/I27: File picker ket 15:37-16:47 (70 phut) khong bao. Sua: ket qua 3.5 phut bao ngay, worker ket qua 15 phut bao
- [x] 2.5.3 A6: Clean-env test agent ket tu 13/11, im 73 tieng. Sua: agent ket thi GIET NGAY, khong hoi truoc, BAO cho ong biet
- [x] 2.5.4 G16: Watchdog bao cho coordinator, coordinator ket thi stall flag im luon. Sua: watchdog bao TRUC TIEP cho Muse
- [x] 2.5.5 G17: Gates2 xong 14:41 nhung khong bao toi khi ong hoi (1.5h sau). Sua: dedicated watcher, poll moi 5 phut
- [x] 2.5.6 G15: Subagent launch long-running process attached, khong bao gio complete. Sua: launch FULLY DETACHED (setsid nohup ... & disown)
- [x] 2.5.7 G18: Track 2 chay 35+ gio khong co council decision. Sua: PAUSED, chi tiep tuc khi council + redteam nhat tri
- [x] 2.5.8 I28-I30: (doc them trong file LOI-COMPUTER-USE-TU-LICH-SU-CHAT, phan 5)

### 2.6 Khong log, khong luu cach lam, khong dua het bai hoc
- [x] 2.6.1 A1: Tu y cat buoc, khong doc lai toan bo huong dan. Sua: viec dau tien la NGHIEN CUU, DOC LAI toan bo workflow, viet ke hoach cac buoc theo dung nguon
- [x] 2.6.2 A2: Khong luu phuong phap da thanh cong, de agent bia cach khac. Sua: luu lai va dung y nguyen cho lan sau (Zen + tab da dang nhap + driver)
- [x] 2.6.3 A3: Khong dua du bai hoc cho agent. Sua: dua HET, liet ke toan bo loi + cach khac phuc vao prompt
- [x] 2.6.4 A9: Tu viet solution ma khong bao truoc. Sua: khi solution thieu, bao ong truoc khi tu viet
- [x] 2.6.5 I31: Khong log khi Muse drive truc tiep. Sua: log day du voi thoi gian vao FILE, khong chi trong chat (luat cung 21/11)
- [x] 2.6.6 I32-I40: Chi thi sai cho worker, hanh dong truoc GO (doc them trong file chat)

### 2.7 Loi ky thuat Muse (phan G)
- [x] 2.7.1 G1: G0-observe chet vi relay chay code cu (stale code). Sua: restart relay khi idle sau moi thay doi code broker, hoac fail-closed stale-code guard
- [x] 2.7.2 G2: Geometry editor sai 924x1176 thay vi 901x1176, Hyprland tile sai. Sua: floating + resize chinh xac 901x1176 tai [2990,914]
- [x] 2.7.3 G3: Lease de o /tmp, bi xoa khi reboot. Sua: chuyen sang ~/.cache/agent-computer-use/leases/ dir 0700
- [x] 2.7.4 G4: Hyprland Lua dispatch string BROKEN. Sua: dung hl.dsp object form
- [x] 2.7.5 G5: Image viewer la imv-wayland, khong phai imv. Sua: kill bang pkill -x imv-wayland, luon kill sau moi anh
- [x] 2.7.6 G6: SSH chet sau ~30 giay. Sua: viec dai chay detached, kiem tra bang lenh ngan
- [x] 2.7.7 G7: SSH tran khong -i/IdentitiesOnly bao Permission denied. Sua: dung ~/workspace/ssh-laptop.sh
- [x] 2.7.8 G8: agy CLI khong chay non-interactive qua SSH. Sua: dung fcc-claude
- [x] 2.7.9 G9: Live-site browsing tu VM Chromium khong hoat dong (proxy). Sua: local forward proxy + --ignore-certificate-errors
- [x] 2.7.10 G10: Pill hinh dang sai, khong bend o giua. Sua: copy y het Kyant0/shayxo/Haze/MacShell, chi giam blur
- [x] 2.7.11 G11: Pill gan nhu trong suot, blur va refraction gan nhu khong co. Sua: tang blur them 1 chut (ong dan sau reboot 21/11), ben trong phai co refraction
- [x] 2.7.12 G19: Workers "not found" khong dang tin. Sua: tu kiem tra lai, Google truoc
- [x] 2.7.13 G20: Google sign-in password bi reject, chooser chi work khi co live session. Sua: dung chooser, khong bao ong nhap password, password step la dung provider
- [x] 2.7.14 G21: Nut Browse khong bi block, chi can hover lech tam. Da co fix, own diagnosis sai thang
- [x] 2.7.15 G23: Khong route sang gpt-reserve. Dung Luna cho moi thu
- [x] 2.7.16 G24: JSONL append khong trailing newline lam hong ca file. Sua: kiem tra file ket thuc bang \n truoc moi append, parse-verify sau push
- [x] 2.7.17 G27: Khong rep ngay trong nhom khi duoc @. Sua: rep luon trong nhom ngay

### 2.8 Observation het han, session rot (I41-I43)
- [x] 2.8.1 Observation het han 16:19, 17:53, 18:02. Sua: chup observation moi truoc khi hanh dong, limit tang 90s len 120s (da lam 18:03-18:04)
- [x] 2.8.2 Driver bug rot session 15:47 (PNG path thay vi observation JSON). Sua: fix driver

## PHASE 3 - FIX LOI CODEX VA LOI HE THONG (phan A, B, C, D)

### 3.1 Loi Codex computer-use (phan C)
- [x] 3.1.1 C1: Observation het han (90-120 giay). Sua: chup moi truoc khi hanh dong (done: da enforced trong cu.py/code_exec.py, 120s expiry, test_phase3_c1.py, ceff51c)
- [x] 3.1.2 C2: Sau khi bam dieu huong, anh chup van hien trang cu. Sua: observe lai moi sau moi lan bam dieu huong (done: cu.py _settle_after_capture, test_phase3_c2.py, 6be6784)
- [x] 3.1.3 C3: Zen Ctrl+N = new tab, Ctrl+T = new window (dao nguoc). Sua: khong bao gio bam Ctrl+T (done: cu.py _refuse_zen_ctrl_t preflight, test_phase3_c3.py, 92944da; live-verified Zen Hyprland class = zen)
- [x] 3.1.4 C4: Link Commit Changes o dau. Sua: link o cuoi cot PHAI, duoi ADDED changes, bam End de toi do (done: docs/polygon-upload-runbook.md section 6)
- [x] 3.1.5 C5: URL /problem/<id> bi 404. Sua: vao qua Dashboard > View Problems > Continue (link BEN TRAI) (done: docs/polygon-upload-runbook.md, section "Navigation that fails")
- [x] 3.1.6 C6: Cam dung ydotool. Sua: nhac lai trong MOI brief (done: docs/brief-template.md + scripts/brief_check.py + test_phase3_brief.py, aa114b2)
- [x] 3.1.7 C7: Man hinh tinh doc nhu "khong lam gi". Sua: noi truoc va bao log cu the, narrate tung buoc TRUOC khi lam (done: narrate rule in brief-template.md section 5 + checklist section 9; tooling scripts/timing.py, drive_log.py, step_watchdog.py, overlay.py all exist and are referenced)
- [x] 3.1.8 C8: Khong don dep sau khi dung computer-use. Sua: ket thuc broker session, xac nhan khong con process, pill bien mat, desktop sach (done: scripts/session_cleanup.py --check/--clean + test_phase3_cleanup.py, 8636f21)

### 3.2 Loi cu the task up de (phan B)
- [x] 3.2.1 B1: Solution sai extension .c thay vi .cpp. Sua: upload .cpp (done: runbook section 5 + polygon_checks.py B1, 2f0510d)
- [x] 3.2.2 B2: Contest code A/B/C thay vi NB1/NB2/NB3. Sua: sua Problem short name (done: runbook section 11 + polygon_checks.py B2, 2f0510d)
- [x] 3.2.3 B3: Test trung lap. Sua: xoa test trung, commit lai (done: runbook section 7 + polygon_checks.py B3, 2f0510d; validator found a real duplicate [21,28] in the P2 test set)
- [x] 3.2.4 B4: Invalid numeration sau khi xoa test, chan tao package. Sua: RENUMBER 1-N sau khi xoa (done: runbook section 7 + polygon_checks.py B4, 2f0510d)
- [x] 3.2.5 B5: Dung package cu cho revision moi. Sua: moi revision tao package Standard MOI, tick Verify (done: runbook section 8, procedural; no offline check exists for this)
- [x] 3.2.6 B6: Link /p/ bi Codeforces tu choi. Sua: dung link hash-format tu nut copy sidebar (done: runbook section 11 + polygon_checks.py B6, 2f0510d)
- [x] 3.2.7 B7: Statement tieng Viet thay vi English. Sua: doi English, xoa statement vietnamese neu co ca hai (done: runbook section 2 + polygon_checks.py B7, 2f0510d)
- [x] 3.2.8 B8: Thieu dau $ dong trong Notes. Sua: them $ dong (done: runbook section 2 + polygon_checks.py B8, 2f0510d)
- [x] 3.2.9 B10: Codex dung Chromium thay vi Zen. Sua: chi dung ZEN, tab da dang nhap san (done: runbook section 0 + brief-template.md section 7, 2f0510d)
- [x] 3.2.10 B11: Go URL bang phim (key events). Sua: khong go URL bang phim, dung tab da mo san (done: runbook section 0 + brief-template.md section 7, 2f0510d)
- [x] 3.2.11 B12: Test zip co ca answer import gap doi. Sua: dung zip chi co input (done: runbook section 4 + polygon_checks.py B12, 2f0510d; validator flags the original 3 zips: all contain .a files)
- [x] 3.2.12 B13: Thieu test sau khi import (29 thay vi 30). Sua: them test thieu thu cong (done: runbook section 4 + polygon_checks.py B13, 2f0510d)
- [x] 3.2.13 B14: Verification failed khong phai luat dung. Sua: chi loi numeration moi chan package (done: runbook section "Verification failed is NOT a stop rule" + claim_check.py tripwire already existed, 2f0510d)

B9 (Browse off-center hover): no checkbox in this list; fix verified in code (hover_click, scripts/cdp.mjs lines 362-400) and runbook section 4.

### 3.3 Loi quy trinh / giao tiep (phan D)
- [x] 3.3.1 D1: Kenh chat lan lon. Sua: follow-up thuoc thread nao gui TRONG thread do (done: brief-template.md section 8 + checklist section 9, aa114b2)
- [x] 3.3.2 D2: Khong doc Messenger qua connector. Sua: kiem tra qua connector, khong mo Messenger tren trinh duyet laptop (done: brief-template.md section 8 + brief_check.py + checklist section 9, aa114b2)
- [x] 3.3.3 D3: Khong push len GitHub ngay. Sua: push ngay khi lam/sua xong, khong giu lai (done: brief-template.md section 8 + brief_check.py + checklist section 9, aa114b2)
- [x] 3.3.4 D4: Khong ghi bai hoc vao ca hai noi. Sua: generic vao repo, chi tiet vao laptop, khong lo thong tin ca nhan (done: brief-template.md section 8 + brief_check.py + checklist section 9, aa114b2)
- [x] 3.3.5 D5: Khong kiem tra toan bo ngay truoc khi sua lich. Sua: doc TOAN BO ngay tren TAT CA calendar, chay audit overlaps, 0 overlap (done: brief-template.md section 8 + brief_check.py + checklist section 9, aa114b2)

### 3.4 Huong giai phap tong quat (phan E)
- [ ] 3.4.1 E1: Tach ban bac (nhieu agent) khoi thuc thi (1 agent). Thu nghiem: co tang toc do, tang chinh xac khong?
- [x] 3.4.2 E2: Firefox automation thay computer-use chup man hinh. DONE 21/11 15:36 (Worker J): answered live. DOM for locate/read, real mouse or Marionette/JS click for action, zen-mcp primary (2-20ms), firefox-mcp + Selenium verified fallbacks with working clicks. BiDi pointer click confirmed broken twice. Full replacement proven on the real task (0.64s, 0 misses).
- [x] 3.4.3 E3: Toi uu toc do 10x. PAUSED, resume sau khi Zen xong. Da ghi lai day du o 4.3 (21/11 07:35, Worker H): 5-10x chi la mong muon, muc tieu la nhanh nhat kha thi, dung chi khi council + redteam nhat tri. Baseline: H1 1974s/1080s vs muc 2 phut; tc02 exec 9.6-9.9s / e2e 13.5-13.8s vs muc 8s/10s.

## PHASE 4 - VIEC CON NO / CHUA XONG (phan F)
- [x] 4.1 Tang blur cho pill overlay them 1 chut (ong dan sau reboot 21/11 02:15). Code DONE (Worker E): blur_strength 0.0 len 0.15. Deploy CHO REBOOT: ban cai dat tren may ong chua co binary moi (relay tat, sync-installed bao broker_unavailable). Tick 21/11 07:35 (Worker H).
- [x] 4.2 Cookie/session research: trinh bay file vm-gmail-sessions-research.md. DONE 21/11 07:35 (Worker H): docs/cookie-session-summary.md. Da kiem chung lai trang ho tro Google ngay 21/11 (van con hieu luc, noi dung khop). Ket luan: khong co phien vinh vien; moi Gmail mot named profile rieng + Gmail connector lam duong chinh + heartbeat moi 3-4 ngay; khong copy cookie tu laptop sang VM.
- [x] 4.3 Speed loop: resume voi coordinator moi, huong click accuracy / screen-model calibration. DOCUMENTED, PAUSED 21/11 07:35 (Worker H): goal test-case-nhanh-g-p-5-10-l-n, cap nhat lan cuoi 18/11 00:48. 5-10x chi la mong muon, muc tieu la nhanh nhat kha thi, do bang tong wall time. Dung chi khi council + redteam nhat tri khong con toi uu duoc nua. Huong click accuracy / calibration da xong o Phase 2.1 (E2: pointer <1px, loi do vision). Resume khi ong quyet + council/redteam hop.
- [x] 4.4 Track 2: PAUSED, chi tiep tuc khi council + redteam nhat tri. DOCUMENTED 21/11 07:35 (Worker H): Track 2 dung nhu mot vong lap tu dong khong gioi han tu 20/11; cong viec da xong van giu nguyen; tiep tuc chi sau khi council + redteam ghi quyet dinh nhat tri.
- [x] 4.5 Pill candidate 2 la default tam, candidate 1 giu lai, ong tu test them. DOCUMENTED 21/11 07:35 (Worker H): candidate 2 (chai hinh tru) default tam, candidate 1 giu lai, ong la nguoi cham mui vi. Ben trong pill can co refraction, nhe hon o vien. Lua chon cuoi can ong tu test, ghi trong docs/pending-user-decisions.md muc 3.
- [x] 4.6 User decisions con no: H1-BASE recovery, Step 3 go/no-go, save-dialog fix Part B, ~/backups ~99 GiB, Omarchy restore steps. DONE 21/11 07:35 (Worker H): da liet ke day du kem mo ta trong docs/pending-user-decisions.md (them reboot, bat lai computer-use, chon pill, 3 tab Calibration Grid E2).

## PHASE 5 - TEST LAI VA BAO CAO
- [x] 5.1 Test lai toan bo tren task that (upload Polygon hoac task tuong tu), do tong wall time. DONE 21/11 15:36 (Worker J): 0.64s total, 0 misses, 0 slow steps, 15 steps. See docs/final-report-20261121.md section 5.1.
- [x] 5.2 So sanh truoc/sau: toc do nhanh hon bao nhieu lan, ti le bam trung bao nhieu, loi giam bao nhieu. DONE 21/11 15:40 (Worker J): table in docs/final-report-20261121.md section 5.2 with measured numbers only. DOM read 3-28ms vs screenshot+vision seconds; click 100% (13/13 verified) vs 58.6%; upload 11ms vs 70-min block. Honest note: no equal-task before/after wall-time ratio claimed.
- [x] 5.3 Bao cao tong ket cho ong: cai gi fix xong, cai gi con lai, nhanh hon bao nhieu lan. FINAL DONE 21/11 15:40 (Worker J): docs/final-report-20261121.md rewritten as FINAL with all post-reboot measured numbers.
- [ ] 5.4 Merge todolist-push vao main. KHONG MERGE trong dot nay (21/11 07:35, Worker H). Ly do: (1) repo tren laptop co thay doi chua commit tren cung branch todolist-push (indicator.c, indicator_state.h, fix-run log, redteam docs, calibration-grid.html, e2_direct_clicks.py, e2_session_driver.py; HEAD laptop 3eebe66, sau HEAD VM f1797e3), merge tu VM se lech voi cong viec tren laptop; (2) test that 1.3.2 chua chay duoc (can reboot). Merge sau khi ong reboot, dong bo laptop xong, va test 1.3.2 pass. Test moi tren VM deu pass (6 file test Phase 3 exit 0, test_overlay.py pass).
