# Redteam batch 10 task 3: tan cong audit CB-8 3 claim DONE

Ngay kiem tra: 22/11/2026, 11:16 den 11:30 +07.
Nguoi redteam: subagent batch 10 redteam task 3.
Doi tuong: docs/batch10-task3-cb8-audit-20261122.md (117 dong, chua commit, o working tree).
Neo kiem tra cua audit: origin/main 81ea6e0, origin/todolist-push 2ed0caf.
Kiem tra lai: doc chi doc tren git o ca hai neo tren, cong them tip origin/todolist-push d2da482 cho cac fact nhay cam theo nhanh. Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. Khong chay lai bench nao. Khong thong tin ca nhan. Khong dau gach ngang dai.

## 0. Ket qua tong ket

| Claim | Verdict cua audit | Redteam |
|---|---|---|
| (a) S2 Pick 1 DONE | REVOKED | SURVIVES |
| (b) bench 2-vision DONE | UPHELD, chi tren run moi | SURVIVES |
| (c) DOM-grounding DONE | REVOKED | SURVIVES |

Khong co verdict nao bi pha vo. Cac loi tim duoc chi la loi nho ve gio, trich dan, va dien dat, xem muc 4. Cac thieu sot ve bang chung phu xem muc 5.

## 1. Claim (a): S2 Pick 1 DONE, REVOKED, SURVIVES

### Tan cong A1: raw records P1/P2 co trong repo duoi ten khac?
Lenh: `git ls-tree -r --name-only 2ed0caf | grep -i "pick1\|records.jsonl\|summary-pick1"`.
Ket qua: chi co 5 file bao cao (pick1-p34fix-report.md, pick1-program-template.md, speed-proto-pick1-p34remeasure.md, speed-proto-pick1.md, summary-pick1-landing.md). Khong co file nao ten records.jsonl hay summary-pick1.md. File summary-pick1-landing.md la file khac, khong phai summary goc.
Ket luan: tan cong that bai. Audit dung, V13 dung.

### Tan cong A2: bao cao P3/P4 trong repo du de giu DONE?
Kiem tra: improvements/speed-proto-pick1-p34remeasure.md dong 4 ghi records.jsonl 21 dong, dong 19 ghi P4 file 128 bytes va sha256 a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170, dong 48 ghi timeline 06:06 den khoang 06:17 ngay 19/11, header ghi HEAD 2aa74ff va relay da ve clean env.
Nhung so headline 37.54s xuong 17.59s va 35.41s xuong 15.43s la trung binh P1-P4, ma P1/P2 chi co trong summary goc o laptop. P3/P4 chi tiet khong bao phu duoc phan P1/P2 cua trung binh.
Ket luan: tan cong that bai doi voi DONE tong 4/4. Audit co the tach verdict P3/P4 rieng, nhung verdict REVOKED doi voi DONE tong van dung.

### Tan cong A3: verdict that ra la FINAL chu khong phai PROVISIONAL?
Kiem tra: improvements/speed-swarm-report.md dong 5 ghi "Status: FINAL, PROVISIONAL verdicts", dong 13 ghi "all PROVISIONAL, non-Astra", dong 15 va 127 ghi "SUCCESS (PROVISIONAL, non-Astra)", dong 485 ghi "Status: FINAL report, PROVISIONAL verdicts".
Ket luan: tan cong that bai. Audit dung, verdict la PROVISIONAL.

### Tan cong A4: co lenh test verbatim cho vong rerun trong repo?
Kiem tra: improvements/speed-proto-pick1.md dong 54 va 68 chi neu ten wrapper timed.py, thu muc chay, va ten file, khong co dong lenh chay day du. File p34remeasure cung chi neu timed.py duoc copy va analyze-p34.py tai tao so, ma ca hai file deu o laptop, khong co trong repo.
Ket luan: tan cong that bai. Audit dung.

### Tan cong A5: so Y1b 19/22, 80/81, 81/81 la so bia?
Kiem tra: improvements/worker-y1b-fix-log.md dong 82-83 ghi 2a/2b pass 2 lan lien tiep o 2.02-2.10s, dong 120 ghi full probe 19/22 PASS, chi fail 2e, 4a, 4b. Dong 54-56 ghi 2e allowed exception va 4a/4b probe artifacts voi 4a-prime/4b-prime passing. Dong 65 ghi 1e pass ca 4 halves.
So 80/81: improvements/worker-y1b-rpc-land-log.md:123 ghi "80/81 pass, 1 failure (the known-open codemode pin test), 0 errors" tren cay da land fd63a7d.
So 81/81: improvements/worker-click4-step1-closeout-log.md (4ac9320) ghi "Ran 81 tests in 14.757s, OK (test_code_exec 55, test_codemode 26)" o 36364b1.
Ket luan: tan cong that bai. Tat ca so deu co that trong repo. Chi thieu sot nho: audit khong neu ten file rpc-land-log cho so 80/81.

### Tan cong A6: code_exec.py 880 dong la so sai?
Kiem tra: `git show e05fc58:scripts/code_exec.py | wc -l` tra ve 880. Commit e05fc58 la commit ghi improvements/worker-click3-final-direction-log.md. O merge 453adc4 file chi 556 dong, o neo 2ed0caf file 1242 dong, nhung con so 880 khop dung tai commit cua direction log.
Ket luan: tan cong that bai. Audit trich dung.

### Tan cong A7: CB-8 bi ap dung sai, vi Pick 1 la bang chung live chu khong phai fixture?
Kiem tra: luat CB-8 o improvements/worker-click3-final-direction-log.md:251 ghi "DONE is a state of specific evidence" va rang buoc "any proposal whose DONE basis is a fixture-only proof gets its DONE revoked until live evidence exists". Pick 1 chay live that, nhung raw records chi o laptop nen khong tinh lai duoc tu repo. Audit ap dung them chuan V4/V7/V8 cua batch 7, "log chi o local thi khong du de kiem tra lai tu repo", va gioi han REVOKED o dang "bang chung proof-grade lam gate", khong phu nhan cac run da xay ra.
Ket luan: tan cong that bai. Cach ap dung co co so ro rang va duoc gioi han pham vi.

### Tan cong A8: "3 fails still open" cua probe-s2 da loi thoi nen audit sai?
Kiem tra: audit muc 2.4 tu ghi ro nhan xet nay chi dung o thoi diem probe. Fix da land va la ancestor cua tip: 3f1b951 (2026-11-22 00:05:52 UTC), 17fdb9b (00:14:20 UTC), fd63a7d (00:54:40 UTC). Council 3 commit 9d9bd63 ghi BLOCK tren 84b88bb, 14/20 PASS, 3 real fails.
Ket luan: tan cong that bai. Audit tu sua diem nay, khong mac loi.

## 2. Claim (b): bench 2-vision DONE, UPHELD chi tren run moi, SURVIVES

### Tan cong B1: manifest commit 5f86046 khong phai ancestor cua main?
Kiem tra: `git merge-base --is-ancestor 5f86046 origin/main` tra ve khong. `git merge-base --is-ancestor 5f86046 origin/todolist-push` tra ve co. 5f86046 cung la ancestor cua neo audit 2ed0caf.
Ket luan: tan cong that bai ve ban chat, nhung audit viet mo ho. Audit ghi "la ancestor cua tip" ma khong noi ro tip nao. Su that: ancestor cua todolist-push, khong phai cua main. File deploy-manifest.json cung chi co tren todolist-push, khong co tren main. Day la loi dien dat, xem muc 4.

### Tan cong B2: d7d569b chi la commit docs, khong chua bench code?
Kiem tra: `git cat-file -e d7d569b:tests/two_vision_bench.py` tra ve co. `git cat-file -e d7d569b:tests/two_vision_fixture.html` tra ve co. Blob bench o d7d569b la 80b00469c4676d7a9a8934626b6bf66ed2a5aeee, giong het blob o a1a672d va o neo 2ed0caf.
Ket luan: tan cong that bai. Source commit pin dung cay chua bench code.

### Tan cong B3: bench code khong byte-identical giua 2 run?
Kiem tra: `git rev-parse` cho bench o a1a672d, d7d569b, 2ed0caf deu tra ve 80b00469c4676d7a9a8934626b6bf66ed2a5aeee. Fixture o ca ba deu la bac2702efa375ad330cce8130df40d8025d86261. `git show c5311ce:tests/two_vision_bench.py | wc -l` tra ve 868, fixture 48 dong, khop audit. Commit c5311ce va 7f3a70b (2026-11-21 23:37:31 UTC) dem bench len todolist-push truoc run a1a672d (23:41:27 UTC) 4 phut.
Ket luan: tan cong that bai. Nhung luu y: blob bench tren main o neo 81ea6e0 da doi thanh e5681192765bd18c26f43f56493d78cefd092159, nen tinh byte-identical chi dung cho ban sao tren todolist-push, xem muc 5.

### Tan cong B4: results.json cung chi o local, vay (b) phai bi REVOKED nhu (a) va (c)?
Kiem tra: khong co results.json cua bench trong repo o neo 2ed0caf, chi co mot file results.json khong lien quan o docs/research. Thu muc /tmp/click4-bench-manifest va /tmp/click4-bench-workdir hien khong con ton tai tren may nay.
Phan biet that: goi bang chung cua (b) trong repo manh hon han (a) va (c). File deploy-manifest.json o neo 2ed0caf pin source_commit d7d569be5c9f88986abdd8416143c64981667986, source_content_sha256 92891523266e1af568e14bdcb65319ee39a2a6ab2fcce9e5fa1c8d4e1966c607, run_id bench-20261122T020225Z-3d9270, wall 12.6852s, visions_used 2, outcome PASS, ca 2 send V12 gated (0.6088s va 0.3867s). Log improvements/worker-click4-bench-manifest-log.md trich verbatim output run va output verify o muc 6, ghi exit 0. Script scripts/bench_manifest.py va test tests/test_bench_manifest.py co trong repo o neo, test 4/4 PASS ghi o muc 5 cua log.
Kiem tra doc lap manh nhat: tao worktree tam o d7d569b, chay ham digest cua chinh repo, ket qua tra ve 92891523266e1af568e14bdcb65319ee39a2a6ab2fcce9e5fa1c8d4e1966c607, MATCH voi manifest. Kich thuoc blob cung khop: bench 38378 bytes, fixture 2014 bytes.
Ket luan: tan cong that bai. CB-9 doi hoi lock source commit, installed artifact, va log, ca ba deu co trong repo cho run moi. Cang thang ve tieu chuan local-only la co that, nhung khong pha duoc verdict vi CB-9 dinh nghia ro dieu kien du cho rung 1. Han che ve do ben xem muc 5.

### Tan cong B5: so run a1a672d bi sai?
Kiem tra: commit a1a672d (2026-11-21 23:41:27 UTC) chi co 1 file improvements/worker-probe-s2-log.md, 199 dong. Log ghi attempt 1 FAILED vi OSError Errno 28, /tmp 100%, attempt 2 06:40:30-06:40:41 +07 EXIT 0, wall 10.8596s, run_id bench-20261121T234030Z-86e8d8, visions_used 2, outcome PASS, 2 send 0.6904s va 0.6807s. Closeout 4ac9320 muc 5 ghi manifest cua a1a672d NOT locked va results.json 733 bytes chi o local.
Ket luan: tan cong that bai. Audit dung.

### Tan cong B6: direction log va contract da sua trich dan sang run moi?
Kiem tra: o neo 2ed0caf, improvements/worker-click3-final-direction-log.md dong 451-455 (step 3) va dong 538-544 (rung 1) van trich a1a672d, kem "pending manifest lock". File docs/layer0-cbexec-contract.md dong 667-668 van trich a1a672d, kem "pending manifest lock".
Ket luan: tan cong that bai. Audit dung khi noi can sua trich dan ngay, va day la sua trich dan chu khong phai chay lai bench.

## 3. Claim (c): DOM-grounding DONE, REVOKED, SURVIVES

### Tan cong C1: bench co tren main nen bang chung da co trong repo?
Kiem tra: tests/dom_grounding_bench.py, tests/dom_grounding_fixture.html, tests/dom_bench_2win.py deu KHONG co tren todolist-push, ca o neo 2ed0caf lan o tip hien tai d2da482. Ca ba deu co tren main o neo 81ea6e0. Claim lam gate nam trong direction log tren todolist-push, ma nhanh do khong chua cong cu chung minh claim cua chinh no.
Ket luan: tan cong that bai. Audit dung tren pham vi nhanh direction. Day la suy luan co the tranh cai nhat cua audit, vi CB-8 khong viet ro bang chung phai nam tren cung nhanh, nhung suy luan nay co ly va duoc ap dung nhat quan voi chuan V4/V7/V8.

### Tan cong C2: raw log grounding co trong repo?
Kiem tra: `git ls-tree -r --name-only` o ca 81ea6e0 va 2ed0caf, grep dom_grounding_run, tra ve khong co file log tho nao.
Ket luan: tan cong that bai. Audit dung.

### Tan cong C3: so lieu grounding bi sai?
Kiem tra: docs/clone2-dom-grounding-20261122.md 401 dong o neo 81ea6e0. Dong 22 va 127 ghi 66 rects, Marionette pooled median 0.030s, 9 samples, BiDi run medians 0.006 den 0.054s. Dong 25-27 va 131 ghi 5 pointer clicks, all 5 landing, 3 runs cua click step, verify bang 1 lan doc DOM 0.002 den 0.015s. Dong 138 ghi agreement toi da 5.7e-14 px. Dong 77-91 ghi run 2 va 3 full 14.35s va 12.74s, run 4 va 5 fix-pass 16.15s va 15.57s.
Dem lai E2: tests/calibration-e2-hits.jsonl 87 dong o neo 2ed0caf. Loc case_id e2-vision: n bang 29, hit true 17, false 12, tuc 17/29 bang 58.6 percent, khop audit.
Ket luan: tan cong that bai. Tat ca so deu khop.

### Tan cong C4: bao cao 2-window corroboration manh den muc cuu duoc DONE?
Kiem tra: docs/clone2-dom-bench-2win-20261122.md dong 150 ghi pooled median 0.0112s, dong 172 ghi max delta 0.0 px o ca 4 window-runs, dong 186-192 ghi all five landed true o ca 4 window-runs.
Nhung cung file nay ghi mot run moved/scroll-btn that bai: dong 36-39, 93, 267-269 ghi 2 of 5 clicks landed on tall spacer o ca 2 windows, all_five_landed false, mechanism UNKNOWN. Audit khong neu run that bai nay.
Ket luan: tan cong that bai ve huong verdict, vi run that bai chi lam REVOKED manh them chu khong cuu duoc DONE. Nhung day la thieu sot ve tinh day du cua audit, xem muc 5.

### Tan cong C5: bao cao khong he ghi UNVERIFIED cho Zen that va live page?
Kiem tra: muc 9 cua bao cao co tieu de "UNVERIFIED on this machine", ghi ro real Zen, live pages, headed runs chua do, tat ca so la Firefox 160.0.1 headless tren fixture tinh local. Dong 7 ghi quy tac "Anything not run here is labelled UNVERIFIED".
Ket luan: tan cong that bai. Audit dung ve ban chat. Chi sai nho ve dien dat: muc 8 la recommendations, khong mang nhan UNVERIFIED, chi muc 9 moi mang nhan do, xem muc 4.

### Tan cong C6: council va redteam khong review bao cao grounding?
Kiem tra: coord/clone2.md dong 687 tro di, o neo 81ea6e0, ghi council va redteam chan lai so session.new BiDi sai, "three full runs" sai, so a11y khong co bang chung, va bao cao da sua het. Noi dung khop audit.
Ket luan: tan cong that bai. Nhan tien, coord ghi bao cao 402 dong va verify 0.005-0.015s, trong khi file that la 401 dong va 0.002-0.015s. Audit ghi dung theo file, coord sai nho.

### Tan cong C7: "DOM click KHONG bang chuot that" la audit tu them?
Kiem tra: docs/zen-error-fix-todolist-20261121.md:47 o neo 2ed0caf ghi dung cau "DOM click KHONG bang chuot that". Dong 60 ghi DONE 21/11 05:30 E2 live, DOM rects chinh xac tuyet doi, vision 58.6 percent (17/29), pointer nho hon 1px.
Ket luan: tan cong that bai. Audit trich dung.

### Tan cong C8: commit bench 79b75e7 va 47d5ee6 khong ton tai?
Kiem tra: 79b75e7 them tests/dom_grounding_bench.py 354 dong va fixture 49 dong. 47d5ee6 them 95 dong vao bench, gom buoc a11y snapshot.
Ket luan: tan cong that bai.

## 4. Loi nho cua audit, khong pha verdict

1. Gio neo main sai 3 phut: audit ghi 81ea6e0 (2026-11-22 04:05 UTC), thuc te commit time la 04:08:01 UTC. Gio bat dau audit ghi 11:04 +07, tuc 04:04 UTC, con truoc ca commit neo main. Neo todolist-push 2ed0caf ghi 04:01 UTC thi dung (04:01:44 UTC).
2. "Ancestor cua tip" mo ho o muc 3.3: 5f86046 chi la ancestor cua todolist-push, khong phai cua main. Can ghi ro nhanh.
3. Trich dan thieu tien to thu muc: audit ghi "worker-click3-final-direction-log.md:251" va ":228", thuc te file o improvements/worker-click3-final-direction-log.md. So dong thi khop dung (251 la dong CB-8, 228 la dong S2+D5). Tuong tu, layer0 contract o docs/.
4. Muc 4.3 viet "muc 8 va 9 ghi UNVERIFIED": chi muc 9 mang nhan UNVERIFIED, muc 8 la recommendations. Ban chat dung.
5. So 80/81 o muc 2.4 khong neu ten file nguon: so nay nam o improvements/worker-y1b-rpc-land-log.md:123, khong phai trong worker-y1b-fix-log.md. So thi dung, trich dan thieu.
6. Audit khong kiem tra duoc tai thoi diem viet rang file deploy-manifest.json khong co tren main. Khong anh huong verdict vi claim nam tren todolist-push.

## 5. Thieu sot ve pham vi va fact lien quan gate, khong pha verdict

1. Audit khong vuot pham vi: chi audit 3 claim, muc 5 la khuyen nghi suy ra tu verdict, va audit tu ghi ro chua qua council 3 nguoi va redteam. Khong co vuot pham vi.
2. Lien he batch 7 dung: docs/clone2-violation-verify-20261122.md (ebf6ec8) upheld 13/13, 3 HIGH, 5 MEDIUM, 5 LOW. V13 bao phu (a), noi ve speed-swarm-report trich laptop /tmp. V4, V7, V8 la cac violation log chi o local. Khong co violation nao nhac toi 2-vision, two_vision, dom_grounding hay dom-grounding, nen (b) va (c) dung la kiem tra moi. File docs/clone1-batch7-high-fixes-verify-20261122.md xac nhan V1, V2, V3 PARTIALLY FIXED.
3. Audit bo sot run that bai trong bao cao 2-window: run moved/scroll-btn co 2 of 5 clicks roi len tall spacer o ca 2 windows, all_five_landed false, mechanism UNKNOWN. Viec bo sot nay khong doi verdict, vi no chi lam suy yeu them phan corroboration cua (c).
4. Blob bench tren main da doi: o neo main 81ea6e0, tests/two_vision_bench.py la blob e5681192, khac blob 80b00469 tren todolist-push. Tinh byte-identical giua 2 run chi dung cho ban sao todolist-push. Run sau chay tu main se khac build.
5. Do ben cua (b): thu muc /tmp/click4-bench-manifest va /tmp/click4-bench-workdir hien khong con, nen lenh verify o muc 6 cua manifest log khong the chay lai y nhu cu, vi no can results.json da mat. UPHELD hien dua vao file manifest trong repo, log trich verbatim, va digest da kiem tra lai khop, chu khong dua vao mot lan verify chay lai duoc. Redteam da tinh lai digest tu worktree tam o d7d569b va khop hoan toan, nen diem nay la canh bao ve do ben, khong phai loi cua audit tai thoi diem viet.
6. Ke hoach khoi phuc cua audit chua noi ai chay lai cac run: trong luc redteam chay, mot cap nhat bo nho ghi rang live run S2 flip khong chay duoc tu may clone1 vi khong co duong SSH toi laptop, nen live run phai chay phia laptop. Cac buoc khoi phuc (a) chay lai P1-P4 va (c) chay tren Zen that va live page can chu so huu ro rang, neu khong se ket o buoc giao viec.

## 6. Nhung gi redteam khong thu

- Khong chay lai bench 2-vision, bench grounding, hay probe Y1b nao.
- Khong chay lai toan bo lenh verify cua manifest, vi results.json goc da mat. Thay vao do, redteam tinh lai source_content_sha256 tu worktree tam o d7d569b bang ham digest cua chinh repo, ket qua MATCH.
- Khong kiem tra noi dung cua 484 file improvements hay toan bo lich su, vi vuot pham vi 3 claim.

## 7. Ket luan

Ca 3 verdict deu SURVIVES sau khi bi tan cong truc tiep bang lenh git va dem lai so tu file: (a) REVOKED SURVIVES, (b) UPHELD chi tren run moi SURVIVES, (c) REVOKED SURVIVES. Cac loi tim duoc la loi nho ve gio neo, trich dan, va dien dat o muc 4, va cac thieu sot o muc 5 khong doi huong verdict nao. Khuyen nghi: sua 6 diem nho o muc 4 truoc khi dung audit lam co so quyet dinh, bo sung run that bai 2-window vao ho so (c), va chi ro chu so huu phia laptop cho cac buoc khoi phuc.
