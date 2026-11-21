# Bao cao tong ket: Zen dieu khien toi da + fix toan bo loi

**BAN NHAP, ngay 21/11/2026.** Chua phai ban cuoi: cac test can reboot van chua chay duoc,
nen phan so sanh truoc/sau ve tong wall time van thieu so lieu thuc te. Sau khi ong reboot
va chay xong 1.3.2, bao cao nay se cap nhat thanh ban cuoi.

## Trang thai chung

- Todo list: 114 muc. Da xong 86 muc truoc khi Worker H bat dau, them 11 muc trong dot nay,
  con lai chu yeu la cac muc bi BLOCKED cho den khi reboot va 3 muc huong chung E1-E3.
- Branch `todolist-push` hon `main` 71 commit. Merge vao main chua thuc hien trong dot nay
  (xem muc 6, ly do ghi ro).
- Khong co thong tin ca nhan nao cua ong duoc push len GitHub. Tat ca commit dung mail
  phamTuan207 (GitHub noreply).

## Phase 1: Zen dieu khien toi da

Ket qua test truc tiep 5 tool tren Zen that (so lieu that, khong uoc luong):

| Tool | Ket qua | Doc DOM | Click | Toc do |
|---|---|---|---|---|
| zen-mcp 1.2.3 | WORKS | 3-5ms | 2-3ms, works | 2-20ms moi action |
| zenpilot 0.7.0 | WORKS | - | works | 439-478ms moi action |
| Selenium + geckodriver | WORKS headless, PARTIAL windowed | 14ms | 66ms, verified headless | 1-80ms |
| Puppeteer via BiDi | PARTIAL | 4ms | FAILED, counter 0 | connect 109ms |
| Playwright | BROKEN | khong attach duoc | - | - |
| firefox-mcp | CHUA TEST | bi chan boi session leak | - | - |

Ket luan chon: chinh la **zen-mcp 1.2.3** (nhanh nhat, click chay duoc tren Zen that).
Fallback la Selenium headless. Click tren Zen that: lay rect tu DOM roi bam bang chuot
that (hybrid), khong tin DOM click vi no khong kich hoat duoc handler nhu chuot that
(Puppeteer BiDi click that bai ngay 21/11 04:49, counter van 0).

Phat hien lon nhat: **gioi han session dung chung giua BiDi va Marionette, chi 1 session
TOTAL cho moi Zen**. Mot node test treo 1h51m lam leak session, chan ca BiDi lan Marionette.
Chi reboot moi xoa duoc. Moi client bat buoc phai goi session.delete trong finally.
Code tich hop: scripts/zen_dom.py (single session manager, file lock, kill-hung watchdog).

Con BLOCKED cho den khi reboot: 1.1.1 (Puppeteer click test lai), 1.1.2 (firefox-mcp),
1.1.3 (Selenium tren Zen that), 1.3.2 (test lai tren task that, do wall time), 1.3.3
(verify .desktop sau reboot).

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
docs/calibration-e2-report.md trong dot nay.

### 2.2 Overlay nhap nhay

- Indicator da sua KHONG ve lai khi idle: do that 06:58-07:01 ngay 21/11, 122 cua so 1 giay,
  max idle paint callbacks 0, max commits 2, 0 event trong 60 giay idle, 32/32 khung hinh
  pill giong het nhau (white_px 9768 o 31/32 khung). Khong co duong code nao trong repo gay
  nhap nhay 10Hz khi idle (redteam worker4 da chung minh).
- Nguyen nhan kha nang nhat con lai: vong lap ve lai cua compositor/plugin khi backdrop dong
  o che do LIQUID. Chua test duoc vi hyprglass khong load trong session hien tai; can reboot.
- Da them: log tung event, retry co gioi han, daemon tu khoi dong lai indicator chet (fix I12).
- H1 da sua trong file LOI: nhap nhay xay ra khi Muse lai truc tiep, khong phai Codex.

### 2.2.6 Overlay luon bat (ong yeu cau rieng)

Da xong va test that tren may ong 04:56-05:00 ngay 21/11: scripts/overlay.py (daemon + CLI,
dem so nguoi giu, hien ten agent + cach dieu khien, vi du "Muse via BiDi"). Test: giu 2 nguoi
thi pill van hien, tha het thi pill tat, desktop sach, khong cham tab nao cua ong. Do idle
3 phut: 0 lan ve lai, 0 lan commit.

CHUA DEPLOY: ban cai dat tren may ong chua co overlay.py va binary moi, vi relay dang tat
(sync-installed.py bao broker_unavailable). Can reboot roi chay sync-installed.py.

### 2.3-2.8

Da xong truoc dot nay (Worker D, Worker E): 22 muc 2.3-2.5, 25 muc 2.6-2.8. Bao gom
scripts/timing.py + step_watchdog.py (log thoi gian luon bat), observation limit 90s len
120s, fix driver bug rot session, scripts/drive_log.py (log drive truc tiep), scripts/vm_proxy.py,
hover action trong cu.py, pill blur 0.0 len 0.15 (code xong, deploy cho reboot).

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

- 4.1 Tang blur pill: code xong (0.0 len 0.15, Worker E), deploy cho reboot.
- 4.2 Cookie/session research: DA TRINH BAY trong dot nay, docs/cookie-session-summary.md.
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

- 5.1 Test lai tren task that: BLOCKED, can session tren Zen that, chi het leak sau reboot.
  Chay dau tien sau khi ong reboot.
- 5.2 So sanh truoc/sau: CHUA CO so lieu tong wall time that, vi test 5.1 chua chay duoc.
  Nhung gi do duoc den nay:
  - Doc DOM: 3-14ms. Observe anh + vision: vai giay moi vong. Vong lap think-observe chiem
    87.8% thoi gian task (theo review 10x). DOM nhanh hon hang tram lan cho viec doc trang thai.
  - Dinh vi DOM: chinh xac tuyet doi (rect that). Vision grounding: 58.6% (17/29) tren
    luoi diem biet truoc.
  - Pointer: sai so 0.5-0.9 px, 29/29 lan.
  - Click zen-mcp: 2-3ms, chay duoc. Click BiDi: that bai (counter 0). Click Marionette
    headless: 66ms, chay duoc. Click Marionette tren Zen cua so: that bai (viewport 0x0).
  - Phase 3: 35/35 test pass. Phase 2.1: 9/11 muc xong (2 muc partial).
  - So sanh tong wall time truoc/sau se co sau khi chay 5.1. Khong suy so truoc.
- 5.3 Bao cao nay la BAN NHAP cua 5.3. Ban cuoi sau khi chay xong 5.1 va 5.2.

## Cac commit chinh (branch todolist-push)

- 28a4b62: todo list sieu chi tiet (5 phase, 80+ muc).
- 4e52731: verdict redteam council.
- 6d4f164, dde13ee, 3eebe66, 5481f96, 5f30e4c: overlay luon bat (scripts/overlay.py).
- b876ee1, c2d41a3, a1ce11d, 407d1f1: calibration E2 Phase 2.1.
- 40c68f9, f1797e3: overlay flicker E1 + so sanh 5 tool + scripts/zen_dom.py.
- ceff51c, 6be6784, 92944da, aa114b2, 2f0510d, 8636f21, fa89ff1, 0f520d2: Phase 3.
- Worker D: Phase 2.3, 2.4, 2.5 (22 muc). Worker E: Phase 2.6, 2.7, 2.8 (25 muc).

## Con lai sau dot nay

1. Ong reboot (mo khoa 8 viec: 1.1.1, 1.1.2, 1.1.3, 1.3.2, 1.3.3, deploy pill blur,
   deploy overlay, E2 phase B backdrop dong).
2. Chay 1.3.2 tren task that, do tong wall time, cap nhat bao cao nay thanh ban cuoi.
3. Merge todolist-push vao main sau khi test 1.3.2 pass.
4. Cac quyet dinh trong docs/pending-user-decisions.md chi ong moi tra loi duoc.
5. E1 (tach ban bac khoi thuc thi) chua thu nghiem; E2 (Firefox automation) da tra loi ve
   nguyen tac qua Phase 1, chung minh live con no sau reboot; E3 (10x) PAUSED.
