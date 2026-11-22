# Council 3: kiem tra phuong phap va do phu cua ban dac ta xoa task 2

- Ngay: 22/11/2026
- Doi tuong: docs/batch11-task2-step8-deletion-spec-20261122.md (212 dong), batch 11 task 2
- Giao viec: dieu phoi Muse, commit d9b0c05 tren origin/main, muc Task 2
- Nhanh doc code: todolist-push, HEAD 759ce41 luc kiem tra (spec ghi HEAD e68e578 luc viet)
- Quy tac: khong thong tin ca nhan, khong dau gach ngang dai, so lieu that co log
- Pham vi council 3: chi kiem tra phuong phap va do phu, khong kiem tra lai tung con so (do la council 1) va khong kiem tra lai tung trich dan (do la council 2)

## Ket luan chung

Verdict: DO PHU MOT PHAN, CHUA DU DE LAM CO SO THUC THI.

Ca 5 muc Muse giao deu co mat va deu co quyet dinh cu the: queue discipline, single-owner serialization, fatal-on-read-failure matrix, fallback/recovery, CB-10 precondition. 9 muc UNKNOWN trong muc 9 deu la cau hoi that, khong co muc nao bia ra. Cac so lieu PROBE-S1 va danh muc loi broker duoc kiem chung dung.

Nhung ban dac ta co 3 lo hong nang ve phuong phap:

1. Cac so dong code chi noi se xoa deu sai so voi nhanh todolist-push ma spec noi da doc. Nguoi thuc thi lam theo so dong do se sua nham ham.
2. Nua pill cua step 8 khong co tieu chi pass va khong co gate test nao, du step 8 gom ca transport lan pill trong cung mot buoc.
3. Danh sach UNKNOWN thieu it nhat 6 cau hoi mo co tinh chat vat lieu, trong do co xung dot giua quy tac owner giu session suot task va co che broker tu dong ket thuc task idle qua 300s.

Chi tiet tung muc o duoi, moi gap deu co lenh chay va bang chung.

## 1. Doi chieu 5 muc Muse giao

| Muc Muse giao | Co trong spec | Danh gia |
|---|---|---|
| Queue discipline | Muc 3, day du, co quyet dinh moi | Tot, con gap G8 |
| Single-owner serialization | Muc 4, day du, co quyet dinh moi | Tot, con gap G3 va G9e |
| Fatal-on-read-failure matrix | Muc 5, ma tran 6 lop R1, R2, W1, W2, W3, W4 | Tot, con gap G7 |
| Fallback/recovery | Muc 6, 4 muc nho | Tot, con gap G4, G6 |
| CB-10 precondition | Muc 7, day du ca hai limb | Manh nhat, khong co gap lon |

## 2. Nhung gi spec lam dung (da kiem chung)

- 5 dieu kien S1 o muc 2 khop tung chu voi docs/layer0-cbexec-contract.md muc 6 tren todolist-push: laptop tree synced, one-shot SSH kept as fallback and recovery, master watchdog plus soak, fatal-on-read-failure decided, single-owner serialization decided.
- So lieu PROBE-S1 dung: broker 12,110s so voi one-shot 28,700s, nhanh 2,37 lan; O5r 5,375s RC 0; fresh SSH 4,459s va 4,528s; mux 0,98-1,35s; laptop HEAD 56f5af4, VM HEAD 49081aa; relay PID 1821, service active tu 21/11 15:17:30 +07; master 1 pid 11815, master 2 pid 13600, master 3 pid 14865. Nguon: improvements/worker-probe-s1-log.md dong 4, 14, 33-35, 74, 86, 91, 93, 100.
- Verdict PROBE-S1 dung: muc 7 cua probe log ghi "The S1 proof-first gate is MET for the desktop batch". Spec noi gate da dat cho desktop batch la dung.
- Danh muc loi broker o muc 3.1 dung: busy, recovery_required, sequence_gap, conflict, expired, not_found, invalid_lease, broker_changed, lease_file_exists, invalid_lease_file, broker_unavailable deu ton tai trong scripts/session_remote.py. Kiem chung: lease_file_exists dong 1389, invalid_lease_file dong 1363-1373, broker_unavailable dong 1344, broker_running dong 1145 va 1163.
- Cac hang so timeout dung: IDLE_TIMEOUT 300,0s, START_TIMEOUT 25,0s, REQUEST_TIMEOUT 120,0s, MAX_REQUEST_BYTES 8 MiB, session_remote.py dong 33-39.
- Owner regex dung: [A-Za-z0-9_.:@+-]{1,80}, session_remote.py dong 580-585 va 1573-1574.
- Ham _task_recovery_required dung dong 932-937. Ham _result cho doi record.done.wait(request_timeout) roi tra response hien co, session_remote.py dong 846-868, nen UNKNOWN 7 la cau hoi that.
- Trich dan Pick 4 dung: run 1 0/4 BLOCKED vi Pick 1 va Pick 2 giu broker, run 2 4/4 sau khi broker idle. Nguon: improvements/speed-proto-pick4-summary.md muc 2 va muc 6. Trich dan live-test-log.md dung: dong 1778 "G0 gates finisher (broker priority 1)", dong 3701 "retry with backoff on lease contention", dong 3852 Pick 4 cho broker thay vi va cham.
- CB-10 muc 7 la muc manh nhat. Ca hai limb deu con thieu, da kiem chung: grep "LIQUID flicker probe" tren todolist-push chi tra ve cac file dinh nghia va log review, khong co log probe nao chay; khong co deferral nao co ten owner. F2 dong 696 va 708 dung nhu spec trich. Worker4 ket luan nguyen nhan flicker van unknown, docs/redteam-council-20261121/worker4-overlay-flicker-redteam.md dong 56 va 128. Ket luan "phan pill bi BLOCKED, phan transport khong bi CB-10 chan truc tiep" dung theo F2: CB-10 gate A4 step (a), khong gate transport.
- Step 7 P2 commit 292753f ton tai tren todolist-push, nen UNKNOWN 9 la cau hoi that.
- 9 muc UNKNOWN trong muc 9 deu la cau hoi that, khong muc nao bia ra. Van de la danh sach chua du, xem muc 4.

## 3. Gap G1 (nang): so dong code noi se xoa deu sai

Phuong phap cua spec o day la sao chep so dong tu cac log review cu ma khong kiem chung lai tren nhanh todolist-push ma spec noi da doc (HEAD e68e578). Ca 3 trich dan vi tri xoa deu sai.

### G1a. first_action.py:172-178, 403-405

Spec muc 1 ghi per-batch spawn o first_action.py:172-178, 403-405.

Kiem chung tren todolist-push:

```
git show e68e578:scripts/first_action.py | sed -n '165,195p;395,410p'
git show e68e578:scripts/first_action.py | grep -n "session_cmd\|attempt_session"
```

Ket qua: dong 172-178 la ham release_overlay, dong 403-405 la ham _first_pointer_action_ms. Ham xay lenh session that su la session_cmd o dong 186-192, caller duy nhat o dong 669-670 (attempt_session voi session_cmd). Cung ket qua tren HEAD 759ce41 hien tai.

So dong 172-178, 403-405 la so dong cua ban review F1 dong 270, doc tren ban installed hoac checkout cu, khong phai tren todolist-push. Spec sao chep ma khong do lai.

### G1b. zen_dom.py:81-115

Spec muc 1 ghi Zen mo va dong session moi lenh o zen_dom.py:81-115.

Kiem chung:

```
git show e68e578:scripts/zen_dom.py | sed -n '75,120p'
git show e68e578:scripts/zen_dom.py | grep -n "class ZenSession"
```

Ket qua: dong 81-115 la _is_transport_failure va _wait_http, khong mo session nao. Class mo session that su la ZenSession o dong 406, geckodriver spawn o dong 442.

### G1c. cu.py:523

Spec muc 5.1 ghi scripts/cu.py:523 raise ValueError('window no longer exists').

Kiem chung:

```
git grep -n "window no longer exists" origin/todolist-push -- scripts/cu.py
```

Ket qua: lenh raise that su o cu.py:577, khong phai 523. So 523 la so dong cua improvements/brokerfix-report.md dong 10, viet tren checkout cu (speed-swarm-brokerfix c519751). Spec sao chep ma khong do lai. Rieng session_driver.py:35-38 thi dung gan dung (except BaseException voi stop_session_on_error o quanh dong 35-38).

### He qua cua G1

Nguoi thuc thi lam theo so dong trong spec se sua nham ham: release_overlay thay vi session_cmd, ham cho HTTP thay vi ZenSession. Pham vi xoa, von la muc dich chinh cua ban dac ta, chua duoc chung minh day du va dung vi tri. Spec cung khong chung minh session_cmd chi co mot caller (dong 669-670) va khong liet ke cac caller cua ZenSession, nen tinh day du cua pham vi xoa chua duoc chung minh.

Yeu cau sua: do lai tat ca so dong tren todolist-push HEAD hien tai, ghi ro ten ham kem so dong, liet ke day du caller cua session_cmd va ZenSession.

## 4. Cac cau hoi mo bi sot (UNKNOWN thieu)

Danh sach 9 muc UNKNOWN la dung nhung chua du. It nhat 6 cau hoi mo co tinh chat vat lieu khong co trong muc 9.

### G2 (nang): tieu chi pass cua session-level pill bi thieu

Step 8 gom ca transport lan pill trong cung mot buoc theo F1 dong 361: "Session-level pill (server kept) in the same step". Trinh tu A4 theo improvements/worker-click3-final-direction-log.md hang A4 yeu cau: (a) session-level pill truoc, acquire once per task, server KEPT, measured, voi CB-10 precondition; (b) driver-owned pill chi khi co proof no hien va clear, ke ca khong co stale hoac missing pill khi driver chet giua task; (c) chi sau do moi xoa server.

Spec chi noi overlay server chi xoa sau khi pill do driver so huu duoc chung minh (muc 1), nhung khong dinh nghia the nao la pill dat: acquire once per task do bang gi, measure cai gi (so repaint theo phase?), the nao la hien va clear, the nao la khong stale pill khi driver chet. Gate test muc 8 co 8 muc, khong muc nao test pill: muc 7 chi test CB-10 limb, khong test pill acquire-once, khong test pill clear khi driver chet, khong test stale pill. Nua pill cua step 8 ve thuc chat chua duoc dac ta.

### G3 (nang): xung dot giua owner giu session suot task va idle timeout 300s

Spec muc 4.2.4 quyet dinh owner giu session trong suot thoi gian task. Spec muc 3.2.3 lay 300s lam gioi han cho, muc 6.3 lay 300s lam nguong wedged tam. Nhung ca hai deu muon so 300s cua IDLE_TIMEOUT ma khong noi IDLE_TIMEOUT that su lam gi.

Kiem chung code, session_remote.py dong 1060-1065:

```
if task.state == 'running' and task.active is None and now - task.last_activity >= self.idle_timeout:
    task.finish_requested = True
    task.stop_reason = 'idle_timeout'
    task.state = 'cleaning'
```

Broker tu dong ket thuc mot task dang chay ma khong co request nao dang chay qua 300s idle. Mot task co thoi gian model suy nghi tren 300s giua hai request se mat session giua chung. Spec khong hoi: think-time co tinh la idle khong, owner co can keepalive khong. Code co co che keepalive: _status voi lease_file lam moi last_activity, session_remote.py dong 870-875, nhung spec khong de cap. Day la cau hoi mo quan trong nhat bi sot, vi no xung dot truc tiep voi quyet dinh o muc 4.2.4.

### G4 (trung binh): buoc kill wedged session khong co nguon PID

Spec muc 6.3 buoc 4 ghi dung one-shot SSH kill driver process theo PID. Nhung status khong tra ve PID, va session.json chi chua token (version + token), session_remote.py ham _read_snapshot dong 170-190, khong co truong PID nao. Spec khong noi lay PID tu dau (ps tren laptop? pgrep theo ten gi?), khong noi signal nao (TERM hay KILL), khong noi thoi gian cho truoc khi kill manh.

Cung muc 6.3 buoc 2: spec ghi cho toi da START_TIMEOUT 25s de finish ket thuc sach. Code that su: _client_finish co timeout mac dinh 120,0s, session_remote.py dong 1495-1510. Spec muon so 25s tu hang so sai, khong trich dan _client_finish. Can sua thanh 120s hoac neu ro day la so de xuat moi, khac code hien co.

### G5 (trung binh): dieu kien 1 khong co co che xac minh, CB-9 vang mat

Spec muc 2 dieu kien 1 ghi laptop chua sync lai, can chay sync-installed.py hoac tuong duong. Nhung spec khong cho lenh chay chinh xac, khong cho cach so sanh HEAD, va khong de cap CB-9 deployment manifest (khoa source commit + installed artifact + log), von la co che F2 noi la OVERDUE de chung minh sync. File scripts/sync-installed.py ton tai tren todolist-push, nhung spec khong trich dan no, khong ghi tham so chay. Dieu kien 1 vi vay chua the kiem tra duoc bang ban dac ta nay.

### G6 (trung binh): dieu kien tien quyet cua fallback chua the thuc thi

Contract muc 6 quy dinh fallback chi dung khi log xac nhan session chua chay action. Spec muc 6.1 lap lai quy tac nay nhung khong noi log nao, lenh nao, ai doc: khong co duong dan log, khong co lenh doc log, khong ro worker hay dieu phoi la nguoi quyet dinh fallback. Spec cung khong noi so sequence xu ly the nao khi fallback mo session driver moi (sequence bat dau lai tu 1 hay tiep tuc), va khong noi ai la nguoi quyet dinh fallback.

### G7 (trung binh): ma tran fatal chua gioi han pham vi, lop W4 phu thuoc P5

Ma tran muc 5.2 chi co 6 lop o tang driver (read-only va act). No khong co hang nao cho loi tang broker: driver_failed, compositor_changed, cancelled, task_stopped, broker_changed, broker_unavailable, nested_session, native_unavailable, cancellation_unavailable. Mot so loi nay duoc xu ly o muc 3.2.7 va muc 6, nhung ma tran dung mot minh se gay hieu lam la no bao phu tat ca loi.

Lop W4 (already-done, khong gui lai) phu thuoc vao postcondition theo tung loai action, tuc la cong viec P5 (contract muc 13 open item 5, owner P5 implementer). Spec khong ghi phu thuoc nay, nen W4 hien chua the thuc thi duoc cho den khi P5 land tap assert theo action. Tuong tu, lop R1 khong noi ai retry (relay hay client) va "re-ground" doi voi mot lenh read-only co nghia cu the la gi. Danh sach lenh read-only (observe, browser observe, windows, doctor, status) duoc khang dinh ma khong doi chieu voi bang lenh cua cu.py, trong khi relay chi forward bat ky lenh cu.py nao.

### G8 (thap den trung binh): queue discipline con 3 cho mo

(a) Spec muc 3.2.1 trich "G0 gates finisher (broker priority 1)" lam tien le sap xep, nhung broker khong co truong priority nao: _validate_start chi nhan owner, start_id, secret, broker_generation. Priority 1 chi la sap xep lich chay, broker khong thuc thi duoc. Spec khong ghi ro gioi han nay.

(b) Thundering herd: nhieu worker cung poll status roi cung start khi broker ve idle, chi mot thang, so con lai nhan busy roi cho lai. Spec noi retry voi backoff theo tien le live-test-log dong 3701 nhung khong cho gia tri backoff hay jitter cho cuoc dua start lai nay.

(c) Broker restart giua luc cho: worker dang cho chua co lease, generation doi thi xu ly the nao khong duoc noi ro. Spec muc 3.2.7 chi noi ve broker_changed luc start, khong noi ve worker dang cho.

### G9 (thap den trung binh): cac muc UNKNOWN nho khac bi sot

(a) D3 khong duoc thao luan. Spec chi neu D3 trong danh sach nguon muc 10. D3 (codex-discussion-position.md hang D3) la gate song sinh cua S1, them yeu cau reviewer kiem tra timeout khong replay action khong chac trang thai. Yeu cau reviewer check nay khong co trong spec.

(b) Soak chua co owner, lich chay, tieu chi pass. Spec ghi soak 1 ngay chua chay nhung khong noi ai chay, bat dau khi nao, the nao la pass (0 lan master chet, hay so lan restart cho phep).

(c) Spec muc 3.1 ghi invalid_lease khi "owner khong khop hoac lease het han". Code khong co lease TTL: _authorize chi kiem tra generation + secret + owner, session_remote.py dong 778-786. Lease chi vo hieu khi broker restart doi generation, khong co het han theo thoi gian. Chu "het han" gay hieu lam, can sua thanh generation mismatch sau restart.

(d) Spec muc 6.2 cho cach restart relay nhung khong cho lenh systemctl day du va khong noi service la user service hay system service, nen buoc nay chua the chay theo dung ban dac ta.

## 5. Danh gia tung muc UNKNOWN hien co

Ca 9 muc deu dung, da kiem chung tung muc:

1. Laptop HEAD hien tai: that, chi biet luc probe la 56f5af4 va VM 49081aa.
2. Khoang poll status: that, de xuat 5s chua co so do.
3. Nguong wedged: that, contract muc 13 open item 3 giao cho prototype worker.
4. Owner buoc kill: that, khong co ten trong repo.
5. Gioi han fallback 3 lan: that, so de xuat chua co so do.
6. LIQUID probe va deferral: that, da kiem chung ca hai limb deu thieu o muc 2.
7. Hanh vi _result sau REQUEST_TIMEOUT 120s: that, code tra response hien co, trang thai session phai doc status moi biet.
8. Latency sau sync: that, so 12,110s vs 28,700s do tren tree lech.
9. Anh huong cua step 7 P2 (292753f): that, batch 11 task 1 dang kiem tra doc lap.

Khong co muc UNKNOWN nao trong 9 muc la gia. Chi thieu cac muc o muc 4.

## 6. Yeu cau fix pass

1. Do lai tat ca so dong code tren todolist-push HEAD hien tai, sua G1a, G1b, G1c, ghi ten ham kem so dong, liet ke day du caller cua session_cmd va ZenSession.
2. Them tieu chi pass cho session-level pill (G2): acquire once per task do bang gi, measure theo phase ra sao, proof hien va clear, test stale pill khi driver chet giua task. Them gate test pill vao muc 8.
3. Them UNKNOWN ve idle timeout doi voi think-time (G3): think-time co tinh la idle khong, owner co can keepalive bang status co lease khong, va dieu chinh muc 4.2.4 cho khop.
4. Sua buoc kill wedged (G4): ghi nguon PID, signal, thoi gian cho; sua thoi gian cho finish tu 25s thanh 120s theo _client_finish hoac ghi ro day la so de xuat moi.
5. Them CB-9 manifest vao dieu kien 1 (G5): lenh sync-installed.py chinh xac, cach so sanh HEAD, manifest can ghi.
6. Lam ro dieu kien tien quyet fallback (G6): duong dan log, lenh doc log, nguoi quyet dinh, xu ly sequence khi fallback.
7. Ghi ro pham vi ma tran va phu thuoc P5 cua W4 (G7), sua chu "lease het han" thanh generation mismatch (G9c), them D3 reviewer check (G9a) va owner/lich/tieu chi pass cua soak (G9b).

## 7. Nguon kiem chung

- Giao viec: coord/clone1.md, batch 11 task 2, commit d9b0c05 tren origin/main.
- Spec bi kiem tra: docs/batch11-task2-step8-deletion-spec-20261122.md, 212 dong, chua commit.
- Code tren todolist-push HEAD 759ce41, doc bang git show va git grep read-only, khong sua todolist-push.
- Contract: docs/layer0-cbexec-contract.md muc 6 va muc 13.
- Broker code: scripts/session_remote.py, scripts/session_driver.py, scripts/first_action.py, scripts/zen_dom.py, scripts/cu.py.
- Probe: improvements/worker-probe-s1-log.md (verdict muc 7, so lieu dong 74, 86, 91, 93).
- Review: improvements/worker-click3-f1-review-log.md dong 270, 361; improvements/worker-click3-f2-review-log.md dong 224, 696, 708; improvements/worker-click3-final-direction-log.md hang A4; improvements/codex-discussion-position.md hang S1, CB-6, CB-10, D3.
- Flicker: docs/redteam-council-20261121/worker4-overlay-flicker-redteam.md dong 56, 128.
- Broker fix: improvements/brokerfix-report.md dong 10, 16.
