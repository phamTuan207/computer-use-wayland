# Council 1, batch 11 task 3: kiem tra doc lap claim (a) S2 Pick 1 DONE

Ngay kiem tra: 22/11/2026, 12:12 den 12:30 +07.
Nguoi lam: council 1, batch 11.
Giao viec: coord/clone1.md, batch 11 task 3, commit d9b0c05 tren origin/main.
Doi tuong kiem tra: docs/batch11-task3-cb8-evidence-repair-20261122.md, muc 2 (claim (a)) va muc 1 lien quan.
Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. Khong thong tin ca nhan. Khong dau gach ngang dai.
Phuong phap: tu suy luan lai tung diem tu git (fetch read-only, log, ls-tree, cat-file, merge-base, branch --contains, grep, show) va file tren VM clone1. Khong chay lai bench nao, khong chay lai do nao, khong tin loi cua ban ghi.

## 0. Neo kiem tra

- origin/main luc kiem tra: f07da6b. Ban ghi neo o ed9b469. Tu ed9b469 den f07da6b chi co 1 commit f07da6b, "clone2: watchdog log 12:09 22/11", chi sua docs/clone2-watchdog-log.md (10 dong them), khong cham gi den Pick 1. Nen ket luan ve claim (a) khong doi.
- origin/todolist-push luc kiem tra: 759ce41, trung neo cua ban ghi.
- origin/y1-snippets luc kiem tra: 6366d24.
- test-w.txt (0 byte, untracked) de nguyen, khong dung den.

## 1. Verdict: REVOKED STANDS, duoc xac nhan

Ca 4 gap cua claim (a) deu van mo o tip hien tai. Khong co commit moi nao tu neo audit (main 81ea6e0, todolist-push 2ed0caf) bo sung bang chung Pick 1. Hieu chinh ve 714e4f9/84b88bb trong ban ghi la chinh xac, va toi tim them duoc 1 bang chung cung co no (xem muc 2.5).

## 2. Kiem tra tung gap

### 2.1 Gap 1: raw records P1/P2 chi o laptop, van mo, DUNG

Tu kiem tra lai:

- `git ls-tree -r` ca origin/todolist-push va origin/main: dung 5 file pick1, giong het ban ghi: improvements/pick1-p34fix-report.md, improvements/pick1-program-template.md, improvements/speed-proto-pick1-p34remeasure.md, improvements/speed-proto-pick1.md, improvements/summary-pick1-landing.md. Khong co file summary-pick1.md hay records.jsonl nao trong cay o ca 2 nhanh.
- `git log --all -- "**/summary-pick1.md"`: 0 commit. Dung.
- `git log --all -- "*pick1/records.jsonl" "*pick1-p34remeasure/records.jsonl" "*pick1/summary-pick1.md"`: 0 commit. Khong commit nao tren bat ky nhanh nao tung dua raw records Pick 1 vao repo.
- `git ls-tree -r` tren origin/speed-swarm: cung khong co raw records Pick 1.
- Tren VM clone1: /tmp/speed-profile-20261118/ khong ton tai, ~/workspace/speed-profile-20261118/ khong ton tai, `find ~/workspace -iname "*records.jsonl*"` khong thay file nao, `find /tmp -iname "*records.jsonl*"` khong thay file nao.
- Cac dong trich dan trong ban ghi deu dung so dong, tu kiem tra bang grep -n tren todolist-push:
  - improvements/live-test-log.md:3968: summary-pick1.md 8,264 B, records.jsonl 1,025 dong (vong 1).
  - Cung file :4016: rerun DONE, summary-pick1.md 10717B mtime 04:17, P1 18.89s, P2 10.18s, P3/P4 BLOCKED luc do.
  - Cung file :3484: 22 dong records fetch ve VM (~/workspace/speed-profile-20261118/records.jsonl). Ban sao nay gio khong con tren VM (xem muc tren).
  - improvements/speed-swarm-report.md:68: "Records.jsonl 398 lines, parses OK", nguon la laptop /tmp/speed-profile-20261118/pick1/summary-pick1.md.
- So lieu trich dan khop nhau giua cac file, nhung mean wall 37.54s xuong 17.59s va think 35.41s xuong 15.43s (swarm-report.md:15 va :127) khong tinh lai duoc tu repo vi khong co file goc.
- Ket luan gap 1: van thieu. Dung nhu ban ghi.

Hieu chinh nho ve cau chu trong ban ghi (khong doi verdict): ban ghi muc 2.1 viet "`git log --all` theo ten file summary-pick1.md va records.jsonl: 0 commit nao dua 2 file goc nay vao repo". Theo dung ten file, `git log --all -- "**/records.jsonl"` tra ve 1 commit d336d4b. Nhung commit nay chi them improvements/live-a2-20261120/records.jsonl (do A2 preflight live, 2026-11-20), khong phai records Pick 1, va no chi co tren remotes/origin/speed-swarm, khong phai ancestor cua tip todolist-push hay tip main. Nen cau trong ban ghi chi dung khi hieu la "2 file goc Pick 1", con doc theo nghia rong ten file thi thieu chinh xac. De nghi sua cau do thanh dang hep theo duong dan pick1 khi trich dan lai.

### 2.2 Gap 2: records P3/P4 21 dong chi o laptop, van mo, DUNG

Tu kiem tra lai, cac dong trich dan deu dung so dong:

- improvements/speed-proto-pick1-p34remeasure.md:4: run dir /tmp/speed-profile-20261118/pick1-p34remeasure/, records.jsonl 21 dong, parses OK, analyze-p34.py trong run dir.
- improvements/speed-swarm-report.md:103: trich lai y nhu vay.
- Cung file p34remeasure.md:19: file P4 /tmp/y-tuong.txt, 128 bytes, sha256 a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170.
- Cung file :46: "Test artifacts removed: /tmp/hoc-ky-2, /tmp/y-tuong.txt deleted after the run". Nghia la ngay ca tren laptop, hash P4 nay gio cung khong kiem tra lai duoc tu file goc.
- Khong commit nao tren bat ky nhanh nao dua records 21 dong nay vao repo (xem muc 2.1, log theo duong dan pick1-p34remeasure tra ve 0 commit).
- Ket luan gap 2: van thieu. Dung nhu ban ghi.

### 2.3 Gap 3: khong co lenh test verbatim, van mo, DUNG

Tu kiem tra lai:

- `git cat-file -e` scripts/timed.py that bai o ca 2 nhanh (exit 128, "path 'scripts/timed.py' does not exist"): tren origin/todolist-push va tren origin/main deu khong co scripts/timed.py. Dung nhu ban ghi.
- Da grep toan bo improvements/ tren todolist-push theo mau lenh chay timed.py (`python3 ... timed.py`, `./timed.py`). Khong co dong lenh chay day du nao cho vong rerun P1/P2 hay re-measure P3/P4. Chi co mo ta phuong phap:
  - improvements/speed-proto-pick1.md:54: "same timed.py wrapper, records.jsonl plus decisions.log in a fresh directory /tmp/speed-profile-20261118/pick1/ on the laptop".
  - Cung file :68: run dir chua records.jsonl, decisions.log, sleeps.log, codex2.log, measure-brief.md, timed.py, analyze.py, nhung khong co dong lenh goi.
  - improvements/speed-proto-pick1-p34remeasure.md:4: "timed.py and smoke envelope copied from /tmp/speed-profile-20261118/pick1/", cung chi la mo ta.
- 2 diem lien quan toi da kiem tra de tranh bo sot, ca 2 deu khong cuu duoc gap nay:
  - improvements/pick2-executor-brief.md:134 co mau `python3 __RUN_DIR__/timed.py --log __RUN_DIR__/records.jsonl <command>`, nhung do la mau chung trong brief Pick 2, co placeholder, khong phai lenh verbatim cua vong rerun Pick 1 hay re-measure P3/P4.
  - improvements/speed-swarm-report.md:378 chi ghi "timed.py call missing --log, retried correctly" nhu 1 ghi chu su co, khong phai dong lenh.
- Ket luan gap 3: van thieu. Dung nhu ban ghi.

### 2.4 Gap 4: verdict van la PROVISIONAL, khong doi thanh FINAL, DUNG

Tu kiem tra lai, tat ca dong trich dan deu dung so dong tren todolist-push:

- improvements/speed-swarm-report.md:5: "Status: FINAL, PROVISIONAL verdicts (non-Astra, Astra 6 out of credit)".
- Cung file :13: "What was measured in the reruns (19/11, all PROVISIONAL, non-Astra):".
- Cung file :15: "Verdict: SUCCESS (PROVISIONAL, non-Astra)" cho Pick 1.
- Cung file :127: "Verdict: SUCCESS (PROVISIONAL, non-Astra). Pick 1 BEAT baseline decisively...".
- Cung file :483: "## 8. Landing recommendation: PROVISIONAL (non-Astra, Astra 6 out of credit)".
- Cung file :485: "Status: FINAL report, PROVISIONAL verdicts."
- improvements/speed-proto-pick1-p34remeasure.md:8: "Verdict: PROVISIONAL (non-Astra, Astra 6 out of credit)."
- improvements/pick1-p34fix-report.md:5: "Verdict: PROVISIONAL (non-Astra)."
- Cung file :65: "This is mock evidence only... Verdict remains PROVISIONAL (non-Astra); do not report live success until that rerun completes."
- Khong commit nao tu neo audit sua cac dong verdict nay. Trong khoang 2ed0caf..759ce41 tren todolist-push chi co 292753f cham den file pick1, va chi la improvements/pick1-program-template.md (10 dong thay doi, xem muc 2.6), khong phai cac file verdict. Tren main, khoang 81ea6e0..f07da6b khong co commit nao cham den file pick1 hay file grounding (log loc theo cac duong dan do tra ve rong).
- Ket luan gap 4: van thieu dieu kien doi verdict sang FINAL. Dung nhu ban ghi.

### 2.5 Hieu chinh ve ancestry 714e4f9/84b88bb, DUNG, va co them bang chung cung co

Tu kiem tra lai bang merge-base:

- Ca 4 commit deu ton tai dang object: 714e4f9 "feat: add verified Pick 1 snippets registry", 84b88bb "fix: harden code execution envelopes", 2e2aeff "Merge a1-landing: A1 DOM code-exec generalization (Track 2, 19/11)", 453adc4 "Merge pick1-landing: Pick 1 code-exec + P3/P4 fixes (Track 2, 19/11)".
- 714e4f9 va 84b88bb KHONG phai ancestor cua tip todolist-push 759ce41 va KHONG phai ancestor cua tip main f07da6b. `git branch -a --contains` chi thay ca 2 tren remotes/origin/y1-snippets. Dung nhu ban ghi.
- 453adc4 la ancestor cua ca 2 tip. Parents cua no la 21684e7 va fa8ef95, dung nhu ban ghi. 2e2aeff cung la ancestor cua ca 2 tip.
- 5 commit Y1b 3f1b951, 17fdb9b, fd63a7d, 36364b1, 4ac9320 deu la ancestor cua tip todolist-push, khong phai ancestor cua tip main. Dung nhu ban ghi.
- scripts/code_exec.py co tren tip todolist-push, 1297 dong, blob 51c4c37dceae9ecddcf3657d0bc2e0c8fdb9ac1b. Dung nhu ban ghi.
- Bang chung them do council tim duoc: 714e4f9 them thu muc snippets/ (snippets/manifest.json, p1-disk-free.py, p2-percent-calc.py, p3-make-dirs.py, p4-write-ideas.py, tests/test_snippets.py, 644 dong them). Tren tip todolist-push, thu muc snippets/ hoan toan vang (so file goc snippets/ la 0), tests/test_snippets.py cung vang. Nghia la noi dung dac trung cua 714e4f9 chua tung land len todolist-push, khong chi la van de ancestry tren giay. scripts/codemode.py thi co tren tip (blob 1d65fd4), nen phan cung cua 84b88bb co the da den bang duong khac, nhung trich dan chinh 84b88bb lam bang chung code da land van sai ve ancestry.
- Ket luan: hieu chinh trong ban ghi la chinh xac. Khi trich dan lai code Pick 1 da land, dung merge 453adc4 va cac commit Y1b o tren, khong dung 714e4f9 va 84b88bb.

### 2.6 Kiem tra them muc 1 cua ban ghi, phan lien quan claim (a)

- Khoang todolist-push 2ed0caf..759ce41 dung 9 commit, dung thu tu va hash nhu ban ghi liet ke: 759ce41, e68e578, f1b85ee, 292753f, 4ae8ccc, 2d198c4, 6aa911b, a42ef12, d2da482.
- Trong 9 commit do, chi 292753f cham den file pick1, va chi improvements/pick1-program-template.md, 10 dong thay doi (10 +- trong stat). Khong commit nao cham den bang chung Pick 1.
- Tren main, khoang 81ea6e0..ed9b469 co 0 commit cham den file pick1 hay file grounding. Dung nhu ban ghi.

## 3. Cac diem ban ghi viet chua chat (khong doi verdict)

1. Cau ve `git log --all` o muc 2.1 (xem muc 2.1 o tren): tim theo ten file rong records.jsonl tra ve d336d4b, file A2 tren nhanh speed-swarm, khong phai records Pick 1. Nen viet hep theo duong dan pick1 khi trich dan lai.
2. Ngoai diem tren, tat ca so dong, hash, so lieu, va ket luan ancestry toi kiem tra lai deu khop. Khong phat hien sai so lieu nao khac trong muc 2 cua ban ghi.

## 4. Ket luan council 1

- Claim (a) S2 Pick 1 DONE: REVOKED STANDS, duoc xac nhan doc lap. Ca 4 gap deu van mo o tip hien tai (todolist-push 759ce41, main f07da6b).
- Hieu chinh ve 714e4f9/84b88bb la chinh xac, va duoc cung co them: thu muc snippets/ cua 714e4f9 vang mat tren tip todolist-push.
- Duong khoi phuc khong doi: commit raw records (summary-pick1.md, records.jsonl 398 dong vong rerun va 21 dong P3/P4) hoac chay lai P1-P4 tren laptop voi log va lenh chay commit trong repo, roi doi verdict sang FINAL. Chay lai la viec laptop-only vi can broker live tren laptop.
- Khong de nghi thay doi verdict cua claim (a). Khong co bang chung moi nao tu luc audit lam yeu di ket luan REVOKED STANDS.
