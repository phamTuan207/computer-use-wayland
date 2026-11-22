# Batch 10 council 1: kiem so doc lap task 1 (S2 flip)

Ngay kiem: 22/11/2026, 11:12-11:20 +07.
Nguoi kiem: batch 10 council 1, chi kiem so, khong sua coord, khong commit, khong push.
Ket luan chung: TAT CA CAC SO DEU KHOP. Khong co so nao lech.

## 1. Nguon da xac minh ton tai

- Nhanh: origin/todolist-push, HEAD luc kiem la d2da482 (bao cao task 1 ghi 2ed0caf, nhanh da tien 1 commit sau do, nhung blob hash cua ca 6 file van giong het, file goc khong doi).
- Lenh: `git fetch origin todolist-push`, ket qua: todolist-push ve d2da482.
- Lenh: `git ls-tree origin/todolist-push -- improvements/s2-flip-runs/ improvements/worker-click4-s2-flip-log.md`, ket qua 6 file, blob hash giong het muc 2 cua bao cao task 1:
  - run-1.json 48cccec7df4388c27bf154f4d40f44c48620e6cd
  - run-2.json 241e7d9fe126328a68de71d710bb30e316928c37
  - run-3.json 1602376c1cb5858556dbd9bce9ff3ad27786e5d0
  - run-4.json 31150c122325dffa956a7114aa212a14d964c7ce
  - run-5.json 7f46be5cdba44de7bb53fbdcbefee0c64431ef59
  - worker-click4-s2-flip-log.md f240600b3ce20d8b62fa2a51d28c4ef2a5d8decf
- Trich file goc bang `git show origin/todolist-push:<duong dan>` ra /tmp/s2flip-council1/, chi doc, khong sua nhanh. File test-w.txt (0 byte, untracked) de nguyen, khong dong den.

## 2. Lenh tinh lai va output day du

Script Python doc 5 file JSON va tinh lai, chay tu /tmp/s2flip-council1/recompute.py. Output:

- wall_ms per run: [33655.6, 33953.2, 33061.9, 33121.8, 33166.9]
- sorted wall_ms: [33061.9, 33121.8, 33166.9, 33655.6, 33953.2]
- median wall_ms: 33166.9 = 33.17 s
- mean wall_ms: 33391.9, min 33061.9, max 33953.2
- brave outcome: ['sent', 'sent', 'sent', 'sent', 'sent']
- chromium outcome: ['failed-unverified', 'failed-unverified', 'failed-unverified', 'failed-unverified', 'failed-unverified']
- brave sent: 5 / 5, chromium sent: 0 / 5
- model_calls total: 0, per run: [0, 0, 0, 0, 0]
- model_calls per browser: brave [0, 0, 0, 0, 0], chromium [0, 0, 0, 0, 0]
- phase_split model per run: [0, 0, 0, 0, 0]
- per-send brave: 100.0 %, chromium: 0.0 %, overall: 50.0 %
- per-run full pass (both sent): 0 / 5 = 0.0 %
- per-run any pass: 5 / 5
- brave program ok: [True x 5], chromium program ok: [False x 5]
- brave cb1 verified: [True x 5], chromium cb1 verified: [False x 5]
- brave v12 found: [True x 5], chromium v12 found: [False x 5]
- brave v12 attempts: [1 x 5], chromium v12 attempts: [40 x 5]
- chromium v12 ms: [11045.1, 11747.4, 11023.1, 11092.6, 11034.1], median: 11045.1
- brave v12 ms: [960.1, 938.1, 966.3, 1017.1, 980.8]
- p9 brave ok: [True x 5], p9 chromium ok: [True x 5]
- dry_run flags: [False x 5]
- brave program elapsed_ms: [163.718, 153.967, 150.12, 134.809, 133.025], median: 150.12
- chromium program elapsed_ms: [5103.697, 5106.312, 5104.459, 5105.836, 5102.649], median: 5104.459
- brave dom_act ms: [72, 51, 53, 48, 41], min: 41, max: 72
- chromium dom_act ms: [5003, 5002, 5003, 5003, 5003], min: 5002, max: 5003
- chromium errors: ['assert failed: dom_act failed' x 5]
- mux baseline: [790.5, 777.8, 789.9, 836.1, 826.9], median: 790.5
- brave per-browser wall_ms: [2621.9, 2731.6, 2703.2, 2698.9, 2592.5], median: 2698.9
- chromium per-browser wall_ms: [18417.5, 18478.5, 17704.8, 17759.2, 17753.6], median: 17759.2
- phase_split ssh: [15623.9, 14931.0, 15011.0, 15648.1, 15498.0], median: 15498.0
- phase_split broker: [689.1, 807.8, 708.2, 633.7, 614.0], median: 689.1
- phase_split observe: [1500.5, 1612.5, 1487.9, 1053.4, 1347.2], median: 1487.9
- phase_split act: [5267.4, 5260.3, 5254.6, 5240.6, 5235.7], median: 5254.6
- phase_split verify: [10424.2, 11129.8, 10409.7, 10437.5, 10361.1], median: 10424.2
- phase_split setup: [148.3, 209.3, 188.1, 105.9, 108.6], median: 148.3
- phase_split residual: [2.3, 2.5, 2.5, 2.4, 2.3], median: 2.4
- routing brave source: ['dom-chromium' x 5], fell_through: [[] x 5]
- routing chromium source: ['dom-chromium' x 5], fell_through: [[] x 5]
- Chu "CDP timeout" trong JSON goc: run 1 False, run 2 True, run 3 True, run 4 True, run 5 True. Chu "Input.dispatchMouseEvent" trong JSON goc: run 1 False, run 2 den run 5 True.

## 3. Doi chieu tung so voi bao cao task 1

- Median wall time 33166.9 ms (33.17 s, lam tron 33.2 s): CONFIRMED.
- Day wall sap xep [33061.9, 33121.8, 33166.9, 33655.6, 33953.2]: CONFIRMED.
- Wall tung run [33655.6, 33953.2, 33061.9, 33121.8, 33166.9]: CONFIRMED.
- Mean wall 33391.9, min 33061.9, max 33953.2: CONFIRMED.
- Brave gui duoc 5 tren 5: CONFIRMED.
- Chromium gui duoc 0 tren 5: CONFIRMED.
- Model call 0 lan tong cong, 0 lan moi run, 0 lan moi trinh duyet, phase_split model 0 ca 5 run: CONFIRMED.
- Per-send pass rate: Brave 100%, Chromium 0%, tong 5/10 = 50%: CONFIRMED.
- Per-run pass rate (ca 2 send deu verified): 0/5 = 0%: CONFIRMED.
- Per-run (it nhat 1 send verified): 5/5: CONFIRMED.
- Brave program elapsed median 150.12 ms (bao cao ghi 150.1 ms, lam tron): CONFIRMED.
- Chromium program elapsed median 5104.459 ms (bao cao ghi 5104.5 ms, lam tron): CONFIRMED.
- Brave dom_act 41-72 ms, cu the [72, 51, 53, 48, 41]: CONFIRMED.
- Chromium dom_act 5002-5003 ms, cu the [5003, 5002, 5003, 5003, 5003]: CONFIRMED.
- Chromium V12 40 attempts ca 5 run, khong tim thay: CONFIRMED.
- Brave V12 1 attempt ca 5 run, tim thay: CONFIRMED.
- Chromium V12 ms median 11045.1 ms: CONFIRMED.
- Brave per-browser wall median 2698.9 ms: CONFIRMED.
- Mux baseline median 790.5 ms: CONFIRMED.
- Phase split median: ssh 15498.0, broker 689.1, observe 1487.9, act 5254.6, verify 10424.2, setup 148.3, residual 2.4: CONFIRMED (bao cao ghi khoang 15000, 700, 1500, 5250, 10400, 150, 2.3-2.5, deu khop).
- Routing dom-chromium 10/10, fell_through rong 10/10: CONFIRMED.
- P9 ok true 10/10 trong JSON (Brave 5, Chromium 5): CONFIRMED.
- CB-1 verified: Brave true 5/5, Chromium false 5/5: CONFIRMED.
- Program ok: Brave true 5/5, Chromium false 5/5: CONFIRMED.
- Chromium error 'assert failed: dom_act failed' ca 5 run: CONFIRMED.
- Dry run false ca 5 run: CONFIRMED.
- Blob hash ca 6 file goc: CONFIRMED, giong het muc 2 cua bao cao.

## 4. Luu y da kiem lai, khong phai lech so

- Bao cao task 1 ghi bang 5 run trong worker log o run 1 Chromium la "CDP timeout Input.dispatchMouseEvent", nhung dong log goc trong run-1.json chi la "dom_act ok False completed 0 ms 5003", khong co chu "CDP timeout". Toi kiem lai doc lap: run-1.json khong chua chu "CDP timeout" hay "Input.dispatchMouseEvent", run 2 den run 5 co ca hai chu. Dong 581 cua worker log dung la ghi chu do o hang run 1. Day chi la cau chu chua chinh xac o mot o trong bang cua worker log, khong doi so nao va khong doi verdict. Bao cao task 1 da ghi luu y nay, toi xac nhan luu y nay la dung.
- Anh P9 ma JSON tro toi (p9-run1-brave.png den p9-run5-chromium.png) khong co tren nhanh todolist-push. Lenh `git ls-tree -r origin/todolist-push -- improvements/s2-flip-runs/` tra ve 0 file png. Toi cung khong mo lai duoc anh P9. Gioi han nay bao cao task 1 da ghi, toi xac nhan la dung. Truong p9.ok true 10/10 trong JSON van dung, va ket qua gui duoc xac nhan doc lap boi CB-1 va V12 trong JSON, nen gioi han nay khong doi verdict.
- Nhanh da tien tu 2ed0caf (luc bao cao task 1 viet) len d2da482 (luc toi kiem), nhung blob hash cua ca 6 file goc khong doi, nen so lieu khong bi anh huong.

## 5. Verdict cua council 1

- Tat ca cac so trong bao cao task 1 deu CONFIRMED, khong co so nao lech, khong co so nao can sua.
- Verdict DO NOT EXPAND dung tren so lieu goc: per-send 50%, per-run day du 0/5, 0 model call, Chromium ket o Input domain ca 5 run voi timeout 5000 ms.
- Khong co y kien khac ve so lieu.
