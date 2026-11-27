# TODO LIST SIEU CHI TIET - Fix toan bo loi trong file tong hop + Zen automation
# Ngay: 21/11/2026. Owner: the project owner.
# Nguon: LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md (phan A-I) + LOI-COMPUTER-USE-TU-LICH-SU-CHAT-20261121.md (I1-I46)
# Nguyen tac: first principles, tim goc sua goc, khong va trieu chung. Khong ep agent theo 1 tu duy, khuyen khich sang tao. Do thoi gian + log moi buoc. Commit nho push nhieu, vai tram commit cung duoc. Mail commit: phamTuan207 (232407559+phamTuan207@users.noreply.github.com).

## THU TU UU TIEN - 21/11 22:32, council + redteam (PRIO, 22:45)
- Len: ong 22:32: todolist da co, hop council phan bien + redteam cai nhau, xep hang viec quan trong nhat; team crawl lai lich su chat tim loi sot; xep theo thai do + luu y cua ong. Council 1 (co che) + Council 2 (thai do ong) + Council 3 (rui ro) + redteam (8 tan cong A1-A8, 5 muc sot M1-M5). Giay to: improvements/worker-prio-crawl-log.md, worker-prio-council-1/2/3.md, worker-prio-redteam.md.
- Muc tieu 240 commit (ong 22:40): 240 commit truoc 24:00 hom nay, hien 190 (189 commit + 1 PR), can them ~51. Moi buoc nho xong la commit + push ngay, khong don. Chat luong tren het, council + redteam day du.
- P0 (tien dieu kien, DA XONG 22:40): VMFIX khoi phuc SSH ben vung (F1 sua dung re/__init__.py tu CPython 3.12.3, dpkg -V sach, observe 22:38 ok). Guardian that bai KHONG phai do re, do cursor-guard plugin chua load, F1 dang sua. Nguyen nhan goc xoa file van CHUA ro. Gate G-VMFIX: verify lai `import re` + SSH_OK truoc moi hang live tu 4 tro di; neu tai dien, dong bang moi viec live, chi lam viec VM-local.
- HANG SERIAL (1 runner live duy nhat, 1 session BiDi/Marionette TOTAL):
  1. F3 khoi phuc Zen + slot Marionette + don 15 tab cuoi (4.7/4.8/4.10, J1/J2/J3, J21). Thu tu trong: verify xem click 22:17 da tu chua slot chua (redteam A7) -> khoi phuc Zen -> sua slot -> don tab cuoi. Gate G-RESTORE, G-TAB. Ly do: ong 22:25 "Zen bi loi, khong the dung binh thuong"; ong 22:30 hoi "viec dau tien gio ong dinh lam luon la gi", Muse tra loi F3, ong khong phan doi. J21 (ong 22:45): mo menu Omarchy + chuyen workspace bang LENH (hyprctl dispatch dang hl.dsp), KHONG BAO GIO bam chuot vao nut workspace/menu tren bar; CLI truoc, chuot sau cung.
  2. Cum fix F1+F2 gop mot (4.11/4.12, J4/J5): F1 truoc (session/guardian, pill hien), F2 sau (<30s tu lenh den dong tac dau tien nhin thay, thao tac lien tuc, overlay luon hien), MOT bang chung end-to-end. Gate G-F1-BEFORE-F2. Ly do: ong 22:16:54 "cai yeu diem im lang nay phai fix DAU TIEN va fix TOI UU TOT NHAT" + 22:21 "khong can noi truoc, phai nhanh + lien tuc + overlay PHAI HIEN". Phan quyet: Council 2 + redteam A1 doc "DAU TIEN" theo nghia den (F2 hang 1); Council 1 + Council 3 + redteam A2 chung minh F2 khong do duoc khi session chet trong 0.46s, overlay khong session lap lai loi I12. Cum nay la fix DAU TIEN cua ong; chi co unblocker F3 dung tren no vi F3 tao dieu kien cho bang chung cua no.
  3. ZT-B chay mu kich ban nguoi dung pho thong (4.9, J6). Gate G-RESTORE, ZT-00 pass, R-01. Ly do: ong 22:26 "cho doi chuyen test ... gia lap nguoi dung pho thong vao cac thao tac".
  4. Y6 pill measurement retry (4.13, 2.2.3). Fix giay A1-A7/A9-A10 chay o lane song song; hang nay la A8 load-only trial + retry. Gate G-PILL. Ly do: ong chon C 18:24; Y6r AMEND nhat tri; 2.2.3 la muc GOAL mo duy nhat.
  5. Y13 live run (4.14). Gate G-RESTORE, G-SINGLE-LIVE, G-HIDDEN, G-H2, Y13r2 + huong H3. Ly do: thu tu roadmap; Y13r2 dang re-review fix diff.
  6. Y14 live run (4.14). Gate nhu tren + Y14b clear. Ly do: sau Y13 theo roadmap.
  7. A1 pilot resume (4.15). Gate: 3 blocker cua clone1 da sua + tien dieu kien (lenh viet tay dat ten 12 run-id, broker SOLO, relay verified, Layer-2 probes, checker cross-check). Ly do: ong duyet de xuat W 18:16; A1 la de xuat duy nhat co thang do duoc rieng (Pick 1: wall -53%).
  8. Thi nghiem quyet dinh hidden-body + follow-up Y4d/Y7 (4.17, J9). Gate G-HIDDEN da keo len truoc vao hang 5-6. Ly do: 0 lan gap o Y4d/Y9b, khong ep duoc khi chua gap.
  9. Clone2 batch nang: re-review doc lap diff F1/F2/F3 (sau khi diff dong bang). Ly do: Council 3 tach batch: nhe chay ngay o lane song song, nang doi diff dong.
  10. Y1b snippets (4.19, J13). Gate G-Y1B tuyet doi. Ly do: Phase A BLOCK van dung; probe 10b/10f se PASS ca ban de tan cong neu khong viet lai.
  11. Scrub email + ten that khoi lich su (4.20, J8). Gate G-SCRUB. Ly do: luat NO PII dung; chi chay trong cua so yen tinh that su, neu khong co thi doi.
  12. Final test, contest Codeforces doc lap 5 bai (4.21). CUOI CUNG trong cac muc viec. Ly do: ong 16:30, xac nhan 2 lan, chay CUOI CUNG sau moi viec khac.
- LANE SONG SONG (bat dau ngay, song song hang serial 1-3, khong lay lane live):
  P-A. Clone2 batch nhe: J14 follow-up + tu verify batch 5 + dong/giao lai nhiem vu watchdog J16.
  P-B. Clone1 J12: bao cao verify batch 4 + ket qua chay lai Firefox Y10 t05/t09/t10 (di kem batch 6 clone1, giao 22:40).
  P-C. Y6 fix giay A1-A7, A9-A10 (nuoi hang serial 4).
  P-D. A1 tien dieu kien giay (sua 3 blocker cua clone1).
  P-E. Y1b viet lai probe giay (nuoi hang serial 10).
  P-F. Y4d/Y7 follow-up giay (nuoi hang serial 8).
  P-G. M2: giai xung dot coord PR #1 + merge (chan G-SCRUB).
  P-H. M4/D3: F1/F2/F3 commit + push diff cua ho NGAY (commit nho, phan cua muc tieu 240). Luat dung cho moi worker.
- PARKED: Track 2 + speed loop (chi mo khi council + redteam nhat tri bang van ban); Super I (ong hoan 17:42); 2.1.7 I7 video (can ong gui lai file goc); pending user decisions (can ong); E1 fresh comparison (4.22, de hoan; neu bao gio xep lich that thi chay truoc final test); J15 freeze (thap, tru khi tai dien). J21 attribution (dua nao click workspace 1 luc ~22:44, log F2/F3 khong ghi) gap vao fix F2/F3 (log moi click).
- GATES (day du): G-VMFIX (tren), G-RESTORE (session restore dem lai 28 tab that, bam tab duoc, mo web that render duoc, doi workspace bang lenh duoc), G-TAB (mo tab hy sinh TRUOC khi dong tab; ket thuc session luc dang focus tab song), G-F1-BEFORE-F2 (do F2 chi khi F1 xanh), G-PILL (A1-A10 + re-review moi, A8 load-only trial truoc, khong bao gio load hyprglass live khi F-team dang sua may), G-SINGLE-LIVE (1 runner live duy nhat), G-HIDDEN (check body-visible truoc dong tac dau tien cua moi live run hang 5-6), G-H2 (think-time instrumentation BAT o hang 5-7; H2 khong con run rieng), G-SCRUB (moi push da len, PR #1 xong, khong live run nao dang chay, moi agent duoc bao re-clone; neu khong co cua so yen tinh that thi doi), G-Y1B (probe 10b/10f + 1e/4a viet lai truoc khi xet Phase B; 12-item BLOCK thi hanh).
- CAC PHAN QUYET CHINH: (1) F1 vs F2: xem hang 2 tren. (2) Clone2: Council 2 doi hang 5, Council 3 tach nhe/nang, redteam A4 doi lane song song; phan quyet: lane song song + tach (nhe ngay, nang hang 9). (3) Y6: redteam A5 doi hang 4 hoac lane song song; phan quyet: fix giay vao lane song song ngay, retry giu hang 4. (4) H2: Council 1 + 3 gap vao Y13/A1, Council 2 doi hang 9; phan quyet: gap instrumentation vao hang 5-7 (G-H2), khong run rieng; bang chung <30s cua F2 do ngay o hang 2. (5) Duoi: redteam A6 dung (E1 sau final test pha lenh CUOI CUNG); phan quyet: E1 ve PARKED, scrub la bao tri co G-SCRUB rieng, final test la muc viec cuoi cung. (6) M5: redteam dung, ong chon C luc 18:24 (memory 1605/1608/1713), ban tom tat truoc ghi nham 18:16; da sua o 2.2.3. (7) M3: F1/VMFIX va cham tren re/__init__.py da dong (VMFIX DONE 22:40), chi con ke xoa file chua ro ten. (8) A7: hang 1 bat dau bang verify xem click 22:17 da tu chua slot chua.

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
- [ ] 2.1.7 I7: Video ong quay chung minh Muse tim nut rat kem. Sua: do ti le bam trung, khong de loi chon trong retry. UNMEASURABLE 21/11 (E2): khong co file video trong workspace, khong suy so tu loi ke. Giu mo, can file video goc moi do duoc. XAC NHAN LAI 21/11 17:52 (Worker X): tim het file video tren VM (~/workspace, ~/memory, /tmp) va laptop (/home/james/workspace, Downloads, Videos, /tmp): chi co hieu-tutorial.mp4 (cua Hieu, khong phai video cua ong) va IMG_6089.mp4 luc 12:04 20/11 (video camera dien thoai, truoc video 19:04 7 tieng). Khong co screen recording nao ngay 20/11 tren laptop, khong co file nao 18:00-20:00 20/11 trong media_library. Video 19:04 chi nam trong chat Messenger (E2EE, connector khong doc duoc media). Chi mo lai duoc khi ong gui lai file video goc. Phan do duoc cua I7 (do ti le bam trung) da xong o 2.1.8 (E2: 17/29 = 58.6% vision, DOM 100%).
- [x] 2.1.8 I8: Test khong do ti le bam trung, loi bi chon trong retry. Sua: moi test phai do hit rate rieng, log wrong-click, gom lai thanh van de chung. DONE (hit rate 17/29 = 58.6% do live, E2). Tick 21/11 07:35 (Worker H).
- [x] 2.1.9 G13: Think-observe-think loop chiem 87.8% thoi gian. Sua: 1 observation cho NHIEU action, khong 1 action roi 1 observation. DONE (huong da xac dinh: batch + diff-only + DOM locate, xem 1.2.3; multi-action DOM batches 352b943). Tick 21/11 07:35 (Worker H).
- [x] 2.1.10 G14: Chong hoc tu: validate tren HELD-OUT cases tu INDEPENDENT subagent, FRESH agent, khong dung baked-in coordinates. DONE 21/11 17:52 (Worker X, danh gia doc lap): validation tren app moi that boi 3 agent doc lap moi toanh, moi nguoi mot bo test moi ma ho khong sinh ra, dung DOM rects (khong toa do baked-in), chay live tren Zen that: Worker P chay clone1 t01-t10 10/10 PASS (tests/realistic/RUN-REPORT-20261121.md, b8db405; full run 9/10 trong 59.1s, t06 pass 3/3 sau fix); Worker R chay agy-q 5/5 PASS sau fix q04 (tests/realistic/RUN-REPORT-AGYQ-20261121.md, 97d28d5; q04 re-run PASS 4,172ms, aa302f7); Worker U chay fcc-k da sua 10/10 PASS live (tests/realistic/RUN-REPORT-FCCK-FIXED-20261121.md, aa302f7; tong 28,613ms, 383 buoc 0 loi). Tong 25/25 test app moi pass. Han che ghi ro: cac run dung scripted DOM driver de do thoi gian may (machine floor); mau hand-driven cua P (t01, ~7 phut, PASS) chung minh agent tu quyet dinh cung chay duoc. Phan held-out tong hop cu (1cfac75) van giu lam bang chung phu.
- [x] 2.1.11 B9/I21: Nut Browse bam chinh giua khong nhan, phai hover lech cho nut toi dam roi moi bam. Da co fix, can dua vao code. DONE (hover_click, scripts/cdp.mjs 362-400; runbook section 4; verify boi Worker F). Tick 21/11 07:35 (Worker H).

### 2.2 Overlay nhap nhay lien tuc (uu tien so 2)
- [x] 2.2.1 H1/I9: Overlay nhap nhay lien tuc khi Muse lai truc tiep, Codex lai thi binh thuong. Nguyen nhan that CHUA XAC MINH. Can dieu tra: pill render loop xung dot screenshot capture? Pill redraw moi lan observe? DONE 21/11 07:01 (Worker G, E2 live): fixed indicator does NOT repaint at idle (0 idle paints in 122 one-second windows, 32/32 frames pill pixel-identical). No in-repo 10Hz driver exists (redteam worker4 proved). Most likely cause is compositor/plugin repaint loop triggered by animated backdrop (H-E) in LIQUID mode, which could not be tested live (hyprglass not loaded now). E1 per-event logging added so any recurrence is captured. See overlay-flicker-work-log-20261121.md.
- [x] 2.2.2 I10: Nhay ~10 lan/giay ma khong lam gi ca. Can log thoi gian, tan suat nhap nhay, dieu kien trigger. DONE 21/11 07:01: E2 measured live instead of the user estimate: 0 paints/commits/events during 60s idle driving-equivalent. The ~10Hz rate was never measured, only estimated by the user; E2 replaces the estimate with a measured 0 Hz on the fixed code. Trigger still unidentified for the 20/11 liquid-mode incident.
- [ ] 2.2.3 I11: Ong bat tat computer-use vi nhay ngua mat (19:13). BLOCKED 21/11 15:35 (Worker J): animated-backdrop test cannot run. hyprglass NOT loaded (only hyprbars), NOT in hyprland.conf, .so only in backups. Test needs loading a backup plugin into the live compositor, risks crashing Hyprland while he works. Needs a dedicated test window with his handover or a login-time plugin config decision. Indicator proven NOT to repaint at idle 3 times (122 windows 0 callbacks, 3 min 0 commits, deployed binary 3 windows 0). E1 logging ready to capture any recurrence. QUYET DINH DA SOAN 21/11 17:52 (Worker X): docs/decision-2-2-3-hyprglass-test-20261121.md, 4 phuong an A/B/C/D (A handover 30 phut load live, B them vao hyprland.conf roi reboot, C Hyprland long nhau cach ly, D bo qua tai hien giam sat bang log). File .so da xac minh lai chi con trong backup (full-1791544423/native/hyprglass.so, sync-20261116-.../trees/native/hyprglass.so). De xuat: thu C truoc, neu khong duoc thi A hoac D, khong khuyen B. Ong chi can noi chu cai. Da ghi vao docs/pending-user-decisions.md muc 2. QUYET DINH 18:24 (sua: ban tom tat truoc ghi nham 18:16; memory 1605/1608/1713 xac nhan 18:24): ong chon C (Hyprland long nhau cach ly). Y6c NO VERDICT (F0 --socket/--wayland-fd, F1 hyprglass ABI chet .so.14/.so.4, U5b gate grep sai log, 5a2b69d); Y6d launcher v3 + C2 ALL PASS (72eb8ad); Y6e rebuild .so 34MB ldd 0 not found + nested LOAD TEST PASS 21:57 (915121d, hyprglass active true versionCheck match, live 1515 untouched); Y6r AMEND nhat tri (6239298 + b53a593): profile DA ap dung (config() parse 2, layers.enabled true), khong manual reload, conf y6e chua stage lam conf chinh nen retry chet o ldd pre-flight; fix A1-A10 + re-review moi truoc khi retry; pill measurement van CHUA chung minh. Xem 4.13.
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

Worker L follow-up (21/11): Phase 3 function-based tests were not collected by `unittest discover`; added `load_tests` adapters and a loader self-test. Stale 90s assertions in C1 coverage (including act diagnostics) now follow `cu.OBSERVATION_MAX_AGE` (120s).

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
- [ ] 3.4.1 E1: Tach ban bac (nhieu agent) khoi thuc thi (1 agent). Thu nghiem: co tang toc do, tang chinh xac khong? THI NGHIEM DANG DO, CHUA CO KET LUAN (Worker X-E1, 21/11 18:07, commit cad1543): task test-05-contact-book (28 buoc). Deliberation xong va do duoc: 3 deliberator song song (fresh codex CLI, moi process rieng, khong nho task), xong trong 8m40s / 7m40s / 4m32s, max song song 8m40s, 0 UNVERIFIED; merge xong ~2 phut thanh 1 plan (58 buoc, 64 JSON command parse duoc, moi id resolve duoc). Ca hai lan chay executor (A truc tiep, B theo plan) deu CHUA DO vi ON HOLD: quy tac moi 17:59 cam lai Zen khi ong dang dung ban phim (vu Y4 cuop focus), va Y4 chua xong. De B thang ve tong thoi gian, lan chay B phai nhanh hon A hon ~10m40s. Plan da merge o /tmp/e1/plan-test-05.md tren laptop, brief + script o /tmp/e1/, chay A truoc roi B, tuan tu. Pre-flight moi: kiem tra tab moi render body visible truoc khi chay (bai hoc vu hidden-body cua Y4). Co che agent: coordinator depth-2 khong co tool spawn subagent nen dung fresh codex CLI process (1 process/agent, khong nho task); Worker X chap nhan vi tinh chat quan trong (doc lap, khong nho chung) van giu nguyen. Bao cao: improvements/worker-x-e1-experiment-report.md, log: improvements/worker-x-e1-experiment-log.md. DONG 21/11 20:26 (Y8b, 0bc1279e + feb3fb7): A BLOCKED (judge 7275171, quoting trap, A1/A2 FAIL), B PASS single-arm (522s, 0/0/0), KHONG co comparative verdict. Fresh comparison DE HOAN, can thiet ke moi + nhan moi + pre-registration moi; neu bao gio chay lai thi chay truoc final test. Xem 4.22. H2 van OPEN (chi co scripted).
- [x] 3.4.2 E2: Firefox automation thay computer-use chup man hinh. DONE 21/11 15:36 (Worker J): answered live. DOM for locate/read, real mouse or Marionette/JS click for action, zen-mcp primary (2-20ms), firefox-mcp + Selenium verified fallbacks with working clicks. BiDi pointer click confirmed broken twice. Full replacement proven on the real task (0.64s, 0 misses).
- [x] 3.4.3 E3: Toi uu toc do 10x. PAUSED, resume sau khi Zen xong. Da ghi lai day du o 4.3 (21/11 07:35, Worker H): 5-10x chi la mong muon, muc tieu la nhanh nhat kha thi, dung chi khi council + redteam nhat tri. Baseline: H1 1974s/1080s vs muc 2 phut; tc02 exec 9.6-9.9s / e2e 13.5-13.8s vs muc 8s/10s.

## PHASE 4 - VIEC CON NO / CHUA XONG (phan F)
- [x] 4.1 Tang blur cho pill overlay them 1 chut (ong dan sau reboot 21/11 02:15). Code DONE (Worker E): blur_strength 0.0 len 0.15. Deploy CHO REBOOT: ban cai dat tren may ong chua co binary moi (relay tat, sync-installed bao broker_unavailable). Tick 21/11 07:35 (Worker H).
- [x] 4.2 Cookie/session research: trinh bay file vm-gmail-sessions-research.md. DONE 21/11 07:35 (Worker H): docs/cookie-session-summary.md. Da kiem chung lai trang ho tro Google ngay 21/11 (van con hieu luc, noi dung khop). Ket luan: khong co phien vinh vien; moi Gmail mot named profile rieng + Gmail connector lam duong chinh + heartbeat moi 3-4 ngay; khong copy cookie tu laptop sang VM.
- [x] 4.3 Speed loop: resume voi coordinator moi, huong click accuracy / screen-model calibration. DOCUMENTED, PAUSED 21/11 07:35 (Worker H): goal test-case-nhanh-g-p-5-10-l-n, cap nhat lan cuoi 18/11 00:48. 5-10x chi la mong muon, muc tieu la nhanh nhat kha thi, do bang tong wall time. Dung chi khi council + redteam nhat tri khong con toi uu duoc nua. Huong click accuracy / calibration da xong o Phase 2.1 (E2: pointer <1px, loi do vision). Resume khi ong quyet + council/redteam hop.
- [x] 4.4 Track 2: PAUSED, chi tiep tuc khi council + redteam nhat tri. DOCUMENTED 21/11 07:35 (Worker H): Track 2 dung nhu mot vong lap tu dong khong gioi han tu 20/11; cong viec da xong van giu nguyen; tiep tuc chi sau khi council + redteam ghi quyet dinh nhat tri.
- [x] 4.5 Pill candidate 2 la default tam, candidate 1 giu lai, ong tu test them. DOCUMENTED 21/11 07:35 (Worker H): candidate 2 (chai hinh tru) default tam, candidate 1 giu lai, ong la nguoi cham mui vi. Ben trong pill can co refraction, nhe hon o vien. Lua chon cuoi can ong tu test, ghi trong docs/pending-user-decisions.md muc 3.
- [x] 4.6 User decisions con no: H1-BASE recovery, Step 3 go/no-go, save-dialog fix Part B, ~/backups ~99 GiB, Omarchy restore steps. DONE 21/11 07:35 (Worker H): da liet ke day du kem mo ta trong docs/pending-user-decisions.md (them reboot, bat lai computer-use, chon pill, 3 tab Calibration Grid E2).
- [ ] 4.7 Zen ket 22:25 (owner-reported): khong bam hay mo duoc bat ky web nao; anh 22:25 (a14e82980194) sidebar thu gon chi con icon, khong thay danh sach tab, trang new-tab/welcome mo; Zen PID 27958 van song. Fix: F3 chan doan (focus/window, retry Marionette) + khoi phuc (restart qua zen-ai wrapper neu ket, verify session restore 28 tab that + bam tab + mo web duoc). DANG LAM (F3).
- [ ] 4.8 Doi workspace nhieu loi rat ki 22:25 (owner-reported). Fix: F3 chan doan qua hyprctl clients/workspaces; ZT kiem tra lai sau khi Zen khoi phuc. DANG LAM (F3 + ZT).
- [ ] 4.9 Doi test gia lap nguoi dung pho thong tren Zen (lenh 22:26): ZT-A viet ~10 kich ban test thuong ngay (composite DOM + CLI + chuot + ban phim, blind: ZT-B chay mu sau khi F3 khoi phuc); loi tim duoc dua vao fix. DANG LAM (ZT-A).
- [ ] 4.10 Marionette session moi fail "browserElement is null" (22:06/22:10/22:12): chan cleanup2 (con 15 tab) va moi live run. Fix: F3 tim goc re (doc source Marionette + crawl) roi fix. DANG LAM (F3).
- [ ] 4.11 Session guardian startup failed (22:15): session khong len, pill/overlay khong bao gio hien. Fix: F1 tim dung cho nem + crawl roi fix tan goc. DANG LAM (F1).
- [ ] 4.12 Tu lenh den click dau tien gan 5 phut (22:11:30 -> 22:17, ban than click 0.31s). Fix: F2 theo huong ong sua 22:21 (khong can noi truoc; NHANH + thao tac LIEN TUC + overlay PHAI HIEN; muc tieu <30s). DANG LAM (F2).
- [ ] 4.13 Y6 A1-A10 + fresh re-review, roi pill measurement retry (2.2.3, hang serial 4). Y6r AMEND nhat tri (6239298 + b53a593): profile DA ap dung (config() parse 2), khong manual reload, conf y6e chua stage lam conf chinh. Fix giay A1-A7/A9-A10 chay lane song song; A8 load-only trial truoc; retry chi sau re-review moi. Gate G-PILL. Ong chon C 18:24.
- [ ] 4.14 Y13 live run + Y14 live run (hang serial 5-6). Y13: sau Y13r2 clear + huong H3 + slot Marionette khoi phuc. Y14: sau Y13, Y14b re-stage tu 1d23532 + fix H2 regex clear. Gate G-RESTORE, G-SINGLE-LIVE, G-HIDDEN, G-H2.
- [ ] 4.15 A1 pilot resume (hang serial 7). Chi sau khi 3 blocker cua clone1 (docs/clone1-a1-pilot-review-20261121.md, 1ddac2d) da sua + tien dieu kien du (lenh viet tay dat ten 12 run-id, broker SOLO, relay verified, Layer-2 probes, checker cross-check). Chromium via CDP, khong Zen.
- [ ] 4.16 Clone2 batch nang (hang serial 9): re-review doc lap diff F1/F2/F3, chi sau khi diff dong bang. Batch nhe (J14 + tu verify batch 5 + J16) chay lane song song P-A.
- [ ] 4.17 Thi nghiem quyet dinh hidden-body + follow-up Y4d/Y7 (hang serial 8, J9). Thiet ke Y4b: htmlClass + rAF tick count tren CUNG tab an tai CUNG phut. Y4d follow-up: shared bootstrap tab khong song qua session (1 session cho ca suite hoac chap nhan tab moi moi test). Y7 follow-up: test-07 restore marker (lo lon nhat), test-09 off-spec bypass note, simulate --all first-crash abort. Gate G-HIDDEN da keo len truoc vao hang 5-6.
- [ ] 4.18 H2 think-time (J10): KHONG run rieng. Instrumentation gap vao Y13/Y14/A1 (G-H2). Todolist 2.3.1 da tick nhung chi la scripted (Y11b, think null); chi co run agent-driven moi dong H2.
- [ ] 4.19 Y1b snippets (hang serial 10, J13). Phase A BLOCK van dung (12-item checklist, chua merge). Probe 10b/10f + 1e/4a phai viet lai truoc khi xet Phase B (chung se PASS ca ban de tan cong). Gate G-Y1B. Trang thai watch Codex PID 184702 chua xac nhan tu ~19:00.
- [ ] 4.20 Scrub email + ten that khoi lich su (hang serial 11, J8). Ke hoach docs/email-history-scrub-plan.md. Chi chay trong cua so yen tinh that su (G-SCRUB: moi push da len, PR #1 xong, khong live run, moi agent duoc bao re-clone); neu khong co thi doi. Email da sach khoi main (1c7d252); ten that 71 dong / 45 file van con.
- [ ] 4.21 Final test (hang serial 12, CUOI CUNG): contest Codeforces doc lap tren nick cua ong, 5 bai qua Polygon, khong quyen Hieu, khong anh huong ai. Ke hoach ~/workspace/cf26-upload/FINAL-TEST-PLAN-20261121.md. Chi chay sau moi viec khac xong.
- [ ] 4.22 E1 fresh comparison, PARKED (de hoan). A BLOCKED, B PASS single-arm, khong comparative verdict (Y8b). Can thiet ke moi + nhan moi + pre-registration moi, budget NEW, replication pair bat buoc. Neu bao gio xep lich that thi chay truoc final test.
- [ ] 4.23 Clone1 no bao cao (J12, lane P-B): docs/clone1-batch23-verification-20261121.md KHONG ton tai + ket qua chay lai Firefox Y10 t05/t09/t10 (dieu 19:27, chua len). Di kem batch 6 clone1 (giao 22:40).
- [ ] 4.24 Batch-3 checker follow-up (J14, lane P-A): Y12 H1-H4 (H1 fix ben: random suffix moi run cho ten moi; H2 assert chi visibility; H3 localStorage chua verify, delivery 6s se fail sai tren poll cap 5s; H4 position chua doc sau Prev/playlist/shuffle/wrap Next) + Y15 follow-up (R1/R2/R3b fix sketch, R5, W1 probe, E5 wart).
- [ ] 4.25 Nguyen nhan dong bang ban phim/chuot 17:59 (J15, thap). Da tu khoi phuc, Y4b chung minh y4c khong gay ra (onset 17:59:13 truoc navigation 17:59:27/33). Chi lam lai neu tai dien.
- [ ] 4.26 PR #1 CONFLICTING tren GitHub (M2/J17, lane P-G). Mo tu 17:40, xung dot file coord, khong xung dot code. Giai xung dot + merge; chan G-SCRUB.
- [ ] 4.27 Commit + push diff F1/F2/F3 ngay (M4/J19, lane P-H, luat D3). F1 co edit chua commit tren scripts/cursor_session.py + cursor_theme.py; F2 co first_action.py chua track. Moi worker commit nho + push ngay khi buoc nho xong.
- [ ] 4.28 Mo menu Omarchy + chuyen workspace bang LENH (J21, ong 22:45). Click truot workspace 1 mo ra Omarchy menu ~22:44; anh 22:44:32 khong thay menu mo nua; log F2/F3 khong ghi cu click, chua xac dinh dua nao. Len: hyprctl dispatch dang hl.dsp; tim lenh launcher chinh xac tu config; KHONG BAO GIO bam chuot vao nut workspace/menu tren bar. CLI truoc, chuot sau cung. Attribution gap vao fix F2/F3 (log moi click).

## PHASE 5 - TEST LAI VA BAO CAO
- [x] 5.1 Test lai toan bo tren task that (upload Polygon hoac task tuong tu), do tong wall time. DONE 21/11 15:36 (Worker J): 0.64s total, 0 misses, 0 slow steps, 15 steps. See docs/final-report-20261121.md section 5.1.
- [x] 5.2 So sanh truoc/sau: toc do nhanh hon bao nhieu lan, ti le bam trung bao nhieu, loi giam bao nhieu. DONE 21/11 15:40 (Worker J): table in docs/final-report-20261121.md section 5.2 with measured numbers only. DOM read 3-28ms vs screenshot+vision seconds; click 100% (13/13 verified) vs 58.6%; upload 11ms vs 70-min block. Honest note: no equal-task before/after wall-time ratio claimed.
- [x] 5.3 Bao cao tong ket cho ong: cai gi fix xong, cai gi con lai, nhanh hon bao nhieu lan. FINAL DONE 21/11 15:40 (Worker J): docs/final-report-20261121.md rewritten as FINAL with all post-reboot measured numbers.
- [x] 5.4 Merge todolist-push vao main. DONE 21/11 15:47 (Worker J): merged into main as 96438bb, pushed, verified via ls-remote. 46/46 tests pass on merged tree. Conflicts resolved: overlay.py/test_overlay.py take main (hardened, holder_id); native/indicator.c unions E1 metrics + label routing + status command; fix-run log keeps both sides + E2 update note. Note: main's overlay.py differs from the deployed copy, redeploy via sync-installed.py owed. SYNC 21/11 17:52 (Worker X): tick nay da co tren main (111/115) nhung file tren todolist-push van ghi cu; dong bo tick sang todolist-push de hai branch khop nhau. Khong phai merge moi.
