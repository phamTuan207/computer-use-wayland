# Sua bang chung cho 2 claim CB-8 bi REVOKED, batch 11 task 3

Ngay kiem tra: 22/11/2026, 12:08 den 12:25 +07.
Hieu chinh ap dung: 22/11/2026, 12:40 den 13:05 +07, theo 4 ban review doc lap (council 1, council 2, council 3, redteam, deu batch 11 task 3). Moi hieu chinh da kiem tra lai truc tiep tu git va file truoc khi sua. Ca 2 verdict REVOKED STANDS khong doi.
Nguoi lam: subagent batch 11 task 3.
Giao viec: coord/clone1.md, batch 11 task 3, commit d9b0c05 tren origin/main.
Can cu: docs/batch10-task3-cb8-audit-20261122.md (batch 10 task 3, 2 REVOKED 1 UPHELD).
Neo kiem tra: origin/main ed9b469, origin/todolist-push 759ce41 (fetch read-only luc 12:08 +07 22/11).
Luu y neo: brief giao viec ghi todolist-push HEAD e68e578, nhung luc fetch tip da la 759ce41, them 1 commit "docs: COORD-CLICK-5 log, CLONE1-APPROVE verified DONE, clone1 batch 11 queued", khong lien quan 2 claim nay.
Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. Khong thong tin ca nhan. Khong dau gach ngang dai.
Phuong phap: chi doc tren git (git fetch, git show, git cat-file, git ls-tree, git grep, git log, git merge-base), kiem tra file local tren VM clone1, khong chay lai bench nao, khong chay lai do nao, khong bia bang chung.

## 1. Ket qua tong ket

| Claim | Verdict batch 10 task 3 | Verdict sau khi tim lai |
|---|---|---|
| (a) S2 Pick 1 DONE | REVOKED | REVOKED STANDS, khong khoi phuc duoc |
| (c) DOM-grounding DONE | REVOKED | REVOKED STANDS, khong khoi phuc duoc |

Khong claim nao duoc khoi phuc. Ly do chung: moi bang chung thieu deu van thieu o tip hien tai, khong co commit moi nao tu luc audit (neo main 81ea6e0, neo todolist-push 2ed0caf) bo sung no. Chi co 1 gap thu hep: bench grounding da co san trong repo tren main, chi can cherry-pick 7 commit sang todolist-push (merge day du ca nhanh co 8 file xung dot, xem muc 3.1).

Thay doi tu luc audit den nay, tren todolist-push tu 2ed0caf den 759ce41 co 9 commit: 759ce41, e68e578, f1b85ee, 292753f, 4ae8ccc, 2d198c4, 6aa911b, a42ef12, d2da482. Trong do chi 292753f cham den file pick1 (improvements/pick1-program-template.md, 10 dong, doi P2 element-ref), khong cham den bang chung Pick 1. Khong commit nao cham den dom_grounding, dom_bench, hay calibration. Tren main tu 81ea6e0 den ed9b469 co 0 commit cham den file pick1 hay file grounding.

## 2. Claim (a): S2 Pick 1 DONE, REVOKED STANDS

### 2.1 Gap 1: raw records P1/P2 chi o laptop, van dung

Tim lai o tip hien tai:

- `git ls-tree -r` ca origin/todolist-push va origin/main: chi co 5 file pick1/speed, khong co file nao ten summary-pick1.md hay records.jsonl trong thu muc run. Cac file co: improvements/pick1-p34fix-report.md, improvements/pick1-program-template.md, improvements/speed-proto-pick1-p34remeasure.md, improvements/speed-proto-pick1.md, improvements/summary-pick1-landing.md.
- `git log --all` theo duong dan pick1: 0 commit nao dua file records.jsonl hay summary-pick1.md cua run Pick 1 vao repo. Hieu chinh (council 1, council 3, redteam): cau goc viet gon "0 commit theo ten file records.jsonl" la khong chinh xac theo nghia rong, vi `git log --all -- "*records.jsonl"` tra ve 1 commit d336d4b, them improvements/live-a2-20261120/records.jsonl (29 dong, run A2 preflight ngay 20/11, tren nhanh speed-swarm). Commit nay khong phai ancestor cua tip todolist-push hay tip main, va file do khong chua so lieu Pick 1 nao. `git log --all -- "*summary-pick1.md"` tra ve rong that su.
- Tren VM clone1: /tmp/speed-profile-20261118/ khong ton tai, ~/workspace/speed-profile-20261118/ khong ton tai, `find ~/workspace -iname "*records.jsonl*"` khong thay file nao. Ban sao VM ma live-test-log.md:3484 tung ghi (22 dong records fetch ve VM) cung khong con.
- Chi co trich dan gian tiep trong repo, khong phai file goc:
  - improvements/live-test-log.md:3968 tren todolist-push: summary-pick1.md 8264B mtime 01:36, records.jsonl 1025 dong (vong 1).
  - Cung file :4016: rerun summary-pick1.md 10717B mtime 04:17, records.jsonl 398 dong, P1 18.89s, P2 10.18s, P3/P4 BLOCKED luc do.
  - improvements/speed-swarm-report.md:68: "Records.jsonl 398 lines, parses OK", nguon ghi ro la laptop /tmp/speed-profile-20261118/pick1/summary-pick1.md.
- Ket luan gap 1: van thieu. So lieu trich dan khop nhau giua cac file, nhung khong tinh lai duoc mean wall 37.54s xuong 17.59s hay think 35.41s xuong 15.43s tu repo vi khong co file goc.

### 2.2 Gap 2: records P3/P4 21 dong chi o laptop, van dung, them chi tiet moi

- improvements/speed-proto-pick1-p34remeasure.md:4 ghi: run dir `/tmp/speed-profile-20261118/pick1-p34remeasure/`, records.jsonl 21 dong, parses OK, analyze-p34.py trong run dir. Ca 3 deu chi o laptop, khong co trong repo.
- improvements/speed-swarm-report.md:103 trich lai y nhu vay.
- Chi tiet moi tim duoc: file P4 duoc kiem chung byte-exact (/tmp/y-tuong.txt, 128 bytes, sha256 a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170, p34remeasure.md:19) da bi xoa sau khi chay. Cung file :46: "Test artifacts removed: /tmp/hoc-ky-2, /tmp/y-tuong.txt deleted after the run". Nghia la ngay ca tren laptop, hash P4 nay gio cung khong kiem tra lai duoc tu file goc, chi con so hash trong bao cao.
- Ket luan gap 2: van thieu.

### 2.3 Gap 3: khong co lenh test verbatim, van dung

- Da doc het improvements/speed-proto-pick1-p34remeasure.md, improvements/speed-proto-pick1.md, va grep improvements/live-test-log.md tren todolist-push. Khong co dong lenh chay day du nao cho vong rerun P1/P2 hay re-measure P3/P4. Chi co mo ta phuong phap: cung wrapper timed.py, thu muc moi /tmp/speed-profile-20261118/pick1/ tren laptop (speed-proto-pick1.md:54), analyze-p34.py trong run dir.
- scripts/timed.py khong co tren ca 2 nhanh (git cat-file fail o ca origin/todolist-push va origin/main). Wrapper chi ton tai duoi dang ban sao theo tung run tren laptop.
- Ket luan gap 3: van thieu.

### 2.4 Gap 4: verdict van la PROVISIONAL, khong doi thanh FINAL

- improvements/speed-swarm-report.md:5: "Status: FINAL, PROVISIONAL verdicts (non-Astra...)"; :13: "all PROVISIONAL, non-Astra"; :15 va :127: "Verdict: SUCCESS (PROVISIONAL, non-Astra)"; :483-485: "Landing recommendation: PROVISIONAL", "Status: FINAL report, PROVISIONAL verdicts".
- improvements/speed-proto-pick1-p34remeasure.md:8: "Verdict: PROVISIONAL (non-Astra, Astra 6 out of credit)".
- improvements/pick1-p34fix-report.md:5 va :65: "Verdict: PROVISIONAL (non-Astra)", "This is mock evidence only... Verdict remains PROVISIONAL (non-Astra); do not report live success until that rerun completes".
- Khong commit nao tu luc audit sua cac dong verdict nay.
- Ket luan gap 4: van thieu dieu kien doi verdict sang FINAL.

### 2.5 Diem giam nhe van dung, them hieu chinh nho ve ancestry

- Y1b 1e/2a/2b da sua: 5 commit 3f1b951, 17fdb9b, fd63a7d, 36364b1, 4ac9320 deu la ancestor cua tip todolist-push 759ce41, da kiem tra bang git merge-base.
- scripts/code_exec.py co tren tip todolist-push, 1297 dong, blob 51c4c37. Merge pick1-landing 453adc4 la ancestor cua tip todolist-push.
- Hieu chinh nho so voi audit muc 2.2: audit ghi 4 commit 714e4f9, 84b88bb, 2e2aeff, 453adc4 "deu ton tai" theo git cat-file. Dung la ca 4 deu ton tai dang object, nhung 714e4f9 va 84b88bb KHONG phai ancestor cua tip todolist-push (759ce41) va cung KHONG phai ancestor cua tip main (ed9b469). `git branch -a --contains` chi thay 2 commit nay tren remotes/origin/y1-snippets. 714e4f9 la "feat: add verified Pick 1 snippets registry", 84b88bb la "fix: harden code execution envelopes". Code Pick 1 da land di qua merge 453adc4 (parents 21684e7, fa8ef95), khong qua 2 commit nay. Hieu chinh nay khong doi verdict, nhung trich dan 714e4f9 va 84b88bb lam bang chung code da land la khong chinh xac ve ancestry, can doi sang merge 453adc4 va cac commit Y1b o tren khi trich dan lai. Hieu chinh nay dung, council 1 xac nhan va bo sung bang chung cung co: 714e4f9 them thu muc snippets/ (snippets/manifest.json, p1-disk-free.py, p2-percent-calc.py, p3-make-dirs.py, p4-write-ideas.py, tests/test_snippets.py), nhung tren tip todolist-push thu muc snippets/ hoan toan vang (0 file), tests/test_snippets.py cung vang. Noi dung dac trung cua 714e4f9 chua tung land len todolist-push, khong chi la van de ancestry tren giay.
- Ket luan (a): REVOKED STANDS. Ca 4 gap deu van mo. De khoi phuc: commit raw records (summary-pick1.md, records.jsonl 398 dong vong rerun va 21 dong P3/P4) hoac chay lai P1-P4 tren laptop voi log va lenh chay commit trong repo, roi doi verdict sang FINAL. Chay lai la viec laptop-only vi can broker live tren laptop.

## 3. Claim (c): DOM-grounding DONE, REVOKED STANDS

### 3.1 Gap 1: bench khong co tren todolist-push, van dung, NHUNG da thu hep

- Kiem tra tai tip todolist-push 759ce41: git cat-file fail ca 3 file tests/dom_grounding_bench.py, tests/dom_grounding_fixture.html, tests/dom_bench_2win.py. Khong commit nao tu 2ed0caf den 759ce41 dua chung len nhanh nay.
- Moi so voi audit: bench va fixture CO trong repo, tren main. 3 commit 79b75e7, 47d5ee6, 7a71efc deu la ancestor cua tip main ed9b469, da kiem tra bang git merge-base. Tai tip main: tests/dom_grounding_bench.py 445 dong, tests/dom_grounding_fixture.html 49 dong, tests/dom_bench_2win.py 429 dong, docs/clone2-dom-grounding-20261122.md 401 dong, docs/clone2-dom-bench-2win-20261122.md co day du.
- Nhanh todolist-push tu thua nhan dieu nay: improvements/worker-grounding-review-log.md:30 ghi "not present on todolist-push working tree, read via git show origin/main", improvements/worker-coord-click2-log.md:28 trich "docs/clone2-dom-grounding-20261122.md on main, commit 3fd6986 + tests/dom_grounding_bench.py 79b75e7".
- Ket luan gap 1: van thieu tren nhanh direction, nhung khong con la "khong co trong repo". Viec khoi phuc gap nay gio chi la cherry-pick tu main sang todolist-push, khong can viet lai bench. Hieu chinh (council 3, redteam): cau goc "chi can merge hoac cherry-pick" noi qua ve merge. Merge day du ca nhanh main sang todolist-push co 8 file xung dot (git merge-tree, merge-base 7007efa): improvements/live-test-log.md, scripts/cu.py, scripts/cursor_session.py, scripts/overlay.py, tests/test_browser_image.py, tests/test_cursor_session.py, tests/test_endpoint_retention.py, tests/test_overlay.py. Khong file bench nao nam trong 8 file do. Duong dung la cherry-pick, da thu trong worktree tam va ap dung sach (exit 0) len tip todolist-push 759ce41. Danh sach day du la 7 commit, khong phai 5 nhu ban dau: 79b75e7, 47d5ee6, 7a71efc (bench va fixture), 3fd6986, 455b6e8 (bao cao grounding v1 va ban sua), cong e7b49ef (them bao cao 2-window, 325 dong) va 4de8c0b (sua fix pass 2-window, 79 them, 33 xoa). Neu chi cherry-pick 5 commit dau, bao cao 2-window, tuc bang chung cho gap 5, van thieu tren todolist-push (file nay co 0 lan xuat hien tren nhanh do). Cho den khi cherry-pick xong, claim van khong dat chuan CB-8 tren nhanh direction vi nhanh nay khong chua cong cu chung minh claim cua chinh no.

### 3.2 Gap 2: raw JSONL logs chi o VM clone2, van dung

- Log goc /tmp/dom_grounding_run1-5.log khong co trong repo o ca 2 nhanh (git ls-tree va git grep khong thay file log tho nao cho bench nay). Tren VM clone1: /tmp/dom_grounding_run*.log khong ton tai, `find ~ -iname "*dom_grounding*"` chi thay 2 file bench va fixture trong working tree main, khong thay log nao.
- Bao cao tren main co bang so day du, nhung khong co dong sample tho, nen median 0.030s khong tinh lai duoc tu repo.
- Ket luan gap 2: van thieu.

### 3.3 Gap 3: Zen that, live page, headed run van UNVERIFIED

- docs/clone2-dom-grounding-20261122.md tren main, muc 9 "UNVERIFIED on this machine": real Zen (moi so la Firefox 160.0.1 headless lam stand-in), headed runs va live pages (fixture local tinh). Muc 7 dong 7: "Anything not run here is labelled UNVERIFIED". Dong 62: "real Zen numbers need the laptop run".
- Tu luc audit den nay khong co do moi nao tren Zen that hay live page. 2 commit moi co chu Zen tren todolist-push (292753f, d2da482) chi la code P2 element-ref va Zen backend (ZenDomBackend), khong co so do grounding nao tren Zen.
- Ket luan gap 3: van thieu, va phan nay chi lam duoc tren laptop (live run).

### 3.4 Gap 4: DOM click khong bang chuot that, van dung

- Bao cao tren main, bang so: "5 DOM clicks (.click() in one evaluate) | 0.0022 to 0.0053 s total | DOM clicks skip the input pipeline". Todolist 1.2.2 tren todolist-push van ghi "DOM click KHONG bang chuot that".
- Ket luan gap 4: van dung, claim DONE khong bao phu duong input that.

### 3.5 Gap 5: log bench 2-window chi o /tmp, van dung

- Log /tmp/dom_2win_run1_stale_rect.log khong co trong repo. Bao cao 2-window tren main tu tiet lo failure run 1 (dong 34-39, 91-94): chi 2 of 5 clicks landed o ca 2 windows, all_five_landed false, mechanism UNKNOWN, 2 click "moved" va "scroll-btn" roi len #tall spacer o toa do stale. Fix re-read rect truoc moi click, sau do 5/5 o ca 2 windows ca 2 runs. Phan sua nay co trong bao cao, nhung log tho de kiem tra lai thi khong co.
- Ket luan gap 5: van thieu.

### 3.6 Phan corroboration kiem tra lai duoc tu repo, so lieu khop

- E2 live dem lai tu file goc tren todolist-push: tests/calibration-e2-hits.jsonl 87 dong, loc case_id e2-vision duoc 29 attempt, trong do hit true 17, hit false 12, tuc 17/29 = 58.6%, khop dung claim. docs/calibration-e2-report.md:31 va :53 ghi dung 17/29 = 58.6%. Phan E2 nay la bang chung repo-verifiable, khong doi.
- So lieu bao cao grounding kiem tra lai theo file tren main (401 dong): one-shot 66 rects pooled median 0.030s (9 samples, run medians 0.013, 0.071, 0.030), BiDi 0.006-0.054s, agreement BiDi vs Marionette toi da 5.7e-14 px, 5 pointer clicks deu trung trong 3 runs cua click step, verify bang 1 lan doc DOM 0.002-0.015s, run 2 va run 3 full 14.35s va 12.74s, run 4 va run 5 fix-pass 16.15s va 15.57s. Tat ca khop voi audit. Nhung day la so trong bao cao da commit, khong phai log tho, nen van la report-grade, chua dat proof-grade theo CB-8.
- Ghi chu phu, tim duoc khi grep, va da hieu chinh theo council 2 va redteam: mot so review tren todolist-push trich so Marionette khac voi bao cao. improvements/worker-click2-c1-review-log.md:82 va improvements/worker-click2-c3-review-log.md:22, :233 ghi "one-shot 66 rects 0.019s Marionette, 0.006-0.011s BiDi", trong khi bao cao goc ghi pooled median 0.030s voi run medians 0.013, 0.071, 0.030 (khong co run median nao la 0.019). Hieu chinh: cau goc "Nguon cua so 0.019s khong truy duoc trong repo" la sai. Nguon tim thay duoc: ban dau (v1) cua bao cao grounding, commit 3fd6986, dong 14, 85, 144, 148 ghi "66 rects in a median 0.019 s (Marionette)" va "0.019 s median (range 0.009 to 0.071)". Commit 455b6e8 ("docs: batch 7 task 2 DOM grounding, council and redteam corrections applied", 150 dong them, 77 dong xoa) da sua cac so nay thanh pooled median 0.030s (run medians 0.013, 0.071, 0.030), BiDi run medians 0.006-0.054 (pooled 0.016), per-element median 24.7 ms moi cai (1.63s total), 54x. Trong bao cao da sua, so 0.019 van xuat hien nhung o cho khac, khong phai median one-shot: dong 134 va 228, la thoi gian lap lai cua buoc a11y snapshot o run 5 (repeats 0.019 to 0.070 s; run 5: 0.019 va 0.020 s). Cac review da trich nham so a11y nay sang hang one-shot Marionette. Them 1 sai nua ma ban goc chua neu: ca cap so trong review deu sai lech so voi bao cao, vi dau tren BiDi 0.011s khong xuat hien o dau trong bao cao goc (grep "0.011" tra ve rong; BiDi run medians la 0.006 den 0.054s). Vay 0.019 la so a11y bi trich nham, 0.011 khong co nguon. Cac noi trich so v1 can sua theo so da sua, ghi nhan lam viec tiep theo, khong sua code chung o day: improvements/worker-click2-c1-review-log.md:82, improvements/worker-click2-c3-review-log.md:22, :233, va docstring ham harvest() trong scripts/zen_dom.py tren todolist-push (dong 1294-1296, "Clone2 measured one-shot 66 rects in 0.019s Marionette versus 16ms per element per-element grounding (55x slower)"). Day khong phai gap moi cua audit, nhung la them 1 ly do can log tho, va manh hon ban goc viet: median one-shot da doi tu 0.019 (v1) sang 0.030 (ban sua) ma khong co log tho trong repo de phan xu ban nao dung, va cac trich dan xuoi khong chi khong thong nhat nhau ma con trich nham hang so lieu. De nguyen ghi nhan o day, khong doi verdict vi no.

### 3.7 Ket luan (c)

REVOKED STANDS. Gap 1 thu hep (bench co tren main, chi can cherry-pick 7 commit, da thu sach len tip 759ce41), cac gap 2, 3, 4, 5 van mo hoan toan. De khoi phuc: cherry-pick bench + fixture + bench 2-window + ca 2 bao cao tu main sang todolist-push (7 commit o muc 3.1, khong merge day du), commit raw logs (dom_grounding_run1-5.log, dom_2win_run1_stale_rect.log), chay tren Zen that va live page tren laptop, roi ghi lai pham vi claim theo dung nhung gi da do (fixture headless Firefox, khong phai live Zen; DOM click khong phai chuot that).

## 4. Bang chung chi co tren laptop hoac VM, tom tat

| Bang chung | O dau | Trang thai |
|---|---|---|
| summary-pick1.md (10717B rerun, 8264B vong 1), records.jsonl 398 dong rerun, 1025 dong vong 1 | laptop /tmp/speed-profile-20261118/pick1/ | chi o laptop, khong co trong repo, khong con tren VM clone1 |
| records.jsonl 21 dong P3/P4, analyze-p34.py, timed.py | laptop /tmp/speed-profile-20261118/pick1-p34remeasure/ | chi o laptop, khong co trong repo |
| File P4 /tmp/y-tuong.txt 128 bytes (sha256 a6e58cb9...) | laptop, da xoa sau run | khong kiem tra lai duoc nua, chi con hash trong bao cao |
| Lenh chay verbatim P1-P4 (timed.py) | laptop, wrapper ngoai repo | khong co trong repo, scripts/timed.py cung khong co tren ca 2 nhanh |
| /tmp/dom_grounding_run1-5.log | VM clone2 | chi o VM clone2, khong co trong repo, khong con tren VM clone1 |
| /tmp/dom_2win_run1_stale_rect.log | VM clone2 | chi o VM clone2, khong co trong repo |
| /tmp/grounding.md, ban sao bao cao grounding (21658 byte, mtime 05:13 22/11) | VM clone1 /tmp | report-grade, byte-identical voi docs/clone2-dom-grounding-20261122.md tren main, nguon goc khong ro, khong cuu duoc gap 2 vi khong phai log tho; can lam ro ai sao chep, tu dau, luc nao |
| Do tren Zen that, live page, headed run | laptop | chua tung chay, muc 9 bao cao ghi UNVERIFIED |
| results.json bench 2-vision (ca 2 run) | da mat o local | da ghi trong audit muc 3.3, khong thuoc pham vi 2 claim nay, chi nhac lai vi lien quan den trich dan run moi |

## 5. Viec can lam tiep theo (cho dieu phoi quyet)

1. (a): commit raw records Pick 1 hoac chay lai P1-P4 tren laptop voi log va lenh chay commit trong repo, roi doi verdict sang FINAL. Khong co cach khoi phuc nao khac vi file goc khong ton tai o dau khac ngoai laptop, va file P4 goc da bi xoa.
2. (c): cherry-pick bench + fixture + bench 2-window + ca 2 bao cao tu main sang todolist-push, dung danh sach 7 commit: 79b75e7, 47d5ee6, 7a71efc, 3fd6986, 455b6e8, e7b49ef, 4de8c0b. Da thu ap dung sach len tip 759ce41 trong worktree tam. Khong merge day du ca nhanh main (8 file xung dot). Sau do commit raw logs, chay tren Zen that va live page tren laptop, ghi lai pham vi claim.
3. (c) phu: sua cac trich dan so v1 sang so da sua (0.030s pooled median, BiDi 0.006-0.054, per-element 24.7 ms, 54x) o improvements/worker-click2-c1-review-log.md:82, improvements/worker-click2-c3-review-log.md:22, :233, va docstring ham harvest() trong scripts/zen_dom.py (dong 1294-1296). Nguon so 0.019s da tim thay: v1 bao cao commit 3fd6986, va so 0.019 trong bao cao da sua chi la thoi gian lap lai a11y snapshot o run 5, bi trich nham sang Marionette one-shot; dau tren BiDi 0.011s khong co o dau trong bao cao. Can log tho de quyet ban so nao dung.
4. (a) phu: khi trich dan lai code Pick 1 da land, dung merge 453adc4 va cac commit Y1b (3f1b951, 17fdb9b, fd63a7d) thay vi 714e4f9 va 84b88bb, vi 2 commit sau chi co tren nhanh y1-snippets, khong phai ancestor cua tip todolist-push hay main.
5. Khong dung 2 claim nay lam gate cho rung 2 live cho den khi muc 1 va 2 xong. Claim (b) bench 2-vision van UPHELD tren trich dan run moi d7d569b theo audit, khong thuoc pham vi sua o day.
6. (c) phu: lam ro nguon goc /tmp/grounding.md tren VM clone1 (ai sao chep, tu dau, luc nao), va hoi clone2 xem VM cua minh co ban sao tuong tu va log tho con khong. Ban sao nay chi la report-grade, khong doi verdict.
7. Ghi chu ve do phu (council 3, da bu sau ban goc): quet het 39 ref remote, 37 dangling commit (git fsck), stash (rong), reflog, PR va issue tren GitHub (ca 2 rong), va liet ke /tmp, tat ca deu am tinh, khong tim thay bang chung nao cuu duoc claim (a) hay (c). Chay lai chi tao run moi, khong tai tao duoc log cu: rieng P4, file goc /tmp/y-tuong.txt 128 byte da bi xoa sau run, nen can fixture P4 moi va ghi ro do la run moi; bench hien tai tren main da qua fix pass 47d5ee6, nen chay lai se la run 6 tro di, khong phai tai tao run 1 den run 5.
