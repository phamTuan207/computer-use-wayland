# Redteam B2-4 log (step 10): pha do A5 migrate, holder fix, 3 drill

Role: redteam, khong sua code cua worker, khong khen, chi pha.
Worktree: ~/workspace/mochi-b2-4-work. HEAD luc bat dau task:
ed4fcd4 (ed4fcd49775db4c61f5238ce10ea515bcbd6e294), thay doi chua
commit cua worker: M scripts/s2_flip_live.py, M
tests/test_s2_flip_wiring.py, M
improvements/worker-click5-step10-prep-log.md, 4 file moi
improvements/mochi-b2-4-a3-wedge-drill.md,
improvements/mochi-b2-4-a4-cb10-probe.md,
improvements/mochi-b2-4-a5-fallback-drill.md,
improvements/mochi-b2-4-worker-log.md.
Khong commit file nguoi khac, khong push, khong chay live, khong
xoa file, khong dong hoac navigate tab trinh duyet, khong dung
ydotool. Khong dau gach ngang dai, chi dau phay, dau cham, gach
noi ngan. Khong thong tin ca nhan. Moi claim co du 4: lenh,
output, commit hash, gio Viet Nam cong elapsed. Bat dau 2026-11-23
00:20 +07. Ghi chu: giua luc lam, HEAD dich sang 43ac912
(00:25:41 +07, commit "B2-4 council 2 review: CHUA PASS,
fallback pre-dispatch proof gap F1", chi them file
improvements/mochi-b2-4-council-2-log.md, khong cham file cua
worker hay file nay). Toi khong doc file council 2 do; bang
chung duoi day la tu cac check toi tu chay.

## 0. Evidence contract (viet truoc moi check tan cong)

Moi check duoi day chi tinh neu dieu kien hoan thanh duoc viet
truoc khi chay, gom lenh tan cong, output mong doi neu pha duoc,
hash commit, log thoi gian. Khong viet truoc thi check do khong
tinh. "Inconclusive" la trung thuc, KHONG phai pass. Ket luan chi
1 trong 3: PHA DUOC, KHONG PHA DUOC, INCONCLUSIVE.

- A1, double-send qua phan loai loi request sai. Lenh: script
  /tmp/b24-rt/attack.py, mock Harness.broker ghi dispatch roi raise
  RuntimeError("broker request failed rc=1: ssh lost"), mock
  oneshot ghi so lan goi, goi _code_exec_send voi lease va seq 3.
  Pha duoc neu oneshot_calls bang 1 mac du broker da dispatch 1,
  tuc tong so send bang 2 cho cung message. Hash: ed4fcd4.
- A2, replay completed bi doc nham thanh tu choi. Lenh: script
  /tmp/b24-rt/attack2.py, mock Harness.ssh tra ve status completed
  kem envelope cho broker request that, goi broker roi
  _code_exec_send. Pha duoc neu broker raise
  _BrokerSendNotAccepted thay vi tra envelope, va fallback
  oneshot chay 1 lan. Hash: ed4fcd4.
- A3, status running hoac failed bi nuot. Lenh: script
  /tmp/b24-rt/attack.py, mock broker tra ve status running khong co
  response, roi status failed kem envelope, goi broker_code_exec.
  Pha duoc neu running tra ve envelope {} va next_seq bang seq
  cong 1 thay vi raise, hoac failed tra ve envelope nhu binh
  thuong. Hash: ed4fcd4.
- A4, fallback khong chay lai count_check. Lenh: script
  /tmp/b24-rt/attack.py, mock count_check dem so lan goi, mock
  broker raise "broker request not accepted" sau khi da dispatch,
  mock oneshot, goi send_browser brave voi lease va seq 3. Pha
  duoc neu count_calls bang 1 (chi truoc broker) trong khi oneshot
  chay 1 lan, tuc khong co lan dem nao truoc fallback. Hash:
  ed4fcd4.
- A5, test rong, dot bien tren ban sao /tmp. Lenh: cp worktree
  sang /tmp/b24-rt/mut, sua tung cho mot (broker accepted check,
  unknown status check, duong broker that), chay 8 test moi
  (BrokerCodeExecTests) bang unittest. Pha duoc neu mot dot bien
  lam hong duong broker that ma 8 test van PASS. Doi chung: dot
  bien bo disabled check phai lam test_disabled... FAIL, neu
  khong thi bo test cung khong bat duoc gi. Hash: ed4fcd4.
- A6, run() oneshot voi relay chet la khong the. Lenh: script
  /tmp/b24-rt/attack2.py, mock broker_start raise RuntimeError,
  mock mux_baseline, mock seed_scratch, mock oneshot dem so lan
  goi, goi Harness(transport="oneshot").run(["chromium"]) voi
  dry_run. Pha duoc neu run() raise thay vi tra run JSON va
  oneshot_calls bang 0, tuc buoc 3 cua A5 drill khong chay duoc
  nhu viet. Hash: ed4fcd4.
- A7, A5 drill doi delayed count o duong fill. Lenh: script
  /tmp/b24-rt/attack.py, import s2_flip_live tu worktree,
  Harness mac dinh, goi variant_for("chromium") va
  delayed_targets voi ket qua chromium fill da sent. Pha duoc neu
  variant bang fill va delayed_targets bang [], tuc drill doi
  delayed count 1 o run 900, 901, 902 chromium la khong the co.
  Hash: ed4fcd4.
- A8, holder thu 6 va toa do section 9. Lenh: grep -rn
  owner_lock, _session_lock, flock, cursor.lock, importlib tren
  scripts, cong kiem tra tung toa do section 9 tai HEAD ed4fcd4.
  Pha duoc neu co holder thu 6, hoac mot toa do sai, hoac noi
  khac trong repo van ghi 4 holder. Hash: ed4fcd4.
- A9, A3 wedge drill sai ky vong hoac thieu buoc. Lenh: doc
  session_remote.py cac ham _start, _result, _status,
  _client_finish, _task_recovery_required, _fail_task, cong grep
  so dong duoc trich dan trong drill. Pha duoc neu mot ky vong
  (lock refusal message, driver not ready, fresh start duoc chap
  nhan o buoc 6, finish sach o buoc 5) trai voi code, hoac buoc
  tim PID driver khong co lenh chay duoc. Hash: ed4fcd4.
- A10, A4 CB-10 probe thieu tien quyet chay duoc. Lenh: kiem tra
  ton tai commit 915121d, file decision doc, 2 duong dan backup
  .so, launcher Y6e, hash .so trong probe file. Pha duoc neu mot
  thu duoc trich dan khong ton tai, hoac buoc 1 den 4 khong neu
  lenh, duong dan, hash cu the de chay. Hash: ed4fcd4.

## 1. Ket luan: PHA DUOC

Pha duoc 7 nhom loi (F1-F7), co bang chung chay duoc moi loi.
Khong pha duoc: holder 5 va toan bo toa do section 9, duong
disabled envelope dang da biet, heredoc envelope, 46 test goc.
Gioi han pham vi that: khong chay live, nen double-send live
chua duoc quan sat truc tiep; F1 chung minh o muc code cong
mock, kem cua so live cu the o muc 2 (F1).

## 2. Bang chung chi tiet theo check

### A1, PHA DUOC, phan loai "broker request failed" thanh pre-dispatch la sai

- Lenh: `python3 /tmp/b24-rt/attack.py`. Output: `A1 dispatch=1
  oneshot=1 transport=broker-fallback-oneshot total_sends=2`,
  kem dong log cua code: `broker code-exec not accepted (broker
  request failed rc=1: ssh lost); one-shot fallback, no send ran
  yet`. Thoi gian: 2026-11-23 00:23:54 +07, elapsed 0.002s cho
  ca script attack.py. Hash: ed4fcd4.
- Giai thich: broker_code_exec chi nhin tien to chuoi
  "broker request failed" de doi sang _BrokerSendNotAccepted
  (s2_flip_live.py, broker_code_exec). Cung chuoi do xay ra ca
  khi request chua dispatch (broker chet) va khi SSH dut sau khi
  broker da dispatch (rc khac 0, timeout, stdout mat). Code
  khong hoi lai broker (khong goi `result --sequence N`, la duong
  replay san co cua broker: cung seq cong cung digest thi tra
  response da ghi) truoc khi fallback, nen cau "no send ran yet"
  la doan, khong phai chung minh.
- Cua so live: guardian giu owner_lock suot session
  (cursor_session.py guardian, `with owner_lock():`), nen
  oneshot chay dong thoi khi broker session con song se chet o
  guardian startup, khong double-send ngay. Double-send can cua
  so lock da nha: driver chet sau khi send (session_continues
  False, guardian don dep, lock nha) trong khi SSH mat, hoac
  relay restart sau dispatch. Luc do fallback oneshot mo session
  moi va gui lai cung message. Voi Chromium fill, khong co
  pre-count nao truoc fallback (xem F3), nen khong gi chan.
- Them bang chung duong that: lenh
  `python3 /tmp/b24-rt/attack2.py`, mock ssh tra rc 1 cho
  broker request that. Output: `A2b real broker() raised
  RuntimeError: broker request failed rc=1:  mux broken`.
  Thoi gian: 2026-11-23 00:24:15 +07. Hash: ed4fcd4.

### A2, PHA DUOC, replay completed bi doc nham thanh tu choi

- Lenh: `python3 /tmp/b24-rt/attack2.py`, mock ssh tra ve cho
  broker request that JSON `{"ok": true, "status": "completed",
  "sequence": 3, "response": {"returncode": 0,
  "session_continues": true, "result": {...ok True...}}}`.
  Output: `A2 real broker() raised RuntimeError: broker request
  not accepted: {"ok": true, "status": "completed", ...}`, roi
  `A2 _code_exec_send transport=broker-fallback-oneshot
  oneshot=1 envelope_ok=True`. Thoi gian: 2026-11-23 00:24:15
  +07. Hash: ed4fcd4.
- Giai thich: broker tra status completed la duong replay hop
  le cua no (session_remote.py _request, cung sequence cong cung
  digest thi tra _record_response, status la completed, failed
  hoac unknown, khong phai accepted). broker() o s2_flip_live.py
  chi chap nhan status accepted, nen replay thanh cong bi doi
  thanh tu choi, roi _code_exec_send fallback oneshot gui lai
  message broker vua gui xong. Day la double-send truc tiep
  theo thiet ke cua broker, khong can gia thiet SSH dut.
- Dieu kien kich hoat o run() hien tai: run() khong goi lai cung
  seq cho cung chuong trinh, nen replay chi xay ra neu co retry
  hoac goi lai broker_code_exec; nhung code hien tai bien bat
  ky replay nao thanh fallback, nen moi retry tuong lai deu
  double-send. Cung gioi han lock nhu F1 ap dung cho truong hop
  session con song.

### A3, PHA DUOC, status running va failed bi nuot, seq tien sai

- Lenh: `python3 /tmp/b24-rt/attack.py`. Output: `A3 running ->
  envelope={} next_seq=4 wall=30.0` va `A3 failed -> envelope=
  {'ok': False, 'error': 'driver died', 'error_type': None,
  'log': []} next_seq=4`. Thoi gian: 2026-11-23 00:23:54 +07.
  Hash: ed4fcd4.
- Giai thich: broker_code_exec chi kiem tra status unknown.
  Voi status running (broker _result het REQUEST_TIMEOUT 120s
  van tra _record_response, chua co response), driver_result
  tra {} (response.get('response') or {}), ham tra envelope {}
  va seq cong 1 nhu the send da xong. Voi status failed
  (driver chet kieu terminal, session_continues False), ham van
  tra envelope nhu binh thuong. _send_browser_inner sau do chi
  dua vao V12 de cham outcome, nen mot send chet terminal van
  co the duoc cham sent neu V12 tim thay message, va run() tiep
  tuc browser ke tiep voi seq da tien trong khi broker van giu
  record active o seq cu: request ke tiep gap sequence_gap hoac
  busy (session_remote.py _request), roi lai roi vao fallback
  oneshot theo F1. Day la hieu ung domino tu mot status khong
  duoc xu ly.

### A4, PHA DUOC, fallback khong chay lai count_check

- Lenh: `python3 /tmp/b24-rt/attack.py`. Output: `A4
  count_calls=1 dispatch=1 oneshot=1 outcome=sent
  transport=broker-fallback-oneshot`. Thoi gian: 2026-11-23
  00:23:54 +07. Hash: ed4fcd4.
- Giai thich: count_check chi chay mot lan trong
  _send_browser_inner truoc _code_exec_send, cho duong
  set_value. Nhanh fallback trong _code_exec_send khong dem
  lai truoc khi gui oneshot. Ly do worker ghi trong docstring
  ("pre-send count check already ran before this call") sai ve
  mat thoi gian: lan dem do xay ra truoc broker attempt, khong
  phai truoc fallback; message hoan toan co the da duoc gui boi
  broker attempt o giua. Voi Chromium fill thi tham chi khong
  co lan dem nao (khong co pre_count), nen fallback la duong
  gui mu.

### A5, PHA DUOC, 8 test moi rong doi voi duong broker that va status unknown

- Lenh co so: cp worktree sang /tmp/b24-rt/mutbase, chay
  `python3 -m unittest tests.test_s2_flip_wiring.BrokerCodeExecTests`.
  Output co so: `Ran 8 tests in 0.004s, OK`. Thoi gian:
  2026-11-23 00:24:27 +07. Hash: ed4fcd4. Ca file goc van 46
  OK (xem muc 4).
- Dot bien M1: broker() chap nhan bat ky status nao mien ok
  True (bo kiem tra status accepted). Ket qua: `Ran 8 tests in
  0.034s, OK`. Thoi gian: 2026-11-23 00:24:33 +07.
- Dot bien M2: kiem tra unknown doi thanh 'UNKNOWN' (khong bao
  gio khop, tuc bo raise unknown). Ket qua: `Ran 8 tests in
  0.004s, OK`. Khong co test nao cho status unknown.
- Dot bien M4: them `--bogus-flag` vao lenh broker request that
  trong broker() (duong SSH that hong). Ket qua: `Ran 8 tests
  in 0.004s, OK`. Ca 8 test mock hoan toan Harness.broker, nen
  khong test nao cham vao broker() that, heredoc envelope, env
  file, hay tham so CLI session_remote.
- Doi chung M3: doi disabled check thanh 'Disabled'. Ket qua:
  `FAILED (failures=1)`. Test disabled that su bat duoc dot
  bien nay, nen bo test khong phai vo dung hoan toan; lo hong
  nam o phan khong duoc bao phu (broker() that, unknown,
  running, failed, replay).
- Ket luan A5: test moi chi chung minh logic dispatch tren
  mock, khong chung minh duong broker that hay xu ly status.

### A6, PHA DUOC, run() oneshot voi relay chet la khong the, buoc 3 A5 drill sai

- Lenh: `python3 /tmp/b24-rt/attack2.py`. Output: `A6 run
  raised RuntimeError: broker start failed rc=1:
  broker_unavailable ; oneshot=0 broker_start=1`. Thoi gian:
  2026-11-23 00:24:15 +07. Hash: ed4fcd4.
- Giai thich: Harness.run() luon goi broker_start truoc, roi
  moi routing (tabs, observe qua broker), khong co nhanh nao
  bo qua broker_start khi transport la oneshot. Voi relay da
  stop (buoc 2 cua A5 drill), run() raise truoc khi bat ky send
  nao chay, main crash, khong co run JSON. Buoc 3 cua drill
  (`--run 901 --dry-run --browser chromium --transport oneshot`,
  ky vong run JSON transport oneshot, outcome sent, V12 found)
  khong the chay nhu viet. Duong oneshot chi doi transport cua
  send, khong phai duong chay doc lap khi relay chet.

### A7, PHA DUOC, A5 drill doi delayed count va pre-count o duong fill

- Lenh: `python3 /tmp/b24-rt/attack.py`. Output: `A7 chromium
  variant=fill brave variant=set_value` va `A7
  delayed_targets chromium-only=[] both=[('brave', 'TAB1',
  'M1')]`. Thoi gian: 2026-11-23 00:23:54 +07. Hash: ed4fcd4.
- Giai thich: delayed_targets chi lay browser set_value co
  target_id va message; Chromium mac dinh la fill nen khong
  bao gio duoc dem lai, results khong co khoa delayed_count
  cho chromium. Tuong tu, pre_count chi chay cho set_value
  trong _send_browser_inner. A5 drill doi o buoc 1, 3, 5 cho
  `--browser chromium` (khong kem --chromium-set-value):
  "delayed count 1", buoc 3 them "pre-count 0". Ca hai tieu chi
  deu khong the co tren duong fill. Tieu chi pass 1, 2, 6 cua
  drill vi the khong the dat nhu viet; drill can them
  --chromium-set-value hoac doi tieu chi theo variant that.

### A8, KHONG PHA DUOC, holder 5 dung, toa do section 9 dung het

- Lenh: `grep -rn "owner_lock" scripts/ --include="*.py"`.
  Output: 8 site, dung nhu worker noi: 5 ngoai (activate-
  cursor-guard.py 63, activate-session-backend.py 72, setup.py
  314, visuals.py 242, sync-installed.py 115) cong 3 noi bo
  cursor_session.py (104, 125, 142). Thoi gian: 2026-11-23
  00:24:39 +07. Hash: ed4fcd4.
- Kiem tra holder thu 6 kieu khac: `_session_lock` chi o
  sync-installed.py (dinh nghia 110, dung 1259); cac flock khac
  la khoa khac (cu.py 2661 desktop.lock, overlay.py 81 holders
  lock, session_remote.py 1142 relay lock, zen_cli.py va
  zen_dom.py khoa rieng), khong phai owner_lock. importlib o
  activate-session-backend.py chi load activate-glass.py va
  activate-cursor-guard.py (da dem), khong them holder moi.
  Grep "four holder" tren repo chi thay cac hit khong lien
  quan va chinh worker log mo ta viec sua; khong con file nao
  ghi 4 holder.
- Toa do section 9 kiem tra tung dong tai HEAD ed4fcd4, tat ca
  dung: cursor_session.py prepare 22, request_stop 27, restore
  39, owner_lock 73, drain_input 87, SessionVisuals 93, recover
  103, stop 120, guardian 136, stop_group 208,
  terminate_driver 220, supervise 228; session_remote.py
  _launch 520, _client_start 1456, _client_start_with_wait
  1494, _client_finish 1563, file 1681 dong; cu.py
  stop_session_on_error request_stop 3460 (import 3459), stop
  3105, supervise 3109, recover 3110, request_stop 3114;
  cancel_hotkey.py latch_present 59, latch 120,
  cancellation_status 157, cancellation_message 197, resume
  unlink 222, request_stop 220; first_action.py acquire_overlay
  116, overlay_visible 150, release_overlay 167, import overlay
  978; session_cleanup.py guardian doc 5-6, holder check 62-69;
  overlay.py _log 48 den main 659, ke ca method Daemon
  _spawn_native 245, serve 377; ssh_mux.py run 303; s2_flip_live
  truoc migrate tai 0400e86 oneshot_code_exec 388, call site
  794; sau migrate broker_code_exec 423, _code_exec_send 467,
  oneshot_code_exec 506, call site 928, file 1230 dong.
- Chi co nhan HEAD loi thoi: worker log va prep log section 9
  ghi HEAD 0400e86, trong khi task giao HEAD ed4fcd4. Gia tri
  van dung vi 3 commit giua (59f8a44, cac7d74, ed4fcd4) chi
  cham zen_backend.py, zen_pointer.py va file f4diag, khong
  cham cac file co toa do. Day la loi nhan, khong phai loi toa
  do (xem F8).

### A9, PHA DUOC, A3 wedge drill sai ky vong, thieu PID, mau thuan phuc hoi

- Co so code, session_remote.py tai HEAD ed4fcd4, doc truoc
  khi ket luan: _fail_task 926, _task_recovery_required 933,
  _client_start_with_wait 1494, IDLE_TIMEOUT 38, REQUEST_TIMEOUT
  40, _client_with_lease request timeout 60 (dong 1560). Cac
  so dong trich dan trong drill dung.
- F6a, lock limb sai message va lenh mo ho: _start tra
  `{'ok': False, 'error': 'busy'}` khi task dang chay, khong
  phai message owner_lock ("another automation session or
  plugin activation is active"). Message do chi xuat hien khi
  chay truc tiep `cu session` (guardian startup failed, boc
  trong RuntimeError). Drill buoc 1 noi "second start attempt"
  khong neu lenh, nen nguoi lam theo broker start se nhan busy
  va theo luat abort ("lock refusal khong xay ra thi STOP") se
  dung mot run khoe manh vi ly do sai.
- F6b, buoc 3 doi hoi khong quan sat duoc: _status khong co
  truong last_activity nao (cac truong la state, owner,
  generation, driver, guardian, cancelled, cancellation_state,
  recovery, next_sequence, active_sequence, error,
  stop_reason). Driver van la 'ready' khi process bi SIGSTOP
  (tick chi doi driver khi process exit hoac request worker loi;
  SIGSTOP khong doi truong nay), nen "driver not ready" la sai.
  "active_sequence stuck" thi dung.
- F6c, buoc 3 nham request voi result: _request tra accepted
  ngay qua worker thread; request timeout cua client la 60s,
  result moi doi REQUEST_TIMEOUT cong 5. Mot request trong
  wedge se nhan accepted (neu chua co request active) hoac busy
  (neu da co), khong phai "no answer within 120s". Khoang
  khong tra loi ap dung cho result, khong phai request.
- F6d, buoc 5 finish khong the sach: sau buoc 4 set cancel
  latch, tick cua broker (process rieng, khong bi STOP) se
  _fail_task(task, 'cancelled'), nhung guardian van active vi
  snapshot con giu, nen _client_finish poll den het 120s roi
  tra cleanup_pending (xem _client_finish 1563-1581). "finish
  with the owner's lease (120s timeout)" khong tra ve sach o
  diem do.
- F6e, buoc 6 doi fresh start duoc chap nhan la sai thu tu:
  _start kiem tra task failed cong _task_recovery_required
  (snapshot con, process chet thi True) va retained snapshot,
  deu tra recovery_required, khong phai acceptance. Acceptance
  chi co sau buoc 7 phuc hoi. Thu tu drill dao nguoc.
- F6f, buoc 7 mau thuan: cung mot buoc vua noi "unlink
  session.json if retained" vua noi "If a snapshot is retained,
  run computer-use recover before the cleanup check". Unlink
  tay va recover la hai duong loai nhau; file khong noi cai nao
  truoc, cai nao dung khi nao.
- F6g, buoc 2 khong co cach lay PID: _status khong expose
  driver PID hay PGID. Drill khong neu lenh nao de ghi PID va
  process group o buoc 1, trong khi buoc 5 cam kill theo
  pattern. Nguoi lam khong co duong xac dinh PID duoc phep.

### A10, PHA DUOC, A4 CB-10 probe thieu tien quyet de chay

- Kiem tra su that dung: commit 915121d ton tai ("Y6e:
  hyprglass rebuild risk review GO, build done, nested load
  test LOADED"); docs/decision-2-2-3-hyprglass-test-20261121.md
  ton tai; ong chon C 18:24 co trong docs/
  zen-error-fix-todolist-20261121.md dong 74 va dong 34; Y6e
  rebuild .so md5 78ac1023, 34,440,704 B, trong message commit
  915121d. Thoi gian: 2026-11-23 00:25:29 den 00:25:40 +07.
  Hash: ed4fcd4 (luc kiem tra, HEAD sau do dich sang 43ac912,
  khong anh huong cac file nay).
- Pha duoc o tinh chay duoc: buoc 1 noi "hyprglass loaded from
  the backup .so (verify the .so hash before loading; record
  it)" nhung khong neu duong dan day du hay hash ky vong. Hai
  duong dan trong file dang rut gon ("full-1791544423/native/
  hyprglass.so", "sync-20261116-230254-783160-a9a24690/trees/
  native/hyprglass.so") khong ton tai trong worktree (ls bao
  No such file or directory); duong dan day du nam tren laptop
  (~/.local/share/agent-computer-use/backups/...) chi
  co trong improvements/worker-y6-hyprglass-nested-probe.md
  dong 113, 118, khong co trong probe file. Launcher Y6e cung
  khong co duong dan trong file (that ra la
  improvements/worker-y6e-nested-load-test.sh, 288 dong, tu
  commit 915121d); buoc 2 (chay indicator nested), buoc 3
  (scripted driver, lich trinh cu the), buoc 4 (lenh E1 logging,
  do dai window moi phase) deu khong neu lenh. Nguoi cam file
  khong the chay probe chi tu file nay.

## 3. Loi tim duoc, xep theo muc do

- F1, nghiem trong: phan loai pre-dispatch bang tien to chuoi
  loi, khong kiem chung voi broker. Bang chung A1, A2.
  Sua thanh check xac dinh: truoc fallback, goi `result
  --sequence N`; neu broker tra recorded response thi dung
  response do, neu not_found thi moi fallback; neu unknown thi
  khong fallback.
- F2, nghiem trong: status running va failed bi nuot, seq tien
  sai, gay domino sang browser ke tiep. Bang chung A3. Sua
  thanh check xac dinh: broker_code_exec raise tren moi status
  khac completed, ke ca running va failed; chi tien seq khi
  status la completed.
- F3, cao: fallback khong dem lai truoc khi gui. Bang chung A4.
  Sua thanh check xac dinh: chay lai count_check ngay truoc
  oneshot fallback (ca hai variant, khong chi set_value), abort
  neu count khac 0; hoac thiet ke lai de fallback khong the gui
  khi broker attempt co the da gui.
- F4, cao: 8 test moi khong bao phu duong broker that va status
  unknown. Bang chung A5 (M1, M2, M4 PASS; doi chung M3 FAIL).
  Sua thanh check xac dinh: them test cho broker() that voi ssh
  mock (replay completed, rc khac 0, unknown, running, failed)
  va test mutation gate cho cac nhanh nay.
- F5, cao: A5 fallback drill khong chay duoc va tieu chi sai
  variant. Bang chung A6, A7. Sua: viet lai buoc 3 de khong
  dung Harness.run() khi relay chet (hoac sua run() de oneshot
  that su chay doc lap), them --chromium-set-value hoac doi
  tieu chi delayed count va pre-count theo variant; sua tien
  de 3 ("verify with broker send in step 3" thanh step 1);
  ghi ro run JSON khong co truong broker_finish (run() bo qua
  gia tri tra ve cua broker_finish).
- F6, cao: A3 wedge drill sai ky vong va thieu buoc. Bang
  chung A9 (F6a-F6g). Sua: neu lenh second start cu the va
  message dung cho tung lenh; sua buoc 3 thanh cac truong
  status that co (state, active_sequence, driver van ready);
  tach request khoi result; doi thu tu finish va fresh start
  sang sau phuc hoi; chon mot trong unlink hoac recover; them
  lenh lay driver PID va PGID duoc phep.
- F7, trung binh: A4 CB-10 probe thieu duong dan, hash, lenh.
  Bang chung A10. Sua: ghi duong dan laptop day du cua backup
  .so, hash ky vong, duong dan launcher
  improvements/worker-y6e-nested-load-test.sh, lenh indicator
  nested, script driver, lenh E1 va do dai window moi phase.
- F8, thap: nhan HEAD loi thoi trong worker log va prep log
  section 9 (ghi 0400e86, task giao ed4fcd4). Gia tri toa do
  van dung. Sua: ghi HEAD dung luc do, ke ca khi HEAD dich
  giua task (o day 43ac912 luc 00:25:41 +07).

## 4. Cai khong pha duoc va inconclusive

- KHONG PHA DUOC: holder 5 va toan bo toa do section 9 (A8);
  duong disabled envelope dang da biet (cu.py 3123-3125 tra
  error_type disabled, test_disabled... bat duoc dot bien doi
  chung M3); heredoc envelope an toan theo cau truc
  (json.dumps khong de lai newline that trong envelope, kiem
  tra bang python3 -c, literal newline False, S2EOF False,
  2026-11-23 00:25:40 +07, hash ed4fcd4); 46 test goc PASS
  (lenh `python3 -m unittest tests.test_s2_flip_wiring
  tests.test_s2_flip_pill` tren ban sao /tmp/b24-rt/mutbase,
  output `Ran 46 tests in 0.345s, OK`, 2026-11-23 00:24:39
  +07, hash ed4fcd4).
- INCONCLUSIVE: double-send live that su (khong chay live theo
  luat, chi chung minh o muc code cong mock va xac dinh cua so
  lock-free; xem F1). Khong co claim live nao khac.
- Ghi nhan dung: A5 drill buoc 2 kiem tra dung (broker status
  khi relay chet tra broker_unavailable, rc 1, theo main
  session_remote.py); session_cleanup.py --check ton tai;
  relay service file ton tai (native/computer-use-relay.service,
  Restart=no); A5 drill buoc 1 da tu ghi chu neu baseline roi
  vao broker-fallback-oneshot thi baseline khong sach.

## 5. De xuat bien thanh check xac dinh (kim tu thap tin tuong)

- Truoc fallback, bat buoc poll result cung seq (test A1, A2
  thanh test don vi voi ssh mock).
- broker_code_exec chi chap nhan status completed (test A3
  thanh test don vi cho running, failed, unknown).
- count_check lai ngay truoc moi oneshot fallback (test A4
  thanh test don vi dem so lan goi).
- Mutation gate cho broker() that (M1, M2, M4 thanh test that
  bai khi dot bien, khong chi test mock).
- Drill A5 viet lai de chay duoc khong can GO live truoc: kiem
  tra tinh chay duoc bang mock broker_start chet (test A6) va
  kiem tra tieu chi theo variant (test A7).
- Drill A3 va probe A4: them buoc kiem tra tien quyet chay duoc
  offline (lenh lay PID, duong dan .so, hash) truoc khi xin GO.

## 6. Time log

- 2026-11-23 00:20 +07, T+0m: nhan task, HEAD ed4fcd4, git
  status ghi 3 file M va 4 file moi. Doc xong s2_flip_live.py,
  test_s2_flip_wiring.py, session_remote.py client, worker log,
  prep log diff, 3 drill.
- 2026-11-23 00:23:54 +07: chay attack.py (A1, A3, A4, A7),
  elapsed 0.002s cho script, hash ed4fcd4.
- 2026-11-23 00:24:15 +07: chay attack2.py (A2, A2b, A6),
  elapsed 0.001s cho script, hash ed4fcd4.
- 2026-11-23 00:24:27 +07: co so mutation, 8 test OK 0.004s.
  2026-11-23 00:24:33 +07: M1, M2, M4 PASS, M3 FAIL 1 test.
  2026-11-23 00:24:39 +07: 46 test goc OK 0.345s, grep A8.
- 2026-11-23 00:25:29 den 00:25:40 +07: A9 doc broker, A10
  kiem tra commit, .so, decision doc, heredoc.
- 2026-11-23 00:25:41 +07: HEAD dich sang 43ac912 (council 2
  commit, chi them file council 2 log). Toi khong doc file do.
- 2026-11-23 00:26 +07: viet xong log nay, chuan bi commit
  chi file nay.
