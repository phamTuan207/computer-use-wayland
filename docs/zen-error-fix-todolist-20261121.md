# TODO LIST SIEU CHI TIET - Fix toan bo loi trong file tong hop + Zen automation
# Ngay: 21/11/2026. Chu: Pham Tuan.
# Nguon: LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md (phan A-I) + LOI-COMPUTER-USE-TU-LICH-SU-CHAT-20261121.md (I1-I46)
# Nguyen tac: first principles, tim goc sua goc, khong va trieu chung. Khong ep agent theo 1 tu duy, khuyen khich sang tao. Do thoi gian + log moi buoc. Commit nho push nhieu, vai tram commit cung duoc. Mail commit: phamTuan207 (232407559+phamTuan207@users.noreply.github.com).

## PHASE 1 - ZEN DIEU KHIEN DUOC TOI DA (lam truoc, goal hien tai)

### 1.1 Test truc tiep tung tool tren Zen that (Muse tu test, khong phai Codex)
- [ ] 1.1.1 Puppeteer via BiDi: chay code clone1 (tests/puppeteer_bidi.mjs) tren Zen that, list tabs, read DOM, click, type, do thoi gian tung buoc, ghi log
- [ ] 1.1.2 firefox-mcp: chay npx @mozilla/firefox-mcp --connect-existing, list tabs, read DOM, click, type, do thoi gian, ghi log
- [ ] 1.1.3 Selenium + geckodriver: chay code clone2 khi no nop len GitHub, attach --connect-existing, list tabs, read DOM, click, type, do thoi gian
- [ ] 1.1.4 zenpilot / zen-mcp: opencode dang test, lay ket qua, do thoi gian
- [ ] 1.1.5 Playwright moz-firefox: fcc dang test, xac nhan KHONG attach duoc vao Zen dang chay (launch-only), co bang chung cu the

### 1.2 So sanh va chon tool tot nhat
- [ ] 1.2.1 Tong hop ket qua 5 tool: WORKS / PARTIAL / BROKEN, toc do moi action, do chinh xac click, do on dinh
- [ ] 1.2.2 So sanh DOM vs screenshot/mouse: DOM nhanh hon bao nhieu lan, chinh xac hon bao nhieu
- [ ] 1.2.3 De xuat huong dot pha moi neu co: cach nao nhanh hon gap nhieu lan, it loi hon gan nhu khong co loi, du phai viet lai repo
- [ ] 1.2.4 Chon tool tot nhat lam cach dieu khien Zen chinh, viet code tich hop vao computer-use repo

### 1.3 Tich hop va commit
- [ ] 1.3.1 Viet code tich hop tool tot nhat vao computer-use repo, commit nho push nhieu
- [ ] 1.3.2 Test lai tren task that, do tong wall time, so sanh truoc/sau
- [ ] 1.3.3 Cap nhat .desktop Zen + Chromium da xong (02:55 21/11), verify lai sau reboot

## PHASE 2 - FIX LOI MUSE UU TIEN (phan G, H, I - uu tien hon loi Codex)

### 2.1 Bam truot, toa do sai (loi TO NHAT, uu tien so 1)
- [ ] 2.1.1 G12/I6: Hieu chuan toa do theo man hinh ong: ghi chinh xac resolution, scale, Hyprland scale, monitor. Toa do tu observation khong khop toa do thuc, lech sang phai
- [ ] 2.1.2 H3/I1: Nham View trung Remove lien tuc (805,825 trung Remove; 837,850 trung Rejudge). Sua: lay toa do chinh xac tu DOM, khong doan tu anh
- [ ] 2.1.3 I2: Bam Discard thay Continue, suy xoa working copy. Sua: xac nhan nut bang DOM truoc khi bam
- [ ] 2.1.4 I3: Chuot dung yen khong bam duoc Add to Contest. Sua: click bang DOM, khong dung chuot ao
- [ ] 2.1.5 I4: Bam truot link General info may lan, lac ve trang chu. Sua: DOM click
- [ ] 2.1.6 I5: Keo chuot long vong tim nut commit. Sua: tim nut bang DOM, khong keo chuot
- [ ] 2.1.7 I7: Video ong quay chung minh Muse tim nut rat kem. Sua: do ti le bam trung, khong de loi chon trong retry
- [ ] 2.1.8 I8: Test khong do ti le bam trung, loi bi chon trong retry. Sua: moi test phai do hit rate rieng, log wrong-click, gom lai thanh van de chung
- [ ] 2.1.9 G13: Think-observe-think loop chiem 87.8% thoi gian. Sua: 1 observation cho NHIEU action, khong 1 action roi 1 observation
- [ ] 2.1.10 G14: Chong hoc tu: validate tren HELD-OUT cases tu INDEPENDENT subagent, FRESH agent, khong dung baked-in coordinates
- [ ] 2.1.11 B9/I21: Nut Browse bam chinh giua khong nhan, phai hover lech cho nut toi dam roi moi bam. Da co fix, can dua vao code

### 2.2 Overlay nhap nhay lien tuc (uu tien so 2)
- [ ] 2.2.1 H1/I9: Overlay nhap nhay lien tuc khi Muse lai truc tiep, Codex lai thi binh thuong. Nguyen nhan that CHUA XAC MINH. Can dieu tra: pill render loop xung dot screenshot capture? Pill redraw moi lan observe?
- [ ] 2.2.2 I10: Nhay ~10 lan/giay ma khong lam gi ca. Can log thoi gian, tan suat nhap nhay, dieu kien trigger
- [ ] 2.2.3 I11: Ong bat tat computer-use vi nhay ngua mat (19:13). Sua xong moi bat lai
- [ ] 2.2.4 I12: Overlay mat han (15:28). Phien computer-use rot hoac pill tat ma worker khong hay. Sua: watchdog phat hien overlay mat, khoi dong lai
- [ ] 2.2.5 I20: Da bia "chup man hinh qua nhieu gay nhay overlay", da thua nhan sai. Khong bia nua, dieu tra that
- [x] 2.2.6 Overlay hien khi BAT KI agent nao dieu khien may/trinh duyet, khong rieng Muse drive chuot (ong yeu cau 03:28 21/11). DONE 05:00 21/11: scripts/overlay.py (daemon + CLI, refcount, session-aware) + label command in native/indicator.c + docs/overlay.md. Live tested on laptop: pill shows "Muse via BiDi", refcount 2->1->0, idle surface_commits=0. PENDING: sync-installed (relay down, broker_unavailable) so installed copy lacks overlay.py + new binary.

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
- [ ] 3.1.1 C1: Observation het han (90-120 giay). Sua: chup moi truoc khi hanh dong
- [ ] 3.1.2 C2: Sau khi bam dieu huong, anh chup van hien trang cu. Sua: observe lai moi sau moi lan bam dieu huong
- [ ] 3.1.3 C3: Zen Ctrl+N = new tab, Ctrl+T = new window (dao nguoc). Sua: khong bao gio bam Ctrl+T
- [ ] 3.1.4 C4: Link Commit Changes o dau. Sua: link o cuoi cot PHAI, duoi ADDED changes, bam End de toi do
- [ ] 3.1.5 C5: URL /problem/<id> bi 404. Sua: vao qua Dashboard > View Problems > Continue (link BEN TRAI)
- [ ] 3.1.6 C6: Cam dung ydotool. Sua: nhac lai trong MOI brief
- [ ] 3.1.7 C7: Man hinh tinh doc nhu "khong lam gi". Sua: noi truoc va bao log cu the, narrate tung buoc TRUOC khi lam
- [ ] 3.1.8 C8: Khong don dep sau khi dung computer-use. Sua: ket thuc broker session, xac nhan khong con process, pill bien mat, desktop sach

### 3.2 Loi cu the task up de (phan B)
- [ ] 3.2.1 B1: Solution sai extension .c thay vi .cpp. Sua: upload .cpp
- [ ] 3.2.2 B2: Contest code A/B/C thay vi NB1/NB2/NB3. Sua: sua Problem short name
- [ ] 3.2.3 B3: Test trung lap. Sua: xoa test trung, commit lai
- [ ] 3.2.4 B4: Invalid numeration sau khi xoa test, chan tao package. Sua: RENUMBER 1-N sau khi xoa
- [ ] 3.2.5 B5: Dung package cu cho revision moi. Sua: moi revision tao package Standard MOI, tick Verify
- [ ] 3.2.6 B6: Link /p/ bi Codeforces tu choi. Sua: dung link hash-format tu nut copy sidebar
- [ ] 3.2.7 B7: Statement tieng Viet thay vi English. Sua: doi English, xoa statement vietnamese neu co ca hai
- [ ] 3.2.8 B8: Thieu dau $ dong trong Notes. Sua: them $ dong
- [ ] 3.2.9 B10: Codex dung Chromium thay vi Zen. Sua: chi dung ZEN, tab da dang nhap san
- [ ] 3.2.10 B11: Go URL bang phim (key events). Sua: khong go URL bang phim, dung tab da mo san
- [ ] 3.2.11 B12: Test zip co ca answer import gap doi. Sua: dung zip chi co input
- [ ] 3.2.12 B13: Thieu test sau khi import (29 thay vi 30). Sua: them test thieu thu cong
- [ ] 3.2.13 B14: Verification failed khong phai luat dung. Sua: chi loi numeration moi chan package

### 3.3 Loi quy trinh / giao tiep (phan D)
- [ ] 3.3.1 D1: Kenh chat lan lon. Sua: follow-up thuoc thread nao gui TRONG thread do
- [ ] 3.3.2 D2: Khong doc Messenger qua connector. Sua: kiem tra qua connector, khong mo Messenger tren trinh duyet laptop
- [ ] 3.3.3 D3: Khong push len GitHub ngay. Sua: push ngay khi lam/sua xong, khong giu lai
- [ ] 3.3.4 D4: Khong ghi bai hoc vao ca hai noi. Sua: generic vao repo, chi tiet vao laptop, khong lo thong tin ca nhan
- [ ] 3.3.5 D5: Khong kiem tra toan bo ngay truoc khi sua lich. Sua: doc TOAN BO ngay tren TAT CA calendar, chay audit overlaps, 0 overlap

### 3.4 Huong giai phap tong quat (phan E)
- [ ] 3.4.1 E1: Tach ban bac (nhieu agent) khoi thuc thi (1 agent). Thu nghiem: co tang toc do, tang chinh xac khong?
- [ ] 3.4.2 E2: Firefox automation thay computer-use chup man hinh. Dang lam o Phase 1
- [ ] 3.4.3 E3: Toi uu toc do 10x. PAUSED, resume sau khi Zen xong

## PHASE 4 - VIEC CON NO / CHUA XONG (phan F)
- [ ] 4.1 Tang blur cho pill overlay them 1 chut (ong dan sau reboot 21/11 02:15)
- [ ] 4.2 Cookie/session research: trinh bay file vm-gmail-sessions-research.md
- [ ] 4.3 Speed loop: resume voi coordinator moi, huong click accuracy / screen-model calibration
- [ ] 4.4 Track 2: PAUSED, chi tiep tuc khi council + redteam nhat tri
- [ ] 4.5 Pill candidate 2 la default tam, candidate 1 giu lai, ong tu test them
- [ ] 4.6 User decisions con no: H1-BASE recovery, Step 3 go/no-go, save-dialog fix Part B, ~/backups ~99 GiB, Omarchy restore steps

## PHASE 5 - TEST LAI VA BAO CAO
- [ ] 5.1 Test lai toan bo tren task that (upload Polygon hoac task tuong tu), do tong wall time
- [ ] 5.2 So sanh truoc/sau: toc do nhanh hon bao nhieu lan, ti le bam trung bao nhieu, loi giam bao nhieu
- [ ] 5.3 Bao cao tong ket cho ong: cai gi fix xong, cai gi con lai, nhanh hon bao nhieu lan
