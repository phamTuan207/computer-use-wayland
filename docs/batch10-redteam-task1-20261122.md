# Batch 10 redteam task 1: tan cong bao cao kiem chung S2 flip

Ngay tan cong: 22/11/2026, 11:12-11:25 +07.
Doi tuong: docs/batch10-task1-s2flip-verify-20261122.md.
Phuong phap: doc lai 5 file JSON goc tren nhanh origin/todolist-push, tinh lai bang script Python rieng, doi chieu tung so, tim so sai, logic sai, doc chon loc, hoac bang chung bia.

## VERDICT: SURVIVES

Khong tim thay loi so nao, khong tim thay logic sai nao, khong tim thay bang chung bia nao. Bao cao dung. Chi co 3 ghi chu nho o muc 3, khong doi so nao va khong doi verdict.

## 1. Nguon da xac minh

- Chay `git fetch origin todolist-push`, ket qua: nhanh ve d2da482.
- `git ls-tree -r origin/todolist-push -- improvements/s2-flip-runs/ improvements/worker-click4-s2-flip-log.md` tra ve dung 6 blob ma bao cao da ghi: 48cccec7df4388c27bf154f4d40f44c48620e6cd, 241e7d9fe126328a68de71d710bb30e316928c37, 1602376c1cb5858556dbd9bce9ff3ad27786e5d0, 31150c122325dffa956a7114aa212a14d964c7ce, 7f46be5cdba44de7bb53fbdcbefee0c64431ef59, f240600b3ce20d8b62fa2a51d28c4ef2a5d8decf.
- Trich 6 file bang `git show origin/todolist-push:<duong dan>` ra /tmp/s2flip-redteam/, chi doc, khong sua nhanh, khong commit, khong push, khong sua coord/clone1.md, khong sua coord/clone2.md, khong dong den test-w.txt.
- Luu y ve HEAD: bao cao ghi HEAD 2ed0caf. Commit 2ed0caf co thoi gian 2026-11-22 04:01:44 +0000, tuc 11:01 +07. Commit d2da482 co thoi gian 04:11:05 +0000, tuc 11:11 +07, roi vao trong khung 11:04-11:15 cua bao cao. Nhanh da tien trong luc kiem chung, nhung ca 6 blob deu trung khop voi bao cao, nen so lieu khong doi. Day la ghi chu ve thoi diem, khong phai loi.

## 2. Cac dot tan cong va ket qua

### A1. Median wall time

Tan cong: tinh lai median bang statistics.median va bang cach lay phan tu giua cua day da sap xep, kiem tra xem bao cao co chon sai dinh nghia median hay tinh sai khong.
Lenh: `python3 /tmp/s2flip-redteam/recompute.py`.
Output: walls raw [33655.6, 33953.2, 33061.9, 33121.8, 33166.9], sorted [33061.9, 33121.8, 33166.9, 33655.6, 33953.2], median 33166.9, mean 33391.9, min 33061.9, max 33953.2.
Ket qua: KHOP. Bao cao ghi 33166.9 ms, 33.17 s, lam tron 33.2 s, dung. Doi sang giay: 33166.9 ms bang 33.1669 s, lam tron 33.17 s o 2 chu so va 33.2 s o 1 chu so, dung.

### A2. Brave 5/5, Chromium 0/5, kiem tra cheo 3 lop doc lap

Tan cong: khong tin truong outcome, doi chieu outcome voi program.ok, cb1.verified, va v12.found tung run, tung trinh duyet, tim run nao mau thuan nhau.
Output: brave outcome sent 5/5, program ok True 5/5, cb1 verified True 5/5, v12 found True 5/5, attempts 1 ca 5 run. Chromium outcome failed-unverified 5/5, program ok False 5/5, cb1 verified False 5/5, v12 found False 5/5, attempts 40 ca 5 run. Khong co run nao lech.
Ket qua: KHOP. Khong co mau thuan nao trong JSON. Bao cao khong chi doc outcome.

### A3. Model call bang 0

Tan cong: kiem tra model_calls o 3 cap: top-level moi run, per-browser moi run, va phase_split_ms.model moi run, tim lan goi model nao bi giau.
Output: total model_calls top-level 0, per-browser sum 0, phase model [0, 0, 0, 0, 0], median 0.
Ket qua: KHOP. Bao cao ghi 0 lan, dung o ca 3 cap.

### A4. Per-send va per-run, dinh nghia ap dung co nhat quan khong

Tan cong: tinh lai per-send 5/10, per-run ca 2 send verified 0/5, per-run ca 2 send deu sent 0/5, per-run it nhat 1 send verified 5/5. Kiem tra xem bao cao co ap dinh nghia per-run khac nhau giua cac run, hoac giau so 5/5 nao khong.
Output: per-send 5/10 bang 0.5, per-run both verified 0/5, per-run both sent 0/5, per-run any verified 5/5.
Ket qua: KHOP. Bao cao ghi ca 3 so: per-send 50%, per-run ca 2 send 0/5, per-run it nhat 1 send 5/5. Dinh nghia ap dung deu cho ca 5 run, khong co doc chon loc. So 5/5 any-pass duoc ghi cong khai, khong bi giau.

### A5. Cac median phu: phase split, mux, per-browser wall, program elapsed

Tan cong: tinh lai toan bo median phu ma bao cao da doi chieu.
Output: phase ssh median 15498.0, broker 689.1, observe 1487.9, act 5254.6, verify 10424.2, setup 148.3, residual 2.4. Mux baseline median 790.5, day [790.5, 777.8, 789.9, 836.1, 826.9]. Brave wall median 2698.9, Chromium wall median 17759.2. Brave program median 150.12, Chromium program median 5104.459. Chromium v12 ms median 11045.1, day sap xep [11023.1, 11034.1, 11045.1, 11092.6, 11747.4].
Ket qua: KHOP. Tat ca trung voi bao cao. Gia tri ngoai le run 2 Chromium v12 11747.4 ms khong doi median, vi median lay phan tu giua 11045.1.

### A6. Dom_act, CDP timeout, va cau chu run 1

Tan cong: trich so ms tu log program moi run, kiem tra chu CDP timeout co that trong log goc khong, tim xem bao cao co gan loi timeout cho run 1 mot cach sai khong.
Output: brave dom_act [72, 51, 53, 48, 41], min 41, max 72. Chromium dom_act [5003, 5002, 5003, 5003, 5003], min 5002, max 5003. Chu CDP timeout co trong log Chromium: [False, True, True, True, True] cho run 1 den run 5. Chromium errors deu la assert failed: dom_act failed, 5/5.
Ket qua: KHOP, voi ghi chu da duoc bao cao tu neu. Log run 1 la dom_act ok False completed 0 ms 5003, khong co chu CDP timeout, nhung elapsed 5103.697 ms khop mau timeout 5 s nhu 4 run kia, cung loi assert, cung completed 0. Bao cao da ghi ro diem nay o muc 5, goi la cau chu chua chinh xac o mot o trong bang, khong doi so. Tan cong nay khong pha duoc bao cao, vi bao cao da tu chi ra truoc.

### A7. Anh P9 khong co tren nhanh

Tan cong: kiem tra xem 10 duong dan PNG ma JSON tro toi co ton tai tren nhanh todolist-push khong, va xem truong p9.ok co dang tin khong.
Lenh: `git ls-tree -r origin/todolist-push -- improvements/s2-flip-runs/`, roi `git ls-tree -r origin/todolist-push -- improvements/ | grep -i p9`.
Output: thu muc chi co 5 file JSON, khong co file PNG nao, grep p9 tra ve rong. Trong JSON, p9 ok True 10/10.
Ket qua: KHOP voi ghi chu cua bao cao. Bao cao da ghi ro gioi han nay o muc 6: khong mo lai duoc anh P9 de doi chieu bang mat. P9 khong phai bang chung chiu tai verdict, vi CB-1 va V12 trong JSON da xac nhan doc lap viec gui duoc o ca 5 run Brave va that bai o ca 5 run Chromium. Khong co bang chung bia o day, chi co gioi han da duoc khai bao.

### A8. Ket luan DO NOT EXPAND co bi ep buoc khong, day la dot tan cong manh nhat

Tan cong: doc dinh nghia plateau trong worker log muc 0. Theo chu cua gate, median duoi 60 s thi plateau CHUA dat, va lop van mo rong. Vay DO NOT EXPAND co mau thuan voi chinh gate ma no vien dan khong. Thu doc thay the: chi can median 33.2 s duoi 60 s thi EXPAND.
Bang chung: worker log ghi plateau REACHED neu median tren 60 s trong 5 run, below 60 s median, S2 is still improving and the class expands. Bao cao muc 7 tu thua nhan median 33.2 s nam duoi nguong, nen theo chu cua gate thi plateau CHUA dat.
Ket qua: TAN CONG THAT BAI, vi bao cao da doi dien truc tiep voi mau thuan nay thay vi giau no. Ly do: gate do median wall, nhung median thap nay den tu viec run that ket thuc som, Chromium chi ton 5 s timeout cong 10 s V12 poll thay vi gui thanh cong. Dinh nghia lop doi ca 2 send deu verified trong mot run, va 0/5 run dat. Mo rong theo chu gate ma bo qua 0/5 thi la truyen mot nua hong sang cac lop khac. Worker log muc Plateau cung ghi ro lap luan letter vs spirit nay truoc bao cao, bao cao chi kiem chung lai. DO NOT EXPAND khong phai suy ra tu so hoc don thuan, no la doc hop ly duy nhat phu hop voi ca postcondition CB-1 va so lieu. Doc thay the EXPAND doi phai bo dinh nghia lop, khong co co so trong JSON.

### A9. Tinh nhat quan noi bo cua JSON: phase split cong lai co bang wall khong

Tan cong: cong phase_split_ms moi run so voi wall_ms, cong spans so voi wall_ms, tim so lieu noi bo mau thuan.
Output: phase sum tru wall: run 1 0.1, run 2 0.0, run 3 0.1, run 4 -0.2, run 5 0.0 ms. Spans sum kem wall 1558.2 den 1674.6 ms moi run.
Ket qua: KHOP o phan co y nghia. Phase split khop wall trong sai so lam tron 0.2 ms, chung to ke toan thoi gian nhat quan. Khoang chenh spans khoang 1.6 s moi run khong duoc giai thich trong JSON, nhung bao cao khong dua ra tuyen bo nao ve tong spans, nen day khong phai loi cua bao cao. Ghi nhan nhu quan sat, khong phai loi pha.

### A10. Tim bang chung bia hoac doc chon loc: message, target, dry run, routing

Tan cong: kiem tra message moi run co phan biet khong, target_id co on dinh khong, dry_run co that la false khong, routing co that la dom-chromium ca 10 quyet dinh khong.
Output: message Brave R1 den R5 va Chromium R1 den R5 deu phan biet theo run. Target Brave on dinh 06074E282C000A95EF89CC9EBB8F9713 ca 5 run, Chromium on dinh D1374C7C994D3DA72678E20C7FD099A0 ca 5 run. Dry_run False ca 5 run. Routing source dom-chromium, fell_through rong, ca 10 quyet dinh.
Ket qua: KHOP. Khong co dau hieu chep so tu run khac, khong co run dry run bi tinh la run that, khong co lan roi xuong screenshot nao bi giau.

## 3. Ghi chu nho, khong phai loi pha

- HEAD cua nhanh da tien tu 2ed0caf luc 11:01 sang d2da482 luc 11:11 trong khung kiem chung, xem muc 1. Ca 6 blob khong doi, so lieu khong doi.
- Worker log co 2 muc deu danh so 6, muc thu 2 chi ghi to be filled, trong. Day la thieu sot trinh bay cua log goc, bao cao khong nhac den, nhung no khong anh huong so nao.
- Khoang chenh spans khoang 1.6 s moi run khong duoc giai thich, xem A9. Khong anh huong verdict.
- Bao cao goc khong co dau gach ngang dai hay gach ngang ngan dai, khong co thong tin ca nhan. Kiem tra bang Python: em dash 0, en dash 0, khong co ten that hay email.

## 4. Ket luan

VERDICT SURVIVES. Da thu 10 dot tan cong: median, dem Brave va Chromium kem kiem tra cheo 3 lop, model call 3 cap, per-send va per-run, median phu, dom_act va cau chu CDP timeout run 1, anh P9, logic DO NOT EXPAND doi voi chu gate, tinh nhat quan noi bo, va tim bang chung bia. Tat ca deu khop. Dot manh nhat la A8, ve mau thuan chu gate voi DO NOT EXPAND, that bai vi bao cao da khai bao mau thuan va lap luan dua tren postcondition CB-1 va 0/5 run hoan thanh. Khong can sua so nao trong bao cao. Huong tiep theo trong bao cao giu nguyen: chung minh hoac loai bo gia thuyet visibility truoc, roi moi xet set_value hoac buoc 9.
