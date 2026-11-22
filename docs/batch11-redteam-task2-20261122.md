# Redteam doc lap: task 2 deletion spec (step 8, S1/CB-6)

- Vai tro: BATCH 11 REDTEAM, tan cong doc dac ta xoa, khong phai tac gia spec.
- Uy quyen: dieu phoi Muse, coord/clone1.md, batch 11 task 2, commit d9b0c05 tren origin/main.
- Doi tuong: docs/batch11-task2-step8-deletion-spec-20261122.md (ban tren main, chua commit).
- Code doc: todolist-push, HEAD 759ce41 (worktree chi doc tai /tmp/rt2-todolist). Moi trich dan dong da doi chieu lai ca o e68e578, HEAD ma spec noi da doc, de loai tru kha nang code doi sau khi spec viet.
- Phuong phap: doc code truc tiep, grep log goc, chay 3 probe thuc nghiem tren broker that (fake driver cua chinh test suite) va tren relay_commands that. Khong tin bao cao cua worker, khong tin spec.
- Quy tac: khong thong tin ca nhan, khong dau gach ngang dai, so lieu that co log.
- Trang thai: chi la bao cao, khong sua code, khong commit, khong push, khong dung toi coord/clone1.md, coord/clone2.md, test-w.txt.

## Ket luan tong

- Tong 16 muc nho duoc danh gia: 11 muc SONG, 5 muc GAY.
- Muc SONG: 2, 3.1, 4.1, 5.1, 6.1, 6.2, 6.4, 7, 8, 9, 10.
- Muc GAY: 1, 3.2, 4.2, 5.2, 6.3.
- 10 loi tim duoc, danh so B1 den B10. Trong do 6 loi nang (B1 den B6), 2 loi thieu (B7, B8), 2 loi nho (B9, B10).
- Phan quyet dinh: spec KHONG THE chay nhu hien viet. Nam muc gay deu nam tren duong thuc thi chinh: toa do xoa sai, dieu kien cho khong bao gio dung, retry bi replay, recovery tu khoa chet minh. Nhung cac gate test o muc 8, neu chay that, se bat duoc B2, B3, B4, B5, B6, vi vay khung gate la dung, chi co noi dung quy trinh la sai.
- Phan dung: toan bo so lieu PROBE-S1, toan bo danh muc loi broker o muc 3.1, co che lease/socket/RLock o muc 4.1, ma tran R2/W2 o muc 5, duong fallback O5r o muc 6.1, va phan CB-10 o muc 7 deu dung sau khi kiem chung truc tiep.

## Bang verdict theo muc

| Muc | Verdict | Ly do mot dong |
|---|---|---|
| 1. Muc dich va pham vi | GAY (B1) | Toa do xoa sai: 172-178 la release_overlay, 403-405 la ham tinh ms, zen_dom 81-115 khong phai session |
| 2. Nam dieu kien tien quyet | SONG | Moi so PROBE-S1 doi chieu dung log goc, trang thai UNKNOWN thanh that |
| 3.1 Co che hien co | SONG | Moi loi, timeout, deque 64 deu khop code |
| 3.2 Queue discipline | GAY (B2, B3) | Cho den state idle khong bao gio dung; retry cung lease file bi replay busy mai |
| 4.1 Co che khoa hien co | SONG | Socket, lease, RLock, relay 9223 deu khop code, chi sai nho ten thong diep (B10) |
| 4.2 Serialization | GAY (B2) | Dieu 6 doi broker ve idle, dieu khong bao gio xay ra sau task dau tien |
| 5.1 Hanh vi hien tai | SONG | relay_commands, execute, is_transient_refusal, B8c2 deu khop, chi sai nho so dong (B9) |
| 5.2 Ma tran quyet dinh | GAY (B4, B7) | W3 noi session song la sai voi args sai va image_policy sai; retry khong noi phai tang sequence |
| 6.1 One-shot fallback | SONG | Duong O5r, so giay, quy tac chi fallback khi chua chay action deu khop log va contract |
| 6.2 Khoi dong lai relay | SONG | Generation doi moi lan restart, 5 dieu kien verify dung sau restart |
| 6.3 Khoi phuc wedged | GAY (B5, B6, B8) | Finish doi lease owner; cancel latch khoa chet moi start sau do; khong co nguon PID |
| 6.4 Master watchdog | SONG | So pid, thoi gian chet, ServerAliveInterval deu khop log probe |
| 7. CB-10 precondition | SONG | Ca hai limb deu thieu that, F2 dong 696/708 trich dung, worker4 ket luan unknown |
| 8. Gate test | SONG | Danh sach gate dung huong, nhung test 3, 4, 5 se FAIL cho den khi sua B2-B6 |
| 9. Danh sach UNKNOWN | SONG | Thanh that, khong bia so; muc 7 nay da tra loi duoc mot phan (xem muc SONG) |
| 10. Nguon chinh | SONG | Moi nguon deu ton tai va dung vi tri |

## B1 (nang, muc 1): toa do code can xoa la sai

Spec viet: per-batch spawn o first_action.py:172-178, 403-405; zen_dom mo dong session moi lenh o zen_dom.py:81-115.

Kiem chung, ca o e68e578 (HEAD spec noi da doc) va o 759ce41:

- Lenh: `git show e68e578:scripts/first_action.py | sed -n '165,180p;395,410p'`
- Ket qua: dong 172-178 la ham `release_overlay` (go overlay holder, gui socket release, khong phai spawn). Dong 403-405 la duoi ham `_first_pointer_action_ms` (tinh ms cho pointer action dau tien, khong phai spawn).
- Spawn that su: `session_cmd` o first_action.py:186-192 (xay argv `[py, cu.py, 'session', '--', py, cu.py, 'act', ...]`), goi o first_action.py:669-670 trong main qua `attempt_session` (dong 194).
- zen_dom.py:81-115: dong 81-115 la `_is_transport_failure`, `_wait_http`, `check_viewport_geometry`. Khong co mo dong session nao o day. Vong doi session that su: class `ZenSession` o zen_dom.py:406, `__enter__` dong 431, `__exit__` dong 463, `_cleanup` dong 467; CLI main o dong 1380 mo mot session moi lenh qua `with ZenSession(...)`.
- Nguon cua loi: F1 dong 270 va F2 dong 224 cung ghi sai toa do nay. Spec da sao lai trich dan cua F1/F2 ma khong mo code kiem tra, du spec tu ghi "Nhanh doc code: todolist-push, HEAD e68e578 luc doc".
- Hau qua: nguoi implement lam theo spec se xoa `release_overlay` (lam hong viec go pill) va mot ham tinh thoi gian, trong khi spawn that su van con nguyen. Day la loi nguy hiem nhat trong spec.

## B2 (nang, muc 3.2 dieu 2 va muc 4.2 dieu 6): state idle khong bao gio tro lai

Spec viet (3.2 dieu 2): worker nhan busy "poll status cho den khi state ve idle, roi start lai". Spec viet (4.2 dieu 6): "broker phai ve idle truoc khi start tiep theo duoc chap nhan".

Code, scripts/session_remote.py:

- Dong 893, ham `_status`: `'state': 'idle' if task is None else task.state`.
- Dong 494 va 667 la hai noi duy nhat gan `self.task`: khoi tao `None`, va gan task moi khi start. Khong co cho nao gan `self.task = None` sau khi task ket thuc. Grep `self\.task =` chi tra 2 dong nay, ca o e68e578 va 759ce41.
- Dieu kien chap nhan start that su (ham `_start`, dong 587): task cu phai o state `finished` hoac `failed`, process da chet, va khong con snapshot. Khong doi state `idle`.

Probe thuc nghiem (/tmp/rt2-probe.py, broker that voi fake driver cua test suite, HEAD 759ce41):

- Status truoc task nao: `state: idle, owner: null, guardian: idle`.
- Sau khi owner A finish xong: `state: finished, owner: owner-a, driver: stopped, guardian: clean`, va `state == idle ? False`.
- Chung cu phu: PROBE-S1 log dong 20 ghi status `state: idle` vi do la broker moi khoi dong, chua chay task nao. Do la lan duy nhat idle xuat hien.

Hau qua: vong cho cua spec poll den gioi han 300s roi bo cuoc, du broker da ranh tu lau. Dieu kien dung phai la: state la `finished` hoac `failed`, guardian khong phai `active`, va khong con session.json (tuc `recovery: none`).

## B3 (nang, muc 3.2 dieu 2 va 3.2 dieu 7): retry cung lease file bi replay busy mai

Spec viet: worker cho roi "start lai voi lease moi (start_id moi)".

Code, scripts/session_remote.py:

- Ham `_start` (dong 587): neu `start_id` da co trong `start_history` thi tra lai `dict(prior['response'])` ma khong chay lai. Response `busy` da ghi cho start_id do se duoc tra lai mai, cho den khi 64 start moi hon day no ra khoi lich su.
- Ham `_client_start` (dong 1456): neu lease file da ton tai thi doc lai va DUNG LAI CUNG start_id. Chi khi file chua ton tai moi tao start_id moi.
- Ham `_write_new_lease` dung O_EXCL: tao lease moi tai CUNG duong dan khi file cu van con thi loi `lease_file_exists`.

Probe thuc nghiem (/tmp/rt2-probe.py):

- Start B trong khi A chay: `{"ok": false, "error": "busy"}`.
- Sau khi A finish xong, start B lai voi CUNG start_id: `{"ok": false, "error": "busy"}` (replay, du broker dang ranh).
- Start B voi start_id MOI: `{"ok": true, "status": "starting", ...}`.
- Probe phu (/tmp/rt2-probe2.py buoc 8): start_id da ghi mot loi ma retry voi secret khac thi tra `conflict`.

Hau qua: spec khong he noi phai xoa lease file cu (unlink) truoc khi start lai, va muc 3.2 dieu 7 khong xu ly loi `lease_file_exists` du muc 3.1 co liet ke no. Worker lam theo spec se hoac bi replay busy im lang mai (dung lai file cu), hoac bi `lease_file_exists` (tao file moi cung duong dan). Quy trinh cho va start lai khong chay duoc nhu viet.

## B4 (nang, muc 5.2 lop W3): session khong song khi args sai hoac image_policy sai

Spec viet lop W3 (JSON khong hop le, args sai, image_policy sai): "KHONG RETRY, tra error envelope, session song" va "day la hanh vi hien co tai relay_commands (I43), giu nguyen".

Code, scripts/session_driver.py, ham `relay_commands` (dong 114):

- Chi dong non-JSON moi duoc tra error envelope va song tiep (dong 121-128, chu thich I43).
- Request la JSON hop le nhung sai dinh dang thi RAISE ValueError ra khoi vong lap, chet ca relay: dong 131 (request khong phai dict), dong 137 (image_policy sai), dong 139 (args sai), dong 146 (lenh khong ho tro). Ham `relay` (dong 59) khong co try/except quanh relay_commands, chi co finally khoi phuc endpoint, nen exception lan ra lam driver process chet, broker danh task failed.

Probe thuc nghiem (/tmp/rt2-w3.py, goi truc tiep relay_commands that):

- W3-a dong non-JSON: tra rc=0, output co error envelope va `session_continues: true`. SONG.
- W3-b args khong phai list: `RAISED ValueError: args must be a non-empty array of strings`, relay chet.
- W3-c image_policy bogus: `RAISED ValueError: image_policy must be auto or always`, relay chet.
- W3-d lenh khong ho tro: `RAISED ValueError: unsupported driver command`, relay chet.
- W3-e request khong phai dict: `RAISED ValueError: request must be an object with args and optional stdin`, relay chet.

Hau qua: trong 3 vi du cua W3, chi co "JSON khong hop le" dang non-JSON line la dung; "args sai" va "image_policy sai" deu ket thuc session, nguoc voi ma tran. Muon W3 dung nhu viet thi step 8 phai sua relay_commands de tra error envelope thay vi raise, giong nhu I43 da lam cho dong non-JSON. Spec hien ghi "giu nguyen" la sai.

## B5 (nang, muc 6.3 buoc 2): finish doi lease cua owner, va sai timeout

Spec viet buoc 2: "Gui finish neu task con song. Cho toi da START_TIMEOUT 25s de driver ket thuc sach."

Code, scripts/session_remote.py:

- Ham `_finish` (dong 914) goi `_authorize` (dong 778): doi generation khop task.generation, lease_secret khop task.secret, owner khop. Thieu mot trong ba thi loi `invalid_lease`. Chi owner giu lease moi finish duoc.
- Ham `_finish` tra ngay lap tuc `{'ok': True, 'status': 'cleaning'}`; no khong cho. Ham client `_client_finish` (dong 1493) moi poll cho, voi timeout mac dinh 120.0s, khong phai 25s.
- START_TIMEOUT 25.0s (dong 38) la timeout cho driver readiness trong `_await_ready` va tick, khong lien quan gi den finish.

Probe thuc nghiem (/tmp/rt2-probe2.py buoc 2):

- Finish voi secret sai: `{"ok": false, "error": "invalid_lease"}`, task van `running` sau do.

Hau qua: neu owner da chet hoac mat lease file thi khong ai finish duoc task wedged. Buoc 2 nhu viet khong the thuc hien boi nguoi khoi phuc thu ba. Can quy dinh ro ai giu lease de finish, hoac bo buoc 2 va di thang sang cancel/kill. Con so 25s cung sai ca gia tri lan y nghia.

## B6 (nang, muc 6.3 buoc 3 + buoc 6, va muc 3.2 dieu 4): cancel latch khoa chet moi start sau do

Spec viet buoc 3: "gui cancel qua cancel latch (file cancelled). Cho guardian don dep." Roi buoc 6: "Restart relay nhu muc 6.2, verify status sach, roi start lai batch moi."

Code:

- Ham `_cancelled` (session_remote.py dong 191): latch ton tai khi file ton tai (lstat). Ham `_start` tra `{'ok': False, 'error': 'cancelled'}` khi latch ton tai. Ham `tick` fail task dang chay thanh `cancelled` khi latch ton tai.
- Khong co cho nao trong broker xoa file latch. Grep toan bo scripts: chi hai cho unlink, deu la lenh resume: cancel_hotkey.py:222 (`CANCEL.unlink` trong lenh `resume`) va cu.py:3166 (lenh `resume`). Thong diep latch ghi ro: "Clear only after the user asks to continue" (cancel_hotkey.py, ham cancellation_message).
- Nhu vay latch la cua rieng nguoi dung, khong phai cong tac dung cua dieu phoi hay worker khoi phuc.

Probe thuc nghiem (/tmp/rt2-probe2.py buoc 3-8):

- Status khi latch ton tai: `cancelled: true, cancellation_state: latched`, task bi fail.
- Start C trong khi latch ton tai: `{"ok": false, "error": "cancelled"}`.
- File latch van ton tai sau do: `True`. Broker khong tu xoa.
- Chi sau khi unlink thu cong (tuong duong lenh resume) thi start moi di tiep duoc.

Hau qua: quy trinh khoi phuc tu khoa chet minh. Buoc 3 latch cancel se lam buoc 6 khong the start lai batch moi cho den khi co mot lenh resume do nguoi dung cho phep, ma spec khong he nhac toi. Cung loi nay anh huong muc 3.2 dieu 4 ("Dieu phoi co the ra lenh dung bang cancel latch"): dung latch de dung owner cung khoa chet broker cho den khi user resume, nen latch khong phai la cong cu dung hop le cua dieu phoi.

## B7 (thieu, muc 5.2 lop R1, W1, W4): retry phai tang sequence, spec khong noi

Code, scripts/session_remote.py, ham `_request`:

- Neu sequence trung voi sequence hien tai va digest giong nhau thi tra lai response DA GHI, khong chay lai lenh. Day la tinh idempotency co chu y.
- Neu sequence nho hon next_sequence thi loi `expired`.

Hau qua: mot worker retry lenh read-only that bai (R1) hoac act chua gui (W1) bang CUNG sequence se nhan lai dung loi cu, khong bao gio chay lai that su. De retry co tac dung thi phai gui sequence TIEP THEO voi request moi. Ma tran muc 5.2 khong noi gi ve sequence, nen nguoi implement retry theo cach hien nhien nhat (gui lai cung sequence) se that bai im lang. Can them quy tac: moi retry la mot sequence moi, va phai ghi log ca hai sequence.

## B8 (thieu, muc 6.3 buoc 4): khong co nguon PID de kill driver

Spec viet buoc 4: "dung one-shot SSH kill driver process theo PID".

Kiem chung:

- Ham `_status` tra cac truong: broker, broker_generation, state, owner, generation, driver, guardian, cancelled, recovery, next_sequence, active_sequence, last_start_error, last_status_error, error, stop_reason. Khong co truong PID nao.
- Cay process that su co 3 tang: broker spawn `cu.py session` (supervise), supervise spawn guardian (`cursor_session.py guard`) va driver (`cursor_session.py driver` exec thanh `cu.py session-driver`). Spec khong noi kill tang nao, va khong noi lay PID bang cach nao (ps/pgrep tren laptop).
- Diem cuu: supervise tu don dep khi driver chet (finally dong goi terminate_driver, dong write_fd lam guardian nhan EOF va thoat, roi goi recover xoa snapshot). Nen kill dung driver child se tu sach. Nhung neu kill nham guardian hoac kill ca cay bang pkill -f thi ket qua khac, va bai hoc pkill tu PROBE-S1 muc 7 cho thay rui ro nay la that.

Hau qua: buoc 4 khong the thuc hien dung nhu viet vi thieu buoc tim PID va xac dinh process. Can them: lenh ps cu the, tang process can kill, va cach xac minh driver da chet truoc khi sang buoc 5.

## B9 (nho, muc 5.1): trich dan cu.py:523 da loi thoi

Spec viet: "scripts/cu.py:523 raise ValueError('window no longer exists')".

Kiem chung: ca o e68e578 va o 759ce41, lenh do nam o cu.py:577 (`if len(matches)!=1: raise ValueError('window no longer exists')`). Spec da sao lai so dong cu tu improvements/brokerfix-report.md dong 10 ma khong mo code doi chieu. Noi dung (window bien mat thi fatal) thi dung, chi sai so dong. Trich dan session_driver.py:35-38 thi dung.

## B10 (nho, muc 4.1): ten thong diep broker_running

Spec viet: listener thu hai nhan loi `broker_running`, thong diep 'a listener already owns this socket'.

Code, ham bind trong UnixSocketServer: flock tren relay.lock chay TRUOC, va neu lock bi giu thi loi la `broker_running` voi thong diep 'another broker owns this socket'. Thong diep spec trich chi xuat hien o buoc probe socket sau do, khi lock khong bi giu nhung socket van co listener. Hanh vi (listener thu hai bi tu choi) thi dung, chi sai thu tu va ten thong diep trong thuc te.

## Nhung muc SONG, va bang chung tan cong that bai

Redteam da co tan cong cac muc sau nhung khong pha duoc; ghi lai de dieu phoi khoi kiem tra lai:

- Muc 2: laptop HEAD 56f5af4, VM HEAD 49081aa (worker-probe-s1-log.md dong 4); O5r 5,375s RC 0 (dong 86); broker 12,110s vs one-shot 28,700s, nhanh 2,37 lan (dong 74, 91, 93); master 1 pid 11815, master 2 pid 13600 chet sau 1-2 phut, master 3 pid 14865 song suot arm khoang 4 phut (dong 35, 100); B8c2 404 tren 9222 ket thuc session (dong 66); scp mux 4,57-4,93s, fresh 8,10-9,38s (dong 55, 60, 79, 81, 91). Tat ca khop.
- Muc 3.1: busy, recovery_required, sequence_gap, conflict, expired, not_found, invalid_lease, broker_changed, lease_file_exists, invalid_lease_file deu co trong code ham _start, _request, _result, _authorize, _client_start, _read_lease, _write_new_lease. Timeout IDLE 300,0s, START 25,0s, REQUEST 120,0s, MAX_REQUEST_BYTES 8 MiB (dong 33-39). start_order la deque lich su 64 lan start (dong 496, 603-607). Poll status khong can lease la dung (ham _status chi yeu cau lease khi co lease_file).
- Muc 3.2 dieu 1, 4, 5, 6: FCFS theo start duoc chap nhan, khong preemption, tuan tu trong owner, retry backoff tren lease contention deu co tien le: live-test-log.md dong 1778 (G0 broker priority 1, cac track lan luot), dong 3701 (retry with backoff on lease contention), dong 3852 (Pick 4 cho broker thay vi va cham); speed-proto-pick4-summary.md dong 25 (run 1 0/4 BLOCKED vi Pick 1 va Pick 2 giu broker) va dong 94 (cho broker idle roi chay lai, run 2 4/4). So dong chinh xac.
- Muc 4.1: socket /run/user/1000/computer-use-wayland/relay.sock mode 0600, SO_PEERCRED cung uid, flock relay.lock (ham bind); lease gom owner, start_id, lease_secret, broker_generation (ham _client_start); RLock (dong 493); Firefox mot remote session moi instance, chung minh trong 4 run (layer0-cbexec-contract.md muc 5.6); relay endpoint mac dinh 9223, khong ke thua endpoint cu, khong ho tro concurrent relay (session_driver.py ham relay, dong 59-77). Tat ca khop.
- Muc 4.2 dieu 1-5 (tru dieu 6): mot owner giu pointer, overlay, Firefox session; lease xac dinh owner; session dong trong finally (ZenSession __exit__ dong 463 goi _cleanup dong 467, xoa session; __enter__ tu cleanup khi tao session that bai); owner giu session suot task (contract muc 5.6, F2 dong 224). Ghi chu: "giu pointer" chi la ky luat, khong co khoa pointer trong code; bat ky process nao cung co the goi truc tiep pointer binary ngoai broker.
- Muc 5.1: relay_commands chi tiep tuc khi returncode 0 hoac rc 1 kem PreflightRefusal co typed provenance hoac act kem is_transient_refusal (session_driver.py dong 165-172); execute goi stop_session_on_error tren moi BaseException (dong 35-38); is_transient_refusal chi nhan screen changed va focus changed co error_code khop, loai capture_error va ime_restore_failed (cu.py dong 1610); B8c2 read-only that bai thi fatal (probe log dong 66); contract muc 2.6 (chi retry khi biet chac chua gui); brightness preflight doi 150ms, mot frame moi, khong retry qua mot lan (brokerfix-report.md Problem 3). Tat ca khop.
- Muc 5.2 lop R2 va W2: dung ngay, 0 retry, session ket thuc (R2) va khong replay khi outcome unknown (W2) la ap dung truc tiep contract muc 2.6 va CB-6 nghia thu nhat (codex-discussion-position.md hang CB-6, ADOPT). Lop R1 thanh that ghi la can thay doi code, khong gia vo la hanh vi hien co.
- Muc 6.1: duong O5r da chay that, 5,375s, RC 0 (probe log dong 86); duong act-now khong ton tai tren laptop, O5 RC 2 invalid choice (dong 82); quy tac fallback chi khi log xac nhan session chua chay action (contract muc 6); fresh SSH 4,459s va 4,528s, mux 0,98-1,35s (probe log dong 33, 98). Tat ca khop.
- Muc 6.2: broker_generation la secrets.token_hex(16) moi lan khoi dong (session_remote.py dong 486), nen restart doi generation that; service computer-use-relay.service, PID 1821, active tu 21/11 15:17:30 +07, socket mode 0600 (probe log muc 1). Nam dieu kien verify sau restart deu dung vi sau restart task la None nen state idle, owner null, guardian idle.
- Muc 6.4: master khong keepalive chet sau 1-2 phut idle, master ServerAliveInterval=15 song suot cua so 4 phut, soak 1 ngay chua chay (probe log dong 35, 100, 104). Khop.
- Muc 7: F2 dong 696 trich dung nguyen van ve LIQUID flicker probe hoac deferral co owner truoc A4 step (a); F2 dong 708 them CB-10 precondition vao session-level pill; worker4 ket luan nguyen nhan unknown, toc do 10 lan/giay chi la uoc tinh cua user, khong co live flicker nao duoc tai hien (worker4-overlay-flicker-redteam.md dong 19, 164); grep toan bo todolist-push khong thay log probe nao load plugin, tai hien flicker, dem repaint. Ca hai limb deu thieu that.
- Muc 8: gate test 1, 2, 3, 6, 7 la yeu cau dung huong. Gate test 3, 4, 5 se FAIL neu chay that voi spec hien tai, tuc gate tu no se bat duoc B2, B3, B4, B5, B6. Day la diem manh cua spec: no tu dat bay dung cho.
- Muc 9: danh sach UNKNOWN thanh that. Bo sung: muc 7 nay da co dap an mot phan tu probe: `_result` cho het REQUEST_TIMEOUT 120s trong khi driver van chay thi tra response hien co voi status `running`, khong phai loi (ham _result, dong 120s wait). Van can doc status moi biet trang thai session sau do, dung nhu spec ghi.
- Muc 10: moi nguon deu ton tai, dung vi tri, dung commit (1af7330 probe S1; cd1dc1c, 9df47a8, df28da9, 1e055eb brokerfix; 292753f P2 step 7, task 1 da verify PASS).

## De nghi sua truoc khi dieu phoi duyet

1. Sua toa do muc 1: first_action.py session_cmd dong 186-192, call site dong 669-670; zen_dom.py ZenSession dong 406-480, CLI main dong 1380. Xoa trich dan 172-178, 403-405, 81-115.
2. Sua dieu kien cho muc 3.2 dieu 2 va muc 4.2 dieu 6: cho den khi status tra state `finished` hoac `failed`, guardian khong phai `active`, va `recovery: none`, khong phai state `idle`.
3. Them buoc unlink lease file cu (hoac dung duong dan lease moi) truoc khi start lai, va them xu ly `lease_file_exists` vao muc 3.2 dieu 7.
4. Sua lop W3: chi dong non-JSON moi song; args sai, image_policy sai, lenh khong ho tro hien ket thuc session. Hoac sua code relay_commands theo mau I43 roi moi ghi W3 nhu hien tai.
5. Sua muc 6.3 buoc 2: chi owner giu lease moi finish duoc; neu owner mat thi bo buoc nay. Timeout finish cua client la 120s, khong phai START_TIMEOUT 25s.
6. Sua muc 6.3 buoc 3: bo viec dung cancel latch lam buoc khoi phuc, hoac them buoc resume do user cho phep va ghi ro latch khoa chet moi start cho den luc do. Cung sua muc 3.2 dieu 4 theo huong nay.
7. Them quy tac sequence cho muc 5.2: moi retry dung sequence moi, khong gui lai cung sequence.
8. Them buoc tim PID vao muc 6.3 buoc 4: lenh ps cu the, tang process can kill (driver child cua supervise), cach xac minh driver da chet.
9. Sua trich dan cu.py:523 thanh cu.py:577.
10. Chay lai gate test muc 8 sau khi sua; test 3, 4, 5 hien se fail va do la bang chung gate hoat dong.

## Danh sach lenh va bang chung

- `git fetch origin main todolist-push`, `git rev-parse origin/todolist-push` = 759ce412ea83fe5118e8f2ae58ec5fa011235df1. Worktree chi doc: `git worktree add --detach /tmp/rt2-todolist origin/todolist-push`.
- `git show e68e578:scripts/first_action.py | sed -n '165,180p;395,410p'` va `git show e68e578:scripts/zen_dom.py | sed -n '75,120p'`: xac nhan toa do sai ca o HEAD spec da doc.
- `grep -n "self\.task =" scripts/session_remote.py`: chi dong 494 va 667. `sed -n '870,900p'` ham _status: state idle chi khi task None.
- `python3 /tmp/rt2-probe.py` (broker that, fake driver cua tests/test_session_remote.py): status sau finish la `finished`, `state == idle ? False`; retry cung start_id tra `busy`; retry start_id moi tra `ok: true, status: starting`.
- `python3 /tmp/rt2-probe2.py`: finish voi secret sai tra `invalid_lease`, task van running; start khi latch ton tai tra `cancelled`; file latch van ton tai sau do; retry cung start_id voi secret khac tra `conflict`.
- `python3 /tmp/rt2-w3.py` (goi truc tiep relay_commands): dong non-JSON tra error envelope va song; args sai, image_policy sai, lenh khong ho tro, request khong phai dict deu raise ValueError, relay chet.
- `git show e68e578:scripts/cu.py | grep -n "window no longer exists"`: dong 577, khong phai 523, ca o e68e578 va 759ce41.
- `grep -rn "LIQUID\|flicker probe" improvements/ docs/`: khong co log probe nao chay; chi co cac log huong dan yeu cau probe.
- Cac file tam probe o /tmp/rt2-probe.py, /tmp/rt2-probe2.py, /tmp/rt2-w3.py, khong commit. Repo chinh tren main khong doi, chi them file bao cao nay.
