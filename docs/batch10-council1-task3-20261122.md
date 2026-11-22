# Council 1: kiem tra claim (a) S2 Pick 1 DONE, batch 10 task 3

- Vai tro: council 1, chi kiem tra claim (a) trong docs/batch10-task3-cb8-audit-20261122.md.
- Ngay kiem tra: 22/11/2026, khoang 11:16 den 11:25 +07.
- Neo kiem tra: origin/main 929a2042cccc791db4527ea3c09ccdeacb95b261, origin/todolist-push d2da4820cbc31adbad39c93670f30a01ff2c7709. Moi hon neo cua audit (81ea6e0, 2ed0caf). Tat ca cac fact duoi day deu do lai truc tiep o tip hien tai bang git cat-file, git show, git ls-tree, git grep, git merge-base. Chi doc, khong sua nhanh nao, khong commit, khong push.
- Khong sua coord/clone1.md, khong sua coord/clone2.md. Khong thong tin ca nhan. Khong dau gach ngang dai.

## Verdict: REVOKED STANDS

Ly do mot dong: raw records P1/P2 khong co trong repo, bao cao tu ghi PROVISIONAL, khong co lenh chay verbatim, nen claim (a) khong du chuan CB-8 de lam gate DONE.

## 1. Fact da kiem tra

### F1. Code da merge o 453adc4: DUNG

- Lenh: `git cat-file -t 714e4f9 84b88bb 2e2aeff 453adc4`, ket qua: ca 4 tra ve `commit`.
- Lenh: `git show -s --format='%H %P %s %ci' 453adc4`, ket qua: `453adc4228049300d5692983ea2a4b9835df37be`, message `Merge pick1-landing: Pick 1 code-exec + P3/P4 fixes (Track 2, 19/11)`, ngay `2026-11-19 17:30:25 +0700`.
- Lenh: `git merge-base --is-ancestor <commit> origin/todolist-push`, ket qua: ca 4 commit deu la ancestor cua tip todolist-push, YES.
- File `scripts/code_exec.py` co tren todolist-push, 1242 dong o tip hien tai.
- Luu y nho, xem muc 2a: so "880 dong" trong audit khong khop voi bat ky commit nao trong 4 commit.

### F2. P3/P4 co ban ghi chi tiet trong repo: DUNG

- File `improvements/speed-proto-pick1-p34remeasure.md` co tren todolist-push. Noi dung do duoc: P3/P4 2/2 SUCCESS, moi task tren retry, timeline 06:06 den 06:17 19/11, HEAD 2aa74ff, P4 file 128 bytes, sha256 `a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170`, records.jsonl 21 dong o laptop `/tmp/speed-profile-20261118/pick1-p34remeasure/`.
- File `improvements/pick1-p34fix-report.md` co tren todolist-push. Noi dung do duoc: unittest final run 32 passed, 0 failed, 10.274s, dong 65 ghi `This is mock evidence only` va `Verdict remains PROVISIONAL (non-Astra); do not report live success until that rerun completes`.
- File `improvements/pick1-program-template.md` co tren todolist-push.
- File `improvements/speed-swarm-report.md` tren todolist-push, dong 15 va 127 ghi `SUCCESS (PROVISIONAL, non-Astra)` voi mean wall 37.54s xuong 17.59s (-53%), think 35.41s xuong 15.43s (-56%), model calls 5 xuong 2 (P1/P2), 5 xuong 4 (P3), 5 xuong 3 (P4). Dong 487 ghi `Pick 1 (code execution): LAND` voi cung bo so. Khop voi trich dan cua audit.

### F3. Raw records P1/P2 chi o laptop, khong co trong repo: DUNG

- Lenh: `git ls-tree -r origin/todolist-push --name-only | awk -F/ '{print $NF}' | grep -xE 'summary-pick1\.md|records\.jsonl'`, ket qua: 0 dong, exit 1. Lam lai tren origin/main, ket qua giong het: 0 dong.
- Chi co file ten gan giong la `improvements/summary-pick1-landing.md`, day la file khac, khong phai ban summary goc o laptop.
- File `records.jsonl` duy nhat trong lich su repo la `improvements/live-a2-20261120/records.jsonl`, them o commit d336d4b, thuoc run A2 ngay 20/11, khong phai run Pick 1.
- So "398 dong" chi xuat hien nhu mot khang dinh ben trong `improvements/speed-swarm-report.md:68`: `Records.jsonl 398 lines, parses OK`, kem trich dan laptop `/tmp/speed-profile-20261118/pick1/summary-pick1.md`. Khong co file nao trong repo de kiem tra lai con so nay.
- V13 batch 7 UPHELD, da do lai o `docs/clone2-violation-verify-20261122.md:176-186` tren main: cung phat hien, goi la disclosed local-only evidence, khong phai bang chung giau. Audit ap dung dung V13 cho claim (a).

### F4. Verdict cua chinh bao cao la PROVISIONAL: DUNG

- `improvements/speed-swarm-report.md:5`: `Status: FINAL, PROVISIONAL verdicts (non-Astra, Astra 6 out of credit)`.
- Cung file dong 13: `all PROVISIONAL, non-Astra`. Dong 15 va 127: `Verdict: SUCCESS (PROVISIONAL, non-Astra)`. Dong 483: `Landing recommendation: PROVISIONAL (non-Astra, Astra 6 out of credit)`.
- `improvements/pick1-p34fix-report.md:65`: `Verdict remains PROVISIONAL (non-Astra)`.
- Khong co cho nao trong hai bao cao doi verdict thanh FINAL.

### F5. Khong co lenh chay verbatim cho vong rerun P1/P2: DUNG

- Lenh: `git show origin/todolist-push:improvements/speed-swarm-report.md | grep -n -iE 'timed\.py|python3? [a-z]|records\.jsonl'`, ket qua: cac dong chi mo ta (`same timed.py wrapper`, duong dan laptop, `Records.jsonl 398 lines`), khong co dong lenh khoi chay day du nao.
- Lenh tuong tu tren `improvements/speed-proto-pick1.md`: chi co mo ta phuong phap va duong dan laptop `/tmp/speed-profile-20261118/pick1/`, khong co lenh chay.
- Dong 68 cua speed-swarm-report mo ta vong rerun (19/11 04:00 den 04:17, HEAD e50da19, smoke ok:true, windows 4, api_calls 1, elapsed 2.39 ms), nhung khong ghi lenh `codex exec` hay lenh goi timed.py voi tham so. Nguoi doc khong the chay lai y het tu repo.

### F6. Y1b 1e/2a/2b da sua sau probe-s2, re-probe 19/22 PASS: DUNG, voi mot sua nho o muc 2b

- Council 9d9bd63, message: `Y1b verdict council 3: OVERALL Phase A BLOCK on 84b88bb (14/20, 3 real fails, 2 probe artifacts)`. Noi dung do duoc: 1e codemode f-string `NameError: name 'chr' is not defined`, 2a wall preemption (elapsed 7.20s, loi chi xuat hien sau khi vong C ket thuc), 2b silent success (elapsed 6.20s, ok=True, khong loi).
- Probe-s2 a1a672d, message: `probe-s2: fixture 2-vision bench PASS 10.86s, Y1b 3 fails still open, flag NOT flipped (gate b unmet)`, ngay 2026-11-21 23:41:27 UTC. Log bat dau 06:36 +07, muc kiem tra Y1b o 06:37 +07, ket luan `the 3 Y1b real fails 1e/2a/2b are STILL OPEN`. Nhan xet "3 fails still open" chi dung o thoi diem probe, audit noi dung la no da loi thoi o tip hien tai.
- Fix commit, deu la ancestor cua tip todolist-push:
  - 3f1b951, 2026-11-22 00:05:52 UTC: `Y1b fix 1e: add chr and ord to SAFE_BUILTINS in both executors`.
  - 17fdb9b, 2026-11-22 00:14:20 UTC: `Y1b fix 2a/2b: run snippets in a forked child, parent kills at the wall`.
  - fd63a7d, 2026-11-22 00:54:40 UTC: `Y1b fix 2a/2b (RPC): API calls run in the parent, snippet in a forked child`.
- Re-probe trong `improvements/worker-y1b-fix-log.md`, do duoc: `Full probe run 07:13: 19/22 PASS`, `Probes 2a/2b pass twice in a row: 2.02-2.10s, wall-clock error envelopes, no silent success`, `Probe 1e passes all four halves`, `Full probe run under the RPC code: 19/22 PASS, fails only 2e, 4a, 4b`.
- Han che audit neu dung: probe runner `/tmp/y1b-fix-probes.py` la file local, tim tren ca hai nhanh deu 0 ket qua, khong co trong repo. Log fix thi co trong repo.

## 2. Hai diem audit ghi chua chinh xac, khong doi verdict

### 2a. So dong code_exec.py "880 dong" khong khop commit nao

- Audit muc 2.1 (trich direction log) ghi `code_exec.py 880 dong`.
- Do truc tiep: 714e4f9 la 1436 dong, 84b88bb la 910 dong, 2e2aeff la 868 dong, 453adc4 la 556 dong.
- Dong `880 lines` co that trong hang S2+D5 cua `improvements/worker-click3-final-direction-log.md`, audit chi lap lai so cua log ma khong do lai. Gan nhat la 868 dong o 2e2aeff, lech 12 dong. O chinh merge 453adc4 file chi 556 dong.
- Anh huong: khong co. Day la so mo ta, code co that va da merge la fact chinh, da dung o F1. Chi can sua so dong khi trich dan lai.

### 2b. Con so "80/81 o fd63a7d" khong phai mot lan chay do duoc

- Audit muc 2.4 ghi `Unit tests: 80/81 o fd63a7d (1 failure la codemode pin test, de mo)`.
- Trong `improvements/worker-y1b-fix-log.md` khong co chuoi `80/81` nao. Log ghi: `The 66 non-tempfile tests pass`, 14 file-gated tests `still need one open-gate run`, pin test de mo cho parent quyet dinh, test file khong sua.
- So 80/81 la phep cong suy dien cua auditor (66 + 14), gia dinh 14 test file-gated se pass, khong phai mot lan chay do duoc o fd63a7d.
- Lan chay 81/81 do duoc co that, nhung o commit sau: closeout 4ac9320 ghi `Ran 81 tests in 14.757s, OK (test_code_exec 55, test_codemode 26)` o 36364b1, lenh `PYTHONPATH=../scripts:. python3 -m unittest test_code_exec test_codemode`, dong thoi ghi Y1b 8-issue status GONE o 36364b1.
- Cach ghi dung: o fd63a7d la 66 do duoc pass + 14 chua chay + 1 mo, va 81/81 do duoc o 36364b1. Ket luan "Y1b da sua" van dung, chi con so gan voi fd63a7d la sai. Khong doi verdict vi re-probe 19/22 PASS va 81/81 o 36364b1 la bang chung do that.

## 3. Ap dung luat CB-8: DUNG

- Luat, doc tu hang CB-8 trong `improvements/worker-click3-final-direction-log.md` tren todolist-push: DONE la trang thai cua bang chung cu the, khong phai trang thai chung cua tinh nang. Rang buoc: `any proposal whose DONE basis is a fixture-only proof gets its DONE revoked until live evidence exists`. Pham vi: chi ap dung cho cac DONE lam gate cho huong di hien tai (`S2's Pick 1 DONE, the bench DONE, the DOM-grounding DONE claims`), khong audit lai toan bo lich su.
- Claim (a) thuoc dung pham vi: hang S2+D5 ghi Pick 1 la winner va de nghi LAND, speed-swarm-report dong 487 ghi LAND. Day la gate DONE.
- Ba thieu sot o F3, F4, F5 trung khop voi ba yeu to CB-8 doi hoi (lenh test, output, commit hash, time log): raw records P1/P2 khong co trong repo nen khong tinh lai duoc, khong co lenh chay verbatim, verdict cua chinh bao cao chi la PROVISIONAL.
- Cac diem giam nhe audit neu (code da merge, P3/P4 chi tiet, Y1b da sua, re-probe 19/22) deu co that, da do lai o F1, F2, F6, nhung chung khong bu duoc ba thieu sot tren, vi chung khong phai raw records hay lenh chay cua vong rerun P1/P2. P3/P4 cung chi co bao cao tom tat trong repo, records.jsonl 21 dong cua no cung chi o laptop.
- UPHELD se doi hoi raw records trong repo hoac mot lan rerun co log commit, hien khong co. PROVISIONAL la nhan cua chinh bao cao, khong phai verdict gate theo CB-8, va luat buoc thu hoi gate DONE cho den khi co bang chung kiem tra duoc tu repo. Vi vay REVOKED la verdict dung, voi pham vi audit da ghi ro: thu hoi voi tu cach bang chung proof-grade lam gate, khong phai phu nhan ket qua do.
- Duong khoi phuc audit de ra la dung va kha thi: commit raw records (summary-pick1.md, records.jsonl) hoac chay lai P1-P4 voi log va lenh chay commit trong repo, roi doi verdict thanh FINAL.

## 4. Ket luan

- REVOKED STANDS cho claim (a).
- Tat ca 6 fact chinh cua audit ve claim (a) deu dung khi do lai tu repo: code merge, P3/P4 chi tiet, P1/P2 raw records vang mat, verdict PROVISIONAL, khong lenh chay verbatim, Y1b da sua va re-probe 19/22.
- Hai sua nho can ghi vao ban audit truoc khi dung lam co so quyet dinh: so dong code_exec.py (muc 2a) va con so 80/81 gan voi fd63a7d (muc 2b). Ca hai deu khong doi verdict.
- Khong dung claim (a) lam gate cho rung 2 live cho den khi duong khoi phuc o muc 3 xong.
