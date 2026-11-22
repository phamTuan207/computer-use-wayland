# Batch 10 council 3 redo: caveat 1 va cac so dan xuat task 1

Ngay kiem tra: 22/11/2026, 11:18-11:30 +07.
Pham vi: kiem chung lai bang doc truc tiep 6 file goc tren nhanh origin/todolist-push, tinh lai bang Python. Lan council 3 truoc bi chan, khong doc duoc file, de lai caveat 1 o trang thai chua kiem chung. Lan nay doc truc tiep va tinh lai day du.
Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. File test-w.txt (0 byte, untracked) de nguyen.

## 1. Nguon va lenh da dung

- `git fetch origin todolist-push`, ket qua: origin/todolist-push ve d2da4820cbc31adbad39c93670f30a01ff2c7709.
- `git ls-tree -r origin/todolist-push -- improvements/s2-flip-runs/ improvements/worker-click4-s2-flip-log.md`, ket qua: 6 file, blob khop voi bao cao task 1 muc 2:
  - run-1.json, blob 48cccec7df4388c27bf154f4d40f44c48620e6cd
  - run-2.json, blob 241e7d9fe126328a68de71d710bb30e316928c37
  - run-3.json, blob 1602376c1cb5858556dbd9bce9ff3ad27786e5d0
  - run-4.json, blob 31150c122325dffa956a7114aa212a14d964c7ce
  - run-5.json, blob 7f46be5cdba44de7bb53fbdcbefee0c64431ef59
  - worker-click4-s2-flip-log.md, blob f240600b3ce20d8b62fa2a51d28c4ef2a5d8decf
- `git show origin/todolist-push:<duong dan>` cho ca 6 file, trich ra /tmp/c3/ (chi doc, khong sua nhanh, khong chay script nao trong repo).
- Python3 doc 5 file JSON va tinh lai, script /tmp/c3/recompute.py (chi doc /tmp/c3, khong ghi vao repo).
- `git ls-tree -r origin/todolist-push -- improvements/` kiem tra PNG P9 va s2-diag2.mjs: khong co file nao.
- `grep -n 'DO NOT EXPAND' coord/clone1.md` (chi doc): 5 dong khop, xem muc 5.

## 2. Caveat 1: nhan "CDP timeout" o run 1 Chromium, DA KIEM CHUNG

### 2.1 run-1.json co chu "CDP timeout" khong

Khong. Lenh `grep -c 'CDP timeout' run-1.json` tra ve 0. Ca 4 run con lai moi run co dung 1 lan:
- run-2.json dong 90: "dom_act ok False completed 0 ms 5002 error CDP timeout: Input.dispatchMouseEvent"
- run-3.json dong 90: "dom_act ok False completed 0 ms 5003 error CDP timeout: Input.dispatchMouseEvent"
- run-4.json dong 90: "dom_act ok False completed 0 ms 5003 error CDP timeout: Input.dispatchMouseEvent"
- run-5.json dong 90: "dom_act ok False completed 0 ms 5003 error CDP timeout: Input.dispatchMouseEvent"

Dong log goc cua run 1 Chromium, doc truc tiep tu run-1.json:
- browsers.chromium.program.log: ["dom_act ok False completed 0 ms 5003"]
- browsers.chromium.program.error: "assert failed: dom_act failed"
- browsers.chromium.program.elapsed_ms: 5103.697
- browsers.chromium.program.ok: false

Trich dan cua bao cao task 1 muc 5 ve dong log goc run 1 la DUNG, da xac nhan doc lap.

### 2.2 Worker log co gan nhan "CDP timeout" cho run 1 khong

Co, o bang tong ket, va khong co o muc mo ta run 1. Hai cho nay mau thuan nhau, can tach ro:
- Muc mo ta run 1 (dong 436-470): khong co chu "CDP timeout". Ghi dung dong log goc "dom_act completed 0 in 5003ms", roi suy luan: 5003ms bang dung timeout 5000ms cua CDP call trong cdp.mjs (dong 60). Day la suy luan tu thoi gian, khong phai trich chu loi goc.
- Muc mo ta run 2 (dong 485-487): "log now names it: 'error CDP timeout: Input.dispatchMouseEvent'". Chu "now" o day xac nhan run 1 chua co chu do, run 2 moi co, nho thay doi ghi log sau run 1.
- Bang tong ket muc 6, dong 581, nguyen van: "| 1 | 33655.6 | sent | failed-unverified | 163.7ms, completed 3 | 5103.7ms, completed 0, CDP timeout Input.dispatchMouseEvent |". O bang nay gan nhan CDP timeout cho run 1 giong het 4 run kia. Doi chieu voi run-1.json thi o bang nay SAI CHU cho run 1: chu "CDP timeout" khong co trong log goc run 1.

### 2.3 Cau "cung mot loi" o muc 7 bao cao task 1

Bao cao task 1 muc 7 viet: "Chromium ket o Input domain o ca 5 run voi cung mot loi timeout 5000 ms." Voi run 1, "cung mot loi" nay KHONG dung theo nghia chu loi goc, vi run-1.json khong co chu "CDP timeout". No chi dung theo nghia suy luan: elapsed 5103.7ms cua run 1 khop mau timeout 5s nhu 4 run kia (5102.6ms den 5106.3ms), cung sub-step (dom_act completed 0), cung error "assert failed: dom_act failed". Cau nay PHAI SUA thanh suy luan tu elapsed, khong viet nhu ca 5 run deu co cung chu loi goc. Vi du: "Chromium ket o Input domain o ca 5 run, 4 run co chu loi CDP timeout Input.dispatchMouseEvent, run 1 suy ra tu elapsed 5103.7ms khop mau timeout 5s."

### 2.4 Caveat 1 co lam yeu verdict khong

KHONG. Ly do, tu so tinh lai o muc 3: khong co con so nao trong muc 4 cua bao cao task 1 phu thuoc vao chu "CDP timeout" xuat hien trong run 1. Verdict dung tren ket qua gui duoc (Brave 5/5, Chromium 0/5), 0 model call, va per-run 0/5, tat ca lay tu truong outcome, verified, model_calls trong JSON. Sai chu o mot o bang va mot cau o muc 7 la loi dien dat, khong doi so nao va khong doi verdict. Can sua cau chu, khong can sua so.

## 3. Cac so dan xuat: tinh lai tu 5 file JSON, TAT CA KHOP

Phuong phap: Python statistics.median tren 5 gia tri, moi run mot gia tri. Truong dung ghi ro tung so.

### 3.1 Phase split median, truong phase_split_ms.<key>

- model: [0, 0, 0, 0, 0], median 0. KHOP.
- ssh: [15623.9, 14931.0, 15011.0, 15648.1, 15498.0], median 15498.0. KHOP.
- broker: [689.1, 807.8, 708.2, 633.7, 614.0], median 689.1. KHOP.
- observe: [1500.5, 1612.5, 1487.9, 1053.4, 1347.2], median 1487.9. KHOP.
- act: [5267.4, 5260.3, 5254.6, 5240.6, 5235.7], median 5254.6. KHOP.
- verify: [10424.2, 11129.8, 10409.7, 10437.5, 10361.1], median 10424.2. KHOP.
- setup: [148.3, 209.3, 188.1, 105.9, 108.6], median 148.3. KHOP.
- residual: [2.3, 2.5, 2.5, 2.4, 2.3], median 2.4. KHOP.

### 3.2 Mux baseline median 790.5 ms, KHOP

Truong mux_baseline_ms, gia tri [790.5, 777.8, 789.9, 836.1, 826.9], median 790.5.

### 3.3 Brave per-browser wall median 2698.9 ms, KHOP

Truong browsers.brave.wall_ms, gia tri [2621.9, 2731.6, 2703.2, 2698.9, 2592.5], median 2698.9.

### 3.4 Chromium V12 median 11045.1 ms, KHOP

Truong browsers.chromium.v12.ms, gia tri [11045.1, 11747.4, 11023.1, 11092.6, 11034.1], median 11045.1. Luu y: truong browsers.chromium.v12.elapsed_ms co median khac, 10052, nen phai dung truong ms moi ra 11045.1.

### 3.5 Cac so chinh khac, tinh lai them

- wall_ms [33655.6, 33953.2, 33061.9, 33121.8, 33166.9], median 33166.9. KHOP.
- Brave program elapsed_ms median 150.12, Chromium program elapsed_ms median 5104.459. KHOP.
- Brave outcome sent 5/5, Chromium outcome failed-unverified 5/5. KHOP.
- model_calls 0 ca 5 run. KHOP.
- Chromium program log ca 5 run nhu muc 2.1, Brave program log "dom_act ok True completed 3 ms 72/51/53/48/41". KHOP.
- Routing source dom-chromium ca 10 quyet dinh, fell_through rong ca 10. KHOP.
- p9.ok true 10/10 trong JSON. KHOP ve gia tri JSON, nhung anh P9 khong co tren nhanh de doi chieu, xem muc 4.

## 4. Caveat 2: anh P9 va script chan doan, KHONG lam yeu verdict

Lan council 3 truoc da ghi caveat 2 khong lam yeu verdict. Lan nay xac nhan lai bang ls-tree: thu muc improvements/s2-flip-runs/ tren origin/todolist-push chi co 5 file JSON, khong co PNG nao; khong co file s2-diag2.mjs trong improvements/. Gioi han con lai nhu lan truoc: p9.ok true 10/10 chi la gia tri trong JSON, khong co anh de doi chieu bang mat; ket qua chan doan rieng khong chay lai duoc. Cac so Brave 5/5 va Chromium 0/5 lay tu truong JSON outcome va verified, khong lay tu anh, nen gioi han nay khong doi verdict.

## 5. Cac khoang G1-G6 cua lan truoc

- G1. Trich dan HEAD loi thoi: XAC NHAN. Bao cao task 1 muc 2 ghi HEAD 2ed0caf. Luc lan nay fetch, origin/todolist-push la d2da4820cbc31adbad39c93670f30a01ff2c7709. Blob cua ca 6 file van khop voi bao cao, nen so khong doi vi ly do nay. Chi can ghi ro HEAD tai thoi diem kiem chung.
- G2. So phu thieu duong dan tinh lai: XAC NHAN la khoang trong trong bao cao, va DA DONG trong lan redo nay. Ten truong va day gia tri day du o muc 3, script tinh o /tmp/c3/recompute.py.
- G3. O bang worker log cho run 1 khong trich nguyen van: DA GIAI QUYET. Nguyen van dong 581 da trich o muc 2.2. O bang co chu "CDP timeout Input.dispatchMouseEvent" cho run 1, va doi chieu run-1.json thi chu do khong co trong log goc run 1. Day la bang chung truc tiep cho caveat 1, khong phai chi tom tat.
- G4. Trich dan DO NOT EXPAND va doan chan doan chua doc lai: DA GIAI QUYET. Worker log dong 636: "### Recommendation: DO NOT EXPAND". Dong 637: "Do not expand the flip to more classes." Dong 168-169 trong muc timeline: "Verdict written (section 6): do not expand." Doan chan doan rieng, muc run 2 dong 492-495: "a standalone node script (/tmp/s2-diag2.mjs) on the live Chromium tab shows baseline Runtime.evaluate 3ms, scrollIntoView 1ms ... and a bare Input.dispatchMouseEvent mouseMoved TIMES OUT at 5000ms." Tom tat cua bao cao task 1 ve doan nay dung ve noi dung. File script khong co trong repo nen khong chay lai duoc, gioi han nay van dung.
- G5. Trich dan verdict hien co chua doc truc tiep: DA GIAI QUYET. Doc truc tiep muc 6 cua worker log (muc 2.2 va muc 5 o tren) va grep coord/clone1.md (chi doc): 5 dong chua "DO NOT EXPAND", dong 3750, 3760, 3782, 3784, 3825 tai thoi diem doc (so dong co the dich khi coord duoc ghi them). Verdict DO NOT EXPAND co trong ca worker log va coord, trich dan cua bao cao task 1 muc 5 la DUNG.
- G6. Gia thuyet workspace 2 chua chung minh: XAC NHAN, van la gia thuyet. Worker log muc run 2: "Leading explanation (not proven)" va "I did NOT switch workspaces to test this". Muc 6, lever 1: "Prove or kill the visibility hypothesis". Khong duoc dung gia thuyet nay nhu ket luan trong bat cu bao cao tiep theo nao cho den khi co chung cu moi.

## 6. Ket luan

- Caveat 1: DA KIEM CHUNG DOC LAP. Run 1 Chromium khong co chu "CDP timeout" trong run-1.json, worker log gan nhan do cho run 1 o bang tong ket dong 581, muc mo ta run 1 thi khong gan. Cau muc 7 cua bao cao task 1 ve "cung mot loi" phai sua thanh suy luan tu elapsed 5103.7ms. Caveat 1 KHONG lam yeu verdict, vi khong so nao phu thuoc vao chu do o run 1.
- Cac so dan xuat: TAT CA KHOP. Phase split median, mux baseline median 790.5 ms, Brave per-browser wall median 2698.9 ms, Chromium V12 median 11045.1 ms, median wall 33166.9 ms, deu tinh lai dung tu truong JSON ghi ro o muc 3.
- Caveat 2: KHONG lam yeu verdict. Da xac nhan lai: khong co PNG P9, khong co s2-diag2.mjs tren nhanh.
- G1-G6: G1 xac nhan (HEAD loi thoi, so khong doi), G2 da dong (ten truong va script o muc 3), G3-G5 da giai quyet bang trich dan nguyen van, G6 xac nhan (gia thuyet chua chung minh).
- Verdict chung: DO NOT EXPAND DUNG, tren so do chinh toi tinh lai tu 5 file JSON goc. Chi can sua cau chu o muc 7 bao cao task 1 (suy luan tu elapsed cho run 1), khong can sua so nao. Lan kiem tra redo nay LA mot lan kiem chung doc lap day du ve so, khac voi lan council 3 truoc chi kiem tra duoc blob va ls-tree.
