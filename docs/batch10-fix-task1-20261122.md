# Batch 10 fix task 1: sua chua bao cao kiem chung S2 flip

Ngay sua: 22/11/2026, 11:25-11:40 +07.
Nguoi sua: batch 10 fix agent task 1.
Doi tuong: docs/batch10-task1-s2flip-verify-20261122.md, sua tai cho.
Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. File test-w.txt (0 byte, untracked) de nguyen, khong dong den.

## 1. Nguon va phuong phap kiem chung lai

- Chay `git fetch origin todolist-push` (chi doc), ket qua: origin/todolist-push ve d2da4820cbc31adbad39c93670f30a01ff2c7709, commit "test: failing-first P2 element-ref tests (protocol, validator fix, Zen backend)", thoi gian 2026-11-22 04:11:05 +0000.
- Chay `git ls-tree -r origin/todolist-push -- improvements/s2-flip-runs/ improvements/worker-click4-s2-flip-log.md`, ket qua: dung 6 file, blob khop het voi bao cao task 1 muc 2: run-1.json 48cccec7df4388c27bf154f4d40f44c48620e6cd, run-2.json 241e7d9fe126328a68de71d710bb30e316928c37, run-3.json 1602376c1cb5858556dbd9bce9ff3ad27786e5d0, run-4.json 31150c122325dffa956a7114aa212a14d964c7ce, run-5.json 7f46be5cdba44de7bb53fbdcbefee0c64431ef59, worker-click4-s2-flip-log.md f240600b3ce20d8b62fa2a51d28c4ef2a5d8decf.
- Trich 6 file bang `git show origin/todolist-push:<duong dan>` ra /tmp/fix1/ (chi doc, khong sua nhanh), tinh lai bang script Python cua rieng toi, chay `grep -c 'CDP timeout'` tren tung JSON, doc truc tiep dong 581 va dong 575, 667, 669 cua worker log.
- Cac review da doc: docs/batch10-council1-task1-20261122.md, docs/batch10-council2-task1-20261122.md, docs/batch10-council3-task1-20261122.md, docs/batch10-council3b-task1-20261122.md, docs/batch10-redteam-task1-20261122.md.
- Bao cao sau khi sua: 132 dong (truoc khi sua 117 dong). Kiem tra bang Python: em dash 0, en dash 0, khong co ten that hay email.

## 2. Sua chua 1: gap 1 cua council 2, ly do median thap bi nguoc chieu (quan trong)

Van de: bao cao muc 7 viet run that ket thuc som vi Chromium chi ton 5 s timeout cong 10 s V12 poll thay vi gui thanh cong. Cau nay nguoc chieu so voi du lieu.

Kiem chung lai tu JSON goc, phuong phap: lay span act-chromium cong verify-chromium lam duong that bai, span act-brave cong verify-brave lam duong thanh cong (cung harness, cung run), roi tinh wall phan thuc bang cach thay 2 span cua Chromium bang 2 span cua Brave, giu nguyen cac span khac. Ket qua tinh lai cua toi, tung run:

| run | wall that (ms) | duong that bai (ms) | duong thanh cong (ms) | wall phan thuc (ms) | that bai lam dai them (ms) |
|-----|----------------|---------------------|-----------------------|---------------------|----------------------------|
| 1 | 33655.6 | 18417.4 | 2621.3 | 17859.5 | 15796.1 |
| 2 | 33953.2 | 18478.3 | 2730.9 | 18205.8 | 15747.4 |
| 3 | 33061.9 | 17704.5 | 2702.5 | 18059.9 | 15002.0 |
| 4 | 33121.8 | 17759.0 | 2698.3 | 18061.1 | 15060.7 |
| 5 | 33166.9 | 17753.4 | 2591.8 | 18005.3 | 15161.6 |

- Duong that bai dai 17704.5-18478.3 ms moi run, duong thanh cong chi 2591.8-2730.9 ms.
- Wall phan thuc: [17859.5, 18205.8, 18059.9, 18061.1, 18005.3], median 18059.9 ms (18.1 s). Khop so council 2 dua ra.
- That bai lam moi run dai them 15002.0-15796.1 ms, khong lam run ngan lai.

Da sua trong bao cao muc 7: bo cau "run that ket thuc som", viet lai ly do dung la lop khong hoan thanh (0/5 run dat) nen median khong co nghia tren run hoan thanh, kem day so phan thuc va khoang dai them o tren. Them ket luan: du thanh cong thi median cung chi khoang 18.1 s, van duoi 60 s, nen nguong wall khong phai rang buoc quyet dinh, rang buoc quyet dinh la ti le dat cua lop (0/5). Verdict DO NOT EXPAND khong doi, ket luan con vung hon.

## 3. Sua chua 2: gap 2 cua council 2 va cau chu muc 7 theo council 3 redo, nhan CDP timeout o run 1

Van de: bao cao muc 7 viet Chromium ket o Input domain o ca 5 run voi cung mot loi timeout 5000 ms, nhu the ca 5 run deu co cung chu loi goc. Run 1 khong co chu do trong log goc.

Kiem chung lai tu JSON goc, lenh `grep -c 'CDP timeout' run-N.json`:

- run 1: 0 lan. Dong log goc duy nhat: "dom_act ok False completed 0 ms 5003". Truong program.error: "assert failed: dom_act failed". Truong program.elapsed_ms: 5103.697.
- run 2: 1 lan, dong 90: "dom_act ok False completed 0 ms 5002 error CDP timeout: Input.dispatchMouseEvent".
- run 3: 1 lan, dong 90: "dom_act ok False completed 0 ms 5003 error CDP timeout: Input.dispatchMouseEvent".
- run 4: 1 lan, dong 90: "dom_act ok False completed 0 ms 5003 error CDP timeout: Input.dispatchMouseEvent".
- run 5: 1 lan, dong 90: "dom_act ok False completed 0 ms 5003 error CDP timeout: Input.dispatchMouseEvent".

Kiem chung lai worker log, dong 581, nguyen van: "| 1 | 33655.6 | sent | failed-unverified | 163.7ms, completed 3 | 5103.7ms, completed 0, CDP timeout Input.dispatchMouseEvent |". O bang nay gan nhan CDP timeout cho run 1, doi chieu run-1.json thi chu do khong co trong log goc run 1, nen o bang nay sai chu cho run 1. Muc mo ta run 1 trong log thi khong gan nhan do, chi suy luan tu thoi gian 5003 ms.

Da sua trong bao cao:

- Muc 7: viet lai thanh "Chromium ket o Input domain o ca 5 run, 4 run co chu loi CDP timeout Input.dispatchMouseEvent trong log goc, run 1 suy ra tu dau thoi gian (dom_act 5003 ms, program elapsed 5103.697 ms) khop mau timeout 5 s".
- Muc 5: them trich dan nguyen van dong 581 cua worker log kem so dong, ghi ro moi run 2 den run 5 co chu do 1 lan o dong 90 trong JSON, va ghi ro o bang cua log gan nhan do cho run 1 la sai chu khi doi chieu run-1.json.
- Khong doi so nao, khong doi verdict. Suy luan run 1 cung ket o timeout 5 s van dung theo dau thoi gian, chi sua tu suy luan thanh suy luan chu khong viet nhu chu loi goc.

## 4. Sua chua 3: G1 cua council 3, trich dan HEAD loi thoi

Van de: bao cao muc 2 va muc 3 ghi HEAD 2ed0caf, trong khi luc council 3 va council 3 redo fetch thi nhanh da la d2da482.

Kiem chung lai: `git rev-parse origin/todolist-push` tra ve d2da4820cbc31adbad39c93670f30a01ff2c7709. `git ls-tree` cho thay ca 6 blob van giong het bao cao task 1, nen so lieu khong doi vi ly do nay.

Da sua trong bao cao muc 2 va muc 3 diem 1: ghi HEAD d2da482, kem chu thich luc kiem chung ban dau la 2ed0caf va ca 6 blob khong doi. Them ghi chu o dau bao cao ve ban sua sau review.

## 5. Sua chua 4: G2 cua council 3, so dan xuat thieu duong dan tinh lai

Van de: bao cao neu cac median phu ma khong ghi ten truong JSON va day gia tri, nguoi doc khong tinh lai duoc chi tu bao cao.

Kiem chung lai tu JSON goc bang statistics.median, moi run mot gia tri, theo thu tu run 1 den run 5. Tat ca khop voi bao cao cu:

- phase_split_ms.model: [0, 0, 0, 0, 0], median 0.
- phase_split_ms.ssh: [15623.9, 14931.0, 15011.0, 15648.1, 15498.0], median 15498.0.
- phase_split_ms.broker: [689.1, 807.8, 708.2, 633.7, 614.0], median 689.1.
- phase_split_ms.observe: [1500.5, 1612.5, 1487.9, 1053.4, 1347.2], median 1487.9.
- phase_split_ms.act: [5267.4, 5260.3, 5254.6, 5240.6, 5235.7], median 5254.6.
- phase_split_ms.verify: [10424.2, 11129.8, 10409.7, 10437.5, 10361.1], median 10424.2.
- phase_split_ms.setup: [148.3, 209.3, 188.1, 105.9, 108.6], median 148.3.
- phase_split_ms.residual: [2.3, 2.5, 2.5, 2.4, 2.3], median 2.4.
- mux_baseline_ms: [790.5, 777.8, 789.9, 836.1, 826.9], median 790.5.
- browsers.brave.wall_ms: [2621.9, 2731.6, 2703.2, 2698.9, 2592.5], median 2698.9.
- browsers.chromium.v12.ms: [11045.1, 11747.4, 11023.1, 11092.6, 11034.1], median 11045.1. Luu y: truong browsers.chromium.v12.elapsed_ms co day [10051, 10054, 10052, 10052, 10054], median 10052, nen phai dung truong ms moi ra 11045.1.

Da sua trong bao cao muc 4: them mot muc con liet ke day du ten truong, day gia tri va median cho tung so dan xuat o tren, kem luu y ve truong v12.elapsed_ms. Khong doi so nao, chi them duong dan tinh lai.

## 6. Sua chua 5: G6 giu nguyen nhan gia thuyet workspace 2, va ghi chu my thuat ve log goc

- G6: bao cao muc 6 da ghi ro gia thuyet Chromium nam tren workspace 2 trong khi workspace 1 dang hoat dong la "giai thich dan dau, chua duoc chung minh", log cung ghi ro nhu vay. Toi giu nguyen nhan nay, khong sua, khong dung gia thuyet nay nhu ket luan.
- Ghi chu my thuat tu redteam: worker log co 2 muc deu danh so 6. Kiem chung lai truc tiep: dong 575 la "## 6. Verdict" (muc that), dong 667 la "## 6. Verdict" thu hai, dong 669 chi ghi "- (to be filled)", trong. Bao cao cu khong nhac den. Da them mot diem vao muc 6 cua bao cao ghi ro 2 muc trung so nay va so dong, kem danh gia day la thieu sot trinh bay cua log goc, khong anh huong so nao va khong doi verdict.

## 7. Nhung gi toi khong doi, va vi sao

- Khong doi so nao: council 1 ket luan tat ca cac so deu khop, khong co so nao lech. Toi tinh lai doc lap cac so chinh va so phu o muc 2, 4, 5 tren day, tat ca khop. Redteam ket luan SURVIVES, 10 dot tan cong deu khong pha duoc bao cao.
- Khong doi verdict DO NOT EXPAND: ca 2 gap cua council 2 deu la loi dien dat, khong doi so nao va khong doi ket luan. Sau khi sua gap 1, ket luan con vung hon vi phan thuc cho thay nguong wall khong phai rang buoc quyet dinh.
- Khong sua G3, G4, G5 cua council 3 theo cach rieng: council 3 redo da giai quyet ca 3 bang trich dan nguyen van truc tiep tu file goc. Toi da dua trich dan nguyen van dong 581 vao muc 5 cua bao cao (phan cua G3), va trich dan verdict DO NOT EXPAND trong worker log dong 636-637 ma council 3 redo da doc (phan cua G5) khong can viet lai vi bao cao muc 5 da trich dung. Doan chan doan rieng /tmp/s2-diag2.mjs (phan cua G4) van khong co file trong repo de chay lai, bao cao muc 6 da ghi ro gioi han nay, khong them duoc gi.
- Khong them ghi chu ve khoang chenh spans khoang 1.6 s moi run ma redteam neu o A9: bao cao khong dua ra tuyen bo nao ve tong spans, day chi la quan sat, khong phai loi cua bao cao. Phase split cong lai khop wall trong sai so lam tron 0.2 ms, toi khong kiem tra lai tong spans vi no khong anh huong sua chua nao.
- Khong sua file worker log goc tren nhanh todolist-push: toi chi sua bao cao kiem chung, mo ta dung o bang cua log la sai chu cho run 1. Log goc thuoc ve worker, khong thuoc pham vi sua cua dot nay.
- Khong doi huong tiep theo trong bao cao: chung minh hoac loai bo gia thuyet visibility truoc, roi moi xet set_value hoac buoc 9. Huong nay giu nguyen nhu council 2, council 3 redo va redteam deu dong y.

## 8. Ket luan

- Da ap dung 5 sua chua: gap 1 (ly do median thap nguoc chieu, kem phan thuc), gap 2 (cau chu CDP timeout o run 1, kem trich dan dong 581), G1 (HEAD d2da482), G2 (ten truong va day gia tri cho cac median dan xuat), G6 cong ghi chu my thuat (gia thuyet workspace 2 giu nguyen nhan chua chung minh, log goc co 2 muc so 6 trung nhau).
- Moi so moi viet vao bao cao deu do toi tinh lai tu file goc tren todolist-push, khong lay so cua review ma khong kiem tra.
- Khong doi so nao da duoc xac nhan, khong doi verdict DO NOT EXPAND.
