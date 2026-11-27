# Bao cao tong ket: Zen dieu khien toi da + fix toan bo loi

**BAN CUOI, ngay 21/11/2026.** Ong da reboot luc 15:19. Tat ca test can reboot da chay xong
tru 1 muc (2.2.3 backdrop dong, bi chan vi can nap plugin thu nghiem vao compositor dang
chay cua ong). Moi so lieu trong bao cao nay la so do that, khong uoc luong, khong suy so.

## Trang thai chung

- Todo list: 115 muc. Da xong 103 muc truoc khi reboot, them 11 muc sau reboot, con lai
  1 muc BLOCKED (2.2.3), 2 muc PARTIAL/UNMEASURABLE (2.1.7, 2.1.10), 3 muc huong chung
  E1-E3 (E1 chua thu nghiem, E2 da tra loi, E3 PAUSED).
- Branch `todolist-push` se merge vao main sau bao cao nay (muc 6).
- Khong co thong tin ca nhan nao cua ong duoc push len GitHub. Tat ca commit dung mail
  the owner (GitHub noreply).

## Phase 1: Zen dieu khien toi da

Ket qua test truc tiep 5 tool tren Zen that (so lieu that, khong uoc luong):

| Tool | Ket qua | Doc DOM | Click | Toc do |
|---|---|---|---|---|
| zen-mcp 1.2.3 | WORKS | 3-5ms | 2-3ms, works | 2-20ms moi action |
| zenpilot 0.7.0 | WORKS | - | works | 439-478ms moi action |
| Selenium + geckodriver | WORKS headless VA live Zen | 31ms | 63ms, verified live Zen | 0.7-122ms |
| Puppeteer via BiDi | PARTIAL | 4-28ms | FAILED, counter 0 (2 lan, truoc va sau reboot) | connect 54-121ms |
| Playwright | BROKEN | khong attach duoc | - | - |
| firefox-mcp 0.11.0 | WORKS | snapshot 14-15ms | 33-59ms, VERIFIED counter 0 len 1 | 3-154ms moi action |

Ket luan chon: chinh la **zen-mcp 1.2.3** (nhanh nhat, click chay duoc tren Zen that).
Du phong co click da chung minh: firefox-mcp 0.11.0 (click_by_uid kich hoat handler that)
va Selenium tren Zen that (11/11 buoc, 0.278s). Click tren Zen that: lay rect tu DOM roi
bam bang chuot that (hybrid), hoac dung JS click / Marionette click. Khong dung Puppeteer
BiDi pointer click: no that bai 2 lan (truoc reboot 04:49 va sau reboot 15:24-15:25),
counter van 0, trong khi evaluate el.click() chay duoc 7-12ms va page.mouse.click cung
khong tang counter.

Phat hien lon nhat: **gioi han session dung chung giua BiDi va Marionette, chi 1 session
TOTAL cho moi Zen**. Mot node test treo 1h51m lam leak session, chan ca BiDi lan Marionette.
Chi reboot moi xoa duoc. Moi client bat buoc phai goi session.delete trong finally.
Code tich hop: scripts/zen_dom.py (single session manager, file lock, kill-hung watchdog).

Da chung minh sau reboot (Worker J, 15:21-15:36 ngay 21/11):
- 1.1.1 Puppeteer click test lai: connect 54ms, new tab 48ms, goto 73ms, read 28ms.
  v1 page.click counter 0 (81ms) FAIL, v2 evaluate counter 1 (12ms) WORKS,
  v3 page.mouse.click counter van 1 (8ms) FAIL. Reboot KHONG sua duoc BiDi click.
- 1.1.2 firefox-mcp: install 3.37s, version 0.11.0, Marionette 2828 dang nghe.
  initialize 100-104ms, 36 tool (basic preset; list_console_messages can developer
  preset). list_pages 1594ms, new_page 105-154ms, snapshot 14-15ms, click_by_uid
  33-59ms, counter 0 len 1 VERIFIED bang evaluate_script, fill 38ms (verified
  "mcp-test"), screenshot 22ms 16.6KB, close 56ms. Tong 417ms cho ca flow.
- 1.1.3 Selenium tren Zen that: FULL PASS 11/11 buoc, tong 0.278s. maximize
  1863x1176 (viewport that, khong 0x0 nhu temp Zen), type 21ms verified, click
  63ms verified "clicked:zen marionette test", delete session xong, Zen van song.
- 1.3.3 .desktop verify: zen.desktop co du co --remote-debugging-port=9222
  --marionette tren tat ca Exec, Zen sau reboot chay PID 11292 voi dung co do.

## Phase 2: loi Muse, uu tien cao nhat

### 2.1 Bam truot, toa do sai (loi lon nhat)

Ket qua quyet dinh tu thi nghiem calibration E2 (chay that tren man hinh ong, 04:36-05:30
ngay 21/11, 29 diem biet truoc):
- Pointer chinh xac tuyet doi: 29/29 click, sai so 0.5-0.9 px, 0 lan tu choi.
- Ti le trung lan dau: 17/29 = 58.6%, dung y nhu du doan tu vision (17/29).
- Moi lan truot deu do vision grounding doc sai anh: loi khung hinh khoang 1.10x theo truc x,
  tuong quan loi voi x la 0.973. Truc y gan nhu chinh xac.
- Chuyen "ti le man hinh 1.55x" la SAI. Man hinh ong 1920x1200, scale 1, logical bang physical.
- Huong fix: lay toa do chinh xac tu DOM, khong bao gio doan pixel tu anh chup.

Trang thai: 2.1.1 va 2.1.2 DONE (live). 2.1.3-2.1.6, 2.1.8, 2.1.9, 2.1.11 DONE o muc
offline fixture, live proof van no. 2.1.7 KHONG DO DUOC (khong co file video trong workspace,
khong suy so tu loi ke). 2.1.10 con PARTIAL (held-out tong hop pass, validation tren app moi
that va chay lai boi agent doc lap van no).

Luu y trung thuc: Worker A2 bao da tick 9/11 muc 2.1 vao todo list, nhung kiem tra lai commit
b876ee1 thi khong cham vao file todo list. Worker H da tick lai dua tren bang chung trong
docs/calibration-e2-report.md.

### 2.2 Overlay nhap nhay

- Indicator da sua KHONG ve lai khi idle: do that 3 lan.
  Lan 1 (Worker G, 06:58-07:01): 122 cua so 1 giay, max idle paint callbacks 0,
  max commits 2, 0 event trong 60 giay idle, 32/32 khung hinh pill giong het nhau.
  Lan 2 (overlay worker, 3 phut): 0 lan ve lai, 0 lan commit.
  Lan 3 (Worker J, 15:33, binary moi sau deploy): 3 cua so 1 giay lien tiep paint 0,
  commits 0, idle 0; chi co 2 paints/2 commits o cua so release (chinh la lenh hide).
- Khong co duong code nao trong repo gay nhap nhay 10Hz khi idle (redteam worker4 da
  chung minh). Nguyen nhan kha nang nhat con lai: vong lap ve lai cua compositor/plugin
  khi backdrop dong o che do LIQUID.
- Da them: log tung event, retry co gioi han, daemon tu khoi dong lai indicator chet (fix I12).
- H1 da sua trong file LOI: nhap nhay xay ra khi Muse lai truc tiep, khong phai Codex.
- 2.2.3 BLOCKED: test backdrop dong khong chay duoc. hyprglass KHONG load trong session
  hien tai (chi co hyprbars), KHONG co trong hyprland.conf, file .so chi co trong backup.
  Test can nap plugin thu nghiem vao compositor dang chay cua ong, co nguy co crash
  Hyprland luc ong dang lam viec. Can cua so test rieng khi ong giao may, hoac quyet dinh
  cau hinh plugin luc login cua ong. Log E1 da san sang ghi lai neu no tai phat.

### 2.2.6 Overlay luon bat (ong yeu cau rieng)

Da xong, test that, va DA DEPLOY:
- scripts/overlay.py (daemon + CLI, dem so nguoi giu, hien ten agent + cach dieu khien,
  vi du "Muse via BiDi"). Test 04:56-05:00: giu 2 nguoi thi pill van hien, tha het thi
  pill tat, desktop sach, khong cham tab nao cua ong.
- Deploy 15:28-15:31 ngay 21/11: sync-installed.py lan 1 loi vi thieu native/visuals.json
  (file generated, khong co trong repo; hash profile doi vi blur 0.15). Sua bang cach copy
  manifest da cai vao repo roi chay scripts/refresh-visuals-manifest.py (profile hash
  khop 9a151634...). Lan 2 THANH CONG: "Installed sync published and verified",
  314 file, --check exit 0. Binary moi 50320 bytes, lua blur_strength = 0.15.
  Kiem chung tu ban cai dat: acquire/release chay duoc, label "Worker J via BiDi".

### 2.3-2.8

Da xong truoc dot nay (Worker D, Worker E): 22 muc 2.3-2.5, 25 muc 2.6-2.8. Bao gom
scripts/timing.py + step_watchdog.py (log thoi gian luon bat), observation limit 90s len
120s, fix driver bug rot session, scripts/drive_log.py (log drive truc tiep), scripts/vm_proxy.py,
hover action trong cu.py, pill blur 0.0 len 0.15 (code xong, DA DEPLOY).

## Phase 3: loi Codex va loi he thong

26/26 muc xong (Worker F, 06:37-08:00 ngay 21/11). 35 test Phase 3 deu pass.

- C1: gioi han 120s da co san, chung minh bang 4 test.
- C2: them settle 400ms chup lai sau khi bam dieu huong, giu khung moi nhat.
- C3: chan Ctrl+T khi cua so dich la Zen, kiem chung that class cua so la `zen`.
- C4/C5: ghi ro vi tri link Commit Changes va duong vao problem khong 404.
- C6: mau brief chuan + script kiem tra tu dong (16 quy tac luon dung + 8 quy tac Polygon).
- C7: quy tac noi truoc khi lam, kem timing/log/watchdog/overlay.
- C8: script session_cleanup.py kiem tra va don sach sau khi dung.
- B1-B14: runbook up Polygon day du theo workflow cua Hieu + script kiem tra offline.
  Kiem tra that voi 3 de CF26: ca 3 pass B1/B2/B4/B7/B8/B13; script phat hien dung loi B12
  trong ca 3 file zip goc (co file .a) va tim ra 1 test trung nhau that o vi tri 21 va 28
  trong de P2.
- D1-D5: ca 5 quy tac quy trinh da co trong mau brief va checklist.

Con can chung minh bang test that (chua lam duoc vi relay tat / ong dang ngu): thoi gian
settle C2 tren trang load cham, C3 chan that mot lan bam Ctrl+T vao Zen, polygon_checks.py
tren de moi that, session_cleanup.py --check sau mot session that.

## Phase 4: viec con no

- 4.1 Tang blur pill: code xong (0.0 len 0.15, Worker E), DA DEPLOY 15:31 ngay 21/11.
- 4.2 Cookie/session research: DA TRINH BAY, docs/cookie-session-summary.md.
  Ket luan: khong co phien vinh vien; moi Gmail mot named profile rieng + Gmail connector
  lam duong chinh + heartbeat moi 3-4 ngay; khong copy cookie tu laptop sang VM.
- 4.3 Speed loop: PAUSED theo quyet dinh cua ong. 5-10x chi la mong muon, muc tieu la nhanh
  nhat kha thi, do bang tong wall time. Dung chi khi council + redteam nhat tri khong con
  toi uu duoc nua. Baseline da biet: task H1 1974 giay (OPT) / 1080 giay (BASE) so voi muc
  2 phut; tc02 exec 9.6-9.9 giay / e2e 13.5-13.8 giay so voi muc 8 giay / 10 giay.
- 4.4 Track 2: PAUSED, chi tiep tuc khi council + redteam ghi quyet dinh nhat tri.
- 4.5 Pill candidate: candidate 2 la default tam, candidate 1 giu lai, ong la nguoi cham.
  Ben trong pill can co refraction, nhe hon o vien.
- 4.6 Quyet dinh con no cua ong: da liet ke day du trong docs/pending-user-decisions.md
  (reboot, bat lai computer-use, chon pill, H1-BASE recovery, Step 3 go/no-go, save-dialog
  Part B, xoa ~/backups ~99 GiB, Omarchy restore steps, 3 tab Calibration Grid E2).

## Phase 5: test lai va bao cao

### 5.1 Test lai tren task that (1.3.2) - DA CHAY, PASS

Task: tao problem qua form 3 buoc mo phong flow up de Polygon (tests/fixtures/
problem-create-fixture.html): dien 4 truong, next step, dien statement + chon checker,
next step, upload zip test (3 file), doi points, submit, kiem chung ket qua. Driver:
firefox-mcp (duong DOM-first), moi action deu kiem chung lai trang thai DOM sau khi lam.
Chay 15:36 ngay 21/11, tren Zen that cua ong, tab moi (khong cham tab cua ong), dong tab
sau khi xong.

Ket qua: **tong 0.64 giay, 0 lan bam truot, 0 buoc cham, 15 buoc, EXIT 0.**
- initialize 106ms, new_page 58ms, dismiss alert cu 217ms.
- 7 fill: 10-32ms moi cai, tat ca verified bang DOM read-back.
- 3 click: 8-15ms moi cai, tat ca verified (step chuyen dung).
- Upload zip: 11ms, "problem-tests.zip (443 bytes)" hien dung. Day la cho tung ket
  70 phut trong task up de hom 20/11, gio 11ms.
- Verify ket qua: Title, Short name, Checker lcmp, Archive, Points 20, tat ca dung.
- Lan chay 1 that bai 10/10 miss vi needle sai (tim theo HTML id, snapshot chi co label
  text) + alert cu chua dismiss. Da sua needle theo label text va dismiss dialog dau
  run, lan 2 pass 0 miss. Loi la o script test cua toi, khong phai o driver.

### 5.2 So sanh truoc/sau (tong wall time)

| Chi so | Truoc (vong lap cu) | Sau (DOM-first) | Nguon so |
|---|---|---|---|
| Doc trang thai | vai giay moi observation (screenshot + vision) | 3-28ms (DOM read / snapshot) | do that 21/11 |
| Click | 58.6% trung lan dau (17/29), truot do vision | 100% (13/13 action co verify, 0 miss) | E2 + real task |
| Upload file | ket 70 phut (file picker) | 11ms (upload_file_by_uid) | 20/11 + 21/11 |
| Mot task 3 buoc, 13 action | khong co baseline tuong duong | 0.64 giay tong | real task 21/11 |
| Click BiDi | that bai (counter 0) | van that bai, dung firefox-mcp/Selenium thay | 2 lan test |
| Click firefox-mcp | chua test | 33-59ms, verified | 21/11 |
| Click Selenium live Zen | chua test | 63ms, verified | 21/11 |

Luu y trung thuc ve so sanh: task up de that hom 20/11 mat ~11 tieng khong phai baseline
cong bang cho fixture 0.64 giay (task that lon hon nhieu, co site that, cho nguoi, sua loi).
So sanh cong bang nhat la chi phi moi action: DOM read 3-28ms so voi screenshot + vision
vai giay, va ti le trung 100% so voi 58.6%. Khong phong dai thanh "nhanh hon X lan" tong the
khi chua co cung mot task chay ca hai vong lap.

### 5.3 Bao cao nay la ban cuoi cua 5.3

## Cac commit chinh (branch todolist-push)

- 28a4b62: todo list sieu chi tiet (5 phase, 80+ muc).
- 4e52731: verdict redteam council.
- 6d4f164, dde13ee, 3eebe66, 5481f96, 5f30e4c: overlay luon bat (scripts/overlay.py).
- b876ee1, c2d41a3, a1ce11d, 407d1f1: calibration E2 Phase 2.1.
- 40c68f9, f1797e3: overlay flicker E1 + so sanh 5 tool + scripts/zen_dom.py.
- ceff51c, 6be6784, 92944da, aa114b2, 2f0510d, 8636f21, fa89ff1, 0f520d2: Phase 3.
- 4ac943c, 2555fbb: Phase 4 + 5 (cookie summary, pending decisions, final report DRAFT).
- Worker J sau reboot: f6cf8c7, a791100 (BiDi click re-test), c4f1376, ac91663, b0c17ac
  (firefox-mcp live test + verify), 83357ed (real-task fixture + driver),
  3e6eb74, bdda9a6, e9a9753 (merge worker-k), cbbbd24 (fix real-task needles).
- Worker K (fcc, song song): b99ac2a, 4daa4c2, a5d0849 (10 realistic test cases).

## Con lai sau dot nay

1. 2.2.3 backdrop dong: BLOCKED, can cua so test rieng khi ong giao may hoac quyet dinh
   cau hinh plugin luc login.
2. 2.1.7 (video hit rate): UNMEASURABLE, khong co file video trong workspace.
3. 2.1.10: PARTIAL, validation tren app moi that va chay lai boi agent doc lap van no.
4. Cac quyet dinh trong docs/pending-user-decisions.md chi ong moi tra loi duoc.
5. E1 (tach ban bac khoi thuc thi) chua thu nghiem; E3 (10x) PAUSED.
6. Merge todolist-push vao main (5.2, 5.4): thuc hien sau bao cao nay.
