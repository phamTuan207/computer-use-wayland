# Khoa dap an rung 3, ma lan chay R3-L1 (frozen)

- Run code: R3-L1. Danh sach: docs/rung3-list-100-tasks.md, nhanh todolist-push, commit 01dd3b981b551001679bd4deec3d3c954673e768.
- List sha256: 47cbb3a1adbb9cb721c02c9ccca0a4e5007005a4a667f405935bc582463feea1 (55 task, trinh duyet 35, desktop 20; trung binh 37, kho 11, rat kho 7).
- Key file nay dong bang truoc task 1. Sau task 1, moi thay doi khoa dap an hoac muc 6, muc 8 cua danh sach deu huy bo lan chay: ma lan chay moi, chay lai tu task 1. Khoa khong bao gio duoc sua giua lan chay. Neu khoa bi chung minh la sai giua lan chay, task do ghi vo hieu, ap dung quy tac du phong.
- Chuan pass: 53/55. Chu so huu xac nhan qua lenh blanket 19:06 ngay 2026-11-23.
- Moc san do kho: kho cong rat kho it nhat 30 phan tram, rat kho it nhat 10 phan tram. Hien trang: kho cong rat kho 18/55 (32,7 phan tram), rat kho 7/55 (12,7 phan tram). Dat moc.
- Muc tran terminal desktop: toi da 70 phan tram. Hien trang: 13/20 (65 phan tram). Trong tran.
- Muc tran vo hieu: toi da 5 tong, toi da 2 moi nhom do kho. Qua 5 thi rung 3 tinh la benchmark moi.
- Dem cap phat (recount cho ban 55 task): 39 lan xuat hien cum "cap phat" trong 55 than task o muc 6 (37 lan) cong 4 than du phong o muc 8 (2 lan, ca 2 o DP-02). Con so 76 o muc 4 la cua ban 82 task, khong dung cho ban nay.
- Nguoi chay chi doc muc 6 cua danh sach, khong bao gio doc muc 8 va khong bao gio doc file khoa nay. Hash sha256 cua ca 2 file khoa (md va json) ghi vao ~/thu-tu-chay.txt va gui cho chu so huu. Moi nguoi cham kiem tra hash truoc khi cham tung task va ghi hash vao ban cham co chu ky.
- Khong co thong tin ca nhan trong file nay. Khong dung dau gach ngang dai.

## Ruling da chot truoc khi chay

- R3-082: dung omacalc (gnome-calculator khong co tren laptop). Tinh tung buoc, tu xu ly thu tu uu tien (khong dung ngoac, khong dung che do khoa hoc). Ket qua ky vong: 71, 78, 120, 89, 25. Bang viet trong nano. Ngay ruling: 2026-11-23.
- R3-013: mau 3 dang escaped duoc dong bang trong key file: \d{2}\/\d{2}\/\d{4}. Dau / la delimiter o regex101 JS flavor nen dang khong escaped bao loi. Checker chap nhan ca 2 dang (\/ duoc chuan hoa thanh / khi so sanh), nhung dang escaped la dang chuan trong key.
- DP-05: chuyen sang sqlite3 (co san tren laptop tai /usr/bin/sqlite3). Cung bang, cung du lieu, cung truy van nhu muc 8. R3-021 van dung sqliteonline.com. Quyet dinh cua dieu phoi vien truoc task 1, ngay 2026-11-23. Viec chuyen nay boi ro rui ro dich vu chung: neu sqliteonline.com sap, R3-021 vo hieu nhung DP-05 van chay duoc tren sqlite3.
- DP-03: N = 5. Lay 5 cong dau co ten tien trinh hien du theo thu tu cong tang dan, do ngay 2026-11-23 19:20, luc do co 9 cong. N toi thieu 3. Nguoi cham doi chieu bao cao voi file ss-output.txt da luu luc chay, khong doi chieu voi danh sach cong o day.
- R3-009: 2 URL https://www.bbc.com/ va https://en.wikipedia.org/wiki/Main_Page, moi trang it nhat 1 loi. Ngay kiem tra URL: 2026-11-23 (chi kiem tra wave.webaim.org tra ve bao cao; so loi WAVE day du cua tung URL van can kiem tra bang trinh duyet truoc task 1. Neu URL nao co 0 loi thi thay URL truoc khi chay va ghi vao day truoc task 1).
- R3-019: tuyen Ha Noi den Ho Chi Minh. Ngay 1 = ngay chay + 30 ngay, ngay 2 = ngay chay + 37 ngay. Ngay cu the chi chot khi ngay chay duoc dat.
- R3-011: ung vien vo hieu truoc khi chay. timeanddate.com van bi chan o muc curl (HTTP 403, trang Cloudflare "Just a moment...", kiem tra 2026-11-23 19:23). Can xac nhan bang trinh duyet that truoc task 1. Neu tuyen bo vo hieu truoc task 1, du phong ap dung: du phong trung binh dau tien chua dung la DP-01.
- R3-073: khong ap dung cho ban 55 task (task da loai ngay 2026-11-23). Khong can guard timer.
- R3-085: khung tham chieu ~/rung3/r3-085-khung-tham-chieu.png, sha256 de410f94b2192e553f4a78ff42df8bcfd84e29e5908c3f02775125cfa4c759c2, trich bang ffmpeg -ss 00:10 tu ~/rung3/nd26-video.mp4 (640x360, 30 fps, 15 giay, sha256 2e9d8103ffe6d1a1052d42cfd6ecb67a49d82c2f4b359c6ff4cf3fccaff5ea40). Mau trung binh vung giua khung tham chieu (x 25-75 phan tram, y 25-75 phan tram): RGB (118.2, 139.7, 121.3).

## Ly do giu 3 task da chay thu va thay 2 task (trial contamination, ghi day du)

3 task da chay thu o preflight trial (R3-076, R3-007, R3-011) duoc GIU trong danh sach, khong thay the, khong loai khoi mau. 2 task (R3-082, R3-013) duoc THAY NOI DUNG MOI cung ID trong FREEZE-2 theo quyet dinh council wave 3 (a), vi dap an trial cua chung nam trong git history va khong the chua bang lenh cam; dap an cu tro thanh dap an SAI cho noi dung moi. Ly do giu 3 task:

1. Bao cao trial khong bao gio commit len GitHub, khong bao gio co tren laptop. Nguoi chay va ca 2 nguoi cham la phien lam viec moi, khong phai phien da chay trial, va ca 3 deu co lenh cam doc bao cao trial bang van ban trong thu-tu-chay.txt va trong brief cua tung nguoi.
2. Bang chung trial tren laptop da xoa sach 2026-11-23 19:20:04 (thu muc ~/rung3-chung-cu/R3-007, R3-011, R3-013, R3-076, R3-082 va file d42-*, nd02-*, nd03-* trong ~/rung3), thu muc ~/rung3, ~/rung3-goc, ~/rung3-chung-cu duoc tao lai tu dau va ghi moc thoi gian. Bang chung trial chi con tren VM, dung lam input test cho CI/CD, khong phai bang chung chay, khong ghi duong dan o day.
3. Khoa dap an dong bang o day khong lay gia tri tu trial: R3-007 dung 5 gia tri dau vao moi, chon rieng cho lan dong bang nay, khac gia tri trial; R3-011 dung 3 ngay moi (2026-01-01, 2026-07-04, 2000-02-29); 2 ngay (2024-02-29, 2026-12-31) trung voi trial; R3-082 va R3-013 dung gia tri moi hoan toan, chon rieng cho FREEZE-2, khac gia tri trial va khac gia tri muc 8 cu; R3-076 dung gia tri he thong live luc chay, cham bang cach doi chieu bao cao voi file lenh da luu, khong phai voi gia tri trial.
4. Voi 3 lop cach ly tren (bao cao khong toi duoc nguoi chay va nguoi cham, bang chung trial da xoa khoi laptop, khoa dung gia tri moi hoac gia tri danh sach), tinh held-out duoc giu o muc thuc hanh doi voi 3 task giu. Doi voi 2 task thay, tinh held-out duoc khoi phuc bang su loe thoi: dap an cu trong git history khong con dung cho noi dung moi. Quyet dinh thay do council wave 3 chot theo uy quyen full-autonomy 23/11 20:05, thay cho phuong an thay 5 task moi o grading decision pitfall H2.

## Ban tier (59 muc: 55 task + 4 du phong)

- Tier A (script kiem tra xac dinh theo key JSON, nguoi cham van xac nhan file bang chung ton tai va anh chup doc duoc): R3-002, R3-007, R3-013, R3-014, R3-021, R3-072, R3-082, DP-02, DP-05.
- Tier C (cham bang mat theo rubric viet san o day, ca 2 nguoi cham dung chung 1 rubric): R3-010, R3-067, R3-083, R3-085.
- Tier B hybrid (phan kiem tra duoc cham theo key dong bang, phan tu do cham bang nguoi): R3-003, R3-004, R3-022, R3-042.
- Tier B (nguoi cham voi neo bang chung: anh chup co timestamp hoac file output da luu; chan ly la trang thai luc chay, khong phai gia tri live hien tai): tat ca task con lai.
- Chi tiet tung task:

| Task | Tier | Task | Tier | Task | Tier |
|---|---|---|---|---|---|
| R3-001 | B | R3-024 | B | R3-078 | B |
| R3-002 | A | R3-025 | B | R3-079 | B |
| R3-003 | B hybrid | R3-026 | B | R3-082 | A |
| R3-004 | B hybrid | R3-027 | B | R3-083 | C |
| R3-005 | B | R3-028 | B | R3-085 | C |
| R3-006 | B | R3-029 | B | R3-086 | B |
| R3-007 | A | R3-035 | B | R3-088 | B |
| R3-008 | B | R3-036 | B | R3-089 | B |
| R3-009 | B | R3-037 | B | R3-093 | B |
| R3-010 | C | R3-040 | B | R3-094 | B |
| R3-011 | B | R3-041 | B | R3-096 | B |
| R3-013 | A | R3-042 | B hybrid | R3-098 | B |
| R3-014 | A | R3-045 | B | R3-099 | B |
| R3-016 | B | R3-046 | B | R3-100 | B |
| R3-017 | B | R3-047 | B | DP-01 | B |
| R3-018 | B | R3-049 | B | DP-02 | A |
| R3-019 | B | R3-055 | B | DP-03 | B |
| R3-021 | A | R3-067 | C | DP-05 | A |
| R3-022 | B hybrid | R3-072 | A | | |

## Rubric Tier C

### R3-010 (ve so do Excalidraw, xuat PNG)

- Thu tuc do: nguoi cham mo file PNG da xuat, do truc tiep tren anh. Tam moi hinh = diem giua cua hinh do. Chieu rong anh xuat la W pixel.
- Hinh chu nhat: tam co x trong [0, 33 phan tram W], sai so 50 pixel. Chu trong hinh phai doc duoc la "Bat dau".
- Hinh tron: tam co x trong [33, 66 phan tram W], sai so 50 pixel. Chu trong hinh phai doc duoc la "Xu ly".
- Hinh thoi: tam co x trong [66, 100 phan tram W], sai so 50 pixel. Chu trong hinh phai doc duoc la "Ket thuc".
- Mui ten 1: noi tu hinh chu nhat sang hinh tron, huong tong the tu trai sang phai, sai so huong 30 do. Mui ten 2: noi tu hinh tron sang hinh thoi, huong tong the tu trai sang phai, sai so huong 30 do.
- Nguoi cham ghi lai x do duoc cua ca 3 tam (pixel va phan tram W), huong do duoc cua ca 2 mui ten (do), vao ban cham.
- PASS: du 3 hinh dung loai, dung chu, tam dung vung (kem sai so), du 2 mui ten dung huong (kem sai so). FAIL: thieu hinh, sai loai hinh, sai chu, tam ngoai vung qua sai so, thieu mui ten, mui ten nguoc huong qua sai so, file khong phai PNG.

### R3-067 (ve 3 hinh trong Pinta, 800x600, nen trang)

- Hinh bat buoc, du 3 hinh: (1) hinh chu nhat, vung x 50-350, y 50-250, to mau do; (2) hinh tron, vung x 300-500, y 200-400, to mau xanh duong; (3) hinh tam giac, vung goc phai duoi x 550-750, y 350-550, to mau xanh la.
- Mau bat buoc: do (red), xanh duong (blue), xanh la (green). Nen trang. Kich thuoc file 800x600.
- Khong co chu bat buoc.
- Hinh sai duoc tinh la: thieu 1 trong 3 hinh; hinh sai loai (vi du tron thay cho chu nhat); hinh nam ngoai vung quy dinh (tam hinh ngoai vung); hinh sai mau (vi du chu nhat to mau xanh); hinh khong to mau (chi vien, khong co mau nen).
- Nguoi cham kiem tra file ~/rung3/nd23-hinh-ve.png, mo lai va doi chieu tung hinh voi rubric, khong cham theo gu tham my.
- PASS: du 3 hinh dung loai, dung vung, dung mau, nen trang, dung kich thuoc. FAIL: bat ky hinh nao sai theo dinh nghia tren, sai kich thuoc, nen khong trang.

### R3-083 (anh bia trong Pinta, 1200x628, nen chuyen sac, chu lon o giua)

- Nen bat buoc: chuyen sac (gradient) tu mau #1E88E5 o tren xuong mau #43A047 o duoi. Ca 2 mau deu phai xuat hien o nen (tren xanh duong, duoi xanh la). Nen mau dac 1 mau la sai. Nen chuyen sac dung 2 mau khac la sai.
- Chu bat buoc: "Chao mung", mau trang, co chu 72, can giua anh trong vung x 300-900, y 250-380, sai so 50 pixel (tam cua chu nam trong vung nay). Chu sai noi dung, sai mau, sai co chu ro rang (nho hon nhieu so voi 72), hoac nam ngoai vung qua sai so la sai.
- Kich thuoc file bat buoc: 1200x628, dinh dang PNG.
- Hinh sai duoc tinh la: nen khong phai chuyen sac; nen sai 1 trong 2 mau; thieu chu; chu sai noi dung; chu khong phai mau trang; chu nam ngoai vung; sai kich thuoc; file khong phai PNG.
- Nguoi cham kiem tra file ~/rung3-chung-cu/R3-083/anh-bia.png, doi chieu tung muc voi rubric, khong cham theo gu tham my.
- PASS: dung kich thuoc, nen chuyen sac dung 2 mau, chu dung noi dung, dung mau trang, co 72, dung vung. FAIL: bat ky muc nao sai theo dinh nghia tren.

### R3-085 (mpv dung o 00:10, chup anh, doi chieu khung tham chieu)

- Anh chup phai hien cua so mpv dang dung o 00:10 (thanh thoi gian hien 00:10, video dung).
- So sanh anh chup voi khung tham chieu ~/rung3/r3-085-khung-tham-chieu.png (sha256 de410f94b2192e553f4a78ff42df8bcfd84e29e5908c3f02775125cfa4c759c2), dat canh nhau.
- Tieu chi bat buoc: anh chup khop voi khung tham chieu ve canh va vat the; file ket qua ghi dung 2 chi tiet nhan dang duoc (vi du vat the, mau sac, chu, bo cuc) co that trong ca 2 anh.
- Huong dan mau (khong phai tieu chi bat buoc): mau trung binh vung giua anh (x 25-75 phan tram, y 25-75 phan tram) cua anh chup so voi khung tham chieu, chap nhan sai lech duoi 10 phan tram; mau trung binh khung tham chieu la RGB (118.2, 139.7, 121.3). Khong doi khop tung pixel.
- Nguoi cham ghi lai 2 chi tiet da kiem tra va ket luan khop hay khong vao ban cham.
- PASS: mpv dung o 00:10, anh chup khop khung tham chieu theo 2 chi tiet, du file ket qua. FAIL: video khong dung o 00:10, anh chup khong hien cua so mpv, anh chup khong khop khung tham chieu, thieu chi tiet nhan dang.

## R3-001 (Tier B)

- 5 viec them (dung thu tu nay): 1. "Mua sach Python" 2. "Tap the duc 30 phut" 3. "Viet bao cao tuan" 4. "Goi dien cho me" 5. "Don dep phong".
- Danh dau hoan thanh: "Mua sach Python" va "Viet bao cao tuan". Sau buoc 3, bo dem con lai la 3.
- Bo loc o buoc 4 (truoc khi sua va xoa): Active hien 3, Completed hien 2, All hien 5.
- Sua: "Tap the duc 30 phut" thanh "Tap the duc 45 phut".
- Xoa: "Mua sach Python" (viec da hoan thanh).
- Danh sach cuoi cung (4 viec): "Tap the duc 45 phut" (chua hoan thanh), "Viet bao cao tuan" (da hoan thanh), "Goi dien cho me" (chua hoan thanh), "Don dep phong" (chua hoan thanh). Bo loc sau buoc 6: Active 3, Completed 1, All 4.
- Vat chung cham: anh chup danh sach cuoi cung + ket-qua.txt trong ~/rung3-chung-cu/R3-001/. Nguoi cham mo lai trang TodoMVC va doi chieu.

## R3-002 (Tier A)

- 3 doan JSON loi, dong loi va cot loi luc dau (kiem tra tren jsonlint.com):
  - Doan 1: '{"ten": "Lan", "tuoi": 30,}' dau phay thua truoc dau ngoac dong, dong 1, cot 27.
  - Doan 2: '{"ten": "Lan", "tuoi": 30, "thanh_pho": "Ha Noi" "so_tien": 100}' thieu dau phay sau "Ha Noi", dong 1, cot 50.
  - Doan 3: '{"ten": "Lan", "tuoi": 30' ngoac khong dong, dong 1, cot 26.
- Cot loi la vi tri cua ky tu dau tien gay loi hoac vi tri ket thuc chuoi.
- Sau khi sua, ca 3 doan dat Valid JSON. Checker doc dong loi va cot loi tu ket-qua.txt.
- Ghi chu: khoa dap an phai duoc kiem chung lai tren jsonlint.com o buoc kiem tra truoc khi chay, giong mau cua R3-009.
- Vat chung cham: 3 anh chup Valid JSON + ket-qua.txt.

## R3-003 (Tier B hybrid)

- Su kien: Giai Nobel Hoa binh 2026 trao cho Navanethem "Navi" Pillay. Kiem chung ngay 2026-11-23.
- Bao 1: Al Jazeera, "2026 Nobel Peace Prize awarded to Navi Pillay", 9 Oct 2026. https://www.aljazeera.com/news/2026/10/9/2026-nobel-peace-prize-awarded-to-navi-pillay
- Bao 2: Channel News Asia (CNA), "South African judge Navi Pillay wins Nobel Peace Prize", 9 Oct 2026. https://www.channelnewsasia.com/world/nobel-peace-prize-navi-pillay-south-africa-6445566
- Bao 3: NPR, "South African human rights lawyer Navi Pillay wins the Nobel Peace Prize", 9 Oct 2026 (cap nhat 10 Oct 2026). Ban NPR doc qua WCBE: https://www.wcbe.org/npr-news/2026-10-09/south-african-human-rights-lawyer-navi-pillay-wins-the-nobel-peace-prize
- Bang dap an (3 hang):
  - Ngay: 9 October 2026. Ca 3 bao: Al Jazeera dang ngay 2026-10-09, thu Sau; CNA "Friday (Oct 9)"; NPR "on Friday", dang ngay 2026-10-09.
  - Dia diem: Oslo, Norway. Ca 3 bao: Al Jazeera "made on Friday in Oslo", le trao o Oslo ngay 10 December; CNA "OSLO", le o Oslo ngay 10 December; NPR "At a ceremony in Oslo".
  - Nhan vat chinh: Navanethem (Navi) Pillay. Ca 3 bao goi ten ba la nguoi doat giai (Al Jazeera, CNA, NPR).
- Ghi chu ho tro: tien thuong 12 trieu crown Thuy Dien, khoang 1,2 trieu USD. Ca 3 bao: Al Jazeera "12 million Swedish crowns ($1.2m)"; CNA "prize sum of US$1.2 million"; NPR "12 million Swedish kronor, approximately $1.2 million".
- Ket luan: KHONG co mau thuan. Ca 3 muc (ngay, dia diem, nhan vat chinh) khop nhau o ca 3 bao. Doan ket luan 3 dong phai viet ro khong co mau thuan va ca 3 muc khop nhau.
- Phan cham theo key: bang du 9 o, gia tri khop bang dap an tren. Phan cham bang nguoi: doan ket luan 3 dong, neu ro khong co mau thuan.
- Vat chung cham: tai lieu online da luu (bang + doan ket luan), mo lai de kiem tra.

## R3-004 (Tier B hybrid)

- Tai lieu: "Download and install" cua Go, trang chinh thuc https://go.dev/doc/install, tab Linux. Kiem chung ngay 2026-11-23.
- 5 buoc cai dat theo thu tu (la buoc danh so 1-5 trong tai lieu; buoc danh so 6 cua tai lieu, "Confirm that the command prints the installed version of Go", khong nam trong 5 buoc nay):
  1. Xoa bo cai dat Go cu bang cach xoa thu muc /usr/local/go (neu co), roi giai nen file vua tai vao /usr/local: rm -rf /usr/local/go && tar -C /usr/local -xzf go1.14.3.linux-amd64.tar.gz
  2. Them /usr/local/go/bin vao PATH: export PATH=$PATH:/usr/local/go/bin (them vao $HOME/.profile hoac /etc/profile)
  3. Them $HOME/go/bin vao PATH de dung cong cu cai qua go install: export PATH="$PATH:$(go env GOPATH)/bin" (them vao $HOME/.profile hoac $HOME/.bashrc)
  4. Khoi dong lai cac phien terminal dang mo de thay doi co hieu luc
  5. Kiem tra bang cach mo command prompt va go: go version
- Link tai lieu ghi o cuoi tai lieu cua nguoi chay: https://go.dev/doc/install
- Phan cham theo key: du 5 buoc theo thu tu, moi buoc khop 1 buoc danh so trong tai lieu, khong gop 2 buoc, khong viet chung chung, co link dung mien go.dev. Phan cham bang nguoi: moi buoc ghi lenh hoac thao tac cu the, lam duoc.
- Vat chung cham: tai lieu online da luu (5 buoc + link), mo lai de kiem tra.

## R3-005 (Tier B)

- 3 link goc (dung thu tu nay): 1. https://example.com 2. https://en.wikipedia.org/wiki/Computer 3. https://go.dev/doc/install
- Moi link giai ma phai khop dung link goc cua no. 3 file anh ma QR dinh dang JPG.
- Vat chung cham: 3 file anh QR + ket-qua.txt gom 3 cap link goc va link giai ma. Nguoi cham giai ma lai 1 ma bat ky de kiem tra neu can.

## R3-006 (Tier B)

- Bai Wikipedia tieng Anh: "Albert Einstein", https://en.wikipedia.org/wiki/Albert_Einstein
- 2 ban sua lien tiep do nguoi chay chon luc chay tu tab lich su cua bai, ghi ro so hieu ban (revision ID) va thoi gian sua cua ca 2 ban.
- 3 thay doi ve noi dung, moi thay doi ghi ro cu va moi, khop trang khac nhau (diff) giua 2 ban sua do. Ten nguoi sua va thoi gian sua cua ca 2 ban phai dung theo lich su.
- 1 trong 3 thay doi phai co that trong bai hien tai (kiem tra bang cach mo ban moi hon).
- Vat chung cham: anh chup trang khac nhau + ket-qua.txt. Nguoi cham mo lai trang khac nhau giua 2 ban sua da ghi va doi chieu 3 thay doi, ten nguoi sua, thoi gian sua.

## R3-007 (Tier A)

- 5 phep doi, gia tri dau vao moi chon rieng cho lan dong bang nay (khac gia tri trial):
  1. 12 km = 7.4565 miles
  2. 8 miles = 12.8748 km
  3. 7 kg = 15.4324 lb
  4. 30 C = 86.0 F
  5. 5 L = 1.3209 US gallons
- Cong thuc checker dung: 1 mile = 1.609344 km; 1 kg = 2.2046226218 lb; F = C x 9/5 + 32; 1 US gallon = 3.785411784 L. Sai so lam tron 0,01.
- Dinh dang hang trong ket-qua.txt: "<gia tri goc> <don vi goc> = <ket qua> <don vi dich>", vi du "12 km = 7.4565 miles".
- Vat chung cham: 5 anh chup ket qua + ket-qua.txt. Checker so sanh tung hang voi key.

## R3-008 (Tier B)

- Giong doc: doan 1 Joanna, doan 2 Matthew, ca 2 la giong Regular tieng Anh My tren ttsmp3.com. Han muc mien phi 3000 ky tu/ngay, chua dung o buoc chuan bi.
- Doan 1 (80 tu, dung tung tu):
  "Learning a new language opens doors to different cultures and new ways of thinking. Every day, learners practice listening, speaking, reading, and writing to build confidence step by step. Mistakes are a natural part of the journey, and each correction brings the learner closer to fluency. With patience, regular practice, and good materials, anyone can make steady progress. The key is to keep going, even when progress feels slow, because small daily efforts add up to real change over time."
- Doan 2 (120 tu, dung tung tu):
  "The bicycle is one of the most useful inventions in human history, and it changed the way people travel in towns and cities. Early bicycles were heavy, hard to ride, and expensive, so only a small number of people could own one. Over time, makers improved the design with lighter frames, better brakes, and air filled tires, which made cycling safer and more comfortable for everyone. Today, bicycles help people stay healthy, save money, and protect the environment, because they use no fuel and make no smoke. In many cities, leaders build special lanes for cyclists, and more people choose to ride to work or school each year. A short ride each morning wakes the body and clears the mind."
- File 1: am-thanh-1.mp3 (doan 1, Joanna). File 2: am-thanh-2.mp3 (doan 2, Matthew). Moi file phat duoc, thoi luong lon hon 10 giay. File 2 nhieu tu hon file 1 (120 so voi 80).
- Neu han muc 3000 ky tu mien phi trong ngay da het truoc khi chay thi task tuyen bo vo hieu truoc khi chay, ap dung du phong.
- Vat chung cham: 2 file MP3 + ket-qua.txt + anh chup trang tao am thanh. Nguoi cham mo 2 file MP3 va kiem tra thoi luong.

## R3-009 (Tier B)

- URL 1: https://www.bbc.com/
- URL 2: https://en.wikipedia.org/wiki/Main_Page
- Moi trang it nhat 1 loi (Errors) theo kiem tra truoc khi chay. Ngay kiem tra URL: 2026-11-23 (xem ruling o dau file: so lieu WAVE day du van can kiem tra bang trinh duyet).
- 5 so lieu moi trang: Errors, Alerts, Features, Structural Elements, Contrast Errors. Cac so lieu la gia tri live tai thoi diem chay; chan ly la bang tom tat trong anh chup, khong phai gia tri hien tai cua trang.
- Ket luan: trang nao co tong loi va canh bao lon hon; neu tong bang nhau thi ghi ro 2 trang bang nhau.
- Vat chung cham: 2 anh chup bang tom tat + ket-qua.txt. Nguoi cham doi chieu so lieu voi anh chup.

## R3-010 (Tier C)

- Xem rubric Tier C o dau file (thu tuc do, vung tam, sai so 50 pixel, sai so huong mui ten 30 do).
- 3 hinh: chu nhat "Bat dau" (tam phan trai), tron "Xu ly" (tam phan giua), thoi "Ket thuc" (tam phan phai). 2 mui ten: chu nhat sang tron, tron sang thoi.
- Vat chung cham: file so-do.png + ket-qua.txt + anh chup bang ve. Nguoi cham do truc tiep tren file PNG da xuat.

## R3-011 (Tier B)

- 5 ngay (dung thu tu nay), thu trong tuan dung:
  1. 2024-02-29: Thursday (ngay 29 thang 2 nam nhuan)
  2. 2026-01-01: Thursday
  3. 2026-07-04: Saturday
  4. 2026-12-31: Thursday (ngay cuoi nam)
  5. 2000-02-29: Tuesday (ngay 29 thang 2 nam nhuan)
- Co it nhat 1 ngay 29 thang 2 nam nhuan (o day co 2) va 1 ngay cuoi nam.
- Xem ruling o dau file: timeanddate.com van bi chan o muc curl; can xac nhan bang trinh duyet truoc task 1, neu van bi chan thi tuyen bo vo hieu truoc task 1.
- Vat chung cham: 5 anh chup ket qua + ket-qua.txt. Nguoi cham doi chieu thu voi anh chup.

## R3-013 (Tier A)

- Van ban mau: 'Lien he Hoa qua hoa@example.com hoac goi 0987654321. Hop luc 09:15 ngay 03/09/2026 tai Da Nang, ket thuc luc 17:45. Ma don DH-2026-0903, tong 2.750.000 VND, phi dich vu 350.000 VND. Han chot 10/09/2026. Email khac dung@test.org va khanh@example.com, dien thoai khac 0978123456. Lien he khan cap 0905551234.'
- 5 mau va so ket qua khop:
  1. Email: [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,} : 3 ket qua (hoa@example.com, dung@test.org, khanh@example.com)
  2. So dien thoai: 0\d{9} : 3 ket qua (0987654321, 0978123456, 0905551234)
  3. Ngay thang: \d{2}\/\d{2}\/\d{4} (dang escaped, xem ruling) : 2 ket qua (03/09/2026, 10/09/2026)
  4. Gio: \d{2}:\d{2} : 2 ket qua (09:15, 17:45)
  5. So tien: \d{1,3}(?:\.\d{3})+ : 2 ket qua (2.750.000, 350.000)
- Giai thich cua trang cho mau thu 5 phai duoc ghi trong ket-qua.txt.
- Vat chung cham: 5 anh chup ket qua + ket-qua.txt. Checker so sanh mau (chuan hoa \/ thanh /), so luong, cac chuoi khop.

## R3-014 (Tier A)

- 3 mau va gia tri RGB dung:
  - #FF0000: RGB(255, 0, 0)
  - #008080: RGB(0, 128, 128)
  - #FFD700: RGB(255, 215, 0)
- Gia tri HSL cua 3 mau ghi theo trang hien thi (live, doi chieu voi anh chup).
- Vat chung cham: 3 anh chup (moi anh 1 ma) + ket-qua.txt. Checker so sanh hex va RGB.

## R3-016 (Tier B)

- Luoc do 4 truong: First Name (First Name), Last Name (Last Name), Email Address (Email Address), Number voi gia tri nho nhat 18 va lon nhat 90.
- So dong: 10. Dinh dang: CSV. File: du-lieu.csv.
- Kiem tra: 10 dong du lieu, 4 cot, ten cot dung 4 truong, moi dong du 4 gia tri, email deu co ky tu @, tuoi deu la so nguyen tu 18 den 90.
- Tai khoan test: chua co. Can browser task tao hoac cap phat tai khoan Mockaroo truoc task 1; nguoi chay chi dang nhap, khong tao tai khoan moi. Neu tai khoan khong tai duoc CSV thi task vo hieu theo muc 1.
- Vat chung cham: du-lieu.csv + ket-qua.txt + anh chup ban xem truoc. Nguoi cham mo file CSV va dem.

## R3-017 (Tier B)

- 5 tab mo tren trinh duyet Brave (dung thu tu mo nay): 1. https://example.com 2. https://en.wikipedia.org/wiki/Main_Page 3. https://www.bbc.com/ 4. https://github.com 5. https://www.python.org
- Mo trinh quan ly tien trinh bang Shift Esc. Neu trinh duyet test khong co phim tat nay thi dung lai, ghi ro vao ket-qua.txt, task vo hieu theo muc 1.
- Bang 5 tab co muc dung bo nho cao nhat, kem bo nho va CPU, sap xep giam dan theo bo nho. Gia tri bo nho va CPU la live tai thoi diem chay; chan ly la anh chup trinh quan ly tien trinh, khong phai lenh chay lai.
- Vat chung cham: anh chup trinh quan ly tien trinh + ket-qua.txt. Nguoi cham doi chieu bang voi anh chup.

## R3-018 (Tier B)

- 3 ten mien (dung thu tu nay): 1. rung3khaosat01.com 2. rung3khaosat02.com 3. rung3khaosat03.com
- Moi ten ghi: tinh trang (con trong hay da co nguoi dung), gia nam dau (neu con trong), ten thay the goi y (neu ten nao da co nguoi dung).
- Tinh trang va gia la live tai thoi diem chay; chan ly la anh chup ket qua tra cuu, khong phai gia hien tai. Khong mua ten mien.
- Neu trang hien thi trang kiem tra 'Verify you are human' hoac trang Cloudflare thi dung lai, ghi ro vao ket-qua.txt, task vo hieu theo muc 1.
- Vat chung cham: 3 anh chup ket qua + ket-qua.txt. Nguoi cham doi chieu voi anh chup.

## R3-019 (Tier B)

- Tuyen: Ha Noi den Ho Chi Minh. Ngay 1 = ngay chay + 30 ngay, ngay 2 = ngay chay + 37 ngay. Ngay cu the chi chot khi ngay chay duoc dat.
- Moi ngay ghi: gia thap nhat, gio bay, hang bay. Bang 2 hang ngay. Chenh lech gia tinh dung. Ket luan co ngay cu the duoc chon. Khong mua ve.
- Gia la live tai thoi diem chay; chan ly la anh chup gia cua tung ngay, khong phai gia hien tai.
- Neu trang hien thi trang kiem tra bot hoac yeu cau xac minh con nguoi thi dung lai, ghi ro vao ket-qua.txt, task vo hieu theo muc 1.
- Vat chung cham: 2 anh chup gia + tai lieu online (bang + ket luan). Nguoi cham doi chieu gia voi anh chup.

## R3-021 (Tier A)

- Bang san_pham (id INTEGER PRIMARY KEY, ten TEXT, gia INTEGER, so_luong INTEGER). 5 dong: Ban 150x10, Ghe 250x5, Den 80x20, Tu 400x3, Giuong 600x2.
- Truy van buoc 4 (SELECT ten, gia FROM san_pham WHERE gia > 100 ORDER BY gia DESC), thu tu ket qua: Giuong 600, Tu 400, Ghe 250, Ban 150.
- Truy van buoc 5 (SELECT SUM(gia * so_luong) FROM san_pham): tong 6750.
- File CSV ket-qua-truy-van.csv: 4 dong ket qua (khong tinh dong tieu de).
- Vat chung cham: ket-qua-truy-van.csv + ket-qua.txt + anh chup ket qua truy van. Checker so sanh thu tu, tong, so dong CSV.

## R3-022 (Tier B hybrid)

- Trang goc tieng Anh: https://en.wikipedia.org/wiki/Computer , dich sang tieng Viet tren translate.google.com (dich trang web).
- 5 thuat ngu va ban dich tieng Viet (ban dich viet co dau, la chuoi ky vong dung; nguoi cham chap nhan ban dich khop nghia):
  1. central processing unit -> "bộ xử lý trung tâm"
  2. random-access memory -> "bộ nhớ truy cập ngẫu nhiên"
  3. motherboard -> "bo mạch chủ"
  4. operating system -> "hệ điều hành"
  5. hard disk drive -> "ổ đĩa cứng"
- Dich nguoc 2 trong 5 thuat ngu (nguoi chay chon 2 bat ky), chap nhan neu khop nghia voi ban goc. Tu dong nghia chap nhan khi dich nguoc:
  1. central processing unit: CPU, central processor
  2. random-access memory: RAM, random access memory
  3. motherboard: mainboard, main board
  4. operating system: OS
  5. hard disk drive: HDD, hard drive, hard disk
- Tieu de trang sau khi dich phai dung (tieu de bai "Computer" da dich).
- Phan cham theo key: du 5 cap thuat ngu, ban dich khop nghia, 2 ket qua dich nguoc khop nghia voi ban goc (chap nhan tu dong nghia o tren). Phan cham bang nguoi: anh chup hien trang da dich.
- Vat chung cham: anh chup trang da dich + ket-qua.txt.

## R3-024 (Tier B)

- 3 tu khoa tim tren openverse.org, loc chi anh dung lai duoc (dung thu tu nay): 1. "mountain lake" 2. "city bicycle" 3. "old library"
- Moi anh ghi: ten anh, tac gia, giay phep su dung cu the, link goc. Ca 3 anh deu phai co giay phep cho phep dung lai.
- Ten, tac gia, giay phep, link la live tai thoi diem chay; chan ly la anh chup trang chi tiet cua tung anh.
- Vat chung cham: 3 anh chup trang chi tiet + ket-qua.txt. Nguoi cham doi chieu voi anh chup. Chi ghi link, khong tai anh ve may.

## R3-025 (Tier B)

- Cau lenh 1 (toan tu site:): site:en.wikipedia.org photosynthesis
- Cau lenh 2 (toan tu filetype:pdf): filetype:pdf photosynthesis
- Moi cau lenh ghi 3 ket qua dau tien, kem tieu de va URL. URL khop ket qua tim kiem tai thoi diem chay; chan ly la anh chup ket qua tim kiem.
- Mo 1 ket qua file PDF trong trinh duyet Brave, kiem tra file mo duoc, ghi so trang (so trang la gia tri live cua file do, doi chieu voi anh chup).
- Neu trang Google hien thi trang xac minh 'Verify you are human' hoac yeu cau nhap captcha thi dung lai, ghi ro vao ket-qua.txt, task vo hieu theo muc 1.
- Vat chung cham: 2 anh chup ket qua tim kiem + ket-qua.txt. Nguoi cham doi chieu URL va so trang voi anh chup.

## R3-026 (Tier B)

- Bang 1: tao ngau nhien tren coolors.co, 5 ma hex (live, doi chieu voi anh chup).
- Bang 2: khoa 1 mau trong bang 1, tao lai bang moi, 5 ma hex; mau da khoa khong doi. Ten mau da khoa ghi ro trong ket-qua.txt.
- Bang 3: tao tu mau goc #1E88E5: mo coolors.co/generate/1E88E5, bam Generate, 5 ma hex (live, doi chieu voi anh chup).
- Ten cua tung mau trong ca 3 bang (ten hien ben duoi moi ma hex) phai ghi dung theo trang.
- Vat chung cham: 3 anh chup bang mau + ket-qua.txt. Nguoi cham doi chieu ma hex, mau khoa, ten mau voi anh chup.

## R3-027 (Tier B)

- 3 ten nguoi dung test (khong dung ten that, dung thu tu nay): 1. rung3testalpha01 2. rung3testbravo02 3. rung3testcharlie03
- 5 nen tang ghi ket qua cho moi ten: GitHub, X (Twitter), Instagram, YouTube, Reddit.
- Moi nen tang ghi ro: con trong, da co nguoi dung, hoac 'khong xac dinh' (neu nen tang tra ve ket qua khong xac dinh thi ghi ro, van tinh pass).
- Ket luan: ten nao con trong tren ca 5 nen tang neu co, hoac ghi ro khong co ten nao con trong ca 5.
- Ket qua la live tai thoi diem chay; chan ly la anh chup ket qua cua tung ten.
- Vat chung cham: 3 anh chup ket qua + ket-qua.txt. Nguoi cham doi chieu voi anh chup.

## R3-028 (Tier B)

- 3 moc thoi gian UTC va 3 mui gio: Asia/Ho_Chi_Minh (UTC+7), Europe/London (UTC+0, gio GMT thang 12), America/New_York (UTC-5, gio EST thang 12).
- Bang dap an:
  - 2026-12-01 12:00 UTC: Ha Noi 2026-12-01 19:00, London 2026-12-01 12:00, New York 2026-12-01 07:00.
  - 2026-12-01 18:00 UTC: Ha Noi 2026-12-02 01:00, London 2026-12-01 18:00, New York 2026-12-01 13:00.
  - 2026-12-02 00:00 UTC: Ha Noi 2026-12-02 07:00, London 2026-12-02 00:00, New York 2026-12-01 19:00.
- Chenh lech gio so voi UTC tai thoi diem doi: Ha Noi +7, London +0, New York -5.
- Vat chung cham: 3 anh chup ket qua + ket-qua.txt. Nguoi cham doi chieu gio dia phuong va chenh lech voi anh chup.

## R3-029 (Tier B)

- Tai khoan test: chua co. Can browser task dang ky tai khoan moi tren ecommerce-playground.lambdatest.io truoc task 1 (email test-only, mat khau chi luu trong Secure Vault neu can), xac nhan dang nhap duoc va tinh nang wishlist hoat dong. Tai khoan chi dung cho R3-029.
- 5 san pham (ten hien tren cua hang demo, dung thu tu nay): 1. iPhone 2. MacBook 3. Canon EOS 5D 4. HP LP3065 5. HTC Touch HD
- Luu yeu thich ca 5, kiem tra danh sach du 5. Bo luu 1 san pham ("Canon EOS 5D"), kiem tra danh sach con 4. Luu lai san pham do, kiem tra danh sach lai du 5.
- Luu y kiem tra truoc khi chay: ten 5 san pham tren phai duoc xac nhan co that tren cua hang demo o buoc kiem tra tai khoan truoc task 1; neu ten nao khac, dieu phoi vien sua key truoc task 1 (sua truoc khi dong bang, commit moi + ghi lai hash).
- Vat chung cham: anh chup trang danh sach yeu thich o cac buoc (du 5, con 4, lai du 5) + ket-qua.txt neu task yeu cau. Nguoi cham doi chieu ten san pham va so luong voi anh chup. Khong dung tai khoan that.

## R3-035 (Tier B)

- 3 cap tien va so tien (doi sang cung 1 loai tien dich la VND):
  1. 100 USD sang VND
  2. 50 EUR sang VND
  3. 200 GBP sang VND
- Moi phep doi ghi ty gia dung tai thoi diem chay (xe.com) va ket qua. Tong = tong 3 ket qua. Sai so lam tron 1 don vi tien dich (1 VND).
- Ty gia va ket qua la live tai thoi diem chay; chan ly la anh chup man hinh co timestamp cua ty gia va ket qua.
- Vat chung cham: anh chup ty gia va ket qua + tai lieu online (bang 4 hang: 3 phep doi + 1 hang tong). Nguoi cham doi chieu ty gia, ket qua, tong voi anh chup.

## R3-036 (Tier B)

- 3 thanh pho: Ha Noi (UTC+7), Tokyo (UTC+9), Sydney (UTC+11, gio AEDT thang 12).
- Ngay hop: Thu Tu 2026-12-02. Gio lam viec dinh nghia 09:00-17:00 gio dia phuong.
- Khoang chung: 02:00-06:00 UTC (Ha Noi 09:00-13:00, Tokyo 11:00-15:00, Sydney 13:00-17:00).
- Gio hop chon (60 phut): 03:00 UTC, tuc Ha Noi 10:00, Tokyo 12:00, Sydney 14:00 ngay 2026-12-02. Ca 3 gio deu trong 09:00-17:00 gio dia phuong.
- Bang 3 hang gio hop theo tung thanh pho + 1 dong giai thich vi sao gio do phu hop (nam trong gio lam viec cua ca 3 ben, trong khoang chung 02:00-06:00 UTC).
- Vat chung cham: tai lieu online (bang + dong giai thich), mo lai de kiem tra. Nguoi cham doi chieu gio hop qua chenh lech mui gio va kiem tra nam trong gio lam viec cua ca 3 ben.

## R3-037 (Tier B)

- 2 ten mien (dung thu tu nay): 1. example.com 2. wikipedia.org
- Moi ten ghi: ten nha dang ky, ngay dang ky, ngay het han, may chu ten, trang thai (con hieu luc hay het han). Cac gia tri la live tai thoi diem chay tren who.is; chan ly la anh chup ket qua WHOIS.
- Neu trang hien thi reCAPTCHA hoac yeu cau xac minh con nguoi thi dung lai, ghi ro vao ket-qua.txt, task vo hieu theo muc 1.
- Vat chung cham: 2 anh chup ket qua + ket-qua.txt. Nguoi cham doi chieu voi anh chup.

## R3-040 (Tier B)

- Trang web cong khai: https://www.bbc.com/news . Kho luu tru: web.archive.org.
- Ban luu tru: ban luu tru cu nhat con doc duoc cua cung trang (da kiem chung: Wayback co snapshot cua bbc.com/news, vi du snapshot 2011-01-28 07:34:58). Neu ban cu nhat co duoi 3 thay doi ro rang thi dung ban ke tiep co du 3 thay doi, ghi ro ngay cua ban da dung.
- Ghi tieu de va 3 muc noi dung chinh o ban hien tai, 3 muc noi dung chinh o ban cu, 3 thay doi ro rang (moi thay doi co cu va moi). Tieu de trang khop ca 2 ban ("BBC News").
- Vat chung cham: tai lieu online (bang 4 hang: muc, ban cu, ban moi, thay doi), mo lai de kiem tra. Nguoi cham mo lai ca 2 ban (hien tai va ban luu tru co ngay da ghi) va doi chieu 3 thay doi.

## R3-041 (Tier B)

- Trang kiem tra: browserleaks.com/javascript (7 thong tin dau) va browserleaks.com/fonts (so luong font).
- 8 thong tin: tac nhan nguoi dung (user agent), ngon ngu, mui gio, kich thuoc man hinh, do sau mau, cookie co bat hay khong, JavaScript co bat hay khong, so luong font phat hien.
- Kiem tra lai kich thuoc man hinh bang cach keo canh phai cua so trinh duyet vao trong 200 pixel, ghi kich thuoc moi.
- Cac gia tri la live tai thoi diem chay; chan ly la anh chup trang kiem tra. Mo lai trang, 8 thong tin van giong lan 1 tru kich thuoc man hinh.
- Vat chung cham: anh chup trang kiem tra + ket-qua.txt. Nguoi cham doi chieu voi anh chup va mo lai trang de kiem tra.

## R3-042 (Tier B hybrid)

- Trang giay phep: opensource.org (MIT, Apache 2.0, GPL 3.0).
- Bang dap an (3 hang x 3 cot):
  - Quyen su dung thuong mai: MIT: Duoc. Apache 2.0: Duoc. GPL 3.0: Duoc.
  - Yeu cau ghi cong: MIT: Co, phai giu thong bao ban quyen va giay phep. Apache 2.0: Co, phai giu thong bao ban quyen, giay phep, NOTICE, va ghi ro thay doi. GPL 3.0: Co, phai giu thong bao ban quyen.
  - Yeu cau mo ma nguon khi phan phoi: MIT: Khong. Apache 2.0: Khong. GPL 3.0: Co, phai cung cap ma nguon theo GPL khi phan phoi.
- Ket luan: GPL 3.0 han che nhat, vi chi GPL yeu cau mo ma nguon khi phan phoi (copyleft), trong khi MIT va Apache 2.0 khong yeu cau.
- Phan cham theo key: bang du 9 o dung noi dung tren, ket luan dung ten giay phep kem ly do. Phan cham bang nguoi: khong sao chep nguyen van ban giay phep.
- Vat chung cham: tai lieu online (bang + dong ket luan), mo lai de kiem tra.

## R3-045 (Tier B)

- 3 URL anh goc: https://picsum.photos/seed/r3a/400/300 , https://picsum.photos/seed/r3b/400/300 , https://picsum.photos/seed/r3c/400/300
- Do tre moi khung hinh: 50 (tuc 500 ms). Anh GIF tao ra co 3 khung hinh. File: anh-dong.gif.
- Vat chung cham: anh-dong.gif + ket-qua.txt + anh chup trang tao GIF va so khung. Nguoi cham mo file GIF va dem so khung, kiem tra do tre.

## R3-046 (Tier B)

- 3 thanh pho: Ha Noi, London, Sydney.
- Ngay 1: 2026-12-02. Ngay 2: 2027-06-02 (cach ngay 1 dung 6 thang).
- Moi lan tra ghi: gio mat troi moc, gio mat troi lan, do dai ngay. Tong 6 hang (3 thanh pho x 2 ngay). Chenh lech do dai ngay giua 2 ngay cua moi thanh pho tinh dung.
- Gio moc, gio lan, do dai ngay la live tai thoi diem chay tren timeanddate.com; chan ly la anh chup ket qua cua ca 6 lan tra.
- Vat chung cham: 6 anh chup ket qua + ket-qua.txt. Nguoi cham doi chieu voi anh chup.

## R3-047 (Tier B)

- 3 cuon sach tren gutenberg.org (dung thu tu nay):
  1. "Pride and Prejudice", tac gia Jane Austen, nam xuat ban 1813, pham vi cong cong, ebook 1342.
  2. "Frankenstein; Or, The Modern Prometheus", tac gia Mary Wollstonecraft Shelley, nam xuat ban 1818, pham vi cong cong, ebook 84.
  3. "Adventures of Huckleberry Finn", tac gia Mark Twain, nam xuat ban 1884, pham vi cong cong, ebook 76.
- Moi cuon ghi it nhat 3 dinh dang file co san (vi du: HTML, EPUB, Kindle, Plain Text). Nam tac gia mat (neu co) ghi theo trang chi tiet.
- Vat chung cham: 3 anh chup trang chi tiet + ket-qua.txt. Nguoi cham doi chieu tac gia, nam xuat ban, trang thai, dinh dang voi anh chup.

## R3-049 (Tier B)

- 3 khoan vay tren calculator.net (may tinh vay), cong thuc tra hang thang M = P x r / (1 - (1 + r)^-n), r = lai suat nam / 12:
  1. So tien 500.000.000 VND, lai suat 8 phan tram/nam, thoi han 120 thang. Tien tra hang thang ky vong: 6.066.379,72 VND. Tong tien lai ky vong: 227.965.566,13 VND.
  2. So tien 300.000.000 VND, lai suat 7,5 phan tram/nam, thoi han 60 thang. Tien tra hang thang ky vong: 6.011.384,58 VND. Tong tien lai ky vong: 60.683.074,72 VND.
  3. So tien 1.000.000.000 VND, lai suat 9 phan tram/nam, thoi han 240 thang. Tien tra hang thang ky vong: 8.997.259,56 VND. Tong tien lai ky vong: 1.159.342.294,04 VND.
- Sai so cho phep: 1 don vi tien. Gia tri tren la gia tri cong thuc; nguoi cham doi chieu voi anh chup ket qua cua trang (gia tri tren trang la chan ly neu lech do lam tron hien thi).
- Vat chung cham: 3 anh chup ket qua + ket-qua.txt. Nguoi cham doi chieu tien tra hang thang va tong tien lai voi anh chup.

## R3-055 (Tier B)

- Mau: ~/rung3/d06-template.txt, sha256 fe957ba1d6000a272177c12a0e11dd6750cf954021ea23502ec975dfa8cd711b.
- Thu muc goc: ~/rung3/d06-du-an-moi. 5 thu muc cap 1: Tai-lieu, Ma-nguon, Kiem-thu, Du-lieu, Cong-cu. 3 thu muc cap 2: Ma-nguon/thu-vien, Ma-nguon/ung-dung, Kiem-thu/kiem-thu-don-vi.
- README.md o thu muc goc co du 3 muc: ten du an, ngay tao, danh sach thu muc.
- .gitignore dung noi dung mau: __pycache__/, *.pyc, .venv/
- Quyen: thu muc Tai-lieu chi doc; cac thu muc khac doc ghi binh thuong.
- Vat chung cham: anh chup cay thu muc + bao cao neu task yeu cau. Nguoi cham mo tung thu muc va kiem tra quyen.

## R3-067 (Tier C)

- Xem rubric Tier C o dau file (3 hinh bat buoc, vung, mau, dinh nghia hinh sai).
- Hinh 1: chu nhat, vung x 50-350, y 50-250, to mau do.
- Hinh 2: tron, vung x 300-500, y 200-400, to mau xanh duong.
- Hinh 3: tam giac (cong cu Freeform Shape, 3 diem), vung goc phai duoi x 550-750, y 350-550, to mau xanh la.
- File: ~/rung3/nd23-hinh-ve.png, 800x600, nen trang. Khong co chu bat buoc.
- Vat chung cham: file PNG. Nguoi cham mo file va doi chieu voi rubric.

## R3-072 (Tier A)

- 5 anh trong ~/rung3/d72-anh/, thu tu trong thu muc:
  - d72-anh-1.png: 800x600, sha256 d47445cddc3b7aafaefc1ca52ba79591260000371b43a088ea80ba9e3417bb5b
  - d72-anh-2.png: 1024x768, sha256 243a8a28654490af070b425410427525f1b7f7dc4780abe1002374f247240df1
  - d72-anh-3.png: 640x480, sha256 ae6e6fd281e5fb7e716553a717b076f72a58e598e8f298f11a62911acfa86bd2
  - d72-anh-4.png: 1280x720, sha256 d0457a976a47678c5e702c2f245f8b318ec02af7181c7d94a03292161b87d402
  - d72-anh-5.png: 400x400, sha256 83235ae5fbfba40b31b0bcd934b994c2d1c67712cb7b97d331f496e19edb3c9b
- Kich thuoc ghi dang rong x cao, chap nhan khoang trang quanh dau x.
- Lop thong tin imv mac dinh hien ten file va kich thuoc (rong x cao). Khong can dat overlay_text truoc khi chay (da kiem tra: ~/.config/imv/config khong dat overlay_text; chuoi mac dinh trong imv-wayland hien ten file va kich thuoc).
- Vat chung cham: ket-qua.txt (bang 5 hang) + anh chup lop thong tin anh thu nhat. Checker so sanh ten file va kich thuoc.

## R3-074 (Tier B)

- Loi: dong 8 dung bien khong dinh nghia `tongue` thay vi `tong`. Chay script goc bao loi NameError: name 'tongue' is not defined, exit 1.
- Sua: doi `tongue` thanh `tong` o dong 8. Khong doi ten bien, khong doi logic chinh.
- File ket qua ~/rung3/d40-ket-qua.txt, du 10 dong dung gia tri: dong 1: tong = 7; dong 2: tong = 9; dong 3: tong = 15; dong 4: tong = 11; dong 5: tong = 14; dong 6: tong = 24; dong 7: tong = 13; dong 8: tong = 18; dong 9: tong = 15; dong 10: tong = 13.
- Chay lan 2 cho ket qua giong lan 1.
- sha256 d40-tinh-toan.py: f3b09ca0df66d3e4c4b8c88c78cffdb374d9ca6d988145587969034e4e3e7025. sha256 d40-ket-qua-ky-vong.txt: f737a14b0e450ed29e2b5842ca7a967a6c93cae20a500462dae027006a68d091.
- Vat chung cham: file ket-qua.txt + anh chup thong bao loi luc dau. Nguoi cham chay lai script (chi doc) va doi chieu 10 dong.

## R3-075 (Tier B)

- requirements.txt: chi co requests==2.32.3. sha256: 4b8183101fd19f071771805a42a31fbb234a7961921fdb8b783a279755a1b5d5
- d41-app.py: import requests, in "Xin chao rung 3" roi in phien ban requests. sha256: 9f368adac0c3e4b2112679198a4f4df8ea9492f5b0db27ba5a08b28e4a85cc3b
- Dong chao ky vong: "Xin chao rung 3". Ung dung chay trong venv in dung dong chao, exit 0.
- Python tren laptop: 3.14.10. Venv tai ~/rung3/d41-venv. Sau khi tat venv, thu muc venv con nguyen.
- Vat chung cham: anh chup terminal (phien ban Python, duong dan python trong venv, output ung dung). Nguoi cham kiem tra venv ton tai va goi da cai.

## R3-076 (Tier B, kem script kiem tra nhat quan bao cao)

- Bao cao ~/rung3/d42-bao-cao.txt co du 3 muc: dia con trong, RAM con trong, bang 5 tien trinh (ten, PID, CPU, RAM) kem thoi gian ghi nhan.
- So lieu dia va RAM trong bao cao phai khop file lenh da luu co timestamp (d42-lenh-dia.txt, d42-lenh-ram.txt). Bang 5 tien trinh phai khop file d42-lenh-tien-trinh.txt (ten va PID cua ca 5 tien trinh co trong file lenh).
- Gia tri dia, RAM, tien trinh la live luc chay; KHONG co gia tri dong bang. Nguoi cham khong chay lai lenh de lay gia tri moi (gia tri RAM thay doi giua cac lan chay); chi doi chieu bao cao voi file lenh da luu.
- Vat chung cham: d42-bao-cao.txt + d42-lenh-dia.txt + d42-lenh-ram.txt + d42-lenh-tien-trinh.txt trong ~/rung3-chung-cu/R3-076/. Script kiem tra nhat quan bao cao (tier-a-check.py, type report-consistency) doi chieu cac gia tri nay.

## R3-078 (Tier B)

- Thu muc lam viec: ~/rung3/d45-work, 10 file d45-file-01.txt den d45-file-10.txt. Thu muc sao luu: ~/rung3/d45-backup.
- So file sao luu bang so file goc (10). Cau truc giu nguyen. Checksum khop toan bo file (0 file sai).
- Danh sach sao luu du so dong (10 hang: ten file, kich thuoc, checksum).
- 3 file o vi tri co dinh thu 1, thu 5, thu 10 theo thu tu sap xep ten (d45-file-01.txt, d45-file-05.txt, d45-file-10.txt) co noi dung dung file goc.
- Vat chung cham: file danh sach sao luu + bao cao. Nguoi cham kiem tra so file va doi chieu checksum 3 file co dinh.

## R3-079 (Tier B)

- Thu muc sao luu: ~/rung3/d46-backup, co 2 ban theo ngay: 2026-11-20 va 2026-11-22, moi ban co bao-cao-tuan.txt.
- File yeu cau d46-yeu-cau.txt: khoi phuc bao-cao-tuan.txt tu ban 2026-11-22 vao ~/rung3/d46-restored.
- Noi dung dung: tuan 47, doanh thu 12500000, don hang 320 (khong phai tuan 46: doanh thu 9800000, don hang 275).
- File hien tai trong thu muc lam viec khong bi ghi de. Bao cao gom ten file, ngay ban sao luu (2026-11-22), ket qua doi chieu dung manifest.txt.
- Vat chung cham: file da khoi phuc + bao cao. Nguoi cham mo file da khoi phuc va doi chieu voi manifest.

## R3-082 (Tier A)

- 5 phep tinh (tinh bang omacalc, tung buoc, tu xu ly thu tu uu tien; xem ruling):
  - (14 + 6) * 4 - 9 = 71
  - 120 / 5 + 18 * 3 = 78
  - (60 - 24) * 3 + 12 = 120
  - 300 / 6 * 2 - 11 = 89
  - (11 + 9) * 5 / 4 = 25
- Sai so lam tron 0,01. File ket qua ~/rung3/nd02-ket-qua.txt co bang 6 hang (tieu de + 5 hang phep tinh) va 1 dong ghi chu kiem tra lai theo mau "Kiem tra lai: <phep> = <ket qua>" voi ket qua dung.
- Vat chung cham: ket-qua.txt + 5 anh chup man hinh may tinh. Checker so sanh phep tinh va ket qua.

## R3-083 (Tier C)

- Xem rubric Tier C o dau file (nen chuyen sac #1E88E5 tren xuong #43A047 duoi, chu "Chao mung" mau trang co 72, vung x 300-900 y 250-380, kich thuoc 1200x628, PNG).
- File: ~/rung3-chung-cu/R3-083/anh-bia.png. ket-qua.txt gom kich thuoc anh, 2 ma mau nen, noi dung chu, co chu, mau chu, ten file da luu.
- Vat chung cham: file anh-bia.png + ket-qua.txt + anh chup anh bia. Nguoi cham doi chieu voi rubric.

## R3-085 (Tier C)

- Xem rubric Tier C o dau file (mpv dung o 00:10, khung tham chieu, 2 chi tiet bat buoc, huong dan mau 10 phan tram).
- Video: ~/rung3/nd26-video.mp4 (ffmpeg testsrc2, 640x360, 30 fps, 15 giay). Khung tham chieu: ~/rung3/r3-085-khung-tham-chieu.png.
- Vat chung cham: anh-mpv-00-10.png + ket-qua.txt (thoi gian dung, ten file anh chup, 2 chi tiet nhan dang duoc, ket luan khop hay khong). Nguoi cham so sanh anh chup voi khung tham chieu.

## R3-086 (Tier B)

- 2 ten mien (dung thu tu nay): 1. example.com 2. en.wikipedia.org. Ca 2 tra ve HTTP 200 qua curl ngay 2026-11-23 19:23.
- Moi ten mien: ping (so goi gui, so goi nhan, ti le mat goi), DNS (dia chi IP tra ve), curl -L (ma trang thai HTTP). Ma trang thai 200 cho ca 2.
- Dia chi IP phai nam trong danh sach dia chi DNS tra ve cua tung ten mien tai thoi diem chay. Ti le mat goi dung nhu ket qua lenh tai thoi diem chay.
- Vat chung cham: 6 file ket qua lenh co timestamp (ping, dns, curl cho moi ten mien) + bao cao nd06-bao-cao.txt. Nguoi cham doi chieu bao cao voi file lenh da luu.

## R3-088 (Tier B)

- Thu muc: ~/rung3/nd28-work, 10 file nd28-file-01.txt den nd28-file-10.txt. File nen: ~/rung3/nd28-luu-tru.tar.gz. Thu muc giai nen kiem tra: ~/rung3/nd28-check.
- So file trong nen bang so file goc (10). So file sau giai nen bang so file goc (10).
- 3 file so sanh o vi tri co dinh thu 1, thu 5, thu 10 theo thu tu sap xep ten (nd28-file-01.txt, nd28-file-05.txt, nd28-file-10.txt) dung noi dung.
- Bao cao ~/rung3/nd28-bao-cao.txt gom so file goc, so file trong nen, so file sau giai nen, ket qua so sanh 3 file.
- Vat chung cham: file tar.gz + bao cao. Nguoi cham liet ke file trong nen va dem.

## R3-089 (Tier B)

- Thu muc: ~/rung3/nd09-logs, 12 file .log. So dong: log-01 50, log-02 65, log-03 80, log-04 95, log-05 110, log-06 125, log-07 140, log-08 155, log-09 170, log-10 185, log-11 195, log-12 200. Tong 1570 dong.
- Thoi gian sua: log-01 den log-06 la 1 ngay tuoi, log-07 den log-12 la 10 ngay tuoi (moc 2026-11-23 19:20). find -mtime -7 tra ve 6 file: log-01 den log-06.
- Bao cao ~/rung3/nd09-bao-cao.txt: tong so file 6, bang duong dan, so dong, ngay sua cua tung file, sap xep giam dan theo so dong (log-06 125, log-05 110, log-04 95, log-03 80, log-02 65, log-01 50). Chay lai find lan 2 khop so file.
- CANH BAO: thoi gian sua se gia. Neu task 1 chay sau 2026-11-29, lam moi fixture ngay truoc khi chay (touch -d "1 day ago" cho 6 file, "10 days ago" cho 6 file con lai). Ghi trong ~/thu-tu-chay.txt.
- Vat chung cham: bao cao nd09-bao-cao.txt. Nguoi cham chay lai lenh find (chi doc) va doi chieu.

## R3-093 (Tier B)

- File goc: ~/rung3/nd13-file-lon.bin, 3000000 bytes (tu /dev/urandom).
- Cat thanh 3 phan bang lenh split, ten phan-01, phan-02, phan-03. Du 3 phan, tong dung luong 3 phan bang dung luong file goc (3000000 bytes).
- Ghep lai thanh ~/rung3/nd13-ghep-lai.bin bang lenh cat. Checksum file moi khop checksum file goc (checksum la gia tri live cua file, ghi trong bao cao; nguoi cham tinh lai checksum cua ca 2 file).
- Bao cao gom kich thuoc file goc, kich thuoc tung phan, checksum goc, checksum moi.
- Vat chung cham: bao cao + 3 file phan + file ghep lai. Nguoi cham tinh checksum va doi chieu.

## R3-094 (Tier B)

- Script ~/rung3/nd14-in-bien.sh in 3 bien R3_TEN, R3_TUOI, R3_THANH_PHO, moi bien 1 dong theo mau "TEN=<gia tri>".
- Gia tri tu file nd14-gia-tri.txt: R3_TEN=An, R3_TUOI=25, R3_THANH_PHO=Ha Noi.
- Lan 1: TEN=An, TUOI=25, THANH_PHO=Ha Noi. Lan 2: doi gia tri 1 bien, chi dong cua bien do doi. Lan 3: tra lai gia tri cu, ket qua giong lan 1.
- 3 file ket qua rieng co timestamp trong ~/rung3-chung-cu/R3-094/: lan-1-YYYYMMDD-HHMMSS.txt, lan-2-YYYYMMDD-HHMMSS.txt, lan-3-YYYYMMDD-HHMMSS.txt.
- Vat chung cham: 3 file ket qua + bao cao. Nguoi cham doi chieu 3 lan chay.

## R3-096 (Tier B)

- 2 file: ~/rung3/nd16-cu.conf va ~/rung3/nd16-moi.conf. Luc dau co dung 4 dong khac: cong 8080 sang 9090; che_do dem sang ngay; ngon_ngu vi sang en; bo_nho 512 sang 1024.
- File yeu cau nd16-yeu-cau.txt: ghep cong (9090) chi 1 dong nay, giu nguyen 3 dong khac con lai o gia tri cu.
- Sau khi ghep, diff chi con 3 dong khac. Dong da ghep co gia tri moi (9090), 3 dong khac van giu gia tri cu.
- Bao cao gom 4 dong khac luc dau, dong da ghep, so dong khac con lai (3).
- Vat chung cham: bao cao + file cu sau khi ghep. Nguoi cham chay lai lenh diff (chi doc) va doi chieu.

## R3-098 (Tier B)

- File: ~/rung3/nd18-du-lieu.csv, 50 dong du lieu + dong tieu de, cot ten,nhom,so_tien. sha256: 71dd42639dadbd62d458d2304e30f05e7ed227f8b55387f830eadd4262648eea.
- Bang tong theo nhom: NhomA: 14 dong, tong 66193. NhomB: 12 dong, tong 52674. NhomC: 13 dong, tong 69300. NhomD: 11 dong, tong 51018.
- Tong chung: 239185 (bang tong cac nhom).
- Vat chung cham: bao cao nd18-bao-cao.txt. Nguoi cham chay lai lenh awk (chi doc) va doi chieu.

## R3-099 (Tier B)

- File: ~/rung3/nd19-du-lieu.csv, 50 dong du lieu + dong tieu de, cot ten,nhom,diem. sha256: fc7abae0e1b68312eac292518076bea9a9a03984d42d83279403728c2e20bea6.
- Bang trung binh theo nhom (lam tron 2 chu so thap phan): NhomA: 14 dong, trung binh 7.91. NhomB: 12 dong, trung binh 7.09. NhomC: 13 dong, trung binh 7.86. NhomD: 11 dong, trung binh 7.12.
- Sai so 0,01. Chay lan 2 cho file bao cao giong lan 1.
- Vat chung cham: script nd19-xu-ly.py + bao cao nd19-bao-cao.txt. Nguoi cham chay lai script (chi doc, tren ban sao neu can) va doi chieu.

## R3-100 (Tier B)

- Thu muc: ~/rung3/nd20-web, 3 file HTML. Tieu de: trang-chu.html "Trang chu", gioi-thieu.html "Gioi thieu", lien-he.html "Lien he". Moi file lien ket den 2 file con lai.
- sha256: trang-chu 2745056563d23d1cd02261ba134937a40ed188b60a355b81929abbb072da2eba; gioi-thieu e760910beb467319d939d528021ab04167882609dfed724ed88b407791b414b5; lien-he 339c81e9e5be6638e66f7d1078828843969bad168486dbcd42b27d12ad3be1fd.
- May chu: python3 -m http.server 8899 tai thu muc nd20-web. Ca 3 trang tra ve ma 200 qua curl. Sau khi xong, cong 8899 da dong (curl khong ket noi duoc).
- Vat chung cham: bao cao gom cong, ma trang thai 3 trang, tieu de 3 trang. Nguoi cham kiem tra cong da dong va doi chieu tieu de voi file HTML.

## DP-01 (Tier B, du phong trung binh)

- 3 loai tien dien tu tren coingecko.com: Bitcoin, Ethereum, Solana.
- Moi loai ghi: gia USD, thay doi 24 gio. Gia la live tai thoi diem chay; chan ly la anh chup trang coin ngay khi gia hien ra, khong phai gia hien tai.
- Thu tu du phong trung binh: DP-01 truoc, DP-03 sau. Khi 1 task trung binh vo hieu, lay DP-01 neu chua dung.
- Vat chung cham: 3 anh chup trang coin + ket-qua.txt. Nguoi cham doi chieu gia va thay doi 24 gio voi anh chup.
- Ghi chu liveness 2026-11-23 19:23: API coingecko tra ve gia live (bitcoin 61255 USD, ethereum 1719.19 USD, solana 72.32 USD); trang chu coingecko.com tra ve HTTP 403 qua curl (bot protection), can kiem tra bang trinh duyet truoc task 1.

## DP-02 (Tier A, du phong kho)

- Fixture: ~/rung3/dp02-code, 12 file van ban (dp02-01.txt den dp02-12.txt), moi file 20-60 dong. Ten file khong chua dau hai cham.
- 5 tu khoa (chi gom chu cai va so, khong tu nao la chuoi con cua tu khac):
  - alpha7: tong 12, file nhieu hit nhat dp02-01.txt (4 hit)
  - bravo21: tong 9, file nhieu hit nhat dp02-02.txt (3 hit)
  - charlie9: tong 15, file nhieu hit nhat dp02-03.txt (5 hit)
  - delta42: tong 7, file nhieu hit nhat dp02-06.txt (3 hit)
  - echo13: tong 11, file nhieu hit nhat dp02-04.txt (4 hit)
- Tong chung ca 5 tu khoa: 54. So file chua it nhat 1 trong 5 tu khoa: 12 (ca 12 file).
- So hit theo tung file (dem bang grep -r -o -F <tu khoa>, khong dung -w):
  - dp02-01.txt (40 dong): alpha7 4, bravo21 0, charlie9 3, delta42 0, echo13 0
  - dp02-02.txt (35 dong): alpha7 3, bravo21 3, charlie9 0, delta42 1, echo13 0
  - dp02-03.txt (45 dong): alpha7 2, bravo21 0, charlie9 5, delta42 0, echo13 0
  - dp02-04.txt (30 dong): alpha7 2, bravo21 0, charlie9 2, delta42 0, echo13 4
  - dp02-05.txt (50 dong): alpha7 1, bravo21 2, charlie9 0, delta42 0, echo13 2
  - dp02-06.txt (25 dong): alpha7 0, bravo21 2, charlie9 0, delta42 3, echo13 0
  - dp02-07.txt (60 dong): alpha7 0, bravo21 1, charlie9 0, delta42 1, echo13 0
  - dp02-08.txt (20 dong): alpha7 0, bravo21 1, charlie9 0, delta42 1, echo13 0
  - dp02-09.txt (55 dong): alpha7 0, bravo21 0, charlie9 2, delta42 0, echo13 2
  - dp02-10.txt (38 dong): alpha7 0, bravo21 0, charlie9 2, delta42 0, echo13 2
  - dp02-11.txt (28 dong): alpha7 0, bravo21 0, charlie9 1, delta42 0, echo13 1
  - dp02-12.txt (48 dong): alpha7 0, bravo21 0, charlie9 0, delta42 1, echo13 0
- Moi file nhieu hit nhat la duy nhat (khong co truong hop dong hang cho bat ky tu khoa nao). Khi nhieu file cung so hit cao nhat thi lay file xuat hien dau tien theo thu tu ten file (quy tac nay khong phai dung o day vi khong co truong hop dong hang).
- Du phong kho duy nhat. Khi 1 task kho vo hieu, lay DP-02 neu chua dung; task kho vo hieu thu hai loai khoi mau khong thay the.
- Vat chung cham: bao cao dp02-bao-cao.txt + ban sao trong ~/rung3-chung-cu/DP-02/bao-cao.txt. Nguoi cham chay lai lenh grep -r -o -F (chi doc) va doi chieu tung so.
- Ghi chu: tier-a-check.py da co checker kieu keyword-counts; DP-02 duoc cham bang script. Lenh grep theo key nay la cross-check phu, khong phai phuong phap chinh.

## DP-03 (Tier B, du phong trung binh)

- Lenh: ss -tlnp, output luu vao ~/rung3-chung-cu/DP-03/ss-output.txt, kem anh chup man hinh terminal co timestamp.
- N = 5. Ghi 5 cong co ten tien trinh hien du dau tien theo thu tu cong tang dan. Moi cong ghi: cong, giao thuc, ten tien trinh.
- N toi thieu 3. Neu it hon 5 cong co ten tien trinh thi ghi so cong thuc te va Pass doi theo so do (ghi ro truoc khi chay). Neu it hon 3 cong thi du phong nay tuyen bo vo hieu truoc khi chay.
- Vat chung cham: ss-output.txt + bao-cao.txt + anh chup terminal. Nguoi cham doi chieu bao cao voi file output va anh chup.
- Thu tu du phong trung binh: DP-01 truoc, DP-03 sau.

## DP-05 (Tier A, du phong rat kho)

- Cong cu: sqlite3 tren laptop (xem ruling o dau file). Cung bang, cung du lieu, cung truy van nhu muc 8 cua danh sach.
- Bang san_pham (ma_san_pham, ten, gia): SP01 Ban 150, SP02 Ghe 250, SP03 Den 80, SP04 Tu 400, SP05 Giuong 600.
- Bang don_hang (ma_don, ma_san_pham, so_luong): DH01 SP01 10, DH02 SP01 4, DH03 SP02 5, DH04 SP03 20, DH05 SP04 3.
- Truy van buoc 2 (INNER JOIN lay ten san pham va so luong theo tung don): 5 dong. DH01 Ban 10, DH02 Ban 4, DH03 Ghe 5, DH04 Den 20, DH05 Tu 3.
- Truy van buoc 3 (INNER JOIN kem GROUP BY, tong so luong theo tung san pham): 4 dong. Ban 14, Ghe 5, Den 20, Tu 3.
- Truy van buoc 4 (INNER JOIN kem GROUP BY, tong gia tri theo tung san pham): 4 dong. Ban 2100, Ghe 1250, Den 1600, Tu 1200.
- File co so du lieu .db la tuy chon (chi khi trang/cong cu co nut tai xuong). Anh chup man hinh ket qua cua ca 3 truy van moi la vat chung bat buoc.
- Du phong rat kho duy nhat. Khi 1 task rat kho vo hieu, lay DP-05 neu chua dung; task rat kho vo hieu thu hai loai khoi mau khong thay the.
- Vat chung cham: ket-qua.txt + anh chup ket qua 3 truy van. Nguoi cham doi chieu file ket qua voi anh chup man hinh. Checker so sanh cac cap ten va gia tri trong ket-qua.txt.

## Ghi chu cuoi

- Thu tu du phong co dinh trong file du-phong.txt truoc task 1: trung binh DP-01 roi DP-03; kho DP-02; rat kho DP-05. Khi 1 task vo hieu, lay du phong DAU TIEN CHUA DUOC DUNG cung do kho. Nguoi cham ghi cap thay the (task vo hieu va du phong thay the) vao du-phong.txt luc quyet dinh, kem ten ca 2 nguoi cham.
- Mot su co dich vu lam vo hieu nhieu task tinh la 1 su kien vo hieu doi voi muc tran 5, nhung moi task bi anh huong van roi khoi mau va van dung quy tac du phong.
- Cham tung task TRUOC khi dat lai (reset) task do. Moc thoi gian ket qua cham phai truoc muc reset-log cua task do. Voi task ma trang thai khong ton tai den luc cham, vat chung cham duoc la file da luu trong ~/rung3-chung-cu/R3-xxx/ nhu ghi o tung muc tren.
- Vat chung cham cua moi task nam trong ~/rung3-chung-cu/R3-xxx/ (hoac DP-xx). Khong co anh chup hoac file ket qua thi task do khong duoc cham pass, tru khi task ghi ro bang chung la trang thai tren dich vu.
- Viec con mo truoc task 1 (khong phai loi cua key file, ghi de dieu phoi vien theo doi): tai khoan test R3-029 va R3-016 chua co (can browser task); kiem tra WAVE day du cho R3-009 chua xong (can browser); xac nhan trinh duyet that cho R3-011 (timeanddate.com) chua xong; xac nhan 5 ten san pham R3-029 tren cua hang demo chua xong.
