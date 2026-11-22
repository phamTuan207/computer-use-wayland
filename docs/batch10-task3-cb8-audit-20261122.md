# Audit CB-8: 3 claim DONE lam gate, batch 10 task 3

Ngay kiem tra: 22/11/2026, bat dau 11:04 +07.
Nguoi audit: subagent batch 10 task 3.
Neo kiem tra: origin/main 81ea6e009ec0111edb3f1561a85a45529a329180 (2026-11-22 04:08 UTC), origin/todolist-push 2ed0caf1509ff9b6cb54da12b43f8ce7085e05b6 (2026-11-22 04:01 UTC).
Hieu chinh: gio neo main sua 04:05 thanh 04:08 UTC theo git log -1 81ea6e0 (04:08:01 UTC); gio bat dau audit 11:04 +07 (04:04 UTC) som hon commit neo 4 phut. Audit da qua council 3 nguoi va redteam ngay 22/11/2026, ca 3 verdict giu nguyen; cac sua nho ghi trong docs/batch10-fix-task3-20261122.md.
Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. Khong chay lai bench nao. Khong thong tin ca nhan. Khong dau gach ngang dai.

## 0. Luat ap dung va pham vi

Luat CB-8 (improvements/worker-click3-final-direction-log.md:251, tren todolist-push): DONE la trang thai cua mot bang chung cu the, khong phai trang thai chung cua tinh nang. Moi DONE phai neu ro bang chung (lenh test, output, commit hash, time log). Rang buoc cua luat: DONE nao chi dua tren fixture thi bi thu hoi cho den khi co bang chung live. Pham vi audit chi 3 claim lam gate cho huong di hien tai, khong audit lai toan bo lich su.

Phuong phap: doc chi doc tren git (git show, git cat-file, git ls-tree, git grep, git log, git merge-base), khong sua nhanh nao, khong chay script trong repo. Moi so duoi day deu kiem tra lai truc tiep o tip neu tren, khong tin so cua nguoi khac.

Lien he voi batch 7: clone2-violation-verify-20261122.md (ebf6ec8) upheld 13/13 violation. Trong do V13 bao phu truc tiep claim (a) duoi day, va V4, V7, V8 dat chuan "log chi o local thi khong du de kiem tra lai tu repo", chuan nay duoc ap dung cho (a) va (c). Khong co violation nao trong 13 cai bao phu truc tiep (b) bench 2-vision hay (c) DOM-grounding, nen (b) va (c) la kiem tra moi o day. Clone1-batch7-high-fixes-verify-20261122.md xac nhan V1, V2, V3 PARTIALLY FIXED, khong lien quan 3 claim nay.

Chu y: audit nay da qua council 3 nguoi va redteam theo quy tac batch 10 ngay 22/11/2026. Ca 3 verdict giu nguyen; cac sua nho ap dung trong ban nay, xem docs/batch10-fix-task3-20261122.md.

## 1. Ket qua tong ket

| Claim | Verdict |
|---|---|
| (a) S2 Pick 1 DONE | REVOKED |
| (b) bench 2-vision DONE | UPHELD, chi tren trich dan run moi, xem muc 3 |
| (c) DOM-grounding DONE | REVOKED |

## 2. Claim (a): S2 Pick 1 DONE, verdict REVOKED

### 2.1 Ban ghi cua claim

- improvements/speed-swarm-report.md:15, :127, :487 (tren todolist-push): Pick 1 4/4 SUCCESS sau P3/P4 re-measure, mean wall 37.54s xuong 17.59s (-53%), think 35.41s xuong 15.43s (-56%), model calls 5 xuong 2 (P1/P2), 5 xuong 4 (P3), 5 xuong 3 (P4). Verdict ghi trong bao cao: SUCCESS (PROVISIONAL, non-Astra), landable.
- improvements/worker-click3-final-direction-log.md:228 (S2 + D5): code da build va merge (code_exec.py 880 dong theo log, Pick 1 winner, commits 714e4f9, 84b88bb, 2e2aeff, merge 453adc4), flag OFF tren live path, flip bi BLOCKED (B2). Hieu chinh so dong: do lai bang git show, file la 1436 dong o 714e4f9, 910 dong o 84b88bb, 868 dong o 2e2aeff, 556 dong o merge 453adc4; so 880 khong khop commit nao trong 4 commit trich dan, no khop tai e05fc58, commit ghi chinh direction log (880 dong).

### 2.2 Bang chung co trong repo

- 4 commit neu tren deu ton tai, da kiem tra bang git cat-file: 714e4f9, 84b88bb, 2e2aeff, 453adc4. File scripts/code_exec.py co tren todolist-push.
- improvements/speed-proto-pick1-p34remeasure.md co trong repo, ghi chi tiet: P3/P4 2/2 SUCCESS (moi task tren retry), timeline 06:06 den 06:17 19/11, HEAD 2aa74ff, P4 file 128 bytes, sha256 a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170, relay da ve clean env.
- improvements/pick1-p34fix-report.md co trong repo: mock tests 32 passed, final run 10.274s, nhung tu ghi ro "This is mock evidence only" va "Verdict remains PROVISIONAL (non-Astra); do not report live success until that rerun completes".
- improvements/pick1-program-template.md co trong repo.

### 2.3 Bang chung thieu

- Raw records cua vong rerun P1/P2 khong co trong repo. Hai file goc duoc trich dan la laptop /tmp/speed-profile-20261118/pick1/summary-pick1.md va records.jsonl (398 dong). Tim theo ten file tren toan nhanh todolist-push: 0 ket qua. File improvements/summary-pick1-landing.md co trong repo la file khac, khong phai summary goc. Day chinh la V13 cua batch 7, da UPHELD, va van dung o tip hien tai.
- Records cua P3/P4 re-measure (records.jsonl 21 dong) cung chi o laptop /tmp/speed-profile-20261118/pick1-p34remeasure/, khong co trong repo. Ban ghi trong repo chi la bao cao tom tat, khong phai log tho.
- Khong co lenh test verbatim cho vong rerun trong repo. Bao cao chi neu ten wrapper (timed.py) va co che relay drop-in, khong ghi lenh chay day du.
- Verdict cua chinh bao cao la PROVISIONAL, khong phai FINAL.

### 2.4 Diem can sua: Y1b 3 fails that da duoc sua sau probe-s2

- Verdict council 3 commit 9d9bd63: Phase A BLOCK tren 84b88bb, 14/20 PASS, 3 real fails (1e chr NameError, 2a/2b wall preemption, 2b silent ok=True).
- Probe-s2 (a1a672d, 06:37 +07 22/11) ghi "3 fails still open". Nhan xet nay chi dung o thoi diem probe, da loi thoi o tip hien tai.
- Fix da land, deu la ancestor cua tip: 3f1b951 (1e: them chr va ord vao SAFE_BUILTINS, 2026-11-22 00:05 UTC), 17fdb9b va fd63a7d (2a/2b: chay snippet trong forked child, parent kill o wall, RPC rework, 2026-11-22 00:14 va 00:54 UTC).
- Re-probe ghi trong improvements/worker-y1b-fix-log.md: full probe run 19/22 PASS, 2a/2b pass 2 lan lien tiep o 2.02-2.10s voi wall-clock error envelope, khong silent success, 1e pass ca 4 halves. Chi fail 2e (allowed exception) va 4a/4b (probe artifacts, primes pass). Unit tests: 80/81 o fd63a7d, do duoc tren cay da land, ghi trong improvements/worker-y1b-rpc-land-log.md:123 ("Tests on the landed tree: 80/81 pass, 1 failure (the known-open codemode pin test), 0 errors"), sau do closeout 4ac9320 ghi 81/81 OK o 36364b1 (Ran 81 tests in 14.757s, test_code_exec 55, test_codemode 26). So 66 + 14 trong fix-log la trang thai truoc khi land (HEAD 5dcf2b3): 66 non-tempfile pass + 14 file-gated = 80 pass, cong 1 pin test fail = 81, khop dung so 80/81 do duoc, khong phai phep cong suy dien.
- Han che con lai: probe runner (/tmp/y1b-fix-probes.py) la file local, khong co trong repo. Log fix thi co trong repo.

### 2.5 Ket luan (a)

REVOKED, voi tu cach bang chung proof-grade lam gate. Ly do: (1) raw records P1/P2 chi o laptop, khong the tinh lai so tu repo; (2) verdict cua chinh bao cao la PROVISIONAL; (3) khong co lenh chay verbatim trong repo. Diem giam nhe: P3/P4 co ban ghi chi tiet trong repo, code da merge, Y1b 1e/2a/2b da sua va re-probe 19/22, nen viec khoi phuc la re. De khoi phuc: commit raw records (summary-pick1.md, records.jsonl) hoac chay lai P1-P4 voi log va lenh chay commit trong repo, roi doi verdict thanh FINAL thay vi PROVISIONAL.

## 3. Claim (b): bench 2-vision DONE, verdict UPHELD (chi tren run moi)

### 3.1 Ban ghi cua claim

- improvements/worker-click3-final-direction-log.md step 3 va section 4 rung 1: "Fixture 2-vision bench: DONE. Bench PASSED (a1a672d, 10.86s, visions_used 2, both sends V12 gated, V-Z5)", kem dieu kien "pending manifest lock" va "must not be quoted as a gate until its manifest is locked".
- docs/layer0-cbexec-contract.md:667: "Rung 1, fixture 2-vision benchmark: PASSED (a1a672d, 10.86s, visions_used 2, both sends V12 gated), pending manifest lock".

### 3.2 Run a1a672d: du 4 yeu to CB-8 cho fixture pass, nhung khong duoc trich lam gate

- Commit a1a672d ton tai (2026-11-21 23:41:27 UTC), chi 1 file improvements/worker-probe-s2-log.md (199 dong).
- Log co day du: lenh chay (venv python tests/two_vision_bench.py --fixture --mode run, workdir va out ghi ro), attempt 1 FAILED vi het disk (/tmp 100%, OSError Errno 28), attempt 2 06:40:30-06:40:41 +07 EXIT 0, wall 10.8596s, run_id bench-20261121T234030Z-86e8d8, visions_used 2, outcome PASS, ca 2 sends V12 gated (0.6904s va 0.6807s).
- Bench code va fixture da co tren todolist-push o c5311ce va 7f3a70b, blob 80b00469 (868 dong) va bac2702e (48 dong).
- Nhung: results.json (733 bytes theo closeout 4ac9320) chi o VM-local, khong co trong repo, va den luc sua audit thi file nay da mat o local (/home/hatch/probe-s2-work/results.json khong con), nen khong the kiem tra lai con so 733 bytes tu file goc. Va quyet dinh: khong co manifest. Closeout 4ac9320 section 5 ket luan manifest NOT locked, "A retroactive manifest cannot be manufactured", pass "must not be quoted as a gate". Nhan xet cua Codex ("khong co log fixture 2-vision pass") va FCC ("benchmark absent") da loi thoi sau khi bench duoc dem len todolist-push o c5311ce/7f3a70b, truoc run a1a672d.

### 3.3 Run moi d7d569b: co manifest, quotable

- improvements/worker-click4-bench-manifest-log.md, commit 5f86046 (2026-11-22 02:08 UTC), la ancestor cua tip todolist-push, khong phai cua tip main (git merge-base --is-ancestor 5f86046 origin/main tra ve khong). deploy-manifest.json co o tip todolist-push, khong co tren origin/main (git cat-file -e origin/main:deploy-manifest.json bao loi file khong ton tai): source_commit d7d569be5c9f88986abdd8416143c64981667986, source_content_sha256 92891523266e1af568e14bdcb65319ee39a2a6ab2fcce9e5fa1c8d4e1966c607, run_id bench-20261122T020225Z-3d9270, wall 12.6852s, visions_used 2, outcome PASS, ca 2 sends V12 gated (0.6088s va 0.3867s).
- Verify chay exit 0, tat ca check ok (ghi verbatim trong log section 6): commit, content digest, clean tree, bench script va fixture theo hash va blob, ca 3 runtime binaries, log neu dung run_id, results khop run_id va outcome. Mechanism tests 4/4 PASS.
- Manifest log noi ro: run quotable la run moi, khong phai a1a672d. Bench code byte-identical giua 2 run, chi tren ban sao todolist-push (blob 80b00469 o ca a1a672d, d7d569b va neo 2ed0caf); blob bench tren main da doi thanh e5681192 o tip hien tai, nen tinh byte-identical khong ap dung cho ban tren main.
- Han che con lai: results.json cua run moi da mat o local (/tmp/click4-bench-workdir/results.json va ca thu muc /tmp/click4-bench-workdir, /tmp/click4-bench-manifest deu khong con), nen lenh verify o muc 6 cua manifest log khong the chay lai y nhu cu, vi no can results.json. Bang chung quotable con lai la manifest da commit cong output verify verbatim da commit trong manifest log (da ghi ok results:run_id_outcome luc verify) va hash sha256 cua results.json (84f43d67f2ddfde3162e1187418539da6e24ba86d7c6febcd6de7a70a9e44ad9) ghi trong manifest log. Nhung manifest trong repo da pin build, hash, outcome, va lenh verify da chay exit 0.

### 3.4 Ket luan (b)

UPHELD, chi tren trich dan run moi: bench 2-vision DONE o run_id bench-20261122T020225Z-3d9270, build d7d569b, manifest commit 5f86046 (tren todolist-push, khong phai main). Trich dan a1a672d nhu mot gate bi thu hoi, vi run do khong co manifest va khong bao gio co duoc. Can sua ngay: final-direction step 3 va rung 1, cung layer0-cbexec-contract.md:667, phai doi trich dan sang run_id moi. Them cac vi tri cung trich gate a1a672d va cung can doi: final-direction dong 207 (hang A10, rung 1, "pending the CB-9 manifest before it is quoted as a gate"), dong 228 (dieu kien gate (a), "MET (a1a672d, 10.86s, V-Z5)"), dong 535-536 (precondition, "not quoted as a gate until its manifest is locked"), dong 687 (dieu kien mo B2, "fixture bench green (MET, a1a672d)"), va docs/layer0-cbexec-contract.md dong 629 (hang CB-9, cung cau "not quoted as a gate"). Cac dong ke chuyen lich su (39, 104, 149, 339, 399, 541, 889, 1016, 1036) mo ta dung run cu, giu nguyen. Day la sua trich dan, khong phai chay lai bench.

## 4. Claim (c): DOM-grounding DONE, verdict REVOKED

### 4.1 Ban ghi cua claim

- improvements/worker-click3-final-direction-log.md settled base: "DOM grounding is single-source (clone2 batch 7: 66 rects, Marionette median 0.030s; C1 applies)".
- docs/zen-error-fix-todolist-20261121.md:47 (1.2.2) DONE: "DOM read 3-14ms vs observe vai giay; DOM locate chinh xac tuyet doi (vision 58.6%); DOM click KHONG bang chuot that".
- Cung file :60 (2.1.2) DONE 21/11 05:30 E2 live: "DOM rects chinh xac tuyet doi, vision 58.6% (17/29), pointer <1px".

### 4.2 Bang chung co trong repo

- docs/clone2-dom-grounding-20261122.md (401 dong, tren main), tests/dom_grounding_bench.py (commits 79b75e7, 47d5ee6 tren main), tests/dom_grounding_fixture.html (79b75e7). So lieu: one-shot 66 rects, Marionette pooled median 0.030s (9 samples, 3 runs), BiDi run medians 0.006-0.054s, agreement BiDi vs Marionette toi da 5.7e-14 px, 5 pointer clicks deu trung trong 3 runs cua click step, verify bang 1 lan doc DOM 0.002-0.015s. Run 2 va run 3 full (14.35s, 12.74s), run 4 va run 5 fix-pass (16.15s, 15.57s), walls UTC ghi ro.
- Council va redteam da review va buoc sua so sai (BiDi session.new, "three full runs", so a11y), theo coord/clone2.md:687. Dong 687 la dong Task 2 trong khoi bao cao Batch 7 (tieu de khoi o dong 682), da kiem tra lai o neo 81ea6e0: dong nay ghi dung noi dung review, trich dan dung. Bao cao da sua va ghi ro phan sua. Ghi chu nho: coord ghi bao cao 402 dong va verify 0.005-0.015s, trong khi file that la 401 dong va 0.002-0.015s; audit ghi dung theo file.
- Corroboration doc lap: docs/clone2-dom-bench-2win-20261122.md (batch 8 task 2), cung fixture, 2 windows: pooled median 0.0112s, 5/5 clicks ca 2 windows ca 2 runs sau fix, ground_many vs one-shot 0.0 px. Run 1 loi stale-rect duoc tiet lo trong chinh bao cao nay (dong 36-39, 93, 267-269): chi 2 of 5 clicks landed o ca 2 windows, all_five_landed false, mechanism UNKNOWN; 2 click "moved" va "scroll-btn" roi len #tall spacer o toa do stale (clicked log "btn-3;btn-17;btn-42;tall;tall;"). Fix re-read rect truoc moi click, sau do 5/5 o ca 2 windows ca 2 runs. Tom tat cu bo qua failure nay; ket qua cuoi khong doi, nhung corroboration yeu hon so voi tom tat cu.
- Phan E2 live co trong repo tren todolist-push: docs/calibration-e2-report.md va tests/calibration-e2-hits.jsonl (87 dong). Dem lai tu file: e2-vision 17 hit true, 12 false, tuc 17/29 = 58.6%, khop voi claim. Phan nay dung.

### 4.3 Bang chung thieu

- Bench va fixture KHONG co tren todolist-push. git cat-file fail ca 3 file: tests/dom_grounding_bench.py, tests/dom_grounding_fixture.html, tests/dom_bench_2win.py. Nhanh direction khong chua cong cu chung minh claim cua chinh no.
- Raw JSONL logs (/tmp/dom_grounding_run1-5.log) chi o VM clone2, khong co trong repo. Khong the tinh lai median 0.030s tu repo. Day la cung chuan nhu V4, V7, V8 cua batch 7.
- Chinh bao cao muc 9 ghi UNVERIFIED (muc 8 la khuyen nghi chay lai, khong mang nhan UNVERIFIED): real Zen, live pages, headed runs. Tat ca so la Firefox 160.0.1 headless tren fixture tinh local. Claim lam gate cho live Zen va Messenger vuot qua pham vi bang chung ma bao cao tu thua nhan.
- Todolist 1.2.2 tu thua nhan "DOM click KHONG bang chuot that". DOM click khong phai input that, nen DONE nay khong bao phu duong input that.
- Log cua bench 2-window cung chi o /tmp, khong co trong repo, nen corroboration cung khong kiem tra lai duoc tu repo.

### 4.4 Ket luan (c)

REVOKED, voi pham vi ro rang. So fixture (66 rects, median 0.030s) la so do that, co corroboration doc lap cung huong, va phan E2 live (17/29, DOM rects exact) trong repo thi dung. Nhung chung khong du chuan CB-8 de lam gate DONE cho huong live: log tho khong co trong repo, bench khong co tren todolist-push, Zen that va live pages chua do. De khoi phuc: commit raw logs hoac chay lai bench voi log commit trong repo, dua bench len todolist-push, chay tren Zen that va live page, roi ghi lai pham vi claim theo dung nhung gi da do.

## 5. Viec can lam tiep theo

1. Sua trich dan bench (muc 3.4): doi a1a672d sang run_id bench-20261122T020225Z-3d9270, build d7d569b, manifest commit 5f86046, o final-direction (step 3, rung 1, dong 207, 228, 535-536, 687) va docs/layer0-cbexec-contract.md (dong 629, 667).
2. Khoi phuc (a): commit raw records Pick 1 hoac chay lai P1-P4 voi log trong repo, roi doi verdict sang FINAL.
3. Khoi phuc (c): commit raw logs grounding, dua bench len todolist-push, chay tren Zen that va live page.
4. Audit nay da qua council 3 nguoi va redteam ngay 22/11/2026, ca 3 verdict giu nguyen; khong can soat lai them truoc khi dung lam co so quyet dinh.
5. Khong dung 3 claim nay lam gate cho rung 2 live cho den khi muc 1, 2, 3 xong, tru (b) tren trich dan run moi.
6. Van de mo cho dieu phoi, xem docs/batch10-fix-task3-20261122.md: blob bench tren main da doi (e5681192) so voi ban todolist-push (80b00469); verify muc 6 cua manifest log khong chay lai duoc vi results.json cua ca 2 run da mat o local; ke hoach khoi phuc chua ghi ai chay lai cac run live, trong khi live run phai chay phia laptop.
