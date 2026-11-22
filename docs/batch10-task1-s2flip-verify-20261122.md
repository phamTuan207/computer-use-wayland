# Batch 10 task 1: kiem chung doc lap verdict S2 flip (DO NOT EXPAND)

Ngay kiem chung: 22/11/2026, 11:04-11:15 +07.
Nguoi kiem chung: batch 10 task 1, doc lap, chi tu file goc.

Ban sua sau review, ngay 22/11/2026: ap dung cac sua chua tu council 2, council 3 redo va redteam task 1, moi sua chua deu kiem chung lai tu file goc truoc khi viet. Khong doi so nao da duoc xac nhan, khong doi verdict DO NOT EXPAND. Chi tiet tung sua chua xem docs/batch10-fix-task1-20261122.md.

## 1. Nhiem vu

Kiem chung doc lap verdict DO NOT EXPAND cho S2 flip, tu file JSON goc, khong tin so cua ai khac. Tinh lai: median wall time 5 run, Brave gui duoc may tren 5, Chromium gui duoc may tren 5, model call may lan, per-send pass rate va per-run pass rate. Ket luan DO NOT EXPAND dung hay sai, bang so cua minh.

## 2. Nguon da xac minh ton tai

- Nhanh: origin/todolist-push, HEAD d2da482 (luc kiem chung ban dau la 2ed0caf, nhanh da tien 1 commit sau do; ca 6 blob van giong het, file goc khong doi), sau `git fetch origin todolist-push`.
- Ca 6 file deu co tren nhanh, kiem tra bang `git ls-tree -r origin/todolist-push`:
  - improvements/s2-flip-runs/run-1.json, blob 48cccec7df4388c27bf154f4d40f44c48620e6cd
  - improvements/s2-flip-runs/run-2.json, blob 241e7d9fe126328a68de71d710bb30e316928c37
  - improvements/s2-flip-runs/run-3.json, blob 1602376c1cb5858556dbd9bce9ff3ad27786e5d0
  - improvements/s2-flip-runs/run-4.json, blob 31150c122325dffa956a7114aa212a14d964c7ce
  - improvements/s2-flip-runs/run-5.json, blob 7f46be5cdba44de7bb53fbdcbefee0c64431ef59
  - improvements/worker-click4-s2-flip-log.md, blob f240600b3ce20d8b62fa2a51d28c4ef2a5d8decf
- Khong co file nao khac voi mo ta trong brief. Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. File test-w.txt (0 byte, untracked) de nguyen, khong dong den.

## 3. Lenh da chay va bang chung

1. `git fetch origin todolist-push`, ket qua: todolist-push ve d2da482 (luc kiem chung ban dau la 2ed0caf, xem muc 2).
2. `git ls-tree -r origin/todolist-push -- improvements/s2-flip-runs/ improvements/worker-click4-s2-flip-log.md`, ket qua: 6 file nhu muc 2.
3. `git show origin/todolist-push:<duong dan>` cho ca 6 file, trich ra /tmp/s2flip-verify/ (chi doc, khong sua nhanh).
4. Python3 doc 5 file JSON va tinh lai. Output day du cua script:
   - wall_ms per run: [33655.6, 33953.2, 33061.9, 33121.8, 33166.9]
   - sorted wall_ms: [33061.9, 33121.8, 33166.9, 33655.6, 33953.2]
   - median wall_ms: 33166.9 ms = 33.17 s
   - mean wall_ms: 33391.9, min 33061.9, max 33953.2
   - brave sent: 5 / 5, chromium sent: 0 / 5
   - total model_calls: 0
   - per-send pass rate brave: 100.0 %, chromium: 0.0 %, overall: 50.0 %
   - per-run full pass (both sends): 0 / 5 = 0.0 %, per-run any pass: 5 / 5
   - brave outcome: ['sent', 'sent', 'sent', 'sent', 'sent']
   - chromium outcome: ['failed-unverified', 'failed-unverified', 'failed-unverified', 'failed-unverified', 'failed-unverified']
   - brave program ok: [True x 5], chromium program ok: [False x 5]
   - brave cb1 verified: [True x 5], chromium cb1 verified: [False x 5]
   - brave v12 found: [True x 5], chromium v12 found: [False x 5]
   - p9 brave ok: [True x 5], p9 chromium ok: [True x 5]
   - dry_run flags: [False x 5]
   - brave act elapsed_ms (laptop): [163.718, 153.967, 150.12, 134.809, 133.025]
   - chromium act elapsed_ms (laptop): [5103.697, 5106.312, 5104.459, 5105.836, 5102.649]
   - chromium errors: ['assert failed: dom_act failed' x 5]
   - chromium v12 attempts: [40 x 5], brave v12 attempts: [1 x 5]
   - phase_split model per run: [0 x 5]
5. Script kiem tra phu, output:
   - routing source: dom-chromium ca 10 quyet dinh trinh duyet, fell_through rong ca 10
   - phase split median: ssh 15498.0, broker 689.1, observe 1487.9, act 5254.6, verify 10424.2, setup 148.3, residual 2.4
   - mux baseline median: 790.5 ms
   - brave per-browser wall median: 2698.9 ms
   - brave program elapsed median: 150.12 ms
   - chromium program elapsed median: 5104.459 ms
   - chromium v12 ms median: 11045.1 ms
   - brave dom_act ms: [72, 51, 53, 48, 41], min 41, max 72
   - chromium dom_act ms: [5003, 5002, 5003, 5003, 5003], min 5002, max 5003
   - run 1 chromium log co chu "CDP timeout": False. Run 2 den run 5: True.

## 4. So lieu tinh lai tu JSON goc

Bang tung run (wall_ms la wall end to end, gom ca transport):

| run | wall_ms | Brave outcome | Chromium outcome | model_calls |
|-----|---------|---------------|------------------|-------------|
| 1 | 33655.6 | sent | failed-unverified | 0 |
| 2 | 33953.2 | sent | failed-unverified | 0 |
| 3 | 33061.9 | sent | failed-unverified | 0 |
| 4 | 33121.8 | sent | failed-unverified | 0 |
| 5 | 33166.9 | sent | failed-unverified | 0 |

So tong hop, tu tinh:

- Median wall time 5 run: 33166.9 ms = 33.17 s, lam tron 33.2 s. Day sap xep: 33061.9, 33121.8, 33166.9, 33655.6, 33953.2.
- Brave gui duoc: 5 tren 5.
- Chromium gui duoc: 0 tren 5.
- Model call: 0 lan tong cong. 0 lan moi run, 0 lan moi trinh duyet, phase_split_ms.model bang 0 ca 5 run.
- Per-send pass rate: Brave 5/5 = 100%, Chromium 0/5 = 0%, tong 5/10 = 50%.
- Per-run pass rate (ca 2 send deu verified): 0/5 = 0%. Per-run (it nhat 1 send verified): 5/5.
- Bang chung phu, tu tinh: Brave program elapsed median 150.12 ms, dom_act 41-72 ms, V12 found attempt 1 ca 5 run, CB-1 verified true ca 5 run. Chromium program elapsed median 5104.459 ms, dom_act 5002-5003 ms, V12 40 attempts khong tim thay, median 11045.1 ms, CB-1 verified false ca 5 run. P9 ok true 10/10 trong JSON. Routing dom-chromium 10/10, khong co lan nao roi xuong screenshot. Ca 5 run deu khong phai dry run.
- So dan xuat, kem ten truong va day gia tri de tinh lai chi tu bao cao nay (moi run mot gia tri, theo thu tu run 1 den run 5):
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

## 5. Doi chieu voi verdict hien co

Verdict hien co, trong muc 6 cua worker log va trong coord: DO NOT EXPAND. Cac so di kem: Brave 5/5 SENT, Chromium 0/5 FAILED-UNVERIFIED, CDP timeout Input.dispatchMouseEvent 5000 ms, 0 model call, median wall 33166.9 ms (33.2 s), per-send 50%, per-run 0/5.

Ket qua doi chieu, tung so:

- Median wall 33166.9 ms: KHOP.
- Day wall sap xep: KHOP.
- Brave 5/5: KHOP.
- Chromium 0/5: KHOP.
- Model call 0: KHOP.
- Per-send 50%: KHOP.
- Per-run 0/5: KHOP.
- Brave program elapsed median 150.1 ms, dom_act 41-72 ms: KHOP.
- Chromium program elapsed median 5104.5 ms: KHOP.
- Chromium V12 median 11045.1 ms, 40 attempts: KHOP.
- Mux baseline median 790.5 ms: KHOP.
- Phase split median (ssh khoang 15000, broker khoang 700, observe khoang 1500, act khoang 5250, verify khoang 10400, setup khoang 150, residual 2.3-2.5): KHOP.
- Brave per-browser wall median 2698.9 ms: KHOP.

Khong co con so nao lech. Khong co so nao can sua trong verdict hien co.

Mot luu y ve cau chu, khong phai lech so: bang 5 run trong log, dong 581, ghi nguyen van o run 1 Chromium la "5103.7ms, completed 0, CDP timeout Input.dispatchMouseEvent", nhung dong log goc trong run-1.json chi la "dom_act ok False completed 0 ms 5003", khong co chu "CDP timeout". Chu nay chi xuat hien trong log cua run 2 den run 5 (moi run 1 lan, dong 90 trong JSON). Suy luan run 1 cung ket o timeout 5 s chi dua tren dau thoi gian: dom_act 5003 ms, program elapsed 5103.697 ms, cung loi "assert failed: dom_act failed" nhu 4 run kia. O bang cua log gan nhan CDP timeout cho run 1 la sai chu, doi chieu voi run-1.json. Day chi la cau chu chua chinh xac o mot o trong bang, khong doi so nao va khong doi verdict.

## 6. Gioi han cua lan kiem chung nay

- File anh P9 ma JSON tro toi (improvements/s2-flip-runs/p9-run1-brave.png den p9-run5-chromium.png) khong co tren nhanh todolist-push. Trong thu muc improvements/s2-flip-runs/ tren nhanh chi co 5 file JSON. Toi khong mo lai duoc anh P9 de doi chieu bang mat. Truong p9.ok true 10/10 trong JSON van dung, va ket qua gui duoc xac nhan doc lap boi CB-1 va V12 trong JSON, nen gioi han nay khong doi verdict.
- Doan chan doan chay rieng (/tmp/s2-diag2.mjs: Runtime.evaluate 1-3 ms, Input.dispatchMouseEvent timeout 5000 ms) chi co trong log, file script khong co trong repo, toi khong chay lai duoc. Toi chi xac nhan JSON phu hop voi no: Chromium program elapsed khoang 5104 ms ca 5 run, Brave program 133-164 ms.
- Gia thuyet Chromium nam tren workspace 2 trong khi workspace 1 dang hoat dong la giai thich dan dau, chua duoc chung minh. Log cung ghi ro nhu vay, va khong doi workspace giua chung de giu nguyen dieu kien do.
- Log goc co 2 muc deu danh so 6: muc 6 thu nhat o dong 575 la muc Verdict that, muc 6 thu hai o dong 667 chi ghi "- (to be filled)", trong. Day la thieu sot trinh bay cua log goc, khong anh huong so nao va khong doi verdict.

## 7. Ket luan: DO NOT EXPAND DUNG

- DO NOT EXPAND la dung, voi so cua chinh toi.
- Ly do: lop (class) dinh nghia can ca 2 send deu verified trong mot run. 0/5 run dat, per-send chi 50%. Nut that la co che, khong phai model: 0 model call, Brave gui trong 41-72 ms, Chromium ket o Input domain o ca 5 run, 4 run co chu loi CDP timeout Input.dispatchMouseEvent trong log goc, run 1 suy ra tu dau thoi gian (dom_act 5003 ms, program elapsed 5103.697 ms) khop mau timeout 5 s.
- Ve nguong plateau 60 s: median 33.2 s nam duoi nguong, nen theo chu cua gate thi plateau CHUA dat. Nhung median thap nay khong phai la pass: lop khong hoan thanh (0/5 run dat), nen median khong co nghia tren run hoan thanh. That bai khong lam run ngan lai ma lam run dai them: duong that bai cua Chromium (span act-chromium cong verify-chromium) dai 17704.5-18478.3 ms moi run, duong thanh cong cua Brave (span act-brave cong verify-brave) chi 2591.8-2730.9 ms. Phan thuc: neu Chromium thanh cong nhu Brave (thay 2 span cua Chromium bang 2 span cua Brave, giu nguyen cac span khac), wall moi run se la 17859.5, 18205.8, 18059.9, 18061.1, 18005.3 ms, median 18059.9 ms (18.1 s). That bai lam moi run dai them 15002.0-15796.1 ms. Du thanh cong thi median cung chi khoang 18.1 s, van duoi 60 s, nen nguong wall khong phai rang buoc quyet dinh o day; rang buoc quyet dinh la ti le dat cua lop (0/5). Lop khong hoan thanh thi khong the mo rong. Mo rong luc nay la truyen mot nua hong sang cac lop khac.
- Khong co so nao lech so voi verdict hien co, nen khong can sua verdict. Huong tiep theo giu nguyen nhu log da ghi: chung minh hoac loai bo gia thuyet visibility truoc, roi moi xet set_value hoac buoc 9.
