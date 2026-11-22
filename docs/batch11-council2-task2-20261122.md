# Council 2, batch 11 task 2: kiem tra ma tran fatal-on-read-failure va fallback

- Ngay: 22/11/2026
- Nhiem vu: kiem tra doc lap ma tran quyet dinh muc 5 va quy trinh fallback/khoi phuc muc 6 trong docs/batch11-task2-step8-deletion-spec-20261122.md
- Giao viec: dieu phoi Muse, batch 11 task 2, commit d9b0c05 tren origin/main
- Nhanh doc code: todolist-push, HEAD 759ce41 luc doc (spec ghi e68e578, log moi nhat cung nhanh nay la 759ce41)
- Phuong phap: chi doc blob bang git cat-file, khong checkout nhanh todolist-push, khong sua code, khong commit, khong push
- Quy tac: khong thong tin ca nhan, khong dau gach ngang dai, so lieu that co log

## Verdict: AMEND, sua roi duyet

Ma tran va fallback dung huong va phan lon co co so that. Nhung co 3 loi phai sua truoc khi duyet: W3 trai code hien tai, muc xoa zen_dom sai ca dong lan pham vi, va vi du stale snapshot cua R1 hien la fatal chu khong phai transient co type. Them 3 sua nho: moc retry 1 lan chi la con so chu khong phai co che, thu tuc restart relay chua tung chay that, va buoc finish cua recovery dung sai hang so timeout. Chi tiet o muc 2.

## 1. Da xac minh dung

### 1.1 Co so cua ma tran trong code

- scripts/session_driver.py, ham relay_commands: mot lenh that bai chi tiep tuc khi returncode 0, hoac returncode 1 kem PreflightRefusal co type, hoac returncode 1 voi lenh act va cu.is_transient_refusal tra true. Moi truong hop khac deu fatal, response kem session_ended voi reason gioi han 400 ky tu va exit_code. Dung nhu spec muc 5.1.
- scripts/session_driver.py, ham execute: bat ky BaseException nao cung goi cu.stop_session_on_error (dong 35-36, spec ghi 35-38, lech 2 dong khong dang ke). PreflightRefusal chi duoc tin dua tren internal provenance, khong bao gio tin co recoverable trong payload. Dung.
- cu.is_transient_refusal (cu.py:1610-1616): chi nhan 'screen changed' va 'focus changed' kem error_code khop, va loai tru capture_error va ime_restore_failed. Matcher hep, dung nhu spec mo ta.
- brokerfix-report.md Problem 1: cu.py raise ValueError('window no longer exists') khi dia chi cua so khong con, va test test_vanished_target_window_remains_fatal_without_typed_provenance khang dinh target bien mat ma khong co typed transient provenance thi session ket thuc. Dung. Chi khac so dong: tren todolist-push HEAD hien tai dong nay la 577, khong phai 523 nhu bao cao cu ghi.
- PROBE-S1 buoc B8c2: browser observe that bai vi CDP 404 tren endpoint 9222, returncode 1, khong phai preflight, toan bo session ket thuc. Log ghi ro day la van de can quyet dinh, khong tu sua. Dung, la co so that cho lop R2.

### 1.2 Moc retry toi da 1 lan

- brokerfix-report.md Problem 3 va code cu.py (desktop_act, khoang dong 1957-1975 tren HEAD hien tai): doi 150ms, chup mot frame moi, chi tien hanh neu hai frame moi khop nhau, khong bao gio retry qua mot lan. Moc 1 lan la that. Chi khac so dong: bao cao ghi 1485-1497, tren HEAD hien tai ham desktop_act bat dau o dong 1812 va doan retry o khoang 1957-1975.
- CB-6 nghia thu nhat trong codex-discussion-position.md (ADOPT): chi retry khi executor biet chac input chua gui; neu ket qua uncertain thi doc lai state truoc khi quyet dinh. Dung, la co so cho lop W2.
- docs/layer0-cbexec-contract.md muc 2.6: retry chi khi biet chac chua gui; postcondition da dung thi danh dau already-done, khong replay; mac dinh khi uncertain thi dung va bao cao; timeout thi tiep tuc ma khong replay. Dung, la co so cho W2 va W4 o muc quyet dinh.

### 1.3 Duong fallback one-shot O5r

- PROBE-S1 muc 6: O5r 5,375s cho ca batch, RC 0, mot lan fresh SSH chay cu.py session voi session-driver, stdin 2 dong JSONL (act voi actions nhung trong, roi finish). Dung nhu spec muc 6.1.
- Fresh SSH don le 4,459s va 4,528s; mux SSH 0,98-1,35s; scp 4,57-4,93s tren mux song va 8,10-9,38s tren fresh SSH. Dung theo log muc 3 va muc 7. Luu y nho: hai mau scp mux giua (4,566 va 4,684) chi xuat hien trong tong ket muc 7, khong duoc liet ke rieng trong danh sach buoc muc 5; spec chi lap lai dung log nen khong sai.
- Duong cu dung act-now khong ton tai tren laptop (O5 tra RC 2, invalid choice). Dung. Fallback phai dung duong O5r, khong dung duong act-now.
- Broker 12,110s so voi one-shot 28,700s, nhanh 2,37 lan. Dung theo log muc 6 va muc 7.

### 1.4 Relay va socket

- PROBE-S1 muc 1: relay PID 1821 song, service computer-use-relay.service active tu 21/11 15:17:30 +07, socket /run/user/1000/computer-use-wayland/relay.sock mode 0600. Dung.
- File native/computer-use-relay.service co tren todolist-push. Dung.
- Code scripts/session_remote.py: socket 0600, kiem tra SO_PEERCRED cung uid, loi broker_running khi listener thu hai chiem socket, loi unsafe_socket khi socket khong an toan. Dung nhu spec muc 4.1.
- Sua sai lam cursor-guard.sock trong PROBE-S1 muc 1: dung, socket relay la relay.sock, khong phai cursor-guard.sock.

### 1.5 Master watchdog va soak

- Master 1 pid 11815 va master 2 pid 13600 khong keepalive chet sau khoang 1-2 phut idle va bi xoa socket. Master 3 pid 14865, ServerAliveInterval=15, song suot khoang 4 phut cua broker arm. Dung theo log muc 3 va muc 7. Soak 1 ngay chua chay. Dung.

### 1.6 Broker: timeout, lease, recovery, hang doi

- IDLE_TIMEOUT 300,0s, START_TIMEOUT 25,0s, REQUEST_TIMEOUT 120,0s, MAX_REQUEST_BYTES 8 MiB (session_remote.py dong 33-39). Dung.
- Start khi task dang song tra busy; start khi con snapshot thi tra recovery_required (dong 629-643). Dung.
- Request khi mot request khac dang chay tra busy, thong diep 'one request is already running' (dong 823). Dung.
- sequence_gap (dong 821), conflict (dong 595, 801), expired, not_found, invalid_lease, broker_changed, lease_file_exists, invalid_lease_file, broker_unavailable: tat ca co trong code. Dung.
- Lease owner 1-80 ky tu, mau [A-Za-z0-9_.:@+-] (dong 580-585 va 1573-1574). Dung.
- start_order la deque lich su 64 lan start gan nhat, khong phai hang doi cho (dong 496, 603-606). Dung.
- _task_recovery_required tra true khi process da chet ma snapshot van ton tai, hoac doc snapshot loi (dong 932-937). Dung chinh xac so dong spec ghi.
- _result cho doi het REQUEST_TIMEOUT roi tra response hien co; trang thai session sau do can doc status moi biet. Dung, spec muc 9 item 7 mo ta dung.
- Cancel latch la file cancelled (dong 32), duoc kiem tra o nhieu diem trong broker. Dung.

### 1.7 Contract va cac log trich dan

- Contract muc 6: nam dieu kien S1, fallback chi dung khi log xac nhan session chua chay action, timeout tiep tuc khong replay, fresh SSH la cach relay duoc khoi dong lai khi broker chet, single-runner lock la task lock do driver giu, LIQUID flicker probe di truoc pill. Tat ca dung.
- Contract muc 5.6: Firefox chi mot remote session, session dong trong finally tren moi duong di, protocol khoi phuc wedged do prototype quy dinh va chung minh. Dung.
- Contract muc 13 open item 3 (wedged-session timeout values, owner prototype worker) va item 4 (queue discipline, owner S1 deletion worker) deu OPEN. Dung, spec muc 6.3 va muc 9 trich dung.
- worker-click3-f1-review-log.md dong 270 (hang CB-6) va dong 361-364 (step 8, gate to step 9). Dung.
- worker-click3-f2-review-log.md dong 224 (hang CB-6, tra loi RTD C5: owner giu single Firefox session trong suot task duration) va dong 696-708 (CB-10 precondition gate A4 step a, va dua vao step 8). Dung.
- live-test-log.md dong 1778 (G0 gates finisher co broker priority 1, cac track lan luot chay va log take/release), dong 3701 (retry with backoff on lease contention), dong 3852 (Pick 4 cho broker thay vi va cham, khong mo session nao). Dung so dong va noi dung.
- speed-proto-pick4-summary.md: run 1 0/4 BLOCKED, run 2 4/4 SUCCESS. Dung.
- worker4-overlay-flicker-redteam.md: nguyen nhan flicker unknown, khong co live flicker nao duoc tai hien, toc do khoang 10 lan/giay chi la uoc tinh cua user, cac gia thuyet H-A den H-G chua duoc xep hang, thay doi after-paint chua duoc chung minh. Dung, spec muc 7 mo ta dung.
- Bai hoc pkill -f trong PROBE-S1 muc 7: dung, pkill -f "http.server 8931" da giet chinh SSH session cua worker.

## 2. Can sua truoc khi duyet

### C1. W3 trai code hien tai, phai tach lam hai

Spec muc 5.2, lop W3: "Read-only, loi dinh dang request ... KHONG RETRY, tra error envelope, session song ... day la hanh vi hien co tai relay_commands (I43), giu nguyen."

Kiem tra that:

- Chi co mot truong hop tra error envelope va session song: dong request khong phai JSON hop le. relay_commands bat ValueError tu json.loads va tra error envelope voi session_continues True. Dung, day la I43.
- Cac loi dinh dang con lai deu RAISE chu khong tra envelope: request khong phai dict, policy khong hop le, args khong phai array khong rong, lenh khong duoc ho tro (unsupported driver command). Cac ValueError nay thoat khoi relay_commands, qua relay, qua cu.main, roi bi __main__ handler cua cu.py (dong 3448-3457) bat theo BaseException, goi stop_session_on_error, thoat 1. Session chet.
- Khong co try/except nao quanh loi goi session_driver.relay trong cu.py (dong 3086-3089).

Sua: tach W3 lam hai dong.

- W3a: dong request khong phai JSON. Tra error envelope, session song. Hanh vi hien co, giu nguyen.
- W3b: JSON hop le nhung args/policy/lenh sai. Hien tai FATAL, session ket thuc, trai voi dong W3 da viet. Hoac sua ma tran ghi nhan W3b la fatal, hoac dua viec doi cac raise nay thanh error envelope vao cong viec code cua step 8 (giong nhu ghi chu R1). Khong duoc giu cau "loi dinh dang request thi session song" o dang tong quat.

### C2. Muc xoa zen_dom sai ca dong lan pham vi, phai bo khoi danh sach xoa step 8

Spec muc 1: "Zen_dom mo va dong mot session moi lenh: zen_dom.py:81-115."

Kiem tra that:

- Tren todolist-push HEAD 759ce41, dong 81-115 cua zen_dom.py la _is_transport_failure, _wait_http, va check_viewport_geometry. Khong co mo hay dong session nao o do.
- Cho mo va dong session that su la class ZenDomSession: __enter__ dong 431-460 (mo session, spawn geckodriver dong 442), __exit__ dong 463, _cleanup dong 467-473.
- Quan trong hon: zen_dom khong duoc noi vao act-now. Khong co import zen_dom nao trong scripts/first_action.py hay scripts/cu.py. Cho dung zen_dom duy nhat tren duong production la dom_act.py ham open_dom_session, va ham nay co 0 caller trong toan bo repo (git grep open_dom_session tren todolist-push tra ve rong). No la helper cho viec P5 chua duoc noi day, khong phai mot phan cua per-batch spawn cua act-now.
- So dong 81-115 va 172-178/403-405 cua first_action.py ma spec trich deu lay tu F1/F2, viet tren HEAD cu hon. Tren HEAD hien tai chung da lech.

Sua: bo dong zen_dom khoi danh sach "Cai se xoa o step 8". Neu muon xu ly zen_dom thi ghi rieng thanh muc P5, khong phai muc xoa cua step 8. Dong thoi sua trich dan first_action.py thanh vi tri that tren HEAD hien tai: session_cmd dong 186-192, attempt_session (Popen) dong 194-230, diem goi dong 669-670. Dong 172-178 hien la code release overlay, dong 403-405 hien la POINTER_ACTION_TYPES, khong phai spawn.

### C3. Vi du stale snapshot cua R1 hien la fatal, khong phai transient co type

Spec muc 5.2, lop R1: vi du gom "PreflightRefusal, observation het han, stale snapshot", quyet dinh RETRY toi da 1 lan.

Kiem tra that:

- require_observation (scripts/session_policy.py:72-79) raise RuntimeError('fresh desktop observation required after transient refusal') khi observation khong khop marker. Khong phai PreflightRefusal.
- Trong cu.py, lenh act goi require_observation o dong 3239 trong khoi with locked(), khong co try/except nao doi RuntimeError nay thanh PreflightRefusal. Cac cho doi sang PreflightRefusal (dong 3228, 3271, 3364, 3411) chi bao JSON actions loi va element ref loi, khong bao require_observation.
- RuntimeError nay roi vao except BaseException cua session_driver.execute, goi stop_session_on_error, session ket thuc. Tuc la stale observation o thoi diem act hien thuoc lop R2 (fatal, 0 retry), khong thuoc R1.

Sua: hoac chuyen vi du stale snapshot sang R2 cho den khi code doi, hoac ghi ro phan code change cua R1 phai bao gom viec doi RuntimeError cua require_observation thanh PreflightRefusal (hoac them matcher co type cho no). Ghi chu hien tai cua spec ("R1 doi hoi thay doi code") noi chung chung, chua goi ten dung cho can doi nay. Luu y them: thong diep loi tu no da noi "after transient refusal", nghia la co che marker nay duoc thiet ke cho luong retry sau transient refusal, nhung dang ket thuc fatal khi model retry bang observation cu thay vi observe lai.

### C4. Moc retry 1 lan la con so dung, khong phai co che san co cho R1/W1

Moc desktop_act la that (muc 1.2), nhung pham vi cua no hep: retry nam gon trong mot khoi if cua desktop_act, tren duong act, cho truong hop brightness preflight. Cac retry R1/W1 vuot qua broker round trip, va khong co code nao hien tai dem so lan retry o tang driver hay broker. Con so 1 lan thi co co so, co che thuc thi cap nay thi chua co: phai do client giu bo dem, hoac them logic moi vao driver. Spec nen ghi ro ai dem va dem o dau, thay vi chi noi "lay tu tien le desktop_act". Day la sua dien dat, khong doi quyet dinh so 1 lan.

### C5. Thu tuc restart relay chua tung chay that

Spec muc 6.2 mo ta cach khoi dong lai relay bang one-shot SSH va kiem tra sau restart.

Kiem tra that:

- Khong co log nao duoc trich dan cho thay lenh restart da tung chay. PROBE-S1 chi chay systemctl --user status. brokerfix-report.md ghi ro: "No live broker session was started and the relay was not restarted."
- Spec cung khong viet ra lenh restart cu the (chi noi "restart service"). Len day du phai la systemctl --user restart computer-use-relay.service, nhung cau lenh nay chua xuat hien o bat ky log nao duoc trich.
- Phan kiem tra sau restart thi co co so code: generation moi lam moi lease cu vo hieu (broker_changed, session_remote.py dong 591, 1465, 1485), va _status tra broker running, state idle, owner null, guardian idle, recovery none khi khong con session.json. Phan nay dung.

Sua: danh dau muc 6.2 la quy trinh de xuat chua duoc chung minh, va dua mot lan restart relay that vao gate test muc 8 (item 5 recovery test hien chi noi wedged session, chua noi restart relay). Khong duoc trinh bay thu tuc nay nhu da duoc kiem chung.

### C6. Buoc finish cua recovery dung sai hang so timeout

Spec muc 6.3 buoc 2: "Gui finish neu task con song. Cho toi da START_TIMEOUT 25s de driver ket thuc sach."

Kiem tra that:

- START_TIMEOUT 25s trong code chi gioi han cho driver san sang: doc ready line (session_remote.py dong 694) va driver_start_timeout (dong 1033-1034). No khong gioi han cho finish.
- Client finish co timeout rieng la 120,0s (_client_finish, dong 1493).

Sua: doi buoc 2 thanh cho toi da 120s theo _client_finish, hoac dat mot con so moi co ten rieng va ghi ro do la quyet dinh moi, khong muon hang so START_TIMEOUT. Cac buoc con lai cua quy trinh 6 buoc thi khop code: cancel latch co that, _task_recovery_required dung nhu mo ta, xoa session.json chi sau khi khong con driver song la dung, va cam pkill -f theo bai hoc PROBE-S1 la dung.

### C7. Tien le cho doi o muc 3.2 bi noi qua

Spec muc 3.2 item 2 noi Pick 4 run 1 0/4 BLOCKED roi cho broker idle chay lai thi run 2 4/4 la "hanh vi da duoc chung minh bang thuc te" cho cach cho bang cach poll status roi start lai.

Kiem tra that:

- Log Pick 4 ghi executor run 1 ghi BLOCKED sau mot lan start that bai moi task, khong poll va khong retry tu dong. Run 2 la chay lai thu cong sau khi Pick 1 va Pick 2 xong. Bang chung chung minh "chay lai sau khi idle thi chay duoc", khong chung minh "worker tu poll status roi start lai voi lease moi". Vong poll la hanh vi moi, chua co code, chua co lan chay nao.
- Tuong tu, item 6 trich live-test-log dong 3701 "retry with backoff on lease contention" nhu tien le, nhung dong do nam trong mot thong bao spawn ke hoach cho 4 coordinator, khong phai mot lan chay da do.

Sua: ha hai trich dan nay xuong muc "bang chung chay lai thu cong sau idle" va "ghi chu ke hoach", va ghi ro vong poll status + backoff la hanh vi moi can code va can test o gate item 3. Quyet dinh discipline van dung duoc, chi co muc do chung minh la thap hon spec viet.

### C8. W4 chua co code, gate test can code moi

"already-done" chi xuat hien trong contract (layer0-cbexec-contract.md dong 170), 0 lan trong cu.py, session_driver.py, session_remote.py. Co che danh dau already-done va doc lai state truoc khi replay chua ton tai trong code. Spec trinh bay W4 nhu quyet dinh, dieu do dung, nhung gate test muc 8 item 4 ("W4 danh dau already-done khong gui lai") doi hoi code moi, khong phai chi la quyet dinh tren giay. Ghi ro dieu nay vao gate test de khong ai doc item 4 nhu mot test chay duoc ngay.

## 3. Ghi chu nho

- Spec muc 5.1 ghi session_driver.py:35-38; tren HEAD hien tai except BaseException o dong 35-36, dong 37 la print. Khong anh huong noi dung.
- brokerfix-report.md ghi cu.py:523 va 1485-1497; tren HEAD hien tai la dong 577 va khoang 1812-1975. Spec lap lai dung bao cao cu, nhung so dong da lech theo HEAD. Cac trich dan dong trong spec nen duoc doi chieu lai voi HEAD 759ce41 truoc khi duyet ban cuoi.
- Spec khong co dau gach ngang dai va khong co thong tin ca nhan. Da kiem tra: 0 dau em dash/en dash trong file spec.

## 4. Ket luan cho dieu phoi

- Duyet ma tran sau khi sua C1 (tach W3), C3 (stale snapshot ve R2 hoac ghi ro code change), C4 (ghi ro ai dem retry), va C8 (ghi ro W4 can code moi).
- Duyet fallback sau khi sua C2 (bo zen_dom khoi muc xoa), C5 (danh dau restart relay la chua chung minh, them lan chay that vao gate), C6 (sua timeout finish thanh 120s hoac so moi), va C7 (ha muc chung minh cua tien le cho doi).
- Khong co quy tac nao trong ma tran mau thuan voi contract 2.6 hay CB-6. Cac mau thuan deu nam giua ma tran va code hien tai (W3, R1 stale), hoac giua trich dan va HEAD hien tai (dong code, zen_dom), khong phai mau thuan ve huong thiet ke.
- Gate test muc 8 cua spec van dung duoc, voi hai bo sung: them lan restart relay that vao item 5, va ghi ro item 4 doi hoi code moi cho R1 va W4.
