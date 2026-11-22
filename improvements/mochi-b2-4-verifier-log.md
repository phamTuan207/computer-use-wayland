# Verifier log B2-4 step 10 (doc lap)

Verifier: verifier doc lap, khong phai worker, khong phai reviewer cu.
Worktree: ~/workspace/mochi-b2-4-work. Commit fix can verify: 87efda9
(87efda94c466a83c50c84b3958cb10504977787b), tren ff747a9, base ed4fcd4.
Worktree sach luc bat dau, git status khong co output. Khong sua code,
khong push, khong chay live, khong xoa file, khong dong hoac navigate
tab trinh duyet, khong dung ydotool. Khong dau gach ngang dai, chi dau
phay, dau cham, gach noi ngan. Khong thong tin ca nhan. Moi claim co du
4: lenh, output, commit hash, gio Viet Nam cong elapsed.

## 0. Evidence contract (viet truoc moi check chay duoc)

Doc dinh huong truoc contract (khong chay test, khong chay mutation):
git status, git log, git show stat 87efda9, doc day du worker log
section 10, council 1 log, council 2 log, council 3 log, redteam log.
Moi check duoi day chi tinh neu dieu kien hoan thanh duoc viet truoc
khi chay, gom lenh, output mong doi, hash commit, log thoi gian.
Khong viet truoc thi check do khong tinh. Do lai moi con so tu du
lieu goc, khong copy claim cua worker sua hay cua reviewer.
"Inconclusive" la trung thuc, KHONG phai pass. Ket luan chi 1 trong
3: PASS, CHUA PASS (kem finding cu the), INCONCLUSIVE (kem ly do).

- V-C1, compile: `python3 -m py_compile scripts/s2_flip_live.py
  tests/test_s2_flip_wiring.py` trong worktree. Mong doi: exit 0,
  khong output. Hash: 87efda9.
- V-C2, wiring cong pill: `python3 -m unittest
  tests.test_s2_flip_wiring tests.test_s2_flip_pill` trong
  worktree. Mong doi: Ran 60 tests, OK (54 wiring cong 6 pill).
  Baseline: ban HEAD nguyen ven qua `git archive HEAD` toi thu
  muc tam, cung lenh. Mong doi: Ran 38 tests, OK. Delta mong
  doi: 22 test moi (8 BrokerCodeExecTests goc cong 14
  BrokerProbeRecountTests moi). Dem so test moi bang grep
  `def test_` trong tung class moi.
- V-C3, neighbour: `python3 -m unittest tests.test_session_remote
  tests.test_code_exec` trong worktree. Mong doi: Ran 163 tests,
  OK.
- V-C4, mutation: chay lai mutation tren ban sao /tmp, khong bao
  gio sua worktree, 8 muc F-C5 (M-F1 seq, M-F2 bo probe, M-F3
  replay thanh refusal, M-F4 running/failed nuot, M-F5 bo raise
  unknown, M-F6 bo recount, M-F7 bo check accepted, M-F8 them
  --bogus-flag). Mong doi: moi mutation lat dung test dich sang
  FAIL hoac ERROR, test dich PASS o ban control. Rieng M-F5:
  kiem tra ky, vi lan chay sua dau tien cua worker M-F5 khong
  lat duoc test (test pass nho catch-all raise) roi moi siet
  test; verify phai chay ca mutation M-F5 goc (bo raise
  unknown) tren code hien tai va ghi ro test bat duoc nho
  assert nao.
- V-C5, code fix doc source: (a) post-accept tra next_seq =
  seq+1 qua _BrokerSendConsumed; (b) probe result --sequence N
  truoc fallback, chi fallback khi not_found; broker_unavailable
  KHONG duoc coi la bang chung (vi _exchange map moi socket
  OSError thanh ten do), probe khong tra loi duoc thi khong
  fallback; (c) replay completed duoc chap nhan; (d)
  running/failed/unknown deu raise voi seq tien; (e) recount
  count_check truoc fallback cho ca 2 variant, fill cung co 1
  lan dem; (f) bo validate program_variant trung lap; (g)
  docstring chi neu CLI subcommand. Mong doi: moi muc co dong
  code cu the trich dan, hoac finding neu thieu.
- V-C6, doc bang grep: HEAD ed4fcd4 trong 3 drill, prep log
  section 9, worker log; importlib 103-106 o ca 3 cho; section
  4/5 prep log sua tai cho cong pointer toi section 9; khong
  dau gach ngang dai trong 7 file cua commit 87efda9. Mong doi:
  moi muc co lenh grep va output cu the.
- V-C7, drill: (a) A5 step 3 script standalone one-shot JSONL
  theo hinh step 8, compile thu, khong chay live; step 1/5 co
  --chromium-set-value, precondition 3 tro ve step 1, run JSON
  khong co truong broker_finish; (b) A3 wedge drill: lenh exact
  cho lock probe (ky vong busy), poll status (driver van ready
  khi SIGSTOP, khong truong last_activity), poll result
  (request tra accepted/busy ngay, chi result cho 120s), finish
  tra cleanup_pending sau 120s, fresh start tra
  recovery_required o buoc 6 va chi duoc chap nhan sau buoc 7,
  computer-use recover truoc va cam unlink session.json tay,
  lay PID/PGID qua cay process cua relay; doi chieu tung so
  dong trich dan voi scripts/session_remote.py tai 87efda9;
  (c) A4 probe: .so Y6e rebuild cong md5, backup 1 dead ABI
  (sha256), launcher Y6e
  improvements/worker-y6e-nested-load-test.sh, runner Y6b v2
  improvements/worker-y6b-run-nested-wayland-v2.sh, ghi ro
  khong ton tai script driver LIQUID standalone trong repo;
  kiem tra cac duong dan file va hash duoc neu co ton tai
  trong worktree, khong chay live.
- V-C8, ghi chu 3 exec exit nonzero trong run cua worker sua:
  xac nhan xem chung co phai la failure co chu y cua mutation
  (test fail tren ban doi) hay la loi that. Mong doi: liet ke
  tung exit nonzero, lenh, output, ket luan tung cai.
- V-C9, kim tu thap tin tuong: fix nao chi la text rule trong
  khi co the lam check xac dinh hoac thiet ke lai thi ghi ro.

Thoi gian bat dau: 2026-11-23 00:44 +07 (nhan task 00:44:40 +07).
Hash co so: 87efda9.

## 1. Check evidence (moi muc co lenh, output, hash, gio, elapsed)

Hash cho moi check: 87efda9, tru khi muc ghi ro hash khac.
Gio Viet Nam (UTC cong 7).

### V-C1, compile: PASS

- Lenh: `python3 -m py_compile scripts/s2_flip_live.py
  tests/test_s2_flip_wiring.py`, trong worktree.
  Output: PY_COMPILE_OK, exit 0, khong output. Thoi gian:
  2026-11-23 00:45:12 +07, elapsed 0.129s. Hash: 87efda9.

### V-C2, wiring cong pill 60 OK, baseline 38 OK, delta 22: PASS

- Lenh: `python3 -m unittest tests.test_s2_flip_wiring
  tests.test_s2_flip_pill`, trong worktree. Output: Ran 60
  tests in 0.334s, OK. Thoi gian: 2026-11-23 00:45:15 +07,
  elapsed 0.546s. Hash: 87efda9.
- Dem test: `grep -c 'def test_' tests/test_s2_flip_wiring.py`
  tra 54 wiring. Class: CodeExecEndpointTests, ProgramShapeTests,
  BrokerCodeExecTests (8 test, dong 848-1004),
  BrokerProbeRecountTests (14 test, dong 1067-1409). 32 cu cong
  8 cong 14 bang 54. Cong 6 pill bang 60.
- Baseline, DIEU CHINH QUAN TRONG: task ghi "baseline ban HEAD
  nguyen ven qua git archive", nhung HEAD luc verify la 87efda9
  (da gom fix), nen `git archive HEAD` se tra 60 test, khong
  phai baseline. Baseline dung la base ed4fcd4. Lenh:
  `git archive ed4fcd4` toi ~/workspace/b24-v-baseline, cung
  lenh unittest. Output: Ran 38 tests in 0.328s, OK. Thoi gian:
  2026-11-23 00:45:29 +07. Hash: ed4fcd4. Delta 60 tru 38 bang
  22, dung 8 cong 14. Ghi chu: /tmp day 97-99% luc chay nen
  ban sao baseline dat o ~/workspace thay vi /tmp, khong anh
  huong ket qua.
- Diff stat commit 87efda9 do lai: 7 file, 2769 insertions,
  79 deletions, khop claim.

### V-C3, neighbour 163 OK: PASS

- Lenh: `python3 -m unittest tests.test_session_remote
  tests.test_code_exec`, trong worktree. Output: Ran 163 tests
  in 52.006s, OK. Thoi gian ket thuc: 2026-11-23 00:46:27 +07,
  elapsed 52.210s. Hash: 87efda9.

### V-C4, mutation 8/8 lat dung test dich: PASS

Ban sao o ~/workspace/b24-v-mutbase (git archive 87efda9),
khong bao gio sua worktree. Git status sau mutation chi con
`?? improvements/mochi-b2-4-verifier-log.md`, worktree sach
ve code.

(a) Mutation cua rieng verifier
(`~/workspace/b24-v-mutations.py`, chay 00:46:53-00:47:01 +07,
elapsed 6.285s, hash 87efda9). Control: 14 test OK, rc 0.
Ket qua tung muc, tat ca rc 1:

- M-F1 (except handler ve seq): FAIL 5 test, gom target
  test_two_browser_disabled_then_broker_seq_advances cong 4
  test cung assert broker_next_seq 4. Collateral hop ly.
- M-F2 (probe thanh not_found): FAIL 2 test, gom target
  test_probe_record_found_refuses_fallback cong
  test_probe_unavailable_refuses_fallback. Hop ly, ca hai
  deu dua vao probe gate.
- M-F3 (replay completed thanh refusal): ERROR 1 test,
  target test_real_broker_replay_completed_accepted.
- M-F4 (running/failed tra envelope): FAIL 3 test, gom target
  running, failed, cong replay-failed. Hop ly, cung nhanh.
- M-F5 (bo raise unknown): FAIL 1 test duy nhat, target
  test_result_unknown_raises_with_next_seq. Xem chi tiet duoi.
- M-F6 (bo recount): FAIL 2 test, gom target recount-refuses
  cong recount-fill.
- M-F7 (bo check accepted): ERROR 1 test, target
  test_real_broker_rejects_unknown_request_status.
- M-F8 (them --bogus-flag): FAIL 1 test, target
  test_real_broker_request_command_shape.

(b) Script mutation cua chinh worker sua
(`/tmp/b24-fix-mutations.py`, chi doi BASE sang
~/workspace/b24-v-fix-mutbase vi /tmp het cho, chay
00:49:40 +07, elapsed 7.604s, hash 87efda9). Output:
control rc 0, moi target rc 1, ket thuc `ALL MUTATIONS FLIP
THEIR TARGET`, script exit 0. Collateral khop log worker
(M-F1 5, M-F2 2, M-F3 2 error gom replay-failed, M-F4 3,
M-F6 2, M-F7 3 error gom ca hai replay test).

(c) M-F5 kiem tra ky (diem worker sua tung thu):
Chay rieng mutation M-F5 tren ban sao, 00:49:05 +07. Output:
FAIL duy nhat test_result_unknown_raises_with_next_seq,
`'result unknown' not found in "broker code-exec unexpected
result status for sequence 3: {'ok': True, 'status':
'unknown', ...}"`. Giai thich: khi bo raise unknown, code
roi xuong catch-all raise, message cua no van chua chu
'unknown' (nam trong dump cua resp), nen mot assert long
chi kiem 'unknown' se van PASS (do la truong hop hollow o
lan chay sua dau tien 00:39:05 +07). Test hien tai assert
chinh xac cum 'result unknown', la cum chi co o raise
chuyen biet, nen mutation bi bat. Ket luan: test da duoc
siet that, M-F5 khong con hollow.

### V-C5, code fix doc source: PASS, tung muc co dong cu the

File scripts/s2_flip_live.py tai 87efda9, 1400 dong.

- (a) Post-accept tra next_seq seq+1: class
  _BrokerSendConsumed dong 234-247, `__init__` gan
  broker_next_seq bang seq+1. broker_code_exec dong 490-494:
  request loi thanh NotAccepted, moi RuntimeError khac thanh
  Consumed(seq). Dong 505-519: status unknown, running,
  failed, bat ky status la nao deu raise _BrokerSendConsumed
  voi message rieng ('result unknown', 'still running',
  'result failed', 'unexpected result status'). Dong 641-644:
  disabled envelope raise Consumed. _send_browser_inner
  except handler dong 1144-1163: `out['broker_next_seq'] =
  getattr(exc, 'broker_next_seq', seq)` khi chua co gia tri,
  nen V12 loi sau send thanh cong khong ghi de seq da tien.
  Test hai browser dong 1067-1111 pin hanh vi nay, M-F1 lat.
- (b) Probe truoc fallback: _probe_request_record dong
  522-561, chay `result --sequence N`, tra record, not_found,
  hoac unavailable. _code_exec_send dong 606-639: chi khi
  probe tra not_found moi chay before_fallback roi oneshot;
  record thi raise Consumed; unavailable thi raise
  RuntimeError thuong, khong fallback. broker_unavailable
  KHONG la bang chung: _exchange o scripts/session_remote.py
  dong 1319-1345, khoi try gom connect, sendall, recv, va
  `except OSError` dong 1344-1345 map moi OSError thanh
  BrokerError('broker_unavailable'). Vay recv loi sau khi
  request da truyen cung mang ten do. Code noi ro dieu nay
  o docstring _code_exec_send dong 579-582. Probe khong tra
  loi duoc thi khong fallback, operator rerun --transport
  oneshot hoac script step 3 drill A5 (lua chon thiet ke co
  chu y, co test test_probe_unavailable_refuses_fallback pin
  broker_next_seq 3).
- (c) Replay completed duoc chap nhan: broker() dong
  401-410, status completed, failed, running, unknown tu
  request deu tra thang recorded response, khong fetch result;
  status accepted moi fetch result. broker_code_exec dong
  497-504: completed tra envelope voi next_seq seq+1.
  Test test_real_broker_replay_completed_accepted dong
  1188-1210 pin, khong co lenh broker-result nao chay. M-F3
  lat.
- (d) Running/failed/unknown deu raise voi seq tien: xem
  (a) dong 505-519, cong test dong 1227-1299. M-F4, M-F5 lat.
- (e) Recount truoc fallback cho ca 2 variant: closure
  _recount_before_fallback dong 1070-1085, nam ngoai nhanh
  `if variant == 'set_value'`, chay count_check va refuse
  khi count khac 0 hoac loi (count -1). Truyen vao
  _code_exec_send dong 1087-1090. Fill khong co pre_count
  nhung recount van chay 1 lan (test dong 1332-1355 pin
  len(count_calls) bang 1, khong co pre_count); set_value
  co pre_count cong recount bang 2 lan dem (test dong
  1300-1330 pin len bang 2). M-F6 lat ca hai test.
- (f) Bo validate program_variant trung lap: chi con 1 lan
  kiem tra dong 258-261 trong __init__. Khong con block
  thu hai.
- (g) Docstring chi neu CLI subcommand: dong 14-21, neu
  subcommand start, request, result, finish, va noi ro
  harness khong bao gio goi _client_start,
  _client_start_with_wait, _client_finish, broker_start
  khong busy-wait. Prep log section 5.2 tai cho dong
  644-652 cung co ghi chu tuong tu.

### V-C6, doc bang grep: PASS

- HEAD ed4fcd4: grep -c tra A3 drill 1, A4 drill 1, A5 drill
  2, worker log 12, prep log 10. Grep 0400e86 trong 3 drill
  tra 0 hit. Cac 0400e86 con lai trong worker log (sections
  0-9) va prep log (5.1 pre-migrate, 9.2 lich su) deu la
  lich su co ghi ngay, dung nhu worker log 10.8 da noi.
- Importlib 103-106 o ca 3 cho: worker log dong 177,
  prep log dong 210 (section 3.2) va dong 916 (section 9.1).
  Doi chieu source: scripts/sync-installed.py dong 103
  spec, 104 module, 106 exec_module, dong 107 trong, lock
  dong 115. Dung.
- Prep log section 4/5 sua tai cho cong pointer: section 4
  pointer dong 355-357, so overlay tai cho 693 dong, Daemon
  238, serve 377, _ensure_daemon 489, cmd_acquire 525, khop
  source (overlay.py 693 dong, Daemon dong 238, serve 377,
  _ensure_daemon 489, cmd_acquire 525). Section 5 pointer
  dong 562-565, so post-migrate broker_code_exec 455,
  _code_exec_send 563, oneshot_code_exec 648, call site 1087,
  file 1400 dong, khop source (grep def: 455, 563, 648, 1400
  dong). Section 9.4 dong 989-1001 ghi ro cac sua nay.
- Khong dau gach ngang dai: kiem tra bang Python tren ca 7
  file cua commit 87efda9 (a3 drill, a4 probe, a5 drill,
  worker log, prep log, s2_flip_live.py,
  test_s2_flip_wiring.py), ket qua no-em va no-en ca 7 file.

### V-C7, drill: PASS

(a) A5 fallback drill:

- Step 3 script standalone: trich 1 code block tu drill,
  `python3 -m py_compile` exit 0, STEP3_COMPILE_OK, thoi gian
  2026-11-23 00:47:53 +07. Script co seed, pre-count, act
  envelope cong finish line JSONL, V12, sleep 10s, delayed
  count, dung hinh step 8. Khong chay live.
- Step 1 va 5 co --chromium-set-value (dong 74, 224 cua
  drill). Precondition 3 tro ve step 1 (dong 41-43). Run JSON
  khong co truong broker_finish, noi 2 lan (dong 230-231,
  289-290). Doi chieu code: run() dong 1252 goi
  `self.broker_finish(lease)` ma khong gan gia tri tra ve,
  nen run JSON that su khong co truong do. Dung.
- scripts/ssh-laptop-mux.sh ton tai trong worktree;
  ~/workspace/ssh-laptop.sh khong ton tai (ls rc 2), dung
  nhu drill noi. build_program_set_value ton tai dong 170.

(b) A3 wedge drill, doi chieu scripts/session_remote.py tai
87efda9:

- So dong trich dan khop het: _status 871, _result 847,
  _request 790, _client_finish 1563, _fail_task 926,
  _task_recovery_required 933, IDLE_TIMEOUT 300.0 dong 38,
  REQUEST_TIMEOUT 120.0 dong 40.
- Lock probe: lenh start fail fast (khong --wait) cu the
  trong drill; _start dong 630-636 tra busy khi task dang
  chay. Ky vong `{"ok": false, "error": "busy"}` rc 1, dung.
  Cau owner_lock chi xuat hien o duong `cu session` truc
  tiep, khong phai o broker start. Dung.
- Poll status: _status dong 871-919 tra cac truong state,
  owner, generation, driver, guardian, cancelled,
  cancellation_state, recovery, next_sequence,
  active_sequence, error, stop_reason. Khong co truong
  last_activity trong body tra ve (last_activity chi la
  thuoc tinh noi bo cua task). Dung. Driver van ready khi
  SIGSTOP: tick() dong 994-1029 chi doi driver thanh failed
  khi process poll() khac None (da exit) hoac worker loi;
  SIGSTOP khong lam poll() tra ve. Dung.
- Poll result: _request dong 790-836 tra accepted ngay
  (worker thread start ngay sau do), busy neu da co request
  active. Chi _result dong 847-870 moi doi toi
  request_timeout 120s khi status running. Dung.
- Finish tra cleanup_pending sau 120s: _client_finish dong
  1563-1581, chi tra khi state finished/failed VA guardian
  khong active, neu khong sau 120s tra `{"ok": false,
  "status": "cleaning", "error": "cleanup_pending"}`. Dung
  voi tinh huong guardian van active vi snapshot con giu.
- Fresh start buoc 6 tra recovery_required: _start dong
  637-640, task failed cong _task_recovery_required true
  (process chet, snapshot con) thi tra recovery_required;
  snapshot con cung tra recovery_required dong 647-654. Chi
  duoc chap nhan sau buoc 7. Dung.
- Recover truoc, cam unlink session.json tay: `cu.py recover`
  dong 3110 goi cursor_session.recover (dong 103-120), lay
  owner lock, request_stop, restore; restore() dong 39-70
  unlink session.json khi thanh cong va tra False neu
  snapshot khong phuc hoi duoc. Docstring restore noi ro
  khong duoc lang lang bo desktop chua phuc hoi. Dung.
- Lay PID/PGID qua cay process cua relay: lenh `ps --ppid
  <relay-pid>` cong `ps -o pid,pgid,args -p <driver-pid>`
  cu the trong drill, kill chi theo PID da ghi. Khong chay
  live nen cay process that chua duoc kiem chung truc tiep,
  nhung lenh co the chay duoc nhu viet.

(c) A4 CB-10 probe:

- Launcher Y6e improvements/worker-y6e-nested-load-test.sh
  ton tai, 291 dong. Runner Y6b v2
  improvements/worker-y6b-run-nested-wayland-v2.sh ton tai,
  973 dong. Khop so dong probe neu.
- Commit 915121d ton tai, message: "Y6e: hyprglass rebuild
  risk review GO, build done, nested load test LOADED",
  hyprglass.so 34,440,704 B md5 78ac1023, nested load test
  21:57 LOADED. Md5 day du 78ac102337ca70842bf604b56c6f4c8e
  co trong improvements/worker-y6e-rebuild-load-log.md dong
  492 va 575. Dung.
- Backup 1 dead ABI: duong dan, 26,643,888 B, sha256
  2671d4ac41941ca62ae8100fc3b57bf3153bf6def893334f3a8ecbc1ea0145d5
  co trong improvements/worker-y6-council-b-evidence.md dong
  81. Backup 2: 30,622,520 B, sha256
  ddfff1c2f2cebb66e10b85a739beae0c7c562ccf9d78e3250647c07f8f31fa8b,
  dong 82 cung file. Dung. Ca hai duong dan .so tren laptop
  khong ton tai trong VM nay (ls rc 2), dung nhu probe noi
  (.so chi con tren laptop); hash phai verify tren laptop
  truoc khi load, probe ghi ro nhu vay.
- Khong ton tai script driver LIQUID standalone trong repo:
  `git ls-files | grep -i liquid` chi tra docs/liquid-glass.md
  (tai lieu, khong phai script driver). Dung.
- Runner tu in verdict: ARM A outcome, ARM B outcome,
  SUMMARY (armA_outcome, armA_diff, armB_outcome,
  armB_pill_diff, armB_bg_diff, armB_pill_only), VERDICT
  REPRODUCED, INCONCLUSIVE, VOID, NOT reproduced (dong
  851-967). Header dong 16 cua runner van noi "loads backup
  1", probe ghi dung la dong nay loi thoi. Ca hai script deu
  bat Y6_HANDOVER_CONFIRMED=1 (runner dong 302, launcher
  dong 85). E1 [indicator-metrics] co o scripts/indicator.py
  dong 30; mpv --loop=inf --no-audio --fullscreen co o runner
  dong 731. Dung.

### V-C8, 3 exec exit nonzero trong run cua worker sua: 2 xac nhan lanh, 1 khong dinh vi duoc

Tim trong worker log section 10.8 va script mutation con
song o /tmp/b24-fix-mutations.py, chi dinh vi duoc 2 exit
nonzero, ca hai deu co chu y, khong phai loi that:

1. Lan chay mutation F-C5 dau tien, 00:39:05 +07: script
   mutation exit nonzero vi M-F5 khong lat duoc target
   (test pass nho catch-all raise). Day la failure co chu
   y cua mutation gate, no bat duoc mot test hollow, dan
   toi siet test roi chay lai sach 00:39:21 +07. Da duoc
   verify lai o V-C4(c): test siet bat duoc M-F5.
2. F-C6 dash grep rc 1, zero hit, 00:41-00:42 +07: grep tra
   rc 1 khi khong co match, la ket qua mong doi (khong co
   dau gach ngang dai), khong phai loi.

Exit nonzero thu ba khong dinh vi duoc tu bat ky file nao
trong worktree hay script /tmp con song: lan chay mutation
cuoi cung cua worker (script /tmp/b24-fix-mutations.py)
exit 0 khi chay lai o V-C4(b) tren commit 87efda9. Vay claim
"3 exec exit nonzero" khong xac nhan duoc tron ven tu repo;
2 cai tim thay deu lanh. Day la gioi han cua bang chung,
khong phai finding chong lai fix, vi khong co check san pham
nao that bai. Ghi lai de coordinator doi chieu voi session
cua worker sua neu can.

### V-C9, kim tu thap tin tuong

- Check xac dinh (tot): probe-before-fallback, recount, seq
  mang theo exception, test broker that cong mutation gate.
  Cac fix code deu o muc nay, khong dua vao text rule.
- Thiet ke lam sai thanh khong the (tot nhat, da lam):
  _BrokerSendConsumed mang broker_next_seq nen caller khong
  the dung lai seq cu; fallback chi chay sau probe cong
  recount, khong co duong fallback mu.
- Text rule con lai (yeu nhat, ghi ro): moi toa do trong doc
  (HEAD label, so dong overlay, importlib, so dong
  s2_flip_live) chi la text, khong co check tu dong nao pin
  chung. Chi co reviewer grep moi bat duoc drift. Neu doc
  drift sau nay, test suite se khong bao. Tuong tu, script
  step 3 cua drill A5 chi duoc compile-check, lan chay live
  dau tien chinh la drill duoi GO.
- Lua chon thiet ke co chu y, khong phai thieu sot: probe
  khong tra loi duoc thi giu seq va khong fallback; operator
  rerun --transport oneshot hoac script step 3. Fail-closed,
  chap nhan duoc.
- Huong manh hon ma council 2 da neu (re-issue cung request
  qua broker thay vi fallback oneshot) khong duoc chon;
  thiet ke hien tai tu choi fallback khi khong chac, dat
  muc tieu an toan tuong duong cho truong hop nay.

## 2. Doi chieu finding cua 4 review (moi finding da co fix va verify)

- Council 1 F1 (seq reuse): fix bang _BrokerSendConsumed
  cong test hai browser, verify V-C4 M-F1, V-C5(a). F2 (A5
  step 3): viet lai standalone, verify V-C7(a). F3
  (set-value): step 1/5 co flag, verify V-C7(a). F4 (HEAD):
  ed4fcd4, verify V-C6. F5 (section 4/5): sua tai cho cong
  pointer, verify V-C6. F6 (A3 lenh exact): lenh cu the,
  verify V-C7(b). F7 (A4 duong dan, hash): verify V-C7(c).
  F8 (docstring): subcommand only, verify V-C5(g).
- Council 2 F1 (probe truoc fallback): fix bang probe cong
  recount, verify V-C4 M-F2/M-F6, V-C5(b)(e). F2 (dup
  validation): bo, verify V-C5(f). F3 (HEAD): verify V-C6.
  F4 (importlib): 103-106, verify V-C6. F5 (comment cong
  seq): comment except handler viet lai dung, verify
  V-C5(a).
- Council 3 F1 (HEAD): verify V-C6. F2 (section 4/5):
  verify V-C6. F3 (lock probe): lenh exact, verify V-C7(b).
  F4 (probe truoc fallback): nhu council 2 F1. F5 (dup
  validation): verify V-C5(f).
- Redteam F1 (phan loai pre-dispatch): probe, verify V-C5(b).
  F2 (status running/failed nuot): raise Consumed, verify
  V-C5(a)(d). F3 (fallback khong dem lai): recount, verify
  V-C5(e). F4 (test khong bao broker that): test broker that
  cong mutation, verify V-C4. F5 (A5 drill): verify V-C7(a).
  F6 (A3 drill): verify V-C7(b). F7 (A4 probe): verify
  V-C7(c). F8 (HEAD): verify V-C6.

## 3. Observations (khong phai finding, khong chan PASS)

- O1: duong follow-on sau probe-unavailable chua co test
  truc tiep. Khi probe unavailable, seq duoc giu; neu broker
  that ra da tieu thu seq va hoi phuc, browser ke tiep dung
  lai seq se gap conflict, probe tim thay record, raise
  Consumed, khong fallback. An toan theo thiet ke nhung
  chuoi nay chua duoc test nao pin.
- O2: broker() neu output request khong parse duoc JSON thi
  json.loads raise ValueError, khong phai RuntimeError, nen
  broker_code_exec khong chuyen doi no; no thoat ra
  _send_browser_inner except, outcome error, seq giu nguyen.
  Hanh vi an toan nhung chua co test.
- O3: baseline dung la ed4fcd4, khong phai HEAD hien tai
  (xem V-C2). Ai chay lai `git archive HEAD` se duoc 60 test,
  khong phai 38.
- O4: /tmp day 99% luc verify (10M trong), do cac ban sao
  scratch cu cua cac lane truoc; verifier dung scratch o
  ~/workspace thay vi /tmp. Khong xoa file cua lane khac.
- O5: test run tao __pycache__ trong worktree; verifier xoa
  truoc khi commit log.

## 4. Ket luan: PASS

Fix commit 87efda9 vuot moi muc verify: compile OK, 60 test
OK tren baseline 38 OK (delta dung 22), neighbour 163 OK,
8/8 mutation lat dung test dich (gom ca script mutation cua
chinh worker sua chay lai sach), tung fix code co dong cu the,
doc va drill doi chieu dung voi source. Khong co finding.
Live proof van can GO nhu worker log da noi, khong thuoc
pham vi verify nay.

Thoi gian verify: nhan task 2026-11-23 00:44:40 +07, check
chay 00:45:12-00:49:40 +07, viet log xong truoc commit.
Hash co so: 87efda9.
