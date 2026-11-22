# Council 2, batch 11 task 3: kiem tra doc lap claim (c) DOM-grounding

Ngay kiem tra: 22/11/2026, 12:12 den 12:35 +07.
Nguoi lam: council 2, batch 11 task 3.
Giao viec: coord/clone1.md, batch 11 task 3, commit d9b0c05 tren origin/main.
Doi tuong kiem tra: docs/batch11-task3-cb8-evidence-repair-20261122.md (ban sua bang chung, goi tat la ban ghi task 3), chi phan claim (c).
Neo kiem tra: origin/main f07da6b, origin/todolist-push 759ce41 (fetch read-only luc 12:12 +07 22/11).
Luu y neo: ban ghi task 3 neo o main ed9b469, nhung luc kiem tra tip main da la f07da6b, them 2 commit watchdog (ed9b469, f07da6b) khong cham den file grounding nao. Tip todolist-push van 759ce41, khong doi. Moi ket luan duoi day dung o ca neo cu va neo moi.
Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. Khong thong tin ca nhan. Khong dau gach ngang dai.
Phuong phap: tu doc lai tu git va file, khong tin loi cua ban ghi task 3. Dung git fetch, git cat-file, git ls-tree, git grep, git log, git merge-base, git show, wc -l, va dem lai bang python tu file goc. Khong chay lai bench nao.

## 0. Verdict

REVOKED STANDS, xac nhan. Gap 1 thu hep la dung. Khong gap nao duoc dong.

Co 1 hieu chinh doi voi ban ghi task 3, muc 3.6: so 0.019s Marionette KHONG phai khong truy duoc nguon. Nguon cua no tim thay trong repo: ban dau (v1) cua bao cao grounding, commit 3fd6986, da bi sua lai boi commit 455b6e8. Hieu chinh nay khong doi verdict, no con lam manh them ly do can log tho, vi median da doi giua 2 ban ma khong co log tho trong repo de phan xu. Chi tiet o muc 5.

## 1. Gap 1: bench vang tren todolist-push, co tren main, XAC NHAN

Kiem tra truc tiep bang git cat-file o tip hien tai:

- Tren origin/todolist-push (759ce41): ca 3 file deu vang. git cat-file bao loi cho tests/dom_grounding_bench.py, tests/dom_grounding_fixture.html, tests/dom_bench_2win.py.
- Tren origin/main (f07da6b): ca 3 file deu co. So dong do truc tiep: tests/dom_grounding_bench.py 445 dong, tests/dom_grounding_fixture.html 49 dong, tests/dom_bench_2win.py 429 dong. Bao cao docs/clone2-dom-grounding-20261122.md 401 dong, bao cao 2-window docs/clone2-dom-bench-2win-20261122.md 371 dong.
- 3 commit 79b75e7, 47d5ee6, 7a71efc: git merge-base --is-ancestor xac nhan ca 3 deu la ancestor cua tip main, va ca 3 deu KHONG phai ancestor cua tip todolist-push. Noi dung tung commit khop mo ta: 79b75e7 them bench 354 dong va fixture 49 dong, 47d5ee6 them buoc a11y snapshot vao bench, 7a71efc them bench 2-window 429 dong.
- git ls-tree -r origin/todolist-push, loc dom_grounding va dom_bench: 0 file. Tren main: dung 4 file (3 bench/fixture cong bao cao grounding).
- Tu luc audit den nay, khong commit nao dua bench sang todolist-push: git log 2ed0caf..759ce41 (9 commit, dem lai dung 9) loc theo 6 duong dan grounding va calibration cho ket qua rong. Tren main tu 81ea6e0 den f07da6b loc theo file grounding cung rong.
- Nhan xet them: nhanh todolist-push tu thua nhan dieu nay trong improvements/worker-grounding-review-log.md:30 ("not present on todolist-push working tree, read via git show origin/main").

Ket luan gap 1: van mo tren nhanh direction, nhung thu hep dung nhu ban ghi task 3 noi. Viec khoi phuc gap nay chi la merge hoac cherry-pick tu main sang todolist-push, khong can viet lai bench. Cho den khi merge xong, claim van khong dat chuan CB-8 tren nhanh direction.

## 2. Gap 2: raw JSONL logs van vang, XAC NHAN

- git ls-tree -r ca 2 nhanh, loc dom_grounding_run va dom_2win_run: khong co file log tho nao. Cac file .log co tren todolist-push deu la log khac, khong lien quan bench nay.
- git grep "dom_grounding_run1-5" tren origin/main chi trung 2 file tai lieu audit (docs/batch10-task3-cb8-audit-20261122.md, docs/batch10-council3-task3-20261122.md), khong phai file log. Tren todolist-push, grep cum nay cho 0 ket qua.
- Tren VM clone1: ls /tmp/dom_grounding_run*.log va /tmp/dom_2win_run1_stale_rect.log deu bao khong co file. find chi thay 2 file bench va fixture trong working tree main, khong thay log nao.
- Bao cao grounding tu ghi ro log o /tmp/dom_grounding_run1.log den run5.log, "kept on this machine, outside the repo". Bao cao 2-window ghi cac log /tmp/dom_2win_run1.log, run2.log, run0_crash.log, run1_stale_rect.log, cung ngoai repo.

Ket luan gap 2: van thieu hoan toan. Median 0.030s khong tinh lai duoc tu repo.

## 3. Gap 3: Zen that, live page, headed run van UNVERIFIED, XAC NHAN

- Bao cao grounding tren main, muc 9 "UNVERIFIED on this machine": so lieu deu la Firefox 160.0.1 lam stand-in, "real Zen numbers need the laptop run", fixture local tinh, headed runs va live pages chua chay.
- 2 commit moi co chu Zen trong 9 commit tu 2ed0caf den 759ce41 la 292753f (P2 element-ref rewrite: protocol, A9 screen point, Zen backend, verified-origin validator) va d2da482 (test: failing-first P2 element-ref tests, 1050 dong test). Ca 2 deu la code va test P2 element-ref, khong co so do grounding nao tren Zen that hay live page. Da kiem tra bang git show --stat.
- Khong co do moi nao tren file grounding tu luc audit, theo muc 1.

Ket luan gap 3: van thieu, va phan nay chi lam duoc tren laptop.

## 4. Gap 4: DOM click khong bang chuot that, XAC NHAN

- Bao cao grounding, bang muc 2: "5 DOM clicks (.click() in one evaluate) | 0.0022 to 0.0053 s total | DOM clicks skip the input pipeline".
- improvements/worker-grounding-review-log.md tren todolist-push trich lai dung y nay: DOM clicks skip the input pipeline, 0.0022-0.0053s.

Ket luan gap 4: van dung, claim DONE khong bao phu duong input that.

## 5. Gap 5: log bench 2-window van vang, XAC NHAN, cong hieu chinh ve 0.019s

### 5.1 Gap 5

- Bao cao 2-window tren main (371 dong, dem lai): run 1 stale rect, 2 of 5 clicks roi len #tall spacer o ca 2 windows, clicked log "btn-3;btn-17;btn-42;tall;tall;", counter "clicks: 5", all_five_landed false, mechanism UNKNOWN, dong 34-39 va 263-281. Fix re-read rect truoc moi click, sau do 5/5 o ca 2 windows ca 2 runs, dong 47-52 va 194.
- Log /tmp/dom_2win_run1_stale_rect.log khong co trong repo o ca 2 nhanh (muc 2) va khong co tren VM clone1.
- Phan sua co trong bao cao, nhung log tho de kiem tra lai thi khong co.

Ket luan gap 5: van thieu.

### 5.2 Hieu chinh: nguon so 0.019s Marionette TIM THAY DUOC, ban ghi task 3 noi sai o diem nay

Ban ghi task 3, muc 3.6, viet: "Nguon cua so 0.019s khong truy duoc trong repo". Kiem tra lai truc tiep cho thay cau nay sai.

Nguon la ban dau (v1) cua bao cao grounding, commit 3fd6986, truoc khi duoc sua:

- 3fd6986, dong 14: "gives 66 rects in a median 0.019 s (Marionette) or about 0.006 to 0.011 s (BiDi)".
- 3fd6986, dong 85, bang muc 2: "One shot, all 66 rects | 0.019 s median (range 0.009 to 0.071) | 0.006 to 0.011 s".
- 3fd6986, dong 144-148: "one shot rects 0.019 s median, per-element rects 16 ms each", "pays 66 round trips for what one evaluate does in 0.019 s", "55x slower than one shot".
- Commit sua 455b6e8 ("docs: batch 7 task 2 DOM grounding, council and redteam corrections applied", 150 dong them, 77 dong xoa) doi cac so nay thanh pooled median 0.030s (run medians 0.013, 0.071, 0.030), BiDi run medians 0.006-0.054 (pooled 0.016), per-element median 24.7 ms moi cai (1.63s total), 54x. Ghi chu sua trong bao cao hien tai noi ro: council va redteam thay mot so so o ban dau sai so voi log duoc bao ton, trong do co table medians.
- Cac trich dan xuoi dung dung bo so v1, khong dung so da sua: improvements/worker-click2-c1-review-log.md:82 ("one-shot 66 rects in 0.019s Marionette / 0.006-0.011s BiDi versus 16ms per element (55x slower)"), improvements/worker-click2-c3-review-log.md:22 va :233 (cung bo so), va scripts/zen_dom.py ham harvest() tren todolist-push, dong 1294-1296 ("Clone2 measured one-shot 66 rects in 0.019s Marionette versus 16ms per element per-element grounding (55x slower)"). Bo 3 so 0.019s, 0.006-0.011s, 16ms/55x chi xuat hien cung nhau o v1, nen day la bang chung cac noi tren trich tu v1, khong phai tu bao cao da sua.
- Luu y them: so 0.019 van xuat hien trong bao cao da sua, nhung o cho khac, khong phai median one-shot: dong 134 va 228, la thoi gian lap lai cua a11y snapshot o run 5 (repeats 0.019 to 0.070 s; run 5: 0.019 va 0.020 s). Khong co run median one-shot nao la 0.019 trong bao cao da sua (cac run median la 0.013, 0.071, 0.030). Ai chi grep 0.019 trong bao cao hien tai se nham sang so a11y nay.
- Audit batch 10 khong he nhac den 0.019 (grep trong docs/batch10-task3-cb8-audit-20261122.md cho 0 ket qua), nen ghi chu nay la moi o task 3, va no sai ve tinh truy duoc.

Anh huong cua hieu chinh: khong doi verdict. No lam manh them ly do can log tho: median one-shot da doi tu 0.019 (v1) sang 0.030 (ban sua) ma khong co log tho trong repo de phan xu ban nao dung, va 3 noi ha tang (2 review log, 1 docstring trong code) van trich so v1 da bi rut lai. Can lam tiep theo: sua docstring scripts/zen_dom.py va 2 review log sang so da sua (0.030s pooled median, BiDi 0.006-0.054, per-element 24.7 ms, 54x), hoac ghi ro chung dang trich v1 da bi rut lai. Viec nay thuoc ve dieu phoi quyet, khong phai mot gap moi cua audit.

## 6. Corroboration E2 va so lieu bao cao grounding, XAC NHAN

### 6.1 E2: dem lai tu file goc, khop dung 17/29 = 58.6%

Dem lai bang python (json.loads) tu file goc tren todolist-push, tests/calibration-e2-hits.jsonl:

- Tong so dong: 87.
- Loc case_id e2-vision: 29 attempt.
- hit true: 17. hit false: 12. Khong co gia tri hit nao khac.
- 17/29 = 58.6207%, lam tron 58.6%.
- docs/calibration-e2-report.md:31 va :53 ghi dung 17/29 = 58.6%, Grid A 8/20, Grid B 9/9, khop voi dem lai.

Luu y phuong phap: grep -c '"hit": true' cho 0 vi JSON ghi true tran (khong co dau ngoac kep), nen dem bang grep tho se sai. Dem bang python tren la dang tin.

Phan E2 nay la bang chung repo-verifiable, khong doi. No chi la corroboration cho huong thiet ke (vision yeu, DOM manh), khong phai log tho cua bench grounding, nen no khong lap day gap 2.

### 6.2 So lieu bao cao grounding, khop dung voi ban ghi task 3

Doc lai toan bo file tren main, docs/clone2-dom-grounding-20261122.md, 401 dong:

- One-shot 66 rects: pooled median 0.030s Marionette, 9 samples, range 0.0085-0.096, run medians 0.013, 0.071, 0.030. BiDi run medians 0.006-0.054s, pooled median 0.016s.
- Agreement BiDi vs Marionette: max delta 5.7e-14 px. One-shot vs per-element: max delta 0.0 px.
- 5 pointer clicks deu trung trong 3 runs cua click step (2 full, 1 partial).
- Verify bang 1 lan doc DOM: 0.002-0.015s.
- Run totals: run 2 full 14.35s, run 3 full 12.74s, run 4 fix-pass 16.15s, run 5 fix-pass 15.57s.
- Tat ca khop voi ban ghi task 3, muc 3.6.

Nhung day la so trong bao cao da commit, khong phai log tho, nen van la report-grade, chua dat proof-grade theo CB-8. Diem nay ban ghi task 3 noi dung.

## 7. Ket luan (c)

REVOKED STANDS, xac nhan. Gap 1 thu hep (bench co tren main, chi can merge sang todolist-push), cac gap 2, 3, 4, 5 van mo hoan toan. De khoi phuc: merge bench + fixture + bench 2-window tu main sang todolist-push, commit raw logs (dom_grounding_run1-5.log, dom_2win_run1_stale_rect.log), chay tren Zen that va live page tren laptop, roi ghi lai pham vi claim theo dung nhung gi da do (fixture headless Firefox, khong phai live Zen; DOM click khong phai chuot that).

Hieu chinh duy nhat doi voi ban ghi task 3: muc 3.6 noi nguon so 0.019s khong truy duoc la sai. Nguon la v1 cua bao cao grounding, commit 3fd6986, da bi sua boi 455b6e8. Cac trich dan 0.019s trong c1-review-log, c3-review-log va docstring scripts/zen_dom.py deu trich tu v1 da bi rut lai va can duoc sua theo so da sua. Hieu chinh nay khong khoi phuc claim, khong dong gap nao.

## 8. Bang kiem tra tung diem cua ban ghi task 3, phan claim (c)

| Diem trong ban ghi task 3 | Ket qua kiem tra doc lap |
|---|---|
| Gap 1: bench vang tren todolist-push | Dung. git cat-file fail ca 3 file o 759ce41. |
| Gap 1: bench co tren main, commit 79b75e7, 47d5ee6, 7a71efc | Dung. Ca 3 la ancestor cua main, khong phai ancestor cua todolist-push. Bench 445 dong, fixture 49 dong, bench 2-window 429 dong. |
| Gap 1: thu hep, chi can merge | Dung. Khong commit nao tu 2ed0caf den 759ce41 cham den file grounding. |
| Gap 2: raw logs van vang | Dung. Khong co trong ls-tree ca 2 nhanh, khong co tren VM clone1. |
| Gap 3: Zen that, live page, headed van UNVERIFIED | Dung. Muc 9 bao cao ghi ro, khong co do moi. 292753f va d2da482 la code/test P2, khong co so grounding. |
| Gap 4: DOM click khong bang chuot that | Dung. Bang muc 2 bao cao: DOM clicks skip the input pipeline. |
| Gap 5: log 2-window van vang | Dung. Bao cao 2-window 371 dong ghi day du failure run 1 va fix, log tho khong co trong repo. |
| E2: 29 attempts, 17 true, 12 false = 58.6% | Dung. Dem lai bang python tu file goc: 87 dong, 29 e2-vision, 17 true, 12 false, 58.6207%. |
| Bao cao grounding 401 dong, pooled median 0.030s, runs 14.35/12.74/16.15/15.57s | Dung. Doc lai toan bo file tren main, khop tung so. |
| 0.019s Marionette: nguon khong truy duoc | SAI, da hieu chinh o muc 5.2. Nguon la v1 bao cao, commit 3fd6986, da bi sua boi 455b6e8. |
| REVOKED STANDS, gap 1 thu hep | Dung. Hieu chinh ve 0.019s khong doi verdict. |
