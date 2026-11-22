# Council 1, batch 11 task 2: kiem tra queue discipline va single-owner cua ban dac ta xoa step 8

- Ngay: 22/11/2026
- Nguoi kiem tra: council 1, batch 11 task 2
- Doi tuong: docs/batch11-task2-step8-deletion-spec-20261122.md, muc 3 (queue discipline), muc 4 (single-owner serialization), va cac so lieu S1 va Pick 4 ma hai muc nay dua vao
- Giao viec: coord/clone1.md, batch 11 task 2, commit d9b0c05 tren origin/main
- Quy tac: khong thong tin ca nhan, khong dau gach ngang dai, khong ydotool, so lieu that co log
- Trang thai: bao cao kiem tra doc lap, khong sua code, khong commit, khong push

## 1. Phuong phap va gioi han

- Doc truc tiep ban dac ta tren nhanh main.
- Doc truc tiep scripts/session_remote.py va scripts/session_driver.py tren ban checkout main hien tai.
- Doc truc tiep improvements/speed-proto-pick4-summary.md va cac doan lien quan trong improvements/live-test-log.md tren main.
- Gioi han 1: improvements/worker-probe-s1-log.md khong co tren ban checkout main, docs/layer0-cbexec-contract.md cung khong co, improvements/codex-discussion-position.md cung khong co. Cac file nay chi co tren todolist-push theo ban dac ta. Lan fetch todolist-push trong dot kiem tra nay bi chan boi kiem tra rui ro thuc thi, nen council khong doc duoc noi dung cac file do trong dot nay. Cac diem dua vao cac file do duoc ghi la CHUA XAC MINH trong dot nay, khong phai la sai.
- Gioi han 2: so lieu tieu de cua commit 1af7330 da duoc thay trong log truoc khi fetch bi chan: "probe-s1: broker batch proven live from VM, 12.11s vs one-shot 28.70s". Day la bang chung thu cap cho tieu de, khong phai noi dung log.
- Gioi han 3: so dong cu the trong ban dac ta (vi du dong 580-585, dong 1573-1574 cua session_remote.py) khong duoc dem lai tung dong trong dot nay. Council xac minh noi dung, khong xac minh moi so dong.

## 2. Ket luan tom tat

- Muc 3.1 va muc 4.1 noi ve co che hien co trong code: PHAN LON DUNG. Cac loi tu choi busy, recovery_required, sequence_gap, conflict, expired, not_found, invalid_lease, broker_changed, lease_file_exists, invalid_lease_file deu co that trong scripts/session_remote.py tren main. RLock, socket 0600, SO_PEERCRED, start_order la deque lich su 64 muc, cac timeout 300/25/120 deu dung.
- Co 3 diem sai can sua trong ban dac ta: endpoint mac dinh cua relay la 9222 chu khong phai 9223; duong socket phu thuoc uid chu khong co dinh la /run/user/1000; Pick 4 khong chung minh hanh vi cho roi poll roi start lai.
- Muc 3.2 va 4.2 la quyet dinh moi, khong phai mo ta code hien co. Ban dac ta ghi ro dieu nay o phan lon cac muc, la dung. Nhung co hai cho viet nhu the code da ho tro, trong khi code khong ho tro: first-come-first-served co thu tu cong bang, va gioi han cho toi da 300s. Ca hai deu chua co trong code, can viet lai thanh chinh sach phia client can implement va can test.
- Khong co preemption: DUNG doi voi client broker khac, CHUA DU doi voi moi duong dung owner. Cancel latch, idle timeout 300s va restart broker deu co the ket thuc owner.
- So S1 12,110s so voi 28,700s, nhanh 2,37 lan: phep chia dung, tieu de commit 1af7330 khop. Noi dung chi tiet cua log PROBE-S1 chua duoc xac minh lai trong dot nay vi file khong co tren main, xem gioi han 1.
- Pick 4 0/4 BLOCKED roi 4/4: dung ve ket qua, sai ve dien giai hanh vi cho. Xem muc 4.
- Verdict: CAN SUA TRUOC KHI DUYET (AMEND). Sua 3 diem sai o muc 5, viet lai 2 quyet dinh o muc 6 thanh chinh sach can implement, bo sung 2 ngoai le cua no-preemption. Khong can viet lai toan bo ban dac ta.

## 3. Kiem tra so S1: 12,110s so voi 28,700s, 2,37 lan, commit 1af7330

- XAC NHAN: commit 1af7330 ton tai, tieu de ghi "probe-s1: broker batch proven live from VM, 12.11s vs one-shot 28.70s; laptop tree skew blocks act-now and browser endpoint". So 12,11 va 28,70 trong tieu de khop so 12,110 va 28,700 trong ban dac ta, chi khac cach viet thap phan.
- XAC NHAN: phep tinh 28,700 chia 12,110 bang 2,3697, lam tron 2,37. So 2,37 lan dung.
- XAC NHAN: commit 1af7330 chi thay doi 1 file, improvements/worker-probe-s1-log.md, them 110 dong. Day khop voi viec ban dac ta goi day la log probe.
- CHUA XAC MINH trong dot nay: noi dung ben trong log, gom cac so O5r 5,375s, master pid 11815, 13600, 14865, laptop HEAD 56f5af4, VM HEAD 49081aa, loi CDP 404 do endpoint 9222, thoi gian chet master 1-2 phut, soak 1 ngay chua chay. Ly do: file khong co tren ban checkout main, fetch todolist-push bi chan, xem gioi han 1. Council khong khang dinh cac so nay sai, chi ghi la chua doc lai duoc.
- CANH BAO VE DIEN GIAI: chinh tieu de commit da ghi laptop tree skew blocks act-now and browser endpoint. Ban dac ta muc 2 cung ghi dieu kien 1 la UNKNOWN va ket luan step 8 chua duoc xoa. Dien giai nay nhat quan voi tieu de commit. Khong duoc dung so 2,37 lan nhu bang chung gate S1 da dat tron ven, vi gate S1 theo ban dac ta con doi serialize hoac refuse request canh tranh va do latency theo phase, ma cac yeu cau do nam trong log chua doc lai duoc.

## 4. Kiem tra bang chung Pick 4: 0/4 BLOCKED roi 4/4

- XAC NHAN ket qua: improvements/speed-proto-pick4-summary.md ghi Arm 1 Run 1: 0/4, all BLOCKED, tu 00:51 den 01:09; Run 2: 4/4 SUCCESS, tu 01:36 den 02:07. Bang chi tiet Run 2 ghi P1 281,494s, P2 43,609s, P3 43,857s, P4 312,513s, mean 170,368s. Muc 6 Blocker 1 cung ghi "Arm1 run 1 went 0/4 on contention" va "Reran arm1 once after Pick 1 and Pick 2 finished, with broker idle; run 2 went 4/4". So 0/4 roi 4/4 la dung.
- XAC NHAN nguyen nhan canh tranh Run 1: file ghi P2, P3, P4 moi task mot lan start deu that bai cung cach, vi Pick 1 va Pick 2 giu broker suot cua so do, cac owner speed-base-p3, speed-pick1-smoke, pick2-p1, pick2-p2, pick2-p4 duoc nhin thay. Day khop voi mo ta trong ban dac ta muc 3.2 muc 2.
- SUA DIEN GIAI, day la diem sai quan trong nhat cua muc 3.2: ban dac ta viet hanh vi cho roi start lai la "hanh vi da duoc chung minh bang thuc te" qua Pick 4. File goc noi nguoc lai ve hanh vi cua worker o Run 1: "The run-1 executor recorded BLOCKED after one failed start per task instead of retrying." Tuc la worker Run 1 fail nhanh sau mot lan start, khong cho, khong poll, khong retry. Run 2 la mot lan chay lai moi sau khi Pick 1 va Pick 2 xong va broker idle, khong phai cung worker cho roi start lai. Vay Pick 4 chung minh duoc: cho den khi broker idle roi chay lai thi thanh cong. Pick 4 khong chung minh duoc: mot worker poll status lien tuc roi start lai voi lease moi.
- XAC NHAN bang chung cho dang thuc te: improvements/live-test-log.md doan 23:52 ngay 18/11 ghi "Pick 4 waited for the broker rather than colliding: probe and both arms never launched, no sessions opened". Day la bang chung cho dang khong khoi dong khi broker ban, nhung cung khong phai bang chung cho vong poll status roi start lai voi lease moi. Ban dac ta nen trich ca hai nguon dung muc do cua chung: live-test-log cho hanh vi cho bang cach khong khoi dong, Pick 4 cho ket qua chay lai sau khi idle.
- XAC NHAN cac trich dan live-test-log khac: dong quanh 1778 ghi cac track lan luot chay va log take/release, G0 gates finisher co broker priority 1. Dong quanh 3701 ghi "Broker is single-owner: retry with backoff on lease contention." Ca hai deu co that trong file tren main. Luu y: "retry with backoff" o dong 3701 la chi dan trong ke hoach, khong phai code retry trong broker, va khong ghi gia tri backoff cu the.

## 5. Kiem tra co che lease va lock, muc 3.1 va 4.1

### 5.1 Cac diem xac nhan dung

- Mot Task tai mot thoi diem: class Broker co self.task, mac dinh None. Dung.
- Start khi task dang song tra busy: ham _start, khi self.task ton tai va process con chay hoac state chua finished/failed, tra {'ok': False, 'error': 'busy'}. Dung. Luu y thu tu: busy duoc kiem tra truoc recovery_required khi process con song.
- Start khi con state cu tra recovery_required: ham _start tra recovery_required khi _task_recovery_required tra true, hoac khi snapshot session.json con ton tai, hoac khi doc snapshot loi. Ham _task_recovery_required tra true khi process da chet ma snapshot van ton tai, hoac doc snapshot loi. Dung.
- Request khi mot request khac dang chay tra busy: ham _request, thong diep 'one request is already running'. Dung.
- Sequence: sequence_gap khi sequence lon hon so tiep theo, conflict khi sequence da dung cho request khac voi digest khac, expired va not_found khi hoi ket qua het han hoac khong biet. Dung, theo ham _request va _result.
- Lease sai: invalid_lease khi generation, secret hoac owner khong khop, theo ham _authorize. broker_changed khi broker_generation khong khop, theo ham _start va cac ham client. lease_file_exists khi file lease da ton tai, theo _write_new_lease dung co O_EXCL. invalid_lease_file khi file lease hong hoac sai dinh dang, theo _read_lease. Dung.
- Khong co hang doi trong broker: start_order la deque, chi luu lich su 64 lan start gan nhat, xoa muc cu nhat khi vuot 64. Day la lich su, khong phai hang doi cho. Dung.
- Timeout: IDLE_TIMEOUT 300,0s, START_TIMEOUT 25,0s, REQUEST_TIMEOUT 120,0s, MAX_REQUEST_BYTES 8 MiB. Dung, o dau file session_remote.py.
- RLock: Broker.lock la threading.RLock, bao quanh start, request, result, status. Dung.
- Socket 0600 va SO_PEERCRED: ham bind kiem tra co SO_PEERCRED, chmod socket 0o600, kiem tra lai S_IMODE phai bang 0o600 neu khong bao unsafe_socket. Ham _peer_uid doc SO_PEERCRED va ham handle_client tu choi peer co uid khac euid. Dung.
- Listener thu hai: ham bind thu flock tren file relay.lock, neu bi khoa thi bao broker_running; neu socket cu con song thi bao broker_running voi thong diep 'a listener already owns this socket'. Dung.
- Owner: mau [A-Za-z0-9_.:@+-], 1-80 ky tu, kiem tra o ham _validate_start va o CLI start. Dung ve noi dung.
- Lease gom owner, start_id, lease_secret, broker_generation, generation: ham _client_start, _read_lease, _write_new_lease. Dung. Co hai generation khac nhau: broker_generation cua broker process, va generation cua task moi start. Ban dac ta khong phan biet ro hai cai nay, xem muc 5.2.
- Poll status khong can lease: ham _status chi goi _authorize khi value co lease_file. Dung, khop voi mo ta "poll status (khong can lease)" trong ban dac ta.

### 5.2 Cac diem can sua

- SUA 1, endpoint relay: ban dac ta muc 4.1 viet "endpoint mac dinh 9223 cho agent Chromium". File scripts/session_driver.py tren main, ham relay, viet ro: cu.BROWSER_ENDPOINT='http://127.0.0.1:9222', kem ghi chu "No concurrent relay support" va "never inherits a previous session's retained endpoint". Vay so 9223 la sai tren ban code council doc duoc. Ghi chu "No concurrent relay support" thi dung. Ban dac ta phai sua 9223 thanh 9222, hoac trich dan nguon khac neu 9223 thuoc ve mot file hay mot nhanh khac, va ghi ro nguon do.
- SUA 2, duong socket: ban dac ta viet socket la /run/user/1000/computer-use-wayland/relay.sock nhu mot duong co dinh. Code ham _default_socket lay XDG_RUNTIME_DIR, neu khong co thi dung /run/user/{uid}, roi noi computer-use-wayland/relay.sock. So 1000 chi dung khi uid bang 1000. Phai viet lai thanh duong suy ra tu XDG_RUNTIME_DIR hoac /run/user/{uid}, khong viet cung 1000.
- SUA 3, bo sung co che khoa file ma ban dac ta bo sot: ngoai socket, ham bind con mo file relay.lock, chmod 0600, flock LOCK_EX | LOCK_NB. Day la lop khoa thu hai chong hai broker cung chay. Ban dac ta chi mo ta socket, nen them mot dong ve relay.lock de mo ta du.
- LAM RO, hai generation: broker_generation doi khi broker restart, lam moi lease cu vo hieu voi loi broker_changed. Task generation duoc tao moi moi lan start thanh cong bang secrets.token_hex(16), ham _authorize kiem tra generation nay. Ban dac ta viet "Generation doi sau restart" ma khong noi ro la broker_generation, va viet "Moi request phai kem dung owner, dung secret, dung generation" ma khong noi ro la task generation. Nen tach ro hai khai niem.
- LAM RO, lease khong co han su dung: ham _authorize khong kiem tra thoi gian het han cua lease. Lease chi vo hieu khi generation doi, secret sai, owner sai, hoac broker restart. Ban dac ta muc 3.1 viet "lease het han" nhu mot truong hop cua invalid_lease, nen sua thanh "lease khong khop generation hoac secret", khong goi la het han neu khong co TTL.
- LAM RO, dong 580-585 va 1573-1574: council xac minh noi dung owner regex co that, nhung khong dem lai so dong. Neu giu so dong trong ban dac ta thi can mot nguoi dem lai tren todolist-push HEAD e68e578, vi file tren main co the lech dong so voi todolist-push.
- CHUA XAC MINH trong dot nay: cau "Firefox chi cho phep dung mot remote session moi instance, da chung minh trong 4 run (layer0-cbexec-contract.md muc 5.6)" vi contract khong co tren main. Cau ve single-runner lock, cancel latch va task scope do driver giu (layer0 muc 6) cung chua xac minh duoc vi cung nguon. Council khong khang dinh hai cau nay sai, chi ghi la chua doc lai duoc trong dot nay.

## 6. Kiem tra first-come-first-served, cho toi da 300s, khong preemption

### 6.1 First-come-first-served: KHONG DUOC CODE HO TRO

- Code khong co hang doi, khong co thu tu den, khong co timestamp den cua contender. start_id co tien to monotonic_ns, nhung chi dung de tu choi start id cu da het han va de phat hien conflict, khong dung de sap xep contender.
- Ai thang la ai giu RLock truoc trong ham _start. Hai worker cung gui start se dua nhau o khoa nay, nguoi thang la nguoi vao critical section truoc, khong co dam bao cong bang nao cho nguoi gui truoc tren mang hay tren VM.
- Cau "first-come-first-served theo lan start duoc broker chap nhan" la dinh nghia vong: ai duoc chap nhan truoc thi la truoc. No khong phai mot discipline ma code bao dam. Ban dac ta phai viet lai thanh: hien tai chi co quy tac nguoi thang duy nhat duoc chap nhan, nguoi thua nhan busy; FCFS cong bang giua cac contender, neu dieu phoi muon, la chinh sach moi can implement o phia client hoac them hang doi vao broker, chua co trong code.
- Khong co muc uu tien trong broker: dung. Code khong co truong priority nao. "G0 gates finisher co broker priority 1" trong live-test-log la cach xep lich chay cua dieu phoi, khong phai truong uu tien trong broker.

### 6.2 Cho toi da 300s: KHONG CO TRONG CODE, LA QUYET DINH MOI

- Khong co vong cho nao trong session_remote.py, ca phia broker va phia client. Ham _client_start chi thu start mot lan, nhan busy thi tra ve ngay. Khong co poll, khong co retry, khong co backoff trong file nay.
- IDLE_TIMEOUT 300,0s khong phai gioi han cho cua contender. Ham tick dung 300s nay de ket thuc mot task dang chay ma khong co request nao trong 300s: neu state running, khong co active request, va idle hon 300s thi dat finish_requested va stop_reason idle_timeout. Lay 300s nay lam moc cho gioi han cho la lua chon thiet ke hop ly, nhung phai ghi ro la so moi, khong phai so code da ap.
- Tong thoi gian cho thuc te co the vuot 300s nhieu lan: mot owner co the chay het task dai, roi owner tiep theo lai chay, contender van phai cho. Gioi han 300s chi co nghia neu hieu la 300s cho mot lan doi mot owner cu the, hoac 300s tong cong roi bao ve dieu phoi. Ban dac ta muc 3.2 muc 3 viet "Qua 300s van busy thi worker dung cho", day la tong cong, nen ghi ro la tong cong va la quyet dinh moi.
- Khoang poll 5s: ban dac ta tu ghi la UNKNOWN va de xuat, la dung. Khong co so do nao trong code ho tro 5s. Giu nguyen cach ghi UNKNOWN nay, khong bien no thanh su that.

### 6.3 Khong co preemption: DUNG MOT PHAN, CAN BO SUNG NGOAI LE

- Dung doi voi client broker: khong co API nao de mot client cuop task cua owner khac. Ham _authorize tu choi moi request, finish, result neu owner, secret hoac generation khong khop. Chi owner moi finish hoac cancel task cua minh qua broker. Dung.
- Chua du: cancel latch la file $STATE/cancelled, ham _cancelled chi kiem tra file co ton tai hay khong, khong kiem tra owner. Ham tick va ham _request deu kiem tra latch nay. Vay bat ky ai tao duoc file cancelled deu dung duoc owner, khong qua lease. Day la mot dang dung tu ben ngoai broker, can ghi ro trong ban dac ta.
- Chua du: idle timeout 300s tu dong ket thuc owner dang chay ma idle, ham tick. Restart broker lam vo hieu moi lease cu, loi broker_changed. Kill process driver hoac broker cung ket thuc owner. Nhung truong hop nay khong phai preemption boi mot worker khac, nhung van la owner bi day ra khong do y muon cua owner.
- Ket luan: viet lai thanh "khong co preemption qua broker API; owner chi co the bi dung boi cancel latch, idle timeout, restart broker, hoac kill process". Cau "Owner dang chay khong bao gio bi day ra" trong ban dac ta la qua manh, phai sua.

### 6.4 Trong mot owner, request tuan tu tuyet doi: DUNG

- Ham _request chi cho mot active request, request thu hai khi request dau chua xong nhan busy voi thong diep 'one request is already running'. Sequence phai la so tiep theo, neu khong bao sequence_gap. Dung, khop hoan toan voi ban dac ta muc 3.2 muc 5.
- Ket thuc owner phai ve idle truoc khi start tiep theo: ham _start tu choi start moi khi task cu con process song hoac state chua finished/failed, va tra recovery_required khi con snapshot. Dung ve co che. Cau "Start tiep theo chi duoc chap nhan sau khi guardian sach (guardian clean)" thi can ghi ro: code kiem tra snapshot khong con ton tai va _task_recovery_required tra false, khong kiem tra chuoi 'guardian clean' mot cach truc tiep trong ham _start. Ham tick dat guardian clean khi process da chet va token la None. Nen giu mo ta o muc snapshot va process, khong viet nhu the co mot buoc kiem tra guardian clean rieng trong _start.

## 7. Danh sach sua cu the gui cho task 2

1. Sua 9223 thanh 9222 o muc 4.1, kem trich dan scripts/session_driver.py ham relay tren ban code da doc, hoac neu 9223 lay tu nguon khac thi ghi ro nguon do.
2. Sua duong socket thanh duong suy ra tu XDG_RUNTIME_DIR hoac /run/user/{uid}, khong viet cung /run/user/1000.
3. Them mot dong ve file relay.lock va flock LOCK_EX | LOCK_NB o muc 4.1.
4. Sua dien giai Pick 4 o muc 3.2 muc 2: bo cum "hanh vi da duoc chung minh bang thuc te" cho vong poll roi start lai. Viet lai thanh: Pick 4 Run 1 fail nhanh sau mot lan start, khong retry; Run 2 la chay lai moi sau khi broker idle va thanh cong 4/4; live-test-log 23:52 ghi Pick 4 cho bang cach khong khoi dong. Vong poll status roi start lai voi lease moi la hanh vi moi can implement va test, chua co bang chung chay that.
5. Viet lai FCFS o muc 3.2 muc 1 thanh: hien tai chi co nguoi thang duy nhat duoc chap nhan, khong co hang doi, khong co dam bao thu tu cong bang. FCFS day du la chinh sach moi, can dieu phoi chot va can implement.
6. Viet lai gioi han cho 300s o muc 3.2 muc 3 thanh: 300s la quyet dinh moi lay moc tu IDLE_TIMEOUT, khong phai gioi han co trong code; ghi ro la tong cong hay cho moi owner; ghi ro khoang poll 5s van la UNKNOWN.
7. Sua cau "Owner dang chay khong bao gio bi day ra" thanh dang co ngoai le: cancel latch, idle timeout 300s, restart broker, kill process.
8. Tach ro broker_generation va task generation o muc 4.1 va 4.2, sua cum "lease het han" thanh "lease khong khop generation hoac secret".
9. Bo sung ghi chu: cac diem dua vao docs/layer0-cbexec-contract.md muc 5.6 va 6, va vao log PROBE-S1 chi tiet, can duoc kiem tra lai tren todolist-push HEAD e68e578 truoc khi duyet, vi dot council nay khong doc duoc cac file do tren main.
10. Kiem tra lai so dong 580-585 va 1573-1574 cua session_remote.py tren todolist-push, vi file tren main co the lech dong.

## 8. Verdict

- Verdict: CAN SUA TRUOC KHI DUYET (AMEND).
- Ly do: co che hien co trong muc 3.1 va 4.1 phan lon dung va co the kiem chung truc tiep tu code, nhung ban dac ta co 1 so sai ve endpoint 9223 va 2 dien giai qua manh ve Pick 4 va ve no-preemption, va 2 quyet dinh FCFS va 300s duoc viet nhu the code da ho tro trong khi code chua co. Cac loi nay deu sua duoc bang cach viet lai, khong can thay doi thiet ke lon.
- Khong co diem nao trong pham vi council 1 duoc xac nhan la sai hoan toan ve co che khoa: single Task, RLock, lease, socket 0600, SO_PEERCRED, busy, recovery_required deu co that.
- De nghi dieu phoi: cho task 2 sua theo muc 7, sau do council 1 hoac redteam doc lai rieng cac muc 3.2 va 4.2 da sua, va doc lai log PROBE-S1 tren todolist-push de khoa cac so chi tiet o muc 2 va 6 cua ban dac ta.

## 9. Nguon da doc truc tiep trong dot nay

- docs/batch11-task2-step8-deletion-spec-20261122.md, toan bo, tren main.
- scripts/session_remote.py, toan bo, tren main: Broker, _start, _request, _result, _status, _authorize, _task_recovery_required, UnixSocketServer.bind, _client_start, _read_lease, _write_new_lease, _lease_path, cac hang IDLE_TIMEOUT, START_TIMEOUT, REQUEST_TIMEOUT, MAX_REQUEST_BYTES.
- scripts/session_driver.py, ham relay va execute, tren main.
- improvements/speed-proto-pick4-summary.md, toan bo, tren main.
- improvements/live-test-log.md, cac doan quanh dong 1778, 3701, 3852, tren main.
- Commit 1af7330, tieu de va stat, tu log truoc khi fetch bi chan: 1 file, improvements/worker-probe-s1-log.md, 110 dong them.
- Khong doc duoc trong dot nay: improvements/worker-probe-s1-log.md, docs/layer0-cbexec-contract.md, improvements/codex-discussion-position.md, vi khong co tren main va fetch todolist-push bi chan boi kiem tra rui ro thuc thi.
