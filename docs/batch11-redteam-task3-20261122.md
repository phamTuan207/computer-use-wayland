# Redteam ban ghi sua bang chung CB-8, batch 11 task 3

Ngay kiem tra: 22/11/2026, 12:12 den 12:35 +07.
Nguoi lam: subagent redteam batch 11 task 3 (doc lap, chi tan cong, khong sua ban ghi goc).
Giao viec: coord/clone1.md, batch 11 task 3, commit d9b0c05 tren origin/main.
Doi tuong: docs/batch11-task3-cb8-evidence-repair-20261122.md (ban ghi task 3, neo origin/main ed9b469, origin/todolist-push 759ce41).
Can cu doi chieu: docs/batch10-task3-cb8-audit-20261122.md.
Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. Khong thong tin ca nhan. Khong dau gach ngang dai. De nguyen test-w.txt (0 byte, untracked).
Phuong phap: chi doc tren git (git fetch, git show, git cat-file, git ls-tree, git grep, git log, git merge-base, git merge-tree), kiem tra file local tren VM clone1, cherry-pick thu trong worktree tam o /tmp roi xoa, khong chay lai bench nao, khong bia bang chung.

## 0. Neo kiem tra cua redteam

Luc redteam fetch (12:13 +07 22/11), origin/main da tien len f07da6b, them 1 commit duy nhat sau neo cua ban ghi task 3:

- f07da6b clone2: watchdog log 12:09 22/11, no stall, clone1 back with batch 11. Chi sua docs/clone2-watchdog-log.md, 10 dong. Khong them bang chung nao cho 2 claim.
- origin/todolist-push van dung o 759ce41, khong co commit moi.
- Brief giao viec dung nhu ban ghi task 3 noi: coord/clone1.md:3911 tai d9b0c05 ghi todolist-push HEAD e68e578. Tu e68e578 den 759ce41 dung la 1 commit (759ce41).

## 1. Ket qua tong ket

| Claim | Verdict ban ghi task 3 | Verdict sau redteam |
|---|---|---|
| (a) S2 Pick 1 DONE | REVOKED STANDS | REVOKED STANDS, khong khoi phuc duoc |
| (c) DOM-grounding DONE | REVOKED STANDS | REVOKED STANDS, khong khoi phuc duoc |

So verdict bi pha vo: 0 trong 2. Ca 2 verdict deu dung vung.
So phat bieu sai trong ban ghi task 3: 3, khong cai nao doi verdict:

1. Muc 2.1: "git log --all ... records.jsonl: 0 commit" la sai nhu viet. Co 1 commit dua 1 file records.jsonl vao repo, nhung la file khac, khong phai records Pick 1. Xem muc 2.
2. Muc 3.6: "Nguon cua so 0.019s khong truy duoc trong repo" la sai. So 0.019s co trong bao cao goc, nhung o hang a11y snapshot, bi cac review trich nham sang Marionette one-shot. Xem muc 3.
3. Muc 1, 3.1, 5: "chi can merge" la noi qua neu hieu la merge ca nhanh main sang todolist-push. Merge day du co 8 file xung dot. Chi cherry-pick 3 commit bench moi sach. Xem muc 4.

Them 1 gap ban ghi task 3 chua neu het: khoang BiDi "0.006-0.011s" trong cac review cung khong khop bao cao goc, dau tren 0.011 khong co o dau trong bao cao. Xem muc 3.2. Diem nay cung co huong ban ghi task 3, khong doi verdict.

## 2. Phat bieu sai 1: records.jsonl co 1 commit trong lich su, khong phai 0

Ban ghi task 3, muc 2.1, viet: "git log --all theo ten file summary-pick1.md va records.jsonl: 0 commit nao dua 2 file goc nay vao repo."

Kiem tra lai:

```
$ git log --all --oneline -- '*summary-pick1.md'
(khong co dong nao)
$ git log --all --oneline -- '*records.jsonl'
d336d4b docs: A4 postcondition + A2 preflight live measure 2026-11-20 (rounds 1-3, A2 INCONCLUSIVE)
```

Commit d336d4b dua file nay vao repo:

```
$ git show --stat --oneline d336d4b | grep records
 improvements/live-a2-20261120/records.jsonl        |  29 ++++
 improvements/live-a4-20261120/records-round1.jsonl |  24 +++
 improvements/live-a4-20261120/records-round2.jsonl |  33 +++
 improvements/live-a4-20261120/records-round3.jsonl |  12 +++
```

Day la records cua run A2 preflight ngay 20/11, 29 dong, tren nhanh speed-swarm, khong phai records Pick 1 (398 dong vong rerun, 1025 dong vong 1, 21 dong P3/P4). Kiem tra ancestry:

```
$ git merge-base --is-ancestor d336d4b origin/todolist-push || echo "NOT ancestor todolist-push"
NOT ancestor todolist-push
$ git merge-base --is-ancestor d336d4b origin/main || echo "NOT ancestor main"
NOT ancestor main
$ git branch -a --contains d336d4b
  remotes/origin/speed-swarm
```

Va trong cay cua ca 2 tip, khong co file nao ten records.jsonl:

```
$ git ls-tree -r origin/todolist-push --name-only | grep -i "records.jsonl"
(khong co dong nao)
$ git ls-tree -r origin/main --name-only | grep -i "records.jsonl"
(khong co dong nao)
```

Ket luan: phat bieu "0 commit" sai nhu viet, can sua thanh: 0 commit cho records.jsonl cua run Pick 1; co 1 file records.jsonl khong lien quan tren nhanh speed-swarm (d336d4b, 29 dong, A2 preflight). Verdict (a) khong doi, vi file do khong chua so lieu Pick 1 nao va khong co trong cay cua 2 nhanh direction.

Phan con lai cua muc 2.1 dung: summary-pick1.md that su 0 commit tren moi nhanh (`git log --all -- '*summary-pick1.md'` rong), chi co improvements/summary-pick1-landing.md (commit fa8ef95), la file khac. Redteam doc het file landing nay: no chi ghi code da land va ket qua unit test, khong co bang so wall/think theo task, khong tinh lai duoc mean 37.54s xuong 17.59s tu no.

## 3. Phat bieu sai 2: nguon cua so 0.019s truy duoc, la so a11y bi trich nham

Ban ghi task 3, muc 3.6, viet: cac review trich "one-shot 66 rects 0.019s Marionette", trong khi bao cao goc ghi pooled median 0.030s voi run medians 0.013, 0.071, 0.030 (khong co run median nao la 0.019), roi ket: "Nguon cua so 0.019s khong truy duoc trong repo."

Kiem tra lai trong bao cao goc tren main:

```
$ git show origin/main:docs/clone2-dom-grounding-20261122.md | grep -n "0.019"
134:| a11y snapshot, whole page | first 0.045 to 0.147 s, repeats 0.019 to 0.070 s | not measured here | 83 nodes, 4,641 chars compact JSON {role, name, children}, to_text 1,851 chars |
228:and 0.045 s, repeats 0.039 and 0.070 s (run 4) and 0.019 and
```

Nguyen van dong 225-230:

```
a11y_snapshot_page and a11y_snapshot_one_element (fix-pass runs
4 and 5, logs /tmp/dom_grounding_run4.log and
/tmp/dom_grounding_run5.log): whole page snapshot first 0.147 s
and 0.045 s, repeats 0.039 and 0.070 s (run 4) and 0.019 and
0.020 s (run 5), 83 nodes, 4,641 chars of compact JSON
```

Nguon cua so 0.019s truy duoc ro rang: no la dau duoi khoang repeat cua buoc a11y snapshot o run 5 (0.019 va 0.020 s), khong phai so Marionette one-shot. Cac review click2 da trich nham hang a11y sang hang one-shot Marionette. Ban ghi task 3 dung o cho so 0.019 khong khop bat ky run median one-shot nao, nhung sai o cho "khong truy duoc". Cach viet dung: nguon da tim thay, la hieu nham hang so lieu.

Hau qua doi voi verdict (c): khong doi. Diem nay that ra lam manh them ly do can log tho: cac trich dan xuoi khong chi khong thong nhat nhau ma con trich nham hang so lieu trong cung mot bao cao. Verdict REVOKED STANDS van dung.

### 3.1 Trich dan 0.019s trong review, da kiem tra lai

- improvements/worker-click2-c1-review-log.md:82 tren todolist-push: "Clone2 measured one-shot 66 rects in 0.019s Marionette / 0.006-0.011s BiDi". Dung nhu ban ghi task 3 trich.
- improvements/worker-click2-c3-review-log.md:22 va :233 tren todolist-push: "one-shot 66 rects 0.019s Marionette, 0.006-0.011s BiDi" va "one-shot 66 rects 0.019s Marionette vs 16 ms each per-element". Dung nhu ban ghi task 3 trich.

### 3.2 Them 1 so khong khop ma ban ghi task 3 chua neu: dau tren BiDi 0.011s

Cung cap so "0.019s Marionette / 0.006-0.011s BiDi" trong 2 review tren co them 1 so khong khop ma ban ghi task 3 khong de cap. Bao cao goc, dong 23 va dong 127:

```
23: samples across 3 runs) or 0.006 to 0.054 s per run median (BiDi),
127:| One shot, all 66 rects | 0.030 s pooled median (9 samples, range 0.0085 to 0.096; run medians 0.013, 0.071, 0.030) | run medians 0.006 to 0.054 s (pooled median 0.016 s, 9 samples, range 0.0048 to 0.124) | ...
```

Dau duoi 0.006 khop, nhung dau tren 0.011 khong khop khoang run median BiDi (0.006 den 0.054), va:

```
$ git show origin/main:docs/clone2-dom-grounding-20261122.md | grep -n "0.011"
(khong co dong nao)
```

So 0.011 khong xuat hien o dau trong bao cao goc. Vay ca cap so trong review deu sai lech so voi bao cao: 0.019 la so a11y bi trich nham, 0.011 khong co nguon. Day la gap trich dan ma ban ghi task 3 chua neu het, cung huong voi nhan xet cua no, khong doi verdict.

## 4. Giam nhe noi qua: "chi can merge" thanh "chi can cherry-pick", merge day du khong sach

Ban ghi task 3, muc 1, 3.1 va 5, viet gap 1 cua claim (c) "gio chi la merge hoac cherry-pick tu main sang todolist-push, khong can viet lai bench".

Redteam thu merge day du bang lenh chi doc:

```
$ git merge-tree $(git merge-base origin/main origin/todolist-push) origin/main origin/todolist-push > /tmp/mergetree.txt
merge-base: 7007efa OPT-M1: log correction (real times) + follow-ups + done
$ grep -c "^changed in both" /tmp/mergetree.txt
8
```

8 file xung dot khi merge ca nhanh main vao todolist-push:

- improvements/live-test-log.md
- scripts/cu.py
- scripts/cursor_session.py
- scripts/overlay.py
- tests/test_browser_image.py
- tests/test_cursor_session.py
- tests/test_endpoint_retention.py
- tests/test_overlay.py

Khong file bench nao nam trong 8 file xung dot. Va cherry-pick dung 3 commit bench thi sach. Redteam thu trong worktree tam, khong cham nhanh nao:

```
$ git worktree add --detach /tmp/rt11-wt origin/todolist-push
HEAD is now at 759ce41 docs: COORD-CLICK-5 log, CLONE1-APPROVE verified DONE, clone1 batch 11 queued
$ git cherry-pick --no-commit 79b75e7 47d5ee6 7a71efc
$ git status --short
A  tests/dom_bench_2win.py
A  tests/dom_grounding_bench.py
A  tests/dom_grounding_fixture.html
```

Sau do abort cherry-pick, xoa worktree, `git worktree prune`. Khong de lai thay doi nao trong repo.

Ket luan: phan giam nhe dung ve ban chat (bench chi can dua sang, khong can viet lai), nhung cach viet "chi can merge" noi qua. Cach viet dung: cherry-pick 3 commit 79b75e7, 47d5ee6, 7a71efc la sach; merge ca nhanh main thi co 8 file xung dot va khong nen dung de dong gap nay. Verdict (c) khong doi, vi gap 1 van chua duoc dong o tip hien tai du no de dong.

Kiem tra phu: moi commit dung noi dung nhu ban ghi task 3 noi. 79b75e7 dua tests/dom_grounding_bench.py va tests/dom_grounding_fixture.html; 47d5ee6 sua tests/dom_grounding_bench.py; 7a71efc dua tests/dom_bench_2win.py; 455b6e8 va 3fd6986 sua docs/clone2-dom-grounding-20261122.md.

## 5. Cac duong khoi phuc da thu va that bai

Redteam co gang tim bang chung co the khoi phuc (a) hoac (c). Tat ca deu khong co ket qua.

### 5.1 Claim (a): khong co ban sao nao khac cua records Pick 1

- `git log --all -- '*summary-pick1.md'`: 0 commit tren moi nhanh. Chi co summary-pick1-landing.md (fa8ef95), da doc, khong co so lieu tho.
- `git log --all -- '*records.jsonl'`: chi d336d4b, file A2 khong lien quan, xem muc 2.
- `git ls-tree -r` ca origin/todolist-push va origin/main: 5 file pick1 nhu ban ghi task 3 liet ke, khong co file records nao.
- Thu muc pick1-run1 (archive vong 1 tren laptop, theo speed-swarm-report.md:68 va speed-swarm-rerun-plan.md:52): chi duoc nhac trong log, khong co trong repo o bat ky nhanh nao (`git log --all -- '*pick1-run1*'` rong).
- Tren VM clone1: /tmp/speed-profile-20261118 khong ton tai, ~/workspace/speed-profile-20261118 khong ton tai, `find ~/workspace -iname "*records.jsonl*"` khong thay file nao. Ban sao VM cua records v2 (22 dong, live-test-log.md:3484) cung khong con, va do la records cua run v2 bi BLOCKED, khong phai records rerun Pick 1.
- Khong co lenh chay verbatim nao cho rerun P1/P2 hay re-measure P3/P4: grep "timed.py" trong improvements/speed-proto-pick1.md, improvements/speed-swarm-rerun-plan.md va improvements/live-test-log.md tren todolist-push chi thay nhac ten wrapper va mo ta phuong phap, khong co dong lenh chay day du nao. scripts/timed.py van khong co tren ca 2 nhanh, 0 commit trong lich su (`git log --all -- '*timed.py'` rong).

### 5.2 Claim (c): khong co log tho nao xuat hien, khong co do moi tren Zen that

- Raw logs /tmp/dom_grounding_run1-5.log va /tmp/dom_2win_run1_stale_rect.log: `git log --all -- '*dom_grounding_run*'` rong; chi co duong dan /tmp duoc nhac trong cac bao cao tren main. Tren VM clone1: ca 2 loai log deu khong ton tai, `find ~ -maxdepth 3 -iname "*dom_grounding*"` chi thay bench va fixture trong working tree main.
- Tu neo audit den nay, khong co do moi nao tren Zen that hay live page: 2 commit moi co chu Zen tren todolist-push (292753f, d2da482) la code P2 element-ref va Zen backend, khong co so do grounding nao. Tren main tu 81ea6e0 den ed9b469 co 0 commit cham file pick1 hay grounding (da kiem tra lai bang pathspec).
- Bench tren main van chua co tren todolist-push o tip 759ce41: `git cat-file -e` fail ca 3 file, dung nhu ban ghi task 3 noi.

## 6. Cac trich dan cua ban ghi task 3 da kiem tra lai va dung

Nhung muc sau redteam kiem tra doc lap bang lenh git truc tiep va thay dung, khong can sua:

- Neo va pham vi thay doi: 9 commit 2ed0caf..759ce41 dung danh sach; chi 292753f cham file pick1 (improvements/pick1-program-template.md, 10 dong); khong commit nao cham dom_grounding, dom_bench hay calibration.
- live-test-log.md tren todolist-push: :3968 summary 8264B, records 1025 dong; :4016 rerun summary 10717B, P1 18.89s, P2 10.18s; :3484 records v2 22 dong fetch ve VM. Ca 3 so dong dung theo `grep -n`.
- speed-swarm-report.md: :68 "Records.jsonl 398 lines, parses OK"; :103 "Records.jsonl 21 lines, parses OK"; :5, :13, :15, :127, :483-485 cac dong verdict PROVISIONAL va "Status: FINAL, PROVISIONAL verdicts". Dung.
- speed-proto-pick1-p34remeasure.md: :4 run dir va records 21 dong; :19 file P4 128 bytes, sha256 a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170; :46 "/tmp/hoc-ky-2, /tmp/y-tuong.txt deleted after the run". Dung.
- pick1-p34fix-report.md: :5 va :65 verdict PROVISIONAL va "This is mock evidence only". Dung.
- Hieu chinh ancestry (muc 2.5): 714e4f9 va 84b88bb chi co tren remotes/origin/y1-snippets, khong phai ancestor cua tip todolist-push hay main; 2e2aeff, 453adc4, 3f1b951, 17fdb9b, fd63a7d, 36364b1, 4ac9320 deu la ancestor cua tip todolist-push; scripts/code_exec.py o tip todolist-push 1297 dong, blob 51c4c37dceae9ecddcf3657d0bc2e0c8fdb9ac1b. Dung.
- Bench tren main: tests/dom_grounding_bench.py 445 dong, tests/dom_grounding_fixture.html 49 dong, tests/dom_bench_2win.py 429 dong, docs/clone2-dom-grounding-20261122.md 401 dong; 79b75e7, 47d5ee6, 7a71efc, 455b6e8, 3fd6986 deu la ancestor cua tip main. Dung.
- Grounding report: pooled median 0.030s, run medians 0.013, 0.071, 0.030; BiDi run medians 0.006 den 0.054s; agreement toi da 5.7e-14 px; run 2 va run 3 full 14.35s va 12.74s; run 4 va run 5 fix-pass 16.15s va 15.57s; 5 pointer clicks deu trung trong 3 runs; verify bang 1 lan doc DOM 0.002-0.015s; DOM clicks 0.0022-0.0053s; muc 9 UNVERIFIED; dong 62 "real Zen numbers need the laptop run". Dung.
- E2 dem lai tu file goc tren todolist-push: tests/calibration-e2-hits.jsonl 87 dong, loc case_id e2-vision duoc 29 attempt, hit true 17, hit false 12, 17/29 = 58.6%, khop bao cao. Dung. (Ghi chu: `grep -c '"case_id": "e2-vision"'` tra 0 do dinh dang JSON khac khoang trang, dem bang python json moi la con so dung.)
- Bench 2-window: run 1 chi 2 of 5 clicks landed o ca 2 windows, all_five_landed false, mechanism UNKNOWN, log /tmp/dom_2win_run1_stale_rect.log, clicked log "btn-3;btn-17;btn-42;tall;tall;". Dung theo docs/clone2-dom-bench-2win-20261122.md:34-39, :91-94.
- worker-grounding-review-log.md:30 va worker-coord-click2-log.md:28 trich dung bench tren main. Dung.
- Todolist 1.2.2: "DOM click KHONG bang chuot that". Dung.

## 7. Ket luan redteam

- Verdict (a) REVOKED STANDS: dung vung. Ca 4 gap van mo. Khong tim thay ban sao records nao khac, khong co lenh chay verbatim nao, verdict van PROVISIONAL.
- Verdict (c) REVOKED STANDS: dung vung. Gap 1 thu hep nhung chua dong (bench co tren main, cherry-pick sach, nhung chua cherry-pick); cac gap 2, 3, 4, 5 van mo hoan toan.
- 3 cho can sua trong ban ghi task 3 truoc khi dung lam co so quyet dinh: sua cau "0 commit records.jsonl" thanh pham vi dung (muc 2); sua "nguon 0.019s khong truy duoc" thanh da tim thay, la so a11y bi trich nham (muc 3); sua "chi can merge" thanh "chi can cherry-pick 3 commit bench", vi merge day du co 8 file xung dot (muc 4).
- Them 1 ghi chu: dau tren BiDi 0.011s trong cac review click2 khong co o dau trong bao cao goc, nen cap so "0.019s Marionette / 0.006-0.011s BiDi" deu khong dung voi bao cao (muc 3.2). Can log tho de quyet, dung nhu ban ghi task 3 ket o muc 5 diem 3, nhung ly do nay con manh hon no viet: khong chi khong khop run median nao ma mot so la trich nham hang, mot so khong co nguon.
- Khong dung 2 claim nay lam gate cho rung 2 live cho den khi cac buoc khoi phuc o muc 5 cua ban ghi task 3 xong, voi sua doi o muc 7 tren day.
