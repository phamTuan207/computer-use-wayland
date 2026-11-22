# Council 2, batch 10 task 3: kiem tra claim (b) bench 2-vision DONE

Ngay kiem tra: 22/11/2026, 11:16 +07.
Nguoi kiem tra: council 2, batch 10 task 3.
Tai lieu duoc kiem tra: docs/batch10-task3-cb8-audit-20261122.md, muc 3.
Neo kiem tra: origin/main 929a2042cccc791db4527ea3c09ccdeacb95b261 (11:16 +07 22/11), origin/todolist-push d2da4820cbc31adbad39c93670f30a01ff2c7709 (cung thoi diem). Chi doc tren git (git show, git cat-file, git ls-tree, git grep, git log, git merge-base), khong sua nhanh nao, khong chay bench nao. Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. Khong thong tin ca nhan. Khong dau gach ngang dai.

## Verdict: UPHELD STANDS

Claim (b) bench 2-vision DONE dung, chi tren trich dan run moi run_id bench-20261122T020225Z-3d9270, build d7d569b, manifest commit 5f86046. Trich dan a1a672d lam gate bi thu hoi la dung. Cac phat hien bo sung o muc 5 khong doi verdict, chi lam ro pham vi va danh sach cho can sua.

## 1. Run a1a672d: du 4 yeu to CB-8 cho fixture pass, khong co manifest, khong bao gio co duoc

- Commit a1a672d ton tai: a1a672db3d93d19bbd5a44868ea7ed43cb9fa876, 2026-11-21 23:41:27 UTC, message "probe-s2: fixture 2-vision bench PASS 10.86s, Y1b 3 fails still open, flag NOT flipped (gate b unmet)". Chi 1 file, improvements/worker-probe-s2-log.md, 199 dong. Kiem tra bang `git log -1` va `git show --stat a1a672d`.
- Log co day du 4 yeu to: lenh chay `venv python tests/two_vision_bench.py --fixture --mode run` (dong 92-93); attempt 1 FAILED vi het disk, OSError Errno 28 No space left (dong 98-99); attempt 2 06:40:30-06:40:41 +07, EXIT 0, outer wall 11,305 ms (dong 111); outcome PASS, wall_s 10.8596, run_id bench-20261121T234030Z-86e8d8, visions_used 2, ca 2 sends V12 gated 0.6904s va 0.6807s (dong 122-133). Kiem tra bang `git show a1a672d:improvements/worker-probe-s2-log.md`.
- Bench va fixture da co tren todolist-push truoc run: c5311ce va 7f3a70b, ca hai 2026-11-21 23:37:31 UTC, truoc a1a672d 4 phut. Blob 80b00469c4676d7a9a8934626b6bf66ed2a5aeee (868 dong, 38378 bytes) va bac2702efa375ad330cce8130df40d8025d86261 (48 dong, 2014 bytes), deu ton tai qua `git cat-file`. Nhan xet Codex va FCC ve bench vang mat da loi thoi, dung nhu audit noi.
- Khong co manifest cho run nay, va khong bao gio co duoc: closeout 4ac9320, section 5, ghi ro "the CB-9 manifest for a1a672d is NOT locked", "must not be quoted as a gate until a manifest is locked", "A retroactive manifest cannot be manufactured: the build predates the mechanism and the installed tree at bench time is gone". Co che manifest chi land o 18f2304, sau khi bench chay luc 06:40 +07, nen khong the co manifest cho build nay. Kiem tra bang `git show 4ac9320:improvements/worker-click4-step1-closeout-log.md`, dong 245-300.
- Ket luan muc 1: audit dung. a1a672d la fixture pass that, nhung khong duoc trich lam gate.

## 2. Run moi d7d569b: co manifest khoa trong repo, verify exit 0, quotable

- Build d7d569b ton tai: d7d569be5c9f88986abdd8416143c64981667986, 2026-11-22 01:58:21 UTC, "docs: C4 step-1 closeout log, record commit hash 4ac9320 in log". Kiem tra bang `git log -1 d7d569b`.
- Manifest commit 5f86046 ton tai: 5f860468b0d1b90fa56fa2a791d8b85cf63879b6, 2026-11-22 02:08:09 UTC, "C4 bench manifest: fixture 2-vision PASS 12.69s at d7d569b, CB-9 manifest locked, rung 1 quotable". 4 file: deploy-manifest.json, improvements/worker-click4-bench-manifest-log.md, scripts/bench_manifest.py, tests/test_bench_manifest.py. Kiem tra bang `git log -1` va `git show --stat 5f86046`.
- deploy-manifest.json o tip todolist-push ghi dung cac so audit neu: source_commit d7d569be5c9f88986abdd8416143c64981667986, source_content_sha256 92891523266e1af568e14bdcb65319ee39a2a6ab2fcce9e5fa1c8d4e1966c607, run_id bench-20261122T020225Z-3d9270, wall_s 12.6852, visions_used 2, outcome PASS, step 1 clone1 0.6088s va step 2 clone2 0.3867s, ca hai v12_gate_ok true, v1_value_ok true, v11_input_events 47. Kiem tra bang `git show origin/todolist-push:deploy-manifest.json`.
- Verify chay exit 0, tat ca check ok, ghi verbatim o manifest log section 6: `ok source_commit`, `ok source_content_sha256`, `ok git_status_clean`, `ok artifact:bench_script` (blob 80b00469), `ok artifact:fixture` (blob bac2702e), `ok fixture:hardcoded_path`, ca 3 runtime binaries (firefox, firefox_bin, geckodriver), `ok log:exists_and_names_run`, `ok results:run_id_outcome: run_id=bench-20261122T020225Z-3d9270 outcome=PASS`, dong cuoi "verify OK: manifest matches the checkout under test", sau do "Exit 0. Every check passes". Kiem tra bang `git show origin/todolist-push:improvements/worker-click4-bench-manifest-log.md`, dong 205-245.
- Mechanism tests 4/4 PASS o section 5: test_write_pins_commit_and_artifacts, test_write_refuses_dirty_checkout, test_write_refuses_non_pass, test_verify_passes_with_log_then_fails_on_tamper, "Ran 4 tests in 0.490s, OK". Kiem tra bang cung file, dong 181-195.
- Manifest log noi ro run quotable la run moi, khong phai a1a672d (headline va section 7, dong 262-269), va bench code byte-identical giua 2 run (dong 110-111, 139-140). Kiem tra bang cung file.
- Ket luan muc 2: audit dung. Run moi co manifest khoa trong repo, verify exit 0, quotable.

## 3. Trich dan can sua: audit xac dinh dung vi tri chinh, danh sach can mo rong

- final-direction step 3, dong 451 tren todolist-push, van trich a1a672d: "3. Fixture 2-vision bench: DONE. Bench PASSED (a1a672d, 10.86s, visions_used 2, both sends V12 gated, V-Z5). ... Pending: the CB-9 manifest for that build is locked before the pass is quoted as a gate."
- final-direction rung 1, dong 371-372 va 538-543, van trich a1a672d va run_id cu bench-20261121T234030Z-86e8d8, status "passed, pending manifest lock".
- layer0-cbexec-contract.md dong 667, van trich a1a672d: "Rung 1, fixture 2-vision benchmark: PASSED (a1a672d, 10.86s, visions_used 2, both sends V12 gated), pending manifest lock."
- Ca 3 vi tri audit neu deu dung va deu can doi sang run_id bench-20261122T020225Z-3d9270. Kiem tra bang `git grep -n a1a672d origin/todolist-push` va `git show` tung file.
- Bo sung o muc 5, phat hien F3: con nhieu cho trich gate khac cung can doi, khong chi 3 cho tren.

## 4. Verdict UPHELD chi tren run moi la verdict dung

- DONE o day la trang thai cua mot bang chung cu the, khong phai cua tinh nang. a1a672d co log day du nhung thieu manifest va khong bao gio co duoc, nen khong dat chuan gate. Run moi co day du log, manifest, verify exit 0, nen dat chuan gate.
- UPHELD chi tren trich dan run moi la phan biet dung: giu gia tri cua bench pass that, dong thoi cam trich dan cu lam gate. Khong co ly do de ha xuong REVOKED hoan toan, vi bang chung cua run moi co trong repo va kiem tra lai duoc. Khong co ly do de mo rong UPHELD sang a1a672d, vi closeout 4ac9320 da ket luan manifest khong the tao hoi to.
- Ket luan: UPHELD STANDS cho claim (b), chi tren trich dan run moi.

## 5. Phat hien bo sung (khong doi verdict)

- F1, audit viet chua chinh xac ve nhanh: audit noi 5f86046 "la ancestor cua tip" va "deploy-manifest.json co o tip". Dung chi tren todolist-push: 5f86046 la ancestor cua tip todolist-push luc audit (2ed0caf) va tip hien tai (d2da482). Khong phai ancestor cua tip main luc audit (81ea6e0) hay tip main hien tai (929a204); `git show origin/main:deploy-manifest.json` bao loi file khong ton tai. Vi claim (b) va huong di nam tren todolist-push, sai sot ve ten nhanh nay khong doi verdict, nhung ban ghi can ghi ro "todolist-push", khong ghi chung "tip".
- F2, results.json cua ca 2 run deu khong con o local: /home/hatch/probe-s2-work/results.json va /tmp/click4-bench-workdir/results.json deu khong ton tai tren VM luc 11:16 +07 22/11 (ls bao No such file or directory). Han che audit ghi o muc 3.3 ("results.json cua run moi van o VM-local") nay da manh hon: khong the chay lai verify doi chieu results.json o dau nua. Bang chung quotable con lai la manifest da commit cong output verify verbatim da commit trong manifest log (da ghi ok results:run_id_outcome luc verify). Dieu nay giam kha nang kiem tra lai doc lap, nhung khong lam sai ban ghi da commit. Ghi chu: con so 733 bytes cua results.json run cu lay tu closeout 4ac9320 ("still present, 733 bytes"), council khong kiem tra lai duoc vi file da mat va khong co trong repo.
- F3, danh sach cho can sua trich dan chua du: ngoai step 3, rung 1, va layer0:667, cac cho trich gate khac van dung a1a672d va cung can doi sang run moi: final-direction dong 207 (hang A10, rung 1 "pending the CB-9 manifest before it is quoted as a gate"), dong 228 (dieu kien gate (a) "MET (a1a672d, 10.86s, V-Z5)"), dong 535-536 (precondition "not quoted as a gate until its manifest is locked"), dong 687 (dieu kien mo B2 "fixture bench green (MET, a1a672d)"), va layer0 dong 629 (hang CB-9, cung cau "not quoted as a gate"). Cac cho ke chuyen lich su (dong 39, 104, 149, 339, 399, 541, 889, 1016, 1036) mo ta dung run cu va giu nguyen. Viec sua la sua trich dan, khong chay lai bench.

## 6. Viec can lam tiep theo

1. Sua trich dan bench o final-direction (step 3, rung 1, hang A10, dieu kien gate (a), precondition, dieu kien mo B2) va layer0-cbexec-contract.md (dong 629 va 667): doi a1a672d sang run_id bench-20261122T020225Z-3d9270, build d7d569b, manifest commit 5f86046.
2. Ghi ro trong ban sua rang manifest nam tren todolist-push, khong phai main.
3. Khong dung a1a672d lam gate o bat ky cho nao nua.
