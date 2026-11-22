# Council 3, batch 10 task 3: kiem tra claim (c) DOM-grounding DONE

Ngay kiem tra: 22/11/2026, bat dau 11:17 +07.
Nguoi kiem tra: council 3, batch 10 task 3.
Pham vi: chi claim (c) trong docs/batch10-task3-cb8-audit-20261122.md, muc 4.
Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push.
Khong thong tin ca nhan. Khong dau gach ngang dai. Khong ydotool.

## 0. Neo kiem tra

- Audit neo o origin/main 81ea6e009ec0111edb3f1561a85a45529a329180 va origin/todolist-push 2ed0caf1509ff9b6cb54da12b43f8ce7085e05b6.
- Council fetch read-only, tip hien tai: origin/main c525c591a7089532b2147555a2fa3d2ce7eca74b, origin/todolist-push d2da4820cbc31adbad39c93670f30a01ff2c7709.
- Ca hai neo audit deu la ancestor cua tip hien tai (git merge-base --is-ancestor, ca hai deu pass).
- Khong co commit moi nao ve grounding tu neo audit den tip tren ca hai nhanh (git log neo..tip -- docs/clone2-dom-grounding-20261122.md tests/dom_grounding_bench.py tests/dom_grounding_fixture.html docs/clone2-dom-bench-2win-20261122.md, output rong; tuong tu tren todolist-push). Bang chung khong doi tu luc audit.
- File audit hien la untracked trong working tree (git status --short). Council kiem tra lai tu git object, khong tin ban working tree.

## 1. Verdict

REVOKED STANDS.

Ly do mot dong: so fixture la so do that va phan E2 live dem lai dung, nhung log tho khong co trong repo, bench khong co tren todolist-push, va chinh bao cao ghi real Zen, live pages, headed runs la UNVERIFIED, nen theo luat CB-8 thi DONE lam gate bi thu hoi cho den khi co bang chung live.

## 2. Từng fact da kiem tra

### 2.1 Ban ghi cua claim co trong repo, dung

- Settled base trong improvements/worker-click3-final-direction-log.md, dong 147-148 tren todolist-push: "DOM grounding is single-source (clone2 batch 7: 66 rects, Marionette median 0.030s; C1 applies)". Kiem bang git show origin/todolist-push:improvements/worker-click3-final-direction-log.md, grep thay dung dong 147-148.
- Todolist docs/zen-error-fix-todolist-20261121.md, dong 47 tren todolist-push: 1.2.2 DONE, "DOM read 3-14ms vs observe vai giay; DOM locate chinh xac tuyet doi (vision 58.6%); DOM click KHONG bang chuot that". Dong 60: 2.1.2 DONE 21/11 05:30 (E2 live), "DOM rects chinh xac tuyet doi, vision 58.6% (17/29), pointer <1px". Kiem bang git show origin/todolist-push:docs/zen-error-fix-todolist-20261121.md, grep -n, ca hai dong khop so audit neu.
- Luu y: dong 47 tu thua nhan DOM click khong bang chuot that. DONE nay khong bao phu duong input that.

### 2.2 So fixture la so do that, dung

- docs/clone2-dom-grounding-20261122.md: 401 dong tren origin/main, ca o neo audit 81ea6e0 va o tip c525c59 (git show ... | wc -l, ca hai deu 401).
- tests/dom_grounding_bench.py tren origin/main, commit 79b75e7 (2026-11-21 19:34:58 UTC, "tests: DOM grounding bench, one-shot rects plus pointer clicks on fixture") va 47d5ee6 (2026-11-21 19:49:45 UTC, a11y snapshot steps). 47d5ee6 la ancestor cua neo audit 81ea6e0. Kiem bang git log origin/main -- tests/dom_grounding_bench.py va git log -1 --format.
- tests/dom_grounding_fixture.html cung commit 79b75e7. Dung nhu audit neu.
- So lieu trong bao cao, kiem bang git show origin/main:docs/clone2-dom-grounding-20261122.md, grep -n:
  - Dong 22-23: 66 rects, Marionette pooled median 0.030 s, 9 samples qua 3 runs; BiDi 0.006 den 0.054 s per run median.
  - Dong 127: bang so, one-shot 66 rects 0.030 s pooled median, range 0.0085 den 0.096, run medians 0.013, 0.071, 0.030; BiDi pooled median 0.016 s.
  - Dong 25-26 va 138: agreement BiDi vs Marionette toi da 5.7e-14 px.
  - Dong 77, 79, 90-91: run 2 va run 3 full, run_total 14.35 s va 12.74 s; run 4 va run 5 fix-pass, 16.15 s va 15.57 s.
  - Dong 131: 5 pointer clicks, all 5 landed, 3 runs cua click step (two full, one partial).
  - Dong 133: verify bang 1 lan doc DOM 0.002 den 0.015 s.
  - Dong 60-62: Firefox 160.0.1 headless tren VM, la Zen stand-in, real Zen numbers need the laptop run.
- Ket luan muc 2.2: 66 rects va median 0.030 s la so co trong bao cao da commit tren main, khong phai so bia. Audit noi dung.

### 2.3 Corroboration doc lap 2-window, dung, co mot thieu sot nho trong tom tat audit

- docs/clone2-dom-bench-2win-20261122.md: 371 dong tren origin/main (git show ... | wc -l).
- Dong 150: one-shot harvest 66 elements per window, 12 samples, pooled median 0.0112 s, range 0.0062 den 0.1685. Dung nhu audit neu.
- Dong 155: 5 pointer clicks per window, 4 gia tri, median 1.3814 s. Dong 186-192: all five landed true o ca hai window, ca hai run sau fix.
- Dong 172: harvest rects exactly, max delta 0.0 px in all 4 window-runs. Dung.
- Thieu sot nho: audit tom tat "5/5 clicks ca 2 windows ca 2 runs" ma khong neu lan chay loi stale-rect duoc tiet lo trong chinh bao cao nay: dong 36-39, run 1 chi 2 of 5 clicks landed, all_five_landed false, mechanism UNKNOWN; dong 49 va 93 ghi fix dung sau do. Tom tat audit khong sai ve ket qua cuoi, nhung bo qua mot failure duoc tiet lo. Khong doi verdict.
- Han che nhu audit neu: log cua bench 2-window cung chi o /tmp. Bao cao trich /tmp/dom_2win_run1.log, /tmp/dom_2win_run2.log, /tmp/dom_2win_run1_stale_rect.log, /tmp/dom_2win_council1.log (dong 37, 83, 87, 97, 245). git grep dom_2win_run tren origin/main chi thay docs/clone2-dom-bench-2win-20261122.md va tests/dom_bench_2win.py (ten file trong code), khong co file log tho nao trong repo. Corroboration khong tinh lai duoc tu repo. Audit noi dung.

### 2.4 Phan E2 live trong repo, dem lai dung

- docs/calibration-e2-report.md va tests/calibration-e2-hits.jsonl co tren origin/todolist-push (git ls-tree -r --name-only origin/todolist-push).
- File hits: 87 dong. Dem bang python3, json.loads tung dong:
  - case_id e2-vision: n = 29, hit = 17, miss = 12, 17/29 = 58.6%.
  - case_id e2-actual: n = 58, hit = 34, miss = 24, 34/58 = 58.6% (trung ti le, hai tap khac nhau).
- Bao cao E2, dong 31 va 53: "Overall predicted hit rate: 17/29 = 58.6%" va "End-to-end first-try hit rate: 17/29 = 58.6%". Dong 114: "2.1.2 DOM vs screenshot: DONE (live). DOM rects exact; vision 58.6%".
- Bao cao E2, dong 4-5: chay 2026-11-21 04:36-05:30 +07 tren man hinh laptop that (Zen, Hyprland). Dong 11-12: Zen window [2509, 914], size [1863, 1176].
- Ket luan muc 2.4: phan E2 live dem lai dung 17/29 = 58.6%, va la bang chung live that cho DOM rects exact va vision 58.6%. Audit noi dung. Nhung E2 khong do median 0.030 s tren Zen that, nen no khong cuu duoc phan fixture timing cua claim.

### 2.5 Bang chung thieu, audit noi dung

- Bench va fixture KHONG co tren todolist-push, ca o neo audit 2ed0caf va o tip d2da482. Kiem bang git cat-file -e origin/todolist-push:tests/dom_grounding_bench.py, tests/dom_grounding_fixture.html, tests/dom_bench_2win.py, ca ba deu NO o ca hai diem. Nhanh direction khong chua cong cu chung minh claim cua chinh no. Audit noi dung.
- Raw JSONL logs (/tmp/dom_grounding_run1-5.log) chi o VM clone2, khong co trong repo. git grep dom_grounding_run tren origin/main chi thay docs/clone2-dom-grounding-20261122.md (tu no trich duong dan /tmp); tren origin/todolist-push khong thay gi. Khong co file log tho nao trong repo. Audit noi dung.
- Median 0.030 s khong tinh lai duoc tu repo: bao cao chi cho range 0.0085 den 0.096 va 3 run medians 0.013, 0.071, 0.030 (dong 127), khong liet ke 9 sample rieng le. Pooled median phu thuoc vao 9 sample khong co trong repo. Day la cung chuan nhu V4, V7, V8 cua batch 7 ma audit trich.
- Chinh bao cao, section 9 "UNVERIFIED on this machine", dong 383-401:
  - Real Zen: every number here is Firefox 160.0.1 as a stand-in, inference not measurement.
  - Headed runs under Xvfb and real web pages: fixture is local and static, not exercised on a live site here.
  - AT-SPI live, BiDi accessibility module: not measured here.
- Section 8, dong 351-380, khuyen nghi chay lai tren laptop doi voi real Zen 1.24.3b va thay median stand-in bang median Zen. Audit viet "muc 8 va 9 ghi UNVERIFIED", chinh xac hon la UNVERIFIED o muc 9, muc 8 la khuyen nghi chay lai. Chat luong bang chung khong doi, chi la chinh ta trich dan.
- Ket luan muc 2.5: claim lam gate cho live Zen va Messenger vuot qua pham vi bang chung ma bao cao tu thua nhan. Audit noi dung.

### 2.6 Council va redteam da review, dung ve co ban, co ghi chu ve trich dan

- coord/clone2.md, khoi "Bao cao clone2: Batch 7 HOAN THANH, 22/11", ghi task 2 qua council 3 nguoi va redteam doc lap, commit bench 79b75e7 va 47d5ee6, bao cao 402 dong (so dong nay la truoc khi sua, ban tren main hien la 401 dong).
- Bao cao grounding tu ghi phan sua: dong 10-13 (BiDi session.new cost, run accounting, a11y numbers corrected from preserved logs), dong 79 (first version wrongly called run totals), dong 92-93 (run 5 voi bench da sua, a11y step, warm session.new probe).
- Ghi chu: audit trich "coord/clone2.md:687". Dong 687 trong file tren main la dong "Luat nhu cu..." ngay truoc tieu de batch 7, khong phai dong ghi council review. Noi dung review co that trong khoi bao cao ngay sau do, chi so dong trich khong chinh xac. Khong co file council hay redteam rieng cho task 2 tren main (git ls-tree docs/ | grep -i dom chi thay 2 bao cao grounding va 2 file comparison). Chung cu review chi la loi tu bao cao trong coord/clone2.md. Day la ghi chu ve do manh chung cu, khong doi verdict.

## 3. Luat CB-8 ap dung co dung khong

- Luat CB-8, improvements/worker-click3-final-direction-log.md:251 tren todolist-push, kiem bang git show va grep -n, dong 251 khop chinh xac. Audit trich duong dan thieu tien to improvements/, nhung so dong dung.
- Noi dung luat: "Its teeth: any proposal whose DONE basis is a fixture-only proof gets its DONE revoked until live evidence exists." Scope: "apply it only to the DONE items that gate this final direction (S2's Pick 1 DONE, the bench DONE, the DOM-grounding DONE claims)".
- Ap dung vao claim (c):
  - Claim (c) nam trong scope luat mot cach tuong minh (DOM-grounding DONE claims).
  - Claim (c) lam gate cho huong di: settled base dong 147-148 dung no lam co so ("DOM grounding is single-source ... C1 applies").
  - Co so cua DONE la fixture-only ve timing: Firefox 160.0.1 headless, fixture tinh local, 66 rects, median 0.030 s. Phan live duy nhat trong repo (E2) chi chung minh DOM rects exact va vision 58.6%, khong chung minh timing tren Zen that.
  - Bao cao tu ghi UNVERIFIED cho real Zen, live pages, headed runs.
- Vay luat CB-8 ap dung dung, va ket qua cua luat la REVOKED cho den khi co bang chung live. Audit ap dung dung.

## 4. Co gi audit noi sai hoac thieu

- Trich dan duong dan luat thieu tien to improvements/ (muc 3). So dong 251 dung. Khong anh huong verdict.
- Trich dan coord/clone2.md:687 lech vai dong so voi khoi bao cao that (muc 2.6). Noi dung review co that. Khong anh huong verdict.
- Tom tat 2-window bo qua failure stale-rect duoc tiet lo (muc 2.3). Ket qua cuoi dung. Khong anh huong verdict.
- "Muc 8 va 9 ghi UNVERIFIED": UNVERIFIED o muc 9, muc 8 la khuyen nghi (muc 2.5). Khong anh huong verdict.
- Khong co fact nao trong muc 4 cua audit bi bac bo. Khong co bang chung live moi nao xuat hien tu neo audit den tip hien tai.

## 5. De khoi phuc (theo audit, council dong y)

1. Commit raw logs grounding (run1-5) hoac chay lai bench voi log commit trong repo, dua bench va fixture len todolist-push.
2. Chay bench tren Zen that va live page, thay median stand-in bang median Zen that.
3. Ghi lai pham vi claim theo dung nhung gi da do, tach phan E2 live (da dung) khoi phan fixture timing (chua du chuan gate).
4. Cho den luc do, khong dung claim (c) lam gate DONE cho huong live.

## 6. Lenh da chay (tai hien)

- git fetch origin main todolist-push; git rev-parse origin/main origin/todolist-push; git log --oneline -3 origin/main; git log --oneline -3 origin/todolist-push; git status --short.
- git ls-tree -r --name-only origin/main -- docs/clone2-dom-grounding-20261122.md docs/clone2-dom-bench-2win-20261122.md tests/dom_grounding_bench.py tests/dom_grounding_fixture.html docs/zen-error-fix-todolist-20261121.md.
- git ls-tree -r --name-only origin/todolist-push -- tests/dom_grounding_bench.py tests/dom_grounding_fixture.html tests/dom_bench_2win.py docs/calibration-e2-report.md tests/calibration-e2-hits.jsonl worker-click3-final-direction-log.md.
- git cat-file -t 81ea6e009ec0111edb3f1561a85a45529a329180 2ed0caf1509ff9b6cb54da12b43f8ce7085e05b6 79b75e7 47d5ee6 (tung hash rieng).
- git cat-file -e origin/todolist-push:tests/dom_grounding_bench.py (NO), :tests/dom_grounding_fixture.html (NO), :tests/dom_bench_2win.py (NO), ca o tip va o neo 2ed0caf.
- git merge-base --is-ancestor 81ea6e009ec0111edb3f1561a85a45529a329180 origin/main (pass); 2ed0caf1509ff9b6cb54da12b43f8ce7085e05b6 origin/todolist-push (pass); 47d5ee6 81ea6e009ec0111edb3f1561a85a45529a329180 (pass).
- git log 81ea6e009ec0111edb3f1561a85a45529a329180..origin/main -- docs/clone2-dom-grounding-20261122.md tests/dom_grounding_bench.py tests/dom_grounding_fixture.html docs/clone2-dom-bench-2win-20261122.md (rong).
- git log 2ed0caf1509ff9b6cb54da12b43f8ce7085e05b6..origin/todolist-push -- tests/dom_grounding_bench.py tests/dom_grounding_fixture.html tests/dom_bench_2win.py docs/calibration-e2-report.md (rong).
- git show origin/main:docs/clone2-dom-grounding-20261122.md | wc -l (401); | grep -n cac so lieu muc 2.2.
- git show origin/main:docs/clone2-dom-bench-2win-20261122.md | wc -l (371); | grep -n 0.0112, 5/5, 0.0 px, /tmp.
- git show origin/todolist-push:tests/calibration-e2-hits.jsonl | wc -l (87); dem bang python3 json.loads theo case_id (e2-vision 17/29 = 58.6%, e2-actual 34/58 = 58.6%).
- git show origin/todolist-push:improvements/worker-click3-final-direction-log.md | grep -n CB-8 (dong 251) va DOM grounding (dong 147-148).
- git show origin/todolist-push:docs/zen-error-fix-todolist-20261121.md | grep -n 1.2.2, 2.1.2 (dong 47, 60).
- git grep dom_grounding_run origin/main (chi bao cao grounding); origin/todolist-push (khong co). git grep dom_2win_run origin/main (chi bao cao 2-window va tests/dom_bench_2win.py).
