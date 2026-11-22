# Batch 10 council 2: kiem tra logic verdict task 1 (S2 flip DO NOT EXPAND)

Ngay kiem tra: 22/11/2026, 11:12-11:35 +07.
Vai tro: council 2, chi kiem tra logic suy luan trong docs/batch10-task1-s2flip-verify-20261122.md, khong phai kiem tra lai toan bo so tu dau, nhung da tinh lai doc lap tu JSON goc.
Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. File test-w.txt de nguyen.

## 1. Nguon va phuong phap

- Nhanh: origin/todolist-push, HEAD d2da482 luc fetch. Bao cao task 1 ghi HEAD 2ed0caf. Nhanh da tien 1 commit sau khi bao cao task 1 xong (d2da482, test P2 element-ref). Ca 6 blob van giong het bao cao task 1: run-1.json 48cccec7, run-2.json 241e7d9f, run-3.json 1602376c, run-4.json 31150c12, run-5.json 7f46be5c, worker log f240600b. Nen cac su kien ma suy luan dua vao khong doi.
- Doc 5 file JSON goc bang git show (chi doc), tinh lai bang script Python cua rieng toi (khong chay code trong repo).
- Doc muc 0 va muc 6 cua worker log de lay dinh nghia goc cua lop va nguong plateau.
- Anh P9: git ls-tree cho thay 0 file png trong improvements/s2-flip-runs/ tren nhanh. Giong nhu bao cao task 1 da ghi. Khong mo lai duoc anh P9.
- Lenh da chay: git fetch origin todolist-push; git ls-tree -r origin/todolist-push; git show cho 5 JSON va worker log; grep "CDP timeout" tung JSON; script Python tinh lai median, ti le, phase split va phan thuc.

## 2. So lieu tinh lai doc lap (tu JSON goc)

- wall_ms: [33655.6, 33953.2, 33061.9, 33121.8, 33166.9], sap xep [33061.9, 33121.8, 33166.9, 33655.6, 33953.2], median 33166.9 ms = 33.17 s, mean 33391.9 ms. Khop bao cao task 1.
- Brave outcome: sent 5/5, cb1 verified true 5/5, v12 found true 5/5, attempt 1 ca 5 run. Chromium outcome: failed-unverified 5/5, cb1 verified false 5/5, v12 found false 5/5, attempt 40 ca 5 run.
- Model call: 0 tong cong, o ca 3 cho: top-level model_calls 0 ca 5 run, model_calls tung trinh duyet 0 ca 10 luot, phase_split_ms.model 0 ca 5 run. Khop.
- Per-send: 5/10 = 50%. Per-run (ca 2 send verified): 0/5 = 0%. Per-run (it nhat 1 send verified): 5/5. Khop.
- Brave program elapsed median 150.12 ms, dom_act 41-72 ms. Chromium program elapsed median 5104.459 ms, dom_act 5002-5003 ms. Khop.
- Chromium v12 ms median 11045.1 ms, 40 attempt. Khop.
- Phase split median: ssh 15498.0, broker 689.1, observe 1487.9, act 5254.6, verify 10424.2, setup 148.3, residual 2.4. Khop.
- Mux baseline median 790.5 ms. Brave wall theo trinh duyet median 2698.9 ms. Khop.
- Routing: dom-chromium 10/10, fell_through rong 10/10. Observe khong truncated 10/10. Dry run false 5/5. Khop.
- Chu "CDP timeout": run 1 co 0 lan, run 2 den run 5 co 1 lan moi run (trong log cua program). Khop bao cao task 1 muc 5.

Ket luan muc nay: khong co con so nao lech. Moi so ma suy luan dua vao deu dung.

## 3. Kiem tra tung buoc suy luan

### 3.1 Ket luan co suy ra tu so khong

Dung. Lop chi dat khi ca 2 send deu verified trong mot run. 0/5 run dat, nen lop khong dat. Per-send 50% khong cuu duoc lop vi dinh nghia lop la theo run. Model 0 o ca 3 cho nen model khong dong gop thoi gian nao. Ket luan DO NOT EXPAND suy ra truc tiep tu 0/5 nay, khong can them gia thuyet nao.

### 3.2 Dinh nghia lop co ap dung dung khong

Dung. Dinh nghia goc trong worker log muc 0: lop la clone chat sends, gom Brave + Chromium, chay live 5 lan, cham bang V12 sent-bubble gate. Muc 6 cua log: per run (both sends verified) 0/5. Bao cao task 1 dung dung dinh nghia nay, va dung CB-1 verified (khong phai envelope ok) de xet dat hay khong, giong log. Ca 3 dau hieu (outcome, cb1.verified, v12.found) dong nhat o ca 10 luot trinh duyet, nen khong co truong hop lap lo nao.

### 3.3 Nut that la co che, khong phai model

Dung, voi gioi han da ghi. Bang chung: model 0 o ca 3 cho; Brave gui duoc trong 41-72 ms dom_act, chung to co che chay duoc khi Input tra loi; Chromium ket o cung mot diem o ca 5 run, dom_act 5002-5003 ms, program elapsed khoang 5104 ms, loi giong nhau; observe thanh cong ca 2 trinh duyet (53-70 element, khong truncated); routing dom-chromium 10/10, khong roi xuong screenshot. Gia thuyet workspace 2 chua duoc chung minh, bao cao task 1 ghi ro nhu vay. Script chan doan rieng khong co trong repo nen khong chay lai duoc, bao cao task 1 cung ghi ro. Nhung gioi han nay khong doi ket luan ve nut that.

### 3.4 Median 33.2 s duoi nguong plateau 60 s

Bao cao task 1 ghi dung chu cua gate: median 33.2 s duoi 60 s nen theo chu thi plateau CHUA dat. Bao cao cung ghi dung su cang thang giua chu va tinh than cua gate: lop khong hoan thanh thi khong the mo rong. Cach doc theo tinh than nay co co so trong muc 0 cua log: cac run duoc cham bang V12 sent-bubble gate, tuc median chi co nghia tren run hoan thanh. Phan nay xu ly dung. Nhung ly do cu the ma bao cao dua ra de giai thich median thap thi sai chieu (xem gap 1 o muc 4).

### 3.5 Per-send so voi per-run: co gay hieu lam khong

Khong. Bao cao dua ca 2 so, ghi ro dinh nghia tung so, va ghi ro so nao cam lop (per-run 0/5). Per-send 50% duoc dat canh per-run 0/5 chu khong dung mot minh. Cach trinh bay nay khong gay hieu lam.

## 4. Cac gap suy luan (liet ke rieng)

### Gap 1: cau "run that ket thuc som" la nguoc chieu so voi du lieu

- Cau co van de: bao cao task 1 muc 7 viet, run that ket thuc som vi Chromium chi ton 5 s timeout cong 10 s V12 poll thay vi gui thanh cong. Log goc muc 6 viet y tuong tu.
- Kiem tra bang so: duong that bai cua Chromium (act wall + verify wall) la 18417.4, 18478.3, 17704.5, 17759.0, 17753.4 ms qua 5 run. Duong thanh cong cua Brave (act wall + verify wall, cung harness, cung run) la 2621.3, 2730.9, 2702.5, 2698.3, 2591.8 ms. Duong that bai dai hon duong thanh cong khoang 15 s moi run.
- Phan thuc: neu Chromium thanh cong nhu Brave (thay act wall va verify wall cua Chromium bang cua Brave, giu nguyen cac span khac), wall moi run se la 17859.5, 18205.8, 18059.9, 18061.1, 18005.3 ms, median 18059.9 ms (18.1 s). That bai lam run dai them 15002.0-15796.1 ms moi run, khong lam run ngan lai.
- Vay 5 s + 10 s dai hon nhieu so voi gui thanh cong (program khoang 0.15 s, verify khoang 1 s). Ve so buoc thi chuong trinh Chromium dung o buoc 0/3, nhung ve thoi gian thi no khong ket thuc som.
- Anh huong: cau nay sai nhung khong doi verdict. Ly do dung de bac median thap la lop khong hoan thanh (0/5), khong phai ly do ve ket thuc som. Sau khi sua, ket luan con vung hon: du thanh cong thi median cung chi khoang 18.1 s, van duoi 60 s, nen nguong wall khong phai la rang buoc quyet dinh o day; rang buoc quyet dinh la ti le dat cua lop (0/5). Can sua cau nay trong ho so, khong can doi verdict.

### Gap 2 (nho): muc 7 bo chu thich ve run 1 ma chinh bao cao da lap o muc 5

- Muc 7 cua bao cao viet Chromium ket o Input domain o ca 5 run voi cung mot loi timeout 5000 ms, ma khong kem chu thich nhu muc 5 cua chinh bao cao.
- Run 1 khong co chu "CDP timeout" trong log goc, chi co dau thoi gian (dom_act 5003 ms, program 5103.697 ms) va loi "assert failed: dom_act failed" giong 4 run kia. Suy luan run 1 cung ket o timeout 5 s la hop ly theo dau thoi gian, nhung muc 7 viet nhu the ca 5 run deu co cung mot chu loi hien ro.
- Day la thieu chinh xac ve cau chu, khong doi so nao va khong doi verdict. Log goc cung viet nhu vay o bang muc 6, bao cao task 1 da bat duoc o muc 5, nhung lai lap lai dang khong chu thich o muc 7.

## 5. Ket luan: VERDICT STANDS

- VERDICT STANDS. Ket luan DO NOT EXPAND la dung va suy ra truc tiep tu so da kiem chung: per-run 0/5, per-send 50%, model 0, nut that la co che.
- 2 gap o muc 4 can ghi vao ho so: gap 1 la cau giai thich median thap bi nguoc chieu (that bai lam run dai them khoang 15 s, phan thuc thanh cong chi khoang 18.1 s), gap 2 la muc 7 bo chu thich ve run 1. Ca 2 gap deu khong doi verdict.
- Huong tiep theo trong bao cao task 1 giu nguyen: chung minh hoac loai bo gia thuyet visibility truoc, roi moi xet set_value hoac buoc 9.
